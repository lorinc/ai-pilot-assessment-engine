"""Unit tests for SessionManager."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from core.session_manager import SessionManager
from models.data_models import AssessmentSession, Output, CreationContext


class MockSessionState:
    """Mock session state that supports attribute access."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __contains__(self, key):
        return hasattr(self, key)


class TestSessionManager:
    """Test suite for SessionManager."""
    
    @pytest.fixture
    def empty_state(self):
        """Create empty session state."""
        return MockSessionState()
    
    @pytest.fixture
    def populated_state(self):
        """Create pre-populated session state."""
        return MockSessionState(
            session=AssessmentSession(
                session_id="test_session_123",
                created_at="2025-01-01T00:00:00Z"
            ),
            phase='assessment',
            current_component='dependency_quality'
        )
    
    def test_init_creates_new_session(self, empty_state):
        """Test initialization creates new session."""
        manager = SessionManager(empty_state)
        
        assert 'session' in empty_state
        assert isinstance(empty_state.session, AssessmentSession)
        assert empty_state.session.session_id.startswith('sess_')
        assert 'Z' in empty_state.session.created_at
    
    def test_init_creates_default_phase(self, empty_state):
        """Test initialization sets default phase."""
        manager = SessionManager(empty_state)
        
        assert 'phase' in empty_state
        assert empty_state.phase == 'discovery'
    
    def test_init_creates_default_component(self, empty_state):
        """Test initialization sets default component."""
        manager = SessionManager(empty_state)
        
        assert 'current_component' in empty_state
        assert empty_state.current_component is None
    
    def test_init_preserves_existing_session(self, populated_state):
        """Test initialization preserves existing session."""
        original_session = populated_state.session
        
        manager = SessionManager(populated_state)
        
        assert manager.session == original_session
        assert manager.session.session_id == "test_session_123"
    
    def test_init_preserves_existing_phase(self, populated_state):
        """Test initialization preserves existing phase."""
        manager = SessionManager(populated_state)
        
        assert manager.phase == 'assessment'
    
    def test_init_preserves_existing_component(self, populated_state):
        """Test initialization preserves existing component."""
        manager = SessionManager(populated_state)
        
        assert manager.current_component == 'dependency_quality'
    
    def test_session_property_getter(self, empty_state):
        """Test session property getter."""
        manager = SessionManager(empty_state)
        
        session = manager.session
        
        assert isinstance(session, AssessmentSession)
        assert session == empty_state.session
    
    def test_phase_property_getter(self, empty_state):
        """Test phase property getter."""
        manager = SessionManager(empty_state)
        
        phase = manager.phase
        
        assert phase == 'discovery'
    
    def test_phase_property_setter(self, empty_state):
        """Test phase property setter."""
        manager = SessionManager(empty_state)
        
        manager.phase = 'gap_analysis'
        
        assert manager.phase == 'gap_analysis'
        assert empty_state.phase == 'gap_analysis'
    
    def test_current_component_property_getter(self, empty_state):
        """Test current_component property getter."""
        manager = SessionManager(empty_state)
        
        component = manager.current_component
        
        assert component is None
    
    def test_current_component_property_setter(self, empty_state):
        """Test current_component property setter."""
        manager = SessionManager(empty_state)
        
        manager.current_component = 'team_execution'
        
        assert manager.current_component == 'team_execution'
        assert empty_state.current_component == 'team_execution'
    
    def test_add_message_user(self, empty_state):
        """Test adding user message."""
        manager = SessionManager(empty_state)
        
        manager.add_message("user", "Hello")
        
        assert len(manager.session.messages) == 1
        assert manager.session.messages[0]["role"] == "user"
        assert manager.session.messages[0]["content"] == "Hello"
    
    def test_add_message_assistant(self, empty_state):
        """Test adding assistant message."""
        manager = SessionManager(empty_state)
        
        manager.add_message("assistant", "Hi there!")
        
        assert len(manager.session.messages) == 1
        assert manager.session.messages[0]["role"] == "assistant"
        assert manager.session.messages[0]["content"] == "Hi there!"
    
    def test_add_multiple_messages(self, empty_state):
        """Test adding multiple messages."""
        manager = SessionManager(empty_state)
        
        manager.add_message("user", "First")
        manager.add_message("assistant", "Second")
        manager.add_message("user", "Third")
        
        assert len(manager.session.messages) == 3
        assert manager.session.messages[0]["content"] == "First"
        assert manager.session.messages[1]["content"] == "Second"
        assert manager.session.messages[2]["content"] == "Third"
    
    def test_set_output(self, empty_state):
        """Test setting output."""
        manager = SessionManager(empty_state)
        
        output = Output(
            id="sales_forecast",
            name="Sales Forecast",
            function="Sales",
            description="Revenue predictions"
        )
        
        manager.set_output(output)
        
        assert manager.session.output == output
        assert manager.session.output.id == "sales_forecast"
    
    def test_set_context(self, empty_state):
        """Test setting context."""
        manager = SessionManager(empty_state)
        
        context = CreationContext(
            team="Sales Operations",
            process="Forecasting",
            system="Salesforce",
            step="Consolidation"
        )
        
        manager.set_context(context)
        
        assert manager.session.context == context
        assert manager.session.context.team == "Sales Operations"
    
    def test_get_conversation_history_empty(self, empty_state):
        """Test getting empty conversation history."""
        manager = SessionManager(empty_state)
        
        history = manager.get_conversation_history()
        
        assert isinstance(history, list)
        assert len(history) == 0
    
    def test_get_conversation_history_with_messages(self, empty_state):
        """Test getting conversation history with messages."""
        manager = SessionManager(empty_state)
        manager.add_message("user", "Hello")
        manager.add_message("assistant", "Hi")
        
        history = manager.get_conversation_history()
        
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
    
    def test_reset_creates_new_session(self, populated_state):
        """Test reset creates new session."""
        manager = SessionManager(populated_state)
        original_session_id = manager.session.session_id
        
        manager.reset()
        
        assert manager.session.session_id != original_session_id
        assert manager.session.session_id.startswith('sess_')
    
    def test_reset_clears_messages(self, populated_state):
        """Test reset clears messages."""
        manager = SessionManager(populated_state)
        manager.add_message("user", "Test")
        
        manager.reset()
        
        assert len(manager.session.messages) == 0
    
    def test_reset_resets_phase(self, populated_state):
        """Test reset resets phase to discovery."""
        manager = SessionManager(populated_state)
        manager.phase = 'recommendation'
        
        manager.reset()
        
        assert manager.phase == 'discovery'
    
    def test_reset_resets_component(self, populated_state):
        """Test reset resets current component."""
        manager = SessionManager(populated_state)
        manager.current_component = 'system_support'
        
        manager.reset()
        
        assert manager.current_component is None
    
    def test_reset_clears_output(self, populated_state):
        """Test reset clears output."""
        manager = SessionManager(populated_state)
        output = Output(id="test", name="Test", function="Test", description="Test output")
        manager.set_output(output)
        
        manager.reset()
        
        assert manager.session.output is None
    
    def test_reset_clears_context(self, populated_state):
        """Test reset clears context."""
        manager = SessionManager(populated_state)
        context = CreationContext(team="Test", process="Test", system="Test")
        manager.set_context(context)
        
        manager.reset()
        
        assert manager.session.context is None
    
    def test_session_id_format(self, empty_state):
        """Test session ID has correct format."""
        manager = SessionManager(empty_state)
        
        session_id = manager.session.session_id
        
        assert session_id.startswith('sess_')
        assert len(session_id) == 13  # 'sess_' + 8 hex chars
    
    def test_created_at_format(self, empty_state):
        """Test created_at has ISO format with Z."""
        manager = SessionManager(empty_state)
        
        created_at = manager.session.created_at
        
        assert created_at.endswith('Z')
        # Should be parseable as ISO datetime
        datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    
    def test_multiple_resets(self, empty_state):
        """Test multiple resets work correctly."""
        manager = SessionManager(empty_state)
        
        session_ids = []
        for _ in range(3):
            session_ids.append(manager.session.session_id)
            manager.reset()
        
        # All session IDs should be unique
        assert len(set(session_ids)) == 3
    
    def test_state_persistence(self, empty_state):
        """Test that changes persist in session_state."""
        manager = SessionManager(empty_state)
        
        manager.add_message("user", "Test")
        manager.phase = 'assessment'
        
        # Create new manager with same state
        manager2 = SessionManager(empty_state)
        
        assert len(manager2.session.messages) == 1
        assert manager2.phase == 'assessment'
