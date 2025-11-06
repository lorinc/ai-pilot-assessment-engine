# Documentation Audit - November 4, 2025

## Purpose
Identify obsolete documentation and salvage still-relevant decisions before creating new scaffolding aligned with output-centric factor model.

---

## 🔴 OBSOLETE - Contradicts Output-Centric Model

### `/poc/IMPLEMENTATION_STATUS.md`
**Status:** OBSOLETE - Phase-based flow  
**Why:** Describes 4-phase conversation flow (Discovery → Assessment → Gap Analysis → Recommendations) which contradicts the output-centric model's single-conversation approach  
**Salvage:**
- ✅ Test statistics (165 tests, 92.89% coverage)
- ✅ File structure and dependencies
- ✅ Mock mode configuration
- ✅ GCP project details
- ❌ Release 2-4 task descriptions (wrong model)

### `/docs/2_technical_spec/scoped_factor_model.md`
**Status:** OBSOLETE - Abstract factors  
**Why:** Describes abstract organizational factors (e.g., "data_quality = 65") not tied to specific outputs  
**Salvage:**
- ✅ Scoping concept (domain/system/team)
- ✅ Confidence tracking patterns
- ❌ Factor calculation approach (superseded by MIN())

### `/docs/2_technical_spec/exploratory_assessment_architecture.md`
**Status:** OBSOLETE - Old architecture  
**Why:** Likely describes pre-output-centric architecture  
**Action:** Review for infrastructure decisions

### `/docs/2_technical_spec/entity_relationship_model.md`
**Status:** NEEDS REVIEW  
**Why:** May contain entity definitions that conflict with output-centric model  
**Action:** Check if entities align with Output/Factor/Component structure

### `/docs/2_technical_spec/kg_based_question_inference.md`
**Status:** NEEDS REVIEW  
**Why:** Question inference may still be relevant for component assessment  
**Action:** Extract question patterns for 4-component diagnostic

---

## 🟡 PARTIALLY OBSOLETE - Contains Salvageable Content

### `/docs/1_functional_spec/domain_model.md`
**Status:** PARTIALLY OBSOLETE  
**Why:** Domain model may predate output-centric shift  
**Salvage:**
- ✅ Entity definitions (if they map to Output/Team/Process/System)
- ✅ Relationship patterns
- ❌ Abstract factor definitions

### `/docs/1_functional_spec/static_knowledge_graph_guide.md`
**Status:** PARTIALLY OBSOLETE  
**Why:** KG structure may need updating for output-centric model  
**Salvage:**
- ✅ Root cause → AI solution mappings
- ✅ Pilot catalog structure
- ✅ Inference rules format
- ❌ Factor relationship definitions (if abstract)

### `/docs/2_technical_spec/POC_TECHNICAL_SPEC.md`
**Status:** PARTIALLY OBSOLETE  
**Why:** Technical spec may describe old conversation flow  
**Salvage:**
- ✅ Infrastructure requirements
- ✅ API design patterns
- ✅ Data persistence strategy
- ❌ Conversation flow diagrams (if release-based)

### `/docs/2_technical_spec/gcp_data_schemas.md`
**Status:** PARTIALLY OBSOLETE  
**Why:** Schemas may need updating for output-centric data model  
**Salvage:**
- ✅ Database infrastructure decisions
- ✅ Schema patterns
- ❌ Factor storage schema (if abstract)

### `/docs/2_technical_spec/gcp_technical_architecture.md`
**Status:** PARTIALLY OBSOLETE  
**Why:** Architecture may be sound, but data flow may need updates  
**Salvage:**
- ✅ GCP service choices (Vertex AI, Firestore, etc.)
- ✅ Security patterns
- ✅ Deployment strategy
- ❌ Data flow diagrams (if based on old model)

---

## ✅ STILL RELEVANT - Aligns with Output-Centric Model

### `/docs/2_technical_spec/output_centric_factor_model_exploration.md`
**Status:** ✅ CURRENT - Primary design document  
**Why:** Defines the output-centric model with scope lock and constraints  
**Use:** Foundation for all new documentation

### `/docs/1_functional_spec/TBD.md`
**Status:** ✅ CURRENT - Design constraints  
**Why:** Contains critical UX patterns and constraints:
- TBD #11: Anti-abstract pattern
- TBD #12: Output-Team-System-Process constraint
- TBD #13: Numbered question format
- TBD #14: Professional reflection (no empathy)
**Use:** UX guidelines for implementation

### `/docs/1_functional_spec/user_interaction_guideline.md`
**Status:** ✅ MOSTLY CURRENT - UX patterns  
**Why:** Core interaction principles still valid:
- LLM generates, user validates
- Simple language (1-5 stars, not 0-100)
- Minimal questions
- Context accumulates
**Needs Update:**
- Remove references to abstract factors
- Update examples to output-centric model
- Simplify to match single-conversation flow

