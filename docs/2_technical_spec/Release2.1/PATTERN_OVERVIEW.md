# Pattern Overview - High-Level Summary

**Purpose**: Quick review of conversation patterns without overwhelming detail.  
**For detailed review**: See individual dense format files.

---

## Core Pattern Categories

### 1. Discovery Patterns (18 triggers, 18 behaviors)

**What**: Moving from vague to concrete, identifying outputs/teams/systems/processes

**Key Patterns**:
- **Abstract → Concrete**: User says vague things → Force specific examples
- **Progressive Narrowing**: "Sales is broken" → "Sales forecasts? Reports? Dashboards?"
- **Context Enrichment**: System/team/process identified → Ask "tell me more about {entity}"
- **Scope Clarification**: "Data quality is bad" → "All systems or just Salesforce?"

**Example Flow**:
```
User: "Sales forecasts are always wrong"
System: "Tell me about the last time this happened" (concrete example)
User: "Last quarter was off by 30%"
System: "So you mean Sales Forecast?" (confirm output)
User: "Yes"
System: "Which team creates this?" (discover context)
```

**Triggers**: Mentions output/problem/team/system, abstract statements, scope ambiguity  
**Behaviors**: Redirect to concrete, progressive narrowing, elicit example, discover team/system/process, enrich context, clarify scope

---

### 2. Assessment Patterns (16 triggers, 18 behaviors)

**What**: Gathering evidence, rating factors, capturing quality levels

**Key Patterns**:
- **Evidence Tiers**: Recognize quality (specific data > vague opinion)
- **Probe for Better**: Vague statement → "Can you quantify that?"
- **Accept with Emotional Safety**: User can't be specific → "That's okay, I can work with that. If we need more precision later, we can refine it."
- **Acknowledge Quality**: User gives numbers → "Thanks for the numbers, that helps"

**Example Flow**:
```
User: "The team is pretty good I guess"
System: "Can you give me a specific instance?" (probe for better evidence)
User: "They delivered Q3 forecast with 95% accuracy"
System: "That's specific data—high confidence. I'm hearing ⭐⭐⭐⭐" (acknowledge + assess)
```

**Triggers**: Provides rating/evidence/example, expresses uncertainty  
**Behaviors**: Assess with reflection, probe for numbers/examples/frequency/impact, acknowledge tiers, accept vague with low confidence

---

### 3. Error Recovery Patterns (13 triggers, 12 behaviors)

**What**: Handling frustration, confusion, mistakes

**Key Patterns**:
- **Frustration → Acknowledge**: Detect frustration → "Tell me what went wrong"
- **Confusion → Rephrase**: User confused → "I haven't given enough context. Let me try a different approach."
- **Stuck → Offer Skip**: User stuck → "You're right, it's not that important right now. We can come back later if we need to."
- **Mistakes → Offer Undo**: User regrets action → "Should I reverse that change?"

**Example Flow**:
```
User: "This doesn't make sense"
System: "I haven't given enough context. Let me try a different approach." (offer rephrase)
User: "Still confused"
System: "You're right, it's not that important right now. We can come back later if we need to." (offer skip)
```

**Triggers**: Expresses frustration/confusion/uncertainty, rapid corrections, user stuck  
**Behaviors**: Detect frustration, acknowledge beta, offer ticket/undo/rephrase/skip, backtrack, accept "I don't know", lower confidence

---

### 4. Navigation Patterns (12 triggers, 15 behaviors)

**What**: Showing progress, orienting user, offering choices

**Key Patterns**:
- **Per-Output Completeness**: "For Sales Forecast: enough data for medium confidence recommendations"
- **Depth vs Breadth Guidance**: Multiple outputs, shallow assessment → "Focus deeply on 1-2 outputs?"
- **Offer Recommendations**: Sufficient data → "I can generate {confidence} recommendations now. Continue or see options?"
- **Show What We Know**: "Known: Output, Team, System. Unknown: Process, Dependencies"

**Example Flow**:
```
User: "Where are we?"
System: "Sales Forecast: 3/4 components (75%). Sales Dashboard: 1/4 (25%)" (show progress)
User: (continues mentioning more outputs)
System: "I notice you've mentioned 5 outputs but shallow knowledge. Focus deeply on one?" (depth guidance)
```

**Triggers**: Request progress, multiple outputs active, sparse knowledge detected, breadth over depth  
**Behaviors**: Show output completeness, progress bar, offer recommendations at confidence, recommend depth over breadth, show assessment gaps, offer focus strategy

---

### 5. Recommendation Patterns (4 triggers, 13 behaviors)

**What**: Generating pilot options, explaining feasibility, prioritizing

**Key Patterns**:
- **Bottleneck → Pilots**: Bottleneck identified → "Based on {bottleneck}, here are 3 options"
- **Explain Feasibility**: "45% confidence - this would need ML expertise to deliver"
- **Show Prerequisites**: Low feasibility → "This pilot would benefit from strengthening {component} first"
- **Request Feedback**: After recommendations → "Am I on the right track?"

