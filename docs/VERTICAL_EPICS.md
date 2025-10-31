# Vertical Epics - AI Pilot Assessment Engine

## Epic Structure Philosophy

**Vertical = End-to-End Functional Slice**
- Each epic delivers a complete user journey across all architectural layers
- From the first epic, users can interact with a working system
- No big upfront planning - deliver one complex happy path, then iterate

**Epic 1 is implementation-ready with full specification**
**Epics 2-4 are outlined at high level for planning**

---

## Epic 1: Single-Factor Conversational Assessment with Persistence
**Status:** Implementation-Ready  
**Timeline:** 2 weeks  
**Value:** Users can discuss one organizational factor, see it inferred and stored, and understand the system's intelligence

### User Journey (Happy Path)

```
1. User visits app → Authenticates with Google
2. User types: "Our data is scattered across 5 different systems"
3. System: "Which data are you thinking about - sales, finance, operations?"
4. User: "Sales data"
5. System infers: data_quality {domain: "sales"} = 20 (confidence: 0.75)
6. System: "Is this across all sales systems, or specific tools?"
7. User: "Mainly our CRM"
8. System updates: data_quality {domain: "sales", system: "crm"} = 15 (confidence: 0.85)
9. User sees in UI:
   - Chat: Natural conversation with clarifying questions
   - Knowledge Tree: 
     └─ Data Quality
        └─ Sales Department: 20% (moderate confidence)
           └─ CRM: 15% (high confidence)
   - Technical Log: "Inferred data_quality[sales/crm]=15 (conf=0.85)"
10. User refreshes page → Data persists, conversation continues
```

### Technical Scope

**Frontend (Streamlit)**
- 3-panel layout: Chat | Knowledge Tree | Technical Log
- Firebase Auth integration (Google OAuth only)
- Session state management
- Real-time streaming display (SSE-style with special tokens)

**Backend Components**
- `ConversationOrchestrator`: Single entry point, coordinates flow
- `IntentAnalyzer`: Classify intent (for now: "assess_factor" or "general")
- `FactorInferenceEngine`: Extract factor updates with scope from conversation
- `FactorInstanceStore`: CRUD operations on scoped factor instances in Firestore
- `ScopeMatcher`: Find most applicable factor instance for given scope
- `ClarifyingQuestionGenerator`: Generate scope discovery questions
- `VertexAIClient`: Streaming LLM calls

**LLM Integration**
- Vertex AI (Gemini 1.5 Flash)
- 3 prompts:
  1. Intent classification
  2. Conversational response generation
  3. Factor inference from conversation

**Data Layer**
- Firestore schema:
  - `/users/{user_id}/factor_instances/{instance_id}` - Scoped factor instances
  - `/users/{user_id}/scope_registry/metadata` - Known domains, systems, teams
- Static knowledge graph (in-memory):
  - Single factor: `data_quality` with scale definition and scope_dimensions
  - Common domains: ["sales", "finance", "operations"]
  - Common systems by domain
  - No dependencies yet

**Deployment**
- Cloud Run with scale-to-zero
- Dockerfile with Streamlit
- Environment variables for GCP project, Vertex AI config

### Detailed Implementation Tasks

#### 1. Infrastructure Setup (2 days)
- [ ] Create GCP project, enable APIs (Vertex AI, Firestore, Cloud Run)
- [ ] Set up Firestore database with security rules
- [ ] Create service account with minimal permissions
- [ ] Set up Cloud Storage bucket for static graph (single factor)
- [ ] Configure Firebase Auth (Google OAuth)

#### 2. Static Knowledge Graph (1 day)
- [ ] Create `src/knowledge/schemas.py` with data classes
- [ ] Create `data_quality` factor definition in JSON
- [ ] Implement `KnowledgeGraph` class to load from Cloud Storage
- [ ] Write unit tests for graph loading

