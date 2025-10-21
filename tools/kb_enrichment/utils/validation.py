"""Validation utilities for nodes and edges."""

import logging
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


# Expected node types
VALID_NODE_TYPES = {
    "AI_ARCHETYPE",
    "COMMON_MODEL",
    "AI_OUTPUT",
    "AI_PREREQUISITE",
    "BUSINESS_FUNCTION",
    "BUSINESS_SECTOR",
    "BUSINESS_TOOL",
    "OPERATIONAL_PAIN_POINT",  # M1
    "MEASURABLE_FAILURE_MODE",  # M2
    "PROBLEM_TYPE",
    "MATURITY_DIMENSION",
}

# Expected edge types
VALID_EDGE_TYPES = {
    "IMPLEMENTED_BY",
    "PRODUCES_OUTPUT",
    "REQUIRES",
    "APPLIES_TO_FUNCTION",
    "OPERATES_IN",
    "GOVERNS_READINESS_FOR",
    "CONTEXTUALIZED_BY",
    "MANIFESTS_AS",
    "MITIGATES_FAILURE",
    "AFFECTS_TOOL",
    "LOCATED_IN",
    "HAS_PURPOSE",
    "BELONGS_TO",
    "ENABLES_FUNCTION",
}


def validate_nodes(nodes: List[Dict[str, Any]], strict: bool = False) -> Dict[str, Any]:
    """Validate node list structure.
    
    Args:
        nodes: List of node dictionaries
        strict: If True, raise errors on validation failures
        
    Returns:
        Validation report dictionary
    """
    report = {
        "valid": True,
        "total_nodes": len(nodes),
        "errors": [],
        "warnings": [],
        "node_types": {},
    }
    
    seen_ids = set()
    
    for idx, node in enumerate(nodes):
        # Check required fields
        if "id" not in node:
            msg = f"Node {idx} missing 'id' field"
            report["errors"].append(msg)
            report["valid"] = False
            if strict:
                raise ValueError(msg)
            continue
        
        node_id = node["id"]
        
        # Check for duplicate IDs
        if node_id in seen_ids:
            msg = f"Duplicate node ID: {node_id}"
            report["errors"].append(msg)
            report["valid"] = False
            if strict:
                raise ValueError(msg)
        
        seen_ids.add(node_id)
        
        # Check node type
        node_type = node.get("node_type")
        if not node_type:
            msg = f"Node {node_id} missing 'node_type' field"
            report["errors"].append(msg)
            report["valid"] = False
            if strict:
                raise ValueError(msg)
        elif node_type not in VALID_NODE_TYPES:
            msg = f"Node {node_id} has invalid node_type: {node_type}"
            report["warnings"].append(msg)
        
        # Count node types
        if node_type:
            report["node_types"][node_type] = report["node_types"].get(node_type, 0) + 1
        
        # Check for name field (recommended but not required)
        if "name" not in node and "label" not in node:
            msg = f"Node {node_id} missing 'name' or 'label' field"
            report["warnings"].append(msg)
    
    logger.info(f"Validated {len(nodes)} nodes: {len(report['errors'])} errors, {len(report['warnings'])} warnings")
    
    return report


def validate_edges(
    edges: List[Dict[str, Any]],
    valid_node_ids: Set[str],
    strict: bool = False
) -> Dict[str, Any]:
    """Validate edge list structure.
    
    Args:
        edges: List of edge dictionaries
        valid_node_ids: Set of valid node IDs to check references
        strict: If True, raise errors on validation failures
        
    Returns:
        Validation report dictionary
    """
    report = {
        "valid": True,
        "total_edges": len(edges),
        "errors": [],
        "warnings": [],
        "edge_types": {},
    }
    
    for idx, edge in enumerate(edges):
        # Check required fields
        required_fields = ["source", "target", "edge_type"]
        for field in required_fields:
            if field not in edge:
                msg = f"Edge {idx} missing '{field}' field"
                report["errors"].append(msg)
                report["valid"] = False
                if strict:
                    raise ValueError(msg)
                continue
        
        # Check edge type
        edge_type = edge.get("edge_type")
        if edge_type and edge_type not in VALID_EDGE_TYPES:
            msg = f"Edge {idx} has invalid edge_type: {edge_type}"
            report["warnings"].append(msg)
        
        # Count edge types
        if edge_type:
            report["edge_types"][edge_type] = report["edge_types"].get(edge_type, 0) + 1
        
        # Check node references
        source = edge.get("source")
        target = edge.get("target")
        
        if source and source not in valid_node_ids:
            msg = f"Edge {idx} references invalid source node: {source}"
            report["errors"].append(msg)
            report["valid"] = False
            if strict:
                raise ValueError(msg)
        
        if target and target not in valid_node_ids:
            msg = f"Edge {idx} references invalid target node: {target}"
            report["errors"].append(msg)
            report["valid"] = False
            if strict:
                raise ValueError(msg)
    
    logger.info(f"Validated {len(edges)} edges: {len(report['errors'])} errors, {len(report['warnings'])} warnings")
    
    return report


