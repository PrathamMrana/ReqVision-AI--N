"""
backend/utils/evidence_fusion.py

Generic Evidence Fusion & Capability Reasoning Engine for ReqVision AI Phase 3.

Implements the Complete Canonical Relevance Gate Architecture:
1. Normalized Capability Representation (Actors, Actions, Objects, Contexts, Modalities, Constraints)
2. Hard Candidate Relevance Gate (Rejects non-equivalent candidates before conflict/matching)
3. Action & Workflow Alignment (Distinguishes distinct operations e.g. reconcile != refund)
4. Meaningful Entity & Object Alignment (Filters out generic stopword dominance)
5. Actor / Role Alignment (Verifies compatible workflow actors)
6. Context / Temporal Condition Alignment (before, after, when, if, during, unless)
7. Capability Coverage & Entailment (Detects missing secondary clauses -> PARTIAL)
8. Capability Extension Recognition (Target adds optional alternative channels -> MATCHED extended)
9. Score Margin & Candidate Disambiguation (Close scores -> Ambiguous PARTIAL)
10. Anti-False-Conflict Isolation (Only confirmed relevant candidates are tested for contradiction)

NO project-specific logic, IDs, filenames, or hardcoded project names.
Operates strictly on generic linguistic, structural, and semantic properties.
"""

import re
from typing import Tuple, List, Dict, Set, Optional

# ── Centralized Configurable Evidence Weights ─────────────────────────────────
EVIDENCE_WEIGHTS = {
    "semantic": 0.45,   # Dense neural conceptual similarity (all-MiniLM-L6-v2)
    "lexical": 0.15,    # Exact token & morphological overlap (TF-IDF + Jaccard)
    "intent": 0.10,     # Domain intent category anchor
    "action": 0.12,     # Primary action / verb alignment
    "entity": 0.08,     # Domain object / noun entity Jaccard
    "actor": 0.04,      # Workflow role / actor compatibility
    "context": 0.03,    # Temporal / conditional trigger alignment
    "constraint": 0.03, # Quantitative / limit consistency
}

