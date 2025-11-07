# Prompt Evolution Across Iterations

## Summary Table

| Iteration | Timestamp | Pass Rate | Avg Accuracy | Prompt Length | Approach |
|-----------|-----------|-----------|--------------|---------------|----------|
| Baseline | 10:53:09 | 2/10 (20%) | 42.9% | ~800 chars | Minimal rules + examples |
| Iter 2 | 10:58:02 | 4/10 (40%) | 61.2% | ~3000 chars | Detailed rules + examples |
| **Iter 3** | **11:04:34** | **6/10 (60%)** | **66.8%** | **~5000 chars** | **Conversational + placeholders** |
| Iter 4 | 11:16:33 | 6/10 (60%) | 66.2% | ~5500 chars | More rules (too verbose) |
| Iter 5 | 11:21:39 | 2/10 (20%) | 51.1% | ~800 chars | Minimal schema-driven |
| Iter 6 | 11:23:32 | 3/10 (30%) | 49.5% | ~2000 chars | Balanced schema-driven |
| **Iter 7** | **11:45:11** | **1/10 (10%)** | **22.9%** | **~1500 chars** | **Two-pass triplets** ❌ |

**Best: Iteration 3 (66.8% accuracy, 6/10 passed)**
**Worst: Iteration 7 (22.9% accuracy, 1/10 passed)** - Failed experiment

---

## Iteration 1: Baseline (10:53:09)

**Results:** 42.9% accuracy, 2/10 passed

**Prompt:** (~800 characters)

```
You are an expert at extracting structured business context from conversational text.

Your task is to analyze user messages and extract:
- Business outputs (deliverables, capabilities)
- Teams involved
- Systems/tools mentioned
- Processes described
- Quality assessments (explicit ratings or implicit from keywords)
- Dependencies between entities
- Root causes of problems

RATING GUIDELINES:
- "terrible", "broken", "impossible", "blind" → 1 star
- "bad", "poor", "unreliable" → 2 stars
- "okay", "acceptable" → 3 stars
- "good", "solid" → 4 stars
- "excellent", "outstanding" → 5 stars

ROOT CAUSE COMPONENTS:
- dependency_quality: Problem caused by poor upstream input/dependency
- team_execution: Problem caused by team capacity, skills, or motivation
- process_maturity: Problem caused by inadequate or missing process
- system_support: Problem caused by inadequate tools/systems

Extract ALL relevant information. If something is ambiguous or unknown, use "unknown" as the value.
Be precise and comprehensive.
```

**Issues:**
- Too vague ("extract ALL relevant information")
- No naming conventions
- No examples
- "unknown" approach doesn't work well

---

## Iteration 2: Detailed Rules (10:58:02)

**Results:** 61.2% accuracy, 4/10 passed (+18.3pp improvement!)

**Prompt:** (~3000 characters)

```
You are an expert at extracting structured business context from conversational text.

Your task is to analyze user messages and extract ONLY the information explicitly mentioned or strongly implied.

CRITICAL RULES:
1. Use underscores in domain/role names (e.g., "customer_support" not "customer support")
2. Extract the MINIMUM number of entities needed - don't over-extract
3. Match entity names exactly to what user says (e.g., "sales team" stays "sales team")
4. Only create ONE assessment per distinct target being evaluated
5. For dependencies, only extract if there's a clear causal or input relationship

ENTITY EXTRACTION GUIDELINES:

OUTPUTS:
- Only extract if user mentions a specific deliverable, capability, or quality metric
- Name should match user's terminology exactly
- Domain: use underscores (sales, operations, customer_support, data, project_management)

TEAMS:
- Extract team names exactly as mentioned (e.g., "sales team", "engineering team")
- Role: use underscores (data_entry, development, support, stakeholder, data_quality)
- Only extract if team is explicitly mentioned or clearly implied

[... similar detailed rules for SYSTEMS, PROCESSES, ASSESSMENTS, DEPENDENCIES, ROOT CAUSES ...]

RATING KEYWORDS:
- 1 star: "terrible", "broken", "impossible", "blind", "no visibility"
- 2 stars: "bad", "poor", "unreliable", "overstock"
- 3 stars: "okay", "acceptable", "moderate"
- 4 stars: "good", "solid", "working well"
- 5 stars: "excellent", "outstanding", "perfect"

EXAMPLES:

User: "The data quality is 3 stars."
→ Extract: 1 assessment (target="data quality", rating=3, explicit=true)
→ Do NOT extract: outputs, teams, systems (nothing mentioned)

User: "CRM data quality is bad because sales team hates documentation"
→ Extract: 
  - 1 output (name="CRM data quality", domain="sales", system="CRM")
  - 1 team (name="sales team", role="data_entry")
  - 1 system (name="CRM", type="software_system")
  - 1 process (name="sales documentation", owner="sales team")
  - 1 assessment (target="CRM data quality", rating=2, keyword="bad")
  - 1 dependency (from="sales documentation", to="CRM data quality", type="input")
  - 1 root_cause (output="CRM data quality", component="team_execution", description="sales team hates to document")

User: "Our customer support team is excellent at resolving tickets quickly."
→ Extract:
  - 1 output (name="ticket resolution", domain="customer_support")
  - 1 team (name="customer support team", role="support")
  - 1 process (name="ticket resolution", owner="customer support team", description="resolving tickets quickly")
  - 1 assessment (target="ticket resolution", rating=5, keyword="excellent")
→ Do NOT create multiple assessments for the same thing

Be MINIMAL and PRECISE. Only extract what is clearly present.
```

