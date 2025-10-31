# Taxonomy Enrichment Roadmap - Knowledge Graph Readiness

**Date:** 2024-11-01  
**Status:** Planning  
**Priority:** Critical - Blocker for Knowledge Graph Construction  
**Estimated Time:** 4-6 days

---

## Executive Summary

The existing taxonomies (`AI_use_case_taxonomy.json`, `AI_dependency_taxonomy.json`) define **WHAT exists** (AI archetypes, technical prerequisites) but lack the **organizational context layer** needed to build a functional knowledge graph for conversational assessment.

**Core Gap:** No structured definition of **organizational factors** - the measurable attributes of an organization that determine AI readiness.

**Impact:** Cannot build knowledge graph edges that connect:
- User conversations → Factor assessments → Capability evaluations → Project feasibility

---

## Current State Analysis

### What We Have ✅

**1. AI Use Case Taxonomy** (`AI_use_case_taxonomy.json`)
- 25 AI archetypes (Anomaly Detection, Classification, Forecasting, etc.)
- Technical families and analytical purposes
- Example outputs and models
- **Status:** Structurally complete

**2. AI Dependency Taxonomy** (`AI_dependency_taxonomy.json`)
- 7 prerequisite categories (Data Quality, Technical Expertise, Infrastructure, etc.)
- 40+ specific prerequisites with descriptions
- Links to dependent models and outputs
- **Status:** Structurally complete but isolated

**3. Scoped Factor Model** (Documentation)
- Architecture for domain/system-specific assessments
- Scope matching algorithm implemented
- Clarifying question patterns defined
- **Status:** Design complete, awaiting data foundation

### What's Missing ❌

**1. Organizational Factors Taxonomy** 🚨 CRITICAL
- No structured definition of assessable organizational attributes
- No 0-100 scales with observable anchors
- No inference hints for LLM-based assessment
- **Impact:** Cannot infer "data_quality = 30" from conversation

**2. Factor-to-Capability Mapping** 🚨 CRITICAL
- No definition of how factors combine to enable project types
- No factor weights or importance levels
- No minimum thresholds per capability
- **Impact:** Cannot evaluate "Can we do sales forecasting?" from assessed factors

**3. Factor Interdependencies** 🔴 HIGH
- No model of how factors influence each other
- Cannot represent "executive support mitigates expertise gaps"
- No mechanism for factor-based reasoning
- **Impact:** Cannot provide nuanced recommendations

**4. Prerequisite-to-Factor Mapping** 🔴 HIGH
- Prerequisites exist in isolation
- No link to organizational factors
- Cannot determine "Is 'Clean_and_validated_data' satisfied?"
- **Impact:** Cannot bridge technical requirements to organizational reality

**5. Assessment Metadata** 🟡 MEDIUM
- No time-to-assess estimates
- No confidence impact calculations
- No ROI data for "what's next" suggestions
- **Impact:** Cannot prioritize assessment activities

**6. Factor-to-Archetype Impact** 🟡 MEDIUM
- No model of which factors improve which archetypes
- Cannot answer "Improving data governance helps which projects?"
- No quantified impact relationships
- **Impact:** Cannot explain factor value or prioritize improvements

---

## Gap Analysis: Why This Blocks Knowledge Graph Construction

### Current Taxonomy Structure
```
AI_use_case_taxonomy.json:
  Archetype → Models → Outputs

AI_dependency_taxonomy.json:
  Prerequisite → Dependent Models → Dependent Outputs
```

### Required Knowledge Graph Structure
```
ORGANIZATIONAL_FACTOR (e.g., data_quality)
  ↓ HAS_SCALE
  FACTOR_SCALE (0-100 with anchors)
  
  ↓ SATISFIES
  PREREQUISITE (e.g., Clean_and_validated_data)
  
  ↓ ENABLES
  CAPABILITY (e.g., Supervised Classification)
  
  ↓ SUPPORTS
  AI_ARCHETYPE (e.g., Classification)
  
  ↓ INFLUENCES
  OTHER_FACTOR (e.g., data_governance → data_quality)
  
  ↓ IMPROVES
  AI_ARCHETYPE (with impact score)
```

### Missing Edges
Without organizational factors, we cannot create:
1. **Conversation → Factor** edges (no scales to map statements to values)
2. **Factor → Prerequisite** edges (no mapping defined)
3. **Factor → Capability** edges (no capability definitions)
4. **Factor → Factor** edges (no interdependencies)
5. **Factor → Archetype** edges (no impact model)

