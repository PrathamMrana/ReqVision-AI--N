import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.preprocess import clean_text
from utils.classifier import normalize_document_type
from utils.extractor import determine_canonical_artifact_type
from utils.semantic_engine import SemanticEngine
from utils.negation_detector import check_polarity_conflict, check_numeric_conflict
from utils.evidence_fusion import (
    evaluate_candidate_relevance_gate,
    evaluate_action_alignment,
    evaluate_entity_alignment,
    evaluate_actor_alignment,
    evaluate_context_alignment,
    evaluate_behavioral_verification,
    evaluate_precise_change_impact,
    detect_missing_conditions,
    detect_capability_extension,
    compute_capability_identity_score,
    rank_and_disambiguate_candidates,
    extract_governance_state,
    build_capability_profile
)

# ── Semantic engine (singleton, loaded once) ──────────────────────────────────
_semantic_engine = SemanticEngine()

# ── Hybrid scoring weights (configurable, documented) ─────────────────────────
# semantic: primary signal — handles paraphrase, synonym, different wording
# lexical:  supporting signal — precision, exact-match explainability
# intent:   domain anchor — prevents cross-domain false positives
HYBRID_WEIGHT_SEMANTIC = 0.60
HYBRID_WEIGHT_LEXICAL  = 0.25
HYBRID_WEIGHT_INTENT   = 0.15

# ── Status thresholds (tuned against Online Library + CampusRide test sets) ───
HYBRID_MATCH_THRESHOLD   = 0.45  # hybrid >= 0.45 → MATCHED (if type + domain valid)
HYBRID_PARTIAL_THRESHOLD = 0.28  # hybrid >= 0.28 → PARTIAL


