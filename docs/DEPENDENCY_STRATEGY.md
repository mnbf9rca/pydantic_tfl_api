# Dependency Management Strategy

This document describes the automated dependency management strategy for pydantic-tfl-api using Renovate.

## Overview

We use Renovate to automatically manage dependencies with different merge strategies based on the type and risk level of each dependency.

## Dependency Categories

### 1. Dev Dependencies (Auto-Merge)

**Scope**: All packages in `[dependency-groups] dev` section of pyproject.toml

**Strategy**: Automatic merge after tests pass

**Rationale**: These tools don't affect the published package. Staying current with tooling improvements is valuable and low-risk.

**Labels**: `dependencies`, `dev`, `automerge`

**Schedule**: Weekly on Mondays before 4am

### 2. GitHub Actions (Auto-Merge)

**Strategy**: Automatic merge with SHA digest pinning

**Rationale**: Actions updates are usually security fixes or improvements. Digest pinning ensures immutability even if tags are moved.

**Labels**: `github-actions`, `automerge`

### 3. Production Dependencies (Test & Auto-Close)

**Packages**: pydantic, requests

**Strategy**: Create PR to test compatibility, then auto-close after tests complete (validation only)

**Rationale**: These dependencies directly affect package users. We want to validate new versions work, but manual control over when to actually widen ranges.

**How it works**:
1. Renovate detects new pydantic/requests version
2. Creates PR with widened range (e.g., `pydantic>=2.8.2,<4.0`)
3. CI runs full test suite including version matrix
4. PR automatically closes after tests complete (pass or fail)
5. You review test results to inform decisions about widening ranges

**Benefits**:
- Automated validation without noise
- Evidence-based decisions (see test results before committing)
- Manual control over when to widen ranges
- Can observe multiple versions before making changes

**When to manually widen ranges**:
- Multiple validation PRs show compatibility
- Changelog review shows no breaking changes
- New features in dependency are desirable
- User ecosystem has adopted new version

**Manual Update Process**:
1. Review several validation PR test results
2. Check dependency changelogs for breaking changes
3. Verify Pydantic version matrix tests passed
4. Manually update `pyproject.toml` with widened range
5. Create PR with your changes

**Labels**: `dependencies`, `production`, `test-only`, `do-not-merge`

### 4. Security Patches (Auto-Merge)

**Strategy**: Immediate auto-merge for all security vulnerability patches

**Rationale**: Security fixes should be applied as quickly as possible regardless of dependency type.

**Priority**: Highest (10)

**Labels**: `security`, `automerge`

### 5. Python Version Updates (Manual Review)

**Strategy**: Create PR for manual review only

**Rationale**: Python version updates affect:
- Which language features we can use
- Minimum version requirements for users
- Whether to add support for new versions (e.g., 3.14)
- Whether to drop support for old versions

**Considerations**:
- **Widen support where possible**: Add new Python versions rather than dropping old ones
- **Check for deprecations**: Review what's deprecated in newer Python versions
- **Test thoroughly**: Ensure all features work across all supported versions
- **Document changes**: Update README and classifiers in pyproject.toml

**Labels**: `python-version`, `needs-review`

### 6. Docker Base Images (Auto-Merge)

**Packages**: devcontainers/*

**Strategy**: Automatic merge

**Rationale**: Dev container updates are low-risk and don't affect production users.

**Labels**: `docker`, `automerge`

## Version Range Strategy

### Production Dependencies

**Approach**: **Widen ranges to maximize compatibility**

**Example**:
- Current: `pydantic>=2.8.2,<3.0`
- Pydantic 3.0.0 releases
- Action: Update to `pydantic>=2.8.2,<4.0` (widen upper bound if compatible)
- Rationale: Users can choose their Pydantic version within our tested range

**Benefits**:
- Users aren't forced to upgrade unnecessarily
- Reduces dependency conflicts in downstream projects
- Maintains compatibility across wider ecosystem

**Testing**:
- Matrix testing ensures compatibility at both ends of range (2.8.2 minimum, latest)
- If tests pass, we know the range is safe

### Dev Dependencies

**Approach**: **Stay current, prefer latest**

**Rationale**: Tooling improvements and bug fixes benefit the development process. Not shipped to users.

## Renovate Configuration

See `renovate.json` for the complete configuration.

### Key Settings

- **Schedule**: Weekly on Mondays before 4am
- **PR Limits**: Max 5 concurrent, 2 per hour (prevents spam)
- **Semantic Commits**: Enabled for consistent commit messages
- **Lockfile Maintenance**: Monthly automatic lockfile updates
- **Rebase Strategy**: Rebase PRs when behind base branch

## Monitoring

Renovate creates a "Dependency Dashboard" issue in the repository showing:
- Pending updates
- Rate-limited PRs
- Errors or warnings
- Configuration issues

Check the dashboard regularly to ensure Renovate is functioning correctly.

## Workflow

### Auto-Merge PRs
1. Renovate creates PR
2. CI tests run automatically
3. If tests pass → PR auto-merges
4. If tests fail → PR stays open for manual review

### Manual Review PRs
1. Renovate creates PR with detailed notes
2. Assignee receives notification
3. Review changelog and test results
4. Approve and merge if safe
5. Close without merging if incompatible

## Troubleshooting

### Too Many PRs

Adjust `prConcurrentLimit` and `prHourlyLimit` in renovate.json.

### Auto-Merge Not Working

Check:
- GitHub branch protection rules allow auto-merge
- All required status checks are passing
- No merge conflicts exist

### Unwanted Updates

Add to renovate.json:
```json
{
  "packageRules": [
    {
      "matchPackageNames": ["package-name"],
      "enabled": false
    }
  ]
}
```

## Related Documentation

- [Renovate Documentation](https://docs.renovatebot.com/)
- [Renovate Configuration Options](https://docs.renovatebot.com/configuration-options/)
- [ROBUSTNESS_IMPLEMENTATION.md](../ROBUSTNESS_IMPLEMENTATION.md) - Overall project roadmap
