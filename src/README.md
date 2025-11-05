# Source Code - Phase 1: Core Infrastructure

This directory contains the production implementation of the AI Pilot Assessment Engine.

## Structure

```
src/
├── core/                   # Core business logic
│   ├── llm_client.py      # Gemini LLM integration with streaming
│   ├── firebase_client.py # Firebase Auth & Firestore persistence
│   ├── session_manager.py # Session state management
│   └── graph_manager.py   # NetworkX ↔ Firestore sync (Phase 2)
├── utils/                  # Utilities
│   └── logger.py          # Technical logging
├── config/                 # Configuration
│   └── settings.py        # Environment settings
├── data/                   # Static data (catalogs, templates)
└── app.py                 # Streamlit application entry point
```

## Phase 1 Components

### Core Modules

**`core/llm_client.py`**
- Gemini 1.5 Flash integration via Vertex AI
- Streaming and non-streaming generation
- Prompt building with conversation history
- Mock mode for testing

**`core/firebase_client.py`**
- Firebase Admin SDK initialization
- Google OAuth token verification
- Firestore CRUD operations
- User-scoped data isolation
- Mock mode for testing

**`core/session_manager.py`**
- Streamlit session state management
- Conversation persistence to Firestore
- Message history tracking
- Phase tracking (discovery, assessment, etc.)

**`utils/logger.py`**
- Technical logging for observability
- Log levels: DEBUG, INFO, WARNING, ERROR
- Circular buffer (max entries limit)
- Summary statistics

**`config/settings.py`**
- Environment variable management
- GCP configuration
- Firebase configuration
- Mock mode flags for testing

### Main Application

**`app.py`**
- Streamlit chat interface
- Firebase authentication flow
- Real-time LLM streaming
- Technical log viewer
- Session controls

## Running the Application

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **For development (mock mode):**
   ```bash
   export MOCK_LLM=true
   export MOCK_FIREBASE=true
   ```

4. **For production:**
   - Run `deployment/setup-infrastructure.sh` to provision GCP resources
   - Download Firebase credentials JSON
   - Set `FIREBASE_CREDENTIALS_PATH` in `.env`

### Start the Application

```bash
streamlit run src/app.py
```

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run specific test types:
```bash
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
```

## Mock Mode

Both LLM and Firebase clients support mock mode for development without GCP credentials:

```bash
export MOCK_LLM=true
export MOCK_FIREBASE=true
```

In mock mode:
- LLM returns canned responses
- Firebase operations succeed without real database
- No GCP API calls or costs

## Next Steps (Phase 2)

Phase 2 will add:
- Output discovery from natural language
- Edge-based assessment engine
- Evidence tracking with Bayesian aggregation
- MIN calculation and bottleneck identification
- Graph operations (NetworkX ↔ Firestore)

See `docs/2_technical_spec/IMPLEMENTATION_DEPLOYMENT_PLAN.md` for full roadmap.
