# Alternative B: Inference & Multi-Hop Logic Stress Test

**Purpose:** Rigorously analyze inference challenges and knowledge graph requirements before implementation  
**Status:** Pre-implementation validation  
**Date:** 2025-11-04

---

## 1. Core Inference Challenge

**Alternative B shifts from property-based to edge-based factors:**
- **Old:** "Team execution = ⭐⭐" (property of output)
- **New:** "Sales Team → Sales Forecast = ⭐⭐" (edge with evidence)

**Critical Question:** Can we infer edge scores from vague user statements without explicit edge mentions?

---

## 2. Inference Scenarios by Vagueness Level

### Scenario A: Explicit Edge Mention (Easy)
**User:** "Sales team is junior, they struggle with forecasting"

**Inference Path:**
```
1. Identify nodes: People("Sales Team"), Output("Sales Forecast")
2. Create edge: Sales Team → Sales Forecast
3. Extract evidence: "junior", "struggle"
4. Classify tier: 3 (user stated directly)
5. Score: ⭐⭐ (junior = low capability)
```

**Data Required:** ✅ Available
- `organizational_templates/functions/sales.json` → typical teams
- `component_scales.json` → "junior" maps to ⭐⭐

**Confidence:** HIGH (0.8+)

---

### Scenario B: Implicit Edge via Output Mention (Medium)
**User:** "Sales forecast quality is horrible"

**Inference Path:**
```
1. Identify output: Sales Forecast
2. Infer typical edges from template:
   - Sales Ops Team → Sales Forecast
   - Salesforce CRM → Sales Forecast
   - Forecasting Process → Sales Forecast
   - Pipeline Data → Sales Forecast (dependency)
3. Distribute low score (⭐) to ALL edges
4. Mark all as Tier 1 (AI inferred)
5. Confidence: 0.3 per edge
```

**Data Required:** ✅ Partially Available
- `organizational_templates/functions/sales.json` → typical_creation_context
- **MISSING:** Explicit dependency graph (Pipeline Data → Sales Forecast)

**Problem:** Template has `typical_creation_context` but NOT `typical_dependencies` as structured edges.

**Gap:**
```json
// MISSING in sales.json:
"outputs": [{
  "id": "sales_forecast",
  "typical_dependencies": [
    {"output_id": "pipeline_data", "confidence": 0.8},
    {"output_id": "historical_sales", "confidence": 0.7}
  ]
}]
```

**Confidence:** MEDIUM (0.5-0.6)

---

### Scenario C: System Mention Only (Hard)
**User:** "We use Salesforce"

**Inference Path:**
```
1. Identify tool: Salesforce CRM
2. Lookup outputs created in Salesforce (from template)
3. Create Tool node: "Salesforce CRM"
4. Create Output nodes: Sales Forecast, Pipeline Reports, etc.
5. Create edges: Salesforce → Sales Forecast, Salesforce → Pipeline Reports
6. NO SCORE (user didn't mention quality)
7. Mark as "mentioned but not assessed"
```

**Data Required:** ✅ Available
- `organizational_templates/cross_functional/common_systems.json` → system catalog
- `organizational_templates/functions/sales.json` → outputs_created per system

**Confidence:** LOW (0.3-0.4) - System mentioned but no quality signal

---

### Scenario D: Pain Point Only (Very Hard)
**User:** "Revenue predictions are always wrong"

**Inference Path:**
```
1. Extract pain point: "predictions wrong"
2. Lookup in pain_point_mapping.json
3. Find matching outputs with this pain point
4. Rank by similarity
5. Suggest: "Sales Forecast" (confidence: 0.6)
6. IF confirmed → Create edges with Tier 1 evidence
```

**Data Required:** ❌ MISSING
- `inference_rules/pain_point_mapping.json` exists but `maps_to_outputs` is EMPTY for all 100+ pain points
- No structured mapping from pain points → outputs

