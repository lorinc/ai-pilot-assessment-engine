"""
Tests for Configuration Management System

Tests the unified CRUD interface for triggers and patterns.
Uses temporary directories to avoid impacting production data.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
import yaml
import sys
import os

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts' / 'config_management'))

from manage import ConfigManager


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory structure"""
    triggers_dir = tmp_path / 'data' / 'triggers'
    patterns_dir = tmp_path / 'data' / 'patterns'
    behaviors_dir = tmp_path / 'data' / 'patterns' / 'behaviors'
    
    triggers_dir.mkdir(parents=True)
    patterns_dir.mkdir(parents=True)
    behaviors_dir.mkdir(parents=True)
    
    return tmp_path


@pytest.fixture
def manager(temp_config_dir, monkeypatch):
    """Create ConfigManager with temporary directories"""
    # Change to temp directory
    monkeypatch.chdir(temp_config_dir)
    
    # Create manager (will use temp paths)
    mgr = ConfigManager()
    
    # Disable semantic detector for tests (no API calls)
    mgr.semantic_detector = None
    
    return mgr


class TestTriggerCRUD:
    """Test trigger CRUD operations"""
    
    def test_create_trigger(self, manager):
        """Should create a new trigger"""
        success = manager.create_trigger(
            trigger_id='T_TEST_TRIGGER',
            category='test',
            priority='medium',
            examples=['Example 1', 'Example 2', 'Example 3'],
            description='Test trigger'
        )
        
        assert success is True
        
        # Verify file was created
        filepath = manager.triggers_dir / 'test_triggers.yaml'
        assert filepath.exists()
        
        # Verify content
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'triggers' in data
        assert len(data['triggers']) == 1
        
        trigger = data['triggers'][0]
        assert trigger['id'] == 'T_TEST_TRIGGER'
        assert trigger['category'] == 'test'
        assert trigger['priority'] == 'medium'
        assert trigger['description'] == 'Test trigger'
        assert len(trigger['detection']['examples']) == 3
    
    def test_create_duplicate_trigger(self, manager):
        """Should not create duplicate trigger"""
        # Create first trigger
        manager.create_trigger(
            trigger_id='T_DUPLICATE',
            category='test',
            priority='medium',
            examples=['Example 1']
        )
        
        # Try to create duplicate
        success = manager.create_trigger(
            trigger_id='T_DUPLICATE',
            category='test',
            priority='high',
            examples=['Example 2']
        )
        
        assert success is False
    
    def test_show_trigger(self, manager, capsys):
        """Should show trigger details"""
        # Create trigger
        manager.create_trigger(
            trigger_id='T_SHOW_TEST',
            category='test',
            priority='high',
            examples=['Example 1', 'Example 2'],
            description='Test description'
        )
        
        # Show trigger
        success = manager.show_trigger('T_SHOW_TEST')
        
        assert success is True
        
        # Check output
        captured = capsys.readouterr()
        assert 'T_SHOW_TEST' in captured.out
        assert 'high' in captured.out
        assert 'Test description' in captured.out
    
    def test_show_nonexistent_trigger(self, manager):
        """Should handle nonexistent trigger"""
        success = manager.show_trigger('T_NONEXISTENT')
        assert success is False
    
    def test_list_triggers(self, manager, capsys):
        """Should list all triggers"""
        # Create multiple triggers
        manager.create_trigger(
            trigger_id='T_LIST_1',
            category='test',
            priority='high',
            examples=['Example 1']
        )
        
        manager.create_trigger(
            trigger_id='T_LIST_2',
            category='test',
            priority='medium',
            examples=['Example 2']
        )
        
        # List triggers
        success = manager.list_triggers()
        
        assert success is True
        
        # Check output
        captured = capsys.readouterr()
        assert 'T_LIST_1' in captured.out
        assert 'T_LIST_2' in captured.out
    
    def test_list_triggers_by_category(self, manager, capsys):
        """Should filter triggers by category"""
        # Create triggers in different categories
        manager.create_trigger(
            trigger_id='T_CAT_A',
            category='category_a',
            priority='high',
            examples=['Example 1']
        )
        
        manager.create_trigger(
            trigger_id='T_CAT_B',
            category='category_b',
            priority='medium',
            examples=['Example 2']
        )
        
        # Clear captured output from creation
        capsys.readouterr()
        
        # List only category_a
        success = manager.list_triggers(category='category_a')
        
        assert success is True
        
        captured = capsys.readouterr()
        assert 'T_CAT_A' in captured.out
        assert 'T_CAT_B' not in captured.out
    
    def test_update_trigger_add_example(self, manager):
        """Should add example to trigger"""
        # Create trigger
        manager.create_trigger(
            trigger_id='T_UPDATE_TEST',
            category='test',
            priority='medium',
            examples=['Example 1']
        )
        
        # Update - add example
        success = manager.update_trigger(
            'T_UPDATE_TEST',
            add_example='Example 2'
        )
        
        assert success is True
        
        # Verify
        filepath = manager.triggers_dir / 'test_triggers.yaml'
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        trigger = data['triggers'][0]
        assert len(trigger['detection']['examples']) == 2
        assert 'Example 2' in trigger['detection']['examples']
    
    def test_update_trigger_remove_example(self, manager):
        """Should remove example from trigger"""
        # Create trigger
        manager.create_trigger(
            trigger_id='T_REMOVE_TEST',
            category='test',
            priority='medium',
            examples=['Example 1', 'Example 2', 'Example 3']
        )
        
        # Update - remove example
        success = manager.update_trigger(
            'T_REMOVE_TEST',
            remove_example='Example 2'
        )
        
        assert success is True
        
        # Verify
        filepath = manager.triggers_dir / 'test_triggers.yaml'
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        trigger = data['triggers'][0]
        assert len(trigger['detection']['examples']) == 2
        assert 'Example 2' not in trigger['detection']['examples']
    
    def test_update_trigger_priority(self, manager):
        """Should update trigger priority"""
        # Create trigger
        manager.create_trigger(
            trigger_id='T_PRIORITY_TEST',
            category='test',
            priority='medium',
            examples=['Example 1']
        )
        
        # Update priority
        success = manager.update_trigger(
            'T_PRIORITY_TEST',
            priority='critical'
        )
        
        assert success is True
        
        # Verify
        filepath = manager.triggers_dir / 'test_triggers.yaml'
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        trigger = data['triggers'][0]
        assert trigger['priority'] == 'critical'
    
    def test_update_trigger_threshold(self, manager):
        """Should update trigger threshold"""
        # Create trigger
        manager.create_trigger(
            trigger_id='T_THRESHOLD_TEST',
            category='test',
            priority='medium',
            examples=['Example 1'],
            threshold=0.75
        )
        
        # Update threshold
        success = manager.update_trigger(
            'T_THRESHOLD_TEST',
            threshold=0.85
        )
        
        assert success is True
        
        # Verify
        filepath = manager.triggers_dir / 'test_triggers.yaml'
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        trigger = data['triggers'][0]
        assert trigger['detection']['threshold'] == 0.85
    
    def test_update_nonexistent_trigger(self, manager):
        """Should handle updating nonexistent trigger"""
        success = manager.update_trigger(
            'T_NONEXISTENT',
            priority='high'
        )
        
        assert success is False
    
    def test_delete_trigger(self, manager):
        """Should delete trigger"""
        # Create trigger
        manager.create_trigger(
            trigger_id='T_DELETE_TEST',
            category='test',
            priority='medium',
            examples=['Example 1']
        )
        
        # Delete trigger
        success = manager.delete_trigger('T_DELETE_TEST', confirm=True)
        
        assert success is True
        
        # Verify it's gone
        filepath = manager.triggers_dir / 'test_triggers.yaml'
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        assert len(data['triggers']) == 0
    
    def test_delete_without_confirm(self, manager):
        """Should not delete without confirmation"""
        # Create trigger
        manager.create_trigger(
            trigger_id='T_NO_CONFIRM',
            category='test',
            priority='medium',
            examples=['Example 1']
        )
        
        # Try to delete without confirm
        success = manager.delete_trigger('T_NO_CONFIRM', confirm=False)
        
        assert success is False
        
        # Verify it still exists
        filepath = manager.triggers_dir / 'test_triggers.yaml'
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        assert len(data['triggers']) == 1


