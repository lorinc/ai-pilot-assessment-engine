# Iteration 8: Retrieval-Augmented Conversational Extraction

**Date:** November 7, 2025  
**Status:** Design Phase  
**Estimated Effort:** 2.5 days

---

## Problem Statement

### The Challenge

We need to extract operational dependency graphs from **conversational user input** where:
- User tells their story incrementally over **20-30+ turns**
- Each turn is **1-4 sentences (~100-500 chars)**
- User references entities mentioned **many turns ago** ("those forecasts", "that system")
- We must resolve references and build a coherent graph **without context explosion**

### Why This Is Hard

**Naive Approach (Keep Full History):**
```
Turn 1: "Marketing creates forecasts" (100 chars)
Turn 2: "They use HubSpot and Excel" (50 chars)
...
Turn 30: "Those forecasts are wrong" (50 chars)

Context at Turn 30:
- Full conversation: ~3000 chars = ~1500 tokens
- Plus extraction prompt: ~500 tokens
- Plus graph state: ~1000 tokens
Total: ~3000 tokens (unsustainable)
```

**The Problem:**
- Context grows linearly with conversation length
- Most historical messages are irrelevant to current turn
- But we can't predict which old messages will be referenced
- By turn 50, context would be 5000+ tokens

### Success Criteria

1. **Scalability:** Handle 50+ turn conversations without context explosion
2. **Context efficiency:** Keep context <600 tokens regardless of turn number
3. **Reference resolution:** Resolve "those forecasts" to correct entity >90% accuracy
4. **Extraction accuracy:** Maintain >85% accuracy with retrieved context
5. **Performance:** <2s per turn processing time

---

## Solution Approach

### Core Insight: Retrieval-Augmented Extraction

**Don't keep conversation history in context. Retrieve relevant graph entities on-demand.**

### Architecture Overview

```
User Message (Turn N)
    ↓
Extract Entity Mentions ("forecasts", "Excel")
    ↓
Retrieve Relevant Context from Graph Store
    ↓
Build Minimal Context (only relevant entities)
    ↓
Extract with LLM (new entities, dependencies, quality issues)
    ↓
Update Graph Store
    ↓
Show Confirmation to User
```

### Key Design Decisions

#### Decision 1: Graph Store as Single Source of Truth

**Options Considered:**
- A) Keep conversation history + graph
- B) Keep graph only, retrieve on-demand
- C) Keep recent messages + graph

**Decision: B (Graph only)**

**Rationale:**
- Graph is structured, compact representation
- Contains all extracted information
- Can reconstruct any context via retrieval
- Conversation text is redundant once extracted

**Trade-offs:**
- ✅ Constant context size
- ✅ Scales to 100+ turns
- ⚠️ Requires good retrieval mechanism
- ⚠️ Can't recover from bad extractions easily (but human-in-loop mitigates this)

---

#### Decision 2: Entity Mention Extraction for Retrieval

**Options Considered:**
- A) Semantic search (embed message, find similar entities)
- B) Entity mention extraction + graph traversal
- C) Keyword matching

**Decision: B (Entity mention + traversal)**

**Rationale:**
- More reliable than embeddings (no semantic drift)
- Simpler than full semantic search
- Leverages graph structure (get neighborhood)
- Can use lightweight LLM call or NER

**Trade-offs:**
- ✅ Precise retrieval (exact entity matches)
- ✅ Fast (no embedding computation)
- ✅ Explainable (can show why entity was retrieved)
- ⚠️ Requires good entity mention extraction
- ⚠️ May miss semantically similar but differently named entities

---

#### Decision 3: Context Retrieval Strategy

**What to retrieve when entity is mentioned:**

```
Entity Mentioned: "campaign forecasts"
    ↓
Retrieve:
1. Entity itself (name, type, properties, quality_score)
2. Creator (Actor who created it)
3. Tool used (if applicable)
4. Upstream dependencies (what it depends on)
5. Downstream dependencies (what depends on it)
6. Quality issues (attached to entity)
```

**Rationale:**
- 1-hop neighborhood provides sufficient context
- Typical retrieval: 3-5 entities, ~300-500 tokens
- Covers most reference resolution needs
- Can expand to 2-hops if needed

**Trade-offs:**
- ✅ Compact context
- ✅ Relevant information
- ⚠️ May miss distant relationships (but rare in practice)