**Critical Gap:**
```json
// CURRENT (pain_point_mapping.json):
{
  "subcategory": "Forecasting quality",
  "pain_points": ["high variance", "systematic bias", "no scenarios"],
  "maps_to_outputs": []  // ❌ EMPTY
}

// REQUIRED:
{
  "subcategory": "Forecasting quality",
  "pain_points": ["high variance", "systematic bias", "no scenarios"],
  "maps_to_outputs": [
    {"output_id": "sales_forecast", "confidence": 0.9},
    {"output_id": "demand_forecast", "confidence": 0.8},
    {"output_id": "financial_forecast", "confidence": 0.7}
  ]
}
```

**Confidence:** LOW (0.3-0.5) - Requires manual mapping of 100+ pain points to 46+ outputs

---

## 3. Multi-Hop Inference Challenges

### Challenge 3.1: Dependency Chain Inference

**User:** "Pipeline data is scattered, so forecasts are wrong"

**Required Inference:**
```
1. Identify upstream: Pipeline Data (output)
2. Identify downstream: Sales Forecast (output)
3. Create dependency edge: Pipeline Data → Sales Forecast
4. Score upstream: ⭐⭐ (scattered = poor quality)
5. Propagate: Sales Forecast limited by ⭐⭐ dependency
```

**Data Required:** ❌ MISSING
- No structured dependency graph in templates
- `inference_rules/output_discovery.json` mentions dependencies but no data structure

**Gap:** Need explicit dependency edges in output catalog:
```json
{
  "output_id": "sales_forecast",
  "dependencies": [
    {"output_id": "pipeline_data", "type": "data", "criticality": "high"},
    {"output_id": "historical_sales", "type": "data", "criticality": "medium"}
  ]
}
```

---

### Challenge 3.2: Cross-Function Dependency

**User:** "Marketing's lead quality is bad, so sales can't forecast"

**Required Inference:**
```
1. Identify: Marketing Leads (output, Marketing function)
2. Identify: Sales Forecast (output, Sales function)
3. Create cross-function edge: Marketing Leads → Sales Forecast
4. Score: Marketing Leads = ⭐⭐
5. Propagate: Sales Forecast limited by ⭐⭐ dependency
```

**Data Required:** ❌ MISSING
- No cross-function dependency mapping
- Templates are function-siloed

**Gap:** Need cross-function dependency catalog:
```json
{
  "cross_function_dependencies": [
    {
      "upstream": {"function": "Marketing", "output_id": "qualified_leads"},
      "downstream": {"function": "Sales", "output_id": "sales_forecast"},
      "confidence": 0.8
    }
  ]
}
```

---

### Challenge 3.3: Transitive Dependency (2-Hop)

**User:** "CRM data is messy, so forecasts are wrong"

**Required Inference:**
```
1. Identify: CRM (tool)
2. Infer: CRM → Pipeline Data (1-hop)
3. Infer: Pipeline Data → Sales Forecast (2-hop)
4. Transitive: CRM affects Sales Forecast via Pipeline Data
5. Score: CRM = ⭐⭐ → Pipeline Data = ⭐⭐ → Sales Forecast = ⭐⭐
```

**Data Required:** ❌ PARTIALLY MISSING
- Tool → Output edges exist in templates
- Output → Output edges (dependencies) MISSING

**Complexity:** Requires graph traversal with MAX 2-3 hops (per scope constraint)

---

## 4. Knowledge Graph Requirements

### 4.1 Node Types & Attributes

**People Node:**
```
- people_id
- archetype_name (e.g., "Sales Team - Junior")
- function (e.g., "Sales")
- description (free-text, inference anchor)
```

**Tool Node:**
```
- tool_id
- tool_name (e.g., "Salesforce CRM")
- tool_type (e.g., "CRM") ← ✅ Available in common_systems.json
- description (free-text, inference anchor)
```

**Process Node:**
```
- process_id
- process_name (e.g., "Sales Forecasting Process")
- function (e.g., "Sales")
- steps[] ← ✅ Available in function templates
- maturity_level (inferred from evidence)
```

**Output Node:**
```
- output_id
- output_name (e.g., "Sales Forecast")
- function (e.g., "Sales")
- description
- quality_metrics[] ← ✅ Available in function templates
```

---

### 4.2 Edge Types & Inference Rules

