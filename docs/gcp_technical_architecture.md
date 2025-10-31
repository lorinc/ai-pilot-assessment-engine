# GCP Technical Architecture & Process Flow

## System Overview

An exploratory AI readiness assessment engine deployed on Google Cloud Platform. The system enables conversational factor assessment through a Streamlit interface, with real-time streaming responses and technical event logging.

**Core Principle:** Factor-centric cumulative inference - every conversation builds evidence about organizational factors, enabling confident project evaluations over time.

**Design Constraints:**
- Low traffic, minimal parallel access
- Cost-sensitive (leverage GCP free tier)
- Stability and simplicity prioritized
- GCP-native services only
- Real-time streaming required (1-2 second latency acceptable)

---

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   Chat Window    │  │  Knowledge Tree  │  │  Technical Log   │  │
│  │   (Left Side)    │  │  (Upper Right)   │  │  (Lower Right)   │  │
│  │                  │  │                  │  │                  │  │
│  │  User: "Can we   │  │  📁 Factors      │  │  [12:01:32]      │  │
│  │  do forecasting?"│  │   └─ Data (60%)  │  │  Intent: eval    │  │
│  │                  │  │   └─ AI (40%)    │  │  [12:01:33]      │  │
│  │  Assistant: ...  │  │  📁 Projects     │  │  Retrieved: 3    │  │
│  │  [streaming]     │  │   └─ Forecast    │  │  factors         │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                               │                        │
                               │ Firestore              │ SSE Stream
                               │ Queries                │ (Events)
                               ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT APP (Cloud Run)                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  ConversationOrchestrator                                      │ │
│  │    ├─ Intent Classification                                    │ │
│  │    ├─ Context Retrieval                                        │ │
│  │    ├─ LLM Streaming Response                                   │ │
│  │    ├─ Factor Inference                                         │ │
│  │    └─ Event Emission (SSE)                                     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│         │              │              │              │              │
│         ▼              ▼              ▼              ▼              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Intent   │  │ Context  │  │ Factor   │  │  LLM     │             │
│  │ Analyzer │  │ Builder  │  │ Journal  │  │ Client   │             │
│  │          │  │          │  │  Store   │  │          │             │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────────────────┘
          │              │              │              │
          ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      GCP SERVICES                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Vertex AI       │  │  Firestore       │  │  Cloud Storage   │   │
│  │  (Gemini)        │  │  (User Data)     │  │  (Static Graph)  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│  ┌──────────────────┐                                               │
│  │  Firebase Auth   │                                               │
│  └──────────────────┘                                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## GCP Service Selection & Rationale

### 1. Cloud Run (Streamlit Container)
**Choice:** Cloud Run with scale-to-zero
**Rationale:**
- Free tier: 2M requests/month, 360K GB-seconds compute
- Scales to zero when idle (cost = $0)
- 1-5 second cold start acceptable (show loading message)
- Session affinity for Streamlit state
- No VM management overhead

**Configuration:**
```bash
--min-instances 0        # Scale to zero when idle
--max-instances 10       # Handle burst traffic
--memory 1Gi             # Sufficient for Streamlit + NetworkX graph
--cpu 1                  # Single CPU adequate for low traffic
--timeout 300s           # 5 min for long conversations
--session-affinity       # Keep user on same instance
```

### 2. Vertex AI (Gemini 1.5 Flash)
**Choice:** Gemini 1.5 Flash via Vertex AI
**Rationale:**
- GCP-native, no external API dependencies
- Streaming support built-in
- Cost-effective: $0.075 per 1M input tokens, $0.30 per 1M output tokens
- Free tier: $300 credit for new accounts
- Fast inference (<1 second first token)
- Large context window (1M tokens) for future context management

**Alternative considered:** Gemini 1.5 Pro (better reasoning, 4x cost) - use for complex synthesis only

### 3. Firestore (User Data Persistence)
**Choice:** Firestore Native Mode
**Rationale:**
- Free tier: 1GB storage, 50K reads/day, 20K writes/day
- Real-time listeners (for knowledge tree updates)
- Subcollection isolation (`/users/{user_id}/...`)
- No schema management
- Automatic indexing
- Scales with usage

