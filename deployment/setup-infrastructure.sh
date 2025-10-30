#!/bin/bash
#
# Infrastructure Setup Script for AI Pilot Assessment Engine - Epic 1
# 
# This script automates the GCP infrastructure setup process.
# Run this after filling in deployment/.env with your configuration.
#
# Usage: ./deployment/setup-infrastructure.sh
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

prompt_continue() {
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "Aborted by user"
        exit 1
    fi
}

# Check if .env file exists
if [ ! -f "deployment/.env" ]; then
    log_error ".env file not found!"
    echo "Please copy deployment/.env.template to deployment/.env and fill in your values"
    exit 1
fi

# Load environment variables
log_info "Loading configuration from deployment/.env..."
source deployment/.env
log_success "Configuration loaded"

# Validate region format (should not end with a zone suffix like -a, -b, -c)
if [[ ${GCP_REGION} =~ -[a-z]$ ]]; then
    log_error "GCP_REGION appears to be a zone (${GCP_REGION}), not a region!"
    log_error "Firestore requires a region-level location (e.g., 'europe-west1', not 'europe-west1-b')"
    log_error "Please update GCP_REGION in deployment/.env and re-run this script."
    exit 1
fi

# Display configuration
echo ""
log_info "Configuration Summary:"
echo "  Project ID: ${GCP_PROJECT_ID}"
echo "  Region: ${GCP_REGION}"
echo "  Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo "  Bucket: ${BUCKET_NAME}"
echo ""
log_warning "This script will create resources in GCP that may incur costs."
prompt_continue

# =============================================================================
# STEP 1: GCP Project Setup
# =============================================================================
echo ""
log_info "STEP 1: Setting up GCP Project..."

# Check if project exists
if gcloud projects describe ${GCP_PROJECT_ID} &>/dev/null; then
    log_success "Project ${GCP_PROJECT_ID} already exists"
else
    log_info "Creating project ${GCP_PROJECT_ID}..."
    gcloud projects create ${GCP_PROJECT_ID} \
        --name="AI Pilot Assessment Engine" \
        --set-as-default
    log_success "Project created"
    
    log_warning "You need to link a billing account to this project."
    echo "Run: gcloud billing accounts list"
    echo "Then: gcloud billing projects link ${GCP_PROJECT_ID} --billing-account=BILLING_ACCOUNT_ID"
    prompt_continue
fi

# Set as default project
gcloud config set project ${GCP_PROJECT_ID}
log_success "Project set as default"

# =============================================================================
# STEP 2: Enable Required APIs
# =============================================================================
echo ""
log_info "STEP 2: Enabling required APIs..."

APIS=(
    "aiplatform.googleapis.com"
    "firestore.googleapis.com"
    "storage.googleapis.com"
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "containerregistry.googleapis.com"
    "identitytoolkit.googleapis.com"
    "firebase.googleapis.com"
)

for api in "${APIS[@]}"; do
    log_info "Enabling ${api}..."
    gcloud services enable ${api} --project=${GCP_PROJECT_ID}
done

log_success "All APIs enabled"

# Wait for APIs to propagate
log_info "Waiting 60 seconds for APIs to propagate..."
sleep 2
log_info "Please listen to this elevator music, while you're waiting..."
sleep 10
log_info "Pumm-purumm-pum, pamm-pamm-parapm-pam, pumm-param-pum, pumm..."
sleep 48

# =============================================================================
# STEP 3: Create Service Account
# =============================================================================
echo ""
log_info "STEP 3: Creating service account..."

if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} --project=${GCP_PROJECT_ID} &>/dev/null; then
    log_success "Service account already exists"
else
    gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
        --display-name="Assessment Engine Service Account" \
        --description="Service account for AI Pilot Assessment Engine Cloud Run service" \
        --project=${GCP_PROJECT_ID}
    log_success "Service account created"
fi

# Grant permissions
log_info "Granting IAM permissions..."

