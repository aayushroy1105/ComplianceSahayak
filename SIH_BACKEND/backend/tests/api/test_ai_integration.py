import builtins
import os
import uuid
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from unittest.mock import patch, AsyncMock
from uuid import UUID

from app.core.config import settings
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.inspection import Inspection
from app.models.inspection_image import InspectionImage
from app.models.audit_log import AuditLog
from app.models.declaration import Declaration
from app.models.violation import Violation
from app.models.evidence import Evidence
from app.models.legal_reference import LegalReference
from app.models.corrective_action import CorrectiveAction
from app.schemas.ai_result import AIAnalyzeResponse
from app.clients.ai_client import AIServiceClient, AIAnalysisError
from app.services.analysis_service import process_inspection_analysis
import io
from PIL import Image

def create_dummy_image(format="JPEG", size=(10, 10)) -> bytes:
    img = Image.new('RGB', size, color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()

@pytest.fixture
async def mock_ai_client():
    client = AIServiceClient(mock_mode=True)
    with patch("app.api.routes.inspections.ai_client_instance", client) as mocked:
        yield mocked

@pytest.fixture
async def sample_inspection_with_image(client: AsyncClient, setup_test_users, db: AsyncSession):
    token = setup_test_users["user_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={"latitude": 10.0, "longitude": 10.0})
    inspection_id = res.json()["id"]
    
    # Upload image
    image_bytes = create_dummy_image()
    files = {'image': ('test.jpg', image_bytes, 'image/jpeg')}
    data = {'image_type': 'FRONT'}
    img_res = await client.post(
        f"{settings.API_V1_STR}/inspections/{inspection_id}/images",
        cookies={"access_token": token},
        data=data,
        files=files
    )
    assert img_res.status_code == 201
    return inspection_id

@pytest.mark.asyncio
async def test_analyze_success_compliant(client: AsyncClient, setup_test_users, sample_inspection_with_image, mock_ai_client):
    token = setup_test_users["user_token"]
    
    # Customize mock response
    mock_response = mock_ai_client._generate_mock_response("test")
    mock_response.compliance.status = "COMPLIANT"
    mock_response.violations = []
    mock_response.corrective_actions = []
    
    with patch.object(mock_ai_client, 'analyze', new_callable=AsyncMock, return_value=mock_response):
        res = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": token}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["compliance_status"] == "COMPLIANT"
        assert data["processing_status"] == "COMPLETED"

@pytest.mark.asyncio
async def test_analyze_success_non_compliant(client: AsyncClient, setup_test_users, sample_inspection_with_image, db: AsyncSession, mock_ai_client):
    token = setup_test_users["user_token"]
    
    # Default mock is NON_COMPLIANT
    mock_response = mock_ai_client._generate_mock_response("test")
    with patch.object(mock_ai_client, 'analyze', new_callable=AsyncMock, return_value=mock_response):
        res = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": token}
        )
        assert res.status_code == 200
        
        # Check database persistence
        v_res = await db.execute(select(Violation).where(Violation.inspection_id == sample_inspection_with_image))
        violations = v_res.scalars().all()
        assert len(violations) > 0
        
        c_res = await db.execute(select(CorrectiveAction).where(CorrectiveAction.inspection_id == sample_inspection_with_image))
        corrective_actions = c_res.scalars().all()
        assert len(corrective_actions) > 0
        
        d_res = await db.execute(select(Declaration).where(Declaration.inspection_id == sample_inspection_with_image))
        declarations = d_res.scalars().all()
        assert len(declarations) > 0
        
        e_res = await db.execute(select(Evidence).where(Evidence.inspection_id == sample_inspection_with_image))
        evidence = e_res.scalars().all()
        assert len(evidence) > 0

@pytest.mark.asyncio
async def test_analyze_ai_error(client: AsyncClient, setup_test_users, sample_inspection_with_image, mock_ai_client, db: AsyncSession):
    token = setup_test_users["user_token"]
    
    with patch.object(mock_ai_client, 'analyze', new_callable=AsyncMock, side_effect=Exception("Simulated AI Failure")):
        res = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": token}
        )
        assert res.status_code == 502
        
        # DB status should be FAILED
        insp_res = await db.execute(select(Inspection).where(Inspection.id == sample_inspection_with_image))
        insp = insp_res.scalars().first()
        assert insp.processing_status == "FAILED"

