# GCP Data Schemas & Structures

**Last Updated:** 2025-11-01 22:00  
**Note:** Factor values use 1-5 star ratings (INTEGER 1-5), not 0-100 percentages. See `output_centric_factor_model_exploration.md` for details.

## Firestore Schema

### User Data Structure

```
/users/{user_id}/
  
  metadata/
    assessment/
      # Aggregate metrics for fast status queries
      assessment_summary: {
        categories: {
          data_readiness: {
            completeness: 0.60,           # 60% of factors assessed
            avg_confidence: 0.70,
            factor_count: 15,             # Assessed factors
            total_factors: 25,            # Total in category
            last_updated: "2024-10-29T12:00:00Z"
          },
          ai_capability: {
            completeness: 0.40,
            avg_confidence: 0.50,
            factor_count: 10,
            total_factors: 25,
            last_updated: "2024-10-28T14:20:00Z"
          }
        },
        overall: {
          total_factors_assessed: 25,
          total_factors: 50,
          avg_confidence: 0.60,
          decision_tier: "low_risk"      # <€25k decisions
        },
        capabilities: {
          can_evaluate: [
            "basic_forecasting_annual",
            "simple_automation"
          ],
          cannot_evaluate_yet: [
            "complex_forecasting_seasonal",
            "ml_automation"
          ]
        },
        last_conversation: {
          topic: "data_quality",
          factor_id: "data_quality",
          timestamp: "2024-10-29T12:00:00Z",
          excerpt: "User mentioned data scattered across 5 systems"
        }
      }
  
  factor_instances/{instance_id}/
    # Scoped factor instance (e.g., data_quality for sales/Salesforce)
    instance_id: "dq_sales_sfdc_002",
    factor_id: "data_quality",
    scope: {
      domain: "sales",                 # or null for generic
      system: "salesforce_crm",        # or null for generic
      team: null                        # or specific team name
    },
    scope_label: "Salesforce CRM",     # Human-readable label
    value: 2,                            # 1-5 stars (INTEGER)
    confidence: 0.80,
    evidence: [
      {
        statement: "Salesforce has incomplete data",
        timestamp: "2024-10-29T12:00:00Z",
        specificity: "system-specific",
        conversation_id: "conv_123"
      },
      {
        statement: "Duplicate customer records in SFDC",
        timestamp: "2024-10-29T12:05:00Z",
        specificity: "system-specific",
        conversation_id: "conv_123"
      }
    ],
    refines: "dq_sales_generic_001",   # instance_id of more generic instance
    refined_by: [],                     # instance_ids of more specific instances
    synthesized_from: [],               # instance_ids if synthesized from multiple
    discovered_in_context: "sales_forecasting_discussion",
    inference_status: "unconfirmed",    # or "confirmed" or "user_provided"
    created_at: "2024-10-29T12:00:00Z",
    updated_at: "2024-10-29T12:05:00Z"
  
  scope_registry/
    metadata/
      # Registry of known domains, systems, and teams
      domains: ["sales", "finance", "operations", "hr", "manufacturing"],
      systems: {
        sales: ["salesforce_crm", "hubspot", "spreadsheets"],
        finance: ["sap_erp", "quickbooks", "custom_db"],
        operations: ["erp_system", "mes"]
      },
      teams: {
        sales: ["enterprise_sales", "smb_sales"],
        finance: ["accounting", "fp_and_a"]
      },
      last_updated: "2024-10-29T12:00:00Z"
  
  projects/{project_id}/
    # Project evaluation snapshots
    project_id: "uuid",
    project_name: "Sales Forecasting Pilot",
    description: "Monthly sales predictions with seasonal trends",
    estimated_cost: 50000,
    created_at: "2024-10-29T12:00:00Z",
    last_evaluated: "2024-10-29T12:00:00Z",
    
    evaluations/{evaluation_id}/
      # Timestamped evaluation snapshots
      evaluation_id: "uuid",
      timestamp: "2024-10-29T12:00:00Z",
      feasibility_confidence: 0.45,
      confidence_breakdown: {
        data_readiness: 0.60,
        ai_capability: 0.40,
        cultural_fit: 0.50
      },
      gaps: [
        {
          factor_id: "data_governance",
          impact: "Would raise confidence from 45% to 60%",
          time_to_assess: "10 minutes"
        },
        {
          factor_id: "ml_infrastructure",
          impact: "Would raise confidence from 60% to 70%",
          time_to_assess: "5 minutes"
        }
      ],
      recommendation: "For €50k project, 45% is low. Assess data governance first.",
      risk_assumptions: [
        {
          assumption: "Sales team will adopt new tool",
          concern_level: "worry",
          needs_testing: true
        }
      ]
```

