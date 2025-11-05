# Phase 2 Test Conversation Fixtures

**Purpose:** Test data for Phase 2 output discovery and assessment features

---

## Overview

These fixtures provide realistic conversation scenarios for testing:
- Output discovery from natural language
- Edge rating inference from user statements
- Evidence tier classification
- MIN calculation and bottleneck identification
- Conversation quality (clarity, efficiency, handling edge cases)

---

## Fixture Format

Each JSON file contains:
- **conversation:** Full turn-by-turn dialogue
- **expected_outcomes:** What the system should produce
  - Output identification (ID, name, confidence)
  - Edge assessments (score, confidence, tier, evidence)
  - Calculated quality (MIN score)
  - Bottlenecks identified
- **evaluation_criteria:** How to validate results
  - Methods: exact_match, semantic_similarity, llm_judge, deterministic
  - Success conditions

---

## Test Scenarios

### 1. sales_forecast_happy_path.json ✅
**Scenario:** Happy path - clear problem, cooperative user

**Coverage:**
- Clear output identification ("sales forecasts are always wrong")
- All 4 edge types assessed
- Multiple bottlenecks (system ⭐ + process ⭐)
- Evidence tiers 2-4

**Key Test:** Basic flow works end-to-end

---

### 2. support_tickets_vague_input.json ✅
**Scenario:** Vague input - user starts unclear, system refines

**Coverage:**
- Vague initial statement ("support is a disaster")
- Progressive refinement through questions
- Single bottleneck (process ⭐)
- Conversation quality assessment

**Key Test:** System handles ambiguity, asks clarifying questions

---

### 3. finance_budget_contradictory.json ✅
**Scenario:** Contradictory input - user changes mind

**Coverage:**
- Initial statement contradicted later
- Evidence weighting (later > earlier)
- Tier 3 overrides Tier 2
- Contradiction detection and resolution

**Key Test:** System handles contradictions, uses latest information

---

### 4. operations_multi_bottleneck.json ✅
**Scenario:** Multi-bottleneck - all edges equally poor

**Coverage:**
- All 4 edges rated ⭐⭐ (tied for MIN)
- Systemic issues across all dimensions
- Multiple bottlenecks identified
- Holistic recommendation needed

**Key Test:** System handles multiple bottlenecks, doesn't assume single issue

---

### 5. marketing_campaign_edge_case.json ✅
**Scenario:** Edge case - excellent execution, terrible dependency

**Coverage:**
- Extreme spread: ⭐⭐⭐⭐⭐, ⭐⭐⭐⭐⭐, ⭐⭐⭐⭐⭐, ⭐
- MIN calculation with extreme values
- Single critical bottleneck (dependency)
- Root cause type: Dependency Issue

**Key Test:** MIN correctly identifies single bad dependency despite excellent other factors

---

## Usage

### Unit Tests
```python
import json
from pathlib import Path

def load_fixture(name):
    path = Path(__file__).parent / "conversations" / f"{name}.json"
    with open(path) as f:
        return json.load(f)

def test_output_discovery():
    fixture = load_fixture("sales_forecast_happy_path")
    # Test output discovery logic
    assert discovered_output_id == fixture["expected_outcomes"]["output_identified"]["output_id"]
```

### Integration Tests
```python
def test_full_assessment_flow():
    fixture = load_fixture("support_tickets_vague_input")
    
    # Simulate conversation
    for turn in fixture["conversation"]:
        if turn["role"] == "user":
            response = agent.process_message(turn["content"])
    
    # Validate outcomes
    assert agent.identified_output == fixture["expected_outcomes"]["output_identified"]["output_id"]
    assert agent.calculated_quality == fixture["expected_outcomes"]["calculated_quality"]["min_score"]
```

### Semantic Evaluation (Phase 2.5)
```python
def test_rating_inference_quality():
    fixture = load_fixture("finance_budget_contradictory")
    
    # Run assessment
    result = agent.assess_output(fixture["conversation"])
    
    # Use LLM-as-judge
    judge_prompt = f"""
    Expected: {fixture["expected_outcomes"]["edges_assessed"]}
    Actual: {result.edges}
    
    Are the ratings semantically equivalent (within ±1 star)?
    """
    
    judgment = llm_judge.evaluate(judge_prompt)
    assert judgment == "CORRECT"
```

---

## Evaluation Methods

### exact_match
- **Use:** Output ID, deterministic calculations
- **Success:** Exact string/number match
- **Example:** `output_id == "sales_forecast"`

### semantic_similarity
- **Use:** Rating inference, evidence classification
- **Success:** Embedding similarity >0.85 OR within ±1 star
- **Example:** Expected ⭐⭐, Actual ⭐⭐⭐ = PASS (within tolerance)

### llm_judge
- **Use:** Conversation quality, contradiction handling
- **Success:** LLM evaluator returns CORRECT/PARTIAL/INCORRECT
- **Example:** "Did system handle contradiction appropriately?"

### deterministic
- **Use:** MIN calculation, bottleneck identification
- **Success:** Mathematical correctness
- **Example:** `MIN(2,1,1,2) == 1`

---

## Coverage Matrix

| Scenario | Output Discovery | Edge Rating | Evidence Tiers | MIN Calc | Bottlenecks | Edge Cases |
|----------|-----------------|-------------|----------------|----------|-------------|------------|
| Sales Forecast | ✅ Clear | ✅ All 4 | ✅ 2-4 | ✅ Multi | ✅ 2 tied | - |
| Support Tickets | ✅ Vague | ✅ All 4 | ✅ 2-3 | ✅ Single | ✅ 1 clear | Ambiguity |
| Finance Budget | ✅ Clear | ✅ All 4 | ✅ 2-3 | ✅ Single | ✅ 1 clear | Contradictions |
| Operations PMO | ✅ Clear | ✅ All 4 | ✅ 3 only | ✅ Multi | ✅ 4 tied | Systemic |
| Marketing Campaign | ✅ Clear | ✅ All 4 | ✅ 3-4 | ✅ Single | ✅ 1 critical | Extreme spread |

---

## Adding New Fixtures

**Template:**
```json
{
  "test_id": "function_scenario_###",
  "scenario": "Brief description",
  "description": "Detailed description",
  "conversation": [...],
  "expected_outcomes": {
    "output_identified": {...},
    "edges_assessed": {...},
    "calculated_quality": {...},
    "bottlenecks": [...]
  },
  "evaluation_criteria": {...}
}
```

**Guidelines:**
- Use realistic user language (not technical jargon)
- Include specific evidence keywords
- Cover different evidence tiers (1-5)
- Test edge cases and error conditions
- Document evaluation methods clearly

---

## Next Steps

1. **Phase 2 Implementation:** Use these fixtures for TDD
2. **Phase 2.5 Evaluation:** Build semantic tests around these scenarios
3. **Expand Coverage:** Add more edge cases as discovered
4. **Real User Data:** Eventually supplement with anonymized real conversations

---

**Status:** ✅ 5 fixtures complete  
**Coverage:** Happy path, vague input, contradictions, multi-bottleneck, edge cases  
**Ready for:** Phase 2 implementation
