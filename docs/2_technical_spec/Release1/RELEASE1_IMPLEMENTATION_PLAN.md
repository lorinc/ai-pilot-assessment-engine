# Release 1: Core Infrastructure Implementation Scaffold

**Duration:** Weeks 1-2  
**Status:** Planning  
**Date:** 2025-11-05

---

## Overview

Migrate POC infrastructure to production-ready `src/` structure with GCP integration. The POC is fully functional—we'll preserve its working components while adding Firebase Auth, Firestore persistence, and proper project structure.

---

## Key Migrations from POC

**Reuse directly:**
- `poc/core/gemini_client.py` → `src/core/llm_client.py` (streaming already works)
- `poc/core/session_manager.py` → `src/core/session_manager.py` (extend for Firestore)
- `poc/utils/technical_logger.py` → `src/utils/logger.py` (production logging)
- `poc/app.py` structure → `src/app.py` (Streamlit chat UI skeleton)

**Add new:**
- `src/core/firebase_client.py` - Auth + Firestore connection
- `src/core/graph_manager.py` - NetworkX ↔ Firestore sync
- `deployment/setup-infrastructure.sh` - GCP resource provisioning

---

## Implementation Tasks

### 1. GCP Infrastructure Setup (Day 1)

**Objective:** Provision all required GCP resources

**Actions:**
- Run `deployment/setup-infrastructure.sh` to provision:
  - Firestore database (Native mode, us-central1)
  - Cloud Storage bucket (static catalogs)
  - Vertex AI API enablement
  - Firebase Auth project
- Create service account with minimal permissions
- Store credentials in `.env` (gitignored)

**Deliverables:**
- GCP project configured
- Service account JSON key downloaded
- `.env` file with `GCP_PROJECT_ID`, `FIREBASE_CREDENTIALS_PATH`, `VERTEX_AI_LOCATION`

---

### 2. Project Structure (Day 2)

**Objective:** Create production-ready directory structure

**Structure:**
```
src/
├── core/
│   ├── llm_client.py          # Gemini streaming (from POC)
│   ├── firebase_client.py     # NEW: Auth + Firestore
│   ├── session_manager.py     # Extended for persistence
│   └── graph_manager.py       # NEW: NetworkX ↔ Firestore
├── utils/
│   └── logger.py              # Technical logging (from POC)
├── config/
│   └── settings.py            # Environment config
└── app.py                     # Streamlit entry point
```

**Actions:**
- Create directory structure
- Copy POC files to new locations
- Update imports
- Add `__init__.py` files

**Deliverables:**
- Clean `src/` structure
- All POC components migrated
- Import paths verified

---

### 3. Firebase Integration (Days 3-4)

**Objective:** Add authentication and persistence layer

**Components:**

**3.1 Firebase Client (`src/core/firebase_client.py`)**
- Initialize Firebase Admin SDK
- Firestore connection management
- User-scoped collection helpers

**3.2 Authentication**
- Google OAuth sign-in widget in Streamlit sidebar
- Session state linked to Firebase user ID
- Auth state persistence across page refreshes

**3.3 Firestore Schema (Initial)**
```
/users/{user_id}/
  conversations/{conversation_id}/
    - messages: [{role, content, timestamp}]
    - status: "in_progress" | "completed"
    - created_at
    - updated_at
```

**Actions:**
- Implement `FirebaseClient` class
- Add Google OAuth to Streamlit UI
- Create Firestore read/write helpers
- Test user isolation (multiple users, separate data)

**Deliverables:**
- Working Firebase Auth
- Firestore read/write operational
- User sessions persist across refreshes

---

### 4. Streamlit Chat UI (Day 5)

**Objective:** Production-ready chat interface with persistence

**Components:**

**4.1 Chat Interface**
- Message history display
- Input field with streaming responses
- Loading states and error handling

**4.2 Session Management**
- Load conversation history on login
- Auto-save messages to Firestore
- Session state synchronization

**4.3 Technical Log Viewer**
- Collapsible sidebar panel
- Real-time operation logging
- Filterable by log level

**Actions:**
- Migrate `poc/app.py` chat UI
- Add Firebase auth gate (redirect if not logged in)
- Wire Gemini streaming to chat messages
- Implement auto-save on message send
- Add technical log viewer component

**Deliverables:**
- Functional chat interface
- Messages persist to Firestore
- Technical logging visible
- Auth-protected access

---

### 5. End-to-End Test (Days 6-7)

**Objective:** Validate complete infrastructure stack

**Test Scenario:**
1. User navigates to app URL
2. Sees login screen (not authenticated)
3. Clicks "Sign in with Google"
4. Redirected to Google OAuth
5. Returns to app, authenticated
6. Sends message: "Our sales forecasts are always wrong"
7. LLM streams response in real-time
8. Message + response saved to Firestore
9. Refreshes page
10. Conversation history loads from Firestore
11. Technical log shows all operations
12. Logs out
13. Logs back in
14. Previous conversation still accessible

