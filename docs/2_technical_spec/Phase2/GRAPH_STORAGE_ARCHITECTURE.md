# Graph Storage Architecture Decision

**Date:** 2025-11-05  
**Status:** Decided - Hybrid Approach  
**Phase:** 2

---

## Decision

**Use Hybrid Storage: NetworkX (in-memory) + Firestore (persistent)**

---

## Context

Phase 2 requires a graph structure to model:
- **Nodes:** Output, Tool, Process, People
- **Edges:** Relationships with ratings (Team→Output, Tool→Output, Process→Output, Output→Output)
- **Operations:** Add/remove nodes/edges, traverse graph, calculate MIN, identify bottlenecks

**Key Requirements:**
1. **Fast graph algorithms** - MIN calculation, BFS/DFS traversal, bottleneck identification
2. **Persistence** - User data must survive session end
3. **User isolation** - Each user has their own graph
4. **Session continuity** - Load previous work on login

---

## Options Evaluated

### Option 1: In-Memory Only (NetworkX)

**Approach:** Store graph in `st.session_state` using NetworkX

**Pros:**
- ✅ Fast graph operations (O(1) node/edge access)
- ✅ Rich graph algorithms built-in (BFS, DFS, shortest path)
- ✅ Simple implementation
- ✅ No Firestore query complexity

**Cons:**
- ❌ Lost on session end (user must start over)
- ❌ No persistence across browser refreshes
- ❌ Can't resume work later
- ❌ No backup if browser crashes

**Verdict:** ❌ Unacceptable - users expect persistence

---

### Option 2: Firestore Only

**Approach:** Store nodes/edges directly in Firestore, query on demand

**Pros:**
- ✅ Fully persistent
- ✅ User isolation built-in
- ✅ No sync complexity
- ✅ Firestore handles backups

**Cons:**
- ❌ Slow graph traversal (multiple Firestore queries)
- ❌ No built-in graph algorithms
- ❌ Complex queries for MIN calculation
- ❌ Expensive for frequent operations
- ❌ Latency on every node/edge access

**Verdict:** ❌ Too slow for interactive use

---

### Option 3: Hybrid (NetworkX + Firestore) ✅ RECOMMENDED

**Approach:** 
- Operate on NetworkX in-memory during session
- Sync to Firestore on changes
- Load from Firestore on session start

**Pros:**
- ✅ Fast graph operations (in-memory)
- ✅ Persistent across sessions (Firestore)
- ✅ Best of both worlds
- ✅ User isolation maintained
- ✅ Can resume work anytime

**Cons:**
- ⚠️ Sync complexity (must keep in-memory and Firestore consistent)
- ⚠️ Potential for sync conflicts (if user has multiple tabs)
- ⚠️ Slightly more code

**Verdict:** ✅ Optimal balance of performance and persistence

---

## Implementation Strategy

### Data Flow

```
Session Start:
  Firestore → Load graph → NetworkX (in-memory)
  
During Session:
  User action → Update NetworkX → Sync to Firestore
  
Session End:
  NetworkX cleared (garbage collected)
  Firestore retains data
```

### Sync Strategy

**When to Sync:**
- After adding/removing nodes
- After adding/removing edges
- After updating edge ratings
- After updating evidence

**How to Sync:**
- Write-through: Update NetworkX first, then Firestore
- Batch writes where possible (reduce Firestore calls)
- Use Firestore transactions for atomic updates

**Conflict Resolution:**
- Single-tab assumption for Phase 2 (simplest)
- Future: Add session locking or last-write-wins

---

## Firestore Schema

```
/users/{user_id}/
  graphs/{graph_id}/
    metadata:
      - created_at
      - updated_at
      - output_id (primary output being assessed)
    
    nodes/{node_id}:
      - node_type: "output" | "tool" | "process" | "people"
      - name
      - description
      - metadata (type-specific fields)
    
    edges/{edge_id}:
      - source_id
      - target_id
      - edge_type: "team_execution" | "system_capabilities" | "process_maturity" | "dependency_quality"
      - current_score: 1-5
      - current_confidence: 0.0-1.0
      - evidence: [
          {statement, tier, timestamp, conversation_id}
        ]
```

