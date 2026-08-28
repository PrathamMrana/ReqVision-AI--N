from flask import Blueprint, request, jsonify
from .project import extract_text_from_file

extract_bp = Blueprint('extract_bp', __name__)

@extract_bp.route('/extract-text', methods=['POST'])
def extract_text():
    """
    Utility endpoint to extract raw text from PDF/DOCX for the UI textareas.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file provided"}), 400
        
    try:
        text = extract_text_from_file(file)
        return jsonify({"success": True, "text": text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
