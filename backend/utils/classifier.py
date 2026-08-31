import re
from typing import Tuple, List, Dict

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

# ── 1. Document Title / Heading Pattern Dictionary (Multi-Regex) ─────────────
# High-weight signals when found near top of document or heading lines
TITLE_PATTERNS = {
    "BRD": [
        r"\b(?:business\s+requirements?(?:\s+document)?|business\s+needs?|business\s+goals?|business\s+objectives?|business\s+capabilities|operational\s+requirements?|operational\s+needs?|operational\s+concept|concept\s+of\s+operations?|enterprise\s+requirements?|stakeholder\s+requirements?|market\s+requirements?(?:\s+document)?|brd)\b",
    ],
    "SRS": [
        r"\b(?:software\s+requirements?(?:\s+specification)?|system\s+requirements?(?:\s+specification)?|system\s+specification|technical\s+requirements?(?:\s+document)?|system\s+capabilities|platform\s+requirements?|engineering\s+requirements?|system\s+behavior(?:\s+specification)?|software\s+specification|srs)\b",
    ],
    "FRD": [
        r"\b(?:functional\s+requirements?(?:\s+document)?|functional\s+specifications?|functional\s+design(?:\s+document)?|functional\s+capabilities|system\s+design\s+capabilities|subsystem\s+design|detailed\s+design(?:\s+document)?|technical\s+design(?:\s+document)?|component\s+architecture|subsystem\s+architecture|functional\s+architecture|module\s+specifications?|frd|fdd)\b",
    ],
    "USER_STORY": [
        r"\b(?:user\s+stor(?:y|ies)(?:\s+backlog)?|agile\s+backlog|sprint\s+backlog|product\s+backlog|user\s+personas?|scrum\s+stories|clinical\s+interface\s+stories|operator\s+stories|client\s+stories|mobile\s+app\s+stories)\b",
    ],
    "TEST_CASE": [
        r"\b(?:test\s+cases?(?:\s+specification)?|verification\s+test\s+cases?|qa\s+suite|verification\s+suite|quality\s+assurance\s+test|validation\s+test\s+plan|system\s+test\s+plan|test\s+procedures?|qa\s+test\s+cases?|qa\s+plan)\b",
    ],
    "CHANGE_REQUEST": [
        r"\b(?:change\s+requests?(?:\s+document)?|engineering\s+change\s+orders?|change\s+proposals?|rfc|ecr|eco|proposed\s+modifications?|engineering\s+change\s+notice)\b",
    ],
    "MEETING_MINUTES": [
        r"\b(?:meeting\s+minutes?|architecture\s+board\s+minutes?|steering\s+committee\s+decisions?|review\s+minutes?|meeting\s+notes?|minutes\s+of\s+meeting|governance\s+board\s+decisions?|mom)\b",
    ],
    "RELEASE_NOTES": [
        r"\b(?:release\s+notes?|version\s+changelog|deployment\s+notes?|release\s+summary|patch\s+notes?)\b",
    ]
}

# ── 2. Structural Section Keywords & Metadata Markers ────────────────────────
SECTION_KEYWORDS = {
    "BRD": [
        "business requirements", "business objective", "business goals", "business needs",
        "stakeholders", "business scope", "roi", "executive summary", "business process",
        "operational concept", "strategic goal", "enterprise capability", "business value",
        "operational need", "concept of operations", "business impact"
    ],
    "SRS": [
        "software requirements", "functional requirements", "non-functional requirements",
        "system requirements", "performance requirements", "security requirements",
        "interface requirements", "system constraints", "reliability requirement",
        "availability requirement", "latency requirement", "throughput requirement",
        "system behavior", "technical specification", "platform requirements", "nfr"
    ],
    "FRD": [
        "functional specification", "functional design", "system function", "subsystem architecture",
        "process flow", "component architecture", "interface specification", "use case",
        "precondition", "postcondition", "data dictionary", "algorithm", "state transition",
        "hardware interface", "driver specification", "internal flow", "database schema",
        "functional capabilities", "subsystem design", "component design", "data flow"
    ],
    "USER_STORY": [
        "user stories", "user story", "story points", "acceptance criteria", "sprint backlog",
        "product backlog", "definition of done", "epic", "persona", "user story backlog"
    ],
    "TEST_CASE": [
        "test case", "test id", "test scenario", "expected result", "actual result",
        "test steps", "test data", "qa suite", "verification suite", "pass/fail",
        "pre-conditions", "post-conditions", "test execution", "validation matrix",
        "test plan", "test summary"
    ],
    "CHANGE_REQUEST": [
        "change request", "change requests", "requested change", "reason for change",
        "change impact", "rollback plan", "engineering change", "change justification",
        "change description", "requestor", "approval status", "urgency"
    ],
    "MEETING_MINUTES": [
        "meeting minutes", "attendees", "agenda", "discussion", "decisions",
        "action items", "meeting date", "architecture board", "review board",
        "decision rationale", "consensus", "quorum", "meeting notes"
    ],
    "RELEASE_NOTES": [
        "release notes", "bug fixes", "enhancements", "new features", "known issues",
        "breaking changes", "changelog", "patch", "resolved issues"
    ]
}

