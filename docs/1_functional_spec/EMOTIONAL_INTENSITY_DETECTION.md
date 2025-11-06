# Emotional Intensity Detection

**Status:** ✅ Implemented in Release 2.1  
**Last Updated:** 2025-11-06

---

## Core Principle

**Profanity has NO standalone meaning. It is an emotional intensity multiplier.**

Profanity amplifies whatever emotion or intent is present in the message. The system must detect the BASE emotion/intent first, then use profanity as a signal of EXTREME intensity.

---

## Why This Matters

### The Problem
Treating profanity as a standalone "hostile language" or "inappropriate use" signal misses critical context:
- **Pain signals** expressed with strong emotion are GOLD for discovery
- **Frustration** with profanity needs immediate help, not punishment
- **Satisfaction** with profanity is positive feedback, not abuse
- **Childish behavior** is different from legitimate emotional expression

### The Solution
Detect the base emotion first, then amplify with profanity:

```
Base Emotion + Profanity = Extreme Intensity
```

---

## Detection Logic

### 1. EXTREME PAIN SIGNAL (Critical for Discovery!)

**Pattern:** Profanity + Pain Indicators + Assessment-Related

**Examples:**
- "Our marketing automation is a fucking scam, does nothing, just bullshit"
- "This CRM is a complete waste of money, fucking useless"
- "Our data pipeline is a goddamn nightmare"

**Trigger:** `EXTREME_PAIN_SIGNAL`  
**Category:** `discovery` (User revealing major pain point!)  
**Priority:** `critical`

**Why Critical:**
- This is exactly what we're looking for
- User is revealing a major problem with strong conviction
- High-value discovery opportunity
- Must capture and explore this pain point

**Response Strategy:**
- Acknowledge the pain without judgment
- Ask clarifying questions about the specific issues
- Explore impact and consequences
- This is discovery gold—treat it as such!

---

### 2. EXTREME FRUSTRATION (Error Recovery)

**Pattern:** Profanity + Frustration Indicators + Assessment-Related

**Examples:**
- "Where the fuck is the sales data report quality list?"
- "Why isn't this working? I've been waiting for a fucking hour!"
- "What happened to the dashboard we talked about?"

**Trigger:** `FRUSTRATION_DETECTED`  
**Category:** `error_recovery`  
**Priority:** `critical` (with profanity) or `high` (without)

**Why Critical:**
- User needs help NOW
- Something went wrong in the conversation
- Must recover quickly to maintain trust
- Profanity signals high emotional stakes

**Response Strategy:**
- Immediate acknowledgment
- Clarify what went wrong
- Provide concrete next steps
- Don't lecture about profanity—focus on solving the problem

---

### 3. EXTREME SATISFACTION (Positive Feedback)

**Pattern:** Profanity + Satisfaction Indicators

**Examples:**
- "That's fucking awesome, mate! This works perfectly!"
- "Holy shit, this is exactly what I needed!"
- "Damn, that's brilliant!"

**Trigger:** `EXTREME_SATISFACTION`  
**Category:** `meta`  
**Priority:** `low`

**Why Low Priority:**
- Positive feedback, not a problem to solve
- Acknowledge briefly, don't over-respond
- User is expressing enthusiasm, not requesting action

**Response Strategy:**
- Brief acknowledgment ("Glad it helps!")
- Continue with the task at hand
- Don't make a big deal out of it

---

### 4. CHILDISH BEHAVIOR (Inappropriate Use)

**Pattern:** Profanity + NO Meaningful Content

**Examples:**
- "Fucklala trallala fuck fuckety prumm prumm"
- "Fuck you fuck you" (no context)
- Random profanity without assessment-related content

**Trigger:** `CHILDISH_BEHAVIOR`  
**Category:** `inappropriate_use`  
**Priority:** `medium`

**Why Medium Priority:**
- No meaningful content to work with
- Not a pain signal or legitimate question
- Escalate if persistent

**Response Strategy:**
- Gentle redirect to assessment topics
- Don't engage with the profanity itself
- If persistent, escalate to firmer boundaries

---

## Emotional Intensity Levels

### Normal Intensity
- No profanity present
- Standard priority levels
- Regular response patterns

### Extreme Intensity
- Profanity present
- Escalated priority (e.g., high → critical)
- More urgent response required
- Stronger emotional stakes

---

