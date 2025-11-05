# Knowledge Graph-Based Question Inference

**Version:** 1.0  
**Date:** 2024-10-31  
**Status:** Design Complete - Ready for Implementation

---

## Overview

This document specifies how the system uses the knowledge graph to generate intelligent clarifying questions about unknown systems and domains, enabling dynamic scope discovery without pre-configured templates.

---

## Problem Statement

When users mention unfamiliar systems or domains, the system needs to:
1. Detect that the system/domain is unknown
2. Ask intelligent questions to understand its context
3. Update the scope registry with the new information
4. Infer similarities to known systems for better assessment

**Example:**
```
User: "Our Cogglepoop system has data quality issues"

Challenge:
- "Cogglepoop" is not in scope registry
- Need to understand: domain, team, purpose, system type
- Should ask intelligent questions, not generic "what is it?"
```

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Conversation Orchestrator                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ├─> 1. Unknown System Detector
                        │   (NER or LLM-based extraction)
                        │
                        ├─> 2. KG Question Generator
                        │   (Query KG for domains, categories)
                        │
                        ├─> 3. Scope Registry Updater
                        │   (Store new system metadata)
                        │
                        └─> 4. Similarity Inference Engine
                            (Find similar known systems)
```

---

## Phase 1: Unknown System Detection

### Detection Strategy

**Method 1: Named Entity Recognition (NER)**
```python
def detect_unknown_systems_ner(user_statement):
    """
    Use NER to extract potential system names.
    """
    # Extract entities tagged as PRODUCT, ORG, or MISC
    entities = ner_model.extract_entities(user_statement)
    
    # Filter for system-like entities
    potential_systems = [
        e for e in entities 
        if e.type in ["PRODUCT", "ORG", "MISC"]
        and is_system_context(e, user_statement)
    ]
    
    # Check against scope registry
    unknown = [
        s for s in potential_systems 
        if s.text not in scope_registry.all_systems
    ]
    
    return unknown
```

**Method 2: LLM-Based Extraction**
```python
def detect_unknown_systems_llm(user_statement, scope_registry):
    """
    Use LLM to identify system mentions.
    """
    prompt = f"""
    User statement: "{user_statement}"
    
    Known systems: {scope_registry.all_systems}
    
    Task: Identify any system, tool, or platform mentioned that is NOT in the known systems list.
    
    Return JSON:
    {{
        "unknown_systems": [
            {{"name": "system_name", "context": "how it was mentioned"}}
        ]
    }}
    """
    
    response = llm.call(prompt)
    return response.unknown_systems
```

### Context Analysis

```python
def is_system_context(entity, statement):
    """
    Determine if entity is mentioned in system context.
    """
    system_indicators = [
        "system", "tool", "platform", "software",
        "CRM", "ERP", "database", "application",
        "data from", "using", "in our"
    ]
    
    # Check if any indicator appears near the entity
    context_window = get_context_window(entity, statement, window=10)
    return any(indicator in context_window for indicator in system_indicators)
```

---

## Phase 2: KG-Based Question Generation

### Query Knowledge Graph for Context

```python
def generate_discovery_questions(unknown_system, context, kg):
    """
    Generate intelligent questions using KG structure.
    """
    # Query KG for common domains
    domains = kg.query_nodes(node_type="DOMAIN")
    domain_names = [d.name for d in domains[:5]]  # Top 5 most common
    
    # Query KG for system categories
    categories = kg.query_nodes(node_type="SYSTEM_CATEGORY")
    category_names = [c.name for c in categories[:5]]
    
    # Query KG for typical system purposes
    purposes = kg.query_edges(
        relationship="USED_FOR",
        source_type="SYSTEM"
    )
    purpose_names = list(set([p.target.name for p in purposes[:5]]))
    
    return {
        "system_name": unknown_system,
        "primary_question": f"I'm not familiar with {unknown_system}. Could you help me understand:",
        "sub_questions": [
            {
                "question": f"Which team or department uses it?",
                "options": domain_names,
                "allow_custom": True,
                "intent": "identify_domain"
            },
            {
                "question": f"What type of system is it?",
                "options": category_names,
                "allow_custom": True,
                "intent": "identify_category"
            }
        ],
        "optional_questions": [
            {
                "question": f"What's it primarily used for?",
                "options": purpose_names,
                "allow_custom": True,
                "intent": "identify_purpose"
            }
        ]
    }
