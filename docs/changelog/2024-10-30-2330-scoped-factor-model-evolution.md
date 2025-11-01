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

## Iteration 5: Output-Centric Model (2025-11-01)

### Major Evolution: From Theoretical Capabilities to Output-Linked Improvement Opportunities

**Date:** 2025-11-01  
**Impact:** Fundamental reconceptualization - Enables direct AI solution recommendations

### The Critical Shift

**Previous Model (Iteration 4):**
- Factor = Abstract organizational capability (e.g., "data_quality = 65")
- Assessed at organization level, scoped to domain/system/team
- **No direct connection to improvement opportunities**
- **Cannot easily recommend AI solutions** - factors exist in isolation
- Generic and context-free

**New Model (Iteration 5):**
- Factor = **Capability to deliver a VERY specific output**
- Example: "Capability to maintain high Sales Forecast quality in CRM by Sales Team during Forecasting Process"
- Assessed in context of: Output + Team + Process + System
- **Direct link to improvement opportunities** - each output can be improved
- **Easy KG-supported inference** to recommend Data Engineering / ML / Advanced AI solutions
- Concrete and actionable

### The Game-Changer: Output → Improvement Opportunity Inference

**Before (Iteration 4):**
```
Factor: "data_quality" = 65 (scoped to sales/Salesforce)
↓
❌ No clear path to improvement recommendations
❌ Cannot easily suggest AI solutions
❌ Factors exist as isolated assessments
```

**After (Iteration 5):**
```
Output: "Sales Forecast" (quality: ⭐⭐)
  ↓ Decompose into 4 components
  - Dependency Quality: ⭐⭐⭐ (upstream data)
  - Team Execution: ⭐⭐⭐ (team skills)
  - Process Maturity: ⭐⭐ (forecasting process) ← BOTTLENECK
  - System Support: ⭐⭐ (CRM features) ← BOTTLENECK
  ↓ MIN() identifies bottlenecks
  ↓ KG traversal: Process Issue → Process Intelligence AI Pilots
  ↓ KG traversal: System Issue → Intelligent Features AI Pilots
✅ Recommend: "Process Mining to optimize forecasting workflow"
✅ Recommend: "Add ML-powered forecasting module to CRM"
```

**The Innovation:** Every output assessment automatically maps to specific AI solution categories through simple KG inference.

### Key Design Decisions (Scope Locked)

#### 1. Output-Centric Factors (THE MAJOR CHANGE)
**What Changed:**
- Factors no longer abstract capabilities floating in isolation
- Every factor tied to a specific Output + Team + Process + System
- Four component decomposition enables root cause identification
- Root cause type directly maps to AI solution category

**Why This Matters:**
- **Before:** "Your data quality is 65%" → ❓ "So what? What do I do?"
- **After:** "Your Sales Forecast is ⭐⭐ because Process Maturity is ⭐⭐" → ✅ "Use Process Intelligence AI to optimize your forecasting workflow"

**The Inference Path:**
```
Output Assessment
  ↓ Component Decomposition (4 components)
  ↓ MIN() Calculation (identifies bottleneck)
  ↓ Root Cause Type (Dependency/Execution/Process/System)
  ↓ KG Edge: Root Cause → AI Solution Category
  ↓ Recommend Specific AI Pilots
```

#### 2. Factor Scoring: 1-5 Stars (Simplification Detail)
**Rationale:**
- All factor values are rough estimations—representation should reflect that
- Prevents false precision ("65 vs 70" is meaningless)
- Standardized across entire system
- Industry-standard pattern everyone understands

**Scale:**
- ⭐ (1 star): Critical issues, major blockers, fundamentally broken
- ⭐⭐ (2 stars): Significant problems, frequent failures, needs major work
- ⭐⭐⭐ (3 stars): Functional but inconsistent, room for improvement
- ⭐⭐⭐⭐ (4 stars): Good quality, minor issues, mostly reliable
- ⭐⭐⭐⭐⭐ (5 stars): Excellent, consistent, best-in-class

#### 2. Factor Calculation: MIN (Weakest Link)
**Formula:**
```
Output_Factor = MIN(Dependency_Quality, Team_Execution, Process_Maturity, System_Support)
```

**Rationale:**
- "Good inputs + good engineers + bad QA = still bad output"
- Chain is only as strong as weakest link
- Arbitrary calculation is honest—we're estimating, not measuring precisely
- Simpler than weighted averages
- Highlights bottlenecks clearly

**Example:**
- Dependency Quality: ⭐⭐⭐⭐ (4 stars)
- Team Execution: ⭐⭐⭐ (3 stars)
- Process Maturity: ⭐⭐ (2 stars) ← BOTTLENECK
- System Support: ⭐⭐⭐⭐⭐ (5 stars)
- **Result: ⭐⭐ (2 stars)** - Process is the limiting factor

#### 3. Scope Constraints Applied

**Feedback Loops:** Detect + communicate only (no management)
- Flag loops, explain virtuous/vicious cycles
- Do NOT track momentum, predict evolution, or manage loop-breaking

**Multi-Output Pilots:** One pilot = one output
- Each pilot targets exactly one output
- Cascading effects communicated but not managed

**Temporal Dynamics:** Ignore
- Current state only, no trend tracking or prediction
- User re-assesses when things change

