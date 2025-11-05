# Situational Awareness Feature

**Date**: 2025-11-05  
**Status**: DESIGN - Phase 2.5 Feature  
**Replaces**: Global phase logic (see PHASE_LOGIC_AUDIT.md)

---

## Core Concept

**Situational Awareness** is a dynamic composition of conversation dimensions that guides pattern selection.

**Key Principle**: The situation is always **100%**, but the composition constantly shifts as the conversation unfolds.

---

## The Model

### Situation as Composition

```python
situation = {
    "discovery": 0.50,      # 50% - Identifying outputs, systems, teams
    "education": 0.50,      # 50% - Teaching system concepts
    "assessment": 0.00,     # 0%  - Not yet assessing
    "analysis": 0.00,       # 0%  - Not yet analyzing
    "recommendation": 0.00, # 0%  - Not yet recommending
    "navigation": 0.00,     # 0%  - Not yet navigating
    "error_recovery": 0.00  # 0%  - No errors yet
}
# Total: 1.00 (100%)
```

**As conversation progresses**:
```python
# After identifying first output
situation = {
    "discovery": 0.30,      # Still discovering (can add more outputs)
    "education": 0.20,      # Less education needed
    "assessment": 0.40,     # Now assessing factors
    "navigation": 0.10      # Showing progress
}

# After partial assessment
situation = {
    "discovery": 0.10,      # Background (can still add outputs)
    "assessment": 0.50,     # Primary activity
    "analysis": 0.20,       # Starting to analyze
    "navigation": 0.15,     # More navigation
    "recommendation": 0.05  # Teasing recommendations
}

# After user confusion
situation = {
    "discovery": 0.05,
    "assessment": 0.30,
    "error_recovery": 0.40, # Spike! Handling confusion
    "navigation": 0.15,
    "education": 0.10       # Re-educating
}
```

---

## Dimensions

### 1. Discovery (0-100%)
**What**: Identifying outputs, systems, teams, processes, dependencies

**Signals**:
- ↑ User mentions new output
- ↑ User describes problem abstractly
- ↑ User mentions new system/team
- ↓ Output identified and confirmed
- ↓ Context fully captured

**Patterns Enabled**:
- B_REDIRECT_TO_CONCRETE
- B_PROGRESSIVE_NARROWING
- B_ELICIT_EXAMPLE
- B_DISCOVER_TEAM/SYSTEM/PROCESS
- B_ENRICH_*_CONTEXT

---

### 2. Education (0-100%)
**What**: Teaching system concepts, model, capabilities

**Signals**:
- ↑ First-time user
- ↑ User asks "how does this work?"
- ↑ User confused about model
- ↓ User demonstrates understanding
- ↓ User uses system terminology correctly

**Patterns Enabled**:
- B_EXPLAIN_OBJECT_MODEL
- B_EXPLAIN_DESIGN_DECISIONS
- B_EXPLAIN_EVIDENCE_TIERS
- B_CITE_UX_PRINCIPLES

---

### 3. Assessment (0-100%)
**What**: Gathering evidence, rating factors, capturing context

**Signals**:
- ↑ Output identified
- ↑ User providing ratings/evidence
- ↑ Assessing components
- ↓ Sufficient data collected
- ↓ Moving to recommendations

**Patterns Enabled**:
- B_ASSESS_WITH_PROFESSIONAL_REFLECTION
- B_PROBE_FOR_NUMBERS
- B_PROBE_FOR_EXAMPLE
- B_ACKNOWLEDGE_TIER1
- B_ACCEPT_VAGUE_WITH_LOW_CONFIDENCE

---

### 4. Analysis (0-100%)
**What**: Calculating quality, identifying bottlenecks, analyzing gaps

**Signals**:
- ↑ Sufficient assessment data
- ↑ User asks "what's the problem?"
- ↑ Calculating MIN() scores
- ↓ Bottleneck identified
- ↓ Moving to recommendations

**Patterns Enabled**:
- B_MAP_BOTTLENECK_TO_ARCHETYPE
- B_SHOW_EXPECTED_IMPACT
- B_SYNTHESIZE_EVIDENCE

