The knowledge base is designed around several core entities: AI capabilities (Archetypes/Models), Implementation Requirements (Prerequisites), and Organizational Context (Maturity, Function, Sector, Problem).

To capture all knowledge and relations in a traversable knowledge graph structure, we need to define distinct JSON structures for **Nodes (Entities)** and a separate structure for **Edges (Relationships)**.

Below are the recommended JSON structures to represent the comprehensive knowledge and relations found in the sources.

---

## 1. Node Structures (Entities)

Nodes represent the core entities in the knowledge graph.

### 1.1. AI Archetype Node Structure

This captures the central AI capability, including its core attributes.

```json
{
  "node_type": "AI_ARCHETYPE",
  "archetype_id": "A_Classification",
  "name": "Classification",
  "core_task": "Assign categorical labels to new instances based on training data.",
  "agnostic_scope": "Universal supervised learning task across domains.",
  // Relationships embedded as attributes for simplicity, but defined as explicit EDGES later:
  "technical_family": "Supervised Learning", // -> Technical_Family Node
  "analytical_purposes": ["Predictive"],      // -> Analytical_Purpose Node
  "source_citation": ""
}
```

### 1.2. Common Model Node Structure

This captures the specific algorithms used.

```json
{
  "node_type": "COMMON_MODEL",
  "model_id": "M_XGBoost",
  "name": "XGBoost",
  "source_citation": ""
}
```

### 1.3. Example Output Node Structure

This captures the measurable or tangible outcomes of an AI archetype.

```json
{
  "node_type": "AI_OUTPUT",
  "output_id": "O_SalesForecast",
  "name": "Sales forecast",
  "source_citation": ""
}
```

### 1.4. AI Prerequisite Node Structure

This structure captures all implementation prerequisites, including Data Quality, Expertise, Infrastructure, MLOps, and Organizational Readiness.

```json
{
  "node_type": "AI_PREREQUISITE",
  "prereq_id": "P_GPUCompute",
  "name": "GPU_compute_for_training",
  "category": "Infrastructure", // Data_Quality, Technical_Expertise, Infrastructure, MLOps_Capabilities, etc.
  "description": "High-performance graphics processing units required for training deep neural networks.",
  "source_citation": ""
}
```

### 1.5. Organizational Context Node Structures

These nodes provide the contextual grounding for where AI is applied and the organization's readiness.

| Node Type | Example Name | Key Attributes | Source Example |
| :--- | :--- | :--- | :--- |
| **MATURITY_DIMENSION** | AI Maturity Stage | `levels`, `metrics` | |
| **BUSINESS_FUNCTION** | Manufacturing / Production | `category` (Core Value Creation) | |
| **BUSINESS_TOOL** | Production scheduling | (Associated with Functions/Sectors) | |
| **BUSINESS_SECTOR** | Aerospace & Defense Manufacturing | `category` (Primary, Industrial & Manufacturing) | |
| **PROBLEM_TYPE** | Quality or reliability gaps | (Simple list) | |

---

## 2. Edge Structures (Relationships)

Edges define the explicit links between the nodes, capturing the relationships that make the knowledge base traversable. These relationships are defined by the explicit dependencies found in the source material (e.g., `dependent_models`, `dependent_outputs`).

The edge structure should allow for referencing the source of the relationship.

### 2.1. Dependency and Composition Edges (Archetype to Model/Output)

| Edge Type | Description | Source Node (A) | Target Node (B) | Source Citation |
| :--- | :--- | :--- | :--- | :--- |
| **IMPLEMENTED_BY** | An Archetype can be realized using this Model. | AI\_ARCHETYPE | COMMON\_MODEL | (via `common_models`) |
| **PRODUCES\_OUTPUT** | An Archetype yields this specific result. | AI\_ARCHETYPE | AI\_OUTPUT | (via `example_outputs`) |
| **HAS\_PURPOSE** | Defines the objective of the Archetype. | AI\_ARCHETYPE | Analytical\_Purpose (Node or String) | (via `analytical_purpose`) |

### 2.2. Prerequisite Edges (The Core Mapping)

This set of edges directly addresses the requirement for comprehensive mapping, linking the technical elements to their necessary preconditions.

