"""
Unit tests for models
Tests Profile, ProcessingResult, and ResultHistory models
"""
import pytest
from datetime import datetime
from src.models.profile import Profile, ProfileManager
from src.models.result import ProcessingResult, ResultManager
from src.models.history import ResultHistory, HistoryManager


class TestProfile:
    """Test Profile model"""
    
    def test_profile_creation(self):
        """Test Profile creation with all fields"""
        profile = Profile(
            id="test_profile",
            name="Test Profile",
            description="A test profile",
            prompt_template="Test template: {{text}}",
            parameters={"param1": "value1"},
            timeout_multiplier=1.5
        )
        
        assert profile.id == "test_profile"
        assert profile.name == "Test Profile"
        assert profile.description == "A test profile"
        assert profile.prompt_template == "Test template: {{text}}"
        assert profile.parameters == {"param1": "value1"}
        assert profile.timeout_multiplier == 1.5
    
    def test_profile_defaults(self):
        """Test Profile with default values"""
        profile = Profile(
            id="minimal_profile",
            name="Minimal Profile",
            description="Minimal profile",
            prompt_template="Minimal template"
        )
        
        assert profile.parameters == {}
        assert profile.timeout_multiplier == 1.0
    
    def test_profile_validation(self):
        """Test Profile validation"""
        # Valid profile
        profile = Profile(
            id="valid_profile",
            name="Valid Profile",
            description="Valid profile",
            prompt_template="Valid template"
        )
        assert profile.id is not None
        assert profile.name is not None
        
        # Test with empty strings (should be handled by validation)
        with pytest.raises(ValueError):
            Profile(
                id="",
                name="Empty ID",
                description="Test",
                prompt_template="Test"
            )


class TestProfileManager:
    """Test ProfileManager"""
    
    def test_get_all_profiles(self):
        """Test getting all profiles"""
        manager = ProfileManager()
        profiles = manager.get_all_profiles()
        
        assert len(profiles) == 6
        assert all(isinstance(p, Profile) for p in profiles)
        
        # Check specific profiles exist
        profile_ids = [p.id for p in profiles]
        expected_ids = [
            "clean_format", "summarize", "extract_tasks",
            "format_email", "meeting_minutes", "translate"
        ]
        for expected_id in expected_ids:
            assert expected_id in profile_ids
    
    def test_get_profile_by_id(self):
        """Test getting profile by ID"""
        manager = ProfileManager()
        
        # Valid profile
        profile = manager.get_profile_by_id("clean_format")
        assert profile is not None
        assert profile.id == "clean_format"
        assert profile.name == "Limpiar y Formatear"
        
        # Invalid profile
        profile = manager.get_profile_by_id("invalid_profile")
        assert profile is None
    
    def test_profile_validation(self):
        """Test profile validation"""
        manager = ProfileManager()
        
        # Valid profile
        assert manager.validate_profile("clean_format") == True
        
        # Invalid profile
        assert manager.validate_profile("invalid_profile") == False


class TestProcessingResult:
    """Test ProcessingResult model"""
    
    def test_processing_result_creation(self):
        """Test ProcessingResult creation"""
        result = ProcessingResult(
            id="test_result_123",
            profile_id="clean_format",
            input_text="test input",
            output_text="test output",
            metadata={"tokens_used": 100},
            processing_time=2.5,
            created_at=datetime.now()
        )
        
        assert result.id == "test_result_123"
        assert result.profile_id == "clean_format"
        assert result.input_text == "test input"
        assert result.output_text == "test output"
        assert result.metadata == {"tokens_used": 100}
        assert result.processing_time == 2.5
        assert isinstance(result.created_at, datetime)
    
    def test_processing_result_defaults(self):
        """Test ProcessingResult with defaults"""
        result = ProcessingResult(
            id="test_result_456",
            profile_id="summarize",
            input_text="test input",
            output_text="test output"
        )
        
        assert result.metadata == {}
        assert result.processing_time == 0.0
        assert isinstance(result.created_at, datetime)


class TestResultManager:
    """Test ResultManager"""
    
    def test_store_and_retrieve_result(self):
        """Test storing and retrieving results"""
        manager = ResultManager()
        
        result = ProcessingResult(
            id="test_result_789",
            profile_id="extract_tasks",
            input_text="test input",
            output_text="test output"
        )
        
        # Store result
        manager.store_result(result)
        
        # Retrieve result
        retrieved = manager.get_result("test_result_789")
        assert retrieved is not None
        assert retrieved.id == result.id
        assert retrieved.profile_id == result.profile_id
        assert retrieved.input_text == result.input_text
        assert retrieved.output_text == result.output_text
    
    def test_get_nonexistent_result(self):
        """Test getting nonexistent result"""
        manager = ResultManager()
        result = manager.get_result("nonexistent_id")
        assert result is None
    
    def test_get_results_by_profile(self):
        """Test getting results by profile"""
        manager = ResultManager()
        
        # Store multiple results
        result1 = ProcessingResult(
            id="result1",
            profile_id="clean_format",
            input_text="input1",
            output_text="output1"
        )
        result2 = ProcessingResult(
            id="result2",
            profile_id="clean_format",
            input_text="input2",
            output_text="output2"
        )
        result3 = ProcessingResult(
            id="result3",
            profile_id="summarize",
            input_text="input3",
            output_text="output3"
        )
        
        manager.store_result(result1)
        manager.store_result(result2)
        manager.store_result(result3)
        
        # Get results by profile
        clean_format_results = manager.get_results_by_profile("clean_format")
        assert len(clean_format_results) == 2
        
        summarize_results = manager.get_results_by_profile("summarize")
        assert len(summarize_results) == 1
        
        # Check results are correct
        assert clean_format_results[0].id in ["result1", "result2"]
        assert clean_format_results[1].id in ["result1", "result2"]
        assert summarize_results[0].id == "result3"


