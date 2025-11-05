# Pre-Phase 2 Readiness Checklist

**Date:** 2025-11-05  
**Purpose:** Ensure Phase 1 is complete and Phase 2 foundations are ready

---

## Phase 1 Completion Status

### ✅ Infrastructure (Complete)
- [x] GCP project configured
- [x] Firebase Auth operational
- [x] Firestore persistence working
- [x] Vertex AI / Gemini integration
- [x] Streamlit chat UI functional
- [x] Session management with persistence
- [x] Technical logging

### ✅ Code Structure (Complete)
- [x] `src/core/llm_client.py` - Gemini streaming
- [x] `src/core/firebase_client.py` - Auth + Firestore
- [x] `src/core/session_manager.py` - Session state
- [x] `src/utils/logger.py` - Technical logging
- [x] `src/config/settings.py` - Environment config
- [x] `src/app.py` - Streamlit entry point

### ✅ Testing (Complete)
- [x] Unit tests for core modules (4 files)
- [x] Integration tests for flows (5 files)
- [x] Mock mode for development
- [x] Real GCP integration tests

### ⚠️ Missing (Phase 1 Scope)
- [ ] `src/core/graph_manager.py` - **Mentioned in README but doesn't exist**
  - **Action:** This is Phase 2 scope, remove from Phase 1 docs

---

## Recommended Actions Before Phase 2

### 1. Clean Up Phase 1 Documentation ⚠️

**Issue:** `src/README.md` mentions `graph_manager.py` as Phase 1, but it's actually Phase 2.

**Action:**
```bash
# Update src/README.md line 13
- "└── graph_manager.py       # NetworkX ↔ Firestore sync (Phase 2)"
+ Remove this line or mark clearly as "Phase 2 only"
```

**Why:** Avoid confusion about what's actually implemented in Phase 1.

---

### 2. Verify Test Suite Runs ✅

**Issue:** `pytest` command not found in environment.

**Action:**
```bash
# Install in virtual environment
source venv/bin/activate
pip install -r requirements.txt

# Verify tests run
pytest tests/unit/ -v
pytest tests/integration/ -v --tb=short
```

**Why:** Ensure baseline quality before adding Phase 2 complexity.

---

### 3. Add Phase 2 Data Validation 📊

**Issue:** Phase 2 relies heavily on `src/data/` files. Need to validate structure.

**Action:** Create validation script to check:
- All 8 function templates have required fields
- `component_scales.json` has all 4 components (Team, System, Process, Dependency)
- `inference_rules/output_discovery.json` exists and is valid JSON
- No missing references between files

**Script Location:** `scripts/validate_data_structure.py`

**Why:** Catch data issues early before Phase 2 implementation.

---

### 4. Create Phase 2 Test Fixtures 🧪

**Issue:** Phase 2 needs conversation test data for output discovery and assessment.

**Action:** Create test fixtures:
```
tests/fixtures/conversations/
├── sales_forecast_happy_path.json
├── support_tickets_vague_input.json
├── finance_budget_contradictory.json
└── operations_multi_bottleneck.json
```

**Format:**
```json
{
  "test_id": "sales_forecast_001",
  "user_input": "Our sales forecasts are always wrong",
  "expected_output_id": "sales_forecast",
  "expected_edges": {
    "team_execution": {"score": 2, "confidence": 0.7},
    "system_capabilities": {"score": 1, "confidence": 0.9}
  }
}
```

**Why:** Enable test-driven development for Phase 2 features.

---

### 5. Set Up Phase 2.5 Evaluation Infrastructure 🔍

**Issue:** Need semantic evaluation ready when Phase 2 features land.

**Action:**
- Install sentence-transformers: `pip install sentence-transformers`
- Create `tests/semantic/` directory structure
- Set up LLM-as-judge evaluation prompts
- Create baseline embedding similarity tests

**Why:** Catch quality regressions immediately, not after Phase 2 is "done."

---

### 6. Review Data File Quality 📋

**Recommendation:** Spot-check data files for Phase 2 readiness.

**Check:**
- [ ] `component_scales.json` - Are indicators clear enough for LLM inference?
- [ ] `organizational_templates/functions/*.json` - Are pain points specific enough?
- [ ] `inference_rules/output_discovery.json` - Are matching rules comprehensive?

**Action:** Read through 2-3 function templates, verify:
- Pain points are realistic and specific
- Typical dependencies make sense
- Creation context (team/process/system) is complete

**Why:** Poor data quality = poor Phase 2 results, regardless of code quality.

---

### 7. Establish Baseline Metrics 📈

