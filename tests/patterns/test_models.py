"""
Tests for pattern data models (TDD - Red Phase)
"""
import pytest
from src.patterns.models import (
    TriggerType,
    TriggerCondition,
    BehaviorSpec,
    KnowledgeUpdates,
    Pattern
)


class TestTriggerType:
    """Test TriggerType enum"""
    
    def test_trigger_types_exist(self):
        """Test all trigger types are defined"""
        assert TriggerType.USER_EXPLICIT.value == "user_explicit"
        assert TriggerType.USER_IMPLICIT.value == "user_implicit"
        assert TriggerType.SYSTEM_PROACTIVE.value == "system_proactive"
        assert TriggerType.SYSTEM_REACTIVE.value == "system_reactive"


class TestTriggerCondition:
    """Test TriggerCondition dataclass"""
    
    def test_create_trigger_condition(self):
        """Test creating a trigger condition"""
        trigger = TriggerCondition(
            type=TriggerType.USER_EXPLICIT,
            keywords=["where are we", "status"],
            situation_affinity={"navigation": 0.8, "discovery": 0.2}
        )
        
        assert trigger.type == TriggerType.USER_EXPLICIT
        assert "where are we" in trigger.keywords
        assert trigger.situation_affinity["navigation"] == 0.8
    
    def test_trigger_condition_optional_fields(self):
        """Test trigger condition with minimal fields"""
        trigger = TriggerCondition(type=TriggerType.SYSTEM_REACTIVE)
        
        assert trigger.type == TriggerType.SYSTEM_REACTIVE
        assert trigger.keywords is None
        assert trigger.signals is None


class TestBehaviorSpec:
    """Test BehaviorSpec dataclass"""
    
    def test_create_behavior_spec(self):
        """Test creating a behavior specification"""
        behavior = BehaviorSpec(
            goal="Welcome first-time user",
            template="Hi! I help you figure out which AI pilots would work.",
            constraints={"max_words": 30, "tone": "professional"},
            teaches_user=["system_purpose", "how_to_start"]
        )
        
        assert behavior.goal == "Welcome first-time user"
        assert "AI pilots" in behavior.template
        assert behavior.constraints["max_words"] == 30
        assert "system_purpose" in behavior.teaches_user
    
    def test_behavior_with_situation_affinity(self):
        """Test behavior with situation affinity scores"""
        behavior = BehaviorSpec(
            goal="Explain system",
            template="Here's how it works...",
            constraints={},
            situation_affinity={"education": 0.9, "discovery": 0.1}
        )
        
        assert behavior.situation_affinity["education"] == 0.9


class TestKnowledgeUpdates:
    """Test KnowledgeUpdates dataclass"""
    
    def test_create_knowledge_updates(self):
        """Test creating knowledge updates"""
        updates = KnowledgeUpdates(
            user_knowledge={"knows_system_purpose": True},
            system_knowledge={"conversation_started": True}
        )
        
        assert updates.user_knowledge["knows_system_purpose"] is True
        assert updates.system_knowledge["conversation_started"] is True
    
    def test_empty_knowledge_updates(self):
        """Test empty knowledge updates"""
        updates = KnowledgeUpdates(
            user_knowledge={},
            system_knowledge={}
        )
        
        assert len(updates.user_knowledge) == 0
        assert len(updates.system_knowledge) == 0


class TestPattern:
    """Test Pattern dataclass"""
    
    def test_create_complete_pattern(self):
        """Test creating a complete pattern"""
        trigger = TriggerCondition(
            type=TriggerType.SYSTEM_REACTIVE,
            signals=["first_message"]
        )
        
        behavior = BehaviorSpec(
            goal="Welcome user",
            template="Hi! What output are you struggling with?",
            constraints={"max_words": 30}
        )
        
        updates = KnowledgeUpdates(
            user_knowledge={"knows_system_purpose": True},
            system_knowledge={"conversation_started": True}
        )
        
        pattern = Pattern(
            pattern_id="PATTERN_001_WELCOME",
            name="First-Time User Welcome",
            category="onboarding",
            trigger=trigger,
            behavior=behavior,
            updates=updates,
            metadata={"version": "1.0", "author": "system"}
        )
        
        assert pattern.pattern_id == "PATTERN_001_WELCOME"
        assert pattern.name == "First-Time User Welcome"
        assert pattern.category == "onboarding"
        assert pattern.trigger.type == TriggerType.SYSTEM_REACTIVE
        assert pattern.behavior.goal == "Welcome user"
        assert pattern.metadata["version"] == "1.0"
    
    def test_pattern_validation(self):
        """Test pattern validation method"""
        trigger = TriggerCondition(type=TriggerType.USER_EXPLICIT)
        behavior = BehaviorSpec(goal="Test", template="Test", constraints={})
        updates = KnowledgeUpdates(user_knowledge={}, system_knowledge={})
        
        pattern = Pattern(
            pattern_id="TEST_001",
            name="Test Pattern",
            category="test",
            trigger=trigger,
            behavior=behavior,
            updates=updates,
            metadata={}
        )
        
        # Should validate successfully
        assert pattern.validate() is True
    
    def test_pattern_validation_fails_missing_id(self):
        """Test validation fails with empty pattern_id"""
        trigger = TriggerCondition(type=TriggerType.USER_EXPLICIT)
        behavior = BehaviorSpec(goal="Test", template="Test", constraints={})
        updates = KnowledgeUpdates(user_knowledge={}, system_knowledge={})
        
        pattern = Pattern(
            pattern_id="",  # Empty ID
            name="Test",
            category="test",
            trigger=trigger,
            behavior=behavior,
            updates=updates,
            metadata={}
        )
        
        assert pattern.validate() is False
    
    def test_pattern_to_dict(self):
        """Test converting pattern to dictionary"""
        trigger = TriggerCondition(type=TriggerType.USER_EXPLICIT)
        behavior = BehaviorSpec(goal="Test", template="Test", constraints={})
        updates = KnowledgeUpdates(user_knowledge={}, system_knowledge={})
        
        pattern = Pattern(
            pattern_id="TEST_001",
            name="Test",
            category="test",
            trigger=trigger,
            behavior=behavior,
            updates=updates,
            metadata={}
        )
        
        pattern_dict = pattern.to_dict()
        
        assert pattern_dict["pattern_id"] == "TEST_001"
        assert pattern_dict["name"] == "Test"
        assert "trigger" in pattern_dict
        assert "behavior" in pattern_dict
    
    def test_pattern_from_dict(self):
        """Test creating pattern from dictionary"""
        pattern_dict = {
            "pattern_id": "TEST_001",
            "name": "Test Pattern",
            "category": "test",
            "trigger": {
                "type": "user_explicit",
                "keywords": ["test"]
            },
            "behavior": {
                "goal": "Test goal",
                "template": "Test template",
                "constraints": {}
            },
            "updates": {
                "user_knowledge": {},
                "system_knowledge": {}
            },
            "metadata": {}
        }
        
        pattern = Pattern.from_dict(pattern_dict)
        
        assert pattern.pattern_id == "TEST_001"
        assert pattern.name == "Test Pattern"
        assert pattern.trigger.type == TriggerType.USER_EXPLICIT