### Firestore Indexes

```javascript
// Required composite indexes
{
  collectionGroup: "factor_instances",
  queryScope: "COLLECTION",
  fields: [
    { fieldPath: "factor_id", order: "ASCENDING" },
    { fieldPath: "updated_at", order: "DESCENDING" }
  ]
}

{
  collectionGroup: "factor_instances",
  queryScope: "COLLECTION",
  fields: [
    { fieldPath: "scope.domain", order: "ASCENDING" },
    { fieldPath: "factor_id", order: "ASCENDING" }
  ]
}

{
  collectionGroup: "factor_instances",
  queryScope: "COLLECTION",
  fields: [
    { fieldPath: "scope.system", order: "ASCENDING" },
    { fieldPath: "factor_id", order: "ASCENDING" }
  ]
}

{
  collectionGroup: "evaluations",
  queryScope: "COLLECTION",
  fields: [
    { fieldPath: "timestamp", order: "DESCENDING" }
  ]
}
```

---

## Static Knowledge Graph (Cloud Storage)

### factors.json

```json
{
  "data_quality": {
    "id": "data_quality",
    "name": "Data Quality",
    "category": "data_readiness",
    "description": "Accuracy, completeness, consistency of organizational data",
    "scale": {
      "0": "No quality controls, frequent errors, no validation",
      "25": "Basic validation rules, manual spot checks",
      "50": "Automated quality checks, error tracking",
      "75": "Comprehensive data profiling, quality dashboards",
      "100": "Enterprise-grade DQ management, automated remediation"
    },
    "assessment_questions": [
      "How often do you encounter data errors?",
      "Do you have automated data validation?",
      "Can you trust your data for decision-making?"
    ]
  },
  "data_availability": {
    "id": "data_availability",
    "name": "Data Availability",
    "category": "data_readiness",
    "description": "Accessibility and completeness of historical data",
    "scale": {
      "0": "No historical data, data scattered/lost",
      "25": "Some data available, gaps in history",
      "50": "1-2 years of data, reasonably complete",
      "75": "3+ years of data, well-organized",
      "100": "Comprehensive data warehouse, 5+ years, real-time access"
    }
  },
  "data_governance": {
    "id": "data_governance",
    "name": "Data Governance",
    "category": "data_readiness",
    "description": "Policies, ownership, and stewardship of data assets",
    "scale": {
      "0": "No governance, ad-hoc data management",
      "25": "Informal practices, no documented policies",
      "50": "Basic policies, designated data owners",
      "75": "Formal governance framework, data catalog",
      "100": "Enterprise data governance, compliance tracking, data lineage"
    }
  },
  "ml_infrastructure": {
    "id": "ml_infrastructure",
    "name": "ML Infrastructure",
    "category": "ai_capability",
    "description": "Technical infrastructure for ML development and deployment",
    "scale": {
      "0": "No ML infrastructure, manual processes",
      "25": "Basic cloud compute, Jupyter notebooks",
      "50": "Managed ML platform (e.g., Vertex AI), version control",
      "75": "MLOps pipeline, automated training, model registry",
      "100": "Full ML platform with CI/CD, monitoring, A/B testing"
    }
  },
  "team_ml_skills": {
    "id": "team_ml_skills",
    "name": "Team ML Skills",
    "category": "ai_capability",
    "description": "In-house machine learning and data science expertise",
    "scale": {
      "0": "No ML skills, no data scientists",
      "25": "1-2 people with basic Python/stats knowledge",
      "50": "Small data team, can build simple models",
      "75": "Experienced data scientists, production ML experience",
      "100": "ML engineering team, research capability, published work"
    }
  },
  "executive_support": {
    "id": "executive_support",
    "name": "Executive Support",
    "category": "cultural_fit",
    "description": "Leadership commitment to AI initiatives",
    "scale": {
      "0": "No executive awareness or interest",
      "25": "Curious but skeptical, no budget allocated",
      "50": "Supportive in principle, pilot budget approved",
      "75": "Active champion, strategic priority, resources committed",
      "100": "AI-first strategy, board-level oversight, transformation mandate"
    }
  }
}
```

