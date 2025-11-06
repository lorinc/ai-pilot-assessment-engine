# Alternative B: POC Refactoring Plan

**Status:** Analysis Complete  
**Date:** 2025-11-04  
**Compatibility:** ❌ **NOT COMPATIBLE** - Major refactoring required

---

## Executive Summary

The current POC implementation is based on the **output-centric factor model** (4 components: Team, System, Process, Dependency) with MIN() calculation. Alternative B proposes a fundamentally different **edge-based factor model** where factors are effects (edges) rather than properties (components).

**Compatibility Score: 15%**
- ✅ Output identification logic (DiscoveryEngine) - Reusable
- ✅ Conversation infrastructure (Streamlit, Gemini, logging) - Reusable
- ❌ Data models - Complete redesign needed
- ❌ Assessment logic - Complete redesign needed
- ❌ Storage strategy - New graph-based approach needed
- ❌ Evidence tracking - Not implemented at all
- ❌ Bayesian aggregation - Not implemented at all

---

## Gap Analysis

### 1. Data Model Incompatibility

#### Current POC Model (data_models.py)
```
Output
  ├─ ComponentAssessment
  │   ├─ team_execution: ComponentRating (1-5 stars)
  │   ├─ system_capabilities: ComponentRating (1-5 stars)
  │   ├─ process_maturity: ComponentRating (1-5 stars)
  │   └─ dependency_quality: ComponentRating (1-5 stars)
  └─ QualityAssessment (MIN calculation)
```

**Problem:** Factors are **properties of outputs**, not edges.

#### Alternative B Model (REPRESENTATION.md)
```
Nodes:
  - Output (measurable deliverable)
  - Tool (renamed from System)
  - Process (how work gets done)
  - People (employee archetype, renamed from Team)

Edges (the factors):
  - People → Output (effect on output)
  - Tool → Output (effect on output)
  - Process → Output (effect on output)
  - Output → Output (dependency effect)

Each edge has:
  - evidence: Array[{statement, tier, timestamp, conversation_id}]
  - current_score: 1-5 stars (calculated from evidence)
  - current_confidence: 0.0-1.0 (calculated from evidence)
```

**Problem:** Factors are **edges between nodes**, not component properties.

---

### 2. Missing Core Features

#### ❌ Evidence Tracking System
- **Current:** Single `ComponentRating` with one description field
- **Required:** Array of evidence pieces with tiers (1-5), timestamps, conversation references
- **Impact:** Cannot handle contradictions, progressive refinement, or confidence growth

#### ❌ Evidence Tier Classification
- **Current:** Not implemented
- **Required:** 
  - Tier 1: AI inferred from indirect data
  - Tier 2: User mentioned indirectly
  - Tier 3: User stated directly
  - Tier 4: User provided example
  - Tier 5: User provided quantified example
- **Impact:** Cannot weight evidence properly

#### ❌ Bayesian-Weighted Ranking Algorithm
- **Current:** Not implemented
- **Required:** 
  - Weight formula: W_t = 3^(t-1)
  - WAR = WSR / TW
  - Final score: S = (TW/(TW+C)) * WAR + (C/(TW+C)) * μ
  - Global average μ = 2.0
  - Confidence threshold C = 10
- **Impact:** Cannot aggregate mixed evidence or handle low-confidence ratings

#### ❌ Graph Structure
- **Current:** Flat component structure
- **Required:** 
  - Node collections (Outputs, Tools, Processes, People)
  - Edge collection with source_id, target_id
  - Graph traversal for MIN() calculation
  - Hybrid storage (Firestore + in-memory graph)
- **Impact:** Cannot model dependencies, cross-output effects, or cascading impact

#### ❌ Node Deduplication Logic
- **Current:** Not implemented
- **Required:**
  - Semantic similarity detection before creating edges
  - 4-option prompt: same/different/different functions/unsure
  - "possible_duplicate" links for unresolved cases
  - Re-prompt when node or neighbors update
- **Impact:** Graph fragmentation, duplicate nodes, incoherent assessments

---

### 3. Architectural Mismatches

