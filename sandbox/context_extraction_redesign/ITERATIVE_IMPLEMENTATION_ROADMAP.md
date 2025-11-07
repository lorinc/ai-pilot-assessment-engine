# Iterative Implementation Roadmap: From Research to Reality

**Context:** Extracting operational dependency graphs from the "Cascading Failures" user story
**Challenge:** Brutally hard - 4 interim outputs, 3 teams, 3 tools, informal processes, cascading quality degradation
**Current State:** Iteration 3 achieves 66.8% accuracy on simpler cases

---

## Analysis: What Makes This Story Hard

### Complexity Factors
1. **Long narrative** (~2000 chars) - exceeds single-context window sweet spot
2. **Implicit causality** - "marketing's 10% error → sales makes it 15% → production makes it 25%"
3. **Informal processes** - "sales managers calling production directly", "holding back capacity just in case"
4. **Quality propagation** - errors compound across 4 stages, but no explicit quality scores mentioned
5. **Missing traceability** - "connections are completely lost", "no data trail"
6. **Ambiguous ownership** - "everyone's pointing fingers"

### What Research Document Recommends
- **Agentic Multi-Step Workflow** (not single-pass)
- **Specialized agents** for nodes, edges, scoring
- **Entity disambiguation** (marketing team = marketing team)
- **Validation loops** with JSONPatch retries
- **LLM-as-a-Judge** for numeric scoring
- **Causal reasoning** with intrinsic correction (CoVe)

### What We Learned from Iteration 7
- ❌ **Don't** use custom formats (triplets failed catastrophically)
- ❌ **Don't** fight model's training data (JSON > triplets)
- ✅ **Do** use familiar formats
- ✅ **Do** keep extraction holistic when possible

---

## Proposed Iterative Path: 8 Vertical Slices

### Philosophy
- **TDD:** Write test first, implement minimal solution, refactor
- **Vertical slicing:** Each iteration delivers end-to-end value
- **UAT checkpoints:** Test with real user story after each iteration
- **Fail fast:** If approach doesn't work, pivot quickly

---

## Iteration 8: Baseline Multi-Step (Node Extraction Only)

### Goal
Prove that multi-step extraction works better than single-pass for this complex story.

### Scope
**Extract only nodes** (Actors, Activities, Artifacts) - no edges yet.

### Implementation
```python
# Stage 1: Preprocessing (chunk the long story)
def chunk_narrative(text: str) -> list[str]:
    """Split into semantic chunks (~500 chars each)."""
    # Use sentence boundaries, keep context overlap
    
# Stage 2: Node extraction per chunk
def extract_nodes_from_chunk(chunk: str) -> NodeCollection:
    """Extract Actor, Activity, Artifact nodes."""
    # Simplified schema - just nodes, no edges
    # Use Iteration 3's conversational prompt style
    
# Stage 3: Entity disambiguation
def merge_duplicate_nodes(chunks: list[NodeCollection]) -> NodeCollection:
    """Merge "marketing team" across chunks."""
    # Simple string matching + LLM confirmation
```

### Test Case
**Input:** Full cascading failures story
**Expected Output:**
- 3 Actors: marketing team, sales team, production planning team
- 3 Tools: HubSpot, Salesforce, Excel
- 4 Artifacts: campaign forecasts, pipeline projections, production forecasts, manufacturing orders
- ~6 Activities: create forecasts, adjust projections, export data, etc.

**Success Criteria:** >80% node recall (find all major entities)

### Estimated Effort
- TDD RED: 0.5 day (write test with expected nodes)
- TDD GREEN: 1 day (implement chunking + extraction)
- UAT: 0.5 day (test on user story, measure recall)

**Deliverable:** Proof that chunking + multi-step > single-pass for long narratives

---

## Iteration 9: Add Simple Edges (PERFORMS, PRODUCES)

### Goal
Extract straightforward relationships before tackling complex causal edges.

### Scope
Add **PERFORMS** (Actor → Activity) and **PRODUCES** (Activity → Artifact) edges.