**Edge: People → Output**
```
Inference Triggers:
- User mentions team + output
- User mentions team capability (generic)
- Template default (Tier 1)

Data Required:
- ✅ typical_teams in function templates
- ✅ component_scales.json for scoring
```

**Edge: Tool → Output**
```
Inference Triggers:
- User mentions system + output
- User mentions system quality (generic)
- Template default (Tier 1)

Data Required:
- ✅ typical_systems in function templates
- ✅ common_systems.json for system catalog
- ❌ MISSING: System capability scales (not in component_scales.json)
```

**Edge: Process → Output**
```
Inference Triggers:
- User mentions process + output
- User mentions process maturity (generic)
- Template default (Tier 1)

Data Required:
- ✅ typical_processes in function templates
- ✅ component_scales.json for process maturity
```

**Edge: Output → Output (Dependency)**
```
Inference Triggers:
- User mentions "X depends on Y"
- User mentions "Y affects X"
- Template default (Tier 1)

Data Required:
- ❌ MISSING: Explicit dependency graph
- ❌ MISSING: Cross-function dependencies
- Partial: inference_rules/output_discovery.json mentions but no data
```

---

### 4.3 Evidence Classification Requirements

**Tier Detection (1-5):**
```
Tier 1: AI inferred from indirect data
  Example: "Sales is a mess" → Infer all edges = ⭐⭐
  Detection: No specific mention, generic complaint
  
Tier 2: User mentioned indirectly
  Example: "We use Salesforce" → Infer Salesforce → Sales Forecast
  Detection: Entity mentioned, no quality signal
  
Tier 3: User stated directly
  Example: "Sales team is junior" → Sales Team → Output = ⭐⭐
  Detection: Entity + quality descriptor
  
Tier 4: User provided example
  Example: "Last quarter, team missed 3 forecasts" → Evidence with specifics
  Detection: Temporal reference + concrete event
  
Tier 5: User provided quantified example
  Example: "Team is 60% accurate on forecasts" → Evidence with metric
  Detection: Numeric value + metric
```

**LLM Prompt Required:**
```
Classify this statement into Tier 1-5:
- Statement: "{user_statement}"
- Context: {output, team, system, process}
- Tier definitions: [above]

Output: {"tier": 3, "reasoning": "..."}
```

**Data Required:** ❌ No tier classification examples in inference_rules/

---

## 5. Critical Data Gaps Summary

### Gap 1: Dependency Graph (HIGH PRIORITY)
**Missing:** Explicit Output → Output edges with confidence
**Impact:** Cannot infer dependency chains, cannot propagate scores
**Required:** 
```json
// Add to each output in function templates:
"dependencies": [
  {"output_id": "pipeline_data", "confidence": 0.8},
  {"output_id": "historical_sales", "confidence": 0.7}
]
```
**Effort:** ~8 hours (46 outputs × 10 min each)

---

### Gap 2: Pain Point Mapping (HIGH PRIORITY)
**Missing:** `maps_to_outputs` is empty for all 100+ pain points
**Impact:** Cannot infer outputs from pain point descriptions
**Required:**
```json
// Fill in pain_point_mapping.json:
"pain_points": ["high variance", "systematic bias"],
"maps_to_outputs": [
  {"output_id": "sales_forecast", "confidence": 0.9},
  {"output_id": "demand_forecast", "confidence": 0.8}
]
```
**Effort:** ~16 hours (100+ pain points × 10 min each)

---

### Gap 3: Cross-Function Dependencies (MEDIUM PRIORITY)
**Missing:** No cross-function dependency catalog
**Impact:** Cannot infer "Marketing affects Sales" scenarios
**Required:** New file `cross_function_dependencies.json`
**Effort:** ~6 hours (estimate 20-30 cross-function edges)

---

### Gap 4: Evidence Tier Examples (MEDIUM PRIORITY)
**Missing:** No tier classification examples for LLM
**Impact:** Inconsistent tier detection, poor confidence scoring
**Required:** Add to `inference_rules/evidence_classification.json`
**Effort:** ~4 hours (5 tiers × 10 examples each)

---

