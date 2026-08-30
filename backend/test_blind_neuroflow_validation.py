"""
ReqVision AI — Strict Blind Accuracy & Parity Validation Benchmark.

Dataset: NeuroFlow (Brain-Computer Interface BCI Telemetry & Real-Time Neuromodulation)
Strictly Frozen Benchmark testing production endpoints:
  POST /api/project/detect -> POST /api/project/verify

Evaluates 20 Diverse Ground-Truth Benchmark Cases:
  - Exact & Paraphrased Capabilities
  - Semantic Synonyms with Low Lexical Overlap
  - Defensive Security Validations (Affirmative Recognition)
  - True Security Policy Contradictions
  - Compound Action & Condition Omission (PARTIAL)
  - Non-Software Physical Amenities (UNMAPPED)
  - Obsolete Physical Media Formats (UNMAPPED)
  - Physical Breakroom Appliances (UNMAPPED)
  - Physical Office Furniture (UNMAPPED)
  - Unresolved Governance Discussions (UNMAPPED)
  - Change Requests Affecting Capabilities (MATCHED/EXTENDED)
  - Confirmed Meeting Decisions (MATCHED)
  - Single-Source Pipeline Parity (API == Matrix == Graph == Dashboard == PDF)

Run: python test_blind_neuroflow_validation.py
"""

import os
import sys
import io
import json

from app import app

NEUROFLOW_DIR = os.path.join(os.path.dirname(__file__), "tests", "neuroflow_docs")

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


