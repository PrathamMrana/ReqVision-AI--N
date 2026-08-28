import time
import logging
from flask import Blueprint, request, jsonify
from utils.preprocess import clean_text
from utils.cross_doc import analyze_cross_documents
from utils.analyzer import generate_recommendations, generate_engineering_impact
from analytics.modules import get_module_impact
from analytics.risk import calculate_metrics, generate_executive_summary

compare_bp = Blueprint('compare_bp', __name__)

# Configure standard logging for the backend
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReqVision-Analyzer")

@compare_bp.route('/compare', methods=['POST'])
def compare_requirements():
    start_time = time.time()
    
    data = request.get_json()
    if not data or 'baseline' not in data or 'updated' not in data:
        return jsonify({"error": "Missing baseline or updated payload"}), 400
        
    baseline_payload = data['baseline']
    updated_payload = data['updated']
    
    # Accept both strings (legacy) and arrays of objects (new UI)
    if isinstance(baseline_payload, str):
        baseline_payload = [{"name": "Pasted Baseline Text", "text": baseline_payload}]
    if isinstance(updated_payload, str):
        updated_payload = [{"name": "Pasted Updated Text", "text": updated_payload}]
    
    # Execute Cross-Document Analysis
    changes, cross_doc_analysis, baseline_sents, updated_sents = analyze_cross_documents(
        baseline_payload, updated_payload
    )
    
    if not baseline_sents and not updated_sents:
        return jsonify({"error": "Both documents are empty"}), 400

    # Debug Logging
    logger.info("================ BASELINE DOCUMENTS ================")
    for doc in cross_doc_analysis["documents"]:
        if doc["side"] == "baseline":
            logger.info(f" - [{doc['document_type']}] {doc['document_name']}: {doc['requirement_count']} requirements extracted")

    logger.info("================ UPDATED DOCUMENTS ================")
    for doc in cross_doc_analysis["documents"]:
        if doc["side"] == "updated":
            logger.info(f" - [{doc['document_type']}] {doc['document_name']}: {doc['requirement_count']} requirements extracted")
            
    logger.info("================ REQUIREMENT MATCHING RESULTS ================")
    for change in changes:
        logger.info(f"[{change.get('req_id', 'N/A')}] {change.get('source_document', 'Unknown')} -> {change.get('matched_document', 'None')} | Sim: {change.get('similarity', 0):.2f} | Status: {change['status']} ({change.get('relationship', '')})")

    logger.info("================ CROSS-DOCUMENT RELATIONSHIPS ================")
    for rel in cross_doc_analysis["relationships"]:
        if rel["relationship"] in ["AFFECTS", "TRACEABLE_TO"]:
            logger.info(f"[{rel['relationship']}] {rel['source_document']}:{rel['source_requirement_id']} -> {rel['target_document']}:{rel['target_requirement_id']} (Sim: {rel['similarity']:.2f})")
    
    # Functional Module Impact Analytics
    module_impact = get_module_impact(changes)
    
    total_quality = 0
    ambiguous_count = 0
    atomic_count = 0
    poor_quality_count = 0
    
    impacted_modules = set()
    review_areas = set()
    testing_focus = set()
    
    for change in changes:
        module = change.get('module', 'Other')
        status = change['status']
        rec = generate_recommendations(status, module, change.get('new', ''), change.get('old', ''))
        change['recommendations'] = rec
        change['engineering_impact'] = generate_engineering_impact(change)
        
        if rec:
            impacted_modules.add(module)
            review_areas.add(rec['review'])
            for t in rec['tests']:
                testing_focus.add(t)
                
        q = change.get('quality', {})
        score = q.get('score', 0)
        total_quality += score
        if any("-10 Ambiguous word" in d for d in q.get('deductions', [])):
            ambiguous_count += 1
        if any("-10 Multiple requirements" not in d for d in q.get('deductions', [])):
            atomic_count += 1
        if score < 70:
            poor_quality_count += 1

    total_reqs = len(changes)
    quality_summary = {
        "average_score": round(total_quality / total_reqs) if total_reqs > 0 else 0,
        "ambiguous_count": ambiguous_count,
        "atomic_count": atomic_count,
        "poor_quality_count": poor_quality_count,
        "total": total_reqs
    }
    
    impact_analysis = {
        "impacted_modules": list(impacted_modules),
        "review_areas": list(review_areas),
        "testing_focus": list(testing_focus)
    }

    metrics = calculate_metrics(len(baseline_sents), len(updated_sents), changes)
    executive_summary = generate_executive_summary(metrics, module_impact)
    
    from datetime import datetime
    executive_summary["comparison_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    executive_summary["baseline_version"] = "v1.0"
    executive_summary["updated_version"] = "v2.0"
    avg_sim = metrics.get("average_similarity", 0)
    conf = "High" if avg_sim >= 70 else "Medium" if avg_sim >= 40 else "Low"
    executive_summary["analysis_confidence"] = f"{conf} (Lexical Match)"
    executive_summary["ai_confidence"] = f"{conf} (Lexical Match)"
    
    execution_time = time.time() - start_time
    
    # Merge execution statistics with cross document statistics
    stats = {
        "execution_time_ms": round(execution_time * 1000, 2),
        "requirements_processed": len(baseline_sents) + len(updated_sents),
        "similarity_calculations": len(baseline_sents) * len(updated_sents),
        **cross_doc_analysis["statistics"]
    }
    
    response = {
        "metrics": metrics,
        "executive_summary": executive_summary,
        "module_impact": module_impact,
        "quality_summary": quality_summary,
        "impact_analysis": impact_analysis,
        "changes": changes,
        "cross_document_analysis": cross_doc_analysis,
        "statistics": stats
    }
    
    return jsonify(response), 200
