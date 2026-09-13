with open("services/extraction/parsers/date_parser.py", "r") as f:
    content = f.read()

old_sort = """        valid_cands = [c for c in candidates if c[2] >= alias_pos - 10]
        if valid_cands:
            # Sort by distance from alias_pos
            valid_cands.sort(key=lambda x: x[2] - alias_pos)
            best_candidate = valid_cands[0]"""

new_sort = """        valid_cands = [c for c in candidates if c[2] >= alias_pos - 4]
        if valid_cands:
            # Sort by positive distance from alias_pos
            valid_cands.sort(key=lambda x: x[2] - alias_pos)
            best_candidate = valid_cands[0]"""
content = content.replace(old_sort, new_sort)
with open("services/extraction/parsers/date_parser.py", "w") as f:
    f.write(content)
print("date patched")
