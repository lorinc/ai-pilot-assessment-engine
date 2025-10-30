# Scoped Factor Model Evolution - Design Iterations

**Date:** 2024-10-30  
**Type:** Architecture Refinement  
**Impact:** Major - Affects data model, UX, and implementation approach

---

## Summary

Evolved from organization-wide factor assessments to a **scoped factor model** that maintains organizational truth while enabling domain/system-specific assessments. This solves the abstraction gap where "sales data quality is poor" was incorrectly generalized to "all organizational data is poor."

---

## Iteration 1: Organization-Wide Factors (Initial Approach)

### Design
```
Factor: data_quality = 40 (organization-wide)
Storage: /users/{user_id}/factors/{factor_id}
```

### Problem Identified
**Abstraction Gap:** User says "our sales reports are unreliable" → System infers "data_quality = 40 organization-wide" → System concludes "cannot do time series analysis on ANY data."

**Reality:** Sales reports unreliable ≠ All data unreliable. Manufacturing sensor data might be pristine (85%), finance data audit-ready (90%), HR data well-governed (75%).

**Why We Iterated:** Organization-wide factors cannot capture domain/system-specific reality. Wild and inaccurate generalizations would undermine trust.

---

## Iteration 2: Project-Scoped Contexts

### Design
```
Context: "sales_forecasting_pilot"
Factors assessed within context: data_quality = 40 (for this project only)
Storage: /users/{user_id}/contexts/{context_id}/factors/{factor_id}
```

### Rationale
Scope factors to project discussions to avoid over-generalization. Each project evaluation creates its own context with isolated factor assessments.

### Problem Identified
**Cross-Project Isolation:** User discusses sales forecasting, mentions "Salesforce CRM data is incomplete" → Factor stored in sales_forecasting context only → Later, user asks about CRM data quality improvement project → System has no memory of the Salesforce issue.

**Philosophical Flaw:** Organizational factors ARE organizational facts, independent of which project triggered their discovery. "Salesforce CRM data quality = 30%" is true whether discovered during forecasting discussion, segmentation discussion, or data quality discussion.

**Why We Iterated:** Project-scoping breaks cross-project knowledge reuse. The same organizational fact should inform ALL relevant projects.

---

## Iteration 3: Faceted Factors (Intermediate Approach)

### Design
```
Factor: data_quality
Facets: {domain: "sales", system: "salesforce_crm", data_type: null, team: null}
Value: 30
```

### Rationale
Factors have multiple dimensions (facets) that can be specified or left generic. System reasons about factor applicability to projects through facet matching.

### Strengths
- ✅ Organizational facts independent of discovery context
- ✅ Cross-project reuse (Salesforce assessment applies to any Salesforce-using project)
- ✅ Flexible granularity (can specify domain, system, or both)

### Problem Identified
**Single Instance Per Facet Combination:** Can only have ONE assessment for each unique facet combination. Cannot maintain both "sales department data quality = 45%" AND "Salesforce CRM data quality = 30%" simultaneously because they have different facet values.

**Missing Hierarchy:** No way to represent that Salesforce (specific) refines sales department (generic). No inheritance when specific assessment unavailable.

**Why We Iterated:** Need to support multiple assessments at different granularity levels with explicit relationships between them.

---

## Iteration 4: Scoped Factor Instances (Final Design)

### Design
```
Factor Definition: data_quality (template)

Instance 1:
  scope: {domain: "sales", system: null}
  value: 45
  refined_by: [instance_2, instance_3]

Instance 2:
  scope: {domain: "sales", system: "salesforce_crm"}
  value: 30
  refines: instance_1

Instance 3:
  scope: {domain: "sales", system: "spreadsheets"}
  value: 25
  refines: instance_1
```

### Key Innovations

**1. Multiple Instances Per Factor**
- Same factor can have multiple assessments at different scopes
- Generic "sales department" AND specific "Salesforce CRM" coexist
- Explicit relationships: specific instances refine generic ones

**2. Scope Hierarchy & Inheritance**
```
Level 1: Organization-wide {domain: null, system: null}
Level 2: Domain-specific {domain: "sales", system: null}
Level 3: System-specific {domain: "sales", system: "salesforce_crm"}
Level 4: Team-specific {domain: "sales", system: "salesforce_crm", team: "enterprise_sales"}
```

**3. Intelligent Scope Matching**
- Query: "data_quality for Salesforce CRM" → Returns exact match (30%)
- Query: "data_quality for data warehouse" → Returns generic sales (45%) with note
- Query: "data_quality for manufacturing" → Returns none, asks to assess

**4. Intelligent Discovery Patterns**

**Pattern A: Generic → Specific Refinement**
```
User: "Sales data has quality issues"
→ Create generic: {domain: "sales"} = 45

System: "Is this across all sales systems, or specific tools?"
User: "Mainly Salesforce"
→ Create specific: {domain: "sales", system: "salesforce_crm"} = 30
→ Link: specific refines generic
```

