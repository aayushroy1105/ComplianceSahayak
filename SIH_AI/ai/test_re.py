import re
texts = ["30 ml / 1.01 fl. oz.", "Amoxycillin Trihydrate IP 500 mg", "Minimalist 30ml"]
for t in texts:
    cleaned = re.sub(r'(?i)ml|g|kg|l|fl|oz|pieces|capsules|tablets|mg', '', t)
    cleaned = re.sub(r'[\d\s./\-]', '', cleaned)
    print(f"Original: {t} -> Cleaned: '{cleaned}' length: {len(cleaned.strip())}")