### `/docs/1_functional_spec/VERTICAL_EPICS.md`
**Status:** NEEDS REVIEW  
**Why:** May contain implementation epics  
**Action:** Check if epics align with output-centric increments

### `/docs/2_technical_spec/DEPLOYMENT_GUIDE.md`
**Status:** ✅ CURRENT - Infrastructure  
**Why:** Deployment details are model-agnostic  
**Use:** Reference for production deployment

### `/docs/2_technical_spec/architecture_summary.md`
**Status:** NEEDS REVIEW  
**Why:** May contain high-level architecture still relevant  
**Action:** Extract infrastructure decisions

### `/docs/2_technical_spec/system_interactions.md`
**Status:** NEEDS REVIEW  
**Why:** System interaction patterns may still apply  
**Action:** Check if interaction patterns align with new flow

---

## 📁 CHANGELOG - Historical Reference

### All files in `/docs/3_changelog/`
**Status:** ✅ ARCHIVE - Historical record  
**Why:** Documents evolution, useful for understanding decisions  
**Use:** Reference only, do not update

**Key Changelogs:**
- `2025-11-01-2125-scope-lock-simplification.md` - Scope lock decisions
- `2025-11-01-0008-taxonomy-enrichment-roadmap.md` - Taxonomy structure
- `2025-10-31-scoped-factor-model-implementation.md` - Scoped factors (superseded)

---

## 🗑️ OBSOLETE FOLDER - Already Archived

### All files in `/docs/obsolete/`
**Status:** ✅ ARCHIVED  
**Why:** Already moved to obsolete, no action needed  
**Use:** Historical reference only

---

## Summary

### Immediate Actions

1. **Mark as OBSOLETE:**
   - `/poc/IMPLEMENTATION_STATUS.md` (Phase-based flow)
   - `/docs/2_technical_spec/scoped_factor_model.md` (Abstract factors)

2. **Review and Salvage:**
   - `/docs/2_technical_spec/POC_TECHNICAL_SPEC.md` (Infrastructure)
   - `/docs/2_technical_spec/gcp_data_schemas.md` (Schema patterns)
   - `/docs/2_technical_spec/gcp_technical_architecture.md` (GCP decisions)
   - `/docs/1_functional_spec/domain_model.md` (Entity definitions)
   - `/docs/1_functional_spec/static_knowledge_graph_guide.md` (KG structure)

3. **Update to Align:**
   - `/docs/1_functional_spec/user_interaction_guideline.md` (Remove abstract factor references)

4. **Create New:**
   - `/docs/CONCEPT.md` - High-level output-centric model explanation
   - `/docs/DECISION_FLOW.md` - Conversation flow and decision tree
   - `/docs/IMPLEMENTATION_ROADMAP.md` - Testable increments
   - `/poc/IMPLEMENTATION_STATUS.md` - Rewrite for output-centric model

---

## Files to Create (New Scaffolding)

### 1. `/docs/CONCEPT.md`
**Purpose:** High-level explanation of output-centric factor model  
**Audience:** You (for review) and me (for staying on track)  
**Content:**
- What is an output-centric factor?
- Why MIN() calculation?
- How does it enable AI pilot recommendations?
- Key constraints and scope locks

### 2. `/docs/DECISION_FLOW.md`
**Purpose:** Conversation flow and decision tree  
**Audience:** Implementation guide  
**Content:**
- Output identification flow
- 4-component diagnostic questions
- MIN() calculation and bottleneck identification
- Recommendation generation logic

### 3. `/docs/IMPLEMENTATION_ROADMAP.md`
**Purpose:** Testable increments with clear success criteria  
**Audience:** Development tracking  
**Content:**
- Increment 1: Single output assessment
- Increment 2: Output dependencies (2 outputs)
- Increment 3: Root cause decomposition (4 components)
- Each with test scenarios and verification steps

### 4. `/poc/IMPLEMENTATION_STATUS.md` (Rewrite)
**Purpose:** Current POC status aligned with output-centric model  
**Audience:** Quick reference for what's built and what's next  
**Content:**
- What's implemented (DiscoveryEngine, infrastructure)
- What needs refactoring (data models, conversation flow)
- Next steps (aligned with roadmap increments)

---

## Next Steps

1. Create CONCEPT.md (high-level model explanation)
2. Create DECISION_FLOW.md (conversation flow)
3. Create IMPLEMENTATION_ROADMAP.md (testable increments)
4. Rewrite IMPLEMENTATION_STATUS.md (current state)
5. Move obsolete files to `/docs/obsolete/`
6. Update user_interaction_guideline.md (remove abstract factor references)
