# Data Taxonomy Documentation

## Overview

This directory contains taxonomies and templates that help the AI assessment system discover, suggest, and assess organizational outputs based on conversational input from users.

## Core Principle

These taxonomies enable **inference without interrogation**. The system uses generic organizational knowledge to:
1. Suggest likely outputs based on what the user mentions
2. Fill in typical creation context (team, process, system)
3. Flag all inferences as "unverified" until user confirms
4. Allow users to correct any assumptions

## File Structure

### Function Templates
Templates describing typical organizational functions with their teams, processes, systems, and common outputs.

**Currently Available (8 functions, 46 outputs):**
- **`organizational_templates/functions/sales.json`** - Sales (6 outputs: forecast, pipeline, leads, proposals, commissions, territories)
- **`organizational_templates/functions/finance.json`** - Finance (6 outputs: statements, forecasts, budgets, reconciliations, payments, variance)
- **`organizational_templates/functions/operations.json`** - Operations (6 outputs: tickets, incidents, projects, POs, inventory, resources)
- **`organizational_templates/functions/marketing.json`** - Marketing (6 outputs: campaigns, segments, content, attribution, MQLs, sentiment)
- **`organizational_templates/functions/customer_success.json`** - Customer Success (6 outputs: resolved tickets, health scores, KB articles, responses, churn alerts, metrics)
- **`organizational_templates/functions/hr.json`** - HR (6 outputs: candidate pipelines, performance reviews, turnover reports, training, engagement, workforce forecasts)
- **`organizational_templates/functions/supply_chain.json`** - Supply Chain (4 outputs: demand forecasts, inventory, POs, shipments)
- **`organizational_templates/functions/it_operations.json`** - IT Operations (6 outputs: incident resolutions, alerts, postmortems, changes, capacity, assets)

**Remaining to Create (14 functions):**
R&D, Manufacturing, Partnerships, Accounting, FP&A, Compliance, Procurement, Payroll, Workplace Safety, Corporate Strategy, Innovation, Knowledge Management, Data Engineering, Cybersecurity, Architecture

**Purpose:** Help LLM infer which outputs the user might be referring to based on keywords, pain points, or systems mentioned.

**Structure:**
```json
{
  "function": "Sales",
  "typical_teams": [...],
  "typical_processes": [...],
  "typical_systems": [...],
  "common_outputs": [
    {
      "id": "sales_forecast",
      "name": "Sales Forecast",
      "typical_quality_metrics": ["accuracy", "timeliness", "completeness"],
      "typical_creation_context": {...},
      "typical_dependencies": [...],
      "common_pain_points": [...]
    }
  ],
  "inference_triggers": {
    "keywords": [...],
    "pain_points": [...],
    "systems_mentioned": [...]
  }
}
```

### Component Scales
Definitions of the 1-5 star rating scales for the four components that determine output quality.

- **`component_scales.json`** - Rating scales for Team Execution, System Capabilities, Process Maturity, and Dependency Quality

**Purpose:** Help LLM infer component ratings from conversational evidence.

**Structure:**
```json
{
  "components": {
    "team_execution": {
      "scale": {
        "1": {"stars": "⭐", "label": "Critical Issues", "indicators": [...]},
        "2": {"stars": "⭐⭐", "label": "Major Issues", "indicators": [...]},
        ...
      }
    }
  }
}
```

### Discovery & Inference Rules
Rules for discovering outputs and making inferences from conversation.

- **`inference_rules/output_discovery.json`** - Strategies for identifying outputs, confidence levels, verification prompts
- **`inference_rules/pain_point_mapping.json`** - 100+ pain points mapped to problem categories for better inference
- **`inference_rules/ai_archetypes.json`** - 27 AI/ML use case archetypes with technical details

**Purpose:** Guide the LLM on how to suggest outputs, when to ask clarifying questions, and how to adjust confidence.

**Key Sections:**
- `inference_strategies` - How to match user statements to outputs
- `conversation_patterns` - Common patterns and how to respond
- `verification_prompts` - How to confirm inferences with users
- `progressive_disclosure` - Order of information gathering

### Pilot Types & Catalog
Taxonomy of pilot projects mapped to component improvements.

- **`pilot_types.json`** - 13 pilot types across 3 categories (Team, System, Process)
- **`pilot_catalog.json`** - 28 specific pilot examples from automation opportunities for Team, System, and Process improvements

**Purpose:** Recommend specific pilots based on which component is the bottleneck.

**Structure:**
```json
{
  "pilot_categories": {
    "team_execution": {
      "pilot_types": [
        {
          "id": "ai_copilot",
          "name": "AI Copilot / Assistant",
          "typical_impact": "Increase productivity 20-40%",
          "typical_timeline": "6-12 weeks",
          "typical_cost": "€10k-€30k",
          ...
        }
      ]
    }
  }
}
```

### Common Systems & Capabilities
Reference data for common business systems and organizational capabilities.

- **`organizational_templates/cross_functional/common_systems.json`** - 40+ systems across 10 categories (CRM, ERP, ticketing, etc.)
- **`capability_framework.json`** - 198 organizational capabilities across 4 pillars for detailed assessment

