# Phase 2 Implementation - Salvage Guide

**Purpose:** Reference archived code during Phase 2 implementation  
**Archive Location:** `../../../archive/phase2_placeholder/`  
**Date:** 2025-11-05

---

## Overview

The archive contains earlier exploration code that demonstrates useful patterns but needs to be **rebuilt** for Phase 2, not copied directly.

**Why rebuild?**
- Old code uses different data model (AI archetypes, not output-centric)
- Old code lacks Firestore integration
- Old code doesn't implement 1-5 star ratings or MIN calculation
- Old code is node-based, not edge-based assessment

**Use archive as:** Reference for patterns, not source for copy-paste

---

## Archived Files

### Knowledge Graph Module
**Location:** `archive/phase2_placeholder/knowledge_graph/`

#### graph_builder.py (534 lines)
**What it does:**
- Loads JSON data files into NetworkX graph
- Creates typed nodes (AI_ARCHETYPE, COMMON_MODEL, AI_OUTPUT, etc.)
- Creates typed edges (IMPLEMENTED_BY, PRODUCES_OUTPUT, REQUIRES, etc.)
- Tracks node/edge IDs to avoid duplicates

**Salvageable patterns:**
- ✅ NetworkX graph construction approach
- ✅ JSON data loading patterns
- ✅ Node/edge ID tracking to avoid duplicates
- ✅ Logging structure for graph operations
- ✅ Batch loading from multiple data sources

**What to change:**
- ❌ Node types (use: Output, Tool, Process, People)
- ❌ Edge types (use: team_execution, system_capabilities, process_maturity, dependency_quality)
- ❌ Data sources (use: organizational_templates, not AI_archetypes)
- ❌ Add Firestore sync (load/save operations)

**Key methods to reference:**
```python
# Pattern: Load data from JSON
def _load_archetypes(self) -> None:
    file_path = self.data_dir / "AI_archetypes.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Process data...

# Pattern: Create node with attributes
def _create_archetype_node(self, data: dict) -> str:
    node_id = f"archetype_{self.node_counter}"
    self.graph.add_node(
        node_id,
        node_type=NodeType.AI_ARCHETYPE,
        name=data.get("name"),
        attributes={...}
    )
    self._node_ids.add(node_id)
    return node_id

# Pattern: Create edge with relationship
def _create_edge(self, source: str, target: str, edge_type: EdgeType):
    self.graph.add_edge(
        source, target,
        relationship=edge_type,
        attributes={...}
    )
```

---

#### schemas.py (257 lines)
**What it does:**
- Pydantic models for graph nodes and edges
- Enums for node types, edge types, categories
- Validation for node/edge attributes

**Salvageable patterns:**
- ✅ Pydantic for type safety
- ✅ Enum-based type definitions
- ✅ Field validation patterns
- ✅ Base model + specific node types inheritance

**What to change:**
- ❌ Node types (AI_ARCHETYPE → Output, Tool, Process, People)
- ❌ Edge types (IMPLEMENTED_BY → team_execution, etc.)
- ❌ Add rating fields (score: 1-5, confidence: 0-1)
- ❌ Add evidence tracking (tier, statement, timestamp)

**Key patterns to reference:**
```python
# Pattern: Enum for type safety
class NodeType(str, Enum):
    OUTPUT = "output"
    TOOL = "tool"
    PROCESS = "process"
    PEOPLE = "people"

class EdgeType(str, Enum):
    TEAM_EXECUTION = "team_execution"
    SYSTEM_CAPABILITIES = "system_capabilities"
    PROCESS_MATURITY = "process_maturity"
    DEPENDENCY_QUALITY = "dependency_quality"

# Pattern: Base model + inheritance
class GraphNode(BaseModel):
    node_id: str
    node_type: NodeType
    name: str
    attributes: Dict[str, Any] = Field(default_factory=dict)

class OutputNode(GraphNode):
    node_type: Literal[NodeType.OUTPUT] = NodeType.OUTPUT
    function: str
    typical_quality_metrics: List[str]
    # ... output-specific fields

# Pattern: Field validation
@field_validator('node_id')
@classmethod
def validate_node_id(cls, v: str) -> str:
    if not v or not v.strip():
        raise ValueError("node_id cannot be empty")
    return v.strip()
```

---

#### scope_matcher.py (11016 bytes)
**What it does:**
- Matches user input to graph nodes
- Fuzzy matching for function/output names
- Scope narrowing through conversation

