import requests
import json
import os

API_BASE = "http://127.0.0.1:5001/api/project"

def test_campusride():
    print("=" * 60)
    print("CAMPUSRIDE ACCEPTANCE TEST — 7 TEST DOCUMENTS")
    print("=" * 60)
    
    files = [
        ('files', ('01_BRD_CampusRide.docx', open('tests/campusride_docs/01_BRD_CampusRide.docx', 'rb'))),
        ('files', ('02_SRS_CampusRide.docx', open('tests/campusride_docs/02_SRS_CampusRide.docx', 'rb'))),
        ('files', ('03_FRD_CampusRide.docx', open('tests/campusride_docs/03_FRD_CampusRide.docx', 'rb'))),
        ('files', ('04_User_Stories_CampusRide.docx', open('tests/campusride_docs/04_User_Stories_CampusRide.docx', 'rb'))),
        ('files', ('05_Test_Cases_CampusRide.docx', open('tests/campusride_docs/05_Test_Cases_CampusRide.docx', 'rb'))),
        ('files', ('06_Change_Requests_CampusRide.docx', open('tests/campusride_docs/06_Change_Requests_CampusRide.docx', 'rb'))),
        ('files', ('07_Meeting_Minutes_CampusRide.docx', open('tests/campusride_docs/07_Meeting_Minutes_CampusRide.docx', 'rb')))
    ]
    
    print("\n1. Uploading 7 CampusRide files to /api/project/detect ...")
    resp = requests.post(f"{API_BASE}/detect", files=files)
    if resp.status_code != 200:
        print(f"FAILED detect: {resp.status_code} {resp.text}")
        return False
        
    data = resp.json()
    print("Detect Success:", data.get("success"))
    print("Total Documents Detected:", data["summary"]["total_documents"])
    print("Total Artifacts Extracted:", data["summary"]["total_artifacts_extracted"])
    
    for doc in data["documents"]:
        print(f"  - [{doc['document_type']}] {doc['filename']}: {doc['artifact_label']} (Confidence: {doc['confidence_score']}%)")
        for art in doc["artifacts"][:2]:
            print(f"      * {art['artifact_id']} [{art['artifact_type']} / {art['document_type']}]: {art['text'][:60]}...")
            
    print("\n2. Executing Cross-Document Verification on /api/project/verify ...")
    verify_resp = requests.post(f"{API_BASE}/verify", json={"documents": data["documents"]})
    if verify_resp.status_code != 200:
        print(f"FAILED verify: {verify_resp.status_code} {verify_resp.text}")
        return False
        
    vdata = verify_resp.json()
    print("\n--- VERIFICATION SUMMARY ---")
    print("Total Documents:", vdata["summary"]["total_documents"])
    print("Total Artifacts:", vdata["summary"]["total_artifacts"])
    print("Total Pairwise Relationships:", vdata["summary"]["total_relationships"])
    print("Status Breakdown:", vdata["summary"]["status_breakdown"])
    print("Path Coverage Breakdown:")
    for k, v in vdata["summary"]["path_coverage"].items():
        print(f"  {k}: {v}")
        
    print("\n--- SAMPLE MATRIX ROWS ---")
    for r in vdata["relationships"][:15]:
        print(f"  [{r['source_type']}] {r['source_artifact']} [{r.get('source_artifact_type', '')}] --({r['relationship']})--> [{r['target_type']}] {r['target_artifact']} [{r.get('target_artifact_type', '')}] | Status: {r['status']} | Sim: {r['similarity']:.2f}")

    print("\n--- CHANGE REQUEST IMPACTS ---")
    for cr in vdata["change_request_impacts"]:
        print(f"  {cr['cr_id']} -> Affected: {cr['affected_doc']} [{cr['affected_req_id']}] [{cr['status']}] (Sim: {cr['similarity']:.2f})")

    print("\n--- MEETING MINUTES GOVERNANCE LINKS ---")
    for mom in vdata["meeting_minutes_links"]:
        print(f"  {mom['mom_id']} -> References: {mom['referenced_doc']} [{mom['referenced_req_id']}] [{mom['status']}] (Sim: {mom['similarity']:.2f})")

    print("\n--- V1 REGRESSION CHECK ---")
    v1_resp = requests.post("http://127.0.0.1:5001/api/compare", json={
        "baseline": "REQ-1: User login with email\nREQ-2: View user profile\nREQ-3: Search catalogue",
        "updated": "REQ-1: User login with email and MFA\nREQ-2: View user profile\nREQ-4: Export analytics report"
    })
    print("V1 Status:", v1_resp.status_code)
    print("V1 Changes:", v1_resp.json().get("metrics"))
    
    return True

if __name__ == "__main__":
    test_campusride()
