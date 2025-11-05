# User Interaction Guidelines

**Last Updated:** 2025-11-01 22:10  
**Note:** Factor values use 1-5 star ratings. See `output_centric_factor_model_exploration.md` for details.

**Principle:** LLM generates, user validates. Simple language. Minimal questions. Context accumulates. Support, not capture. **"Withhold education until it is relevant."**

---

## 1. Project Ideas & Next Steps Generation

The system generates suggestions based on accumulated context—never asks users to enumerate solutions.

### When to Generate Options

**Project Ideas (3-5 options):**
- **Trigger:** User asks "What AI projects could we do?" or "Give me some ideas"
- **Format:** 3-5 project ideas based on assessed factors
- **Interaction:** User picks one to refine, or asks for more/different ideas

**Next Steps (2-5 options):**
- **Trigger:** User asks "What should we do next?" or "What's next?"
- **Format:** 3-5 concrete next actions with ROI
- **Interaction:** User picks, or explores freely

**Status Response (2-3 options):**
- **Trigger:** User asks "Where are we?" or finishes a topic
- **Format:** 2-3 brief next options
- **Interaction:** User picks or ignores

```json
{
  "project_ideas_context": {
    "assessed_factors": ["data_quality: ⭐⭐", "data_availability: ⭐⭐⭐⭐"],
    "organizational_context": {
      "budget_range": "extracted from past conversations",
      "time_constraints": "extracted from past conversations",
      "capabilities": ["what they've done before"]
    },
    "prompt": "Generate 3-5 project ideas. Use simple language. Show feasibility."
  }
}
```

**Interaction Pattern:**
- User asks for project ideas
- System generates 3-5 based on factors
- User picks one to refine: "Tell me more about #2"
- Or asks for more: "These don't fit, give me different ideas"
- System adjusts based on feedback
- Or user says "These are all way off" and the system displays the factors that resulted in these options and asks if something is missing or way off

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

No p90, no statistics jargon. Simple language for user input, percentages OK for system output.

```json
{
  "user_input_scale": {
    "impossible": 0.0,
    "unlikely": 0.25,
    "50/50": 0.5,
    "likely": 0.75,
    "fairly_sure": 0.9,
    "certain": 1.0
  },
  "system_output": "Can show percentages (70% confident) in status/summaries",
  "user_input": "Simple language only (unlikely / 50/50 / likely / fairly sure)"
}
```

**Interaction Pattern:**
- **System asks user:** "How sure are you? (unlikely / 50/50 / likely / fairly sure)"
- **User responds:** Simple language (no numbers)
- **System shows status:** Can use percentages ("70% confident")
- **Never ask user for:** Decimals, p90, confidence intervals

**Important:** User's confidence in their statement ≠ factor score
- User says "fairly sure we have great data engineers"
- But if evidence suggests no QA, no formal ETL → data_engineering score stays low
- LLM can explain: "On our scale, these factors suggest lower readiness than you might expect"

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

## 7. Project Evaluation (not decision tracking)

This is an exploration and evaluation system, not a decision tracking system. Help evaluate, don't track execution.

```json
{
  "system_produces": {
    "project_evaluation": {
      "project_name": "Sales forecasting pilot",
      "feasibility_confidence": 0.45,
      "confidence_breakdown": {
        "data_readiness": 0.60,
        "ai_capability": 0.40,
        "cultural_fit": 0.50
      },
      "gaps": ["data_governance", "ml_infrastructure"],
      "recommendation": "For €15k pilot, 45% is borderline. Consider assessing data governance first.",
      "timestamp": "2024-10-28T10:30:00Z"
    },
    "exportable_as": {
      "format": "detailed_prompt",
      "content": "Full context dump for user's favorite AI",
      "includes": ["all org context", "evidence", "factor assessments", "reasoning"]
    }
  }
}
```

**Interaction Pattern:**
- User asks: "Can we do sales forecasting?"
- System evaluates with current knowledge: "45% confidence, here's why..."
- User can: proceed anyway | assess more factors | ask for different project
- System does NOT track: "Did you do it? How did it go?"
- System DOES offer: "Want to re-evaluate this project later?"

**No decision record, just evaluation snapshots (TBD persistence)**

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

