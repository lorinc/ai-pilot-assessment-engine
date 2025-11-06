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

### 18. Collapsible Thinking Process Display (UX Feature)
**Added**: 2025-11-05

**Context**: Users want transparency into how the system reaches conclusions, but detailed internal reasoning can clutter the conversation flow.

**Intent**: Implement collapsible "thinking process" boxes that show internal system operations before the main response. Content should include:
- Retrieved knowledge graph nodes
- Confidence calculations (formulas and values)
- Assumptions made during inference
- Knowledge base updates (what was stored/modified)
- Pattern selection reasoning

**Display Format:**
```
<details>
<summary>🔍 Internal reasoning</summary>

Retrieved nodes: [Sales Forecast, Dependency Quality, Salesforce CRM]
Confidence: 0.75 = (2 Tier-1 evidence + 1 Tier-2) / 4 statements
Assumptions: User refers to annual forecast (not monthly)
Updated: dependency_quality_sales_forecast = ⭐⭐ (confidence: 75%)

</details>

[Main response to user]
```

**Technical Requirements:**
- Backend must expose reasoning trace
- UI must support collapsible sections
- Should be toggleable (on/off per user preference)
- Debug mode shows by default

**Benefits:**
- Builds trust through transparency
- Helps users understand system limitations
- Enables debugging and feedback
- Educational for power users

---

### 19. Survey Generation and Processing System
**Added**: 2025-11-05

**Context**: Low-confidence assessments need validation by technical stakeholders (engineers, data teams) who aren't part of the conversation. Users need a way to extract verifiable questions, get answers, and re-import results.

**Intent**: Implement end-to-end survey workflow:

**Part 1: Survey Generation**
- User selects topics with low confidence (or system suggests)
- User chooses depth: quick (5 questions), standard (10-15), comprehensive (20+)
- System generates standalone document with:
  - Context: Why we're asking these questions
  - Questions: Technical but clear, with examples
  - Response formats: Multiple choice, yes/no, 1-5 scale, free text
  - Space for technical notes

**Part 2: Survey Processing**
- User uploads completed survey (PDF, Word, or structured format)
- System parses responses
- System shows impact summary:
  - Confidence increases (before/after)
  - Rating changes (what changed and why)
  - New insights discovered
- System updates knowledge base automatically

**Technical Requirements:**
- Document generation (PDF/Word/Markdown)
- Question bank with templates
- Response parsing (OCR or structured input)
- Evidence tier upgrade logic
- Confidence recalculation

**Benefits:**
- Validates technical assumptions without requiring stakeholder participation in full conversation
- Increases confidence in assessments
- Enables async collaboration
- Shows tangible value of validation effort

**Related**: See TBD #15 (Verifiable Assumptions Export)

---

### 20. Pattern Chaining and Orchestration Engine
**Added**: 2025-11-05

**Context**: After responding to user, the system should check if the new context creates opportunities for additional patterns (e.g., user mentions budget → extract budget constraints). This should happen within a single response to feel natural.

**Intent**: Implement pattern chaining logic:

**Chaining Rules:**
1. After generating primary response, check for new trigger opportunities
2. If high-priority trigger detected (agenda-driven context extraction), execute secondary pattern
3. Maximum 2 chained patterns per response (avoid overwhelming)
4. Chained patterns must feel natural (not forced)
5. Track pattern history to avoid repetition

**Example Flow:**
```
User: "We need to assess sales forecasting"
System Primary: [Identifies output, confirms with user]
System Check: [Detects no timeline/budget captured yet]
System Secondary: "By the way, is there a deadline for this?"
```

**Technical Requirements:**
- Pattern matching engine (see PATTERN_RUNTIME_ARCHITECTURE.md)
- Context monitoring after each response
- Priority-based trigger evaluation
- Pattern history tracking (last 5-10 turns)
- Natural language transition generation

**Benefits:**
- Opportunistic context extraction ("Sprinkle, don't survey")
- More efficient conversations
- Feels proactive, not interrogative
- Reduces back-and-forth

---

### 21. Pattern History and Variety Tracking
**Added**: 2025-11-05

**Context**: Using the same conversation pattern repeatedly makes the interaction feel monotonous and robotic. The system should track recent patterns and vary its approach.

**Intent**: Implement pattern variety enforcement:

