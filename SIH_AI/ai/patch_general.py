with open("services/extraction/extractor.py", "r") as f:
    content = f.read()

old_general = """            # General
            for gen in ["COUNTRY_OF_ORIGIN", "CONSUMER_CARE"]:
                status, n_val, n_unit, exact_raw = parse_general(raw_text, norm_text, gen)
                if status != "MISSING":
                    results[gen].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))"""

new_general = """            # General
            for gen in ["COUNTRY_OF_ORIGIN", "CONSUMER_CARE"]:
                status, n_val, n_unit, exact_raw = parse_general(raw_text, norm_text, gen)
                if status != "MISSING":
                    # For consumer care, if the extracted value is very short, check next block
                    if gen == "CONSUMER_CARE" and len(str(n_val)) < 15:
                        for j in range(i + 1, min(len(blocks), i + 6)):
                            if is_spatially_close(bbox, blocks[j].get('bbox', None)):
                                combined = raw_text + " " + blocks[j]['text']
                                s, nv, nu, ex = parse_general(combined, normalize_ocr_text(combined), gen)
                                if s != "MISSING":
                                    results[gen].append((s, nv, nu, ex or combined, conf, blocks[j].get('bbox', None)))
                                    break
                    else:
                        results[gen].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
                else:
                    if gen == "CONSUMER_CARE":
                        care_aliases = ["consumer care", "customer care", "feedback", "consumer complaints", "complaints", "complaints / queries", "customer complaints", "queries", "consumer queries"]
                        if any(a in norm_text for a in care_aliases):
                            for j in range(i + 1, min(len(blocks), i + 6)):
                                if is_spatially_close(bbox, blocks[j].get('bbox', None)):
                                    combined = raw_text + " " + blocks[j]['text']
                                    s, nv, nu, ex = parse_general(combined, normalize_ocr_text(combined), gen)
                                    if s != "MISSING":
                                        results[gen].append((s, nv, nu, ex or combined, conf, blocks[j].get('bbox', None)))
                                        break"""

content = content.replace(old_general, new_general)
with open("services/extraction/extractor.py", "w") as f:
    f.write(content)
print("general patched")
