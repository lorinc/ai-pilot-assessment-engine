# Knowledge Base Enrichment Tool

This tool uses Gemini (via Vertex AI) to iteratively scaffold and enrich the AI Pilot Assessment Engine knowledge base to its intended shape, following the specification in `docs/E1S1_enrichment_tool_specification.md`.

## Overview

The tool executes four phases:

- **Phase 0:** Pre-processing and script generation (node explosion)
- **Phase I:** Core node extraction and formatting
- **Phase II:** Explicit edge generation (rule-based linking)
- **Phase III:** LLM enrichment and inference (pain assessment with semantic deduplication)

## Features

- ✅ **Test Mode:** Process 2-3 nodes per category for validation before full run
- ✅ **Checkpointing:** Resume from interruption without losing progress
- ✅ **Semantic Deduplication:** Uses Vertex AI embeddings to merge similar M1/M2 nodes
- ✅ **Progress Tracking:** Real-time progress bars and detailed logging
- ✅ **Validation:** Schema validation at each phase

## Prerequisites

1. **Python 3.10+**
2. **Google Cloud Project** with Vertex AI API enabled
3. **Authentication:** One of:
   - Application Default Credentials (ADC): `gcloud auth application-default login`
   - Service account key in `.env` file
4. **Environment Variables** in project root `.env`:
   ```bash
   GOOGLE_API_KEY=your-api-key
   GOOGLE_CLOUD_PROJECT=your-project-id  # Optional, can use gcloud config
   ```

## Installation

```bash
# From the tools/kb_enrichment directory
cd tools/kb_enrichment

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start (Test Mode)

```bash
# Run all phases with 3 nodes per category
python main.py --all

# Run specific phase
python main.py --phase 0
python main.py --phase 1-3
```

### Full Production Run

```bash
# Edit config.yaml and set mode: "full"
python main.py --all --mode full
```

### Resume from Checkpoint

```bash
# Automatically resumes from last checkpoint
python main.py --all --resume
```

### Advanced Options

```bash
# Dry run (show what would be executed)
python main.py --all --dry-run

# Override config settings
python main.py --all --mode test --chunk-size 10

# Clean output directory and start fresh
python main.py --all --clean
```

## Configuration

Edit `config.yaml` to customize:

- **Test mode limits:** Number of nodes per category
- **Gemini model:** Model name, temperature, max tokens
- **Chunking:** Inference chunk size
- **Deduplication:** Similarity threshold, embedding model
- **Logging:** Level, format, output

## Output Structure

```
output/
├── checkpoint.json              # Progress tracking
├── enrichment.log              # Detailed logs
├── phase_0/
│   ├── FUNCTION_NODES.json
│   ├── SECTOR_NODES.json
│   └── TOOL_NODES.json
├── phase_1/
│   ├── AI_ARCHETYPE_NODES.json
│   ├── COMMON_MODEL_NODES.json
│   ├── AI_OUTPUT_NODES.json
│   ├── AI_PREREQUISITE_NODES.json
│   └── INFERENCE_CHUNK_*.json
├── phase_2/
│   ├── EXPLICIT_EDGES.json
│   └── CONTEXTUAL_EDGES.json
├── phase_3/
│   ├── INFERENCE_OUTPUT_CHUNK_*.json
│   └── E1S1_Knowledge_Graph_v1.0.json  # FINAL OUTPUT
└── stats/
    └── processing_stats.json
```

## Troubleshooting

### Authentication Errors

```bash
# Set up Application Default Credentials
gcloud auth application-default login

# Or verify service account key path
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### API Quota Exceeded

- Reduce `test_mode.nodes_per_category` in `config.yaml`
- Add delays between API calls (edit `gemini/client.py`)

### Checkpoint Corruption

```bash
# Remove checkpoint and restart
rm output/checkpoint.json
python main.py --all
```

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Phases

1. Create phase module in `phases/`
2. Add phase to `orchestrator.py`
3. Update prompts in `gemini/prompts.py`
4. Add tests in `tests/`

## Architecture

```
kb_enrichment/
├── main.py                 # CLI entry point
├── orchestrator.py         # Phase execution coordinator
├── config.yaml            # Configuration
├── phases/
│   ├── phase_0_preprocessing.py
│   ├── phase_1_extraction.py
│   ├── phase_2_edges.py
│   └── phase_3_inference.py
├── gemini/
│   ├── client.py          # Vertex AI wrapper
│   └── prompts.py         # Prompt templates
├── utils/
│   ├── file_io.py         # JSON I/O
│   ├── deduplication.py   # Semantic similarity
│   ├── validation.py      # Schema validation
│   └── checkpoint.py      # Progress tracking
└── tests/
    └── test_phases.py
```

## License

Part of the AI Pilot Assessment Engine project.
