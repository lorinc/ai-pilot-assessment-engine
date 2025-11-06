"""
Trigger detector for pattern matching.

Detects 4 types of triggers:
1. User-Explicit: Direct requests (navigation, help, review)
2. User-Implicit: Inferred needs (confusion, contradiction, ambiguity)
3. System-Proactive: Opportunities (context extraction, education, recommendations)
4. System-Reactive: State-based (first message, milestones, frustration)

Release 2.2: Added semantic similarity support for intent detection.
"""
from typing import List, Dict, Any, Optional
from src.patterns.knowledge_tracker import KnowledgeTracker
import re


# Optional: Import semantic intent detector
try:
    from src.patterns.semantic_intent import get_detector
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False


class TriggerDetector:
    """
    Detects conversation triggers from user messages and context.
    
    Supports 4 trigger types across 10 pattern categories.
    """
    
    def __init__(self, trigger_definitions: Optional[List[Dict[str, Any]]] = None, use_semantic: bool = True):
        """
        Initialize trigger detector.
        
        Args:
            trigger_definitions: Optional list of trigger definitions from YAML
            use_semantic: Whether to use semantic similarity (requires OpenAI API key)
        """
        self.trigger_definitions = trigger_definitions or []
        self.use_semantic = use_semantic and SEMANTIC_AVAILABLE
        
        # Initialize semantic detector if available
        if self.use_semantic:
            try:
                self.semantic_detector = get_detector()
            except Exception:
                self.use_semantic = False
                self.semantic_detector = None
        else:
            self.semantic_detector = None
        
        self._init_keyword_patterns()
    
    def _init_keyword_patterns(self):
        """Initialize keyword patterns for trigger detection"""
        # User-Explicit triggers
        self.navigation_keywords = [
            'where are we', 'what\'s next', 'status', 'progress',
            'where do we stand', 'what have we done', 'what\'s left'
        ]
        
        self.help_keywords = [
            'explain', 'what does', 'what is', 'help me understand',
            'can you clarify', 'tell me about', 'how does'
        ]
        
        self.review_keywords = [
            'show me', 'review', 'summary', 'what we\'ve covered',
            'recap', 'go over', 'list'
        ]
        
        # User-Implicit triggers
        self.confusion_keywords = [
            'confused', 'don\'t understand', 'unclear', 'not sure',
            'lost', 'what do you mean', 'huh', 'wait'
        ]
        
        self.contradiction_keywords = [
            'actually', 'no', 'that\'s not right', 'incorrect',
            'i said', 'i meant', 'correction'
        ]
        
        self.system_mistake_keywords = [
            'that\'s wrong', 'you misunderstood', 'that doesn\'t make sense',
            'you\'re confused', 'that\'s not what i said', 'you got it wrong'
        ]
        
        self.ambiguity_keywords = [
            'everywhere', 'all of them', 'everything', 'in general',
            'overall', 'across the board', 'throughout'
        ]
        
        # System-Proactive triggers
        self.timeline_keywords = [
            'by', 'deadline', 'due', 'end of', 'quarter', 'month',
            'week', 'soon', 'urgent', 'asap'
        ]
        
        self.budget_keywords = [
            'cost', 'budget', 'expensive', 'cheap', 'afford',
            'price', 'investment', 'spend'
        ]
        
        self.stakeholder_keywords = [
            'board', 'ceo', 'executive', 'management', 'leadership',
            'stakeholder', 'sponsor', 'owner'
        ]
        
        # Inappropriate Use triggers
        self.off_topic_keywords = [
            'weather', 'joke', 'story', 'recipe', 'game', 'chat',
            'talk about', 'tell me about', 'what about', 'how about'
        ]
        
        self.testing_keywords = [
            'can you', 'will you', 'are you able', 'what if', 'try this',
            'do you know', 'have you heard'
        ]
        
        self.humor_keywords = [
            'haha', 'lol', 'joke', 'kidding', 'just messing', 'jk',
            'funny', 'hilarious'
        ]
        
        # Emotional intensity multipliers (profanity)
        # Profanity has NO standalone meaning - it's a multiplier that shows
        # whatever is being said has strong emotion behind it:
        # - Extreme frustration: "fuck this shit"
        # - Extreme satisfaction: "that's fucking awesome"
        # - Extreme pain signal: "our CRM is a fucking scam"
        # - Childish/inappropriate: "fucklala trallala"
        self.profanity_keywords = [
            'fuck', 'shit', 'damn', 'hell', 'ass', 'bitch', 'bastard',
            'crap', 'piss', 'dick', 'cock', 'pussy'
        ]
        
        self.out_of_scope_keywords = [
            'chicken', 'factory', 'farm', 'agriculture', 'restaurant',
            'recipe', 'cooking', 'food', 'weather', 'sports', 'movie',
            'game', 'music', 'travel', 'vacation', 'personal', 'family',
            'egg', 'eggs', 'poops', 'chick', 'animal'
        ]
        
        self.frustration_indicators = [
            'where the', 'where is', 'what happened to', 'why isn\'t',
            'still waiting', 'been waiting', 'for an hour', 'forever',
            'taking so long', 'not working'
        ]
        
        self.satisfaction_indicators = [
            'awesome', 'amazing', 'perfect', 'exactly', 'great', 'love',
            'excellent', 'fantastic', 'brilliant', 'works', 'helpful'
        ]
        
        self.pain_indicators = [
            'scam', 'useless', 'waste', 'broken', 'doesn\'t work', 'nothing',
            'bullshit', 'terrible', 'awful', 'nightmare', 'disaster'
        ]
        
        # Assessment-related keywords (to distinguish from off-topic)
        self.assessment_keywords = [
            'output', 'factor', 'component', 'dependency', 'bottleneck',
            'team', 'process', 'system', 'data', 'quality', 'pilot',
            'assessment', 'evaluate', 'rate', 'score', 'report', 'forecast',
            'sales', 'revenue', 'crm', 'dashboard', 'marketing', 'automation',
            'analytics', 'pipeline', 'workflow', 'integration'
        ]
    
    def detect(
        self, 
        message: str, 
        tracker: KnowledgeTracker,
        is_first_message: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Detect triggers from user message and context.
        
        Args:
            message: User's message
            tracker: Knowledge tracker with conversation state
            is_first_message: Whether this is the first message
            
        Returns:
            List of detected triggers with metadata
        """
        triggers = []
        
        # Detect all trigger types
        triggers.extend(self._detect_user_explicit(message, tracker))
        triggers.extend(self._detect_user_implicit(message, tracker))
        triggers.extend(self._detect_system_proactive(message, tracker))
        triggers.extend(self._detect_system_reactive(message, tracker, is_first_message))
        triggers.extend(self._detect_inappropriate_use(message, tracker))
        
        # Sort by priority (critical > high > medium > low)
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        triggers.sort(
            key=lambda t: priority_order.get(t.get('priority', 'medium'), 0),
            reverse=True
        )
        
        return triggers
    
    def _detect_user_explicit(
        self, 
        message: str, 
        tracker: KnowledgeTracker
    ) -> List[Dict[str, Any]]:
        """Detect user-explicit triggers (direct requests)"""
        triggers = []
        message_lower = message.lower()
        
        # Navigation queries
        if self._match_keywords(message_lower, self.navigation_keywords):
            triggers.append({
                'type': 'user_explicit',
                'category': 'navigation',
                'trigger_id': 'NAVIGATION_QUERY',
                'priority': 'high',
                'message': message
            })
        
        # Help/explanation requests
        if self._match_keywords(message_lower, self.help_keywords):
            triggers.append({
                'type': 'user_explicit',
                'category': 'education',
                'trigger_id': 'HELP_REQUEST',
                'priority': 'high',
                'message': message
            })
        
        # Review/summary requests
        if self._match_keywords(message_lower, self.review_keywords):
            triggers.append({
                'type': 'user_explicit',
                'category': 'meta',
                'trigger_id': 'REVIEW_REQUEST',
                'priority': 'medium',
                'message': message
            })
        
        return triggers
    
    def _detect_user_implicit(
        self, 
        message: str, 
        tracker: KnowledgeTracker
    ) -> List[Dict[str, Any]]:
        """Detect user-implicit triggers (inferred needs)"""
        triggers = []
        message_lower = message.lower()
        
        # Assessment: Rating detection (CRITICAL - check this FIRST before education)
        rating_patterns = [
            r'\d+\s*stars?',  # "3 stars", "3 star"
            r'\d+\s*out\s*of\s*\d+',  # "3 out of 5"
            r'\d+/\d+',  # "3/5"
            r'rate.*\d+',  # "rate it 3"
            r'is\s+(poor|terrible|bad|mediocre|okay|good|great|excellent)',  # qualitative
            r'(poor|terrible|bad|mediocre|okay|good|great|excellent)\s+(quality|execution|maturity|support)',  # qualitative with component
        ]
        
        import re
        has_rating = any(re.search(pattern, message_lower) for pattern in rating_patterns)
        
        # Also check for component mentions with assessment context
        component_keywords = ['data quality', 'team execution', 'team', 'process', 'system support', 'quality']
        has_component = any(kw in message_lower for kw in component_keywords)
        
        assessment_indicators = [
            'is', 'are', 'rate', 'rated', 'rating', 'about', 'around', 'approximately',
            'issue', 'issues', 'problem', 'problems', 'struggle', 'struggles', 'weak',
            'strong', 'capable', 'needs improvement', 'needs work'
        ]
        has_assessment_context = any(ind in message_lower for ind in assessment_indicators)
        
        if has_rating or (has_component and has_assessment_context):
            triggers.append({
                'type': 'user_implicit',
                'category': 'assessment',
                'trigger_id': 'T_RATE_EDGE',
                'priority': 'high',
                'message': message
            })
        
        # Confusion signals
        if self._match_keywords(message_lower, self.confusion_keywords):
            triggers.append({
                'type': 'user_implicit',
                'category': 'error_recovery',
                'trigger_id': 'CONFUSION_DETECTED',
                'priority': 'critical',
                'message': message
            })
            
            # Update conversation state
            tracker.update_conversation_state({'confusion_level': 0.7})
        
        # System mistake detection (user corrects system)
        if self._match_keywords(message_lower, self.system_mistake_keywords):
            triggers.append({
                'type': 'user_implicit',
                'category': 'error_recovery',
                'trigger_id': 'USER_CORRECTS_SYSTEM',
                'priority': 'critical',
                'message': message,
                'requires_self_deprecation': True
            })
        
        # Contradiction signals
        if self._match_keywords(message_lower, self.contradiction_keywords):
            # Check if there's previous context to contradict
            outputs = tracker.system_knowledge.get('outputs_identified', [])
            if outputs:
                triggers.append({
                    'type': 'user_implicit',
                    'category': 'error_recovery',
                    'trigger_id': 'CONTRADICTION_DETECTED',
                    'priority': 'critical',
                    'message': message
                })
        
        # Scope ambiguity
        if self._match_keywords(message_lower, self.ambiguity_keywords):
            triggers.append({
                'type': 'user_implicit',
                'category': 'discovery',
                'trigger_id': 'SCOPE_AMBIGUITY',
                'priority': 'high',
                'message': message
            })
        
        return triggers
    
    def _detect_system_proactive(
        self, 
        message: str, 
        tracker: KnowledgeTracker
    ) -> List[Dict[str, Any]]:
        """Detect system-proactive triggers (opportunities)"""
        triggers = []
        message_lower = message.lower()
        
        # Natural context extraction opportunities
        if self._match_keywords(message_lower, self.timeline_keywords):
            triggers.append({
                'type': 'system_proactive',
                'category': 'context_extraction',
                'trigger_id': 'TIMELINE_MENTIONED',
                'priority': 'medium',
                'message': message
            })
        
        if self._match_keywords(message_lower, self.budget_keywords):
            triggers.append({
                'type': 'system_proactive',
                'category': 'context_extraction',
                'trigger_id': 'BUDGET_MENTIONED',
                'priority': 'medium',
                'message': message
            })
        
        if self._match_keywords(message_lower, self.stakeholder_keywords):
            triggers.append({
                'type': 'system_proactive',
                'category': 'context_extraction',
                'trigger_id': 'STAKEHOLDER_MENTIONED',
                'priority': 'medium',
                'message': message
            })
        
        # Education opportunity (user mentions components without understanding MIN)
        if not tracker.user_knowledge.get('understands_min_calculation', False):
            # Check if message mentions multiple components
            component_keywords = ['team', 'data', 'process', 'system', 'quality']
            component_count = sum(1 for kw in component_keywords if kw in message_lower)
            
            if component_count >= 2:
                triggers.append({
                    'type': 'system_proactive',
                    'category': 'education',
                    'trigger_id': 'EDUCATION_OPPORTUNITY_MIN',
                    'priority': 'medium',
                    'message': message
                })
        
        # Recommendation opportunity (bottleneck identified)
        bottlenecks = tracker.system_knowledge.get('bottlenecks_identified', {})
        if bottlenecks and ('what should' in message_lower or 'recommend' in message_lower):
            triggers.append({
                'type': 'system_proactive',
                'category': 'recommendation',
                'trigger_id': 'RECOMMENDATION_OPPORTUNITY',
                'priority': 'high',
                'message': message
            })
        
        return triggers
    
    def _detect_system_reactive(
        self, 
        message: str, 
        tracker: KnowledgeTracker,
        is_first_message: bool
    ) -> List[Dict[str, Any]]:
        """Detect system-reactive triggers (state-based)"""
        triggers = []
        
        # First message (onboarding)
        if is_first_message:
            triggers.append({
                'type': 'system_reactive',
                'category': 'onboarding',
                'trigger_id': 'FIRST_MESSAGE',
                'priority': 'high',
                'message': message
            })
        
        # Milestone reached (e.g., 3+ outputs identified)
        outputs = tracker.system_knowledge.get('outputs_identified', [])
        if len(outputs) >= 3:
            # Check if this is a completion signal
            completion_keywords = ['that\'s all', 'that\'s it', 'done', 'finished', 'complete']
            if any(kw in message.lower() for kw in completion_keywords):
                triggers.append({
                    'type': 'system_reactive',
                    'category': 'navigation',
                    'trigger_id': 'MILESTONE_OUTPUTS_IDENTIFIED',
                    'priority': 'medium',
                    'message': message
                })
        
        # High frustration (error recovery needed)
        frustration = tracker.conversation_state.get('frustration_level', 0.0)
        if frustration >= 0.7:
            triggers.append({
                'type': 'system_reactive',
                'category': 'error_recovery',
                'trigger_id': 'HIGH_FRUSTRATION',
                'priority': 'critical',
                'message': message
            })
        
        # High confusion (already tracked in user_implicit, but state-based too)
        confusion = tracker.conversation_state.get('confusion_level', 0.0)
        if confusion >= 0.7:
            triggers.append({
                'type': 'system_reactive',
                'category': 'error_recovery',
                'trigger_id': 'HIGH_CONFUSION',
                'priority': 'critical',
                'message': message
            })
        
        # No progress for multiple turns
        turns_since_progress = tracker.conversation_state.get('turns_since_progress', 0)
        if turns_since_progress >= 3:
            triggers.append({
                'type': 'system_reactive',
                'category': 'navigation',
                'trigger_id': 'STALLED_PROGRESS',
                'priority': 'high',
                'message': message
            })
        
        return triggers
    
    def _detect_inappropriate_use(
        self,
        message: str,
        tracker: KnowledgeTracker
    ) -> List[Dict[str, Any]]:
        """Detect inappropriate use triggers (off-topic, testing, resource waste)"""
        triggers = []
        message_lower = message.lower()
        
        # Check if message is assessment-related
        is_assessment_related = self._match_keywords(message_lower, self.assessment_keywords)
        
        # PROFANITY AS EMOTIONAL INTENSITY MULTIPLIER
        # Profanity has NO standalone meaning - it amplifies whatever emotion is present
        has_profanity = self._match_keywords(message_lower, self.profanity_keywords)
        emotional_intensity = 'extreme' if has_profanity else 'normal'
        
        # Detect base emotion/intent (profanity will amplify these)
        has_frustration = self._match_keywords(message_lower, self.frustration_indicators)
        has_satisfaction = self._match_keywords(message_lower, self.satisfaction_indicators)
        has_pain = self._match_keywords(message_lower, self.pain_indicators)
        has_out_of_scope = self._match_keywords(message_lower, self.out_of_scope_keywords)
        
        # 1. EXTREME PAIN SIGNAL (profanity + pain + assessment-related)
        # "Our CRM is a fucking scam" - CRITICAL for us to detect!
        if has_profanity and has_pain and is_assessment_related:
            triggers.append({
                'type': 'user_implicit',
                'category': 'discovery',  # This is discovery! User revealing pain point
                'trigger_id': 'EXTREME_PAIN_SIGNAL',
                'priority': 'critical',
                'message': message,
                'emotional_intensity': 'extreme',
                'note': 'User expressing strong dissatisfaction with current solution'
            })
        
        # 2. EXTREME FRUSTRATION (profanity + frustration + assessment-related)
        # "Where the fuck is the sales data report?"
        if has_profanity and has_frustration and is_assessment_related:
            triggers.append({
                'type': 'user_implicit',
                'category': 'error_recovery',
                'trigger_id': 'FRUSTRATION_DETECTED',
                'priority': 'critical',
                'message': message,
                'emotional_intensity': 'extreme'
            })
        elif has_frustration and is_assessment_related:
            # Normal frustration without profanity
            triggers.append({
                'type': 'user_implicit',
                'category': 'error_recovery',
                'trigger_id': 'FRUSTRATION_DETECTED',
                'priority': 'high',
                'message': message,
                'emotional_intensity': 'normal'
            })
        
        # 3. EXTREME SATISFACTION (profanity + satisfaction)
        # "That's fucking awesome, mate!"
        if has_profanity and has_satisfaction:
            triggers.append({
                'type': 'user_implicit',
                'category': 'meta',
                'trigger_id': 'EXTREME_SATISFACTION',
                'priority': 'low',
                'message': message,
                'emotional_intensity': 'extreme',
                'note': 'Positive feedback - acknowledge briefly'
            })
        
        # 4. CHILDISH/INAPPROPRIATE (profanity + no meaningful content)
        # "Fucklala trallala fuck fuckety prumm prumm"
        if has_profanity and not is_assessment_related and not has_frustration and not has_satisfaction and not has_pain:
            triggers.append({
                'type': 'user_implicit',
                'category': 'inappropriate_use',
                'trigger_id': 'CHILDISH_BEHAVIOR',
                'priority': 'medium',
                'message': message,
                'emotional_intensity': 'extreme',
                'note': 'Profanity without meaningful content'
            })
        
        # 5. OUT OF SCOPE (with or without profanity multiplier)
        if has_out_of_scope:
            # Count how many out-of-scope vs assessment keywords
            out_of_scope_count = sum(1 for kw in self.out_of_scope_keywords if kw in message_lower)
            assessment_count = sum(1 for kw in self.assessment_keywords if kw in message_lower)
            
            # If more out-of-scope keywords, or if clearly unrelated
            if out_of_scope_count > assessment_count or not is_assessment_related:
                priority = 'high' if has_profanity else 'medium'  # Profanity escalates priority
                triggers.append({
                    'type': 'user_implicit',
                    'category': 'inappropriate_use',
                    'trigger_id': 'OUT_OF_SCOPE',
                    'priority': priority,
                    'message': message,
                    'emotional_intensity': emotional_intensity
                })
        
        # Off-topic detection (only if not assessment-related)
        if not is_assessment_related:
            if self._match_keywords(message_lower, self.off_topic_keywords):
                # Get current off-topic count
                off_topic_count = tracker.conversation_state.get('off_topic_count', 0)
                
                # Increment count
                tracker.update_conversation_state({'off_topic_count': off_topic_count + 1})
                
                # Determine escalation level
                if off_topic_count == 0:
                    trigger_id = 'OFF_TOPIC_FIRST'
                    priority = 'medium'
                elif off_topic_count == 1:
                    trigger_id = 'OFF_TOPIC_SECOND'
                    priority = 'high'
                elif off_topic_count == 2:
                    trigger_id = 'OFF_TOPIC_THIRD'
                    priority = 'high'
                elif off_topic_count >= 3:
                    trigger_id = 'OFF_TOPIC_PERSISTENT'
                    priority = 'critical'
                else:
                    trigger_id = 'OFF_TOPIC_DETECTED'
                    priority = 'medium'
                
                triggers.append({
                    'type': 'user_implicit',
                    'category': 'inappropriate_use',
                    'trigger_id': trigger_id,
                    'priority': priority,
                    'message': message,
                    'off_topic_count': off_topic_count + 1
                })
        
        # Humor detection (allow if not excessive)
        if self._match_keywords(message_lower, self.humor_keywords):
            humor_allowed = tracker.conversation_state.get('humor_allowed', True)
            if humor_allowed:
                triggers.append({
                    'type': 'user_implicit',
                    'category': 'inappropriate_use',
                    'trigger_id': 'HUMOR_DETECTED',
                    'priority': 'low',
                    'message': message,
                    'allow_brief_response': True
                })
        
        # Testing limits detection
        if self._match_keywords(message_lower, self.testing_keywords) and not is_assessment_related:
            triggers.append({
                'type': 'user_implicit',
                'category': 'inappropriate_use',
                'trigger_id': 'TESTING_LIMITS',
                'priority': 'medium',
                'message': message
            })
        
        # No progress made (system-reactive)
        turns_since_progress = tracker.conversation_state.get('turns_since_progress', 0)
        outputs = tracker.system_knowledge.get('outputs_identified', [])
        if turns_since_progress >= 5 and len(outputs) == 0:
            triggers.append({
                'type': 'system_reactive',
                'category': 'inappropriate_use',
                'trigger_id': 'NO_PROGRESS_MADE',
                'priority': 'high',
                'message': message,
                'turns_since_progress': turns_since_progress
            })
        
        return triggers
    
    def _match_keywords(self, message: str, keywords: List[str]) -> bool:
        """
        Check if message contains any of the keywords.
        
        Args:
            message: Message to check (should be lowercase)
            keywords: List of keywords/phrases to match
            
        Returns:
            True if any keyword found
        """
        for keyword in keywords:
            if keyword in message:
                return True
        return False
