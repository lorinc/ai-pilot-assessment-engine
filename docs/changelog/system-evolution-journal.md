# Scoped Factor Model Evolution - Design Iterations

**Date:** 2024-10-30  
**Type:** Architecture Refinement  
**Impact:** Major - Affects data model, UX, and implementation approach

---

## Summary

Evolved through 5 major iterations from organization-wide factor assessments to an **output-centric model** that directly links every assessment to AI solution recommendations.

**The Journey:**
1. **Organization-Wide Factors** → Wild generalizations, no specificity
2. **Project-Scoped Contexts** → Cross-project isolation, knowledge loss
3. **Faceted Factors** → Single instance limitation, no hierarchy
4. **Scoped Factor Instances** → Organizational truth + specificity, but factors still isolated
5. **Output-Centric Model** → **BREAKTHROUGH: Direct path from assessment to AI solution recommendations via KG inference**

**The Critical Innovation (Iteration 5):**
Factors are no longer abstract capabilities assessed in isolation. Every factor is now tied to a specific output (Output + Team + Process + System), decomposed into 4 components, and automatically mapped to AI solution categories through simple knowledge graph traversal. This makes recommending Data Engineering / ML / Advanced AI solutions trivial.

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

## Next Steps (Updated 2025-11-01)

### Completed Today:
1. ✅ Updated all architecture documents for output-centric model
2. ✅ Created `output_centric_factor_model_exploration.md` (v0.3)
3. ✅ Updated 8 core documentation files to 1-5 star system
4. ✅ Defined scope constraints (locked)
5. ✅ Documented KG inference path: Root Cause → AI Solution Category

### Remaining:
1. Create output-centric factor schemas (Output + Team + Process + System)
2. Implement 4-component decomposition (Dependency/Execution/Process/System)
3. Implement MIN() calculation logic
4. Build KG edges: Root Cause Type → AI Solution Category
5. Update Epic 1 specification with output-centric model
6. Implement output dependency graph with loop detection

**Estimated Time:** 20-25 hours (3-4 days)

---

## Decision Rationale (Evolution Summary)

**Iteration 4 (Scoped Instances):**
- ✅ Maintains organizational truth (not project-specific)
- ✅ Supports multiple granularity levels simultaneously
- ✅ Enables cross-project knowledge reuse
- ✅ Honest about uncertainty and scope limitations
- ❌ But factors still isolated - no path to AI solution recommendations

**Iteration 5 (Output-Centric):**
- ✅ All benefits of Iteration 4, PLUS:
- ✅ **Direct link from assessment to AI solution recommendations**
- ✅ **KG-supported inference makes recommendations automatic**
- ✅ Output-centric = users understand what's being assessed
- ✅ Component decomposition identifies root causes
- ✅ Root cause type maps to AI solution category
- ✅ "AI suggests itself" pattern now trivial via KG traversal

**Trade-offs accepted:**
- More structured model (Output + Team + Process + System context)
- 4-component decomposition required
- MIN() calculation (but simpler than weighted averages)

**Value delivered:**
- **Automatic AI solution recommendations** (the breakthrough)
- Accurate, trustworthy assessments (no wild generalizations)
- Actionable insights (know exactly what to fix AND how to fix it)
- Cross-project intelligence (learn once, apply everywhere)
- Clear improvement path (output → bottleneck → AI solution)

---

---

## Iteration 5: Output-Centric Model (Final Design)

### Design
```
Factor: Capability to deliver specific output
Example: "Sales Forecast quality" (Output + Team + Process + System)

Components (4):
  - Dependency Quality: ⭐⭐⭐ (upstream data)
  - Team Execution: ⭐⭐⭐ (team skills)
  - Process Maturity: ⭐⭐ (forecasting process)
  - System Support: ⭐⭐ (CRM features)

Calculation: MIN(components) = ⭐⭐
Bottleneck: Process Maturity ⭐⭐
  ↓ KG Edge: Process Issue → Process Intelligence AI Pilots
  ↓ Recommend: "Use Process Mining to optimize forecasting workflow"
```

### Rationale
Factors in Iteration 4 were abstract capabilities assessed in isolation with no clear path to AI solution recommendations. Output-centric model ties every factor to a specific output, decomposes it into 4 components, and uses simple KG traversal to automatically recommend AI solutions based on bottleneck type.

### Strengths
- ✅ **Direct path to AI solutions** - Every assessment automatically maps to solution categories
- ✅ **KG-supported inference** - Root cause type → AI solution category (built into model)
- ✅ **Output-centric = actionable** - Users understand what's being assessed
- ✅ **Clear bottlenecks** - MIN() identifies weakest link immediately
- ✅ **Honest estimation** - 1-5 stars reflect rough estimation nature
- ✅ **Scope control** - Constraints prevent complexity explosion

### Problem Identified
**Missing Link to Solutions:** Iteration 4's scoped factors could diagnose problems ("Salesforce data quality = 65") but had no connection to improvement opportunities. System could assess organizational capabilities but couldn't recommend AI solutions. Factors existed as isolated assessments with no clear path to action.