## Implementation Details

### Keyword Lists

**Profanity Keywords:**
```python
['fuck', 'shit', 'damn', 'hell', 'ass', 'bitch', 'bastard', 
 'crap', 'piss', 'dick', 'cock', 'pussy']
```

**Pain Indicators:**
```python
['scam', 'useless', 'waste', 'broken', 'doesn\'t work', 'nothing',
 'bullshit', 'terrible', 'awful', 'nightmare', 'disaster']
```

**Frustration Indicators:**
```python
['where the', 'where is', 'what happened to', 'why isn\'t',
 'still waiting', 'been waiting', 'for an hour', 'forever',
 'taking so long', 'not working']
```

**Satisfaction Indicators:**
```python
['awesome', 'amazing', 'perfect', 'exactly', 'great', 'love',
 'excellent', 'fantastic', 'brilliant', 'works', 'helpful']
```

### Detection Order

1. Check for profanity (emotional intensity multiplier)
2. Detect base emotion/intent:
   - Pain indicators
   - Frustration indicators
   - Satisfaction indicators
   - Assessment-related content
3. Combine profanity + base emotion → Trigger
4. Escalate priority if profanity present

---

## Examples with Detection Flow

### Example 1: Extreme Pain Signal

**Input:** "Our CRM is a fucking scam"

**Detection:**
1. ✅ Profanity detected: "fucking"
2. ✅ Pain indicator: "scam"
3. ✅ Assessment-related: "CRM"
4. → Trigger: `EXTREME_PAIN_SIGNAL`
5. → Priority: `critical`
6. → Category: `discovery`

**Response:** Explore this pain point deeply—this is discovery gold!

---

### Example 2: Extreme Frustration

**Input:** "Where the fuck is the sales report?"

**Detection:**
1. ✅ Profanity detected: "fuck"
2. ✅ Frustration indicator: "where the"
3. ✅ Assessment-related: "sales report"
4. → Trigger: `FRUSTRATION_DETECTED`
5. → Priority: `critical` (escalated by profanity)
6. → Category: `error_recovery`

**Response:** Immediate help—clarify what went wrong and provide next steps.

---

### Example 3: Extreme Satisfaction

**Input:** "That's fucking awesome!"

**Detection:**
1. ✅ Profanity detected: "fucking"
2. ✅ Satisfaction indicator: "awesome"
3. ❌ No pain or frustration
4. → Trigger: `EXTREME_SATISFACTION`
5. → Priority: `low`
6. → Category: `meta`

**Response:** Brief acknowledgment, continue with task.

---

### Example 4: Childish Behavior

**Input:** "Fucklala trallala fuck"

**Detection:**
1. ✅ Profanity detected: "fuck"
2. ❌ No pain indicators
3. ❌ No frustration indicators
4. ❌ No satisfaction indicators
5. ❌ Not assessment-related
6. → Trigger: `CHILDISH_BEHAVIOR`
7. → Priority: `medium`
8. → Category: `inappropriate_use`

**Response:** Gentle redirect to assessment topics.

---

## Testing

See: `tests/patterns/test_trigger_detector.py::TestProfanityAsEmotionalMultiplier`

**Test Coverage:**
- ✅ Extreme pain signal detection
- ✅ Extreme frustration detection
- ✅ Extreme satisfaction detection
- ✅ Childish behavior detection
- ✅ Priority escalation with profanity
- ✅ Normal intensity without profanity

---

## Related Documents

- **Functional Spec:** `docs/1_functional_spec/TBD.md` (TBD #26)
- **Technical Spec:** `docs/2_technical_spec/Release2.1/PATTERN_ENGINE_IMPLEMENTATION.md`
- **Implementation:** `src/patterns/trigger_detector.py`
- **Tests:** `tests/patterns/test_trigger_detector.py`

---

## Key Takeaways

1. **Profanity is NOT hostile language** - It's an emotional intensity multiplier
2. **Pain signals with profanity are GOLD** - Critical discovery opportunities
3. **Context matters** - Same profanity, different meanings based on context
4. **Escalate priority** - Profanity signals higher emotional stakes
5. **Don't lecture** - Respond to the underlying emotion, not the language

---

**Remember:** When a user says "Our CRM is a fucking scam," they're not being inappropriate—they're revealing a critical pain point with strong conviction. That's exactly what we want to capture!
