# Evidence Hierarchy & Confidence System - Discussion Notes

**Date:** 2025-11-04  
**Status:** Conceptual exploration - Q2/Q4 BLOCKING for implementation

---

## Context

The output-centric factor model needs a way to differentiate between AI inferences and user-provided facts. This affects:
- **Confidence scoring** - How certain are we about component ratings?
- **Transparency** - Can we explain why we think Dependency Quality = ⭐⭐?
- **Validation** - Can user verify assumptions with their technical teams?

---

## The 4-Level Evidence Hierarchy

User wants to distinguish evidence quality:

1. **AI Inference** - System guesses from vague statement
   - Example: "Sales is completely ad-hoc" → infers data_quality: ⭐
   - Lowest certainty about rating

2. **Indirect Mention** - User describes symptoms/outcomes  
   - Example: "Sales reports are garbage" → infers data_quality: ⭐
   - Medium-low certainty

3. **Direct Mention** - User explicitly names the thing
   - Example: "Sales data quality is horrible" → data_quality: ⭐
   - Medium-high certainty

4. **User Example** - User provides concrete evidence
   - Example: "Sales is still using ad-hoc Excels to track everything" → data_quality: ⭐
   - Highest certainty about rating

---

## Key Decisions Made

### Q1: What does "confidence" mean?

**DECIDED:** Confidence = **Certainty about the rating**