**Result:** Knowledge graph has archetypes and prerequisites, but no way to connect them to organizational reality.

---

## Detailed Gap Breakdown

### Gap 1: Organizational Factors Taxonomy 🚨

**What's Missing:**
```json
{
  "factor_id": "data_quality",
  "factor_name": "Data Quality",
  "category": "data_readiness",
  "description": "Quality, consistency, and reliability of organizational data",
  
  "scale": {
    "type": "0-100",
    "anchors": {
      "0": "No quality controls, data unreliable for any use",
      "20": "Ad-hoc quality checks, many known issues, manual fixes",
      "40": "Basic quality processes, some validation, reactive fixes",
      "60": "Systematic quality framework, automated checks, proactive monitoring",
      "80": "Comprehensive quality governance, continuous improvement",
      "100": "World-class data quality, real-time monitoring, zero tolerance"
    }
  },
  
  "scope_dimensions": {
    "domain": {"required": false, "common_values": ["sales", "finance", "operations"]},
    "system": {"required": false, "allow_custom": true},
    "team": {"required": false, "allow_custom": true}
  },
  
  "inference_hints": {
    "positive_indicators": ["automated validation", "data quality dashboard", "quality SLAs"],
    "negative_indicators": ["scattered data", "no data catalog", "frequent duplicates"]
  },
  
  "assessment_metadata": {
    "typical_time_minutes": 10,
    "complexity": "medium",
    "requires_technical_knowledge": false
  }
}
```

**Why Critical:**
- LLM needs scales to map "data scattered across 5 systems" → `data_quality = 20`
- Scope dimensions enable domain/system-specific assessments
- Inference hints guide conversational extraction
- Assessment metadata enables ROI calculations

**Minimum Required Factors (15):**

**Data Readiness (5):**
1. `data_quality` - Quality, consistency, reliability
2. `data_availability` - Volume, coverage, accessibility
3. `data_governance` - Policies, ownership, compliance
4. `data_infrastructure` - Storage, processing, pipelines
5. `data_security` - Access controls, privacy, encryption

**AI Capability (5):**
6. `ml_infrastructure` - Compute, MLOps, deployment
7. `ml_expertise` - Team skills, experience, training
8. `ml_tooling` - Frameworks, platforms, monitoring
9. `experimentation_culture` - Testing, iteration, learning
10. `model_lifecycle_management` - Versioning, monitoring, retraining

**Organizational Readiness (5):**
11. `executive_support` - CxO buy-in, budget, priority
12. `change_management` - Adoption processes, training, communication
13. `cross_functional_collaboration` - Data science + business alignment
14. `risk_tolerance` - Willingness to experiment, fail fast
15. `business_process_maturity` - Documented, measured, optimized

### Gap 2: Factor-to-Capability Mapping 🚨

**What's Missing:**
```json
{
  "capability_id": "supervised_classification",
  "capability_name": "Supervised Classification Projects",
  "description": "Ability to build and deploy classification models",
  
  "enabled_archetypes": [
    "Content Analysis / Labeling / Evaluation",
    "Classification",
    "Intent Detection & Routing"
  ],
  
  "factor_requirements": [
    {
      "factor_id": "data_quality",
      "importance": "critical",
      "minimum_threshold": 50,
      "weight": 0.25,
      "rationale": "Classification requires clean, consistent labeled data"
    },
    {
      "factor_id": "data_availability",
      "importance": "critical",
      "minimum_threshold": 60,
      "weight": 0.20,
      "rationale": "Need sufficient labeled examples for training"
    },
    {
      "factor_id": "ml_expertise",
      "importance": "important",
      "minimum_threshold": 40,
      "weight": 0.15,
      "rationale": "Classification is well-understood, moderate expertise sufficient"
    }
  ],
  
  "confidence_calculation": {
    "formula": "weighted_average",
    "minimum_confidence_threshold": 0.60
  }
}
```

**Why Critical:**
- Enables project feasibility evaluation: "Can we do sales forecasting?"
- Provides confidence scoring: "45% confident based on assessed factors"
- Identifies gaps: "Need data_governance (10 min) → +15% confidence"
- Links factors to actionable project types

