# Architecture Documentation Update: Scoped Factor Model

**Date:** 2024-10-31  
**Time:** 23:07 UTC+01:00  
**Task:** Task 1 from docs/next_tasks.md  
**Status:** Completed

---

## Overview

Updated all four core architecture documents to reflect the **Scoped Factor Model** as specified in `docs/scoped_factor_model.md`. This represents a fundamental shift from organization-wide factor assessments to multi-level scoped instances.

---

## Key Changes

### 1. Core Concept Shift

**Before:**
- Factors had single organization-wide values
- `data_quality = 20` applied to entire organization
- No way to represent domain/system-specific reality

**After:**
- Factors have multiple scoped instances
- `data_quality {domain: "sales", system: "salesforce_crm"} = 30`
- `data_quality {domain: "finance", system: "sap_erp"} = 85`
- Intelligent scope matching finds most applicable instance

---

## Documents Updated

### 1. architecture_summary.md

**Changes:**
- Updated "Factor-Centric Design" principle to include scoped instances
- Added scope matching explanation to "Cumulative Inference" section
- Updated data flow example to show scope matching in context retrieval
- Modified knowledge tree visualization to show hierarchical scoped instances
- Updated component contracts to use `FactorInstanceStore` instead of `FactorJournalStore`
- Added `ScopeMatcher` to ContextBuilder contract

**Key Additions:**
```
Scope Matching Examples:
- Exact match: Query for "sales/Salesforce" finds exact instance (confidence: 1.0)
- Generic fallback: Query for "sales/data_warehouse" falls back to "sales/all systems" (confidence: 0.86)
- No match: Query for "manufacturing" returns None if not assessed
```

### 2. gcp_data_schemas.md

**Changes:**
- Replaced `/users/{user_id}/factors/{factor_id}` collection
- Added `/users/{user_id}/factor_instances/{instance_id}` collection
- Added `/users/{user_id}/scope_registry/metadata` collection
- Updated Firestore indexes for scope-based queries
- Added `FactorScope`, `FactorInstance`, and `ScopeMatch` data classes
- Updated `FactorInference` to include scope and specificity
- Modified LLM prompts to include scope inference

**New Schema Structure:**
```
factor_instances/{instance_id}/
  - instance_id: "dq_sales_sfdc_002"
  - factor_id: "data_quality"
  - scope: {domain: "sales", system: "salesforce_crm", team: null}
  - scope_label: "Salesforce CRM"
  - value: 30
  - confidence: 0.80
  - evidence: [...]
  - refines: "dq_sales_generic_001"
  - refined_by: []
  - synthesized_from: []
```

**New Indexes:**
- `factor_instances` by `factor_id` + `updated_at`
- `factor_instances` by `scope.domain` + `factor_id`
- `factor_instances` by `scope.system` + `factor_id`

### 3. exploratory_assessment_architecture.md

**Changes:**
- Updated cumulative inference section to use scope matching
- Added `get_applicable_instance()` function with scope matching algorithm
- Modified synthesis prompts to include scope context
- Updated status/summary responses to show scoped instances hierarchically
- Changed `FactorJournalStore` to `FactorInstanceStore` with scope parameters
- Updated conversation memory integration to use scope-aware retrieval
- Modified all examples to show domain/system-specific assessments

**Key Algorithm Addition:**
```python
def get_applicable_instance(factor_id, needed_scope, user_id):
    """Find most specific applicable instance using scope matching"""
    instances = get_factor_instances(factor_id, user_id)
    candidates = []
    
    for instance in instances:
        match_score = calculate_scope_match(instance.scope, needed_scope)
        if match_score > 0:
            candidates.append((instance, match_score))
    
    # Return most specific match (highest score, then highest confidence)
    candidates.sort(key=lambda x: (x[1], x[0].confidence), reverse=True)
    return candidates[0][0] if candidates else None
```

### 4. gcp_technical_architecture.md

**Changes:**
- Updated context retrieval flow to include scope matching step
- Modified component contracts to use `FactorInstanceStore`
- Added `ScopeMatcher` to ContextBuilder contract
- Updated security rules to include `factor_instances` and `scope_registry` collections
- Modified lookup pattern to show scope matching workflow
- Updated performance metrics to include scope matching calculation time

**New Contract Methods:**
```python
# FactorInstanceStore
await instance_store.update_factor_instance(
    factor_id="data_quality",
    scope={"domain": "sales", "system": "salesforce_crm", "team": None},
    new_value=30,
    ...
)

instance = await instance_store.get_applicable_instance(
    factor_id="data_quality",
    needed_scope={"domain": "sales", "system": "salesforce_crm"}
)
```

