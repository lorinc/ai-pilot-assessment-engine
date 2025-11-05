"""Integration tests for streaming chat functionality."""

import pytest
from unittest.mock import patch

from src.core.llm_client import LLMClient
from src.core.firebase_client import FirebaseClient
from src.core.session_manager import SessionManager
from src.utils.logger import TechnicalLogger


@pytest.fixture
def llm_client():
    """Create LLM client in mock mode."""
    with patch('src.config.settings.settings.MOCK_LLM', True):
        return LLMClient(logger=TechnicalLogger())


@pytest.fixture
def firebase_client():
    """Create Firebase client in mock mode."""
    with patch('src.config.settings.settings.MOCK_FIREBASE', True):
        return FirebaseClient(logger=TechnicalLogger())


@pytest.fixture
def session_manager(firebase_client):
    """Create session manager."""
    state = {}
    manager = SessionManager(state, firebase_client, TechnicalLogger())
    manager.user_id = "test_user"
    manager.create_conversation()
    return manager


class TestStreamingChat:
    """Test streaming chat functionality."""
    
    def test_send_message_to_llm(self, llm_client):
        """Test sending message to LLM."""
        response = llm_client.generate("Hello, how are you?")
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_receive_streaming_response(self, llm_client):
        """Test receiving streaming response."""
        chunks = []
        for chunk in llm_client.generate_stream("Tell me a story"):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
    
    def test_save_message_and_response(self, session_manager, llm_client):
        """Test saving message and response to Firestore."""
        # User sends message
        user_message = "What is AI?"
        session_manager.add_message("user", user_message, persist=True)
        
        # Generate response
        response = llm_client.generate(user_message)
        
        # Save response
        session_manager.add_message("assistant", response, persist=True)
        
        # Verify both messages in history
        assert len(session_manager.messages) == 2
        assert session_manager.messages[0]["role"] == "user"
        assert session_manager.messages[1]["role"] == "assistant"
    
    def test_load_conversation_history(self, session_manager):
        """Test loading conversation history."""
        # Add some messages
        session_manager.add_message("user", "Message 1", persist=True)
        session_manager.add_message("assistant", "Response 1", persist=True)
        session_manager.add_message("user", "Message 2", persist=True)
        
        # Get history
        history = session_manager.get_conversation_history()
        
        assert len(history) == 3
        assert history[0]["content"] == "Message 1"
        assert history[1]["content"] == "Response 1"
        assert history[2]["content"] == "Message 2"
    
    def test_streaming_with_conversation_context(self, llm_client, session_manager):
        """Test streaming with conversation context."""
        # Build conversation history
        session_manager.add_message("user", "My name is Alice", persist=False)
        session_manager.add_message("assistant", "Nice to meet you, Alice!", persist=False)
        
        # Build prompt with history
        history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in session_manager.messages
        ]
        
        prompt = llm_client.build_prompt(
            "What is my name?",
            conversation_history=history
        )
        
        # Prompt should include history
        assert "Alice" in prompt
        assert "What is my name?" in prompt
    
    def test_handle_streaming_interruption(self, llm_client):
        """Test handling streaming interruption."""
        chunks = []
        try:
            for i, chunk in enumerate(llm_client.generate_stream("Test")):
                chunks.append(chunk)
                if i >= 0:  # Interrupt after first chunk
                    break
        except Exception as e:
            pytest.fail(f"Streaming should not raise exception: {e}")
        
        # Should have at least one chunk
        assert len(chunks) > 0
    
    def test_end_to_end_chat_flow(self, llm_client, session_manager):
        """Test complete chat flow."""
        # 1. User sends message
        user_msg = "Hello, I need help with sales forecasts"
        session_manager.add_message("user", user_msg, persist=True)
        
        # 2. Build prompt with context
        prompt = llm_client.build_prompt(user_msg)
        
        # 3. Stream response
        full_response = ""
        for chunk in llm_client.generate_stream(prompt):
            full_response += chunk
        
        # 4. Save response
        session_manager.add_message("assistant", full_response, persist=True)
        
        # 5. Verify conversation state
        assert len(session_manager.messages) == 2
        assert session_manager.messages[0]["role"] == "user"
        assert session_manager.messages[1]["role"] == "assistant"
        assert len(session_manager.messages[1]["content"]) > 0
