# AI Pilot Assessment Engine

A **Decision-to-Act system** that bridges the gap from "we think we have a problem" to "we authorize action" through structured problem formation, option evaluation, and evidence-based decision rules.

## Vision

This system guides leaders through a **linear discovery process** that stops at a clear **Go/No-Go/Time-boxed Try** decision while capturing projections (plans, metrics, risks) without executing them. It transforms vague signals into defensible, auditable decisions.

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

This monitor surfaces patterns across decisions, enabling continuous improvement of the decision-making process itself

---

## Key Concepts

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
