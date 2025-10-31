# Architecture Summary

## System Overview

The AI Pilot Assessment Engine is a **factor-centric conversational assessment system** that helps organizations evaluate their AI readiness through natural dialogue. The system accumulates evidence over time, building confidence in organizational factor assessments, which enables informed project feasibility evaluations.

---

## Core Architecture Principles

### 1. Factor-Centric Design with Scoped Instances
**Everything links to factors.** The system doesn't track arbitrary conversations—it extracts evidence about specific organizational factors (data_quality, ml_infrastructure, team_skills, etc.) and maintains a cumulative journal for each.

**Key insight:** Factors can have multiple scoped instances (e.g., data_quality for "sales/Salesforce CRM" vs "finance/SAP ERP"). This enables domain/system-specific assessments while maintaining organizational truth across projects.

**Scoped Factor Model:** Each factor instance has a scope defined by domain, system, and team dimensions. The system intelligently matches the most specific applicable instance for any query, falling back to generic assessments when specific ones don't exist.

### 2. Hybrid Knowledge Model
- **Static domain knowledge** (factors, archetypes, scales) → Cloud Storage, loaded into memory (NetworkX graph)
- **Dynamic user data** (factor values, journal entries) → Firestore, queried on-demand
- **Lookup pattern:** Static graph provides structure, Firestore provides user-specific values

### 3. Cumulative Inference with Scope Matching
Factor values are **synthesized from ALL evidence for that scope**, not single mentions. Confidence increases with consistent evidence. The system uses intelligent scope matching to find the most applicable assessment:
- **Exact match:** Query for "sales/Salesforce" finds exact instance (confidence: 1.0)
- **Generic fallback:** Query for "sales/data_warehouse" falls back to "sales/all systems" (confidence: 0.86)
- **No match:** Query for "manufacturing" returns None if not assessed

LLM re-synthesizes on demand for "why?" questions, considering scope hierarchy.

### 4. Real-Time Streaming
- **LLM responses:** Stream tokens as generated (Vertex AI streaming API)
- **Technical events:** Prefixed to LLM response as `⚙️ SYSTEM:` markers, parsed in UI
- **Knowledge tree:** Polls Firestore for factor updates (1-2 second latency acceptable)

---

## System Components & Responsibilities

### Frontend (Streamlit on Cloud Run)
**Responsibilities:**
- Three-panel UI (chat | knowledge tree | technical log)
- Firebase authentication
- Stream LLM responses to chat window
- Parse SSE events to technical log window
- Query Firestore for knowledge tree rendering
- Session state management (in-memory, 3-minute timeout)

**Key files:**
- `streamlit_app.py` - Main entry point
- `components/chat_panel.py` - Chat interface
- `components/knowledge_tree.py` - Factor browser
- `components/technical_log.py` - Event display

### ConversationOrchestrator (Backend Logic)
**Responsibilities:**
- Receive user input
- Classify intent (LLM call)
- Retrieve context (Firestore + graph traversal)
- Generate streaming response (LLM streaming)
- Infer factor updates (LLM call)
- Persist updates (Firestore writes)
- Emit technical events (SSE format)

**Key methods:**
- `process_message()` - Main entry point, async generator
- `_infer_factor_updates()` - Extract factor changes from conversation
- `_build_system_prompt()` - Assemble context for LLM

### FactorJournalStore (Persistence Layer)
**Responsibilities:**
- CRUD operations on user factors
- Journal entry creation
- Aggregate metrics calculation
- Cumulative synthesis (LLM-based)
- Factor confirmation/validation

**Key methods:**
- `update_factor()` - Create journal entry, update current state
- `get_current_state()` - Retrieve factor value
- `get_journal_entries()` - Retrieve evidence trail
- `recalculate_factor_from_journal()` - LLM synthesis of all evidence
- `get_assessment_summary()` - Aggregate metrics for status queries

### ContextBuilder (Context Assembly)
**Responsibilities:**
- Assemble context for LLM prompts
- Fetch factor states from Firestore
- Traverse graph for dependencies
- Manage token budget (prioritize recent/relevant)