**Example (with scoped factors):**
```
User: "Where are we with all this?"

System: "Here's what we've mapped out:

**Data Readiness: 60% mapped, 70% confident**
With this, you can evaluate basic forecasting projects that use historical sales data.

**AI Capability: 40% mapped, 50% confident**  
You can assess simple automation, but not complex ML projects yet.

**Confirmed factors:**
- data_availability (Sales): 80% ✓ (you explicitly said "3 years of sales data")

**Unconfirmed inferences:**
- data_quality varies by system:
  • Salesforce CRM: 30% ⚠️ (80% confident, from "incomplete data" and "duplicates")
  • Sales overall: 45% ⚠️ (60% confident, inferred from Salesforce issues)
  • Finance: Not assessed
- data_governance (Sales): 15% (60% confident, from "no formal policies")

**What you can do now:**
You can evaluate sales forecasting, but confidence varies by which system you'd use:
- Using Salesforce: 35% confidence (low)
- Using data warehouse: 45% confidence (moderate, not assessed specifically)

**Next steps:**
- Confirm those inferences (2 min) → Boost confidence
- Assess specific systems (data warehouse, spreadsheets) → Refine feasibility
- Start evaluating that sales forecasting project you mentioned

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

System: "Last time we discussed **sales data quality**. You mentioned Salesforce data is incomplete with duplicates. This created a specific assessment for Salesforce CRM (30%, 80% confident) and a generic sales assessment (45%, 60% confident).

**If we continue:**
We could assess other sales systems (data warehouse, spreadsheets) to get a complete picture of your sales data landscape. This would help determine which system is best for forecasting.

**Or you could:**
- Explore AI capability instead (team skills, infrastructure)
- Start evaluating that sales forecasting project (we'd recommend which system to use)
- Assess finance or operations data quality

**What you can do now:**
You can evaluate sales forecasting, but the feasibility depends on which system you'd use. Assessing your data warehouse specifically would clarify this.

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

### 7. **Surface Unconfirmed Inferences**
Always mention factors the LLM inferred but user hasn't validated
- ✅ "data_quality: 20% (75% confident, based on 3 mentions)"
- ✅ Show confirmed vs unconfirmed in status queries
- ✅ Offer quick validation: "Confirm these (2 min) → boost confidence"
- ✅ Cumulative evidence: confidence increases with more consistent mentions
- ❌ Single mention: "from 'scattered data'" (too weak)
- ❌ Treat inferences as facts without validation

---

## 9. Clarifying Question Patterns for Scoped Factors

The system uses intelligent clarifying questions to determine the appropriate scope (domain, system, team) for factor assessments. These questions help distinguish between organization-wide issues and domain/system-specific problems.

### Pattern 1: Narrow from Generic

**Trigger:** User makes generic statement about a factor

**Example Statement:** "Our sales data quality is poor"

**System Response:**
```
"Is this across all your sales systems (CRM, spreadsheets, databases), 
or mainly in specific tools?"
```

**Possible User Responses:**
- **"All systems"** → Keep generic scope `{domain: "sales", system: null}`, increase confidence
- **"Mainly Salesforce"** → Create specific scope `{domain: "sales", system: "salesforce_crm"}`, reduce generic confidence
- **"Not sure"** → Keep generic, flag for later clarification

**Storage:**
```json
{
  "generic_instance": {
    "scope": {"domain": "sales", "system": null},
    "value": 45,
    "confidence": 0.60,
    "refined_by": ["dq_sales_sfdc_001"]
  },
  "specific_instance": {
    "scope": {"domain": "sales", "system": "salesforce_crm"},
    "value": 30,
    "confidence": 0.80,
    "refines": "dq_sales_generic_001"
  }
}
```

### Pattern 2: Generalize from Specific

**Trigger:** User mentions specific system

**Example Statement:** "Salesforce data is incomplete"

**System Response:**
```
"Do other sales systems (data warehouse, spreadsheets) have similar issues, 
or is this isolated to Salesforce?"
```

**Possible User Responses:**
- **"Isolated to Salesforce"** → Keep only specific scope, don't create generic
- **"Similar everywhere"** → Create generic scope, link specific instances
- **"Haven't checked others"** → Keep specific, suggest checking others later

**Example Follow-up:**
```
User: "It's just Salesforce, our data warehouse is fine"

System: "Understood - data quality varies by system:
- Salesforce: ~35% (incomplete)
- Data warehouse: ~75% (fine)

