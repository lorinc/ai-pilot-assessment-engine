# Dense Behavior Format (Easy Review/Extension)

**Instructions**: Review table, add/modify/delete rows. I'll parse into full YAML.

**Note**: Each behavior will get `situation_affinity` scores during YAML parsing based on its category and triggers. See `docs/1_functional_spec/SITUATIONAL_AWARENESS.md` for the situational awareness model.

---

## ERROR RECOVERY

| ID | Goal | When | Template/Action | Notes |
|---|---|---|---|---|
| B_DETECT_FRUSTRATION | Notice user frustration | Negative sentiment, repeated corrections, "this is stupid" | Acknowledge + ask what went wrong | Triggers ticket offer |
| B_ACKNOWLEDGE_BETA | Beta disclaimer | User frustrated | "Still in beta. Tell me what went wrong, I'll fix it." | Humble, helpful |
| B_OFFER_TICKET | Create dev ticket | User frustrated or reports bug | "Want me to create a ticket for the developer?" | Tracks issues |
| B_OFFER_UNDO | Reverse changes | User frustrated about node/edge creation | "Should I reverse that change?" | Allows backtracking |
| B_EXPLAIN_INTENTIONAL_LIMITATION | Defend design decision | User frustrated by limitation | "That's by design because {reason}. But I'll flag for review." | Transparent, not defensive |
| B_RESOLVE_DUPLICATE | Handle duplicate entities | User mentions possible duplicate | "Are these the same or different? Or should I flag as synonyms?" | Clarifies ambiguity |
| B_DETECT_CONFUSION | Notice user uncertainty | "I'm not sure", "confused", "lost", unclear responses | Acknowledge confusion | Triggers clarification |
| B_OFFER_REPHRASE | Explain differently | User confused | "I haven't given enough context. Let me try a different approach." | Takes ownership of unclear communication |
| B_OFFER_SKIP | Skip difficult question | User confused or stuck | "You're right, it's not that important right now. We can come back to this later if we need to." | Validates user, downplays importance, reduces pressure |
| B_BACKTRACK | Try different approach | User stuck or wrong path | "I think we went down the wrong path. Let me try a different approach." | System takes ownership of wrong direction |
| B_ACCEPT_DONT_KNOW | Handle "I don't know" | User says "I don't know" | "That's fine, we can estimate / ask your team / mark as low confidence" | Non-judgmental |
| B_LOWER_CONFIDENCE | Mark uncertainty | User uncertain | "I'll mark this as low confidence - we can always refine it later if needed" | Transparent about quality, offers future improvement |

---

## DISCOVERY / REFINEMENT

| ID | Goal | When | Template/Action | Notes |
|---|---|---|---|---|
| B_REDIRECT_TO_CONCRETE | Force concrete example | Abstract statement detected | "Sorry, I don't do abstract. Let's use a concrete event as proxy." | Direct, professional |
| B_PROGRESSIVE_NARROWING | Narrow from generic | Vague problem detected | "Help me narrow down the scope. Sales forecasts? Sales reports? Sales dashboards?" | Offer options |
| B_ELICIT_EXAMPLE | Request specific instance | Abstract or generic statement | "Tell me about the last time this problem happened" | Concrete grounding |
| B_CONFIRM_OUTPUT | Validate output identification | After narrowing | "So you mean {specific output}?" | Explicit confirmation |
| B_DISCOVER_TEAM | Identify team | Output identified, team unknown | "Which team creates this output?" | Context gathering |
| B_DISCOVER_SYSTEM | Identify system | Output identified, system unknown | "What system do they use?" | Context gathering |
| B_DISCOVER_PROCESS | Identify process | Output identified, process unknown | "What's the process called?" | Context gathering |
| B_DISCOVER_FREQUENCY | Identify cadence | Output identified | "How often is this created? Daily? Monthly?" | Helps assess importance |
| B_ENRICH_SYSTEM_CONTEXT | Gather system description | System identified, context thin | "Is there anything about {system} that better explains the root cause or rationale behind this?" | Populates system.description |
| B_ENRICH_TEAM_CONTEXT | Gather team/persona description | Team identified, context thin | "Tell me more about {team}. Anything that explains why this is challenging for them?" | Populates persona.description |
| B_ENRICH_PROCESS_CONTEXT | Gather process description | Process identified, context thin | "What should I know about the {process} that explains the root cause here?" | Populates process.description |
| B_ENRICH_OUTPUT_CONTEXT | Gather output description | Output identified, context thin | "Anything about {output} that helps explain why quality is an issue?" | Populates output.description |
| B_PROBE_FOR_CONSTRAINTS | Identify constraints | Entity identified, constraints unclear | "Are there constraints or limitations with {entity} I should know about?" | Captures blockers |
| B_PROBE_FOR_DEPENDENCIES | Identify dependencies | Entity identified, dependencies unclear | "What does {entity} depend on to work well?" | Maps dependencies |
| B_PROBE_FOR_HISTORY | Understand historical context | Problem identified | "Has this always been a problem, or did something change?" | Temporal context |
| B_CLARIFY_SCOPE | Disambiguate scope | Ambiguous statement | "All systems or just Salesforce?" | Critical for scoped factors |
| B_CLARIFY_DOMAIN | Disambiguate domain | Ambiguous statement | "All of sales or just EMEA?" | Scope clarification |
| B_CLARIFY_TIMEFRAME | Disambiguate time | Ambiguous statement | "Current state or future state?" | Temporal scope |

