# Alternative B: Edge-Based Factor Model

**Core Idea:** Factors are edges (effects on outputs), not properties. Outputs are calculated fields from contributing edges.

**Status:** Under exploration

---

## Conceptual Model

### The Shift

**Old Model:** "Factor = capability to deliver output"
**New Model:** "Factor = effect on output quality/quantity"

### Graph Structure

**Nodes:**
- **Output** - Measurable deliverable with quality/quantity metrics
- **Tool** - Software, platforms (renamed from System)
- **Process** - How work gets done (steps, workflows)
- **People** - Employee archetypes (team + role + seniority + context)

**Edges (the factors):**
- **People → Output** - How this archetype affects output
- **Tool → Output** - How this tool affects output
- **Process → Output** - How this process affects output
- **Output → Output** - How upstream output affects downstream

Each edge represents: "X's effect on Y's quality/quantity"

---

## Example

User says: *"Sales team is understaffed and overworked, their process is not streamlined, they simply cannot deliver the required amount of targeted outgoing calls."*

**Nodes created:**
- Output: "Targeted Outgoing Calls" (quantity metric)
- People: "Sales Team - Understaffed Archetype"
- Process: "Outbound Calling Process"

**Edges created:**
- "Sales Team - Understaffed → Outgoing Calls" (effect: reduces quantity)
- "Outbound Calling Process → Outgoing Calls" (effect: not streamlined, reduces quantity)

**Factor calculation:**
- Output quality/quantity = MIN(People edge, Process edge, Tool edge, Dependency edges)
- Identifies bottleneck: Both People and Process are limiting

---

## Core Principles

### 1. Outputs as Calculated Fields

Output quality is **never stored directly** - it's calculated from contributing edges.

If user says: *"Lead quality is horrible"* but can't elaborate:
- We distribute low score + low confidence to ALL edges affecting "Lead Quality"
- Each edge gets flagged: "Inferred from output complaint"
- This is acceptable duplication - it's fair assessment at this level

### 2. Evidence Aggregation

Evidence has **tiers** (not numeric confidence):
- **Tier 1:** AI inferred from indirect data
- **Tier 2:** User mentioned indirectly
- **Tier 3:** User stated directly
- **Tier 4:** User provided example
- **Tier 5:** User provided quantified example

Aggregation uses **Bayesian-Weighted Ranking** (see `Bayesian_Ranking_Algorithm.md`):
- Each tier worth 3× previous tier
- Weighted average with Bayesian shrinkage
- Final confidence always 0.0-1.0

### 3. Power of Elimination

If user says output is bad, but rates all inputs good → discrepancy.

System uses elimination:
> "You said [Tool is good], [People are capable], [Data is clean], so the only thing left that could cause this quality issue is the Process. Do you agree?"

This is both:
- **Automatic inference** (system calculates)
- **Conversational confirmation** (system asks user)

### 4. Targeted Mentions Outweigh Inferences

User says (Turn 1): *"Lead quality is horrible"* → Tier 1 inference distributed to all edges
User says (Turn 5): *"Actually, CRM is great for lead tracking"* → Tier 4 specific statement

Result:
- Edge "CRM → Lead Quality" now has both pieces of evidence
- Tier 4 (weight 27) outweighs Tier 1 (weight 1)
- Calculated score reflects Tier 4 more heavily
- **Both pieces kept** - this is vital for system intelligence

---

## Entity Definitions

### Output Node

**Purpose:** Measurable deliverable or work product

**Attributes:**
- `output_id`: Unique identifier
- `output_name`: User-provided or extracted name
- `description`: Free-text field for user notes (inference anchor)
- `metrics`: List of quality/quantity dimensions
  - Example: "Lead Quality" has dimensions: completeness, accuracy, relevance
  - Example: "Outgoing Calls" has dimensions: volume, conversion rate

**Note:** Output quality is **calculated**, not stored. It's MIN() of incoming edges.

### Tool Node

**Purpose:** Software, platform, or system used in work

