# Pattern Engine Implementation Plan

**Release:** 2.1 - Pattern Engine Foundation  
**Status:** Specification  
**Date:** 2025-11-06

---

## Overview

Build production-ready pattern engine that provides:
1. Pattern loading and validation
2. Trigger detection (4 types)
3. Knowledge state tracking
4. Pattern selection by affinity
5. LLM prompt integration
6. Semantic and behavioral testing

**Full Format Spec:** See `PATTERN_FORMAT.md`  
**Runtime Architecture:** See `PATTERN_RUNTIME_ARCHITECTURE.md`

---

## Week 1: Core Pattern System

### Goal
Load pattern library and track knowledge state

### Tasks

**1. Pattern Data Structure**
```python
# src/patterns/models.py
@dataclass
class Pattern:
    pattern_id: str
    name: str
    category: str
    trigger: TriggerCondition
    behavior: BehaviorSpec
    updates: KnowledgeUpdates
    tests: TestSpec
    metadata: PatternMetadata
```

**2. Pattern Loader**
```python
# src/patterns/pattern_loader.py
class PatternLoader:
    def load_from_yaml(path: str) -> Pattern
    def load_category(category: str) -> List[Pattern]
    def load_all() -> Dict[str, Pattern]
    def validate_pattern(pattern: Pattern) -> bool
```

**3. Knowledge Tracker**
```python
# src/patterns/knowledge_tracker.py
class KnowledgeTracker:
    user_knowledge: Dict[str, Any]
    system_knowledge: Dict[str, Any]
    
    def update(updates: KnowledgeUpdates)
    def check_prerequisites(pattern: Pattern) -> bool
    def get_state() -> KnowledgeState
    def serialize() -> dict
```

**4. Trigger Detector (Basic)**
```python
# src/patterns/trigger_detector.py
class TriggerDetector:
    def detect_user_explicit(message: str) -> List[str]
    def detect_user_implicit(message: str, context: Context) -> List[str]
    def detect_system_reactive(state_change: StateChange) -> List[str]
    # System-proactive in Week 2
```

### Deliverables
- Pattern data models
- YAML loader with validation
- Knowledge state tracking
- Basic trigger detection
- 15+ unit tests

### Success Criteria
✅ Load 77 behaviors from YAML  
✅ Validate pattern structure  
✅ Track user/system knowledge  
✅ Detect explicit triggers (keywords)  
✅ All unit tests pass

---

## Week 2: Behavior Library & Selection

### Goal
Implement pattern selection algorithm and migrate behavior library

### Tasks

**1. Migrate Behavior Library**
```
sandbox/conversation_ux_exercise/atomic_behaviors.yaml
  ↓ Split by category
data/patterns/behaviors/
  ├── education.yaml
  ├── transparency.yaml
  ├── navigation.yaml
  ├── assessment.yaml
  ├── discovery.yaml
  ├── onboarding.yaml
  ├── context_extraction.yaml
  ├── analysis.yaml
  ├── recommendation.yaml
  └── error_recovery.yaml
```

**2. Add Situation Affinity Scores**
```yaml
# Example: data/patterns/behaviors/education.yaml
- id: B_EXPLAIN_OBJECT_MODEL
  goal: "Teach simplistic object model design"
  situation_affinity:  # NEW
    discovery: 0.3
    assessment: 0.4
    education: 0.9
    clarification: 0.5
  template: |
    Quick note on how this works...
```

**3. Pattern Selector**
```python
# src/patterns/pattern_selector.py
class PatternSelector:
    def __init__(self, patterns: Dict[str, Pattern]):
        self.index = self._build_index(patterns)
    
    def select(
        self,
        triggers: List[str],
        knowledge: KnowledgeState,
        situation: Optional[SituationComposition] = None
    ) -> List[Pattern]:
        # 1. Filter by triggers
        # 2. Filter by prerequisites
        # 3. Score by situation affinity (if provided)
        # 4. Apply priority resolution
        # 5. Return top N
```

**4. LLM Integration**
```python
# src/patterns/llm_integration.py
class PatternPromptBuilder:
    def inject_patterns(
        base_prompt: str,
        active_patterns: List[Pattern],
        situation: Optional[SituationComposition]
    ) -> str:
        # Add pattern context to LLM prompt
        # Include situation composition
        # Add behavior templates
```

**5. Complete Trigger Detection**
```python
# src/patterns/trigger_detector.py (enhanced)
class TriggerDetector:
    # Week 1 methods +
    def detect_system_proactive(
        message: str,
        context: Context,
        knowledge: KnowledgeState
    ) -> List[str]:
        # Detect opportunities (timeline, budget mentions)
        # Check if already extracted
        # Return proactive patterns
```

