# Cumulative Inference Architecture

## Key Insight

**One mention means nothing.** Factor values must be derived from **cumulative evidence** across all journal entries, not single mentions.

---

## What Changed

### ❌ Old Approach (Single Mention)
```yaml
/factors/{factor_id}:
  current_value: 20
  inference_status: "unconfirmed"
  inferred_from_conversation: "User mentioned data scattered across 5 systems"
```

**Problem:**
- Single mention is weak evidence
- Duplicates information already in journal
- Doesn't account for multiple conversations

### ✅ New Approach (Cumulative Evidence)
```yaml
/factors/{factor_id}:
  current_value: 20  # Derived from ALL journal entries
  current_confidence: 0.75  # Based on evidence quality + quantity
  inference_status: "unconfirmed"
  # NO inferred_from_conversation - that's in the journal
```

**Benefits:**
- Value synthesized from ALL evidence
- Confidence increases with more consistent mentions
- No duplication—full trail is in journal entries

---

## How It Works

### 1. Journal Entries Accumulate Evidence

```yaml
/factors/data_quality/journal:
  - entry_1:
      timestamp: "2024-10-20"
      conversation_excerpt: "Our data is scattered across 5 systems"
      change_rationale: "User mentioned data distribution issues"
  
  - entry_2:
      timestamp: "2024-10-22"
      conversation_excerpt: "We don't have a data catalog"
      change_rationale: "User confirmed lack of data governance"
  
  - entry_3:
      timestamp: "2024-10-25"
      conversation_excerpt: "Sales data has lots of duplicates"
      change_rationale: "User mentioned data quality issues"
```

### 2. LLM Synthesizes ALL Evidence

```python
def recalculate_factor_from_journal(factor_id: str, user_id: str):
    """
    Cumulative inference from ALL journal entries
    """
    # Get all journal entries
    entries = get_journal_entries(factor_id)
    
    # Prepare evidence pieces
    evidence = [
        {
            "text": entry.conversation_excerpt,
            "timestamp": entry.timestamp,
            "context": entry.change_rationale
        }
        for entry in entries
    ]
    
    # LLM synthesizes
    synthesis = llm.synthesize_evidence(
        factor_id=factor_id,
        evidence_pieces=evidence,
        scale=knowledge_graph.get_factor_scale(factor_id),
        prompt=f"""
        Factor: data_quality
        Scale: 0=no quality controls, 50=basic checks, 100=comprehensive governance
        
        Evidence from {len(evidence)} conversations:
        1. [Oct 20] "Our data is scattered across 5 systems"
        2. [Oct 22] "We don't have a data catalog"
        3. [Oct 25] "Sales data has lots of duplicates"
        
        Synthesize:
        1. What's the data_quality score (0-100) based on ALL evidence?
        2. How confident are you (0-1)?
        3. Are the evidence pieces consistent or contradictory?
        
        Return: {{"value": <score>, "confidence": <0-1>}}
        """
    )
    
    # LLM returns:
    # value: 20 (scattered + no catalog + quality issues = very low)
    # confidence: 0.75 (3 consistent pieces of evidence)
    
    return synthesis.value, synthesis.confidence
```

### 3. Status Shows Evidence Count, Not Single Mention

**❌ Old (weak):**
```
Unconfirmed inferences:
- data_quality: 20% (inferred from "data scattered across 5 systems")
```

**✅ New (strong):**
```
Unconfirmed inferences:
- data_quality: 20% (75% confident, based on 3 mentions: scattered data, no catalog, duplicates)
```

---

## Confidence Calculation

Confidence increases with:
1. **More evidence** - 3 mentions > 1 mention
2. **Consistency** - All pointing to "low quality" > contradictory
3. **Recency** - Recent mentions weighted higher
4. **Specificity** - "20% duplicates" > "some issues"

```python
def calculate_confidence(evidence_pieces: List[dict]) -> float:
    """
    Confidence based on evidence quality and quantity
    """
    base_confidence = 0.3  # Start low
    
    # More evidence = higher confidence
    evidence_bonus = min(len(evidence_pieces) * 0.15, 0.4)
    
    # Consistency check
    consistency_score = check_consistency(evidence_pieces)
    
    # Recency bonus
    recency_bonus = calculate_recency_weight(evidence_pieces)
    
    total = base_confidence + evidence_bonus + consistency_score + recency_bonus
    
    return min(total, 0.95)  # Cap at 95% for unconfirmed

# Examples:
# 1 mention: 0.3 + 0.15 = 0.45 (45% confident)
# 3 consistent mentions: 0.3 + 0.45 + 0.2 = 0.95 (95% confident)
# 3 contradictory mentions: 0.3 + 0.45 - 0.2 = 0.55 (55% confident)
```

