# High-Level Implementation & Deployment Plan

**Version:** 1.0  
**Date:** 2025-11-04  
**Scope:** Full conversational assessment system per functional spec

---

## Executive Summary

This plan outlines the implementation and deployment of a conversational AI pilot assessment engine that helps organizations identify AI opportunities through natural dialogue. The system uses an **edge-based factor model** where outputs are assessed through their contributing factors (People, Tools, Processes, Dependencies), then recommends targeted AI pilots based on bottleneck analysis.

**Core Innovation:** Output-centric assessment with LLM-powered semantic inference for solution recommendations.

---

## 1. System Architecture Overview

### 1.1 Technology Stack

**Backend:**
- **Language:** Python 3.11+
- **LLM:** Gemini 1.5 Flash via Vertex AI (streaming)
- **Graph:** NetworkX (in-memory graph operations)
- **Data:** Firestore (user data), Cloud Storage (static catalogs)

**Frontend:**
- **Framework:** Streamlit (conversational chat interface)
- **Streaming:** Async generators for real-time LLM responses
- **Auth:** Firebase Authentication (Google OAuth)

**Deployment:**
- **Platform:** Google Cloud Platform
- **Compute:** Cloud Run (scale-to-zero, session affinity)
- **Region:** us-central1 (Vertex AI availability)

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Browser)                           │
│  Chat Interface + Knowledge Tree + Technical Log            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT APP (Cloud Run)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Conversation Orchestrator                             │ │
│  │    ├─ Discovery Engine (Output identification)         │ │
│  │    ├─ Assessment Engine (Edge rating + MIN calc)       │ │
│  │    ├─ Context Extractor (Business constraints)         │ │
│  │    ├─ Recommendation Engine (LLM semantic inference)   │ │
│  │    └─ Report Generator (Comprehensive PDF)             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Vertex AI   │ │  Firestore   │ │   Cloud      │ │  Firebase    │
│  (Gemini)    │ │  (User Data) │ │   Storage    │ │    Auth      │
│              │ │              │ │  (Catalogs)  │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

**Why this stack:**
- **Gemini Flash:** 4x cheaper than Pro, <1s first token, sufficient quality
- **Firestore:** User isolation, real-time updates, free tier covers POC
- **Cloud Run:** Scale-to-zero ($0 when idle), no VM management
- **Streamlit:** Rapid prototyping, built-in session management

---

## 2. Core Components

### 2.1 Discovery Engine

**Purpose:** Identify output from natural language description

**Process:**
1. User describes problem ("Sales forecasts are always wrong")
2. LLM extracts keywords, pain points, system mentions
3. Match against output catalog using semantic similarity
4. Present top 1-3 candidates for confirmation
5. Infer creation context (Team, Process, System) from templates

**Key Files:**
- `organizational_templates/functions/*.json` - Output catalog
- `inference_rules/output_discovery.json` - Matching rules
- `organizational_templates/cross_functional/common_systems.json` - System defaults

**Implementation:**
```python
# Pseudocode
def discover_output(user_message, conversation_history):
    # LLM extracts semantic features
    features = llm.extract_features(user_message)
    
    # Match against output catalog
    candidates = semantic_match(features, output_catalog)
    
    # Present for confirmation
    return top_candidates(candidates, limit=3)
```

### 2.2 Assessment Engine

**Purpose:** Collect edge ratings and calculate output quality

**Edge-Based Model:**
- **Nodes:** Output, Tool, Process, People
- **Edges (Factors):** Effect of one entity on output quality
  - People → Output (Team execution impact)
  - Tool → Output (System capability impact)
  - Process → Output (Process maturity impact)
  - Output → Output (Dependency quality impact)

**Rating Collection:**
1. **Conversational inference:** LLM infers ⭐ rating from user description
2. **Validation:** System shows inference, user confirms/adjusts
3. **Evidence tracking:** Store user's exact words with tier (1-5)
4. **Bayesian aggregation:** Multiple evidence pieces weighted by tier

**Calculation:**
```python
# Pseudocode
def calculate_output_quality(edges):
    # MIN of all incoming edges
    return min(edge.score for edge in edges)

def identify_bottleneck(edges):
    min_score = calculate_output_quality(edges)
    return [edge for edge in edges if edge.score == min_score]
```

**Evidence Tiers:**
- Tier 1: AI inferred from indirect data (weight=1)
- Tier 2: User mentioned indirectly (weight=3)
- Tier 3: User stated directly (weight=9)
- Tier 4: User provided example (weight=27)
- Tier 5: User provided quantified example (weight=81)

