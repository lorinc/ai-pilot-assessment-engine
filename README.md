# AI Pilot Assessment Engine

An **exploratory assessment system** that helps organizations understand their AI readiness through conversational factor assessment and project evaluation.

**No effort is ever lost.** Every conversation builds cumulative evidence about your organization's factors, making project evaluations more confident over time.

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

## Documentation

- **[Conversation Memory Architecture](docs/conversation_memory_architecture.md)** - Factor journal persistence
- **[User Interaction Guidelines](docs/user_interaction_guideline.md)** - Conversational patterns
- **[Exploratory Assessment Architecture](docs/exploratory_assessment_architecture.md)** - System design

---

## Status

Active development. Core architecture documented, implementation in progress.
