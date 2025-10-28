# Conversation Memory & Temporal Tracking Architecture

## Core Insight: Factor-Centric Journal

**Key Realization:** Everything worth remembering is directly linked to a **factor**. Instead of complex event sourcing, build a simple journal system around factors themselves.

**Why This Works:**
- ✅ Factors are already first-class entities in the domain model
- ✅ Knowledge graph provides natural navigation via existing edges
- ✅ Only meaningful changes (value updates) need persistence, not every utterance
- ✅ Current state + confidence stored directly on factor for fast access
- ✅ Journal provides temporal audit trail when needed

**What to Store:**
- Value changes (before/after)
- Brief rationale for change
- Conversation excerpt (2-3 exchanges)
- Confidence score
- Links to influencing factors

---

## Quick Navigation

- **[Recommended Architecture](#recommended-architecture-factor-centric-journal)** - Factor-centric journal design
- **[Data Model](#data-model)** - FactorJournal and JournalEntry schemas
- **[Storage Structure](#storage-structure)** - Firestore collections layout
- **[Query Patterns](#query-patterns)** - "Why?" questions and user challenges
- **[Implementation](#implementation)** - FactorJournalStore class
- **[Alternative Approaches](#alternative-approaches-for-comparison)** - Event sourcing, hybrid, logs
- **[Why This Wins](#why-factor-centric-journal-wins)** - Comparison with alternatives
- **[Implementation Roadmap](#implementation-roadmap)** - 8-week phased approach

---

## Current Persistence Model

### What Exists (from architecture docs):

1. **Firebase Firestore** - Session persistence
   - Stores: `{email, last_active, intent, recommendation, score}`
   - Purpose: Resume conversations via email links
   - Limitation: **Only summary data, not full conversation history**

2. **In-Memory Logs** - Observability layer
   - Stores: Agent reasoning steps, tool calls, retrieved facts
   - Purpose: Transparency and debugging
   - Limitation: **Lost when session ends**

3. **Knowledge Graph (NetworkX)** - Domain knowledge
   - Stores: AI archetypes, prerequisites, maturity models
   - Purpose: Structured reasoning
   - Limitation: **Static, not user-specific**

4. **Vector Store (FAISS/Pinecone)** - Semantic search
   - Stores: Embedded knowledge chunks
   - Purpose: Retrieval-augmented generation
   - Limitation: **No temporal dimension, no user context**

### What's Missing:

❌ **No conversation history persistence** beyond session  
❌ **No temporal tracking** of when user provided information  
❌ **No versioning** of assessment values over time  
❌ **No inference provenance** (why the LLM concluded X)  
❌ **No cross-conversation retrieval** for answering "Why?" questions  

---

## Recommended Architecture: Factor-Centric Journal

### Data Model

```python
@dataclass
class FactorJournal:
    factor_id: str              # e.g., "data_quality", "ai_readiness.governance"
    current_value: Any          # Latest assessed value
    current_confidence: float   # LLM confidence in current value
    last_updated: datetime
    
    entries: List[JournalEntry]  # Chronological log

@dataclass
class JournalEntry:
    entry_id: str
    timestamp: datetime
    
    # Change tracking
    previous_value: Any
    new_value: Any
    change_rationale: str       # Brief: "User mentioned lack of data catalog"
    
    # Evidence
    conversation_excerpt: str   # 2-3 relevant exchanges
    confidence: float           # How certain is this inference?
    
    # Provenance
    inferred_from: List[str]    # Other factor_ids that influenced this
    session_id: str             # Link back to full conversation if needed
```

### Storage Structure

```yaml
Firestore:
  /factors/{factor_id}:
    current_value: 20
    current_confidence: 0.75
    last_updated: "2024-10-28T10:30:00Z"
    
  /factors/{factor_id}/journal/{entry_id}:
    timestamp: "2024-10-28T10:30:00Z"
    previous_value: null
    new_value: 20
    change_rationale: "User mentioned scattered data across 5 systems, no catalog"
    conversation_excerpt: |
      User: "Our data is all over the place, 5 different systems"
      Assistant: "That suggests limited data governance. Would you say you have a data catalog?"
      User: "No, nothing like that yet"
    confidence: 0.75
    inferred_from: ["data_governance", "data_infrastructure"]
    session_id: "session_abc123"
```

### Knowledge Graph Integration

The graph already has factor nodes—just add journal edges:

```python
# Existing graph structure
(Problem)-[:REQUIRES]->(Factor)
(Option)-[:DEPENDS_ON]->(Factor)
(Factor)-[:PREREQUISITE_FOR]->(AIArchetype)

# New journal edges
(Factor)-[:CURRENT_STATE]->(LatestJournalEntry)
(JournalEntry)-[:INFLUENCED_BY]->(OtherFactor)
(JournalEntry)-[:PART_OF]->(Session)
```

### Query Patterns

#### "Why can't we do Project X?"

```python
def explain_blockers(project_name: str, user_id: str):
    # 1. Get project prerequisites from graph
    required_factors = graph.query(
        "MATCH (p:Project {name: $project})-[:REQUIRES]->(f:Factor) RETURN f",
        project=project_name
    )
    
    # 2. For each unmet factor, get latest journal entry
    blockers = []
    for factor in required_factors:
        current = get_factor_current_state(factor.id)
        if not current.meets_threshold(factor.required_value):
            latest_entry = get_latest_journal_entry(factor.id)
            blockers.append({
                "factor": factor.name,
                "required": factor.required_value,
                "current": current.value,
                "confidence": current.confidence,
                "evidence": {
                    "date": latest_entry.timestamp,
                    "rationale": latest_entry.change_rationale,
                    "excerpt": latest_entry.conversation_excerpt
                }
            })
    
    return format_blockers(project_name, blockers)
```

**Output:**
```
Project X requires AI Archetype: Predictive Analytics, which depends on:

1. Data Quality ≥ 60% (currently 20%, confidence: 75%)
   Last assessed: Oct 28, 2024
   
   Rationale: User mentioned scattered data across 5 systems, no catalog
   
   From our conversation:
   > User: "Our data is all over the place, 5 different systems"
   > Assistant: "That suggests limited data governance. Would you say you have a data catalog?"
   > User: "No, nothing like that yet"

2. Historical Data Availability (currently: Limited, confidence: 80%)
   Last assessed: Oct 20, 2024
   
   Rationale: User noted only 6 months of clean data available
   ...
```

#### "Why do you think data_governance is only 20%?"

```python
def explain_factor_value(factor_id: str, user_id: str):
    # Get current state
    current = get_factor_current_state(factor_id)
    
    # Get recent journal entries (last 3-5 changes)
    history = get_journal_entries(factor_id, limit=5)
    
    # Show evolution with evidence
    return {
        "factor": factor_id,
        "current_value": current.value,
        "confidence": current.confidence,
        "reasoning_chain": [
            {
                "date": entry.timestamp,
                "change": f"{entry.previous_value} → {entry.new_value}",
                "why": entry.change_rationale,
                "evidence": entry.conversation_excerpt,
                "influenced_by": [
                    get_factor_name(fid) for fid in entry.inferred_from
                ]
            }
            for entry in history
        ]
    }
```

#### User Challenges Value

```python
User: "Actually, we DO have a data catalog now"

# 1. LLM detects challenge to existing factor value
# 2. Create new journal entry
log_journal_entry(
    factor_id="data_quality",
    previous_value=20,
    new_value=45,  # Inferred from new information
    change_rationale="User corrected: data catalog now exists",
    conversation_excerpt="""
        User: "Actually, we DO have a data catalog now"
        Assistant: "That's significant! When was it implemented?"
        User: "Last month, covers about 60% of our data sources"
    """,
    confidence=0.85,
    inferred_from=["data_governance", "data_infrastructure"]
)

# 3. Update current state
update_factor_current_state("data_quality", value=45, confidence=0.85)

# 4. Propagate to dependent factors
propagate_factor_update("data_quality")
```

### Advantages

✅ **Natural aggregation** - Factor is the domain boundary  
✅ **Simple queries** - No complex event replay  
✅ **Graph-native** - Leverages existing knowledge graph  
✅ **Minimal storage** - Only meaningful changes, not every utterance  
✅ **Easy "latest state"** - Stored directly on factor node  
✅ **Provenance built-in** - `inferred_from` links factors  

### Storage Efficiency

```
Event Sourcing Approach:
- 100 events/user/week
- 2 KB/event
- 10.4 MB/user/year

Factor Journal Approach:
- ~50 factors tracked
- ~2-3 updates/factor/month (only when value changes)
- 1 KB/journal entry (more compact, just the delta)
- 50 factors × 3 updates/month × 12 months × 1 KB = 1.8 MB/user/year

Savings: 83% less storage
```

### Context Window Management

```python
def get_context_for_question(question: str, user_id: str):
    # 1. Identify relevant factors from question
    relevant_factors = extract_factors_from_question(question)
    
    # 2. Get current state + latest journal entry for each
    context = []
    for factor_id in relevant_factors:
        current = get_factor_current_state(factor_id)
        latest = get_latest_journal_entry(factor_id)
        
        context.append({
            "factor": factor_id,
            "value": current.value,
            "confidence": current.confidence,
            "last_change": {
                "date": latest.timestamp,
                "rationale": latest.change_rationale,
                "excerpt": latest.conversation_excerpt
            }
        })
    
    # 3. If user asks "why?", get full history
    if is_why_question(question):
        for item in context:
            item["history"] = get_journal_entries(
                item["factor"], 
                limit=5
            )
    
    return context
```

**Token budget:**
- Current state: ~50 tokens/factor
- Latest journal entry: ~200 tokens/factor
- Full history (5 entries): ~1000 tokens/factor

For "Why?" question about 3 factors: ~3K tokens (very manageable)

### Implementation

```python
# /src/persistence/factor_journal.py

class FactorJournalStore:
    def __init__(self, firestore_client, graph):
        self.db = firestore_client
        self.graph = graph
    
    def update_factor(
        self,
        factor_id: str,
        new_value: Any,
        rationale: str,
        conversation_excerpt: str,
        confidence: float,
        inferred_from: List[str] = None,
        session_id: str = None
    ):
        # Get current value
        current = self.get_current_state(factor_id)
        
        # Create journal entry
        entry = {
            "entry_id": generate_id(),
            "timestamp": datetime.now(),
            "previous_value": current.value if current else None,
            "new_value": new_value,
            "change_rationale": rationale,
            "conversation_excerpt": conversation_excerpt,
            "confidence": confidence,
            "inferred_from": inferred_from or [],
            "session_id": session_id
        }
        
        # Write to Firestore
        self.db.collection("factors").document(factor_id).collection("journal").add(entry)
        
        # Update current state
        self.db.collection("factors").document(factor_id).set({
            "current_value": new_value,
            "current_confidence": confidence,
            "last_updated": entry["timestamp"]
        }, merge=True)
        
        # Update graph
        self.graph.update_factor_state(factor_id, new_value, confidence)
    
    def get_current_state(self, factor_id: str):
        doc = self.db.collection("factors").document(factor_id).get()
        return doc.to_dict() if doc.exists else None
    
    def get_journal_entries(self, factor_id: str, limit: int = None):
        query = (
            self.db.collection("factors")
            .document(factor_id)
            .collection("journal")
            .order_by("timestamp", direction="DESCENDING")
        )
        if limit:
            query = query.limit(limit)
        
        return [doc.to_dict() for doc in query.stream()]
    
    def explain_factor(self, factor_id: str):
        current = self.get_current_state(factor_id)
        history = self.get_journal_entries(factor_id, limit=5)
        
        return {
            "factor": factor_id,
            "current_value": current["current_value"],
            "confidence": current["current_confidence"],
            "last_updated": current["last_updated"],
            "reasoning_chain": history
        }
```

### Migration from Current Architecture

```python
# Current: In-memory logs lost after session
# New: Extract factor updates during conversation

def process_conversation_turn(user_input: str, llm_response: str, session_id: str):
    # Existing LLM reasoning
    reasoning = llm.process(user_input)
    
    # NEW: Extract factor updates
    factor_updates = extract_factor_updates(reasoning)
    
    for update in factor_updates:
        journal_store.update_factor(
            factor_id=update.factor_id,
            new_value=update.value,
            rationale=update.rationale,
            conversation_excerpt=format_excerpt(user_input, llm_response),
            confidence=update.confidence,
            inferred_from=update.dependencies,
            session_id=session_id
        )
    
    return llm_response
```

---

## Alternative Approaches (For Comparison)

### Option A: Event-Sourced Conversation Store

**Concept:** Treat every user statement and LLM inference as an **immutable event** in a temporal log.

#### Data Model:

```python
@dataclass
class ConversationEvent:
    event_id: str              # UUID
    session_id: str            # Links to conversation
    user_id: str               # For cross-session queries
    timestamp: datetime        # When event occurred
    event_type: str            # "user_statement" | "llm_inference" | "value_update"
    
    # Content
    raw_text: str              # Original user input or LLM output
    structured_data: dict      # Extracted entities/values
    
    # Provenance
    inferred_from: List[str]   # Event IDs that led to this inference
    confidence: float          # LLM confidence in inference
    
    # Impact
    affected_factors: List[str] # Which assessment factors changed
    factor_deltas: dict        # Before/after values
    
    # Retrieval
    embedding: List[float]     # For semantic search
    tags: List[str]            # ["data_quality", "governance", "project_x"]

@dataclass
class AssessmentSnapshot:
    snapshot_id: str
    timestamp: datetime
    factors: dict              # Current state of all tracked factors
    derived_from: List[str]    # Event IDs that built this state
```

#### Storage:

```yaml
Firestore Collections:
  
  /users/{user_id}/events/{event_id}:
    - Append-only log of all conversation events
    - Indexed by timestamp, event_type, tags
    - Embedded vectors stored for semantic search
  
  /users/{user_id}/snapshots/{snapshot_id}:
    - Periodic snapshots of assessment state
    - Enables "time travel" queries
    - Stores provenance chain
  
  /users/{user_id}/factors/{factor_name}:
    - Current value + history of changes
    - Each change links to event_id
    - Enables "Why is data_quality=20%?" queries
```

#### Query Patterns:

```python
# "Why can't we do project X?"
def answer_why_not(project_name: str, user_id: str):
    # 1. Retrieve project prerequisites
    prereqs = get_project_prerequisites(project_name)
    
    # 2. For each unmet prerequisite, find relevant events
    explanations = []
    for prereq in prereqs:
        events = query_events(
            user_id=user_id,
            tags=[prereq.factor_name],
            event_type="user_statement",
            order_by="timestamp DESC",
            limit=3
        )
        explanations.append({
            "factor": prereq.factor_name,
            "current_value": get_current_factor_value(prereq.factor_name),
            "evidence": [
                {
                    "statement": e.raw_text,
                    "date": e.timestamp,
                    "confidence": e.confidence
                }
                for e in events
            ]
        })
    
    return format_explanation(project_name, explanations)

# Example output:
"""
According to my understanding, Project X requires:

1. **Data Quality ≥ 60%** (currently 20%)
   - You mentioned on 2024-10-15: "Our data is scattered across 5 systems"
   - You said on 2024-10-20: "We don't have a data catalog yet"
   - This suggests limited data governance and quality controls

2. **AI Archetype: Predictive Analytics** (requires dependencies not met)
   - On 2024-10-18 you noted: "We barely have historical data"
   - Predictive models need 2+ years of clean historical data
"""
```

#### Advantages:
✅ **Full audit trail** - Every inference is traceable  
✅ **Temporal reasoning** - "You said X on [date]"  
✅ **Queryable provenance** - "Why do you think Y?" → Show event chain  
✅ **Scalable** - Firestore handles millions of events  
✅ **Semantic search** - Embed events for "similar past discussions"  

#### Challenges:
⚠️ **Storage cost** - Events accumulate (mitigate: compress old events)  
⚠️ **Query complexity** - Need efficient indexing strategy  
⚠️ **Context window** - Still need to summarize for LLM (but now with provenance)  

---

### Option B: Hybrid Vector + Graph Store

**Concept:** Combine vector embeddings (for semantic search) with a knowledge graph (for reasoning chains).

#### Architecture:

```yaml
Vector Store (Pinecone/Vertex AI):
  - Embed every user statement and LLM inference
  - Metadata: {timestamp, session_id, factor_tags, confidence}
  - Enables: "Find all past discussions about data quality"

Knowledge Graph (Neo4j or NetworkX + Firestore):
  Nodes:
    - ConversationTurn (user input + LLM response)
    - FactorValue (assessment value at a point in time)
    - Inference (LLM reasoning step)
  
  Edges:
    - (ConversationTurn)-[:INFERRED]->(FactorValue)
    - (FactorValue)-[:BASED_ON]->(ConversationTurn)
    - (Inference)-[:REFERENCES]->(ConversationTurn)
    - (FactorValue)-[:SUPERSEDES]->(PreviousFactorValue)
```

#### Query Example:

```cypher
// "Why is data_governance only 20%?"
MATCH (current:FactorValue {name: "data_governance", is_current: true})
MATCH (current)-[:BASED_ON]->(turn:ConversationTurn)
MATCH (turn)-[:PART_OF]->(session:Session)
RETURN turn.user_input, turn.timestamp, turn.llm_reasoning
ORDER BY turn.timestamp DESC
LIMIT 5
```

#### Advantages:
✅ **Powerful queries** - Graph traversal for complex reasoning  
✅ **Semantic search** - Vector store for "similar discussions"  
✅ **Explainability** - Visualize reasoning chains  

#### Challenges:
⚠️ **Complexity** - Two systems to maintain  
⚠️ **Cost** - Neo4j hosting or complex Firestore queries  
⚠️ **Sync issues** - Keep vector and graph in sync  

---

### Option C: Lightweight Structured Logs + Semantic Cache

**Concept:** Persist structured conversation logs with semantic embeddings for retrieval.

#### Data Model:

```python
@dataclass
class ConversationTurn:
    turn_id: str
    session_id: str
    timestamp: datetime
    
    user_input: str
    llm_response: str
    
    # Structured extraction
    extracted_facts: List[dict]  # [{factor: "data_quality", value: 20, confidence: 0.8}]
    mentioned_factors: List[str]  # Tags for retrieval
    
    # Embeddings
    input_embedding: List[float]
    response_embedding: List[float]

@dataclass
class FactorHistory:
    factor_name: str
    current_value: Any
    history: List[dict]  # [{value, timestamp, turn_id, reasoning}]
```

#### Storage:

```yaml
Firestore:
  /users/{user_id}/conversations/{session_id}/turns/{turn_id}:
    - Full conversation history
    - Indexed by timestamp, mentioned_factors
  
  /users/{user_id}/factors/{factor_name}:
    - Current value + change history
    - Each change links to turn_id

Vector Store:
  - Embed each turn for semantic search
  - Metadata: {user_id, session_id, timestamp, factors}
```

#### Retrieval Strategy:

```python
def answer_why_question(question: str, user_id: str):
    # 1. Semantic search for relevant past turns
    relevant_turns = vector_search(
        query=question,
        filter={"user_id": user_id},
        top_k=5
    )
    
    # 2. Fetch full turn context from Firestore
    turn_details = [
        get_turn_details(turn.turn_id)
        for turn in relevant_turns
    ]
    
    # 3. Build context for LLM
    context = {
        "question": question,
        "relevant_history": turn_details,
        "current_factors": get_current_factors(user_id)
    }
    
    # 4. LLM generates answer with citations
    return llm.generate_with_citations(context)
```

#### Advantages:
✅ **Simpler** - One primary store (Firestore) + vector index  
✅ **Cost-effective** - Firestore free tier covers moderate usage  
✅ **Fast retrieval** - Semantic search finds relevant context  

#### Challenges:
⚠️ **Less structured** - Harder to do complex reasoning queries  
⚠️ **Manual extraction** - Need to parse factors from conversation  

---

## Why Factor-Centric Journal Wins

**Compared to Event Sourcing:**
- ✅ Simpler - No event replay needed
- ✅ More efficient - 83% less storage
- ✅ Domain-aligned - Factors are natural boundaries
- ✅ Easier queries - Direct factor lookup vs event reconstruction

**Compared to Hybrid Vector+Graph:**
- ✅ Less complexity - One storage system (Firestore)
- ✅ Lower cost - No Neo4j hosting
- ✅ No sync issues - Single source of truth

**Compared to Structured Logs:**
- ✅ More structured - Factor-centric vs turn-centric
- ✅ Better provenance - Explicit `inferred_from` links
- ✅ Graph integration - Leverages existing edges

---

## Storage Cost Analysis

### Firestore Pricing (Free Tier):
- **Stored data:** 1 GB free
- **Document reads:** 50,000/day free
- **Document writes:** 20,000/day free

### Estimated Usage:
```
Assumptions:
- 10 active users
- 5 conversations/user/week
- 20 turns/conversation
- 100 events/user/week

Storage per event: ~2 KB (text + metadata)
Storage per user/year: 100 events/week × 52 weeks × 2 KB = 10.4 MB
Storage for 10 users/year: 104 MB

Reads per "Why?" query: ~10 events = 10 reads
Writes per conversation: 20 turns × 2 events/turn = 40 writes

Daily writes (10 users, 1 conversation/day): 400 writes
Daily reads (10 users, 2 "Why?" queries/day): 200 reads
```

**Verdict:** Well within free tier for MVP; scales to 100+ users before costs kick in.

---

## Context Window Management

### Problem:
Even with event storage, you can't load 1000+ events into LLM context.

### Solution: Staged Retrieval + Summarization

```python
def get_context_for_question(question: str, user_id: str):
    # 1. Semantic search for relevant events (top 10)
    relevant_events = vector_search(
        query=question,
        filter={"user_id": user_id},
        top_k=10
    )
    
    # 2. Fetch full event details
    events = [get_event(e.event_id) for e in relevant_events]
    
    # 3. If too many tokens, summarize older events
    if estimate_tokens(events) > 5000:
        recent_events = events[:5]  # Keep recent ones full
        old_events = events[5:]
        old_summary = llm.summarize(old_events)
        context = recent_events + [old_summary]
    else:
        context = events
    
    return context
```

---

## Anti-Pattern: What NOT to Do

❌ **Don't:** Store only final assessment values  
✅ **Do:** Store the reasoning chain that led to those values

❌ **Don't:** Rely on LLM memory across sessions  
✅ **Do:** Explicitly retrieve and inject past context

❌ **Don't:** Treat all events equally  
✅ **Do:** Weight recent events higher, summarize old ones

❌ **Don't:** Let users arbitrarily change values  
✅ **Do:** Require narrative evidence, log the justification

---

## Implementation Roadmap

### Phase 1: Core Journal System (Week 1-2)
1. **Define factor taxonomy** - List all trackable factors
2. **Implement FactorJournalStore** - Basic CRUD operations
3. **Set up Firestore collections** - `/factors/{id}` and `/factors/{id}/journal/{entry_id}`
4. **Test basic logging** - Create journal entries, retrieve current state

### Phase 2: LLM Integration (Week 3-4)
1. **Extract factor updates from conversation** - Parse LLM reasoning for value changes
2. **Auto-generate rationales** - LLM summarizes why value changed
3. **Create conversation excerpts** - Format relevant exchanges
4. **Implement confidence scoring** - LLM assesses certainty

### Phase 3: Query & Explanation (Week 5-6)
1. **"Why can't we do X?" queries** - Fetch prerequisites, explain blockers
2. **"Why is Y only Z%?" queries** - Show reasoning chain with evidence
3. **User challenges** - Detect corrections, update journal
4. **Cross-factor propagation** - Update dependent factors

### Phase 4: Optimization (Week 7-8)
1. **Add semantic search** - Embed journal entries for similarity search
2. **Context window management** - Smart retrieval based on question type
3. **Performance tuning** - Index optimization, caching
4. **UI integration** - Display provenance in interface

---

## Conclusion

**Your intuition is spot-on:** Build the memory system around factors, not events or conversations.

**Recommended approach:** Factor-Centric Journal with Firestore + Knowledge Graph integration.

**Key insight:** Factors are the natural aggregation boundary—everything worth remembering maps to a factor value change.

**This enables:**
- ✅ "Why can't we do X?" → Show prerequisite gaps with dated evidence
- ✅ "Why is Y only 20%?" → Display reasoning chain from journal entries
- ✅ Users challenge values → LLM explains with conversation excerpts
- ✅ Audit trail → Track how assessments evolved over time
- ✅ Cross-factor reasoning → `inferred_from` links show dependencies

**Architecture benefits:**
- 83% less storage than event sourcing
- Simpler queries (no event replay)
- Graph-native (leverages existing edges)
- Domain-aligned (factors are first-class entities)

**This is not just persistence—it's building a memory system that reasons about its own past inferences, grounded in the domain model.**
