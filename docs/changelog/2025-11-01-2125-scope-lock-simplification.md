# Scope Lock: Simplification & Complexity Constraints

**Date:** 2025-11-01 21:25  
**Version:** 0.3  
**Status:** Scope Locked  
**Impact:** Major - Fundamental design simplifications applied

---

## Summary

Applied critical scope constraints to the output-centric factor model to prevent complexity explosion. All open questions resolved with bias toward simplicity and honest estimation over false precision.

**Core Philosophy:** "The more we specify system requirements, the faster the scope accelerates away. I want the scope to stop."

---

## Key Decisions

### 1. ✅ Factor Scoring: 1-5 Stars (Not 0-100)

**Rationale:**
- All factor values are rough estimations—representation should reflect that
- Prevents false precision ("65 vs 70" is meaningless)
- Standardized across entire system
- Makes factor calculation simpler and more arbitrary (which is good, because it IS arbitrary)
- Industry-standard pattern everyone understands

**Scale:**
- ⭐ (1 star): Critical issues, major blockers, fundamentally broken
- ⭐⭐ (2 stars): Significant problems, frequent failures, needs major work
- ⭐⭐⭐ (3 stars): Functional but inconsistent, room for improvement
- ⭐⭐⭐⭐ (4 stars): Good quality, minor issues, mostly reliable
- ⭐⭐⭐⭐⭐ (5 stars): Excellent, consistent, best-in-class

**Impact:**
- All factors: 1-5 integer values
- All components: 1-5 integer values
- All dependencies: 1-5 strength ratings
- No decimals, no percentages, no 0-100 scales anywhere

---

### 2. ✅ Factor Calculation: MIN (Weakest Link)

**Rationale:**
- "Good inputs + good engineers + bad QA = still bad output"
- Chain is only as strong as weakest link
- Arbitrary calculation is honest—we're estimating, not measuring precisely
- Simpler than weighted averages
- Highlights bottlenecks clearly

**Formula:**
```
Output_Factor = MIN(Dependency_Quality, Team_Execution, Process_Maturity, System_Support)
```

**Example:**
- Dependency Quality: ⭐⭐⭐⭐ (4 stars)
- Team Execution: ⭐⭐⭐ (3 stars)
- Process Maturity: ⭐⭐ (2 stars) ← BOTTLENECK
- System Support: ⭐⭐⭐⭐⭐ (5 stars)
- **Result: ⭐⭐ (2 stars)** - Process is the limiting factor

**Deprecated:** Weighted average approach (0.25 each or archetype-specific weights)

---

### 3. ✅ Feedback Loops: Detect + Communicate Only

**Rationale:**
- Feedback loops are valuable organizational insights
- Detecting and communicating them adds value
- Managing loop dynamics adds significant complexity
- Scope constraint: Keep system focused on core assessment

**Implementation:**
- Detect loops during dependency traversal
- Flag as "positive feedback loop" in diagnostics
- Explain effect: "Virtuous cycle" or "Vicious cycle"
- Communicate what can be done: "Breaking this loop by improving [Output X] would have cascading benefits"
- **Do NOT:** Track loop momentum, predict evolution, manage loop-breaking strategies

**Future:** TBD marker for potential enhancement if user demand emerges

---

### 4. ✅ Multi-Output Pilots: One Pilot = One Output

**Rationale:**
- Scope constraint: Prevents complexity explosion
- Pilots are scoped to specific, measurable outcomes
- One output = clear success criteria
- Multi-output optimization adds significant assessment complexity

**Implementation:**
- Each AI Pilot targets exactly one output
- System detects and communicates cascading effects: "Improving Clean Customer Data will also benefit Sales Forecast and Inventory Plan"
- User understands broader impact, but pilot assessed against primary output only
- **Do NOT:** Assess feasibility across multiple outputs, track multi-output ROI, optimize for multiple targets

---

### 5. ✅ Temporal Dynamics: Ignore

**Rationale:**
- Scope constraint: Time-series tracking adds significant complexity
- If something improves, user will tell us
- System will know current state through new assessment
- Prediction is unreliable and adds false precision

**Implementation:**
- Store factor assessments with timestamps (audit trail only)
- **Do NOT:** Track trends, predict future states, show historical charts, use temporal data in recommendations
- Each assessment is a snapshot of current state
- User can re-assess anytime to capture changes
- System treats each assessment independently

**User Communication:**
- "Based on current state..."
- No promises about future feasibility
- If user mentions planned improvements: "Great! Re-assess after those changes to see updated feasibility"

---

