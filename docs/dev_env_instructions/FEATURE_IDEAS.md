# Feature Ideas & TBD Management

**Purpose:** How to handle feature ideas and design decisions that need discussion.

---

## Where to Put Feature Ideas

**Location:** `docs/1_functional_spec/TBD.md`

**When to use:**
- New feature ideas
- Design decisions to be made
- Open questions
- Important constraints
- Future improvements

---

## TBD Entry Format

Each entry should follow this template:

```markdown
### [Number]. [Feature Name]
**Added**: YYYY-MM-DD

**Context**: [What this relates to / why this came up]

**Intent**: [What needs to be done or decided]

**Examples** (if applicable):
- Example 1
- Example 2

**Technical Requirements** (if applicable):
- Requirement 1
- Requirement 2

**Benefits** (if applicable):
- Benefit 1
- Benefit 2

**Related** (if applicable):
- Link to other TBD items
- Link to relevant docs

---
```

---

## Example Entry

```markdown
### 25. Multi-Pattern Responses (Merged or Sequential)
**Added**: 2025-11-06

**Context**: When the situation allows (i.e., the LLM does not have to transfer 
a lot of information in the next reply), the system could use TWO patterns at once, 
either merged or in sequence within a single answer.

**Intent**: Enable the system to combine multiple conversation patterns in one 
response when appropriate. This adds significant freedom in guiding the conversation, 
feels more natural and intelligent, and reduces the number of back-and-forth exchanges.

**Examples:**

**Merged Pattern (Single Cohesive Response):**
```
User: "We need to assess sales forecasting"

System combines:
- B_IDENTIFY_OUTPUT (discovery)
- B_CONFIRM_OUTPUT_DETAILS (discovery)

Response: "Got it—Sales Forecast. Just to confirm: is this the forecast that 
your Sales Team maintains in Salesforce, or a different forecasting process?"
```

**When to Use Multi-Pattern:**
1. Low information density: Primary response is brief (< 50 words)
2. Natural opportunity: Secondary pattern feels like natural follow-up
3. High-priority secondary: Context extraction or education opportunity
4. User engagement: Keeps conversation flowing efficiently
5. Pattern compatibility: Both patterns can coexist without confusion
6. CRITICAL: High relevance: Secondary pattern MUST be highly relevant to the first

**Benefits:**
- More efficient conversations (fewer turns)
- Feels more natural and intelligent
- Better user experience (less back-and-forth)

**Related:**
- TBD #20 (Pattern Chaining and Orchestration Engine)
- PATTERN_RUNTIME_ARCHITECTURE.md (pattern selection algorithm)

---
```

---

## Workflow for Feature Ideas

### 1. Capture Immediately
When idea comes up:
```
User: "I want to add X feature"
AI: "TBD: [captures idea in proper format]"
```

### 2. Discussion (Optional)
- Discuss trade-offs
- Explore alternatives
- Clarify requirements

### 3. Decision Point
User decides:
- **Implement now** → Create implementation plan
- **Implement later** → Leave in TBD.md
- **Reject** → Document why and remove

### 4. Implementation
If approved:
- Create detailed technical spec
- Add to implementation roadmap
- Follow vertical slicing workflow

---

## TBD Categories

### Design Decisions
- How should X work?
- What's the best approach for Y?
- Trade-offs between A and B?

### Feature Requests
- Add capability X
- Improve behavior Y
- Support use case Z

### Open Questions
- How do we handle edge case X?
- What happens when Y?
- Should we support Z?

### Constraints & Requirements
- System must do X
- Cannot do Y because Z
- Performance requirement: X

### Future Improvements
- Nice to have: X
- Could optimize: Y
- Consider adding: Z

---

## Numbering Convention

- Sequential numbering (1, 2, 3, ...)
- Never reuse numbers
- If item is implemented, mark as such but keep in file for reference

**Example:**
```markdown
### 25. Multi-Pattern Responses (IMPLEMENTED)
**Added**: 2025-11-06
**Implemented**: 2025-11-06 (Release 2.1)
**Status**: ✅ Complete

[Original content...]

**Implementation Notes:**
- Implemented in PatternSelector.select_patterns()
- Context continuity check prevents topic jumping
- Tests: test_pattern_selector.py
```

---

## Searching TBD

To find specific topics:
```bash
# Search for keyword
grep -i "pattern" docs/1_functional_spec/TBD.md

# List all TBD items
grep "^### [0-9]" docs/1_functional_spec/TBD.md

# Find pending items
grep -A 2 "PENDING\|TODO" docs/1_functional_spec/TBD.md
```

---

## Related Workflows

- **Development:** See `DEVELOPMENT_WORKFLOW.md`
- **Planning:** See `docs/2_technical_spec/Release2.1/PATTERN_ENGINE_IMPLEMENTATION.md`
- **Progress:** See `docs/2_technical_spec/Release2.1/TDD_PROGRESS.md`

---

**Last Updated:** 2025-11-06  
**Status:** Active guideline for all feature ideas