### archetypes.json

```json
{
  "basic_forecasting": {
    "id": "basic_forecasting",
    "name": "Basic Forecasting",
    "description": "Annual sales/demand predictions using historical data",
    "typical_cost_range": [10000, 50000],
    "typical_timeline_weeks": [8, 16],
    "required_factors": [
      {
        "factor_id": "data_availability",
        "min_value": 60,
        "rationale": "Need 2+ years of historical data"
      },
      {
        "factor_id": "data_quality",
        "min_value": 40,
        "rationale": "Data must be reasonably clean for accurate predictions"
      }
    ],
    "optional_factors": [
      {
        "factor_id": "ml_infrastructure",
        "benefit": "Faster iteration and experimentation",
        "impact_on_timeline": -2
      },
      {
        "factor_id": "team_ml_skills",
        "benefit": "In-house maintenance and improvements",
        "impact_on_cost": -5000
      }
    ],
    "typical_roi": {
      "low": 20000,
      "medium": 50000,
      "high": 100000
    }
  },
  "complex_forecasting": {
    "id": "complex_forecasting",
    "name": "Complex Forecasting",
    "description": "Monthly/weekly predictions with seasonal trends, multiple variables",
    "typical_cost_range": [50000, 150000],
    "typical_timeline_weeks": [16, 26],
    "required_factors": [
      {
        "factor_id": "data_availability",
        "min_value": 75,
        "rationale": "Need 3+ years of granular data"
      },
      {
        "factor_id": "data_quality",
        "min_value": 60,
        "rationale": "High-quality data essential for complex models"
      },
      {
        "factor_id": "ml_infrastructure",
        "min_value": 50,
        "rationale": "Need platform for model experimentation"
      },
      {
        "factor_id": "team_ml_skills",
        "min_value": 50,
        "rationale": "Requires experienced data scientists"
      }
    ],
    "optional_factors": [
      {
        "factor_id": "data_governance",
        "benefit": "Easier feature engineering, data lineage",
        "impact_on_timeline": -3
      }
    ]
  },
  "simple_automation": {
    "id": "simple_automation",
    "name": "Simple Process Automation",
    "description": "Rule-based automation of repetitive tasks",
    "typical_cost_range": [5000, 25000],
    "typical_timeline_weeks": [4, 12],
    "required_factors": [
      {
        "factor_id": "data_availability",
        "min_value": 40,
        "rationale": "Need access to process data"
      }
    ],
    "optional_factors": [
      {
        "factor_id": "executive_support",
        "benefit": "Faster adoption, less resistance",
        "impact_on_timeline": -2
      }
    ]
  }
}
```

### edges.json

```json
{
  "edges": [
    {
      "from": "data_quality",
      "to": "data_governance",
      "type": "DEPENDS_ON",
      "weight": 0.8,
      "rationale": "Data quality requires governance policies"
    },
    {
      "from": "data_quality",
      "to": "data_infrastructure",
      "type": "DEPENDS_ON",
      "weight": 0.6,
      "rationale": "Quality checks need infrastructure"
    },
    {
      "from": "ml_infrastructure",
      "to": "team_ml_skills",
      "type": "DEPENDS_ON",
      "weight": 0.7,
      "rationale": "Infrastructure requires skills to operate"
    },
    {
      "from": "basic_forecasting",
      "to": "data_availability",
      "type": "REQUIRES",
      "min_value": 60,
      "criticality": "high"
    },
    {
      "from": "basic_forecasting",
      "to": "data_quality",
      "type": "REQUIRES",
      "min_value": 40,
      "criticality": "high"
    },
    {
      "from": "complex_forecasting",
      "to": "data_availability",
      "type": "REQUIRES",
      "min_value": 75,
      "criticality": "critical"
    },
    {
      "from": "complex_forecasting",
      "to": "ml_infrastructure",
      "type": "REQUIRES",
      "min_value": 50,
      "criticality": "high"
    }
  ]
}
```

