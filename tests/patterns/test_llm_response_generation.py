"""
Tests for LLM Response Generation (Day 10 - Release 2.2)

Tests the LLM integration that generates actual responses from composed components.

TDD RED Phase: These tests define the desired behavior before implementation.

Note: Refactored to use Gemini (via LLMClient) instead of OpenAI.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.patterns.llm_response_generator import LLMResponseGenerator
from src.patterns.response_composer import ResponseComponent, ComposedResponse


@pytest.fixture
def mock_llm_client():
    """Fixture to provide mocked LLMClient"""
    return Mock()


class TestLLMPromptBuilder:
    """Test prompt building for reactive + proactive composition"""
    
    def test_build_reactive_only_prompt(self):
        """Should build prompt for reactive-only response"""
        # Mock LLMClient to avoid GCP initialization
        mock_client = Mock()
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'behaviors': ['B_ACKNOWLEDGE_OUTPUT', 'B_CONFIRM_UNDERSTANDING']
            },
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        context = {
            'message': 'We need to assess sales forecasting',
            'relevant_knowledge': {},
            'conversation_state': {'turn_count': 1}
        }
        
        prompt = generator.build_prompt(composed, context)
        
        # Should contain system role (Gemini format)
        assert 'System Role' in prompt or 'system' in prompt.lower()
        
        # Should contain reactive pattern info
        assert 'PATTERN_IDENTIFY_OUTPUT' in prompt
        assert 'discovery' in prompt
        assert 'B_ACKNOWLEDGE_OUTPUT' in prompt
        
        # Should contain message
        assert 'sales forecasting' in prompt
        
        # Should have reactive section
        assert 'REACTIVE' in prompt
    
    def test_build_reactive_plus_proactive_prompt(self):
        """Should build prompt for reactive + proactive response"""
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
        
        proactive_1 = ResponseComponent(
            type='proactive',
            pattern={
                'id': 'PATTERN_EXTRACT_TIMELINE',
                'category': 'context_extraction',
                'behaviors': ['B_ASK_TIMELINE']
            },
            priority='medium',
            token_budget=100
        )
        
        proactive_2 = ResponseComponent(
            type='proactive',
            pattern={
                'id': 'PATTERN_ASK_BUDGET',
                'category': 'context_extraction',
                'behaviors': ['B_ASK_BUDGET']
            },
            priority='low',
            token_budget=60
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[proactive_1, proactive_2],
            total_tokens=310
        )
        
        context = {
            'message': 'We need to assess sales forecasting',
            'relevant_knowledge': {},
            'conversation_state': {'turn_count': 1}
        }
        
        prompt = generator.build_prompt(composed, context)
        
        # Should contain reactive pattern
        assert 'PATTERN_IDENTIFY_OUTPUT' in prompt
        
        # Should contain both proactive patterns
        assert 'PATTERN_EXTRACT_TIMELINE' in prompt
        assert 'PATTERN_ASK_BUDGET' in prompt
        
        # Should indicate sequential composition
        assert 'first' in prompt.lower() or 'then' in prompt.lower() or 'also' in prompt.lower()
    
    def test_prompt_includes_token_budgets(self):
        """Should include token budget constraints in prompt"""
        mock_client = Mock()
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        prompt = generator.build_prompt(composed, context)
        
        # Should mention token budget
        assert '150' in prompt or 'token' in prompt.lower()
    
    def test_prompt_includes_relevant_knowledge(self):
        """Should include relevant knowledge in prompt"""
        mock_client = Mock()
        generator = LLMResponseGenerator(llm_client=mock_client)
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'assessment', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        context = {
            'message': 'test',
            'relevant_knowledge': {
                'output_identified': True,
                'current_ratings': {'data_quality': 3}
            },
            'conversation_state': {'turn_count': 5}
        }
        
        prompt = generator.build_prompt(composed, context)
        
        # Should include knowledge
        assert 'output_identified' in prompt or 'output' in prompt.lower()
        assert 'data_quality' in prompt or '3' in prompt


class TestLLMResponseGeneration:
    """Test actual LLM response generation"""
    
    @patch('src.patterns.llm_response_generator.OpenAI')
    def test_generate_response_calls_openai(self, mock_openai_class):
        """Should call OpenAI API with correct parameters"""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        generator = LLMResponseGenerator()
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        response = generator.generate_response(composed, context)
        
        # Should call OpenAI
        assert mock_client.chat.completions.create.called
        
        # Should return response
        assert response == "Test response"
    
    @patch('src.patterns.llm_response_generator.OpenAI')
    def test_generate_response_uses_gpt4(self, mock_openai_class):
        """Should use GPT-4 model for quality responses"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        generator = LLMResponseGenerator()
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        generator.generate_response(composed, context)
        
        # Check model parameter
        call_args = mock_client.chat.completions.create.call_args
        assert 'gpt-4' in call_args.kwargs.get('model', '')
    
    @patch('src.patterns.llm_response_generator.OpenAI')
    def test_generate_response_respects_token_budget(self, mock_openai_class):
        """Should set max_tokens based on composition budget"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        generator = LLMResponseGenerator()
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        proactive_1 = ResponseComponent(
            type='proactive',
            pattern={'id': 'PATTERN_TEST2', 'category': 'test', 'behaviors': []},
            priority='medium',
            token_budget=100
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[proactive_1],
            total_tokens=250
        )
        
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        generator.generate_response(composed, context)
        
        # Check max_tokens parameter
        call_args = mock_client.chat.completions.create.call_args
        max_tokens = call_args.kwargs.get('max_tokens', 0)
        
        # Should be around 250 (with some buffer)
        assert 200 <= max_tokens <= 350
    
    @patch('src.patterns.llm_response_generator.OpenAI')
    def test_generate_response_handles_errors(self, mock_openai_class):
        """Should handle OpenAI API errors gracefully"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Simulate API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        generator = LLMResponseGenerator()
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_TEST', 'category': 'test', 'behaviors': []},
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        context = {'message': 'test', 'relevant_knowledge': {}, 'conversation_state': {}}
        
        response = generator.generate_response(composed, context)
        
        # Should return fallback message
        assert response is not None
        assert 'error' in response.lower() or 'sorry' in response.lower()