**Key methods:**
- `build_context()` - Main assembly with token budget
- `_estimate_tokens()` - Token counting
- `_summarize_history()` - Compress old entries

### KnowledgeGraph (Static Domain Model)
**Responsibilities:**
- Load static graph from Cloud Storage
- Provide graph traversal operations
- Factor metadata (scales, categories)
- AI archetype prerequisites

**Key methods:**
- `get_dependencies()` - Factors this factor depends on
- `get_dependents()` - Factors that depend on this factor
- `get_factor_scale()` - 0-100 scale definition
- `get_enabled_archetypes()` - Projects user can evaluate

### VertexAIClient (LLM Interface)
**Responsibilities:**
- Streaming chat generation
- Non-streaming generation (intent, inference)
- Token counting
- Error handling and retries

**Key methods:**
- `stream_chat()` - Async generator for streaming
- `generate()` - Non-streaming generation
- `count_tokens()` - Estimate token usage

---

## Data Flow: End-to-End Example

**User asks:** "Can we do sales forecasting?"

```
1. USER INPUT
   ↓
2. STREAMLIT
   - Validate auth token → user_id
   - Call orchestrator.process_message("Can we do sales forecasting?")
   ↓
3. INTENT CLASSIFICATION
   - Emit: "⚙️ SYSTEM: Analyzing intent..."
   - LLM call: classify_intent()
   - Result: {type: "evaluate_project", entities: {project: "sales_forecasting"}, 
             relevant_factors: ["data_quality", "data_availability", "ml_infrastructure"],
             scope: {domain: "sales", system: null}}
   - Emit: "⚙️ SYSTEM: Intent: evaluate_project (scope: sales)"
   ↓
4. CONTEXT RETRIEVAL WITH SCOPE MATCHING
   - Emit: "⚙️ SYSTEM: Retrieving factors for sales domain..."
   - Scope matching query: data_quality for {domain: "sales", system: null}
     • Found: {domain: "sales", system: "salesforce_crm"} = 30 (match_score: 0.86)
     • Found: {domain: "sales", system: null} = 45 (match_score: 1.0) ← Best match
   - Scope matching query: data_availability for {domain: "sales", system: null}
     • Found: {domain: "sales", system: null} = 80 (match_score: 1.0)
   - Scope matching query: ml_infrastructure for {domain: "sales", system: null}
     • No match found → null
   - Graph traversal: get_dependencies("data_quality") → ["data_governance", "data_infrastructure"]
   - Emit: "⚙️ SYSTEM: Retrieved 3 factor instances: data_quality[sales]=45, data_availability[sales]=80, ml_infrastructure=null"
   ↓
5. LLM RESPONSE GENERATION
   - Emit: "⚙️ SYSTEM: Generating response..."
   - Build system prompt with context
   - Vertex AI streaming call
   - Yield tokens: "Based", " on", " what", " we've", " discussed", ":", "\n\n", "**Feasibility", ...
   - Streamlit displays tokens in chat window as they arrive
   ↓
6. FACTOR INFERENCE
   - Emit: "⚙️ SYSTEM: Analyzing for factor updates..."
   - LLM call: infer_factor_updates(user_msg, assistant_response, context)
   - Result: [] (no new factor information in this exchange)
   - Emit: "⚙️ SYSTEM: No factor updates detected"
   ↓
7. UI UPDATES
   - Chat window: Shows full LLM response
   - Technical log: Shows all "⚙️ SYSTEM:" events
   - Knowledge tree: Polls Firestore, no changes
```

**Result:** User sees:
- **Chat:** "Based on what we've discussed: **Feasibility: Proceed with caution (45% confidence)** ..."
- **Log:** 
  ```
  [12:01:32] Analyzing intent...
  [12:01:33] Intent: evaluate_project
  [12:01:34] Retrieving factors...
  [12:01:35] Retrieved 3 factors: data_quality(20), data_availability(80), ml_infrastructure(null)
  [12:01:36] Generating response...
  [12:01:42] Analyzing for factor updates...
  [12:01:43] No factor updates detected
  ```