---

#### Decision 4: Graph Store Technology

**Options Considered:**
- A) Neo4j (full graph database)
- B) In-memory Python graph (networkx)
- C) Simple dict-based store

**Decision: Start with C (dict-based), migrate to B if needed**

**Rationale:**
- Iteration 8 is proof-of-concept
- Dict-based is simplest to implement
- Can migrate to networkx later for better traversal
- Neo4j is overkill for 20-30 entities

**Trade-offs:**
- ✅ Fast implementation
- ✅ No external dependencies
- ✅ Easy to debug
- ⚠️ Manual traversal logic
- ⚠️ Not production-ready (but fine for iteration)

---

## Technical Design

### Data Structures

```python
# Graph Store (in-memory dict-based)
class GraphStore:
    entities: dict[str, Entity]  # id -> Entity
    dependencies: list[Dependency]
    
class Entity:
    id: str
    type: EntityType  # Actor, Artifact, Tool, Activity
    name: str
    properties: dict
    quality_score: float | None
    issues: list[str]
    mentioned_turn: int
    
class Dependency:
    from_id: str
    to_id: str
    type: DependencyType  # PERFORMS, PRODUCES, DEPENDS_ON
    mentioned_turn: int
```

### Core Components

#### 1. Entity Mention Extractor

```python
def extract_entity_mentions(message: str) -> list[str]:
    """Extract potential entity references from message.
    
    Examples:
    - "those forecasts" -> ["forecasts"]
    - "the Excel file" -> ["Excel", "file"]
    - "they" -> ["they"] (pronoun, needs special handling)
    """
    
    # Use lightweight LLM call
    prompt = f"""
    Extract entity mentions from: "{message}"
    
    Include:
    - Nouns referring to outputs, teams, tools, processes
    - Pronouns (it, they, those, that)
    
    Return JSON: {{"mentions": ["entity1", "entity2"]}}
    """
    
    response = llm.generate(prompt, temperature=0.1)
    return parse_mentions(response)
```

#### 2. Entity Resolver

```python
def resolve_entities(mentions: list[str], graph: GraphStore) -> list[Entity]:
    """Resolve mentions to graph entities.
    
    Strategies:
    1. Exact name match
    2. Partial name match (fuzzy)
    3. Type-based resolution for pronouns
    """
    
    resolved = []
    
    for mention in mentions:
        # Exact match
        candidates = graph.find_by_name(mention)
        
        if len(candidates) == 1:
            resolved.append(candidates[0])
        
        elif len(candidates) > 1:
            # Ambiguous - use recency
            resolved.append(max(candidates, key=lambda e: e.mentioned_turn))
        
        else:
            # No match - might be new entity or pronoun
            if is_pronoun(mention):
                resolved.append(resolve_pronoun(mention, graph))
            # else: new entity, will be extracted
    
    return resolved
```

#### 3. Context Retriever

```python
def retrieve_context(entities: list[Entity], graph: GraphStore) -> dict:
    """Retrieve 1-hop neighborhood for entities.
    
    Returns compact context for LLM.
    """
    
    context = {
        "entities": [],
        "dependencies": [],
        "quality_issues": []
    }
    
    for entity in entities:
        # Add entity itself
        context["entities"].append(serialize_entity(entity))
        
        # Add creator (for artifacts)
        if entity.type == "Artifact" and entity.created_by:
            creator = graph.get_entity(entity.created_by)
            context["entities"].append(serialize_entity(creator))
        
        # Add dependencies
        upstream = graph.get_upstream_dependencies(entity.id)
        downstream = graph.get_downstream_dependencies(entity.id)
        context["dependencies"].extend(upstream + downstream)
        
        # Add quality issues
        if entity.issues:
            context["quality_issues"].extend([
                {"entity": entity.name, "issue": issue}
                for issue in entity.issues
            ])
    
    return context
```

#### 4. Extraction Agent

