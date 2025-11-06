# Development Workflow

**Purpose:** Guidelines for how to develop features in this project to minimize risk and maximize feedback.

---

## Core Principles

### 1. Test-Driven Development (TDD) - MANDATORY

**RED → GREEN → REFACTOR**

Write tests BEFORE implementation, always.

**Process:**
1. **RED** - Write failing test that defines desired behavior
2. **GREEN** - Write minimal code to make test pass
3. **REFACTOR** - Improve code quality while keeping tests green

**Why TDD is Mandatory:**
- Catches bugs early (before they exist)
- Forces clear requirements (test defines behavior)
- Enables confident refactoring (tests catch regressions)
- Documents expected behavior (tests are living documentation)
- Prevents scope creep (only implement what tests require)

**Example:**
```python
# 1. RED - Write test first (it will fail)
def test_trigger_detector_detects_confusion():
    detector = TriggerDetector()
    message = "I'm confused about this"
    triggers = detector.detect(message, tracker)
    assert any(t['trigger_id'] == 'CONFUSION_DETECTED' for t in triggers)

# 2. GREEN - Implement minimal code to pass
def detect(self, message, tracker):
    if 'confused' in message.lower():
        return [{'trigger_id': 'CONFUSION_DETECTED'}]
    return []

# 3. REFACTOR - Improve while keeping tests green
def detect(self, message, tracker):
    triggers = []
    if self._match_keywords(message.lower(), self.confusion_keywords):
        triggers.append({
            'type': 'user_implicit',
            'category': 'error_recovery',
            'trigger_id': 'CONFUSION_DETECTED',
            'priority': 'critical'
        })
    return triggers
```

**No Exceptions:**
- Every feature must have tests written first
- No "I'll add tests later" - tests come first
- If you can't write the test, you don't understand the requirement

---

### 2. Vertical Slicing Over Horizontal Layers

**❌ DON'T DO THIS (Horizontal Layers):**
```
Week 1: Build all data models
Week 2: Build all services  
Week 3: Build all UI
Week 4: Test everything
Week 5: UAT (discover major issues!)
```

**✅ DO THIS (Vertical Slices):**
```
Day 1-2: Feature A (end-to-end: model + service + UI)
        → UAT CHECKPOINT (user tests, provides feedback)
        
Day 3-4: Feature B (end-to-end: model + service + UI)
        → UAT CHECKPOINT (user tests, provides feedback)
        
Day 5-6: Feature C (end-to-end: model + service + UI)
        → UAT CHECKPOINT (user tests, provides feedback)
```

**Why?**
- Catch issues early (before building on wrong assumptions)
- User can adjust direction frequently
- Lower risk (small, testable increments)
- Faster feedback loops
- Working software at every checkpoint

---

### 3. UAT Checkpoint Frequency

**RULE: Maximum 2-3 days between UAT checkpoints**

Never build more than one "vertical slice" without user testing.

**What is a UAT Checkpoint?**
- Working software that user can actually test
- Not just unit tests passing
- Not just code written
- Actual behavior user can interact with

**Checkpoint Format:**
```
✅ Feature X complete
   - User can do: [specific action]
   - Expected behavior: [what should happen]
   - UAT: User tests and provides feedback
   - Adjust: Make changes based on feedback
   - Continue: Move to next feature
```

---

## Planning with Checkpoints

### Example: Pattern System (What We Should Have Done)

**❌ What We Did (Risky):**
```
Week 1: Data Models + Pattern Loader + Knowledge Tracker
Week 2: Trigger Detector + Pattern Selector + LLM Integration
Week 3: Test everything
Week 4: UAT (too late!)
```

**✅ What We Should Do Next Time:**
```
Day 1-2: Welcome Pattern (End-to-End)
  - Data model for welcome pattern
  - Trigger: first message detection
  - Selector: choose welcome pattern
  - LLM: generate welcome response
  - UAT: Does welcome work? ← CHECKPOINT
  
Day 3-4: Confusion Detection (End-to-End)
  - Add confusion trigger
  - Add error recovery pattern
  - LLM: generate recovery response
  - UAT: Does confusion recovery work? ← CHECKPOINT
  
Day 5-6: Navigation Pattern (End-to-End)
  - Add navigation trigger
  - Add status pattern
  - LLM: generate status response
  - UAT: Does navigation work? ← CHECKPOINT
```

