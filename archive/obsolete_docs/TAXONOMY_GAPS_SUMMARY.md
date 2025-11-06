# Taxonomy Gaps - Quick Reference

**Status:** Superseded by Output-Centric Model (v0.3)  
**Priority:** Review Required  
**Note:** This document describes gaps for the scoped factor model. See `output_centric_factor_model_exploration.md` for evolved approach.

---

## The Problem in One Sentence

**Existing taxonomies define AI capabilities and technical prerequisites, but lack the organizational factor layer needed to assess "Can our organization do this AI project?"**

---

## What We Have ✅

1. **AI Use Case Taxonomy** - 25 AI archetypes (Classification, Forecasting, etc.)
2. **AI Dependency Taxonomy** - 40+ technical prerequisites (Clean data, ML expertise, etc.)
3. **Scoped Factor Model** - Architecture for domain/system-specific assessments

---

## What's Missing ❌

### Critical Gaps (Block Epic 1)

**1. Organizational Factors Taxonomy** 🚨 **UPDATED TO 1-5 STARS**
- **Missing:** Structured definition of output-centric factors
- **Need:** 1-5 star scales with observable anchors for each factor component
- **Impact:** Cannot infer "data_quality = ⭐⭐" from user saying "data scattered across 5 systems"
- **Example:**
  ```json
  {
    "factor_id": "output_capability",
    "output": "Sales Forecast",
    "scale": {
      "1": "⭐ Critical issues, major blockers",
      "2": "⭐⭐ Significant problems, frequent failures",
      "3": "⭐⭐⭐ Functional but inconsistent",
      "4": "⭐⭐⭐⭐ Good quality, minor issues",
      "5": "⭐⭐⭐⭐⭐ Excellent, consistent"
    },
    "components": {
      "dependency_quality": "1-5 stars",
      "team_execution": "1-5 stars",
      "process_maturity": "1-5 stars",
      "system_support": "1-5 stars"
    },
    "calculation": "MIN(components)"  
  }
  ```

**2. Factor-to-Capability Mapping** 🚨 **SIMPLIFIED WITH MIN LOGIC**
- **Missing:** How output-centric factors determine AI pilot feasibility
- **Need:** MIN-based bottleneck identification, no complex weights
- **Impact:** Cannot evaluate "Can we improve sales forecasting?" from assessed output factors
- **Example:**
  ```json
  {
    "output": "Sales Forecast",
    "current_capability": 2,
    "components": [
      {"component": "dependency_quality", "value": 3},
      {"component": "team_execution", "value": 3},
      {"component": "process_maturity", "value": 2},
      {"component": "system_support", "value": 2}
    ],
    "calculation": "MIN(3, 3, 2, 2) = 2 stars",
    "bottlenecks": ["process_maturity", "system_support"]
  }
  ```

### High Priority Gaps

**3. Factor Interdependencies** 🔴
- **Missing:** How factors influence each other
- **Impact:** Cannot model "executive support mitigates expertise gaps"

**4. Prerequisite-to-Factor Mapping** 🔴
- **Missing:** Link between technical prerequisites and organizational factors
- **Impact:** Cannot determine "Is 'Clean_and_validated_data' satisfied?"

### Medium Priority Gaps

**5. Assessment Metadata** 🟡
- **Missing:** Time-to-assess, confidence impact, ROI data
- **Impact:** Cannot prioritize "what's next" suggestions

**6. Factor-to-Archetype Impact** 🟡
- **Missing:** Which factors improve which archetypes
- **Impact:** Cannot answer "Improving data governance helps which projects?"

---

## Why This Blocks Knowledge Graph

**Current graph structure:**
```
AI_ARCHETYPE → PREREQUISITE → MODEL → OUTPUT
```

**Required graph structure:**
```
CONVERSATION → FACTOR → PREREQUISITE → CAPABILITY → ARCHETYPE
                ↓           ↓              ↓
            FACTOR_SCALE  FACTOR_MAP   CONFIDENCE
```

**Missing edges:** All connections involving FACTOR nodes

---

## The Fix: 6-Phase Roadmap

### Release 1-2: Minimum Viable (2-3 days) 🚨
- Define 15 factors with scales
- Map factors to 6 capabilities
- **Unblocks:** Epic 1 implementation

### Phase 3-4: Recommended (4-5 days) 🔴
- Add factor interdependencies
- Link prerequisites to factors
- **Unblocks:** Full knowledge graph, project feasibility

