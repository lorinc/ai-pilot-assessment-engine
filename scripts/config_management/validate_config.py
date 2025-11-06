#!/usr/bin/env python3
"""
Validate YAML configuration files for triggers and behaviors.

Usage:
    python scripts/validate_config.py
    python scripts/validate_config.py --file data/triggers/assessment_triggers.yaml
"""
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any


class ConfigValidator:
    """Validates trigger and behavior YAML files"""
    
    REQUIRED_TRIGGER_FIELDS = ['id', 'category', 'priority', 'type', 'detection']
    REQUIRED_DETECTION_FIELDS = ['method', 'examples']
    VALID_CATEGORIES = [
        'assessment', 'discovery', 'clarification', 'navigation',
        'recommendation', 'context_extraction', 'error_recovery', 'meta'
    ]
    VALID_PRIORITIES = ['low', 'medium', 'high', 'critical']
    VALID_TYPES = ['user_explicit', 'user_implicit', 'system_proactive', 'system_reactive']
    VALID_METHODS = ['semantic_similarity', 'regex', 'keywords']
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_trigger_file(self, filepath: Path) -> bool:
        """Validate a trigger YAML file"""
        print(f"\n📋 Validating: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML syntax error: {e}")
            return False
        except FileNotFoundError:
            self.errors.append(f"File not found: {filepath}")
            return False
        
        if not data:
            self.errors.append("Empty YAML file")
            return False
        
        if 'triggers' not in data:
            self.errors.append("Missing 'triggers' key")
            return False
        
        triggers = data['triggers']
        if not isinstance(triggers, list):
            self.errors.append("'triggers' must be a list")
            return False
        
        for i, trigger in enumerate(triggers):
            self._validate_trigger(trigger, i)
        
        return len(self.errors) == 0
    
    def _validate_trigger(self, trigger: Dict[str, Any], index: int):
        """Validate a single trigger"""
        prefix = f"Trigger {index}"
        
        # Check required fields
        for field in self.REQUIRED_TRIGGER_FIELDS:
            if field not in trigger:
                self.errors.append(f"{prefix}: Missing required field '{field}'")
        
        # Validate ID
        if 'id' in trigger:
            trigger_id = trigger['id']
            if not trigger_id.startswith('T_'):
                self.warnings.append(f"{prefix}: ID should start with 'T_' (got: {trigger_id})")
            if not trigger_id.isupper():
                self.warnings.append(f"{prefix}: ID should be uppercase (got: {trigger_id})")
        
        # Validate category
        if 'category' in trigger:
            if trigger['category'] not in self.VALID_CATEGORIES:
                self.errors.append(
                    f"{prefix}: Invalid category '{trigger['category']}'. "
                    f"Must be one of: {', '.join(self.VALID_CATEGORIES)}"
                )
        
        # Validate priority
        if 'priority' in trigger:
            if trigger['priority'] not in self.VALID_PRIORITIES:
                self.errors.append(
                    f"{prefix}: Invalid priority '{trigger['priority']}'. "
                    f"Must be one of: {', '.join(self.VALID_PRIORITIES)}"
                )
        
        # Validate type
        if 'type' in trigger:
            if trigger['type'] not in self.VALID_TYPES:
                self.errors.append(
                    f"{prefix}: Invalid type '{trigger['type']}'. "
                    f"Must be one of: {', '.join(self.VALID_TYPES)}"
                )
        
        # Validate detection
        if 'detection' in trigger:
            self._validate_detection(trigger['detection'], prefix)
    
    def _validate_detection(self, detection: Dict[str, Any], prefix: str):
        """Validate detection configuration"""
        # Check required fields
        for field in self.REQUIRED_DETECTION_FIELDS:
            if field not in detection:
                self.errors.append(f"{prefix}: Detection missing required field '{field}'")
        
        # Validate method
        if 'method' in detection:
            if detection['method'] not in self.VALID_METHODS:
                self.errors.append(
                    f"{prefix}: Invalid detection method '{detection['method']}'. "
                    f"Must be one of: {', '.join(self.VALID_METHODS)}"
                )
        
        # Validate examples
        if 'examples' in detection:
            examples = detection['examples']
            if not isinstance(examples, list):
                self.errors.append(f"{prefix}: Detection examples must be a list")
            elif len(examples) < 3:
                self.warnings.append(f"{prefix}: Detection has only {len(examples)} examples. Recommend at least 5 for good coverage.")
        
        # Validate threshold for semantic similarity
        if detection.get('method') == 'semantic_similarity':
            if 'threshold' in detection:
                threshold = detection['threshold']
                if not isinstance(threshold, (int, float)):
                    self.errors.append(f"{prefix}: Threshold must be a number")
                elif not (0.0 <= threshold <= 1.0):
                    self.errors.append(f"{prefix}: Threshold must be between 0.0 and 1.0")
            else:
                self.warnings.append(f"{prefix}: No threshold specified for semantic_similarity. Will use default 0.75")
    
    def print_results(self):
        """Print validation results"""
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")
        elif not self.errors:
            print("\n✅ No errors (warnings can be ignored)")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} error(s)")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate trigger and behavior YAML files')
    parser.add_argument('--file', help='Specific file to validate')
    args = parser.parse_args()
    
    validator = ConfigValidator()
    
    if args.file:
        # Validate specific file
        filepath = Path(args.file)
        success = validator.validate_trigger_file(filepath)
    else:
        # Validate all trigger files
        trigger_dir = Path('data/triggers')
        if not trigger_dir.exists():
            print(f"❌ Trigger directory not found: {trigger_dir}")
            sys.exit(1)
        
        trigger_files = list(trigger_dir.glob('*.yaml')) + list(trigger_dir.glob('*.yml'))
        
        if not trigger_files:
            print(f"⚠️  No YAML files found in {trigger_dir}")
            sys.exit(0)
        
        print(f"Found {len(trigger_files)} trigger file(s)")
        
        all_success = True
        for filepath in trigger_files:
            success = validator.validate_trigger_file(filepath)
            if not success:
                all_success = False
    
    validator.print_results()
    
    if validator.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
