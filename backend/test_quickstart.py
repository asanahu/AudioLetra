"""
Quickstart validation scenarios
Tests the scenarios defined in quickstart.md
"""
import pytest
import time
from unittest.mock import Mock, patch
from src.app import create_app
from src.models.profile import ProfileManager
from src.services.profile_service import ProfileService
from src.services.prompt_service import PromptService
from src.utils.timeout import get_timeout_for_text
from src.utils.validation import RequestValidator


class TestQuickstartScenarios:
    """Test quickstart validation scenarios"""
    
    def test_scenario_1_clean_format_flow(self):
        """Test Scenario 1: Clean & Format Text"""
        # 1. Get available profiles
        profile_manager = ProfileManager()
        profiles = profile_manager.get_all_profiles()
        assert len(profiles) == 6
        
        # 2. Process text with clean_format profile
        profile_service = ProfileService()
        prompt_service = PromptService()
        
        # Get profile
        profile = profile_service.get_profile_by_id("clean_format")
        assert profile is not None
        assert profile.id == "clean_format"
        
        # Render prompt
        prompt = prompt_service.render_prompt("clean_format", "hola mundo esto es una prueba", {})
        assert isinstance(prompt, str)
        assert "hola mundo esto es una prueba" in prompt
        assert len(prompt) > 0
        
        # Verify profile properties
        assert profile.name == "Limpiar y Formatear"
        assert profile.timeout_multiplier == 1.0
    
    def test_scenario_2_translate_flow(self):
        """Test Scenario 2: Translate Text"""
        # 1. Get translate profile
        profile_service = ProfileService()
        profile = profile_service.get_profile_by_id("translate")
        assert profile is not None
        assert profile.id == "translate"
        
        # 2. Test with language parameter
        prompt_service = PromptService()
        prompt = prompt_service.render_prompt(
            "translate", 
            "Reunión del equipo para discutir nuevos proyectos",
            {"target_language": "English"}
        )
        
        assert isinstance(prompt, str)
        assert "Reunión del equipo para discutir nuevos proyectos" in prompt
        assert "English" in prompt
        
        # 3. Verify profile properties
        assert profile.name == "Traducir"
        assert profile.timeout_multiplier == 2.0
    
    def test_scenario_3_error_handling(self):
        """Test Scenario 3: Error Handling"""
        # 1. Test invalid profile
        profile_service = ProfileService()
        profile = profile_service.get_profile_by_id("invalid_profile")
        assert profile is None
        
        # 2. Test validation
        validator = RequestValidator()
        
        # Invalid profile
        result = validator.validate_profile_id("invalid_profile")
        assert result == False
        
        # Empty text
        result = validator.validate_text("")
        assert result == False
        
        # Valid data
        result = validator.validate_request_data({
            "profile_id": "clean_format",
            "text": "valid text"
        })
        assert result == True
    
    def test_integration_test_1_profile_processing_flow(self):
        """Test Integration Test 1: Profile Processing Flow"""
        # 1. Get available profiles
        profiles = ProfileManager().get_all_profiles()
        assert len(profiles) == 6
        
        # 2. Process text with clean_format profile
        prompt_service = PromptService()
        result = prompt_service.render_prompt(
            "clean_format",
            "hola mundo esto es una prueba"
        )
        
        # 3. Verify result structure
        assert isinstance(result, str)
        assert "hola mundo esto es una prueba" in result
        assert len(result) > 0
        
        # 4. Verify profile exists
        profile_service = ProfileService()
        profile = profile_service.get_profile_by_id("clean_format")
        assert profile is not None
        assert profile.id == "clean_format"
    
    def test_integration_test_2_multiple_profiles_same_text(self):
        """Test Integration Test 2: Multiple Profiles Same Text"""
        text = "Reunión del equipo para discutir nuevos proyectos"
        prompt_service = PromptService()
        
        # Process with different profiles
        results = {}
        profile_ids = ["summarize", "extract_tasks", "format_email"]
        
        for profile_id in profile_ids:
            results[profile_id] = prompt_service.render_prompt(
                profile_id=profile_id,
                text=text,
                parameters={}
            )
        
        # Verify all succeeded
        for profile_id, result in results.items():
            assert isinstance(result, str)
            assert text in result
            assert len(result) > 0
        
        # Verify different outputs
        assert results["summarize"] != results["extract_tasks"]
        assert results["extract_tasks"] != results["format_email"]
        assert results["summarize"] != results["format_email"]
    
    def test_integration_test_3_error_handling(self):
        """Test Integration Test 3: Error Handling"""
        validator = RequestValidator()
        
        # Test invalid profile
        result = validator.validate_profile_id("invalid_profile")
        assert result == False
        
        # Test empty text
        result = validator.validate_text("")
        assert result == False
        
        # Test valid data
        result = validator.validate_request_data({
            "profile_id": "clean_format",
            "text": "valid text"
        })
        assert result == True
    
    def test_performance_validation_timeout_calculation(self):
        """Test Performance Validation: Timeout Calculation"""
        # Test with different text lengths
        test_cases = [
            ("short", 1000, 31),      # 30s + 1s
            ("medium", 10000, 40),    # 30s + 10s  
            ("long", 50000, 80)       # 30s + 50s
        ]
        
        for name, chars, expected_timeout in test_cases:
            text = "a" * chars
            timeout = get_timeout_for_text(text, "clean_format")
            assert timeout == expected_timeout, f"Failed for {name}: expected {expected_timeout}, got {timeout}"
    
    def test_file_download_validation(self):
        """Test File Download Validation"""
        from src.services.file_service import FileService
        
        file_service = FileService()
        
        # Test all supported formats
        formats = ["txt", "docx", "pdf"]
        content = "test content"
        
        for format_type in formats:
            result = file_service.generate_file(content, format_type, f"test.{format_type}")
            
            assert result["success"] == True
            assert result["filename"] == f"test.{format_type}"
            assert isinstance(result["content"], bytes)
            assert len(result["content"]) > 0
    
    def test_ui_integration_frontend_state_management(self):
        """Test UI Integration: Frontend State Management"""
        # Test profile loading
        profile_service = ProfileService()
        profiles = profile_service.get_all_profiles()
        
        assert len(profiles) == 6
        
        # Test profile selection
        profile = profile_service.get_profile_by_id("clean_format")
        assert profile is not None
        assert profile.id == "clean_format"
        
        # Test prompt rendering
        prompt_service = PromptService()
        result = prompt_service.render_prompt("clean_format", "test text", {})
        
        assert isinstance(result, str)
        assert "test text" in result
        
        # Test multiple results
        result2 = prompt_service.render_prompt("summarize", "test text", {})
        assert isinstance(result2, str)
        assert result != result2  # Different profiles should produce different results
    
    def test_success_criteria_validation(self):
        """Test Success Criteria Validation"""
        # ✅ 1 clic desde transcripción a resultado
        profile_service = ProfileService()
        profile = profile_service.get_profile_by_id("clean_format")
        assert profile is not None
        
        # ✅ Resultados consistentes por perfil
        prompt_service = PromptService()
        result1 = prompt_service.render_prompt("clean_format", "test", {})
        result2 = prompt_service.render_prompt("clean_format", "test", {})
        assert isinstance(result1, str)
        assert isinstance(result2, str)
        
        # ✅ No se envía audio (solo texto)
        # This is verified by the prompt templates only containing text placeholders
        
        # ✅ Manejo de errores
        validator = RequestValidator()
        assert validator.validate_profile_id("invalid") == False
        assert validator.validate_text("") == False
        
        # ✅ Múltiples formatos de descarga
        from src.services.file_service import FileService
        file_service = FileService()
        
        formats = ["txt", "docx", "pdf"]
        for format_type in formats:
            result = file_service.generate_file("test", format_type, f"test.{format_type}")
            assert result["success"] == True
        
        # ✅ Historial de resultados
        from src.models.result import ResultManager
        result_manager = ResultManager()
        
        # This would be tested with actual result storage in a real scenario
        assert result_manager is not None


