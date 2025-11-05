# Scoped Factor Model - Architecture Specification

**Version:** 1.1  
**Date:** 2024-10-30  
**Last Updated:** 2025-11-01 21:55  
**Status:** Superseded by Output-Centric Model  
**Note:** This document describes the scoped factor model. See `output_centric_factor_model_exploration.md` (v0.3) for the evolved output-centric approach with 1-5 star ratings.

---

## Overview

The **Scoped Factor Model** enables the system to assess organizational factors at multiple levels of specificity while maintaining organizational truth across different project discussions.

### Core Principle

**Organizational factors are organizational facts, independent of discovery context.**

A factor assessment discovered during a sales forecasting discussion (e.g., "Salesforce CRM data quality is poor") remains valid and applicable to any other project that uses Salesforce CRM data.

---

## Problem Statement

### The Abstraction Gap

**Naive approach:**
```
User: "Our sales reports are unreliable"
System infers: data_quality = 40 (organization-wide)
System concludes: Cannot do time series analysis on ANY data
```

**Reality:**
- Sales reports unreliable ≠ All data unreliable
- Manufacturing sensor data might be pristine (85%)
- Finance data might be audit-ready (90%)
- HR data might be well-governed (75%)

**The gap:** Organization-wide factors cannot capture domain/system-specific reality.

### The Dimensionality Challenge

```
Possible factor instances:
- 15 organizational factors
- × 10 data domains (sales, finance, HR, manufacturing...)
- × 50+ systems (Salesforce, SAP, custom tools...)
- × 20+ teams
= 150,000+ potential combinations

Pre-building project templates: Impossible
```

---

## Solution: Scoped Factor Instances

### Core Concept

Each factor can have **multiple instances** with different **scopes**. The system maintains:

1. **Generic assessments** - "Sales department data quality = ⭐⭐⭐ (3 stars)"
2. **Specific assessments** - "Salesforce CRM data quality = ⭐⭐ (2 stars)"
3. **Relationships** - Specific instances refine generic ones
4. **Inheritance** - Fall back to generic when specific unknown

**UPDATE:** Output-centric model uses Output + Team + Process + System context instead of domain/system/team scopes.

### Scope Dimensions

Every factor instance has a scope defined by:

- **domain** - Data/business domain (sales, finance, manufacturing, HR, etc.)
- **system** - Specific system/tool (Salesforce CRM, SAP ERP, spreadsheets, etc.)
- **team** - Organizational team (enterprise sales, accounting, etc.)

Each dimension can be:
- **Specified** - `{domain: "sales"}` - Applies to sales domain
- **Null (generic)** - `{domain: null}` - Applies to all domains

---

## Data Model

### Factor Definition (Template)

```json
{
  "factor_id": "data_quality",
  "factor_name": "Data Quality",
  "description": "Quality, consistency, and reliability of data",
  "scale": {
    "1": "⭐ No quality controls, data unreliable",
    "3": "⭐⭐⭐ Basic quality processes",
    "5": "⭐⭐⭐⭐⭐ World-class data quality"
  },
  "scope_dimensions": ["domain", "system", "team"],
  "allows_generic_scope": true
}
```

### Factor Instance (Assessment)

```json
{
  "instance_id": "dq_sales_sfdc_002",
  "factor_id": "data_quality",
  "scope": {
    "domain": "sales",
    "system": "salesforce_crm",
    "team": null
  },
  "scope_label": "Salesforce CRM",
  "value": 30,
  "confidence": 0.80,
  "evidence": [
    {
      "statement": "Salesforce has incomplete data",
      "timestamp": "2024-10-30T10:05:00Z",
      "specificity": "system-specific"
    },
    {
      "statement": "Duplicate customer records in SFDC",
      "timestamp": "2024-10-30T10:07:00Z",
      "specificity": "system-specific"
    }
  ],
  "refines": "dq_sales_generic_001",
  "refined_by": [],
  "synthesized_from": [],
  "discovered_in_context": "sales_forecasting_discussion",
  "created_at": "2024-10-30T10:05:00Z",
  "updated_at": "2024-10-30T10:07:00Z"
}
```