---

## NetworkX Structure

```python
# Node attributes
{
  "node_id": "sales_forecast",
  "node_type": "output",
  "name": "Sales Forecast",
  "description": "...",
  # ... other attributes
}

# Edge attributes
{
  "edge_type": "team_execution",
  "score": 2,
  "confidence": 0.7,
  "evidence": [...]
}
```

---

## GraphManager API (Conceptual)

```python
class GraphManager:
    def __init__(self, firebase_client, user_id):
        self.firebase = firebase_client
        self.user_id = user_id
        self.graph = None  # NetworkX DiGraph
    
    # Load/Save
    def load_graph(self, graph_id) -> nx.DiGraph
    def save_graph(self, graph_id) -> None
    
    # Node operations
    def add_node(self, node_id, node_type, **attributes) -> None
    def remove_node(self, node_id) -> None
    def get_node(self, node_id) -> dict
    
    # Edge operations
    def add_edge(self, source_id, target_id, edge_type, **attributes) -> None
    def remove_edge(self, source_id, target_id) -> None
    def get_edge(self, source_id, target_id) -> dict
    def update_edge_rating(self, source_id, target_id, score, confidence) -> None
    def add_evidence(self, source_id, target_id, statement, tier) -> None
    
    # Graph queries
    def calculate_output_quality(self, output_id) -> float
    def identify_bottlenecks(self, output_id) -> List[dict]
    def get_incoming_edges(self, node_id) -> List[dict]
    def get_outgoing_edges(self, node_id) -> List[dict]
```

---

## Performance Considerations

**In-Memory Operations (Fast):**
- Node/edge access: O(1)
- MIN calculation: O(E) where E = incoming edges (~4 for Phase 2)
- Bottleneck identification: O(E)
- Graph traversal: O(V + E) where V = nodes, E = edges

**Firestore Operations (Slower):**
- Load graph: ~200-500ms (one-time per session)
- Save node/edge: ~50-100ms per write
- Batch write: ~100-200ms for multiple operations

**Optimization:**
- Batch Firestore writes where possible
- Debounce rapid updates (wait 500ms before syncing)
- Cache frequently accessed data

---

## Risks & Mitigations

**Risk 1: Sync Failures**
- **Mitigation:** Retry logic with exponential backoff
- **Fallback:** Show user "Saving..." indicator, warn if sync fails

**Risk 2: Large Graphs**
- **Mitigation:** Phase 2 scope limits (1 output, ~10 nodes, ~4 edges)
- **Future:** Lazy loading for multi-output graphs

**Risk 3: Multiple Tabs**
- **Mitigation:** Phase 2 assumes single tab
- **Future:** Add session locking or conflict resolution

**Risk 4: Firestore Costs**
- **Mitigation:** Batch writes, debounce updates
- **Monitoring:** Track writes per session (target <50)

---

## Testing Strategy

**Unit Tests:**
- GraphManager CRUD operations
- Sync logic (mock Firestore)
- MIN calculation correctness
- Bottleneck identification

**Integration Tests:**
- Load graph from Firestore
- Save graph to Firestore
- Round-trip consistency (save → load → verify)
- Multiple users (isolation)

---

## Future Enhancements (Out of Scope for Phase 2)

- Multi-output graphs (dependency traversal)
- Graph versioning (undo/redo)
- Collaborative editing (multiple users)
- Graph visualization (interactive UI)
- Export/import (JSON, GraphML)

---

## Decision Rationale

**Why Hybrid?**

1. **Performance:** Interactive UX requires fast operations (<100ms)
2. **Persistence:** Users expect to resume work
3. **Simplicity:** NetworkX provides graph algorithms out-of-box
4. **Scalability:** Firestore handles user isolation and backups
5. **Cost:** Reasonable Firestore usage (~20-50 writes per session)

**Trade-offs Accepted:**
- Sync complexity (worth it for performance)
- Single-tab limitation (acceptable for Phase 2)
- Slightly more code (manageable)

---

**Status:** ✅ Decided  
**Implementation:** Phase 2 Day 1-2  
**Owner:** Technical Lead
