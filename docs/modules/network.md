# Network Module

The PepperPy Network module provides robust networking capabilities for both low-level TCP/IP connections and high-level HTTP requests. It includes features for connection management, request retries, rate limiting, and response handling.

## HTTP Client

The HTTP client provides a high-level interface for making HTTP requests with features like:

- Base URL and default headers
- Automatic retries with configurable delay
- Rate limiting
- Response format handling (JSON, Text, Bytes)
- SSL verification control
- Proxy support
- Logging integration
- Status code handling
- Form data support
- Request/Response interceptors

### Basic Usage

```python
from pepperpy.network import HTTPClient, HTTPConfig, ResponseFormat

# Create client with configuration
config = HTTPConfig(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token"},
    timeout=30.0,
    retries=3,
    retry_delay=1.0,
    verify_ssl=True,
    response_format=ResponseFormat.JSON,
    raise_for_status=True,
    max_rate_limit=100  # requests per second
)

async with HTTPClient(config) as client:
    # GET request with JSON response
    data = await client.get("/users")
    
    # POST request with custom headers
    response = await client.post(
        "/users",
        json={"name": "John Doe"},
        headers={"X-Custom": "value"}
    )
    
    # GET request with text response
    text = await client.get(
        "/status",
        response_format=ResponseFormat.TEXT
    )
    
    # PUT request with retry configuration
    result = await client.put(
        "/items/123",
        json={"status": "active"},
        retries=5,
        retry_delay=2.0
    )
```

### Configuration

The `HTTPConfig` class allows customization of client behavior:

```python
@dataclass
class HTTPConfig:
    base_url: str = ""              # Base URL for all requests
    headers: dict[str, str] = None  # Default headers
    timeout: float = 30.0           # Request timeout in seconds
    retries: int = 3               # Number of retry attempts
    retry_delay: float = 1.0       # Delay between retries
    verify_ssl: bool = True        # SSL certificate verification
    response_format: ResponseFormat = ResponseFormat.JSON  # Default response format
    raise_for_status: bool = True  # Raise exception for error status codes
    max_rate_limit: int = 0        # Max requests per second (0 = no limit)
    interceptors: list[RequestInterceptor] = []  # Request/Response interceptors
```

### Response Formats

The client supports multiple response formats through the `ResponseFormat` enum:

```python
class ResponseFormat(str, Enum):
    JSON = "json"   # Parse response as JSON
    TEXT = "text"   # Return raw text
    BYTES = "bytes" # Return bytes data
```

### Advanced Features

#### Status Code Handling

```python
# Configure status code handling
config = HTTPConfig(
    base_url="https://api.example.com",
    raise_for_status=True  # Raise NetworkError for non-2xx status codes
)

try:
    await client.get("/not-found")
except NetworkError as e:
    print(f"Request failed: {e}")  # Request failed with status 404: Not Found
```

#### Form Data

```python
from aiohttp import FormData

# Create form data
form = FormData()
form.add_field("file", open("image.jpg", "rb"))
form.add_field("description", "Profile picture")

# Send multipart request
response = await client.post("/upload", data=form)
```

#### Request Interceptors

```python
from dataclasses import dataclass
from aiohttp import ClientResponse
from pepperpy.network import RequestInterceptor

@dataclass
class LoggingInterceptor(RequestInterceptor):
    """Log all requests and responses."""
    
    async def pre_request(
        self,
        method: str,
        url: str,
        **kwargs: Any
    ) -> None:
        print(f"Making {method} request to {url}")
    
    async def post_response(self, response: ClientResponse) -> None:
        print(f"Got response with status {response.status}")

# Configure client with interceptor
config = HTTPConfig(
    base_url="https://api.example.com",
    interceptors=[LoggingInterceptor()]
)
```

#### Rate Limiting

```python
# Create client with rate limit
config = HTTPConfig(max_rate_limit=100)  # 100 requests per second
client = HTTPClient(config)

# Client will automatically handle rate limiting
for i in range(1000):
    await client.get("/endpoint")  # Requests are throttled
```

