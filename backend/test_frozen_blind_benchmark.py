"""
ReqVision AI — Frozen Independent Blind External Ground-Truth Benchmark.

Dataset: AgriGrid (Autonomous Agricultural IoT Irrigation & Soil Nutrient Management)
Evaluates production API endpoints (/api/project/detect -> /api/project/verify)
against pre-frozen human ground truth across 12 distinct verification points:
  1. True Positive Paraphrase: BR-002 (Weather irrigation deferral) -> FR-102
  2. True Positive Paraphrase: BR-004 (Cancel fertigation cycle) -> FR-104
  3. True Positive Downstream: US-304 (Cancel fertigation story) -> TC-404 (Cancel fertigation test)
  4. Defensive Security Defense: BR-006 (Deduplicate sensor telemetry) -> FR-106 (MATCHED, not CONFLICT)
  5. True Policy Contradiction: FR-109 (Reversible Caesar cipher) vs FS-209 (Argon2id hashing) -> CONFLICT
  6. Non-Software Physical Amenity: US-310 (Cafeteria lunch specials) -> UNMAPPED
  7. Obsolete Physical Media: US-311 (Microfiche storage) -> UNMAPPED
  8. Physical Breakroom Appliance: TC-411 (Microwave oven) -> UNMAPPED
  9. Physical Office Furniture: CR-506 (Motorized standing desks) -> UNMAPPED
 10. Physical Office Decision: DEC-607 (Standing desks procurement) -> UNMAPPED
 11. Unresolved Governance: DEC-603 (Drone flight path discussion) -> UNMAPPED
 12. Single-Source Parity: Matrix active mapped edges == Graph active visual edges

Run: python test_frozen_blind_benchmark.py
"""

import os
import sys
import io
import json

from app import app

AGRIGRID_DIR = os.path.join(os.path.dirname(__file__), "tests", "agrigrid_docs")

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