---

## Python Data Classes

### Domain Models

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

@dataclass
class FactorScope:
    """Scope dimensions for a factor instance."""
    domain: Optional[str]  # e.g., "sales", "finance", or None for generic
    system: Optional[str]  # e.g., "salesforce_crm", or None for generic
    team: Optional[str]    # e.g., "enterprise_sales", or None for generic

@dataclass
class FactorInstance:
    """Scoped factor instance (e.g., data_quality for sales/Salesforce)."""
    instance_id: str
    factor_id: str
    scope: FactorScope
    scope_label: str       # Human-readable: "Salesforce CRM"
    value: int             # 0-100
    confidence: float      # 0.0-1.0
    evidence: List[Dict[str, Any]]  # Evidence statements
    refines: Optional[str]          # instance_id of more generic instance
    refined_by: List[str]           # instance_ids of more specific instances
    synthesized_from: List[str]     # instance_ids if synthesized
    discovered_in_context: str
    inference_status: str  # "unconfirmed" | "confirmed" | "user_provided"
    created_at: datetime
    updated_at: datetime

@dataclass
class ScopeMatch:
    """Result of scope matching query."""
    instance: FactorInstance
    match_score: float     # 0.0-1.0, where 1.0 is exact match
    match_type: str        # "exact" | "generic_fallback" | "partial"

@dataclass
class FactorInference:
    """LLM-inferred factor update from conversation."""
    factor_id: str
    scope: FactorScope     # Inferred scope for this assessment
    old_value: Optional[int]
    new_value: int
    confidence: float
    rationale: str
    inferred_from: List[str]
    specificity: str       # "generic" | "domain-specific" | "system-specific"

class IntentType(Enum):
    """User intent classification."""
    EVALUATE_PROJECT = "evaluate_project"
    EXPLORE_POSSIBILITIES = "explore_possibilities"
    ASSESS_FACTOR = "assess_factor"
    STATUS_CHECK = "status_check"
    WHAT_NEXT = "what_next"
    GENERAL_QUESTION = "general_question"

@dataclass
class Intent:
    """Classified user intent."""
    type: IntentType
    entities: Dict[str, Any]
    relevant_factors: List[str]
    needs_history: bool
    needs_dependencies: bool

@dataclass
class Context:
    """Assembled context for LLM prompt."""
    factors: Dict[str, Dict[str, Any]]
    dependencies: Dict[str, Dict[str, Any]]
    constraints: Dict[str, Any] = field(default_factory=dict)
    estimated_tokens: int = 0

@dataclass
class ProjectEvaluation:
    """Project feasibility evaluation snapshot."""
    evaluation_id: str
    project_id: str
    timestamp: datetime
    feasibility_confidence: float
    confidence_breakdown: Dict[str, float]
    gaps: List[Dict[str, Any]]
    recommendation: str
    risk_assumptions: List[Dict[str, Any]]

@dataclass
class AssessmentSummary:
    """Aggregate metrics for user's assessment progress."""
    categories: Dict[str, Dict[str, Any]]
    overall: Dict[str, Any]
    capabilities: Dict[str, List[str]]
    last_conversation: Dict[str, Any]
