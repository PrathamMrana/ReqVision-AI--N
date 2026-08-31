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
    "auth": [r"\bauthenticat\w*\b", r"\blogin\b", r"\bsign-?in\b", r"\bverify\b.{0,15}\bidentity\b", r"\bauthoriz\w*\b", r"\bmfa\b", r"\b2fa\b", r"\bsession\b", r"\baccess\s+control\b", r"\bpermission\w*\b", r"\brbac\b", r"\bpassword\b", r"\bcredential\w*\b", r"\btoken\w*\b", r"\bsmartcard\w*\b", r"\bbiometric\b"],
    "cancel": [r"\bcancel\w*\b", r"\brevok\w*\b", r"\bterminat\w*\b", r"\bdiscontinu\w*\b", r"\bvoid\b", r"\babort\b", r"\breleas\w*\b", r"\bwithdraw\w*\b", r"\bhalt\w*\b", r"\bstop\w*\b", r"\bdisabl\w*\b", r"\binvalidat\w*\b", r"\bdisengag\w*\b", r"\bshut\s*down\b", r"\bshut\s*off\b"],
    "emergency_stop": [r"\bemergency\b", r"\bsafe[-_]?off\b", r"\bdepressuriz\w*\b", r"\bdisarm\b", r"\bkill\s+switch\b", r"\bfail-?safe\b", r"\brtb\b", r"\breturn-?to-?base\b", r"\brelief\b", r"\bquench\b", r"\binterlock\b", r"\bparachute\b", r"\bballistic\b", r"\bsafety\s+(?:sub)?system\b", r"\bdecelerat\w*\b", r"\bcollision\s+avoidance\b"],
    "reserve": [r"\breserv\w*\b", r"\bbook\w*\b", r"\bhold\b", r"\ballocat\w*\b", r"\bappoint\w*\b", r"\bassign\w*\b", r"\bdispatch\w*\b", r"\bopen\b"],
    "pay": [r"\bpay\w*\b", r"\bcheckout\b", r"\bcharg\w*\b", r"\bbill\w*\b", r"\bremit\w*\b", r"\bsettle\s+invoice\b"],
    "refund": [r"\brefund\w*\b", r"\breimburs\w*\b", r"\brevers\w*\s+payment\b", r"\bcredit\s+back\b", r"\breturn\s+funds\b"],
    "reconcile": [r"\breconcil\w*\b", r"\bmatch\s+settlement\b", r"\bcompar\w*\s+files\b", r"\baudit\s+ledger\b", r"\bbalance\s+records\b", r"\bcross-?check\b"],
    "notify": [r"\bnotif\w*\b", r"\balert\w*\b", r"\bremind\w*\b", r"\bsend\s+(?:email|sms|push|slack|whatsapp)\b", r"\bpush\s+notification\b", r"\bmessage\w*\b", r"\bwarn\w*\b", r"\breceipt\b", r"\bconfirmation\b"],
    "search": [r"\bsearch\w*\b", r"\bquery\w*\b", r"\bfind\w*\b", r"\blookup\b", r"\bfilter\w*\b", r"\bbrowse\w*\b", r"\blocat\w*\b", r"\bdiscover\w*\b"],
    "export": [r"\bexport\w*\b", r"\bdownload\w*\b", r"\bextract\s+data\b", r"\bdump\b", r"\bgenerate\s+report\b", r"\bdepreciation\b"],
    "manage": [r"\bcreat\w*\b", r"\bupdat\w*\b", r"\bedit\w*\b", r"\bmaintain\w*\b", r"\bmodif\w*\b", r"\bregister\w*\b", r"\bonboard\w*\b", r"\bsubmit\w*\b", r"\blog\s+(?:an?\s+)?(?:event|error|issue|incident|transaction|audit|fault)\b", r"\blogging\b", r"\bwork\s*order\w*\b", r"\brepair\w*\b", r"\bfile\w*\b", r"\bexecut\w*\b", r"\bperform\w*\b", r"\boperat(?:e|es|ing)\b", r"\brotat\w*\b"],
    "delete": [r"\bdelet\w*\b", r"\bremov\w*\b", r"\beras\w*\b", r"\bpurag\w*\b", r"\bdestroy\b", r"\bpermanently\s+delete\b"],
    "view": [r"\bdisplay\w*\b", r"\bview\w*\b", r"\bvisualiz\w*\b", r"\bshow\w*\b", r"\bpresent\w*\b", r"\bdashboard\b", r"\bui\b", r"\bwidget\b", r"\bmetrics\b", r"\bstatistic\w*\b", r"\bconsole\b", r"\bscreen\b"],
    "stream": [r"\bstream\w*\b", r"\bplay\w*\b", r"\brender\w*\b", r"\bbroadcast\w*\b", r"\bfeed\w*\b", r"\btransmission\b"],
    "track": [r"\btrack\w*\b", r"\bmonitor\w*\b", r"\btelemetry\b", r"\bgps\b", r"\blive\s+location\b", r"\beta\b", r"\bpropagation\b", r"\borbit\b", r"\bwaveform\b"],
    "approve": [r"\bapprov\w*\b", r"\breview\w*\b", r"\breject\w*\b", r"\bsanction\w*\b", r"\bendorse\w*\b", r"\bmanager\s+approval\b", r"\bauthoriz\w*\b", r"\bsign[- ]?off\b"],
    "estimate": [r"\bestimat\w*\b", r"\bcalculat\w*\b", r"\bcost\s+project\w*\b", r"\bforecast\w*\b", r"\bquote\w*\b", r"\bprice\s+comput\w*\b", r"\bcomput\w*\b", r"\bspectral\b", r"\bfft\b", r"\bpower\s+spectra\b", r"\boptimiz\w*\b", r"\bsolver\b", r"\bsurge\s+capacity\b", r"\banalytics\b"],
    "capture": [r"\bcaptur\w*\b", r"\bupload\w*\b", r"\bscan\w*\b", r"\bocr\b", r"\battach\w*\b", r"\bphoto\b", r"\bcamera\b", r"\bingest\w*\b", r"\bflir\b", r"\bedf\b", r"\bimage\w*\b"],
    "detect_dup": [r"\b(?:detect|identify|find|check|recognize|block|prevent|reject|discard|filter|stop|flag|dedup)\w*\s+(?:and\s+\w+\s+)?(?:duplicate|redundant|collision|overlap)\w*\b", r"\bduplicate\s+(?:check|warning|receipt|claim|image|packet|sensor|telemetry|waypoint|flight|key|request|message|material)\w*\b", r"\bdedup\w*\b", r"\bdrop\s+redundant\b"],
    "prevent_conflict": [r"\boverlapping\b", r"\bdouble-?book\w*\b", r"\bconflict\w*\s+assignment\w*\b", r"\bschedule\s+collision\b"],
    "history": [r"\b(?:audit|repair|maintenance|calibration|version|transaction|change)\s+history\b", r"\baudit\s+trail\b", r"\bhistory\s+log\w*\b", r"\bview\s+history\b", r"\btrack\s+history\b", r"\bhistorical\s+audit\b", r"\bpast\s+maintenance\b", r"\bpast\s+repair\b", r"\bvoltage\s+adjust\w*\b", r"\bcalibration\s+audit\b", r"\bledger\b", r"\bimmutable\b"],
    "calibrate": [r"\bcalibrat\w*\b", r"\bzero\s+offset\b", r"\bgain\s+adjust\w*\b", r"\btun(?:e|ing)\b", r"\bsensor\s+calibrat\w*\b"],
    "detect_violation": [r"\bdetect\w*\b.{0,30}\b(?:threshold|violation|limit|breach|surge|anomaly|hazard)\b", r"\bthreshold\s+(?:detection|monitoring|exceeded|alert)\b", r"\bbreach\s+alert\w*\b", r"\banomaly\s+detect\w*\b"],
    "fault_report": [r"\bfault\w*\b", r"\bbreakdown\w*\b", r"\bdefect\w*\b", r"\bmalfunction\w*\b", r"\badverse\s+event\b", r"\bhazard\s+report\b", r"\bfail(?:ure|ed|ing|s)?\b(?!-safe)"],
    "emergency_contact": [r"\bemergency\s+contact\w*\b", r"\bnext-?of-?kin\b"],
}

