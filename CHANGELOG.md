# CHANGELOG


## v0.4.1 (2025-01-14)

### Bug Fixes

- Update template module and tests to handle missing variables
  ([`a8e97c3`](https://github.com/felipepimentel/pepperpy-core/commit/a8e97c34cb5b6a1f1cf0fedffb413728fcb433ec))

### Refactoring

- Reorganize error handling and module structure
  ([`3b96580`](https://github.com/felipepimentel/pepperpy-core/commit/3b9658014b003422e3b259196ecd79bdb6166a15))

### Testing

- Add comprehensive test cases for template module
  ([`f0b5ecb`](https://github.com/felipepimentel/pepperpy-core/commit/f0b5ecb216af780d403d2cf920437182793c76d3))

- Add edge case tests for template module
  ([`dac4735`](https://github.com/felipepimentel/pepperpy-core/commit/dac47359b4de3351ef31670177aaefb52fd0792a))


## v0.4.0 (2025-01-14)

### Chores

- Bump version to 0.3.1 in pyproject.toml
  ([`6fd1898`](https://github.com/felipepimentel/pepperpy-core/commit/6fd1898c247265b86328c6b0d93c7493065ad38e))

### Features

- Enhance network module with status code handling, form data, and interceptors
  ([`7a746f8`](https://github.com/felipepimentel/pepperpy-core/commit/7a746f81381872f60f663494a6983960ad2ec5d4))


## v0.3.0 (2025-01-14)

### Chores

- Bump version to 0.2.1 in pyproject.toml
  ([`55b1fbe`](https://github.com/felipepimentel/pepperpy-core/commit/55b1fbea55aafba175d5c66a695178b9e2bda061))

### Documentation

- Update package name references in documentation
  ([`c4404f9`](https://github.com/felipepimentel/pepperpy-core/commit/c4404f91ffec77c443d93dc0a5865b1ac428ef15))

### Features

- **package**: Rename package from pepperpy_core to pepperpy
  ([`ea92ec6`](https://github.com/felipepimentel/pepperpy-core/commit/ea92ec6efd5691cbb0e614dd7a56d3d3e6a0005e))


## v0.2.0 (2025-01-14)

### Build System

- Add pre-commit as dev dependency
  ([`3db7628`](https://github.com/felipepimentel/pepperpy-core/commit/3db7628c653af633d8437cce3f6f918c0f628714))

- Remove coverage threshold requirement
  ([`26c63cc`](https://github.com/felipepimentel/pepperpy-core/commit/26c63cceb6e848aab588492f820e0eb9d62b1767))

### Chores

- Update dependencies and enhance README documentation
  ([`d21cafa`](https://github.com/felipepimentel/pepperpy-core/commit/d21cafaf0f9c9ac3f2f4fa646aa06fce51b059a3))

- Updated `pygments` from version 2.19.0 to 2.19.1 in `poetry.lock`. - Updated `pytest-asyncio` from
  version 0.25.1 to 0.25.2 in `poetry.lock`. - Expanded the `README.md` to include detailed
  features, installation instructions, quick start guide, core modules, development setup,
  contributing guidelines, and best practices for the PepperPy Core library.

- Update repository URL and remove development status classifier in pyproject.toml
  ([`ea90e10`](https://github.com/felipepimentel/pepperpy-core/commit/ea90e10dce78072deb49e73050cd30390b40f4a4))

- Changed the repository URL from "https://github.com/pimentel/pepperpy-core" to
  "https://github.com/felipepimentel/pepperpy-core". - Removed the "Development Status :: 4 - Beta"
  classifier from the classifiers list.

### Documentation

- Add error handling section and utilities examples
  ([`62536af`](https://github.com/felipepimentel/pepperpy-core/commit/62536af0a2c1344079928a66430fbcb064ebc092))

- Introduced a new "Error Handling" section in the documentation, detailing exception hierarchy and
  types. - Added examples for error handling utilities in `utils.md`, including `format_exception`,
  `format_error_context`, and `get_error_type`. - Provided best practices for error logging and
  reporting, enhancing the clarity and usability of error management in the codebase.

This commit improves the documentation related to error handling, making it easier for developers to
  implement robust error management in their applications.

- Enhance utilities documentation and remove deprecated utils.py
  ([`9c6612d`](https://github.com/felipepimentel/pepperpy-core/commit/9c6612d6b42a7c76cd896214a78235a1cbb2e5db))

- Expanded the Utilities Module documentation to include detailed sections on Error Utilities and
  Logging Utilities, providing examples and best practices for error handling and logging. - Removed
  the deprecated `utils.py` file, consolidating utility functions into the appropriate modules for
  better organization and maintainability. - Updated the error handling examples to reflect the new
  structure and improved clarity in the documentation.

This commit improves the usability and clarity of the utilities documentation, making it easier for
  developers to implement error handling and logging in their applications.

### Features

- Add error utilities and pre-commit hooks
  ([`4078eab`](https://github.com/felipepimentel/pepperpy-core/commit/4078eabbdfe4867102b7f1fcc9e14b6b12875ee2))

- Reorganize utility modules and improve code structure
  ([`7f18bff`](https://github.com/felipepimentel/pepperpy-core/commit/7f18bffe997c6fd2b547e52ca59959340871aca2))

- **plugin**: Add ResourcePlugin with RESTful-like capabilities
  ([`6d7ea75`](https://github.com/felipepimentel/pepperpy-core/commit/6d7ea75ab17333617b0de86c094a485881f1d54c))

### Refactoring

- **plugin**: Improve code structure and enhance documentation
  ([`f883d7a`](https://github.com/felipepimentel/pepperpy-core/commit/f883d7aeb44286cc45eaa618e29749b2e9b889a8))

- Reorganized import statements for better readability and maintainability. - Streamlined parameters
  in `create_resource` and `update_resource` methods. - Removed unnecessary line breaks and ensured
  consistent formatting across the codebase. - Expanded documentation for core modules, including
  installation instructions and usage examples. - Updated README.md with detailed features and
  contributing guidelines.

This commit enhances both the code quality and the documentation, making it easier for developers to
  understand and use the plugin effectively.

- **plugin**: Reorganize imports and streamline ResourcePlugin methods
  ([`2126fba`](https://github.com/felipepimentel/pepperpy-core/commit/2126fba9846fed59073ffbbf368fc2617711706a))

- Moved import statements for `Callable` and `dataclass` to improve readability. - Consolidated
  parameters in `create_resource` and `update_resource` methods for cleaner syntax. - Enhanced code
  clarity by removing unnecessary line breaks and ensuring consistent formatting.

- **tests**: Remove test_logging.py file
  ([`01a6ad5`](https://github.com/felipepimentel/pepperpy-core/commit/01a6ad57a382a6d6527197d0a90cec08efb6f91a))

- Deleted the `test_logging.py` file, which contained tests for the logging module. - This removal
  helps streamline the test suite by eliminating outdated or redundant tests, contributing to better
  maintainability and clarity in the testing framework.

- **tests**: Remove unused imports in test_plugin.py
  ([`d311235`](https://github.com/felipepimentel/pepperpy-core/commit/d3112355d518440346e8bd3ed99439b7bbe72790))


## v0.1.6 (2025-01-06)


## v0.1.5 (2025-01-06)


## v0.1.4 (2025-01-06)


## v0.1.3 (2025-01-06)


## v0.1.2 (2025-01-06)


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