**Example Flow**:
```
System: "Bottleneck: Team Execution (⭐⭐). Here are 3 pilot options..." (generate)
System: "Option 1: Team Augmentation. Feasibility: 45% - this would need ML expertise" (explain)
User: "That's too hard"
System: "This pilot would benefit from strengthening ML capability first" (show prerequisites)
System: "What do you think? Am I missing something?" (request feedback)
```

**Triggers**: Assessment sufficient, bottleneck identified, request recommendations  
**Behaviors**: Generate options, map bottleneck to archetype, show details/feasibility/prerequisites/risks/tradeoffs, prioritize, request feedback

---

### 6. Scope Management Patterns (8 triggers, 13 behaviors)

**What**: Disambiguating scope, handling multi-output scenarios

**Key Patterns**:
- **Detect Ambiguity**: "Data quality is bad" → "All systems or just Salesforce?"
- **Multi-Output → Focus**: User mentions 3 outputs → "Let's focus on one first"
- **Narrow to Specific**: Too broad → "Pick one system as an example"
- **Expand to Generic**: Specific assessed → "Does this apply to other systems too?"

**Example Flow**:
```
User: "We have problems with sales forecasts, dashboards, and reports"
System: "You mentioned 3 outputs. Let's focus on one first. Which is most critical?" (handle multi)
User: "All of them are bad"
System: "Let's pick one system as an example" (narrow to specific)
```

**Triggers**: Scope ambiguity, multiple outputs mentioned, abstract statements  
**Behaviors**: Detect scope ambiguity, clarify system/team/domain/time scope, narrow to specific, handle multi-output, offer scoped assessment

---

### 7. Evidence Quality Patterns (4 triggers, 15 behaviors)

**What**: Tracking evidence quality, probing for better data

**Key Patterns**:
- **Tier Recognition**: Specific data (Tier 1) > vague opinion (Tier 5)
- **Probe When Vague**: "Can you quantify that? Like % or count?"
- **Acknowledge Quality**: "That's specific data—high confidence"
- **Conflict Resolution**: "Earlier you said X, now Y. Which is more accurate?"

**Example Flow**:
```
User: "Quality is low"
System: "Can you quantify that?" (probe for numbers)
User: "Maybe 30% error rate"
System: "Thanks for the numbers" (acknowledge quantified)
Later...
User: "Actually it's 50%"
System: "Earlier you said 30%, now 50%. Which is more accurate?" (resolve conflict)
```

**Triggers**: Provides evidence, expresses uncertainty, conflicting evidence detected  
**Behaviors**: Acknowledge tier1/quantified/concrete, probe for numbers/examples/frequency/impact, accept vague with low confidence, detect conflicts, resolve conflicts, synthesize evidence

---

### 8. Education Patterns (8 triggers, 6 behaviors)

**What**: Teaching system concepts (only when relevant)

**Key Patterns**:
- **Withhold Until Relevant**: Don't educate unless user asks or demonstrates readiness
- **Just-in-Time**: Explain when user encounters the concept
- **Never Educate Frustrated Users**: Error recovery > education in priority
- **Adaptive**: Only explain advanced concepts if user knows basics

**Example Flow**:
```
User: "How does this work?"
System: "This system uses an output-centric model..." (explain on request)

vs.

User: "This is stupid" (frustrated)
System: (Does NOT educate, focuses on error recovery instead)
```

**Triggers**: Request explanation, first-time user, understanding demonstrated  
**Behaviors**: Explain object model, explain design decisions, explain evidence tiers, cite UX principles (existing behaviors)

---

## Cross-Cutting Patterns

### Priority Hierarchy (When Multiple Patterns Compete)

1. **Error Recovery** (highest) - Always prioritize frustrated/confused users
2. **Scope Management** - Clarify ambiguity before proceeding
3. **Assessment** - Core activity
4. **Discovery** - Foundation for assessment
5. **Recommendation** - Deliver value when ready
6. **Navigation** - Help user orient
7. **Analysis** - Background calculation
8. **Education** - Only when relevant (lowest)

**Example**: User says "I'm confused about sales forecasts"
- Triggers: Confusion (error recovery) + Mentions output (discovery)
- Selected: Error recovery (higher priority)
- Response: "I haven't given enough context. Let me try a different approach." (not "Tell me more about sales forecasts")

---

### Anti-Patterns (Never Combine These)

| Don't Do This | Why Not | Do This Instead |
|---------------|---------|-----------------|
| Educate frustrated user | Makes frustration worse | Error recovery first |
| Probe confused user | Adds to confusion | Rephrase or skip first (validate + downplay importance) |
| Recommend without concrete output | No context for recommendations | Discovery first |
| Defend design to frustrated user | Feels dismissive | Acknowledge frustration first |
| Show complexity to stuck user | Overwhelms | Simplify or skip |

---

### Repetition Avoidance

