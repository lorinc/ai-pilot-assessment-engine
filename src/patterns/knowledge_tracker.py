"""
Knowledge tracker for conversation state management.

Tracks two dimensions of knowledge:
1. User Knowledge: What the user knows about the system
2. System Knowledge: What the system knows about the user's context

Also tracks conversation state and quality metrics.
"""
from typing import Dict, Any, Optional
from copy import deepcopy


class KnowledgeTracker:
    """
    Tracks knowledge state during conversation.
    
    Manages:
    - User knowledge (9 dimensions)
    - System knowledge (12 dimensions)
    - Conversation state (8 dimensions)
    - Quality metrics (6 dimensions)
    
    Total: 35 dimensions tracked
    """
    
    def __init__(self):
        """Initialize knowledge tracker with default values"""
        self.user_knowledge = self._init_user_knowledge()
        self.system_knowledge = self._init_system_knowledge()
        self.conversation_state = self._init_conversation_state()
        self.quality_metrics = self._init_quality_metrics()
    
    def _init_user_knowledge(self) -> Dict[str, Any]:
        """
        Initialize user knowledge with defaults.
        
        User knowledge tracks what the user knows about the system.
        Defaults to False (user doesn't know yet).
        """
        return {
            # Understanding of system
            'understands_object_model': False,
            'understands_min_calculation': False,
            'understands_evidence_tiers': False,
            'understands_scope_importance': False,
            'understands_bottleneck_concept': False,
            
            # Experience
            'has_seen_recommendations': False,
            'has_used_system_before': False,
            
            # Comfort level
            'comfort_level': 'learning',  # confused, learning, comfortable, expert
            'preferred_interaction_style': 'guided'  # detailed, concise, guided, exploratory
        }
    
    def _init_system_knowledge(self) -> Dict[str, Any]:
        """
        Initialize system knowledge with defaults.
        
        System knowledge tracks what the system knows about user's context.
        """
        return {
            # Outputs and assessment
            'outputs_identified': [],  # List of output IDs
            'outputs_assessed': {},  # {output_id: {components: int, confidence: str}}
            'bottlenecks_identified': {},  # {output_id: [component_ids]}
            'recommendations_shown': {},  # {output_id: [pilot_ids]}
            
            # User context
            'user_domain': 'unknown',  # sales, finance, operations, unknown
            'user_role': 'unknown',  # manager, analyst, executive, unknown
            
            # Quality and scope
            'evidence_quality': 'medium',  # high, medium, low
            'scope_clarity': 'ambiguous',  # clear, ambiguous, conflicting
            
            # Active work
            'active_outputs': [],  # Currently active output IDs
            'session_history': {},  # {session_id: summary}
            
            # Depth metrics
            'assessment_depth_ratio': 0.0,  # avg_components_per_output / total_outputs
            'sparse_knowledge_flag': False  # True if 3+ outputs, all <2 components
        }
    
    def _init_conversation_state(self) -> Dict[str, Any]:
        """
        Initialize conversation state with defaults.
        
        Tracks current state of the conversation.
        """
        return {
            # Current focus
            'current_focus': 'discovering_output',  # discovering_output, assessing_component, analyzing, recommending
            
            # Interaction tracking
            'last_question_answered': True,
            'pattern_history': [],  # Last 5 patterns used
            
            # Emotional state (0.0-1.0)
            'frustration_level': 0.0,  # 0=calm, 1=very frustrated
            'confusion_level': 0.0,  # 0=clear, 1=very confused
            'engagement_level': 0.5,  # 0=disengaged, 1=highly engaged
            
            # Progress tracking
            'turns_since_progress': 0,
            'needs_navigation': False
        }
    
    def _init_quality_metrics(self) -> Dict[str, Any]:
        """
        Initialize quality metrics with defaults.
        
        Tracks conversation quality indicators.
        """
        return {
            # Evidence quality
            'tier1_evidence_count': 0,  # High-quality evidence
            'tier5_evidence_count': 0,  # Low-quality evidence
            
            # Assessment quality
            'confidence_by_output': {},  # {output_id: low/medium/high}
            'missing_components': {},  # {output_id: [component_names]}
            
            # Issues
            'scope_ambiguities': [],  # List of ambiguous statements
            'contradictions_resolved': 0  # Count of resolved contradictions
        }
    
    def update_user_knowledge(self, updates: Dict[str, Any]):
        """
        Update user knowledge dimensions.
        
        Args:
            updates: Dictionary of knowledge updates
        """
        self.user_knowledge.update(updates)
    
    def update_system_knowledge(self, updates: Dict[str, Any]):
        """
        Update system knowledge dimensions.
        
        Args:
            updates: Dictionary of knowledge updates
        """
        self.system_knowledge.update(updates)
    
    def update_conversation_state(self, updates: Dict[str, Any]):
        """
        Update conversation state dimensions.
        
        Args:
            updates: Dictionary of state updates
        """
        self.conversation_state.update(updates)
    
    def update_quality_metrics(self, updates: Dict[str, Any]):
        """
        Update quality metrics.
        
        Args:
            updates: Dictionary of metric updates
        """
        self.quality_metrics.update(updates)
    
    def check_prerequisites(self, requires: Optional[Dict[str, Any]]) -> bool:
        """
        Check if prerequisites are met.
        
        Args:
            requires: Dictionary of prerequisites in format:
                     {'user_knowledge.dimension': value, ...}
        
        Returns:
            True if all prerequisites met, False otherwise
        """
        if not requires:
            return True
        
        for key, required_value in requires.items():
            # Parse key (e.g., "user_knowledge.understands_object_model")
            if '.' in key:
                category, dimension = key.split('.', 1)
                
                if category == 'user_knowledge':
                    actual_value = self.user_knowledge.get(dimension)
                elif category == 'system_knowledge':
                    actual_value = self.system_knowledge.get(dimension)
                elif category == 'conversation_state':
                    actual_value = self.conversation_state.get(dimension)
                else:
                    # Unknown category
                    return False
                
                # Check if value matches
                if actual_value != required_value:
                    return False
            else:
                # Invalid key format
                return False
        
        return True
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current knowledge state.
        
        Returns:
            Dictionary with user and system knowledge
        """
        return {
            'user': deepcopy(self.user_knowledge),
            'system': deepcopy(self.system_knowledge),
            'conversation': deepcopy(self.conversation_state),
            'quality': deepcopy(self.quality_metrics)
        }
    
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize knowledge state for session storage.
        
        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            'user': self.user_knowledge.copy(),
            'system': self.system_knowledge.copy(),
            'conversation': self.conversation_state.copy(),
            'quality': self.quality_metrics.copy()
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'KnowledgeTracker':
        """
        Restore knowledge tracker from serialized data.
        
        Args:
            data: Serialized knowledge state
            
        Returns:
            KnowledgeTracker instance
        """
        tracker = cls()
        
        if 'user' in data:
            tracker.user_knowledge.update(data['user'])
        if 'system' in data:
            tracker.system_knowledge.update(data['system'])
        if 'conversation' in data:
            tracker.conversation_state.update(data['conversation'])
        if 'quality' in data:
            tracker.quality_metrics.update(data['quality'])
        
        return tracker
    
    def apply_decay(self):
        """
        Apply decay to time-sensitive dimensions.
        
        Some dimensions decay over time if not reinforced:
        - frustration_level: decays by 0.1 per turn
        - confusion_level: decays by 0.15 per turn
        - engagement_level: decays by 0.05 per turn
        """
        # Decay frustration
        if self.conversation_state['frustration_level'] > 0:
            self.conversation_state['frustration_level'] = max(
                0.0,
                self.conversation_state['frustration_level'] - 0.1
            )
        
        # Decay confusion
        if self.conversation_state['confusion_level'] > 0:
            self.conversation_state['confusion_level'] = max(
                0.0,
                self.conversation_state['confusion_level'] - 0.15
            )
        
        # Decay engagement
        if self.conversation_state['engagement_level'] > 0:
            self.conversation_state['engagement_level'] = max(
                0.0,
                self.conversation_state['engagement_level'] - 0.05
            )
    
    def increment_evidence_count(self, tier: str):
        """
        Increment evidence count for a specific tier.
        
        Args:
            tier: Evidence tier (tier1, tier2, tier3, tier4, tier5)
        """
        key = f'{tier}_evidence_count'
        if key in self.quality_metrics:
            self.quality_metrics[key] += 1
