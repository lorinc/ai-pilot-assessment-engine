# Release 2: Discovery & Assessment

**Duration:** Weeks 3-4  
**Status:** Planning  
**Prerequisites:** Release 1 complete (auth, persistence, streaming chat)

---

## Quick Links

- **[Implementation Plan](RELEASE2_IMPLEMENTATION_PLAN.md)** - Detailed scaffolding and tasks
- **[Cleanup Summary](CLEANUP_SUMMARY.md)** - Data file archival decisions

---

## What Gets Built

### Core Capabilities
1. **Output Discovery** - Identify outputs from natural language descriptions
2. **Edge Assessment** - Rate 4 edge types conversationally (People, Tool, Process, Dependency → Output)
3. **Evidence Tracking** - Classify and weight user statements by tier
4. **Bayesian Aggregation** - Weighted scoring with confidence
5. **Bottleneck Identification** - MIN calculation to find weakest link
6. **Graph Operations** - NetworkX ↔ Firestore sync

### User Experience
```
User: "Sales forecasts are always wrong"
  ↓
System: "I think you're talking about Sales Forecast. Is that right?"
  ↓
User: "Yes, the team is junior and the CRM is terrible"
  ↓
System: "I'm hearing Team=⭐⭐ and System=⭐. Let me ask about Process..."
  ↓
[Assessment continues for all 4 edges]
  ↓
System: "Your Sales Forecast quality is ⭐ (MIN). The bottleneck is System (⭐)."
```

---

## What's NOT Built (Yet)

- ❌ Business context extraction (budget, timeline) → Release 3
- ❌ AI pilot recommendations → Release 4
- ❌ Feasibility assessment → Release 4
- ❌ Report generation → Release 5

---

## Key Files

### New Code
- `src/core/graph_manager.py` - Graph operations and Firestore sync
- Extended: `src/core/session_manager.py` - Phase tracking
- Extended: `src/app.py` - Assessment UI components

### Data Files (Active)
- `src/data/organizational_templates/functions/*.json` - 8 functions, 46 outputs
- `src/data/component_scales.json` - Rating scales
- `src/data/inference_rules/output_discovery.json` - Discovery rules

### Data Files (Archived)
- `src/data/Archive/` - Release 3+ files (recommendations, feasibility)

---

## Success Criteria

✅ Identifies outputs from descriptions (>80% accuracy)  
✅ Assesses all 4 edge types conversationally  
✅ Evidence classified by tier (1-5)  
✅ Bayesian aggregation correct  
✅ MIN calculation accurate  
✅ Bottleneck identification working  
✅ Graph persists across sessions

---

## Timeline

| Days | Task | Deliverable |
|------|------|-------------|
| 1-2 | Graph infrastructure | NetworkX + Firestore sync |
| 3-4 | Output discovery | Identify from natural language |
| 5-7 | Assessment engine | 4 edge types, evidence tracking |
| 8-9 | Bottleneck ID | MIN calc, gap analysis |
| 10 | UI integration | Full flow in Streamlit |

---

## Next Steps

1. Review implementation plan
2. Ensure Release 1 is complete
3. Begin Day 1: Graph infrastructure
4. Weekly check-ins on progress

---

**Owner:** Technical Lead  
**Reviewers:** Product Owner