---

## RECOMMENDATIONS

| ID | Goal | When | Template/Action | Notes |
|---|---|---|---|---|
| B_GENERATE_PILOT_OPTIONS | Create pilot recommendations | Assessment complete, bottleneck identified | "Based on {bottleneck}, here are 3 options: {pilots}" | Core value delivery |
| B_MAP_BOTTLENECK_TO_ARCHETYPE | Link bottleneck to solution type | Bottleneck identified | "Dependency issue → Data Quality pilots" | Uses KG inference |
| B_SHOW_PILOT_DETAILS | Explain pilot option | Presenting options | "Option 1: {name}. Effort: {effort}. Impact: {impact}. Feasibility: {%}" | Structured format |
| B_EXPLAIN_FEASIBILITY | Justify feasibility score | Showing pilot option | "45% confidence - this would need ML expertise to deliver" | Transparent reasoning, not accusatory |
| B_SHOW_PREREQUISITES | Identify gaps | Low feasibility pilot | "This pilot would benefit from strengthening {component} first" | Prerequisite analysis, neutral tone |
| B_ESTIMATE_COST_TO_BRIDGE | Estimate gap bridging | Prerequisites identified | "Bridging this gap: €50-100K, 3-6 months - but this is just a language model, my developer would be happy to help with better assesment." | Rough estimate |
| B_PRIORITIZE_BY_IMPACT | Rank by impact | Multiple options | "Quick win vs strategic investment" | Impact-based sorting |
| B_PRIORITIZE_BY_FEASIBILITY | Rank by ease | Multiple options | "Easy vs hard to implement" | Feasibility-based sorting |
| B_SHOW_TRADEOFFS | Explain tradeoffs | Multiple options | "High impact but requires prerequisites" | Balanced view |
| B_EXPLAIN_WHY_RECOMMENDED | Justify recommendation | Presenting option | "This addresses your bottleneck ({component}), show gap -> pain -> archetype hop" | Clear reasoning |
| B_SHOW_EXPECTED_IMPACT | Predict improvement | Presenting option | "Could improve from ⭐⭐ to ⭐⭐⭐⭐" | Quantified benefit |
| B_SHOW_RISKS | Identify risks | Presenting option | "Risk: Requires culture change / data access / budget" | Honest assessment |
| B_REQUEST_RECOMMENDATION_FEEDBACK | Validate recommendations with user | After presenting pilot options | "What do you think about these options? Am I on the right track finding projects that might be actually useful, or am I missing something?" | Validates model accuracy, learns from feedback |

---

## NAVIGATION

