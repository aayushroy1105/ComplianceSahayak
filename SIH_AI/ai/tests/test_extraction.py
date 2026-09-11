import pytest
from services.extraction.extractor import DeclarationExtractor

def test_mrp_extraction():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "MRP Rs. 120.00", "confidence": 0.99, "bbox": [10, 10, 50, 50]}
    ]
    decls = extractor.extract(blocks)
    mrp = next(d for d in decls if d.field_name == "MRP")
    assert mrp.extraction_status == "FOUND"
    assert mrp.normalized_value == 120.0
    assert mrp.normalized_unit == "INR"
    assert mrp.raw_value == "MRP Rs. 120.00"

def test_quantity_extraction():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "Net Qty: 1 kg", "confidence": 0.95, "bbox": [10, 10, 50, 50]}
    ]
    decls = extractor.extract(blocks)
    qty = next(d for d in decls if d.field_name == "NET_QUANTITY")
    assert qty.extraction_status == "FOUND"
    assert qty.normalized_value == 1000
    assert qty.normalized_unit == "g"

def test_ocr_imperfection_uncertain():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "MRP8150", "confidence": 0.90, "bbox": [10, 10, 50, 50]}
    ]
    decls = extractor.extract(blocks)
    mrp = next(d for d in decls if d.field_name == "MRP")
    assert mrp.extraction_status == "UNCERTAIN"
    assert mrp.normalized_value is None

def test_conflict_handling():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "MRP ₹120", "confidence": 0.99, "bbox": [10, 10, 50, 50]},
        {"text": "MRP ₹150", "confidence": 0.98, "bbox": [10, 60, 50, 90]}
    ]
    decls = extractor.extract(blocks)
    mrp = next(d for d in decls if d.field_name == "MRP")
    assert mrp.extraction_status == "CONFLICTING"
    assert mrp.normalized_value is None

def test_missing_handling():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "Random Text", "confidence": 0.99, "bbox": [10, 10, 50, 50]}
    ]
    decls = extractor.extract(blocks)
    mrp = next(d for d in decls if d.field_name == "MRP")
    assert mrp.extraction_status == "MISSING"
    assert mrp.normalized_value is None

def test_date_extraction():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "Mfg Date: 05/09/2026", "confidence": 0.99, "bbox": [10, 10, 50, 50]}
    ]
    decls = extractor.extract(blocks)
    date = next(d for d in decls if d.field_name == "MANUFACTURING_DATE")
    assert date.extraction_status == "FOUND"
    assert date.normalized_value == "2026-09-05"

def test_country_of_origin():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "CountryofOrigin: India", "confidence": 0.99, "bbox": [0, 0, 10, 10]}
    ]
    decls = extractor.extract(blocks)
    coo = next(d for d in decls if d.field_name == "COUNTRY_OF_ORIGIN")
    assert coo.extraction_status == "FOUND"
    assert coo.normalized_value == "India"

from pydantic import ValidationError
from schemas.base import Declaration

def test_pydantic_rejects_arbitrary_object():
    with pytest.raises(ValidationError):
        Declaration(
            field_name="MRP",
            extraction_status="FOUND",
            normalized_value={"invalid": "object"},
            confidence=0.9
        )

def test_multiline_manufacturer_same_block():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "Manufactured & Marketed By: HALDIRAM SNACKS PVT. LTD.,", "confidence": 0.99, "bbox": [10, 10, 500, 50]}
    ]
    decls = extractor.extract(blocks)
    mfg = next(d for d in decls if d.field_name == "MANUFACTURER")
    assert mfg.extraction_status == "FOUND"
    assert mfg.normalized_value == "Haldiram Snacks Pvt. Ltd.,"

def test_multiline_manufacturer_nearby_value():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "Manufactured & Marketed By:", "confidence": 0.99, "bbox": [10, 10, 200, 50]},
        {"text": "HALDIRAM SNACKS PVT. LTD.,", "confidence": 0.99, "bbox": [10, 60, 200, 90]}
    ]
    decls = extractor.extract(blocks)
    mfg = next(d for d in decls if d.field_name == "MANUFACTURER")
    assert mfg.extraction_status == "FOUND"
    assert mfg.normalized_value == "Haldiram Snacks Pvt. Ltd.,"
    assert "Manufactured & Marketed By:\nHALDIRAM SNACKS PVT. LTD.," in mfg.raw_value

def test_multiline_manufacturer_ignore_unrelated():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "Manufactured & Marketed By:", "confidence": 0.99, "bbox": [469, 247, 682, 269]},
        {"text": "NUTRITIONALINFORMATION", "confidence": 0.99, "bbox": [97, 259, 412, 273]}, # Horizontally far
        {"text": "Approximate Values)", "confidence": 0.99, "bbox": [96, 272, 264, 285]},   # Horizontally far
        {"text": "HALDIRAM SNACKS PVT. LTD.,", "confidence": 0.99, "bbox": [469, 263, 742, 285]} # Vertically below, same X
    ]
    decls = extractor.extract(blocks)
    mfg = next(d for d in decls if d.field_name == "MANUFACTURER")
    assert mfg.extraction_status == "FOUND"
    assert mfg.normalized_value == "Haldiram Snacks Pvt. Ltd.,"
    assert "HALDIRAM" in mfg.raw_value
    assert "NUTRITIONAL" not in mfg.raw_value

def test_netweight_no_space():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "NETWEIGHT:440g", "confidence": 0.99, "bbox": [10, 10, 50, 50]}
    ]
    decls = extractor.extract(blocks)
    qty = next(d for d in decls if d.field_name == "NET_QUANTITY")
    assert qty.extraction_status == "FOUND"
    assert qty.normalized_value == 440
    assert qty.normalized_unit == "g"

def test_country_of_origin_product_of():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "PRODUCT OF INDIA", "confidence": 0.99, "bbox": [10, 10, 50, 50]}
    ]
    decls = extractor.extract(blocks)
    coo = next(d for d in decls if d.field_name == "COUNTRY_OF_ORIGIN")
    assert coo.extraction_status == "FOUND"
    assert coo.normalized_value == "India"

def test_mrpr_uncertain():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "MRPR", "confidence": 0.99, "bbox": [10, 10, 50, 50]}
    ]
    decls = extractor.extract(blocks)
    mrp = next(d for d in decls if d.field_name == "MRP")
    assert mrp.extraction_status == "UNCERTAIN"

def test_ambiguous_manufacturing_date():
    extractor = DeclarationExtractor()
    blocks = [
        {"text": "Batch No. and Manufacturing Date) to :", "confidence": 0.99, "bbox": [10, 10, 50, 50]},
        {"text": "MFG: DATE:", "confidence": 0.99, "bbox": [10, 60, 50, 90]}
    ]
    decls = extractor.extract(blocks)
    date = next(d for d in decls if d.field_name == "MANUFACTURING_DATE")
    # Due to no specific date format found, it defaults to UNCERTAIN
    assert date.extraction_status == "UNCERTAIN"
