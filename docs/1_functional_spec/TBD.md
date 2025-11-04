# TBD - To Be Done/Discussed

This document tracks items that need future attention, discussion, or implementation.

## Format
Each entry includes:
- **Context**: What this relates to
- **Intent**: What needs to be done or decided
- **Added**: Date added

---

## Items

### 1. System Self-Awareness Response Pattern
**Added**: 2025-11-01

**Context**: When the system identifies its own limitations or imperfections during user interaction.

**Intent**: Implement a response that acknowledges the system's inherent limitations using George Box's principle: "All models are wrong, but some are useful" (1976 conference). This means that all designs must simplify reality into manageable patterns. If done well, that cut is taken from the top 20% of the Pareto principle on the usefulness/complexity plane. The response should frame limitations as intentional design constraints rather than flaws, while inviting users to report genuine UX/usefulness issues to the developer. This balances transparency about model limitations with actionable feedback collection.

---

### 2. Data Engineer Technical Assessment Document
**Added**: 2025-11-01

**Context**: Technical infrastructure details require specialized expertise that business users may not possess.

**Intent**: Create a downloadable/uploadable document template for data engineer leads to complete. This document should gather technical details about data infrastructure, quality, governance, and capabilities. Responses from this document should be flagged as high-confidence data in the assessment system.

---

### 3. User Data Export Feature
**Added**: 2025-11-01

**Context**: Users need to save, review, and share their assessment progress and results.

**Intent**: Implement export functionality that generates a markdown file containing: (1) a "How to use this document" section explaining the export format and potential uses, and (2) the complete user assessment data in JSON format. This enables portability, backup, and sharing of assessment data.

---

### 4. NDA Generation and Tracking
**Added**: 2025-11-01

**Context**: Users may be hesitant to share sensitive organizational information without confidentiality assurance.

**Intent**: Offer NDA generation early in the conversation flow. Persist both the offer event and user response (accepted/declined/deferred). Inform users they can request the NDA at any point. This builds trust and removes barriers to honest assessment while maintaining audit trail of confidentiality agreements.

---

### 5. User Feedback Collection System
**Added**: 2025-11-01

**Context**: Continuous improvement requires capturing user insights about conversation quality and system usefulness.

**Intent**: Implement feedback mechanism allowing users to provide comments about their experience. When triggered, send email to developer containing user feedback and relevant conversation context. This creates a direct feedback loop for identifying UX issues and improvement opportunities.

---

### 6. User Challenge of Hard-Coded Knowledge (Advanced)
**Added**: 2025-11-01

**Context**: Knowledge graph contains generalized relationships (e.g., "Strong CTO support improves data quality capability by 25%") that may not apply to specific organizational contexts.

**Intent**: Allow users to challenge and override hard-coded assertions with context-specific reasoning. Example: user states "If the CTO is behind this, we can throw money at data quality and solve it fast"—system should accept this as higher-impact override. This personalizes the model to organizational realities while maintaining the base knowledge structure for typical cases.

---

### 7. Entity Relationship Representation Format
**Added**: 2025-11-01

**Context**: Need to capture relationships between factors, capabilities, prerequisites, and archetypes in a format that's both human-readable and LLM-processable for knowledge graph construction.

**Intent**: Implement hybrid JSON-LD + natural language format for relationship definitions. Structure includes: (1) JSON-LD context for graph semantics (@id, @type, relationship types), (2) human_readable section with summary/explanation/examples for documentation, (3) llm_hints section with inference patterns and conversation signals to guide LLM reasoning, (4) quantitative_impact with formulas and confidence calculations. Benefits: aligns with existing JSON taxonomies, self-documenting, knowledge graph ready, enables both conversational inference and structured queries. Alternative considered: markdown tables with YAML frontmatter (more git-friendly but less structured). Recommendation: JSON-LD approach for consistency with existing taxonomy files and better validation support. Include metadata for confidence/provenance tracking and bidirectional query support. Apply to all relationship files: factor_interdependencies.json, factor_capability_mappings.json, prerequisite_factor_mappings.json, factor_archetype_impacts.json. **See: docs/entity_relationship_model.md for complete entity catalog and relationship patterns.**

---

### 8. Output-Centric Factor Model (Exploratory)
**Added**: 2025-11-01

**Context**: Current factor model uses abstract organizational capabilities (e.g., "data_quality = 65"). This lacks specificity for diagnostic questioning and root cause analysis.