### Implementation
```python
# Stage 3: Relationship extraction (simple edges only)
def extract_simple_edges(nodes: NodeCollection, chunk: str) -> EdgeCollection:
    """Extract PERFORMS and PRODUCES edges."""
    # Prompt: "Which actor performs which activity?"
    # Prompt: "Which activity produces which artifact?"
    # Use node names from Stage 2 as context
```

### Test Case
**Expected Edges:**
- marketing team PERFORMS "create campaign forecasts"
- "create campaign forecasts" PRODUCES "campaign forecasts"
- sales team PERFORMS "adjust projections"
- "adjust projections" PRODUCES "pipeline projections"
- production planning team PERFORMS "generate production orders"
- etc.

**Success Criteria:** >70% edge accuracy (correct source/target pairing)

### Estimated Effort
- TDD RED: 0.5 day
- TDD GREEN: 1 day
- UAT: 0.5 day

**Deliverable:** Basic graph structure (nodes + simple edges)

---

## Iteration 10: Add Causal Edges (DEPENDS_ON)

### Goal
Extract the critical upstream dependencies that show how errors propagate.

### Scope
Add **DEPENDS_ON** edges (Activity → Artifact) showing causal prerequisites.

### Implementation
```python
# Stage 4: Causal reasoning agent
def extract_causal_edges(nodes: NodeCollection, edges: EdgeCollection, chunk: str) -> CausalEdges:
    """Extract DEPENDS_ON relationships."""
    # Use Chain-of-Verification (CoVe) for reasoning
    # Prompt: "What upstream artifacts does this activity depend on?"
    # Prompt: "Is this dependency necessary or just temporal?"
```

### Test Case
**Expected Causal Edges:**
- "adjust projections" DEPENDS_ON "campaign forecasts"
- "generate production orders" DEPENDS_ON "pipeline projections"
- "manufacturing orders" DEPENDS_ON "production forecasts"

**Success Criteria:** >60% causal edge accuracy (hard problem!)

### Estimated Effort
- TDD RED: 0.5 day
- TDD GREEN: 1.5 days (causal reasoning is hard)
- UAT: 0.5 day

**Deliverable:** Complete dependency graph showing error propagation paths

---

## Iteration 11: Add Validation Loop (Schema Compliance)

### Goal
Ensure extracted graph is structurally valid before scoring.

### Scope
Implement Pydantic validation + retry loop (NOT JSONPatch yet - keep it simple).

### Implementation
```python
# Validation loop
def extract_with_validation(chunk: str, max_retries: int = 3) -> ExtractedGraph:
    """Extract with automatic retry on validation failure."""
    for attempt in range(max_retries):
        try:
            result = extract_nodes_and_edges(chunk)
            validated = ExtractedGraph(**result)  # Pydantic validation
            return validated
        except ValidationError as e:
            # Feed error back to LLM
            result = retry_with_error_feedback(chunk, result, e)
    raise ExtractionFailure("Max retries exceeded")
```

### Test Case
**Inject schema violations:**
- Missing required field (e.g., Actor.name)
- Wrong type (e.g., string instead of float)
- Invalid enum value

**Success Criteria:** 100% schema compliance after retries

### Estimated Effort
- TDD RED: 0.5 day
- TDD GREEN: 1 day
- UAT: 0.5 day

**Deliverable:** Reliable extraction with guaranteed schema compliance

---

## Iteration 12: Add Quality Scoring (LLM-as-a-Judge)

### Goal
Quantify node and edge quality to identify weak points in the operational chain.

### Scope
Separate scoring agent that assigns numeric quality scores.

### Implementation
```python
# Phase A: Extraction (existing)
graph = extract_with_validation(story)

# Phase B: Scoring (new)
def score_graph(graph: ExtractedGraph, source_text: str) -> ScoredGraph:
    """Add quality scores to nodes and edges."""
    
    # Score nodes (Artifact quality)
    for artifact in graph.artifacts:
        artifact.data_quality_score = score_artifact_quality(artifact, source_text)
        # Rubric: specificity, source citation, coherence
    
    # Score edges (Causal certainty)
    for edge in graph.causal_edges:
        edge.causal_certainty_score = score_causal_strength(edge, source_text)
        # Rubric: explicit language, necessity, confidence markers
        
        edge.error_propagation_factor = score_error_risk(edge, source_text)
        # Rubric: mentioned errors, quality issues, compounding effects
```

