"""Unit tests for AssessmentEngine."""

import pytest
from unittest.mock import Mock, AsyncMock
import json

from engines.assessment import AssessmentEngine


class TestAssessmentEngine:
    """Test AssessmentEngine."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM client."""
        llm = Mock()
        llm.generate_text = AsyncMock()
        return llm
    
    @pytest.fixture
    def mock_graph(self):
        """Create mock GraphManager."""
        graph = Mock()
        graph.get_edge.return_value = None
        graph.add_edge.return_value = True
        graph.update_edge_rating.return_value = True
        graph.add_evidence.return_value = True
        graph.get_incoming_edges.return_value = []
        return graph
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()
    
    @pytest.fixture
    def assessment_engine(self, mock_llm, mock_graph, mock_logger):
        """Create AssessmentEngine instance."""
        return AssessmentEngine(
            llm_client=mock_llm,
            graph_manager=mock_graph,
            logger=mock_logger
        )
    
    def test_tier_weights(self, assessment_engine):
        """Test that tier weights follow 3^(tier-1) pattern."""
        assert assessment_engine.get_tier_weight(1) == 1
        assert assessment_engine.get_tier_weight(2) == 3
        assert assessment_engine.get_tier_weight(3) == 9
        assert assessment_engine.get_tier_weight(4) == 27
        assert assessment_engine.get_tier_weight(5) == 81
    
    def test_validate_rating(self, assessment_engine):
        """Test rating validation."""
        assert assessment_engine.validate_rating(1) is True
        assert assessment_engine.validate_rating(3) is True
        assert assessment_engine.validate_rating(5) is True
        assert assessment_engine.validate_rating(0) is False
        assert assessment_engine.validate_rating(6) is False
        assert assessment_engine.validate_rating(3.5) is True
    
    def test_score_to_stars(self, assessment_engine):
        """Test score to stars conversion."""
        assert "⭐" in assessment_engine._score_to_stars(1.0)
        assert "⭐⭐⭐" in assessment_engine._score_to_stars(3.0)
        assert "⭐⭐⭐⭐⭐" in assessment_engine._score_to_stars(5.0)
        assert "Not assessed" in assessment_engine._score_to_stars(None)
    
    def test_calculate_bayesian_score_empty(self, assessment_engine):
        """Test Bayesian calculation with no evidence."""
        score, confidence = assessment_engine.calculate_bayesian_score([])
        
        assert score == 2.5  # Prior mean
        assert confidence == 0.0
    
    def test_calculate_bayesian_score_single_tier3(self, assessment_engine):
        """Test Bayesian calculation with single Tier 3 evidence."""
        evidence = [{"score": 2, "tier": 3}]
        
        score, confidence = assessment_engine.calculate_bayesian_score(evidence)
        
        # Tier 3 weight = 9
        # WAR = 2
        # Confidence = 9 / (9 + 10) = 0.474
        # Score = 0.474 * 2 + 0.526 * 2.5 = 2.263
        assert 2.2 < score < 2.3
        assert 0.47 < confidence < 0.48
    
    def test_calculate_bayesian_score_multiple_evidence(self, assessment_engine):
        """Test Bayesian calculation with multiple evidence pieces."""
        evidence = [
            {"score": 5, "tier": 1},  # weight=1
            {"score": 2, "tier": 4}   # weight=27
        ]
        
        score, confidence = assessment_engine.calculate_bayesian_score(evidence)
        
        # WAR = (5*1 + 2*27) / (1+27) = 59/28 = 2.107
        # Confidence = 28 / (28 + 10) = 0.737
        # Score = 0.737 * 2.107 + 0.263 * 2.5 = 2.21
        assert 2.1 < score < 2.3
        assert 0.73 < confidence < 0.74
    
    def test_calculate_bayesian_score_high_confidence(self, assessment_engine):
        """Test Bayesian calculation with high confidence evidence."""
        evidence = [
            {"score": 4, "tier": 5},  # weight=81
            {"score": 4, "tier": 5},  # weight=81
            {"score": 4, "tier": 4}   # weight=27
        ]
        
        score, confidence = assessment_engine.calculate_bayesian_score(evidence)
        
        # Total weight = 81 + 81 + 27 = 189
        # WAR = (4*81 + 4*81 + 4*27) / 189 = 4.0
        # Confidence = 189 / (189 + 10) = 0.950
        # Score ≈ 4.0
        assert 3.9 < score < 4.1
        assert confidence > 0.94
    
    @pytest.mark.asyncio
    async def test_infer_rating_success(self, assessment_engine, mock_llm):
        """Test successful rating inference."""
        # Mock LLM response
        mock_response = json.dumps({
            "inferred_score": 2,
            "evidence_tier": 3,
            "reasoning": "Team is junior with limited experience",
            "confidence": 0.8
        })
        mock_llm.generate_text.return_value = mock_response
        
        # Infer rating
        result = await assessment_engine.infer_rating(
            "The team is junior, no one to learn from",
            "team_execution",
            {"output_name": "Sales Forecast"}
        )
        
        assert result["inferred_score"] == 2
        assert result["evidence_tier"] == 3
        assert result["confidence"] == 0.8
        assert "reasoning" in result
    
    @pytest.mark.asyncio
    async def test_infer_rating_invalid_json(self, assessment_engine, mock_llm):
        """Test rating inference with invalid JSON."""
        mock_llm.generate_text.return_value = "Not valid JSON"
        
        result = await assessment_engine.infer_rating(
            "Some statement",
            "team_execution"
        )
        
        # Should return defaults
        assert result["inferred_score"] == 3
        assert result["evidence_tier"] == 2
        assert result["confidence"] == 0.3
    
    @pytest.mark.asyncio
    async def test_infer_rating_constrains_values(self, assessment_engine, mock_llm):
        """Test that inferred values are constrained to valid ranges."""
        # Mock response with out-of-range values
        mock_response = json.dumps({
            "inferred_score": 10,  # Too high
            "evidence_tier": 0,    # Too low
            "reasoning": "Test",
            "confidence": 1.5      # Too high
        })
        mock_llm.generate_text.return_value = mock_response
        
        result = await assessment_engine.infer_rating(
            "Test statement",
            "team_execution"
        )
        
        # Should be constrained
        assert result["inferred_score"] == 5  # Max
        assert result["evidence_tier"] == 1   # Min
        assert result["confidence"] == 1.0    # Max
    
    @pytest.mark.asyncio
    async def test_assess_edge_new_edge(self, assessment_engine, mock_llm, mock_graph):
        """Test assessing a new edge."""
        # Mock LLM response
        mock_response = json.dumps({
            "inferred_score": 2,
            "evidence_tier": 3,
            "reasoning": "Team lacks experience",
            "confidence": 0.8
        })
        mock_llm.generate_text.return_value = mock_response
        mock_graph.get_edge.return_value = None  # New edge
        
        # Assess edge
        result = await assessment_engine.assess_edge(
            "team_node",
            "output_node",
            "team_execution",
            "The team is junior",
            "conv_123",
            {"output_name": "Sales Forecast"}
        )
        
        assert result["inferred_score"] == 2
        assert result["evidence_tier"] == 3
        assert result["evidence_count"] == 1
        assert "final_score" in result
        assert "confidence" in result
        
        # Verify graph operations called
        mock_graph.add_edge.assert_called_once()
        mock_graph.update_edge_rating.assert_called_once()
        mock_graph.add_evidence.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_assess_edge_existing_edge(self, assessment_engine, mock_llm, mock_graph):
        """Test assessing an existing edge with prior evidence."""
        # Mock LLM response
        mock_response = json.dumps({
            "inferred_score": 3,
            "evidence_tier": 4,
            "reasoning": "Provided example of improvement",
            "confidence": 0.9
        })
        mock_llm.generate_text.return_value = mock_response
        
        # Mock existing edge with evidence
        mock_graph.get_edge.return_value = {
            "edge_type": "team_execution",
            "current_score": 2.3,
            "current_confidence": 0.5,
            "evidence": [
                {"score": 2, "tier": 3, "statement": "Previous statement"}
            ]
        }
        
        # Assess edge
        result = await assessment_engine.assess_edge(
            "team_node",
            "output_node",
            "team_execution",
            "We hired a senior person who improved things",
            "conv_123"
        )
        
        assert result["evidence_count"] == 2  # Previous + new
        assert result["inferred_score"] == 3
        
        # Score should be updated based on both evidence pieces
        mock_graph.update_edge_rating.assert_called_once()
    
    def test_get_edge_assessment_summary(self, assessment_engine, mock_graph):
        """Test getting edge assessment summary."""
        # Mock edge data
        mock_graph.get_edge.return_value = {
            "edge_type": "team_execution",
            "current_score": 3.5,
            "current_confidence": 0.7,
            "evidence": [
                {"score": 3, "tier": 3, "statement": "Statement 1"},
                {"score": 4, "tier": 4, "statement": "Statement 2"}
            ]
        }
        
        summary = assessment_engine.get_edge_assessment_summary("team", "output")
        
        assert summary is not None
        assert summary["edge_type"] == "team_execution"
        assert summary["current_score"] == 3.5
        assert summary["evidence_count"] == 2
        assert "⭐" in summary["score_display"]
    
    def test_get_edge_assessment_summary_nonexistent(self, assessment_engine, mock_graph):
        """Test getting summary for nonexistent edge."""
        mock_graph.get_edge.return_value = None
        
        summary = assessment_engine.get_edge_assessment_summary("team", "output")
        
        assert summary is None
    
    def test_get_assessment_progress_no_edges(self, assessment_engine, mock_graph):
        """Test assessment progress with no edges."""
        mock_graph.get_incoming_edges.return_value = []
        
        progress = assessment_engine.get_assessment_progress("output_1")
        
        assert progress["total_edges"] == 0
        assert progress["assessed_edges"] == 0
        assert progress["completion_percentage"] == 0
    
    def test_get_assessment_progress_partial(self, assessment_engine, mock_graph):
        """Test assessment progress with partial completion."""
        mock_graph.get_incoming_edges.return_value = [
            ("team", "output", {"edge_type": "team_execution", "current_score": 3.0, "current_confidence": 0.7}),
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": None, "current_confidence": 0.0}),
            ("process", "output", {"edge_type": "process_maturity", "current_score": 2.5, "current_confidence": 0.6}),
            ("dep", "output", {"edge_type": "dependency_quality", "current_score": None, "current_confidence": 0.0})
        ]
        
        progress = assessment_engine.get_assessment_progress("output")
        
        assert progress["total_edges"] == 4
        assert progress["assessed_edges"] == 2
        assert progress["completion_percentage"] == 50.0
        assert len(progress["edges"]) == 4
    
    def test_get_assessment_progress_complete(self, assessment_engine, mock_graph):
        """Test assessment progress with all edges assessed."""
        mock_graph.get_incoming_edges.return_value = [
            ("team", "output", {"edge_type": "team_execution", "current_score": 3.0, "current_confidence": 0.7}),
            ("tool", "output", {"edge_type": "system_capabilities", "current_score": 2.0, "current_confidence": 0.8}),
            ("process", "output", {"edge_type": "process_maturity", "current_score": 4.0, "current_confidence": 0.9}),
            ("dep", "output", {"edge_type": "dependency_quality", "current_score": 3.5, "current_confidence": 0.6})
        ]
        
        progress = assessment_engine.get_assessment_progress("output")
        
        assert progress["total_edges"] == 4
        assert progress["assessed_edges"] == 4
        assert progress["completion_percentage"] == 100.0
    
    def test_build_inference_prompt_team_execution(self, assessment_engine):
        """Test prompt building for team execution."""
        prompt = assessment_engine._build_inference_prompt(
            "The team is junior",
            "team_execution",
            {"output_name": "Sales Forecast"}
        )
        
        assert "team" in prompt.lower()
        assert "skills" in prompt.lower()
        assert "Sales Forecast" in prompt
        assert "1-5 stars" in prompt
        assert "Evidence Tiers" in prompt
    
    def test_build_inference_prompt_system_capabilities(self, assessment_engine):
        """Test prompt building for system capabilities."""
        prompt = assessment_engine._build_inference_prompt(
            "The CRM is terrible",
            "system_capabilities",
            {"output_name": "Pipeline Reports"}
        )
        
        assert "system" in prompt.lower() or "tool" in prompt.lower()
        assert "features" in prompt.lower() or "reliability" in prompt.lower()
        assert "Pipeline Reports" in prompt
    
    def test_parse_inference_response_valid(self, assessment_engine):
        """Test parsing valid inference response."""
        response = json.dumps({
            "inferred_score": 4,
            "evidence_tier": 5,
            "reasoning": "User provided quantified example",
            "confidence": 0.95
        })
        
        result = assessment_engine._parse_inference_response(response)
        
        assert result["inferred_score"] == 4
        assert result["evidence_tier"] == 5
        assert result["confidence"] == 0.95
        assert "reasoning" in result
