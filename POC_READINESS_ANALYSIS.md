# POC Readiness Analysis

## Minimal POC Happy Path (from domain_model.md)

### Required Flow:
1. **Output Discovery** - User describes an output (e.g., "Sales Forecast")
2. **Context Inference** - System infers creation context (Team, Process, Step, System)
3. **Confirmation** - User confirms or corrects
4. **Component Assessment** - System asks about 4 components (⭐ 1-5 each):
   - Team Execution Ability
   - System Capabilities
   - Process Maturity
   - Dependency Quality (from upstream outputs)
5. **Calculate Actual Quality** - System calculates MIN() → actual_quality
6. **Required Quality** - User provides required_quality (⭐ 1-5)
7. **Gap Analysis** - System identifies GAP and bottleneck component (the MIN)
8. **Pilot Recommendation** - System recommends Pilot Project targeting bottleneck
9. **(Optional) ROI Estimation** - System estimates business impact

---

## Data Source Availability Check

### ✅ HAVE - Complete and Ready

#### 1. Function Templates (8 functions, 46 outputs)
**Location:** `src/data/organizational_templates/functions/`
- ✅ sales.json
- ✅ finance.json
- ✅ operations.json
- ✅ marketing.json
- ✅ customer_success.json
- ✅ hr.json
- ✅ supply_chain.json
- ✅ it_operations.json

**Contains:**
- Typical teams and roles
- Typical processes and steps
- Typical systems
- Common outputs with:
  - Typical quality metrics (names)
  - Creation context
  - Dependencies
  - Pain points
  - Inference triggers

**POC Usage:** Steps 1-3 (Output Discovery & Context Inference)

---

#### 2. Component Scales
**Location:** `src/data/component_scales.json`

**Contains:**
- 1-5 star rating scales for all 4 components:
  - Team Execution Ability (⭐-⭐⭐⭐⭐⭐)
  - System Capabilities (⭐-⭐⭐⭐⭐⭐)
  - Process Maturity (⭐-⭐⭐⭐⭐⭐)
  - Dependency Quality (⭐-⭐⭐⭐⭐⭐)
- Detailed indicators for each star level
- Inference guidelines

**POC Usage:** Step 4 (Component Assessment)

---

#### 3. Pilot Types
**Location:** `src/data/pilot_types.json`

**Contains:**
- 13 pilot types across 3 categories:
  - **Team Execution** (4 types): AI Copilot, Training, Augmentation, Knowledge Management
  - **System Capabilities** (5 types): AI Features, Automation, Integration, Upgrade, Data Quality
  - **Process Maturity** (4 types): Automation, Intelligence, Optimization, Standardization
- For each pilot type:
  - Description
  - Typical use cases
  - Expected impact
  - Timeline
  - Cost range
  - Prerequisites

**POC Usage:** Step 8 (Pilot Recommendation)

---

#### 4. Inference Rules
**Location:** `src/data/inference_rules/`
- ✅ output_discovery.json - Discovery strategies, conversation patterns
- ✅ pain_point_mapping.json - 100+ pain points in 12 categories
- ✅ ai_archetypes.json - 27 AI/ML archetypes

**POC Usage:** Steps 1-3 (Output Discovery & Context Inference)

---

#### 5. Common Systems
**Location:** `src/data/organizational_templates/cross_functional/common_systems.json`

**Contains:**
- 40+ systems across 10 categories
- System aliases
- Typical outputs created by each system

**POC Usage:** Steps 2-3 (Context Inference)

---

#### 6. Pilot Catalog
**Location:** `src/data/pilot_catalog.json`

**Contains:**
- 28 specific pilot examples
- Pain points addressed
- AI archetypes required

**POC Usage:** Step 8 (Pilot Recommendation - specific examples)

---

#### 7. Capability Framework
**Location:** `src/data/capability_framework.json`

**Contains:**
- 198 organizational capabilities across 4 pillars
- Can be used for detailed component assessment

**POC Usage:** Step 4 (Component Assessment - detailed indicators)

---

## ❌ MISSING - Required for Full POC

### 1. **ROI Calculation Data** ⚠️ CRITICAL GAP

**What's Missing:**
- **Output → Business KPI Mapping**
  - Which outputs affect which business KPIs
  - Example: "Sales Forecast" → "Revenue Forecast Accuracy"
  
- **Quality Improvement → KPI Impact Multipliers**
  - How much does +1 star in a quality metric improve the KPI?
  - Example: +1 star in forecast accuracy → +7.5% revenue accuracy
  
- **KPI → Dollar Value Conversion**
  - How to translate KPI improvements to dollar value
  - Example: +15% revenue accuracy → $500K annual value
  - Needs business context (revenue size, cost structure, etc.)

**Required for:** Step 9 (ROI Estimation)

**Impact:** Without this, POC can only recommend pilots but cannot estimate business value/ROI

---

### 2. **Quality Metric Definitions** ⚠️ MODERATE GAP

**What's Missing:**
- **Standard quality metric names** for each output type
  - Currently, function templates mention "typical_quality_metrics" as strings
  - Need: Structured definitions of what each metric means
  - Example for "Sales Forecast":
    - `accuracy`: "Forecast matches actual within X%"
    - `completeness`: "All required fields populated"
    - `timeliness`: "Delivered by deadline"

