# Output-Centric Factor Model - Core Concept

**Version:** 1.0  
**Date:** 2025-11-04  
**Status:** Active Design  
**Source:** `output_centric_factor_model_exploration.md` v0.3 (Scope Locked)

---

## The Core Idea

### What is a Factor?

**Factor = Capability to deliver a VERY specific output**

Not: "data_quality = 65" (abstract, organizational)  
But: "Capability to maintain high Sales Forecast quality in CRM by Sales Team during Forecasting Process" (concrete, actionable)

### The Formula

```
Output_Factor = MIN(
    Dependency_Quality,    # Quality of upstream outputs this relies on
    Team_Execution,        # Team's capability (skills, resources)
    Process_Maturity,      # Process quality (documentation, optimization)
    System_Support         # System's capability (features, integration)
)
```

**All values: 1-5 stars ⭐**

### Why MIN()?

**"A chain is only as strong as its weakest link"**

- Good inputs + good engineers + bad QA = still bad output
- Highlights bottlenecks clearly
- Simpler than weighted averages
- Honest about estimation nature
- Prevents masking critical issues

**Example:**
- Dependency Quality: ⭐⭐⭐⭐ (4 stars)
- Team Execution: ⭐⭐⭐ (3 stars)
- Process Maturity: ⭐⭐ (2 stars) ← **BOTTLENECK**
- System Support: ⭐⭐⭐⭐⭐ (5 stars)
- **Result: ⭐⭐ (2 stars)** - Process is the limiting factor

---

## The Breakthrough

### From Abstract to Concrete

**Before (Abstract Factors):**
```
Question: "What is your data quality?"
Problem: Too vague, no context, no action
```

**After (Output-Centric):**
```
Question: "What's preventing Sales Team from maintaining 
high Sales Forecast quality in CRM during Forecasting Process?"

Diagnostic Options:
1. Is it upstream data (Clean Customer Data) that this relies on?
2. Is it Sales Team failing at execution?
3. Is the CRM System making it hard?
4. Is the Forecasting Process itself flawed?
```

### Direct Link to AI Solutions

**The Inference Path:**
```
Output Assessment 
  → Component Decomposition (4 questions)
  → MIN() identifies bottleneck
  → Root Cause Type
  → AI Solution Category
  → Recommend Specific AI Pilots
```

**Root Cause → AI Solution Mapping:**
- **Dependency Issue** → Data Quality/Pipeline AI Pilots
- **Execution Issue** → Augmentation/Automation AI Pilots
- **Process Issue** → Process Intelligence AI Pilots
- **System Issue** → Intelligent Features AI Pilots

**No manual mapping needed - it's built into the model.**

---

## Key Constraints (Scope Lock)

### 1. 1-5 Star Rating System
- All factors, components, and dependencies use 1-5 stars
- Prevents false precision
- Reflects estimation nature
- ⭐ = critical issues, ⭐⭐⭐ = functional, ⭐⭐⭐⭐⭐ = excellent

### 2. MIN() Calculation (Weakest Link)
- Formula: `Output_Factor = MIN(Dependency, Team, Process, System)`
- Highlights bottlenecks clearly
- Simpler than weighted averages

### 3. Dependency Modeling
- Allow loops (organizational feedback loops)
- Limit traversal to 2-3 hops
- Max 10 dependencies per output
- Max 50 outputs in scope

### 4. Feedback Loops: Detect + Communicate Only
- Flag loops, explain virtuous/vicious cycles
- **Do NOT:** Track momentum, predict evolution, manage loop-breaking

### 5. Multi-Output Pilots: One Pilot = One Output
- Each pilot targets exactly one output
- Cascading effects communicated but not managed
- **Do NOT:** Assess across multiple outputs

### 6. Temporal Dynamics: Ignore
- Current state only
- No trend tracking or prediction
- User re-assesses when things change

### 7. Cross-Functional: Simple Model
- One output = one team + one system + multiple upstream outputs
- Dependencies can cross teams naturally
- **Do NOT:** Model matrix organizations or complex governance

---

## The Data Model

### Core Entities

**Output:**
```python
{
    "id": "sales_forecast",
    "name": "Sales Forecast",
    "function": "Sales",
    "description": "Monthly sales predictions in CRM",
    "team": "Sales Operations",
    "process": "Sales Forecasting Process",
    "system": "Salesforce CRM"
}
```

**Factor (tied to Output):**
```python
{
    "output_id": "sales_forecast",
    "factor_value": 2,  # 1-5 stars, calculated as MIN(components)
    "components": {
        "dependency_quality": 3,    # 1-5 stars
        "team_execution": 3,        # 1-5 stars
        "process_maturity": 2,      # 1-5 stars ← bottleneck
        "system_support": 2         # 1-5 stars ← bottleneck
    },
    "bottlenecks": ["process_maturity", "system_support"],
    "confidence": 0.80
}
```

**Output Dependency:**
```python
{
    "source_output_id": "clean_customer_data",
    "target_output_id": "sales_forecast",
    "strength": 5  # 1-5 stars (how critical is this dependency?)
}
```

---

## The Conversation Flow

### Single Conversation, Not Phases

**Not This (Phase-Based):**
```
Phase 1: Discovery → Identify output
Phase 2: Assessment → Rate components
Phase 3: Gap Analysis → Calculate MIN()
Phase 4: Recommendations → Suggest pilots
```

