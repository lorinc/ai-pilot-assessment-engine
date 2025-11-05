"""Unit tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from models.data_models import (
    Output,
    CreationContext,
    ComponentRating,
    ComponentAssessment,
    QualityAssessment,
    PilotRecommendation,
    AssessmentSession
)


class TestOutput:
    """Test suite for Output model."""
    
    def test_valid_output(self):
        """Test creating valid output."""
        output = Output(
            id="sales_forecast",
            name="Sales Forecast",
            function="Sales",
            description="Monthly sales predictions"
        )
        
        assert output.id == "sales_forecast"
        assert output.name == "Sales Forecast"
        assert output.function == "Sales"
        assert output.description == "Monthly sales predictions"
    
    def test_output_without_description(self):
        """Test output without optional description."""
        output = Output(
            id="sales_forecast",
            name="Sales Forecast",
            function="Sales"
        )
        
        assert output.description is None
    
    def test_output_missing_required_fields(self):
        """Test validation error when required fields missing."""
        with pytest.raises(ValidationError):
            Output(id="sales_forecast")


class TestCreationContext:
    """Test suite for CreationContext model."""
    
    def test_valid_context(self):
        """Test creating valid creation context."""
        context = CreationContext(
            team="Sales Operations",
            process="Sales Forecasting Process",
            step="Forecast Generation",
            system="Salesforce CRM",
            confidence=0.85
        )
        
        assert context.team == "Sales Operations"
        assert context.process == "Sales Forecasting Process"
        assert context.step == "Forecast Generation"
        assert context.system == "Salesforce CRM"
        assert context.confidence == 0.85
    
    def test_context_without_step(self):
        """Test context without optional step."""
        context = CreationContext(
            team="Sales Operations",
            process="Sales Forecasting Process",
            system="Salesforce CRM",
            confidence=0.85
        )
        
        assert context.step is None
    
    def test_context_default_confidence(self):
        """Test default confidence value."""
        context = CreationContext(
            team="Sales Operations",
            process="Sales Forecasting Process",
            system="Salesforce CRM"
        )
        
        assert context.confidence == 0.0
    
    def test_context_confidence_validation(self):
        """Test confidence must be between 0 and 1."""
        with pytest.raises(ValidationError):
            CreationContext(
                team="Sales Operations",
                process="Sales Forecasting Process",
                system="Salesforce CRM",
                confidence=1.5
            )


class TestComponentRating:
    """Test suite for ComponentRating model."""
    
    def test_valid_rating(self):
        """Test creating valid component rating."""
        rating = ComponentRating(
            rating=2,
            description="Junior team, learning on the job",
            confidence=0.80,
            indicators_matched=["Limited experience", "No formal training"]
        )
        
        assert rating.rating == 2
        assert rating.description == "Junior team, learning on the job"
        assert rating.confidence == 0.80
        assert len(rating.indicators_matched) == 2
    
    def test_rating_bounds(self):
        """Test rating must be between 1 and 5."""
        with pytest.raises(ValidationError):
            ComponentRating(rating=0, description="Test", confidence=0.5)
        
        with pytest.raises(ValidationError):
            ComponentRating(rating=6, description="Test", confidence=0.5)
    
    def test_rating_default_indicators(self):
        """Test default empty indicators list."""
        rating = ComponentRating(
            rating=3,
            description="Test",
            confidence=0.5
        )
        
        assert rating.indicators_matched == []


class TestComponentAssessment:
    """Test suite for ComponentAssessment model."""
    
    def test_empty_assessment(self):
        """Test creating empty assessment."""
        assessment = ComponentAssessment()
        
        assert assessment.team_execution is None
        assert assessment.system_capabilities is None
        assert assessment.process_maturity is None
        assert assessment.dependency_quality is None
        assert not assessment.is_complete()
    
    def test_partial_assessment(self):
        """Test partially complete assessment."""
        assessment = ComponentAssessment(
            team_execution=ComponentRating(rating=2, description="Test", confidence=0.8)
        )
        
        assert assessment.team_execution is not None
        assert not assessment.is_complete()
    
    def test_complete_assessment(self):
        """Test fully complete assessment."""
        assessment = ComponentAssessment(
            team_execution=ComponentRating(rating=2, description="Test", confidence=0.8),
            system_capabilities=ComponentRating(rating=2, description="Test", confidence=0.8),
            process_maturity=ComponentRating(rating=3, description="Test", confidence=0.8),
            dependency_quality=ComponentRating(rating=3, description="Test", confidence=0.8)
        )
        
        assert assessment.is_complete()
    
    def test_get_ratings(self):
        """Test getting ratings dictionary."""
        assessment = ComponentAssessment(
            team_execution=ComponentRating(rating=2, description="Test", confidence=0.8),
            system_capabilities=ComponentRating(rating=3, description="Test", confidence=0.8)
        )
        
        ratings = assessment.get_ratings()
        
        assert ratings["team_execution"] == 2
        assert ratings["system_capabilities"] == 3
        assert ratings["process_maturity"] == 0  # Not set
        assert ratings["dependency_quality"] == 0  # Not set


class TestQualityAssessment:
    """Test suite for QualityAssessment model."""
    
    def test_valid_quality_assessment(self):
        """Test creating valid quality assessment."""
        assessment = QualityAssessment(
            actual_quality=2,
            required_quality=4,
            gap=2,
            bottleneck=["team_execution", "system_capabilities"],
            calculation="MIN(2, 2, 3, 3) = 2"
        )
        
        assert assessment.actual_quality == 2
        assert assessment.required_quality == 4
        assert assessment.gap == 2
        assert len(assessment.bottleneck) == 2
        assert "MIN" in assessment.calculation


class TestPilotRecommendation:
    """Test suite for PilotRecommendation model."""
    
    def test_valid_recommendation(self):
        """Test creating valid pilot recommendation."""
        pilot = PilotRecommendation(
            name="AI Copilot for Sales Forecasting",
            category="team_execution",
            description="AI assistant that helps team",
            expected_impact="⭐⭐ → ⭐⭐⭐⭐",
            timeline="8-12 weeks",
            cost="€20k-€40k",
            prerequisites=["Team willing to adopt", "Data access"]
        )
        
        assert pilot.name == "AI Copilot for Sales Forecasting"
        assert pilot.category == "team_execution"
        assert len(pilot.prerequisites) == 2
    
    def test_recommendation_default_prerequisites(self):
        """Test default empty prerequisites list."""
        pilot = PilotRecommendation(
            name="Test Pilot",
            category="team_execution",
            description="Test",
            expected_impact="Test",
            timeline="Test",
            cost="Test"
        )
        
        assert pilot.prerequisites == []


class TestAssessmentSession:
    """Test suite for AssessmentSession model."""
    
    def test_new_session(self):
        """Test creating new assessment session."""
        session = AssessmentSession(
            session_id="sess_123",
            created_at="2025-11-02T19:00:00Z"
        )
        
        assert session.session_id == "sess_123"
        assert session.status == "in_progress"
        assert session.output is None
        assert session.context is None
        assert len(session.messages) == 0
    
    def test_session_with_output(self):
        """Test session with output."""
        output = Output(
            id="sales_forecast",
            name="Sales Forecast",
            function="Sales"
        )
        
        session = AssessmentSession(
            session_id="sess_123",
            created_at="2025-11-02T19:00:00Z",
            output=output
        )
        
        assert session.output is not None
        assert session.output.id == "sales_forecast"
    
    def test_session_with_messages(self):
        """Test session with conversation history."""
        session = AssessmentSession(
            session_id="sess_123",
            created_at="2025-11-02T19:00:00Z",
            messages=[
                {"role": "user", "content": "Test message"},
                {"role": "assistant", "content": "Test response"}
            ]
        )
        
        assert len(session.messages) == 2
        assert session.messages[0]["role"] == "user"
        assert session.messages[1]["role"] == "assistant"