#### 3. Firestore Persistence (2 days)
- [ ] Implement `FactorInstanceStore` class
  - `update_factor_instance()` - Create/update scoped instance with evidence
  - `get_applicable_instance()` - Retrieve instance using scope matching
  - `get_factor_instances()` - Retrieve all instances for a factor
- [ ] Implement `ScopeMatcher` class
  - `calculate_scope_match()` - Score how well instance matches needed scope
  - `get_applicable_value()` - Find best matching instance
- [ ] Write integration tests with Firestore emulator
- [ ] Implement retry logic for transient errors

#### 4. LLM Integration (2 days)
- [ ] Implement `VertexAIClient` wrapper
  - `stream_chat()` - Streaming response generation
  - `generate()` - Non-streaming for intent/inference
- [ ] Create 3 prompt templates:
  - Intent classification prompt
  - Conversational response prompt (with factor context)
  - Factor inference prompt
- [ ] Write unit tests with mocked Vertex AI responses

#### 5. Conversation Orchestrator (2 days)
- [ ] Implement `ConversationOrchestrator.process_message()`
  - Yield technical log events as special tokens
  - Call intent analyzer
  - Build context from Firestore using scope matching
  - Stream LLM response
  - Infer factor updates with scope
  - Generate clarifying questions when scope ambiguous
  - Persist to Firestore
- [ ] Implement `IntentAnalyzer` (simple: "assess_factor" vs "general")
- [ ] Implement `FactorInferenceEngine`
  - Parse LLM output for factor updates AND scope
  - Infer scope from context (domain, system, team)
  - Calculate cumulative value from evidence for that scope
- [ ] Implement `ClarifyingQuestionGenerator`
  - Detect ambiguous scope in user statements
  - Generate "narrow from generic" questions
  - Generate "identify domain" questions
- [ ] Write integration tests

#### 6. Streamlit Frontend (3 days)
- [ ] Set up 3-panel layout with Streamlit columns
- [ ] Implement Firebase Auth flow
  - Google OAuth button
  - Token validation
  - Session state management
- [ ] Implement chat window
  - Input box
  - Message history
  - Streaming response display
- [ ] Implement knowledge tree panel
  - Display hierarchical scoped instances
  - Show generic and specific instances in tree structure
  - Show "unconfirmed" badge per instance
  - Poll Firestore for updates (every 2 seconds)
- [ ] Implement technical log panel
  - Parse special tokens from orchestrator
  - Display timestamped events
- [ ] Add loading states and error handling

#### 7. Deployment (1 day)
- [ ] Create Dockerfile
- [ ] Build and push to Google Container Registry
- [ ] Deploy to Cloud Run
- [ ] Test end-to-end with production services
- [ ] Document deployment process

#### 8. Testing & Polish (1 day)
- [ ] End-to-end user testing
- [ ] Fix bugs and edge cases
- [ ] Add helpful error messages
- [ ] Create user documentation (README)

### Acceptance Criteria

**Must Have:**
- ✅ User can authenticate with Google
- ✅ User can have natural conversation about data quality
- ✅ System asks clarifying questions to determine scope (domain, system)
- ✅ System infers `data_quality` value AND scope from conversation
- ✅ Factor instances appear in knowledge tree hierarchically (generic → specific)
- ✅ Technical log shows inference events with scope in real-time
- ✅ Data persists across page refreshes
- ✅ Evidence stored per scoped instance
- ✅ Cumulative inference: value derived from ALL evidence for that scope
- ✅ Scope matching: queries find most applicable instance

**Nice to Have:**
- ⭐ User can challenge inference: "Why do you think it's 20%?"
- ⭐ System explains reasoning from journal entries
- ⭐ Cold start shows loading message

