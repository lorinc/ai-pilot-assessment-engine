# Epic 01: Knowledge Graph Foundation with RAG Integration

## Epic Goal
Build the foundational knowledge layer that combines a NetworkX-based knowledge graph with vector embeddings for RAG, demonstrating hybrid retrieval (structured graph + semantic search) producing coherent responses through LangChain + Gemini.

## Success Criteria
- ✅ Knowledge graph loaded from existing JSON with nodes (archetypes, models, outputs, prerequisites, functions, maturity) and edges (relationships)
- ✅ Vector embeddings created for knowledge chunks using Vertex AI
- ✅ Graph traversal queries work with 3 test cases proving multi-hop reasoning:
  - Archetype → Prerequisites → Maturity feasibility check
  - Function → Tool → Pain → Solution discovery
  - Maturity-constrained archetype filtering
- ✅ Vector similarity search retrieves relevant chunks
- ✅ LangChain orchestrates hybrid retrieval: graph + RAG
- ✅ Simple CLI/notebook interface demonstrates coherent response combining both sources
- ✅ Minimal mapping files created for maturity constraints

## Architecture Layers Touched
```
┌─────────────────────────────────────────────┐
│ Interface Layer (CLI/Notebook - minimal)    │ ← Simple query interface
├─────────────────────────────────────────────┤
│ Orchestration Layer (LangChain)             │ ← Hybrid retrieval logic
├─────────────────────────────────────────────┤
│ Knowledge Layer                             │
│  ├─ NetworkX Graph (structured)             │ ← Graph traversal
│  └─ FAISS Vector Store (semantic)           │ ← Similarity search
├─────────────────────────────────────────────┤
│ LLM Layer (Vertex AI Gemini + Embeddings)   │ ← API integration
├─────────────────────────────────────────────┤
│ Data Layer (JSON files)                     │ ← Mock knowledge base
└─────────────────────────────────────────────┘
```

---

## User Stories

### Story 1.1: Load Knowledge Graph from Existing JSON
**As a** developer  
**I want to** load AI archetypes, models, outputs, prerequisites, functions, and maturity from existing JSON files into a NetworkX graph  
**So that** I can perform structured multi-hop queries on relationships

**Acceptance Criteria:**
- Pydantic schemas defined for 6 core node types and 5 edge types
- Python module `src/knowledge/graph_builder.py` loads from:
  - `src/data/AI_archetypes.json` → Archetype, Model, Output nodes
  - `src/data/AI_prerequisites.json` → Prerequisite nodes
  - `src/data/AI_discovery.json` → Function, Maturity nodes
- Graph has typed nodes: `AI_ARCHETYPE`, `COMMON_MODEL`, `AI_OUTPUT`, `AI_PREREQUISITE`, `BUSINESS_FUNCTION`, `MATURITY_DIMENSION`
- Edges: `IMPLEMENTED_BY`, `PRODUCES_OUTPUT`, `REQUIRES`, `APPLIES_TO_FUNCTION`, `OPERATES_IN`
- Two mapping files created:
  - `data/mappings/archetype_maturity_requirements.json` (3+ archetypes mapped)
  - `data/mappings/maturity_prerequisite_constraints.json` (maturity levels → prerequisites)
- Unit tests verify graph structure and node counts

**Technical Notes:**
- Use NetworkX `DiGraph` for directed relationships
- Node attributes store all JSON properties as dict
- Edge attributes store relationship metadata
- Pydantic models validate data integrity
- Graph builder handles missing/malformed data gracefully

**Out of Scope (Deferred to Epic 02):**
- OPERATIONAL_PAIN_POINT nodes (M1 granularity)
- MEASURABLE_FAILURE_MODE nodes (M2 granularity)
- MITIGATES_FAILURE edges
- Comprehensive pain taxonomy
- Business tool nodes (use simple string references)

---

### Story 1.2: Create Vector Embeddings for Knowledge Chunks
**As a** developer  
**I want to** generate text embeddings for knowledge graph content  
**So that** I can perform semantic similarity search

**Acceptance Criteria:**
- Text chunks generated from graph nodes (QA format or narrative)
- Vertex AI `text-embedding-004` model integrated
- FAISS index created and persisted locally
- Metadata links chunks back to graph node IDs
- Embedding pipeline is reproducible

