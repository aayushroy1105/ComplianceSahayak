import pytest
from services.classification.product_classifier import ProductClassifier
from services.classification.context_classifier import ContextClassifier
from schemas.base import Declaration

def test_product_food():
    classifier = ProductClassifier()
    blocks = [{"text": "ingredients: wheat, sugar, edible fat"}]
    product = classifier.classify([], blocks)
    assert product.product_category == "FOOD"
    assert product.classification_confidence > 0.0
    assert "keyword:ingredients" in product.signals
    assert product.classification_method == "HEURISTIC"

def test_product_conflict():
    classifier = ProductClassifier()
    # Both food and cosmetic strong signals
    blocks = [{"text": "ingredients nutritional cosmetic skin cream"}]
    product = classifier.classify([], blocks)
    assert product.product_category == "UNKNOWN"
    assert product.classification_confidence == 0.0
    assert "conflict:multiple_strong_signals" in product.signals

def test_product_unknown():
    classifier = ProductClassifier()
    blocks = [{"text": "random stuff without any markers"}]
    product = classifier.classify([], blocks)
    assert product.product_category == "UNKNOWN"
    assert product.classification_confidence == 0.0
    assert len(product.signals) == 0

def test_context_mrp_weak_signal():
    classifier = ContextClassifier()
    decls = [Declaration(field_name="MRP", extraction_status="FOUND", confidence=0.9)]
    context = classifier.classify(decls, [{"text": "MRP Rs 100"}])
    # MRP alone is score 1.0. The threshold for RETAIL is 1.5 now. Should be UNKNOWN.
    assert context.package_context == "UNKNOWN"
    assert context.context_confidence == 0.0
    assert context.relevant_metadata["mrp_signal"] is True

def test_context_ambiguous_wholesale():
    classifier = ContextClassifier()
    decls = [Declaration(field_name="MRP", extraction_status="FOUND", confidence=0.9)]
    context = classifier.classify(decls, [{"text": "MRP Rs 100 not for retail sale wholesale pack"}])
    # Wholesale string overrides MRP retail signal completely
    assert context.package_context == "WHOLESALE"
    assert context.context_confidence > 0.0

def test_context_importer_weak():
    classifier = ContextClassifier()
    decls = [Declaration(field_name="IMPORTER", extraction_status="FOUND", confidence=0.9)]
    context = classifier.classify(decls, [{"text": "Imported by XYZ"}])
    # Importer alone is score 1.0 -> UNKNOWN
    assert context.package_context == "UNKNOWN"
    assert context.relevant_metadata["importer_signal"] is True

def test_context_imported_strong():
    classifier = ContextClassifier()
    decls = [
        Declaration(field_name="COUNTRY_OF_ORIGIN", extraction_status="FOUND", normalized_value="China", confidence=0.9),
        Declaration(field_name="IMPORTER", extraction_status="FOUND", confidence=0.9)
    ]
    context = classifier.classify(decls, [{"text": "Imported by XYZ"}])
    # Importer + COO(China) = 2.0 -> IMPORTED
    assert context.package_context == "IMPORTED"
    assert context.context_confidence == 0.9

def test_context_unknown():
    classifier = ContextClassifier()
    context = classifier.classify([], [{"text": "plain box"}])
    assert context.package_context == "UNKNOWN"
    assert context.context_confidence == 0.0