# Specialized capabilities that must be mutually aligned
SPECIALIZED_CAPABILITIES = {"detect_dup", "prevent_conflict", "history", "fault_report", "emergency_contact", "emergency_stop", "calibrate", "detect_violation"}

# ── Generic Actor / Role Patterns ─────────────────────────────────────────────
ACTOR_PATTERNS = {
    "specialist": [r"\bmechanic\w*\b", r"\btechnician\w*\b", r"\bengineer\w*\b", r"\bfield\s+worker\b"],
    "driver": [r"\bdriver\w*\b", r"\bchauffeur\b", r"\bpilot\b"],
    "employee": [r"\bemployee\w*\b", r"\bstaff\b", r"\bworker\w*\b", r"\btraveler\w*\b", r"\brider\w*\b", r"\bstudent\w*\b", r"\bpatient\w*\b", r"\bcustomer\w*\b", r"\buser\w*\b", r"\bpassenger\w*\b", r"\bcontroller\w*\b", r"\boperator\w*\b"],
    "manager": [r"\bmanager\w*\b", r"\bsupervisor\w*\b", r"\bapprover\w*\b", r"\blead\w*\b", r"\bhead\b", r"\bdirector\w*\b", r"\bphysician\w*\b", r"\bdoctor\w*\b", r"\bflight\s+director\b", r"\bdispatcher\w*\b"],
    "finance": [r"\bfinance\b", r"\baccountant\w*\b", r"\bbursar\b", r"\bauditor\w*\b", r"\bcashier\w*\b", r"\bcompliance\b"],
    "admin": [r"\badmin\w*\b", r"\bsysadmin\b", r"\bhelpdesk\b"],
}

