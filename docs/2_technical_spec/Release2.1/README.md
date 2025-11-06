# Release 2.1: Pattern Engine Foundation

**Type:** UX Infrastructure - Conversation Pattern System  
**Status:** Specification  
**Date:** 2025-11-06

---

## Overview

Build production-ready pattern engine that enables dynamic, context-aware conversation management. This infrastructure is **required** by Release 2.2 (Situational Awareness) and Release 2.5 (Semantic Evaluation).

**Why 2.1:** Situational Awareness explicitly depends on pattern selection, trigger detection, and knowledge tracking—all provided by the pattern engine.

---

## Quick Links

### Core Documentation
- **[Pattern Format](PATTERN_FORMAT.md)** - YAML specification for dual-use (runtime + testing)
- **[Runtime Architecture](PATTERN_RUNTIME_ARCHITECTURE.md)** - Performance-optimized implementation
- **[UX Principles](UX_PRINCIPLES.md)** - 15 foundational conversation principles
- **[Implementation Plan](PATTERN_ENGINE_IMPLEMENTATION.md)** - Technical implementation plan

### Pattern Library Reference
- **[Pattern Overview](PATTERN_OVERVIEW.md)** - High-level summary of pattern categories
- **[Composition Strategy](PATTERN_COMPOSITION_STRATEGY.md)** - How to scale from atomic to composed patterns
- **[Comprehensive Summary](COMPREHENSIVE_SUMMARY.md)** - Complete inventory (38 triggers, 74 behaviors, 28 dimensions)
- **[Review Checklist](REVIEW_CHECKLIST.md)** - QA checklist for pattern validation

### Data Files
- **Behaviors:** `data/patterns/behaviors/atomic_behaviors.yaml` (77 behaviors)
- **Triggers:** `data/patterns/triggers/atomic_triggers.yaml` (40+ triggers)
- **Knowledge:** `data/patterns/knowledge_dimensions.yaml` (28 dimensions)

### Source Material
- **Sandbox:** `sandbox/conversation_ux_exercise/` - Design exploration and prototypes (archived)

---

## What Gets Built

### Week 1: Core Pattern System
**Goal:** Load and manage pattern library

**Deliverables:**
- `src/patterns/pattern_loader.py` - Load YAML → runtime objects
- `src/patterns/knowledge_tracker.py` - Track user/system knowledge state
- `src/patterns/trigger_detector.py` - Detect triggers from user messages
- Pattern data structure and validation
- Unit tests for pattern loading

### Week 2: Behavior Library & Selection
**Goal:** Implement pattern selection algorithm

**Deliverables:**
- `data/patterns/behaviors/` - 77 atomic behaviors (migrated from sandbox)
- `data/patterns/triggers/` - 40+ triggers by type
- `src/patterns/pattern_selector.py` - Score patterns by situation affinity
- `src/patterns/llm_integration.py` - Inject patterns into LLM prompts
- Integration tests for pattern selection

### Week 3: Testing Infrastructure
**Goal:** Enable semantic and behavioral testing

**Deliverables:**
- `tests/patterns/semantic/` - LLM-as-judge test framework
- `tests/patterns/behavioral/` - State assertion tests
- `tests/patterns/integration/` - End-to-end conversation scenarios
- Pattern validation pipeline
- CI/CD integration

---

## Key Components

### 1. Pattern Format (Dual-Use)
**Purpose:** Single YAML format for both runtime behavior AND test validation

**Structure:**
```yaml
pattern_id: "PATTERN_001_WELCOME_FIRST_TIME"
category: "onboarding"
trigger:
  type: "system_reactive"
  conditions: {...}
behavior:
  response_template: "..."
  teaches_user: [...]
tests:
  semantic: [...]
  behavioral: [...]
```

### 2. Knowledge Tracking
**Two dimensions:**
- **User Knowledge:** What user knows about system (purpose, features, model)
- **System Knowledge:** What system knows about user (outputs, context, progress)

**Replaces:** Global phase/release logic

### 3. Trigger Detection
**Four types:**
- **User-Explicit:** Direct requests ("Where are we?")
- **User-Implicit:** Inferred needs (confusion, contradiction)
- **System-Proactive:** Opportunity-driven (extract context naturally)
- **System-Reactive:** State-based (first message, milestone reached)

### 4. Pattern Selection
**Algorithm:**
1. Detect triggers from user message
2. Filter patterns by prerequisites (knowledge, state, data)
3. Score by situation affinity (if situational awareness active)
4. Apply priority resolution (critical > high > medium > low)
5. Return top N patterns for LLM prompt

