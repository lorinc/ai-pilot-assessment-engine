# Exploratory Assessment Architecture

## Core Principle

**The system is a thinking partner, not a checklist enforcer.**

Users explore freely. The system remembers context, suggests next moves, shows confidence, but never blocks exploration. "What's missing, what would be the gain?" replaces rigid linear processes.

---

## Key Architectural Changes

### 1. Drop Linear Process Entirely

**Old approach:** Problem → Options → Evidence → Impact → Decision (enforced sequence)

**New approach:** Start anywhere, jump freely, system tracks context

- ✅ User can start with: project idea | problem | "what's possible?" | factor exploration
- ✅ User can jump: discuss KPIs → back to data quality → forward to project feasibility
- ✅ System never blocks: "You can't evaluate yet, need X first" ❌
- ✅ System always proceeds: "Low confidence (40%), here's why..." ✅

### 2. Always-On Confidence Scoring

Every assessment, every project evaluation shows:
- **Current confidence level** (40%, 70%, 90%)
- **What's driving low confidence** (missing: data governance, team skills)
- **What would improve it** (10 min on data governance → +20% confidence)
- **Diminishing returns signal** (assessing 3 more factors → only +5% confidence)

**User decides when "good enough":**
- €10k pilot? 40% confidence might be fine
- €100k project? Probably want 75%+
- System suggests, user decides

### 3. Unconfirmed Inferences Tracking

**Problem:** LLM infers "data_quality = 20%" from conversation, but user never explicitly validated it.

**Solution:** Track inference status, derive value from cumulative evidence

```yaml
/factors/{factor_id}:
  current_value: 20  # Derived from ALL journal entries, not single mention
  current_confidence: 0.75  # Based on evidence quality + quantity
  inference_status: "unconfirmed"  # or "confirmed" or "user_provided"
  last_updated: "2024-10-28T10:30:00Z"
  # NO inferred_from_conversation - that's in the journal
```

**How inference works with scoped instances:**
```python
def calculate_factor_value(factor_id: str, scope: dict, user_id: str) -> tuple[int, float]:
    """
    Cumulative inference from ALL evidence for this scope
    """
    # Get the most applicable instance using scope matching
    instance = get_applicable_instance(factor_id, scope, user_id)
    
    if not instance:
        return None, 0.0
    
    # Each evidence piece contributes
    evidence_pieces = []
    for evidence in instance.evidence:
        evidence_pieces.append({
            "text": evidence["statement"],
            "timestamp": evidence["timestamp"],
            "specificity": evidence["specificity"]
        })
    
    # LLM synthesizes ALL evidence for this scope
    synthesis = llm.synthesize_evidence(
        factor_id=factor_id,
        scope=scope,
        evidence_pieces=evidence_pieces,
        scale=knowledge_graph.get_factor_scale(factor_id)
    )
    
    return synthesis.value, synthesis.confidence

def get_applicable_instance(factor_id: str, needed_scope: dict, user_id: str):
    """
    Find most specific applicable instance using scope matching
    """
    instances = get_factor_instances(factor_id, user_id)
    candidates = []
    
    for instance in instances:
        match_score = calculate_scope_match(instance.scope, needed_scope)
        if match_score > 0:
            candidates.append((instance, match_score))
    
    # Return most specific match (highest score, then highest confidence)
    candidates.sort(key=lambda x: (x[1], x[0].confidence), reverse=True)
    return candidates[0][0] if candidates else None

# Example synthesis prompt with scope:
"""
Factor: data_quality
Scope: {domain: "sales", system: "salesforce_crm"}
Scale: 0=no quality controls, 50=basic checks, 100=comprehensive governance

Evidence from 2 conversations:
1. [Oct 20] "Salesforce has incomplete data" (system-specific)
2. [Oct 22] "Duplicate customer records in SFDC" (system-specific)

Synthesize: What's the data_quality score for Salesforce CRM (0-100)?
How confident are you (0-1)?
"""

# LLM returns:
# value: 30 (incomplete + duplicates = low quality)
# confidence: 0.80 (2 consistent system-specific pieces of evidence)
```

**In status/summary responses with scoped instances:**
```
System: "Here's what we've mapped out:

**Data Readiness: 60% mapped, 70% confident**

**Confirmed factors:**
- data_availability (Sales): 80% ✓ (you explicitly said "we have 3 years of sales data")

**Unconfirmed inferences:**
- data_quality (Sales/Salesforce CRM): 30% (80% confident, based on 2 mentions: incomplete data, duplicates)
- data_quality (Sales/generic): 45% (60% confident, inferred from Salesforce issues)
- data_governance (Sales): 15% (60% confident, based on 2 mentions: no formal policies, no data steward)

Want to confirm these, or should we move on?"
```

