"""
Contract test for POST /llm/process endpoint
Tests the API contract for text processing with LLM profiles
"""
import pytest
import json
from flask import Flask
from unittest.mock import patch

# This test will FAIL initially - that's expected in TDD approach
class TestLLMProcessContract:
    """Contract tests for POST /llm/process endpoint"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask app"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_process_text_success_contract(self, client):
        """Test successful text processing contract"""
        # Arrange
        request_data = {
            "profile_id": "clean_format",
            "text": "hola mundo esto es una prueba",
            "parameters": {}
        }
        
        # Act
        response = client.post('/llm/process', 
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert data['profile_id'] == 'clean_format'
        assert 'result_id' in data
        assert 'output' in data
        assert 'metadata' in data
        assert 'created_at' in data
        
        # Verify metadata structure
        metadata = data['metadata']
        assert 'processing_time' in metadata
        assert 'tokens_used' in metadata
        assert 'model_used' in metadata
    
    def test_process_text_with_parameters_contract(self, client):
        """Test text processing with parameters contract"""
        # Arrange
        request_data = {
            "profile_id": "translate",
            "text": "Hola mundo",
            "parameters": {
                "target_language": "en"
            }
        }
        
        # Act
        response = client.post('/llm/process',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] == True
        assert data['profile_id'] == 'translate'
        assert len(data['output']) > 0
    
    def test_process_text_error_contract(self, client):
        """Test error response contract"""
        # Arrange
        request_data = {
            "profile_id": "invalid_profile",
            "text": "test text",
            "parameters": {}
        }
        
        # Act
        response = client.post('/llm/process',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] == False
        assert 'error' in data
        
        error = data['error']
        assert 'code' in error
        assert 'message' in error
        assert error['code'] == 'INVALID_PROFILE'
    
    def test_process_text_empty_text_error_contract(self, client):
        """Test empty text error contract"""
        # Arrange
        request_data = {
            "profile_id": "clean_format",
            "text": "",
            "parameters": {}
        }
        
        # Act
        response = client.post('/llm/process',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] == False
        assert data['error']['code'] == 'INVALID_TEXT'
    
    def test_process_text_timeout_error_contract(self, client):
        """Test timeout error contract"""
        # Arrange
        request_data = {
            "profile_id": "summarize",
            "text": "a" * 100000,  # Very long text
            "parameters": {}
        }
        
        # Act - Mock timeout scenario
        with patch('src.services.llm_service.LLMService.process_text') as mock_process:
            mock_process.side_effect = TimeoutError("Processing timeout")
            
            response = client.post('/llm/process',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 408
        
        data = response.get_json()
        assert data['success'] == False
        assert data['error']['code'] == 'TIMEOUT_ERROR'
        assert 'timeout_seconds' in data['error']['details']
    
    def test_process_text_request_validation_contract(self, client):
        """Test request validation contract"""
        # Test missing profile_id
        request_data = {
            "text": "test text",
            "parameters": {}
        }
        
        response = client.post('/llm/process',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Test missing text
        request_data = {
            "profile_id": "clean_format",
            "parameters": {}
        }
        
        response = client.post('/llm/process',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error']['code'] == 'VALIDATION_ERROR'
