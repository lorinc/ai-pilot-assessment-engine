# Configuration Management System

**CRITICAL SYSTEM COMPONENT** - Unified CRUD interface for pattern engine configuration.

## Overview

This system provides a declarative, YAML-driven approach to managing all pattern engine elements:
- **Triggers** - When to detect user intent
- **Behaviors** - How to respond
- **Patterns** - Trigger → Behavior mappings
- **Knowledge Dimensions** - What to track

## Why This Exists

**Problem:** Adding/modifying triggers and behaviors required writing Python code, running tests manually, and risking breaking changes.

**Solution:** Declarative YAML configuration with automated validation, testing, and hot reload.

**Benefits:**
- ✅ **2-minute process** to add a trigger (vs 30+ minutes of coding)
- ✅ **1-minute process** to modify a behavior
- ✅ **Automatic validation** - catches errors before deployment
- ✅ **No code changes** - just edit YAML
- ✅ **Version controlled** - Git tracks all changes
- ✅ **Hot reload** - no restart needed (future)

---

## Quick Start

### List all triggers
```bash
python scripts/config_management/manage.py list triggers
```

### Show trigger details
```bash
python scripts/config_management/manage.py show trigger T_RATE_EDGE
```

### Add a new trigger
```bash
python scripts/config_management/manage.py create trigger \
  --id T_TIMELINE_MENTIONED \
  --category context_extraction \
  --priority medium \
  --examples \
    "We need this by next month" \
    "The deadline is Q2" \
    "Timeline is 6 weeks"
```

### Update a trigger
```bash
# Add an example
python scripts/config_management/manage.py update trigger T_RATE_EDGE \
  --add-example "The quality is around 4 stars"

# Change priority
python scripts/config_management/manage.py update trigger T_RATE_EDGE \
  --priority critical

# Update threshold
python scripts/config_management/manage.py update trigger T_RATE_EDGE \
  --threshold 0.80
```

### Delete a trigger
```bash
python scripts/config_management/manage.py delete trigger T_OLD_TRIGGER --confirm
```

### Cache Management

**Show cache statistics:**
```bash
python scripts/config_management/manage.py cache-stats
```

**Clear cache for specific trigger:**
```bash
python scripts/config_management/manage.py clear-cache --trigger T_RATE_EDGE
```

**Clear all caches:**
```bash
python scripts/config_management/manage.py clear-cache --all
```

**Rebuild all embeddings:**
```bash
python scripts/config_management/manage.py rebuild-embeddings
# Or force rebuild even if cached:
python scripts/config_management/manage.py rebuild-embeddings --force
```

---

## Tools

### 1. `manage.py` - Unified CRUD Interface ⭐

**Main tool for all configuration management.**

#### Operations

**CREATE**
```bash
# Create trigger
python scripts/config_management/manage.py create trigger \
  --id T_NEW_TRIGGER \
  --category <category> \
  --priority <low|medium|high|critical> \
  --examples "example 1" "example 2" "example 3" \
  [--type user_implicit] \
  [--method semantic_similarity] \
  [--threshold 0.75] \
  [--description "Optional description"]

# Create pattern
python scripts/config_management/manage.py create pattern \
  --id PATTERN_NEW \
  --category <category> \
  --response-type <reactive|proactive> \
  --triggers T_TRIGGER_1 T_TRIGGER_2 \
  --behavior-id B_NEW_BEHAVIOR \
  --behavior-template "Template with {variables}"
```

**READ**
```bash
# Show details
python scripts/config_management/manage.py show trigger T_RATE_EDGE
python scripts/config_management/manage.py show pattern PATTERN_ACKNOWLEDGE_RATING

# List all
python scripts/config_management/manage.py list triggers
python scripts/config_management/manage.py list triggers --category assessment
```

**UPDATE**
```bash
# Update trigger
python scripts/config_management/manage.py update trigger T_RATE_EDGE \
  [--add-example "New example"] \
  [--remove-example "Old example"] \
  [--priority high] \
  [--threshold 0.80] \
  [--description "New description"]
```

