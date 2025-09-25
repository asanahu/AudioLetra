"""
Timeout calculation logic
Calculates processing timeouts based on text length and profile characteristics
"""
from typing import Optional
from src.config import Config
from src.services.profile_service import get_profile_service


class TimeoutCalculator:
    """Calculates timeouts for LLM processing"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.profile_service = get_profile_service(config)
    
    def calculate_timeout(self, text_length: int, profile_id: Optional[str] = None) -> int:
        """Calculate timeout based on text length and profile"""
        # Base timeout from config
        base_timeout = self.config.DEFAULT_TIMEOUT_BASE
        
        # Additional time per 1000 characters
        chars_per_unit = 1000
        additional_time_per_unit = self.config.TIMEOUT_PER_1000_CHARS
        
        # Calculate base timeout based on text length
        additional_time = (text_length // chars_per_unit) * additional_time_per_unit
        calculated_timeout = base_timeout + additional_time
        
        # Apply profile-specific multiplier if profile is provided
        if profile_id:
            multiplier = self.profile_service.get_profile_timeout_multiplier(profile_id)
            calculated_timeout = int(calculated_timeout * multiplier)
        
        # Ensure minimum and maximum bounds
        min_timeout = 10  # Minimum 10 seconds
        max_timeout = 300  # Maximum 5 minutes
        
        return max(min_timeout, min(calculated_timeout, max_timeout))
    
    def calculate_timeout_with_buffer(self, text_length: int, profile_id: Optional[str] = None, buffer_percent: int = 20) -> int:
        """Calculate timeout with additional buffer"""
        base_timeout = self.calculate_timeout(text_length, profile_id)
        buffer = int(base_timeout * (buffer_percent / 100))
        return base_timeout + buffer
    
    def get_timeout_breakdown(self, text_length: int, profile_id: Optional[str] = None) -> dict:
        """Get detailed timeout calculation breakdown"""
        base_timeout = self.config.DEFAULT_TIMEOUT_BASE
        chars_per_unit = 1000
        additional_time_per_unit = self.config.TIMEOUT_PER_1000_CHARS
        
        # Calculate components
        text_units = text_length // chars_per_unit
        additional_time = text_units * additional_time_per_unit
        base_calculated = base_timeout + additional_time
        
        # Get profile multiplier
        profile_multiplier = 1.0
        if profile_id:
            profile_multiplier = self.profile_service.get_profile_timeout_multiplier(profile_id)
        
        # Final calculation
        final_timeout = int(base_calculated * profile_multiplier)
        
        # Apply bounds
        min_timeout = 10
        max_timeout = 300
        bounded_timeout = max(min_timeout, min(final_timeout, max_timeout))
        
        return {
            "text_length": text_length,
            "text_units": text_units,
            "base_timeout": base_timeout,
            "additional_time": additional_time,
            "base_calculated": base_calculated,
            "profile_id": profile_id,
            "profile_multiplier": profile_multiplier,
            "final_timeout": final_timeout,
            "bounded_timeout": bounded_timeout,
            "min_timeout": min_timeout,
            "max_timeout": max_timeout,
            "was_bounded": final_timeout != bounded_timeout
        }
    
    def estimate_processing_time(self, text_length: int, profile_id: Optional[str] = None) -> dict:
        """Estimate actual processing time (usually less than timeout)"""
        timeout = self.calculate_timeout(text_length, profile_id)
        
        # Estimate actual processing time as percentage of timeout
        # Based on profile complexity
        complexity_factors = {
            "clean_format": 0.3,    # Simple formatting
            "summarize": 0.6,       # More complex analysis
            "extract_tasks": 0.4,   # Moderate complexity
            "format_email": 0.3,    # Simple formatting
            "meeting_minutes": 0.7, # Complex structuring
            "translate": 0.8        # Most complex
        }
        
        complexity_factor = complexity_factors.get(profile_id, 0.5)
        estimated_time = int(timeout * complexity_factor)
        
        return {
            "timeout": timeout,
            "estimated_processing_time": estimated_time,
            "complexity_factor": complexity_factor,
            "profile_id": profile_id,
            "confidence": "medium"  # Could be low/medium/high based on historical data
        }
    
    def get_timeout_recommendations(self, text_length: int) -> dict:
        """Get timeout recommendations for different scenarios"""
        recommendations = {}
        
        # Calculate for each profile
        profile_ids = ["clean_format", "summarize", "extract_tasks", "format_email", "meeting_minutes", "translate"]
        
        for profile_id in profile_ids:
            timeout = self.calculate_timeout(text_length, profile_id)
            estimate = self.estimate_processing_time(text_length, profile_id)
            
            recommendations[profile_id] = {
                "timeout": timeout,
                "estimated_time": estimate["estimated_processing_time"],
                "complexity": estimate["complexity_factor"]
            }
        
        # Overall recommendations
        timeouts = [rec["timeout"] for rec in recommendations.values()]
        
        return {
            "text_length": text_length,
            "profiles": recommendations,
            "min_timeout": min(timeouts),
            "max_timeout": max(timeouts),
            "average_timeout": sum(timeouts) // len(timeouts),
            "recommended_buffer": 20  # 20% buffer recommended
        }


# Utility functions
def calculate_timeout(text_length: int, profile_id: Optional[str] = None, config: Optional[Config] = None) -> int:
    """Utility function to calculate timeout"""
    calculator = TimeoutCalculator(config)
    return calculator.calculate_timeout(text_length, profile_id)


def calculate_timeout_with_buffer(text_length: int, profile_id: Optional[str] = None, buffer_percent: int = 20, config: Optional[Config] = None) -> int:
    """Utility function to calculate timeout with buffer"""
    calculator = TimeoutCalculator(config)
    return calculator.calculate_timeout_with_buffer(text_length, profile_id, buffer_percent)


def get_timeout_for_text(text: str, profile_id: Optional[str] = None, config: Optional[Config] = None) -> int:
    """Get timeout for a text string"""
    return calculate_timeout(len(text), profile_id, config)


def validate_timeout(timeout: int) -> bool:
    """Validate if a timeout value is reasonable"""
    return 10 <= timeout <= 300


def get_timeout_category(timeout: int) -> str:
    """Categorize timeout duration"""
    if timeout < 30:
        return "fast"
    elif timeout < 60:
        return "normal"
    elif timeout < 120:
        return "slow"
    else:
        return "very_slow"


def format_timeout_duration(timeout: int) -> str:
    """Format timeout duration for display"""
    if timeout < 60:
        return f"{timeout} segundos"
    else:
        minutes = timeout // 60
        seconds = timeout % 60
        if seconds == 0:
            return f"{minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minuto{'s' if minutes != 1 else ''} y {seconds} segundo{'s' if seconds != 1 else ''}"


# Global calculator instance
_timeout_calculator: Optional[TimeoutCalculator] = None


def get_timeout_calculator(config: Optional[Config] = None) -> TimeoutCalculator:
    """Get or create the global timeout calculator instance"""
    global _timeout_calculator
    
    if _timeout_calculator is None:
        _timeout_calculator = TimeoutCalculator(config)
    
    return _timeout_calculator


def reset_timeout_calculator():
    """Reset the global timeout calculator instance"""
    global _timeout_calculator
    _timeout_calculator = None
