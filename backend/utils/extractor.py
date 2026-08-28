import re

def get_raw_chunks(text):
    """
    Splits text into meaningful requirement statements/paragraphs,
    supporting both single-newline paragraphs (docx/txt) and double-newline blocks.
    Filters out pure metadata/header rows.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    chunks = []
    
    header_patterns = [
        r'^(business requirements document|software requirements specification|functional requirements document|user stories|test case specification|change request|meeting minutes)\b',
        r'^(stakeholders|business objective|scope|functional specification|attendees|agenda|discussion|date|author|version|table of contents):\s*.*$'
    ]
    
    for line in lines:
        is_header = any(re.match(hp, line, re.IGNORECASE) for hp in header_patterns)
        has_req_tag = bool(re.search(r'\b[A-Z]{2,4}-\d+\b', line))
        
        # If it is a header and does not have an explicit requirement identifier, drop it
        if is_header and not has_req_tag:
            continue
        chunks.append(line)
        
    return chunks

def extract_artifacts(document_id, document_type, text):
    """
    Extracts structured artifacts from a document based on its classified type.
    Normalizes output to a Common Artifact Model:
    { artifact_id, artifact_type, document_id, document_type, text, section, metadata }
    Prevents document title pollution and preserves strict artifact boundaries.
    """
    artifacts = []
    chunks = get_raw_chunks(text)
    
    # Check if the document contains explicit IDs anywhere
    has_explicit_ids = any(re.search(r'\b[A-Z]{2,4}-\d+\b', chunk) for chunk in chunks)
    
    # Prefix mapping by document type
    prefix_map = {
        "BRD": ("BR", "Business Requirement", "Business Needs"),
        "SRS": ("FR", "Functional Requirement", "System Requirements"),
        "FRD": ("FS", "Functional Specification", "Subsystem Architecture"),
        "User Story": ("US", "User Story", "Sprint Backlog"),
        "Test Case": ("TC", "Test Case", "QA & Verification"),
        "Change Request": ("CR", "Change Request", "Engineering Change"),
        "Meeting Minutes": ("MOM", "Meeting Artifact", "Architecture Board"),
        "Release Notes": ("RN", "Release Item", "Changelog")
    }
    
    default_pfx, default_type, default_sec = prefix_map.get(document_type, ("ART", "Artifact", "General"))
    
    extracted_count = 0
    for chunk in chunks:
        # Regex for ID tag at the beginning of the chunk or within the first 20 characters
        id_match = re.search(r'\b([A-Z]{2,4}-\d+)\b', chunk[:25])
        
        if id_match:
            art_id = id_match.group(1).upper()
            # Clean up the text by removing the ID prefix if it starts with it
            art_text = re.sub(r'^[A-Z]{2,4}-\d+[^\w]*', '', chunk).strip()
            if not art_text:
                art_text = chunk
                
            extracted_count += 1
            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": default_type,
                "document_id": document_id,
                "document_type": document_type,
                "text": art_text,
                "section": default_sec,
                "metadata": {"raw_line": chunk}
            })
        elif not has_explicit_ids:
            # Only generate sequential IDs if the document has NO explicit IDs anywhere
            # and ignore short header-like lines (< 30 chars)
            if len(chunk) < 30 and not re.search(r'[.!?]$', chunk):
                continue
                
            extracted_count += 1
            artifacts.append({
                "artifact_id": f"{default_pfx}-{extracted_count:03d}",
                "artifact_type": default_type,
                "document_id": document_id,
                "document_type": document_type,
                "text": chunk,
                "section": default_sec,
                "metadata": {"raw_line": chunk}
            })

    return artifacts
