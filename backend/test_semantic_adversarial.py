"""
ReqVision AI — Phase 3 Final Complete 22-Case Adversarial Semantic Suite.

Verifies the Complete Generic Capability Reasoning & Anti-Hallucination Pipeline:
 1. Paraphrase (Cancel booking vs Revoke reservation)
 2. Synonym (Authenticate vs Verify identity)
 3. Different sentence structure (Alert on cancellation vs When shuttle cancelled send notification)
 4. Active vs Passive voice (Flight controllers track orbits vs Orbits are tracked by controllers)
 5. Related topic / different action (Reconcile settlement vs Refund transactions)
 6. Related topic / different object (Patient chart access vs Appointment reminder)
 7. Same object / different capability (Receipt photo capture vs Duplicate receipt fraud detection)
 8. Missing condition (Submit expenses & upload receipts vs Submit expenses)
 9. Additional condition (Extension: Pay with card vs Pay with card or digital wallet)
10. Numeric change (5000 concurrent sessions vs 15000 simultaneous sessions -> MODIFIED_VALUE)
11. Extension channels (Email alert vs Email or Slack notification)
12. Replacement / Incompatibility (Reversible XOR encryption vs Salted Argon2id hashing -> CONFLICT)
13. Negation (Guest checkout allowed vs Guest checkout prohibited -> CONFLICT)
14. Actual contradiction (Mutually exclusive access policy -> CONFLICT)
15. Ambiguous candidate (Score margin < 0.04 -> PARTIAL)
16. Weak nearest neighbor (All candidates fail Relevance Gate -> UNMAPPED)
17. One valid + multiple invalid candidates (Only valid candidate accepted)
18. One-to-many (Single source independently verified by multiple valid targets)
19. Many-to-one (Multiple user stories tracing to single consolidated core service)
20. Genuinely unmapped (No downstream artifact exists -> UNMAPPED)
21. Unresolved meeting statement (Discussed but did not define -> UNMAPPED)
22. Unsupported change request (New unsupported feature delta -> UNMAPPED)

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
    evaluate_actor_alignment,
    evaluate_context_alignment,
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


def run_all_22_adversarial_tests():
    print("\n" + SEP)
    print("  REQVISION AI — PHASE 3 COMPLETE 22-CASE ADVERSARIAL SUITE")
    print(f"  Model: {engine.model_name}")
    print(f"  Available: {engine.is_available()}")
    print(SEP)

    if not engine.is_available():
        print("\n⚠ Semantic engine not available — cannot run semantic tests.")
        return False

    all_passed = True

    # ── CASE 1: PARAPHRASE ───────────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 1 — Paraphrase (different wording, same meaning)")
    a = "Users can cancel a booking."
    b = "Passengers may revoke their reservation."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.20, set())
    act_score, _ = evaluate_action_alignment(a, b)
    passed = check("Semantic similarity > 0.55", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Passes Relevance Gate", is_rel)
    passed &= check("Action alignment recognized (cancel == revoke)", act_score >= 0.80)
    all_passed &= passed

    # ── CASE 2: SYNONYM ──────────────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 2 — Synonym (authenticate vs verify identity)")
    a = "Users must authenticate."
    b = "Members must verify their identity."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.20, set())
    act_score, _ = evaluate_action_alignment(a, b)
    passed = check("Semantic similarity > 0.55", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Passes Relevance Gate", is_rel)
    passed &= check("Action alignment recognized (authenticate == verify identity)", act_score >= 0.80)
    all_passed &= passed

    # ── CASE 3: DIFFERENT SENTENCE STRUCTURE ─────────────────────────────────
    print(f"\n{MINI}\nCASE 3 — Different Sentence Structure")
    a = "The platform must send an alert when a reserved vehicle is cancelled."
    b = "When a booked shuttle is cancelled, riders receive a notification."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.30, set())
    passed = check("Semantic similarity > 0.55", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Passes Relevance Gate", is_rel)
    all_passed &= passed

    # ── CASE 4: ACTIVE VS PASSIVE VOICE ──────────────────────────────────────
    print(f"\n{MINI}\nCASE 4 — Active vs Passive Voice")
    a = "Flight controllers calculate satellite orbit trajectories."
    b = "Satellite orbit trajectories are computed by mission flight controllers."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.40, set())
    passed = check("Semantic similarity > 0.65 across voice active/passive", sim is not None and sim > 0.65, f"Got: {sim:.4f}")
    passed &= check("Passes Relevance Gate", is_rel)
    all_passed &= passed

    # ── CASE 5: RELATED TOPIC / DIFFERENT ACTION ─────────────────────────────
    print(f"\n{MINI}\nCASE 5 — Related Topic / Different Action (reconcile vs refund)")
    a = "Finance staff reconcile settlement records."
    b = "Finance staff issue refunds for transactions."
    sim = engine.compute_semantic_similarity(a, b)
    act_score, act_reason = evaluate_action_alignment(a, b)
    is_rel, rel_reason = evaluate_candidate_relevance_gate(a, b, sim, 0.15, set())
    passed = check("Incompatible action rejected at Relevance Gate", not is_rel)
    all_passed &= passed

    # ── CASE 6: RELATED TOPIC / DIFFERENT OBJECT ─────────────────────────────
    print(f"\n{MINI}\nCASE 6 — Related Topic / Different Object (patient chart vs appointment reminder)")
    a = "Physicians access electronic patient medical charts."
    b = "Automated appointment reminders are dispatched to clinic visitors."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.05, set())
    passed = check("Disjoint domain objects rejected at Relevance Gate", not is_rel)
    all_passed &= passed

    # ── CASE 7: SAME OBJECT / DIFFERENT CAPABILITY ───────────────────────────
    print(f"\n{MINI}\nCASE 7 — Same Object / Different Capability (receipt capture vs duplicate check)")
    a = "The mobile application shall capture and upload digital photos of expense receipts."
    b = "Verify that uploading a duplicate receipt image flags the claim with a duplicate warning."
    sim = engine.compute_semantic_similarity(a, b)
    act_score, _ = evaluate_action_alignment(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.35, set())
    passed = check("Specialized fraud check rejected for basic photo capture", not is_rel)
    all_passed &= passed

    # ── CASE 8: MISSING CONDITION ────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 8 — Missing Condition (submit expense + upload receipt vs submit only)")
    a = "Employees can submit expenses and upload receipts."
    b = "Employees can submit expenses."
    sim = engine.compute_semantic_similarity(a, b)
    has_missing, missing_reason = detect_missing_conditions(a, b)
    passed = check("Missing secondary condition detected -> PARTIAL", has_missing)
    all_passed &= passed

    # ── CASE 9: ADDITIONAL CONDITION / EXTENSION ─────────────────────────────
    print(f"\n{MINI}\nCASE 9 — Additional Condition / Extension (pay by card or wallet)")
    a = "Students can pay with cards."
    b = "Students can pay with cards or digital wallets."
    is_ext, _ = detect_capability_extension(a, b)
    pol, _ = check_polarity_conflict(a, b)
    passed = check("Recognized as capability extension", is_ext)
    passed &= check("NOT flagged as CONFLICT", not pol)
    all_passed &= passed

    # ── CASE 10: NUMERIC CHANGE ──────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 10 — Numeric Change (5000 vs 15000 concurrent sessions)")
    a = "System supports 5000 concurrent sessions."
    b = "Platform handles 15000 simultaneous sessions."
    sim = engine.compute_semantic_similarity(a, b)
    num_res, num_reason = check_numeric_conflict(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.40, set())
    passed = check("Passes Relevance Gate", is_rel)
    passed &= check("Numeric result is MODIFIED_VALUE (not CONFLICT)", num_res == "MODIFIED_VALUE")
    all_passed &= passed

    # ── CASE 11: EXTENSION CHANNELS ──────────────────────────────────────────
    print(f"\n{MINI}\nCASE 11 — Extension Channels (email vs email + Slack)")
    a = "Send approval notifications via email."
    b = "Send approval notifications via email or Slack."
    is_ext, _ = detect_capability_extension(a, b)
    pol, _ = check_polarity_conflict(a, b)
    passed = check("Recognized as capability extension", is_ext)
    passed &= check("NOT flagged as CONFLICT", not pol)
    all_passed &= passed

    # ── CASE 12: REPLACEMENT / INCOMPATIBILITY ────────────────────────────────
    print(f"\n{MINI}\nCASE 12 — Replacement / Incompatibility (reversible encryption vs salted hash)")
    a = "Employee passwords shall be stored using reversible DES encryption."
    b = "Employee passwords shall be stored using salted PBKDF2 hashing. Reversible storage is prohibited."
    sim = engine.compute_semantic_similarity(a, b)
    pol, _ = check_polarity_conflict(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.40, set())
    passed = check("Passes Relevance Gate (same authentication capability)", is_rel)
    passed &= check("Flags CONFLICT due to incompatible security policy", pol)
    all_passed &= passed

    # ── CASE 13: NEGATION ────────────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 13 — Negation (guest checkout allowed vs prohibited)")
    a = "Guests may check out without logging in."
    b = "Guest checkout is prohibited."
    sim = engine.compute_semantic_similarity(a, b)
    pol, _ = check_polarity_conflict(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.40, set())
    passed = check("Same capability passes Relevance Gate", is_rel)
    passed &= check("Polarity conflict detected on same capability", pol)
    all_passed &= passed

    # ── CASE 14: ACTUAL CONTRADICTION ────────────────────────────────────────
    print(f"\n{MINI}\nCASE 14 — Actual Contradiction (mandatory vs optional biometric auth)")
    a = "Biometric facial authentication is mandatory for login."
    b = "Biometric facial authentication is prohibited for login."
    sim = engine.compute_semantic_similarity(a, b)
    pol, _ = check_polarity_conflict(a, b)
    passed = check("Mandatory vs Prohibited detected as CONFLICT", pol)
    all_passed &= passed

    # ── CASE 15: AMBIGUOUS CANDIDATE ─────────────────────────────────────────
    print(f"\n{MINI}\nCASE 15 — Ambiguous Candidate (score margin < 0.04)")
    c1 = {"cand": {"text": "Reduce refund processing time."}, "composite_score": 0.52, "hybrid": 0.52, "sem_score": 0.55, "lex_score": 0.30, "intent_val": 0.0, "action_score": 0.7, "entity_score": 0.7, "has_missing": False, "missing_reason": "", "is_extension": False, "extension_reason": "", "num_result": "NONE", "num_reason": "", "evidence": "", "shared_intents": set()}
    c2 = {"cand": {"text": "Expand refund eligibility."}, "composite_score": 0.51, "hybrid": 0.51, "sem_score": 0.54, "lex_score": 0.30, "intent_val": 0.0, "action_score": 0.7, "entity_score": 0.7, "has_missing": False, "missing_reason": "", "is_extension": False, "extension_reason": "", "num_result": "NONE", "num_reason": "", "evidence": "", "shared_intents": set()}
    ranked = rank_and_disambiguate_candidates([c1, c2], min_match_threshold=0.45, ambiguity_margin=0.04)
    passed = check("Close candidates flagged as ambiguous -> PARTIAL", ranked[0].get("is_ambiguous") is True and ranked[0].get("status") == "PARTIAL")
    all_passed &= passed

    # ── CASE 16: WEAK NEAREST NEIGHBOR ───────────────────────────────────────
    print(f"\n{MINI}\nCASE 16 — Weak Nearest Neighbor (all candidates fail gate -> UNMAPPED)")
    src = "Calculate travel cost estimates before booking."
    cands = [
        "Issue refunds for cancelled trips.",
        "Store employee profile pictures.",
        "Configure LDAP active directory integration."
    ]
    surviving = [c for c in cands if evaluate_candidate_relevance_gate(src, c, engine.compute_semantic_similarity(src, c), 0.05, set())[0]]
    passed = check("All weak candidates rejected -> 0 surviving", len(surviving) == 0)
    all_passed &= passed

    # ── CASE 17: ONE VALID + MULTIPLE INVALID CANDIDATES ─────────────────────
    print(f"\n{MINI}\nCASE 17 — One Valid + Multiple Invalid Candidates")
    src = "Employees can withdraw a pending travel request."
    c_val = "Verify that an employee can withdraw a pending travel request and release booking holds."
    c_inv1 = "Verify that uploading a duplicate receipt image flags duplicate warning."
    c_inv2 = "Verify that database connection pool supports 100 connections."
    is_val, _ = evaluate_candidate_relevance_gate(src, c_val, engine.compute_semantic_similarity(src, c_val), 0.40, set())
    is_inv1, _ = evaluate_candidate_relevance_gate(src, c_inv1, engine.compute_semantic_similarity(src, c_inv1), 0.05, set())
    is_inv2, _ = evaluate_candidate_relevance_gate(src, c_inv2, engine.compute_semantic_similarity(src, c_inv2), 0.05, set())
    passed = check("Valid candidate accepted", is_val)
    passed &= check("All invalid candidates rejected", not is_inv1 and not is_inv2)
    all_passed &= passed

    # ── CASE 18: ONE-TO-MANY ─────────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 18 — One-to-Many Independent Valid Targets")
    src = "The system shall support student fee payments."
    t1 = "Implement student credit card payment checkout."
    t2 = "Implement net banking payment checkout for students."
    is_t1, _ = evaluate_candidate_relevance_gate(src, t1, engine.compute_semantic_similarity(src, t1), 0.35, set())
    is_t2, _ = evaluate_candidate_relevance_gate(src, t2, engine.compute_semantic_similarity(src, t2), 0.35, set())
    passed = check("Both independent payment targets pass relevance gate", is_t1 and is_t2)
    all_passed &= passed

    # ── CASE 19: MANY-TO-ONE ─────────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 19 — Many-to-One Consolidation")
    s1 = "As a student, I want to pay tuition online."
    s2 = "As a parent, I want to pay course fees online."
    t_shared = "Implement payment gateway checkout service for student tuition and course fee invoices."
    is_s1, _ = evaluate_candidate_relevance_gate(s1, t_shared, engine.compute_semantic_similarity(s1, t_shared), 0.35, set())
    is_s2, _ = evaluate_candidate_relevance_gate(s2, t_shared, engine.compute_semantic_similarity(s2, t_shared), 0.35, set())
    passed = check("Both stories independently map to consolidated service", is_s1 and is_s2)
    all_passed &= passed

    # ── CASE 20: GENUINELY UNMAPPED ──────────────────────────────────────────
    print(f"\n{MINI}\nCASE 20 — Genuinely Unmapped Artifact (no downstream realization)")
    src = "Export satellite structural blueprints to microfiche film for national space museum archives."
    spec = "Implement SGP4 two-line element satellite orbit propagation REST API."
    sim = engine.compute_semantic_similarity(src, spec)
    is_rel, _ = evaluate_candidate_relevance_gate(src, spec, sim, 0.05, set())
    passed = check("Unmapped microfiche archive rejected -> UNMAPPED", not is_rel)
    all_passed &= passed

    # ── CASE 21: UNRESOLVED MEETING STATEMENT ────────────────────────────────
    print(f"\n{MINI}\nCASE 21 — Unresolved Meeting Statement (consensus not agreed)")
    src = "The team discussed laser optical crosslink bandwidth upgrades but did not define technical specifications."
    spec = "The telemetry ingestion service shall unpack CCSDS telemetry frames in real time."
    sim = engine.compute_semantic_similarity(src, spec)
    is_rel, _ = evaluate_candidate_relevance_gate(src, spec, sim, 0.20, set())
    passed = check("Unresolved review statement excluded from mapping -> UNMAPPED", not is_rel)
    all_passed &= passed

    # ── CASE 22: UNSUPPORTED CHANGE REQUEST ──────────────────────────────────
    print(f"\n{MINI}\nCASE 22 — Unsupported Change Request (new unsupported delta)")
    src = "Install an automated commercial espresso brewing machine and bean grinder in the mission control center breakroom."
    spec = "The flight commanding audit service shall write append-only cryptographic log records."
    sim = engine.compute_semantic_similarity(src, spec)
    is_rel, _ = evaluate_candidate_relevance_gate(src, spec, sim, 0.05, set())
    passed = check("Breakroom espresso change request rejected -> UNMAPPED", not is_rel)
    all_passed &= passed

    # ── FINAL SUMMARY ────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    if all_passed:
        print("🎉 ALL 22 ADVERSARIAL CASES PASSED")
    else:
        print("❌ SOME ADVERSARIAL CASES FAILED — review output above")
    print(SEP)
    return all_passed


if __name__ == "__main__":
    success = run_all_22_adversarial_tests()
    sys.exit(0 if success else 1)
