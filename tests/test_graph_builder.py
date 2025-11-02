"""Unit tests for knowledge graph builder."""

import pytest
from pathlib import Path
import networkx as nx

from src.knowledge_graph.graph_builder import KnowledgeGraphBuilder
from src.knowledge_graph.schemas import NodeType, EdgeType


@pytest.fixture
def data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent.parent / "src" / "data"


@pytest.fixture
def graph_builder(data_dir):
    """Create a graph builder instance."""
    return KnowledgeGraphBuilder(data_dir)


@pytest.fixture
def built_graph(graph_builder):
    """Build and return the knowledge graph."""
    return graph_builder.build()


class TestGraphConstruction:
    """Tests for basic graph construction."""

    def test_graph_is_directed(self, built_graph):
        """Verify the graph is a directed graph."""
        assert isinstance(built_graph, nx.DiGraph)

    def test_graph_has_nodes(self, built_graph):
        """Verify the graph contains nodes."""
        assert built_graph.number_of_nodes() > 0

    def test_graph_has_edges(self, built_graph):
        """Verify the graph contains edges."""
        assert built_graph.number_of_edges() > 0

    def test_all_nodes_have_type(self, built_graph):
        """Verify all nodes have a node_type attribute."""
        for node_id, data in built_graph.nodes(data=True):
            assert "node_type" in data, f"Node {node_id} missing node_type"
            assert data["node_type"] in [nt.value for nt in NodeType]

    def test_all_nodes_have_name(self, built_graph):
        """Verify all nodes have a name attribute."""
        for node_id, data in built_graph.nodes(data=True):
            assert "name" in data, f"Node {node_id} missing name"
            assert isinstance(data["name"], str)

    def test_all_edges_have_relationship(self, built_graph):
        """Verify all edges have a relationship attribute."""
        for source, target, data in built_graph.edges(data=True):
            assert "relationship" in data, f"Edge {source}->{target} missing relationship"
            assert data["relationship"] in [et.value for et in EdgeType]


class TestNodeTypes:
    """Tests for specific node types."""

    def test_archetype_nodes_exist(self, built_graph):
        """Verify AI_ARCHETYPE nodes were created."""
        archetypes = [
            node for node, data in built_graph.nodes(data=True)
            if data.get("node_type") == NodeType.AI_ARCHETYPE.value
        ]
        assert len(archetypes) > 0, "No archetype nodes found"
        # AI_archetypes.json has 28 archetypes
        assert len(archetypes) >= 20, f"Expected at least 20 archetypes, got {len(archetypes)}"

    def test_model_nodes_exist(self, built_graph):
        """Verify COMMON_MODEL nodes were created."""
        models = [
            node for node, data in built_graph.nodes(data=True)
            if data.get("node_type") == NodeType.COMMON_MODEL.value
        ]
        assert len(models) > 0, "No model nodes found"

    def test_output_nodes_exist(self, built_graph):
        """Verify AI_OUTPUT nodes were created."""
        outputs = [
            node for node, data in built_graph.nodes(data=True)
            if data.get("node_type") == NodeType.AI_OUTPUT.value
        ]
        assert len(outputs) > 0, "No output nodes found"

    def test_prerequisite_nodes_exist(self, built_graph):
        """Verify AI_PREREQUISITE nodes were created."""
        prerequisites = [
            node for node, data in built_graph.nodes(data=True)
            if data.get("node_type") == NodeType.AI_PREREQUISITE.value
        ]
        assert len(prerequisites) > 0, "No prerequisite nodes found"

    def test_function_nodes_exist(self, built_graph):
        """Verify BUSINESS_FUNCTION nodes were created."""
        functions = [
            node for node, data in built_graph.nodes(data=True)
            if data.get("node_type") == NodeType.BUSINESS_FUNCTION.value
        ]
        assert len(functions) > 0, "No function nodes found"

    def test_maturity_nodes_exist(self, built_graph):
        """Verify MATURITY_DIMENSION nodes were created."""
        maturity = [
            node for node, data in built_graph.nodes(data=True)
            if data.get("node_type") == NodeType.MATURITY_DIMENSION.value
        ]
        assert len(maturity) > 0, "No maturity dimension nodes found"
        # AI_discovery.json has 4 maturity subdimensions
        assert len(maturity) == 4, f"Expected 4 maturity dimensions, got {len(maturity)}"


