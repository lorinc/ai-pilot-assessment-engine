# Behavior Analysis Summary

**Date**: 2025-11-05  
**Source**: `freetext_list_of_behaviors.md`

---

## What Was Done

### 1. Extracted Atomic Behaviors (18 total)
Created `atomic_behaviors.yaml` with categorized behavioral patterns:

**Education & Explanation (6 behaviors)**
- B_EXPLAIN_OBJECT_MODEL - Teach simplistic design
- B_EXPLAIN_DATA_PRESERVATION - How data is stored/extracted
- B_BUILD_TRUST_WITH_CAPABILITIES - State system strengths
- B_EXPLAIN_DESIGN_DECISIONS - Defend limitations with rationale
- B_EXPLAIN_INTERNAL_LOGIC - Show MIN calculation, confidence
- B_CITE_UX_PRINCIPLES - Reference principles being applied

**Transparency & Reflection (4 behaviors)**
- B_SHOW_USER_KNOWLEDGE_STATE - What user knows/doesn't know
- B_SHOW_COLLECTED_KNOWLEDGE - Summary of captured data
- B_SHOW_THINKING_PROCESS - Expose internal reasoning (system feature)
- B_SHOW_DATA_NEEDS - Assessment completeness

**Conversation Management (2 behaviors)**
- B_CHAIN_PATTERNS - Check for next pattern after response
- B_AVOID_PATTERN_REPETITION - Track and vary patterns

**Assessment (2 behaviors)**
- B_ASSESS_WITH_PROFESSIONAL_REFLECTION - No empathy, show reasoning
- B_IDENTIFY_LOW_CONFIDENCE_NODES - Surface uncertain assessments

**Survey & Validation (2 behaviors)**
- B_GENERATE_SURVEY - Create questionnaire for validation
- B_PROCESS_SURVEY_RESULTS - Summarize impact, update knowledge

**Trust & Safety (2 behaviors)**
- B_OFFER_NDA - Proactively offer confidentiality
- B_GENERATE_NDA - Create NDA document

**Feedback (1 behavior)**
- B_APPRECIATE_FEEDBACK - Thank and explain value

---

## System Features Identified (6 total)

These require backend implementation, not just LLM patterns:

### Added to TBD.md

**TBD #18: Collapsible Thinking Process Display**
- Show internal reasoning in collapsible box
- Retrieved nodes, confidence calculations, assumptions, updates
- Toggleable per user preference
- Builds trust through transparency

**TBD #19: Survey Generation and Processing System**
- Generate questionnaires for low-confidence topics
- User selects depth (quick/standard/comprehensive)
- Parse uploaded survey results
- Show impact summary, update knowledge base
- Enables async validation with technical stakeholders

**TBD #20: Pattern Chaining and Orchestration Engine**
- Check for new trigger opportunities after each response
- Execute secondary patterns within single response
- Max 2 chained patterns (avoid overwhelming)
- Opportunistic context extraction ("Sprinkle, don't survey")

**TBD #21: Pattern History and Variety Tracking**
- Track last 5-10 patterns used
- Avoid same pattern twice within 5 turns
- Vary response templates for engagement
- Prevents monotonous conversation

**TBD #22: Automated Knowledge Base Updates from External Sources**
- Parse survey results, questionnaires, structured data
- Extract evidence, classify tier, update confidence
- Detect conflicts, generate impact summary
- Enables async collaboration

**TBD #23: Meta-Awareness: System Explains Its Own Design**
- Explain UX principles, design decisions, limitations
- Reference principle taxonomy
- Self-deprecating when appropriate
- Builds trust through transparency

---

## Gaps Identified

### Critical Gaps (Need Immediate Attention)

**1. Error Recovery Behaviors (Missing)**
- How to handle user confusion gracefully
- How to recover from misunderstandings
- How to handle "I don't know" responses
- How to backtrack when wrong path taken

**2. Discovery Behaviors (Partially Covered)**
- How to identify outputs from vague problems ✓ (in triggers)
- How to discover unknown systems ✓ (in triggers)
- How to map dependencies ✓ (in triggers)
- How to handle abstract statements ✓ (in triggers)
- **Missing**: Progressive refinement templates
- **Missing**: Concrete example elicitation

**3. Recommendation Behaviors (Missing)**
- How to generate pilot options
- How to explain feasibility calculations
- How to handle prerequisite gaps
- How to prioritize recommendations

**4. Navigation Behaviors (Partially Covered)**
- How to offer status summaries ✓ (B_SHOW_COLLECTED_KNOWLEDGE)
- How to show progress milestones (partial)
- How to suggest next steps (partial)
- How to handle "where were we?" (missing)

**5. Evidence Quality Behaviors (Missing)**
- How to acknowledge high-quality evidence
- How to probe for better evidence when vague
- How to handle conflicting evidence
- How to synthesize evidence across statements

**6. Scope Management Behaviors (Missing)**
- How to narrow from generic to specific
- How to expand scope when too narrow
- How to handle multi-output scenarios
- How to defer or skip assessments

---

## Areas for Further Elaboration

### High Priority

**1. Error Recovery & Confusion Handling**
- **Why**: Critical for UX, prevents user frustration
- **What**: 5-8 behaviors for graceful error handling
- **Examples**:
  - B_CLARIFY_CONFUSION - "Let me rephrase..."
  - B_OFFER_SKIP - "We can come back to this"
  - B_BACKTRACK - "Let's try a different approach"
  - B_ACKNOWLEDGE_DONT_KNOW - "That's fine, we can estimate"