#### Storage Strategy
- **Current:** AssessmentSession model assumes single output with 4 components
- **Required:** Graph with nodes and edges, hybrid Firestore + in-memory
- **Refactoring:** Complete storage layer redesign

#### Calculation Logic
- **Current:** MIN() of 4 component ratings (simple)
- **Required:** 
  1. Calculate edge scores from evidence using Bayesian algorithm
  2. Find all incoming edges to output
  3. MIN() of edge scores
  4. Identify bottleneck edges
- **Refactoring:** New calculation engine

#### Conversation Flow
- **Current:** Linear flow through 4 components
- **Required:**
  - Vague statements → Create default nodes + edges with Tier 1 evidence
  - Specific statements → Create/update specific edges with higher tier
  - Contradictions → Keep both, force resolution if both Tier 3+
  - Unknowns → Create edge with confidence = 0.0
  - Progressive refinement → Evidence accumulates on same edge
- **Refactoring:** New conversation engine

---

## Refactoring Strategy

### Release 1: Data Model Redesign (8-12 hours)

**Goal:** Implement Alternative B data models

#### 1.1 Create New Models (4 hours)
**File:** `poc/models/graph_models.py`

**New Classes:**
- `OutputNode` - Measurable deliverable
- `ToolNode` - Software/platform (renamed from System)
- `ProcessNode` - How work gets done
- `PeopleNode` - Employee archetype (renamed from Team)
- `EvidencePiece` - Single piece of evidence with tier
- `Edge` - Factor as edge with evidence array
- `AssessmentGraph` - Graph container with nodes and edges

**Validation:**
- Unit tests for each model
- Evidence tier validation (1-5)
- Score validation (1-5 stars)
- Confidence validation (0.0-1.0)

#### 1.2 Implement Bayesian Algorithm (4 hours)
**File:** `poc/engines/bayesian_ranking.py`

**Functions:**
- `calculate_tier_weight(tier: int) -> int` - Returns 3^(t-1)
- `calculate_war(evidence: List[EvidencePiece]) -> float` - Weighted average rating
- `calculate_bayesian_score(war: float, tw: float, mu: float, c: float) -> float` - Final score
- `aggregate_evidence(evidence: List[EvidencePiece]) -> Tuple[float, float]` - Returns (score, confidence)

**Testing:**
- Unit tests matching examples from Bayesian_Ranking_Algorithm.md
- Edge cases: no evidence, single evidence, contradictory evidence

#### 1.3 Migrate Existing Data (2 hours)
**File:** `poc/utils/migration.py`

**Migration Logic:**
- Convert `ComponentAssessment` → 4 edges (People→Output, Tool→Output, Process→Output, Dependency→Output)
- Convert `ComponentRating.description` → `EvidencePiece` with Tier 3
- Preserve conversation history
- Mark migrated sessions

**Validation:**
- Test migration on sample sessions
- Verify no data loss

---

### Release 2: Graph Infrastructure (10-14 hours)

**Goal:** Implement graph storage and traversal

#### 2.1 In-Memory Graph (6 hours)
**File:** `poc/core/assessment_graph.py`

**Class:** `AssessmentGraph`

**Methods:**
- `add_node(node: Node) -> None`
- `add_edge(edge: Edge) -> None`
- `get_node(node_id: str) -> Optional[Node]`
- `get_edges_to_output(output_id: str) -> List[Edge]`
- `calculate_output_score(output_id: str) -> Tuple[int, List[str]]` - Returns (MIN score, bottleneck edge IDs)
- `detect_duplicates(node: Node) -> List[Node]` - Semantic similarity
- `to_dict() -> Dict` - Serialize for Firestore
- `from_dict(data: Dict) -> AssessmentGraph` - Deserialize from Firestore

**Testing:**
- Unit tests for all methods
- Graph traversal tests
- MIN() calculation tests
- Duplicate detection tests

#### 2.2 Firestore Integration (4 hours)
**File:** `poc/core/graph_storage.py`

**Class:** `GraphStorage`