---

### 5. Recommendation (0-100%)
**What**: Generating pilot options, explaining feasibility, prioritizing

**Signals**:
- ↑ Bottleneck identified
- ↑ User asks "what should I do?"
- ↑ Sufficient confidence for recommendations
- ↓ Recommendations presented
- ↓ User feedback received

**Patterns Enabled**:
- B_GENERATE_PILOT_OPTIONS
- B_SHOW_PILOT_DETAILS
- B_EXPLAIN_FEASIBILITY
- B_SHOW_PREREQUISITES
- B_REQUEST_RECOMMENDATION_FEEDBACK

---

### 6. Navigation (0-100%)
**What**: Showing progress, offering choices, orienting user

**Signals**:
- ↑ User asks "where are we?"
- ↑ Multiple outputs in progress
- ↑ Natural break points
- ↓ Clear next action
- ↓ User engaged in primary activity

**Patterns Enabled**:
- B_SHOW_OUTPUT_COMPLETENESS
- B_SHOW_PROGRESS_BAR
- B_OFFER_RECOMMENDATIONS_AT_CONFIDENCE
- B_SHOW_WHERE_WE_ARE
- B_SUGGEST_NEXT_ACTION

---

### 7. Error Recovery (0-100%)
**What**: Handling confusion, frustration, mistakes

**Signals**:
- ↑ User expresses frustration
- ↑ User says "I'm confused"
- ↑ Repeated corrections
- ↑ User stuck
- ↓ Issue resolved
- ↓ User back on track

**Patterns Enabled**:
- B_DETECT_FRUSTRATION
- B_OFFER_UNDO
- B_OFFER_REPHRASE
- B_BACKTRACK
- B_ACCEPT_DONT_KNOW

---

### 8. Scope Management (0-100%)
**What**: Disambiguating scope, handling multi-output scenarios

**Signals**:
- ↑ Ambiguous statements
- ↑ Multiple outputs mentioned
- ↑ Scope unclear (all systems? just one?)
- ↓ Scope clarified
- ↓ Focused on single output

**Patterns Enabled**:
- B_DETECT_SCOPE_AMBIGUITY
- B_CLARIFY_SYSTEM_SCOPE
- B_NARROW_TO_SPECIFIC
- B_HANDLE_MULTI_OUTPUT

---

## Calculation Algorithm

### Input Signals

```python
signals = {
    "new_output_mentioned": bool,
    "output_confirmed": bool,
    "user_confused": bool,
    "user_frustrated": bool,
    "assessment_data_provided": bool,
    "sufficient_data_for_recommendations": bool,
    "bottleneck_identified": bool,
    "recommendations_requested": bool,
    "scope_ambiguous": bool,
    "first_time_user": bool,
    "user_demonstrates_understanding": bool,
    "progress_query": bool,
    "multiple_outputs_active": bool
}
```

### Calculation Rules

**1. Base Composition (First Message)**
```python
situation = {
    "discovery": 0.50,
    "education": 0.50
}
```

