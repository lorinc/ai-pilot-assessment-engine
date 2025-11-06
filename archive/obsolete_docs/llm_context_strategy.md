# LLM Context Strategy: Multi-Stage Retrieval + Progressive Disclosure

**Problem:** The full taxonomy set (problem taxonomy, AI use cases, dependencies, decision dimensions) is too large to fit in a single LLM context window.

**Solution:** Hybrid retrieval with staged context loading—only load what's relevant for each conversation stage.

---

## Architecture: Hybrid Retrieval + Staged Context Loading

### 1. Semantic Search Layer (Pre-LLM)

Before calling the LLM, use semantic search to retrieve only relevant taxonomy chunks.

```yaml
user_input: "Our sales forecasts are always wrong"

semantic_search:
  embed: user_input
  search_against:
    - problem_taxonomy (embedded by category + symptoms)
    - AI_use_case_taxonomy (embedded by core_task + example_outputs)
  
  retrieve_top_k: 3
  
  results:
    - problem: "Data Quality & Forecasting Issues" (0.89 similarity)
    - archetype: "Time Series Forecasting" (0.87 similarity)
    - archetype: "Anomaly Detection" (0.72 similarity)
```

**Only these 3 chunks go into LLM context**, not the entire taxonomy.

---

### 2. Progressive Context Loading (Conversation Stages)

Load different context based on which stage of the decision process the user is in.

#### Stage 1: Problem Discovery (Minimal Context)

```json
{
  "system_prompt": "You are a decision support assistant...",
  "context_loaded": {
    "conversation_guidelines": "full (5KB)",
    "problem_categories": "top 3 matches only (2KB)",
    "user_history": "constraints from past conversations (1KB)"
  },
  "total_tokens": "~2K tokens"
}
```

**LLM Task:** Ask 1-2 questions, extract problem category, identify constraints.

---

#### Stage 2: Option Generation (Targeted Context)

```json
{
  "system_prompt": "Generate 3-5 options...",
  "context_loaded": {
    "problem_details": "matched category + symptoms (1KB)",
    "relevant_archetypes": "top 2-3 AI use cases (3KB)",
    "prerequisites": "only for matched archetypes (2KB)",
    "organizational_context": "budget, time, past decisions (1KB)",
    "option_templates": "for matched problem type (2KB)"
  },
  "total_tokens": "~2.5K tokens"
}
```

**LLM Task:** Generate options using templates, check prerequisites, estimate effort.

---

#### Stage 3: Impact & Assumptions (Focused Context)

```json
{
  "system_prompt": "Estimate impact and extract assumptions...",
  "context_loaded": {
    "selected_option": "user's choice (0.5KB)",
    "impact_estimation_guide": "for this problem category (1KB)",
    "assumption_templates": "for this option type (1KB)",
    "decision_dimensions": "only relevant ones (2KB)",
    "user_responses": "from conversation so far (1KB)"
  },
  "total_tokens": "~1.5K tokens"
}
```

**LLM Task:** Generate scenarios, extract assumptions, probe for confidence.

---

#### Stage 4: Decision Support (Synthesis Context)

```json
{
  "system_prompt": "Synthesize recommendation...",
  "context_loaded": {
    "full_conversation_summary": "problem + options + assumptions (2KB)",
    "scoring_framework": "Value/Speed/Priority formulas (1KB)",
    "decision_checklist": "from linear_discovery_process.md (1KB)",
    "organizational_constraints": "accumulated context (1KB)"
  },
  "total_tokens": "~1.5K tokens"
}
```

**LLM Task:** Recommend Go/No-Go/Try, show reasoning, flag red flags.

---

### 3. Retrieval Strategy Per Stage

```python
def get_context_for_stage(stage, user_input, conversation_state):
    if stage == "problem_discovery":
        return {
            "guidelines": load_full("user_interaction_guideline.md"),
            "problem_matches": semantic_search(
                query=user_input,
                corpus="problem_taxonomy",
                top_k=3
            ),
            "user_context": get_user_constraints(user_id)
        }
    
    elif stage == "option_generation":
        problem_category = conversation_state["problem_category"]
        return {
            "problem_details": get_problem_details(problem_category),
            "archetypes": semantic_search(
                query=problem_category,
                corpus="AI_use_case_taxonomy",
                top_k=3
            ),
            "prerequisites": get_prerequisites_for_archetypes(
                conversation_state["matched_archetypes"]
            ),
            "option_templates": get_option_templates(problem_category),
            "org_context": get_user_constraints(user_id)
        }
    
    elif stage == "impact_estimation":
        selected_option = conversation_state["selected_option"]
        return {
            "option_details": selected_option,
            "impact_guide": get_impact_guide(problem_category),
            "assumption_templates": get_assumption_templates(
                option_type=selected_option["type"]
            ),
            "relevant_dimensions": filter_decision_dimensions(
                selected_option,
                top_k=5  # Only 5 most relevant dimensions
            )
        }
    
    elif stage == "decision_synthesis":
        return {
            "conversation_summary": summarize_conversation(conversation_state),
            "scoring_framework": load("scoring_framework.json"),
            "decision_checklist": load("linear_discovery_process.md"),
            "org_context": get_user_constraints(user_id)
        }
```