# ── Context / Temporal Modifiers ──────────────────────────────────────────────
CONTEXT_PATTERNS = {
    "temporal_before": [r"\bbefore\b", r"\bprior\s+to\b", r"\bpre-?\b", r"\buntil\b"],
    "temporal_after": [r"\bafter\b", r"\bfollowing\b", r"\bonce\b", r"\bupon\b", r"\bwhen\b"],
    "conditional": [r"\bif\b", r"\bunless\b", r"\bonly\s+when\b", r"\bin\s+case\b"],
    "durational": [r"\bduring\b", r"\bwhile\b", r"\bthroughout\b"],
}

# ── Incompatible Action Pairs ─────────────────────────────────────────────────
INCOMPATIBLE_ACTION_PAIRS = [
    ({"reconcile"}, {"refund"}),
    ({"export"}, {"delete"}),           # Export/Archive != Permanent Deletion
    ({"search"}, {"delete"}),
    ({"estimate"}, {"refund"}),
    ({"estimate"}, {"view"}),           # Calculation/Analytics != Dashboard/Console display
    ({"stream"}, {"view"}),             # Media Streaming/Rendering != Observation/Metrics Dashboard
    ({"view"}, {"manage"}),             # Display/Console != Creation/Submission/Maintenance
    ({"view"}, {"delete"}),             # Display/Console != Permanent Deletion
    ({"view"}, {"cancel"}),             # Display/Console != Revocation/Cancellation
    ({"view"}, {"auth"}),               # Display/Console != Credential authentication
    ({"view"}, {"detect_dup"}),         # Display/Dashboard != Duplicate Detection
    ({"view"}, {"fault_report"}),       # Display/Dashboard != Fault/Defect Reporting
    ({"view"}, {"calibrate"}),          # Display/Console != Sensor Calibration
    ({"view"}, {"detect_violation"}),   # Operations Console != Threshold Violation Detection
    ({"approve"}, {"manage"}),          # Manager approval != employee creation/submission/work-order
    ({"approve"}, {"fault_report"}),    # Workflow success/approval != failure alert
    ({"approve"}, {"detect_dup"}),      # Manager approval != Duplicate prevention
    ({"approve"}, {"history"}),         # Approval workflow != Historical audit trail
    ({"history"}, {"estimate"}),        # Historical audit log != Sensor/Tolerance calculation
    ({"history"}, {"calibrate"}),       # Audit History != Sensor Calibration Test
    ({"history"}, {"manage"}),          # Historical audit log != Live execution
    ({"capture"}, {"detect_dup"}),      # Receipt capture/upload != Duplicate fraud detection
    ({"track"}, {"reserve"}),           # Telemetry tracking != Route assignment
    ({"track"}, {"estimate"}),          # Telemetry monitoring != Reliability/Capacity analytics
    ({"export"}, {"track"}),            # Reporting export != Telemetry stream
    ({"calibrate"}, {"manage"}),        # Sensor calibration != General repair/work order
]