### 2.3 Context Extraction Engine

**Purpose:** Extract business decision factors naturally throughout conversation

**Strategy:** "Sprinkle, don't survey"
- Extract naturally when user volunteers information
- Only ask explicitly for missing critical factors before recommendations

**Critical Factors (always need):**
- Budget range
- Timeline urgency
- Visibility preference (quiet win vs showcase)

**Contextual Factors (only if relevant):**
- Compliance requirements
- Vendor constraints
- Stakeholder pressure
- Resource constraints

**Extraction Moments:**
- **Moment 1:** After output identified → Timeline urgency
- **Moment 2:** When user describes pain → Business impact
- **Moment 4:** When user reveals constraints → Budget
- **Moment 7:** Pre-recommendation checkpoint → Ask missing factors

### 2.4 Recommendation Engine

**Purpose:** Map bottlenecks to AI pilot recommendations

**LLM Semantic Inference Approach:**

**Why not hardcoded mapping:**
- Combinatorial explosion (46+ outputs × 4 edge types × 5 scores × 100+ pain points)
- Same bottleneck has different solutions based on context
- Example: "Team ⭐⭐" could mean knowledge gaps, SME bottleneck, or incentive issues

**Process:**
1. **Build rich context bundle:**
   - Output details + current/required quality
   - Bottleneck edges with evidence
   - Business constraints (cost, timeline, visibility)
   - Team/system archetypes

2. **LLM inference with structured catalogs:**
   - Pain point catalog (100+ pain points)
   - AI archetype catalog (27 archetypes)
   - Pilot catalog (28 specific examples)

3. **Structured output:**
   - Identified pain points (with confidence)
   - Mapped AI archetypes (with rationale)
   - Ranked pilot recommendations (2-3 options)

**Prompt Structure:**
```
Given context:
- Output: Sales Forecast (⭐⭐ → ⭐⭐⭐⭐ gap)
- Bottleneck: People(Junior) → Output (⭐⭐)
- Evidence: "No one to learn from", "Team is junior"
- Constraints: €30k-€50k, 3 months, quiet win

Tasks:
1. Identify pain points (reference catalog)
2. Map to AI archetypes (reference catalog)
3. Recommend specific pilots (reference catalog)

Output: JSON with pain_points[], archetypes[], pilots[]
```

### 2.5 Feasibility Assessment Engine

**Purpose:** Check prerequisites and identify gaps

**Archetype-Based Prerequisites:**
- 27 AI archetypes with structured prerequisites
- Categories: Data, Team, System, Organizational
- Feasibility tiers:
  - Tier 1: Ready (0 weeks, €0, 80-90% success)
  - Tier 2: Minor gaps (+4-6 weeks, +€10k-€20k, 60-80%)
  - Tier 3: Major gaps (+8-16 weeks, +€30k-€60k, 40-60%)
  - Tier 4: Not feasible (deal-breakers present)

**Process:**
```python
# Pseudocode
def assess_feasibility(pilot, user_context):
    archetype = get_archetype(pilot)
    prerequisites = load_prerequisites(archetype)
    
    gaps = []
    for prereq in prerequisites:
        if not met(prereq, user_context):
            gaps.append(prereq)
    
    tier = calculate_tier(gaps)
    cost_to_bridge = estimate_gap_cost(gaps)
    
    return FeasibilityResult(tier, gaps, cost_to_bridge)
```

### 2.6 Report Generator

**Purpose:** Generate comprehensive assessment report for stakeholders

**Two-Tier Strategy:**
- **In-conversation:** 2-3 targeted recommendations (fast decisions)
- **Downloadable report:** 5-10+ options with full analysis (stakeholder approval)

**Report Structure:**
1. Executive Summary (1 page)
2. Top 3 Recommendations (3-5 pages)
   - Expected impact, timeline, cost
   - Prerequisites, feasibility tier
   - Implementation approach
3. Alternative Solutions (2-3 pages)
   - 4-7 additional options
   - Comparison matrix
4. Prerequisite Deep Dive (3-4 pages)
   - Data, team, system, organizational gaps
   - Cost-to-bridge estimates
5. Staged Approach (1-2 pages)
   - Quick wins → comprehensive solutions
6. Decision Matrix (1 page)
7. Appendix (2-3 pages)

**Total:** 13-18 pages

---

## 3. Data Models

### 3.1 Firestore Schema