```python
def extract_with_context(message: str, context: dict) -> Extraction:
    """Extract entities/dependencies with retrieved context.
    
    Prompt includes:
    - Current message
    - Relevant entities from graph
    - Relevant dependencies
    - Quality issues
    """
    
    prompt = f"""
    You are extracting operational information from a conversation.
    
    Current message:
    "{message}"
    
    Relevant context from previous conversation:
    Entities: {format_entities(context["entities"])}
    Dependencies: {format_dependencies(context["dependencies"])}
    Quality issues: {format_issues(context["quality_issues"])}
    
    Extract:
    1. New entities (actors, artifacts, tools, activities)
    2. New dependencies (PERFORMS, PRODUCES, DEPENDS_ON)
    3. Quality issues mentioned
    4. Updates to existing entities
    
    Return JSON matching ExtractedContext schema.
    """
    
    response = llm.generate(prompt, schema=ExtractedContext)
    return parse_extraction(response)
```

#### 5. Graph Updater

```python
def update_graph(extraction: Extraction, graph: GraphStore, turn: int):
    """Merge extraction into graph store."""
    
    # Add new entities
    for entity in extraction.entities:
        if not graph.has_entity(entity.name):
            entity.mentioned_turn = turn
            graph.add_entity(entity)
        else:
            # Update existing
            graph.update_entity(entity.name, entity.properties)
    
    # Add dependencies
    for dep in extraction.dependencies:
        if not graph.has_dependency(dep.from_id, dep.to_id):
            dep.mentioned_turn = turn
            graph.add_dependency(dep)
    
    # Update quality scores
    for update in extraction.quality_updates:
        entity = graph.get_entity(update.entity_id)
        entity.quality_score = update.score
        entity.issues.extend(update.new_issues)
```

---

## Test Plan

### Test Data: Cascading Failures Story Split into Turns

**Turn 1:**
```
"Marketing creates campaign performance forecasts in HubSpot."
```

**Expected Extraction:**
- Actor: marketing team
- Activity: create campaign forecasts
- Tool: HubSpot
- Artifact: campaign forecasts

**Expected Graph State:**
```json
{
  "entities": [
    {"id": "marketing_team", "type": "Actor", "name": "marketing team"},
    {"id": "hubspot", "type": "Tool", "name": "HubSpot"},
    {"id": "campaign_forecasts", "type": "Artifact", "name": "campaign forecasts"}
  ],
  "dependencies": [
    {"from": "marketing_team", "to": "create_forecasts", "type": "PERFORMS"},
    {"from": "create_forecasts", "to": "campaign_forecasts", "type": "PRODUCES"}
  ]
}
```

---

**Turn 2:**
```
"The forecasts are based on data scattered across HubSpot, Google Analytics, and an old Excel file."
```

**Expected Behavior:**
1. Extract mentions: ["forecasts", "HubSpot", "Google Analytics", "Excel"]
2. Resolve: campaign_forecasts (from Turn 1), HubSpot (from Turn 1)
3. Retrieve context: campaign_forecasts + HubSpot + marketing_team
4. Extract: Google Analytics (new tool), Excel (new tool), quality issue

**Expected Extraction:**
- Tools: Google Analytics, Excel
- Quality issue: "scattered data sources" attached to campaign_forecasts
- Update: campaign_forecasts.issues += ["scattered data sources"]

**Expected Context Size:** ~300 tokens (3 entities + 2 dependencies)

---

**Turn 5:**
```
"Sales team takes those forecasts and builds pipeline projections in Salesforce."
```

**Expected Behavior:**
1. Extract mentions: ["those forecasts", "Sales team", "pipeline projections", "Salesforce"]
2. Resolve: "those forecasts" → campaign_forecasts (from Turn 1)
3. Retrieve context: campaign_forecasts + marketing_team + HubSpot + quality issues
4. Extract: sales team (new actor), Salesforce (new tool), pipeline projections (new artifact), dependency

**Expected Extraction:**
- Actor: sales team
- Tool: Salesforce
- Artifact: pipeline projections
- Dependency: pipeline_projections DEPENDS_ON campaign_forecasts

**Expected Context Size:** ~400 tokens (4 entities + 3 dependencies + 1 quality issue)

---

**Turn 15:**
```
"Those forecasts are always wrong because of the Excel file."
```

**Expected Behavior:**
1. Extract mentions: ["those forecasts", "Excel file"]
2. Resolve: campaign_forecasts (from Turn 1), Excel (from Turn 2)
3. Retrieve context: campaign_forecasts + Excel + marketing_team + existing issues
4. Extract: quality issue, causal link

