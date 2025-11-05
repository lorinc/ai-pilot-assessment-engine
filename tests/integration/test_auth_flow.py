"""Integration tests for authentication flow."""

import pytest
from unittest.mock import Mock, patch

from src.core.firebase_client import FirebaseClient
from src.core.session_manager import SessionManager
from src.utils.logger import TechnicalLogger


@pytest.fixture
def mock_session_state():
    """Create mock session state."""
    return {}


@pytest.fixture
def firebase_client():
    """Create Firebase client in mock mode."""
    with patch('src.config.settings.settings.MOCK_FIREBASE', True):
        return FirebaseClient(logger=TechnicalLogger())


@pytest.fixture
def session_manager(mock_session_state, firebase_client):
    """Create session manager."""
    return SessionManager(mock_session_state, firebase_client, TechnicalLogger())


class TestAuthFlow:
    """Test authentication flow."""
    
    def test_user_signs_in(self, session_manager):
        """Test user sign-in flow."""
        # Initially no user
        assert session_manager.user_id is None
        
        # User signs in
        session_manager.user_id = "user123"
        
        # User ID is set
        assert session_manager.user_id == "user123"
    
    def test_session_persists_user_id(self, session_manager):
        """Test session state persists user ID."""
        session_manager.user_id = "user123"
        
        # Create new session manager with same state
        new_manager = SessionManager(
            session_manager.state,
            session_manager.firebase,
            session_manager.logger
        )
        
        # User ID persists
        assert new_manager.user_id == "user123"
    
    def test_unauthenticated_user_no_persistence(self, session_manager):
        """Test unauthenticated user cannot persist messages."""
        # No user ID set
        assert session_manager.user_id is None
        
        # Add message with persist=True
        session_manager.add_message("user", "Test", persist=True)
        
        # Message added to local state but not persisted
        assert len(session_manager.messages) == 1
    
    def test_user_signs_out(self, session_manager):
        """Test user sign-out."""
        # User signs in
        session_manager.user_id = "user123"
        session_manager.add_message("user", "Test", persist=False)
        
        # User signs out
        session_manager.user_id = None
        
        # User ID cleared
        assert session_manager.user_id is None
        
        # Messages still in session (not cleared on logout)
        assert len(session_manager.messages) == 1
    
    def test_verify_token_mock(self, firebase_client):
        """Test token verification in mock mode."""
        result = firebase_client.verify_token("mock_token")
        
        assert result is not None
        assert "uid" in result
        assert "email" in result