### 6. ✅ Cross-Functional Dependencies: Simple Model Only

**Rationale:**
- Scope constraint: Complex cross-functional modeling explodes complexity
- The model already handles this: Output A (Team 1) depends on Output B (Team 2)
- Dependency graph captures cross-team relationships naturally
- User understands their context, system doesn't need to manage it

**Model:**
- **One output** is produced by:
  - **One team** (the team responsible)
  - Using **one system** (primary system)
  - Depending on **multiple upstream outputs** (from any teams/systems)
- This simple model can handle any complexity if user uses it well

**Implementation:**
- Store team_id and system_id with each output
- Dependencies can cross team/system boundaries (no special handling)
- System can detect: "Sales Forecast (Sales Team) depends on Clean Data (Data Engineering Team)"
- Communicate collaboration need, but don't manage it
- **Do NOT:** Model matrix organizations, shared ownership, cross-functional governance, organizational silos

---

## Document Updates

### File: `docs/output_centric_factor_model_exploration.md`

**Version:** 0.2 → 0.3  
**Status:** "Core design decisions resolved" → "Scope locked, complexity constraints applied"

**Sections Updated:**
1. Added Decision #5: Factor Scoring System (1-5 stars)
2. Added Decision #6: Factor Calculation Logic (MIN)
3. Deprecated Decision #7: Factor Calculation Weights
4. Resolved Open Question #1: Factor Component Measurement (1-5 stars)
5. Resolved Open Question #3: Feedback Loop Handling (detect + communicate)
6. Resolved Open Question #4: Multi-Output AI Pilots (one pilot = one output)
7. Resolved Open Question #5: Temporal Dynamics (ignore)
8. Resolved Open Question #6: Cross-Functional Dependencies (simple model)
9. Updated Diagram 3: Multi-Level Dependency Chain (star ratings)
10. Updated Diagram 8: Factor as Composite of Sub-Factors (star ratings + MIN formula)
11. Updated Implementation Roadmap Increment 1 (star ratings)
12. Updated Implementation Roadmap Increment 2 (star ratings, simplified impact)
13. Updated Implementation Roadmap Increment 3 (star ratings, MIN calculation)
14. Updated final status section with scope constraints summary

---

## Impact on Implementation

### Data Model Changes
- All factor values: `INTEGER` (1-5) instead of `DECIMAL` (0-100)
- All component values: `INTEGER` (1-5)
- All dependency strengths: `INTEGER` (1-5)
- No temporal tracking tables needed
- No complex cross-functional relationship tables needed

### Calculation Logic Changes
- Replace weighted average with `MIN()` function
- Identify bottleneck(s) = component(s) with minimum value
- Simpler, faster, more transparent

### UI/UX Changes
- Display star ratings everywhere (⭐⭐⭐)
- Show bottleneck components prominently
- No trend charts, no predictions
- Cascading effects shown as informational only

### Conversation Flow Changes
- Ask for star ratings (1-5) instead of percentages
- Map natural language to stars: "struggling" = 2, "okay" = 3, "great" = 5
- Focus recommendations on weakest link
- Communicate cascading effects without managing them

---

## Scope Constraints Summary

**Applied:**
- ✅ 1-5 star rating system (no false precision)
- ✅ MIN() calculation (weakest link)
- ✅ Feedback loops: detect + communicate only
- ✅ One pilot = one output (cascading effects communicated)
- ✅ No temporal tracking (current state only)
- ✅ Simple cross-functional model (one output = one team + one system)

**Prevented:**
- ❌ 0-100 scales with false precision
- ❌ Weighted averages with arbitrary weights
- ❌ Loop momentum tracking and prediction
- ❌ Multi-output pilot optimization
- ❌ Time-series analysis and forecasting
- ❌ Matrix organization modeling

---

## Next Steps

1. ~~Answer open questions 1-6~~ ✅ COMPLETE
2. Begin Phase 1: Data Model implementation (1-5 star schema)
3. Implement MIN() factor calculation logic
4. Prototype dependency graph engine (with loop detection)
5. Test with synthetic data before user testing

---

## Related Documents

- `docs/output_centric_factor_model_exploration.md` (v0.3)
- `docs/taxonomy_completion_task.md` (needs update for 1-5 star scales)

---

## Notes

This scope lock represents a critical pivot toward simplicity and honesty about the estimation nature of the system. By embracing rough approximations (stars) and simple logic (MIN), we prevent the false precision trap and keep the system implementable.

The philosophy: "It IS arbitrary, so let's be honest about it and make it simple."
