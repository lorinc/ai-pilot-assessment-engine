#!/usr/bin/env python3
"""
One-time script to add component target tags to project_scope_taxonomy.json

Purpose:
    Adds metadata section and "targets" field to each taxonomy item to enable
    direct inference from output quality gaps to specific improvement recommendations.

Usage:
    python3 tools/add_component_targets.py

What it does:
    1. Adds metadata.component_mapping section with 4 components:
       - team_execution
       - system_capabilities
       - process_maturity
       - dependency_quality
    
    2. Tags each of 170 taxonomy items with which component(s) it improves
    
    3. Restructures JSON from array to object with metadata + taxonomy

Result:
    Enables simple inference: filter(taxonomy, item.targets.includes(bottleneck))

Created: 2025-11-02
Status: COMPLETED - Taxonomy updated successfully
"""

import json

# Load the current taxonomy
with open('/home/lorinc/CascadeProjects/ai-pilot-assessment-engine/src/data/project_scope_taxonomy.json', 'r') as f:
    taxonomy = json.load(f)

# Define component metadata
metadata = {
    "component_mapping": {
        "team_execution": {
            "name": "Team Execution Ability",
            "description": "Current capability of the team to execute the process step"
        },
        "system_capabilities": {
            "name": "System Capabilities",
            "description": "Current capabilities provided by the system/tools"
        },
        "process_maturity": {
            "name": "Process Maturity",
            "description": "Current maturity level of the process (standards, automation, monitoring)"
        },
        "dependency_quality": {
            "name": "Dependency Quality",
            "description": "Quality of upstream outputs this output depends on"
        }
    }
}

# Define target mappings based on what each item improves
# Key patterns:
# - Infrastructure/system items -> system_capabilities
# - Monitoring/testing/automation -> process_maturity
# - Data quality/validation -> dependency_quality
# - Training/hiring/expertise -> team_execution