class TestEdgeTypes:
    """Tests for specific edge types."""

    def test_implemented_by_edges_exist(self, built_graph):
        """Verify IMPLEMENTED_BY edges were created."""
        edges = [
            (s, t) for s, t, data in built_graph.edges(data=True)
            if data.get("relationship") == EdgeType.IMPLEMENTED_BY.value
        ]
        assert len(edges) > 0, "No IMPLEMENTED_BY edges found"

    def test_produces_output_edges_exist(self, built_graph):
        """Verify PRODUCES_OUTPUT edges were created."""
        edges = [
            (s, t) for s, t, data in built_graph.edges(data=True)
            if data.get("relationship") == EdgeType.PRODUCES_OUTPUT.value
        ]
        assert len(edges) > 0, "No PRODUCES_OUTPUT edges found"

    def test_requires_edges_exist(self, built_graph):
        """Verify REQUIRES edges were created."""
        edges = [
            (s, t) for s, t, data in built_graph.edges(data=True)
            if data.get("relationship") == EdgeType.REQUIRES.value
        ]
        assert len(edges) > 0, "No REQUIRES edges found"


class TestGraphTraversal:
    """Tests for basic graph traversal."""

    def test_archetype_to_models(self, built_graph):
        """Test traversal from archetype to models."""
        # Find an archetype node
        archetype_nodes = [
            node for node, data in built_graph.nodes(data=True)
            if data.get("node_type") == NodeType.AI_ARCHETYPE.value
        ]
        assert len(archetype_nodes) > 0

        # Check if it has IMPLEMENTED_BY edges
        archetype_id = archetype_nodes[0]
        successors = list(built_graph.successors(archetype_id))

        # Filter for models
        model_successors = [
            node for node in successors
            if built_graph.nodes[node].get("node_type") == NodeType.COMMON_MODEL.value
        ]

        # At least some archetypes should have models
        if len(model_successors) > 0:
            # Verify edge relationship
            edge_data = built_graph.edges[archetype_id, model_successors[0]]
            assert edge_data.get("relationship") == EdgeType.IMPLEMENTED_BY.value

    def test_model_to_prerequisites(self, built_graph):
        """Test traversal from model to prerequisites."""
        # Find a model node
        model_nodes = [
            node for node, data in built_graph.nodes(data=True)
            if data.get("node_type") == NodeType.COMMON_MODEL.value
        ]
        assert len(model_nodes) > 0

        # Check for REQUIRES edges
        found_prerequisite = False
        for model_id in model_nodes:
            successors = list(built_graph.successors(model_id))
            prereq_successors = [
                node for node in successors
                if built_graph.nodes[node].get("node_type") == NodeType.AI_PREREQUISITE.value
            ]

            if len(prereq_successors) > 0:
                found_prerequisite = True
                # Verify edge relationship
                edge_data = built_graph.edges[model_id, prereq_successors[0]]
                assert edge_data.get("relationship") == EdgeType.REQUIRES.value
                break

        assert found_prerequisite, "No model->prerequisite edges found"


class TestGraphStatistics:
    """Tests for graph statistics."""

    def test_get_statistics(self, graph_builder, built_graph):
        """Test statistics generation."""
        stats = graph_builder.get_statistics()

        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert stats["total_nodes"] > 0
        assert stats["total_edges"] > 0

        # Check node type counts
        for node_type in NodeType:
            key = f"nodes_{node_type.value}"
            assert key in stats

        # Check edge type counts
        for edge_type in EdgeType:
            key = f"edges_{edge_type.value}"
            assert key in stats


class TestSpecificArchetypes:
    """Tests for specific archetypes mentioned in requirements."""

    def test_optimization_scheduling_exists(self, built_graph):
        """Verify 'Optimization & Scheduling' archetype exists."""
        found = False
        for node_id, data in built_graph.nodes(data=True):
            if (data.get("node_type") == NodeType.AI_ARCHETYPE.value and
                "Optimization" in data.get("name", "")):
                found = True
                break
        assert found, "Optimization & Scheduling archetype not found"

    def test_anomaly_detection_exists(self, built_graph):
        """Verify 'Anomaly Detection' archetype exists."""
        found = False
        for node_id, data in built_graph.nodes(data=True):
            if (data.get("node_type") == NodeType.AI_ARCHETYPE.value and
                "Anomaly" in data.get("name", "")):
                found = True
                break
        assert found, "Anomaly Detection archetype not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
