"""
Unit tests for validation utilities
Tests RequestValidator, ErrorHandler, and validation functions
"""
import pytest
from unittest.mock import Mock
from src.utils.validation import (
    ValidationError, ErrorHandler, RequestValidator,
    require_profile_id, require_result_id, require_text
)


class TestValidationError:
    """Test ValidationError exception"""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation"""
        error = ValidationError("Test error message")
        
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_validation_error_with_code(self):
        """Test ValidationError with error code"""
        error = ValidationError("Test error", code="TEST_ERROR")
        
        assert str(error) == "Test error"
        assert hasattr(error, 'code')
        assert error.code == "TEST_ERROR"


class TestRequestValidator:
    """Test RequestValidator"""
    
    def test_request_validator_initialization(self):
        """Test RequestValidator initialization"""
        validator = RequestValidator()
        assert validator is not None
    
    def test_validate_profile_id_valid(self):
        """Test validating valid profile ID"""
        validator = RequestValidator()
        
        result = validator.validate_profile_id("clean_format")
        assert result == True
    
    def test_validate_profile_id_invalid(self):
        """Test validating invalid profile ID"""
        validator = RequestValidator()
        
        result = validator.validate_profile_id("invalid_profile")
        assert result == False
        
        result = validator.validate_profile_id("")
        assert result == False
        
        result = validator.validate_profile_id(None)
        assert result == False
    
    def test_validate_text_valid(self):
        """Test validating valid text"""
        validator = RequestValidator()
        
        result = validator.validate_text("This is valid text")
        assert result == True
        
        result = validator.validate_text("Short")
        assert result == True
    
    def test_validate_text_invalid(self):
        """Test validating invalid text"""
        validator = RequestValidator()
        
        result = validator.validate_text("")
        assert result == False
        
        result = validator.validate_text(None)
        assert result == False
        
        result = validator.validate_text("   ")  # Only whitespace
        assert result == False
    
    def test_validate_result_id_valid(self):
        """Test validating valid result ID"""
        validator = RequestValidator()
        
        result = validator.validate_result_id("result_123")
        assert result == True
        
        result = validator.validate_result_id("test-result-456")
        assert result == True
    
    def test_validate_result_id_invalid(self):
        """Test validating invalid result ID"""
        validator = RequestValidator()
        
        result = validator.validate_result_id("")
        assert result == False
        
        result = validator.validate_result_id(None)
        assert result == False
    
    def test_validate_parameters_valid(self):
        """Test validating valid parameters"""
        validator = RequestValidator()
        
        result = validator.validate_parameters({"target_language": "English"})
        assert result == True
        
        result = validator.validate_parameters({})
        assert result == True
        
        result = validator.validate_parameters(None)
        assert result == True
    
    def test_validate_parameters_invalid(self):
        """Test validating invalid parameters"""
        validator = RequestValidator()
        
        # Parameters should be dict or None
        result = validator.validate_parameters("invalid")
        assert result == False
        
        result = validator.validate_parameters(123)
        assert result == False
    
    def test_validate_request_data_complete(self):
        """Test validating complete request data"""
        validator = RequestValidator()
        
        data = {
            "profile_id": "clean_format",
            "text": "Test text",
            "parameters": {"param": "value"}
        }
        
        result = validator.validate_request_data(data)
        assert result == True
    
    def test_validate_request_data_missing_fields(self):
        """Test validating request data with missing fields"""
        validator = RequestValidator()
        
        # Missing profile_id
        data = {"text": "Test text"}
        result = validator.validate_request_data(data)
        assert result == False
        
        # Missing text
        data = {"profile_id": "clean_format"}
        result = validator.validate_request_data(data)
        assert result == False
    
    def test_validate_request_data_invalid_fields(self):
        """Test validating request data with invalid fields"""
        validator = RequestValidator()
        
        # Invalid profile_id
        data = {
            "profile_id": "invalid_profile",
            "text": "Test text"
        }
        result = validator.validate_request_data(data)
        assert result == False
        
        # Invalid text
        data = {
            "profile_id": "clean_format",
            "text": ""
        }
        result = validator.validate_request_data(data)
        assert result == False


class TestErrorHandler:
    """Test ErrorHandler"""
    
    def test_error_handler_initialization(self):
        """Test ErrorHandler initialization"""
        handler = ErrorHandler()
        assert handler is not None
    
    def test_create_error_response_basic(self):
        """Test creating basic error response"""
        response = ErrorHandler.create_error_response(
            code="TEST_ERROR",
            message="Test error message"
        )
        
        assert response[1] == 400  # status_code
        assert "error" in response[0]
        assert response[0]["error"]["code"] == "TEST_ERROR"
        assert response[0]["error"]["message"] == "Test error message"
    
    def test_create_error_response_with_details(self):
        """Test creating error response with details"""
        response = ErrorHandler.create_error_response(
            code="TEST_ERROR",
            message="Test error message",
            details={"field": "value"},
            status_code=422
        )
        
        assert response[1] == 422
        assert response[0]["error"]["details"] == {"field": "value"}
    
    def test_handle_validation_error(self):
        """Test handling validation error"""
        error = ValidationError("Validation failed", code="VALIDATION_ERROR")
        
        response = ErrorHandler.handle_validation_error(error)
        
        assert response[1] == 400
        assert response[0]["error"]["code"] == "VALIDATION_ERROR"
        assert response[0]["error"]["message"] == "Validation failed"
    
    def test_handle_profile_error(self):
        """Test handling profile error"""
        response = ErrorHandler.handle_profile_error("invalid_profile")
        
        assert response[1] == 400
        assert response[0]["error"]["code"] == "INVALID_PROFILE"
        assert "invalid_profile" in response[0]["error"]["message"]
    
    def test_handle_text_error(self):
        """Test handling text error"""
        response = ErrorHandler.handle_text_error()
        
        assert response[1] == 400
        assert response[0]["error"]["code"] == "INVALID_TEXT"
        assert "text is required" in response[0]["error"]["message"]
    
    def test_handle_llm_error(self):
        """Test handling LLM error"""
        response = ErrorHandler.handle_llm_error("API Error", "openai")
        
        assert response[1] == 500
        assert response[0]["error"]["code"] == "LLM_ERROR"
        assert "API Error" in response[0]["error"]["message"]
        assert "openai" in response[0]["error"]["message"]
    
    def test_handle_timeout_error(self):
        """Test handling timeout error"""
        response = ErrorHandler.handle_timeout_error(30, "clean_format")
        
        assert response[1] == 408
        assert response[0]["error"]["code"] == "TIMEOUT_ERROR"
        assert "30" in response[0]["error"]["message"]
        assert "clean_format" in response[0]["error"]["message"]
    
    def test_handle_prompt_error(self):
        """Test handling prompt error"""
        response = ErrorHandler.handle_prompt_error("Template error")
        
        assert response[1] == 500
        assert response[0]["error"]["code"] == "PROMPT_ERROR"
        assert "Template error" in response[0]["error"]["message"]
    
    def test_handle_file_error(self):
        """Test handling file error"""
        response = ErrorHandler.handle_file_error("File generation failed")
        
        assert response[1] == 500
        assert response[0]["error"]["code"] == "FILE_ERROR"
        assert "File generation failed" in response[0]["error"]["message"]
    
    def test_handle_result_error(self):
        """Test handling result error"""
        response = ErrorHandler.handle_result_error("result_123")
        
        assert response[1] == 404
        assert response[0]["error"]["code"] == "RESULT_NOT_FOUND"
        assert "result_123" in response[0]["error"]["message"]


class TestValidationFunctions:
    """Test validation functions"""
    
    def test_require_profile_id_valid(self):
        """Test require_profile_id with valid profile"""
        result = require_profile_id("clean_format")
        assert result == True
    
    def test_require_profile_id_invalid(self):
        """Test require_profile_id with invalid profile"""
        result = require_profile_id("invalid_profile")
        assert result == False
    
    def test_require_profile_id_none(self):
        """Test require_profile_id with None"""
        result = require_profile_id(None)
        assert result == False
    
    def test_require_result_id_valid(self):
        """Test require_result_id with valid result ID"""
        result = require_result_id("result_123")
        assert result == True
    
    def test_require_result_id_invalid(self):
        """Test require_result_id with invalid result ID"""
        result = require_result_id("")
        assert result == False
    
    def test_require_result_id_none(self):
        """Test require_result_id with None"""
        result = require_result_id(None)
        assert result == False
    
    def test_require_text_valid(self):
        """Test require_text with valid text"""
        result = require_text("This is valid text")
        assert result == True
    
    def test_require_text_invalid(self):
        """Test require_text with invalid text"""
        result = require_text("")
        assert result == False
        
        result = require_text("   ")
        assert result == False
    
    def test_require_text_none(self):
        """Test require_text with None"""
        result = require_text(None)
        assert result == False


# Integration tests for validation
class TestValidationIntegration:
    """Test validation working together"""
    
    def test_validator_error_handler_integration(self):
        """Test RequestValidator and ErrorHandler integration"""
        validator = RequestValidator()
        
        # Test invalid data
        data = {"profile_id": "invalid", "text": ""}
        
        if not validator.validate_request_data(data):
            response = ErrorHandler.handle_validation_error(
                ValidationError("Invalid request data")
            )
            
            assert response[1] == 400
            assert "error" in response[0]
    
    def test_validation_functions_integration(self):
        """Test validation functions working together"""
        # Test complete validation flow
        profile_valid = require_profile_id("clean_format")
        text_valid = require_text("Valid text")
        result_valid = require_result_id("result_123")
        
        assert profile_valid == True
        assert text_valid == True
        assert result_valid == True
        
        # Test with invalid data
        profile_invalid = require_profile_id("invalid")
        text_invalid = require_text("")
        result_invalid = require_result_id("")
        
        assert profile_invalid == False
        assert text_invalid == False
        assert result_invalid == False
    
    def test_error_response_consistency(self):
        """Test error response format consistency"""
        # Test different error types have consistent format
        errors = [
            ErrorHandler.handle_profile_error("invalid"),
            ErrorHandler.handle_text_error(),
            ErrorHandler.handle_llm_error("test", "openai"),
            ErrorHandler.handle_timeout_error(30, "test"),
            ErrorHandler.handle_prompt_error("test"),
            ErrorHandler.handle_file_error("test"),
            ErrorHandler.handle_result_error("test")
        ]
        
        for response in errors:
            assert len(response) == 2  # (data, status_code)
            assert "error" in response[0]
            assert "code" in response[0]["error"]
            assert "message" in response[0]["error"]
            assert isinstance(response[1], int)
    
    def test_validation_edge_cases(self):
        """Test validation edge cases"""
        validator = RequestValidator()
        
        # Test with very long text
        long_text = "a" * 10000
        result = validator.validate_text(long_text)
        assert result == True
        
        # Test with special characters
        special_text = "Text with special chars: !@#$%^&*()"
        result = validator.validate_text(special_text)
        assert result == True
        
        # Test with unicode characters
        unicode_text = "Text with unicode: ñáéíóú"
        result = validator.validate_text(unicode_text)
        assert result == True
        
        # Test with numbers
        numeric_text = "123456789"
        result = validator.validate_text(numeric_text)
        assert result == True
