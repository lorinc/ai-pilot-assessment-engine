"""
Graph Renderer: Convert operational graph to st-link-analysis format.

Minimal implementation to pass TDD tests.
"""

import json
from pathlib import Path
from typing import Dict, List, Any

try:
    from st_link_analysis import NodeStyle, EdgeStyle
except ImportError:
    # Fallback for testing without st-link-analysis installed
    from dataclasses import dataclass
    
    @dataclass
    class NodeStyle:
        """Node style definition for st-link-analysis."""
        label: str
        color: str
        caption: str
        icon: str
    
    @dataclass
    class EdgeStyle:
        """Edge style definition for st-link-analysis."""
        label: str
        directed: bool = True
        caption: str = "label"


def load_graph_data(filename: str) -> Dict[str, Any]:
    """Load graph data from JSON file.
    
    Args:
        filename: Name of JSON file in current directory
        
    Returns:
        Graph data dict with nodes, edges, metadata
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(__file__).parent / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Graph file not found: {filename}")
    
    with open(filepath, 'r') as f:
        return json.load(f)


def format_node(node: Dict[str, Any]) -> Dict[str, Any]:
    """Format node for st-link-analysis.
    
    Args:
        node: Node dict with data field
        
    Returns:
        Formatted node with quality indicators
    """
    formatted = {
        "data": node["data"].copy()
    }
    
    # Add quality indicators
    data = node["data"]
    quality_score = None
    
    # Check for quality score (different fields for different node types)
    if "data_quality_score" in data:
        quality_score = data["data_quality_score"]
    elif "quality_score" in data:
        quality_score = data["quality_score"]
    elif "reliability_score" in data:
        quality_score = data["reliability_score"]
    elif "process_maturity" in data:
        quality_score = data["process_maturity"]
    
    # Add quality class and badge
    if quality_score is not None:
        if quality_score < 0.4:
            formatted["classes"] = "quality-critical"
        elif quality_score < 0.7:
            formatted["classes"] = "quality-warning"
        else:
            formatted["classes"] = "quality-good"
        
        # Add badge
        formatted["data"]["badge"] = f"⚠️ {quality_score:.1f}"
    
    return formatted


def format_edge(edge: Dict[str, Any]) -> Dict[str, Any]:
    """Format edge for st-link-analysis.
    
    Args:
        edge: Edge dict with data field
        
    Returns:
        Formatted edge with quality indicators
    """
    formatted = {
        "data": edge["data"].copy()
    }
    
    # Add error propagation indicators for DEPENDS_ON edges
    data = edge["data"]
    if data.get("type") == "DEPENDS_ON":
        error_factor = data.get("error_propagation_factor", 0)
        
        if error_factor > 0.7:
            formatted["classes"] = "error-high"
        elif error_factor > 0.4:
            formatted["classes"] = "error-medium"
        else:
            formatted["classes"] = "error-low"
    
    return formatted


def get_node_styles() -> List[NodeStyle]:
    """Get node style definitions for all entity types.
    
    Returns:
        List of NodeStyle objects
    """
    return [
        NodeStyle(
            label="Actor",
            color="#FF7F3E",  # Orange
            caption="name",
            icon="group"
        ),
        NodeStyle(
            label="Artifact",
            color="#2A629A",  # Blue
            caption="name",
            icon="description"
        ),
        NodeStyle(
            label="Tool",
            color="#7E60BF",  # Purple
            caption="name",
            icon="computer"
        ),
        NodeStyle(
            label="Activity",
            color="#4CAF50",  # Green
            caption="name",
            icon="settings"
        )
    ]


def get_edge_styles() -> List[EdgeStyle]:
    """Get edge style definitions for all relationship types.
    
    Returns:
        List of EdgeStyle objects
    """
    return [
        EdgeStyle(label="PERFORMS", directed=True),
        EdgeStyle(label="PRODUCES", directed=True),
        EdgeStyle(label="DEPENDS_ON", directed=True),
        EdgeStyle(label="USES", directed=True)
    ]


def render_graph(graph_data: Dict[str, Any]) -> Dict[str, List]:
    """Render graph data in st-link-analysis format.
    
    Args:
        graph_data: Graph dict with nodes and edges
        
    Returns:
        Elements dict with formatted nodes and edges
    """
    elements = {
        "nodes": [format_node(node) for node in graph_data.get("nodes", [])],
        "edges": [format_edge(edge) for edge in graph_data.get("edges", [])]
    }
    
    return elements


def identify_bottleneck(graph_data: Dict[str, Any]) -> Dict[str, Any]:
    """Identify quality bottleneck (lowest quality artifact).
    
    Args:
        graph_data: Graph dict with nodes
        
    Returns:
        Bottleneck node info with id, name, score
    """
    artifacts = [
        node["data"] for node in graph_data.get("nodes", [])
        if node["data"].get("label") == "Artifact"
    ]
    
    if not artifacts:
        return {}
    
    # Find artifact with lowest quality score
    bottleneck = min(artifacts, key=lambda a: a.get("data_quality_score", 1.0))
    
    return {
        "id": bottleneck.get("id", ""),
        "name": bottleneck.get("name", ""),
        "score": bottleneck.get("data_quality_score", 0)
    }


def calculate_quality_summary(graph_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate quality statistics for artifacts.
    
    Args:
        graph_data: Graph dict with nodes
        
    Returns:
        Quality summary with avg, min, max, count
    """
    artifacts = [
        node["data"] for node in graph_data.get("nodes", [])
        if node["data"].get("label") == "Artifact"
    ]
    
    if not artifacts:
        return {
            "avg_quality": 0,
            "min_quality": 0,
            "max_quality": 0,
            "artifacts_with_issues": 0
        }
    
    quality_scores = [a.get("data_quality_score", 0) for a in artifacts]
    
    return {
        "avg_quality": sum(quality_scores) / len(quality_scores),
        "min_quality": min(quality_scores),
        "max_quality": max(quality_scores),
        "artifacts_with_issues": len([s for s in quality_scores if s < 0.7])
    }
