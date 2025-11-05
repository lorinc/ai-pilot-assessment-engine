# Phase 2.5: Semantic Evaluation Infrastructure

**Type:** Cross-Phase Quality Assurance  
**Status:** Specification  
**Date:** 2025-11-05

---

## Overview

Automated semantic evaluation strategy for the conversational assessment agent using LLM-as-judge, embedding similarity, and deterministic tests.

**Why 2.5:** Quality infrastructure must exist BEFORE adding complexity in Phase 3+.

---

## Quick Links

- **[Semantic Evaluation Spec](SEMANTIC_EVALUATION_SPEC.md)** - Full functional/technical specification

---

## What Gets Built

### Three-Layer Evaluation

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

✅ 55+ total tests across 3 layers  
✅ Quality score >85%  
✅ CI/CD pipeline operational  
✅ Regression detection within 1 commit  
✅ Manual QA time reduced by 70%

---

## Next Steps

1. Review specification
2. Set up test infrastructure (fixtures, prompts)
3. Implement Layer 1 tests (deterministic)
4. Implement Layer 2 tests (semantic)
5. Implement Layer 3 tests (conversation)
6. Integrate into CI/CD

---

**Owner:** Technical Lead  
**Dependencies:** Phase 2 in progress  
**Timeline:** Implement alongside Phase 2 (parallel track)
