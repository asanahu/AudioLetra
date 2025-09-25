"""
Integration test for profile processing flow
Tests the complete flow from profile selection to result generation
"""
import pytest
import json
from flask import Flask
from unittest.mock import patch, MagicMock

# This test will FAIL initially - that's expected in TDD approach
class TestProfileProcessingFlow:
    """Integration tests for complete profile processing flow"""
    
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
    
    def test_complete_profile_processing_flow(self, client):
        """Test complete profile processing flow"""
        # Step 1: Get available profiles
        profiles_response = client.get('/llm/profiles')
        assert profiles_response.status_code == 200
        
        profiles_data = profiles_response.get_json()
        assert 'profiles' in profiles_data
        assert len(profiles_data['profiles']) == 6
        
        # Step 2: Process text with clean_format profile
        process_data = {
            "profile_id": "clean_format",
            "text": "hola mundo esto es una prueba de procesamiento",
            "parameters": {}
        }
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        # This will FAIL until implementation
        assert process_response.status_code == 200
        
        process_result = process_response.get_json()
        assert process_result['success'] == True
        assert process_result['profile_id'] == 'clean_format'
        assert 'result_id' in process_result
        assert 'output' in process_result
        
        result_id = process_result['result_id']
        
        # Step 3: Retrieve the result
        result_response = client.get(f'/llm/results/{result_id}')
        assert result_response.status_code == 200
        
        result_data = result_response.get_json()
        assert result_data['result_id'] == result_id
        assert result_data['profile_id'] == 'clean_format'
        assert len(result_data['output']) > 0
        
        # Step 4: Download the result
        download_data = {
            "format": "txt",
            "filename": "resultado.txt"
        }
        
        download_response = client.post(f'/llm/download/{result_id}',
                                       data=json.dumps(download_data),
                                       content_type='application/json')
        
        assert download_response.status_code == 200
        assert download_response.content_type == 'text/plain'
        
        # Verify downloaded content
        downloaded_content = download_response.get_data(as_text=True)
        assert len(downloaded_content) > 0
        assert downloaded_content == result_data['output']
    
    def test_multiple_profiles_same_text_flow(self, client):
        """Test processing same text with multiple profiles"""
        test_text = "Reunión del equipo para discutir nuevos proyectos y estrategias"
        
        # Process with different profiles
        profiles_to_test = ["summarize", "extract_tasks", "format_email"]
        results = {}
        
        for profile_id in profiles_to_test:
            process_data = {
                "profile_id": profile_id,
                "text": test_text,
                "parameters": {}
            }
            
            process_response = client.post('/llm/process',
                                          data=json.dumps(process_data),
                                          content_type='application/json')
            
            # This will FAIL until implementation
            assert process_response.status_code == 200
            
            process_result = process_response.get_json()
            assert process_result['success'] == True
            assert process_result['profile_id'] == profile_id
            
            results[profile_id] = process_result
        
        # Verify all results are different
        outputs = [result['output'] for result in results.values()]
        assert len(set(outputs)) == len(outputs)  # All outputs should be unique
        
        # Verify each result can be retrieved
        for profile_id, result in results.items():
            result_id = result['result_id']
            
            result_response = client.get(f'/llm/results/{result_id}')
            assert result_response.status_code == 200
            
            result_data = result_response.get_json()
            assert result_data['profile_id'] == profile_id
            assert result_data['output'] == result['output']
    
    def test_translate_profile_with_parameters_flow(self, client):
        """Test translate profile with language parameters"""
        test_text = "Hola mundo, esto es una prueba de traducción"
        
        # Test translation to English
        process_data = {
            "profile_id": "translate",
            "text": test_text,
            "parameters": {
                "target_language": "en"
            }
        }
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        # This will FAIL until implementation
        assert process_response.status_code == 200
        
        process_result = process_response.get_json()
        assert process_result['success'] == True
        assert process_result['profile_id'] == 'translate'
        
        # Verify output is different from input (translated)
        assert process_result['output'] != test_text
        assert len(process_result['output']) > 0
        
        # Test translation to French
        process_data['parameters']['target_language'] = 'fr'
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        assert process_response.status_code == 200
        
        french_result = process_response.get_json()
        assert french_result['success'] == True
        
        # Verify different outputs for different languages
        assert french_result['output'] != process_result['output']
    
    def test_meeting_minutes_profile_flow(self, client):
        """Test meeting minutes profile processing flow"""
        meeting_text = """
        Reunión del equipo de desarrollo
        Fecha: 17 de enero de 2025
        Asistentes: Juan, María, Carlos, Ana
        
        Puntos discutidos:
        - Nuevo proyecto de aplicación móvil
        - Presupuesto para herramientas de desarrollo
        - Cronograma de entrega para el primer trimestre
        
        Acuerdos:
        - Comenzar desarrollo en febrero
        - Usar React Native para la aplicación
        - Reunión semanal los viernes
        
        Próximos pasos:
        - Juan: Investigar herramientas de testing
        - María: Crear mockups de la interfaz
        - Carlos: Configurar entorno de desarrollo
        """
        
        process_data = {
            "profile_id": "meeting_minutes",
            "text": meeting_text,
            "parameters": {}
        }
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        # This will FAIL until implementation
        assert process_response.status_code == 200
        
        process_result = process_response.get_json()
        assert process_result['success'] == True
        assert process_result['profile_id'] == 'meeting_minutes'
        
        # Verify structured output
        output = process_result['output']
        assert len(output) > 0
        
        # Verify output contains meeting structure elements
        assert 'Asistentes' in output or 'Attendees' in output
        assert 'Acuerdos' in output or 'Agreements' in output
        assert 'Próximos pasos' in output or 'Next Steps' in output
    
    def test_error_handling_in_flow(self, client):
        """Test error handling throughout the flow"""
        # Test invalid profile
        process_data = {
            "profile_id": "invalid_profile",
            "text": "test text",
            "parameters": {}
        }
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        # This will FAIL until implementation
        assert process_response.status_code == 400
        
        error_data = process_response.get_json()
        assert error_data['success'] == False
        assert error_data['error']['code'] == 'INVALID_PROFILE'
        
        # Test empty text
        process_data = {
            "profile_id": "clean_format",
            "text": "",
            "parameters": {}
        }
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        assert process_response.status_code == 400
        
        error_data = process_response.get_json()
        assert error_data['success'] == False
        assert error_data['error']['code'] == 'INVALID_TEXT'
    
    def test_timeout_handling_in_flow(self, client):
        """Test timeout handling in processing flow"""
        # Test with very long text that might cause timeout
        long_text = "a" * 100000  # 100k characters
        
        process_data = {
            "profile_id": "summarize",
            "text": long_text,
            "parameters": {}
        }
        
        # Mock timeout scenario
        with patch('src.services.llm_service.LLMService.process_text') as mock_process:
            mock_process.side_effect = TimeoutError("Processing timeout")
            
            process_response = client.post('/llm/process',
                                          data=json.dumps(process_data),
                                          content_type='application/json')
        
        # This will FAIL until implementation
        assert process_response.status_code == 408
        
        error_data = process_response.get_json()
        assert error_data['success'] == False
        assert error_data['error']['code'] == 'TIMEOUT_ERROR'
