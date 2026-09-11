from typing import List, Tuple, Optional
from ai.schemas.base import Declaration, PackageContext, Compliance, Violation, Evidence
from ai.schemas.applicability import ApplicabilityResult
from ai.schemas.rag import RetrievalResult, RetrievalMode
from ai.services.rules.registry import get_validators_for_rule

class RuleEngine:
    def evaluate(
        self, 
        declarations: List[Declaration],
        applicability: ApplicabilityResult,
        retrieval: RetrievalResult,
        package_context: PackageContext
    ) -> Tuple[Compliance, List[Violation], List[Evidence], bool, Optional[str]]:
        """
        Deterministically evaluates declarations against applicable, retrieved rules.
        """
        
        # 1. Applicability Gate
        # Using exact string to match the schema representation
        if applicability.status == "UNABLE_TO_DETERMINE":
            return Compliance(status="INCONCLUSIVE"), [], [], True, "APPLICABILITY_UNCERTAIN"
            
        # 2. Retrieval Mode Gate
        if retrieval.retrieval_mode == RetrievalMode.REVIEW_ONLY:
            return Compliance(status="INCONCLUSIVE"), [], [], True, "LEGAL_CONTEXT_INSUFFICIENT"
            
        # 3. Determine rules to evaluate
        allowed_rule_ids = set(applicability.applicable_rule_ids + applicability.candidate_rule_ids)
        retrieved_rule_ids = {chunk.rule_id for chunk in retrieval.chunks}
        
        # Only evaluate rules that Phase 6 allowed AND Phase 7 retrieved automatically
        rules_to_evaluate = allowed_rule_ids.intersection(retrieved_rule_ids)
        
        if not rules_to_evaluate:
            if allowed_rule_ids:
                # We expected some rules but didn't retrieve them, cannot conclude compliance
                return Compliance(status="INCONCLUSIVE"), [], [], True, "LEGAL_CONTEXT_INSUFFICIENT"
            else:
                # No rules apply -> technically compliant
                return Compliance(status="COMPLIANT"), [], [], False, None
                
        violations: List[Violation] = []
        evidences: List[Evidence] = []
        has_inconclusive = False
        
        for rule_id in rules_to_evaluate:
            validators = get_validators_for_rule(rule_id)
            if not validators:
                # Unmapped rule -> force INCONCLUSIVE (we cannot reliably say it is compliant)
                has_inconclusive = True
                continue
                
            for validator in validators:
                result = validator(declarations, rule_id)
                # result: (is_compliant: bool|None, violation_code: str|None, evidence: Evidence|None)
                is_compliant, v_code, evidence = result
                
                if is_compliant is False:
                    violation = Violation(
                        violation_code=v_code,
                        rule_id=rule_id,
                        description=evidence.description if evidence else "Violation detected",
                        evidence_references=[evidence.evidence_id] if evidence else []
                    )
                    violations.append(violation)
                    if evidence:
                        evidences.append(evidence)
                elif is_compliant is None:
                    # e.g., missing evidence model support or conflicting data
                    has_inconclusive = True
                    
        # 4. Deterministic Compliance Aggregation Precedence
        
        # Any confirmed violation -> NON_COMPLIANT
        if violations:
            return Compliance(status="NON_COMPLIANT"), violations, evidences, False, None
            
        # No violations, but some required evaluation couldn't be done reliably
        if has_inconclusive:
            return Compliance(status="INCONCLUSIVE"), [], [], True, "INSUFFICIENT_EVIDENCE"
            
        # No violations and all required evaluated rules deterministically satisfied
        return Compliance(status="COMPLIANT"), [], [], False, None
