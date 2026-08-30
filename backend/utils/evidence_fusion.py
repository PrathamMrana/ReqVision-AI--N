"""
backend/utils/evidence_fusion.py

Generic Evidence Fusion & Anti-Hallucination Engine for ReqVision AI Phase 3.

Evaluates multi-dimensional evidence between source and target requirements:
1. Action / Verb Alignment (reconcile != refund, cancel == revoke, authenticate == verify identity)
2. Entity / Concept Alignment (settlement != refund transaction)
3. Completeness & Entailment (source has A + B, target only has A -> PARTIAL)
4. Capability Extension (target adds alternative option -> MATCHED/EXTENDED, not CONFLICT)
5. Candidate Ranking & Ambiguity Margin Check (close candidates -> AMBIGUOUS)

NO project-specific logic, IDs, filenames, or hardcoded project names.
Operates strictly on generic linguistic, structural, and semantic properties.
"""

import re
from typing import Tuple, List, Dict, Set, Optional

# Generic core action patterns and synonymous action families
ACTION_PATTERNS = {
    "auth": [r"\bauthenticat\w*\b", r"\blogin\b", r"\bsign-?in\b", r"\bverify\b.{0,15}\bidentity\b", r"\bauthoriz\w*\b", r"\bmfa\b", r"\b2fa\b", r"\bsession\b"],
    "cancel": [r"\bcancel\w*\b", r"\brevok\w*\b", r"\bterminat\w*\b", r"\bdiscontinu\w*\b", r"\bvoid\b", r"\babort\b", r"\breleas\w*\b"],
    "reserve": [r"\breserv\w*\b", r"\bbook\w*\b", r"\bhold\b", r"\ballocat\w*\b", r"\bschedul\w*\b", r"\bappoint\w*\b"],
    "pay": [r"\bpay\w*\b", r"\bcheckout\b", r"\bcharg\w*\b", r"\bbill\w*\b", r"\bremit\w*\b"],
    "refund": [r"\brefund\w*\b", r"\breimburs\w*\b", r"\brevers\w*\s+payment\b", r"\bcredit\s+back\b", r"\breturn\s+funds\b"],
    "reconcile": [r"\breconcil\w*\b", r"\bmatch\s+settlement\b", r"\bcompar\w*\s+files\b", r"\baudit\s+ledger\b", r"\bbalance\s+records\b"],
    "notify": [r"\bnotif\w*\b", r"\balert\w*\b", r"\bremind\w*\b", r"\bsend\s+(?:email|sms)\b", r"\bdispatch\w*\b", r"\bpush\s+notification\b"],
    "search": [r"\bsearch\w*\b", r"\bquery\w*\b", r"\bfind\w*\b", r"\blookup\b", r"\bfilter\w*\b", r"\bbrowse\w*\b", r"\blocat\w*\b"],
    "export": [r"\bexport\w*\b", r"\bdownload\w*\b", r"\bextract\s+data\b", r"\barchiv\w*\b", r"\bdump\b"],
    "manage": [r"\bcreat\w*\b", r"\bupdat\w*\b", r"\bdelet\w*\b", r"\bedit\w*\b", r"\bmaintain\w*\b", r"\bmodif\w*\b", r"\bregister\w*\b", r"\bonboard\w*\b"],
    "track": [r"\btrack\w*\b", r"\bmonitor\w*\b", r"\btelemetry\b", r"\bgps\b", r"\blive\s+location\b", r"\beta\b"],
}

# Stopwords to filter out when extracting entities
GENERIC_BOILERPLATE = {
    "system", "platform", "user", "users", "service", "services", "application",
    "feature", "module", "component", "endpoint", "shall", "must", "should",
    "will", "able", "allow", "allows", "allowed", "provide", "provides", "provided",
    "want", "wants", "order", "view", "views", "data", "information", "details",
    "support", "supports", "supported", "implement", "implements", "implemented",
    "verify", "verifies", "verified", "test", "tests", "tested", "scenario", "scenarios"
}


def extract_actions(text: str) -> Set[str]:
    """
    Extracts high-level action cluster keys present in the requirement text.
    """
    t = text.lower()
    detected_clusters = set()
    for cluster_name, patterns in ACTION_PATTERNS.items():
        if any(re.search(pat, t) for pat in patterns):
            detected_clusters.add(cluster_name)
    return detected_clusters


def extract_entities(text: str) -> Set[str]:
    """
    Extracts domain-relevant entity tokens (excluding boilerplate).
    """
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


def evaluate_action_alignment(text_a: str, text_b: str) -> Tuple[float, str]:
    """
    Evaluates action compatibility between source and target.
    """
    actions_a = extract_actions(text_a)
    actions_b = extract_actions(text_b)

    if not actions_a or not actions_b:
        return 0.70, "Neutral action alignment"

    shared = actions_a & actions_b
    if shared:
        return 1.0, f"Aligned actions on [{', '.join(shared)}]"

    # Incompatible action pairs
    INCOMPATIBLE_PAIRS = [
        ({"reconcile"}, {"refund"}),
        ({"export"}, {"manage"}),
        ({"cancel"}, {"reserve"}),
        ({"search"}, {"manage"}),
    ]
    for group1, group2 in INCOMPATIBLE_PAIRS:
        if (actions_a & group1 and actions_b & group2) or (actions_a & group2 and actions_b & group1):
            return 0.10, f"Action divergence: [{', '.join(actions_a)}] vs [{', '.join(actions_b)}]"

    return 0.40, f"Different actions: [{', '.join(actions_a)}] vs [{', '.join(actions_b)}]"


def evaluate_entity_alignment(text_a: str, text_b: str) -> Tuple[float, str]:
    """
    Calculates entity Jaccard overlap between source and target requirements.
    """
    ent_a = extract_entities(text_a)
    ent_b = extract_entities(text_b)

    if not ent_a or not ent_b:
        return 0.50, "Neutral entity overlap"

    intersection = ent_a & ent_b
    union = ent_a | ent_b
    jaccard = len(intersection) / len(union) if union else 0.0

    if jaccard >= 0.25:
        return min(1.0, 0.60 + jaccard), f"Shared domain entities: [{', '.join(list(intersection)[:4])}]"
    elif intersection:
        return 0.60, f"Weak shared entity overlap: [{', '.join(list(intersection)[:3])}]"
    else:
        return 0.20, "No shared domain entities"


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

    if re.search(r'\bor\s+(?:digital\s+wallets?|apple\s+pay|google\s+pay|cash|sms|bank\s+transfers?|qr)\b', tgt_lower):
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
    Ranks evaluated candidates, computes score margins, and disambiguates close candidates.
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
            if top.get("action_score", 0) <= second.get("action_score", 0) and top.get("entity_score", 0) <= second.get("entity_score", 0):
                top["is_ambiguous"] = True
                top["status"] = "PARTIAL"
                top["confidence"] = "Medium"
                top["evidence"] += f" | Ambiguous match (close candidate score margin: {score_margin:.3f})"
                return [top]

    top["score_margin"] = 1.0 if len(sorted_cands) == 1 else round(top["composite_score"] - sorted_cands[1]["composite_score"], 4)
    return [top]
