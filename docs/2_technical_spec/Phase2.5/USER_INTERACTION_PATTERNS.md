# User Interaction Patterns - Canonical Conversations

**Purpose:** Pure conversation examples. No system logic, no interpretation, no analysis.

**Note:** How to handle these goes in `alternative_X/` folders.

---

## Conversation 1: Happy Path

**Context:** User knows their output, can answer questions directly

```
System: "What output are you struggling with?"

User: "Sales Forecast - our monthly predictions are consistently off by 20-30%."

System: "Got it. Sales Forecast created by Sales Operations in CRM during forecasting process?"

User: "Yes."

System: "How urgent is fixing this?"  [MOMENT 1: Extract timeline urgency]

User: "Very urgent. Board is asking about forecast accuracy every week."

System: "What's the business impact of these errors?"  [MOMENT 2: Extract business impact]

User: "We're missing revenue targets. Cost us €500k last quarter."

System: "Let's assess 4 areas. First, data quality from upstream sources?"

User: "2 stars. Customer data is scattered across multiple systems and outdated."

System: "Team skills and resources?"

User: "2 stars. Team is junior, mostly fresh grads. And we're understaffed."

System: "What budget range could you work with for improvements?"  [MOMENT 4: Extract budget]

User: "Maybe €30k-€50k for a pilot."

System: "Process maturity?"

User: "1 star. No standard process, everyone does it their own way."

System: "CRM support for forecasting?"

User: "1 star. No forecasting tools, we export to Excel manually. We're locked into Salesforce though."

System: "Can you add integrations or plugins to Salesforce?"  [MOMENT 5: Extract vendor constraints]

User: "Yes, but procurement takes 3-6 months."
```

---

## Conversation 2: Edge Cases

**Context:** User is vague, contradicts themselves, doesn't know things, mentions dependencies

```
System: "What output are you struggling with?"

User: "Sales is a complete mess."

System: "Can you be more specific?"

User: "The forecasts are always wrong."

System: "Sales Forecast - is that what you mean?"

User: "Yes."

System: "Data quality from upstream?"

User: "Pretty good actually. We have clean data."

System: "Team skills?"

User: "The team is solid, mostly experienced people."

System: "Process maturity?"

User: "I don't know, I'm not involved in the process."

System: "CRM support?"

User: "The CRM is ancient, nobody likes it."

---

[Later in conversation]

User: "Actually, the data quality is horrible. We're using ad-hoc Excel files."

System: "Earlier you said data was clean?"

User: "I meant the CRM data is clean, but we also pull from Excel which is a mess."

---

[Even later]

User: "The forecasts depend on customer data from Marketing, but their data quality is only 60%."

System: "So there's an upstream dependency?"

User: "Yes, and the team is actually pretty junior - I was thinking of the old team."
```

---

## Conversation 3: Problem-to-Solution Jump

**Context:** System has gathered context, now needs to bridge problem → pain points → solutions

```
System: "Let me summarize what I understand:
- Output: Sales Forecast (accuracy metric)
- Current quality: 2 stars (20-30% error rate)
- Team: Sales Ops - Junior (mostly fresh grads)
- System: Salesforce CRM (no forecasting tools, manual Excel export)
- Process: Ad-hoc (no standardization)
- Dependencies: Customer data from Marketing (2 stars, scattered)

Is this accurate?"

User: "Yes, that's right."

System: "Based on this context, I see a few underlying issues:

1. **Knowledge gaps** - Junior team lacks forecasting expertise, no documentation or training materials
2. **Tool limitations** - CRM doesn't support forecasting workflow, forcing manual workarounds
3. **Process immaturity** - No standard methodology, each person does it differently
4. **Data quality issues** - Upstream dependency on scattered Marketing data

Does this match what you're experiencing?"

User: "Exactly. The knowledge gap is the biggest issue - we have no one to learn from."

System: "Before I recommend options, a few quick questions:  [MOMENT 7: Pre-recommendation checkpoint]
- What's your budget range for a pilot?
- How quickly do you need results?
- Is this a visible initiative or quiet improvement?"

User: "€30k-€50k budget, need results in 3 months, prefer quiet win first."

System: "Perfect. Given that knowledge transfer is the primary bottleneck and your constraints, here are 3 pilot options:

**Option 1: AI Forecasting Copilot** (Recommended)
- Provides real-time guidance during forecasting
- Learns from historical patterns
- Expected impact: 2 stars → 4 stars
- Timeline: 8-12 weeks (fits your 3-month window)
- Cost: €30k-€50k (fits budget)
- Quiet deployment: Start with 2-3 team members

**Option 2: Interactive Training System**
- Structured learning path for forecasting
- Practice scenarios with feedback
- Expected impact: 2 stars → 3 stars
- Timeline: 12-16 weeks (exceeds your timeline)
- Cost: €20k-€40k (fits budget)

**Option 3: Knowledge Base + RAG**
- Capture expert knowledge, make it searchable
- Answer forecasting questions on-demand
- Expected impact: 2 stars → 3 stars
- Timeline: 6-8 weeks (fits timeline)
- Cost: €15k-€30k (under budget)
- Quick win option

Which approach interests you most?"

User: "The Copilot sounds perfect. How does it work?"

System: "The AI Copilot integrates with your CRM and..."
```

