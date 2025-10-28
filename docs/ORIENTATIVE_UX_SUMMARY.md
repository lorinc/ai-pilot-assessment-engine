# Orientative UX - Implementation Summary

## What Was Added

### 1. User Interaction Guidelines (`user_interaction_guideline.md`)

Added **Section 8: Orientative Conversation Patterns** with 4 patterns:

#### Pattern 1: Status Query - "Where Are We?"
- **Trigger:** User asks OR system offers at natural conclusion
- **Shows:** Per-category completeness/confidence + what this enables
- **Format:** Adaptive based on conversation stage + grouped by category
- **Always includes:** Current capability + next logical steps

#### Pattern 2: Next Tier Query - "What's Missing?"
- **Trigger:** User asks "what do we need?" OR approaching tier boundary
- **Shows:** Per-category gaps + confidence thresholds
- **Tiers:** Risk-based (exploratory → low-risk <€25k → medium-risk €25k-€100k)
- **Format:** Current tier + what's needed for next + 2-3 options

#### Pattern 3: Conversation Continuity - "Where Were We?"
- **Trigger:** User returns OR explicitly asks
- **Default:** Last meaningful factor update + quick status
- **With scope:** Last conversation about specific topic
- **Shows:** Factor dependencies + what continuing would unlock

#### Pattern 4: Proactive Milestone Offers
- **Trigger:** Discussion reaches natural conclusion
- **Shows:** What completed + new capability unlocked + progress indicator
- **Format:** Before/after comparison + 2-3 next options

### 2. Orientative Pattern Principles

1. **Always Show Current Capability** - Concrete examples, not abstract percentages
2. **Progress, Not Completeness** - "Can assess 5 types now" vs "Only 30% complete"
3. **Risk-Based Tiers** - Tied to decision stakes (€25k, €100k)
4. **Diminishing Returns Awareness** - Signal when ROI is low
5. **Agency Through Options** - Always 2-3 concrete next actions
6. **Brevity** - Under 150 words, bullets, clear sections

### 3. Persistence Architecture (`conversation_memory_architecture.md`)

#### Added User Metadata Collection

```yaml
/users/{user_id}/metadata:
  assessment_summary:
    categories:
      data_readiness:
        completeness: 0.60
        avg_confidence: 0.70
        factor_count: 15
        total_factors: 25
    
    overall:
      total_factors_assessed: 25
      avg_confidence: 0.60
      decision_tier: "low_risk"
    
    capabilities:
      can_evaluate: ["basic_forecasting_annual"]
      cannot_evaluate_yet: ["complex_forecasting_seasonal"]
    
    last_conversation:
      topic: "data_quality"
      timestamp: "2024-10-28T10:30:00Z"
      excerpt: "User mentioned data scattered..."
```

#### Extended FactorJournalStore

New methods:
- `update_assessment_summary()` - Recalculates aggregates on every factor update
- `calculate_decision_tier()` - Determines risk tier from confidence + completeness
- `calculate_capabilities()` - Maps factors → project archetypes via graph
- `get_assessment_summary()` - Fast O(1) retrieval for orientative queries

#### Orientative Query Handler

```python
def handle_orientative_query(query_type: str, user_id: str):
    summary = journal_store.get_assessment_summary(user_id)
    
    if query_type == "status":
        return format_status_response(summary)
    elif query_type == "next_tier":
        return format_next_tier_response(summary)
    elif query_type == "where_were_we":
        return format_continuity_response(summary)
    elif query_type == "milestone":
        return format_milestone_response(summary)
```

---

## Key Design Decisions

### 1. Completeness Philosophy
**70% Risk-based, 30% Diminishing returns**
- Tie completeness to decision stakes (€25k, €100k, €500k)
- Signal when additional assessment has low ROI
- Stop at "good enough for decision," not 100%

### 2. Status Query Scope
**Adaptive + Grouped by category**
- Show factors relevant to mentioned projects
- Group by category (Data Readiness, AI Capability)
- Drill-down option for details

### 3. Next Tier Thresholds
**Per-category completeness + confidence**
- "Data Readiness: 60% mapped, 70% confident"
- "To reach next tier: need 75% confidence in data factors"
- Specific gaps: "Missing: data governance, ML infrastructure"