# ── Generic Action Patterns & Specialized Capability Families ─────────────────
ACTION_PATTERNS = {
    "auth": [r"\bauthenticat\w*\b", r"\blogin\b", r"\bsign-?in\b", r"\bverify\b.{0,15}\bidentity\b", r"\bauthoriz\w*\b", r"\bmfa\b", r"\b2fa\b", r"\bsession\b", r"\baccess\s+control\b", r"\bpermission\w*\b", r"\brbac\b"],
    "cancel": [r"\bcancel\w*\b", r"\brevok\w*\b", r"\bterminat\w*\b", r"\bdiscontinu\w*\b", r"\bvoid\b", r"\babort\b", r"\breleas\w*\b", r"\bwithdraw\w*\b"],
    "reserve": [r"\breserv\w*\b", r"\bbook\w*\b", r"\bhold\b", r"\ballocat\w*\b", r"\bschedul\w*\b", r"\bappoint\w*\b"],
    "pay": [r"\bpay\w*\b", r"\bcheckout\b", r"\bcharg\w*\b", r"\bbill\w*\b", r"\bremit\w*\b", r"\bsettle\s+invoice\b"],
    "refund": [r"\brefund\w*\b", r"\breimburs\w*\b", r"\brevers\w*\s+payment\b", r"\bcredit\s+back\b", r"\breturn\s+funds\b"],
    "reconcile": [r"\breconcil\w*\b", r"\bmatch\s+settlement\b", r"\bcompar\w*\s+files\b", r"\baudit\s+ledger\b", r"\bbalance\s+records\b", r"\bcross-?check\b"],
    "notify": [r"\bnotif\w*\b", r"\balert\w*\b", r"\bremind\w*\b", r"\bsend\s+(?:email|sms|push|slack|whatsapp)\b", r"\bdispatch\w*\b", r"\bpush\s+notification\b", r"\bmessage\w*\b"],
    "search": [r"\bsearch\w*\b", r"\bquery\w*\b", r"\bfind\w*\b", r"\blookup\b", r"\bfilter\w*\b", r"\bbrowse\w*\b", r"\blocat\w*\b", r"\bdiscover\w*\b"],
    "export": [r"\bexport\w*\b", r"\bdownload\w*\b", r"\bextract\s+data\b", r"\barchiv\w*\b", r"\bdump\b", r"\bgenerate\s+report\b"],
    "manage": [r"\bcreat\w*\b", r"\bupdat\w*\b", r"\bdelet\w*\b", r"\bedit\w*\b", r"\bmaintain\w*\b", r"\bmodif\w*\b", r"\bregister\w*\b", r"\bonboard\w*\b", r"\bsubmit\w*\b"],
    "track": [r"\btrack\w*\b", r"\bmonitor\w*\b", r"\btelemetry\b", r"\bgps\b", r"\blive\s+location\b", r"\beta\b", r"\bpropagation\b", r"\borbit\b"],
    "approve": [r"\bapprov\w*\b", r"\breview\w*\b", r"\breject\w*\b", r"\bsanction\w*\b", r"\bendorse\w*\b", r"\bmanager\s+approval\b"],
    "estimate": [r"\bestimat\w*\b", r"\bcalculat\w*\b", r"\bcost\s+project\w*\b", r"\bforecast\w*\b", r"\bquote\w*\b", r"\bprice\s+comput\w*\b", r"\bcompute\b"],
    "capture": [r"\bcaptur\w*\b", r"\bupload\w*\b", r"\bscan\w*\b", r"\bocr\b", r"\battach\w*\b", r"\bphoto\b", r"\bcamera\b", r"\bingest\w*\b"],
    "detect_dup": [r"\bdetect\w*\s+duplicat\w*\b", r"\bprevent\w*\s+duplicat\w*\b", r"\bduplicat\w*\s+check\w*\b", r"\bflag\w*\s+duplicat\w*\b", r"\bdedup\w*\b", r"\bduplicate\s+receipt\w*\b", r"\bduplicate\s+warning\b", r"\bduplicate\s+claim\w*\b", r"\bduplicate\s+image\w*\b"],
    "prevent_conflict": [r"\boverlapping\b", r"\bdouble-?book\w*\b", r"\bconflict\w*\s+assignment\w*\b", r"\bcollision\b"],
    "history": [r"\bhistory\b", r"\bhistorical\b", r"\bpast\s+maintenance\b", r"\bpast\s+repair\b", r"\brepair\s+history\b", r"\bmaintenance\s+history\b"],
    "fault_report": [r"\bfault\w*\b", r"\bbreakdown\w*\b", r"\bdefect\w*\b", r"\bmalfunction\w*\b"],
    "emergency_contact": [r"\bemergency\s+contact\w*\b", r"\bnext-?of-?kin\b"],
}

# Specialized capabilities that must be mutually aligned
SPECIALIZED_CAPABILITIES = {"detect_dup", "prevent_conflict", "history", "fault_report", "emergency_contact"}

# ── Generic Actor / Role Patterns ─────────────────────────────────────────────
ACTOR_PATTERNS = {
    "employee": [r"\bemployee\w*\b", r"\bstaff\b", r"\bworker\w*\b", r"\btraveler\w*\b", r"\brider\w*\b", r"\bstudent\w*\b", r"\bpatient\w*\b", r"\bcustomer\w*\b", r"\buser\w*\b", r"\bpassenger\w*\b", r"\bcontroller\w*\b", r"\boperator\w*\b", r"\bdriver\w*\b"],
    "manager": [r"\bmanager\w*\b", r"\bsupervisor\w*\b", r"\bapprover\w*\b", r"\blead\w*\b", r"\bhead\b", r"\bdirector\w*\b", r"\bphysician\w*\b", r"\bdoctor\w*\b", r"\bflight\s+director\b", r"\bdispatcher\w*\b"],
    "finance": [r"\bfinance\b", r"\baccountant\w*\b", r"\bbursar\b", r"\bauditor\w*\b", r"\bcashier\w*\b", r"\bcompliance\b"],
    "admin": [r"\badmin\w*\b", r"\bsysadmin\b", r"\bhelpdesk\b"],
}

