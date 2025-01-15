Quickstart Guide
==============

This guide will help you get started with PepperPy Core quickly.

Basic Usage
----------

Here's a simple example of using PepperPy Core:

.. code-block:: python

    from pepperpy import Core, Event, Plugin

    # Create a core instance
    core = Core()

    # Define a plugin
    class MyPlugin(Plugin):
        async def on_start(self):
            print("Plugin started!")
            
        async def on_event(self, event: Event):
            if event.name == "greet":
                print(f"Hello, {event.data['name']}!")

    # Register and start the plugin
    core.register_plugin(MyPlugin())
    
    # Run the core
    await core.start()
    
    # Emit an event
    await core.emit_event(Event("greet", {"name": "World"}))

Event System
-----------

Events are the core communication mechanism:

.. code-block:: python

    from pepperpy import Event

    # Create an event
    event = Event(
        name="user_login",
        data={"user_id": "123", "username": "john_doe"}
    )

    # Emit the event
    await core.emit_event(event)

Plugin System
-----------

Plugins are the main way to extend functionality:

.. code-block:: python

    from pepperpy import Plugin, Event

    class AuthPlugin(Plugin):
        async def on_start(self):
            # Plugin initialization
            self.users = {}

        async def on_event(self, event: Event):
            if event.name == "user_login":
                await self.authenticate_user(event.data)

        async def authenticate_user(self, data):
            # Authentication logic here
            pass

Task Management
-------------

PepperPy Core includes a task management system:

.. code-block:: python

    from pepperpy import Task

    # Create a task
    async def my_task():
        while True:
            print("Task running...")
            await asyncio.sleep(1)

    # Register the task
    task = Task(my_task)
    core.register_task(task)

Next Steps
---------

- Check out the :doc:`api/index` for detailed documentation
- Read about :doc:`advanced topics <advanced>` for more features
- Join our community for support and discussions 