**Data isolation:** Each user has isolated subcollection, no cross-user queries needed

### 4. Cloud Storage (Static Knowledge Graph)
**Choice:** Standard Storage bucket
**Rationale:**
- Free tier: 5GB storage, 5K Class A operations/month
- Static graph loaded once on container startup
- Versioned objects (rollback if graph update breaks)
- No query overhead (load into memory)

### 5. Firebase Authentication
**Choice:** Firebase Auth with Google OAuth + Email/Password
**Rationale:**
- Free tier: unlimited users
- Simple integration with Firestore security rules
- No user management code needed
- Session token validation built-in

---

## Data Flow & Process

### Conversation Flow (End-to-End)

```
1. USER SENDS MESSAGE
   ↓
2. STREAMLIT receives input
   ├─ Validates Firebase auth token
   ├─ Extracts user_id
   └─ Calls ConversationOrchestrator.process_message()
   ↓
3. INTENT CLASSIFICATION
   ├─ Emit SSE: "Analyzing intent..."
   ├─ Call Vertex AI (Gemini) with intent classification prompt
   ├─ Parse response: intent type, entities, relevant factors
   └─ Emit SSE: "Intent: evaluate_project, factors: [data_quality, ml_infra]"
   ↓
4. CONTEXT RETRIEVAL WITH SCOPE MATCHING
   ├─ Emit: "⚙️ SYSTEM: Retrieving factors for scope..."
   ├─ Determine needed scope from intent (e.g., {domain: "sales", system: null})
   ├─ Query Firestore: /users/{user_id}/factor_instances (filtered by factor_id)
   ├─ Apply scope matching algorithm to find most applicable instances
   ├─ Traverse static graph (in-memory) for dependencies
   ├─ Assemble context dict with token budget management
   └─ Emit: "⚙️ SYSTEM: Retrieved 3 instances: data_quality[sales]=45, data_availability[sales]=80, ml_infra=null"
   ↓
5. LLM RESPONSE GENERATION
   ├─ Emit SSE: "Generating response..."
   ├─ Build system prompt with context
   ├─ Call Vertex AI streaming API
   ├─ For each token:
   │   ├─ Yield token to Streamlit (appears in chat)
   │   └─ Accumulate for full response
   └─ Full response complete
   ↓
6. FACTOR INFERENCE
   ├─ Emit SSE: "Analyzing for factor updates..."
   ├─ Call Vertex AI with inference prompt (user msg + assistant response + context)
   ├─ Parse inferences: [{factor_id, new_value, confidence, rationale}, ...]
   └─ For each inference:
       ├─ Emit SSE: "Inferred data_quality=20 (confidence=0.75)"
       ├─ Create journal entry in Firestore
       ├─ Update factor current state in Firestore
       └─ Update aggregate metrics in Firestore
   ↓
7. UI UPDATES
   ├─ Chat window: Shows streamed response
   ├─ Technical log: Shows all SSE events
   └─ Knowledge tree: Polls Firestore, updates factor values
```

### Technical Log Streaming (SSE)

**Challenge:** LLM processing happens server-side, but user needs real-time visibility into decisions.

**Solution:** Prefix LLM response with formatted technical events, parse in UI.

**Implementation:**

```python
# Backend: ConversationOrchestrator
async def process_message(self, user_message: str) -> AsyncIterator[str]:
    # Emit technical events as special tokens
    yield "⚙️ SYSTEM: Analyzing intent...\n"
    intent = await self.intent_analyzer.classify(user_message)
    yield f"⚙️ SYSTEM: Intent classified: {intent.type}\n"
    
    yield "⚙️ SYSTEM: Retrieving factors...\n"
    context = await self.context_builder.build_context(...)
    yield f"⚙️ SYSTEM: Retrieved {len(context['factors'])} factors\n"
    
    yield "⚙️ SYSTEM: Generating response...\n"
    # Now stream actual LLM response
    async for token in self.llm_client.stream_chat(...):
        yield token
    
    yield "\n⚙️ SYSTEM: Analyzing for factor updates...\n"
    inferences = await self._infer_factor_updates(...)
    for inf in inferences:
        yield f"⚙️ SYSTEM: Inferred {inf.factor_id}={inf.new_value} (conf={inf.confidence})\n"

# Frontend: Streamlit
response_placeholder = st.empty()
log_placeholder = st.empty()

full_response = ""
log_entries = []

for chunk in orchestrator.process_message(user_input):
    if chunk.startswith("⚙️ SYSTEM:"):
        # Technical log entry
        log_entries.append(chunk)
        log_placeholder.text("\n".join(log_entries))
    else:
        # LLM response token
        full_response += chunk
        response_placeholder.markdown(full_response)
```

