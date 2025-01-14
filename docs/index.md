# PepperPy Documentation

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Poetry](https://img.shields.io/badge/poetry-managed-blue)
![Black](https://img.shields.io/badge/code%20style-black-black)
![Mypy](https://img.shields.io/badge/types-mypy-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

PepperPy is a powerful utility library designed to accelerate Python project development through:

- **Productivity Acceleration**: Rich set of tools and utilities that eliminate boilerplate code
- **Security by Design**: Built-in security features and best practices
- **Optimized Performance**: Async-first architecture with efficient resource management
- **Total Extensibility**: Plugin system and modular design for maximum flexibility

## Quick Start

### Installation

```bash
# Using Poetry (recommended)
poetry add pepperpy

# Using pip
pip install pepperpy
```

### Basic Usage

```python
from pepperpy import PepperPy
from pepperpy.config import ConfigManager
from pepperpy.logging import LogManager

async def main():
    # Initialize core
    app = PepperPy()
    
    # Configure components
    await app.configure(
        config=ConfigManager("config"),
        logging=LogManager()
    )
    
    # Start application
    await app.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Core Features

### 1. Async Operations

```python
from pepperpy.task import TaskManager

async def process_data():
    # Create task manager
    manager = TaskManager()
    
    # Add tasks
    task1 = await manager.create_task(
        name="process_images",
        func=process_images,
        priority=1
    )
    
    task2 = await manager.create_task(
        name="update_database",
        func=update_database,
        priority=2
    )
    
    # Execute tasks
    results = await manager.execute_all()
```

### 2. Type Safety

```python
from pepperpy.types import DataModel
from pepperpy.validation import validate_model

class UserModel(DataModel):
    id: int
    name: str
    email: str
    active: bool = True

async def create_user(data: dict):
    # Validate data
    user = await validate_model(
        UserModel,
        data
    )
    
    # Process user
    return await save_user(user)
```

### 3. Event System

```python
from pepperpy.event import EventManager

async def setup_events():
    # Create event manager
    events = EventManager()
    
    # Register handlers
    @events.on("user.created")
    async def handle_user_created(user):
        await send_welcome_email(user)
    
    @events.on("order.completed")
    async def handle_order_completed(order):
        await process_payment(order)
    
    # Emit event
    await events.emit(
        "user.created",
        user_data
    )
```

### 4. Resource Management

```python
from pepperpy.resources import ResourceManager
from pepperpy.cache import CacheManager

async def setup_resources():
    # Create managers
    resources = ResourceManager()
    cache = CacheManager()
    
    # Configure cache
    await cache.configure(
        max_size=1000,
        ttl=3600
    )
    
    # Load resources
    templates = await resources.load(
        "templates/*.html",
        cache=cache
    )
```

## Module Documentation

### Core Modules
- [Task Management](modules/task.md)
- [Event System](modules/event.md)
- [Configuration](modules/config.md)
- [Logging](modules/logging.md)

### Data & Types
- [Types](modules/types.md)
- [Validation](modules/validation.md)
- [Serialization](modules/serialization.md)
- [Models](modules/models.md)

### Resources
- [Resource Management](modules/resources.md)
- [Cache](modules/cache.md)
- [Storage](modules/storage.md)
- [I/O Operations](modules/io.md)

### Security
- [Security](modules/security.md)
- [Authentication](modules/auth.md)
- [Authorization](modules/authz.md)

### Development
- [Development Tools](modules/dev.md)
- [Testing](modules/testing.md)
- [Debugging](modules/debug.md)

### Extensions
- [Plugin System](modules/plugin.md)
- [Registry](modules/registry.md)
- [Pipeline](modules/pipeline.md)

### Utilities
- [Utilities](modules/utils.md)
- [Network](modules/network.md)
- [Telemetry](modules/telemetry.md)

### Error Handling
- [Exceptions](modules/exceptions.md) - Exception hierarchy and types
- [Error Context](modules/exceptions.md#error-context) - Contextual error information
- [Exception Events](modules/exceptions.md#exception-events) - Error event handling

## Best Practices

### 1. Configuration Management

```python
from pepperpy.config import ConfigManager
from pepperpy.validation import ConfigValidator

async def setup_config():
    # Create manager
    config = ConfigManager()
    
    # Load configurations
    app_config = await config.load(
        "config/app.yaml",
        validate=True
    )
    
    # Validate schema
    validator = ConfigValidator()
    await validator.validate(
        app_config,
        schema="schemas/app.json"
    )
```

### 2. Error Handling

```python
from pepperpy.exceptions import (
    PepperpyError,
    ConfigError,
    ValidationError
)

async def safe_operation():
    try:
        # Perform operation
        result = await process_data()
        
    except ConfigError as e:
        # Handle configuration error
        logger.error(f"Config error: {e}")
        await notify_admin(e)
        
    except ValidationError as e:
        # Handle validation error
        logger.error(f"Validation error: {e}")
        raise HTTPError(400, str(e))
        
    except PepperpyError as e:
        # Handle general error
        logger.error(f"Operation failed: {e}")
        await handle_error(e)
```

### 3. Testing

```python
from pepperpy.testing import TestCase
from pepperpy.mock import MockManager

class UserTests(TestCase):
    async def setUp(self):
        # Setup mocks
        self.mock = MockManager()
        self.db = await self.mock.create_db()
        
    async def test_create_user(self):
        # Prepare data
        user_data = {
            "name": "Test User",
            "email": "test@example.com"
        }
        
        # Create user
        user = await create_user(
            self.db,
            user_data
        )
        
        # Assert result
        self.assertIsNotNone(user.id)
        self.assertEqual(user.name, user_data["name"])
```

## Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.