```
/users/{user_id}/
  nodes/
    outputs/{output_id}
      - output_name, function, description
      - incoming_edges: [edge_id, ...]  # Denormalized
      - calculated_score: 2.5  # Cached MIN()
      - calculated_confidence: 0.75
    
    tools/{tool_id}
      - tool_name, tool_type, description
      - outgoing_edges: [edge_id, ...]
    
    processes/{process_id}
      - process_name, maturity_level, description
      - outgoing_edges: [edge_id, ...]
    
    people/{people_id}
      - archetype_name, description
      - outgoing_edges: [edge_id, ...]
  
  edges/{edge_id}
    - source_id, target_id
    - edge_name
    - current_score: 1-5 stars
    - current_confidence: 0.0-1.0
    - evidence: [
        {statement, tier, timestamp, conversation_id}
      ]
  
  conversations/{conversation_id}
    - messages: [{role, content, timestamp}]
    - extracted_context: {budget, timeline, visibility, ...}
    - status: "in_progress" | "completed"
  
  assessments/{assessment_id}
    - output_id
    - bottleneck_edges: [edge_id, ...]
    - recommendations: [pilot_id, ...]
    - feasibility_results: {...}
    - created_at
```

### 3.2 In-Memory Graph (per session)

**Hybrid Approach:**
- Firestore = source of truth (persistence)
- NetworkX = fast graph operations (BFS, DFS, MIN calculation)
- Load relevant subgraph on session start
- Write back to Firestore on changes

**Why hybrid:**
- Graph won't be large (humans can't comprehend deep recursion)
- In-memory enables fast traversal, power of elimination
- Firestore for persistence, conversation history

---

## 4. Implementation Phases

### Phase 1: Core Infrastructure (Weeks 1-2)

**Deliverables:**
- GCP project setup (Firestore, Cloud Storage, Vertex AI, Firebase Auth)
- Python project structure
- Streamlit basic chat interface
- LLM integration (Gemini streaming)
- Session management

**Tasks:**
1. Run infrastructure setup script (`deployment/setup-infrastructure.sh`)
2. Create Python virtual environment
3. Install dependencies (`requirements.txt`)
4. Implement Gemini client with streaming
5. Create Streamlit chat UI skeleton
6. Test end-to-end: user message → LLM response

**Success Criteria:**
✅ Can send message and receive streaming LLM response  
✅ Firebase auth working  
✅ Firestore connection established

### Phase 2: Discovery & Assessment (Weeks 3-4)

**Deliverables:**
- Output discovery from natural language
- Edge-based assessment with conversational inference
- Evidence tracking with Bayesian aggregation
- MIN calculation and bottleneck identification

**Tasks:**
1. Load output catalog from JSON
2. Implement semantic matching (LLM-based)
3. Build conversational assessment flow
4. Implement evidence tier classification
5. Implement Bayesian weighted ranking
6. Build in-memory graph (NetworkX)
7. Implement MIN calculation

**Success Criteria:**
✅ Can identify outputs from descriptions  
✅ Can assess all 4 edge types  
✅ Correctly calculates MIN() and identifies bottlenecks  
✅ Evidence properly weighted by tier

### Phase 3: Context Extraction (Week 5)

**Deliverables:**
- Natural business context extraction
- Pre-recommendation checkpoint
- Contradiction detection

**Tasks:**
1. Implement context tracker
2. Build LLM-based context extractor
3. Create question generator for missing factors
4. Implement Moment 7 checkpoint
5. Add contradiction detection

**Success Criteria:**
✅ Extracts budget, timeline, visibility naturally  
✅ Asks for missing critical factors before recommendations  
✅ Handles contradictions gracefully

### Phase 4: Recommendation Engine (Weeks 6-7)

**Deliverables:**
- LLM semantic inference for recommendations
- Feasibility assessment
- Pilot ranking with constraints

**Tasks:**
1. Load pain point, archetype, pilot catalogs
2. Build rich context bundle
3. Implement LLM recommendation prompt
4. Parse and validate JSON output
5. Load prerequisite catalog
6. Implement feasibility checker
7. Rank pilots by fit score + feasibility

**Success Criteria:**
✅ Recommends 2-3 relevant pilots  
✅ Explains reasoning (pain points → archetypes → pilots)  
✅ Checks feasibility and identifies gaps  
✅ Respects business constraints (cost, timeline)

### Phase 5: Report Generation (Week 8)

**Deliverables:**
- Comprehensive assessment report (PDF)
- Decision matrix
- Staged approach recommendations

**Tasks:**
1. Design report template
2. Implement report generator
3. Add decision matrix logic
4. Create staged approach algorithm
5. Generate PDF output

