# Pattern Composition Strategy

**Goal:** Maximize pattern coverage with minimal human effort  
**Approach:** Define atomic building blocks, compose into patterns, generate variations

---

## The Leverage Opportunity

### Traditional Approach (Linear Effort)
```
Human writes 100 patterns × 30 min each = 50 hours
```

### Compositional Approach (Exponential Benefit)
```
Human defines:
- 10 atomic triggers      × 10 min = 100 min
- 10 atomic behaviors     × 10 min = 100 min
- 5 knowledge dimensions  × 5 min  = 25 min
- 3 composition rules     × 15 min = 45 min
                          ─────────────────
                          Total: 270 min (4.5 hours)

System generates:
- 10 × 10 × 5 = 500 pattern combinations
- Human reviews/curates top 100 = 5 hours
                          ─────────────────
                          Total: 9.5 hours vs 50 hours
```

**5x efficiency gain + better consistency**

---

## Step 1: Define Atomic Triggers (10-15 primitives)

**Human Input:** Identify the fundamental trigger types

```yaml
# atomic_triggers.yaml

triggers:
  # USER-EXPLICIT TRIGGERS
  - id: "T_STATUS_QUERY"
    type: "user_explicit"
    keywords: ["where are we", "what's our progress", "status"]
    intent: "user wants orientation"
    
  - id: "T_HOW_IT_WORKS"
    type: "user_explicit"
    keywords: ["how does this work", "explain", "what is this"]
    intent: "user needs education"
  
  - id: "T_FEASIBILITY_CHECK"
    type: "user_explicit"
    keywords: ["can we do", "is it possible", "would this work"]
    intent: "user wants recommendation"
  
  # USER-IMPLICIT TRIGGERS
  - id: "T_CONTRADICTION_DETECTED"
    type: "user_implicit"
    signal: "current_statement contradicts previous_statement"
    detection: "semantic_comparison"
  
  - id: "T_CONFUSION_DETECTED"
    type: "user_implicit"
    signal: "user expresses uncertainty or confusion"
    keywords: ["I don't know", "not sure", "confused", "lost"]
  
  - id: "T_ABSTRACT_STATEMENT"
    type: "user_implicit"
    signal: "user describes problem in abstract terms"
    detection: "lacks concrete output/team/system/process"
  
  # SYSTEM-PROACTIVE TRIGGERS
  - id: "T_URGENCY_SIGNAL"
    type: "system_proactive"
    signal: "user mentions time pressure"
    keywords: ["urgent", "deadline", "board", "asap", "quickly"]
    extracts: "timeline_urgency"
  
  - id: "T_COST_SIGNAL"
    type: "system_proactive"
    signal: "user mentions money or resources"
    keywords: ["budget", "cost", "expensive", "€", "$", "spend"]
    extracts: "budget_constraints"
  
  - id: "T_STAKEHOLDER_SIGNAL"
    type: "system_proactive"
    signal: "user mentions leadership or visibility"
    keywords: ["CEO", "board", "VP", "showcase", "demo", "visible"]
    extracts: "visibility_preference"
  
  # SYSTEM-REACTIVE TRIGGERS
  - id: "T_FIRST_MESSAGE"
    type: "system_reactive"
    condition: "conversation_turn == 1"
  
  - id: "T_ASSESSMENT_COMPLETE"
    type: "system_reactive"
    condition: "all_four_components_assessed == true"
  
  - id: "T_UNKNOWN_ENTITY"
    type: "system_reactive"
    condition: "user_mentions_unknown_system_or_output"
  
  - id: "T_MILESTONE_REACHED"
    type: "system_reactive"
    condition: "significant_state_change"
    examples: ["output_identified", "bottleneck_found", "pilots_generated"]
```

**Effort:** 10-15 triggers × 10 min = **2-3 hours**

---

## Step 2: Define Atomic Behaviors (10-15 primitives)

**Human Input:** Identify the fundamental response types

