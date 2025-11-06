#!/usr/bin/env python3
"""
Unified management CLI for pattern engine configuration.

Usage:
    # Triggers
    python scripts/manage.py create trigger --id T_NEW --category assessment --examples "..." "..."
    python scripts/manage.py update trigger T_RATE_EDGE --add-example "New example"
    python scripts/manage.py delete trigger T_OLD --confirm
    python scripts/manage.py show trigger T_RATE_EDGE
    python scripts/manage.py list triggers --category assessment
    
    # Behaviors
    python scripts/manage.py create behavior --id B_NEW --pattern PATTERN_X --template "..."
    python scripts/manage.py update behavior B_ACKNOWLEDGE --template "New template"
    python scripts/manage.py add-variant --pattern PATTERN_X --template "..." --weight 0.3
    
    # Patterns
    python scripts/manage.py create pattern --id PATTERN_NEW --triggers T_X --behaviors B_Y
    python scripts/manage.py update pattern PATTERN_X --add-trigger T_NEW
    python scripts/manage.py show pattern PATTERN_ACKNOWLEDGE_RATING
"""
import yaml
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess


class ConfigManager:
    """Manages pattern engine configuration (CRUD operations)"""
    
    def __init__(self):
        self.triggers_dir = Path('data/triggers')
        self.patterns_dir = Path('data/patterns')
        self.behaviors_dir = Path('data/patterns/behaviors')
        
        # Ensure directories exist
        self.triggers_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        self.behaviors_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize semantic detector if available
        try:
            from src.patterns.semantic_intent import get_detector
            self.semantic_detector = get_detector()
        except Exception:
            self.semantic_detector = None
    
    # ==================== TRIGGER OPERATIONS ====================
    
    def create_trigger(self, trigger_id: str, category: str, priority: str, 
                      examples: List[str], trigger_type: str = 'user_implicit',
                      method: str = 'semantic_similarity', threshold: float = 0.75,
                      description: str = None) -> bool:
        """Create a new trigger"""
        filepath = self.triggers_dir / f'{category}_triggers.yaml'
        
        # Load existing or create new
        data = self._load_yaml(filepath) or {'triggers': []}
        
        # Check if exists
        if self._find_trigger(data, trigger_id):
            print(f"❌ Trigger {trigger_id} already exists")
            return False
        
        # Create trigger
        new_trigger = {
            'id': trigger_id,
            'category': category,
            'priority': priority,
            'type': trigger_type,
            'detection': {
                'method': method,
                'threshold': threshold,
                'examples': examples
            }
        }
        
        if description:
            new_trigger['description'] = description
        
        data['triggers'].append(new_trigger)
        
        # Save
        self._save_yaml(filepath, data)
        print(f"✅ Created trigger {trigger_id} in {filepath}")
        
        # Precompute embeddings for semantic similarity
        if method == 'semantic_similarity' and self.semantic_detector:
            print(f"\n📊 Precomputing embeddings for {len(examples)} examples...")
            try:
                self.semantic_detector.precompute_embeddings(examples)
            except Exception as e:
                print(f"⚠️  Warning: Could not precompute embeddings: {e}")
        
        return self._validate_file(filepath)
    
    def update_trigger(self, trigger_id: str, **kwargs) -> bool:
        """Update an existing trigger"""
        # Find the trigger
        filepath, data, trigger = self._find_trigger_in_files(trigger_id)
        
        if not trigger:
            print(f"❌ Trigger {trigger_id} not found")
            return False
        
        print(f"📝 Updating trigger {trigger_id} in {filepath}")
        
        # Update fields
        if 'add_example' in kwargs and kwargs['add_example']:
            if 'detection' not in trigger:
                trigger['detection'] = {}
            if 'examples' not in trigger['detection']:
                trigger['detection']['examples'] = []
            trigger['detection']['examples'].append(kwargs['add_example'])
            print(f"   Added example: {kwargs['add_example']}")
        
        if 'remove_example' in kwargs and kwargs['remove_example']:
            if 'detection' in trigger and 'examples' in trigger['detection']:
                try:
                    trigger['detection']['examples'].remove(kwargs['remove_example'])
                    print(f"   Removed example: {kwargs['remove_example']}")
                except ValueError:
                    print(f"   ⚠️  Example not found: {kwargs['remove_example']}")
        
        if 'priority' in kwargs and kwargs['priority']:
            trigger['priority'] = kwargs['priority']
            print(f"   Updated priority: {kwargs['priority']}")
        
        if 'threshold' in kwargs and kwargs['threshold']:
            if 'detection' not in trigger:
                trigger['detection'] = {}
            trigger['detection']['threshold'] = kwargs['threshold']
            print(f"   Updated threshold: {kwargs['threshold']}")
        
        if 'description' in kwargs and kwargs['description']:
            trigger['description'] = kwargs['description']
            print(f"   Updated description")
        
        # Save
        self._save_yaml(filepath, data)
        print(f"✅ Updated trigger {trigger_id}")
        
        # Invalidate and recompute embeddings if examples changed
        if ('add_example' in kwargs or 'remove_example' in kwargs) and self.semantic_detector:
            if 'detection' in trigger and 'examples' in trigger['detection']:
                examples = trigger['detection']['examples']
                print(f"\n📊 Recomputing embeddings for {len(examples)} examples...")
                try:
                    # Clear old embeddings
                    self.semantic_detector.clear_cache(examples)
                    # Recompute
                    self.semantic_detector.precompute_embeddings(examples)
                except Exception as e:
                    print(f"⚠️  Warning: Could not recompute embeddings: {e}")
        
        return self._validate_file(filepath)
    
    def delete_trigger(self, trigger_id: str, confirm: bool = False) -> bool:
        """Delete a trigger"""
        if not confirm:
            print(f"❌ Must use --confirm to delete trigger {trigger_id}")
            return False
        
        # Find the trigger
        filepath, data, trigger = self._find_trigger_in_files(trigger_id)
        
        if not trigger:
            print(f"❌ Trigger {trigger_id} not found")
            return False
        
        # Remove from list
        data['triggers'] = [t for t in data['triggers'] if t['id'] != trigger_id]
        
        # Save
        self._save_yaml(filepath, data)
        print(f"✅ Deleted trigger {trigger_id} from {filepath}")
        
        return True
    
    def show_trigger(self, trigger_id: str) -> bool:
        """Show trigger details"""
        filepath, data, trigger = self._find_trigger_in_files(trigger_id)
        
        if not trigger:
            print(f"❌ Trigger {trigger_id} not found")
            return False
        
        print(f"\n📋 Trigger: {trigger_id}")
        print(f"   File: {filepath}")
        print(f"   Category: {trigger.get('category')}")
        print(f"   Priority: {trigger.get('priority')}")
        print(f"   Type: {trigger.get('type')}")
        
        if 'description' in trigger:
            print(f"   Description: {trigger['description']}")
        
        if 'detection' in trigger:
            detection = trigger['detection']
            print(f"\n   Detection:")
            print(f"     Method: {detection.get('method')}")
            if 'threshold' in detection:
                print(f"     Threshold: {detection['threshold']}")
            if 'examples' in detection:
                print(f"     Examples ({len(detection['examples'])}):")
                for i, example in enumerate(detection['examples'][:5], 1):
                    print(f"       {i}. {example}")
                if len(detection['examples']) > 5:
                    print(f"       ... and {len(detection['examples']) - 5} more")
        
        print()
        return True
    
    def list_triggers(self, category: Optional[str] = None) -> bool:
        """List all triggers"""
        all_triggers = []
        
        # Load all trigger files
        for filepath in self.triggers_dir.glob('*.yaml'):
            data = self._load_yaml(filepath)
            if data and 'triggers' in data:
                for trigger in data['triggers']:
                    trigger['_file'] = filepath.name
                    all_triggers.append(trigger)
        
        # Filter by category if specified
        if category:
            all_triggers = [t for t in all_triggers if t.get('category') == category]
        
        if not all_triggers:
            print(f"No triggers found" + (f" in category '{category}'" if category else ""))
            return True
        
        print(f"\n📋 Found {len(all_triggers)} trigger(s)" + (f" in category '{category}'" if category else ""))
        print()
        
        # Group by category
        by_category = {}
        for trigger in all_triggers:
            cat = trigger.get('category', 'unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(trigger)
        
        for cat, triggers in sorted(by_category.items()):
            print(f"  {cat}:")
            for trigger in triggers:
                examples_count = len(trigger.get('detection', {}).get('examples', []))
                print(f"    • {trigger['id']} ({trigger.get('priority')}) - {examples_count} examples")
        
        print()
        return True
    
    # ==================== PATTERN OPERATIONS ====================
    
    def create_pattern(self, pattern_id: str, category: str, response_type: str,
                      triggers: List[str], behaviors: List[Dict[str, Any]],
                      situation_affinity: Optional[Dict[str, float]] = None) -> bool:
        """Create a new pattern"""
        filepath = self.patterns_dir / f'{category}_patterns.yaml'
        
        # Load existing or create new
        data = self._load_yaml(filepath) or {'patterns': []}
        
        # Check if exists
        if any(p['id'] == pattern_id for p in data.get('patterns', [])):
            print(f"❌ Pattern {pattern_id} already exists")
            return False
        
        # Create pattern
        new_pattern = {
            'id': pattern_id,
            'category': category,
            'response_type': response_type,
            'triggers': triggers,
            'behaviors': behaviors
        }
        
        if situation_affinity:
            new_pattern['situation_affinity'] = situation_affinity
        
        if 'patterns' not in data:
            data['patterns'] = []
        
        data['patterns'].append(new_pattern)
        
        # Save
        self._save_yaml(filepath, data)
        print(f"✅ Created pattern {pattern_id} in {filepath}")
        
        return True
    
    def show_pattern(self, pattern_id: str) -> bool:
        """Show pattern details"""
        # Find pattern
        for filepath in self.patterns_dir.glob('*_patterns.yaml'):
            data = self._load_yaml(filepath)
            if data and 'patterns' in data:
                for pattern in data['patterns']:
                    if pattern['id'] == pattern_id:
                        print(f"\n📋 Pattern: {pattern_id}")
                        print(f"   File: {filepath}")
                        print(f"   Category: {pattern.get('category')}")
                        print(f"   Response Type: {pattern.get('response_type')}")
                        print(f"   Triggers: {', '.join(pattern.get('triggers', []))}")
                        print(f"   Behaviors: {len(pattern.get('behaviors', []))}")
                        
                        if 'situation_affinity' in pattern:
                            print(f"\n   Situation Affinity:")
                            for dim, score in pattern['situation_affinity'].items():
                                print(f"     {dim}: {score}")
                        
                        if 'behaviors' in pattern:
                            print(f"\n   Behavior Variants:")
                            for i, behavior in enumerate(pattern['behaviors'], 1):
                                weight = behavior.get('weight', 1.0)
                                print(f"     {i}. {behavior.get('id')} (weight: {weight})")
                        
                        print()
                        return True
        
        print(f"❌ Pattern {pattern_id} not found")
        return False
    
    # ==================== HELPER METHODS ====================
    
    def _load_yaml(self, filepath: Path) -> Optional[Dict]:
        """Load YAML file"""
        if not filepath.exists():
            return None
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return None
    
    def _save_yaml(self, filepath: Path, data: Dict):
        """Save YAML file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)
    
    def _find_trigger(self, data: Dict, trigger_id: str) -> Optional[Dict]:
        """Find trigger in data"""
        for trigger in data.get('triggers', []):
            if trigger['id'] == trigger_id:
                return trigger
        return None
    
    def _find_trigger_in_files(self, trigger_id: str) -> tuple:
        """Find trigger across all files"""
        for filepath in self.triggers_dir.glob('*.yaml'):
            data = self._load_yaml(filepath)
            if data:
                trigger = self._find_trigger(data, trigger_id)
                if trigger:
                    return filepath, data, trigger
        return None, None, None
    
    def _validate_file(self, filepath: Path) -> bool:
        """Validate a YAML file"""
        # For now, do basic YAML validation inline
        # Full validation requires the validate_config.py script
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            
            # Basic checks
            if 'triggers' in data:
                for trigger in data['triggers']:
                    if 'id' not in trigger:
                        print(f"❌ Validation failed: Missing 'id' in trigger")
                        return False
                    if 'category' not in trigger:
                        print(f"❌ Validation failed: Missing 'category' in trigger {trigger.get('id')}")
                        return False
                    if 'priority' not in trigger:
                        print(f"❌ Validation failed: Missing 'priority' in trigger {trigger.get('id')}")
                        return False
            
            return True
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Unified management CLI for pattern engine configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='operation', help='Operation to perform')
    
    # CREATE
    create_parser = subparsers.add_parser('create', help='Create a new element')
    create_sub = create_parser.add_subparsers(dest='element')
    
    # Create trigger
    create_trigger = create_sub.add_parser('trigger', help='Create a new trigger')
    create_trigger.add_argument('--id', required=True, help='Trigger ID (e.g., T_NEW)')
    create_trigger.add_argument('--category', required=True, help='Category')
    create_trigger.add_argument('--priority', required=True, choices=['low', 'medium', 'high', 'critical'])
    create_trigger.add_argument('--examples', nargs='+', required=True, help='Example messages')
    create_trigger.add_argument('--type', default='user_implicit', help='Trigger type')
    create_trigger.add_argument('--method', default='semantic_similarity', help='Detection method')
    create_trigger.add_argument('--threshold', type=float, default=0.75, help='Similarity threshold')
    create_trigger.add_argument('--description', help='Description')
    
    # Create pattern
    create_pattern = create_sub.add_parser('pattern', help='Create a new pattern')
    create_pattern.add_argument('--id', required=True, help='Pattern ID')
    create_pattern.add_argument('--category', required=True, help='Category')
    create_pattern.add_argument('--response-type', required=True, choices=['reactive', 'proactive'])
    create_pattern.add_argument('--triggers', nargs='+', required=True, help='Trigger IDs')
    create_pattern.add_argument('--behavior-id', required=True, help='Behavior ID')
    create_pattern.add_argument('--behavior-template', required=True, help='Behavior template')
    
    # UPDATE
    update_parser = subparsers.add_parser('update', help='Update an existing element')
    update_sub = update_parser.add_subparsers(dest='element')
    
    # Update trigger
    update_trigger = update_sub.add_parser('trigger', help='Update a trigger')
    update_trigger.add_argument('id', help='Trigger ID')
    update_trigger.add_argument('--add-example', help='Add an example')
    update_trigger.add_argument('--remove-example', help='Remove an example')
    update_trigger.add_argument('--priority', choices=['low', 'medium', 'high', 'critical'])
    update_trigger.add_argument('--threshold', type=float, help='Update threshold')
    update_trigger.add_argument('--description', help='Update description')
    
    # DELETE
    delete_parser = subparsers.add_parser('delete', help='Delete an element')
    delete_sub = delete_parser.add_subparsers(dest='element')
    
    # Delete trigger
    delete_trigger = delete_sub.add_parser('trigger', help='Delete a trigger')
    delete_trigger.add_argument('id', help='Trigger ID')
    delete_trigger.add_argument('--confirm', action='store_true', help='Confirm deletion')
    
    # SHOW
    show_parser = subparsers.add_parser('show', help='Show element details')
    show_sub = show_parser.add_subparsers(dest='element')
    
    # Show trigger
    show_trigger = show_sub.add_parser('trigger', help='Show trigger details')
    show_trigger.add_argument('id', help='Trigger ID')
    
    # Show pattern
    show_pattern = show_sub.add_parser('pattern', help='Show pattern details')
    show_pattern.add_argument('id', help='Pattern ID')
    
    # LIST
    list_parser = subparsers.add_parser('list', help='List elements')
    list_sub = list_parser.add_subparsers(dest='element')
    
    # List triggers
    list_triggers = list_sub.add_parser('triggers', help='List all triggers')
    list_triggers.add_argument('--category', help='Filter by category')
    
    # CACHE MANAGEMENT
    cache_parser = subparsers.add_parser('clear-cache', help='Clear embedding cache')
    cache_parser.add_argument('--trigger', help='Clear cache for specific trigger')
    cache_parser.add_argument('--all', action='store_true', help='Clear all caches')
    
    rebuild_parser = subparsers.add_parser('rebuild-embeddings', help='Rebuild all embeddings')
    rebuild_parser.add_argument('--force', action='store_true', help='Force rebuild even if cached')
    
    stats_parser = subparsers.add_parser('cache-stats', help='Show cache statistics')
    
    args = parser.parse_args()
    
    if not args.operation:
        parser.print_help()
        sys.exit(1)
    
    manager = ConfigManager()
    
    # Route to appropriate method
    if args.operation == 'create':
        if args.element == 'trigger':
            success = manager.create_trigger(
                trigger_id=args.id,
                category=args.category,
                priority=args.priority,
                examples=args.examples,
                trigger_type=args.type,
                method=args.method,
                threshold=args.threshold,
                description=args.description
            )
        elif args.element == 'pattern':
            behaviors = [{
                'id': args.behavior_id,
                'weight': 1.0,
                'template': args.behavior_template
            }]
            success = manager.create_pattern(
                pattern_id=args.id,
                category=args.category,
                response_type=args.response_type,
                triggers=args.triggers,
                behaviors=behaviors
            )
        else:
            print(f"❌ Unknown element: {args.element}")
            sys.exit(1)
    
    elif args.operation == 'update':
        if args.element == 'trigger':
            success = manager.update_trigger(
                trigger_id=args.id,
                add_example=args.add_example,
                remove_example=args.remove_example,
                priority=args.priority,
                threshold=args.threshold,
                description=args.description
            )
        else:
            print(f"❌ Unknown element: {args.element}")
            sys.exit(1)
    
    elif args.operation == 'delete':
        if args.element == 'trigger':
            success = manager.delete_trigger(args.id, args.confirm)
        else:
            print(f"❌ Unknown element: {args.element}")
            sys.exit(1)
    
    elif args.operation == 'show':
        if args.element == 'trigger':
            success = manager.show_trigger(args.id)
        elif args.element == 'pattern':
            success = manager.show_pattern(args.id)
        else:
            print(f"❌ Unknown element: {args.element}")
            sys.exit(1)
    
    elif args.operation == 'list':
        if args.element == 'triggers':
            success = manager.list_triggers(args.category)
        else:
            print(f"❌ Unknown element: {args.element}")
            sys.exit(1)
    
    elif args.operation == 'clear-cache':
        if not manager.semantic_detector:
            print("❌ Semantic detector not available")
            sys.exit(1)
        
        if args.all:
            manager.semantic_detector.clear_cache()
            success = True
        elif args.trigger:
            # Find trigger and clear its examples
            filepath, data, trigger = manager._find_trigger_in_files(args.trigger)
            if trigger and 'detection' in trigger and 'examples' in trigger['detection']:
                examples = trigger['detection']['examples']
                manager.semantic_detector.clear_cache(examples)
                success = True
            else:
                print(f"❌ Trigger {args.trigger} not found or has no examples")
                success = False
        else:
            print("❌ Must specify --all or --trigger")
            success = False
    
    elif args.operation == 'rebuild-embeddings':
        if not manager.semantic_detector:
            print("❌ Semantic detector not available")
            sys.exit(1)
        
        print("🔄 Rebuilding all embeddings...")
        
        # Find all triggers with semantic similarity
        count = 0
        for filepath in manager.triggers_dir.glob('*.yaml'):
            data = manager._load_yaml(filepath)
            if data and 'triggers' in data:
                for trigger in data['triggers']:
                    if trigger.get('detection', {}).get('method') == 'semantic_similarity':
                        examples = trigger.get('detection', {}).get('examples', [])
                        if examples:
                            print(f"\n  Trigger: {trigger['id']} ({len(examples)} examples)")
                            manager.semantic_detector.precompute_embeddings(examples, force=args.force)
                            count += 1
        
        print(f"\n✅ Rebuilt embeddings for {count} triggers")
        success = True
    
    elif args.operation == 'cache-stats':
        if not manager.semantic_detector:
            print("❌ Semantic detector not available")
            sys.exit(1)
        
        stats = manager.semantic_detector.get_cache_stats()
        print("\n📊 Cache Statistics:")
        print(f"   In-memory: {stats['in_memory_count']} embeddings")
        print(f"   On-disk: {stats['persistent_count']} embeddings")
        print(f"   Cache dir: {stats['cache_dir']}")
        success = True
    
    else:
        print(f"❌ Unknown operation: {args.operation}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
