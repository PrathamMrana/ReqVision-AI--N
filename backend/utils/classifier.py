import re

DOCUMENT_SIGNALS = {
    "SRS": [
        "software requirements specification", "functional requirements", 
        "non-functional requirements", "system shall", "system requirements",
        "performance requirements", "security requirements", r"\bFR-\d+\b", r"\bNFR-\d+\b", r"\bREQ-\d+\b"
    ],
    "BRD": [
        "business requirements document", "business objective", "business goals",
        "stakeholders", "business need", "roi", "business scope", "executive summary",
        "business process", r"\bBR-\d+\b", r"\bOBJ-\d+\b"
    ],
    "FRD": [
        "functional requirements document", "functional specification", "system function",
        "input", "output", "process flow", "use case", "precondition", "postcondition", r"\bFS-\d+\b"
    ],
    "User Story": [
        "as a user", "as a member", "as an administrator", "as a librarian", "as a director",
        "i want", "so that", "acceptance criteria", "given", "when", "then",
        "story points", "user stories", "backlog", r"\bUS-\d+\b", r"\bSTORY-\d+\b"
    ],
    "Test Case": [
        "test case", "test id", "test scenario", "expected result", "actual result",
        "pass", "fail", "test steps", "test data", "qa suite", r"\bTC-\d+\b", r"\bTEST-\d+\b"
    ],
    "Change Request": [
        "change request", "requested change", "reason for change", "change impact",
        "approval", "priority", r"\bCR-\d+\b", "rollback plan", "engineering change"
    ],
    "Release Notes": [
        "release notes", "version", "bug fixes", "enhancements", "new features",
        "known issues", "breaking changes", "changelog", r"\bRN-\d+\b"
    ],
    "Meeting Minutes": [
        "meeting minutes", "mom", "attendees", "agenda", "discussion", "decisions",
        "action items", "meeting date", "architecture board", r"\bMOM-\d+\b", r"\bDEC-\d+\b"
    ]
}

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
                scores[doc_type]["score"] += min(matches * 2, 10) # Cap repetition bonus
                matched_signals[doc_type].append(f"Found: '{signal}' (x{matches})")
                    
    # Calculate final scores: (unique_signals * 10) + repetition_bonus
    final_scores = {dt: (val["unique"] * 10) + val["score"] for dt, val in scores.items()}
    
    # Sort by top score
    sorted_types = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
    best_type, best_score = sorted_types[0]
    runner_up_type, runner_up_score = sorted_types[1] if len(sorted_types) > 1 else (None, 0)
    
    if best_score == 0:
        return "Unknown", 0.0, []
        
    # Check for Ambiguity: If the top two scores are very close, it's ambiguous
    if best_score > 0 and (best_score - runner_up_score) <= 5 and runner_up_score > 15:
        # Conflicting strong signals -> Unknown
        ambiguous_signals = matched_signals[best_type] + matched_signals[runner_up_type]
        return "Unknown", 20.0, [f"Ambiguous: Conflicting signals between {best_type} and {runner_up_type}"] + ambiguous_signals

    # Non-ML confidence calculation
    confidence = min((best_score / 45.0) * 100, 99.0)
    
    # Require a minimum threshold (at least 1 solid unique signal + repetition, or 2 unique)
    if confidence < 30.0:
        return "Unknown", round(confidence, 1), matched_signals[best_type]
        
    return best_type, round(confidence, 1), matched_signals[best_type]
