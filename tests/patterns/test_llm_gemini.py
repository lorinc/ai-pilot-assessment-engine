"""
Tests for LLM Response Generation with Gemini (Day 10 - Release 2.2 Refactored)

Tests the LLM integration using Gemini via existing LLMClient.

Note: These tests use mocked LLMClient for unit testing.
For real Gemini API testing, see demo_llm_real_gemini.py
"""
import pytest
from unittest.mock import Mock
from src.patterns.llm_response_generator import LLMResponseGenerator
from src.patterns.response_composer import ResponseComponent, ComposedResponse


class TestLLMPromptBuilderGemini:
    """Test prompt building for Gemini format"""
    
    def test_build_prompt_includes_system_role(self):
        """Should include system role at top (Gemini format)"""
        mock_client = Mock()
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(reactive=reactive, proactive=[], total_tokens=150)
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        prompt = generator.build_prompt(composed, context)
        
        # Gemini format: system role at top
        assert prompt.startswith('# System Role') or 'System Role' in prompt[:200]
    
    def test_build_prompt_includes_reactive_pattern(self):
        """Should include reactive pattern information"""
        mock_client = Mock()
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'behaviors': ['B_ACKNOWLEDGE_OUTPUT']
            },
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(reactive=reactive, proactive=[], total_tokens=150)
        context = {'message': 'We need to assess sales forecasting', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        prompt = generator.build_prompt(composed, context)
        
        assert 'PATTERN_IDENTIFY_OUTPUT' in prompt
        assert 'discovery' in prompt
        assert 'B_ACKNOWLEDGE_OUTPUT' in prompt
        assert 'sales forecasting' in prompt
    
    def test_build_prompt_includes_proactive_patterns(self):
        """Should include proactive patterns when present"""
        mock_client = Mock()
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_REACTIVE', 'category': 'discovery', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        proactive_1 = ResponseComponent(
            type='proactive',
            pattern={'id': 'PATTERN_PROACTIVE_1', 'category': 'context_extraction', 'behaviors': []},
            priority='medium',
            token_budget=100
        )
        
        composed = ComposedResponse(reactive=reactive, proactive=[proactive_1], total_tokens=250)
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        prompt = generator.build_prompt(composed, context)
        
        assert 'PATTERN_REACTIVE' in prompt
        assert 'PATTERN_PROACTIVE_1' in prompt
        assert 'REACTIVE' in prompt
        assert 'PROACTIVE' in prompt


class TestLLMResponseGenerationGemini:
    """Test actual response generation with Gemini"""
    
    def test_generate_response_calls_llm_client(self):
        """Should call LLMClient.generate() with correct parameters"""
        mock_client = Mock()
        mock_client.generate.return_value = "Test response from Gemini"
        
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(reactive=reactive, proactive=[], total_tokens=150)
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        response = generator.generate_response(composed, context)
        
        # Should call LLMClient.generate
        assert mock_client.generate.called
        
        # Should return response
        assert response == "Test response from Gemini"
    
    def test_generate_response_passes_token_budget(self):
        """Should pass max_output_tokens to LLMClient"""
        mock_client = Mock()
        mock_client.generate.return_value = "Test response"
        
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(reactive=reactive, proactive=[], total_tokens=150)
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        generator.generate_response(composed, context)
        
        # Check call arguments
        call_args = mock_client.generate.call_args
        assert 'max_output_tokens' in call_args.kwargs
        # Should be ~150 with 20% buffer = 180
        assert 150 <= call_args.kwargs['max_output_tokens'] <= 200
    
    def test_generate_response_handles_errors(self):
        """Should handle LLM errors gracefully"""
        mock_client = Mock()
        mock_client.generate.side_effect = Exception("Gemini API Error")
        
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(reactive=reactive, proactive=[], total_tokens=150)
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        response = generator.generate_response(composed, context)
        
        # Should return fallback message
        assert response is not None
        assert len(response) > 0
        assert 'error' in response.lower() or 'sorry' in response.lower()


class TestPromptOptimization:
    """Test prompt optimization for token efficiency"""
    
    def test_prompt_is_reasonably_sized(self):
        """Should generate reasonably sized prompts"""
        mock_client = Mock()
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': ['B_TEST']},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(reactive=reactive, proactive=[], total_tokens=150)
        context = {
            'message': 'test message',
            'relevant_knowledge': {'key': 'value'},
            'conversation_state': {'turn_count': 1}
        }
        
        prompt = generator.build_prompt(composed, context)
        
        # Prompt should be < 5000 characters for simple case
        assert len(prompt) < 5000
