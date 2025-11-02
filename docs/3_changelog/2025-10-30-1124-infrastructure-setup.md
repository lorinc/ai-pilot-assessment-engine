# 2025-10-30: Infrastructure Setup & Deployment Automation

**Date:** 2025-10-30  
**Type:** Infrastructure, DevOps, Automation  
**Status:** Completed  
**Impact:** Complete GCP infrastructure setup + automated deployment scripts

## Summary

Completed three major milestones:

1. **Infrastructure Setup (11:24):** Successfully set up GCP infrastructure for the AI Pilot Assessment Engine
2. **Setup Script Improvements (11:21):** Improved deployment script to handle edge cases and validation
3. **Firebase Automation (12:51):** Automated Firebase CLI installation and project initialization

**Result:** Reduced manual setup steps from 10+ to just 2, with robust error handling and idempotent operations.

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

1. `deployment/setup-infrastructure.sh` - Added validation, error handling, and Firebase automation
2. `deployment/README.md` - Added troubleshooting entries
3. `docs/DEPLOYMENT_GUIDE.md` - Updated Firebase Authentication Setup section
4. `.gitignore` - Verified all sensitive files are protected + clarified firebase.json should be committed

## Files Created

1. `.env.local` - Local development configuration
2. `deployment/keys/service-account-key.json` - Service account key for local development
3. `.firebaserc` - Firebase project configuration (auto-generated)
4. `firebase.json` - Firebase features configuration (auto-generated)
5. `deployment/firestore.indexes.json` - Firestore indexes (auto-generated)

---

## Part 2: Setup Script Improvements (11:21)

### Changes to `deployment/setup-infrastructure.sh`

#### Region Validation
**Added:** Automatic validation to detect if `GCP_REGION` is a zone instead of a region

```bash
if [[ ${GCP_REGION} =~ -[a-z]$ ]]; then
    log_error "GCP_REGION appears to be a zone, not a region!"
    exit 1
fi
```

**Why:** Firestore requires region-level locations (e.g., `europe-west1`), not zones (e.g., `europe-west1-b`)  
**Impact:** Prevents "Invalid locationId" error by catching the issue before API calls

#### Improved Firestore Index Handling
**Changed:** Better handling of "index not necessary" errors

**Why:** Single-field indexes are automatic in Firestore; composite index creation fails with a specific message  
**Impact:** Script now correctly identifies when indexes aren't needed instead of showing warnings

#### Enhanced Bucket Operations Error Handling
**Added:** Explicit error checking for bucket creation, permissions, and versioning

**Why:** Operations may fail silently or may already be configured  
**Impact:** Better feedback and graceful handling of idempotent operations

#### Non-Blocking Firebase Setup
**Changed:** Removed `prompt_continue` after Firebase Auth instructions

**Why:** Firebase Auth can be configured later; shouldn't block infrastructure setup  
**Impact:** Script can complete without waiting for manual Firebase configuration

#### Fixed Firestore Rules Deployment
**Changed:** Use Firebase CLI instead of non-existent `gcloud firestore deploy` command

**Why:** The gcloud command doesn't exist; Firebase CLI is the correct tool  
**Impact:** Rules can now be deployed if Firebase CLI is installed

---

## Part 3: Firebase Setup Automation (12:51)

### Problem Solved

The initial Firebase setup was entirely manual and required 10+ steps. Now automated to just 2 manual steps.

### Automated in Setup Script

The `deployment/setup-infrastructure.sh` now automatically:

1. **Checks for Firebase CLI**
   - Detects if already installed
   - Installs via npm if available
   - Provides clear instructions if npm is missing

2. **Creates Firebase Configuration Files**
   - `.firebaserc` - Project selection
   - `firebase.json` - Firestore rules and indexes configuration
   - `deployment/firestore.indexes.json` - Empty indexes file

3. **Provides Clear Instructions**
   - Direct URL to Firebase Console authentication page
   - Step-by-step manual instructions for OAuth enablement
   - Explanation of why manual steps are required

### Manual Steps (Cannot be Automated)

Only 2 manual steps remain:

1. **Enable Google OAuth Provider** (requires interactive consent)
   - URL: `https://console.firebase.google.com/project/${GCP_PROJECT_ID}/authentication/providers`
   - Click Google → Enable → Set support email → Save

2. **(Optional) Get Firebase Web Config** (for frontend integration)
   - Run: `firebase apps:sdkconfig web > deployment/firebase-config.json`

### Node.js Version Requirement

Firebase CLI v14.22.0+ requires Node.js v20+ or v22+. The deployment guide now includes:

**Option A: NodeSource Repository (Ubuntu/Debian)**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Option B: nvm (Recommended for multiple Node versions)**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

### Firebase Configuration Files Created

**`.firebaserc`** - Project selection
```json
{
  "projects": {
    "default": "ai-assessment-engine-476709"
  }
}
```

**`firebase.json`** - Features configuration
```json
{
  "firestore": {
    "rules": "deployment/firestore.rules",
    "indexes": "deployment/firestore.indexes.json"
  }
}
```

**`deployment/firestore.indexes.json`** - Index definitions
```json
{
  "indexes": [],
  "fieldOverrides": []
}
```

---

## Benefits

1. **Reduced Manual Steps**: From 10+ to 2
2. **Faster Setup**: ~15 minutes saved per deployment
3. **Fewer Errors**: Automated file creation eliminates typos
4. **Better Documentation**: Clear separation of automated vs manual steps
5. **Idempotent**: Script can be re-run safely
6. **Robust Error Handling**: Validates configuration before API calls
7. **Graceful Degradation**: Continues when optional tools are missing

---

## Testing

The script now handles these scenarios correctly:

1. ✅ Running with zone instead of region (fails early with clear error)
2. ✅ Re-running after partial completion (idempotent operations)
3. ✅ Missing Firebase CLI (warns but continues)
4. ✅ Bucket already exists (skips creation)
5. ✅ Permissions already set (handles gracefully)
6. ✅ Detects existing Firebase CLI installation
7. ✅ Installs Firebase CLI when npm is available
8. ✅ Creates all configuration files correctly
9. ✅ Provides clear manual instructions

---

## Status

✅ **Infrastructure setup complete and ready for development**

The setup script is now production-ready and can handle fresh installations, partial re-runs after failures, configuration validation, and graceful degradation when optional tools are missing.
