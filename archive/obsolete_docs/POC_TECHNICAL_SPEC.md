# POC Technical Specification - Minimal Happy Path (No ROI)

**Version:** 1.0  
**Date:** 2025-11-02  
**Ground Truth:** `docs/1_functional_spec/domain_model.md`  
**Scope:** Steps 1-8 of assessment flow (Output Discovery → Pilot Recommendation)

---

## Assumptions & Decisions

### Platform & Architecture
**Decision:** LLM-based conversational interface (chat-based)
- **Technology:** Python backend with Gemini API (Vertex AI)
- **Interface:** Streamlit web app (chat window)
- **Deployment:** Local development initially, Cloud Run for demo
- **Rationale:** Aligns with user_interaction_guideline.md emphasis on conversational flow and existing architecture_summary.md

### Data Storage
**Decision:** Simplified for POC (vs full architecture)
- **POC Approach:** JSON file-based persistence
  - **Session data:** Streamlit session_state (in-memory, 3-minute timeout)
  - **Assessment snapshots:** Saved to JSON files on disk
  - **Taxonomy data:** Read from existing `src/data/` JSON files
- **Full Architecture (future):**
  - **Firestore:** User data, factors, journal entries
  - **Cloud Storage:** Static knowledge graph
  - **NetworkX:** In-memory graph traversal
- **Rationale:** POC keeps it simple; full architecture provides scalability and multi-user support

### LLM Integration
**Decision:** Hybrid approach (Gemini + rule-based)
- **LLM:** Gemini 1.5 Flash via Vertex AI (streaming responses)
- **Why Flash not Pro:** 4x cheaper ($0.075 vs $0.30 per 1M output tokens), fast inference (<1s first token), sufficient quality
- **LLM Role:** Natural language understanding, context inference, conversation management
- **Rules Role:** Component assessment logic (MIN calculation), pilot selection
- **Taxonomy Access:** Gemini has access to relevant taxonomy files as context
- **Streaming:** Async generators for real-time token streaming
- **Rationale:** Gemini for flexibility, rules for deterministic calculations per domain_model.md

### Scope Limitations
**Decision:** Simplified for POC
- **Functions:** Use 2-3 function templates (Sales, Finance, Operations) - ~18 outputs
- **Dependencies:** User manually specifies, no automatic dependency graph traversal
- **Quality Metrics:** Generic "quality" rating (1-5 stars) OR user defines metric names conversationally
- **Quantity:** Skip quantity assessment in POC, focus on quality only
- **Rationale:** Demonstrates core value without full complexity

### Component Assessment
**Assumption:** Conversational inference with validation
- **User describes situation** → LLM infers star rating using component_scales.json indicators
- **System shows inference** → User confirms or adjusts
- **Fallback:** User can directly provide star rating (1-5)
- **Rationale:** Follows user_interaction_guideline.md "LLM generates, user validates"

---

## System Architecture

### High-Level Flow
```
User Input (Chat)
    ↓
LLM Conversation Manager
    ↓
[Step 1-3] Output Discovery & Context Inference
    ├─→ Query: function_templates/*.json
    ├─→ Query: inference_rules/output_discovery.json
    └─→ Query: common_systems.json
    ↓
[Step 4] Component Assessment
    ├─→ Query: component_scales.json
    └─→ LLM infers ratings from user descriptions
    ↓
[Step 5] MIN Calculation (Rule-Based)
    └─→ actual_quality = MIN(Team, System, Process, Dependency)
    ↓
[Step 6] Required Quality Collection
    └─→ User provides target (⭐ 1-5)
    ↓
[Step 7] Gap Analysis (Rule-Based)
    └─→ gap = required - actual
    └─→ bottleneck = component with MIN value
    ↓
[Step 8] Pilot Recommendation
    ├─→ Query: pilot_types.json (by bottleneck component)
    ├─→ Query: pilot_catalog.json (specific examples)
    └─→ LLM formats recommendation
    ↓
Output: Recommendation Report
```

### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (Chat)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Conversation Manager (LLM-based)                │
│  - Manages conversation state                                │
│  - Routes to appropriate handler                             │
│  - Maintains context                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
│   Discovery  │  │    Assessment    │  │ Recommender  │
│    Engine    │  │     Engine       │  │    Engine    │
│              │  │                  │  │              │
│ - Output ID  │  │ - Component      │  │ - Pilot      │
│ - Context    │  │   Rating         │  │   Selection  │
│   Inference  │  │ - MIN Calc       │  │ - Formatting │
└──────────────┘  └──────────────────┘  └──────────────┘
        ↓                   ↓                   ↓
