from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

MODULES = {
    "Authentication": "login sign in sign up register registration password oauth sso authenticate mfa session identity credential user account",
    "Authorization": "role permission access admin privilege rbac authorize restrict rule group grant membership tier access control",
    "Payment": "payment stripe checkout credit card billing invoice refund transaction pay subscription fee cost",
    "Search & Catalog": "search filter find sort lookup catalog category book item product inventory browse",
    "Loan Management": "borrow return loan due fine overdue issue renew checkout period returnable reserve",
    "Dashboard": "dashboard home page overview landing panel home hub central",
    "Reporting": "report export pdf csv summary excel download print analytics chart table",
    "Notifications": "email notification alert sms push message notify inbox broadcast",
    "Database": "database schema table sql nosql query record store save data repository migration backup",
    "API": "api endpoint rest graphql webhook integration payload sync fetch request response json http",
    "Profile": "profile avatar account settings preferences customer client user detail personal info",
    "Analytics": "analytics metric track statistic graph chart monitor performance usage trend dashboard",
    "Security": "security encryption hash ssl tls vulnerability secure protect firewall audit compliance bcrypt salt jwt token auth timeout session inactivity penetration rbac",
    "Scalability & Infrastructure": "aws cloud microservices docker scale horizontal vertical container cluster kubernetes deploy infrastructure load balancer auto instance architecture containerized",
    "Performance": "performance speed latency throughput response time load concurrent scalable fast cache optimize ms seconds capacity",
    "Usability & Platforms": "ios android mobile app native browser ui ux usability interface responsive frontend desktop plugin navigation accessibility design experience screen",
    "Availability & Reliability": "uptime downtime availability redundancy failover maintenance 99 reliable SLA resilient recover backup window scheduled"
}

_module_names = list(MODULES.keys())
_module_docs = list(MODULES.values())
_vectorizer = TfidfVectorizer(stop_words='english')
_module_vectors = _vectorizer.fit_transform(_module_docs)

def detect_functional_area(text):
    if not text or not text.strip():
        return "Other"
        
    text_lower = text.lower()
    
    # 1. Hard Regex Overrides for critical architectural keywords (solves false positives)
    if re.search(r'\b(ios|android|mobile|native app)\b', text_lower): return "Usability & Platforms"
    if re.search(r'\b(concurrent users?|throughput|latency|response time)\b', text_lower): return "Performance"
    if re.search(r'\b(uptime|downtime|99\.\d+%)\b', text_lower): return "Availability & Reliability"
    if re.search(r'\b(aws|microservices|docker|kubernetes|horizontal scaling)\b', text_lower): return "Scalability & Infrastructure"
    if re.search(r'\b(jwt|oauth|sso|bcrypt|encryption|salt)\b', text_lower): return "Security"
    
    try:
        req_vector = _vectorizer.transform([text_lower])
        similarities = cosine_similarity(req_vector, _module_vectors)[0]
        best_idx = similarities.argmax()
        best_score = similarities[best_idx]
        if best_score > 0.15: # Raised threshold to avoid generic keyword matches
            return _module_names[best_idx]
    except Exception:
        pass
    return "Other"

def get_module_impact(changes):
    impact_data = {}
    total_changes = 0
    for change in changes:
        if change['status'] == 'Unchanged':
            continue
        text_to_analyze = change['new'] if change['new'] else change['old']
        module = detect_functional_area(text_to_analyze)
        change['module'] = module
        if module not in impact_data:
            impact_data[module] = {"Changed Requirements": 0, "Impact %": 0, "Risk Level": "Low"}
        impact_data[module]["Changed Requirements"] += 1
        total_changes += 1

    for module in impact_data:
        impact_pct = round((impact_data[module]["Changed Requirements"] / total_changes) * 100) if total_changes > 0 else 0
        impact_data[module]["Impact %"] = impact_pct
        if module in ["Authentication", "Authorization", "Payments", "Security", "Scalability & Infrastructure", "Availability & Reliability"]:
            impact_data[module]["Risk Level"] = "High"
        elif module in ["Database", "API", "Performance"]:
            if impact_data[module]["Changed Requirements"] >= 2:
                impact_data[module]["Risk Level"] = "High"
            else:
                impact_data[module]["Risk Level"] = "Medium"
        else:
            if impact_data[module]["Changed Requirements"] >= 3:
                impact_data[module]["Risk Level"] = "Medium"
            else:
                impact_data[module]["Risk Level"] = "Low"
                
    for change in changes:
        if change['status'] == 'Unchanged':
            change['module'] = detect_functional_area(change['old'])
            
    result = []
    for module, data in impact_data.items():
        result.append({
            "module": module,
            "changed": data["Changed Requirements"],
            "impact_pct": data["Impact %"],
            "risk": data["Risk Level"]
        })
    return sorted(result, key=lambda x: x['changed'], reverse=True)