### 4. Where Were We Context
**Configurable with smart default**
- Default: Last meaningful factor update
- With scope: Last conversation about specific topic
- Always include quick status

### 5. Progress Indicators
**Project archetypes with high-level examples**
- "You can evaluate basic forecasting of annual sales"
- "Not yet: monthly predictions with seasonal trends"
- Generalizable, not too specific

### 6. Interaction Triggers
**Hybrid: Proactive + User-initiated**
- LLM offers at natural breakpoints (milestone reached)
- User can always request ("where are we?")
- Not too chatty, not too silent

### 7. Next Step Recommendations
**Mix based on context**
- Questions to ask ("Tell me about data governance")
- Categories to explore ("Assess AI capability")
- Project evaluations ("Evaluate that forecasting project")

### 8. Continuity Benefits
**Show factor dependencies**
- "Finishing data quality unlocks 3 other assessments"
- Not feasible to show project impact (generated at runtime)
- Qualitative when quantitative not available

---

## Implementation Impact

### Storage
- **New collection:** `/users/{user_id}/metadata/assessment`
- **Size:** ~2 KB per user (aggregate metrics only)
- **Updates:** On every factor update (real-time)

### Performance
- **Orientative queries:** O(1) - single document read
- **Factor updates:** +O(n) for aggregation (n = total factors)
- **Trade-off:** Slightly slower writes, much faster reads

### Graph Requirements
New graph methods needed:
- `get_factor_category(factor_id)` - Map factor to category
- `get_category_factor_count(category)` - Total factors in category
- `get_enabled_archetypes(factor_ids)` - What can user evaluate?
- `get_disabled_archetypes(factor_ids)` - What's still locked?

---

## Example Flow

**User completes data quality assessment:**

1. **System detects milestone** (factor assessment complete)

2. **Updates aggregate metrics:**
   - Data Readiness: 40% → 60% mapped
   - Avg confidence: 65% → 70%
   - Decision tier: exploratory → low_risk
   - Capabilities: +3 project archetypes

3. **Proactive milestone offer:**
   ```
   System: "Okay, we've mapped out your data quality pretty well.
   
   **New capability unlocked:**
   You can now evaluate projects that need historical sales data—
   things like demand forecasting, trend analysis.
   
   **Progress:** You could assess 2 project types before, now you can assess 5.
   
   **What next?**
   - Continue with data governance (builds on what we just discussed)
   - Switch to AI capability (team skills, infrastructure)
   - Evaluate that forecasting project you mentioned
   
   What sounds good?"
   ```

4. **User can always check status:**
   ```
   User: "Where are we overall?"
   
   System: [Retrieves pre-calculated summary in <100ms]
   "Here's what we've mapped out:
   
   **Data Readiness: 60% mapped, 70% confident**
   With this, you can evaluate basic forecasting projects.
   
   **AI Capability: 40% mapped, 50% confident**
   You can assess simple automation, not complex ML yet.
   
   **What you can do now:**
   You can evaluate basic forecasting of annual sales results,
   but not monthly predictions with seasonal trends.
   
   **Next steps:**
   - Continue mapping data readiness → Unlock quarterly forecasting
   - Explore AI capability → Unlock 3 more project types
   - Start evaluating that sales forecasting project
   
   What sounds most useful?"
   ```

---

## Next Implementation Steps

1. **Define factor taxonomy** - List all factors + categories
2. **Implement graph methods** - Category mapping, archetype enablement
3. **Extend FactorJournalStore** - Add aggregation methods
4. **Create orientative handlers** - Format response functions
5. **Add LLM prompts** - Detect when to offer orientative responses
6. **Test with real conversations** - Verify UX feels natural

---

## Success Criteria

Users should always know:
- ✅ What they can evaluate **right now**
- ✅ What they'd unlock by continuing
- ✅ What their options are
- ✅ How much progress they've made
- ✅ When "good enough" has been reached

Users should never feel:
- ❌ Lost ("where are we?")
- ❌ Forced to complete everything
- ❌ Unsure what to do next
- ❌ Like they're filling out forms
