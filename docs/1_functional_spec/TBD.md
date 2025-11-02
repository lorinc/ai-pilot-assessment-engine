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