- NOT: Certainty that evidence exists (we're always 100% sure they said it)
- NOT: Weight in synthesis (that's implicit in evidence level)
- YES: How confident are we that ⭐⭐ is the correct rating?

**Implication:** Multiple pieces of evidence at the same rating → increase confidence

### Q2: How do multiple pieces combine?

**DECIDED:** **Synthesize** into single rating with accumulated confidence

- Store each mention separately (factor-level storage)
- Synthesize at runtime to calculate current rating + confidence
- Evidence from multiple conversations accumulates

**CRITICAL ISSUE (BLOCKING):** 
- "Sales data is bad" can influence MANY outputs (any output that depends on sales data)
- Need to store once, retrieve at inference runtime
- Where in domain model? How to represent shared factors?

### Q3: UX for showing evidence to users?

**DECIDED:** Show evidence quality, allow drill-down

Display format:
```
Dependency Quality: ⭐⭐ (2 stars)
Based on: 1 direct mention, 2 inferences
[Want to see details?]
```

If user asks for details:
```
Evidence for Dependency Quality = ⭐⭐:
📋 "Sales is still using ad-hoc Excels" (your example)
📝 "Sales data quality is horrible" (you mentioned)
🤖 "Sales is completely ad-hoc" (inferred from your description)
```

### Q4: Static vs Dynamic boundary

**DECIDED:** Follow obsolete doc pattern:
- **Static (JSON):** Taxonomy, scales, inference rules
- **Dynamic (Firestore):** User's evidence trail, ratings, confidence

**CRITICAL ISSUE (BLOCKING):**
- How/where in domain model do we represent a factor and its confidence?
- Is a "factor" output-specific or shared across outputs?
- Storage/retrieval strategy?

---

## Open Questions (BLOCKING)

### 🚨 Q2/Q4: Factor Representation & Storage

**The Problem:**

User says: "Sales data is bad"

This statement could influence:
- Output: "Sales Forecast" → Dependency Quality component
- Output: "Sales Dashboard" → Dependency Quality component  
- Output: "Revenue Report" → Dependency Quality component
- Output: "Customer Segmentation" → Dependency Quality component

**Current model (output-centric):**
```
OutputFactor {
  output: "Sales Forecast"
  dependency_quality: ComponentRating {
    rating: 2
    confidence: 0.75
    evidence: [...]
  }
}
```

**The tension:**
- Evidence about "sales data quality" is **shared** across outputs
- But factors are **output-specific** (capability to deliver THIS output)
- Do we duplicate evidence across all affected outputs?
- Or do we have a shared "factor" concept separate from output-specific components?

**Options to explore:**

**Option A: Duplicate evidence across outputs**
- Store "Sales data is bad" in every OutputFactor that depends on sales data
- Pro: Simple, output-centric stays pure
- Con: Redundant storage, update complexity

**Option B: Shared factor pool**
- Have a separate "Factor" entity (e.g., "sales_data_quality")
- OutputFactor.dependency_quality **references** this shared factor
- Pro: Single source of truth, efficient storage
- Con: Breaks pure output-centric model, adds indirection

**Option C: Hybrid - Evidence pool, ratings per-output**
- Store evidence in shared pool (e.g., "sales_data" evidence collection)
- Each OutputFactor synthesizes its own rating from relevant evidence
- Pro: Efficient storage, output-specific ratings
- Con: More complex retrieval logic

**Questions:**
1. Is "sales data quality" a factor in its own right, or just evidence for output-specific components?
2. If it's shared, how do we model the relationship in the domain?
3. How does this affect the MIN() calculation and bottleneck identification?
4. What's the retrieval pattern at inference time?

---

## Related: TBD #15 - Verifiable Assumptions Export

**Added to TBD.md:** Track assumptions that can be verified by technical teams

**Connection to evidence hierarchy:**
- Verifiable assumptions are candidates for moving from Level 1-2 → Level 3-4
- Export questionnaire to technical stakeholders
- Re-import answers to update evidence levels and confidence

**Examples:**
- "You have 3 years of historical sales data" → Ask data engineer
- "CRM has no forecasting tools" → Ask system admin
- "Data quality is ~30%" → Ask data team
- "Team lacks ML expertise" → Ask engineering manager

---

## Design Principles (from obsolete doc)

From `conversation_memory_architecture.md`:

1. **Factor-Centric Journal**
   - Everything worth remembering links to a factor
   - Current state + confidence stored directly on factor
   - Journal provides temporal audit trail

2. **Evidence Accumulation**
   - Multiple mentions increase confidence
   - Each mention stored with timestamp, context, evidence level
   - LLM synthesizes all evidence to calculate current rating

3. **Provenance Tracking**
   - Can always explain "why this rating?"
   - Show evidence trail to user
   - Distinguish inferences from facts

4. **Static vs Dynamic**
   - Static: Taxonomy, scales, rules (JSON, loaded at startup)
   - Dynamic: User evidence, ratings (Firestore, accumulated over time)

---

## Next Steps

### Before proceeding with implementation:

1. **Resolve Q2/Q4:** Factor representation in domain model
   - Is there a shared "Factor" concept?
   - How does it relate to OutputFactor components?
   - Storage and retrieval strategy?

2. **Add TBD for Q2/Q4** (BLOCKING)

3. **Design domain model** that handles:
   - Output-specific component ratings
   - Shared evidence that influences multiple outputs
   - Efficient storage and retrieval
   - Clear provenance tracking

### After Q2/Q4 resolved:

4. Update CONCEPT.md with evidence hierarchy
5. Update DECISION_FLOW.md with evidence collection steps
6. Update IMPLEMENTATION_ROADMAP.md with evidence storage
7. Design component_scales.json (inference rules)
8. Design questionnaire export format (TBD #15)

---

## Key Insights

1. **Confidence is about rating certainty, not evidence existence**
   - Multiple pieces of evidence → higher confidence in rating
   - Evidence level affects how much it increases confidence

2. **Evidence accumulates over time**
   - Not just "current conversation" but across all conversations
   - Need temporal tracking (journal pattern)

3. **Shared evidence problem is critical**
   - Can't ignore cross-output dependencies
   - Must solve before implementing Increment 1

4. **UX must show evidence quality**
   - Users need to see: "This is an inference" vs "You told me this"
   - Enables validation and correction

5. **Verifiable assumptions enable validation**
   - Export questionnaire for technical stakeholders
   - Upgrade evidence levels when verified
   - Reduces reliance on AI inference

---

## Questions for Discussion

### On Q2/Q4 (Factor Representation):

1. Should "sales data quality" be a first-class entity in the domain model?
2. How do we model the relationship: Evidence → Factor → Component → Output?
3. Is the MIN() calculation still purely output-centric, or does it reference shared factors?
4. What's the retrieval pattern when user asks "Why is Sales Forecast rated ⭐⭐?"

### On Evidence Synthesis:

1. How does LLM synthesize multiple evidence pieces into single rating?
2. Do we weight by evidence level? (Level 4 > Level 1)
3. Do we weight by recency? (Recent mentions > old mentions)
4. How do we handle contradictions? ("Data is good" vs "Data is bad")

### On Storage:

1. Firestore collection structure for evidence?
2. How to query "all evidence about sales data" efficiently?
3. How to query "all evidence affecting Sales Forecast" efficiently?
4. Token budget management when retrieving evidence?

---

## References

- **Obsolete doc:** `/docs/obsolete/conversation_memory_architecture.md`
  - Factor-Centric Journal pattern
  - Evidence accumulation strategy
  - Static vs Dynamic data separation

- **TBD #15:** Verifiable Assumptions Export
  - `/docs/1_functional_spec/TBD.md`

- **Current model:** Output-Centric Factor Model
  - `/docs/CONCEPT.md`
  - `/docs/DECISION_FLOW.md`
  - `/docs/IMPLEMENTATION_ROADMAP.md`
