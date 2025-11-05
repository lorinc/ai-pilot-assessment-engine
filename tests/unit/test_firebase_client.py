"""Unit tests for Firebase client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.core.firebase_client import FirebaseClient
from src.utils.logger import TechnicalLogger


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return TechnicalLogger(max_entries=10)


@pytest.fixture
def mock_firebase_client(mock_logger):
    """Create Firebase client in mock mode."""
    with patch('src.config.settings.settings.MOCK_FIREBASE', True):
        return FirebaseClient(logger=mock_logger)


class TestFirebaseClient:
    """Test FirebaseClient class."""
    
    def test_init_mock_mode(self, mock_firebase_client, mock_logger):
        """Test initialization in mock mode."""
        assert mock_firebase_client.logger == mock_logger
        assert mock_firebase_client.db is None
    
    def test_verify_token_mock(self, mock_firebase_client):
        """Test token verification in mock mode."""
        result = mock_firebase_client.verify_token("mock_token")
        assert result is not None
        assert result["uid"] == "mock_user_123"
        assert result["email"] == "mock@example.com"
    
    def test_get_user_ref_mock(self, mock_firebase_client):
        """Test getting user reference in mock mode."""
        result = mock_firebase_client.get_user_ref("user123")
        assert result is None  # Mock mode returns None
    
    def test_get_conversation_ref_mock(self, mock_firebase_client):
        """Test getting conversation reference in mock mode."""
        result = mock_firebase_client.get_conversation_ref("user123", "conv456")
        assert result is None  # Mock mode returns None
    
    def test_create_conversation_mock(self, mock_firebase_client):
        """Test conversation creation in mock mode."""
        result = mock_firebase_client.create_conversation(
            "user123",
            "conv456",
            {"test": "data"}
        )
        assert result is True
    
    def test_create_conversation_with_no_data(self, mock_firebase_client):
        """Test conversation creation without initial data."""
        result = mock_firebase_client.create_conversation(
            "user123",
            "conv789"
        )
        assert result is True
    
    def test_save_message_mock(self, mock_firebase_client):
        """Test message saving in mock mode."""
        result = mock_firebase_client.save_message(
            "user123",
            "conv456",
            "user",
            "Hello world"
        )
        assert result is True
    
    def test_save_message_assistant(self, mock_firebase_client):
        """Test saving assistant message."""
        result = mock_firebase_client.save_message(
            "user123",
            "conv456",
            "assistant",
            "Hello! How can I help?"
        )
        assert result is True
    
    def test_get_conversation_mock(self, mock_firebase_client):
        """Test conversation retrieval in mock mode."""
        result = mock_firebase_client.get_conversation("user123", "conv456")
        assert result is not None
        assert "messages" in result
        assert result["status"] == "in_progress"
        assert "created_at" in result
        assert "updated_at" in result
    
    def test_list_conversations_mock(self, mock_firebase_client):
        """Test conversation listing in mock mode."""
        result = mock_firebase_client.list_conversations("user123")
        assert isinstance(result, list)
        assert len(result) == 0  # Mock returns empty list
    
    def test_list_conversations_with_limit(self, mock_firebase_client):
        """Test conversation listing with custom limit."""
        result = mock_firebase_client.list_conversations("user123", limit=5)
        assert isinstance(result, list)


@pytest.mark.skipif(
    True,  # Skip real Firebase tests by default
    reason="Requires Firebase credentials"
)
class TestFirebaseClientReal:
    """Test FirebaseClient with real Firebase (requires credentials)."""
    
    @pytest.fixture
    def real_firebase_client(self, mock_logger):
        """Create real Firebase client."""
        with patch('src.config.settings.settings.MOCK_FIREBASE', False):
            return FirebaseClient(logger=mock_logger)
    
    def test_init_real_mode(self, real_firebase_client):
        """Test initialization with real Firebase."""
        # This would require actual Firebase credentials
        pass
