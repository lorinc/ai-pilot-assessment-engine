# Next Tasks - Scoped Factor Model Implementation

**Created:** 2024-10-30  
**Priority:** High - Blocker for Epic 1

---

## Task 1: Update Architecture Documents

**Status:** Pending  
**Estimated Time:** 2-3 hours

### Files to Update

1. **`docs/architecture_summary.md`**
   - Replace organization-wide factor model with scoped instances
   - Update data flow examples to show scope matching
   - Add scope inheritance logic to architecture diagrams

2. **`docs/gcp_data_schemas.md`**
   - Replace `/users/{user_id}/factors/{factor_id}` schema
   - Add `/users/{user_id}/factor_instances/{instance_id}` schema
   - Add scope registry schema
   - Update example documents with scope fields

3. **`docs/exploratory_assessment_architecture.md`**
   - Update cumulative inference section to handle scoped instances
   - Add scope matching logic to context retrieval
   - Update confidence calculation to account for scope match quality

4. **`docs/gcp_technical_architecture.md`**
   - Update Firestore collections structure
   - Add scope matching queries to API contracts
   - Update security rules for factor_instances collection

### Specific Changes

**Before:**
```
Factor: data_quality = 40 (organization-wide)
```

**After:**
```
Factor Instances:
- data_quality {domain: "sales", system: "salesforce_crm"} = 30
- data_quality {domain: "sales", system: null} = 45
- data_quality {domain: "finance", system: "sap_erp"} = 85
```

---

## Task 2: Update UX Guidelines

**Status:** Pending  
**Estimated Time:** 2 hours

### Files to Update

1. **`docs/user_interaction_guideline.md`**
   - Add clarifying question patterns (narrow, generalize, identify, resolve)
   - Add scope-aware conversation examples
   - Update "what's next" suggestions to be scope-aware

2. **`README.md`**
   - Update examples to show scoped assessments
   - Add "intelligent scope discovery" to key features

### New Sections to Add

**Clarifying Question Patterns:**
- When to ask "Is this across all systems or specific tools?"
- When to ask "Do other domains have similar issues?"
- How to resolve contradictions between generic and specific

**Scope-Aware Responses:**
- "For sales forecasting using Salesforce data specifically..."
- "I don't have info about your data warehouse, but sales data generally..."
- "This affects both Salesforce AND spreadsheets, suggesting a broader issue..."

---

## Task 3: Knowledge Graph-Based Question Inference

**Status:** Pending  
**Estimated Time:** 3-4 hours (design + implementation)

### Objective

Enable the system to ask intelligent questions about unknown systems/domains by querying the knowledge graph.

### Example Scenario

```
User: "Our Cogglepoop system has data quality issues"

System detects:
- "Cogglepoop" is not in scope registry
- User mentioned it in context of data quality
- Need to understand: domain, team, purpose

System queries KG:
- What domains typically have "systems"? (sales, finance, operations, etc.)
- What are common system purposes? (CRM, ERP, analytics, etc.)

System asks:
"I'm not familiar with Cogglepoop. Could you help me understand:
- Which team or department uses it?
- What's it used for - customer data, financial data, operations?"

User: "It's our custom CRM for the sales team"

System updates:
- Scope registry: systems.sales.push("cogglepoop_crm")
- Creates instance: data_quality {domain: "sales", system: "cogglepoop_crm"}
- Links to knowledge: "custom CRM" → similar to "salesforce_crm"
```

### Implementation Approach

**Phase 1: Unknown System Detection**
```python
def detect_unknown_system(user_statement):
    """
    Identify mentions of systems not in scope registry.
    """
    # Extract potential system names (NER or LLM)
    mentioned_systems = extract_systems(user_statement)
    
    # Check against registry
    unknown = [s for s in mentioned_systems if s not in scope_registry.all_systems]
    
    return unknown
```

