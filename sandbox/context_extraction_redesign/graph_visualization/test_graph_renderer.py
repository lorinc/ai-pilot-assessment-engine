"""
Test suite for graph visualization renderer.

TDD RED Phase: Define expected behavior before implementation.
"""

import pytest
import json
from pathlib import Path


class TestGraphDataLoader:
    """Test loading and validating graph data."""
    
    def test_load_example_graph(self):
        """Should load example graph JSON successfully."""
        from graph_renderer import load_graph_data
        
        graph = load_graph_data("example_cascading_failures_graph.json")
        
        assert graph is not None
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) == 15
        assert len(graph["edges"]) == 14
    
    def test_graph_has_metadata(self):
        """Should include metadata about the graph."""
        from graph_renderer import load_graph_data
        
        graph = load_graph_data("example_cascading_failures_graph.json")
        
        assert "metadata" in graph
        assert graph["metadata"]["entities"] == 15
        assert graph["metadata"]["dependencies"] == 14
    
    def test_invalid_file_raises_error(self):
        """Should raise error for non-existent file."""
        from graph_renderer import load_graph_data
        
        with pytest.raises(FileNotFoundError):
            load_graph_data("nonexistent.json")


class TestNodeFormatting:
    """Test converting graph nodes to st-link-analysis format."""
    
    def test_format_actor_node(self):
        """Should format actor node with correct style."""
        from graph_renderer import format_node
        
        node = {
            "data": {
                "id": "marketing_team",
                "label": "Actor",
                "name": "Marketing Team",
                "reliability_score": 0.6,
                "issues": ["understaffed"]
            }
        }
        
        formatted = format_node(node)
        
        assert formatted["data"]["id"] == "marketing_team"
        assert formatted["data"]["label"] == "Actor"
        assert formatted["data"]["name"] == "Marketing Team"
        # Should include quality indicator
        assert "badge" in formatted["data"] or "quality_class" in formatted
    
    def test_format_artifact_node_with_quality(self):
        """Should format artifact with quality score and border color."""
        from graph_renderer import format_node
        
        node = {
            "data": {
                "id": "campaign_forecasts",
                "label": "Artifact",
                "name": "Campaign Forecasts",
                "data_quality_score": 0.3,
                "issues": ["scattered data"]
            }
        }
        
        formatted = format_node(node)
        
        # Should have quality badge
        assert "0.3" in str(formatted["data"].get("badge", ""))
        # Should have critical quality class (score < 0.4)
        assert "quality-critical" in formatted.get("classes", "")
    
    def test_format_tool_node(self):
        """Should format tool node correctly."""
        from graph_renderer import format_node
        
        node = {
            "data": {
                "id": "hubspot",
                "label": "Tool",
                "name": "HubSpot",
                "quality_score": 0.7
            }
        }
        
        formatted = format_node(node)
        
        assert formatted["data"]["label"] == "Tool"
        assert formatted["data"]["name"] == "HubSpot"


class TestEdgeFormatting:
    """Test converting graph edges to st-link-analysis format."""
    
    def test_format_performs_edge(self):
        """Should format PERFORMS edge correctly."""
        from graph_renderer import format_edge
        
        edge = {
            "data": {
                "id": "e1",
                "source": "marketing_team",
                "target": "create_forecasts",
                "label": "PERFORMS",
                "type": "PERFORMS"
            }
        }
        
        formatted = format_edge(edge)
        
        assert formatted["data"]["source"] == "marketing_team"
        assert formatted["data"]["target"] == "create_forecasts"
        assert formatted["data"]["label"] == "PERFORMS"
    
    def test_format_depends_on_edge_with_quality(self):
        """Should format DEPENDS_ON edge with error propagation indicator."""
        from graph_renderer import format_edge
        
        edge = {
            "data": {
                "id": "e9",
                "source": "adjust_projections",
                "target": "campaign_forecasts",
                "label": "DEPENDS_ON",
                "type": "DEPENDS_ON",
                "error_propagation_factor": 0.8
            }
        }
        
        formatted = format_edge(edge)
        
        # Should have class indicating high error propagation
        assert "error-high" in formatted.get("classes", "")


class TestStyleDefinitions:
    """Test node and edge style definitions."""
    
    def test_get_node_styles(self):
        """Should return NodeStyle objects for all entity types."""
        from graph_renderer import get_node_styles
        
        styles = get_node_styles()
        
        assert len(styles) == 4  # Actor, Artifact, Tool, Activity
        
        # Check each style has required properties
        for style in styles:
            assert hasattr(style, 'label')
            assert hasattr(style, 'color')
            assert hasattr(style, 'caption')
            assert hasattr(style, 'icon')
    
    def test_get_edge_styles(self):
        """Should return EdgeStyle objects for all relationship types."""
        from graph_renderer import get_edge_styles
        
        styles = get_edge_styles()
        
        assert len(styles) == 4  # PERFORMS, PRODUCES, DEPENDS_ON, USES
        
        # Check each style has required properties
        for style in styles:
            assert hasattr(style, 'label')
            assert style.directed == True  # All edges are directed