**DELETE**
```bash
# Delete (requires confirmation)
python scripts/config_management/manage.py delete trigger T_OLD --confirm
```

---

### 2. `validate_config.py` - Configuration Validator

**Validates YAML syntax and schema.**

```bash
# Validate all trigger files
python scripts/config_management/validate_config.py

# Validate specific file
python scripts/config_management/validate_config.py \
  --file data/triggers/assessment_triggers.yaml
```

**What it checks:**
- ✅ YAML syntax
- ✅ Required fields present
- ✅ Valid categories, priorities, types
- ✅ Valid detection methods
- ✅ Threshold ranges (0.0-1.0)
- ✅ Minimum example count (warns if < 3)

---

---

## File Structure

```
data/
├── triggers/
│   ├── assessment_triggers.yaml
│   ├── discovery_triggers.yaml
│   ├── navigation_triggers.yaml
│   └── ...
├── patterns/
│   ├── assessment_patterns.yaml
│   ├── discovery_patterns.yaml
│   └── behaviors/
│       ├── assessment_behaviors.yaml
│       └── ...
└── config/
    ├── similarity_thresholds.yaml
    └── priority_rules.yaml

scripts/config_management/
├── README.md              # This file
├── manage.py              # Main CRUD interface
└── validate_config.py     # Validator
```

---

## YAML Schema

### Trigger Schema

```yaml
triggers:
  - id: T_TRIGGER_NAME              # Required: Uppercase, starts with T_
    category: assessment             # Required: See categories below
    priority: high                   # Required: low|medium|high|critical
    type: user_implicit              # Required: See types below
    description: "Optional description"
    
    detection:
      method: semantic_similarity    # Required: semantic_similarity|regex|keywords
      threshold: 0.75                # Required for semantic_similarity
      
      examples:                      # Required: At least 3 recommended
        - "Example message 1"
        - "Example message 2"
        - "Example message 3"
      
      fallback_patterns:             # Optional: Regex for fast path
        - '\d+\s*stars?'
        - 'is\s+(poor|good|excellent)'
      
      context_keywords:              # Optional: Additional keywords
        - 'data quality'
        - 'team execution'
      
      assessment_indicators:         # Optional: Indicator words
        - 'is'
        - 'rate'
```

### Pattern Schema

```yaml
patterns:
  - id: PATTERN_NAME                 # Required: Uppercase
    category: assessment             # Required
    response_type: reactive          # Required: reactive|proactive
    
    triggers:                        # Required: List of trigger IDs
      - T_TRIGGER_1
      - T_TRIGGER_2
    
    behaviors:                       # Required: At least one
      - id: B_BEHAVIOR_1
        weight: 0.6                  # Optional: Default 1.0
        template: |
          Response template with {variables}
      
      - id: B_BEHAVIOR_2
        weight: 0.4
        template: |
          Alternative response
    
    situation_affinity:              # Optional: For proactive patterns
      assessment: 0.9
      analysis: 0.3
    
    knowledge_updates:               # Optional
      - dimension: edge_rated
        value: true
```

---

## Valid Values

### Categories
- `assessment` - Rating/evaluating components
- `discovery` - Identifying outputs/problems
- `clarification` - Confusion/asking for help
- `navigation` - Progress/next steps
- `recommendation` - Asking for suggestions
- `context_extraction` - Timeline, budget, stakeholders
- `error_recovery` - System mistakes, contradictions
- `meta` - Review, summary, reflection

### Priorities
- `low` - Nice to have
- `medium` - Standard priority
- `high` - Important
- `critical` - Must handle immediately

### Trigger Types
- `user_explicit` - Direct user request
- `user_implicit` - Inferred from message
- `system_proactive` - System-initiated
- `system_reactive` - System response to state

### Detection Methods
- `semantic_similarity` - Embedding-based (recommended)
- `regex` - Pattern matching
- `keywords` - Keyword lists

### Response Types
- `reactive` - Answers user's immediate need
- `proactive` - Advances conversation

---

## Workflow