**Cooldown Periods** (don't repeat pattern within N turns):
- Education: 10 turns
- Navigation: 5 turns
- Error recovery: 3 turns
- Assessment: 1 turn (unless different component)
- Discovery: 2 turns (unless different output)

**Example**: System asks "Can you quantify that?" → User gives vague answer → System does NOT ask again for 3 turns, tries different approach instead

---

### Knowledge-Based Gating

**Patterns require knowledge conditions**:
- Advanced education → User understands basics
- High-confidence recommendations → 3+ components assessed
- Bottleneck analysis → 3+ components assessed
- Scope disambiguation → Scope is ambiguous
- Error recovery → Frustration/confusion level > threshold

**Example**: System won't explain "MIN calculation" unless user already understands "output-centric model"

---

## Situational Awareness (How Patterns Are Selected)

**8 Dimensions** (always sum to 100%):
1. Discovery (identifying outputs, context)
2. Education (teaching concepts)
3. Assessment (gathering evidence)
4. Analysis (calculating, finding bottlenecks)
5. Recommendation (generating pilots)
6. Navigation (showing progress, orienting)
7. Error Recovery (handling frustration/confusion)
8. Scope Management (disambiguating scope)

**How It Works**:
```
Start: {discovery: 50%, education: 50%}
After output identified: {discovery: 30%, assessment: 40%, education: 20%, navigation: 10%}
User gets confused: {assessment: 30%, error_recovery: 40%, navigation: 15%, education: 10%, discovery: 5%}
```

**Pattern Selection**:
- Each behavior has affinity scores for dimensions
- Calculate: score = sum(situation[dim] * behavior.affinity[dim])
- Select top-scoring behaviors that pass knowledge gates

---

## Generic Pattern Structure

**Every pattern has**:
1. **Trigger** - What causes it (user action or system detection)
2. **Behavior** - What to do (template, action)
3. **Knowledge Updates** - What to remember
4. **Situation Affinity** - Which dimensions it fits
5. **Constraints** - When NOT to use it

**Example**:
```yaml
Trigger: T_EXPRESS_CONFUSION
Behavior: B_OFFER_REPHRASE
  Template: "I haven't given enough context. Let me try a different approach."
  Affinity: {error_recovery: 0.9, education: 0.3}
  Requires: confusion_level > 0.3
  Blocks: frustration_level > 0.7 (use different approach if very frustrated)
Knowledge Update: confusion_level += 0.2
```

---

## Adjustment Process (Future)

### To Add a New Pattern:

1. **Identify the need** - "Users get stuck when X happens"
2. **Choose category** - Discovery? Error recovery? Navigation?
3. **Add to dense format** - One line in appropriate table
4. **Regenerate YAML** - Automatic from dense format
5. **Test** - Semantic evaluation

### To Modify a Pattern:

1. **Edit dense format** - Change template or trigger
2. **Regenerate YAML** - Automatic
3. **Test** - Ensure no regressions

### To Remove a Pattern:

1. **Delete from dense format** - Remove row
2. **Regenerate YAML** - Automatic
3. **Test** - Ensure coverage still complete

**Key**: Dense format is source of truth. YAML is generated. Easy to maintain.

---

## Key Questions for Review

### 1. Coverage
- [ ] Are all user needs covered? (help, skip, correct, progress, recommendations)
- [ ] Are all failure modes handled? (frustration, confusion, stuck, mistakes)
- [ ] Are all conversation phases covered? (discovery, assessment, analysis, recommendations)

### 2. Priority
- [ ] Does error recovery always win?
- [ ] Is education deprioritized appropriately?
- [ ] Are anti-patterns prevented?

### 3. User Agency
- [ ] Can user skip anything?
- [ ] Can user work non-linearly?
- [ ] Can user assess multiple outputs?
- [ ] Are choices explicit?

### 4. Quality
- [ ] Is evidence quality tracked?
- [ ] Is scope clarified before proceeding?
- [ ] Are recommendations gated by confidence?
- [ ] Is repetition avoided?

### 5. Gaps
- [ ] Any user scenarios not covered?
- [ ] Any failure modes not handled?
- [ ] Any missing guidance patterns?

---

## Current Stats

- **40 triggers** (user explicit/implicit, system proactive/reactive)
- **77 behaviors** (across 8 categories)
- **30 knowledge dimensions** (system knowledge, user knowledge, conversation state, quality metrics)
- **8 composition rules** (mapping, filtering, gating, chaining, anti-patterns, priority, repetition, adaptation)

**Expected output**: ~200-300 viable patterns after composition  
**Release 1 target**: Top 100 patterns for initial implementation

---

## Next Steps

1. **Review this overview** - Understand high-level patterns
2. **Ask questions** - About any pattern category or rule
3. **Identify gaps** - Missing scenarios or failure modes
4. **Approve or adjust** - Make changes to dense formats
5. **Generate YAML** - Automatic from approved dense formats
6. **Implement Release 2.5** - Situational awareness + pattern engine

---

**Questions to consider**:
- Do these pattern categories make sense?
- Are priority rules appropriate?
- Are anti-patterns comprehensive?
- Any missing user scenarios?
- Any patterns that feel wrong?
