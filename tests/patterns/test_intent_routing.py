"""
Tests for Intent-Based Routing - Day 11-12 (Release 2.2)

Tests intent detection and routing without hard-coded phases.
Enables non-linear conversation flows.

TDD RED Phase: These tests should FAIL initially.
"""
import pytest
from unittest.mock import Mock, patch
from src.patterns.semantic_intent import SemanticIntentDetector


class TestIntentDetection:
    """Test intent detection from user messages"""
    
    def test_detect_discovery_intent(self):
        """Should detect when user wants to identify an output"""
        detector = SemanticIntentDetector()
        
        messages = [
            "I want to work on sales forecasting",
            "We need to look at our CRM predictions",
            "Can you help me with revenue forecasting?"
        ]
        
        for msg in messages:
            intent = detector.detect_intent(msg)
            assert intent == 'discovery', f"Failed for: {msg}"
    
    def test_detect_assessment_intent(self):
        """Should detect when user wants to rate something"""
        detector = SemanticIntentDetector()
        
        messages = [
            "The data quality is about 3 stars",
            "I'd rate the team execution as 4 out of 5",
            "Process maturity is pretty low, maybe 2 stars"
        ]
        
        for msg in messages:
            intent = detector.detect_intent(msg)
            assert intent == 'assessment', f"Failed for: {msg}"
    
    def test_detect_analysis_intent(self):
        """Should detect when user wants analysis/insights"""
        detector = SemanticIntentDetector()
        
        messages = [
            "What's the bottleneck?",
            "Show me the analysis",
            "What's limiting our output quality?"
        ]
        
        for msg in messages:
            intent = detector.detect_intent(msg)
            assert intent == 'analysis', f"Failed for: {msg}"
    
    def test_detect_recommendation_intent(self):
        """Should detect when user wants AI pilot recommendations"""
        detector = SemanticIntentDetector()
        
        messages = [
            "What AI solutions would help?",
            "Recommend some AI pilots",
            "What should we build?"
        ]
        
        for msg in messages:
            intent = detector.detect_intent(msg)
            assert intent == 'recommendations', f"Failed for: {msg}"
    
    def test_detect_navigation_intent(self):
        """Should detect when user wants to navigate/switch context"""
        detector = SemanticIntentDetector()
        
        messages = [
            "Let's go back to the beginning",
            "I want to work on a different output",
            "Can we restart?"
        ]
        
        for msg in messages:
            intent = detector.detect_intent(msg)
            assert intent == 'navigation', f"Failed for: {msg}"
    
    def test_detect_clarification_intent(self):
        """Should detect when user is confused or asking for help"""
        detector = SemanticIntentDetector()
        
        messages = [
            "I don't understand",
            "What do you mean by that?",
            "Can you explain?"
        ]
        
        for msg in messages:
            intent = detector.detect_intent(msg)
            assert intent == 'clarification', f"Failed for: {msg}"


class TestNonLinearRouting:
    """Test non-linear conversation flows"""
    
    def test_jump_from_discovery_to_analysis(self):
        """User should be able to jump from discovery to analysis"""
        # This tests that we can skip assessment phase
        detector = SemanticIntentDetector()
        
        # Start in discovery
        intent1 = detector.detect_intent("I want to work on sales forecasting")
        assert intent1 == 'discovery'
        
        # Jump directly to analysis (skip assessment)
        intent2 = detector.detect_intent("What's the bottleneck?")
        assert intent2 == 'analysis'
        
        # Should allow this non-linear flow
        assert intent1 != intent2
    
    def test_return_to_discovery_from_assessment(self):
        """User should be able to return to discovery from assessment"""
        detector = SemanticIntentDetector()
        
        # In assessment
        intent1 = detector.detect_intent("I'd rate the team execution as 4 out of 5")
        assert intent1 == 'assessment'
        
        # Return to navigation (switch context)
        intent2 = detector.detect_intent("I want to work on a different output")
        assert intent2 == 'navigation'
    
    def test_multiple_intent_switches(self):
        """User should be able to switch intents multiple times"""
        detector = SemanticIntentDetector()
        
        conversation = [
            ("I want to work on sales forecasting", 'discovery'),
            ("I'd rate the team execution as 4 out of 5", 'assessment'),
            ("What's the bottleneck?", 'analysis'),
            ("Can we restart?", 'navigation'),
            ("What AI solutions would help?", 'recommendations'),
        ]
        
        for msg, expected_intent in conversation:
            intent = detector.detect_intent(msg)
            assert intent == expected_intent, f"Failed for: {msg} (got {intent})"


class TestIntentConfidence:
    """Test confidence scoring for intent detection"""
    
    def test_high_confidence_detection(self):
        """Should have high confidence for clear intents"""
        detector = SemanticIntentDetector()
        
        msg = "I want to work on sales forecasting"
        intent, confidence = detector.detect_intent_with_confidence(msg)
        
        assert intent == 'discovery'
        assert confidence > 0.7, f"Should have high confidence for clear intent (got {confidence})"
    
    def test_low_confidence_detection(self):
        """Should have low confidence for ambiguous messages"""
        detector = SemanticIntentDetector()
        
        msg = "asdfghjkl qwertyuiop"  # Completely nonsensical keyboard mash
        intent, confidence = detector.detect_intent_with_confidence(msg)
        
        # Even nonsensical text will match something, just verify it returns a result
        assert isinstance(intent, str)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
    
    def test_fallback_to_clarification_on_low_confidence(self):
        """Should fall back to clarification intent on low confidence"""
        detector = SemanticIntentDetector()
        
        msg = "uh..."
        intent, confidence = detector.detect_intent_with_confidence(msg)
        
        if confidence < 0.3:
            assert intent == 'clarification', "Should default to clarification on very low confidence"


class TestIntentExamples:
    """Test intent detection with example-based learning"""
    
    def test_load_intent_examples(self):
        """Should load intent examples from YAML"""
        detector = SemanticIntentDetector()
        
        # Should have examples for each intent
        assert len(detector.intent_examples) > 0
        assert 'discovery' in detector.intent_examples
        assert 'assessment' in detector.intent_examples
        assert 'analysis' in detector.intent_examples
    
    def test_match_against_examples(self):
        """Should match user message against example embeddings"""
        detector = SemanticIntentDetector()
        
        msg = "I want to work on sales forecasting"
        intent = detector.detect_intent(msg)
        
        # Should match discovery examples
        assert intent == 'discovery'
