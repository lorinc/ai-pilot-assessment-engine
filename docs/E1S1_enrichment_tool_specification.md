### Phase 0: Pre-Processing and Script Generation

This phase focuses on preparing the necessary tools for input explosion and chunking the massive `AI_discovery.txt` node lists before downstream processing.

| Task | Input File Requirements | GenAI Prompt / Action | Output |
| :--- | :--- | :--- | :--- |
| **0.1: Script Generation for Discovery Node Explosion** | `AI_discovery.txt` (Full Content) | **Prompt:** "Write a Python script that reads the `AI_discovery.txt` JSON. This script must recursively iterate through the nested `Organizational_Maturity`, `Business_Function`, and `Business_Sector` categories. **The script must explode the data into separate JSON files:** 1. `FUNCTION_NODES.json` (flat list). 2. `SECTOR_NODES.json` (flat list). 3. `TOOL_NODES.json` (flat list of all unique tools/processes). This normalization is critical for subsequent linking." | **Python Script:** `explode_discovery.py` |
| **0.2: Execute Node Explosion (VM Action)** | `AI_discovery.txt` + `explode_discovery.py` | **Action:** Execute `python explode_discovery.py`. | **Initial Flattened Nodes:** `FUNCTION_NODES.json`, `SECTOR_NODES.json`, `TOOL_NODES.json` |

### Phase I: Core Node Extraction and Formatting

This phase extracts remaining nodes and generates clean lists suitable for iterative processing.

| Task | Input File Requirements | GenAI Prompt / Action | Output |
| :--- | :--- | :--- | :--- |
| **I.1: AI Archetype & Prerequisite Node Extraction** | `AI_archetypes.txt`, `AI_prerequisites.txt` (Full Contents) | **Prompt:** "Extract and normalize all unique nodes from both files into separate JSON arrays for: `AI_ARCHETYPE`, `COMMON_MODEL`, `AI_OUTPUT`, and `AI_PREREQUISITE`. Do not generate edges yet." | **JSON Files:** `AI_ARCHETYPE_NODES.json`, `COMMON_MODEL_NODES.json`, `AI_OUTPUT_NODES.json`, `AI_PREREQUISITE_NODES.json` |
| **I.2: Script Generation for Inference Task Chunking** | `AI_OUTPUT_NODES.json`, `FUNCTION_NODES.json`, `PROBLEM_NODES.json` (from Phase 0) | **Prompt:** "The critical inference task (Phase III.1) requires inferring pain connections (M1/M2) by combining `AI_OUTPUT`, `PROBLEM_TYPE`, and `BUSINESS_FUNCTION`. Write a Python script to generate a 'cross-product' list of unique triplets: (Output, Problem Type, Function). **Split this master list into chunks of no more than 15 triplets each.** Output these chunks as sequential JSON files: `INFERENCE_CHUNK_001.json`, `INFERENCE_CHUNK_002.json`, etc." | **Python Script:** `chunk_inference_tasks.py` |
| **I.3: Execute Task Chunking (VM Action)** | Input Node Lists + `chunk_inference_tasks.py` | **Action:** Execute `python chunk_inference_tasks.py`. | **Chunked Input Files:** `INFERENCE_CHUNK_XXX.json` (e.g., 100+ files) |

### Phase II: Explicit Edge Generation (Rule-Based Linking)

This phase generates foundational edges. Since the source files are small and the output edge lists are linear (not context-intensive), chunking is not necessary here.

| Task | Input File Requirements | GenAI Prompt / Action | Output |
| :--- | :--- | :--- | :--- |
| **II.1: Compositional and Prerequisite Edges** | `AI_archetypes.txt`, `AI_prerequisites.txt`, All Node Files | **Prompt:** "Generate all explicit edge triples for `IMPLEMENTED_BY`, `PRODUCES_OUTPUT`, `REQUIRES` (Model -> Prerequisite, Output -> Prerequisite), and `HAS_PURPOSE`. Ensure each edge includes the source citation." | **JSON File:** `EXPLICIT_EDGES.json` |
| **II.2: Contextual Tool Edges** | `AI_discovery.txt`, `FUNCTION_NODES.json`, `SECTOR_NODES.json`, `TOOL_NODES.json` | **Prompt:** "Generate all `OPERATES_IN` edges by mapping the `tools_and_processes` lists within the functions and sectors defined in `AI_discovery.txt`." | **JSON File:** `CONTEXTUAL_EDGES.json` |

### Phase III: LLM Enrichment and Inference (Iterative Granular Pain Assessment)

This phase utilizes the LLM's **Chain-of-Thought (CoT) inference** iteratively across the generated chunks, ensuring the context window limit is never breached for the complex reasoning task.

| Task | Input File Requirements | GenAI Prompt / Action | Output |
| :--- | :--- | :--- | :--- |
| **III.1: Granular Pain Node and Mitigation Inference (Iterative)** | **Input:** `INFERENCE_CHUNK_XXX.json` (Iterate through ALL chunks) | **Prompt (High-Complexity Inference):** "You are receiving one chunk of inference tasks, structured as a list of (AI\_Output, Problem\_Type, Function) triplets. For each triplet, perform a Chain-of-Thought inference to: 1. Infer a specific `OPERATIONAL_PAIN_POINT` (M1). 2. Infer the associated `MEASURABLE_FAILURE_MODE` (M2). 3. Generate the following edge triples: M1 `CONTEXTUALIZED_BY` Problem, M1 `MANIFESTS_AS` M2, and AI\_Output `MITIGATES_FAILURE` M2. Output a single JSON file containing only the newly generated **M1/M2 nodes** and **their associated edge triples**." | **JSON Files (Chunked Output):** `INFERENCE_OUTPUT_CHUNK_XXX.json` |
| **III.2: Final Knowledge Graph Assembly and De-duplication** | **Input:** All Node Files (Phase I/0), `EXPLICIT_EDGES.json`, `CONTEXTUAL_EDGES.json`, and **ALL** `INFERENCE_OUTPUT_CHUNK_XXX.json` files. | **Prompt:** "Merge the generated nodes and edges from all sources. **Crucially, perform de-duplication** on the M1 and M2 nodes generated across the `INFERENCE_OUTPUT_CHUNK_XXX.json` files, ensuring only unique entities are kept. Combine all unique nodes and all generated edges into the final, single, comprehensive JSON structure as specified by the Integrated Knowledge Graph Structure." | **Final JSON File:** `E1S1_Knowledge_Graph_v1.0.json` |