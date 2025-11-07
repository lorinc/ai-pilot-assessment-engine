# Graph Visualization Design: Making Knowledge Extraction Transparent

**Date:** November 7, 2025  
**Tool:** st-link-analysis (Streamlit + Cytoscape.js)  
**Context:** Conversational operational graph extraction (Iteration 8+)

---

## Problem Statement

### The Challenge

During conversational knowledge extraction, users tell their story incrementally over 20-30+ turns. The system builds an operational dependency graph in the background. **Users need to see:**

1. **What we've extracted so far** - Current graph state
2. **What we just added** - New entities/dependencies this turn
3. **What we're asking about** - Why we need clarification
4. **Where the problems are** - Quality scores, bottlenecks, error propagation

### Why Visualization Matters

**Without visualization:**
- User has no mental model of what system knows
- Can't verify extraction accuracy
- Can't see connections between entities
- No sense of progress

**With visualization:**
- Immediate feedback after each turn
- Visual confirmation of understanding
- See graph growing in real-time
- Identify missing information visually
- Understand quality degradation paths

---

## Solution: st-link-analysis Integration

### Why st-link-analysis?

**Key Features:**
- ✅ **Streamlit native** - Integrates with our conversational UI
- ✅ **Cytoscape.js backend** - Powerful graph rendering
- ✅ **Interactive** - Click nodes/edges to see details
- ✅ **Customizable styling** - Color-code by type, quality
- ✅ **Material icons** - Visual entity type indicators
- ✅ **Layout algorithms** - Auto-arrange for clarity
- ✅ **Event handling** - Node expand/remove actions
- ✅ **Side panel** - View entity properties
- ✅ **Toolbar** - Zoom, fit, export JSON

**Perfect fit for:**
- Real-time graph updates during conversation
- Highlighting new additions
- Color-coding quality issues
- Interactive exploration

---

## Visual Design Strategy

### Node Types & Styling

#### 1. Actor Nodes (Teams/People)
```python
NodeStyle(
    label="Actor",
    color="#FF7F3E",  # Orange
    caption="name",
    icon="group"  # Material icon: group of people
)
```

**Visual Properties:**
- Shape: Circle
- Icon: `group` (team) or `person` (individual)
- Size: Based on number of activities performed
- Border: Solid

**Example:** "marketing team", "sales team", "production planning team"

---

#### 2. Artifact Nodes (Outputs/Data)
```python
NodeStyle(
    label="Artifact",
    color="#2A629A",  # Blue
    caption="name",
    icon="description"  # Material icon: document
)
```

**Visual Properties:**
- Shape: Rounded rectangle
- Icon: `description` (document) or `dataset` (data)
- Size: Based on number of dependencies
- Border: Quality-based (solid=good, dashed=issues, red=critical)

**Quality Color Coding:**
- Quality 0.8-1.0: Green border
- Quality 0.5-0.7: Yellow border
- Quality 0.0-0.4: Red border

**Example:** "campaign forecasts", "pipeline projections", "production orders"

---

#### 3. Tool Nodes (Systems/Software)
```python
NodeStyle(
    label="Tool",
    color="#7E60BF",  # Purple
    caption="name",
    icon="computer"  # Material icon: computer
)
```

**Visual Properties:**
- Shape: Diamond
- Icon: `computer` (system) or `storage` (database)
- Size: Based on number of activities using it
- Border: Solid

**Example:** "HubSpot", "Salesforce", "Excel"

---

#### 4. Activity Nodes (Processes)
```python
NodeStyle(
    label="Activity",
    color="#4CAF50",  # Green
    caption="name",
    icon="settings"  # Material icon: gear
)
```

**Visual Properties:**
- Shape: Hexagon
- Icon: `settings` (process) or `sync` (workflow)
- Size: Medium (uniform)
- Border: Solid

**Example:** "create campaign forecasts", "adjust projections", "generate production orders"

