"""
Tests for Pattern Selector (Situational Awareness Engine).

The Pattern Selector:
1. Takes detected triggers from TriggerDetector
2. Evaluates situation affinity scores
3. Selects best pattern(s) based on context
4. Supports multi-pattern responses (TBD #25)
5. Tracks pattern history to avoid repetition
"""
import pytest
from src.patterns.pattern_selector import PatternSelector
from src.patterns.knowledge_tracker import KnowledgeTracker
from src.patterns.pattern_loader import PatternLoader


class TestPatternSelectorInitialization:
    """Test pattern selector initialization"""
    
    def test_initialization_with_patterns(self):
        """Should initialize with pattern definitions"""
        patterns = [
            {
                'id': 'PATTERN_001',
                'category': 'onboarding',
                'triggers': ['T_FIRST_MESSAGE'],
                'behaviors': ['B_WELCOME']
            }
        ]
        selector = PatternSelector(patterns)
        assert selector.patterns == patterns
        assert len(selector.pattern_history) == 0
    
    def test_initialization_empty(self):
        """Should initialize with empty patterns"""
        selector = PatternSelector([])
        assert selector.patterns == []


class TestSinglePatternSelection:
    """Test selecting single best pattern"""
    
    def test_select_pattern_by_trigger(self):
        """Should select pattern matching trigger"""
        patterns = [
            {
                'id': 'PATTERN_001',
                'category': 'onboarding',
                'triggers': ['T_FIRST_MESSAGE'],
                'behaviors': ['B_WELCOME'],
                'situation_affinity': {'onboarding': 1.0}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [
            {'trigger_id': 'T_FIRST_MESSAGE', 'priority': 'high', 'category': 'onboarding'}
        ]
        
        selected = selector.select_pattern(triggers, tracker)
        assert selected is not None
        assert selected['id'] == 'PATTERN_001'
    
    def test_select_pattern_by_priority(self):
        """Should prefer higher priority trigger"""
        patterns = [
            {
                'id': 'PATTERN_CRITICAL',
                'triggers': ['T_CONFUSION'],
                'situation_affinity': {'error_recovery': 1.0}
            },
            {
                'id': 'PATTERN_LOW',
                'triggers': ['T_HUMOR'],
                'situation_affinity': {'inappropriate_use': 0.5}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [
            {'trigger_id': 'T_HUMOR', 'priority': 'low'},
            {'trigger_id': 'T_CONFUSION', 'priority': 'critical'}
        ]
        
        selected = selector.select_pattern(triggers, tracker)
        assert selected['id'] == 'PATTERN_CRITICAL'
    
    def test_select_pattern_by_affinity(self):
        """Should prefer pattern with higher situation affinity"""
        patterns = [
            {
                'id': 'PATTERN_HIGH_AFFINITY',
                'triggers': ['T_MENTION_OUTPUT'],
                'situation_affinity': {'discovery': 0.9}
            },
            {
                'id': 'PATTERN_LOW_AFFINITY',
                'triggers': ['T_MENTION_OUTPUT'],
                'situation_affinity': {'discovery': 0.3}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'medium', 'category': 'discovery'}
        ]
        
        selected = selector.select_pattern(triggers, tracker)
        assert selected['id'] == 'PATTERN_HIGH_AFFINITY'
    
    def test_no_pattern_selected(self):
        """Should return None if no pattern matches"""
        patterns = [
            {
                'id': 'PATTERN_001',
                'triggers': ['T_FIRST_MESSAGE']
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [
            {'trigger_id': 'T_UNKNOWN', 'priority': 'medium'}
        ]
        
        selected = selector.select_pattern(triggers, tracker)
        assert selected is None


class TestMultiPatternSelection:
    """Test selecting multiple patterns (TBD #25)"""
    
    def test_select_two_patterns_same_context(self):
        """Should select two patterns if highly relevant"""
        patterns = [
            {
                'id': 'PATTERN_PRIMARY',
                'triggers': ['T_MENTION_OUTPUT'],
                'category': 'discovery',
                'situation_affinity': {'discovery': 0.9}
            },
            {
                'id': 'PATTERN_SECONDARY',
                'triggers': ['T_MENTION_OUTPUT'],
                'category': 'discovery',
                'situation_affinity': {'discovery': 0.7}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        
        selected = selector.select_patterns(triggers, tracker, max_patterns=2)
        assert len(selected) == 2
        assert selected[0]['id'] == 'PATTERN_PRIMARY'
        assert selected[1]['id'] == 'PATTERN_SECONDARY'
    
    def test_reject_multi_pattern_context_jump(self):
        """Should NOT select second pattern if context jumps"""
        patterns = [
            {
                'id': 'PATTERN_PRIMARY',
                'triggers': ['T_MENTION_PROBLEM'],
                'category': 'discovery',
                'situation_affinity': {'discovery': 0.9}
            },
            {
                'id': 'PATTERN_UNRELATED',
                'triggers': ['T_EXTRACT_TIMELINE'],
                'category': 'context_extraction',
                'situation_affinity': {'context_extraction': 0.8}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [
            {'trigger_id': 'T_MENTION_PROBLEM', 'priority': 'high', 'category': 'discovery'},
            {'trigger_id': 'T_EXTRACT_TIMELINE', 'priority': 'medium', 'category': 'context_extraction'}
        ]
        
        selected = selector.select_patterns(triggers, tracker, max_patterns=2)
        # Should only select primary, reject secondary due to context jump
        assert len(selected) == 1
        assert selected[0]['id'] == 'PATTERN_PRIMARY'
    
    def test_multi_pattern_same_output(self):
        """Should allow multi-pattern if both relate to same output"""
        patterns = [
            {
                'id': 'PATTERN_IDENTIFY',
                'triggers': ['T_MENTION_OUTPUT'],
                'category': 'discovery',
                'context': {'output': 'sales_forecast'}
            },
            {
                'id': 'PATTERN_CONFIRM',
                'triggers': ['T_MENTION_OUTPUT'],
                'category': 'discovery',
                'context': {'output': 'sales_forecast'}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [
            {'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}
        ]
        
        selected = selector.select_patterns(triggers, tracker, max_patterns=2)
        assert len(selected) == 2


class TestPatternHistory:
    """Test pattern history tracking to avoid repetition"""
    
    def test_track_pattern_usage(self):
        """Should track which patterns were used"""
        patterns = [
            {'id': 'PATTERN_001', 'triggers': ['T_FIRST_MESSAGE']}
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [{'trigger_id': 'T_FIRST_MESSAGE', 'priority': 'high'}]
        
        selected = selector.select_pattern(triggers, tracker)
        selector.record_pattern_usage(selected['id'])
        
        assert 'PATTERN_001' in selector.pattern_history
    
    def test_avoid_recent_pattern(self):
        """Should avoid using same pattern within 5 turns"""
        patterns = [
            {
                'id': 'PATTERN_REPEATED',
                'triggers': ['T_REQUEST_STATUS'],
                'situation_affinity': {'navigation': 0.8}
            },
            {
                'id': 'PATTERN_ALTERNATIVE',
                'triggers': ['T_REQUEST_STATUS'],
                'situation_affinity': {'navigation': 0.7}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        # Use first pattern
        selector.record_pattern_usage('PATTERN_REPEATED')
        
        triggers = [{'trigger_id': 'T_REQUEST_STATUS', 'priority': 'medium'}]
        
        # Should select alternative, not repeated
        selected = selector.select_pattern(triggers, tracker)
        assert selected['id'] == 'PATTERN_ALTERNATIVE'
    
    def test_pattern_history_limit(self):
        """Should only track last 10 patterns"""
        selector = PatternSelector([])
        
        for i in range(15):
            selector.record_pattern_usage(f'PATTERN_{i}')
        
        assert len(selector.pattern_history) == 10
        assert 'PATTERN_5' in selector.pattern_history
        assert 'PATTERN_0' not in selector.pattern_history


class TestContextAwareness:
    """Test context-aware pattern selection"""
    
    def test_select_based_on_knowledge_state(self):
        """Should select pattern based on what user knows"""
        patterns = [
            {
                'id': 'PATTERN_EXPLAIN_MIN',
                'triggers': ['T_MENTION_COMPONENTS'],
                'prerequisites': {'user_knowledge': {'understands_min_calculation': False}}
            },
            {
                'id': 'PATTERN_SKIP_EXPLANATION',
                'triggers': ['T_MENTION_COMPONENTS'],
                'prerequisites': {'user_knowledge': {'understands_min_calculation': True}}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        # User doesn't understand MIN yet
        tracker.update_user_knowledge({'understands_min_calculation': False})
        
        triggers = [{'trigger_id': 'T_MENTION_COMPONENTS', 'priority': 'medium'}]
        
        selected = selector.select_pattern(triggers, tracker)
        assert selected['id'] == 'PATTERN_EXPLAIN_MIN'
    
    def test_select_based_on_conversation_state(self):
        """Should select pattern based on conversation state"""
        patterns = [
            {
                'id': 'PATTERN_ESCALATE',
                'triggers': ['T_OFF_TOPIC'],
                'prerequisites': {'conversation_state': {'off_topic_count': 3}}
            },
            {
                'id': 'PATTERN_GENTLE',
                'triggers': ['T_OFF_TOPIC'],
                'prerequisites': {'conversation_state': {'off_topic_count': 1}}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        # First off-topic
        tracker.update_conversation_state({'off_topic_count': 1})
        
        triggers = [{'trigger_id': 'T_OFF_TOPIC', 'priority': 'medium'}]
        
        selected = selector.select_pattern(triggers, tracker)
        assert selected['id'] == 'PATTERN_GENTLE'


class TestSituationAffinity:
    """Test situation affinity scoring"""
    
    def test_calculate_affinity_score(self):
        """Should calculate affinity score correctly"""
        pattern = {
            'id': 'PATTERN_001',
            'situation_affinity': {
                'discovery': 0.9,
                'assessment': 0.3
            }
        }
        selector = PatternSelector([pattern])
        
        # Trigger in discovery situation
        trigger = {'category': 'discovery'}
        score = selector.calculate_affinity_score(pattern, trigger)
        assert score == 0.9
    
    def test_default_affinity_score(self):
        """Should use default score if category not in affinity"""
        pattern = {
            'id': 'PATTERN_001',
            'situation_affinity': {
                'discovery': 0.9
            }
        }
        selector = PatternSelector([pattern])
        
        # Trigger in different category
        trigger = {'category': 'education'}
        score = selector.calculate_affinity_score(pattern, trigger)
        assert score == 0.5  # Default affinity


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_triggers(self):
        """Should handle empty trigger list"""
        selector = PatternSelector([{'id': 'PATTERN_001'}])
        tracker = KnowledgeTracker()
        
        selected = selector.select_pattern([], tracker)
        assert selected is None
    
    def test_malformed_pattern(self):
        """Should handle malformed pattern gracefully"""
        patterns = [
            {'id': 'PATTERN_MALFORMED'}  # Missing triggers
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [{'trigger_id': 'T_FIRST_MESSAGE', 'priority': 'high'}]
        
        # Should not crash, just skip malformed pattern
        selected = selector.select_pattern(triggers, tracker)
        assert selected is None
    
    def test_multiple_triggers_same_priority(self):
        """Should handle multiple triggers with same priority"""
        patterns = [
            {
                'id': 'PATTERN_A',
                'triggers': ['T_TRIGGER_A'],
                'situation_affinity': {'discovery': 0.8}
            },
            {
                'id': 'PATTERN_B',
                'triggers': ['T_TRIGGER_B'],
                'situation_affinity': {'discovery': 0.9}
            }
        ]
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [
            {'trigger_id': 'T_TRIGGER_A', 'priority': 'high', 'category': 'discovery'},
            {'trigger_id': 'T_TRIGGER_B', 'priority': 'high', 'category': 'discovery'}
        ]
        
        selected = selector.select_pattern(triggers, tracker)
        # Should select higher affinity
        assert selected['id'] == 'PATTERN_B'
