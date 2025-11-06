"""
Tests for trigger detector (TDD - Red Phase)
"""
import pytest
from src.patterns.trigger_detector import TriggerDetector
from src.patterns.knowledge_tracker import KnowledgeTracker


class TestTriggerDetectorInitialization:
    """Test trigger detector initialization"""
    
    def test_initialization(self):
        """Test trigger detector can be initialized"""
        detector = TriggerDetector()
        assert detector is not None
    
    def test_initialization_with_triggers(self, sample_triggers):
        """Test initialization with trigger definitions"""
        detector = TriggerDetector(sample_triggers)
        assert detector is not None


class TestUserExplicitTriggers:
    """Test detection of user-explicit triggers"""
    
    def test_detect_navigation_query(self):
        """Test detecting 'where are we' navigation queries"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        message = "Where are we in the process?"
        triggers = detector.detect(message, tracker)
        
        # Should detect user-explicit navigation trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'user_explicit' for t in triggers)
        assert any('navigation' in t.get('category', '').lower() for t in triggers)
    
    def test_detect_help_request(self):
        """Test detecting help/explanation requests"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        message = "Can you explain what MIN calculation means?"
        triggers = detector.detect(message, tracker)
        
        # Should detect user-explicit education trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'user_explicit' for t in triggers)
    
    def test_detect_review_request(self):
        """Test detecting review/summary requests"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        message = "Can you show me what we've covered so far?"
        triggers = detector.detect(message, tracker)
        
        # Should detect user-explicit meta trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'user_explicit' for t in triggers)
    
    def test_no_trigger_on_normal_response(self):
        """Test that normal responses don't trigger false positives"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        message = "The sales forecast quality is medium"
        triggers = detector.detect(message, tracker)
        
        # May have triggers, but shouldn't be navigation/help
        # (could be implicit triggers based on content)
        pass  # This is more of a sanity check


class TestUserImplicitTriggers:
    """Test detection of user-implicit triggers"""
    
    def test_detect_confusion(self):
        """Test detecting confusion signals"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        message = "I'm not sure I understand what you mean"
        triggers = detector.detect(message, tracker)
        
        # Should detect user-implicit confusion trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'user_implicit' for t in triggers)
        assert any('confusion' in str(t).lower() for t in triggers)
    
    def test_detect_contradiction(self):
        """Test detecting contradictions"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Set up context with previous statement
        tracker.update_system_knowledge({
            'outputs_identified': ['sales_forecast']
        })
        
        message = "Actually, we don't have a sales forecast output"
        triggers = detector.detect(message, tracker)
        
        # Should detect user-implicit contradiction trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'user_implicit' for t in triggers)
    
    def test_detect_scope_ambiguity(self):
        """Test detecting scope ambiguity"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        message = "We need better data quality everywhere"
        triggers = detector.detect(message, tracker)
        
        # Should detect user-implicit scope ambiguity trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'user_implicit' for t in triggers)


class TestSystemProactiveTriggers:
    """Test detection of system-proactive triggers"""
    
    def test_detect_natural_extraction_opportunity(self):
        """Test detecting opportunities to extract context naturally"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # User mentions timeline without being asked
        message = "We need this done by end of Q2"
        triggers = detector.detect(message, tracker)
        
        # Should detect system-proactive context extraction trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'system_proactive' for t in triggers)
    
    def test_detect_education_opportunity(self):
        """Test detecting opportunities to educate"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # User hasn't learned about MIN calculation yet
        tracker.update_user_knowledge({'understands_min_calculation': False})
        
        # User mentions components
        message = "The team is good but the data quality is poor"
        triggers = detector.detect(message, tracker)
        
        # Should detect system-proactive education opportunity
        assert len(triggers) > 0
        assert any(t['type'] == 'system_proactive' for t in triggers)
    
    def test_detect_recommendation_opportunity(self):
        """Test detecting opportunities to recommend"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # User has identified bottleneck
        tracker.update_system_knowledge({
            'bottlenecks_identified': {'output_1': ['data_quality']}
        })
        
        message = "So what should we do about the data quality issue?"
        triggers = detector.detect(message, tracker)
        
        # Should detect system-proactive recommendation opportunity
        assert len(triggers) > 0
        assert any(t['type'] == 'system_proactive' for t in triggers)