**Key difference:**
- ❌ "inferred from 'data scattered across 5 systems'" (single mention)
- ✅ "75% confident, based on 3 mentions" (cumulative evidence)
- ✅ Confidence increases with more consistent evidence
- ✅ Full evidence trail is in journal, not duplicated in status

**Persistence with scoped instances:**
```python
class FactorInstanceStore:
    def update_factor_instance(
        self,
        user_id: str,
        factor_id: str,
        scope: dict,  # NEW: {domain, system, team}
        new_value: Any,
        rationale: str,
        confidence: float,
        inference_status: str = "unconfirmed",
        user_confirmed: bool = False,
        refines: str = None,  # NEW: instance_id of more generic instance
        specificity: str = "generic"  # NEW: "generic" | "domain-specific" | "system-specific"
    ):
        # Generate instance_id
        instance_id = generate_instance_id(factor_id, scope)
        
        # Create or update instance document
        instance_doc = self.user_ref.collection("factor_instances").document(instance_id)
        
        instance_doc.set({
            "instance_id": instance_id,
            "factor_id": factor_id,
            "scope": scope,
            "scope_label": generate_scope_label(scope),
            "value": new_value,
            "confidence": confidence,
            "inference_status": "confirmed" if user_confirmed else "unconfirmed",
            "refines": refines,
            "discovered_in_context": self.current_context,
            "updated_at": firestore.SERVER_TIMESTAMP
        }, merge=True)
```

### 4. Project-Specific "Good Enough" Thresholds

**Not:** "You need 80% completeness to proceed"  
**Instead:** "For this €10k pilot, you have enough. For a €100k project, I'd want more on governance."

```python
def evaluate_project_feasibility(
    project_idea: str,
    estimated_cost: int,
    user_id: str
) -> dict:
    """
    Always proceed with evaluation, show confidence + gaps
    """
    # Get current factor state
    factors = get_all_assessed_factors(user_id)
    
    # Identify relevant factors for this project
    relevant_factors = identify_relevant_factors(project_idea, factors)
    
    # Calculate confidence
    confidence = calculate_confidence(relevant_factors)
    
    # Identify gaps
    missing_factors = identify_missing_factors(project_idea, factors)
    
    # Risk-based threshold
    recommended_confidence = get_recommended_confidence(estimated_cost)
    
    return {
        "feasibility": "proceed_with_caution" if confidence < recommended_confidence else "good_to_go",
        "confidence": confidence,
        "confidence_breakdown": {
            "data_readiness": 0.60,
            "ai_capability": 0.40,
            "cultural_fit": 0.50
        },
        "gaps": [
            {
                "factor": "data_governance",
                "impact": "Would raise confidence from 45% to 60%",
                "time_to_assess": "10 minutes"
            },
            {
                "factor": "team_skills",
                "impact": "Would raise confidence from 60% to 70%",
                "time_to_assess": "5 minutes"
            }
        ],
        "recommendation": f"For a €{estimated_cost} project, I'd recommend {recommended_confidence}% confidence. You're at {confidence}%. {'Good to proceed' if confidence >= recommended_confidence else 'Consider assessing: ' + ', '.join([g['factor'] for g in missing_factors[:2]])}",
        "diminishing_returns": "Assessing 3 more factors would only improve confidence by 5%"
    }

def get_recommended_confidence(estimated_cost: int) -> float:
    """Risk-based confidence thresholds"""
    if estimated_cost < 25000:
        return 0.40  # Low-risk pilot
    elif estimated_cost < 100000:
        return 0.60  # Medium-risk project
    else:
        return 0.75  # High-stakes project
```

### 5. Conversation Memory Integration

**Auto-populate from factor journal:**

```python
User: "Can we do a sales forecasting project?"

System: 
# 1. Determine needed scope from project context
needed_scope = {"domain": "sales", "system": None}

# 2. Retrieve relevant factor instances using scope matching
factors = {
    "data_quality": get_applicable_value("data_quality", needed_scope),
    # Returns: {value: 45, confidence: 0.60, scope: {domain: "sales", system: null}}
    # Note: Falls back to generic sales if no specific system mentioned
    
    "data_availability": get_applicable_value("data_availability", needed_scope),
    # Returns: {value: 80, confidence: 0.90, scope: {domain: "sales", system: null}}
    
    "ml_infrastructure": get_applicable_value("ml_infrastructure", needed_scope)
    # Returns: None (never discussed for sales domain)
}

# 3. Evaluate with scoped data
evaluation = evaluate_project_feasibility(
    "sales_forecasting", 
    15000, 
    user_id,
    scope={"domain": "sales", "system": None}
)

# 4. Respond with scope-aware context
"Based on what we've discussed about your sales data:

**Feasibility: Proceed with caution (45% confidence)**

Why 45%?
- ✅ Sales data availability is strong (80%) - you have 3 years of sales data
- ⚠️ Sales data quality is moderate (45%) - some issues in Salesforce (30%), but might be better in other systems
- ❓ ML infrastructure unknown - haven't discussed this yet

**For a €15k pilot, 45% confidence is borderline.**

**To improve confidence:**
- Discuss data governance (10 min) → +15% confidence
- Assess ML infrastructure (5 min) → +10% confidence

Or we can proceed now and treat this as a high-risk pilot. Your call."
```

