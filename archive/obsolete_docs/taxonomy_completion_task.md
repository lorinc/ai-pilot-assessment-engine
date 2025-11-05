# Taxonomy Completion Task - Pre-Epic 1 Foundation

**Status:** Planning  
**Priority:** Blocker for Epic 1 implementation  
**Estimated Time:** 3-5 days

---

## Problem Statement

The existing taxonomies (`AI_use_case_taxonomy.json`, `AI_dependency_taxonomy.json`) are **structurally sound but functionally incomplete** for implementing the conversational assessment system. They define WHAT exists (archetypes, prerequisites) but not HOW these elements interact in the context of organizational AI readiness assessment.

### Critical Gaps Identified

1. **Missing Organizational Factors** - No structured definition of the factors users will assess
2. **No Factor Scales** - Can't infer "data_quality = 20" without 0-100 scale definitions
3. **No Factor-to-Capability Mapping** - How do factors combine to enable project types?
4. **No Factor Weights/Impacts** - Which factors are critical vs. nice-to-have for each archetype?
5. **No Factor Interdependencies** - How factors influence each other (e.g., CxO support mitigates technical gaps)
6. **No Assessment Metadata** - Time to assess, confidence impact, typical values
7. **Incomplete Prerequisite-to-Factor Mapping** - Prerequisites exist but don't link to organizational factors

---

## Task Goal

**Create a complete, implementation-ready factor taxonomy that enables:**

1. **Conversational inference** - LLM can map user statements to factor values (0-100)
2. **Confidence calculation** - System can determine "how sure are we?" for each factor
3. **Project feasibility** - System can evaluate "can we do X?" based on assessed factors
4. **ROI-driven suggestions** - System can recommend "assess Y next for +15% confidence"
5. **Factor synthesis** - System can explain "data_quality = 20 because: scattered data, no catalog, duplicates"

---

## Deliverables

### 1. Organizational Factor Taxonomy (NEW)
**File:** `src/data/organizational_factors.json`

**Structure:**
```json
{
  "factor_categories": [
    {
      "category_id": "data_readiness",
      "category_name": "Data Readiness",
      "description": "Organization's data infrastructure and quality",
      "factors": [
        {
          "factor_id": "data_quality",
          "factor_name": "Data Quality",
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
          "assessment_metadata": {
            "typical_assessment_time_minutes": 10,
            "complexity": "medium",
            "requires_technical_knowledge": false,
            "typical_evidence": [
              "Data quality reports",
              "Error rates",
              "Data validation processes",
              "Quality incident history"
            ]
          },
          "inference_hints": {
            "positive_indicators": [
              "automated validation",
              "data quality dashboard",
              "quality SLAs",
              "data steward role"
            ],
            "negative_indicators": [
              "scattered data",
              "no data catalog",
              "frequent duplicates",
              "manual data cleaning"
            ]
          }
        }
      ]
    }
  ]
}
```

**Required Factors (minimum for Epic 1-2):**

**Data Readiness (5 factors):**
- `data_quality` - Quality, consistency, reliability
- `data_availability` - Volume, coverage, accessibility
- `data_governance` - Policies, ownership, compliance
- `data_infrastructure` - Storage, processing, pipelines
- `data_security` - Access controls, privacy, encryption

**AI Capability (5 factors):**
- `ml_infrastructure` - Compute, MLOps, deployment
- `ml_expertise` - Team skills, experience, training
- `ml_tooling` - Frameworks, platforms, monitoring
- `experimentation_culture` - Testing, iteration, learning
- `model_lifecycle_management` - Versioning, monitoring, retraining

**Organizational Readiness (5 factors):**
- `executive_support` - CxO buy-in, budget, priority
- `change_management` - Adoption processes, training, communication
- `cross_functional_collaboration` - Data science + business alignment
- `risk_tolerance` - Willingness to experiment, fail fast
- `business_process_maturity` - Documented, measured, optimized

