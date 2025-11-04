# Alternative B: Solution Recommendation Strategy

**Status:** Design Decision  
**Date:** 2025-11-04

---

## Core Decision: LLM-Based Semantic Inference

**Problem:** Cannot hardcode mappings from (Output + Edge Type + Score + Context) → AI Pilots due to combinatorial explosion.

**Solution:** Use LLM semantic inference with rich context and structured catalogs.

---

## Why Hardcoded Mapping Fails

### The Combinatorial Explosion

**Search space dimensions:**
- 46+ outputs (and growing)
- 4 edge types (People, Tool, Process, Dependency)
- 5 score levels (⭐ to ⭐⭐⭐⭐⭐)
- 100+ pain points across 12 categories
- 27 AI archetypes
- Business decision dimensions (cost, timeline, competitive pressure, etc.)
- Team archetypes (junior, senior, understaffed, etc.)
- System types (CRM, ERP, spreadsheet, custom, etc.)
- Process maturity levels (ad-hoc, documented, standardized, optimized)

**Total permutations: Astronomical (10,000+ unique scenarios)**

### The Interpretation Problem

**Same bottleneck, different pain points:**

**Example: "Team → Sales Forecast = ⭐⭐"**

Could mean:
1. **Knowledge gaps** - Junior team, no training materials, no expert to learn from
2. **Skill availability** - SME bottleneck, overloaded reviewers, handoff delays
3. **Incentive misalignment** - KPIs reward speed over accuracy, no recognition for quality
4. **Training gaps** - No formal forecasting training, thin onboarding
5. **Workforce impact** - Role fear, skill gap unaddressed, talent attrition

**Each leads to different solutions:**
1. Knowledge gaps → AI Copilot, Knowledge Base + RAG
2. SME bottleneck → Automation, Augmentation (reduce dependency on experts)
3. Incentive issues → Process Intelligence (not AI at all - organizational fix)
4. Training gaps → Interactive Training System, Structured Learning
5. Workforce impact → Change Management, Reskilling Programs (not AI)

**The pain point IS the semantic bridge between problem and solution.**

---

## LLM Semantic Inference Architecture

### Input: Rich Context Bundle

**Structured context passed to LLM:**

```
Output Context:
- output_id: "sales_forecast"
- output_name: "Sales Forecast"
- function: "Sales"
- quality_metric: "accuracy"
- current_score: ⭐⭐ (20-30% error rate)
- required_score: ⭐⭐⭐⭐ (5-10% error rate)
- gap: 2 stars

Bottleneck Edges:
- Edge 1: People("Sales Ops - Junior") → Output
  - score: ⭐⭐
  - evidence: ["Team is junior, mostly fresh grads", "No one to learn from"]
  - confidence: 0.8
  
- Edge 2: Tool("Salesforce CRM") → Output
  - score: ⭐
  - evidence: ["No forecasting tools", "Manual Excel export"]
  - confidence: 0.9

- Edge 3: Process("Forecasting Process") → Output
  - score: ⭐
  - evidence: ["Ad-hoc", "No standardization", "Everyone does it differently"]
  - confidence: 0.7

- Edge 4: Dependency("Customer Data from Marketing") → Output
  - score: ⭐⭐
  - evidence: ["Scattered across systems", "Outdated"]
  - confidence: 0.6

Business Context:
- competitive_pressure: "high"
- cost_sensitivity: "medium"
- timeline_urgency: "medium"
- visibility_preference: "quiet win"

Team Archetype:
- seniority: "junior"
- size: "understaffed"
- motivation: "learning-oriented"
```

### Reference Catalogs

**Pain Point Catalog** (`pain_point_mapping.json`):
- 100+ pain points across 12 categories
- Used as semantic reference, not lookup table

**AI Archetype Catalog** (`ai_archetypes.json`):
- 27 AI/ML use case archetypes
- With concrete examples and typical applications

**Pilot Catalog** (`pilot_catalog.json`):
- 28 specific pilot examples
- With timelines, costs, expected impacts

### LLM Task: Structured Inference

**Prompt structure:**