**Phase 2: KG-Based Question Generation**
```python
def generate_system_discovery_questions(unknown_system, context):
    """
    Use KG to generate intelligent questions about unknown system.
    """
    # Query KG for common system categories
    system_categories = kg.get_node_types("SYSTEM")
    # e.g., ["CRM", "ERP", "Analytics", "Custom Database"]
    
    # Query KG for common domains
    domains = kg.get_node_types("DOMAIN")
    # e.g., ["sales", "finance", "operations", "hr"]
    
    return {
        "question": f"I'm not familiar with {unknown_system}. Could you help me understand:",
        "sub_questions": [
            f"Which team or department uses it? ({', '.join(domains[:5])})",
            f"What type of system is it? ({', '.join(system_categories[:5])})"
        ],
        "intent": "discover_system_scope"
    }
```

**Phase 3: Scope Registry Update**
```python
def update_scope_registry(system_name, domain, system_type):
    """
    Add newly discovered system to registry.
    """
    scope_registry.systems[domain].append(system_name)
    scope_registry.system_metadata[system_name] = {
        "type": system_type,
        "domain": domain,
        "discovered_at": timestamp,
        "similar_to": find_similar_systems(system_type)
    }
```

**Phase 4: Similarity Inference**
```python
def find_similar_systems(system_type):
    """
    Find known systems of similar type for inference.
    """
    # If user says "custom CRM", find other CRMs
    similar = kg.query(
        node_type="SYSTEM",
        attributes={"type": system_type}
    )
    return [s.id for s in similar]
```

### KG Schema Additions

**New Node Type: SYSTEM_CATEGORY**
```json
{
  "node_type": "SYSTEM_CATEGORY",
  "category_id": "crm",
  "category_name": "Customer Relationship Management",
  "common_domains": ["sales", "marketing"],
  "typical_data_types": ["customer_data", "transactional"],
  "examples": ["salesforce", "hubspot", "dynamics"]
}
```

**New Edge Type: SIMILAR_TO**
```json
{
  "source": "cogglepoop_crm",
  "target": "salesforce_crm",
  "relationship": "SIMILAR_TO",
  "similarity_score": 0.85,
  "reason": "Both are CRM systems for sales"
}
```

### Deliverables

1. **Unknown system detection** in conversation orchestrator
2. **KG-based question templates** for system discovery
3. **Scope registry update logic** with metadata
4. **Similarity inference** for unknown systems
5. **Updated KG schema** with SYSTEM_CATEGORY nodes

---

## Task 4: Update Taxonomy Files

**Status:** Pending  
**Estimated Time:** 2-3 hours

### Files to Create/Update

1. **`src/data/organizational_factors.json`** (NEW)
   - Add scope_dimensions to each factor
   - Add allows_generic_scope flag
   - Add clarifying_question_templates

2. **`src/data/scope_registry_template.json`** (NEW)
   - Common domains (sales, finance, operations, hr, manufacturing)
   - Common systems by domain
   - Common system categories (CRM, ERP, Analytics, etc.)

3. **`src/data/AI_dependency_taxonomy.json`** (UPDATE)
   - Add scope_applicability to each prerequisite
   - Link prerequisites to factor scopes

### Example: Factor with Scope Schema

```json
{
  "factor_id": "data_quality",
  "factor_name": "Data Quality",
  "scope_dimensions": {
    "domain": {
      "required": false,
      "common_values": ["sales", "finance", "operations", "hr"],
      "allow_custom": true
    },
    "system": {
      "required": false,
      "common_values": ["salesforce_crm", "sap_erp", "custom_db"],
      "allow_custom": true
    },
    "team": {
      "required": false,
      "allow_custom": true
    }
  },
  "allows_generic_scope": true,
  "clarifying_questions": {
    "narrow_from_generic": "Is this across all {domain} systems, or specific to certain tools?",
    "generalize_from_specific": "Do other {domain} systems have similar issues, or is this isolated to {system}?"
  }
}
```

---

## Task 5: Update Epic 1 Specification

