# Phase 2 Placeholder Code - Archived

This directory contains code from earlier explorations that will be reimplemented in Phase 2.

## Contents

### Old Test Files
- `test_graph_builder.py` - Tests for knowledge graph operations
- `test_scope_matcher.py` - Tests for scope matching logic

### Old Knowledge Graph Module
- `knowledge_graph/graph_builder.py` - Graph construction from data files
- `knowledge_graph/schemas.py` - Pydantic schemas for graph nodes
- `knowledge_graph/scope_matcher.py` - Scope matching algorithms

## Why Archived?

These files were causing test failures because they reference:
- Data files that don't exist yet (`AI_archetypes.json`, etc.)
- Data models not yet implemented in Phase 1
- Features planned for Phase 2 (Discovery & Assessment)

## Phase 2 Implementation

When implementing Phase 2, use these files as reference but rebuild with:
- Output-centric factor model (1-5 stars)
- MIN calculation for bottleneck identification
- Edge-based assessment (not node-based)
- Firestore integration for persistence
- NetworkX for graph operations

See `docs/2_technical_spec/IMPLEMENTATION_DEPLOYMENT_PLAN.md` for Phase 2 plan.

---

**Archived:** 2025-11-05  
**Reason:** Clean Phase 1 completion, defer to Phase 2
