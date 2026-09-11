import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from unittest.mock import patch, AsyncMock
from uuid import UUID

from app.core.config import settings
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
