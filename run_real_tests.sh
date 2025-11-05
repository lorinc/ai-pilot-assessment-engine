#!/bin/bash
# Run integration tests with real GCP services
# This will incur small API costs (~$0.05 total)

set -e

echo "🧪 Running integration tests with real GCP services..."
echo ""
echo "⚠️  WARNING: This will make real API calls and incur costs (~$0.05)"
echo ""

# Activate virtual environment
source venv/bin/activate

# Run tests with environment variables set
# Note: Must set BEFORE pytest imports modules
echo "Running Firebase integration tests..."
MOCK_FIREBASE=false \
MOCK_LLM=false \
GCP_PROJECT_ID=ai-assessment-engine-476709 \
GCP_LOCATION=europe-west1 \
GEMINI_MODEL=gemini-1.5-flash \
FIREBASE_CREDENTIALS_PATH=/home/lorinc/CascadeProjects/ai-pilot-assessment-engine/deployment/keys/service-account-key.json \
pytest tests/integration/test_real_firebase.py -v -m requires_gcp --tb=short

echo ""
echo "Running LLM integration tests..."
MOCK_FIREBASE=false \
MOCK_LLM=false \
GCP_PROJECT_ID=ai-assessment-engine-476709 \
GCP_LOCATION=europe-west1 \
GEMINI_MODEL=gemini-1.5-flash \
FIREBASE_CREDENTIALS_PATH=/home/lorinc/CascadeProjects/ai-pilot-assessment-engine/deployment/keys/service-account-key.json \
pytest tests/integration/test_real_llm.py -v -m requires_gcp --tb=short

echo ""
echo "✅ All real integration tests completed!"
echo ""
echo "💰 Estimated API costs: ~$0.05"