def validate_knowledge_graph(graph_data: Dict[str, Any], strict: bool = False) -> Dict[str, Any]:
    """Validate complete knowledge graph structure.
    
    Args:
        graph_data: Knowledge graph dictionary with 'nodes' and 'edges'
        strict: If True, raise errors on validation failures
        
    Returns:
        Validation report dictionary
    """
    report = {
        "valid": True,
        "nodes_report": None,
        "edges_report": None,
        "errors": [],
    }
    
    # Check top-level structure
    if "nodes" not in graph_data:
        msg = "Knowledge graph missing 'nodes' field"
        report["errors"].append(msg)
        report["valid"] = False
        if strict:
            raise ValueError(msg)
        return report
    
    if "edges" not in graph_data:
        msg = "Knowledge graph missing 'edges' field"
        report["errors"].append(msg)
        report["valid"] = False
        if strict:
            raise ValueError(msg)
        return report
    
    # Validate nodes
    nodes_report = validate_nodes(graph_data["nodes"], strict=strict)
    report["nodes_report"] = nodes_report
    
    if not nodes_report["valid"]:
        report["valid"] = False
    
    # Validate edges
    valid_node_ids = {node["id"] for node in graph_data["nodes"] if "id" in node}
    edges_report = validate_edges(graph_data["edges"], valid_node_ids, strict=strict)
    report["edges_report"] = edges_report
    
    if not edges_report["valid"]:
        report["valid"] = False
    
    logger.info(f"Knowledge graph validation: {'PASSED' if report['valid'] else 'FAILED'}")
    
    return report


def print_validation_report(report: Dict[str, Any]) -> None:
    """Print validation report in human-readable format.
    
    Args:
        report: Validation report dictionary
    """
    print("\n=== Validation Report ===")
    print(f"Status: {'✓ PASSED' if report['valid'] else '✗ FAILED'}")
    
    if "nodes_report" in report and report["nodes_report"]:
        nr = report["nodes_report"]
        print(f"\nNodes: {nr['total_nodes']}")
        print(f"  Errors: {len(nr['errors'])}")
        print(f"  Warnings: {len(nr['warnings'])}")
        
        if nr["node_types"]:
            print("  Node Types:")
            for node_type, count in sorted(nr["node_types"].items()):
                print(f"    - {node_type}: {count}")
        
        if nr["errors"]:
            print("\n  Node Errors:")
            for error in nr["errors"][:5]:  # Show first 5
                print(f"    - {error}")
            if len(nr["errors"]) > 5:
                print(f"    ... and {len(nr['errors']) - 5} more")
    
    if "edges_report" in report and report["edges_report"]:
        er = report["edges_report"]
        print(f"\nEdges: {er['total_edges']}")
        print(f"  Errors: {len(er['errors'])}")
        print(f"  Warnings: {len(er['warnings'])}")
        
        if er["edge_types"]:
            print("  Edge Types:")
            for edge_type, count in sorted(er["edge_types"].items()):
                print(f"    - {edge_type}: {count}")
        
        if er["errors"]:
            print("\n  Edge Errors:")
            for error in er["errors"][:5]:  # Show first 5
                print(f"    - {error}")
            if len(er["errors"]) > 5:
                print(f"    ... and {len(er['errors']) - 5} more")
    
    print()