```yaml
# atomic_behaviors.yaml

behaviors:
  # INFORMATION GATHERING
  - id: "B_ASK_CLARIFYING_QUESTION"
    goal: "Get specific information to resolve ambiguity"
    template: |
      {clarification_needed}
      
      {specific_question}
    constraints:
      max_questions: 1
      tone: "helpful, not interrogative"
  
  - id: "B_EXTRACT_CONTEXT"
    goal: "Capture business context naturally"
    template: |
      {acknowledge_statement}
      
      {follow_up_that_extracts_context}
    constraints:
      max_words: 30
      must_feel_natural: true
  
  # INFORMATION DELIVERY
  - id: "B_SHOW_STATUS"
    goal: "Orient user on current state"
    template: |
      {what_we_know}
      
      {what_you_can_do_now}
      
      {next_options}
    constraints:
      max_words: 100
      must_show_value: true
  
  - id: "B_EXPLAIN_CONCEPT"
    goal: "Teach just-in-time"
    template: |
      {concept_explanation_one_sentence}
      
      {why_it_matters_to_user}
    constraints:
      max_words: 40
      only_when_relevant: true
  
  - id: "B_GENERATE_OPTIONS"
    goal: "Provide 2-3 choices"
    template: |
      {context_summary}
      
      {option_1}
      {option_2}
      {option_3}
      
      {which_interests_you}
    constraints:
      num_options: [2, 3]
      must_be_actionable: true
  
  # VALIDATION & CORRECTION
  - id: "B_CONFIRM_UNDERSTANDING"
    goal: "Validate inference with user"
    template: |
      {what_i_understood}
      
      {is_this_correct}
    constraints:
      max_words: 30
      must_be_specific: true
  
  - id: "B_RESOLVE_CONTRADICTION"
    goal: "Help user clarify conflicting statements"
    template: |
      Earlier you said {previous_statement}.
      Now you're saying {current_statement}.
      
      {clarifying_question}
    constraints:
      tone: "neutral, not accusatory"
      max_words: 40
  
  # GUIDANCE & NAVIGATION
  - id: "B_OFFER_NEXT_STEPS"
    goal: "Show clear path forward"
    template: |
      {what_we_just_accomplished}
      
      {next_step_options}
    constraints:
      num_options: [2, 3]
      must_show_progress: true
  
  - id: "B_REDIRECT_TO_CONCRETE"
    goal: "Move from abstract to specific"
    template: |
      Sorry, I do not do abstract. Let's pick a concrete example.
      
      {specific_question}
    constraints:
      must_request_example: true
      tone: "direct, professional"
  
  # ANALYSIS & INSIGHT
  - id: "B_IDENTIFY_BOTTLENECK"
    goal: "Show MIN calculation result"
    template: |
      {component_ratings}
      
      The bottleneck is {min_component} at {rating}.
      
      {what_this_means}
    constraints:
      must_explain_min: true
      max_words: 60
  
  - id: "B_RECOMMEND_PILOTS"
    goal: "Map bottleneck to AI solutions"
    template: |
      Based on {bottleneck_type}, here are {num} options:
      
      {pilot_options_with_feasibility}
      
      {which_interests_you}
    constraints:
      num_options: [2, 3]
      must_show_feasibility: true
```

**Effort:** 10-15 behaviors × 10 min = **2-3 hours**

---

## Step 3: Define Knowledge Dimensions (5-10 dimensions)

**Human Input:** Identify what knowledge gates which patterns