#### Request Retries

```python
# Configure retries per request
response = await client.post(
    "/endpoint",
    json=data,
    retries=5,           # Override default retries
    retry_delay=2.0      # Wait 2 seconds between retries
)
```

#### Custom Headers

```python
# Set default headers in config
config = HTTPConfig(
    headers={
        "Authorization": "Bearer token",
        "User-Agent": "PepperPy/1.0"
    }
)

# Override or add headers per request
response = await client.get(
    "/endpoint",
    headers={
        "X-Custom": "value",  # Add custom header
        "Authorization": "Bearer new-token"  # Override default
    }
)
```

#### Proxy Support

```python
# Use proxy for request
response = await client.get(
    "/endpoint",
    proxy="http://proxy.example.com:8080"
)
```

## Error Handling

The client provides comprehensive error handling:

```python
from pepperpy.network import NetworkError

try:
    response = await client.get("/endpoint")
except NetworkError as e:
    print(f"Request failed: {e}")
    if e.__cause__:
        print(f"Caused by: {e.__cause__}")
```

## Best Practices

1. **Use Context Managers**
   ```python
   async with HTTPClient(config) as client:
       await client.get("/endpoint")
   ```

2. **Configure Timeouts**
   ```python
   config = HTTPConfig(timeout=30.0)
   ```

3. **Handle Rate Limits**
   ```python
   config = HTTPConfig(max_rate_limit=100)
   ```

4. **Use Retries for Reliability**
   ```python
   config = HTTPConfig(retries=3, retry_delay=1.0)
   ```

5. **Validate SSL Certificates**
   ```python
   config = HTTPConfig(verify_ssl=True)
   ```

6. **Log Network Operations**
   ```python
   # Client inherits from LoggerMixin
   client.logger.debug("Making request...")
   ```

7. **Use Interceptors for Cross-Cutting Concerns**
   ```python
   config = HTTPConfig(interceptors=[
       LoggingInterceptor(),
       MetricsInterceptor(),
       AuthInterceptor()
   ])
   ```

8. **Handle Status Codes**
   ```python
   config = HTTPConfig(raise_for_status=True)
   ```

## Common Patterns

### API Client

```python
class APIClient:
    def __init__(self, api_key: str):
        self.config = HTTPConfig(
            base_url="https://api.example.com",
            headers={"Authorization": f"Bearer {api_key}"},
            response_format=ResponseFormat.JSON,
            raise_for_status=True,
            interceptors=[LoggingInterceptor()]
        )
        self.client = HTTPClient(self.config)
    
    async def get_user(self, user_id: int) -> dict:
        return await self.client.get(f"/users/{user_id}")
    
    async def create_user(self, user_data: dict) -> dict:
        return await self.client.post("/users", json=user_data)
```

### Batch Operations

```python
async def batch_process(urls: list[str]) -> list[dict]:
    async with HTTPClient() as client:
        tasks = [client.get(url) for url in urls]
        return await asyncio.gather(*tasks)
```

### Error Retry

```python
async def retry_operation(client: HTTPClient) -> dict:
    return await client.get(
        "/flaky-endpoint",
        retries=5,
        retry_delay=2.0,
        raise_for_status=True
    )
```

### File Upload

```python
async def upload_file(client: HTTPClient, file_path: str) -> dict:
    form = FormData()
    form.add_field("file", open(file_path, "rb"))
    return await client.post("/upload", data=form)
```

### Authentication

```python
@dataclass
class AuthInterceptor(RequestInterceptor):
    """Add authentication to all requests."""
    
    token: str
    
    async def pre_request(self, method: str, url: str, headers: dict, **kwargs: Any) -> None:
        headers["Authorization"] = f"Bearer {self.token}"

config = HTTPConfig(
    base_url="https://api.example.com",
    interceptors=[AuthInterceptor(token="secret")]
)
``` 