```

---

## LLM Prompt Templates

### Intent Classification Prompt

```python
INTENT_CLASSIFICATION_PROMPT = """
Analyze this user message and extract:

1. **Intent type** (choose one):
   - evaluate_project: User wants to assess feasibility of a specific project
   - explore_possibilities: User wants ideas for what projects they could do
   - assess_factor: User is providing information about their organization
   - status_check: User wants to know where they are in the assessment
   - what_next: User wants suggestions for next steps
   - general_question: General inquiry or conversation

2. **Mentioned entities**:
   - Projects (e.g., "sales forecasting", "chatbot")
   - Factors (e.g., "data quality", "team skills")
   - Constraints (e.g., "budget <€50k", "need results in 3 months")

3. **Relevant factor IDs** from knowledge graph that relate to this message

4. **Context needs**:
   - needs_history: Does answering require factor history?
   - needs_dependencies: Does answering require factor dependencies?

User message: "{user_message}"

Available factors: {factor_list}

Return JSON:
{{
    "type": "evaluate_project",
    "entities": {{
        "project": "sales forecasting",
        "constraints": ["budget <€50k"]
    }},
    "relevant_factors": ["data_quality", "data_availability", "ml_infrastructure"],
    "needs_history": false,
    "needs_dependencies": true
}}
"""
```

### Factor Inference Prompt

```python
FACTOR_INFERENCE_PROMPT = """
Analyze this conversation for implicit factor value updates.

**Current context:**
{context_json}

**Conversation:**
User: {user_message}
Assistant: {assistant_response}

**Task:**
Extract any factor values mentioned or implied. For each factor:
- factor_id (from knowledge graph)
- scope (domain, system, team - infer from context)
- new_value (0-100, based on factor scale)
- confidence (0.0-1.0, how certain are you?)
- rationale (brief explanation of why this value)
- inferred_from (related factor_ids that influenced this)
- specificity ("generic", "domain-specific", "system-specific")

**Factor scales:**
{factor_scales}

**Rules:**
1. Only infer if there's clear evidence in the conversation
2. Use cumulative evidence from context + new conversation
3. Confidence should reflect evidence quality and quantity
4. If user explicitly states a value, confidence = 0.95
5. If inferring from indirect mentions, confidence = 0.5-0.8
6. If contradictory evidence, flag for user review

Return JSON array:
[
    {{
        "factor_id": "data_quality",
        "scope": {{
            "domain": "sales",
            "system": "salesforce_crm",
            "team": null
        }},
        "new_value": 30,
        "confidence": 0.80,
        "rationale": "User mentioned Salesforce has incomplete data and duplicates",
        "inferred_from": ["data_governance"],
        "specificity": "system-specific"
    }}
]

Return empty array [] if no factor updates detected.
"""
```

### Cumulative Synthesis Prompt

```python
CUMULATIVE_SYNTHESIS_PROMPT = """
Synthesize factor value from ALL historical evidence.

**Factor:** {factor_id}
**Scale:** {factor_scale}

**Evidence from {num_entries} conversation(s):**
{evidence_list}

**Task:**
1. What's the {factor_id} score (0-100) based on ALL evidence?
2. How confident are you (0.0-1.0)?
3. Are the evidence pieces consistent or contradictory?
4. What would increase confidence?

**Synthesis rules:**
- More evidence → higher confidence
- Consistent evidence → higher confidence
- Contradictory evidence → lower confidence, flag for user review
- Recent evidence weighted slightly higher than old
- Explicit user statements weighted higher than inferences

Return JSON:
{{
    "value": 20,
    "confidence": 0.75,
    "consistency": "consistent",
    "rationale": "All 3 mentions point to low data quality: scattered systems, no catalog, quality issues",
    "to_increase_confidence": "Ask about specific data quality processes or tools"
}}
"""
```

### Project Evaluation Prompt

```python
PROJECT_EVALUATION_PROMPT = """
Evaluate project feasibility based on assessed factors.

**Project:** {project_name}
**Description:** {project_description}
**Estimated cost:** €{estimated_cost}

**Assessed factors:**
{assessed_factors_json}

**Project requirements (from archetype '{archetype_id}'):**
{archetype_requirements}

**Task:**
1. Calculate feasibility confidence (0.0-1.0)
2. Break down confidence by category (data_readiness, ai_capability, cultural_fit)
3. Identify gaps (missing or low-value factors)
4. Estimate impact of filling each gap
5. Provide recommendation based on cost and confidence

**Confidence calculation:**
- All required factors met at min_value → 0.8+ confidence
- Some required factors below min_value → 0.4-0.7 confidence
- Missing required factors → 0.0-0.3 confidence
- Optional factors add +0.05-0.1 per factor

**Risk-based thresholds:**
- €0-€25k (low risk): 0.4+ confidence acceptable
- €25k-€100k (medium risk): 0.6+ confidence recommended
- €100k+ (high risk): 0.75+ confidence required

Return JSON:
{{
    "feasibility_confidence": 0.45,
    "confidence_breakdown": {{
        "data_readiness": 0.60,
        "ai_capability": 0.40,
        "cultural_fit": 0.50
    }},
    "gaps": [
        {{
            "factor_id": "data_governance",
            "current_value": 15,
            "required_value": 40,
            "impact": "Would raise confidence from 45% to 60%",
            "time_to_assess": "10 minutes"
        }}
    ],
    "recommendation": "For €50k project, 45% confidence is borderline. Recommend assessing data governance first (10 min, +15% confidence).",
    "decision": "proceed_with_caution"
}}
"""
```

---

## SSE Event Format

### Technical Log Events

```python
@dataclass
class SSEEvent:
    """Server-Sent Event for technical log."""
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    
    def to_sse_format(self) -> str:
        """Convert to SSE wire format."""
        return f"⚙️ SYSTEM: [{self.timestamp.strftime('%H:%M:%S')}] {self.event_type}: {self._format_data()}\n"
    
    def _format_data(self) -> str:
        """Format data for display."""
        if self.event_type == "intent_classified":
            return f"{self.data['type']}"
        elif self.event_type == "context_retrieved":
            factors = ", ".join(self.data['factors'])
            return f"{self.data['factor_count']} factors ({factors})"
        elif self.event_type == "factor_update":
            return f"{self.data['factor_id']}={self.data['new_value']} (conf={self.data['confidence']:.2f})"
        else:
            return str(self.data)

