from typing import List, Optional, Tuple
from ai.schemas.base import Declaration, Evidence
import ai.services.rules.reason_codes as rc

def check_presence(
    declarations: List[Declaration],
    field_name: str,
    violation_code: str,
    rule_id: str,
    description: str
) -> Tuple[bool, Optional[str], Optional[Evidence]]:
    """
    Checks if a mandatory field is present in the declarations list.
    Returns (is_compliant, violation_code, evidence_object).
    """
    # Find the declaration
    decl = next((d for d in declarations if d.field_name == field_name), None)
    
    # If the declaration is missing entirely or explicitly marked as MISSING
    if decl is None or decl.extraction_status == "MISSING":
        evidence = Evidence(
            evidence_id=f"EVID_MISSING_{field_name}_{rule_id}",
            evidence_type="MISSING_FIELD",
            declaration_reference=field_name,
            rule_id=rule_id,
            description=f"System failed to find any valid {field_name.replace('_', ' ').lower()} declaration."
        )
        return False, violation_code, evidence
    
    # If the declaration is UNCERTAIN or CONFLICTING, it cannot establish deterministic compliance
    if decl.extraction_status in ["UNCERTAIN", "CONFLICTING"]:
        # We don't return False (NON_COMPLIANT), we return a special state to trigger INCONCLUSIVE
        return None, None, None  # Let the engine handle inconclusive fallback
        
    return True, None, None
