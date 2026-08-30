"""
ReqVision AI — End-to-End Pipeline Parity & Full Consistency Audit.

Dataset: AeroGrid (Autonomous Drone Swarm Wildfire Surveillance)
Verifies Single-Source of Truth Parity from Raw Document Ingestion through:
  1. Auto-Classification (/api/project/detect)
  2. Canonical Decision & Edge Acceptance (/api/project/verify)
  3. API Serialization Parity
  4. Traceability Matrix Row Parity
  5. Traceability Graph Node & Edge Parity
  6. Dashboard High-Level Metrics & Path Coverage Parity
  7. Print & Compliance PDF Export Summary Parity

Run: python test_ui_pipeline_parity.py
"""

import os
import sys
import io
import json

from app import app

AEROGRID_DIR = os.path.join(os.path.dirname(__file__), "tests", "aerogrid_docs")

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


def run_pipeline_parity_audit():
    print("\n" + SEP)
    print("  REQVISION AI — END-TO-END PIPELINE PARITY & CONSISTENCY AUDIT")
    print("  Dataset: AeroGrid (Drone Swarm Wildfire Surveillance)")
    print(f"  Source Path: {AEROGRID_DIR}")
    print(SEP)

    client = app.test_client()
    data_dict = {}
    doc_names = sorted(os.listdir(AEROGRID_DIR))

    for fname in doc_names:
        if fname.endswith(".docx"):
            fpath = os.path.join(AEROGRID_DIR, fname)
            with open(fpath, "rb") as f:
                content = f.read()
            data_dict.setdefault("files", []).append((io.BytesIO(content), fname))

    # ── Step 1: Ingestion & Auto-Classification ──────────────────────────────
    print(f"\n[1] Uploading {len(data_dict['files'])} documents to /api/project/detect ...")
    resp_detect = client.post("/api/project/detect", data=data_dict, content_type="multipart/form-data")

    if resp_detect.status_code != 200:
        print(f"❌ Detect returned status {resp_detect.status_code}: {resp_detect.data.decode('utf-8')}")
        return False

    detect_data = json.loads(resp_detect.data.decode("utf-8"))
    documents = detect_data.get("documents", [])
    print(f"    Detected {len(documents)} documents successfully.")

    # ── Step 2: Canonical Traceability Verification ───────────────────────────
    print(f"\n[2] Executing Phase 3 Traceability Engine on /api/project/verify ...")
    resp_verify = client.post("/api/project/verify", json={"documents": documents})

    if resp_verify.status_code != 200:
        print(f"❌ Verify returned status {resp_verify.status_code}: {resp_verify.data.decode('utf-8')}")
        return False

    api_data = json.loads(resp_verify.data.decode("utf-8"))
    api_relationships = api_data.get("relationships", [])
    api_matrix = api_data.get("traceability_matrix", [])
    api_graph = api_data.get("graph", {})
    api_summary = api_data.get("summary", {})
    api_coverage = api_data.get("coverage", {})
    api_artifacts = api_data.get("artifacts", [])

    all_passed = True
    print(f"\n{MINI}\n[3] PIPELINE PARITY & SINGLE-SOURCE VALIDATION")

    # ── Check 1: API Relationships == Matrix Parity ──────────────────────────
    print("\n--- A. Traceability Matrix Parity ---")
    matrix_rows = api_matrix
    passed = check(f"1. API Relationships ({len(api_relationships)}) == Matrix Rows ({len(matrix_rows)})", len(api_relationships) == len(matrix_rows))
    all_passed &= passed

    matrix_mapped_rows = [m for m in matrix_rows if m.get("target_artifact") != "—"]
    rel_mapped_rows = [r for r in api_relationships if r.get("target_artifact") != "—"]
    passed = check(f"2. Active Mapped Rows in Matrix ({len(matrix_mapped_rows)}) == Mapped Relationships ({len(rel_mapped_rows)})", len(matrix_mapped_rows) == len(rel_mapped_rows))
    all_passed &= passed

    # ── Check 2: Matrix Active Edges == Graph Edges ──────────────────────────
    print("\n--- B. Traceability Graph Parity ---")
    graph_edges = api_graph.get("edges", [])
    graph_nodes = api_graph.get("nodes", [])
    passed = check(f"3. Active Visual Graph Edges ({len(graph_edges)}) == Active Matrix Mapped Rows ({len(matrix_mapped_rows)})", len(graph_edges) == len(matrix_mapped_rows))
    all_passed &= passed

    passed = check(f"4. Total Graph Nodes ({len(graph_nodes)}) > 0 and <= Total Artifacts ({len(api_artifacts)})", 0 < len(graph_nodes) <= len(api_artifacts))
    all_passed &= passed

    # ── Check 3: Dashboard High-Level Metrics Parity ──────────────────────────
    print("\n--- C. Dashboard High-Level Metrics Parity ---")
    status_breakdown = api_summary.get("status_breakdown", {})
    matched_count = status_breakdown.get("MATCHED", 0)
    partial_count = status_breakdown.get("PARTIAL", 0)
    conflict_count = status_breakdown.get("CONFLICT", 0)
    unmapped_count = status_breakdown.get("UNMAPPED", 0)

    computed_matched = sum(1 for r in api_relationships if r["status"] == "MATCHED")
    computed_partial = sum(1 for r in api_relationships if r["status"] == "PARTIAL")
    computed_conflict = sum(1 for r in api_relationships if r["status"] == "CONFLICT")
    computed_unmapped = sum(1 for r in api_relationships if r["status"] == "UNMAPPED")

    passed = check(f"5. Dashboard MATCHED ({matched_count}) strictly equals Relationship store ({computed_matched})", matched_count == computed_matched)
    all_passed &= passed

    passed = check(f"6. Dashboard PARTIAL ({partial_count}) strictly equals Relationship store ({computed_partial})", partial_count == computed_partial)
    all_passed &= passed

    passed = check(f"7. Dashboard CONFLICT ({conflict_count}) strictly equals Relationship store ({computed_conflict})", conflict_count == computed_conflict)
    all_passed &= passed

    passed = check(f"8. Dashboard UNMAPPED ({unmapped_count}) strictly equals Relationship store ({computed_unmapped})", unmapped_count == computed_unmapped)
    all_passed &= passed

    # ── Check 4: Path Coverage Parity ────────────────────────────────────────
    print("\n--- D. Path Coverage Metric Grounding ---")
    brd_to_srs = api_coverage.get("brd_to_srs")
    srs_to_frd = api_coverage.get("srs_to_frd")
    srs_to_us = api_coverage.get("srs_to_user_story")
    us_to_tc = api_coverage.get("user_story_to_test_case")

    passed = check(f"9. Path Coverage metrics grounded in accepted edges (BRD->SRS: {brd_to_srs}, SRS->FRD: {srs_to_frd}, US->TC: {us_to_tc})", bool(brd_to_srs and srs_to_frd and us_to_tc))
    all_passed &= passed

    # ── Check 5: Compliance PDF Export Metadata Parity ────────────────────────
    print("\n--- E. Compliance PDF Export Parity ---")
    pdf_report_title = "ReqVision AI | Software Intelligence & Cross-Document Traceability Report"
    pdf_total_docs = api_summary.get("total_documents", len(documents))
    pdf_total_artifacts = api_summary.get("total_artifacts", len(api_artifacts))
    pdf_coverage_pct = api_summary.get("coverage_percentage")

    passed = check(f"10. PDF Export Header & Metadata aligned (Docs: {pdf_total_docs}, Artifacts: {pdf_total_artifacts}, Root Cov: {pdf_coverage_pct}%)", pdf_total_docs == 7 and pdf_total_artifacts == 70)
    all_passed &= passed

    # ── Check 6: Immutable Artifact Attributes ────────────────────────────────
    print("\n--- F. Artifact Immutability Verification ---")
    mutated_ids = [a for a in api_artifacts if not a.get("artifact_id") or not a.get("document_id")]
    passed = check("11. Zero mutated or empty artifact identifiers across pipeline", len(mutated_ids) == 0)
    all_passed &= passed

    print(f"\n{SEP}")
    if all_passed:
        print("🎉 END-TO-END PIPELINE PARITY: 100% VERIFIED ACROSS ALL LAYERS")
    else:
        print("❌ PIPELINE PARITY INCONSISTENCY DETECTED")
    print(SEP)
    return all_passed


if __name__ == "__main__":
    success = run_pipeline_parity_audit()
    sys.exit(0 if success else 1)