### 5. Runtime Architecture
**Performance-optimized:**
- **Pattern Index:** In-memory hash maps (~50-100 KB)
- **Pattern Cache:** LRU cache for hot patterns (~500 KB)
- **Knowledge State:** Bit flags for boolean knowledge (8 bytes vs 100+ bytes)
- **Pattern Matching:** <5ms overhead (LLM is bottleneck at 500-2000ms)

---

## Pattern Categories

**10 categories, 77 atomic behaviors:**

1. **Onboarding** - First-time user welcome, trust building
2. **Discovery** - Output identification, problem refinement
3. **Assessment** - Factor rating, evidence collection
4. **Context Extraction** - Timeline, budget, visibility (agenda-driven)
5. **Navigation** - Status queries, progress milestones
6. **Education** - Just-in-time feature explanations
7. **Analysis** - Bottleneck identification, root cause categorization
8. **Recommendation** - Pilot suggestions, feasibility checks
9. **Error Recovery** - Contradiction handling, confusion recovery
10. **Meta** - Review, edit, export, challenge assumptions

---

## Success Criteria

### Functional Requirements
✅ Pattern library loaded and validated (77 behaviors, 40 triggers, 28 dimensions)  
✅ Trigger detection working for all 4 types  
✅ Knowledge state tracking operational  
✅ Pattern selection algorithm functional  
✅ **LLM prompt integration with selective loading (CRITICAL)**  
✅ 20+ semantic tests passing (LLM-as-judge)  
✅ 30+ behavioral tests passing (state assertions)  
✅ 5+ integration tests passing (end-to-end scenarios)  
✅ Pattern matching overhead <5ms

### Cost Efficiency Requirements (MANDATORY)
✅ **Selective context loading implemented**  
✅ **Token usage ≤ 310 tokens/turn** (vs 9,747 full YAML)  
✅ Extract only: goal + template + relevant knowledge + recent history  
✅ Never send full YAML to LLM  
✅ Truncate long values in knowledge state  
✅ Limit conversation history to last 3 turns  
✅ **Cost target: ~$0.000047/turn** (vs $0.0015 without optimization)  
✅ **Annual savings: $16,986 at scale** (100K conversations/month)

---

## Dependencies

**Requires:**
- Release 2 complete (graph operations, conversation orchestrator)

**Enables:**
- Release 2.2 (Situational Awareness needs pattern selection)
- Release 2.5 (Semantic Evaluation needs test infrastructure)

**Blocks:**
- Release 2.2 cannot start without pattern engine
- Release 3 conversation quality depends on patterns

---

## Data Migration

### From Sandbox to Production

**Documentation:**
```
sandbox/conversation_ux_exercise/PATTERN_FORMAT.md
  → docs/2_technical_spec/Release2.1/PATTERN_FORMAT.md

sandbox/conversation_ux_exercise/PATTERN_RUNTIME_ARCHITECTURE.md
  → docs/2_technical_spec/Release2.1/PATTERN_RUNTIME_ARCHITECTURE.md

sandbox/conversation_ux_exercise/WHAT_MAKES_CONVERSATION_GOOD.md
  → docs/2_technical_spec/Release2.1/UX_PRINCIPLES.md
```

**Data Files:**
```
sandbox/conversation_ux_exercise/atomic_behaviors.yaml
  → data/patterns/behaviors/*.yaml (split by category)

sandbox/conversation_ux_exercise/atomic_triggers.yaml
  → data/patterns/triggers/*.yaml (split by type)

sandbox/conversation_ux_exercise/generated_knowledge_dimensions.yaml
  → data/patterns/knowledge_dimensions.yaml
```

**Code:**
```
New implementation in src/patterns/
(sandbox was design exploration only)
```

---

## Timeline

**Duration:** 3 weeks  
**Parallel with:** Release 2 completion  
**Start:** After Release 2 core functionality stable

**Week-by-week:**
- **Week 1:** Core pattern system (loading, validation, knowledge tracking)
- **Week 2:** Behavior library & selection (77 behaviors, selection algorithm)
- **Week 3:** Testing infrastructure (semantic + behavioral + integration)

---

## Cost Estimate

**Development:** 3 weeks (1 engineer)  
**Infrastructure:** No additional cost (uses existing LLM)  
**Testing:** ~$5-10/month for LLM-as-judge semantic tests

---

## Related Documents

- **Functional Spec:** `docs/1_functional_spec/SITUATIONAL_AWARENESS.md`
- **Release 2.2:** `docs/2_technical_spec/Release2.2/` - Depends on this release
- **Release 2.5:** `docs/2_technical_spec/Release2.5/` - Uses test infrastructure
- **Sandbox:** `sandbox/conversation_ux_exercise/` - Design exploration archive

---

**Owner:** Technical Lead  
**Priority:** High - Blocks Release 2.2 and 2.5  
**Status:** Ready to implement