**2. Update on Each Turn**
```python
def update_situation(current_situation, signals, outputs_state):
    new_situation = {}
    
    # Discovery
    if signals["new_output_mentioned"]:
        new_situation["discovery"] = min(1.0, current_situation.get("discovery", 0) + 0.3)
    elif signals["output_confirmed"]:
        new_situation["discovery"] = max(0.1, current_situation.get("discovery", 0) - 0.2)
    else:
        new_situation["discovery"] = current_situation.get("discovery", 0) * 0.9  # Decay
    
    # Education
    if signals["user_confused"] or signals["first_time_user"]:
        new_situation["education"] = min(1.0, current_situation.get("education", 0) + 0.2)
    elif signals["user_demonstrates_understanding"]:
        new_situation["education"] = max(0.05, current_situation.get("education", 0) - 0.15)
    else:
        new_situation["education"] = current_situation.get("education", 0) * 0.95  # Slow decay
    
    # Assessment
    if signals["assessment_data_provided"]:
        new_situation["assessment"] = min(1.0, current_situation.get("assessment", 0) + 0.3)
    elif signals["sufficient_data_for_recommendations"]:
        new_situation["assessment"] = max(0.1, current_situation.get("assessment", 0) - 0.2)
    else:
        new_situation["assessment"] = current_situation.get("assessment", 0) * 0.95
    
    # Analysis
    if signals["sufficient_data_for_recommendations"]:
        new_situation["analysis"] = min(1.0, current_situation.get("analysis", 0) + 0.3)
    elif signals["bottleneck_identified"]:
        new_situation["analysis"] = max(0.1, current_situation.get("analysis", 0) - 0.2)
    else:
        new_situation["analysis"] = current_situation.get("analysis", 0) * 0.9
    
    # Recommendation
    if signals["recommendations_requested"] or signals["bottleneck_identified"]:
        new_situation["recommendation"] = min(1.0, current_situation.get("recommendation", 0) + 0.4)
    else:
        new_situation["recommendation"] = current_situation.get("recommendation", 0) * 0.9
    
    # Navigation
    if signals["progress_query"] or signals["multiple_outputs_active"]:
        new_situation["navigation"] = min(1.0, current_situation.get("navigation", 0) + 0.3)
    else:
        new_situation["navigation"] = max(0.05, current_situation.get("navigation", 0) * 0.8)
    
    # Error Recovery
    if signals["user_confused"] or signals["user_frustrated"]:
        new_situation["error_recovery"] = min(1.0, current_situation.get("error_recovery", 0) + 0.5)
    else:
        new_situation["error_recovery"] = current_situation.get("error_recovery", 0) * 0.7  # Fast decay
    
    # Scope Management
    if signals["scope_ambiguous"] or signals["multiple_outputs_active"]:
        new_situation["scope_management"] = min(1.0, current_situation.get("scope_management", 0) + 0.3)
    else:
        new_situation["scope_management"] = current_situation.get("scope_management", 0) * 0.8
    
    # Normalize to 100%
    total = sum(new_situation.values())
    if total > 0:
        new_situation = {k: v/total for k, v in new_situation.items()}
    
    return new_situation
```

**3. Normalize to 100%**
```python
total = sum(situation.values())
situation = {k: v/total for k, v in situation.items()}
```

---

## Pattern Selection

### How Patterns Use Situation

**Pattern Definition**:
```yaml
- id: B_REDIRECT_TO_CONCRETE
  goal: "Force concrete example"
  template: "Sorry, I don't do abstract. Let's use a concrete event as proxy."
  situation_affinity:
    discovery: 0.8      # Strong affinity with discovery
    education: 0.3      # Some affinity with education
    assessment: 0.2     # Weak affinity with assessment
  min_situation_score: 0.3  # Only trigger if discovery >= 30%
```

**Selection Algorithm**:
```python
def select_patterns(situation, available_patterns):
    scored_patterns = []
    
    for pattern in available_patterns:
        # Calculate affinity score
        score = sum(
            situation[dim] * pattern.situation_affinity.get(dim, 0)
            for dim in situation.keys()
        )
        
        # Check minimum threshold
        primary_dim = max(pattern.situation_affinity.items(), key=lambda x: x[1])[0]
        if situation[primary_dim] >= pattern.min_situation_score:
            scored_patterns.append((pattern, score))
    
    # Sort by score, return top N
    scored_patterns.sort(key=lambda x: x[1], reverse=True)
    return [p for p, s in scored_patterns[:5]]
```

---

## Integration with Phase 2.5

### Conversation Pattern Engine

**Pattern Composition**:
```python
# Current situation
situation = {
    "discovery": 0.20,
    "assessment": 0.50,
    "error_recovery": 0.30
}

# Select patterns
patterns = pattern_engine.select_patterns(
    situation=situation,
    triggers=detected_triggers,
    context=conversation_context
)

# Compose response
response = pattern_engine.compose_response(
    patterns=patterns,
    situation=situation,
    user_message=user_message
)
```

