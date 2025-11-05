# Dense Knowledge Dimensions Format (For Review)

**Instructions**: Review and modify. I'll parse into full YAML.

**Note**: Knowledge dimensions track what the system knows about the user's context and what the user knows about the system.

---

## SYSTEM KNOWLEDGE (What System Knows About User's Context)

| Dimension | Description | Values | Updated By |
|---|---|---|---|
| outputs_identified | Outputs discovered | List of output IDs with names | Discovery behaviors |
| outputs_assessed | Assessment completeness per output | {output_id: {components: 3, confidence: "medium"}} | Assessment behaviors |
| bottlenecks_identified | Known bottlenecks per output | {output_id: [component_ids]} | Analysis behaviors |
| recommendations_shown | Recommendations presented | {output_id: [pilot_ids]} | Recommendation behaviors |
| user_domain | User's business domain | "sales", "finance", "operations", "unknown" | Discovery behaviors |
| user_role | User's role/perspective | "manager", "analyst", "executive", "unknown" | Discovery behaviors |
| evidence_quality | Overall evidence quality | "high", "medium", "low" | Evidence quality behaviors |
| scope_clarity | How clear scope is | "clear", "ambiguous", "conflicting" | Scope management behaviors |
| active_outputs | Currently active outputs | List of output IDs | Navigation behaviors |
| session_history | Previous sessions | {session_id: summary} | Session management |
| assessment_depth_ratio | Depth vs breadth indicator | avg_components_per_output / total_outputs | Navigation, strategic guidance |
| sparse_knowledge_flag | Multiple outputs, shallow assessment | true/false (true if 3+ outputs, all <2 components) | Navigation behaviors |

---

## USER KNOWLEDGE (What User Knows About System)

| Dimension | Description | Values | Updated By |
|---|---|---|---|
| understands_object_model | User knows output-centric model | true/false | Education behaviors |
| understands_min_calculation | User knows MIN() logic | true/false | Education behaviors |
| understands_evidence_tiers | User knows evidence quality system | true/false | Education behaviors |
| understands_scope_importance | User knows scope matters | true/false | Education behaviors |
| understands_bottleneck_concept | User knows bottleneck analysis | true/false | Education behaviors |
| has_seen_recommendations | User has seen pilot recommendations | true/false | Recommendation behaviors |
| has_used_system_before | Returning user | true/false | Session management |
| comfort_level | User's comfort with system | "confused", "learning", "comfortable", "expert" | Error recovery, education |
| preferred_interaction_style | How user likes to interact | "detailed", "concise", "guided", "exploratory" | Adaptive from patterns |

---

## CONVERSATION STATE

| Dimension | Description | Values | Updated By |
|---|---|---|---|
| current_focus | What we're currently doing | "discovering_output", "assessing_component", "analyzing", "recommending" | All behaviors |
| last_question_answered | Did user answer last question | true/false | Error recovery |
| pattern_history | Last 5 patterns used | List of pattern IDs | Pattern engine |
| frustration_level | User frustration indicator | 0.0-1.0 (0=calm, 1=very frustrated) | Error recovery behaviors |
| confusion_level | User confusion indicator | 0.0-1.0 (0=clear, 1=very confused) | Error recovery behaviors |
| engagement_level | User engagement | 0.0-1.0 (0=disengaged, 1=highly engaged) | All behaviors |
| turns_since_progress | Turns without useful data | Integer count | Error recovery |
| needs_navigation | User seems lost | true/false | Navigation behaviors |

---

## QUALITY METRICS

| Dimension | Description | Values | Updated By |
|---|---|---|---|
| tier1_evidence_count | High-quality evidence statements | Integer count | Evidence quality behaviors |
| tier5_evidence_count | Low-quality evidence statements | Integer count | Evidence quality behaviors |
| confidence_by_output | Confidence level per output | {output_id: "low"/"medium"/"high"} | Assessment behaviors |
| missing_components | Components not yet assessed | {output_id: [component_names]} | Assessment behaviors |
| scope_ambiguities | Unresolved scope questions | List of ambiguous statements | Scope management |
| contradictions_resolved | Conflicting evidence resolved | Integer count | Error recovery |

---

## COMPOSITION RULES

### Knowledge Updates in Patterns

**Pattern Structure**:
```yaml
pattern:
  id: PATTERN_001
  triggers: [T_MENTION_OUTPUT]
  behavior: B_REDIRECT_TO_CONCRETE
  knowledge_updates:
    system_knowledge:
      - dimension: outputs_identified
        action: append
        value: "{extracted_output_id}"
      - dimension: scope_clarity
        action: set
        value: "ambiguous"
    user_knowledge:
      - dimension: understands_object_model
        action: set_if_demonstrated
        condition: "user_uses_output_terminology"
    conversation_state:
      - dimension: current_focus
        action: set
        value: "discovering_output"
```

### Knowledge-Based Pattern Selection

**Patterns can require knowledge conditions**:
```yaml
pattern:
  id: PATTERN_050
  triggers: [T_ASSESSMENT_SUFFICIENT]
  behavior: B_OFFER_RECOMMENDATIONS_AT_CONFIDENCE
  requires:
    system_knowledge:
      - outputs_assessed[output_id].components >= 3
    user_knowledge:
      - understands_bottleneck_concept == true  # Only if user understands
```

### Knowledge Decay

**Some knowledge decays over time**:
- `frustration_level`: Decays by 0.1 per turn if no new frustration signals
- `confusion_level`: Decays by 0.15 per turn if no new confusion signals
- `engagement_level`: Decays by 0.05 per turn if no engagement signals

---

## STATS

**Total Dimensions**: 30
- System Knowledge: 12 (added depth ratio, sparse knowledge flag)
- User Knowledge: 9
- Conversation State: 8
- Quality Metrics: 6

**Update Frequency**:
- Every turn: conversation_state (8 dimensions)
- On specific events: system_knowledge, user_knowledge
- Accumulated: quality_metrics

**Purpose**:
- Enable context-aware pattern selection
- Track conversation quality
- Adapt to user understanding
- Prevent repetition and frustration
