# Remaining Epics - High-Level Overview

This document outlines the remaining vertical epics after Epic 01 (Knowledge Graph Foundation). Each epic cuts through all architecture layers and delivers an independently testable feature.

---

## Epic 02: Test Data Preparation Pipeline
**Goal:** Automate creation and validation of mock knowledge base for development and testing.

### Key Deliverables
- JSON schema validation with Pydantic models
- Data generation scripts for archetypes, pains, prerequisites, maturity levels
- Realistic business scenarios (3-5 domains: Manufacturing, Healthcare, Retail, Finance)
- Data versioning and migration tools
- Validation suite ensuring graph consistency

### Architecture Layers
- **Data Layer:** JSON generators, schema validators
- **Knowledge Layer:** Graph validation rules
- **Testing:** Fixtures and test data loaders

### Assumptions
- Epic 01 defines the JSON schema structure
- We need 10-15 archetypes, 15-20 pain points, 20-30 prerequisites minimum
- Data should cover different maturity levels (Exploring → Operationalized)
- Relationships must be bidirectionally consistent

### Success Criteria
- Command to generate fresh test dataset: `python scripts/generate_test_data.py`
- Validation script catches schema violations and orphaned relationships
- Multiple dataset profiles (minimal, standard, comprehensive)

---

## Epic 03: LangChain Agent with ReAct Pattern
**Goal:** Implement multi-tool LangChain agent using ReAct (Reason+Act) pattern for iterative problem-solving.

### Key Deliverables
- ReAct agent configuration with Gemini
- Multiple tools: knowledge retrieval, graph query, calculation (if needed)
- Agent memory for conversation context
- Verbose logging of thought → action → observation cycles
- CLI interface for agent interaction

### Architecture Layers
- **Orchestration Layer:** LangChain ReAct agent setup
- **LLM Layer:** Gemini with function calling
- **Tool Layer:** Structured tool definitions
- **Interface Layer:** CLI with agent trace display

### Assumptions
- Epic 01 provides the knowledge retrieval tool
- Agent needs to decide when to query graph vs vector store
- No UI yet - focus on agent logic correctness
- Single-turn conversations (no session persistence)

### Success Criteria
- Agent can answer: "What AI solutions help with inventory management?"
- Agent trace shows: Thought → Tool call → Observation → Answer
- Agent uses multiple tools in sequence when needed
- Handles ambiguous queries by asking clarifying questions (via tool)

---

## Epic 04: Multi-Stage Conversation Flow
**Goal:** Implement the 4-stage reasoning pipeline: Intent Capture → Retrieval → Reasoning → Report Generation.

### Key Deliverables
- Stage 1: Intent extraction (function, pain, maturity)
- Stage 2: Grounded retrieval (hybrid KG + RAG)
- Stage 3: Solution synthesis with ReAct reasoning
- Stage 4: Formatted report generation
- Stage orchestrator managing transitions
- Structured outputs at each stage

### Architecture Layers
- **Orchestration Layer:** Stage manager, transition logic
- **LLM Layer:** Stage-specific prompts
- **Knowledge Layer:** Stage 2 retrieval
- **Interface Layer:** Stage progress display

### Assumptions
- Epic 03 provides the ReAct agent foundation
- Each stage has explicit input/output contracts
- Stages can be tested independently
- User can provide partial context (e.g., maturity unknown)

### Success Criteria
- Given vague input: "We waste too much time on scheduling"
  - Stage 1 extracts: function=Operations, pain=Efficiency, maturity=Unknown
  - Stage 2 retrieves: Optimization archetype + prerequisites
  - Stage 3 reasons: Checks maturity constraints, proposes solution
  - Stage 4 outputs: Executive summary with next steps
- Each stage logs its decisions
- Pipeline handles missing information gracefully

---

## Epic 05: Streamlit Chat Interface
**Goal:** Build user-facing chat UI with conversation history and basic interaction patterns.

### Key Deliverables
- Streamlit app with chat interface (using `st.chat_message`)
- Session state management for conversation history
- Message rendering (user/assistant with markdown support)
- Input validation and error handling
- Clear chat functionality
- Basic configuration sidebar

### Architecture Layers
- **Interface Layer:** Streamlit UI components
- **Session Layer:** State management
- **Orchestration Layer:** Integration with multi-stage agent
- **LLM Layer:** Streaming responses (if supported)

### Assumptions
- Epic 04 provides the conversation engine
- UI follows the Gemini Streamlit boilerplate patterns
- No authentication yet - single user session
- Local deployment only at this stage