class TestSystemReactiveTriggers:
    """Test detection of system-reactive triggers"""
    
    def test_detect_first_message(self):
        """Test detecting first message in conversation"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # First message indicator
        message = "Hello"
        triggers = detector.detect(message, tracker, is_first_message=True)
        
        # Should detect system-reactive onboarding trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'system_reactive' for t in triggers)
        assert any('onboarding' in t.get('category', '').lower() for t in triggers)
    
    def test_detect_milestone_reached(self):
        """Test detecting milestone completion"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # User has identified 3 outputs
        tracker.update_system_knowledge({
            'outputs_identified': ['output_1', 'output_2', 'output_3']
        })
        
        message = "That's all the outputs"
        triggers = detector.detect(message, tracker)
        
        # Should detect system-reactive milestone trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'system_reactive' for t in triggers)
    
    def test_detect_high_frustration(self):
        """Test detecting high frustration state"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Set high frustration
        tracker.update_conversation_state({'frustration_level': 0.8})
        
        message = "This is taking too long"
        triggers = detector.detect(message, tracker)
        
        # Should detect system-reactive error recovery trigger
        assert len(triggers) > 0
        assert any(t['type'] == 'system_reactive' for t in triggers)


class TestTriggerPriority:
    """Test trigger priority handling"""
    
    def test_multiple_triggers_sorted_by_priority(self):
        """Test that multiple triggers are sorted by priority"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Message that could trigger multiple patterns
        message = "I'm confused about where we are"
        triggers = detector.detect(message, tracker)
        
        if len(triggers) > 1:
            # Should be sorted by priority
            priorities = [t.get('priority', 'medium') for t in triggers]
            # Critical > high > medium > low
            priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            priority_values = [priority_order.get(p, 0) for p in priorities]
            
            # Check if sorted descending
            assert priority_values == sorted(priority_values, reverse=True)


class TestKeywordMatching:
    """Test keyword-based trigger matching"""
    
    def test_match_navigation_keywords(self):
        """Test matching navigation keywords"""
        detector = TriggerDetector()
        
        keywords = ['where are we', 'what\'s next', 'status', 'progress']
        
        for keyword in keywords:
            message = f"Can you tell me {keyword}?"
            result = detector._match_keywords(message, keywords)
            assert result is True
    
    def test_match_confusion_keywords(self):
        """Test matching confusion keywords"""
        detector = TriggerDetector()
        
        keywords = ['confused', 'don\'t understand', 'unclear', 'not sure']
        
        for keyword in keywords:
            message = f"I'm {keyword} about this"
            result = detector._match_keywords(message, keywords)
            assert result is True
    
    def test_no_match_on_unrelated_message(self):
        """Test no match on unrelated message"""
        detector = TriggerDetector()
        
        keywords = ['where are we', 'status']
        message = "The sales forecast is important"
        
        result = detector._match_keywords(message, keywords)
        assert result is False


class TestContextAwareness:
    """Test context-aware trigger detection"""
    
    def test_trigger_depends_on_knowledge_state(self):
        """Test that some triggers depend on knowledge state"""
        detector = TriggerDetector()
        tracker1 = KnowledgeTracker()
        tracker2 = KnowledgeTracker()
        
        # Tracker1: user doesn't understand MIN
        tracker1.update_user_knowledge({'understands_min_calculation': False})
        
        # Tracker2: user understands MIN
        tracker2.update_user_knowledge({'understands_min_calculation': True})
        
        message = "The team is good but data quality is poor"
        
        triggers1 = detector.detect(message, tracker1)
        triggers2 = detector.detect(message, tracker2)
        
        # Should have different triggers based on knowledge state
        # (tracker1 might trigger education, tracker2 might not)
        # This is a behavioral check
        assert isinstance(triggers1, list)
        assert isinstance(triggers2, list)


