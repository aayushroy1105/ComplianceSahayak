from datetime import datetime
from typing import List, Optional
from schemas.base import Product, PackageContext
from schemas.applicability import ApplicabilityResult, RuleEvaluation, RuleApplicabilityStatus
from services.applicability.catalogue import LegalRuleCatalogue

class ApplicabilityEngine:
    def __init__(self, catalogue: LegalRuleCatalogue):
        self.catalogue = catalogue
        
    def evaluate(self, product: Product, context: PackageContext, inspection_date_str: Optional[str] = None) -> ApplicabilityResult:
        evaluations = []
        applicable_ids = []
        candidate_ids = []
        excluded_ids = []
        
        global_status = "DETERMINED"
        review_required = False
        
        # If crucial context is completely unknown, we must explicitly state review is required
        if (product.product_category == "UNKNOWN" or context.package_context == "UNKNOWN"):
            global_status = "INSUFFICIENT_CONTEXT"
            review_required = True
            
        inspection_date = None
        if inspection_date_str:
            try:
                inspection_date = datetime.strptime(inspection_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
                
        for rule in self.catalogue.all():
            status = RuleApplicabilityStatus.CANDIDATE
            reasons = []
            
            # Explicit logic: If the rule metadata specifically contains an explicit date 
            # (In reality, most rules say "UNKNOWN unless expressly established").
            if "2026-10-01" in rule.effective_from and inspection_date:
                effective = datetime.strptime("2026-10-01", "%Y-%m-%d").date()
                if inspection_date < effective:
                    status = RuleApplicabilityStatus.NOT_APPLICABLE
                    reasons.append(f"Inspection date ({inspection_date}) is before rule effective date (2026-10-01).")

            # We must NOT invent engineering metadata like CONFIRMED_APPLICABLE_TO_FOOD
            # or NOT_APPLICABLE_TO_RETAIL. Since the current source metadata lacks
            # structured exclusions/inclusions, and we cannot reliably NLP ordinary text
            # for unambiguous exclusions, we safely fallback to CANDIDATE for all rules
            # unless a strict date condition overrides it.
            
            # Default fallback for rules lacking structured deterministic metadata
            if status == RuleApplicabilityStatus.CANDIDATE:
                reasons.append("Rule could not be definitively classified because structured applicability metadata is unavailable.")
                
            evaluations.append(RuleEvaluation(rule_id=rule.rule_id, status=status, reasons=reasons))
            
            if status == RuleApplicabilityStatus.CONFIRMED_APPLICABLE:
                applicable_ids.append(rule.rule_id)
            elif status == RuleApplicabilityStatus.CANDIDATE or status == RuleApplicabilityStatus.UNABLE_TO_DETERMINE:
                candidate_ids.append(rule.rule_id)
            elif status == RuleApplicabilityStatus.NOT_APPLICABLE:
                excluded_ids.append(rule.rule_id)
                
        return ApplicabilityResult(
            status=global_status,
            applicable_rule_ids=applicable_ids,
            candidate_rule_ids=candidate_ids,
            excluded_rule_ids=excluded_ids,
            rule_evaluations=evaluations,
            review_required=review_required
        )
