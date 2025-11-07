# Two-Pass Extraction Design

## Core Idea

**Problem with current approach:**
- Single-pass JSON extraction asks LLM to do too much at once:
  - Identify entities
  - Classify them correctly
  - Structure them in nested JSON
  - Handle ambiguity
  - Infer missing information
- Result: 66.8% accuracy ceiling

**New approach: Separate concerns**

### Pass 1: Raw Material Capture (Liberal)
- **Goal:** Capture EVERYTHING mentioned or implied
- **Format:** Simple triplets (easy for LLM)
- **Philosophy:** "Better to capture too much than miss something"
- **No decisions:** Don't worry about exact classification yet

### Pass 2: Structured Refinement (Conservative)
- **Goal:** Convert raw triplets into clean ExtractedContext
- **Format:** Pydantic models (type-safe)
- **Philosophy:** "Now we have all the pieces, let's organize them"
- **Post-processing:** Deduplicate, normalize, validate

## Why This Should Work Better

1. **Cognitive load reduction** - Each pass has ONE job
2. **Format simplicity** - Triplets are easier than nested JSON
3. **Robustness** - Parse errors in Pass 1 don't break everything
4. **Flexibility** - Can tune Pass 2 logic without re-prompting
5. **Debugging** - Can inspect raw triplets to see what LLM captured

## Pass 1: Raw Capture Format

### Triplet Structure
```
ENTITY_TYPE | entity_mention | context_clues
```

### Entity Types (Liberal - capture everything)
- `THING` - Any output, deliverable, metric, or thing being discussed
- `ACTOR` - Any team, person, or group mentioned
- `TOOL` - Any system, software, or tool
- `ACTIVITY` - Any process, workflow, or action
- `QUALITY` - Any assessment, rating, or quality statement
- `LINK` - Any relationship or dependency
- `PROBLEM` - Any issue, cause, or explanation
- `UNCLEAR` - Ambiguous reference that needs clarification

### Examples

**Input:** "CRM data quality is bad because sales team hates documentation"

**Pass 1 Output (Raw Triplets):**
```
THING | CRM data quality | mentioned_as:output, related_to:CRM
TOOL | CRM | mentioned_as:system
ACTOR | sales team | mentioned_as:team
ACTIVITY | documentation | owner:sales team, related_to:CRM data quality
QUALITY | bad | target:CRM data quality, keyword:bad
LINK | documentation -> CRM data quality | relationship:affects
PROBLEM | sales team hates documentation | affects:CRM data quality, type:behavioral
```

**Input:** "It's broken because they never test it properly"

**Pass 1 Output (Raw Triplets):**
```
UNCLEAR | it | mentioned_as:thing, context:is broken
UNCLEAR | they | mentioned_as:actor, context:never test
ACTIVITY | testing | owner:they, target:it, quality:never properly
QUALITY | broken | target:it, keyword:broken
PROBLEM | never test properly | affects:it, type:process_issue
```

**Input:** "Sales forecasts are terrible, which makes inventory planning impossible, so we overstock"

**Pass 1 Output (Raw Triplets):**
```
THING | sales forecasts | mentioned_as:output, domain:sales
THING | inventory planning | mentioned_as:output, domain:operations
THING | inventory levels | mentioned_as:output, domain:operations, symptom:overstock
QUALITY | terrible | target:sales forecasts, keyword:terrible
QUALITY | impossible | target:inventory planning, keyword:impossible
QUALITY | overstock | target:inventory levels, keyword:overstock
LINK | sales forecasts -> inventory planning | relationship:blocks
LINK | inventory planning -> inventory levels | relationship:causes_problem
PROBLEM | poor sales forecasts | affects:inventory planning, type:dependency
PROBLEM | poor inventory planning | affects:inventory levels, type:dependency
```

## Pass 2: Structured Refinement

### Processing Steps

