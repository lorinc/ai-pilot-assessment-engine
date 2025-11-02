# Deployment Guide - Epic 1 Infrastructure Setup

## Overview

This guide provides a **complete, repeatable process** for setting up the GCP infrastructure for the AI Pilot Assessment Engine. Every command, every configuration, every permission is documented.

**Time estimate:** 1-2 hours for first-time setup  
**Prerequisites:** GCP account with billing enabled, `gcloud` CLI installed

---

## Table of Contents

1. [Prerequisites & Tools](#prerequisites--tools)
2. [GCP Project Setup](#gcp-project-setup)
3. [Enable Required APIs](#enable-required-apis)
4. [Service Account Configuration](#service-account-configuration)
5. [Firestore Database Setup](#firestore-database-setup)
6. [Cloud Storage Setup](#cloud-storage-setup)
7. [Firebase Authentication Setup](#firebase-authentication-setup)
8. [Vertex AI Configuration](#vertex-ai-configuration)
9. [Cloud Run Preparation](#cloud-run-preparation)
10. [Local Development Setup](#local-development-setup)
11. [Verification & Testing](#verification--testing)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites & Tools

### Required Tools

```bash
# 1. Install Google Cloud SDK
# macOS
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verify installation
gcloud --version

# 2. Install Node.js (required for Firebase CLI)
# Firebase CLI requires Node.js v20+ or v22+

# Option A: Using NodeSource repository (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Option B: Using nvm (Node Version Manager) - Recommended
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20

# Verify Node.js version (must be 20+)
node --version  # Should show v20.x.x or higher

# 3. Install Firebase CLI
npm install -g firebase-tools

# Verify installation
firebase --version  # Should show v14.x.x or higher

# 3. Install Python 3.11+ (for local development)
python3 --version  # Should be 3.11 or higher
```

### Required Accounts

- **GCP Account** with billing enabled
- **GitHub Account** (optional, for CI/CD)
- **Domain** (optional, for custom domain)

### Environment Variables Template

Create a file to store your configuration (DO NOT commit to git):

```bash
# deployment/.env.template
# Copy this to deployment/.env and fill in your values

# GCP Configuration
export GCP_PROJECT_ID="ai-pilot-assessment-prod"
export GCP_REGION="us-central1"
export GCP_ZONE="us-central1-a"

# Service Account
export SERVICE_ACCOUNT_NAME="assessment-engine-sa"
export SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

# Firestore
export FIRESTORE_DATABASE="(default)"

# Cloud Storage
export BUCKET_NAME="${GCP_PROJECT_ID}-static-knowledge"

# Cloud Run
export CLOUD_RUN_SERVICE_NAME="assessment-engine"
export CLOUD_RUN_REGION="us-central1"

# Vertex AI
export VERTEX_AI_LOCATION="us-central1"
export VERTEX_AI_MODEL="gemini-1.5-flash"

# Firebase
export FIREBASE_PROJECT_ID="${GCP_PROJECT_ID}"
```

---

## GCP Project Setup

### Step 1: Create GCP Project

```bash
# Set your desired project ID
export GCP_PROJECT_ID="ai-pilot-assessment-prod"

# Create the project
gcloud projects create ${GCP_PROJECT_ID} \
  --name="AI Pilot Assessment Engine" \
  --set-as-default

# Verify project creation
gcloud projects describe ${GCP_PROJECT_ID}

# Link billing account (replace BILLING_ACCOUNT_ID with your actual billing account)
# Find your billing account ID:
gcloud billing accounts list

# Link billing (replace 0X0X0X-0X0X0X-0X0X0X with your billing account ID)
gcloud billing projects link ${GCP_PROJECT_ID} \
  --billing-account=0X0X0X-0X0X0X-0X0X0X

# Set as default project for gcloud commands
gcloud config set project ${GCP_PROJECT_ID}
```

### Step 2: Verify Project Setup

```bash
# Verify project is set correctly
gcloud config get-value project

# Should output: ai-pilot-assessment-prod (or your project ID)
```

---

## Enable Required APIs

### Enable All Required APIs

```bash
# Enable all required APIs in one command
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  identitytoolkit.googleapis.com \
  firebase.googleapis.com \
  --project=${GCP_PROJECT_ID}

# Verify APIs are enabled
gcloud services list --enabled --project=${GCP_PROJECT_ID}
```

**Expected output should include:**
- `aiplatform.googleapis.com` - Vertex AI
- `firestore.googleapis.com` - Firestore
- `storage.googleapis.com` - Cloud Storage
- `run.googleapis.com` - Cloud Run
- `cloudbuild.googleapis.com` - Cloud Build
- `containerregistry.googleapis.com` - Container Registry
- `identitytoolkit.googleapis.com` - Firebase Auth
- `firebase.googleapis.com` - Firebase

---

## Service Account Configuration

### Step 1: Create Service Account

```bash
export SERVICE_ACCOUNT_NAME="assessment-engine-sa"
export SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

# Create service account
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
  --display-name="Assessment Engine Service Account" \
  --description="Service account for AI Pilot Assessment Engine Cloud Run service" \
  --project=${GCP_PROJECT_ID}

# Verify creation
gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} \
  --project=${GCP_PROJECT_ID}
```

### Step 2: Grant Required Permissions

```bash
# Grant Vertex AI User role (for LLM calls)
gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/aiplatform.user"

# Grant Firestore User role (for database operations)
gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/datastore.user"

# Grant Cloud Storage Object Viewer role (for reading static graph)
gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/storage.objectViewer"

# Grant Cloud Run Invoker role (for Cloud Run service)
gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/run.invoker"

# Grant Logs Writer role (for Cloud Logging)
gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/logging.logWriter"

# Verify permissions
gcloud projects get-iam-policy ${GCP_PROJECT_ID} \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT_EMAIL}"
```

### Step 3: Create Service Account Key (for Local Development)

```bash
# Create keys directory (ignored by git)
mkdir -p deployment/keys

# Generate service account key
gcloud iam service-accounts keys create deployment/keys/service-account-key.json \
  --iam-account=${SERVICE_ACCOUNT_EMAIL} \
  --project=${GCP_PROJECT_ID}

# Set environment variable for local development
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/deployment/keys/service-account-key.json"

# Verify key was created
ls -l deployment/keys/service-account-key.json
```

**⚠️ SECURITY WARNING:**
- **NEVER commit service account keys to git**
- Add `deployment/keys/` to `.gitignore`
- Rotate keys regularly (every 90 days)
- Use Workload Identity for production (Cloud Run doesn't need keys)

---

## Firestore Database Setup

### Step 1: Create Firestore Database

```bash
# Create Firestore database in Native mode
gcloud firestore databases create \
  --location=${GCP_REGION} \
  --project=${GCP_PROJECT_ID}

# Verify database creation
gcloud firestore databases describe --project=${GCP_PROJECT_ID}
```

**Note:** You can only create one Firestore database per project. Choose location carefully (cannot be changed later).

### Step 2: Create Firestore Indexes

For Epic 1, we need indexes for journal entry queries:

```bash
# Create firestore.indexes.json
cat > deployment/firestore.indexes.json <<'EOF'
{
  "indexes": [
    {
      "collectionGroup": "journal",
      "queryScope": "COLLECTION",
      "fields": [
        {
          "fieldPath": "timestamp",
          "order": "DESCENDING"
        }
      ]
    }
  ]
}
EOF

# Deploy indexes
gcloud firestore indexes composite create \
  --collection-group=journal \
  --query-scope=COLLECTION \
  --field-config field-path=timestamp,order=descending \
  --project=${GCP_PROJECT_ID}

# Check index creation status
gcloud firestore indexes composite list --project=${GCP_PROJECT_ID}
```

### Step 3: Configure Firestore Security Rules

```bash
# Create firestore.rules
cat > deployment/firestore.rules <<'EOF'
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Deny all other access
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
EOF

# Deploy security rules
gcloud firestore deploy \
  --rules=deployment/firestore.rules \
  --project=${GCP_PROJECT_ID}
```

### Step 4: Verify Firestore Setup

```bash
# Test Firestore connection (requires Python SDK)
python3 << 'PYTHON_EOF'
from google.cloud import firestore

db = firestore.Client()
print("✅ Firestore connection successful!")

# Test write (will fail due to security rules, but confirms connection)
try:
    db.collection('test').document('test').set({'test': 'value'})
except Exception as e:
    print(f"⚠️ Expected error (security rules working): {type(e).__name__}")
PYTHON_EOF
```

---

## Cloud Storage Setup

### Step 1: Create Storage Bucket

```bash
export BUCKET_NAME="${GCP_PROJECT_ID}-static-knowledge"

# Create bucket with standard storage class
gsutil mb \
  -p ${GCP_PROJECT_ID} \
  -c STANDARD \
  -l ${GCP_REGION} \
  gs://${BUCKET_NAME}

# Verify bucket creation
gsutil ls -p ${GCP_PROJECT_ID}
```

### Step 2: Configure Bucket Permissions

```bash
# Grant service account read access
gsutil iam ch \
  serviceAccount:${SERVICE_ACCOUNT_EMAIL}:objectViewer \
  gs://${BUCKET_NAME}

# Verify permissions
gsutil iam get gs://${BUCKET_NAME}
```

### Step 3: Upload Static Knowledge Graph

```bash
# Create static graph data for Epic 1 (single factor)
mkdir -p src/data/static-graph

cat > src/data/static-graph/factors.json <<'EOF'
{
  "factors": {
    "data_quality": {
      "id": "data_quality",
      "name": "Data Quality",
      "category": "data_readiness",
      "description": "Quality, consistency, and reliability of organizational data",
      "scale": {
        "0": "No quality controls, data unreliable",
        "20": "Ad-hoc quality checks, many issues",
        "50": "Basic quality processes, some automation",
        "80": "Comprehensive quality framework, mostly automated",
        "100": "World-class data quality, continuous monitoring"
      },
      "dependencies": [],
      "typical_assessment_time_minutes": 10
    }
  }
}
EOF

# Upload to Cloud Storage
gsutil cp src/data/static-graph/factors.json gs://${BUCKET_NAME}/factors.json

# Verify upload
gsutil ls gs://${BUCKET_NAME}
```

### Step 4: Enable Versioning (Optional but Recommended)

```bash
# Enable object versioning for rollback capability
gsutil versioning set on gs://${BUCKET_NAME}

# Verify versioning
gsutil versioning get gs://${BUCKET_NAME}
```

---

## Firebase Authentication Setup

> **Note:** The setup script (`deployment/setup-infrastructure.sh`) automates Firebase CLI installation and project initialization. Manual steps are only required for enabling authentication providers.

### Automated Setup (via setup script)

The setup script automatically:
- Installs Firebase CLI (if npm is available)
- Creates `.firebaserc` with project configuration
- Creates `firebase.json` with Firestore rules configuration
- Creates `deployment/firestore.indexes.json` for index management

### Manual Steps Required

#### 1. Enable Google OAuth Provider

**This must be done manually in the Firebase Console:**

1. Go to: `https://console.firebase.google.com/project/${GCP_PROJECT_ID}/authentication/providers`
2. Click on **Google** provider
3. Toggle **Enable**
4. Set **Support email**: your-email@example.com
5. Click **Save**

**Why manual?** Firebase Authentication provider configuration requires interactive consent and email verification that cannot be automated via CLI.

#### 2. (Optional) Enable Additional Providers

If you want to support email/password authentication:
1. In the same Authentication → Sign-in method page
2. Click on **Email/Password**
3. Toggle **Enable**
4. Click **Save**

### Step 2: Get Firebase Configuration

```bash
# Get Firebase config (needed for frontend)
firebase apps:sdkconfig web

# Save output to a file
firebase apps:sdkconfig web > deployment/firebase-config.json
```

**Example output:**
```json
{
  "apiKey": "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "authDomain": "ai-pilot-assessment-prod.firebaseapp.com",
  "projectId": "ai-pilot-assessment-prod",
  "storageBucket": "ai-pilot-assessment-prod.appspot.com",
  "messagingSenderId": "123456789012",
  "appId": "1:123456789012:web:abcdef1234567890"
}
```

### Step 3: Configure Authorized Domains

```bash
# Add your Cloud Run domain to authorized domains (do this after Cloud Run deployment)
# Manual step in Firebase Console:
# Authentication → Settings → Authorized domains → Add domain
```

**For now, note that you'll need to:**
1. Deploy Cloud Run service first
2. Get the Cloud Run URL
3. Add that domain to Firebase authorized domains

---

## Vertex AI Configuration

### Step 1: Verify Vertex AI API is Enabled

```bash
# Check if Vertex AI API is enabled
gcloud services list --enabled --filter="name:aiplatform.googleapis.com" --project=${GCP_PROJECT_ID}

# Should show: aiplatform.googleapis.com
```

### Step 2: Test Vertex AI Access

```bash
# Test Vertex AI access with a simple API call
gcloud ai models list \
  --region=${VERTEX_AI_LOCATION} \
  --project=${GCP_PROJECT_ID}

# Should list available models (or show empty list if none deployed)
```

### Step 3: Verify Gemini Model Access

```bash
# Test Gemini model access (requires Python SDK)
python3 << 'PYTHON_EOF'
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Vertex AI
vertexai.init(project="${GCP_PROJECT_ID}", location="${VERTEX_AI_LOCATION}")

# Test model access
model = GenerativeModel("gemini-1.5-flash")
print("✅ Vertex AI Gemini model access successful!")

# Test simple generation
response = model.generate_content("Say hello")
print(f"Test response: {response.text}")
PYTHON_EOF
```

**Note:** Gemini models are available in specific regions. Use `us-central1` for best availability.

---

## Cloud Run Preparation

### Step 1: Configure Cloud Run Service Settings

```bash
export CLOUD_RUN_SERVICE_NAME="assessment-engine"
export CLOUD_RUN_REGION="us-central1"

# Note: Actual deployment happens later, but we prepare the configuration
```

### Step 2: Create Cloud Run Configuration File

```bash
cat > deployment/cloud-run-config.yaml <<EOF
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ${CLOUD_RUN_SERVICE_NAME}
  labels:
    app: assessment-engine
    environment: production
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/sessionAffinity: "true"
    spec:
      serviceAccountName: ${SERVICE_ACCOUNT_EMAIL}
      containerConcurrency: 10
      timeoutSeconds: 300
      containers:
      - image: gcr.io/${GCP_PROJECT_ID}/${CLOUD_RUN_SERVICE_NAME}:latest
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "${GCP_PROJECT_ID}"
        - name: FIRESTORE_DATABASE
          value: "(default)"
        - name: VERTEX_AI_LOCATION
          value: "${VERTEX_AI_LOCATION}"
        - name: VERTEX_AI_MODEL
          value: "${VERTEX_AI_MODEL}"
        - name: BUCKET_NAME
          value: "${BUCKET_NAME}"
        - name: SESSION_TIMEOUT_MINUTES
          value: "30"
EOF
```

### Step 3: Grant Cloud Run Permissions

```bash
# Allow unauthenticated access to Cloud Run (for public app)
# Note: Firebase Auth will handle user authentication at app level
gcloud run services add-iam-policy-binding ${CLOUD_RUN_SERVICE_NAME} \
  --region=${CLOUD_RUN_REGION} \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=${GCP_PROJECT_ID} \
  --quiet || echo "Service not yet deployed, will set this after deployment"
```

---

## Local Development Setup

### Step 1: Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Set Environment Variables for Local Development

```bash
# Create .env file for local development (DO NOT commit)
cat > .env <<EOF
# GCP Configuration
GOOGLE_CLOUD_PROJECT=${GCP_PROJECT_ID}
GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/deployment/keys/service-account-key.json

# Firestore
FIRESTORE_DATABASE=(default)

# Vertex AI
VERTEX_AI_LOCATION=${VERTEX_AI_LOCATION}
VERTEX_AI_MODEL=${VERTEX_AI_MODEL}

# Cloud Storage
BUCKET_NAME=${BUCKET_NAME}

# Streamlit
STREAMLIT_SERVER_PORT=8080
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
EOF

# Load environment variables
source .env
```

### Step 3: Test Local Development Environment

```bash
# Test Firestore connection
python3 -c "from google.cloud import firestore; db = firestore.Client(); print('✅ Firestore OK')"

# Test Cloud Storage connection
python3 -c "from google.cloud import storage; client = storage.Client(); print('✅ Storage OK')"

# Test Vertex AI connection
python3 -c "import vertexai; vertexai.init(); print('✅ Vertex AI OK')"
```

---

## Verification & Testing

### Complete Infrastructure Verification Script

```bash
# Create verification script
cat > deployment/verify-infrastructure.sh <<'EOF'
#!/bin/bash
set -e

echo "🔍 Verifying GCP Infrastructure Setup..."
echo ""

# Load environment variables
source .env

# 1. Verify GCP Project
echo "1️⃣ Checking GCP Project..."
gcloud projects describe ${GOOGLE_CLOUD_PROJECT} > /dev/null 2>&1
echo "   ✅ Project exists: ${GOOGLE_CLOUD_PROJECT}"

# 2. Verify APIs
echo "2️⃣ Checking Required APIs..."
REQUIRED_APIS=(
  "aiplatform.googleapis.com"
  "firestore.googleapis.com"
  "storage.googleapis.com"
  "run.googleapis.com"
  "identitytoolkit.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
  if gcloud services list --enabled --filter="name:${api}" --project=${GOOGLE_CLOUD_PROJECT} | grep -q ${api}; then
    echo "   ✅ ${api}"
  else
    echo "   ❌ ${api} NOT ENABLED"
    exit 1
  fi
done

# 3. Verify Service Account
echo "3️⃣ Checking Service Account..."
if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} --project=${GOOGLE_CLOUD_PROJECT} > /dev/null 2>&1; then
  echo "   ✅ Service account exists: ${SERVICE_ACCOUNT_EMAIL}"
else
  echo "   ❌ Service account not found"
  exit 1
fi

# 4. Verify Firestore
echo "4️⃣ Checking Firestore..."
if gcloud firestore databases describe --project=${GOOGLE_CLOUD_PROJECT} > /dev/null 2>&1; then
  echo "   ✅ Firestore database exists"
else
  echo "   ❌ Firestore database not found"
  exit 1
fi

# 5. Verify Cloud Storage Bucket
echo "5️⃣ Checking Cloud Storage..."
if gsutil ls gs://${BUCKET_NAME} > /dev/null 2>&1; then
  echo "   ✅ Bucket exists: ${BUCKET_NAME}"
  
  # Check if static graph exists
  if gsutil ls gs://${BUCKET_NAME}/factors.json > /dev/null 2>&1; then
    echo "   ✅ Static graph uploaded"
  else
    echo "   ⚠️  Static graph not found (upload factors.json)"
  fi
else
  echo "   ❌ Bucket not found"
  exit 1
fi

# 6. Verify Service Account Key (local dev)
echo "6️⃣ Checking Service Account Key..."
if [ -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
  echo "   ✅ Service account key exists"
else
  echo "   ⚠️  Service account key not found (needed for local dev)"
fi

# 7. Test Python SDK Connections
echo "7️⃣ Testing Python SDK Connections..."
python3 << PYTHON_EOF
try:
    from google.cloud import firestore
    db = firestore.Client()
    print("   ✅ Firestore SDK connection successful")
except Exception as e:
    print(f"   ❌ Firestore SDK error: {e}")
    exit(1)

try:
    from google.cloud import storage
    client = storage.Client()
    print("   ✅ Cloud Storage SDK connection successful")
except Exception as e:
    print(f"   ❌ Cloud Storage SDK error: {e}")
    exit(1)

try:
    import vertexai
    vertexai.init()
    print("   ✅ Vertex AI SDK connection successful")
except Exception as e:
    print(f"   ❌ Vertex AI SDK error: {e}")
    exit(1)
PYTHON_EOF

echo ""
echo "✅ All infrastructure checks passed!"
echo ""
echo "Next steps:"
echo "  1. Implement application code"
echo "  2. Build Docker container"
echo "  3. Deploy to Cloud Run"
EOF

chmod +x deployment/verify-infrastructure.sh

# Run verification
./deployment/verify-infrastructure.sh
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Permission denied" errors

```bash
# Verify you're authenticated
gcloud auth list

# Re-authenticate if needed
gcloud auth login

# Verify project is set
gcloud config get-value project
```

#### Issue 2: Firestore "already exists" error

```bash
# Check if Firestore already exists
gcloud firestore databases describe --project=${GCP_PROJECT_ID}

# If it exists in wrong location, you cannot change it
# You must create a new project
```

#### Issue 3: Service account key not working

```bash
# Verify key file exists and is valid JSON
cat deployment/keys/service-account-key.json | python3 -m json.tool

# Verify environment variable is set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Re-create key if corrupted
gcloud iam service-accounts keys create deployment/keys/service-account-key.json \
  --iam-account=${SERVICE_ACCOUNT_EMAIL} \
  --project=${GCP_PROJECT_ID}
```

#### Issue 4: Vertex AI quota errors

```bash
# Check quotas
gcloud compute project-info describe --project=${GCP_PROJECT_ID}

# Request quota increase in GCP Console:
# IAM & Admin → Quotas → Filter: "Vertex AI" → Request increase
```

#### Issue 5: Firebase Auth not working

```bash
# Verify Firebase project is linked
firebase projects:list

# Re-initialize if needed
firebase use ${GCP_PROJECT_ID}
```

---

## Security Checklist

Before going to production, verify:

- [ ] Service account has **minimum required permissions** only
- [ ] Firestore security rules are deployed and tested
- [ ] Service account keys are **NOT committed to git**
- [ ] `.env` and `deployment/keys/` are in `.gitignore`
- [ ] Cloud Storage bucket has proper IAM permissions
- [ ] Firebase authorized domains include only your domains
- [ ] Cloud Run service uses service account (not default compute SA)
- [ ] API keys (if any) are stored in Secret Manager, not env vars
- [ ] Billing alerts are configured
- [ ] Cloud Logging is enabled for audit trail

---

## Cost Monitoring Setup

```bash
# Create budget alert (replace YOUR_EMAIL with actual email)
gcloud billing budgets create \
  --billing-account=0X0X0X-0X0X0X-0X0X0X \
  --display-name="Assessment Engine Monthly Budget" \
  --budget-amount=50USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100 \
  --all-updates-rule-pubsub-topic=projects/${GCP_PROJECT_ID}/topics/budget-alerts \
  --notification-channels=YOUR_EMAIL
```

---

## Next Steps

After completing infrastructure setup:

1. ✅ Verify all checks pass: `./deployment/verify-infrastructure.sh`
2. 📝 Proceed to **Epic 1, Task 2: Static Knowledge Graph**
3. 🔧 Start implementing application code
4. 🐳 Build Docker container
5. 🚀 Deploy to Cloud Run

---

## Quick Reference Commands

```bash
# Activate environment
source .env
source venv/bin/activate

# Verify infrastructure
./deployment/verify-infrastructure.sh

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50 --project=${GCP_PROJECT_ID}

# Check costs
gcloud billing accounts list
gcloud billing projects describe ${GCP_PROJECT_ID}

# Update static graph
gsutil cp src/data/static-graph/factors.json gs://${BUCKET_NAME}/factors.json

# Test Firestore locally
python3 -c "from google.cloud import firestore; db = firestore.Client(); print(db.collection('test').limit(1).get())"
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-10-29  
**Status:** Ready for Epic 1 implementation