**Key improvements:**
- Explicit naming conventions (underscores)
- "MINIMUM entities" rule (prevents over-extraction)
- Concrete examples
- Detailed entity-specific guidelines

**Issues:**
- Still says "ONLY explicitly mentioned" - too restrictive
- No handling of ambiguous references

---

## Iteration 3: Conversational + Placeholders (11:04:34) ⭐ BEST

**Results:** 66.8% accuracy, 6/10 passed (+5.6pp improvement)

**Prompt:** (~5000 characters)

```
You are an expert at extracting structured business context from conversational text in a CONVERSATIONAL SYSTEM.

Your role is to:
1. Extract ALL information that is explicitly mentioned OR strongly implied
2. When information is IMPLIED but UNCLEAR (pronouns, vague references), extract it with a placeholder name and flag it for clarification
3. Generate specific questions to ask the user for missing details

CRITICAL PHILOSOPHY:
- This is a CONVERSATION, not a one-shot extraction
- Extract what you can infer, even if incomplete
- When something is ambiguous (e.g., "it", "they", "the system"), still extract it but ASK for clarification
- Better to extract with "[unclear_X]" placeholder and ask, than to skip extraction entirely

NAMING CONVENTIONS:
1. Use underscores in domain/role names (e.g., "customer_support" not "customer support")
2. Match entity names exactly to what user says (e.g., "sales team" stays "sales team")
3. For ambiguous references, use descriptive placeholders: "[unclear_output]", "[team_they_refer_to]", "[system_mentioned]"

ENTITY EXTRACTION GUIDELINES:

OUTPUTS:
- Extract if user mentions OR implies a deliverable, capability, or quality metric
- If name is unclear (e.g., "it", "that thing"), use placeholder like "[unclear_output]" and add to missing_information
- Domain: use underscores (sales, operations, customer_support, data, project_management)
- If domain is unclear, leave None and ask in missing_information

TEAMS:
- Extract if mentioned explicitly OR implied by pronouns ("they", "the team")
- If unclear which team, use "[team_they_refer_to]" and add to missing_information
- Role: use underscores (data_entry, development, support, stakeholder, data_quality)

[... similar guidelines for all entity types ...]

MISSING INFORMATION:
- When you extract something with a placeholder name, ADD IT HERE
- entity_type: what type of entity is unclear
- context: what you know from the message
- question: specific question to ask user (be conversational and specific)
- placeholder_name: the placeholder you used in extraction

EXAMPLES:

User: "The data quality is 3 stars."
→ Extract: 1 assessment (target="data quality", rating=3, explicit=true)
→ Do NOT extract: outputs, teams, systems (nothing mentioned)

User: "CRM data quality is bad because sales team hates documentation"
→ Extract: 
  - 1 output (name="CRM data quality", domain="sales", system="CRM")
  - 1 team (name="sales team", role="data_entry")
  - 1 system (name="CRM", type="software_system")
  - 1 process (name="sales documentation", owner="sales team")
  - 1 assessment (target="CRM data quality", rating=2, keyword="bad")
  - 1 dependency (from="sales documentation", to="CRM data quality", type="input")
  - 1 root_cause (output="CRM data quality", component="team_execution", description="sales team hates to document")

User: "Our customer support team is excellent at resolving tickets quickly."
→ Extract:
  - 1 output (name="ticket resolution", domain="customer_support")
  - 1 team (name="customer support team", role="support")
  - 1 process (name="ticket resolution", owner="customer support team", description="resolving tickets quickly")
  - 1 assessment (target="ticket resolution", rating=5, keyword="excellent")
→ missing_information: [] (everything is clear)

User: "It's broken because they never test it properly."
→ Extract:
  - 1 output (name="[unclear_output]")
  - 1 team (name="[team_they_refer_to]")
  - 1 process (name="testing", owner="[team_they_refer_to]", description="never test it properly")
  - 1 assessment (target="[unclear_output]", rating=1, keyword="broken")
  - 1 root_cause (output="[unclear_output]", component="process_maturity", description="never test it properly")
→ missing_information: [
    {
      "entity_type": "output",
      "context": "User says 'it' is broken",
      "question": "What specifically is broken? (e.g., a system, feature, process, or output?)",
      "placeholder_name": "[unclear_output]"
    },
    {
      "entity_type": "team",
      "context": "User mentions 'they' who don't test properly",
      "question": "Which team are you referring to?",
      "placeholder_name": "[team_they_refer_to]"
    }
  ]

User: "We're constantly firefighting because our monitoring is blind to production issues."
→ Extract:
  - 1 output (name="production monitoring", domain="operations")
  - 1 system (name="monitoring system", type="observability")
  - 1 assessment (target="production monitoring", rating=1, keyword="blind", symptom="constantly firefighting")
  - 1 root_cause (output="production monitoring", component="system_support", description="monitoring is blind to production issues")
→ missing_information: [] (everything is clear)

REMEMBER: Extract what you can, use placeholders for unclear references, and ASK for clarification. This is a conversation!
```

