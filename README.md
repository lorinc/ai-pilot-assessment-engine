# AI Pilot Assessment Engine

A knowledge graph-powered system for discovering and recommending AI solutions based on organizational context, maturity, and business needs.

## Project Status

**Current Epic:** Epic 01 - Knowledge Graph Foundation  
**Current Story:** Story 1.1 - Load Knowledge Graph from Existing JSON  
**Status:** ✅ **COMPLETE & TESTED**

**Latest Test Results:**
- ✅ 281 nodes created (27 archetypes, 96 models, 79 outputs, 53 prerequisites, 22 functions, 4 maturity dimensions)
- ✅ 758 edges created (101 IMPLEMENTED_BY, 79 PRODUCES_OUTPUT, 578 REQUIRES)
- ✅ Multi-hop traversal working (Archetype → Models → Prerequisites)
- ✅ All validation checks passing

---

## Quick Start

### Prerequisites

- Python 3.10+
- pip or conda

### Installation & Testing

**Automated Setup (Recommended):**
```bash
# One command to create venv, install dependencies, and run tests
bash scripts/setup_and_test.sh
```

**Manual Setup:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install minimal dependencies for Story 1.1
pip install pydantic networkx pytest

# Run tests
python3 scripts/test_graph_construction.py
```

**Full Installation (for future stories):**
```bash
# Install all dependencies including LangChain, Vertex AI, FAISS
pip install -r requirements.txt
```

---

## Project Structure

```
ai-pilot-assessment-engine/
├── src/
│   ├── data/                          # Existing knowledge base JSON files
│   │   ├── AI_archetypes.json         # 28 AI use-case archetypes
│   │   ├── AI_prerequisites.json      # Implementation prerequisites
│   │   └── AI_discovery.json          # Maturity dimensions, functions
│   └── knowledge/                     # NEW: Graph construction
│       ├── schemas.py                 # Pydantic models for nodes/edges
│       └── graph_builder.py           # NetworkX graph builder
├── data/
│   └── mappings/                      # NEW: Maturity mappings
│       ├── archetype_maturity_requirements.json
│       └── maturity_prerequisite_constraints.json
├── tests/
│   └── test_graph_builder.py         # Unit tests
├── scripts/
│   └── test_graph_construction.py    # Standalone test script
├── docs/
│   ├── system_architecture_specification.md
│   ├── GEMINI_STREAMLIT_BOILERPLATE.md
│   ├── epic_01_knowledge_graph_foundation.md
│   ├── remaining_epics_overview.md
│   ├── E1S1_enrichment_structure.md
│   ├── E1S1_enrichment_dimansions_v2.md
│   └── E1S1_implementation_summary.md
└── requirements.txt
```

---

## Architecture

### Knowledge Graph Structure

The system uses a **NetworkX directed graph** with 6 node types and 6 edge types:

#### Node Types
1. **AI_ARCHETYPE** - AI use-case patterns (e.g., "Optimization & Scheduling")
2. **COMMON_MODEL** - ML algorithms (e.g., "XGBoost", "LSTM")
3. **AI_OUTPUT** - System outputs (e.g., "Sales forecast", "Fraud flagging")
4. **AI_PREREQUISITE** - Implementation requirements (e.g., "Clean_and_validated_data")
5. **BUSINESS_FUNCTION** - Organizational functions (e.g., "Manufacturing", "Sales")
6. **MATURITY_DIMENSION** - Readiness dimensions (e.g., "AI Maturity Stage", "Data Maturity")

#### Edge Types
1. **IMPLEMENTED_BY** - Archetype → Model
2. **PRODUCES_OUTPUT** - Archetype → Output
3. **REQUIRES** - Model/Output → Prerequisite
4. **APPLIES_TO_FUNCTION** - Archetype → Function
5. **OPERATES_IN** - Function → Tool/Process
6. **GOVERNS_READINESS_FOR** - Maturity → Prerequisite

### Multi-Hop Reasoning

The graph enables complex queries like:

```
Query: "What prerequisites does 'Optimization & Scheduling' need for a 'Piloting' stage org?"

Traversal:
  Archetype "Optimization & Scheduling"
    → IMPLEMENTED_BY → Models ["Linear Programming", "Genetic Algorithms"]
      → REQUIRES → Prerequisites ["Clean_and_validated_data", "Historical_process_data"]
        → Check against Maturity "Piloting" constraints
          → Gap Analysis: Can satisfy "Clean data" but may lack "Optimization experts"
