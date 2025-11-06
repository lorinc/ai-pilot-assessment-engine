# Release 2: Discovery & Assessment Implementation Scaffold

**Duration:** Weeks 3-4  
**Status:** Planning  
**Date:** 2025-11-05

---

## Overview

Build the core assessment engine: output discovery from natural language, edge-based factor assessment, evidence tracking with Bayesian aggregation, and bottleneck identification via MIN calculation.

**Foundation:** Release 1 infrastructure (auth, persistence, streaming chat) is operational.

---

## Scope

### In Release 2
- Output discovery from user descriptions
- Edge-based assessment (4 edge types: People→Output, Tool→Output, Process→Output, Output→Output)
- Conversational rating inference (LLM infers ⭐ from user statements)
- Evidence tracking with tier classification
- Bayesian weighted aggregation
- MIN calculation for output quality
- Bottleneck identification
- Graph operations (NetworkX ↔ Firestore)

### Not in Release 2
- Context extraction (budget, timeline, visibility) → Release 3
- Recommendations engine → Release 4
- Report generation → Release 5
- Multi-output dependency traversal → Future

---

## Implementation Tasks

### 1. Graph Infrastructure (Days 1-2)

**Objective:** NetworkX graph with Firestore persistence

**Components:**

**1.1 Graph Manager (`src/core/graph_manager.py`)**
- Initialize NetworkX DiGraph
- Load/save to Firestore
- Node CRUD (Output, Tool, Process, People)
- Edge CRUD with evidence tracking
- Graph queries (find bottlenecks, traverse dependencies)

**1.2 Firestore Schema Extension**
```
/users/{user_id}/
  nodes/
    outputs/{output_id}
      - name, function, description
      - incoming_edges: [edge_id, ...]
      - calculated_score: 1-5 (cached MIN)
      - calculated_confidence: 0.0-1.0
    
    tools/{tool_id}
      - name, type, description
    
    processes/{process_id}
      - name, maturity_level, description
    
    people/{people_id}
      - archetype, description
  
  edges/{edge_id}
    - source_id, target_id, edge_type
    - current_score: 1-5
    - current_confidence: 0.0-1.0
    - evidence: [{statement, tier, timestamp, conversation_id}]
```

**Actions:**
- Implement `GraphManager` class
- Add Firestore schema helpers
- Implement graph sync (load on session start, save on changes)
- Test graph persistence across sessions

**Deliverables:**
- Graph operations working
- Firestore sync operational
- User isolation verified

---

### 2. Output Discovery Engine (Days 3-4)

**Objective:** Identify outputs from natural language descriptions

**Components:**

**2.1 Output Catalog Loader**
- Load from `src/data/organizational_templates/functions/*.json`
- Index by keywords, pain points, systems
- Semantic search preparation

**2.2 Discovery Flow**
```
User: "Sales forecasts are always wrong"
  ↓
LLM extracts: keywords=[forecast, sales], pain=[accuracy], system=[CRM]
  ↓
Match against catalog: "Sales Forecast" (confidence=0.85)
  ↓
Present for confirmation
  ↓
Infer context: Team=Sales, Process=Forecasting, System=CRM
```

**2.3 Conversation Manager Extension**
- Add discovery phase tracking
- Multi-turn refinement (if ambiguous)
- Confirmation handling

**Actions:**
- Load output catalog
- Implement LLM-based semantic matching
- Build confirmation flow
- Infer Team/Process/System from templates
- Create initial graph nodes (Output, Tool, Process, People)

**Deliverables:**
- Can identify outputs from descriptions
- Handles ambiguous cases (presents options)
- Creates graph nodes automatically

---

### 3. Assessment Engine (Days 5-7)

**Objective:** Collect edge ratings conversationally

**Components:**

**3.1 Edge Types**
- **People → Output:** Team execution capability
- **Tool → Output:** System support quality
- **Process → Output:** Process maturity impact
- **Output → Output:** Dependency quality (upstream outputs)

**3.2 Conversational Rating Inference**
```
User: "The team is junior, no one to learn from"
  ↓
LLM infers: People→Output = ⭐⭐ (Tier 3: direct statement)
  ↓
System: "I'm hearing the team capability is ⭐⭐. Is that right?"
  ↓
User confirms/adjusts
```

**3.3 Evidence Tier Classification**
- **Tier 1:** AI inferred from indirect data (weight=1)
- **Tier 2:** User mentioned indirectly (weight=3)
- **Tier 3:** User stated directly (weight=9)
- **Tier 4:** User provided example (weight=27)
- **Tier 5:** User provided quantified example (weight=81)

**3.4 Bayesian Weighted Aggregation**
```python
# Pseudocode
WAR = sum(score_i * weight_i) / sum(weight_i)
Confidence = sum(weight_i) / (sum(weight_i) + C)
Final_Score = (Confidence * WAR) + ((1 - Confidence) * μ)
```

