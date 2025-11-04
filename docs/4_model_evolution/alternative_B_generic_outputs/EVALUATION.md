# Alternative B: Evaluation Against Conversation Patterns

**Purpose:** Briefly show how edge-based model handles the 8 patterns from USER_INTERACTION_PATTERNS.md

---

## Pattern 1: Vagueness - "Sales is a mess"

**How it handles:**
- Creates sensible default nodes: Sales Output, Sales Team, Sales Process, CRM, Marketing Output
- Creates edges with Tier 1 evidence
- User refines later without losing context

**Strength:** Doesn't block on vagueness, captures intent immediately

---

## Pattern 2: Specificity - "2 stars, scattered data"

**How it handles:**
- Creates specific edge: "Upstream Data → Sales Forecast"
- Tier 4 evidence (quantified example)
- High confidence (0.8+)

**Strength:** Precise attribution to specific edge

---

## Pattern 3: Contradictions - "good" then "horrible"

**How it handles:**
- Keeps both evidence pieces on same edge
- Bayesian aggregation weights higher tier evidence
- **Forces resolution only if both are Tier 3+:** Shows user both statements with timestamps, asks which is correct
- **If one is Tier 1-2:** Weighted aggregation handles it, no user interruption needed

**Strength:** Intelligence from keeping history, only bothers user for significant contradictions

---

## Pattern 4: Unknowns - "I don't know"

**How it handles:**
- Creates edge with confidence = 0.0
- Attaches evidence: "User said I don't know"
- Skips in MIN() calculation
- UI exports unknowns as survey questions

**Strength:** Captures gaps, enables verification workflow

---

## Pattern 5: Generic statements - "CRM is ancient"

**How it handles:**
- Creates Tool node "CRM" if doesn't exist
- Adds Tier 2 evidence to ALL edges from CRM
- Low confidence (0.3-0.4)
- User can later specify which outputs affected

**Strength:** Distributes generic evidence, refines later

---

## Pattern 6: Progressive refinement - Vague → specific over time

**How it handles:**
- Turn 1: Creates defaults with Tier 1
- Turn 3: Adds Tier 3 to specific edge
- Turn 5: Adds Tier 4 to same edge
- Bayesian aggregation naturally increases confidence

**Strength:** Evidence accumulates, confidence grows organically

---

## Pattern 7: Cross-output mentions - Marketing data affects Sales

**How it handles:**
- Creates "Marketing Output" node
- Creates edge: "Marketing Output → Sales Forecast"
- Same evidence can affect multiple downstream outputs
- Graph traversal shows cascading impact

**Strength:** Dependency chains explicit, impact visible

---

## Pattern 8: Corrections - User changes their mind

**How it handles:**
- Keeps old evidence (experienced team)
- Adds new evidence (junior team)
- Forces resolution: "You said experienced, now junior - which is correct?"
- User picks, system updates

**Strength:** Catches corrections, maintains coherence

---

## Pattern 9: Ambiguity - "Sales tool" vs "CRM"

**Scenario:** User says "Sales tool" in Turn 1, then "CRM" in Turn 5. Are these:
- **Synonyms?** (Same tool, different names)
- **Different tools?** (Two separate systems)
- **Different functions?** (Same tool, different capabilities)

**How it handles:**

**Detection:** Before creating edge, check for semantic similarity + context overlap with existing nodes

**User prompt (with context):**
> "You mentioned 'CRM' - I have an existing tool called 'Sales tool' that you mentioned in Turn 1 affecting Sales Forecast. Are these:
> 1. The same system (I'll merge them)
> 2. Different systems (I'll keep them separate)
> 3. Different functions of the same system (I'll create 'CRM - Data Entry' and 'CRM - Reporting')
> 4. Not sure (I'll create both and mark as possible duplicates)"

**Resolution:**
- **Same:** Merge nodes, update name to user's preferred term
- **Different:** Keep separate, no link
- **Different functions:** Create two nodes: "Tool name - Function A", "Tool name - Function B"
- **Unsure:** Create new node, add "possible duplicate" link

**If unresolved:**
- Every time that node or its neighbors need updating, ask again
- Show context: "You have 'Sales tool' and 'CRM' marked as possible duplicates. Are they the same?"
- **Warning:** "If these are actually different and you merge them, it will mess up the assessment beyond recovery."

**Applies to all node types:**
- **Tools:** "Sales tool" vs "CRM"
- **People:** "Sales team" vs "Sales reps"
- **Processes:** "When we enter data" vs "Data entry workflow" (already handled)
- **Outputs:** "Sales Forecast" vs "Monthly forecast"

---

---

## Pattern 10: Solution Recommendation (NEW)

**Scenario:** System has gathered context, needs to recommend pilots

**How it handles:**

**Step 1: Context Aggregation**
- Collect all edges for output
- Calculate MIN() to identify bottlenecks
- Extract evidence from all edges
- Include business context (cost, timeline, competitive pressure)

**Step 2: LLM Semantic Inference**
- Pass rich context + pain point catalog + AI archetype catalog + pilot catalog to LLM
- LLM identifies 2-4 most likely pain points
- LLM maps pain points to 2-3 AI archetypes
- LLM recommends 2-3 specific pilots with rationale

**Step 3: User Validation**
- Present pain points: "I see these underlying issues: [list]. Does this match?"
- User validates/corrects pain point interpretation
- Present pilot options with expected impact, timeline, cost
- User selects based on priorities

**Strength:** Handles combinatorial complexity (10,000+ scenarios) without hardcoded mappings. Context-aware, explainable, flexible.

**See:** `SOLUTION_RECOMMENDATION.md` for detailed design

---

## Summary

**What works well:**
- Handles all 10 patterns without blocking user
- Evidence accumulation is natural
- Graph structure makes dependencies explicit
- Bayesian aggregation handles mixed evidence
- LLM semantic inference handles problem-to-solution jump

**What needs work:**
- Default node creation needs domain templates
- CRUD operations on graph need UX design
- Contradiction resolution needs clear UI
- Survey generation from unknowns needs implementation
- LLM prompt engineering for recommendation quality