**Current State:**
- Function templates have metric names in `typical_quality_metrics` array
- Component scales have generic indicators
- **Gap:** No explicit mapping of metric names to definitions

**Required for:** Steps 4-7 (Component Assessment & Gap Analysis)

**Impact:** POC can work with generic quality assessment, but lacks precision

**Workaround:** Use generic "quality" rating and let user define metrics conversationally

---

### 3. **Dependency Inference Rules** ⚠️ MINOR GAP

**What's Missing:**
- **Typical dependencies between outputs**
  - Which outputs typically depend on which other outputs
  - Example: "Sales Forecast" depends on "Pipeline Data", "Historical Sales Data"
  
**Current State:**
- Function templates have `typical_dependencies` field
- Some outputs list dependencies
- **Gap:** Not comprehensive, not structured for inference

**Required for:** Step 4 (Dependency Quality Assessment)

**Impact:** POC can ask user to manually specify dependencies, but cannot suggest them

**Workaround:** Ask user "Does this output depend on any other outputs?" without suggestions

---

## 🎯 POC Feasibility Assessment

### Can Build Minimal POC? **YES ✅**

### What Works Out of the Box:
1. ✅ **Output Discovery** (Steps 1-3)
   - 8 functions with 46 outputs
   - Inference rules and pain point mapping
   - Common systems for context

2. ✅ **Component Assessment** (Step 4)
   - Component scales with 1-5 star definitions
   - Detailed indicators for each level
   - Can assess Team, System, Process
   - Can ask about dependencies (user provides)

3. ✅ **MIN Calculation** (Step 5)
   - Simple MIN() logic - no data needed

4. ✅ **Gap Analysis** (Steps 6-7)
   - User provides required_quality
   - System calculates gap
   - Identifies bottleneck (MIN component)

5. ✅ **Pilot Recommendation** (Step 8)
   - 13 pilot types mapped to components
   - 28 specific examples
   - Can recommend based on bottleneck

### What Requires Workarounds:
1. ⚠️ **Quality Metric Specificity** (Step 4)
   - **Workaround:** Use generic "quality" rating or let user define metrics
   - **Better:** Pre-populate metric names from function templates

2. ⚠️ **Dependency Suggestions** (Step 4)
   - **Workaround:** Ask user to manually specify dependencies
   - **Better:** Suggest typical dependencies from templates

3. ❌ **ROI Estimation** (Step 9)
   - **Cannot implement without:**
     - Output → KPI mapping
     - Quality → KPI impact multipliers
     - KPI → Dollar value conversion
   - **Workaround:** Skip ROI in minimal POC, show only qualitative impact

---

## 📋 Minimal POC Recommendation

### Phase 1: Core Assessment (Fully Supported)
**Steps 1-8 can be implemented immediately with existing data:**

```
User: "Our sales forecasts are always wrong"
↓
System: [Infers] "Sales Forecast" output
        [Suggests] Team: Sales Operations
                   Process: Sales Forecasting
                   System: CRM
↓
User: Confirms
↓
System: Asks about 4 components (⭐ 1-5):
        - Team Execution: ⭐⭐ (learning as they go)
        - System Capabilities: ⭐⭐ (basic CRM)
        - Process Maturity: ⭐⭐⭐ (standardized but manual)
        - Dependency Quality: ⭐⭐⭐ (pipeline data is decent)
↓
System: Calculates MIN(⭐⭐, ⭐⭐, ⭐⭐⭐, ⭐⭐⭐) = ⭐⭐
        Bottleneck: Team Execution OR System Capabilities (tied)
↓
User: Required quality = ⭐⭐⭐⭐
↓
System: Gap = 2 stars
        Recommends:
        - Option 1: AI Copilot for Sales Forecasting (Team)
        - Option 2: AI-Powered Forecasting Features (System)
        Timeline: 8-12 weeks
        Cost: €20k-€40k
        Expected Impact: ⭐⭐ → ⭐⭐⭐⭐
```

### Phase 2: ROI Estimation (Requires New Data)
**Would need:**
1. Create `roi_mapping.json` with:
   - Output → KPI mappings
   - Quality improvement → KPI impact multipliers
   - Industry benchmarks or templates for dollar value conversion

2. User provides business context:
   - Annual revenue
   - Cost of poor quality
   - Strategic importance

---

## 🚀 Action Items for POC

### Immediate (No Blockers):
1. ✅ Build Steps 1-8 using existing data
2. ✅ Use generic quality assessment or let user define metrics
3. ✅ Ask user to manually specify dependencies
4. ✅ Skip ROI estimation in v1

### Short-term (Nice to Have):
1. ⚠️ Enhance quality metric definitions in function templates
2. ⚠️ Add more typical dependencies to outputs
3. ⚠️ Create dependency inference rules

### Medium-term (For Full Product):
1. ❌ Create `roi_mapping.json` with:
   - Output → KPI mappings
   - Quality → KPI impact multipliers
   - Dollar value conversion templates
2. ❌ Build ROI estimation logic
3. ❌ Add business context collection

---

## ✅ CONCLUSION

**You have everything needed for a minimal POC!**

The only missing piece is **ROI calculation data**, which is:
- Not required for core assessment flow (Steps 1-8)
- Can be added later as Phase 2
- Requires business context that varies by organization

**Recommendation:** Build POC with Steps 1-8, demonstrate value through pilot recommendations, then add ROI estimation based on customer feedback and real business data.
