#!/bin/bash
#
# Infrastructure Verification Script
# 
# Verifies that all GCP infrastructure components are properly configured
# Run this after setup-infrastructure.sh completes
#
# Usage: ./deployment/verify-infrastructure.sh
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

check_command() {
    if command -v $1 &> /dev/null; then
        log_success "$1 is installed"
        return 0
    else
        log_error "$1 is not installed"
        return 1
    fi
}

# Check if .env file exists
if [ ! -f "deployment/.env" ]; then
    log_error ".env file not found!"
    echo "Please create deployment/.env from deployment/.env.template"
    exit 1
fi

# Load environment variables
log_info "Loading configuration from deployment/.env..."
source deployment/.env

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Infrastructure Verification for AI Pilot Assessment Engine"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Project: ${GCP_PROJECT_ID}"
echo "Region: ${GCP_REGION}"
echo ""

# =============================================================================
# CHECK 1: Required CLI Tools
# =============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 1: Required CLI Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_command "gcloud"
check_command "gsutil"
check_command "python3"

if command -v firebase &> /dev/null; then
    log_success "firebase CLI is installed"
else
    log_warning "firebase CLI not installed (needed for Firebase Auth setup)"
fi

# =============================================================================
# CHECK 2: GCP Authentication
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 2: GCP Authentication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    log_success "Authenticated as: ${ACTIVE_ACCOUNT}"
else
    log_error "Not authenticated. Run: gcloud auth login"
fi

CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "${CURRENT_PROJECT}" = "${GCP_PROJECT_ID}" ]; then
    log_success "Current project: ${CURRENT_PROJECT}"
else
    log_error "Current project (${CURRENT_PROJECT}) doesn't match expected (${GCP_PROJECT_ID})"
    echo "Run: gcloud config set project ${GCP_PROJECT_ID}"
fi

# =============================================================================
# CHECK 3: GCP Project
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 3: GCP Project"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gcloud projects describe ${GCP_PROJECT_ID} &>/dev/null; then
    log_success "Project exists: ${GCP_PROJECT_ID}"
    
    # Check billing
    if gcloud billing projects describe ${GCP_PROJECT_ID} --format="value(billingEnabled)" 2>/dev/null | grep -q "True"; then
        log_success "Billing is enabled"
    else
        log_error "Billing is not enabled. Link a billing account."
    fi
else
    log_error "Project not found: ${GCP_PROJECT_ID}"
fi

# =============================================================================
# CHECK 4: Required APIs
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 4: Required APIs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

REQUIRED_APIS=(
    "aiplatform.googleapis.com:Vertex AI"
    "firestore.googleapis.com:Firestore"
    "storage.googleapis.com:Cloud Storage"
    "run.googleapis.com:Cloud Run"
    "cloudbuild.googleapis.com:Cloud Build"
    "containerregistry.googleapis.com:Container Registry"
    "identitytoolkit.googleapis.com:Identity Toolkit"
    "firebase.googleapis.com:Firebase"
)

for api_info in "${REQUIRED_APIS[@]}"; do
    IFS=':' read -r api name <<< "$api_info"
    if gcloud services list --enabled --filter="name:${api}" --project=${GCP_PROJECT_ID} 2>/dev/null | grep -q ${api}; then
        log_success "${name} (${api})"
    else
        log_error "${name} (${api}) is not enabled"
    fi
done

# =============================================================================
# CHECK 5: Service Account
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 5: Service Account"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} --project=${GCP_PROJECT_ID} &>/dev/null; then
    log_success "Service account exists: ${SERVICE_ACCOUNT_EMAIL}"
    
    # Check IAM roles
    REQUIRED_ROLES=(
        "roles/aiplatform.user"
        "roles/datastore.user"
        "roles/storage.objectViewer"
        "roles/run.invoker"
        "roles/logging.logWriter"
    )
    
    IAM_POLICY=$(gcloud projects get-iam-policy ${GCP_PROJECT_ID} --flatten="bindings[].members" --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT_EMAIL}" --format="value(bindings.role)")
    
    for role in "${REQUIRED_ROLES[@]}"; do
        if echo "${IAM_POLICY}" | grep -q "${role}"; then
            log_success "Role granted: ${role}"
        else
            log_error "Role missing: ${role}"
        fi
    done
else
    log_error "Service account not found: ${SERVICE_ACCOUNT_EMAIL}"
fi

# Check service account key for local development
if [ -f "deployment/keys/service-account-key.json" ]; then
    log_success "Service account key exists for local development"
    
    # Verify it's valid JSON
    if python3 -m json.tool deployment/keys/service-account-key.json &>/dev/null; then
        log_success "Service account key is valid JSON"
    else
        log_error "Service account key is corrupted (invalid JSON)"
    fi
else
    log_warning "Service account key not found (needed for local development)"
fi

# =============================================================================
# CHECK 6: Firestore Database
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 6: Firestore Database"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gcloud firestore databases describe --project=${GCP_PROJECT_ID} &>/dev/null; then
    log_success "Firestore database exists"
    
    DB_LOCATION=$(gcloud firestore databases describe --project=${GCP_PROJECT_ID} --format="value(locationId)")
    if [ "${DB_LOCATION}" = "${GCP_REGION}" ]; then
        log_success "Database location matches: ${DB_LOCATION}"
    else
        log_warning "Database location (${DB_LOCATION}) differs from configured region (${GCP_REGION})"
    fi
    
    # Check indexes
    if gcloud firestore indexes composite list --project=${GCP_PROJECT_ID} 2>/dev/null | grep -q "journal"; then
        log_success "Firestore indexes configured"
    else
        log_warning "Firestore indexes may not be configured"
    fi