### Gap 5: Node Deduplication Catalog (LOW PRIORITY)
**Missing:** No semantic similarity rules for nodes
**Impact:** Cannot detect "Sales tool" vs "CRM" ambiguity
**Required:** Alias mappings in common_systems.json
**Effort:** ~2 hours (already partially exists)

---

## 6. Inference Algorithm Pseudo-Code

### Algorithm 6.1: Vague Statement → Default Graph
```python
def handle_vague_statement(user_message: str) -> Graph:
    # Extract function mention
    function = extract_function(user_message)  # "sales"
    
    # Load template
    template = load_function_template(function)
    
    # Create default nodes
    output_nodes = create_outputs(template.common_outputs)
    people_nodes = create_people(template.typical_teams)
    tool_nodes = create_tools(template.typical_systems)
    process_nodes = create_processes(template.typical_processes)
    
    # Create edges with Tier 1 evidence
    edges = []
    for output in output_nodes:
        for people in people_nodes:
            edges.append(Edge(
                source=people, target=output,
                evidence=[Evidence(statement=user_message, tier=1)],
                score=None, confidence=0.3
            ))
        # Repeat for tools, processes
    
    return Graph(nodes=all_nodes, edges=edges)
```

**Data Required:** ✅ Available in function templates

---

### Algorithm 6.2: Specific Statement → Targeted Edge
```python
def handle_specific_statement(user_message: str, graph: Graph) -> Edge:
    # Extract entities
    entities = extract_entities(user_message)  # LLM call
    # {"people": "Sales Team", "output": "Sales Forecast", "quality": "junior"}
    
    # Find or create nodes
    people_node = graph.find_or_create_node("People", entities["people"])
    output_node = graph.find_or_create_node("Output", entities["output"])
    
    # Find or create edge
    edge = graph.find_or_create_edge(people_node, output_node)
    
    # Classify tier
    tier = classify_tier(user_message, entities)  # LLM call → 3
    
    # Extract score
    score = extract_score(entities["quality"])  # "junior" → ⭐⭐
    
    # Add evidence
    edge.evidence.append(Evidence(
        statement=user_message, tier=tier, score=score
    ))
    
    # Recalculate edge score using Bayesian
    edge.score, edge.confidence = aggregate_evidence(edge.evidence)
    
    return edge
```

**Data Required:** 
- ✅ component_scales.json for score mapping
- ❌ Tier classification examples

---

### Algorithm 6.3: Dependency Inference (2-Hop)
```python
def infer_dependency_chain(user_message: str, graph: Graph) -> List[Edge]:
    # Extract: "CRM data is messy, so forecasts are wrong"
    entities = extract_entities(user_message)
    # {"tool": "CRM", "output": "Sales Forecast", "quality": "messy"}
    
    # Find nodes
    tool_node = graph.find_node("Tool", entities["tool"])
    output_node = graph.find_node("Output", entities["output"])
    
    # Check if direct edge exists
    direct_edge = graph.find_edge(tool_node, output_node)
    if direct_edge:
        return [direct_edge]
    
    # Find intermediate nodes (1-hop)
    intermediate_outputs = graph.find_outputs_created_by_tool(tool_node)
    # → ["Pipeline Data"]
    
    # Find dependency edges (2-hop)
    dependency_edges = []
    for intermediate in intermediate_outputs:
        dep_edge = graph.find_dependency_edge(intermediate, output_node)
        if dep_edge:
            dependency_edges.append(dep_edge)
    
    # Create transitive edge: CRM → Pipeline Data → Sales Forecast
    if dependency_edges:
        # Create 1-hop edge: CRM → Pipeline Data
        edge_1 = graph.create_edge(tool_node, intermediate_outputs[0])
        edge_1.evidence.append(Evidence(statement=user_message, tier=3))
        
        # Use existing 2-hop edge: Pipeline Data → Sales Forecast
        edge_2 = dependency_edges[0]
        edge_2.evidence.append(Evidence(
            statement=f"Inferred from: {user_message}", tier=1
        ))
        
        return [edge_1, edge_2]
    
    # No path found → Ask user
    return []
```

**Data Required:** 
- ❌ MISSING: Dependency graph (Output → Output edges)
- ❌ MISSING: Tool → Output edges (partially in templates)

