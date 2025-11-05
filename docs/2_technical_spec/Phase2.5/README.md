# Phase 2.5: UX & Quality Infrastructure

**Type:** Cross-Phase Quality & Conversation Management  
**Status:** Specification  
**Date:** 2025-11-05

---

## Overview

Two parallel tracks that must exist BEFORE Phase 3 complexity:

1. **Situational Awareness** - Replace broken phase logic with dynamic conversation management
2. **Semantic Evaluation** - Automated quality assurance using LLM-as-judge

**Why 2.5:** Quality and UX infrastructure must exist BEFORE adding complexity in Phase 3+.

---

## Quick Links

### Situational Awareness
- **[Implementation Plan](SITUATIONAL_AWARENESS_IMPLEMENTATION.md)** - High-level implementation plan
- **[Full Design Spec](../../1_functional_spec/SITUATIONAL_AWARENESS.md)** - Complete functional specification
- **[Appendix: Design Rationale](appendix/NO_GLOBAL_PHASES.md)** - Why global phases are wrong
- **[Appendix: Code Audit](appendix/PHASE_LOGIC_AUDIT.md)** - Current violations and migration

### Semantic Evaluation
- **[User Interaction Patterns](USER_INTERACTION_PATTERNS.md)** - Pattern-based conversation system
- **[LLM QA Monitoring](LLM_QA_MONITORING.md)** - Quality monitoring strategy

---

## What Gets Built

### Track 1: Situational Awareness (4 weeks)

**Replace global phase logic with dynamic composition model**

**Week 1: Core Infrastructure**
- `SituationalAwareness` class with 8 dimensions
- Remove `phase` property from session
- Composition always sums to 100%

**Week 2: Pattern Integration**
- Add `situation_affinity` to behaviors
- Pattern selection algorithm
- LLM prompt integration

**Week 3: Intent Detection**
- Replace phase routing with intent detection
- Enable non-linear conversation
- Multi-output support

**Week 4: Refinement**
- Tune weights and decay rates
- Performance optimization
- Documentation

**Deliverables:**
- No global phase logic
- Dynamic pattern selection
- User agency preserved
- Non-linear conversation flows

---

### Track 2: Semantic Evaluation (Parallel)

**Three-Layer Evaluation**

**Layer 1: Deterministic Tests (30%)**
- Graph operations (add/remove nodes/edges)
- MIN calculation correctness
- Bayesian aggregation math
- Traditional pytest assertions

**Layer 2: Semantic Similarity (50%)**
- Output discovery accuracy (embedding + LLM-judge)
- Rating inference quality (LLM-judge)
- Evidence tier classification (LLM-judge)
- Reference-based evaluation

**Layer 3: Conversation Quality (20%)**
- End-to-end task completion
- Interaction quality (clarity, efficiency, naturalness)
- Multi-turn conversation flows
- LLM-as-judge with conversation-level criteria

---

## Key Concepts

### LLM-as-Judge

Use an LLM (Gemini Flash) to evaluate agent outputs against expected behavior:

```
Evaluator Prompt:
  Task: Did the agent identify the correct output?
  User said: "Sales forecasts are always wrong"
  Agent identified: "Sales Forecast"
  Expected: "Sales Forecast"
  
  Answer: CORRECT / INCORRECT / PARTIAL
  Reasoning: [brief explanation]
```

**Benefits:**
- Handles semantic equivalence ("forecast accuracy is poor" ≈ "predictions are wrong")
- Evaluates subjective qualities (clarity, helpfulness)
- Scales with complexity (no manual labeling needed)

**Challenges:**
- Non-deterministic (same input may get different scores)
- Requires careful prompt engineering
- Costs ~$0.01-0.05 per evaluation

---

## Evaluation Metrics

### Quality Score
```
Quality = (Deterministic * 0.3) + (Semantic * 0.5) + (Conversation * 0.2)
Target: >85%
```

### Per-Layer Metrics
- **Deterministic:** Pass/fail rate, code coverage
- **Semantic:** Embedding similarity, LLM-judge agreement
- **Conversation:** Task completion, interaction quality scores

---

## Cost Estimate

**Monthly Evaluation Budget:**
- Layer 1 (Deterministic): $0
- Layer 2 (Semantic): ~$5 (50 tests × 10 runs)
- Layer 3 (Conversation): ~$2.50 (10 tests × 5 runs)
- **Total: ~$7.50/month**

**Optimization:**
- Cache LLM judge responses
- Use embeddings first (filter before LLM judge)
- Run expensive tests nightly (not per-commit)

---

## Test Coverage Strategy

### Phase 2 (Immediate)
- 20+ deterministic tests (graph, MIN, Bayesian)
- 30+ semantic tests (output discovery, rating inference)
- 5+ conversation tests (end-to-end flows)

### Phase 3+ (Future)
- Context extraction tests (budget, timeline, visibility)
- Recommendation relevance tests
- Feasibility assessment tests

---

## Tooling

**Embedding Models:**
- `sentence-transformers/all-MiniLM-L6-v2` (fast, good quality)

**LLM-as-Judge:**
- Gemini 2.5 Flash (same as production)
- Separate evaluation prompts

**Test Framework:**
- pytest with custom fixtures
- Parameterized tests for scenarios
- CI/CD integration

---

## CI/CD Integration

**On Every Commit:**
- Run Layer 1 (deterministic) - fast, free

**On PR Creation:**
- Run Layer 2 (semantic) - moderate cost

**Nightly / Pre-Release:**
- Run Layer 3 (conversation) - expensive

**Quality Gate:**
- Block deployment if quality <80%
- Alert if quality drops >5% between commits

---

## Success Criteria

### Situational Awareness
✅ No global phase logic in codebase  
✅ Situation always sums to 100%  
✅ User can assess multiple outputs simultaneously  
✅ User can get recommendations at any confidence level  
✅ Pattern selection reflects situation  
✅ Conversation flows naturally (no forced transitions)

### Semantic Evaluation
✅ 55+ total tests across 3 layers  
✅ Quality score >85%  
✅ CI/CD pipeline operational  
✅ Regression detection within 1 commit  
✅ Manual QA time reduced by 70%

---

## Next Steps

### Situational Awareness Track
1. Review implementation plan
2. Week 1: Core infrastructure
3. Week 2: Pattern integration
4. Week 3: Intent detection
5. Week 4: Refinement

### Semantic Evaluation Track (Parallel)
1. Review specification
2. Set up test infrastructure (fixtures, prompts)
3. Implement Layer 1 tests (deterministic)
4. Implement Layer 2 tests (semantic)
5. Implement Layer 3 tests (conversation)
6. Integrate into CI/CD

---

**Owner:** Technical Lead  
**Dependencies:** Phase 2 in progress  
**Timeline:** 4 weeks parallel tracks alongside Phase 2