**Technical Notes:**
- Use `langchain_google_vertexai.VertexAIEmbeddings`
- Chunk format: "Q: What is {archetype}? A: {description}. Addresses: {pains}. Requires: {prerequisites}."
- Store in `data/embeddings/` directory
- FAISS index saved as `.faiss` file with metadata pickle

---

### Story 1.3: Implement Graph Traversal Queries with 3 Test Cases
**As a** developer  
**I want to** query the knowledge graph using multi-hop traversal patterns  
**So that** I can prove the graph enables complex reasoning

**Acceptance Criteria:**
- `src/knowledge/graph_queries.py` module with query functions:
  - `get_prerequisites_for_archetype(archetype_id)` → prerequisites with maturity check
  - `get_archetypes_by_maturity(maturity_level)` → feasible archetypes
  - `get_models_for_archetype(archetype_id)` → implementation models
  - `check_prerequisite_feasibility(prereq_id, user_maturity)` → gap analysis
- **3 Test Queries Implemented:**
  1. **Query 1:** "What prerequisites does 'Optimization & Scheduling' need and can we satisfy them?"
     - Traversal: Archetype → Models → Prerequisites → Maturity constraints
  2. **Query 2:** "What archetypes are feasible for 'Exploring' maturity stage?"
     - Traversal: Maturity → Archetype requirements → Filter by complexity
  3. **Query 3:** "What models implement 'Anomaly Detection' and what data do they need?"
     - Traversal: Archetype → Models → Prerequisites (filtered by Data_Quality category)
- Queries return structured dicts with full node attributes
- Tests cover all 3 queries with assertions

**Technical Notes:**
- Use NetworkX `neighbors()`, `successors()`, `predecessors()`, `shortest_path()`
- Return Pydantic models or structured dicts
- Handle missing nodes/edges gracefully with informative errors
- Add query result caching for performance

---

### Story 1.4: Implement Vector Similarity Search
**As a** developer  
**I want to** perform semantic search over knowledge chunks  
**So that** I can retrieve relevant information for user queries

**Acceptance Criteria:**
- `src/knowledge/vector_store.py` wraps FAISS index
- `search(query: str, k: int)` returns top-k chunks with scores
- Results include chunk text + metadata (node_id, node_type)
- Integration with Vertex AI embeddings for query encoding

**Technical Notes:**
- Use `langchain_community.vectorstores.FAISS`
- Return `Document` objects with metadata
- Configurable similarity threshold

---

### Story 1.5: Build LangChain Hybrid Retrieval Tool
**As a** developer  
**I want to** create a LangChain tool that combines graph + vector retrieval  
**So that** the agent can access both structured and semantic knowledge

**Acceptance Criteria:**
- `src/agents/tools/knowledge_tool.py` implements LangChain `BaseTool`
- Tool input: user query (e.g., "efficiency problems in manufacturing")
- Tool logic:
  1. Vector search for top-3 relevant chunks
  2. Extract node IDs from chunk metadata
  3. Graph traversal for related nodes (prerequisites, constraints)
  4. Combine results into structured response
- Tool output: JSON with `{archetypes: [...], prerequisites: [...], context: [...]}`

**Technical Notes:**
- Use `langchain.tools.BaseTool` or `@tool` decorator
- Tool description guides LLM on when to use it
- Return format parseable by LLM

---

### Story 1.6: Create Simple Query Interface
**As a** developer  
**I want to** test the hybrid retrieval with a CLI or notebook  
**So that** I can validate end-to-end knowledge retrieval

**Acceptance Criteria:**
- Script `scripts/test_knowledge_retrieval.py` or Jupyter notebook
- User inputs a query (e.g., "How to reduce manufacturing costs?")
- System performs hybrid retrieval via LangChain tool
- Gemini generates coherent response using retrieved knowledge
- Output shows:
  - Retrieved chunks (vector search)
  - Graph traversal results
  - Final LLM response combining both

**Technical Notes:**
- Use `langchain_google_vertexai.ChatVertexAI` for Gemini
- Simple prompt: "Based on this knowledge: {retrieved_data}, answer: {query}"
- No multi-stage reasoning yet - single LLM call

---

## Technical Implementation Plan

