"""
Prompt template manager using Jinja2
Handles prompt generation and parameter substitution for different profiles
"""
from typing import Dict, Any, Optional
from jinja2 import Template, Environment, BaseLoader
from src.models.profile import Profile
from src.services.profile_service import get_profile_service
from src.config import Config


class PromptService:
    """Service for managing and rendering prompt templates"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.env = Environment(loader=BaseLoader())
        self.profile_service = get_profile_service(config)
    
    def render_prompt(self, profile_id: str, text: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Render a prompt template with the given text and parameters"""
        if parameters is None:
            parameters = {}
        
        # Get profile template
        profile = self.profile_service.get_profile(profile_id)
        if not profile:
            raise ValueError(f"Profile '{profile_id}' not found")
        
        template_str = profile.prompt_template
        
        # Create template context
        context = {
            'text': text,
            **parameters
        }
        
        # Handle special cases for different profiles
        context = self._prepare_context(profile_id, context)
        
        try:
            template = Template(template_str)
            rendered = template.render(**context)
            return rendered.strip()
        except Exception as e:
            raise ValueError(f"Failed to render template for profile '{profile_id}': {str(e)}")
    
    def _prepare_context(self, profile_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for specific profiles"""
        
        if profile_id == "translate":
            # Map language codes to full names for better prompts
            language_map = {
                "es": "español",
                "en": "inglés", 
                "fr": "francés",
                "de": "alemán"
            }
            
            target_lang = context.get("target_language", "en")
            context["target_language"] = language_map.get(target_lang, target_lang)
        
        elif profile_id == "extract_tasks":
            # Add context for task extraction
            context["task_verbs"] = [
                "Implementar", "Crear", "Desarrollar", "Diseñar", "Configurar",
                "Revisar", "Analizar", "Documentar", "Probar", "Optimizar"
            ]
        
        elif profile_id == "format_email":
            # Add email formatting context
            context["greeting"] = context.get("greeting", "Estimado/a")
            context["closing"] = context.get("closing", "Saludos cordiales")
        
        elif profile_id == "meeting_minutes":
            # Add meeting structure context
            context["sections"] = [
                "Asistentes",
                "Agenda",
                "Puntos Discutidos",
                "Acuerdos",
                "Próximos Pasos"
            ]
        
        return context
    
    def validate_template(self, template_str: str, test_context: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
        """Validate a template string"""
        if test_context is None:
            test_context = {"text": "Sample text for validation"}
        
        try:
            template = Template(template_str)
            template.render(**test_context)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def get_template_variables(self, template_str: str) -> list[str]:
        """Extract variables from a template string"""
        try:
            template = Template(template_str)
            variables = list(template.environment.parse(template_str).find_all('Name'))
            return [var.name for var in variables if var.ctx == 'load']
        except Exception:
            return []
    
    def get_profile_template_info(self, profile_id: str) -> Dict[str, Any]:
        """Get information about a profile's template"""
        profile = self.profile_service.get_profile(profile_id)
        if not profile:
            return {"error": f"Profile '{profile_id}' not found"}
        
        template_str = profile.prompt_template
        variables = self.get_template_variables(template_str)
        is_valid, error = self.validate_template(template_str)
        
        return {
            "profile_id": profile_id,
            "template": template_str,
            "variables": variables,
            "is_valid": is_valid,
            "validation_error": error,
            "required_parameters": self._get_required_parameters(profile_id),
            "optional_parameters": self._get_optional_parameters(profile_id)
        }
    
    def _get_required_parameters(self, profile_id: str) -> list[str]:
        """Get required parameters for a profile"""
        if profile_id == "translate":
            return ["target_language"]
        return []
    
    def _get_optional_parameters(self, profile_id: str) -> list[str]:
        """Get optional parameters for a profile"""
        optional_params = {
            "format_email": ["greeting", "closing", "recipient_name"],
            "meeting_minutes": ["meeting_date", "organizer", "location"],
            "extract_tasks": ["priority_level", "due_date"],
            "summarize": ["summary_length", "focus_area"],
            "clean_format": ["style_preference"]
        }
        
        return optional_params.get(profile_id, [])
    
    def create_sample_prompt(self, profile_id: str) -> Dict[str, Any]:
        """Create a sample prompt for testing purposes"""
        sample_texts = {
            "clean_format": "hola mundo esto es una prueba de texto sin puntuacion ni estructura",
            "summarize": "Este es un texto largo que necesita ser resumido. Contiene mucha información importante sobre el proyecto AudioLetra y sus funcionalidades. El sistema permite procesar audio y convertirlo a texto usando Whisper localmente.",
            "extract_tasks": "En la reunión de hoy discutimos varios puntos. Necesitamos implementar la funcionalidad de perfiles LLM, crear tests de integración, diseñar la interfaz de usuario y documentar la API.",
            "format_email": "Quería informarte sobre el progreso del proyecto. Hemos completado la implementación de los modelos y servicios. Los próximos pasos incluyen la integración con la API y las pruebas.",
            "meeting_minutes": "Reunión del equipo - Asistentes: Juan, María, Carlos. Discutimos el progreso del sprint, decidimos usar pytest para testing, acordamos reunirnos semanalmente.",
            "translate": "Hola mundo, esto es una prueba de traducción del sistema AudioLetra."
        }
        
        sample_text = sample_texts.get(profile_id, "Texto de ejemplo para procesamiento.")
        
        # Default parameters for testing
        sample_params = {}
        if profile_id == "translate":
            sample_params["target_language"] = "en"
        
        try:
            rendered_prompt = self.render_prompt(profile_id, sample_text, sample_params)
            return {
                "profile_id": profile_id,
                "sample_text": sample_text,
                "sample_parameters": sample_params,
                "rendered_prompt": rendered_prompt,
                "success": True
            }
        except Exception as e:
            return {
                "profile_id": profile_id,
                "error": str(e),
                "success": False
            }
    
    def get_all_sample_prompts(self) -> Dict[str, Any]:
        """Get sample prompts for all profiles"""
        profile_ids = self.profile_service.profile_manager.get_profile_ids()
        samples = {}
        
        for profile_id in profile_ids:
            samples[profile_id] = self.create_sample_prompt(profile_id)
        
        return samples


# Global service instance
_prompt_service: Optional[PromptService] = None


def get_prompt_service(config: Optional[Config] = None) -> PromptService:
    """Get or create the global prompt service instance"""
    global _prompt_service
    
    if _prompt_service is None:
        _prompt_service = PromptService(config)
    
    return _prompt_service


def reset_prompt_service():
    """Reset the global prompt service instance"""
    global _prompt_service
    _prompt_service = None
