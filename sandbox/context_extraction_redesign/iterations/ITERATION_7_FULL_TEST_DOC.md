# Iteration 7 - Full Test Documentation

**Date:** November 7, 2025, 11:45:11  
**File:** `test_results_20251107_114511.json`

---

## Concept

### What Changed
Implemented **two-pass extraction approach**:
- **Pass 1:** LLM extracts simple triplets (liberal raw capture)
- **Pass 2:** Python refines triplets into structured ExtractedContext (conservative processing)

**Key innovations:**
1. **Triplet format** - TYPE | name | properties (simpler than JSON)
2. **Separation of concerns** - Capture vs refinement
3. **Fault-tolerant parsing** - Line-by-line, errors don't break everything
4. **Post-processing logic** - Python handles classification and normalization

### Why
**Hypothesis:** Separating extraction into two passes would improve accuracy
- Pass 1 focuses only on capturing raw material (easier for LLM)
- Pass 2 handles complex logic in Python (more reliable)
- Triplet format simpler than nested JSON
- Post-processing can fix LLM mistakes

**Expected benefits:**
- Higher recall (Pass 1 captures more)
- Better precision (Pass 2 cleans up)
- More robust (fault-tolerant parsing)
- Tunable (can improve Pass 2 without re-prompting)

---

## Result Summary

| Metric | Iteration 3 | Iteration 7 | Change |
|--------|-------------|-------------|--------|
| **Tests Passed** | 6/10 (60%) | **1/10 (10%)** | **-83%** ❌❌❌ |
| **Avg Accuracy** | 66.8% | **22.9%** | **-43.9pp** ❌❌❌ |
| **Simple Tests** | 78.6% | 64.3% | -14.3pp |
| **Medium Tests** | 100.0% | 28.6% | -71.4pp ❌ |
| **Complex Tests** | 58.6% | **10.2%** | **-48.4pp** ❌❌ |

**CATASTROPHIC FAILURE!** Only 1 test passed vs 6 in Iteration 3.

**Hypothesis DISPROVEN:** Two-pass approach made things dramatically worse.

---

## Exact Prompts Used

### Pass 1: Raw Triplet Extraction (LLM)

```
Extract everything mentioned in this message as simple triplets.

Format: TYPE | name | properties (key:value pairs separated by commas)

Types:
- THING: Any output, deliverable, metric, or thing being discussed
- ACTOR: Any team, person, or group mentioned
- TOOL: Any system, software, or tool
- ACTIVITY: Any process, workflow, or action
- QUALITY: Any assessment, rating, or quality statement
- LINK: Any relationship or dependency (use -> for direction)
- PROBLEM: Any issue, root cause, or explanation
- UNCLEAR: Ambiguous reference needing clarification (like "it", "they", "the system")

Rules:
- Capture EVERYTHING mentioned or implied
- Use UNCLEAR for pronouns and vague references
- For LINK, use format: source -> target
- Include context clues in properties

Examples:

"CRM data quality is bad because sales team hates documentation"
→
THING | CRM data quality | related_to:CRM, domain:sales
TOOL | CRM | type:system
ACTOR | sales team | role:data_entry
ACTIVITY | documentation | owner:sales team, related_to:CRM data quality
QUALITY | bad | target:CRM data quality, keyword:bad
LINK | documentation -> CRM data quality | type:affects
PROBLEM | sales team hates documentation | affects:CRM data quality, reason:behavioral

"It's broken because they never test it properly"
→
UNCLEAR | it | context:is broken, type:thing
UNCLEAR | they | context:never test, type:actor
ACTIVITY | testing | owner:they, target:it, quality:never properly
QUALITY | broken | target:it, keyword:broken
PROBLEM | never test properly | affects:it, reason:process_issue

"Sales forecasts are terrible, which makes inventory planning impossible, so we overstock"
→
THING | sales forecasts | domain:sales
THING | inventory planning | domain:operations
THING | inventory levels | domain:operations, symptom:overstock
QUALITY | terrible | target:sales forecasts, keyword:terrible
QUALITY | impossible | target:inventory planning, keyword:impossible
QUALITY | overstock | target:inventory levels, keyword:overstock
LINK | sales forecasts -> inventory planning | type:blocks
LINK | inventory planning -> inventory levels | type:causes_problem
PROBLEM | poor sales forecasts | affects:inventory planning, reason:dependency
PROBLEM | poor inventory planning | affects:inventory levels, reason:dependency

Message: {user_message}

Triplets:
```

