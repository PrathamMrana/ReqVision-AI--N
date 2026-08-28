import os
import io
import uuid
import time
from flask import Blueprint, request, jsonify
from utils.classifier import classify_document
from utils.extractor import extract_artifacts
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
    Accepts multipart/form-data with multiple files (PDF/DOCX/TXT), 
    detects their types independently, and extracts their normalized artifacts.
    """
    start_time = time.time()
    
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400
        
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files provided"}), 400
        
    processed_documents = []
    total_artifacts = 0
    
    for file in files:
        if file.filename == '':
            continue
            
        filename = file.filename
        content = extract_text_from_file(file)
        
        if not content.strip():
            continue # Skip empty or unsupported unparseable files
        
        # 1. Generate unique Document ID
        doc_id = str(uuid.uuid4())
        
        # 2. Independent Classification
        doc_type, confidence, signals = classify_document(content, filename)
        
        # 3. Independent Modular Artifact Extraction
        artifacts = extract_artifacts(doc_id, doc_type, content)
        
        total_artifacts += len(artifacts)
        
        processed_documents.append({
            "document_id": doc_id,
            "filename": filename,
            "document_type": doc_type,
            "confidence_score": confidence,
            "signals_matched": signals,
            "artifact_count": len(artifacts),
            "artifacts": artifacts
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