For sales forecasting, which system would we use?"
```

### Pattern 3: Identify Domain

**Trigger:** User makes statement without domain context

**Example Statement:** "Our data quality is terrible"

**System Response:**
```
"Which data domains are you thinking about - sales, finance, operations, 
or across the organization?"
```

**Possible User Responses:**
- **"Sales"** → Create domain-specific scope `{domain: "sales", system: null}`
- **"Everything"** → Create org-wide scope `{domain: null, system: null}`, high confidence
- **"Not sure"** → Keep generic, ask about specific use case

**Example Follow-up:**
```
User: "Sales data mainly"

System: "Got it. Is this across all sales systems, or specific tools 
like your CRM, spreadsheets, or analytics platform?"
```

### Pattern 4: Resolve Contradictions

**Trigger:** New statement contradicts existing assessment

**Example Contradiction:**
- **Previous:** "Sales data quality is good" (generic = 75)
- **New:** "Salesforce data is incomplete" (specific = 35)

**System Response:**
```
"Earlier you mentioned sales data quality is good, but now you're saying 
Salesforce has issues. Is Salesforce the exception, or should I revise 
my understanding of overall sales data quality?"
```

**Possible User Responses:**
- **"Salesforce is the exception"** → Keep generic high (75), specific low (35)
- **"I was wrong earlier"** → Update generic to match specific reality
- **"Good is relative"** → Clarify scale interpretation

**Resolution:**
```json
{
  "generic_instance": {
    "scope": {"domain": "sales", "system": null},
    "value": 75,
    "confidence": 0.50,
    "note": "User indicated Salesforce is exception, other systems better"
  },
  "specific_instance": {
    "scope": {"domain": "sales", "system": "salesforce_crm"},
    "value": 35,
    "confidence": 0.80,
    "refines": "dq_sales_generic_001"
  }
}
```

### Pattern 5: Multiple Specifics → Generic Synthesis

**Trigger:** User mentions multiple systems with similar issues

**Example Sequence:**
```
User: "Our Salesforce data is incomplete"
System: Creates dq_sales_sfdc = 35

User: "And our sales spreadsheets are a mess"
System: Creates dq_sales_spreadsheets = 25

System detects pattern: Multiple sales systems with low quality
```

**System Response:**
```
"I'm noticing a pattern - sales data quality seems low across multiple systems 
(Salesforce ~35%, spreadsheets ~25%).

This suggests a broader sales data quality issue. Root causes might be:
- No data governance in sales department
- Lack of data entry training
- No data steward for sales

Want to explore what's causing this pattern?"
```

**Storage:**
```json
{
  "synthesized_generic": {
    "scope": {"domain": "sales", "system": null},
    "value": 30,
    "confidence": 0.75,
    "synthesized_from": ["dq_sales_sfdc", "dq_sales_spreadsheets"],
    "note": "Weighted average of specific instances"
  }
}
```

### Clarifying Question Guidelines

**When to Ask:**
- ✅ When scope is ambiguous ("our data" vs "sales data" vs "Salesforce data")
- ✅ When contradiction detected between generic and specific
- ✅ When pattern emerges across multiple systems
- ❌ Don't ask if context makes scope obvious
- ❌ Don't ask more than ONE clarifying question per user statement

**How to Ask:**
- ✅ Offer concrete options ("CRM, spreadsheets, databases")
- ✅ Allow "not sure" or "haven't checked" responses
- ✅ Frame as helpful clarification, not interrogation
- ❌ Don't use technical jargon ("scope dimensions", "instance hierarchy")
- ❌ Don't force user to answer before proceeding

**After Clarification:**
- Always acknowledge the clarification
- Show how it affects the assessment
- Proceed with the conversation naturally
- Store both generic and specific instances as appropriate

---

## 10. Scope-Aware Conversation Examples

### Example 1: Sales Forecasting with Scoped Data

```
User: "Can we do sales forecasting?"

System: [Determines needed scope: {domain: "sales", system: null}]
        [Retrieves applicable instances using scope matching]

"Based on what we've discussed about your sales data:

**Feasibility: Proceed with caution (45% confidence)**

Why 45%?
- ✅ Sales data availability is strong (80%) - you have 3 years of sales data
- ⚠️ Sales data quality is moderate (45%) - some issues in Salesforce (30%), 
  but might be better in other systems
- ❓ ML infrastructure unknown - haven't discussed this yet

