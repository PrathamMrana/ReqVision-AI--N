"""
ReqVision AI — Phase 3 Complete Adversarial Semantic Suite (Cases 1 - 12).

Tests the multi-dimensional evidence fusion engine directly:
- Dense semantic embeddings (all-MiniLM-L6-v2)
- Action / Verb alignment
- Entity alignment
- Negation / Polarity conflicts
- Numeric dimension extraction
- Missing secondary conditions / Entailment
- Capability extensions
- Ambiguity margin detection

Run: python test_semantic_adversarial.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.semantic_engine import SemanticEngine
from utils.negation_detector import check_polarity_conflict, check_numeric_conflict
from utils.evidence_fusion import (
    evaluate_action_alignment,
    evaluate_entity_alignment,
    detect_missing_conditions,
    detect_capability_extension,
    rank_and_disambiguate_candidates
)

engine = SemanticEngine()

PASS = "✅ PASS"
FAIL = "❌ FAIL"
SEP = "=" * 75
MINI = "-" * 75


def check(label, condition, detail=""):
    result = PASS if condition else FAIL
    print(f"  {result}  {label}")
    if detail:
        print(f"         {detail}")
    return condition


def run_all_adversarial_tests():
    print("\n" + SEP)
    print("  REQVISION AI — PHASE 3 COMPLETE ADVERSARIAL SEMANTIC SUITE (CASES 1-12)")
    print(f"  Model: {engine.model_name}")
    print(f"  Available: {engine.is_available()}")
    print(SEP)

    if not engine.is_available():
        print("\n⚠ Semantic engine not available — cannot run semantic tests.")
        return False

    all_passed = True

    # ── CASE 1: PARAPHRASE ───────────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 1 — Paraphrase (different wording, same meaning)")
    a = "Users can cancel a booking."
    b = "Passengers may revoke their reservation."
    sim = engine.compute_semantic_similarity(a, b)
    pol, _ = check_polarity_conflict(a, b)
    act_score, _ = evaluate_action_alignment(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Action score: {act_score:.2f}")
    passed = check("Semantic similarity > 0.55 (semantically related)", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Action alignment recognized (cancel == revoke)", act_score >= 0.80)
    passed &= check("No polarity conflict", not pol)
    all_passed &= passed

    # ── CASE 2: SYNONYM ──────────────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 2 — Synonym (authenticate vs verify identity)")
    a = "Users must authenticate."
    b = "Members must verify their identity."
    sim = engine.compute_semantic_similarity(a, b)
    act_score, _ = evaluate_action_alignment(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Action score: {act_score:.2f}")
    passed = check("Semantic similarity > 0.55", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Action alignment recognized (authenticate == verify identity)", act_score >= 0.80)
    all_passed &= passed

    # ── CASE 3: NEGATION CONFLICT ────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 3 — Negation Conflict (guest checkout allowed vs prohibited)")
    a = "Guests may check out without logging in."
    b = "Guest checkout is prohibited."
    sim = engine.compute_semantic_similarity(a, b)
    pol, reason = check_polarity_conflict(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Polarity conflict: {pol} ({reason})")
    passed = check("Polarity conflict detected", pol, f"Reason: {reason}")
    passed &= check("Correctly flagged as CONFLICT (not MATCHED)", pol and sim is not None and sim > 0.40)
    all_passed &= passed

    # ── CASE 4: NUMERIC CHANGE ───────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 4 — Numeric Change (same capability, different quantity)")
    a = "System supports 500 concurrent users."
    b = "Platform handles 2000 simultaneous users."
    sim = engine.compute_semantic_similarity(a, b)
    num_res, num_reason = check_numeric_conflict(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Numeric: {num_res} ({num_reason})")
    passed = check("Semantic similarity > 0.55 (same capability)", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Numeric result is MODIFIED_VALUE (not CONFLICT, not UNMAPPED)", num_res == "MODIFIED_VALUE")
    all_passed &= passed

    # ── CASE 5: FALSE POSITIVE ───────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 5 — False Positive Prevention (unrelated admin actions)")
    a = "Administrator exports historical catalogue data."
    b = "Administrator updates inventory quantity."
    sim = engine.compute_semantic_similarity(a, b)
    act_score, act_reason = evaluate_action_alignment(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Action score: {act_score:.2f} ({act_reason})")
    passed = check("Semantic similarity < 0.70", sim is not None and sim < 0.70, f"Got: {sim:.4f}")
    passed &= check("Action divergence detected (export != update/manage)", act_score <= 0.40)
    all_passed &= passed

    # ── CASE 6: MISSING CONDITION ────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 6 — Missing Condition (reserve + notification vs reserve only)")
    a = "Members may reserve books and receive email notification."
    b = "Members may reserve books."
    sim = engine.compute_semantic_similarity(a, b)
    has_missing, missing_reason = detect_missing_conditions(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Missing condition: {has_missing} ({missing_reason})")
    passed = check("Semantic similarity > 0.55 (conceptually related)", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Missing secondary condition detected -> PARTIAL", has_missing)
    all_passed &= passed

    # ── CASE 7: SAME MEANING, DIFFERENT STRUCTURE ────────────────────────────
    print(f"\n{MINI}")
    print("CASE 7 — Same Meaning, Different Sentence Structure")
    a = "The platform must send an alert when a reserved vehicle is cancelled."
    b = "When a booked shuttle is cancelled, riders receive a notification."
    sim = engine.compute_semantic_similarity(a, b)
    act_score, _ = evaluate_action_alignment(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Action score: {act_score:.2f}")
    passed = check("Semantic similarity > 0.55", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Actions aligned on notify & cancel", act_score >= 0.80)
    all_passed &= passed

    # ── CASE 8: SAME TOPIC, DIFFERENT ACTION ─────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 8 — Same Topic, Different Action (reconcile vs refund)")
    a = "Finance staff reconcile processor settlements."
    b = "Finance staff refund eligible transactions."
    sim = engine.compute_semantic_similarity(a, b)
    act_score, act_reason = evaluate_action_alignment(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Action score: {act_score:.2f} ({act_reason})")
    passed = check("Incompatible actions penalized (reconcile != refund)", act_score <= 0.20)
    # Even if semantic similarity is non-zero, action conflict prevents false MATCHED
    all_passed &= passed

    # ── CASE 9: SAME WORDS, OPPOSITE POLICY ──────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 9 — Same Words, Opposite Policy (allowed vs not allowed)")
    a = "Guest checkout is allowed."
    b = "Guest checkout is not allowed."
    sim = engine.compute_semantic_similarity(a, b)
    pol, reason = check_polarity_conflict(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Polarity conflict: {pol} ({reason})")
    passed = check("Opposite policy detected as polarity conflict", pol)
    passed &= check("Emits CONFLICT rather than false MATCHED", pol)
    all_passed &= passed

    # ── CASE 10: HIGH SIMILARITY BUT PARTIAL ─────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 10 — High Similarity but Partial (card + receipt vs card only)")
    a = "Students can pay with a card and receive an email receipt."
    b = "Students can pay with a card."
    sim = engine.compute_semantic_similarity(a, b)
    has_missing, missing_reason = detect_missing_conditions(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Missing condition: {has_missing} ({missing_reason})")
    passed = check("Missing receipt clause detected -> PARTIAL", has_missing)
    all_passed &= passed

    # ── CASE 11: EXTENSION ───────────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 11 — Capability Extension (cards vs cards or digital wallets)")
    a = "Students can pay with cards."
    b = "Students can pay with cards or digital wallets."
    is_ext, ext_reason = detect_capability_extension(a, b)
    pol, _ = check_polarity_conflict(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Is extension: {is_ext} ({ext_reason}) | Polarity conflict: {pol}")
    passed = check("Extended payment option recognized", is_ext)
    passed &= check("NOT flagged as CONFLICT", not pol)
    all_passed &= passed

    # ── CASE 12: AMBIGUITY ───────────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 12 — Candidate Disambiguation (close candidates with no clear winner)")
    src = "Improve refund handling."
    c1 = {"cand": {"text": "Reduce refund processing time."}, "composite_score": 0.52, "hybrid": 0.52, "sem_score": 0.55, "lex_score": 0.30, "intent_val": 0.0, "action_score": 0.7, "entity_score": 0.7, "has_missing": False, "missing_reason": "", "is_extension": False, "extension_reason": "", "num_result": "NONE", "num_reason": "", "evidence": "", "shared_intents": set()}
    c2 = {"cand": {"text": "Expand refund eligibility."}, "composite_score": 0.51, "hybrid": 0.51, "sem_score": 0.54, "lex_score": 0.30, "intent_val": 0.0, "action_score": 0.7, "entity_score": 0.7, "has_missing": False, "missing_reason": "", "is_extension": False, "extension_reason": "", "num_result": "NONE", "num_reason": "", "evidence": "", "shared_intents": set()}
    ranked = rank_and_disambiguate_candidates([c1, c2], min_match_threshold=0.45, ambiguity_margin=0.04)
    print(f"  Source: {src}")
    print(f"  Candidate 1 score: {c1['composite_score']} | Candidate 2 score: {c2['composite_score']}")
    print(f"  Ranked status: {ranked[0].get('status')} | Is ambiguous: {ranked[0].get('is_ambiguous')}")
    passed = check("Close candidates flagged as ambiguous -> PARTIAL", ranked[0].get("is_ambiguous") is True and ranked[0].get("status") == "PARTIAL")
    all_passed &= passed

    # ── FINAL SUMMARY ────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    if all_passed:
        print("🎉 ALL 12 ADVERSARIAL CASES PASSED")
    else:
        print("❌ SOME ADVERSARIAL CASES FAILED — review output above")
    print(SEP)
    return all_passed


if __name__ == "__main__":
    success = run_all_adversarial_tests()
    sys.exit(0 if success else 1)