**This (Single Flow):**
```
1. User describes problem
   "Our sales forecasts are always wrong"

2. System identifies output
   Output: Sales Forecast
   Team: Sales Operations
   Process: Sales Forecasting Process
   System: Salesforce CRM

3. System asks 4 diagnostic questions
   Q1: "How would you rate the quality of data you receive 
        from upstream sources? (1-5 stars)"
   User: "3 stars - customer data is okay but not great"
   
   Q2: "How would you rate your team's skills and resources 
        for forecasting? (1-5 stars)"
   User: "3 stars - decent but we lack ML expertise"
   
   Q3: "How mature is your forecasting process? 
        (documented, standardized, optimized) (1-5 stars)"
   User: "2 stars - very ad-hoc, no standard process"
   
   Q4: "How well does your CRM system support forecasting 
        workflows? (1-5 stars)"
   User: "2 stars - no built-in forecasting tools"

4. System calculates MIN()
   factor_value = MIN(3, 3, 2, 2) = 2 stars

5. System identifies bottlenecks
   Bottlenecks: Process Maturity (⭐⭐), System Support (⭐⭐)

6. System recommends improvements
   "Your bottlenecks are Process and System. 
    Recommendation: Add forecasting tools to CRM first - 
    this would have immediate impact and enable process improvements."
```

---

## UX Principles (from TBD.md)

### TBD #11: Anti-Abstract Pattern
When user talks abstractly, respond:  
"Sorry, I do not do abstract. Let's pick a very concrete example of when this problem manifested, and use that example as a proxy."

### TBD #12: Output-Team-System-Process Constraint
If something cannot be expressed as "an output created by a team in a system in a process", it's probably not a good candidate for an internal, data-driven technical pilot.

### TBD #13: Numbered Question Format
Add numeric IDs to questions:  
"1. What team creates this output?"  
"2. Which system do they use?"  
User can respond: "1: Sales Team, 2: Salesforce"

### TBD #14: Professional Reflection (No Empathy)
Don't empathize ("I understand that must be frustrating...").  
Instead, state why information is relevant:  
"This indicates a bottleneck in Team Execution. Created factor: Sales Forecast quality = ⭐⭐ due to junior team."

---

## What Makes This Different

### 1. Specificity
Factors tied to concrete outputs, not abstract capabilities

### 2. Traceability
Output dependencies enable root cause analysis

### 3. Actionability
Questions specific to Team/Process/System context

### 4. Diagnostic Power
Can distinguish upstream dependency problems from execution problems

### 5. Granularity
Same capability assessed differently in different contexts

### 6. Smart Questioning
System asks "Why is X preventing Y in context Z?"

---

## Example: Sales Forecast Assessment

**User Input:**
"Our sales forecasts are always wrong"

**System Identifies:**
- Output: Sales Forecast
- Team: Sales Operations
- Process: Sales Forecasting Process
- System: Salesforce CRM

**System Assesses (4 questions):**
- Dependency Quality: ⭐⭐⭐ (3 stars) - customer data okay
- Team Execution: ⭐⭐⭐ (3 stars) - decent but lack ML expertise
- Process Maturity: ⭐⭐ (2 stars) - ad-hoc, no standard
- System Support: ⭐⭐ (2 stars) - no forecasting tools

**System Calculates:**
```
factor_value = MIN(3, 3, 2, 2) = 2 stars
bottlenecks = [process_maturity, system_support]
```

**System Recommends:**
"Your bottlenecks are Process (⭐⭐) and System (⭐⭐).

**Root Cause:** Process Issue + System Issue

**AI Pilot Opportunities:**
1. **Process Intelligence Pilot** - Use process mining to identify forecasting workflow bottlenecks
2. **Intelligent Features Pilot** - Add ML-powered forecasting module to CRM

**Recommendation:** Focus on System Support first (add forecasting tools to CRM). This would have immediate impact and enable process improvements.

**Expected Impact:** Improving System from ⭐⭐ to ⭐⭐⭐⭐ would lift overall factor to ⭐⭐⭐ (if Process also improves to ⭐⭐⭐)."

---

## Success Criteria

### For a Single Output Assessment

✅ User can describe an output problem in natural language  
✅ System extracts Output + Team + Process + System  
✅ System asks 4 component questions (1-5 stars each)  
✅ System calculates factor as MIN(components)  
✅ System identifies bottleneck(s) (components at MIN value)  
✅ System recommends AI pilots based on root cause type  
✅ Database stores output-centric factor with context  
✅ End-to-end conversation → storage → retrieval works

---

## What's Out of Scope

❌ Abstract organizational factors ("data_quality = 65")  
❌ Weighted averages or complex formulas  
❌ Temporal tracking (trends, predictions)  
❌ Feedback loop management (detect + communicate only)  
❌ Multi-output pilot optimization  
❌ Matrix organization modeling  
❌ Decision tracking and execution monitoring

---

## References

- **Primary Design:** `docs/2_technical_spec/output_centric_factor_model_exploration.md`
- **UX Constraints:** `docs/1_functional_spec/TBD.md` (#11, #12, #13, #14)
- **Interaction Patterns:** `docs/1_functional_spec/user_interaction_guideline.md`
- **Scope Lock:** `docs/3_changelog/2025-11-01-2125-scope-lock-simplification.md`
