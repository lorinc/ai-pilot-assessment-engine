# Interim Data Files - Repurposing Plan

## Overview

The `interim_data_files/` directory contains **high-quality taxonomies** from the previous factor-centric model. Much of this content can be repurposed for the new output-centric model.

## Files Analysis

### 1. ✅ **business_core_function_taxonomy.json** (8.9 KB)
**Status:** HIGHLY VALUABLE - Expand into function templates

**Content:**
- 6 categories covering 20+ business functions
- Each function has detailed "tools_and_processes" lists
- Comprehensive coverage: R&D, Manufacturing, Supply Chain, Sales, Marketing, Customer Success, Finance, HR, IT, etc.

**Repurposing Strategy:**
- **Use as foundation for new function templates**
- Current templates cover: Sales, Finance, Operations (3 functions)
- This file provides 17 MORE functions to create templates for:
  - **Core Value Creation:** R&D, Manufacturing, Supply Chain, Service Delivery
  - **Revenue & Growth:** Marketing, Customer Success, Partnerships
  - **Finance & Compliance:** Accounting, FP&A, Compliance, Procurement
  - **People & Culture:** HR, Payroll, Workplace Safety
  - **Strategy & Intelligence:** Corporate Strategy, Innovation, Knowledge Management
  - **Technology:** IT Operations, Data Engineering, Cybersecurity, Architecture

**Action Items:**
1. Create `organizational_templates/functions/marketing.json` using Marketing section
2. Create `organizational_templates/functions/customer_success.json`
3. Create `organizational_templates/functions/hr.json`
4. Create `organizational_templates/functions/manufacturing.json`
5. Create `organizational_templates/functions/supply_chain.json`
6. Create `organizational_templates/functions/it_operations.json`
7. etc. (17 total new function templates)

**Template Structure:**
```json
{
  "function": "Marketing",
  "description": "...",
  "typical_teams": [...],  // Infer from function name
  "typical_processes": [   // Extract from "tools_and_processes"
    {
      "name": "Campaign Execution & Optimization",
      "steps": [...],
      "outputs_by_step": {...}
    }
  ],
  "typical_systems": [...],  // Add based on function
  "common_outputs": [        // Create 4-6 outputs per function
    {
      "id": "campaign_performance_report",
      "name": "Campaign Performance Report",
      ...
    }
  ],
  "inference_triggers": {...}
}
```

---

### 2. ✅ **problem_taxonomy.json** (8.5 KB)
**Status:** EXTREMELY VALUABLE - Enrich output pain points

**Content:**
- 11 major problem categories
- 100+ specific pain points organized hierarchically
- Categories: Knowledge Systems, Process Gaps, Ownership Issues, Communication, Data Management, Tooling, Ops Reliability, Security, Performance, Measurement, Supply Chain, Strategic Alignment

**Repurposing Strategy:**
- **Enrich `common_pain_points` in output definitions**
- **Create pain point → output mapping**
- **Improve inference accuracy** by matching user statements to specific pain points

**Example Mapping:**

```json
// From problem_taxonomy.json
"Data Management Failures": {
  "Data quality": ["incompleteness", "inaccuracy", "untimeliness"]
}

// Maps to outputs in function templates
{
  "id": "sales_forecast",
  "common_pain_points": [
    "Forecasts are consistently inaccurate",  // ← Maps to "inaccuracy"
    "Data is incomplete",                      // ← Maps to "incompleteness"
    "Forecast arrives too late"                // ← Maps to "untimeliness"
  ]
}
```

**Action Items:**
1. Create `pain_point_mapping.json` that maps problem taxonomy to outputs
2. Enhance existing output definitions with more specific pain points
3. Add pain point categories to `inference_rules/output_discovery.json`

---

### 3. ✅ **AI_use_case_taxonomy.json** (17.5 KB)
**Status:** VALUABLE - Enhance pilot recommendations

**Content:**
- 20+ AI use case archetypes
- Each with: core task, analytical purpose, technical family, common models, example outputs
- Examples: Anomaly Detection, Content Analysis, Clustering, Regression, Classification, NLP, Recommendation Systems, etc.

**Repurposing Strategy:**
- **Enhance pilot type descriptions** with technical details
- **Add "AI archetype" field** to pilot types
- **Create technical feasibility checks** based on archetypes

**Example Enhancement:**

