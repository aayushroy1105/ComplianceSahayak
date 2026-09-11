from typing import Callable, List, Dict
from ai.services.rules.validators.presence import check_presence
import ai.services.rules.reason_codes as rc

# A rule validator function takes:
# declarations, rule_id
# and returns (bool, str, Evidence) - is_compliant, violation_code, evidence
RuleValidator = Callable

# EXPLICIT, HUMAN-VERIFIED RULE-TO-REQUIREMENT MAPPINGS.
# We do not infer these. They must be explicitly mapped here.

def validate_lm_005_mrp(declarations, rule_id):
    # Rule 6 (LM-005) explicitly requires Retail Sale Price (MRP)
    return check_presence(
        declarations=declarations,
        field_name="MRP",
        violation_code=rc.MISSING_MRP,
        rule_id=rule_id,
        description="MRP declaration is missing as required by Rule 6."
    )

def validate_lm_005_net_quantity(declarations, rule_id):
    # Rule 6 (LM-005) explicitly requires Net Quantity
    return check_presence(
        declarations=declarations,
        field_name="NET_QUANTITY",
        violation_code=rc.MISSING_NET_QUANTITY,
        rule_id=rule_id,
        description="Net Quantity declaration is missing as required by Rule 6."
    )

def validate_lm_005_manufacturer(declarations, rule_id):
    # Rule 6 (LM-005) explicitly requires Manufacturer/Packer/Importer
    return check_presence(
        declarations=declarations,
        field_name="MANUFACTURER",
        violation_code=rc.MISSING_MANUFACTURER,
        rule_id=rule_id,
        description="Manufacturer declaration is missing as required by Rule 6."
    )

# The deterministic registry mapping rule IDs to a list of validator functions
VALIDATOR_REGISTRY: Dict[str, List[RuleValidator]] = {
    "LM-005": [
        validate_lm_005_mrp,
        validate_lm_005_net_quantity,
        validate_lm_005_manufacturer
    ]
}

def get_validators_for_rule(rule_id: str) -> List[RuleValidator]:
    """
    Returns the explicitly mapped validators for a rule_id, or an empty list if unmapped.
    """
    return VALIDATOR_REGISTRY.get(rule_id, [])