**Success Criteria:**
✅ Generates 13-18 page professional report  
✅ Includes all 7 sections  
✅ Downloadable from UI

### Phase 6: Polish & Testing (Weeks 9-10)

**Deliverables:**
- Error handling
- User testing
- Demo scenarios
- Documentation

**Tasks:**
1. Add comprehensive error handling
2. Implement session save/load
3. Create demo scenarios (Sales, Finance, Operations)
4. User testing with 3-5 users
5. Bug fixes
6. Documentation

**Success Criteria:**
✅ Handles edge cases gracefully  
✅ User testing feedback incorporated  
✅ Demo-ready

---

## 5. Deployment Strategy

### 5.1 Development Environment

```bash
# Local development setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment variables
export GOOGLE_CLOUD_PROJECT="ai-pilot-assessment-dev"
export GOOGLE_APPLICATION_CREDENTIALS="./deployment/keys/service-account-key.json"
export VERTEX_AI_LOCATION="us-central1"
export VERTEX_AI_MODEL="gemini-1.5-flash"

# Run locally
streamlit run app.py
```

### 5.2 Cloud Run Deployment

**Container Configuration:**
```yaml
# deployment/cloud-run-config.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: assessment-engine
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"  # Scale to zero
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/sessionAffinity: "true"  # Sticky sessions
    spec:
      serviceAccountName: assessment-engine-sa@PROJECT.iam.gserviceaccount.com
      containerConcurrency: 10
      timeoutSeconds: 300  # 5 min for long conversations
      containers:
      - image: gcr.io/PROJECT/assessment-engine:latest
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "ai-pilot-assessment-prod"
        - name: VERTEX_AI_LOCATION
          value: "us-central1"
        - name: VERTEX_AI_MODEL
          value: "gemini-1.5-flash"
```

**Deployment Commands:**
```bash
# Build container
gcloud builds submit --tag gcr.io/${PROJECT_ID}/assessment-engine

# Deploy to Cloud Run
gcloud run deploy assessment-engine \
  --image gcr.io/${PROJECT_ID}/assessment-engine \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account assessment-engine-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --min-instances 0 \
  --max-instances 10 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --session-affinity
```

### 5.3 Cost Optimization

**GCP Free Tier Coverage:**
- **Cloud Run:** 2M requests/month, 360K GB-seconds (covers POC)
- **Firestore:** 1GB storage, 50K reads/day, 20K writes/day
- **Cloud Storage:** 5GB storage
- **Vertex AI:** $300 credit for new accounts

**Estimated Monthly Cost (after free tier):**
- Cloud Run: ~$5-10 (low traffic)
- Firestore: ~$0-5 (< 1GB data)
- Vertex AI: ~$10-20 (Gemini Flash, ~100 conversations/month)
- **Total:** ~$15-35/month

**Scale-to-zero strategy:**
- Cloud Run scales to 0 instances when idle
- Cost = $0 when no traffic
- 1-5s cold start acceptable (show loading message)

---

## 6. Testing Strategy

### 6.1 Unit Tests

**Coverage:**
- Bayesian weighted ranking (evidence aggregation)
- MIN calculation (output quality)
- Bottleneck identification
- Context extraction
- Feasibility tier calculation

**Example:**
```python
def test_bayesian_ranking():
    evidence = [
        {"tier": 1, "score": 5},  # weight=1
        {"tier": 4, "score": 2},  # weight=27
    ]
    # WAR = (5*1 + 2*27) / (1+27) = 59/28 = 2.1
    # With C=10, μ=2.0: S = (28/38)*2.1 + (10/38)*2.0 = 2.08
    assert calculate_score(evidence) == pytest.approx(2.08, 0.01)
```

### 6.2 Integration Tests

**Scenarios:**
1. **Happy Path:** User knows output, can answer questions, gets recommendations
2. **Vague Input:** "Sales is a mess" → progressive refinement
3. **Contradictions:** User changes mind, system detects and resolves
4. **Multi-Bottleneck:** Multiple tied bottlenecks, combo recommendations
5. **Feasibility Gaps:** Prerequisites missing, system identifies cost-to-bridge

### 6.3 Demo Scenarios

**Scenario 1: Sales Forecast (Happy Path)**
```
User: "Our sales forecasts are always wrong"
→ System identifies "Sales Forecast" output
→ Infers context: Sales Ops team, CRM system
→ Assesses edges: Team ⭐⭐, System ⭐, Process ⭐, Deps ⭐⭐
→ Calculates: Actual = ⭐ (MIN)
→ User sets required = ⭐⭐⭐⭐
→ Gap = 3 stars, Bottleneck = System + Process
→ Recommends: AI Copilot OR Process Automation
```

