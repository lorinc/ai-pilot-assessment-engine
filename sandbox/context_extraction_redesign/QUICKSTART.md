# Quickstart Guide

Get the testbed running in 2 steps.

## Step 1: Ensure GCP Credentials

The testbed uses the existing project's Gemini/Vertex AI setup. Make sure you have:

1. GCP credentials configured (gcloud auth or service account)
2. Proper `.env` file in project root with GCP settings

## Step 2: Run Tests

```bash
python3 test_runner.py
```

## What You'll See

The test runner will:
1. Run 10 test cases (simple → complex)
2. Show progress for each test
3. Display accuracy scores
4. Print summary with pass/fail counts
5. Save detailed results to `test_results.json`

## Example Output

```
================================================================================
Test 1/10: Simple Assessment (Simple)
================================================================================
Message: The data quality is 3 stars.

PASS: 95.0% accuracy

================================================================================
Test 2/10: The Sentence That Broke Us (Complex)
================================================================================
Message: I think data quality in our CRM is bad because the sales team hates to document their work.

PASS: 87.5% accuracy

Differences:
  assessments: {'score': 0.8, 'missing': None, 'extra': ['implicit rating off by 1']}
...
```

## Iterating

1. **Check results**: Look at failed tests in output
2. **Modify extractor**: Edit `extractor.py` system prompt
3. **Re-run tests**: `python3 test_runner.py`
4. **Compare**: Check if accuracy improved
5. **Repeat**: Until satisfied with results

## Files Overview

- `schemas.py` - Data structures for extracted context
- `test_cases.py` - 10 test cases with expected outputs
- `extractor.py` - Outlines-based extraction engine
- `test_runner.py` - Test runner with metrics
- `validate_setup.py` - Check everything is configured
- `test_results.json` - Detailed results (created after first run)

## Troubleshooting

**Import errors?**
- Make sure you're using the project's venv: `source venv/bin/activate`
- Or run from project root

**GCP auth errors?**
```bash
gcloud auth application-default login
```

**Want to test one case?**
```python
from extractor import create_extractor

extractor = create_extractor()
result = extractor.extract("Your test message here")
print(result)
```

## Cost Estimate

Using Gemini (default: `gemini-1.5-flash`):
- ~10 test cases × ~1000 tokens each = ~10,000 tokens
- Input: ~$0.0001 (10K tokens × $0.075/1M)
- Output: ~$0.0003 (10K tokens × $0.30/1M)
- **Total: ~$0.0004 per run** (extremely cheap for iteration)

To use `gemini-1.5-pro` for better accuracy:
- Edit `.env`, change `GEMINI_MODEL=gemini-1.5-pro`
- Cost: ~$0.01 per run
