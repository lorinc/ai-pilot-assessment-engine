# Taxonomy Gap Analysis for Runtime Inference

Looking at the taxonomies through the lens of **runtime inference**, here's what's imbalanced:

## **1. CRITICAL GAP: Organizational Context Taxonomy**

**What's missing:** A structured taxonomy describing **organizational state/readiness**.

**Why it matters for inference:** You can't assess feasibility without knowing:
- AI maturity level (Exploring, Piloting, Scaling, Optimizing)
- Data infrastructure state (Siloed, Centralized, Governed, Real-time)
- Team capabilities (No ML team, Junior team, Mature ML org)
- Industry/sector context (Healthcare, Finance, Manufacturing, Retail)

**Current state:** 
- [business_decision_dimension_taxonomy.json](cci:7://file:///home/lorinc/CascadeProjects/ai-pilot-assessment-engine/src/data/business_decision_dimension_taxonomy.json:0:0-0:0) has **decision criteria** (what they care about)
- **Missing:** Organizational **capabilities** (what they have)

**Needed:** `organizational_context_taxonomy.json` with:
```json
{
  "AI_Maturity": ["Exploring", "Piloting", "Scaling", "Optimizing"],
  "Data_Infrastructure": ["Siloed", "Centralized", "Governed", "Real-time"],
  "ML_Team_Capability": ["None", "Outsourced", "Junior", "Mature"],
  "Industry_Sector": ["Healthcare", "Finance", "Manufacturing", "Retail", ...],
  "Company_Size": ["Startup", "SMB", "Mid-market", "Enterprise"]
}
```

---

## **2. SPARSE: Automation Opportunities (30 use cases)**

**Current:** 30 use cases across 5 categories
**Compare to:**
- Business functions: ~30 functions × ~150 processes = **4,500 touchpoints**
- Business decisions: **50+ dimensions**
- AI archetypes: **25 archetypes**

**The problem:** 
- 30 use cases cannot cover the intersection of 30 business functions
- Many functions have **zero** mapped automation opportunities
- Example: "R&D / Product Development" has no clear use case mapping

**What's needed:**
Either:
1. **Expand to 100-150 use cases** (one per major business process), OR
2. **Add semantic tags** to enable inference without exhaustive enumeration

**Recommended approach:** Add tags to existing 30 use cases:
```json
{
  "use_case": "Intelligent Document Processing & Retrieval (IDP/RAG)",
  "applicable_functions": ["Finance", "Legal", "HR", "Procurement"],
  "applicable_processes": [
    "Invoice Processing", 
    "Contract Management",
    "Compliance Documentation"
  ],
  "problem_patterns": [
    "manual_document_review",
    "knowledge_access_bottleneck",
    "compliance_verification"
  ]
}
```

---

## **3. ILL-LAYERED: AI Use Case Taxonomy**

**Current structure:** Flat list of 25 archetypes with minimal hierarchy

**Problem for inference:**
- No way to navigate from **business problem type** → **archetype family** → **specific archetype**
- Missing abstraction layers for matching

**Example of poor layering:**
```
User pain: "Too much manual data entry"
→ Which archetype? Classification? OCR? Agentic Orchestration? RAG?
→ No clear decision tree
```

**What's needed:** Add **problem-oriented groupings**:

```json
{
  "Problem_Oriented_Groups": {
    "Manual_Repetitive_Work": {
      "archetypes": ["Classification", "Agentic Orchestration", "Content Analysis"],
      "typical_outputs": ["Automated routing", "Data extraction", "Form filling"]
    },
    "Knowledge_Access_Bottleneck": {
      "archetypes": ["Information Retrieval / RAG", "Summarization", "Knowledge Graph"],
      "typical_outputs": ["Search results", "Q&A responses", "Document summaries"]
    },
    "Prediction_Uncertainty": {
      "archetypes": ["Regression & Forecasting", "Time-Series Forecasting", "Scenario Simulation"],
      "typical_outputs": ["Forecasts", "Risk scores", "What-if scenarios"]
    },
    "Quality_Reliability_Issues": {
      "archetypes": ["Anomaly Detection", "Classification", "Multimodal Fusion"],
      "typical_outputs": ["Defect alerts", "Quality scores", "Fault predictions"]
    }
  }
}
```

---

## **4. MISSING: Problem Type Taxonomy**

**Referenced in documentation but doesn't exist as a file.**

**Why it's critical:** This is the **entry point** for users who don't think in terms of "AI archetypes"

**What's needed:** `problem_type_taxonomy.json`:
```json
{
  "Problem_Types": [
    {
      "type": "Manual Effort / Repetitive Work",
      "indicators": ["high_volume", "rule_based", "copy_paste", "data_entry"],
      "maps_to_archetypes": ["Classification", "Agentic Orchestration"]
    },
    {
      "type": "Knowledge Access / Search",
      "indicators": ["document_search", "expert_dependency", "tribal_knowledge"],
      "maps_to_archetypes": ["Information Retrieval / RAG", "Summarization"]
    },
    {
      "type": "Quality / Reliability Gaps",
      "indicators": ["defects", "downtime", "errors", "inconsistency"],
      "maps_to_archetypes": ["Anomaly Detection", "Classification", "Explainability"]
    },
    {
      "type": "Prediction / Planning Uncertainty",
      "indicators": ["forecasting", "demand_planning", "resource_allocation"],
      "maps_to_archetypes": ["Regression & Forecasting", "Time-Series", "Optimization"]
    }
  ]
}
```

---

## **5. STRUCTURAL ISSUE: AI Dependency Taxonomy**

**Current:** 988 lines, very detailed, BUT organized backward for querying

**Problem:** 
- Organized as: `Prerequisite → [Models, Outputs]`
- Needed for inference: `Archetype/Output → [Prerequisites]`

**Not necessarily missing content, but needs:**
- **Reverse index** or **dual structure**
- **Prerequisite scoring** (critical vs. nice-to-have)

**Add to each archetype in [AI_use_case_taxonomy.json](cci:7://file:///home/lorinc/CascadeProjects/ai-pilot-assessment-engine/src/data/AI_use_case_taxonomy.json:0:0-0:0):**
```json
{
  "archetype": "Information Retrieval / RAG",
  "prerequisites": {
    "critical": [
      "Vector_database_infrastructure",
      "Pre-trained_models_or_APIs",
      "Unstructured_text_data"
    ],
    "recommended": [
      "NLP_Specialists",
      "Data_governance_policies"
    ],
    "optional": [
      "GPU_compute_for_training"
    ]
  }
}
```

---

## **Priority Ranking**

### **Must Add (Blocks inference):**
1. **Organizational Context Taxonomy** - Can't assess feasibility without it
2. **Problem Type Taxonomy** - Users need a business-oriented entry point

### **Should Enhance (Improves quality):**
3. **Expand Automation Opportunities** to 60-100 OR add semantic tags
4. **Add problem-oriented groupings** to AI Use Case Taxonomy
5. **Restructure AI Dependencies** for efficient querying

### **Nice to Have:**
6. Add **industry-specific variations** to automation opportunities
7. Add **complexity scores** to archetypes (simple/medium/advanced)

---

## **Bottom Line**

**Most imbalanced:** [automation_opportunity_taxonomy.json](cci:7://file:///home/lorinc/CascadeProjects/ai-pilot-assessment-engine/src/data/automation_opportunity_taxonomy.json:0:0-0:0) (30 items) vs. [business_core_function_taxonomy.json](cci:7://file:///home/lorinc/CascadeProjects/ai-pilot-assessment-engine/src/data/business_core_function_taxonomy.json:0:0-0:0) (150+ processes)

**Most critical missing:** Organizational context taxonomy - without it, you can't do feasibility assessment

**Quick win:** Add semantic tags (`problem_patterns`, `applicable_functions`) to existing taxonomies rather than expanding them 10x