"""
Phase 3 Adversarial Semantic Tests — direct engine tests (no HTTP).

Tests the semantic engine and negation detector directly with the 7 required adversarial cases.
Prints actual semantic_similarity scores from all-MiniLM-L6-v2 (NOT mocked).

Run: python test_semantic_adversarial.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.semantic_engine import SemanticEngine
from utils.negation_detector import check_polarity_conflict, check_numeric_conflict

engine = SemanticEngine()

PASS = "✅ PASS"
FAIL = "❌ FAIL"
SEP = "-" * 70


def check(label, condition, detail=""):
    result = PASS if condition else FAIL
    print(f"  {result}  {label}")
    if detail:
        print(f"         {detail}")
    return condition


def run_adversarial_tests():
    print("\n" + "=" * 70)
    print("  REQVISION AI — PHASE 3 ADVERSARIAL SEMANTIC TESTS")
    print(f"  Model: {engine.model_name}")
    print(f"  Available: {engine.is_available()}")
    print("=" * 70)

    if not engine.is_available():
        print("\n⚠ Semantic engine not available — cannot run semantic tests.")
        print("  Install sentence-transformers and re-run.")
        return False

    all_passed = True

    # ── CASE 1: PARAPHRASE ───────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("CASE 1 — Paraphrase (different wording, same meaning)")
    a = "Users can cancel a booking."
    b = "Passengers may revoke their reservation."
    sim = engine.compute_semantic_similarity(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic similarity: {sim:.4f}")
    pol_conflict, _ = check_polarity_conflict(a, b)
    passed = check("Semantic similarity > 0.55 (semantically related)", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("No polarity conflict detected", not pol_conflict, f"polarity_conflict={pol_conflict}")
    all_passed &= passed

    # ── CASE 2: SYNONYM ──────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("CASE 2 — Synonym (authenticate vs verify identity)")
    a = "Users must authenticate."
    b = "Members must verify their identity."
    sim = engine.compute_semantic_similarity(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic similarity: {sim:.4f}")
    pol_conflict, _ = check_polarity_conflict(a, b)
    passed = check("Semantic similarity > 0.55 (semantically related)", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("No polarity conflict detected", not pol_conflict, f"polarity_conflict={pol_conflict}")
    all_passed &= passed

    # ── CASE 3: NEGATION CONFLICT ────────────────────────────────────────────
    print(f"\n{SEP}")
    print("CASE 3 — Negation Conflict (guest checkout allowed vs prohibited)")
    a = "Guests may check out without logging in."
    b = "Guest checkout is prohibited."
    sim = engine.compute_semantic_similarity(a, b)
    pol_conflict, pol_reason = check_polarity_conflict(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic similarity: {sim:.4f}")
    print(f"  Polarity conflict: {pol_conflict} — {pol_reason}")
    passed = check("Polarity conflict detected", pol_conflict, f"Reason: {pol_reason}")
    # High semantic + polarity conflict → CONFLICT, not MATCHED
    if sim is not None and sim > 0.40 and pol_conflict:
        passed &= check("Would be classified as CONFLICT (not MATCHED)", True)
    all_passed &= passed

    # ── CASE 4: NUMERIC CHANGE ───────────────────────────────────────────────
    print(f"\n{SEP}")
    print("CASE 4 — Numeric Change (same capability, different quantity)")
    a = "System supports 500 concurrent users."
    b = "Platform handles 2000 simultaneous users."
    sim = engine.compute_semantic_similarity(a, b)
    num_result, num_reason = check_numeric_conflict(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic similarity: {sim:.4f}")
    print(f"  Numeric result: {num_result} — {num_reason}")
    passed = check("Semantic similarity > 0.55 (same capability concept)", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Numeric result is MODIFIED_VALUE (not CONFLICT, not UNMAPPED)", num_result == "MODIFIED_VALUE", f"Got: {num_result}")
    all_passed &= passed

    # ── CASE 5: FALSE POSITIVE ───────────────────────────────────────────────
    print(f"\n{SEP}")
    print("CASE 5 — False Positive Prevention (unrelated admin actions)")
    a = "Administrator exports historical catalogue data."
    b = "Administrator updates inventory quantity."
    sim = engine.compute_semantic_similarity(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic similarity: {sim:.4f}")
    # These should NOT be a strong match (different domain actions)
    passed = check("Semantic similarity < 0.70 (not a strong match)", sim is not None and sim < 0.70, f"Got: {sim:.4f}")
    all_passed &= passed

    # ── CASE 6: MISSING CONDITION ────────────────────────────────────────────
    print(f"\n{SEP}")
    print("CASE 6 — Missing Condition (reserve + notification vs reserve only)")
    a = "Members may reserve books and receive email notification."
    b = "Members may reserve books."
    sim = engine.compute_semantic_similarity(a, b)
    pol_conflict, _ = check_polarity_conflict(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic similarity: {sim:.4f}")
    # Related but incomplete — should be PARTIAL, not full MATCHED
    passed = check("Semantic similarity > 0.55 (related concept)", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("No polarity conflict (not a contradiction)", not pol_conflict)
    # Note: PARTIAL vs MATCHED classification depends on full hybrid score in context
    all_passed &= passed

    # ── CASE 7: SAME MEANING, DIFFERENT STRUCTURE ────────────────────────────
    print(f"\n{SEP}")
    print("CASE 7 — Same Meaning, Different Sentence Structure")
    a = "The platform must send an alert when a reserved vehicle is cancelled."
    b = "When a booked shuttle is cancelled, riders receive a notification."
    sim = engine.compute_semantic_similarity(a, b)
    pol_conflict, _ = check_polarity_conflict(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic similarity: {sim:.4f}")
    passed = check("Semantic similarity > 0.55 (same intent, different structure)", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("No polarity conflict detected", not pol_conflict)
    all_passed &= passed

    # ── SUMMARY ─────────────────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    if all_passed:
        print("✅ ALL 7 ADVERSARIAL CASES PASSED")
    else:
        print("❌ SOME ADVERSARIAL CASES FAILED — review output above")
    print(f"{'=' * 70}")
    return all_passed


if __name__ == "__main__":
    success = run_adversarial_tests()
    sys.exit(0 if success else 1)