### Release 1: Data Preparation (Story 1.1)
```
data/
├── knowledge/
│   ├── ai_archetypes.json       # 3-5 sample archetypes
│   ├── ai_pains.json            # 5-7 pain points
│   ├── ai_prerequisites.json    # 5-10 prerequisites
│   └── schema.md                # JSON schema documentation
└── embeddings/                  # Generated artifacts
    ├── knowledge.faiss
    └── metadata.pkl
```

**Sample JSON Structure:**
```json
// ai_archetypes.json
{
  "archetypes": [
    {
      "id": "optimization_scheduling",
      "name": "Optimization & Scheduling",
      "description": "Prescriptive AI that finds optimal resource allocation",
      "analytical_purpose": "Prescriptive",
      "typical_models": ["Linear Programming", "Reinforcement Learning"],
      "example_outputs": ["Optimal shift plans", "Delivery routes"],
      "pain_ids": ["efficiency_loss", "cost_pressure"],
      "prerequisite_ids": ["historical_process_data", "optimization_expert"]
    }
  ]
}
```

### Release 2: Graph Construction (Story 1.1, 1.3)
```python
# src/knowledge/graph_builder.py
import networkx as nx
from pathlib import Path
import json

class KnowledgeGraphBuilder:
    def __init__(self, data_dir: Path):
        self.graph = nx.DiGraph()
        self.data_dir = data_dir
    
    def build(self) -> nx.DiGraph:
        """Load JSON files and construct graph."""
        self._load_archetypes()
        self._load_pains()
        self._load_prerequisites()
        self._create_relationships()
        return self.graph
    
    def _load_archetypes(self):
        """Add archetype nodes."""
        pass  # Implementation
    
    def _create_relationships(self):
        """Create edges based on IDs in JSON."""
        pass  # Implementation
```

### Phase 3: Vector Store (Story 1.2, 1.4)
```python
# src/knowledge/vector_store.py
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

class KnowledgeVectorStore:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.embeddings = VertexAIEmbeddings(
            model_name="text-embedding-004"
        )
        self.vector_store = None
    
    def build_index(self):
        """Generate chunks from graph and create FAISS index."""
        chunks = self._generate_chunks()
        self.vector_store = FAISS.from_documents(
            chunks, 
            self.embeddings
        )
    
    def _generate_chunks(self) -> list[Document]:
        """Convert graph nodes to text chunks with metadata."""
        chunks = []
        for node_id, data in self.graph.nodes(data=True):
            if data['type'] == 'Archetype':
                text = self._format_archetype_chunk(node_id, data)
                chunks.append(Document(
                    page_content=text,
                    metadata={'node_id': node_id, 'type': 'Archetype'}
                ))
        return chunks
    
    def search(self, query: str, k: int = 3):
        """Semantic search."""
        return self.vector_store.similarity_search(query, k=k)
```

### Phase 4: Hybrid Retrieval Tool (Story 1.5)
```python
# src/agents/tools/knowledge_tool.py
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class KnowledgeRetrievalInput(BaseModel):
    query: str = Field(description="User's business problem or question")

class HybridKnowledgeTool(BaseTool):
    name = "knowledge_retrieval"
    description = """
    Retrieves relevant AI solution archetypes and prerequisites 
    by combining semantic search and knowledge graph traversal.
    Use this when the user describes a business problem or asks 
    about AI solutions.
    """
    args_schema = KnowledgeRetrievalInput
    
    def __init__(self, graph, vector_store):
        super().__init__()
        self.graph = graph
        self.vector_store = vector_store
    
    def _run(self, query: str) -> str:
        # 1. Vector search
        chunks = self.vector_store.search(query, k=3)
        
        # 2. Extract node IDs from metadata
        node_ids = [chunk.metadata['node_id'] for chunk in chunks]
        
        # 3. Graph traversal for each node
        results = {
            'archetypes': [],
            'prerequisites': [],
            'context': []
        }
        
        for node_id in node_ids:
            if self.graph.nodes[node_id]['type'] == 'Archetype':
                # Get prerequisites
                prereqs = list(self.graph.successors(node_id))
                results['archetypes'].append({
                    'id': node_id,
                    'name': self.graph.nodes[node_id]['name'],
                    'description': self.graph.nodes[node_id]['description']
                })
                results['prerequisites'].extend([
                    self.graph.nodes[p]['name'] for p in prereqs
                ])
        
        # 4. Format for LLM
        return json.dumps(results, indent=2)
```

