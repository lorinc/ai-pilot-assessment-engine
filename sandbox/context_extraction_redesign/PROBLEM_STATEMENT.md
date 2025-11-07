# Problem Statement: Context Extraction Redesign

**Date:** 2025-11-06

---

## The Fundamental Issue

**We're trying to parse rich, multi-dimensional business context with one-dimensional keyword triggers.**

This is like trying to catch a fish with a fork. It fundamentally cannot work.

---

## Example: The Sentence That Broke Us

**User says:**
> "I think data quality in our CRM is bad because the sales team hates to document their work."

### What This Sentence Contains

1. **Output Identification**
   - Output: "CRM data quality"
   - Domain: Sales/CRM
   - Specificity: Clear target

2. **Assessment/Rating**
   - Quality level: "bad"
   - Implicit rating: 1-2 stars (out of 5)
   - Sentiment: Negative

3. **Team Identification**
   - Team: "sales team"
   - Role: Data entry/documentation
   - Relationship: Responsible for process

4. **System Identification**
   - System: "CRM"
   - Type: Software system
   - Purpose: Data storage/management

5. **Process Identification**
   - Process: "document their work"
   - Owner: Sales team
   - Context: Data entry into CRM

6. **Root Cause Analysis**
   - Cause type: Team execution issue
   - Specific issue: "hates to document"
   - Category: Motivation/willingness problem
   - Component: Team Execution (not Data Quality, not System Support)

7. **Dependency Chain**
   - Upstream: Sales documentation process
   - Downstream: CRM data quality
   - Relationship: Input dependency
   - Impact: Poor process → Poor output

8. **Sentiment Analysis**
   - Overall: Negative
   - Keywords: "bad", "hates"
   - Tone: Frustrated

### What Our Current System Captures

**Atomic Triggers That Might Fire:**
- `T_MENTION_PROBLEM` (keyword: "bad")
- `T_MENTION_TEAM` (keyword: "team")

**Information Captured:**
- Problem mentioned: Yes
- Team mentioned: Yes

**Information LOST:**
- ❌ Which output? (CRM data quality)
- ❌ What rating? (1-2 stars)
- ❌ Which system? (CRM)
- ❌ Which process? (documentation)
- ❌ What root cause? (team execution)
- ❌ What dependency? (process → output)
- ❌ Why is it bad? (hate to document)

**Information Loss: ~90%**

---

## Why Atomic Triggers Cannot Work

### Problem 1: One-Dimensional Capture

Each trigger captures ONE thing:
- `T_MENTION_PROBLEM` → "problem mentioned"
- `T_MENTION_TEAM` → "team mentioned"
- `T_MENTION_SYSTEM` → "system mentioned"

But business context is **multi-dimensional**:
- Output + Team + System + Process + Assessment + Root Cause + Dependencies

**You cannot decompose a multi-dimensional problem into one-dimensional triggers.**

### Problem 2: No Relationship Extraction

Triggers can detect entities but not relationships:
- ✅ Can detect: "sales team" (entity)
- ✅ Can detect: "CRM" (entity)
- ❌ Cannot detect: "sales team documents work in CRM" (relationship)
- ❌ Cannot detect: "poor documentation causes poor data quality" (causality)

### Problem 3: Keyword Matching vs Semantic Understanding

Triggers use keywords:
- "bad" → T_MENTION_PROBLEM
- "team" → T_MENTION_TEAM

But meaning depends on context:
- "bad data quality" (assessment)
- "bad idea" (opinion, not assessment)
- "not bad" (positive, despite keyword "bad")

### Problem 4: Cannot Handle Complexity

**Simple sentence (triggers work):**
> "The data quality is 3 stars."

- `T_RATING_PROVIDED` fires
- Clear, one-dimensional

**Complex sentence (triggers fail):**
> "I think data quality in our CRM is bad because the sales team hates to document their work."

- Multiple entities
- Multiple relationships
- Causal chain
- Implicit rating
- Triggers cannot capture this

### Problem 5: Information Loss Compounds

Each lost piece of information makes the next extraction harder:
1. Miss the output → Don't know what to assess
2. Miss the system → Don't know where the problem is
3. Miss the root cause → Don't know what to fix
4. Miss the dependency → Don't know what affects what

