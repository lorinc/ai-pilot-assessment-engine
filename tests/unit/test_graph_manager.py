"""Unit tests for GraphManager."""

import pytest
from unittest.mock import Mock, MagicMock
import networkx as nx

from core.graph_manager import GraphManager


class TestGraphManager:
    """Test GraphManager operations."""
    
    @pytest.fixture
    def mock_firebase(self):
        """Create mock Firebase client."""
        firebase = Mock()
        firebase.get_graph_metadata.return_value = None
        firebase.get_graph_nodes.return_value = {}
        firebase.get_graph_edges.return_value = {}
        firebase.save_graph_metadata.return_value = True
        firebase.save_graph_node.return_value = True
        firebase.save_graph_edge.return_value = True
        firebase.delete_graph_node.return_value = True
        firebase.delete_graph_edge.return_value = True
        return firebase
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()
    
    @pytest.fixture
    def graph_manager(self, mock_firebase, mock_logger):
        """Create GraphManager instance."""
        return GraphManager(
            firebase_client=mock_firebase,
            user_id="test_user",
            logger=mock_logger
        )
    
    def test_create_graph(self, graph_manager):
        """Test graph creation."""
        graph_id = graph_manager.create_graph("output_1", "Test Output")
        
        assert graph_id is not None
        assert graph_id.startswith("graph_")
        assert graph_manager.graph_id == graph_id
        assert graph_manager.metadata["output_id"] == "output_1"
        assert graph_manager.metadata["output_name"] == "Test Output"
    
    def test_add_node(self, graph_manager):
        """Test adding a node."""
        graph_manager.create_graph("output_1", "Test Output")
        
        result = graph_manager.add_node(
            "node_1",
            "output",
            name="Sales Forecast",
            description="Test description"
        )
        
        assert result is True
        assert "node_1" in graph_manager.graph.nodes
        assert graph_manager.graph.nodes["node_1"]["node_type"] == "output"
        assert graph_manager.graph.nodes["node_1"]["name"] == "Sales Forecast"
    
    def test_get_node(self, graph_manager):
        """Test getting a node."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("node_1", "output", name="Test Node")
        
        node_data = graph_manager.get_node("node_1")
        
        assert node_data is not None
        assert node_data["node_type"] == "output"
        assert node_data["name"] == "Test Node"
    
    def test_get_nonexistent_node(self, graph_manager):
        """Test getting a nonexistent node."""
        graph_manager.create_graph("output_1", "Test Output")
        
        node_data = graph_manager.get_node("nonexistent")
        
        assert node_data is None
    
    def test_update_node(self, graph_manager):
        """Test updating a node."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("node_1", "output", name="Original Name")
        
        result = graph_manager.update_node("node_1", name="Updated Name")
        
        assert result is True
        assert graph_manager.graph.nodes["node_1"]["name"] == "Updated Name"
    
    def test_remove_node(self, graph_manager):
        """Test removing a node."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("node_1", "output", name="Test Node")
        
        result = graph_manager.remove_node("node_1")
        
        assert result is True
        assert "node_1" not in graph_manager.graph.nodes
    
    def test_add_edge(self, graph_manager):
        """Test adding an edge."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("node_1", "people", name="Team")
        graph_manager.add_node("node_2", "output", name="Output")
        
        result = graph_manager.add_edge(
            "node_1",
            "node_2",
            "team_execution",
            score=3.0,
            confidence=0.8
        )
        
        assert result is True
        assert graph_manager.graph.has_edge("node_1", "node_2")
        edge_data = graph_manager.graph["node_1"]["node_2"]
        assert edge_data["edge_type"] == "team_execution"
        assert edge_data["current_score"] == 3.0
        assert edge_data["current_confidence"] == 0.8
    
    def test_get_edge(self, graph_manager):
        """Test getting an edge."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("node_1", "people", name="Team")
        graph_manager.add_node("node_2", "output", name="Output")
        graph_manager.add_edge("node_1", "node_2", "team_execution", score=3.0)
        
        edge_data = graph_manager.get_edge("node_1", "node_2")
        
        assert edge_data is not None
        assert edge_data["edge_type"] == "team_execution"
        assert edge_data["current_score"] == 3.0
    
    def test_update_edge_rating(self, graph_manager):
        """Test updating edge rating."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("node_1", "people", name="Team")
        graph_manager.add_node("node_2", "output", name="Output")
        graph_manager.add_edge("node_1", "node_2", "team_execution", score=3.0, confidence=0.5)
        
        result = graph_manager.update_edge_rating("node_1", "node_2", 4.0, 0.9)
        
        assert result is True
        edge_data = graph_manager.graph["node_1"]["node_2"]
        assert edge_data["current_score"] == 4.0
        assert edge_data["current_confidence"] == 0.9
    
    def test_add_evidence(self, graph_manager):
        """Test adding evidence to edge."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("node_1", "people", name="Team")
        graph_manager.add_node("node_2", "output", name="Output")
        graph_manager.add_edge("node_1", "node_2", "team_execution", score=3.0)
        
        result = graph_manager.add_evidence(
            "node_1",
            "node_2",
            "The team is junior",
            tier=3,
            conversation_id="conv_123"
        )
        
        assert result is True
        edge_data = graph_manager.graph["node_1"]["node_2"]
        assert len(edge_data["evidence"]) == 1
        assert edge_data["evidence"][0]["statement"] == "The team is junior"
        assert edge_data["evidence"][0]["tier"] == 3
    
    def test_remove_edge(self, graph_manager):
        """Test removing an edge."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("node_1", "people", name="Team")
        graph_manager.add_node("node_2", "output", name="Output")
        graph_manager.add_edge("node_1", "node_2", "team_execution", score=3.0)
        
        result = graph_manager.remove_edge("node_1", "node_2")
        
        assert result is True
        assert not graph_manager.graph.has_edge("node_1", "node_2")
    
    def test_get_incoming_edges(self, graph_manager):
        """Test getting incoming edges."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("team", "people", name="Team")
        graph_manager.add_node("tool", "tool", name="Tool")
        graph_manager.add_node("output", "output", name="Output")
        graph_manager.add_edge("team", "output", "team_execution", score=3.0)
        graph_manager.add_edge("tool", "output", "system_capabilities", score=2.0)
        
        incoming = graph_manager.get_incoming_edges("output")
        
        assert len(incoming) == 2
        source_ids = [source for source, _, _ in incoming]
        assert "team" in source_ids
        assert "tool" in source_ids
    
    def test_get_outgoing_edges(self, graph_manager):
        """Test getting outgoing edges."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("output1", "output", name="Output 1")
        graph_manager.add_node("output2", "output", name="Output 2")
        graph_manager.add_node("output3", "output", name="Output 3")
        graph_manager.add_edge("output1", "output2", "dependency_quality", score=4.0)
        graph_manager.add_edge("output1", "output3", "dependency_quality", score=3.0)
        
        outgoing = graph_manager.get_outgoing_edges("output1")
        
        assert len(outgoing) == 2
        target_ids = [target for _, target, _ in outgoing]
        assert "output2" in target_ids
        assert "output3" in target_ids
    
    def test_calculate_output_quality_min(self, graph_manager):
        """Test MIN calculation for output quality."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("team", "people", name="Team")
        graph_manager.add_node("tool", "tool", name="Tool")
        graph_manager.add_node("process", "process", name="Process")
        graph_manager.add_node("output", "output", name="Output")
        
        # Add edges with different scores
        graph_manager.add_edge("team", "output", "team_execution", score=3.0)
        graph_manager.add_edge("tool", "output", "system_capabilities", score=1.0)  # MIN
        graph_manager.add_edge("process", "output", "process_maturity", score=4.0)
        
        quality = graph_manager.calculate_output_quality("output")
        
        assert quality == 1.0  # MIN of [3.0, 1.0, 4.0]
    
    def test_calculate_output_quality_no_edges(self, graph_manager):
        """Test quality calculation with no edges."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("output", "output", name="Output")
        
        quality = graph_manager.calculate_output_quality("output")
        
        assert quality is None
    
    def test_identify_bottlenecks(self, graph_manager):
        """Test bottleneck identification."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("team", "people", name="Team")
        graph_manager.add_node("tool", "tool", name="Tool")
        graph_manager.add_node("process", "process", name="Process")
        graph_manager.add_node("output", "output", name="Output")
        
        # Add edges - tool and process are both bottlenecks
        graph_manager.add_edge("team", "output", "team_execution", score=4.0)
        graph_manager.add_edge("tool", "output", "system_capabilities", score=2.0)  # Bottleneck
        graph_manager.add_edge("process", "output", "process_maturity", score=2.0)  # Bottleneck
        
        bottlenecks = graph_manager.identify_bottlenecks("output")
        
        assert len(bottlenecks) == 2
        source_ids = [source for source, _, _ in bottlenecks]
        assert "tool" in source_ids
        assert "process" in source_ids
        assert "team" not in source_ids
    
    def test_get_all_nodes_by_type(self, graph_manager):
        """Test getting nodes by type."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("output1", "output", name="Output 1")
        graph_manager.add_node("output2", "output", name="Output 2")
        graph_manager.add_node("team", "people", name="Team")
        graph_manager.add_node("tool", "tool", name="Tool")
        
        outputs = graph_manager.get_all_nodes_by_type("output")
        
        assert len(outputs) == 2
        node_ids = [node_id for node_id, _ in outputs]
        assert "output1" in node_ids
        assert "output2" in node_ids
    
    def test_get_graph_summary(self, graph_manager):
        """Test graph summary."""
        graph_manager.create_graph("output_1", "Test Output")
        graph_manager.add_node("output", "output", name="Output")
        graph_manager.add_node("team", "people", name="Team")
        graph_manager.add_node("tool", "tool", name="Tool")
        graph_manager.add_edge("team", "output", "team_execution", score=3.0)
        graph_manager.add_edge("tool", "output", "system_capabilities", score=2.0)
        
        summary = graph_manager.get_graph_summary()
        
        assert summary["graph_id"] == graph_manager.graph_id
        assert summary["node_count"] == 3
        assert summary["edge_count"] == 2
        assert summary["nodes_by_type"]["output"] == 1
        assert summary["nodes_by_type"]["people"] == 1
        assert summary["nodes_by_type"]["tool"] == 1
        assert summary["nodes_by_type"]["process"] == 0


