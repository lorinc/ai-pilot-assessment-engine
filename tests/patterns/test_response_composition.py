"""
Tests for response composition (reactive + proactive architecture)

TDD RED phase - tests written first to define behavior
"""
import pytest
from src.patterns.response_composer import (
    ResponseComponent,
    ComposedResponse,
    ResponseComposer
)


class TestResponseComponent:
    """Test response component data model"""
    
    def test_create_reactive_component(self):
        """Should create reactive response component"""
        component = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_001', 'category': 'discovery'},
            priority='critical',
            token_budget=150
        )
        
        assert component.type == 'reactive'
        assert component.pattern['id'] == 'PATTERN_001'
        assert component.priority == 'critical'
        assert component.token_budget == 150
    
    def test_create_proactive_component(self):
        """Should create proactive response component"""
        component = ResponseComponent(
            type='proactive',
            pattern={'id': 'PATTERN_002', 'category': 'context_extraction'},
            priority='medium',
            token_budget=100
        )
        
        assert component.type == 'proactive'
        assert component.pattern['id'] == 'PATTERN_002'
        assert component.priority == 'medium'
        assert component.token_budget == 100


class TestComposedResponse:
    """Test composed response model"""
    
    def test_create_composed_response_reactive_only(self):
        """Should create composed response with only reactive component"""
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_001'},
            priority='critical',
            token_budget=150
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[],
            total_tokens=150
        )
        
        assert composed.reactive == reactive
        assert len(composed.proactive) == 0
        assert composed.total_tokens == 150
    
    def test_create_composed_response_with_proactive(self):
        """Should create composed response with reactive + proactive"""
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_001'},
            priority='critical',
            token_budget=150
        )
        
        proactive1 = ResponseComponent(
            type='proactive',
            pattern={'id': 'PATTERN_002'},
            priority='medium',
            token_budget=100
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[proactive1],
            total_tokens=250
        )
        
        assert composed.reactive == reactive
        assert len(composed.proactive) == 1
        assert composed.proactive[0] == proactive1
        assert composed.total_tokens == 250
    
    def test_create_composed_response_with_two_proactive(self):
        """Should create composed response with reactive + 2 proactive"""
        reactive = ResponseComponent(
            type='reactive',
            pattern={'id': 'PATTERN_001'},
            priority='critical',
            token_budget=150
        )
        
        proactive1 = ResponseComponent(
            type='proactive',
            pattern={'id': 'PATTERN_002'},
            priority='medium',
            token_budget=100
        )
        
        proactive2 = ResponseComponent(
            type='proactive',
            pattern={'id': 'PATTERN_003'},
            priority='low',
            token_budget=60
        )
        
        composed = ComposedResponse(
            reactive=reactive,
            proactive=[proactive1, proactive2],
            total_tokens=310
        )
        
        assert composed.reactive == reactive
        assert len(composed.proactive) == 2
        assert composed.total_tokens == 310