### Out of Scope for Epic 1
- ❌ Multiple factors (only data_quality)
- ❌ Factor dependencies
- ❌ Project evaluation
- ❌ "What's next" suggestions
- ❌ Email/password auth (Google OAuth only)
- ❌ Export/import
- ❌ Multi-user collaboration
- ❌ Unknown system detection (only predefined domains/systems)
- ❌ Contradiction resolution (Pattern 4 from UX guidelines)
- ❌ Generic synthesis from multiple specifics (Pattern 5)

### Technical Debt & Future Work
- Token budget management (not needed for single factor)
- Context window optimization
- Semantic search for journal entries
- Advanced error recovery

### Success Metrics
- User can complete conversation in <2 minutes
- Factor inference accuracy: >80% (manual review of 10 conversations)
- System responds within 3 seconds (P95)
- Zero data loss on page refresh
- Cost: <$0.50 for 100 test conversations

---

## Epic 2: Multi-Factor Assessment with Dependencies
**Status:** High-Level Plan  
**Timeline:** 1.5 weeks  
**Value:** Users can explore multiple related factors, system shows dependencies

### User Journey

```
User: "Tell me about our data readiness"
System: "Let's explore that. I see we've already discussed data_quality (20%). 
         Data readiness also depends on data_availability and data_governance.
         Want to discuss those?"
User: "We have 3 years of sales data"
System: [Infers data_availability=80, shows in tree under "Data Readiness" category]
User: "What's our overall data readiness?"
System: "Based on 3 factors assessed:
         - data_quality: 20%
         - data_availability: 80%
         - data_governance: not assessed yet
         Overall: 50% mapped, 75% confident"
```

### Technical Additions
- Expand static graph: 10-15 factors with dependencies
- Factor categories (data_readiness, ai_capability, cultural_fit)
- Graph traversal for related factors
- Aggregate scoring by category
- Enhanced knowledge tree UI (hierarchical display)

### Key Tasks
- Load full factor taxonomy from JSON
- Implement graph traversal (NetworkX)
- Update inference engine to handle multiple factors
- Add category-level aggregation
- Enhance UI to show factor relationships

---

## Epic 3: Project Evaluation with Confidence Scoring
**Status:** High-Level Plan  
**Timeline:** 2 weeks  
**Value:** Users can evaluate project ideas, see feasibility confidence, understand gaps

### User Journey

```
User: "Can we do a sales forecasting project?"
System: "Let me evaluate based on what we've discussed...

**Feasibility: Proceed with caution (45% confidence)**

Why 45%?
- ✅ Data availability: 80% (you have 3 years of sales data)
- ⚠️ Data quality: 20% (data scattered, no catalog)
- ❓ ML infrastructure: Not assessed yet

For a typical forecasting project, I'd recommend 60%+ confidence.

**To improve confidence:**
1. Assess ML infrastructure (5 min) → +15% confidence
2. Discuss data governance (10 min) → +10% confidence

Want to proceed with current confidence, or explore these factors first?"
```

### Technical Additions
- AI archetype taxonomy (20+ project types)
- Project-factor mapping (which factors matter for which projects)
- Confidence calculation engine
- Gap analysis (missing factors, ROI of assessing them)
- Project evaluation persistence
- Risk-based confidence thresholds

### Key Tasks
- Create AI archetype taxonomy
- Implement project-factor relevance mapping
- Build confidence scoring algorithm
- Create gap analysis engine
- Add project evaluation to Firestore schema
- Enhance UI with project evaluation panel

---

## Epic 4: Exploratory Flow with "What's Next" Guidance
**Status:** High-Level Plan  
**Timeline:** 1.5 weeks  
**Value:** Users get intelligent suggestions, understand ROI of continuing assessment

### User Journey

```
User: "What should we discuss next?"
System: "Here's where you'd get the most value:

**Top 3 next steps:**
1. Assess ML infrastructure (5 min) → +15% confidence, unlocks 3 project types
2. Discuss team skills (5 min) → +10% confidence
3. Explore data governance (10 min) → +8% confidence

After these, you'd be at 78% confidence—good for most medium-risk projects.

Assessing the remaining 12 factors would only add another 10% confidence.
Probably not worth it unless you're planning something high-stakes.

What sounds most useful?"
```