---

## Conversation 4: Multi-Dimensional Problem

**Context:** Multiple bottlenecks, complex pain points, business constraints

```
System: "I see multiple bottlenecks:
- Team: 2 stars (junior, knowledge gaps)
- System: 1 star (no forecasting tools)
- Process: 1 star (no standardization)
- Dependencies: 2 stars (scattered data)

You also mentioned board pressure and tight budget.  [INFERRED: timeline_urgency: high, cost_sensitivity: high]

Let me identify the pain points:

1. **Knowledge silos** - No expert to learn from, tribal knowledge lost
2. **Tool gaps** - Manual Excel workarounds, no automation
3. **Process chaos** - Everyone does it differently, no playbook
4. **Data fragmentation** - Multiple sources, no single source of truth

Given your constraints (need quick wins, limited budget), which pain point hurts most?"

User: "The tool situation. We're wasting hours on manual work."

System: "Focusing on tool automation, here are options:

**Option 1: Workflow Automation**
- Automate data collection from multiple sources
- Auto-populate forecast templates
- Expected impact: Saves 10-15 hours/week, improves consistency
- Timeline: 4-6 weeks
- Cost: €10k-€20k (fits budget constraint)

**Option 2: Intelligent CRM Features**
- Add AI-powered forecasting module to existing CRM
- Predictive analytics, anomaly detection
- Expected impact: 1 star → 3 stars on system capability
- Timeline: 12-16 weeks
- Cost: €40k-€60k (over budget)

Given cost sensitivity, Option 1 gives you quick wins while you build budget for Option 2."

User: "That makes sense. Let's start with automation."
```

---

## Conversation 5: Feasibility Assessment & Report Generation

**Context:** System checks prerequisites, identifies gaps, offers comprehensive report

```
System: "Before I recommend options, a few quick questions to assess feasibility:

1. Data Quality: What % of your historical data has missing values?
   - Less than 10% (mostly complete)
   - 10-30% (some gaps but usable)
   - More than 30% (significant quality issues)

2. Data Refresh: How often is your CRM data updated?
   - Daily
   - Weekly
   - Monthly or less

3. Compliance: Is sales forecasting in a regulated domain for you?
   - Yes (financial services, healthcare, etc.)
   - No (standard B2B/B2C sales)"

User: "10-30% missing values, weekly updates, not regulated."

System: "Perfect. Based on your situation, here are 3 options:

**Option 1: AI Forecasting Copilot** ✅ Ready (Recommended)
- Expected impact: ⭐⭐ → ⭐⭐⭐⭐
- Timeline: 8-12 weeks
- Cost: €30k-€50k
- Prerequisites: None, ready to start
- Feasibility: High (80-90% success probability)

**Option 2: Knowledge Base + RAG** ✅ Ready
- Expected impact: ⭐⭐ → ⭐⭐⭐
- Timeline: 6-8 weeks
- Cost: €15k-€30k
- Prerequisites: None, ready to start
- Feasibility: High (80-90% success probability)

**Option 3: Predictive Forecasting AI** ⚠️ Minor Gaps
- Expected impact: ⭐⭐ → ⭐⭐⭐⭐⭐
- Timeline: 16-22 weeks (includes 4-6 weeks prep)
- Cost: €60k-€100k (includes €10k-€20k prep)
- Prerequisites: Data cleaning, team training needed
- Feasibility: Medium-High (60-80% success probability)
- Note: Exceeds budget and timeline constraints

Which approach interests you most?"

User: "Option 1 sounds good, but I need to get approval from the VP."

System: "I can generate a detailed assessment report with:
- All 7 solution options (not just these 3)
- Complete prerequisite breakdown
- Cost-to-bridge-gaps estimates
- Decision matrix comparing all options
- Staged approach recommendations

This is a professional document you can share with stakeholders. Would that help?"

User: "Yes, that would be perfect."

System: "Generating comprehensive assessment report...

[Download: Assessment_Report_Sales_Forecast_2025-11-04.pdf]

The report includes:
- Executive summary (1 page)
- Top 3 recommendations with detailed implementation plans (3-5 pages)
- 4 alternative solutions with feasibility analysis (2-3 pages)
- Prerequisite deep dive (data, team, system, organizational) (3-4 pages)
- Staged approach recommendation (1-2 pages)
- Decision matrix comparing all 7 options (1 page)
- Appendix with detailed definitions (2-3 pages)

Total: 13-18 pages

You can share this with your VP. Let me know if you have questions or need any adjustments."

User: "This is great. One question - can we actually skip the data cleaning for Option 3? Our core data is cleaner than I described."

System: "Got it. Let me re-assess Option 3 with better data quality...

**Updated: Predictive Forecasting AI** ✅ Ready
- Expected impact: ⭐⭐ → ⭐⭐⭐⭐⭐
- Timeline: 12-16 weeks (no prep needed)
- Cost: €50k-€80k (no prep costs)
- Prerequisites: All met (with updated data quality)
- Feasibility: High (80-90% success probability)
- Note: Still exceeds budget (€50k-€80k vs €30k-€50k)

Would you like an updated report with this adjustment?"

User: "No, the current report is fine. I'll discuss budget with the VP."
```

