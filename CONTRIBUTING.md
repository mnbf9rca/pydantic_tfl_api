# Contributing to pydantic-tfl-api

Thank you for your interest in contributing to pydantic-tfl-api! This document provides guidelines and workflows for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Branch Strategy](#branch-strategy)
- [Commit Message Convention](#commit-message-convention)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Release Process](#release-process)
- [Code Style](#code-style)

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Initial Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/pydantic_tfl_api.git
cd pydantic_tfl_api
```

2. Install dependencies:
```bash
uv sync --all-extras --dev
```

3. Install pre-commit hooks:
```bash
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

This will automatically run before every commit:
- **Ruff** - Linting and auto-formatting
- **mypy** - Type checking (targeting Python 3.11 for compatibility)
- **Commitizen** - Validate commit messages follow conventional commits
- **File checks** - YAML/JSON/TOML validation, trailing whitespace, etc.
- **Renovate** - Validate renovate.json configuration

## Branch Strategy

We use a two-branch strategy for development and releases:

### `main` Branch
- **Purpose**: Active development
- **Protection**: Requires PR review, all tests must pass
- **Workflow**: All feature branches merge here

### `release` Branch
- **Purpose**: Production releases, deployed to PyPI
- **Protection**: Requires PR review, status checks, admin approval
- **Workflow**: Synced from `main` when ready for release

### Branch Naming

- **Features**: `feature/description-of-feature`
- **Fixes**: `fix/description-of-fix`
- **Docs**: `docs/description-of-change`
- **Automated**: `automated/update-description`

## Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages. This enables:
- Automatic semantic versioning
- Automatic CHANGELOG generation
- Clear git history

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature (triggers MINOR version bump)
- `fix`: Bug fix (triggers PATCH version bump)
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements (triggers PATCH version bump)
- `test`: Test additions or modifications
- `build`: Build system changes
- `ci`: CI/CD configuration changes
- `chore`: Maintenance tasks
- `revert`: Revert a previous commit

### Breaking Changes

Add `!` after the type or include `BREAKING CHANGE:` in the footer to trigger a MAJOR version bump:

```
feat!: remove deprecated API endpoint

BREAKING CHANGE: The /old-endpoint has been removed. Use /new-endpoint instead.
```

### Examples

```bash
# Feature (minor bump)
git commit -m "feat(models): add new BikePoint occupancy fields"

# Bug fix (patch bump)
git commit -m "fix(api): correct datetime serialization in Journey model"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Breaking change (major bump)
git commit -m "feat!: upgrade to Pydantic v2

BREAKING CHANGE: All models now use Pydantic v2. Users must update their code."
```

### Validation

The pre-commit hooks will automatically validate and format your code. If there are issues:

```bash
# Check the error message and fix your commit
git commit --amend
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the [Code Style](#code-style)
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests Locally

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_models.py

# Run linting
uv run ruff check .
uv run mypy .
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat(models): add new feature"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub targeting the `main` branch.

### 6. PR Review

- Ensure all CI checks pass
- Address review feedback
- Squash commits if needed before merge

## Testing

### Running Tests

```bash
# All tests
uv run pytest

# Unit tests only (fast)
uv run pytest -m unit

# Integration tests (requires network)
uv run pytest -m integration

# Skip slow tests
uv run pytest -m "not slow"
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names: `test_description_of_what_is_tested`
- Mark tests appropriately:
  - `@pytest.mark.unit` - Fast, no network
  - `@pytest.mark.integration` - Requires network/external services
  - `@pytest.mark.slow` - Long-running tests

### Coverage Requirements

- Minimum coverage: 85%
- All new code should have tests
- Focus on critical paths and edge cases

## Release Process

Releases are automated through the release branch workflow:

### For Maintainers

1. **Sync main to release branch**:
   - The sync workflow runs automatically on push to `main`
   - Or trigger manually via GitHub Actions

2. **Bump version on release branch**:
```bash
# Checkout release branch
git checkout release
git pull origin release

# Bump version (uses conventional commits to determine bump type)
uv run cz bump --yes

# Or manually trigger via GitHub Actions with bump type (major/minor/patch)
```

3. **Deploy to PyPI**:
   - Deployment workflow triggers automatically after version bump
   - Artifacts are built, tested, and published to PyPI
   - GitHub release is created with changelog

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (x.Y.0): New features, backward compatible
- **PATCH** (x.y.Z): Bug fixes, backward compatible

Version bumps are determined automatically from commit messages:
- `feat:` commits → MINOR bump
- `fix:`, `perf:` commits → PATCH bump
- `BREAKING CHANGE:` or `!` → MAJOR bump

## Code Style

### Python Style

We use:
- **Ruff** for linting and formatting
- **mypy** for type checking
- **Black** code style (120 character line length)

### Type Hints

- All functions must have type hints
- Use modern Python typing (`list[str]` not `List[str]`)
- Avoid `Any` where possible

### Documentation

- Add docstrings to all public classes and functions
- Use Google-style docstring format
- Include examples for complex functionality

### Code Organization

- Keep functions focused and single-purpose
- Extract complex logic into separate functions
- Use descriptive variable and function names
- Follow existing code patterns in the repository

### Pre-commit Checks

Before committing, the following checks run automatically (via pre-commit hooks):

1. **Ruff linting** - Auto-fixes style issues
2. **Ruff formatting** - Ensures consistent code style
3. **mypy type checking** - Validates types against Python 3.11
4. **Commitizen** - Validates commit message format
5. **File checks** - YAML/JSON/TOML validation, trailing whitespace, end-of-file
6. **Renovate config** - Validates renovate.json

If hooks fail, fix the issues and commit again. The hooks will auto-fix what they can.

**Bypass hooks (not recommended):**
```bash
git commit --no-verify -m "your message"
```

**Run hooks manually:**
```bash
# Run all hooks on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files
uv run pre-commit run mypy --all-files

# Update hook versions
uv run pre-commit autoupdate
```

**Manual checks (if needed):**
```bash
# Auto-fix ruff issues
uv run ruff check --fix .

# Format with ruff
uv run ruff format .

# Check types
uv run mypy .
```

## Automated Workflows

### TfL API Specification Updates

- **Frequency**: Weekly (Mondays at 3 AM UTC)
- **Process**: Automatically fetches TfL API specs, rebuilds models, creates PR if changes detected
- **Action**: Review the PR, check for breaking changes, merge if acceptable

### Dependency Updates

- **Tool**: Renovate
- **Frequency**: Weekly (Mondays before 4 AM)
- **Strategy**:
  - Dev dependencies: Auto-merge after tests pass
  - Production dependencies: Test-only PRs for review
  - Security patches: Auto-merge

### Release Branch Sync

- **Trigger**: Push to `main` branch
- **Process**: Automatically merges `main` into `release` branch
- **Action**: Conflicts require manual resolution

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/mnbf9rca/pydantic_tfl_api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mnbf9rca/pydantic_tfl_api/discussions)
- **TfL API Docs**: [TfL API Portal](https://api-portal.tfl.gov.uk/)

## Code of Conduct

- Be respectful and constructive
- Follow the Python community guidelines
- Help maintain a welcoming environment

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to pydantic-tfl-api!