**Minimum Required Capabilities (6):**
1. Supervised Classification
2. Regression & Forecasting
3. Anomaly Detection
4. Clustering & Segmentation
5. Natural Language Processing
6. Generative AI

### Gap 3: Factor Interdependencies 🔴

**What's Missing:**
```json
{
  "source_factor": "executive_support",
  "target_factor": "ml_expertise",
  "relationship_type": "mitigates_gap",
  "strength": 0.30,
  "description": "Strong executive support can compensate for expertise gaps",
  "mechanism": "budget_for_training",
  "examples": [
    "CxO approves 6-month learning period",
    "Budget for external consultants",
    "Protected time for experimentation"
  ]
}
```

**Relationship Types:**
- `mitigates_gap` - Source compensates for weakness in target
- `enables` - Source is prerequisite for target
- `reinforces` - Source amplifies target
- `conflicts_with` - Source undermines target

**Why Important:**
- Enables nuanced reasoning: "Low ML expertise, but high executive support → viable with training"
- Explains factor interactions in recommendations
- Supports "what-if" scenarios: "If we improve governance, quality will improve"

**Minimum Required Interdependencies (10-15):**
- executive_support → ml_expertise (mitigates)
- data_governance → data_quality (enables)
- experimentation_culture → risk_tolerance (reinforces)
- ml_infrastructure → model_lifecycle_management (enables)
- cross_functional_collaboration → change_management (reinforces)
- data_security → data_governance (enables)
- ml_tooling → ml_expertise (mitigates)
- business_process_maturity → change_management (enables)
- risk_tolerance → experimentation_culture (reinforces)
- executive_support → cross_functional_collaboration (enables)

### Gap 4: Prerequisite-to-Factor Mapping 🔴

**What's Missing:**
```json
// In AI_dependency_taxonomy.json, add to each prerequisite:
{
  "prerequisite_id": "Clean_and_validated_data",
  "description": "...",
  "dependent_models": [...],
  
  "maps_to_factors": [
    {
      "factor_id": "data_quality",
      "contribution": "primary",
      "threshold": 50,
      "notes": "This prerequisite is satisfied when data_quality >= 50"
    },
    {
      "factor_id": "data_infrastructure",
      "contribution": "supporting",
      "threshold": 40,
      "notes": "Infrastructure needed to implement quality checks"
    }
  ]
}
```

**Why Important:**
- Bridges technical requirements to organizational factors
- Enables prerequisite satisfaction checking
- Links existing taxonomy to new factor model
- Maintains backward compatibility

**Scope:** Update all 40+ prerequisites in `AI_dependency_taxonomy.json`

### Gap 5: Assessment Metadata 🟡

**What's Missing:**
```json
{
  "factor_id": "data_quality",
  "typical_assessment_time_minutes": 10,
  "confidence_impact_by_capability": {
    "supervised_classification": 0.15,
    "regression_forecasting": 0.18,
    "anomaly_detection": 0.12
  },
  "assessment_difficulty": "medium",
  "requires_technical_expert": false,
  "can_be_partially_assessed": true,
  "diminishing_returns_threshold": 3
}
```

**Why Useful:**
- Enables ROI-driven "what's next" suggestions
- Prioritizes assessment activities by impact/time
- Signals diminishing returns: "After 3 turns, <5% confidence gain"
- Supports Pareto principle: "20% of factors, 80% of value"

### Gap 6: Factor-to-Archetype Impact 🟡

**What's Missing:**
```json
{
  "factor_id": "data_quality",
  "improves_archetypes": [
    {
      "archetype": "Classification",
      "impact_score": 0.85,
      "mechanism": "Better data quality directly improves classification accuracy",
      "typical_improvement": "10-30% accuracy gain"
    },
    {
      "archetype": "Regression & Forecasting",
      "impact_score": 0.90,
      "mechanism": "Clean data reduces noise in predictions",
      "typical_improvement": "15-40% error reduction"
    }
  ]
}
```

**Why Useful:**
- Answers: "Improving data governance helps which projects?"
- Quantifies factor value: "data_quality has 0.85 impact on classification"
- Prioritizes improvement efforts
- Explains why factors matter

---

## Implementation Roadmap

### Phase 1: Core Factor Definition (Day 1-2) 🚨
**Priority:** Critical  
**Estimated Time:** 12-16 hours

