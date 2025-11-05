"""Unit tests for Session Manager."""

import pytest
from unittest.mock import Mock, MagicMock

from src.core.session_manager import SessionManager
from src.core.firebase_client import FirebaseClient
from src.utils.logger import TechnicalLogger


@pytest.fixture
def mock_session_state():
    """Create mock Streamlit session state."""
    return {}


@pytest.fixture
def mock_firebase():
    """Create mock Firebase client."""
    firebase = Mock(spec=FirebaseClient)
    firebase.save_message.return_value = True
    firebase.create_conversation.return_value = True
    firebase.get_conversation.return_value = None
    return firebase


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return TechnicalLogger(max_entries=10)


@pytest.fixture
def session_manager(mock_session_state, mock_firebase, mock_logger):
    """Create session manager."""
    return SessionManager(mock_session_state, mock_firebase, mock_logger)


class TestSessionManager:
    """Test SessionManager class."""
    
    def test_init_creates_session_id(self, session_manager):
        """Test initialization creates session ID."""
        assert session_manager.session_id is not None
        assert session_manager.session_id.startswith("sess_")
    
    def test_init_creates_conversation_id(self, session_manager):
        """Test initialization creates conversation ID."""
        assert session_manager.conversation_id is not None
        assert session_manager.conversation_id.startswith("conv_")
    
    def test_init_default_phase(self, session_manager):
        """Test default phase is discovery."""
        assert session_manager.phase == "discovery"
    
    def test_set_user_id(self, session_manager):
        """Test setting user ID."""
        session_manager.user_id = "user123"
        assert session_manager.user_id == "user123"
    
    def test_add_message_without_persist(self, session_manager, mock_firebase):
        """Test adding message without persistence."""
        session_manager.add_message("user", "Hello", persist=False)
        assert len(session_manager.messages) == 1
        assert session_manager.messages[0]["role"] == "user"
        assert session_manager.messages[0]["content"] == "Hello"
        mock_firebase.save_message.assert_not_called()
    
    def test_add_message_with_persist(self, session_manager, mock_firebase):
        """Test adding message with persistence."""
        session_manager.user_id = "user123"
        session_manager.add_message("user", "Hello", persist=True)
        assert len(session_manager.messages) == 1
        mock_firebase.save_message.assert_called_once()
    
    def test_add_message_no_persist_without_user(self, session_manager, mock_firebase):
        """Test message not persisted if user not authenticated."""
        session_manager.add_message("user", "Hello", persist=True)
        mock_firebase.save_message.assert_not_called()
    
    def test_phase_setter(self, session_manager):
        """Test phase setter."""
        session_manager.phase = "assessment"
        assert session_manager.phase == "assessment"
    
    def test_get_conversation_history(self, session_manager):
        """Test getting conversation history."""
        session_manager.add_message("user", "Message 1", persist=False)
        session_manager.add_message("assistant", "Response 1", persist=False)
        history = session_manager.get_conversation_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
    
    def test_reset(self, session_manager):
        """Test session reset."""
        old_session_id = session_manager.session_id
        old_conversation_id = session_manager.conversation_id
        
        session_manager.add_message("user", "Test", persist=False)
        session_manager.phase = "assessment"
        
        session_manager.reset()
        
        assert session_manager.session_id != old_session_id
        assert session_manager.conversation_id != old_conversation_id
        assert len(session_manager.messages) == 0
        assert session_manager.phase == "discovery"
    
    def test_create_conversation(self, session_manager, mock_firebase):
        """Test creating conversation."""
        session_manager.user_id = "user123"
        result = session_manager.create_conversation()
        assert result is True
        mock_firebase.create_conversation.assert_called_once()
    
    def test_load_conversation(self, session_manager, mock_firebase):
        """Test loading conversation."""
        mock_firebase.get_conversation.return_value = {
            "messages": [{"role": "user", "content": "Test"}],
            "phase": "assessment"
        }
        session_manager.user_id = "user123"
        
        result = session_manager.load_conversation()
        assert result is True
        assert len(session_manager.messages) == 1
        assert session_manager.phase == "assessment"
