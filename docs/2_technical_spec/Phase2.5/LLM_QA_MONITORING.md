# Phase 2.5: Semantic Evaluation Strategy

**Type:** Cross-Phase Infrastructure  
**Date:** 2025-11-05  
**Status:** Specification

---

## Purpose

Establish automated semantic evaluation for the conversational assessment agent to ensure quality, detect regressions, and validate behavior across development phases.

**Why Phase 2.5:** Evaluation infrastructure must be in place BEFORE Phase 3+ complexity (context extraction, recommendations) to prevent quality degradation and enable confident iteration.

---

## Problem Statement

### The Challenge

Traditional unit tests verify code correctness but fail for conversational AI:
- **Non-deterministic outputs:** Same input → different (but valid) responses
- **Semantic equivalence:** "Sales forecast accuracy is poor" ≈ "Forecast quality is low" ≈ "Predictions are often wrong"
- **Multi-turn context:** Evaluation must consider conversation history, not isolated turns
- **Subjective quality:** "Helpfulness," "clarity," "appropriateness" lack ground truth

### What We Need to Evaluate

**Phase 2 (Current):**
- Output discovery accuracy (did it identify the right output?)
- Edge assessment quality (are inferred ratings reasonable?)
- Evidence tier classification (correct tier assignment?)
- Bottleneck identification (MIN calculation correct?)

**Phase 3+ (Future):**
- Context extraction completeness (captured budget, timeline, visibility?)
- Recommendation relevance (pilots match bottleneck + constraints?)
- Feasibility assessment accuracy (gaps correctly identified?)

---

## Evaluation Strategy

### Three-Layer Approach

#### Layer 1: Deterministic Tests (Traditional)
**What:** Exact matching for algorithmic correctness  
**When:** Graph operations, MIN calculation, Bayesian aggregation  
**How:** Standard pytest assertions

**Examples:**
- MIN([⭐⭐, ⭐⭐⭐, ⭐]) = ⭐
- Bayesian score with evidence tiers 1,3,5 = expected value
- Graph node count after add/remove operations

**Coverage:** ~30% of system behavior

---

#### Layer 2: Semantic Similarity (Reference-Based)
**What:** Compare LLM outputs to expected semantic meaning  
**When:** Output discovery, rating inference, context extraction  
**How:** Embedding-based similarity + LLM-as-judge

**Approach:**

**2.1 Embedding Similarity (Fast, Cheap)**
- Use sentence transformers (e.g., `all-MiniLM-L6-v2`)
- Compute cosine similarity between actual and expected outputs
- Threshold: >0.85 = pass, 0.70-0.85 = review, <0.70 = fail

**Example:**
```
Input: "Our sales predictions are never accurate"
Expected: "Sales Forecast" (output_id: sales_forecast)
Actual: "Revenue Forecast" (output_id: revenue_forecast)
Similarity: 0.78 → REVIEW (semantically close but wrong output)
```

**2.2 LLM-as-Judge (Slower, More Accurate)**
- Use Gemini Flash as evaluator (same model, different prompt)
- Binary or 3-point scale (correct/incorrect/partial)
- Focused evaluation criteria per test case

**Example Prompt:**
```
Task: Evaluate if the agent correctly identified the output.

User said: "Sales forecasts are always wrong"
Agent identified: "Sales Forecast" (ID: sales_forecast)
Expected: "Sales Forecast" (ID: sales_forecast)

Question: Did the agent identify the correct output?
Answer: [CORRECT / INCORRECT / PARTIAL]
Reasoning: [brief explanation]
```

**Coverage:** ~50% of system behavior

---

#### Layer 3: Multi-Turn Conversation Evaluation
**What:** End-to-end conversation quality assessment  
**When:** Full assessment flows, user experience validation  
**How:** LLM-as-judge with conversation-level criteria

**Evaluation Dimensions:**

**3.1 Task Completion**
- Did the agent complete the assessment (all 4 edges rated)?
- Did it identify bottlenecks correctly?
- Did it handle user corrections appropriately?