class TestProfanityAsEmotionalMultiplier:
    """Test profanity as emotional intensity multiplier (not standalone signal)"""
    
    def test_extreme_pain_signal(self):
        """Profanity + pain + assessment = EXTREME_PAIN_SIGNAL (CRITICAL for discovery!)"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Test: User expressing extreme dissatisfaction with current solution
        message = "Our marketing automation is a fucking scam, does nothing, just bullshit"
        triggers = detector.detect(message, tracker)
        
        # Should detect EXTREME_PAIN_SIGNAL (this is discovery!)
        assert any(t['trigger_id'] == 'EXTREME_PAIN_SIGNAL' for t in triggers), \
            "Should detect EXTREME_PAIN_SIGNAL for profanity + pain + assessment"
        
        # Should be critical priority
        pain_trigger = next((t for t in triggers if t['trigger_id'] == 'EXTREME_PAIN_SIGNAL'), None)
        assert pain_trigger and pain_trigger['priority'] == 'critical', \
            "EXTREME_PAIN_SIGNAL should be critical priority"
        
        # Should be discovery category (user revealing pain point!)
        assert pain_trigger and pain_trigger['category'] == 'discovery', \
            "EXTREME_PAIN_SIGNAL should be discovery category"
    
    def test_extreme_frustration(self):
        """Profanity + frustration + assessment = EXTREME_FRUSTRATION"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Test: Frustrated question with profanity
        message = "Where the fuck is the sales data report quality list?"
        triggers = detector.detect(message, tracker)
        
        # Should detect FRUSTRATION_DETECTED with extreme intensity
        frustration = next((t for t in triggers if t['trigger_id'] == 'FRUSTRATION_DETECTED'), None)
        assert frustration is not None, "Should detect FRUSTRATION_DETECTED"
        assert frustration.get('emotional_intensity') == 'extreme', \
            "Should mark as extreme emotional intensity"
        assert frustration['priority'] == 'critical', \
            "Extreme frustration should be critical priority"
    
    def test_extreme_satisfaction(self):
        """Profanity + satisfaction = EXTREME_SATISFACTION (positive!)"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Test: Positive feedback with profanity
        message = "That's fucking awesome, mate! This works perfectly!"
        triggers = detector.detect(message, tracker)
        
        # Should detect EXTREME_SATISFACTION
        assert any(t['trigger_id'] == 'EXTREME_SATISFACTION' for t in triggers), \
            "Should detect EXTREME_SATISFACTION for profanity + positive sentiment"
        
        # Should be low priority (acknowledge briefly)
        satisfaction = next((t for t in triggers if t['trigger_id'] == 'EXTREME_SATISFACTION'), None)
        assert satisfaction and satisfaction['priority'] == 'low', \
            "EXTREME_SATISFACTION should be low priority"
    
    def test_childish_behavior(self):
        """Profanity + no meaningful content = CHILDISH_BEHAVIOR"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Test: Gibberish with profanity
        message = "Fucklala trallala fuck fuckety prumm prumm"
        triggers = detector.detect(message, tracker)
        
        # Should detect CHILDISH_BEHAVIOR (not hostile language)
        assert any(t['trigger_id'] == 'CHILDISH_BEHAVIOR' for t in triggers), \
            "Should detect CHILDISH_BEHAVIOR for profanity without meaningful content"
    
    def test_profanity_escalates_priority(self):
        """Profanity should escalate priority of other triggers"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Test: Out of scope without profanity
        message_normal = "I work in a chicken factory counting eggs"
        triggers_normal = detector.detect(message_normal, tracker)
        
        # Test: Out of scope WITH profanity
        message_profane = "I work in a fucking chicken factory counting eggs"
        triggers_profane = detector.detect(message_profane, tracker)
        
        # Both should detect OUT_OF_SCOPE
        normal_oos = next((t for t in triggers_normal if t['trigger_id'] == 'OUT_OF_SCOPE'), None)
        profane_oos = next((t for t in triggers_profane if t['trigger_id'] == 'OUT_OF_SCOPE'), None)
        
        assert normal_oos is not None, "Should detect OUT_OF_SCOPE without profanity"
        assert profane_oos is not None, "Should detect OUT_OF_SCOPE with profanity"
        
        # Profanity should escalate priority
        assert profane_oos['priority'] == 'high', "Profanity should escalate to high priority"
        assert normal_oos['priority'] == 'medium', "Without profanity should be medium priority"
    
    def test_normal_frustration_without_profanity(self):
        """Frustration without profanity should still be detected (normal intensity)"""
        detector = TriggerDetector()
        tracker = KnowledgeTracker()
        
        # Test: Frustration without profanity
        message = "Where is the sales data report? I've been waiting forever"
        triggers = detector.detect(message, tracker)
        
        # Should detect FRUSTRATION_DETECTED
        frustration = next((t for t in triggers if t['trigger_id'] == 'FRUSTRATION_DETECTED'), None)
        assert frustration is not None, "Should detect frustration without profanity"
        assert frustration.get('emotional_intensity') == 'normal', \
            "Should mark as normal emotional intensity"
        assert frustration['priority'] == 'high', \
            "Normal frustration should be high priority (not critical)"


@pytest.fixture
def sample_triggers():
    """Sample trigger definitions for testing"""
    return [
        {
            'trigger_id': 'TRIGGER_001',
            'type': 'user_explicit',
            'category': 'navigation',
            'keywords': ['where are we', 'status', 'progress'],
            'priority': 'high'
        },
        {
            'trigger_id': 'TRIGGER_002',
            'type': 'user_implicit',
            'category': 'confusion',
            'keywords': ['confused', 'don\'t understand'],
            'priority': 'critical'
        },
        {
            'trigger_id': 'TRIGGER_003',
            'type': 'system_reactive',
            'category': 'onboarding',
            'condition': 'is_first_message',
            'priority': 'high'
        }
    ]