### Success Criteria
- User can type questions and receive formatted responses
- Chat history persists during session
- Assistant responses render markdown properly
- Loading states show during LLM processing
- Error messages are user-friendly

---

## Epic 06: Observability & Technical Log Panel
**Goal:** Add transparent logging of agent reasoning for debugging and trust-building.

### Key Deliverables
- Expandable log panel in Streamlit sidebar
- Structured logging of:
  - Stage transitions
  - Tool invocations with arguments
  - LLM thoughts (ReAct pattern)
  - Retrieved knowledge chunks
  - Decision points and thresholds
- Color-coded log entries (thought/action/observation/error)
- Timestamp and step numbering
- Export log functionality

### Architecture Layers
- **Interface Layer:** Log panel UI component
- **Orchestration Layer:** Logging hooks in agent
- **Observability Layer:** Log formatting and filtering

### Assumptions
- Epic 05 provides the Streamlit foundation
- LangChain callbacks capture agent traces
- Logs stored in session state (not persisted)
- Technical audience can toggle log visibility

### Success Criteria
- Log panel shows complete agent reasoning trace
- Each tool call is visible with inputs/outputs
- Thoughts are distinguishable from actions
- Errors are highlighted in red
- Log is human-readable and aids debugging

---

## Epic 07: Evaluation Metrics & Scoring
**Goal:** Implement rule-based conversation quality metrics displayed in UI.

### Key Deliverables
- Evaluation rubric implementation:
  - Ambiguity resolution (yes/no)
  - Pain → Archetype mapping correctness
  - Prerequisite surfacing
  - Maturity alignment
  - Proposal concreteness
- Scoring engine (0-100% usefulness)
- Metrics panel in Streamlit UI
- Checkmark indicators for each criterion
- Post-conversation evaluation trigger

### Architecture Layers
- **Evaluation Layer:** Scoring logic
- **Interface Layer:** Metrics display panel
- **Orchestration Layer:** Evaluation hooks

### Assumptions
- Epic 04 provides structured stage outputs for evaluation
- Metrics calculated after Stage 4 completes
- Rules are deterministic (no LLM-as-judge yet)
- Ground truth from knowledge graph for validation

### Success Criteria
- After conversation, metrics panel shows 5 criteria scores
- Overall usefulness percentage displayed
- Failed criteria are clearly indicated
- Metrics help identify agent weaknesses

---

## Epic 08: GCP Deployment & Cloud Run Setup
**Goal:** Deploy application to GCP Cloud Run with Vertex AI integration.

### Key Deliverables
- Dockerfile for containerization
- Cloud Run deployment configuration
- Vertex AI authentication setup
- Environment variable management (Secret Manager)
- Cloud Build CI/CD pipeline (optional)
- Deployment documentation

### Architecture Layers
- **Infrastructure Layer:** Docker, Cloud Run, GCP services
- **LLM Layer:** Vertex AI API integration (replace local)
- **Deployment Layer:** Configuration management

### Assumptions
- Application runs locally successfully (Epic 05+)
- GCP project exists with billing enabled
- Vertex AI API is enabled
- Free tier limits are respected

### Success Criteria
- `gcloud run deploy` successfully deploys app
- Public URL accessible and functional
- Vertex AI embeddings and Gemini work in cloud
- Environment variables configured securely
- Logs visible in Cloud Logging
- Stays within free tier limits for demo usage

---

## Epic 09: Session Persistence with Firebase
**Goal:** Enable users to save and resume conversations via Firebase Firestore.

### Key Deliverables
- Firebase Firestore integration
- Session document schema
- Save conversation summary on completion
- Load previous session by ID or email
- Shareable session links
- Session list view (optional)

### Architecture Layers
- **Persistence Layer:** Firestore client
- **Session Layer:** Session management logic
- **Interface Layer:** Save/load UI controls

### Assumptions
- Epic 08 provides cloud deployment
- Firebase project linked to GCP project
- Only summaries stored (not full logs) to save quota
- No authentication - sessions identified by UUID

### Success Criteria
- User can save session and receive shareable link
- Returning to link loads previous context
- Session includes: intent, recommendations, score
- Firestore writes stay within free tier (1 write per session)

---

## Epic 10: Intent Capture & Clarification Dialog
**Goal:** Enhance Stage 1 with interactive clarification when user input is ambiguous.

