import re

AMBIGUOUS_WORDS = ['robust', 'user-friendly', 'fast', 'quick', 'easy', 'seamless', 'efficient', 'state-of-the-art', 'modern', 'scalable', 'reliable', 'high-performance']
CONDITIONALS = ['if', 'when', 'unless', 'provided that', 'in case of', 'should', 'depending on']
PRIORITY_HIGH = ['must', 'shall', 'critical', 'urgent', 'immediately', 'required']
PRIORITY_LOW = ['may', 'optional', 'nice to have', 'could', 'desired']

def analyze_quality(req_text):
    if not req_text:
        return {"score": 0, "deductions": [], "strengths": [], "weaknesses": [], "suggestions": [], "ambiguous_words": []}

    score = 100
    found_ambiguous = [w for w in AMBIGUOUS_WORDS if w in req_text.lower()]
    if found_ambiguous:
        score -= min(30, len(found_ambiguous) * 10)

    # Simplified for the demo, just return the score
    return {"score": max(0, score), "deductions": [], "strengths": [], "weaknesses": [], "suggestions": [], "ambiguous_words": found_ambiguous}

def detect_priority(req_text):
    if not req_text:
        return "Medium"
    text_lower = req_text.lower()
    if any(w in text_lower for w in PRIORITY_HIGH):
        return "High"
    if any(w in text_lower for w in PRIORITY_LOW):
        return "Low"
    return "Medium"

def calculate_complexity(old_text, new_text, status):
    # Determine the actual text that represents the "work"
    target_text = new_text if status != "Removed" else old_text
    if not target_text:
        return "Low"
        
    text_lower = target_text.lower()
    score = 0
    
    # 1. Base complexity from size/structure
    words = len(text_lower.split())
    if words > 20: score += 1
    if any(c in text_lower for c in CONDITIONALS): score += 2
    
    # 2. Architectural/Engineering complexity
    if re.search(r'\b(aws|microservices|cluster|scaling|concurrent|throughput|latency)\b', text_lower):
        score += 3
    if re.search(r'\b(ios|android|mobile|native)\b', text_lower):
        score += 3
    if re.search(r'\b(oauth|jwt|sso|security|encryption|bcrypt)\b', text_lower):
        score += 2
    if re.search(r'\b(database|migration|schema|redis)\b', text_lower):
        score += 2
        
    # 3. Change Delta complexity
    if status == 'Modified' and old_text:
        # Check numerical target changes
        old_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', old_text))
        new_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', new_text))
        if old_nums != new_nums:
            score += 2 # Changing a number is often a major constraint shift
            
        # Hard capability added/removed
        old_words = set(re.findall(r'\b\w+\b', old_text.lower()))
        new_words = set(re.findall(r'\b\w+\b', new_text.lower()))
        added = new_words - old_words
        if len(added) > 5:
            score += 1
            
    if score >= 6:
        return "Very High"
    elif score >= 4:
        return "High"
    elif score >= 2:
        return "Medium"
    else:
        return "Low"

def generate_recommendations(status, module, new_text, old_text):
    if status in ["Unchanged", "N/A"]:
        return None
        
    text_lower = new_text.lower() if status != 'Removed' else old_text.lower()
    
    # Dynamic rules based on text explicitly
    rec = {}
    if re.search(r'\b(email|push|sms|notification)\b', text_lower):
        rec = {
            "review": "Review Notification Service, Email/Push provider limits, and template integrations.",
            "components": ["Notification Service", "Email/Push Integration"],
            "tests": ["Delivery Failure Handling", "Notification Integration Tests"]
        }
    elif re.search(r'\b(concurrent|throughput|latency|performance|scale)\b', text_lower):
        rec = {
            "review": "Requires capacity planning, infrastructure scaling, and bottleneck analysis.",
            "components": ["Load Balancer", "Caching Layer", "Database Performance"],
            "tests": ["Load Testing", "Stress Testing", "Infrastructure Capacity Checks"]
        }
    elif re.search(r'\b(ios|android|mobile|app)\b', text_lower):
        rec = {
            "review": "Ensure API contracts are frozen for mobile backward compatibility.",
            "components": ["Mobile UI (iOS/Android)", "API Gateway"],
            "tests": ["Mobile E2E Tests", "Cross-Platform UI Tests"]
        }
    elif re.search(r'\b(jwt|oauth|sso|login|auth)\b', text_lower):
        rec = {
            "review": "Audit authentication middleware, token validation, and session handling.",
            "components": ["Auth Middleware", "Session Handling", "Identity Provider"],
            "tests": ["Security Tests", "Token Expiry Tests", "Penetration Tests"]
        }
    elif re.search(r'\b(database|schema|migrate)\b', text_lower):
        rec = {
            "review": "Review database migration scripts, indexing, and schema changes.",
            "components": ["Database Layer", "ORM Models"],
            "tests": ["Data Migration Tests", "Query Performance Tests"]
        }
    elif module == "API":
        rec = {
            "review": "Update API documentation and notify consumers of potential payload changes.",
            "components": ["API Gateway", "Route Controllers"],
            "tests": ["API Contract Tests", "Endpoint E2E Tests"]
        }
    else:
        rec = {
            "review": "Review affected feature implementation and component integrations.",
            "components": [f"{module} Module" if module != "Unknown" else "Affected Components"],
            "tests": ["Unit Tests", "Regression Test Suite"]
        }
        
    return rec