class TestResultHistory:
    """Test ResultHistory model"""
    
    def test_result_history_creation(self):
        """Test ResultHistory creation"""
        history = ResultHistory(
            transcription_id="trans_123",
            results=["result1", "result2"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert history.transcription_id == "trans_123"
        assert history.results == ["result1", "result2"]
        assert isinstance(history.created_at, datetime)
        assert isinstance(history.updated_at, datetime)
    
    def test_result_history_defaults(self):
        """Test ResultHistory with defaults"""
        history = ResultHistory(transcription_id="trans_456")
        
        assert history.results == []
        assert isinstance(history.created_at, datetime)
        assert isinstance(history.updated_at, datetime)


class TestHistoryManager:
    """Test HistoryManager"""
    
    def test_store_and_retrieve_history(self):
        """Test storing and retrieving history"""
        manager = HistoryManager()
        
        history = ResultHistory(
            transcription_id="trans_789",
            results=["result1", "result2"]
        )
        
        # Store history
        manager.store_history(history)
        
        # Retrieve history
        retrieved = manager.get_history("trans_789")
        assert retrieved is not None
        assert retrieved.transcription_id == history.transcription_id
        assert retrieved.results == history.results
    
    def test_get_nonexistent_history(self):
        """Test getting nonexistent history"""
        manager = HistoryManager()
        history = manager.get_history("nonexistent_id")
        assert history is None
    
    def test_add_result_to_history(self):
        """Test adding result to existing history"""
        manager = HistoryManager()
        
        # Create initial history
        history = ResultHistory(
            transcription_id="trans_123",
            results=["result1"]
        )
        manager.store_history(history)
        
        # Add new result
        manager.add_result_to_history("trans_123", "result2")
        
        # Retrieve updated history
        updated = manager.get_history("trans_123")
        assert len(updated.results) == 2
        assert "result1" in updated.results
        assert "result2" in updated.results
    
    def test_get_all_histories(self):
        """Test getting all histories"""
        manager = HistoryManager()
        
        # Store multiple histories
        history1 = ResultHistory(transcription_id="trans_1", results=["result1"])
        history2 = ResultHistory(transcription_id="trans_2", results=["result2"])
        
        manager.store_history(history1)
        manager.store_history(history2)
        
        # Get all histories
        all_histories = manager.get_all_histories()
        assert len(all_histories) == 2
        
        # Check histories are correct
        trans_ids = [h.transcription_id for h in all_histories]
        assert "trans_1" in trans_ids
        assert "trans_2" in trans_ids


# Integration tests for models working together
class TestModelIntegration:
    """Test models working together"""
    
    def test_profile_result_integration(self):
        """Test Profile and ProcessingResult integration"""
        profile_manager = ProfileManager()
        result_manager = ResultManager()
        
        # Get a profile
        profile = profile_manager.get_profile_by_id("clean_format")
        assert profile is not None
        
        # Create result using profile
        result = ProcessingResult(
            id="integration_test",
            profile_id=profile.id,
            input_text="test input",
            output_text="test output"
        )
        
        # Store result
        result_manager.store_result(result)
        
        # Retrieve and verify
        retrieved = result_manager.get_result("integration_test")
        assert retrieved.profile_id == profile.id
    
    def test_result_history_integration(self):
        """Test ProcessingResult and ResultHistory integration"""
        result_manager = ResultManager()
        history_manager = HistoryManager()
        
        # Create and store result
        result = ProcessingResult(
            id="history_test",
            profile_id="summarize",
            input_text="test input",
            output_text="test output"
        )
        result_manager.store_result(result)
        
        # Create history with result
        history = ResultHistory(
            transcription_id="trans_history",
            results=[result.id]
        )
        history_manager.store_history(history)
        
        # Verify integration
        retrieved_history = history_manager.get_history("trans_history")
        assert result.id in retrieved_history.results
        
        retrieved_result = result_manager.get_result(result.id)
        assert retrieved_result is not None
        assert retrieved_result.profile_id == "summarize"