---

### Edge Types & Styling

#### 1. PERFORMS (Actor → Activity)
```python
EdgeStyle(
    label="PERFORMS",
    color="#666666",  # Gray
    caption="label",
    directed=True,
    line_style="solid"
)
```

**Visual Properties:**
- Arrow: Yes (directed)
- Line: Solid
- Width: Thin
- Label: "PERFORMS"

---

#### 2. PRODUCES (Activity → Artifact)
```python
EdgeStyle(
    label="PRODUCES",
    color="#4CAF50",  # Green
    caption="label",
    directed=True,
    line_style="solid"
)
```

**Visual Properties:**
- Arrow: Yes (directed)
- Line: Solid
- Width: Medium
- Label: "PRODUCES"

---

#### 3. DEPENDS_ON (Artifact → Activity or Activity → Artifact)
```python
EdgeStyle(
    label="DEPENDS_ON",
    color="#FF5722",  # Red-orange
    caption="label",
    directed=True,
    line_style="dashed"
)
```

**Visual Properties:**
- Arrow: Yes (directed)
- Line: Dashed (indicates dependency)
- Width: Thick (critical relationship)
- Label: "DEPENDS_ON"

**Quality Indicators:**
- Error propagation risk: Line thickness
- High risk (>0.7): Very thick, bright red
- Medium risk (0.4-0.7): Medium, orange
- Low risk (<0.4): Thin, yellow

---

#### 4. USES (Activity → Tool)
```python
EdgeStyle(
    label="USES",
    color="#7E60BF",  # Purple
    caption="label",
    directed=True,
    line_style="dotted"
)
```

**Visual Properties:**
- Arrow: Yes (directed)
- Line: Dotted
- Width: Thin
- Label: "USES"

---

## Conversational Integration

### Turn-by-Turn Visualization Flow

#### Turn 1: First Extraction
```
User: "Marketing creates campaign forecasts in HubSpot"

System extracts:
- Actor: marketing team
- Activity: create campaign forecasts
- Tool: HubSpot
- Artifact: campaign forecasts

Visualization shows:
[marketing team] --PERFORMS--> [create forecasts] --PRODUCES--> [campaign forecasts]
                                      |
                                    USES
                                      ↓
                                  [HubSpot]

Highlight: All nodes/edges in bright yellow (NEW)
```

**User sees:**
- 4 nodes appear
- 3 edges connect them
- All highlighted as new
- Side panel: "Added this turn: 4 entities, 3 relationships"

---

#### Turn 2: Adding Context
```
User: "The forecasts are based on data scattered across HubSpot, 
       Google Analytics, and an old Excel file"

System extracts:
- Tools: Google Analytics, Excel
- Quality issue: "scattered data sources"
- Update: campaign_forecasts.quality_score = 0.3

Visualization shows:
- Previous graph (fades to normal color)
- New tools: Google Analytics, Excel (highlighted yellow)
- campaign_forecasts node: border turns RED (quality issue)
- Quality badge appears: "⚠️ 0.3"

Highlight: New nodes in yellow, updated node border flashes red
```

**User sees:**
- 2 new tool nodes appear
- campaign_forecasts border changes to red
- Quality score badge appears
- Side panel: "Quality issue detected: scattered data sources"

---

#### Turn 5: Adding Dependencies
```
User: "Sales team takes those forecasts and builds pipeline projections in Salesforce"

System extracts:
- Actor: sales team
- Activity: build pipeline projections
- Tool: Salesforce
- Artifact: pipeline projections
- Dependency: pipeline_projections DEPENDS_ON campaign_forecasts

Visualization shows:
- New chain appears to the right
- Thick dashed red line: campaign_forecasts --> pipeline_projections
- Line thickness indicates error propagation risk

Highlight: New nodes/edges in yellow, dependency edge pulses
```