### Phase 5-6: Complete (5-6 days) 🟡
- Add assessment metadata
- Add factor-archetype impacts
- **Unblocks:** ROI suggestions, factor improvement recommendations

---

## 15 Core Factors to Define

### Data Readiness (5)
1. data_quality
2. data_availability
3. data_governance
4. data_infrastructure
5. data_security

### AI Capability (5)
6. ml_infrastructure
7. ml_expertise
8. ml_tooling
9. experimentation_culture
10. model_lifecycle_management

### Organizational Readiness (5)
11. executive_support
12. change_management
13. cross_functional_collaboration
14. risk_tolerance
15. business_process_maturity

---

## Example: What Each Factor Needs

```json
{
  "factor_id": "data_quality",
  "factor_name": "Data Quality",
  "category": "data_readiness",
  
  "scale": {
    "type": "1-5 stars",
    "anchors": {
      "1": "⭐ No quality controls, data unreliable",
      "2": "⭐⭐ Ad-hoc checks, many known issues",
      "3": "⭐⭐⭐ Basic processes, some validation",
      "4": "⭐⭐⭐⭐ Systematic framework, automated checks",
      "5": "⭐⭐⭐⭐⭐ World-class quality, real-time monitoring"
    }
  },
  
  "scope_dimensions": {
    "domain": {"required": false, "common_values": ["sales", "finance"]},
    "system": {"required": false, "allow_custom": true}
  },
  
  "inference_hints": {
    "positive_indicators": ["automated validation", "quality dashboard", "SLAs"],
    "negative_indicators": ["scattered data", "no catalog", "duplicates"]
  },
  
  "assessment_metadata": {
    "typical_time_minutes": 10,
    "complexity": "medium",
    "requires_technical_knowledge": false
  }
}
```

---

## Validation Checklist

### For Each Factor (Output-Centric Model)
- [ ] Has 1-5 star scale with clear definitions
- [ ] Anchors are observable and measurable
- [ ] Has inference hints (positive and negative indicators)
- [ ] Tied to specific Output + Team + Process + System
- [ ] Has 4 components: Dependency Quality, Team Execution, Process Maturity, System Support
- [ ] Uses MIN() calculation to identify bottlenecks
- [ ] Can map 2-3 conversation excerpts to star ratings

### For Each Output Capability
- [ ] Identifies target output
- [ ] Has 4 component assessments (1-5 stars each)
- [ ] Uses MIN() to calculate overall capability
- [ ] Identifies bottleneck component(s)
- [ ] Can recommend improvement focus (weakest link)

### For Each Interdependency
- [ ] Has clear relationship type (mitigates/enables/reinforces/conflicts)
- [ ] Strength is realistic (0.2-0.6 range)
- [ ] Has concrete examples
- [ ] Makes intuitive sense

---

## Files to Create

1. **`src/data/organizational_factors.json`** (NEW) - 15 factors with scales
2. **`src/data/factor_capability_mapping.json`** (NEW) - 6 capabilities
3. **`src/data/factor_interdependencies.json`** (NEW) - 10-15 relationships
4. **`src/data/AI_dependency_taxonomy.json`** (UPDATE) - Add factor mappings
5. **`src/data/assessment_metadata.json`** (NEW) - ROI data
6. **`src/data/factor_archetype_impact.json`** (NEW) - Impact scores

---

## Quick Decision Matrix

| Scope | Time | What You Get | Unblocks |
|-------|------|--------------|----------|
| **Minimum** (Phases 1-2) | 2-3 days | 15 factors + 6 capabilities | Epic 1 |
| **Recommended** (Phases 1-4) | 4-5 days | + interdependencies + prerequisite links | Full KG, Epic 2-3 |
| **Complete** (All phases) | 5-6 days | + ROI data + impact scores | Epic 4, full features |

---

## Next Actions

1. **Review** - Confirm scope (minimum/recommended/complete)
2. **Assign** - Who will execute the phases?
3. **Execute** - Begin Release 1 (Core Factor Definition)

**Detailed roadmap:** See `docs/taxonomy_enrichment_roadmap.md`

---

**Last Updated:** 2025-11-01 21:45  
**Status:** Superseded by Output-Centric Model (see `output_centric_factor_model_exploration.md` v0.3)  
**Key Changes:** 
- 0-100 scales → 1-5 star ratings
- Weighted averages → MIN() bottleneck identification
- Abstract factors → Output-centric capability assessment
- Scoped factors → Output + Team + Process + System context
