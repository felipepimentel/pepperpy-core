Overview
========

PepperPy Core is a powerful Python library for building event-driven applications. It provides a robust foundation for creating modular, extensible, and type-safe applications.

Key Features
-----------

Event System
~~~~~~~~~~~
The event system is the heart of PepperPy Core. It enables loose coupling between components through an event-driven architecture:

- Asynchronous event emission and handling
- Type-safe event data
- Event prioritization and filtering
- Event history and replay capabilities

Plugin System
~~~~~~~~~~~~
The plugin system allows for modular application design:

- Hot-pluggable components
- Dependency injection
- Lifecycle management
- Plugin configuration
- Plugin isolation

Task Management
~~~~~~~~~~~~~
Robust task management capabilities:

- Async task execution
- Task prioritization
- Resource management
- Error handling
- Task cancellation
- Task dependencies

Type Safety
~~~~~~~~~~
Strong emphasis on type safety:

- Full type hints coverage
- Runtime type checking
- Type-safe event data
- MyPy compatibility
- Type-safe plugin interfaces

Architecture
-----------

Core Components
~~~~~~~~~~~~~

1. Core
    - Central orchestrator
    - Event dispatch
    - Plugin management
    - Task scheduling

2. Event System
    - Event creation
    - Event dispatch
    - Event handling
    - Event filtering

3. Plugin System
    - Plugin loading
    - Plugin lifecycle
    - Plugin configuration
    - Plugin communication

4. Task System
    - Task creation
    - Task scheduling
    - Task monitoring
    - Resource management

Design Principles
---------------

1. Modularity
    - Loose coupling
    - High cohesion
    - Pluggable architecture
    - Clear interfaces

2. Type Safety
    - Static typing
    - Runtime checks
    - Type-safe interfaces
    - Type documentation

3. Performance
    - Async by default
    - Resource efficient
    - Minimal overhead
    - Scalable design

4. Extensibility
    - Plugin system
    - Event system
    - Custom handlers
    - Extension points

Best Practices
------------

1. Event Design
    - Use meaningful event names
    - Include necessary context
    - Consider event ordering
    - Handle failures gracefully

2. Plugin Development
    - Single responsibility
    - Clear dependencies
    - Proper cleanup
    - Error handling

3. Task Management
    - Appropriate priorities
    - Resource constraints
    - Error handling
    - Cleanup routines

4. Error Handling
    - Specific exceptions
    - Proper logging
    - Recovery strategies
    - User feedback

Getting Started
-------------

Check out our :doc:`quickstart` guide to begin using PepperPy Core.

For more detailed information, visit the :doc:`api/index`. 