```

### Question Templates from KG

```python
class QuestionTemplateGenerator:
    """
    Generate question templates based on KG structure.
    """
    
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
    
    def get_domain_question(self):
        """Generate domain identification question."""
        domains = self.kg.get_common_domains(limit=5)
        return {
            "question": "Which team or department uses it?",
            "options": [d.name for d in domains],
            "examples": [d.example for d in domains],
            "allow_custom": True
        }
    
    def get_category_question(self):
        """Generate system category question."""
        categories = self.kg.get_system_categories(limit=5)
        return {
            "question": "What type of system is it?",
            "options": [c.name for c in categories],
            "descriptions": {c.name: c.description for c in categories},
            "allow_custom": True
        }
    
    def get_purpose_question(self, domain=None):
        """Generate purpose question, optionally filtered by domain."""
        if domain:
            purposes = self.kg.get_purposes_for_domain(domain, limit=5)
        else:
            purposes = self.kg.get_common_purposes(limit=5)
        
        return {
            "question": "What's it primarily used for?",
            "options": [p.name for p in purposes],
            "allow_custom": True
        }
```

---

## Phase 3: Scope Registry Update

### Update Logic

```python
class ScopeRegistryUpdater:
    """
    Update scope registry with newly discovered systems.
    """
    
    def __init__(self, firestore_client, user_id):
        self.db = firestore_client
        self.user_id = user_id
    
    async def add_system(
        self,
        system_name: str,
        domain: str,
        system_type: str,
        purpose: str = None,
        custom_metadata: dict = None
    ):
        """
        Add newly discovered system to user's scope registry.
        """
        # Normalize system name
        normalized_name = self._normalize_system_name(system_name, system_type)
        
        # Create system metadata
        metadata = {
            "original_name": system_name,
            "normalized_name": normalized_name,
            "domain": domain,
            "type": system_type,
            "purpose": purpose,
            "discovered_at": firestore.SERVER_TIMESTAMP,
            "similar_to": await self._find_similar_systems(system_type, domain),
            "custom_metadata": custom_metadata or {}
        }
        
        # Update registry
        registry_ref = self.db.collection("users").document(self.user_id) \
                              .collection("scope_registry").document("metadata")
        
        await registry_ref.set({
            f"systems.{domain}": firestore.ArrayUnion([normalized_name]),
            f"system_metadata.{normalized_name}": metadata
        }, merge=True)
        
        return normalized_name
    
    def _normalize_system_name(self, name: str, system_type: str) -> str:
        """
        Create normalized system identifier.
        
        Examples:
        - "Cogglepoop" + "CRM" -> "cogglepoop_crm"
        - "Our custom database" + "Database" -> "custom_database"
        """
        # Remove common words
        clean_name = name.lower().replace("our ", "").replace("the ", "")
        
        # Append type if not already in name
        type_suffix = system_type.lower().replace(" ", "_")
        if type_suffix not in clean_name:
            clean_name = f"{clean_name}_{type_suffix}"
        
        # Normalize to snake_case
        normalized = clean_name.replace(" ", "_").replace("-", "_")
        
        return normalized
    
    async def _find_similar_systems(self, system_type: str, domain: str) -> list:
        """
        Find known systems of similar type in same domain.
        """
        # Query KG for systems with same type and domain
        similar = self.kg.query_nodes(
            node_type="SYSTEM",
            filters={
                "type": system_type,
                "domain": domain
            }
        )
        
        return [s.id for s in similar[:3]]  # Top 3 most similar