```yaml
# knowledge_dimensions.yaml

user_knowledge:
  # System Understanding (gates onboarding patterns)
  - dimension: "system_awareness"
    states:
      - knows_nothing: "First-time user, no context"
      - knows_purpose: "Understands what system does"
      - knows_how_to_use: "Can navigate and interact"
      - power_user: "Knows advanced features"
  
  # Feature Understanding (gates education patterns)
  - dimension: "feature_awareness"
    states:
      - unaware: "Hasn't encountered feature"
      - first_use: "Using feature for first time"
      - familiar: "Has used feature before"
  
  # Domain Understanding (gates assessment patterns)
  - dimension: "model_awareness"
    states:
      - no_context: "Doesn't know output-centric model"
      - basic: "Knows output/team/system/process"
      - advanced: "Understands MIN, dependencies, bottlenecks"

system_knowledge:
  # Assessment Progress (gates analysis patterns)
  - dimension: "assessment_completeness"
    states:
      - not_started: "No output identified"
      - discovery: "Output identified, no ratings"
      - partial: "Some components assessed"
      - complete: "All four components assessed"
  
  # Context Richness (gates recommendation patterns)
  - dimension: "business_context"
    states:
      - minimal: "No business constraints known"
      - partial: "Some constraints known (1-2)"
      - rich: "Most constraints known (3+)"
```

**Effort:** 5-10 dimensions × 5 min = **30-60 min**

---

## Step 4: Define Composition Rules

**Human Input:** How triggers + behaviors + knowledge combine

```yaml
# composition_rules.yaml

rules:
  # Rule 1: Onboarding patterns
  - name: "First-time user patterns"
    trigger_types: ["system_reactive"]
    trigger_conditions: ["T_FIRST_MESSAGE"]
    user_knowledge: {system_awareness: "knows_nothing"}
    behaviors: ["B_EXPLAIN_CONCEPT", "B_ASK_CLARIFYING_QUESTION"]
    priority: "high"
    generates:
      - PATTERN_001_WELCOME_FIRST_TIME
  
  # Rule 2: Context extraction patterns (agenda-driven)
  - name: "Opportunistic context extraction"
    trigger_types: ["system_proactive"]
    trigger_conditions: ["T_URGENCY_SIGNAL", "T_COST_SIGNAL", "T_STAKEHOLDER_SIGNAL"]
    system_knowledge: {business_context: ["minimal", "partial"]}
    behaviors: ["B_EXTRACT_CONTEXT"]
    priority: "medium"
    generates:
      - PATTERN_030_EXTRACT_TIMELINE_URGENCY
      - PATTERN_031_EXTRACT_BUDGET_CONSTRAINTS
      - PATTERN_032_EXTRACT_VISIBILITY_PREFERENCE
  
  # Rule 3: Education patterns (just-in-time)
  - name: "Just-in-time education"
    trigger_types: ["user_explicit", "system_reactive"]
    trigger_conditions: ["T_HOW_IT_WORKS", "T_FIRST_USE_*"]
    user_knowledge: {feature_awareness: ["unaware", "first_use"]}
    behaviors: ["B_EXPLAIN_CONCEPT"]
    priority: "high"
    generates:
      - PATTERN_050_USER_ASKS_HOW_IT_WORKS
      - PATTERN_052_EXPLAIN_STAR_RATING_FIRST_USE
      - PATTERN_053_EXPLAIN_EVIDENCE_TIERS_FIRST_USE
  
  # Rule 4: Error recovery patterns
  - name: "Handle user confusion"
    trigger_types: ["user_implicit"]
    trigger_conditions: ["T_CONTRADICTION_DETECTED", "T_CONFUSION_DETECTED"]
    behaviors: ["B_RESOLVE_CONTRADICTION", "B_ASK_CLARIFYING_QUESTION"]
    priority: "critical"
    generates:
      - PATTERN_024_HANDLE_CONTRADICTION
      - PATTERN_080_CLARIFY_CONTRADICTION
      - PATTERN_083_RECOVER_FROM_CONFUSION
  
  # Rule 5: Navigation patterns
  - name: "User orientation"
    trigger_types: ["user_explicit", "system_reactive"]
    trigger_conditions: ["T_STATUS_QUERY", "T_MILESTONE_REACHED"]
    behaviors: ["B_SHOW_STATUS", "B_OFFER_NEXT_STEPS"]
    priority: "medium"
    generates:
      - PATTERN_040_STATUS_QUERY_WHERE_ARE_WE
      - PATTERN_041_PROGRESS_MILESTONE_REACHED
  
  # Rule 6: Assessment patterns
  - name: "Gather component ratings"
    trigger_types: ["system_reactive"]
    trigger_conditions: ["T_OUTPUT_IDENTIFIED"]
    system_knowledge: {assessment_completeness: ["discovery", "partial"]}
    behaviors: ["B_ASK_CLARIFYING_QUESTION", "B_CONFIRM_UNDERSTANDING"]
    priority: "medium"
    generates:
      - PATTERN_020_DEPENDENCY_QUALITY_ASSESSMENT
      - PATTERN_021_TEAM_EXECUTION_ASSESSMENT
      - PATTERN_022_PROCESS_MATURITY_ASSESSMENT
      - PATTERN_023_SYSTEM_SUPPORT_ASSESSMENT
  
  # Rule 7: Analysis patterns
  - name: "Identify bottlenecks"
    trigger_types: ["system_reactive"]
    trigger_conditions: ["T_ASSESSMENT_COMPLETE"]
    system_knowledge: {assessment_completeness: "complete"}
    behaviors: ["B_IDENTIFY_BOTTLENECK", "B_GENERATE_OPTIONS"]
    priority: "medium"
    generates:
      - PATTERN_060_IDENTIFY_BOTTLENECK
      - PATTERN_061_EXPLAIN_MIN_RESULT
  
  # Rule 8: Recommendation patterns
  - name: "Generate pilot options"
    trigger_types: ["user_explicit", "system_reactive"]
    trigger_conditions: ["T_FEASIBILITY_CHECK", "T_BOTTLENECK_IDENTIFIED"]
    system_knowledge: 
      assessment_completeness: "complete"
      business_context: ["partial", "rich"]
    behaviors: ["B_RECOMMEND_PILOTS", "B_GENERATE_OPTIONS"]
    priority: "medium"
    generates:
      - PATTERN_070_GENERATE_PILOT_OPTIONS
      - PATTERN_071_CHECK_PREREQUISITES
```