### Deliverables
- 77 behaviors in `data/patterns/behaviors/`
- 40+ triggers in `data/patterns/triggers/`
- Pattern selection algorithm
- LLM prompt integration
- Complete trigger detection
- 20+ integration tests

### Success Criteria
✅ All 77 behaviors loaded with affinity scores  
✅ Pattern selection works with/without situation  
✅ Trigger detection covers all 4 types  
✅ LLM prompts include pattern context  
✅ Integration tests pass

---

## Week 3: Testing Infrastructure

### Goal
Enable semantic and behavioral testing for patterns

### Tasks

**1. Semantic Test Framework (LLM-as-Judge)**
```python
# tests/patterns/semantic/test_framework.py
class SemanticTestRunner:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def run_test(pattern: Pattern, test_case: SemanticTest) -> TestResult:
        # Generate response using pattern
        # Evaluate with LLM-as-judge
        # Return PASS/FAIL with reasoning
```

**2. Behavioral Test Framework (State Assertions)**
```python
# tests/patterns/behavioral/test_framework.py
class BehavioralTestRunner:
    def run_test(pattern: Pattern, test_case: BehavioralTest) -> TestResult:
        # Set up initial state
        # Execute pattern
        # Assert state changes
        # Return PASS/FAIL
```

**3. Integration Test Scenarios**
```python
# tests/patterns/integration/test_scenarios.py
def test_first_time_user_flow():
    # Turn 1: Welcome pattern
    # Turn 2: Output discovery
    # Turn 3: Context identification
    # Assert: Knowledge updated correctly

def test_multi_output_assessment():
    # Assess multiple outputs
    # Switch between them
    # Assert: State tracked per output

def test_error_recovery():
    # User contradicts self
    # System detects contradiction
    # Clarification pattern triggers
    # Assert: Contradiction resolved
```

**4. Pattern Validation Pipeline**
```python
# tests/patterns/validation/validate_patterns.py
def validate_all_patterns():
    # Load all patterns
    # Check structure
    # Verify triggers exist
    # Verify knowledge dimensions exist
    # Check for circular dependencies
    # Validate test coverage
```

**5. CI/CD Integration**
```yaml
# .github/workflows/pattern-tests.yml
name: Pattern Tests
on: [push, pull_request]
jobs:
  test:
    - Run pattern validation
    - Run behavioral tests (fast, free)
    - Run semantic tests (on PR only, costs $)
```

### Deliverables
- Semantic test framework (LLM-as-judge)
- Behavioral test framework (state assertions)
- 5+ integration test scenarios
- Pattern validation pipeline
- CI/CD workflow
- Test documentation

### Success Criteria
✅ 20+ semantic tests passing  
✅ 30+ behavioral tests passing  
✅ 5+ integration scenarios passing  
✅ Pattern validation catches errors  
✅ CI/CD pipeline operational  
✅ Test execution <2 minutes (excluding semantic)

---

## Technical Architecture

### File Structure

```
src/patterns/
├── __init__.py
├── models.py                  # Pattern data structures
├── pattern_loader.py          # YAML → objects
├── pattern_selector.py        # Selection algorithm
├── trigger_detector.py        # 4 trigger types
├── knowledge_tracker.py       # State tracking
└── llm_integration.py         # Prompt injection

data/patterns/
├── behaviors/
│   ├── education.yaml         # 10 behaviors
│   ├── transparency.yaml      # 8 behaviors
│   ├── navigation.yaml        # 7 behaviors
│   ├── assessment.yaml        # 12 behaviors
│   ├── discovery.yaml         # 9 behaviors
│   ├── onboarding.yaml        # 6 behaviors
│   ├── context_extraction.yaml # 8 behaviors
│   ├── analysis.yaml          # 6 behaviors
│   ├── recommendation.yaml    # 7 behaviors
│   └── error_recovery.yaml    # 4 behaviors
│
├── triggers/
│   ├── user_explicit.yaml     # 15 triggers
│   ├── user_implicit.yaml     # 10 triggers
│   ├── system_proactive.yaml  # 8 triggers
│   └── system_reactive.yaml   # 7 triggers
│
└── knowledge_dimensions.yaml  # User + system knowledge

tests/patterns/
├── semantic/
│   ├── test_framework.py
│   ├── test_onboarding.py
│   ├── test_discovery.py
│   └── ...
│
├── behavioral/
│   ├── test_framework.py
│   ├── test_knowledge_updates.py
│   ├── test_state_transitions.py
│   └── ...
│
├── integration/
│   ├── test_first_time_user.py
│   ├── test_multi_output.py
│   ├── test_error_recovery.py
│   └── ...
│
└── validation/
    └── validate_patterns.py
```

