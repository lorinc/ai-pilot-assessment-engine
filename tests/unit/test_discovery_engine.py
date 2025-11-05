"""Unit tests for OutputDiscoveryEngine."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

from engines.discovery import OutputDiscoveryEngine


class TestOutputDiscoveryEngine:
    """Test OutputDiscoveryEngine."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM client."""
        llm = Mock()
        llm.generate_text = AsyncMock()
        return llm
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()
    
    @pytest.fixture
    def discovery_engine(self, mock_llm, mock_logger):
        """Create OutputDiscoveryEngine instance."""
        return OutputDiscoveryEngine(
            llm_client=mock_llm,
            data_dir="src/data",
            logger=mock_logger
        )
    
    def test_load_output_catalog(self, discovery_engine):
        """Test that output catalog loads successfully."""
        assert len(discovery_engine.output_catalog) > 0
        assert "sales_forecast" in discovery_engine.output_catalog
        
        # Check structure of loaded output
        sales_forecast = discovery_engine.output_catalog["sales_forecast"]
        assert "name" in sales_forecast
        assert "description" in sales_forecast
        assert "function" in sales_forecast
        assert sales_forecast["function"] == "Sales"
    
    def test_get_output_details(self, discovery_engine):
        """Test getting output details."""
        output = discovery_engine.get_output_details("sales_forecast")
        
        assert output is not None
        assert output["name"] == "Sales Forecast"
        assert "description" in output
        assert "typical_creation_context" in output
    
    def test_get_nonexistent_output(self, discovery_engine):
        """Test getting nonexistent output."""
        output = discovery_engine.get_output_details("nonexistent_output")
        assert output is None
    
    def test_infer_creation_context(self, discovery_engine):
        """Test inferring creation context."""
        context = discovery_engine.infer_creation_context("sales_forecast")
        
        assert "team" in context
        assert "process" in context
        assert "system" in context
        
        assert context["team"]["name"] == "Sales Operations Team"
        assert context["process"]["name"] == "Sales Forecasting Process"
        assert "CRM" in context["system"]["name"] or "Spreadsheet" in context["system"]["name"]
    
    def test_infer_team_archetype(self, discovery_engine):
        """Test team archetype inference."""
        assert discovery_engine._infer_team_archetype("Sales Operations Team") == "Operations"
        assert discovery_engine._infer_team_archetype("Sales Development Team") == "Development"
        assert discovery_engine._infer_team_archetype("Account Executive Team") == "Execution"
        assert discovery_engine._infer_team_archetype("Sales Leadership") == "Leadership"
    
    def test_infer_system_category(self, discovery_engine):
        """Test system category inference."""
        assert discovery_engine._infer_system_category("CRM") == "CRM"
        assert discovery_engine._infer_system_category("Salesforce") == "CRM"
        assert discovery_engine._infer_system_category("Excel") == "Spreadsheet"
        assert discovery_engine._infer_system_category("Google Sheets") == "Spreadsheet"
        assert discovery_engine._infer_system_category("Tableau") == "Business Intelligence"
    
    @pytest.mark.asyncio
    async def test_discover_output_success(self, discovery_engine, mock_llm):
        """Test successful output discovery."""
        # Mock LLM response
        mock_response = json.dumps({
            "extracted_features": {
                "keywords": ["forecast", "sales"],
                "pain_points": ["inaccurate"],
                "systems": ["CRM"],
                "function": "Sales"
            },
            "candidates": [
                {
                    "output_id": "sales_forecast",
                    "confidence": 0.9,
                    "reasoning": "User mentioned sales forecasts being inaccurate"
                }
            ]
        })
        mock_llm.generate_text.return_value = mock_response
        
        # Discover output
        candidates = await discovery_engine.discover_output("Sales forecasts are always wrong")
        
        assert len(candidates) > 0
        assert candidates[0]["id"] == "sales_forecast"
        assert candidates[0]["confidence"] == 0.9
        assert "reasoning" in candidates[0]
    
    @pytest.mark.asyncio
    async def test_discover_output_multiple_candidates(self, discovery_engine, mock_llm):
        """Test discovery with multiple candidates."""
        # Mock LLM response with multiple candidates
        mock_response = json.dumps({
            "extracted_features": {
                "keywords": ["pipeline", "reports"],
                "pain_points": ["stale", "incomplete"],
                "systems": ["CRM"],
                "function": "Sales"
            },
            "candidates": [
                {
                    "output_id": "pipeline_reports",
                    "confidence": 0.85,
                    "reasoning": "User mentioned pipeline reports"
                },
                {
                    "output_id": "sales_forecast",
                    "confidence": 0.6,
                    "reasoning": "Related to sales reporting"
                }
            ]
        })
        mock_llm.generate_text.return_value = mock_response
        
        # Discover output
        candidates = await discovery_engine.discover_output("Pipeline reports are stale")
        
        assert len(candidates) == 2
        # Should be sorted by confidence
        assert candidates[0]["confidence"] >= candidates[1]["confidence"]
    
    @pytest.mark.asyncio
    async def test_discover_output_invalid_json(self, discovery_engine, mock_llm):
        """Test handling of invalid JSON response."""
        # Mock invalid JSON response
        mock_llm.generate_text.return_value = "This is not valid JSON"
        
        # Should return empty list
        candidates = await discovery_engine.discover_output("Some problem")
        
        assert len(candidates) == 0
    
    @pytest.mark.asyncio
    async def test_discover_output_unknown_output_id(self, discovery_engine, mock_llm):
        """Test handling of unknown output ID in response."""
        # Mock response with unknown output ID
        mock_response = json.dumps({
            "extracted_features": {
                "keywords": ["test"],
                "pain_points": [],
                "systems": [],
                "function": "Unknown"
            },
            "candidates": [
                {
                    "output_id": "nonexistent_output",
                    "confidence": 0.9,
                    "reasoning": "Test"
                }
            ]
        })
        mock_llm.generate_text.return_value = mock_response
        
        # Should filter out unknown outputs
        candidates = await discovery_engine.discover_output("Some problem")
        
        assert len(candidates) == 0
    
    def test_build_catalog_summary(self, discovery_engine):
        """Test catalog summary building."""
        summary = discovery_engine._build_catalog_summary()
        
        assert len(summary) > 0
        assert "sales_forecast" in summary.lower()
        assert "Sales Forecast" in summary
    
    def test_get_catalog_stats(self, discovery_engine):
        """Test catalog statistics."""
        stats = discovery_engine.get_catalog_stats()
        
        assert "total_outputs" in stats
        assert stats["total_outputs"] > 0
        assert "outputs_by_function" in stats
        assert "outputs_by_team_type" in stats
        
        # Should have Sales outputs
        assert "Sales" in stats["outputs_by_function"]
        assert stats["outputs_by_function"]["Sales"] > 0
    
    def test_parse_discovery_response_sorts_by_confidence(self, discovery_engine):
        """Test that candidates are sorted by confidence."""
        response = json.dumps({
            "candidates": [
                {"output_id": "sales_forecast", "confidence": 0.6, "reasoning": "Low"},
                {"output_id": "pipeline_reports", "confidence": 0.9, "reasoning": "High"},
                {"output_id": "qualified_leads", "confidence": 0.75, "reasoning": "Medium"}
            ]
        })
        
        candidates = discovery_engine._parse_discovery_response(response)
        
        # Should be sorted descending by confidence
        assert len(candidates) == 3
        assert candidates[0]["confidence"] == 0.9
        assert candidates[1]["confidence"] == 0.75
        assert candidates[2]["confidence"] == 0.6
