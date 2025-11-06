"""
Tests for knowledge tracker (TDD - Red Phase)
"""
import pytest
from src.patterns.knowledge_tracker import KnowledgeTracker


class TestKnowledgeTrackerInitialization:
    """Test knowledge tracker initialization"""
    
    def test_initialization(self):
        """Test default knowledge state"""
        tracker = KnowledgeTracker()
        
        # Should have user knowledge
        assert hasattr(tracker, 'user_knowledge')
        assert isinstance(tracker.user_knowledge, dict)
        
        # Should have system knowledge
        assert hasattr(tracker, 'system_knowledge')
        assert isinstance(tracker.system_knowledge, dict)
    
    def test_user_knowledge_defaults(self):
        """Test user knowledge initialized with defaults"""
        tracker = KnowledgeTracker()
        
        # Check key user knowledge dimensions exist
        assert 'understands_object_model' in tracker.user_knowledge
        assert 'understands_min_calculation' in tracker.user_knowledge
        assert 'understands_evidence_tiers' in tracker.user_knowledge
        
        # Should default to False (user doesn't know yet)
        assert tracker.user_knowledge['understands_object_model'] is False
        assert tracker.user_knowledge['understands_min_calculation'] is False
    
    def test_system_knowledge_defaults(self):
        """Test system knowledge initialized with defaults"""
        tracker = KnowledgeTracker()
        
        # Check key system knowledge dimensions exist
        assert 'outputs_identified' in tracker.system_knowledge
        assert 'evidence_quality' in tracker.system_knowledge
        assert 'active_outputs' in tracker.system_knowledge
        
        # Should have sensible defaults
        assert tracker.system_knowledge['outputs_identified'] == []
        assert tracker.system_knowledge['evidence_quality'] == 'medium'


class TestKnowledgeUpdate:
    """Test knowledge state updates"""
    
    def test_update_user_knowledge(self):
        """Test updating user knowledge"""
        tracker = KnowledgeTracker()
        
        # Update user knowledge
        tracker.update_user_knowledge({
            'understands_object_model': True,
            'understands_min_calculation': True
        })
        
        assert tracker.user_knowledge['understands_object_model'] is True
        assert tracker.user_knowledge['understands_min_calculation'] is True
    
    def test_update_system_knowledge(self):
        """Test updating system knowledge"""
        tracker = KnowledgeTracker()
        
        # Update system knowledge
        tracker.update_system_knowledge({
            'outputs_identified': ['output_1', 'output_2'],
            'evidence_quality': 'high'
        })
        
        assert tracker.system_knowledge['outputs_identified'] == ['output_1', 'output_2']
        assert tracker.system_knowledge['evidence_quality'] == 'high'
    
    def test_update_preserves_other_values(self):
        """Test update doesn't overwrite unrelated values"""
        tracker = KnowledgeTracker()
        
        # Set initial value
        tracker.update_user_knowledge({'understands_object_model': True})
        
        # Update different value
        tracker.update_user_knowledge({'understands_min_calculation': True})
        
        # Both should be set
        assert tracker.user_knowledge['understands_object_model'] is True
        assert tracker.user_knowledge['understands_min_calculation'] is True


class TestPrerequisiteChecking:
    """Test prerequisite checking"""
    
    def test_check_simple_prerequisite(self):
        """Test checking a simple boolean prerequisite"""
        tracker = KnowledgeTracker()
        
        # Prerequisite not met
        requires = {'user_knowledge.understands_object_model': True}
        assert tracker.check_prerequisites(requires) is False
        
        # Meet prerequisite
        tracker.update_user_knowledge({'understands_object_model': True})
        assert tracker.check_prerequisites(requires) is True
    
    def test_check_multiple_prerequisites(self):
        """Test checking multiple prerequisites"""
        tracker = KnowledgeTracker()
        
        requires = {
            'user_knowledge.understands_object_model': True,
            'user_knowledge.understands_min_calculation': True
        }
        
        # Neither met
        assert tracker.check_prerequisites(requires) is False
        
        # One met
        tracker.update_user_knowledge({'understands_object_model': True})
        assert tracker.check_prerequisites(requires) is False
        
        # Both met
        tracker.update_user_knowledge({'understands_min_calculation': True})
        assert tracker.check_prerequisites(requires) is True
    
    def test_check_system_knowledge_prerequisite(self):
        """Test checking system knowledge prerequisites"""
        tracker = KnowledgeTracker()
        
        requires = {'system_knowledge.outputs_identified': ['output_1']}
        
        # Not met
        assert tracker.check_prerequisites(requires) is False
        
        # Met
        tracker.update_system_knowledge({'outputs_identified': ['output_1']})
        assert tracker.check_prerequisites(requires) is True
    
    def test_check_no_prerequisites(self):
        """Test pattern with no prerequisites always passes"""
        tracker = KnowledgeTracker()
        
        # Empty requirements should pass
        assert tracker.check_prerequisites({}) is True
        assert tracker.check_prerequisites(None) is True