---

## Integration Points

### With Existing System

**1. Session Manager**
```python
# src/core/session_manager.py
class SessionManager:
    def __init__(self):
        self.knowledge_tracker = KnowledgeTracker()  # NEW
        # Remove: self.phase
```

**2. Conversation Orchestrator**
```python
# src/orchestrator/conversation_orchestrator.py
class ConversationOrchestrator:
    def __init__(self):
        self.pattern_selector = PatternSelector(patterns)  # NEW
        self.trigger_detector = TriggerDetector()  # NEW
    
    async def handle_message(self, message: str):
        # Detect triggers
        triggers = self.trigger_detector.detect_all(message, context)
        
        # Select patterns
        patterns = self.pattern_selector.select(
            triggers,
            self.session.knowledge_tracker.get_state()
        )
        
        # Inject into LLM prompt
        prompt = PatternPromptBuilder.inject_patterns(
            base_prompt, patterns
        )
        
        # Generate response
        response = await self.llm.generate(prompt)
        
        # Update knowledge
        self.session.knowledge_tracker.update(patterns[0].updates)
```

---

## Migration from Sandbox

### What to Keep
- Pattern format specification ✅
- Runtime architecture design ✅
- UX principles ✅
- Behavior library (77 behaviors) ✅
- Trigger library (40+ triggers) ✅
- Knowledge dimensions ✅

### What to Implement Fresh
- Pattern loader (new code)
- Pattern selector (new code)
- Trigger detector (new code)
- Knowledge tracker (new code)
- Test frameworks (new code)

### What to Archive
- Sandbox exploration docs (keep for reference)
- Prototype code (not production-ready)
- Design iterations (historical value)

---

## Testing Strategy

### Unit Tests (Fast, Free)
- Pattern loading and validation
- Knowledge state updates
- Trigger detection logic
- Pattern selection algorithm
- **Run on:** Every commit

### Integration Tests (Fast, Free)
- End-to-end conversation flows
- Multi-pattern scenarios
- State transitions
- **Run on:** Every commit

### Semantic Tests (Slow, Costs $)
- LLM-as-judge evaluation
- Response quality checks
- Pattern appropriateness
- **Run on:** PR creation, pre-release

---

## Success Metrics

### Functional
- ✅ 77 behaviors loaded and validated
- ✅ 40+ triggers detected correctly
- ✅ Pattern selection <5ms overhead
- ✅ Knowledge state tracked accurately
- ✅ LLM prompts include pattern context

### Quality
- ✅ 20+ semantic tests passing (>85% accuracy)
- ✅ 30+ behavioral tests passing (100% pass rate)
- ✅ 5+ integration scenarios passing
- ✅ Pattern validation catches structural errors
- ✅ CI/CD pipeline operational

### Performance
- ✅ Pattern index: <100 KB memory
- ✅ Pattern matching: <5ms per turn
- ✅ Knowledge state: <10 KB per session
- ✅ Test execution: <2 min (excluding semantic)

---

## Risk Mitigation

### Risk: Pattern complexity overwhelming
**Mitigation:** Start with 20 core patterns, expand incrementally

### Risk: LLM doesn't follow patterns
**Mitigation:** Semantic tests validate adherence, iterate on prompts

### Risk: Performance overhead
**Mitigation:** Compiled index + lazy loading architecture

### Risk: Test costs too high
**Mitigation:** Cache LLM judge responses, run expensive tests nightly only

---

## Dependencies

**Requires:**
- Release 2 complete (conversation orchestrator, session manager)
- LLM client operational (Gemini)
- YAML parser (PyYAML)

**Enables:**
- Release 2.2 (Situational Awareness)
- Release 2.5 (Semantic Evaluation)

**Blocks:**
- Release 2.2 cannot start without pattern selection
- Release 3 conversation quality depends on patterns

---

## Timeline

**Total Duration:** 3 weeks  
**Effort:** 1 engineer full-time  
**Parallel:** Can run alongside Release 2 completion

**Week 1:** Core system (loading, validation, knowledge tracking)  
**Week 2:** Behavior library & selection (77 behaviors, algorithm)  
**Week 3:** Testing infrastructure (semantic + behavioral + integration)

---

**Owner:** Technical Lead  
**Priority:** High - Blocks Release 2.2 and 2.5  
**Status:** Ready to implement