# Example events
SSEEvent(
    event_type="intent_analysis",
    timestamp=datetime.now(),
    data={"message": "Analyzing user intent..."}
).to_sse_format()
# Output: "⚙️ SYSTEM: [12:01:32] intent_analysis: Analyzing user intent...\n"

SSEEvent(
    event_type="intent_classified",
    timestamp=datetime.now(),
    data={"type": "evaluate_project", "entities": {"project": "forecasting"}}
).to_sse_format()
# Output: "⚙️ SYSTEM: [12:01:33] intent_classified: evaluate_project\n"

SSEEvent(
    event_type="context_retrieved",
    timestamp=datetime.now(),
    data={"factor_count": 3, "factors": ["data_quality", "data_availability", "ml_infra"]}
).to_sse_format()
# Output: "⚙️ SYSTEM: [12:01:34] context_retrieved: 3 factors (data_quality, data_availability, ml_infra)\n"

SSEEvent(
    event_type="factor_update",
    timestamp=datetime.now(),
    data={"factor_id": "data_quality", "old_value": None, "new_value": 20, "confidence": 0.75}
).to_sse_format()
# Output: "⚙️ SYSTEM: [12:01:40] factor_update: data_quality=20 (conf=0.75)\n"
```

---

## Configuration Files

### requirements.txt

```
streamlit==1.29.0
google-cloud-firestore==2.13.1
google-cloud-storage==2.14.0
google-cloud-aiplatform==1.38.1
firebase-admin==6.3.0
networkx==3.2.1
python-dotenv==1.0.0
asyncio==3.4.3
aiohttp==3.9.1
```

### .streamlit/config.toml

```toml
[server]
port = 8080
address = "0.0.0.0"
headless = true
maxUploadSize = 10
sessionTimeout = 180  # 3 minutes

[theme]
primaryColor = "#4285F4"  # Google Blue
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#202124"
font = "sans serif"

[browser]
gatherUsageStats = false
```

### .env.example

```bash
# GCP Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Firestore
FIRESTORE_DATABASE=(default)

# Vertex AI
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-flash
VERTEX_AI_TEMPERATURE=0.7

# Firebase Auth
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com

# Application
SESSION_TIMEOUT_MINUTES=3
LOG_LEVEL=INFO
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-29  
**Companion to:** gcp_technical_architecture.md