**Methods:**
- `save_graph(user_id: str, session_id: str, graph: AssessmentGraph) -> None`
- `load_graph(user_id: str, session_id: str) -> AssessmentGraph`
- `save_node(user_id: str, session_id: str, node: Node) -> None`
- `save_edge(user_id: str, session_id: str, edge: Edge) -> None`
- `list_sessions(user_id: str) -> List[str]`

**Schema:**
```
/users/{user_id}/
  sessions/{session_id}/
    graph/
      nodes/
        outputs/{output_id}
        tools/{tool_id}
        processes/{process_id}
        people/{people_id}
      edges/{edge_id}
    conversations/{conversation_id}
```

**Testing:**
- Integration tests with Firestore emulator
- Save/load round-trip tests
- Concurrent access tests

#### 2.3 Session Manager Update (2 hours)
**File:** `poc/core/session_manager.py`

**Changes:**
- Replace `AssessmentSession` with `AssessmentGraph`
- Add graph operations to session state
- Maintain backward compatibility for conversation history

**Testing:**
- Update existing session manager tests
- Add graph-specific tests

---

### Phase 3: Evidence & Conversation Engine (12-16 hours)

**Goal:** Implement evidence tracking and conversation patterns

#### 3.1 Evidence Classifier (4 hours)
**File:** `poc/engines/evidence_classifier.py`

**Class:** `EvidenceClassifier`

**Methods:**
- `classify_tier(user_statement: str, context: Dict) -> int` - Returns tier 1-5
- `extract_score(user_statement: str) -> Optional[int]` - Extract 1-5 stars if mentioned
- `detect_contradiction(new_evidence: EvidencePiece, existing_evidence: List[EvidencePiece]) -> bool`
- `should_force_resolution(evidence_a: EvidencePiece, evidence_b: EvidencePiece) -> bool` - True if both Tier 3+

**Implementation:**
- Use Gemini for tier classification with structured prompt
- Pattern matching for explicit scores ("2 stars", "terrible", "excellent")
- Timestamp comparison for contradiction detection

**Testing:**
- Unit tests for each tier with examples from EVALUATION.md
- Contradiction detection tests
- Edge cases: ambiguous statements, mixed sentiment

#### 3.2 Conversation Patterns Engine (6 hours)
**File:** `poc/engines/conversation_patterns.py`

**Class:** `ConversationEngine`

**Methods:**
- `handle_vague_statement(user_message: str, graph: AssessmentGraph) -> Dict` - Create default nodes
- `handle_specific_statement(user_message: str, graph: AssessmentGraph) -> Dict` - Create/update specific edge
- `handle_contradiction(new_evidence: EvidencePiece, edge: Edge) -> str` - Generate resolution prompt
- `handle_unknown(user_message: str, graph: AssessmentGraph) -> Dict` - Create edge with confidence=0.0
- `handle_progressive_refinement(user_message: str, edge: Edge) -> Dict` - Add evidence to existing edge
- `detect_node_ambiguity(node_name: str, graph: AssessmentGraph) -> Optional[List[Node]]` - Find potential duplicates
- `generate_deduplication_prompt(new_node: Node, existing_nodes: List[Node]) -> str` - 4-option prompt

**Implementation:**
- Pattern matching for vague vs specific
- Evidence aggregation using Bayesian algorithm
- Context-aware duplicate detection
- Prompt templates for each pattern

**Testing:**
- Unit tests for each pattern from EVALUATION.md
- Integration tests with graph
- End-to-end conversation flow tests

#### 3.3 Discovery Engine Update (2 hours)
**File:** `poc/engines/discovery.py`

**Changes:**
- Update to work with graph structure
- Create OutputNode instead of Output model
- Integrate with ConversationEngine

**Testing:**
- Update existing discovery tests
- Add graph integration tests

---

### Phase 4: UI & Integration (6-8 hours)

**Goal:** Update Streamlit app to use new graph model

#### 4.1 App Refactoring (4 hours)
**File:** `poc/app.py`

**Changes:**
- Replace session manager with graph-based session
- Update conversation flow to use ConversationEngine
- Add graph visualization (optional, using Streamlit graphviz)
- Update sidebar to show graph stats (nodes, edges, bottlenecks)

