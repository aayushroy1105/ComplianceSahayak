import hashlib
import os
from typing import List, Dict, Optional

class LegalRule:
    def __init__(self, rule_id: str, title: str, category: str, effective_from: str, applicability: str, raw_text: str = ""):
        self.rule_id = rule_id
        self.title = title
        self.category = category
        self.effective_from = effective_from
        self.applicability = applicability
        self.raw_text = raw_text

class LegalRuleCatalogue:
    def __init__(self):
        self.rules: Dict[str, LegalRule] = {}
        self.file_hash: Optional[str] = None
        self.rule_count: int = 0
        
    def load(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Legal rules file not found: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        blocks = content.split("# RULE ")
        
        for block in blocks[1:]:
            lines = [line.strip() for line in block.split('\n')]
            if not lines:
                continue
                
            rule_id = lines[0].strip()
            if not rule_id.startswith("LM-"):
                continue
                
            title = "UNKNOWN"
            category = "UNKNOWN"
            effective_from = "UNKNOWN"
            applicability = "UNKNOWN"
            
            raw_text_lines = []
            parsing_metadata = True
            
            for i, line in enumerate(lines):
                if line.startswith("## Title"):
                    title = lines[i+1] if i+1 < len(lines) else "UNKNOWN"
                elif line.startswith("## Category"):
                    category = lines[i+1] if i+1 < len(lines) else "UNKNOWN"
                elif line.startswith("## Effective From"):
                    effective_from = lines[i+1] if i+1 < len(lines) else "UNKNOWN"
                elif line.startswith("## Applicability"):
                    applicability = lines[i+1] if i+1 < len(lines) else "UNKNOWN"
                elif line.startswith("## Exact Preserved Text"):
                    parsing_metadata = False
                elif not parsing_metadata:
                    raw_text_lines.append(line)
                    
            raw_text = "\n".join(raw_text_lines).strip()
            # If the parser couldn't find the exact reserved text boundary, just use everything
            if not raw_text:
                raw_text = "\n".join(lines[1:]).strip()
                    
            rule = LegalRule(rule_id, title, category, effective_from, applicability, raw_text)
            self.rules[rule_id] = rule
            
        self.rule_count = len(self.rules)

    def get(self, rule_id: str) -> Optional[LegalRule]:
        return self.rules.get(rule_id)
        
    def all(self) -> List[LegalRule]:
        return list(self.rules.values())
        
    def version(self) -> Optional[str]:
        return self.file_hash
