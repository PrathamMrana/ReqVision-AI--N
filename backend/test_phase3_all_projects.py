"""
Phase 3 All-Projects Test — runs Online Library, CampusRide, Hospital PMS, and V1 regression.

Run:
  1. Start backend: source venv/bin/activate && python app.py &
  2. python test_phase3_all_projects.py

Reports per project:
  - Docs, Artifacts, Relationships, MATCHED/PARTIAL/CONFLICT/UNMAPPED
  - semantic_enabled, semantic_model, analysis_mode
  - Path coverages
  - Sample relationships showing semantic_sim, lexical_sim, hybrid_score
  - Cases where semantic added value (high sem, low lex)
  - Cases where lexical anchored (high lex, low sem)
"""

import sys
import os
import json
import urllib.request
import urllib.error

BACKEND = "http://127.0.0.1:5001"

ONLINE_LIBRARY_DIR = os.path.join(os.path.dirname(__file__), "tests", "test_docs")
CAMPUSRIDE_DIR = os.path.join(os.path.dirname(__file__), "tests", "campusride_docs")
HEALTH_DIR = os.path.join(os.path.dirname(__file__), "tests", "health_docs")

SEP = "=" * 70
MINI = "-" * 50


def upload_and_verify(project_name, docs_dir):
    """Upload all .docx files from docs_dir, detect, then verify."""
    print(f"\n{SEP}")
    print(f"  PROJECT: {project_name}")
    print(SEP)

    doc_files = sorted([f for f in os.listdir(docs_dir) if f.endswith(".docx")])
    if not doc_files:
        print(f"  ❌ No .docx files found in {docs_dir}")
        return False

    print(f"  Files: {len(doc_files)}")
    for f in doc_files:
        print(f"    - {f}")

    # ── Step 1: Detect (POST /api/project/detect) ─────────────────────────
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
        print(f"  ❌ detect not success: {detect_result.get('error')}")
        return False

    print(f"\n  [DETECT] ✅  {detect_result.get('total_documents', '?')} docs, {detect_result.get('total_artifacts', '?')} artifacts")

    # ── Step 2: Verify (POST /api/project/verify) ─────────────────────────
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
        print(f"  ❌ verify not success: {result.get('error')}")
        return False

    # ── Print results ─────────────────────────────────────────────────────
    summary = result.get("summary", {})
    breakdown = summary.get("status_breakdown", {})
    path_cov = summary.get("path_coverage", {})

    print(f"\n  [VERIFY] ✅")
    print(f"    Documents    : {summary.get('total_documents', '?')}")
    print(f"    Artifacts    : {summary.get('total_artifacts', '?')}")
    print(f"    Relationships: {summary.get('total_relationships', '?')}")
    print(f"    MATCHED      : {breakdown.get('MATCHED', 0)}")
    print(f"    PARTIAL      : {breakdown.get('PARTIAL', 0)}")
    print(f"    CONFLICT     : {breakdown.get('CONFLICT', 0)}")
    print(f"    UNMAPPED     : {breakdown.get('UNMAPPED', 0)}")
    print()
    print(f"    BRD→SRS      : {path_cov.get('brd_to_srs_coverage', '?')}")
    print(f"    SRS→FRD      : {path_cov.get('srs_to_frd_coverage', '?')}")
    print(f"    SRS→US       : {path_cov.get('srs_to_user_story_coverage', '?')}")
    print(f"    US→TC        : {path_cov.get('user_story_to_test_case_coverage', '?')}")
    print()
    print(f"    semantic_enabled : {result.get('semantic_enabled', 'N/A')}")
    print(f"    semantic_model   : {result.get('semantic_model', 'N/A')}")
    print(f"    analysis_mode    : {result.get('analysis_mode', 'N/A')}")
    print(f"    analysis_type    : {result.get('analysis_type', 'N/A')}")

    # ── Sample relationships with all 3 scores ────────────────────────────
    rels = result.get("traceability_matrix", [])
    print(f"\n  {MINI}")
    print("  SAMPLE RELATIONSHIPS (semantic_sim | lexical_sim | hybrid_score)")
    print(f"  {MINI}")
    shown = 0
    for r in rels:
        if r.get("status") in ("MATCHED", "CONFLICT") and r.get("target_artifact") != "—":
            sem = r.get("semantic_similarity")
            lex = r.get("lexical_similarity", 0)
            hyb = r.get("hybrid_score", 0)
            sem_str = f"{sem:.2f}" if sem is not None else "N/A"
            print(f"    {r['source_artifact']} → {r['target_artifact']}  [{r['status']}]")
            print(f"      sem={sem_str}  lex={lex:.2f}  hyb={hyb:.2f}")
            shown += 1
            if shown >= 5:
                break

    # ── Cases where semantic helped (high sem, low lex) ───────────────────
    semantic_wins = [
        r for r in rels
        if r.get("semantic_similarity") is not None
        and r.get("semantic_similarity", 0) > 0.55
        and r.get("lexical_similarity", 1) < 0.35
        and r.get("status") in ("MATCHED", "PARTIAL")
    ]
    print(f"\n  Semantic > Lexical cases (sem>0.55, lex<0.35, MATCHED/PARTIAL): {len(semantic_wins)}")
    for r in semantic_wins[:3]:
        print(f"    {r['source_artifact']} → {r['target_artifact']}  sem={r['semantic_similarity']:.2f}  lex={r['lexical_similarity']:.2f}")

    # ── Cases where lexical anchored ──────────────────────────────────────
    lexical_anchors = [
        r for r in rels
        if r.get("lexical_similarity", 0) > 0.35
        and (r.get("semantic_similarity") or 0) < 0.40
        and r.get("status") in ("MATCHED", "PARTIAL")
    ]
    print(f"\n  Lexical > Semantic cases (lex>0.35, sem<0.40, MATCHED/PARTIAL): {len(lexical_anchors)}")
    for r in lexical_anchors[:2]:
        sem = r.get("semantic_similarity")
        sem_str = f"{sem:.2f}" if sem is not None else "N/A"
        print(f"    {r['source_artifact']} → {r['target_artifact']}  lex={r['lexical_similarity']:.2f}  sem={sem_str}")

    return True


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
        # Look for change summary
        changes = data.get("changes") or data.get("summary") or data
        if isinstance(changes, dict):
            for k, v in changes.items():
                if isinstance(v, (int, float, list)):
                    print(f"    {k}: {v if not isinstance(v, list) else len(v)}")
        print("  ✅ V1 /api/compare returned 200 OK")
        return True
    else:
        print(f"  ❌ V1 returned HTTP {code}")
        return False


