# Document Coherence Fixes

## Summary of Changes

All three core documents are now coherent. Here's what was fixed:

---

## 1. Confidence Display Language ✅

### Fixed Contradiction
**Before:** Section 3 said "never show decimals to user," but Section 8 showed "75% confident"

**After:** Clarified two different contexts:
- **User input:** Simple language only (unlikely / 50/50 / likely / fairly sure)
- **System output:** Can show percentages (70% confident, 75% confident)

### Updated in: `user_interaction_guideline.md`
```
System asks user: "How sure are you? (unlikely / 50/50 / likely / fairly sure)"
User responds: Simple language (no numbers)
System shows status: Can use percentages ("70% confident")
```

---

## 2. User Confidence ≠ Factor Score ✅

### Added Clarification
**Problem:** User says "fairly sure we have great data engineers" but evidence suggests otherwise

**Solution:** Explicitly documented that user's confidence in their statement doesn't override cumulative evidence

### Updated in: `user_interaction_guideline.md`
```
Important: User's confidence in their statement ≠ factor score
- User says "fairly sure we have great data engineers"
- But if evidence suggests no QA, no formal ETL → data_engineering score stays low
- LLM can explain: "On our scale, these factors suggest lower readiness than you might expect"
```

---

## 3. Options Generation Clarity ✅

### Fixed Ambiguity
**Before:** Unclear when system generates options (always? never? sometimes?)

**After:** Explicit triggers for different contexts:

### Updated in: `user_interaction_guideline.md`
```
Project Ideas (3-5 options):
- Trigger: User asks "What AI projects could we do?"
- Format: 3-5 project ideas based on assessed factors
- Interaction: User picks one to refine, or asks for more

Next Steps (3-5 options):
- Trigger: User asks "What should we do next?"
- Format: 3-5 concrete next actions with ROI
- Interaction: User picks, or explores freely

Status Response (2-3 options):
- Trigger: User asks "Where are we?" or finishes a topic
- Format: 2-3 brief next options
- Interaction: User picks or ignores
```

---

## 4. Removed Decision Tracking ✅

### Dropped Formal Decision Flow
**Before:** Section 7 had "Decision Record" with Go/No-Go/Try-N-weeks

**After:** Replaced with project evaluation snapshots (no execution tracking)

### Updated in: `user_interaction_guideline.md`
```
Section 7: Project Evaluation (not decision tracking)

System produces:
- Project evaluation with confidence score
- Gaps and recommendations
- Timestamped snapshot

System does NOT track:
- "Did you do it?"
- "How did it go?"
- Execution outcomes

System DOES offer:
- "Want to re-evaluate this project later?"
- Evaluation history (confidence changes over time)
```

### Updated in: `exploratory_assessment_architecture.md`
```
TBD: Project Evaluation Persistence
- Store evaluations as timestamped snapshots
- Track confidence changes over time
- No decision tracking—just evaluation history
```

---

## 5. Removed Linear Process References ✅

### Cleaned Up
**Before:** Some references to rigid Problem → Options → Decision flow

**After:** All references now point to exploratory, non-blocking flow

### Confirmed in all three documents:
- ✅ `conversation_memory_architecture.md` - Factor-centric journal, no linear flow
- ✅ `user_interaction_guideline.md` - Exploration and evaluation, no decision tracking
- ✅ `exploratory_assessment_architecture.md` - Drop linear process entirely

---

## Current State: Fully Coherent

### Core Principles (Aligned Across All Docs)

1. **Exploratory, not rigid**
   - Start anywhere, jump freely
   - System never blocks
   - User decides "good enough"

2. **Factor-centric persistence**
   - Everything links to factors
   - Journal tracks evidence over time
   - Cumulative inference from all entries

3. **Confidence everywhere**
   - System shows percentages (70% confident)
   - User inputs simple language (likely / fairly sure)
   - User confidence ≠ factor score

4. **No decision tracking**
   - Evaluation snapshots only
   - No "Did you do it?" tracking
   - User owns execution

5. **Context accumulates**
   - Never ask twice
   - Auto-populate from journal
   - Reuse everything automatically

6. **Options when requested**
   - Project ideas: 3-5 when user asks
   - Next steps: 3-5 when user asks
   - Status: 2-3 brief options

7. **Simple language**
   - No jargon for user input
   - Percentages OK for system output
   - Elementary school terminology

---

## No Remaining Contradictions

All three documents now tell the same story:
- **conversation_memory_architecture.md** - How to persist factor assessments
- **user_interaction_guideline.md** - How to interact with users
- **exploratory_assessment_architecture.md** - How to enable free exploration

They're coherent, complementary, and ready for implementation.

---

## Key Takeaways

### What Users Experience
1. Explore freely, no rigid structure
2. System shows confidence on everything
3. Get project ideas when they ask (3-5 options)
4. Get next steps when they ask (3-5 options)
5. See 2-3 options after status checks
6. Never tracked on execution
7. Can re-evaluate projects over time

### What System Does
1. Accumulates evidence in factor journals
2. Synthesizes cumulative inferences
3. Tracks unconfirmed vs confirmed factors
4. Calculates confidence from evidence quality + quantity
5. Stores project evaluation snapshots (TBD)
6. Never blocks exploration
7. Shows ROI of continuing

### What System Never Does
1. ❌ Ask for decimals or p90 from users
2. ❌ Enforce linear process
3. ❌ Block exploration ("need X first")
4. ❌ Track decisions or execution
5. ❌ Ask "Did you do it?"
6. ❌ Require formal decision records
7. ❌ Force users to complete everything
