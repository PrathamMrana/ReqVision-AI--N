import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.classifier import classify_document
from utils.preprocess import get_sentences, clean_text
from utils.analyzer import (
    analyze_quality,
    detect_priority,
    calculate_complexity,
    generate_recommendations,
    generate_engineering_impact
)
from utils.matcher import get_detected_changes, get_confidence_score
from analytics.modules import get_module_impact

def classify_doc_type(text, filename=""):
    """
    Classifies the document using content signals and filename heuristics.
    """
    doc_type, confidence, signals = classify_document(text, filename)
    
    # If ambiguous or unknown, use filename heuristics to resolve
    if doc_type == "Unknown" and filename:
        fn_lower = filename.lower()
        if re.search(r'\b(brd|business)\b', fn_lower) or "brd" in fn_lower:
            return "BRD"
        elif re.search(r'\b(cr|change[_\s-]?request)\b', fn_lower) or "change" in fn_lower or "cr" in fn_lower:
            return "Change Request"
        elif re.search(r'\b(srs|software[_\s-]?req)\b', fn_lower) or "srs" in fn_lower:
            return "SRS"
        elif re.search(r'\b(frd|functional)\b', fn_lower) or "frd" in fn_lower:
            return "FRD"
        elif re.search(r'\b(user[_\s-]?stor|story)\b', fn_lower):
            return "User Story"
        elif re.search(r'\b(test[_\s-]?case|qa|test)\b', fn_lower):
            return "Test Case"
        elif re.search(r'\b(release[_\s-]?note)\b', fn_lower):
            return "Release Notes"
        elif re.search(r'\b(meeting[_\s-]?min|mom)\b', fn_lower):
            return "Meeting Minutes"
        return "SRS"
        
    return doc_type if doc_type != "Unknown" else "SRS"


def extract_document_requirements(doc_id, doc_name, doc_type, side, text):
    """
    Extracts individual requirement objects preserving document provenance.
    """
    raw_sents = get_sentences(text)
    prefix_map = {
        "BRD": "BRD",
        "Change Request": "CR",
        "SRS": "REQ",
        "FRD": "FR",
        "User Story": "US",
        "Test Case": "TC",
        "Release Notes": "RN",
        "Meeting Minutes": "MOM"
    }
    default_prefix = prefix_map.get(doc_type, "REQ")
    
    req_objects = []
    for i, s in enumerate(raw_sents):
        req_id = s.get("id") or f"{default_prefix}-{(i+1):03d}"
        clean = clean_text(s["text"])
        req_objects.append({
            "requirement_id": req_id,
            "document_id": doc_id,
            "document_name": doc_name,
            "document_type": doc_type,
            "side": side,
            "text": s["text"],
            "clean_text": clean,
            "section": "General"
        })
        
    return req_objects