def main():
    print("\n" + "=" * 70)
    print("  REQVISION AI — PHASE 3 ALL-PROJECTS TEST")
    print("=" * 70)

    results = {}

    # Check backend is up
    try:
        with urllib.request.urlopen(f"{BACKEND}/", timeout=5):
            pass
    except Exception:
        pass  # root might 404 but that's fine

    # Online Library
    if os.path.exists(ONLINE_LIBRARY_DIR):
        results["Online Library"] = upload_and_verify("Online Library", ONLINE_LIBRARY_DIR)
    else:
        print(f"\n  ⚠ Online Library docs not found: {ONLINE_LIBRARY_DIR}")
        results["Online Library"] = False

    # CampusRide
    if os.path.exists(CAMPUSRIDE_DIR):
        results["CampusRide"] = upload_and_verify("CampusRide", CAMPUSRIDE_DIR)
    else:
        print(f"\n  ⚠ CampusRide docs not found: {CAMPUSRIDE_DIR}")
        results["CampusRide"] = False

    # Hospital PMS
    if os.path.exists(HEALTH_DIR):
        results["Hospital PMS"] = upload_and_verify("Hospital PMS", HEALTH_DIR)
    else:
        print(f"\n  ⚠ Hospital PMS docs not found: {HEALTH_DIR}")
        results["Hospital PMS"] = False

    # V1 Regression
    results["V1 Regression"] = run_v1_regression()

    # Summary
    print(f"\n{SEP}")
    print("  FINAL SUMMARY")
    print(SEP)
    all_passed = True
    for name, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon}  {name}")
        all_passed &= passed

    print()
    if all_passed:
        print("  🎉 ALL PHASE 3 TESTS PASSED")
    else:
        print("  ⚠  SOME TESTS FAILED — review output above")
    print(SEP)
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