**Result:** Technical events appear in log window in real-time, LLM response streams to chat window.

---

## Component Details

See separate documents for detailed implementation:
- [Component Implementations](./gcp_component_implementations.md) - Detailed code for each component
- [Data Schemas](./gcp_data_schemas.md) - Firestore and data structure definitions
- [Deployment Guide](./gcp_deployment_guide.md) - Step-by-step deployment instructions

---

## Key Contracts Between Components

### 1. Streamlit ↔ ConversationOrchestrator

**Contract:** Async generator for streaming responses

```python
# Streamlit calls
async for chunk in orchestrator.process_message(user_input):
    if chunk.startswith("⚙️ SYSTEM:"):
        display_in_log(chunk)
    else:
        display_in_chat(chunk)

# Orchestrator yields
yield "⚙️ SYSTEM: <technical event>"  # Log entries
yield "<token>"                        # LLM response tokens
```

### 2. ConversationOrchestrator ↔ FactorInstanceStore

**Contract:** CRUD operations on scoped factor instances

```python
# Create/Update scoped instance
await instance_store.update_factor_instance(
    factor_id="data_quality",
    scope={"domain": "sales", "system": "salesforce_crm", "team": None},
    new_value=30,
    rationale="User mentioned Salesforce data is incomplete",
    conversation_excerpt="User: ...\nAssistant: ...",
    confidence=0.80,
    refines="dq_sales_generic_001",
    specificity="system-specific"
)

# Read using scope matching
instance = await instance_store.get_applicable_instance(
    factor_id="data_quality",
    needed_scope={"domain": "sales", "system": "salesforce_crm"}
)
# Returns: {instance, match_score, match_type}

# Read all instances for a factor
instances = await instance_store.get_factor_instances("data_quality")
# Returns: [{instance_id, scope, value, confidence, evidence, ...}, ...]

# Read aggregate summary
summary = await instance_store.get_assessment_summary()
# Returns: {categories: {...}, overall: {...}, capabilities: {...}}
```

### 3. ContextBuilder ↔ KnowledgeGraph & ScopeMatcher

**Contract:** Graph traversal and scope matching operations

```python
# Get dependencies
deps = graph.get_dependencies("data_quality")
# Returns: ["data_governance", "data_infrastructure"]

# Get factor metadata
scale = graph.get_factor_scale("data_quality")
# Returns: {"0": "No quality controls", "50": "Basic checks", ...}

scope_dims = graph.get_factor_scope_dimensions("data_quality")
# Returns: ["domain", "system", "team"]

category = graph.get_factor_category("data_quality")
# Returns: "data_readiness"

# Scope matching
match = scope_matcher.calculate_scope_match(
    instance_scope={"domain": "sales", "system": "salesforce_crm"},
    needed_scope={"domain": "sales", "system": None}
)
# Returns: 0.86 (domain match, system is more specific)

# Get enabled archetypes
archetypes = graph.get_enabled_archetypes(["data_quality", "data_availability"])
# Returns: ["basic_forecasting", "simple_automation"]
```

### 4. ConversationOrchestrator ↔ Vertex AI Client

**Contract:** Streaming LLM inference

```python
# Streaming chat
async for token in llm_client.stream_chat(
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ],
    model="gemini-1.5-flash",
    temperature=0.7
):
    yield token

# Non-streaming generation (for intent/inference)
response = await llm_client.generate(
    prompt=intent_classification_prompt,
    model="gemini-1.5-flash",
    temperature=0.3,
    response_format="json"
)
```

