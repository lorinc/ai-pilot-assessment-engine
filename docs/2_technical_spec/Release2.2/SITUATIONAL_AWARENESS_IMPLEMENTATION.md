# Situational Awareness Implementation Plan

**Phase:** 2.5 - UX Infrastructure  
**Status:** Design  
**Date:** 2025-11-05

---

## Overview

Replace broken global phase logic with **Situational Awareness** - a dynamic composition model that enables pattern-based conversation management.

**Full Design**: See `docs/1_functional_spec/SITUATIONAL_AWARENESS.md`

---

## The Problem

Current implementation uses global phases (DISCOVERY → ASSESSMENT → ANALYSIS → RECOMMENDATIONS → COMPLETE) that:
- ❌ Force linear progression
- ❌ Prevent multi-output assessment
- ❌ Block early recommendations
- ❌ Create false "complete" state
- ❌ Destroy user agency

**Detailed Audit**: See appendix for violations and migration notes.

---

## The Solution

**Situational Awareness** = 100% composition that shifts dynamically:

```python
# Start of conversation
situation = {
    "discovery": 0.50,
    "education": 0.50
}

# After identifying output
situation = {
    "discovery": 0.30,
    "assessment": 0.40,
    "education": 0.20,
    "navigation": 0.10
}

# User gets confused
situation = {
    "assessment": 0.30,
    "error_recovery": 0.40,  # Spike!
    "navigation": 0.15,
    "education": 0.10,
    "discovery": 0.05
}
```

**Always sums to 100%**. Composition guides pattern selection.

---

## Implementation Phases

### Release 1: Core Infrastructure (Week 1)

**Goal**: Replace phase logic with situational awareness

**Tasks**:
1. Create `SituationalAwareness` class
   - 8 dimensions (discovery, education, assessment, analysis, recommendation, navigation, error_recovery, scope_management)
   - Signal detection from user messages
   - Composition calculation (always sums to 100%)
   - Decay/growth rules

2. Update `SessionManager`
   - Remove `phase` property
   - Add `situation` property
   - Track per-output state

3. Refactor `ConversationOrchestrator`
   - Remove `AssessmentPhase` enum
   - Remove release-based routing
   - Add situation updates per turn

**Deliverables**:
- `src/core/situational_awareness.py`
- Updated `src/core/session_manager.py`
- Updated `src/orchestrator/conversation_orchestrator.py`
- Unit tests for composition calculation

---

### Release 2: Pattern Integration (Week 2)

**Goal**: Connect situational awareness to pattern selection

**Tasks**:
1. Add `situation_affinity` to behavior definitions
   - Parse from `sandbox/conversation_ux_exercise/atomic_behaviors.yaml`
   - Map behaviors to dimensions

2. Implement pattern selection algorithm
   - Score patterns by situation affinity
   - Filter by minimum thresholds
   - Return top N patterns

3. Update LLM prompts
   - Include situation composition
   - Include active patterns
   - Guide response generation

**Deliverables**:
- Updated behavior YAML with affinity scores
- `src/engines/pattern_selector.py`
- Updated LLM system prompts
- Integration tests

---

### Release 3: Intent Detection (Week 3)

**Goal**: Replace release-based routing with intent detection

**Tasks**:
1. Implement intent detection
   - Classify user messages (identify_output, provide_assessment, request_recommendations, etc.)
   - Use LLM + heuristics

2. Route by intent + situation
   - No more "in this phase, that's not possible"
   - User can jump between activities
   - Multi-output support

3. Update conversation handlers
   - Remove phase guards
   - Add per-output state tracking
   - Enable non-linear flows

**Deliverables**:
- `src/engines/intent_detector.py`
- Refactored conversation handlers
- End-to-end conversation tests

---

### Release 4: Refinement (Week 4)

**Goal**: Tune and optimize

**Tasks**:
1. Log situation over conversations
2. Analyze effectiveness
3. Tune decay rates and weights
4. Add debug UI (optional)
5. Performance optimization

**Deliverables**:
- Situation logging
- Tuned parameters
- Performance benchmarks
- Documentation

---

## Success Criteria

