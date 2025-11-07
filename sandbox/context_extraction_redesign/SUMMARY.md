# Context Extraction Testbed - Summary

## Final Results

**Best Approach: Iteration 3 - Conversational + Placeholders**
- **Accuracy:** 66.8%
- **Pass Rate:** 6/10 tests (60%)
- **File:** `iterations/test_results_20251107_110434.json`

## Journey Overview

### 7 Iterations Tested

| # | Approach | Accuracy | Pass Rate | Outcome |
|---|----------|----------|-----------|---------|
| 1 | Baseline (minimal) | 42.9% | 2/10 | Starting point |
| 2 | Detailed rules | 61.2% | 4/10 | +18.3pp ✅ |
| **3** | **Conversational + placeholders** | **66.8%** | **6/10** | **Best** ⭐ |
| 4 | Too verbose | 66.2% | 6/10 | Regression |
| 5 | Minimal schema-driven | 51.1% | 2/10 | -15.7pp ❌ |
| 6 | Balanced schema-driven | 49.5% | 3/10 | Still too minimal |
| 7 | Two-pass triplets | 22.9% | 1/10 | Catastrophic failure ❌❌ |

### Key Milestones

1. **Switched from OpenAI to Gemini** - Uses project's existing LLMClient
2. **Added placeholder strategy** - Handles ambiguous references gracefully
3. **Conversational philosophy** - "Extract + ask for clarification"
4. **Tested schema-driven approach** - Didn't work without constrained generation
5. **Tested two-pass approach** - Failed dramatically

## What Works ✅

1. **Conversational philosophy** - Extract what you can, ask for clarification
2. **Placeholder strategy** - `[unclear_output]`, `[team_they_refer_to]` for ambiguous refs
3. **Concrete examples** - 3-4 full examples covering edge cases
4. **Naming conventions** - Explicit rules about underscores, exact names
5. **Balanced prompt length** - ~3000-5000 chars optimal
6. **JSON format** - Stick with what Gemini knows

## What Doesn't Work ❌

1. **Too minimal prompts** - Schema alone isn't enough (Iter 5-6)
2. **Too verbose prompts** - Diminishing returns after ~5000 chars (Iter 4)
3. **Custom formats** - Triplets/XML worse than JSON (Iter 7)
4. **Multi-pass extraction** - Loses context (Iter 7)
5. **"Only explicit" restriction** - Too conservative, misses implied info (Iter 1)

## Test Results Breakdown

### Passing Tests (6/10)
1. ✅ **Simple Assessment** (85.7%) - "The data quality is 3 stars"
2. ✅ **The Sentence That Broke Us** (71.4%) - Complex multi-entity extraction
3. ✅ **Implicit Assessment** (85.7%) - Infers rating from "blind to production issues"
4. ✅ **Positive Assessment** (100%) - "Customer support team is excellent"
5. ✅ **Ambiguous Reference** (85.7%) - Handles "it" and "they" with placeholders
6. ✅ **Partial Information** (85.7%) - "I want to work on sales forecasting"

### Failing Tests (4/10)
1. ❌ **Multi-Output Dependency Chain** (43.8%) - Cascading outputs still challenging
2. ❌ **Team + Process + System** (42.9%) - Output naming inconsistencies
3. ❌ **Multiple Systems** (42.9%) - Complex data flows
4. ❌ **Comparative Assessment** (38.1%) - Team vs person naming issues

## Key Learnings

### 1. Format Matters
- **JSON > Custom formats** - Use what the model knows
- Gemini has more training data on JSON than triplets/XML
- Don't fight the model's training distribution

### 2. Prompt Engineering Sweet Spot
- **Too short:** Model lacks guidance (Iter 1, 5, 6)
- **Too long:** Diminishing returns, confusion (Iter 4)
- **Just right:** ~3000-5000 chars with examples (Iter 2-3)

### 3. Holistic > Decomposed
- Single-pass with context > Multi-pass without
- Breaking extraction into passes loses important context
- Gemini does better seeing the whole picture

### 4. Conversational Philosophy Works
- "Extract + ask for clarification" > "Only extract what's clear"
- Placeholder strategy handles ambiguity gracefully
- Prepares system for follow-up questions

### 5. Schema-Driven Needs Constrained Generation
- Rich Pydantic schemas alone aren't enough
- Works great WITH Outlines' constrained generation
- Doesn't work with plain Gemini + JSON prompting

## Cost Analysis

**Per extraction:**
- Gemini Flash: ~$0.0004
- 10 test cases: ~$0.004
- Extremely cheap for iteration

**vs OpenAI (original plan):**
- GPT-4: ~$0.004 per extraction
- 10x more expensive
- Switching to Gemini was the right call

## Files Created

### Core Implementation
- `extractor.py` - Main extractor (Iteration 3 prompt)
- `extractor_v2.py` - Two-pass version (failed experiment)
- `schemas.py` - Pydantic models with rich descriptions
- `test_cases.py` - 10 test cases with expected outputs
- `test_runner.py` - Test harness with accuracy metrics
- `validate_setup.py` - Environment validation

### Documentation
- `TESTBED_README.md` - How to use the testbed
- `QUICKSTART.md` - 2-step getting started guide
- `CHANGES.md` - Migration from OpenAI to Gemini
- `EXAMPLES.md` - Test case examples
- `PROMPT_EVOLUTION.md` - All 7 prompts with analysis
- `TWO_PASS_DESIGN.md` - Two-pass approach design doc
- `SUMMARY.md` - This file

### Iteration Results
- `iterations/test_results_*.json` - Timestamped test results
- `iterations/BASELINE_*.md` - Analysis documents
- `iterations/ITERATION_*_*.md` - Detailed iteration reports

## Recommendations

### For This Testbed
1. **Use Iteration 3** as the production prompt
2. **Accept 66.8%** as good enough for now
3. **Move to intent detection** layer (next phase)
4. **Keep iterating** if higher accuracy needed

### For Future Improvements
1. **Add more examples** for failing test patterns
2. **Fine-tune extraction rules** within JSON format
3. **Consider Outlines** if need >80% accuracy (with constrained generation)
4. **Don't try custom formats** - stick with JSON

### For Other Projects
1. **Start with JSON** - Don't reinvent output formats
2. **Test incrementally** - Validate assumptions before full implementation
3. **Use familiar formats** - Leverage model's training data
4. **Balance prompt length** - 3000-5000 chars sweet spot
5. **Include examples** - 3-4 concrete examples crucial

## Next Steps

### Option A: Accept & Move On
- 66.8% accuracy is good enough
- Build intent detection layer on top
- Iterate on full system, not just extraction

### Option B: Keep Improving
- Add examples for failing tests (3, 4, 8, 10)
- Refine output naming rules
- Test with Gemini Pro (vs Flash)
- Target 75-80% accuracy

### Option C: Implement Outlines
- Proper constrained generation
- Guaranteed schema compliance
- Likely 80-90% accuracy
- More complex setup

**Recommendation: Option A** - Move to intent detection, iterate on full system.

## Conclusion

**Success!** Built a working testbed that:
- ✅ Switched from OpenAI to Gemini (10x cheaper)
- ✅ Achieved 66.8% accuracy (vs 42.9% baseline)
- ✅ Handles ambiguity with placeholders
- ✅ Ready for conversational follow-up
- ✅ Fully documented and reproducible
- ✅ Learned what works and what doesn't

**The testbed works. Time to build the intent detection layer.**