target_rules = {
    # Data Acquisition - mostly system capabilities (infrastructure to get data)
    "streaming event ingestion": ["system_capabilities"],
    "change data capture replication": ["system_capabilities"],
    "web scraping at scale": ["system_capabilities", "process_maturity"],
    "email-to-data parsing": ["system_capabilities", "process_maturity"],
    "webhook ingestion pipeline": ["system_capabilities"],
    "Large historical datasets": ["dependency_quality"],
    "Sufficient training samples": ["dependency_quality"],
    "Continuous data streams": ["system_capabilities"],
    "Transactional or event data": ["dependency_quality"],
    "Third-party data enrichment integration": ["system_capabilities", "dependency_quality"],
    "External prospecting data integration": ["system_capabilities", "dependency_quality"],
    "Organizational metadata enrichment": ["dependency_quality"],
    "Contact data verification services": ["dependency_quality", "process_maturity"],
    "Transactional system integration": ["system_capabilities"],
    "Social platform data ingestion": ["system_capabilities"],
    "Environmental and location data feeds": ["system_capabilities", "dependency_quality"],
    "Market and reference data feeds": ["system_capabilities", "dependency_quality"],
    
    # Data Transformation - process + dependency quality
    "slowly changing dimension handling": ["process_maturity", "dependency_quality"],
    "Dimensional modeling design": ["process_maturity", "team_execution"],
    "geocoding enrichment": ["dependency_quality"],
    "Multi-tier data quality layering": ["process_maturity", "dependency_quality"],
    "data contract authoring": ["process_maturity", "dependency_quality"],
    "Time-indexed sequential data": ["dependency_quality"],
    "Unstructured text data": ["dependency_quality"],
    "Structured tabular data": ["dependency_quality"],
    "Graph or network data": ["dependency_quality"],
    "Multimodal data": ["dependency_quality"],
    "Semantic representation indexing": ["system_capabilities", "dependency_quality"],
    "Address standardization and normalization": ["dependency_quality", "process_maturity"],
    "Phone number parsing and validation": ["dependency_quality", "process_maturity"],
    "Currency conversion and normalization": ["dependency_quality", "process_maturity"],
    "Text normalization and cleaning": ["dependency_quality", "process_maturity"],
    "Date and timezone standardization": ["dependency_quality", "process_maturity"],
    "Null value handling strategy": ["dependency_quality", "process_maturity"],
    "Duplicate detection and resolution": ["dependency_quality", "process_maturity"],
    
    # Performance & Infrastructure - system capabilities
    "table clustering optimization": ["system_capabilities"],
    "spot instance utilization": ["system_capabilities"],
    "materialized view creation": ["system_capabilities"],
    "query cost guardrails": ["system_capabilities", "process_maturity"],
    "Accelerated compute for training": ["system_capabilities"],
    "Real-time inference infrastructure": ["system_capabilities"],
    "Vector database infrastructure": ["system_capabilities"],
    "Distributed computing systems": ["system_capabilities"],
    "Model serving infrastructure": ["system_capabilities"],
    "Data warehouse query optimization": ["system_capabilities", "process_maturity"],
    "Incremental data loading patterns": ["process_maturity", "system_capabilities"],
    "Data compression strategies": ["system_capabilities"],
    "Partitioning and bucketing strategies": ["system_capabilities", "process_maturity"],
    "Cold storage archival policies": ["system_capabilities", "process_maturity"],
    
    # Data Quality - dependency quality + process maturity
    "golden dataset certification": ["dependency_quality", "process_maturity"],
    "Data validation test suites": ["dependency_quality", "process_maturity"],
    "record linkage and deduplication": ["dependency_quality", "process_maturity"],
    "reconciliation across systems": ["dependency_quality", "process_maturity"],
    "mean time to resolve data issues": ["process_maturity", "team_execution"],
    "Clean and validated data": ["dependency_quality"],
    "Labeled training data": ["dependency_quality", "team_execution"],
    "Data consistency and completeness": ["dependency_quality"],
    "Normalized and standardized features": ["dependency_quality", "process_maturity"],
    "Bias-free and representative datasets": ["dependency_quality", "team_execution"],
    "Field-level statistics tracking": ["dependency_quality", "process_maturity"],
    "Null rate monitoring and alerting": ["dependency_quality", "process_maturity"],
    "Cardinality drift detection": ["dependency_quality", "process_maturity"],
    "Row count anomaly detection": ["dependency_quality", "process_maturity"],
    "Data freshness SLA monitoring": ["dependency_quality", "process_maturity"],
    "Schema drift detection and alerts": ["dependency_quality", "process_maturity"],
    "Referential integrity validation": ["dependency_quality", "process_maturity"],
    "Business rule validation checks": ["dependency_quality", "process_maturity"],
    "Outlier detection and flagging": ["dependency_quality", "process_maturity"],
    "Data quality scorecards": ["dependency_quality", "process_maturity"],
    "Automated data profiling": ["dependency_quality", "process_maturity"],
    
    # Security & Governance - process maturity
    "Sensitive data masking": ["process_maturity", "system_capabilities"],
    "tokenization of sensitive fields": ["process_maturity", "system_capabilities"],
    "row level security filters": ["system_capabilities", "process_maturity"],
    "Data subject rights request workflow": ["process_maturity", "system_capabilities"],
    "Input validation and sanitization": ["process_maturity", "system_capabilities"],
    "data encryption at rest": ["system_capabilities", "process_maturity"],
    "Ethics and fairness review board": ["process_maturity", "team_execution"],
    "Data governance policies": ["process_maturity"],
    "Compliance and legal experts": ["team_execution", "process_maturity"],
    
    # Pipeline Operations - process maturity
    "idempotent job design": ["process_maturity"],
    "blue green pipeline deploys": ["process_maturity", "system_capabilities"],
    "root cause analysis automation": ["process_maturity", "system_capabilities"],
    "pipeline repair agent": ["system_capabilities", "process_maturity"],
    "platform observability rollout": ["process_maturity", "system_capabilities"],
    "dependency graph orchestration": ["process_maturity", "system_capabilities"],
    "Pipeline execution time monitoring": ["process_maturity", "dependency_quality"],
    "Job failure rate tracking": ["process_maturity", "dependency_quality"],
    "Data pipeline testing framework": ["process_maturity"],
    "Pipeline version control": ["process_maturity"],
    "Automated pipeline documentation": ["process_maturity"],
    "Cost monitoring per pipeline": ["process_maturity"],
    "Data lineage visualization": ["process_maturity", "dependency_quality"],
    "Pipeline health dashboards": ["process_maturity"],
    "Alerting escalation policies": ["process_maturity"],
    "Pipeline retry and backoff strategies": ["process_maturity", "system_capabilities"],
    
    # Disaster Recovery - system capabilities + process maturity
    "cross cloud data replication": ["system_capabilities"],
    "multi region failover setup": ["system_capabilities", "process_maturity"],
    "disaster recovery testing": ["process_maturity"],
    "rpo rto validation": ["process_maturity"],
    "time travel retention policy": ["system_capabilities", "process_maturity"],
    "Automated backup verification": ["process_maturity", "system_capabilities"],
    "Data retention policy enforcement": ["process_maturity", "system_capabilities"],
    "Point-in-time recovery testing": ["process_maturity"],
    
    # MLOps - system + process
    "feature store online serving": ["system_capabilities"],
    "shadow deployment of models": ["process_maturity", "system_capabilities"],
    "hyperparameter search service": ["system_capabilities", "process_maturity"],
    "fairness evaluation reports": ["process_maturity", "team_execution"],
    "feature/Data/Concept drift detection": ["process_maturity", "dependency_quality"],
    "Model versioning and tracking": ["process_maturity", "system_capabilities"],
    "Automated retraining workflows": ["process_maturity", "system_capabilities"],
    "Controlled experiment framework": ["process_maturity", "system_capabilities"],
    "Continuous monitoring pipelines": ["process_maturity", "system_capabilities"],
    "Feature store": ["system_capabilities"],
    
    # GenAI - system + team
    "Semantic search indexing": ["system_capabilities", "process_maturity"],
    "multi agent collaboration protocol": ["system_capabilities", "process_maturity"],
    "Output factuality verification": ["process_maturity", "system_capabilities"],
    "Query language generation": ["system_capabilities"],
    "knowledge graph construction": ["system_capabilities", "process_maturity"],
    "Agentic Orchestration (archetype)": ["system_capabilities"],
    "Retrieval-augmented generation (archetype)": ["system_capabilities"],
    "Language & Sequence Generation (archetype)": ["system_capabilities"],
    "AI interaction design expertise": ["team_execution"],
    "External integration ecosystem": ["system_capabilities"],
    "Document segmentation strategy": ["process_maturity", "dependency_quality"],
    "Reward signal design": ["team_execution", "process_maturity"],
    
    # Advanced Analytics - system + team
    "Customer value modeling pipeline": ["system_capabilities", "team_execution"],
    "Experiment registry": ["process_maturity"],
    "demand forecasting pipeline": ["system_capabilities", "team_execution"],
    "dynamic pricing policy": ["system_capabilities", "team_execution"],
    "route optimization service": ["system_capabilities", "team_execution"],
    "Anomaly & Outlier Detection (archetype)": ["system_capabilities", "team_execution"],
    "Classification (archetype)": ["system_capabilities", "team_execution"],
    "Optimization & Scheduling (archetype)": ["system_capabilities", "team_execution"],
    "Causal Inference & Uplift Modeling (archetype)": ["system_capabilities", "team_execution"],
    "Scenario Simulation / What-If Engines (archetype)": ["system_capabilities", "team_execution"],
    "Causal graph or domain theory": ["team_execution"],
    
    # Data Consumption - system + process
    "Semantic layer for metrics": ["system_capabilities", "process_maturity"],
    "automated commentary on dashboards": ["system_capabilities"],
    "report redundancy pruning": ["process_maturity"],
    "Executive metrics automation": ["system_capabilities", "process_maturity"],
    "report access personalization": ["system_capabilities", "process_maturity"],
    "Explainability / Interpretability (archetype)": ["system_capabilities", "team_execution"],
    "Human-in-the-Loop Validation (archetype)": ["process_maturity", "team_execution"],
    
    # Data Sharing - system + process
    "Operational data activation": ["system_capabilities", "process_maturity"],
    "Audience segment synchronization": ["system_capabilities", "process_maturity"],
    "Data access monetization metering": ["system_capabilities", "process_maturity"],
    "secure data sandbox for partners": ["system_capabilities", "process_maturity"],
    "webhook event catalog": ["system_capabilities", "process_maturity"],
    "Behavioral intent data enrichment": ["dependency_quality", "system_capabilities"],
    "Identity resolution platform integration": ["system_capabilities", "dependency_quality"],
    "Attribution data activation": ["system_capabilities", "process_maturity"],
    "Usage metrics to operational systems sync": ["system_capabilities", "process_maturity"],
    
    # Organizational - team + process
    "data readiness scorecards": ["process_maturity", "dependency_quality"],
    "Data product service level objectives": ["process_maturity"],
    "value tracking for data products": ["process_maturity"],
    "skill matrix mapping for data team": ["team_execution", "process_maturity"],
    "owner discovery automation": ["process_maturity", "system_capabilities"],
    "Data scientists and ML engineers": ["team_execution"],
    "ML operations engineers": ["team_execution"],
    "Natural language processing specialists": ["team_execution"],
    "Business domain experts": ["team_execution"],
    "Change management capabilities": ["team_execution", "process_maturity"],
    
    # Documentation - team + process
    "data catalog curation": ["process_maturity", "team_execution"],
    "lineage impact analysis": ["process_maturity", "system_capabilities"],
    "golden path documentation": ["process_maturity", "team_execution"],
    "data-driven onboarding tours": ["process_maturity", "team_execution"],
    "reusable query snippet library": ["process_maturity", "team_execution"],
    "Content Analysis / Labeling / Evaluation (archetype)": ["team_execution", "process_maturity"],
    "Summarization & Compression (archetype)": ["system_capabilities", "team_execution"],
    "Multi-hop Reasoning / Chain-of-Thought (archetype)": ["system_capabilities", "team_execution"],
}

# Add targets to each item
for domain in taxonomy:
    for category in domain.get("categories", []):
        for example in category.get("examples", []):
            name = example["name"]
            if name in target_rules:
                example["targets"] = target_rules[name]
            else:
                # Default fallback - try to infer
                print(f"Warning: No target rule for '{name}', using default")
                example["targets"] = ["process_maturity"]

# Create new structure with metadata
output = {
    "metadata": metadata,
    "taxonomy": taxonomy
}

# Write the updated taxonomy
with open('/home/lorinc/CascadeProjects/ai-pilot-assessment-engine/src/data/project_scope_taxonomy.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✓ Added metadata and targets to taxonomy")
print(f"✓ Total items tagged: {sum(len(cat.get('examples', [])) for domain in taxonomy for cat in domain.get('categories', []))}")