class TestKnowledgeState:
    """Test getting knowledge state"""
    
    def test_get_state(self):
        """Test getting current knowledge state"""
        tracker = KnowledgeTracker()
        
        state = tracker.get_state()
        
        assert 'user' in state
        assert 'system' in state
        assert isinstance(state['user'], dict)
        assert isinstance(state['system'], dict)
    
    def test_get_state_returns_copy(self):
        """Test get_state returns a copy, not reference"""
        tracker = KnowledgeTracker()
        
        state1 = tracker.get_state()
        state2 = tracker.get_state()
        
        # Modifying one shouldn't affect the other
        state1['user']['test'] = True
        assert 'test' not in state2['user']


class TestSerialization:
    """Test serialization for session storage"""
    
    def test_serialize(self):
        """Test serializing knowledge state"""
        tracker = KnowledgeTracker()
        tracker.update_user_knowledge({'understands_object_model': True})
        tracker.update_system_knowledge({'outputs_identified': ['output_1']})
        
        serialized = tracker.serialize()
        
        assert isinstance(serialized, dict)
        assert 'user' in serialized
        assert 'system' in serialized
        assert serialized['user']['understands_object_model'] is True
        assert serialized['system']['outputs_identified'] == ['output_1']
    
    def test_deserialize(self):
        """Test deserializing knowledge state"""
        data = {
            'user': {'understands_object_model': True},
            'system': {'outputs_identified': ['output_1']}
        }
        
        tracker = KnowledgeTracker.deserialize(data)
        
        assert tracker.user_knowledge['understands_object_model'] is True
        assert tracker.system_knowledge['outputs_identified'] == ['output_1']
    
    def test_serialize_deserialize_roundtrip(self):
        """Test serialize/deserialize roundtrip"""
        tracker1 = KnowledgeTracker()
        tracker1.update_user_knowledge({'understands_object_model': True})
        tracker1.update_system_knowledge({'outputs_identified': ['output_1']})
        
        # Serialize
        serialized = tracker1.serialize()
        
        # Deserialize
        tracker2 = KnowledgeTracker.deserialize(serialized)
        
        # Should be identical
        assert tracker2.user_knowledge['understands_object_model'] is True
        assert tracker2.system_knowledge['outputs_identified'] == ['output_1']


class TestConversationState:
    """Test conversation state tracking"""
    
    def test_track_frustration_level(self):
        """Test tracking frustration level"""
        tracker = KnowledgeTracker()
        
        # Should have conversation state
        assert hasattr(tracker, 'conversation_state')
        assert 'frustration_level' in tracker.conversation_state
        
        # Should default to 0
        assert tracker.conversation_state['frustration_level'] == 0.0
    
    def test_update_conversation_state(self):
        """Test updating conversation state"""
        tracker = KnowledgeTracker()
        
        tracker.update_conversation_state({
            'frustration_level': 0.7,
            'confusion_level': 0.5
        })
        
        assert tracker.conversation_state['frustration_level'] == 0.7
        assert tracker.conversation_state['confusion_level'] == 0.5
    
    def test_decay_frustration(self):
        """Test frustration level decay"""
        tracker = KnowledgeTracker()
        
        # Set high frustration
        tracker.update_conversation_state({'frustration_level': 0.8})
        
        # Apply decay
        tracker.apply_decay()
        
        # Should be lower (decays by 0.1 per turn)
        assert tracker.conversation_state['frustration_level'] < 0.8
        assert tracker.conversation_state['frustration_level'] >= 0.7


class TestQualityMetrics:
    """Test quality metrics tracking"""
    
    def test_track_evidence_quality(self):
        """Test tracking evidence quality"""
        tracker = KnowledgeTracker()
        
        # Should have quality metrics
        assert hasattr(tracker, 'quality_metrics')
        assert 'tier1_evidence_count' in tracker.quality_metrics
        assert 'tier5_evidence_count' in tracker.quality_metrics
        
        # Should default to 0
        assert tracker.quality_metrics['tier1_evidence_count'] == 0
    
    def test_increment_evidence_count(self):
        """Test incrementing evidence counts"""
        tracker = KnowledgeTracker()
        
        tracker.increment_evidence_count('tier1')
        tracker.increment_evidence_count('tier1')
        tracker.increment_evidence_count('tier5')
        
        assert tracker.quality_metrics['tier1_evidence_count'] == 2
        assert tracker.quality_metrics['tier5_evidence_count'] == 1
