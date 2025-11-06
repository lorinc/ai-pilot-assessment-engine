# Release 2.2: Situational Awareness

**Type:** UX Infrastructure - Dynamic Conversation Management  
**Status:** Specification  
**Date:** 2025-11-06

---

## Overview

Replace broken global release/phase logic with dynamic situational awareness system that enables:
- Non-linear conversation flows
- Multi-output assessment
- User agency preservation
- Natural conversation patterns

**Why 2.2:** Must exist BEFORE Release 3 complexity (context extraction, recommendations).

---

## Quick Links

### Core Documentation
- **[Implementation Plan](SITUATIONAL_AWARENESS_IMPLEMENTATION.md)** - Technical implementation plan
- **[Full Design Spec](../../1_functional_spec/SITUATIONAL_AWARENESS.md)** - Complete functional specification

### Appendix
- **[Design Rationale](appendix/NO_GLOBAL_RELEASES.md)** - Why global phases/releases are wrong
- **[Code Audit](appendix/RELEASE_LOGIC_AUDIT.md)** - Current violations and migration strategy

---

## What Gets Built

### Week 1: Core Infrastructure
- `SituationalAwareness` class with 8 dimensions
- Remove `phase`/`release` property from session
- Composition always sums to 100%

### Week 2: Pattern Integration
- Add `situation_affinity` to behaviors
- Pattern selection algorithm
- LLM prompt integration

### Week 3: Intent Detection
- Replace release-based routing with intent detection
- Enable non-linear conversation
- Multi-output support

### Week 4: Refinement
- Tune weights and decay rates
- Performance optimization
- Documentation

---

## Key Concepts

### Situational Awareness Model

**8 Dimensions** (always sum to 100%):
1. **Discovery** - Identifying outputs, context
2. **Assessment** - Rating edges, gathering evidence
3. **Analysis** - Calculating bottlenecks, understanding issues
4. **Recommendation** - Suggesting AI pilots
5. **Feasibility** - Checking prerequisites
6. **Clarification** - Resolving ambiguity
7. **Validation** - Confirming understanding
8. **Meta** - System help, conversation management

**Dynamic Composition:**
- Situation evolves based on user actions
- Multiple dimensions can be active simultaneously
- Pattern selection driven by situation affinity
- No forced linear progression

---

## Migration Strategy

### Backward Compatibility

**Release 1-2**: Dual tracking
- Keep existing release logic
- Add situational awareness in parallel
- Log both, compare results

**Stage 3**: Switch
- Remove release-based routing
- Use intent + situation
- Monitor for regressions

**Stage 4**: Cleanup
- Delete release enum
- Remove release properties
- Update all references

### Risk Mitigation
- Feature flag for new logic
- A/B test with subset of users
- Rollback plan if quality drops
- Extensive logging for debugging

---

## Success Criteria

✅ No global phase/release logic in codebase  
✅ Situation always sums to 100%  
✅ User can assess multiple outputs simultaneously  
✅ User can get recommendations at any confidence level  
✅ Pattern selection reflects situation  
✅ Conversation flows naturally (no forced transitions)

---

## Dependencies

**Requires:**
- Release 2 complete (graph operations, MIN calculation)
- **Release 2.1 complete (pattern engine, trigger detection, knowledge tracking)**

**Blocks:**
- Release 3 (context extraction needs intent detection)
- Release 4 (recommendations need multi-output support)

---

## Timeline

**Duration:** 4 weeks  
**Sequential after:** Release 2.1 (pattern engine)  
**Start:** After Release 2.1 complete

---

**Owner:** Technical Lead  
**Status:** Ready to implement  
**Priority:** High - Blocks Release 3