def run_frozen_benchmark():
    print("\n" + SEP)
    print("  REQVISION AI — FROZEN INDEPENDENT BLIND BENCHMARK")
    print("  Dataset: AgriGrid (Agricultural IoT Irrigation & Telemetry)")
    print(f"  Source Path: {AGRIGRID_DIR}")
    print(SEP)

    client = app.test_client()
    data_dict = {}
    doc_names = sorted(os.listdir(AGRIGRID_DIR))

    for fname in doc_names:
        if fname.endswith(".docx"):
            fpath = os.path.join(AGRIGRID_DIR, fname)
            with open(fpath, "rb") as f:
                content = f.read()
            data_dict.setdefault("files", []).append((io.BytesIO(content), fname))

    print(f"\n[1] Submitting {len(data_dict['files'])} AgriGrid documents to /api/project/detect ...")
    resp_detect = client.post("/api/project/detect", data=data_dict, content_type="multipart/form-data")

    if resp_detect.status_code != 200:
        print(f"❌ Detect returned status {resp_detect.status_code}: {resp_detect.data.decode('utf-8')}")
        return False

    detect_data = json.loads(resp_detect.data.decode("utf-8"))
    documents = detect_data.get("documents", [])
    print(f"    Detected & extracted {len(documents)} documents successfully.")

    print(f"\n[2] Executing Phase 3 Cross-Document Traceability on /api/project/verify ...")
    resp_verify = client.post("/api/project/verify", json={"documents": documents})

    if resp_verify.status_code != 200:
        print(f"❌ Verify returned status {resp_verify.status_code}: {resp_verify.data.decode('utf-8')}")
        return False

    data = json.loads(resp_verify.data.decode("utf-8"))
    relationships = data.get("relationships", [])
    artifacts = data.get("artifacts", [])
    matrix = data.get("traceability_matrix", [])
    graph = data.get("graph", {})
    coverage = data.get("coverage", {})

    print(f"\n[3] Production Inference Summary:")
    print(f"    Total Extracted Artifacts: {len(artifacts)}")
    print(f"    Accepted Canonical Edges : {len(relationships)}")
    print(f"    Semantic Active          : {data.get('semantic_enabled')}")
    print(f"    Semantic Model           : {data.get('semantic_model')}")

    # Build lookup map: (source_artifact, target_artifact) -> rel_dict
    rel_map = {}
    for r in relationships:
        rel_map[(r["source_artifact"], r["target_artifact"])] = r

    # Build unmapped sets
    mapped_sources = {r["source_artifact"] for r in relationships if r.get("target_artifact") != "—"}
    mapped_targets = {r["target_artifact"] for r in relationships if r.get("target_artifact") != "—"}

    all_passed = True
    print(f"\n{MINI}\n[4] FROZEN GROUND-TRUTH VALIDATION ASSERTIONS")

    # ── 1. True Positives & Paraphrases ──────────────────────────────────────
    print("\n--- Group 1: True Positive Paraphrased Realizations ---")
    r1 = rel_map.get(("BR-002", "FR-102"))
    passed = check("1. BR-002 (Weather forecast irrigation deferral) -> FR-102 is Mapped", r1 is not None and r1["status"] in ["MATCHED", "PARTIAL"], f"Status: {r1.get('status') if r1 else 'None'}")
    all_passed &= passed

    r2 = rel_map.get(("BR-004", "FR-104"))
    passed = check("2. BR-004 (Cancel fertigation cycle) -> FR-104 is MATCHED", r2 is not None and r2["status"] == "MATCHED", f"Evidence: {r2.get('evidence') if r2 else 'None'}")
    all_passed &= passed

    r3 = rel_map.get(("US-304", "TC-404"))
    passed = check("3. US-304 (Cancel fertigation job story) -> TC-404 (Cancel fertigation test) is MATCHED", r3 is not None and r3["status"] == "MATCHED", f"Evidence: {r3.get('evidence') if r3 else 'None'}")
    all_passed &= passed

    # ── 2. Defensive Security Validation ─────────────────────────────────────
    print("\n--- Group 2: Defensive Security Validation (Affirmative Recognition) ---")
    r4 = rel_map.get(("BR-006", "FR-106"))
    passed = check("4. BR-006 (Deduplicate sensor telemetry defense) -> FR-106 is MATCHED (Not CONFLICT)", r4 is not None and r4["status"] == "MATCHED", f"Evidence: {r4.get('evidence') if r4 else 'None'}")
    all_passed &= passed

    # ── 3. True Contradiction ────────────────────────────────────────────────
    print("\n--- Group 3: True Policy Contradiction ---")
    r5 = rel_map.get(("FR-109", "FS-209"))
    passed = check("5. FR-109 (Reversible Caesar cipher) vs FS-209 (Argon2id hashing) is CONFLICT", r5 is not None and r5["status"] == "CONFLICT", f"Reason: {r5.get('reason') if r5 else 'None'}")
    all_passed &= passed

    # ── 4. Non-Software / Physical Discrimination ────────────────────────────
    print("\n--- Group 4: Unmapped Physical & Non-Software Artifacts ---")
    passed = check("6. US-310 (Cafeteria hot lunch specials) is UNMAPPED", "US-310" not in mapped_sources)
    all_passed &= passed

    passed = check("7. US-311 (Crop records to 35mm microfiche) is UNMAPPED", "US-311" not in mapped_sources)
    all_passed &= passed

    passed = check("8. TC-411 (Breakroom microwave oven) is UNMAPPED", "TC-411" not in mapped_targets)
    all_passed &= passed

    passed = check("9. CR-506 (Procure motorized standing desks) is UNMAPPED", "CR-506" not in mapped_sources)
    all_passed &= passed

    passed = check("10. DEC-607 (Standing desks procurement decision) is UNMAPPED", "DEC-607" not in mapped_sources)
    all_passed &= passed

    passed = check("11. DEC-603 (Unresolved drone flight path discussion) is UNMAPPED", "DEC-603" not in mapped_sources)
    all_passed &= passed

    # ── 5. Pipeline Consistency ──────────────────────────────────────────────
    print("\n--- Group 5: Pipeline Single-Source Parity ---")
    matrix_edge_count = len([m for m in matrix if m.get("target_artifact") != "—"])
    graph_edge_count = len(graph.get("edges", []))
    passed = check(f"12. Matrix active edges ({matrix_edge_count}) == Graph visual edges ({graph_edge_count})", matrix_edge_count == graph_edge_count)
    all_passed &= passed

    print(f"\n{SEP}")
    if all_passed:
        print("🎉 ALL 12 FROZEN GROUND-TRUTH BENCHMARK ASSERTIONS PASSED (100% SUCCESS)")
    else:
        print("❌ SOME FROZEN BENCHMARK ASSERTIONS FAILED")
    print(SEP)
    return all_passed


if __name__ == "__main__":
    success = run_frozen_benchmark()
    sys.exit(0 if success else 1)
