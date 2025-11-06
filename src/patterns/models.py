"""
Pattern data models for conversation pattern engine.

This module defines the core data structures for patterns, triggers, behaviors,
and knowledge tracking.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum


class TriggerType(Enum):
    """Types of triggers that can activate patterns"""
    USER_EXPLICIT = "user_explicit"
    USER_IMPLICIT = "user_implicit"
    SYSTEM_PROACTIVE = "system_proactive"
    SYSTEM_REACTIVE = "system_reactive"


@dataclass
class TriggerCondition:
    """
    Conditions that trigger a pattern.
    
    Attributes:
        type: Type of trigger (explicit, implicit, proactive, reactive)
        keywords: Keywords to match for user-explicit triggers
        signals: Signals to detect for user-implicit triggers
        requires: Prerequisites (knowledge state requirements)
        situation_affinity: Affinity scores for each situation dimension
    """
    type: TriggerType
    keywords: Optional[List[str]] = None
    signals: Optional[List[str]] = None
    requires: Optional[Dict[str, Any]] = None
    situation_affinity: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "type": self.type.value,
        }
        if self.keywords:
            result["keywords"] = self.keywords
        if self.signals:
            result["signals"] = self.signals
        if self.requires:
            result["requires"] = self.requires
        if self.situation_affinity:
            result["situation_affinity"] = self.situation_affinity
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TriggerCondition':
        """Create from dictionary"""
        return cls(
            type=TriggerType(data["type"]),
            keywords=data.get("keywords"),
            signals=data.get("signals"),
            requires=data.get("requires"),
            situation_affinity=data.get("situation_affinity")
        )


@dataclass
class BehaviorSpec:
    """
    Specification for pattern behavior.
    
    Attributes:
        goal: What this behavior aims to achieve
        template: Response template or action description
        constraints: Constraints on response (max_words, tone, etc.)
        teaches_user: What user learns from this behavior
        situation_affinity: Affinity scores for situation dimensions
    """
    goal: str
    template: str
    constraints: Dict[str, Any]
    teaches_user: Optional[List[str]] = None
    situation_affinity: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "goal": self.goal,
            "template": self.template,
            "constraints": self.constraints,
        }
        if self.teaches_user:
            result["teaches_user"] = self.teaches_user
        if self.situation_affinity:
            result["situation_affinity"] = self.situation_affinity
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BehaviorSpec':
        """Create from dictionary"""
        return cls(
            goal=data["goal"],
            template=data["template"],
            constraints=data.get("constraints", {}),
            teaches_user=data.get("teaches_user"),
            situation_affinity=data.get("situation_affinity")
        )


@dataclass
class KnowledgeUpdates:
    """
    Knowledge state updates after pattern execution.
    
    Attributes:
        user_knowledge: Updates to user knowledge (what user knows)
        system_knowledge: Updates to system knowledge (what system knows)
    """
    user_knowledge: Dict[str, Any]
    system_knowledge: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_knowledge": self.user_knowledge,
            "system_knowledge": self.system_knowledge
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeUpdates':
        """Create from dictionary"""
        return cls(
            user_knowledge=data.get("user_knowledge", {}),
            system_knowledge=data.get("system_knowledge", {})
        )


@dataclass
class Pattern:
    """
    Complete pattern definition.
    
    A pattern combines a trigger condition, behavior specification, and
    knowledge updates to define a conversation pattern.
    
    Attributes:
        pattern_id: Unique identifier (e.g., "PATTERN_001_WELCOME")
        name: Human-readable name
        category: Pattern category (onboarding, discovery, etc.)
        trigger: Trigger condition
        behavior: Behavior specification
        updates: Knowledge updates
        metadata: Additional metadata (version, author, etc.)
    """
    pattern_id: str
    name: str
    category: str
    trigger: TriggerCondition
    behavior: BehaviorSpec
    updates: KnowledgeUpdates
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """
        Validate pattern structure.
        
        Returns:
            True if pattern is valid, False otherwise
        """
        # Check required fields
        if not self.pattern_id or not self.pattern_id.strip():
            return False
        
        if not self.name or not self.name.strip():
            return False
        
        if not self.category or not self.category.strip():
            return False
        
        # Validate trigger
        if not isinstance(self.trigger, TriggerCondition):
            return False
        
        # Validate behavior
        if not isinstance(self.behavior, BehaviorSpec):
            return False
        
        if not self.behavior.goal or not self.behavior.template:
            return False
        
        # Validate updates
        if not isinstance(self.updates, KnowledgeUpdates):
            return False
        
        # Validate situation affinity sums (if present)
        if self.behavior.situation_affinity:
            total = sum(self.behavior.situation_affinity.values())
            # Allow some tolerance for floating point
            if not (0.99 <= total <= 1.01):
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary"""
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "category": self.category,
            "trigger": self.trigger.to_dict(),
            "behavior": self.behavior.to_dict(),
            "updates": self.updates.to_dict(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        """Create pattern from dictionary"""
        return cls(
            pattern_id=data["pattern_id"],
            name=data["name"],
            category=data["category"],
            trigger=TriggerCondition.from_dict(data["trigger"]),
            behavior=BehaviorSpec.from_dict(data["behavior"]),
            updates=KnowledgeUpdates.from_dict(data["updates"]),
            metadata=data.get("metadata", {})
        )