**Intent**: Reconceptualize factors as "capability to deliver a VERY specific output" (e.g., "capability to maintain high Sales Forecast quality in CRM by Sales Team during Forecasting Process"). Introduce output dependency edges to enable smart diagnostic questions like "What's preventing [Team X] from maintaining high [Output Y] quality in [System Z] during [Process P]? Is it upstream [Output O] that this relies on, or [Team X] execution failure, or [System Z] limitations?" Benefits: (1) specificity ties factors to concrete deliverables, (2) output dependencies enable root cause tracing, (3) questions become context-specific and actionable, (4) can distinguish upstream dependency problems from execution problems, (5) same capability assessed differently in different contexts. **See: docs/output_centric_factor_model_exploration.md for 10 exploratory diagrams.**

---

### 9. Output-Centric Factor Calculation Weights
**Added**: 2025-11-01

**Context**: In output-centric model, each factor is composite of sub-factors: Dependency Quality (upstream outputs), Team Execution (skills/resources), Process Maturity (design/optimization), System Support (features/integration). Need to determine how to weight these components.

**Intent**: Determine weighting strategy for factor calculation. Questions: (1) What are default weights? (e.g., 0.35, 0.30, 0.20, 0.15 or equal 0.25 each), (2) Do weights vary by output type or AI archetype? (data-heavy projects weight Dependency higher, automation projects weight System higher, augmentation projects weight Team higher), (3) How to learn/adjust weights from real assessments?, (4) Should weights be exposed to users for customization? Starting recommendation: equal weights (0.25 each), collect data from real assessments, iterate based on patterns. Consider archetype-specific weight profiles in v2.

---

### 10. Output-Centric Conversation Design
**Added**: 2025-11-01

**Context**: Output-centric factor model requires conversation flows that naturally elicit output-specific information without interrogation. Need to identify target output, discover Team/Process/System context, assess factor components, and trace upstream dependencies conversationally.

**Intent**: Design conversation patterns for output-centric assessment. Key challenges: (1) Balancing specificity with natural flow, (2) Knowing when to drill down vs. move on, (3) Handling ambiguity in output identification, (4) Managing multi-output scenarios (user wants to improve 3 things). Considerations: progressive disclosure (start broad, get specific), contextual follow-ups based on detected gaps, visual aids (show output dependency graph?), allow user to skip/defer questions. Recommendation: prototype 3-5 conversation flows with different entry points (problem-first, output-first, team-first, system-first, opportunity-first), test with real users, measure completion rate and user satisfaction.

---

### 11. Anti-Abstract Response Pattern
**Added**: 2025-11-02

**Context**: Users may describe problems in abstract or generalized terms that prevent actionable assessment and measurable outcomes.

**Intent**: When user talks about abstract or generalized problems, LLM should respond: "Sorry, I do not do abstract. Let's pick a very concrete example of when this problem manifested, and use that example as a proxy to solve this problem." This system enforces actionability and measurability by grounding all discussions in specific, observable instances rather than theoretical scenarios.

---

### 12. Output-Team-System-Process Constraint Enforcement
**Added**: 2025-11-02

**Context**: The assessment system is designed specifically for internal, data-driven technical pilots that can be expressed within the output-centric model framework.

**Intent**: When the user comes up with something that cannot reasonably be expressed as "an output created by a team in a system in a process", the LLM is free to answer that this problem is probably not a good candidate for an internal, data-driven technical pilot—unless it is rephrased to meet the requirement for that. This maintains system focus on problems where the output-centric factor model can provide value and prevents scope creep into areas where the methodology doesn't apply.

---

### 13. Numbered Question Format for User Responses
**Added**: 2025-11-02

**Context**: When the system asks multiple questions, users need a clear, efficient way to provide structured answers without repeating the questions.

**Intent**: When asking questions, add numeric IDs to them (e.g., "1. What team creates this output?", "2. Which system do they use?"). This allows users to respond concisely in the format "1: answer, 2: answer" without having to retype or reference the questions. This reduces friction, speeds up the conversation, and makes responses more parseable for the LLM.

---

### 14. Professional Reflection Pattern (No Empathy)
**Added**: 2025-11-02

**Context**: When reflecting back what the user said, the system should maintain a professional, analytical tone rather than an empathetic or supportive tone.

**Intent**: Do not empathize ("I understand that must be frustrating..."). Instead, state why the information is relevant in the assessment ("This indicates a bottleneck in Team Execution") and what factors were created or updated from the statement ("Created factor: Sales Forecast quality = ⭐⭐ due to junior team"). This keeps the conversation focused on actionable assessment rather than emotional support, and makes the system's reasoning transparent.

---

### 15. Verifiable Assumptions Export (Technical Questionnaire)
**Added**: 2025-11-04