**Deliverable:** `src/data/organizational_factors.json`

**Tasks:**
1. Define 15 core factors across 3 categories
2. Create 0-100 scales with 6 anchors (0, 20, 40, 60, 80, 100) per factor
3. Add scope dimensions (domain, system, team) per factor
4. Define inference hints (positive/negative indicators)
5. Add assessment metadata (time, complexity, evidence types)

**Validation:**
- [ ] All 15 factors have complete scales
- [ ] Scale anchors are observable and measurable
- [ ] Inference hints are specific and actionable
- [ ] Can map 5 test conversation excerpts to factor values

**Example Output:**
```json
{
  "factor_categories": [
    {
      "category_id": "data_readiness",
      "category_name": "Data Readiness",
      "factors": [
        {
          "factor_id": "data_quality",
          "factor_name": "Data Quality",
          "scale": { "anchors": {...} },
          "scope_dimensions": {...},
          "inference_hints": {...},
          "assessment_metadata": {...}
        }
      ]
    }
  ]
}
```

### Phase 2: Factor-to-Capability Mapping (Day 2-3) 🚨
**Priority:** Critical  
**Estimated Time:** 10-12 hours

**Deliverable:** `src/data/factor_capability_mapping.json`

**Tasks:**
1. Define 6 AI capabilities matching common archetypes
2. For each capability, specify:
   - Enabled archetypes (from AI_use_case_taxonomy.json)
   - 5-8 factor requirements with importance, threshold, weight, rationale
   - Confidence calculation formula
3. Validate weights sum to 1.0
4. Test confidence calculations with 3 scenarios

**Validation:**
- [ ] All 6 capabilities have complete factor requirements
- [ ] Weights sum to 1.0 for each capability
- [ ] Can calculate confidence for 3 test scenarios
- [ ] Confidence scores match intuition

**Example Output:**
```json
{
  "ai_capabilities": [
    {
      "capability_id": "supervised_classification",
      "enabled_archetypes": [...],
      "factor_requirements": [
        {
          "factor_id": "data_quality",
          "importance": "critical",
          "minimum_threshold": 50,
          "weight": 0.25,
          "rationale": "..."
        }
      ],
      "confidence_calculation": {...}
    }
  ]
}
```

### Phase 3: Factor Interdependencies (Day 3-4) 🔴
**Priority:** High  
**Estimated Time:** 8-10 hours

**Deliverable:** `src/data/factor_interdependencies.json`

**Tasks:**
1. Identify 10-15 key interdependencies
2. For each, define:
   - Source and target factors
   - Relationship type (mitigates/enables/reinforces/conflicts)
   - Strength (0-1)
   - Description, mechanism, examples
3. Validate no circular dependencies (or document if intentional)
4. Test interdependencies with 3 scenarios

**Validation:**
- [ ] 10-15 interdependencies defined
- [ ] All relationship types represented
- [ ] Strengths are realistic (0.2-0.6 range)
- [ ] Interdependencies make intuitive sense

### Phase 4: Prerequisite-to-Factor Mapping (Day 4) 🔴
**Priority:** High  
**Estimated Time:** 6-8 hours

**Deliverable:** Updated `src/data/AI_dependency_taxonomy.json`

**Tasks:**
1. For each of 40+ prerequisites, add:
   - Primary factor mapping (main determinant)
   - Supporting factor mappings (contributors)
   - Threshold values (when prerequisite is satisfied)
2. Validate every prerequisite maps to at least one factor
3. Test: "If data_quality = 50, is 'Clean_and_validated_data' satisfied?"

**Validation:**
- [ ] All prerequisites have factor mappings
- [ ] Thresholds are realistic (30-70 range)
- [ ] Can determine prerequisite satisfaction for 5 test cases

### Phase 5: Assessment Metadata (Day 5) 🟡
**Priority:** Medium  
**Estimated Time:** 4-6 hours

**Deliverable:** `src/data/assessment_metadata.json`

**Tasks:**
1. For each factor, estimate:
   - Typical assessment time (5-30 minutes)
   - Confidence impact by capability (0.05-0.25)
   - Assessment difficulty (low/medium/high)
   - Technical expertise required (yes/no)
   - Diminishing returns threshold (2-5 turns)
2. Validate assessment times sum to reasonable total
3. Test ROI calculations with 3 scenarios

