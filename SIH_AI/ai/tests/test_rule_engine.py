import pytest
from ai.schemas.base import Declaration, PackageContext
from ai.schemas.applicability import ApplicabilityResult
from ai.schemas.rag import RetrievalResult, RetrievalMode, RetrievedChunk
from ai.services.rules.engine import RuleEngine

@pytest.fixture
def engine():
    return RuleEngine()

@pytest.fixture
def pkg_context():
    return PackageContext(package_context="retail")

# 1. Compliance Pass
def test_compliance_pass(engine, pkg_context):
    declarations = [
        Declaration(field_name="MRP", confidence=0.99, extraction_status="FOUND"),
        Declaration(field_name="NET_QUANTITY", confidence=0.99, extraction_status="FOUND"),
        Declaration(field_name="MANUFACTURER", confidence=0.99, extraction_status="FOUND")
    ]
    applicability = ApplicabilityResult(
        status="CONFIRMED_APPLICABLE", 
        applicable_rule_ids=["LM-005"]
    )
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    
    compliance, violations, evidences, review, reason = engine.evaluate(declarations, applicability, retrieval, pkg_context)
    assert compliance.status == "COMPLIANT"
    assert len(violations) == 0
    assert not review

# 2. Missing Field Non-Compliance
def test_missing_field_non_compliance(engine, pkg_context):
    declarations = [
        Declaration(field_name="NET_QUANTITY", confidence=0.99, extraction_status="FOUND"),
        Declaration(field_name="MANUFACTURER", confidence=0.99, extraction_status="FOUND")
        # MRP is entirely missing from the list
    ]
    applicability = ApplicabilityResult(
        status="CONFIRMED_APPLICABLE", 
        applicable_rule_ids=["LM-005"]
    )
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    
    compliance, violations, evidences, review, reason = engine.evaluate(declarations, applicability, retrieval, pkg_context)
    assert compliance.status == "NON_COMPLIANT"
    assert len(violations) == 1
    assert violations[0].violation_code == "MISSING_MRP"
    assert "EVID_MISSING_MRP_LM-005" in violations[0].evidence_references
    assert len(evidences) == 1
    assert evidences[0].declaration_reference == "MRP"
    assert not review