**3.2 Interaction Quality**
- Clarity: Are questions clear and unambiguous?
- Efficiency: Minimal questions to reach conclusion?
- Naturalness: Does conversation flow naturally?

**3.3 Correctness**
- Output identification accuracy
- Rating inference reasonableness
- Evidence tier classification accuracy

**Approach:**
```
Evaluator Prompt:
- Input: Full conversation transcript + expected outcomes
- Output: Scores (1-5) for task completion, clarity, efficiency
- Reasoning: Brief explanation per dimension
```

**Coverage:** ~20% of system behavior (expensive, use sparingly)

---

## Implementation Architecture

### Test Data Structure

```
tests/
├── fixtures/
│   ├── conversations/
│   │   ├── sales_forecast_happy_path.json
│   │   ├── support_tickets_vague_input.json
│   │   └── finance_budget_multi_bottleneck.json
│   ├── expected_outputs/
│   │   ├── sales_forecast_expected.json
│   │   └── ...
│   └── evaluation_prompts/
│       ├── output_discovery_judge.txt
│       ├── rating_inference_judge.txt
│       └── conversation_quality_judge.txt
├── semantic/
│   ├── test_output_discovery.py
│   ├── test_rating_inference.py
│   ├── test_evidence_classification.py
│   └── test_conversation_flows.py
└── integration/
    └── test_end_to_end_scenarios.py
```

### Test Case Format

```json
{
  "test_id": "sales_forecast_001",
  "description": "User describes inaccurate sales forecasts",
  "conversation": [
    {"role": "user", "content": "Our sales forecasts are always wrong"},
    {"role": "assistant", "content": "..."}
  ],
  "expected_outcomes": {
    "output_identified": {
      "output_id": "sales_forecast",
      "output_name": "Sales Forecast",
      "confidence_threshold": 0.8
    },
    "edges_assessed": {
      "people_to_output": {"score": 2, "tier": 3},
      "tool_to_output": {"score": 1, "tier": 4},
      "process_to_output": {"score": 2, "tier": 2},
      "dependency_to_output": {"score": 3, "tier": 1}
    },
    "bottleneck": {
      "edge_type": "tool_to_output",
      "score": 1
    }
  },
  "evaluation_criteria": {
    "output_discovery": "exact_match",
    "rating_inference": "semantic_similarity",
    "conversation_quality": "llm_judge"
  }
}
```

---

## Evaluation Metrics

### Per-Layer Metrics

**Layer 1 (Deterministic):**
- Pass/Fail rate
- Code coverage
- Execution time

**Layer 2 (Semantic):**
- Embedding similarity distribution
- LLM-judge agreement rate
- False positive/negative rates

**Layer 3 (Conversation):**
- Task completion rate
- Average interaction quality score
- User experience proxy metrics

### Aggregate Metrics

**Quality Score:**
```
Quality = (Deterministic_Pass_Rate * 0.3) + 
          (Semantic_Pass_Rate * 0.5) + 
          (Conversation_Pass_Rate * 0.2)
```

**Regression Detection:**
- Track metrics over time
- Alert if quality drops >5% between commits
- Block deployment if quality <80%

---

## Tooling & Infrastructure

### Recommended Stack

**Embedding Models:**
- `sentence-transformers/all-MiniLM-L6-v2` (fast, good quality)
- Alternative: `sentence-transformers/all-mpnet-base-v2` (slower, better)

**LLM-as-Judge:**
- Gemini 2.5 Flash (same as production, cost-effective)
- Separate evaluation prompts from production prompts
- Cache evaluator responses to reduce cost

**Test Framework:**
- pytest for test execution
- Custom fixtures for conversation scenarios
- Parameterized tests for multiple scenarios

**CI/CD Integration:**
- Run Layer 1 (deterministic) on every commit
- Run Layer 2 (semantic) on PR creation
- Run Layer 3 (conversation) nightly or pre-release

---

## Cost Management

### Evaluation Budget

