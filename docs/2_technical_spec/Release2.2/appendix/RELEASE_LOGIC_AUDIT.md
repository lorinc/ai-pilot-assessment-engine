# Phase Logic Audit - Code Violations

**Date**: 2025-11-05  
**Status**: CRITICAL - Code violates NO_GLOBAL_PHASES principle

---

## Summary

The `/src` folder contains **hard-coded global phase logic** that violates the per-output assessment model. This must be refactored before production.

---

## Violations Found

### 1. ❌ `src/orchestrator/conversation_orchestrator.py`

**Lines 16-22: Global Phase Enum**
```python
class AssessmentPhase(Enum):
    """Assessment conversation phases."""
    DISCOVERY = "discovery"
    ASSESSMENT = "assessment"
    ANALYSIS = "analysis"
    RECOMMENDATIONS = "recommendations"
    COMPLETE = "complete"
```

**Problem**: Defines global phases that apply to entire session, not per-output.

---

**Lines 82-87: Global Phase State**
```python
# State
self.current_phase = AssessmentPhase.DISCOVERY
self.current_output_id = None
self.current_output_name = None
self.required_quality = None
self.edges_to_assess = []
self.current_edge_index = 0
```

**Problem**: Single `current_phase` for entire orchestrator. Should be per-output state.

---

**Lines 105-119: Phase-Based Routing**
```python
# Route to appropriate handler based on phase
if self.current_phase == AssessmentPhase.DISCOVERY:
    return self._handle_discovery(user_message)
elif self.current_phase == AssessmentPhase.ASSESSMENT:
    return self._handle_assessment(user_message)
elif self.current_phase == AssessmentPhase.ANALYSIS:
    return self._handle_analysis(user_message)
elif self.current_phase == AssessmentPhase.RECOMMENDATIONS:
    return self._handle_recommendations(user_message)
else:
    return {
        "message": "Assessment complete. Type 'restart' to begin a new assessment.",
        "phase": self.current_phase.value,
        "data": {}
    }
```

**Problem**: Routes based on global phase. Prevents:
- Assessing multiple outputs simultaneously
- Getting recommendations for Output A while assessing Output B
- Non-linear conversation flow

---

**Lines 189-191: Forced Phase Transition**
```python
# Move to assessment phase
self.current_phase = AssessmentPhase.ASSESSMENT
self.session.phase = self.current_phase.value
```

**Problem**: Forces linear progression. User cannot:
- Skip assessment if they already know the ratings
- Jump to recommendations early
- Assess multiple outputs in parallel

---

**Lines 207-218: Phase-Gated Logic**
```python
if self.current_edge_index >= len(self.edges_to_assess):
    # All edges assessed, move to analysis
    self.current_phase = AssessmentPhase.ANALYSIS
    self.session.phase = self.current_phase.value
    
    return {
        "message": f"Thank you! I've assessed all the key factors.\n\nNow, what quality level do you **need** for {self.current_output_name}? (1-5 stars, where ⭐=critical issues, ⭐⭐⭐=functional, ⭐⭐⭐⭐⭐=excellent)",
        "phase": self.current_phase.value,
        "data": {
            "assessment_complete": True
        }
    }
```

**Problem**: Blocks analysis until ALL edges assessed. Should allow:
- Partial assessment with low confidence
- User-driven decision to proceed
- Recommendations at any confidence level

---

**Lines 304-306: Another Forced Transition**
```python
# Move to recommendations
self.current_phase = AssessmentPhase.RECOMMENDATIONS
self.session.phase = self.current_phase.value
```

**Problem**: Linear progression enforced.

---

**Lines 366-368: Final Forced Transition**
```python
# Move to complete
self.current_phase = AssessmentPhase.COMPLETE
self.session.phase = self.current_phase.value
```

**Problem**: Marks assessment as "complete" globally. Prevents:
- Assessing additional outputs
- Refining previous assessments
- Continuous conversation

---

### 2. ❌ `src/core/session_manager.py`

**Lines 82-92: Phase Property**
```python
@property
def phase(self) -> str:
    """Get current phase."""
    return self.state['phase']

@phase.setter
def phase(self, value: str):
    """Set current phase."""
    self.state['phase'] = value
    if self.logger:
        self.logger.info("session_phase", f"Phase changed to {value}", {
            "phase": value
        })
```

**Problem**: Session has single global `phase` property. Should track per-output state.

---

### 3. ❌ `src/app.py`

**Lines 172-176: Phase Display**
```python
release_display = progress['phase'].title()
if progress.get('output_name'):
    st.markdown(f"**Assessing:** {progress['output_name']} | **Phase:** {release_display} | **Progress:** {progress.get('assessment_progress', 'N/A')}")
else:
    st.markdown(f"**Phase:** {release_display} | **Session:** `{session_manager.session_id}`")
```

**Problem**: Displays global phase in UI.

---

**Lines 213-221: Phase Documentation**
```python
st.markdown("""
This system helps identify AI opportunities through conversational assessment.

**Current Phase:**
- 🔍 Discovery: Identify output
- 📊 Assessment: Rate factors
- 🎯 Analysis: Find bottlenecks
- 💡 Recommendations: AI pilots

**Release 2 Complete:**
```

**Problem**: Documents linear phase progression to users.

