"""Session state management for Streamlit."""

import uuid
from datetime import datetime
from typing import Optional

from models.data_models import AssessmentSession, Output, CreationContext


class SessionManager:
    """Manages assessment session state."""
    
    def __init__(self, session_state: dict):
        """
        Initialize session manager.
        
        Args:
            session_state: Streamlit session_state object
        """
        self.state = session_state
        
        # Initialize session if not exists
        if 'session' not in self.state:
            self.state.session = AssessmentSession(
                session_id=f"sess_{uuid.uuid4().hex[:8]}",
                created_at=datetime.utcnow().isoformat() + "Z"
            )
        
        # Initialize phase tracking
        if 'phase' not in self.state:
            self.state.phase = 'discovery'  # discovery, assessment, gap_analysis, recommendation
        
        # Initialize component tracking
        if 'current_component' not in self.state:
            self.state.current_component = None
    
    @property
    def session(self) -> AssessmentSession:
        """Get current session."""
        return self.state.session
    
    @property
    def phase(self) -> str:
        """Get current phase."""
        return self.state.phase
    
    @phase.setter
    def phase(self, value: str):
        """Set current phase."""
        self.state.phase = value
    
    @property
    def current_component(self) -> Optional[str]:
        """Get current component being assessed."""
        return self.state.current_component
    
    @current_component.setter
    def current_component(self, value: Optional[str]):
        """Set current component being assessed."""
        self.state.current_component = value
    
    def add_message(self, role: str, content: str):
        """
        Add message to conversation history.
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        self.session.messages.append({
            "role": role,
            "content": content
        })
    
    def set_output(self, output: Output):
        """
        Set identified output.
        
        Args:
            output: Output object
        """
        self.session.output = output
    
    def set_context(self, context: CreationContext):
        """
        Set creation context.
        
        Args:
            context: CreationContext object
        """
        self.session.context = context
    
    def get_conversation_history(self) -> list:
        """Get conversation history."""
        return self.session.messages
    
    def reset(self):
        """Reset session to start new assessment."""
        self.state.session = AssessmentSession(
            session_id=f"sess_{uuid.uuid4().hex[:8]}",
            created_at=datetime.utcnow().isoformat() + "Z"
        )
        self.state.phase = 'discovery'
        self.state.current_component = None
