# AI Pilot Assessment Engine

A **conversational AI pilot recommendation system** that helps organizations identify AI opportunities through natural dialogue. The system assesses organizational outputs (deliverables, work products) through their contributing factors, identifies bottlenecks, and recommends targeted AI pilots to address them.

**Core Innovation:** Output-centric assessment with LLM-powered semantic inference for solution recommendations.

---

## Quick Links

**📖 Documentation:**
- **Functional Specification:** [`docs/1_functional_spec/`](docs/1_functional_spec/)
  - [User Interaction Patterns](docs/1_functional_spec/USER_INTERACTION_PATTERNS.md) - Canonical conversation examples
  - [Representation Model](docs/1_functional_spec/REPRESENTATION.md) - Edge-based factor model
  - [Business Context Extraction](docs/1_functional_spec/BUSINESS_CONTEXT_EXTRACTION.md) - Natural constraint extraction
  - [Solution Recommendation](docs/1_functional_spec/SOLUTION_RECOMMENDATION.md) - LLM semantic inference
  - [Feasibility Assessment](docs/1_functional_spec/FEASIBILITY_AND_REPORTING.md) - Prerequisites and reporting
  
- **Technical Specification:** [`docs/2_technical_spec/`](docs/2_technical_spec/)
  - [Implementation & Deployment Plan](docs/2_technical_spec/IMPLEMENTATION_DEPLOYMENT_PLAN.md) - Complete technical roadmap

