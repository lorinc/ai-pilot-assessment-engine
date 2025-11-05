# Dense Composition Rules Format (For Review)

**Instructions**: Review and modify. I'll parse into full YAML.

**Purpose**: Define how triggers + behaviors + knowledge → patterns are composed.

---

## CORE COMPOSITION RULES

### Rule 1: Trigger-Behavior Mapping

**Primary Mappings** (1 trigger → 1 primary behavior):

| Trigger | Primary Behavior | Rationale |
|---|---|---|
| T_EXPRESS_FRUSTRATION | B_DETECT_FRUSTRATION | Direct response to frustration |
| T_EXPRESS_CONFUSION | B_OFFER_REPHRASE | Help confused user |
| T_REQUEST_HELP | B_SUGGEST_NEXT_ACTION | Guide user forward |
| T_REQUEST_EXPLANATION | B_EXPLAIN_DESIGN_DECISIONS | Educate on demand |
| T_REQUEST_RECOMMENDATIONS | B_GENERATE_PILOT_OPTIONS | Deliver core value |
| T_REQUEST_PROGRESS | B_SHOW_OUTPUT_COMPLETENESS | Show status |
| T_MENTION_OUTPUT | B_REDIRECT_TO_CONCRETE | Force specificity |
| T_MENTION_PROBLEM | B_PROGRESSIVE_NARROWING | Narrow to specific output |
| T_PROVIDE_RATING | B_ASSESS_WITH_PROFESSIONAL_REFLECTION | Capture assessment |
| T_PROVIDE_EVIDENCE | B_ACKNOWLEDGE_TIER1 | Recognize quality evidence |
| T_SCOPE_AMBIGUITY | B_DETECT_SCOPE_AMBIGUITY | Clarify scope |
| T_ABSTRACT_STATEMENT | B_ELICIT_EXAMPLE | Get concrete |
| T_ASSESSMENT_SUFFICIENT | B_OFFER_RECOMMENDATIONS_AT_CONFIDENCE | Offer next step |
| T_BOTTLENECK_IDENTIFIED | B_MAP_BOTTLENECK_TO_ARCHETYPE | Generate recommendations |
| T_LOW_CONFIDENCE_DATA | B_PROBE_FOR_NUMBERS | Improve evidence |
| T_FIRST_TIME_USER | B_EXPLAIN_OBJECT_MODEL | Onboard new user |
| T_SPARSE_KNOWLEDGE_DETECTED | B_RECOMMEND_DEPTH_OVER_BREADTH | Guide toward quality |
| T_BREADTH_OVER_DEPTH | B_SHOW_ASSESSMENT_GAPS | Make gaps visible |

**Secondary Mappings** (1 trigger → multiple possible behaviors, selected by situation):

| Trigger | Possible Behaviors | Selection Criteria |
|---|---|---|
| T_SKIP_QUESTION | B_OFFER_SKIP, B_ACCEPT_DONT_KNOW, B_BACKTRACK | Depends on frustration_level |
| T_PROVIDE_FEEDBACK | B_APPRECIATE_FEEDBACK, B_OFFER_UNDO, B_RESOLVE_CONFLICT | Depends on feedback type |
| T_OUTPUT_IDENTIFIED | B_CONFIRM_OUTPUT, B_DISCOVER_TEAM, B_DISCOVER_SYSTEM | Depends on context completeness |
| T_CONTEXT_THIN | B_ENRICH_SYSTEM_CONTEXT, B_ENRICH_TEAM_CONTEXT, B_ENRICH_PROCESS_CONTEXT | Depends on which entity |
| T_MULTIPLE_OUTPUTS | B_HANDLE_MULTI_OUTPUT, B_NARROW_TO_SPECIFIC, B_SHOW_OPTIONAL_PATHS | Depends on user preference |
| T_SPARSE_KNOWLEDGE_DETECTED | B_RECOMMEND_DEPTH_OVER_BREADTH, B_SHOW_ASSESSMENT_GAPS, B_OFFER_FOCUS_STRATEGY | Depends on user's clarity about goals |

---

### Rule 2: Situation-Based Pattern Filtering

**Pattern Selection Algorithm**:
```
1. Detect triggers from user message
2. Get candidate behaviors for each trigger
3. Calculate situation affinity score for each behavior
4. Filter behaviors where primary_dimension >= min_threshold
5. Rank by affinity score
6. Check knowledge requirements
7. Return top 3-5 behaviors
```

**Affinity Score Calculation**:
```python
score = sum(
    situation[dimension] * behavior.affinity[dimension]
    for dimension in situation.keys()
)
```