```

### Registry Schema

```json
{
  "users/{user_id}/scope_registry/metadata": {
    "domains": ["sales", "finance", "operations"],
    "systems": {
      "sales": ["salesforce_crm", "hubspot", "cogglepoop_crm"],
      "finance": ["sap_erp", "quickbooks"],
      "operations": ["custom_mes"]
    },
    "system_metadata": {
      "cogglepoop_crm": {
        "original_name": "Cogglepoop",
        "normalized_name": "cogglepoop_crm",
        "domain": "sales",
        "type": "CRM",
        "purpose": "customer_relationship_management",
        "discovered_at": "2024-10-31T12:00:00Z",
        "similar_to": ["salesforce_crm", "hubspot"],
        "custom_metadata": {
          "is_custom_built": true,
          "vendor": "internal"
        }
      }
    },
    "last_updated": "2024-10-31T12:00:00Z"
  }
}
```

---

## Phase 4: Similarity Inference

### Finding Similar Systems

```python
class SimilarityInferenceEngine:
    """
    Infer similarities between unknown and known systems.
    """
    
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
    
    def find_similar_systems(
        self,
        system_type: str,
        domain: str = None,
        purpose: str = None
    ) -> list:
        """
        Find known systems similar to the unknown system.
        
        Similarity based on:
        1. Same system type (e.g., both CRMs)
        2. Same domain (e.g., both in sales)
        3. Same purpose (e.g., both for customer management)
        """
        # Build query filters
        filters = {"type": system_type}
        if domain:
            filters["domain"] = domain
        if purpose:
            filters["purpose"] = purpose
        
        # Query KG
        similar_systems = self.kg.query_nodes(
            node_type="SYSTEM",
            filters=filters
        )
        
        # Calculate similarity scores
        scored_systems = []
        for system in similar_systems:
            score = self._calculate_similarity_score(
                system, system_type, domain, purpose
            )
            scored_systems.append((system, score))
        
        # Sort by score and return top matches
        scored_systems.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored_systems[:5]]
    
    def _calculate_similarity_score(
        self,
        system,
        target_type: str,
        target_domain: str,
        target_purpose: str
    ) -> float:
        """
        Calculate similarity score (0.0 to 1.0).
        """
        score = 0.0
        
        # Type match (most important)
        if system.type == target_type:
            score += 0.5
        
        # Domain match
        if target_domain and system.domain == target_domain:
            score += 0.3
        
        # Purpose match
        if target_purpose and system.purpose == target_purpose:
            score += 0.2
        
        return score
    
    def infer_factor_values(
        self,
        unknown_system: str,
        similar_systems: list,
        factor_id: str
    ) -> dict:
        """
        Infer likely factor value for unknown system based on similar systems.
        
        Returns: {value: int, confidence: float, reasoning: str}
        """
        # Get factor values for similar systems
        similar_values = []
        for system in similar_systems:
            instance = self._get_factor_instance(factor_id, system.id)
            if instance:
                similar_values.append({
                    "system": system.name,
                    "value": instance.value,
                    "confidence": instance.confidence
                })
        
        if not similar_values:
            return None
        
        # Calculate weighted average
        total_weight = sum(v["confidence"] for v in similar_values)
        weighted_value = sum(
            v["value"] * v["confidence"] for v in similar_values
        ) / total_weight
        
        # Reduce confidence for inference
        avg_confidence = total_weight / len(similar_values)
        inferred_confidence = avg_confidence * 0.7  # 30% penalty for inference
        
        return {
            "value": int(weighted_value),
            "confidence": inferred_confidence,
            "reasoning": f"Inferred from {len(similar_values)} similar systems: "
                        f"{', '.join(v['system'] for v in similar_values)}",
            "similar_systems": similar_values
        }
