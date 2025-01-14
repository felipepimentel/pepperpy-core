# Dependencies Module

The dependencies module provides utilities for managing Python package dependencies in PepperPy, including dependency checking, verification, and installation command generation.

## Overview

The module implements a comprehensive dependency management system that supports:
- Checking if dependencies are installed
- Verifying required dependencies
- Managing provider-specific dependencies
- Managing feature-specific dependencies
- Generating installation commands
- Dependency error handling

## Functions

### check_dependency

```python
def check_dependency(package: str) -> bool
```

Check if a Python package is installed.

**Arguments:**
- `package`: Package name to check

**Returns:**
- `True` if package is installed, `False` otherwise

### get_missing_dependencies

```python
def get_missing_dependencies(packages: list[str]) -> list[str]
```

Get a list of missing dependencies.

**Arguments:**
- `packages`: List of package names to check

**Returns:**
- List of missing package names

### verify_dependencies

```python
def verify_dependencies(packages: list[str]) -> None
```

Verify that all required dependencies are installed.

**Arguments:**
- `packages`: List of package names to verify

**Raises:**
- `DependencyError`: If any dependencies are missing

### get_installation_command

```python
def get_installation_command(missing_deps: list[str], use_poetry: bool = True) -> str
```

Get command to install missing dependencies.

**Arguments:**
- `missing_deps`: List of missing package names
- `use_poetry`: Whether to use Poetry for installation (default: True)

**Returns:**
- Installation command string

## Classes

### DependencyError

A specialized error class for dependency-related issues.

```python
class DependencyError(PepperpyError):
    def __init__(self, message: str, cause: Optional[Exception] = None, package: Optional[str] = None)
```

**Arguments:**
- `message`: Error message describing the issue
- `cause`: Optional underlying exception that caused the error
- `package`: Optional name of the package that caused the error

### DependencyManager

Manager for handling package dependencies.

```python
class DependencyManager:
    def __init__(self) -> None
```

The DependencyManager provides functionality for:
- Registering provider and feature dependencies
- Verifying dependencies are installed
- Checking availability of providers and features
- Getting installation commands

#### Methods

##### register_provider

```python
def register_provider(self, provider: str, dependencies: list[str]) -> None
```

Register dependencies for a provider.

**Arguments:**
- `provider`: Provider name
- `dependencies`: List of package dependencies

##### register_feature

```python
def register_feature(self, feature: str, dependencies: list[str]) -> None
```

Register dependencies for a feature.

**Arguments:**
- `feature`: Feature name
- `dependencies`: List of package dependencies

##### verify_provider

```python
def verify_provider(self, provider: str) -> list[str] | None
```

Verify dependencies for a specific provider.

**Arguments:**
- `provider`: Provider name

**Returns:**
- List of missing dependencies if any, None if all dependencies are met

**Raises:**
- `ValueError`: If provider is not supported

##### verify_feature

```python
def verify_feature(self, feature: str) -> list[str] | None
```

Verify dependencies for a specific feature.

**Arguments:**
- `feature`: Feature name

**Returns:**
- List of missing dependencies if any, None if all dependencies are met

**Raises:**
- `ValueError`: If feature is not supported

##### check_provider_availability

```python
def check_provider_availability(self, provider: str) -> bool
```

Check if a provider is available for use.

**Arguments:**
- `provider`: Provider name

**Returns:**
- `True` if provider is available, `False` otherwise

##### check_feature_availability

```python
def check_feature_availability(self, feature: str) -> bool
```

Check if a feature is available for use.

**Arguments:**
- `feature`: Feature name

**Returns:**
- `True` if feature is available, `False` otherwise

##### get_available_providers

```python
def get_available_providers(self) -> set[str]
```

Get set of available providers.

**Returns:**
- Set of provider names that are available for use

##### get_available_features

```python
def get_available_features(self) -> set[str]
```

Get set of available features.

**Returns:**
- Set of feature names that are available for use

##### clear

```python
def clear(self) -> None
```

Clear all registered dependencies.

## Usage Examples

### Basic Dependency Checking

```python
from pepperpy.dependencies import check_dependency, verify_dependencies

# Check if a single package is installed
is_installed = check_dependency("requests")

# Verify multiple required dependencies
try:
    verify_dependencies(["requests", "pandas", "numpy"])
except DependencyError as e:
    print(f"Missing dependency: {e.package}")
```

### Using DependencyManager

```python
from pepperpy.dependencies import DependencyManager

# Create a dependency manager
manager = DependencyManager()

# Register provider dependencies
manager.register_provider("aws", ["boto3", "botocore"])
manager.register_provider("gcp", ["google-cloud-storage"])

# Register feature dependencies
manager.register_feature("ml", ["scikit-learn", "tensorflow"])
manager.register_feature("viz", ["matplotlib", "seaborn"])

# Check provider availability
if manager.check_provider_availability("aws"):
    print("AWS provider is available")

# Get available features
available_features = manager.get_available_features()
print(f"Available features: {available_features}")

# Verify feature dependencies
missing_deps = manager.verify_feature("ml")
if missing_deps:
    cmd = get_installation_command(missing_deps)
    print(f"Install missing dependencies with: {cmd}")
```

## Best Practices

1. **Early Verification**: Verify dependencies early in your application startup
2. **Graceful Handling**: Handle missing dependencies gracefully with clear error messages
3. **Provider Management**: Use DependencyManager for provider-specific dependencies
4. **Feature Management**: Use DependencyManager for feature-specific dependencies
5. **Installation Commands**: Use get_installation_command for consistent installation instructions

## See Also

- [Core Module](core.md) - Core functionality including base error classes
- [Plugin Module](plugin.md) - Plugin system that may require dependency management 