### Phase 5: LangChain Agent Integration (Story 1.6)
```python
# scripts/test_knowledge_retrieval.py
from langchain_google_vertexai import ChatVertexAI
from langchain.agents import initialize_agent, AgentType
from src.knowledge.graph_builder import KnowledgeGraphBuilder
from src.knowledge.vector_store import KnowledgeVectorStore
from src.agents.tools.knowledge_tool import HybridKnowledgeTool

def main():
    # Build knowledge base
    builder = KnowledgeGraphBuilder(Path("data/knowledge"))
    graph = builder.build()
    
    vector_store = KnowledgeVectorStore(graph)
    vector_store.build_index()
    
    # Create tool
    knowledge_tool = HybridKnowledgeTool(graph, vector_store)
    
    # Initialize LangChain agent
    llm = ChatVertexAI(model_name="gemini-1.5-flash")
    agent = initialize_agent(
        tools=[knowledge_tool],
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    # Test query
    query = "We have efficiency problems in manufacturing. What AI solutions exist?"
    response = agent.run(query)
    
    print("\n=== RESPONSE ===")
    print(response)

if __name__ == "__main__":
    main()
```

---

## Dependencies

### Python Packages
```txt
# Core
langchain>=0.1.0
langchain-google-vertexai>=1.0.0
langchain-community>=0.0.20

# Knowledge Graph
networkx>=3.2

# Vector Store
faiss-cpu>=1.7.4
numpy>=1.24.0

# GCP
google-cloud-aiplatform>=1.38.0

# Utilities
pydantic>=2.5.0
python-dotenv>=1.0.0
```

### GCP Setup
- Vertex AI API enabled
- Service account with `Vertex AI User` role
- Environment variable: `GOOGLE_APPLICATION_CREDENTIALS`

---

## Testing Strategy

### Unit Tests
- `tests/test_graph_builder.py`: Graph construction from JSON
- `tests/test_graph_queries.py`: Traversal functions
- `tests/test_vector_store.py`: Embedding generation and search
- `tests/test_knowledge_tool.py`: Hybrid retrieval logic

### Integration Tests
- `tests/integration/test_end_to_end.py`: Full pipeline from query → response

### Manual Testing
- Jupyter notebook: `notebooks/01_knowledge_exploration.ipynb`
- Test queries covering different pain points and archetypes

---

## Definition of Done
- [ ] All 6 user stories completed and tested
- [ ] Mock JSON data created (3+ archetypes, 5+ pains, 5+ prerequisites)
- [ ] Knowledge graph builds successfully from JSON
- [ ] Vector embeddings generated and indexed in FAISS
- [ ] Graph queries return correct relationships
- [ ] Vector search returns relevant chunks
- [ ] LangChain tool combines both retrieval methods
- [ ] Test script demonstrates coherent LLM response using hybrid knowledge
- [ ] Unit tests pass (>80% coverage for knowledge layer)
- [ ] Documentation updated with usage examples

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Vertex AI quota limits | High | Use local embeddings (sentence-transformers) as fallback |
| Graph schema changes during development | Medium | Version JSON schema, use Pydantic models for validation |
| FAISS index size grows too large | Low | Start with small dataset, optimize chunking strategy |
| LangChain API changes | Medium | Pin versions, use stable LangChain patterns |

---

## Out of Scope (Future Epics)
- ❌ Multi-stage reasoning (Stage 1-4 flow)
- ❌ Streamlit UI
- ❌ Session persistence (Firebase)
- ❌ Evaluation metrics
- ❌ Observability/logging panel
- ❌ Intent capture and clarification
- ❌ Report generation

---

## Estimated Effort
**5-7 days** (assuming 1 developer, part-time)

- Story 1.1: 1 day (JSON schema + graph builder)
- Story 1.2: 1 day (embeddings + FAISS)
- Story 1.3: 0.5 day (graph queries)
- Story 1.4: 0.5 day (vector search wrapper)
- Story 1.5: 1.5 days (LangChain tool + hybrid logic)
- Story 1.6: 1 day (test interface + validation)
- Testing & docs: 0.5 day

---

## Next Epic Preview
**Epic 02: Test Data Preparation Pipeline** - Automated generation of realistic mock knowledge base with validation and versioning.