---

### 4. Vector Store Structure

```yaml
collections:
  
  problem_taxonomy:
    chunk_strategy: "category + symptoms combined"
    embedding_model: "text-embedding-004"
    chunks: ~50 (one per problem category × dimension)
    metadata: {category, dimension, symptoms, conversation_starters}
  
  AI_use_case_taxonomy:
    chunk_strategy: "archetype + core_task + outputs"
    chunks: ~30 (one per archetype)
    metadata: {archetype, technical_family, prerequisites, effort_range}
  
  AI_dependency_taxonomy:
    chunk_strategy: "prerequisite + description"
    chunks: ~40 (one per prerequisite)
    metadata: {prerequisite, category, conversation_check}
  
  decision_dimensions:
    chunk_strategy: "dimension + levels + question"
    chunks: ~60 (one per dimension)
    metadata: {dimension, category, user_facing_question}
  
  organizational_context:
    chunk_strategy: "per user, per constraint type"
    chunks: variable (grows with usage)
    metadata: {user_id, type, category, reusable, last_updated}
```

---

### 5. Context Budget Per Stage

| Stage | System Prompt | Retrieved Context | Conversation History | Total |
|-------|---------------|-------------------|---------------------|-------|
| Problem Discovery | 1K | 3K | 1K | **5K tokens** |
| Option Generation | 1K | 8K | 2K | **11K tokens** |
| Impact Estimation | 1K | 6K | 2K | **9K tokens** |
| Decision Synthesis | 1K | 5K | 3K | **9K tokens** |

**Max context per call: ~11K tokens** (well within 128K window, leaves room for response)

---

## Key Techniques

### A. Semantic Chunking

- Don't embed entire taxonomies
- Chunk at meaningful boundaries (category + symptoms, archetype + task)
- Embed with rich metadata for filtering

**Example:**
```python
# Bad: Embed entire problem_taxonomy.json as one chunk
# Good: Embed each problem category separately

chunks = []
for category, dimensions in problem_taxonomy.items():
    for dimension, symptoms in dimensions.items():
        chunk = {
            "text": f"{category}: {dimension} - {', '.join(symptoms)}",
            "metadata": {
                "category": category,
                "dimension": dimension,
                "symptoms": symptoms
            }
        }
        chunks.append(chunk)
```

---

### B. Metadata Filtering

Don't retrieve all decision dimensions—filter by relevance first.

```python
# Don't retrieve all decision dimensions
# Filter by relevance first
relevant_dimensions = vector_store.search(
    query=selected_option,
    collection="decision_dimensions",
    filter={
        "category": ["Risk", "Economics", "Operations"],  # Only relevant categories
        "criticality": "high"
    },
    top_k=5
)
```

---

### C. Conversation State as Filter

Use conversation state to narrow retrieval and avoid redundancy.

```python
# Use conversation state to narrow retrieval
if conversation_state["budget_mentioned"]:
    # Don't retrieve budget-related dimensions again
    exclude_dimensions = ["Budget type", "Funding trigger"]

if conversation_state["time_constraint_set"]:
    # Don't ask about urgency again
    exclude_dimensions.append("Urgency")
```

---

### D. Summarization Between Stages

Don't carry full conversation history—summarize after each stage.

```python
# Don't carry full conversation history
# Summarize after each stage
stage_1_summary = llm.summarize(
    conversation_stage_1,
    format="structured_json",
    fields=["problem_category", "constraints", "urgency"]
)
# Pass summary to stage 2, not full transcript
```

---

## Example: Full Flow with Context Loading