@pytest.mark.asyncio
async def test_analyze_llm_failure_preserves_compliance(client: AsyncClient, setup_test_users, sample_inspection_with_image, mock_ai_client, db: AsyncSession):
    token = setup_test_users["user_token"]
    
    # Mock LLM failure scenario
    mock_response = mock_ai_client._generate_mock_response("test")
    mock_response.compliance.status = "NON_COMPLIANT"
    mock_response.corrective_actions = []
    mock_response.review_required = True
    mock_response.model_info.llm_version = "ERROR_TIMEOUT"
    
    with patch.object(mock_ai_client, 'analyze', new_callable=AsyncMock, return_value=mock_response):
        res = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": token}
        )
        assert res.status_code == 200
        
        insp_res = await db.execute(select(Inspection).where(Inspection.id == sample_inspection_with_image))
        insp = insp_res.scalars().first()
        
        assert insp.compliance_status == "NON_COMPLIANT"
        assert insp.review_status == "PENDING"
        assert insp.llm_version == "ERROR_TIMEOUT"

@pytest.mark.asyncio
async def test_analyze_idempotency_cleans_up(client: AsyncClient, setup_test_users, sample_inspection_with_image, mock_ai_client, db: AsyncSession):
    token = setup_test_users["user_token"]
    
    mock_response = mock_ai_client._generate_mock_response("test")
    
    with patch.object(mock_ai_client, 'analyze', new_callable=AsyncMock, return_value=mock_response):
        # Run first time
        res1 = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": token}
        )
        assert res1.status_code == 200
        
        # Count declarations
        d_res1 = await db.execute(select(Declaration).where(Declaration.inspection_id == sample_inspection_with_image))
        initial_count = len(d_res1.scalars().all())
        assert initial_count > 0
        
        # Run second time
        res2 = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": token}
        )
        assert res2.status_code == 200
        
        # Count should remain same (replaced)
        d_res2 = await db.execute(select(Declaration).where(Declaration.inspection_id == sample_inspection_with_image))
        final_count = len(d_res2.scalars().all())
        assert final_count == initial_count

@pytest.mark.asyncio
async def test_analyze_audit_logs(client: AsyncClient, setup_test_users, sample_inspection_with_image, mock_ai_client, db: AsyncSession):
    token = setup_test_users["user_token"]
    
    mock_response = mock_ai_client._generate_mock_response("test")
    with patch.object(mock_ai_client, 'analyze', new_callable=AsyncMock, return_value=mock_response):
        res = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": token}
        )
        assert res.status_code == 200
        
        a_res = await db.execute(select(AuditLog).where(AuditLog.inspection_id == sample_inspection_with_image, AuditLog.action == "AI_ANALYSIS_COMPLETED"))
        audit = a_res.scalars().first()
        assert audit is not None
        assert audit.metadata_col["compliance"] == "NON_COMPLIANT"


@pytest.fixture
async def additional_test_users(db: AsyncSession):
    user_b = User(
        id=uuid.uuid4(),
        name="Other User",
        email="other_user@example.com",
        password_hash=get_password_hash("test"),
        role="USER",
        is_active=True,
    )
    admin = User(
        id=uuid.uuid4(),
        name="Admin User",
        email="admin_analysis@example.com",
        password_hash=get_password_hash("test"),
        role="ADMIN",
        is_active=True,
    )
    db.add_all([user_b, admin])
    await db.commit()
    return {
        "user_b": user_b,
        "user_b_token": create_access_token(user_b.email),
        "admin": admin,
        "admin_token": create_access_token(admin.email),
    }


