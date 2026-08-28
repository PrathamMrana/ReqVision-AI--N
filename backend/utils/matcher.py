import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from .analyzer import analyze_quality, detect_priority, calculate_complexity, generate_recommendations

try:
    base_stop_words = set(stopwords.words('english'))
except LookupError:
    base_stop_words = set()

custom_stopwords = {'shall', 'system', 'user', 'users', 'using', 'without', 'time', 'must', 'will', 'should', 'can', 'may', 'allow', 'provide', 'ensure', 'require', 'requirement', 'application', 'software', 'increased', 'decreased', 'added', 'removed', 'modified', 'change', 'changed', 'within', 'also', 'only', 'the', 'and', 'for', 'that', 'this'}
stop_words = base_stop_words.union(custom_stopwords)

def get_confidence_score(similarity, status):
    if status in ["Added", "Removed"]:
        return "New" if status == "Added" else "N/A"
    
    sim_pct = similarity * 100
    if sim_pct >= 95:
        return "Very High"
    elif sim_pct >= 80:
        return "High"
    elif sim_pct >= 60:
        return "Medium"
    else:
        return "Low"

def get_detected_changes(old_text, new_text):
    def extract_tokens(text):
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b|\b\d+(?:\.\d+)?%?\b', text.lower())
        return {w for w in tokens if w not in stop_words}

    old_tokens = extract_tokens(old_text)
    new_tokens = extract_tokens(new_text)

    added_set = new_tokens - old_tokens
    removed_set = old_tokens - new_tokens
    common_set = old_tokens.intersection(new_tokens)

    num_added = {t for t in added_set if any(c.isdigit() for c in t)}
    num_removed = {t for t in removed_set if any(c.isdigit() for c in t)}
    
    added_words = {t for t in added_set if not any(c.isdigit() for c in t)}
    removed_words = {t for t in removed_set if not any(c.isdigit() for c in t)}

    added = sorted(list(added_words))[:3]
    removed = sorted(list(removed_words))[:3]
    common = sorted(list(common_set))[:3]

    changes = []
    reason_parts = []

    if num_added or num_removed:
        reason_parts.append("Numerical targets modified.")
    if added_words and removed_words:
        reason_parts.append(f"Introduced '{added[0]}' capability. Reduced emphasis on '{removed[0]}'.")
    elif added_words:
        reason_parts.append(f"{added[0].capitalize()} capability expanded.")
    elif removed_words:
        reason_parts.append(f"{removed[0].capitalize()} capability reduced.")
    
    if not reason_parts:
        reason_parts.append("Minor textual/grammar modifications.")
        
    reason = " ".join(reason_parts)
    
    if num_added or num_removed:
        changes.append("Summary: Operational or numerical constraints were materially altered.")
    elif added_words and removed_words:
        changes.append(f"Summary: Scope modified by adding '{', '.join(added)}' while removing '{', '.join(removed)}'.")
    elif added_words:
        changes.append(f"Summary: Scope expanded to include '{', '.join(added)}'.")
    elif removed_words:
        changes.append(f"Summary: Scope narrowed by removing '{', '.join(removed)}'.")
    else:
        changes.append("Summary: Phrasing updated without semantic shifts.")

    if num_added:
        changes.append(f"+ Added targets: {', '.join(num_added)}")
    elif added_words:
        changes.append(f"+ Added keywords: {', '.join(added)}")
        
    if num_removed:
        changes.append(f"- Removed targets: {', '.join(num_removed)}")
    elif removed_words:
        changes.append(f"- Removed keywords: {', '.join(removed)}")
        
    if common:
        changes.append(f"✓ Retained concepts: {', '.join(common)}")
        
    return {
        "highlights": changes,
        "reason": reason
    }

