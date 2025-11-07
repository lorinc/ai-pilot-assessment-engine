"""
Tests for Enhanced Pattern Selection Algorithm (Days 8-9).

Tests the enhanced features:
1. Dimension-weighted affinity scoring
2. Pattern priority system
3. Context jumping prevention
4. Scoring weight tuning
"""
import pytest
from src.patterns.pattern_selector import PatternSelector
from src.patterns.knowledge_tracker import KnowledgeTracker


class TestDimensionWeightedScoring:
    """Test dimension-weighted affinity scoring"""
    
    def test_affinity_with_dimension_weights(self):
        """Should calculate affinity using knowledge dimensions"""
        patterns = [
            {
                'id': 'PATTERN_001',
                'category': 'assessment',
                'triggers': ['T_RATE_EDGE'],
                'situation_affinity': {'assessment': 0.8},
                'dimension_weights': {
                    'output_identified': 1.0,
                    'assessment_in_progress': 0.5
                }
            }
        ]
        
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        # Set dimension values
        tracker.update_system_knowledge({'output_identified': True})
        tracker.update_conversation_state({'assessment_in_progress': True})
        
        trigger = {'trigger_id': 'T_RATE_EDGE', 'category': 'assessment', 'priority': 'high'}
        
        # Calculate affinity
        affinity = selector.calculate_affinity_score(patterns[0], trigger, tracker)
        
        # Should be > base affinity due to positive dimensions
        assert affinity > 0.8
        assert affinity <= 1.0
    
    def test_affinity_without_tracker(self):
        """Should use base affinity when no tracker provided"""
        patterns = [
            {
                'id': 'PATTERN_001',
                'category': 'assessment',
                'triggers': ['T_RATE_EDGE'],
                'situation_affinity': {'assessment': 0.7}
            }
        ]
        
        selector = PatternSelector(patterns)
        trigger = {'trigger_id': 'T_RATE_EDGE', 'category': 'assessment'}
        
        affinity = selector.calculate_affinity_score(patterns[0], trigger, None)
        
        assert affinity == 0.7
    
    def test_affinity_without_dimension_weights(self):
        """Should use base affinity when pattern has no dimension weights"""
        patterns = [
            {
                'id': 'PATTERN_001',
                'category': 'assessment',
                'triggers': ['T_RATE_EDGE'],
                'situation_affinity': {'assessment': 0.6}
            }
        ]
        
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        tracker.update_system_knowledge({'output_identified': True})
        
        trigger = {'trigger_id': 'T_RATE_EDGE', 'category': 'assessment'}
        
        affinity = selector.calculate_affinity_score(patterns[0], trigger, tracker)
        
        assert affinity == 0.6


class TestValueNormalization:
    """Test dimension value normalization"""
    
    def test_normalize_boolean_true(self):
        """Should normalize True to 1.0"""
        selector = PatternSelector([])
        assert selector._normalize_value(True) == 1.0
    
    def test_normalize_boolean_false(self):
        """Should normalize False to 0.0"""
        selector = PatternSelector([])
        assert selector._normalize_value(False) == 0.0
    
    def test_normalize_float_in_range(self):
        """Should keep float in 0-1 range as-is"""
        selector = PatternSelector([])
        assert selector._normalize_value(0.75) == 0.75
        assert selector._normalize_value(0.0) == 0.0
        assert selector._normalize_value(1.0) == 1.0
    
    def test_normalize_star_rating(self):
        """Should normalize 1-5 star rating"""
        selector = PatternSelector([])
        # Note: integers 1-5 are treated as star ratings
        # But single digit 1 is in 0-1 range, so returns 1.0
        # Need to test with values clearly in 1-5 range
        assert selector._normalize_value(3) == 0.6  # 3/5
        assert selector._normalize_value(5) == 1.0  # 5/5
        assert selector._normalize_value(2) == 0.4  # 2/5
    
    def test_normalize_percentage(self):
        """Should normalize 0-100 percentage"""
        selector = PatternSelector([])
        assert selector._normalize_value(75) == 0.75
        assert selector._normalize_value(100) == 1.0
        assert selector._normalize_value(0) == 0.0
    
    def test_normalize_categorical_high(self):
        """Should normalize 'high' to 1.0"""
        selector = PatternSelector([])
        assert selector._normalize_value('high') == 1.0
        assert selector._normalize_value('yes') == 1.0
        assert selector._normalize_value('good') == 1.0
    
    def test_normalize_categorical_low(self):
        """Should normalize 'low' to 0.0"""
        selector = PatternSelector([])
        assert selector._normalize_value('low') == 0.0
        assert selector._normalize_value('no') == 0.0
        assert selector._normalize_value('poor') == 0.0
    
    def test_normalize_categorical_medium(self):
        """Should normalize 'medium' to 0.5"""
        selector = PatternSelector([])
        assert selector._normalize_value('medium') == 0.5
        assert selector._normalize_value('moderate') == 0.5
        assert selector._normalize_value('ok') == 0.5


