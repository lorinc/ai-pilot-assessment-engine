# Quick Start Guide

Get the KB enrichment tool running in 5 minutes.

## Prerequisites

1. **Python 3.10+** installed
2. **Google Cloud Project** with Vertex AI API enabled
3. **Authentication** configured (see below)

## Setup

### 1. Install Dependencies

```bash
cd tools/kb_enrichment
pip install -r requirements.txt
```

### 2. Configure Authentication

**Option A: Application Default Credentials (Recommended)**
```bash
gcloud auth application-default login
```

**Option B: Service Account Key**

Add to project root `.env` file:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### 3. Verify Configuration

Check `config.yaml` settings:
- `mode: "test"` - Runs with 3 nodes per category
- `gemini.model: "gemini-1.5-pro"` - Model to use
- `paths.input_data: "../../src/data"` - Source data location

## Run

### Test Mode (Recommended First Run)

Process 3 nodes per category to validate setup:

```bash
python main.py --all
```

**Expected output:**
```
PHASE 0: PRE-PROCESSING AND SCRIPT GENERATION
[Task 0.1] Generating node explosion script...
✓ Script generated: output/phase_0/explode_discovery.py
[Task 0.2] Executing node explosion...
✓ Generated: FUNCTION_NODES.json
✓ Generated: SECTOR_NODES.json
✓ Generated: TOOL_NODES.json
✓ Phase 0 complete. Generated 3 files.

PHASE 1: CORE NODE EXTRACTION AND FORMATTING
...
```

**Time:** ~5-10 minutes  
**Cost:** ~$0.10-0.50

### Full Production Run

Process entire dataset:

```bash
# Edit config.yaml: set mode: "full"
python main.py --all --mode full
```

**Time:** ~30-60 minutes  
**Cost:** ~$2-6

## Output

Final knowledge graph:
```
tools/kb_enrichment/output/phase_3/E1S1_Knowledge_Graph_v1.0.json
```

Structure:
```json
{
  "metadata": {
    "version": "1.0",
    "total_nodes": 500,
    "total_edges": 1200,
    "node_type_counts": {...},
    "edge_type_counts": {...}
  },
  "nodes": [...],
  "edges": [...]
}
```

## Validate

Check the output quality:

```bash
python main.py --validate
```

## Common Commands

```bash
# Run specific phase
python main.py --phase 0

# Run phase range
python main.py --phase 1-3

# Resume after interruption
python main.py --all --resume

# Force re-run
python main.py --all --force

# Clean and restart
python main.py --all --clean

# Dry run (show what would execute)
python main.py --all --dry-run
```

## Troubleshooting

### Authentication Error

```
Error: Failed to initialize Vertex AI
```

**Solution:**
```bash
# Set up ADC
gcloud auth application-default login

# Or set project ID
export GOOGLE_CLOUD_PROJECT=your-project-id
```

### Script Generation Failed

```
Error: Script execution failed
```

**Solution:**
1. Check generated script: `output/phase_0/explode_discovery.py`
2. Run manually to see error: `python output/phase_0/explode_discovery.py`
3. Fix and re-run: `python main.py --phase 0 --force`

### API Quota Exceeded

```
Error: 429 Resource exhausted
```

**Solution:**
1. Reduce test mode limit in `config.yaml`:
   ```yaml
   test_mode:
     nodes_per_category: 2
   ```
2. Add delay between API calls (edit `gemini/client.py`)

### Checkpoint Issues

```
Warning: Checkpoint corruption detected
```

**Solution:**
```bash
# Reset checkpoint
rm output/checkpoint.json
python main.py --all
```

## Next Steps

1. **Review Test Output:** Inspect `output/phase_3/E1S1_Knowledge_Graph_v1.0.json`
2. **Adjust Configuration:** Tune similarity threshold, chunk size, etc.
3. **Run Full Pipeline:** Switch to `mode: "full"` in config
4. **Integrate with Project:** Load graph into NetworkX (see main project README)

## Support

- **Documentation:** See [README.md](README.md) and [DESIGN.md](DESIGN.md)
- **Specification:** See [E1S1 Enrichment Spec](../../docs/E1S1_enrichment_tool_specification.md)
- **Issues:** Check logs in `output/enrichment.log`