**For a €15k pilot, 45% confidence is borderline.**

Which system would you use for forecasting - Salesforce, your data warehouse, 
or something else?"

User: "Probably the data warehouse"

System: "I don't have specific information about your data warehouse quality yet. 
Based on generic sales data quality (45%), I'd estimate moderate confidence.

Want to tell me about your data warehouse specifically? That would help 
refine the feasibility assessment."
```

### Example 2: Cross-Domain Factor Reuse

```
[Discussion 1: Sales Forecasting]
User: "Salesforce data is incomplete"
System: Stores data_quality {domain: "sales", system: "salesforce_crm"} = 35

[Discussion 2: Days Later - Customer Segmentation]
User: "Can we do customer segmentation?"

System: [Determines needed scope: {domain: "sales", system: "salesforce_crm"}]
        [Retrieves existing instance via scope matching]

"For customer segmentation using Salesforce data:

**Feasibility: Low confidence (35%)**

We already identified that Salesforce CRM data quality is around 35% 
(you mentioned incomplete data when we discussed sales forecasting).

For customer segmentation, we'd need:
- Data quality: 60%+ (currently: 35% ⚠️)
- Data completeness: customer attributes, purchase history
- ML infrastructure: clustering capabilities

Want to explore improving Salesforce data quality first, or consider 
using a different data source?"
```

### Example 3: Scope-Aware Status Response

```
User: "Where are we?"

System: "Here's what we've mapped out:

**Data Readiness: 60% mapped, 70% confident**

**Confirmed factors:**
- data_availability (Sales): 80% ✓ (you said "3 years of sales data")

**Unconfirmed inferences:**
- data_quality varies by system:
  • Salesforce CRM: 30% ⚠️ (80% confident, from "incomplete data" and "duplicates")
  • Sales overall: 45% ⚠️ (60% confident, inferred from Salesforce issues)
  • Finance: Not assessed yet
- data_governance (Sales): 15% (60% confident, from "no formal policies")

**What you can do now:**
You can evaluate sales forecasting projects, but confidence varies by 
which system you'd use:
- Using Salesforce: 35% confidence (low)
- Using data warehouse: 45% confidence (moderate, not assessed specifically)
- Using other systems: Unknown

Want to confirm those inferences, assess other systems, or proceed with 
current knowledge?"
```

### Example 4: Unknown System Discovery

```
User: "Our Cogglepoop system has data quality issues"

System: [Detects unknown system "Cogglepoop"]

"I'm not familiar with Cogglepoop. Could you help me understand:
- Which team or department uses it? (sales, finance, operations, etc.)
- What's it used for - customer data, financial data, operations?"

User: "It's our custom CRM for the sales team"

System: [Updates scope registry: systems.sales.push("cogglepoop_crm")]
        [Creates instance: data_quality {domain: "sales", system: "cogglepoop_crm"}]
        [Links to knowledge: "custom CRM" → similar to "salesforce_crm"]

"Got it - Cogglepoop is your custom CRM for sales. I'll track that.

Since it's a CRM, typical data quality issues include:
- Incomplete customer records
- Duplicate entries
- Inconsistent data entry

Which of these are you seeing?"
```

### Example 5: Scope Inheritance in Recommendations

```
User: "What AI projects could we do?"

System: [Retrieves all assessed factor instances]
        [Matches project archetypes to scoped assessments]

"Based on your assessments, here are 3 options:

**1. Sales Forecasting (Annual)**
   Feasibility: 60% confidence
   - Uses: Sales data warehouse (quality: 75% ✓)
   - Timeline: 8-12 weeks
   - Cost: €15-25k

**2. Salesforce Data Quality Improvement**
   Feasibility: 75% confidence
   - Addresses: Salesforce CRM issues (quality: 30% ⚠️)
   - Would unlock: Customer segmentation, lead scoring
   - Timeline: 6-8 weeks
   - Cost: €10-20k

**3. Finance Process Automation**
   Feasibility: 45% confidence
   - Uses: SAP ERP data (quality: 85% ✓)
   - But: Need to assess finance team readiness
   - Timeline: 10-14 weeks
   - Cost: €20-35k

Notice how Option 2 could improve Salesforce data quality, which would 
then enable more sales-focused AI projects. Want to explore any of these?"
```

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
✅ **Do:** Evaluate projects, enable export, let user own execution

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