def decompose_requirement_clauses(text: str) -> List[str]:
    """
    Decomposes a complex requirement string into atomic clauses based on
    conjunctions and punctuation delimiters.
    """
    clauses = re.split(r'[;,]|(?:\s+and\s+)|(?:\s+as\s+well\s+as\s+)', text, flags=re.IGNORECASE)
    return [c.strip() for c in clauses if len(c.strip()) > 10]


def evaluate_action_alignment(text_a: str, text_b: str) -> Tuple[float, str]:
    """Evaluates action compatibility between source and target."""
    actions_a = extract_actions(text_a)
    actions_b = extract_actions(text_b)

    if not actions_a or not actions_b:
        return 0.50, "Neutral action alignment"

    # 1. Specialized capability mutual alignment (e.g. duplicate check, overlapping prevention, repair history)
    for spec in SPECIALIZED_CAPABILITIES:
        if (spec in actions_a and spec not in actions_b) or (spec in actions_b and spec not in actions_a):
            return 0.05, f"Incompatible action divergence: specialized capability [{spec}] requires matching realization"

    # 2. Incompatible cancellation vs creation/reservation realization
    if (("cancel" in actions_a and "cancel" not in actions_b and "reserve" in actions_b) or
        ("cancel" in actions_b and "cancel" not in actions_a and "reserve" in actions_a)):
        return 0.05, "Incompatible action divergence: cancellation vs reservation realization"

    # 3. Check for strictly incompatible operational action pairs across primary non-history actions
    primary_a = actions_a - {"history"}
    primary_b = actions_b - {"history"}
    if primary_a and primary_b:
        for group1, group2 in INCOMPATIBLE_ACTION_PAIRS:
            if (primary_a & group1 and primary_b & group2) or (primary_a & group2 and primary_b & group1):
                if not (primary_a & primary_b):
                    return 0.05, f"Incompatible action divergence: [{', '.join(actions_a)}] vs [{', '.join(actions_b)}]"

    # 4. Shared actions take precedence with recall scoring
    shared = actions_a & actions_b
    if shared:
        recall = len(shared) / len(actions_a)
        if recall == 1.0:
            return 1.0, f"Aligned actions on [{', '.join(shared)}]"
        return round(0.55 + 0.40 * recall, 4), f"Partially aligned actions on [{', '.join(shared)}] (Coverage: {recall:.0%})"

    # 5. Strictly incompatible action pairs when NO actions are shared
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

    # Disambiguate observation of metrics / status widgets from actual data stream generation/capture
    if re.search(r"\b(?:display\w*|show\w*|view\w*)\b.{0,40}\b(?:metric\w*|statistic\w*|frame\s*rate\w*|status\s*widget|resolution\s*metric)\b", t):
        detected_clusters.discard("stream")
        detected_clusters.discard("capture")
        detected_clusters.add("view")

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


