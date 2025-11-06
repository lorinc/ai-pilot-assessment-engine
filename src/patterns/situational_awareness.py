"""
Situational Awareness - Dynamic Conversation Composition

8-dimensional composition that always sums to 100%:
1. Discovery - Identifying outputs, context
2. Assessment - Rating edges, gathering evidence
3. Analysis - Calculating bottlenecks, understanding issues
4. Recommendation - Suggesting AI pilots
5. Feasibility - Checking prerequisites
6. Clarification - Resolving ambiguity
7. Validation - Confirming understanding
8. Meta - System help, conversation management

Release 2.2 - Situational Awareness
"""
from typing import Dict, List, Tuple, Any


class SituationalAwareness:
    """
    Dynamic situational awareness composition.
    
    Tracks where the conversation is across 8 dimensions.
    Composition always sums to 100% (1.0).
    Updates based on triggers and decays over time.
    """
    
    # 8 dimensions
    DIMENSIONS = [
        'discovery',
        'assessment',
        'analysis',
        'recommendation',
        'feasibility',
        'clarification',
        'validation',
        'meta'
    ]
    
    # Default starting composition (discovery + meta heavy)
    DEFAULT_COMPOSITION = {
        'discovery': 0.50,      # Start with discovery
        'assessment': 0.05,
        'analysis': 0.02,
        'recommendation': 0.01,
        'feasibility': 0.01,
        'clarification': 0.05,
        'validation': 0.01,
        'meta': 0.35            # System help available
    }
    
    # Mapping from trigger categories to situation dimensions
    CATEGORY_TO_DIMENSION = {
        'discovery': 'discovery',
        'assessment': 'assessment',
        'analysis': 'analysis',
        'recommendation': 'recommendation',
        'context_extraction': 'discovery',  # Context extraction is part of discovery
        'error_recovery': 'clarification',  # Error recovery needs clarification
        'navigation': 'meta',               # Navigation is meta
        'inappropriate_use': 'meta',        # Inappropriate use is meta
        'onboarding': 'meta',              # Onboarding is meta
        'education': 'meta'                # Education is meta
    }
    
    # Signal strength (how much to boost dimension per trigger)
    SIGNAL_STRENGTH = 0.15
    
    # Decay rate (how much dimensions decay toward baseline per step)
    DECAY_RATE = 0.10
    
    def __init__(self, initial_composition: Dict[str, float] = None):
        """
        Initialize situational awareness.
        
        Args:
            initial_composition: Optional custom starting composition
        """
        if initial_composition:
            self.composition = initial_composition.copy()
        else:
            self.composition = self.DEFAULT_COMPOSITION.copy()
        
        # Normalize to ensure sum = 1.0
        self._normalize()
    
    def update_from_triggers(self, triggers: List[Dict[str, Any]]) -> None:
        """
        Update composition based on detected triggers.
        
        Args:
            triggers: List of trigger dicts with 'category' field
        """
        if not triggers:
            return
        
        # Count signals per dimension
        signals = {dim: 0 for dim in self.DIMENSIONS}
        
        for trigger in triggers:
            category = trigger.get('category')
            if category in self.CATEGORY_TO_DIMENSION:
                dimension = self.CATEGORY_TO_DIMENSION[category]
                signals[dimension] += 1
        
        # Apply signals (boost dimensions)
        for dimension, count in signals.items():
            if count > 0:
                boost = self.SIGNAL_STRENGTH * count
                self.composition[dimension] += boost
        
        # Normalize to maintain sum = 1.0
        self._normalize()
    
    def apply_decay(self) -> None:
        """
        Apply decay to all dimensions (move toward baseline).
        
        Dimensions decay toward DEFAULT_COMPOSITION over time.
        This prevents dimensions from staying high indefinitely.
        """
        baseline = self.DEFAULT_COMPOSITION
        
        for dimension in self.DIMENSIONS:
            current = self.composition[dimension]
            target = baseline[dimension]
            
            # Move toward baseline
            delta = (target - current) * self.DECAY_RATE
            self.composition[dimension] += delta
        
        # Normalize to maintain sum = 1.0
        self._normalize()
    
    def get_dominant_dimensions(self, n: int = 3) -> List[Tuple[str, float]]:
        """
        Get top N dimensions sorted by value.
        
        Args:
            n: Number of dimensions to return
            
        Returns:
            List of (dimension, value) tuples sorted by value (descending)
        """
        sorted_dims = sorted(
            self.composition.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_dims[:n]
    
    def reset(self) -> None:
        """Reset composition to default starting state"""
        self.composition = self.DEFAULT_COMPOSITION.copy()
        self._normalize()
    
    def _normalize(self) -> None:
        """
        Normalize composition to sum to 1.0 (100%).
        
        This is called after every update to maintain the constraint.
        """
        total = sum(self.composition.values())
        
        if total > 0:
            for dimension in self.DIMENSIONS:
                self.composition[dimension] /= total
    
    def __repr__(self) -> str:
        """String representation"""
        top_3 = self.get_dominant_dimensions(n=3)
        top_str = ", ".join([f"{dim}: {val:.1%}" for dim, val in top_3])
        return f"SituationalAwareness({top_str})"
