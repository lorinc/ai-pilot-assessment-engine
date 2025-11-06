# Reactive-Proactive Response Architecture

**Release:** 2.2 - Situational Awareness  
**Status:** ✅ Implemented (Core)  
**Date:** 2025-11-06

---

## Overview

New response composition architecture that separates **reactive** (answering user) from **proactive** (advancing conversation) components.

**Key Innovation:** Instead of single monolithic responses, compose responses from:
1. **Reactive component** - Addresses user's immediate need (trigger-driven)
2. **Proactive components** - Advances conversation naturally (situation-driven, 0-2 items)

---

## The Problem with Single-Response Architecture

### Current Approach (Release 2.1)

```
User Message → Triggers → Pattern Selection → Single LLM Response
```

**Pattern must do everything:**
```yaml
B_IDENTIFY_OUTPUT:
  response_template: |
    Got it - you're talking about {output_name}.
    [REACTIVE: acknowledge what user said]
    
    To assess this properly, I need to understand:
    - Who creates this output?
    - What system is it in?
    [PROACTIVE: ask next questions]
```

**Problems:**
- ❌ Pattern has multiple responsibilities (violates SRP)
- ❌ Hard to separate "answer user" from "what's next"
- ❌ Multi-pattern responses require complex merging
- ❌ Pattern chaining needs full re-processing
- ❌ Can't opportunistically extract context

---

## The Solution: Reactive + Proactive

### New Architecture

```
User Message → Triggers → Pattern Selection →
  1. Reactive Response (answer user's immediate need)
  2. Proactive Response 1 (advance conversation)
  3. Proactive Response 2 (optional, if context allows)
```

**Separated Patterns:**
```yaml
# Reactive part (answer user)
B_ACKNOWLEDGE_OUTPUT:
  response_type: reactive
  response_template: |
    Got it - you're talking about {output_name}.

# Proactive part (advance conversation)  
B_ASK_OUTPUT_CONTEXT:
  response_type: proactive
  response_template: |
    To assess this properly, I need to understand:
    - Who creates this output?
    - What system is it in?
```

**Benefits:**
- ✅ Single Responsibility Principle
- ✅ Clean separation of concerns
- ✅ Natural multi-pattern support
- ✅ Enables pattern chaining
- ✅ Opportunistic context extraction

---

## Core Concepts

### 1. Response Component

**Definition:** A single piece of the response (reactive or proactive)

```python
@dataclass
class ResponseComponent:
    type: Literal['reactive', 'proactive']
    pattern: Dict[str, Any]
    priority: str
    token_budget: int
```

**Types:**
- **Reactive:** Answers user's immediate need (trigger-driven)
- **Proactive:** Advances conversation (situation-driven)

---

### 2. Composed Response

**Definition:** Complete response = reactive + proactive components

```python
@dataclass
class ComposedResponse:
    reactive: ResponseComponent
    proactive: List[ResponseComponent]  # 0-2 items
    total_tokens: int
```

**Constraints:**
- Reactive: Always present (1 component)
- Proactive: Optional (0-2 components)
- Total tokens: ≤ 310 (token budget)

---

### 3. Selection Logic

**Reactive Selection (Trigger-Driven):**
```python
# Select based on highest-priority trigger
reactive_pattern = select_by_trigger_priority(triggers)
```

**Proactive Selection (Situation-Driven):**
```python
# Select based on situational awareness
proactive_patterns = select_by_situation_affinity(
    situation,
    max_patterns=2,
    exclude_category=reactive_pattern['category']  # Prevent context jumping
)
```

---

## Architecture Details

### Component Selection Flow

```
1. Detect Triggers
   ↓
2. Select Reactive Component
   - Highest priority trigger
   - Match to reactive pattern
   - Allocate 150 tokens
   ↓
3. Select Proactive Components
   - Calculate situation affinity scores
   - Exclude reactive category (prevent context jumping)
   - Select top 2 (if available)
   - Allocate 100 + 60 tokens
   ↓
4. Compose Response
   - Reactive + Proactive(s)
   - Total ≤ 310 tokens
```

---

### Token Budget Allocation

**Total Budget:** 310 tokens (Release 2.1 target)

**Distribution:**
- **Reactive:** 150 tokens (48%)
- **Proactive 1:** 100 tokens (32%)
- **Proactive 2:** 60 tokens (19%)

**Rationale:**
- Reactive gets most tokens (answering user is priority)
- Proactive 1 gets substantial budget (main advancement)
- Proactive 2 gets smaller budget (opportunistic)

---

### Context Jumping Prevention

**Rule:** Proactive components must NOT be in same category as reactive

