"""
Response Composer - Reactive + Proactive Architecture

Composes responses from:
1. Reactive component (answers user's immediate need)
2. Proactive components (advances conversation, 0-2 items)

Release 2.2 - Situational Awareness
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Literal


@dataclass
class ResponseComponent:
    """
    A single response component (reactive or proactive).
    
    Attributes:
        type: 'reactive' (answer user) or 'proactive' (advance conversation)
        pattern: Pattern definition dict
        priority: Trigger priority (critical, high, medium, low)
        token_budget: Maximum tokens for this component
    """
    type: Literal['reactive', 'proactive']
    pattern: Dict[str, Any]
    priority: str
    token_budget: int


@dataclass
class ComposedResponse:
    """
    Complete response composed of reactive + proactive components.
    
    Attributes:
        reactive: The reactive component (always present)
        proactive: List of proactive components (0-2 items)
        total_tokens: Sum of all token budgets
    """
    reactive: ResponseComponent
    proactive: List[ResponseComponent]
    total_tokens: int


class ResponseComposer:
    """
    Selects and composes responses using reactive + proactive architecture.
    
    Selection Logic:
    - Reactive: Driven by highest-priority trigger
    - Proactive: Driven by situational awareness (situation affinity)
    - Prevents context jumping (proactive != reactive category)
    - Respects token budget (~310 tokens total)
    """
    
    def __init__(self):
        """Initialize response composer"""
        # Token budgets
        self.reactive_budget = 150
        self.proactive_1_budget = 100
        self.proactive_2_budget = 60
        self.max_total_tokens = 310
    
    def select_components(
        self,
        triggers: List[Dict[str, Any]],
        situation: Dict[str, float],
        patterns: List[Dict[str, Any]]
    ) -> ComposedResponse:
        """
        Select response components based on triggers and situation.
        
        Args:
            triggers: Detected triggers with priorities
            situation: Situational awareness composition (sums to 1.0)
            patterns: Available patterns
            
        Returns:
            ComposedResponse with reactive + proactive components
        """
        # 1. Select reactive component (trigger-driven)
        reactive = self._select_reactive(triggers, patterns)
        
        # 2. Select proactive components (situation-driven)
        proactive = self._select_proactive(
            situation,
            patterns,
            exclude_category=reactive.pattern.get('category'),
            max_count=2
        )
        
        # 3. Calculate total tokens
        total_tokens = reactive.token_budget + sum(p.token_budget for p in proactive)
        
        return ComposedResponse(
            reactive=reactive,
            proactive=proactive,
            total_tokens=total_tokens
        )
    
    def _select_reactive(
        self,
        triggers: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]]
    ) -> ResponseComponent:
        """
        Select reactive component based on highest-priority trigger.
        
        Args:
            triggers: Detected triggers
            patterns: Available patterns
            
        Returns:
            Reactive response component
        """
        if not triggers:
            # Fallback: no triggers
            return ResponseComponent(
                type='reactive',
                pattern={'id': 'FALLBACK', 'category': 'meta'},
                priority='low',
                token_budget=self.reactive_budget
            )
        
        # Sort triggers by priority
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        sorted_triggers = sorted(
            triggers,
            key=lambda t: priority_order.get(t.get('priority', 'medium'), 0),
            reverse=True
        )
        
        # Find pattern matching highest-priority trigger
        top_trigger = sorted_triggers[0]
        
        # Filter reactive patterns
        reactive_patterns = [
            p for p in patterns
            if p.get('response_type') == 'reactive'
        ]
        
        # Find matching pattern
        for pattern in reactive_patterns:
            pattern_triggers = pattern.get('triggers', [])
            if top_trigger['trigger_id'] in pattern_triggers:
                return ResponseComponent(
                    type='reactive',
                    pattern=pattern,
                    priority=top_trigger['priority'],
                    token_budget=self.reactive_budget
                )
        
        # Fallback: use first reactive pattern
        if reactive_patterns:
            return ResponseComponent(
                type='reactive',
                pattern=reactive_patterns[0],
                priority=top_trigger['priority'],
                token_budget=self.reactive_budget
            )
        
        # Fallback: no reactive patterns
        return ResponseComponent(
            type='reactive',
            pattern={'id': 'FALLBACK', 'category': 'meta'},
            priority='low',
            token_budget=self.reactive_budget
        )
    
    def _select_proactive(
        self,
        situation: Dict[str, float],
        patterns: List[Dict[str, Any]],
        exclude_category: str = None,
        max_count: int = 2
    ) -> List[ResponseComponent]:
        """
        Select proactive components based on situation affinity.
        
        Args:
            situation: Situational awareness composition
            patterns: Available patterns
            exclude_category: Category to exclude (prevent context jumping)
            max_count: Maximum number of proactive components
            
        Returns:
            List of proactive response components (0-2 items)
        """
        # Filter proactive patterns
        proactive_patterns = [
            p for p in patterns
            if p.get('response_type') == 'proactive'
            and p.get('category') != exclude_category  # Prevent context jumping
        ]
        
        if not proactive_patterns:
            return []
        
        # Score patterns by situation affinity
        scored_patterns = []
        for pattern in proactive_patterns:
            affinity = pattern.get('situation_affinity', {})
            # Calculate weighted score based on situation
            score = sum(
                affinity.get(dim, 0) * situation.get(dim, 0)
                for dim in situation.keys()
            )
            scored_patterns.append((score, pattern))
        
        # Sort by score (highest first)
        scored_patterns.sort(key=lambda x: x[0], reverse=True)
        
        # Select top patterns (up to max_count)
        selected = []
        for i, (score, pattern) in enumerate(scored_patterns[:max_count]):
            if i == 0:
                budget = self.proactive_1_budget
            else:
                budget = self.proactive_2_budget
            
            selected.append(ResponseComponent(
                type='proactive',
                pattern=pattern,
                priority='medium' if i == 0 else 'low',
                token_budget=budget
            ))
        
        return selected