### Scope Hierarchy

```
Level 1: Organization-wide (most generic)
  scope: {domain: null, system: null, team: null}
  example: "Overall organizational data quality"

Level 2: Domain-specific
  scope: {domain: "sales", system: null, team: null}
  example: "Sales department data quality"

Level 3: System-specific
  scope: {domain: "sales", system: "salesforce_crm", team: null}
  example: "Salesforce CRM data quality"

Level 4: Team-specific
  scope: {domain: "sales", system: "salesforce_crm", team: "enterprise_sales"}
  example: "Enterprise sales team's Salesforce data quality"
```

---

## Intelligent Discovery Patterns

### Pattern 1: Generic → Specific Refinement

```
User: "Our sales data has quality issues"

System:
1. Creates generic instance
   - scope: {domain: "sales", system: null}
   - value: 3  // 3 stars (was: 45)
   - confidence: 0.60

2. Asks clarifying question:
   "Is this across all your sales systems, or specific to certain tools 
   like your CRM, data warehouse, or spreadsheets?"

User: "Mainly our Salesforce CRM"

System:
3. Creates specific instance
   - scope: {domain: "sales", system: "salesforce_crm"}
   - value: 2  // 2 stars
   - confidence: 0.80
   - refines: dq_sales_generic_001

4. Updates generic instance
   - value: 3  // 3 stars
   - confidence: 0.40 (reduced - not truly generic)
   - refined_by: [dq_sales_sfdc_002]

5. Responds:
   "Got it. Salesforce CRM data quality is particularly low (⭐⭐).
   Your other sales systems might be better (⭐⭐⭐)."
```

### Pattern 2: Specific → Generic Inference

```
User: "Our Salesforce data is incomplete"

System:
1. Creates specific instance
   - scope: {domain: "sales", system: "salesforce_crm"}
   - value: 35
   - confidence: 0.75

2. Asks clarifying question:
   "Do other sales systems have similar issues, or is this 
   isolated to Salesforce?"

User: "It's just Salesforce, our data warehouse is fine"

System:
3. Creates another specific instance
   - scope: {domain: "sales", system: "data_warehouse"}
   - value: 75
   - confidence: 0.70

4. Does NOT create generic sales instance
   (user indicated issue is isolated)

5. Responds:
   "Understood - data quality varies by system:
   - Salesforce: ~35% (incomplete)
   - Data warehouse: ~75% (fine)
   
   For sales forecasting, which system would we use?"
```

### Pattern 3: Multiple Specifics → Generic Synthesis

```
User: "Our Salesforce data is incomplete"
System: Creates dq_sales_sfdc = 35

User: "And our sales spreadsheets are a mess"
System: Creates dq_sales_spreadsheets = 25

System:
1. Detects pattern: Multiple sales systems with low quality

2. Creates generic instance via synthesis
   - scope: {domain: "sales", system: null}
   - value: 2  // 2 stars (MIN of components in output-centric model)
   - confidence: 0.75 (high - multiple data points)
   - synthesized_from: [dq_sales_sfdc, dq_sales_spreadsheets]

3. Responds:
   "I'm noticing a pattern - sales data quality seems low across 
   multiple systems (Salesforce ~35%, spreadsheets ~25%).
   
   This suggests a broader sales data quality issue. 
   Root causes might be:
   - No data governance in sales department
   - Lack of data entry training
   - No data steward for sales
   
   Want to explore what's causing this pattern?"
```

---

## Scope Matching & Inheritance

### Matching Algorithm

