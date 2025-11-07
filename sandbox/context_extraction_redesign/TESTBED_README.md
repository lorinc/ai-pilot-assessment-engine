# Context Extraction Testbed

Minimal testbed for iteratively improving LLM-based context extraction using Outlines.

## Structure

```
sandbox/context_extraction_redesign/
├── schemas.py          # Pydantic models for extracted context
├── test_cases.py       # 10 test cases with expected outputs
├── extractor.py        # Outlines-based extraction engine
├── test_runner.py      # Test runner with accuracy metrics
├── requirements.txt    # Python dependencies
└── TESTBED_README.md   # This file
```

## Setup

**No additional setup needed!** The testbed uses the existing project's Gemini/Vertex AI configuration.

Just ensure:
1. GCP credentials are configured (`gcloud auth application-default login`)
2. Project `.env` file has proper GCP settings

## Usage

### Run all tests

```bash
python test_runner.py
```

This will:
- Run all 10 test cases
- Show progress and results for each test
- Print summary with pass/fail counts and accuracy scores
- Save detailed results to `iterations/test_results_YYYYMMDD_HHMMSS.json`

### Use extractor programmatically

```python
from extractor import create_extractor

# Create extractor
extractor = create_extractor()

# Extract context from a message
context = extractor.extract("Our CRM data quality is bad because sales team hates documentation.")

# Access extracted information
print(f"Outputs: {context.outputs}")
print(f"Teams: {context.teams}")
print(f"Assessments: {context.assessments}")
print(f"Root causes: {context.root_causes}")
```

### Iterate on improvements

1. **Modify system prompt** in `extractor.py` to improve extraction
2. **Adjust schemas** in `schemas.py` to capture different information
3. **Add test cases** in `test_cases.py` for new scenarios
4. **Run tests** to measure improvement
5. **Compare results** in `test_results.json`

## Test Cases

10 test cases covering:
- **Simple** (1 test): Explicit ratings, minimal context
- **Medium** (1 test): Positive assessments, team strengths
- **Complex** (8 tests): Multi-entity, implicit ratings, dependencies, root causes

## Metrics

- **Accuracy Score**: 0.0 to 1.0 (F1 score across all fields)
- **Pass Threshold**: 70% accuracy
- **Field-level Scores**: Precision/recall for each field (outputs, teams, systems, etc.)

## Iteration Workflow

1. Run baseline: `python test_runner.py`
2. Identify failures in output
3. Modify extractor prompt or schemas
4. Re-run tests (creates new timestamped file in `iterations/`)
5. Compare accuracy improvements between runs
6. Repeat until satisfied

**All test results are saved in `iterations/` with timestamps for tracking progress over time.**

## Current Status

- ✅ Schemas defined
- ✅ Test cases created (10 cases)
- ✅ Extractor implemented (uses project's LLMClient + Gemini)
- ✅ Test runner with metrics
- ✅ Baseline run complete (42.9% avg accuracy, 2/10 passed)
- ✅ Results saved in `iterations/` with timestamps

## Notes

- Uses project's Gemini model (default: `gemini-1.5-flash`)
- Extremely cheap: ~$0.0004 per full test run
- Can switch to `gemini-1.5-pro` in `.env` for better accuracy
- All work stays in this sandbox folder
- No changes to main codebase during iteration
