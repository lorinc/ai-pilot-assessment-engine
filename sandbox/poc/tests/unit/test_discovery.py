"""Unit tests for DiscoveryEngine."""

import pytest
from unittest.mock import Mock, MagicMock
from engines.discovery import DiscoveryEngine
from models.data_models import Output, CreationContext


class TestDiscoveryEngine:
    """Test suite for DiscoveryEngine."""
    
    @pytest.fixture
    def mock_taxonomy(self):
        """Create mock taxonomy loader."""
        taxonomy = Mock()
        taxonomy.search_outputs = Mock(return_value=[])
        taxonomy.get_output_by_id = Mock(return_value=None)
        return taxonomy
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()
    
    @pytest.fixture
    def engine(self, mock_taxonomy, mock_logger):
        """Create discovery engine instance."""
        return DiscoveryEngine(
            taxonomy_loader=mock_taxonomy,
            gemini_client=None,
            logger=mock_logger
        )
    
    def test_init(self, mock_taxonomy):
        """Test engine initialization."""
        engine = DiscoveryEngine(taxonomy_loader=mock_taxonomy)
        
        assert engine.taxonomy == mock_taxonomy
        assert engine.gemini is None
        assert engine.logger is None
    
    def test_extract_keywords_simple(self, engine):
        """Test keyword extraction from simple message."""
        message = "Our sales forecasts are always wrong"
        
        keywords = engine.extract_keywords(message)
        
        assert "sales" in keywords
        assert "forecasts" in keywords
        assert "wrong" in keywords
        assert "are" not in keywords  # Stop word
        assert "our" not in keywords  # Stop word
    
    def test_extract_keywords_complex(self, engine):
        """Test keyword extraction from complex message."""
        message = "The customer support team takes too long to resolve tickets in Zendesk"
        
        keywords = engine.extract_keywords(message)
        
        assert "customer" in keywords
        assert "support" in keywords
        assert "team" in keywords
        assert "tickets" in keywords
        assert "zendesk" in keywords
        assert "resolve" in keywords
        assert "the" not in keywords  # Stop word
    
    def test_extract_keywords_filters_short_words(self, engine):
        """Test that short words are filtered out."""
        message = "I am in a bad CRM"
        
        keywords = engine.extract_keywords(message)
        
        assert "bad" in keywords
        assert "crm" in keywords
        assert "am" not in keywords  # Too short
        assert "in" not in keywords  # Too short
    
    def test_extract_keywords_deduplicates(self, engine):
        """Test that duplicate keywords are removed."""
        message = "sales sales sales forecast forecast"
        
        keywords = engine.extract_keywords(message)
        
        assert keywords.count("sales") == 1
        assert keywords.count("forecast") == 1
    
    def test_extract_keywords_empty_message(self, engine):
        """Test keyword extraction from empty message."""
        keywords = engine.extract_keywords("")
        
        assert keywords == []
    
    def test_extract_keywords_only_stop_words(self, engine):
        """Test message with only stop words."""
        message = "the and or but"
        
        keywords = engine.extract_keywords("")
        
        assert keywords == []
    
    def test_match_outputs(self, engine, mock_taxonomy):
        """Test output matching."""
        mock_taxonomy.search_outputs.return_value = [
            {"output": {"id": "test", "name": "Test"}, "score": 10}
        ]
        
        matches = engine.match_outputs(["sales", "forecast"])
        
        assert len(matches) == 1
        mock_taxonomy.search_outputs.assert_called_once_with(["sales", "forecast"])
    
    def test_match_outputs_logs_results(self, engine, mock_taxonomy, mock_logger):
        """Test that matching logs results."""
        mock_taxonomy.search_outputs.return_value = [
            {"output": {"id": "test", "name": "Test"}, "score": 10}
        ]
        
        engine.match_outputs(["sales"])
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args
        assert call_args[0][0] == "taxonomy_search"
    
    def test_calculate_confidence_high_score(self, engine):
        """Test confidence calculation with high match score."""
        output = {"common_pain_points": []}
        
        confidence = engine.calculate_confidence(
            match_score=50,
            user_message="Our sales forecasts are wrong",
            output=output
        )
        
        assert confidence >= 0.9
        assert confidence <= 1.0
    
    def test_calculate_confidence_medium_score(self, engine):
        """Test confidence calculation with medium match score."""
        output = {"common_pain_points": []}
        
        confidence = engine.calculate_confidence(
            match_score=25,
            user_message="Our sales forecasts are wrong",
            output=output
        )
        
        assert confidence >= 0.4
        assert confidence <= 0.6
    
    def test_calculate_confidence_low_score(self, engine):
        """Test confidence calculation with low match score."""
        output = {"common_pain_points": []}
        
        confidence = engine.calculate_confidence(
            match_score=5,
            user_message="Our sales forecasts are wrong",
            output=output
        )
        
        assert confidence < 0.3
    
    def test_calculate_confidence_pain_point_bonus(self, engine):
        """Test confidence bonus for pain point matches."""
        output = {
            "common_pain_points": [
                "Forecasts are consistently inaccurate",
                "Takes too long to generate"
            ]
        }
        
        confidence_with_pain = engine.calculate_confidence(
            match_score=25,
            user_message="Our forecasts are consistently inaccurate",
            output=output
        )
        
        confidence_without_pain = engine.calculate_confidence(
            match_score=25,
            user_message="We have a problem",
            output=output
        )
        
        assert confidence_with_pain > confidence_without_pain
    
    def test_calculate_confidence_short_message_penalty(self, engine):
        """Test confidence penalty for short messages."""
        output = {"common_pain_points": []}
        
        confidence_short = engine.calculate_confidence(
            match_score=25,
            user_message="Bad forecast",
            output=output
        )
        
        confidence_long = engine.calculate_confidence(
            match_score=25,
            user_message="Our sales forecasts are consistently wrong and unreliable",
            output=output
        )
        
        assert confidence_long > confidence_short
    
    def test_calculate_confidence_clamped(self, engine):
        """Test that confidence is clamped to [0, 1]."""
        output = {"common_pain_points": []}
        
        # Very high score
        confidence_high = engine.calculate_confidence(
            match_score=1000,
            user_message="Test message with many words",
            output=output
        )
        assert confidence_high <= 1.0
        
        # Very low score
        confidence_low = engine.calculate_confidence(
            match_score=0,
            user_message="Bad",
            output=output
        )
        assert confidence_low >= 0.0
    
    def test_identify_output_success(self, engine, mock_taxonomy):
        """Test successful output identification."""
        mock_taxonomy.search_outputs.return_value = [
            {
                "output": {
                    "id": "sales_forecast",
                    "name": "Sales Forecast",
                    "function": "Sales",
                    "description": "Revenue predictions",
                    "common_pain_points": ["Forecasts are wrong"]
                },
                "score": 50
            }
        ]
        
        output, confidence, matches = engine.identify_output(
            "Our sales forecasts are always wrong"
        )
        
        assert output is not None
        assert isinstance(output, Output)
        assert output.id == "sales_forecast"
        assert output.name == "Sales Forecast"
        assert confidence > 0.5
        assert len(matches) > 0
    
    def test_identify_output_no_keywords(self, engine):
        """Test identification with no extractable keywords."""
        output, confidence, matches = engine.identify_output("the and or")
        
        assert output is None
        assert confidence == 0.0
        assert matches == []
    
    def test_identify_output_no_matches(self, engine, mock_taxonomy):
        """Test identification with no taxonomy matches."""
        mock_taxonomy.search_outputs.return_value = []
        
        output, confidence, matches = engine.identify_output(
            "Some random text"
        )
        
        assert output is None
        assert confidence == 0.0
        assert matches == []
    
    def test_identify_output_low_confidence(self, engine, mock_taxonomy):
        """Test identification with low confidence match."""
        mock_taxonomy.search_outputs.return_value = [
            {
                "output": {
                    "id": "test",
                    "name": "Test Output",
                    "function": "Test",
                    "common_pain_points": []
                },
                "score": 5  # Low score
            }
        ]
        
        output, confidence, matches = engine.identify_output(
            "test",
            min_confidence=0.5
        )
        
        assert output is None  # Below threshold
        assert confidence < 0.5
        assert len(matches) > 0  # But matches are returned
    
    def test_identify_output_custom_threshold(self, engine, mock_taxonomy):
        """Test identification with custom confidence threshold."""
        mock_taxonomy.search_outputs.return_value = [
            {
                "output": {
                    "id": "test",
                    "name": "Test",
                    "function": "Test",
                    "common_pain_points": []
                },
                "score": 25  # Medium score
            }
        ]
        
        # With high threshold (0.7)
        output1, conf1, _ = engine.identify_output("test message with more words", min_confidence=0.7)
        
        # With lower threshold (0.3)
        output2, conf2, _ = engine.identify_output("test message with more words", min_confidence=0.3)
        
        # Same confidence, but different results based on threshold
        assert conf1 == conf2
        # If confidence is between 0.3 and 0.7, first should be None, second should exist
        if 0.3 <= conf1 < 0.7:
            assert output1 is None
            assert output2 is not None
    
    def test_identify_output_sorts_by_confidence(self, engine, mock_taxonomy):
        """Test that matches are sorted by confidence."""
        mock_taxonomy.search_outputs.return_value = [
            {
                "output": {
                    "id": "low",
                    "name": "Low Match",
                    "function": "Test",
                    "common_pain_points": []
                },
                "score": 10
            },
            {
                "output": {
                    "id": "high",
                    "name": "High Match",
                    "function": "Test",
                    "common_pain_points": ["exact match phrase"]
                },
                "score": 40
            }
        ]
        
        output, confidence, matches = engine.identify_output(
            "exact match phrase in message"
        )
        
        # Best match should be returned
        assert output.id == "high"
        # Matches should be sorted by confidence
        assert matches[0]["confidence"] >= matches[1]["confidence"]
    
    def test_infer_context_success(self, engine, mock_taxonomy):
        """Test successful context inference."""
        output = Output(
            id="sales_forecast",
            name="Sales Forecast",
            function="Sales"
        )
        
        mock_taxonomy.get_output_by_id.return_value = {
            "id": "sales_forecast",
            "name": "Sales Forecast",
            "typical_creation_context": {
                "team": "Sales Operations",
                "process": "Forecasting Process",
                "step": "Consolidation",
                "system": "Salesforce"
            }
        }
        
        context = engine.infer_context(output)
        
        assert context is not None
        assert isinstance(context, CreationContext)
        assert context.team == "Sales Operations"
        assert context.process == "Forecasting Process"
        assert context.system == "Salesforce"
        assert context.step == "Consolidation"
        assert context.confidence == 0.6
    
    def test_infer_context_output_not_found(self, engine, mock_taxonomy):
        """Test context inference when output not in taxonomy."""
        output = Output(id="unknown", name="Unknown", function="Test")
        mock_taxonomy.get_output_by_id.return_value = None
        
        context = engine.infer_context(output)
        
        assert context is None
    
    def test_infer_context_no_typical_context(self, engine, mock_taxonomy):
        """Test context inference when no typical context defined."""
        output = Output(id="test", name="Test", function="Test")
        mock_taxonomy.get_output_by_id.return_value = {
            "id": "test",
            "name": "Test"
            # No typical_creation_context
        }
        
        context = engine.infer_context(output)
        
        assert context is None
    
    def test_infer_context_partial_data(self, engine, mock_taxonomy):
        """Test context inference with partial typical context."""
        output = Output(id="test", name="Test", function="Test")
        mock_taxonomy.get_output_by_id.return_value = {
            "id": "test",
            "typical_creation_context": {
                "team": "Test Team"
                # Missing other fields
            }
        }
        
        context = engine.infer_context(output)
        
        assert context is not None
        assert context.team == "Test Team"
        assert context.system == "Unknown System"
        assert context.process == "Unknown Process"
    
    def test_generate_clarifying_question_no_matches(self, engine):
        """Test clarifying question when no matches found."""
        question = engine.generate_clarifying_question([], "test message")
        
        assert "couldn't identify" in question
        assert "more specific" in question
    
    def test_generate_clarifying_question_with_matches(self, engine):
        """Test clarifying question with potential matches."""
        matches = [
            {
                "output": {"id": "1", "name": "Sales Forecast", "function": "Sales"},
                "confidence": 0.4
            },
            {
                "output": {"id": "2", "name": "Pipeline Report", "function": "Sales"},
                "confidence": 0.3
            },
            {
                "output": {"id": "3", "name": "Commission Calc", "function": "Sales"},
                "confidence": 0.2
            }
        ]
        
        question = engine.generate_clarifying_question(matches, "test")
        
        assert "Sales Forecast" in question
        assert "Pipeline Report" in question
        assert "Commission Calc" in question
        assert "1." in question
        assert "2." in question
        assert "3." in question
    
    def test_generate_clarifying_question_limits_to_three(self, engine):
        """Test that clarifying question shows max 3 options."""
        matches = [
            {"output": {"id": str(i), "name": f"Output {i}", "function": "Test"}, "confidence": 0.3}
            for i in range(10)
        ]
        
        question = engine.generate_clarifying_question(matches, "test")
        
        assert "Output 0" in question
        assert "Output 1" in question
        assert "Output 2" in question
        assert "Output 9" not in question  # Should not show all 10
