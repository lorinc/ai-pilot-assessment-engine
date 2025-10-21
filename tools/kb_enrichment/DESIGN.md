# KB Enrichment Tool - Design Document

## Overview

This tool implements the E1S1 enrichment specification using Gemini (via Vertex AI) to iteratively scaffold and enrich the knowledge base. It follows a four-phase approach with checkpointing, semantic deduplication, and test mode support.

## Architecture

### Core Components

```
kb_enrichment/
├── main.py                    # CLI entry point
├── orchestrator.py            # Phase coordination
├── config.yaml               # Configuration
├── gemini/
│   ├── client.py             # Vertex AI wrapper
│   └── prompts.py            # Prompt templates
├── phases/
│   ├── phase_0_preprocessing.py
│   ├── phase_1_extraction.py
│   ├── phase_2_edges.py
│   └── phase_3_inference.py
└── utils/
    ├── file_io.py            # JSON I/O
    ├── checkpoint.py         # Progress tracking
    ├── validation.py         # Schema validation
    └── deduplication.py      # Semantic similarity
```

### Design Decisions

#### 1. Phase 0: Script Generation vs Direct Implementation

**Decision:** Use Gemini to generate the explosion script (as per spec)

**Rationale:**
- Follows the specification exactly
- Demonstrates Gemini's code generation capabilities
- Allows for flexibility in handling edge cases
- Generated script can be inspected and modified if needed

**Trade-offs:**
- Slower than direct implementation
- Potential for generation errors
- Requires script execution subprocess

#### 2. Test Mode Implementation

**Decision:** Limit nodes at input stage, not output stage

**Rationale:**
- Reduces API calls and costs
- Faster iteration during development
- More realistic test of full pipeline
- Easier to validate results

**Implementation:**
- Apply limits when loading source data
- Limit applies to each node category independently
- Default: 3 nodes per category

#### 3. Checkpointing Strategy

**Decision:** JSON-based checkpoint file with granular progress tracking

**Rationale:**
- Human-readable format
- Easy to inspect and debug
- Supports resumption at phase and chunk level
- No external dependencies

**Checkpoint Structure:**
```json
{
  "last_completed_phase": "1",
  "phase_0": {"completed": true, "files_generated": [...]},
  "phase_3": {
    "total_chunks": 127,
    "chunks_processed": 42,
    "chunks_completed": ["CHUNK_001", "CHUNK_002", ...]
  }
}
```

#### 4. Semantic Deduplication

**Decision:** Use Vertex AI text-embedding-004 with cosine similarity

**Rationale:**
- Consistent with project's Vertex AI stack
- High-quality embeddings (768 dimensions)
- Handles semantic similarity better than string matching
- Configurable threshold (default: 0.85)

**Process:**
1. Extract text from M1/M2 nodes (name + description)
2. Generate embeddings in batches
3. Compute cosine similarity matrix
4. Merge nodes above threshold
5. Update edge references

#### 5. Business Sector Simplification

**Decision:** Create nodes only at category level, not individual sectors

**Rationale:**
- Reduces graph complexity
- Aligns with user requirement
- Individual sectors stored as metadata/examples
- Category provides sufficient granularity for traversal

**Implementation:**
- Phase 0 script generates SECTOR_NODES.json with categories only
- Individual sector data preserved in node metadata
- Tools/processes linked to category level

#### 6. Error Handling and Resumption

**Decision:** Sequential processing with checkpoint-based resumption

**Rationale:**
- Simpler than parallel processing
- Easier to debug
- Sufficient for infrequent runs
- Checkpoint allows resumption after failures

**Error Handling:**
- Catch and log errors per chunk
- Record in checkpoint
- Continue processing in test mode
- Fail fast in production mode

## Prompt Engineering

### Key Principles

1. **Structured Output:** Request JSON format explicitly
2. **Few-shot Examples:** Include example outputs in prompts
3. **Chain-of-Thought:** For Phase 3 inference, request step-by-step reasoning
4. **Context Injection:** Provide relevant node IDs and metadata
5. **Validation Instructions:** Specify required fields and formats

### Prompt Templates

Each phase has dedicated prompts in `gemini/prompts.py`:

