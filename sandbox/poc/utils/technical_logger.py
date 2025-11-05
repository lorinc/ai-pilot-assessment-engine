"""Technical logger for observability and debugging."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class TechnicalLogger:
    """Logger for tracking LLM actions, decisions, and context."""
    
    def __init__(self, max_entries: int = 20):
        """
        Initialize technical logger.
        
        Args:
            max_entries: Maximum number of log entries to keep (default: 20)
        """
        self.max_entries = max_entries
        self.entries: List[Dict[str, Any]] = []
    
    def log(
        self,
        level: LogLevel,
        log_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add log entry.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            log_type: Type of log (llm_call, decision, tool_call, context, error)
            message: Log message
            metadata: Optional metadata dictionary
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.value,
            "type": log_type,
            "message": message,
            "metadata": metadata or {}
        }
        
        self.entries.append(entry)
        
        # Keep only last N entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
    
    def debug(self, log_type: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log DEBUG level entry."""
        self.log(LogLevel.DEBUG, log_type, message, metadata)
    
    def info(self, log_type: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log INFO level entry."""
        self.log(LogLevel.INFO, log_type, message, metadata)
    
    def warning(self, log_type: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log WARNING level entry."""
        self.log(LogLevel.WARNING, log_type, message, metadata)
    
    def error(self, log_type: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log ERROR level entry."""
        self.log(LogLevel.ERROR, log_type, message, metadata)
    
    def get_entries(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get log entries.
        
        Args:
            limit: Maximum number of entries to return (default: all)
            
        Returns:
            List of log entries
        """
        if limit:
            return self.entries[-limit:]
        return self.entries
    
    def clear(self):
        """Clear all log entries."""
        self.entries = []
    
    def get_summary(self) -> Dict[str, int]:
        """
        Get summary statistics.
        
        Returns:
            Dictionary with counts by level and type
        """
        summary = {
            "total": len(self.entries),
            "by_level": {},
            "by_type": {}
        }
        
        for entry in self.entries:
            level = entry["level"]
            log_type = entry["type"]
            
            summary["by_level"][level] = summary["by_level"].get(level, 0) + 1
            summary["by_type"][log_type] = summary["by_type"].get(log_type, 0) + 1
        
        return summary
