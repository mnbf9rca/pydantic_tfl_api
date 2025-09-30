# Dependency Management Strategy

This document describes the automated dependency management strategy for pydantic-tfl-api using Renovate.

## Overview

We use Renovate to automatically manage dependencies with different merge strategies based on the type and risk level of each dependency.

## Dependency Categories

### 1. Dev Dependencies (Auto-Merge)

**Packages**: pytest, black, ruff, mypy, coverage, pre-commit, types-*, jsonschema

**Strategy**: Automatic merge after tests pass

**Rationale**: These tools don't affect the published package. Staying current with tooling improvements is valuable and low-risk.

**Labels**: `dependencies`, `dev`, `automerge`

**Schedule**: Weekly on Mondays before 4am

### 2. GitHub Actions (Auto-Merge)

**Strategy**: Automatic merge with SHA digest pinning

**Rationale**: Actions updates are usually security fixes or improvements. Digest pinning ensures immutability even if tags are moved.

**Labels**: `github-actions`, `automerge`

### 3. Production Dependencies (Manual Review)

**Packages**: pydantic, requests

**Strategy**: Create PR for manual review, widen version ranges where possible

**Rationale**: These dependencies directly affect package users. Changes require careful review for:
- Breaking changes in dependencies
- Compatibility across version ranges
- Impact on existing users
- Whether we can widen support (e.g., pydantic>=2.8.2,<3.0 → >=2.8.2,<4.0)

**Review Checklist**:
1. ✅ Review dependency changelog for breaking changes
2. ✅ Verify Pydantic version matrix tests pass (2.8.2 and latest)
3. ✅ Consider impact on users with older dependency versions
4. ✅ Prefer widening ranges over bumping minimums
5. ✅ Test package build and installation

**Labels**: `dependencies`, `production`, `needs-review`

**Assignees**: @mnbf9rca

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