import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.preprocess import clean_text

# Explainable Security and Behavioral Conflict Rules
CONFLICT_RULES = [
    {
        "domain": "security_passwords",
        "keywords": ["password", "credential", "auth", "login"],
        "patterns_a": [r"\breversible encryption\b", r"\brecover\s+(?:the\s+)?(?:original\s+)?password\b", r"\bplaintext\b", r"\bcleartext\b"],
        "patterns_b": [r"\bhashing\b", r"\bsalted\b", r"\bone-way\b", r"\boauth\b", r"\bjwt\b", r"\bemail and password\b", r"\bauthenticate\b"],
        "reason": "Security contradiction: Reversible password storage/recovery contradicts secure credential authentication standards."
    },
    {
        "domain": "mfa_contradiction",
        "keywords": ["mfa", "2fa", "authentication", "login"],
        "patterns_a": [r"\bmandatory\s+(?:mfa|2fa|multi-factor)\b", r"\benforce\s+(?:mfa|2fa)\b"],
        "patterns_b": [r"\bpassword\s+only\b", r"\bno\s+(?:mfa|2fa)\b", r"\bsingle-factor\b"],
        "reason": "Authentication contradiction: Mandatory MFA requirement contradicts single-factor password-only access."
    },
    {
        "domain": "encryption_at_rest",
        "keywords": ["encrypt", "storage", "database"],
        "patterns_a": [r"\bno\s+encryption\b", r"\bunencrypted\b"],
        "patterns_b": [r"\baes-256\b", r"\bencrypted\s+at\s+rest\b"],
        "reason": "Data Protection contradiction: Unencrypted database storage contradicts AES-256 encryption requirement."
    }
]

DOMAIN_SYNONYMS = [
    {"terms": {"auth", "authenticate", "authentication", "credential", "credentials", "login", "password"}},
    {"terms": {"search", "catalog", "query", "find", "discover", "browse", "index"}},
    {"terms": {"payment", "fee", "fines", "fine", "settlement", "pay", "stripe", "overdue"}},
    {"terms": {"role", "roles", "rbac", "permission", "permissions", "access", "authorization", "librarian", "admin"}},
    {"terms": {"report", "reports", "circulation", "inventory", "statistics", "analytics", "csv", "pdf"}},
    {"terms": {"renew", "renewal", "renewals", "renewing", "extend", "duration"}},
    {"terms": {"notification", "notifications", "alert", "alerts", "reminder", "reminders", "smtp", "email", "dispatch"}},
    {"terms": {"audit", "trail", "immutable", "logging", "log", "logs", "transitions", "history"}},
    {"terms": {"quota", "limit", "maximum", "allowable", "checkout", "loans", "borrow"}}
]

def check_explainable_conflict(text_a, text_b):
    """
    Evaluates explainable domain rules to determine if text_a and text_b contain contradictory requirements.
    """
    ta_lower = text_a.lower()
    tb_lower = text_b.lower()
    
    for rule in CONFLICT_RULES:
        if any(kw in ta_lower for kw in rule["keywords"]) and any(kw in tb_lower for kw in rule["keywords"]):
            has_a1 = any(re.search(p, ta_lower) for p in rule["patterns_a"])
            has_b2 = any(re.search(p, tb_lower) for p in rule["patterns_b"])
            has_a2 = any(re.search(p, tb_lower) for p in rule["patterns_a"])
            has_b1 = any(re.search(p, ta_lower) for p in rule["patterns_b"])
            
            if (has_a1 and has_b2) or (has_a2 and has_b1):
                return True, rule["reason"]
                
    return False, None