**2. Progressive Refinement (Discovery)**
- **Why**: Core to output-centric model
- **What**: 5-8 behaviors for vague → concrete
- **Examples**:
  - B_REDIRECT_TO_CONCRETE - "Sorry, I don't do abstract..."
  - B_ELICIT_EXAMPLE - "Give me a specific instance"
  - B_NARROW_SCOPE - "Is this all systems or just X?"
  - B_CONFIRM_OUTPUT - "So you mean Sales Forecast?"

**3. Recommendation Generation**
- **Why**: Final value delivery
- **What**: 5-8 behaviors for pilot recommendations
- **Examples**:
  - B_GENERATE_PILOT_OPTIONS - "Based on bottleneck, here are 3 options"
  - B_EXPLAIN_FEASIBILITY - "45% confidence because..."
  - B_SHOW_PREREQUISITES - "You'd need to improve X first"
  - B_PRIORITIZE_PILOTS - "Quick win vs strategic investment"

### Medium Priority

**4. Evidence Quality Management**
- **Why**: Confidence depends on evidence quality
- **What**: 4-6 behaviors for evidence handling
- **Examples**:
  - B_ACKNOWLEDGE_QUANTIFIED - "That's Tier-1 evidence, high confidence"
  - B_PROBE_FOR_SPECIFICS - "Can you quantify that?"
  - B_RESOLVE_CONFLICT - "Earlier you said X, now Y..."
  - B_SYNTHESIZE_EVIDENCE - "From 3 mentions, I infer..."

**5. Scope Clarification**
- **Why**: Critical for scoped factor instances
- **What**: 4-6 behaviors for scope management
- **Examples**:
  - B_NARROW_SCOPE - "All systems or just Salesforce?"
  - B_EXPAND_SCOPE - "Does this affect other teams?"
  - B_HANDLE_MULTI_OUTPUT - "Let's focus on one output first"
  - B_DEFER_ASSESSMENT - "We can skip this for now"

**6. Navigation & Continuity**
- **Why**: User orientation, session resumption
- **What**: 4-6 behaviors for navigation
- **Examples**:
  - B_SHOW_MILESTONE - "We've completed discovery phase"
  - B_OFFER_NEXT_STEPS - "Continue assessment or evaluate now?"
  - B_RESUME_SESSION - "Last time we discussed X..."
  - B_SHOW_PROGRESS - "3 of 4 components assessed"

---

## Recommendations

### Immediate Actions (This Week)

1. **Expand Behavior Library**
   - Add 5-8 error recovery behaviors
   - Add 5-8 discovery/refinement behaviors
   - Add 5-8 recommendation behaviors
   - Target: 40-50 total atomic behaviors

2. **Create Composition Rules**
   - Map 39 triggers → 40-50 behaviors
   - Define knowledge prerequisites
   - Specify priority rules
   - Document in `composition_rules.yaml`

3. **Generate Initial Patterns**
   - Use composition strategy (see PATTERN_COMPOSITION_STRATEGY.md)
   - Generate 50-100 candidate patterns
   - Human curation to keep best 30-40
   - Document in `patterns/` folders

### Next Week Actions

4. **Write Conversation Scenarios**
   - 5-10 canonical user journeys
   - Cover all phases: discovery → assessment → analysis → recommendations
   - Validate pattern coverage
   - Identify remaining gaps

5. **Build Pattern Matcher (MVP)**
   - Simple dict-based index
   - Trigger detection logic
   - Pattern selection algorithm
   - Test with scenarios

6. **Iterate Based on Scenarios**
   - Add missing behaviors
   - Refine existing behaviors
   - Update composition rules
   - Regenerate patterns

---

## Success Metrics

### Coverage Goals
- ✅ 18 behaviors defined (baseline)
- 🎯 40-50 behaviors (target for MVP)
- 🎯 30-40 patterns generated and curated
- 🎯 5-10 scenarios validated

### Quality Goals
- All behaviors have clear templates
- All behaviors map to triggers
- All behaviors specify constraints
- All behaviors include examples

### System Feature Goals
- 6 features documented in TBD.md ✅
- Requirements specified ✅
- Implementation priority assigned (next step)
- Effort estimates (next step)

---

## Next Steps

1. **Expand behaviors** (Priority 1)
   - Error recovery (5-8)
   - Discovery/refinement (5-8)
   - Recommendations (5-8)

2. **Create composition rules** (Priority 2)
   - Trigger → Behavior mappings
   - Knowledge prerequisites
   - Priority resolution

3. **Generate patterns** (Priority 3)
   - Use composition strategy
   - Human curation
   - Document in YAML

4. **Write scenarios** (Priority 4)
   - 5-10 user journeys
   - Validate coverage
   - Identify gaps

5. **Build pattern matcher** (Priority 5)
   - MVP implementation
   - Test with scenarios
   - Iterate

---

## Files Created/Updated

**Created:**
- `sandbox/conversation_ux_exercise/atomic_behaviors.yaml` - 18 atomic behaviors
- `sandbox/conversation_ux_exercise/BEHAVIOR_ANALYSIS_SUMMARY.md` - This file

**Updated:**
- `docs/1_functional_spec/TBD.md` - Added 6 system features (#18-23)

**Existing:**
- `sandbox/conversation_ux_exercise/atomic_triggers.yaml` - 39 triggers
- `sandbox/conversation_ux_exercise/PATTERN_FORMAT.md` - Pattern template
- `sandbox/conversation_ux_exercise/PATTERN_COMPOSITION_STRATEGY.md` - Composition approach
- `sandbox/conversation_ux_exercise/PATTERN_RUNTIME_ARCHITECTURE.md` - Performance strategy

---

## Summary

**Extracted**: 18 atomic behaviors from freetext  
**Identified**: 6 system features requiring backend work  
**Documented**: 6 critical gaps needing attention  
**Recommended**: 6 areas for further elaboration  

**Status**: Foundation complete, ready to expand behavior library and generate patterns.
