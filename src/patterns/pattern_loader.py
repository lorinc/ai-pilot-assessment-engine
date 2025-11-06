"""
Pattern loader for loading patterns from YAML files.

This module handles loading behaviors, triggers, and knowledge dimensions
from YAML files and converting them to Python objects.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from .models import Pattern, TriggerCondition, BehaviorSpec, TriggerType, KnowledgeUpdates


class PatternLoader:
    """
    Loads patterns from YAML files.
    
    Handles loading behaviors, triggers, and knowledge dimensions from
    the data/patterns directory and provides caching for performance.
    """
    
    def __init__(self, patterns_dir: str = "data/patterns"):
        """
        Initialize pattern loader.
        
        Args:
            patterns_dir: Path to patterns directory
        """
        self.patterns_dir = Path(patterns_dir)
        self._behaviors_cache: Optional[Dict[str, BehaviorSpec]] = None
        self._triggers_cache: Optional[Dict[str, TriggerCondition]] = None
        self._knowledge_cache: Optional[Dict[str, Any]] = None
    
    def load_behaviors(self) -> Dict[str, BehaviorSpec]:
        """
        Load all behaviors from YAML files.
        
        Returns:
            Dictionary mapping behavior IDs to BehaviorSpec objects
            
        Raises:
            FileNotFoundError: If behaviors directory doesn't exist
        """
        if self._behaviors_cache is not None:
            return self._behaviors_cache
        
        behaviors_file = self.patterns_dir / "behaviors" / "atomic_behaviors.yaml"
        
        if not behaviors_file.exists():
            raise FileNotFoundError(f"Behaviors file not found: {behaviors_file}")
        
        with open(behaviors_file, 'r') as f:
            # Load all documents (YAML file has multiple documents separated by ---)
            documents = list(yaml.safe_load_all(f))
        
        behaviors = {}
        
        # Parse behaviors from YAML structure
        # The YAML has multiple documents, each with categories as top-level keys
        for data in documents:
            if not data:
                continue
            for category, category_behaviors in data.items():
                if isinstance(category_behaviors, list):
                    for behavior_data in category_behaviors:
                        behavior_id = behavior_data.get('id')
                        if behavior_id:
                            behaviors[behavior_id] = self._parse_behavior(behavior_data)
        
        self._behaviors_cache = behaviors
        return behaviors
    
    def _parse_behavior(self, data: Dict[str, Any]) -> BehaviorSpec:
        """Parse behavior from YAML data"""
        return BehaviorSpec(
            goal=data.get('goal', ''),
            template=data.get('template', ''),
            constraints=data.get('constraints', {}),
            teaches_user=data.get('teaches'),
            situation_affinity=data.get('situation_affinity')
        )
    
    def load_triggers(self) -> Dict[str, TriggerCondition]:
        """
        Load all triggers from YAML files.
        
        Returns:
            Dictionary mapping trigger IDs to TriggerCondition objects
            
        Raises:
            FileNotFoundError: If triggers directory doesn't exist
        """
        if self._triggers_cache is not None:
            return self._triggers_cache
        
        triggers_file = self.patterns_dir / "triggers" / "atomic_triggers.yaml"
        
        if not triggers_file.exists():
            raise FileNotFoundError(f"Triggers file not found: {triggers_file}")
        
        with open(triggers_file, 'r') as f:
            # Load all documents (YAML file has multiple documents separated by ---)
            documents = list(yaml.safe_load_all(f))
        
        triggers = {}
        
        # Parse triggers from YAML structure
        for data in documents:
            if not data:
                continue
            for trigger_type, type_triggers in data.items():
                if isinstance(type_triggers, list):
                    for trigger_data in type_triggers:
                        trigger_id = trigger_data.get('id')
                        if trigger_id:
                            triggers[trigger_id] = self._parse_trigger(trigger_data, trigger_type)
        
        self._triggers_cache = triggers
        return triggers
    
    def _parse_trigger(self, data: Dict[str, Any], trigger_type: str) -> TriggerCondition:
        """Parse trigger from YAML data"""
        # Map YAML trigger type to TriggerType enum
        type_mapping = {
            'user_explicit': TriggerType.USER_EXPLICIT,
            'user_implicit': TriggerType.USER_IMPLICIT,
            'system_proactive': TriggerType.SYSTEM_PROACTIVE,
            'system_reactive': TriggerType.SYSTEM_REACTIVE,
        }
        
        return TriggerCondition(
            type=type_mapping.get(trigger_type, TriggerType.USER_EXPLICIT),
            keywords=data.get('keywords'),
            signals=data.get('signals'),
            requires=data.get('requires'),
            situation_affinity=data.get('situation_affinity')
        )
    
    def load_knowledge_dimensions(self) -> Dict[str, Any]:
        """
        Load knowledge dimension definitions.
        
        Returns:
            Dictionary containing user and system knowledge dimensions
            
        Raises:
            FileNotFoundError: If knowledge dimensions file doesn't exist
        """
        if self._knowledge_cache is not None:
            return self._knowledge_cache
        
        knowledge_file = self.patterns_dir / "knowledge_dimensions.yaml"
        
        if not knowledge_file.exists():
            raise FileNotFoundError(f"Knowledge dimensions file not found: {knowledge_file}")
        
        with open(knowledge_file, 'r') as f:
            # Load all documents (YAML file may have multiple documents)
            documents = list(yaml.safe_load_all(f))
            # Merge all documents into one
            data = {}
            for doc in documents:
                if doc:
                    data.update(doc)
        
        self._knowledge_cache = data
        return data
    
    def get_behavior(self, behavior_id: str) -> Optional[BehaviorSpec]:
        """
        Get a specific behavior by ID.
        
        Args:
            behavior_id: Behavior identifier
            
        Returns:
            BehaviorSpec if found, None otherwise
        """
        behaviors = self.load_behaviors()
        return behaviors.get(behavior_id)
    
    def get_trigger(self, trigger_id: str) -> Optional[TriggerCondition]:
        """
        Get a specific trigger by ID.
        
        Args:
            trigger_id: Trigger identifier
            
        Returns:
            TriggerCondition if found, None otherwise
        """
        triggers = self.load_triggers()
        return triggers.get(trigger_id)
    
    def reload(self):
        """Clear all caches and force reload on next access"""
        self._behaviors_cache = None
        self._triggers_cache = None
        self._knowledge_cache = None
    
    def validate_all(self) -> List[str]:
        """
        Validate all loaded patterns.
        
        Returns:
            List of validation error messages (empty if all valid)
        """
        errors = []
        
        try:
            # Validate behaviors
            behaviors = self.load_behaviors()
            for behavior_id, behavior in behaviors.items():
                if not behavior.goal:
                    errors.append(f"Behavior {behavior_id} missing goal")
                if not behavior.template:
                    errors.append(f"Behavior {behavior_id} missing template")
                
                # Validate situation affinity sums
                if behavior.situation_affinity:
                    total = sum(behavior.situation_affinity.values())
                    if not (0.99 <= total <= 1.01):
                        errors.append(
                            f"Behavior {behavior_id} situation affinity sums to {total}, "
                            f"should be ~1.0"
                        )
        except Exception as e:
            errors.append(f"Error loading behaviors: {str(e)}")
        
        try:
            # Validate triggers
            triggers = self.load_triggers()
            for trigger_id, trigger in triggers.items():
                if trigger.type is None:
                    errors.append(f"Trigger {trigger_id} missing type")
        except Exception as e:
            errors.append(f"Error loading triggers: {str(e)}")
        
        try:
            # Validate knowledge dimensions
            knowledge = self.load_knowledge_dimensions()
            if not knowledge:
                errors.append("Knowledge dimensions file is empty")
        except Exception as e:
            errors.append(f"Error loading knowledge dimensions: {str(e)}")
        
        return errors