1. **Parse triplets** - Line-by-line, fault-tolerant
2. **Classify entities** - THING → Output, ACTOR → Team, etc.
3. **Extract properties** - Parse key:value pairs
4. **Resolve references** - Match entity names across triplets
5. **Handle UNCLEAR** - Create MissingInformation entries
6. **Deduplicate** - Merge similar entities
7. **Validate** - Create Pydantic models
8. **Return** - ExtractedContext

### Classification Rules

```python
THING → Output (if it's a deliverable/metric/capability)
ACTOR → Team (if it's a group/team/people)
TOOL → System (if it's software/tool/platform)
ACTIVITY → Process (if it's a workflow/action)
QUALITY → Assessment (extract rating from keyword)
LINK → Dependency (parse source → target)
PROBLEM → RootCause (determine component type)
UNCLEAR → MissingInformation (generate clarification question)
```

### Example Refinement

**Raw triplet:**
```
QUALITY | bad | target:CRM data quality, keyword:bad
```

**Refined to:**
```python
Assessment(
    target="CRM data quality",
    rating=2,  # bad = 2 stars
    explicit=False,
    sentiment="negative",
    keyword="bad"
)
```

**Raw triplet:**
```
UNCLEAR | it | mentioned_as:thing, context:is broken
```

**Refined to:**
```python
Output(name="[unclear_output]")

MissingInformation(
    entity_type="output",
    context="User says 'it' is broken",
    question="What specifically is broken?",
    placeholder_name="[unclear_output]"
)
```

## Implementation Plan

### 1. Create `extractor_v2.py`
- `extract_raw_triplets()` - Pass 1 with simple prompt
- `refine_to_context()` - Pass 2 with Python logic
- `extract()` - Orchestrates both passes

### 2. Simple Pass 1 Prompt (~500 chars)
```
Extract everything mentioned in this message as simple triplets.

Format: TYPE | name | properties

Types: THING, ACTOR, TOOL, ACTIVITY, QUALITY, LINK, PROBLEM, UNCLEAR

Capture EVERYTHING, even if unclear. Use UNCLEAR for ambiguous references like "it" or "they".

Examples:
"CRM is bad" →
THING | CRM | type:system
QUALITY | bad | target:CRM

"It's broken" →
UNCLEAR | it | context:broken
QUALITY | broken | target:it

Message: {user_message}

Triplets:
```

### 3. Pass 2 Parser (Python)
- Robust line-by-line parsing
- Property extraction with regex
- Entity classification logic
- Deduplication and normalization
- Pydantic model creation

### 4. Test Against Same 10 Cases
- Compare with Iteration 3 (66.8%)
- Measure improvement
- Document results

## Expected Benefits

1. **Higher recall** - Pass 1 captures more (liberal)
2. **Better precision** - Pass 2 cleans up (conservative)
3. **Handles ambiguity** - UNCLEAR type + Pass 2 processing
4. **More robust** - Triplet parsing is fault-tolerant
5. **Debuggable** - Can inspect raw triplets
6. **Tunable** - Can improve Pass 2 logic without re-prompting

## Success Criteria

- **Accuracy > 70%** (vs 66.8% current)
- **Pass rate > 7/10** (vs 6/10 current)
- **Test 3 (cascading)** - Should improve significantly
- **Test 4 (multi-entity)** - Should improve
- **Test 7 (ambiguous)** - Should maintain 85.7%

## Risks

1. **Two LLM calls** - 2x cost, 2x latency
   - Mitigation: Pass 2 is Python, not LLM!
2. **Pass 1 quality** - If triplets are bad, Pass 2 can't fix
   - Mitigation: Simple format should be easier for LLM
3. **Pass 2 complexity** - Parsing logic could get complex
   - Mitigation: Start simple, iterate

## Next Steps

1. Implement `extractor_v2.py`
2. Create Pass 1 prompt
3. Create Pass 2 parser
4. Run tests
5. Document as Iteration 7
