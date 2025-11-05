### I. Value & Impact Quantification (Grounded in Business Reality)

To determine which AI project would benefit an organization *best*, the graph must explicitly model the potential return on investment (ROI) by linking technical outputs to specific business outcomes.

| New Dimension (Node Type) | Description | Recommended Edges | Source Connection |
| :--- | :--- | :--- | :--- |
| **Quantifiable Business Metric** | Nodes representing the specific KPIs or financial metrics that the AI solution is intended to move (e.g., Customer Acquisition Cost, Inventory Turnover Rate, Production Yield, Mean Time to Resolution). | `IMPROVES_METRIC_X_BY`: Links the `AI Archetype` output (e.g., "Sales forecast") to the targeted `Business Metric` (e.g., Accuracy of Revenue Forecasting). | Connects `Example Outputs` to `Business Functions` and the strategic dimension of `Corporate Strategy / BI`. |
| **Severity of Pain Point** | A scale (e.g., Low, Medium, High) quantifying the current negative impact of the `Problem_or_Pain_Type` within a specific `Business Function`. | `TARGETS_PAIN_AT_SEVERITY`: Links a `Business Function` (e.g., Manufacturing) to a `Problem or Pain Type` (e.g., "Quality or reliability gaps") and assigns a severity rating. | Connects `Problem_or_Pain_Type` to `Business Function` nodes. |
| **Causal Linkage** | Modeling the hypothesized mechanism by which an AI intervention causes a specific business improvement. | `EXPLAINS_DRIVE_IN_METRIC`: Links `Causal Inference & Uplift Modeling` to the resulting `Marketing lift` or `Policy impact estimation`. | Crucial for leveraging `Causal Analysis` and `Structural Causal Models`. |

### II. Feasibility & Cost Assessment (Grounded in Effort)

For a recommendation to be realistic, it must account for the current deficit between the organization's **Maturity** and the **Prerequisites** required by the project.

| New Dimension (Node Type) | Description | Recommended Edges | Source Connection |
| :--- | :--- | :--- | :--- |
| **Prerequisite Deficit Score** | Quantifies the gap between a required prerequisite (e.g., "GPU compute for training") and the organization's existing `Technical Stack Sophistication` or current `Infrastructure`. | `REQUIRES_GAP_FILLING`: Links a specific `AI Prerequisite` (e.g., "Labeled training data") to the `AI Maturity Stage` of the organization (e.g., "Exploring") and calculates the necessary investment (cost/time). | Links `Organizational Maturity` and `Technical Stack Sophistication` directly to the detailed `AI Implementation Prerequisites`. |
| **Implementation Complexity Level** | Categorizes the required `Technical Expertis`e and `Infrastructure` for an `AI Archetype` (e.g., Basic, Intermediate, Advanced). For example, `Generative Modeling` would require high complexity due to dependence on "GPU compute for training". | `HAS_COMPLEXITY_LEVEL`: Assigns a level of effort to the `Common Models` and `Technical Family`. | Leverages specific expert roles like `MLOps Engineers` and `Data Scientists` required for deployment and maintenance. |
| **Data Effort Requirement** | Quantifies the effort to secure the required data format and quality (e.g., low effort for `Structured tabular data` if data maturity is high; high effort for `Bias-free and representative datasets` if governance is poor). | `DATA_REMEDIATION_COST`: Links the `Data Quality` dimension to the organization's current `Data Maturity` level and flags archetypes requiring significant `Annotation and labeling services`. | Uses specific data needs (e.g., `Time-indexed sequential data`) and connects them to organizational readiness for labeling. |

### III. Operational Integration & Process Alignment

To ensure a project is actionable, it must align with or augment the existing workflows, tools, and processes detailed in the Business Function and Business Sector structures.

| New Dimension (Node Type) | Description | Recommended Edges | Source Connection |
| :--- | :--- | :--- | :--- |
| **Targeted Tool / System** | The specific existing technology or platform that the AI solution will interface with or replace, drawn directly from the detailed lists of `tools_and_processes`. | `AUGMENTS_TOOL`: Links a `Common Model` (e.g., `BERT-based classifiers`) to a specific tool (e.g., "Help desk software" or "CRM systems") for `Intent Detection & Routing`. | This makes the connection concrete: the `Intent Detection` archetype is linked to the `Customer Success / Support` function, which `USES_TOOL` (Help desk software). The AI solution *augments* this tool. |
| **Process Change Score** | A dimension assessing the necessary `Change management capabilities` required for a successful implementation. Projects involving `Autonomous control policy` will typically require a higher change score than those providing merely an `Executive summary`. | `REQUIRES_PROCESS_OVERHAUL`: Links the `AI Archetype` to the needed level of `Change management capabilities` within `Organizational Readiness`. | Leverages the distinction between prescriptive/autonomous archetypes (`Reinforcement Learning`) and diagnostic/generative archetypes. |
| **Data Source Specificity** | Connects the abstract data requirements to concrete organizational data assets derived from sector/function-specific tools. | `DATA_IS_SOURCED_FROM`: Links a `Data Format/Structure` prerequisite (e.g., `Time-indexed sequential data`) to the specific `tools_and_processes` (e.g., "Production scheduling" or "SCADA systems") within the organization's sector. | Grounding abstract prerequisites (like `Transactional_or_event_data`) to concrete systems listed across `Business Sectors`. |

### IV. Risk and Governance Profile

Realistic AI project selection must account for governance requirements, especially for high-stakes applications.

| New Dimension (Node Type) | Description | Recommended Edges | Source Connection |
| :--- | :--- | :--- | :--- |
| **Regulatory Domain** | Specifies the governing regulatory frameworks (e.g., HIPAA, GDPR, ISO 27001, CMMC, AS9100) that apply to a specific `Business Sector` or `Example Output`. | `GOVERNED_BY_REGULATION`: Links the `Business Sector` (e.g., "Hospitals & Clinics") to the `Regulatory Domain` (e.g., HIPAA compliance). | Connects `Compliance & Risk` and `Legal Services & Compliance` functions/sectors to the required governance frameworks. |
| **Explainability Requirement** | Flags whether an AI output (especially a high-stakes one) needs high `Explainability / Interpretability` to meet internal or external standards. | `REQUIRES_XAI`: Links high-stakes `Example Outputs` (e.g., "Price estimation" or "Defect classification") to the need for models like `SHAP` or `LIME`. | Links outputs from high-stakes predictive models directly to the `Explainability / Interpretability` archetype and the `Compliance and legal experts` prerequisite. |
| **Bias/Drift Monitoring Need** | Flags use cases that are highly susceptible to data drift or bias, mandating continuous `MLOps Capabilities`. | `SUSCEPTIBLE_TO_DRIFT`: Links `Adaptive Feedback Loops` and high-frequency `Predictive` archetypes to the need for `Continuous monitoring pipelines` and the `Bias / Drift Detection` archetype. | Connects specific model types (e.g., `Online Learning`, `Bandit Algorithms`) to the required MLOps capabilities. |