### Technical Additions
- Pareto analysis engine (high-impact factors)
- ROI calculation (confidence gain per minute)
- Diminishing returns detection
- Capability unlocking (which project types become feasible)
- Status summary generation
- Multi-session continuity patterns

### Key Tasks
- Implement Pareto analysis for gap prioritization
- Build ROI calculation engine
- Create "what's next" suggestion generator
- Add diminishing returns signaling
- Implement status summary formatter
- Add welcome-back flow for returning users

---

## Future Epics (Vague Outline)

### Epic 5: Collaboration & Export
- Factor export to CSV/Excel
- Import with validation
- Conflict resolution for colleague input
- Shareable assessment links

### Epic 6: Advanced Context Management
- Token budget optimization
- Conversation summarization
- Semantic search for journal entries
- Cross-session context continuity

### Epic 7: Analytics & Insights
- Factor correlation analysis
- Confidence trend visualization
- Project success patterns
- Organizational benchmarking

---

## Implementation Principles

**For Epic 1 (and all epics):**
1. **Deliver working software** - No stubs, no TODOs in critical path
2. **Test as you go** - Unit tests for logic, integration tests for data flow
3. **Deploy early** - Get to Cloud Run by day 5, iterate in production
4. **Measure everything** - Log all LLM calls, track latency, monitor costs
5. **User feedback loop** - Test with real users after each epic

**Avoid:**
- ❌ Building all components before integration
- ❌ Perfect code before user feedback
- ❌ Premature optimization
- ❌ Feature creep within epic

**Embrace:**
- ✅ Ugly but working code first, refactor later
- ✅ Hardcoded prompts initially, parameterize when patterns emerge
- ✅ Manual testing first, automate when stable
- ✅ Simplest solution that works

---

## Epic 1 Detailed Specifications

### Data Schemas

#### Firestore Schema

```python
# /users/{user_id}/factor_instances/{instance_id}
{
    "instance_id": "dq_sales_crm_001",
    "factor_id": "data_quality",
    "scope": {
        "domain": "sales",
        "system": "crm",
        "team": None
    },
    "scope_label": "Sales CRM",
    "value": 15,
    "confidence": 0.85,
    "evidence": [
        {
            "statement": "Our data is scattered across 5 different systems",
            "timestamp": "2024-10-29T10:30:00Z",
            "specificity": "domain-specific",
            "conversation_id": "conv_abc123"
        },
        {
            "statement": "Mainly our CRM",
            "timestamp": "2024-10-29T10:32:00Z",
            "specificity": "system-specific",
            "conversation_id": "conv_abc123"
        }
    ],
    "refines": "dq_sales_generic_001",  # instance_id of more generic instance
    "refined_by": [],
    "synthesized_from": [],
    "discovered_in_context": "data_quality_discussion",
    "inference_status": "unconfirmed",
    "created_at": "2024-10-29T10:30:00Z",
    "updated_at": "2024-10-29T10:32:00Z"
}

# /users/{user_id}/scope_registry/metadata
{
    "domains": ["sales", "finance", "operations"],
    "systems": {
        "sales": ["crm", "spreadsheets"],
        "finance": ["erp", "accounting_software"],
        "operations": ["mes", "custom_db"]
    },
    "teams": {
        "sales": ["enterprise_sales", "smb_sales"],
        "finance": ["accounting", "fp_and_a"]
    },
    "last_updated": "2024-10-29T10:30:00Z"
}
```

#### Static Graph Schema (JSON)