**Salvageable patterns:**
- ✅ Fuzzy matching approach
- ✅ Confidence scoring for matches
- ✅ Progressive refinement through questions

**What to change:**
- ❌ Match to outputs (not AI archetypes)
- ❌ Use organizational templates as source
- ❌ Integrate with LLM for semantic matching (not just fuzzy)

**Key patterns to reference:**
```python
# Pattern: Fuzzy matching with confidence
def match_output(self, user_input: str) -> List[Tuple[str, float]]:
    matches = []
    for output_id, output_data in self.outputs.items():
        score = self._calculate_similarity(user_input, output_data['name'])
        if score > 0.7:
            matches.append((output_id, score))
    return sorted(matches, key=lambda x: x[1], reverse=True)

# Pattern: Progressive refinement
def narrow_scope(self, current_matches: List, user_clarification: str):
    # Filter matches based on additional context
    # Ask follow-up questions if still ambiguous
```

---

### Test Files

#### test_graph_builder.py (252 lines)
**What it does:**
- Unit tests for graph construction
- Validates node/edge types
- Checks graph structure

**Salvageable patterns:**
- ✅ Test fixtures for graph builder
- ✅ Validation tests (all nodes have required attributes)
- ✅ Graph structure tests (directed, connected, etc.)

**What to change:**
- ❌ Update expected node/edge types
- ❌ Add tests for Firestore sync
- ❌ Add tests for MIN calculation
- ❌ Add tests for evidence tracking

**Key test patterns to reference:**
```python
# Pattern: Test graph structure
def test_graph_is_directed(self, built_graph):
    assert isinstance(built_graph, nx.DiGraph)

def test_all_nodes_have_type(self, built_graph):
    for node_id, data in built_graph.nodes(data=True):
        assert "node_type" in data
        assert data["node_type"] in [nt.value for nt in NodeType]

# Pattern: Test specific node types
def test_output_nodes_exist(self, built_graph):
    outputs = [
        node for node, data in built_graph.nodes(data=True)
        if data.get("node_type") == NodeType.OUTPUT.value
    ]
    assert len(outputs) > 0

# Pattern: Test edge relationships
def test_edges_have_ratings(self, built_graph):
    for source, target, data in built_graph.edges(data=True):
        assert "score" in data
        assert 1 <= data["score"] <= 5
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1
```

---

#### test_scope_matcher.py (15336 bytes)
**What it does:**
- Tests for output discovery from user input
- Tests for scope narrowing
- Tests for ambiguity handling

**Salvageable patterns:**
- ✅ Test cases for output discovery
- ✅ Test cases for fuzzy matching
- ✅ Test cases for ambiguous input

**What to change:**
- ❌ Update to use conversation fixtures
- ❌ Add semantic similarity tests
- ❌ Add LLM-as-judge evaluation

**Key test patterns to reference:**
```python
# Pattern: Test output discovery
def test_discover_output_from_clear_input():
    user_input = "Our sales forecasts are always wrong"
    result = discover_output(user_input)
    assert result.output_id == "sales_forecast"
    assert result.confidence > 0.85

# Pattern: Test ambiguous input
def test_discover_output_from_vague_input():
    user_input = "Support is a disaster"
    result = discover_output(user_input)
    # Should ask clarifying question
    assert result.needs_clarification == True
    assert "support tickets" in result.clarification_question.lower()
```

---

## Implementation Strategy for Phase 2

### Day 1-2: Graph Infrastructure
**Reference:** `graph_builder.py` patterns

**Build:**
1. `GraphManager` class (similar to `KnowledgeGraphBuilder`)
   - Use NetworkX DiGraph
   - Add Firestore sync (load/save)
   - Track node/edge IDs

2. Node schemas (similar to `schemas.py`)
   - OutputNode, ToolNode, ProcessNode, PeopleNode
   - Use Pydantic for validation
   - Add rating fields (score, confidence)

3. Edge schemas
   - EdgeType enum (team_execution, system_capabilities, etc.)
   - Rating attributes (score 1-5, confidence 0-1)
   - Evidence tracking (tier, statement, timestamp)

**Salvage from:**
- `graph_builder.py` lines 30-70 (initialization, build pattern)
- `schemas.py` lines 16-92 (enum + base model patterns)

---

### Day 3-4: Output Discovery
**Reference:** `scope_matcher.py` patterns