**Status:** Pending  
**Estimated Time:** 1 hour

### File to Update

**`docs/VERTICAL_EPICS.md`**

### Changes Needed

1. **Update Data Layer section:**
   - Replace `/users/{user_id}/factors/{factor_id}` 
   - Add `/users/{user_id}/factor_instances/{instance_id}`
   - Add scope matching logic

2. **Update User Journey:**
   - Add clarifying questions about scope
   - Show scoped instances in UI

3. **Update Implementation Tasks:**
   - Add "Scope matching logic" task
   - Add "Clarifying question generator" task
   - Add "Scope registry initialization" task

### Updated User Journey

```
1. User: "Our data is scattered across 5 different systems"
2. System: "Which data are you thinking about - sales, finance, operations?"
3. User: "Sales data"
4. System infers: data_quality {domain: "sales"} = 20
5. System: "Is this across all sales systems, or specific tools?"
6. User: "Mainly our CRM"
7. System updates: data_quality {domain: "sales", system: "crm"} = 15
8. UI shows:
   - Data Quality
     └─ Sales Department: 20% (moderate confidence)
        └─ CRM: 15% (high confidence)
```

---

## Task 6: Implement Scope Matching Logic

**Status:** Pending  
**Estimated Time:** 4-5 hours (implementation + tests)

### Components to Build

1. **`src/knowledge/scope_matcher.py`** (NEW)
   - `calculate_scope_match()` function
   - `get_applicable_value()` function
   - `find_best_match()` function

2. **`tests/test_scope_matcher.py`** (NEW)
   - Test exact matches
   - Test generic fallbacks
   - Test no matches
   - Test multi-level hierarchies

### Test Cases

```python
def test_exact_match():
    # Query: {domain: "sales", system: "salesforce_crm"}
    # Available: {domain: "sales", system: "salesforce_crm"} = 30
    # Expected: 30, match_score=1.0
    pass

def test_generic_fallback():
    # Query: {domain: "sales", system: "data_warehouse"}
    # Available: {domain: "sales", system: null} = 45
    # Expected: 45, match_score=0.86
    pass

def test_no_match():
    # Query: {domain: "manufacturing", system: "iot"}
    # Available: {domain: "sales", system: "salesforce_crm"} = 30
    # Expected: None
    pass
```

---

## Task 7: Update Graph Builder

**Status:** Pending  
**Estimated Time:** 2-3 hours

### File to Update

**`src/knowledge/graph_builder.py`**

### Changes Needed

1. **Add ORGANIZATIONAL_FACTOR node type**
   - Load from organizational_factors.json
   - Include scope_dimensions schema

2. **Add IMPROVES edge type**
   - AI_ARCHETYPE → ORGANIZATIONAL_FACTOR
   - Include typical_improvement metadata

3. **Add scope registry loading**
   - Load common domains, systems, categories
   - Make available for scope matching

### New Methods

```python
class KnowledgeGraphBuilder:
    def load_organizational_factors(self):
        """Load factor definitions with scope schemas."""
        pass
    
    def load_scope_registry(self):
        """Load common domains, systems, categories."""
        pass
    
    def add_improvement_edges(self):
        """Add IMPROVES edges from archetypes to factors."""
        pass
```

---

## Priority Order

1. **Task 1** - Update architecture documents (foundation)
2. **Task 4** - Update taxonomy files (data foundation)
3. **Task 7** - Update graph builder (load new data)
4. **Task 6** - Implement scope matching (core logic)
5. **Task 5** - Update Epic 1 spec (implementation ready)
6. **Task 2** - Update UX guidelines (conversation patterns)
7. **Task 3** - KG-based question inference (enhancement)

---

## Estimated Total Time

**Core tasks (1, 4, 5, 6, 7):** 12-15 hours  
**Enhancement tasks (2, 3):** 5-6 hours  
**Total:** 17-21 hours (2-3 days)

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-30  
**Status:** Ready for execution
