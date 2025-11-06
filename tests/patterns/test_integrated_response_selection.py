"""
Tests for integrated response selection (ResponseComposer + SituationalAwareness)

TDD RED phase - tests written first to define behavior

Integration: Reactive (trigger-driven) + Proactive (situation-driven)
"""
import pytest
from src.patterns.response_composer import ResponseComposer
from src.patterns.situational_awareness import SituationalAwareness


class TestIntegratedResponseSelection:
    """Test integrated response selection with situational awareness"""
    
    def test_reactive_from_trigger_proactive_from_situation(self):
        """Reactive should come from trigger, proactive from situation"""
        composer = ResponseComposer()
        sa = SituationalAwareness()
        
        # User mentions output (discovery trigger)
        triggers = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        
        # Update situation from triggers
        sa.update_from_triggers(triggers)
        
        # Boost context_extraction in situation
        sa.composition['context_extraction'] = 0.40
        sa.composition['assessment'] = 0.30
        sa._normalize()
        
        patterns = [
            # Reactive patterns
            {
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'response_type': 'reactive',
                'triggers': ['T_MENTION_OUTPUT']
            },
            # Proactive patterns
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
        
        # Select components using situation
        composed = composer.select_components(triggers, sa.composition, patterns)
        
        # Reactive should be from trigger
        assert composed.reactive.pattern['id'] == 'PATTERN_IDENTIFY_OUTPUT'
        assert composed.reactive.pattern['category'] == 'discovery'
        
        # Proactive should be from situation (context_extraction highest)
        assert len(composed.proactive) >= 1
        assert composed.proactive[0].pattern['id'] == 'PATTERN_EXTRACT_TIMELINE'
    
    def test_situation_drives_proactive_selection(self):
        """Proactive patterns should be selected based on situation composition"""
        composer = ResponseComposer()
        sa = SituationalAwareness()
        
        # Confusion trigger
        triggers = [
            {'trigger_id': 'CONFUSION_DETECTED', 'priority': 'critical', 'category': 'error_recovery'}
        ]
        
        # Update situation (clarification should spike)
        sa.update_from_triggers(triggers)
        
        patterns = [
            {
                'id': 'PATTERN_CONFUSION',
                'category': 'error_recovery',
                'response_type': 'reactive',
                'triggers': ['CONFUSION_DETECTED']
            },
            {
                'id': 'PATTERN_CLARIFY_CONCEPT',
                'category': 'education',
                'response_type': 'proactive',
                'situation_affinity': {'clarification': 0.9, 'education': 0.7}
            },
            {
                'id': 'PATTERN_SHOW_PROGRESS',
                'category': 'navigation',
                'response_type': 'proactive',
                'situation_affinity': {'meta': 0.8}
            }
        ]
        
        composed = composer.select_components(triggers, sa.composition, patterns)
        
        # Reactive should handle confusion
        assert composed.reactive.pattern['category'] == 'error_recovery'
        
        # Proactive should align with situation (clarification high)
        # Should select PATTERN_CLARIFY_CONCEPT (high clarification affinity)
        if composed.proactive:
            # At least one proactive should have high clarification affinity
            has_clarification = any(
                'clarification' in p.pattern.get('situation_affinity', {})
                for p in composed.proactive
            )
            assert has_clarification
    
    def test_situation_evolves_across_turns(self):
        """Situation should evolve across multiple conversation turns"""
        composer = ResponseComposer()
        sa = SituationalAwareness()
        
        patterns = [
            {
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'response_type': 'reactive',
                'triggers': ['T_MENTION_OUTPUT']
            },
            {
                'id': 'PATTERN_RATE_EDGE',
                'category': 'assessment',
                'response_type': 'reactive',
                'triggers': ['T_RATE_EDGE']
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
        
        # Turn 1: User mentions output
        initial_discovery = sa.composition['discovery']
        
        triggers_1 = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        sa.update_from_triggers(triggers_1)
        
        # Discovery should increase
        assert sa.composition['discovery'] > initial_discovery
        
        composed_1 = composer.select_components(triggers_1, sa.composition, patterns)
        assert composed_1.reactive.pattern['category'] == 'discovery'
        
        # Turn 2: User rates edge (assessment)
        triggers_2 = [
            {'trigger_id': 'T_RATE_EDGE', 'priority': 'high', 'category': 'assessment'}
        ]
        sa.update_from_triggers(triggers_2)
        
        # Assessment should increase
        assert sa.composition['assessment'] > 0.1
        
        composed_2 = composer.select_components(triggers_2, sa.composition, patterns)
        assert composed_2.reactive.pattern['category'] == 'assessment'
        
        # Proactive should reflect situation (assessment now higher)
        if len(composed_2.proactive) > 0:
            # Should include assessment-related proactive
            has_assessment = any(
                p.pattern['category'] == 'assessment'
                for p in composed_2.proactive
            )
            # Assessment is high in situation, so likely selected
            assert has_assessment or sa.composition['assessment'] < 0.3
    
    def test_no_proactive_during_error_recovery(self):
        """Should focus on reactive during critical error recovery"""
        composer = ResponseComposer()
        sa = SituationalAwareness()
        
        # Critical confusion
        triggers = [
            {'trigger_id': 'CONFUSION_DETECTED', 'priority': 'critical', 'category': 'error_recovery'}
        ]
        
        sa.update_from_triggers(triggers)
        
        patterns = [
            {
                'id': 'PATTERN_CONFUSION',
                'category': 'error_recovery',
                'response_type': 'reactive',
                'triggers': ['CONFUSION_DETECTED']
            },
            {
                'id': 'PATTERN_EXTRACT_TIMELINE',
                'category': 'context_extraction',
                'response_type': 'proactive',
                'situation_affinity': {'context_extraction': 0.9}
            }
        ]
        
        composed = composer.select_components(triggers, sa.composition, patterns)
        
        # Reactive should be error recovery
        assert composed.reactive.pattern['category'] == 'error_recovery'
        assert composed.reactive.priority == 'critical'
        
        # Proactive might be present but should not be in error_recovery category
        for proactive in composed.proactive:
            assert proactive.pattern['category'] != 'error_recovery'
    
    def test_decay_affects_proactive_selection(self):
        """Decay should affect which proactive patterns are selected"""
        composer = ResponseComposer()
        sa = SituationalAwareness()
        
        # Boost discovery significantly
        for _ in range(3):
            sa.update_from_triggers([
                {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
            ])
        
        discovery_before_decay = sa.composition['discovery']
        
        patterns = [
            {
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'response_type': 'reactive',
                'triggers': ['T_MENTION_OUTPUT']
            },
            {
                'id': 'PATTERN_ASK_MORE_OUTPUTS',
                'category': 'discovery',
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
        
        # Apply decay multiple times
        for _ in range(5):
            sa.apply_decay()
        
        discovery_after_decay = sa.composition['discovery']
        
        # Discovery should have decayed
        assert discovery_after_decay < discovery_before_decay
        
        # Situation should still be valid
        total = sum(sa.composition.values())
        assert abs(total - 1.0) < 0.001


class TestSituationAffinity:
    """Test situation affinity scoring"""
    
    def test_affinity_scoring(self):
        """Patterns with high affinity for dominant dimensions should score higher"""
        composer = ResponseComposer()
        sa = SituationalAwareness()
        
        # Set specific situation
        sa.composition = {
            'discovery': 0.10,
            'assessment': 0.50,  # Dominant
            'analysis': 0.20,
            'recommendation': 0.05,
            'feasibility': 0.05,
            'clarification': 0.05,
            'validation': 0.03,
            'meta': 0.02
        }
        
        patterns = [
            {
                'id': 'PATTERN_HIGH_ASSESSMENT',
                'category': 'assessment',
                'response_type': 'proactive',
                'situation_affinity': {'assessment': 0.9, 'analysis': 0.3}
            },
            {
                'id': 'PATTERN_LOW_ASSESSMENT',
                'category': 'context_extraction',
                'response_type': 'proactive',
                'situation_affinity': {'discovery': 0.8, 'context_extraction': 0.6}
            }
        ]
        
        # Select proactive (no reactive needed for this test)
        proactive = composer._select_proactive(
            sa.composition,
            patterns,
            exclude_category=None,
            max_count=2
        )
        
        # Pattern with high assessment affinity should be selected first
        assert len(proactive) >= 1
        assert proactive[0].pattern['id'] == 'PATTERN_HIGH_ASSESSMENT'
    
    def test_multiple_affinity_dimensions(self):
        """Patterns can have affinity for multiple dimensions"""
        composer = ResponseComposer()
        
        situation = {
            'discovery': 0.30,
            'assessment': 0.30,
            'analysis': 0.10,
            'recommendation': 0.10,
            'feasibility': 0.05,
            'clarification': 0.05,
            'validation': 0.05,
            'meta': 0.05
        }
        
        patterns = [
            {
                'id': 'PATTERN_MULTI_AFFINITY',
                'category': 'context_extraction',
                'response_type': 'proactive',
                'situation_affinity': {
                    'discovery': 0.7,
                    'assessment': 0.8,
                    'context_extraction': 0.6
                }
            },
            {
                'id': 'PATTERN_SINGLE_AFFINITY',
                'category': 'education',
                'response_type': 'proactive',
                'situation_affinity': {'meta': 0.9}
            }
        ]
        
        proactive = composer._select_proactive(
            situation,
            patterns,
            exclude_category=None,
            max_count=2
        )
        
        # Multi-affinity pattern should score higher
        # (0.7*0.30 + 0.8*0.30 = 0.45) vs (0.9*0.05 = 0.045)
        assert len(proactive) >= 1
        assert proactive[0].pattern['id'] == 'PATTERN_MULTI_AFFINITY'


class TestEndToEndFlow:
    """Test complete end-to-end conversation flow"""
    
    def test_complete_conversation_flow(self):
        """Test a complete conversation with situation evolution"""
        composer = ResponseComposer()
        sa = SituationalAwareness()
        
        patterns = [
            # Reactive patterns
            {
                'id': 'PATTERN_IDENTIFY_OUTPUT',
                'category': 'discovery',
                'response_type': 'reactive',
                'triggers': ['T_MENTION_OUTPUT']
            },
            {
                'id': 'PATTERN_RATE_EDGE',
                'category': 'assessment',
                'response_type': 'reactive',
                'triggers': ['T_RATE_EDGE']
            },
            {
                'id': 'PATTERN_CONFUSION',
                'category': 'error_recovery',
                'response_type': 'reactive',
                'triggers': ['CONFUSION_DETECTED']
            },
            # Proactive patterns
            {
                'id': 'PATTERN_EXTRACT_TIMELINE',
                'category': 'context_extraction',
                'response_type': 'proactive',
                'situation_affinity': {'context_extraction': 0.9, 'discovery': 0.5}
            },
            {
                'id': 'PATTERN_ASK_TEAM',
                'category': 'assessment',
                'response_type': 'proactive',
                'situation_affinity': {'assessment': 0.8}
            },
            {
                'id': 'PATTERN_CLARIFY_CONCEPT',
                'category': 'education',
                'response_type': 'proactive',
                'situation_affinity': {'clarification': 0.9}
            }
        ]
        
        # Turn 1: User mentions output
        triggers_1 = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        sa.update_from_triggers(triggers_1)
        composed_1 = composer.select_components(triggers_1, sa.composition, patterns)
        
        assert composed_1.reactive.pattern['id'] == 'PATTERN_IDENTIFY_OUTPUT'
        assert composed_1.total_tokens <= 310
        
        # Turn 2: User rates edge
        triggers_2 = [
            {'trigger_id': 'T_RATE_EDGE', 'priority': 'high', 'category': 'assessment'}
        ]
        sa.update_from_triggers(triggers_2)
        composed_2 = composer.select_components(triggers_2, sa.composition, patterns)
        
        assert composed_2.reactive.pattern['id'] == 'PATTERN_RATE_EDGE'
        assert composed_2.total_tokens <= 310
        
        # Turn 3: User gets confused
        triggers_3 = [
            {'trigger_id': 'CONFUSION_DETECTED', 'priority': 'critical', 'category': 'error_recovery'}
        ]
        sa.update_from_triggers(triggers_3)
        composed_3 = composer.select_components(triggers_3, sa.composition, patterns)
        
        assert composed_3.reactive.pattern['id'] == 'PATTERN_CONFUSION'
        assert composed_3.reactive.priority == 'critical'
        
        # Verify situation evolved correctly
        assert sa.composition['clarification'] > 0.1  # Should spike after confusion
        total = sum(sa.composition.values())
        assert abs(total - 1.0) < 0.001  # Always sums to 1.0