**User sees:**
- Graph expands horizontally
- Dependency chain becomes visible
- Error propagation path highlighted
- Side panel: "Dependency detected: pipeline projections relies on campaign forecasts (quality: 0.3)"

---

#### Turn 15: Completing the Chain
```
User: "Production planning takes those sales projections and creates production orders"

System extracts:
- Actor: production planning team
- Activity: create production orders
- Artifact: production orders
- Dependency: production_orders DEPENDS_ON pipeline_projections

Visualization shows:
- Full chain now visible:
  campaign_forecasts (0.3) --> pipeline_projections (0.4) --> production_orders (0.2)
- Quality degradation path highlighted in red gradient
- Bottleneck indicator on campaign_forecasts (root cause)

Highlight: New nodes/edges in yellow, quality path in red gradient
```

**User sees:**
- Complete operational flow
- Quality degradation clearly visible
- Root cause highlighted (campaign_forecasts)
- Side panel: "Quality bottleneck identified: campaign forecasts (0.3) affects 2 downstream outputs"

---

## Interactive Features

### 1. Node Click: View Details
**User clicks on "campaign forecasts" node**

**Side panel shows:**
```
Artifact: campaign forecasts
Type: Artifact
Quality Score: 0.3 ⚠️

Issues:
- Scattered data sources
- Stale data
- Always wrong

Created by: marketing team
Tool: HubSpot

Upstream dependencies: None
Downstream dependencies:
- pipeline projections (sales team)

Mentioned in turns: 1, 2, 7, 15
```

---

### 2. Edge Click: View Dependency Details
**User clicks on DEPENDS_ON edge: campaign_forecasts → pipeline_projections**

**Side panel shows:**
```
Dependency: pipeline projections ← campaign forecasts
Type: DEPENDS_ON
Causal Certainty: 0.9 (high confidence)
Error Propagation Risk: 0.8 ⚠️

Impact:
- Quality of campaign forecasts (0.3) directly affects pipeline projections
- Errors compound: 10% error becomes 15% error

Mentioned in turn: 5
```

---

### 3. Node Expand: Show Neighborhood
**User double-clicks on "sales team" node**

**Graph expands to show:**
- All activities performed by sales team
- All artifacts produced
- All tools used
- All dependencies

**Use case:** Explore what a specific team does

---

### 4. Layout Refresh: Re-arrange Graph
**User clicks layout button**

**Options:**
- `cose`: Force-directed (default) - good for general graphs
- `breadthfirst`: Hierarchical - good for dependency chains
- `circle`: Circular - good for seeing all entities
- `grid`: Grid layout - good for large graphs

**Use case:** Find best view for current graph structure

---

### 5. Zoom & Fit: Navigate Large Graphs
**Toolbar buttons:**
- Zoom in/out
- Fit to screen
- Center on selected node

**Use case:** Navigate graphs with 20+ entities

---

### 6. Export JSON: Save Graph State
**User clicks export button**

**Downloads:**
```json
{
  "nodes": [...],
  "edges": [...],
  "metadata": {
    "turns": 15,
    "entities": 12,
    "dependencies": 8,
    "quality_issues": 5
  }
}
```

**Use case:** Save progress, share with team, debug

---

## Implementation Strategy

### Phase 1: Basic Visualization (Iteration 8)

**Goal:** Show graph after each turn with basic styling

**Features:**
- Render graph with 4 node types
- Color-code by entity type
- Show new additions highlighted
- Basic layout (cose)

