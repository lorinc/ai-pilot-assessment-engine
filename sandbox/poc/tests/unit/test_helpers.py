"""Unit tests for helper utilities."""

import pytest
import json
from utils.helpers import format_json, truncate_text


class TestFormatJson:
    """Test suite for format_json function."""
    
    def test_format_json_simple_dict(self):
        """Test formatting simple dictionary."""
        data = {"name": "test", "value": 42}
        
        result = format_json(data)
        
        assert '"name": "test"' in result
        assert '"value": 42' in result
        # Check it's pretty-printed (has newlines)
        assert '\n' in result
    
    def test_format_json_nested_dict(self):
        """Test formatting nested dictionary."""
        data = {
            "user": {
                "name": "John",
                "age": 30
            },
            "active": True
        }
        
        result = format_json(data)
        
        assert '"user"' in result
        assert '"name": "John"' in result
        assert '"age": 30' in result
        assert '"active": true' in result
    
    def test_format_json_list(self):
        """Test formatting list."""
        data = ["apple", "banana", "cherry"]
        
        result = format_json(data)
        
        assert '"apple"' in result
        assert '"banana"' in result
        assert '"cherry"' in result
        assert result.startswith('[')
        assert result.rstrip().endswith(']')
    
    def test_format_json_mixed_types(self):
        """Test formatting with mixed types."""
        data = {
            "string": "text",
            "number": 123,
            "float": 45.67,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        result = format_json(data)
        
        assert '"string": "text"' in result
        assert '"number": 123' in result
        assert '"float": 45.67' in result
        assert '"boolean": true' in result
        assert '"null": null' in result
        assert '"list"' in result
        assert '"nested"' in result
    
    def test_format_json_custom_indent(self):
        """Test formatting with custom indentation."""
        data = {"a": {"b": "c"}}
        
        result_2 = format_json(data, indent=2)
        result_4 = format_json(data, indent=4)
        
        # 4-space indent should be longer
        assert len(result_4) > len(result_2)
        # Both should be valid JSON
        assert json.loads(result_2) == data
        assert json.loads(result_4) == data
    
    def test_format_json_unicode(self):
        """Test formatting with unicode characters."""
        data = {"message": "Hello 世界", "emoji": "🚀"}
        
        result = format_json(data)
        
        # ensure_ascii=False should preserve unicode
        assert "世界" in result
        assert "🚀" in result
    
    def test_format_json_empty_dict(self):
        """Test formatting empty dictionary."""
        data = {}
        
        result = format_json(data)
        
        assert result == "{}"
    
    def test_format_json_empty_list(self):
        """Test formatting empty list."""
        data = []
        
        result = format_json(data)
        
        assert result == "[]"
    
    def test_format_json_string(self):
        """Test formatting plain string."""
        data = "simple string"
        
        result = format_json(data)
        
        assert result == '"simple string"'
    
    def test_format_json_number(self):
        """Test formatting plain number."""
        data = 42
        
        result = format_json(data)
        
        assert result == "42"
    
    def test_format_json_boolean(self):
        """Test formatting boolean."""
        result_true = format_json(True)
        result_false = format_json(False)
        
        assert result_true == "true"
        assert result_false == "false"
    
    def test_format_json_null(self):
        """Test formatting None/null."""
        result = format_json(None)
        
        assert result == "null"
    
    def test_format_json_special_characters(self):
        """Test formatting with special characters."""
        data = {
            "quote": 'He said "hello"',
            "newline": "line1\nline2",
            "tab": "col1\tcol2",
            "backslash": "path\\to\\file"
        }
        
        result = format_json(data)
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == data


class TestTruncateText:
    """Test suite for truncate_text function."""
    
    def test_truncate_text_short(self):
        """Test text shorter than max length."""
        text = "Short text"
        
        result = truncate_text(text, max_length=100)
        
        assert result == "Short text"
        assert "..." not in result
    
    def test_truncate_text_exact_length(self):
        """Test text exactly at max length."""
        text = "A" * 100
        
        result = truncate_text(text, max_length=100)
        
        assert result == text
        assert "..." not in result
    
    def test_truncate_text_long(self):
        """Test text longer than max length."""
        text = "A" * 150
        
        result = truncate_text(text, max_length=100)
        
        assert len(result) == 100
        assert result.endswith("...")
        assert result == ("A" * 97) + "..."
    
    def test_truncate_text_default_length(self):
        """Test with default max length."""
        text = "A" * 150
        
        result = truncate_text(text)
        
        assert len(result) == 100
        assert result.endswith("...")
    
    def test_truncate_text_custom_length(self):
        """Test with custom max length."""
        text = "This is a longer text that needs truncation"
        
        result = truncate_text(text, max_length=20)
        
        assert len(result) == 20
        assert result.endswith("...")
        # Truncates at character 17, adds "..."
        assert result.startswith("This is a longer")
    
    def test_truncate_text_very_short_limit(self):
        """Test with very short max length."""
        text = "Hello world"
        
        result = truncate_text(text, max_length=5)
        
        assert len(result) == 5
        assert result == "He..."
    
    def test_truncate_text_empty_string(self):
        """Test with empty string."""
        result = truncate_text("", max_length=100)
        
        assert result == ""
    
    def test_truncate_text_unicode(self):
        """Test truncation with unicode characters."""
        text = "Hello 世界 " * 20
        
        result = truncate_text(text, max_length=50)
        
        assert len(result) == 50
        assert result.endswith("...")
    
    def test_truncate_text_newlines(self):
        """Test truncation with newlines."""
        text = "Line 1\nLine 2\nLine 3\n" * 10
        
        result = truncate_text(text, max_length=30)
        
        assert len(result) == 30
        assert result.endswith("...")
    
    def test_truncate_text_preserves_beginning(self):
        """Test that truncation preserves the beginning of text."""
        text = "Important information at the start, less important at the end"
        
        result = truncate_text(text, max_length=30)
        
        assert result.startswith("Important information")
        assert result.endswith("...")
    
    def test_truncate_text_minimum_length(self):
        """Test with minimum possible length (4 chars for '...')."""
        text = "Hello"
        
        result = truncate_text(text, max_length=4)
        
        assert len(result) == 4
        assert result == "H..."
    
    def test_truncate_text_length_3(self):
        """Test edge case with max_length=3."""
        text = "Hello"
        
        result = truncate_text(text, max_length=3)
        
        assert len(result) == 3
        assert result == "..."
