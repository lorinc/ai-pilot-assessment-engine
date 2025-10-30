# Setup Script Improvements

## Summary
Updated `deployment/setup-infrastructure.sh` to be more robust and handle edge cases that were encountered during manual setup.

## Changes Made

### 1. Region Validation
- **Added**: Automatic validation to detect if `GCP_REGION` is a zone instead of a region
- **Why**: Firestore requires region-level locations (e.g., `europe-west1`), not zones (e.g., `europe-west1-b`)
- **Impact**: Prevents the "Invalid locationId" error by catching the issue before API calls

```bash
# Validates that GCP_REGION doesn't end with zone suffix (-a, -b, -c)
if [[ ${GCP_REGION} =~ -[a-z]$ ]]; then
    log_error "GCP_REGION appears to be a zone, not a region!"
    exit 1
fi
```

### 2. Improved Firestore Index Handling
- **Changed**: Better handling of "index not necessary" errors
- **Why**: Single-field indexes are automatic in Firestore; composite index creation fails with a specific message
- **Impact**: Script now correctly identifies when indexes aren't needed instead of showing warnings

### 3. Enhanced Bucket Operations Error Handling
- **Added**: Explicit error checking for bucket creation, permissions, and versioning
- **Why**: Operations may fail silently or may already be configured
- **Impact**: Better feedback and graceful handling of idempotent operations

### 4. Non-Blocking Firebase Setup
- **Changed**: Removed `prompt_continue` after Firebase Auth instructions
- **Why**: Firebase Auth can be configured later; shouldn't block infrastructure setup
- **Impact**: Script can complete without waiting for manual Firebase configuration

### 5. Fixed Firestore Rules Deployment
- **Changed**: Use Firebase CLI instead of non-existent `gcloud firestore deploy` command
- **Why**: The gcloud command doesn't exist; Firebase CLI is the correct tool
- **Impact**: Rules can now be deployed if Firebase CLI is installed

## Security Verification

All sensitive files are properly protected by `.gitignore`:

✅ **Protected Files:**
- `.env` - Root environment file with API keys
- `.env.local` - Local development configuration
- `deployment/.env` - GCP deployment configuration
- `deployment/keys/` - Service account keys directory
- `deployment/firebase-config.json` - Firebase web app config
- `.firebase/` - Firebase CLI cache
- `firebase-debug.log` - Firebase debug logs

✅ **Verification Command:**
```bash
git check-ignore -v .env .env.local deployment/.env deployment/keys/
```

## Testing

The script now handles these scenarios correctly:

1. ✅ Running with zone instead of region (fails early with clear error)
2. ✅ Re-running after partial completion (idempotent operations)
3. ✅ Missing Firebase CLI (warns but continues)
4. ✅ Bucket already exists (skips creation)
5. ✅ Permissions already set (handles gracefully)

## Next Steps

The setup script is now production-ready and can handle:
- Fresh installations
- Partial re-runs after failures
- Configuration validation
- Graceful degradation when optional tools are missing

To run the improved script:
```bash
./deployment/setup-infrastructure.sh
```