| Edge Type | Description | Source Node (A) | Target Node (B) | Source Citation |
| :--- | :--- | :--- | :--- | :--- |
| **REQUIRES** | A Model depends on a specific Prerequisite. | COMMON\_MODEL | AI\_PREREQUISITE | (via `dependent_models`) |
| **REQUIRES** | An Output depends on a specific Prerequisite. | AI\_OUTPUT | AI\_PREREQUISITE | (via `dependent_outputs`) |

### 2.3. Contextual Edges

These link the AI capabilities to the organizational context where they are relevant.

| Edge Type | Description | Source Node (A) | Target Node (B) | Source Citation |
| :--- | :--- | :--- | :--- | :--- |
| **APPLIES\_TO\_FUNCTION** | An Archetype is applicable within this function (derived from `agnostic_scope` and implied usage). | AI\_ARCHETYPE | BUSINESS\_FUNCTION | |
| **OPERATES\_IN** | A Function or Sector uses this tool/process. | BUSINESS\_FUNCTION or BUSINESS\_SECTOR | BUSINESS\_TOOL | (via `tools_and_processes`) |
| **TARGETS\_PAIN** | An Archetype addresses this organizational problem. | AI\_ARCHETYPE | PROBLEM\_TYPE | (Implied by core task/output, targeting pain points like "Cost pressure") |

### 2.4. Organizational Maturity Edges

These edges link the Maturity dimensions to the Prerequisites to enable gap analysis, as requested in the initial query.

| Edge Type | Description | Source Node (A) | Target Node (B) | Source Citation |
| :--- | :--- | :--- | :--- | :--- |
| **GOVERNED\_BY** | Maturity Dimension defines the state of a Prerequisite category. | MATURITY\_DIMENSION | AI\_PREREQUISITE (Category) | (e.g., Data Maturity governs Data Quality prerequisites) |

---

## 3. Integrated Knowledge Graph Structure (JSON Example)

A comprehensive JSON structure that bundles all nodes and edges for full traversal:

```json
{
  "knowledge_graph_schema": {
    "version": "1.0",
    "description": "Integrated schema for AI Archetypes, Prerequisites, and Organizational Context."
  },
  "nodes": [
    // 1. Core AI Capability (Archetype)
    {
      "node_id": "A_AnomalyDetection",
      "node_type": "AI_ARCHETYPE",
      "name": "Anomaly & Outlier Detection",
      "technical_family": "Unsupervised Learning"
    },
    // 2. Models
    {
      "node_id": "M_IsolationForest",
      "node_type": "COMMON_MODEL",
      "name": "Isolation Forest"
    },
    // 3. Prerequisites
    {
      "node_id": "P_LabeledTrainingData",
      "node_type": "AI_PREREQUISITE",
      "name": "Labeled_training_data",
      "category": "Data_Quality"
    },
    {
      "node_id": "P_NLPExperts",
      "node_type": "AI_PREREQUISITE",
      "name": "NLP_Specialists",
      "category": "Technical_Expertise"
    },
    // 4. Context (Function)
    {
      "node_id": "F_CustomerSupport",
      "node_type": "BUSINESS_FUNCTION",
      "name": "Customer Success / Support",
      "category": "Revenue & Growth"
    },
    // 5. Context (Tool)
    {
      "node_id": "T_HelpdeskSoftware",
      "node_type": "BUSINESS_TOOL",
      "name": "Help desk software"
    }
  ],
  "edges": [
    // Archetype -> Model (IMPLEMENTATION)
    {
      "id": "E_A1_M1",
      "source": "A_AnomalyDetection",
      "target": "M_IsolationForest",
      "relationship": "IMPLEMENTED_BY",
      "citation": ""
    },
    // Model -> Prerequisite (DEPENDENCY)
    {
      "id": "E_M1_P1",
      "source": "M_IsolationForest",
      "target": "P_LabeledTrainingData",
      "relationship": "REQUIRES",
      "prereq_type": "Data_Quality",
      "citation": ""
    },
    // Archetype -> Context (APPLICATION)
    {
      "id": "E_A1_F1",
      "source": "A_AnomalyDetection",
      "target": "F_CustomerSupport",
      "relationship": "APPLIES_TO_FUNCTION",
      "citation": "" // Implied use case for fraud/fault flagging in service ops
    },
    // Function -> Tool (OPERATIONAL REALITY)
    {
      "id": "E_F1_T1",
      "source": "F_CustomerSupport",
      "target": "T_HelpdeskSoftware",
      "relationship": "OPERATES_IN",
      "citation": ""
    }
  ]
}
```