```

---

## Knowledge Graph Schema Additions

### New Node Type: SYSTEM_CATEGORY

```json
{
  "node_type": "SYSTEM_CATEGORY",
  "category_id": "crm",
  "category_name": "Customer Relationship Management",
  "short_name": "CRM",
  "description": "Systems for managing customer interactions and data",
  "common_domains": ["sales", "marketing", "customer_service"],
  "typical_data_types": ["customer_data", "transactional", "interaction_history"],
  "typical_purposes": ["lead_management", "customer_tracking", "sales_pipeline"],
  "examples": ["salesforce", "hubspot", "dynamics_365"],
  "related_categories": ["marketing_automation", "sales_enablement"]
}
```

### New Node Type: DOMAIN

```json
{
  "node_type": "DOMAIN",
  "domain_id": "sales",
  "domain_name": "Sales",
  "description": "Sales and revenue generation activities",
  "typical_systems": ["crm", "sales_enablement", "analytics"],
  "typical_teams": ["enterprise_sales", "smb_sales", "inside_sales"],
  "common_data_types": ["customer_data", "opportunity_data", "pipeline_data"]
}
```

### New Edge Type: SIMILAR_TO

```json
{
  "source": "cogglepoop_crm",
  "source_type": "SYSTEM",
  "target": "salesforce_crm",
  "target_type": "SYSTEM",
  "relationship": "SIMILAR_TO",
  "similarity_score": 0.85,
  "similarity_reasons": [
    "Both are CRM systems",
    "Both used in sales domain",
    "Both manage customer data"
  ],
  "inferred_at": "2024-10-31T12:00:00Z"
}
```

---

## Complete Flow Example

### Scenario: Unknown System "Cogglepoop"

```python
# 1. User mentions unknown system
user_input = "Our Cogglepoop system has data quality issues"

# 2. Detect unknown system
unknown_systems = detector.detect_unknown_systems(user_input)
# Returns: [{"name": "Cogglepoop", "context": "system has data quality issues"}]

# 3. Generate questions using KG
questions = question_generator.generate_discovery_questions(
    unknown_system="Cogglepoop",
    context="data quality issues",
    kg=knowledge_graph
)

# 4. Ask user
system_response = """
I'm not familiar with Cogglepoop. Could you help me understand:
- Which team or department uses it? (sales, finance, operations, hr, other)
- What type of system is it? (CRM, ERP, Database, Analytics, other)
"""

# 5. User responds
user_response = "It's our custom CRM for the sales team"

# 6. Parse response
parsed = {
    "domain": "sales",
    "system_type": "CRM",
    "is_custom": True
}

# 7. Update scope registry
normalized_name = registry_updater.add_system(
    system_name="Cogglepoop",
    domain="sales",
    system_type="CRM",
    custom_metadata={"is_custom_built": True}
)
# Returns: "cogglepoop_crm"

# 8. Find similar systems
similar = similarity_engine.find_similar_systems(
    system_type="CRM",
    domain="sales"
)
# Returns: ["salesforce_crm", "hubspot"]

# 9. Create factor instance with inferred baseline
inferred = similarity_engine.infer_factor_values(
    unknown_system="cogglepoop_crm",
    similar_systems=similar,
    factor_id="data_quality"
)
# Returns: {
#   "value": 45,
#   "confidence": 0.50,
#   "reasoning": "Inferred from 2 similar CRM systems"
# }

# 10. Create instance with user's statement
instance_store.create_factor_instance(
    factor_id="data_quality",
    scope={"domain": "sales", "system": "cogglepoop_crm", "team": None},
    value=30,  # From "has data quality issues"
    confidence=0.75,
    evidence=[{
        "statement": "Cogglepoop system has data quality issues",
        "timestamp": "2024-10-31T12:00:00Z",
        "specificity": "system-specific"
    }],
    baseline_inference=inferred
)