**Pattern B: Specific → Generic Inference**
```
User: "Salesforce data is incomplete"
→ Create specific: {domain: "sales", system: "salesforce_crm"} = 35

System: "Do other sales systems have similar issues?"
User: "Just Salesforce, data warehouse is fine"
→ Create another specific: {domain: "sales", system: "data_warehouse"} = 75
→ Do NOT create generic (user said issue is isolated)
```

**Pattern C: Multiple Specifics → Generic Synthesis**
```
User: "Salesforce data is incomplete"
→ Create: {domain: "sales", system: "salesforce_crm"} = 35

User: "Sales spreadsheets are a mess"
→ Create: {domain: "sales", system: "spreadsheets"} = 25

System detects pattern:
→ Create generic via synthesis: {domain: "sales"} = 30 (weighted average)
→ Link: generic synthesized_from [salesforce, spreadsheets]

System: "I'm noticing sales data quality is low across multiple systems. 
This suggests a broader issue - maybe lack of data governance?"
```

**5. Clarifying Questions**
- "Is this across all systems or specific tools?" (narrow from generic)
- "Do other systems have similar issues?" (generalize from specific)
- "Which data domain - sales, finance, operations?" (identify domain)
- "Earlier you said sales data is good, now you say Salesforce is bad. Is Salesforce the exception?" (resolve contradictions)

---

## Key Benefits of Final Design

### 1. Organizational Truth
Factors describe organizational reality, not project-specific assessments. "Salesforce CRM data quality = 30%" is true regardless of which project discussion discovered it.

### 2. Cross-Project Reuse
```
[Discussion 1: Sales Forecasting]
User: "Salesforce data is incomplete"
→ Store: data_quality {domain: "sales", system: "salesforce_crm"} = 30

[Discussion 2: Days Later - CRM Data Quality]
User: "What about improving CRM data quality?"
System: "We already know Salesforce CRM quality is ~30% (you mentioned 
incomplete data during sales forecasting discussion). Improving this 
would unblock sales forecasting AND enable customer segmentation."
```

### 3. Honest About Scope
- "Salesforce CRM quality is 30% (high confidence)"
- "Sales department generally around 45% (moderate confidence)"
- "Don't have info about data warehouse yet - want to discuss?"

### 4. AI Suggests Itself
```
User: "Can we do sales forecasting?"
System: "Salesforce data quality too low (30%, need 60%).

BUT - AI can help improve Salesforce data quality:
- Automated duplicate detection
- Missing value prediction
- Data validation

Want to use AI to fix the data quality problem first?"
```

Graph traversal: Project requires data_quality → Gap detected → Search for AI_ARCHETYPE with IMPROVES edge to data_quality → Suggest data quality improvement project.

---

## Implementation Impact

### Data Schema Changes
**Before:** `/users/{user_id}/factors/{factor_id}`  
**After:** `/users/{user_id}/factor_instances/{instance_id}` with scope fields

### New Components
- Scope matching algorithm (find best applicable instance)
- Clarifying question generator (KG-based)
- Scope registry (domains, systems, teams)
- Instance relationship tracking (refines, refined_by, synthesized_from)

### Epic 1 Scope Adjustment
- Single factor: `data_quality`
- 2-3 scope levels: generic, domain-specific, system-specific
- 2 clarifying question patterns: narrow and generalize
- UI: Tree view showing scoped instances

---

## Next Steps

1. Update architecture documents (architecture_summary.md, gcp_data_schemas.md, etc.)
2. Create organizational_factors.json with scope schemas
3. Update graph builder to load scoped factors
4. Implement scope matching logic with tests
5. Update Epic 1 specification with scoped factor model
6. Design KG-based question inference for unknown systems

**Estimated Time:** 17-21 hours (2-3 days)

---

## Decision Rationale

**Why scoped instances over alternatives:**
- ✅ Maintains organizational truth (not project-specific)
- ✅ Supports multiple granularity levels simultaneously
- ✅ Enables cross-project knowledge reuse
- ✅ Honest about uncertainty and scope limitations
- ✅ Scales to unknown systems/domains via intelligent questions
- ✅ Enables "AI suggests itself" pattern via graph traversal

**Trade-offs accepted:**
- More complex data model (multiple instances vs. single value)
- Requires scope matching logic (not simple lookup)
- Need intelligent clarifying questions (not just accept statements)

**Value delivered:**
- Accurate, trustworthy assessments (no wild generalizations)
- Actionable insights (know exactly what to fix)
- Cross-project intelligence (learn once, apply everywhere)
- Exploratory UX (system asks smart questions, learns organizational structure)

---

**Changelog Version:** 1.0  
**Document Status:** Complete