### 6. "What's Next" Driven by Pareto Principle

**Always show ROI of continuing:**

```python
def suggest_next_steps(user_id: str, context: str = None) -> dict:
    """
    Pareto-driven suggestions: 20% of factors explain 80% of feasibility
    """
    summary = get_assessment_summary(user_id)
    
    # Identify high-impact gaps
    gaps = identify_high_impact_gaps(summary)
    
    # Calculate ROI for each potential action
    suggestions = []
    for gap in gaps:
        roi = calculate_roi(gap)
        suggestions.append({
            "action": f"Assess {gap['factor']}",
            "time": gap["time_to_assess"],
            "confidence_gain": gap["confidence_gain"],
            "unlocks": gap["unlocks"],  # What project types this enables
            "roi": roi  # confidence_gain / time
        })
    
    # Sort by ROI
    suggestions.sort(key=lambda x: x["roi"], reverse=True)
    
    # Signal diminishing returns
    top_3_gain = sum(s["confidence_gain"] for s in suggestions[:3])
    rest_gain = sum(s["confidence_gain"] for s in suggestions[3:])
    
    return {
        "top_suggestions": suggestions[:3],
        "diminishing_returns": f"Top 3 actions would gain {top_3_gain}% confidence in 20 min. Remaining actions would only gain {rest_gain}% more.",
        "current_capability": summary["capabilities"]["can_evaluate"],
        "next_unlock": suggestions[0]["unlocks"] if suggestions else None
    }
```

**Example output:**
```
System: "Here's where you'd get the most value:

**Top 3 next steps:**
1. Assess data governance (10 min) → +15% confidence, unlocks 3 project types
2. Discuss team skills (5 min) → +10% confidence, unlocks 2 project types
3. Explore ML infrastructure (5 min) → +8% confidence

After these, you'd be at 78% confidence—good for most medium-risk projects.

Assessing the remaining 12 factors would only add another 10% confidence. 
Probably not worth it unless you're planning something high-stakes.

What sounds most useful?"
```

### 7. Flexible Entry Points

**User can start anywhere:**

```python
def handle_user_intent(user_input: str, user_id: str):
    """
    Detect intent and route appropriately
    """
    intent = llm.classify_intent(user_input, [
        "evaluate_project",
        "explore_possibilities",
        "assess_factor",
        "status_check",
        "what_next",
        "general_question"
    ])
    
    if intent == "evaluate_project":
        # "Can we do sales forecasting?"
        return evaluate_project_with_context(user_input, user_id)
    
    elif intent == "explore_possibilities":
        # "What AI projects could we do?"
        return generate_project_ideas_from_factors(user_id)
    
    elif intent == "assess_factor":
        # "Let me tell you about our data quality"
        return conversational_factor_assessment(user_input, user_id)
    
    elif intent == "status_check":
        # "Where are we?"
        return format_status_response(user_id)
    
    elif intent == "what_next":
        # "What should we discuss next?"
        return suggest_next_steps(user_id)
    
    else:
        # General conversation
        return llm.respond_with_context(user_input, user_id)
```

### 8. Multi-Session Continuity Pattern

**When user returns:**

```python
def welcome_back(user_id: str, days_since_last: int):
    """
    Adaptive welcome based on time elapsed
    """
    summary = get_assessment_summary(user_id)
    last_conv = summary["last_conversation"]
    
    if days_since_last < 1:
        # Same day - resume
        return f"Welcome back! We were discussing {last_conv['topic']}. Want to continue, or switch topics?"
    
    elif days_since_last < 7:
        # Within a week - status + resume option
        return f"""
        Welcome back! Quick status:
        
        **What you can do now:**
        {format_capabilities(summary['capabilities'])}
        
        **Last time:** We discussed {last_conv['topic']}. 
        {format_last_conversation_impact(last_conv)}
        
        **Options:**
        - Continue with {last_conv['topic']}
        - Evaluate a project idea
        - Explore what's next
        
        What sounds good?
        """
    
    else:
        # Long gap - full status
        return format_status_response(user_id) + "\n\nWhat would you like to work on?"
```

