# Critical Design Principle: No Global Phases

**Date**: 2025-11-05  
**Status**: LOCKED - This is a fundamental constraint

---

## The Mistake

**Wrong Assumption**: "The system has global phases like 'Discovery Phase', 'Assessment Phase', 'Analysis Phase' that the user progresses through linearly."

**Why It's Wrong**: 
- Users can have multiple outputs, systems, teams
- Each output has independent assessment completeness
- User can jump between outputs non-linearly
- "Discovery" never "completes" - user can always add more outputs

**Example of Wrong Thinking**:
```
❌ "We've completed discovery phase"
❌ "Moving from assessment to analysis"
❌ "Discovery: 100% complete"
```

---

## The Correct Model

**Per-Output Assessment Completeness**

Each output has its own assessment state:
- **Low Confidence** (1-2 components assessed) → Can generate low-confidence recommendations
- **Medium Confidence** (3 components assessed) → Can generate medium-confidence recommendations
- **High Confidence** (4 components + dependencies assessed) → Can generate high-confidence recommendations

**No Global State**

The system does NOT have a global state like:
- ❌ "Discovery Phase"
- ❌ "Assessment Phase"
- ❌ "Analysis Phase"

Instead, it tracks:
- ✅ Per-output assessment completeness
- ✅ Per-output confidence levels
- ✅ Which outputs have enough data for recommendations

---

## Correct Behaviors

**Show Completeness Per Output**:
```
✅ "For Sales Forecast: enough data for medium confidence recommendations"
✅ "For Sales Dashboard: 2 of 4 components assessed - need more for recommendations"
```

**Offer Recommendations Per Output**:
```
✅ "I can generate medium confidence recommendations for Sales Forecast now. 
    Continue assessing or see options?"
```

**Progress Tracking Per Output**:
```
✅ "Sales Forecast: 3/4 components (75%)"
✅ "Sales Dashboard: 1/4 components (25%)"
```

**Session Summary**:
```
✅ "In this session: 
    - Identified 3 outputs
    - Sales Forecast: ready for recommendations (high confidence)
    - Sales Dashboard: partial assessment (low confidence)
    - Revenue Report: just identified, not assessed yet"
```

---

## Why This Matters

### 1. **User Agency**
Users should be able to:
- Jump between outputs freely
- Get recommendations for one output while continuing to assess others
- Add new outputs at any time
- Revisit and update previous assessments

### 2. **Realistic Workflow**
Real conversations are non-linear:
- User mentions 3 outputs initially
- Assesses one deeply
- Gets recommendations
- Mentions 2 more outputs
- Goes back to first output with new information

### 3. **Confidence-Based Recommendations**
Recommendations should be available as soon as there's enough data:
- Low confidence: 1-2 components → "Here are some ideas based on limited data..."
- Medium confidence: 3 components → "Based on what we know, here are solid options..."
- High confidence: 4 components + dependencies → "With high confidence, I recommend..."

### 4. **No False Completion**
"Discovery complete" is a lie:
- User can always discover more outputs
- User can always add more context
- User can always refine assessments
- There is no "done" state

---

## Implementation Impact

### Conversation Patterns

**Wrong Pattern**:
```yaml
trigger: T_DISCOVERY_COMPLETE
behavior: B_ANNOUNCE_PHASE_TRANSITION
template: "Discovery complete! Moving to assessment phase."
```

**Correct Pattern**:
```yaml
trigger: T_OUTPUT_ASSESSMENT_SUFFICIENT
behavior: B_OFFER_RECOMMENDATIONS_AT_CONFIDENCE
template: "For {output}: enough data for {confidence} recommendations. Continue or see options?"
```

### Navigation Behaviors

**Remove These**:
- ❌ B_SHOW_MILESTONE (implies global phases)
- ❌ B_SHOW_PHASE_TRANSITION (implies linear progression)
- ❌ B_ANNOUNCE_DISCOVERY_COMPLETE (discovery never completes)

**Use These Instead**:
- ✅ B_SHOW_OUTPUT_COMPLETENESS (per-output state)
- ✅ B_OFFER_RECOMMENDATIONS_AT_CONFIDENCE (per-output decision)
- ✅ B_SHOW_SESSION_SUMMARY (what was accomplished, not what phase we're in)

### Knowledge State Tracking

**Per Output**:
```python
output_state = {
    "output_id": "sales_forecast_001",
    "components_assessed": 3,
    "confidence_level": "medium",
    "can_recommend": True,
    "missing_components": ["Process_Maturity"]
}
```

**NOT Global**:
```python
# ❌ WRONG
session_state = {
    "phase": "assessment",
    "discovery_complete": True,
    "assessment_progress": 0.75
}
```

---

## UX Implications

### Progress Indicators

**Wrong**:
```
Discovery: ████████████ 100%
Assessment: ██████░░░░░░ 50%
Analysis: ░░░░░░░░░░░░ 0%
```

**Correct**:
```
Sales Forecast: ████████░░░░ 75% (3/4 components) - Medium confidence
Sales Dashboard: ███░░░░░░░░░ 25% (1/4 components) - Low confidence
Revenue Report: ░░░░░░░░░░░░ 0% (just identified)
```

### User Messaging

**Wrong**:
- "Let's complete discovery before moving to assessment"
- "We need to finish assessment phase"
- "You're in the analysis phase now"

**Correct**:
- "Want to assess Sales Forecast more deeply, or see recommendations now?"
- "We have enough for medium confidence recommendations. Continue or evaluate?"
- "You can get recommendations for Sales Forecast while we assess Sales Dashboard"

---

## Testing Criteria

**Validate No Global Phase Assumptions**:

1. User can request recommendations for Output A while Output B is partially assessed ✓
2. User can add new Output C after getting recommendations for Output A ✓
3. User can revisit Output A assessment after seeing recommendations ✓
4. System never says "phase complete" or "moving to next phase" ✓
5. Progress indicators are always per-output, never global ✓

---

## Related Documents

- `docs/0_best_practices/user_interaction_guideline.md` - User agency principles
- `sandbox/conversation_ux_exercise/atomic_behaviors.yaml` - Behavior definitions
- `sandbox/conversation_ux_exercise/atomic_triggers.yaml` - Trigger definitions

---

## Summary

**The Core Principle**:
> There are no global phases. Only per-output assessment completeness and confidence-based recommendation thresholds.

**The Rule**:
> Never say "we've completed X phase" or "moving to Y phase". Always say "for {output}: enough data for {confidence} recommendations".

**The Why**:
> Users work non-linearly across multiple outputs. Forcing linear phases destroys user agency and creates false expectations.