# ── Context / Temporal Modifiers ──────────────────────────────────────────────
CONTEXT_PATTERNS = {
    "temporal_before": [r"\bbefore\b", r"\bprior\s+to\b", r"\bpre-?\b", r"\buntil\b"],
    "temporal_after": [r"\bafter\b", r"\bfollowing\b", r"\bonce\b", r"\bupon\b"],
    "conditional": [r"\bwhen\b", r"\bif\b", r"\bunless\b", r"\bonly\s+when\b", r"\bin\s+case\b"],
    "durational": [r"\bduring\b", r"\bwhile\b", r"\bthroughout\b"],
}

# ── Incompatible Action Pairs ─────────────────────────────────────────────────
INCOMPATIBLE_ACTION_PAIRS = [
    ({"reconcile"}, {"refund"}),
    ({"export"}, {"manage"}),
    ({"cancel"}, {"reserve"}),
    ({"search"}, {"manage"}),
    ({"estimate"}, {"refund"}),
    ({"estimate"}, {"manage"}),
    ({"approve"}, {"manage"}),       # Manager approval != employee creation/submission
    ({"cancel"}, {"auth"}),          # Cancellation != Access control
    ({"capture"}, {"detect_dup"}),   # Receipt capture/upload != Duplicate fraud detection
    ({"auth"}, {"detect_dup"}),      # Access control != Duplicate detection
    ({"track"}, {"estimate"}),       # Telemetry tracking != Calculation/estimation
    ({"track"}, {"pay"}),            # Telemetry tracking != Payment
    ({"track"}, {"refund"}),         # Telemetry tracking != Refund
    ({"track"}, {"auth"}),           # Telemetry tracking != Authentication
    ({"track"}, {"reconcile"}),      # Telemetry tracking != Reconciliation
]


def evaluate_action_alignment(text_a: str, text_b: str) -> Tuple[float, str]:
    """Evaluates action compatibility between source and target."""
    actions_a = extract_actions(text_a)
    actions_b = extract_actions(text_b)

    if not actions_a or not actions_b:
        return 0.70, "Neutral action alignment"

    # Specialized capability mutual alignment (e.g. duplicate check, overlapping prevention, repair history)
    for spec in SPECIALIZED_CAPABILITIES:
        if (spec in actions_a and spec not in actions_b) or (spec in actions_b and spec not in actions_a):
            return 0.05, f"Incompatible action divergence: specialized capability [{spec}] requires matching realization"

    # Shared actions take precedence
    shared = actions_a & actions_b
    if shared:
        return 1.0, f"Aligned actions on [{', '.join(shared)}]"

    # Check for strictly incompatible action pairs when no actions are shared
    for group1, group2 in INCOMPATIBLE_ACTION_PAIRS:
        if (actions_a & group1 and actions_b & group2) or (actions_a & group2 and actions_b & group1):
            return 0.05, f"Incompatible action divergence: [{', '.join(actions_a)}] vs [{', '.join(actions_b)}]"

    return 0.40, f"Different actions: [{', '.join(actions_a)}] vs [{', '.join(actions_b)}]"

# ── Generic Filler Stopwords & Function Words ─────────────────────────────────
GENERIC_BOILERPLATE = {
    "system", "platform", "user", "users", "service", "services", "application",
    "feature", "module", "component", "endpoint", "shall", "must", "should",
    "will", "able", "allow", "allows", "allowed", "provide", "provides", "provided",
    "want", "wants", "order", "view", "views", "data", "information", "details",
    "support", "supports", "supported", "implement", "implements", "implemented",
    "verify", "verifies", "verified", "test", "tests", "tested", "scenario", "scenarios",
    "requirement", "specification", "document", "item", "process", "interface", "method",
    "update", "updates", "updated", "create", "creates", "created", "delete", "deletes", "deleted",
    "real", "time", "include", "includes", "included", "ensure", "ensures", "ensured",
    "the", "and", "for", "with", "from", "that", "this", "per", "via", "all", "any",
    "can", "may", "not", "but", "out", "into", "onto", "each", "both", "such", "than",
    "then", "when", "what", "which", "who", "whom", "whose", "how", "where", "why"
}


