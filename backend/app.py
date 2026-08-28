import os
import nltk
from flask import Flask
from flask_cors import CORS
from api.routes.compare import compare_bp
from api.routes.project import project_bp
from api.routes.extract import extract_bp

def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')

def create_app():
    download_nltk_data()
    app = Flask(__name__)
    CORS(app)
    
    app.register_blueprint(compare_bp, url_prefix='/api')
    app.register_blueprint(project_bp, url_prefix='/api/project')
    app.register_blueprint(extract_bp, url_prefix='/api')
    
    return app

app = create_app()

if __name__ == '__main__':
    # Bind to 0.0.0.0 to support both localhost (IPv6/IPv4) and 127.0.0.1
    app.run(host='0.0.0.0', debug=True, port=5001)
