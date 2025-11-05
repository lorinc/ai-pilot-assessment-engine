"""Unit tests for Technical Logger."""

import pytest
from datetime import datetime

from src.utils.logger import TechnicalLogger, LogLevel


@pytest.fixture
def logger():
    """Create logger instance."""
    return TechnicalLogger(max_entries=5)


class TestTechnicalLogger:
    """Test TechnicalLogger class."""
    
    def test_init(self, logger):
        """Test logger initialization."""
        assert logger.max_entries == 5
        assert len(logger.entries) == 0
    
    def test_log_info(self, logger):
        """Test logging info message."""
        logger.info("test_type", "Test message", {"key": "value"})
        assert len(logger.entries) == 1
        entry = logger.entries[0]
        assert entry["level"] == "INFO"
        assert entry["type"] == "test_type"
        assert entry["message"] == "Test message"
        assert entry["metadata"]["key"] == "value"
    
    def test_log_debug(self, logger):
        """Test logging debug message."""
        logger.debug("test_type", "Debug message")
        assert len(logger.entries) == 1
        assert logger.entries[0]["level"] == "DEBUG"
    
    def test_log_warning(self, logger):
        """Test logging warning message."""
        logger.warning("test_type", "Warning message")
        assert len(logger.entries) == 1
        assert logger.entries[0]["level"] == "WARNING"
    
    def test_log_error(self, logger):
        """Test logging error message."""
        logger.error("test_type", "Error message")
        assert len(logger.entries) == 1
        assert logger.entries[0]["level"] == "ERROR"
    
    def test_max_entries_limit(self, logger):
        """Test max entries limit."""
        for i in range(10):
            logger.info("test", f"Message {i}")
        assert len(logger.entries) == 5
        # Should keep last 5 entries
        assert logger.entries[-1]["message"] == "Message 9"
        assert logger.entries[0]["message"] == "Message 5"
    
    def test_get_entries(self, logger):
        """Test getting entries."""
        logger.info("test", "Message 1")
        logger.info("test", "Message 2")
        entries = logger.get_entries()
        assert len(entries) == 2
    
    def test_get_entries_with_limit(self, logger):
        """Test getting entries with limit."""
        for i in range(5):
            logger.info("test", f"Message {i}")
        entries = logger.get_entries(limit=3)
        assert len(entries) == 3
        assert entries[-1]["message"] == "Message 4"
    
    def test_clear(self, logger):
        """Test clearing entries."""
        logger.info("test", "Message")
        logger.clear()
        assert len(logger.entries) == 0
    
    def test_get_summary(self, logger):
        """Test getting summary statistics."""
        logger.info("type1", "Message 1")
        logger.info("type2", "Message 2")
        logger.warning("type1", "Warning")
        logger.error("type3", "Error")
        
        summary = logger.get_summary()
        assert summary["total"] == 4
        assert summary["by_level"]["INFO"] == 2
        assert summary["by_level"]["WARNING"] == 1
        assert summary["by_level"]["ERROR"] == 1
        assert summary["by_type"]["type1"] == 2
        assert summary["by_type"]["type2"] == 1
        assert summary["by_type"]["type3"] == 1
    
    def test_timestamp_format(self, logger):
        """Test timestamp format."""
        logger.info("test", "Message")
        timestamp = logger.entries[0]["timestamp"]
        assert timestamp.endswith("Z")
        # Should be valid ISO format
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