**Code Structure:**
```python
def render_graph(graph: GraphStore, new_entities: list, new_edges: list):
    """Render graph with st-link-analysis."""
    
    # Convert graph to elements format
    elements = {
        "nodes": [format_node(e) for e in graph.entities],
        "edges": [format_edge(e) for e in graph.dependencies]
    }
    
    # Define styles
    node_styles = [
        NodeStyle("Actor", "#FF7F3E", "name", "group"),
        NodeStyle("Artifact", "#2A629A", "name", "description"),
        NodeStyle("Tool", "#7E60BF", "name", "computer"),
        NodeStyle("Activity", "#4CAF50", "name", "settings")
    ]
    
    edge_styles = [
        EdgeStyle("PERFORMS", directed=True),
        EdgeStyle("PRODUCES", directed=True),
        EdgeStyle("DEPENDS_ON", directed=True, line_style="dashed"),
        EdgeStyle("USES", directed=True, line_style="dotted")
    ]
    
    # Render
    st_link_analysis(elements, "cose", node_styles, edge_styles)
```

**Effort:** 0.5 day

---

### Phase 2: Quality Visualization (Iteration 10)

**Goal:** Show quality scores and issues visually

**Features:**
- Color-code node borders by quality
- Show quality badges on nodes
- Highlight quality degradation paths
- Thickness of dependency edges = error propagation risk

**Code Structure:**
```python
def format_node_with_quality(entity: Entity) -> dict:
    """Format node with quality indicators."""
    
    node = {
        "data": {
            "id": entity.id,
            "label": entity.type,
            "name": entity.name
        }
    }
    
    # Add quality styling
    if entity.quality_score is not None:
        if entity.quality_score < 0.4:
            node["classes"] = "quality-critical"
        elif entity.quality_score < 0.7:
            node["classes"] = "quality-warning"
        else:
            node["classes"] = "quality-good"
        
        # Add badge
        node["data"]["badge"] = f"⚠️ {entity.quality_score:.1f}"
    
    return node
```

**Effort:** 1 day

---

### Phase 3: Interactive Exploration (Iteration 12)

**Goal:** Enable user to explore graph interactively

**Features:**
- Click node to see details in side panel
- Click edge to see dependency details
- Double-click to expand neighborhood
- Highlight path on hover

**Code Structure:**
```python
# Enable node actions
selected = st_link_analysis(
    elements, 
    layout="cose",
    node_styles=node_styles,
    edge_styles=edge_styles,
    node_actions=True  # Enable expand/remove
)

# Handle selection
if selected:
    if selected["event"] == "node_click":
        show_node_details(selected["node_id"])
    elif selected["event"] == "edge_click":
        show_edge_details(selected["edge_id"])
    elif selected["event"] == "node_expand":
        expand_neighborhood(selected["node_id"])
```

**Effort:** 1 day

---

## UI Layout Design

### Streamlit App Layout

