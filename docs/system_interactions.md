# System Interactions & Process Flows

## Component Responsibility Matrix

| Component | Reads From | Writes To | Calls | Called By |
|-----------|-----------|-----------|-------|-----------|
| **Streamlit** | Firestore (factors) | - | Orchestrator | User |
| **ConversationOrchestrator** | - | - | IntentAnalyzer, ContextBuilder, LLMClient, JournalStore | Streamlit |
| **IntentAnalyzer** | - | - | LLMClient | Orchestrator |
| **ContextBuilder** | - | - | JournalStore, Graph | Orchestrator |
| **FactorJournalStore** | Firestore (all collections) | Firestore (all collections) | LLMClient (synthesis) | Orchestrator, ContextBuilder |
| **KnowledgeGraph** | Cloud Storage (once) | - | - | ContextBuilder |
| **VertexAIClient** | - | Vertex AI API | - | Orchestrator, IntentAnalyzer, JournalStore |

## Key Interactions

### 1. User Message → Response
```
User Input → Streamlit → Orchestrator → Intent Analyzer → LLM → Intent
                                      → Context Builder → JournalStore → Firestore
                                                        → Graph (in-memory)
                                      → LLM (streaming) → Tokens
                                      → Factor Inference → LLM → Inferences
                                      → JournalStore → Firestore (write)
```

### 2. Factor Update Flow
```
Inference → JournalStore.update_factor()
         → get_current_state() → Firestore read
         → create journal entry → Firestore write (journal/)
         → update current state → Firestore write (factors/)
         → update aggregates → Firestore write (metadata/)
```

### 3. Context Assembly Flow
```
ContextBuilder.build_context()
         → For each factor_id:
             → JournalStore.get_current_state() → Firestore read
             → JournalStore.get_journal_entries() → Firestore read
             → Graph.get_dependencies() → In-memory traversal
             → For each dependency:
                 → JournalStore.get_current_state() → Firestore read
         → Assemble context dict
         → Return to Orchestrator
```

### 4. Knowledge Tree Rendering
```
Streamlit (every 2 seconds)
         → Firestore query: /users/{user_id}/factors
         → Group by category
         → For each factor:
             → Graph.get_factor_metadata() → In-memory lookup
         → Render UI with st.expander()
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-29
