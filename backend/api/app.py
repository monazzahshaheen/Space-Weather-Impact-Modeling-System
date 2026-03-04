"""
Space Weather Impact Modeling System - Backend API
Main Flask application with CORS support
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging

# Import route blueprints
from routes.satellites import satellites_bp
from routes.space_weather import space_weather_bp
from routes.predictions import predictions_bp
from routes.reports import reports_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Register blueprints
app.register_blueprint(satellites_bp, url_prefix='/api/satellites')
app.register_blueprint(space_weather_bp, url_prefix='/api/space-weather')
app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

# Root endpoint
@app.route('/')
def home():
    return jsonify({
        'name': 'Space Weather Impact Modeling API',
        'version': '1.0.0',
        'status': 'active',
        'endpoints': {
            'satellites': '/api/satellites',
            'space_weather': '/api/space-weather',
            'predictions': '/api/predictions',
            'reports': '/api/reports'
        }
    })

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': 'operational'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400

# Run the application
if __name__ == '__main__':
    logger.info("Starting Space Weather Impact Modeling API...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )