# Conversation Pattern Format

**Purpose:** Capture patterns for both LLM conversation engine AND semantic test validation  
**Dual Use:** Runtime behavior + Test assertions

---

## Pattern Template

```yaml
pattern_id: "PATTERN_001_WELCOME_FIRST_TIME"
name: "First-Time User Welcome"
category: "onboarding"  # onboarding | discovery | assessment | analysis | recommendations | navigation

# TRIGGER CONDITIONS
trigger:
  type: "system_proactive"  # user_explicit | user_implicit | system_proactive | system_reactive
  
  conditions:
    user_knowledge:
      knows_system_purpose: false
      knows_how_to_start: false
      session_count: 0
    
    system_state:
      has_active_assessment: false
      conversation_turn: 1
    
    context_requirements: []  # No prerequisites for first interaction
  
  priority: "high"  # high | medium | low (for competing patterns)

# PATTERN BEHAVIOR
behavior:
  system_goals:
    - "Establish safety and trust"
    - "Show immediate value (no upfront education)"
    - "Get user started with minimal friction"
  
  response_template: |
    Hi! I help you figure out which AI pilots would actually work in your organization.
    
    What output or process are you struggling with?
  
  response_constraints:
    max_words: 30
    tone: "professional, direct"
    avoid: ["empathy theater", "feature lists", "how it works explanations"]
  
  teaches_user:
    - concept: "system_purpose"
      detail_level: "minimal"
      explanation: "One sentence: what system does"
    - concept: "how_to_start"
      detail_level: "implicit"
      explanation: "Ask a question, user answers naturally"

# KNOWLEDGE UPDATES
updates:
  user_knowledge:
    knows_system_purpose: true
    knows_how_to_start: true
  
  system_knowledge:
    conversation_started: true
    user_engagement_level: "to_be_inferred"

# FOLLOW-UP PATTERNS
next_patterns:
  likely:
    - "PATTERN_010_OUTPUT_DISCOVERY"
    - "PATTERN_011_VAGUE_PROBLEM_REFINEMENT"
  
  possible:
    - "PATTERN_050_USER_ASKS_HOW_IT_WORKS"
    - "PATTERN_051_USER_ASKS_ABOUT_DATA_PRIVACY"

# TEST ASSERTIONS
tests:
  semantic:
    - assertion: "Response contains system purpose"
      validation: "LLM should identify purpose statement"
      
    - assertion: "Response asks for user's problem"
      validation: "LLM should identify question to user"
      
    - assertion: "Response is under 30 words"
      validation: "Word count check"
      
    - assertion: "Response does not explain features"
      validation: "LLM should NOT find feature explanations"
      
    - assertion: "Response does not use empathy phrases"
      validation: "LLM should NOT find phrases like 'I understand', 'must be frustrating'"
  
  behavioral:
    - assertion: "User knowledge updated correctly"
      validation: "knows_system_purpose == true after pattern"
      
    - assertion: "Conversation turn incremented"
      validation: "conversation_turn == 2 after pattern"

# EXAMPLES
examples:
  good:
    - response: "Hi! I help you figure out which AI pilots would actually work in your organization. What output or process are you struggling with?"
      why: "Direct, shows value, asks specific question, under 30 words"
    
    - response: "I assess AI pilot feasibility for your org. What's the problem you're trying to solve?"
      why: "Clear purpose, direct question, concise"
  
  bad:
    - response: "Welcome! I'm an AI-powered assessment system that uses advanced knowledge graphs to evaluate organizational readiness across multiple dimensions..."
      why: "Too long, technical jargon, feature-focused, no immediate value"
    
    - response: "I understand starting a new tool can be overwhelming. Let me walk you through how this works..."
      why: "Empathy theater, assumes user needs tutorial, delays value"

# PATTERN METADATA
metadata:
  version: "1.0"
  created: "2025-11-05"
  updated: "2025-11-05"
  author: "UX Exercise"
  status: "draft"  # draft | review | approved | deprecated
  
  related_principles:
    - "Safety & Trust (1)"
    - "Progressive Knowledge Building (2)"
    - "Volume Control (4)"
    - "Value-First Engagement (15)"
```

---

## Pattern Categories

### 1. Onboarding Patterns
**Trigger:** User knowledge gaps, first-time interactions  
**Goal:** Establish trust, show value, minimal friction

- `PATTERN_001_WELCOME_FIRST_TIME`
- `PATTERN_002_EXPLAIN_FEATURE_ON_FIRST_USE`
- `PATTERN_003_OFFER_NDA_EARLY`

### 2. Discovery Patterns
**Trigger:** User describes problem, system needs to identify output  
**Goal:** Narrow from vague to specific, identify output/team/system/process

- `PATTERN_010_OUTPUT_DISCOVERY`
- `PATTERN_011_VAGUE_PROBLEM_REFINEMENT`
- `PATTERN_012_ABSTRACT_TO_CONCRETE`
- `PATTERN_013_IDENTIFY_OUTPUT_TEAM_SYSTEM`

### 3. Assessment Patterns
**Trigger:** System needs factor ratings, user provides evidence  
**Goal:** Extract ratings naturally, classify evidence tiers

- `PATTERN_020_DEPENDENCY_QUALITY_ASSESSMENT`
- `PATTERN_021_TEAM_EXECUTION_ASSESSMENT`
- `PATTERN_022_PROCESS_MATURITY_ASSESSMENT`
- `PATTERN_023_SYSTEM_SUPPORT_ASSESSMENT`
- `PATTERN_024_HANDLE_CONTRADICTION`
- `PATTERN_025_HANDLE_I_DONT_KNOW`

### 4. Context Extraction Patterns (Agenda-Driven)
**Trigger:** Opportunity to extract business context naturally  
**Goal:** Sprinkle, don't survey - get timeline/budget/visibility

- `PATTERN_030_EXTRACT_TIMELINE_URGENCY`
- `PATTERN_031_EXTRACT_BUDGET_CONSTRAINTS`
- `PATTERN_032_EXTRACT_VISIBILITY_PREFERENCE`
- `PATTERN_033_EXTRACT_STAKEHOLDER_PRESSURE`
- `PATTERN_034_EXTRACT_VENDOR_CONSTRAINTS`

### 5. Navigation Patterns
**Trigger:** User lost, needs orientation, or natural checkpoint  
**Goal:** Show where they are, what they can do, what's next

- `PATTERN_040_STATUS_QUERY_WHERE_ARE_WE`
- `PATTERN_041_PROGRESS_MILESTONE_REACHED`
- `PATTERN_042_NEXT_TIER_WHATS_MISSING`
- `PATTERN_043_CONVERSATION_CONTINUITY`

### 6. Education Patterns (Just-in-Time)
**Trigger:** User encounters feature first time OR asks explicit question  
**Goal:** Explain when relevant, not upfront

- `PATTERN_050_USER_ASKS_HOW_IT_WORKS`
- `PATTERN_051_USER_ASKS_ABOUT_DATA_PRIVACY`
- `PATTERN_052_EXPLAIN_STAR_RATING_FIRST_USE`
- `PATTERN_053_EXPLAIN_EVIDENCE_TIERS_FIRST_USE`
- `PATTERN_054_EXPLAIN_MIN_CALCULATION_FIRST_USE`

### 7. Analysis Patterns
**Trigger:** Assessment complete, system identifies bottlenecks  
**Goal:** Show MIN calculation, identify root causes

- `PATTERN_060_IDENTIFY_BOTTLENECK`
- `PATTERN_061_EXPLAIN_MIN_RESULT`
- `PATTERN_062_CATEGORIZE_ROOT_CAUSE`
- `PATTERN_063_SHOW_DEPENDENCY_CHAIN`

### 8. Recommendation Patterns
**Trigger:** User asks for solutions, or system has enough context  
**Goal:** Map bottleneck → AI pilot category → specific pilots

- `PATTERN_070_GENERATE_PILOT_OPTIONS`
- `PATTERN_071_CHECK_PREREQUISITES`
- `PATTERN_072_EXPLAIN_FEASIBILITY`
- `PATTERN_073_OFFER_COMPREHENSIVE_REPORT`

### 9. Error Recovery Patterns
**Trigger:** User confused, contradicts self, or system uncertain  
**Goal:** Graceful handling, don't lose progress

- `PATTERN_080_CLARIFY_CONTRADICTION`
- `PATTERN_081_HANDLE_UNKNOWN_SYSTEM`
- `PATTERN_082_HANDLE_OUT_OF_SCOPE`
- `PATTERN_083_RECOVER_FROM_CONFUSION`

### 10. Meta Patterns
**Trigger:** User wants to review, edit, export, or challenge  
**Goal:** User control, transparency, portability

- `PATTERN_090_REVIEW_CAPTURED_DATA`
- `PATTERN_091_EDIT_PREVIOUS_ANSWER`
- `PATTERN_092_CHALLENGE_ASSUMPTION`
- `PATTERN_093_EXPORT_ASSESSMENT`
- `PATTERN_094_GENERATE_TECH_QUESTIONNAIRE`

---

## Trigger Types Explained

### User-Explicit
**Definition:** User directly asks for something  
**Examples:**
- "Where are we?"
- "How does this work?"
- "Can we do sales forecasting?"

**Detection:** Keyword matching, intent classification

### User-Implicit
**Definition:** User's statement implies a need  
**Examples:**
- User says "I'm lost" → trigger navigation pattern
- User contradicts earlier statement → trigger clarification pattern
- User mentions abstract problem → trigger concrete refinement pattern

**Detection:** Semantic analysis, context comparison

### System-Proactive
**Definition:** System initiates based on opportunity  
**Examples:**
- User mentions "board pressure" → extract timeline urgency
- Assessment complete → offer status summary
- User describes pain intensity → extract business impact

**Detection:** Agenda-driven goals + context monitoring

### System-Reactive
**Definition:** System responds to state changes  
**Examples:**
- First message in session → welcome pattern
- Contradiction detected → clarification pattern
- Unknown system mentioned → discovery pattern

**Detection:** State monitoring, rule-based triggers

---

## Knowledge Prerequisites

### User Knowledge Dimensions
```yaml
user_knowledge:
  # System Understanding
  knows_system_purpose: bool
  knows_how_to_start: bool
  knows_can_edit_answers: bool
  knows_can_pause_resume: bool
  knows_data_is_private: bool
  
  # Feature Understanding
  knows_star_rating_scale: bool
  knows_evidence_tiers: bool
  knows_min_calculation: bool
  knows_can_challenge_assumptions: bool
  knows_can_export: bool
  
  # Domain Understanding
  knows_output_centric_model: bool
  knows_four_components: bool
  knows_dependency_concept: bool
  knows_bottleneck_identification: bool
  
  # Progress Understanding
  knows_current_phase: string  # discovery | assessment | analysis | recommendations
  knows_what_unlocked: []  # list of capabilities
  
  # Interaction History
  session_count: int
  conversation_turn: int
  has_seen_pattern: {}  # pattern_id -> count
```

### System Knowledge Dimensions
```yaml
system_knowledge:
  # Assessment State
  identified_output: bool
  output_id: string | null
  team_identified: bool
  system_identified: bool
  process_identified: bool
  
  # Factor Assessments
  dependency_quality_assessed: bool
  team_execution_assessed: bool
  process_maturity_assessed: bool
  system_support_assessed: bool
  
  # Evidence Collected
  evidence_count: int
  evidence_by_tier: {}  # tier -> count
  confidence_level: float
  
  # Business Context
  timeline_urgency_known: bool
  budget_constraints_known: bool
  visibility_preference_known: bool
  stakeholder_pressure_known: bool
  
  # Analysis State
  bottleneck_identified: bool
  root_cause_categorized: bool
  
  # Recommendation State
  pilots_generated: bool
  feasibility_checked: bool
  report_offered: bool
```

