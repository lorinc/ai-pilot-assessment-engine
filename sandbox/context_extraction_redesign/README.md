# Context Extraction Redesign - Sandbox

**Date:** 2025-11-06  
**Status:** EXPLORATION (Not implemented)  
**Purpose:** Design and test LLM-based business context extraction to replace atomic triggers

---

## The Problem

**User says:** "I think data quality in our CRM is bad because the sales team hates to document their work."

**What we need to extract:**
1. **Output:** CRM data quality
2. **Assessment:** "bad" (implicit 1-2 stars)
3. **Team:** Sales team
4. **System:** CRM
5. **Process:** Sales documentation process
6. **Root Cause:** Team execution issue (hate to document)
7. **Dependency Chain:** Documentation process → CRM data quality
8. **Sentiment:** Negative ("hates", "bad")

**What our current atomic triggers capture:**
- Maybe `T_MENTION_PROBLEM` fires
- Maybe `T_MENTION_TEAM` fires
- **We lose 90% of the information**

---

## Current Architecture (Broken)

```
User Message
    ↓
Atomic Triggers (keyword matching)
    ↓
T_MENTION_PROBLEM, T_MENTION_TEAM fire
    ↓
Lost: Output, Assessment, System, Process, Root Cause, Dependencies
```

**Problems:**
- ❌ One-dimensional (each trigger captures one thing)
- ❌ Keyword-based (not semantic)
- ❌ Information loss (90% of context lost)
- ❌ Cannot handle complex sentences
- ❌ Cannot extract relationships

---

## Proposed Architecture

```
User Message
    ↓
LLM Business Context Extractor
    ↓
Structured BusinessContext object
    ↓
{
    outputs: [Output],
    teams: [Team],
    systems: [System],
    processes: [Process],
    assessments: [Assessment],
    dependencies: [Dependency],
    root_causes: [RootCause]
}
    ↓
Intent Detection (for routing)
    ↓
Route to handler with FULL context
```

**Benefits:**
- ✅ Multi-dimensional (extract everything in one pass)
- ✅ Semantic understanding (LLM comprehension)
- ✅ No information loss (capture all entities and relationships)
- ✅ Handles complex sentences naturally
- ✅ Extracts relationships (dependencies, root causes)

---

## Design Questions to Answer

### 1. Extraction Granularity
- **Option A:** Extract everything in one LLM call (single prompt)
- **Option B:** Multi-stage extraction (entities first, then relationships)
- **Option C:** Streaming extraction (extract as we go)

### 2. Schema Design
- What entities do we need? (Output, Team, System, Process, etc.)
- What relationships? (Dependencies, Root Causes, etc.)
- How to handle ambiguity? (Multiple interpretations)
- How to handle partial information? (User says "CRM" but not which output)

### 3. Integration with Intent Detection
- **Option A:** Extract context first, then detect intent
- **Option B:** Detect intent first, then extract relevant context
- **Option C:** Do both in parallel

### 4. Trigger Replacement Strategy
- **Option A:** Replace all triggers with LLM extraction (clean slate)
- **Option B:** Keep simple triggers (greetings), add LLM for complex context
- **Option C:** Hybrid (triggers for fast path, LLM for fallback)

### 5. Performance & Cost
- How many LLM calls per message?
- Can we batch multiple messages?
- Caching strategy?
- Fallback if LLM fails?

---

## Testbed Structure

This sandbox contains:

1. **`PROBLEM_STATEMENT.md`** - Detailed problem analysis
2. **`DESIGN_OPTIONS.md`** - Alternative approaches with trade-offs
3. **`SCHEMA.md`** - Proposed entity and relationship schemas
4. **`EXAMPLES.md`** - Test cases with expected extractions
5. **`prototype_extractor.py`** - Working prototype for testing
6. **`test_extraction.py`** - Tests for extraction accuracy
7. **`INTEGRATION_PLAN.md`** - How to integrate with existing system

---

## Workflow

1. **Define Schema** - What entities and relationships do we need?
2. **Create Examples** - Test cases with expected outputs
3. **Prototype** - Build working extractor
4. **Test** - Validate extraction accuracy
5. **Iterate** - Refine based on test results
6. **Decide** - Choose best approach
7. **Integrate** - Plan integration with main system

---

## Success Criteria

**Extraction Accuracy:**
- ✅ 90%+ accuracy on entity extraction (outputs, teams, systems)
- ✅ 80%+ accuracy on relationship extraction (dependencies, root causes)
- ✅ Handles complex multi-entity sentences
- ✅ Handles ambiguous/partial information gracefully

**Performance:**
- ✅ <500ms per message (including LLM call)
- ✅ Reasonable cost (Gemini pricing)
- ✅ Caching for repeated entities

**Integration:**
- ✅ Clean separation from intent detection
- ✅ Backward compatible (can coexist with triggers during transition)
- ✅ Easy to test (structured output)

---

## Next Steps

1. Create `PROBLEM_STATEMENT.md` with detailed analysis
2. Create `SCHEMA.md` with entity/relationship definitions
3. Create `EXAMPLES.md` with 20+ test cases
4. Build `prototype_extractor.py`
5. Test and iterate

---

**Status:** Ready for exploration  
**Owner:** To be determined  
**Timeline:** TBD (depends on priority vs Day 13)
