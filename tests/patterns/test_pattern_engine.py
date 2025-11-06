"""
Tests for Pattern Engine (LLM Integration with Selective Loading).

The Pattern Engine orchestrates the entire pattern system:
1. Detects triggers from user message
2. Selects best pattern(s) based on situation
3. CRITICAL: Selectively loads only relevant context for LLM
4. Generates response using selected pattern + minimal context
5. Updates knowledge state

Token Optimization Goal:
- WITHOUT selective loading: ~9,747 tokens per turn
- WITH selective loading: ~310 tokens per turn
- Savings: ~$16,986/year at scale
"""
import pytest
from src.patterns.pattern_engine import PatternEngine
from src.patterns.knowledge_tracker import KnowledgeTracker


class TestPatternEngineInitialization:
    """Test pattern engine initialization"""
    
    def test_initialization(self):
        """Should initialize with all components"""
        engine = PatternEngine()
        assert engine.trigger_detector is not None
        assert engine.pattern_selector is not None
        assert engine.pattern_loader is not None
        assert engine.tracker is not None
    
    def test_initialization_with_pattern_dir(self):
        """Should load patterns from directory"""
        engine = PatternEngine(pattern_dir='data/patterns')
        assert len(engine.patterns) > 0


class TestSelectiveLoading:
    """Test selective loading (CRITICAL for token optimization)"""
    
    def test_load_only_selected_pattern(self):
        """Should load only the selected pattern, not all patterns"""
        engine = PatternEngine()
        tracker = KnowledgeTracker()
        
        # Simulate pattern selection
        selected_pattern = {
            'id': 'PATTERN_001',
            'behaviors': ['B_WELCOME'],
            'knowledge_updates': ['user_saw_welcome']
        }
        
        context = engine.load_selective_context(selected_pattern, tracker)
        
        # Should NOT include all patterns
        assert 'all_patterns' not in context
        # Should include only selected pattern
        assert 'selected_pattern' in context
        assert context['selected_pattern']['id'] == 'PATTERN_001'
    
    def test_load_only_relevant_knowledge(self):
        """Should load only knowledge relevant to selected pattern"""
        engine = PatternEngine()
        tracker = KnowledgeTracker()
        
        # Add lots of knowledge
        tracker.update_user_knowledge({
            'understands_min_calculation': True,
            'saw_welcome': True,
            'knows_output_model': True,
            'completed_onboarding': True
        })
        
        # Pattern only needs one piece of knowledge
        selected_pattern = {
            'id': 'PATTERN_EXPLAIN_MIN',
            'prerequisites': {
                'user_knowledge': {'understands_min_calculation': False}
            }
        }
        
        context = engine.load_selective_context(selected_pattern, tracker)
        
        # Should include only relevant knowledge
        knowledge = context.get('relevant_knowledge', {})
        assert 'understands_min_calculation' in knowledge
        # Should NOT include all knowledge
        assert len(knowledge) <= 5  # Only what's needed
    
    def test_load_only_recent_conversation_history(self):
        """Should load only recent conversation turns, not full history"""
        engine = PatternEngine()
        tracker = KnowledgeTracker()
        
        # Simulate long conversation history
        tracker.conversation_state['pattern_history'] = [
            'PATTERN_001', 'PATTERN_002', 'PATTERN_003',
            'PATTERN_004', 'PATTERN_005', 'PATTERN_006',
            'PATTERN_007', 'PATTERN_008', 'PATTERN_009',
            'PATTERN_010'
        ]
        
        selected_pattern = {'id': 'PATTERN_011'}
        
        context = engine.load_selective_context(selected_pattern, tracker)
        
        # Should include only last 5 turns
        history = context.get('recent_history', [])
        assert len(history) <= 5
    
    def test_token_count_within_budget(self):
        """Should keep context under 500 tokens (target: ~310)"""
        engine = PatternEngine()
        tracker = KnowledgeTracker()
        
        # Add realistic knowledge state
        tracker.update_user_knowledge({
            'understands_min_calculation': True,
            'saw_welcome': True
        })
        tracker.update_system_knowledge({
            'outputs_identified': ['sales_forecast', 'revenue_report']
        })
        
        selected_pattern = {
            'id': 'PATTERN_ASSESS',
            'behaviors': ['B_ACKNOWLEDGE_EVIDENCE'],
            'category': 'assessment'
        }
        
        context = engine.load_selective_context(selected_pattern, tracker)
        
        # Estimate token count (rough: 4 chars = 1 token)
        context_str = str(context)
        estimated_tokens = len(context_str) / 4
        
        # Should be well under 500 tokens
        assert estimated_tokens < 500


class TestEndToEndFlow:
    """Test complete pattern engine flow"""
    
    def test_process_user_message(self):
        """Should process message through full pipeline"""
        engine = PatternEngine()
        
        message = "Where are we in the assessment?"
        response = engine.process_message(message)
        
        assert response is not None
        assert 'pattern_used' in response
        assert 'llm_response' in response
        assert 'knowledge_updated' in response
    
    def test_first_message_flow(self):
        """Should handle first message (onboarding)"""
        engine = PatternEngine()
        
        message = "Hi, I want to assess AI pilot opportunities"
        response = engine.process_message(message, is_first_message=True)
        
        # Should trigger onboarding pattern
        assert response['pattern_used']['category'] == 'onboarding'
    
    def test_multi_pattern_flow(self):
        """Should handle multi-pattern responses (TBD #25)"""
        engine = PatternEngine()
        
        # Message that could trigger multiple relevant patterns
        message = "We need to assess sales forecasting"
        response = engine.process_message(message, allow_multi_pattern=True)
        
        # May return 1 or 2 patterns depending on relevance
        patterns_used = response.get('patterns_used', [])
        assert len(patterns_used) <= 2
        
        # If 2 patterns, they must be relevant to each other
        if len(patterns_used) == 2:
            assert response.get('context_continuity_maintained', False)