```python
def get_applicable_value(factor_id, needed_scope):
    """
    Find the most specific applicable assessment for a given scope.
    
    Args:
        factor_id: The factor to query (e.g., "data_quality")
        needed_scope: The scope needed (e.g., {domain: "sales", system: "salesforce_crm"})
    
    Returns:
        (instance, match_confidence) or None
    """
    instances = get_factor_instances(factor_id)
    candidates = []
    
    for instance in instances:
        match_score = calculate_scope_match(instance.scope, needed_scope)
        if match_score > 0:
            candidates.append((instance, match_score))
    
    # Return most specific match (highest score, then highest confidence)
    candidates.sort(key=lambda x: (x[1], x[0].confidence), reverse=True)
    return candidates[0] if candidates else None

def calculate_scope_match(instance_scope, needed_scope):
    """
    Calculate how well an instance matches a needed scope.
    
    Returns: 0.0 (no match) to 1.0 (exact match)
    """
    score = 0.0
    dimensions = ["domain", "system", "team"]
    
    for dim in dimensions:
        instance_val = instance_scope.get(dim)
        needed_val = needed_scope.get(dim)
        
        if needed_val is None:
            # Don't care about this dimension
            score += 0.33
        elif instance_val == needed_val:
            # Exact match
            score += 0.33
        elif instance_val is None and needed_val is not None:
            # Instance is more generic - can apply but less confident
            score += 0.20
        else:
            # Mismatch - doesn't apply
            return 0.0
    
    return score
```

### Matching Examples

**Example 1: Exact Match**
```
Query: data_quality for {domain: "sales", system: "salesforce_crm"}

Available:
1. {domain: "sales", system: "salesforce_crm"} = 2 stars, conf=0.80
   → match_score = 1.0 (exact)

Result: 2 stars, confidence=0.80
```

**Example 2: Generic Fallback**
```
Query: data_quality for {domain: "sales", system: "data_warehouse"}

Available:
1. {domain: "sales", system: "salesforce_crm"} = 2 stars, conf=0.80
   → match_score = 0.0 (system mismatch)
   
2. {domain: "sales", system: null} = 3 stars, conf=0.60
   → match_score = 0.86 (domain match, system generic)

Result: 3 stars, confidence=0.60
System note: "No specific data warehouse assessment, using generic sales data quality"
```

**Example 3: No Match**
```
Query: data_quality for {domain: "manufacturing", system: "iot_sensors"}

Available:
1. {domain: "sales", system: "salesforce_crm"} = 2 stars
   → match_score = 0.0 (domain mismatch)
   
2. {domain: "sales", system: null} = 3 stars
   → match_score = 0.0 (domain mismatch)

Result: None
System: "I don't have information about manufacturing data quality yet. 
Want to discuss it?"
```

---

## Clarifying Questions

### Question Generation Logic

```python
def generate_clarifying_question(user_statement, inferred_factor, initial_scope):
    """
    Generate intelligent clarifying question based on statement specificity.
    """
    specificity = analyze_specificity(user_statement)
    
    if specificity == "generic":
        # "Our sales data has issues"
        return {
            "question": f"Is this across all your {initial_scope['domain']} systems, "
                       f"or specific to certain tools?",
            "intent": "narrow_scope",
            "options": ["all_systems", "specific_system", "unsure"]
        }
    
    elif specificity == "system_mentioned":
        # "Our Salesforce data is incomplete"
        return {
            "question": f"Do other {initial_scope['domain']} systems have similar issues, "
                       f"or is this isolated to {initial_scope['system']}?",
            "intent": "check_generalization",
            "options": ["isolated", "similar_elsewhere", "unsure"]
        }
    
    elif specificity == "ambiguous":
        # "Our data is incomplete"
        return {
            "question": "Which data are you referring to - sales, finance, operations, or other?",
            "intent": "identify_domain",
            "options": ["sales", "finance", "operations", "all", "other"]
        }
```

### Question Patterns

**Pattern 1: Narrow from Generic**
```
Trigger: Generic statement detected
Example: "Our sales data quality is poor"

Question: "Is this across all sales systems (CRM, spreadsheets, databases), 
or mainly in specific tools?"

Responses:
- "All systems" → Keep generic scope, increase confidence
- "Mainly Salesforce" → Create specific scope, reduce generic confidence
- "Not sure" → Keep generic, flag for later clarification
```

