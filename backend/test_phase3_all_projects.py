"""
ReqVision AI — Phase 3 Multi-Domain Cross-Document Traceability Test Suite.

Executes and verifies 5 distinct project domains:
  1. Online Library System (tests/test_docs/)
  2. CampusRide Transit Platform (tests/campusride_docs/)
  3. Hospital Patient Management System (tests/health_docs/)
  4. EduPay University Billing & Tuition (tests/edupay_docs/)
  5. FoodFlow Kitchen Logistics & Meal Delivery (tests/foodflow_docs/)
  + V1 Baseline/Updated Regression (/api/compare)
  + Automated Integrity & Anti-Hallucination Assertions

Run: python test_phase3_all_projects.py
"""

import sys
import os
import json
import urllib.request
import urllib.error

BACKEND = "http://127.0.0.1:5001"

DOMAINS = [
    ("Online Library", os.path.join(os.path.dirname(__file__), "tests", "test_docs")),
    ("CampusRide", os.path.join(os.path.dirname(__file__), "tests", "campusride_docs")),
    ("Hospital PMS", os.path.join(os.path.dirname(__file__), "tests", "health_docs")),
    ("EduPay", os.path.join(os.path.dirname(__file__), "tests", "edupay_docs")),
    ("FoodFlow (5th Domain)", os.path.join(os.path.dirname(__file__), "tests", "foodflow_docs")),
    ("TravelOps (6th Domain)", os.path.join(os.path.dirname(__file__), "tests", "travelops_docs")),
    ("InsureFlow (Blind Dataset)", os.path.join(os.path.dirname(__file__), "tests", "insureflow_docs")),
    ("AeroLogix (7th Unseen Domain)", os.path.join(os.path.dirname(__file__), "tests", "aerologix_docs")),
    ("FleetOps (Vehicle Logistics)", os.path.join(os.path.dirname(__file__), "tests", "fleetops_docs")),
]

SEP = "=" * 75
MINI = "-" * 50


