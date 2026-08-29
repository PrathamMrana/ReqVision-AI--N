import re

# Canonical Document Types
CANONICAL_DOCUMENT_TYPES = [
    "BRD",
    "SRS",
    "FRD",
    "USER_STORY",
    "TEST_CASE",
    "CHANGE_REQUEST",
    "MEETING_MINUTES",
    "RELEASE_NOTES",
    "UNKNOWN"
]

DOCUMENT_SIGNALS = {
    "SRS": [
        "software requirements specification", "software requirements", "functional requirements", 
        "non-functional requirements", "system shall", "system requirements",
        "performance requirements", "security requirements", r"\bFR-\d+\b", r"\bNFR-\d+\b", r"\bREQ-\d+\b"
    ],
    "BRD": [
        "business requirements document", "business requirements", "business objective", "business goals",
        "stakeholders", "business need", "roi", "business scope", "executive summary",
        "business process", r"\bBR-\d+\b", r"\bOBJ-\d+\b"
    ],
    "FRD": [
        "functional requirements document", "functional specification", "system function",
        "subsystem architecture", "process flow", "component architecture", "interface specification",
        "use case", "precondition", "postcondition", r"\bFS-\d+\b"
    ],
    "USER_STORY": [
        "as a user", "as a rider", "as a student", "as a driver", "as a member", "as an administrator",
        "as a librarian", "as a director", "as a manager", "as a staff",
        "i want", "so that", "acceptance criteria", "given", "when", "then",
        "story points", "user stories", "product backlog", "sprint backlog", r"\bUS-\d+\b", r"\bSTORY-\d+\b"
    ],
    "TEST_CASE": [
        "test case", "test id", "test scenario", "expected result", "actual result",
        "pass", "fail", "test steps", "test data", "qa suite", "verification suite", r"\bTC-\d+\b", r"\bTEST-\d+\b"
    ],
    "CHANGE_REQUEST": [
        "change request", "change requests", "requested change", "reason for change", "change impact",
        "approval", "priority", r"\bCR-\d+\b", "rollback plan", "engineering change"
    ],
    "RELEASE_NOTES": [
        "release notes", "version", "bug fixes", "enhancements", "new features",
        "known issues", "breaking changes", "changelog", r"\bRN-\d+\b"
    ],
    "MEETING_MINUTES": [
        "meeting minutes", "mom", "attendees", "agenda", "discussion", "decisions",
        "action items", "meeting date", "architecture board", "review board", r"\bMOM-\d+\b", r"\bDEC-\d+\b"
    ]
}

def normalize_document_type(doc_type_str):
    """
    Normalizes any string or case representation into the canonical document type enum.
    """
    if not doc_type_str:
        return "UNKNOWN"
    norm = str(doc_type_str).strip().upper().replace(" ", "_").replace("-", "_")
    if norm in ["USER_STORY", "USER_STORIES", "USERSTORY"]:
        return "USER_STORY"
    if norm in ["TEST_CASE", "TEST_CASES", "TESTCASE", "QA"]:
        return "TEST_CASE"
    if norm in ["CHANGE_REQUEST", "CHANGE_REQUESTS", "CHANGEREQUEST", "CR"]:
        return "CHANGE_REQUEST"
    if norm in ["MEETING_MINUTES", "MEETING_MINS", "MOM"]:
        return "MEETING_MINUTES"
    if norm in ["FUNCTIONAL_SPECIFICATION", "FUNCTIONAL_REQUIREMENTS_DOCUMENT", "FRD", "FUNCTIONAL_SPEC"]:
        return "FRD"
    if norm in ["BUSINESS_REQUIREMENTS_DOCUMENT", "BUSINESS_REQUIREMENT", "BRD"]:
        return "BRD"
    if norm in ["SOFTWARE_REQUIREMENTS_SPECIFICATION", "SYSTEM_REQUIREMENTS_SPECIFICATION", "SRS"]:
        return "SRS"
    if norm in ["RELEASE_NOTES", "RELEASE_NOTE", "RN"]:
        return "RELEASE_NOTES"
    return "UNKNOWN"

def classify_document(text, filename=""):
    """
    Analyzes document text to determine document type.
    Filename is explicitly ignored for scoring.
    """
    text_lower = text.lower()
    
    scores = {doc_type: {"score": 0, "unique": 0} for doc_type in DOCUMENT_SIGNALS}
    matched_signals = {doc_type: [] for doc_type in DOCUMENT_SIGNALS}
    
    # Scan text for signals
    for doc_type, signals in DOCUMENT_SIGNALS.items():
        for signal in signals:
            matches = 0
            if signal.startswith(r"\b"):
                matches = len(re.findall(signal, text, re.IGNORECASE))
            else:
                matches = text_lower.count(signal)
                
            if matches > 0:
                scores[doc_type]["unique"] += 1
                scores[doc_type]["score"] += min(matches * 3, 15) # Stronger weight for explicit signals
                matched_signals[doc_type].append(f"Found: '{signal}' (x{matches})")
                    
    # Calculate final scores: (unique_signals * 10) + repetition_bonus
    final_scores = {dt: (val["unique"] * 10) + val["score"] for dt, val in scores.items()}
    
    # Sort by top score
    sorted_types = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
    best_type, best_score = sorted_types[0]
    runner_up_type, runner_up_score = sorted_types[1] if len(sorted_types) > 1 else (None, 0)
    
    if best_score == 0:
        return "UNKNOWN", 0.0, []
        
    # Check for Ambiguity: If the top two scores are very close, it's ambiguous
    if best_score > 0 and (best_score - runner_up_score) <= 5 and runner_up_score > 20:
        ambiguous_signals = matched_signals[best_type] + matched_signals[runner_up_type]
        return "UNKNOWN", 20.0, [f"Ambiguous: Conflicting signals between {best_type} and {runner_up_type}"] + ambiguous_signals

    confidence = min((best_score / 45.0) * 100, 99.0)
    
    if confidence < 25.0:
        return "UNKNOWN", round(confidence, 1), matched_signals[best_type]
        
    return best_type, round(confidence, 1), matched_signals[best_type]