**LLM Prompt Enhancement**:
```python
system_prompt = f"""
You are an AI pilot assessment assistant.

Current Situation Awareness:
- Discovery: {situation['discovery']:.0%}
- Assessment: {situation['assessment']:.0%}
- Error Recovery: {situation['error_recovery']:.0%}
- Navigation: {situation['navigation']:.0%}

Primary Focus: {max(situation.items(), key=lambda x: x[1])[0]}

Active Patterns:
{format_patterns(selected_patterns)}

Respond accordingly, prioritizing error recovery if present.
"""
```

---

## Benefits

### 1. **Enables Non-Linear Conversation**
- No forced phase transitions
- User can jump between activities
- Multiple outputs in parallel

### 2. **Dynamic Pattern Selection**
- Patterns selected based on current situation
- Automatic priority adjustment (error recovery spikes)
- Smooth transitions between activities

### 3. **Better Context Awareness**
- System knows what's happening
- Can explain its focus to user
- Can adapt to user needs

### 4. **Transparent to User**
- Can show situation composition in debug mode
- Can explain why certain patterns are active
- User understands system behavior

### 5. **Measurable & Tunable**
- Can log situation over time
- Can analyze which compositions work best
- Can tune weights and decay rates

---

## UI Representation

### Debug View (Optional)
```
Situation Awareness:
████████████████░░░░ Assessment (50%)
██████░░░░░░░░░░░░░░ Error Recovery (30%)
████░░░░░░░░░░░░░░░░ Discovery (20%)

Active Patterns:
- B_ASSESS_WITH_PROFESSIONAL_REFLECTION (assessment)
- B_OFFER_REPHRASE (error_recovery)
- B_ENRICH_SYSTEM_CONTEXT (discovery)
```

### User-Facing (Subtle)
```
💬 Assessing Sales Forecast (2/4 components)
   I notice some confusion - let me clarify...
```

---

## Implementation Plan

### Phase 1: Core Situational Awareness
1. Create `SituationalAwareness` class
2. Implement signal detection
3. Implement composition calculation
4. Add to session state

### Phase 2: Pattern Integration
1. Add `situation_affinity` to pattern definitions
2. Implement pattern selection algorithm
3. Test pattern composition

### Phase 3: LLM Integration
1. Add situation to system prompt
2. Test response quality
3. Tune weights and thresholds

### Phase 4: Refinement
1. Log situation over conversations
2. Analyze effectiveness
3. Tune decay rates and weights
4. Add more dimensions if needed

---

## Migration from Phase Logic

**Before (Wrong)**:
```python
if self.current_phase == AssessmentPhase.DISCOVERY:
    return self._handle_discovery(user_message)
```

**After (Correct)**:
```python
# Update situation
signals = self._detect_signals(user_message, outputs_state)
self.situation = update_situation(self.situation, signals, outputs_state)

# Select patterns
patterns = self.pattern_engine.select_patterns(
    situation=self.situation,
    triggers=self._detect_triggers(user_message),
    context=self._get_context()
)

# Compose response
return self.pattern_engine.compose_response(patterns, user_message)
```

---

## Testing

**Validate Situational Awareness**:

1. ✅ Situation always sums to 100%
2. ✅ Error recovery spikes when user confused
3. ✅ Discovery decays as outputs confirmed
4. ✅ Assessment rises when gathering evidence
5. ✅ Multiple dimensions active simultaneously
6. ✅ Smooth transitions (no sudden jumps)
7. ✅ Pattern selection reflects situation
8. ✅ User can work non-linearly

---

## Related Documents

- `docs/1_functional_spec/NO_GLOBAL_PHASES.md` - Why global phases are wrong
- `docs/1_functional_spec/PHASE_LOGIC_AUDIT.md` - Current violations
- `sandbox/conversation_ux_exercise/atomic_behaviors.yaml` - Pattern definitions
- `sandbox/conversation_ux_exercise/PATTERN_COMPOSITION_STRATEGY.md` - Pattern composition

---

## Summary

**Situational Awareness** replaces broken global phases with a dynamic, compositional model that:
- Always sums to 100%
- Shifts composition as conversation unfolds
- Enables pattern selection
- Supports non-linear conversation
- Adapts to user needs in real-time

**Key Innovation**: The situation is not a state machine—it's a continuous composition that guides behavior without constraining user agency.