**Actions:**
- Implement edge rating conversation flow
- Build LLM inference prompt for rating extraction
- Implement tier classifier
- Implement Bayesian aggregation
- Store evidence with edges
- Handle rating updates (later evidence outweighs earlier)

**Deliverables:**
- Can assess all 4 edge types
- Evidence properly weighted
- Ratings update as conversation progresses

---

### 4. Bottleneck Identification (Days 8-9)

**Objective:** Calculate output quality and identify bottlenecks

**Components:**

**4.1 MIN Calculation**
```python
# Pseudocode
def calculate_output_quality(output_node):
    incoming_edges = graph.get_incoming_edges(output_node)
    if not incoming_edges:
        return None
    return min(edge.score for edge in incoming_edges)
```

**4.2 Bottleneck Detection**
```python
# Pseudocode
def identify_bottlenecks(output_node):
    min_score = calculate_output_quality(output_node)
    return [edge for edge in incoming_edges if edge.score == min_score]
```

**4.3 Gap Analysis**
```
Current Quality: ⭐⭐ (MIN of all edges)
Required Quality: ⭐⭐⭐⭐ (user specified)
Gap: 2 stars
Bottleneck: People→Output (⭐⭐)
```

**Actions:**
- Implement MIN calculation
- Implement bottleneck identification
- Add required quality collection
- Calculate gap (required - current)
- Display bottleneck analysis in UI

**Deliverables:**
- Correctly calculates MIN
- Identifies bottleneck edges
- Shows gap analysis

---

### 5. UI Integration (Day 10)

**Objective:** Wire assessment flow into Streamlit UI

**Components:**

**5.1 Assessment Flow UI**
- Phase indicator (Discovery → Assessment → Analysis)
- Edge rating display (⭐ visualization)
- Evidence tracker (show what user said)
- Bottleneck visualization

**5.2 Graph Viewer (Simple)**
- Text-based graph summary
- Node list with scores
- Edge list with ratings
- Bottleneck highlighting

**Actions:**
- Add phase tracking to UI
- Create rating display components
- Add evidence viewer
- Build simple graph summary view
- Add bottleneck highlight

**Deliverables:**
- Full assessment flow in UI
- User can see ratings and evidence
- Bottleneck clearly displayed

---

## Data Files Used

### From `src/data/`
- `organizational_templates/functions/*.json` - Output catalog
- `organizational_templates/cross_functional/common_systems.json` - System defaults
- `organizational_templates/cross_functional/common_processes.json` - Process defaults
- `component_scales.json` - Rating scale definitions

### Not Used Yet (Release 3+)
- `pilot_catalog.json` → Release 4
- `pilot_types.json` → Release 4
- `capability_framework.json` → Release 4
- `inference_rules/` → Release 3-4

---

## Testing Strategy

### Unit Tests
- Graph operations (add/remove nodes/edges)
- MIN calculation with various edge configurations
- Bayesian aggregation with different evidence tiers
- Tier classification from user statements

### Integration Tests
- Full discovery flow (description → output identification)
- Full assessment flow (4 edge types rated)
- Graph persistence (save → load → verify)
- Multi-session continuity

### Demo Scenarios
**Scenario 1: Sales Forecast**
```
User: "Sales forecasts are always wrong"
→ Identifies: Sales Forecast output
→ Assesses: Team ⭐⭐, System ⭐, Process ⭐⭐, Deps ⭐⭐⭐
→ Calculates: Quality = ⭐ (MIN)
→ Bottleneck: System (⭐)
```

**Scenario 2: Support Tickets**
```
User: "Support tickets take forever"
→ Identifies: Resolved Support Tickets output
→ Assesses: Team ⭐⭐⭐, System ⭐⭐, Process ⭐, Deps ⭐⭐⭐⭐
→ Calculates: Quality = ⭐ (MIN)
→ Bottleneck: Process (⭐)
```

---

## Success Criteria

✅ Identifies outputs from natural language (>80% accuracy on test cases)  
✅ Assesses all 4 edge types conversationally  
✅ Evidence properly classified by tier  
✅ Bayesian aggregation working correctly  
✅ MIN calculation correct  
✅ Bottleneck identification accurate  
✅ Graph persists across sessions  
✅ User isolation maintained

---

## Handoff to Phase 3

**What's Ready:**
- Output identified and assessed
- Bottleneck(s) identified
- Graph persisted in Firestore

**What's Next (Release 3):**
- Extract business context (budget, timeline, visibility)
- Prepare for recommendation engine
- Handle contradictions and refinements

---

## Technical Debt to Address

- Graph traversal limited to 1 hop (no recursive dependencies yet)
- Single output per assessment (no multi-output scenarios)
- No dependency quality propagation
- Evidence tier classification is LLM-based (may need refinement)

---

**Document Status:** Ready for Implementation  
**Dependencies:** Release 1 complete  
**Owner:** Technical Lead