**Effort:** 8-10 rules × 15 min = **2-3 hours**

---

## Step 5: Pattern Generator

**System generates patterns from composition rules**

```python
class PatternGenerator:
    def __init__(self, triggers, behaviors, knowledge_dims, rules):
        self.triggers = triggers
        self.behaviors = behaviors
        self.knowledge = knowledge_dims
        self.rules = rules
    
    def generate_patterns(self) -> List[dict]:
        """Generate all patterns from composition rules"""
        patterns = []
        
        for rule in self.rules:
            # For each trigger in rule
            for trigger_id in rule["trigger_conditions"]:
                trigger = self.triggers[trigger_id]
                
                # For each behavior in rule
                for behavior_id in rule["behaviors"]:
                    behavior = self.behaviors[behavior_id]
                    
                    # Generate pattern
                    pattern = self._compose_pattern(
                        trigger=trigger,
                        behavior=behavior,
                        knowledge=rule.get("user_knowledge", {}),
                        system_state=rule.get("system_knowledge", {}),
                        priority=rule["priority"]
                    )
                    
                    patterns.append(pattern)
        
        return patterns
    
    def _compose_pattern(self, trigger, behavior, knowledge, system_state, priority):
        """Compose atomic pieces into full pattern"""
        pattern_id = self._generate_id(trigger, behavior)
        
        return {
            "pattern_id": pattern_id,
            "name": self._generate_name(trigger, behavior),
            "category": self._infer_category(trigger, behavior),
            
            "trigger": {
                "type": trigger["type"],
                "conditions": {
                    "user_knowledge": knowledge,
                    "system_state": system_state,
                    **trigger.get("conditions", {})
                },
                "priority": priority
            },
            
            "behavior": {
                "system_goals": behavior["goal"],
                "response_template": behavior["template"],
                "response_constraints": behavior["constraints"]
            },
            
            "updates": self._infer_updates(behavior),
            "next_patterns": self._infer_next_patterns(pattern_id),
            
            # Auto-generate tests
            "tests": self._generate_tests(trigger, behavior)
        }
```