### Test Case
**Expected Scores (from story):**
- "campaign forecasts" data_quality_score: 0.3 (stale data, scattered sources)
- "pipeline projections" data_quality_score: 0.4 (inconsistent adjustments, out of date)
- "production forecasts" data_quality_score: 0.2 (3-4 weeks old data)
- DEPENDS_ON edges: error_propagation_factor: 0.7-0.9 (high compounding risk)

**Success Criteria:** Scores correlate with described quality issues

### Estimated Effort
- TDD RED: 0.5 day (define rubrics)
- TDD GREEN: 1.5 days (implement scoring agent)
- UAT: 0.5 day

**Deliverable:** Quantified operational graph showing quality bottlenecks

---

## Iteration 13: Optimize with JSONPatch Retries

### Goal
Make validation loop more efficient for large graphs.

### Scope
Replace full regeneration with targeted JSONPatch corrections.

### Implementation
```python
def retry_with_jsonpatch(chunk: str, result: dict, error: ValidationError) -> dict:
    """Generate JSONPatch to fix specific error."""
    # Format error message with expected schema
    # Prompt: "Generate JSONPatch to fix this field"
    # Apply patch to existing result (don't regenerate everything)
    patch = llm.generate_jsonpatch(error, result)
    return jsonpatch.apply_patch(result, patch)
```

### Test Case
**Measure efficiency:**
- Before: Full regeneration takes ~5s, 2000 tokens
- After: JSONPatch takes ~1s, 200 tokens

**Success Criteria:** 5x speedup on retry operations

### Estimated Effort
- TDD RED: 0.5 day
- TDD GREEN: 1 day
- UAT: 0.5 day

**Deliverable:** Production-ready extraction with efficient error correction

---

## Iteration 14: Add Intrinsic Correction (CoVe for Causal Reasoning)

### Goal
Improve causal edge accuracy by having LLM verify its own reasoning.

### Scope
Implement Chain-of-Verification for causal extraction step.

### Implementation
```python
def extract_causal_edges_with_cove(nodes, edges, chunk):
    """Extract causal edges with self-verification."""
    
    # Step 1: Initial extraction
    initial_edges = extract_causal_edges_initial(nodes, edges, chunk)
    
    # Step 2: Generate verification questions
    questions = generate_verification_questions(initial_edges)
    # e.g., "Is 'pipeline projections' truly necessary for 'production orders'?"
    
    # Step 3: Answer questions
    answers = answer_verification_questions(questions, chunk)
    
    # Step 4: Revise based on answers
    revised_edges = revise_causal_edges(initial_edges, answers)
    
    return revised_edges
```

### Test Case
**Measure improvement:**
- Before CoVe: 60% causal edge accuracy
- After CoVe: Target 75% causal edge accuracy

**Success Criteria:** 15pp improvement in causal edge accuracy

### Estimated Effort
- TDD RED: 0.5 day
- TDD GREEN: 1.5 days
- UAT: 0.5 day

**Deliverable:** High-confidence causal reasoning for complex dependencies

---

## Iteration 15: End-to-End Integration + Neo4j Export

### Goal
Complete pipeline from user story → validated graph → Neo4j database.

### Scope
Integrate all stages + export to graph database for querying.

### Implementation
```python
def extract_operational_graph(user_story: str) -> Neo4jGraph:
    """End-to-end extraction pipeline."""
    
    # Stage 1: Chunk
    chunks = chunk_narrative(user_story)
    
    # Stage 2: Extract nodes per chunk
    node_collections = [extract_nodes_from_chunk(c) for c in chunks]
    
    # Stage 3: Disambiguate
    nodes = merge_duplicate_nodes(node_collections)
    
    # Stage 4: Extract simple edges
    simple_edges = extract_simple_edges(nodes, user_story)
    
    # Stage 5: Extract causal edges (with CoVe)
    causal_edges = extract_causal_edges_with_cove(nodes, simple_edges, user_story)
    
    # Stage 6: Validate (with JSONPatch retries)
    graph = validate_graph(nodes, simple_edges, causal_edges)
    
    # Stage 7: Score (LLM-as-a-Judge)
    scored_graph = score_graph(graph, user_story)
    
    # Stage 8: Export to Neo4j
    neo4j_graph = export_to_neo4j(scored_graph)
    
    return neo4j_graph
```

