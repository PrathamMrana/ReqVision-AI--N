import re
from utils.preprocess import get_sentences

def extract_artifacts(document_id, document_type, text):
    """
    Extracts structured artifacts from a document based on its classified type.
    Normalizes output to a Common Artifact Model:
    { artifact_id, artifact_type, document_id, document_type, text, section, metadata }
    """
    artifacts = []
    
    # 1. Existing SRS / FRD Logic (Wrap existing functionality exactly as is)
    if document_type in ["SRS", "FRD", "Unknown"]:
        legacy_reqs = get_sentences(text)
        for i, req in enumerate(legacy_reqs):
            artifact_id = req.get("id") or f"{document_type[:3].upper()}-{(i+1):03d}"
            artifacts.append({
                "artifact_id": artifact_id,
                "artifact_type": "Functional Requirement" if document_type == "SRS" else "Specification",
                "document_id": document_id,
                "document_type": document_type,
                "text": req["text"],
                "section": "General",
                "metadata": {"legacy_id": req.get("id")}
            })
            
    # 2. BRD Extraction (Business Requirements)
    elif document_type == "BRD":
        chunks = [c.strip() for c in re.split(r'\n\s*\n', text.strip()) if c.strip()]
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(BR-\d+|OBJ-\d+)[^\w]*(.*)', chunk, re.DOTALL)
            if match:
                art_id = match.group(1)
                art_text = match.group(2).strip()
            else:
                art_id = f"BRD-{(i+1):03d}"
                art_text = chunk
            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "Business Requirement",
                "document_id": document_id,
                "document_type": document_type,
                "text": art_text,
                "section": "Business Needs",
                "metadata": {}
            })
            
    # 3. User Story Extraction
    elif document_type == "User Story":
        chunks = [c.strip() for c in re.split(r'\n\s*\n', text.strip()) if c.strip()]
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(US-\d+)[^\w]*(.*)', chunk, re.DOTALL)
            if match:
                art_id = match.group(1)
                art_text = match.group(2).strip()
            else:
                art_id = f"US-{(i+1):03d}"
                art_text = chunk
            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "Story",
                "document_id": document_id,
                "document_type": document_type,
                "text": art_text,
                "section": "Backlog",
                "metadata": {}
            })
            
    # 4. Test Case Extraction
    elif document_type == "Test Case":
        chunks = [c.strip() for c in re.split(r'\n\s*\n', text.strip()) if c.strip()]
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(TC-\d+|Test ID:.*)[^\w]*(.*)', chunk, re.DOTALL)
            if match:
                art_id = match.group(1)[:15].strip()
                art_text = match.group(2).strip()
            else:
                art_id = f"TC-{(i+1):03d}"
                art_text = chunk
            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "Test Scenario",
                "document_id": document_id,
                "document_type": document_type,
                "text": art_text,
                "section": "QA",
                "metadata": {}
            })

    # 5. Fallback (Change Request, Release Notes, Meeting Minutes)
    else:
        chunks = [c.strip() for c in re.split(r'\n\s*\n', text.strip()) if c.strip()]
        prefix_map = {"Change Request": "CR", "Release Notes": "RN", "Meeting Minutes": "MOM"}
        prefix = prefix_map.get(document_type, "ART")
        
        for i, chunk in enumerate(chunks):
            artifacts.append({
                "artifact_id": f"{prefix}-{(i+1):03d}",
                "artifact_type": document_type.rstrip('s'),
                "document_id": document_id,
                "document_type": document_type,
                "text": chunk,
                "section": "Content",
                "metadata": {}
            })
            
    return artifacts