class TestGraphRenderer:
    """Test main graph rendering function."""
    
    def test_render_graph_returns_elements(self):
        """Should return formatted elements dict for st-link-analysis."""
        from graph_renderer import render_graph
        
        graph_data = {
            "nodes": [
                {"data": {"id": "n1", "label": "Actor", "name": "Team"}}
            ],
            "edges": [
                {"data": {"id": "e1", "source": "n1", "target": "n2", "label": "PERFORMS"}}
            ]
        }
        
        elements = render_graph(graph_data)
        
        assert "nodes" in elements
        assert "edges" in elements
        assert len(elements["nodes"]) == 1
        assert len(elements["edges"]) == 1
    
    def test_render_graph_with_quality_highlighting(self):
        """Should highlight nodes with quality issues."""
        from graph_renderer import render_graph
        
        graph_data = {
            "nodes": [
                {
                    "data": {
                        "id": "artifact1",
                        "label": "Artifact",
                        "name": "Bad Output",
                        "data_quality_score": 0.2
                    }
                }
            ],
            "edges": []
        }
        
        elements = render_graph(graph_data)
        
        # Node should have critical quality class
        node = elements["nodes"][0]
        assert "quality-critical" in node.get("classes", "")


class TestQualityAnalysis:
    """Test quality analysis and bottleneck detection."""
    
    def test_identify_bottleneck(self):
        """Should identify lowest quality artifact as bottleneck."""
        from graph_renderer import identify_bottleneck
        
        graph_data = {
            "nodes": [
                {"data": {"id": "a1", "label": "Artifact", "data_quality_score": 0.5}},
                {"data": {"id": "a2", "label": "Artifact", "data_quality_score": 0.2}},
                {"data": {"id": "a3", "label": "Artifact", "data_quality_score": 0.8}}
            ]
        }
        
        bottleneck = identify_bottleneck(graph_data)
        
        assert bottleneck["id"] == "a2"
        assert bottleneck["score"] == 0.2
    
    def test_calculate_quality_summary(self):
        """Should calculate quality statistics."""
        from graph_renderer import calculate_quality_summary
        
        graph_data = {
            "nodes": [
                {"data": {"id": "a1", "label": "Artifact", "data_quality_score": 0.3}},
                {"data": {"id": "a2", "label": "Artifact", "data_quality_score": 0.4}},
                {"data": {"id": "a3", "label": "Artifact", "data_quality_score": 0.2}}
            ]
        }
        
        summary = calculate_quality_summary(graph_data)
        
        assert summary["avg_quality"] == 0.3
        assert summary["min_quality"] == 0.2
        assert summary["max_quality"] == 0.4
        assert summary["artifacts_with_issues"] == 3


# UAT Test Cases
class TestUATScenarios:
    """User Acceptance Test scenarios."""
    
    def test_uat_load_and_display_cascading_failures(self):
        """
        UAT Scenario 1: Load cascading failures graph and display it.
        
        User Story:
        As a user, I want to see the cascading failures graph visualized
        so that I can understand the operational flow.
        
        Acceptance Criteria:
        - Graph loads without errors
        - All 15 nodes are visible
        - All 14 edges are visible
        - Quality issues are color-coded
        """
        from graph_renderer import load_graph_data, render_graph
        
        # Load graph
        graph = load_graph_data("example_cascading_failures_graph.json")
        
        # Render
        elements = render_graph(graph)
        
        # Verify all nodes present
        assert len(elements["nodes"]) == 15
        
        # Verify all edges present
        assert len(elements["edges"]) == 14
        
        # Verify quality color coding exists
        critical_nodes = [
            n for n in elements["nodes"]
            if "quality-critical" in n.get("classes", "")
        ]
        assert len(critical_nodes) > 0  # Should have at least one critical node
    
    def test_uat_identify_quality_bottleneck(self):
        """
        UAT Scenario 2: Identify quality bottleneck visually.
        
        User Story:
        As a user, I want to see which output has the worst quality
        so that I know where to focus improvement efforts.
        
        Acceptance Criteria:
        - Bottleneck is identified (lowest quality artifact)
        - Bottleneck has red border
        - Quality score is displayed
        """
        from graph_renderer import load_graph_data, identify_bottleneck
        
        graph = load_graph_data("example_cascading_failures_graph.json")
        bottleneck = identify_bottleneck(graph)
        
        # Should identify one of the 0.2 quality artifacts as bottleneck
        assert bottleneck["score"] == 0.2
        assert bottleneck["name"] in ["Production Forecasts", "Manufacturing Orders"]
    
    def test_uat_see_dependency_chain(self):
        """
        UAT Scenario 3: See dependency chain from marketing to production.
        
        User Story:
        As a user, I want to see how outputs depend on each other
        so that I can understand error propagation.
        
        Acceptance Criteria:
        - DEPENDS_ON edges are visible
        - Edges connect: campaign_forecasts → pipeline_projections → production
        - Error propagation factor is indicated by edge thickness/color
        """
        from graph_renderer import load_graph_data, render_graph
        
        graph = load_graph_data("example_cascading_failures_graph.json")
        elements = render_graph(graph)
        
        # Find DEPENDS_ON edges
        dependency_edges = [
            e for e in elements["edges"]
            if e["data"]["label"] == "DEPENDS_ON"
        ]
        
        assert len(dependency_edges) == 2  # Two critical dependencies
        
        # Verify error propagation indicators
        high_error_edges = [
            e for e in dependency_edges
            if "error-high" in e.get("classes", "")
        ]
        assert len(high_error_edges) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