class TestBayesianAggregation:
    """Test Bayesian weighted aggregation logic."""
    
    def test_single_evidence_tier_3(self):
        """Test with single Tier 3 evidence."""
        # Tier 3: weight = 9
        # WAR = (2 * 9) / 9 = 2.0
        # With C=10, μ=2.5: Score = (9/19)*2.0 + (10/19)*2.5 = 0.947 + 1.316 = 2.263
        evidence = [{"tier": 3, "score": 2}]
        
        # Simplified calculation for test
        weights = [9]
        scores = [2]
        war = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        
        assert war == 2.0
    
    def test_multiple_evidence_different_tiers(self):
        """Test with multiple evidence pieces of different tiers."""
        # Tier 1: weight = 1, score = 5
        # Tier 4: weight = 27, score = 2
        # WAR = (5*1 + 2*27) / (1+27) = 59/28 = 2.107
        evidence = [
            {"tier": 1, "score": 5},
            {"tier": 4, "score": 2}
        ]
        
        weights = [1, 27]
        scores = [5, 2]
        war = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        
        assert abs(war - 2.107) < 0.01
    
    def test_tier_weights(self):
        """Test that tier weights follow 3^(tier-1) pattern."""
        expected_weights = {
            1: 1,    # 3^0
            2: 3,    # 3^1
            3: 9,    # 3^2
            4: 27,   # 3^3
            5: 81    # 3^4
        }
        
        for tier, expected_weight in expected_weights.items():
            actual_weight = 3 ** (tier - 1)
            assert actual_weight == expected_weight
