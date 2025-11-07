"""Integration tests for LLM with real Vertex AI.

These tests require:
- Valid GCP credentials
- MOCK_LLM=false
- Vertex AI API enabled
- Will incur small API costs (~$0.01 per test run)

Run with: pytest tests/integration/test_real_llm.py -m requires_gcp
"""

import pytest
import os

from src.core.llm_client import LLMClient
from src.utils.logger import TechnicalLogger


@pytest.fixture
def real_llm_client():
    """Create LLM client with real Vertex AI.
    
    Note: Requires MOCK_LLM=false to be set BEFORE pytest starts.
    Run with: ./tests/run_real_tests.sh
    """
    logger = TechnicalLogger(max_entries=10)
    client = LLMClient(logger=logger)
    return client


@pytest.mark.requires_gcp
class TestRealLLMClient:
    """Test LLMClient with real Vertex AI."""
    
    def test_initialize_vertex_ai(self, real_llm_client):
        """Test Vertex AI initialization with real credentials."""
        assert real_llm_client.model is not None
        assert real_llm_client.project_id is not None
        assert real_llm_client.location is not None
    
    def test_generate_simple_response(self, real_llm_client):
        """Test generating a simple response."""
        response = real_llm_client.generate(
            "Say 'Hello, World!' and nothing else.",
            temperature=0.0,
            max_output_tokens=50
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "hello" in response.lower() or "world" in response.lower()
    
    def test_generate_with_temperature(self, real_llm_client):
        """Test generation with different temperature."""
        response = real_llm_client.generate(
            "What is 2+2?",
            temperature=0.1,
            max_output_tokens=20
        )
        
        assert isinstance(response, str)
        assert "4" in response
    
    def test_generate_stream_simple(self, real_llm_client):
        """Test streaming generation."""
        chunks = []
        for chunk in real_llm_client.generate_stream(
            "Count from 1 to 3, one number per line.",
            temperature=0.0,
            max_output_tokens=50
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
    
    def test_generate_stream_with_prompt_builder(self, real_llm_client):
        """Test streaming with prompt builder."""
        prompt = real_llm_client.build_prompt(
            user_message="What is AI?",
            system_context={"role": "You are a helpful assistant."}
        )
        
        chunks = []
        for chunk in real_llm_client.generate_stream(prompt, max_output_tokens=100):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
        assert "AI" in full_response or "artificial" in full_response.lower()
    
    def test_build_prompt_with_history(self, real_llm_client):
        """Test prompt building with conversation history."""
        history = [
            {"role": "user", "content": "My name is Alice"},
            {"role": "assistant", "content": "Nice to meet you, Alice!"}
        ]
        
        prompt = real_llm_client.build_prompt(
            user_message="What is my name?",
            conversation_history=history
        )
        
        response = real_llm_client.generate(prompt, temperature=0.0, max_output_tokens=50)
        
        assert isinstance(response, str)
        assert "alice" in response.lower()
    
    def test_generate_with_max_tokens(self, real_llm_client):
        """Test generation respects max token limit."""
        response = real_llm_client.generate(
            "Write a long essay about AI.",
            temperature=0.5,
            max_output_tokens=50  # Very limited
        )
        
        assert isinstance(response, str)
        # Response should be relatively short due to token limit
        assert len(response) < 500
    
    def test_multiple_streaming_calls(self, real_llm_client):
        """Test multiple streaming calls work correctly."""
        # First call
        chunks1 = list(real_llm_client.generate_stream(
            "Say 'First'",
            temperature=0.0,
            max_output_tokens=20
        ))
        
        # Second call
        chunks2 = list(real_llm_client.generate_stream(
            "Say 'Second'",
            temperature=0.0,
            max_output_tokens=20
        ))
        
        assert len(chunks1) > 0
        assert len(chunks2) > 0
        
        response1 = "".join(chunks1)
        response2 = "".join(chunks2)
        
        # Responses should be different
        assert response1 != response2