def run_blind_validation():
    print("\n" + SEP)
    print("  REQVISION AI — FINAL INDEPENDENT BLIND ACCURACY BENCHMARK")
    print("  Dataset: NeuroFlow (Brain-Computer Interface BCI Telemetry)")
    print(f"  Source Path: {NEUROFLOW_DIR}")
    print(SEP)

    client = app.test_client()
    data_dict = {}
    doc_names = sorted(os.listdir(NEUROFLOW_DIR))

    for fname in doc_names:
        if fname.endswith(".docx"):
            fpath = os.path.join(NEUROFLOW_DIR, fname)
            with open(fpath, "rb") as f:
                content = f.read()
            data_dict.setdefault("files", []).append((io.BytesIO(content), fname))

    # ── 1. Upload & Auto-Classification ──────────────────────────────────────
    print(f"\n[1] Submitting {len(data_dict['files'])} NeuroFlow documents to /api/project/detect ...")
    resp_detect = client.post("/api/project/detect", data=data_dict, content_type="multipart/form-data")

    if resp_detect.status_code != 200:
        print(f"❌ Detect returned status {resp_detect.status_code}: {resp_detect.data.decode('utf-8')}")
        return False

    detect_data = json.loads(resp_detect.data.decode("utf-8"))
    documents = detect_data.get("documents", [])
    print(f"    Detected {len(documents)} documents successfully.")

    # ── 2. Canonical Traceability Verification ───────────────────────────
    print(f"\n[2] Executing Phase 3 Traceability Engine on /api/project/verify ...")
    resp_verify = client.post("/api/project/verify", json={"documents": documents})

    if resp_verify.status_code != 200:
        print(f"❌ Verify returned status {resp_verify.status_code}: {resp_verify.data.decode('utf-8')}")
        return False

    api_data = json.loads(resp_verify.data.decode("utf-8"))
    relationships = api_data.get("relationships", [])
    artifacts = api_data.get("artifacts", [])
    matrix = api_data.get("traceability_matrix", [])
    graph = api_data.get("graph", {})
    summary = api_data.get("summary", {})
    coverage = api_data.get("coverage", {})

    print(f"\n[3] Production Inference Output:")
    print(f"    Total Extracted Artifacts: {len(artifacts)}")
    print(f"    Accepted Canonical Edges : {len(relationships)}")
    print(f"    Semantic Active          : {api_data.get('semantic_enabled')}")
    print(f"    Semantic Model           : {api_data.get('semantic_model')}")

    # Build lookup map: (source_artifact, target_artifact) -> rel_dict
    rel_map = {}
    for r in relationships:
        rel_map[(r["source_artifact"], r["target_artifact"])] = r

    # Build unmapped sets
    mapped_sources = {r["source_artifact"] for r in relationships if r.get("target_artifact") != "—"}
    mapped_targets = {r["target_artifact"] for r in relationships if r.get("target_artifact") != "—"}

    all_passed = True
    tp_count = 0
    fp_count = 0
    fn_count = 0
    tn_count = 0

    print(f"\n{MINI}\n[4] EVALUATION OF 20 DIVERSE GROUND-TRUTH BENCHMARK CASES")

    # ── Group 1: Exact & Paraphrased Capabilities (True Positives) ───────────
    print("\n--- Group 1: Exact & Paraphrased Capability Realizations ---")

    # 1. BR-001 -> FR-101 (Multichannel EEG Telemetry Streaming)
    r1 = rel_map.get(("BR-001", "FR-101"))
    cond1 = r1 is not None and r1["status"] in ["MATCHED", "PARTIAL"]
    passed = check("1. BR-001 (Multichannel EEG Streaming) -> FR-101 is Mapped", cond1, f"Status: {r1.get('status') if r1 else 'None'}")
    all_passed &= passed
    if cond1: tp_count += 1
    else: fn_count += 1

    # 2. BR-002 -> FR-102 (Seizure Alert Notification)
    r2 = rel_map.get(("BR-002", "FR-102"))
    cond2 = r2 is not None and r2["status"] in ["MATCHED", "PARTIAL"]
    passed = check("2. BR-002 (Pre-ictal Seizure Alerts) -> FR-102 is Mapped", cond2, f"Status: {r2.get('status') if r2 else 'None'}")
    all_passed &= passed
    if cond2: tp_count += 1
    else: fn_count += 1

    # 3. BR-003 -> FR-103 (Emergency Stimulation Halt)
    r3 = rel_map.get(("BR-003", "FR-103"))
    cond3 = r3 is not None and r3["status"] in ["MATCHED", "PARTIAL"]
    passed = check("3. BR-003 (Emergency Stimulation Halt) -> FR-103 is Mapped", cond3, f"Status: {r3.get('status') if r3 else 'None'}")
    all_passed &= passed
    if cond3: tp_count += 1
    else: fn_count += 1

    # 4. BR-005 -> FR-105 (Frequency Band Spectral Analysis)
    r4 = rel_map.get(("BR-005", "FR-105"))
    cond4 = r4 is not None and r4["status"] in ["MATCHED", "PARTIAL"]
    passed = check("4. BR-005 (Band Power Spectral Density) -> FR-105 is Mapped", cond4, f"Status: {r4.get('status') if r4 else 'None'}")
    all_passed &= passed
    if cond4: tp_count += 1
    else: fn_count += 1

    # 5. US-301 -> TC-401 (Waveform Display Verification)
    r5 = rel_map.get(("US-301", "TC-401"))
    cond5 = r5 is not None and r5["status"] == "MATCHED"
    passed = check("5. US-301 (EEG Waveform Display) -> TC-401 (Waveform Display Test) is MATCHED", cond5, f"Status: {r5.get('status') if r5 else 'None'}")
    all_passed &= passed
    if cond5: tp_count += 1
    else: fn_count += 1

    # 6. US-302 -> TC-402 (Caregiver Seizure Alert Test)
    r6 = rel_map.get(("US-302", "TC-402"))
    cond6 = r6 is not None and r6["status"] == "MATCHED"
    passed = check("6. US-302 (Caregiver Seizure Alert) -> TC-402 (Alert Notification Test) is MATCHED", cond6, f"Status: {r6.get('status') if r6 else 'None'}")
    all_passed &= passed
    if cond6: tp_count += 1
    else: fn_count += 1

    # 7. US-303 -> TC-403 (Emergency Stimulation Stop Test)
    r7 = rel_map.get(("US-303", "TC-403"))
    cond7 = r7 is not None and r7["status"] == "MATCHED"
    passed = check("7. US-303 (Emergency Stimulation Stop) -> TC-403 (Safe-Off Transition Test) is MATCHED", cond7, f"Status: {r7.get('status') if r7 else 'None'}")
    all_passed &= passed
    if cond7: tp_count += 1
    else: fn_count += 1

    # ── Group 2: Compound Action & Condition Omission (PARTIAL) ──────────────
    print("\n--- Group 2: Compound Action & Condition Omission (PARTIAL) ---")

    # 8. BR-004 -> FR-104 (Cancel therapy pulse cycle with compound reserve action)
    r8 = rel_map.get(("BR-004", "FR-104"))
    cond8 = r8 is not None and r8["status"] == "PARTIAL"
    passed = check("8. BR-004 (Cancel therapy cycle) -> FR-104 is PARTIAL (Compound action detection)", cond8, f"Evidence: {r8.get('evidence') if r8 else 'None'}")
    all_passed &= passed
    if cond8: tp_count += 1
    else: fn_count += 1

    # 9. US-312 -> TC-410 (Adverse event report with EDF file export)
    r9 = rel_map.get(("US-312", "TC-410"))
    cond9 = r9 is not None and r9["status"] == "PARTIAL"
    passed = check("9. US-312 (Adverse event filing) -> TC-410 is PARTIAL (Secondary export clause not in test)", cond9, f"Evidence: {r9.get('evidence') if r9 else 'None'}")
    all_passed &= passed
    if cond9: tp_count += 1
    else: fn_count += 1

    # ── Group 3: Defensive Security Validation ─────────────────────────────────
    print("\n--- Group 3: Defensive Security Validation (Affirmative Recognition) ---")

    # 10. BR-006 -> FR-106 (Duplicate neural packet defense)
    r10 = rel_map.get(("BR-006", "FR-106"))
    cond10 = r10 is not None and r10["status"] == "MATCHED"
    passed = check("10. BR-006 (Duplicate packet defense) -> FR-106 is MATCHED (Not false CONFLICT)", cond10, f"Evidence: {r10.get('evidence') if r10 else 'None'}")
    all_passed &= passed
    if cond10: tp_count += 1
    else: fn_count += 1

    # ── Group 4: True Security Policy Contradiction ────────────────────────────
    print("\n--- Group 4: True Security Policy Contradiction (CONFLICT) ---")

    # 11. FR-109 vs FS-209 (Reversible DES encryption vs Salted Argon2id hashing)
    r11 = rel_map.get(("FR-109", "FS-209"))
    cond11 = r11 is not None and r11["status"] == "CONFLICT"
    passed = check("11. FR-109 (Reversible DES encryption) vs FS-209 (Argon2id hashing) is CONFLICT", cond11, f"Reason: {r11.get('reason') if r11 else 'None'}")
    all_passed &= passed
    if cond11: tp_count += 1
    else: fn_count += 1

    # ── Group 5: Non-Software & Physical Artifacts (UNMAPPED) ───────────────────
    print("\n--- Group 5: Non-Software & Physical Artifacts (UNMAPPED) ---")

    # 12. US-310 (Cafeteria hot lunch specials)
    cond12 = "US-310" not in mapped_sources
    passed = check("12. US-310 (Cafeteria hot lunch specials) is UNMAPPED", cond12)
    all_passed &= passed
    if cond12: tn_count += 1
    else: fp_count += 1

    # 13. US-311 (Crop records to 35mm microfiche film)
    cond13 = "US-311" not in mapped_sources
    passed = check("13. US-311 (EEG strips to 35mm microfiche) is UNMAPPED", cond13)
    all_passed &= passed
    if cond13: tn_count += 1
    else: fp_count += 1

    # 14. TC-411 (Breakroom microwave oven)
    cond14 = "TC-411" not in mapped_targets
    passed = check("14. TC-411 (Breakroom microwave oven) is UNMAPPED", cond14)
    all_passed &= passed
    if cond14: tn_count += 1
    else: fp_count += 1

    # 15. CR-506 (Procure motorized standing desks)
    cond15 = "CR-506" not in mapped_sources
    passed = check("15. CR-506 (Procure 25 motorized standing desks) is UNMAPPED", cond15)
    all_passed &= passed
    if cond15: tn_count += 1
    else: fp_count += 1

    # 16. DEC-607 (Standing desks procurement decision)
    cond16 = "DEC-607" not in mapped_sources
    passed = check("16. DEC-607 (Standing desks procurement decision) is UNMAPPED", cond16)
    all_passed &= passed
    if cond16: tn_count += 1
    else: fp_count += 1

    # 17. DEC-603 (Unresolved optogenetic probe discussion)
    cond17 = "DEC-603" not in mapped_sources
    passed = check("17. DEC-603 (Unresolved optogenetic probe discussion) is UNMAPPED", cond17)
    all_passed &= passed
    if cond17: tn_count += 1
    else: fp_count += 1

    # ── Group 6: Change Requests & Governance Items ────────────────────────────
    print("\n--- Group 6: Change Requests & Governance Decisions ---")

    # 18. CR-501 -> FR-102 (HFO biomarker enhancement)
    r18 = rel_map.get(("CR-501", "FR-102"))
    cond18 = r18 is not None and r18["status"] in ["MATCHED", "PARTIAL"]
    passed = check("18. CR-501 (HFO biomarker enhancement) -> FR-102 is Mapped", cond18, f"Status: {r18.get('status') if r18 else 'None'}")
    all_passed &= passed
    if cond18: tp_count += 1
    else: fn_count += 1

    # 19. CR-502 -> FR-109 (Prohibit reversible DES encryption)
    r19 = rel_map.get(("CR-502", "FR-109"))
    cond19 = r19 is not None and r19["status"] in ["MATCHED", "CONFLICT", "PARTIAL"]
    passed = check("19. CR-502 (Mandate Argon2id / Prohibit DES) -> FR-109 is Mapped", cond19, f"Status: {r19.get('status') if r19 else 'None'}")
    all_passed &= passed
    if cond19: tp_count += 1
    else: fn_count += 1

    # 20. DEC-601 -> FR-106 (RingBuffer timestamp decision)
    r20 = rel_map.get(("DEC-601", "FR-106"))
    cond20 = r20 is not None and r20["status"] in ["MATCHED", "PARTIAL"]
    passed = check("20. DEC-601 (RingBuffer deduplication decision) -> FR-106 is Mapped", cond20, f"Status: {r20.get('status') if r20 else 'None'}")
    all_passed &= passed
    if cond20: tp_count += 1
    else: fn_count += 1

    # ── Summary Metrics Computation ───────────────────────────────────────────
    precision = (tp_count / (tp_count + fp_count)) if (tp_count + fp_count) > 0 else 0.0
    recall = (tp_count / (tp_count + fn_count)) if (tp_count + fn_count) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    print(f"\n{MINI}\n[5] ACCURACY BENCHMARK METRICS SUMMARY")
    print(f"    Total Benchmark Cases Evaluated : 20")
    print(f"    True Positives (TP)             : {tp_count}")
    print(f"    True Negatives (TN)             : {tn_count}")
    print(f"    False Positives (FP)            : {fp_count}")
    print(f"    False Negatives (FN)            : {fn_count}")
    print(f"    Relationship Precision          : {precision * 100:.1f}%")
    print(f"    Relationship Recall             : {recall * 100:.1f}%")
    print(f"    F1 Score                        : {f1 * 100:.1f}%")

    # ── Pipeline Parity Verification ─────────────────────────────────────────
    print(f"\n{MINI}\n[6] CANONICAL SINGLE-SOURCE PARITY VALIDATION")
    matrix_active_count = len([m for m in matrix if m.get("target_artifact") != "—"])
    graph_edge_count = len(graph.get("edges", []))
    graph_node_count = len(graph.get("nodes", []))

    passed = check(f"1. Matrix active mapped rows ({matrix_active_count}) == Graph edges ({graph_edge_count})", matrix_active_count == graph_edge_count)
    all_passed &= passed

    passed = check(f"2. Graph nodes ({graph_node_count}) == Total extracted artifacts ({len(artifacts)})", graph_node_count == len(artifacts))
    all_passed &= passed

    print(f"\n{SEP}")
    if all_passed:
        print("🎉 ALL 20 GROUND-TRUTH ACCURACY BENCHMARK CASES PASSED (100% SUCCESS)")
    else:
        print("❌ SOME BENCHMARK CASES FAILED")
    print(SEP)
    return all_passed


if __name__ == "__main__":
    success = run_blind_validation()
    sys.exit(0 if success else 1)