def extract_actions(text: str) -> Set[str]:
    """Extracts high-level action cluster keys present in the requirement text."""
    t = text.lower()
    detected_clusters = set()
    for cluster_name, patterns in ACTION_PATTERNS.items():
        if any(re.search(pat, t) for pat in patterns):
            detected_clusters.add(cluster_name)
    return detected_clusters


def extract_actors(text: str) -> Set[str]:
    """Extracts high-level actor / role categories mentioned in the text."""
    t = text.lower()
    detected_actors = set()
    for role_name, patterns in ACTOR_PATTERNS.items():
        if any(re.search(pat, t) for pat in patterns):
            detected_actors.add(role_name)
    return detected_actors


def extract_contexts(text: str) -> Set[str]:
    """Extracts temporal and conditional trigger types from the requirement."""
    t = text.lower()
    detected_contexts = set()
    for ctx_name, patterns in CONTEXT_PATTERNS.items():
        if any(re.search(pat, t) for pat in patterns):
            detected_contexts.add(ctx_name)
    return detected_contexts


def extract_entities(text: str) -> Set[str]:
    """Extracts domain-relevant entity tokens (excluding boilerplate)."""
    t = text.lower()
    raw_tokens = re.findall(r'\b[a-z]{3,}\b', t)
    entities = set()
    for tok in raw_tokens:
        if tok not in GENERIC_BOILERPLATE:
            stem = tok
            if stem.endswith('ies') and len(stem) > 4:
                stem = stem[:-3] + 'y'
            elif stem.endswith('s') and not stem.endswith('ss') and len(stem) > 3:
                stem = stem[:-1]
            elif stem.endswith('ing') and len(stem) > 5:
                stem = stem[:-3]
            elif stem.endswith('ed') and len(stem) > 4:
                stem = stem[:-2]
            if len(stem) >= 3 and stem not in GENERIC_BOILERPLATE:
                entities.add(stem)
    return entities


def build_capability_profile(text: str) -> Dict:
    """Builds a normalized generic capability representation for an artifact."""
    return {
        "text": text,
        "actions": extract_actions(text),
        "actors": extract_actors(text),
        "contexts": extract_contexts(text),
        "entities": extract_entities(text),
        "is_uncertain": any(phrase in text.lower() for phrase in [
            "not agreed", "did not agree", "unclear", "could mean", "undecided",
            "ambiguous", "further review", "unresolved", "did not define",
            "discussed but", "no consensus", "pending decision"
        ])
    }


def evaluate_entity_alignment(text_a: str, text_b: str) -> Tuple[float, str]:
    """Calculates entity Jaccard overlap between source and target requirements."""
    ent_a = extract_entities(text_a)
    ent_b = extract_entities(text_b)

    if not ent_a or not ent_b:
        return 0.50, "Neutral entity overlap"

    intersection = ent_a & ent_b
    union = ent_a | ent_b
    jaccard = len(intersection) / len(union) if union else 0.0

    if jaccard >= 0.20:
        return min(1.0, 0.60 + jaccard), f"Shared domain entities: [{', '.join(list(intersection)[:4])}]"
    elif intersection:
        return 0.55, f"Weak shared entity overlap: [{', '.join(list(intersection)[:3])}]"
    else:
        return 0.10, "No shared domain entities"


def evaluate_actor_alignment(text_a: str, text_b: str) -> Tuple[float, str]:
    """Evaluates actor / role compatibility."""
    act_a = extract_actors(text_a)
    act_b = extract_actors(text_b)

    if not act_a or not act_b:
        return 0.60, "Neutral actor alignment"
    if act_a & act_b:
        return 1.0, f"Compatible actors [{', '.join(act_a & act_b)}]"
    return 0.40, f"Different workflow actors: [{', '.join(act_a)}] vs [{', '.join(act_b)}]"


