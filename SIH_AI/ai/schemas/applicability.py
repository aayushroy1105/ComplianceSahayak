from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class RuleApplicabilityStatus(str, Enum):
    CONFIRMED_APPLICABLE = "CONFIRMED_APPLICABLE"
    CANDIDATE = "CANDIDATE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNABLE_TO_DETERMINE = "UNABLE_TO_DETERMINE"

class RuleEvaluation(BaseModel):
    rule_id: str
    status: RuleApplicabilityStatus
    reasons: List[str]

class ApplicabilityResult(BaseModel):
    status: str
    applicable_rule_ids: List[str] = []
    candidate_rule_ids: List[str] = []
    excluded_rule_ids: List[str] = []
    rule_evaluations: List[RuleEvaluation] = []
    review_required: bool = False
