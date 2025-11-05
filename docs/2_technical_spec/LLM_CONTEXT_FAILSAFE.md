# LLM Context Size Failsafe

**Status:** Implemented ✅  
**Date:** 2025-11-05  
**Location:** `src/core/llm_client.py`

---

## Overview

Enforced failsafe mechanism that prevents sending unreasonably large context to the LLM and provides detailed debugging information when triggered.

### Thresholds

```python
WARN_PROMPT_CHARS = 20,000  # Warning threshold (~5k tokens)
MAX_PROMPT_CHARS = 30,000   # Hard limit (~7.5k tokens)
```

**Conservative by design:** Gemini supports 1M tokens, but we limit to ~7.5k to catch bugs early.

---

## Behavior

### ✅ Normal Prompts (< 20k chars)
- Pass silently
- No logging overhead
- Normal operation

### ⚠️ Large Prompts (20k - 30k chars)
- **Action:** Allow but log warning
- **Log Type:** `llm_context_warning`
- **Details Logged:**
  ```json
  {
    "caller": "OutputDiscoveryEngine.discover_output",
    "prompt_length": 25000,
    "warn_threshold": 20000,
    "max_allowed": 30000,
    "usage_percent": 83.3
  }
  ```

### 🚨 Oversized Prompts (> 30k chars)
- **Action:** Reject with `ValueError`
- **Log Type:** `llm_context_overflow`
- **Error Message:**
  ```
  Prompt size (35000 chars) exceeds maximum allowed (30000 chars).
  Caller: OutputDiscoveryEngine.discover_output.
  Exceeded by: 5000 chars.
  This is a failsafe to prevent sending unreasonably large context to the LLM.
  Check logs for details.
  ```

- **Details Logged:**
  ```json
  {
    "caller": "OutputDiscoveryEngine.discover_output",
    "prompt_length": 35000,
    "max_allowed": 30000,
    "exceeded_by": 5000,
    "prompt_preview": "First 500 chars of prompt...",
    "prompt_end": "...Last 500 chars of prompt"
  }
  ```

---

## Usage

### All LLM Calls Must Specify Caller

```python
# Discovery Engine
response = self.llm.generate(
    prompt,
    caller="OutputDiscoveryEngine.discover_output"
)

# Assessment Engine
response = self.llm.generate(
    prompt,
    caller=f"AssessmentEngine.infer_rating[{edge_type}]"
)

# Custom caller with context
response = self.llm.generate(
    prompt,
    caller="CustomEngine.method[specific_context]"
)
```

**Why caller parameter?**
- Identifies which component created oversized context
- Enables targeted debugging
- Shows up in both error message and logs

---

## Debugging Oversized Context

### Step 1: Check Logs

Look for `llm_context_overflow` or `llm_context_warning`:

```
🚨 CONTEXT SIZE FAILSAFE TRIGGERED by OutputDiscoveryEngine.discover_output
{
  "caller": "OutputDiscoveryEngine.discover_output",
  "prompt_length": 35000,
  "exceeded_by": 5000,
  "prompt_preview": "You are helping identify...",
  "prompt_end": "...return empty candidates array."
}
```

### Step 2: Identify Root Cause

**Common causes:**
1. **Catalog too large:** Loading all 46 outputs in prompt
2. **Conversation history:** Including entire chat history
3. **Verbose instructions:** Overly detailed prompts
4. **Data dumps:** Including raw data instead of summaries

### Step 3: Fix the Issue

**Solutions:**
- **Lazy loading:** Don't load data until needed
- **Summarization:** Condense catalog/data before including
- **Pagination:** Break large operations into smaller chunks
- **Filtering:** Only include relevant subset of data
- **Truncation:** Limit conversation history to recent messages

---

## Example: Discovery Engine Fix

### Before (Oversized)
```python
def _build_catalog_summary(self):
    """Include full details for all 46 outputs."""
    for output_id, output_data in self.output_catalog.items():
        summary += f"- {output_id}: {name}\n"
        summary += f"  Description: {description}\n"
        summary += f"  Pain points: {'; '.join(pain_points)}\n"
        summary += f"  Dependencies: {'; '.join(dependencies)}\n"
    # Result: ~15k chars for 46 outputs
```

