"""
Tests for Situational Awareness

TDD RED phase - tests written first to define behavior

Situational Awareness = 8-dimensional composition that always sums to 100%
Dimensions: discovery, assessment, analysis, recommendation, 
            feasibility, clarification, validation, meta
"""
import pytest
from src.patterns.situational_awareness import SituationalAwareness


class TestSituationalAwarenessInitialization:
    """Test situational awareness initialization"""
    
    def test_initialization_default(self):
        """Should initialize with default starting composition"""
        sa = SituationalAwareness()
        
        # Should have 8 dimensions
        assert len(sa.composition) == 8
        
        # Should sum to 100% (1.0)
        total = sum(sa.composition.values())
        assert abs(total - 1.0) < 0.001  # Allow small floating point error
        
        # Default: discovery and meta should be highest at start
        assert sa.composition['discovery'] > 0
        assert sa.composition['meta'] > 0
    
    def test_initialization_custom(self):
        """Should initialize with custom composition"""
        custom_composition = {
            'discovery': 0.50,
            'assessment': 0.30,
            'analysis': 0.10,
            'recommendation': 0.05,
            'feasibility': 0.02,
            'clarification': 0.01,
            'validation': 0.01,
            'meta': 0.01
        }
        
        sa = SituationalAwareness(initial_composition=custom_composition)
        
        # Should match custom composition
        for dim, value in custom_composition.items():
            assert abs(sa.composition[dim] - value) < 0.001


class TestCompositionConstraint:
    """Test that composition always sums to 100%"""
    
    def test_composition_sums_to_one(self):
        """Composition must always sum to 1.0 (100%)"""
        sa = SituationalAwareness()
        
        total = sum(sa.composition.values())
        assert abs(total - 1.0) < 0.001
    
    def test_composition_after_update(self):
        """Composition must sum to 1.0 after updates"""
        sa = SituationalAwareness()
        
        # Update with signals
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])
        
        total = sum(sa.composition.values())
        assert abs(total - 1.0) < 0.001
    
    def test_composition_after_multiple_updates(self):
        """Composition must sum to 1.0 after multiple updates"""
        sa = SituationalAwareness()
        
        # Multiple updates
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])
        sa.update_from_triggers([
            {'trigger_id': 'CONFUSION_DETECTED', 'category': 'error_recovery'}
        ])
        sa.update_from_triggers([
            {'trigger_id': 'T_REQUEST_PROGRESS', 'category': 'navigation'}
        ])
        
        total = sum(sa.composition.values())
        assert abs(total - 1.0) < 0.001


class TestSignalDetection:
    """Test signal detection from triggers"""
    
    def test_discovery_signal(self):
        """Should increase discovery dimension when discovery trigger fires"""
        sa = SituationalAwareness()
        initial_discovery = sa.composition['discovery']
        
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])
        
        # Discovery should increase
        assert sa.composition['discovery'] > initial_discovery
    
    def test_error_recovery_signal(self):
        """Should increase clarification when error recovery trigger fires"""
        sa = SituationalAwareness()
        initial_clarification = sa.composition['clarification']
        
        sa.update_from_triggers([
            {'trigger_id': 'CONFUSION_DETECTED', 'category': 'error_recovery'}
        ])
        
        # Clarification should increase (error recovery maps to clarification)
        assert sa.composition['clarification'] > initial_clarification
    
    def test_navigation_signal(self):
        """Should increase meta when navigation trigger fires"""
        sa = SituationalAwareness()
        initial_meta = sa.composition['meta']
        
        sa.update_from_triggers([
            {'trigger_id': 'T_REQUEST_PROGRESS', 'category': 'navigation'}
        ])
        
        # Meta should increase
        assert sa.composition['meta'] > initial_meta
    
    def test_multiple_signals(self):
        """Should handle multiple triggers in one update"""
        sa = SituationalAwareness()
        
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'},
            {'trigger_id': 'CONFUSION_DETECTED', 'category': 'error_recovery'}
        ])
        
        # Both dimensions should be affected
        # Composition should still sum to 1.0
        total = sum(sa.composition.values())
        assert abs(total - 1.0) < 0.001