def upload_and_verify(project_name, docs_dir):
    print(f"\n{SEP}")
    print(f"  PROJECT DOMAIN: {project_name}")
    print(SEP)

    doc_files = sorted([f for f in os.listdir(docs_dir) if f.endswith(".docx")])
    if not doc_files:
        print(f"  ❌ No .docx files found in {docs_dir}")
        return False

    print(f"  Ingesting {len(doc_files)} documents:")
    for f in doc_files:
        print(f"    - {f}")

    # 1. Detect
    boundary = "----ReqVisionBoundary"
    body_parts = []
    for fname in doc_files:
        fpath = os.path.join(docs_dir, fname)
        with open(fpath, "rb") as fh:
            fdata = fh.read()
        part = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"files\"; filename=\"{fname}\"\r\n"
            f"Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n"
        ).encode("utf-8") + fdata + b"\r\n"
        body_parts.append(part)
    body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(body_parts)

    req = urllib.request.Request(
        f"{BACKEND}/api/project/detect",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            detect_result = json.loads(resp.read())
    except Exception as e:
        print(f"  ❌ /api/project/detect failed: {e}")
        return False

    if not detect_result.get("success"):
        print(f"  ❌ detect error: {detect_result.get('error')}")
        return False

    # 2. Verify
    verify_payload = json.dumps(detect_result).encode("utf-8")
    req2 = urllib.request.Request(
        f"{BACKEND}/api/project/verify",
        data=verify_payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req2, timeout=120) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        print(f"  ❌ /api/project/verify failed: {e}")
        return False

    if not result.get("success"):
        print(f"  ❌ verify error: {result.get('error')}")
        return False

    summary = result.get("summary", {})
    breakdown = summary.get("status_breakdown", {})
    path_cov = summary.get("path_coverage", {})
    rels = result.get("traceability_matrix", [])

    print(f"\n  [VERIFIED OUTPUT]")
    print(f"    Total Documents: {summary.get('total_documents', '?')}")
    print(f"    Total Artifacts: {summary.get('total_artifacts', '?')}")
    print(f"    Relationships  : {summary.get('total_relationships', '?')}")
    print(f"    MATCHED        : {breakdown.get('MATCHED', 0)}")
    print(f"    PARTIAL        : {breakdown.get('PARTIAL', 0)}")
    print(f"    CONFLICT       : {breakdown.get('CONFLICT', 0)}")
    print(f"    UNMAPPED       : {breakdown.get('UNMAPPED', 0)}")
    print()
    print(f"    BRD → SRS      : {path_cov.get('brd_to_srs_coverage', '?')}")
    print(f"    SRS → FRD      : {path_cov.get('srs_to_frd_coverage', '?')}")
    print(f"    SRS → US       : {path_cov.get('srs_to_user_story_coverage', '?')}")
    print(f"    US → TC        : {path_cov.get('user_story_to_test_case_coverage', '?')}")
    print()
    print(f"    semantic_enabled: {result.get('semantic_enabled')}")
    print(f"    semantic_model  : {result.get('semantic_model')}")
    print(f"    analysis_mode   : {result.get('analysis_mode')}")

    # 3. Automated Integrity Assertions
    print(f"\n  {MINI}")
    print("  AUTOMATED INTEGRITY ASSERTIONS")
    print(f"  {MINI}")
    assertions_passed = True

    # A1: Ensure no fabricated artifact IDs or relationships
    valid_source_ids = {a["artifact_id"] for a in result.get("artifacts", [])}
    for r in rels:
        if r["source_artifact"] not in valid_source_ids:
            print(f"    ❌ Fabricated source artifact detected: {r['source_artifact']}")
            assertions_passed = False

    # A2: Type-safe relationship assertions
    for r in rels:
        if r["relationship"] == "TRACEABLE_TO" and r["source_type"] != "BRD":
            print(f"    ❌ Type violation in TRACEABLE_TO: source_type={r['source_type']}")
            assertions_passed = False
        if r["relationship"] == "IMPLEMENTED_BY" and r["source_type"] != "SRS":
            print(f"    ❌ Type violation in IMPLEMENTED_BY: source_type={r['source_type']}")
            assertions_passed = False
        if r["relationship"] == "VERIFIED_BY" and r["source_type"] != "USER_STORY":
            print(f"    ❌ Type violation in VERIFIED_BY: source_type={r['source_type']}")
            assertions_passed = False

    # A3: Score validity
    for r in rels:
        if r["status"] in ("MATCHED", "PARTIAL", "CONFLICT") and r["target_artifact"] != "—":
            if r.get("semantic_similarity") is None and result.get("semantic_enabled"):
                print(f"    ❌ Missing semantic score for verified link: {r['source_artifact']} -> {r['target_artifact']}")
                assertions_passed = False

    if assertions_passed:
        print("    ✅ All Type-Safety & Anti-Hallucination Assertions PASSED")

    # Sample relationships
    print(f"\n  {MINI}")
    print("  SAMPLE DUAL EVIDENCE (Semantic | Lexical | Hybrid)")
    print(f"  {MINI}")
    shown = 0
    for r in rels:
        if r.get("status") in ("MATCHED", "CONFLICT") and r.get("target_artifact") != "—":
            sem = r.get("semantic_similarity")
            lex = r.get("lexical_similarity", 0)
            hyb = r.get("hybrid_score", 0)
            sem_str = f"{sem:.2f}" if sem is not None else "N/A"
            print(f"    {r['source_artifact']} → {r['target_artifact']}  [{r['status']}]")
            print(f"      sem={sem_str}  lex={lex:.2f}  hyb={hyb:.2f}  conf={r['confidence']}")
            shown += 1
            if shown >= 4:
                break

    return assertions_passed


def run_v1_regression():
    print(f"\n{SEP}")
    print("  V1 REGRESSION — /api/compare")
    print(SEP)
    baseline = "REQ-001: Users shall be able to search for books by title and author.\nREQ-002: System shall support member login.\nREQ-003: System shall track borrowed items."
    updated  = "REQ-001: Users shall be able to search for books by title, author, and ISBN with sub-200ms response time.\nREQ-002: System shall support member login.\nREQ-004: System shall support digital ebook downloads."
    payload = json.dumps({"baseline": baseline, "updated": updated}).encode("utf-8")
    req = urllib.request.Request(
        f"{BACKEND}/api/compare",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            code = resp.status
    except urllib.error.HTTPError as e:
        code = e.code
        data = {}
    except Exception as e:
        print(f"  ❌ V1 call failed: {e}")
        return False

    print(f"  HTTP Status: {code}")
    if code == 200:
        print("  ✅ V1 /api/compare returned 200 OK (Isolated from Phase 3 changes)")
        return True
    else:
        print(f"  ❌ V1 returned HTTP {code}")
        return False


def main():
    print("\n" + SEP)
    print("  REQVISION AI — PHASE 3 5-DOMAIN MULTI-PROJECT ACCEPTANCE SUITE")
    print(SEP)

    results = {}
    for name, docs_dir in DOMAINS:
        if os.path.exists(docs_dir):
            results[name] = upload_and_verify(name, docs_dir)
        else:
            print(f"\n  ⚠ Directory not found: {docs_dir}")
            results[name] = False

    results["V1 Regression (/api/compare)"] = run_v1_regression()

    print(f"\n{SEP}")
    print("  FINAL 5-DOMAIN EXECUTION SUMMARY")
    print(SEP)
    all_passed = True
    for name, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon}  {name}")
        all_passed &= passed

    print()
    if all_passed:
        print("  🎉 ALL 5 DOMAINS & V1 REGRESSION PASSED SUCCESSFULLY")
    else:
        print("  ❌ SOME DOMAINS FAILED — review output above")
    print(SEP)
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
