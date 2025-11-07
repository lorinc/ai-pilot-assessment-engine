# Test Iterations

This folder contains timestamped test results from each run.

## File Naming Convention

`test_results_YYYYMMDD_HHMMSS.json`

Example: `test_results_20251107_105309.json` = Run on Nov 7, 2025 at 10:53:09

## Comparing Iterations

To compare two runs:

```bash
# Show summary stats
jq '.[] | {test_id, test_name, accuracy_score}' test_results_20251107_105309.json

# Compare accuracy between two runs
diff <(jq '.[] | {id: .test_id, acc: .accuracy_score}' run1.json) \
     <(jq '.[] | {id: .test_id, acc: .accuracy_score}' run2.json)
```

## Tracking Progress

Each file contains:
- Test results with pass/fail status
- Accuracy scores per test
- Detailed differences between expected and actual
- Full expected and actual outputs

Use these to:
1. Track accuracy improvements over time
2. Identify which tests improve/regress
3. Debug specific extraction issues
4. Document what prompt changes helped