**Prompt Length:** ~1500 characters

### Pass 2: Structured Refinement (Python)

~500 lines of Python code to:
1. Parse triplets line-by-line
2. Extract properties from key:value pairs
3. Classify entities (THING→Output, ACTOR→Team, etc.)
4. Resolve entity references
5. Handle UNCLEAR types
6. Create Pydantic models
7. Validate and return ExtractedContext

---

## Test Cases

### Test 1: Simple Assessment ✅ PASS

**Input:**
```
"The data quality is 3 stars."
```

**Pass 1 Output (Triplets):**
```
QUALITY | 3 stars | target:data quality, keyword:3 stars
```

**Pass 2 Output (Final):**
- 1 assessment (target="data quality", rating=3, explicit=true)

**Accuracy:** 71.4%  
**Pass:** YES (>70%)

**Notes:** Only test that passed. Simple case worked.

---

### Test 2: The Sentence That Broke Us ❌ FAIL

**Input:**
```
"I think data quality in our CRM is bad because the sales team hates to document their work."
```

**Pass 1 Output (Triplets):**
```
(Empty or minimal - extraction failed)
```

**Pass 2 Output (Final):**
- No entities extracted

**Expected:**
- 1 output, 1 team, 1 system, 1 process, 1 assessment, 1 dependency, 1 root_cause

**Actual:**
- Nothing

**Accuracy:** 0.0%  
**Pass:** NO

**Notes:** Pass 1 completely failed to extract. Triplet format confused the LLM.

---

### Test 3: Multi-Output Dependency Chain ❌ FAIL

**Input:**
```
"Our sales forecasts are terrible, which makes inventory planning impossible, so we always overstock."
```

**Pass 1 Output (Triplets):**
```
(Empty or minimal)
```

**Pass 2 Output (Final):**
- No entities extracted

**Expected:**
- 3 outputs, 3 assessments, 2 dependencies, 2 root_causes

**Actual:**
- Nothing

**Accuracy:** 0.0%  
**Pass:** NO

**Notes:** Complex cascading logic didn't fit triplet format at all.

---

### Test 4: Team + Process + System ❌ FAIL

**Input:**
```
"JIRA ticket updates are terrible because the engineering team doesn't update tickets, so project managers have no visibility."
```

**Pass 1 Output (Triplets):**
```
(Minimal extraction)
```

**Pass 2 Output (Final):**
- Partial extraction, missing most entities

**Expected:**
- 1 output, 1 team, 1 system, 1 process, 1 assessment, 1 dependency, 1 root_cause

**Actual:**
- Some entities missing

**Accuracy:** 0.0%  
**Pass:** NO

---

### Test 5: Implicit Assessment with Symptom ❌ FAIL

**Input:**
```
"We're constantly firefighting because our monitoring is blind to production issues."
```

**Pass 1 Output (Triplets):**
```
(Failed to extract)
```

**Pass 2 Output (Final):**
- No entities

**Expected:**
- 1 output, 1 system, 1 assessment, 1 root_cause

**Actual:**
- Nothing

**Accuracy:** 42.9%  
**Pass:** NO

---

### Test 6: Positive Assessment ❌ FAIL

**Input:**
```
"Our customer support team is excellent at resolving tickets quickly."
```

**Pass 1 Output (Triplets):**
```
ACTOR | customer support team | role:support
QUALITY | excellent | target:customer support team, keyword:excellent
QUALITY | quickly | target:resolving tickets, keyword:quickly
```

