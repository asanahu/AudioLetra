"""
Módulo de configuración para el dictado inteligente con Whisper.
Carga y valida la configuración desde archivos .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any


class Config:
    """Clase para manejar la configuración del sistema"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Inicializa la configuración"""
        self.config_file = config_file or ".env"
        self._load_config()
    
    def _load_config(self):
        """Carga la configuración desde el archivo .env"""
        # Buscar archivo .env en el directorio actual
        env_path = Path(self.config_file)
        
        if not env_path.exists():
            # Si no existe, usar la plantilla
            template_path = Path("config/config_template.env")
            if template_path.exists():
                print(f"⚠️  Archivo {self.config_file} no encontrado. Usando configuración por defecto.")
                print(f"💡 Copia config/config_template.env a {self.config_file} para personalizar.")
                load_dotenv(template_path)
            else:
                print("❌ No se encontró archivo de configuración.")
                self._set_defaults()
        else:
            load_dotenv(env_path)
        
        self._validate_config()
    
    def _set_defaults(self):
        """Establece valores por defecto si no hay configuración"""
        defaults = {
            "WHISPER_MODEL": "base",
            "WHISPER_LANGUAGE": "es",
            "WHISPER_USE_GPU": "true",
            "VAD_SENSITIVITY": "2",
            "VAD_SILENCE_DURATION": "1.0",
            "VAD_MIN_SPEECH_DURATION": "0.5",
            "LLM_ENABLED": "false",
            "OPENAI_MODEL": "gpt-4o-mini",
            "SAMPLE_RATE": "16000",
            "CHUNK_SIZE": "1024",
            "CHANNELS": "1",
            "OUTPUT_DIR": "output",
            "OUTPUT_FORMAT": "txt",
            "INCLUDE_TIMESTAMP": "true",
            "REALTIME_DISPLAY": "true",
            "DEBUG_MODE": "false",
            "USE_COLORS": "true"
        }
        
        for key, value in defaults.items():
            os.environ[key] = value
    
    def _validate_config(self):
        """Valida la configuración cargada"""
        # Validar modelo de Whisper
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if self.whisper_model not in valid_models:
            print(f"⚠️  Modelo de Whisper inválido: {self.whisper_model}")
            print(f"💡 Usando 'base' por defecto. Modelos válidos: {valid_models}")
            os.environ["WHISPER_MODEL"] = "base"
        
        # Validar idioma
        valid_languages = ["es", "en", "auto"]
        if self.whisper_language not in valid_languages:
            print(f"⚠️  Idioma inválido: {self.whisper_language}")
            print(f"💡 Usando 'es' por defecto. Idiomas válidos: {valid_languages}")
            os.environ["WHISPER_LANGUAGE"] = "es"
        
        # Validar sensibilidad VAD
        try:
            sensitivity = int(self.vad_sensitivity)
            if not 0 <= sensitivity <= 3:
                print(f"⚠️  Sensibilidad VAD inválida: {sensitivity}")
                print("💡 Usando 2 por defecto. Rango válido: 0-3")
                os.environ["VAD_SENSITIVITY"] = "2"
        except ValueError:
            print("⚠️  Sensibilidad VAD debe ser un número")
            os.environ["VAD_SENSITIVITY"] = "2"
    
    @property
    def whisper_model(self) -> str:
        return os.getenv("WHISPER_MODEL", "base")
    
    @property
    def whisper_language(self) -> str:
        return os.getenv("WHISPER_LANGUAGE", "es")
    
    @property
    def whisper_use_gpu(self) -> bool:
        return os.getenv("WHISPER_USE_GPU", "true").lower() == "true"
    
    @property
    def vad_sensitivity(self) -> int:
        return int(os.getenv("VAD_SENSITIVITY", "2"))
    
    @property
    def vad_silence_duration(self) -> float:
        return float(os.getenv("VAD_SILENCE_DURATION", "1.0"))
    
    @property
    def vad_min_speech_duration(self) -> float:
        return float(os.getenv("VAD_MIN_SPEECH_DURATION", "0.5"))
    
    @property
    def llm_enabled(self) -> bool:
        return os.getenv("LLM_ENABLED", "false").lower() == "true"
    
    @property
    def openai_api_key(self) -> Optional[str]:
        key = os.getenv("OPENAI_API_KEY")
        return key if key and key.strip() else None
    
    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
    
    @property
    def llm_provider(self) -> str:
        return os.getenv("LLM_PROVIDER", "openrouter")
    
    @property
    def llm_base_url(self) -> Optional[str]:
        url = os.getenv("LLM_BASE_URL")
        return url if url and url.strip() else None
    
    @property
    def sample_rate(self) -> int:
        return int(os.getenv("SAMPLE_RATE", "16000"))
    
    @property
    def chunk_size(self) -> int:
        return int(os.getenv("CHUNK_SIZE", "1024"))
    
    @property
    def channels(self) -> int:
        return int(os.getenv("CHANNELS", "1"))
    
    @property
    def audio_input_device(self) -> Optional[str]:
        device = os.getenv("AUDIO_INPUT_DEVICE")
        return device if device and device.strip() else None
    
    @property
    def output_dir(self) -> str:
        return os.getenv("OUTPUT_DIR", "data/transcriptions")
    
    @property
    def output_format(self) -> str:
        return os.getenv("OUTPUT_FORMAT", "txt")
    
    @property
    def include_timestamp(self) -> bool:
        return os.getenv("INCLUDE_TIMESTAMP", "true").lower() == "true"
    
    @property
    def realtime_display(self) -> bool:
        return os.getenv("REALTIME_DISPLAY", "true").lower() == "true"
    
    @property
    def debug_mode(self) -> bool:
        return os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    @property
    def use_colors(self) -> bool:
        return os.getenv("USE_COLORS", "true").lower() == "true"
    
    @property
    def llm_prompt_cleanup(self) -> str:
        return os.getenv("LLM_PROMPT_CLEANUP", 
                        "Mejora la puntuación y formato de este texto transcrito, manteniendo el contenido original:")
    
    @property
    def llm_prompt_summary(self) -> str:
        return os.getenv("LLM_PROMPT_SUMMARY", "Crea un resumen conciso de este texto:")
    
    @property
    def llm_prompt_tasks(self) -> str:
        return os.getenv("LLM_PROMPT_TASKS", "Extrae las tareas y puntos importantes de este texto en formato de lista:")
    
    @property
    def llm_prompt_email(self) -> str:
        return os.getenv("LLM_PROMPT_EMAIL", "Formatea este texto como un email profesional:")
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Retorna configuración de audio como diccionario"""
        return {
            "sample_rate": self.sample_rate,
            "chunk_size": self.chunk_size,
            "channels": self.channels,
            "input_device": self.audio_input_device
        }
    
    def get_whisper_config(self) -> Dict[str, Any]:
        """Retorna configuración de Whisper como diccionario"""
        return {
            "model": self.whisper_model,
            "language": self.whisper_language,
            "use_gpu": self.whisper_use_gpu
        }
    
    def get_vad_config(self) -> Dict[str, Any]:
        """Retorna configuración de VAD como diccionario"""
        return {
            "sensitivity": self.vad_sensitivity,
            "silence_duration": self.vad_silence_duration,
            "min_speech_duration": self.vad_min_speech_duration
        }
    
    def print_config(self):
        """Imprime la configuración actual"""
        print("🔧 Configuración actual:")
        print(f"   Modelo Whisper: {self.whisper_model}")
        print(f"   Idioma: {self.whisper_language}")
        print(f"   Usar GPU: {self.whisper_use_gpu}")
        print(f"   Sensibilidad VAD: {self.vad_sensitivity}")
        print(f"   LLM habilitado: {self.llm_enabled}")
        print(f"   Directorio salida: {self.output_dir}")
        print(f"   Formato salida: {self.output_format}")
        if self.debug_mode:
            print(f"   Modo debug: {self.debug_mode}")


# Instancia global de configuración
config = Config()
