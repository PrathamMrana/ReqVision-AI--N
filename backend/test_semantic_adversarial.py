"""
ReqVision AI — Phase 3 Final Complete 16-Case Adversarial Semantic Suite.

Verifies the Canonical Relevance Gate, Capability Extraction & Anti-Hallucination:
 1. Paraphrase
 2. Synonym
 3. Action divergence
 4. Entity divergence
 5. Negation conflict
 6. Numeric change (MODIFIED_VALUE)
 7. Extension (Additional channels != conflict)
 8. Replacement / Incompatibility (Mutual exclusion -> CONFLICT)
 9. Missing condition (Entailment -> PARTIAL)
10. Unrelated high semantic candidate (Relevance Gate rejection)
11. High lexical but wrong action (Relevance Gate rejection)
12. Ambiguous candidates (Score margin -> PARTIAL)
13. Multiple weak candidates (Relevance Gate rejection -> UNMAPPED)
14. One valid + one invalid target (Single valid edge retained)
15. Unresolved meeting statement (Consensus not agreed -> UNMAPPED)
16. Genuinely unmapped change request (No underlying target -> UNMAPPED)

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
    evaluate_candidate_relevance_gate,
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
    print("  REQVISION AI — PHASE 3 COMPLETE 16-CASE ADVERSARIAL SUITE")
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
    is_rel, rel_reason = evaluate_candidate_relevance_gate(a, b, sim, 0.20, set())
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Action: {act_score:.2f} | Gate: {is_rel}")
    passed = check("Semantic similarity > 0.55 (semantically related)", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Candidate passes Relevance Gate", is_rel)
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
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.20, set())
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Semantic: {sim:.4f} | Action: {act_score:.2f} | Gate: {is_rel}")
    passed = check("Semantic similarity > 0.55", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Candidate passes Relevance Gate", is_rel)
    passed &= check("Action alignment recognized (authenticate == verify identity)", act_score >= 0.80)
    all_passed &= passed

    # ── CASE 3: ACTION DIVERGENCE ────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 3 — Action Divergence (reconcile vs refund)")
    a = "Finance staff reconcile settlement records."
    b = "Finance staff issue refunds."
    sim = engine.compute_semantic_similarity(a, b)
    act_score, act_reason = evaluate_action_alignment(a, b)
    is_rel, rel_reason = evaluate_candidate_relevance_gate(a, b, sim, 0.15, set())
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Action: {act_score:.2f} ({act_reason}) | Gate: {is_rel} ({rel_reason})")
    passed = check("Incompatible actions rejected at Relevance Gate", not is_rel)
    all_passed &= passed

    # ── CASE 4: ENTITY DIVERGENCE ────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 4 — Entity Divergence (mobile receipt capture vs passport storage)")
    a = "The mobile application shall capture digital photos of expense receipts."
    b = "Add an international biometric passport storage vault."
    sim = engine.compute_semantic_similarity(a, b)
    ent_score, ent_reason = evaluate_entity_alignment(a, b)
    is_rel, rel_reason = evaluate_candidate_relevance_gate(a, b, sim, 0.05, set())
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Entity overlap: {ent_score:.2f} | Gate: {is_rel} ({rel_reason})")
    passed = check("Incompatible entity concepts rejected at Relevance Gate", not is_rel)
    all_passed &= passed

    # ── CASE 5: NEGATION CONFLICT ────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 5 — Negation Conflict (guest checkout allowed vs prohibited)")
    a = "Guests may check out without logging in."
    b = "Guest checkout is prohibited."
    sim = engine.compute_semantic_similarity(a, b)
    pol, reason = check_polarity_conflict(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.40, set())
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Gate: {is_rel} | Polarity conflict: {pol} ({reason})")
    passed = check("Same capability passes Relevance Gate", is_rel)
    passed &= check("Polarity conflict detected on same capability", pol)
    all_passed &= passed

    # ── CASE 6: NUMERIC CHANGE ───────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 6 — Numeric Change (5000 vs 15000 concurrent sessions)")
    a = "System supports 5000 concurrent sessions."
    b = "Platform handles 15000 simultaneous sessions."
    sim = engine.compute_semantic_similarity(a, b)
    num_res, num_reason = check_numeric_conflict(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.40, set())
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Gate: {is_rel} | Numeric: {num_res} ({num_reason})")
    passed = check("Passes Relevance Gate", is_rel)
    passed &= check("Numeric result is MODIFIED_VALUE (not CONFLICT)", num_res == "MODIFIED_VALUE")
    all_passed &= passed

    # ── CASE 7: EXTENSION ────────────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 7 — Capability Extension (email vs email + Slack)")
    a = "Send approval notifications via email."
    b = "Send approval notifications via email or Slack."
    is_ext, ext_reason = detect_capability_extension(a, b)
    pol, _ = check_polarity_conflict(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Is extension: {is_ext} ({ext_reason}) | Polarity conflict: {pol}")
    passed = check("Recognized as capability extension", is_ext)
    passed &= check("NOT flagged as CONFLICT", not pol)
    all_passed &= passed

    # ── CASE 8: REPLACEMENT / INCOMPATIBILITY ─────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 8 — Replacement / Incompatibility (reversible password vs salted hash)")
    a = "Employee passwords shall be stored using reversible DES encryption."
    b = "Employee passwords shall be stored using salted PBKDF2 hashing. Reversible storage is prohibited."
    sim = engine.compute_semantic_similarity(a, b)
    pol, reason = check_polarity_conflict(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.40, set())
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Gate: {is_rel} | Polarity conflict: {pol}")
    passed = check("Passes Relevance Gate (same authentication credential capability)", is_rel)
    passed &= check("Flags CONFLICT due to incompatible security policy", pol)
    all_passed &= passed

    # ── CASE 9: MISSING CONDITION ────────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 9 — Missing Condition (submit expense + upload receipt vs submit only)")
    a = "Employees can submit expenses and upload receipts."
    b = "Employees can submit expenses."
    sim = engine.compute_semantic_similarity(a, b)
    has_missing, missing_reason = detect_missing_conditions(a, b)
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Missing condition: {has_missing} ({missing_reason})")
    passed = check("Missing secondary condition detected -> PARTIAL", has_missing)
    all_passed &= passed

    # ── CASE 10: UNRELATED HIGH SEMANTIC CANDIDATE ───────────────────────────
    print(f"\n{MINI}")
    print("CASE 10 — Unrelated High Semantic Candidate (admin export vs inventory update)")
    a = "Administrator exports historical catalogue data."
    b = "Administrator updates inventory quantity."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, rel_reason = evaluate_candidate_relevance_gate(a, b, sim, 0.15, set())
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Gate: {is_rel} ({rel_reason})")
    passed = check("Rejected by Relevance Gate (divergent action and intent)", not is_rel)
    all_passed &= passed

    # ── CASE 11: HIGH LEXICAL BUT WRONG ACTION ───────────────────────────────
    print(f"\n{MINI}")
    print("CASE 11 — High Lexical but Wrong Action (receipt capture vs duplicate detection)")
    a = "The mobile application shall capture and upload digital photos of expense receipts."
    b = "Verify that uploading a duplicate receipt image flags the claim with a duplicate warning."
    sim = engine.compute_semantic_similarity(a, b)
    act_score, act_reason = evaluate_action_alignment(a, b)
    is_rel, rel_reason = evaluate_candidate_relevance_gate(a, b, sim, 0.35, set())
    print(f"  Text A: {a}")
    print(f"  Text B: {b}")
    print(f"  Action: {act_score:.2f} ({act_reason}) | Gate: {is_rel} ({rel_reason})")
    passed = check("Action divergence (capture vs duplicate check) rejected at Relevance Gate", not is_rel)
    all_passed &= passed

    # ── CASE 12: AMBIGUOUS CANDIDATES ────────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 12 — Candidate Disambiguation (close candidates with no clear winner)")
    c1 = {"cand": {"text": "Reduce refund processing time."}, "composite_score": 0.52, "hybrid": 0.52, "sem_score": 0.55, "lex_score": 0.30, "intent_val": 0.0, "action_score": 0.7, "entity_score": 0.7, "has_missing": False, "missing_reason": "", "is_extension": False, "extension_reason": "", "num_result": "NONE", "num_reason": "", "evidence": "", "shared_intents": set()}
    c2 = {"cand": {"text": "Expand refund eligibility."}, "composite_score": 0.51, "hybrid": 0.51, "sem_score": 0.54, "lex_score": 0.30, "intent_val": 0.0, "action_score": 0.7, "entity_score": 0.7, "has_missing": False, "missing_reason": "", "is_extension": False, "extension_reason": "", "num_result": "NONE", "num_reason": "", "evidence": "", "shared_intents": set()}
    ranked = rank_and_disambiguate_candidates([c1, c2], min_match_threshold=0.45, ambiguity_margin=0.04)
    print(f"  Candidate 1 score: {c1['composite_score']} | Candidate 2 score: {c2['composite_score']}")
    print(f"  Ranked status: {ranked[0].get('status')} | Is ambiguous: {ranked[0].get('is_ambiguous')}")
    passed = check("Close candidates flagged as ambiguous -> PARTIAL", ranked[0].get("is_ambiguous") is True and ranked[0].get("status") == "PARTIAL")
    all_passed &= passed

    # ── CASE 13: MULTIPLE WEAK CANDIDATES ────────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 13 — Multiple Weak Candidates (all fail Relevance Gate -> UNMAPPED)")
    src = "Calculate travel cost estimates before booking."
    cands = [
        "Issue refunds for cancelled trips.",
        "Store employee profile pictures.",
        "Configure LDAP active directory integration."
    ]
    surviving = []
    for c in cands:
        sim = engine.compute_semantic_similarity(src, c)
        is_rel, _ = evaluate_candidate_relevance_gate(src, c, sim, 0.05, set())
        if is_rel:
            surviving.append(c)
    print(f"  Source: {src}")
    print(f"  Surviving candidates after Relevance Gate: {len(surviving)}")
    passed = check("All weak unrelated candidates rejected -> 0 surviving", len(surviving) == 0)
    all_passed &= passed

    # ── CASE 14: ONE VALID + ONE INVALID TARGET ──────────────────────────────
    print(f"\n{MINI}")
    print("CASE 14 — One Valid + One Invalid Target (accept valid, reject invalid)")
    src = "Employees can withdraw a pending travel request."
    c_valid = "Verify that an employee can withdraw a pending travel request and release booking holds."
    c_invalid = "Verify that uploading a duplicate receipt image flags duplicate warning."
    sim_val = engine.compute_semantic_similarity(src, c_valid)
    sim_inv = engine.compute_semantic_similarity(src, c_invalid)
    is_rel_val, _ = evaluate_candidate_relevance_gate(src, c_valid, sim_val, 0.40, set())
    is_rel_inv, _ = evaluate_candidate_relevance_gate(src, c_invalid, sim_inv, 0.05, set())
    print(f"  Valid target gate: {is_rel_val} (sim={sim_val:.2f})")
    print(f"  Invalid target gate: {is_rel_inv} (sim={sim_inv:.2f})")
    passed = check("Valid candidate accepted", is_rel_val)
    passed &= check("Invalid candidate rejected", not is_rel_inv)
    all_passed &= passed

    # ── CASE 15: UNRESOLVED MEETING STATEMENT ────────────────────────────────
    print(f"\n{MINI}")
    print("CASE 15 — Unresolved Meeting Statement (consensus not reached -> UNMAPPED)")
    src = "The team discussed faster approvals but did not define the meaning or implementation."
    target = "The manager workflow service shall route travel requests to designated managers."
    sim = engine.compute_semantic_similarity(src, target)
    is_rel, rel_reason = evaluate_candidate_relevance_gate(src, target, sim, 0.20, set())
    print(f"  Source: {src}")
    print(f"  Gate: {is_rel} ({rel_reason})")
    passed = check("Unresolved review statement excluded from automatic mapping", not is_rel)
    all_passed &= passed

    # ── CASE 16: GENUINELY UNMAPPED CHANGE REQUEST ───────────────────────────
    print(f"\n{MINI}")
    print("CASE 16 — Genuinely Unmapped Change Request (new unsupported capability)")
    src = "Add a biometric international passport storage vault in travel agency partner office."
    spec = "The mobile receipt service shall allow employees to photograph receipts and attach to claims."
    sim = engine.compute_semantic_similarity(src, spec)
    is_rel, rel_reason = evaluate_candidate_relevance_gate(src, spec, sim, 0.10, set())
    print(f"  Source: {src}")
    print(f"  Spec: {spec}")
    print(f"  Gate: {is_rel} ({rel_reason})")
    passed = check("Unsupported delta rejected at Relevance Gate -> UNMAPPED", not is_rel)
    all_passed &= passed

    # ── FINAL SUMMARY ────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    if all_passed:
        print("🎉 ALL 16 ADVERSARIAL CASES PASSED")
    else:
        print("❌ SOME ADVERSARIAL CASES FAILED — review output above")
    print(SEP)
    return all_passed


if __name__ == "__main__":
    success = run_all_adversarial_tests()
    sys.exit(0 if success else 1)
