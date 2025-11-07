# Iteration 7 - Two-Pass Approach (Nov 7, 2025 11:45)

**File:** `test_results_20251107_114511.json`

## Approach: Raw Triplet Capture → Structured Refinement

**Hypothesis:** Separating concerns would improve accuracy
- Pass 1: LLM extracts simple triplets (liberal capture)
- Pass 2: Python refines into structured ExtractedContext (conservative)

## Results: FAILED ❌

| Metric | Iter 3 (Best) | Iter 7 (Two-Pass) | Change |
|--------|---------------|-------------------|--------|
| **Tests Passed** | 6/10 (60%) | **1/10 (10%)** | **-83%** ❌❌❌ |
| **Avg Accuracy** | 66.8% | **22.9%** | **-43.9pp** ❌❌❌ |
| **Simple** | 78.6% | 64.3% | -14.3pp |
| **Medium** | 100.0% | 28.6% | -71.4pp ❌ |
| **Complex** | 58.6% | **10.2%** | **-48.4pp** ❌❌ |

**Catastrophic failure!** Only 1 test passed (vs 6 in Iteration 3).

## What Went Wrong

### 1. Pass 1 Didn't Capture Enough
Looking at the errors, Pass 1 (LLM triplet extraction) **completely failed** to extract most entities.

**Example: Test 2 (0.0% accuracy)**
- Expected: outputs, teams, systems, processes, assessments, dependencies, root_causes
- Got: Nothing extracted

**The triplet format was too different from what Gemini is trained on.**

### 2. Pass 2 Can't Fix Missing Data
Pass 2 (Python refinement) can only work with what Pass 1 captured. If Pass 1 misses entities, Pass 2 has nothing to refine.

**Garbage in → Garbage out**

### 3. Validation Errors
Multiple tests failed with Pydantic validation errors:
```
entity_type: Input should be 'output', 'team', 'system', 'process' or 'other'
[type=literal_error, input_value='thing', input_type=str]
```

Even though I added the mapping, there were still edge cases.

### 4. Over-Extraction of Wrong Things
Test 6 created wrong assessments:
- Expected: 1 assessment for "ticket resolution"
- Got: 2 assessments - one for "resolving tickets" (rating=2, negative!) and one for "customer support team"

The triplet format confused the LLM about what to extract.

### 5. Prompt Too Different
The triplet prompt format (TYPE | name | properties) is very different from natural JSON. Gemini likely has less training data on this format.

## Why The Hypothesis Failed

### Assumption 1: "Triplets are simpler for LLM" ❌
**Reality:** JSON is what Gemini is trained on. Triplets are actually HARDER because:
- Less training data in this format
- Unfamiliar syntax
- Requires understanding a custom format

### Assumption 2: "Separating concerns helps" ❌
**Reality:** The concerns are intertwined:
- Identifying entities requires understanding their relationships
- Classification requires context from other entities
- Gemini does better with holistic understanding

### Assumption 3: "Python can fix LLM mistakes" ❌
**Reality:** Python can only work with what LLM provides:
- If LLM misses an entity, Python can't invent it
- If LLM misclassifies, Python has wrong input
- Post-processing can clean, but can't create

## Specific Failures

### Test 2: "The Sentence That Broke Us" (0.0%)
**Message:** "CRM data quality is bad because sales team hates documentation"

**Expected:** Full extraction (7 entities)
**Got:** Nothing or minimal extraction

**Why:** Triplet format confused the LLM

### Test 3: Multi-Output Dependency Chain (0.0%)
**Message:** "Sales forecasts are terrible, which makes inventory planning impossible, so we overstock"

**Expected:** 3 outputs, 3 assessments, 2 dependencies, 2 root_causes
**Got:** Nothing

**Why:** Complex cascading logic doesn't fit triplet format well

### Test 7: Ambiguous Reference (0.0% + validation error)
**Message:** "It's broken because they never test it properly"

**Expected:** Placeholders + missing_information
**Got:** Validation error on entity_type

**Why:** Mapping from 'thing'/'actor' to 'output'/'team' had bugs

## Key Learnings

### 1. Format Matters More Than We Thought
- Gemini is trained on JSON, not custom triplet formats
- Familiarity > Simplicity
- Don't fight the model's training data

### 2. Holistic Understanding > Separation of Concerns
- Context extraction requires seeing the whole picture
- Breaking it into passes loses context
- Single-pass with good prompt > multi-pass with simple prompts

### 3. Post-Processing Has Limits
- Can clean and normalize
- Can't create missing information
- Can't fix fundamental extraction failures

### 4. Complexity Budget
- LLMs have a "complexity budget" per task
- Better to spend it on one good extraction than two mediocre ones
- Iteration 3's longer prompt uses the budget well

## What We Should Have Done

**Before implementing:**
1. Test Pass 1 prompt in isolation first
2. Verify triplet extraction works on 2-3 examples
3. Only proceed if Pass 1 shows promise

**We jumped straight to full implementation without validating the core assumption.**

## Recommendation

**Abandon the two-pass triplet approach.**

**Stick with Iteration 3:**
- 66.8% accuracy
- 6/10 tests passing
- Proven to work
- JSON format Gemini understands

**If we want to improve further:**
1. Refine Iteration 3 prompt (not format)
2. Add more examples for failing tests
3. Fine-tune specific extraction rules
4. Consider actual Outlines with constrained generation (not custom triplets)

## Cost Analysis

**Two-pass approach also costs more:**
- 2 LLM calls per extraction (Pass 1 + potential retries)
- More tokens (triplet format + JSON schema)
- More latency (sequential calls)

**And delivers worse results!**

## Conclusion

**The two-pass triplet approach was a failed experiment.**

- Hypothesis: Simpler format → better extraction ❌
- Reality: Familiar format (JSON) → better extraction ✅
- Result: 22.9% accuracy (vs 66.8% baseline) ❌

**Key insight:** Don't fight the model's training data. Use formats it knows well (JSON), not custom formats (triplets).

**Next steps:** Revert to Iteration 3, focus on prompt refinement within JSON format.

---

## Technical Details

**Files created:**
- `extractor_v2.py` - Two-pass implementation
- `test_runner_v2.py` - Test runner for v2
- `TWO_PASS_DESIGN.md` - Design document

**Prompt length:**
- Pass 1: ~1500 characters (triplet format)
- Pass 2: ~500 lines of Python logic

**Total tokens per extraction:**
- Pass 1 prompt: ~400 tokens
- Pass 1 response: ~200 tokens
- Pass 2 processing: 0 tokens (Python)
- Total: ~600 tokens (vs ~800 for Iteration 3)

**But accuracy dropped 66% despite lower token usage!**

Token efficiency doesn't matter if results are wrong.
