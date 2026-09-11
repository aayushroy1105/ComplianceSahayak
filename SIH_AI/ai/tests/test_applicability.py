import pytest
from datetime import date
from schemas.base import Product, PackageContext
from schemas.applicability import RuleApplicabilityStatus, ApplicabilityResult
from services.applicability.catalogue import LegalRuleCatalogue, LegalRule
from services.applicability.engine import ApplicabilityEngine

@pytest.fixture
def test_catalogue():
    cat = LegalRuleCatalogue()
    cat.rules = {
        "LM-001": LegalRule("LM-001", "Short title", "GENERAL", "UNKNOWN", "UNKNOWN"),
        "SYNTHETIC-LM-TEST-002": LegalRule("SYNTHETIC-LM-TEST-002", "Date Test", "GENERAL", "2026-10-01", "UNKNOWN"),
        "SYNTHETIC-LM-TEST-003": LegalRule("SYNTHETIC-LM-TEST-003", "Exclusion Test", "GENERAL", "UNKNOWN", "NOT_APPLICABLE_TO_RETAIL"),
        "SYNTHETIC-LM-TEST-004": LegalRule("SYNTHETIC-LM-TEST-004", "Inclusion Test", "GENERAL", "UNKNOWN", "CONFIRMED_APPLICABLE_TO_FOOD"),
    }
    cat.rule_count = 4
    return cat

@pytest.fixture
def engine(test_catalogue):
    return ApplicabilityEngine(test_catalogue)

def test_startup_parsing(tmp_path):
    # Test 1 & 2: Startup parsing and rule catalogue loading
    # Create a small fake markdown file mimicking the real one
    fake_md = """# LEGAL METROLOGY — VERIFIED SOURCE CORPUS

# RULE LM-001
## Title
Title 1
## Category
GENERAL
## Effective From
UNKNOWN
## Applicability
UNKNOWN

# RULE LM-002
## Title
Title 2
"""
    p = tmp_path / "fake_rules.md"
    p.write_text(fake_md)
    cat = LegalRuleCatalogue()
    cat.load(str(p))
    assert cat.rule_count == 2
    assert cat.get("LM-001").title == "Title 1"
    assert cat.get("LM-002").title == "Title 2"

def test_malformed_rule(tmp_path):
    # Test 4: Malformed rule and INDEX exclusion
    fake_md = """# RULE LM-BROKEN\njust random text\n# RULE INDEX\nTitle\n"""
    p = tmp_path / "fake_rules.md"
    p.write_text(fake_md)
    cat = LegalRuleCatalogue()
    cat.load(str(p))
    assert cat.get("LM-BROKEN").title == "UNKNOWN"
    assert "INDEX" not in cat.rules
    assert cat.rule_count == 1

def test_rule_lookup(test_catalogue):
    # Test 5: rule lookup
    rule = test_catalogue.get("LM-001")
    assert rule.rule_id == "LM-001"

def test_catalogue_real_count():
    import os
    cat = LegalRuleCatalogue()
    rules_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "legal_metrology_rules.md")
    if os.path.exists(rules_path):
        cat.load(rules_path)
        assert cat.rule_count == 31
        assert len(cat.rules) == 31
        expected_ids = [f"LM-{str(i).zfill(3)}" for i in range(1, 32)]
        for expected_id in expected_ids:
            assert expected_id in cat.rules
        assert "INDEX" not in cat.rules

def test_candidate_rule(engine):
    # Test 6: candidate rule
    product = Product(product_category="FOOD")
    context = PackageContext(package_context="DOMESTIC")
    res = engine.evaluate(product, context)
    assert "LM-001" in res.candidate_rule_ids
    assert res.status == "DETERMINED"

def test_confirmed_applicability(engine):
    # Test 7: confirmed applicability only where explicitly supported
    # Since we removed fabricated metadata parsing, this rule now falls back to CANDIDATE.
    product = Product(product_category="FOOD")
    context = PackageContext(package_context="DOMESTIC")
    res = engine.evaluate(product, context)
    assert "SYNTHETIC-LM-TEST-004" in res.candidate_rule_ids

def test_not_applicable(engine):
    # Test 8: not-applicable only where explicitly supported
    # Removed fabricated metadata means this rule now falls back to CANDIDATE.
    product = Product(product_category="FOOD")
    context = PackageContext(package_context="RETAIL")
    res = engine.evaluate(product, context)
    assert "SYNTHETIC-LM-TEST-003" in res.candidate_rule_ids

def test_unknown_product(engine):
    # Test 10: unknown product
    product = Product(product_category="UNKNOWN")
    context = PackageContext(package_context="RETAIL")
    res = engine.evaluate(product, context)
    assert res.status == "INSUFFICIENT_CONTEXT"
    assert res.review_required is True

def test_unknown_context(engine):
    # Test 11: unknown context
    product = Product(product_category="FOOD")
    context = PackageContext(package_context="UNKNOWN")
    res = engine.evaluate(product, context)
    assert res.status == "INSUFFICIENT_CONTEXT"
    assert res.review_required is True

def test_unknown_effective_date(engine):
    # Test 13: unknown effective date
    product = Product(product_category="FOOD")
    context = PackageContext(package_context="RETAIL")
    res = engine.evaluate(product, context)
    # LM-001 has UNKNOWN effective date, should be candidate
    assert "LM-001" in res.candidate_rule_ids

def test_supported_effective_date_before(engine):
    # Test 14: supported effective date, inspection is before effective date
    product = Product(product_category="FOOD")
    context = PackageContext(package_context="RETAIL")
    res = engine.evaluate(product, context, "2026-09-01")
    # SYNTHETIC-LM-TEST-002 has 2026-10-01 effective date, so 09-01 is before it -> NOT_APPLICABLE
    assert "SYNTHETIC-LM-TEST-002" in res.excluded_rule_ids

def test_supported_effective_date_after(engine):
    product = Product(product_category="FOOD")
    context = PackageContext(package_context="RETAIL")
    res = engine.evaluate(product, context, "2026-11-01")
    # After effective date -> candidate (since no explicit inclusion metadata)
    assert "SYNTHETIC-LM-TEST-002" in res.candidate_rule_ids

def test_multiple_candidate_rules(engine):
    # Test 16: multiple candidate rules
    product = Product(product_category="HOUSEHOLD")
    context = PackageContext(package_context="WHOLESALE")
    res = engine.evaluate(product, context)
    # All 4 rules will be candidate since they lack explicit metadata for HOUSEHOLD/WHOLESALE
    assert len(res.candidate_rule_ids) == 4

def test_traceability(engine):
    product = Product(product_category="FOOD")
    context = PackageContext(package_context="DOMESTIC")
    res = engine.evaluate(product, context)
    eval_lm001 = next(r for r in res.rule_evaluations if r.rule_id == "LM-001")
    assert "metadata is unavailable" in eval_lm001.reasons[0]