**🎯 Key Concepts:**
- [What This System Does](#what-this-system-does)
- [How It Works](#how-it-works)
- [Technical Architecture](#technical-architecture)

---

## What This System Does

### The Problem

Organizations struggle to identify which AI pilots to pursue because:
- **Combinatorial complexity:** 46+ outputs × 4 bottleneck types × 100+ pain points × 27 AI archetypes
- **Context matters:** Same bottleneck (e.g., "junior team") requires different solutions based on context
- **Stakeholder alignment:** Need comprehensive analysis for approval, not just quick recommendations

### The Solution

A conversational system that:
1. **Identifies struggling outputs** through natural dialogue ("Sales forecasts are always wrong")
2. **Assesses contributing factors** via edge-based model (People, Tools, Processes, Dependencies)
3. **Calculates bottlenecks** using MIN() - weakest link determines output quality
4. **Extracts business context** naturally (budget, timeline, visibility preferences)
5. **Recommends AI pilots** using LLM semantic inference (not hardcoded rules)
6. **Checks feasibility** against archetype prerequisites
7. **Generates comprehensive reports** for stakeholder approval (13-18 pages)

---

## How It Works

### 1. Edge-Based Factor Model

**Outputs are assessed through their contributing edges:**

```
Nodes:
  - Output (deliverable: Sales Forecast, Customer Support Ticket, etc.)
  - People (team archetype: Sales Ops - Junior, Data Engineers - Senior)
  - Tool (system: Salesforce CRM, Excel, Custom Dashboard)
  - Process (workflow: Forecasting Process, Data Entry Workflow)

Edges (the factors):
  - People → Output (team's effect on output quality)
  - Tool → Output (system's effect on output quality)
  - Process → Output (process's effect on output quality)
  - Output → Output (upstream dependency's effect)
```

**Each edge has:**
- **Evidence array:** User statements with confidence tiers (1-5)
- **Current score:** 1-5 stars (calculated via Bayesian aggregation)
- **Current confidence:** 0.0-1.0 (based on evidence weight)

**Output quality = MIN(all incoming edges)** - weakest link determines quality.

### 2. Evidence-Based Assessment

**Tier-weighted evidence aggregation:**
- **Tier 1:** AI inferred from indirect data (weight=1)
- **Tier 2:** User mentioned indirectly (weight=3)
- **Tier 3:** User stated directly (weight=9)
- **Tier 4:** User provided example (weight=27)
- **Tier 5:** User provided quantified example (weight=81)

**Bayesian-weighted ranking:**
- Multiple evidence pieces weighted by tier
- Regressed toward global average (μ=2.0) for low-confidence edges
- Handles contradictions (later evidence outweighs earlier)
- Accepts "I don't know" (confidence=0.0)

### 3. Natural Context Extraction

**"Sprinkle, don't survey" approach:**
- Extract business constraints naturally throughout conversation
- Only ask explicitly for missing critical factors before recommendations

**Critical factors (always needed):**
- Budget range
- Timeline urgency
- Visibility preference (quiet win vs showcase)

**Contextual factors (only if relevant):**
- Compliance requirements
- Vendor constraints
- Stakeholder pressure

### 4. LLM Semantic Inference for Recommendations

**Why not hardcoded mapping:**
- Combinatorial explosion makes rules infeasible
- Same bottleneck has different solutions based on context
- Example: "Team ⭐⭐" could mean knowledge gaps, SME bottleneck, or incentive issues

**LLM inference process:**
1. Build rich context bundle (output + edges + evidence + business constraints)
2. Reference structured catalogs (100+ pain points, 27 AI archetypes, 28 pilots)
3. LLM identifies pain points → maps to archetypes → recommends specific pilots
4. Output: JSON with pain points, archetypes, ranked pilots (with reasoning)

### 5. Feasibility Assessment

**Archetype-based prerequisites:**
- Data prerequisites (historical data, quality, infrastructure)
- Team prerequisites (domain expertise, technical skills, capacity)
- System prerequisites (API access, integration, deployment)
- Organizational prerequisites (change readiness, stakeholder support, compliance)

**Feasibility tiers:**
- **Tier 1 (Ready):** 0 weeks, €0, 80-90% success probability
- **Tier 2 (Minor gaps):** +4-6 weeks, +€10k-€20k, 60-80% success
- **Tier 3 (Major gaps):** +8-16 weeks, +€30k-€60k, 40-60% success
- **Tier 4 (Not feasible):** Deal-breakers present

### 6. Two-Tier Recommendations

**In-conversation:** 2-3 targeted pilots (fast decisions)  
**Downloadable report:** 5-10+ options with full analysis (stakeholder approval)

**Report structure (13-18 pages):**
1. Executive Summary
2. Top 3 Recommendations (expected impact, timeline, cost, prerequisites)
3. Alternative Solutions (4-7 additional options)
4. Prerequisite Deep Dive (gaps, cost-to-bridge)
5. Staged Approach (quick wins → comprehensive solutions)
6. Decision Matrix
7. Appendix

---

## Example Conversation Flow

**User:** "Our sales forecasts are always wrong"

**System:** "Sales Forecast - got it. How urgent is fixing this?"  
*[Moment 1: Extract timeline urgency]*

**User:** "Very urgent. Board is asking about forecast accuracy every week."

**System:** "What's the business impact of these errors?"  
*[Moment 2: Extract business impact]*

**User:** "We're missing revenue targets. Cost us €500k last quarter."

**System:** "Let's assess 4 areas. First, data quality from upstream sources?"

**User:** "2 stars. Customer data is scattered across multiple systems and outdated."

**System:** "Team skills and resources?"

**User:** "2 stars. Team is junior, mostly fresh grads. And we're understaffed."

**System:** "What budget range could you work with for improvements?"  
*[Moment 4: Extract budget]*

**User:** "Maybe €30k-€50k for a pilot."

**System:** "Process maturity?"

**User:** "1 star. No standard process, everyone does it their own way."

**System:** "CRM support for forecasting?"

**User:** "1 star. No forecasting tools, we export to Excel manually."

---

**System Analysis:**
```
Output: Sales Forecast
Current Quality: ⭐ (MIN of all edges)
Required Quality: ⭐⭐⭐⭐
Gap: 3 stars

Bottlenecks:
- Tool → Output: ⭐ (No forecasting tools, manual Excel)
- Process → Output: ⭐ (Ad-hoc, no standardization)
- People → Output: ⭐⭐ (Junior team, understaffed)
- Dependency → Output: ⭐⭐ (Scattered customer data)

Business Context:
- Budget: €30k-€50k
- Timeline: Urgent (board pressure)
- Impact: €500k/quarter revenue miss
```

**System Recommendations:**

**Option 1: AI Forecasting Copilot** ✅ Ready (Recommended)
- **What it does:** Real-time AI assistant for forecasting workflow
- **Expected impact:** ⭐ → ⭐⭐⭐⭐ (addresses Tool + People bottlenecks)
- **Timeline:** 8-12 weeks
- **Cost:** €30k-€50k (fits budget)
- **Prerequisites:** All met, ready to start
- **Feasibility:** High (80-90% success probability)

**Option 2: Process Automation + Data Pipeline** ⚠️ Minor Gaps
- **What it does:** Automate data collection, standardize process
- **Expected impact:** ⭐ → ⭐⭐⭐ (addresses Process + Dependency bottlenecks)
- **Timeline:** 12-16 weeks (+4 weeks for data cleanup)
- **Cost:** €40k-€60k (+€10k for data work, exceeds budget)
- **Prerequisites:** Need data cleanup first
- **Feasibility:** Medium-High (60-80% success probability)

**User:** "Option 1 sounds perfect. Can I get a detailed report for the VP?"

**System:** "Generating comprehensive assessment report... [Download: Assessment_Report_Sales_Forecast_2025-11-04.pdf]"

---

## Technical Architecture

### Technology Stack

**Backend:**
- **Language:** Python 3.11+
- **LLM:** Gemini 1.5 Flash via Vertex AI (streaming, 4x cheaper than Pro)
- **Graph:** NetworkX (in-memory graph operations)
- **Data:** Firestore (user data), Cloud Storage (static catalogs)

**Frontend:**
- **Framework:** Streamlit (conversational chat interface)
- **Streaming:** Async generators for real-time LLM responses
- **Auth:** Firebase Authentication (Google OAuth)

**Deployment:**
- **Platform:** Google Cloud Platform
- **Compute:** Cloud Run (scale-to-zero, session affinity)
- **Region:** us-central1 (Vertex AI availability)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Browser)                           │
│  Chat Interface + Knowledge Tree + Technical Log            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT APP (Cloud Run)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Conversation Orchestrator                             │ │
│  │    ├─ Discovery Engine (Output identification)         │ │
│  │    ├─ Assessment Engine (Edge rating + MIN calc)       │ │
│  │    ├─ Context Extractor (Business constraints)         │ │
│  │    ├─ Recommendation Engine (LLM semantic inference)   │ │
│  │    └─ Report Generator (Comprehensive PDF)             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Vertex AI   │ │  Firestore   │ │   Cloud      │ │  Firebase    │
│  (Gemini)    │ │  (User Data) │ │   Storage    │ │    Auth      │
│              │ │              │ │  (Catalogs)  │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### Data Model

**Firestore Schema:**
```
/users/{user_id}/
  nodes/
    outputs/{output_id}
      - output_name, function, description
      - incoming_edges: [edge_id, ...]
      - calculated_score: 2.5  # Cached MIN()
      - calculated_confidence: 0.75
    
    tools/{tool_id}
      - tool_name, tool_type, description
      - outgoing_edges: [edge_id, ...]
    
    processes/{process_id}
      - process_name, maturity_level
      - outgoing_edges: [edge_id, ...]
    
    people/{people_id}
      - archetype_name, description
      - outgoing_edges: [edge_id, ...]
  
  edges/{edge_id}
    - source_id, target_id, edge_name
    - current_score: 1-5 stars
    - current_confidence: 0.0-1.0
    - evidence: [
        {statement, tier, timestamp, conversation_id}
      ]
  
  conversations/{conversation_id}
    - messages: [{role, content, timestamp}]
    - extracted_context: {budget, timeline, visibility, ...}
    - status: "in_progress" | "completed"
```

**Hybrid Storage:**
- Firestore = source of truth (persistence)
- NetworkX = fast graph operations (BFS, DFS, MIN calculation)
- Load relevant subgraph on session start
- Write back to Firestore on changes

### Cost Optimization

**GCP Free Tier Coverage:**
- Cloud Run: 2M requests/month, 360K GB-seconds
- Firestore: 1GB storage, 50K reads/day, 20K writes/day
- Cloud Storage: 5GB storage
- Vertex AI: $300 credit for new accounts

**Estimated Monthly Cost (after free tier):**
- Cloud Run: ~$5-10 (low traffic)
- Firestore: ~$0-5 (< 1GB data)
- Vertex AI: ~$10-20 (Gemini Flash, ~100 conversations/month)
- **Total: ~$15-35/month**

**Scale-to-zero:** Cloud Run scales to 0 instances when idle (cost = $0)

---

## Implementation Timeline

**Total Duration:** 10 weeks (2.5 months)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Infrastructure | Weeks 1-2 | GCP setup, basic chat |
| 2. Discovery & Assessment | Weeks 3-4 | Output ID, edge rating, MIN calc |
| 3. Context Extraction | Week 5 | Business context extraction |
| 4. Recommendations | Weeks 6-7 | LLM inference, feasibility |
| 5. Report Generation | Week 8 | PDF report |
| 6. Polish & Testing | Weeks 9-10 | Demo-ready |

---

## Status

**Functional Specification:** ✅ Complete - All interaction patterns, models, and algorithms defined  
**Technical Specification:** ✅ Complete - Implementation and deployment plan documented  
**Implementation:** 📋 Ready to begin - See [Implementation Plan](docs/2_technical_spec/IMPLEMENTATION_DEPLOYMENT_PLAN.md)  
**Deployment:** 📋 Planned - Cloud Run serverless deployment with scale-to-zero cost optimization
