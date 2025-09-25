"""
Performance tests for timeout calculation and system performance
"""
import pytest
import time
from src.utils.timeout import get_timeout_for_text
from src.models.profile import ProfileManager
from src.services.profile_service import ProfileService
from src.config import Config


class TestTimeoutCalculation:
    """Test timeout calculation performance"""
    
    def test_timeout_calculation_short_text(self):
        """Test timeout calculation for short text"""
        text = "a" * 1000  # 1000 characters
        
        timeout = get_timeout_for_text(text, "clean_format")
        
        # Should be 30s base + 1s per 1000 chars = 31s
        assert timeout == 31
    
    def test_timeout_calculation_medium_text(self):
        """Test timeout calculation for medium text"""
        text = "a" * 10000  # 10000 characters
        
        timeout = get_timeout_for_text(text, "clean_format")
        
        # Should be 30s base + 10s per 10000 chars = 40s
        assert timeout == 40
    
    def test_timeout_calculation_long_text(self):
        """Test timeout calculation for long text"""
        text = "a" * 50000  # 50000 characters
        
        timeout = get_timeout_for_text(text, "clean_format")
        
        # Should be 30s base + 50s per 50000 chars = 80s
        assert timeout == 80
    
    def test_timeout_calculation_with_multiplier(self):
        """Test timeout calculation with profile multiplier"""
        text = "a" * 1000  # 1000 characters
        
        # Test with translate profile (multiplier 2.0)
        timeout = get_timeout_for_text(text, "translate")
        
        # Should be (30s base + 1s) * 2.0 = 62s
        assert timeout == 62
    
    def test_timeout_calculation_edge_cases(self):
        """Test timeout calculation edge cases"""
        # Empty text
        timeout = get_timeout_for_text("", "clean_format")
        assert timeout == 30  # Base timeout
        
        # Very short text
        timeout = get_timeout_for_text("a", "clean_format")
        assert timeout == 30  # Base timeout
        
        # Very long text
        text = "a" * 100000  # 100000 characters
        timeout = get_timeout_for_text(text, "clean_format")
        assert timeout == 130  # 30s base + 100s
    
    def test_timeout_calculation_performance(self):
        """Test timeout calculation performance"""
        # Test that calculation is fast
        text = "a" * 10000
        
        start_time = time.time()
        timeout = get_timeout_for_text(text, "clean_format")
        end_time = time.time()
        
        calculation_time = end_time - start_time
        
        # Should be very fast (< 1ms)
        assert calculation_time < 0.001
        assert timeout == 40


class TestProfileServicePerformance:
    """Test ProfileService performance"""
    
    def test_get_all_profiles_performance(self):
        """Test getting all profiles performance"""
        config = Config()
        service = ProfileService(config)
        
        start_time = time.time()
        profiles = service.get_all_profiles()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 10ms)
        assert execution_time < 0.01
        assert len(profiles) == 6
    
    def test_get_profile_by_id_performance(self):
        """Test getting profile by ID performance"""
        config = Config()
        service = ProfileService(config)
        
        start_time = time.time()
        profile = service.get_profile_by_id("clean_format")
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 5ms)
        assert execution_time < 0.005
        assert profile is not None
        assert profile.id == "clean_format"
    
    def test_validate_profile_performance(self):
        """Test profile validation performance"""
        config = Config()
        service = ProfileService(config)
        
        # Test valid profile
        start_time = time.time()
        result = service.validate_profile("clean_format")
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 5ms)
        assert execution_time < 0.005
        assert result == True
        
        # Test invalid profile
        start_time = time.time()
        result = service.validate_profile("invalid_profile")
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 5ms)
        assert execution_time < 0.005
        assert result == False


