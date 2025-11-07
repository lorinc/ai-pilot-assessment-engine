"""Integration tests for Firebase with real GCP credentials.

These tests require:
- Valid Firebase credentials
- MOCK_FIREBASE=false
- Actual Firestore database

Run with: pytest tests/integration/test_real_firebase.py -m requires_gcp
"""

import pytest
import os
from datetime import datetime

from src.core.firebase_client import FirebaseClient
from src.utils.logger import TechnicalLogger


@pytest.fixture
def real_firebase_client():
    """Create Firebase client with real credentials.
    
    Note: Requires MOCK_FIREBASE=false to be set BEFORE pytest starts.
    Run with: ./tests/run_real_tests.sh
    """
    logger = TechnicalLogger(max_entries=10)
    client = FirebaseClient(logger=logger)
    return client


@pytest.fixture
def test_user_id():
    """Generate unique test user ID."""
    return f"test_user_{datetime.utcnow().timestamp()}"


@pytest.fixture
def test_conversation_id():
    """Generate unique test conversation ID."""
    return f"test_conv_{datetime.utcnow().timestamp()}"


@pytest.mark.requires_gcp
class TestRealFirebaseClient:
    """Test FirebaseClient with real Firebase."""
    
    def test_initialize_firebase(self, real_firebase_client):
        """Test Firebase initialization with real credentials."""
        assert real_firebase_client.db is not None
        assert real_firebase_client.logger is not None
    
    def test_get_user_ref(self, real_firebase_client, test_user_id):
        """Test getting user document reference."""
        ref = real_firebase_client.get_user_ref(test_user_id)
        assert ref is not None
        assert test_user_id in ref.path
    
    def test_get_conversation_ref(self, real_firebase_client, test_user_id, test_conversation_id):
        """Test getting conversation document reference."""
        ref = real_firebase_client.get_conversation_ref(test_user_id, test_conversation_id)
        assert ref is not None
        assert test_user_id in ref.path
        assert test_conversation_id in ref.path
    
    def test_create_and_get_conversation(self, real_firebase_client, test_user_id, test_conversation_id):
        """Test creating and retrieving a conversation."""
        # Create conversation
        initial_data = {
            "test_field": "test_value",
            "created_by": "pytest"
        }
        result = real_firebase_client.create_conversation(
            test_user_id,
            test_conversation_id,
            initial_data
        )
        assert result is True
        
        # Retrieve conversation
        conversation = real_firebase_client.get_conversation(test_user_id, test_conversation_id)
        assert conversation is not None
        assert conversation["test_field"] == "test_value"
        assert conversation["created_by"] == "pytest"
        assert conversation["status"] == "in_progress"
        assert "created_at" in conversation
        assert "updated_at" in conversation
    
    def test_save_and_retrieve_messages(self, real_firebase_client, test_user_id, test_conversation_id):
        """Test saving and retrieving messages."""
        # Create conversation first
        real_firebase_client.create_conversation(test_user_id, test_conversation_id)
        
        # Save user message
        result1 = real_firebase_client.save_message(
            test_user_id,
            test_conversation_id,
            "user",
            "Hello, this is a test message"
        )
        assert result1 is True
        
        # Save assistant message
        result2 = real_firebase_client.save_message(
            test_user_id,
            test_conversation_id,
            "assistant",
            "Hello! I received your test message."
        )
        assert result2 is True
        
        # Retrieve conversation with messages
        conversation = real_firebase_client.get_conversation(test_user_id, test_conversation_id)
        assert conversation is not None
        assert "messages" in conversation
        assert len(conversation["messages"]) == 2
        
        # Verify message content
        messages = conversation["messages"]
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello, this is a test message"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Hello! I received your test message."
    
    def test_list_conversations(self, real_firebase_client, test_user_id):
        """Test listing user conversations."""
        # Create multiple conversations
        conv_id_1 = f"test_conv_1_{datetime.utcnow().timestamp()}"
        conv_id_2 = f"test_conv_2_{datetime.utcnow().timestamp()}"
        
        real_firebase_client.create_conversation(test_user_id, conv_id_1, {"name": "Conv 1"})
        real_firebase_client.create_conversation(test_user_id, conv_id_2, {"name": "Conv 2"})
        
        # List conversations
        conversations = real_firebase_client.list_conversations(test_user_id, limit=10)
        assert isinstance(conversations, list)
        assert len(conversations) >= 2
        
        # Verify conversations have IDs
        conv_ids = [c.get('id') for c in conversations]
        assert conv_id_1 in conv_ids or conv_id_2 in conv_ids
    
    def test_conversation_not_found(self, real_firebase_client, test_user_id):
        """Test retrieving non-existent conversation."""
        conversation = real_firebase_client.get_conversation(
            test_user_id,
            "non_existent_conversation_id"
        )
        assert conversation is None
    
    def test_create_conversation_without_initial_data(self, real_firebase_client, test_user_id):
        """Test creating conversation with no initial data."""
        conv_id = f"test_conv_empty_{datetime.utcnow().timestamp()}"
        
        result = real_firebase_client.create_conversation(test_user_id, conv_id)
        assert result is True
        
        conversation = real_firebase_client.get_conversation(test_user_id, conv_id)
        assert conversation is not None
        assert conversation["status"] == "in_progress"