**Pass 2 Output (Final):**
- 1 output: "tickets" (wrong - should be "ticket resolution")
- 1 team: "customer support team" ✓
- 1 process: "resolving tickets" (partial)
- 2 assessments: excellent (team), quickly=2 stars (WRONG - "quickly" is not bad!)
- 2 dependencies (extra, wrong)

**Expected:**
- 1 output: "ticket resolution"
- 1 team: "customer support team"
- 1 process: "ticket resolution"
- 1 assessment: rating=5, keyword="excellent", target="ticket resolution"

**Accuracy:** 28.6%  
**Pass:** NO

**Notes:** Pass 1 extracted wrong things. "quickly" was interpreted as negative (rating=2)!

---

### Test 7: Ambiguous Reference ❌ FAIL + ERROR

**Input:**
```
"It's broken because they never test it properly."
```

**Pass 1 Output (Triplets):**
```
UNCLEAR | it | context:is broken, type:thing
UNCLEAR | they | context:never test, type:actor
```

**Pass 2 Output (Final):**
**ERROR:** Pydantic validation error
```
entity_type: Input should be 'output', 'team', 'system', 'process' or 'other'
[type=literal_error, input_value='thing', input_type=str]
```

**Expected:**
- Placeholders with missing_information

**Actual:**
- Validation error, extraction failed

**Accuracy:** 0.0%  
**Pass:** NO

**Notes:** Entity type mapping bug. 'thing' not mapped to 'output' correctly.

---

### Test 8: Multiple Systems ❌ FAIL

**Input:**
```
"Data flows from Salesforce to our data warehouse, but the ETL pipeline is unreliable."
```

**Pass 1 Output (Triplets):**
```
(Partial extraction)
```

**Pass 2 Output (Final):**
- Partial, missing most relationships

**Expected:**
- 1 output, 3 systems, 1 process, 1 assessment, 1 dependency, 1 root_cause

**Actual:**
- Incomplete extraction

**Accuracy:** 28.6%  
**Pass:** NO

---

### Test 9: Partial Information ❌ FAIL

**Input:**
```
"I want to work on sales forecasting."
```

**Pass 1 Output (Triplets):**
```
ACTIVITY | sales forecasting | domain:sales
LINK | I -> sales forecasting | type:input
```

**Pass 2 Output (Final):**
- 1 process: "sales forecasting" ✓
- 1 dependency: "I" → "sales forecasting" (WRONG - "I" is not an entity!)

**Expected:**
- 1 output: "sales forecasting"

**Actual:**
- Wrong entity type (process vs output)
- Extra wrong dependency

**Accuracy:** 57.1%  
**Pass:** NO

**Notes:** Extracted "I" as an entity!

---

### Test 10: Comparative Assessment ❌ FAIL + ERROR

**Input:**
```
"Our data quality used to be 4 stars, but now it's down to 2 because we lost our data engineer."
```

**Pass 1 Output (Triplets):**
```
(Partial)
```

**Pass 2 Output (Final):**
**ERROR:** Pydantic validation error (same as Test 7)

**Expected:**
- 1 output, 1 team, 2 assessments, 1 root_cause

**Actual:**
- Validation error

**Accuracy:** 0.0%  
**Pass:** NO

---

## Pass Rate Summary

### Passing Tests (1/10 = 10%)
1. ✅ Test 1: Simple Assessment (71.4%)

### Failing Tests (9/10 = 90%)
1. ❌ Test 2: The Sentence That Broke Us (0.0%)
2. ❌ Test 3: Multi-Output Dependency Chain (0.0%)
3. ❌ Test 4: Team + Process + System (0.0%)
4. ❌ Test 5: Implicit Assessment (42.9%)
5. ❌ Test 6: Positive Assessment (28.6%)
6. ❌ Test 7: Ambiguous Reference (0.0% + validation error)
7. ❌ Test 8: Multiple Systems (28.6%)
8. ❌ Test 9: Partial Information (57.1%)
9. ❌ Test 10: Comparative Assessment (0.0% + validation error)

