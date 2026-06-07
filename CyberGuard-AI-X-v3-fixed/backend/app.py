"""
CyberGuard AI X - Flask Backend
Main application entry point
"""

import os
import sys

# Add ml directory to path for model imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ml'))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

# Import routes
from routes.auth_routes import auth_bp
from routes.complaint_routes import complaint_bp
from routes.analytics_routes import analytics_bp
from routes.ai_routes import ai_bp
from routes.report_routes import report_bp
from database.db import init_db


def create_app():
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cyberguard-ai-x-super-secret-2024')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-cyberguard-secret-key-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours

    # MySQL Config
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_PORT'] = int(os.getenv('DB_PORT', 3307))
    app.config['DB_USER'] = os.getenv('DB_USER', 'root')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'cyberguard_ai')

    # CORS — allow all origins for API and handle preflight
    CORS(app, resources={r"/api/*": {"origins": "*"}},
         supports_credentials=False,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # JWT
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({'error': 'Authorization token required', 'code': 401}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired', 'code': 401}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token', 'code': 401}), 401

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(complaint_bp, url_prefix='/api/complaints')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(report_bp, url_prefix='/api/reports')

    # Health check
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'ok',
            'service': 'CyberGuard AI X',
            'version': '1.0.0'
        })

    # Serve frontend
    from flask import render_template, send_from_directory

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/explore')
    def explore():
        return render_template('explore.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/complaints')
    def complaints():
        return render_template('complaints.html')

    @app.route('/analytics')
    def analytics():
        return render_template('analytics.html')

    @app.route('/admin')
    def admin():
        return render_template('admin.html')

    return app


if __name__ == '__main__':
    app = create_app()
    print("Starting CyberGuard AI X Backend...")
    print("Dashboard: http://localhost:5000")
    print("API: http://localhost:5000/api/")
    app.run(debug=True, host='0.0.0.0', port=5000)
