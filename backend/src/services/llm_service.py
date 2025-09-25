"""
LLM service abstraction for OpenAI/OpenRouter integration
Provides a unified interface for different LLM providers
"""
import os
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import requests
import json
from src.config import Config


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def process_text(self, prompt: str, model: str = None, timeout: int = 30) -> Dict[str, Any]:
        """Process text using the LLM provider"""
        pass
    
    @abstractmethod
    def get_models(self) -> list[str]:
        """Get available models"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def process_text(self, prompt: str, model: str = None, timeout: int = 30) -> Dict[str, Any]:
        """Process text using OpenAI API"""
        if model is None:
            model = "gpt-3.5-turbo"
        
        start_time = time.time()
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "output": data["choices"][0]["message"]["content"],
                "metadata": {
                    "processing_time": processing_time,
                    "model_used": model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "provider": "openai"
                }
            }
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"OpenAI request timed out after {timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenAI API error: {str(e)}")
        except KeyError as e:
            raise Exception(f"Invalid OpenAI response format: {str(e)}")
    
    def get_models(self) -> list[str]:
        """Get available OpenAI models"""
        return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]


class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider"""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "AudioLetra"
        }
    
    def process_text(self, prompt: str, model: str = None, timeout: int = 30) -> Dict[str, Any]:
        """Process text using OpenRouter API"""
        if model is None:
            model = "anthropic/claude-3-haiku"
        
        start_time = time.time()
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "output": data["choices"][0]["message"]["content"],
                "metadata": {
                    "processing_time": processing_time,
                    "model_used": model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "provider": "openrouter"
                }
            }
            
        except requests.exceptions.Timeout:
            raise TimeoutError(f"OpenRouter request timed out after {timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API error: {str(e)}")
        except KeyError as e:
            raise Exception(f"Invalid OpenRouter response format: {str(e)}")
    
    def get_models(self) -> list[str]:
        """Get available OpenRouter models"""
        return ["anthropic/claude-3-haiku", "openai/gpt-3.5-turbo", "meta-llama/llama-2-70b-chat"]


class LLMService:
    """Main LLM service that manages different providers"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self) -> LLMProvider:
        """Initialize the appropriate LLM provider"""
        provider_type = self.config.LLM_PROVIDER.lower()
        api_key = self.config.OPENAI_API_KEY
        
        if not api_key:
            raise ValueError("LLM API key is required")
        
        if provider_type == "openai":
            return OpenAIProvider(api_key, self.config.LLM_BASE_URL)
        elif provider_type == "openrouter":
            return OpenRouterProvider(api_key, self.config.LLM_BASE_URL)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_type}")
    
    def process_text(self, prompt: str, timeout: int = 30) -> Dict[str, Any]:
        """Process text using the configured LLM provider"""
        try:
            model = self.config.OPENAI_MODEL
            return self.provider.process_text(prompt, model, timeout)
        except TimeoutError:
            raise
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "LLM_ERROR",
                    "message": f"LLM processing failed: {str(e)}",
                    "details": {"provider": self.config.LLM_PROVIDER}
                }
            }
    
    def get_available_models(self) -> list[str]:
        """Get available models from the current provider"""
        return self.provider.get_models()
    
    def test_connection(self) -> bool:
        """Test connection to the LLM provider"""
        try:
            result = self.process_text("Test connection", timeout=10)
            return result.get("success", False)
        except Exception:
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        return {
            "provider": self.config.LLM_PROVIDER,
            "base_url": self.config.LLM_BASE_URL,
            "model": self.config.OPENAI_MODEL,
            "available_models": self.get_available_models()
        }


# Global service instance
_llm_service: Optional[LLMService] = None


def get_llm_service(config: Optional[Config] = None) -> LLMService:
    """Get or create the global LLM service instance"""
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMService(config)
    
    return _llm_service


def reset_llm_service():
    """Reset the global LLM service instance"""
    global _llm_service
    _llm_service = None