**Effort:** Write generator once = **4-6 hours**

---

## Step 6: Human Curation

**Review generated patterns, keep best ones**

```python
class PatternCurator:
    def curate(self, generated_patterns: List[dict]) -> List[dict]:
        """
        Human reviews generated patterns.
        Keeps good ones, discards nonsensical combinations.
        """
        curated = []
        
        for pattern in generated_patterns:
            # Show to human
            print(f"\n{pattern['name']}")
            print(f"Trigger: {pattern['trigger']}")
            print(f"Behavior: {pattern['behavior']}")
            
            decision = input("Keep? (y/n/edit): ")
            
            if decision == 'y':
                curated.append(pattern)
            elif decision == 'edit':
                edited = self._human_edit(pattern)
                curated.append(edited)
            # else: discard
        
        return curated
```

**Effort:** Review 500 generated patterns at ~30 sec each = **4-5 hours**

---

## The Exponential Benefit

### Combinatorial Explosion (Good Kind)

```
10 triggers × 10 behaviors = 100 base combinations

With knowledge dimensions:
100 × 3 user states × 3 system states = 900 potential patterns

With composition rules (filtering):
900 → 200 sensible patterns

Human curation:
200 → 100 high-quality patterns
```

### Consistency Benefits

**All patterns share:**
- Same trigger vocabulary
- Same behavior templates
- Same knowledge dimensions
- Same test structure

**Result:** Perfect consistency across 100 patterns

### Maintenance Benefits

**Update 1 atomic trigger:**
- Affects all patterns using that trigger
- Regenerate patterns
- Re-run tests
- **Propagates fix to 10-20 patterns instantly**

**Update 1 atomic behavior:**
- Affects all patterns using that behavior
- **Propagates improvement to 10-20 patterns instantly**

---

## High-Leverage Human Input Points

### 1. Identify Missing Triggers (Ongoing)

**As you simulate conversations:**
```
"Hmm, user asked X but no pattern triggered"
→ Add new atomic trigger T_X
→ Regenerate patterns
→ Now 10 new patterns cover this case
```

**Effort:** 10 min per new trigger  
**Benefit:** 5-10 new patterns automatically

### 2. Refine Behavior Templates (Ongoing)

**As you test patterns:**
```
"This response feels too verbose"
→ Update B_SHOW_STATUS template
→ Regenerate patterns
→ All 15 status patterns now improved
```

**Effort:** 15 min per behavior refinement  
**Benefit:** 10-20 patterns improved instantly

### 3. Add Composition Rules (Strategic)

**As you identify new pattern families:**
```
"We need patterns for handling dependencies"
→ Add rule: dependency_exploration
→ Combines T_DEPENDENCY_MENTION + B_ASK_CLARIFYING_QUESTION
→ Generates 5 new patterns
```

**Effort:** 20 min per new rule  
**Benefit:** 5-15 new patterns

### 4. Create Example Conversations (Validation)

**Write 5-10 canonical conversations:**
```yaml
# conversation_examples/first_time_user.yaml
turns:
  - user: null
    expected_pattern: PATTERN_001_WELCOME_FIRST_TIME
    expected_response_type: "welcome + question"
  
  - user: "Sales forecasts are always wrong"
    expected_pattern: PATTERN_010_OUTPUT_DISCOVERY
    expected_response_type: "output confirmation"
  
  # ... 8 more turns
```

**Effort:** 30 min per conversation × 10 = **5 hours**  
**Benefit:** 
- Validates 50-100 patterns
- Identifies gaps in pattern coverage
- Creates integration tests

---

## Recommended Workflow

### Week 1: Foundation (10-12 hours)
1. **Define atomic triggers** (3 hours)
   - Start with 10 most common triggers
   - Add more as you discover gaps

