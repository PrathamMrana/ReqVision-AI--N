import os
import requests
import json

base_url = "http://127.0.0.1:5001"
doc_dir = "tests/test_docs"
filenames = [
    "01_BRD_Online_Library.docx",
    "02_SRS_Online_Library.docx",
    "03_FRD_Online_Library.docx",
    "04_User_Stories_Online_Library.docx",
    "05_Test_Cases_Online_Library.docx",
    "06_Change_Request_Online_Library.docx",
    "07_Meeting_Minutes_Online_Library.docx"
]

print("==================================================")
print("PHASE 2 REAL ACCEPTANCE TEST — 7 TEST DOCUMENTS")
print("==================================================")

# 1. Multi-File Upload & Content-Based Classification
files = []
for fname in filenames:
    fpath = os.path.join(doc_dir, fname)
    files.append(('files', (fname, open(fpath, 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')))

print(f"\n1. Uploading {len(files)} files to /api/project/detect ...")
resp_detect = requests.post(f"{base_url}/api/project/detect", files=files)
assert resp_detect.status_code == 200, f"Detect failed: {resp_detect.text}"
detect_data = resp_detect.json()

print(f"Detect Success: {detect_data['success']}")
print(f"Total Documents Detected: {detect_data['summary']['total_documents']}")
print(f"Total Artifacts Extracted: {detect_data['summary']['total_artifacts_extracted']}")

for doc in detect_data['documents']:
    print(f"  - [{doc['document_type']}] {doc['filename']}: {doc['artifact_label']} (Confidence: {doc['confidence_score']}%)")

# 2. Phase 2 Cross-Document Traceability Verification
print(f"\n2. Executing Cross-Document Verification on /api/project/verify ...")
resp_verify = requests.post(f"{base_url}/api/project/verify", json={"documents": detect_data['documents']})
assert resp_verify.status_code == 200, f"Verify failed: {resp_verify.text}"
verify_data = resp_verify.json()

summary = verify_data['summary']
print(f"\n--- VERIFICATION SUMMARY ---")
print(f"Title: {verify_data.get('title')}")
print(f"Analysis Type: {verify_data.get('analysis_type')}")
print(f"Total Documents: {summary['total_documents']}")
print(f"Total Artifacts: {summary['total_artifacts']}")
print(f"Total Pairwise Relationships: {summary['total_relationships']}")
print(f"Overall Traceability Coverage: {summary['coverage_percentage']}%")
print(f"Status Breakdown: {summary['status_breakdown']}")
print(f"Path Coverage Breakdown: {json.dumps(summary['path_coverage'], indent=2)}")

print(f"\n--- SOURCE -> TARGET TRACEABILITY MATRIX (Sample Rows) ---")
for rel in verify_data['traceability_matrix'][:8]:
    print(f"  [{rel['source_type']}] {rel['source_artifact']} --({rel['relationship']})--> [{rel['target_type']}] {rel['target_artifact']} | Status: {rel['status']} | Sim: {rel['similarity']:.2f} | Conf: {rel['confidence']}")

print(f"\n--- END-TO-END TRACEABILITY CHAINS (Sample) ---")
for chain in verify_data['traceability_chains'][:5]:
    brd = chain['brd']['id'] if chain['brd'] else '—'
    srs = chain['srs']['id'] if chain['srs'] else '—'
    frd = chain['frd']['id'] if chain['frd'] else '—'
    us = chain['user_story']['id'] if chain['user_story'] else '—'
    tc = chain['test_case']['id'] if chain['test_case'] else '—'
    print(f"  {brd} -> {srs} -> {frd} -> {us} -> {tc} | Status: {chain['overall_status']}")

print(f"\n--- TOP CONFLICTS ---")
for c in verify_data['top_conflicts']:
    print(f"  - CONFLICT in {c['source_id']} ({c['source_doc']}): {c['reason']}")

print(f"\n--- TOP UNMAPPED ---")
for u in verify_data['top_unmapped']:
    print(f"  - UNMAPPED: {u['artifact_id']} ({u['document_name']}) — {u['reason']}")

print(f"\n--- CHANGE REQUEST IMPACTS ---")
for cr in verify_data['change_request_impacts']:
    print(f"  - {cr['cr_id']} -> Affected: {cr['affected_doc']} [{cr['affected_req_id']}] | Status: {cr['status']} (Sim: {cr['similarity']:.2f})")

print(f"\n--- MEETING MINUTES GOVERNANCE LINKS ---")
for mom in verify_data['meeting_minutes_links']:
    print(f"  - {mom['mom_id']} -> References: {mom['referenced_doc']} [{mom['referenced_req_id']}] | Status: {mom['status']}")

# 3. Test V1 Mode Regression Safety
print(f"\n3. Testing V1 Mode Regression (/api/compare) ...")
v1_payload = {
    "baseline": [{"name": "SRS_v1.txt", "text": "FR-001 The system shall authenticate users with password.\nFR-002 System shall log transactions."}],
    "updated": [{"name": "SRS_v2.txt", "text": "FR-001 The system shall authenticate users with password and MFA.\nFR-003 System shall export reports."}]
}
resp_v1 = requests.post(f"{base_url}/api/compare", json=v1_payload)
assert resp_v1.status_code == 200, f"V1 Compare failed: {resp_v1.text}"
v1_data = resp_v1.json()
print(f"V1 Metrics: {v1_data['metrics']['counts']}")
print(f"V1 Regression Passed: Status {resp_v1.status_code}, Changes Count: {len(v1_data['changes'])}")
print("\nALL ACCEPTANCE TESTS COMPLETED SUCCESSFULLY!")
