"""File I/O utilities for JSON handling."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(file_path: Union[str, Path]) -> Union[Dict, List]:
    """Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    logger.debug(f"Loading JSON from {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.debug(f"Loaded {len(data) if isinstance(data, (list, dict)) else 'N/A'} items")
    return data


def save_json(
    data: Union[Dict, List],
    file_path: Union[str, Path],
    indent: int = 2,
    ensure_ascii: bool = False
) -> None:
    """Save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Output file path
        indent: JSON indentation
        ensure_ascii: Whether to escape non-ASCII characters
    """
    file_path = Path(file_path)
    
    # Ensure parent directory exists
    ensure_dir(file_path.parent)
    
    logger.debug(f"Saving JSON to {file_path}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
    
    logger.info(f"Saved {len(data) if isinstance(data, (list, dict)) else 'N/A'} items to {file_path}")


def load_multiple_json(file_paths: List[Union[str, Path]]) -> List[Union[Dict, List]]:
    """Load multiple JSON files.
    
    Args:
        file_paths: List of file paths
        
    Returns:
        List of loaded JSON data
    """
    results = []
    for path in file_paths:
        try:
            results.append(load_json(path))
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            results.append(None)
    
    return results


def get_file_size(file_path: Union[str, Path]) -> str:
    """Get human-readable file size.
    
    Args:
        file_path: Path to file
        
    Returns:
        Formatted file size string
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return "N/A"
    
    size = file_path.stat().st_size
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    
    return f"{size:.2f} TB"
