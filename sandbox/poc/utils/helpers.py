"""Utility helper functions."""

import json
from typing import Any


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as pretty-printed JSON.
    
    Args:
        data: Data to format
        indent: Number of spaces for indentation
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