@pytest.mark.asyncio
async def test_analyze_owner_by_inspection_code(
    client: AsyncClient, setup_test_users, sample_inspection_with_image, db: AsyncSession, mock_ai_client
):
    token = setup_test_users["user_token"]
    insp_res = await db.execute(select(Inspection).where(Inspection.id == sample_inspection_with_image))
    inspection = insp_res.scalars().first()

    mock_response = mock_ai_client._generate_mock_response(inspection.inspection_code)
    mock_response.compliance.status = "COMPLIANT"
    mock_response.violations = []
    mock_response.corrective_actions = []

    with patch.object(mock_ai_client, "analyze", new_callable=AsyncMock, return_value=mock_response):
        res = await client.post(
            f"{settings.API_V1_STR}/inspections/{inspection.inspection_code}/analyze",
            cookies={"access_token": token},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == sample_inspection_with_image
        assert data["processing_status"] == "COMPLETED"
        assert data["compliance_status"] == "COMPLIANT"


@pytest.mark.asyncio
async def test_analyze_denied_for_other_user_no_side_effects(
    client: AsyncClient, setup_test_users, additional_test_users, sample_inspection_with_image, db: AsyncSession, mock_ai_client
):
    other_token = additional_test_users["user_b_token"]
    insp_res = await db.execute(select(Inspection).where(Inspection.id == sample_inspection_with_image))
    inspection = insp_res.scalars().first()
    img_res = await db.execute(select(InspectionImage).where(InspectionImage.inspection_id == inspection.id))
    image = img_res.scalars().first()
    image_basename = os.path.basename(image.storage_path)

    opened_files = []
    real_open = builtins.open

    def tracking_open(file, *args, **kwargs):
        if image_basename in str(file):
            opened_files.append(str(file))
        return real_open(file, *args, **kwargs)

    with (
        patch.object(mock_ai_client, "check_health", new_callable=AsyncMock) as mock_health,
        patch.object(mock_ai_client, "analyze", new_callable=AsyncMock) as mock_analyze,
        patch("builtins.open", side_effect=tracking_open),
    ):
        for identifier in (sample_inspection_with_image, inspection.inspection_code):
            res = await client.post(
                f"{settings.API_V1_STR}/inspections/{identifier}/analyze",
                cookies={"access_token": other_token},
            )
            assert res.status_code == 403

        mock_health.assert_not_awaited()
        mock_analyze.assert_not_awaited()
        assert opened_files == []

    await db.refresh(inspection)
    assert inspection.processing_status == "PENDING"

    audit_res = await db.execute(
        select(AuditLog).where(
            AuditLog.inspection_id == inspection.id,
            AuditLog.action.in_(["AI_ANALYSIS_COMPLETED", "AI_ANALYSIS_FAILED"]),
        )
    )
    assert audit_res.scalars().all() == []


@pytest.mark.asyncio
async def test_analyze_frontend_supplied_user_id_ignored(
    client: AsyncClient, setup_test_users, additional_test_users, sample_inspection_with_image, db: AsyncSession, mock_ai_client
):
    owner_id = str(setup_test_users["user"].id)
    other_token = additional_test_users["user_b_token"]

    with (
        patch.object(mock_ai_client, "check_health", new_callable=AsyncMock) as mock_health,
        patch.object(mock_ai_client, "analyze", new_callable=AsyncMock) as mock_analyze,
    ):
        res = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze?user_id={owner_id}",
            cookies={"access_token": other_token},
            headers={"X-User-Id": owner_id},
            json={"user_id": owner_id},
        )
        assert res.status_code == 403
        mock_health.assert_not_awaited()
        mock_analyze.assert_not_awaited()

    insp_res = await db.execute(
        select(Inspection)
        .where(Inspection.id == sample_inspection_with_image)
        .execution_options(populate_existing=True)
    )
    assert insp_res.scalars().first().processing_status == "PENDING"


@pytest.mark.asyncio
async def test_analyze_unauthenticated_rejected(
    client: AsyncClient, sample_inspection_with_image, db: AsyncSession, mock_ai_client
):
    with (
        patch.object(mock_ai_client, "check_health", new_callable=AsyncMock) as mock_health,
        patch.object(mock_ai_client, "analyze", new_callable=AsyncMock) as mock_analyze,
    ):
        res = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze"
        )
        assert res.status_code == 401
        mock_health.assert_not_awaited()
        mock_analyze.assert_not_awaited()

    insp_res = await db.execute(
        select(Inspection)
        .where(Inspection.id == sample_inspection_with_image)
        .execution_options(populate_existing=True)
    )
    assert insp_res.scalars().first().processing_status == "PENDING"


@pytest.mark.asyncio
async def test_process_inspection_analysis_service_enforces_ownership(
    additional_test_users, sample_inspection_with_image, db: AsyncSession, mock_ai_client
):
    other_user = additional_test_users["user_b"]

    with (
        patch.object(mock_ai_client, "check_health", new_callable=AsyncMock) as mock_health,
        patch.object(mock_ai_client, "analyze", new_callable=AsyncMock) as mock_analyze,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await process_inspection_analysis(
                db=db,
                inspection_id=UUID(sample_inspection_with_image),
                current_user=other_user,
                ai_client=mock_ai_client,
            )
        assert exc_info.value.status_code == 403
        mock_health.assert_not_awaited()
        mock_analyze.assert_not_awaited()

    insp_res = await db.execute(
        select(Inspection)
        .where(Inspection.id == sample_inspection_with_image)
        .execution_options(populate_existing=True)
    )
    assert insp_res.scalars().first().processing_status == "PENDING"


@pytest.mark.asyncio
async def test_analyze_allowed_for_officer_and_admin(
    client: AsyncClient, setup_test_users, additional_test_users, sample_inspection_with_image, db: AsyncSession, mock_ai_client
):
    mock_response = mock_ai_client._generate_mock_response("test")

    with patch.object(mock_ai_client, "analyze", new_callable=AsyncMock, return_value=mock_response):
        res_officer = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": setup_test_users["officer_token"]},
        )
        assert res_officer.status_code == 200
        assert res_officer.json()["processing_status"] == "COMPLETED"

        res_admin = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": additional_test_users["admin_token"]},
        )
        assert res_admin.status_code == 200
        assert res_admin.json()["processing_status"] == "COMPLETED"

    audit_res = await db.execute(
        select(AuditLog).where(
            AuditLog.inspection_id == sample_inspection_with_image,
            AuditLog.action == "AI_ANALYSIS_COMPLETED",
        )
    )
    actor_ids = {log.user_id for log in audit_res.scalars().all()}
    assert setup_test_users["officer"].id in actor_ids
    assert additional_test_users["admin"].id in actor_ids