---

## Unconfirmed Inferences in Practice

### Scenario 1: Status Check

```
User: "Where are we?"

System: "Here's what we've mapped out:

**Data Readiness: 60% mapped, 70% confident**

Confirmed:
- data_availability (Sales): 80% ✓ (you said "3 years of sales data")

Unconfirmed (I inferred these, but you haven't validated):
- data_quality varies by system:
  • Salesforce CRM: 30% (from "incomplete data" and "duplicates")
  • Sales overall: 45% (inferred from Salesforce issues)
- data_governance (Sales): 15% (from "no formal policies")

**What you can do now:**
You can evaluate sales forecasting projects, but confidence varies by which system you'd use.

Want to confirm those inferences, or should we move on?"
```

### Scenario 2: Project Evaluation

```
User: "Can we do predictive maintenance?"

System: "Let me check... 

**Feasibility: Low confidence (35%)**

Based on what we've discussed:
- ✅ You have sensor data (confirmed)
- ⚠️ Data quality unclear (I inferred 20% from earlier comments—not confirmed)
- ❓ ML infrastructure unknown

**For predictive maintenance, I'd want 60%+ confidence.**

**Quick wins to improve:**
1. Confirm data quality (2 min) → Would clarify biggest uncertainty
2. Discuss ML infrastructure (5 min) → +15% confidence

Or we can proceed with high uncertainty. Your call."
```

### Scenario 3: Proactive Validation

```
System: "By the way, I've been assuming your data governance is around 15% 
based on you mentioning 'no formal policies.' 

If that's changed, or if I misunderstood, let me know—it affects 3 project types."
```

---

## TBD Items (Future Work)

### 1. Project Evaluation Persistence

**Need:**
- Store project evaluations as timestamped snapshots
- Track: project name, feasibility confidence, gaps, timestamp
- Allow: "Re-evaluate that forecasting project with updated knowledge"
- No decision tracking—just evaluation history

**Data model:**
```yaml
/users/{user_id}/project_evaluations/{evaluation_id}:
  project_name: "Sales forecasting"
  description: "Monthly sales predictions with seasonal trends"
  estimated_cost: 50000
  
  evaluation_snapshot:
    timestamp: "2024-10-28T10:30:00Z"
    feasibility_confidence: 0.45
    confidence_breakdown:
      data_readiness: 0.60
      ai_capability: 0.40
      cultural_fit: 0.50
    gaps: ["data_governance", "ml_infrastructure"]
    recommendation: "For €50k project, 45% is low. Assess data governance first."
    
  previous_evaluations:
    - timestamp: "2024-10-20T14:00:00Z"
      feasibility_confidence: 0.30
      gaps: ["data_quality", "data_governance", "ml_infrastructure"]
```

**UX:**
- "Show me all projects we've evaluated"
- "Re-evaluate sales forecasting" → Shows confidence change over time
- "What changed since last evaluation?" → Diff of factor assessments
- No "Did you do it?" tracking—just evaluation snapshots

### 2. Factor Export/Import (Spreadsheet)

**Use case:** User wants to:
- Export all factors to Excel for review
- Share with colleagues to gather input
- Import back with colleague assessments

**Export format:**
```csv
factor_id,factor_name,current_value,confidence,rationale,status
data_quality,Data Quality,20,0.75,"Data scattered across 5 systems, no catalog",unconfirmed
data_availability,Data Availability,80,0.90,"3 years of sales data in warehouse",confirmed
data_governance,Data Governance,15,0.60,"No formal policies mentioned",unconfirmed
```

**Import behavior:**
```python
def import_factors(user_id: str, csv_file: str):
    """
    Import factors from spreadsheet
    - Flag all as very low confidence (0.30)
    - LLM compares rationale against knowledge graph scale
    - If LLM agrees with value, raise confidence to 0.70
    - If LLM disagrees, flag for user review
    """
    imported_factors = parse_csv(csv_file)
    
    for factor in imported_factors:
        # LLM validates
        validation = llm.validate_factor_value(
            factor_id=factor["factor_id"],
            value=factor["current_value"],
            rationale=factor["rationale"],
            scale=knowledge_graph.get_factor_scale(factor["factor_id"])
        )
        
        if validation["agrees"]:
            confidence = 0.70  # LLM confirmed
            status = "confirmed"
        else:
            confidence = 0.30  # Needs review
            status = "needs_review"
            validation_notes = validation["reason"]
        
        # Store with import metadata
        journal_store.update_factor(
            user_id=user_id,
            factor_id=factor["factor_id"],
            new_value=factor["current_value"],
            rationale=factor["rationale"],
            confidence=confidence,
            inference_status=status,
            import_metadata={
                "imported_at": datetime.now(),
                "validation": validation,
                "original_confidence": factor.get("confidence", 0.30)
            }
        )
```

