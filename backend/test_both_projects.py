import requests
import json
import time

API_BASE = "http://127.0.0.1:5001/api"

def run_project_test(project_name, file_tuples):
    print("\n" + "=" * 70)
    print(f"RUNNING ACCEPTANCE TEST: {project_name.upper()}")
    print("=" * 70)
    
    # 1. Detect
    print(f"1. Ingesting & Classifying {len(file_tuples)} documents ...")
    t0 = time.time()
    files_payload = [('files', (fname, open(fpath, 'rb'))) for fname, fpath in file_tuples]
    detect_resp = requests.post(f"{API_BASE}/project/detect", files=files_payload)
    if detect_resp.status_code != 200:
        print(f"FAILED detect: {detect_resp.status_code} {detect_resp.text}")
        return False
    ddata = detect_resp.json()
    print(f"   -> Detected {ddata['summary']['total_documents']} documents, {ddata['summary']['total_artifacts_extracted']} artifacts in {(time.time()-t0)*1000:.1f}ms")
    
    for doc in ddata["documents"]:
        print(f"      [{doc['document_type']}] {doc['filename']}: {doc['artifact_label']} (Conf: {doc['confidence_score']}%)")
        
    # 2. Verify
    print(f"\n2. Executing Type-Safe Cross-Document Traceability ...")
    t1 = time.time()
    verify_resp = requests.post(f"{API_BASE}/project/verify", json={"documents": ddata["documents"]})
    if verify_resp.status_code != 200:
        print(f"FAILED verify: {verify_resp.status_code} {verify_resp.text}")
        return False
    vdata = verify_resp.json()
    print(f"   -> Traceability analysis completed in {(time.time()-t1)*1000:.1f}ms")
    print(f"   Total Artifacts: {vdata['summary']['total_artifacts']}")
    print(f"   Total Relationships: {vdata['summary']['total_relationships']}")
    print(f"   Status Breakdown: {vdata['summary']['status_breakdown']}")
    print("   Path Coverages:")
    for k, v in vdata["summary"]["path_coverage"].items():
        print(f"      - {k}: {v}")
        
    print("\n   Key Change Request Impacts:")
    for cr in vdata["change_request_impacts"]:
        print(f"      * {cr['cr_id']} -> Affected: {cr['affected_doc']} [{cr['affected_req_id']}] [{cr['status']}] (Sim: {cr['similarity']:.2f})")

    print("\n   Key Meeting Minutes Links:")
    for mom in vdata["meeting_minutes_links"]:
        print(f"      * {mom['mom_id']} -> References: {mom['referenced_doc']} [{mom['referenced_req_id']}] [{mom['status']}] (Sim: {mom['similarity']:.2f})")

    if vdata.get("conflicts"):
        print("\n   Detected Conflicts:")
        for c in vdata["conflicts"]:
            print(f"      ! {c['source_id']} <-> {c['target_id']}: {c['reason']}")
            
    return True

def test_all():
    print("=" * 70)
    print("REQVISION AI — MULTI-PROJECT GENERIC PIPELINE VALIDATION")
    print("=" * 70)
    
    # Dataset 1: Online Library
    online_library_files = [
        ('01_BRD_Online_Library.docx', 'tests/test_docs/01_BRD_Online_Library.docx'),
        ('02_SRS_Online_Library.docx', 'tests/test_docs/02_SRS_Online_Library.docx'),
        ('03_FRD_Online_Library.docx', 'tests/test_docs/03_FRD_Online_Library.docx'),
        ('04_User_Stories_Online_Library.docx', 'tests/test_docs/04_User_Stories_Online_Library.docx'),
        ('05_Test_Cases_Online_Library.docx', 'tests/test_docs/05_Test_Cases_Online_Library.docx'),
        ('06_Change_Request_Online_Library.docx', 'tests/test_docs/06_Change_Request_Online_Library.docx'),
        ('07_Meeting_Minutes_Online_Library.docx', 'tests/test_docs/07_Meeting_Minutes_Online_Library.docx')
    ]
    res1 = run_project_test("Online Library", online_library_files)
    
    # Dataset 2: CampusRide
    campusride_files = [
        ('01_BRD_CampusRide.docx', 'tests/campusride_docs/01_BRD_CampusRide.docx'),
        ('02_SRS_CampusRide.docx', 'tests/campusride_docs/02_SRS_CampusRide.docx'),
        ('03_FRD_CampusRide.docx', 'tests/campusride_docs/03_FRD_CampusRide.docx'),
        ('04_User_Stories_CampusRide.docx', 'tests/campusride_docs/04_User_Stories_CampusRide.docx'),
        ('05_Test_Cases_CampusRide.docx', 'tests/campusride_docs/05_Test_Cases_CampusRide.docx'),
        ('06_Change_Requests_CampusRide.docx', 'tests/campusride_docs/06_Change_Requests_CampusRide.docx'),
        ('07_Meeting_Minutes_CampusRide.docx', 'tests/campusride_docs/07_Meeting_Minutes_CampusRide.docx')
    ]
    res2 = run_project_test("CampusRide", campusride_files)
    
    # V1 Regression
    print("\n" + "=" * 70)
    print("RUNNING V1 MODE REGRESSION TEST (/api/compare)")
    print("=" * 70)
    v1_resp = requests.post(f"{API_BASE}/compare", json={
        "baseline": "REQ-1: User login with email\nREQ-2: View user profile\nREQ-3: Search catalogue",
        "updated": "REQ-1: User login with email and MFA\nREQ-2: View user profile\nREQ-4: Export analytics report"
    })
    print(f"V1 HTTP Status: {v1_resp.status_code}")
    print(f"V1 Result Metrics: {v1_resp.json().get('metrics')}")
    
    if res1 and res2 and v1_resp.status_code == 200:
        print("\n" + "=" * 70)
        print("ALL MULTI-PROJECT & V1 REGRESSION TESTS PASSED SUCCESSFULLY!")
        print("=" * 70)

if __name__ == "__main__":
    test_all()
