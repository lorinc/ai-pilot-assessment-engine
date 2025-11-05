# Quick Start Guide - Phase 1

Get the AI Pilot Assessment Engine running in under 5 minutes.

---

## Option 1: Development Mode (Recommended for Testing)

No GCP credentials needed. Perfect for development and testing.

### Step 1: Install Dependencies

```bash
# Create/activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Environment Variables

```bash
export MOCK_LLM=true
export MOCK_FIREBASE=true
export GCP_PROJECT_ID=test-project
```

### Step 3: Run the Application

```bash
streamlit run src/app.py
```

### Step 4: Test It

1. Open browser at `http://localhost:8501`
2. Click "Sign In (Mock)" button
3. Type a message: "Our sales forecasts are always wrong"
4. See mock LLM response stream in real-time
5. Check technical log in sidebar

**That's it!** You're running Phase 1 infrastructure.

---

## Option 2: Production Mode (With GCP)

For production deployment with real Firebase and Gemini.

### Prerequisites

- GCP account with billing enabled
- `gcloud` CLI installed and authenticated

### Step 1: Provision Infrastructure

```bash
# Configure deployment settings
cp deployment/.env.template deployment/.env
# Edit deployment/.env with your GCP project ID

# Run infrastructure setup
./deployment/setup-infrastructure.sh
```

This will create:
- Firestore database
- Cloud Storage bucket
- Vertex AI API access
- Firebase Auth project
- Service account

### Step 2: Configure Application

```bash
# Create application .env
cp .env.template .env

# Edit .env with:
# - GCP_PROJECT_ID=your-project-id
# - FIREBASE_CREDENTIALS_PATH=./deployment/keys/firebase-admin-key.json
# - MOCK_LLM=false
# - MOCK_FIREBASE=false
```

### Step 3: Run Application

```bash
streamlit run src/app.py
```

### Step 4: Deploy to Cloud Run (Optional)

```bash
# Build and deploy
gcloud run deploy ai-assessment-engine \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Running Tests

### All Tests

```bash
pytest
```

### Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/ -v

# Logger tests
pytest tests/unit/test_logger.py -v

# LLM client tests
pytest tests/unit/test_llm_client.py -v
```

### With Coverage

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Troubleshooting

### "Module not found" errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Firebase credentials not found"

```bash
# Use mock mode for development
export MOCK_FIREBASE=true
```

### "Vertex AI not found"

```bash
# Use mock mode for development
export MOCK_LLM=true
```

### Port already in use

```bash
# Use different port
streamlit run src/app.py --server.port 8502
```

---

## What's Working in Phase 1

✅ Streamlit chat interface  
✅ LLM streaming (mock mode)  
✅ Firebase Auth framework  
✅ Firestore persistence (mock mode)  
✅ Session management  
✅ Technical logging  
✅ 18 passing unit tests  

---

## What's Coming in Phase 2

🔜 Output discovery from natural language  
🔜 Edge-based assessment engine  
🔜 Evidence tracking  
🔜 MIN calculation  
🔜 Bottleneck identification  
🔜 NetworkX graph operations  

---

## Need Help?

- **Documentation:** See `src/README.md`
- **Implementation Plan:** See `docs/2_technical_spec/IMPLEMENTATION_DEPLOYMENT_PLAN.md`
- **Phase 1 Details:** See `docs/2_technical_spec/phase1_core_infrastructure.md`
- **Completion Report:** See `PHASE1_COMPLETION.md`