def compute_lexical_similarity(vectorizer, text_a_clean, text_b_clean, text_a_raw, text_b_raw):
    """
    Computes explainable lexical similarity using TF-IDF cosine similarity + token overlap with numerical preservation penalty.
    """
    if not text_a_clean and not text_b_clean:
        return 1.0, "Identical empty content"
    if not text_a_clean or not text_b_clean:
        return 0.0, "No content overlap"
    if text_a_clean.strip() == text_b_clean.strip():
        return 1.0, "Exact lexical match"

    try:
        vecs = vectorizer.transform([text_a_clean, text_b_clean])
        tfidf_sim = float(cosine_similarity(vecs[0:1], vecs[1:2])[0][0])
        
        tokens_a = set(text_a_clean.split())
        tokens_b = set(text_b_clean.split())
        
        # Exact Token Jaccard
        jaccard = len(tokens_a.intersection(tokens_b)) / len(tokens_a.union(tokens_b)) if tokens_a.union(tokens_b) else 0.0
        
        # Domain Synonyms Overlap Bonus
        domain_overlap = 0.0
        matched_domain_concepts = []
        for group in DOMAIN_SYNONYMS:
            has_a = bool(tokens_a.intersection(group["terms"]))
            has_b = bool(tokens_b.intersection(group["terms"]))
            if has_a and has_b:
                domain_overlap += 0.25
                common_concept = list(tokens_a.intersection(group["terms"]))[0]
                matched_domain_concepts.append(common_concept)
        
        # Numbers penalty
        nums_a = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', text_a_raw))
        nums_b = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', text_b_raw))
        penalty = 0.25 if (nums_a and nums_b and nums_a != nums_b) else 0.0
        
        score = max(0.0, min(1.0, ((tfidf_sim * 0.50) + (jaccard * 0.25) + min(domain_overlap, 0.40)) - penalty))
        
        common_tokens = list(tokens_a.intersection(tokens_b)) + matched_domain_concepts
        unique_common = list(dict.fromkeys(common_tokens))[:4]
        evidence = f"Lexical overlap on [{', '.join(unique_common)}] (Score: {score:.2f}, TF-IDF: {tfidf_sim:.2f})"
        return round(score, 4), evidence
    except Exception as e:
        return 0.0, f"Similarity error: {str(e)}"


def match_artifact_to_candidates(source_art, candidate_arts, vectorizer, min_match=0.25, min_partial=0.10):
    """
    Matches a single source artifact against a list of candidate artifacts in downstream document.
    Returns: best_candidate, status, similarity, evidence
    """
    if not candidate_arts:
        return None, "UNMAPPED", 0.0, "No target artifacts in document"

    best_cand = None
    best_score = -1.0
    best_evidence = ""
    conflict_cand = None
    conflict_reason = None

    for cand in candidate_arts:
        # 1. Check for intentional explainable contradiction
        has_conflict, reason = check_explainable_conflict(source_art["text"], cand["text"])
        if has_conflict:
            conflict_cand = cand
            conflict_reason = reason
        
        # 2. Compute similarity
        sim, evidence = compute_lexical_similarity(
            vectorizer,
            source_art["clean_text"],
            cand["clean_text"],
            source_art["text"],
            cand["text"]
        )

        if sim > best_score:
            best_score = sim
            best_cand = cand
            best_evidence = evidence

    # If an explainable contradiction was detected against an artifact in this domain
    if conflict_cand and best_score >= min_partial:
        return conflict_cand, "CONFLICT", best_score, conflict_reason

    if best_score >= min_match:
        return best_cand, "MATCHED", best_score, best_evidence
    elif best_score >= min_partial:
        return best_cand, "PARTIAL", best_score, f"Partial conceptual overlap ({best_evidence})"
    else:
        return None, "UNMAPPED", 0.0, "No target artifact satisfied minimum lexical match threshold"