**Example Gap:**
```
User: "Can we improve sales forecasting?"
System: "Your data_quality is 65, ml_expertise is 40..."
User: "So what do I do about it?"
System: ❌ No clear answer - factors don't map to solutions
```

**Why We Iterated:** Need direct, automatic path from assessment to AI solution recommendations. The system should not just diagnose but also prescribe.

### Key Innovations

**1. Output-Centric Factors**
- Factor = Capability to deliver specific output (not abstract capability)
- Full context: Output + Team + Process + System
- Example: "Sales Forecast quality by Sales Team in CRM during Forecasting Process"

**2. Four Component Decomposition**
```
Output Factor decomposes into:
  1. Dependency Quality (upstream outputs)
  2. Team Execution (team capability)
  3. Process Maturity (process design)
  4. System Support (system features)
```

**3. MIN() Calculation (Weakest Link)**
- Output_Factor = MIN(4 components)
- Immediately identifies bottleneck
- "Good inputs + good engineers + bad QA = still bad output"
- Simpler than weighted averages, highlights critical issues

**4. Automatic AI Solution Mapping**
```
Bottleneck Type → AI Solution Category (via KG edge)
  - Dependency Issue → Data Quality/Pipeline AI Pilots
  - Execution Issue → Augmentation/Automation AI Pilots
  - Process Issue → Process Intelligence AI Pilots
  - System Issue → Intelligent Features AI Pilots
```

**5. 1-5 Star Rating System**
- Reflects rough estimation nature (not false precision)
- ⭐ = critical, ⭐⭐⭐ = functional, ⭐⭐⭐⭐⭐ = excellent
- Industry-standard pattern everyone understands

**6. Scope Constraints (Locked)**
- Feedback loops: Detect + communicate only
- Multi-output: One pilot = one output
- Temporal: Current state only, no tracking
- Cross-functional: Simple model (one output = one team + one system)

### The Breakthrough: Assessment → Solution Inference

**Pattern: Automatic AI Recommendations**
```
User: "Can we improve sales forecasting?"

System assesses output:
→ Sales Forecast = ⭐⭐ (MIN of components)
→ Bottleneck: Process Maturity = ⭐⭐
→ KG traversal: Process Issue → Process Intelligence AI Pilots
→ Recommend: "Use Process Mining to optimize forecasting workflow"

User: "What about the CRM system?"
→ Bottleneck: System Support = ⭐⭐
→ KG traversal: System Issue → Intelligent Features AI Pilots
→ Recommend: "Add ML-powered forecasting module to CRM"
```

**No manual mapping needed** - it's built into the model through KG edges.

---

## Key Benefits of Output-Centric Model

### 1. Automatic AI Solution Recommendations
**The Breakthrough:** Every output assessment automatically maps to AI solution categories through simple KG inference. No manual mapping, no complex logic - just follow the edges.

**Example:**
```
"Sales Forecast ⭐⭐ due to Process ⭐⭐" 
  → "Use Process Mining AI to optimize workflow"
```

### 2. Honest About Uncertainty
- 1-5 stars reflect rough estimation nature
- No false precision ("65 vs 70" is meaningless)
- Users understand star ratings intuitively

### 3. Clear Bottlenecks
- MIN() immediately identifies weakest link
- Recommendations focus on fixing bottlenecks
- No masking critical issues with averages

### 4. Output-Centric = Actionable
```
"Sales Forecast quality by Sales Team in CRM"
  vs
"data_quality = 65"
```
Users understand what's being assessed and what to improve.

### 5. Scope Control
- Complexity constraints prevent scope creep
- One pilot = one output = clear success criteria
- No temporal tracking, no multi-output optimization
- "The scope stops here"

---

## Implementation Impact

### Data Schema Changes
**Before:** `/users/{user_id}/factor_instances/{instance_id}` with scope {domain, system, team}  
**After:** Output-centric factors with 4 components + MIN() calculation

### New Components
- Output registry (Output + Team + Process + System)
- 4-component decomposition per output
- MIN() calculation engine
- KG edges: Root Cause Type → AI Solution Category
- Dependency graph with loop detection

### Documentation Updates (2025-11-01)
- Updated 8 core documentation files to 1-5 star system
- Created `output_centric_factor_model_exploration.md` (v0.3)
- Created scope lock changelog
- Marked superseded documents (scoped factor model)

---

## Philosophy Evolution

**Iteration 1-3:** Struggled with abstraction and scope
**Iteration 4:** Solved abstraction with scoped instances, but factors still isolated
**Iteration 5:** **Breakthrough - factors become improvement opportunities**

**From:** "Assess organizational capabilities"
**To:** "Identify improvement opportunities with automatic AI solution recommendations"

**From:** "Measure precisely"
**To:** "Estimate honestly and highlight bottlenecks"

**From:** "Track everything"
**To:** "Current state snapshot, scope locked"

---

**Changelog Version:** 2.0  
**Document Status:** Complete - 5 iterations documented  
**Last Updated:** 2025-11-01 22:30