class TestPatternPrioritySystem:
    """Test pattern priority in scoring"""
    
    def test_critical_pattern_scores_highest(self):
        """Critical patterns should score higher than others"""
        patterns = [
            {
                'id': 'PATTERN_CRITICAL',
                'category': 'error_recovery',
                'triggers': ['T_USER_CONFUSED'],
                'priority': 'critical',
                'situation_affinity': {'error_recovery': 0.9}
            },
            {
                'id': 'PATTERN_MEDIUM',
                'category': 'error_recovery',
                'triggers': ['T_USER_CONFUSED'],
                'priority': 'medium',
                'situation_affinity': {'error_recovery': 0.9}
            }
        ]
        
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        trigger = {
            'trigger_id': 'T_USER_CONFUSED',
            'category': 'error_recovery',
            'priority': 'high'
        }
        
        score_critical = selector._calculate_pattern_score(
            patterns[0], trigger, tracker, avoid_recent=False
        )
        score_medium = selector._calculate_pattern_score(
            patterns[1], trigger, tracker, avoid_recent=False
        )
        
        # Critical pattern should score higher
        assert score_critical > score_medium
        # Difference should be pattern priority bonus (8 vs 2 = 6 points)
        assert abs((score_critical - score_medium) - 6) < 0.1
    
    def test_pattern_priority_levels(self):
        """Test all pattern priority levels"""
        pattern_base = {
            'id': 'PATTERN_TEST',
            'category': 'test',
            'triggers': ['T_TEST'],
            'situation_affinity': {'test': 0.5}
        }
        
        selector = PatternSelector([])
        tracker = KnowledgeTracker()
        trigger = {'trigger_id': 'T_TEST', 'category': 'test', 'priority': 'medium'}
        
        # Test each priority level
        priorities = ['critical', 'high', 'medium', 'low']
        scores = []
        
        for priority in priorities:
            pattern = {**pattern_base, 'priority': priority}
            score = selector._calculate_pattern_score(pattern, trigger, tracker, False)
            scores.append(score)
        
        # Scores should decrease with priority
        assert scores[0] > scores[1]  # critical > high
        assert scores[1] > scores[2]  # high > medium
        assert scores[2] > scores[3]  # medium > low


class TestContextJumpingPrevention:
    """Test enhanced context jumping prevention"""
    
    def test_same_category_allows_combination(self):
        """Patterns in same category should allow combination"""
        patterns = [
            {
                'id': 'PATTERN_PRIMARY',
                'category': 'assessment',
                'triggers': ['T_RATE_EDGE']
            },
            {
                'id': 'PATTERN_SECONDARY',
                'category': 'assessment',
                'triggers': ['T_ASSESS_FACTOR']
            }
        ]
        
        selector = PatternSelector(patterns)
        
        # Same category = good continuity
        continuity = selector._check_context_continuity(patterns[0], patterns[1])
        assert continuity is True
    
    def test_different_category_blocks_combination(self):
        """Patterns in different categories should block combination"""
        patterns = [
            {
                'id': 'PATTERN_PRIMARY',
                'category': 'assessment',
                'triggers': ['T_RATE_EDGE'],
                'context': {}
            },
            {
                'id': 'PATTERN_SECONDARY',
                'category': 'recommendation',
                'triggers': ['T_RECOMMEND_PILOT'],
                'context': {}
            }
        ]
        
        selector = PatternSelector(patterns)
        
        # Different categories, no shared context = context jump
        continuity = selector._check_context_continuity(patterns[0], patterns[1])
        assert continuity is False
    
    def test_shared_output_allows_combination(self):
        """Patterns sharing same output should allow combination"""
        patterns = [
            {
                'id': 'PATTERN_PRIMARY',
                'category': 'assessment',
                'triggers': ['T_RATE_EDGE'],
                'context': {'output': 'Sales Forecast'}
            },
            {
                'id': 'PATTERN_SECONDARY',
                'category': 'analysis',
                'triggers': ['T_ANALYZE_BOTTLENECK'],
                'context': {'output': 'Sales Forecast'}
            }
        ]
        
        selector = PatternSelector(patterns)
        
        # Different categories but same output = good continuity
        continuity = selector._check_context_continuity(patterns[0], patterns[1])
        assert continuity is True


