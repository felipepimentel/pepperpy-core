# Event Module

The PepperPy Core event system provides a robust and flexible implementation for event-based communication, with support for advanced patterns such as pub/sub, event sourcing, and asynchronous processing.

## Basic Usage

```python
from pepperpy.event import EventManager

# Create event manager
manager = EventManager()

# Subscribe to event
@manager.on("user.created")
async def handle_user_created(event):
    print(f"New user: {event.data['name']}")

# Create advanced manager with configuration
manager = EventManager(
    max_listeners=100,
    buffer_size=1000,
    retry_policy=RetryPolicy.EXPONENTIAL
)

# Emit event
await manager.emit("user.created", {
    "id": "123",
    "name": "John"
})
```

## Event Bus

```python
from pepperpy.event import EventBus

# Create bus with topics
bus = EventBus([
    "users.*",
    "orders.*",
    "system.*"
])

# Subscribe to pattern
@bus.subscribe("users.*")
async def handle_user_events(event):
    print(f"User event: {event.type}")

# Publish event
await bus.publish("users.login", {
    "user_id": "123",
    "timestamp": "2023-01-01T12:00:00Z"
})
```

## Usage Patterns

### Event Sourcing

```python
from pepperpy.event import EventStore

# Create store
store = EventStore()

# Store event
await store.append("user.123", {
    "type": "PasswordChanged",
    "data": {"new_hash": "abc123"}
})

# Get event stream
events = await store.get_stream("user.123")
for event in events:
    print(f"Event: {event.type}")
```

### Event Processing

```python
from pepperpy.event import EventProcessor

# Create processor
processor = EventProcessor()

# Add middleware
@processor.middleware
async def add_timestamp(event, next_handler):
    event.metadata["processed_at"] = time.time()
    await next_handler(event)

# Add handler
@processor.handle("user.*")
async def process_user_events(event):
    user_id = event.data["user_id"]
    await update_user(user_id, event.data)
```

### Event Metrics

```python
from pepperpy.event import MetricsCollector

# Create collector
collector = MetricsCollector()

# Register metrics
@collector.measure("event_processing")
async def handle_event(event):
    await process_event(event)

# Get metrics
metrics = collector.get_metrics()
print(f"Average latency: {metrics.avg_latency}ms")
print(f"Events/sec: {metrics.throughput}")
```

## Best Practices

1. **Event Design**
   - Use immutable events
   - Include useful metadata
   - Version events
   - Document schema

2. **Performance**
   - Batch when possible
   - Optimize serialization
   - Cache when possible
   - Use async handlers

3. **Monitoring**
   - Collect metrics
   - Track failures
   - Monitor latency
   - Alert on issues

4. **Security**
   - Validate events
   - Encrypt sensitive data
   - Control access
   - Audit changes

## Common Patterns

### 1. Notification System

```python
from pepperpy.event import NotificationSystem

# Create system
notifications = NotificationSystem()

# Add channels
notifications.add_channel("email")
notifications.add_channel("push")
notifications.add_channel("sms")

# Subscribe to notifications
@notifications.on("user.signup")
async def send_welcome(event):
    user = event.data["user"]
    await notifications.notify(
        channels=["email"],
        template="welcome",
        user=user
    )
```

### 2. Event Replay

```python
from pepperpy.event import EventReplay

# Create replay system
replay = EventReplay(store)

# Configure handlers
@replay.handle("user.*")
async def rebuild_user_state(event):
    user_id = event.data["user_id"]
    await update_user_state(user_id, event)

# Replay events
await replay.replay_stream(
    "user.123",
    start_time="2023-01-01T00:00:00Z"
)
```

### 3. Event Validation

```python
from pepperpy.event import EventValidator

# Create validator
validator = EventValidator()

# Define schema
@validator.schema("user.created")
class UserCreatedSchema:
    user_id: str
    name: str
    email: str

# Validate event
try:
    event = await validator.validate(
        "user.created",
        event_data
    )
except ValidationError as e:
    print(f"Invalid event: {e}")
```

## API Reference

### Event Manager

```python
class EventManager:
    async def emit(
        self,
        event_type: str,
        data: dict,
        metadata: dict = None
    ) -> None:
        """Emit an event."""
        
    def on(
        self,
        event_type: str
    ) -> Callable:
        """Subscribe to event."""
        
    async def off(
        self,
        event_type: str,
        handler: Callable
    ) -> None:
        """Unsubscribe from event."""
```

### Event Bus

```python
class EventBus:
    async def publish(
        self,
        topic: str,
        message: Any
    ) -> None:
        """Publish to topic."""
        
    def subscribe(
        self,
        pattern: str
    ) -> Callable:
        """Subscribe to pattern."""
```

### Event Store

```python
class EventStore:
    async def append(
        self,
        stream: str,
        event: dict
    ) -> None:
        """Append to stream."""
        
    async def get_stream(
        self,
        stream: str,
        start_pos: int = 0
    ) -> AsyncIterator[dict]:
        """Get event stream."""
``` 