```json
// Current pilot_types.json
{
  "id": "ai_features",
  "name": "AI-Powered Features",
  "typical_use_cases": ["Predictive analytics", "Recommendation engines"]
}

// Enhanced with AI use case taxonomy
{
  "id": "ai_features",
  "name": "AI-Powered Features",
  "ai_archetypes": [
    {
      "archetype": "Regression & Forecasting",
      "use_case": "Predictive analytics (e.g., sales forecasting)",
      "technical_family": "Supervised Learning",
      "common_models": ["Linear Regression", "XGBoost", "LSTM"],
      "data_requirements": ["Historical time-series data", "Labeled outcomes"]
    },
    {
      "archetype": "Recommendation Systems",
      "use_case": "Next best action suggestions",
      "technical_family": "Collaborative Filtering / Content-Based",
      "common_models": ["Matrix Factorization", "Neural Collaborative Filtering"],
      "data_requirements": ["User-item interactions", "Item features"]
    }
  ]
}
```

**Action Items:**
1. Create `ai_archetypes.json` in `inference_rules/`
2. Link pilot types to relevant archetypes
3. Add technical feasibility checks to pilot recommendations

---

### 4. ✅ **automation_opportunity_taxonomy.json** (14.2 KB)
**Status:** VALUABLE - Expand pilot catalog

**Content:**
- 50+ automation use cases across 10 categories
- Each with: consolidated pain points, key AI archetypes
- Categories: Data Management, Financial, Customer-Facing, HR, Legal, Sales, Supply Chain, IT, Content, Strategic

**Repurposing Strategy:**
- **Create specific pilot project examples** from use cases
- **Enrich pilot types** with real-world examples
- **Add to output definitions** as improvement opportunities

**Example Usage:**

```json
// From automation_opportunity_taxonomy.json
{
  "use_case": "Financial Transaction Processing and Reconciliation",
  "consolidated_pain_points": "Automating high-volume manual GL account reconciliation...",
  "key_archetypes": ["Anomaly & Outlier Detection", "Classification", "Agentic Orchestration"]
}

// Add to finance.json outputs
{
  "id": "account_reconciliations",
  "typical_improvement_opportunities": {
    "system_capabilities": "AI-powered automated reconciliation using anomaly detection and classification to match transactions"
  },
  "pilot_examples": [
    {
      "name": "Automated GL Reconciliation",
      "description": "Use AI to automatically match transactions and flag exceptions",
      "ai_archetypes": ["Anomaly & Outlier Detection", "Classification"],
      "expected_impact": "Reduce reconciliation time by 70%"
    }
  ]
}
```

**Action Items:**
1. Extract 50+ specific pilot examples from automation opportunities
2. Add to relevant output definitions
3. Create `pilot_catalog/` directory with detailed pilot specs

---

### 5. ✅ **business_capability_taxonomy.json** (13.3 KB)
**Status:** VALUABLE - Create capability assessment framework

**Content:**
- 100+ organizational capabilities across 5 pillars
- Hierarchical structure: T1 Pillar → T2 Category → T3 Capabilities
- Pillars: Data Assets, Technical Infrastructure, People & Process, Governance, Business Context

**Repurposing Strategy:**
- **Use for component assessment** (Team, System, Process)
- **Create capability checklists** for pilot prerequisites
- **Add to component_scales.json** as detailed indicators

**Example Enhancement:**

```json
// From business_capability_taxonomy.json
"Data_Foundation_and_Feature_Engineering": {
  "T3_Capabilities": [
    "Data availability and provisioning capability",
    "Data quality assurance capability",
    "Labeled training data availability"
  ]
}

// Add to component_scales.json
{
  "component": "system_capabilities",
  "scale": {
    "4": {
      "indicators": [
        "Data availability: automated provisioning",
        "Data quality: automated assurance processes",
        "Training data: labeled datasets readily available"
      ]
    }
  }
}
```

**Action Items:**
1. Map capabilities to component scales
2. Create `capability_checklist.json` for pilot prerequisites
3. Add capability requirements to pilot types

---

### 6. ⚠️ **AI_dependency_taxonomy.json** (37.3 KB)
**Status:** PARTIALLY RELEVANT - Extract useful patterns

**Content:**
- Large taxonomy of AI project dependencies
- May contain prerequisite patterns

