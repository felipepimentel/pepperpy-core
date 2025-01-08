# Network Module

The PepperPy Core Network module provides an asynchronous interface for network operations, including HTTP requests, WebSockets, and connection management.

## Core Components

### AsyncHTTPClient

Asynchronous HTTP client:

```python
from pepperpy_core.network import AsyncHTTPClient

# Create client
client = AsyncHTTPClient()

# Make request
response = await client.get(
    "https://api.example.com/data"
)

# Process response
data = await response.json()
```

### AsyncWebSocket

Asynchronous WebSocket client:

```python
from pepperpy_core.network import AsyncWebSocket

async with AsyncWebSocket("wss://example.com") as ws:
    # Send message
    await ws.send({"type": "subscribe"})
    
    # Receive messages
    async for message in ws:
        await process_message(message)
```

### ConnectionManager

Connection manager:

```python
from pepperpy_core.network import ConnectionManager

manager = ConnectionManager()

# Add connection
conn = await manager.connect("example.com")

# Monitor connection
async for state in manager.watch(conn):
    print(f"State: {state}")
```

## Usage Examples

### HTTP Client

```python
from pepperpy_core.network import HTTPClient

# Create client with configuration
client = HTTPClient(
    base_url="https://api.example.com",
    timeout=30,
    retries=3
)

# GET with parameters
response = await client.get(
    "/users",
    params={"active": True}
)

# POST with JSON
response = await client.post(
    "/users",
    json={"name": "John"}
)
```

### WebSocket Client

```python
from pepperpy_core.network import WebSocket

class ChatClient(WebSocket):
    async def connect(self):
        await super().connect()
        await self.subscribe()
    
    async def subscribe(self):
        await self.send({
            "type": "subscribe",
            "channel": "chat"
        })
    
    async def on_message(self, message):
        await self.process_message(message)
```

### Connection Pool

```python
from pepperpy_core.network import ConnectionPool

pool = ConnectionPool(
    max_size=10,
    timeout=30
)

async with pool.acquire() as conn:
    await conn.execute(query)
```

## Advanced Features

### Rate Limiter

```python
from pepperpy_core.network import RateLimiter

class LimitedClient(HTTPClient):
    def __init__(self):
        super().__init__()
        self.limiter = RateLimiter(
            max_requests=100,
            window=60
        )
    
    async def cleanup(self):
        # Clean up old requests
        await self.limiter.cleanup()
    
    async def request(self, *args, **kwargs):
        if not await self.limiter.allow():
            raise RateLimitError(
                f"requests per {self.window}s exceeded"
            )
        
        # Record request
        self.limiter.record()
        
        return await super().request(
            *args,
            **kwargs
        )
```

### Retry Handler

```python
from pepperpy_core.network import RetryHandler

class RetryClient(HTTPClient):
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0
    ):
        super().__init__()
        self.max_retries = max_retries
        self.delay = delay
    
    async def request(self, *args, **kwargs):
        retries = 0
        while True:
            try:
                return await super().request(
                    *args,
                    **kwargs
                )
            except RequestError as e:
                retries += 1
                if retries >= self.max_retries:
                    raise RequestError(
                        f"Failed after {retries} attempts: {last_error}"
                    )
                await asyncio.sleep(self.delay)
```

## Best Practices

1. **Connection Management**
   - Use connection pools
   - Close connections
   - Handle timeouts
   - Monitor usage

2. **WebSocket**
   - Monitor connection
   - Handle reconnection
   - Implement heartbeat
   - Handle backoff

3. **Security**
   - Use HTTPS
   - Validate certificates
   - Secure WebSockets
   - Handle authentication

4. **Performance**
   - Monitor latency
   - Use connection pooling
   - Implement caching
   - Handle backpressure

5. **Resilience**
   - Implement retry
   - Handle failures
   - Monitor health
   - Use circuit breakers

## Common Patterns

### HTTP Client with Retry

```python
from pepperpy_core.network import RetryClient

class APIClient(RetryClient):
    def __init__(self):
        super().__init__(
            max_retries=3,
            delay=1.0
        )
    
    async def get_user(self, user_id: str):
        # Make request
        response = await self.get(
            f"/users/{user_id}"
        )
        
        return await response.json()
```

### Batch Request Handler

```python
from pepperpy_core.network import BatchHandler

class BatchClient(HTTPClient):
    def __init__(self):
        super().__init__()
        self.batch = BatchHandler(
            max_size=100,
            timeout=1.0
        )
    
    async def request(self, *args, **kwargs):
        # Add to batch
        future = self.batch.add(
            args,
            kwargs
        )
        
        # Wait for result
        return await future
```

### Client with Metrics

```python
from pepperpy_core.network import MetricsClient

class MonitoredClient(MetricsClient):
    async def request(self, *args, **kwargs):
        # Start timer
        with self.timer("request"):
            try:
                # Make request
                response = await super().request(
                    *args,
                    **kwargs
                )
                
                # Record success
                self.record_success()
                
                return response
            except Exception as e:
                # Record failure
                self.record_failure(str(e))
                raise
```

## API Reference

### HTTPClient

```python
class HTTPClient:
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Response:
        """Make HTTP request."""
        
    async def get(
        self,
        url: str,
        **kwargs
    ) -> Response:
        """Make GET request."""
        
    async def post(
        self,
        url: str,
        **kwargs
    ) -> Response:
        """Make POST request."""
```

### WebSocket

```python
class WebSocket:
    async def connect(self):
        """Connect to server."""
        
    async def send(
        self,
        message: Any
    ):
        """Send message."""
        
    async def receive(self) -> Any:
        """Receive message."""
```

### ConnectionPool

```python
class ConnectionPool:
    async def acquire(self) -> Connection:
        """Acquire connection."""
        
    async def release(
        self,
        conn: Connection
    ):
        """Release connection."""
        
    async def close(self):
        """Close all connections."""
```
``` 