**Validation:**
- [ ] All 15 factors have complete metadata
- [ ] Total assessment time is reasonable (2-4 hours)
- [ ] Confidence impacts align with factor importance
- [ ] ROI calculations produce sensible suggestions

### Phase 6: Factor-to-Archetype Impact (Day 6) 🟡
**Priority:** Medium  
**Estimated Time:** 4-6 hours

**Deliverable:** `src/data/factor_archetype_impact.json`

**Tasks:**
1. For each factor, identify:
   - Which archetypes it improves
   - Impact score (0-1)
   - Mechanism (how it helps)
   - Typical improvement range
2. Validate impact scores are consistent with capability mappings
3. Test: "Improving data_quality helps which projects most?"

**Validation:**
- [ ] All 15 factors have archetype impacts
- [ ] Impact scores are realistic (0.3-0.9 range)
- [ ] Can answer "which factors help X archetype?" for 5 archetypes

---

## Validation Framework

### Structural Validation
- [ ] All JSON files parse without errors
- [ ] All factor IDs are unique and stable
- [ ] All references (factor_id, capability_id, archetype) resolve correctly
- [ ] Weights sum to 1.0 where required
- [ ] Thresholds are in valid range (0-100)
- [ ] Strengths are in valid range (0-1)

### Semantic Validation
- [ ] Factor scales are monotonic (higher = better)
- [ ] Scale anchors are observable and measurable
- [ ] Factor names and descriptions are clear
- [ ] Interdependencies make intuitive sense
- [ ] Capability requirements align with domain knowledge
- [ ] Prerequisite mappings are logical

### Functional Validation
- [ ] Can infer factor values from 10 conversation excerpts
- [ ] Can calculate confidence for 5 project scenarios
- [ ] Can determine "what's next" for 5 assessment states
- [ ] Can identify missing prerequisites for 5 AI archetypes
- [ ] ROI calculations produce reasonable suggestions
- [ ] Can explain factor interactions in 3 scenarios

### Integration Validation
- [ ] Knowledge graph builder can load all new files
- [ ] Scope matcher works with factor definitions
- [ ] LLM prompts can use factor scales
- [ ] Firestore schema supports all data structures
- [ ] No breaking changes to existing code

---

## Success Criteria

### Completeness
- ✅ 15 factors fully defined with scales
- ✅ 6 capabilities mapped to factors
- ✅ 10-15 interdependencies documented
- ✅ All 40+ prerequisites linked to factors
- ✅ Assessment metadata for all factors
- ✅ Factor-to-archetype impacts defined

### Quality
- ✅ 0 structural validation errors
- ✅ 0 semantic inconsistencies
- ✅ 10/10 functional validation tests pass
- ✅ Integration tests pass

### Readiness
- ✅ Knowledge graph builder can construct complete graph
- ✅ Epic 1 can proceed with `data_quality` factor
- ✅ Epic 2 can expand to all 15 factors
- ✅ Epic 3 can implement project feasibility
- ✅ Epic 4 can implement "what's next" suggestions

---

## Risk Assessment & Mitigation

### Risk 1: Scales Too Subjective 🔴
**Impact:** LLM can't reliably infer values from conversation  
**Probability:** Medium  
**Mitigation:**
- Use observable, measurable anchors
- Test with 10 real conversation excerpts
- Iterate based on inference accuracy
- Provide inference hints to guide LLM

### Risk 2: Too Many Factors 🟡
**Impact:** Cognitive overload, assessment fatigue  
**Probability:** Low  
**Mitigation:**
- Start with 15 core factors (validated minimum)
- Use Pareto principle (20% of factors, 80% of value)
- Implement diminishing returns signaling
- Allow partial assessments

### Risk 3: Weights/Impacts Arbitrary 🟡
**Impact:** Confidence scores don't match reality  
**Probability:** Medium  
**Mitigation:**
- Start with equal weights, iterate based on tests
- Get domain expert validation
- Test with 5 real organizational scenarios
- Document rationale for all weights

### Risk 4: Interdependencies Too Complex 🟡
**Impact:** Hard to explain, maintain, validate  
**Probability:** Low  
**Mitigation:**
- Limit to 10-15 key relationships
- Document mechanism clearly
- Use simple relationship types
- Validate with intuition tests