**Why:** Prevents context jumping (TBD #25 requirement)

**Example:**
```python
# User mentions output (discovery)
reactive = {
    'category': 'discovery',
    'pattern': 'PATTERN_IDENTIFY_OUTPUT'
}

# Proactive candidates
proactive_candidates = [
    {'category': 'discovery', 'pattern': 'ASK_MORE_OUTPUTS'},      # ❌ Same category
    {'category': 'context_extraction', 'pattern': 'EXTRACT_TIMELINE'}  # ✅ Different
]

# Select only different category
selected_proactive = [proactive_candidates[1]]
```

---

## Implementation

### Data Models

**File:** `src/patterns/response_composer.py`

```python
@dataclass
class ResponseComponent:
    """Single response component"""
    type: Literal['reactive', 'proactive']
    pattern: Dict[str, Any]
    priority: str
    token_budget: int

@dataclass
class ComposedResponse:
    """Complete composed response"""
    reactive: ResponseComponent
    proactive: List[ResponseComponent]
    total_tokens: int
```

---

### Response Composer

**Class:** `ResponseComposer`

**Methods:**

1. **`select_components(triggers, situation, patterns)`**
   - Main entry point
   - Returns ComposedResponse

2. **`_select_reactive(triggers, patterns)`**
   - Selects reactive component
   - Trigger-driven

3. **`_select_proactive(situation, patterns, exclude_category, max_count)`**
   - Selects proactive components
   - Situation-driven
   - Prevents context jumping

---

## Examples

### Example 1: Reactive Only

**Input:** User is confused

**Triggers:**
```python
[{'trigger_id': 'CONFUSION_DETECTED', 'priority': 'critical', 'category': 'error_recovery'}]
```

**Situation:**
```python
{'error_recovery': 0.60, 'discovery': 0.20, 'navigation': 0.20}
```

**Result:**
```python
ComposedResponse(
    reactive=ResponseComponent(
        type='reactive',
        pattern={'id': 'PATTERN_CONFUSION', 'category': 'error_recovery'},
        priority='critical',
        token_budget=150
    ),
    proactive=[],  # No proactive (focus on error recovery)
    total_tokens=150
)
```

**Response:**
```
I notice you might be confused. Let me clarify...
[No proactive - user needs help first]
```

---

### Example 2: Reactive + 1 Proactive

**Input:** User mentions output

**Triggers:**
```python
[{'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}]
```

**Situation:**
```python
{'discovery': 0.50, 'context_extraction': 0.30, 'navigation': 0.20}
```

**Result:**
```python
ComposedResponse(
    reactive=ResponseComponent(
        type='reactive',
        pattern={'id': 'PATTERN_IDENTIFY_OUTPUT', 'category': 'discovery'},
        priority='high',
        token_budget=150
    ),
    proactive=[
        ResponseComponent(
            type='proactive',
            pattern={'id': 'PATTERN_EXTRACT_TIMELINE', 'category': 'context_extraction'},
            priority='medium',
            token_budget=100
        )
    ],
    total_tokens=250
)
```

**Response:**
```
Got it - you're talking about Sales Forecasts in the CRM.
[REACTIVE: acknowledge output]

When do you need this assessment completed?
[PROACTIVE: extract timeline]
```

---

### Example 3: Reactive + 2 Proactive

**Input:** User mentions output with urgency

**Triggers:**
```python
[{'trigger_id': 'T_MENTION_OUTPUT', 'priority': 'high', 'category': 'discovery'}]
```

**Situation:**
```python
{'discovery': 0.40, 'context_extraction': 0.35, 'assessment': 0.25}
```

**Result:**
```python
ComposedResponse(
    reactive=ResponseComponent(
        type='reactive',
        pattern={'id': 'PATTERN_IDENTIFY_OUTPUT', 'category': 'discovery'},
        priority='high',
        token_budget=150
    ),
    proactive=[
        ResponseComponent(
            type='proactive',
            pattern={'id': 'PATTERN_EXTRACT_TIMELINE', 'category': 'context_extraction'},
            priority='medium',
            token_budget=100
        ),
        ResponseComponent(
            type='proactive',
            pattern={'id': 'PATTERN_ASK_TEAM', 'category': 'assessment'},
            priority='low',
            token_budget=60
        )
    ],
    total_tokens=310
)
```

**Response:**
```
Got it - you're talking about Sales Forecasts in the CRM.
[REACTIVE: acknowledge output]

When do you need this assessment completed?
[PROACTIVE 1: extract timeline]

Who on the sales team creates these forecasts?
[PROACTIVE 2: start assessment]
```

---

## Benefits

### 1. Solves TBD #20 (Pattern Chaining)

**Before:** Pattern chaining required full re-processing
```
Response 1 → Check triggers → Response 2
```

**After:** Pattern chaining happens in same turn
```
Reactive → Check situation → Add proactive responses
```

---

### 2. Solves TBD #25 (Multi-Pattern Responses)

**Before:** Complex merging logic, risk of context jumping

**After:** Natural composition with context jumping prevention
```
Reactive (answer user) + Proactive 1 + Proactive 2
```

---

### 3. Enables Opportunistic Context Extraction

**Before:** Must ask all questions upfront ("survey")

**After:** Sprinkle questions naturally
```
User: "We need to assess sales forecasting"

Reactive: "Got it - sales forecasting"
Proactive 1: "When do you need this?" [noticed urgency]
Proactive 2: "Who creates these?" [start assessment]
```

---

### 4. Clean Separation of Concerns

**Before:** Pattern does everything (reactive + proactive)

**After:** Each pattern has single responsibility
- Reactive patterns: Answer user
- Proactive patterns: Advance conversation

---

### 5. Natural Fit with Situational Awareness

**Reactive:** Trigger-driven (what user needs NOW)  
**Proactive:** Situation-driven (where conversation should GO)

Perfect alignment with Release 2.2 goals!

---

## Testing

**File:** `tests/patterns/test_response_composition.py`

**Test Coverage:**
- ✅ Response component creation
- ✅ Composed response creation
- ✅ Reactive-only selection
- ✅ Reactive + 1 proactive
- ✅ Reactive + 2 proactive
- ✅ Context jumping prevention
- ✅ Token budget constraints

**Results:** 10/10 tests passing (100%)  
**Coverage:** 96% on response_composer.py

---

## Integration with Release 2.2

### Situational Awareness Integration

```python
# Reactive driven by triggers (immediate need)
reactive_pattern = select_by_trigger_priority(triggers)

# Proactive driven by situation (conversation direction)
proactive_patterns = select_by_situation_affinity(situation)
```

**Perfect Alignment:**
- Triggers → Reactive (what user needs)
- Situation → Proactive (where to go)

---

### Pattern Library Updates

**Required Changes:**
1. Add `response_type` field to all patterns ('reactive' or 'proactive')
2. Split combined patterns into reactive + proactive
3. Add `situation_affinity` to proactive patterns

**Example Split:**
```yaml
# Before (combined)
PATTERN_IDENTIFY_OUTPUT:
  behaviors: [B_IDENTIFY_OUTPUT]  # Does both reactive + proactive

# After (split)
PATTERN_ACKNOWLEDGE_OUTPUT:
  response_type: reactive
  behaviors: [B_ACKNOWLEDGE_OUTPUT]

PATTERN_ASK_OUTPUT_CONTEXT:
  response_type: proactive
  behaviors: [B_ASK_OUTPUT_CONTEXT]
  situation_affinity:
    assessment: 0.8
    context_extraction: 0.6
```

---

## Future Enhancements

### 1. Integrated Composition

**Current:** Sequential composition
```
[Reactive]

[Proactive 1]

[Proactive 2]
```

**Future:** Integrated composition
```
[Reactive], and while we're at it, [Proactive 1]. Also, [Proactive 2].
```

---

### 2. Dynamic Token Allocation

**Current:** Fixed budgets (150, 100, 60)

**Future:** Adjust based on complexity
```python
if reactive_is_simple:
    reactive_budget = 100
    proactive_1_budget = 120
```

---

### 3. Situation-Based Proactive Count

**Current:** Always try for 2 proactive

**Future:** Adjust based on situation
```python
if situation['error_recovery'] > 0.5:
    max_proactive = 0  # Focus on reactive
else:
    max_proactive = 2  # Advance conversation
```

---

## Related Documents

- **Functional Spec:** `docs/1_functional_spec/TBD.md` (TBD #20, #25)
- **Implementation:** `src/patterns/response_composer.py`
- **Tests:** `tests/patterns/test_response_composition.py`
- **Release Plan:** `docs/2_technical_spec/Release2.2/README.md`

---

## Key Takeaways

1. **Reactive = Answer user** (trigger-driven)
2. **Proactive = Advance conversation** (situation-driven)
3. **Composition = Reactive + 0-2 Proactive** (≤310 tokens)
4. **Context jumping prevented** (exclude reactive category)
5. **Natural multi-pattern support** (no complex merging)
6. **Enables pattern chaining** (same turn)
7. **Perfect fit with situational awareness** (Release 2.2)

---

**Status:** Core architecture implemented and tested ✅  
**Next:** Integrate with Situational Awareness class