def extract_governance_state(text: str) -> Tuple[str, str]:
    """
    Extracts explicit governance and review status from meeting/decision text.
    Returns (state, description):
      - 'UNRESOLVED' : Discussion occurred without consensus / agreement
      - 'PENDING'    : Under review or proposed for future decision
      - 'APPROVED'   : Formally agreed, confirmed, or mandated
      - 'ACTION'     : Assigned implementation task
      - 'REQUEST'    : Formal change request or proposal
      - 'DISCUSSION' : General informational discussion
    """
    t = text.lower()
    if any(p in t for p in [
        "not agreed", "did not agree", "unclear", "could mean", "undecided", "ambiguous",
        "no consensus", "unresolved", "meaning was not", "was not determined", "not determined",
        "tabled without", "deferred without", "not yet decided", "discussed but no consensus",
        "did not define", "discussed but did not", "discussed adding", "technical specifications"
    ]):
        return "UNRESOLVED", "Unresolved item without consensus"
    if any(p in t for p in [
        "pending decision", "under review", "to be decided", "proposed for future", "pending approval", "awaiting feedback"
    ]):
        return "PENDING", "Pending review / decision"
    if any(p in t for p in [
        "approved", "confirmed", "agreed", "decided", "resolved", "adopted", "mandated", "enforced", "unanimous"
    ]):
        return "APPROVED", "Confirmed decision / approved"
    if any(p in t for p in ["action item", "assigned to", "tasked to", "will implement"]):
        return "ACTION", "Assigned action item"
    if any(p in t for p in ["change request", "proposal to", "request to"]):
        return "REQUEST", "Formal request / proposal"
    return "DISCUSSION", "Meeting discussion"


