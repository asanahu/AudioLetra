"""
Integration test for multiple profiles processing same text
Tests that different profiles produce different outputs for the same input
"""
import pytest
import json
from flask import Flask
from unittest.mock import patch

# This test will FAIL initially - that's expected in TDD approach
class TestMultipleProfiles:
    """Integration tests for multiple profiles processing same text"""
    
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
    def sample_text(self):
        """Sample text for testing multiple profiles"""
        return """
        Reunión del equipo de desarrollo del proyecto AudioLetra.
        
        Asistentes: Juan Pérez (PM), María García (Dev), Carlos López (QA), Ana Martín (Design)
        
        Agenda:
        1. Revisión del progreso del sprint actual
        2. Discusión sobre la nueva funcionalidad de perfiles LLM
        3. Planificación del próximo sprint
        4. Decisiones sobre herramientas de testing
        
        Puntos clave discutidos:
        - El desarrollo de la funcionalidad de perfiles está al 80%
        - Necesitamos implementar tests de integración
        - La interfaz de usuario necesita mejoras en la selección de perfiles
        - Se requiere documentación técnica para los nuevos endpoints
        
        Acuerdos:
        - Completar la implementación de perfiles para el viernes
        - Implementar tests de integración antes del deploy
        - Crear documentación de API para el equipo frontend
        - Programar demo para stakeholders el próximo lunes
        
        Próximos pasos:
        - Juan: Coordinar con el equipo frontend para la integración
        - María: Finalizar la implementación de servicios LLM
        - Carlos: Crear suite de tests de integración
        - Ana: Diseñar mockups para la selección de perfiles
        """
    
    def test_all_profiles_process_same_text(self, client, sample_text):
        """Test that all profiles can process the same text"""
        profiles = [
            "clean_format",
            "summarize", 
            "extract_tasks",
            "format_email",
            "meeting_minutes",
            "translate"
        ]
        
        results = {}
        
        for profile_id in profiles:
            process_data = {
                "profile_id": profile_id,
                "text": sample_text,
                "parameters": {}
            }
            
            # Add language parameter for translate profile
            if profile_id == "translate":
                process_data["parameters"]["target_language"] = "en"
            
            process_response = client.post('/llm/process',
                                          data=json.dumps(process_data),
                                          content_type='application/json')
            
            # This will FAIL until implementation
            assert process_response.status_code == 200
            
            process_result = process_response.get_json()
            assert process_result['success'] == True
            assert process_result['profile_id'] == profile_id
            assert len(process_result['output']) > 0
            
            results[profile_id] = process_result
        
        # Verify all profiles produced different outputs
        outputs = [result['output'] for result in results.values()]
        assert len(set(outputs)) == len(outputs), "All profiles should produce different outputs"
        
        # Verify each output is different from input
        for profile_id, result in results.items():
            assert result['output'] != sample_text, f"Profile {profile_id} should transform the input"
    
    def test_profiles_produce_expected_structures(self, client, sample_text):
        """Test that profiles produce expected output structures"""
        # Test extract_tasks profile
        process_data = {
            "profile_id": "extract_tasks",
            "text": sample_text,
            "parameters": {}
        }
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        # This will FAIL until implementation
        assert process_response.status_code == 200
        
        result = process_response.get_json()
        output = result['output']
        
        # Verify task extraction structure
        assert '•' in output or '-' in output or '*' in output, "Should contain bullet points"
        assert any(word in output.lower() for word in ['implementar', 'crear', 'completar', 'diseñar']), "Should contain action verbs"
        
        # Test format_email profile
        process_data['profile_id'] = 'format_email'
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        assert process_response.status_code == 200
        
        result = process_response.get_json()
        output = result['output']
        
        # Verify email structure
        assert 'Asunto:' in output or 'Subject:' in output, "Should contain subject line"
        assert 'Estimado' in output or 'Dear' in output, "Should contain greeting"
        
        # Test meeting_minutes profile
        process_data['profile_id'] = 'meeting_minutes'
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        assert process_response.status_code == 200
        
        result = process_response.get_json()
        output = result['output']
        
        # Verify meeting minutes structure
        assert any(section in output for section in ['Asistentes', 'Attendees', 'Participantes']), "Should contain attendees section"
        assert any(section in output for section in ['Acuerdos', 'Agreements', 'Decisions']), "Should contain agreements section"
        assert any(section in output for section in ['Próximos pasos', 'Next Steps', 'Action Items']), "Should contain next steps section"
    
    def test_translate_profile_multiple_languages(self, client, sample_text):
        """Test translate profile with multiple target languages"""
        languages = ['en', 'fr', 'de']
        results = {}
        
        for lang in languages:
            process_data = {
                "profile_id": "translate",
                "text": sample_text,
                "parameters": {
                    "target_language": lang
                }
            }
            
            process_response = client.post('/llm/process',
                                          data=json.dumps(process_data),
                                          content_type='application/json')
            
            # This will FAIL until implementation
            assert process_response.status_code == 200
            
            result = process_response.get_json()
            assert result['success'] == True
            assert result['profile_id'] == 'translate'
            
            results[lang] = result['output']
        
        # Verify all translations are different
        outputs = list(results.values())
        assert len(set(outputs)) == len(outputs), "All translations should be different"
        
        # Verify translations are different from original
        for lang, output in results.items():
            assert output != sample_text, f"Translation to {lang} should be different from original"
    
    def test_profiles_metadata_consistency(self, client, sample_text):
        """Test that all profiles return consistent metadata"""
        profiles = ["clean_format", "summarize", "extract_tasks"]
        
        for profile_id in profiles:
            process_data = {
                "profile_id": profile_id,
                "text": sample_text,
                "parameters": {}
            }
            
            process_response = client.post('/llm/process',
                                          data=json.dumps(process_data),
                                          content_type='application/json')
            
            # This will FAIL until implementation
            assert process_response.status_code == 200
            
            result = process_response.get_json()
            
            # Verify metadata structure
            assert 'metadata' in result
            metadata = result['metadata']
            
            assert 'processing_time' in metadata
            assert isinstance(metadata['processing_time'], (int, float))
            assert metadata['processing_time'] > 0
            
            assert 'tokens_used' in metadata
            assert isinstance(metadata['tokens_used'], int)
            assert metadata['tokens_used'] > 0
            
            assert 'model_used' in metadata
            assert isinstance(metadata['model_used'], str)
            assert len(metadata['model_used']) > 0
    
    def test_profiles_result_retrieval_consistency(self, client, sample_text):
        """Test that results can be retrieved consistently after processing"""
        profile_id = "summarize"
        
        # Process text
        process_data = {
            "profile_id": profile_id,
            "text": sample_text,
            "parameters": {}
        }
        
        process_response = client.post('/llm/process',
                                      data=json.dumps(process_data),
                                      content_type='application/json')
        
        # This will FAIL until implementation
        assert process_response.status_code == 200
        
        process_result = process_response.get_json()
        result_id = process_result['result_id']
        
        # Retrieve result multiple times
        for _ in range(3):
            result_response = client.get(f'/llm/results/{result_id}')
            assert result_response.status_code == 200
            
            result_data = result_response.get_json()
            
            # Verify consistency
            assert result_data['result_id'] == result_id
            assert result_data['profile_id'] == profile_id
            assert result_data['output'] == process_result['output']
            assert result_data['metadata'] == process_result['metadata']
    
    def test_profiles_performance_consistency(self, client, sample_text):
        """Test that profiles have consistent performance characteristics"""
        profiles = ["clean_format", "summarize", "extract_tasks"]
        processing_times = {}
        
        for profile_id in profiles:
            process_data = {
                "profile_id": profile_id,
                "text": sample_text,
                "parameters": {}
            }
            
            process_response = client.post('/llm/process',
                                          data=json.dumps(process_data),
                                          content_type='application/json')
            
            # This will FAIL until implementation
            assert process_response.status_code == 200
            
            result = process_response.get_json()
            processing_times[profile_id] = result['metadata']['processing_time']
        
        # Verify all processing times are reasonable (less than 30 seconds)
        for profile_id, time in processing_times.items():
            assert time < 30, f"Profile {profile_id} took too long: {time}s"
            assert time > 0, f"Profile {profile_id} processing time should be positive"