### Test Case
**Full pipeline test on cascading failures story:**
- Input: 2000 char user story
- Output: Neo4j graph with ~15 nodes, ~20 edges, quality scores
- Query: "Show me the path from marketing forecasts to overstock"
- Query: "Which dependency has the highest error propagation risk?"

**Success Criteria:** 
- Complete extraction in <30s
- >75% overall accuracy
- Queryable graph in Neo4j

### Estimated Effort
- TDD RED: 0.5 day
- TDD GREEN: 1.5 days (integration + Neo4j export)
- UAT: 1 day (full testing + documentation)

**Deliverable:** Production-ready operational graph extraction system

---

## Summary: 8 Iterations, ~16 Days

| Iteration | Focus | Effort | Cumulative |
|-----------|-------|--------|------------|
| 8 | Multi-step nodes | 2 days | 2 days |
| 9 | Simple edges | 2 days | 4 days |
| 10 | Causal edges | 2.5 days | 6.5 days |
| 11 | Validation loop | 2 days | 8.5 days |
| 12 | Quality scoring | 2.5 days | 11 days |
| 13 | JSONPatch optimization | 2 days | 13 days |
| 14 | CoVe intrinsic correction | 2.5 days | 15.5 days |
| 15 | End-to-end integration | 3 days | 18.5 days |

**Total: ~19 days (4 weeks) with UAT checkpoints every 2-3 days**

---

## Key Decisions & Trade-offs

### What We're Adopting from Research
✅ **Agentic multi-step workflow** - proven better than single-pass
✅ **Pydantic validation** - schema compliance guaranteed
✅ **LLM-as-a-Judge** - separate scoring from extraction
✅ **Entity disambiguation** - merge duplicates across chunks
✅ **Causal reasoning** - dedicated agent for DEPENDS_ON edges

### What We're Deferring
⏸️ **LangGraph orchestration** - start with simple Python, add if needed
⏸️ **Constrained decoding (Outlines)** - validation loop sufficient for now
⏸️ **Neo4j optimization** - basic export first, optimize later
⏸️ **Multiple LLM models** - use Gemini for everything initially

### What We're NOT Doing (Learned from Iteration 7)
❌ **Custom output formats** - stick with JSON
❌ **Two-pass with different formats** - keep format consistent
❌ **Fighting model training data** - use what Gemini knows

---

## Risk Mitigation

### Risk 1: Causal edge accuracy <60%
**Mitigation:** Iteration 14 (CoVe) specifically addresses this
**Fallback:** Use simpler heuristics (temporal sequence) if CoVe doesn't help

### Risk 2: Long narrative causes context loss
**Mitigation:** Iteration 8 (chunking) addresses this
**Fallback:** Use sliding window with overlap if fixed chunks don't work

### Risk 3: Entity disambiguation fails
**Mitigation:** Start with simple string matching, add LLM confirmation
**Fallback:** Manual disambiguation rules for common cases

### Risk 4: Scoring rubrics don't correlate with reality
**Mitigation:** Iteration 12 UAT tests this explicitly
**Fallback:** Simplify rubrics or use binary (good/bad) instead of 0-1 scale

---

## Success Metrics

### Iteration-Level Metrics
- **Node recall:** % of expected entities found
- **Edge accuracy:** % of edges with correct source/target
- **Schema compliance:** % of extractions passing validation
- **Scoring correlation:** Do scores match described quality issues?

### System-Level Metrics (Iteration 15)
- **End-to-end accuracy:** >75% overall
- **Extraction time:** <30s for 2000 char story
- **Graph queryability:** Can answer "where does error originate?" queries
- **User satisfaction:** UAT feedback on usefulness

---

## Next Steps

1. **Review this roadmap** - Does the iterative approach make sense?
2. **Start Iteration 8** - Implement multi-step node extraction
3. **Set up test infrastructure** - Automated testing for each iteration
4. **Define UAT process** - How will we evaluate each iteration?

**Ready to start Iteration 8?**
