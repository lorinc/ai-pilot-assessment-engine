"""Session state management for Streamlit with Firebase persistence."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from core.firebase_client import FirebaseClient
from utils.logger import TechnicalLogger


class SessionManager:
    """Manages assessment session state with Firebase persistence."""
    
    def __init__(
        self,
        session_state: dict,
        firebase_client: Optional[FirebaseClient] = None,
        logger: Optional[TechnicalLogger] = None
    ):
        """
        Initialize session manager.
        
        Args:
            session_state: Streamlit session_state object
            firebase_client: Firebase client for persistence
            logger: Technical logger instance
        """
        self.state = session_state
        self.firebase = firebase_client
        self.logger = logger
        
        # Initialize session ID
        if 'session_id' not in self.state:
            self.state['session_id'] = f"sess_{uuid.uuid4().hex[:8]}"
        
        # Initialize conversation ID
        if 'conversation_id' not in self.state:
            self.state['conversation_id'] = f"conv_{uuid.uuid4().hex[:12]}"
        
        # Initialize user ID (will be set after auth)
        if 'user_id' not in self.state:
            self.state['user_id'] = None
        
        # Initialize messages
        if 'messages' not in self.state:
            self.state['messages'] = []
        
        # Initialize phase tracking
        if 'phase' not in self.state:
            self.state['phase'] = 'discovery'  # discovery, assessment, gap_analysis, recommendation
        
        # Initialize metadata
        if 'created_at' not in self.state:
            self.state['created_at'] = datetime.utcnow().isoformat() + "Z"
    
    @property
    def session_id(self) -> str:
        """Get current session ID."""
        return self.state['session_id']
    
    @property
    def conversation_id(self) -> str:
        """Get current conversation ID."""
        return self.state['conversation_id']
    
    @property
    def user_id(self) -> Optional[str]:
        """Get current user ID."""
        return self.state['user_id']
    
    @user_id.setter
    def user_id(self, value: str):
        """Set user ID after authentication."""
        self.state['user_id'] = value
        if self.logger:
            self.logger.info("session_auth", "User authenticated", {
                "user_id": value,
                "session_id": self.session_id
            })
    
    @property
    def phase(self) -> str:
        """Get current phase."""
        return self.state['phase']
    
    @phase.setter
    def phase(self, value: str):
        """Set current phase."""
        self.state['phase'] = value
        if self.logger:
            self.logger.info("session_phase", f"Phase changed to {value}", {
                "phase": value
            })
    
    @property
    def messages(self) -> list:
        """Get conversation messages."""
        return self.state['messages']
    
    def add_message(self, role: str, content: str, persist: bool = True):
        """
        Add message to conversation history.
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            persist: Whether to persist to Firestore
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        self.state['messages'].append(message)
        
        if self.logger:
            self.logger.info("session_message", f"Message added: {role}", {
                "role": role,
                "content_length": len(content)
            })
        
        # Persist to Firestore if user is authenticated
        if persist and self.firebase and self.user_id:
            self.firebase.save_message(
                self.user_id,
                self.conversation_id,
                role,
                content
            )
    
    def load_conversation(self) -> bool:
        """
        Load conversation from Firestore.
        
        Returns:
            True if conversation loaded successfully
        """
        if not self.firebase or not self.user_id:
            return False
        
        data = self.firebase.get_conversation(self.user_id, self.conversation_id)
        if data:
            self.state['messages'] = data.get('messages', [])
            self.state['phase'] = data.get('phase', 'discovery')
            
            if self.logger:
                self.logger.info("session_load", "Conversation loaded from Firestore", {
                    "conversation_id": self.conversation_id,
                    "message_count": len(self.state['messages'])
                })
            return True
        return False
    
    def create_conversation(self) -> bool:
        """
        Create new conversation in Firestore.
        
        Returns:
            True if conversation created successfully
        """
        if not self.firebase or not self.user_id:
            return False
        
        initial_data = {
            "messages": [],
            "phase": self.phase,
            "session_id": self.session_id
        }
        
        return self.firebase.create_conversation(
            self.user_id,
            self.conversation_id,
            initial_data
        )
    
    def get_conversation_history(self) -> list:
        """Get conversation history."""
        return self.state['messages']
    
    def reset(self):
        """Reset session to start new assessment."""
        self.state['session_id'] = f"sess_{uuid.uuid4().hex[:8]}"
        self.state['conversation_id'] = f"conv_{uuid.uuid4().hex[:12]}"
        self.state['messages'] = []
        self.state['phase'] = 'discovery'
        self.state['created_at'] = datetime.utcnow().isoformat() + "Z"
        
        if self.logger:
            self.logger.info("session_reset", "Session reset", {
                "new_session_id": self.session_id,
                "new_conversation_id": self.conversation_id
            })
        
        # Create new conversation in Firestore
        if self.firebase and self.user_id:
            self.create_conversation()