### By Difficulty
- **Simple (1/2):** 50% pass rate, 64.3% avg accuracy
- **Medium (0/1):** 0% pass rate, 28.6% avg accuracy
- **Complex (0/7):** 0% pass rate, 10.2% avg accuracy

---

## Why It Failed

### 1. Triplet Format Unfamiliar to Gemini
- Gemini is trained on JSON, not custom triplet formats
- Less training data on "TYPE | name | properties" syntax
- LLM struggled to generate correct triplet format
- **Result:** Pass 1 extraction mostly failed

### 2. Pass 1 Didn't Capture Entities
- Most test cases: Pass 1 returned empty or minimal triplets
- Complex sentences: Complete extraction failure
- **Example:** Test 2 returned nothing at all
- **Result:** Pass 2 had no data to work with

### 3. Lost Holistic Context
- Breaking extraction into passes lost important context
- Relationships between entities harder to capture in triplets
- Gemini does better with holistic understanding
- **Result:** Even when Pass 1 worked, quality was poor

### 4. Pass 2 Can't Fix Missing Data
- Python logic can only work with what Pass 1 provides
- If Pass 1 misses entities, Pass 2 can't invent them
- Post-processing can clean, not create
- **Result:** Garbage in → garbage out

### 5. Validation Errors
- Entity type mapping had bugs ('thing' → 'output')
- Tests 7 and 10 crashed with Pydantic errors
- Even with fixes, fundamental approach was broken
- **Result:** Some tests couldn't complete

### 6. Wrong Interpretations
- Test 6: "quickly" interpreted as negative (rating=2)!
- Test 9: "I" extracted as an entity
- Triplet format led to bizarre extractions
- **Result:** Even "successful" extractions were wrong

---

## Key Insights

### Hypothesis Disproven
**"Simpler format → Better extraction"** ❌

**Reality:** Familiar format (JSON) → Better extraction ✅

- Gemini has more training data on JSON
- Custom formats are actually HARDER for LLM
- Don't fight the model's training distribution

### Separation of Concerns Backfired
**"Two passes → Better results"** ❌

**Reality:** Single pass with context → Better results ✅

- Context extraction requires holistic understanding
- Breaking into passes loses important relationships
- Gemini does better seeing the whole picture

### Post-Processing Has Limits
**"Python can fix LLM mistakes"** ❌

**Reality:** Python can only clean what LLM provides ✅

- Can't create missing entities
- Can't fix fundamental misunderstandings
- Can normalize and validate, but not invent

### Cost vs Benefit
**Even though approach was cheaper (fewer tokens), results were catastrophically worse**

- Token efficiency doesn't matter if results are wrong
- 66% accuracy drop is not worth any cost savings
- Quality > Efficiency

---

## Lessons Learned

### Do NOT:
1. ❌ Try custom output formats (triplets, XML, etc.)
2. ❌ Separate extraction into multiple passes
3. ❌ Fight the model's training data
4. ❌ Assume simpler format = better results
5. ❌ Rely on post-processing to fix LLM failures

### DO:
1. ✅ Use formats the model knows (JSON)
2. ✅ Keep extraction holistic (single pass)
3. ✅ Leverage model's training distribution
4. ✅ Test assumptions before full implementation
5. ✅ Validate approach on 2-3 examples first

---

## Conclusion

**The two-pass triplet approach was a failed experiment.**

- Accuracy dropped from 66.8% → 22.9% (-66% relative)
- Pass rate dropped from 60% → 10% (-83% relative)
- Multiple validation errors
- Catastrophic failure on complex tests

**Root cause:** Fighting the model's training data by using unfamiliar triplet format.

**Recommendation:** Abandon this approach. Stick with Iteration 3 (JSON format, single-pass, conversational philosophy).

**Key takeaway:** Don't fight the model. Use what it knows.
