# Infrastructure Setup and Script Improvements

**Date:** 2025-10-30  
**Type:** Infrastructure, DevOps  
**Status:** Completed

## Summary

Successfully set up GCP infrastructure for the AI Pilot Assessment Engine and improved the deployment script to handle edge cases and validation.

## Infrastructure Created

### GCP Resources
- **Project:** `ai-assessment-engine-476709`
- **Region:** `europe-west1` (Belgium)
- **Firestore Database:** Created in `europe-west1`
- **Cloud Storage Bucket:** `gs://ai-assessment-engine-476709-static-knowledge`
  - Versioning enabled
  - Service account permissions configured
- **Service Account:** `assessment-engine-sa@ai-assessment-engine-476709.iam.gserviceaccount.com`
  - IAM roles: Vertex AI, Firestore, Storage, Cloud Run, Logging
  - Service account key created for local development

### APIs Enabled
- Vertex AI (aiplatform.googleapis.com)
- Firestore (firestore.googleapis.com)
- Cloud Storage (storage.googleapis.com)
- Cloud Run (run.googleapis.com)
- Cloud Build (cloudbuild.googleapis.com)
- Container Registry (containerregistry.googleapis.com)
- Identity Toolkit (identitytoolkit.googleapis.com)
- Firebase (firebase.googleapis.com)

### Local Configuration
- `.env.local` generated with credentials
- Service account key stored in `deployment/keys/`

## Setup Script Improvements

### Changes to `deployment/setup-infrastructure.sh`

#### 1. Region Validation
**Added:** Automatic validation to detect if `GCP_REGION` is a zone instead of a region

```bash
if [[ ${GCP_REGION} =~ -[a-z]$ ]]; then
    log_error "GCP_REGION appears to be a zone, not a region!"
    exit 1
fi
```

**Why:** Firestore requires region-level locations (e.g., `europe-west1`), not zones (e.g., `europe-west1-b`)  
**Impact:** Prevents "Invalid locationId" error by catching the issue before API calls

#### 2. Improved Firestore Index Handling
**Changed:** Better handling of "index not necessary" errors

**Why:** Single-field indexes are automatic in Firestore; composite index creation fails with a specific message  
**Impact:** Script now correctly identifies when indexes aren't needed instead of showing warnings

#### 3. Enhanced Bucket Operations Error Handling
**Added:** Explicit error checking for bucket creation, permissions, and versioning

**Why:** Operations may fail silently or may already be configured  
**Impact:** Better feedback and graceful handling of idempotent operations

#### 4. Non-Blocking Firebase Setup
**Changed:** Removed `prompt_continue` after Firebase Auth instructions

**Why:** Firebase Auth can be configured later; shouldn't block infrastructure setup  
**Impact:** Script can complete without waiting for manual Firebase configuration

#### 5. Fixed Firestore Rules Deployment
**Changed:** Use Firebase CLI instead of non-existent `gcloud firestore deploy` command

**Why:** The gcloud command doesn't exist; Firebase CLI is the correct tool  
**Impact:** Rules can now be deployed if Firebase CLI is installed

## Security Verification

All sensitive files are properly protected by `.gitignore`:

- ✅ `.env` - Root environment file with API keys
- ✅ `.env.local` - Local development configuration
- ✅ `deployment/.env` - GCP deployment configuration
- ✅ `deployment/keys/` - Service account keys directory
- ✅ `deployment/firebase-config.json` - Firebase web app config
- ✅ `.firebase/` - Firebase CLI cache
- ✅ `firebase-debug.log` - Firebase debug logs

**Verification:**
```bash
git check-ignore -v .env .env.local deployment/.env deployment/keys/
```

## Issues Resolved

1. **Region Configuration Error:** Fixed `GCP_REGION` from `europe-west1-b` (zone) to `europe-west1` (region)
2. **Firestore Rules Deployment:** Updated to use Firebase CLI instead of non-existent gcloud command
3. **Manual Bucket Creation:** Script now handles bucket creation, permissions, and versioning automatically

## Testing

The script now handles these scenarios correctly:

1. ✅ Running with zone instead of region (fails early with clear error)
2. ✅ Re-running after partial completion (idempotent operations)
3. ✅ Missing Firebase CLI (warns but continues)
4. ✅ Bucket already exists (skips creation)
5. ✅ Permissions already set (handles gracefully)

## Documentation Updates

- Created `SETUP_IMPROVEMENTS.md` with detailed change documentation
- Updated `deployment/README.md` troubleshooting section:
  - Added "Invalid locationId error" troubleshooting
  - Added "Firestore deploy error" troubleshooting

## Next Steps

1. **Deploy Firestore Security Rules** (optional, requires Firebase CLI):
   ```bash
   npm install -g firebase-tools
   firebase deploy --only firestore:rules --project=ai-assessment-engine-476709
   ```

2. **Set up Firebase Authentication** (manual):
   - Go to https://console.firebase.google.com/
   - Select project: `ai-assessment-engine-476709`
   - Enable Google authentication provider

3. **Start Local Development**:
   ```bash
   source .env.local
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Files Modified

- `deployment/setup-infrastructure.sh` - Added validation and improved error handling
- `deployment/README.md` - Added troubleshooting entries
- `.gitignore` - Verified all sensitive files are protected (no changes needed)

## Files Created

- `SETUP_IMPROVEMENTS.md` - Detailed documentation of script improvements
- `.env.local` - Local development configuration
- `deployment/keys/service-account-key.json` - Service account key for local development

## Status

✅ **Infrastructure setup complete and ready for development**

The setup script is now production-ready and can handle fresh installations, partial re-runs after failures, configuration validation, and graceful degradation when optional tools are missing.