class TestScoringWeights:
    """Test scoring weight tuning"""
    
    def test_affinity_weight_dominates(self):
        """Affinity score should be primary factor (weight=10)"""
        pattern_high_affinity = {
            'id': 'PATTERN_HIGH',
            'category': 'test',
            'triggers': ['T_TEST'],
            'situation_affinity': {'test': 1.0},
            'priority': 'low'
        }
        
        pattern_low_affinity = {
            'id': 'PATTERN_LOW',
            'category': 'test',
            'triggers': ['T_TEST'],
            'situation_affinity': {'test': 0.1},
            'priority': 'high'
        }
        
        selector = PatternSelector([])
        tracker = KnowledgeTracker()
        trigger = {'trigger_id': 'T_TEST', 'category': 'test', 'priority': 'medium'}
        
        score_high = selector._calculate_pattern_score(
            pattern_high_affinity, trigger, tracker, False
        )
        score_low = selector._calculate_pattern_score(
            pattern_low_affinity, trigger, tracker, False
        )
        
        # High affinity should win despite lower pattern priority
        # High: 1.0 * 10 + 1 (trigger) + 0 (pattern) = 11
        # Low: 0.1 * 10 + 1 (trigger) + 4 (pattern) = 6
        assert score_high > score_low
    
    def test_recent_pattern_penalty(self):
        """Recently used patterns should be penalized"""
        pattern = {
            'id': 'PATTERN_RECENT',
            'category': 'test',
            'triggers': ['T_TEST'],
            'situation_affinity': {'test': 0.8}
        }
        
        selector = PatternSelector([pattern])
        tracker = KnowledgeTracker()
        trigger = {'trigger_id': 'T_TEST', 'category': 'test', 'priority': 'medium'}
        
        # Score without recent usage
        score_fresh = selector._calculate_pattern_score(pattern, trigger, tracker, False)
        
        # Mark as recently used
        selector.record_pattern_usage('PATTERN_RECENT')
        
        # Score with recent usage
        score_recent = selector._calculate_pattern_score(pattern, trigger, tracker, True)
        
        # Recent usage should reduce score by 5
        assert abs((score_fresh - score_recent) - 5) < 0.1


class TestIntegration:
    """Test integrated pattern selection with enhancements"""
    
    def test_select_best_pattern_with_dimensions(self):
        """Should select best pattern using dimension-weighted scoring"""
        patterns = [
            {
                'id': 'PATTERN_GOOD_FIT',
                'category': 'assessment',
                'triggers': ['T_RATE_EDGE'],
                'priority': 'high',
                'situation_affinity': {'assessment': 0.8},
                'dimension_weights': {
                    'output_identified': 1.0
                }
            },
            {
                'id': 'PATTERN_POOR_FIT',
                'category': 'assessment',
                'triggers': ['T_RATE_EDGE'],
                'priority': 'medium',
                'situation_affinity': {'assessment': 0.5}
            }
        ]
        
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        tracker.update_system_knowledge({'output_identified': True})
        
        triggers = [
            {'trigger_id': 'T_RATE_EDGE', 'category': 'assessment', 'priority': 'high'}
        ]
        
        selected = selector.select_pattern(triggers, tracker)
        
        # Should select better-fitting pattern
        assert selected is not None
        assert selected['id'] == 'PATTERN_GOOD_FIT'
    
    def test_critical_pattern_always_wins(self):
        """Critical patterns should always be selected first"""
        patterns = [
            {
                'id': 'PATTERN_CRITICAL',
                'category': 'error_recovery',
                'triggers': ['T_USER_CONFUSED'],
                'priority': 'critical',
                'situation_affinity': {'error_recovery': 0.9}
            },
            {
                'id': 'PATTERN_NORMAL',
                'category': 'assessment',
                'triggers': ['T_RATE_EDGE'],
                'priority': 'medium',
                'situation_affinity': {'assessment': 1.0}
            }
        ]
        
        selector = PatternSelector(patterns)
        tracker = KnowledgeTracker()
        
        triggers = [
            {'trigger_id': 'T_USER_CONFUSED', 'category': 'error_recovery', 'priority': 'critical'},
            {'trigger_id': 'T_RATE_EDGE', 'category': 'assessment', 'priority': 'medium'}
        ]
        
        selected = selector.select_pattern(triggers, tracker)
        
        # Critical pattern should be selected
        assert selected is not None
        assert selected['id'] == 'PATTERN_CRITICAL'