```
┌─────────────────────────────────────────────────────────────┐
│  AI Pilot Assessment: Operational Graph Extraction          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Chat Interface (Left Column - 40%)                         │
│  ┌────────────────────────────────────┐                    │
│  │ User: Marketing creates forecasts  │                    │
│  │                                     │                    │
│  │ System: Got it! I see:             │                    │
│  │ • Marketing team                   │                    │
│  │ • Campaign forecasts               │                    │
│  │ • HubSpot                          │                    │
│  │                                     │                    │
│  │ Is this correct?                   │                    │
│  │                                     │                    │
│  │ [User input box]                   │                    │
│  └────────────────────────────────────┘                    │
│                                                              │
│  Graph Visualization (Right Column - 60%)                   │
│  ┌────────────────────────────────────────────────────────┐│
│  │  [Toolbar: Zoom | Fit | Layout | Export]              ││
│  │                                                         ││
│  │     [marketing team]                                   ││
│  │           ↓ PERFORMS                                   ││
│  │     [create forecasts]                                 ││
│  │           ↓ PRODUCES                                   ││
│  │     [campaign forecasts] ⚠️ 0.3                       ││
│  │           ↓ USES                                       ││
│  │        [HubSpot]                                       ││
│  │                                                         ││
│  │  New this turn: 4 entities, 3 relationships           ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  Details Panel (Bottom - Collapsible)                       │
│  ┌────────────────────────────────────────────────────────┐│
│  │  Selected: campaign forecasts                          ││
│  │  Quality: 0.3 ⚠️                                       ││
│  │  Issues: scattered data sources, stale data            ││
│  │  Downstream impact: pipeline projections (0.4)         ││
│  └────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## User Experience Flow

### Scenario: User Tells Cascading Failures Story

**Turn 1:**
```
User types: "Marketing creates campaign forecasts in HubSpot"
→ Graph appears with 4 nodes (all highlighted yellow)
→ User sees: "✓ Added: marketing team, campaign forecasts, HubSpot"
```

**Turn 2:**
```
User types: "The data is scattered across multiple tools"
→ Graph updates: campaign forecasts border turns red
→ User sees: "⚠️ Quality issue detected on campaign forecasts"
```

**Turn 5:**
```
User types: "Sales takes those forecasts and builds projections"
→ Graph expands: new chain appears to the right
→ User sees dependency line connecting forecasts → projections
→ User thinks: "Oh, I see how it flows now"
```

**Turn 10:**
```
User clicks on campaign forecasts node
→ Side panel shows: quality score, issues, downstream impact
→ User thinks: "This is the root cause!"
```

**Turn 15:**
```
User finishes story
→ Graph shows complete operational flow
→ Quality degradation path highlighted in red
→ User sees: "Bottleneck identified: campaign forecasts affects 3 downstream outputs"
→ User exports graph for discussion with team
```

---

## Benefits

### For Users
1. **Transparency** - See what system understands
2. **Verification** - Confirm extraction accuracy visually
3. **Insight** - Discover connections they didn't realize
4. **Progress** - See graph growing, feel productive
5. **Exploration** - Click around to understand relationships

### For System
1. **Feedback** - User corrections improve extraction
2. **Engagement** - Visual feedback keeps user engaged
3. **Trust** - Transparency builds trust
4. **Debugging** - Easy to spot extraction errors
5. **Communication** - Graph is shareable artifact

---

## Technical Requirements

### Dependencies
```bash
pip install streamlit
pip install st-link-analysis
```

### Integration Points
1. **After extraction:** Convert graph to elements format
2. **After update:** Highlight new additions
3. **On user click:** Show entity details
4. **On export:** Save graph JSON

### Performance Considerations
- Render time: <500ms for 20 nodes
- Update time: <200ms for incremental updates
- Memory: ~5MB for 50 node graph
- Responsive: Works on laptop screens (1366x768+)

---

## Future Enhancements

### Phase 4: Advanced Features
1. **Time travel** - Replay graph building turn-by-turn
2. **Diff view** - Show what changed between turns
3. **Quality heatmap** - Color entire graph by quality
4. **Path highlighting** - Show error propagation paths
5. **Clustering** - Group entities by team/domain
6. **Search** - Find entities by name
7. **Filters** - Hide/show entity types
8. **Annotations** - User can add notes to nodes

### Phase 5: Collaboration
1. **Share graph** - Generate shareable link
2. **Comments** - Team can comment on nodes
3. **Versions** - Save multiple graph versions
4. **Compare** - Diff two graph versions

---

## Success Metrics

### Quantitative
- Graph render time: <500ms
- User interaction rate: >50% of users click nodes
- Export rate: >30% of users export graph
- Error detection: Users catch 80% of extraction errors visually

### Qualitative
- User feedback: "I can see what you're building"
- User feedback: "The visualization helped me understand the problem"
- User feedback: "I found connections I didn't realize existed"

---

## Conclusion

st-link-analysis provides the perfect foundation for making operational graph extraction transparent and accessible. By showing users the graph as it builds, we:

1. **Build trust** through transparency
2. **Enable verification** through visualization
3. **Facilitate insight** through exploration
4. **Create artifacts** through export

The conversational + visual approach transforms extraction from a black box into a collaborative graph-building experience.

**Next steps:** Implement Phase 1 (basic visualization) in Iteration 8.