# ── 3. Grammatical & Sentence Syntaxes (per line regex) ──────────────────────
SYNTAX_PATTERNS = {
    "USER_STORY": [
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?As an?\s+[\w\s-]+,\s*I\s+want\s+.+?\s+so\s+that\s+",
        r"\bacceptance\s+criteria\b",
        r"\b(?:given|when|then)\b.+\b(?:given|when|then)\b"
    ],
    "TEST_CASE": [
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?Verify\s+(?:that\s+)?",
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?Test\s+(?:that\s+|the\s+|whether\s+)",
        r"\bexpected\s+result\b",
        r"\btest\s+steps?\b",
        r"\bpass\s*/\s*fail\b"
    ],
    "CHANGE_REQUEST": [
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?(?:Change|Add|Remove|Modify|Replace|Upgrade|Migrate)\s+.+?\s+(?:to|in|for|from|by)\s+",
        r"\breason\s+for\s+change\b",
        r"\brollback\s+plan\b",
        r"\bchange\s+impact\b"
    ],
    "MEETING_MINUTES": [
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?(?:Decision|Action\s+Item|Decided|Agreed|Approved|Pending|Rejected|Discussed)[:\s]+",
        r"^\s*Attendees[:\s]+",
        r"^\s*Agenda[:\s]+"
    ],
    "FRD": [
        r"\b(?:modulates|actuates|disengages|fires\s+emergency|interlock|solenoid|ring\s+buffer|driver\s+driver|controller\s+engages|algorithm\s+evaluates|solver\s+computes|packet\s+validator|servo\s+torque|parser\s+service|pipeline\s+ingests|demodulat\w*|duty\s+cycle|pulse\s+sequences?)\b"
    ],
    "SRS": [
        r"\b(?:nfr|non-functional|latency\s+must\s+remain|uptime\s+of\s+at\s+least|shall\s+authenticate|shall\s+be\s+capable\s+of|shall\s+display|feedback\s+latency|throughput\s+must|shall\s+support\s+up\s+to)\b"
    ],
    "BRD": [
        r"\b(?:shall\s+provide\s+a\s+portal|shall\s+enable\s+(?:users|operators|technicians|surgeons|drivers|dispatchers)\s+to|shall\s+automate|shall\s+ensure\s+compliance|business\s+goal|operational\s+need|strategic\s+objective)\b"
    ]
}

# ── 4. Supporting Artifact ID Patterns ─────────────────────────────────────────
ID_PATTERNS = {
    "BRD": r"\b(?:BR|BUS|OBJ|BN|OPS)[-_]?\d+\b",
    "SRS": r"\b(?:FR|SRS|SYS|REQ|NFR|PERF|SEC|FN)[-_]?\d+\b",
    "FRD": r"\b(?:FS|FRD|CAP|SPEC|DSG|FDD|COMP|MOD|FUNC)[-_]?\d+\b",
    "USER_STORY": r"\b(?:US|STORY|ST|AGILE)[-_]?\d+\b",
    "TEST_CASE": r"\b(?:TC|TEST|QA|VERIF|TS)[-_]?\d+\b",
    "CHANGE_REQUEST": r"\b(?:CR|RFC|ECR|ECO|CHG)[-_]?\d+\b",
    "MEETING_MINUTES": r"\b(?:MOM|DEC|ACT|MIN|MEET)[-_]?\d+\b",
    "RELEASE_NOTES": r"\b(?:RN|REL|VER|PATCH)[-_]?\d+\b"
}

# ── 5. Filename Clues (Weak Supporting, +5 pts) ───────────────────────────────
FILENAME_CLUES = {
    "BRD": r"(?:brd|business|operat)",
    "SRS": r"(?:srs|system|software_req)",
    "FRD": r"(?:frd|functional|design|spec)",
    "USER_STORY": r"(?:user_stor|story|backlog)",
    "TEST_CASE": r"(?:test|tc|qa|verif)",
    "CHANGE_REQUEST": r"(?:change|cr|rfc)",
    "MEETING_MINUTES": r"(?:meeting|mom|decision|minutes)",
    "RELEASE_NOTES": r"(?:release|changelog|rn)"
}