```json
{
  "factors": {
    "data_quality": {
      "id": "data_quality",
      "name": "Data Quality",
      "category": "data_readiness",
      "description": "Quality, consistency, and reliability of organizational data",
      "scale": {
        "0": "No quality controls, data unreliable",
        "20": "Ad-hoc quality checks, many issues",
        "50": "Basic quality processes, some automation",
        "80": "Comprehensive quality framework, mostly automated",
        "100": "World-class data quality, continuous monitoring"
      },
      "scope_dimensions": ["domain", "system", "team"],
      "allows_generic_scope": true,
      "dependencies": [],
      "typical_assessment_time_minutes": 10
    }
  },
  "common_domains": [
    {"id": "sales", "name": "Sales"},
    {"id": "finance", "name": "Finance"},
    {"id": "operations", "name": "Operations"}
  ],
  "common_systems": {
    "sales": [{"id": "crm", "name": "CRM"}, {"id": "spreadsheets", "name": "Spreadsheets"}],
    "finance": [{"id": "erp", "name": "ERP"}, {"id": "accounting_software", "name": "Accounting Software"}],
    "operations": [{"id": "mes", "name": "MES"}, {"id": "custom_db", "name": "Custom Database"}]
  }
}
```

### LLM Prompts

#### 1. Intent Classification Prompt

```python
INTENT_CLASSIFICATION_PROMPT = """
You are an intent classifier for an AI readiness assessment system.

User message: "{user_message}"

Classify the intent as one of:
- "assess_factor": User is providing information about an organizational factor
- "general": General question or conversation

Respond with JSON:
{{
  "intent": "assess_factor" | "general",
  "confidence": 0.0-1.0
}}
"""
```

#### 2. Conversational Response Prompt

```python
CONVERSATIONAL_RESPONSE_PROMPT = """
You are a thoughtful AI readiness assessment assistant. Your role is to have natural conversations about organizational factors.

**Context:**
Factor: {factor_name}
Description: {factor_description}
Scale: {factor_scale}
Current assessment: {current_value} (confidence: {current_confidence}, status: {inference_status})

**Recent conversation:**
{conversation_history}

**User message:** {user_message}

**Guidelines:**
- Be conversational and empathetic, not interrogative
- Acknowledge what the user shared
- If relevant, reflect on implications for their organization
- Don't ask follow-up questions unless natural
- Keep responses concise (2-3 sentences)

Respond naturally:
"""
```

#### 3. Factor Inference Prompt

```python
FACTOR_INFERENCE_PROMPT = """
You are a factor inference engine. Analyze the conversation and infer factor values.

**Factor Definition:**
Factor: {factor_name}
Scale: {factor_scale}

**Conversation:**
User: {user_message}
Assistant: {assistant_response}

**Previous assessment:** {current_value} (confidence: {current_confidence})

**Task:**
Based on this conversation, infer the factor value (0-100) and confidence (0-1).

**Rules:**
- If user provided new information, update the value
- If no new information, return null
- Confidence should reflect evidence quality and consistency
- Consider cumulative evidence from previous assessment

Respond with JSON:
{{
  "factor_id": "data_quality",
  "new_value": 20 | null,
  "confidence": 0.75,
  "rationale": "User mentioned data scattered across 5 systems, indicating fragmented data management"
}}
"""
```

### Component Interfaces

#### ConversationOrchestrator