**Validation Checklist:**
- [ ] Firebase Auth working (Google OAuth)
- [ ] Firestore connection established (read/write conversations)
- [ ] Gemini streaming functional in Streamlit
- [ ] Session persists across page refreshes
- [ ] Technical logger operational
- [ ] User data isolated (test with 2+ accounts)
- [ ] Error handling graceful (network failures, auth errors)

**Deliverables:**
- Passing end-to-end test
- Documentation of test results
- Known issues logged (if any)

---

## Test Requirements

### Unit Tests

**Target Coverage:** 80%+ for core modules

**Test Structure:**
```
tests/
├── unit/
│   ├── test_firebase_client.py
│   ├── test_llm_client.py
│   ├── test_session_manager.py
│   └── test_logger.py
└── integration/
    ├── test_auth_flow.py
    ├── test_firestore_persistence.py
    └── test_streaming_chat.py
```

**Unit Test Requirements:**

**`test_firebase_client.py`**
- [ ] Initialize Firebase with valid credentials
- [ ] Handle missing credentials gracefully
- [ ] Create user-scoped document reference
- [ ] Read/write conversation data
- [ ] Handle Firestore connection errors

**`test_llm_client.py`**
- [ ] Initialize Gemini client
- [ ] Stream response with mock prompt
- [ ] Handle API rate limits
- [ ] Handle network timeouts
- [ ] Parse streaming chunks correctly

**`test_session_manager.py`**
- [ ] Create new session
- [ ] Load existing session from Firestore
- [ ] Update session state
- [ ] Handle session expiration
- [ ] Isolate user data by user_id

**`test_logger.py`**
- [ ] Log messages at different levels
- [ ] Format log entries correctly
- [ ] Limit max entries (circular buffer)
- [ ] Filter logs by level
- [ ] Export logs to JSON

**Mocking Strategy:**
- Mock Firestore with `google.cloud.firestore_v1.client.Client`
- Mock Vertex AI with `unittest.mock.patch`
- Use `pytest` fixtures for test data
- No real API calls in unit tests

---

### Integration Tests

**Target:** Critical user flows end-to-end

**Integration Test Requirements:**

**`test_auth_flow.py`**
- [ ] User signs in with Google OAuth (mocked)
- [ ] Session state persists user_id
- [ ] Unauthenticated user redirected to login
- [ ] User signs out, session cleared

**`test_firestore_persistence.py`**
- [ ] Write conversation to Firestore
- [ ] Read conversation from Firestore
- [ ] Update existing conversation
- [ ] Delete conversation
- [ ] Verify user isolation (user A cannot read user B's data)

**`test_streaming_chat.py`**
- [ ] Send message to LLM
- [ ] Receive streaming response
- [ ] Save message + response to Firestore
- [ ] Load conversation history
- [ ] Handle streaming interruption

**Test Environment:**
- Use Firestore emulator (no real GCP resources)
- Mock Vertex AI responses with pre-recorded outputs
- Run in CI/CD pipeline (GitHub Actions)

**Test Data:**
- Sample conversations in `tests/fixtures/conversations.json`
- Mock LLM responses in `tests/fixtures/llm_responses.json`
- Test user credentials in environment variables

---

## Success Criteria

✅ Firebase Auth working (Google OAuth)  
✅ Firestore connection established (read/write conversations)  
✅ Gemini streaming functional in Streamlit  
✅ Session persists across page refreshes  
✅ Technical logger operational  
✅ Unit tests passing (80%+ coverage)  
✅ Integration tests passing (critical flows)  
✅ Zero data model implementation (Release 2 work)

---

## Dependencies

**Python Packages (`requirements.txt`):**
```
streamlit>=1.28.0
google-cloud-aiplatform>=1.38.0
google-cloud-firestore>=2.13.0
firebase-admin>=6.2.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
```

**Environment Variables (`.env`):**
```
GCP_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./credentials/firebase-admin-key.json
VERTEX_AI_LOCATION=us-central1
```

**External Resources:**
- GCP project with billing enabled
- Firebase project (can be same as GCP project)
- Service account with roles:
  - `roles/datastore.user` (Firestore)
  - `roles/aiplatform.user` (Vertex AI)
  - `roles/firebase.admin` (Firebase Auth)

---

## Notes

- **POC Code:** Fully functional, copy-paste ready
- **No Data Model Work:** Release 1 focuses purely on infrastructure
- **Assessment Logic:** Deferred to Release 2 (Discovery & Assessment)
- **Catalogs:** Not loaded yet, will be added in Release 2
- **Graph Operations:** Stub only, NetworkX integration in Release 2

---

## Next Phase

**Release 2: Discovery & Assessment (Weeks 3-4)**
- Output discovery from natural language
- Edge-based assessment with conversational inference
- Evidence tracking with Bayesian aggregation
- MIN calculation and bottleneck identification