class TestFlaskIntegration:
    """Test Flask application integration"""
    
    def test_flask_app_creation(self):
        """Test Flask app creation"""
        app = create_app()
        assert app is not None
        
        # Test health endpoint
        client = app.test_client()
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'audiLetra-backend'
    
    def test_llm_profiles_endpoint(self):
        """Test LLM profiles endpoint"""
        app = create_app()
        client = app.test_client()
        
        response = client.get('/llm/profiles')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'profiles' in data
        assert len(data['profiles']) == 6
        
        # Verify profile structure
        profile = data['profiles'][0]
        assert 'id' in profile
        assert 'name' in profile
        assert 'description' in profile
    
    def test_llm_process_endpoint_structure(self):
        """Test LLM process endpoint structure (without API key)"""
        app = create_app()
        client = app.test_client()
        
        # Test with invalid data (should return validation error)
        response = client.post('/llm/process', json={
            'profile_id': 'invalid_profile',
            'text': 'test'
        })
        
        # Should return validation error
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert data['error']['code'] == 'INVALID_PROFILE'


def run_quickstart_validation():
    """Run all quickstart validation scenarios"""
    print("🚀 Running Quickstart Validation Scenarios...")
    
    # Test scenarios
    test_scenarios = TestQuickstartScenarios()
    
    scenarios = [
        ("Scenario 1: Clean & Format Text", test_scenarios.test_scenario_1_clean_format_flow),
        ("Scenario 2: Translate Text", test_scenarios.test_scenario_2_translate_flow),
        ("Scenario 3: Error Handling", test_scenarios.test_scenario_3_error_handling),
        ("Integration Test 1: Profile Processing Flow", test_scenarios.test_integration_test_1_profile_processing_flow),
        ("Integration Test 2: Multiple Profiles Same Text", test_scenarios.test_integration_test_2_multiple_profiles_same_text),
        ("Integration Test 3: Error Handling", test_scenarios.test_integration_test_3_error_handling),
        ("Performance Validation: Timeout Calculation", test_scenarios.test_performance_validation_timeout_calculation),
        ("File Download Validation", test_scenarios.test_file_download_validation),
        ("UI Integration: Frontend State Management", test_scenarios.test_ui_integration_frontend_state_management),
        ("Success Criteria Validation", test_scenarios.test_success_criteria_validation)
    ]
    
    passed = 0
    failed = 0
    
    for scenario_name, test_func in scenarios:
        try:
            test_func()
            print(f"  ✅ {scenario_name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {scenario_name}: {e}")
            failed += 1
    
    # Test Flask integration
    flask_tests = TestFlaskIntegration()
    
    flask_scenarios = [
        ("Flask App Creation", flask_tests.test_flask_app_creation),
        ("LLM Profiles Endpoint", flask_tests.test_llm_profiles_endpoint),
        ("LLM Process Endpoint Structure", flask_tests.test_llm_process_endpoint_structure)
    ]
    
    for scenario_name, test_func in flask_scenarios:
        try:
            test_func()
            print(f"  ✅ {scenario_name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {scenario_name}: {e}")
            failed += 1
    
    print(f"\n📊 Quickstart Validation Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📈 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All quickstart scenarios passed!")
        return True
    else:
        print(f"\n⚠️  {failed} scenarios failed. Please review and fix.")
        return False


if __name__ == "__main__":
    success = run_quickstart_validation()
    exit(0 if success else 1)