---

## Development Sequence

### Phase 1: Write Tests (TDD Red Phase)
- Write failing tests that define desired behavior
- Tests should fail (RED)
- Clarify requirements through test cases
- **Time:** 0.5-1 day

### Phase 2: Minimal Implementation (TDD Green Phase)
- Write minimal code to make tests pass
- Tests should pass (GREEN)
- Can be simple, focus on functionality
- **Time:** 1-2 days
- **→ UAT CHECKPOINT** (working software)

### Phase 3: Refine Based on Feedback
- Incorporate user feedback
- Adjust tests if requirements change
- Fix major issues
- **Time:** 0.5-1 day

### Phase 4: Refactor (TDD Refactor Phase)
- Improve code quality
- Keep tests green
- Add documentation
- **Time:** 0.5-1 day
- **→ UAT CHECKPOINT** (polished version)

### Phase 5: Next Feature
- Repeat cycle with TDD

---

## Feature Flags for Incremental Rollout

Use feature flags to deploy incomplete features:

```python
# config/feature_flags.py
ENABLE_PATTERN_ENGINE = os.getenv('ENABLE_PATTERN_ENGINE', 'false') == 'true'
ENABLE_MULTI_PATTERN = os.getenv('ENABLE_MULTI_PATTERN', 'false') == 'true'

# In code
if ENABLE_PATTERN_ENGINE:
    # Use new pattern system
else:
    # Use old system (fallback)
```

**Benefits:**
- Deploy to production without enabling
- Test with real users gradually
- Roll back instantly if issues
- A/B test different approaches

---

## Communication During Development

### Daily Updates (for multi-day features)
- What was completed today
- What's blocked
- When next UAT checkpoint

### UAT Checkpoint Format
```
🎯 UAT Checkpoint: [Feature Name]

What's Ready:
- [Specific functionality user can test]

How to Test:
- [Step-by-step instructions]

Expected Behavior:
- [What should happen]

Known Limitations:
- [What's not implemented yet]

Feedback Needed:
- [Specific questions for user]
```

---

## Anti-Patterns to Avoid

### ❌ Building in Isolation
- "I'll build everything, then show you"
- Risk: Builds wrong thing for weeks

### ❌ Horizontal Layers
- "Let me finish all the backend first"
- Risk: No working software until very late

### ❌ Premature Optimization
- "Let me make this perfect before showing you"
- Risk: Optimizing the wrong thing

### ❌ Feature Creep Without Checkpoints
- "Just one more thing before UAT..."
- Risk: Scope grows, UAT keeps getting delayed

---

## Checklist for Starting New Feature

Before starting any feature:

- [ ] **TDD:** Have I written the tests first? (RED phase)
- [ ] Can this be split into smaller vertical slices?
- [ ] What's the minimal working version?
- [ ] When is the first UAT checkpoint? (max 2-3 days)
- [ ] What specific behavior will user test?
- [ ] Do we have a rollback plan?
- [ ] Is there a feature flag if needed?

**TDD Checklist During Development:**
- [ ] Tests written before implementation? (RED)
- [ ] Tests failing as expected? (RED)
- [ ] Minimal code written to pass tests? (GREEN)
- [ ] All tests passing? (GREEN)
- [ ] Code refactored while keeping tests green? (REFACTOR)
- [ ] Test coverage adequate? (aim for 80%+)

---

## Related Documents

- **Feature Ideas:** Add to `docs/1_functional_spec/TBD.md` (see format there)
- **Implementation Plans:** `docs/2_technical_spec/`
- **Progress Tracking:** `docs/2_technical_spec/Release2.1/TDD_PROGRESS.md`

---

**Last Updated:** 2025-11-06  
**Status:** Active guideline for all future development
