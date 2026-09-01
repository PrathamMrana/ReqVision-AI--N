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
        "operational need", "concept of operations", "business impact", "business case",
        "market requirements", "business rules", "business constraints", "business drivers",
        "competitive analysis", "return on investment", "business benefits", "strategic objective",
        "organizational goals", "business vision", "business mission", "business strategy",
        "business requirement",
    ],
    "SRS": [
        "software requirements", "functional requirements", "non-functional requirements",
        "system requirements", "performance requirements", "security requirements",
        "interface requirements", "system constraints", "reliability requirement",
        "availability requirement", "latency requirement", "throughput requirement",
        "system behavior", "technical specification", "platform requirements", "nfr",
        "scalability requirements", "compliance requirements", "audit requirements",
        "api requirements", "data requirements", "integration requirements",
        "system interfaces", "external interfaces", "software interfaces", "hardware interfaces",
    ],
    "FRD": [
        "functional specification", "functional design", "system function", "subsystem architecture",
        "process flow", "component architecture", "interface specification", "use case",
        "precondition", "postcondition", "data dictionary", "algorithm", "state transition",
        "hardware interface", "driver specification", "internal flow", "database schema",
        "functional capabilities", "subsystem design", "component design", "data flow",
        "detailed design", "module design", "api specification", "service specification",
        "class diagram", "sequence diagram", "entity relationship", "data model",
    ],
    "USER_STORY": [
        "user stories", "user story", "story points", "acceptance criteria", "sprint backlog",
        "product backlog", "definition of done", "epic", "persona", "user story backlog",
        "feature", "agile", "scrum", "kanban", "backlog refinement", "sprint planning",
        "story estimate", "as a user", "i want to", "so that",
    ],
    "TEST_CASE": [
        "test case", "test id", "test scenario", "expected result", "actual result",
        "test steps", "test data", "qa suite", "verification suite", "pass/fail",
        "pre-conditions", "post-conditions", "test execution", "validation matrix",
        "test plan", "test summary", "pass fail", "expected outcome", "test procedure",
        "test objective", "test coverage", "test environment", "defect", "bug report",
        "regression test", "smoke test", "integration test", "system test",
        "verification test",
    ],
    "CHANGE_REQUEST": [
        "change request", "change requests", "requested change", "reason for change",
        "change impact", "rollback plan", "engineering change", "change justification",
        "change description", "requestor", "approval status", "urgency", "change log",
        "modification request", "proposed change", "change management", "change control",
    ],
    "MEETING_MINUTES": [
        "meeting minutes", "attendees", "agenda", "discussion", "decisions",
        "action items", "meeting date", "architecture board", "review board",
        "decision rationale", "consensus", "quorum", "meeting notes",
        "action item", "decided", "agreed", "next steps", "follow-up",
        "attendee", "minutes of meeting",
    ],
    "RELEASE_NOTES": [
        "release notes", "bug fixes", "enhancements", "new features", "known issues",
        "breaking changes", "changelog", "patch", "resolved issues", "deprecated",
        "migration guide", "upgrade notes", "version history",
    ]
}