**Context**: During conversation, the system makes inferences and the user makes assumptions about technical capabilities, data quality, infrastructure, and team skills. Many of these assumptions can be verified by talking to engineers, data teams, or technical leads within the organization.

**Intent**: Track assumptions that are verifiable through internal investigation (as opposed to subjective judgments). Allow selective export of these assumptions in a questionnaire format that the user can share with technical stakeholders (e.g., data engineers, infrastructure leads, ML engineers). The questionnaire should be structured for easy completion by technical staff and easy re-import of answers back into the assessment. This enables the user to validate technical assumptions without requiring technical stakeholders to participate in the full conversational assessment.

**Examples of Verifiable Assumptions:**
- "You have 3 years of historical sales data" → Can ask data engineer to confirm
- "Your CRM has no built-in forecasting tools" → Can ask system admin to verify
- "Data quality in Salesforce is around 30%" → Can ask data team to assess
- "Team lacks ML expertise" → Can ask engineering manager to confirm skill levels

**Export Format Considerations:**
- Questionnaire should be standalone (includes context about why we're asking)
- Questions should be technical but clear (avoid jargon where possible)
- Should support multiple-choice, yes/no, and scale responses
- Should include space for technical notes/clarifications
- Re-import should update evidence levels and confidence scores

---

### 16. 🚨 BLOCKING: Shared Evidence & Factor Representation
**Added**: 2025-11-04  
**Status**: BLOCKING for Increment 1 implementation

**Context**: User statements like "Sales data is bad" can influence multiple outputs (Sales Forecast, Sales Dashboard, Revenue Report, etc.). The evidence is shared, but the output-centric model treats each output's components as independent. This creates a fundamental tension in the domain model.

**The Problem:**
- Evidence about "sales data quality" is **shared** across outputs
- But OutputFactor components are **output-specific** (capability to deliver THIS output)
- Do we duplicate evidence across all affected outputs?
- Or do we have a shared "Factor" concept separate from output-specific components?

**Critical Questions:**
1. Is "sales data quality" a first-class entity in the domain model, or just evidence for output-specific components?
2. How do we model: Evidence → Factor → Component → Output?
3. Where/how do we store evidence to enable:
   - Store once (efficiency)
   - Retrieve at inference runtime for ANY affected output
   - Maintain output-centric purity (MIN() calculation per output)
4. What's the retrieval pattern when user asks "Why is Sales Forecast rated ⭐⭐?"

**Options to Consider:**
- **Option A:** Duplicate evidence across outputs (simple, redundant)
- **Option B:** Shared factor pool (efficient, adds indirection)
- **Option C:** Hybrid - Evidence pool, ratings per-output (complex retrieval)

**Related:** See `/docs/EVIDENCE_HIERARCHY_DISCUSSION.md` for full context

**Decision Required Before:** Implementing Increment 1 data models

---

### 17. LLM Evaluation Metrics and Observability
**Added**: 2025-11-05

**Context**: The system relies heavily on LLM semantic inference across multiple components: output discovery, edge rating inference, evidence tier classification, context extraction, and pilot recommendations. Need quantitative metrics to evaluate LLM performance and prevent regression.

**Intent**: Add LLM evaluation metrics to the unit test suite following observability best practices. Key areas requiring evaluation:

1. **Output Discovery:** Accuracy of matching user descriptions to output catalog (semantic similarity, false positive/negative rates)
2. **Evidence Tier Classification:** Correct classification of user statements into Tiers 1-5 (accuracy, inter-rater reliability with human labelers)
3. **Context Extraction:** Precision/recall of business constraint extraction (budget, timeline, visibility preferences)
4. **Recommendation Quality:** Relevance of pain point → archetype → pilot mappings (reasoning quality assessment)
5. **Feasibility Assessment:** Accuracy of prerequisite gap identification and cost-to-bridge estimation

**Suggested Metrics:**
- Classification metrics: Accuracy, Precision, Recall, F1
- Matching metrics: Semantic similarity scores, ranking quality
- Performance metrics: Latency (p50, p95, p99), token usage, cost per conversation
- Reliability metrics: Error rates, timeout rates, retry counts

**Observability Best Practices:**
- Structured logging with trace IDs (correlate across components)
- Real-time metrics dashboards (Cloud Monitoring/Grafana)
- Alerting on degraded performance thresholds
- A/B testing framework for prompt iterations
- Human-in-the-loop validation sampling (10% of conversations)

**Implementation Phase:** Week 9-10 (Polish & Testing) per Implementation Plan

---
