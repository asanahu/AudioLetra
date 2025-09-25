"""
Contract test for GET /llm/results/{id} endpoint
Tests the API contract for retrieving specific processing results
"""
import pytest
import json
from flask import Flask
from unittest.mock import patch

# This test will FAIL initially - that's expected in TDD approach
class TestLLMResultsContract:
    """Contract tests for GET /llm/results/{id} endpoint"""
    
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
    
    @pytest.fixture
    def sample_result_id(self):
        """Sample result ID for testing"""
        return "550e8400-e29b-41d4-a716-446655440000"
    
    def test_get_result_success_contract(self, client, sample_result_id):
        """Test successful result retrieval contract"""
        # Act
        response = client.get(f'/llm/results/{sample_result_id}')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'result_id' in data
        assert 'profile_id' in data
        assert 'output' in data
        assert 'metadata' in data
        assert 'created_at' in data
        
        # Verify specific values
        assert data['result_id'] == sample_result_id
        assert data['profile_id'] == 'clean_format'
        assert len(data['output']) > 0
        
        # Verify metadata structure
        metadata = data['metadata']
        assert 'processing_time' in metadata
        assert isinstance(metadata['processing_time'], (int, float))
        assert metadata['processing_time'] > 0
    
    def test_get_result_structure_contract(self, client, sample_result_id):
        """Test result structure contract"""
        # Act
        response = client.get(f'/llm/results/{sample_result_id}')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        data = response.get_json()
        
        # Verify all required fields are present
        required_fields = ['result_id', 'profile_id', 'output', 'metadata', 'created_at']
        for field in required_fields:
            assert field in data
        
        # Verify field types
        assert isinstance(data['result_id'], str)
        assert isinstance(data['profile_id'], str)
        assert isinstance(data['output'], str)
        assert isinstance(data['metadata'], dict)
        assert isinstance(data['created_at'], str)
        
        # Verify metadata contains expected fields
        metadata = data['metadata']
        assert 'processing_time' in metadata
        assert isinstance(metadata['processing_time'], (int, float))
    
    def test_get_result_not_found_contract(self, client):
        """Test result not found error contract"""
        # Arrange
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        
        # Act
        response = client.get(f'/llm/results/{non_existent_id}')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        
        error = data['error']
        assert 'code' in error
        assert 'message' in error
        assert error['code'] == 'RESULT_NOT_FOUND'
    
    def test_get_result_invalid_id_format_contract(self, client):
        """Test invalid ID format error contract"""
        # Arrange
        invalid_id = "invalid-uuid-format"
        
        # Act
        response = client.get(f'/llm/results/{invalid_id}')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_ID_FORMAT'
    
    def test_get_result_response_format_contract(self, client, sample_result_id):
        """Test response format contract"""
        # Act
        response = client.get(f'/llm/results/{sample_result_id}')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # Verify response is valid JSON
        assert isinstance(data, dict)
        
        # Verify timestamp format (ISO format)
        created_at = data['created_at']
        assert isinstance(created_at, str)
        # Should be ISO format: 2025-01-17T10:30:00Z
        assert 'T' in created_at
        assert created_at.endswith('Z') or '+' in created_at
    
    def test_get_result_different_profiles_contract(self, client):
        """Test retrieving results from different profiles"""
        # Test results from different profiles
        test_cases = [
            ("result-summarize-id", "summarize"),
            ("result-translate-id", "translate"),
            ("result-email-id", "format_email")
        ]
        
        for result_id, expected_profile in test_cases:
            # Act
            response = client.get(f'/llm/results/{result_id}')
            
            # Assert - This will FAIL until implementation
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['profile_id'] == expected_profile
            assert data['result_id'] == result_id
            assert len(data['output']) > 0
    
    def test_get_result_metadata_completeness_contract(self, client, sample_result_id):
        """Test metadata completeness contract"""
        # Act
        response = client.get(f'/llm/results/{sample_result_id}')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        data = response.get_json()
        metadata = data['metadata']
        
        # Verify metadata contains processing information
        assert 'processing_time' in metadata
        assert isinstance(metadata['processing_time'], (int, float))
        assert metadata['processing_time'] > 0
        
        # Additional metadata fields that might be present
        optional_fields = ['tokens_used', 'model_used', 'profile_version']
        for field in optional_fields:
            if field in metadata:
                assert metadata[field] is not None
