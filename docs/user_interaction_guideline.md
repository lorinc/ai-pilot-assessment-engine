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