### 2. Factor-to-Capability Mapping (NEW)
**File:** `src/data/factor_capability_mapping.json`

**Purpose:** Define how factors combine to enable project types

**Structure:**
```json
{
  "ai_capabilities": [
    {
      "capability_id": "supervised_classification",
      "capability_name": "Supervised Classification Projects",
      "description": "Ability to build and deploy classification models",
      "enabled_archetypes": [
        "Content Analysis / Labeling / Evaluation",
        "Classification & Categorization",
        "Predictive Classification"
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
        },
        {
          "factor_id": "ml_infrastructure",
          "importance": "important",
          "minimum_threshold": 40,
          "weight": 0.15,
          "rationale": "Can start with cloud services, doesn't need custom infrastructure"
        },
        {
          "factor_id": "executive_support",
          "importance": "nice-to-have",
          "minimum_threshold": 30,
          "weight": 0.10,
          "rationale": "Helpful for resources but not blocking"
        }
      ],
      "confidence_calculation": {
        "formula": "weighted_average",
        "minimum_confidence_threshold": 0.60,
        "notes": "Confidence = Σ(factor_value * weight) / 100, adjusted by number of assessed factors"
      }
    }
  ]
}
```

**Required Capabilities (minimum for Epic 2-3):**
- Supervised Classification
- Regression & Forecasting
- Anomaly Detection
- Clustering & Segmentation
- Natural Language Processing
- Generative AI

### 3. Factor Interdependencies (NEW)
**File:** `src/data/factor_interdependencies.json`

**Purpose:** Define how factors influence each other

**Structure:**
```json
{
  "interdependencies": [
    {
      "source_factor": "executive_support",
      "target_factor": "ml_expertise",
      "relationship_type": "mitigates_gap",
      "strength": 0.30,
      "description": "Strong executive support can compensate for expertise gaps by providing time and budget for learning",
      "mechanism": "budget_for_training",
      "examples": [
        "CxO approves 6-month learning period",
        "Budget for external consultants",
        "Protected time for experimentation"
      ]
    },
    {
      "source_factor": "data_governance",
      "target_factor": "data_quality",
      "relationship_type": "enables",
      "strength": 0.60,
      "description": "Strong governance directly improves data quality through policies and processes",
      "mechanism": "systematic_improvement",
      "examples": [
        "Data quality SLAs enforced",
        "Automated validation rules",
        "Data steward accountability"
      ]
    },
    {
      "source_factor": "experimentation_culture",
      "target_factor": "risk_tolerance",
      "relationship_type": "reinforces",
      "strength": 0.40,
      "description": "Culture of experimentation increases organizational risk tolerance",
      "mechanism": "normalized_failure",
      "examples": [
        "Fail-fast mentality",
        "Learning from experiments",
        "Celebrating informed risk-taking"
      ]
    }
  ]
}
```

**Relationship Types:**
- `mitigates_gap` - Source compensates for weakness in target
- `enables` - Source is prerequisite for target
- `reinforces` - Source amplifies target
- `conflicts_with` - Source undermines target (e.g., siloed culture vs. collaboration)

### 4. Enhanced AI Dependency Taxonomy (UPDATE EXISTING)
**File:** `src/data/AI_dependency_taxonomy.json`

