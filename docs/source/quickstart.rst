Quickstart Guide
===============

This guide will help you get started with PepperPy Core quickly.

Basic Usage
----------

1. Install PepperPy Core:

   .. code-block:: bash

      pip install pepperpy-core

2. Create a basic application:

   .. code-block:: python

      from pepperpy import Registry, Event

      # Initialize registry
      registry = Registry()
      await registry.initialize()

      # Create and emit events
      event = Event("user.created", {"id": 1, "name": "John"})
      await registry.emit(event)

Event System
-----------

The event system allows components to communicate through events:

.. code-block:: python

    from pepperpy import Event, EventHandler

    # Define an event handler
    class UserCreatedHandler(EventHandler):
        async def handle(self, event: Event) -> None:
            print(f"User created: {event.data}")

    # Register the handler
    registry.register_handler("user.created", UserCreatedHandler())

Plugin System
-----------

Extend functionality through plugins:

.. code-block:: python

    from pepperpy import Plugin, PluginConfig

    class UserPlugin(Plugin):
        def __init__(self):
            super().__init__(PluginConfig(name="user_plugin"))

        async def setup(self) -> None:
            # Plugin initialization
            pass

        async def cleanup(self) -> None:
            # Plugin cleanup
            pass

Task Management
-------------

Handle background tasks efficiently:

.. code-block:: python

    from pepperpy import Task, TaskConfig

    # Create a task
    async def background_job():
        # Task logic
        pass

    task = Task(
        TaskConfig(name="background_job"),
        background_job
    )

    # Start the task
    await registry.start_task(task)

Next Steps
---------

- Explore the :doc:`api/index` for detailed documentation
- Check out the examples in the repository
- Join our community for support 