---

## Impact Assessment

### What This Breaks

1. **User Cannot Assess Multiple Outputs**
   - Only one output can be "in progress" at a time
   - Must complete Output A before starting Output B

2. **User Cannot Get Early Recommendations**
   - Must complete all 3 edge assessments before seeing recommendations
   - Cannot get low-confidence recommendations with partial data

3. **User Cannot Refine After "Complete"**
   - Once phase = COMPLETE, conversation ends
   - Cannot add more outputs or update assessments

4. **User Cannot Skip Steps**
   - Must go through: Discovery → Assessment → Analysis → Recommendations
   - Cannot jump to recommendations if they already know the problem

5. **User Cannot Work Non-Linearly**
   - Cannot assess Output A, get recommendations, then assess Output B
   - Cannot revisit Output A after seeing Output B recommendations

---

## Required Refactoring

### 1. Replace Global Phase with Per-Output State

**Current (Wrong)**:
```python
class ConversationOrchestrator:
    def __init__(self):
        self.current_phase = AssessmentPhase.DISCOVERY  # ❌ Global
        self.current_output_id = None
```

**Correct**:
```python
class ConversationOrchestrator:
    def __init__(self):
        self.outputs = {}  # ✅ Per-output state
        # {
        #   "output_001": {
        #       "name": "Sales Forecast",
        #       "components_assessed": 2,
        #       "confidence": "low",
        #       "can_recommend": True,
        #       "edges": {...}
        #   }
        # }
```

---

### 2. Replace Phase-Based Routing with Intent Detection

**Current (Wrong)**:
```python
if self.current_phase == AssessmentPhase.DISCOVERY:
    return self._handle_discovery(user_message)
elif self.current_phase == AssessmentPhase.ASSESSMENT:
    return self._handle_assessment(user_message)
```

**Correct**:
```python
# Detect user intent from message
intent = self._detect_intent(user_message)

if intent == "identify_output":
    return self._handle_output_identification(user_message)
elif intent == "provide_assessment":
    return self._handle_assessment_data(user_message)
elif intent == "request_recommendations":
    return self._handle_recommendation_request(user_message)
```

---

### 3. Allow Recommendations at Any Confidence Level

**Current (Wrong)**:
```python
if self.current_edge_index >= len(self.edges_to_assess):
    # All edges assessed, move to analysis
    self.current_phase = AssessmentPhase.ANALYSIS
```

**Correct**:
```python
# Check if enough data for recommendations
output_state = self.outputs[output_id]
confidence = self._calculate_confidence(output_state)

if confidence >= "low":
    # Offer recommendations at current confidence level
    return self._offer_recommendations(output_id, confidence)
```

---

### 4. Remove "Complete" State

**Current (Wrong)**:
```python
self.current_phase = AssessmentPhase.COMPLETE
return {"message": "Assessment complete. Type 'restart' to begin a new assessment."}
```

**Correct**:
```python
# No "complete" state - conversation continues
return {
    "message": "Recommendations for {output} generated. Want to:\n"
                "1. Assess another output\n"
                "2. Refine this assessment\n"
                "3. Export results"
}
```

---

### 5. Update Session State Model

**Current (Wrong)**:
```python
session.state = {
    'phase': 'discovery',  # ❌ Global phase
    'messages': [...]
}
```

**Correct**:
```python
session.state = {
    'outputs': {  # ✅ Per-output state
        'output_001': {
            'name': 'Sales Forecast',
            'components_assessed': 3,
            'confidence': 'medium',
            'can_recommend': True
        }
    },
    'messages': [...]
}
```

---

## Migration Plan

### Release 1: Add Per-Output State (Non-Breaking)
1. Add `outputs` dict to orchestrator
2. Populate per-output state alongside existing phase logic
3. Test dual tracking

### Release 2: Add Intent Detection (Non-Breaking)
1. Implement intent detection alongside phase routing
2. Log both approaches
3. Compare results

### Release 3: Switch to Intent-Based Routing (Breaking)
1. Replace release-based routing with intent detection
2. Remove global `current_phase`
3. Update UI to show per-output state

### Release 4: Remove Phase Logic (Cleanup)
1. Delete `AssessmentPhase` enum
2. Remove `session.phase` property
3. Update all references

---

## Testing Requirements

**Validate No Phase Restrictions**:

1. ✅ User can assess multiple outputs simultaneously
2. ✅ User can get low-confidence recommendations with partial data
3. ✅ User can refine assessments after seeing recommendations
4. ✅ User can add new outputs at any time
5. ✅ User can skip assessment if they already know ratings
6. ✅ Conversation never reaches "complete" dead end

---

## Related Documents

- `docs/1_functional_spec/NO_GLOBAL_PHASES.md` - Design principle
- `sandbox/conversation_ux_exercise/behaviors_dense_format.md` - Correct behaviors
- `src/orchestrator/conversation_orchestrator.py` - Code to refactor
- `src/core/session_manager.py` - Session state to update

---

## Priority

**CRITICAL** - This is a fundamental architectural violation that prevents the system from working as designed. Must be fixed before adding more features.

**Estimated Effort**: 2-3 days
- Day 1: Add per-output state tracking
- Day 2: Implement intent detection
- Day 3: Remove phase logic, test thoroughly