```
You are an AI pilot recommendation engine. Given the context below, perform these steps:

1. IDENTIFY PAIN POINTS (2-4 most likely)
   - Analyze bottleneck edges and evidence
   - Reference pain_point_catalog for semantic matching
   - Consider business context and constraints
   - Output: List of pain points with confidence scores

2. MAP TO AI ARCHETYPES (2-3 most relevant)
   - For each pain point, identify applicable AI archetypes
   - Reference ai_archetype_catalog
   - Explain reasoning for each mapping
   - Output: List of archetypes with rationale

3. RECOMMEND SPECIFIC PILOTS (2-3 concrete options)
   - Match archetypes to specific pilots from pilot_catalog
   - Consider business constraints (cost, timeline, visibility)
   - Rank by expected impact on bottleneck
   - Output: Structured pilot recommendations

CONTEXT:
{rich_context_bundle}

CATALOGS:
{pain_point_catalog}
{ai_archetype_catalog}
{pilot_catalog}

OUTPUT FORMAT (JSON):
{
  "pain_points": [
    {
      "pain_point": "Knowledge gaps",
      "category": "Missing Ownership, Misaligned Incentives & Skills",
      "confidence": 0.9,
      "evidence": ["Junior team", "No one to learn from"],
      "affected_edges": ["People → Output"]
    }
  ],
  "ai_archetypes": [
    {
      "archetype": "Conversational AI / Copilot",
      "rationale": "Addresses knowledge gaps by providing real-time guidance",
      "addresses_pain_points": ["Knowledge gaps"],
      "confidence": 0.85
    }
  ],
  "pilot_recommendations": [
    {
      "pilot_name": "AI Forecasting Copilot",
      "pilot_id": "copilot_forecasting",
      "category": "Team Execution",
      "description": "Real-time AI assistant for forecasting workflow",
      "expected_impact": "⭐⭐ → ⭐⭐⭐⭐ (2 star improvement)",
      "timeline": "8-12 weeks",
      "cost": "€30k-€50k",
      "prerequisites": ["Team willing to adopt", "CRM API access"],
      "addresses_bottlenecks": ["People → Output", "Process → Output"],
      "fit_score": 0.9,
      "rationale": "Best fit for knowledge gap + process immaturity. Provides guidance without requiring process redesign."
    }
  ]
}
```

### Output: Structured Recommendations

**LLM returns JSON with:**
- Identified pain points (with confidence)
- Mapped AI archetypes (with rationale)
- Ranked pilot recommendations (with fit scores)

**System presents to user:**
- Natural language summary
- 2-3 pilot options with trade-offs
- Expected impact per pilot
- User selects based on priorities

---

## Why This Approach Works

### 1. Handles Nuance
**LLM can weigh multiple signals:**
- "Junior team" + "No one to learn from" → Knowledge gaps (not just skill availability)
- "Ad-hoc process" + "Everyone does it differently" → Process immaturity (not just lack of documentation)
- "High competitive pressure" + "Cost sensitive" → Prioritize quick wins over comprehensive solutions

### 2. Context-Aware
**Same bottleneck, different solutions based on context:**
- Junior team + Complex tool → AI Copilot (guidance)
- Junior team + Simple tool → Training System (structured learning)
- Junior team + High turnover → Knowledge Base (capture tribal knowledge)

### 3. Explainable
**LLM articulates reasoning:**
- "Given junior team + no expert + complex forecasting, likely pain point is knowledge transfer"
- "AI Copilot addresses this by providing real-time guidance without requiring expert availability"
- "Expected impact: Team can perform at ⭐⭐⭐⭐ level with AI assistance"

### 4. Flexible
**Easy to extend:**
- New pain points → Add to catalog, LLM adapts
- New AI archetypes → Add to catalog, LLM considers
- New pilots → Add to catalog, LLM recommends
- No code changes, just prompt/catalog updates

### 5. Handles Multi-Dimensional Constraints
**Business context influences recommendations:**
- Cost sensitive → Prioritize lower-cost pilots
- Timeline urgent → Prioritize quick wins
- Visibility preference → Prioritize quiet wins vs showcase projects
- Competitive pressure → Prioritize differentiation vs parity

---

## Implementation Requirements

### 1. Structured Context Builder
**Module:** `engines/context_builder.py`

**Responsibilities:**
- Aggregate all edges for output
- Calculate MIN() and identify bottlenecks
- Extract evidence from all edges
- Load business context from conversation
- Format as structured JSON

### 2. Catalog Loaders
**Module:** `core/catalog_loader.py`