**Repurposing Strategy:**
- **Review for pilot prerequisites**
- **Extract dependency patterns**
- Lower priority - review after other files

---

### 7. ⚠️ **business_decision_dimension_taxonomy.json** (28.7 KB)
**Status:** REVIEW NEEDED

**Repurposing Strategy:**
- Review for decision-making patterns
- May inform ROI calculation logic
- Lower priority

---

### 8. ⚠️ **project_scope_taxonomy.json** (59.2 KB)
**Status:** REVIEW NEEDED - May contain valuable patterns

**Repurposing Strategy:**
- Review for project scoping patterns
- May inform pilot scoping logic
- Lower priority

---

## Immediate Action Plan

### Phase 1: Expand Function Coverage (High Priority)
**Goal:** Go from 3 functions to 20+ functions

1. **Create 17 new function templates** using `business_core_function_taxonomy.json`:
   - Marketing
   - Customer Success
   - HR
   - Manufacturing
   - Supply Chain
   - IT Operations
   - Data Engineering
   - Cybersecurity
   - Procurement
   - Compliance
   - R&D
   - Partnerships
   - Corporate Strategy
   - Innovation
   - Knowledge Management
   - Architecture
   - Workplace Safety

2. **For each function:**
   - Extract processes from "tools_and_processes"
   - Define 4-6 common outputs
   - Add typical systems
   - Create inference triggers

**Estimated Effort:** 2-3 days
**Impact:** Massive increase in system coverage

---

### Phase 2: Enrich Pain Points (High Priority)
**Goal:** Improve inference accuracy with detailed pain points

1. **Create `pain_point_mapping.json`:**
   - Map 100+ pain points from problem_taxonomy to outputs
   - Add pain point categories to inference rules

2. **Enhance existing outputs:**
   - Add more specific pain points from taxonomy
   - Link pain points to component bottlenecks

**Estimated Effort:** 1 day
**Impact:** Better output discovery from user statements

---

### Phase 3: Add Technical Depth (Medium Priority)
**Goal:** Enhance pilot recommendations with AI archetypes

1. **Create `ai_archetypes.json`:**
   - Extract 20+ archetypes from AI_use_case_taxonomy
   - Add technical details (models, data requirements)

2. **Link to pilot types:**
   - Add "ai_archetypes" field to each pilot type
   - Add technical feasibility checks

**Estimated Effort:** 1 day
**Impact:** More credible, technically-grounded recommendations

---

### Phase 4: Expand Pilot Catalog (Medium Priority)
**Goal:** Provide 50+ specific pilot examples

1. **Extract pilot examples from automation_opportunity_taxonomy:**
   - 50+ use cases with pain points and archetypes
   - Add to relevant output definitions

2. **Create `pilot_catalog/` directory:**
   - Detailed pilot specifications
   - Real-world examples

**Estimated Effort:** 1-2 days
**Impact:** Richer, more actionable recommendations

---

### Phase 5: Capability Assessment (Lower Priority)
**Goal:** Add detailed capability checklists

1. **Map capabilities to component scales**
2. **Create prerequisite checklists for pilots**

**Estimated Effort:** 1 day
**Impact:** More rigorous pilot feasibility assessment

---

## Summary

### High-Value Files (Immediate Use)
1. ✅ **business_core_function_taxonomy.json** → 17 new function templates
2. ✅ **problem_taxonomy.json** → Enhanced pain point matching
3. ✅ **AI_use_case_taxonomy.json** → Technical depth for pilots
4. ✅ **automation_opportunity_taxonomy.json** → 50+ pilot examples
5. ✅ **business_capability_taxonomy.json** → Capability assessment

### Total Potential
- **17 new functions** (from 3 to 20+)
- **100+ pain points** for better inference
- **20+ AI archetypes** for technical credibility
- **50+ pilot examples** for actionable recommendations
- **100+ capabilities** for assessment depth

### Recommended Priority
1. **Phase 1** (Expand Functions) - Highest ROI
2. **Phase 2** (Enrich Pain Points) - Improves core inference
3. **Phase 3** (Technical Depth) - Adds credibility
4. **Phase 4** (Pilot Catalog) - Adds value
5. **Phase 5** (Capabilities) - Nice to have

**Next Step:** Should I start with Phase 1 and create the first few new function templates (e.g., Marketing, Customer Success, HR)?
