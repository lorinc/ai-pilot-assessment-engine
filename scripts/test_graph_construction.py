"""Simple test script to verify graph construction without pytest."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.knowledge.graph_builder import KnowledgeGraphBuilder
from src.knowledge.schemas import NodeType, EdgeType


def main():
    """Run basic graph construction tests."""
    print("=" * 70)
    print("KNOWLEDGE GRAPH CONSTRUCTION TEST")
    print("=" * 70)

    # Build the graph
    data_dir = Path(__file__).parent.parent / "src" / "data"
    print(f"\n1. Loading data from: {data_dir}")

    builder = KnowledgeGraphBuilder(data_dir)
    graph = builder.build()

    print(f"   ✓ Graph built successfully")

    # Get statistics
    stats = builder.get_statistics()

    print(f"\n2. Graph Statistics:")
    print(f"   Total nodes: {stats['total_nodes']}")
    print(f"   Total edges: {stats['total_edges']}")

    print(f"\n3. Node counts by type:")
    for node_type in NodeType:
        key = f"nodes_{node_type.value}"
        count = stats.get(key, 0)
        print(f"   {node_type.value:25s}: {count:3d}")

    print(f"\n4. Edge counts by type:")
    for edge_type in EdgeType:
        key = f"edges_{edge_type.value}"
        count = stats.get(key, 0)
        print(f"   {edge_type.value:25s}: {count:3d}")

    # Test specific nodes
    print(f"\n5. Verifying specific archetypes:")
    test_archetypes = [
        "Optimization & Scheduling",
        "Anomaly & Outlier Detection",
        "Classification",
        "Generative Modeling"
    ]

    for archetype_name in test_archetypes:
        found = False
        for node_id, data in graph.nodes(data=True):
            if (data.get("node_type") == NodeType.AI_ARCHETYPE.value and
                archetype_name in data.get("name", "")):
                found = True
                print(f"   ✓ Found: {archetype_name} (ID: {node_id})")
                
                # Show connected models
                successors = list(graph.successors(node_id))
                models = [
                    graph.nodes[n]["name"] for n in successors
                    if graph.nodes[n].get("node_type") == NodeType.COMMON_MODEL.value
                ]
                if models:
                    print(f"     Models: {', '.join(models[:3])}" + 
                          (f" (+{len(models)-3} more)" if len(models) > 3 else ""))
                break
        
        if not found:
            print(f"   ✗ NOT FOUND: {archetype_name}")

    # Test traversal
    print(f"\n6. Testing multi-hop traversal:")
    
    # Find Optimization & Scheduling archetype
    opt_node = None
    for node_id, data in graph.nodes(data=True):
        if (data.get("node_type") == NodeType.AI_ARCHETYPE.value and
            "Optimization" in data.get("name", "")):
            opt_node = node_id
            break

    if opt_node:
        print(f"   Starting from: {graph.nodes[opt_node]['name']}")
        
        # Hop 1: Archetype -> Models
        models = [
            n for n in graph.successors(opt_node)
            if graph.nodes[n].get("node_type") == NodeType.COMMON_MODEL.value
        ]
        print(f"   Hop 1 (Archetype → Models): Found {len(models)} models")
        
        # Hop 2: Models -> Prerequisites
        all_prereqs = set()
        for model in models[:3]:  # Check first 3 models
            prereqs = [
                n for n in graph.successors(model)
                if graph.nodes[n].get("node_type") == NodeType.AI_PREREQUISITE.value
            ]
            all_prereqs.update(prereqs)
        
        print(f"   Hop 2 (Models → Prerequisites): Found {len(all_prereqs)} unique prerequisites")
        
        if all_prereqs:
            print(f"   Sample prerequisites:")
            for prereq_id in list(all_prereqs)[:3]:
                prereq_name = graph.nodes[prereq_id]["name"]
                print(f"     - {prereq_name}")

    # Validation checks
    print(f"\n7. Validation Checks:")
    
    checks = [
        ("Graph has nodes", stats['total_nodes'] > 0),
        ("Graph has edges", stats['total_edges'] > 0),
        ("Has archetype nodes", stats.get(f"nodes_{NodeType.AI_ARCHETYPE.value}", 0) > 0),
        ("Has model nodes", stats.get(f"nodes_{NodeType.COMMON_MODEL.value}", 0) > 0),
        ("Has prerequisite nodes", stats.get(f"nodes_{NodeType.AI_PREREQUISITE.value}", 0) > 0),
        ("Has IMPLEMENTED_BY edges", stats.get(f"edges_{EdgeType.IMPLEMENTED_BY.value}", 0) > 0),
        ("Has REQUIRES edges", stats.get(f"edges_{EdgeType.REQUIRES.value}", 0) > 0),
    ]

    all_passed = True
    for check_name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"   {status}: {check_name}")
        if not passed:
            all_passed = False

    print(f"\n" + "=" * 70)
    if all_passed:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
