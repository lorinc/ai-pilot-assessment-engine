# Development Environment Instructions

**Purpose:** Guidelines, best practices, and workflows for developing this project.

---

## Quick Reference

### Core Documents

1. **[DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md)** - How to develop features
   - Vertical slicing over horizontal layers
   - UAT checkpoint frequency (max 2-3 days)
   - Working software over comprehensive tests

2. **[FEATURE_IDEAS.md](./FEATURE_IDEAS.md)** - How to handle feature ideas
   - Add to `docs/1_functional_spec/TBD.md`
   - Standard format for entries
   - Workflow from idea to implementation

---

## Key Principles

### 1. Test-Driven Development (TDD) - MANDATORY
Write tests BEFORE implementation, always.

**RED → GREEN → REFACTOR**
- **RED:** Write failing test
- **GREEN:** Make it pass
- **REFACTOR:** Improve code

**No exceptions:** Every feature must have tests written first.

### 2. Vertical Slicing
Build ONE complete feature end-to-end, then UAT, then next feature.

**❌ DON'T:** Build all models → all services → all UI → test  
**✅ DO:** Build Feature A (tests+model+service+UI) → UAT → Feature B → UAT

### 3. Frequent UAT Checkpoints
Maximum 2-3 days between user acceptance testing.

**Rule:** Never build more than one vertical slice without user testing.

### 4. Feature Ideas Go to TBD
When user mentions a feature idea:
- Add to `docs/1_functional_spec/TBD.md`
- Use standard format (see FEATURE_IDEAS.md)
- Discuss, decide, then implement (or defer)

---

## Development Cycle

```
1. Plan vertical slice (1 complete feature)
2. Write tests first (TDD RED) - 0.5-1 day
3. Implement to pass tests (TDD GREEN) - 1-2 days
4. UAT CHECKPOINT ← User tests
5. Refine based on feedback - 0.5-1 day
6. Refactor & document (TDD REFACTOR) - 0.5-1 day
7. UAT CHECKPOINT ← User tests again
8. Next feature (repeat with TDD)
```

---

## When Starting New Work

**Checklist:**
- [ ] **TDD:** Have I written the tests first? (RED phase)
- [ ] Can this be split into smaller vertical slices?
- [ ] What's the minimal working version?
- [ ] When is the first UAT checkpoint? (max 2-3 days)
- [ ] What specific behavior will user test?
- [ ] Have I added any new feature ideas to TBD.md?

---

## Project Structure

```
docs/
├── dev_env_instructions/          ← You are here
│   ├── README.md                  ← This file
│   ├── DEVELOPMENT_WORKFLOW.md    ← How to develop
│   └── FEATURE_IDEAS.md           ← How to handle ideas
│
├── 1_functional_spec/
│   └── TBD.md                     ← Feature ideas & decisions
│
├── 2_technical_spec/
│   └── Release2.1/
│       ├── PATTERN_ENGINE_IMPLEMENTATION.md
│       ├── TDD_PROGRESS.md
│       └── ...
│
└── ...
```

---

## Common Scenarios

### Scenario: User Has Feature Idea

1. **Capture:** Add to `docs/1_functional_spec/TBD.md` using standard format
2. **Discuss:** Explore trade-offs, alternatives
3. **Decide:** Implement now, later, or never
4. **Plan:** If implementing, create vertical slices with UAT checkpoints

### Scenario: Starting New Feature

1. **Define:** What's the minimal working version?
2. **Plan:** Break into vertical slices (max 2-3 days each)
3. **Build:** First slice (end-to-end)
4. **UAT:** User tests → feedback → adjust
5. **Repeat:** Next slice

### Scenario: Feature Taking Too Long

**If more than 3 days without UAT:**
- STOP building
- Create minimal demo of what's done
- UAT checkpoint NOW
- Get feedback before continuing

---

## Anti-Patterns to Avoid

❌ Building for weeks without user testing  
❌ "Let me finish everything first"  
❌ Horizontal layers (all backend, then all frontend)  
❌ Premature optimization  
❌ Feature creep without checkpoints  

---

## Related Memories

The AI assistant has memories about:
- Vertical slicing & UAT checkpoints
- TBD.md format and workflow
- Development best practices

These memories will guide future development automatically.

---

**Last Updated:** 2025-11-06  
**Maintained By:** Project team  
**Status:** Active guidelines