**Pattern 2: Generalize from Specific**
```
Trigger: Specific system mentioned
Example: "Salesforce data is incomplete"

Question: "Do other sales systems (data warehouse, spreadsheets) have 
similar issues, or is this isolated to Salesforce?"

Responses:
- "Isolated" → Keep only specific scope
- "Similar everywhere" → Create generic scope, link specifics
- "Haven't checked" → Keep specific, suggest checking others
```

**Pattern 3: Identify Domain**
```
Trigger: No domain mentioned
Example: "Our data quality is terrible"

Question: "Which data domains are you thinking about - sales, finance, 
operations, or across the organization?"

Responses:
- "Sales" → Create domain-specific scope
- "Everything" → Create org-wide scope, high confidence
- "Not sure" → Keep generic, ask about specific use case
```

**Pattern 4: Resolve Contradictions**
```
Trigger: New statement contradicts existing assessment
Example: 
  Previous: "Sales data quality is good" (generic = 75)
  New: "Salesforce data is incomplete" (specific = 35)

Question: "Earlier you mentioned sales data quality is good, but now 
you're saying Salesforce has issues. Is Salesforce the exception, 
or should I revise my understanding of overall sales data quality?"

Responses:
- "Salesforce is the exception" → Keep generic high, specific low
- "I was wrong earlier" → Update generic to match specific
- "Good is relative" → Clarify scale interpretation
```

---

## Firestore Schema

### Collections Structure

```
/users/{user_id}/
  /factor_instances/{instance_id}
    - factor_id: string
    - scope: {domain: string|null, system: string|null, team: string|null}
    - scope_label: string
    - value: number (0-100)
    - confidence: number (0-1)
    - evidence: array
    - refines: string|null (instance_id of generic instance)
    - refined_by: array of instance_ids
    - synthesized_from: array of instance_ids
    - discovered_in_context: string
    - created_at: timestamp
    - updated_at: timestamp
  
  /scope_registry/
    - domains: array of strings
    - systems: map {domain: [systems]}
    - teams: map {domain: [teams]}
```

### Example Document

```json
{
  "instance_id": "dq_sales_sfdc_002",
  "factor_id": "data_quality",
  "scope": {
    "domain": "sales",
    "system": "salesforce_crm",
    "team": null
  },
  "scope_label": "Salesforce CRM",
  "value": 30,
  "confidence": 0.80,
  "evidence": [
    {
      "statement": "Salesforce has incomplete data",
      "timestamp": "2024-10-30T10:05:00Z",
      "specificity": "system-specific",
      "conversation_id": "conv_123"
    }
  ],
  "refines": "dq_sales_generic_001",
  "refined_by": [],
  "synthesized_from": [],
  "discovered_in_context": "sales_forecasting_discussion",
  "created_at": "2024-10-30T10:05:00Z",
  "updated_at": "2024-10-30T10:07:00Z"
}
```

---

## UI Representation

### Tree View (Recommended)

```
📊 Data Quality
├─ 🏢 Organization-wide: Not assessed
├─ 💼 Sales Department: 45% (moderate confidence)
│  ├─ 🔧 Salesforce CRM: 30% ⚠️ (high confidence)
│  ├─ 📊 Spreadsheets: 25% ⚠️ (high confidence)
│  └─ 🗄️ Data Warehouse: Not assessed
├─ 💰 Finance Department: 80% ✓ (high confidence)
│  └─ 🔧 SAP ERP: 85% ✓ (high confidence)
└─ 🏭 Manufacturing: Not assessed
```

### Conversation Summary View

```
💬 Data Quality Assessment

Your data quality varies significantly:

Sales Department (45%, moderate confidence)
  ⚠️ Salesforce CRM is particularly problematic (30%)
     Evidence:
     • "Salesforce has incomplete data"
     • "Duplicate customer records in SFDC"
  
  ⚠️ Spreadsheets also have issues (25%)
     Evidence:
     • "Sales spreadsheets are a mess"

Finance Department (80%, high confidence)
  ✓ SAP ERP has strong quality controls (85%)
     Evidence:
     • "Finance data is audit-ready"

Not yet assessed: Manufacturing, HR, Operations
```

