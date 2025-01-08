# PepperPy Core

PepperPy Core is a comprehensive Python utility library designed to accelerate development by providing essential core capabilities. It offers a robust foundation for building scalable, maintainable, and secure Python applications.

## Features

- **Task Management**: Asynchronous task execution with priority queuing
- **Event System**: Flexible event-driven architecture
- **Plugin System**: Extensible plugin architecture
- **Security**: Built-in security features and validation
- **Logging**: Advanced structured logging
- **Configuration**: Flexible configuration management
- **I/O Operations**: Async-first I/O utilities
- **Network Operations**: Robust networking capabilities
- **Resource Management**: Efficient resource handling
- **Telemetry**: Built-in monitoring capabilities
- **Type Safety**: Full type hints support

## Installation

```bash
pip install pepperpy-core
```

Or with Poetry (recommended):

```bash
poetry add pepperpy-core
```

## Quick Start

```python
from pepperpy_core import Task, Event, Logger

# Configure logging
logger = Logger("my_app")
logger.info("Starting application")

# Create and execute a task
@Task.register
async def process_data(data: dict) -> dict:
    logger.debug("Processing data", data=data)
    # Process your data
    return processed_data

# Execute the task
result = await process_data.execute({"input": "data"})

# Emit an event
event = Event("data_processed", {"status": "success"})
await event_bus.emit(event)
```

## Core Modules

### [Task System](docs/modules/task.md)
Asynchronous task management with features like:
- Priority-based execution
- Task cancellation
- Worker pools
- Task chaining

### [Event System](docs/modules/event.md)
Event-driven architecture supporting:
- Event emission and handling
- Priority-based listeners
- Event metadata
- Async event processing

### [Plugin System](docs/modules/plugin.md)
Extensible plugin architecture with:
- Dynamic plugin loading
- Plugin lifecycle management
- Plugin configuration
- Hook system

### [Security System](docs/modules/security.md)
Comprehensive security features including:
- Authentication
- Input validation
- Security contexts
- Validation chains

### [Logging System](docs/modules/logging.md)
Advanced logging capabilities with:
- Structured logging
- Multiple handlers
- Log levels
- Context-aware logging

### [Configuration System](docs/modules/config.md)
Flexible configuration management with:
- Hierarchical configuration
- Configuration validation
- Environment-based settings
- Dynamic updates

### [I/O Operations](docs/modules/io.md)
Async-first I/O utilities supporting:
- File operations
- Multiple formats
- Streaming
- Resource management

### [Network Operations](docs/modules/network.md)
Robust networking capabilities including:
- Async TCP/IP communication
- Connection pooling
- Retry handling
- Load balancing

## Development

### Prerequisites

- Python 3.12+
- Poetry for dependency management

### Setup

1. Clone the repository:
```bash
git clone https://github.com/felipepimentel/pepperpy-core.git
cd pepperpy-core
```

2. Install dependencies:
```bash
poetry install
```

3. Run tests:
```bash
poetry run pytest
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Structure

```
pepperpy-core/
├── pepperpy_core/        # Core package
│   ├── task.py          # Task management
│   ├── event.py         # Event system
│   ├── plugin.py        # Plugin system
│   ├── security.py      # Security features
│   ├── logging.py       # Logging system
│   ├── config.py        # Configuration system
│   ├── io.py           # I/O operations
│   ├── network.py      # Network operations
│   └── ...
├── tests/               # Test suite
├── docs/                # Documentation
│   └── modules/         # Module documentation
├── examples/            # Usage examples
└── scripts/             # Development scripts
```

## Best Practices

- Use type hints consistently
- Write comprehensive tests
- Follow PEP 8 guidelines
- Document your code
- Handle errors gracefully

## Support

- Issue Tracker: [GitHub Issues](https://github.com/felipepimentel/pepperpy-core/issues)
- Documentation: [Project Documentation](docs/index.md)
- Discussion: [GitHub Discussions](https://github.com/felipepimentel/pepperpy-core/discussions)

## Acknowledgments

- The Python community
- All contributors who have helped shape this project
- Open source projects that have inspired this work