### Adding a New Trigger

**1. Create the trigger**
```bash
python scripts/config_management/manage.py create trigger \
  --id T_BUDGET_MENTIONED \
  --category context_extraction \
  --priority medium \
  --examples \
    "Our budget is $50k" \
    "We have about 100k to spend" \
    "Budget is tight"
```

**2. Verify it was created**
```bash
python scripts/config_management/manage.py show trigger T_BUDGET_MENTIONED
```

**3. Test it** (future: auto-generated tests)
```bash
pytest tests/patterns/
```

**4. Commit**
```bash
git add data/triggers/context_extraction_triggers.yaml
git commit -m "Add T_BUDGET_MENTIONED trigger"
```

---

### Modifying a Trigger

**1. Show current state**
```bash
python scripts/config_management/manage.py show trigger T_RATE_EDGE
```

**2. Make changes**
```bash
# Add more examples
python scripts/config_management/manage.py update trigger T_RATE_EDGE \
  --add-example "Quality is approximately 3 stars"

# Adjust threshold
python scripts/config_management/manage.py update trigger T_RATE_EDGE \
  --threshold 0.80
```

**3. Verify changes**
```bash
python scripts/config_management/manage.py show trigger T_RATE_EDGE
```

**4. Commit**
```bash
git add data/triggers/assessment_triggers.yaml
git commit -m "Update T_RATE_EDGE: add example, increase threshold"
```

---

## Best Practices

### Trigger Examples
- ✅ **Provide 5-10 examples** for good coverage
- ✅ **Include variations** (formal, casual, different phrasings)
- ✅ **Real user messages** when possible
- ❌ Don't use synthetic/artificial examples

### Priorities
- ✅ **critical** - Confusion, errors, system mistakes
- ✅ **high** - User requests, important actions
- ✅ **medium** - Context extraction, proactive suggestions
- ✅ **low** - Nice-to-have features

### Thresholds
- ✅ **0.75** - Default (good balance)
- ✅ **0.80-0.85** - Stricter (fewer false positives)
- ✅ **0.65-0.70** - Looser (catch more variations)
- ❌ Don't go below 0.60 (too many false positives)

### Validation
- ✅ **Always validate** before committing
- ✅ **Run tests** after changes
- ✅ **Review YAML** for syntax errors
- ❌ Don't skip validation

---

## Troubleshooting

### "Trigger already exists"
```bash
# Check if trigger exists
python scripts/config_management/manage.py show trigger T_NAME

# If you want to replace it, delete first
python scripts/config_management/manage.py delete trigger T_NAME --confirm
```

### "Validation failed"
```bash
# Run validator to see errors
python scripts/config_management/validate_config.py \
  --file data/triggers/your_file.yaml

# Common issues:
# - Missing required fields
# - Invalid category/priority
# - Threshold out of range (0.0-1.0)
# - YAML syntax error
```

### "File not found"
```bash
# List all triggers to see what exists
python scripts/config_management/manage.py list triggers

# Check file structure
ls -la data/triggers/
```

---

## Future Enhancements

**Planned for Week 2, Days 7-8:**
- ✅ Behavior variants (multiple templates with weights)
- ✅ Pattern updates (add/remove triggers)
- ✅ Auto-test generation from examples
- ✅ Hot reload (no restart needed)
- ✅ Interactive editor mode
- ✅ Bulk import/export
- ✅ Migration tools

---

## Related Documentation

- **TBD #29** - Change Management Pipeline (design doc)
- **TBD #28** - Semantic Intent Detection
- **Release 2.2 Progress** - `docs/2_technical_spec/Release2.2/PROGRESS.md`
- **Development Workflow** - `docs/dev_env_instructions/DEVELOPMENT_WORKFLOW.md`

---

## Support

**Issues?** Check:
1. This README
2. Run validator: `python scripts/config_management/validate_config.py`
3. Check YAML syntax
4. Review examples in `data/triggers/assessment_triggers.yaml`

**Questions?** See TBD #29 in `docs/1_functional_spec/TBD.md`
