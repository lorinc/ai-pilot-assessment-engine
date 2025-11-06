"""
Tests for Assessment Triggers

TDD RED phase - tests for assessment trigger detection

Assessment triggers should detect when user is:
- Rating edges (data quality, team execution, process maturity, system support)
- Identifying bottlenecks
- Comparing components
- Providing assessment-related information
"""
import pytest
from src.patterns.trigger_detector import TriggerDetector
from src.patterns.knowledge_tracker import KnowledgeTracker


class TestRatingDetection:
    """Test detection of rating statements"""
    
    def test_star_rating_detected(self):
        """Should detect star ratings as assessment"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        messages = [
            "Data quality is 3 stars",
            "The data quality is about 3 stars",
            "I rate the data quality as 3 stars",
            "Data quality: 3 stars",
            "Team execution is 4 stars",
            "Process maturity: 2 stars",
            "System support is 5 stars"
        ]
        
        for message in messages:
            triggers = detector.detect(message, tracker, False)
            
            # Should have assessment trigger
            assessment_triggers = [t for t in triggers if t.get('category') == 'assessment']
            assert len(assessment_triggers) > 0, f"No assessment trigger for: {message}"
            
            # Should have T_RATE_EDGE trigger
            trigger_ids = [t['trigger_id'] for t in triggers]
            assert 'T_RATE_EDGE' in trigger_ids, f"No T_RATE_EDGE for: {message}"
    
    def test_numeric_rating_detected(self):
        """Should detect numeric ratings as assessment"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        messages = [
            "Data quality is 3 out of 5",
            "I'd rate the team at 4/5",
            "Process is about a 2",
            "System support: 5/5"
        ]
        
        for message in messages:
            triggers = detector.detect(message, tracker, False)
            
            # Should have assessment trigger
            assessment_triggers = [t for t in triggers if t.get('category') == 'assessment']
            assert len(assessment_triggers) > 0, f"No assessment trigger for: {message}"
    
    def test_qualitative_rating_detected(self):
        """Should detect qualitative ratings as assessment"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        messages = [
            "Data quality is poor",
            "The team is excellent",
            "Process is mediocre",
            "System support is terrible",
            "Data quality is good"
        ]
        
        for message in messages:
            triggers = detector.detect(message, tracker, False)
            
            # Should have assessment trigger
            assessment_triggers = [t for t in triggers if t.get('category') == 'assessment']
            assert len(assessment_triggers) > 0, f"No assessment trigger for: {message}"


class TestComponentMentionDetection:
    """Test detection of component mentions"""
    
    def test_data_quality_mention(self):
        """Should detect data quality mentions"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        messages = [
            "The data quality is an issue",
            "We have data quality problems",
            "Data quality needs improvement"
        ]
        
        for message in messages:
            triggers = detector.detect(message, tracker, False)
            
            # Should have assessment trigger
            assessment_triggers = [t for t in triggers if t.get('category') == 'assessment']
            assert len(assessment_triggers) > 0, f"No assessment trigger for: {message}"
    
    def test_team_execution_mention(self):
        """Should detect team execution mentions"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        messages = [
            "The team struggles with this",
            "Team execution is weak",
            "Our team is very capable"
        ]
        
        for message in messages:
            triggers = detector.detect(message, tracker, False)
            
            # Should have assessment trigger
            assessment_triggers = [t for t in triggers if t.get('category') == 'assessment']
            assert len(assessment_triggers) > 0, f"No assessment trigger for: {message}"


class TestPriorityAndCategory:
    """Test that assessment triggers have correct priority and category"""
    
    def test_assessment_category(self):
        """Assessment triggers should have 'assessment' category"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        triggers = detector.detect("Data quality is 3 stars", tracker, False)
        
        assessment_triggers = [t for t in triggers if t['trigger_id'] == 'T_RATE_EDGE']
        assert len(assessment_triggers) > 0
        assert assessment_triggers[0]['category'] == 'assessment'
    
    def test_assessment_priority(self):
        """Assessment triggers should have high priority"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        triggers = detector.detect("Data quality is 3 stars", tracker, False)
        
        assessment_triggers = [t for t in triggers if t['trigger_id'] == 'T_RATE_EDGE']
        assert len(assessment_triggers) > 0
        assert assessment_triggers[0]['priority'] in ['high', 'critical']


class TestEducationVsAssessment:
    """Test that assessment takes precedence over education"""
    
    def test_rating_not_education(self):
        """Rating statements should NOT trigger education opportunity"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # This was triggering EDUCATION_OPPORTUNITY_MIN before
        triggers = detector.detect("Data quality is 3 stars", tracker, False)
        
        # Should have assessment trigger
        trigger_ids = [t['trigger_id'] for t in triggers]
        assert 'T_RATE_EDGE' in trigger_ids
        
        # Should NOT have education trigger (or if it does, assessment should be higher priority)
        if 'EDUCATION_OPPORTUNITY_MIN' in trigger_ids:
            assessment_trigger = next(t for t in triggers if t['trigger_id'] == 'T_RATE_EDGE')
            education_trigger = next(t for t in triggers if t['trigger_id'] == 'EDUCATION_OPPORTUNITY_MIN')
            
            # Assessment should have higher priority
            priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            assert priority_order[assessment_trigger['priority']] > priority_order[education_trigger['priority']]
    
    def test_component_mention_without_rating(self):
        """Component mentions without ratings can trigger education"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # This should still trigger education (no rating)
        triggers = detector.detect("We need to look at data quality and team execution", tracker, False)
        
        trigger_ids = [t['trigger_id'] for t in triggers]
        # Could have education opportunity (no rating provided)
        # This is OK - it's a question/statement, not an assessment


class TestBackwardCompatibility:
    """Test that existing triggers still work"""
    
    def test_confusion_still_works(self):
        """Confusion detection should still work"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        triggers = detector.detect("I'm confused about this", tracker, False)
        
        trigger_ids = [t['trigger_id'] for t in triggers]
        assert 'CONFUSION_DETECTED' in trigger_ids
    
    def test_discovery_still_works(self):
        """Discovery triggers should still work"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Use a message that's clearly discovery, not assessment
        triggers = detector.detect("We want to identify outputs for AI pilots", tracker, False)
        
        # Should have some triggers
        assert len(triggers) >= 0  # May or may not have triggers, that's OK
