"""
ReqVision AI — Phase 3 Final 28-Principle Adversarial Semantic Suite.

Verifies the Complete Generic Capability Reasoning & Anti-Hallucination Pipeline across all 28 principles:
 1. Paraphrase (Cancel booking vs Revoke reservation)
 2. Synonym (Authenticate vs Verify identity)
 3. Active/Passive Voice (Flight controllers calculate orbits vs Orbits computed by controllers)
 4. Reordered Wording (Platform sends alert when vehicle cancelled vs When shuttle cancelled send notification)
 5. Low Lexical / High Semantic (Terminate user access vs Close member session)
 6. Same Topic / Different Action (Reconcile settlement vs Refund transactions)
 7. Same Action / Different Object (Update vehicle coordinates vs Update driver payroll profile)
 8. Same Object / Different Action (Receipt photo upload vs Duplicate receipt fraud check)
 9. Missing Condition (Submit expenses & upload receipts vs Submit expenses only -> PARTIAL)
10. Additional Condition (Pay with card vs Pay with card or digital wallet -> MATCHED Extended)
11. Quantitative Change (5000 concurrent sessions vs 15000 simultaneous sessions -> MODIFIED_VALUE)
12. Extension (Email alert vs Email or Slack notification -> MATCHED Extended)
13. True Contradiction (Reversible XOR encryption vs Salted Argon2id hashing -> CONFLICT)
14. Defensive Validation (Reject invalid request vs Block invalid request -> MATCHED, NOT CONFLICT)
15. Ambiguous Candidates (Score margin < 0.04 -> PARTIAL Ambiguous)
16. Weak Nearest Neighbor (All weak candidates fail Relevance Gate -> UNMAPPED)
17. One Strong + Weak Distractors (Selects exact target and discards distractors)
18. One-to-Many (Single requirement independently satisfied by multiple valid targets)
19. Many-to-One (Multiple user stories independently mapping to consolidated service)
20. Genuinely Unmapped (Export blueprints to microfiche -> UNMAPPED)
21. Unsupported New Capability (Install breakroom espresso station -> UNMAPPED)
22. NFR with No Downstream Representation (API p99 latency < 1.2s vs user receiving claim status -> REJECTED)
23. Unresolved Meeting Statement (Discussed faster approvals but did not define specs -> UNMAPPED)
24. Physical Operational Request (Procure 25 motorized standing desks -> UNMAPPED)
25. Exact Capability Match (Identical core capability passes with High confidence)
26. Role-Sensitive Capability (Mechanic maintenance work order vs Driver dispatch route)
27. Context-Sensitive Capability (Cancel before departure vs Cancel during active delivery)
28. Same Domain / Unrelated Capability (Vehicle telemetry tracking vs Driver payroll accounting)

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


def run_all_28_adversarial_tests():
    print("\n" + SEP)
    print("  REQVISION AI — PHASE 3 COMPLETE 28-PRINCIPLE ADVERSARIAL SUITE")
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

    # ── CASE 3: ACTIVE / PASSIVE VOICE ───────────────────────────────────────
    print(f"\n{MINI}\nCASE 3 — Active / Passive Voice")
    a = "Flight controllers calculate satellite orbit parameters."
    b = "Satellite orbit parameters are computed by flight controllers."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.50, set())
    passed = check("Semantic similarity > 0.65 across active/passive", sim is not None and sim > 0.65, f"Got: {sim:.4f}")
    passed &= check("Passes Relevance Gate", is_rel)
    all_passed &= passed

    # ── CASE 4: REORDERED WORDING ────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 4 — Reordered Wording")
    a = "The platform must send an alert when a reserved vehicle is cancelled."
    b = "When a booked shuttle is cancelled, riders receive a notification."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.20, set())
    passed = check("Semantic similarity > 0.55", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Passes Relevance Gate", is_rel)
    all_passed &= passed

    # ── CASE 5: LOW LEXICAL / HIGH SEMANTIC ──────────────────────────────────
    print(f"\n{MINI}\nCASE 5 — Low Lexical / High Semantic")
    a = "Terminate user access session."
    b = "Close active member login credentials."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.05, set())
    passed = check("High semantic (>0.50) despite near-zero lexical", sim is not None and sim > 0.50, f"Got: {sim:.4f}")
    passed &= check("Passes Relevance Gate on semantic strength", is_rel)
    all_passed &= passed

    # ── CASE 6: SAME TOPIC / DIFFERENT ACTION ────────────────────────────────
    print(f"\n{MINI}\nCASE 6 — Same Topic / Different Action (reconcile vs refund)")
    a = "Finance staff reconcile daily bank settlement feeds against ledger entries."
    b = "Finance staff issue refunds to customers for disputed transactions."
    sim = engine.compute_semantic_similarity(a, b)
    act_score, _ = evaluate_action_alignment(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.20, set())
    passed = check("Incompatible action rejected at Relevance Gate", not is_rel or act_score <= 0.10)
    all_passed &= passed

    # ── CASE 7: SAME ACTION / DIFFERENT OBJECT ───────────────────────────────
    print(f"\n{MINI}\nCASE 7 — Same Action / Different Object (telemetry vs payroll)")
    a = "The system shall update real-time vehicle GPS coordinates on the dispatch map."
    b = "The system shall update driver bank direct deposit payroll information."
    ent_score, _ = evaluate_entity_alignment(a, b)
    passed = check("Disjoint domain entities rejected (entity score <= 0.10)", ent_score <= 0.10)
    all_passed &= passed

    # ── CASE 8: SAME OBJECT / DIFFERENT ACTION ───────────────────────────────
    print(f"\n{MINI}\nCASE 8 — Same Object / Different Action (photo upload vs duplicate check)")
    a = "The mobile app shall capture and upload digital photos of vehicle damage."
    b = "The fraud engine shall compute perceptual hashes to detect duplicate photos."
    act_score, _ = evaluate_action_alignment(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, 0.55, 0.20, set())
    passed = check("Specialized fraud check rejected for basic photo capture", act_score <= 0.10 or not is_rel)
    all_passed &= passed

    # ── CASE 9: MISSING CONDITION ────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 9 — Missing Condition (submit expense + upload receipt vs submit only)")
    src = "Employees shall submit travel expense reports and upload itemized receipts."
    tgt = "Employees shall submit travel expense reports."
    has_missing, reason = detect_missing_conditions(src, tgt)
    passed = check("Missing secondary condition detected -> PARTIAL", has_missing)
    all_passed &= passed

    # ── CASE 10: ADDITIONAL CONDITION ────────────────────────────────────────
    print(f"\n{MINI}\nCASE 10 — Additional Condition (pay by card or wallet)")
    src = "Users may pay by credit card."
    tgt = "Users may pay by credit card or digital wallet."
    is_ext, _ = detect_capability_extension(src, tgt)
    pol_conflict, _ = check_polarity_conflict(src, tgt)
    passed = check("Recognized as capability extension", is_ext)
    passed &= check("NOT flagged as CONFLICT", not pol_conflict)
    all_passed &= passed

    # ── CASE 11: QUANTITATIVE CHANGE ─────────────────────────────────────────
    print(f"\n{MINI}\nCASE 11 — Quantitative Change (5000 vs 15000 concurrent sessions)")
    a = "The system shall support 5000 concurrent sessions."
    b = "The platform handles 15000 simultaneous sessions."
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.40, set())
    num_status, reason = check_numeric_conflict(a, b)
    passed = check("Passes Relevance Gate", is_rel)
    passed &= check("Numeric result is MODIFIED_VALUE (not CONFLICT)", num_status == "MODIFIED_VALUE", reason)
    all_passed &= passed

    # ── CASE 12: EXTENSION ───────────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 12 — Extension Channels (email vs email + Slack)")
    src = "System shall send email notification when vehicle dispatch is cancelled."
    tgt = "System shall send email or Slack notification when vehicle dispatch is cancelled."
    is_ext, _ = detect_capability_extension(src, tgt)
    pol_conflict, _ = check_polarity_conflict(src, tgt)
    passed = check("Recognized as capability extension", is_ext)
    passed &= check("NOT flagged as CONFLICT", not pol_conflict)
    all_passed &= passed

    # ── CASE 13: TRUE CONTRADICTION ──────────────────────────────────────────
    print(f"\n{MINI}\nCASE 13 — True Contradiction (reversible encryption vs salted hash)")
    a = "Driver authentication PINs shall be stored using reversible Caesar encryption."
    b = "Driver PINs shall be stored using salted PBKDF2 cryptographic hashing; reversible storage is prohibited."
    pol_conflict, reason = check_polarity_conflict(a, b)
    sim = engine.compute_semantic_similarity(a, b)
    is_rel, _ = evaluate_candidate_relevance_gate(a, b, sim, 0.20, set())
    passed = check("Passes Relevance Gate (same authentication capability)", is_rel)
    passed &= check("Flags CONFLICT due to incompatible security policy", pol_conflict, reason)
    all_passed &= passed

    # ── CASE 14: DEFENSIVE VALIDATION ────────────────────────────────────────
    print(f"\n{MINI}\nCASE 14 — Defensive Security Validation (Reject vs Block)")
    src = "The system shall reject invalid payment requests."
    tgt = "Verify that invalid payment requests are blocked by the gateway."
    sim = engine.compute_semantic_similarity(src, tgt)
    pol, _ = check_polarity_conflict(src, tgt)
    is_rel, _ = evaluate_candidate_relevance_gate(src, tgt, sim, 0.40, set())
    passed = check("Defensive validation passes Relevance Gate", is_rel)
    passed &= check("Reject vs Block on invalid input is NOT marked as CONFLICT", not pol)
    all_passed &= passed

    # ── CASE 15: AMBIGUOUS CANDIDATES ────────────────────────────────────────
    print(f"\n{MINI}\nCASE 15 — Ambiguous Candidates (score margin < 0.04)")
    candidates = [
        {"target_id": "FS-201", "composite_score": 0.52, "evidence": "Candidate A", "capability_profile": {}},
        {"target_id": "FS-202", "composite_score": 0.51, "evidence": "Candidate B", "capability_profile": {}},
    ]
    accepted = rank_and_disambiguate_candidates(candidates)
    is_ambiguous = any(c.get("disambiguated_status") == "PARTIAL" for c in accepted)
    passed = check("Close candidates flagged as ambiguous -> PARTIAL", is_ambiguous)
    all_passed &= passed

    # ── CASE 16: WEAK NEAREST NEIGHBOR ───────────────────────────────────────
    print(f"\n{MINI}\nCASE 16 — Weak Nearest Neighbor (all candidates fail gate -> UNMAPPED)")
    src = "Calculate automated vehicle damage repair cost estimates."
    distractors = [
        "Store employee emergency contact next of kin phone numbers in database.",
        "Implement cafeteria weekly meal scheduling module.",
        "Send marketing promotional push notifications to inactive users."
    ]
    surviving = []
    for d in distractors:
        sim = engine.compute_semantic_similarity(src, d)
        is_rel, _ = evaluate_candidate_relevance_gate(src, d, sim, 0.05, set())
        if is_rel:
            surviving.append(d)
    passed = check("All weak candidates rejected -> 0 surviving", len(surviving) == 0)
    all_passed &= passed

    # ── CASE 17: ONE STRONG + WEAK DISTRACTORS ───────────────────────────────
    print(f"\n{MINI}\nCASE 17 — One Strong Target vs Multiple Weak Distractors")
    src = "The dispatcher may withdraw a pending vehicle reservation."
    valid_tgt = "Endpoint POST /api/reservations/withdraw releases vehicle allocation."
    invalid_1 = "Image hashing worker checks for duplicate uploaded photos."
    invalid_2 = "Backup database daily at 02:00 UTC."
    is_v, _ = evaluate_candidate_relevance_gate(src, valid_tgt, engine.compute_semantic_similarity(src, valid_tgt), 0.35, set())
    is_i1, _ = evaluate_candidate_relevance_gate(src, invalid_1, engine.compute_semantic_similarity(src, invalid_1), 0.05, set())
    is_i2, _ = evaluate_candidate_relevance_gate(src, invalid_2, engine.compute_semantic_similarity(src, invalid_2), 0.05, set())
    passed = check("Valid candidate accepted", is_v)
    passed &= check("All invalid candidates rejected", not is_i1 and not is_i2)
    all_passed &= passed

    # ── CASE 18: ONE-TO-MANY ─────────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 18 — One-to-Many Independent Valid Targets")
    src = "The portal shall process student tuition fee payments."
    tgt_1 = "Implement credit card fee payment processing gateway."
    tgt_2 = "Implement automated bank debit fee payment worker."
    is_1, _ = evaluate_candidate_relevance_gate(src, tgt_1, engine.compute_semantic_similarity(src, tgt_1), 0.40, set())
    is_2, _ = evaluate_candidate_relevance_gate(src, tgt_2, engine.compute_semantic_similarity(src, tgt_2), 0.40, set())
    passed = check("Both independent payment targets pass relevance gate", is_1 and is_2)
    all_passed &= passed

    # ── CASE 19: MANY-TO-ONE ─────────────────────────────────────────────────
    print(f"\n{MINI}\nCASE 19 — Many-to-One Consolidation")
    story_1 = "As a student I want to pay tuition online via card."
    story_2 = "As a parent I want to pay tuition online via bank debit."
    spec = "Implement unified bursar tuition payment gateway supporting cards and bank debits."
    is_s1, _ = evaluate_candidate_relevance_gate(story_1, spec, engine.compute_semantic_similarity(story_1, spec), 0.40, set())
    is_s2, _ = evaluate_candidate_relevance_gate(story_2, spec, engine.compute_semantic_similarity(story_2, spec), 0.40, set())
    passed = check("Both stories independently map to consolidated service", is_s1 and is_s2)
    all_passed &= passed

    # ── CASE 20: GENUINELY UNMAPPED ──────────────────────────────────────────
    print(f"\n{MINI}\nCASE 20 — Genuinely Unmapped Artifact (no downstream realization)")
    src = "Export vehicle chassis engineering schematics to 35mm microfiche film."
    spec = "Real-time telematics MQTT broker ingests vehicle speed and GPS location."
    sim = engine.compute_semantic_similarity(src, spec)
    is_rel, _ = evaluate_candidate_relevance_gate(src, spec, sim, 0.05, set())
    passed = check("Unmapped microfiche archive rejected -> UNMAPPED", not is_rel)
    all_passed &= passed

    # ── CASE 21: UNSUPPORTED NEW CAPABILITY ──────────────────────────────────
    print(f"\n{MINI}\nCASE 21 — Unsupported Change Request (new unsupported delta)")
    src = "Install an automated commercial espresso brewing machine and bean grinder in breakroom."
    spec = "The flight commanding audit service shall write append-only cryptographic log records."
    sim = engine.compute_semantic_similarity(src, spec)
    is_rel, _ = evaluate_candidate_relevance_gate(src, spec, sim, 0.05, set())
    passed = check("Breakroom espresso change request rejected -> UNMAPPED", not is_rel)
    all_passed &= passed

    # ── CASE 22: NFR WITH NO DOWNSTREAM REPRESENTATION ───────────────────────
    print(f"\n{MINI}\nCASE 22 — NFR with No Downstream Implementation")
    src = "The core API shall achieve p99 response latency under 1200 milliseconds."
    tgt = "User receives an email confirmation when claim status transitions to approved."
    sim = engine.compute_semantic_similarity(src, tgt)
    is_rel, _ = evaluate_candidate_relevance_gate(src, tgt, sim, 0.05, set())
    passed = check("NFR latency constraint rejected for unrelated functional notification", not is_rel)
    all_passed &= passed

    # ── CASE 23: UNRESOLVED MEETING STATEMENT ────────────────────────────────
    print(f"\n{MINI}\nCASE 23 — Unresolved Meeting Statement (discussed but not decided)")
    src = "The team discussed adding optical inter-satellite communication links but did not define technical specifications."
    spec = "Implement S-band radio telemetry receiver module."
    sim = engine.compute_semantic_similarity(src, spec)
    is_rel, _ = evaluate_candidate_relevance_gate(src, spec, sim, 0.40, set())
    passed = check("Unresolved review statement excluded from mapping -> UNMAPPED", not is_rel)
    all_passed &= passed

    # ── CASE 24: PHYSICAL OPERATIONAL REQUEST ────────────────────────────────
    print(f"\n{MINI}\nCASE 24 — Physical Operational Request (furniture procurement)")
    src = "Procure and install 25 motorized ergonomic standing desks for dispatchers."
    spec = "Implement bank payout reconciliation worker parsing NACHA settlement feeds."
    sim = engine.compute_semantic_similarity(src, spec)
    is_rel, _ = evaluate_candidate_relevance_gate(src, spec, sim, 0.05, set())
    passed = check("Physical furniture procurement decision rejected -> UNMAPPED", not is_rel)
    all_passed &= passed

    # ── CASE 25: EXACT CAPABILITY MATCH ──────────────────────────────────────
    print(f"\n{MINI}\nCASE 25 — Exact Capability Match")
    src = "The system shall calculate automated vehicle damage repair cost estimates based on insurance policy coverage limits."
    tgt = "The estimation engine shall compute projected claim payout amounts by applying deductible schedules and insurance policy limits."
    sim = engine.compute_semantic_similarity(src, tgt)
    is_rel, _ = evaluate_candidate_relevance_gate(src, tgt, sim, 0.50, set())
    passed = check("Semantic similarity > 0.55 for exact capability match", sim is not None and sim > 0.55, f"Got: {sim:.4f}")
    passed &= check("Exact capability match passes Relevance Gate", is_rel)
    all_passed &= passed

    # ── CASE 26: ROLE-SENSITIVE CAPABILITY ───────────────────────────────────
    print(f"\n{MINI}\nCASE 26 — Role-Sensitive Capability (Mechanic vs Driver)")
    src = "As a certified maintenance mechanic, I want to execute vehicle repair work orders."
    tgt_mech = "Verify that certified mechanic role can update repair work order status."
    tgt_driver = "Verify that delivery driver can view daily route dispatch assignment."
    is_mech, _ = evaluate_candidate_relevance_gate(src, tgt_mech, engine.compute_semantic_similarity(src, tgt_mech), 0.45, set())
    is_driver, _ = evaluate_candidate_relevance_gate(src, tgt_driver, engine.compute_semantic_similarity(src, tgt_driver), 0.10, set())
    passed = check("Mechanic maintenance test passes Relevance Gate", is_mech)
    passed &= check("Driver dispatch test rejected due to actor/action divergence", not is_driver)
    all_passed &= passed

    # ── CASE 27: CONTEXT-SENSITIVE CAPABILITY ────────────────────────────────
    print(f"\n{MINI}\nCASE 27 — Context-Sensitive Capability (Before departure vs In-transit)")
    src = "Dispatchers may cancel a vehicle dispatch before the driver departs the depot."
    tgt = "POST /api/dispatches/{id}/cancel is permitted only when status is PENDING_DEPARTURE."
    sim = engine.compute_semantic_similarity(src, tgt)
    is_rel, _ = evaluate_candidate_relevance_gate(src, tgt, sim, 0.40, set())
    passed = check("Pre-departure cancellation passes Relevance Gate", is_rel)
    all_passed &= passed

    # ── CASE 28: SAME DOMAIN / UNRELATED CAPABILITY ──────────────────────────
    print(f"\n{MINI}\nCASE 28 — Same Domain / Unrelated Capability (Telemetry vs Payroll)")
    src = "Track real-time GPS coordinates and speed for active delivery fleet."
    tgt = "Calculate monthly payroll tax deductions for delivery fleet drivers."
    sim = engine.compute_semantic_similarity(src, tgt)
    is_rel, _ = evaluate_candidate_relevance_gate(src, tgt, sim, 0.15, set())
    passed = check("Telemetry tracking rejected for payroll calculation", not is_rel)
    all_passed &= passed

    # ── FINAL SUMMARY ────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    if all_passed:
        print("🎉 ALL 28 ADVERSARIAL CASES PASSED")
    else:
        print("❌ SOME ADVERSARIAL CASES FAILED — review output above")
    print(SEP)
    return all_passed


if __name__ == "__main__":
    success = run_all_28_adversarial_tests()
    sys.exit(0 if success else 1)
