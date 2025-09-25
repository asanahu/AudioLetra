"""
Input validation and error handling utilities
Provides validation functions and standardized error responses
"""
from typing import Dict, Any, Optional, Tuple, List
from flask import jsonify
import uuid
import re


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_profile_id(profile_id: Any) -> Tuple[bool, Optional[str]]:
        """Validate profile ID"""
        if not profile_id:
            return False, "Profile ID is required"
        
        if not isinstance(profile_id, str):
            return False, "Profile ID must be a string"
        
        if len(profile_id.strip()) == 0:
            return False, "Profile ID cannot be empty"
        
        # Check for valid profile ID format (alphanumeric and underscores)
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', profile_id):
            return False, "Profile ID must start with a letter and contain only letters, numbers, and underscores"
        
        return True, None
    
    @staticmethod
    def validate_text(text: Any) -> Tuple[bool, Optional[str]]:
        """Validate input text"""
        if text is None:
            return False, "Text is required"
        
        if not isinstance(text, str):
            return False, "Text must be a string"
        
        if len(text.strip()) == 0:
            return False, "Text cannot be empty"
        
        # Check maximum length (1MB of text)
        if len(text) > 1000000:
            return False, "Text is too long (maximum 1,000,000 characters)"
        
        return True, None
    
    @staticmethod
    def validate_parameters(parameters: Any) -> Tuple[bool, Optional[str]]:
        """Validate parameters object"""
        if parameters is None:
            return True, None  # Parameters are optional
        
        if not isinstance(parameters, dict):
            return False, "Parameters must be a dictionary"
        
        # Validate parameter values
        for key, value in parameters.items():
            if not isinstance(key, str):
                return False, "Parameter keys must be strings"
            
            # Check for reasonable parameter value types
            if not isinstance(value, (str, int, float, bool, list)):
                return False, f"Parameter '{key}' has invalid type"
        
        return True, None
    
    @staticmethod
    def validate_uuid(uuid_str: Any) -> Tuple[bool, Optional[str]]:
        """Validate UUID format"""
        if not uuid_str:
            return False, "ID is required"
        
        if not isinstance(uuid_str, str):
            return False, "ID must be a string"
        
        try:
            uuid.UUID(uuid_str)
            return True, None
        except ValueError:
            return False, "ID must be a valid UUID format"
    
    @staticmethod
    def validate_file_format(format_type: Any) -> Tuple[bool, Optional[str]]:
        """Validate file format"""
        if not format_type:
            return False, "Format is required"
        
        if not isinstance(format_type, str):
            return False, "Format must be a string"
        
        supported_formats = ['txt', 'docx', 'pdf']
        if format_type.lower() not in supported_formats:
            return False, f"Unsupported format. Supported formats: {', '.join(supported_formats)}"
        
        return True, None
    
    @staticmethod
    def validate_filename(filename: Any) -> Tuple[bool, Optional[str]]:
        """Validate filename"""
        if not filename:
            return False, "Filename is required"
        
        if not isinstance(filename, str):
            return False, "Filename must be a string"
        
        filename = filename.strip()
        if len(filename) == 0:
            return False, "Filename cannot be empty"
        
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in filename:
                return False, f"Filename cannot contain '{char}'"
        
        # Check length
        if len(filename) > 100:
            return False, "Filename is too long (maximum 100 characters)"
        
        return True, None
    
    @staticmethod
    def validate_language_code(language: Any, supported_languages: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate language code"""
        if not language:
            return False, "Language is required"
        
        if not isinstance(language, str):
            return False, "Language must be a string"
        
        if language not in supported_languages:
            return False, f"Unsupported language. Supported languages: {', '.join(supported_languages)}"
        
        return True, None
    
    @staticmethod
    def validate_process_request(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate complete process request"""
        # Validate profile_id
        valid, error = InputValidator.validate_profile_id(data.get('profile_id'))
        if not valid:
            return False, error
        
        # Validate text
        valid, error = InputValidator.validate_text(data.get('text'))
        if not valid:
            return False, error
        
        # Validate parameters
        valid, error = InputValidator.validate_parameters(data.get('parameters'))
        if not valid:
            return False, error
        
        return True, None
    
    @staticmethod
    def validate_download_request(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate complete download request"""
        # Validate format
        valid, error = InputValidator.validate_file_format(data.get('format'))
        if not valid:
            return False, error
        
        # Validate filename
        valid, error = InputValidator.validate_filename(data.get('filename'))
        if not valid:
            return False, error
        
        return True, None


class ErrorHandler:
    """Error handling utilities"""
    
    @staticmethod
    def create_error_response(code: str, message: str, details: Optional[Dict[str, Any]] = None, status_code: int = 400):
        """Create standardized error response"""
        error_data = {
            "success": False,
            "error": {
                "code": code,
                "message": message
            }
        }
        
        if details:
            error_data["error"]["details"] = details
        
        return jsonify(error_data), status_code
    
    @staticmethod
    def handle_validation_error(error: ValidationError):
        """Handle validation errors"""
        return ErrorHandler.create_error_response(
            code=error.code,
            message=error.message,
            status_code=400
        )
    
    @staticmethod
    def handle_profile_not_found(profile_id: str):
        """Handle profile not found error"""
        return ErrorHandler.create_error_response(
            code="INVALID_PROFILE",
            message=f"Profile '{profile_id}' not found",
            details={"profile_id": profile_id},
            status_code=400
        )
    
    @staticmethod
    def handle_result_not_found(result_id: str):
        """Handle result not found error"""
        return ErrorHandler.create_error_response(
            code="RESULT_NOT_FOUND",
            message=f"Result '{result_id}' not found",
            details={"result_id": result_id},
            status_code=404
        )
    
    @staticmethod
    def handle_timeout_error(timeout_seconds: int, profile_id: str = None):
        """Handle timeout errors"""
        details = {"timeout_seconds": timeout_seconds}
        if profile_id:
            details["profile_id"] = profile_id
        
        return ErrorHandler.create_error_response(
            code="TIMEOUT_ERROR",
            message=f"Processing exceeded the time limit of {timeout_seconds} seconds",
            details=details,
            status_code=408
        )
    
    @staticmethod
    def handle_llm_error(error_message: str, provider: str = None):
        """Handle LLM service errors"""
        details = {}
        if provider:
            details["provider"] = provider
        
        return ErrorHandler.create_error_response(
            code="LLM_ERROR",
            message=f"LLM processing failed: {error_message}",
            details=details,
            status_code=500
        )
    
    @staticmethod
    def handle_rate_limit_error():
        """Handle rate limit errors"""
        return ErrorHandler.create_error_response(
            code="RATE_LIMIT",
            message="Request rate limit exceeded. Please try again later.",
            status_code=429
        )
    
    @staticmethod
    def handle_invalid_json():
        """Handle invalid JSON errors"""
        return ErrorHandler.create_error_response(
            code="VALIDATION_ERROR",
            message="Invalid JSON in request body",
            status_code=400
        )
    
    @staticmethod
    def handle_missing_content_type():
        """Handle missing content type errors"""
        return ErrorHandler.create_error_response(
            code="VALIDATION_ERROR",
            message="Content-Type must be application/json",
            status_code=400
        )
    
    @staticmethod
    def handle_file_generation_error(format_type: str, error_message: str):
        """Handle file generation errors"""
        return ErrorHandler.create_error_response(
            code="FILE_GENERATION_ERROR",
            message=f"Failed to generate {format_type.upper()} file: {error_message}",
            details={"format": format_type},
            status_code=500
        )
    
    @staticmethod
    def handle_internal_error(error_message: str = None):
        """Handle internal server errors"""
        message = error_message or "An internal server error occurred"
        return ErrorHandler.create_error_response(
            code="INTERNAL_ERROR",
            message=message,
            status_code=500
        )


class RequestValidator:
    """Request-level validation utilities"""
    
    @staticmethod
    def validate_json_request(request):
        """Validate JSON request"""
        if not request.is_json:
            raise ValidationError("Content-Type must be application/json", "VALIDATION_ERROR")
        
        try:
            data = request.get_json()
            if data is None:
                raise ValidationError("Invalid JSON in request body", "VALIDATION_ERROR")
            return data
        except Exception:
            raise ValidationError("Invalid JSON in request body", "VALIDATION_ERROR")
    
    @staticmethod
    def validate_and_get_process_data(request) -> Dict[str, Any]:
        """Validate and extract process request data"""
        data = RequestValidator.validate_json_request(request)
        
        valid, error = InputValidator.validate_process_request(data)
        if not valid:
            raise ValidationError(error, "VALIDATION_ERROR")
        
        return {
            "profile_id": data["profile_id"],
            "text": data["text"],
            "parameters": data.get("parameters", {})
        }
    
    @staticmethod
    def validate_and_get_download_data(request) -> Dict[str, Any]:
        """Validate and extract download request data"""
        data = RequestValidator.validate_json_request(request)
        
        valid, error = InputValidator.validate_download_request(data)
        if not valid:
            raise ValidationError(error, "VALIDATION_ERROR")
        
        return {
            "format": data["format"].lower(),
            "filename": data["filename"]
        }


# Utility functions for common validations
def require_profile_id(profile_id: str) -> str:
    """Require and validate profile ID"""
    valid, error = InputValidator.validate_profile_id(profile_id)
    if not valid:
        raise ValidationError(error, "INVALID_PROFILE")
    return profile_id


def require_result_id(result_id: str) -> str:
    """Require and validate result ID"""
    valid, error = InputValidator.validate_uuid(result_id)
    if not valid:
        raise ValidationError(error, "INVALID_ID_FORMAT")
    return result_id


def require_text(text: str) -> str:
    """Require and validate text"""
    valid, error = InputValidator.validate_text(text)
    if not valid:
        raise ValidationError(error, "INVALID_TEXT")
    return text
