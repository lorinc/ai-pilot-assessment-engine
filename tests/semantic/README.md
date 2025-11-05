# Semantic Evaluation Tests

**Purpose:** Evaluate conversational AI agent using semantic similarity and LLM-as-judge

---

## Overview

Traditional unit tests verify code correctness but fail for conversational AI:
- Non-deterministic outputs
- Semantic equivalence ("forecast is wrong" ≈ "predictions are inaccurate")
- Subjective quality (helpfulness, clarity)

This directory contains semantic evaluation infrastructure for Phase 2 features.

---

## Structure

```
tests/semantic/
├── __init__.py
├── README.md (this file)
├── conftest.py (pytest fixtures for semantic tests)
├── test_output_discovery.py
├── test_rating_inference.py
├── test_evidence_classification.py
├── test_conversation_quality.py
├── prompts/
│   ├── output_discovery_judge.txt
│   ├── rating_inference_judge.txt
│   └── evidence_tier_judge.txt
└── utils/
    ├── embedding_similarity.py
    ├── llm_judge.py
    └── test_helpers.py
```

---

## Evaluation Methods

### 1. Embedding Similarity (Fast, Cheap)

**Use:** Quick semantic comparison
**How:** Sentence transformers + cosine similarity
**Threshold:** >0.85 = pass, 0.70-0.85 = review, <0.70 = fail

```python
from tests.semantic.utils.embedding_similarity import compute_similarity

similarity = compute_similarity(
    "Sales forecasts are always wrong",
    "Revenue predictions are inaccurate"
)
assert similarity > 0.85  # Semantically equivalent
```

### 2. LLM-as-Judge (Slower, More Accurate)

**Use:** Complex evaluation criteria
**How:** Gemini Flash with evaluation prompts
**Output:** CORRECT / PARTIAL / INCORRECT + reasoning

```python
from tests.semantic.utils.llm_judge import evaluate_output_discovery

result = evaluate_output_discovery(
    user_description="Our sales forecasts are always wrong",
    agent_output_id="sales_forecast",
    expected_output_id="sales_forecast"
)
assert result.judgment == "CORRECT"
```

---

## Test Categories

### test_output_discovery.py
**What:** Can agent identify correct output from user description?
**Method:** Embedding similarity + LLM-as-judge
**Fixtures:** All 5 conversation fixtures

### test_rating_inference.py
**What:** Are inferred ratings reasonable given user statements?
**Method:** LLM-as-judge (within ±1 star tolerance)
**Fixtures:** All 5 conversation fixtures

### test_evidence_classification.py
**What:** Are evidence tiers correctly classified?
**Method:** LLM-as-judge
**Fixtures:** All 5 conversation fixtures

### test_conversation_quality.py
**What:** Is conversation flow natural and efficient?
**Method:** LLM-as-judge with conversation-level criteria
**Fixtures:** Vague input, contradictory scenarios

---

## Running Tests

### All Semantic Tests
```bash
pytest tests/semantic/ -v
```

### Specific Test File
```bash
pytest tests/semantic/test_output_discovery.py -v
```

### With Coverage
```bash
pytest tests/semantic/ --cov=src --cov-report=html
```

### Skip Expensive Tests (LLM-as-judge)
```bash
pytest tests/semantic/ -v -m "not expensive"
```

---

## Cost Management

**Embedding Similarity:** $0 (local model)
**LLM-as-Judge:** ~$0.01-0.02 per evaluation

**Estimated Monthly Cost:**
- 50 semantic tests × 10 runs = $5-10
- Run on PR creation, not every commit

**Optimization:**
- Cache LLM judge responses (same input = same eval)
- Use embeddings first (filter before LLM judge)
- Run expensive tests nightly, not per-commit

---

## Adding New Tests

### 1. Create Test File
```python
# tests/semantic/test_new_feature.py
import pytest
from tests.semantic.utils.llm_judge import evaluate_custom

def test_new_feature_semantic():
    # Load fixture
    fixture = load_fixture("scenario_name")
    
    # Run agent
    result = agent.process(fixture["conversation"])
    
    # Evaluate with LLM-as-judge
    judgment = evaluate_custom(
        expected=fixture["expected_outcomes"],
        actual=result,
        criteria="Is the result semantically correct?"
    )
    
    assert judgment.is_correct()
```

### 2. Create Evaluation Prompt (if needed)
```
# tests/semantic/prompts/new_feature_judge.txt
You are evaluating...

[Criteria]
[Examples]
[Response format]
```

### 3. Mark Expensive Tests
```python
@pytest.mark.expensive  # Skip in fast test runs
def test_expensive_llm_evaluation():
    ...
```

---

## Best Practices

### 1. Use Embeddings First
- Fast, free, good for filtering
- Only use LLM-as-judge for borderline cases

### 2. Clear Evaluation Criteria
- Define CORRECT/PARTIAL/INCORRECT precisely
- Include examples in prompts
- Use binary or 3-point scales (not 1-100)

### 3. Cache Aggressively
- Same input → same evaluation
- Store LLM judge responses
- Reduce API costs

### 4. Tolerance Ranges
- Ratings: ±1 star acceptable
- Similarity: >0.85 for pass, 0.70-0.85 review
- Don't expect perfection

---

## Integration with CI/CD

### On Every Commit
- Run deterministic tests only (unit tests)
- Skip semantic tests (too slow/expensive)

### On PR Creation
- Run embedding similarity tests (fast, free)
- Run critical LLM-as-judge tests (subset)

### Nightly
- Run full semantic test suite
- Generate quality report
- Alert if quality drops >5%

---

## Troubleshooting

### High Failure Rate
- Check if evaluation criteria too strict
- Review LLM judge prompts (add examples)
- Verify fixtures have correct expected outcomes

### High Cost
- Cache LLM responses
- Use embeddings first
- Run expensive tests less frequently

### Flaky Tests
- LLM-as-judge can be non-deterministic
- Run multiple times, use majority vote
- Set temperature=0 for consistency

---

## Future Enhancements

- [ ] Multi-turn conversation evaluation
- [ ] User experience scoring
- [ ] A/B testing framework for prompts
- [ ] Automated regression detection
- [ ] Quality dashboard

---

**Status:** Infrastructure ready, tests to be implemented in Phase 2  
**Dependencies:** sentence-transformers, Gemini API access  
**Owner:** Technical Lead
