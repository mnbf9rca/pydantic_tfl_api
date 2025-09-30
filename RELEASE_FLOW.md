# Release Flow Documentation

## Overview

This document defines the **desired** release flow for the `pydantic_tfl_api` project. It includes both current implementation status and planned improvements.

## Branch Strategy

The project uses a **two-branch release strategy**:

- **`main` branch**: Development branch where all features and fixes are merged
- **`release` branch**: Production-ready branch that gates deployments to PyPI

**Key Principle:** The release branch is a **gate**, not a **mirror**. Features are promoted intentionally, not automatically.

## Complete Release Flow

### 1. Development Phase

```mermaid
Developer → Feature Branch → Pull Request → main branch
```

- Developers create feature branches from `main`
- PRs are reviewed and merged into `main`
- All tests and checks must pass before merging
- Code accumulates on `main` until ready for release

### 2. Manual Sync to Release + Version Bump (Atomic Operation)

**Workflow:** `.github/workflows/sync_release.yml`

**Trigger:** 🎯 **Manual workflow dispatch only** (on-demand)

**Current State:** ❌ Currently triggers automatically on every push to main and doesn't bump version (needs fixing)

**Desired Behavior - All in ONE workflow:**

1. **Manual trigger** when ready to create a release
   - Maintainer dispatches workflow from GitHub Actions UI
   - Optional input: manual bump type override (major/minor/patch)
   - If not provided, auto-detect from dependencies

2. **Sync process:**
   - Fetch full history of both branches
   - Checkout the `release` branch
   - Merge `main` into `release`
   - If merge conflicts:
     - Abort merge
     - Create summary with conflicting files
     - Exit with error (require manual conflict resolution)

3. **Automatic version detection:**
   - Run `scripts/determine-version-bump.sh`
   - Diff `pyproject.toml` between pre-merge `release` and `main`
   - Extract production dependency version changes:
     - `pydantic` version changes
     - `requests` version changes
   - Determine bump type based on most significant dependency change:
     - Dependency major bump → major version bump
     - Dependency minor bump → minor version bump
     - Dependency patch bump → patch version bump
   - Priority: major > minor > patch
   - If manual override provided, use that instead

4. **Version update and tagging:**
   - Use `anothrNick/github-tag-action` to determine new version
   - **Set** new version in `pyproject.toml`
   - Create Git tag with new version
   - Commit updated `pyproject.toml` to `release` branch
   - Push both commit and tag

5. **Verification:**
   - Confirm tag was created successfully
   - Log new version number

**Important:** Uses GitHub App token to bypass branch protection rules

**Note:** Commitizen remains available for future changelog generation

### 3. Security Checks, Build, and Deploy

**Workflow:** `.github/workflows/deploy_workflow_wrapper.yml`

**Trigger:** Automatically after successful version bump on `release` branch

**Desired Behavior:**

1. **Deployment Target Selection:**
   - Use GitHub environment variable or repository variable as flag
   - Options:
     - `DEPLOY_TARGET=test` → Deploy to Test PyPI
     - `DEPLOY_TARGET=prod` → Deploy to Production PyPI
   - Allow testing on Test PyPI before promoting to production
   - Can be set per-deployment or as persistent repo variable

2. **Security Checks:**
   - Run CodeQL analysis
   - Dependency vulnerability scanning
   - License compliance checks
   - SBOM generation

3. **Build Artifacts:**
   - Build wheel and source distribution
   - Generate checksums

4. **Sign Artifacts:**
   - Use Sigstore for artifact signing
   - Generate provenance attestations

5. **Deploy to PyPI:**
   - Use trusted publishing (OIDC) for secure deployment
   - Deploy to Test PyPI or Production PyPI based on flag
   - Create GitHub Release with artifacts and changelog

## Current Issues and Required Changes

### Issue 1: Sync Workflow - Automatic Trigger

**Problem:** The workflow triggers automatically on every push to `main`, making release branch just a mirror.

**Fix Required:**
```yaml
# Remove this from sync_release.yml:
on:
  push:
    branches:
      - main

# Keep only this:
on:
  workflow_dispatch:  # Manual trigger only
```

### Issue 2: Sync Workflow - Verification Step Bug

**Problem:** The "Verify sync" step (line 122-136) fails with:
```
fatal: refusing to fetch into branch 'refs/heads/release' checked out
```

**Root Cause:** Line 125 attempts `git fetch origin release:release` while release is checked out.

**Fix Required:**
```yaml
# Option 1: Use remote refs only (recommended)
- name: Verify sync
  run: |
    git fetch origin release main
    if git merge-base --is-ancestor origin/main origin/release; then
      echo "✅ Release branch is now in sync with main"
    fi

# Option 2: Checkout main first
- name: Verify sync
  run: |
    git checkout main
    git fetch origin release:release main:main
    if git merge-base --is-ancestor main release; then
      echo "✅ Release branch is now in sync with main"
    fi
```

### Issue 3: Version Bump - Manual Type Selection

**Problem:** Requires manual selection of major/minor/patch, prone to human error.

**Fix Required:** Replace manual input with dependency-based version detection.

**Recommended Implementation:**

1. **Create version detection script** (`scripts/determine-version-bump.sh`):
   ```bash
   # Diff pyproject.toml between main and release
   # Extract production dependency versions (pydantic, requests)
   # Compare semantic versions to determine bump type
   # Return most significant bump (major > minor > patch)
   ```

2. **Use `anothrNick/github-tag-action@v1`:**
   - Reads the determined bump type
   - Creates and pushes Git tag
   - Returns new version number

3. **Update `pyproject.toml`:**
   - **Set** version field to new version (not increment)
   - Use Python TOML parser to update version field

4. **Allow manual override:**
   - Keep `workflow_dispatch` with optional bump_type input
   - If provided, use manual bump type instead of automatic detection