class TestModelPerformance:
    """Test model performance"""
    
    def test_profile_manager_performance(self):
        """Test ProfileManager performance"""
        manager = ProfileManager()
        
        # Test getting all profiles
        start_time = time.time()
        profiles = manager.get_all_profiles()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 5ms)
        assert execution_time < 0.005
        assert len(profiles) == 6
        
        # Test getting profile by ID
        start_time = time.time()
        profile = manager.get_profile_by_id("clean_format")
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 1ms)
        assert execution_time < 0.001
        assert profile is not None
    
    def test_result_manager_performance(self):
        """Test ResultManager performance"""
        from src.models.result import ResultManager, ProcessingResult
        from datetime import datetime
        
        manager = ResultManager()
        
        # Test storing result
        result = ProcessingResult(
            id="perf_test_123",
            profile_id="clean_format",
            input_text="test input",
            output_text="test output"
        )
        
        start_time = time.time()
        manager.store_result(result)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 1ms)
        assert execution_time < 0.001
        
        # Test retrieving result
        start_time = time.time()
        retrieved = manager.get_result("perf_test_123")
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 1ms)
        assert execution_time < 0.001
        assert retrieved is not None
        assert retrieved.id == "perf_test_123"


class TestValidationPerformance:
    """Test validation performance"""
    
    def test_request_validator_performance(self):
        """Test RequestValidator performance"""
        from src.utils.validation import RequestValidator
        
        validator = RequestValidator()
        
        # Test validating request data
        data = {
            "profile_id": "clean_format",
            "text": "test text",
            "parameters": {}
        }
        
        start_time = time.time()
        result = validator.validate_request_data(data)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 1ms)
        assert execution_time < 0.001
        assert result == True
    
    def test_validation_functions_performance(self):
        """Test validation functions performance"""
        from src.utils.validation import require_profile_id, require_text, require_result_id
        
        # Test all validation functions
        start_time = time.time()
        
        profile_valid = require_profile_id("clean_format")
        text_valid = require_text("test text")
        result_valid = require_result_id("result_123")
        
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should be very fast (< 1ms)
        assert execution_time < 0.001
        assert profile_valid == True
        assert text_valid == True
        assert result_valid == True


class TestSystemPerformance:
    """Test overall system performance"""
    
    def test_system_initialization_performance(self):
        """Test system initialization performance"""
        start_time = time.time()
        
        # Initialize all major components
        config = Config()
        profile_service = ProfileService(config)
        profile_manager = ProfileManager()
        
        end_time = time.time()
        
        initialization_time = end_time - start_time
        
        # Should be fast (< 50ms)
        assert initialization_time < 0.05
    
    def test_memory_usage(self):
        """Test memory usage of key components"""
        import sys
        
        # Test ProfileManager memory usage
        manager = ProfileManager()
        profiles = manager.get_all_profiles()
        
        # Should not use excessive memory
        assert len(profiles) == 6
        
        # Test that profiles are lightweight
        for profile in profiles:
            assert sys.getsizeof(profile) < 1000  # Less than 1KB per profile
    
    def test_concurrent_access_performance(self):
        """Test concurrent access performance"""
        import threading
        import time
        
        config = Config()
        service = ProfileService(config)
        
        results = []
        
        def get_profiles():
            start_time = time.time()
            profiles = service.get_all_profiles()
            end_time = time.time()
            results.append(end_time - start_time)
        
        # Test concurrent access
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_profiles)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All should complete quickly
        for execution_time in results:
            assert execution_time < 0.01  # Less than 10ms each
        
        # Should have 10 results
        assert len(results) == 10


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Test performance benchmarks"""
    
    def test_timeout_calculation_benchmark(self):
        """Benchmark timeout calculation"""
        text_lengths = [1000, 10000, 50000, 100000]
        
        for length in text_lengths:
            text = "a" * length
            
            start_time = time.time()
            timeout = get_timeout_for_text(text, "clean_format")
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Should be very fast regardless of text length
            assert execution_time < 0.001
            assert timeout > 0
    
    def test_profile_operations_benchmark(self):
        """Benchmark profile operations"""
        config = Config()
        service = ProfileService(config)
        
        # Benchmark getting all profiles
        start_time = time.time()
        for _ in range(100):
            profiles = service.get_all_profiles()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        
        # Should average less than 1ms per operation
        assert avg_time < 0.001
        assert len(profiles) == 6
    
    def test_validation_benchmark(self):
        """Benchmark validation operations"""
        from src.utils.validation import RequestValidator
        
        validator = RequestValidator()
        
        # Benchmark validation
        data = {
            "profile_id": "clean_format",
            "text": "test text",
            "parameters": {}
        }
        
        start_time = time.time()
        for _ in range(1000):
            result = validator.validate_request_data(data)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000
        
        # Should average less than 0.1ms per operation
        assert avg_time < 0.0001
        assert result == True
