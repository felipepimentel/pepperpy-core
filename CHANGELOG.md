# CHANGELOG


## v0.1.1 (2025-01-06)

### Chores

- Remove semantic release configuration from pyproject.toml
  ([`0456f53`](https://github.com/felipepimentel/pepperpy-core/commit/0456f53c6cd36b92f31034719b5b45b63c970bac))

- Deleted the `[tool.semantic_release]` section from `pyproject.toml`, which included settings for
  versioning and PyPI upload.


## v0.1.0 (2025-01-05)

### Bug Fixes

- **ci_cd**: Standardize indentation and remove duplicate source-path entry in workflow
  configuration
  ([`337d707`](https://github.com/felipepimentel/pepperpy-core/commit/337d7074d3c19eefef947dab400830ee800879d4))

- Adjusted indentation for better readability in `.github/workflows/ci_cd.yml`. - Removed redundant
  `source-path` entry to streamline the workflow configuration.

- **global**: Correct ci_cd.yml workflow configuration and indentation
  ([`27bbe5d`](https://github.com/felipepimentel/pepperpy-core/commit/27bbe5d15070a6cfb5c6b7eaa23329193c20ba9f))

### Chores

- Add black formatter to dependencies in pyproject.toml
  ([`a4cafa1`](https://github.com/felipepimentel/pepperpy-core/commit/a4cafa118406f3fc7a710fa7bd2ed30efcc97bae))

- Added `black` version 24.10.0 to the project dependencies for code formatting.

- Bump version to 3.1.1 in pyproject.toml
  ([`4d2fcfb`](https://github.com/felipepimentel/pepperpy-core/commit/4d2fcfb3d4e98b8adaf08f354b1c430636eaacf9))

- Trigger workflow
  ([`b1a58cd`](https://github.com/felipepimentel/pepperpy-core/commit/b1a58cd5228f092a3855e02759ef46ad6953dc3f))

- Trigger workflow
  ([`9336ad5`](https://github.com/felipepimentel/pepperpy-core/commit/9336ad51a06de37262876843a0db3a238b479d11))

- Trigger workflow
  ([`6d10898`](https://github.com/felipepimentel/pepperpy-core/commit/6d10898705a7ff5fadb694432df59e2107e1e1eb))

- Trigger workflow
  ([`018c86c`](https://github.com/felipepimentel/pepperpy-core/commit/018c86c8dd1e8be84eafee153cb493aab942c136))

- Trigger workflow
  ([`dcde914`](https://github.com/felipepimentel/pepperpy-core/commit/dcde9145a64748ffe216e755bdb2770e6ddc4cf3))

- Trigger workflow
  ([`f88fca3`](https://github.com/felipepimentel/pepperpy-core/commit/f88fca30e9d1cb3d6c2fed37e9bd9e3dbb90e06a))

- Trigger workflow
  ([`9fff575`](https://github.com/felipepimentel/pepperpy-core/commit/9fff5758b67fd639e83b59be406bc0a15caebf8f))

- Update dependencies and add new packages
  ([`ad95940`](https://github.com/felipepimentel/pepperpy-core/commit/ad9594070af93074f25ef3881d81a89f0af88167))

- Added new packages: `click-option-group`, `dotty-dict`, `gitdb`, `gitpython`,
  `importlib-resources`, `jinja2`, `markupsafe`, `python-gitlab`, `python-semantic-release`,
  `requests-toolbelt`, `shellingham`, and `smmap` to `poetry.lock`. - Updated `pyproject.toml` to
  include `python-semantic-release` for automatic semantic versioning. - Enhanced dependency
  management with additional extras for several packages.

- Update dependencies and improve logging
  ([`1072571`](https://github.com/felipepimentel/pepperpy-core/commit/10725712a5e3a084e97d39c060fec5e146a44343))

- Added `aiofiles` and its typing stubs `types-aiofiles` to `pyproject.toml`. - Updated `mypy` to
  version 1.14.1 in `poetry.lock`. - Enhanced `pytest.ini` to filter specific warnings during tests.
  - Refactored `pepperpy_core` modules for improved clarity and performance, including: - Simplified
  exception handling and logging configurations. - Updated event handling and task management logic.
  - Removed deprecated validation functionality. - Improved test coverage and organization across
  various modules. - Removed unused scripts for linting and formatting.

### Continuous Integration

- **global**: Enable debug logging for workflow troubleshooting
  ([`835e57d`](https://github.com/felipepimentel/pepperpy-core/commit/835e57d0b222a0b4612fea4d418099e9df62fec6))

- **global**: Specify dagger version in workflow
  ([`e51d804`](https://github.com/felipepimentel/pepperpy-core/commit/e51d8041fb2e80fb546deac629359ff546222915))

- **global**: Trigger workflow with updated daggerverse modules
  ([`dda45f7`](https://github.com/felipepimentel/pepperpy-core/commit/dda45f7482304479593b9cc41c6edceb32df9aa1))

- **global**: Trigger workflow with updated daggerverse modules
  ([`36d7c7b`](https://github.com/felipepimentel/pepperpy-core/commit/36d7c7b15c9682c649794e1f0f027e9ff2c31228))

- **global**: Update dagger version parameter name
  ([`787c7c6`](https://github.com/felipepimentel/pepperpy-core/commit/787c7c65d5e8b03bbfa6b952440e525904d9029f))

### Features

- **python**: Refactor CI/CD workflow to streamline pipeline execution
  ([`32a6700`](https://github.com/felipepimentel/pepperpy-core/commit/32a670075848c0ff9eba42914818991f40eb4f37))

- Renamed job from 'dagger' to 'pipeline' for clarity. - Removed the version management step,
  simplifying the workflow. - Updated the Python pipeline step to eliminate the version argument,
  enhancing the command's simplicity. - Ensured the use of the GITHUB_TOKEN environment variable for
  improved security during execution.