**Complexity:** O(N) for 1-hop, O(N²) for 2-hop (N = outputs per function, ~6)

---

## 7. Stress Test Results

### Test 7.1: Can Alternative B handle all 13 conversation patterns?

**Assessment Phase (Patterns 1-8):**

| Pattern | Data Available | Inference Possible | Confidence |
|---------|---------------|-------------------|------------|
| 1. Vagueness | ✅ Function templates | ✅ Yes | Medium (0.5) |
| 2. Specificity | ✅ Component scales | ✅ Yes | High (0.8) |
| 3. Contradictions | N/A (algorithm only) | ✅ Yes | High (0.9) |
| 4. Unknowns | N/A (algorithm only) | ✅ Yes | N/A |
| 5. Generic statements | ✅ Function templates | ✅ Yes | Low (0.3) |
| 6. Progressive refinement | N/A (algorithm only) | ✅ Yes | High (0.8) |
| 7. Cross-output mentions | ❌ Dependency graph | ❌ NO | N/A |
| 8. Corrections | N/A (algorithm only) | ✅ Yes | High (0.9) |

**Recommendation Phase (Patterns 9-13):**

| Pattern | Data Available | Inference Possible | Confidence |
|---------|---------------|-------------------|------------|
| 9. Pain point inference | ⚠️ Partial (empty maps_to_outputs) | ⚠️ LLM-based | Medium (0.6) |
| 10. Business context extraction | ✅ Decision dimensions taxonomy | ✅ Yes | High (0.7) |
| 11. Feasibility assessment | ❌ Archetype prerequisites | ❌ NO | N/A |
| 12. Solution mapping | ✅ AI archetypes + pilot catalog | ✅ LLM-based | Medium (0.6) |
| 13. Report generation | N/A (presentation only) | ✅ Yes | High (0.9) |

**Result:** 10/13 patterns supported, 3 require new data (dependency graph, archetype prerequisites, pain point mapping)

---

### Test 7.2: Can we infer pilot recommendations from bottleneck edges?

**Scenario:** Sales Forecast has bottleneck edge: Sales Team → Sales Forecast (⭐⭐)

**Required Inference:**
```
1. Identify bottleneck type: People edge
2. Lookup pilot types for People bottlenecks
3. Match to pilot catalog
4. Recommend: "AI Copilot for Sales Forecasting"
```

**Data Required:**
- ✅ `pilot_types.json` → 13 pilot types
- ✅ `pilot_catalog.json` → 28 specific pilots
- ❌ MISSING: Mapping from (bottleneck_type + output) → pilot

**Gap:** Need structured mapping:
```json
{
  "bottleneck_type": "People",
  "output_id": "sales_forecast",
  "recommended_pilots": [
    {"pilot_id": "ai_copilot_forecasting", "confidence": 0.9},
    {"pilot_id": "training_forecasting", "confidence": 0.7}
  ]
}
```

**Effort:** ~8 hours (46 outputs × 4 bottleneck types × 2 min each)

---

### Test 7.3: Can we handle feedback loops?

**Scenario:** "Bad forecasts → Bad territory planning → Bad forecasts"

**Required Inference:**
```
1. Detect cycle: Sales Forecast → Territory Plan → Sales Forecast
2. Flag as feedback loop
3. Communicate: "Vicious cycle detected"
4. Do NOT track momentum (per scope constraint)
```

**Data Required:** ❌ MISSING
- No feedback loop catalog
- No cycle detection rules

**Scope Decision:** Alternative B says "Detect + Communicate Only"
**Implementation:** Graph cycle detection algorithm (standard BFS/DFS)
**Effort:** ~4 hours (algorithm + tests)

---
## 8. Implementation Readiness Assessment

### Data Completeness: 55%
- Function templates (8/22 functions, 46 outputs)
- Component scales (1-5 star ratings)
- System catalog (40+ systems)
- Pilot catalog (28 pilots)
- AI archetypes (27 archetypes)
- Business decision dimensions taxonomy
- Dependency graph (0% complete)
- Pain point mapping (0% complete - maps_to_outputs empty)
- Cross-function dependencies (0% complete)
- Evidence tier examples (0% complete)
- Archetype prerequisites (0% complete - NEW REQUIREMENT)

