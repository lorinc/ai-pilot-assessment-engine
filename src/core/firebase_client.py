"""Firebase client for authentication and Firestore persistence."""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth

from config.settings import settings
from utils.logger import TechnicalLogger


class FirebaseClient:
    """Client for Firebase Auth and Firestore operations."""
    
    def __init__(self, logger: Optional[TechnicalLogger] = None):
        """
        Initialize Firebase client.
        
        Args:
            logger: Technical logger instance
        """
        self.logger = logger
        self.db = None
        
        if not settings.MOCK_FIREBASE:
            self._initialize_firebase()
        else:
            if self.logger:
                self.logger.warning("firebase_init", "Mock mode enabled - no real Firebase calls", {
                    "mock_mode": True
                })
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        try:
            # Check if already initialized
            firebase_admin.get_app()
            if self.logger:
                self.logger.info("firebase_init", "Firebase already initialized", {})
        except ValueError:
            # Initialize Firebase
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {
                'projectId': settings.GCP_PROJECT_ID,
            })
            if self.logger:
                self.logger.info("firebase_init", "Firebase initialized", {
                    "project": settings.GCP_PROJECT_ID
                })
        
        self.db = firestore.client()
    
    def verify_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token.
        
        Args:
            id_token: Firebase ID token from client
            
        Returns:
            Decoded token with user info, or None if invalid
        """
        if settings.MOCK_FIREBASE:
            return {"uid": "mock_user_123", "email": "mock@example.com"}
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            if self.logger:
                self.logger.info("auth_verify", "Token verified", {
                    "user_id": decoded_token.get("uid")
                })
            return decoded_token
        except Exception as e:
            if self.logger:
                self.logger.error("auth_verify", f"Token verification failed: {str(e)}", {
                    "error": str(e)
                })
            return None
    
    def get_user_ref(self, user_id: str):
        """
        Get Firestore reference to user document.
        
        Args:
            user_id: User ID
            
        Returns:
            Firestore document reference
        """
        if settings.MOCK_FIREBASE:
            return None
        
        return self.db.collection('users').document(user_id)
    
    def get_conversation_ref(self, user_id: str, conversation_id: str):
        """
        Get Firestore reference to conversation document.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            
        Returns:
            Firestore document reference
        """
        if settings.MOCK_FIREBASE:
            return None
        
        return self.db.collection('users').document(user_id).collection('conversations').document(conversation_id)
    
    def create_conversation(
        self,
        user_id: str,
        conversation_id: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create new conversation document.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            initial_data: Initial conversation data
            
        Returns:
            True if successful
        """
        if settings.MOCK_FIREBASE:
            if self.logger:
                self.logger.info("firestore_write", "Mock conversation created", {
                    "user_id": user_id,
                    "conversation_id": conversation_id
                })
            return True
        
        try:
            data = initial_data or {}
            data.update({
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "in_progress"
            })
            
            self.get_conversation_ref(user_id, conversation_id).set(data)
            
            if self.logger:
                self.logger.info("firestore_write", "Conversation created", {
                    "user_id": user_id,
                    "conversation_id": conversation_id
                })
            return True
        except Exception as e:
            if self.logger:
                self.logger.error("firestore_write", f"Failed to create conversation: {str(e)}", {
                    "error": str(e)
                })
            return False
    
    def save_message(
        self,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        Save message to conversation.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            True if successful
        """
        if settings.MOCK_FIREBASE:
            if self.logger:
                self.logger.info("firestore_write", "Mock message saved", {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "role": role
                })
            return True
        
        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            }
            
            self.get_conversation_ref(user_id, conversation_id).update({
                "messages": firestore.ArrayUnion([message]),
                "updated_at": datetime.utcnow()
            })
            
            if self.logger:
                self.logger.info("firestore_write", "Message saved", {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "role": role
                })
            return True
        except Exception as e:
            if self.logger:
                self.logger.error("firestore_write", f"Failed to save message: {str(e)}", {
                    "error": str(e)
                })
            return False
    
    def get_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get conversation data.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            
        Returns:
            Conversation data or None
        """
        if settings.MOCK_FIREBASE:
            return {
                "messages": [],
                "status": "in_progress",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        
        try:
            doc = self.get_conversation_ref(user_id, conversation_id).get()
            if doc.exists:
                if self.logger:
                    self.logger.info("firestore_read", "Conversation retrieved", {
                        "user_id": user_id,
                        "conversation_id": conversation_id
                    })
                return doc.to_dict()
            return None
        except Exception as e:
            if self.logger:
                self.logger.error("firestore_read", f"Failed to get conversation: {str(e)}", {
                    "error": str(e)
                })
            return None
    
    def list_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List user's conversations.
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation data
        """
        if settings.MOCK_FIREBASE:
            return []
        
        try:
            conversations = []
            docs = self.db.collection('users').document(user_id).collection('conversations')\
                .order_by('updated_at', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                conversations.append(data)
            
            if self.logger:
                self.logger.info("firestore_read", "Conversations listed", {
                    "user_id": user_id,
                    "count": len(conversations)
                })
            return conversations
        except Exception as e:
            if self.logger:
                self.logger.error("firestore_read", f"Failed to list conversations: {str(e)}", {
                    "error": str(e)
                })
            return []
