# AI Pilot Assessment Engine

A **Decision-to-Act system** that bridges the gap from "we think we have a problem" to "we authorize action" through structured problem formation, option evaluation, and evidence-based decision rules.

**No effort is ever lost.** Every piece of context, evidence, and decision pattern is preserved and reused—making each decision faster and better informed than the last.

## Vision

This system guides leaders through a **linear discovery process** that stops at a clear **Go/No-Go/Time-boxed Try** decision while capturing projections (plans, metrics, risks) without executing them. It transforms vague signals into defensible, auditable decisions.

The system operates on a **"do once, benefit forever"** principle: organizational context is captured once and applied to all future decisions. Conversations can be paused and resumed via email links. Everything can be exported as detailed AI prompts—no lock-in, full portability.

### Core Process

**Signal → Problem → Options → Evidence → Decision**

1. **Problem Formation** - Convert signals and interpretations into falsifiable problem statements with clear stakes and scope
2. **Objective Setting** - Define time-bound business outcomes with measurable targets
3. **Option Generation** - Force consideration of ≥3 options (including "Do Nothing" and "Delay")
4. **Evidence Collection** - Gather internal data and external sources with quality ratings
5. **Impact Projection** - Model how each option moves objectives, including risks and reversibility
6. **Decision Rule Definition** - Set metric thresholds that trigger action (e.g., "Proceed if pilot ≤€25k and cycle time reduction ≥15% at p90")
7. **Decision Record** - Document the Go/No-Go/Try decision with rationale and owner

### Decision Readiness Checklist

Before any decision, the system ensures:
- Problem statement is **falsifiable** and **valuable**
- At least **3 options** considered (including "Do Nothing")
- Evidence quality rated; key assumptions listed with confidence
- Objectives mapped to **measurable metrics** with targets
- Constraints acknowledged; **reversibility** scored
- **Decision rule** formulated with clear thresholds
- **Decision owner** named; **Decision Record** drafted

### Observability Monitor

The system includes an **observability monitor** that tracks:
- Decision quality metrics (completeness, evidence strength, assumption confidence)
- Process adherence (checklist completion, option diversity)
- Projection accuracy (when decisions proceed to action)
- Assumption validation status
- Decision velocity and bottlenecks

This monitor surfaces patterns across decisions, enabling continuous improvement of the decision-making process itself.

### Persistence & Portability

The system operates on a **"do once, benefit forever"** principle:

**Zero Effort Loss**
- All user-provided information is automatically preserved and reusable across future decisions
- Organizational context (norms, policies, constraints) is captured once and applied to all subsequent decisions
- Evidence, assumptions, and decision patterns build a growing knowledge base
- Conversations can be paused and resumed via email links—no work is ever lost, even accidentally

**No Lock-In**
- Every piece of information can be exported as detailed AI prompts
- Users can "smarten up" their favorite AI with their organizational context
- Exported prompts create a transferable, intelligent sparring partner
- Decision history and patterns remain portable across tools

This ensures that the system becomes more valuable over time while keeping users in full control of their data.

---

## Key Concepts

### UX Design Philosophy

The system is designed with **user experience as a core principle**. The LLM is **not inquisitive**—users are not burdened with answering deep, difficult questions. Instead, the LLM infers data points for the comprehensive model (described below) through **deep but natural conversation**.

**Inference-Driven Interaction**
- The system infers assessment values from conversational context rather than explicit questioning
- Inferred data points are displayed transparently to the user
- Users can challenge inferences: *"Why do you think our data governance is only at 20%?"*
- The LLM provides insights and reasoning to support or adjust values

**Evidence-Based Updates**
- Users cannot arbitrarily change values (*"Set data governance readiness to 80%"*) without backing them up with narrative evidence
- Every adjustment must be grounded in context, examples, or reasoning provided through conversation
- This maintains assessment integrity while keeping the interaction natural

**Scope Discipline**
- This is **not a what-if tool**—the scope is already substantial
- The system focuses on inference and evidence-based assessment, not hypothetical scenario modeling

### Object Model

The system structures decisions around these core objects:

- **Signal/Data → Interpretation** - Raw observations transformed into meaning
- **Norms/Policies → Expectations** - Organizational standards that shape problem framing
- **Problem** - Falsifiable statement with stake & scope
- **Objectives** - Time-bound business outcomes
- **Constraints** - Budget, time, capabilities
- **Assumptions/Hypotheses** - With confidence levels
- **Options** - Including "Do Nothing" and "Delay"
- **Evidence** - Internal data and external sources with quality ratings
- **Impact Model** - Projection per option showing how it moves objectives
- **Risks & Reversibility** - Per option assessment
- **Effort & Cost** - One-off and recurring
- **Metrics & Guardrails** - Leading/lagging indicators (projections only)
- **Decision Rule** - Thresholds on metrics/conditions that trigger action
- **Decision Record** - Go/No-Go/Try decision with rationale

### Scoring Framework

**Value** = Expected Impact × Confidence  
**Speed** = Reversibility ÷ Effort  
**Priority** = Value × Cost-of-Delay factor

Results surface as a 2×2 matrix (Impact vs Effort) with Confidence labels, supporting quick Go/No-Go/Try decisions.

### Outputs

Each decision produces:
- **Decision Packet** - Complete record of problem, objectives, options, evidence, projections, risks, and decision
- **Assumption Register** - What to test if action proceeds
- **Metric Template** - Names, formulas, target thresholds (projection only)

---

## Documentation

- **[Linear Discovery Process](docs/linear_discovery_process.md)** - Full vision and methodology
- **[System Architecture](docs/system_architecture_specification.md)** - Technical design
- **[Epic Documentation](docs/)** - Implementation details

---

## Status

This project is under active development. See `docs/` for current implementation status and roadmap.