class TestDecay:
    """Test decay of dimensions over time"""
    
    def test_decay_reduces_dimensions(self):
        """Decay should reduce all dimensions toward baseline"""
        sa = SituationalAwareness()
        
        # Boost discovery
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])
        
        discovery_after_boost = sa.composition['discovery']
        
        # Apply decay
        sa.apply_decay()
        
        # Discovery should decrease (decay toward baseline)
        assert sa.composition['discovery'] < discovery_after_boost
    
    def test_decay_maintains_sum(self):
        """Decay must maintain composition sum of 1.0"""
        sa = SituationalAwareness()
        
        # Boost some dimensions
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])
        
        # Apply decay
        sa.apply_decay()
        
        # Sum should still be 1.0
        total = sum(sa.composition.values())
        assert abs(total - 1.0) < 0.001
    
    def test_multiple_decay_steps(self):
        """Multiple decay steps should gradually reduce dimensions"""
        sa = SituationalAwareness()
        
        # Boost discovery
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])
        
        discovery_values = [sa.composition['discovery']]
        
        # Apply decay multiple times
        for _ in range(5):
            sa.apply_decay()
            discovery_values.append(sa.composition['discovery'])
        
        # Discovery should gradually decrease
        for i in range(len(discovery_values) - 1):
            assert discovery_values[i] >= discovery_values[i + 1]


class TestDimensionMapping:
    """Test mapping from trigger categories to situation dimensions"""
    
    def test_discovery_mapping(self):
        """Discovery triggers should map to discovery dimension"""
        sa = SituationalAwareness()
        
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])
        
        # Discovery dimension should be affected
        assert sa.composition['discovery'] > 0.1
    
    def test_assessment_mapping(self):
        """Assessment triggers should map to assessment dimension"""
        sa = SituationalAwareness()
        
        sa.update_from_triggers([
            {'trigger_id': 'T_RATE_EDGE', 'category': 'assessment'}
        ])
        
        # Assessment dimension should be affected
        assert sa.composition['assessment'] > 0.1
    
    def test_error_recovery_to_clarification(self):
        """Error recovery triggers should map to clarification dimension"""
        sa = SituationalAwareness()
        
        sa.update_from_triggers([
            {'trigger_id': 'CONFUSION_DETECTED', 'category': 'error_recovery'}
        ])
        
        # Clarification should increase (error recovery needs clarification)
        assert sa.composition['clarification'] > 0.1
    
    def test_navigation_to_meta(self):
        """Navigation triggers should map to meta dimension"""
        sa = SituationalAwareness()
        
        sa.update_from_triggers([
            {'trigger_id': 'T_REQUEST_PROGRESS', 'category': 'navigation'}
        ])
        
        # Meta should increase
        assert sa.composition['meta'] > 0.1


class TestGetDominantDimensions:
    """Test getting dominant dimensions"""
    
    def test_get_top_dimension(self):
        """Should return dimension with highest value"""
        sa = SituationalAwareness()
        
        # Boost discovery significantly
        for _ in range(3):
            sa.update_from_triggers([
                {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
            ])
        
        top_dims = sa.get_dominant_dimensions(n=1)
        
        assert len(top_dims) == 1
        assert top_dims[0][0] == 'discovery'  # (dimension, value)
    
    def test_get_top_three_dimensions(self):
        """Should return top 3 dimensions sorted by value"""
        sa = SituationalAwareness()
        
        # Create varied composition
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'},
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'},
            {'trigger_id': 'CONFUSION_DETECTED', 'category': 'error_recovery'}
        ])
        
        top_dims = sa.get_dominant_dimensions(n=3)
        
        assert len(top_dims) == 3
        # Should be sorted by value (descending)
        assert top_dims[0][1] >= top_dims[1][1] >= top_dims[2][1]


class TestResetComposition:
    """Test resetting composition"""
    
    def test_reset_to_default(self):
        """Should reset to default starting composition"""
        sa = SituationalAwareness()
        
        # Modify composition
        sa.update_from_triggers([
            {'trigger_id': 'T_MENTION_OUTPUT', 'category': 'discovery'}
        ])
        
        # Reset
        sa.reset()
        
        # Should be back to default
        # Discovery and meta should be highest
        assert sa.composition['discovery'] > 0.3
        assert sa.composition['meta'] > 0.1
        
        # Should sum to 1.0
        total = sum(sa.composition.values())
        assert abs(total - 1.0) < 0.001