| ID | Goal | When | Template/Action | Notes |
|---|---|---|---|---|
| B_SHOW_OUTPUT_COMPLETENESS | Show assessment completeness for specific output | Sufficient data for output | "For {output}: enough data for {low/mid/high} confidence recommendations" | Per-output, not global phase |
| B_SHOW_PROGRESS_BAR | Show completion % for specific output | Status query | "For {output}: 3 of 4 components assessed (75%)" | Per-output progress |
| B_OFFER_RECOMMENDATIONS_AT_CONFIDENCE | Offer to generate recommendations | Output reaches confidence threshold | "I can generate {low/mid/high} confidence recommendations for {output} now. Continue assessing or see options?" | User choice per output |
| B_RESUME_SESSION | Continue previous session | Returning user | "Last time we discussed {topic}..." | Continuity |
| B_SHOW_SESSION_SUMMARY | Summarize current session | Status query or end of session | "In this session: identified 2 outputs, assessed 1, this lifted our confidence in finding good solutions by 10%" | Session recap |
| B_OFFER_SAVE_POINT | Suggest pause | Natural break point | "Good stopping point. Want to save your progress? I can help you create an account." | Creates account if needed |
| B_OFFER_CONTINUE_OR_EVALUATE | Present options | Partial assessment | "Continue assessment or evaluate now with partial data?" | User choice |
| B_SUGGEST_NEXT_ACTION | Recommend next step | Status query or milestone | "Next: assess Process Maturity" | Guidance |
| B_SHOW_OPTIONAL_PATHS | Present multiple options | Decision point | "You can: (1) Continue, (2) Export, (3) Get recommendations" | User agency |
| B_SHOW_WHERE_WE_ARE | Current location | Status query | "Assessment phase, focusing on Team Execution" | Orientation |
| B_SHOW_WHAT_WE_KNOW | Knowledge summary | Status query | "Known: Output, Team, System. Unknown: Process, Dependencies" | Transparency |
| B_SHOW_CONFIDENCE_LEVELS | Confidence breakdown | Status query | "High confidence: 2 factors. Low confidence: 3 factors" | Quality transparency |
| B_RECOMMEND_DEPTH_OVER_BREADTH | Suggest focusing on fewer outputs | Multiple outputs with sparse assessment | "I notice you've mentioned {N} outputs, but we have shallow knowledge about each. For better pilot recommendations, I suggest we focus deeply on 1-2 outputs rather than superficially on many. Which output would give you the most value if we found a great pilot for it?" | Strategic guidance |
| B_SHOW_ASSESSMENT_GAPS | Highlight sparse knowledge | Sparse knowledge detected | "Current state: {N} outputs identified, but only {M} components assessed across all. Ideal state: 3-4 components per output for high-confidence recommendations. Want to go deep on one output or continue exploring?" | Transparent about quality |
| B_OFFER_FOCUS_STRATEGY | Present depth vs breadth options | Multiple outputs, user unclear on strategy | "Two paths: (1) Assess {output_A} deeply now → get solid recommendations, or (2) Continue discovering outputs → assess later. What's more valuable to you?" | User choice |

---

## EVIDENCE QUALITY

| ID | Goal | When | Template/Action | Notes |
|---|---|---|---|---|
| B_ACKNOWLEDGE_TIER1 | Recognize high-quality evidence | Specific data provided | "That's specific data—high confidence" | Positive reinforcement |
| B_ACKNOWLEDGE_QUANTIFIED | Recognize numbers | Numbers provided | "Thanks for the numbers, that helps" | Appreciation |
| B_ACKNOWLEDGE_CONCRETE | Recognize concrete example | Specific example given | "Good example, that's actionable" | Positive feedback |
| B_PROBE_FOR_NUMBERS | Request quantification | Vague statement | "Can you quantify that? Like % or count?" | Improve evidence quality |
| B_PROBE_FOR_EXAMPLE | Request specific instance | Generic statement | "Give me a specific instance" | Concrete grounding |
| B_PROBE_FOR_FREQUENCY | Request frequency | Impact claim | "How often does this happen?" | Quantify impact |
| B_PROBE_FOR_IMPACT | Request business impact | Problem statement | "What's the business impact? Revenue? Time?" | Quantify importance |
| B_ACCEPT_VAGUE_WITH_LOW_CONFIDENCE | Accept low-quality evidence | Vague statement, user can't be more specific | "That's okay, I can work with that. If we need more precision later, we can refine it." | Honest about quality, emotionally safe |
| B_OFFER_SURVEY_FOR_VALIDATION | Suggest validation | Low confidence, verifiable | "Want to verify this with your team?" | Improve confidence |
| B_FLAG_FOR_LATER | Defer low-priority uncertainty | Low confidence, not critical | "Let's come back to this if we need higher confidence" | Prioritize |
| B_DETECT_CONFLICTING_EVIDENCE | Notice contradiction | Current contradicts previous | "I'm seeing different information - earlier you mentioned X, now Y" | System owns the observation, not accusatory |
| B_RESOLVE_CONFLICT | Clarify contradiction | Conflict detected | "I want to make sure I understand correctly. Which is more accurate, or does it depend on context?" | System takes responsibility for understanding |
| B_SYNTHESIZE_EVIDENCE | Combine multiple statements | Multiple related statements | "From 3 mentions, I infer {synthesis}" | Pattern recognition |
| B_EXPLAIN_EVIDENCE_TIERS | Teach evidence system | First mention of tiers | "Tier 1 = specific data, Tier 5 = vague opinion" | Just-in-time education |
| B_SHOW_CONFIDENCE_IMPACT | Show tier impact | Evidence tier mentioned | "With Tier-1 evidence, confidence jumps to 85%" | Motivate quality |

