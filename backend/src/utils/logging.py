"""
Request/response logging middleware
Logs API requests and responses for debugging and monitoring
"""
import logging
import time
from flask import request, g
from functools import wraps


def setup_logging():
    """Setup logging configuration"""
    import os
    
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'audiLetra.log')),
            logging.StreamHandler()
        ]
    )
    
    # Create specific loggers
    api_logger = logging.getLogger('audiLetra.api')
    api_logger.setLevel(logging.INFO)
    
    return api_logger


def log_request_response(f):
    """Decorator to log request and response"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger = logging.getLogger('audiLetra.api')
        
        # Log request
        start_time = time.time()
        request_id = f"{int(start_time * 1000)}"
        
        logger.info(f"[{request_id}] REQUEST: {request.method} {request.path}")
        logger.info(f"[{request_id}] Headers: {dict(request.headers)}")
        
        # Log request body (if JSON)
        if request.is_json and request.get_json():
            # Don't log sensitive data
            data = request.get_json()
            sanitized_data = sanitize_log_data(data)
            logger.info(f"[{request_id}] Body: {sanitized_data}")
        
        # Store request ID in g for response logging
        g.request_id = request_id
        g.start_time = start_time
        
        # Execute the function
        try:
            response = f(*args, **kwargs)
            
            # Log response
            duration = time.time() - start_time
            logger.info(f"[{request_id}] RESPONSE: {response[1] if isinstance(response, tuple) else 200}")
            logger.info(f"[{request_id}] Duration: {duration:.3f}s")
            
            return response
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(f"[{request_id}] ERROR: {str(e)}")
            logger.error(f"[{request_id}] Duration: {duration:.3f}s")
            raise
    
    return decorated_function


def sanitize_log_data(data):
    """Remove sensitive data from logs"""
    if not isinstance(data, dict):
        return data
    
    sanitized = data.copy()
    
    # Remove sensitive fields
    sensitive_fields = ['api_key', 'password', 'token', 'secret']
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '***REDACTED***'
    
    # Sanitize nested objects
    for key, value in sanitized.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_log_data(item) if isinstance(item, dict) else item for item in value]
    
    return sanitized


def log_llm_request(profile_id, text_length, timeout):
    """Log LLM processing request"""
    logger = logging.getLogger('audiLetra.llm')
    logger.info(f"LLM Request: profile={profile_id}, text_length={text_length}, timeout={timeout}s")


def log_llm_response(profile_id, success, processing_time, tokens_used=None):
    """Log LLM processing response"""
    logger = logging.getLogger('audiLetra.llm')
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"LLM Response: profile={profile_id}, status={status}, time={processing_time:.3f}s")
    if tokens_used:
        logger.info(f"LLM Tokens: {tokens_used}")


def log_file_generation(format_type, filename, success, error=None):
    """Log file generation"""
    logger = logging.getLogger('audiLetra.files')
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"File Generation: format={format_type}, filename={filename}, status={status}")
    if error:
        logger.error(f"File Generation Error: {error}")


def log_profile_usage(profile_id, text_length):
    """Log profile usage statistics"""
    logger = logging.getLogger('audiLetra.stats')
    logger.info(f"Profile Usage: {profile_id}, text_length={text_length}")


# Global logger instance
api_logger = setup_logging()
