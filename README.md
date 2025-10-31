# AI Pilot Assessment Engine

An **exploratory assessment system** that helps organizations understand their AI readiness through conversational factor assessment and project evaluation. (Everything that influences the feasibility of an AI pilot is a "factor" in this system.)

**No effort is ever lost.** 
- Every conversation builds cumulative evidence about your organization's factors (your effort keeps working for you)
- Your data is yours, always available to export in LLM or human-friendly formats.
- Your data is safe, LLM will send you a signed NDA the second you ask for it.

---

## Quick Links

**📖 Documentation:**
- [Technical Architecture](docs/gcp_technical_architecture.md) - Complete GCP implementation guide
- [Architecture Summary](docs/architecture_summary.md) - High-level overview
- [Implementation Roadmap](ARCHITECTURE_COMPLETE.md) - Next steps

**🎯 Key Concepts:**
- [Vision & Features](#vision) - What this system does
- [Technical Architecture](#technical-architecture) - GCP deployment details
- [Status](#status) - Current progress

---

## Vision

This system enables **free exploration** of organizational readiness without rigid processes. Users can:
- Start anywhere (project idea, factor discussion, "what's possible?")
- Jump freely between topics
- Evaluate projects at any confidence level
- Never be blocked by "you need X first"

The system shows **confidence scores** and **what would improve them**, letting users decide when "good enough" is reached.

### Core Principle

**Factor-centric assessment** - Everything links to factors (data_quality, ai_capability, cultural_fit, etc.). The system:
1. Accumulates evidence from conversations
2. Infers factor values cumulatively (not from single mentions)
3. Tracks confirmed vs unconfirmed inferences
4. Evaluates project feasibility based on assessed factors
5. Shows ROI of continuing assessment

### What This Is NOT

- ❌ Not a decision tracking system
- ❌ Not a linear process enforcer
- ❌ Not a "what-if" scenario modeler
- ❌ Not an execution tracker

### What This IS

- ✅ An exploration tool for organizational readiness
- ✅ A project evaluation system with confidence scoring
- ✅ A conversation-based factor assessment engine
- ✅ A "thinking partner" that remembers everything

---

## Key Features

### 1. Exploratory, Not Rigid
- Start with any question
- Jump between topics freely
- System never blocks exploration
- Always proceed with confidence score

### 2. Cumulative Inference
- Factor values derived from ALL conversation history
- Confidence increases with consistent evidence
- Even confirmed claims stay low-confidence without examples
- User can validate or correct anytime

### 3. Project Evaluation
- Evaluate any project idea at any time
- Shows confidence breakdown by factor category
- Identifies gaps and ROI of filling them
- Risk/assumption ledger instead of arbitrary thresholds

### 4. Pareto-Driven Suggestions
- "What's next?" shows top 3 high-ROI actions
- Signals diminishing returns
- User decides when "good enough"

### 5. Context Accumulation
- Never ask twice
- Auto-populate from factor journal
- Organizational context reused forever

---

## Persistence & Portability

The system operates on a **"do once, benefit forever"** principle:

**Zero Effort Loss**
- All user-provided information is automatically preserved and reusable across future assessments
- Organizational context (norms, policies, constraints) is captured once and applied to all subsequent evaluations
- Evidence, assumptions, and factor assessments build a growing knowledge base
- Conversations can be paused and resumed via email links—no work is ever lost, even accidentally

**No Lock-In**
- Every piece of information can be exported as detailed AI prompts
- Users can "smarten up" their favorite AI with their organizational context
- Exported prompts create a transferable, intelligent sparring partner
- Assessment history and patterns remain portable across tools

This ensures that the system becomes more valuable over time while keeping users in full control of their data.

---

## Key Concepts

### UX Design Philosophy

The system is designed with **user experience as a core principle**. The LLM is **not inquisitive**—users are not burdened with answering deep, difficult questions. Instead, the LLM infers factor values through **deep but natural conversation**.

**Inference-Driven Interaction**
- The system infers factor values from conversational context rather than explicit questioning
- Inferred values are displayed transparently to the user
- Users can challenge inferences: *"Why do you think our data governance is only at 20%?"*
- The LLM provides insights and reasoning to support or adjust values

**Evidence-Based Updates**
- Users cannot arbitrarily change values (*"Set data governance readiness to 80%"*) without backing them up with narrative evidence
- Every adjustment must be grounded in context, examples, or reasoning provided through conversation
- Even confirmed claims stay low-confidence until backed by examples (e.g., "Our CEO supports AI pilots" needs concrete examples to increase confidence)
- This maintains assessment integrity while keeping the interaction natural

**Scope Discipline**
- This is **not a what-if tool**—the scope is already substantial
- The system focuses on inference and evidence-based assessment, not hypothetical scenario modeling

### Project Evaluation Approach

When evaluating a project, the system helps clarify:

**Project Definition (TBD - needs better specification)**
- Clear project description and scope
- Estimated cost and timeline *(with massive disclaimer: zero guarantees, user must validate with experts)*

**Internal Selling**
- ROI estimation with KPIs and deadline for stakeholder buy-in

**Feasibility Assessment**
- Assumptions enumerated and pushed to reasonable level of discovery
- Key dependencies identified *(rough and arbitrary at this stage—vital for primer guidance, but not nuanced enough for final decisions)*
- Risk/assumption ledger maintained

This is **not a mandatory checklist**—users can evaluate projects at any time. It's a guide for what makes evaluations more confident and actionable.

### Outputs

The system produces:
- **Project Evaluation Snapshots** - Timestamped feasibility assessments with confidence breakdowns, gaps, risk/assumption ledger, and recommendations
- **Factor Assessment Summary** - Current state of all assessed factors with confirmed/unconfirmed status
- **Evidence Trail** - Full conversation history linked to factor journals
- **Exportable Context** - All organizational knowledge as portable AI prompts

---

## Technical Architecture

The system is deployed on **Google Cloud Platform** with a Streamlit frontend and serverless backend.

### Architecture Overview

- **Frontend:** Streamlit app with 3-panel layout (chat | knowledge tree | technical log)
- **Backend:** Python-based conversation orchestrator with async streaming
- **LLM:** Vertex AI (Gemini 1.5 Flash) for intent classification, factor inference, and response generation
- **Persistence:** Firestore for user data, factors, journal entries, and project evaluations
- **Static Knowledge:** Cloud Storage for domain graph (factors, archetypes, relationships)
- **Authentication:** Firebase Auth (Google OAuth + Email/Password)
- **Hosting:** Cloud Run (serverless, scale-to-zero for cost optimization)

### Key Technical Decisions

**Hybrid Knowledge Model**
- Static domain graph (factors, AI archetypes, scales) loaded into memory from Cloud Storage
- Dynamic user data (factor values, journal entries) stored in Firestore
- Fast graph traversal (<1ms) with clean separation of concerns

**Real-Time Streaming**
- LLM responses stream token-by-token to chat window
- Technical events (intent classification, factor updates) stream to log window in real-time
- Knowledge tree updates via Firestore polling (1-2 second latency)

**Cost Optimization**
- Cloud Run scales to zero when idle (free tier covers low traffic)
- Gemini 1.5 Flash (4x cheaper than Pro, sufficient for task)
- Estimated cost: **~$1.50/month** for 10 users, 500 conversations/month

**Factor-Centric Persistence**
- Journal entries created only for meaningful factor updates (not every utterance)
- 83% storage savings vs full event sourcing
- Cumulative inference: factor values synthesized from ALL journal entries via LLM

### Architecture Documentation

**Implementation Guides:**
- **[GCP Technical Architecture](docs/gcp_technical_architecture.md)** - Complete system architecture, component responsibilities, data flow, deployment
- **[Data Schemas](docs/gcp_data_schemas.md)** - Firestore schema, static graph structure, Python data classes, LLM prompts
- **[Architecture Summary](docs/architecture_summary.md)** - High-level overview, key decisions, technology stack
- **[System Interactions](docs/system_interactions.md)** - Component interactions, responsibility matrix, process flows
- **[Architecture Complete](ARCHITECTURE_COMPLETE.md)** - Implementation roadmap and design summary

**Domain Design:**
- **[Conversation Memory Architecture](docs/conversation_memory_architecture.md)** - Factor journal persistence, cumulative inference
- **[Exploratory Assessment Architecture](docs/exploratory_assessment_architecture.md)** - Assessment flow patterns, confidence scoring
- **[User Interaction Guidelines](docs/user_interaction_guideline.md)** - Conversational UX patterns, LLM guidelines

---

## Status

**Architecture:** ✅ Complete - Full GCP technical architecture documented (49,000+ words)  
**Implementation:** 🔄 Ready to begin - All components, schemas, and contracts defined  
**Deployment:** 📋 Planned - Cloud Run serverless deployment with scale-to-zero cost optimization