┌─────────────────────────────────────────────────────────────┐
│                  Taxonomy Data Layer                         │
│  - function_templates/                                       │
│  - component_scales.json                                     │
│  - pilot_types.json                                          │
│  - pilot_catalog.json                                        │
│  - inference_rules/                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## POC vs Full Architecture

This POC is a **simplified implementation** of the full architecture documented in `architecture_summary.md`. Key differences:

| Aspect | POC | Full Architecture |
|--------|-----|-------------------|
| **UI** | Single chat window | 3-panel UI (chat \| knowledge tree \| technical log) |
| **Persistence** | JSON files on disk | Firestore + Cloud Storage |
| **Session** | In-memory (Streamlit session_state) | Firestore with user isolation |
| **Auth** | None (single user) | Firebase Auth (Google OAuth + Email) |
| **Graph** | No graph (direct taxonomy lookup) | NetworkX in-memory graph with traversal |
| **Scope** | Output-centric (Steps 1-8 only) | Output-centric (full flow + ROI) |
| **Streaming** | Simple async generators | SSE with technical event markers |
| **Context** | Conversation history only | Cumulative factor journal with synthesis |
| **Multi-user** | No | Yes (isolated Firestore subcollections) |

**POC Goal:** Validate the core assessment flow (Output Discovery → Pilot Recommendation) with minimal infrastructure.

**Migration Path:** POC code can be refactored to use Firestore/Firebase by replacing the JSON persistence layer and adding authentication. The core logic (discovery, assessment, recommendation) remains the same.

---

## Detailed Component Specifications

### 1. Discovery Engine

**Purpose:** Identify output from user description (Steps 1-3)

**Inputs:**
- User message (natural language)
- Conversation history
- Taxonomy files:
  - `organizational_templates/functions/*.json`
  - `inference_rules/output_discovery.json`
  - `inference_rules/pain_point_mapping.json`
  - `organizational_templates/cross_functional/common_systems.json`

**Process:**
1. **LLM Analysis:**
   - Extract keywords, pain points, system mentions from user message
   - Match against inference_triggers in function templates
   - Rank potential outputs by confidence

2. **Output Suggestion:**
   - Present top 1-3 matching outputs
   - Show confidence level
   - Format: "It sounds like you're talking about [Output Name]. Is that right?"

3. **Context Inference:**
   - Load `typical_creation_context` from matched output
   - Present as [UNVERIFIED]: Team, Process, System
   - Ask user to confirm or correct

**Outputs:**
- Identified output (confirmed by user)
- Creation context (Team, Process, System)
- Confidence score

**Implementation Notes:**
- Use semantic similarity for fuzzy matching (embeddings or LLM-based)
- Fall back to exact keyword matching if LLM unavailable
- Support user correction: "No, I meant [different output]"

---

### 2. Assessment Engine

**Purpose:** Collect component ratings and calculate actual quality (Steps 4-5)

**Inputs:**
- Confirmed output
- User descriptions of situation
- `component_scales.json`

**Process:**

#### Step 4a: Team Execution Assessment
```
System: "Tell me about the team creating [Output Name]. 
         How experienced are they? Any challenges?"

User: "They're learning as they go, no formal training"

LLM: [Matches to component_scales.json indicators]
     → Team Execution = ⭐⭐ (Junior team, learning on the job)

System: "Based on what you described, I'd rate Team Execution as ⭐⭐ 
         (Junior team, learning on the job). Does that sound right?"

User: "Yes" OR "No, more like ⭐⭐⭐"
```

#### Step 4b: System Capabilities Assessment
```
System: "What system do you use to create [Output Name]?"

User: "Salesforce, but it's pretty basic"

LLM: [Matches to component_scales.json indicators]
     → System Capabilities = ⭐⭐ (Basic features, limited automation)

System: "I'd rate System Capabilities as ⭐⭐ (Basic features). Confirm?"
```

#### Step 4c: Process Maturity Assessment
```
System: "How would you describe the process for creating [Output Name]?"

User: "We have a standard process but it's all manual"

LLM: → Process Maturity = ⭐⭐⭐ (Standardized but manual)

System: "Process Maturity: ⭐⭐⭐ (Standardized but manual). Right?"
```

#### Step 4d: Dependency Quality Assessment
```
System: "Does [Output Name] depend on any other outputs or data sources?"

User: "Yes, it uses pipeline data from our CRM"

System: "How would you rate the quality of that pipeline data?"

User: "It's decent, maybe ⭐⭐⭐"

System: → Dependency Quality = ⭐⭐⭐
```