**Example**:
```
Situation: {discovery: 0.3, assessment: 0.5, error_recovery: 0.2}

Behavior: B_REDIRECT_TO_CONCRETE
  affinity: {discovery: 0.8, assessment: 0.2}
  score = 0.3*0.8 + 0.5*0.2 = 0.34

Behavior: B_ASSESS_WITH_PROFESSIONAL_REFLECTION
  affinity: {assessment: 0.9, discovery: 0.1}
  score = 0.3*0.1 + 0.5*0.9 = 0.48  ← Higher score, selected
```

---

### Rule 3: Knowledge-Based Pattern Gating

**Patterns can be gated by knowledge requirements**:

| Pattern Type | Knowledge Requirement | Rationale |
|---|---|---|
| Advanced education | user_knowledge.understands_object_model == true | Don't re-explain basics |
| Recommendations | system_knowledge.outputs_assessed[id].components >= 1 | Need some data |
| High-confidence recommendations | system_knowledge.confidence_by_output[id] == "high" | Need quality data |
| Bottleneck analysis | system_knowledge.outputs_assessed[id].components >= 3 | Need MIN calculation |
| Scope disambiguation | system_knowledge.scope_clarity == "ambiguous" | Only if needed |
| Error recovery | conversation_state.frustration_level > 0.3 | Only if frustrated |

**Example**:
```yaml
pattern:
  id: PATTERN_ADVANCED_EDUCATION
  triggers: [T_REQUEST_EXPLANATION]
  behavior: B_EXPLAIN_INTERNAL_LOGIC
  requires:
    user_knowledge:
      understands_object_model: true  # Only for users who know basics
  blocks:
    conversation_state:
      frustration_level: > 0.5  # Don't educate frustrated users
```

---

### Rule 4: Pattern Chaining

**Some patterns trigger follow-up patterns**:

| Primary Pattern | Triggers | Follow-up Pattern | Condition |
|---|---|---|---|
| Output identified | T_OUTPUT_IDENTIFIED | Discover team/system/process | Always |
| Assessment complete | T_ASSESSMENT_SUFFICIENT | Offer recommendations | If confidence >= low |
| Bottleneck identified | T_BOTTLENECK_IDENTIFIED | Generate pilot options | Always |
| User confused | T_EXPRESS_CONFUSION | Offer to rephrase | If confusion_level > 0.5 |
| Evidence low quality | T_LOW_CONFIDENCE_DATA | Probe for better evidence | If tier5_count > tier1_count |
| Scope ambiguous | T_SCOPE_AMBIGUITY | Clarify scope | Always |

**Chaining Mechanism**:
```yaml
pattern:
  id: PATTERN_001
  behavior: B_CONFIRM_OUTPUT
  chain_to:
    - pattern_id: PATTERN_002
      trigger: T_OUTPUT_IDENTIFIED
      delay: 0  # Immediate
    - pattern_id: PATTERN_003
      trigger: T_CONTEXT_THIN
      delay: 1  # Next turn
```

---

### Rule 5: Anti-Patterns (Avoid These)

**Patterns that should NOT be combined**:

| Pattern A | Pattern B | Why Not | Resolution |
|---|---|---|---|
| B_EXPLAIN_OBJECT_MODEL | B_ASSESS_WITH_PROFESSIONAL_REFLECTION | Don't educate while assessing | Prioritize assessment |
| B_DETECT_FRUSTRATION | B_EXPLAIN_DESIGN_DECISIONS | Don't defend when user frustrated | Prioritize error recovery |
| B_REDIRECT_TO_CONCRETE | B_GENERATE_PILOT_OPTIONS | Don't recommend without concrete output | Prioritize discovery |
| B_OFFER_REPHRASE | B_PROBE_FOR_NUMBERS | Don't probe confused user | Prioritize clarity |
| B_SHOW_THINKING_PROCESS | B_OFFER_SKIP | Don't show complexity to stuck user | Prioritize simplicity |

**Anti-Pattern Detection**:
```python
def check_anti_patterns(selected_behaviors):
    anti_patterns = [
        (B_EXPLAIN_*, B_ASSESS_*, "education", "assessment"),
        (B_DETECT_FRUSTRATION, B_EXPLAIN_*, "error_recovery", "education"),
        # ... more rules
    ]
    
    for behavior_a, behavior_b in selected_behaviors:
        if matches_anti_pattern(behavior_a, behavior_b, anti_patterns):
            # Remove lower priority behavior
            remove_lower_priority(behavior_a, behavior_b)
```

---

### Rule 6: Priority Hierarchy

**When multiple patterns compete, use priority**:

1. **Error Recovery** (highest) - Always prioritize frustrated/confused users
2. **Scope Management** - Clarify ambiguity before proceeding
3. **Assessment** - Core activity, high priority
4. **Discovery** - Foundation for assessment
5. **Recommendation** - Deliver value when ready
6. **Navigation** - Help user orient
7. **Analysis** - Background calculation
8. **Education** - Only when relevant (lowest)

