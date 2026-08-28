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


def match_artifact_to_candidates(source_art, candidate_arts, vectorizer, relationship_type="TRACEABLE_TO", min_match=0.25, min_partial=0.10):
    """
    Matches a single source artifact against a list of candidate artifacts in downstream document.
    Returns: relationship_record (dict)
    """
    if not candidate_arts:
        return {
            "source_document": source_art["document_name"],
            "source_type": source_art["document_type"],
            "source_artifact": source_art["artifact_id"],
            "source_text": source_art["text"],
            "target_document": "—",
            "target_type": "—",
            "target_artifact": "—",
            "target_text": "—",
            "relationship": relationship_type,
            "status": "UNMAPPED",
            "similarity": 0.0,
            "confidence": "Low",
            "evidence": "No candidate artifacts found in target document"
        }

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

    # Conflict check
    if conflict_cand and best_score >= min_partial:
        return {
            "source_document": source_art["document_name"],
            "source_type": source_art["document_type"],
            "source_artifact": source_art["artifact_id"],
            "source_text": source_art["text"],
            "target_document": conflict_cand["document_name"],
            "target_type": conflict_cand["document_type"],
            "target_artifact": conflict_cand["artifact_id"],
            "target_text": conflict_cand["text"],
            "relationship": relationship_type,
            "status": "CONFLICT",
            "similarity": best_score,
            "confidence": "High",
            "evidence": conflict_reason
        }

    if best_score >= min_match:
        conf = "High" if best_score >= 0.45 else "Medium"
        return {
            "source_document": source_art["document_name"],
            "source_type": source_art["document_type"],
            "source_artifact": source_art["artifact_id"],
            "source_text": source_art["text"],
            "target_document": best_cand["document_name"],
            "target_type": best_cand["document_type"],
            "target_artifact": best_cand["artifact_id"],
            "target_text": best_cand["text"],
            "relationship": relationship_type,
            "status": "MATCHED",
            "similarity": best_score,
            "confidence": conf,
            "evidence": best_evidence
        }
    elif best_score >= min_partial:
        return {
            "source_document": source_art["document_name"],
            "source_type": source_art["document_type"],
            "source_artifact": source_art["artifact_id"],
            "source_text": source_art["text"],
            "target_document": best_cand["document_name"],
            "target_type": best_cand["document_type"],
            "target_artifact": best_cand["artifact_id"],
            "target_text": best_cand["text"],
            "relationship": relationship_type,
            "status": "PARTIAL",
            "similarity": best_score,
            "confidence": "Medium",
            "evidence": f"Partial conceptual overlap ({best_evidence})"
        }
    else:
        return {
            "source_document": source_art["document_name"],
            "source_type": source_art["document_type"],
            "source_artifact": source_art["artifact_id"],
            "source_text": source_art["text"],
            "target_document": "—",
            "target_type": "—",
            "target_artifact": "—",
            "target_text": "—",
            "relationship": relationship_type,
            "status": "UNMAPPED",
            "similarity": 0.0,
            "confidence": "Low",
            "evidence": "No target artifact satisfied minimum lexical match threshold"
        }


