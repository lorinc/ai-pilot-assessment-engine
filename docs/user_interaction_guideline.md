# User Interaction Guidelines

**Principle:** LLM generates, user validates. Simple language. Minimal questions. Context accumulates. Support, not capture.

---

## 1. Option Generation Context (for LLM)

The system generates options at runtime based on accumulated context—never asks users to enumerate solutions.

```json
{
  "problem_summary": "user's vague problem statement",
  "organizational_context": {
    "budget_range": "extracted from past conversations",
    "time_constraints": "extracted from past conversations",
    "capabilities": ["what they've done before"],
    "risk_tolerance": "inferred from past decisions"
  },
  "option_templates": [
    {"type": "do_nothing", "always_include": true},
    {"type": "delay", "conditions": ["if uncertainty high"]},
    {"type": "buy", "when": ["capability exists in market"]},
    {"type": "build", "when": ["unique requirements"]},
    {"type": "pilot", "when": ["high uncertainty"]}
  ],
  "prompt": "Generate 3-5 options. Include 'Do Nothing'. Use simple language. Show trade-offs."
}
```

**Interaction Pattern:**
- User describes problem vaguely
- System generates 3-5 options automatically
- User picks, adjusts, or asks for more

---

## 2. Evidence Extraction Prompt

Turn vague user statements into structured evidence without interrogation.

```yaml
user_input: "I think sales forecasts are always wrong"
llm_task: |
  Extract:
  - What signal did they observe? (forecasts miss by X%)
  - How do they know? (gut feel vs data)
  - How recent? (this quarter vs always)
  
  Then ask ONE clarifying question, max.
  
conversation_flow:
  - "What made you notice this?" 
  - Store answer as evidence
  - Rate quality internally (don't show user)
```

**Interaction Pattern:**
- User makes vague claim
- System extracts what it can
- Asks ONE follow-up if critical info missing
- Rates evidence quality internally (never shown)

---

## 3. Simple Confidence Language

No p90, no decimals, no statistics jargon. Elementary school terminology only.

```json
{
  "user_facing_scale": {
    "impossible": 0.0,
    "unlikely": 0.25,
    "50/50": 0.5,
    "likely": 0.75,
    "fairly_sure": 0.9,
    "certain": 1.0
  },
  "conversation_pattern": "How sure are you? (unlikely / 50/50 / likely / fairly sure)",
  "internal_mapping": "Convert to 0-1 for calculations, never show decimals to user"
}
```

**Interaction Pattern:**
- System asks: "How sure are you?"
- User picks: unlikely | 50/50 | likely | fairly sure
- System converts to numbers internally
- User never sees 0.75 or "p90"

---

## 4. Assumption Management UX

Extract assumptions from conversation, let user mark concerns, track automatically.

```json
{
  "llm_extracts_assumptions": [
    "Sales team will use the new tool",
    "Data quality is good enough",
    "Budget won't be cut mid-project"
  ],
  "show_to_user": "I'm assuming: [list]. Which ones worry you?",
  "user_marks": ["worry", "ok", "critical"],
  "system_tracks": {
    "assumption_id": "auto-generated",
    "user_concern_level": "worry | ok | critical",
    "needs_testing": "auto-set if 'worry' or 'critical'"
  }
}
```

**Interaction Pattern:**
- System extracts assumptions from conversation
- Shows list: "I'm assuming X, Y, Z. Which ones worry you?"
- User marks: ok | worry | critical
- System auto-flags worried/critical ones for testing
- No forms, no IDs visible to user

---

## 5. Impact Model - LLM Generation

Most leaders don't think in scenarios, but can validate them when shown.

```yaml
input_from_user: "This could save us maybe 50k, probably more like 30k"
llm_generates:
  pessimistic: 10000
  likely: 30000
  optimistic: 50000
shows_to_user: |
  "If things go badly: €10k
   Most likely: €30k  
   If things go well: €50k
   
   Sound about right?"
user_adjusts: simple sliders or text
```

**Interaction Pattern:**
- User gives vague estimate
- System generates three scenarios
- Shows in plain language
- User adjusts with sliders or "actually, more like..."
- System recalculates silently