**By the time we route to a handler, we've lost the context needed to handle it.**

---

## Real-World Examples

### Example 1: Multi-Output with Dependencies
> "Our sales forecasts are terrible, which makes inventory planning impossible, so we always overstock."

**Entities:**
- Output 1: Sales forecasts (quality: terrible)
- Output 2: Inventory planning (quality: impossible)
- Output 3: Inventory levels (quality: overstocked)

**Dependencies:**
- Sales forecasts → Inventory planning
- Inventory planning → Inventory levels

**Root Cause:**
- Upstream: Sales forecast quality

**Current System:**
- `T_MENTION_PROBLEM` fires
- Lost: 3 outputs, 2 dependencies, root cause chain

### Example 2: Team + Process + System
> "The engineering team uses JIRA but they don't update tickets, so project managers have no visibility."

**Entities:**
- Team: Engineering team
- System: JIRA
- Process: Ticket updates
- Output: Project visibility
- Stakeholder: Project managers

**Relationships:**
- Engineering team → Ticket update process
- Ticket update process → JIRA system
- JIRA system → Project visibility
- Project visibility → Project managers

**Root Cause:**
- Process maturity issue (don't update tickets)

**Current System:**
- `T_MENTION_TEAM` fires
- `T_MENTION_SYSTEM` fires
- Lost: Process, output, stakeholder, relationships, root cause

### Example 3: Implicit Assessment
> "We're constantly firefighting because our monitoring is blind to production issues."

**Entities:**
- Output: Production monitoring quality
- Symptom: Firefighting (reactive mode)
- System: Monitoring system
- Problem: Blind spots

**Implicit Assessment:**
- Monitoring quality: 1-2 stars (very poor)
- Impact: High (constant firefighting)

**Root Cause:**
- System support issue (monitoring inadequate)

**Current System:**
- `T_MENTION_PROBLEM` fires
- Lost: Output, system, implicit rating, root cause, impact

---

## Why This Matters

### Impact on User Experience

**User expects:**
1. Say something once
2. System understands full context
3. System acts on that context

**Current reality:**
1. User says something complex
2. System captures 10% of context
3. System asks user to repeat information
4. User gets frustrated

### Impact on Assessment Quality

**Without full context:**
- Cannot build accurate knowledge graph
- Cannot identify bottlenecks
- Cannot recommend solutions
- Cannot track dependencies

**With full context:**
- Build complete knowledge graph in one pass
- Identify bottlenecks from root cause analysis
- Recommend targeted solutions
- Track dependency chains

### Impact on Development Velocity

**Current approach:**
- Add trigger for each new pattern
- Triggers conflict and overlap
- Maintenance nightmare
- Cannot scale

**LLM extraction approach:**
- One extraction engine
- Handles all patterns
- Easy to extend (update prompt)
- Scales naturally

---

## The Solution: LLM-Based Structured Extraction

**Instead of:**
```
User Message → Keyword Triggers → Fire/Don't Fire → Lost Information
```

**We need:**
```
User Message → LLM Extraction → Structured Context → Full Information Preserved
```

**Key Insight:**
- LLMs are ALREADY doing semantic understanding
- We're using them for response generation
- Why not use them for context extraction?
- This is what LLMs are BEST at

---

## Success Criteria

**Must capture:**
- ✅ All entities (outputs, teams, systems, processes)
- ✅ All relationships (dependencies, causality)
- ✅ All assessments (explicit and implicit ratings)
- ✅ All root causes (why things are the way they are)

**Must handle:**
- ✅ Complex multi-entity sentences
- ✅ Implicit information (ratings, sentiment)
- ✅ Ambiguous references ("it", "that", "the system")
- ✅ Partial information (user mentions CRM but not which output)

**Must preserve:**
- ✅ 90%+ of information (vs 10% today)
- ✅ Relationships between entities
- ✅ Causal chains
- ✅ User intent

---

## Next Steps

1. Define entity and relationship schemas
2. Create test cases with expected extractions
3. Build prototype extractor
4. Validate extraction accuracy
5. Design integration strategy

---

**Bottom Line:** Atomic triggers are fundamentally inadequate for capturing rich business context. We need LLM-based structured extraction.
