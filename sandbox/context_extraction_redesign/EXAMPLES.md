# Test Cases for Context Extraction

**Purpose:** Define expected extractions for various user messages to validate extraction accuracy.

---

## Test Case Format

For each test case:
1. **User Message** - What the user says
2. **Expected Extraction** - Structured context we should extract
3. **Difficulty** - Simple, Medium, Complex
4. **Notes** - Special considerations

---

## Test Case 1: Simple Assessment

**User Message:**
> "The data quality is 3 stars."

**Expected Extraction:**
```json
{
  "outputs": [],
  "teams": [],
  "systems": [],
  "processes": [],
  "assessments": [
    {
      "target": "data quality",
      "rating": 3,
      "explicit": true,
      "sentiment": "neutral"
    }
  ],
  "dependencies": [],
  "root_causes": []
}
```

**Difficulty:** Simple  
**Notes:** Clear, explicit rating. No other context.

---

## Test Case 2: The Sentence That Broke Us

**User Message:**
> "I think data quality in our CRM is bad because the sales team hates to document their work."

**Expected Extraction:**
```json
{
  "outputs": [
    {
      "name": "CRM data quality",
      "domain": "sales",
      "system": "CRM"
    }
  ],
  "teams": [
    {
      "name": "sales team",
      "role": "data_entry"
    }
  ],
  "systems": [
    {
      "name": "CRM",
      "type": "software_system"
    }
  ],
  "processes": [
    {
      "name": "sales documentation",
      "owner": "sales team",
      "description": "document their work"
    }
  ],
  "assessments": [
    {
      "target": "CRM data quality",
      "rating": 2,
      "explicit": false,
      "sentiment": "negative",
      "keyword": "bad"
    }
  ],
  "dependencies": [
    {
      "from": "sales documentation",
      "to": "CRM data quality",
      "type": "input"
    }
  ],
  "root_causes": [
    {
      "output": "CRM data quality",
      "component": "team_execution",
      "description": "sales team hates to document",
      "sentiment": "negative"
    }
  ]
}
```

**Difficulty:** Complex  
**Notes:** Multi-entity, implicit rating, causal chain, sentiment analysis.

---

## Test Case 3: Multi-Output Dependency Chain

**User Message:**
> "Our sales forecasts are terrible, which makes inventory planning impossible, so we always overstock."

**Expected Extraction:**
```json
{
  "outputs": [
    {
      "name": "sales forecasts",
      "domain": "sales"
    },
    {
      "name": "inventory planning",
      "domain": "operations"
    },
    {
      "name": "inventory levels",
      "domain": "operations"
    }
  ],
  "teams": [],
  "systems": [],
  "processes": [],
  "assessments": [
    {
      "target": "sales forecasts",
      "rating": 1,
      "explicit": false,
      "sentiment": "very_negative",
      "keyword": "terrible"
    },
    {
      "target": "inventory planning",
      "rating": 1,
      "explicit": false,
      "sentiment": "very_negative",
      "keyword": "impossible"
    },
    {
      "target": "inventory levels",
      "rating": 2,
      "explicit": false,
      "sentiment": "negative",
      "keyword": "overstock"
    }
  ],
  "dependencies": [
    {
      "from": "sales forecasts",
      "to": "inventory planning",
      "type": "input",
      "impact": "blocks"
    },
    {
      "from": "inventory planning",
      "to": "inventory levels",
      "type": "input",
      "impact": "causes_problem"
    }
  ],
  "root_causes": [
    {
      "output": "inventory planning",
      "component": "dependency_quality",
      "description": "poor sales forecasts",
      "upstream": "sales forecasts"
    },
    {
      "output": "inventory levels",
      "component": "dependency_quality",
      "description": "poor inventory planning",
      "upstream": "inventory planning"
    }
  ]
}
```

**Difficulty:** Complex  
**Notes:** Cascading dependencies, multiple outputs, implicit ratings, causal chain.

---

## Test Case 4: Team + Process + System

**User Message:**
> "The engineering team uses JIRA but they don't update tickets, so project managers have no visibility."