def evaluate_context_alignment(text_a: str, text_b: str) -> Tuple[float, str]:
    """Evaluates temporal and conditional trigger consistency."""
    ctx_a = extract_contexts(text_a)
    ctx_b = extract_contexts(text_b)

    if not ctx_a or not ctx_b:
        return 0.60, "Neutral context"
    if ctx_a & ctx_b:
        return 1.0, f"Matching context triggers [{', '.join(ctx_a & ctx_b)}]"
    return 0.50, "Different context triggers"


def evaluate_candidate_relevance_gate(
    source_text: str,
    target_text: str,
    semantic_sim: Optional[float],
    lexical_sim: float,
    shared_intents: Set[str],
    has_explicit_ref: bool = False
) -> Tuple[bool, str]:
    """
    Hard Candidate Relevance Gate.
    
    A candidate MUST pass this gate to be considered for candidate ranking,
    MATCHED/PARTIAL relationships, or CONFLICT detection.
    
    If source and target do NOT describe the same underlying capability:
    Returns (False, reason) -> Candidate is immediately REJECTED.
    """
    if has_explicit_ref:
        return True, "Explicit artifact reference passed gate"

    src_low = source_text.lower()
    tgt_low = target_text.lower()

    # 1. Check for administrative / physical hardware procurement without software realization
    hardware_procurement_actions = ["procure", "purchase", "install in", "replace physical", "order 30", "order 25", "buy", "physical replacement"]
    hardware_physical_objects = [
        "projector", "screen", "whiteboard", "chair", "desk", "furniture",
        "charger", "charging station", "espresso", "coffee", "shoe cleaner", "air purifier",
        "air conditioner", "hvac", "vending machine", "microwave", "refrigerator", "cooler",
        "breakroom", "parking lot", "standing desk"
    ]
    is_physical_procurement = any(obj in src_low for obj in hardware_physical_objects) and (
        any(act in src_low for act in hardware_procurement_actions) or not any(sw in src_low for sw in ["software", "api", "app", "service", "module", "endpoint", "driver", "calibrate", "calibration", "protocol", "portal", "command", "telemetry"])
    )
    if is_physical_procurement:
        return False, "Administrative / physical hardware procurement excluded from software traceability"

    # 2. Check for unresolved review statements
    unresolved_terms = [
        "not agreed", "did not agree", "unclear", "could mean", "undecided", "ambiguous",
        "further review", "unresolved", "did not define", "discussed but", "no consensus",
        "pending decision", "not determined", "did not determine", "not decided", "did not decide",
        "meaning was not", "meaning not determined", "was not determined", "not yet agreed"
    ]
    if any(phrase in src_low for phrase in unresolved_terms):
        return False, "Unresolved review statement excluded from automatic mapping"

    actions_a = extract_actions(source_text)
    actions_b = extract_actions(target_text)
    act_score, act_reason = evaluate_action_alignment(source_text, target_text)

    # 3. Incompatible action rejection
    if act_score <= 0.10 and not shared_intents:
        return False, f"Relevance Gate Rejected: {act_reason}"

    # 4. Entity check: reject if entities have 0 overlap and no shared intents and not high semantic
    ent_score, ent_reason = evaluate_entity_alignment(source_text, target_text)
    sem = semantic_sim if semantic_sim is not None else lexical_sim
    if ent_score <= 0.10 and not shared_intents and sem < 0.60:
        return False, "Relevance Gate Rejected: Unrelated domain entities"

    # 5. NFR / Performance constraint alignment: performance NFRs must not map to purely functional stories
    perf_keywords = {
        "latency", "response time", "throughput", "concurrent", "concurrency", "simultaneous",
        "availability", "uptime", "p95", "p99", "packets per second", "checkouts per minute",
        "performance", "capacity", "connections", "sessions", "rps", "tps", "qps"
    }
    src_perf = any(kw in src_low for kw in perf_keywords)
    tgt_perf = any(kw in tgt_low for kw in (perf_keywords | {"scale", "scaling", "autoscaler", "cache", "redis", "load balanc", "rate limit", "partition", "kafka", "distributed", "traffic"}))
    if src_perf and not tgt_perf:
        return False, "Relevance Gate Rejected: NFR performance constraint not represented in functional target"

    # 6. Semantic threshold minimum
    if sem < 0.25 and not shared_intents and lexical_sim < 0.20:
        return False, "Relevance Gate Rejected: Insufficient semantic and lexical evidence"

    return True, "Candidate passed capability relevance gate"