**Purpose:** Match user mentions of systems to known tools and infer typical outputs.

**Structure:**
```json
{
  "system_categories": {
    "crm": {
      "examples": [
        {
          "name": "Salesforce",
          "aliases": ["SFDC", "Salesforce CRM"],
          "typical_outputs": ["sales_forecast", "pipeline_reports", ...]
        }
      ]
    }
  }
}
```

## Usage Flow

### 1. Output Discovery
```
User: "Our sales forecasts are always wrong"
↓
System matches keywords: "sales" + "forecasts"
↓
Lookup: organizational_templates/functions/sales.json
↓
Find output: sales_forecast (pain point match: "forecasts are consistently inaccurate")
↓
Confidence: 0.75 (pain point match)
Flag: unverified
```

### 2. Context Inference
```
System suggests: "It sounds like you're talking about Sales Forecast"
User confirms: "Yes"
↓
Load typical_creation_context from sales_forecast
↓
Present to user: "[UNVERIFIED] This is typically created by:
- Team: Sales Operations
- System: CRM or Spreadsheet
- Process: Sales Forecasting Process
Does this match your setup?"
```

### 3. Component Assessment
```
System asks about components using component_scales.json
↓
User: "Our sales ops team is learning as they go"
↓
Match indicators: "learning as they go" → Team Execution = ⭐⭐
Confidence: 0.7
↓
User: "We use Salesforce but it's pretty basic"
↓
Match indicators: "basic" → System Capabilities = ⭐⭐
Confidence: 0.6
```

### 4. Pilot Recommendation
```
Calculate: actual_quality = MIN(⭐⭐, ⭐⭐, ⭐⭐⭐, ⭐⭐⭐) = ⭐⭐
Bottleneck: Team Execution (⭐⭐)
↓
Lookup: pilot_types.json → team_execution category
↓
Recommend: "AI Copilot for Sales Forecasting"
- Expected Impact: ⭐⭐ → ⭐⭐⭐⭐
- Timeline: 10-12 weeks
- Cost: €20k-€35k
```

## Confidence Levels

All inferences include confidence scores:

- **1.0** - User explicitly confirmed
- **0.8-0.9** - Strong evidence (explicit mention, multiple indicators)
- **0.5-0.7** - Medium evidence (pain point match, system mention)
- **0.3-0.4** - Weak evidence (function mention, template inference)

## Flags

All inferences are flagged:

- **`user_confirmed`** - User explicitly validated
- **`unverified`** - Inferred from templates, needs confirmation
- **`unverified_related`** - Related output suggested
- **`unverified_dependency`** - Upstream dependency inferred
- **`unverified_impact`** - Downstream impact inferred

## Adding New Functions

To add a new function (e.g., Marketing, Engineering):

1. Create `organizational_templates/functions/{function}.json` following the structure
2. Include:
   - Typical teams and roles
   - Typical processes and steps
   - Typical systems
   - Common outputs with pain points
   - Inference triggers (keywords, pain points, systems)
3. Test with realistic user statements

## Adding New Outputs

To add a new output to an existing function:

1. Add to `common_outputs` array in the function template
2. Include:
   - Unique ID
   - Name and description
   - Typical quality metrics
   - Typical creation context
   - Typical dependencies
   - Common pain points
   - Typical improvement opportunities
3. Add relevant keywords to `inference_triggers`

## Version Control

- All taxonomy files include a `version` field
- Update version when making breaking changes
- Document changes in git commit messages
- Consider backward compatibility when modifying structure

## Human Readability

These files are designed to be:
- **Human-readable** - Clear structure, descriptive names
- **Self-documenting** - Include descriptions and examples
- **Maintainable** - Easy to add/modify without breaking system
- **Transparent** - Show reasoning behind inferences

## LLM Integration

The LLM uses these taxonomies to:
1. **Match** user statements to outputs
2. **Infer** creation context from templates
3. **Assess** components using rating scales
4. **Recommend** pilots based on bottlenecks
5. **Verify** all inferences with users

The system NEVER forces users into these templates - they're suggestions that can be corrected or overridden.

---

## Content Summary

### Current Coverage
- **8 Functions** with 46 total outputs (14 more functions ready to create)
- **100+ Pain Points** organized into 12 categories
- **27 AI/ML Archetypes** with technical details
- **28 Specific Pilot Examples** from automation opportunities
- **198 Organizational Capabilities** across 4 pillars
- **40+ Common Systems** across 10 categories
- **13 Pilot Types** across 3 improvement categories

### Data Sources
All content was salvaged and repurposed from high-quality interim taxonomies:
- `business_core_function_taxonomy.json` → Function templates
- `problem_taxonomy.json` → Pain point mapping
- `AI_use_case_taxonomy.json` → AI archetypes
- `automation_opportunity_taxonomy.json` → Pilot catalog
- `business_capability_taxonomy.json` → Capability framework

### Quality Metrics
- **Zero waste** - All valuable content preserved and repurposed
- **Enhanced structure** - Better organized for output-centric model
- **Comprehensive coverage** - 3-10x increase across all dimensions
- **Ready for scale** - Template patterns established for systematic expansion