def analyze_cross_documents(baseline_payload, updated_payload):
    """
    Executes True Cross-Document Analysis:
    1. Extracts requirements with document provenance.
    2. Runs lexical requirement matching across baseline and updated collections.
    3. Identifies cross-document relationships (SAME_REQUIREMENT, MODIFIED_FROM, ADDED_IN, REMOVED_FROM).
    4. Computes Change Request <-> SRS linking (AFFECTS).
    5. Computes BRD <-> SRS traceability (TRACEABLE_TO).
    6. Constructs Traceability Matrix and Cross-Document statistics.
    """
    # 1. Normalize Payload inputs
    if isinstance(baseline_payload, str):
        baseline_payload = [{"name": "Baseline Document", "text": baseline_payload}]
    if isinstance(updated_payload, str):
        updated_payload = [{"name": "Updated Document", "text": updated_payload}]

    documents_meta = []
    baseline_reqs = []
    updated_reqs = []

    # Process Baseline Documents
    for idx, doc in enumerate(baseline_payload):
        doc_name = doc.get("name") or f"Baseline_Doc_{idx+1}"
        doc_text = doc.get("text", "")
        doc_type = classify_doc_type(doc_text, doc_name)
        doc_id = f"base_doc_{idx+1}"
        
        extracted = extract_document_requirements(doc_id, doc_name, doc_type, "baseline", doc_text)
        baseline_reqs.extend(extracted)
        
        documents_meta.append({
            "document_id": doc_id,
            "document_name": doc_name,
            "document_type": doc_type,
            "side": "baseline",
            "requirement_count": len(extracted)
        })

    # Process Updated Documents
    for idx, doc in enumerate(updated_payload):
        doc_name = doc.get("name") or f"Updated_Doc_{idx+1}"
        doc_text = doc.get("text", "")
        doc_type = classify_doc_type(doc_text, doc_name)
        doc_id = f"up_doc_{idx+1}"
        
        extracted = extract_document_requirements(doc_id, doc_name, doc_type, "updated", doc_text)
        updated_reqs.extend(extracted)
        
        documents_meta.append({
            "document_id": doc_id,
            "document_name": doc_name,
            "document_type": doc_type,
            "side": "updated",
            "requirement_count": len(extracted)
        })

    # 2. Build Unified TF-IDF Vectorizer across all cleaned requirement texts
    all_clean_texts = [r["clean_text"] for r in (baseline_reqs + updated_reqs)]
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        lowercase=True,
        min_df=1,
        token_pattern=r'(?u)\b[a-zA-Z0-9_]{2,}\b'
    )
    if all_clean_texts:
        vectorizer.fit(all_clean_texts)

    def calculate_lexical_similarity(old_clean, new_clean, old_raw, new_raw):
        if not old_raw and not new_raw:
            return {"semantic": 1.0, "keyword": 1.0, "overall": 1.0}
        if not old_raw or not new_raw:
            return {"semantic": 0.0, "keyword": 0.0, "overall": 0.0}
        if old_raw.strip().lower() == new_raw.strip().lower():
            return {"semantic": 1.0, "keyword": 1.0, "overall": 1.0}

        try:
            vecs = vectorizer.transform([old_clean, new_clean])
            semantic = float(cosine_similarity(vecs[0:1], vecs[1:2])[0][0])

            old_tokens = set(old_clean.split())
            new_tokens = set(new_clean.split())
            if not old_tokens and not new_tokens:
                keyword = 1.0
            else:
                intersection = len(old_tokens.intersection(new_tokens))
                union = len(old_tokens.union(new_tokens))
                keyword = intersection / union if union > 0 else 0.0

            old_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', old_raw))
            new_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', new_raw))

            penalty = 0.0
            if old_nums != new_nums:
                penalty = 0.40

            overall = max(0.0, ((semantic * 0.7) + (keyword * 0.3)) - penalty)

            return {
                "semantic": round(semantic, 4),
                "keyword": round(keyword, 4),
                "overall": round(overall, 4)
            }
        except Exception:
            return {"semantic": 0.0, "keyword": 0.0, "overall": 0.0}

    # 3. Requirement-level Baseline <-> Updated Matching
    changes = []
    relationships = []

    base_by_id = {}
    base_unmatched = []
    for b in baseline_reqs:
        rid = b["requirement_id"]
        # If it's an explicit ID format and unique in baseline
        if rid and rid not in base_by_id:
            base_by_id[rid] = b
        else:
            base_unmatched.append(b)

    up_by_id = {}
    up_unmatched = []
    for u in updated_reqs:
        rid = u["requirement_id"]
        if rid and rid not in up_by_id:
            up_by_id[rid] = u
        else:
            up_unmatched.append(u)

    all_explicit_ids = sorted(list(set(base_by_id.keys()).union(set(up_by_id.keys()))))
    matched_base_ids = set()
    matched_up_ids = set()

    for rid in all_explicit_ids:
        in_base = rid in base_by_id
        in_up = rid in up_by_id

        if in_base and not in_up:
            # Baseline only => Removed
            b_item = base_by_id[rid]
            changes.append({
                "req_id": rid,
                "old": b_item["text"],
                "new": "",
                "status": "Removed",
                "relationship": "REMOVED_FROM",
                "similarity": 0.0,
                "confidence": "N/A",
                "source_document": b_item["document_name"],
                "source_requirement_id": rid,
                "matched_document": None,
                "matched_requirement_id": None,
                "baseline_source": b_item["document_name"],
                "updated_source": None,
                "quality": analyze_quality(b_item["text"]),
                "priority": detect_priority(b_item["text"]),
                "complexity": calculate_complexity(b_item["text"], "", "Removed")
            })
            relationships.append({
                "source_document": b_item["document_name"],
                "source_requirement_id": rid,
                "source_text": b_item["text"],
                "target_document": None,
                "target_requirement_id": None,
                "target_text": None,
                "relationship": "REMOVED_FROM",
                "similarity": 0.0,
                "confidence": "N/A",
                "status": "Removed"
            })
            matched_base_ids.add(rid)

        elif not in_base and in_up:
            # Updated only => Added
            u_item = up_by_id[rid]
            changes.append({
                "req_id": rid,
                "old": "",
                "new": u_item["text"],
                "status": "Added",
                "relationship": "ADDED_IN",
                "similarity": 0.0,
                "confidence": "New Requirement",
                "source_document": u_item["document_name"],
                "source_requirement_id": rid,
                "matched_document": None,
                "matched_requirement_id": None,
                "baseline_source": None,
                "updated_source": u_item["document_name"],
                "quality": analyze_quality(u_item["text"]),
                "priority": detect_priority(u_item["text"]),
                "complexity": calculate_complexity("", u_item["text"], "Added")
            })
            relationships.append({
                "source_document": u_item["document_name"],
                "source_requirement_id": rid,
                "source_text": u_item["text"],
                "target_document": None,
                "target_requirement_id": None,
                "target_text": None,
                "relationship": "ADDED_IN",
                "similarity": 0.0,
                "confidence": "New Requirement",
                "status": "Added"
            })
            matched_up_ids.add(rid)

        elif in_base and in_up:
            # Matched by ID
            b_item = base_by_id[rid]
            u_item = up_by_id[rid]
            sim_data = calculate_lexical_similarity(b_item["clean_text"], u_item["clean_text"], b_item["text"], u_item["text"])
            sim_score = sim_data["overall"]
            
            status = "Unchanged" if sim_score >= 0.97 else "Modified"
            rel = "SAME_REQUIREMENT" if status == "Unchanged" else "MODIFIED_FROM"
            conf = get_confidence_score(sim_score, status)

            change_obj = {
                "req_id": rid,
                "old": b_item["text"],
                "new": u_item["text"],
                "status": status,
                "relationship": rel,
                "similarity": sim_score,
                "similarity_breakdown": sim_data,
                "confidence": conf,
                "source_document": u_item["document_name"],
                "source_requirement_id": rid,
                "matched_document": b_item["document_name"],
                "matched_requirement_id": rid,
                "baseline_source": b_item["document_name"],
                "updated_source": u_item["document_name"],
                "quality": analyze_quality(u_item["text"]),
                "priority": detect_priority(u_item["text"]),
                "complexity": calculate_complexity(b_item["text"], u_item["text"], status)
            }
            if status == "Modified":
                change_obj["detected_changes"] = get_detected_changes(b_item["text"], u_item["text"])
            
            changes.append(change_obj)
            relationships.append({
                "source_document": u_item["document_name"],
                "source_requirement_id": rid,
                "source_text": u_item["text"],
                "target_document": b_item["document_name"],
                "target_requirement_id": rid,
                "target_text": b_item["text"],
                "relationship": rel,
                "similarity": sim_score,
                "confidence": conf,
                "status": status
            })
            matched_base_ids.add(rid)
            matched_up_ids.add(rid)

    # 4. Process Remaining Unmatched via Greedy TF-IDF Lexical Similarity
    remaining_base = [b for b in base_unmatched if b["requirement_id"] not in matched_base_ids]
    remaining_up = [u for u in up_unmatched if u["requirement_id"] not in matched_up_ids]

    if remaining_base and remaining_up:
        b_clean = [b["clean_text"] for b in remaining_base]
        u_clean = [u["clean_text"] for u in remaining_up]

        b_vecs = vectorizer.transform(b_clean)
        u_vecs = vectorizer.transform(u_clean)
        sim_matrix = cosine_similarity(b_vecs, u_vecs)

        matched_b_idx = set()
        matched_u_idx = set()

        for _ in range(min(len(remaining_base), len(remaining_up))):
            i, j = np.unravel_index(np.argmax(sim_matrix), sim_matrix.shape)
            best_score = sim_matrix[i, j]
            if best_score < 0.30:
                break

            matched_b_idx.add(i)
            matched_u_idx.add(j)
            sim_matrix[i, :] = -1
            sim_matrix[:, j] = -1

            b_item = remaining_base[i]
            u_item = remaining_up[j]
            sim_data = calculate_lexical_similarity(b_item["clean_text"], u_item["clean_text"], b_item["text"], u_item["text"])
            sim_score = sim_data["overall"]

            status = "Unchanged" if sim_score >= 0.97 else "Modified"
            rel = "SAME_REQUIREMENT" if status == "Unchanged" else "MODIFIED_FROM"
            conf = get_confidence_score(sim_score, status)

            req_id_to_use = u_item["requirement_id"] or b_item["requirement_id"] or f"REQ-MATCH-{i+1}"

            change_obj = {
                "req_id": req_id_to_use,
                "old": b_item["text"],
                "new": u_item["text"],
                "status": status,
                "relationship": rel,
                "similarity": sim_score,
                "similarity_breakdown": sim_data,
                "confidence": conf,
                "source_document": u_item["document_name"],
                "source_requirement_id": u_item["requirement_id"],
                "matched_document": b_item["document_name"],
                "matched_requirement_id": b_item["requirement_id"],
                "baseline_source": b_item["document_name"],
                "updated_source": u_item["document_name"],
                "quality": analyze_quality(u_item["text"]),
                "priority": detect_priority(u_item["text"]),
                "complexity": calculate_complexity(b_item["text"], u_item["text"], status)
            }
            if status == "Modified":
                change_obj["detected_changes"] = get_detected_changes(b_item["text"], u_item["text"])

            changes.append(change_obj)
            relationships.append({
                "source_document": u_item["document_name"],
                "source_requirement_id": u_item["requirement_id"],
                "source_text": u_item["text"],
                "target_document": b_item["document_name"],
                "target_requirement_id": b_item["requirement_id"],
                "target_text": b_item["text"],
                "relationship": rel,
                "similarity": sim_score,
                "confidence": conf,
                "status": status
            })

        for i, b_item in enumerate(remaining_base):
            if i not in matched_b_idx:
                changes.append({
                    "req_id": b_item["requirement_id"],
                    "old": b_item["text"],
                    "new": "",
                    "status": "Removed",
                    "relationship": "REMOVED_FROM",
                    "similarity": 0.0,
                    "confidence": "N/A",
                    "source_document": b_item["document_name"],
                    "source_requirement_id": b_item["requirement_id"],
                    "matched_document": None,
                    "matched_requirement_id": None,
                    "baseline_source": b_item["document_name"],
                    "updated_source": None,
                    "quality": analyze_quality(b_item["text"]),
                    "priority": detect_priority(b_item["text"]),
                    "complexity": calculate_complexity(b_item["text"], "", "Removed")
                })
                relationships.append({
                    "source_document": b_item["document_name"],
                    "source_requirement_id": b_item["requirement_id"],
                    "source_text": b_item["text"],
                    "target_document": None,
                    "target_requirement_id": None,
                    "target_text": None,
                    "relationship": "REMOVED_FROM",
                    "similarity": 0.0,
                    "confidence": "N/A",
                    "status": "Removed"
                })

        for j, u_item in enumerate(remaining_up):
            if j not in matched_u_idx:
                changes.append({
                    "req_id": u_item["requirement_id"],
                    "old": "",
                    "new": u_item["text"],
                    "status": "Added",
                    "relationship": "ADDED_IN",
                    "similarity": 0.0,
                    "confidence": "New Requirement",
                    "source_document": u_item["document_name"],
                    "source_requirement_id": u_item["requirement_id"],
                    "matched_document": None,
                    "matched_requirement_id": None,
                    "baseline_source": None,
                    "updated_source": u_item["document_name"],
                    "quality": analyze_quality(u_item["text"]),
                    "priority": detect_priority(u_item["text"]),
                    "complexity": calculate_complexity("", u_item["text"], "Added")
                })
                relationships.append({
                    "source_document": u_item["document_name"],
                    "source_requirement_id": u_item["requirement_id"],
                    "source_text": u_item["text"],
                    "target_document": None,
                    "target_requirement_id": None,
                    "target_text": None,
                    "relationship": "ADDED_IN",
                    "similarity": 0.0,
                    "confidence": "New Requirement",
                    "status": "Added"
                })
    else:
        for b_item in remaining_base:
            changes.append({
                "req_id": b_item["requirement_id"],
                "old": b_item["text"],
                "new": "",
                "status": "Removed",
                "relationship": "REMOVED_FROM",
                "similarity": 0.0,
                "confidence": "N/A",
                "source_document": b_item["document_name"],
                "source_requirement_id": b_item["requirement_id"],
                "matched_document": None,
                "matched_requirement_id": None,
                "baseline_source": b_item["document_name"],
                "updated_source": None,
                "quality": analyze_quality(b_item["text"]),
                "priority": detect_priority(b_item["text"]),
                "complexity": calculate_complexity(b_item["text"], "", "Removed")
            })
            relationships.append({
                "source_document": b_item["document_name"],
                "source_requirement_id": b_item["requirement_id"],
                "source_text": b_item["text"],
                "target_document": None,
                "target_requirement_id": None,
                "target_text": None,
                "relationship": "REMOVED_FROM",
                "similarity": 0.0,
                "confidence": "N/A",
                "status": "Removed"
            })
        for u_item in remaining_up:
            changes.append({
                "req_id": u_item["requirement_id"],
                "old": "",
                "new": u_item["text"],
                "status": "Added",
                "relationship": "ADDED_IN",
                "similarity": 0.0,
                "confidence": "New Requirement",
                "source_document": u_item["document_name"],
                "source_requirement_id": u_item["requirement_id"],
                "matched_document": None,
                "matched_requirement_id": None,
                "baseline_source": None,
                "updated_source": u_item["document_name"],
                "quality": analyze_quality(u_item["text"]),
                "priority": detect_priority(u_item["text"]),
                "complexity": calculate_complexity("", u_item["text"], "Added")
            })
            relationships.append({
                "source_document": u_item["document_name"],
                "source_requirement_id": u_item["requirement_id"],
                "source_text": u_item["text"],
                "target_document": None,
                "target_requirement_id": None,
                "target_text": None,
                "relationship": "ADDED_IN",
                "similarity": 0.0,
                "confidence": "New Requirement",
                "status": "Added"
            })

    # 5. Inter-Document Relationship Discovery (CR <-> SRS and BRD <-> SRS)
    change_requests_linked = 0
    brd_requirements_traced = 0

    cr_items = [u for u in (updated_reqs + baseline_reqs) if u["document_type"] == "Change Request"]
    srs_up_items = [u for u in updated_reqs if u["document_type"] in ["SRS", "FRD", "Specification", "Functional Requirement"]]
    brd_items = [b for b in (baseline_reqs + updated_reqs) if b["document_type"] == "BRD"]
    srs_all_items = [r for r in (baseline_reqs + updated_reqs) if r["document_type"] in ["SRS", "FRD", "Specification", "Functional Requirement"]]

    cr_links_by_target = {}
    brd_links_by_target = {}

    # A. Change Request -> Updated SRS (AFFECTS)
    if cr_items and srs_up_items:
        cr_clean = [c["clean_text"] for c in cr_items]
        srs_clean = [s["clean_text"] for s in srs_up_items]
        cr_vecs = vectorizer.transform(cr_clean)
        srs_vecs = vectorizer.transform(srs_clean)
        cr_sim_matrix = cosine_similarity(cr_vecs, srs_vecs)

        for i, cr_item in enumerate(cr_items):
            best_j = int(np.argmax(cr_sim_matrix[i]))
            best_sim = float(cr_sim_matrix[i][best_j])
            if best_sim >= 0.15:
                matched_srs = srs_up_items[best_j]
                conf = get_confidence_score(best_sim, "Modified")
                rel_obj = {
                    "source_document": cr_item["document_name"],
                    "source_requirement_id": cr_item["requirement_id"],
                    "source_text": cr_item["text"],
                    "target_document": matched_srs["document_name"],
                    "target_requirement_id": matched_srs["requirement_id"],
                    "target_text": matched_srs["text"],
                    "relationship": "AFFECTS",
                    "similarity": round(best_sim, 4),
                    "confidence": conf,
                    "status": "Affects"
                }
                relationships.append(rel_obj)
                change_requests_linked += 1

                t_id = matched_srs["requirement_id"]
                if t_id not in cr_links_by_target:
                    cr_links_by_target[t_id] = []
                cr_links_by_target[t_id].append({
                    "cr_id": cr_item["requirement_id"],
                    "cr_doc": cr_item["document_name"],
                    "similarity": round(best_sim, 4)
                })

    # B. BRD -> SRS (TRACEABLE_TO)
    if brd_items and srs_all_items:
        brd_clean = [b["clean_text"] for b in brd_items]
        srs_clean = [s["clean_text"] for s in srs_all_items]
        brd_vecs = vectorizer.transform(brd_clean)
        srs_vecs = vectorizer.transform(srs_clean)
        brd_sim_matrix = cosine_similarity(brd_vecs, srs_vecs)

        for i, brd_item in enumerate(brd_items):
            best_j = int(np.argmax(brd_sim_matrix[i]))
            best_sim = float(brd_sim_matrix[i][best_j])
            if best_sim >= 0.15:
                matched_srs = srs_all_items[best_j]
                conf = get_confidence_score(best_sim, "Modified")
                rel_obj = {
                    "source_document": brd_item["document_name"],
                    "source_requirement_id": brd_item["requirement_id"],
                    "source_text": brd_item["text"],
                    "target_document": matched_srs["document_name"],
                    "target_requirement_id": matched_srs["requirement_id"],
                    "target_text": matched_srs["text"],
                    "relationship": "TRACEABLE_TO",
                    "similarity": round(best_sim, 4),
                    "confidence": conf,
                    "status": "Traceable"
                }
                relationships.append(rel_obj)
                brd_requirements_traced += 1

                t_id = matched_srs["requirement_id"]
                if t_id not in brd_links_by_target:
                    brd_links_by_target[t_id] = []
                brd_links_by_target[t_id].append({
                    "brd_id": brd_item["requirement_id"],
                    "brd_doc": brd_item["document_name"],
                    "similarity": round(best_sim, 4)
                })

    # 6. Build Traceability List & Enrich Changes
    traceability_entries = []
    for c in changes:
        rid = c["req_id"]
        c["linked_change_requests"] = cr_links_by_target.get(rid, [])
        c["linked_brd_requirements"] = brd_links_by_target.get(rid, [])

        traceability_entries.append({
            "req_id": rid,
            "text": c.get("new") or c.get("old", ""),
            "source_document": c.get("source_document") or c.get("updated_source") or c.get("baseline_source"),
            "matched_req_id": c.get("matched_requirement_id"),
            "matched_document": c.get("matched_document") or c.get("baseline_source"),
            "relationship": c.get("relationship", "SAME_REQUIREMENT"),
            "status": c.get("status"),
            "similarity": c.get("similarity", 0.0),
            "confidence": c.get("confidence", "N/A"),
            "module": c.get("module", "Other"),
            "linked_change_requests": c["linked_change_requests"],
            "linked_brd_requirements": c["linked_brd_requirements"]
        })

    # Add CR and BRD direct rows to traceability if not already covered in changes
    for rel in relationships:
        if rel["relationship"] in ["AFFECTS", "TRACEABLE_TO"]:
            traceability_entries.append({
                "req_id": rel["source_requirement_id"],
                "text": rel["source_text"],
                "source_document": rel["source_document"],
                "matched_req_id": rel["target_requirement_id"],
                "matched_document": rel["target_document"],
                "relationship": rel["relationship"],
                "status": rel["status"],
                "similarity": rel["similarity"],
                "confidence": rel["confidence"],
                "module": "Other",
                "linked_change_requests": [],
                "linked_brd_requirements": []
            })

    # 7. Document-Level Statistics
    doc_stats = {
        "documents_analyzed": len(documents_meta),
        "baseline_documents": len(baseline_payload),
        "updated_documents": len(updated_payload),
        "cross_document_relationships": len(relationships),
        "requirements_with_traceability": len([t for t in traceability_entries if t["matched_req_id"]]),
        "change_requests_linked": change_requests_linked,
        "brd_requirements_traced": brd_requirements_traced
    }

    cross_doc_analysis = {
        "documents": documents_meta,
        "relationships": relationships,
        "traceability": traceability_entries,
        "statistics": doc_stats
    }

    return changes, cross_doc_analysis, baseline_reqs, updated_reqs