### Key Deliverables
- Ambiguity detection logic
- Clarification question generator
- Multi-turn dialog handler for Stage 1
- Confidence scoring for extracted intent
- Fallback strategies for unclear input

### Architecture Layers
- **Orchestration Layer:** Stage 1 enhancement
- **LLM Layer:** Intent extraction prompts
- **Interface Layer:** Clarification UI flow

### Assumptions
- Epic 04 provides basic Stage 1
- Some queries will be inherently ambiguous
- Agent should ask 1-2 clarifying questions max
- User may refuse to clarify (handle gracefully)

### Success Criteria
- Vague input: "We need AI" → Agent asks: "What business problem?"
- After clarification, Stage 1 completes successfully
- Evaluation metrics track ambiguity resolution
- No infinite clarification loops

---

## Epic 11: Report Generation & Formatting
**Goal:** Enhance Stage 4 to produce professional, structured reports with templates.

### Key Deliverables
- Report templates (Executive Summary, Feasibility, Impact, Next Steps)
- Markdown formatting with sections
- Dynamic content insertion from Stage 3 reasoning
- Export options (markdown, PDF via library)
- Customizable report styles

### Architecture Layers
- **Orchestration Layer:** Stage 4 enhancement
- **Template Layer:** Jinja2 or similar
- **Interface Layer:** Report display and export

### Assumptions
- Epic 04 provides basic Stage 4
- Reports should be non-technical and executive-friendly
- Templates are configurable
- PDF export is optional (nice-to-have)

### Success Criteria
- Report includes all required sections
- Tone is prescriptive and actionable
- Prerequisites listed as checklist
- Next steps are concrete (not generic)
- Report renders beautifully in Streamlit

---

## Epic 12: Advanced Graph Queries & Multi-Hop Reasoning
**Goal:** Implement complex graph traversals for sophisticated recommendations.

### Key Deliverables
- Multi-hop graph queries (e.g., pain → archetype → prerequisites → maturity constraints)
- Path finding algorithms (shortest path to solution)
- Constraint satisfaction logic (maturity + data availability)
- Graph query optimization
- Query result caching

### Architecture Layers
- **Knowledge Layer:** Advanced graph algorithms
- **Orchestration Layer:** Multi-hop reasoning in Stage 3
- **Tool Layer:** Enhanced graph query tools

### Assumptions
- Epic 01 provides basic graph queries
- Some recommendations require chaining multiple relationships
- Graph size remains manageable (<1000 nodes)
- NetworkX algorithms are sufficient (no Neo4j needed yet)

### Success Criteria
- Agent can answer: "What's the easiest AI project for a company with no data?"
  - Traverses: maturity=Exploring → low-complexity archetypes → minimal prerequisites
- Multi-hop queries complete in <1 second
- Results are ranked by feasibility

---

## Epic 13: Knowledge Base Expansion & Management
**Goal:** Tools for adding, updating, and versioning knowledge base content.

### Key Deliverables
- Admin CLI for adding new archetypes/pains/prerequisites
- JSON validation on updates
- Graph rebuild and re-indexing pipeline
- Knowledge base versioning (git-based or timestamps)
- Conflict detection (duplicate IDs, broken relationships)

### Architecture Layers
- **Data Layer:** CRUD operations on JSON
- **Knowledge Layer:** Incremental graph updates
- **Admin Layer:** Management CLI

### Assumptions
- Knowledge base will grow over time
- Multiple contributors may edit JSON
- Graph should support hot-reloading (no full restart)
- Version control prevents data loss

### Success Criteria
- Command: `python scripts/add_archetype.py --name "Churn Prediction" --pain "customer_retention"`
- Validation catches errors before committing
- Graph automatically rebuilds after changes
- Vector index updates incrementally

---

## Dependency Graph

```
Epic 01: Knowledge Graph Foundation
    ↓
Epic 02: Test Data Preparation ← (parallel with Epic 03)
    ↓
Epic 03: LangChain ReAct Agent
    ↓
Epic 04: Multi-Stage Flow
    ↓
Epic 05: Streamlit Chat UI
    ↓
Epic 06: Observability Panel ← (parallel with Epic 07)
    ↓
Epic 07: Evaluation Metrics
    ↓
Epic 08: GCP Deployment ← **CRITICAL EARLY DEPLOYMENT**
    ↓
Epic 09: Firebase Persistence
    ↓
Epic 10: Intent Clarification ← (parallel with Epic 11)
    ↓
Epic 11: Report Generation
    ↓
Epic 12: Advanced Graph Queries ← (parallel with Epic 13)
    ↓
Epic 13: Knowledge Management
```

