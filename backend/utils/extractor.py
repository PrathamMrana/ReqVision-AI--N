import re
from typing import Tuple, List, Dict
from utils.classifier import normalize_document_type

# Canonical Artifact Types Enum
CANONICAL_ARTIFACT_TYPES = [
    "BRD_REQUIREMENT",
    "FUNCTIONAL_REQUIREMENT",
    "NON_FUNCTIONAL_REQUIREMENT",
    "FUNCTIONAL_SPECIFICATION",
    "USER_STORY",
    "TEST_CASE",
    "CHANGE_REQUEST",
    "DECISION",
    "ACTION_ITEM",
    "UNKNOWN"
]

def determine_canonical_artifact_type(art_id: str, doc_type: str) -> Tuple[str, str]:
    """
    Determines the canonical artifact_type and document_type based on ID prefix
    and document type.
    Prioritizes explicit structural signals when present, and routes generic/un-prefixed
    artifacts via the classified document layer.
    """
    norm_dt = normalize_document_type(doc_type)
    id_upper = (art_id or "").upper().strip()
    
    # 1. Explicit ID prefix pattern matching (Semantic Layer Identity)
    if re.match(r'^NFR[-_]?\d+', id_upper):
        return "NON_FUNCTIONAL_REQUIREMENT", "SRS"
    if re.match(r'^DEC[-_]?\d+', id_upper):
        return "DECISION", "MEETING_MINUTES"
    if re.match(r'^(?:MOM|ACT|MIN|MEET)[-_]?\d+', id_upper):
        return "ACTION_ITEM", "MEETING_MINUTES"
    if re.match(r'^(?:FS|FRD|CAP|SPEC|DSG|FDD|COMP|MOD|FUNC)[-_]?\d+', id_upper):
        return "FUNCTIONAL_SPECIFICATION", "FRD"
    if re.match(r'^(?:US|STORY|ST|AGILE)[-_]?\d+', id_upper):
        return "USER_STORY", "USER_STORY"
    if re.match(r'^(?:TC|TEST|QA|VERIF|TS)[-_]?\d+', id_upper):
        return "TEST_CASE", "TEST_CASE"
    if re.match(r'^(?:CR|RFC|ECR|ECO|CHG)[-_]?\d+', id_upper):
        return "CHANGE_REQUEST", "CHANGE_REQUEST"
    if re.match(r'^(?:BR|BUS|OBJ|BN|OPS|RQ)[-_]?\d+', id_upper):
        return "BRD_REQUIREMENT", "BRD"
    if re.match(r'^(?:FR|SRS|SYS|REQ|FN)[-_]?\d+', id_upper):
        return "FUNCTIONAL_REQUIREMENT", "SRS"
    if re.match(r'^(?:RN|REL|VER|PATCH)[-_]?\d+', id_upper):
        return "RELEASE_NOTES", "RELEASE_NOTES"
        
    # 2. Classified Document Type Routing (For generic IDs like ART-001, ITEM-001, FEAT-001, etc.)
    doc_layer_map = {
        "BRD": ("BRD_REQUIREMENT", "BRD"),
        "SRS": ("FUNCTIONAL_REQUIREMENT", "SRS"),
        "FRD": ("FUNCTIONAL_SPECIFICATION", "FRD"),
        "USER_STORY": ("USER_STORY", "USER_STORY"),
        "TEST_CASE": ("TEST_CASE", "TEST_CASE"),
        "CHANGE_REQUEST": ("CHANGE_REQUEST", "CHANGE_REQUEST"),
        "MEETING_MINUTES": ("ACTION_ITEM", "MEETING_MINUTES"),
        "RELEASE_NOTES": ("RELEASE_NOTES", "RELEASE_NOTES")
    }
    
    if norm_dt in doc_layer_map:
        return doc_layer_map[norm_dt]

    return "UNKNOWN", norm_dt if norm_dt != "UNKNOWN" else "UNKNOWN"