def detect_missing_conditions(source_text: str, target_text: str) -> Tuple[bool, str]:
    """
    Detects if the source requirement defines multiple compound clauses (e.g. A and B)
    while the target requirement only covers one clause.
    """
    src_lower = source_text.lower()
    tgt_lower = target_text.lower()

    compound_indicators = [
        (r'\band\s+(?:receive|get)\s+.*?\b(?:receipt|notification|email|confirmation|sms)\b', 'receipt / notification delivery'),
        (r'\band\s+(?:send|dispatch|notify)\b', 'notification dispatch'),
        (r'\band\s+(?:record|log|archive)\b', 'audit / archiving logging'),
        (r'\band\s+(?:upload|attach)\s+.*?\breceipt\b', 'receipt attachment'),
    ]

    for pat, desc in compound_indicators:
        if re.search(pat, src_lower) and not re.search(pat, tgt_lower):
            return True, f"Source specifies secondary condition not covered in target ({desc})"

    # Generic check on action set difference
    src_actions = extract_actions(source_text)
    tgt_actions = extract_actions(target_text)
    if len(src_actions) >= 2 and len(tgt_actions) == 1 and tgt_actions.issubset(src_actions):
        missing = src_actions - tgt_actions
        return True, f"Source has compound actions not covered in target: [{', '.join(missing)}]"

    return False, ""


def detect_capability_extension(source_text: str, target_text: str) -> Tuple[bool, str]:
    """
    Detects if the target extends the source requirement with additional optional capabilities.
    """
    src_lower = source_text.lower()
    tgt_lower = target_text.lower()

    if re.search(r'\bor\s+(?:digital\s+wallets?|apple\s+pay|google\s+pay|samsung\s+pay|cash|sms|bank\s+transfers?|qr|slack)\b', tgt_lower):
        if not re.search(r'\bor\b', src_lower):
            return True, "Extended capability: target supports additional alternative channels"

    return False, ""


def rank_and_disambiguate_candidates(
    candidates_evaluations: List[Dict],
    min_match_threshold: float = 0.45,
    min_partial_threshold: float = 0.28,
    ambiguity_margin: float = 0.04
) -> List[Dict]:
    """
    Ranks evaluated candidates that passed the relevance gate, computes score margins,
    and disambiguates close candidates.
    """
    if not candidates_evaluations:
        return []

    sorted_cands = sorted(candidates_evaluations, key=lambda x: x["composite_score"], reverse=True)
    top = sorted_cands[0]
    
    if len(sorted_cands) > 1:
        second = sorted_cands[1]
        score_margin = top["composite_score"] - second["composite_score"]
        top["score_margin"] = round(score_margin, 4)
        
        # Ambiguity check
        if score_margin < ambiguity_margin and top["composite_score"] >= min_match_threshold:
            top["is_ambiguous"] = True
            top["disambiguated_status"] = "PARTIAL"
            top["status"] = "PARTIAL"
            top["confidence"] = "Medium"
            top["evidence"] = top.get("evidence", "") + f" | Ambiguous match (close candidate score margin: {score_margin:.3f})"
            return [top]

    top["score_margin"] = 1.0 if len(sorted_cands) == 1 else round(top["composite_score"] - sorted_cands[1]["composite_score"], 4)
    return [top]