✅ No global phase logic in codebase  
✅ Situation always sums to 100%  
✅ User can assess multiple outputs simultaneously  
✅ User can get recommendations at any confidence level  
✅ Error recovery spikes appropriately  
✅ Pattern selection reflects situation  
✅ Conversation flows naturally (no forced transitions)  
✅ All existing tests pass with new logic

---

## Technical Architecture

### Core Components

```
src/core/
  ├── situational_awareness.py   # NEW: Situation calculation
  └── session_manager.py          # UPDATED: Remove phase, add situation

src/engines/
  ├── pattern_selector.py         # NEW: Pattern selection by situation
  └── intent_detector.py          # NEW: Intent classification

src/orchestrator/
  └── conversation_orchestrator.py # REFACTORED: Remove phase routing
```

### Data Flow

```
User Message
    ↓
Intent Detection → Classify intent
    ↓
Signal Detection → Extract signals (confused, frustrated, etc.)
    ↓
Situation Update → Calculate new composition (100%)
    ↓
Pattern Selection → Score patterns by affinity
    ↓
Response Generation → Compose response with patterns
    ↓
LLM Prompt → Include situation + patterns
    ↓
Response
```

---

## Migration Strategy

### Backward Compatibility

**Release 1-2**: Dual tracking
- Keep existing release logic
- Add situational awareness in parallel
- Log both, compare results

**Stage 3**: Switch
- Remove release-based routing
- Use intent + situation
- Monitor for regressions

**Stage 4**: Cleanup
- Delete release enum
- Remove release properties
- Update all references

### Risk Mitigation

- Feature flag for new logic
- A/B test with subset of users
- Rollback plan if quality drops
- Extensive logging for debugging

---

## Testing Strategy

### Unit Tests
- Situation composition always sums to 100%
- Signal detection accuracy
- Pattern scoring algorithm
- Intent classification

### Integration Tests
- Multi-output assessment flows
- Early recommendation requests
- Error recovery scenarios
- Non-linear conversation paths

### Semantic Tests (LLM-as-Judge)
- Conversation quality maintained
- Pattern selection appropriateness
- User experience improvements

---

## Cost & Timeline

**Effort**: 4 weeks (1 engineer)  
**Dependencies**: Release 2 complete, atomic behaviors defined  
**Cost**: Development time only (no additional infrastructure)

**Timeline**:
- Week 1: Core infrastructure
- Week 2: Pattern integration
- Week 3: Intent detection
- Week 4: Refinement

---

## Appendix: Current Violations

### Files with Phase Logic

**`src/orchestrator/conversation_orchestrator.py`**:
- Lines 16-22: `AssessmentPhase` enum
- Lines 82-87: Global phase state
- Lines 105-119: Phase-based routing
- Lines 189-191, 304-306, 366-368: Forced transitions

**`src/core/session_manager.py`**:
- Lines 82-92: `phase` property

**`src/app.py`**:
- Lines 172-176: Phase display
- Lines 213-221: Phase documentation

### Migration Notes

**Remove**:
- `AssessmentPhase` enum
- `self.current_phase` property
- `session.phase` property
- Phase-based `if/elif` routing
- "Assessment complete" messages

**Add**:
- `SituationalAwareness` class
- `self.situation` property (dict with 8 dimensions)
- Intent detection
- Pattern selection by affinity
- Per-output state tracking

**Preserve**:
- All existing functionality
- Graph operations
- Assessment logic
- Recommendation generation
- User experience quality

---

## Related Documents

- **Design**: `docs/1_functional_spec/SITUATIONAL_AWARENESS.md` - Full specification
- **Rationale**: `docs/1_functional_spec/NO_GLOBAL_PHASES.md` - Why phases are wrong
- **Audit**: `docs/1_functional_spec/PHASE_LOGIC_AUDIT.md` - Current violations
- **Behaviors**: `sandbox/conversation_ux_exercise/atomic_behaviors.yaml` - Pattern definitions
- **UX Patterns**: `docs/2_technical_spec/Release2.5/USER_INTERACTION_PATTERNS.md` - Pattern system

---

**Owner**: Technical Lead  
**Priority**: High - Blocks Release 3 conversation quality  
**Status**: Ready for implementation
