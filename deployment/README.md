# Deployment Directory

This directory contains all deployment-related configuration, scripts, and credentials for the AI Pilot Assessment Engine.

## Contents

### Configuration Files

- **`.env.template`** - Template for environment variables. Copy to `.env` and fill in your values.
- **`.env`** - Your actual environment configuration (NOT committed to git)
- **`firestore.rules`** - Firestore security rules
- **`firestore.indexes.json`** - Firestore composite indexes (auto-generated)
- **`cloud-run-config.yaml`** - Cloud Run service configuration (auto-generated)
- **`firebase-config.json`** - Firebase web app configuration (NOT committed to git)

### Scripts

- **`setup-infrastructure.sh`** - Automated infrastructure setup script
- **`verify-infrastructure.sh`** - Infrastructure verification script

### Directories

- **`keys/`** - Service account keys for local development (NOT committed to git)

## Quick Start

### 1. Initial Setup

```bash
# Copy environment template
cp deployment/.env.template deployment/.env

# Edit .env with your values
nano deployment/.env  # or use your preferred editor

# Run infrastructure setup
./deployment/setup-infrastructure.sh

# Verify everything is configured correctly
./deployment/verify-infrastructure.sh
```

### 2. Local Development

```bash
# Load environment variables
source .env.local

# Activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application locally
streamlit run streamlit_app.py
```

### 3. Deploy to Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/assessment-engine

# Deploy to Cloud Run
gcloud run deploy assessment-engine \
  --image gcr.io/${GCP_PROJECT_ID}/assessment-engine \
  --platform managed \
  --region ${GCP_REGION} \
  --service-account ${SERVICE_ACCOUNT_EMAIL} \
  --allow-unauthenticated
```

## Security Notes

⚠️ **NEVER commit these files to git:**
- `deployment/.env`
- `deployment/keys/`
- `deployment/firebase-config.json`
- `.env.local`

These files contain sensitive credentials and are already in `.gitignore`.

## Troubleshooting

If verification fails, see the detailed troubleshooting section in:
- `docs/DEPLOYMENT_GUIDE.md`

Common issues:
1. **Permission denied** - Run `gcloud auth login`
2. **Billing not enabled** - Link billing account in GCP Console
3. **API not enabled** - Re-run `setup-infrastructure.sh`
4. **Service account key invalid** - Delete and regenerate key

## File Permissions

The setup script automatically sets execute permissions on shell scripts. If needed, run:

```bash
chmod +x deployment/*.sh
```

## Cost Monitoring

Monitor your GCP costs:
```bash
# View current month costs
gcloud billing accounts list

# Check project billing
gcloud billing projects describe ${GCP_PROJECT_ID}
```

Set up budget alerts in GCP Console:
- Billing → Budgets & alerts → Create budget

## Support

For detailed documentation, see:
- `docs/DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `docs/VERTICAL_EPICS.md` - Epic 1 implementation details
