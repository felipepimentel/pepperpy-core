# PepperPy Core Documentation

PepperPy Core is a powerful utility library designed to accelerate Python project development by providing essential core capabilities and abstractions. This library serves as the foundation for building robust, scalable, and maintainable Python applications.

## Key Features

- **Task Management**: Robust task handling and execution system
- **Event System**: Flexible event-driven architecture
- **Security**: Built-in security features and utilities
- **Logging**: Advanced structured logging capabilities
- **Configuration**: Flexible configuration management
- **I/O Operations**: Async-first I/O utilities
- **Plugin System**: Extensible plugin architecture
- **Resource Management**: Efficient resource handling
- **Telemetry**: Built-in telemetry and monitoring
- **Type Safety**: Full type hints support with strict mypy checking

## Quick Start

```python
from pepperpy_core import Task, Event, Config

# Initialize configuration
config = Config.from_yaml("config.yaml")

# Create a task
@Task.register
async def process_data(data: dict) -> dict:
    # Process your data
    return processed_data

# Create an event
event = Event("data_processed", payload={"status": "success"})

# Execute the task
result = await process_data.execute({"input": "data"})
```

## Installation

```bash
pip install pepperpy-core
```

Or with Poetry (recommended):

```bash
poetry add pepperpy-core
```

## Project Structure

The library is organized into several core modules:

- `task.py`: Task management and execution
- `event.py`: Event system implementation
- `config.py`: Configuration management
- `logging.py`: Structured logging utilities
- `security.py`: Security features
- And more...

## Requirements

- Python 3.12+
- Dependencies managed via Poetry

## Contributing

We welcome contributions! Please check our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 