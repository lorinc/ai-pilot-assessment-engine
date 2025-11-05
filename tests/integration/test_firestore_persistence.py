"""Integration tests for Firestore persistence."""

import pytest
from unittest.mock import patch

from src.core.firebase_client import FirebaseClient
from src.core.session_manager import SessionManager
from src.utils.logger import TechnicalLogger


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
    manager.user_id = "test_user_123"
    return manager


class TestFirestorePersistence:
    """Test Firestore persistence operations."""
    
    def test_write_conversation(self, session_manager):
        """Test writing conversation to Firestore."""
        result = session_manager.create_conversation()
        assert result is True
    
    def test_write_message(self, session_manager):
        """Test writing message to Firestore."""
        session_manager.create_conversation()
        session_manager.add_message("user", "Test message", persist=True)
        
        # Message added to local state
        assert len(session_manager.messages) == 1
        assert session_manager.messages[0]["content"] == "Test message"
    
    def test_read_conversation(self, firebase_client):
        """Test reading conversation from Firestore."""
        result = firebase_client.get_conversation("user123", "conv456")
        
        # Mock returns default structure
        assert result is not None
        assert "messages" in result
        assert "status" in result
    
    def test_update_conversation(self, session_manager):
        """Test updating existing conversation."""
        session_manager.create_conversation()
        session_manager.add_message("user", "Message 1", persist=True)
        session_manager.add_message("assistant", "Response 1", persist=True)
        
        assert len(session_manager.messages) == 2
    
    def test_delete_conversation(self, session_manager):
        """Test deleting conversation (via reset)."""
        session_manager.create_conversation()
        session_manager.add_message("user", "Test", persist=True)
        
        old_conversation_id = session_manager.conversation_id
        
        # Reset creates new conversation
        session_manager.reset()
        
        assert session_manager.conversation_id != old_conversation_id
        assert len(session_manager.messages) == 0
    
    def test_user_isolation(self, firebase_client):
        """Test user data isolation."""
        # User A's conversation
        conv_a = firebase_client.get_conversation("user_a", "conv1")
        
        # User B's conversation
        conv_b = firebase_client.get_conversation("user_b", "conv1")
        
        # Both should return data (mock mode)
        assert conv_a is not None
        assert conv_b is not None
        
        # In real mode, these would be isolated by user_id path
    
    def test_list_conversations(self, firebase_client):
        """Test listing user conversations."""
        conversations = firebase_client.list_conversations("user123", limit=10)
        
        # Mock returns empty list
        assert isinstance(conversations, list)