**Layer 1:** $0 (no API calls)  
**Layer 2:** ~$0.01 per test case (embedding + LLM judge)  
**Layer 3:** ~$0.05 per conversation (multi-turn LLM judge)

**Monthly Estimate:**
- 50 Layer 2 tests × 10 runs/month = $5
- 10 Layer 3 tests × 5 runs/month = $2.50
- **Total: ~$7.50/month**

### Optimization Strategies

1. **Cache LLM judge responses** (same input → same evaluation)
2. **Use embeddings first** (filter obvious failures before LLM judge)
3. **Batch evaluations** (reduce API overhead)
4. **Run expensive tests selectively** (nightly, not per-commit)

---

## Best Practices

### Prompt Engineering for Judges

**1. Binary or Low-Precision Scoring**
- Use CORRECT/INCORRECT/PARTIAL (not 1-100 scale)
- Reduces variability, improves consistency

**2. Clear Criteria Definitions**
```
CORRECT: Agent identified exact output with >0.8 confidence
PARTIAL: Agent identified semantically similar output
INCORRECT: Agent identified wrong output or failed to identify
```

**3. Split Complex Evaluations**
- Separate judges for output discovery, rating inference, conversation quality
- Combine results deterministically

**4. Add Examples to Prompts**
- Show 2-3 examples of CORRECT/INCORRECT cases
- Improves judge calibration

### Test Data Curation

**Coverage Strategy:**
- Happy path (clear, unambiguous inputs)
- Edge cases (vague, ambiguous, contradictory)
- Error handling (invalid inputs, API failures)
- Multi-turn complexity (refinements, corrections)

**Diversity:**
- 8 function domains (Sales, Finance, Operations, etc.)
- 4 edge types (People, Tool, Process, Dependency)
- 5 rating levels (⭐ to ⭐⭐⭐⭐⭐)

---

## Rollout Plan

### Phase 2 (Immediate)
- ✅ Layer 1: Deterministic tests for graph operations, MIN calc
- ✅ Layer 2: Semantic tests for output discovery
- ✅ Layer 2: LLM-judge for rating inference

### Phase 3 (Context Extraction)
- Add semantic tests for budget/timeline/visibility extraction
- Add conversation-level tests for context completeness

### Phase 4 (Recommendations)
- Add semantic tests for pilot relevance
- Add LLM-judge for recommendation quality
- Add end-to-end tests for full assessment → recommendation flow

---

## Success Criteria

**Phase 2 Readiness:**
✅ 20+ deterministic tests (graph, MIN, Bayesian)  
✅ 30+ semantic tests (output discovery, rating inference)  
✅ 5+ conversation tests (end-to-end flows)  
✅ CI/CD pipeline running all tests  
✅ Quality score >85%

**Long-Term Goals:**
- Detect regressions within 1 commit
- Reduce manual QA time by 70%
- Enable confident refactoring
- Support A/B testing of prompts

---

## Open Questions

**Q1:** Should we use a different LLM for evaluation (e.g., GPT-4) vs production (Gemini)?  
**A:** Start with same model (Gemini) to reduce costs. Upgrade if judge quality insufficient.

**Q2:** How do we handle LLM judge disagreement with human reviewers?  
**A:** Track disagreement rate. If >20%, refine judge prompts or add human-labeled examples.

**Q3:** What's the right balance between test coverage and cost?  
**A:** Start with 50 total tests (20 deterministic, 25 semantic, 5 conversation). Expand based on failure patterns.

---

## References

- [LLM-as-a-Judge Guide](https://www.evidentlyai.com/llm-guide/llm-as-a-judge)
- [LLM Evaluation Metrics](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)
- [Multi-Turn Agent Evaluation Survey](https://arxiv.org/abs/2503.22458)
- G-Eval Framework (NLG Evaluation using GPT-4)

---

**Document Status:** Ready for Review  
**Owner:** Technical Lead  
**Next Steps:** Implement Layer 1 + Layer 2 for Phase 2 outputs