```yaml
User: "Our sales forecasts are always wrong"

# Stage 1: Problem Discovery
context_loaded:
  - user_interaction_guideline.md (full)
  - problem_taxonomy: top 3 matches
  - user_constraints: from past conversations
tokens: 5K

LLM: "What made you notice this? Is it getting worse?"
User: "Yeah, we missed Q3 by 20%"

# Stage 2: Option Generation
context_loaded:
  - problem_category: "Data Quality & Forecasting" (details)
  - archetypes: ["Time Series Forecasting", "Anomaly Detection"]
  - prerequisites: only for these 2 archetypes
  - option_templates: for forecasting problems
  - user_constraints: budget <€50K, time <1 quarter
tokens: 11K

LLM: "Here are 3 options: 1. Do nothing, 2. Improve process, 3. Pilot ML..."
User: "Let's explore option 2"

# Stage 3: Impact Estimation
context_loaded:
  - option_2_details: "Improve existing process"
  - impact_guide: for process improvement
  - assumption_templates: for process changes
  - decision_dimensions: only 5 most relevant (Risk, Change, Ownership, Measurement, Operations)
tokens: 9K

LLM: "If things go badly: €10K, likely: €30K, optimistic: €50K. Sound right?"
User: "Yeah, that's about right"

# Stage 4: Decision Synthesis
context_loaded:
  - conversation_summary: problem + option + impact
  - scoring_framework: Value/Speed/Priority
  - decision_checklist: from linear_discovery_process.md
  - user_constraints: accumulated
tokens: 9K

LLM: "Recommendation: Go with Option 2. Reasoning: ..."
```

---

## Implementation Checklist

### Release 1: Vector Store Setup
- [ ] Chunk taxonomies at meaningful boundaries
- [ ] Embed chunks with text-embedding-004
- [ ] Add rich metadata to each chunk
- [ ] Create separate collections per taxonomy type
- [ ] Test retrieval quality with sample queries

### Release 2: Retrieval Functions
- [ ] Implement `semantic_search()` with metadata filtering
- [ ] Implement `get_context_for_stage()` with stage routing
- [ ] Implement `get_user_constraints()` for organizational context
- [ ] Implement `filter_decision_dimensions()` for relevance filtering
- [ ] Test context size per stage (should be <15K tokens)

### Phase 3: Conversation State Management
- [ ] Define conversation state schema
- [ ] Implement stage detection logic
- [ ] Implement summarization between stages
- [ ] Implement constraint extraction and storage
- [ ] Test state persistence across sessions

### Phase 4: LLM Integration
- [ ] Create system prompts per stage
- [ ] Implement context assembly per stage
- [ ] Implement response parsing and state updates
- [ ] Test full conversation flow
- [ ] Monitor token usage per stage

### Phase 5: Optimization
- [ ] Profile retrieval latency
- [ ] Optimize chunk sizes for retrieval quality
- [ ] Implement caching for frequently accessed chunks
- [ ] A/B test top_k values for retrieval
- [ ] Monitor and tune context budgets

---

## Anti-Patterns to Avoid

❌ **Don't:** Load entire taxonomies into every LLM call  
✅ **Do:** Use semantic search to retrieve only relevant chunks

❌ **Don't:** Carry full conversation history across all stages  
✅ **Do:** Summarize after each stage, pass structured summaries

❌ **Don't:** Retrieve all decision dimensions for every option  
✅ **Do:** Filter by relevance using metadata and conversation state

❌ **Don't:** Re-retrieve organizational context every time  
✅ **Do:** Cache user constraints, only update when new info appears

❌ **Don't:** Use same context for all conversation stages  
✅ **Do:** Load different context based on stage (discovery vs synthesis)

---

## Technology Stack

### Vector Store
- **FAISS** - For local/prototype development
- **Vertex AI Vector Search** - For production deployment
- **Embedding Model:** text-embedding-004 (768 dimensions)

### LLM
- **Gemini 1.5 Pro** - 128K context window, good for synthesis
- **Gemini 1.5 Flash** - Faster, cheaper for simple stages

### Orchestration
- **LangChain** - For retrieval chains and conversation management
- **LangGraph** - For multi-stage conversation flows

---

## Summary

**Don't load everything at once. Use:**

1. **Semantic search** to retrieve only relevant taxonomy chunks
2. **Staged context loading** based on conversation phase
3. **Metadata filtering** to narrow retrieval
4. **Summarization** to compress conversation history
5. **Progressive disclosure** to keep context budget <15K tokens per stage

**Result:** Full taxonomy knowledge accessible, but only ~10K tokens loaded per LLM call.