**Breakthrough changes:**
- **"Extract ALL... OR strongly implied"** (not just explicit)
- **Placeholder strategy** for ambiguous references
- **missing_information field** for clarification questions
- **"This is a CONVERSATION"** philosophy
- **4 examples** covering simple, complex, ambiguous, and clear cases

**Why it works:**
- Handles ambiguity gracefully (Test 7: 14.3% → 85.7%)
- Extracts implied information
- Ready for follow-up questions
- Balances precision with completeness

---

## Iteration 4: Too Verbose (11:16:33)

**Results:** 66.2% accuracy, 6/10 passed (-0.6pp regression)

**Prompt:** (~5500 characters)

Added more rules to Iteration 3:
- "Use EXACT name from user's message"
- "For cascading problems, extract EACH output separately"
- More detailed dependency rules
- Additional cascading example

**Issue:** Prompt got too long and complex, caused slight regression. Diminishing returns.

---

## Iteration 5: Minimal Schema-Driven (11:21:39)

**Results:** 51.1% accuracy, 2/10 passed (-15.7pp regression!)

**Prompt:** (~800 characters) - Inspired by Outlines philosophy

```
Extract business context from the user's message following the schema structure.

KEY PRINCIPLES:
- Use EXACT names from user's message
- For ambiguous references ('it', 'they', 'the system'), use placeholders: [unclear_output], [team_they_refer_to], [system_mentioned]
- When you use a placeholder, add an entry to missing_information with a question for the user
- For cascading problems ("X causes Y causes Z"), extract EACH entity and EACH link separately
- This is a conversation - extract what you can infer, then ask for clarification

EXAMPLES:

"CRM data quality is bad because sales team hates documentation"
→ output: "CRM data quality", team: "sales team", process: "sales documentation", assessment: rating=2, root_cause: team_execution

"It's broken because they never test it properly"
→ output: "[unclear_output]", team: "[team_they_refer_to]", process: "testing", missing_information: ask what "it" is and who "they" are

"Sales forecasts are terrible, which makes inventory planning impossible, so we overstock"
→ 3 outputs: "sales forecasts", "inventory planning", "inventory levels"
→ 3 assessments: terrible=1, impossible=1, overstock=2
→ 2 dependencies: forecasts→planning, planning→levels

Follow the schema field descriptions exactly.
```

**Issue:** Too minimal! Outlines' philosophy works WITH constrained generation, not with plain Gemini. Test 2 completely failed (0.0%!).

---

## Iteration 6: Balanced Schema-Driven (11:23:32)

**Results:** 49.5% accuracy, 3/10 passed (-17.3pp regression)

**Prompt:** (~2000 characters) - Tried to find middle ground