- **Phase 0.1:** Script generation with detailed requirements
- **Phase 1.1:** Node extraction with schema specification
- **Phase 1.2:** Chunking script generation
- **Phase 2.1/2.2:** Edge generation with relationship types
- **Phase 3.1:** Pain inference with CoT reasoning
- **Phase 3.2:** Final assembly (handled programmatically)

## Data Flow

```
Input Data (JSON)
    ↓
Phase 0: Node Explosion
    ├── FUNCTION_NODES.json
    ├── SECTOR_NODES.json (categories only)
    └── TOOL_NODES.json
    ↓
Phase 1: Node Extraction
    ├── AI_ARCHETYPE_NODES.json
    ├── COMMON_MODEL_NODES.json
    ├── AI_OUTPUT_NODES.json
    ├── AI_PREREQUISITE_NODES.json
    ├── PROBLEM_NODES.json
    └── INFERENCE_CHUNK_*.json
    ↓
Phase 2: Edge Generation
    ├── EXPLICIT_EDGES.json
    └── CONTEXTUAL_EDGES.json
    ↓
Phase 3: Inference & Assembly
    ├── INFERENCE_OUTPUT_CHUNK_*.json
    └── E1S1_Knowledge_Graph_v1.0.json (FINAL)
```

## Configuration

### Key Parameters

- **mode:** "test" or "full"
- **test_mode.nodes_per_category:** Node limit for test runs (default: 3)
- **chunking.inference_chunk_size:** Triplets per chunk (default: 15)
- **deduplication.similarity_threshold:** Merge threshold (default: 0.85)
- **gemini.model:** Model name (default: "gemini-1.5-pro")
- **gemini.temperature:** Sampling temperature (default: 0.2)

### Environment Variables

Required in `.env` file at project root:

```bash
GOOGLE_API_KEY=your-api-key
GOOGLE_CLOUD_PROJECT=your-project-id  # Optional
```

## Testing Strategy

### Unit Tests

- File I/O operations
- Checkpoint management
- Validation logic
- Deduplication algorithm (with mock embeddings)

### Integration Tests

- Full pipeline in test mode (requires credentials)
- Validation of final graph structure
- Checkpoint resumption

### Manual Testing

1. Run in test mode with 2-3 nodes
2. Inspect intermediate outputs
3. Validate final graph
4. Test resumption after interruption

## Performance Considerations

### API Costs

Estimated costs for full run (assuming ~1000 nodes):

- **Phase 0-2:** ~10-20 API calls (~$0.05)
- **Phase 3:** ~100-150 chunks (~$2-5)
- **Embeddings:** ~500-1000 nodes (~$0.01)
- **Total:** ~$2-6 per full run

### Optimization Opportunities

1. **Batch Processing:** Group similar tasks
2. **Caching:** Cache embeddings for repeated runs
3. **Parallel Chunks:** Process Phase 3 chunks in parallel (future)
4. **Prompt Optimization:** Reduce token usage

## Future Enhancements

1. **Parallel Processing:** Use asyncio for Phase 3 chunks
2. **Embedding Cache:** Persist embeddings between runs
3. **Interactive Review:** UI for reviewing M1/M2 merges
4. **Incremental Updates:** Support adding new nodes without full rebuild
5. **Quality Metrics:** Track inference quality and consistency
6. **Alternative Models:** Support for other LLMs (Claude, GPT-4)

## Troubleshooting

### Common Issues

**Issue:** "Failed to initialize Vertex AI"
- **Solution:** Check `GOOGLE_CLOUD_PROJECT` env var or run `gcloud auth application-default login`

**Issue:** "Script execution failed"
- **Solution:** Inspect generated script in `output/phase_0/explode_discovery.py`

**Issue:** "Checkpoint corruption"
- **Solution:** Delete `output/checkpoint.json` and restart

**Issue:** "API quota exceeded"
- **Solution:** Reduce `test_mode.nodes_per_category` or add rate limiting

## References

- [E1S1 Enrichment Specification](../../docs/E1S1_enrichment_tool_specification.md)
- [Knowledge Graph Dimensions](../../docs/E1S1_enrichment_dimansions_v2.md)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Gemini API Reference](https://ai.google.dev/docs)