def analyze_project_documents_traceability(project_documents):
    """
    Executes True Project-Level Cross-Document Traceability across all uploaded documents:
    1. Collects and normalizes all extracted artifacts with full document provenance.
    2. Builds TF-IDF lexical vocabulary across the entire project collection.
    3. Traces primary engineering path: BRD -> SRS -> FRD -> User Story -> Test Case.
    4. Traces supporting impact path: Change Request -> Requirements & Meeting Minutes -> Decisions.
    5. Computes Traceability Matrix, Traceability Graph, and Coverage Metrics with zero baseline/updated bias.
    """
    all_artifacts = []
    docs_by_type = {}
    doc_type_counts = {}

    for doc in project_documents:
        doc_id = doc.get("document_id") or doc.get("id")
        doc_name = doc.get("filename") or doc.get("name") or "Document"
        doc_type = doc.get("document_type") or "Unknown"
        doc_artifacts = doc.get("artifacts") or []

        doc_type_counts[doc_type] = doc_type_counts.get(doc_type, 0) + len(doc_artifacts)
        if doc_type not in docs_by_type:
            docs_by_type[doc_type] = []

        for art in doc_artifacts:
            art_id = art.get("artifact_id") or f"ART-{len(all_artifacts)+1:03d}"
            art_text = art.get("text", "").strip()
            clean = clean_text(art_text)
            
            norm_art = {
                "artifact_id": art_id,
                "artifact_type": art.get("artifact_type") or "Requirement",
                "document_id": doc_id,
                "document_name": doc_name,
                "document_type": doc_type,
                "text": art_text,
                "clean_text": clean,
                "section": art.get("section") or "General",
                "metadata": art.get("metadata") or {}
            }
            all_artifacts.append(norm_art)
            docs_by_type[doc_type].append(norm_art)

    # Build Project-wide TF-IDF Vectorizer
    all_clean_texts = [a["clean_text"] for a in all_artifacts if a["clean_text"]]
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        lowercase=True,
        min_df=1,
        token_pattern=r'(?u)\b[a-zA-Z0-9_]{2,}\b'
    )
    if all_clean_texts:
        vectorizer.fit(all_clean_texts)

    # Artifact collections by standard tiers
    brd_list = docs_by_type.get("BRD", [])
    srs_list = docs_by_type.get("SRS", [])
    frd_list = docs_by_type.get("FRD", [])
    us_list = docs_by_type.get("User Story", [])
    tc_list = docs_by_type.get("Test Case", [])
    cr_list = docs_by_type.get("Change Request", [])
    mom_list = docs_by_type.get("Meeting Minutes", [])

    if not brd_list and srs_list:
        root_artifacts = srs_list
    elif brd_list:
        root_artifacts = brd_list
    else:
        root_artifacts = all_artifacts

    traceability_chains = []
    direct_relationships = []
    status_counts = {"MATCHED": 0, "PARTIAL": 0, "CONFLICT": 0, "UNMAPPED": 0}
    top_conflicts = []
    top_unmapped = []

    # 1. Trace from BRD (or Root) downstream
    for root_art in root_artifacts:
        chain = {
            "chain_id": f"CHAIN-{len(traceability_chains)+1:03d}",
            "brd": None,
            "srs": None,
            "frd": None,
            "user_story": None,
            "test_case": None,
            "overall_status": "UNMAPPED",
            "evidence_chain": []
        }

        if root_art["document_type"] == "BRD":
            chain["brd"] = {
                "id": root_art["artifact_id"],
                "name": root_art["document_name"],
                "text": root_art["text"]
            }
            # Match BRD -> SRS
            matched_srs, srs_status, srs_sim, srs_ev = match_artifact_to_candidates(root_art, srs_list, vectorizer)
            direct_relationships.append({
                "source_doc": root_art["document_name"],
                "source_id": root_art["artifact_id"],
                "source_text": root_art["text"],
                "target_doc": matched_srs["document_name"] if matched_srs else None,
                "target_id": matched_srs["artifact_id"] if matched_srs else None,
                "target_text": matched_srs["text"] if matched_srs else None,
                "relation_type": "BRD_TO_SRS",
                "status": srs_status,
                "similarity": srs_sim,
                "evidence": srs_ev
            })
            if matched_srs:
                chain["srs"] = {
                    "id": matched_srs["artifact_id"],
                    "name": matched_srs["document_name"],
                    "text": matched_srs["text"]
                }
                chain["evidence_chain"].append(f"BRD→SRS: {srs_ev}")
            current_srs = matched_srs
        else:
            current_srs = root_art
            chain["srs"] = {
                "id": current_srs["artifact_id"],
                "name": current_srs["document_name"],
                "text": current_srs["text"]
            }

        current_frd = None
        current_us = None
        current_tc = None
        step_statuses = []

        # Match SRS -> FRD
        if current_srs:
            matched_frd, frd_status, frd_sim, frd_ev = match_artifact_to_candidates(current_srs, frd_list, vectorizer)
            step_statuses.append(frd_status)
            direct_relationships.append({
                "source_doc": current_srs["document_name"],
                "source_id": current_srs["artifact_id"],
                "source_text": current_srs["text"],
                "target_doc": matched_frd["document_name"] if matched_frd else None,
                "target_id": matched_frd["artifact_id"] if matched_frd else None,
                "target_text": matched_frd["text"] if matched_frd else None,
                "relation_type": "SRS_TO_FRD",
                "status": frd_status,
                "similarity": frd_sim,
                "evidence": frd_ev
            })
            if matched_frd:
                current_frd = matched_frd
                chain["frd"] = {
                    "id": matched_frd["artifact_id"],
                    "name": matched_frd["document_name"],
                    "text": matched_frd["text"]
                }
                chain["evidence_chain"].append(f"SRS→FRD: {frd_ev}")

        # Match SRS -> User Story
        if current_srs:
            matched_us, us_status, us_sim, us_ev = match_artifact_to_candidates(current_srs, us_list, vectorizer)
            step_statuses.append(us_status)
            direct_relationships.append({
                "source_doc": current_srs["document_name"],
                "source_id": current_srs["artifact_id"],
                "source_text": current_srs["text"],
                "target_doc": matched_us["document_name"] if matched_us else None,
                "target_id": matched_us["artifact_id"] if matched_us else None,
                "target_text": matched_us["text"] if matched_us else None,
                "relation_type": "SRS_TO_USER_STORY",
                "status": us_status,
                "similarity": us_sim,
                "evidence": us_ev
            })
            if matched_us:
                current_us = matched_us
                chain["user_story"] = {
                    "id": matched_us["artifact_id"],
                    "name": matched_us["document_name"],
                    "text": matched_us["text"]
                }
                chain["evidence_chain"].append(f"SRS→US: {us_ev}")

        # Match User Story -> Test Case
        target_for_tc = current_us or current_srs
        if target_for_tc:
            matched_tc, tc_status, tc_sim, tc_ev = match_artifact_to_candidates(target_for_tc, tc_list, vectorizer)
            step_statuses.append(tc_status)
            direct_relationships.append({
                "source_doc": target_for_tc["document_name"],
                "source_id": target_for_tc["artifact_id"],
                "source_text": target_for_tc["text"],
                "target_doc": matched_tc["document_name"] if matched_tc else None,
                "target_id": matched_tc["artifact_id"] if matched_tc else None,
                "target_text": matched_tc["text"] if matched_tc else None,
                "relation_type": "US_TO_TEST_CASE",
                "status": tc_status,
                "similarity": tc_sim,
                "evidence": tc_ev
            })
            if matched_tc:
                current_tc = matched_tc
                chain["test_case"] = {
                    "id": matched_tc["artifact_id"],
                    "name": matched_tc["document_name"],
                    "text": matched_tc["text"]
                }
                chain["evidence_chain"].append(f"US→TC: {tc_ev}")

        # Determine overall chain status
        if "CONFLICT" in step_statuses:
            overall = "CONFLICT"
            top_conflicts.append({
                "source_id": root_art["artifact_id"],
                "source_doc": root_art["document_name"],
                "source_text": root_art["text"],
                "reason": next((ev for ev in chain["evidence_chain"] if "contradiction" in ev.lower()), "Contradiction detected in downstream requirement specifications")
            })
        elif all(st == "MATCHED" for st in step_statuses if st) and len(step_statuses) > 0:
            overall = "MATCHED"
        elif any(st in ["MATCHED", "PARTIAL"] for st in step_statuses):
            overall = "PARTIAL"
        else:
            overall = "UNMAPPED"
            top_unmapped.append({
                "artifact_id": root_art["artifact_id"],
                "document_name": root_art["document_name"],
                "text": root_art["text"],
                "reason": "No downstream requirement, functional spec, or test case mapped"
            })

        chain["overall_status"] = overall
        status_counts[overall] += 1
        traceability_chains.append(chain)

    # 2. Supporting Impact Mapping: Change Request -> Requirements
    cr_impacts = []
    for cr in cr_list:
        matched_req, cr_status, cr_sim, cr_ev = match_artifact_to_candidates(cr, srs_list + frd_list, vectorizer, min_match=0.15, min_partial=0.08)
        cr_impacts.append({
            "cr_id": cr["artifact_id"],
            "cr_doc": cr["document_name"],
            "cr_text": cr["text"],
            "affected_req_id": matched_req["artifact_id"] if matched_req else None,
            "affected_doc": matched_req["document_name"] if matched_req else None,
            "affected_text": matched_req["text"] if matched_req else None,
            "status": cr_status,
            "similarity": cr_sim,
            "evidence": cr_ev
        })

    # 3. Supporting Context: Meeting Minutes -> Requirements
    mom_links = []
    for mom in mom_list:
        matched_req, mom_status, mom_sim, mom_ev = match_artifact_to_candidates(mom, brd_list + srs_list + cr_list, vectorizer, min_match=0.15, min_partial=0.08)
        mom_links.append({
            "mom_id": mom["artifact_id"],
            "mom_doc": mom["document_name"],
            "mom_text": mom["text"],
            "referenced_req_id": matched_req["artifact_id"] if matched_req else None,
            "referenced_doc": matched_req["document_name"] if matched_req else None,
            "referenced_text": matched_req["text"] if matched_req else None,
            "status": mom_status,
            "similarity": mom_sim,
            "evidence": mom_ev
        })

    # 4. Construct Traceability Graph
    graph_nodes = []
    graph_edges = []
    node_ids_added = set()

    for art in all_artifacts:
        node_id = f"{art['document_name']}:{art['artifact_id']}"
        if node_id not in node_ids_added:
            graph_nodes.append({
                "id": node_id,
                "artifact_id": art["artifact_id"],
                "document_name": art["document_name"],
                "document_type": art["document_type"],
                "text": art["text"][:120] + ("..." if len(art["text"]) > 120 else "")
            })
            node_ids_added.add(node_id)

    for rel in direct_relationships:
        if rel["target_id"]:
            source_node = f"{rel['source_doc']}:{rel['source_id']}"
            target_node = f"{rel['target_doc']}:{rel['target_id']}"
            graph_edges.append({
                "source": source_node,
                "target": target_node,
                "relation_type": rel["relation_type"],
                "status": rel["status"],
                "similarity": rel["similarity"],
                "evidence": rel["evidence"]
            })

    # 5. Exact Traceability Coverage Calculation
    total_root = len(root_artifacts)
    mapped_root = sum(1 for c in traceability_chains if c["overall_status"] in ["MATCHED", "PARTIAL", "CONFLICT"])
    coverage_pct = round((mapped_root / total_root * 100), 1) if total_root > 0 else 0.0

    return {
        "success": True,
        "mode": "project_intelligence",
        "summary": {
            "total_documents": len(project_documents),
            "total_artifacts": len(all_artifacts),
            "document_types": doc_type_counts,
            "coverage_percentage": coverage_pct,
            "status_breakdown": status_counts,
            "brd_to_srs_mappings": sum(1 for r in direct_relationships if r["relation_type"] == "BRD_TO_SRS" and r["target_id"]),
            "srs_to_frd_mappings": sum(1 for r in direct_relationships if r["relation_type"] == "SRS_TO_FRD" and r["target_id"]),
            "srs_to_user_story_mappings": sum(1 for r in direct_relationships if r["relation_type"] == "SRS_TO_USER_STORY" and r["target_id"]),
            "user_story_to_test_case_mappings": sum(1 for r in direct_relationships if r["relation_type"] == "US_TO_TEST_CASE" and r["target_id"]),
        },
        "traceability_matrix": traceability_chains,
        "traceability_graph": {
            "nodes": graph_nodes,
            "edges": graph_edges
        },
        "relationships": direct_relationships,
        "top_conflicts": top_conflicts,
        "top_unmapped": top_unmapped,
        "change_request_impacts": cr_impacts,
        "meeting_minutes_links": mom_links,
        "documents": [
            {
                "document_id": doc.get("document_id") or doc.get("id"),
                "filename": doc.get("filename") or doc.get("name"),
                "document_type": doc.get("document_type"),
                "artifact_count": len(doc.get("artifacts") or [])
            } for doc in project_documents
        ]
    }