---

## Implementation Changes

### Storage Schema
```yaml
# REMOVED from /factors/{factor_id}:
- inferred_from_conversation  # Redundant, already in journal

# KEPT:
- current_value  # Synthesized from ALL journal entries
- current_confidence  # Based on evidence quality + quantity
- inference_status  # "unconfirmed" | "confirmed" | "user_provided"
```

### New Method: `recalculate_factor_from_journal()`
```python
class FactorJournalStore:
    def recalculate_factor_from_journal(self, user_id: str, factor_id: str):
        """
        Core cumulative inference mechanism
        Recalculates factor value from ALL journal entries
        """
        entries = self.get_journal_entries(factor_id)
        evidence = [format_evidence(e) for e in entries]
        synthesis = self.llm.synthesize_evidence(factor_id, evidence)
        return synthesis.value, synthesis.confidence
```

### Updated Method: `get_unconfirmed_factors()`
```python
def get_unconfirmed_factors(self, user_id: str):
    """
    Returns unconfirmed factors with evidence count
    """
    unconfirmed = []
    for factor in all_factors:
        if factor.inference_status == "unconfirmed":
            journal_entries = get_journal_entries(factor.id)
            unconfirmed.append({
                "factor_id": factor.id,
                "value": factor.value,
                "confidence": factor.confidence,
                "evidence_count": len(journal_entries),  # NEW
                "latest_mention": journal_entries[0].timestamp
            })
    return unconfirmed
```

---

## User-Facing Changes

### Status Queries
```
User: "Where are we?"

System: "Here's what we've mapped out:

**Confirmed factors:**
- data_availability: 80% ✓ (you explicitly said "3 years of sales data")

**Unconfirmed inferences:**
- data_quality: 20% (75% confident, based on 3 mentions)
- data_governance: 15% (60% confident, based on 2 mentions)

Want to confirm these, or move on?"
```

### Project Evaluations
```
User: "Can we do sales forecasting?"

System: "Based on what we've discussed:

**Feasibility: 45% confidence**

Why 45%?
- ✅ Data availability: 80% (confirmed, 3 years of data)
- ⚠️ Data quality: 20% (unconfirmed, 75% confident from 3 mentions)
- ❓ ML infrastructure: unknown

The data quality inference is based on:
1. Scattered data across 5 systems
2. No data catalog
3. Duplicate issues in sales data

Sound right, or should we adjust?"
```

---

## Benefits

### 1. **Stronger Evidence**
- 3 consistent mentions > 1 mention
- Confidence reflects evidence quality

### 2. **No Duplication**
- Evidence stored once in journal
- Factor document stays lean

### 3. **Transparent Reasoning**
- User sees evidence count
- Can drill down to journal for details

### 4. **Adaptive Confidence**
- More evidence → higher confidence
- Contradictory evidence → lower confidence
- Recent evidence → weighted higher

### 5. **Scalable**
- Works with 1 mention or 100 mentions
- LLM synthesis handles complexity

---

## Example: Confidence Evolution

### After 1 mention:
```
data_quality: 20% (45% confident, based on 1 mention)
```

### After 3 consistent mentions:
```
data_quality: 20% (75% confident, based on 3 mentions: scattered, no catalog, duplicates)
```

### After user confirmation:
```
data_quality: 20% ✓ (95% confident, user confirmed)
```

### After contradictory evidence:
```
data_quality: 35% (60% confident, based on 4 mentions: 3 negative, 1 positive about recent improvements)
```

---

## Implementation Priority

### Phase 1: Core Mechanism (Week 1)
1. ✅ Remove `inferred_from_conversation` field
2. ✅ Implement `recalculate_factor_from_journal()`
3. ✅ Update `get_unconfirmed_factors()` to show evidence count
4. ✅ Update status responses to show cumulative evidence

### Phase 2: LLM Synthesis (Week 2)
1. 🔲 Build LLM synthesis prompt
2. 🔲 Implement consistency checking
3. 🔲 Add recency weighting
4. 🔲 Test with real conversations

### Phase 3: Confidence Tuning (Week 3)
1. 🔲 Calibrate confidence thresholds
2. 🔲 Handle contradictory evidence
3. 🔲 Add specificity scoring
4. 🔲 Validate with users

---

## Key Principle

**Inference is cumulative, not instantaneous.**

Every conversation adds to the evidence pool. The LLM synthesizes ALL evidence to produce a value and confidence score. Single mentions are weak; patterns across multiple conversations are strong.