ROLES=(
    "roles/aiplatform.user"
    "roles/datastore.user"
    "roles/storage.objectViewer"
    "roles/run.invoker"
    "roles/logging.logWriter"
)

for role in "${ROLES[@]}"; do
    log_info "Granting ${role}..."
    gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="${role}" \
        --quiet
done

log_success "IAM permissions granted"

# Create service account key for local development
log_info "Creating service account key for local development..."
mkdir -p deployment/keys

if [ -f "deployment/keys/service-account-key.json" ]; then
    log_warning "Service account key already exists. Skipping creation."
    log_warning "Delete deployment/keys/service-account-key.json if you want to regenerate."
else
    gcloud iam service-accounts keys create deployment/keys/service-account-key.json \
        --iam-account=${SERVICE_ACCOUNT_EMAIL} \
        --project=${GCP_PROJECT_ID}
    log_success "Service account key created"
fi

# =============================================================================
# STEP 4: Create Firestore Database
# =============================================================================
echo ""
log_info "STEP 4: Creating Firestore database..."

if gcloud firestore databases describe --project=${GCP_PROJECT_ID} &>/dev/null; then
    log_success "Firestore database already exists"
else
    log_info "Creating Firestore database in ${GCP_REGION}..."
    log_warning "This cannot be changed later. Make sure ${GCP_REGION} is correct."
    prompt_continue
    
    gcloud firestore databases create \
        --location=${GCP_REGION} \
        --project=${GCP_PROJECT_ID}
    log_success "Firestore database created"
    
    # Wait for database to be ready
    log_info "Waiting 30 seconds for Firestore to be ready..."
    sleep 30
fi

# Create Firestore indexes (optional - single field indexes are automatic)
log_info "Checking Firestore indexes..."
if gcloud firestore indexes composite create \
    --collection-group=journal \
    --query-scope=COLLECTION \
    --field-config field-path=timestamp,order=descending \
    --project=${GCP_PROJECT_ID} \
    --quiet 2>&1 | grep -q "not necessary"; then
    log_success "Firestore indexes not needed (single field indexes are automatic)"
else
    log_success "Firestore indexes configured"
fi

# Deploy security rules
log_info "Deploying Firestore security rules..."
if [ -f "deployment/firestore.rules" ]; then
    # Use Firebase CLI to deploy rules (gcloud doesn't support this directly)
    if command -v firebase &> /dev/null; then
        firebase deploy --only firestore:rules --project=${GCP_PROJECT_ID}
        log_success "Security rules deployed"
    else
        log_warning "Firebase CLI not installed. Skipping rules deployment."
        log_warning "Install with: npm install -g firebase-tools"
        log_warning "Then run: firebase deploy --only firestore:rules --project=${GCP_PROJECT_ID}"
    fi
else
    log_warning "firestore.rules not found. You'll need to deploy security rules manually."
fi

# =============================================================================
# STEP 5: Create Cloud Storage Bucket
# =============================================================================
echo ""
log_info "STEP 5: Creating Cloud Storage bucket..."

if gsutil ls gs://${BUCKET_NAME} &>/dev/null; then
    log_success "Bucket already exists"
else
    log_info "Creating bucket gs://${BUCKET_NAME}..."
    if gsutil mb \
        -p ${GCP_PROJECT_ID} \
        -c STANDARD \
        -l ${GCP_REGION} \
        gs://${BUCKET_NAME}; then
        log_success "Bucket created"
    else
        log_error "Failed to create bucket. Check if the name is globally unique."
        exit 1
    fi
fi

# Grant service account access
log_info "Granting service account access to bucket..."
if gsutil iam ch \
    serviceAccount:${SERVICE_ACCOUNT_EMAIL}:objectViewer \
    gs://${BUCKET_NAME} 2>/dev/null; then
    log_success "Bucket permissions configured"
else
    log_warning "Failed to set bucket permissions (may already be set)"
fi