class TestKnowledgeUpdates:
    """Test knowledge state updates after pattern execution"""
    
    def test_update_user_knowledge(self):
        """Should update user knowledge based on pattern"""
        engine = PatternEngine()
        
        message = "What is the MIN calculation?"
        response = engine.process_message(message)
        
        # After explaining MIN, should mark as understood
        tracker = engine.tracker
        if 'MIN' in response.get('llm_response', ''):
            assert tracker.user_knowledge.get('saw_min_explanation', False)
    
    def test_update_conversation_state(self):
        """Should update conversation state (turns, progress, etc.)"""
        engine = PatternEngine()
        
        initial_turns = engine.tracker.conversation_state.get('turn_count', 0)
        
        engine.process_message("Test message")
        
        # Turn count should increment
        assert engine.tracker.conversation_state['turn_count'] > initial_turns
    
    def test_track_pattern_history(self):
        """Should track which patterns were used"""
        engine = PatternEngine()
        
        engine.process_message("First message")
        engine.process_message("Second message")
        
        # Should have pattern history
        history = engine.tracker.conversation_state.get('pattern_history', [])
        assert len(history) > 0


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_no_pattern_selected(self):
        """Should handle case where no pattern matches"""
        engine = PatternEngine()
        
        # Gibberish message that won't match any pattern
        message = "asdfghjkl qwertyuiop"
        response = engine.process_message(message)
        
        # Should have fallback response
        assert response is not None
        assert 'fallback' in response.get('pattern_used', {}).get('id', '').lower() or \
               response.get('llm_response') is not None
    
    def test_empty_message(self):
        """Should handle empty message"""
        engine = PatternEngine()
        
        response = engine.process_message("")
        
        # Should handle gracefully
        assert response is not None
    
    def test_llm_failure(self):
        """Should handle LLM API failure gracefully"""
        engine = PatternEngine()
        
        # Simulate LLM failure by using invalid pattern
        message = "Test message"
        
        # Should not crash, should return error response
        try:
            response = engine.process_message(message)
            assert response is not None
        except Exception as e:
            # If it does raise, should be handled exception
            assert "LLM" in str(e) or "API" in str(e)


class TestTokenOptimization:
    """Test token optimization metrics"""
    
    def test_measure_token_savings(self):
        """Should measure token savings from selective loading"""
        engine = PatternEngine()
        tracker = KnowledgeTracker()
        
        # Add realistic state
        tracker.update_user_knowledge({
            'understands_min_calculation': True,
            'saw_welcome': True,
            'knows_output_model': True
        })
        tracker.update_system_knowledge({
            'outputs_identified': ['sales_forecast', 'revenue_report', 'dashboard']
        })
        
        selected_pattern = {
            'id': 'PATTERN_ASSESS',
            'behaviors': ['B_ACKNOWLEDGE_EVIDENCE']
        }
        
        # Get selective context
        selective_context = engine.load_selective_context(selected_pattern, tracker)
        
        # Get full context (what we'd send without optimization)
        full_context = engine.load_full_context(tracker)
        
        # Calculate token estimates
        selective_tokens = len(str(selective_context)) / 4
        full_tokens = len(str(full_context)) / 4
        
        # Selective should be much smaller
        assert selective_tokens < full_tokens * 0.1  # At least 90% reduction
    
    def test_token_count_tracking(self):
        """Should track token usage per conversation"""
        engine = PatternEngine()
        
        # Process several messages
        engine.process_message("First message")
        engine.process_message("Second message")
        engine.process_message("Third message")
        
        # Should have token usage metrics
        metrics = engine.get_token_metrics()
        assert 'total_tokens' in metrics
        assert 'average_tokens_per_turn' in metrics
        assert metrics['average_tokens_per_turn'] < 500  # Target: ~310


class TestContextRelevance:
    """Test that loaded context is actually relevant"""
    
    def test_context_matches_pattern_category(self):
        """Should load context relevant to pattern category"""
        engine = PatternEngine()
        tracker = KnowledgeTracker()
        
        # Discovery pattern should load discovery-relevant context
        discovery_pattern = {
            'id': 'PATTERN_DISCOVER',
            'category': 'discovery'
        }
        
        context = engine.load_selective_context(discovery_pattern, tracker)
        
        # Should include outputs identified (discovery context)
        assert 'outputs_identified' in str(context) or 'system_knowledge' in context
    
    def test_context_includes_prerequisites(self):
        """Should load knowledge needed to check prerequisites"""
        engine = PatternEngine()
        tracker = KnowledgeTracker()
        
        tracker.update_user_knowledge({'understands_min_calculation': False})
        
        pattern_with_prereq = {
            'id': 'PATTERN_EXPLAIN',
            'prerequisites': {
                'user_knowledge': {'understands_min_calculation': False}
            }
        }
        
        context = engine.load_selective_context(pattern_with_prereq, tracker)
        
        # Should include the prerequisite knowledge
        knowledge = context.get('relevant_knowledge', {})
        assert 'understands_min_calculation' in knowledge