---

## Critical Path & Priorities

### Release 1: Foundation (Epics 1-4)
**Goal:** Core reasoning engine working end-to-end
- Epic 01: Knowledge Graph ← **CURRENT**
- Epic 02: Test Data
- Epic 03: ReAct Agent
- Epic 04: Multi-Stage Flow

### Release 2: User Interface (Epics 5-7)
**Goal:** Usable demo with transparency
- Epic 05: Streamlit UI
- Epic 06: Observability
- Epic 07: Evaluation

### Phase 3: Production Readiness (Epics 8-9)
**Goal:** Cloud deployment and persistence
- Epic 08: GCP Deployment ← **EARLY DEPLOYMENT**
- Epic 09: Firebase Persistence

### Phase 4: Enhancements (Epics 10-13)
**Goal:** Polish and advanced features
- Epic 10: Intent Clarification
- Epic 11: Report Generation
- Epic 12: Advanced Queries
- Epic 13: Knowledge Management

---

## Key Assumptions Across All Epics

### Technical
- Python 3.10+ as runtime
- LangChain as primary orchestration framework
- Vertex AI Gemini 1.5 Flash as LLM (cost-effective)
- NetworkX sufficient for graph operations (no Neo4j needed initially)
- FAISS adequate for vector search (no Pinecone unless scaling)
- Streamlit for UI (no React/complex frontend)

### Scope
- Single-user sessions (no multi-tenancy until Epic 9+)
- English language only
- Focus on SME business scenarios
- Demo/MVP quality (not production-hardened)
- Free tier constraints respected

### Data
- Knowledge base remains <100 archetypes, <200 pains, <500 prerequisites
- No real customer data (all synthetic/mock)
- Graph fits in memory (<10MB)
- Vector index <100k embeddings

### Deployment
- GCP as primary cloud provider
- Local development environment supported
- No Kubernetes (Cloud Run sufficient)
- No CDN or global distribution (single region)

---

## Risk Register

| Risk | Affected Epics | Mitigation |
|------|----------------|------------|
| Vertex AI quota exhaustion | 1, 3, 4, 8 | Use caching, implement rate limiting, fallback to local models |
| LangChain breaking changes | 3, 4, 6 | Pin versions, monitor changelog, abstract LangChain behind interfaces |
| Graph complexity explosion | 1, 12, 13 | Set hard limits on nodes/edges, optimize queries, consider Neo4j migration path |
| Streamlit performance issues | 5, 6, 11 | Lazy loading, pagination, caching, consider FastAPI backend |
| GCP free tier limits | 8, 9 | Monitor usage, implement quotas, document cost projections |
| Knowledge base inconsistency | 2, 13 | Strict validation, automated tests, version control |

---

## Success Metrics (Overall Project)

### Functional
- ✅ System answers 10 test queries correctly (pain → recommendation)
- ✅ Hybrid retrieval (KG + RAG) improves response quality vs RAG-only
- ✅ Multi-stage flow completes in <10 seconds
- ✅ Evaluation metrics show >80% usefulness on test cases

### Technical
- ✅ Unit test coverage >70%
- ✅ Integration tests for all epics
- ✅ Deployment completes in <5 minutes
- ✅ Application runs within GCP free tier for 100 sessions/month

### User Experience
- ✅ Non-technical users can interact without confusion
- ✅ Technical log provides full transparency
- ✅ Reports are actionable and well-formatted
- ✅ Session persistence works reliably

---

## Open Questions for Future Epics

1. **Epic 03:** Should the agent support parallel tool execution or strictly sequential?
2. **Epic 05:** Do we need streaming responses or is batch response acceptable?
3. **Epic 08:** Should we implement auto-scaling or keep concurrency=1?
4. **Epic 09:** How long should sessions persist? (30 days? 90 days?)
5. **Epic 11:** PDF export - is this required or nice-to-have?
6. **Epic 12:** At what graph size do we need to migrate to Neo4j?
7. **Epic 13:** Should knowledge updates require approval workflow?

---

## Next Steps

1. **Complete Epic 01** (Knowledge Graph Foundation)
2. **Review and refine Epic 02** (Test Data) based on Epic 01 learnings
3. **Spike on LangChain + Vertex AI integration** before Epic 03
4. **Early deployment experiment** (Epic 08 spike) after Epic 05 to validate cloud setup

---

*This document will be updated as epics are completed and new requirements emerge.*