**Cross-Functional:** Simple model
- One output = one team + one system + multiple upstream outputs
- Dependencies can cross teams naturally
- Do NOT model matrix organizations or complex governance

### Why This Evolution?

**Critical Problem with Iteration 4:**
- **Factors had no connection to improvement opportunities**
- Abstract capabilities ("data_quality") assessed in isolation
- No clear path from assessment to AI solution recommendation
- System could diagnose problems but not suggest solutions
- Scoping to domain/system helps but doesn't enable solution inference

**Solution in Iteration 5:**
- **Every factor linked to a specific output that can be improved**
- Output decomposition (4 components) enables root cause identification
- Root cause type maps directly to AI solution category via KG
- Simple MIN() calculation highlights bottlenecks
- **KG-supported inference makes recommendations trivial:**
  - Process Issue → Process Intelligence AI Pilots
  - System Issue → Intelligent Features AI Pilots
  - Execution Issue → Augmentation/Automation AI Pilots
  - Dependency Issue → Data Quality/Pipeline AI Pilots

### Root Cause to AI Pilot Mapping

Each bottleneck type maps to AI opportunity:
- **Dependency Issue** (upstream output) → Data Quality/Pipeline AI Pilots
- **Execution Issue** (team capability) → Augmentation/Automation AI Pilots
- **Process Issue** (process design) → Process Intelligence AI Pilots
- **System Issue** (system limitations) → Intelligent Features AI Pilots

### Documentation Impact

**Files Updated (2025-11-01):**
1. `entity_relationship_model.md` (v1.1 → v1.2)
2. `TAXONOMY_GAPS_SUMMARY.md` (marked superseded)
3. `taxonomy_enrichment_roadmap.md` (updated for stars)
4. `scoped_factor_model.md` (v1.0 → v1.1, marked superseded)
5. `gcp_data_schemas.md` (schema updated to INTEGER 1-5)
6. `VERTICAL_EPICS.md` (examples updated)
7. `user_interaction_guideline.md` (examples updated)
8. `architecture_summary.md` (added MIN() references)

**New Documents Created:**
- `output_centric_factor_model_exploration.md` (v0.3) - Primary design document
- `changelog/2025-11-01-2125-scope-lock-simplification.md` - Scope decisions
- `changelog/2025-11-01-2200-documentation-coherence-update.md` - Documentation updates

### Key Benefits of Iteration 5

**1. Direct Path to AI Solutions (THE BREAKTHROUGH)**
- Every output assessment → automatic AI solution recommendations
- KG-supported inference: Root cause type → AI solution category
- No manual mapping needed - it's built into the model
- **Example:** "Sales Forecast ⭐⭐ due to Process ⭐⭐" → "Use Process Mining AI"

**2. Output-Centric = Actionable**
- Factors tied to specific, measurable outputs
- Full context: Output + Team + Process + System
- Users understand what's being assessed ("Sales Forecast quality")
- Clear improvement target ("improve this specific output")

**3. Clear Bottlenecks**
- MIN() calculation immediately identifies weakest link
- Recommendations focus on fixing bottlenecks
- No masking critical issues with high averages

**4. Honest Estimation**
- 1-5 stars reflect rough estimation nature
- No false precision from 0-100 scales
- Users understand star ratings intuitively

**5. Scope Control**
- Complexity constraints prevent scope creep
- One pilot = one output = clear success criteria
- No temporal tracking, no multi-output optimization

### Implementation Changes

**Data Model:**
- Factor values: INTEGER (1-5), not DECIMAL (0-100)
- Component values: INTEGER (1-5) for each of 4 components
- Dependency strengths: INTEGER (1-5)
- Calculation: MIN() function

**UI/UX:**
- Display star ratings (⭐⭐⭐) everywhere
- Show bottleneck components prominently
- No trend charts, no predictions
- Cascading effects shown as informational only

**Conversation Flow:**
- Ask for star ratings (1-5) instead of percentages
- Map natural language to stars: "struggling" = 2, "okay" = 3, "great" = 5
- Focus recommendations on weakest link

### Philosophy Shift

**From:** "Let's measure organizational capabilities precisely"
**To:** "Let's honestly estimate what's blocking specific outputs"

**From:** "Assess abstract factors in isolation"
**To:** "Assess output capabilities with direct path to AI solutions"

**From:** "Complex weighted calculations for accuracy"
**To:** "Simple MIN() to highlight bottlenecks"

**From:** "Track everything over time"
**To:** "Current state snapshot, re-assess when things change"

**From:** "Factors as theoretical capabilities"
**To:** "Factors as improvement opportunities with KG-supported AI solution recommendations"

### Scope Lock Rationale

**User Statement:** "The more we specify system requirements, the faster the scope accelerates away. I want the scope to stop."

**Response:**
- Locked to 1-5 stars (no false precision)
- Locked to MIN() calculation (no complex weights)
- Locked to simple model (no temporal, no multi-output, no matrix orgs)
- Locked to detect-only for feedback loops

**Result:** Implementable, honest, focused system

---

**Changelog Version:** 2.0  
**Document Status:** Updated with Iteration 5 (Output-Centric Model)  
**Last Updated:** 2025-11-01 22:25
