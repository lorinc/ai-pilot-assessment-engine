# Alternative B: Feasibility Assessment & Reporting Strategy

**Status:** Design Decision  
**Date:** 2025-11-04

---

## Core Principle: Light Conversational, Deep Report

**Two-tier recommendation strategy:**
1. **In-conversation:** 2-3 targeted recommendations with high-level feasibility
2. **Downloadable report:** Comprehensive assessment with 5-10+ options, full prerequisite analysis

**Rationale:** Users need fast decisions in conversation, comprehensive analysis for stakeholders.

---

## 1. Feasibility Assessment Architecture

### Data Source: AI Archetype Prerequisites

**File:** `src/data/inference_rules/ai_archetype_prerequisites.json`

**Granularity:** 27 AI archetypes (from `ai_archetypes.json`)

**Why archetypes, not specific pilots:**
- 27 archetypes is manageable (vs 10,000+ solution permutations)
- Archetypes are stable (won't change frequently)
- Covers all solution space comprehensively
- LLM maps specific problem → archetype at runtime
- Specific pilots inherit prerequisites from their archetype

---

### Prerequisite Structure Per Archetype

```json
{
  "archetype_id": "predictive_analytics_forecasting",
  "archetype_name": "Predictive Analytics & Forecasting",
  
  "data_prerequisites": {
    "historical_data": {
      "minimum_timespan": "12-24 months",
      "minimum_volume": "500+ records",
      "required_fields": ["timestamp", "outcome_variable", "predictor_variables"],
      "data_quality_requirements": [
        "Completeness: <10% missing values in key fields",
        "Accuracy: Labeled outcomes must be verified",
        "Timeliness: Data must be current (not stale)",
        "Consistency: Schema must be stable over time"
      ],
      "deal_breakers": [
        "No historical data available",
        "Outcome variable not tracked",
        "Data quality too poor to clean (<50% usable)"
      ]
    },
    "data_infrastructure": {
      "storage": "Centralized data warehouse or lake",
      "access": "API or SQL access to historical data",
      "refresh_cadence": "Weekly or better"
    }
  },
  
  "team_prerequisites": {
    "domain_expertise": {
      "required": "Understanding of forecasting domain",
      "level": "Intermediate (can explain what good forecast looks like)",
      "deal_breakers": ["No one understands the domain"]
    },
    "technical_skills": {
      "required": "Basic ML/AI literacy",
      "level": "Can interpret model outputs, understand confidence intervals",
      "deal_breakers": ["Team rejects AI/ML entirely"]
    },
    "capacity": {
      "required": "2-4 hours/week for pilot duration",
      "roles": ["Domain expert", "Data owner", "End user representative"],
      "deal_breakers": ["No capacity for pilot participation"]
    }
  },
  
  "system_prerequisites": {
    "integration": {
      "required": "API access to source systems",
      "complexity": "Medium (read-only API sufficient)",
      "deal_breakers": ["No API access, no export capability"]
    },
    "infrastructure": {
      "required": "Cloud compute for model training",
      "alternatives": ["Can use vendor-hosted solution"],
      "deal_breakers": ["No cloud access, no vendor allowed"]
    },
    "deployment": {
      "required": "Ability to integrate predictions back into workflow",
      "complexity": "Medium (can be manual initially)",
      "deal_breakers": ["No way to use predictions in practice"]
    }
  },
  
  "organizational_prerequisites": {
    "change_readiness": {
      "required": "Willingness to trust AI recommendations",
      "level": "Medium (start with human-in-loop)",
      "deal_breakers": ["Organization rejects AI-driven decisions"]
    },
    "stakeholder_support": {
      "required": "Executive sponsor for pilot",
      "level": "Director-level or above",
      "deal_breakers": ["No budget authority, no air cover"]
    },
    "compliance": {
      "considerations": ["Model explainability may be required", "Bias testing if regulated"],
      "deal_breakers": ["Regulated domain forbids ML predictions"]
    }
  },
  
  "feasibility_tiers": {
    "tier_1_ready": {
      "description": "Prerequisites fully met, can start immediately",
      "timeline_impact": "0 weeks",
      "cost_impact": "€0",
      "success_probability": "High (80-90%)"
    },
    "tier_2_minor_gaps": {
      "description": "1-2 prerequisites need minor work",
      "typical_gaps": ["Data needs cleaning", "Team needs training"],
      "timeline_impact": "+4-6 weeks",
      "cost_impact": "+€10k-€20k",
      "success_probability": "Medium-High (60-80%)"
    },
    "tier_3_major_gaps": {
      "description": "3+ prerequisites missing or major work needed",
      "typical_gaps": ["No historical data", "No API access", "No domain expertise"],
      "timeline_impact": "+8-16 weeks",
      "cost_impact": "+€30k-€60k",
      "success_probability": "Medium (40-60%)",
      "recommendation": "Consider staged approach or different archetype"
    },
    "tier_4_not_feasible": {
      "description": "Deal-breakers present",
      "typical_deal_breakers": ["No data", "No capacity", "Compliance forbids"],
      "recommendation": "Do not recommend this archetype"
    }
  }
}
```

---

## 2. Feasibility Inference Flow

### Step 1: User Assessment Complete
**Input:** User's current state from graph

```
Output: Sales Forecast
Edges:
- People → Output: ⭐⭐ (junior team, limited ML literacy)
- Tool → Output: ⭐ (no forecasting tools, Salesforce CRM with API)
- Process → Output: ⭐ (ad-hoc, no standardization)
- Dependency → Output: ⭐⭐ (18 months historical data, some quality gaps)

Business Context:
- Budget: €30k-€50k
- Timeline: 3 months
- Visibility: Quiet win preferred
- Stakeholder: Board pressure (exec support)
```

---

### Step 2: LLM Identifies Relevant Archetypes
**LLM Prompt:**
```
Given bottlenecks and context, identify 5-7 relevant AI archetypes.

Context: {user_state}
Pain Point Catalog: {pain_point_mapping.json}
AI Archetype Catalog: {ai_archetypes.json}

Rank by relevance to user's problem.

Output: 
1. Predictive Analytics & Forecasting (high relevance)
2. Conversational AI / Copilot (high relevance)
3. Information Retrieval / RAG (medium relevance)
4. Workflow Automation (medium relevance)
5. Classification (low relevance)
```

---

### Step 3: Load Prerequisites for Each Archetype
**System loads from `ai_archetype_prerequisites.json`:**
- Predictive Analytics & Forecasting → prerequisites
- Conversational AI / Copilot → prerequisites
- Information Retrieval / RAG → prerequisites
- Workflow Automation → prerequisites
- Classification → prerequisites

---

### Step 4: Feasibility Check (Automated + Clarifying Questions)

**For each archetype, check prerequisites against user state:**

**Example: Predictive Analytics & Forecasting**

```
Data Prerequisites:
✅ Historical data: 18 months available (meets 12-24 month requirement)
⚠️ Data quality: "Some gaps" → Need to verify if <10% missing values
✅ Data infrastructure: In CRM (centralized)
✅ Access: CRM has API
⚠️ Refresh cadence: Unknown (need to ask)

Team Prerequisites:
✅ Domain expertise: Sales Ops team understands forecasting
⚠️ Technical skills: "Limited ML literacy" → Below required level
✅ Capacity: Assume available (can verify if needed)

System Prerequisites:
✅ Integration: CRM has API
✅ Infrastructure: User mentioned AWS access
✅ Deployment: Can integrate back into CRM

Organizational Prerequisites:
✅ Change readiness: User seeking AI solution (implies willingness)
✅ Stakeholder support: Board pressure (implies exec support)
⚠️ Compliance: Unknown (need to ask if regulated)

Missing Information (need to ask):
1. Data quality: Can you quantify missing values? (<10%, 10-30%, >30%)
2. Data refresh: How often is data updated? (Daily, weekly, monthly)
3. Compliance: Is this a regulated domain? (Financial, healthcare, etc.)
```

**System asks clarifying questions:**
```
System: "A few quick questions to assess feasibility:

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
```

**User answers:**
```
1. 10-30% (some gaps but usable)
2. Weekly
3. No (standard B2B sales)
```

---

### Step 5: Feasibility Tier Classification

**System calculates for each archetype:**

**Predictive Analytics & Forecasting:**
```
Prerequisites Status:
✅ Data: 18 months historical (sufficient)
⚠️ Data quality: 10-30% missing → Needs cleaning
✅ Data refresh: Weekly (sufficient)
✅ Team domain expertise: Present
⚠️ Team technical skills: Limited → Needs training
✅ System integration: API available
✅ Infrastructure: AWS access
✅ Organizational: Support present
✅ Compliance: Not regulated

Gaps:
1. Data quality needs improvement (minor gap)
2. Team needs ML training (minor gap)

Feasibility Tier: Tier 2 (Minor Gaps)
- Timeline impact: +4-6 weeks
- Cost impact: +€10k-€20k
- Success probability: 60-80%
```

**Conversational AI / Copilot:**
```
Prerequisites Status:
✅ Data: Historical data available (sufficient for training)
✅ Data quality: 10-30% missing → Acceptable for copilot
✅ Team domain expertise: Present
✅ Team technical skills: No ML literacy required
✅ System integration: API available
✅ Infrastructure: AWS access
✅ Organizational: Support present

Gaps: None

Feasibility Tier: Tier 1 (Ready)
- Timeline impact: 0 weeks
- Cost impact: €0
- Success probability: 80-90%
```

---

### Step 6: Rank by Fit Score

**Fit score calculation:**
```
Fit Score = (Relevance × 0.4) + (Feasibility × 0.3) + (Budget Fit × 0.2) + (Timeline Fit × 0.1)

Predictive Analytics & Forecasting:
- Relevance: 0.9 (high)
- Feasibility: 0.7 (Tier 2)
- Budget fit: 0.5 (€60k-€100k vs €30k-€50k budget → over budget)
- Timeline fit: 0.4 (16-22 weeks vs 3 months → exceeds timeline)
→ Fit score: 0.69

Conversational AI / Copilot:
- Relevance: 0.9 (high)
- Feasibility: 0.9 (Tier 1)
- Budget fit: 1.0 (€30k-€50k vs €30k-€50k budget → perfect fit)
- Timeline fit: 1.0 (8-12 weeks vs 3 months → fits timeline)
→ Fit score: 0.93

Information Retrieval / RAG:
- Relevance: 0.6 (medium)
- Feasibility: 0.9 (Tier 1)
- Budget fit: 1.0 (€15k-€30k vs €30k-€50k budget → under budget)
- Timeline fit: 1.0 (6-8 weeks vs 3 months → fits timeline)
→ Fit score: 0.76
```

**Ranked:**
1. Conversational AI / Copilot (0.93)
2. Information Retrieval / RAG (0.76)
3. Predictive Analytics & Forecasting (0.69)

---

## 3. In-Conversation Recommendations (Top 3)

**System presents light recommendations:**

```
System: "Based on your situation, here are 3 options:

**Option 1: AI Forecasting Copilot** ✅ Ready (Recommended)
- Provides real-time guidance during forecasting
- Expected impact: ⭐⭐ → ⭐⭐⭐⭐
- Timeline: 8-12 weeks
- Cost: €30k-€50k
- Prerequisites: None, ready to start
- Feasibility: High (80-90% success probability)

**Option 2: Knowledge Base + RAG** ✅ Ready
- Capture expert knowledge, make it searchable
- Expected impact: ⭐⭐ → ⭐⭐⭐
- Timeline: 6-8 weeks
- Cost: €15k-€30k
- Prerequisites: None, ready to start
- Feasibility: High (80-90% success probability)

**Option 3: Predictive Forecasting AI** ⚠️ Minor Gaps
- AI-powered predictions from historical data
- Expected impact: ⭐⭐ → ⭐⭐⭐⭐⭐
- Timeline: 16-22 weeks (includes 4-6 weeks prep)
- Cost: €60k-€100k (includes €10k-€20k prep)
- Prerequisites: Data cleaning, team training needed
- Feasibility: Medium-High (60-80% success probability)
- Note: Exceeds budget and timeline constraints

Which approach interests you most?"
```

---

## 4. Downloadable Report (Comprehensive)

### Report Trigger Points

**When to offer report:**
1. User asks "What are all my options?"
2. User mentions "need to get approval" or "share with stakeholders"
3. User says "send me something I can forward"
4. After user selects option (as next step documentation)
5. Automatically at end of assessment

**System prompt:**
```
System: "I can generate a detailed assessment report with:
- All 5-7 solution options (not just top 3)
- Complete prerequisite breakdown
- Cost-to-bridge-gaps estimates
- Decision matrix comparing all options
- Staged approach recommendations

This is a professional document you can share with stakeholders. 
Would that be helpful?"
```

---

### Report Structure

**File format:** PDF or Markdown  
**Filename:** `Assessment_Report_[Output]_[Date].pdf`

---

#### Section 1: Executive Summary (1 page)

```
AI Pilot Assessment Report
Output: Sales Forecast
Date: 2025-11-04

Current State:
- Quality: ⭐⭐ (20-30% error rate)
- Required: ⭐⭐⭐⭐ (5-10% error rate)
- Gap: 2 stars

Bottlenecks Identified:
- Team: ⭐⭐ (junior, limited ML literacy)
- System: ⭐ (no forecasting tools)
- Process: ⭐ (ad-hoc, no standardization)
- Dependencies: ⭐⭐ (data quality gaps)

Business Context:
- Budget: €30k-€50k
- Timeline: 3 months
- Stakeholder: Board pressure (exec support)
- Visibility: Quiet win preferred

Top Recommendation:
AI Forecasting Copilot (€30k-€50k, 8-12 weeks, High feasibility)
```

---

#### Section 2: Recommended Solutions (3-5 pages)

**For each of top 3 solutions:**

```
Solution 1: AI Forecasting Copilot

Overview:
Real-time AI assistant that guides users through forecasting workflow, 
provides suggestions based on historical patterns, and flags potential errors.

Expected Impact:
- Current: ⭐⭐ (20-30% error rate)
- Target: ⭐⭐⭐⭐ (5-10% error rate)
- Improvement: 2 stars

Timeline: 8-12 weeks
- Weeks 1-2: Requirements gathering, data access setup
- Weeks 3-6: Copilot development, training on historical data
- Weeks 7-10: Pilot with 2-3 users, iteration
- Weeks 11-12: Rollout to full team

Cost: €30k-€50k
- Development: €20k-€35k
- Infrastructure: €5k-€10k
- Training: €5k

Prerequisites: ✅ All Met
- Data: 18 months historical data available
- Team: Domain expertise present, no ML literacy required
- System: CRM API access available
- Infrastructure: AWS access confirmed
- Organizational: Exec support, experimentation-friendly

Feasibility: Tier 1 (Ready)
- Success probability: 80-90%
- Timeline impact: 0 weeks (no prep needed)
- Cost impact: €0 (no prerequisite work)

Risks:
- Low: User adoption (mitigated by gradual rollout)
- Low: Data quality (copilot handles noisy data well)

Success Metrics:
- Forecast error rate: 20-30% → 5-10%
- Time to complete forecast: -30% reduction
- User satisfaction: >4/5 stars

Next Steps:
1. Secure budget approval (€30k-€50k)
2. Identify 2-3 pilot users
3. Set up data access (1-2 weeks)
4. Begin development (Week 3)
```

---

#### Section 3: Alternative Solutions (2-3 pages)

**For each of 5-7 additional solutions:**

```
Solution 4: Workflow Automation

Overview:
Automate data collection from multiple sources, auto-populate forecast 
templates, reduce manual work.

Expected Impact:
- Current: ⭐⭐ (20-30% error rate)
- Target: ⭐⭐⭐ (10-15% error rate)
- Improvement: 1 star (less than Copilot)

Timeline: 6-8 weeks
Cost: €20k-€40k

Prerequisites: ✅ Mostly Met
- Data: Multiple sources identified
- System: API access available
- Team: No special skills required

Feasibility: Tier 1 (Ready)
- Success probability: 80-90%

Why Not Recommended:
- Lower impact than Copilot (1 star vs 2 stars)
- Doesn't address knowledge gap (main bottleneck)
- Similar cost to Copilot but less value

When to Consider:
- If manual work is primary pain point (not knowledge gap)
- If team rejects AI-assisted decision making
- As complement to Copilot (Release 2)
```

---

#### Section 4: Feasibility Deep Dive (3-4 pages)

**Detailed prerequisite analysis:**

```
Data Prerequisites Analysis

Current State:
- Historical data: 18 months of sales forecasts in CRM
- Data volume: ~500 forecast records
- Data quality: 10-30% missing values (some gaps but usable)
- Data refresh: Weekly updates
- Data access: CRM API available

What Each Solution Needs:

Predictive Analytics & Forecasting:
- Minimum: 12-24 months historical data ✅ Met
- Minimum: 500+ records ✅ Met
- Data quality: <10% missing values ❌ Not met (currently 10-30%)
- Refresh: Weekly or better ✅ Met
- Gap: Data cleaning required
- Cost to bridge: €5k-€10k (2-3 weeks data cleaning)

Conversational AI / Copilot:
- Minimum: 6-12 months historical data ✅ Met
- Data quality: Tolerates 10-30% missing ✅ Met
- Refresh: Weekly or better ✅ Met
- Gap: None
- Cost to bridge: €0

Information Retrieval / RAG:
- Minimum: Documented knowledge base ⚠️ Partial (tribal knowledge)
- Data quality: Not critical ✅ Met
- Gap: Knowledge capture needed
- Cost to bridge: €5k-€10k (2-3 weeks knowledge capture)

[Repeat for Team, System, Organizational prerequisites]
```

---

#### Section 5: Staged Approach Recommendations (1-2 pages)

**If major gaps exist:**

```
Recommended Phased Approach

Your current state has minor gaps that can be addressed incrementally.

Release 1: Quick Win (Months 1-3)
Solution: AI Forecasting Copilot
- Timeline: 8-12 weeks
- Cost: €30k-€50k
- Prerequisites: None (ready to start)
- Impact: ⭐⭐ → ⭐⭐⭐⭐
- Benefit: Immediate improvement, builds AI confidence

Release 2: Build Foundation (Months 4-5)
Solution: Data Quality Improvement
- Timeline: 4-6 weeks
- Cost: €10k-€20k
- Prerequisites: None
- Impact: Data quality ⭐⭐ → ⭐⭐⭐⭐
- Benefit: Enables advanced AI solutions

Phase 3: Advanced Solution (Months 6-9)
Solution: Predictive Forecasting AI
- Timeline: 12-16 weeks
- Cost: €50k-€80k
- Prerequisites: Release 2 complete
- Impact: ⭐⭐⭐⭐ → ⭐⭐⭐⭐⭐
- Benefit: Maximum accuracy, fully automated

Total Investment: €90k-€150k over 9 months
Total Impact: ⭐⭐ → ⭐⭐⭐⭐⭐ (3 star improvement)

Alternative: Start with Release 1 only, re-assess after 3 months.
```

---

#### Section 6: Decision Matrix (1 page)

**Table comparing all solutions:**

| Solution | Impact | Timeline | Cost | Feasibility | Prerequisites | Risk | Fit Score |
|----------|--------|----------|------|-------------|---------------|------|-----------|
| AI Copilot | ⭐⭐⭐⭐ | 8-12 wks | €30-50k | ✅ Ready | None | Low | 0.93 |
| RAG / KB | ⭐⭐⭐ | 6-8 wks | €15-30k | ✅ Ready | None | Low | 0.76 |
| Predictive AI | ⭐⭐⭐⭐⭐ | 16-22 wks | €60-100k | ⚠️ Minor Gaps | Data cleaning, training | Med | 0.69 |
| Workflow Auto | ⭐⭐⭐ | 6-8 wks | €20-40k | ✅ Ready | None | Low | 0.65 |
| Classification | ⭐⭐ | 8-10 wks | €25-45k | ⚠️ Minor Gaps | Training data | Med | 0.52 |

**Color coding:**
- Green: Fits budget and timeline
- Yellow: Slightly exceeds constraints
- Red: Significantly exceeds constraints

---

#### Section 7: Appendix (2-3 pages)

**Detailed prerequisite definitions:**
- What "data quality" means per archetype
- What "ML literacy" means per archetype
- What "API access" means per archetype
- Success probability calibration methodology
- Assumptions and limitations

---

## 5. Implementation Requirements

### Module 1: Feasibility Checker
**File:** `engines/feasibility_checker.py`

**Responsibilities:**
- Load archetype prerequisites from JSON
- Match user state to prerequisites
- Identify missing information
- Generate clarifying questions
- Calculate feasibility tier (1-4)
- Adjust timeline/cost based on gaps
- Calculate fit score

**Effort:** 16 hours

---

### Module 2: Report Generator
**File:** `engines/report_generator.py`

**Responsibilities:**
- Generate PDF or Markdown report
- Format all sections (1-7)
- Create decision matrix table
- Generate charts (optional)
- Handle user branding (optional)

**Effort:** 8 hours

---

### Module 3: Recommendation Presenter
**File:** `utils/recommendation_formatter.py`

**Responsibilities:**
- Format light recommendations for conversation (top 3)
- Format deep recommendations for report (5-10+)
- Handle feasibility badges (✅ Ready, ⚠️ Minor Gaps, ❌ Major Gaps)
- Generate user-friendly explanations

**Effort:** 4 hours

---

### Data Work: Document Archetype Prerequisites
**File:** `src/data/inference_rules/ai_archetype_prerequisites.json`

**Tasks:**
- Research prerequisites for 27 archetypes
- Define feasibility tiers per archetype
- Document deal-breakers per archetype
- Validate with domain experts

**Effort:** 54 hours (2 hours per archetype)

---

### Total Effort: 82 hours (~2 weeks)

---

## 6. Success Metrics

### Recommendation Quality
- **Precision:** % of recommended pilots that user considers relevant (target: >80%)
- **Feasibility accuracy:** % of feasibility assessments validated by user (target: >70%)
- **User selection rate:** % of recommendations that user selects (target: >50%)

### Report Utility
- **Download rate:** % of users who request report (target: >60%)
- **Stakeholder sharing:** % of reports shared with stakeholders (target: >40%)
- **Approval rate:** % of reports that lead to pilot approval (target: >30%)

### User Experience
- **Clarity:** User understands feasibility reasoning (measured via feedback)
- **Trust:** User trusts feasibility assessment (measured via override rate)
- **Satisfaction:** User finds recommendations helpful (measured via survey)

---

## 7. User Override Mechanism

**System presents inference, user can challenge:**

```
System: "Based on your data quality (10-30% missing values), I'm concerned 
Predictive AI may need data cleaning first. This adds 2-3 weeks and €5k-€10k.

However, if your data is cleaner than described, or you're willing to proceed 
with current quality, we can skip this step."

User: "Actually, the missing values are in non-critical fields. Core data is clean."

System: "Got it. Re-assessing feasibility..."
→ Re-run feasibility check with updated data quality
→ May move from Tier 2 to Tier 1
→ Adjust timeline/cost accordingly
```

**Override is respected and documented in report.**

---

## Conclusion

**Two-tier strategy balances speed and depth:**
- In-conversation: Fast decision (2-3 options, high-level feasibility)
- Report: Comprehensive analysis (5-10+ options, full prerequisite breakdown)

**Feasibility assessment prevents failed pilots:**
- Prerequisites checked against user state
- Gaps identified with cost-to-bridge estimates
- Feasibility tiers guide risk assessment
- User override mechanism maintains flexibility

**Implementation effort: 82 hours (~2 weeks)**
- 54 hours: Document 27 archetype prerequisites
- 28 hours: Build feasibility checker + report generator

**Status:** Ready for implementation
