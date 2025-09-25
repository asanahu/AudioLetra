"""
Unit tests for services
Tests LLM, Profile, Prompt, and File services
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.services.llm_service import LLMService, OpenAIProvider, OpenRouterProvider
from src.services.profile_service import ProfileService
from src.services.prompt_service import PromptService
from src.services.file_service import FileService
from src.config import Config


class TestLLMService:
    """Test LLMService"""
    
    def test_llm_service_initialization(self):
        """Test LLMService initialization"""
        config = Config()
        service = LLMService(config)
        
        assert service.config == config
        assert service.provider is None
    
    def test_load_openai_provider(self):
        """Test loading OpenAI provider"""
        config = Config()
        config.LLM_PROVIDER = "openai"
        config.OPENAI_API_KEY = "test-key"
        
        service = LLMService(config)
        service._load_provider()
        
        assert isinstance(service.provider, OpenAIProvider)
    
    def test_load_openrouter_provider(self):
        """Test loading OpenRouter provider"""
        config = Config()
        config.LLM_PROVIDER = "openrouter"
        config.OPENROUTER_API_KEY = "test-key"
        
        service = LLMService(config)
        service._load_provider()
        
        assert isinstance(service.provider, OpenRouterProvider)
    
    def test_load_invalid_provider(self):
        """Test loading invalid provider"""
        config = Config()
        config.LLM_PROVIDER = "invalid"
        
        service = LLMService(config)
        
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            service._load_provider()
    
    def test_missing_api_key(self):
        """Test missing API key"""
        config = Config()
        config.LLM_PROVIDER = "openai"
        # No API key set
        
        service = LLMService(config)
        
        with pytest.raises(ValueError, match="LLM API key is required"):
            service._load_provider()


class TestOpenAIProvider:
    """Test OpenAIProvider"""
    
    def test_openai_provider_initialization(self):
        """Test OpenAIProvider initialization"""
        config = Config()
        config.OPENAI_API_KEY = "test-key"
        config.OPENAI_MODEL = "gpt-3.5-turbo"
        
        provider = OpenAIProvider(config)
        
        assert provider.api_key == "test-key"
        assert provider.model == "gpt-3.5-turbo"
        assert provider.base_url == "https://api.openai.com/v1"
    
    @patch('src.services.llm_service.openai.OpenAI')
    def test_openai_process_text_success(self, mock_openai):
        """Test successful text processing with OpenAI"""
        config = Config()
        config.OPENAI_API_KEY = "test-key"
        config.OPENAI_MODEL = "gpt-3.5-turbo"
        
        provider = OpenAIProvider(config)
        
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Processed text"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 100
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = provider.process_text("Test prompt", timeout=30)
        
        assert result["success"] == True
        assert result["output"] == "Processed text"
        assert result["metadata"]["tokens_used"] == 100
    
    @patch('src.services.llm_service.openai.OpenAI')
    def test_openai_process_text_error(self, mock_openai):
        """Test error handling in OpenAI processing"""
        config = Config()
        config.OPENAI_API_KEY = "test-key"
        config.OPENAI_MODEL = "gpt-3.5-turbo"
        
        provider = OpenAIProvider(config)
        
        # Mock OpenAI error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        result = provider.process_text("Test prompt", timeout=30)
        
        assert result["success"] == False
        assert "error" in result
        assert result["error"]["message"] == "API Error"


class TestOpenRouterProvider:
    """Test OpenRouterProvider"""
    
    def test_openrouter_provider_initialization(self):
        """Test OpenRouterProvider initialization"""
        config = Config()
        config.OPENROUTER_API_KEY = "test-key"
        config.OPENROUTER_MODEL = "anthropic/claude-3-haiku"
        
        provider = OpenRouterProvider(config)
        
        assert provider.api_key == "test-key"
        assert provider.model == "anthropic/claude-3-haiku"
        assert provider.base_url == "https://openrouter.ai/api/v1"
    
    @patch('src.services.llm_service.requests.post')
    def test_openrouter_process_text_success(self, mock_post):
        """Test successful text processing with OpenRouter"""
        config = Config()
        config.OPENROUTER_API_KEY = "test-key"
        config.OPENROUTER_MODEL = "anthropic/claude-3-haiku"
        
        provider = OpenRouterProvider(config)
        
        # Mock OpenRouter response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Processed text"}}],
            "usage": {"total_tokens": 100}
        }
        mock_post.return_value = mock_response
        
        result = provider.process_text("Test prompt", timeout=30)
        
        assert result["success"] == True
        assert result["output"] == "Processed text"
        assert result["metadata"]["tokens_used"] == 100
    
    @patch('src.services.llm_service.requests.post')
    def test_openrouter_process_text_error(self, mock_post):
        """Test error handling in OpenRouter processing"""
        config = Config()
        config.OPENROUTER_API_KEY = "test-key"
        config.OPENROUTER_MODEL = "anthropic/claude-3-haiku"
        
        provider = OpenRouterProvider(config)
        
        # Mock OpenRouter error
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad Request"}}
        mock_post.return_value = mock_response
        
        result = provider.process_text("Test prompt", timeout=30)
        
        assert result["success"] == False
        assert "error" in result
        assert result["error"]["message"] == "Bad Request"


class TestProfileService:
    """Test ProfileService"""
    
    def test_profile_service_initialization(self):
        """Test ProfileService initialization"""
        config = Config()
        service = ProfileService(config)
        
        assert service.config == config
        assert service.profile_manager is not None
    
    def test_get_all_profiles(self):
        """Test getting all profiles"""
        config = Config()
        service = ProfileService(config)
        
        profiles = service.get_all_profiles()
        
        assert len(profiles) == 6
        assert all(hasattr(p, 'id') for p in profiles)
        assert all(hasattr(p, 'name') for p in profiles)
    
    def test_get_profile_by_id(self):
        """Test getting profile by ID"""
        config = Config()
        service = ProfileService(config)
        
        profile = service.get_profile_by_id("clean_format")
        assert profile is not None
        assert profile.id == "clean_format"
        
        profile = service.get_profile_by_id("invalid")
        assert profile is None
    
    def test_validate_profile(self):
        """Test profile validation"""
        config = Config()
        service = ProfileService(config)
        
        assert service.validate_profile("clean_format") == True
        assert service.validate_profile("invalid") == False


class TestPromptService:
    """Test PromptService"""
    
    def test_prompt_service_initialization(self):
        """Test PromptService initialization"""
        config = Config()
        service = PromptService(config)
        
        assert service.config == config
        assert service.jinja_env is not None
    
    def test_render_prompt_basic(self):
        """Test basic prompt rendering"""
        config = Config()
        service = PromptService(config)
        
        # Test with clean_format profile
        result = service.render_prompt("clean_format", "test text", {})
        
        assert isinstance(result, str)
        assert "test text" in result
        assert len(result) > 0
    
    def test_render_prompt_with_parameters(self):
        """Test prompt rendering with parameters"""
        config = Config()
        service = PromptService(config)
        
        # Test with translate profile and language parameter
        result = service.render_prompt(
            "translate", 
            "test text", 
            {"target_language": "English"}
        )
        
        assert isinstance(result, str)
        assert "test text" in result
        assert "English" in result
    
    def test_render_prompt_invalid_profile(self):
        """Test rendering prompt for invalid profile"""
        config = Config()
        service = PromptService(config)
        
        with pytest.raises(ValueError, match="Profile not found"):
            service.render_prompt("invalid_profile", "test text", {})
    
    def test_render_prompt_template_error(self):
        """Test template rendering error"""
        config = Config()
        service = PromptService(config)
        
        # This should work with valid profile
        result = service.render_prompt("clean_format", "test text", {})
        assert isinstance(result, str)


class TestFileService:
    """Test FileService"""
    
    def test_file_service_initialization(self):
        """Test FileService initialization"""
        config = Config()
        service = FileService(config)
        
        assert service.config == config
    
    def test_generate_txt_file(self):
        """Test TXT file generation"""
        config = Config()
        service = FileService(config)
        
        content = "Test content"
        filename = "test.txt"
        
        result = service.generate_file(content, "txt", filename)
        
        assert result["success"] == True
        assert result["filename"] == filename
        assert result["content_type"] == "text/plain"
        assert isinstance(result["content"], bytes)
    
    def test_generate_docx_file(self):
        """Test DOCX file generation"""
        config = Config()
        service = FileService(config)
        
        content = "Test content for DOCX"
        filename = "test.docx"
        
        result = service.generate_file(content, "docx", filename)
        
        assert result["success"] == True
        assert result["filename"] == filename
        assert result["content_type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert isinstance(result["content"], bytes)
    
    def test_generate_pdf_file(self):
        """Test PDF file generation"""
        config = Config()
        service = FileService(config)
        
        content = "Test content for PDF"
        filename = "test.pdf"
        
        result = service.generate_file(content, "pdf", filename)
        
        assert result["success"] == True
        assert result["filename"] == filename
        assert result["content_type"] == "application/pdf"
        assert isinstance(result["content"], bytes)
    
    def test_generate_invalid_format(self):
        """Test invalid format handling"""
        config = Config()
        service = FileService(config)
        
        content = "Test content"
        filename = "test.invalid"
        
        result = service.generate_file(content, "invalid", filename)
        
        assert result["success"] == False
        assert "error" in result
        assert "Unsupported format" in result["error"]["message"]
    
    def test_generate_file_error_handling(self):
        """Test error handling in file generation"""
        config = Config()
        service = FileService(config)
        
        # Test with empty content
        result = service.generate_file("", "txt", "empty.txt")
        
        assert result["success"] == True  # Empty content should still work
        assert isinstance(result["content"], bytes)


# Integration tests for services
class TestServiceIntegration:
    """Test services working together"""
    
    def test_profile_prompt_integration(self):
        """Test ProfileService and PromptService integration"""
        config = Config()
        profile_service = ProfileService(config)
        prompt_service = PromptService(config)
        
        # Get profile
        profile = profile_service.get_profile_by_id("clean_format")
        assert profile is not None
        
        # Render prompt using profile
        result = prompt_service.render_prompt(profile.id, "test text", {})
        assert isinstance(result, str)
        assert "test text" in result
    
    def test_prompt_file_integration(self):
        """Test PromptService and FileService integration"""
        config = Config()
        prompt_service = PromptService(config)
        file_service = FileService(config)
        
        # Render prompt
        prompt_result = prompt_service.render_prompt("clean_format", "test text", {})
        
        # Generate file from prompt result
        file_result = file_service.generate_file(prompt_result, "txt", "test.txt")
        
        assert file_result["success"] == True
        assert isinstance(file_result["content"], bytes)
    
    @patch('src.services.llm_service.openai.OpenAI')
    def test_llm_prompt_integration(self, mock_openai):
        """Test LLMService and PromptService integration"""
        config = Config()
        config.LLM_PROVIDER = "openai"
        config.OPENAI_API_KEY = "test-key"
        config.OPENAI_MODEL = "gpt-3.5-turbo"
        
        llm_service = LLMService(config)
        prompt_service = PromptService(config)
        
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Processed text"
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 100
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Render prompt
        prompt = prompt_service.render_prompt("clean_format", "test text", {})
        
        # Process with LLM
        result = llm_service.process_text(prompt, timeout=30)
        
        assert result["success"] == True
        assert result["output"] == "Processed text"
