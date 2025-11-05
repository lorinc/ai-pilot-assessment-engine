# Dense Trigger Format (For Review)

**Instructions**: Review and modify. I'll parse into full YAML.

---

## USER EXPLICIT TRIGGERS

| ID | Description | Example Phrases | Situation Affinity |
|---|---|---|---|
| T_REQUEST_HELP | User explicitly asks for help | "help", "what should I do?", "I'm stuck" | navigation: 0.8, education: 0.6 |
| T_REQUEST_EXPLANATION | User asks how something works | "how does this work?", "explain", "what is X?" | education: 0.9, discovery: 0.3 |
| T_REQUEST_RECOMMENDATIONS | User asks for pilot suggestions | "what should I build?", "recommend", "suggestions?" | recommendation: 0.9, analysis: 0.5 |
| T_REQUEST_PROGRESS | User asks about status | "where are we?", "progress?", "how much done?" | navigation: 0.9 |
| T_REQUEST_EXPORT | User wants to save/export | "export", "save", "download", "report" | navigation: 0.7 |
| T_PROVIDE_FEEDBACK | User gives feedback | "this is wrong", "actually...", "let me clarify" | error_recovery: 0.6, assessment: 0.4 |
| T_RESTART_ASSESSMENT | User wants to start over | "restart", "start over", "new assessment" | navigation: 0.8 |
| T_SKIP_QUESTION | User wants to skip | "skip", "I don't know", "pass", "later" | error_recovery: 0.5, navigation: 0.5 |

---

## USER IMPLICIT TRIGGERS

| ID | Description | Signals | Situation Affinity |
|---|---|---|---|
| T_MENTION_OUTPUT | User describes an output | Mentions deliverable, report, dashboard, forecast | discovery: 0.9, assessment: 0.3 |
| T_MENTION_PROBLEM | User describes a problem | "issue", "problem", "broken", "doesn't work" | discovery: 0.7, assessment: 0.5 |
| T_MENTION_TEAM | User mentions team/people | Team names, roles, "we", "they" | discovery: 0.6, scope_management: 0.4 |
| T_MENTION_SYSTEM | User mentions system/tool | System names, "Excel", "Salesforce", "our tool" | discovery: 0.6, scope_management: 0.4 |
| T_MENTION_PROCESS | User mentions process | Process names, "workflow", "procedure" | discovery: 0.6, scope_management: 0.4 |
| T_PROVIDE_RATING | User gives quality assessment | Numbers, stars, "good", "bad", "terrible", "excellent" | assessment: 0.9 |
| T_PROVIDE_EVIDENCE | User gives specific data | Numbers, percentages, "30% of the time", "last week" | assessment: 0.8, evidence_quality: 0.7 |
| T_PROVIDE_EXAMPLE | User gives concrete example | "for example", "like when", "last time" | assessment: 0.7, discovery: 0.5 |
| T_EXPRESS_UNCERTAINTY | User shows uncertainty | "maybe", "I think", "not sure", "probably" | error_recovery: 0.6, evidence_quality: 0.5 |
| T_EXPRESS_FRUSTRATION | User shows frustration | "this is stupid", "doesn't make sense", "annoying" | error_recovery: 0.9 |
| T_EXPRESS_CONFUSION | User shows confusion | "confused", "lost", "don't understand", "what?" | error_recovery: 0.9, education: 0.6 |
| T_SCOPE_AMBIGUITY | Statement lacks scope | "data quality is bad" (all systems? one system?) | scope_management: 0.9, discovery: 0.4 |
| T_ABSTRACT_STATEMENT | Vague/generic statement | "things are broken", "quality is low" (no specifics) | discovery: 0.8, error_recovery: 0.3 |
| T_MULTIPLE_OUTPUTS | User mentions multiple outputs | Lists several deliverables | scope_management: 0.8, navigation: 0.5 |

---

## SYSTEM PROACTIVE TRIGGERS

| ID | Description | Condition | Situation Affinity |
|---|---|---|---|
| T_OUTPUT_IDENTIFIED | Output successfully identified | Discovery engine found output with >70% confidence | assessment: 0.7, navigation: 0.5 |
| T_ASSESSMENT_SUFFICIENT | Enough data for recommendations | 3+ components assessed OR user requested recommendations | recommendation: 0.8, analysis: 0.6 |
| T_BOTTLENECK_IDENTIFIED | Bottleneck analysis complete | MIN calculation done, bottleneck found | recommendation: 0.9, analysis: 0.5 |
| T_LOW_CONFIDENCE_DATA | Evidence quality is low | Multiple Tier 4-5 evidence statements | evidence_quality: 0.8, assessment: 0.4 |
| T_CONFLICTING_EVIDENCE | Contradictory statements detected | Current statement contradicts previous | error_recovery: 0.7, evidence_quality: 0.6 |
| T_MILESTONE_REACHED | Natural break point | Output fully assessed, recommendations shown | navigation: 0.8 |
| T_CONTEXT_THIN | Entity lacks description | System/team/process identified but no context | discovery: 0.7, assessment: 0.5 |
| T_MULTIPLE_OUTPUTS_ACTIVE | Multiple outputs in progress | User working on 2+ outputs | scope_management: 0.8, navigation: 0.7 |
| T_SESSION_RESUME | Returning user | User has previous session data | navigation: 0.7, education: 0.3 |
| T_FIRST_TIME_USER | New user detected | No previous sessions | education: 0.9, discovery: 0.5 |
| T_SPARSE_KNOWLEDGE_DETECTED | Multiple outputs but shallow assessment | 3+ outputs identified, all with <2 components assessed | navigation: 0.8, recommendation: 0.6, scope_management: 0.5 |
| T_BREADTH_OVER_DEPTH | User exploring many outputs superficially | 5+ outputs mentioned, none fully assessed | navigation: 0.9, discovery: 0.4 |

---

## SYSTEM REACTIVE TRIGGERS

| ID | Description | Response To | Situation Affinity |
|---|---|---|---|
| T_PATTERN_REPETITION | Same pattern triggered 3+ times | Avoid repetition, try different approach | error_recovery: 0.6, navigation: 0.4 |
| T_USER_STUCK | No progress in 3+ turns | User not providing useful data | error_recovery: 0.8, navigation: 0.5 |
| T_RAPID_CORRECTIONS | User corrects multiple times | User says "no, actually..." repeatedly | error_recovery: 0.7, assessment: 0.5 |
| T_QUESTION_IGNORED | User didn't answer question | User changed topic or gave unrelated response | error_recovery: 0.6, navigation: 0.4 |
| T_SCOPE_CLARIFIED | User provided scope signal | User said "all systems" or "just Salesforce" | scope_management: 0.7, assessment: 0.5 |
| T_UNDERSTANDING_DEMONSTRATED | User uses system terminology | User correctly uses "bottleneck", "MIN", etc. | education: 0.3, assessment: 0.7 |

---

## STATS

**Total Triggers**: 40
- User Explicit: 8
- User Implicit: 14
- System Proactive: 12 (added sparse knowledge detection)
- System Reactive: 6

**Situation Dimensions Covered**: All 8
- Discovery: 18 triggers
- Education: 8 triggers
- Assessment: 16 triggers
- Analysis: 3 triggers
- Recommendation: 4 triggers
- Navigation: 12 triggers
- Error Recovery: 13 triggers
- Scope Management: 8 triggers
- Evidence Quality: 4 triggers
