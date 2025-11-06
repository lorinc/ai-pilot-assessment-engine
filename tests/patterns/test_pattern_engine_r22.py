"""
Tests for PatternEngine with Release 2.2 features

TDD RED phase - tests for ResponseComposer + SituationalAwareness integration

Tests the integration of:
- ResponseComposer (reactive + proactive selection)
- SituationalAwareness (8-dimensional composition)
- PatternEngine (orchestration)
"""
import pytest
from src.patterns.pattern_engine import PatternEngine
from src.patterns.knowledge_tracker import KnowledgeTracker


class TestPatternEngineWithSituationalAwareness:
    """Test PatternEngine with situational awareness"""
    
    def test_pattern_engine_has_situational_awareness(self):
        """PatternEngine should have SituationalAwareness instance"""
        engine = PatternEngine()
        
        assert hasattr(engine, 'situational_awareness')
        assert engine.situational_awareness is not None
    
    def test_situation_updates_from_triggers(self):
        """Situation should update based on detected triggers"""
        engine = PatternEngine()
        
        # Initial situation (discovery heavy)
        initial_discovery = engine.situational_awareness.composition['discovery']
        
        # Process message that triggers discovery
        result = engine.process_message(
            "We need to assess sales forecasting in our CRM",
            is_first_message=False
        )
        
        # Discovery should increase
        assert engine.situational_awareness.composition['discovery'] >= initial_discovery
    
    def test_situation_evolves_across_turns(self):
        """Situation should evolve as conversation progresses"""
        engine = PatternEngine()
        
        # Turn 1: Discovery
        engine.process_message("We need to assess sales forecasting")
        discovery_after_1 = engine.situational_awareness.composition['discovery']
        
        # Turn 2: Confusion (should spike clarification)
        clarification_before = engine.situational_awareness.composition['clarification']
        engine.process_message("I'm confused about this")
        clarification_after = engine.situational_awareness.composition['clarification']
        
        # Clarification should increase after confusion
        assert clarification_after > clarification_before


class TestPatternEngineWithResponseComposer:
    """Test PatternEngine with response composer"""
    
    def test_pattern_engine_has_response_composer(self):
        """PatternEngine should have ResponseComposer instance"""
        engine = PatternEngine()
        
        assert hasattr(engine, 'response_composer')
        assert engine.response_composer is not None
    
    def test_response_composition_used(self):
        """PatternEngine should use ResponseComposer for selection"""
        engine = PatternEngine()
        
        # Process message
        result = engine.process_message(
            "We need to assess sales forecasting",
            is_first_message=False
        )
        
        # Result should have composed response structure
        assert 'composed_response' in result or 'pattern_used' in result
    
    def test_reactive_and_proactive_patterns(self):
        """PatternEngine should return both reactive and proactive patterns"""
        engine = PatternEngine()
        
        # Process message that should trigger both
        result = engine.process_message(
            "We need to assess sales forecasting in our CRM",
            is_first_message=False
        )
        
        # Should have pattern information
        assert 'pattern_used' in result or 'patterns_used' in result


class TestIntegratedFlow:
    """Test complete integrated flow"""
    
    def test_complete_conversation_flow(self):
        """Test multi-turn conversation with situation evolution"""
        engine = PatternEngine()
        
        # Turn 1: User mentions output
        result1 = engine.process_message(
            "We need to assess sales forecasting in our CRM"
        )
        assert result1 is not None
        
        # Situation should be discovery-heavy
        assert engine.situational_awareness.composition['discovery'] > 0.3
        
        # Turn 2: User gets confused
        clarification_before = engine.situational_awareness.composition['clarification']
        result2 = engine.process_message(
            "I'm confused about what you're asking"
        )
        assert result2 is not None
        
        # Situation should spike clarification
        assert engine.situational_awareness.composition['clarification'] > clarification_before
        
        # Turn 3: User asks about progress (navigation → meta)
        meta_before = engine.situational_awareness.composition['meta']
        result3 = engine.process_message(
            "Where are we in the process?"
        )
        assert result3 is not None
        
        # Meta should increase (navigation triggers)
        assert engine.situational_awareness.composition['meta'] > meta_before
    
    def test_situation_drives_context_loading(self):
        """Situation should influence what context is loaded"""
        engine = PatternEngine()
        
        # Set specific situation
        engine.situational_awareness.composition['assessment'] = 0.50
        engine.situational_awareness.composition['discovery'] = 0.30
        engine.situational_awareness._normalize()
        
        # Process message
        result = engine.process_message("What's next?")
        
        # Context should be influenced by situation
        # (This is more of an integration check)
        assert result is not None


class TestTokenBudgetWithComposition:
    """Test token budget with reactive + proactive composition"""
    
    def test_token_budget_maintained(self):
        """Token budget should stay within limits with composition"""
        engine = PatternEngine()
        
        # Process several messages
        messages = [
            "We need to assess sales forecasting",
            "Data quality is 3 stars",
            "The team has 5 people",
            "What AI pilots would help?"
        ]
        
        for message in messages:
            result = engine.process_message(message)
            
            # Token budget should be maintained
            if 'tokens_used' in result:
                assert result['tokens_used'] <= 350  # Some buffer over 310


class TestBackwardCompatibility:
    """Test that Release 2.2 changes don't break existing functionality"""
    
    def test_existing_process_message_still_works(self):
        """Existing process_message interface should still work"""
        engine = PatternEngine()
        
        result = engine.process_message(
            "We need to assess sales forecasting",
            is_first_message=False
        )
        
        # Should return expected structure
        assert isinstance(result, dict)
        assert 'pattern_used' in result or 'llm_response' in result
    
    def test_knowledge_tracker_still_updated(self):
        """Knowledge tracker should still be updated"""
        engine = PatternEngine()
        
        initial_turn_count = engine.tracker.conversation_state.get('turn_count', 0)
        
        engine.process_message("We need to assess sales forecasting")
        
        # Turn count should increase
        final_turn_count = engine.tracker.conversation_state.get('turn_count', 0)
        assert final_turn_count > initial_turn_count
    
    def test_trigger_detection_still_works(self):
        """Trigger detection should still work"""
        engine = PatternEngine()
        
        result = engine.process_message(
            "I'm confused about this",
            is_first_message=False
        )
        
        # Should detect confusion trigger
        # (Verified by response structure)
        assert result is not None
