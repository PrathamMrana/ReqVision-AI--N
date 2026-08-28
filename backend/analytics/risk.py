def calculate_metrics(baseline_count, updated_count, changes):
    """
    Calculates advanced resume features like Scope Creep, Volatility, and Stability.
    """
    counts = {
        "Added": 0,
        "Modified": 0,
        "Removed": 0,
        "Unchanged": 0
    }
    
    total_similarity = 0
    sim_count = 0
    
    for c in changes:
        counts[c['status']] += 1
        if c['status'] in ['Unchanged', 'Modified']:
            total_similarity += c['similarity']
            sim_count += 1
            
    avg_similarity = (total_similarity / sim_count) if sim_count > 0 else 0
    
    # Advanced Metrics
    # Requirement Volatility Score: (Modified + Added) / Total Original
    volatility_score = ((counts["Modified"] + counts["Added"]) / baseline_count) if baseline_count > 0 else 0
    
    # Scope Creep Index: Added / Total Original
    scope_creep = (counts["Added"] / baseline_count) if baseline_count > 0 else 0
    
    # Stability Score: Unchanged / Total Original
    stability_score = (counts["Unchanged"] / baseline_count) if baseline_count > 0 else 0
    
    return {
        "counts": counts,
        "total_baseline": baseline_count,
        "total_updated": updated_count,
        "average_similarity": round(avg_similarity * 100, 2),
        "volatility_score": round(volatility_score * 100, 2),
        "scope_creep_index": round(scope_creep * 100, 2),
        "stability_score": round(stability_score * 100, 2)
    }

def generate_executive_summary(metrics, module_impact):
    """
    Generates a professional management report.
    """
    counts = metrics['counts']
    scope_creep = metrics['scope_creep_index']
    volatility = metrics['volatility_score']
    avg_sim = metrics['average_similarity']
    
    # Risk Level determination based on Scope Creep, Volatility, and Similarity
    risk_level = "Low"
    if scope_creep > 25 or volatility > 30 or avg_sim < 70:
        risk_level = "High"
    elif scope_creep > 10 or volatility > 15 or avg_sim < 85:
        risk_level = "Medium"
        
    for m in module_impact:
        if m['risk'] == 'High':
            risk_level = "High"

    # Assessment
    assessment = f"The updated SRS demonstrates a {'significant' if risk_level == 'High' else 'moderate' if risk_level == 'Medium' else 'minor'} shift in requirements. Overall similarity remains at {avg_sim}%, with {metrics['stability_score']}% of original requirements remaining completely unchanged."

    # Business Impact
    impacts = []
    impacts.append(f"Scope increased by {scope_creep}%.")
    if counts["Modified"] > 0:
        impacts.append(f"{counts['Modified']} requirements were modified.")
    if counts["Added"] > 0:
        impacts.append(f"{counts['Added']} requirements were added.")
    if counts["Removed"] > 0:
        impacts.append(f"{counts['Removed']} requirements were removed.")
    
    high_risk_modules = [m['module'] for m in module_impact if m['risk'] == 'High']
    if high_risk_modules:
        impacts.append(f"Highest affected modules: {', '.join(high_risk_modules)}.")

    # Recommendation
    if risk_level == "High":
        rec = "Immediate review required. Review these changes before Sprint Planning to avoid uncontrolled scope expansion and architectural risks."
    elif risk_level == "Medium":
        rec = "Review recommended for newly added and modified components to ensure alignment with project capacity."
    else:
        rec = "Changes are within acceptable variance. Proceed with standard sprint planning."
    # Top Risks
    top_risks = []
    if counts["Removed"] > 0:
        top_risks.append(f"{counts['Removed']} requirement(s) removed from baseline")
    if counts["Added"] > 0:
        top_risks.append(f"{counts['Added']} new capability(s) introduced into scope")
    if scope_creep > 0:
        top_risks.append(f"{scope_creep}% overall scope increase detected")
    if high_risk_modules:
        top_risks.append(f"High architectural risk in: {', '.join(high_risk_modules[:3])}")
    if counts["Modified"] > 3:
        top_risks.append(f"Significant revision volatility ({counts['Modified']} modified requirements)")
    if not top_risks:
        top_risks.append("Minimal scope creep and low architectural risk detected")

    return {
        "overall_risk": risk_level,
        "assessment": assessment,
        "business_impact": impacts,
        "recommendation": rec,
        "top_risks": top_risks
    }