```python
class ConversationOrchestrator:
    """
    Main orchestrator for conversation flow.
    Yields special tokens for technical log + LLM response tokens.
    """
    
    def __init__(
        self,
        user_id: str,
        llm_client: VertexAIClient,
        journal_store: FactorJournalStore,
        knowledge_graph: KnowledgeGraph
    ):
        self.user_id = user_id
        self.llm_client = llm_client
        self.journal_store = journal_store
        self.knowledge_graph = knowledge_graph
        self.intent_analyzer = IntentAnalyzer(llm_client)
        self.inference_engine = FactorInferenceEngine(llm_client, knowledge_graph)
    
    async def process_message(self, user_message: str) -> AsyncIterator[str]:
        """
        Process user message and yield streaming response.
        
        Yields:
            Special tokens for technical log: "⚙️ SYSTEM: <event>"
            LLM response tokens: "<token>"
        """
        # 1. Intent classification
        yield "⚙️ SYSTEM: Analyzing intent...\n"
        intent = await self.intent_analyzer.classify(user_message)
        yield f"⚙️ SYSTEM: Intent: {intent['intent']} (conf={intent['confidence']})\n"
        
        # 2. Build context
        yield "⚙️ SYSTEM: Retrieving factor context...\n"
        context = await self._build_context(user_message)
        yield f"⚙️ SYSTEM: Retrieved factor: {context['factor']['id']}\n"
        
        # 3. Generate response
        yield "⚙️ SYSTEM: Generating response...\n"
        full_response = ""
        async for token in self._generate_response(user_message, context):
            full_response += token
            yield token
        
        # 4. Infer factor updates
        yield "\n⚙️ SYSTEM: Analyzing for factor updates...\n"
        inference = await self.inference_engine.infer_from_conversation(
            user_message=user_message,
            assistant_response=full_response,
            context=context
        )
        
        if inference and inference["new_value"] is not None:
            yield f"⚙️ SYSTEM: Inferred {inference['factor_id']}={inference['new_value']} (conf={inference['confidence']})\n"
            
            # 5. Persist to Firestore
            await self.journal_store.update_factor(
                factor_id=inference["factor_id"],
                new_value=inference["new_value"],
                rationale=inference["rationale"],
                conversation_excerpt=f"User: {user_message}\nAssistant: {full_response}",
                confidence=inference["confidence"]
            )
            yield "⚙️ SYSTEM: Factor updated in knowledge base\n"
        else:
            yield "⚙️ SYSTEM: No factor updates detected\n"
```

#### FactorJournalStore

```python
class FactorJournalStore:
    """
    Manages factor persistence in Firestore.
    """
    
    def __init__(self, user_id: str, firestore_client):
        self.user_id = user_id
        self.db = firestore_client
        self.user_ref = self.db.collection("users").document(user_id)
    
    async def update_factor(
        self,
        factor_id: str,
        new_value: int,
        rationale: str,
        conversation_excerpt: str,
        confidence: float,
        inference_status: str = "unconfirmed"
    ):
        """
        Create journal entry and update current factor state.
        """
        # Get current state
        current = await self.get_current_state(factor_id)
        previous_value = current["current_value"] if current else None
        
        # Create journal entry
        entry_ref = self.user_ref.collection("factors").document(factor_id).collection("journal").document()
        entry_data = {
            "entry_id": entry_ref.id,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "previous_value": previous_value,
            "new_value": new_value,
            "confidence": confidence,
            "change_rationale": rationale,
            "conversation_excerpt": conversation_excerpt,
            "inference_method": "llm_inference",
            "inferred_from": []
        }
        await entry_ref.set(entry_data)
        
        # Update current state
        factor_ref = self.user_ref.collection("factors").document(factor_id)
        await factor_ref.set({
            "factor_id": factor_id,
            "current_value": new_value,
            "current_confidence": confidence,
            "inference_status": inference_status,
            "last_updated": firestore.SERVER_TIMESTAMP
        }, merge=True)
    
    async def get_current_state(self, factor_id: str) -> dict | None:
        """
        Retrieve current factor state.
        """
        doc = await self.user_ref.collection("factors").document(factor_id).get()
        return doc.to_dict() if doc.exists else None
    
    async def get_journal_entries(self, factor_id: str, limit: int = 10) -> list[dict]:
        """
        Retrieve journal entries for a factor.
        """
        entries = await (
            self.user_ref
            .collection("factors")
            .document(factor_id)
            .collection("journal")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .get()
        )
        return [entry.to_dict() for entry in entries]
```

### Streamlit UI Structure

