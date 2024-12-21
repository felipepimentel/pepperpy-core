# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup
- Core configuration management
- Logging system with structlog
- Security module for configuration validation
- Metrics collection system
- CI/CD pipeline with GitHub Actions and Dagger
- Type hints and strict type checking
- Test coverage with pytest and coverage.py
- Code quality checks with Ruff
- Security scanning with Bandit

### Changed
- Updated async fixtures in tests to use pytest-asyncio
- Improved CI/CD process with separate workflows
- Enhanced type annotations and validation

### Fixed
- Async fixture warnings in pytest
- Type annotation issues in core modules

## [0.1.0] - 2024-03-21

### Added
- First release of pepperpy-core
- Basic configuration management
- Logging system
- Security module
- Metrics collection
- Full test coverage
- Type hints and validation
- CI/CD automation

[Unreleased]: https://github.com/pimentel/pepperpy-core/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/pimentel/pepperpy-core/releases/tag/v0.1.0