---

## What These Show

**Conversation 3 (Problem-to-Solution Jump):**
- System summarizes gathered context
- Identifies underlying pain points (not just symptoms)
- User validates/corrects pain point interpretation
- **Moment 7 checkpoint:** Asks for missing critical factors (budget, timeline, visibility)
- System recommends 2-3 targeted pilots
- Explains expected impact per pilot **with constraint fit** (timeline, cost)
- User selects based on priorities

**Conversation 4 (Multi-Dimensional Problem):**
- Multiple bottlenecks identified
- **Business constraints inferred** from earlier conversation (board pressure, tight budget)
- Pain points prioritized by user
- Solutions ranked by constraints (budget, timeline)
- Trade-offs explained clearly
- Quick win vs long-term solution path

**Conversation 5 (Feasibility Assessment & Report):**
- System asks targeted prerequisite questions (data quality, refresh cadence, compliance)
- Feasibility checked automatically against archetype prerequisites
- Recommendations presented with feasibility badges (✅ Ready, ⚠️ Minor Gaps)
- User requests comprehensive report for stakeholder approval
- System generates 13-18 page professional document
- User overrides prerequisite assessment ("data is cleaner than described")
- System re-assesses and adjusts feasibility tier in real-time

**Conversation 1 (Happy Path):**
- User knows the output
- Can answer all questions
- Provides specific ratings
- Gives concrete examples
- **Business context extracted naturally:** Timeline urgency (Moment 1), business impact (Moment 2), budget (Moment 4), vendor constraints (Moment 5)

**Conversation 2 (Edge Cases):**
- Vague initial statement ("Sales is a mess")
- Progressive refinement (mess → forecasts → Sales Forecast)
- Contradictions (data "good" → "horrible")
- Partial knowledge ("I don't know")
- Generic mentions ("CRM is ancient")
- Clarifications (CRM data vs Excel data)
- Dependencies mentioned (Marketing → Sales)
- Corrections (experienced → junior)

---

## Evaluation Criteria

Any representation model must handle:

### Assessment Phase (Patterns 1-8)
1. **Vagueness** - "Sales is a mess"
2. **Specificity** - "2 stars, scattered data"
3. **Contradictions** - "good" then "horrible"
4. **Unknowns** - "I don't know"
5. **Generic statements** - "CRM is ancient"
6. **Progressive refinement** - Vague → specific over time
7. **Cross-output mentions** - Marketing data affects Sales
8. **Corrections** - User changes their mind

### Recommendation Phase (Patterns 9-13)
9. **Pain point inference** - Gap → underlying issues (knowledge gaps, tool limitations, etc.)
10. **Business context extraction** - Extract constraints (budget, timeline, visibility) naturally throughout conversation
11. **Feasibility assessment** - Check prerequisites, identify gaps, calculate cost-to-bridge
12. **Solution mapping** - Pain points + context + constraints + feasibility → targeted pilot recommendations
13. **Report generation** - Comprehensive assessment document for stakeholder approval

Each alternative model should briefly explain how it handles all 13 patterns.

---

## Business Context Extraction Moments

Throughout conversations, system extracts business decision factors at natural moments:

**Moment 1:** After output identified → Timeline urgency, competitive pressure  
**Moment 2:** When user describes pain intensity → Business impact, cost of problem  
**Moment 3:** When user mentions stakeholders → Visibility preference, stakeholder pressure  
**Moment 4:** When user reveals constraints → Budget range, resource constraints  
**Moment 5:** When discussing tools → Vendor constraints, procurement friction  
**Moment 6:** When user mentions compliance → Compliance requirements, data sovereignty  
**Moment 7:** Pre-recommendation checkpoint → Ask missing critical factors (budget, timeline, visibility)  
**Moment 8:** When user asks about solutions → Risk tolerance, solution scope preference  

**See Alternative B:** `BUSINESS_CONTEXT_EXTRACTION.md` for detailed strategy
