"""
Tests for PatternEngine LLM Integration (Day 10 - Release 2.2)

Tests the integration of LLMResponseGenerator into PatternEngine.
"""
import pytest
from unittest.mock import Mock, patch
from src.patterns.pattern_engine import PatternEngine


class TestPatternEngineLLMIntegration:
    """Test PatternEngine with LLM response generation"""
    
    @patch('src.patterns.pattern_engine.LLMResponseGenerator')
    def test_pattern_engine_uses_llm_generator(self, mock_llm_class):
        """Should initialize LLMResponseGenerator"""
        mock_generator = Mock()
        mock_llm_class.return_value = mock_generator
        
        engine = PatternEngine()
        
        # Should have llm_generator attribute
        assert hasattr(engine, 'llm_generator')
    
    @patch('src.patterns.pattern_engine.LLMResponseGenerator')
    @patch('src.patterns.pattern_engine.TriggerDetector')
    def test_process_message_generates_llm_response(self, mock_trigger_class, mock_llm_class):
        """Should generate LLM response when processing message"""
        # Setup LLM mock
        mock_generator = Mock()
        mock_generator.generate_response.return_value = "Generated LLM response"
        mock_llm_class.return_value = mock_generator
        
        # Setup trigger detector mock
        mock_detector = Mock()
        mock_detector.detect.return_value = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        mock_trigger_class.return_value = mock_detector
        
        engine = PatternEngine()
        
        # Add a simple pattern
        engine.patterns = [{
            'id': 'PATTERN_TEST',
            'category': 'discovery',
            'triggers': ['T_MENTION_OUTPUT'],
            'response_type': 'reactive',
            'behaviors': ['B_ACKNOWLEDGE_OUTPUT'],
            'situation_affinity': {'discovery': 0.8},
            'prerequisites': {}
        }]
        
        # Reinitialize selector with patterns
        from src.patterns.pattern_selector import PatternSelector
        engine.pattern_selector = PatternSelector(engine.patterns)
        
        # Process message
        result = engine.process_message("We need to assess sales forecasting")
        
        # Should call LLM generator
        assert mock_generator.generate_response.called
        
        # Should return LLM response
        assert result['llm_response'] == "Generated LLM response"
    
    @patch('src.patterns.pattern_engine.LLMResponseGenerator')
    @patch('src.patterns.pattern_engine.TriggerDetector')
    def test_llm_receives_composed_response(self, mock_trigger_class, mock_llm_class):
        """Should pass ComposedResponse to LLM generator"""
        # Setup LLM mock
        mock_generator = Mock()
        mock_generator.generate_response.return_value = "Test response"
        mock_llm_class.return_value = mock_generator
        
        # Setup trigger detector mock
        mock_detector = Mock()
        mock_detector.detect.return_value = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        mock_trigger_class.return_value = mock_detector
        
        engine = PatternEngine()
        
        # Add patterns (reactive + proactive)
        engine.patterns = [
            {
                'id': 'PATTERN_REACTIVE',
                'category': 'discovery',
                'triggers': ['T_MENTION_OUTPUT'],
                'response_type': 'reactive',
                'behaviors': ['B_ACKNOWLEDGE_OUTPUT'],
                'situation_affinity': {'discovery': 0.8},
                'prerequisites': {}
            },
            {
                'id': 'PATTERN_PROACTIVE',
                'category': 'context_extraction',
                'response_type': 'proactive',
                'behaviors': ['B_ASK_TIMELINE'],
                'situation_affinity': {'context_extraction': 0.9},
                'prerequisites': {}
            }
        ]
        
        from src.patterns.pattern_selector import PatternSelector
        engine.pattern_selector = PatternSelector(engine.patterns)
        
        # Process message
        engine.process_message("We need to assess sales forecasting")
        
        # Check that generate_response was called
        assert mock_generator.generate_response.called
        
        # Get the call arguments
        call_args = mock_generator.generate_response.call_args
        composed_response = call_args[0][0]
        context = call_args[0][1]
        
        # Should have ComposedResponse structure
        assert hasattr(composed_response, 'reactive')
        assert hasattr(composed_response, 'proactive')
        assert hasattr(composed_response, 'total_tokens')
        
        # Context should have required fields
        assert 'message' in context
        assert 'relevant_knowledge' in context
        assert 'conversation_state' in context
    
    @patch('src.patterns.pattern_engine.LLMResponseGenerator')
    @patch('src.patterns.pattern_engine.TriggerDetector')
    def test_llm_receives_selective_context(self, mock_trigger_class, mock_llm_class):
        """Should pass selective context (not full context) to LLM"""
        # Setup LLM mock
        mock_generator = Mock()
        mock_generator.generate_response.return_value = "Test response"
        mock_llm_class.return_value = mock_generator
        
        # Setup trigger detector mock
        mock_detector = Mock()
        mock_detector.detect.return_value = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        mock_trigger_class.return_value = mock_detector
        
        engine = PatternEngine()
        
        # Add pattern
        engine.patterns = [{
            'id': 'PATTERN_TEST',
            'category': 'discovery',
            'triggers': ['T_MENTION_OUTPUT'],
            'response_type': 'reactive',
            'behaviors': ['B_ACKNOWLEDGE_OUTPUT'],
            'situation_affinity': {'discovery': 0.8},
            'prerequisites': {}
        }]
        
        from src.patterns.pattern_selector import PatternSelector
        engine.pattern_selector = PatternSelector(engine.patterns)
        
        # Process message
        engine.process_message("We need to assess sales forecasting")
        
        # Get context passed to LLM
        call_args = mock_generator.generate_response.call_args
        context = call_args[0][1]
        
        # Should have selective context (not full patterns list)
        assert 'all_patterns' not in context
        assert 'all_user_knowledge' not in context
        assert 'full_conversation_state' not in context
        
        # Should have minimal context
        assert 'relevant_knowledge' in context
        assert 'conversation_state' in context


class TestLLMFallback:
    """Test LLM fallback behavior"""
    
    @patch('src.patterns.pattern_engine.LLMResponseGenerator')
    def test_fallback_on_llm_error(self, mock_llm_class):
        """Should handle LLM errors gracefully"""
        # Setup mock to raise error
        mock_generator = Mock()
        mock_generator.generate_response.side_effect = Exception("LLM Error")
        mock_llm_class.return_value = mock_generator
        
        engine = PatternEngine()
        
        # Add pattern
        engine.patterns = [{
            'id': 'PATTERN_TEST',
            'category': 'discovery',
            'triggers': ['T_MENTION_OUTPUT'],
            'response_type': 'reactive',
            'behaviors': ['B_ACKNOWLEDGE_OUTPUT'],
            'situation_affinity': {'discovery': 0.8},
            'prerequisites': {}
        }]
        
        from src.patterns.pattern_selector import PatternSelector
        engine.pattern_selector = PatternSelector(engine.patterns)
        
        # Process message - should not crash
        result = engine.process_message("We need to assess sales forecasting")
        
        # Should return fallback response
        assert 'llm_response' in result
        assert result['llm_response'] is not None
        assert len(result['llm_response']) > 0