def normalize_document_type(doc_type_str: str) -> str:
    """
    Normalizes any string or case representation into the canonical document type enum.
    """
    if not doc_type_str:
        return "UNKNOWN"
    norm = str(doc_type_str).strip().upper().replace(" ", "_").replace("-", "_")
    if norm in ["USER_STORY", "USER_STORIES", "USERSTORY", "STORY", "STORIES", "AGILE_BACKLOG"]:
        return "USER_STORY"
    if norm in ["TEST_CASE", "TEST_CASES", "TESTCASE", "QA", "TESTS", "VERIFICATION_SUITE"]:
        return "TEST_CASE"
    if norm in ["CHANGE_REQUEST", "CHANGE_REQUESTS", "CHANGEREQUEST", "CR", "RFC", "ECR"]:
        return "CHANGE_REQUEST"
    if norm in ["MEETING_MINUTES", "MEETING_MINS", "MOM", "MINUTES", "DECISIONS"]:
        return "MEETING_MINUTES"
    if norm in ["FUNCTIONAL_SPECIFICATION", "FUNCTIONAL_REQUIREMENTS_DOCUMENT", "FRD", "FUNCTIONAL_SPEC", "FUNCTIONAL_DESIGN", "FDD"]:
        return "FRD"
    if norm in ["BUSINESS_REQUIREMENTS_DOCUMENT", "BUSINESS_REQUIREMENT", "BRD", "BUSINESS_NEEDS", "OPERATIONAL_REQUIREMENTS"]:
        return "BRD"
    if norm in ["SOFTWARE_REQUIREMENTS_SPECIFICATION", "SYSTEM_REQUIREMENTS_SPECIFICATION", "SRS", "SYSTEM_SPECIFICATION", "SOFTWARE_SPECIFICATION"]:
        return "SRS"
    if norm in ["RELEASE_NOTES", "RELEASE_NOTE", "RN", "CHANGELOG"]:
        return "RELEASE_NOTES"
    return "UNKNOWN"

def classify_document(text: str, filename: str = "") -> Tuple[str, float, List[str]]:
    """
    Analyzes document content, headings, structural syntaxes, and supporting metadata
    to determine document type in a template-flexible, content-driven manner.
    """
    if not text or not text.strip():
        return "UNKNOWN", 0.0, ["Empty document content"]
        
    text_lower = text.lower()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    top_lines = lines[:6]
    top_text = " ".join(top_lines).lower()
    
    scores = {dt: 0 for dt in TITLE_PATTERNS}
    evidence = {dt: [] for dt in TITLE_PATTERNS}
    
    # 1. Document Title / Top Heading Match (High Weight)
    for dt, patterns in TITLE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, top_text, re.IGNORECASE):
                scores[dt] += 40
                evidence[dt].append(f"Top title match: {pat}")
                break
                
    # 2. Section Headings Throughout Text
    for dt, kw_list in SECTION_KEYWORDS.items():
        for kw in kw_list:
            cnt = text_lower.count(kw)
            if cnt > 0:
                pts = min(cnt * 5, 20)
                scores[dt] += pts
                evidence[dt].append(f"Section keyword [{kw}] (x{cnt})")
                
    # 3. Sentence / Grammatical Syntaxes
    for dt, patterns in SYNTAX_PATTERNS.items():
        for pat in patterns:
            matches = len(re.findall(pat, text, re.IGNORECASE | re.MULTILINE))
            if matches > 0:
                pts = min(matches * 8, 30)
                scores[dt] += pts
                evidence[dt].append(f"Syntax pattern match (x{matches})")
                
    # 4. Artifact ID Supporting Evidence
    for dt, id_pat in ID_PATTERNS.items():
        id_matches = len(re.findall(id_pat, text, re.IGNORECASE))
        if id_matches > 0:
            pts = min(id_matches * 4, 15)
            scores[dt] += pts
            evidence[dt].append(f"ID prefix signal (x{id_matches})")
            
    # 5. Filename Supporting Evidence (Weak)
    if filename:
        fn_lower = filename.lower()
        for dt, fn_pat in FILENAME_CLUES.items():
            if re.search(fn_pat, fn_lower):
                scores[dt] += 5
                evidence[dt].append(f"Filename clue match")
                
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_type, best_score = sorted_scores[0]
    runner_up_type, runner_up_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)
    
    if best_score < 15:
        return "UNKNOWN", 0.0, ["Insufficient classification signals across document"]
        
    confidence = min(round((best_score / 60.0) * 100, 1), 99.0)
    
    # Check ambiguity if top two are close and non-zero
    if best_score > 0 and (best_score - runner_up_score) <= 5 and runner_up_score >= 35:
        return "UNKNOWN", 25.0, [f"Ambiguous: {best_type} ({best_score}) vs {runner_up_type} ({runner_up_score})"]
        
    return best_type, confidence, evidence[best_type]