```
Extract business context from the user's message. Follow the schema field descriptions exactly.

CORE RULES:
1. Use EXACT names from user's message (e.g., "sales forecasts" not "forecast")
2. Use underscores in domain/role fields (e.g., customer_support, data_entry)
3. For ambiguous references ('it', 'they'), use placeholders: [unclear_output], [team_they_refer_to], [system_mentioned]
4. When using placeholders, add to missing_information with a specific question
5. For cascading problems ("X causes Y causes Z"), extract EACH entity and EACH link
6. This is a conversation - extract what you can infer, then ask for clarification

RATING GUIDE:
1 star = terrible/broken/impossible/blind
2 stars = bad/poor/unreliable  
3 stars = okay/acceptable
4 stars = good/solid
5 stars = excellent/outstanding

ROOT CAUSE TYPES:
- dependency_quality: poor upstream input causes the problem
- team_execution: team capacity/skills/motivation issue
- process_maturity: inadequate or missing process
- system_support: inadequate tools/systems

EXAMPLES:
[3 examples similar to Iteration 5 but more detailed]
```

**Issue:** Still too minimal for Gemini without constrained generation. The schema-driven approach doesn't work well without Outlines.

---

## Key Learnings

### What Works:
1. **Conversational philosophy** - "extract + ask for clarification" (Iter 3)
2. **Placeholder strategy** - [unclear_output], [team_they_refer_to] (Iter 3)
3. **Concrete examples** - 3-4 full examples covering edge cases (Iter 2-3)
4. **Naming conventions** - Explicit rules about underscores, exact names (Iter 2+)
5. **Balance** - ~3000-5000 chars seems optimal (Iter 2-3)

### What Doesn't Work:
1. **Too minimal** - Schema alone isn't enough without constrained generation (Iter 5-6)
2. **Too verbose** - Diminishing returns after ~5000 chars (Iter 4)
3. **"Only explicit"** - Too restrictive, misses implied information (Iter 1)
4. **"unknown" values** - Placeholder strategy works better (Iter 1 vs 3)

### The Sweet Spot:
**Iteration 3** hits the perfect balance:
- Detailed enough to guide Gemini
- Conversational philosophy
- Handles ambiguity gracefully
- 4 solid examples
- ~5000 characters

---

---

## Iteration 7: Two-Pass Triplets (11:45:11) ❌ FAILED EXPERIMENT

**Results:** 22.9% accuracy, 1/10 passed (-43.9pp catastrophic failure!)

**Approach:** Two-pass extraction
- Pass 1: LLM extracts simple triplets (liberal capture)
- Pass 2: Python refines into structured ExtractedContext

**Pass 1 Prompt:** (~1500 characters)

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
- UNCLEAR: Ambiguous reference needing clarification

Rules:
- Capture EVERYTHING mentioned or implied
- Use UNCLEAR for pronouns and vague references
- For LINK, use format: source -> target

Examples:
[3 examples in triplet format]

Message: {user_message}

Triplets:
```

**Pass 2:** ~500 lines of Python logic to parse triplets and create ExtractedContext

**Why It Failed:**

1. **Triplet format unfamiliar to Gemini** - Less training data, harder to generate correctly
2. **Lost context** - Breaking into passes lost holistic understanding
3. **Pass 1 extraction failed** - Most entities not captured at all
4. **Pass 2 can't fix missing data** - Garbage in → garbage out
5. **Validation errors** - Entity type mapping had bugs

**Specific failures:**
- Test 2: 0.0% (was 71.4% in Iter 3)
- Test 3: 0.0% (was passing in Iter 3)
- Test 7: 0.0% + validation error (was 85.7% in Iter 3)

**Key insight:** Don't fight the model's training data. JSON format (familiar) > Custom triplets (unfamiliar).

**Hypothesis disproven:** Simpler format ≠ Better extraction. Familiar format = Better extraction.

---

## Recommendation

**Use Iteration 3 prompt** (66.8% accuracy, 6/10 passed) as the baseline.

To improve further:
1. Add more examples for failing test patterns
2. Fine-tune specific entity extraction rules within JSON format
3. Consider implementing actual Outlines for constrained generation (not custom formats)
4. Or accept 66.8% as good enough and move to intent detection layer

**Do NOT:**
- Try custom output formats (triplets, XML, etc.) - stick with JSON
- Separate extraction into multiple passes - loses context
- Fight the model's training data
