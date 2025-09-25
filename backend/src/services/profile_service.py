"""
Profile service for managing LLM processing profiles
Handles profile retrieval, validation, and management
"""
from typing import List, Dict, Any, Optional
from src.models.profile import Profile, ProfileManager
from src.config import Config


class ProfileService:
    """Service for managing processing profiles"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.profile_manager = ProfileManager()
    
    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Get all available profiles for API response"""
        profiles = self.profile_manager.get_all_profiles()
        return [profile.to_dict() for profile in profiles]
    
    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """Get a specific profile by ID"""
        try:
            return self.profile_manager.get_profile(profile_id)
        except ValueError:
            return None
    
    def get_profile_dict(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific profile as dictionary"""
        profile = self.get_profile(profile_id)
        return profile.to_dict() if profile else None
    
    def validate_profile_exists(self, profile_id: str) -> bool:
        """Check if a profile exists"""
        return self.get_profile(profile_id) is not None
    
    def validate_profile_parameters(self, profile_id: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate parameters for a specific profile"""
        profile = self.get_profile(profile_id)
        if not profile:
            return False, f"Profile '{profile_id}' not found"
        
        # Special validation for translate profile
        if profile_id == "translate":
            if "target_language" not in parameters:
                return False, "Parameter 'target_language' is required for translate profile"
            
            target_lang = parameters["target_language"]
            supported_languages = profile.parameters.get("supported_languages", [])
            
            if target_lang not in supported_languages:
                return False, f"Language '{target_lang}' not supported. Supported languages: {', '.join(supported_languages)}"
        
        return True, None
    
    def get_profile_timeout_multiplier(self, profile_id: str) -> float:
        """Get timeout multiplier for a specific profile"""
        profile = self.get_profile(profile_id)
        return profile.timeout_multiplier if profile else 1.0
    
    def get_profile_template(self, profile_id: str) -> Optional[str]:
        """Get prompt template for a specific profile"""
        profile = self.get_profile(profile_id)
        return profile.prompt_template if profile else None
    
    def get_supported_languages(self, profile_id: str) -> List[str]:
        """Get supported languages for a profile (mainly for translate)"""
        profile = self.get_profile(profile_id)
        if profile and profile_id == "translate":
            return profile.parameters.get("supported_languages", [])
        return []
    
    def get_profile_statistics(self) -> Dict[str, Any]:
        """Get statistics about available profiles"""
        profiles = self.profile_manager.get_all_profiles()
        
        stats = {
            "total_profiles": len(profiles),
            "predefined_profiles": 6,
            "custom_profiles": len(profiles) - 6,
            "profiles_by_category": {
                "formatting": ["clean_format", "format_email"],
                "analysis": ["summarize", "extract_tasks", "meeting_minutes"],
                "translation": ["translate"]
            }
        }
        
        return stats
    
    def search_profiles(self, query: str) -> List[Dict[str, Any]]:
        """Search profiles by name or description"""
        query = query.lower().strip()
        if not query:
            return self.get_all_profiles()
        
        matching_profiles = []
        profiles = self.profile_manager.get_all_profiles()
        
        for profile in profiles:
            if (query in profile.name.lower() or 
                query in profile.description.lower() or
                query in profile.id.lower()):
                matching_profiles.append(profile.to_dict())
        
        return matching_profiles
    
    def get_profile_recommendations(self, text_length: int, text_content: str = "") -> List[str]:
        """Get profile recommendations based on text characteristics"""
        recommendations = []
        
        # Basic recommendations based on text length
        if text_length < 500:
            recommendations.extend(["clean_format", "format_email"])
        elif text_length > 2000:
            recommendations.extend(["summarize", "extract_tasks"])
        else:
            recommendations.extend(["clean_format", "summarize"])
        
        # Content-based recommendations
        text_lower = text_content.lower()
        
        if any(word in text_lower for word in ["reunión", "meeting", "agenda", "acuerdo"]):
            recommendations.insert(0, "meeting_minutes")
        
        if any(word in text_lower for word in ["tarea", "task", "hacer", "implementar"]):
            recommendations.insert(0, "extract_tasks")
        
        if any(word in text_lower for word in ["email", "correo", "mensaje"]):
            recommendations.insert(0, "format_email")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:3]  # Return top 3 recommendations
    
    def add_custom_profile(self, profile_data: Dict[str, Any]) -> tuple[bool, str]:
        """Add a custom profile (for future extensibility)"""
        try:
            profile = Profile.from_dict(profile_data)
            self.profile_manager.add_profile(profile)
            return True, f"Profile '{profile.id}' added successfully"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Failed to add profile: {str(e)}"
    
    def remove_custom_profile(self, profile_id: str) -> tuple[bool, str]:
        """Remove a custom profile (cannot remove predefined profiles)"""
        try:
            self.profile_manager.remove_profile(profile_id)
            return True, f"Profile '{profile_id}' removed successfully"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Failed to remove profile: {str(e)}"


# Global service instance
_profile_service: Optional[ProfileService] = None


def get_profile_service(config: Optional[Config] = None) -> ProfileService:
    """Get or create the global profile service instance"""
    global _profile_service
    
    if _profile_service is None:
        _profile_service = ProfileService(config)
    
    return _profile_service


def reset_profile_service():
    """Reset the global profile service instance"""
    global _profile_service
    _profile_service = None