**Simplified Approach (if LLM inference fails):**
```
System: "Rate each component from ⭐ to ⭐⭐⭐⭐⭐:
         - Team Execution: [1-5]
         - System Capabilities: [1-5]
         - Process Maturity: [1-5]
         - Dependency Quality: [1-5]"
```

#### Step 5: MIN Calculation (Rule-Based)
```python
def calculate_actual_quality(team, system, process, dependency):
    """
    Per domain_model.md: actual_quality = MIN of 4 components
    """
    return min(team, system, process, dependency)
```

**Outputs:**
- Team Execution: ⭐ 1-5
- System Capabilities: ⭐ 1-5
- Process Maturity: ⭐ 1-5
- Dependency Quality: ⭐ 1-5
- **Actual Quality: MIN of above**
- **Bottleneck Component: Which component = MIN**

**Implementation Notes:**
- Store each component rating separately
- If multiple components tied at MIN, identify all bottlenecks
- Show calculation to user: "MIN(⭐⭐, ⭐⭐, ⭐⭐⭐, ⭐⭐⭐) = ⭐⭐"

---

### 3. Gap Analysis Engine

**Purpose:** Identify gap and bottleneck (Steps 6-7)

**Inputs:**
- Actual Quality (from Assessment Engine)
- Required Quality (from user)
- Component ratings

**Process:**

#### Step 6: Required Quality Collection
```
System: "What quality level do you need for [Output Name]?
         Current: ⭐⭐
         Target: [⭐ to ⭐⭐⭐⭐⭐]"

User: "We need at least ⭐⭐⭐⭐"

System: → Required Quality = ⭐⭐⭐⭐
```

#### Step 7: Gap Calculation (Rule-Based)
```python
def analyze_gap(actual, required, components):
    """
    Calculate gap and identify bottleneck(s)
    """
    gap = required - actual
    bottleneck_value = min(components.values())
    bottlenecks = [name for name, value in components.items() 
                   if value == bottleneck_value]
    
    return {
        'gap': gap,
        'bottleneck_value': bottleneck_value,
        'bottlenecks': bottlenecks
    }
```

**Outputs:**
- Gap size (stars)
- Bottleneck component(s)
- Improvement needed

**Display Format:**
```
System: "Gap Analysis:
         Current: ⭐⭐
         Target: ⭐⭐⭐⭐
         Gap: 2 stars
         
         Bottleneck: Team Execution (⭐⭐) and System Capabilities (⭐⭐)
         
         To reach ⭐⭐⭐⭐, you need to improve the weakest components."
```

---

### 4. Recommender Engine

**Purpose:** Recommend pilot projects (Step 8)

**Inputs:**
- Bottleneck component(s)
- Gap size
- Output context
- Taxonomy files:
  - `pilot_types.json`
  - `pilot_catalog.json`
  - `ai_archetypes.json`

**Process:**

1. **Pilot Type Selection:**
```python
def select_pilot_types(bottleneck_component):
    """
    Map bottleneck to pilot category
    Per domain_model.md:
    - Team Execution → Team pilots
    - System Capabilities → System pilots
    - Process Maturity → Process pilots
    """
    pilot_mapping = {
        'Team Execution': 'team_execution',
        'System Capabilities': 'system_capabilities',
        'Process Maturity': 'process_maturity'
    }
    
    category = pilot_mapping[bottleneck_component]
    return load_pilot_types(category)
```

2. **Specific Example Matching:**
```python
def find_pilot_examples(output_name, bottleneck, pilot_catalog):
    """
    Find relevant examples from pilot_catalog.json
    Match by:
    - Applicable functions
    - Pain points
    - AI archetypes
    """
    relevant_examples = []
    for category in pilot_catalog['categories']:
        for pilot in category['pilots']:
            if matches_context(pilot, output_name, bottleneck):
                relevant_examples.append(pilot)
    
    return relevant_examples[:3]  # Top 3
```

3. **Recommendation Formatting:**
```
System: "Based on your bottleneck (Team Execution ⭐⭐), here are 3 pilot options:

**Option 1: AI Copilot for [Output Name]**
- What it does: Assists team with real-time suggestions
- Expected impact: ⭐⭐ → ⭐⭐⭐⭐ (2 star improvement)
- Timeline: 8-12 weeks
- Cost: €20k-€40k
- Prerequisites: Team willing to adopt new tool

**Option 2: Team Training & Upskilling**
- What it does: Formal training program for the team
- Expected impact: ⭐⭐ → ⭐⭐⭐ (1 star improvement, slower)
- Timeline: 12-16 weeks
- Cost: €10k-€20k
- Prerequisites: Time for training, management support

**Option 3: Knowledge Management System**
- What it does: Centralized knowledge base with best practices
- Expected impact: ⭐⭐ → ⭐⭐⭐ (1 star improvement)
- Timeline: 6-10 weeks
- Cost: €15k-€25k
- Prerequisites: Content creation, team adoption

Which option interests you most?"
```

