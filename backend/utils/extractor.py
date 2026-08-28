import re

def get_raw_chunks(text):
    """
    Splits text into meaningful requirement statements/paragraphs,
    supporting both single-newline paragraphs (docx/txt) and double-newline blocks.
    Filters out pure metadata/header rows.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    chunks = []
    
    # Metadata headers that are not individual requirement items
    header_patterns = [
        r'^(business requirements document|software requirements specification|functional requirements document|user stories|test case specification|change request|meeting minutes)\b',
        r'^(stakeholders|business objective|scope|functional specification|attendees|agenda|discussion):\s*.*$'
    ]
    
    for line in lines:
        is_header = any(re.match(hp, line, re.IGNORECASE) for hp in header_patterns)
        # If it has an explicit requirement tag like BR-001 or MOM-601, keep it regardless
        has_req_tag = bool(re.search(r'\b[A-Z]{2,4}-\d+\b', line))
        
        if is_header and not has_req_tag:
            continue
        chunks.append(line)
        
    return chunks if chunks else [text.strip()] if text.strip() else []

def extract_artifacts(document_id, document_type, text):
    """
    Extracts structured artifacts from a document based on its classified type.
    Normalizes output to a Common Artifact Model:
    { artifact_id, artifact_type, document_id, document_type, text, section, metadata }
    """
    artifacts = []
    chunks = get_raw_chunks(text)
    
    # 1. BRD Extraction (Business Requirements)
    if document_type == "BRD":
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(BR-\d+|OBJ-\d+|BRD-\d+)[^\w]*(.*)', chunk, re.DOTALL | re.IGNORECASE)
            if match:
                art_id = match.group(1).upper()
                art_text = match.group(2).strip() or chunk
            else:
                art_id = f"BR-{(i+1):03d}"
                art_text = chunk
                
            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "Business Requirement",
                "document_id": document_id,
                "document_type": "BRD",
                "text": art_text,
                "section": "Business Needs",
                "metadata": {}
            })

    # 2. SRS Extraction (Software / Functional Requirements)
    elif document_type == "SRS":
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(FR-\d+|REQ-\d+|SRS-\d+|NFR-\d+)[^\w]*(.*)', chunk, re.DOTALL | re.IGNORECASE)
            if match:
                art_id = match.group(1).upper()
                art_text = match.group(2).strip() or chunk
            else:
                art_id = f"FR-{(i+1):03d}"
                art_text = chunk

            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "Functional Requirement",
                "document_id": document_id,
                "document_type": "SRS",
                "text": art_text,
                "section": "System Requirements",
                "metadata": {}
            })

    # 3. FRD Extraction (Functional Specifications)
    elif document_type == "FRD":
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(FS-\d+|FRD-\d+|FR-\d+)[^\w]*(.*)', chunk, re.DOTALL | re.IGNORECASE)
            if match:
                art_id = match.group(1).upper()
                art_text = match.group(2).strip() or chunk
            else:
                art_id = f"FS-{(i+1):03d}"
                art_text = chunk

            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "Functional Specification",
                "document_id": document_id,
                "document_type": "FRD",
                "text": art_text,
                "section": "Subsystem Architecture",
                "metadata": {}
            })

    # 4. User Story Extraction
    elif document_type == "User Story":
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(US-\d+|STORY-\d+)[^\w]*(.*)', chunk, re.DOTALL | re.IGNORECASE)
            if match:
                art_id = match.group(1).upper()
                art_text = match.group(2).strip() or chunk
            else:
                art_id = f"US-{(i+1):03d}"
                art_text = chunk

            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "User Story",
                "document_id": document_id,
                "document_type": "User Story",
                "text": art_text,
                "section": "Sprint Backlog",
                "metadata": {}
            })

    # 5. Test Case Extraction
    elif document_type == "Test Case":
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(TC-\d+|TEST-\d+|Test ID:[^\w]*\w+)[^\w]*(.*)', chunk, re.DOTALL | re.IGNORECASE)
            if match:
                art_id = match.group(1).upper().replace("TEST ID:", "").strip()
                art_text = match.group(2).strip() or chunk
            else:
                art_id = f"TC-{(i+1):03d}"
                art_text = chunk

            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "Test Case",
                "document_id": document_id,
                "document_type": "Test Case",
                "text": art_text,
                "section": "QA & Verification",
                "metadata": {}
            })

    # 6. Change Request Extraction
    elif document_type == "Change Request":
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(CR-\d+|RFC-\d+)[^\w]*(.*)', chunk, re.DOTALL | re.IGNORECASE)
            if match:
                art_id = match.group(1).upper()
                art_text = match.group(2).strip() or chunk
            else:
                art_id = f"CR-{(i+1):03d}"
                art_text = chunk

            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "Change Request",
                "document_id": document_id,
                "document_type": "Change Request",
                "text": art_text,
                "section": "Engineering Change",
                "metadata": {}
            })

    # 7. Meeting Minutes Extraction
    elif document_type == "Meeting Minutes":
        for i, chunk in enumerate(chunks):
            match = re.match(r'^(MOM-\d+|DEC-\d+|ACT-\d+)[^\w]*(.*)', chunk, re.DOTALL | re.IGNORECASE)
            if match:
                art_id = match.group(1).upper()
                art_text = match.group(2).strip() or chunk
            else:
                art_id = f"MOM-{(i+1):03d}"
                art_text = chunk

            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": "Meeting Artifact",
                "document_id": document_id,
                "document_type": "Meeting Minutes",
                "text": art_text,
                "section": "Architecture Board",
                "metadata": {}
            })

    # Fallback / Unknown
    else:
        for i, chunk in enumerate(chunks):
            artifacts.append({
                "artifact_id": f"ART-{(i+1):03d}",
                "artifact_type": "Artifact",
                "document_id": document_id,
                "document_type": document_type,
                "text": chunk,
                "section": "General",
                "metadata": {}
            })

    return artifacts
