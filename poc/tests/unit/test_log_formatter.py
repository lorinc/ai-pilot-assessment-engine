"""Unit tests for LogFormatter."""

import pytest
from utils.log_formatter import LogFormatter


class TestLogFormatter:
    """Test suite for LogFormatter."""
    
    def test_format_entry_simple_info(self):
        """Test formatting simple INFO entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "app_init",
            "message": "App initialized",
            "metadata": {}
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "[2025-01-01 12:00:00]" in result
        assert "**INFO**:" in result
        assert "Gemini client created and cached in session" in result
        assert "🟢" not in result  # Icon not in formatted output, just level text
    
    def test_format_entry_with_metadata_interpolation(self):
        """Test formatting with metadata interpolation."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "llm_init",
            "message": "LLM initialized",
            "metadata": {"model": "gemini-pro"}
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Initialized LLM: gemini-pro" in result
    
    def test_format_entry_llm_call(self):
        """Test formatting LLM call entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "llm_call",
            "message": "Calling LLM",
            "metadata": {
                "prompt_length": 1500,
                "temperature": 0.7
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Sending prompt to LLM (1500 chars, temp=0.7)" in result
    
    def test_format_entry_llm_response(self):
        """Test formatting LLM response entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "llm_response",
            "message": "Response received",
            "metadata": {
                "response_length": 500,
                "total_chunks": 5
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Received LLM response (500 chars, 5 chunks)" in result
    
    def test_format_entry_user_input(self):
        """Test formatting user input entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "user_input",
            "message": "User sent message",
            "metadata": {"message_length": 42}
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "User message received (42 chars)" in result
    
    def test_format_entry_context_build_custom(self):
        """Test custom formatting for context_build."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "context_build",
            "message": "Building context",
            "metadata": {
                "phase": "discovery",
                "available_functions": ["Sales", "Finance", "Marketing", "HR", "IT", "Operations"]
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Building context for LLM:" in result
        assert "Phase: discovery" in result
        assert "Available functions (6):" in result
        assert "Sales, Finance, Marketing, HR, IT..." in result
        # Check multi-line indentation
        lines = result.split('\n')
        assert len(lines) == 3
        assert lines[1].startswith('  ')
        assert lines[2].startswith('  ')
    
    def test_format_entry_context_build_few_functions(self):
        """Test context_build with few functions (no truncation)."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "context_build",
            "message": "Building context",
            "metadata": {
                "phase": "assessment",
                "available_functions": ["Sales", "Finance"]
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Available functions (2): Sales, Finance" in result
        assert "..." not in result
    
    def test_format_entry_prompt_built_custom(self):
        """Test custom formatting for prompt_built."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "DEBUG",
            "type": "prompt_built",
            "message": "Prompt ready",
            "metadata": {
                "prompt_length": 2000,
                "prompt_preview": "# System Context\nYou are an AI assistant.\n\n# User Message\nHello world"
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Prompt constructed (2000 chars):" in result
        assert "Preview: # System Context You are an AI assistant." in result
        # Check multi-line structure
        lines = result.split('\n')
        assert len(lines) == 2
        # Second line is indented (after timestamp/level line wraps the first content line)
        assert 'Preview:' in lines[1]
    
    def test_format_entry_prompt_built_long_preview(self):
        """Test prompt_built with long preview (truncation)."""
        long_text = "A" * 300
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "DEBUG",
            "type": "prompt_built",
            "message": "Prompt ready",
            "metadata": {
                "prompt_length": 300,
                "prompt_preview": long_text
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "..." in result
        assert len(result) < len(long_text) + 100  # Significantly shorter
    
    def test_format_entry_taxonomy_search(self):
        """Test formatting taxonomy search entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "taxonomy_search",
            "message": "Search complete",
            "metadata": {
                "query": "sales forecast",
                "result_count": 3
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Searching taxonomy: sales forecast → 3 results" in result
    
    def test_format_entry_output_identified(self):
        """Test formatting output identified entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "output_identified",
            "message": "Output found",
            "metadata": {
                "output_name": "Sales Forecast",
                "confidence": 0.87
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Output identified: Sales Forecast (confidence: 0.87)" in result
    
    def test_format_entry_context_inferred(self):
        """Test formatting context inferred entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "context_inferred",
            "message": "Context ready",
            "metadata": {
                "team": "Sales Operations",
                "system": "Salesforce"
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Context inferred: team=Sales Operations, system=Salesforce" in result
    
    def test_format_entry_phase_transition(self):
        """Test formatting phase transition entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "phase_transition",
            "message": "Phase changed",
            "metadata": {
                "from_phase": "discovery",
                "to_phase": "assessment"
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Phase transition: discovery → assessment" in result
    
    def test_format_entry_error(self):
        """Test formatting error entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "ERROR",
            "type": "error",
            "message": "Error occurred",
            "metadata": {
                "error_message": "Connection timeout"
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "**ERROR**:" in result
        assert "Error: Connection timeout" in result
    
    def test_format_entry_warning(self):
        """Test formatting warning entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "WARNING",
            "type": "warning",
            "message": "Warning issued",
            "metadata": {
                "warning_message": "Low confidence match"
            }
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "**WARNING**:" in result
        assert "Warning: Low confidence match" in result
    
    def test_format_entry_missing_metadata_fallback(self):
        """Test fallback when metadata is missing for template."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "llm_init",
            "message": "LLM initialized",
            "metadata": {}  # Missing 'model' key
        }
        
        result = LogFormatter.format_entry(entry)
        
        # Should fallback to original message
        assert "LLM initialized" in result
    
    def test_format_entry_unknown_type(self):
        """Test formatting entry with unknown type."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "unknown_type",
            "message": "Custom message",
            "metadata": {}
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Custom message" in result
    
    def test_format_entry_debug_level(self):
        """Test formatting DEBUG level entry."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "DEBUG",
            "type": "app_init",
            "message": "Debug info",
            "metadata": {}
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "**DEBUG**:" in result
    
    def test_format_entry_timestamp_format(self):
        """Test timestamp formatting."""
        entry = {
            "timestamp": "2025-01-01T12:34:56.789Z",
            "level": "INFO",
            "type": "app_init",
            "message": "Test",
            "metadata": {}
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "[2025-01-01 12:34:56]" in result
    
    def test_format_entry_multiline_indentation(self):
        """Test multi-line message indentation."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "context_build",
            "message": "Context",
            "metadata": {
                "phase": "discovery",
                "available_functions": ["Sales"]
            }
        }
        
        result = LogFormatter.format_entry(entry)
        lines = result.split('\n')
        
        # First line should have timestamp and level
        assert lines[0].startswith('[2025-01-01')
        # Subsequent lines should be indented
        for line in lines[1:]:
            assert line.startswith('  ')
    
    def test_format_entries_multiple(self):
        """Test formatting multiple entries."""
        entries = [
            {
                "timestamp": "2025-01-01T12:00:00Z",
                "level": "INFO",
                "type": "app_init",
                "message": "First",
                "metadata": {}
            },
            {
                "timestamp": "2025-01-01T12:00:01Z",
                "level": "INFO",
                "type": "user_input",
                "message": "Second",
                "metadata": {"message_length": 10}
            }
        ]
        
        result = LogFormatter.format_entries(entries)
        
        # Should have double newlines between entries
        assert '\n\n' in result
        assert "Gemini client created" in result
        assert "User message received (10 chars)" in result
    
    def test_format_entries_empty(self):
        """Test formatting empty list."""
        result = LogFormatter.format_entries([])
        
        assert result == ""
    
    def test_format_entries_single(self):
        """Test formatting single entry."""
        entries = [
            {
                "timestamp": "2025-01-01T12:00:00Z",
                "level": "INFO",
                "type": "app_init",
                "message": "Test",
                "metadata": {}
            }
        ]
        
        result = LogFormatter.format_entries(entries)
        
        assert '\n\n' not in result  # No double newlines for single entry
        assert "Gemini client created" in result
    
    def test_format_entry_no_metadata_key(self):
        """Test entry without metadata key."""
        entry = {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "INFO",
            "type": "app_init",
            "message": "Test"
            # No metadata key at all
        }
        
        result = LogFormatter.format_entry(entry)
        
        assert "Gemini client created" in result
    
    def test_templates_coverage(self):
        """Test that all template types are defined."""
        expected_types = [
            "app_init", "llm_init", "llm_call", "llm_response",
            "user_input", "context_build", "prompt_built",
            "assistant_response", "decision", "tool_call",
            "taxonomy_search", "output_identified", "context_inferred",
            "phase_transition", "error", "warning"
        ]
        
        for log_type in expected_types:
            assert log_type in LogFormatter.TEMPLATES