def analyze_project_documents_traceability(project_documents):
    """
    Executes True Project-Level Cross-Document Traceability across all uploaded documents:
    1. Collects and normalizes all extracted artifacts with canonical deduplication.
    2. Builds TF-IDF lexical vocabulary across the entire project collection.
    3. Traces primary engineering path: BRD -> SRS -> FRD -> User Story -> Test Case.
    4. Traces supporting impact path: Change Request -> Requirements & Meeting Minutes -> Decisions.
    5. Builds the Full Source -> Target Traceability Matrix, Traceability Chains, and Graph.
    """
    all_artifacts = []
    seen_canonical_ids = set()
    docs_by_type = {}
    doc_type_counts = {}

    for doc in project_documents:
        doc_id = doc.get("document_id") or doc.get("id")
        doc_name = doc.get("filename") or doc.get("name") or "Document"
        doc_type = doc.get("document_type") or "Unknown"
        doc_artifacts = doc.get("artifacts") or []

        if doc_type not in docs_by_type:
            docs_by_type[doc_type] = []

        valid_doc_artifacts = []
        for art in doc_artifacts:
            art_id = art.get("artifact_id") or f"ART-{len(all_artifacts)+1:03d}"
            canonical_key = f"{doc_name}::{art_id}"
            
            # Prevent duplicate canonical identity extraction
            if canonical_key in seen_canonical_ids:
                continue
            seen_canonical_ids.add(canonical_key)

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
            valid_doc_artifacts.append(norm_art)

        docs_by_type[doc_type].extend(valid_doc_artifacts)
        doc_type_counts[doc_type] = len(docs_by_type[doc_type])

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

    # Direct Pairwise Relationships List (The Exact Source -> Target Matrix)
    traceability_relationships = []
    
    # 1. BRD -> SRS (TRACEABLE_TO)
    for brd in brd_list:
        rel = match_artifact_to_candidates(brd, srs_list, vectorizer, relationship_type="TRACEABLE_TO")
        traceability_relationships.append(rel)

    # 2. SRS -> FRD (IMPLEMENTED_BY)
    for srs in srs_list:
        rel = match_artifact_to_candidates(srs, frd_list, vectorizer, relationship_type="IMPLEMENTED_BY")
        traceability_relationships.append(rel)

    # 3. SRS / FRD -> User Story (REALIZED_BY)
    for srs in srs_list:
        rel = match_artifact_to_candidates(srs, us_list, vectorizer, relationship_type="REALIZED_BY")
        traceability_relationships.append(rel)

    # 4. User Story -> Test Case (VERIFIED_BY)
    for us in us_list:
        rel = match_artifact_to_candidates(us, tc_list, vectorizer, relationship_type="VERIFIED_BY")
        traceability_relationships.append(rel)

    # 5. Change Requests -> Requirements (AFFECTS)
    cr_impacts = []
    for cr in cr_list:
        rel = match_artifact_to_candidates(cr, srs_list + frd_list, vectorizer, relationship_type="AFFECTS", min_match=0.15, min_partial=0.08)
        traceability_relationships.append(rel)
        cr_impacts.append({
            "cr_id": cr["artifact_id"],
            "cr_doc": cr["document_name"],
            "cr_text": cr["text"],
            "affected_doc": rel["target_document"],
            "affected_req_id": rel["target_artifact"],
            "status": rel["status"],
            "similarity": rel["similarity"],
            "evidence": rel["evidence"]
        })

    # 6. Meeting Minutes -> Artifacts (RELATED_TO)
    mom_links = []
    for mom in mom_list:
        rel = match_artifact_to_candidates(mom, brd_list + srs_list + cr_list, vectorizer, relationship_type="RELATED_TO", min_match=0.15, min_partial=0.08)
        traceability_relationships.append(rel)
        mom_links.append({
            "mom_id": mom["artifact_id"],
            "mom_doc": mom["document_name"],
            "mom_text": mom["text"],
            "referenced_doc": rel["target_document"],
            "referenced_req_id": rel["target_artifact"],
            "status": rel["status"],
            "similarity": rel["similarity"],
            "evidence": rel["evidence"]
        })

    # End-to-End Traceability Chains Assembly (BRD -> SRS -> FRD -> US -> TC)
    root_artifacts = brd_list if brd_list else srs_list if srs_list else all_artifacts
    traceability_chains = []
    top_conflicts = []
    top_unmapped = []

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

        # Step 1: BRD
        if root_art["document_type"] == "BRD":
            chain["brd"] = {
                "id": root_art["artifact_id"],
                "name": root_art["document_name"],
                "text": root_art["text"]
            }
            srs_rel = match_artifact_to_candidates(root_art, srs_list, vectorizer, relationship_type="TRACEABLE_TO")
            if srs_rel["status"] in ["MATCHED", "PARTIAL", "CONFLICT"]:
                matched_srs_art = next((s for s in srs_list if s["artifact_id"] == srs_rel["target_artifact"]), None)
                if matched_srs_art:
                    chain["srs"] = {
                        "id": matched_srs_art["artifact_id"],
                        "name": matched_srs_art["document_name"],
                        "text": matched_srs_art["text"]
                    }
                    chain["evidence_chain"].append(f"BRD→SRS [{srs_rel['status']}]: {srs_rel['evidence']}")
            current_srs = next((s for s in srs_list if s["artifact_id"] == srs_rel["target_artifact"]), None)
        else:
            current_srs = root_art
            chain["srs"] = {
                "id": current_srs["artifact_id"],
                "name": current_srs["document_name"],
                "text": current_srs["text"]
            }

        # Step 2: FRD
        current_frd = None
        if current_srs:
            frd_rel = match_artifact_to_candidates(current_srs, frd_list, vectorizer, relationship_type="IMPLEMENTED_BY")
            if frd_rel["status"] in ["MATCHED", "PARTIAL", "CONFLICT"]:
                matched_frd_art = next((f for f in frd_list if f["artifact_id"] == frd_rel["target_artifact"]), None)
                if matched_frd_art:
                    chain["frd"] = {
                        "id": matched_frd_art["artifact_id"],
                        "name": matched_frd_art["document_name"],
                        "text": matched_frd_art["text"]
                    }
                    chain["evidence_chain"].append(f"SRS→FRD [{frd_rel['status']}]: {frd_rel['evidence']}")
                    current_frd = matched_frd_art

        # Step 3: User Story
        current_us = None
        target_for_us = current_frd or current_srs
        if target_for_us:
            us_rel = match_artifact_to_candidates(target_for_us, us_list, vectorizer, relationship_type="REALIZED_BY")
            if us_rel["status"] in ["MATCHED", "PARTIAL", "CONFLICT"]:
                matched_us_art = next((u for u in us_list if u["artifact_id"] == us_rel["target_artifact"]), None)
                if matched_us_art:
                    chain["user_story"] = {
                        "id": matched_us_art["artifact_id"],
                        "name": matched_us_art["document_name"],
                        "text": matched_us_art["text"]
                    }
                    chain["evidence_chain"].append(f"FRD→US [{us_rel['status']}]: {us_rel['evidence']}")
                    current_us = matched_us_art

        # Step 4: Test Case
        target_for_tc = current_us or current_frd or current_srs
        if target_for_tc:
            tc_rel = match_artifact_to_candidates(target_for_tc, tc_list, vectorizer, relationship_type="VERIFIED_BY")
            if tc_rel["status"] in ["MATCHED", "PARTIAL", "CONFLICT"]:
                matched_tc_art = next((t for t in tc_list if t["artifact_id"] == tc_rel["target_artifact"]), None)
                if matched_tc_art:
                    chain["test_case"] = {
                        "id": matched_tc_art["artifact_id"],
                        "name": matched_tc_art["document_name"],
                        "text": matched_tc_art["text"]
                    }
                    chain["evidence_chain"].append(f"US→TC [{tc_rel['status']}]: {tc_rel['evidence']}")

        # Determine overall chain status
        chain_statuses = [ev.split('[')[1].split(']')[0] for ev in chain["evidence_chain"] if '[' in ev]
        if "CONFLICT" in chain_statuses:
            overall = "CONFLICT"
            top_conflicts.append({
                "source_id": root_art["artifact_id"],
                "source_doc": root_art["document_name"],
                "source_text": root_art["text"],
                "reason": next((ev for ev in chain["evidence_chain"] if "contradiction" in ev.lower()), "Security or behavioral contradiction detected in downstream specifications")
            })
        elif all(st == "MATCHED" for st in chain_statuses) and len(chain_statuses) >= 2:
            overall = "MATCHED"
        elif any(st in ["MATCHED", "PARTIAL"] for st in chain_statuses):
            overall = "PARTIAL"
        else:
            overall = "UNMAPPED"
            top_unmapped.append({
                "artifact_id": root_art["artifact_id"],
                "document_name": root_art["document_name"],
                "text": root_art["text"],
                "reason": "No downstream requirement, functional spec, or test case satisfied lexical match threshold"
            })

        chain["overall_status"] = overall
        traceability_chains.append(chain)

    # Status counts over all pairwise direct relationships
    status_counts = {
        "MATCHED": sum(1 for r in traceability_relationships if r["status"] == "MATCHED"),
        "PARTIAL": sum(1 for r in traceability_relationships if r["status"] == "PARTIAL"),
        "CONFLICT": sum(1 for r in traceability_relationships if r["status"] == "CONFLICT"),
        "UNMAPPED": sum(1 for r in traceability_relationships if r["status"] == "UNMAPPED")
    }

    # Traceability Graph (Real Nodes and Discovered Edges)
    graph_nodes = []
    graph_edges = []
    node_ids_added = set()

    for art in all_artifacts:
        node_id = f"{art['document_name']}::{art['artifact_id']}"
        if node_id not in node_ids_added:
            graph_nodes.append({
                "id": node_id,
                "artifact_id": art["artifact_id"],
                "document_name": art["document_name"],
                "document_type": art["document_type"],
                "text": art["text"][:100] + ("..." if len(art["text"]) > 100 else "")
            })
            node_ids_added.add(node_id)

    for rel in traceability_relationships:
        if rel["target_artifact"] != "—":
            source_node = f"{rel['source_document']}::{rel['source_artifact']}"
            target_node = f"{rel['target_document']}::{rel['target_artifact']}"
            graph_edges.append({
                "source": source_node,
                "target": target_node,
                "relationship": rel["relationship"],
                "status": rel["status"],
                "similarity": rel["similarity"],
                "evidence": rel["evidence"]
            })

    # Exact Dynamic Path Coverage Calculations
    brd_mapped = sum(1 for r in traceability_relationships if r["source_type"] == "BRD" and r["status"] in ["MATCHED", "PARTIAL", "CONFLICT"])
    brd_total = len(brd_list)
    brd_srs_cov = round((brd_mapped / brd_total * 100), 1) if brd_total > 0 else 0.0

    srs_frd_mapped = sum(1 for r in traceability_relationships if r["source_type"] == "SRS" and r["relationship"] == "IMPLEMENTED_BY" and r["status"] in ["MATCHED", "PARTIAL", "CONFLICT"])
    srs_total = len(srs_list)
    srs_frd_cov = round((srs_frd_mapped / srs_total * 100), 1) if srs_total > 0 else 0.0

    srs_us_mapped = sum(1 for r in traceability_relationships if r["source_type"] == "SRS" and r["relationship"] == "REALIZED_BY" and r["status"] in ["MATCHED", "PARTIAL", "CONFLICT"])
    srs_us_cov = round((srs_us_mapped / srs_total * 100), 1) if srs_total > 0 else 0.0

    us_tc_mapped = sum(1 for r in traceability_relationships if r["source_type"] == "User Story" and r["relationship"] == "VERIFIED_BY" and r["status"] in ["MATCHED", "PARTIAL", "CONFLICT"])
    us_total = len(us_list)
    us_tc_cov = round((us_tc_mapped / us_total * 100), 1) if us_total > 0 else 0.0

    root_total = len(root_artifacts)
    root_mapped = sum(1 for c in traceability_chains if c["overall_status"] in ["MATCHED", "PARTIAL", "CONFLICT"])
    overall_cov = round((root_mapped / root_total * 100), 1) if root_total > 0 else 0.0

    return {
        "success": True,
        "mode": "project_intelligence",
        "title": "ReqVision AI — Software Intelligence Report",
        "analysis_type": "Cross-Document Lexical Traceability",
        "summary": {
            "total_documents": len(project_documents),
            "total_artifacts": len(all_artifacts),
            "total_relationships": len(traceability_relationships),
            "document_types": doc_type_counts,
            "coverage_percentage": overall_cov,
            "status_breakdown": status_counts,
            "path_coverage": {
                "brd_to_srs_coverage": f"{brd_srs_cov}% ({brd_mapped}/{brd_total})",
                "srs_to_frd_coverage": f"{srs_frd_cov}% ({srs_frd_mapped}/{srs_total})",
                "srs_to_user_story_coverage": f"{srs_us_cov}% ({srs_us_mapped}/{srs_total})",
                "user_story_to_test_case_coverage": f"{us_tc_cov}% ({us_tc_mapped}/{us_total})"
            }
        },
        "traceability_matrix": traceability_relationships,
        "traceability_chains": traceability_chains,
        "traceability_graph": {
            "nodes": graph_nodes,
            "edges": graph_edges
        },
        "top_conflicts": top_conflicts,
        "top_unmapped": top_unmapped,
        "change_request_impacts": cr_impacts,
        "meeting_minutes_links": mom_links,
        "documents": [
            {
                "document_id": doc.get("document_id") or doc.get("id"),
                "filename": doc.get("filename") or doc.get("name"),
                "document_type": doc.get("document_type"),
                "artifact_count": len(docs_by_type.get(doc.get("document_type"), []))
            } for doc in project_documents
        ]
    }
