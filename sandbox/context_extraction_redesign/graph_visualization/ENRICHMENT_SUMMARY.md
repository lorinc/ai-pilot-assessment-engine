# Graph Enrichment Summary: From Outputs to Root Causes

**Date:** November 7, 2025  
**Version:** 2.0 (Enriched)

---

## What Was Added

### Original Graph (v1.0)
- **15 nodes:** 3 actors, 5 tools, 4 artifacts, 3 activities
- **14 edges:** PERFORMS, PRODUCES, USES, DEPENDS_ON
- **Focus:** Outputs and their dependencies

### Enriched Graph (v2.0)
- **27 nodes** (+12): Added 8 processes + 4 organizational constraints
- **32 edges** (+18): Added ENABLES, DEGRADES, FORCES, CAUSES, INFLUENCES relationships
- **Focus:** Root causes affecting output quality

---

## Key Additions

### 1. Process Nodes (8 new)

These are the **activities that affect quality** but were missing from the original graph:

#### Data Integration Process
- **Maturity:** 0.2 (very immature)
- **Issues:** Manual, time-consuming, error-prone
- **Affected by:** Understaffing, no time for cleanup
- **Impact:** Directly degrades `create_forecasts` quality
- **AI Opportunity:** Automated data integration pipeline

#### Data Cleanup & Maintenance
- **Maturity:** 0.1 (essentially doesn't happen)
- **Issues:** Not done, no time, no resources, Excel never updated
- **Affected by:** Understaffing, time constraint
- **Impact:** Stale data in forecasts
- **AI Opportunity:** Automated data cleanup and deduplication

#### Salesforce Data Entry
- **Maturity:** 0.3 (poor)
- **Issues:** Inconsistent, delayed, low priority, weeks behind
- **Affected by:** Measured on deals not data, always in meetings
- **Impact:** Projections based on stale data
- **AI Opportunity:** Automated CRM data entry from emails/meetings

#### Manual Salesforce Export
- **Maturity:** 0.3 (poor)
- **Issues:** Every Monday only, sometimes delayed, manual copy-paste
- **Affected by:** No proper system, manual process
- **Impact:** 3-4 week delay in production data
- **AI Opportunity:** Automated Salesforce → Production integration

#### Gut Feel Adjustment Process
- **Maturity:** 0.2 (very inconsistent)
- **Issues:** 20-40% variance, no standard, different by manager
- **Affected by:** Trust issues with marketing data
- **Impact:** Adds noise to projections
- **AI Opportunity:** ML-based forecast adjustment recommendations

#### Safety Buffer Addition
- **Maturity:** 0.3 (undocumented)
- **Issues:** Undocumented, compounds errors, "just in case" mentality
- **Affected by:** No trust in upstream data
- **Impact:** Compounds upstream errors
- **AI Opportunity:** Data-driven safety stock optimization

#### Campaign-to-Order Traceability
- **Maturity:** 0.0 (doesn't exist)
- **Issues:** Connections lost, no tracking
- **Affected by:** No system support
- **Impact:** Can't identify root cause of errors
- **AI Opportunity:** End-to-end traceability system

#### Forecast Accuracy Feedback
- **Maturity:** 0.0 (doesn't exist)
- **Issues:** No feedback, can't learn from errors
- **Affected by:** No traceability
- **Impact:** No continuous improvement
- **AI Opportunity:** Automated forecast accuracy analysis

---

### 2. Organizational Constraint Nodes (4 new)

These are the **root causes** that degrade process quality:

#### Marketing Understaffing (Resource Constraint)
- **Quality:** 0.3
- **Issues:** Understaffed, no time for data cleanup
- **Degrades:** Data integration process, data cleanup process
- **Impact Chain:** → create_forecasts → campaign_forecasts (0.3)
- **AI Opportunity:** Automation frees up time

#### Sales Incentive Structure (Incentive Misalignment)
- **Quality:** 0.4
- **Issues:** Measured on deals not data quality
- **Degrades:** Salesforce data entry
- **Impact Chain:** → adjust_projections → pipeline_projections (0.4)
- **AI Opportunity:** Automated data entry removes burden

#### IT Budget Limitation (Budget Constraint)
- **Quality:** 0.2
- **Issues:** No budget for proper system, 6-month project not approved
- **Forces:** Manual export process
- **Impact Chain:** → generate_production_orders → production_forecasts (0.2)
- **AI Opportunity:** Low-cost cloud alternatives

#### Inter-Team Trust Deficit (Trust Deficit)
- **Quality:** 0.3
- **Issues:** Sales doesn't trust marketing, burned before
- **Causes:** Gut feel adjustment process
- **Impact Chain:** → adjust_projections → pipeline_projections (0.4)
- **AI Opportunity:** Transparent data quality metrics build trust

---

### 3. New Edge Types (5 new relationship types)

#### ENABLES
- **Meaning:** Process enables an activity
- **Example:** `data_integration_process` ENABLES `create_forecasts`
- **Interpretation:** Poor process quality directly degrades activity output

#### DEGRADES
- **Meaning:** Constraint degrades a process
- **Example:** `resource_constraint` DEGRADES `data_integration_process`
- **Interpretation:** Organizational constraint reduces process maturity

#### FORCES
- **Meaning:** Constraint forces a workaround
- **Example:** `budget_constraint` FORCES `manual_export_process`
- **Interpretation:** Lack of resources forces manual process

#### CAUSES
- **Meaning:** Constraint causes problematic behavior
- **Example:** `trust_deficit` CAUSES `gut_feel_adjustment`
- **Interpretation:** Organizational issue drives inconsistent process

#### INFLUENCES
- **Meaning:** Process influences another process
- **Example:** `gut_feel_adjustment` INFLUENCES `adjust_projections`
- **Interpretation:** Informal process affects formal process

---

## Impact on AI Pilot Recommendations

### Before Enrichment (v1.0)
**4 AI opportunities** based on output quality:
- Campaign forecasts → Data integration
- Pipeline projections → Process intelligence
- Pipeline projections → Automation
- Production forecasts → Intelligent features

**Problem:** Recommendations were generic, didn't explain **why** these solutions would work.

### After Enrichment (v2.0)
**7 AI opportunities** based on root cause analysis:

1. **Data Integration Process** (maturity: 0.2)
   - **Root cause:** Resource constraint (understaffing)
   - **AI solution:** Automated data integration pipeline
   - **Impact:** Frees up marketing team time, eliminates manual work

2. **Data Cleanup Process** (maturity: 0.1)
   - **Root cause:** Resource constraint (no time)
   - **AI solution:** Automated data cleanup
   - **Impact:** Removes need for manual cleanup, improves freshness

3. **Salesforce Data Entry** (maturity: 0.3)
   - **Root cause:** Incentive misalignment (measured on deals)
   - **AI solution:** Automated CRM data entry
   - **Impact:** Reduces burden, improves freshness

4. **Gut Feel Adjustment** (maturity: 0.2)
   - **Root cause:** Trust deficit (burned before)
   - **AI solution:** ML-based adjustment recommendations
   - **Impact:** Standardizes process, reduces variance, builds trust

5. **Manual Export Process** (maturity: 0.3)
   - **Root cause:** Budget constraint (no proper system)
   - **AI solution:** Automated integration
   - **Impact:** Eliminates 3-4 week delay

6. **Traceability Process** (maturity: 0.0)
   - **Root cause:** No system support
   - **AI solution:** End-to-end traceability
   - **Impact:** Enables feedback loop, stops finger pointing

7. **Feedback Loop Process** (maturity: 0.0)
   - **Root cause:** No traceability
   - **AI solution:** Automated forecast accuracy analysis
   - **Impact:** Enables continuous improvement

---

## Root Cause Chain Analysis

### Chain 1: Marketing Forecasts (Quality: 0.3)
```
Resource Constraint (understaffing)
  ↓ DEGRADES
Data Integration Process (0.2)
  ↓ ENABLES
Create Forecasts (0.4)
  ↓ PRODUCES
Campaign Forecasts (0.3)
```

**Insight:** Understaffing forces poor data integration, which directly degrades forecast quality.

**AI Solution:** Automated data integration frees up time, breaks the constraint.

---

### Chain 2: Sales Projections (Quality: 0.4)
```
Incentive Misalignment (measured on deals)
  ↓ DEGRADES
Salesforce Data Entry (0.3)
  ↓ ENABLES
Adjust Projections (0.3)
  ↓ PRODUCES
Pipeline Projections (0.4)

Trust Deficit (burned before)
  ↓ CAUSES
Gut Feel Adjustment (0.2)
  ↓ INFLUENCES
Adjust Projections (0.3)
```

**Insight:** Two root causes - incentive misalignment causes poor data entry, trust deficit causes inconsistent adjustments.

**AI Solutions:** 
- Automated data entry removes burden (addresses incentive issue)
- ML-based adjustments build trust (addresses trust issue)

---

### Chain 3: Production Forecasts (Quality: 0.2)
```
Budget Constraint (no proper system)
  ↓ FORCES
Manual Export Process (0.3)
  ↓ ENABLES
Generate Production Orders (0.3)
  ↓ PRODUCES
Production Forecasts (0.2)
```

**Insight:** Budget constraint forces manual process, which adds 3-4 week delay.

**AI Solution:** Low-cost cloud alternative breaks budget constraint.

---

## Visualization Improvements

### Node Types
- **Original:** 4 types (Actor, Artifact, Tool, Activity)
- **Enriched:** 4 types (same, but Activity now includes processes)

### Edge Types
- **Original:** 4 types (PERFORMS, PRODUCES, USES, DEPENDS_ON)
- **Enriched:** 9 types (added ENABLES, DEGRADES, FORCES, CAUSES, INFLUENCES)

### Color Coding
- **Processes:** Same as activities (green) but with lower maturity scores
- **Constraints:** New artifact type (organizational domain)
- **Degradation edges:** Red/orange to show negative impact

---

## Key Learnings

### What Was Missing in v1.0
1. **Processes that affect quality** - Data integration, data cleanup, data entry
2. **Organizational constraints** - Understaffing, incentive misalignment, budget
3. **Causal relationships** - Why processes are poor (DEGRADES, FORCES, CAUSES)
4. **Root cause traceability** - From constraint → process → activity → output

### What v2.0 Enables
1. **Root cause analysis** - Trace quality issues to organizational constraints
2. **Targeted AI recommendations** - Address specific process gaps
3. **Impact prediction** - Understand how fixing one constraint helps multiple outputs
4. **Investment justification** - Show ROI of AI pilots (e.g., "frees up marketing time")

### Why This Matters for AI Pilots
- **Before:** "You need data integration" (generic)
- **After:** "Understaffing prevents data cleanup, automated pipeline frees up 10 hours/week" (specific, measurable)

---

## Test with Enriched Graph

### Load the enriched graph in the app:
1. Open http://localhost:8502
2. Select "example_cascading_failures_graph_enriched.json"
3. Observe:
   - 27 nodes (vs 15 before)
   - 32 edges (vs 14 before)
   - New process nodes (green, low maturity scores)
   - New constraint nodes (organizational artifacts)
   - New edge types showing degradation

### Explore root causes:
1. Click on "Data Integration Process" node
2. See: maturity=0.2, affected by "resource_constraint"
3. Follow edge to "create_forecasts"
4. See how poor process degrades forecast quality

### Verify AI opportunities:
1. Scroll to "🤖 AI Pilot Opportunities" section
2. See 7 opportunities (vs 4 before)
3. Each shows: target output, root cause, constraint, specific recommendations
4. Recommendations now explain **why** they work (e.g., "frees up time")

---

## Next Steps

1. **Validate enrichment** - Does this match the user story?
2. **Test visualization** - Are processes and constraints clear?
3. **Refine AI recommendations** - Are they specific enough?
4. **Iterate** - Add more processes/constraints as needed

**Goal:** Every AI pilot recommendation should trace back to a specific organizational constraint that it addresses.
