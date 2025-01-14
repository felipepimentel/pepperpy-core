# Network Module

The PepperPy Core Network module provides asynchronous network clients for both TCP and HTTP protocols, with support for connection management, retries, and proper resource cleanup.

## Core Components

### NetworkConfig

Configuration for TCP network client:

```python
from pepperpy.network import NetworkConfig

# Create configuration
config = NetworkConfig(
    host="localhost",
    port=8000,
    timeout=5.0,
    retries=3,
    retry_delay=1.0
)
```

### NetworkClient

TCP client implementation:

```python
from pepperpy.network import NetworkClient

# Create client
client = NetworkClient(config)

# Use with context manager
async with client:
    # Send data
    await client.send(b"Hello")
    
    # Receive data
    data = await client.receive(1024)
```

### HTTPClient

HTTP client implementation:

```python
from pepperpy.network import HTTPClient

# Create client
async with HTTPClient() as client:
    # Make GET request
    response = await client.get(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer token"}
    )
    
    # Make POST request with JSON
    response = await client.post(
        "https://api.example.com/users",
        json={
            "str_value": "test",
            "int_value": 123
        }
    )
```

## Usage Examples

### TCP Client

```python
from pepperpy.network import NetworkClient, NetworkConfig

async def handle_connection():
    config = NetworkConfig(
        host="localhost",
        port=8000
    )
    
    async with NetworkClient(config) as client:
        # Send request
        await client.send(b"GET /data\n")
        
        # Receive response
        response = await client.receive(1024)
        print(f"Received: {response}")
```

### HTTP Client

```python
from pepperpy.network import HTTPClient
from aiohttp import ClientTimeout

async def make_requests():
    async with HTTPClient() as client:
        # GET request with parameters
        response = await client.get(
            "https://api.example.com/search",
            params={"q": "test"},
            timeout=ClientTimeout(total=30)
        )
        
        # POST request with JSON data
        response = await client.post(
            "https://api.example.com/users",
            json={
                "str_value": "john",
                "int_value": 30,
                "bool_value": True
            }
        )
        
        # PUT request
        response = await client.put(
            "https://api.example.com/users/123",
            json={"str_value": "john.doe"}
        )
        
        # DELETE request
        response = await client.delete(
            "https://api.example.com/users/123"
        )
```

## Advanced Features

### Request Data Typing

```python
from pepperpy.network import RequestData

# Type-safe request data
data: RequestData = {
    "str_value": "test",
    "int_value": 123,
    "float_value": 3.14,
    "bool_value": True,
    "list_value": ["a", 1, 2.0, True],
    "dict_value": {"key": "value"}
}
```

### Proxy Support

```python
from pepperpy.network import HTTPClient

async with HTTPClient() as client:
    # Use proxy
    response = await client.get(
        "https://api.example.com/data",
        proxy="http://proxy.example.com:8080"
    )
```

### SSL Verification

```python
from pepperpy.network import HTTPClient

async with HTTPClient() as client:
    # Disable SSL verification
    response = await client.get(
        "https://api.example.com/data",
        verify_ssl=False
    )
```

## Best Practices

1. **Resource Management**
   - Use context managers
   - Close connections
   - Handle cleanup
   - Monitor resources

2. **Error Handling**
   - Handle network errors
   - Implement retries
   - Log failures
   - Provide context

3. **Security**
   - Verify SSL
   - Use HTTPS
   - Validate hosts
   - Handle timeouts

4. **Performance**
   - Reuse connections
   - Configure timeouts
   - Monitor latency
   - Handle backpressure

## API Reference

### NetworkClient

```python
class NetworkClient:
    async def connect(self) -> None:
        """Connect to server."""
        
    async def disconnect(self) -> None:
        """Disconnect from server."""
        
    async def send(self, data: bytes) -> None:
        """Send data to server."""
        
    async def receive(self, size: int) -> bytes:
        """Receive data from server."""
```

### HTTPClient

```python
class HTTPClient:
    async def get(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        proxy: str = None,
        timeout: ClientTimeout = None,
        verify_ssl: bool = True
    ) -> str:
        """Send GET request."""
        
    async def post(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        proxy: str = None,
        timeout: ClientTimeout = None,
        verify_ssl: bool = True,
        json: RequestData = None
    ) -> str:
        """Send POST request."""
```

### Error Handling

```python
try:
    async with HTTPClient() as client:
        response = await client.get("https://api.example.com")
except NetworkError as e:
    print(f"Network error: {e}")
```
``` 