def get_raw_chunks(text):
    """
    Splits text into meaningful requirement statements/paragraphs.
    Filters out pure document headers/metadata rows without requirement tags.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    chunks = []
    
    header_patterns = [
        r'^(business requirements document|software requirements specification|functional requirements document|functional specification|user stories|test case specification|change request|change requests|meeting minutes)\b',
        r'^(stakeholders|business objective|scope|functional specification|attendees|agenda|discussion|date|author|version|table of contents):\s*.*$'
    ]
    
    for line in lines:
        is_header = any(re.match(hp, line, re.IGNORECASE) for hp in header_patterns)
        has_req_tag = bool(re.search(r'\b[A-Z]{1,6}[-_]?\d{1,5}\b', line))
        
        # If it is a header and does not have an explicit requirement identifier, drop it
        if is_header and not has_req_tag:
            continue
        chunks.append(line)
        
    return chunks

def extract_artifacts(document_id, document_type, text, document_name=""):
    """
    Extracts structured artifacts from a document.
    Normalizes output to the Canonical Immutable Artifact Model:
    { artifact_id, artifact_type, document_id, document_type, document_name, text, section, metadata }
    Preserves strict artifact boundaries and prevents title pollution.
    """
    norm_doc_type = normalize_document_type(document_type)
    artifacts = []
    chunks = get_raw_chunks(text)
    
    has_explicit_ids = any(re.search(r'\b[A-Z]{1,6}[-_]?\d{1,5}\b', chunk) for chunk in chunks)
    
    prefix_map = {
        "BRD": ("BR", "BRD_REQUIREMENT", "Business Needs"),
        "SRS": ("FR", "FUNCTIONAL_REQUIREMENT", "System Requirements"),
        "FRD": ("FS", "FUNCTIONAL_SPECIFICATION", "Subsystem Architecture"),
        "USER_STORY": ("US", "USER_STORY", "Sprint Backlog"),
        "TEST_CASE": ("TC", "TEST_CASE", "QA & Verification"),
        "CHANGE_REQUEST": ("CR", "CHANGE_REQUEST", "Engineering Change"),
        "MEETING_MINUTES": ("MOM", "ACTION_ITEM", "Architecture Board"),
        "RELEASE_NOTES": ("RN", "RELEASE_NOTES", "Changelog")
    }
    
    default_pfx, default_type, default_sec = prefix_map.get(norm_doc_type, ("ART", "UNKNOWN", "General"))
    
    extracted_count = 0
    for chunk in chunks:
        # Regex for ID tag at the beginning of the chunk or within the first 25 characters
        id_match = re.search(r'\b([A-Z]{1,6}[-_]?\d{1,5})\b', chunk[:25])
        
        if id_match:
            art_id = id_match.group(1).upper()
            art_type, art_doc_type = determine_canonical_artifact_type(art_id, norm_doc_type)
            
            # Clean up the text by removing the ID prefix if it starts with it
            art_text = re.sub(r'^[A-Z]{1,6}[-_]?\d{1,5}[^\w]*', '', chunk).strip()
            if not art_text:
                art_text = chunk
                
            extracted_count += 1
            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": art_type,
                "document_id": document_id,
                "document_type": art_doc_type,
                "document_name": document_name,
                "text": art_text,
                "section": default_sec,
                "metadata": {"raw_line": chunk}
            })
        elif not has_explicit_ids:
            if len(chunk) < 30 and not re.search(r'[.!?]$', chunk):
                continue
                
            extracted_count += 1
            art_id = f"{default_pfx}-{extracted_count:03d}"
            art_type, art_doc_type = determine_canonical_artifact_type(art_id, norm_doc_type)
            artifacts.append({
                "artifact_id": art_id,
                "artifact_type": art_type,
                "document_id": document_id,
                "document_type": art_doc_type,
                "document_name": document_name,
                "text": chunk,
                "section": default_sec,
                "metadata": {"raw_line": chunk}
            })

    return artifacts