**Add to each prerequisite:**
```json
{
  "prerequisite_id": "Clean_and_validated_data",
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

### 5. Assessment Time & Confidence Impact (NEW)
**File:** `src/data/assessment_metadata.json`

**Purpose:** Enable ROI-driven "what's next" suggestions

**Structure:**
```json
{
  "factor_assessment_metadata": [
    {
      "factor_id": "data_quality",
      "typical_assessment_time_minutes": 10,
      "confidence_impact_by_capability": {
        "supervised_classification": 0.15,
        "regression_forecasting": 0.18,
        "anomaly_detection": 0.12,
        "clustering_segmentation": 0.10
      },
      "assessment_difficulty": "medium",
      "requires_technical_expert": false,
      "can_be_partially_assessed": true,
      "diminishing_returns_threshold": 3,
      "notes": "After 3 conversation turns, additional detail provides <5% confidence gain"
    }
  ]
}
```

---

## Implementation Path

### Phase 1: Core Factor Definition (Day 1-2)

**Goal:** Define 15 core factors with complete scales

**Tasks:**
1. **Select 15 factors** across 3 categories (5 each)
   - Data Readiness: quality, availability, governance, infrastructure, security
   - AI Capability: infrastructure, expertise, tooling, culture, lifecycle
   - Organizational: executive support, change mgmt, collaboration, risk tolerance, process maturity

2. **For each factor, define:**
   - Unique ID (stable, semantic)
   - Display name and description
   - 0-100 scale with 6 anchors (0, 20, 40, 60, 80, 100)
   - Assessment metadata (time, complexity, evidence types)
   - Inference hints (positive/negative indicators)

3. **Validation:**
   - Substitution test: Can all factors be used in "We need to assess [FACTOR]"?
   - Abstraction consistency: All at same conceptual level?
   - Scale clarity: Can you place real organizations on each scale?

**Deliverable:** `organizational_factors.json` with 15 complete factor definitions

### Phase 2: Factor-to-Capability Mapping (Day 2-3)

**Goal:** Define how factors enable 6 AI capabilities

**Tasks:**
1. **Select 6 capabilities** matching common AI archetypes
   - Supervised Classification
   - Regression & Forecasting
   - Anomaly Detection
   - Clustering & Segmentation
   - Natural Language Processing
   - Generative AI

2. **For each capability, define:**
   - Which archetypes it enables
   - 5-8 factor requirements with:
     - Importance (critical/important/nice-to-have)
     - Minimum threshold (0-100)
     - Weight (sum to 1.0)
     - Rationale (why this factor matters)
   - Confidence calculation formula

3. **Validation:**
   - Do weights sum to 1.0?
   - Are critical factors actually critical? (test with edge cases)
   - Can you calculate confidence for real scenarios?

**Deliverable:** `factor_capability_mapping.json` with 6 capability definitions

### Phase 3: Factor Interdependencies (Day 3-4)

**Goal:** Define 10-15 key interdependencies

**Tasks:**
1. **Identify interdependencies:**
   - Mitigations: What compensates for what? (e.g., executive support → expertise gap)
   - Enablers: What's prerequisite for what? (e.g., governance → quality)
   - Reinforcements: What amplifies what? (e.g., culture → risk tolerance)
   - Conflicts: What undermines what? (e.g., silos → collaboration)

2. **For each interdependency, define:**
   - Source and target factors
   - Relationship type
   - Strength (0-1, how much influence)
   - Description and mechanism
   - Concrete examples

3. **Validation:**
   - Do interdependencies make intuitive sense?
   - Are strengths realistic? (test with scenarios)
   - Any circular dependencies? (should be rare, document if intentional)

**Deliverable:** `factor_interdependencies.json` with 10-15 interdependencies

### Phase 4: Prerequisite-to-Factor Mapping (Day 4)

**Goal:** Link existing prerequisites to organizational factors

**Tasks:**
1. **For each prerequisite in `AI_dependency_taxonomy.json`:**
   - Identify primary factor (main determinant)
   - Identify supporting factors (contribute but not primary)
   - Define threshold (factor value where prerequisite is satisfied)

2. **Validation:**
   - Does every prerequisite map to at least one factor?
   - Are thresholds realistic?
   - Test: "If data_quality = 50, is 'Clean_and_validated_data' satisfied?" → Should make sense

**Deliverable:** Updated `AI_dependency_taxonomy.json` with factor mappings

### Phase 5: Assessment Metadata (Day 5)

**Goal:** Enable ROI-driven suggestions

**Tasks:**
1. **For each factor, estimate:**
   - Typical assessment time (5-30 minutes)
   - Confidence impact by capability (0.05-0.25)
   - Assessment difficulty (low/medium/high)
   - Technical expertise required (yes/no)
   - Diminishing returns threshold (2-5 conversation turns)

2. **Validation:**
   - Do assessment times sum to reasonable total? (15 factors × 10 min = 2.5 hours)
   - Do confidence impacts make sense? (critical factors = higher impact)
   - Test ROI calculation: "Assess data_quality (10 min) → +15% confidence" → Reasonable?

**Deliverable:** `assessment_metadata.json` with complete metadata

---

## Validation Criteria

### Structural Validation
- [ ] All JSON files parse without errors
- [ ] All factor IDs are unique and stable
- [ ] All references (factor_id, capability_id) resolve correctly
- [ ] Weights sum to 1.0 where required
- [ ] Thresholds are in valid range (0-100)

### Semantic Validation
- [ ] Factor scales are monotonic (higher = better, consistently)
- [ ] Scale anchors are observable and measurable
- [ ] Factor names and descriptions are clear and actionable
- [ ] Interdependencies make intuitive sense
- [ ] Capability requirements align with domain knowledge

### Functional Validation
- [ ] Can calculate confidence for 3 test scenarios
- [ ] Can determine "what's next" for 3 test scenarios
- [ ] Can explain factor values from conversation excerpts
- [ ] Can identify missing prerequisites for 3 AI archetypes
- [ ] ROI calculations produce reasonable suggestions

### Domain Expert Validation
- [ ] 2-3 domain experts review factor definitions
- [ ] Test with 3 real organizational scenarios
- [ ] Validate that confidence scores match expert intuition
- [ ] Confirm that interdependencies reflect real-world dynamics

---

## Success Metrics

**Completeness:**
- 15 factors fully defined with scales
- 6 capabilities mapped to factors
- 10-15 interdependencies documented
- All prerequisites linked to factors
- Assessment metadata for all factors

**Quality:**
- 0 structural validation errors
- 0 semantic inconsistencies
- 3/3 functional validation tests pass
- 2/3 domain experts approve

**Readiness:**
- Epic 1 can proceed with `data_quality` factor
- Epic 2 can expand to 10-15 factors
- Epic 3 can implement project feasibility
- Epic 4 can implement "what's next" suggestions

---

## Risks & Mitigation

### Risk 1: Scales Too Subjective
**Impact:** LLM can't reliably infer values  
**Mitigation:** Use observable anchors, test with real conversation excerpts

### Risk 2: Too Many Factors
**Impact:** Cognitive overload, assessment fatigue  
**Mitigation:** Start with 15, validate before expanding, use Pareto principle

### Risk 3: Weights/Impacts Arbitrary
**Impact:** Confidence scores don't match reality  
**Mitigation:** Start with equal weights, iterate based on test scenarios, get expert input

### Risk 4: Interdependencies Too Complex
**Impact:** Hard to explain, maintain, validate  
**Mitigation:** Limit to 10-15 key relationships, document mechanism clearly

### Risk 5: Time Estimates Wrong
**Impact:** ROI suggestions misleading  
**Mitigation:** Test with real users, adjust based on feedback, provide ranges

---

## Next Steps After Completion

1. **Update Epic 1 scope** - Confirm `data_quality` factor is complete
2. **Create graph builder update** - Load new taxonomy files
3. **Write unit tests** - Validate taxonomy loading and queries
4. **Document for LLM** - Create prompt templates using factor scales
5. **Begin Epic 1 implementation** - Now unblocked

---

## Questions to Resolve

1. **Scope:** 15 factors sufficient for MVP, or need 20-25?
2. **Granularity:** Should factors have sub-factors, or keep flat?
3. **Interdependencies:** Model as graph edges, or separate file?
4. **Validation:** Need automated tests, or manual review sufficient?
5. **Maintenance:** Who owns taxonomy updates after initial creation?

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-30  
**Status:** Ready for review and execution
