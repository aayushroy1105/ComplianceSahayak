import json

class MockLLMProvider:
    def __init__(self):
        pass

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Mocks an LLM response.
        For deterministic testing, we can simulate specific outputs based on the input text.
        """
        
        # Simulate LLM failure for specific keywords
        if "SIMULATE_TIMEOUT" in user_prompt:
            raise TimeoutError("LLM timed out")
        
        if "SIMULATE_MALFORMED" in user_prompt:
            return "This is not valid JSON."
            
        if "SIMULATE_WRONG_REFERENCE" in user_prompt:
            return json.dumps({
                "violation_reference": "WRONG_REF",
                "action_text": "This reference is wrong."
            })
            
        if "SIMULATE_EXTRA_FIELDS" in user_prompt:
            return json.dumps({
                "violation_reference": self._extract_violation_code(user_prompt),
                "action_text": "Fix this.",
                "unexpected_field": "Should be rejected"
            })
            
        if "IGNORE" in user_prompt and "PROMPT_INJECTION" in user_prompt:
            # Our mock LLM ignores prompt injections just as the real one is instructed to
            pass
            
        violation_code = self._extract_violation_code(user_prompt)
        
        return json.dumps({
            "violation_reference": violation_code,
            "action_text": f"Please ensure compliance with the legal text regarding {violation_code}."
        })
        
    def _extract_violation_code(self, prompt: str) -> str:
        # Simple extraction for the mock based on the prompt template
        import re
        match = re.search(r'Violation Code: (\S+)', prompt)
        return match.group(1) if match else "UNKNOWN"