**Build:**
1. Output discovery from user input
   - Load organizational templates
   - Fuzzy matching + LLM semantic matching
   - Confidence scoring

2. Scope narrowing
   - Progressive refinement through questions
   - Ambiguity handling

**Salvage from:**
- `scope_matcher.py` (fuzzy matching patterns)
- `test_scope_matcher.py` (test cases for discovery)

---

### Day 5-7: Assessment Engine
**New implementation** (no direct archive reference)

**Build:**
1. Conversational rating inference
   - LLM extracts ratings from user statements
   - Evidence tier classification (1-5)
   - Confidence scoring

2. Edge rating updates
   - Update graph edges with ratings
   - Track evidence with timestamps
   - Sync to Firestore

**Reference for:**
- Graph update patterns from `graph_builder.py`
- Validation patterns from `schemas.py`

---

### Day 8-9: Bottleneck Identification
**New implementation** (no direct archive reference)

**Build:**
1. MIN calculation
   - Get incoming edges for output
   - Calculate MIN(team, tool, process, dependency)
   - Identify bottlenecks (edges at MIN)

2. Gap analysis
   - Compare current vs target ratings
   - Prioritize by impact

**Reference for:**
- Graph traversal patterns from `graph_builder.py`

---

## Key Differences: Old vs New

| Aspect | Old (Archive) | New (Phase 2) |
|--------|---------------|---------------|
| **Data Model** | AI archetypes, prerequisites | Output-centric (Output + 4 edges) |
| **Node Types** | AI_ARCHETYPE, COMMON_MODEL, etc. | Output, Tool, Process, People |
| **Edge Types** | IMPLEMENTED_BY, REQUIRES, etc. | team_execution, system_capabilities, etc. |
| **Ratings** | None | 1-5 stars per edge |
| **Evidence** | None | Tier 1-5 with statements |
| **Calculation** | None | MIN(4 edges) = output quality |
| **Persistence** | In-memory only | NetworkX + Firestore sync |
| **Discovery** | Fuzzy matching only | Fuzzy + LLM semantic |
| **Assessment** | None | Conversational rating inference |

---

## What NOT to Salvage

❌ **Do not copy directly:**
- Node type definitions (wrong model)
- Edge type definitions (wrong relationships)
- Data loading logic (wrong data sources)
- Test expectations (wrong data model)

❌ **Do not use:**
- AI archetype concepts
- Prerequisite categories
- Maturity dimensions (use 1-5 stars instead)

---

## What TO Salvage

✅ **Patterns to reuse:**
- NetworkX graph construction approach
- Pydantic validation patterns
- JSON data loading patterns
- Node/edge ID tracking
- Fuzzy matching approach
- Test structure and fixtures
- Logging patterns

✅ **Code snippets to reference:**
- Graph initialization (lines 30-46 in graph_builder.py)
- Node creation with attributes (lines 88-98)
- Edge creation (lines 200-220)
- Pydantic base models (lines 73-92 in schemas.py)
- Field validation (lines 86-92)
- Test fixtures (test_graph_builder.py lines 11-26)

---

## Implementation Checklist

### Before Starting
- [ ] Review this salvage guide
- [ ] Read archived code to understand patterns
- [ ] Review Phase 2 implementation plan
- [ ] Review graph storage architecture decision

### During Implementation
- [ ] Reference patterns, don't copy code
- [ ] Adapt to output-centric model
- [ ] Add Firestore sync from Day 1
- [ ] Write tests alongside implementation
- [ ] Use conversation fixtures for testing

### After Implementation
- [ ] Compare with archived code (what worked, what didn't)
- [ ] Document learnings
- [ ] Update this guide if needed

---

## Quick Reference

**Archive location:** `../../../archive/phase2_placeholder/`

**Key files:**
- `knowledge_graph/graph_builder.py` - Graph construction patterns
- `knowledge_graph/schemas.py` - Pydantic validation patterns
- `knowledge_graph/scope_matcher.py` - Output discovery patterns
- `test_graph_builder.py` - Graph testing patterns
- `test_scope_matcher.py` - Discovery testing patterns

**Use for:** Patterns and inspiration, not direct copying

**Remember:** Rebuild for output-centric model, don't port old code

---

**Status:** Ready for Phase 2 implementation  
**Last Updated:** 2025-11-05  
**Owner:** Technical Lead
