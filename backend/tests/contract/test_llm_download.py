"""
Contract test for POST /llm/download/{id} endpoint
Tests the API contract for downloading processing results in different formats
"""
import pytest
import json
from flask import Flask
from unittest.mock import patch

# This test will FAIL initially - that's expected in TDD approach
class TestLLMDownloadContract:
    """Contract tests for POST /llm/download/{id} endpoint"""
    
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
    
    def test_download_txt_format_contract(self, client, sample_result_id):
        """Test TXT format download contract"""
        # Arrange
        request_data = {
            "format": "txt",
            "filename": "resultado.txt"
        }
        
        # Act
        response = client.post(f'/llm/download/{sample_result_id}',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        assert response.content_type == 'text/plain'
        
        # Verify file content
        content = response.get_data(as_text=True)
        assert len(content) > 0
        assert isinstance(content, str)
    
    def test_download_docx_format_contract(self, client, sample_result_id):
        """Test DOCX format download contract"""
        # Arrange
        request_data = {
            "format": "docx",
            "filename": "resultado.docx"
        }
        
        # Act
        response = client.post(f'/llm/download/{sample_result_id}',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        assert response.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        # Verify binary content
        content = response.get_data()
        assert len(content) > 0
        assert isinstance(content, bytes)
    
    def test_download_pdf_format_contract(self, client, sample_result_id):
        """Test PDF format download contract"""
        # Arrange
        request_data = {
            "format": "pdf",
            "filename": "resultado.pdf"
        }
        
        # Act
        response = client.post(f'/llm/download/{sample_result_id}',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
        
        # Verify binary content
        content = response.get_data()
        assert len(content) > 0
        assert isinstance(content, bytes)
        # PDF files start with %PDF
        assert content.startswith(b'%PDF')
    
    def test_download_invalid_format_contract(self, client, sample_result_id):
        """Test invalid format error contract"""
        # Arrange
        request_data = {
            "format": "invalid_format",
            "filename": "resultado.invalid"
        }
        
        # Act
        response = client.post(f'/llm/download/{sample_result_id}',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_FORMAT'
    
    def test_download_result_not_found_contract(self, client):
        """Test result not found error contract"""
        # Arrange
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        request_data = {
            "format": "txt",
            "filename": "resultado.txt"
        }
        
        # Act
        response = client.post(f'/llm/download/{non_existent_id}',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 404
        
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'RESULT_NOT_FOUND'
    
    def test_download_missing_format_contract(self, client, sample_result_id):
        """Test missing format parameter error contract"""
        # Arrange
        request_data = {
            "filename": "resultado.txt"
        }
        
        # Act
        response = client.post(f'/llm/download/{sample_result_id}',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'
    
    def test_download_filename_header_contract(self, client, sample_result_id):
        """Test filename in response headers contract"""
        # Arrange
        request_data = {
            "format": "txt",
            "filename": "mi_resultado.txt"
        }
        
        # Act
        response = client.post(f'/llm/download/{sample_result_id}',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        # Verify Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition')
        assert content_disposition is not None
        assert 'filename=' in content_disposition
        assert 'mi_resultado.txt' in content_disposition
    
    def test_download_all_supported_formats_contract(self, client, sample_result_id):
        """Test all supported formats contract"""
        # Test all supported formats
        formats = [
            ("txt", "text/plain"),
            ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("pdf", "application/pdf")
        ]
        
        for format_type, expected_content_type in formats:
            # Arrange
            request_data = {
                "format": format_type,
                "filename": f"resultado.{format_type}"
            }
            
            # Act
            response = client.post(f'/llm/download/{sample_result_id}',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            
            # Assert - This will FAIL until implementation
            assert response.status_code == 200
            assert response.content_type == expected_content_type
            
            # Verify content is not empty
            content = response.get_data()
            assert len(content) > 0
    
    def test_download_request_validation_contract(self, client, sample_result_id):
        """Test request validation contract"""
        # Test empty request body
        response = client.post(f'/llm/download/{sample_result_id}',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error']['code'] == 'VALIDATION_ERROR'
        
        # Test invalid JSON
        response = client.post(f'/llm/download/{sample_result_id}',
                              data="invalid json",
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error']['code'] == 'VALIDATION_ERROR'
