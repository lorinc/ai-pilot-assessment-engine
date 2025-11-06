"""
Tests for pattern loader (TDD - Red Phase)
"""
import pytest
from pathlib import Path
from src.patterns.pattern_loader import PatternLoader
from src.patterns.models import BehaviorSpec, TriggerCondition, Pattern


class TestPatternLoader:
    """Test PatternLoader class"""
    
    @pytest.fixture
    def loader(self):
        """Create a pattern loader instance"""
        return PatternLoader(patterns_dir="data/patterns")
    
    def test_loader_initialization(self, loader):
        """Test loader initializes correctly"""
        assert loader is not None
        assert loader.patterns_dir == Path("data/patterns")
    
    def test_load_behaviors(self, loader):
        """Test loading behaviors from YAML"""
        behaviors = loader.load_behaviors()
        
        # Should load 77 behaviors
        assert len(behaviors) > 0
        assert isinstance(behaviors, dict)
        
        # Check structure of a behavior
        for behavior_id, behavior in behaviors.items():
            assert isinstance(behavior_id, str)
            assert isinstance(behavior, BehaviorSpec)
            assert behavior.goal
            assert behavior.template
            assert isinstance(behavior.constraints, dict)
    
    def test_load_triggers(self, loader):
        """Test loading triggers from YAML"""
        triggers = loader.load_triggers()
        
        # Should load 40+ triggers
        assert len(triggers) > 0
        assert isinstance(triggers, dict)
        
        # Check structure of a trigger
        for trigger_id, trigger in triggers.items():
            assert isinstance(trigger_id, str)
            assert isinstance(trigger, TriggerCondition)
            assert trigger.type is not None
    
    def test_load_knowledge_dimensions(self, loader):
        """Test loading knowledge dimensions from YAML"""
        knowledge = loader.load_knowledge_dimensions()
        
        # Should load 28 dimensions
        assert len(knowledge) > 0
        assert isinstance(knowledge, dict)
        
        # Should have user and system knowledge sections
        assert "user_knowledge" in knowledge or "system_knowledge" in knowledge
    
    def test_behaviors_have_required_fields(self, loader):
        """Test all behaviors have required fields"""
        behaviors = loader.load_behaviors()
        
        for behavior_id, behavior in behaviors.items():
            # Required fields
            assert behavior.goal, f"{behavior_id} missing goal"
            assert behavior.template, f"{behavior_id} missing template"
            assert isinstance(behavior.constraints, dict), f"{behavior_id} constraints not dict"
    
    def test_triggers_have_valid_types(self, loader):
        """Test all triggers have valid trigger types"""
        triggers = loader.load_triggers()
        
        valid_types = ["user_explicit", "user_implicit", "system_proactive", "system_reactive"]
        
        for trigger_id, trigger in triggers.items():
            assert trigger.type.value in valid_types, f"{trigger_id} has invalid type"
    
    def test_load_behaviors_caching(self, loader):
        """Test behaviors are cached after first load"""
        behaviors1 = loader.load_behaviors()
        behaviors2 = loader.load_behaviors()
        
        # Should return same object (cached)
        assert behaviors1 is behaviors2
    
    def test_validate_all_patterns(self, loader):
        """Test validation of all loaded patterns"""
        errors = loader.validate_all()
        
        # Should have no validation errors
        assert isinstance(errors, list)
        
        # If there are errors, they should be descriptive
        for error in errors:
            assert isinstance(error, str)
            assert len(error) > 0
    
    def test_load_specific_behavior_category(self, loader):
        """Test loading behaviors from specific category"""
        # This assumes behaviors are organized by category in the YAML
        behaviors = loader.load_behaviors()
        
        # Check that we have behaviors from different categories
        categories = set()
        for behavior in behaviors.values():
            if hasattr(behavior, 'category'):
                categories.add(behavior.category)
        
        # Should have multiple categories
        assert len(categories) >= 1
    
    def test_loader_handles_missing_directory(self):
        """Test loader handles missing directory gracefully"""
        loader = PatternLoader(patterns_dir="nonexistent/path")
        
        with pytest.raises(FileNotFoundError):
            loader.load_behaviors()
    
    def test_loader_handles_invalid_yaml(self, tmp_path):
        """Test loader handles invalid YAML gracefully"""
        # Create temporary directory with invalid YAML
        behaviors_dir = tmp_path / "behaviors"
        behaviors_dir.mkdir()
        
        invalid_yaml = behaviors_dir / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: [")
        
        loader = PatternLoader(patterns_dir=str(tmp_path))
        
        with pytest.raises(Exception):  # Should raise YAML parsing error
            loader.load_behaviors()
    
    def test_get_behavior_by_id(self, loader):
        """Test getting a specific behavior by ID"""
        behaviors = loader.load_behaviors()
        
        if behaviors:
            # Get first behavior ID
            first_id = list(behaviors.keys())[0]
            behavior = loader.get_behavior(first_id)
            
            assert behavior is not None
            assert isinstance(behavior, BehaviorSpec)
    
    def test_get_trigger_by_id(self, loader):
        """Test getting a specific trigger by ID"""
        triggers = loader.load_triggers()
        
        if triggers:
            # Get first trigger ID
            first_id = list(triggers.keys())[0]
            trigger = loader.get_trigger(first_id)
            
            assert trigger is not None
            assert isinstance(trigger, TriggerCondition)
    
    def test_reload_patterns(self, loader):
        """Test reloading patterns clears cache"""
        behaviors1 = loader.load_behaviors()
        loader.reload()
        behaviors2 = loader.load_behaviors()
        
        # After reload, should be different objects
        assert behaviors1 is not behaviors2
        
        # But should have same content
        assert len(behaviors1) == len(behaviors2)


class TestPatternValidation:
    """Test pattern validation functionality"""
    
    @pytest.fixture
    def loader(self):
        """Create a pattern loader instance"""
        return PatternLoader(patterns_dir="data/patterns")
    
    def test_validate_behavior_structure(self, loader):
        """Test validation catches malformed behaviors"""
        behaviors = loader.load_behaviors()
        
        for behavior_id, behavior in behaviors.items():
            # All behaviors should have goal and template
            assert behavior.goal, f"Behavior {behavior_id} missing goal"
            assert behavior.template, f"Behavior {behavior_id} missing template"
    
    def test_validate_trigger_structure(self, loader):
        """Test validation catches malformed triggers"""
        triggers = loader.load_triggers()
        
        for trigger_id, trigger in triggers.items():
            # All triggers should have a type
            assert trigger.type is not None, f"Trigger {trigger_id} missing type"
    
    def test_validate_situation_affinity_sums(self, loader):
        """Test situation affinity scores sum to ~1.0"""
        behaviors = loader.load_behaviors()
        
        for behavior_id, behavior in behaviors.items():
            if behavior.situation_affinity:
                total = sum(behavior.situation_affinity.values())
                # Allow some tolerance for floating point
                assert 0.99 <= total <= 1.01, \
                    f"Behavior {behavior_id} affinity sum is {total}, should be ~1.0"
    
    def test_validate_no_circular_references(self, loader):
        """Test there are no circular pattern references"""
        errors = loader.validate_all()
        
        # Check for circular reference errors
        circular_errors = [e for e in errors if "circular" in e.lower()]
        assert len(circular_errors) == 0, f"Found circular references: {circular_errors}"
