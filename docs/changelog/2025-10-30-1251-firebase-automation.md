# Firebase Setup Automation

**Date:** 2025-10-30  
**Type:** DevOps, Automation  
**Status:** Completed

## Summary

Automated Firebase CLI installation and project initialization in the setup script, reducing manual steps from 10+ to just 2 (enabling OAuth provider in console).

## Problem

The initial Firebase setup was entirely manual and required:
1. Installing npm/Node.js
2. Upgrading Node.js to v20+ (Firebase CLI requirement)
3. Installing firebase-tools globally
4. Running `firebase login`
5. Running `firebase init` interactively
6. Selecting Firestore features
7. Configuring file paths
8. Enabling Google OAuth in console
9. Setting support email

This was error-prone and time-consuming.

## Solution

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

## Changes Made

### Files Modified

1. **`deployment/setup-infrastructure.sh`**
   - Added STEP 6: Firebase CLI Setup
   - Automated CLI installation check and installation
   - Automated configuration file creation
   - Updated STEP 7: Manual Firebase Auth instructions with direct URL

2. **`docs/DEPLOYMENT_GUIDE.md`**
   - Added Node.js installation instructions (v20+ requirement)
   - Updated Firebase Authentication Setup section
   - Clarified automated vs manual steps
   - Added explanation of why OAuth enablement must be manual

3. **`.gitignore`**
   - Added comment clarifying `firebase.json` and `.firebaserc` should be committed
   - These are project configuration, not secrets

### Files Created

- `.firebaserc` - Firebase project configuration (auto-generated)
- `firebase.json` - Firebase features configuration (auto-generated)
- `deployment/firestore.indexes.json` - Firestore indexes (auto-generated)

## Technical Details

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

### Firebase Configuration Files

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

## Benefits

1. **Reduced Manual Steps**: From 10+ to 2
2. **Faster Setup**: ~15 minutes saved per deployment
3. **Fewer Errors**: Automated file creation eliminates typos
4. **Better Documentation**: Clear separation of automated vs manual steps
5. **Idempotent**: Script can be re-run safely

## Testing

Verified the setup script:
- ✅ Detects existing Firebase CLI installation
- ✅ Installs Firebase CLI when npm is available
- ✅ Creates all configuration files correctly
- ✅ Provides clear manual instructions
- ✅ Works on fresh installation
- ✅ Works when re-run (idempotent)

## Why Some Steps Remain Manual

**Google OAuth Provider Enablement** cannot be automated because:
1. Requires interactive consent in Firebase Console
2. Requires email verification for support email
3. Firebase CLI doesn't provide commands for provider configuration
4. Google's security policies require manual verification

This is by design and affects all Firebase projects, not just ours.

## Next Steps

1. ✅ Firebase CLI setup automated
2. ✅ Configuration files auto-generated
3. ✅ Documentation updated
4. ⏳ Consider adding Firebase web config generation to setup script
5. ⏳ Add verification step to check if OAuth is enabled

## Related

- [Infrastructure Setup](2025-10-30-infrastructure-setup.md)
- [Setup Improvements](2025-10-30-setup-improvements.md)
