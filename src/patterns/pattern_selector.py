"""
Pattern Selector (Situational Awareness Engine).

Selects best conversation pattern(s) based on:
1. Detected triggers (from TriggerDetector)
2. Situation affinity scores
3. Knowledge state (what user knows, conversation state)
4. Pattern history (avoid repetition)
5. Context continuity (TBD #25 - no context jumping)
"""
from typing import List, Dict, Any, Optional
from collections import deque


class PatternSelector:
    """
    Selects conversation patterns based on triggers and context.
    
    Core responsibility: Situational awareness - choosing the right
    pattern for the current conversation state.
    """
    
    def __init__(self, patterns: List[Dict[str, Any]]):
        """
        Initialize pattern selector.
        
        Args:
            patterns: List of pattern definitions from YAML
        """
        self.patterns = patterns
        self.pattern_history = deque(maxlen=10)  # Track last 10 patterns
        self.default_affinity = 0.5
    
    def select_pattern(
        self,
        triggers: List[Dict[str, Any]],
        tracker: Any,
        avoid_recent: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Select single best pattern based on triggers and context.
        
        Args:
            triggers: List of detected triggers from TriggerDetector
            tracker: KnowledgeTracker with conversation state
            avoid_recent: Whether to avoid recently used patterns
            
        Returns:
            Selected pattern dict, or None if no match
        """
        if not triggers:
            return None
        
        # Sort triggers by priority
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        sorted_triggers = sorted(
            triggers,
            key=lambda t: priority_order.get(t.get('priority', 'medium'), 0),
            reverse=True
        )
        
        # Find matching patterns for each trigger
        candidates = []
        for trigger in sorted_triggers:
            for pattern in self.patterns:
                if self._pattern_matches_trigger(pattern, trigger):
                    if self._check_prerequisites(pattern, tracker):
                        score = self._calculate_pattern_score(
                            pattern, trigger, tracker, avoid_recent
                        )
                        candidates.append({
                            'pattern': pattern,
                            'trigger': trigger,
                            'score': score
                        })
        
        if not candidates:
            return None
        
        # Select highest scoring pattern
        best = max(candidates, key=lambda c: c['score'])
        return best['pattern']
    
    def select_patterns(
        self,
        triggers: List[Dict[str, Any]],
        tracker: Any,
        max_patterns: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Select multiple patterns for combined response (TBD #25).
        
        CRITICAL: Secondary pattern must be highly relevant to primary.
        No context jumping - very bad UX.
        
        Args:
            triggers: List of detected triggers
            tracker: KnowledgeTracker with conversation state
            max_patterns: Maximum patterns to select (default 2)
            
        Returns:
            List of selected patterns (primary + secondary if relevant)
        """
        if not triggers or max_patterns < 1:
            return []
        
        # Select primary pattern
        primary = self.select_pattern(triggers, tracker)
        if not primary:
            return []
        
        if max_patterns == 1:
            return [primary]
        
        # Try to find relevant secondary pattern
        secondary = self._select_secondary_pattern(
            primary, triggers, tracker
        )
        
        if secondary:
            return [primary, secondary]
        else:
            return [primary]
    
    def _select_secondary_pattern(
        self,
        primary: Dict[str, Any],
        triggers: List[Dict[str, Any]],
        tracker: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Select secondary pattern that's highly relevant to primary.
        
        CRITICAL: Checks context continuity - no topic jumping.
        """
        candidates = []
        
        # Check all patterns, not just those matching different triggers
        for pattern in self.patterns:
            # Skip if same as primary
            if pattern['id'] == primary['id']:
                continue
            
            # Check if pattern matches any trigger
            matches_trigger = False
            for trigger in triggers:
                if self._pattern_matches_trigger(pattern, trigger):
                    matches_trigger = True
                    break
            
            if not matches_trigger:
                continue
            
            # Check prerequisites
            if not self._check_prerequisites(pattern, tracker):
                continue
            
            # CRITICAL: Check context continuity
            if not self._check_context_continuity(primary, pattern):
                continue
            
            # Calculate relevance score
            relevance = self._calculate_relevance(primary, pattern)
            if relevance >= 0.5:  # Relevance threshold (lowered to 0.5 for same-category patterns)
                candidates.append({
                    'pattern': pattern,
                    'relevance': relevance
                })
        
        if not candidates:
            return None
        
        # Select most relevant
        best = max(candidates, key=lambda c: c['relevance'])
        return best['pattern']
    
    def _check_context_continuity(
        self,
        primary: Dict[str, Any],
        secondary: Dict[str, Any]
    ) -> bool:
        """
        Check if secondary pattern maintains context continuity.
        
        Returns False if context jumps (different topic/focus).
        """
        # Same category = good continuity
        primary_category = primary.get('category', '')
        secondary_category = secondary.get('category', '')
        
        if primary_category == secondary_category:
            return True
        
        # Check if both relate to same output
        primary_context = primary.get('context', {})
        secondary_context = secondary.get('context', {})
        
        if primary_context.get('output') == secondary_context.get('output'):
            if primary_context.get('output'):  # Not empty
                return True
        
        # Check if both relate to same component
        if primary_context.get('component') == secondary_context.get('component'):
            if primary_context.get('component'):  # Not empty
                return True
        
        # Different categories and no shared context = context jump
        return False
    
    def _calculate_relevance(
        self,
        primary: Dict[str, Any],
        secondary: Dict[str, Any]
    ) -> float:
        """
        Calculate relevance score between two patterns.
        
        Higher score = more relevant (same context).
        """
        score = 0.0
        
        # Same category: +0.5
        if primary.get('category') == secondary.get('category'):
            score += 0.5
        
        # Same output: +0.3
        primary_context = primary.get('context', {})
        secondary_context = secondary.get('context', {})
        
        if primary_context.get('output') == secondary_context.get('output'):
            if primary_context.get('output'):
                score += 0.3
        
        # Same component: +0.2
        if primary_context.get('component') == secondary_context.get('component'):
            if primary_context.get('component'):
                score += 0.2
        
        return min(score, 1.0)
    
    def _pattern_matches_trigger(
        self,
        pattern: Dict[str, Any],
        trigger: Dict[str, Any]
    ) -> bool:
        """Check if pattern matches trigger"""
        pattern_triggers = pattern.get('triggers', [])
        trigger_id = trigger.get('trigger_id', '')
        
        return trigger_id in pattern_triggers
    
    def _check_prerequisites(
        self,
        pattern: Dict[str, Any],
        tracker: Any
    ) -> bool:
        """
        Check if pattern prerequisites are met.
        
        Prerequisites can include:
        - user_knowledge: What user knows
        - conversation_state: Current conversation state
        - system_knowledge: What system knows about user
        """
        prerequisites = pattern.get('prerequisites', {})
        
        if not prerequisites:
            return True
        
        # Check user knowledge prerequisites
        user_prereqs = prerequisites.get('user_knowledge', {})
        for key, required_value in user_prereqs.items():
            actual_value = tracker.user_knowledge.get(key)
            if actual_value != required_value:
                return False
        
        # Check conversation state prerequisites
        state_prereqs = prerequisites.get('conversation_state', {})
        for key, required_value in state_prereqs.items():
            actual_value = tracker.conversation_state.get(key)
            
            # Handle numeric comparisons
            if isinstance(required_value, (int, float)):
                if actual_value != required_value:
                    return False
            else:
                if actual_value != required_value:
                    return False
        
        return True
    
    def _calculate_pattern_score(
        self,
        pattern: Dict[str, Any],
        trigger: Dict[str, Any],
        tracker: Any,
        avoid_recent: bool
    ) -> float:
        """
        Calculate overall score for pattern selection.
        
        Considers:
        - Situation affinity (how well pattern fits situation)
        - Trigger priority
        - Pattern history (avoid repetition)
        """
        score = 0.0
        
        # Situation affinity score (0.0 - 1.0)
        affinity = self.calculate_affinity_score(pattern, trigger)
        score += affinity * 10  # Weight: 10
        
        # Trigger priority bonus
        priority = trigger.get('priority', 'medium')
        priority_bonus = {
            'critical': 5,
            'high': 3,
            'medium': 1,
            'low': 0
        }
        score += priority_bonus.get(priority, 0)
        
        # Penalty for recently used patterns
        if avoid_recent and pattern['id'] in self.pattern_history:
            score -= 5
        
        return score
    
    def calculate_affinity_score(
        self,
        pattern: Dict[str, Any],
        trigger: Dict[str, Any]
    ) -> float:
        """
        Calculate situation affinity score.
        
        Returns affinity value for trigger's category, or default.
        """
        situation_affinity = pattern.get('situation_affinity', {})
        trigger_category = trigger.get('category', '')
        
        return situation_affinity.get(trigger_category, self.default_affinity)
    
    def record_pattern_usage(self, pattern_id: str):
        """
        Record that a pattern was used.
        
        Tracks last 10 patterns to avoid repetition.
        """
        self.pattern_history.append(pattern_id)