**Attributes:**
- `tool_id`: Unique identifier
- `tool_name`: User-provided name
- `tool_type`: "crm" | "erp" | "spreadsheet" | "custom" | etc. (helps find common pilot use cases)
- `description`: Free-text field for user notes (what it does, how it's used - inference anchor)

**Note:** Same tool can have different effects on different outputs.
- CRM might be great for "Lead Tracking" but terrible for "Call Data Capture"

### Process Node

**Purpose:** How work gets done (even if unnamed)

**Attributes:**
- `process_id`: Unique identifier (e.g., "proc_001")
- `process_name`: User-provided or extracted (e.g., "when we enter data")
- `process_steps`: List of steps (if user provides)
- `maturity_level`: Inferred from evidence (ad-hoc, documented, standardized, optimized)

**Deduplication:**
- If user says "when we enter data" then later "the data entry workflow"
- System asks ONCE: "Are these the same? If not, explain how they differ."
- If Yes: Merge, update name
- If No + context: Keep separate
- If No + no context: Create "possible duplicate" link, never ask again

### People Node

**Purpose:** Employee archetype with context

**Attributes:**
- `people_id`: Unique identifier
- `archetype_name`: "Sales Team - Junior" | "Data Engineers - Senior" | etc.
- `description`: Free-text field for user notes (team, role, seniority, motivation, stress, culture, skills - inference anchor)

**Granularity:** Per archetype, not per individual
- "Sales Team - Junior Archetype" is one entity
- "Sales Team - Senior Archetype" is another entity
- Different archetypes can have different effects on same output

### Edge (Factor)

**Purpose:** Represents effect of one entity on another

**Attributes:**
- `edge_id`: Unique identifier
- `source_id`: Node ID (People/Tool/Process/Output)
- `target_id`: Output node ID
- `edge_name`: Human-readable (e.g., "Sales Team - Junior impact on Lead Quality")
- `current_score`: 1-5 stars (calculated from evidence using Bayesian algorithm)
- `current_confidence`: 0.0-1.0 (calculated from evidence weights)
- `evidence`: Array of evidence pieces

**Evidence Piece:**
```
{
  statement: "User's exact words or system inference",
  tier: 1-5,
  timestamp: ISO timestamp,
  conversation_id: Reference to conversation,
  inferred_from: (if Tier 1) Reference to what it was inferred from
}
```

---

## How It Handles Conversation Patterns

### Pattern 1: Vague Statement

**User:** *"Sales is a mess"*

**System action:**
1. Identify scope: Sales (could be team, process, or outputs)
2. **Create sensible default nodes** if they don't exist:
   - Output: "Sales Output" (generic)
   - People: "Sales Team"
   - Process: "Sales Process"
   - Tool: "CRM" (common default)
   - Upstream: "Marketing Output" (common dependency)
3. **Create edges** with Tier 1 evidence: "User said 'Sales is a mess'"
4. User can later adjust these defaults with specificity or add more nodes

**Storage:**
- All default nodes created
- All edges created with low confidence (Tier 1)
- User can refine later without losing initial context

### Pattern 2: Specific Statement

**User:** *"Sales Forecast data quality is horrible because we're using ad-hoc Excel files"*

**System action:**
1. Identify: Output = "Sales Forecast", dimension = "data quality"
2. Identify: Upstream dependency = Excel files (Tool)
3. Create edge: "Excel → Sales Forecast" with Tier 4 evidence
4. Calculate: Edge score = ⭐ or ⭐⭐

**Storage:**
- Edge "Excel → Sales Forecast" gets evidence piece with Tier 4

### Pattern 3: Contradiction

**User (Turn 1):** *"Data quality is pretty good"*
**User (Turn 5):** *"Data quality is horrible, we're using Excel"*

**System action:**
1. Detect: Same topic, opposite sentiment
2. Keep both evidence pieces
3. Calculate: Tier 4 (Turn 5) outweighs Tier 2 (Turn 1) in aggregation
4. **Ask only if both are Tier 3+:** "Earlier you said data was good, now horrible. Which is more accurate?"
5. **If one is Tier 1-2:** Weighted aggregation handles it silently, no user interruption

**Storage:**
- Edge has 2 evidence pieces, weighted aggregation favors Turn 5

### Pattern 4: Unknown

**User:** *"I don't know, I'm not involved in that process"*

**System action:**
1. Accept: Don't force user to guess
2. Create edge with confidence = 0.0
3. Attach evidence: "User said 'I don't know, I'm not involved in that process'"
4. Continue: Calculate output with 3/4 edges (skip 0.0 confidence edges)

**Storage:**
- Edge exists with Tier 0 evidence ("I don't know")
- Confidence = 0.0
- UI allows user to generate surveys for outputs of interest (export these unknowns)

### Pattern 5: Dependency Chain

**User:** *"Sales Forecast depends on customer data from Marketing, but their data quality is only 60%"*

**System action:**
1. Create nodes: "Customer Data" output (if doesn't exist)
2. Create edge: "Customer Data → Sales Forecast"
3. Create evidence on "Customer Data" output edges: Tier 3, score ≈ ⭐⭐⭐
4. Propagate: Sales Forecast limited by upstream ⭐⭐⭐

**Storage:**
- Edge "Customer Data → Sales Forecast" with Tier 3 evidence
- "Customer Data" output's edges get Tier 2 evidence (inferred from downstream complaint)

### Pattern 6: Ambiguity (Node Deduplication)

**User (Turn 1):** *"Sales tool is outdated"*
**User (Turn 5):** *"CRM has no reporting features"*

**System action:**
1. **Before creating edge:** Detect semantic similarity + context overlap
2. **Prompt with context:** "You mentioned 'CRM' - I have 'Sales tool' from Turn 1 affecting Sales Forecast. Are these:
   1. Same system (merge)
   2. Different systems (keep separate)
   3. Different functions (create 'CRM - Data Entry' and 'CRM - Reporting')
   4. Not sure (mark as possible duplicates)"
3. **Resolution:**
   - Same: Merge nodes, use preferred name
   - Different: Keep separate
   - Different functions: Create "Tool - Function A", "Tool - Function B"
   - Unsure: Create "possible duplicate" link
4. **If unresolved:** Ask again every time node or neighbors update
5. **Warning:** "Wrong merge breaks assessment beyond recovery"

**Storage:**
- If merged: Single node with combined evidence
- If separate: Two nodes, no link
- If different functions: Two nodes with function-specific names
- If unsure: Two nodes with "possible_duplicate" link

**Applies to:** Tools, People, Processes, Outputs (all node types)

---

## Storage Options

### Option A: Firestore Collections (Document-Based)

```
/users/{user_id}/
  nodes/
    outputs/{output_id}
    tools/{tool_id}
    processes/{process_id}
    people/{people_id}
  
  edges/{edge_id}
    source_id, target_id, evidence[], current_score, current_confidence
  
  conversations/{conversation_id}
    messages[], context
```

**Pros:**
- Familiar structure (current schema)
- Easy to query by user
- Good for conversation history

**Cons:**
- Graph traversal requires multiple queries
- Edge queries need composite indexes
- Harder to find "all edges affecting Output X"

### Option B: Firestore with Denormalization

```
/users/{user_id}/
  nodes/
    outputs/{output_id}
      incoming_edges: [edge_id, edge_id, ...]  # Denormalized
      calculated_score: 2.5  # Cached
      calculated_confidence: 0.75  # Cached
    
    tools/{tool_id}
      outgoing_edges: [edge_id, edge_id, ...]  # Denormalized
  
  edges/{edge_id}
    source_id, target_id, evidence[], current_score, current_confidence
```

**Pros:**
- Fast retrieval: "Show all edges affecting Output X"
- Cached calculations reduce compute
- Still uses Firestore

**Cons:**
- Denormalization = update complexity
- Cache invalidation when evidence changes
- More storage

### Option C: Hybrid (Firestore + In-Memory Graph)

```
Firestore:
  - Stores nodes, edges, evidence (source of truth)
  - Optimized for persistence, conversation history

In-Memory (per session):
  - Loads relevant subgraph for current conversation
  - Fast graph traversal, calculations
  - Writes back to Firestore on changes
```

**Pros:**
- Fast graph operations (BFS, DFS, MIN calculation)
- Firestore for persistence
- Best of both worlds

**Cons:**
- More complex architecture
- Need to manage sync between memory and Firestore
- Memory limits for large graphs

### Recommendation

**Option C (Hybrid)** is the choice:
- Graph will not be large (humans can't comprehend deep recursion)
- Output-centric approach doesn't require massive knowledge graph
- In-memory graph enables fast traversal, MIN() calculation, power of elimination
- Firestore for persistence, conversation history
- Best fit for conversational, exploratory assessment

---

## Pilot Recommendation Logic

### Step 1: Identify Bottleneck Edges

For each output with low score:
1. Calculate: Output score = MIN(incoming edges)
2. Find: Edge(s) with lowest score
3. Classify: Bottleneck type (People/Tool/Process/Dependency)

### Step 2: Match to Solution Space

**Not hardcoded mapping** - use knowledge base JSON:

```json
{
  "solution_categories": [
    {
      "category": "Data Quality Pilots",
      "addresses_bottlenecks": ["dependency"],
      "typical_problems": ["scattered data", "outdated data", "incomplete data"],
      "solution_vector": [0.9, 0.1, 0.2, 0.8]  // [people, tool, process, dependency]
    },
    {
      "category": "Process Automation",
      "addresses_bottlenecks": ["process", "tool"],
      "typical_problems": ["manual process", "no standardization", "poor UX"],
      "solution_vector": [0.2, 0.7, 0.9, 0.1]
    }
  ]
}
```

### Step 3: Distance Calculation

For each output's bottleneck profile:
- Create vector: [people_score, tool_score, process_score, dependency_score]
- Calculate distance to each solution category's vector
- Rank solutions by distance (closest = best fit)

### Step 4: Recommend Multiple Solutions

Same output can have multiple bottlenecks:
- "Call Data Capture" has Tool bottleneck (⭐⭐) AND Process bottleneck (⭐)

Recommendations:
1. **Fix Process:** Automate data entry workflow (closest match)
2. **Fix Tool:** Add AI-assisted capture to CRM (second closest)

Both improve same output, different bottlenecks.

---

## Open Questions

1. **Evidence tier detection:** How do we automatically classify user statements into Tiers 1-5?
   - Answer: LLM inference with good prompt + LLM inference tests

2. **Global average (μ):** For Bayesian shrinkage, what's the global average?
   - Answer: 2.0 ("Most orgs are made of ducktape and prayers")

3. **Confidence threshold (C):** What's the minimum effective weight for trust in recommendations?
   - Answer: As low as 1, but warn user about low-confidence factors in recommendations

4. **Process step granularity:** Do we model individual steps or just processes?
   - Answer: Process level. Steps are mainly for context and intelligent conversation - people rarely realize they follow protocols

5. **Node/Edge CRUD operations:** How do we make CRUD operations UX-first while keeping coherent?
   - Answer (Node deduplication): Detect semantic + context similarity before creating edge, prompt with 4 options (same/different/different functions/unsure), ask again if unresolved when node/neighbors update
   - OPEN: When do we delete/archive nodes and edges?
   - OPEN: How do we prevent graph fragmentation from user edits?
   - **Critical:** Need UX design for graph manipulation without breaking coherence

6. **Contradiction resolution:** How do we handle conflicting evidence?
   - Answer: Force resolution **only if both are Tier 3+**. Tell user: "You said XY on [timestamp] that contradicts this claim. Let's figure out what truth to store - or if there's confusion and these are two different things."
   - If one is Tier 1-2: Weighted aggregation handles silently

7. **Default node creation:** What are sensible defaults for each domain (Sales, Finance, etc.)?
   - OPEN: Need domain-specific templates
   - OPEN: How do we learn from user corrections to improve defaults?

---

## Next Steps

1. Create STORAGE.md with detailed Firestore schema
2. Create RETRIEVAL.md with query patterns
3. Create CONVERSATION_FLOW.md with UX implications
4. Create TRADEOFFS.md comparing to other alternatives
5. Build unit tests for Bayesian aggregation (0.0-1.0 output, 3× multiplier)