```python
# streamlit_app.py

import streamlit as st
from src.orchestration.conversation_orchestrator import ConversationOrchestrator
from src.auth.firebase_auth import authenticate_user

# Page config
st.set_page_config(
    page_title="AI Pilot Assessment Engine",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Authentication
user_id = authenticate_user()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_entries' not in st.session_state:
    st.session_state.log_entries = []

# Layout: 3 columns
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Conversation")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if user_input := st.chat_input("Tell me about your organization..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Process with orchestrator
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            orchestrator = get_orchestrator(user_id)
            for chunk in orchestrator.process_message(user_input):
                if chunk.startswith("⚙️ SYSTEM:"):
                    # Technical log entry
                    st.session_state.log_entries.append(chunk)
                else:
                    # LLM response token
                    full_response += chunk
                    response_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

with col2:
    # Knowledge Tree
    st.header("🌳 Knowledge")
    factors = get_user_factors(user_id)  # Poll Firestore
    for factor in factors:
        status_badge = "🔵" if factor["inference_status"] == "unconfirmed" else "✅"
        st.metric(
            label=f"{status_badge} {factor['name']}",
            value=f"{factor['current_value']}%",
            delta=f"{int(factor['current_confidence']*100)}% confident"
        )
    
    # Technical Log
    st.header("⚙️ Technical Log")
    log_container = st.container(height=300)
    with log_container:
        for entry in st.session_state.log_entries[-10:]:  # Last 10 entries
            st.text(entry)
```

### Testing Strategy

#### Unit Tests
```python
# tests/test_factor_inference.py

def test_inference_from_conversation():
    """Test factor inference from conversation"""
    engine = FactorInferenceEngine(mock_llm_client, mock_graph)
    
    inference = await engine.infer_from_conversation(
        user_message="Our data is scattered across 5 systems",
        assistant_response="That suggests fragmented data management...",
        context={"factor": {"id": "data_quality", ...}}
    )
    
    assert inference["factor_id"] == "data_quality"
    assert inference["new_value"] == 20
    assert inference["confidence"] > 0.7
    assert "scattered" in inference["rationale"].lower()
```

#### Integration Tests
```python
# tests/test_orchestrator_integration.py

@pytest.mark.integration
async def test_end_to_end_conversation(firestore_emulator):
    """Test full conversation flow with Firestore"""
    orchestrator = ConversationOrchestrator(
        user_id="test_user",
        llm_client=real_vertex_client,
        journal_store=FactorJournalStore("test_user", firestore_emulator),
        knowledge_graph=load_test_graph()
    )
    
    chunks = []
    async for chunk in orchestrator.process_message("Our data is scattered"):
        chunks.append(chunk)
    
    # Verify technical log events
    assert any("Intent: assess_factor" in c for c in chunks)
    assert any("Inferred data_quality=" in c for c in chunks)
    
    # Verify persistence
    state = await orchestrator.journal_store.get_current_state("data_quality")
    assert state["current_value"] == 20
    assert state["inference_status"] == "unconfirmed"
```

### Deployment Checklist

- [ ] GCP project created
- [ ] Firestore database initialized
- [ ] Firebase Auth configured
- [ ] Service account created with permissions
- [ ] Cloud Storage bucket created
- [ ] Static graph uploaded to Cloud Storage
- [ ] Dockerfile tested locally
- [ ] Container built and pushed to GCR
- [ ] Cloud Run service deployed
- [ ] Environment variables configured
- [ ] End-to-end test in production
- [ ] Cost monitoring dashboard created
- [ ] Documentation updated

---

## Next Steps After Epic 1

1. **User Testing** - Get 5 users to test Epic 1, gather feedback
2. **Measure & Learn** - Review logs, identify pain points, measure latency/cost
3. **Refine** - Fix bugs, improve prompts, optimize performance
4. **Plan Epic 2** - Based on learnings, detail out Epic 2 specifications
5. **Iterate** - Repeat cycle for each epic

**Key Principle:** Don't start Epic 2 until Epic 1 is deployed and tested with real users.
