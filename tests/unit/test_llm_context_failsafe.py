"""Test LLM context size failsafe."""

import pytest
from unittest.mock import Mock

from core.llm_client import LLMClient


class TestLLMContextFailsafe:
    """Test context size validation and failsafe mechanisms."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()
    
    @pytest.fixture
    def llm_client(self, mock_logger):
        """Create LLM client with mock logger."""
        return LLMClient(logger=mock_logger)
    
    def test_normal_prompt_passes(self, llm_client):
        """Test that normal-sized prompts pass validation."""
        prompt = "This is a normal prompt" * 100  # ~2400 chars
        
        # Should not raise
        llm_client._validate_prompt_size(prompt, caller="test_normal")
    
    def test_large_prompt_warning(self, llm_client, mock_logger):
        """Test that large prompts trigger warning but pass."""
        # Create prompt just over warning threshold (20k chars)
        prompt = "x" * 21000
        
        # Should not raise, but should log warning
        llm_client._validate_prompt_size(prompt, caller="test_warning")
        
        # Check warning was logged
        assert mock_logger.warning.called
        call_args = mock_logger.warning.call_args
        assert "llm_context_warning" in call_args[0]
        assert "test_warning" in str(call_args)
    
    def test_oversized_prompt_rejected(self, llm_client, mock_logger):
        """Test that oversized prompts are rejected with detailed error."""
        # Create prompt over max limit (30k chars)
        prompt = "x" * 35000
        
        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            llm_client._validate_prompt_size(prompt, caller="test_overflow")
        
        # Check error message
        error_msg = str(exc_info.value)
        assert "35000" in error_msg  # Actual size
        assert "30000" in error_msg  # Max allowed
        assert "test_overflow" in error_msg  # Caller
        assert "5000" in error_msg  # Exceeded by
        assert "failsafe" in error_msg.lower()
        
        # Check error was logged
        assert mock_logger.error.called
        call_args = mock_logger.error.call_args
        assert "llm_context_overflow" in call_args[0]
        assert "FAILSAFE TRIGGERED" in call_args[0][1]
        
        # Check error details
        error_details = call_args[0][2]
        assert error_details["caller"] == "test_overflow"
        assert error_details["prompt_length"] == 35000
        assert error_details["exceeded_by"] == 5000
        assert "prompt_preview" in error_details
        assert "prompt_end" in error_details
    
    def test_generate_with_oversized_prompt(self, llm_client):
        """Test that generate() rejects oversized prompts."""
        prompt = "x" * 35000
        
        with pytest.raises(ValueError) as exc_info:
            llm_client.generate(prompt, caller="test_generate")
        
        assert "test_generate" in str(exc_info.value)
    
    def test_generate_stream_with_oversized_prompt(self, llm_client):
        """Test that generate_stream() rejects oversized prompts."""
        prompt = "x" * 35000
        
        with pytest.raises(ValueError) as exc_info:
            list(llm_client.generate_stream(prompt, caller="test_stream"))
        
        assert "test_stream" in str(exc_info.value)
    
    def test_error_includes_preview_and_end(self, llm_client, mock_logger):
        """Test that error log includes prompt preview and end for debugging."""
        # Create distinctive prompt
        prompt = "START" + ("x" * 34000) + "END"
        
        with pytest.raises(ValueError):
            llm_client._validate_prompt_size(prompt, caller="test_preview")
        
        # Check error details include preview and end
        error_details = mock_logger.error.call_args[0][2]
        assert "START" in error_details["prompt_preview"]
        assert "END" in error_details["prompt_end"]
    
    def test_warning_includes_usage_percent(self, llm_client, mock_logger):
        """Test that warning includes usage percentage."""
        # 25k chars = 83.3% of 30k limit
        prompt = "x" * 25000
        
        llm_client._validate_prompt_size(prompt, caller="test_percent")
        
        warning_details = mock_logger.warning.call_args[0][2]
        assert "usage_percent" in warning_details
        assert 80 < warning_details["usage_percent"] < 85
    
    def test_caller_parameter_required(self, llm_client):
        """Test that caller parameter helps identify source of large prompts."""
        prompt = "x" * 35000
        
        # Without caller (defaults to "unknown")
        with pytest.raises(ValueError) as exc_info:
            llm_client._validate_prompt_size(prompt)
        
        assert "unknown" in str(exc_info.value)
        
        # With specific caller
        with pytest.raises(ValueError) as exc_info:
            llm_client._validate_prompt_size(prompt, caller="SpecificEngine.method")
        
        assert "SpecificEngine.method" in str(exc_info.value)
