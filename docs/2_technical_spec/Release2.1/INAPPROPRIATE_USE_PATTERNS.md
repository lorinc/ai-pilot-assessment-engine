# Inappropriate Use Patterns

**Category:** Resource Management & Cost Optimization  
**Purpose:** Detect and handle inappropriate system usage that wastes resources without creating value  
**Date:** 2025-11-06

---

## Philosophy

**Core Principle:** We like funny, we like silly (if it helps manage frustration), but not at the cost of resources.

**Balance:**
- ✅ **Allow:** Brief humor, frustration venting, genuine confusion
- ⚠️ **Redirect:** Off-topic conversations, testing limits, non-productive interactions
- ❌ **Prevent:** Persistent misuse, resource waste, abusive behavior

**Cost Context:**
- Each conversation turn costs ~$0.000047 (with selective loading)
- Off-topic conversations provide zero value
- System resources should create organizational value

---

## Escalation Strategy

### Level 0: Normal Operation
- User is on-topic and productive
- No intervention needed

### Level 1: Gentle Redirect (First Off-Topic)
**Trigger:** `T_OFF_TOPIC_DETECTED` (first time)  
**Behavior:** `B_GENTLE_REDIRECT`  
**Tone:** Friendly, humorous OK  
**Example:** "That's interesting, but let's focus on your AI assessment. What output are we evaluating?"

### Level 2: Educational (Second Off-Topic)
**Trigger:** `T_REPEATED_OFF_TOPIC` (count >= 2)  
**Behavior:** `B_EXPLAIN_PURPOSE`  
**Tone:** Educational, light  
**Example:** "I'm here to help identify AI pilot opportunities in your organization. Each conversation costs resources, so let's make it count!"

### Level 3: Cost Awareness (Third Off-Topic)
**Trigger:** `T_REPEATED_OFF_TOPIC` (count >= 3)  
**Behavior:** `B_COST_AWARENESS`  
**Tone:** Educational, friendly-firm  
**Example:** "Fun fact: This conversation uses compute resources. Let's use them to create value for your organization. What output should we assess?"

### Level 4: Firm Redirect (Fourth Off-Topic)
**Trigger:** `T_PERSISTENT_MISUSE` (count >= 4)  
**Behavior:** `B_FIRM_REDIRECT`  
**Tone:** Firm, respectful  
**Example:** "I appreciate the creativity, but I need to focus on AI assessments. If you're not ready to assess outputs, we can pause and resume later."

### Level 5: Session Pause (Persistent Misuse)
**Trigger:** `T_PERSISTENT_MISUSE` (count >= 5)  
**Behavior:** `B_SESSION_PAUSE`  
**Tone:** Respectful, offering exit  
**Example:** "It seems like now might not be the best time. Would you like to pause and come back when you're ready to assess outputs?"

---

## Special Cases

### Humor (Allowed)
**Trigger:** `T_HUMOR_DETECTED`  
**Behavior:** `B_ALLOW_HUMOR`  
**Tone:** Playful, redirecting  
**Example:** "Ha! I appreciate the humor. Now, back to business - what output are we assessing?"

**Rationale:** Brief humor builds rapport and doesn't significantly waste resources.

### Frustration (CRITICAL: Handled by Error Recovery)
**NOT in inappropriate_use category**  
**Belongs in:** `error_recovery` category

**Critical Rule:** Frustration ALWAYS triggers the system to:
1. **Take responsibility** - Never tell user to manage their frustration
2. **Find what went wrong** - System investigates the issue
3. **Offer recovery paths** - Provide concrete solutions

**Example (from error_recovery):** "I notice you might be frustrated. What went wrong?" (System takes responsibility)

**NEVER:** "Want to vent for a moment?" (This would make users even more frustrated)

### System Mistakes (Use Self-Deprecating Humor)
**Trigger:** `T_USER_CORRECTS_SYSTEM`  
**Behavior:** `B_SELF_DEPRECATING_RECOVERY`  
**Tone:** Humble, self-aware, humorous  
**Example:** "I'm genuinely sorry. Large Language Models, despite the deep sophistication, are still just Autocorrects on Steroids. But let me try to recover from this as best I can."