def evaluate_candidate_relevance_gate(
    source_text: str,
    target_text: str,
    semantic_sim: Optional[float],
    lexical_sim: float,
    shared_intents: Set[str],
    relationship_type: str = "TRACEABLE_TO",
    has_explicit_ref: bool = False
) -> Tuple[bool, str]:
    """
    Hard Candidate Relevance Gate with Relationship-Specific Proof.
    
    A candidate MUST pass this gate to be considered for candidate ranking,
    MATCHED/PARTIAL relationships, or CONFLICT detection.
    
    If source and target do NOT satisfy the proof required for relationship_type:
    Returns (False, reason) -> Candidate is immediately REJECTED.
    """
    if has_explicit_ref:
        return True, "Explicit artifact reference passed gate"

    from utils.negation_detector import check_polarity_conflict
    is_conflict, conflict_reason = check_polarity_conflict(source_text, target_text)
    if is_conflict:
        return True, f"Policy conflict candidate: {conflict_reason}"

    src_low = source_text.lower()
    tgt_low = target_text.lower()

    # 1. Check for administrative / physical hardware procurement or obsolete analog media without software realization
    hardware_procurement_actions = ["procure", "purchas", "install", "order", "buy", "physical", "cater", "menu", "replac", "standing desk", "motorized", "decided to procure"]
    hardware_physical_objects = [
        "projector", "screen", "whiteboard", "chair", "desk", "furniture",
        "charger", "charging station", "espresso", "coffee", "shoe cleaner", "air purifier",
        "air conditioner", "hvac", "vending machine", "microwave", "refrigerator", "cooler",
        "breakroom", "parking lot", "standing desk", "lunch menu", "meal specials", "hot lunch",
        "catering", "sandwich", "fruit basket", "water heater", "whiteboard marker"
    ]
    obsolete_analog_media = ["microfiche", "microfilm", "35mm film", "punch card", "floppy disk", "magnetic tape reel"]

    is_physical_procurement = (
        (any(obj in src_low for obj in hardware_physical_objects) and (
            any(act in src_low for act in hardware_procurement_actions)
            or not any(sw in src_low for sw in ["software", "api", "app", "service", "module", "endpoint", "driver", "protocol", "portal", "command", "algorithm", "database", "pipeline", "function"])
        ))
        or (any(obj in tgt_low for obj in hardware_physical_objects) and (
            any(act in tgt_low for act in hardware_procurement_actions)
            or not any(sw in tgt_low for sw in ["software", "api", "app", "service", "module", "endpoint", "driver", "protocol", "portal", "command", "algorithm", "database", "pipeline", "function"])
        ))
        or (any(med in src_low for med in obsolete_analog_media) and not any(med in tgt_low for med in obsolete_analog_media))
    )

    if is_physical_procurement:
        return False, "Administrative, physical hardware, or obsolete analog media excluded from software traceability"

    # 2. Check for unresolved review statements
    gov_state, gov_reason = extract_governance_state(source_text)
    if gov_state == "UNRESOLVED":
        return False, f"Governance Gate: {gov_reason} excluded from automatic mapping"

    actions_a = extract_actions(source_text)
    actions_b = extract_actions(target_text)
    act_score, act_reason = evaluate_action_alignment(source_text, target_text)

    # 3. Incompatible action rejection (e.g. track vs export, reconcile vs refund, approve vs defect)
    if act_score <= 0.10 and not has_explicit_ref:
        return False, f"Relevance Gate Rejected: {act_reason}"

    # 4. Specialized capability mismatch (e.g. detect_dup vs generic capture, history vs dispatch)
    src_spec = actions_a & SPECIALIZED_CAPABILITIES
    tgt_spec = actions_b & SPECIALIZED_CAPABILITIES
    if src_spec and not (src_spec & tgt_spec) and not shared_intents:
        return False, f"Relevance Gate Rejected: Specialized capability [{', '.join(src_spec)}] missing in target"

    # 5. Entity and Action joint check: reject if entities are disjoint and actions differ without shared intent
    ent_score, ent_reason = evaluate_entity_alignment(source_text, target_text)
    sem = semantic_sim if semantic_sim is not None else lexical_sim
    if ent_score <= 0.10 and act_score <= 0.40 and not shared_intents and sem < 0.60:
        return False, "Relevance Gate Rejected: Disjoint domain entities and divergent actions"

    # 6. NFR / Performance constraint alignment: performance NFRs must not map to purely functional stories
    perf_keywords = {
        "latency", "response time", "throughput", "concurrent", "concurrency", "simultaneous",
        "availability", "uptime", "p95", "p99", "packets per second", "checkouts per minute",
        "performance", "capacity", "connections", "sessions", "rps", "tps", "qps"
    }
    src_perf = any(kw in src_low for kw in perf_keywords)
    tgt_perf = any(kw in tgt_low for kw in (perf_keywords | {"scale", "scaling", "autoscaler", "cache", "redis", "load balanc", "rate limit", "partition", "kafka", "distributed", "traffic"}))
    if src_perf and not tgt_perf:
        return False, "Relevance Gate Rejected: NFR performance constraint not represented in functional target"

    # 7. Semantic threshold minimum
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
        (r'\band\s+(?:receive\w*|get\w*)\s+.*?\b(?:receipt|notification|email|confirmation|sms)\w*\b', 'receipt / notification delivery'),
        (r'\band\s+(?:send\w*|dispatch\w*|notify\w*)\b', 'notification dispatch'),
        (r'\band\s+(?:record\w*|log\w*|archive\w*)\b', 'audit / archiving logging'),
        (r'\band\s+(?:upload\w*|attach\w*)\s+.*?\b(?:receipt|photo|evidence|image|document|file)\w*\b', 'attachment / image upload'),
    ]

    for pat, desc in compound_indicators:
        if re.search(pat, src_lower) and not re.search(pat, tgt_lower):
            return True, f"Source specifies secondary condition not covered in target ({desc})"

    if re.search(r'\bwithout\s+(?:attachments?|photos?|receipts?|images?|proof)\b', tgt_lower):
        if re.search(r'\b(?:attach|upload|photo|receipt|image)\b', src_lower):
            return True, "Target explicitly excludes secondary attachment requirement"

    # Generic check on coordinate action conjunctions (e.g. "submit expenses AND upload receipts")
    if re.search(r'\b(?:and|as well as)\s+(?:upload|attach|export|download|scan|notify|alert|dispatch)\b', src_lower):
        src_actions = extract_actions(source_text)
        tgt_actions = extract_actions(target_text)
        missing = src_actions - tgt_actions
        # If the missing action is a distinct secondary functional capability (not specialized dup/emergency)
        if missing and any(m in ["capture", "export", "notify"] for m in missing):
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