### Issue 4: Missing Security Checks, Signing, and Test Deployment

**Current State:** Basic build and deploy workflow exists, but lacks security features and test environment option.

**Enhancements Needed:**

1. **Deployment Control:**
   - Add GitHub repository variable: `DEPLOY_TARGET` (values: `test` or `prod`)
   - Allow testing on Test PyPI before production deployment
   - Support environment-specific configurations

2. **Security Checks:**
   - Add CodeQL security scanning
   - Add dependency vulnerability checks
   - Implement Sigstore artifact signing
   - Generate SBOM (Software Bill of Materials)
   - Add provenance attestations

## Expected Outcomes After Implementation

1. ✅ **Controlled releases:** Only when maintainer manually triggers sync
2. ✅ **Automated versioning:** No manual version selection needed
3. ✅ **Security assurance:** All artifacts scanned and signed
4. ✅ **Full automation:** Manual trigger → automatic version → automatic deploy
5. ✅ **Clear audit trail:** Git tags, signed artifacts, and GitHub releases

## Branch Protection Recommendations

From the workflow comments, the following protections should be applied to `release` branch:

- ✅ Require pull request before merging
- ✅ Require status checks to pass
- ✅ Require branches to be up-to-date
- ✅ Include administrators (optional, but recommended)

**Exception:** The bump version workflow needs to push directly to `release`, which is why it uses a GitHub App token with elevated permissions.

## Summary Flow Diagram (Desired State)

```
┌─────────────────────────────────────────────────────────────┐
│  Development Phase                                           │
│  (Continuous - multiple merges accumulate)                   │
│                                                               │
│  Feature Branch → PR → main                                  │
│  Feature Branch → PR → main                                  │
│  Feature Branch → PR → main                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ (Code ready for release)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  🎯 MANUAL TRIGGER - Atomic Sync + Bump                     │
│  (sync_release.yml - workflow_dispatch)                     │
│                                                               │
│  Maintainer clicks "Run workflow" in GitHub UI               │
│  └─> ATOMIC OPERATION:                                       │
│      1. Merge main → release                                 │
│      2. Diff dependencies in pyproject.toml                  │
│      3. Determine bump type (or use manual override)         │
│      4. Set version in pyproject.toml                        │
│      5. Create and push git tag                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  🤖 AUTOMATIC - Security, Build & Deploy                    │
│  (deploy_workflow_wrapper.yml - workflow_run)               │
│                                                               │
│  1. Security: CodeQL + dependency scan                       │
│  2. Build: wheel + sdist + checksums                         │
│  3. Sign: Sigstore + provenance                              │
│  4. Deploy: PyPI (test/prod based on DEPLOY_TARGET)         │
│  5. Release: Create GitHub release                           │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**
- ✅ Only ONE manual step: triggering the sync
- ✅ Sync + version bump = atomic operation (no intermediate state)
- ✅ Version determined from dependency changes (or manual override)
- ✅ Everything after trigger is fully automated
- ✅ Security checks and signing happen automatically
- ✅ Release gate maintained (release branch controls deployments)

## Implementation Priority

### Phase 1: Implement Atomic Sync+Bump Workflow (Critical)

1. Create `scripts/determine-version-bump.sh`:
   - Diff `pyproject.toml` between `main` and `release`
   - Extract and compare production dependency versions (pydantic, requests)
   - Return bump type (major/minor/patch)
   - Handle edge cases (no changes, new dependencies, etc.)

2. Update `sync_release.yml`:
   - Remove automatic push trigger (keep only workflow_dispatch)
   - Add optional manual bump type input
   - Integrate version detection script
   - Add `anothrNick/github-tag-action` for tagging
   - Set version in `pyproject.toml` after determining bump
   - Commit and push version change + tag atomically
   - Fix verification step bug (use remote refs)

3. Removed obsolete `deploy_bump_version.yml`:
   - Version bumping now happens in `bump_version.yml` (reusable workflow)
   - Called by `sync_release.yml` after successful sync

### Phase 2: Add Security, Signing & Test Deployment (Medium Priority)

1. Add `DEPLOY_TARGET` repository variable support:
   - Check variable value (test/prod)
   - Route to appropriate PyPI environment
   - Default to `prod` if not set

2. Integrate CodeQL scanning
3. Add dependency vulnerability checks
4. Implement Sigstore signing
5. Generate SBOM and provenance

## Testing the Implementation

### Testing Phase 1 (Atomic Sync+Bump):

1. **Test automatic dependency-based bumping:**
   - Update a production dependency in `main` (e.g., bump pydantic minor version)
   - Trigger sync workflow manually (no bump type input)
   - Verify version detection script correctly identifies bump type
   - Check that `release` branch receives the merge
   - Check that `pyproject.toml` version is **set** correctly
   - Verify git tag is created with correct version
   - Verify workflow summary shows sync + version details

2. **Test manual override:**
   - Trigger sync workflow with explicit bump type
   - Verify manual bump type is used instead of automatic detection

3. **Test conflict handling:**
   - Create conflicting changes in main and release
   - Trigger sync workflow
   - Verify workflow exits gracefully with conflict details

### Testing Phase 2 (Security & Deploy):

1. **Test deployment flag:**
   - Set `DEPLOY_TARGET=test` in repository variables
   - Trigger release and verify deployment to Test PyPI
   - Verify package can be installed from Test PyPI
   - Switch to `DEPLOY_TARGET=prod` and verify production deployment

2. **Security checks:**
   - Verify CodeQL scans complete successfully
   - Check that artifacts are signed with Sigstore
   - Verify SBOM is generated

3. **Deployment verification:**
   - Confirm GitHub release is created with all artifacts
   - Verify changelog is included in release notes