@pytest.mark.asyncio
async def test_analyze_locked_inspection_blocked(
    client: AsyncClient, setup_test_users, additional_test_users, sample_inspection_with_image, db: AsyncSession, mock_ai_client
):
    insp_res = await db.execute(select(Inspection).where(Inspection.id == sample_inspection_with_image))
    inspection = insp_res.scalars().first()
    inspection.review_status = "LOCKED"
    inspection.processing_status = "COMPLETED"
    await db.commit()

    with (
        patch.object(mock_ai_client, "check_health", new_callable=AsyncMock) as mock_health,
        patch.object(mock_ai_client, "analyze", new_callable=AsyncMock) as mock_analyze,
    ):
        # Unauthorized user is denied with 403 before status checks
        res_other = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": additional_test_users["user_b_token"]},
        )
        assert res_other.status_code == 403

        # Owner, Officer, and Admin are blocked from analyzing a LOCKED docket
        for token in (
            setup_test_users["user_token"],
            setup_test_users["officer_token"],
            additional_test_users["admin_token"],
        ):
            res = await client.post(
                f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
                cookies={"access_token": token},
            )
            assert res.status_code == 400
            assert "locked" in res.json()["detail"].lower()

        mock_health.assert_not_awaited()
        mock_analyze.assert_not_awaited()

    await db.refresh(inspection)
    assert inspection.processing_status == "COMPLETED"


@pytest.mark.asyncio
async def test_analyze_already_processing_inspection_blocked(
    client: AsyncClient, setup_test_users, additional_test_users, sample_inspection_with_image, db: AsyncSession, mock_ai_client
):
    insp_res = await db.execute(select(Inspection).where(Inspection.id == sample_inspection_with_image))
    inspection = insp_res.scalars().first()
    inspection.processing_status = "PROCESSING"
    await db.commit()

    with (
        patch.object(mock_ai_client, "check_health", new_callable=AsyncMock) as mock_health,
        patch.object(mock_ai_client, "analyze", new_callable=AsyncMock) as mock_analyze,
    ):
        # Unauthorized user is denied with 403 before status checks
        res_other = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": additional_test_users["user_b_token"]},
        )
        assert res_other.status_code == 403

        # Owner and Officer get 409 Conflict
        for token in (setup_test_users["user_token"], setup_test_users["officer_token"]):
            res = await client.post(
                f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
                cookies={"access_token": token},
            )
            assert res.status_code == 409
            assert "already being processed" in res.json()["detail"].lower()

        mock_health.assert_not_awaited()
        mock_analyze.assert_not_awaited()

    await db.refresh(inspection)
    assert inspection.processing_status == "PROCESSING"


@pytest.mark.asyncio
async def test_analyze_reanalysis_returns_updated_declarations(
    client: AsyncClient, setup_test_users, sample_inspection_with_image, mock_ai_client
):
    token = setup_test_users["user_token"]

    first_response = mock_ai_client._generate_mock_response("test")
    second_response = mock_ai_client._generate_mock_response("test")
    second_response.compliance.status = "COMPLIANT"
    second_response.violations = []
    second_response.corrective_actions = []
    second_response.declarations = [first_response.declarations[0].model_copy(update={"raw_value": "Rs 99"})]

    with patch.object(mock_ai_client, "analyze", new_callable=AsyncMock, side_effect=[first_response, second_response]):
        res1 = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": token},
        )
        assert res1.status_code == 200
        assert res1.json()["compliance_status"] == "NON_COMPLIANT"
        assert len(res1.json()["violations"]) == 1

        res2 = await client.post(
            f"{settings.API_V1_STR}/inspections/{sample_inspection_with_image}/analyze",
            cookies={"access_token": token},
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["compliance_status"] == "COMPLIANT"
        assert data2["violations"] == []
        assert [d["raw_value"] for d in data2["declarations"]] == ["Rs 99"]