**Expected Extraction:**
```json
{
  "outputs": [
    {
      "name": "project visibility",
      "domain": "project_management",
      "stakeholder": "project managers"
    }
  ],
  "teams": [
    {
      "name": "engineering team",
      "role": "development"
    },
    {
      "name": "project managers",
      "role": "stakeholder"
    }
  ],
  "systems": [
    {
      "name": "JIRA",
      "type": "project_management_system"
    }
  ],
  "processes": [
    {
      "name": "ticket updates",
      "owner": "engineering team",
      "system": "JIRA"
    }
  ],
  "assessments": [
    {
      "target": "project visibility",
      "rating": 1,
      "explicit": false,
      "sentiment": "negative",
      "keyword": "no visibility"
    }
  ],
  "dependencies": [
    {
      "from": "ticket updates",
      "to": "project visibility",
      "type": "input"
    }
  ],
  "root_causes": [
    {
      "output": "project visibility",
      "component": "process_maturity",
      "description": "engineering team doesn't update tickets"
    }
  ]
}
```

**Difficulty:** Complex  
**Notes:** Multiple teams, process issue, system mentioned but not root cause.

---

## Test Case 5: Implicit Assessment with Symptom

**User Message:**
> "We're constantly firefighting because our monitoring is blind to production issues."

**Expected Extraction:**
```json
{
  "outputs": [
    {
      "name": "production monitoring",
      "domain": "operations"
    }
  ],
  "teams": [],
  "systems": [
    {
      "name": "monitoring system",
      "type": "observability"
    }
  ],
  "processes": [],
  "assessments": [
    {
      "target": "production monitoring",
      "rating": 1,
      "explicit": false,
      "sentiment": "very_negative",
      "keyword": "blind",
      "symptom": "constantly firefighting"
    }
  ],
  "dependencies": [],
  "root_causes": [
    {
      "output": "production monitoring",
      "component": "system_support",
      "description": "monitoring system has blind spots"
    }
  ]
}
```

**Difficulty:** Medium  
**Notes:** Implicit rating, symptom-based assessment, system inadequacy.

---

## Test Case 6: Positive Assessment

**User Message:**
> "Our customer support team is excellent at resolving tickets quickly."

**Expected Extraction:**
```json
{
  "outputs": [
    {
      "name": "ticket resolution",
      "domain": "customer_support"
    }
  ],
  "teams": [
    {
      "name": "customer support team",
      "role": "support"
    }
  ],
  "systems": [],
  "processes": [
    {
      "name": "ticket resolution",
      "owner": "customer support team"
    }
  ],
  "assessments": [
    {
      "target": "ticket resolution",
      "rating": 5,
      "explicit": false,
      "sentiment": "very_positive",
      "keyword": "excellent"
    }
  ],
  "dependencies": [],
  "root_causes": [
    {
      "output": "ticket resolution",
      "component": "team_execution",
      "description": "team is excellent",
      "sentiment": "positive"
    }
  ]
}
```

**Difficulty:** Medium  
**Notes:** Positive sentiment, implicit high rating, team strength.

---

## Test Case 7: Ambiguous Reference

**User Message:**
> "It's broken because they never test it properly."

**Expected Extraction:**
```json
{
  "outputs": [
    {
      "name": "unknown",
      "ambiguous": true,
      "reference": "it"
    }
  ],
  "teams": [
    {
      "name": "unknown",
      "ambiguous": true,
      "reference": "they"
    }
  ],
  "systems": [],
  "processes": [
    {
      "name": "testing",
      "owner": "unknown team",
      "quality": "poor"
    }
  ],
  "assessments": [
    {
      "target": "unknown",
      "rating": 1,
      "explicit": false,
      "sentiment": "negative",
      "keyword": "broken"
    }
  ],
  "dependencies": [],
  "root_causes": [
    {
      "output": "unknown",
      "component": "process_maturity",
      "description": "inadequate testing"
    }
  ]
}
```

**Difficulty:** Complex  
**Notes:** Ambiguous references ("it", "they"), requires conversation context to resolve.

---

## Test Case 8: Multiple Systems

**User Message:**
> "Data flows from Salesforce to our data warehouse, but the ETL pipeline is unreliable."