### After (Optimized)
```python
def _build_catalog_summary(self):
    """Group by function, show only ID + name."""
    by_function = {}
    for output_id, output_data in self.output_catalog.items():
        function = output_data.get("function")
        by_function[function].append(f"{output_id} ({name})")
    
    for function, outputs in by_function.items():
        summary += f"**{function}**: {', '.join(outputs)}\n"
    # Result: ~3k chars for 46 outputs
```

---

## Testing

### Unit Tests (8 tests, all passing)

**File:** `tests/unit/test_llm_context_failsafe.py`

**Coverage:**
- ✅ Normal prompts pass
- ✅ Large prompts trigger warning
- ✅ Oversized prompts rejected
- ✅ Error includes caller info
- ✅ Error includes prompt preview/end
- ✅ Warning includes usage percent
- ✅ Works with `generate()`
- ✅ Works with `generate_stream()`

### Manual Testing

```python
from core.llm_client import LLMClient
from utils.logger import TechnicalLogger

logger = TechnicalLogger()
llm = LLMClient(logger=logger)

# Test warning threshold
prompt = "x" * 25000
llm.generate(prompt, caller="test_warning")
# Check logs for warning

# Test hard limit
prompt = "x" * 35000
try:
    llm.generate(prompt, caller="test_overflow")
except ValueError as e:
    print(f"Caught: {e}")
    # Check logs for detailed error
```

---

## Configuration

### Adjusting Thresholds

Edit `src/core/llm_client.py`:

```python
class LLMClient:
    # Conservative defaults
    MAX_PROMPT_CHARS = 30000   # Hard limit
    WARN_PROMPT_CHARS = 20000  # Warning threshold
```

**When to adjust:**
- **Increase:** If legitimate use cases hit limit
- **Decrease:** If costs are too high or responses slow
- **Monitor:** Check logs for warning frequency

### Disabling (NOT RECOMMENDED)

```python
# Remove validation from generate() and generate_stream()
# self._validate_prompt_size(prompt, caller)  # Comment out
```

**Why not recommended:**
- Loses debugging visibility
- Can cause expensive LLM calls
- Harder to diagnose issues
- May hit actual API limits

---

## Monitoring

### Key Metrics

**Warning Rate:**
```
grep "llm_context_warning" logs/*.log | wc -l
```

**Overflow Rate:**
```
grep "llm_context_overflow" logs/*.log | wc -l
```

**Average Prompt Size:**
```
grep "llm_call" logs/*.log | jq '.prompt_length' | awk '{sum+=$1; count++} END {print sum/count}'
```

### Alerts

**Set up alerts for:**
- Any `llm_context_overflow` (hard limit hit)
- High frequency of `llm_context_warning` (>10% of calls)
- Increasing average prompt size trend

---

## Benefits

### 1. Early Bug Detection
- Catches oversized context before expensive LLM call
- Identifies which component is responsible
- Prevents cascading issues

### 2. Cost Control
- Prevents accidentally sending huge prompts
- Conservative limits keep costs predictable
- Warning threshold enables proactive optimization

### 3. Debugging Support
- Caller parameter identifies source
- Prompt preview/end shows what's being sent
- Usage percent shows how close to limit

### 4. Performance
- Smaller prompts = faster responses
- Encourages efficient prompt design
- Forces developers to optimize

---

## Future Enhancements

### Token-Based Limits (vs Character-Based)
```python
# Use tiktoken for accurate token counting
import tiktoken
encoder = tiktoken.encoding_for_model("gpt-4")
token_count = len(encoder.encode(prompt))
```

### Dynamic Thresholds by Model
```python
MODEL_LIMITS = {
    "gemini-2.5-flash": 30000,
    "gemini-1.5-pro": 100000,
    "gpt-4": 8000
}
```

### Automatic Summarization
```python
if len(prompt) > WARN_THRESHOLD:
    prompt = self._auto_summarize(prompt)
```

### Prompt Compression
```python
# Remove redundant whitespace, compress JSON
prompt = self._compress_prompt(prompt)
```

---

## Related Documentation

- **LLM Client:** `src/core/llm_client.py`
- **Discovery Engine:** `src/engines/discovery.py`
- **Assessment Engine:** `src/engines/assessment.py`
- **Technical Logger:** `src/utils/logger.py`

---

**Status:** Production Ready ✅  
**Test Coverage:** 8/8 tests passing  
**Last Updated:** 2025-11-05