**Expected Extraction:**
- Quality issue: "always wrong" attached to campaign_forecasts
- Update: campaign_forecasts.quality_score = 0.2 (inferred from "always wrong")
- Causal link: Excel tool affects campaign_forecasts quality

**Expected Context Size:** ~350 tokens (3 entities + 2 dependencies + 2 quality issues)

**Critical Test:** Resolves "those forecasts" correctly despite 13 turns since last mention!

---

### Test Metrics

#### 1. Context Size Test
**Goal:** Verify context stays <600 tokens across 30 turns

**Method:**
- Process all 30 turns
- Measure context size at each turn
- Plot: turn_number vs context_size

**Success Criteria:**
- Max context size: <600 tokens
- Average context size: <450 tokens
- No linear growth with turn number

---

#### 2. Reference Resolution Test
**Goal:** Verify pronouns/references resolve correctly

**Test Cases:**
| Turn | Reference | Expected Resolution | Distance (turns) |
|------|-----------|---------------------|------------------|
| 5 | "those forecasts" | campaign_forecasts | 4 |
| 8 | "they" (team) | sales team | 3 |
| 15 | "those forecasts" | campaign_forecasts | 13 |
| 20 | "that system" | Salesforce | 15 |

**Success Criteria:**
- Resolution accuracy: >90%
- Works across 10+ turn distance

---

#### 3. Extraction Accuracy Test
**Goal:** Verify extraction quality with retrieved context

**Method:**
- Compare extracted graph to expected graph
- Measure: node recall, edge accuracy, quality score correlation

**Success Criteria:**
- Node recall: >85% (find all major entities)
- Edge accuracy: >80% (correct dependencies)
- Quality score correlation: >0.7 (scores match described issues)

---

#### 4. Performance Test
**Goal:** Verify processing time is acceptable

**Method:**
- Measure time per turn: mention extraction + retrieval + extraction + update

**Success Criteria:**
- Average time per turn: <2s
- Max time per turn: <5s
- No degradation over 30 turns

---

## Implementation Plan

### Day 1: Core Infrastructure (8 hours)

**Morning (4h):**
- [ ] Implement GraphStore (dict-based)
- [ ] Implement Entity, Dependency data classes
- [ ] Write basic CRUD operations (add, get, update)
- [ ] Write unit tests for GraphStore

**Afternoon (4h):**
- [ ] Implement entity mention extractor
- [ ] Implement entity resolver (exact + fuzzy matching)
- [ ] Implement pronoun resolution
- [ ] Write unit tests for resolution

---

### Day 2: Retrieval & Extraction (8 hours)

**Morning (4h):**
- [ ] Implement context retriever (1-hop neighborhood)
- [ ] Implement context serialization (compact format)
- [ ] Write unit tests for retrieval
- [ ] Test: context size <600 tokens

**Afternoon (4h):**
- [ ] Implement extraction agent (with context)
- [ ] Implement graph updater (merge logic)
- [ ] Write unit tests for extraction
- [ ] Test: extraction with retrieved context

---

### Day 3: Integration & Testing (4 hours)

**Morning (2h):**
- [ ] Integrate all components into process_turn()
- [ ] Implement confirmation UI
- [ ] Test: single turn end-to-end

**Afternoon (2h):**
- [ ] Test: 30-turn conversation (cascading failures)
- [ ] Measure: context size, accuracy, performance
- [ ] Document results
- [ ] Create test report

---

## Expected Outcomes

### Quantitative Results

| Metric | Target | Expected |
|--------|--------|----------|
| Context size (turn 30) | <600 tokens | ~450 tokens |
| Reference resolution | >90% | ~92% |
| Node recall | >85% | ~88% |
| Edge accuracy | >80% | ~82% |
| Processing time | <2s/turn | ~1.5s/turn |

### Qualitative Results

**What we'll learn:**
1. Does retrieval-augmented approach work for conversational extraction?
2. Is entity mention extraction reliable enough?
3. Is 1-hop neighborhood sufficient context?
4. What are the failure modes?

**What we'll prove:**
- Scalability: Can handle 50+ turn conversations
- Efficiency: Constant context size regardless of length
- Accuracy: Maintains quality with retrieved context

---

## Risks & Mitigations

