"""Unit tests for BottleneckEngine."""

import pytest
from unittest.mock import Mock

from engines.bottleneck import BottleneckEngine


class TestBottleneckEngine:
    """Test BottleneckEngine."""
    
    @pytest.fixture
    def mock_graph(self):
        """Create mock GraphManager."""
        graph = Mock()
        graph.calculate_output_quality.return_value = None
        graph.identify_bottlenecks.return_value = []
        graph.get_incoming_edges.return_value = []
        graph.get_node.return_value = None
        return graph
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()
    
    @pytest.fixture
    def bottleneck_engine(self, mock_graph, mock_logger):
        """Create BottleneckEngine instance."""
        return BottleneckEngine(
            graph_manager=mock_graph,
            logger=mock_logger
        )
    
    def test_analyze_output_not_assessed(self, bottleneck_engine, mock_graph):
        """Test analyzing output with no assessments."""
        mock_graph.calculate_output_quality.return_value = None
        
        result = bottleneck_engine.analyze_output("output_1")
        
        assert result["status"] == "not_assessed"
        assert "message" in result
    
    def test_analyze_output_no_bottlenecks(self, bottleneck_engine, mock_graph):
        """Test analyzing output with no bottlenecks (all edges equal)."""
        mock_graph.calculate_output_quality.return_value = 3.0
        mock_graph.identify_bottlenecks.return_value = []
        mock_graph.get_incoming_edges.return_value = [
            ("team", "output", {"edge_type": "team_execution", "current_score": 3.0, "current_confidence": 0.7, "evidence": []}),
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": 3.0, "current_confidence": 0.8, "evidence": []})
        ]
        
        result = bottleneck_engine.analyze_output("output_1")
        
        assert result["status"] == "analyzed"
        assert result["current_quality"] == 3.0
        assert result["bottleneck_count"] == 0
        assert "⭐⭐⭐" in result["current_quality_display"]
    
    def test_analyze_output_single_bottleneck(self, bottleneck_engine, mock_graph):
        """Test analyzing output with single bottleneck."""
        mock_graph.calculate_output_quality.return_value = 2.0
        mock_graph.identify_bottlenecks.return_value = [
            ("tool", "output", {
                "edge_type": "system_capabilities",
                "current_score": 2.0,
                "current_confidence": 0.8,
                "evidence": [{"statement": "CRM is terrible"}]
            })
        ]
        mock_graph.get_incoming_edges.return_value = [
            ("team", "output", {"edge_type": "team_execution", "current_score": 4.0, "current_confidence": 0.7, "evidence": []}),
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": 2.0, "current_confidence": 0.8, "evidence": [{"statement": "CRM is terrible"}]})
        ]
        mock_graph.get_node.return_value = {"name": "CRM System"}
        
        result = bottleneck_engine.analyze_output("output_1")
        
        assert result["status"] == "analyzed"
        assert result["current_quality"] == 2.0
        assert result["bottleneck_count"] == 1
        assert len(result["bottlenecks"]) == 1
        assert result["bottlenecks"][0]["edge_type"] == "system_capabilities"
    
    def test_analyze_output_multiple_bottlenecks(self, bottleneck_engine, mock_graph):
        """Test analyzing output with multiple bottlenecks."""
        mock_graph.calculate_output_quality.return_value = 2.0
        mock_graph.identify_bottlenecks.return_value = [
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": 2.0, "current_confidence": 0.8, "evidence": []}),
            ("process", "output", {"edge_type": "process_maturity", "current_score": 2.0, "current_confidence": 0.6, "evidence": []})
        ]
        mock_graph.get_incoming_edges.return_value = [
            ("team", "output", {"edge_type": "team_execution", "current_score": 4.0, "current_confidence": 0.7, "evidence": []}),
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": 2.0, "current_confidence": 0.8, "evidence": []}),
            ("process", "output", {"edge_type": "process_maturity", "current_score": 2.0, "current_confidence": 0.6, "evidence": []})
        ]
        mock_graph.get_node.return_value = {"name": "Test Node"}
        
        result = bottleneck_engine.analyze_output("output_1")
        
        assert result["bottleneck_count"] == 2
        assert len(result["bottlenecks"]) == 2
    
    def test_analyze_output_with_gap(self, bottleneck_engine, mock_graph):
        """Test analyzing output with quality gap."""
        mock_graph.calculate_output_quality.return_value = 2.0
        mock_graph.identify_bottlenecks.return_value = []
        mock_graph.get_incoming_edges.return_value = []
        
        result = bottleneck_engine.analyze_output("output_1", required_quality=4.0)
        
        assert result["required_quality"] == 4.0
        assert result["gap"] == 2.0
        assert result["gap_stars"] == 2
    
    def test_root_cause_categorization(self, bottleneck_engine, mock_graph):
        """Test root cause categorization."""
        mock_graph.calculate_output_quality.return_value = 1.5
        mock_graph.identify_bottlenecks.return_value = [
            ("team", "output", {"edge_type": "team_execution", "current_score": 1.5, "current_confidence": 0.7, "evidence": []}),
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": 1.5, "current_confidence": 0.8, "evidence": []})
        ]
        mock_graph.get_incoming_edges.return_value = []
        mock_graph.get_node.return_value = {"name": "Test"}
        
        result = bottleneck_engine.analyze_output("output_1")
        
        root_causes = result["root_causes"]
        assert len(root_causes) == 2
        
        # Check team execution maps to Augmentation/Automation
        team_cause = [c for c in root_causes if c["edge_type"] == "team_execution"][0]
        assert team_cause["category"] == "Execution Issue"
        assert "Augmentation/Automation" in team_cause["solution_type"]
        
        # Check system capabilities maps to Intelligent Features
        system_cause = [c for c in root_causes if c["edge_type"] == "system_capabilities"][0]
        assert system_cause["category"] == "System Issue"
        assert "Intelligent Features" in system_cause["solution_type"]
    
    def test_score_to_stars(self, bottleneck_engine):
        """Test score to stars conversion."""
        assert "⭐" in bottleneck_engine._score_to_stars(1.0)
        assert "⭐⭐" in bottleneck_engine._score_to_stars(2.0)
        assert "⭐⭐⭐" in bottleneck_engine._score_to_stars(3.0)
        assert "⭐⭐⭐⭐" in bottleneck_engine._score_to_stars(4.0)
        assert "⭐⭐⭐⭐⭐" in bottleneck_engine._score_to_stars(5.0)
        assert "½" in bottleneck_engine._score_to_stars(2.5)
        assert "Not assessed" in bottleneck_engine._score_to_stars(None)
    
    def test_get_improvement_priority(self, bottleneck_engine, mock_graph):
        """Test getting prioritized improvement opportunities."""
        mock_graph.calculate_output_quality.return_value = 2.0
        mock_graph.identify_bottlenecks.return_value = [
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": 2.0, "current_confidence": 0.8, "evidence": []}),
            ("process", "output", {"edge_type": "process_maturity", "current_score": 2.0, "current_confidence": 0.5, "evidence": []})
        ]
        mock_graph.get_incoming_edges.return_value = []
        mock_graph.get_node.return_value = {"name": "Test"}
        
        priorities = bottleneck_engine.get_improvement_priority("output_1")
        
        assert len(priorities) == 2
        # Higher confidence should come first when scores are equal
        assert priorities[0]["confidence"] == 0.8
    
    def test_compare_outputs(self, bottleneck_engine, mock_graph):
        """Test comparing multiple outputs."""
        def mock_quality(output_id):
            qualities = {"output_1": 2.0, "output_2": 4.0, "output_3": 3.0}
            return qualities.get(output_id)
        
        def mock_bottlenecks(output_id):
            bottlenecks = {"output_1": [("a", "b", {})], "output_2": [], "output_3": [("c", "d", {})]}
            return bottlenecks.get(output_id, [])
        
        mock_graph.calculate_output_quality.side_effect = mock_quality
        mock_graph.identify_bottlenecks.side_effect = mock_bottlenecks
        mock_graph.get_node.return_value = {"name": "Test Output"}
        
        result = bottleneck_engine.compare_outputs(["output_1", "output_2", "output_3"])
        
        assert result["output_count"] == 3
        # Should be sorted by quality (lowest first)
        assert result["outputs"][0]["output_id"] == "output_1"  # 2.0
        assert result["outputs"][1]["output_id"] == "output_3"  # 3.0
        assert result["outputs"][2]["output_id"] == "output_2"  # 4.0
        assert result["lowest_quality"]["output_id"] == "output_1"
        assert result["highest_quality"]["output_id"] == "output_2"
    
    def test_get_gap_summary_no_gap(self, bottleneck_engine, mock_graph):
        """Test gap summary when quality meets requirement."""
        mock_graph.calculate_output_quality.return_value = 4.0
        mock_graph.identify_bottlenecks.return_value = []
        mock_graph.get_incoming_edges.return_value = []
        
        result = bottleneck_engine.get_gap_summary("output_1", 4.0)
        
        assert result["severity"] == "none"
        assert result["gap"] <= 0
    
    def test_get_gap_summary_minor(self, bottleneck_engine, mock_graph):
        """Test gap summary with minor gap."""
        mock_graph.calculate_output_quality.return_value = 3.5
        mock_graph.identify_bottlenecks.return_value = []
        mock_graph.get_incoming_edges.return_value = []
        
        result = bottleneck_engine.get_gap_summary("output_1", 4.0)
        
        assert result["severity"] == "minor"
        assert 0 < result["gap"] <= 1
    
    def test_get_gap_summary_moderate(self, bottleneck_engine, mock_graph):
        """Test gap summary with moderate gap."""
        mock_graph.calculate_output_quality.return_value = 2.5
        mock_graph.identify_bottlenecks.return_value = []
        mock_graph.get_incoming_edges.return_value = []
        
        result = bottleneck_engine.get_gap_summary("output_1", 4.0)
        
        assert result["severity"] == "moderate"
        assert 1 < result["gap"] <= 2
    
    def test_get_gap_summary_significant(self, bottleneck_engine, mock_graph):
        """Test gap summary with significant gap."""
        mock_graph.calculate_output_quality.return_value = 1.5
        mock_graph.identify_bottlenecks.return_value = []
        mock_graph.get_incoming_edges.return_value = []
        
        result = bottleneck_engine.get_gap_summary("output_1", 4.0)
        
        assert result["severity"] == "significant"
        assert 2 < result["gap"] <= 3
    
    def test_get_gap_summary_critical(self, bottleneck_engine, mock_graph):
        """Test gap summary with critical gap."""
        mock_graph.calculate_output_quality.return_value = 1.0
        mock_graph.identify_bottlenecks.return_value = []
        mock_graph.get_incoming_edges.return_value = []
        
        result = bottleneck_engine.get_gap_summary("output_1", 5.0)
        
        assert result["severity"] == "critical"
        assert result["gap"] > 3
    
    def test_get_solution_recommendations(self, bottleneck_engine, mock_graph):
        """Test getting solution recommendations."""
        mock_graph.calculate_output_quality.return_value = 2.0
        mock_graph.identify_bottlenecks.return_value = [
            ("team", "output", {"edge_type": "team_execution", "current_score": 2.0, "current_confidence": 0.7, "evidence": []}),
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": 2.0, "current_confidence": 0.8, "evidence": []})
        ]
        mock_graph.get_incoming_edges.return_value = []
        mock_graph.get_node.return_value = {"name": "Test"}
        
        recommendations = bottleneck_engine.get_solution_recommendations("output_1")
        
        assert len(recommendations) == 2
        # Should have both Augmentation/Automation and Intelligent Features
        solution_types = [r["solution_type"] for r in recommendations]
        assert "Augmentation/Automation AI Pilots" in solution_types
        assert "Intelligent Features AI Pilots" in solution_types
    
    def test_get_solution_recommendations_prioritized(self, bottleneck_engine, mock_graph):
        """Test that solution recommendations are prioritized correctly."""
        mock_graph.calculate_output_quality.return_value = 1.5
        mock_graph.identify_bottlenecks.return_value = [
            ("team", "output", {"edge_type": "team_execution", "current_score": 1.0, "current_confidence": 0.7, "evidence": []}),  # High priority
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": 3.0, "current_confidence": 0.8, "evidence": []})  # Low priority
        ]
        mock_graph.get_incoming_edges.return_value = []
        mock_graph.get_node.return_value = {"name": "Test"}
        
        recommendations = bottleneck_engine.get_solution_recommendations("output_1")
        
        # High priority (score < 2) should come first
        assert recommendations[0]["priority"] == "high"
        assert recommendations[1]["priority"] == "low"
