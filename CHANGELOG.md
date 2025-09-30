# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Automated TfL API specification monitoring workflow
- Release branch strategy for production deployments
- Semantic versioning with conventional commits support
- Automated CHANGELOG generation
- Pre-commit hooks for commit message validation

### Changed
- Updated deployment workflows to use release branch
- Enhanced Renovate configuration for intelligent dependency management

## [2.0.0] - 2025-09-28

### Changed
- Complete refactor to modular build system with 143 tests
- Migration to UV package manager
- Full Pydantic v2 compatibility
- Comprehensive test suite with 85% coverage
- Modern Python 3.11+ typing with progressive type checking
- CI/CD with Ruff, mypy, and codecov integration
- GitHub Actions pinned by SHA for security

### Added
- Live TfL API testing infrastructure
- Code quality tooling (Ruff, mypy)
- Automated dependency management with Renovate

---

*This CHANGELOG is automatically generated using [Commitizen](https://commitizen-tools.github.io/commitizen/).*

*For changes prior to v2.0.0, please see the [git commit history](https://github.com/mnbf9rca/pydantic_tfl_api/commits/main).*