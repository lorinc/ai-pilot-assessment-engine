# Alternative B: Business Context Extraction Strategy

**Status:** Design Decision  
**Date:** 2025-11-04

---

## Core Principle: Sprinkle, Don't Survey

**Approach:** Extract business decision factors naturally throughout conversation, not upfront questionnaire.

**Rationale:** Users don't know why they're answering business questions before seeing value. Context emerges naturally during problem discussion. Only ask explicitly for missing critical factors before recommendations.

---

## Business Decision Factors

**Source:** `docs/obsolete/interim_data_files/business_decision_dimension_taxonomy.json`

**Categories:**
- Timeline urgency (quick win vs long-term)
- Budget constraints (cost-sensitive vs flexible)
- Visibility preference (quiet win vs showcase)
- Competitive pressure (parity vs leapfrog)
- Strategic alignment (on-OKR vs off-OKR)
- Risk tolerance (proven vs experimental)
- Compliance requirements (regulated vs flexible)
- Vendor constraints (locked-in vs flexible)
- Stakeholder pressure (board-level vs team-level)
- Resource constraints (understaffed vs adequate)

**Critical factors (always need):** Budget, timeline, visibility  
**Contextual factors (only if relevant):** Compliance, vendor constraints, strategic alignment

---

## Natural Extraction Moments

### Moment 1: After Output Identified
**Context:** User just confirmed output (e.g., "Yes, Sales Forecast")

**Natural questions:**
- "How urgent is fixing this?"
- "What's driving the need to improve this now?"
- "Is this a top priority or one of many?"

**Extracts:**
- `timeline_urgency`: high/medium/low
- `competitive_pressure`: high/medium/low
- `strategic_alignment`: on-OKR/off-OKR

**Example:**
```
System: "Sales Forecast - got it. How urgent is fixing this?"
User: "Very urgent. Board is asking about forecast accuracy every week."
→ timeline_urgency: high, stakeholder_pressure: board-level
```

---

### Moment 2: When User Describes Pain Intensity
**Context:** User quantifies problem (e.g., "20-30% error rate")

**Natural questions:**
- "What's the business impact of these errors?"
- "How much is this costing you?"
- "What happens if this doesn't improve?"

**Extracts:**
- `business_impact`: high/medium/low
- `cost_of_problem`: quantified or qualitative
- Sets context for budget expectations

**Example:**
```
System: "20-30% error rate - what's the business impact?"
User: "We're missing revenue targets. Cost us €500k last quarter."
→ business_impact: high, cost_of_problem: €500k/quarter
```

---

### Moment 3: When User Mentions Stakeholders
**Context:** User mentions VP, board, team leads, etc.

**Natural questions:**
- "Is this a visible initiative or more of a quiet improvement?"
- "Who's sponsoring this effort?"
- "Any expectations on showcasing results?"

**Extracts:**
- `visibility_preference`: showcase/internal/quiet
- `stakeholder_pressure`: board/exec/team
- `political_sensitivity`: high/medium/low

**Example:**
```
System: "You mentioned the VP is involved. Is this a visible initiative?"
User: "Yes, they want to showcase AI wins to the board."
→ visibility_preference: showcase, stakeholder_pressure: exec
```

---

### Moment 4: When User Reveals Constraints Naturally
**Context:** User says "no budget", "understaffed", "locked into vendor"

**Natural follow-ups:**
- "What budget range are we working with?"
- "Any other constraints I should know?"
- "How flexible are you on [mentioned constraint]?"

**Extracts:**
- `cost_sensitivity`: high/medium/low
- `resource_constraints`: understaffed/adequate/flexible
- `vendor_dependency`: locked-in/flexible

**Example:**
```
User: "We're understaffed and have no budget for new tools."
System: "Got it. What budget range could you work with for a pilot?"
User: "Maybe €20k-€30k max."
→ cost_sensitivity: high, budget_range: €20k-€30k
```

---

### Moment 5: When Discussing System/Tool Bottlenecks
**Context:** User mentions CRM, ERP, vendor lock-in