---

## Pattern Dependencies

### Dependency Types

**1. Knowledge Prerequisites**
```yaml
requires:
  user_knowledge:
    knows_star_rating_scale: true
  system_knowledge:
    identified_output: true
```

**2. State Prerequisites**
```yaml
requires:
  assessment_state:
    phase: "assessment"
    components_assessed: ["dependency_quality", "team_execution"]
```

**3. Data Prerequisites**
```yaml
requires:
  data_availability:
    output_catalog_loaded: true
    inference_rules_loaded: true
```

**4. Context Prerequisites**
```yaml
requires:
  conversation_context:
    min_turns: 3
    has_user_problem_statement: true
```

---

## Pattern Priority Resolution

When multiple patterns could trigger simultaneously:

```yaml
priority_rules:
  1_critical:
    - "Error recovery patterns"
    - "User-explicit requests"
  
  2_high:
    - "First-time onboarding"
    - "Contradiction handling"
    - "Out-of-scope detection"
  
  3_medium:
    - "Context extraction (agenda-driven)"
    - "Navigation patterns"
    - "Just-in-time education"
  
  4_low:
    - "Proactive status offers"
    - "Milestone celebrations"
    - "Optional optimizations"

conflict_resolution:
  - "Higher priority always wins"
  - "Within same priority: user-triggered > system-triggered"
  - "Within same type: more specific > more generic"
  - "Defer lower priority patterns to next turn"
```

---

## Test Format

### Semantic Tests (LLM-Based)
```yaml
semantic_test:
  pattern_id: "PATTERN_001_WELCOME_FIRST_TIME"
  
  input:
    user_message: null  # First message, no user input
    user_knowledge: {knows_system_purpose: false}
    system_state: {conversation_turn: 1}
  
  expected_behavior:
    response_contains:
      - "system purpose statement"
      - "question to user"
    
    response_does_not_contain:
      - "feature explanations"
      - "empathy phrases"
      - "technical jargon"
    
    response_constraints:
      max_words: 30
      tone: "professional, direct"
  
  validation_method: "llm_semantic_check"
  
  llm_validation_prompt: |
    Analyze this system response:
    "{response}"
    
    Check:
    1. Does it contain a clear statement of system purpose? (yes/no)
    2. Does it ask the user a question? (yes/no)
    3. Does it explain features or how the system works? (yes/no - should be NO)
    4. Does it use empathy phrases like "I understand" or "must be frustrating"? (yes/no - should be NO)
    5. Word count: {count}
    6. Tone assessment: professional and direct? (yes/no)
    
    Return: PASS/FAIL with reasons
```

### Behavioral Tests (State-Based)
```yaml
behavioral_test:
  pattern_id: "PATTERN_001_WELCOME_FIRST_TIME"
  
  input:
    user_knowledge: {knows_system_purpose: false, session_count: 0}
    system_state: {conversation_turn: 1}
  
  expected_state_changes:
    user_knowledge:
      knows_system_purpose: true
      knows_how_to_start: true
    
    system_state:
      conversation_turn: 2
      conversation_started: true
  
  validation_method: "state_assertion"
```