# ── 3. Grammatical & Sentence Syntaxes (per line regex) ──────────────────────
SYNTAX_PATTERNS = {
    "USER_STORY": [
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?As an?\s+[\w\s-]+,\s*I\s+want\s+.+?\s+so\s+that\s+",
        r"\bacceptance\s+criteria\b",
        r"\b(?:given|when|then)\b.+\b(?:given|when|then)\b",
        r"^\s*Story[\s:]+",
        r"^\s*Feature[\s:]+",
        r"\bstory\s+points?\b",
        r"\bdefinition\s+of\s+done\b",
        r"\bthe\s+(?:user|driver|customer|admin|operator|technician|patient|passenger|employee|rider|dispatcher)\s+(?:should|can|must|wants?\s+to|needs?\s+to|shall|is\s+able\s+to)\s+(?:be\s+able\s+to\s+)?\w+",
    ],
    "TEST_CASE": [
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?Verify\s+(?:that\s+)?",
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?Test\s+(?:that\s+|the\s+|whether\s+)",
        r"\bexpected\s+result\b",
        r"\btest\s+steps?\b",
        r"\bpass\s*/\s*fail\b",
        r"\bpre-?conditions?\b",
        r"\btest\s+data\b",
        r"\bactual\s+result\b",
        r"\btest\s+scenario\b",
        r"\bstep\s+\d+\b.{0,30}(?:navigate|click|enter|select|verify|assert|check|submit)",
    ],
    "CHANGE_REQUEST": [
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?(?:Change|Add|Remove|Modify|Replace|Upgrade|Migrate)\s+.+?\s+(?:to|in|for|from|by)\s+",
        r"\breason\s+for\s+change\b",
        r"\brollback\s+plan\b",
        r"\bchange\s+impact\b",
        r"\bchange\s+justification\b",
    ],
    "MEETING_MINUTES": [
        r"^\s*(?:[A-Z0-9_-]+[:\s]+)?(?:Decision|Action\s+Item|Decided|Agreed|Approved|Pending|Rejected|Discussed)[:\s]+",
        r"^\s*Attendees[:\s]+",
        r"^\s*Agenda[:\s]+",
        r"\baction\s+items?\b",
        r"\bnext\s+steps?\b",
    ],
    "FRD": [
        r"\b(?:modulates|actuates|disengages|fires\s+emergency|interlock|solenoid|ring\s+buffer|controller\s+engages|algorithm\s+evaluates|solver\s+computes|packet\s+validator|servo\s+torque|parser\s+service|pipeline\s+ingests|demodulat\w*|duty\s+cycle|pulse\s+sequences?)\b",
        r"\b(?:precondition|postcondition|state\s+transition|data\s+flow|process\s+flow)\b",
        r"\b(?:api\s+endpoint|rest\s+api|database\s+schema|data\s+model|entity\s+relationship|class\s+diagram|sequence\s+diagram)\b",
    ],
    "SRS": [
        r"\b(?:nfr|non-functional|latency\s+must\s+remain|uptime\s+of\s+at\s+least|shall\s+authenticate|shall\s+be\s+capable\s+of|shall\s+display|feedback\s+latency|throughput\s+must|shall\s+support\s+up\s+to)\b",
        r"\b(?:the\s+system|the\s+software|the\s+application|the\s+platform|the\s+api)\s+(?:shall|must|will)\s+(?:support|handle|provide|maintain|ensure|comply|authenticate|validate|encrypt|process|store|manage)\b",
        r"\b(?:availability\s+requirement|reliability\s+requirement|security\s+requirement|performance\s+requirement|scalability\s+requirement)\b",
        r"\b(?:maximum\s+(?:response|latency|load)\s+time|minimum\s+uptime|concurrent\s+users?\s+(?:supported|limit))\b",
    ],
    "BRD": [
        r"\b(?:shall\s+provide\s+a\s+portal|shall\s+enable\s+(?:users|operators|technicians|surgeons|drivers|dispatchers)\s+to|shall\s+automate|shall\s+ensure\s+compliance|business\s+goal|operational\s+need|strategic\s+objective)\b",
        r"\b(?:the\s+organization|the\s+company|the\s+business|the\s+enterprise|the\s+client)\s+(?:requires?|needs?|wants?|must\s+have|expects?)\b",
        r"\b(?:roi|return\s+on\s+investment|payback\s+period|cost\s+savings?|operational\s+costs?|business\s+value)\b",
        r"\bstakeholder\s+(?:requirement|need|expectation|concern)\b",
    ],
    "RELEASE_NOTES": [
        r"\b(?:version\s+\d+\.\d+|v\d+\.\d+[\.\d]*)\b",
        r"\b(?:fixed\s+(?:a\s+)?(?:bug|issue|defect)|resolved\s+(?:a\s+)?(?:bug|issue|defect))\b",
        r"\b(?:new\s+feature|added\s+support\s+for|deprecated|breaking\s+change|migration\s+required)\b",
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

# ── 5. Filename Clues (Weak Supporting, +8 pts) ───────────────────────────────
FILENAME_CLUES = {
    "BRD": r"(?:brd|business[\._-]req|business[\._-]requirement|operat[\._-]req)",
    "SRS": r"(?:srs|system[\._-]req|software[\._-]req|sys[\._-]req)",
    "FRD": r"(?:frd|functional[\._-]|design[\._-]|spec[\._-]|fdd[\._-])",
    "USER_STORY": r"(?:user[\._-]stor|stories|backlog|us[\._-])",
    "TEST_CASE": r"(?:test[\._-]|tc[\._-]|qa[\._-]|verif[\._-])",
    "CHANGE_REQUEST": r"(?:change[\._-]|cr[\._-]|rfc[\._-])",
    "MEETING_MINUTES": r"(?:meeting|mom[\._-]|decision|minutes[\._-])",
    "RELEASE_NOTES": r"(?:release[\._-]|changelog|rn[\._-]|patch[\._-])"
}

# ── 6. Narrative Signals — real-world writing patterns by type ─────────────────
NARRATIVE_SIGNALS = {
    "BRD": [
        r"\b(?:the\s+(?:organization|company|business|enterprise|client|customer))\s+(?:requires?|needs?|wants?|must\s+have|expects?)\b",
        r"\bto\s+(?:reduce|improve|increase|enhance|optimize|automate|streamline)\s+.{5,50}\b",
        r"\b(?:pain\s+point|bottleneck|inefficiency|manual\s+process|cost\s+reduction|operational\s+efficiency)\b",
        r"\bstakeholder\s+(?:requirement|need|expectation|concern)\b",
        r"\boperational\s+(?:need|requirement|efficiency|cost|benefit|goal)\b",
        r"\b(?:increase\s+revenue|reduce\s+cost|improve\s+customer\s+satisfaction|competitive\s+advantage)\b",
        r"\b(?:business\s+owner|product\s+owner|executive\s+stakeholder|business\s+sponsor)\b",
    ],
    "SRS": [
        r"\b(?:the\s+system|the\s+software|the\s+application|the\s+platform|the\s+api)\s+(?:shall|must|will|should)\s+\w+",
        r"\b(?:functional\s+requirement|non-functional\s+requirement|system\s+constraint)\b",
        r"\b(?:concurrent\s+users?|throughput|response\s+time|uptime|availability|latency|sla)\b",
        r"\b(?:encryption|authentication|authorization|ssl|tls|https|oauth|jwt|mfa|2fa|single\s+sign.on|sso)\b",
        r"\b(?:the\s+(?:service|module|component|interface|endpoint))\s+(?:shall|must|will)\s+\w+",
        r"\b(?:the\s+system\s+(?:shall|must)\s+(?:be\s+able\s+to|support|provide|maintain|handle|ensure))\b",
    ],
    "FRD": [
        r"\b(?:the\s+(?:component|module|service|handler|processor|engine|pipeline|parser|controller|driver))\s+(?:shall|must|will|handles?|processes?|parses?|validates?|computes?)\b",
        r"\b(?:input\s+parameter|output\s+parameter|return\s+value|error\s+code|exception)\b",
        r"\b(?:data\s+flow|control\s+flow|event\s+handler|callback|trigger|webhook)\b",
        r"\b(?:database|schema|table|index|query|stored\s+procedure|migration|orm)\b",
        r"\b(?:endpoint|resource\s+path|http\s+method|request\s+body|response\s+body|status\s+code)\b",
    ],
    "USER_STORY": [
        r"\bas\s+(?:a|an)\s+\w+(?:\s+\w+)?,?\s+(?:i\s+want|i\s+need|i\s+should\s+be\s+able)\b",
        r"\bthe\s+(?:user|driver|customer|admin|operator|technician|patient|passenger|employee|manager|rider|dispatcher)\s+(?:should|can|must|wants?\s+to|needs?\s+to|shall|is\s+able\s+to)\s+(?:be\s+able\s+to\s+)?\w+",
        r"\bwhen\s+the\s+(?:user|driver|customer|admin|operator)\s+(?:clicks?|selects?|submits?|opens?|navigates?|uploads?|enters?)\b",
        r"\b(?:priority|story\s+points?|sprint|backlog|epic|feature|iteration)\s*[:\-]\s*(?:high|medium|low|\d+)\b",
    ],
    "TEST_CASE": [
        r"\b(?:verify\s+that|confirm\s+that|ensure\s+that|validate\s+that|assert\s+that)\b",
        r"\bexpected\s+(?:result|behavior|output|response|outcome)\b",
        r"\b(?:steps?\s+to\s+(?:reproduce|test)|test\s+(?:step|procedure|script))\b",
        r"\b(?:pass|fail)\s*[:/]?\s*(?:pass|fail)\b",
        r"\b(?:tc-|test\s+case\s+id|test\s+id)\s*[:\-]?\s*\w+\b",
    ],
    "CHANGE_REQUEST": [
        r"\b(?:requested\s+by|approved\s+by|submitted\s+by|change\s+owner)\b",
        r"\b(?:impact\s+assessment|risk\s+assessment|rollback\s+plan)\b",
        r"\b(?:modification\s+to|update\s+to|enhancement\s+of|fix\s+for)\s+.{5,50}\b",
    ],
    "MEETING_MINUTES": [
        r"\b(?:attendees?|participants?|present)\s*[:\-]",
        r"\b(?:date|time|location|venue)\s*[:\-]\s*\d",
        r"\b(?:action\s+item|follow-up|owner|due\s+date)\s*[:\-]",
        r"\b(?:decided|resolved|agreed|approved|rejected|deferred|tabled)\s+(?:that|to)\b",
    ],
    "RELEASE_NOTES": [
        r"\b(?:what['']?s\s+new|what\s+changed|breaking\s+changes?|known\s+issues?)\b",
        r"\b(?:bug\s+fix|hot\s+fix|patch\s+note|release\s+highlight|release\s+date)\b",
    ]
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
    Classifies document type from content.  Works correctly for:
      - Documents with explicit type headings ("Business Requirements Document")
      - Documents without headings (narrative BRDs, Jira-style stories, numbered spec lists)
      - Real-world PDF/DOCX/TXT with mixed formatting
      - Numbered section lists, bullet-point requirements, table-format test cases
    """
    if not text or not text.strip():
        return "UNKNOWN", 0.0, ["Empty document content"]
        
    text_lower = text.lower()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    top_lines = lines[:8]
    top_text = " ".join(top_lines).lower()
    
    scores = {dt: 0 for dt in TITLE_PATTERNS}
    evidence = {dt: [] for dt in TITLE_PATTERNS}
    
    # 1. Document Title / Top Heading Match (High Weight: 40 pts)
    for dt, patterns in TITLE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, top_text, re.IGNORECASE):
                scores[dt] += 40
                evidence[dt].append(f"Title match: {dt}")
                break
                
    # 2. Section Headings Throughout Text (Up to 20 pts per keyword)
    for dt, kw_list in SECTION_KEYWORDS.items():
        for kw in kw_list:
            cnt = text_lower.count(kw)
            if cnt > 0:
                pts = min(cnt * 5, 20)
                scores[dt] += pts
                evidence[dt].append(f"Section keyword [{kw}] (x{cnt})")
                
    # 3. Sentence / Grammatical Syntaxes (Up to 24 pts per pattern)
    for dt, patterns in SYNTAX_PATTERNS.items():
        for pat in patterns:
            matches = len(re.findall(pat, text, re.IGNORECASE | re.MULTILINE))
            if matches > 0:
                pts = min(matches * 6, 24)
                scores[dt] += pts
                evidence[dt].append(f"Syntax pattern match (x{matches})")
    
    # 4. Narrative Signals — real-world writing styles (Up to 18 pts per type)
    for dt, patterns in NARRATIVE_SIGNALS.items():
        narrative_hits = 0
        for pat in patterns:
            matches = len(re.findall(pat, text, re.IGNORECASE | re.MULTILINE))
            narrative_hits += matches
        if narrative_hits > 0:
            pts = min(narrative_hits * 3, 18)
            scores[dt] += pts
            evidence[dt].append(f"Narrative signal (x{narrative_hits})")
                
    # 5. Artifact ID Supporting Evidence (Up to 15 pts)
    for dt, id_pat in ID_PATTERNS.items():
        id_matches = len(re.findall(id_pat, text, re.IGNORECASE))
        if id_matches > 0:
            pts = min(id_matches * 4, 15)
            scores[dt] += pts
            evidence[dt].append(f"ID prefix signal (x{id_matches})")
            
    # 6. Filename Supporting Evidence (+8 pts)
    if filename:
        fn_lower = filename.lower()
        for dt, fn_pat in FILENAME_CLUES.items():
            if re.search(fn_pat, fn_lower):
                scores[dt] += 8
                evidence[dt].append(f"Filename clue match")
    
    # 7. Section heading structure analysis
    section_heading_lines = [l for l in lines if 5 < len(l) < 80 and not l.endswith('.') and (l[0].isupper() or l[0].isdigit())]
    if len(section_heading_lines) > 2:
        section_text = "\n".join(section_heading_lines).lower()
        if re.search(r'\b(?:business\s+(?:goals?|objectives?|needs?|scope|value|impact|requirements?)|stakeholders?|roi|executive\s+summary)\b', section_text):
            scores["BRD"] += 12
            evidence["BRD"].append("Section heading: business-oriented structure")
        if re.search(r'\b(?:functional\s+requirements?|non-functional\s+requirements?|system\s+constraints?|performance\s+requirements?|security\s+requirements?)\b', section_text):
            scores["SRS"] += 12
            evidence["SRS"].append("Section heading: requirements specification structure")
        if re.search(r'\b(?:use\s+cases?|data\s+dictionary|state\s+transition|data\s+flow|component\s+design|api\s+specification|database\s+schema)\b', section_text):
            scores["FRD"] += 12
            evidence["FRD"].append("Section heading: functional design structure")
        if re.search(r'\b(?:test\s+(?:case|plan|scenario|objective|coverage)|qa\s+(?:suite|plan)|verification|expected\s+result)\b', section_text):
            scores["TEST_CASE"] += 12
            evidence["TEST_CASE"].append("Section heading: test structure")
        if re.search(r'\b(?:user\s+stor(?:y|ies)|acceptance\s+criteria|story\s+points?|sprint\s+backlog|product\s+backlog)\b', section_text):
            scores["USER_STORY"] += 12
            evidence["USER_STORY"].append("Section heading: agile user story structure")

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_type, best_score = sorted_scores[0]
    runner_up_type, runner_up_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)
    
    # Lower minimum threshold to catch real-world docs without strong headings
    if best_score < 8:
        return "UNKNOWN", 0.0, ["Insufficient classification signals across document"]
    
    raw_confidence = min(round((best_score / 55.0) * 100, 1), 99.0)
    
    # Only mark ambiguous when scores are nearly identical AND both very high
    if best_score > 0 and (best_score - runner_up_score) <= 3 and runner_up_score >= 45 and best_score < 50:
        return "UNKNOWN", 20.0, [f"Ambiguous: {best_type} ({best_score}) vs {runner_up_type} ({runner_up_score})"]
    
    return best_type, raw_confidence, evidence[best_type]