def match_sentences(baseline_dicts, updated_dicts, clean_baseline, clean_updated):
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, lowercase=True, min_df=1, token_pattern=r'(?u)\b[a-zA-Z0-9_]{2,}\b')
    all_clean = clean_baseline + clean_updated
    if all_clean:
        vectorizer.fit(all_clean)
        
    def get_sim(old_txt_clean, new_txt_clean, old_raw, new_raw):
        if not old_raw and not new_raw: 
            return {"semantic": 1.0, "keyword": 1.0, "overall": 1.0}
        if not old_raw or not new_raw: 
            return {"semantic": 0.0, "keyword": 0.0, "overall": 0.0}
            
        if old_raw.strip().lower() == new_raw.strip().lower():
            return {"semantic": 1.0, "keyword": 1.0, "overall": 1.0}
        
        try:
            vecs = vectorizer.transform([old_txt_clean, new_txt_clean])
            semantic = float(cosine_similarity(vecs[0:1], vecs[1:2])[0][0])
            
            old_tokens = set(old_txt_clean.split())
            new_tokens = set(new_txt_clean.split())
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

    changes = []
    
    base_explicit = {}
    base_unmatched = []
    
    for i, b in enumerate(baseline_dicts):
        rid = b.get('id')
        if rid:
            base_explicit[rid] = {"text": b['text'], "clean": clean_baseline[i], "source": b.get("source", "Unknown")}
        else:
            base_unmatched.append({"text": b['text'], "clean": clean_baseline[i], "idx": i, "source": b.get("source", "Unknown")})
            
    up_explicit = {}
    up_unmatched = []
    
    for j, u in enumerate(updated_dicts):
        rid = u.get('id')
        if rid:
            up_explicit[rid] = {"text": u['text'], "clean": clean_updated[j], "source": u.get("source", "Unknown")}
        else:
            up_unmatched.append({"text": u['text'], "clean": clean_updated[j], "idx": j, "source": u.get("source", "Unknown")})
            
    all_explicit_ids = set(base_explicit.keys()).union(set(up_explicit.keys()))
    
    # Process explicit ID matches
    for rid in sorted(list(all_explicit_ids)):
        in_base = rid in base_explicit
        in_up = rid in up_explicit
        
        if in_base and not in_up:
            old_text = base_explicit[rid]['text']
            changes.append({
                "req_id": rid,
                "old": old_text, "new": "", "status": "Removed", "baseline_source": base_explicit[rid]["source"], "updated_source": None,
                "similarity": 0.0, "confidence": "N/A",
                "quality": analyze_quality(old_text),
                "priority": detect_priority(old_text),
                "complexity": calculate_complexity(old_text, "", "Removed")
            })
            
        elif not in_base and in_up:
            new_text = up_explicit[rid]['text']
            changes.append({
                "req_id": rid,
                "old": "", "new": new_text, "status": "Added", "baseline_source": None, "updated_source": up_explicit[rid]["source"],
                "similarity": 0.0, "confidence": "New",
                "quality": analyze_quality(new_text),
                "priority": detect_priority(new_text),
                "complexity": calculate_complexity("", new_text, "Added")
            })
            
        elif in_base and in_up:
            old_text = base_explicit[rid]['text']
            new_text = up_explicit[rid]['text']
            
            sim_data = get_sim(base_explicit[rid]['clean'], up_explicit[rid]['clean'], old_text, new_text)
            sim_score = sim_data["overall"]
            
            if sim_score >= 0.97:
                status = "Unchanged"
            else:
                status = "Modified"
                
            change_obj = {
                "req_id": rid,
                "old": old_text, "new": new_text, "status": status, "baseline_source": base_explicit[rid]["source"], "updated_source": up_explicit[rid]["source"],
                "similarity": sim_score, "similarity_breakdown": sim_data,
                "confidence": get_confidence_score(sim_score, status),
                "quality": analyze_quality(new_text),
                "priority": detect_priority(new_text),
                "complexity": calculate_complexity(old_text, new_text, status)
            }
            if status == "Modified":
                change_obj["detected_changes"] = get_detected_changes(old_text, new_text)
            changes.append(change_obj)
            
    # Process implicit matches via greedy lexical similarity
    if base_unmatched and up_unmatched:
        from utils.similarity import calculate_similarity_matrix
        b_docs = [u['clean'] for u in base_unmatched]
        u_docs = [u['clean'] for u in up_unmatched]
        
        sim_matrix = calculate_similarity_matrix(b_docs, u_docs)
        
        matched_base = set()
        matched_up = set()
        
        if sim_matrix.size > 0:
            # Greedy matching
            for _ in range(min(len(base_unmatched), len(up_unmatched))):
                i, j = np.unravel_index(np.argmax(sim_matrix), sim_matrix.shape)
                best_score = sim_matrix[i, j]
                if best_score < 0.30: # If best match is less than 30%, treat them as entirely different
                    break
                    
                matched_base.add(i)
                matched_up.add(j)
                sim_matrix[i, :] = -1
                sim_matrix[:, j] = -1
                
                old_raw = base_unmatched[i]['text']
                new_raw = up_unmatched[j]['text']
                old_clean = base_unmatched[i]['clean']
                new_clean = up_unmatched[j]['clean']
                
                sim_data = get_sim(old_clean, new_clean, old_raw, new_raw)
                sim_score = sim_data["overall"]
                
                status = "Unchanged" if sim_score >= 0.97 else "Modified"
                
                change_obj = {
                    "req_id": f"AUTO-MATCH-{i}-{j}",
                    "old": old_raw, "new": new_raw, "status": status,
                    "baseline_source": base_unmatched[i]["source"],
                    "updated_source": up_unmatched[j]["source"],
                    "similarity": sim_score, "similarity_breakdown": sim_data,
                    "confidence": get_confidence_score(sim_score, status),
                    "quality": analyze_quality(new_raw),
                    "priority": detect_priority(new_raw),
                    "complexity": calculate_complexity(old_raw, new_raw, status)
                }
                if status == "Modified":
                    change_obj["detected_changes"] = get_detected_changes(old_raw, new_raw)
                changes.append(change_obj)
                
        # Handle unmatched leftovers
        for i, b in enumerate(base_unmatched):
            if i not in matched_base:
                old_text = b['text']
                changes.append({
                    "req_id": f"AUTO-DEL-{i}",
                    "old": old_text, "new": "", "status": "Removed",
                    "baseline_source": b["source"],
                    "updated_source": None,
                    "similarity": 0.0, "confidence": "N/A",
                    "quality": analyze_quality(old_text),
                    "priority": detect_priority(old_text),
                    "complexity": calculate_complexity(old_text, "", "Removed")
                })
                
        for j, u in enumerate(up_unmatched):
            if j not in matched_up:
                new_text = u['text']
                changes.append({
                    "req_id": f"AUTO-ADD-{j}",
                    "old": "", "new": new_text, "status": "Added",
                    "baseline_source": None,
                    "updated_source": u["source"],
                    "similarity": 0.0, "confidence": "New",
                    "quality": analyze_quality(new_text),
                    "priority": detect_priority(new_text),
                    "complexity": calculate_complexity("", new_text, "Added")
                })
    else:
        # Either all were matched by ID, or one of them is empty
        for i, b in enumerate(base_unmatched):
            old_text = b['text']
            changes.append({
                "req_id": f"AUTO-DEL-{i}",
                "old": old_text, "new": "", "status": "Removed",
                "baseline_source": b["source"],
                "updated_source": None,
                "similarity": 0.0, "confidence": "N/A",
                "quality": analyze_quality(old_text),
                "priority": detect_priority(old_text),
                "complexity": calculate_complexity(old_text, "", "Removed")
            })
        for j, u in enumerate(up_unmatched):
            new_text = u['text']
            changes.append({
                "req_id": f"AUTO-ADD-{j}",
                "old": "", "new": new_text, "status": "Added",
                "baseline_source": None,
                "updated_source": u["source"],
                "similarity": 0.0, "confidence": "New",
                "quality": analyze_quality(new_text),
                "priority": detect_priority(new_text),
                "complexity": calculate_complexity("", new_text, "Added")
            })

    return changes