---

## 6. Organizational Context - Conversation Capture

Never ask users to "fill out their organizational context." Extract it over time from natural conversation.

```yaml
# Not a form to fill, but extracted over time from conversations

conversation_snippets:
  - user: "We can't spend more than 50k on pilots"
    extract: {type: "constraint", category: "budget", value: 50000}
  
  - user: "Last time we tried AI, leadership killed it after 2 months"
    extract: {type: "norm", category: "cultural", pattern: "short_patience"}
  
  - user: "We need board approval for anything customer-facing"
    extract: {type: "policy", category: "regulatory", scope: "customer_facing"}

storage_format: |
  {
    "context_id": "CTX-001",
    "type": "constraint",
    "category": "budget",
    "statement": "All AI pilots require <€50k budget",
    "scope": "enterprise",
    "reusable": true,
    "applies_to": ["all_ai_decisions"],
    "last_updated": "2024-10-15"
  }

reuse: "Next decision auto-includes these constraints without asking again"
```

**Interaction Pattern:**
- User mentions constraint casually in conversation
- System extracts and stores silently
- Next decision: system applies constraint automatically
- User never asked twice
- User can review/edit accumulated context anytime

---

## 7. Decision Support Output (not capture)

This is a decision support system, not a decision tracking system. Help decide, don't track execution.

```json
{
  "system_produces": {
    "recommendation": "Try Option 2 (pilot) for 8 weeks",
    "reasoning": "Highest value/effort ratio, reversible, tests key assumptions",
    "red_flags": ["Assumption X is critical but uncertain"],
    "next_steps": ["Test assumption X in week 1", "Set up metrics Y"]
  },
  "exportable_as": {
    "format": "detailed_prompt",
    "content": "Full context dump for user's favorite AI",
    "includes": ["all org context", "evidence", "assumptions", "reasoning"]
  },
  "user_action": "Take recommendation elsewhere, not captured in system"
}
```

**Interaction Pattern:**
- System provides recommendation with reasoning
- User can export everything as detailed AI prompt
- User takes recommendation and acts outside system
- System does NOT track: "Did you do it? How did it go?"
- System DOES offer: "Want to revisit this decision later?"

---

## 8. Orientative Conversation Patterns

Users need to understand: "What are we doing? Where are we? What can I do next?"

### Pattern 1: Status Query - "Where Are We?"

**Trigger:** User asks explicitly OR system offers when discussion reaches natural conclusion

**Response Structure:**
```yaml
assessment_status:
  per_category:
    - category: "Data Readiness"
      completeness: "60% mapped"
      confidence: "70% confident"
      what_this_enables: "You can evaluate basic forecasting projects"
      
    - category: "AI Capability"  
      completeness: "40% mapped"
      confidence: "50% confident"
      what_this_enables: "You can assess simple automation, not complex ML yet"

  overall_capability:
    can_do_now: "You can now evaluate basic forecasting of annual sales results, but not monthly predictions that consider seasonal trends"
    
  next_logical_step:
    to_improve: "To evaluate more complex projects, we need to know more about [ML infrastructure, data governance, team skills]"
    or_proceed: "Or we can start evaluating that sales forecasting project you mentioned"
```

**Example:**
```
User: "Where are we with all this?"

System: "Here's what we've mapped out:

**Data Readiness: 60% mapped, 70% confident**
With this, you can evaluate basic forecasting projects that use historical sales data.

**AI Capability: 40% mapped, 50% confident**  
You can assess simple automation, but not complex ML projects yet.

**What you can do now:**
You can evaluate basic forecasting of your annual sales results, but not monthly predictions that consider seasonal trends.

**Next steps:**
- Continue mapping data readiness → Would unlock quarterly forecasting
- Start evaluating that sales forecasting project you mentioned
- Explore AI capability → Would unlock 3 more project types

What sounds most useful?"
```

### Pattern 2: Next Tier Query - "What's Missing?"

**Trigger:** User asks "what do we need?" OR system suggests when approaching tier boundary