- **Knowledge Tree:** 
  ```
  📁 Factors
    └─ Data Readiness (60%)
        ├─ 📊 data_quality
        │   ├─ 💼 Sales Department: 45% ⚠️ (moderate confidence)
        │   │   └─ 🔧 Salesforce CRM: 30% ⚠️ (high confidence)
        │   └─ 💰 Finance: Not assessed
        └─ 📊 data_availability
            └─ 💼 Sales Department: 80% ✓ (high confidence)
    └─ AI Capability (40%)
        └─ ml_infrastructure: Not assessed
  📁 Projects
    └─ (none yet)
  ```

---

## Key Technical Decisions

### 1. Why Cloud Run (not Compute Engine)?
- **Scale to zero** when idle → $0 cost for low traffic
- **Session affinity** keeps user on same instance (Streamlit state preserved)
- **1-5 second cold start** acceptable (show loading message)
- **No VM management** overhead

### 2. Why Gemini 1.5 Flash (not Pro)?
- **4x cheaper** than Pro ($0.075 vs $0.30 per 1M output tokens)
- **Fast inference** (<1 second first token)
- **Sufficient quality** for intent classification and factor inference
- **Use Pro only for complex synthesis** (future optimization)

### 3. Why Firestore (not Cloud SQL)?
- **Free tier** covers low traffic (50K reads/day, 20K writes/day)
- **No schema management** (flexible for evolving data model)
- **Real-time listeners** (future: live knowledge tree updates)
- **Automatic indexing** (no query optimization needed)
- **Subcollection isolation** (clean user data separation)

### 4. Why NetworkX in-memory (not graph database)?
- **Static graph** doesn't change per-user
- **Fast traversal** (<1ms for typical queries)
- **No query overhead** (no network calls)
- **Simple deployment** (no separate graph service)
- **Cost: $0** (loaded from Cloud Storage once)

### 5. Why SSE via prefixed tokens (not WebSocket)?
- **Simpler implementation** (no separate WebSocket server)
- **Works with Streamlit** async generators
- **1-2 second latency acceptable** (not real-time trading)
- **No connection management** overhead
- **Fallback to polling** if SSE fails

---

## Data Isolation & Security

### User Data Isolation
- Each user has isolated Firestore subcollection: `/users/{user_id}/...`
- No cross-user queries possible
- Firestore security rules enforce user-level access

### Authentication Flow
1. User visits Streamlit app
2. Firebase Auth UI (Google OAuth or Email/Password)
3. Firebase returns ID token
4. Streamlit validates token → extracts `user_id`
5. All operations scoped to `user_id`

### Security Rules (Firestore)
```javascript
match /users/{userId}/{document=**} {
  allow read, write: if request.auth != null && request.auth.uid == userId;
}
```

### API Security
- Vertex AI uses Application Default Credentials (no API keys in code)
- Cloud Run service account has minimal permissions:
  - `roles/aiplatform.user` (Vertex AI)
  - `roles/datastore.user` (Firestore)
  - `roles/storage.objectViewer` (Cloud Storage, static graph only)

---

## Cost Estimation

### Low Traffic (10 users, 500 conversations/month)
- **Cloud Run:** $0 (within free tier)
- **Vertex AI:** ~$1.50 (5M tokens)
- **Firestore:** $0 (within free tier)
- **Cloud Storage:** $0 (within free tier)
- **Total: ~$1.50/month**

### Medium Traffic (100 users, 5,000 conversations/month)
- **Cloud Run:** $0 (within free tier)
- **Vertex AI:** ~$15 (50M tokens)
- **Firestore:** ~$5 (exceeds free tier)
- **Total: ~$20/month**

### High Traffic (1,000 users, 50,000 conversations/month)
- **Cloud Run:** ~$10
- **Vertex AI:** ~$150
- **Firestore:** ~$50
- **Total: ~$210/month**

---

## Deployment Overview

### Prerequisites
1. GCP project with billing enabled
2. Enable APIs: Cloud Run, Vertex AI, Firestore, Cloud Storage
3. Create Firebase project (linked to GCP project)
4. Upload static graph to Cloud Storage bucket

