import os
import io
import uuid
import time
from flask import Blueprint, request, jsonify
from utils.classifier import classify_document
from utils.extractor import extract_artifacts
from utils.project_traceability import analyze_project_documents_traceability
import PyPDF2
import docx

project_bp = Blueprint('project_bp', __name__)

def extract_text_from_file(file):
    filename = file.filename.lower()
    
    if filename.endswith('.txt'):
        return file.read().decode('utf-8', errors='ignore')
        
    elif filename.endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""
            
    elif filename.endswith('.docx'):
        try:
            doc = docx.Document(io.BytesIO(file.read()))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return ""
    else:
        return ""

@project_bp.route('/detect', methods=['POST'])
def detect_documents():
    """
    Accepts:
    1. multipart/form-data with multiple files (PDF/DOCX/TXT), OR
    2. application/json with {"documents": [{"name": "...", "text": "..."}]}
    
    Detects their types independently from content, and extracts their normalized artifacts.
    """
    start_time = time.time()
    processed_documents = []
    total_artifacts = 0
    
    # Check if JSON payload was sent
    if request.is_json:
        data = request.get_json() or {}
        doc_list = data.get('documents', [])
        
        for idx, doc in enumerate(doc_list):
            filename = doc.get('name') or f"document_{idx+1}.txt"
            content = doc.get('text', '')
            
            if not content.strip():
                continue
                
            doc_id = doc.get('id') or str(uuid.uuid4())
            doc_type, confidence, signals = classify_document(content, filename)
            artifacts = extract_artifacts(doc_id, doc_type, content, filename)
            total_artifacts += len(artifacts)
            
            type_label_map = {
                "BRD": "Business Requirements",
                "SRS": "Software Requirements",
                "FRD": "Functional Specifications",
                "USER_STORY": "User Stories",
                "TEST_CASE": "Test Cases",
                "CHANGE_REQUEST": "Change Requests",
                "MEETING_MINUTES": "Action Items",
                "RELEASE_NOTES": "Release Items"
            }
            label = type_label_map.get(doc_type, "Artifacts")
            
            processed_documents.append({
                "document_id": doc_id,
                "filename": filename,
                "document_type": doc_type,
                "confidence_score": confidence,
                "signals_matched": signals,
                "artifact_count": len(artifacts),
                "artifact_label": f"{len(artifacts)} {label}",
                "artifacts": artifacts,
                "content": content
            })
            
        execution_time = time.time() - start_time
        return jsonify({
            "success": True,
            "documents": processed_documents,
            "summary": {
                "total_documents": len(processed_documents),
                "total_artifacts_extracted": total_artifacts,
                "processing_time_ms": round(execution_time * 1000, 2)
            }
        }), 200

    # Multipart file upload
    if 'files' not in request.files:
        return jsonify({"error": "No files provided", "success": False}), 400
        
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files provided", "success": False}), 400
    
    try:
        for file in files:
            if not file or file.filename == '':
                continue
                
            filename = file.filename
            content = extract_text_from_file(file)
            
            if not content.strip():
                continue
            
            doc_id = str(uuid.uuid4())
            doc_type, confidence, signals = classify_document(content, filename)
            artifacts = extract_artifacts(doc_id, doc_type, content, filename)
            total_artifacts += len(artifacts)
            
            type_label_map = {
                "BRD": "Business Requirements",
                "SRS": "Software Requirements",
                "FRD": "Functional Specifications",
                "USER_STORY": "User Stories",
                "TEST_CASE": "Test Cases",
                "CHANGE_REQUEST": "Change Requests",
                "MEETING_MINUTES": "Action Items",
                "RELEASE_NOTES": "Release Items"
            }
            label = type_label_map.get(doc_type, "Artifacts")
            
            processed_documents.append({
                "document_id": doc_id,
                "filename": filename,
                "document_type": doc_type,
                "confidence_score": confidence,
                "signals_matched": signals,
                "artifact_count": len(artifacts),
                "artifact_label": f"{len(artifacts)} {label}",
                "artifacts": artifacts,
                "content": content
            })
            
        execution_time = time.time() - start_time
            
        return jsonify({
            "success": True,
            "documents": processed_documents,
            "summary": {
                "total_documents": len(processed_documents),
                "total_artifacts_extracted": total_artifacts,
                "processing_time_ms": round(execution_time * 1000, 2)
            }
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to process uploaded documents: {str(e)}", "success": False}), 500


@project_bp.route('/verify', methods=['POST'])
def verify_project_traceability():
    """
    Accepts:
    application/json with:
    {
      "documents": [
         {
           "document_id": "...",
           "filename": "01_BRD_Online_Library.docx",
           "document_type": "BRD",
           "content": "...",
           "artifacts": [ ... ]
         },
         ...
      ]
    }
    
    Executes True Project-Level Cross-Document Traceability across all documents with zero baseline/updated bias.
    """
    try:
        data = request.get_json(silent=True) or {}
        documents = data.get('documents', [])
        
        if not documents:
            return jsonify({"error": "No project documents provided for verification", "success": False}), 400
            
        # Ensure artifacts are extracted for any document that might only have content
        for doc in documents:
            if not doc.get('artifacts'):
                doc_id = doc.get('document_id') or doc.get('id') or str(uuid.uuid4())
                doc_type = doc.get('document_type') or "SRS"
                content = doc.get('content') or doc.get('text') or ""
                doc['artifacts'] = extract_artifacts(doc_id, doc_type, content)
                
        # Run the comprehensive Traceability Engine
        result = analyze_project_documents_traceability(documents)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Traceability analysis error: {str(e)}", "success": False}), 500
