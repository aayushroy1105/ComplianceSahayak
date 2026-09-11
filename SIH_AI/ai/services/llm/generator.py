import json
import logging
from typing import List, Optional
from ai.schemas.base import Violation, CorrectiveAction
from ai.schemas.rag import RetrievalResult, RetrievalMode
from ai.services.llm.prompts import SYSTEM_PROMPT, build_prompt
from ai.services.llm.mock_provider import MockLLMProvider

logger = logging.getLogger(__name__)

class LLMGenerator:
    def __init__(self):
        self.provider = MockLLMProvider()

    def generate_corrections(self, violations: List[Violation], retrieval: RetrievalResult) -> List[CorrectiveAction]:
        corrective_actions = []
        
        for violation in violations:
            # 1. Exact Rule/Violation Context Binding
            matched_chunks = []
            if retrieval.retrieval_mode == RetrievalMode.AUTOMATIC:
                for chunk in retrieval.chunks:
                    if chunk.rule_id == violation.rule_id:
                        matched_chunks.append(chunk.text)
                        
            # REVIEW_ONLY retrieval or Missing Legal Context -> fail closed for this violation
            if not matched_chunks:
                logger.warning(f"No AUTOMATIC legal context found for rule {violation.rule_id}. Bypassing LLM.")
                continue
                
            legal_text = "\n\n".join(matched_chunks)
            user_prompt = build_prompt(
                violation_code=violation.violation_code,
                rule_id=violation.rule_id,
                violation_description=violation.description,
                legal_text=legal_text
            )
            
            try:
                # 2. LLM Call
                raw_response = self.provider.generate(SYSTEM_PROMPT, user_prompt)
                
                # 3. Structured Output Validation
                parsed = json.loads(raw_response)
                
                # Strict structural checks before accepting
                if not isinstance(parsed, dict):
                    raise ValueError("Response is not a JSON object")
                    
                # Must exactly contain violation_reference and action_text (status is optional but not returned by our prompt)
                allowed_keys = {"violation_reference", "action_text", "status"}
                if not set(parsed.keys()).issubset(allowed_keys):
                    raise ValueError(f"Unexpected structural fields in LLM response: {set(parsed.keys())}")
                    
                if "violation_reference" not in parsed or "action_text" not in parsed:
                    raise ValueError("Missing required fields in LLM response")
                    
                if parsed["violation_reference"] != violation.violation_code:
                    raise ValueError("LLM hallucinated a different violation_reference")
                    
                # Validate against Pydantic schema
                action = CorrectiveAction(**parsed)
                corrective_actions.append(action)
                
            except Exception as e:
                # 4. LLM Failure -> Fails closed safely
                logger.error(f"LLM generation failed for violation {violation.violation_code}: {e}")
                continue
                
        return corrective_actions
