# Changes: Switched from OpenAI to Gemini

## What Changed

**Original approach:** Used Outlines library with OpenAI API for structured generation

**Updated approach:** Uses existing project's `LLMClient` class with Gemini/Vertex AI

## Why This Is Better

1. **Consistency**: Uses same LLM infrastructure as rest of project
2. **Cost**: Gemini is ~10x cheaper than OpenAI for this use case
3. **No new dependencies**: Leverages existing setup
4. **Logging**: Inherits project's technical logging
5. **Configuration**: Uses project's `.env` and settings

## Technical Details

### Removed Dependencies
- `openai` package
- `outlines` package (Gemini support not mature yet)

### Added Integration
- Imports `LLMClient` from `src.core.llm_client`
- Uses Pydantic schema → JSON Schema → prompt engineering approach
- Gemini natively handles JSON output well with proper prompting

### How It Works

1. **Schema Definition**: Pydantic models define structure (unchanged)
2. **Schema Extraction**: Convert Pydantic to JSON Schema
3. **Prompt Engineering**: Include schema in prompt, ask for JSON output
4. **Response Parsing**: Clean and parse JSON response
5. **Validation**: Pydantic validates parsed JSON

This approach is more flexible than Outlines' constrained generation and works well with Gemini's strong instruction-following capabilities.

## Cost Comparison

| Provider | Model | Cost per 10 tests | Notes |
|----------|-------|-------------------|-------|
| OpenAI | gpt-4o-mini | ~$0.01 | Original approach |
| OpenAI | gpt-4o | ~$0.10 | Higher accuracy |
| **Gemini** | **gemini-1.5-flash** | **~$0.0004** | **Current (25x cheaper!)** |
| Gemini | gemini-1.5-pro | ~$0.01 | Higher accuracy option |

## Files Modified

- `extractor.py` - Switched to LLMClient, removed Outlines
- `test_runner.py` - Updated to check GCP config instead of OpenAI key
- `validate_setup.py` - Check for vertexai/LLMClient instead of openai/outlines
- `requirements.txt` - Removed external dependencies
- `setup.sh` - Updated instructions
- `QUICKSTART.md` - Updated setup steps
- `TESTBED_README.md` - Updated documentation

## No Changes Needed

- `schemas.py` - Pydantic models unchanged
- `test_cases.py` - Test cases unchanged
- Core testing logic - Unchanged

## Next Steps

Same as before:
1. Run validation: `python3 validate_setup.py`
2. Run tests: `python3 test_runner.py`
3. Iterate on prompt/schema to improve accuracy
