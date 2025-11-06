# Building Static Knowledge Graphs for LLM Chain-of-Thought Reasoning

**A Practical Guide for Cross-Domain, Expert-Curated Knowledge Graphs**

---

## Table of Contents

1. [Introduction](#introduction)
2. [When to Build a Static KG](#when-to-build-a-static-kg)
3. [Scoping Your Knowledge Graph](#scoping-your-knowledge-graph)
4. [Structuring Principles](#structuring-principles)
5. [Taxonomy Depth & Abstraction Consistency](#taxonomy-depth--abstraction-consistency)
6. [Enrichment for Completeness](#enrichment-for-completeness)
7. [Transformation for LLM Reasoning](#transformation-for-llm-reasoning)
8. [Validation Methodology](#validation-methodology)
9. [Maintenance & Evolution](#maintenance--evolution)
10. [Case Study: AI Pilot Assessment Engine](#case-study)

---

## Introduction

### What is a Static Knowledge Graph?

A **static knowledge graph** is an expert-curated, domain-specific graph of entities and relationships that:
- Changes infrequently (weeks/months, not real-time)
- Represents structured domain knowledge
- Enables multi-hop reasoning for LLMs
- Provides consistent, validated information

**Research Finding** (arXiv 2412.10654v1):
> LLMs fine-tuned with structured graph representations outperform larger models on multi-hop reasoning tasks. Small models + good graph structure > large models alone.

---

## When to Build a Static KG

### ✅ Good Use Cases

1. **Cross-domain decision support** - "Can we do X project given Y constraints?"
2. **Guided exploration** - "What's possible given what we know?"
3. **Prerequisite checking** - "What do we need for X?"
4. **Impact analysis** - "If we improve Y, what becomes feasible?"

### ❌ Poor Use Cases

1. **Real-time data** - Stock prices, sensor readings
2. **Unstructured content** - Document search (use RAG)
3. **Rapidly changing domains** - Daily news, trends
4. **Simple lookups** - Key-value pairs

### Manual vs. Automated

**Manual (this guide):**
- ✅ High quality, domain-validated
- ✅ Consistent abstraction levels
- ✅ Suitable for 100-1000 nodes

**Automated (NER/extraction):**
- ✅ Scales to millions
- ❌ Noisy, needs cleanup
- ❌ Inconsistent abstraction

**Recommendation:** For <1000 core concepts, manual curation is superior.

---

## Scoping Your Knowledge Graph

### The Four Scoping Questions

#### 1. Coverage: What's In Scope?

**Examples:**
- ❌ Too broad: "All business processes in all industries"
- ✅ Focused: "AI project feasibility for tech/finance"

#### 2. Granularity: How Many Nodes?

**Guidelines:**
- Factors/Dimensions: 20-30 per category
- Archetypes/Solutions: 15-25
- Prerequisites: 30-50 (grouped)

#### 3. Depth: How Many Levels?

**Sweet Spot:** 3-5 levels

```
Level 1: Business Context
Level 2: Pain Point
Level 3: Solution Type
Level 4: Implementation Requirement
```

#### 4. Audience: Who Uses This?

Adjust terminology and detail for:
- Non-technical executives
- Technical leads
- Data scientists

---

## Structuring Principles

### Node Design

#### 1. Stable, Semantic IDs

```json
{
  "id": "data_quality_001",
  "name": "Data Quality",
  "display_name": "Data Quality & Consistency"
}
```

#### 2. Rich Attributes

```json
{
  "id": "data_quality",
  "type": "FACTOR",
  "category": "data_readiness",
  "scale": {"0": "No controls", "100": "World-class"},
  "assessment_time_minutes": 10
}
```

### Edge Design

#### 1. Typed, Directional Relationships

```
Archetype --[IMPLEMENTED_BY]--> Model
Model --[REQUIRES]--> Prerequisite
Output --[MITIGATES_FAILURE]--> Problem
```

#### 2. Optional Weights

```json
{
  "source": "forecasting",
  "target": "data_quality",
  "relationship": "REQUIRES",
  "strength": "critical"
}
```

### Common Relationship Types

| Type | Use | Example |
|------|-----|---------|
| `REQUIRES` | Feasibility | Solution → Prerequisite |
| `PRODUCES` | Capability | Archetype → Output |
| `MITIGATES` | Justification | Output → Problem |
| `ENABLES` | Unlock | Capability → Solution |

---

## Taxonomy Depth & Abstraction Consistency

### The Problem

**Mixing levels breaks reasoning:**

```
❌ Inconsistent:
├── data_quality (abstract)
├── missing_values (concrete metric)
└── PostgreSQL (specific tool)

✅ Consistent:
├── data_quality (all abstract)
├── data_availability
└── data_governance
```

### Checking Methods

#### 1. Peer Review Test
List all nodes of same type → "Same conceptual level?"

#### 2. Substitution Test
"We need [FACTOR] for this project" → All should work

#### 3. Depth Analysis
All leaves ~same distance from root

---

## Enrichment for Completeness

### What to Enrich

#### 1. Scales (for Factors)

```json
{
  "factor_id": "data_quality",
  "scale": {
    "0": "No quality controls",
    "50": "Basic processes",
    "100": "World-class quality"
  }
}
```

#### 2. Assessment Time

```json
{
  "factor_id": "data_governance",
  "typical_assessment_time_minutes": 10
}
```

#### 3. Confidence Impact

```json
{
  "factor_id": "ml_infrastructure",
  "confidence_impact": {
    "forecasting": 0.15,
    "classification": 0.10
  }
}
```

#### 4. Dependency Strength

```json
{
  "relationship": "REQUIRES",
  "strength": "critical",
  "rationale": "Project fails without this"
}
```

### Enrichment Workflow

```
1. LLM drafts scales/descriptions
2. Human reviews and edits
3. Validate against use cases
4. Check cross-reference consistency
```

---

## Transformation for LLM Reasoning

### Representation Formats

**Research Finding:** Python code > JSON > Natural language for multi-hop reasoning

#### Natural Language (Most Compatible)

```
"Classification requires labeled training data.
You currently have data_quality at 20% (low)."
```

**Pros:** LLM-native, conversational
**Cons:** Ambiguous for complex reasoning

#### JSON (Structured)

```json
{
  "sales_forecasting": {
    "requires": ["data_quality"],
    "confidence_threshold": 0.60
  }
}
```

**Pros:** Structured, parseable
**Cons:** Hard to represent multi-hop logic

#### Python Pseudocode (Best for Reasoning)

```python
class Project:
    def check_feasibility(self, factors):
        for req in self.requirements:
            if factors[req].value < threshold:
                return False, f"Low {req}"
        return True, "Requirements met"
```

**Pros:** Explicit reasoning, supports complex logic
**Cons:** More verbose

### Hybrid Approach (Recommended)

```
Storage: JSON files
    ↓
Loading: NetworkX graph
    ↓
Prompts: Natural language + structured hints
    ↓
Results: JSON from LLM
```

---

## Validation Methodology

### Release 1: Structural Validation

```
✓ Graph constructs without errors
✓ No dangling edges
✓ All nodes have required attributes
✓ No isolated nodes
```

### Release 2: Reasoning Validation

```
✓ Paths exist between related nodes
✓ Multi-hop queries work
✓ No circular dependencies
✓ Dependency strengths consistent
```

### Release 3: Domain Expert Review

**Checklist:**
- [ ] All major use cases covered?
- [ ] Factor scales make sense?
- [ ] Terminology matches domain?
- [ ] Abstraction levels consistent?

**Process:**
```
1. Select 2-3 domain experts
2. Walk through 3-5 scenarios
3. Collect feedback
4. Iterate
```

### Release 4: End-to-End Testing

Test realistic scenarios:
- New user exploration
- Project feasibility checks
- Guided assessment flow

---

## Maintenance & Evolution

### Version Control

```
src/data/
├── AI_taxonomy.json (v1.2.0)
└── CHANGELOG.md
```

**Semantic versioning:**
- Major: Breaking changes
- Minor: New nodes/edges
- Patch: Description fixes

### When to Refactor

**Extend (minor):**
- Adding nodes/edges
- Enriching attributes

**Refactor (major):**
- Changing node types
- Restructuring hierarchy
- Renaming core concepts

### Changelog Format

```markdown
## [1.2.0] - 2024-10-30

### Added
- 5 new AI archetypes

### Changed
- Renamed ML_infrastructure → ai_infrastructure

### Fixed
- Circular dependency removed
```

---

## Case Study: AI Pilot Assessment Engine

### Context

**Goal:** Evaluate AI project feasibility through conversation

**Challenge:** Reason about 30+ factors, 20+ archetypes, 50+ prerequisites

### Scoping Decisions

- **Coverage:** Cross-industry (tech, finance, healthcare)
- **Granularity:** 30 factors, 20 archetypes, 50 prerequisites
- **Depth:** 4 levels (Business → Pain → Solution → Prerequisite)
- **Audience:** Non-technical executives + technical leads

### What Worked

1. **Factor-centric design** - Everything links to organizational factors
2. **Unconfirmed inferences** - Track LLM-inferred vs. user-confirmed
3. **Pareto-driven suggestions** - 20% of factors, 80% of value
4. **Hybrid representation** - JSON storage, natural language prompts

### What Didn't Work

1. **Linear process** → Exploratory flow with confidence
2. **Event sourcing** → Factor journaling (83% storage reduction)
3. **Single-mention inference** → Cumulative from all evidence
4. **Rigid thresholds** → Risk-based (€10k ≠ €100k project)

### Lessons Learned

1. **Start small** - Epic 1: 1 factor → Epic 2: 10-15 factors
2. **Abstraction consistency is critical** - Refactored once, worth it
3. **LLM-assisted enrichment works** - 70% LLM, 30% human review
4. **Validation catches 80% of issues** - Test early, test often
5. **Version control essential** - Changelog saved hours

### Metrics

- 193 nodes, 312 edges
- Construction: <100ms
- Single-hop query: <50ms
- Multi-hop (3 hops): <200ms

---

## Key Takeaways

1. **Manual curation beats automation** for <1000 nodes
2. **Abstraction consistency** is more important than depth
3. **Enrich for reasoning** - scales, times, impacts, strengths
4. **Hybrid representation** - JSON storage, natural language prompts
5. **Validate thoroughly** - structure, reasoning, domain, end-to-end
6. **Version control** - treat taxonomies as code
7. **Start small, iterate** - prove value before full build

---

## References

1. **"Thinking with Knowledge Graphs"** (arXiv 2412.10654v1) - Python representation for LLM reasoning
2. **"Why KGs Upgrade Taxonomies"** (Enterprise Knowledge) - Taxonomy → KG relationship
3. **"KG Construction Survey"** (MDPI) - Construction methodology
4. **"KGs and Taxonomies"** (Hedden) - When to use each

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-30  
**Status:** Complete scaffolding for guide
