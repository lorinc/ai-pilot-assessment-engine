"""Unit tests for LLM client."""

import pytest
from unittest.mock import Mock, patch

from src.core.llm_client import LLMClient
from src.utils.logger import TechnicalLogger


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return TechnicalLogger(max_entries=10)


@pytest.fixture
def mock_llm_client(mock_logger):
    """Create LLM client in mock mode."""
    with patch('src.config.settings.settings.MOCK_LLM', True):
        return LLMClient(logger=mock_logger)


class TestLLMClient:
    """Test LLMClient class."""
    
    def test_init_mock_mode(self, mock_llm_client, mock_logger):
        """Test initialization in mock mode."""
        assert mock_llm_client.logger == mock_logger
        assert mock_llm_client.model is None
    
    def test_generate_mock(self, mock_llm_client):
        """Test non-streaming generation in mock mode."""
        response = mock_llm_client.generate("Test prompt")
        assert isinstance(response, str)
        assert "mock response" in response.lower()
    
    def test_generate_stream_mock(self, mock_llm_client):
        """Test streaming generation in mock mode."""
        chunks = list(mock_llm_client.generate_stream("Test prompt"))
        assert len(chunks) == 1
        assert isinstance(chunks[0], str)
        assert "mock response" in chunks[0].lower()
    
    def test_build_prompt_simple(self, mock_llm_client):
        """Test prompt building with just user message."""
        prompt = mock_llm_client.build_prompt("Hello")
        assert "Hello" in prompt
        assert "Current User Message" in prompt
    
    def test_build_prompt_with_history(self, mock_llm_client):
        """Test prompt building with conversation history."""
        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"}
        ]
        prompt = mock_llm_client.build_prompt("Second message", conversation_history=history)
        assert "First message" in prompt
        assert "First response" in prompt
        assert "Second message" in prompt
        assert "Conversation History" in prompt
    
    def test_build_prompt_with_context(self, mock_llm_client):
        """Test prompt building with system context."""
        context = {"key1": "value1", "key2": "value2"}
        prompt = mock_llm_client.build_prompt("Message", system_context=context)
        assert "System Context" in prompt
        assert "value1" in prompt
        assert "value2" in prompt
    
    def test_generate_with_params(self, mock_llm_client):
        """Test generation with custom parameters."""
        response = mock_llm_client.generate(
            "Test",
            temperature=0.5,
            max_output_tokens=1024
        )
        assert isinstance(response, str)


@pytest.mark.skipif(
    True,  # Skip real LLM tests by default
    reason="Requires GCP credentials and costs money"
)
class TestLLMClientReal:
    """Test LLMClient with real Gemini (requires credentials)."""
    
    @pytest.fixture
    def real_llm_client(self, mock_logger):
        """Create real LLM client."""
        with patch('src.config.settings.settings.MOCK_LLM', False):
            return LLMClient(logger=mock_logger)
    
    def test_generate_real(self, real_llm_client):
        """Test real generation."""
        # This would make actual API calls
        pass
