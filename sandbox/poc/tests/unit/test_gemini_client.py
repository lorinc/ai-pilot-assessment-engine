"""Unit tests for GeminiClient."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.gemini_client import GeminiClient
from utils.technical_logger import TechnicalLogger


class TestGeminiClient:
    """Test suite for GeminiClient."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock(spec=TechnicalLogger)
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch('core.gemini_client.settings') as mock:
            mock.GCP_PROJECT_ID = "test-project"
            mock.GCP_LOCATION = "us-central1"
            mock.GEMINI_MODEL = "gemini-pro"
            mock.MOCK_LLM = True  # Use mock mode by default
            yield mock
    
    def test_init_mock_mode(self, mock_settings, mock_logger):
        """Test initialization in mock mode."""
        client = GeminiClient(logger=mock_logger)
        
        assert client.project_id == "test-project"
        assert client.location == "us-central1"
        assert client.model_name == "gemini-pro"
        assert client.model is None
        mock_logger.warning.assert_called_once()
    
    def test_init_with_custom_params(self, mock_settings, mock_logger):
        """Test initialization with custom parameters."""
        client = GeminiClient(
            project_id="custom-project",
            location="europe-west1",
            model_name="gemini-flash",
            logger=mock_logger
        )
        
        assert client.project_id == "custom-project"
        assert client.location == "europe-west1"
        assert client.model_name == "gemini-flash"
    
    @patch('core.gemini_client.vertexai')
    @patch('core.gemini_client.GenerativeModel')
    def test_init_real_mode(self, mock_model_class, mock_vertexai, mock_settings, mock_logger):
        """Test initialization in real mode."""
        mock_settings.MOCK_LLM = False
        mock_model_instance = Mock()
        mock_model_class.return_value = mock_model_instance
        
        client = GeminiClient(logger=mock_logger)
        
        mock_vertexai.init.assert_called_once_with(
            project="test-project",
            location="us-central1"
        )
        mock_model_class.assert_called_once_with("gemini-pro")
        assert client.model == mock_model_instance
        mock_logger.info.assert_called_once()
    
    def test_generate_mock_mode(self, mock_settings, mock_logger):
        """Test generate in mock mode."""
        client = GeminiClient(logger=mock_logger)
        
        response = client.generate("Test prompt")
        
        assert isinstance(response, str)
        assert "mock response" in response.lower()
        assert mock_logger.info.call_count == 2  # llm_call and llm_response
    
    def test_generate_with_params(self, mock_settings, mock_logger):
        """Test generate with custom parameters."""
        client = GeminiClient(logger=mock_logger)
        
        response = client.generate(
            "Test prompt",
            temperature=0.5,
            max_output_tokens=1024
        )
        
        assert isinstance(response, str)
        # Verify logger was called with correct params
        call_args = mock_logger.info.call_args_list[0]
        assert call_args[0][0] == "llm_call"
        assert call_args[0][2]["temperature"] == 0.5
        assert call_args[0][2]["max_tokens"] == 1024
    
    @patch('core.gemini_client.GenerationConfig')
    @patch('core.gemini_client.vertexai')
    @patch('core.gemini_client.GenerativeModel')
    def test_generate_real_mode(self, mock_model_class, mock_vertexai, mock_gen_config, mock_settings, mock_logger):
        """Test generate in real mode."""
        mock_settings.MOCK_LLM = False
        
        # Setup mocks
        mock_model_instance = Mock()
        mock_response = Mock()
        mock_response.text = "Real response from Gemini"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance
        
        client = GeminiClient(logger=mock_logger)
        response = client.generate("Test prompt", temperature=0.7)
        
        assert response == "Real response from Gemini"
        mock_model_instance.generate_content.assert_called_once()
        mock_gen_config.assert_called_once()
    
    def test_generate_stream_mock_mode(self, mock_settings, mock_logger):
        """Test generate_stream in mock mode."""
        client = GeminiClient(logger=mock_logger)
        
        chunks = list(client.generate_stream("Test prompt"))
        
        assert len(chunks) == 1
        assert isinstance(chunks[0], str)
        assert "mock response" in chunks[0].lower()
    
    @patch('core.gemini_client.GenerationConfig')
    @patch('core.gemini_client.vertexai')
    @patch('core.gemini_client.GenerativeModel')
    def test_generate_stream_real_mode(self, mock_model_class, mock_vertexai, mock_gen_config, mock_settings, mock_logger):
        """Test generate_stream in real mode."""
        mock_settings.MOCK_LLM = False
        
        # Setup mocks
        mock_model_instance = Mock()
        mock_chunk1 = Mock()
        mock_chunk1.text = "Chunk 1 "
        mock_chunk2 = Mock()
        mock_chunk2.text = "Chunk 2"
        mock_model_instance.generate_content.return_value = [mock_chunk1, mock_chunk2]
        mock_model_class.return_value = mock_model_instance
        
        client = GeminiClient(logger=mock_logger)
        chunks = list(client.generate_stream("Test prompt"))
        
        assert len(chunks) == 2
        assert chunks[0] == "Chunk 1 "
        assert chunks[1] == "Chunk 2"
        mock_model_instance.generate_content.assert_called_once()
    
    def test_build_prompt_minimal(self, mock_settings):
        """Test build_prompt with only user message."""
        client = GeminiClient()
        
        prompt = client.build_prompt("Hello")
        
        assert "# Current User Message" in prompt
        assert "Hello" in prompt
    
    def test_build_prompt_with_context(self, mock_settings):
        """Test build_prompt with system context."""
        client = GeminiClient()
        
        context = {
            "phase": "discovery",
            "available_functions": ["Sales", "Finance"]
        }
        
        prompt = client.build_prompt("Hello", system_context=context)
        
        assert "# System Context" in prompt
        assert "phase" in prompt
        assert "discovery" in prompt
        assert "available_functions" in prompt
        assert "# Current User Message" in prompt
        assert "Hello" in prompt
    
    def test_build_prompt_with_history(self, mock_settings):
        """Test build_prompt with conversation history."""
        client = GeminiClient()
        
        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"}
        ]
        
        prompt = client.build_prompt("Second message", conversation_history=history)
        
        assert "# Conversation History" in prompt
        assert "First message" in prompt
        assert "First response" in prompt
        assert "# Current User Message" in prompt
        assert "Second message" in prompt
    
    def test_build_prompt_complete(self, mock_settings):
        """Test build_prompt with all parameters."""
        client = GeminiClient()
        
        context = {"phase": "assessment"}
        history = [{"role": "user", "content": "Previous"}]
        
        prompt = client.build_prompt(
            "Current message",
            system_context=context,
            conversation_history=history
        )
        
        assert "# System Context" in prompt
        assert "# Conversation History" in prompt
        assert "# Current User Message" in prompt
        assert "assessment" in prompt
        assert "Previous" in prompt
        assert "Current message" in prompt
    
    def test_mock_generate(self, mock_settings):
        """Test _mock_generate method."""
        client = GeminiClient()
        
        response = client._mock_generate("Any prompt")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_without_logger(self, mock_settings):
        """Test generate works without logger."""
        client = GeminiClient(logger=None)
        
        response = client.generate("Test")
        
        assert isinstance(response, str)
    
    def test_generate_stream_without_logger(self, mock_settings):
        """Test generate_stream works without logger."""
        client = GeminiClient(logger=None)
        
        chunks = list(client.generate_stream("Test"))
        
        assert len(chunks) > 0
