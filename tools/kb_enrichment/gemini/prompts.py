"""Prompt templates for knowledge graph enrichment."""


class PromptTemplates:
    """Collection of prompt templates for each phase."""
    
    # ========== PHASE 0: PRE-PROCESSING ==========
    
    PHASE_0_1_SCRIPT_GENERATION = """You are a Python code generation expert. Write a complete, production-ready Python script that performs the following task:

**Task:** Read the `AI_discovery.json` file and recursively iterate through the nested structure to explode the data into separate, normalized JSON files.

**Input Structure:**
The `AI_discovery.json` file contains:
1. `Organizational_Maturity` with subdimensions (AI Maturity Stage, Data Maturity, etc.)
2. `Business_Function` with categories and functions, each containing `tools_and_processes` lists
3. `Business_Sector` with categories and sectors, each containing `tools_and_processes` lists

**Output Requirements:**
Generate THREE separate JSON files:

1. **FUNCTION_NODES.json** - Flat list of all business functions
   - Each node should have: id, name, node_type="BUSINESS_FUNCTION", category, tools_and_processes

2. **SECTOR_NODES.json** - Flat list of all business sector CATEGORIES (not individual sectors)
   - Each node should have: id, name, node_type="BUSINESS_SECTOR", category
   - NOTE: Only create nodes for the category level, not individual sectors

3. **TOOL_NODES.json** - Flat list of all unique tools/processes
   - Each node should have: id, name, node_type="BUSINESS_TOOL"
   - Deduplicate tools across all functions and sectors

**Script Requirements:**
- Use only Python standard library (json, pathlib)
- Include proper error handling
- Add logging/print statements for progress tracking
- Generate unique IDs for each node (e.g., "FUNCTION_001", "SECTOR_CAT_001", "TOOL_001")
- Handle special characters in names properly
- Include a main() function and if __name__ == "__main__" block

**Additional Context:**
- Input file path: "../../src/data/AI_discovery.json"
- Output directory: "./output/phase_0/"
- The script will be saved as "explode_discovery.py" and executed directly

Generate the complete Python script now. Include all necessary imports, functions, and error handling."""

    # ========== PHASE I: NODE EXTRACTION ==========
    
    PHASE_1_1_ARCHETYPE_EXTRACTION = """You are a knowledge graph data extraction expert. Extract and normalize all unique nodes from the provided AI archetype and prerequisite data.

**Input Data:**
{input_data}

**Task:**
Extract nodes into FOUR separate categories:

1. **AI_ARCHETYPE** - AI use-case patterns
   - Fields: id, name, node_type="AI_ARCHETYPE", description, analytical_purpose, technical_family, complexity

2. **COMMON_MODEL** - Machine learning algorithms
   - Fields: id, name, node_type="COMMON_MODEL", description

3. **AI_OUTPUT** - System outputs/artifacts
   - Fields: id, name, node_type="AI_OUTPUT", description, output_type

4. **AI_PREREQUISITE** - Implementation requirements
   - Fields: id, name, node_type="AI_PREREQUISITE", category, description

**Output Format:**
Return a JSON object with four arrays:
```json
{{
  "AI_ARCHETYPE": [...],
  "COMMON_MODEL": [...],
  "AI_OUTPUT": [...],
  "AI_PREREQUISITE": [...]
}}
```

**Important:**
- Generate unique IDs (e.g., "ARCHETYPE_001", "MODEL_001", "OUTPUT_001", "PREREQ_001")
- Preserve all relevant metadata from the source
- Ensure no duplicates within each category
- Do NOT generate edges yet (edges will be created in Phase II)

Generate the normalized node data now."""

    PHASE_1_2_CHUNKING_SCRIPT = """You are a Python code generation expert. Write a script that generates inference task chunks for Phase III.

**Task:**
The critical inference task (Phase III.1) requires inferring pain connections by combining AI_OUTPUT, PROBLEM_TYPE, and BUSINESS_FUNCTION nodes. This script must:

1. Load three JSON files:
   - AI_OUTPUT_NODES.json
   - PROBLEM_NODES.json (you'll need to extract these from the source data)
   - FUNCTION_NODES.json

2. Generate a cross-product of unique triplets: (AI_Output, Problem_Type, Business_Function)

3. Split this master list into chunks of NO MORE THAN {chunk_size} triplets each

4. Output sequential JSON files: INFERENCE_CHUNK_001.json, INFERENCE_CHUNK_002.json, etc.

**Chunk Format:**
Each chunk file should be a JSON array of objects:
```json
[
  {{
    "ai_output_id": "OUTPUT_001",
    "ai_output_name": "Equipment fault alert",
    "problem_type_id": "PROBLEM_001",
    "problem_type_name": "Quality or reliability gap",
    "function_id": "FUNCTION_005",
    "function_name": "Manufacturing"
  }},
  ...
]
```

**Script Requirements:**
- Use only Python standard library
- Include progress tracking
- Handle edge cases (empty inputs, etc.)
- Generate meaningful chunk IDs with zero-padding (001, 002, etc.)
- Input directory: "./output/phase_1/"
- Output directory: "./output/phase_1/"

Generate the complete Python script now."""

    # ========== PHASE II: EDGE GENERATION ==========
    
    PHASE_2_1_EXPLICIT_EDGES = """You are a knowledge graph relationship extraction expert. Generate explicit edge triples from the provided archetype and prerequisite data.

**Input Data:**
{input_data}

**Task:**
Generate edges for the following relationship types:

1. **IMPLEMENTED_BY** - AI_ARCHETYPE → COMMON_MODEL
   - Links archetypes to their implementing algorithms

2. **PRODUCES_OUTPUT** - AI_ARCHETYPE → AI_OUTPUT
   - Links archetypes to their output artifacts

3. **REQUIRES** (Model Prerequisites) - COMMON_MODEL → AI_PREREQUISITE
   - Links models to their technical requirements

4. **REQUIRES** (Output Prerequisites) - AI_OUTPUT → AI_PREREQUISITE
   - Links outputs to their implementation requirements

5. **HAS_PURPOSE** - AI_ARCHETYPE → ANALYTICAL_PURPOSE
   - Links archetypes to their analytical purpose (you may need to create purpose nodes)

**Edge Format:**
```json
[
  {{
    "source": "ARCHETYPE_001",
    "target": "MODEL_005",
    "edge_type": "IMPLEMENTED_BY",
    "source_citation": "AI_archetypes.json - Optimization & Scheduling"
  }},
  ...
]
```

**Important:**
- Use the node IDs from Phase I output
- Include source_citation for traceability
- Ensure all referenced nodes exist
- No duplicate edges

Generate the edge list now."""

    PHASE_2_2_CONTEXTUAL_EDGES = """You are a knowledge graph relationship extraction expert. Generate contextual edges by mapping tools and processes to functions and sectors.

**Input Data:**
{input_data}

**Task:**
Generate **OPERATES_IN** edges that map tools/processes to their business context.

**Edge Types:**

1. **OPERATES_IN** - BUSINESS_FUNCTION → BUSINESS_TOOL
   - Links functions to the tools they use

2. **OPERATES_IN** - BUSINESS_SECTOR → BUSINESS_TOOL
   - Links sectors to the tools they use

**Edge Format:**
```json
[
  {{
    "source": "FUNCTION_005",
    "target": "TOOL_042",
    "edge_type": "OPERATES_IN",
    "source_citation": "AI_discovery.json - Manufacturing"
  }},
  ...
]
```

**Important:**
- Extract relationships from the `tools_and_processes` lists in AI_discovery.json
- Use node IDs from Phase 0 output (FUNCTION_NODES.json, SECTOR_NODES.json, TOOL_NODES.json)
- Ensure all referenced nodes exist
- No duplicate edges

Generate the edge list now."""

    # ========== PHASE III: LLM INFERENCE ==========
    
    PHASE_3_1_PAIN_INFERENCE = """You are an expert business analyst specializing in operational pain point analysis and AI solution mapping.

**Context:**
You are receiving one chunk of inference tasks. Each task is a triplet of (AI_Output, Problem_Type, Business_Function). Your job is to perform Chain-of-Thought reasoning to infer specific operational pain points and measurable failure modes.

**Input Chunk:**
{chunk_data}

**Task:**
For EACH triplet, perform the following analysis:

**Step 1: Contextualize the Problem**
- Given the Problem_Type (broad pain category) and Business_Function, infer a specific OPERATIONAL_PAIN_POINT (M1)
- This should be a concrete, function-specific manifestation of the problem
- Example: "Quality gaps" in "Manufacturing" → "High rate of unplanned equipment failures"

**Step 2: Define Measurable Failure**
- For the M1 pain point, infer the associated MEASURABLE_FAILURE_MODE (M2)
- This should be a quantifiable KPI or metric
- Example: "High rate of unplanned equipment failures" → "Low MTBF (Mean Time Between Failures)"

**Step 3: Generate Nodes and Edges**
Create the following for each triplet:

**New Nodes:**
- One OPERATIONAL_PAIN_POINT (M1) node
- One MEASURABLE_FAILURE_MODE (M2) node

**New Edges:**
- M1 CONTEXTUALIZED_BY Problem_Type
- M1 MANIFESTS_AS M2
- AI_Output MITIGATES_FAILURE M2

**Output Format:**
Return a JSON object with two arrays:
```json
{{
  "nodes": [
    {{
      "id": "PAIN_001",
      "name": "High rate of unplanned equipment failures",
      "node_type": "OPERATIONAL_PAIN_POINT",
      "description": "Frequent unexpected breakdowns in manufacturing equipment",
      "context": "Manufacturing - Quality gaps"
    }},
    {{
      "id": "FAILURE_001",
      "name": "Low MTBF",
      "node_type": "MEASURABLE_FAILURE_MODE",
      "description": "Mean Time Between Failures below industry standard",
      "metric_type": "Reliability KPI"
    }}
  ],
  "edges": [
    {{
      "source": "PAIN_001",
      "target": "PROBLEM_001",
      "edge_type": "CONTEXTUALIZED_BY"
    }},
    {{
      "source": "PAIN_001",
      "target": "FAILURE_001",
      "edge_type": "MANIFESTS_AS"
    }},
    {{
      "source": "OUTPUT_001",
      "target": "FAILURE_001",
      "edge_type": "MITIGATES_FAILURE"
    }}
  ]
}}
```

**Important Guidelines:**
- Be specific and concrete in your pain point descriptions
- Ensure M2 nodes represent truly measurable metrics
- Use realistic business terminology
- Generate unique IDs for new nodes
- Reference the correct input node IDs in edges

Perform the analysis now for all triplets in the chunk."""

    PHASE_3_2_FINAL_ASSEMBLY = """You are a knowledge graph assembly expert. Merge and deduplicate the generated knowledge graph components.

**Input Data:**
You have access to:
- All node files from Phase 0 and Phase I
- All edge files from Phase II
- All inference output chunks from Phase III.1

**Task:**
1. Merge all nodes from all sources
2. Merge all edges from all sources
3. **Crucially: Perform deduplication on M1 (OPERATIONAL_PAIN_POINT) and M2 (MEASURABLE_FAILURE_MODE) nodes**
   - Nodes with similar names/descriptions should be merged
   - Update edge references accordingly
4. Validate the final structure
5. Output the complete knowledge graph

**Output Format:**
```json
{{
  "metadata": {{
    "version": "1.0",
    "generated_at": "ISO timestamp",
    "total_nodes": 0,
    "total_edges": 0,
    "node_type_counts": {{}},
    "edge_type_counts": {{}}
  }},
  "nodes": [...],
  "edges": [...]
}}
```

**Deduplication Strategy:**
- For M1/M2 nodes, merge if semantic similarity > 85%
- Keep the most descriptive version
- Update all edge references to merged nodes
- Remove self-loop edges created by merging

Generate the final knowledge graph now."""

    # ========== HELPER METHODS ==========
    
    @staticmethod
    def format_chunk_data(chunk: list) -> str:
        """Format chunk data for prompt injection.
        
        Args:
            chunk: List of triplet dictionaries
            
        Returns:
            Formatted string
        """
        import json
        return json.dumps(chunk, indent=2)
    
    @staticmethod
    def format_input_data(data: dict) -> str:
        """Format input data for prompt injection.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Formatted string
        """
        import json
        # Truncate if too large
        data_str = json.dumps(data, indent=2)
        if len(data_str) > 50000:
            return data_str[:50000] + "\n\n... (truncated)"
        return data_str
