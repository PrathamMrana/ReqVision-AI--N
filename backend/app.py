import os
from flask import Flask
from flask_cors import CORS
from api.routes.compare import compare_bp
from api.routes.project import project_bp
from api.routes.extract import extract_bp

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5001", "http://127.0.0.1:5001", "http://localhost:3000"]}}, supports_credentials=True)
    
    app.register_blueprint(compare_bp, url_prefix='/api')
    app.register_blueprint(project_bp, url_prefix='/api/project')
    app.register_blueprint(extract_bp, url_prefix='/api')
    
    return app

app = create_app()

if __name__ == '__main__':
    print("Starting ReqVision AI Backend on 0.0.0.0:5001 ...")
    app.run(host='0.0.0.0', debug=False, port=5001)