**Scenario 2: Customer Support (Process Bottleneck)**
```
User: "Support tickets take forever to resolve"
→ Output: Resolved Support Tickets
→ Edges: Team ⭐⭐⭐, System ⭐⭐, Process ⭐, Deps ⭐⭐⭐⭐
→ Actual = ⭐ (Process bottleneck)
→ Required = ⭐⭐⭐⭐
→ Recommends: Process Intelligence OR Workflow Automation
```

---

## 7. Success Criteria

### 7.1 Functional Requirements

✅ Identifies outputs from natural language (>80% accuracy)  
✅ Assesses all 4 edge types conversationally  
✅ Correctly calculates MIN() for output quality  
✅ Identifies bottleneck edges  
✅ Extracts business context naturally (budget, timeline, visibility)  
✅ Recommends 2-3 relevant pilots with reasoning  
✅ Checks feasibility and identifies gaps  
✅ Generates comprehensive assessment report

### 7.2 User Experience Requirements

✅ Conversational flow (not form-based)  
✅ LLM generates, user validates  
✅ Minimal questions (<10 for full assessment)  
✅ Clear explanations of ratings and calculations  
✅ Streaming responses (<2s first token)  
✅ Simple language (no jargon)

### 7.3 Performance Requirements

✅ Response time <3s per message  
✅ Full assessment in <15 minutes  
✅ Report generation <10s  
✅ Cold start <5s (acceptable with loading message)

---

## 8. Risk Mitigation

### 8.1 LLM Dependency Risks

**Risk:** LLM hallucinations, errors, latency

**Mitigation:**
- Structured output format (JSON schema validation)
- Fallback heuristics (bottleneck type → pilot category)
- Cache LLM responses for identical contexts
- Timeout handling (5s max per LLM call)
- Log all LLM calls for debugging

### 8.2 Data Quality Risks

**Risk:** User provides contradictory or incomplete information

**Mitigation:**
- Evidence tracking with tiers (later evidence outweighs earlier)
- Contradiction detection and resolution
- Accept "I don't know" (confidence=0.0)
- Power of elimination (infer from what's NOT the problem)

### 8.3 Scalability Risks

**Risk:** System doesn't scale beyond POC

**Mitigation:**
- Cloud Run auto-scales (0-10 instances)
- Firestore scales automatically
- In-memory graph limited to relevant subgraph
- Session affinity prevents state fragmentation

### 8.4 Cost Risks

**Risk:** Unexpected GCP costs

**Mitigation:**
- Budget alerts at 50%, 90%, 100%
- Scale-to-zero when idle
- Use Gemini Flash (4x cheaper than Pro)
- Monitor per-conversation cost
- Free tier covers POC phase

---

## 9. Future Enhancements (Out of Scope for V1)

❌ ROI calculation (requires additional data)  
❌ Dependency graph traversal (manual for V1)  
❌ Multiple quality metrics per output (generic quality only)  
❌ Quantity assessment (quality only)  
❌ Multi-user collaboration  
❌ All 22 function templates (use 3-5 for V1)  
❌ Advanced scoping (domain/system-specific factors)  
❌ Assumption tracking and testing  
❌ Project evaluation history  
❌ Integration with project management tools

---

## 10. Timeline Summary

**Total Duration:** 10 weeks (2.5 months)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Infrastructure | Weeks 1-2 | GCP setup, basic chat |
| 2. Discovery & Assessment | Weeks 3-4 | Output ID, edge rating, MIN calc |
| 3. Context Extraction | Week 5 | Business context extraction |
| 4. Recommendations | Weeks 6-7 | LLM inference, feasibility |
| 5. Report Generation | Week 8 | PDF report |
| 6. Polish & Testing | Weeks 9-10 | Demo-ready |

**Milestones:**
- Week 2: Basic chat working
- Week 4: Full assessment flow working
- Week 7: Recommendations working
- Week 10: Demo-ready

---

## 11. Next Steps

1. **Review & Approve:** Stakeholder review of this plan
2. **Infrastructure Setup:** Run `deployment/setup-infrastructure.sh`
3. **Kickoff Phase 1:** Set up development environment
4. **Weekly Check-ins:** Progress review every Friday
5. **Demo at Week 10:** Stakeholder demo

---

**Document Status:** Ready for Review  
**Owner:** Technical Lead  
**Approvers:** Product Owner, Engineering Manager