# 3. Inconclusive Fallback
def test_inconclusive_fallback(engine, pkg_context):
    applicability = ApplicabilityResult(status="UNABLE_TO_DETERMINE", applicable_rule_ids=[])
    retrieval = RetrievalResult(
        query="test", retrieval_mode=RetrievalMode.AUTOMATIC, chunks=[], corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate([], applicability, retrieval, pkg_context)
    assert compliance.status == "INCONCLUSIVE"
    assert review is True
    assert reason == "APPLICABILITY_UNCERTAIN"

# 4. Extraneous Field Ignore
def test_extraneous_field_ignore(engine, pkg_context):
    declarations = [
        Declaration(field_name="MRP", confidence=0.99, extraction_status="FOUND"),
        Declaration(field_name="NET_QUANTITY", confidence=0.99, extraction_status="FOUND"),
        Declaration(field_name="MANUFACTURER", confidence=0.99, extraction_status="FOUND"),
        Declaration(field_name="RANDOM_FIELD", confidence=0.99, extraction_status="FOUND")
    ]
    applicability = ApplicabilityResult(
        status="CONFIRMED_APPLICABLE", 
        applicable_rule_ids=["LM-005"]
    )
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    
    compliance, violations, evidences, review, reason = engine.evaluate(declarations, applicability, retrieval, pkg_context)
    assert compliance.status == "COMPLIANT"
    assert len(violations) == 0

# 5. Violation Evidence Mapping
def test_violation_evidence_mapping(engine, pkg_context):
    declarations = [Declaration(field_name="MRP", confidence=0.99, extraction_status="MISSING")]
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-005"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate(declarations, applicability, retrieval, pkg_context)
    assert compliance.status == "NON_COMPLIANT"
    assert evidences[0].evidence_id == violations[0].evidence_references[0]
    assert evidences[0].rule_id == violations[0].rule_id

# 6. No Applicability Bypass
def test_no_applicability_bypass(engine, pkg_context):
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-001"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.REVIEW_ONLY,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate([], applicability, retrieval, pkg_context)
    assert compliance.status == "INCONCLUSIVE"
    assert review is True
    assert reason == "LEGAL_CONTEXT_INSUFFICIENT"

# 7. Unmapped Rule -> Inconclusive
def test_unmapped_rule_inconclusive(engine, pkg_context):
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-999"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-999", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate([], applicability, retrieval, pkg_context)
    assert compliance.status == "INCONCLUSIVE"
    assert review is True
    assert reason == "INSUFFICIENT_EVIDENCE"

# 8. REVIEW_ONLY Prevention
def test_review_only_prevention(engine, pkg_context):
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-005"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.REVIEW_ONLY,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate([], applicability, retrieval, pkg_context)
    assert compliance.status == "INCONCLUSIVE"
    assert review is True
    assert reason == "LEGAL_CONTEXT_INSUFFICIENT"

# 9. Phase 6 Veto
def test_phase_6_veto(engine, pkg_context):
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-001"]) # Not LM-005
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate([], applicability, retrieval, pkg_context)
    assert compliance.status == "INCONCLUSIVE"

# 10. Empty Declarations Safety
def test_empty_declarations_safety(engine, pkg_context):
    # Empty declarations against LM-005 (which expects 3 fields) -> NON_COMPLIANT directly
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-005"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate([], applicability, retrieval, pkg_context)
    assert compliance.status == "NON_COMPLIANT"
    assert len(violations) == 3

# 11. Unsupported Legal Requirement
def test_unsupported_legal_requirement(engine, pkg_context):
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-999"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-999", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate([], applicability, retrieval, pkg_context)
    assert compliance.status == "INCONCLUSIVE"
    assert len(violations) == 0

# 12. Conflicting Data
def test_conflicting_data(engine, pkg_context):
    declarations = [
        Declaration(field_name="MRP", confidence=0.99, extraction_status="CONFLICTING"),
        Declaration(field_name="NET_QUANTITY", confidence=0.99, extraction_status="FOUND"),
        Declaration(field_name="MANUFACTURER", confidence=0.99, extraction_status="FOUND")
    ]
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-005"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate(declarations, applicability, retrieval, pkg_context)
    assert compliance.status == "INCONCLUSIVE"
    assert review is True

# 13. Aggregation 1 (One NON_COMPLIANT, one INCONCLUSIVE)
def test_aggregation_1(engine, pkg_context):
    declarations = [
        Declaration(field_name="MRP", confidence=0.99, extraction_status="MISSING"),
        Declaration(field_name="NET_QUANTITY", confidence=0.99, extraction_status="UNCERTAIN"),
        Declaration(field_name="MANUFACTURER", confidence=0.99, extraction_status="FOUND")
    ]
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-005"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate(declarations, applicability, retrieval, pkg_context)
    assert compliance.status == "NON_COMPLIANT" # Confirmed violation takes precedence
    assert violations[0].violation_code == "MISSING_MRP"

# 14. Aggregation 2 (All pass)
def test_aggregation_2(engine, pkg_context):
    # Same as test 1
    test_compliance_pass(engine, pkg_context)

# 15. Missing Provenance
def test_missing_provenance(engine, pkg_context):
    # Rule engine evaluates only rules that were BOTH in applicable_rule_ids AND actually retrieved
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-005"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[], # Missing provenance (not retrieved)
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate([], applicability, retrieval, pkg_context)
    assert compliance.status == "INCONCLUSIVE"

# 16. Evidence Integrity
def test_evidence_integrity(engine, pkg_context):
    declarations = [Declaration(field_name="MRP", confidence=0.99, extraction_status="MISSING")]
    applicability = ApplicabilityResult(status="CONFIRMED_APPLICABLE", applicable_rule_ids=["LM-005"])
    retrieval = RetrievalResult(
        query="test",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="", score=1.0, source_document="", source_section="", corpus_hash="", chunk_index=0)],
        corpus_hash="test"
    )
    compliance, violations, evidences, review, reason = engine.evaluate(declarations, applicability, retrieval, pkg_context)
    assert evidences[0].declaration_reference == "MRP"
    assert evidences[0].evidence_id.startswith("EVID_MISSING_MRP")