---

## Authentication & Authorization

### Firebase Auth Integration

**User Flow:**
1. User visits Streamlit app (Cloud Run URL)
2. If not authenticated, redirect to Firebase Auth UI
3. User signs in with Google OAuth or Email/Password
4. Firebase returns ID token
5. Streamlit validates token, extracts `user_id`
6. All Firestore operations scoped to `/users/{user_id}/...`

**Security Rules (Firestore):**

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Specific rules for factor_instances collection
    match /users/{userId}/factor_instances/{instanceId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId
                   && request.resource.data.keys().hasAll(['factor_id', 'scope', 'value', 'confidence']);
    }
    
    // Scope registry access
    match /users/{userId}/scope_registry/metadata {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

**Streamlit Implementation:**

```python
import streamlit as st
from firebase_admin import auth, credentials, initialize_app

# Initialize Firebase Admin SDK
cred = credentials.ApplicationDefault()
initialize_app(cred)

def authenticate_user():
    """
    Handle Firebase authentication in Streamlit.
    """
    if 'user_id' not in st.session_state:
        # Show login UI
        st.title("AI Pilot Assessment Engine")
        st.write("Please sign in to continue")
        
        # Firebase Auth UI (using Streamlit components)
        id_token = st.text_input("Enter your Firebase ID token", type="password")
        
        if st.button("Sign In"):
            try:
                # Verify token
                decoded_token = auth.verify_id_token(id_token)
                st.session_state.user_id = decoded_token['uid']
                st.session_state.user_email = decoded_token.get('email')
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
        
        st.stop()  # Don't render rest of app
    
    return st.session_state.user_id
```

**Note:** For production, use Streamlit custom component for Firebase Auth UI (better UX than manual token entry).

---

## Knowledge Graph Architecture

### Hybrid Model: Static Domain + Dynamic User Data

**Static Part (Cloud Storage):**
- Factor definitions (50+ factors)
- AI archetypes (20+ project types)
- Graph edges (dependencies, prerequisites)
- Factor scales (0-100 definitions)
- **Shared across all users**
- Loaded into memory on container startup
- NetworkX DiGraph

**Dynamic Part (Firestore):**
- User-specific factor values
- Journal entries (evidence trail)
- Project evaluations
- **Per-user subcollections**
- Queried on-demand

**Lookup Pattern with Scope Matching:**

```python
# Example: "Why is my Salesforce data quality score 30?"

# 1. Find factor in static graph (in-memory, instant)
factor_node = graph.nodes["data_quality"]
scale = factor_node["scale"]
category = factor_node["category"]
scope_dims = factor_node["scope_dimensions"]

# 2. Determine needed scope
needed_scope = {"domain": "sales", "system": "salesforce_crm", "team": None}

# 3. Retrieve applicable instance using scope matching
instance = await instance_store.get_applicable_instance(
    factor_id="data_quality",
    needed_scope=needed_scope
)
# Returns: {instance, match_score: 1.0, match_type: "exact"}
# instance = {value: 30, confidence: 0.80, scope: {domain: "sales", system: "salesforce_crm"}}

# 4. Get evidence for this instance
evidence = instance["evidence"]
# Returns: [{statement, timestamp, specificity, conversation_id}, ...]

# 5. Traverse static graph for dependencies (in-memory)
dependencies = graph.get_dependencies("data_quality")
# Returns: ["data_governance", "data_infrastructure"]

# 6. Fetch dependent factor instances with same scope
for dep_id in dependencies:
    dep_instance = await instance_store.get_applicable_instance(dep_id, needed_scope)
    # Use in context

# 7. Assemble context for LLM
context = {
    "factor": {
        "id": "data_quality",
        "name": factor_node["name"],
        "scale": scale,
        "scope": needed_scope,
        "scope_label": instance["scope_label"],
        "value": instance["value"],
        "confidence": instance["confidence"],
        "evidence": evidence,
        "match_type": "exact"
    },
    "dependencies": {...}
}
```

**Performance:**
- Static graph lookup: <1ms (in-memory)
- Firestore read (factor_instances): 10-50ms (indexed queries)
- Scope matching calculation: <1ms (in-memory algorithm)
- Total context assembly: <100ms for typical query (including scope matching)

---

## Context Management (TBD)

**Current Status:** Not yet implemented. Placeholder for future optimization.

**Future Considerations:**
- Token budget management (summarize old journal entries)
- Semantic relevance filtering (embed entries, retrieve top-k)
- Temporal windowing (prioritize recent conversations)
- Cross-session context continuity

**Impact on UX:** Minor. System will notify user when context window is approaching limits and suggest archiving old conversations.

---

## Cost Estimation

### Monthly Cost (Low Traffic Scenario)

**Assumptions:**
- 10 active users
- 50 conversations/user/month = 500 total conversations
- 20 messages/conversation = 10,000 messages/month
- 500 tokens/message average (input + output)
- Container runs 10 hours/month (cold start + active time)

**GCP Services:**

| Service | Usage | Free Tier | Billable | Cost |
|---------|-------|-----------|----------|------|
| Cloud Run | 10 hours × 1 CPU × 1GB | 360K GB-seconds/month | 0 | $0 |
| Vertex AI (Gemini Flash) | 10K msgs × 500 tokens = 5M tokens | $300 credit | 5M tokens | ~$1.50 |
| Firestore | 10K writes, 30K reads, 1GB storage | 20K writes, 50K reads, 1GB | 0 | $0 |
| Cloud Storage | 100MB static graph, 1K reads | 5GB, 5K reads | 0 | $0 |
| Firebase Auth | 10 users | Unlimited | 0 | $0 |

**Total: ~$1.50/month** (within free tier for first year with $300 credit)

### Scaling Costs

**100 users (10x traffic):**
- Cloud Run: Still within free tier
- Vertex AI: ~$15/month
- Firestore: ~$5/month (exceeds free tier)
- **Total: ~$20/month**

**1,000 users (100x traffic):**
- Cloud Run: ~$10/month
- Vertex AI: ~$150/month
- Firestore: ~$50/month
- **Total: ~$210/month**

---

## Deployment Architecture

### Cloud Run Configuration

```yaml
# cloud-run-config.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: assessment-engine
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/sessionAffinity: "true"
    spec:
      containerConcurrency: 10  # Max concurrent requests per container
      timeoutSeconds: 300
      containers:
      - image: gcr.io/PROJECT_ID/assessment-engine:latest
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "PROJECT_ID"
        - name: FIRESTORE_DATABASE
          value: "(default)"
        - name: VERTEX_AI_LOCATION
          value: "us-central1"
        - name: VERTEX_AI_MODEL
          value: "gemini-1.5-flash"
        - name: SESSION_TIMEOUT_MINUTES
          value: "3"
```

### Container Structure

```
/app/
  streamlit_app.py              # Main entry point
  requirements.txt
  .streamlit/
    config.toml                 # Streamlit config
  src/
    orchestration/
      conversation_orchestrator.py
    persistence/
      factor_journal_store.py
    context/
      context_builder.py
    knowledge/
      knowledge_graph.py
    llm/
      vertex_ai_client.py
    auth/
      firebase_auth.py
  static-graph/                 # Downloaded from Cloud Storage on startup
    factors.json
    archetypes.json
    edges.json
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download static graph from Cloud Storage on build (optional, can also do at runtime)
# RUN gsutil cp -r gs://PROJECT_ID-static-knowledge/* ./static-graph/

# Expose Streamlit port
EXPOSE 8080

# Set Streamlit config
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080"]
```

---

## Error Handling & Resilience

### Cold Start Handling

**Problem:** First request after idle period takes 3-5 seconds (container startup + graph loading).

**Solution:**

```python
# streamlit_app.py
if 'initialized' not in st.session_state:
    with st.spinner("🔄 Initializing assessment engine... (first load may take 3-5 seconds)"):
        # Load static graph from Cloud Storage
        graph = KnowledgeGraph()
        graph.load_from_storage()
        st.session_state.graph = graph
        st.session_state.initialized = True
```

### Firestore Retry Logic

```python
from google.api_core import retry

@retry.Retry(predicate=retry.if_transient_error, deadline=30.0)
async def get_current_state(self, factor_id: str) -> dict:
    """
    Retrieve factor state with automatic retry on transient errors.
    """
    doc = await self.user_ref.collection("factors").document(factor_id).get()
    return doc.to_dict() if doc.exists else None
```

### LLM Timeout Handling

```python
try:
    async with asyncio.timeout(60):  # 60 second timeout
        async for token in llm_client.stream_chat(...):
            yield token
except asyncio.TimeoutError:
    yield "\n\n⚠️ Response generation timed out. Please try again."
    log_error("LLM timeout", user_id=self.user_id)
```

### Session Timeout

```python
# Streamlit config
# .streamlit/config.toml
[server]
maxUploadSize = 10
sessionTimeout = 180  # 3 minutes

# Cleanup on timeout
def on_session_timeout():
    # No persistent state to clean up (everything in Firestore)
    # Just log event
    logger.info(f"Session timeout for user {user_id}")
```

---

## Security Considerations

### 1. User Data Isolation
- Firestore security rules enforce user-level isolation
- No cross-user queries possible
- Each user's data in separate subcollection: `/users/{user_id}/...`

### 2. Authentication
- Firebase Auth handles all authentication
- ID tokens validated on every request
- Tokens expire after 1 hour (automatic refresh)

### 3. API Keys
- Vertex AI uses Application Default Credentials (no API keys in code)
- Cloud Run service account has minimal permissions:
  - `roles/aiplatform.user` (Vertex AI)
  - `roles/datastore.user` (Firestore)
  - `roles/storage.objectViewer` (Cloud Storage, static graph only)

### 4. Input Validation
- All user input sanitized before LLM prompts
- No SQL/NoSQL injection risk (Firestore SDK handles escaping)
- Rate limiting via Cloud Run concurrency limits

### 5. Data Privacy
- No PII stored except email (from Firebase Auth)
- All conversation data encrypted at rest (Firestore default)
- No data shared across users
- Export functionality allows user to download all their data

---

## Monitoring & Observability

### Cloud Logging

```python
import google.cloud.logging

logging_client = google.cloud.logging.Client()
logger = logging_client.logger("assessment-engine")

# Log structured events
logger.log_struct({
    "event": "factor_updated",
    "user_id": user_id,
    "factor_id": "data_quality",
    "new_value": 20,
    "confidence": 0.75,
    "timestamp": datetime.now().isoformat()
}, severity="INFO")
```

### Key Metrics to Track

- **Conversation metrics:**
  - Messages per conversation
  - Conversation duration
  - Factors assessed per conversation

- **Performance metrics:**
  - LLM response time (first token, full response)
  - Firestore query latency
  - Cold start frequency

- **Cost metrics:**
  - Vertex AI token usage
  - Firestore read/write operations
  - Cloud Run instance hours

### Cloud Monitoring Dashboards

Create dashboards for:
1. **User Activity:** Active users, conversations/day, messages/day
2. **Performance:** P50/P95/P99 latency, error rate
3. **Cost:** Daily spend by service
4. **System Health:** Container restarts, cold starts, timeout rate

---

## Future Enhancements

### 1. Context Management (TBD)
- Implement token budget optimization
- Add semantic search for journal entries
- Summarize old conversations

### 2. Multi-Language Support
- Detect user language
- Translate factor names/descriptions
- Maintain English factor IDs for consistency

### 3. Collaboration Features
- Export factors to CSV
- Import colleague assessments
- Conflict resolution UI

### 4. Advanced Analytics
- Factor correlation analysis
- Confidence trend visualization
- Project success prediction

### 5. Mobile Optimization
- Responsive UI for mobile browsers
- Progressive Web App (PWA)
- Offline mode (cached graph)

---

## Appendix: Technology Stack Summary

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
| **Logging** | Cloud Logging | Structured logs |
| **Monitoring** | Cloud Monitoring | Metrics and dashboards |

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-29  
**Status:** Architecture design complete, implementation pending