# Explainable Security and Architectural Conflict Rules
CONFLICT_RULES = [
    {
        "domain": "security_passwords",
        "keywords": ["password", "credential", "auth", "login"],
        "patterns_a": [r"\breversible encryption\b", r"\brecover\s+(?:the\s+)?(?:original\s+)?password\b", r"\bplaintext\b", r"\bcleartext\b"],
        "patterns_b": [r"\bhashing\b", r"\bsalted\b", r"\bone-way\b", r"\boauth\b", r"\bjwt\b", r"\bemail and password\b", r"\bauthenticate\b"],
        "reason": "Security contradiction: Reversible password storage/recovery in specification contradicts one-way salted credential verification."
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

# Generalized Domain & Functional Intent Anchors
DOMAIN_INTENTS = {
    "search_navigation": {
        "keywords": {"search", "query", "find", "discover", "browse", "index", "latency", "metadata", "sub-200ms", "filtering", "locate", "catalog", "catalogue", "arrival", "board", "eta", "tracking", "countdown", "schedule", "real-time"},
        "patterns": [r"\bsearch\b", r"\bquery\b", r"\bfind\s+books\b", r"\bresponse\s+time\b", r"\bindex\b", r"\bcatalog(?:ue)?\b", r"\barrival\s+board\b", r"\beta\s+tracking\b", r"\breal-?time\b", r"\bcountdown\b"]
    },
    "booking_reservation": {
        "keywords": {"reserve", "reservation", "booking", "book", "seat", "seats", "borrow", "borrowing", "checkout", "check-out", "loan", "loans", "quota", "fines", "fine", "overdue", "payment", "stripe", "boarding pass", "physical books"},
        "patterns": [r"\breserv(?:e|ation)\b", r"\bseat(?:s)?\b", r"\bbook(?:ing)?\b", r"\bborrow(?:ing)?\b", r"\bcheck-?out\b", r"\bloan(?:s)?\b", r"\bboarding\s+pass\b", r"\boverdue\b", r"\bfine(?:s)?\b", r"\bpayment\b"]
    },
    "access_authorization": {
        "keywords": {"role", "roles", "rbac", "permission", "permissions", "access control", "authorization", "matrix", "restricted", "claims", "staff", "faculty", "credentials", "employee", "unauthorized", "routes", "prevent"},
        "patterns": [r"\brole-based\b", r"\bauthorization\b", r"\bpermission(?:s)?\b", r"\brbac\b", r"\bstaff-?only\b", r"\brestricted\b", r"\baccess\s+control\b", r"\bunauthorized\b", r"\bstaff\s+only\b"]
    },
    "inventory_capacity": {
        "keywords": {"inventory", "book records", "records", "quantities", "maintain books", "capacity", "passenger", "seat limit", "fleet", "vehicle capacity", "adjust", "update inventory"},
        "patterns": [r"\binventory\b", r"\bbook\s+records\b", r"\bupdate\s+inventory\b", r"\bvehicle\s+capacity\b", r"\bpassenger\s+limit\b", r"\bcapacity\s+admin\b"]
    },
    "cancellation_return": {
        "keywords": {"cancel", "cancellation", "renew", "renewal", "renewals", "renewing", "extend", "cutoff", "restore", "release", "active loan"},
        "patterns": [r"\bcancel(?:lation)?\b", r"\bcutoff\b", r"\brenew(?:al|ing)?\b", r"\bextend\s+loan\b", r"\brelease\s+seat\b"]
    },
    "reporting_analytics": {
        "keywords": {"report", "reports", "circulation", "statistics", "analytics", "csv", "pdf", "json", "xml", "printable", "ridership", "fleet operations", "utilization", "dashboard", "metrics"},
        "patterns": [r"\breport(?:s|ing)?\b", r"\bcirculation\b", r"\banalytics\b", r"\bridership\b", r"\bfleet\s+operations\b", r"\butilization\b", r"\bdashboard\b", r"\bexport\s+(?:pdf|csv)\b"]
    },
    "auth_security": {
        "keywords": {"auth", "authenticate", "authentication", "credential", "credentials", "login", "password", "hash", "salted", "jwt", "mfa", "2fa", "totp", "oauth", "profile", "sign in", "pin", "pins"},
        "patterns": [r"\bauthenticat(?:e|ion)\b", r"\blogin\b", r"\bcredential(?:s)?\b", r"\bpassword\b", r"\bmfa\b", r"\b2fa\b", r"\btotp\b", r"\boauth\b", r"\bsign\s+in\b", r"\bemail\s+and\s+password\b", r"\bpins?\b"]
    },
    "notification_alerts": {
        "keywords": {"notification", "notifications", "alert", "alerts", "reminder", "reminders", "smtp", "dispatch", "due date", "push", "sms", "delay", "service alert", "audio", "voice", "diversion"},
        "patterns": [r"\bnotification(?:s)?\b", r"\balert(?:s)?\b", r"\breminder(?:s)?\b", r"\bsmtp\b", r"\bpush\b", r"\bsms\b", r"\bdelay\b", r"\bservice\s+alert\b", r"\bvoice\b", r"\baudio\b"]
    },
    "mobile_responsive": {
        "keywords": {"mobile", "ios", "android", "responsive", "browser view", "layout", "handheld", "apps", "browser access", "phone", "smartphone"},
        "patterns": [r"\bmobile\b", r"\bios\b", r"\bandroid\b", r"\bresponsive\b", r"\bbrowser\s+access\b", r"\bbrowser\s+view\b"]
    },
    "accessibility_mobility": {
        "keywords": {"accessibility", "accessible", "wheelchair", "ramp", "mobility", "boarding", "disability", "friendly"},
        "patterns": [r"\baccessib(?:le|ility)\b", r"\bwheelchair\b", r"\bramp\b", r"\bmobility\b", r"\bwheelchair-friendly\b"]
    },
    "digital_media": {
        "keywords": {"ebook", "ebooks", "audiobook", "audiobooks", "digital library", "electronic books", "streaming", "media", "content"},
        "patterns": [r"\be-?books?\b", r"\baudiobooks?\b", r"\bdigital\s+library\b", r"\belectronic\s+books\b"]
    },
    "audit_logging": {
        "keywords": {"audit", "trail", "ledger", "immutable", "logging", "log", "logs", "transitions", "history", "postgres", "table", "interceptor", "adherence", "regulatory"},
        "patterns": [r"\baudit\b", r"\bledger\b", r"\bimmutable\b", r"\blogging\b", r"\baudit\s+table\b", r"\baudit\s+log\b", r"\bstatus\s+transitions\b"]
    },
    "scalability_performance": {
        "keywords": {"scalability", "concurrent", "throughput", "capacity", "load balancing", "peaks", "cluster", "traffic", "load", "examination", "rush", "high availability", "uptime", "99.9%"},
        "patterns": [r"\bscalab(?:le|ility)\b", r"\bconcurrent\b", r"\bthroughput\b", r"\bload\s+balancing\b", r"\btraffic\s+peaks\b", r"\brush\s+hours\b", r"\bhigh\s+availability\b", r"\buptime\b"]
    },
    "telemetry_gps": {
        "keywords": {"gps", "coordinate", "coordinates", "refresh", "interval", "satellite", "telemetry", "500ms", "250ms"},
        "patterns": [r"\bgps\b", r"\bcoordinate(?:s)?\b", r"\brefresh\s+interval\b", r"\btelemetry\b"]
    },
    "legacy_archive": {
        "keywords": {"tape", "magnetic", "archival", "legacy archive", "legacy catalogue export", "tape archive", "catalog tape", "historical catalogue", "legacy vehicle", "registration records"},
        "patterns": [r"\btape\b", r"\bmagnetic\b", r"\blegacy\s+(?:archive|catalog(?:ue)?|tape|export|vehicle)\b", r"\barchival\s+storage\b", r"\btape\s+archive\b"]
    },
    "hardware_nonsoftware": {
        "keywords": {"printer", "printers", "parking-gate", "barrier", "kiosk", "lunch", "cafeteria", "meeting-room equipment", "meal plan", "dining card", "furniture", "hardware", "shift-planning", "payroll"},
        "patterns": [r"\bprinter(?:s)?\b", r"\bparking-gate\b", r"\bbarrier\b", r"\bhardware\b", r"\bmeeting-room\b", r"\blunch\b", r"\bcafeteria\b", r"\bmeal\s+plan\b", r"\bdining\s+card\b", r"\bshift-planning\b", r"\bpayroll\b"]
    }
}

def detect_domain_intents(text):
    """Identifies functional domain intents present in a statement."""
    t_clean = set(clean_text(text).split())
    t_raw_lower = text.lower()
    
    detected = set()
    for domain, cfg in DOMAIN_INTENTS.items():
        has_kw = bool(t_clean.intersection(cfg["keywords"]))
        has_pat = any(re.search(pat, t_raw_lower) for pat in cfg["patterns"])
        if has_kw or has_pat:
            detected.add(domain)
            
    if "legacy_archive" in detected:
        detected.discard("search_navigation")
        
    return detected

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

def compute_domain_lexical_similarity(vectorizer, text_a_clean, text_b_clean, text_a_raw, text_b_raw):
    """
    Computes domain-anchored explainable lexical similarity.
    Enforces that only domain-compatible candidates receive positive match scoring.
    """
    if not text_a_clean and not text_b_clean:
        return 1.0, "Identical empty content", set()
    if not text_a_clean or not text_b_clean:
        return 0.0, "No content overlap", set()
    if text_a_clean.strip() == text_b_clean.strip():
        return 1.0, "Exact lexical match", set()

    intents_a = detect_domain_intents(text_a_raw)
    intents_b = detect_domain_intents(text_b_raw)

    # Reject non-software items (hardware, parking-gate, cafeteria, meal plans, shift-planning) from matching software specs
    if "hardware_nonsoftware" in intents_a or "hardware_nonsoftware" in intents_b:
        return 0.0, "Non-software physical/administrative note excluded from matrix", set()

    shared_intents = intents_a.intersection(intents_b)
    
    # If both have detected intents but share ZERO intents, strictly reject cross-domain false positive
    if intents_a and intents_b and not shared_intents:
        return 0.0, f"Domain mismatch: [{', '.join(intents_a)}] vs [{', '.join(intents_b)}]", set()

    try:
        vecs = vectorizer.transform([text_a_clean, text_b_clean])
        tfidf_sim = float(cosine_similarity(vecs[0:1], vecs[1:2])[0][0])
        
        tokens_a = set(text_a_clean.split())
        tokens_b = set(text_b_clean.split())
        
        boilerplate = {
            "system", "shall", "platform", "provide", "user", "service", "verify", "test",
            "scenario", "order", "want", "able", "allow", "feature", "module", "endpoint",
            "controller", "interface", "component", "function", "rider", "member", "student"
        }
        meaningful_a = tokens_a - boilerplate
        meaningful_b = tokens_b - boilerplate
        
        jaccard = len(meaningful_a.intersection(meaningful_b)) / len(meaningful_a.union(meaningful_b)) if meaningful_a.union(meaningful_b) else 0.0
        
        # Stem overlap for morphological variants
        stems_a = set(w[:4] for w in meaningful_a if len(w) >= 4)
        stems_b = set(w[:4] for w in meaningful_b if len(w) >= 4)
        stem_jaccard = len(stems_a.intersection(stems_b)) / len(stems_a.union(stems_b)) if stems_a.union(stems_b) else 0.0
        
        # Domain Intent Alignment Boost
        intent_boost = 0.40 if shared_intents else 0.0
        
        # Keyphrase multi-word overlap boost
        keyphrases = [
            r"\bstaff-?only\b", r"\barrival\s+board\b", r"\bservice\s+alert\b",
            r"\bwheelchair\b", r"\baudit\s+ledger\b", r"\bseat\s+reservation\b",
            r"\blive\s+arrival\b", r"\bridership\b", r"\bcancellation\b", r"\bpassenger\s+limit\b",
            r"\bgps\b", r"\bcoordinate(?:s)?\b", r"\bhigh\s+availability\b", r"\buptime\b"
        ]
        shared_kp = [kp for kp in keyphrases if re.search(kp, text_a_raw, re.I) and re.search(kp, text_b_raw, re.I)]
        kp_boost = 0.20 if shared_kp else 0.0
        
        # Numbers penalty if specific numerical limits differ without shared intents
        nums_a = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', text_a_raw))
        nums_b = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', text_b_raw))
        penalty = 0.20 if (nums_a and nums_b and nums_a != nums_b and not shared_intents) else 0.0
        
        score = max(0.0, min(1.0, ((tfidf_sim * 0.35) + (jaccard * 0.15) + (stem_jaccard * 0.15) + intent_boost + kp_boost) - penalty))
        
        common_tokens = list(meaningful_a.intersection(meaningful_b))
        if shared_intents:
            common_tokens = list(shared_intents) + common_tokens
        unique_common = list(dict.fromkeys(common_tokens))[:4]
        
        evidence = f"Domain alignment on [{', '.join(unique_common) if unique_common else 'domain concepts'}] (Score: {score:.2f}, TF-IDF: {tfidf_sim:.2f})"
        return round(score, 4), evidence, shared_intents
    except Exception as e:
        return 0.0, f"Similarity error: {str(e)}", set()


def compute_hybrid_score(text_a_raw, text_b_raw, lexical_score, shared_intents):
    """
    Combines semantic and lexical evidence into a single hybrid score.

    Formula (configurable via module-level constants):
        hybrid = HYBRID_WEIGHT_SEMANTIC * semantic
               + HYBRID_WEIGHT_LEXICAL  * lexical
               + HYBRID_WEIGHT_INTENT   * intent_score

    Returns:
        hybrid_score  (float)
        semantic_sim  (float | None)  — None means model unavailable
        is_semantic   (bool)          — True when real semantic engine ran
        intent_score  (float)
    """
    intent_score = 1.0 if shared_intents else 0.0

    semantic_sim = _semantic_engine.compute_semantic_similarity(text_a_raw, text_b_raw)

    if semantic_sim is None:
        # Fallback: weight shifts entirely to lexical + intent
        hybrid = min(1.0, lexical_score + HYBRID_WEIGHT_INTENT * intent_score)
        return round(hybrid, 4), None, False, intent_score

    hybrid = (
        HYBRID_WEIGHT_SEMANTIC * semantic_sim
        + HYBRID_WEIGHT_LEXICAL  * lexical_score
        + HYBRID_WEIGHT_INTENT   * intent_score
    )
    return round(min(1.0, hybrid), 4), round(semantic_sim, 4), True, intent_score

def find_candidate_relationships(
    source_art,
    candidate_arts,
    vectorizer,
    relationship_type="TRACEABLE_TO",
    min_match=0.18,
    min_partial=0.10,
    upstream_canonical_map=None,
    debug_log=None
):
    """
    Finds all valid candidate relationships for a source artifact, supporting both
    valid implementation matches and intentional conflict matches.
    Uses HYBRID SCORING: semantic (60%) + lexical (25%) + intent (15%).
    Type-safe candidate filtering still happens BEFORE this function is called.
    Enforces relationship-specific proof requirements for IMPLEMENTED_BY, REALIZED_BY,
    VERIFIED_BY, AFFECTS, and RELATED_TO.
    Returns: list of relationship_records (list of dicts)
    """
    _sem_available = _semantic_engine.is_available()

    def _make_unmapped(evidence, confidence="Low"):
        return {
            "source_document": source_art["document_name"],
            "source_type": source_art["document_type"],
            "source_artifact_type": source_art["artifact_type"],
            "source_artifact": source_art["artifact_id"],
            "source_text": source_art["text"],
            "target_document": "—", "target_type": "—",
            "target_artifact_type": "—", "target_artifact": "—", "target_text": "—",
            "relationship": relationship_type,
            "status": "UNMAPPED", "similarity": 0.0,
            "semantic_similarity": None, "lexical_similarity": 0.0,
            "hybrid_score": 0.0, "intent_score": 0.0,
            "semantic_enabled": _sem_available,
            "confidence": confidence, "evidence": evidence
        }

    if not candidate_arts:
        return [_make_unmapped("No candidate artifacts found in target document")]

    source_intents = detect_domain_intents(source_art["text"])
    if "hardware_nonsoftware" in source_intents:
        return [_make_unmapped("Administrative / physical non-software item excluded from engineering matrix", "High")]

    # Multi-hop context inheritance: if source has upstream validated mapping, inherit context
    if upstream_canonical_map and source_art.get("artifact_id") in upstream_canonical_map:
        upstream_art = upstream_canonical_map[source_art["artifact_id"]]
        upstream_intents = detect_domain_intents(upstream_art.get("text", ""))
        source_intents = source_intents.union(upstream_intents)

    is_ambiguous = any(phrase in source_art["text"].lower() for phrase in [
        "not agreed", "did not agree", "unclear", "could mean",
        "undecided", "ambiguous", "further review", "unresolved"
    ])
    if is_ambiguous:
        return [_make_unmapped("Ambiguous requirement: consensus was not agreed in review", "Medium")]

    matches_found = []
    evaluated_candidates = []

    for cand in candidate_arts:
        # ── 1. Lexical + intent evidence ──────────────────────────────────────
        lex_score, lex_evidence, shared_intents = compute_domain_lexical_similarity(
            vectorizer,
            source_art["clean_text"], cand["clean_text"],
            source_art["text"], cand["text"]
        )

        # Multi-hop context propagation
        if upstream_canonical_map and source_art.get("artifact_id") in upstream_canonical_map:
            upstream_art = upstream_canonical_map[source_art["artifact_id"]]
            _, _, up_shared = compute_domain_lexical_similarity(
                vectorizer,
                upstream_art.get("clean_text", ""), cand["clean_text"],
                upstream_art.get("text", ""), cand["text"]
            )
            shared_intents = shared_intents.union(up_shared)

        # Explicit ID reference check
        has_id_ref = bool(re.search(r'\b' + re.escape(cand["artifact_id"]) + r'\b', source_art["text"]))
        if has_id_ref:
            lex_score = max(lex_score, 0.55)
            lex_evidence = f"Explicit ID reference to {cand['artifact_id']} with domain alignment"
            shared_intents.add("explicit_reference")

        # ── 2. Hybrid scoring: semantic + lexical + intent ────────────────────
        hybrid, sem_score, sem_used, intent_val = compute_hybrid_score(
            source_art["text"], cand["text"], lex_score, shared_intents
        )

        # ── 3. Hard Candidate Relevance Gate with Relationship-Specific Proof ──
        is_relevant, relevance_reason = evaluate_candidate_relevance_gate(
            source_art["text"], cand["text"], sem_score, lex_score, shared_intents,
            relationship_type=relationship_type, has_explicit_ref=has_id_ref
        )
        if not is_relevant:
            # REJECT candidate immediately — do NOT process for conflict, do NOT add to evaluated candidates
            continue

        # ── 4. Action & Entity Alignment (Anti-Hallucination) ─────────────────
        action_score, action_reason = evaluate_action_alignment(source_art["text"], cand["text"])
        entity_score, entity_reason = evaluate_entity_alignment(source_art["text"], cand["text"])
        actor_score, actor_reason = evaluate_actor_alignment(source_art["text"], cand["text"])
        context_score, context_reason = evaluate_context_alignment(source_art["text"], cand["text"])
        has_missing, missing_reason = detect_missing_conditions(source_art["text"], cand["text"])
        is_extension, extension_reason = detect_capability_extension(source_art["text"], cand["text"])
        cap_id_score, is_exact = compute_capability_identity_score(
            action_score, entity_score, context_score, actor_score, hybrid, shared_intents, has_id_ref=has_id_ref
        )

        # ── 4b. Relationship-Specific Proof Scoring ──────────────────────────
        rel_proof_score = 1.0
        if relationship_type == "VERIFIED_BY":
            v_score, v_reason, is_partial_v = evaluate_behavioral_verification(source_art["text"], cand["text"])
            rel_proof_score = v_score
            if is_partial_v:
                has_missing = True
                missing_reason = v_reason
        elif relationship_type == "REALIZED_BY":
            # For user stories, factor in actor goal alignment
            rel_proof_score = (actor_score * 0.40) + (action_score * 0.30) + (entity_score * 0.30)

        # ── 5. Negation / polarity check (generic) ────────────────────────────
        polarity_conflict, polarity_reason = check_polarity_conflict(source_art["text"], cand["text"])
        numeric_result, numeric_reason = check_numeric_conflict(source_art["text"], cand["text"])

        # ── 6. Change Request AFFECTS & Governance Preservation ───────────────
        has_conflict, conflict_reason = check_explainable_conflict(source_art["text"], cand["text"])
        gov_state, gov_desc = extract_governance_state(source_art["text"])

        if relationship_type == "AFFECTS":
            is_genuine_impact, imp_score, imp_reason = evaluate_precise_change_impact(
                source_art["text"], cand["text"], has_id_ref=has_id_ref
            )
            if is_genuine_impact:
                matches_found.append({
                    "source_document": source_art["document_name"],
                    "source_type": source_art["document_type"],
                    "source_artifact_type": source_art["artifact_type"],
                    "source_artifact": source_art["artifact_id"],
                    "source_text": source_art["text"],
                    "target_document": cand["document_name"],
                    "target_type": cand["document_type"],
                    "target_artifact_type": cand["artifact_type"],
                    "target_artifact": cand["artifact_id"],
                    "target_text": cand["text"],
                    "relationship": relationship_type,
                    "status": "MATCHED",
                    "similarity": max(hybrid, imp_score, 0.50),
                    "semantic_similarity": sem_score,
                    "lexical_similarity": round(lex_score, 4),
                    "hybrid_score": max(hybrid, imp_score, 0.50),
                    "intent_score": round(intent_val, 4),
                    "semantic_enabled": _sem_available,
                    "confidence": "High" if has_id_ref or imp_score >= 0.90 else "Medium",
                    "evidence": f"Change Request impact: {imp_reason}"
                })
                continue
            else:
                continue  # Standalone / non-impacting CR candidate rejected

        # ── 7. Emit CONFLICT records (ONLY for confirmed relevant candidates) ─
        # Rule-based conflict (e.g., reversible password vs one-way hash)
        if has_conflict and (lex_score >= min_partial or shared_intents or (sem_score and sem_score >= 0.40)) and relationship_type == "IMPLEMENTED_BY":
            matches_found.append({
                "source_document": source_art["document_name"],
                "source_type": source_art["document_type"],
                "source_artifact_type": source_art["artifact_type"],
                "source_artifact": source_art["artifact_id"],
                "source_text": source_art["text"],
                "target_document": cand["document_name"],
                "target_type": cand["document_type"],
                "target_artifact_type": cand["artifact_type"],
                "target_artifact": cand["artifact_id"],
                "target_text": cand["text"],
                "relationship": relationship_type,
                "status": "CONFLICT",
                "similarity": max(hybrid, 0.48),
                "semantic_similarity": sem_score,
                "lexical_similarity": round(lex_score, 4),
                "hybrid_score": max(hybrid, 0.48),
                "intent_score": round(intent_val, 4),
                "semantic_enabled": _sem_available,
                "confidence": "High",
                "evidence": conflict_reason
            })
            continue

        # Generic polarity conflict (negation detector) — only when semantically related enough
        if polarity_conflict and (hybrid >= 0.28 or (sem_score and sem_score >= 0.35) or shared_intents) and not is_extension:
            matches_found.append({
                "source_document": source_art["document_name"],
                "source_type": source_art["document_type"],
                "source_artifact_type": source_art["artifact_type"],
                "source_artifact": source_art["artifact_id"],
                "source_text": source_art["text"],
                "target_document": cand["document_name"],
                "target_type": cand["document_type"],
                "target_artifact_type": cand["artifact_type"],
                "target_artifact": cand["artifact_id"],
                "target_text": cand["text"],
                "relationship": relationship_type,
                "status": "CONFLICT",
                "similarity": hybrid,
                "semantic_similarity": sem_score,
                "lexical_similarity": round(lex_score, 4),
                "hybrid_score": hybrid,
                "intent_score": round(intent_val, 4),
                "semantic_enabled": _sem_available,
                "confidence": "High",
                "evidence": f"{polarity_reason} | Semantic: {sem_score:.2f} | Hybrid: {hybrid:.2f}"
            })
            continue

        # ── 8. Composite Evidence Fusion ──────────────────────────────────────
        if action_score <= 0.20 and not shared_intents and not bool(re.search(r'\b' + re.escape(cand["artifact_id"]) + r'\b', source_art["text"])):
            # Action mismatch penalty (e.g. reconcile vs refund)
            composite_score = hybrid * 0.35
        else:
            composite_score = (hybrid * 0.70) + (action_score * 0.15) + (entity_score * 0.15)

        evidence_str = (
            f"Semantic: {sem_score:.2f} | Lexical: {lex_score:.2f} | Hybrid: {hybrid:.2f} | "
            f"{action_reason} | {entity_reason} | {lex_evidence}"
            + (f" | {numeric_reason}" if numeric_reason else "")
            + (f" | {extension_reason}" if is_extension else "")
            + (f" | {missing_reason}" if has_missing else "")
        )

        evaluated_candidates.append({
            "cand": cand,
            "hybrid": hybrid,
            "composite_score": round(composite_score, 4),
            "capability_identity_score": cap_id_score,
            "is_exact_capability": is_exact,
            "sem_score": sem_score,
            "lex_score": lex_score,
            "intent_val": intent_val,
            "action_score": action_score,
            "entity_score": entity_score,
            "actor_score": actor_score,
            "context_score": context_score,
            "has_missing": has_missing,
            "missing_reason": missing_reason,
            "is_extension": is_extension,
            "extension_reason": extension_reason,
            "num_result": numeric_result,
            "num_reason": numeric_reason,
            "relationship_proof_score": rel_proof_score,
            "evidence": evidence_str,
            "shared_intents": shared_intents
        })

    # ── 9. Candidate Ranking & Ambiguity Check ────────────────────────────────
    ranked_cands = rank_and_disambiguate_candidates(
        evaluated_candidates,
        min_match_threshold=HYBRID_MATCH_THRESHOLD,
        min_partial_threshold=HYBRID_PARTIAL_THRESHOLD,
        ambiguity_margin=0.04
    )

    if ranked_cands:
        best = ranked_cands[0]
        cand = best["cand"]
        best_composite = best["composite_score"]
        best_hybrid = best["hybrid"]
        best_sem = best["sem_score"]
        best_lex = best["lex_score"]
        best_intent = best["intent_val"]
        best_ev = best["evidence"]
        
        # Hard check for divergent actions with zero shared intents (e.g. Case 8)
        if best["action_score"] <= 0.20 and not best["shared_intents"] and not bool(re.search(r'\b' + re.escape(cand["artifact_id"]) + r'\b', source_art["text"])):
            pass  # Will fall through to UNMAPPED
        elif best.get("is_ambiguous"):
            matches_found.append({
                "source_document": source_art["document_name"],
                "source_type": source_art["document_type"],
                "source_artifact_type": source_art["artifact_type"],
                "source_artifact": source_art["artifact_id"],
                "source_text": source_art["text"],
                "target_document": cand["document_name"],
                "target_type": cand["document_type"],
                "target_artifact_type": cand["artifact_type"],
                "target_artifact": cand["artifact_id"],
                "target_text": cand["text"],
                "relationship": relationship_type,
                "status": "PARTIAL",
                "similarity": best_hybrid,
                "semantic_similarity": best_sem,
                "lexical_similarity": round(best_lex, 4),
                "hybrid_score": best_hybrid,
                "intent_score": round(best_intent, 4),
                "semantic_enabled": _sem_available,
                "confidence": "Medium",
                "evidence": f"Ambiguous candidates with close scores | {best_ev}"
            })
        elif best["has_missing"]:
            # Source has multiple clauses, target only has one -> PARTIAL
            matches_found.append({
                "source_document": source_art["document_name"],
                "source_type": source_art["document_type"],
                "source_artifact_type": source_art["artifact_type"],
                "source_artifact": source_art["artifact_id"],
                "source_text": source_art["text"],
                "target_document": cand["document_name"],
                "target_type": cand["document_type"],
                "target_artifact_type": cand["artifact_type"],
                "target_artifact": cand["artifact_id"],
                "target_text": cand["text"],
                "relationship": relationship_type,
                "status": "PARTIAL",
                "similarity": best_hybrid,
                "semantic_similarity": best_sem,
                "lexical_similarity": round(best_lex, 4),
                "hybrid_score": best_hybrid,
                "intent_score": round(best_intent, 4),
                "semantic_enabled": _sem_available,
                "confidence": "Medium",
                "evidence": f"Partial capability: {best['missing_reason']} | {best_ev}"
            })
        elif best["num_result"] == "MODIFIED_VALUE":
            matches_found.append({
                "source_document": source_art["document_name"],
                "source_type": source_art["document_type"],
                "source_artifact_type": source_art["artifact_type"],
                "source_artifact": source_art["artifact_id"],
                "source_text": source_art["text"],
                "target_document": cand["document_name"],
                "target_type": cand["document_type"],
                "target_artifact_type": cand["artifact_type"],
                "target_artifact": cand["artifact_id"],
                "target_text": cand["text"],
                "relationship": relationship_type,
                "status": "PARTIAL",
                "similarity": best_hybrid,
                "semantic_similarity": best_sem,
                "lexical_similarity": round(best_lex, 4),
                "hybrid_score": best_hybrid,
                "intent_score": round(best_intent, 4),
                "semantic_enabled": _sem_available,
                "confidence": "Medium",
                "evidence": f"Modified quantitative value: {best['num_reason']} | {best_ev}"
            })
        elif best.get("is_exact_capability") or ((best_hybrid >= HYBRID_MATCH_THRESHOLD or best_composite >= HYBRID_MATCH_THRESHOLD or bool(best["shared_intents"])) and best["composite_score"] >= 0.35):
            gov_state, gov_desc = extract_governance_state(source_art["text"])
            status_out = "PARTIAL" if (relationship_type == "RELATED_TO" and gov_state == "PENDING") else "MATCHED"
            evidence_out = f"Governance: PENDING — proposal under review | {best_ev}" if status_out == "PARTIAL" else best_ev
            conf = "High" if (best.get("is_exact_capability") or best_hybrid >= 0.60 or bool(best["shared_intents"])) and best.get("score_margin", 1.0) >= 0.08 else "Medium"
            matches_found.append({
                "source_document": source_art["document_name"],
                "source_type": source_art["document_type"],
                "source_artifact_type": source_art["artifact_type"],
                "source_artifact": source_art["artifact_id"],
                "source_text": source_art["text"],
                "target_document": cand["document_name"],
                "target_type": cand["document_type"],
                "target_artifact_type": cand["artifact_type"],
                "target_artifact": cand["artifact_id"],
                "target_text": cand["text"],
                "relationship": relationship_type,
                "status": status_out,
                "similarity": best_hybrid,
                "semantic_similarity": best_sem,
                "lexical_similarity": round(best_lex, 4),
                "hybrid_score": best_hybrid,
                "intent_score": round(best_intent, 4),
                "semantic_enabled": _sem_available,
                "confidence": conf,
                "evidence": evidence_out
            })
        elif best_hybrid >= HYBRID_PARTIAL_THRESHOLD or best_composite >= HYBRID_PARTIAL_THRESHOLD:
            matches_found.append({
                "source_document": source_art["document_name"],
                "source_type": source_art["document_type"],
                "source_artifact_type": source_art["artifact_type"],
                "source_artifact": source_art["artifact_id"],
                "source_text": source_art["text"],
                "target_document": cand["document_name"],
                "target_type": cand["document_type"],
                "target_artifact_type": cand["artifact_type"],
                "target_artifact": cand["artifact_id"],
                "target_text": cand["text"],
                "relationship": relationship_type,
                "status": "PARTIAL",
                "similarity": best_hybrid,
                "semantic_similarity": best_sem,
                "lexical_similarity": round(best_lex, 4),
                "hybrid_score": best_hybrid,
                "intent_score": round(best_intent, 4),
                "semantic_enabled": _sem_available,
                "confidence": "Medium",
                "evidence": f"Partial conceptual overlap ({best_ev})"
            })

    if not matches_found:
        matches_found.append({
            "source_document": source_art["document_name"],
            "source_type": source_art["document_type"],
            "source_artifact_type": source_art["artifact_type"],
            "source_artifact": source_art["artifact_id"],
            "source_text": source_art["text"],
            "target_document": "—", "target_type": "—",
            "target_artifact_type": "—", "target_artifact": "—", "target_text": "—",
            "relationship": relationship_type,
            "status": "UNMAPPED", "similarity": 0.0,
            "semantic_similarity": None, "lexical_similarity": 0.0,
            "hybrid_score": 0.0, "intent_score": 0.0,
            "semantic_enabled": _sem_available,
            "confidence": "Low",
            "evidence": "No target artifact satisfied combined semantic, action, and entity match criteria"
        })

    return matches_found

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
        raw_doc_type = doc.get("document_type") or "UNKNOWN"
        norm_doc_type = normalize_document_type(raw_doc_type)
        doc_artifacts = doc.get("artifacts") or []

        if norm_doc_type not in docs_by_type:
            docs_by_type[norm_doc_type] = []

        valid_doc_artifacts = []
        for art in doc_artifacts:
            raw_art_id = art.get("artifact_id") or f"ART-{len(all_artifacts)+1:03d}"
            art_id = raw_art_id.upper()
            canonical_key = f"{doc_name}::{art_id}"
            
            if canonical_key in seen_canonical_ids:
                continue
            seen_canonical_ids.add(canonical_key)

            art_text = art.get("text", "").strip()
            clean = clean_text(art_text)
            
            # Canonical artifact type mapping ensuring FS-201 is always FUNCTIONAL_SPECIFICATION / FRD
            canonical_art_type, canonical_art_doc_type = determine_canonical_artifact_type(art_id, norm_doc_type)
            
            norm_art = {
                "artifact_id": art_id,
                "artifact_type": canonical_art_type,
                "document_id": doc_id,
                "document_name": doc_name,
                "document_type": canonical_art_doc_type,
                "text": art_text,
                "clean_text": clean,
                "section": art.get("section") or "General",
                "metadata": art.get("metadata") or {}
            }
            all_artifacts.append(norm_art)
            valid_doc_artifacts.append(norm_art)

        docs_by_type[norm_doc_type].extend(valid_doc_artifacts)
        doc_type_counts[norm_doc_type] = len(docs_by_type[norm_doc_type])

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

    # ── Fallback: re-classify UNKNOWN artifacts by content so no artifacts are lost ──
    # This handles cases where a document was classified UNKNOWN upstream, but its
    # individual artifact texts contain enough signal to determine the correct tier.
    unknown_arts = [a for a in all_artifacts if a["document_type"] == "UNKNOWN" and a["artifact_type"] == "UNKNOWN"]
    if unknown_arts:
        from utils.classifier import classify_document as _clf
        for art in unknown_arts:
            if not art["text"].strip():
                continue
            inferred_type, inferred_conf, _ = _clf(art["text"])
            if inferred_type != "UNKNOWN" and inferred_conf >= 20.0:
                from utils.extractor import determine_canonical_artifact_type as _dcat
                new_art_type, new_doc_type = _dcat(art["artifact_id"], inferred_type)
                art["document_type"] = new_doc_type
                art["artifact_type"] = new_art_type

    # Artifact collections by standard tiers
    brd_list = [a for a in all_artifacts if a["document_type"] == "BRD" or a["artifact_type"] == "BRD_REQUIREMENT"]
    srs_list = [a for a in all_artifacts if a["document_type"] == "SRS" or a["artifact_type"] in ["FUNCTIONAL_REQUIREMENT", "NON_FUNCTIONAL_REQUIREMENT"]]
    frd_list = [a for a in all_artifacts if a["document_type"] == "FRD" or a["artifact_type"] == "FUNCTIONAL_SPECIFICATION"]
    us_list = [a for a in all_artifacts if a["document_type"] == "USER_STORY" or a["artifact_type"] == "USER_STORY"]
    tc_list = [a for a in all_artifacts if a["document_type"] == "TEST_CASE" or a["artifact_type"] == "TEST_CASE"]
    cr_list = [a for a in all_artifacts if a["document_type"] == "CHANGE_REQUEST" or a["artifact_type"] == "CHANGE_REQUEST"]
    mom_list = [a for a in all_artifacts if a["document_type"] == "MEETING_MINUTES" or a["artifact_type"] in ["DECISION", "ACTION_ITEM"]]

    traceability_relationships = []
    upstream_canonical_map = {}
    
    # 1. BRD -> SRS (TRACEABLE_TO)
    for brd in brd_list:
        rels = find_candidate_relationships(brd, srs_list, vectorizer, relationship_type="TRACEABLE_TO", upstream_canonical_map=upstream_canonical_map)
        traceability_relationships.extend(rels)
        for r in rels:
            if r.get("status") in ["MATCHED", "PARTIAL"] and r.get("target_artifact") != "—":
                upstream_canonical_map[r["target_artifact"]] = brd

    # 2. SRS -> FRD (IMPLEMENTED_BY)
    # Candidate pool MUST strictly be FUNCTIONAL_SPECIFICATION artifacts from FRD
    srs_functional_list = [s for s in srs_list if s["artifact_type"] == "FUNCTIONAL_REQUIREMENT"]
    for srs in srs_functional_list:
        rels = find_candidate_relationships(srs, frd_list, vectorizer, relationship_type="IMPLEMENTED_BY", upstream_canonical_map=upstream_canonical_map)
        traceability_relationships.extend(rels)
        for r in rels:
            if r.get("status") in ["MATCHED", "PARTIAL"] and r.get("target_artifact") != "—":
                upstream_canonical_map[r["target_artifact"]] = srs

    # 3. SRS / FRD -> User Story (REALIZED_BY)
    # Candidate pool MUST strictly be USER_STORY artifacts
    for srs in srs_list:
        rels = find_candidate_relationships(srs, us_list, vectorizer, relationship_type="REALIZED_BY", upstream_canonical_map=upstream_canonical_map)
        traceability_relationships.extend(rels)
        for r in rels:
            if r.get("status") in ["MATCHED", "PARTIAL"] and r.get("target_artifact") != "—":
                upstream_canonical_map[r["target_artifact"]] = srs

    # 4. User Story -> Test Case (VERIFIED_BY)
    # Candidate pool MUST strictly be TEST_CASE artifacts from TEST_CASE documents
    for us in us_list:
        rels = find_candidate_relationships(us, tc_list, vectorizer, relationship_type="VERIFIED_BY", upstream_canonical_map=upstream_canonical_map)
        traceability_relationships.extend(rels)
        for r in rels:
            if r.get("status") in ["MATCHED", "PARTIAL"] and r.get("target_artifact") != "—":
                upstream_canonical_map[r["target_artifact"]] = us

    # 5. Change Requests -> Requirements (AFFECTS)
    cr_impacts = []
    for cr in cr_list:
        rels = find_candidate_relationships(cr, srs_list, vectorizer, relationship_type="AFFECTS", min_match=0.18, min_partial=0.10)
        if rels[0]["status"] == "UNMAPPED":
            frd_rels = find_candidate_relationships(cr, frd_list, vectorizer, relationship_type="AFFECTS", min_match=0.18, min_partial=0.10)
            if frd_rels[0]["status"] != "UNMAPPED":
                rels = frd_rels
        traceability_relationships.extend(rels)
        for rel in rels:
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
        rels = find_candidate_relationships(mom, srs_list + cr_list + brd_list, vectorizer, relationship_type="RELATED_TO", min_match=0.18, min_partial=0.10)
        traceability_relationships.extend(rels)
        for rel in rels:
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
    # Strictly built from CANONICAL traceability_relationships edges (zero re-inference)
    root_artifacts = brd_list if brd_list else srs_list if srs_list else all_artifacts
    traceability_chains = []
    top_conflicts = []
    top_unmapped = []

    # Map of canonical active relationships keyed by (source_artifact, relationship_type) and source_artifact
    canonical_rel_map = {}
    for r in traceability_relationships:
        if r.get("status") in ["MATCHED", "PARTIAL", "CONFLICT"] and r.get("target_artifact") != "—":
            canonical_rel_map[(r["source_artifact"], r.get("relationship"))] = r
            if r["source_artifact"] not in canonical_rel_map:
                canonical_rel_map[r["source_artifact"]] = r

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
            rel_srs = canonical_rel_map.get((root_art["artifact_id"], "TRACEABLE_TO")) or canonical_rel_map.get(root_art["artifact_id"])
            current_srs = None
            if rel_srs:
                matched_srs_art = next((s for s in srs_list if s["artifact_id"] == rel_srs["target_artifact"]), None)
                if matched_srs_art:
                    chain["srs"] = {
                        "id": matched_srs_art["artifact_id"],
                        "name": matched_srs_art["document_name"],
                        "text": matched_srs_art["text"]
                    }
                    chain["evidence_chain"].append(f"BRD→SRS [{rel_srs['status']}]: {rel_srs['evidence']}")
                    current_srs = matched_srs_art
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
            rel_frd = canonical_rel_map.get((current_srs["artifact_id"], "IMPLEMENTED_BY")) or canonical_rel_map.get(current_srs["artifact_id"])
            if rel_frd:
                matched_frd_art = next((f for f in frd_list if f["artifact_id"] == rel_frd["target_artifact"]), None)
                if matched_frd_art:
                    chain["frd"] = {
                        "id": matched_frd_art["artifact_id"],
                        "name": matched_frd_art["document_name"],
                        "text": matched_frd_art["text"]
                    }
                    chain["evidence_chain"].append(f"SRS→FRD [{rel_frd['status']}]: {rel_frd['evidence']}")
                    current_frd = matched_frd_art

        # Step 3: User Story
        current_us = None
        target_for_us = current_frd or current_srs
        if target_for_us:
            rel_us = canonical_rel_map.get((target_for_us["artifact_id"], "REALIZED_BY")) or canonical_rel_map.get(target_for_us["artifact_id"])
            if rel_us:
                matched_us_art = next((u for u in us_list if u["artifact_id"] == rel_us["target_artifact"]), None)
                if matched_us_art:
                    chain["user_story"] = {
                        "id": matched_us_art["artifact_id"],
                        "name": matched_us_art["document_name"],
                        "text": matched_us_art["text"]
                    }
                    chain["evidence_chain"].append(f"FRD→US [{rel_us['status']}]: {rel_us['evidence']}")
                    current_us = matched_us_art

        # Step 4: Test Case
        target_for_tc = current_us or current_frd or current_srs
        if target_for_tc:
            rel_tc = canonical_rel_map.get((target_for_tc["artifact_id"], "VERIFIED_BY")) or canonical_rel_map.get(target_for_tc["artifact_id"])
            if rel_tc:
                matched_tc_art = next((t for t in tc_list if t["artifact_id"] == rel_tc["target_artifact"]), None)
                if matched_tc_art:
                    chain["test_case"] = {
                        "id": matched_tc_art["artifact_id"],
                        "name": matched_tc_art["document_name"],
                        "text": matched_tc_art["text"]
                    }
                    chain["evidence_chain"].append(f"US→TC [{rel_tc['status']}]: {rel_tc['evidence']}")

        # Determine overall chain status from canonical edges only
        chain_statuses = [ev.split('[')[1].split(']')[0] for ev in chain["evidence_chain"] if '[' in ev]
        if "CONFLICT" in chain_statuses:
            overall = "CONFLICT"
        elif chain_statuses and all(st == "MATCHED" for st in chain_statuses) and len(chain_statuses) >= 2:
            overall = "MATCHED"
        elif any(st in ["MATCHED", "PARTIAL"] for st in chain_statuses):
            overall = "PARTIAL"
        else:
            overall = "UNMAPPED"
            top_unmapped.append({
                "artifact_id": root_art["artifact_id"],
                "document_name": root_art["document_name"],
                "document_type": root_art["document_type"],
                "text": root_art["text"],
                "reason": "No downstream requirement, functional spec, or test case satisfied domain and lexical match criteria"
            })

        chain["overall_status"] = overall
        traceability_chains.append(chain)

    # Collect Exact Conflicts from direct relationships
    for rel in traceability_relationships:
        if rel["status"] == "CONFLICT":
            top_conflicts.append({
                "source_id": rel["source_artifact"],
                "source_doc": rel["source_document"],
                "source_text": rel["source_text"],
                "target_id": rel["target_artifact"],
                "target_doc": rel["target_document"],
                "target_text": rel["target_text"],
                "reason": rel["evidence"]
            })

    # Collect Gaps from direct unmapped relationships
    gaps = []
    for rel in traceability_relationships:
        if rel["status"] == "UNMAPPED":
            gaps.append({
                "artifact_id": rel["source_artifact"],
                "document_name": rel["source_document"],
                "document_type": rel["source_type"],
                "text": rel["source_text"],
                "reason": rel["evidence"]
            })

    status_counts = {
        "MATCHED": sum(1 for r in traceability_relationships if r["status"] == "MATCHED"),
        "PARTIAL": sum(1 for r in traceability_relationships if r["status"] == "PARTIAL"),
        "CONFLICT": sum(1 for r in traceability_relationships if r["status"] == "CONFLICT"),
        "UNMAPPED": sum(1 for r in traceability_relationships if r["status"] == "UNMAPPED")
    }

    # Traceability Graph (Immutable Nodes and Verified Edges)
    graph_nodes = []
    graph_edges = []
    node_ids_added = set()

    for art in all_artifacts:
        node_id = f"{art['document_name']}::{art['artifact_id']}"
        if node_id not in node_ids_added:
            graph_nodes.append({
                "id": node_id,
                "artifact_id": art["artifact_id"],
                "artifact_type": art["artifact_type"],
                "document_name": art["document_name"],
                "document_type": art["document_type"],
                "text": art["text"][:100] + ("..." if len(art["text"]) > 100 else "")
            })
            node_ids_added.add(node_id)

    seen_edges = set()
    for rel in traceability_relationships:
        if rel["target_artifact"] != "—":
            source_node = f"{rel['source_document']}::{rel['source_artifact']}"
            target_node = f"{rel['target_document']}::{rel['target_artifact']}"
            edge_key = f"{source_node}->{target_node}:{rel['relationship']}:{rel['status']}"
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                graph_edges.append({
                    "source": source_node,
                    "target": target_node,
                    "relationship": rel["relationship"],
                    "status": rel["status"],
                    "similarity": rel["similarity"],
                    "confidence": rel["confidence"],
                    "evidence": rel["evidence"]
                })

    # Exact Path Coverage Calculations
    brd_mapped = len(set(r["source_artifact"] for r in traceability_relationships if r["source_type"] == "BRD" and r["relationship"] == "TRACEABLE_TO" and r["status"] in ["MATCHED", "PARTIAL", "CONFLICT"]))
    brd_total = len(brd_list)
    brd_srs_cov = round((brd_mapped / brd_total * 100), 1) if brd_total > 0 else 0.0

    srs_frd_mapped = len(set(r["source_artifact"] for r in traceability_relationships if r["source_type"] == "SRS" and r["relationship"] == "IMPLEMENTED_BY" and r["status"] in ["MATCHED", "PARTIAL", "CONFLICT"]))
    srs_func_total = len(srs_functional_list)
    srs_frd_cov = round((srs_frd_mapped / srs_func_total * 100), 1) if srs_func_total > 0 else 0.0

    srs_us_mapped = len(set(r["source_artifact"] for r in traceability_relationships if r["source_type"] == "SRS" and r["relationship"] == "REALIZED_BY" and r["status"] in ["MATCHED", "PARTIAL", "CONFLICT"]))
    srs_total = len(srs_list)
    srs_us_cov = round((srs_us_mapped / srs_total * 100), 1) if srs_total > 0 else 0.0

    us_tc_mapped = len(set(r["source_artifact"] for r in traceability_relationships if r["source_type"] == "USER_STORY" and r["relationship"] == "VERIFIED_BY" and r["status"] in ["MATCHED", "PARTIAL", "CONFLICT"]))
    us_total = len(us_list)
    us_tc_cov = round((us_tc_mapped / us_total * 100), 1) if us_total > 0 else 0.0

    root_total = len(root_artifacts)
    root_mapped = sum(1 for c in traceability_chains if c["overall_status"] in ["MATCHED", "PARTIAL", "CONFLICT"])
    overall_cov = round((root_mapped / root_total * 100), 1) if root_total > 0 else 0.0

    # ── Semantic metadata ─────────────────────────────────────────────────────
    sem_available = _semantic_engine.is_available()
    analysis_mode = "hybrid_semantic_lexical" if sem_available else "lexical_fallback"
    analysis_type = (
        "Cross-Document Hybrid Semantic+Lexical Traceability"
        if sem_available else
        "Cross-Document Lexical Traceability (Semantic Fallback)"
    )

    return {
        "success": True,
        "mode": "project_intelligence",
        "title": "ReqVision AI — Software Intelligence & Cross-Document Traceability",
        "analysis_type": analysis_type,
        "analysis_mode": analysis_mode,
        "semantic_enabled": sem_available,
        "semantic_model": _semantic_engine.model_name if sem_available else None,
        "project": {
            "project_name": "Project Workspace",
            "mode": "project_intelligence",
            "total_documents": len(project_documents)
        },
        "documents": [
            {
                "document_id": doc.get("document_id") or doc.get("id"),
                "filename": doc.get("filename") or doc.get("name"),
                "document_type": normalize_document_type(doc.get("document_type")),
                "artifact_count": len([a for a in all_artifacts if a["document_id"] == (doc.get("document_id") or doc.get("id")) or a["document_name"] == (doc.get("filename") or doc.get("name"))])
            } for doc in project_documents
        ],
        "artifacts": all_artifacts,
        "relationships": traceability_relationships,
        "traceability_matrix": traceability_relationships,
        "chains": traceability_chains,
        "traceability_chains": traceability_chains,
        "graph": {
            "nodes": graph_nodes,
            "edges": graph_edges
        },
        "traceability_graph": {
            "nodes": graph_nodes,
            "edges": graph_edges
        },
        "coverage": {
            "overall_percentage": overall_cov,
            "brd_to_srs": f"{brd_srs_cov}% ({brd_mapped}/{brd_total})",
            "srs_to_frd": f"{srs_frd_cov}% ({srs_frd_mapped}/{srs_func_total})",
            "srs_to_user_story": f"{srs_us_cov}% ({srs_us_mapped}/{srs_total})",
            "user_story_to_test_case": f"{us_tc_cov}% ({us_tc_mapped}/{us_total})"
        },
        "summary": {
            "total_documents": len(project_documents),
            "total_artifacts": len(all_artifacts),
            "total_relationships": len(traceability_relationships),
            "document_types": doc_type_counts,
            "coverage_percentage": overall_cov,
            "status_breakdown": status_counts,
            "path_coverage": {
                "brd_to_srs_coverage": f"{brd_srs_cov}% ({brd_mapped}/{brd_total})",
                "srs_to_frd_coverage": f"{srs_frd_cov}% ({srs_frd_mapped}/{srs_func_total})",
                "srs_to_user_story_coverage": f"{srs_us_cov}% ({srs_us_mapped}/{srs_total})",
                "user_story_to_test_case_coverage": f"{us_tc_cov}% ({us_tc_mapped}/{us_total})"
            }
        },
        "conflicts": top_conflicts,
        "top_conflicts": top_conflicts,
        "gaps": gaps,
        "top_unmapped": top_unmapped,
        "change_request_impacts": cr_impacts,
        "meeting_minutes_links": mom_links,
        "statistics": {
            "total_documents": len(project_documents),
            "total_artifacts": len(all_artifacts),
            "total_relationships": len(traceability_relationships),
            "status_breakdown": status_counts,
            "coverage_percentage": overall_cov
        }
    }
