# Review Checklist

**Purpose**: Quick guide for reviewing the dense format files before YAML generation.

---

## What to Review

### 1. `triggers_dense_format.md` (38 triggers)

**Check**:
- [ ] Are all user intents covered? (explicit requests, implicit signals)
- [ ] Are system triggers appropriate? (proactive vs reactive)
- [ ] Do situation affinities make sense?
- [ ] Any missing triggers from your experience?
- [ ] Any redundant triggers to merge?

**Key Questions**:
- Can the system detect when user is stuck/frustrated/confused?
- Can the system detect scope ambiguity?
- Can the system detect when to offer recommendations?

---

### 2. `behaviors_dense_format.md` (74 behaviors)

**Check**:
- [ ] Are templates clear and actionable?
- [ ] Do behaviors match your UX vision?
- [ ] Are context enrichment behaviors sufficient?
- [ ] Are error recovery behaviors comprehensive?
- [ ] Any behaviors that feel wrong or missing?

**Key Questions**:
- Will these behaviors preserve user agency?
- Will error recovery spike appropriately?
- Will education be withheld until relevant?
- Will scope be clarified before proceeding?

**Special Attention**:
- **Discovery/Refinement** (18): Do context enrichment behaviors populate entity descriptions well?
- **Error Recovery** (12): Will frustrated/confused users be handled gracefully?
- **Recommendations** (13): Is feedback validation included?
- **Navigation** (12): Is per-output completeness shown (not global phases)?

---

### 3. `knowledge_dimensions_dense_format.md` (28 dimensions)

**Check**:
- [ ] Does system knowledge capture enough context?
- [ ] Does user knowledge track understanding appropriately?
- [ ] Are conversation state dimensions sufficient?
- [ ] Are quality metrics useful?
- [ ] Any missing dimensions?

**Key Questions**:
- Can the system adapt to user knowledge level?
- Can the system detect when user is lost?
- Can the system track evidence quality?
- Can the system prevent repetition?

---

### 4. `composition_rules_dense_format.md` (8 rules)

**Check**:
- [ ] Are trigger-behavior mappings correct?
- [ ] Is priority hierarchy appropriate?
- [ ] Are anti-patterns comprehensive?
- [ ] Are cooldown periods reasonable?
- [ ] Do examples make sense?

**Key Questions**:
- Will error recovery always win priority?
- Will education be deprioritized appropriately?
- Will repetition be avoided?
- Will patterns chain logically?

---

## Common Issues to Watch For

### ❌ Anti-Patterns

1. **Educating frustrated users**
   - Check: B_EXPLAIN_* should never trigger when frustration_level > 0.5
   
2. **Repeating patterns too soon**
   - Check: Cooldown periods prevent repetition
   
3. **Ignoring scope ambiguity**
   - Check: Scope management has high priority
   
4. **Forcing linear progression**
   - Check: No "phase complete" or "must finish X before Y" logic
   
5. **Asking for data from confused users**
   - Check: Error recovery > assessment in priority

### ✅ Good Patterns

1. **Error recovery spikes**
   - Frustration/confusion → immediate priority shift
   
2. **Context enrichment**
   - System/team/process descriptions populated naturally
   
3. **Per-output state**
   - No global "we've completed discovery" messages
   
4. **Adaptive education**
   - Only when user demonstrates readiness
   
5. **Evidence quality awareness**
   - Probe for better evidence, accept vague with low confidence

---

## Quick Edits

### To Add a Trigger
```markdown
| T_NEW_TRIGGER | Description | Signals/Examples | Situation Affinity |
```

### To Add a Behavior
```markdown
| B_NEW_BEHAVIOR | Goal | When | Template/Action | Notes |
```

### To Add a Knowledge Dimension
```markdown
| new_dimension | Description | Values | Updated By |
```

### To Add a Composition Rule
Add to appropriate section in `composition_rules_dense_format.md`

---

## Approval Process

### Option 1: Approve as-is
**Action**: Reply "Approved - generate YAML"
**Result**: I'll generate all 5 YAML files immediately

### Option 2: Request changes
**Action**: Specify changes in any dense format file
**Result**: I'll update and re-summarize

### Option 3: Iterate
**Action**: Edit files directly, let me know when done
**Result**: I'll generate YAML from your edited versions

---

## After Approval

### I Will Generate:

1. **`atomic_triggers.yaml`**
   - Full trigger definitions
   - Situation affinities
   - Detection patterns
   - Examples

2. **`atomic_behaviors.yaml`** (updated)
   - Merge with existing 19 behaviors
   - Add 55 new behaviors
   - Full templates and constraints
   - Situation affinities

3. **`knowledge_dimensions.yaml`**
   - All 28 dimensions
   - Update rules
   - Decay rates
   - Default values

4. **`composition_rules.yaml`**
   - All 8 rules
   - Trigger-behavior mappings
   - Anti-patterns
   - Priority hierarchy
   - Examples

5. **`pattern_index.yaml`** (generated)
   - Top 100 composed patterns
   - Ranked by usefulness
   - Ready for Phase 1 implementation

---

## Estimated Timeline

**If approved now**:
- YAML generation: 1-2 hours
- Validation: 30 min
- Documentation: 30 min
- **Total**: ~3 hours

**Then you can**:
- Start Phase 2.5 implementation
- Test patterns with semantic evaluation
- Iterate based on real conversations

---

## Questions to Consider

1. **Are there specific conversation scenarios you want to ensure are covered?**
   - Example: "User mentions 5 outputs at once"
   - Example: "User gives conflicting evidence"

2. **Are there specific UX failures you want to prevent?**
   - Example: "System repeats same question 3 times"
   - Example: "System educates when user is frustrated"

3. **Are there specific behaviors you want to prioritize?**
   - Example: "Always clarify scope before assessing"
   - Example: "Always offer to skip when user stuck"

4. **Any domain-specific patterns to add?**
   - Example: "Recognize sales terminology"
   - Example: "Handle finance-specific outputs"

---

**Ready for your review!** 🎯

Check the 4 dense format files, make any changes, then let me know to proceed with YAML generation.