**Natural questions:**
- "Any procurement or vendor constraints?"
- "How flexible are you on tooling changes?"
- "Can you integrate with existing systems?"

**Extracts:**
- `vendor_dependency`: locked-in/flexible
- `procurement_friction`: high/medium/low
- `integration_requirements`: strict/flexible

**Example:**
```
User: "We're locked into Salesforce, can't switch."
System: "Understood. Can you add integrations or plugins?"
User: "Yes, but procurement takes 3-6 months."
→ vendor_dependency: locked-in, procurement_friction: high
```

---

### Moment 6: When User Mentions Compliance/Security
**Context:** User says "regulated", "sensitive data", "audit requirements"

**Natural questions:**
- "Any compliance or security requirements for solutions?"
- "What data can/can't be used for AI?"
- "Any regulatory constraints?"

**Extracts:**
- `compliance_pressure`: high/medium/low
- `security_posture`: strict/moderate/flexible
- `data_sovereignty`: strict/flexible
- `privacy_mode`: strict/moderate/flexible

**Example:**
```
User: "We handle financial data, heavily regulated."
System: "Any compliance requirements for AI solutions?"
User: "Must be GDPR compliant, data stays in EU."
→ compliance_pressure: high, data_sovereignty: EU-only
```

---

### Moment 7: Pre-Recommendation Checkpoint
**Context:** After bottlenecks identified, before generating recommendations

**Explicit questions for missing critical factors:**
- "What's your budget range for this?" (if not mentioned)
- "How quickly do you need results?" (if not mentioned)
- "Prefer a quiet win or showcase project?" (if not mentioned)

**Always ask these 3 if not already extracted.**

**Example:**
```
System: "I've identified the bottlenecks. Before I recommend options, a few quick questions:
- What's your budget range for a pilot?
- How quickly do you need results?
- Is this a visible initiative or quiet improvement?"

User: "€30k-€50k budget, need results in 3 months, prefer quiet win first."
→ budget_range: €30k-€50k, timeline_urgency: high, visibility_preference: quiet
```

---

### Moment 8: When User Asks About Solutions
**Context:** User says "What can we do?" or "What are our options?"

**Natural questions:**
- "Quick win or comprehensive fix?"
- "Prefer low-cost experiments or proven solutions?"
- "Willing to try new approaches or stick to proven?"

**Extracts:**
- `risk_tolerance`: experimental/moderate/conservative
- `optionality_preference`: keep-options-open/commit-early
- `solution_scope`: quick-win/comprehensive

**Example:**
```
User: "What are our options?"
System: "Would you prefer a quick win to show progress, or a comprehensive solution?"
User: "Quick win first, then we can get budget for more."
→ solution_scope: quick-win, optionality_preference: keep-options-open
```

---

## Extraction Strategy Summary

### Primary: Contextual Inference (Moments 1-6)
**Approach:** Listen for natural mentions, extract factors as they emerge

**Advantages:**
- Zero friction
- Feels natural
- User volunteers information
- Context-aware

**Disadvantages:**
- May miss factors
- Requires good NLP/LLM
- Non-deterministic

---

### Fallback: Explicit Questions (Moment 7)
**Approach:** Ask 2-3 critical missing factors before recommendations

**Always ask if not mentioned:**
1. Budget range
2. Timeline urgency
3. Visibility preference

**Only ask if relevant to bottleneck:**
- Compliance (if data/system bottleneck)
- Vendor constraints (if tool bottleneck)
- Resource constraints (if team bottleneck)

**Advantages:**
- Ensures critical factors captured
- Minimal friction (2-3 questions)
- Contextual (only ask what matters)

**Disadvantages:**
- Slight delay before recommendations
- Feels like questionnaire if too many

---

## Implementation Requirements

### 1. Context Tracker
**Module:** `core/context_tracker.py`

**Responsibilities:**
- Track extracted business factors throughout conversation
- Mark confidence level per factor (inferred vs stated)
- Identify missing critical factors
- Format for LLM prompt