else
    log_error "Firestore database not found"
fi

# Check security rules
if [ -f "deployment/firestore.rules" ]; then
    log_success "Firestore security rules file exists"
else
    log_warning "Firestore security rules file not found"
fi

# =============================================================================
# CHECK 7: Cloud Storage Bucket
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 7: Cloud Storage Bucket"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if gsutil ls gs://${BUCKET_NAME} &>/dev/null; then
    log_success "Bucket exists: gs://${BUCKET_NAME}"
    
    # Check versioning
    if gsutil versioning get gs://${BUCKET_NAME} | grep -q "Enabled"; then
        log_success "Object versioning is enabled"
    else
        log_warning "Object versioning is not enabled"
    fi
    
    # Check for static graph
    if gsutil ls gs://${BUCKET_NAME}/factors.json &>/dev/null; then
        log_success "Static graph uploaded: factors.json"
    else
        log_warning "Static graph not found (factors.json)"
        echo "Upload with: gsutil cp src/data/static-graph/factors.json gs://${BUCKET_NAME}/"
    fi
    
    # Check IAM permissions
    BUCKET_IAM=$(gsutil iam get gs://${BUCKET_NAME})
    if echo "${BUCKET_IAM}" | grep -q "${SERVICE_ACCOUNT_EMAIL}"; then
        log_success "Service account has bucket access"
    else
        log_error "Service account doesn't have bucket access"
    fi
else
    log_error "Bucket not found: gs://${BUCKET_NAME}"
fi

# =============================================================================
# CHECK 8: Python SDK Connections
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 8: Python SDK Connections"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Set credentials for testing
if [ -f "deployment/keys/service-account-key.json" ]; then
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/deployment/keys/service-account-key.json"
    export GOOGLE_CLOUD_PROJECT="${GCP_PROJECT_ID}"
fi

# Test Firestore SDK
python3 << 'PYTHON_EOF' 2>/dev/null
try:
    from google.cloud import firestore
    db = firestore.Client()
    print("✅ Firestore SDK connection successful")
except ImportError:
    print("⚠️  google-cloud-firestore not installed (pip install google-cloud-firestore)")
except Exception as e:
    print(f"❌ Firestore SDK error: {type(e).__name__}: {e}")
PYTHON_EOF

# Test Cloud Storage SDK
python3 << 'PYTHON_EOF' 2>/dev/null
try:
    from google.cloud import storage
    client = storage.Client()
    print("✅ Cloud Storage SDK connection successful")
except ImportError:
    print("⚠️  google-cloud-storage not installed (pip install google-cloud-storage)")
except Exception as e:
    print(f"❌ Cloud Storage SDK error: {type(e).__name__}: {e}")
PYTHON_EOF

# Test Vertex AI SDK
python3 << PYTHON_EOF 2>/dev/null
try:
    import vertexai
    vertexai.init(project="${GCP_PROJECT_ID}", location="${VERTEX_AI_LOCATION}")
    print("✅ Vertex AI SDK connection successful")
except ImportError:
    print("⚠️  google-cloud-aiplatform not installed (pip install google-cloud-aiplatform)")
except Exception as e:
    print(f"❌ Vertex AI SDK error: {type(e).__name__}: {e}")
PYTHON_EOF

# =============================================================================
# CHECK 9: Local Development Environment
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 9: Local Development Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".env.local" ]; then
    log_success "Local environment file exists (.env.local)"
else
    log_warning "Local environment file not found (.env.local)"
fi

if [ -f "requirements.txt" ]; then
    log_success "requirements.txt exists"
else
    log_warning "requirements.txt not found"
fi

if [ -d "venv" ]; then
    log_success "Virtual environment exists (venv/)"
else
    log_warning "Virtual environment not found (create with: python3 -m venv venv)"
fi

# =============================================================================
# CHECK 10: Firebase Configuration
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "CHECK 10: Firebase Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "deployment/firebase-config.json" ]; then
    log_success "Firebase config exists"
else
    log_warning "Firebase config not found (run: firebase apps:sdkconfig web > deployment/firebase-config.json)"
fi

if [ -f ".firebaserc" ]; then
    log_success "Firebase project configuration exists"
else
    log_warning "Firebase not initialized (run: firebase init)"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Verification Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ Passed: ${PASSED}${NC}"
echo -e "${YELLOW}⚠️  Warnings: ${WARNINGS}${NC}"
echo -e "${RED}❌ Failed: ${FAILED}${NC}"
echo ""

if [ ${FAILED} -eq 0 ]; then
    if [ ${WARNINGS} -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}🎉 All checks passed! Infrastructure is ready.${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Set up local development environment:"
        echo "     source .env.local"
        echo "     source venv/bin/activate"
        echo "     pip install -r requirements.txt"
        echo "  2. Proceed to Epic 1, Task 2: Static Knowledge Graph implementation"
        exit 0
    else
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}⚠️  Infrastructure is mostly ready, but has warnings.${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "Review warnings above and address if needed."
        echo "You can proceed with development, but some features may not work."
        exit 0
    fi
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ Infrastructure verification failed.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Please fix the errors above before proceeding."
    echo "See docs/DEPLOYMENT_GUIDE.md for detailed troubleshooting."
    exit 1
fi
