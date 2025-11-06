# Release 2 Scope Cleanup Summary

**Date:** 2025-11-05  
**Action:** Archive non-Release 1-2 files from `src/data/`

---

## Files Archived

Moved to `src/data/Archive/`:

### Recommendation Engine (Release 4)
- ✅ `pilot_catalog.json` - 28 specific AI pilot examples
- ✅ `pilot_types.json` - AI pilot archetypes and categories
- ✅ `inference_rules/ai_archetypes.json` - 27 AI archetype definitions
- ✅ `inference_rules/pain_point_mapping.json` - Pain point to solution mapping

### Feasibility Assessment (Release 4)
- ✅ `capability_framework.json` - Prerequisite checking framework

---

## Files Remaining (Active in Release 1-2)

### Output Discovery (Release 2)
- `organizational_templates/functions/sales.json`
- `organizational_templates/functions/finance.json`
- `organizational_templates/functions/operations.json`
- `organizational_templates/functions/marketing.json`
- `organizational_templates/functions/customer_success.json`
- `organizational_templates/functions/hr.json`
- `organizational_templates/functions/supply_chain.json`
- `organizational_templates/functions/it_operations.json`
- `organizational_templates/cross_functional/common_systems.json`
- `inference_rules/output_discovery.json`

### Assessment Engine (Release 2)
- `component_scales.json` - 1-5 star rating scale definitions

---

## Rationale

**Release 1-2 Focus:**
- Output discovery from natural language
- Edge-based assessment (People, Tool, Process, Dependency → Output)
- Evidence tracking and Bayesian aggregation
- MIN calculation and bottleneck identification

**Not Needed Yet:**
- AI pilot recommendations → Release 4
- Feasibility checking → Release 4
- Business context extraction → Release 3

**Benefit:**
- Cleaner `src/data/` structure
- Clear scope boundaries
- Easier to understand what's active vs future
- Prevents premature optimization

---

## Restoration Plan

When Release 4 begins:
```bash
# Move files back from archive
mv src/data/Archive/pilot_catalog.json src/data/
mv src/data/Archive/pilot_types.json src/data/
mv src/data/Archive/capability_framework.json src/data/
mv src/data/Archive/ai_archetypes.json src/data/inference_rules/
mv src/data/Archive/pain_point_mapping.json src/data/inference_rules/
```

---

**Status:** ✅ Complete  
**Impact:** No breaking changes (files not yet referenced in code)
