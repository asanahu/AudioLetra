"""
Configuration module for AudioLetra Backend
"""
import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # LLM Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.openai.com/v1')
    
    # Processing Configuration
    DEFAULT_TIMEOUT_BASE = 30  # seconds
    TIMEOUT_PER_1000_CHARS = 1  # seconds
    MAX_TEXT_LENGTH = 1000000  # characters
    
    # File Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'temp')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    # Profile Configuration
    SUPPORTED_LANGUAGES = ['es', 'en', 'fr', 'de']
    
    @staticmethod
    def get_timeout(text_length: int) -> int:
        """Calculate timeout based on text length"""
        return Config.DEFAULT_TIMEOUT_BASE + (text_length // 1000) * Config.TIMEOUT_PER_1000_CHARS

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