**Expected Extraction:**
```json
{
  "outputs": [
    {
      "name": "data pipeline reliability",
      "domain": "data_engineering"
    }
  ],
  "teams": [],
  "systems": [
    {
      "name": "Salesforce",
      "type": "CRM",
      "role": "source"
    },
    {
      "name": "data warehouse",
      "type": "data_storage",
      "role": "destination"
    },
    {
      "name": "ETL pipeline",
      "type": "data_pipeline",
      "role": "integration"
    }
  ],
  "processes": [
    {
      "name": "data flow",
      "from_system": "Salesforce",
      "to_system": "data warehouse",
      "via_system": "ETL pipeline"
    }
  ],
  "assessments": [
    {
      "target": "ETL pipeline",
      "rating": 2,
      "explicit": false,
      "sentiment": "negative",
      "keyword": "unreliable"
    }
  ],
  "dependencies": [
    {
      "from": "Salesforce",
      "to": "data warehouse",
      "type": "data_flow",
      "via": "ETL pipeline"
    }
  ],
  "root_causes": [
    {
      "output": "data pipeline reliability",
      "component": "system_support",
      "description": "ETL pipeline is unreliable"
    }
  ]
}
```

**Difficulty:** Complex  
**Notes:** Multiple systems, data flow, system reliability issue.

---

## Test Case 9: Partial Information

**User Message:**
> "I want to work on sales forecasting."

**Expected Extraction:**
```json
{
  "outputs": [
    {
      "name": "sales forecasting",
      "domain": "sales",
      "status": "identified_not_assessed"
    }
  ],
  "teams": [],
  "systems": [],
  "processes": [],
  "assessments": [],
  "dependencies": [],
  "root_causes": []
}
```

**Difficulty:** Simple  
**Notes:** Output identification only, no assessment or context yet.

---

## Test Case 10: Comparative Assessment

**User Message:**
> "Our data quality used to be 4 stars, but now it's down to 2 because we lost our data engineer."

**Expected Extraction:**
```json
{
  "outputs": [
    {
      "name": "data quality",
      "domain": "data"
    }
  ],
  "teams": [
    {
      "name": "data engineering",
      "status": "understaffed",
      "change": "lost_member"
    }
  ],
  "systems": [],
  "processes": [],
  "assessments": [
    {
      "target": "data quality",
      "rating": 2,
      "explicit": true,
      "sentiment": "negative",
      "historical_rating": 4,
      "trend": "declining"
    }
  ],
  "dependencies": [],
  "root_causes": [
    {
      "output": "data quality",
      "component": "team_execution",
      "description": "lost data engineer",
      "type": "staffing_issue"
    }
  ]
}
```

**Difficulty:** Complex  
**Notes:** Temporal comparison, staffing change, trend analysis.

---

## Validation Criteria

For each test case, extraction is considered **successful** if:

1. **Entity Extraction:** 90%+ of entities identified
2. **Relationship Extraction:** 80%+ of relationships identified
3. **Assessment Accuracy:** Rating within ±1 star
4. **Root Cause Identification:** Correct component identified
5. **Ambiguity Handling:** Ambiguous references flagged

---

## Additional Test Cases Needed

1. **Negation:** "The data quality is NOT bad" (positive despite "bad" keyword)
2. **Conditional:** "IF we hire a data engineer, THEN data quality would improve"
3. **Multiple Assessments:** "Data quality is 2 stars, but team execution is 4 stars"
4. **Stakeholder Mention:** "The CEO is frustrated with our reporting delays"
5. **Quantitative Metrics:** "We have 500 open bugs and only 3 QA engineers"
6. **Process Breakdown:** "The approval process takes 2 weeks because it goes through 5 people"
7. **System Integration:** "Salesforce doesn't sync with our ERP, so we have duplicate data"
8. **Cultural Issues:** "Nobody wants to own this process"
9. **Technical Debt:** "The codebase is a mess, so every change takes forever"
10. **External Dependencies:** "We're blocked waiting for the vendor to fix their API"

---

**Next Step:** Build prototype extractor and test against these cases.