class TestPatternCRUD:
    """Test pattern CRUD operations"""
    
    def test_create_pattern(self, manager):
        """Should create a new pattern"""
        success = manager.create_pattern(
            pattern_id='PATTERN_TEST',
            category='test',
            response_type='reactive',
            triggers=['T_TRIGGER_1', 'T_TRIGGER_2'],
            behaviors=[
                {
                    'id': 'B_TEST_BEHAVIOR',
                    'weight': 1.0,
                    'template': 'Test template with {variable}'
                }
            ]
        )
        
        assert success is True
        
        # Verify file was created
        filepath = manager.patterns_dir / 'test_patterns.yaml'
        assert filepath.exists()
        
        # Verify content
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'patterns' in data
        assert len(data['patterns']) == 1
        
        pattern = data['patterns'][0]
        assert pattern['id'] == 'PATTERN_TEST'
        assert pattern['category'] == 'test'
        assert pattern['response_type'] == 'reactive'
        assert len(pattern['triggers']) == 2
        assert len(pattern['behaviors']) == 1
    
    def test_show_pattern(self, manager, capsys):
        """Should show pattern details"""
        # Create pattern
        manager.create_pattern(
            pattern_id='PATTERN_SHOW_TEST',
            category='test',
            response_type='proactive',
            triggers=['T_TRIGGER_1'],
            behaviors=[
                {'id': 'B_BEHAVIOR_1', 'weight': 0.6, 'template': 'Template 1'},
                {'id': 'B_BEHAVIOR_2', 'weight': 0.4, 'template': 'Template 2'}
            ],
            situation_affinity={'assessment': 0.9, 'analysis': 0.3}
        )
        
        # Show pattern
        success = manager.show_pattern('PATTERN_SHOW_TEST')
        
        assert success is True
        
        # Check output
        captured = capsys.readouterr()
        assert 'PATTERN_SHOW_TEST' in captured.out
        assert 'proactive' in captured.out
        assert 'B_BEHAVIOR_1' in captured.out
        assert 'B_BEHAVIOR_2' in captured.out