### Integration Tests (End-to-End)
```yaml
integration_test:
  scenario: "First-time user discovers output"
  
  conversation_flow:
    - turn: 1
      pattern: "PATTERN_001_WELCOME_FIRST_TIME"
      user_input: null
      expected_pattern_triggered: true
      expected_response_type: "welcome_with_question"
    
    - turn: 2
      pattern: "PATTERN_010_OUTPUT_DISCOVERY"
      user_input: "Sales forecasts are always wrong"
      expected_pattern_triggered: true
      expected_response_type: "output_identification_with_confirmation"
    
    - turn: 3
      pattern: "PATTERN_013_IDENTIFY_OUTPUT_TEAM_SYSTEM"
      user_input: "Yes, sales forecast"
      expected_pattern_triggered: true
      expected_response_type: "context_questions"
  
  final_state_assertions:
    user_knowledge:
      knows_system_purpose: true
      knows_how_to_start: true
    
    system_knowledge:
      identified_output: true
      output_id: "sales_forecast"
```

---

## Usage Guidelines

### For LLM Conversation Engine

**Pattern Selection:**
1. Evaluate all trigger conditions
2. Filter patterns where conditions are met
3. Apply priority resolution
4. Execute highest priority pattern
5. Update knowledge states
6. Queue next likely patterns

**Response Generation:**
1. Use response_template as base
2. Apply response_constraints
3. Inject dynamic context
4. Validate against tests
5. Update teaches_user knowledge

### For Test Engine

**Test Execution:**
1. Load pattern definition
2. Set up input state
3. Execute conversation turn
4. Run semantic validations (LLM)
5. Run behavioral validations (state)
6. Assert expected outcomes
7. Report pass/fail with details

**Test Coverage:**
1. Every pattern has semantic tests
2. Every pattern has behavioral tests
3. Critical flows have integration tests
4. Edge cases have specific tests

---

## Pattern Evolution

### Version Control
```yaml
pattern_version:
  version: "1.2"
  changelog:
    - version: "1.0"
      date: "2025-11-05"
      changes: "Initial pattern definition"
    
    - version: "1.1"
      date: "2025-11-10"
      changes: "Added budget extraction trigger"
    
    - version: "1.2"
      date: "2025-11-15"
      changes: "Refined response template based on user feedback"
```

### A/B Testing Support
```yaml
pattern_variants:
  variant_a:
    response_template: "Version A text..."
    weight: 0.5
  
  variant_b:
    response_template: "Version B text..."
    weight: 0.5
  
  metrics:
    - "user_engagement_rate"
    - "conversation_completion_rate"
    - "user_satisfaction_score"
```

---

## File Organization

```
sandbox/conversation_ux_exercise/
├── PATTERN_FORMAT.md              # This file (format spec)
├── WHAT_MAKES_CONVERSATION_GOOD.md  # Principles
│
├── patterns/
│   ├── onboarding/
│   │   ├── PATTERN_001_welcome_first_time.yaml
│   │   ├── PATTERN_002_explain_feature_first_use.yaml
│   │   └── PATTERN_003_offer_nda_early.yaml
│   │
│   ├── discovery/
│   │   ├── PATTERN_010_output_discovery.yaml
│   │   ├── PATTERN_011_vague_problem_refinement.yaml
│   │   └── ...
│   │
│   ├── assessment/
│   ├── context_extraction/
│   ├── navigation/
│   ├── education/
│   ├── analysis/
│   ├── recommendation/
│   ├── error_recovery/
│   └── meta/
│
├── tests/
│   ├── semantic/
│   │   └── test_pattern_001_semantic.yaml
│   ├── behavioral/
│   │   └── test_pattern_001_behavioral.yaml
│   └── integration/
│       └── test_first_time_user_flow.yaml
│
└── scenarios/
    ├── SCENARIO_001_first_time_user.md
    ├── SCENARIO_002_returning_user.md
    └── ...
```

---

## Next Steps

1. **Create First Pattern:** `PATTERN_001_WELCOME_FIRST_TIME`
2. **Create Test Suite:** Semantic + Behavioral tests
3. **Build Pattern Library:** 10-15 core patterns
4. **Create Scenarios:** User journeys using patterns
5. **Validate Format:** Ensure LLM + test engine can consume
6. **Iterate:** Refine based on actual usage

---

**Status:** Format specification complete, ready for pattern creation  
**Next:** Create first pattern using this template