**New Features:**
- Display current graph state
- Show evidence for each edge
- Highlight bottleneck edges
- Node deduplication UI

#### 4.2 Testing & Validation (2 hours)
**Files:** `poc/tests/integration/test_full_flow.py`

**Tests:**
- End-to-end assessment flow
- All 9 conversation patterns from EVALUATION.md
- Evidence accumulation over multiple turns
- Contradiction resolution
- Node deduplication

---

### Phase 5: Documentation & Migration (4-6 hours)

**Goal:** Update documentation and provide migration path

#### 5.1 Documentation (2 hours)
**Files:**
- Update `poc/README.md` with new architecture
- Update `poc/IMPLEMENTATION_STATUS.md` with Alternative B status
- Create `poc/MIGRATION_GUIDE.md` for existing users

#### 5.2 Backward Compatibility (2 hours)
**File:** `poc/utils/compatibility.py`

**Features:**
- Detect old vs new session format
- Auto-migrate on load
- Preserve conversation history
- Warning messages for users

---

## Implementation Roadmap

### Total Effort: 40-56 hours (1-1.5 weeks full-time)

**Week 1:**
- Days 1-2: Release 1 (Data Model Redesign)
- Days 3-4: Release 2 (Graph Infrastructure)
- Day 5: Phase 3 Start (Evidence Classifier)

**Week 2:**
- Days 1-2: Phase 3 Complete (Conversation Engine)
- Day 3: Phase 4 (UI & Integration)
- Day 4: Phase 5 (Documentation & Migration)
- Day 5: Testing & Bug Fixes

---

## Risk Assessment

### High Risk
- ❌ **Breaking Changes:** Existing sessions will not work without migration
- ❌ **Complexity:** Graph model is significantly more complex than current model
- ❌ **Testing Burden:** Need comprehensive tests for evidence aggregation

### Medium Risk
- ⚠️ **Performance:** In-memory graph may have memory limits for large assessments
- ⚠️ **UX Complexity:** Node deduplication adds friction to conversation flow
- ⚠️ **LLM Dependency:** Evidence tier classification requires reliable LLM

### Low Risk
- ✅ **Infrastructure:** Firestore and Gemini already working
- ✅ **Discovery:** Output identification logic is reusable
- ✅ **Conversation:** Streamlit chat interface is reusable

---

## Recommendation

### Option A: Full Refactoring (Recommended for Production)
**Effort:** 40-56 hours  
**Benefit:** Implements Alternative B completely, handles all conversation patterns, production-ready

**When to choose:**
- Alternative B is the chosen design
- Need to handle complex conversation patterns
- Want evidence tracking and confidence scoring
- Plan to support multiple outputs and dependencies

### Option B: Hybrid Approach (Recommended for POC Extension)
**Effort:** 20-30 hours  
**Benefit:** Add evidence tracking to current model without full graph refactoring

**Changes:**
- Add `evidence: List[EvidencePiece]` to `ComponentRating`
- Implement Bayesian aggregation for component scores
- Keep 4-component structure (Team, System, Process, Dependency)
- Add evidence tier classification
- Add contradiction detection

**When to choose:**
- Alternative B is still under evaluation
- Want to test evidence tracking without full refactoring
- Need to maintain backward compatibility
- Limited development time

### Option C: Wait for Decision (Recommended for Now)
**Effort:** 0 hours  
**Benefit:** Don't invest in refactoring until Alternative B is confirmed

**When to choose:**
- Alternative B is still a thought experiment
- Other alternatives are being explored
- Design is not finalized
- POC is sufficient for current needs

---

## Next Steps

1. **Decision:** Choose Option A, B, or C based on project priorities
2. **If Option A:** Start with Release 1 (Data Model Redesign)
3. **If Option B:** Create `HYBRID_APPROACH.md` with detailed plan
4. **If Option C:** Continue exploring alternatives in `docs/4_model_evolution/`

---

**Status:** Ready for decision  
**Last Updated:** 2025-11-04