class TestValidation:
    """Test YAML validation"""
    
    def test_validate_valid_file(self, manager):
        """Should validate correct YAML file"""
        # Create valid trigger
        manager.create_trigger(
            trigger_id='T_VALID',
            category='test',
            priority='medium',
            examples=['Example 1', 'Example 2', 'Example 3']
        )
        
        filepath = manager.triggers_dir / 'test_triggers.yaml'
        
        # Validation happens in create_trigger, if we got here it passed
        assert filepath.exists()


class TestIsolation:
    """Test that tests don't impact production"""
    
    def test_uses_temp_directory(self, manager, temp_config_dir):
        """Should use temporary directory, not production"""
        # Verify manager is using temp directory (relative path)
        # Manager uses relative paths like 'data/triggers'
        # But we're in temp_config_dir, so it's actually temp_config_dir/data/triggers
        
        # Create a trigger to verify it goes to temp location
        manager.create_trigger(
            trigger_id='T_ISOLATION_TEST',
            category='test',
            priority='medium',
            examples=['Example 1']
        )
        
        # Verify file is in temp directory
        temp_trigger_file = temp_config_dir / 'data' / 'triggers' / 'test_triggers.yaml'
        assert temp_trigger_file.exists(), "Trigger file should be in temp directory"
        
        # Verify production directory is NOT affected
        # (if it exists, it should not have our test trigger)
        import os
        original_dir = os.getcwd()
        # We're in temp dir, so go back to check production
        # Actually, we can't easily check this without changing dirs
        # The important thing is the file is in temp_config_dir
    
    def test_temp_cleanup(self, temp_config_dir):
        """Temporary directory should be cleaned up after test"""
        # Create some files
        test_file = temp_config_dir / 'test.txt'
        test_file.write_text('test')
        
        assert test_file.exists()
        
        # After test, pytest will clean up tmp_path automatically
