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

## Proposed Architecture Options

### Option 1: Event-Sourced Conversation Store (Recommended)

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

### Option 2: Hybrid Vector + Graph Store

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

### Option 3: Lightweight Structured Logs + Semantic Cache

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

## Recommendation: Option 1 (Event-Sourced) with Pragmatic Simplifications

### Why Event Sourcing Fits:

1. **Immutable audit trail** - Critical for assessment integrity
2. **Temporal reasoning** - Native support for "when did you say X?"
3. **Provenance tracking** - Every value change has a reason
4. **Scalability** - Append-only log scales well
5. **Debugging** - Replay events to understand LLM behavior

### Pragmatic Simplifications:

Instead of full CQRS/Event Sourcing:
- **Use Firestore subcollections** (not a separate event store)
- **Snapshot every N events** (not every state change)
- **Embed only key events** (not every turn)
- **Summarize old events** (compress after 30 days)

### Implementation Phases:

#### Phase 1: Basic Event Logging
```python
# Log every user statement that mentions a factor
log_event(
    user_id=user_id,
    event_type="user_statement",
    raw_text=user_input,
    extracted_factors=extract_factors(user_input),
    timestamp=now()
)

# Log every LLM inference about a factor
log_event(
    user_id=user_id,
    event_type="llm_inference",
    raw_text=llm_reasoning,
    inferred_factors={factor: value},
    confidence=confidence_score,
    inferred_from=[previous_event_ids]
)
```

#### Phase 2: Factor History Tracking
```python
# Maintain current state + change log
update_factor(
    user_id=user_id,
    factor_name="data_quality",
    new_value=20,
    reason_event_id=event_id,
    previous_value=None
)
```

#### Phase 3: Semantic Retrieval
```python
# Embed key events for semantic search
embed_and_index(
    event_id=event_id,
    text=event.raw_text,
    metadata={
        "user_id": user_id,
        "timestamp": event.timestamp,
        "factors": event.affected_factors
    }
)
```

#### Phase 4: Provenance Queries
```python
# "Why is data_quality only 20%?"
def explain_factor(factor_name: str, user_id: str):
    current = get_current_factor(user_id, factor_name)
    history = get_factor_history(user_id, factor_name)
    
    explanation = []
    for change in history:
        event = get_event(change.reason_event_id)
        explanation.append({
            "date": event.timestamp,
            "statement": event.raw_text,
            "impact": f"Changed from {change.previous_value} to {change.new_value}"
        })
    
    return format_explanation(factor_name, current.value, explanation)
```

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

## Next Steps

### Immediate (Week 1):
1. **Design event schema** - Define ConversationEvent and AssessmentSnapshot
2. **Set up Firestore collections** - /users/{id}/events, /factors
3. **Implement basic logging** - Log user statements and LLM inferences
4. **Test retrieval** - Query events by factor, timestamp

### Short-term (Week 2-3):
1. **Add factor history tracking** - Maintain current state + change log
2. **Implement "Why?" queries** - Fetch relevant events, format explanation
3. **Add semantic search** - Embed key events, index in vector store
4. **Test with real conversations** - Verify provenance chains work

### Medium-term (Month 2):
1. **Optimize context loading** - Summarization strategy for old events
2. **Add cross-session reasoning** - "You said X in our last conversation..."
3. **Build provenance UI** - Show reasoning chains in interface
4. **Performance tuning** - Index optimization, caching

---

## Conclusion

**Your instinct is correct:** Temporal persistence with provenance is essential for this system.

**Recommended approach:** Event-sourced conversation store (Option 1) with pragmatic simplifications.

**Key insight:** Don't just persist "what changed" → Persist "why it changed" with full reasoning chain.

**This enables:**
- ✅ "Why can't we do X?" → Reference past evidence with timestamps
- ✅ "Why is Y only 20%?" → Show inference chain from conversations
- ✅ Users can challenge values → LLM explains reasoning
- ✅ Audit trail → Track how assessments evolved

**Challenge accepted:** This is not just persistence—it's building a **memory system that reasons about its own past inferences**. That's the hard part, and it's what makes this system valuable.