**Responsibilities:**
- Load pain_point_mapping.json
- Load ai_archetypes.json
- Load pilot_catalog.json
- Format for LLM prompt

### 3. LLM Inference Engine
**Module:** `engines/recommendation_engine.py`

**Responsibilities:**
- Build recommendation prompt
- Call LLM with structured context + catalogs
- Parse JSON response
- Validate output structure
- Handle LLM errors/hallucinations

### 4. Recommendation Presenter
**Module:** `utils/recommendation_formatter.py`

**Responsibilities:**
- Convert JSON to natural language
- Format pilot options for user
- Explain trade-offs
- Handle user selection

---

## Quality Assurance

### 1. Validation Rules
**Prevent hallucinations:**
- All recommended pilots must exist in pilot_catalog
- All pain points must reference pain_point_mapping categories
- All AI archetypes must exist in ai_archetypes catalog
- Confidence scores must be 0.0-1.0
- Fit scores must be 0.0-1.0

### 2. Fallback Strategies
**If LLM fails:**
- Use simple heuristic: Bottleneck type → Pilot category
  - People bottleneck → Team Execution pilots
  - Tool bottleneck → System Capabilities pilots
  - Process bottleneck → Process Maturity pilots
  - Dependency bottleneck → Data Quality pilots
- Show warning: "Using simplified recommendations"

### 3. User Feedback Loop
**Improve over time:**
- Track which recommendations user selects
- Track which pain points user validates
- Use feedback to refine prompts
- Build few-shot examples from successful recommendations

---

## Trade-offs

### Advantages
✅ Handles combinatorial complexity  
✅ Context-aware and nuanced  
✅ Explainable reasoning  
✅ Easy to extend (no code changes)  
✅ Adapts to new scenarios  

### Disadvantages
❌ LLM dependency (latency, cost, errors)  
❌ Non-deterministic (same input may yield different outputs)  
❌ Requires validation to prevent hallucinations  
❌ Harder to debug than hardcoded rules  
❌ Prompt engineering required  

### Mitigation
- Cache LLM responses for identical contexts
- Use structured output format to reduce variability
- Implement strict validation rules
- Provide fallback heuristics
- Log all LLM calls for debugging

---

## Alternative Approaches Considered

### Alternative 1: Hardcoded Mapping Table
**Approach:** Create lookup table from (Edge Type + Score) → Pilots

**Rejected because:**
- Cannot handle nuance (junior team ≠ SME bottleneck)
- Ignores context (cost, timeline, business constraints)
- Maintenance nightmare (10,000+ permutations)
- No explanation/reasoning

### Alternative 2: Rule-Based Expert System
**Approach:** IF-THEN rules for pain point inference

**Rejected because:**
- Brittle (breaks on edge cases)
- Cannot handle multi-dimensional constraints
- Hard to maintain (rule conflicts)
- No learning/improvement over time

### Alternative 3: Hybrid (Rules + LLM)
**Approach:** Use rules for simple cases, LLM for complex

**Rejected because:**
- Complexity of maintaining two systems
- Unclear boundary between "simple" and "complex"
- Rules still suffer from combinatorial explosion
- Better to use LLM with fallback heuristics

---

## Success Metrics

### Recommendation Quality
- **Precision:** % of recommended pilots that user considers relevant
- **User selection rate:** % of recommendations that user selects
- **Pain point accuracy:** % of identified pain points that user validates

### System Performance
- **Latency:** < 5 seconds for recommendation generation
- **Cost:** < €0.10 per recommendation (LLM API costs)
- **Reliability:** > 95% successful LLM calls (with fallback)

### User Experience
- **Clarity:** User understands reasoning (measured via feedback)
- **Trust:** User trusts recommendations (measured via adoption rate)
- **Satisfaction:** User finds recommendations helpful (measured via survey)

---

## Conclusion

**LLM semantic inference is the professional approach for Alternative B's problem-to-solution jump.**

The combinatorial complexity of the problem space makes hardcoded mapping infeasible. LLM-based inference provides the nuance, context-awareness, and flexibility required to bridge the gap from bottleneck edges to targeted pilot recommendations.

**Key insight:** Pain points are the semantic bridge. The LLM's role is to infer pain points from context, then map them to solutions using structured catalogs as reference.

**Implementation priority:** HIGH - This is core to Alternative B's value proposition.