### Risk 1: Entity Mention Extraction Fails
**Symptom:** Misses key entity references, retrieves wrong context

**Mitigation:**
- Use LLM for mention extraction (more reliable than regex)
- Include pronouns explicitly in extraction
- Fall back to recent entities if no mentions found

**Fallback:**
- Keep last 2 entities in context as backup
- Ask user for clarification if ambiguous

---

### Risk 2: Retrieval Misses Relevant Context
**Symptom:** LLM can't resolve references, extraction incomplete

**Mitigation:**
- Expand to 2-hop neighborhood if 1-hop insufficient
- Include quality issues in retrieval (often relevant)
- Monitor retrieval precision/recall

**Fallback:**
- Ask user to clarify reference
- Show retrieved context to user for confirmation

---

### Risk 3: Graph Store Gets Corrupted
**Symptom:** Duplicate entities, inconsistent state

**Mitigation:**
- Implement entity deduplication logic
- Validate graph integrity after each update
- Human-in-loop catches errors early

**Fallback:**
- Allow user to correct/delete entities
- Implement undo functionality

---

## Success Criteria Summary

**Iteration 8 is successful if:**

1. ✅ **Scalability:** Handles 30-turn conversation with <600 token context
2. ✅ **Accuracy:** >85% node recall, >80% edge accuracy
3. ✅ **Resolution:** >90% reference resolution accuracy
4. ✅ **Performance:** <2s per turn processing time
5. ✅ **Proof of concept:** Demonstrates retrieval-augmented approach works

**If successful, proceed to Iteration 9 (Smart Reference Resolution)**

**If not successful:**
- Analyze failure modes
- Adjust retrieval strategy
- Consider hybrid approach (retrieval + recent messages)

---

## Next Iterations Preview

**Iteration 9:** Smart Reference Resolution
- Improve pronoun resolution (context-aware)
- Handle ambiguous references with clarification
- Add confidence scores to resolutions

**Iteration 10:** Incremental Quality Tracking
- Track quality degradation across turns
- Accumulate issues on entities
- Infer quality scores from language

**Iteration 11:** Dependency Chain Detection
- Detect causal dependencies across turns
- Build dependency chains incrementally
- Identify error propagation paths

---

## Appendix: Pseudo-Code for Key Functions

### Complete Process Turn Flow

```python
def process_turn(user_message: str, graph: GraphStore, turn: int) -> Response:
    """Main entry point for processing one conversation turn."""
    
    # 1. Extract entity mentions
    mentions = extract_entity_mentions(user_message)
    # ["forecasts", "Excel"]
    
    # 2. Resolve to graph entities
    entities = resolve_entities(mentions, graph)
    # [campaign_forecasts, Excel]
    
    # 3. Retrieve relevant context
    context = retrieve_context(entities, graph)
    # {entities: [...], dependencies: [...], issues: [...]}
    
    # 4. Extract with context
    extraction = extract_with_context(user_message, context)
    # New entities, dependencies, quality updates
    
    # 5. Update graph
    update_graph(extraction, graph, turn)
    
    # 6. Format confirmation
    confirmation = format_confirmation(extraction, graph)
    
    return confirmation
```

### Context Serialization

```python
def serialize_entity(entity: Entity) -> dict:
    """Compact entity representation for LLM context."""
    return {
        "name": entity.name,
        "type": entity.type,
        "quality": entity.quality_score,
        "issues": entity.issues[:3],  # Max 3 issues
        # Omit: id, mentioned_turn, full properties
    }

def format_context_for_llm(context: dict) -> str:
    """Format retrieved context as compact text."""
    
    lines = ["Relevant context:"]
    
    for entity in context["entities"]:
        line = f"- {entity['name']} ({entity['type']})"
        if entity.get("quality"):
            line += f" [quality: {entity['quality']}]"
        lines.append(line)
    
    for dep in context["dependencies"]:
        lines.append(f"- {dep['from']} → {dep['to']}")
    
    return "\n".join(lines)
```

---

## References

- Research document: `research_document.md`
- User story: `USER_STORY_CASCADING_FAILURES.md`
- Previous iterations: `ITERATION_3_FULL_TEST_DOC.md`, `ITERATION_7_FULL_TEST_DOC.md`
- Implementation roadmap: `ITERATIVE_IMPLEMENTATION_ROADMAP.md`