---

## Epic 1 Implementation Scope

### Simplified for MVP

**Focus:** Single factor (`data_quality`), 2 scope levels

**Supported scopes:**
- Generic: `{domain: null, system: null}`
- Domain-specific: `{domain: "sales", system: null}`
- System-specific: `{domain: "sales", system: "salesforce_crm"}`

**Clarifying questions:** 2 patterns
1. Narrow from generic
2. Generalize from specific

**UI:** Simple tree or list showing scoped instances

### Epic 1 User Flow

```
1. User: "Our data quality is poor"
   → System creates: {domain: null} = 40

2. System: "Which data are you thinking about?"
   User: "Sales data"
   → System creates: {domain: "sales"} = 40
   → System updates: {domain: null} confidence = 0.30

3. System: "Is this across all sales systems, or specific tools?"
   User: "Mainly Salesforce"
   → System creates: {domain: "sales", system: "salesforce_crm"} = 35
   → System updates: {domain: "sales"} confidence = 0.50
```

---

## Cross-Project Reuse Example

### Scenario

```
[Discussion 1: Sales Forecasting]
User: "Can we do sales forecasting?"
System: "How's your sales data quality?"
User: "Salesforce data is incomplete"
→ Stores: data_quality {domain: "sales", system: "salesforce_crm"} = 35

[Discussion 2: Days Later - CRM Data Quality]
User: "What about improving our CRM data quality?"
System: [Retrieves existing assessment]
"We've already identified that Salesforce CRM data quality is around 35% 
(you mentioned incomplete data when we discussed sales forecasting).

Improving this could:
1. Enable the sales forecasting project
2. Improve customer segmentation
3. Make reporting more reliable

Want to explore AI solutions for data quality improvement?"
```

---

## AI Suggests Itself Pattern

### Graph Enhancement: IMPROVES Edge

```json
{
  "edges": [
    {
      "source": "anomaly_detection",
      "source_type": "AI_ARCHETYPE",
      "target": "data_quality",
      "target_type": "ORGANIZATIONAL_FACTOR",
      "relationship": "IMPROVES",
      "mechanism": "Identifies data quality issues automatically",
      "typical_improvement": "+20 to +40 points",
      "prerequisites": ["some_data_exists", "patterns_detectable"]
    }
  ]
}
```

### Discovery Flow

```
User: "Can we do sales forecasting?"

System evaluates:
- Needs: data_quality >= 60 for sales domain
- Have: data_quality {domain: "sales", system: "salesforce_crm"} = 35
- Gap: 25 points

System searches graph:
"What AI archetypes can IMPROVE data_quality?"

Finds:
- Anomaly Detection → improves data_quality (+20-40)
- Classification → improves data_quality (+15-30)

System responds:
"Sales forecasting on current Salesforce data isn't feasible - 
data quality is too low (35%, need 60%+).

BUT - AI could help improve your Salesforce data quality:
- Automated duplicate detection and merging
- Missing value prediction
- Data validation and anomaly flagging

Want to explore using AI to fix the data quality problem first?"
```

---

## Next Steps

### Immediate Tasks

1. **Update architecture documents** to reflect scoped factor model
2. **Update UX guidelines** with clarifying question patterns
3. **Update data schemas** with scope structure
4. **Design KG-based question inference** - "This Cogglepoop system - I do not know it. Which team uses it for what?"

### Future Enhancements

1. **Scope registry learning** - System learns domains/systems from user mentions
2. **Automatic scope detection** - NER to identify systems in user statements
3. **Scope relationship inference** - "Is Salesforce part of your sales stack or marketing stack?"
4. **Multi-dimensional scoping** - Team + system + domain combinations

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-30  
**Status:** Ready for implementation