**Issue:** Need to measure Phase 2 progress objectively.

**Action:** Run baseline measurements:
- Unit test coverage: `pytest --cov=src --cov-report=term`
- Code complexity: `radon cc src/ -a`
- Response time: Measure current LLM streaming latency

**Why:** Track whether Phase 2 maintains quality (coverage, performance).

---

### 8. Architecture Decision: Graph Storage Strategy 🏗️

**Question:** Where should the graph live during Phase 2?

**Options:**
1. **In-memory only (NetworkX)** - Fast, simple, lost on session end
2. **Firestore only** - Persistent, slower queries, no graph algorithms
3. **Hybrid (recommended)** - NetworkX in-memory, sync to Firestore

**Recommendation:** Hybrid approach
- Load graph from Firestore on session start
- Operate on NetworkX in-memory (fast traversal, MIN calc)
- Write back to Firestore on changes
- Clear in-memory graph on session end

**Why:** Balances performance (graph algorithms) with persistence (user data).

---

### 9. Clarify Phase 2 Scope Boundaries 🎯

**Question:** What's IN vs OUT of Phase 2?

**IN Phase 2:**
- ✅ Single output assessment (4 edges: Team, System, Process, Dependency)
- ✅ Conversational rating inference (LLM infers ⭐ from user statements)
- ✅ Evidence tracking with tiers (1-5)
- ✅ Bayesian aggregation
- ✅ MIN calculation and bottleneck identification
- ✅ Graph CRUD operations (add/remove nodes/edges)

**OUT of Phase 2 (Phase 3+):**
- ❌ Multi-output dependency traversal (just single output for now)
- ❌ Business context extraction (budget, timeline, visibility)
- ❌ AI pilot recommendations
- ❌ Feasibility assessment
- ❌ Report generation

**Action:** Document this clearly in Phase 2 plan to avoid scope creep.

---

### 10. Create Phase 2 Progress Tracker 📝

**Issue:** Need visibility into Phase 2 implementation progress.

**Action:** Create simple progress tracker:
```
PHASE2_PREP_PROGRESS.md

## Day 1-2: Graph Infrastructure
- [ ] Create GraphManager class
- [ ] Implement node CRUD
- [ ] Implement edge CRUD
- [ ] Firestore sync (load/save)
- [ ] Unit tests

## Day 3-4: Output Discovery
...
```

**Why:** Track daily progress, identify blockers early.

---

## Priority Recommendations

### Must Do Before Phase 2 (Blockers)
1. ✅ **Verify test suite runs** - Can't build without tests
2. ✅ **Create data validation script** - Catch data issues early
3. ✅ **Clarify graph storage strategy** - Architecture decision needed

### Should Do (High Value)
4. **Create Phase 2 test fixtures** - Enable TDD
5. **Set up Phase 2.5 evaluation** - Quality assurance ready
6. **Review data file quality** - Prevent garbage-in-garbage-out

### Nice to Have (Lower Priority)
7. **Establish baseline metrics** - Track progress objectively
8. **Create progress tracker** - Visibility into work
9. **Clean up Phase 1 docs** - Remove confusion

---

## Estimated Effort

**Must Do:** 4-6 hours
- Test suite verification: 1 hour
- Data validation script: 2-3 hours
- Architecture decision doc: 1-2 hours

**Should Do:** 6-8 hours
- Test fixtures: 3-4 hours
- Phase 2.5 setup: 2-3 hours
- Data quality review: 1 hour

**Total:** 10-14 hours (1-2 days)

---

## Risks if Skipped

**Skip test verification:**
- Risk: Build Phase 2 on broken foundation
- Impact: High - could waste days debugging Phase 1 issues

**Skip data validation:**
- Risk: Phase 2 fails due to malformed data
- Impact: Medium - fixable but frustrating

**Skip test fixtures:**
- Risk: Manual testing only, slow feedback loop
- Impact: Medium - slower development, more bugs

**Skip Phase 2.5 setup:**
- Risk: No quality measurement until Phase 2 "done"
- Impact: Medium - harder to catch regressions

---

## Decision

**Recommended Path:**
1. Spend 1-2 days on "Must Do" + "Should Do" items
2. Start Phase 2 Day 1 with clean foundation
3. Implement Phase 2.5 evaluation in parallel with Phase 2 features

**Alternative (Faster but Riskier):**
1. Only do "Must Do" items (4-6 hours)
2. Start Phase 2 immediately
3. Add test fixtures and evaluation reactively as issues arise

---

**Document Status:** Ready for Review  
**Owner:** Technical Lead  
**Next Steps:** Review with team, decide on path forward