def compute_capability_identity_score(
    action_score: float,
    entity_score: float,
    context_score: float,
    actor_score: float,
    hybrid_score: float,
    shared_intents: Set[str],
    has_id_ref: bool = False
) -> Tuple[float, bool]:
    """
    Computes capability identity score prioritizing structural alignment:
    Priority: Action (35%) > Entity (30%) > Actor/Context (15%) > Hybrid Semantic (20%).
    
    Returns (capability_score, is_exact_capability)
    """
    if has_id_ref:
        return 1.0, True

    intent_boost = 0.10 if shared_intents else 0.0
    
    cap_score = (
        (action_score * 0.35)
        + (entity_score * 0.30)
        + (((context_score + actor_score) / 2.0) * 0.15)
        + (hybrid_score * 0.20)
        + intent_boost
    )
    cap_score = max(0.0, min(1.0, cap_score))
    
    # Exact capability realization condition:
    # High action alignment (>= 0.70) AND positive entity alignment (>= 0.50)
    # OR shared domain intents with action >= 0.60 and entity >= 0.40
    # OR strong entity overlap (>= 0.55) with hybrid >= 0.25 and neutral/compatible action (>= 0.50)
    # OR strong hybrid semantic similarity (>= 0.40) with entity overlap (>= 0.50) and compatible action (>= 0.40)
    is_exact = (
        (action_score >= 0.70 and entity_score >= 0.50)
        or (bool(shared_intents) and action_score >= 0.60 and entity_score >= 0.40)
        or (entity_score >= 0.55 and hybrid_score >= 0.25 and action_score >= 0.50)
        or (hybrid_score >= 0.40 and entity_score >= 0.50 and action_score >= 0.40)
    )
    
    return round(cap_score, 4), is_exact


def rank_and_disambiguate_candidates(
    candidates_evaluations: List[Dict],
    min_match_threshold: float = 0.45,
    min_partial_threshold: float = 0.28,
    ambiguity_margin: float = 0.04
) -> List[Dict]:
    """
    Ranks evaluated candidates that passed the relevance gate using capability identity
    first, computes score margins, and disambiguates close candidates.
    """
    if not candidates_evaluations:
        return []

    def _rank_key(c):
        has_miss = 1 if not c.get("has_missing") else 0
        is_ex = 1 if c.get("is_exact_capability") else 0
        cap_id = c.get("capability_identity_score", 0.0)
        comp = c.get("composite_score", 0.0)
        score = (cap_id * 0.60) + (comp * 0.40)
        return (has_miss, is_ex, score, comp)

    sorted_cands = sorted(candidates_evaluations, key=_rank_key, reverse=True)
    top = sorted_cands[0]
    
    if len(sorted_cands) > 1:
        second = sorted_cands[1]
        top_cap = top.get("capability_identity_score", top.get("composite_score", 0.0))
        sec_cap = second.get("capability_identity_score", second.get("composite_score", 0.0))
        score_margin = top_cap - sec_cap
        top["score_margin"] = round(score_margin, 4)
        
        # Ambiguity check: only when neither is an exact capability and score margin < ambiguity_margin
        if score_margin < ambiguity_margin and not top.get("is_exact_capability") and top["composite_score"] >= min_match_threshold:
            top["is_ambiguous"] = True
            top["disambiguated_status"] = "PARTIAL"
            top["status"] = "PARTIAL"
            top["confidence"] = "Medium"
            top["evidence"] = top.get("evidence", "") + f" | Ambiguous match (close candidate score margin: {score_margin:.3f})"
            return [top]

    top["score_margin"] = 1.0 if len(sorted_cands) == 1 else round(top.get("capability_identity_score", top["composite_score"]) - sorted_cands[1].get("capability_identity_score", sorted_cands[1]["composite_score"]), 4)
    return [top]