**Response Structure:**
```yaml
current_tier:
  factor_completeness: "15/50 factors assessed"
  confidence_level: "60% average confidence"
  decision_capability: "Can make low-risk pilot decisions (<€25k)"

next_tier:
  requires:
    factor_completeness: "25/50 factors"
    confidence_level: "75% average"
    specific_gaps: ["data_governance", "ml_infrastructure", "team_skills"]
  
  unlocks:
    decision_capability: "Can make medium-risk decisions (€25k-€100k)"
    project_types: ["Complex forecasting", "Basic ML automation"]
  
  options:
    - "Tell me about your data governance (5 min)"
    - "Describe your ML infrastructure (5 min)"
    - "Or start evaluating projects with current knowledge"
```

**Example:**
```
User: "What do we need to evaluate bigger projects?"

System: "Right now you're at 60% confidence across data factors. With this, you can make low-risk pilot decisions under €25k.

**To reach the next tier** (medium-risk decisions €25k-€100k):
- Need 75% confidence in data factors
- Missing: data governance, ML infrastructure, team skills

**This would unlock:**
- Complex forecasting (seasonal trends, multiple variables)
- Basic ML automation projects

**Your options:**
1. Tell me about your data governance (5 min) → Biggest confidence boost
2. Describe your ML infrastructure (5 min) → Unlocks 2 project types
3. Start evaluating projects now with current knowledge

What makes sense?"
```

### Pattern 3: Conversation Continuity - "Where Were We?"

**Trigger:** User returns after break OR explicitly asks

**Default (no scope provided):** Show last meaningful factor update + quick status

**With scope:** Show last conversation about that topic

**Response Structure:**
```yaml
last_conversation:
  topic: "data_quality"
  excerpt: "You mentioned data is scattered across 5 systems, no catalog yet"
  impact: "This moved data_quality from unknown to 20% (confidence: 75%)"
  
benefit_of_continuing:
  factor_dependencies: "Finishing data quality assessment unlocks data governance and ML infrastructure assessments"
  confidence_gain: "Would raise confidence from 75% to 85%"
  
other_options:
  - "Explore AI capability instead"
  - "Start evaluating a forecasting project"
  
current_capability:
  can_evaluate: "Basic forecasting with annual data"
  next_unlock: "Quarterly forecasting (need data governance)"
```

**Example:**
```
User: "Where were we?"

System: "Last time we discussed **data quality**. You mentioned data is scattered across 5 systems with no catalog yet. This moved data_quality from unknown to 20% (75% confident).

**If we continue:**
Finishing this would unlock assessments of data governance and ML infrastructure—basically, we'd understand your full data landscape.

**Or you could:**
- Explore AI capability instead (team skills, infrastructure)
- Start evaluating that sales forecasting project

**What you can do now:**
You can evaluate basic forecasting with annual data. To unlock quarterly forecasting, we need to map data governance next.

What would be most useful?"
```

### Pattern 4: Proactive Milestone Offers

**Trigger:** Discussion reaches natural conclusion (factor assessed, topic exhausted)

**Response Structure:**
```yaml
milestone_reached:
  what_completed: "Data quality assessment complete"
  new_capability: "You can now evaluate projects requiring historical data"
  
progress_indicator:
  before: "Could assess 2 project archetypes"
  now: "Can assess 5 project archetypes"
  
next_options:
  continue_thread: "Explore data governance (related to what we just discussed)"
  new_thread: "Assess AI capability (team, infrastructure)"
  apply_knowledge: "Evaluate a specific project idea"
```

**Example:**
```
System: "Okay, we've mapped out your data quality pretty well.

**New capability unlocked:**
You can now evaluate projects that need historical sales data—things like demand forecasting, trend analysis.

**Progress:** You could assess 2 project types before, now you can assess 5.

**What next?**
- Continue with data governance (builds on what we just discussed)
- Switch to AI capability (team skills, infrastructure)  
- Evaluate that forecasting project you mentioned

What sounds good?"
```

---

## Orientative Pattern Principles