# 11. System continues conversation
system_response = """
Got it - Cogglepoop is your custom CRM for sales. I'll track that.

Since it's a CRM, typical data quality issues include:
- Incomplete customer records
- Duplicate entries
- Inconsistent data entry

Which of these are you seeing?
"""
```

---

## Implementation Checklist

### Phase 1: Detection
- [ ] Implement NER-based system detection
- [ ] Implement LLM-based system detection
- [ ] Add context analysis for system mentions
- [ ] Test with various user inputs

### Phase 2: Question Generation
- [ ] Query KG for domains, categories, purposes
- [ ] Generate question templates from KG structure
- [ ] Add option handling (predefined + custom)
- [ ] Test question quality and relevance

### Phase 3: Registry Update
- [ ] Implement system normalization logic
- [ ] Add Firestore registry update methods
- [ ] Handle duplicate system names
- [ ] Test registry persistence

### Phase 4: Similarity Inference
- [ ] Implement similarity scoring algorithm
- [ ] Add factor value inference from similar systems
- [ ] Create SIMILAR_TO edges in KG
- [ ] Test inference accuracy

### KG Schema
- [ ] Add SYSTEM_CATEGORY node type
- [ ] Add DOMAIN node type with metadata
- [ ] Add SIMILAR_TO edge type
- [ ] Update graph builder to load new types

---

## Testing Strategy

### Unit Tests
```python
def test_unknown_system_detection():
    """Test detection of unfamiliar systems."""
    statement = "Our Cogglepoop system has issues"
    unknown = detector.detect_unknown_systems(statement)
    assert "Cogglepoop" in [s.name for s in unknown]

def test_question_generation():
    """Test KG-based question generation."""
    questions = generator.generate_discovery_questions("Cogglepoop", kg)
    assert "domain" in questions.sub_questions[0].intent
    assert len(questions.sub_questions) >= 2

def test_registry_update():
    """Test scope registry update."""
    normalized = updater.add_system("Cogglepoop", "sales", "CRM")
    assert normalized == "cogglepoop_crm"
    assert normalized in registry.systems["sales"]

def test_similarity_inference():
    """Test finding similar systems."""
    similar = engine.find_similar_systems("CRM", "sales")
    assert "salesforce_crm" in [s.id for s in similar]
```

### Integration Tests
```python
def test_complete_discovery_flow():
    """Test end-to-end unknown system discovery."""
    # User mentions unknown system
    response = orchestrator.process_message(
        "Our Cogglepoop system has data quality issues"
    )
    
    # System should ask clarifying question
    assert "not familiar with Cogglepoop" in response
    assert "Which team" in response or "What type" in response
    
    # User responds
    response = orchestrator.process_message(
        "It's our custom CRM for the sales team"
    )
    
    # System should acknowledge and create instance
    assert "cogglepoop_crm" in registry.systems["sales"]
    instance = get_factor_instance("data_quality", "cogglepoop_crm")
    assert instance is not None
```

---

## Performance Considerations

### Caching
- Cache KG query results for common questions
- Cache similar system lookups
- Invalidate cache when registry updated

### Optimization
- Limit KG queries to top N results (5-10)
- Pre-compute common system categories
- Batch registry updates

### Scalability
- Registry updates are per-user (no cross-user conflicts)
- KG queries are read-only (no locking needed)
- Similarity calculations can be async

---

## Future Enhancements

### 1. Learning from User Corrections
```python
# If user corrects system type
user: "Actually, it's not a CRM, it's more like an ERP"
system: Updates metadata, recalculates similarities
```

### 2. Automatic Category Detection
```python
# Use LLM to infer category from description
user: "It tracks our manufacturing processes"
system: Infers category = "MES" (Manufacturing Execution System)
```

### 3. Cross-User System Knowledge
```python
# Learn from other users' systems (privacy-preserving)
# If multiple users mention "Cogglepoop", aggregate metadata
```

### 4. System Relationship Inference
```python
# Detect when systems are related
user: "We export data from Cogglepoop to our data warehouse"
system: Creates EXPORTS_TO edge
```

---

**Document Version:** 1.0  
**Status:** Design Complete - Ready for Implementation  
**Estimated Implementation Time:** 3-4 hours