### Algorithm Complexity: Medium-High
- **Simple:** Vague statement → Default graph (O(N))
- **Medium:** Specific statement → Targeted edge (O(1))
- **Complex:** Dependency inference (O(N²) for 2-hop)
- **Very Complex:** Node deduplication (semantic similarity, LLM-dependent)

### LLM Dependency: High
- Entity extraction (every user message)
- Tier classification (every evidence piece)
- Score extraction (every quality mention)
- Semantic similarity (every node creation)
- Contradiction detection (every evidence update)

**Risk:** LLM errors cascade through graph

---

## 9. Recommendations

### Option A: Implement with Data Gaps (NOT RECOMMENDED)
- Start with 55% data completeness
- Implement algorithms, fill data incrementally
- **Risk:** Poor inference quality, low user confidence, failed pilots

### Option B: Fill Critical Gaps First (RECOMMENDED)
**Release 1: Fill Data (4-5 days)**
1. Add dependency graph to 46 outputs (~8h)
2. Map 100+ pain points to outputs (~16h)
3. Add evidence tier examples (~4h)
4. Document archetype prerequisites for 27 archetypes (~54h)

**Release 2: Implement (1.5-2 weeks)**
5. Build graph infrastructure
6. Implement inference algorithms
7. Implement feasibility checker
8. Implement report generator
9. Test with real conversations

**Total:** ~3-3.5 weeks

### Option C: Hybrid Model (ALTERNATIVE)
- Keep 4-component model (Team, System, Process, Dependency)
- Add evidence tracking to components
- Add LLM semantic inference for recommendations
- Add feasibility assessment (simplified)
- Skip full graph refactoring
- **Benefit:** Faster implementation (2 weeks), less data required
- **Tradeoff:** Cannot handle cross-output dependencies, less flexible, no multi-hop inference

---

## 10. Critical Questions for Decision

1. **Is cross-function dependency inference required?**
   - If YES → Need cross-function dependency catalog (~6h)
   - If NO → Can skip, limit to single-function assessments

2. **Is pain point inference required?**
   - If YES → Need pain point mapping (~16h)
   - If NO → User must explicitly mention outputs

3. **Is 2-hop dependency inference required?**
   - If YES → Need full dependency graph (~8h)
   - If NO → Limit to 1-hop (direct dependencies only)

4. **What LLM error tolerance is acceptable?**
   - If LOW → Need extensive validation, tier examples
   - If HIGH → Can proceed with basic prompts

5. **What is the target assessment scope?**
   - Single output → Simpler, less data needed
   - Multiple outputs → Requires dependency graph
   - Cross-function → Requires cross-function catalog

---

## Conclusion

**Alternative B is FEASIBLE but requires 82 hours (~2 weeks) of data preparation before implementation.**

**Critical Path:**
1. Dependency graph (8h) → Enables multi-hop inference
2. Pain point mapping (16h) → Enables pain point discovery
3. Evidence tier examples (4h) → Enables confidence scoring
4. Archetype prerequisites (54h) → Enables feasibility assessment & prevents failed pilots

**Without these, Alternative B will have:**
- ❌ Poor inference from vague statements
- ❌ No dependency chain reasoning
- ❌ Inconsistent confidence scores
- ❌ No feasibility assessment → Failed pilots, lost user trust
- ❌ Cannot generate comprehensive reports

**New Capabilities Added:**
- ✅ LLM semantic inference for problem→solution jump
- ✅ Business context extraction (8 natural moments)
- ✅ Feasibility assessment with prerequisite checking
- ✅ Two-tier recommendations (light conversational + deep report)
- ✅ User override mechanism for prerequisite assessment

**Total Implementation Effort:**
- Data preparation: 82 hours (~2 weeks)
- Implementation: 120-160 hours (~3-4 weeks)
- **Total: 200-240 hours (~5-6 weeks)**

**Recommendation:** Fill critical data gaps (Release 1) before implementing graph model (Release 2). Alternative B is production-ready design with clear implementation path.
