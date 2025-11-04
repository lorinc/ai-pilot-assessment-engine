# Model Evolution - Exploring Representation Alternatives

**Purpose:** Structured exploration of different ways to represent knowledge in the output-centric factor model

**Status:** Active exploration - TBD #16 blocking issue

---

## Overview

The output-centric factor model has a fundamental tension:
- **Factors are output-specific** (capability to deliver THIS output)
- **Evidence is often shared** (one statement affects many outputs)

This folder contains:
1. **Canonical user interaction patterns** (what we must handle)
2. **Alternative representation models** (how we might handle them)
3. **Comparative analysis** (trade-offs between models)

---

## Structure

```
4_model_evolution/
├── README.md                           # This file
├── USER_INTERACTION_PATTERNS.md        # Canonical examples (10 patterns)
│
├── alternative_A_pure_output_centric/
│   ├── REPRESENTATION.md               # How knowledge is structured
│   ├── STORAGE.md                      # Firestore schema
│   ├── RETRIEVAL.md                    # Query patterns
│   ├── CONVERSATION_FLOW.md            # How it affects UX
│   └── TRADEOFFS.md                    # Pros/cons vs. other models
│
├── alternative_B_generic_outputs/
│   ├── REPRESENTATION.md
│   ├── STORAGE.md
│   ├── RETRIEVAL.md
│   ├── CONVERSATION_FLOW.md
│   └── TRADEOFFS.md
│
├── alternative_C_shared_factors/
│   ├── REPRESENTATION.md
│   ├── STORAGE.md
│   ├── RETRIEVAL.md
│   ├── CONVERSATION_FLOW.md
│   └── TRADEOFFS.md
│
└── DECISION.md                         # Final decision + rationale
```

---

## Evaluation Criteria

Each alternative model is evaluated on:

### 1. Pattern Coverage
- Can it handle all 10 user interaction patterns?
- Are there patterns it handles poorly?

### 2. Conceptual Clarity
- Is it easy to explain to users?
- Does it align with output-centric principle?
- Is the domain model intuitive?

### 3. Storage Efficiency
- How much duplication?
- Storage cost at scale (50 outputs, 100 conversations)?

### 4. Retrieval Performance
- Can we efficiently query "all evidence for Sales Forecast"?
- Can we efficiently query "all evidence about sales data quality"?
- Token budget for context retrieval?

### 5. Conversation Flow
- Does it require extra clarifying questions?
- Can user stay vague or must they be specific?
- How does it handle progressive refinement?

### 6. Implementation Complexity
- How complex is the code?
- How many edge cases?
- Maintainability?

---

## Alternative Models (To Be Explored)

### Alternative A: Pure Output-Centric (Duplication)
**Core Idea:** Each output has its own evidence, duplicate shared statements

**Key Question:** How much duplication is acceptable?

### Alternative B: Generic Outputs (Your Proposal)
**Core Idea:** Create "Generic Team/System/Process Outputs" to hold vague evidence

**Key Question:** When do we use Generic vs. Specific?

### Alternative C: Shared Factors (Two-Level Model)
**Core Idea:** Have shared "Factors" (e.g., sales_data_quality) that outputs reference

**Key Question:** Does this break output-centric purity?

### Alternative D: Evidence Pool (Hybrid)
**Core Idea:** Shared evidence pool, output-specific ratings synthesized at runtime

**Key Question:** Is retrieval too complex?

---

## Process

For each alternative:

1. **Document representation** - What entities exist? How do they relate?
2. **Design storage** - Firestore collections, document structure
3. **Define retrieval** - Query patterns for common questions
4. **Map conversation flow** - How does it affect user experience?
5. **Analyze trade-offs** - Pros/cons vs. other alternatives

Then:

6. **Compare alternatives** - Side-by-side on evaluation criteria
7. **Make decision** - Choose one, document rationale
8. **Update main docs** - CONCEPT.md, DECISION_FLOW.md, IMPLEMENTATION_ROADMAP.md

---

## Current Status

- ✅ **USER_INTERACTION_PATTERNS.md** - 10 canonical patterns documented
- 🔄 **Alternative B (Generic Outputs)** - Currently exploring with user
- ⏸️ **Other alternatives** - Not yet documented
- ⏸️ **Decision** - Blocked until alternatives explored

---

## References

- **TBD #16:** Shared Evidence & Factor Representation (BLOCKING)
- **EVIDENCE_HIERARCHY_DISCUSSION.md:** Q2/Q4 discussion notes
- **Obsolete doc:** `conversation_memory_architecture.md` (Factor-Centric Journal pattern)