### 1. **Always Show Current Capability**
Every orientative response includes: "What you can evaluate now" with concrete examples
- ✅ "You can evaluate basic forecasting of annual sales"
- ❌ "You have 60% data readiness"

### 2. **Progress, Not Completeness**
Frame as "what you can do now" vs "what's missing"
- ✅ "You can assess 5 project types now, up from 2"
- ❌ "You've only completed 30% of factors"

### 3. **Risk-Based Tiers**
Tie completeness to decision stakes, not arbitrary percentages
- ✅ "Can make €25k pilot decisions, need more for €100k projects"
- ❌ "Need 80% completeness to proceed"

### 4. **Diminishing Returns Awareness**
Signal when additional assessment has low ROI
- ✅ "Assessing 3 more factors would only improve confidence by 5%"
- ❌ Never mention this, keep pushing for completeness

### 5. **Agency Through Options**
Always give 2-3 concrete next actions
- ✅ "Continue this thread | Switch topics | Evaluate a project"
- ❌ "What would you like to do?"

### 6. **Brevity**
Keep orientative responses under 150 words
- Show structure, not walls of text
- Use bullets and clear sections
- One example per capability

---

## Core Interaction Principles

### 1. LLM Generates, User Validates
- System makes smart guesses from vague input
- Shows assumptions clearly
- User corrects, doesn't create from scratch

### 2. Simple Language Only
- No: p90, confidence intervals, statistical terms
- Yes: unlikely, 50/50, likely, fairly sure
- No: 0.75 probability
- Yes: "fairly sure"

### 3. Minimal Questions
- Extract from conversation, don't interrogate
- ONE follow-up question max per topic
- If user won't tolerate more questions, make assumptions and show them

### 4. Context Accumulates
- Never ask the same thing twice
- Extract constraints/norms from casual mentions
- Reuse everything automatically in future decisions
- "No effort is ever lost"

### 5. Support, Not Capture
- Help make decision
- Don't track execution
- Don't ask "how did it go?"
- DO allow export for portability

---

## Anti-Patterns to Avoid

❌ **Don't:** Ask user to enumerate all possible solutions  
✅ **Do:** Generate options, let user pick/adjust

❌ **Don't:** Ask "What's the p90 confidence interval?"  
✅ **Do:** Ask "How sure are you? (unlikely/likely/fairly sure)"

❌ **Don't:** Make user fill out forms with 20 fields  
✅ **Do:** Extract from conversation, show for validation

❌ **Don't:** Ask same question in next decision  
✅ **Do:** Remember and reuse automatically

❌ **Don't:** Track execution and outcomes  
✅ **Do:** Support decision, enable export, let user own execution

❌ **Don't:** Lock user into the system  
✅ **Do:** Export everything as portable AI prompts

---

## Conversation Flow Example

**User:** "Our sales forecasts are always wrong and it's costing us."

**System:** *(extracts: problem = forecast accuracy, impact = cost)*  
"What made you notice this? Is it getting worse?"

**User:** "Yeah, we missed Q3 by 20%. Sales ops is frustrated."

**System:** *(stores: evidence = Q3 miss 20%, stakeholder = sales ops)*  
"Got it. Let me think about options...  
1. Do nothing (accept current accuracy)  
2. Improve existing process (train reps, better templates)  
3. Pilot ML forecasting tool (8-week test)  

I'm assuming you have <€50k budget and need results this quarter. Sound right?"

**User:** "Budget's fine, but we need something faster than a quarter."

**System:** *(updates: time constraint = <1 quarter)*  
"Okay, that rules out Option 3. Between doing nothing and improving the process, improving seems better—likely saves €30k, fairly quick. Want to explore that?"

**User:** "Yeah, what would that look like?"

**System:** *(generates plan, shows assumptions)*  
"Here's what I'm thinking... [plan]. I'm assuming sales ops will cooperate and data quality is decent. Which worries you more?"

**User:** "Data quality is sketchy."

**System:** *(marks assumption as 'worry', flags for testing)*  
"Got it. Let's test data quality first—here's how... [next steps]"

---

**End of interaction. User has a plan. System has learned constraints. Next decision will be faster.**
