# Testing Module

The PepperPy Core Testing module provides utilities and base classes for testing, including support for asynchronous tests, mocks, fixtures, and custom assertions.

## Core Components

### AsyncTestCase

Base class for asynchronous tests:

```python
from pepperpy.testing import AsyncTestCase

class TestExample(AsyncTestCase):
    async def setUp(self):
        # Async setup
        self.client = await create_client()
    
    async def test_operation(self):
        # Async test
        result = await self.client.process()
        self.assertEqual(result.status, "success")
    
    async def tearDown(self):
        # Async cleanup
        await self.client.close()
```

### MockClient

```python
from pepperpy.testing import MockClient

class TestAPI(AsyncTestCase):
    def setUp(self):
        self.client = MockClient()
        
        # Configure mock responses
        self.client.mock_get(
            "/users/123",
            response={"id": "123", "name": "John"}
        )
    
    async def test_get_user(self):
        # Make request
        response = await self.client.get("/users/123")
        self.assertEqual(response["name"], "John")
```

### MockServer

```python
from pepperpy.testing import MockServer

class TestServer(AsyncTestCase):
    async def setUp(self):
        self.server = MockServer()
        await self.server.start()
        
        # Configure routes
        self.server.route("/ping", lambda: "pong")
    
    async def test_ping(self):
        # Make request
        response = await make_request(self.server.url + "/ping")
        self.assertEqual(response, "pong")
    
    async def tearDown(self):
        await self.server.stop()
```

### MockDatabase

```python
from pepperpy.testing import MockDatabase

class TestDatabase(AsyncTestCase):
    async def setUp(self):
        # Create connection
        self.db = MockDatabase()
        await self.db.connect()
        
        # Add test data
        await self.db.insert("users", {
            "id": "123",
            "name": "John"
        })
    
    async def test_query(self):
        # Check insertion
        user = await self.db.get("users", "123")
        self.assertEqual(user["name"], "John")
```

## Advanced Features

### Custom Assertions

```python
from pepperpy.testing import TestCase

class CustomTestCase(TestCase):
    def assertEventEmitted(self, event_name):
        """Assert that event was emitted."""
        events = self.get_emitted_events()
        self.assertIn(
            event_name,
            events,
            f"Event {event_name} was not emitted"
        )
    
    def assertStateChanged(self, path, expected):
        """Assert that state changed to expected value."""
        actual = self.get_state(path)
        self.assertEqual(
            actual,
            expected,
            f"State {path} did not change to {expected}"
        )
    
    def assertContextSet(self, context):
        """Assert that context was set."""
        current = self.get_context()
        self.assertEqual(
            current,
            context,
            f"Context {context} not set"
        )
```

### Test Fixtures

```python
from pepperpy.testing import fixture

@fixture
async def database():
    """Database fixture."""
    db = MockDatabase()
    await db.connect()
    
    yield db
    
    await db.disconnect()

@fixture
async def client(database):
    """API client fixture."""
    client = MockClient()
    client.db = database
    
    yield client
    
    await client.close()
```

## Best Practices

1. **Organization**
   - Group related tests
   - Use descriptive names
   - Follow AAA pattern
   - Keep tests focused

2. **Assertions**
   - Use specific assertions
   - Check edge cases
   - Validate errors
   - Test boundaries

3. **Mocking**
   - Mock external services
   - Simulate failures
   - Track metrics
   - Verify behavior

4. **Maintenance**
   - Remove duplication
   - Refactor code
   - Document changes
   - Keep tests clean

## Common Patterns

### Integration Tests

```python
from pepperpy.testing import IntegrationTest

class TestUserFlow(IntegrationTest):
    async def setUp(self):
        self.db = await self.fixture("database")
        self.client = await self.fixture("client")
    
    async def test_create_user(self):
        # Create user
        user = await self.client.create_user({
            "name": "John",
            "email": "john@example.com"
        })
        
        # Verify database
        stored = await self.db.get_user(user["id"])
        self.assertEqual(stored["email"], user["email"])
        
        # Verify events
        self.assertEventEmitted("user.created")
```

### Performance Tests

```python
from pepperpy.testing import PerformanceTest

class TestAPIPerformance(PerformanceTest):
    async def setUp(self):
        self.client = await self.fixture("client")
    
    @performance(
        requests=1000,
        concurrency=10,
        timeout=30
    )
    async def test_api_throughput(self):
        response = await self.client.get("/api/data")
        self.assertEqual(response.status, 200)
    
    def tearDown(self):
        stats = self.get_performance_stats()
        self.assertLess(stats.avg_latency, 100)
        self.assertGreater(stats.requests_per_sec, 50)
```

### Security Tests

```python
from pepperpy.testing import SecurityTest

class TestAPISecurity(SecurityTest):
    async def setUp(self):
        self.client = await self.fixture("client")
    
    async def test_authentication(self):
        # Test without token
        response = await self.client.get("/api/secure")
        self.assertEqual(response.status, 401)
        
        # Test with invalid token
        response = await self.client.get(
            "/api/secure",
            token="invalid"
        )
        self.assertEqual(response.status, 403)
        
        # Test with valid token
        response = await self.client.get(
            "/api/secure",
            token=self.valid_token
        )
        self.assertEqual(response.status, 200)
```

## API Reference

### TestCase

```python
class TestCase:
    async def setUp(self):
        """Set up test case."""
        
    async def tearDown(self):
        """Clean up test case."""
        
    def assertEqual(self, first, second, msg=None):
        """Assert that first equals second."""
        
    def assertRaises(self, exc_type, callable, *args, **kwargs):
        """Assert that callable raises exc_type."""
```

### MockClient

```python
class MockClient:
    def mock_get(self, url: str, response: Any):
        """Mock GET response."""
        
    def mock_post(self, url: str, response: Any):
        """Mock POST response."""
        
    def mock_error(self, url: str, error: Exception):
        """Mock error response."""
```

### Fixtures

```python
class Fixture:
    async def setup(self):
        """Set up fixture."""
        
    async def teardown(self):
        """Clean up fixture."""
        
    def __call__(self):
        """Get fixture value."""
``` 