**Partial import (colleague input):**
```python
def import_partial_factors(user_id: str, csv_file: str):
    """
    Import subset of factors (e.g., colleague filled in 5 factors)
    - Merge with existing factors
    - Flag conflicts (colleague says 80%, you said 20%)
    - Suggest resolution
    """
    imported = parse_csv(csv_file)
    existing = get_all_factors(user_id)
    
    conflicts = []
    for imp_factor in imported:
        existing_factor = existing.get(imp_factor["factor_id"])
        
        if existing_factor and abs(existing_factor["value"] - imp_factor["value"]) > 20:
            conflicts.append({
                "factor": imp_factor["factor_id"],
                "your_value": existing_factor["value"],
                "colleague_value": imp_factor["value"],
                "your_rationale": existing_factor["rationale"],
                "colleague_rationale": imp_factor["rationale"]
            })
    
    if conflicts:
        return {
            "status": "conflicts_found",
            "conflicts": conflicts,
            "suggestion": "Review these differences with your colleague"
        }
    else:
        # No conflicts, merge
        for imp_factor in imported:
            update_factor_from_import(user_id, imp_factor)
        return {"status": "success", "imported_count": len(imported)}
```

### 3. Colleague Collaboration Workflow

**Scenario:** User wants input from data team lead on data factors

**Workflow:**
1. User exports partial spreadsheet (only data factors)
2. Colleague fills in their assessment
3. User imports back
4. System shows conflicts, suggests discussion points

**Export:**
```python
def export_factors_for_colleague(
    user_id: str,
    factor_category: str,
    colleague_name: str
) -> str:
    """
    Export subset of factors for colleague input
    """
    factors = get_factors_by_category(user_id, factor_category)
    
    # Create CSV with instructions
    csv = f"# Assessment for {colleague_name}\n"
    csv += f"# Please fill in your assessment for these {factor_category} factors\n"
    csv += f"# Scale: 0-100, where 0=none, 50=moderate, 100=excellent\n\n"
    csv += "factor_name,your_assessment,your_rationale\n"
    
    for factor in factors:
        csv += f"{factor['name']},,\n"
    
    return csv
```

---

## Implementation Priority

### Phase 1: Core Exploratory Flow (Week 1-2)
1. ✅ Drop linear process enforcement
2. ✅ Always-proceed project evaluation with confidence
3. ✅ Unconfirmed inferences tracking
4. ✅ "What's next" with ROI calculation

### Phase 2: Enhanced Context (Week 3-4)
1. ✅ Auto-populate from factor journal
2. ✅ Multi-session continuity patterns
3. ✅ Flexible entry points
4. ✅ Diminishing returns signaling

### Phase 3: Collaboration (Week 5-6)
1. 🔲 Factor export/import (full)
2. 🔲 Partial import with conflict resolution
3. 🔲 Colleague collaboration workflow

### Phase 4: Project Management (Week 7-8)
1. 🔲 Project ideas persistence
2. 🔲 Project re-evaluation
3. 🔲 Project status tracking

---

## Success Criteria

**Users should feel:**
- ✅ Free to explore without rigid structure
- ✅ Confident in "good enough" decisions
- ✅ Aware of what would improve confidence
- ✅ Supported, not interrogated

**Users should never feel:**
- ❌ Blocked from exploring
- ❌ Forced to complete everything
- ❌ Unsure what the system "knows"
- ❌ Like they're filling out forms

**System should:**
- ✅ Remember everything from conversations
- ✅ Show confidence on all assessments
- ✅ Suggest high-ROI next steps
- ✅ Signal diminishing returns
- ✅ Validate inferences proactively
- ✅ Support collaboration (export/import)

---

## Key Architectural Principles

1. **Never block exploration** - Always proceed with confidence score
2. **Pareto everywhere** - 20% of factors, 80% of value
3. **Validate inferences** - Track unconfirmed, surface in summaries
4. **Risk-based thresholds** - €10k pilot ≠ €100k project
5. **ROI-driven suggestions** - Show confidence gain per minute
6. **Diminishing returns** - Signal when "good enough" reached
7. **Collaboration-friendly** - Export/import for colleague input
8. **Context-aware** - Auto-populate from conversation memory