# Enable versioning
log_info "Enabling object versioning..."
if gsutil versioning set on gs://${BUCKET_NAME} 2>/dev/null; then
    log_success "Versioning enabled"
else
    log_warning "Failed to enable versioning (may already be enabled)"
fi

# Upload static graph if it exists
if [ -f "src/data/static-graph/factors.json" ]; then
    log_info "Uploading static knowledge graph..."
    gsutil cp src/data/static-graph/factors.json gs://${BUCKET_NAME}/factors.json
    log_success "Static graph uploaded"
else
    log_warning "src/data/static-graph/factors.json not found. You'll need to upload it manually."
fi

# =============================================================================
# STEP 6: Firebase Authentication Setup
# =============================================================================
echo ""
log_info "STEP 6: Firebase Authentication setup..."
log_warning "Firebase Auth requires manual setup in the Firebase Console."
echo ""
echo "Please complete these steps manually:"
echo "  1. Go to https://console.firebase.google.com/"
echo "  2. Select project: ${GCP_PROJECT_ID}"
echo "  3. Navigate to Authentication → Sign-in method"
echo "  4. Enable Google provider"
echo "  5. Set support email and save"
echo ""
log_info "After completing Firebase setup, run: firebase apps:sdkconfig web > deployment/firebase-config.json"
echo ""
log_info "You can complete Firebase setup later. Continuing with infrastructure setup..."

# =============================================================================
# STEP 7: Verify Setup
# =============================================================================
echo ""
log_info "STEP 7: Verifying infrastructure setup..."

# Check project
if gcloud projects describe ${GCP_PROJECT_ID} &>/dev/null; then
    log_success "Project verified"
else
    log_error "Project verification failed"
    exit 1
fi

# Check APIs
for api in "${APIS[@]}"; do
    if gcloud services list --enabled --filter="name:${api}" --project=${GCP_PROJECT_ID} | grep -q ${api}; then
        log_success "${api} enabled"
    else
        log_error "${api} not enabled"
        exit 1
    fi
done

# Check service account
if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} --project=${GCP_PROJECT_ID} &>/dev/null; then
    log_success "Service account verified"
else
    log_error "Service account verification failed"
    exit 1
fi

# Check Firestore
if gcloud firestore databases describe --project=${GCP_PROJECT_ID} &>/dev/null; then
    log_success "Firestore verified"
else
    log_error "Firestore verification failed"
    exit 1
fi

# Check bucket
if gsutil ls gs://${BUCKET_NAME} &>/dev/null; then
    log_success "Cloud Storage bucket verified"
else
    log_error "Bucket verification failed"
    exit 1
fi

# =============================================================================
# STEP 8: Generate Local Development Configuration
# =============================================================================
echo ""
log_info "STEP 8: Generating local development configuration..."

cat > .env.local <<EOF
# Auto-generated by setup-infrastructure.sh
# DO NOT COMMIT THIS FILE

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

log_success "Local development configuration created: .env.local"

# =============================================================================
# COMPLETION
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_success "Infrastructure setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Summary:"
echo "  ✅ GCP Project: ${GCP_PROJECT_ID}"
echo "  ✅ Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo "  ✅ Firestore Database: Created in ${GCP_REGION}"
echo "  ✅ Cloud Storage Bucket: gs://${BUCKET_NAME}"
echo "  ✅ APIs: All enabled"
echo ""
echo "Next steps:"
echo "  1. Complete Firebase Auth setup (see manual steps above)"
echo "  2. Run verification: ./deployment/verify-infrastructure.sh"
echo "  3. Set up local development environment:"
echo "     source .env.local"
echo "     python3 -m venv venv"
echo "     source venv/bin/activate"
echo "     pip install -r requirements.txt"
echo "  4. Proceed to Epic 1, Task 2: Static Knowledge Graph implementation"
echo ""
echo "Documentation: docs/DEPLOYMENT_GUIDE.md"
echo ""