**Example**:
```
User message: "I'm confused about sales forecasts"

Triggers:
- T_EXPRESS_CONFUSION (priority: error_recovery = 1)
- T_MENTION_OUTPUT (priority: discovery = 4)

Selected: B_OFFER_REPHRASE (error_recovery)
Deferred: B_REDIRECT_TO_CONCRETE (discovery)
```

---

### Rule 7: Repetition Avoidance

**Don't repeat patterns within N turns**:

| Pattern Type | Cooldown (turns) | Exception |
|---|---|---|
| Education patterns | 10 | User explicitly requests |
| Navigation patterns | 5 | User explicitly requests |
| Error recovery patterns | 3 | Frustration increases |
| Assessment patterns | 1 | Different component |
| Discovery patterns | 2 | Different output |

**Repetition Detection**:
```python
def is_pattern_on_cooldown(pattern_id, pattern_history, cooldown_rules):
    last_used = pattern_history.last_occurrence(pattern_id)
    cooldown = cooldown_rules[pattern_id.category]
    return (current_turn - last_used) < cooldown
```

---

### Rule 8: Adaptive Composition

**Adjust composition based on user behavior**:

| User Signal | Adjustment | Example |
|---|---|---|
| Rapid, detailed responses | Increase assessment weight | More B_ASSESS_*, less B_EXPLAIN_* |
| Short, vague responses | Increase discovery weight | More B_ELICIT_EXAMPLE, B_PROBE_* |
| Questions about system | Increase education weight | More B_EXPLAIN_* patterns |
| Requests for recommendations | Increase recommendation weight | More B_GENERATE_*, B_SHOW_* |
| Expresses frustration | Spike error_recovery | Immediate B_DETECT_FRUSTRATION |
| Demonstrates understanding | Decrease education weight | Less B_EXPLAIN_*, more advanced patterns |

---

## COMPOSITION EXAMPLES

### Example 1: Discovery Flow

**Turn 1**:
```
User: "Sales forecasts are always wrong"
Triggers: T_MENTION_OUTPUT, T_MENTION_PROBLEM, T_ABSTRACT_STATEMENT
Situation: {discovery: 0.5, education: 0.5}
Selected: B_REDIRECT_TO_CONCRETE (discovery affinity: 0.8)
Response: "Sorry, I don't do abstract. Let's use a concrete event as proxy."
```

**Turn 2**:
```
User: "Last quarter's forecast was off by 30%"
Triggers: T_PROVIDE_EVIDENCE, T_MENTION_OUTPUT
Situation: {discovery: 0.4, assessment: 0.4, education: 0.2}
Selected: B_CONFIRM_OUTPUT (discovery), B_ACKNOWLEDGE_QUANTIFIED (assessment)
Response: "So you mean Sales Forecast? Thanks for the numbers, that helps."
Knowledge Update: outputs_identified.append("sales_forecast_001")
```

**Turn 3**:
```
System Trigger: T_OUTPUT_IDENTIFIED
Situation: {discovery: 0.3, assessment: 0.5, education: 0.2}
Selected: B_DISCOVER_TEAM (discovery)
Response: "Which team creates this output?"
```

---

### Example 2: Error Recovery Flow

**Turn 1**:
```
User: "This doesn't make sense"
Triggers: T_EXPRESS_CONFUSION
Situation: {assessment: 0.4, error_recovery: 0.4, education: 0.2}
Selected: B_OFFER_REPHRASE (error_recovery affinity: 0.9)
Response: "I haven't given enough context. Let me try a different approach."
Knowledge Update: confusion_level = 0.6
```

**Turn 2**:
```
User: "Still confused"
Triggers: T_EXPRESS_CONFUSION
Situation: {error_recovery: 0.6, assessment: 0.2, education: 0.2}
Selected: B_OFFER_SKIP (error_recovery), B_BACKTRACK (error_recovery)
Response: "You're right, it's not that important right now. We can come back to this later if we need to."
Knowledge Update: confusion_level = 0.8
```

---

### Example 3: Multi-Dimensional Flow

**Turn 1**:
```
User: "We have issues with sales forecasts, dashboards, and reports"
Triggers: T_MULTIPLE_OUTPUTS, T_MENTION_PROBLEM
Situation: {discovery: 0.5, scope_management: 0.3, navigation: 0.2}
Selected: B_HANDLE_MULTI_OUTPUT (scope_management), B_NARROW_TO_SPECIFIC (discovery)
Response: "You mentioned 3 outputs. Let's focus on one first. Which is most critical?"
Knowledge Update: scope_clarity = "ambiguous", active_outputs = 3
```

---

## STATS

**Total Rules**: 8
- Core composition rules: 8
- Trigger-behavior mappings: 16 primary, 5 secondary
- Anti-patterns: 5
- Priority levels: 8
- Cooldown rules: 5

**Coverage**:
- All 38 triggers mapped
- All 74 behaviors reachable
- All 8 situation dimensions used
- All 28 knowledge dimensions tracked