2. **Define atomic behaviors** (3 hours)
   - Start with 10 most common response types
   - Add more as you discover gaps

3. **Define knowledge dimensions** (1 hour)
   - 5-7 key dimensions
   - 2-4 states per dimension

4. **Define composition rules** (3 hours)
   - 8-10 rules covering main pattern families
   - Focus on high-value combinations

5. **Build pattern generator** (4-6 hours)
   - Write code to compose patterns
   - Auto-generate tests

### Week 2: Generation & Curation (8-10 hours)
1. **Generate patterns** (1 hour)
   - Run generator
   - Get 200-500 candidate patterns

2. **Curate patterns** (5 hours)
   - Review all generated patterns
   - Keep ~100 best ones
   - Discard nonsensical combinations

3. **Write example conversations** (5 hours)
   - 10 canonical user journeys
   - Cover main use cases
   - Validate pattern coverage

### Week 3: Refinement (5-8 hours)
1. **Test patterns** (3 hours)
   - Run generated tests
   - Fix failures

2. **Identify gaps** (2 hours)
   - Which conversations aren't covered?
   - Add missing triggers/behaviors

3. **Regenerate & re-curate** (3 hours)
   - Regenerate with new atoms
   - Review new patterns

**Total: 25-30 hours for 100 high-quality patterns**

vs **50+ hours writing patterns manually**

---

## Additional Leverage: LLM-Assisted Curation

**Use LLM to pre-filter generated patterns:**

```python
def llm_pre_filter(pattern: dict) -> dict:
    """
    Ask LLM: Does this pattern make sense?
    Reduces human review burden.
    """
    prompt = f"""
    Pattern: {pattern['name']}
    Trigger: {pattern['trigger']}
    Behavior: {pattern['behavior']}
    
    Questions:
    1. Does this combination make sense? (yes/no)
    2. Is this a useful conversation pattern? (yes/no)
    3. Suggested improvements (if any)
    
    Score: 1-5 (5 = definitely keep, 1 = definitely discard)
    """
    
    result = llm.generate(prompt)
    pattern['llm_score'] = result['score']
    pattern['llm_feedback'] = result['feedback']
    
    return pattern

# Human only reviews patterns with score >= 3
# Reduces review time by 50-70%
```

**Effort:** 2 hours to set up  
**Benefit:** Reduces curation time from 5 hours → 2 hours

---

## Summary: The Leverage Points

### High-Leverage Activities (Do These)
1. ✅ **Define atomic triggers** (3 hours → enables 100+ patterns)
2. ✅ **Define atomic behaviors** (3 hours → enables 100+ patterns)
3. ✅ **Define composition rules** (3 hours → generates 200+ patterns)
4. ✅ **Write example conversations** (5 hours → validates all patterns)
5. ✅ **Build pattern generator** (5 hours → automates everything)

**Total: 19 hours of high-leverage work**

### Low-Leverage Activities (Avoid These)
1. ❌ Writing individual patterns manually (50+ hours)
2. ❌ Writing individual tests manually (20+ hours)
3. ❌ Manually ensuring consistency (10+ hours)

### The Math
```
Traditional: 80+ hours
Compositional: 25-30 hours (19 high-leverage + 6-11 curation)

Efficiency gain: 2.5-3x
Consistency: Perfect (generated from same atoms)
Maintainability: Excellent (update atoms, regenerate)
Coverage: Better (combinatorial explosion finds edge cases)
```

---

## Next Steps

1. **Start with triggers** - identify 10 atomic triggers
2. **Define behaviors** - identify 10 atomic behaviors  
3. **Write 1-2 composition rules** - prove the concept
4. **Generate 10-20 patterns** - validate approach
5. **Iterate** - add more atoms and rules as needed

**The key insight:** Invest time in defining the atoms and composition rules, not in writing individual patterns. The system does the combinatorial work for you.