def generate_engineering_impact(change):
    status = change.get('status')
    if status in ['Unchanged', 'N/A']:
        return None
        
    module = change.get('module', 'Other')
    complexity = change.get('complexity', 'Low')
    new_text = change.get('new', '').lower()
    old_text = change.get('old', '').lower()
    target_text = new_text if status != 'Removed' else old_text
    
    # Story Points based directly on calculated complexity
    points_map = {
        "Very High": 13,
        "High": 8,
        "Medium": 5,
        "Low": 3
    }
    
    points = points_map.get(complexity, 3)
    
    # Minor text tweaks should drop to 1 or 2
    if status == 'Modified':
        old_words = set(re.findall(r'\b\w+\b', old_text))
        new_words = set(re.findall(r'\b\w+\b', new_text))
        diff = len(old_words ^ new_words)
        if diff <= 3 and complexity in ['Low', 'Medium']:
            points = 1 if diff <= 1 else 2
            
    # Estimate Sprint Effort
    effort_map = {
        1: "< 1 day",
        2: "1–2 days",
        3: "2–3 days",
        5: "3–5 days (1 Sprint)",
        8: "1–2 Sprints",
        13: "2+ Sprints (Major Epic)"
    }
    sprint_effort = effort_map.get(points, "3–5 days")
    
    # Backward Compatibility
    breaking_keywords = ['remove', 'delete', 'replace', 'migrate', 'schema', 'breaking', 'deprecated', 'drop', 'alter', 'rename']
    is_breaking = any(kw in target_text for kw in breaking_keywords) or status == 'Removed'
    
    # If performance constraints INCREASED significantly (e.g. 500 -> 2000), it's architecturally breaking or at least high impact, but API compatible usually.
    # We will let explicitly breaking keywords define it, or if a capability is removed.
    backward_compatible = not is_breaking
    
    # Dynamic Keyword-Driven Architecture Impact Stars
    stars = {
        "Frontend": 1,
        "Backend": 1,
        "Database": 1,
        "API": 1,
        "Testing": 1
    }
    
    if re.search(r'\b(oauth|sso|jwt|token|auth|login|security)\b', target_text):
        stars.update({"Backend": 5, "API": 5, "Testing": 4, "Frontend": 2})
    if re.search(r'\b(payment|stripe|checkout|billing|invoice|transaction)\b', target_text):
        stars.update({"Backend": 5, "API": 5, "Testing": 5, "Database": 4, "Frontend": 3})
    if re.search(r'\b(database|schema|table|sql|migration|index|query)\b', target_text):
        stars.update({"Database": 5, "Backend": 4, "API": 2, "Testing": 3})
    if re.search(r'\b(ui|button|screen|view|layout|dashboard|theme|mobile|ios|android)\b', target_text):
        stars.update({"Frontend": 5, "Backend": 2, "API": 3, "Testing": 3})
    if re.search(r'\b(concurrent|throughput|latency|uptime|scale)\b', target_text):
        stars.update({"Backend": 5, "Database": 4, "Testing": 5, "Frontend": 1, "API": 1})
    if re.search(r'\b(email|push|sms|notification)\b', target_text):
        stars.update({"Backend": 4, "API": 3, "Testing": 4, "Frontend": 2})
        
    if is_breaking:
        stars['Testing'] = 5
        
    # Richer Dependency Chain Story
    if re.search(r"\b(aws|microservices|container|docker|scale|scaling|horizontal)\b", target_text):
        chain = ["API Gateway", "Containerized Services", "Load Balancer", "Auto Scaling", "Integration/Load Tests"]
    elif re.search(r"\b(ios|android|mobile|native)\b", target_text):
        chain = ["Mobile UI (iOS/Android)", "API Gateway", "Auth Middleware", "Mobile E2E Tests"]
    elif re.search(r"\b(performance|concurrent|latency|throughput|cache|redis|uptime)\b", target_text):
        chain = ["Load Balancer", "Caching Layer", "Read Replicas", "Performance/Load Tests"]
    elif re.search(r"\b(email|push|sms|notification)\b", target_text):
        chain = ["Notification Service", "Email/Push Provider", "Delivery Failure Handlers", "Delivery Tests"]
    elif re.search(r"\b(jwt|token|oauth|sso|login)\b", target_text) or module in ["Authentication", "Security"]:
        chain = ["Auth Module", "JWT/OAuth Gateway", "Auth Middleware", "User Identity DB", "Security Tests"]
    elif re.search(r"\b(payment|stripe|checkout|billing|invoice|transaction)\b", target_text):
        chain = ["Payment Module", "Transaction Service", "Billing Database", "Integration Tests"]
    elif re.search(r'\b(database|schema|table|sql|migration)\b', target_text) or module == 'Database':
        chain = ["Data Access Layer", "ORM Models", "Core Database", "Data Migration Tests"]
    elif re.search(r'\b(search|filter|sort|catalog)\b', target_text):
        chain = ["Search API", "Catalog Service", "Read Replica DB", "Load Tests"]
    else:
        rec = generate_recommendations(status, module, new_text, old_text)
        components = rec.get('components', ['Core Layer']) if rec else ['Core Layer']
        tests = rec.get('tests', ['Regression Tests']) if rec else ['Regression Tests']
        chain = list(components) + list(tests)
    
    return {
        "story_points": points,
        "sprint_effort": sprint_effort,
        "backward_compatible": backward_compatible,
        "stars": stars,
        "dependency_chain": chain,
        "is_breaking": is_breaking
    }
