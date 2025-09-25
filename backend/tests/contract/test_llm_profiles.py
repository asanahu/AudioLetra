"""
Contract test for GET /llm/profiles endpoint
Tests the API contract for retrieving available LLM profiles
"""
import pytest
import json
from flask import Flask

# This test will FAIL initially - that's expected in TDD approach
class TestLLMProfilesContract:
    """Contract tests for GET /llm/profiles endpoint"""
    
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
    
    def test_get_profiles_success_contract(self, client):
        """Test successful profiles retrieval contract"""
        # Act
        response = client.get('/llm/profiles')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'profiles' in data
        assert isinstance(data['profiles'], list)
        assert len(data['profiles']) == 6  # Expected 6 predefined profiles
        
        # Verify profile structure
        profile = data['profiles'][0]
        assert 'id' in profile
        assert 'name' in profile
        assert 'description' in profile
        assert 'parameters' in profile
    
    def test_profiles_include_all_predefined_contract(self, client):
        """Test that all predefined profiles are included"""
        # Act
        response = client.get('/llm/profiles')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        data = response.get_json()
        profiles = data['profiles']
        
        # Check all 6 predefined profiles are present
        expected_profiles = [
            'clean_format',
            'summarize', 
            'extract_tasks',
            'format_email',
            'meeting_minutes',
            'translate'
        ]
        
        profile_ids = [p['id'] for p in profiles]
        for expected_id in expected_profiles:
            assert expected_id in profile_ids
    
    def test_profile_structure_contract(self, client):
        """Test individual profile structure contract"""
        # Act
        response = client.get('/llm/profiles')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        data = response.get_json()
        profiles = data['profiles']
        
        # Test clean_format profile
        clean_profile = next(p for p in profiles if p['id'] == 'clean_format')
        assert clean_profile['name'] == 'Limpiar y Formatear'
        assert 'Mejora la puntuación' in clean_profile['description']
        assert isinstance(clean_profile['parameters'], dict)
        
        # Test translate profile with parameters
        translate_profile = next(p for p in profiles if p['id'] == 'translate')
        assert translate_profile['name'] == 'Traducir'
        assert 'supported_languages' in translate_profile['parameters']
        assert isinstance(translate_profile['parameters']['supported_languages'], list)
        assert 'es' in translate_profile['parameters']['supported_languages']
        assert 'en' in translate_profile['parameters']['supported_languages']
        assert 'fr' in translate_profile['parameters']['supported_languages']
        assert 'de' in translate_profile['parameters']['supported_languages']
    
    def test_profiles_response_format_contract(self, client):
        """Test response format contract"""
        # Act
        response = client.get('/llm/profiles')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        
        # Verify response is valid JSON
        assert isinstance(data, dict)
        assert 'profiles' in data
        
        # Verify profiles array structure
        profiles = data['profiles']
        assert isinstance(profiles, list)
        assert len(profiles) > 0
        
        # Verify each profile has required fields
        for profile in profiles:
            assert isinstance(profile, dict)
            assert 'id' in profile
            assert 'name' in profile
            assert 'description' in profile
            assert 'parameters' in profile
            
            # Verify field types
            assert isinstance(profile['id'], str)
            assert isinstance(profile['name'], str)
            assert isinstance(profile['description'], str)
            assert isinstance(profile['parameters'], dict)
    
    def test_profiles_no_auth_required_contract(self, client):
        """Test that profiles endpoint doesn't require authentication"""
        # Act
        response = client.get('/llm/profiles')
        
        # Assert - This will FAIL until implementation
        assert response.status_code == 200
        
        # Should not require any authentication headers
        data = response.get_json()
        assert 'profiles' in data