class TestResponseComposer:
    """Test response composer (selects and composes responses)"""
    
    def test_select_reactive_only(self):
        """Should select only reactive component when no proactive opportunities"""
        composer = ResponseComposer()
        
        triggers = [
            {'trigger_id': 'CONFUSION_DETECTED', 'priority': 'critical', 'category': 'error_recovery'}
        ]
        
        situation = {
            'error_recovery': 0.60,
            'discovery': 0.20,
            'navigation': 0.20
        }
        
        patterns = [
            {
                'id': 'PATTERN_CONFUSION',
                'category': 'error_recovery',
                'response_type': 'reactive',
                'triggers': ['CONFUSION_DETECTED']
            }
        ]
        
        composed = composer.select_components(triggers, situation, patterns)
        
        assert composed.reactive is not None
        assert composed.reactive.type == 'reactive'
        assert len(composed.proactive) == 0
    
    def test_select_reactive_plus_one_proactive(self):
        """Should select reactive + 1 proactive when opportunity exists"""
        composer = ResponseComposer()
        
        triggers = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        
        situation = {
            'discovery': 0.50,
            'context_extraction': 0.30,
            'navigation': 0.20
        }
        
        patterns = [
            {
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'response_type': 'reactive',
                'triggers': ['T_MENTION_OUTPUT']
            },
            {
                'id': 'PATTERN_EXTRACT_TIMELINE',
                'category': 'context_extraction',
                'response_type': 'proactive',
                'situation_affinity': {'context_extraction': 0.9}
            }
        ]
        
        composed = composer.select_components(triggers, situation, patterns)
        
        assert composed.reactive is not None
        assert composed.reactive.pattern['id'] == 'PATTERN_IDENTIFY_OUTPUT'
        assert len(composed.proactive) == 1
        assert composed.proactive[0].pattern['id'] == 'PATTERN_EXTRACT_TIMELINE'
    
    def test_select_reactive_plus_two_proactive(self):
        """Should select reactive + 2 proactive when multiple opportunities"""
        composer = ResponseComposer()
        
        triggers = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        
        situation = {
            'discovery': 0.40,
            'context_extraction': 0.35,
            'assessment': 0.25
        }
        
        patterns = [
            {
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'response_type': 'reactive',
                'triggers': ['T_MENTION_OUTPUT']
            },
            {
                'id': 'PATTERN_EXTRACT_TIMELINE',
                'category': 'context_extraction',
                'response_type': 'proactive',
                'situation_affinity': {'context_extraction': 0.9}
            },
            {
                'id': 'PATTERN_ASK_TEAM',
                'category': 'assessment',
                'response_type': 'proactive',
                'situation_affinity': {'assessment': 0.8}
            }
        ]
        
        composed = composer.select_components(triggers, situation, patterns)
        
        assert composed.reactive is not None
        assert len(composed.proactive) == 2
        assert composed.total_tokens <= 310  # Token budget constraint
    
    def test_prevent_context_jumping(self):
        """Should not select proactive from same category as reactive"""
        composer = ResponseComposer()
        
        triggers = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        
        situation = {
            'discovery': 0.60,
            'context_extraction': 0.40
        }
        
        patterns = [
            {
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'response_type': 'reactive',
                'triggers': ['T_MENTION_OUTPUT']
            },
            {
                'id': 'PATTERN_ASK_MORE_OUTPUTS',
                'category': 'discovery',  # Same category!
                'response_type': 'proactive',
                'situation_affinity': {'discovery': 0.9}
            },
            {
                'id': 'PATTERN_EXTRACT_TIMELINE',
                'category': 'context_extraction',
                'response_type': 'proactive',
                'situation_affinity': {'context_extraction': 0.8}
            }
        ]
        
        composed = composer.select_components(triggers, situation, patterns)
        
        # Should select context_extraction, not discovery (same category as reactive)
        assert len(composed.proactive) == 1
        assert composed.proactive[0].pattern['category'] != 'discovery'
    
    def test_token_budget_constraint(self):
        """Should respect total token budget of ~310 tokens"""
        composer = ResponseComposer()
        
        triggers = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        
        situation = {
            'discovery': 0.40,
            'context_extraction': 0.30,
            'assessment': 0.30
        }
        
        patterns = [
            {
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'response_type': 'reactive'
            },
            {
                'id': 'PATTERN_EXTRACT_TIMELINE',
                'category': 'context_extraction',
                'response_type': 'proactive'
            },
            {
                'id': 'PATTERN_ASK_TEAM',
                'category': 'assessment',
                'response_type': 'proactive'
            }
        ]
        
        composed = composer.select_components(triggers, situation, patterns)
        
        # Total tokens should not exceed 310
        assert composed.total_tokens <= 310
        # Reactive gets ~150, proactive 1 gets ~100, proactive 2 gets ~60
        assert composed.reactive.token_budget == 150
        if len(composed.proactive) >= 1:
            assert composed.proactive[0].token_budget == 100
        if len(composed.proactive) >= 2:
            assert composed.proactive[1].token_budget == 60
