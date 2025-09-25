"""
AudioLetra Backend Application
Main Flask application for LLM Profile Processing
"""
from flask import Flask
from flask_cors import CORS
from src.config import config

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # Register blueprints
    from src.api.llm_routes import llm_bp
    app.register_blueprint(llm_bp, url_prefix='/llm')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'audiLetra-backend'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
