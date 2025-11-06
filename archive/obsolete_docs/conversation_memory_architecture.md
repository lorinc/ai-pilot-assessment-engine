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
- **[Generalizable Context Retrieval](#generalizable-context-retrieval)** - Two-stage system for any question
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
  /users/{user_id}/metadata:
    # Aggregate metrics for fast orientative queries
    assessment_summary:
      categories:
        data_readiness:
          completeness: 0.60  # 60% of factors assessed
          avg_confidence: 0.70
          factor_count: 15
          total_factors: 25
          last_updated: "2024-10-28T10:30:00Z"
        
        ai_capability:
          completeness: 0.40
          avg_confidence: 0.50
          factor_count: 10
          total_factors: 25
          last_updated: "2024-10-27T14:20:00Z"
      
      overall:
        total_factors_assessed: 25
        total_factors: 50
        avg_confidence: 0.60
        decision_tier: "low_risk"  # <€25k decisions
        
      capabilities:
        can_evaluate:
          - "basic_forecasting_annual"
          - "simple_automation"
        cannot_evaluate_yet:
          - "complex_forecasting_seasonal"
          - "ml_automation"
        
      last_conversation:
        topic: "data_quality"
        factor_id: "data_quality"
        timestamp: "2024-10-28T10:30:00Z"
        excerpt: "User mentioned data scattered across 5 systems"
  
  /factors/{factor_id}:
    current_value: 20  # Derived from ALL journal entries via LLM synthesis
    current_confidence: 0.75  # Based on evidence quality + quantity
    last_updated: "2024-10-28T10:30:00Z"
    category: "data_readiness"  # For aggregation
    inference_status: "unconfirmed"  # or "confirmed" or "user_provided"
    # NO inferred_from_conversation - full evidence trail is in journal entries
    
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

### Generalizable Context Retrieval

Instead of hardcoding query patterns, use a **two-stage retrieval system**:

#### Stage 1: Intent Recognition → Factor Identification

```python
def get_context_for_question(question: str, user_id: str):
    # 1. LLM extracts intent and identifies relevant factors
    intent_analysis = llm.analyze_intent(
        question=question,
        system_prompt="""
        Extract:
        1. Question type: ["why_blocker", "why_value", "what_if", "how_to", "comparison"]
        2. Mentioned entities: [projects, factors, archetypes, constraints]
        3. Relevant factors: List factor IDs that need context
        
        Return JSON: {
            "question_type": "...",
            "entities": {...},
            "relevant_factors": ["factor_id_1", "factor_id_2"],
            "needs_history": true/false,
            "needs_dependencies": true/false
        }
        """
    )
    
    # 2. Fetch context based on identified factors
    context = build_context(
        factor_ids=intent_analysis.relevant_factors,
        include_history=intent_analysis.needs_history,
        include_dependencies=intent_analysis.needs_dependencies,
        user_id=user_id
    )
    
    # 3. LLM generates answer with retrieved context
    return llm.answer_with_context(question, context)
```

#### Stage 2: Smart Context Assembly

```python
def build_context(
    factor_ids: List[str],
    include_history: bool,
    include_dependencies: bool,
    user_id: str
) -> dict:
    """
    Assembles context by:
    1. Fetching current factor states
    2. Optionally fetching journal history
    3. Optionally traversing graph for dependencies
    """
    context = {
        "factors": {},
        "dependencies": {},
        "constraints": {}
    }
    
    for factor_id in factor_ids:
        # Get current state
        current = get_factor_current_state(factor_id)
        context["factors"][factor_id] = {
            "value": current.value,
            "confidence": current.confidence,
            "last_updated": current.last_updated
        }
        
        # Add latest journal entry (always include for "why" questions)
        latest = get_latest_journal_entry(factor_id)
        if latest:
            context["factors"][factor_id]["latest_change"] = {
                "date": latest.timestamp,
                "rationale": latest.change_rationale,
                "excerpt": latest.conversation_excerpt
            }
        
        # Optionally add full history
        if include_history:
            history = get_journal_entries(factor_id, limit=5)
            context["factors"][factor_id]["history"] = [
                {
                    "date": entry.timestamp,
                    "change": f"{entry.previous_value} → {entry.new_value}",
                    "rationale": entry.change_rationale
                }
                for entry in history
            ]
        
        # Optionally traverse graph for dependencies
        if include_dependencies:
            # What factors does this depend on?
            dependencies = graph.query(
                "MATCH (f:Factor {id: $factor_id})-[:DEPENDS_ON]->(dep:Factor) RETURN dep",
                factor_id=factor_id
            )
            for dep in dependencies:
                dep_state = get_factor_current_state(dep.id)
                context["dependencies"][dep.id] = {
                    "value": dep_state.value,
                    "affects": factor_id
                }
            
            # What factors depend on this?
            dependents = graph.query(
                "MATCH (f:Factor {id: $factor_id})<-[:DEPENDS_ON]-(dependent:Factor) RETURN dependent",
                factor_id=factor_id
            )
            for dependent in dependents:
                dep_state = get_factor_current_state(dependent.id)
                context["dependencies"][dependent.id] = {
                    "value": dep_state.value,
                    "affected_by": factor_id
                }
    
    return context
```

#### Example: Handling Arbitrary Questions

```python
# Question 1: "Why can't we do Project X?"
question = "Why can't we do predictive maintenance?"

intent = llm.analyze_intent(question)
# Returns: {
#   "question_type": "why_blocker",
#   "entities": {"project": "predictive_maintenance"},
#   "relevant_factors": ["data_quality", "sensor_data", "ml_expertise"],
#   "needs_history": true,
#   "needs_dependencies": true
# }

context = build_context(
    factor_ids=["data_quality", "sensor_data", "ml_expertise"],
    include_history=True,
    include_dependencies=True,
    user_id=user_id
)

answer = llm.answer_with_context(question, context)
# LLM has all factor states, journal entries, and dependencies to explain blockers


# Question 2: "What changed in our data governance since last month?"
question = "What changed in our data governance since last month?"

intent = llm.analyze_intent(question)
# Returns: {
#   "question_type": "what_changed",
#   "entities": {"factor": "data_governance", "timeframe": "last_month"},
#   "relevant_factors": ["data_governance"],
#   "needs_history": true,
#   "needs_dependencies": false
# }

context = build_context(
    factor_ids=["data_governance"],
    include_history=True,
    include_dependencies=False,
    user_id=user_id
)

answer = llm.answer_with_context(question, context)
# LLM has journal history to show what changed


# Question 3: "If we improve data quality, what becomes possible?"
question = "If we improve data quality, what becomes possible?"

intent = llm.analyze_intent(question)
# Returns: {
#   "question_type": "what_if",
#   "entities": {"factor": "data_quality", "direction": "improve"},
#   "relevant_factors": ["data_quality"],
#   "needs_history": false,
#   "needs_dependencies": true  # Need to know what depends on this
# }

context = build_context(
    factor_ids=["data_quality"],
    include_history=False,
    include_dependencies=True,
    user_id=user_id
)

answer = llm.answer_with_context(question, context)
# LLM has dependency graph to explain what becomes unblocked
```

### Semantic Fallback for Unknown Factors

```python
def get_context_for_question(question: str, user_id: str):
    # Try structured intent extraction first
    intent = llm.analyze_intent(question)
    
    # If LLM can't identify specific factors, use semantic search
    if not intent.relevant_factors:
        # Embed question and search journal entries
        relevant_entries = vector_search(
            query=question,
            collection="journal_entries",
            filter={"user_id": user_id},
            top_k=5
        )
        
        # Extract factor IDs from retrieved entries
        factor_ids = list(set([entry.factor_id for entry in relevant_entries]))
        
        # Build context from semantically similar past discussions
        context = build_context(
            factor_ids=factor_ids,
            include_history=True,
            include_dependencies=False,
            user_id=user_id
        )
    else:
        # Use structured factor IDs from intent analysis
        context = build_context(
            factor_ids=intent.relevant_factors,
            include_history=intent.needs_history,
            include_dependencies=intent.needs_dependencies,
            user_id=user_id
        )
    
    return llm.answer_with_context(question, context)
```

### Token Budget Management

```python
def build_context(
    factor_ids: List[str],
    include_history: bool,
    include_dependencies: bool,
    user_id: str,
    max_tokens: int = 5000  # Budget for context
) -> dict:
    """
    Builds context with token budget awareness
    """
    context = {"factors": {}, "dependencies": {}}
    estimated_tokens = 0
    
    # Priority 1: Current state (always include)
    for factor_id in factor_ids:
        current = get_factor_current_state(factor_id)
        latest = get_latest_journal_entry(factor_id)
        
        factor_context = {
            "value": current.value,
            "confidence": current.confidence,
            "latest_change": {
                "date": latest.timestamp,
                "rationale": latest.change_rationale,
                "excerpt": latest.conversation_excerpt[:200]  # Truncate if needed
            }
        }
        
        tokens = estimate_tokens(factor_context)
        if estimated_tokens + tokens > max_tokens:
            break  # Hit budget limit
        
        context["factors"][factor_id] = factor_context
        estimated_tokens += tokens
    
    # Priority 2: History (if requested and budget allows)
    if include_history and estimated_tokens < max_tokens * 0.7:
        for factor_id in factor_ids:
            if estimated_tokens > max_tokens * 0.9:
                break
            
            history = get_journal_entries(factor_id, limit=3)  # Limit history depth
            history_summary = summarize_history(history)  # Compress old entries
            
            tokens = estimate_tokens(history_summary)
            if estimated_tokens + tokens <= max_tokens:
                context["factors"][factor_id]["history"] = history_summary
                estimated_tokens += tokens
    
    # Priority 3: Dependencies (if requested and budget allows)
    if include_dependencies and estimated_tokens < max_tokens * 0.85:
        for factor_id in factor_ids:
            if estimated_tokens > max_tokens:
                break
            
            deps = get_factor_dependencies(factor_id)
            context["dependencies"].update(deps)
            estimated_tokens += estimate_tokens(deps)
    
    return context
```

---

### Concrete Example Flow

**User asks:** "Why is our AI readiness score so low?"

```python
# 1. Intent analysis
intent = {
    "question_type": "why_value",
    "entities": {"metric": "ai_readiness_score"},
    "relevant_factors": ["ai_readiness_score"],  # LLM identifies this
    "needs_history": True,
    "needs_dependencies": True  # Score is composite, need components
}

# 2. Build context
context = {
    "factors": {
        "ai_readiness_score": {
            "value": 35,
            "confidence": 0.8,
            "latest_change": {
                "date": "2024-10-20",
                "rationale": "Composite score from data_quality, governance, infrastructure",
                "excerpt": "..."
            },
            "history": [...]
        }
    },
    "dependencies": {
        "data_quality": {"value": 20, "affects": "ai_readiness_score"},
        "data_governance": {"value": 15, "affects": "ai_readiness_score"},
        "ml_infrastructure": {"value": 50, "affects": "ai_readiness_score"}
    }
}

# 3. LLM generates answer
answer = """
Your AI readiness score is 35% because it's a composite of:

1. **Data Quality: 20%** (largest drag)
   Last assessed: Oct 28, 2024
   You mentioned: "Our data is scattered across 5 systems, no catalog"
   
2. **Data Governance: 15%** (also low)
   Last assessed: Oct 20, 2024
   You noted: "We don't have formal data policies yet"
   
3. **ML Infrastructure: 50%** (relatively strong)
   You have basic cloud infrastructure in place

The low data quality and governance are pulling down your overall score.
"""
```

---

## Key Principles

### 1. **LLM as Intent Router**
- Don't hardcode query patterns
- Let LLM identify relevant factors from natural language
- LLM decides what context is needed (history, dependencies, constraints)

### 2. **Graph as Navigation**
- Use knowledge graph to traverse factor relationships
- Automatically fetch dependencies when needed
- No manual mapping of "project → prerequisites"

### 3. **Journal as Evidence**
- Every factor has its own journal
- Retrieve only relevant factor journals based on question
- Latest entry always included, full history optional

### 4. **Semantic Search as Fallback**
- If structured extraction fails, use vector search
- Find similar past discussions
- Extract factors from retrieved journal entries

### 5. **Token Budget Awareness**
- Prioritize: current state > latest change > history > dependencies
- Truncate or summarize when approaching limits
- Always include enough context to answer, but no more

---

### Comparison: Hardcoded vs Generalizable

**Hardcoded approach (doesn't scale):**
```python
# Need separate function for each question type
def explain_blockers(project_name: str, user_id: str): ...
def explain_factor_value(factor_id: str, user_id: str): ...
def handle_user_challenge(factor_id: str, new_info: str): ...
# ... hundreds more?
```

**Generalizable approach (scales to any question):**
```python
# Single entry point handles all questions
def get_context_for_question(question: str, user_id: str):
    intent = llm.analyze_intent(question)  # LLM figures out what's needed
    context = build_context(intent, user_id)  # Fetch relevant data
    return llm.answer_with_context(question, context)  # LLM generates answer
```

The key insight: **Let the LLM do the routing, use the graph for navigation, use the journal for evidence.**

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
        user_id: str,
        factor_id: str,
        new_value: Any,
        rationale: str,
        conversation_excerpt: str,
        confidence: float,
        inferred_from: List[str] = None,
        session_id: str = None,
        inference_status: str = "unconfirmed",  # NEW: track if user confirmed
        user_confirmed: bool = False  # NEW: explicit confirmation flag
    ):
        # Get current value
        current = self.get_current_state(user_id, factor_id)
        
        # Create journal entry
        entry = {
            "entry_id": generate_id(),
            "timestamp": datetime.now(),
            "previous_value": current["value"] if current else None,
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
        factor_doc = self.db.collection("factors").document(factor_id)
        factor_doc.set({
            "current_value": new_value,
            "current_confidence": confidence,
            "last_updated": entry["timestamp"],
            "category": self.graph.get_factor_category(factor_id),
            "inference_status": "confirmed" if user_confirmed else inference_status
            # NO inferred_from_conversation - that's in the journal entries
        }, merge=True)
        
        # Update graph
        self.graph.update_factor_state(factor_id, new_value, confidence)
        
        # Update aggregate metrics
        self.update_assessment_summary(user_id, factor_id, entry["timestamp"], rationale[:100])
    
    def update_assessment_summary(self, user_id: str, factor_id: str, timestamp: datetime, excerpt: str):
        """
        Recalculate aggregate metrics for orientative queries
        """
        # Get all factors for this user
        all_factors = self.get_all_factors(user_id)
        
        # Group by category
        categories = {}
        for factor in all_factors:
            cat = factor.get("category", "uncategorized")
            if cat not in categories:
                categories[cat] = {
                    "factors": [],
                    "total_factors": self.graph.get_category_factor_count(cat)
                }
            categories[cat]["factors"].append(factor)
        
        # Calculate per-category metrics
        category_summary = {}
        for cat, data in categories.items():
            assessed = [f for f in data["factors"] if f.get("current_value") is not None]
            category_summary[cat] = {
                "completeness": len(assessed) / data["total_factors"],
                "avg_confidence": sum(f["current_confidence"] for f in assessed) / len(assessed) if assessed else 0,
                "factor_count": len(assessed),
                "total_factors": data["total_factors"],
                "last_updated": max(f["last_updated"] for f in assessed) if assessed else None
            }
        
        # Calculate overall metrics
        all_assessed = [f for f in all_factors if f.get("current_value") is not None]
        total_factors = sum(data["total_factors"] for data in categories.values())
        avg_confidence = sum(f["current_confidence"] for f in all_assessed) / len(all_assessed) if all_assessed else 0
        
        # Determine decision tier
        decision_tier = self.calculate_decision_tier(avg_confidence, len(all_assessed), total_factors)
        
        # Determine capabilities
        capabilities = self.calculate_capabilities(all_assessed)
        
        # Update metadata document
        metadata_doc = self.db.collection("users").document(user_id).collection("metadata").document("assessment")
        metadata_doc.set({
            "assessment_summary": {
                "categories": category_summary,
                "overall": {
                    "total_factors_assessed": len(all_assessed),
                    "total_factors": total_factors,
                    "avg_confidence": avg_confidence,
                    "decision_tier": decision_tier
                },
                "capabilities": capabilities,
                "last_conversation": {
                    "topic": self.graph.get_factor_name(factor_id),
                    "factor_id": factor_id,
                    "timestamp": timestamp,
                    "excerpt": excerpt
                }
            }
        }, merge=True)
    
    def calculate_decision_tier(self, avg_confidence: float, assessed_count: int, total_count: int) -> str:
        """
        Determine what decision tier user can make based on completeness and confidence
        """
        completeness = assessed_count / total_count if total_count > 0 else 0
        
        if avg_confidence >= 0.75 and completeness >= 0.50:
            return "medium_risk"  # €25k-€100k decisions
        elif avg_confidence >= 0.60 and completeness >= 0.30:
            return "low_risk"  # <€25k pilot decisions
        else:
            return "exploratory"  # Can explore, not decide yet
    
    def calculate_capabilities(self, assessed_factors: List[dict]) -> dict:
        """
        Determine what project types user can evaluate based on assessed factors
        Uses graph to map factors → project archetypes
        """
        factor_ids = [f["factor_id"] for f in assessed_factors if f.get("current_confidence", 0) >= 0.6]
        
        # Query graph for project archetypes enabled by these factors
        can_evaluate = self.graph.get_enabled_archetypes(factor_ids)
        cannot_evaluate = self.graph.get_disabled_archetypes(factor_ids)
        
        return {
            "can_evaluate": can_evaluate,
            "cannot_evaluate_yet": cannot_evaluate[:5]  # Top 5 next unlocks
        }
    
    def get_assessment_summary(self, user_id: str, include_unconfirmed: bool = True) -> dict:
        """
        Fast retrieval of aggregate metrics for orientative queries
        """
        metadata_doc = self.db.collection("users").document(user_id).collection("metadata").document("assessment").get()
        summary = metadata_doc.to_dict() if metadata_doc.exists else None
        
        if summary and include_unconfirmed:
            # Add unconfirmed inferences for status queries
            summary["unconfirmed_inferences"] = self.get_unconfirmed_factors(user_id)
        
        return summary
    
    def get_unconfirmed_factors(self, user_id: str) -> List[dict]:
        """
        Get all factors with inference_status = "unconfirmed"
        """
        all_factors = self.get_all_factors(user_id)
        
        unconfirmed = []
        for f in all_factors:
            if f.get("inference_status") == "unconfirmed":
                # Get evidence count from journal
                journal_entries = self.get_journal_entries(f["factor_id"])
                
                unconfirmed.append({
                    "factor_id": f["factor_id"],
                    "factor_name": self.graph.get_factor_name(f["factor_id"]),
                    "value": f["current_value"],
                    "confidence": f["current_confidence"],
                    "evidence_count": len(journal_entries),  # Cumulative evidence
                    "latest_mention": journal_entries[0]["timestamp"] if journal_entries else None
                })
        
        return unconfirmed
    
    def recalculate_factor_from_journal(self, user_id: str, factor_id: str) -> tuple[Any, float]:
        """
        Recalculate factor value from ALL journal entries via LLM synthesis
        This is the core cumulative inference mechanism
        """
        # Get all journal entries for this factor
        entries = self.get_journal_entries(factor_id)
        
        if not entries:
            return None, 0.0
        
        # Prepare evidence pieces
        evidence_pieces = [
            {
                "text": entry["conversation_excerpt"],
                "timestamp": entry["timestamp"],
                "context": entry["change_rationale"]
            }
            for entry in entries
        ]
        
        # LLM synthesizes ALL evidence
        synthesis = self.llm.synthesize_evidence(
            factor_id=factor_id,
            evidence_pieces=evidence_pieces,
            scale=self.graph.get_factor_scale(factor_id),
            prompt=f"""
            Factor: {factor_id}
            Scale: {self.graph.get_factor_scale(factor_id)}
            
            Evidence from {len(evidence_pieces)} conversation(s):
            {format_evidence_list(evidence_pieces)}
            
            Synthesize:
            1. What's the {factor_id} score based on ALL evidence?
            2. How confident are you (0-1)?
            3. Are the evidence pieces consistent or contradictory?
            
            Return: {{"value": <score>, "confidence": <0-1>}}
            """
        )
        
        return synthesis.value, synthesis.confidence
    
    def confirm_factor(self, user_id: str, factor_id: str, confirmed_value: Any = None):
        """
        User explicitly confirms or adjusts an inferred factor
        """
        current = self.get_current_state(user_id, factor_id)
        
        if confirmed_value is not None and confirmed_value != current["current_value"]:
            # User corrected the value
            self.update_factor(
                user_id=user_id,
                factor_id=factor_id,
                new_value=confirmed_value,
                rationale=f"User corrected from {current['current_value']} to {confirmed_value}",
                conversation_excerpt="User explicitly provided correction",
                confidence=0.95,  # High confidence when user provides
                user_confirmed=True
            )
        else:
            # User confirmed the inferred value
            factor_doc = self.db.collection("factors").document(factor_id)
            factor_doc.update({
                "inference_status": "confirmed",
                "current_confidence": min(current["current_confidence"] + 0.1, 1.0)  # Boost confidence
            })
    
    def get_current_state(self, user_id: str, factor_id: str):
        doc = self.db.collection("factors").document(factor_id).get()
        return doc.to_dict() if doc.exists else None
    
    def get_all_factors(self, user_id: str):
        """Get all factors for a user (for aggregation)"""
        # In practice, filter by user_id if factors are user-specific
        # For now, return all factors
        return [doc.to_dict() for doc in self.db.collection("factors").stream()]
    
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

### Orientative Query Support

The system maintains aggregate metrics for fast "where are we?" queries without scanning all factors.

```python
def handle_orientative_query(query_type: str, user_id: str):
    """
    Fast retrieval for orientative conversation patterns
    """
    # Get pre-calculated summary
    summary = journal_store.get_assessment_summary(user_id)
    
    if query_type == "status":
        # "Where are we?"
        return format_status_response(summary)
    
    elif query_type == "next_tier":
        # "What's missing?"
        return format_next_tier_response(summary)
    
    elif query_type == "where_were_we":
        # "Where were we?"
        last_conv = summary["last_conversation"]
        return format_continuity_response(last_conv, summary)
    
    elif query_type == "milestone":
        # Proactive milestone offer
        return format_milestone_response(summary)

def format_status_response(summary: dict) -> str:
    """
    Generate "where are we?" response from aggregate metrics
    """
    categories = summary["assessment_summary"]["categories"]
    overall = summary["assessment_summary"]["overall"]
    capabilities = summary["assessment_summary"]["capabilities"]
    
    response = "Here's what we've mapped out:\n\n"
    
    # Per-category status
    for cat_name, cat_data in categories.items():
        completeness_pct = int(cat_data["completeness"] * 100)
        confidence_pct = int(cat_data["avg_confidence"] * 100)
        
        response += f"**{cat_name.replace('_', ' ').title()}: {completeness_pct}% mapped, {confidence_pct}% confident**\n"
        
        # What this enables (from capabilities)
        enabled = [c for c in capabilities["can_evaluate"] if cat_name in c]
        if enabled:
            response += f"With this, you can evaluate {enabled[0].replace('_', ' ')}.\n\n"
    
    # Overall capability
    response += "**What you can do now:**\n"
    if capabilities["can_evaluate"]:
        response += f"You can evaluate {capabilities['can_evaluate'][0].replace('_', ' ')}"
        if len(capabilities["can_evaluate"]) > 1:
            response += f" and {len(capabilities['can_evaluate']) - 1} other types"
        response += ".\n\n"
    
    # Next steps
    response += "**Next steps:**\n"
    tier = overall["decision_tier"]
    if tier == "exploratory":
        response += "- Continue mapping factors → Unlock pilot decisions\n"
    elif tier == "low_risk":
        response += "- Continue mapping → Unlock medium-risk decisions (€25k-€100k)\n"
    
    if capabilities["cannot_evaluate_yet"]:
        response += f"- Assess {capabilities['cannot_evaluate_yet'][0].replace('_', ' ')} → Would unlock new project types\n"
    
    response += "\nWhat sounds most useful?"
    
    return response
```

**Key Benefits:**
- ✅ **O(1) retrieval** - No scanning all factors
- ✅ **Real-time updates** - Metrics recalculated on every factor update
- ✅ **Category-aware** - Shows progress per factor category
- ✅ **Capability-driven** - Maps factors → project archetypes via graph

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

### Release 1: Core Journal System (Week 1-2)
1. **Define factor taxonomy** - List all trackable factors
2. **Implement FactorJournalStore** - Basic CRUD operations
3. **Set up Firestore collections** - `/factors/{id}` and `/factors/{id}/journal/{entry_id}`
4. **Test basic logging** - Create journal entries, retrieve current state

### Release 2: LLM Integration (Week 3-4)
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