### Deployment Steps
1. Build Docker image: `docker build -t gcr.io/{project}/assessment-engine .`
2. Push to GCR: `docker push gcr.io/{project}/assessment-engine`
3. Deploy to Cloud Run: `gcloud run deploy assessment-engine --image gcr.io/{project}/assessment-engine`
4. Configure Firestore security rules
5. Set up Firebase Auth (Google OAuth + Email/Password)
6. Test authentication and first conversation

### Environment Variables
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
FIRESTORE_DATABASE=(default)
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-flash
SESSION_TIMEOUT_MINUTES=3
```

---

## Future Enhancements (TBD)

### 1. Context Management
**Problem:** LLM context window fills up with long conversations.

**Solutions (TBD):**
- Summarize old journal entries (keep recent full)
- Semantic search for relevant entries only
- Temporal windowing (archive old conversations)

**Impact:** Minor UX change (notify user when context approaching limit)

### 2. Collaboration Features
- Export factors to CSV
- Import colleague assessments
- Conflict resolution UI
- Shared organizational context

### 3. Advanced Analytics
- Factor correlation analysis
- Confidence trend visualization
- Project success prediction
- ROI tracking

### 4. Mobile Optimization
- Responsive UI for mobile browsers
- Progressive Web App (PWA)
- Offline mode (cached graph)

---

## Key Contracts Summary

### Streamlit ↔ Orchestrator
```python
async for chunk in orchestrator.process_message(user_input):
    if chunk.startswith("⚙️ SYSTEM:"):
        display_in_log(chunk)
    else:
        display_in_chat(chunk)
```

### Orchestrator ↔ FactorInstanceStore
```python
await instance_store.update_factor_instance(
    factor_id="data_quality",
    scope={"domain": "sales", "system": "salesforce_crm", "team": None},
    new_value=30,
    rationale="User mentioned Salesforce data is incomplete",
    conversation_excerpt="User: ...\nAssistant: ...",
    confidence=0.80,
    refines="dq_sales_generic_001"  # Links to generic sales instance
)
```

### ContextBuilder ↔ Graph & ScopeMatcher
```python
# Get factor metadata from graph
deps = graph.get_dependencies("data_quality")
scale = graph.get_factor_scale("data_quality")

# Get applicable instance using scope matching
instance = scope_matcher.get_applicable_value(
    factor_id="data_quality",
    needed_scope={"domain": "sales", "system": "salesforce_crm"}
)
# Returns: (instance, match_score) or None

archetypes = graph.get_enabled_archetypes(["data_quality", "data_availability"])
```

### Orchestrator ↔ LLM
```python
async for token in llm_client.stream_chat(messages=[...]):
    yield token
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Streamlit | UI framework |
| **Backend** | Python 3.11 | Application logic |
| **LLM** | Vertex AI (Gemini 1.5 Flash) | Intent, inference, generation |
| **Persistence** | Firestore | User data, factors, journal |
| **Static Data** | Cloud Storage | Knowledge graph |
| **Auth** | Firebase Auth | User authentication |
| **Hosting** | Cloud Run | Serverless container |
| **Graph** | NetworkX | In-memory graph traversal |
| **Streaming** | Async generators | Real-time response streaming |

---

## Documentation Index

1. **[README.md](../README.md)** - System vision and features
2. **[gcp_technical_architecture.md](./gcp_technical_architecture.md)** - Detailed architecture and process flows
3. **[gcp_data_schemas.md](./gcp_data_schemas.md)** - Firestore schema and data structures
4. **[conversation_memory_architecture.md](./conversation_memory_architecture.md)** - Factor journal design
5. **[exploratory_assessment_architecture.md](./exploratory_assessment_architecture.md)** - Assessment flow patterns
6. **[user_interaction_guideline.md](./user_interaction_guideline.md)** - Conversational UX patterns
7. **[architecture_summary.md](./architecture_summary.md)** - This document

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-29  
**Status:** Architecture design complete, ready for implementation