**Data structure:**
```python
{
  "timeline_urgency": {"value": "high", "confidence": 0.8, "source": "inferred from 'board asking weekly'"},
  "budget_range": {"value": "€30k-€50k", "confidence": 1.0, "source": "user stated"},
  "visibility_preference": None,  # Missing, will ask at Moment 7
  "compliance_pressure": {"value": "high", "confidence": 0.6, "source": "inferred from 'financial data'"}
}
```

---

### 2. Natural Language Extractor
**Module:** `engines/context_extractor.py`

**Responsibilities:**
- Analyze user messages for business context signals
- Extract factors using LLM
- Update context tracker
- Flag when to ask explicit questions

**LLM prompt:**
```
Analyze this user message for business decision factors:

Message: "{user_message}"

Extract any mentioned:
- Timeline urgency (urgent/moderate/flexible)
- Budget constraints (tight/moderate/flexible)
- Visibility preference (showcase/internal/quiet)
- Competitive pressure (high/medium/low)
- Compliance requirements (strict/moderate/flexible)
- Vendor constraints (locked-in/flexible)
- Stakeholder pressure (board/exec/team/none)
- Resource constraints (understaffed/adequate)

Output JSON with confidence scores.
```

---

### 3. Question Generator
**Module:** `engines/question_generator.py`

**Responsibilities:**
- Identify missing critical factors at Moment 7
- Generate natural follow-up questions for Moments 1-6
- Prioritize questions by relevance to bottleneck

**Logic:**
```python
def generate_pre_recommendation_questions(context_tracker, bottlenecks):
    missing = []
    
    # Always ask if missing
    if not context_tracker.has("budget_range"):
        missing.append("What's your budget range for this pilot?")
    if not context_tracker.has("timeline_urgency"):
        missing.append("How quickly do you need results?")
    if not context_tracker.has("visibility_preference"):
        missing.append("Is this a visible initiative or quiet improvement?")
    
    # Ask if relevant to bottleneck
    if "Tool" in bottlenecks and not context_tracker.has("vendor_dependency"):
        missing.append("Any vendor or procurement constraints?")
    if "Dependency" in bottlenecks and not context_tracker.has("compliance_pressure"):
        missing.append("Any compliance requirements for data/AI solutions?")
    
    return missing[:3]  # Max 3 questions
```

---

## Quality Assurance

### 1. Validation Rules
**Ensure extracted values are valid:**
- Budget ranges are numeric or qualitative (tight/moderate/flexible)
- Timeline urgency is high/medium/low
- Visibility preference is showcase/internal/quiet
- All confidence scores are 0.0-1.0

### 2. Contradiction Detection
**If user contradicts earlier statement:**
- Flag contradiction
- Ask for clarification
- Update with latest value

**Example:**
```
Earlier: "We have no budget" → cost_sensitivity: high
Later: "We can spend €50k" → budget_range: €50k

System: "Earlier you mentioned no budget, but now €50k. Which is accurate?"
```

### 3. Missing Critical Factors
**Before recommendations, verify:**
- Budget range (stated or inferred)
- Timeline urgency (stated or inferred)
- Visibility preference (stated or inferred)

**If missing, trigger Moment 7 questions.**

---

## Success Metrics

### Extraction Quality
- **Coverage:** % of critical factors extracted before Moment 7
- **Accuracy:** % of extracted factors validated by user
- **Inference precision:** % of inferred factors that are correct

### User Experience
- **Question count:** Avg # of explicit questions asked (target: < 3)
- **Friction:** User feedback on "too many questions" vs "just right"
- **Natural flow:** % of conversations where factors emerge naturally

### Recommendation Impact
- **Relevance:** % of recommendations that match user constraints
- **Selection rate:** % of recommended pilots that user selects
- **Constraint fit:** % of recommendations within budget/timeline

---

## Conclusion

**Business context extraction is sprinkled throughout conversation, not surveyed upfront.**

**Key principles:**
1. Listen first, ask second
2. Extract naturally when user volunteers information
3. Only ask explicitly for missing critical factors
4. Keep questions contextual and minimal (< 3)
5. Validate extracted context before recommendations

**This approach minimizes friction while ensuring recommendations are tailored to user's constraints.**