### Risk 5: Time Estimates Wrong 🟢
**Impact:** ROI suggestions misleading  
**Probability:** Medium  
**Mitigation:**
- Provide ranges (5-15 min) instead of point estimates
- Test with real users in Epic 1
- Adjust based on feedback
- Track actual assessment times

### Risk 6: Prerequisite Mappings Incomplete 🔴
**Impact:** Cannot bridge technical requirements to factors  
**Probability:** Low  
**Mitigation:**
- Systematic review of all 40+ prerequisites
- Validate with domain experts
- Test prerequisite satisfaction logic
- Document edge cases

---

## Dependencies & Blockers

### Dependencies
- ✅ Scoped factor model design (completed)
- ✅ Scope matcher implementation (completed)
- ✅ Architecture documentation (completed)
- ✅ Existing taxonomies (AI_use_case, AI_dependency)

### Blockers (None)
- All prerequisites are met
- Can proceed immediately

### Downstream Impacts
- **Epic 1 Implementation** - Blocked until Phase 1-2 complete
- **Knowledge Graph Builder** - Blocked until Phase 1-4 complete
- **Project Feasibility** - Blocked until Phase 2 complete
- **"What's Next" Suggestions** - Blocked until Phase 5 complete

---

## Resource Requirements

### Personnel
- **Primary:** 1 person with AI/ML domain expertise
- **Validation:** 2-3 domain experts for review (2-3 hours each)
- **Total Effort:** 4-6 days (32-48 hours)

### Tools
- JSON editor with schema validation
- Python for validation scripts
- Knowledge graph visualization (optional, for validation)

### Deliverables
1. `src/data/organizational_factors.json` (new)
2. `src/data/factor_capability_mapping.json` (new)
3. `src/data/factor_interdependencies.json` (new)
4. `src/data/AI_dependency_taxonomy.json` (updated)
5. `src/data/assessment_metadata.json` (new)
6. `src/data/factor_archetype_impact.json` (new)
7. Validation test suite (Python)
8. Documentation updates

---

## Next Steps After Completion

### Immediate (Week 1)
1. Update knowledge graph builder to load new taxonomies
2. Create validation test suite
3. Update LLM prompts to use factor scales
4. Begin Epic 1 implementation with `data_quality` factor

### Short-term (Week 2-3)
1. Expand to all 15 factors in Epic 2
2. Implement project feasibility evaluation (Epic 3)
3. Build "what's next" suggestion engine (Epic 4)
4. Test with real users, iterate based on feedback

### Long-term (Month 2-3)
1. Add more factors based on usage patterns (expand to 20-25)
2. Refine weights and impacts based on real data
3. Add more capabilities (expand to 10-12)
4. Build factor improvement recommendation engine

---

## Open Questions

1. **Scope:** 15 factors sufficient for MVP, or need 20-25?
   - **Recommendation:** Start with 15, expand based on usage data

2. **Granularity:** Should factors have sub-factors, or keep flat?
   - **Recommendation:** Keep flat for MVP, consider hierarchy in v2

3. **Interdependencies:** Model as graph edges, or separate file?
   - **Recommendation:** Separate file for maintainability, load as edges in graph

4. **Validation:** Need automated tests, or manual review sufficient?
   - **Recommendation:** Both - automated for structure, manual for semantics

5. **Maintenance:** Who owns taxonomy updates after initial creation?
   - **Recommendation:** Define ownership and update process in Phase 6

6. **Versioning:** How to handle taxonomy evolution over time?
   - **Recommendation:** Semantic versioning, migration scripts for breaking changes

---

## Conclusion

This roadmap provides a clear, prioritized path to complete the taxonomy foundation needed for knowledge graph construction. The 6-phase approach balances critical needs (Phases 1-2) with important enhancements (Phases 3-4) and useful optimizations (Phases 5-6).

**Critical Path:** Phases 1-2 (Factor Definition + Capability Mapping) are sufficient to unblock Epic 1 and begin implementation.

**Estimated Timeline:**
- **Minimum Viable:** 2-3 days (Phases 1-2)
- **Recommended:** 4-5 days (Phases 1-4)
- **Complete:** 5-6 days (All phases)

**Next Action:** Review this roadmap, confirm scope and priorities, then proceed with Phase 1 (Core Factor Definition).

---

**Document Version:** 1.0  
**Created:** 2024-11-01  
**Status:** Ready for review and execution  
**Owner:** [To be assigned]