```

---

## Current Implementation (Story 1.1)

### What's Built

✅ **Pydantic Schemas** (`src/knowledge/schemas.py`)
- Type-safe models for 6 node types and 6 edge types
- 10 prerequisite categories, 8 analytical purposes, 3 complexity levels
- Full validation and serialization support
- ~280 lines of code

✅ **Graph Builder** (`src/knowledge/graph_builder.py`)
- Loads 3 existing JSON files into NetworkX DiGraph
- Creates 281 nodes, 758 edges from real data
- Handles duplicates, missing data, and validation errors gracefully
- Provides statistics and helper methods
- ~450 lines of code

✅ **Maturity Mappings** (`data/mappings/`)
- 10 archetypes mapped to minimum maturity requirements
- 10 maturity levels mapped to prerequisite constraints
- Enables gap analysis and feasibility checks
- JSON format for easy updates

✅ **Test Suite**
- 20+ unit tests covering all node/edge types (`tests/test_graph_builder.py`)
- Standalone test script for quick validation (`scripts/test_graph_construction.py`)
- Automated setup script (`scripts/setup_and_test.sh`)
- Multi-hop traversal verification

### What's Next

**Story 1.2:** Vector Embeddings (Vertex AI + FAISS)  
**Story 1.3:** Graph Traversal Queries (3 test cases)  
**Story 1.4:** Vector Similarity Search  
**Story 1.5:** LangChain Hybrid Retrieval Tool  
**Story 1.6:** CLI/Notebook Interface

---

## Usage Example

```python
from pathlib import Path
from src.knowledge.graph_builder import KnowledgeGraphBuilder

# Build the graph
data_dir = Path("src/data")
builder = KnowledgeGraphBuilder(data_dir)
graph = builder.build()

# Get statistics
stats = builder.get_statistics()
print(f"Nodes: {stats['total_nodes']}, Edges: {stats['total_edges']}")

# Find an archetype
for node_id, data in graph.nodes(data=True):
    if data.get("name") == "Optimization & Scheduling":
        print(f"Found: {node_id}")
        
        # Get connected models
        models = [
            graph.nodes[n]["name"] 
            for n in graph.successors(node_id)
            if graph.nodes[n]["node_type"] == "COMMON_MODEL"
        ]
        print(f"Models: {models}")
        break
```

---

## Documentation

- **[System Architecture Specification](docs/system_architecture_specification.md)** - Overall system design
- **[Epic 01: Knowledge Graph Foundation](docs/epic_01_knowledge_graph_foundation.md)** - Current epic details
- **[Remaining Epics Overview](docs/remaining_epics_overview.md)** - Future work (Epics 2-13)
- **[E1S1 Implementation Summary](docs/E1S1_implementation_summary.md)** - Story 1.1 details
- **[Knowledge Graph Structure](docs/E1S1_enrichment_structure.md)** - Node/edge design
- **[Traversal Patterns](docs/E1S1_enrichment_dimansions_v2.md)** - Multi-hop reasoning

---

## Technology Stack

### Current (Story 1.1)
- **Python 3.10+** - Core language
- **Pydantic 2.5+** - Schema validation
- **NetworkX 3.2+** - Graph structure
- **pytest** - Testing

### Future (Stories 1.2-1.6)
- **LangChain** - Agent orchestration
- **Vertex AI** - Gemini LLM + Embeddings
- **FAISS** - Vector similarity search
- **Streamlit** - UI (Epic 05)
- **Firebase** - Session persistence (Epic 09)

---

## Development Roadmap

### Phase 1: Foundation (Epics 1-4) - **IN PROGRESS**
- [x] **Epic 01 Story 1.1: Knowledge Graph Loading** ✅ **COMPLETE**
  - 281 nodes, 758 edges from existing JSON
  - Pydantic schemas with full validation
  - NetworkX graph builder with statistics
  - Maturity mapping files created
  - Test suite passing
- [ ] Epic 01 Story 1.2: Vector Embeddings (Vertex AI + FAISS)
- [ ] Epic 01 Story 1.3: Graph Queries (3 test cases)
- [ ] Epic 02: Test Data Preparation
- [ ] Epic 03: LangChain ReAct Agent
- [ ] Epic 04: Multi-Stage Flow

### Phase 2: User Interface (Epics 5-7)
- [ ] Epic 05: Streamlit Chat UI
- [ ] Epic 06: Observability Panel
- [ ] Epic 07: Evaluation Metrics

### Phase 3: Production (Epics 8-9)
- [ ] Epic 08: GCP Deployment
- [ ] Epic 09: Firebase Persistence

### Phase 4: Enhancements (Epics 10-13)
- [ ] Epic 10: Intent Clarification
- [ ] Epic 11: Report Generation
- [ ] Epic 12: Advanced Graph Queries
- [ ] Epic 13: Knowledge Management

---

## Contributing

This is a portfolio/demonstration project. For questions or suggestions, please refer to the documentation in `docs/`.

---

## License

[To be determined]

---

## Contact

Project maintained as part of AI solution discovery research.

---

## Recent Updates

**October 21, 2025 - Story 1.1 Complete ✅**
- Implemented Pydantic schemas for 6 node types and 6 edge types
- Built NetworkX graph loader from 3 existing JSON files
- Created maturity mapping files (archetype requirements + prerequisite constraints)
- Fixed enum handling and prerequisite category validation
- All tests passing: 281 nodes, 758 edges successfully created
- Automated setup script for venv creation and testing

---

**Last Updated:** October 21, 2025  
**Version:** 0.1.0 (Epic 01, Story 1.1 Complete ✅)