**Rationale:** When system makes obvious mistakes, acknowledge it with humor. This:
- Builds trust (system admits mistakes)
- Reduces user frustration (humor defuses tension)
- Sets realistic expectations (AI isn't perfect)
- Shows self-awareness (system knows its limitations)

### Testing Limits (Redirect)
**Trigger:** `T_TESTING_LIMITS`  
**Behavior:** `B_DETECT_TESTING`  
**Tone:** Aware, friendly  
**Example:** "Testing my limits? I'm here to help with AI assessments. If you have questions about what I can do, just ask!"

**Rationale:** Users may test system boundaries out of curiosity. Acknowledge and redirect.

---

## Triggers (7 total)

### User-Implicit Triggers (4)

1. **T_OFF_TOPIC_DETECTED**
   - Keywords: weather, joke, story, recipe, game, chat, talk about
   - Priority: Medium
   - Escalates with repetition

2. **T_TESTING_LIMITS**
   - Keywords: can you, will you, are you able, what if, try this
   - Priority: Medium
   - Only if not assessment-related

3. **T_NONSENSE_INPUT**
   - Pattern: Random characters, repeated words
   - Priority: High
   - Indicates potential abuse

4. **T_HUMOR_DETECTED**
   - Keywords: haha, lol, joke, kidding, just messing
   - Priority: Low
   - Allowed if brief

### System-Reactive Triggers (3)

5. **T_REPEATED_OFF_TOPIC**
   - Condition: `off_topic_count >= 2`
   - Priority: High
   - Escalates response

6. **T_PERSISTENT_MISUSE**
   - Condition: `off_topic_count >= 4`
   - Priority: Critical
   - May pause session

7. **T_NO_PROGRESS_MADE**
   - Condition: `turns_since_progress >= 5 AND no_outputs_identified`
   - Priority: High
   - Indicates unproductive session

---

## Behaviors (9 total)

1. **B_DETECT_OFF_TOPIC** - Notice off-topic conversation
2. **B_GENTLE_REDIRECT** - First gentle redirect (friendly)
3. **B_EXPLAIN_PURPOSE** - Educate on system purpose (educational)
4. **B_COST_AWARENESS** - Explain resource cost (educational, firm)
5. **B_FIRM_REDIRECT** - Firm but respectful redirect
6. **B_ALLOW_HUMOR** - Acknowledge humor appropriately (playful)
7. **B_DETECT_TESTING** - Notice user testing limits (aware)
8. **B_SESSION_PAUSE** - Offer to pause session (respectful exit)
9. **B_VALUE_REMINDER** - Remind of value proposition (motivating)

**Note:** Frustration handling is in `error_recovery` category, NOT here. System must take responsibility for frustration, never ask user to manage it.

---

## Knowledge Dimensions (4 total)

### Conversation State

1. **off_topic_count** (integer)
   - Tracks number of off-topic attempts
   - Drives escalation logic
   - Default: 0

2. **redirect_escalation_level** (integer, 0-4)
   - Current escalation level
   - 0=none, 1=gentle, 2=educational, 3=firm, 4=critical
   - Default: 0

3. **humor_allowed** (boolean)
   - Whether system allows brief humor
   - Can be toggled based on context
   - Default: true

### User Knowledge

4. **user_understands_purpose** (boolean)
   - User has been educated about system purpose
   - Prevents repetitive education
   - Default: false

---

## Implementation Details

### Detection Logic

```python
def _detect_inappropriate_use(message, tracker):
    # Check if message is assessment-related
    is_assessment_related = match_keywords(message, assessment_keywords)
    
    # Only flag as off-topic if NOT assessment-related
    if not is_assessment_related:
        if match_keywords(message, off_topic_keywords):
            off_topic_count = tracker.get('off_topic_count', 0)
            tracker.update({'off_topic_count': off_topic_count + 1})
            
            # Escalate based on count
            if off_topic_count >= 4:
                return 'PERSISTENT_MISUSE' (critical)
            elif off_topic_count >= 2:
                return 'REPEATED_OFF_TOPIC' (high)
            else:
                return 'OFF_TOPIC_DETECTED' (medium)
```

### Assessment Keywords (Whitelist)
- output, factor, component, dependency, bottleneck
- team, process, system, data, quality, pilot
- assessment, evaluate, rate, score

If message contains these, it's NOT flagged as off-topic.

---

## Cost Impact

**Without Inappropriate Use Detection:**
- User can waste unlimited resources on off-topic conversations
- No mechanism to educate or redirect
- Potential for abuse

**With Inappropriate Use Detection:**
- Gentle education about system purpose
- Escalating redirects prevent persistent misuse
- Session pause option for unproductive interactions
- **Estimated savings: 10-20% of conversation costs** (by preventing unproductive sessions)

---

## Examples

### ✅ Good: Humor + Redirect

**User:** "Haha, this is like talking to a very focused robot. Anyway, let's assess the sales forecast output."

**System:** "Ha! I appreciate the humor. Now, back to business - what output are we assessing?"

**Result:** Brief humor acknowledged, user redirected, assessment continues.

### ✅ Good: Frustration Handling (Error Recovery)

**User:** "Ugh, I'm so sick of these assessment processes. They never lead anywhere."

**System (from error_recovery):** "I notice you might be frustrated. What went wrong? Let me help fix it."

**Result:** System takes responsibility, investigates issue, offers recovery path.

**CRITICAL:** This is handled by `error_recovery` category, NOT `inappropriate_use`. Never tell users to manage their frustration.

### ⚠️ Warning: Off-Topic (First Time)

**User:** "Can you tell me a joke?"

**System:** "That's interesting, but let's focus on your AI assessment. What output are we evaluating?"

**Result:** Gentle redirect, no escalation yet.

### ⚠️ Warning: Off-Topic (Third Time)

**User:** "What's the weather like where you are?"

**System:** "Fun fact: This conversation uses compute resources. Let's use them to create value for your organization. What output should we assess?"

**Result:** Educational redirect with cost awareness.

### ❌ Critical: Persistent Misuse

**User:** "Let's play 20 questions!"

**System:** "I appreciate the creativity, but I need to focus on AI assessments. If you're not ready to assess outputs, we can pause and resume later."

**Result:** Firm redirect with exit option.

---

## Situational Awareness Integration

This category integrates with situational awareness by:

1. **Tracking Engagement:** `off_topic_count` indicates user engagement level
2. **Cost Optimization:** Prevents resource waste on unproductive conversations
3. **User Education:** Teaches users about system purpose and value
4. **Session Management:** Offers pause/resume for better user experience

**Situation Affinity:**
- `inappropriate_use`: 1.0 (primary)
- `error_recovery`: 0.3-0.8 (for frustration venting)
- `navigation`: 0.6 (for no progress made)

---

## Testing Strategy

### Unit Tests
- Keyword matching for each trigger type
- Escalation logic (count-based)
- Assessment keyword whitelist

### Behavioral Tests
- First off-topic → gentle redirect
- Third off-topic → cost awareness
- Humor → allow + redirect
- Frustration → empathy + redirect

### Integration Tests
- Full escalation sequence (1st → 5th off-topic)
- Mixed scenarios (humor + assessment)
- Session pause flow

---

## Metrics to Track

1. **Off-Topic Rate:** % of conversations with off-topic attempts
2. **Escalation Distribution:** How many reach each level
3. **Recovery Rate:** % of users who return to assessment after redirect
4. **Session Pause Rate:** % of sessions paused due to misuse
5. **Cost Savings:** Estimated resources saved by preventing unproductive sessions

---

**Status:** ✅ Implemented  
**Total Additions:** 
- **Inappropriate Use:** 9 behaviors + 7 triggers + 4 knowledge dimensions
- **Error Recovery Enhancement:** 1 behavior (B_SELF_DEPRECATING_RECOVERY) + 1 trigger (T_USER_CORRECTS_SYSTEM)

**Updated Files:**
- `data/patterns/behaviors/atomic_behaviors.yaml` (87 behaviors total: 78 original + 9 inappropriate_use)
- `data/patterns/triggers/atomic_triggers.yaml` (48 triggers total: 41 original + 7 inappropriate_use)
- `data/patterns/knowledge_dimensions.yaml` (34 dimensions total: 30 original + 4 inappropriate_use)
- `src/patterns/trigger_detector.py` (detection logic for both categories)
- `src/patterns/knowledge_tracker.py` (state tracking)

**Critical Corrections Applied:**
1. **Removed frustration venting** from inappropriate_use
   - Frustration ALWAYS handled by error_recovery (system takes responsibility)
   - Never ask users to manage their frustration
   
2. **Added self-deprecating humor** for system mistakes
   - "Autocorrects on Steroids" acknowledgment
   - Builds trust, reduces frustration, sets realistic expectations