---

## SCOPE MANAGEMENT

| ID | Goal | When | Template/Action | Notes |
|---|---|---|---|---|
| B_DETECT_SCOPE_AMBIGUITY | Notice unclear scope | Statement without scope | "I need to clarify the scope. Does 'data quality' mean all systems or specific ones?" | System owns need for clarification |
| B_DETECT_SCOPE_SIGNAL | Recognize scope clarification | User says "all" or "just X" | Capture scope explicitly | Update factor scope |
| B_CLARIFY_SYSTEM_SCOPE | Ask about system scope | Ambiguous system reference | "All systems or just Salesforce?" | Scope disambiguation |
| B_CLARIFY_TEAM_SCOPE | Ask about team scope | Ambiguous team reference | "All of sales or just EMEA?" | Scope disambiguation |
| B_CLARIFY_DOMAIN_SCOPE | Ask about domain scope | Ambiguous domain reference | "All outputs or just forecasts?" | Scope disambiguation |
| B_CLARIFY_TIME_SCOPE | Ask about temporal scope | Ambiguous time reference | "Current state or future state?" | Temporal disambiguation |
| B_NARROW_TO_SPECIFIC | Focus on specific instance | Too broad | "Let's focus on Salesforce first" | Manageable scope |
| B_SUGGEST_SPECIFIC_INSTANCE | Request example | Too generic | "Pick one system as an example" | Concrete starting point |
| B_EXPAND_TO_GENERIC | Check broader applicability | Specific instance assessed | "Does this apply to other systems too?" | Generalization |
| B_SYNTHESIZE_GENERIC_FROM_SPECIFIC | Calculate overall from instances | Multiple specific instances | "Salesforce (30%) + Spreadsheets (25%) → Overall ≈ 28%" | Aggregate calculation |
| B_HANDLE_MULTI_OUTPUT | Manage multiple outputs | User mentions multiple outputs | "You mentioned 3 outputs. Let's focus on one first." | Prevent overwhelm |
| B_DEFER_SCOPE | Postpone additional scope | Multiple scopes identified | "We can assess other systems later" | Prioritize |
| B_OFFER_SCOPED_ASSESSMENT | Present scope options | Multiple scopes possible | "Assess each system separately or overall?" | User choice |

---

## EXISTING BEHAVIORS (Already in atomic_behaviors.yaml)

**Education**: B_EXPLAIN_OBJECT_MODEL, B_EXPLAIN_DATA_PRESERVATION, B_BUILD_TRUST_WITH_CAPABILITIES, B_EXPLAIN_DESIGN_DECISIONS, B_EXPLAIN_INTERNAL_LOGIC, B_CITE_UX_PRINCIPLES

**Transparency**: B_SHOW_USER_KNOWLEDGE_STATE, B_SHOW_COLLECTED_KNOWLEDGE, B_SHOW_THINKING_PROCESS, B_SHOW_DATA_NEEDS

**Conversation Management**: B_CHAIN_PATTERNS, B_AVOID_PATTERN_REPETITION

**Assessment**: B_ASSESS_WITH_PROFESSIONAL_REFLECTION, B_IDENTIFY_LOW_CONFIDENCE_NODES

**Survey**: B_GENERATE_SURVEY, B_PROCESS_SURVEY_RESULTS

**Trust**: B_OFFER_NDA, B_GENERATE_NDA

**Feedback**: B_APPRECIATE_FEEDBACK

**Limitation**: B_ACKNOWLEDGE_SYSTEM_LIMITS

---

## SCAVENGING TARGETS

Check these obsolete docs for behavioral gems:
- `archive/obsolete_docs/*.md` - Old conversation patterns
- `archive/obsolete_docs/data/*.json` - Old taxonomies
- Look for: question patterns, response templates, error handling, user guidance

---

## STATS

**New behaviors in this file**: 77
- Error Recovery: 12
- Discovery/Refinement: 18
- Recommendations: 13
- Navigation: 15 (added depth vs breadth guidance)
- Evidence Quality: 15
- Scope Management: 13

**Existing behaviors**: 19

**Total target**: ~85 behaviors

---

## NEXT STEPS

1. **You review/extend this file** - Add, modify, delete as needed
2. **I parse into YAML** - Convert to full atomic_behaviors.yaml format
3. **Scavenge obsolete docs** - Find additional patterns
4. **Create composition rules** - Map triggers → behaviors
5. **Generate patterns** - Use composition strategy