class TestSequentialComposition:
    """Test sequential composition of reactive + proactive responses"""
    
    @patch('src.patterns.llm_response_generator.OpenAI')
    def test_sequential_composition_structure(self, mock_openai_class):
        """Should generate response with clear reactive → proactive structure"""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Mock response with clear structure
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = (
            "Got it - you're talking about Sales Forecasts. "
            "When do you need this assessment completed?"
        )
        mock_client.chat.completions.create.return_value = mock_response
        
        generator = LLMResponseGenerator()
        
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
        
        proactive_1 = ResponseComponent(
            type='proactive',
            pattern={
                'id': 'PATTERN_EXTRACT_TIMELINE',
                'category': 'context_extraction',
                'behaviors': ['B_ASK_TIMELINE']
            },
            priority='medium',
            token_budget=100
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[proactive_1],
            total_tokens=250
        )
        
        context = {
            'message': 'We need to assess sales forecasting',
            'relevant_knowledge': {},
            'conversation_state': {'turn_count': 1}
        }
        
        response = generator.generate_response(composed, context)
        
        # Should have both parts
        assert len(response) > 0
        assert 'sales' in response.lower() or 'forecast' in response.lower()


class TestPromptOptimization:
    """Test prompt optimization for token efficiency"""
    
    def test_prompt_is_concise(self):
        """Should generate concise prompts (not verbose)"""
        generator = LLMResponseGenerator()
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={
                'id': 'PATTERN_TEST',
                'category': 'test',
                'behaviors': ['B_TEST']
            },
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        context = {
            'message': 'test message',
            'relevant_knowledge': {'key': 'value'},
            'conversation_state': {'turn_count': 1}
        }
        
        prompt = generator.build_prompt(composed, context)
        
        # Rough estimate: prompt should be < 1000 tokens (4000 chars)
        assert len(prompt) < 4000
    
    def test_prompt_excludes_unnecessary_details(self):
        """Should not include unnecessary implementation details"""
        generator = LLMResponseGenerator()
        
        reactive = ResponseComponent(
            type='reactive',
            pattern={
                'id': 'PATTERN_TEST',
                'category': 'test',
                'behaviors': ['B_TEST']
            },
            priority='high',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        context = {
            'message': 'test',
            'relevant_knowledge': {},
            'conversation_state': {'turn_count': 1}
        }
        
        prompt = generator.build_prompt(composed, context)
        
        # Should not include implementation details
        assert 'ResponseComponent' not in prompt
        assert 'ComposedResponse' not in prompt
        assert 'token_budget' not in prompt.lower() or 'within' in prompt.lower()