---

## Impact Assessment

### Breaking Changes
- **Firestore Schema:** Collection name changed from `factors` to `factor_instances`
- **Data Structure:** Factor documents now require `scope` field
- **API Contracts:** All factor CRUD operations now require scope parameter
- **Component Names:** `FactorJournalStore` → `FactorInstanceStore`

### New Components Required
1. **ScopeMatcher** - Implements scope matching algorithm
2. **Scope Registry** - Tracks known domains, systems, teams
3. **Instance ID Generator** - Creates unique IDs for scoped instances

### Performance Considerations
- Scope matching adds <1ms overhead (in-memory calculation)
- Firestore queries now filter by `factor_id` + `scope.domain`/`scope.system`
- Total context assembly remains <100ms for typical queries

---

## Implementation Readiness

### Ready for Implementation
✅ All architecture documents updated and consistent  
✅ Data schemas defined with Firestore indexes  
✅ Component contracts specified  
✅ Security rules updated  
✅ Performance characteristics documented  

### Next Steps (from next_tasks.md)
1. **Task 2:** Update UX guidelines with clarifying question patterns
2. **Task 4:** Update taxonomy files (organizational_factors.json, scope_registry_template.json)
3. **Task 7:** Update graph builder to load scoped factor definitions
4. **Task 6:** Implement scope matching logic (src/knowledge/scope_matcher.py)
5. **Task 5:** Update Epic 1 specification with scoped factor flow

---

## Examples of Scoped Factor Usage

### Example 1: Sales Forecasting Project
```
User: "Can we do sales forecasting?"

System determines needed scope: {domain: "sales", system: null}

Scope matching retrieves:
- data_quality[sales] = 45 (generic sales, match_score: 1.0)
  - Refined by: data_quality[sales/salesforce_crm] = 30
- data_availability[sales] = 80 (match_score: 1.0)

Response: "Based on your sales data: data quality is moderate (45%), 
but specifically in Salesforce it's lower (30%). Data availability is strong (80%)."
```

### Example 2: Cross-Project Reuse
```
[Discussion 1: Sales Forecasting]
User: "Salesforce data is incomplete"
→ Stores: data_quality {domain: "sales", system: "salesforce_crm"} = 35

[Discussion 2: CRM Data Quality - Days Later]
User: "What about improving our CRM data quality?"
→ Retrieves existing: data_quality[sales/salesforce_crm] = 35
→ Response: "We already identified Salesforce CRM data quality is around 35% 
   (incomplete data from sales forecasting discussion). Improving this could 
   enable multiple projects..."
```

---

## Validation

### Document Consistency Check
✅ All four documents use consistent terminology  
✅ Data structures match across documents  
✅ Component contracts align  
✅ Examples use same scope format: `{domain, system, team}`  
✅ Firestore paths consistent: `/users/{user_id}/factor_instances/{instance_id}`  

### Alignment with scoped_factor_model.md
✅ Scope dimensions: domain, system, team  
✅ Scope matching algorithm matches specification  
✅ Instance relationships: refines, refined_by, synthesized_from  
✅ Evidence structure with specificity tracking  
✅ Clarifying question patterns referenced  

---

## Technical Debt & Future Work

### Deferred to Later Tasks
- Clarifying question generation logic (Task 2)
- KG-based unknown system detection (Task 3)
- Scope registry template and common values (Task 4)
- Actual implementation of ScopeMatcher (Task 6)

### Potential Optimizations
- Caching of scope matching results
- Precomputed match scores for common queries
- Scope registry learning from user mentions
- Automatic scope detection using NER

---

## Summary

Successfully updated all four core architecture documents to reflect the scoped factor model. The system can now:

1. **Assess factors at multiple levels of specificity** - organization-wide, domain-secific, system-specific, team-specific
2. **Intelligently match scopes** - find most applicable instance using fallback hierarchy
3. **Maintain organizational truth** - assessments discovered in one context apply to all relevant contexts
4. **Support cross-project reuse** - factor instances persist across conversations and project discussions

The architecture is now ready for implementation, with clear component contracts, data schemas, and security rules defined.

---

**Estimated Implementation Time:** 12-15 hours for core tasks (Tasks 4, 6, 7)  
**Document Version:** All updated to reflect scoped factor model v1.0  
**Next Task:** Task 2 - Update UX Guidelines