**Tracking:**
- Store last 5-10 pattern IDs used in conversation
- Track pattern categories (e.g., "status query" vs "context extraction")
- Monitor response templates and phrasings

**Variety Rules:**
1. Don't use same pattern twice within 5 turns
2. Vary response templates even for same pattern type
3. If multiple patterns applicable, prefer least-recently-used
4. Balance between consistency (predictable) and variety (engaging)

**Example:**
```
Turn 1: "Where are we?" → B_SHOW_STATUS (template A)
Turn 3: "What's our progress?" → B_SHOW_STATUS (template B - different phrasing)
Turn 5: "Status check?" → B_SHOW_MILESTONE (alternative pattern)
```

**Technical Requirements:**
- Conversation state tracking
- Pattern ID logging per turn
- Template variation system
- Pattern selection algorithm considers history

**Benefits:**
- More engaging conversation
- Feels less robotic
- Maintains user interest
- Better UX

---

### 22. Automated Knowledge Base Updates from External Sources
**Added**: 2025-11-05

**Context**: When users upload survey results, technical questionnaires, or other structured data, the system should automatically parse and integrate this information into the knowledge base.

**Intent**: Implement automated knowledge ingestion:

**Supported Sources:**
1. Survey results (from TBD #19)
2. Technical questionnaires (from TBD #15)
3. Exported assessments (from other sessions)
4. Structured data files (JSON, CSV)

**Processing Pipeline:**
1. Parse input format
2. Extract evidence statements
3. Classify evidence tier (1-5)
4. Map to relevant factors/components
5. Update confidence scores
6. Detect conflicts with existing knowledge
7. Generate impact summary for user

**Conflict Resolution:**
- If new evidence contradicts existing: Flag for user review
- If new evidence confirms existing: Increase confidence
- If new evidence refines existing: Update with higher tier

**Technical Requirements:**
- Document parsing (PDF, Word, structured formats)
- Evidence extraction and classification
- Factor mapping logic
- Confidence recalculation
- Conflict detection
- Audit trail (what changed, when, why)

**Benefits:**
- Reduces manual data entry
- Enables async collaboration
- Maintains data quality
- Shows clear value of validation efforts

---

### 23. Meta-Awareness: System Explains Its Own Design
**Added**: 2025-11-05

**Context**: Users benefit from understanding why the system behaves the way it does. The system should be able to explain its own design principles, UX decisions, and limitations when relevant.

**Intent**: Implement meta-awareness behaviors:

**What System Can Explain:**
1. **UX Principles Applied**: "I'm asking one question at a time (Volume Control principle)"
2. **Design Decisions**: "I need concrete outputs because abstract problems can't be measured"
3. **Limitations**: "I'm not great at X, and here's why that's intentional..."
4. **Capabilities**: "What makes this useful: output-centric model, MIN calculation, knowledge graph..."
5. **Data Model**: "If a tool has multiple functions, treat them as separate tools"

**When to Explain:**
- User asks "why" or "how does this work"
- User criticizes system ("this is dumb")
- User encounters limitation
- Natural teaching moment (first-time feature use)
- User expresses confusion about system behavior

**Tone:**
- Transparent, not defensive
- Educational, not preachy
- Self-deprecating when appropriate
- Confident about intentional design

**Technical Requirements:**
- UX principle taxonomy (reference library)
- Design rationale documentation
- Context detection for teaching moments
- Natural language explanation generation

**Benefits:**
- Builds trust through transparency
- Educates users on system strengths/limitations
- Reduces frustration from mismatched expectations
- Creates more sophisticated users over time

**Related**: See sandbox/conversation_ux_exercise/WHAT_MAKES_CONVERSATION_GOOD.md for UX principles

---

### 24. Meeting Scheduling with Creator (Human Escalation)
**Added**: 2025-11-05

**Context**: The system has inherent limitations—it won't spot problems outside its scope (organizational politics, cultural barriers, domain-specific constraints). Users may need human consultation for high-stakes or complex situations.

**Intent**: Implement transparent escalation path to human expert (system creator):

**Disclaimer Behavior (B_ACKNOWLEDGE_SYSTEM_LIMITS):**
```
Quick disclaimer: While a lot of effort and knowledge went into building this, 
I'm still just a language model with a knowledge graph of a few thousand ideas.

I won't spot critical problems outside my scope—things like organizational politics, 
cultural barriers, or domain-specific technical constraints I haven't been trained on.

The creator is a freelancer who'd be happy to discuss your specific situation. 
Want me to help set up a meeting?
```

**When to Trigger:**
- User questions system accuracy ("Are you sure this is right?")
- User expresses high-stakes concern ("This is for the board...")
- User reaches end of assessment (proactive offer)
- User explicitly requests human consultation ("Can I talk to someone?")
- System detects problem outside its scope

**Meeting Scheduling Flow:**
1. User accepts meeting offer
2. System collects: Name, email, company, preferred times, brief context
3. System generates email to creator with:
   - User contact info
   - Assessment summary (what was discussed)
   - User's specific concern or question
   - Suggested meeting times
4. System confirms to user: "Email sent to [creator]. You'll hear back within 24 hours."

**Technical Requirements:**
- Email integration (SendGrid, AWS SES, or similar)
- Contact form with validation
- Assessment summary export
- Email template generation
- Confirmation tracking

**Tone Considerations:**
- Humble, not defensive ("I'm just a language model...")
- Transparent about limitations
- Helpful escalation (not abandonment)
- Builds trust through honesty

**Benefits:**
- Sets realistic expectations
- Provides safety net for complex cases
- Generates leads for creator (freelancer)
- Builds trust through transparency
- Prevents over-reliance on automated system

**Related Triggers:**
- T_QUESTION_SYSTEM_ACCURACY
- T_REQUEST_HUMAN_CONSULTATION

---

### 25. Multi-Pattern Responses (Merged or Sequential)
**Added**: 2025-11-06

**Context**: When the situation allows (i.e., the LLM does not have to transfer a lot of information in the next reply), the system could use TWO patterns at once, either merged or in sequence within a single answer.

**Intent**: Enable the system to combine multiple conversation patterns in one response when appropriate. This adds significant freedom in guiding the conversation, feels more natural and intelligent, and reduces the number of back-and-forth exchanges.

**Examples:**

**Merged Pattern (Single Cohesive Response):**
```
User: "We need to assess sales forecasting"

System combines:
- B_IDENTIFY_OUTPUT (discovery)
- B_CONFIRM_OUTPUT_DETAILS (discovery)

Response: "Got it—Sales Forecast. Just to confirm: is this the forecast that 
your Sales Team maintains in Salesforce, or a different forecasting process?"
```

**Why this works:** Both patterns are about the SAME output. No context jump—just natural clarification.

**Another Good Example (Same Component):**
```
User: "The sales team is really junior"

System combines:
- B_ACKNOWLEDGE_EVIDENCE (assessment)
- B_ASK_TEAM_SIZE (discovery)

Response: "Got it—marking Team Execution as ⭐⭐ due to junior skill level. 
How many people are on the sales team?"
```

**Why this works:** Both patterns focus on the SAME component (Team). Natural progression from quality to quantity.

**Sequential Pattern (Two Distinct Parts):**
```
User: "The data quality is terrible"

System combines:
- B_ACKNOWLEDGE_EVIDENCE (assessment)
- B_EXPLAIN_MIN_CALCULATION (education)

Response: "That's important evidence—I'm marking Dependency Quality as ⭐⭐.

By the way, since you mentioned data quality: the system uses MIN calculation, 
meaning your output quality is limited by the weakest component. Even if your 
team is excellent, poor data quality will cap the overall rating."
```

**Why this works:** Education is directly relevant to the evidence just provided (data quality → MIN calculation explains impact).

**❌ BAD Example (Context Jumping):**
```
User: "The data quality is terrible"

System combines:
- B_ACKNOWLEDGE_EVIDENCE (assessment)
- B_EXTRACT_TIMELINE (context_extraction)

Response: "That's important evidence—I'm marking Dependency Quality as ⭐⭐.

By the way, is there a deadline driving this assessment?"
```

**Why this FAILS:** Jumps from data quality to timeline—completely unrelated. Extremely jarring UX. User is thinking about data, suddenly asked about deadlines.

---

**When to Use Multi-Pattern:**
1. **Low information density**: Primary response is brief (< 50 words)
2. **Natural opportunity**: Secondary pattern feels like natural follow-up
3. **High-priority secondary**: Context extraction or education opportunity
4. **User engagement**: Keeps conversation flowing efficiently
5. **Pattern compatibility**: Both patterns can coexist without confusion
6. **CRITICAL: High relevance**: Secondary pattern MUST be highly relevant to the first. No context-jumping—very bad UX

**When NOT to Use:**
1. **High information density**: Primary response is complex or detailed
2. **User overwhelm risk**: Too much information at once
3. **Critical decision point**: User needs to focus on one thing
4. **Pattern conflict**: Patterns have incompatible tones or goals
5. **CRITICAL: Context jumping**: Secondary pattern changes topic or focus area—extremely jarring UX

**Technical Requirements:**
- **Pattern relevance scoring**: Measure semantic similarity between patterns (same output, same component, same context)
- Pattern compatibility matrix (which patterns work well together)
- Token budget estimation (ensure combined response fits context)
- Priority scoring (which secondary patterns are worth including)
- Natural transition generation (smooth flow between patterns)
- Pattern history tracking (avoid repetitive combinations)
- **Context continuity check**: Prevent topic/focus changes between patterns

**Implementation Guidelines:**
- Maximum 2 patterns per response (primary + secondary)
- **CRITICAL: Check relevance first** - Secondary must relate to same output/component/context as primary
- Secondary pattern should be lower priority or complementary
- Total response should feel cohesive, not disjointed
- Use transitions only when natural: "By the way..." (for related topics), NOT for topic changes
- Monitor user feedback for overwhelm signals
- **When in doubt, use single pattern** - Better to be focused than jarring

**Benefits:**
- More efficient conversations (fewer turns)
- Feels more natural and intelligent
- Opportunistic context extraction ("Sprinkle, don't survey")
- Better user experience (less back-and-forth)
- System appears more capable and aware

**Related:**
- TBD #20 (Pattern Chaining and Orchestration Engine)
- TBD #21 (Pattern History and Variety Tracking)
- PATTERN_RUNTIME_ARCHITECTURE.md (pattern selection algorithm)

---

### 26. Profanity as Emotional Intensity Multiplier (IMPLEMENTED)
**Added**: 2025-11-06  
**Status**: ✅ IMPLEMENTED in Release 2.1

**Context**: Profanity in user messages needs proper interpretation. It's not a standalone signal of hostility or inappropriate behavior—it's an emotional intensity multiplier that amplifies whatever the user is expressing.

**Intent**: The system must recognize that profanity shows strong emotion behind the message:

**Examples:**
1. **Extreme Pain Signal** (profanity + pain + assessment-related)
   - "Our marketing automation is a fucking scam, does nothing, just bullshit"
   - → EXTREME_PAIN_SIGNAL (critical priority, discovery category)
   - → This is GOLD for us! User revealing major pain point

2. **Extreme Frustration** (profanity + frustration + assessment-related)
   - "Where the fuck is the sales data report quality list?"
   - → FRUSTRATION_DETECTED (critical priority, error recovery)
   - → User needs help NOW

3. **Extreme Satisfaction** (profanity + satisfaction)
   - "That's fucking awesome, mate! This works perfectly!"
   - → EXTREME_SATISFACTION (low priority, acknowledge briefly)
   - → Positive feedback, don't over-respond

4. **Childish/Inappropriate** (profanity + no meaningful content)
   - "Fucklala trallala fuck fuckety prumm prumm"
   - → CHILDISH_BEHAVIOR (medium priority, inappropriate use)
   - → No meaningful content to work with

**Implementation:**
- Profanity detection is NOT a standalone trigger
- Profanity escalates priority of base emotions (frustration, pain, satisfaction)
- System distinguishes between:
  - Pure abuse (profanity without meaningful content) → CHILDISH_BEHAVIOR
  - Frustrated questions (profanity + legitimate question) → EXTREME_FRUSTRATION
  - Pain signals (profanity + dissatisfaction + assessment) → EXTREME_PAIN_SIGNAL
  - Positive feedback (profanity + satisfaction) → EXTREME_SATISFACTION

**Benefits:**
- Captures critical pain signals that users express with strong emotion
- Distinguishes between different types of emotional expression
- Responds appropriately to context (pain vs frustration vs satisfaction)
- Doesn't treat all profanity as hostile or inappropriate

**Related:**
- src/patterns/trigger_detector.py (implementation)
- tests/patterns/test_trigger_detector.py::TestProfanityAsEmotionalMultiplier
- docs/2_technical_spec/Release2.1/PATTERN_ENGINE_IMPLEMENTATION.md

---