**Outputs:**
- 2-3 pilot recommendations
- For each pilot:
  - Name and description
  - Expected impact (star improvement)
  - Timeline
  - Cost range
  - Prerequisites

**Implementation Notes:**
- If multiple bottlenecks, offer pilots for each OR combo pilots
- Use `ai_archetypes.json` to add technical credibility
- Use `pilot_catalog.json` for specific examples
- Format for easy comparison

---

## Data Models

### Assessment Session
```json
{
  "session_id": "uuid",
  "created_at": "timestamp",
  "status": "in_progress | completed",
  
  "output": {
    "id": "sales_forecast",
    "name": "Sales Forecast",
    "function": "Sales",
    "creation_context": {
      "team": "Sales Operations",
      "process": "Sales Forecasting Process",
      "step": "Forecast Generation",
      "system": "Salesforce CRM"
    },
    "confidence": 0.85
  },
  
  "components": {
    "team_execution": {
      "rating": 2,
      "description": "Junior team, learning on the job",
      "confidence": 0.80
    },
    "system_capabilities": {
      "rating": 2,
      "description": "Basic CRM features, limited automation",
      "confidence": 0.75
    },
    "process_maturity": {
      "rating": 3,
      "description": "Standardized but manual process",
      "confidence": 0.85
    },
    "dependency_quality": {
      "rating": 3,
      "description": "Pipeline data is decent",
      "confidence": 0.60
    }
  },
  
  "assessment": {
    "actual_quality": 2,
    "required_quality": 4,
    "gap": 2,
    "bottleneck": ["team_execution", "system_capabilities"],
    "calculation": "MIN(2, 2, 3, 3) = 2"
  },
  
  "recommendations": [
    {
      "pilot_type": "AI Copilot",
      "category": "team_execution",
      "expected_impact": "2 → 4 stars",
      "timeline": "8-12 weeks",
      "cost": "€20k-€40k",
      "prerequisites": ["Team adoption", "Data access"]
    }
  ],
  
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
**Tasks:**
1. Set up Python project structure
2. Implement taxonomy data loader
   - Read JSON files from `src/data/`
   - Cache in memory
3. Set up LLM integration (OpenAI/Anthropic)
4. Create basic chat interface (Streamlit/Gradio)
5. Implement session management (in-memory)

**Deliverable:** Basic chat interface that can load taxonomies

---

### Phase 2: Discovery Engine (Week 1-2)
**Tasks:**
1. Implement output matching logic
   - Keyword extraction
   - Inference trigger matching
   - Confidence scoring
2. Implement context inference
   - Load typical_creation_context
   - Present for validation
3. Build conversation flow for Steps 1-3
4. Test with 3-5 outputs from different functions

**Deliverable:** Can identify outputs from user descriptions

---

### Phase 3: Assessment Engine (Week 2)
**Tasks:**
1. Implement component assessment prompts
2. Build LLM-based rating inference
   - Use component_scales.json indicators
   - Extract ratings from user descriptions
3. Implement validation/correction flow
4. Implement MIN calculation
5. Test with various user inputs

**Deliverable:** Can assess all 4 components and calculate actual quality

---

### Phase 4: Gap Analysis & Recommendation (Week 2-3)
**Tasks:**
1. Implement required quality collection
2. Build gap analysis logic
3. Implement bottleneck identification
4. Build pilot selection logic
   - Map bottleneck to pilot category
   - Load relevant pilot types
   - Find specific examples
5. Format recommendations
6. Test end-to-end flow

**Deliverable:** Complete Steps 1-8 working

---

### Phase 5: Polish & Demo Prep (Week 3)
**Tasks:**
1. Improve conversation flow
2. Add error handling
3. Implement session save/load (JSON files)
4. Create demo scenarios
5. Documentation
6. User testing

**Deliverable:** Demo-ready POC

---

## Testing Strategy

### Unit Tests
- Taxonomy data loading
- MIN calculation
- Gap analysis
- Pilot selection logic

### Integration Tests
- Full conversation flow (Steps 1-8)
- Multiple outputs from different functions
- Edge cases (tied bottlenecks, zero dependencies)

### Demo Scenarios
**Scenario 1: Sales Forecast (Happy Path)**
```
User: "Our sales forecasts are always wrong"
→ System identifies "Sales Forecast" output
→ Infers context: Sales Ops team, CRM system
→ Assesses components: Team ⭐⭐, System ⭐⭐, Process ⭐⭐⭐, Deps ⭐⭐⭐
→ Calculates: Actual = ⭐⭐ (MIN)
→ User sets required = ⭐⭐⭐⭐
→ Gap = 2 stars, Bottleneck = Team + System
→ Recommends: AI Copilot OR System Enhancement
```

**Scenario 2: Customer Support Tickets**
```
User: "Support tickets take forever to resolve"
→ System identifies "Resolved Support Tickets"
→ Context: Support Team, Ticketing System
→ Components: Team ⭐⭐⭐, System ⭐⭐, Process ⭐⭐, Deps ⭐⭐⭐⭐
→ Actual = ⭐⭐ (Process bottleneck)
→ Required = ⭐⭐⭐⭐
→ Recommends: Process Automation OR Process Intelligence
```

**Scenario 3: Finance Reports**
```
User: "Our financial reports are slow and error-prone"
→ System identifies "Financial Statements"
→ Context: Finance team, ERP system
→ Components: Team ⭐⭐⭐⭐, System ⭐⭐⭐, Process ⭐⭐, Deps ⭐⭐
→ Actual = ⭐⭐ (Process + Deps tied)
→ Required = ⭐⭐⭐⭐⭐
→ Recommends: Process Automation + Improve upstream data quality
```

---

## Success Criteria

### Functional Requirements
✅ Can identify outputs from natural language descriptions  
✅ Can infer creation context (Team, Process, System)  
✅ Can assess all 4 components (⭐ 1-5)  
✅ Correctly calculates MIN() for actual quality  
✅ Identifies bottleneck component(s)  
✅ Recommends appropriate pilot types  
✅ Provides 2-3 specific pilot options with details  

### User Experience Requirements
✅ Conversational flow (not form-based)  
✅ LLM generates, user validates  
✅ Minimal questions (per user_interaction_guideline.md)  
✅ Clear explanations of ratings and calculations  
✅ Simple language (no technical jargon)  

### Performance Requirements
✅ Response time < 3 seconds per message  
✅ Can complete full assessment in < 10 minutes  
✅ Works with 2-3 function templates (18 outputs)  

---

## Out of Scope (Future Work)

❌ ROI calculation (requires additional data)  
❌ Dependency graph traversal (manual for POC)  
❌ Multiple quality metrics per output (generic quality only)  
❌ Quantity assessment (quality only)  
❌ Multi-user support  
❌ Database persistence  
❌ All 22 function templates (use 2-3 for POC)  
❌ Advanced scoping (domain/system-specific factors)  
❌ Assumption tracking and testing  
❌ Project evaluation history  

---

## Technology Stack

### Backend
- **Language:** Python 3.10+
- **LLM:** Gemini via Vertex AI (streaming)
- **Data:** JSON files (no database for POC)
- **Session:** Streamlit session_state (in-memory)

### Frontend
- **Framework:** Streamlit
- **Layout:** Single chat window for POC (full architecture has 3-panel UI: chat | knowledge tree | technical log)
- **Streaming:** Display Gemini responses as they stream (async generators)
- **Session Management:** Streamlit session_state (in-memory, 3-minute timeout)
- **Authentication:** Skip for POC (full architecture uses Firebase Auth)

### Deployment
- **Development:** Local Python environment
- **Demo:** Cloud Run (containerized, scale-to-zero, session affinity)
- **Why Cloud Run:** Scale to zero ($0 when idle), no VM management, 1-5s cold start acceptable
- **Dependencies:** requirements.txt
- **Service Account:** Minimal permissions (Vertex AI user only for POC)

### Key Libraries
```
streamlit>=1.28.0           # UI framework
google-cloud-aiplatform     # Vertex AI / Gemini
python-dotenv>=1.0.0        # Environment variables
pydantic>=2.0.0             # Data validation
```

---

## Next Steps

1. **Review & Adjust:** User reviews assumptions and makes corrections
2. **Approve Spec:** Confirm technical approach
3. **Create Tasks:** Break down into detailed implementation tasks
4. **Start Development:** Begin Phase 1 (Core Infrastructure)

---

## Questions for User

Before proceeding with implementation, please confirm or adjust:

1. **LLM Choice:** OpenAI (GPT-4) or Anthropic (Claude)? Or local model?
2. **UI Framework:** Streamlit, Gradio, or custom web app?
3. **Function Scope:** Which 2-3 functions to include? (Sales, Finance, Operations recommended)
4. **Timeline:** 3-week estimate reasonable? Need faster/slower?
5. **Demo Focus:** What's the primary use case to demonstrate?
6. **Any other requirements or constraints?**
