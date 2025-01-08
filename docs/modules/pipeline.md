# Pipeline Module

The PepperPy Core Pipeline module provides a framework for creating and executing processing pipelines, allowing operations to be chained together flexibly and efficiently.

## Core Components

### BasePipeline

Base class for defining pipelines:

```python
from pepperpy_core.pipeline import Pipeline

class DataPipeline(Pipeline):
    async def process(self, data: dict) -> dict:
        # Validate input
        if not self._validate(data):
            raise ValidationError("Invalid data")
            
        # Transform data
        result = await self._transform(data)
        
        # Return result
        return result
    
    def _validate(self, data: dict) -> bool:
        # Implement validation
        return True
    
    async def _transform(self, data: dict) -> dict:
        # Transform data
        return data
```

## Usage Examples

### Basic Pipeline

```python
from pepperpy_core.pipeline import Pipeline

class UserPipeline(Pipeline):
    async def process(self, user: dict) -> dict:
        # Validate
        self.validate_user(user)
        
        # Transform
        user = await self.normalize_user(user)
        
        # Enrich
        user = await self.enrich_user(user)
        
        return user
```

### Branching Pipeline

```python
from pepperpy_core.pipeline import BranchingPipeline

class DataProcessor(BranchingPipeline):
    async def process(self, data: dict) -> dict:
        # Process user data
        if "user" in data:
            data["user"] = await self.process_user(
                data["user"]
            )
            
        # Process order data
        if "order" in data:
            data["order"] = await self.process_order(
                data["order"]
            )
            
        return data
    
    def configure(self):
        # Configure specific pipelines
        self.add_pipeline(
            "user",
            UserPipeline()
        )
        self.add_pipeline(
            "order",
            OrderPipeline()
        )
```

## Advanced Features

### Pipeline with Retry

```python
from pepperpy_core.pipeline import RetryPipeline

class APIProcessor(RetryPipeline):
    def __init__(self):
        super().__init__(
            max_retries=3,
            retry_delay=1.0
        )
    
    async def process(self, data: dict) -> dict:
        try:
            return await self.api_call(data)
        except APIError as e:
            if self.should_retry(e):
                return await self.retry(data)
            raise
```

### Pipeline with Cache

```python
from pepperpy_core.pipeline import CachedPipeline

class DataProcessor(CachedPipeline):
    def __init__(self):
        super().__init__(
            cache_size=1000,
            ttl=300
        )
    
    def cache_key(self, data: dict) -> str:
        return f"{data['type']}:{data['id']}"
    
    async def process(self, data: dict) -> dict:
        # Check cache
        key = self.cache_key(data)
        if self.in_cache(key):
            return self.get_cached(key)
        
        # Process data
        result = await self.process_data(data)
        
        # Cache result
        self.cache_result(key, result)
        
        return result
```

## Best Practices

1. **Design**
   - Keep pipelines focused
   - Implement validations
   - Handle errors gracefully
   - Document steps

2. **Error Handling**
   - Handle failures gracefully
   - Allow recovery
   - Log errors
   - Provide context

3. **Performance**
   - Use cache when possible
   - Batch operations
   - Monitor execution time
   - Profile bottlenecks

4. **Maintenance**
   - Monitor execution
   - Track metrics
   - Document changes
   - Keep tests updated

5. **Extensibility**
   - Design for extension
   - Allow customization
   - Support plugins
   - Use interfaces

## Common Patterns

### Pipeline with Validation

```python
from pepperpy_core.pipeline import ValidationPipeline

class DataValidator(ValidationPipeline):
    def __init__(self):
        super().__init__([
            TypeValidator(),
            SchemaValidator(),
            BusinessValidator()
        ])
    
    async def process(self, data: dict) -> dict:
        # Run all validators
        for validator in self.validators:
            if not await validator.validate(data):
                raise ValidationError(
                    f"Validation failed: {validator.__name__}"
                )
        
        return data
```

### Pipeline with Metrics

```python
from pepperpy_core.pipeline import MetricsPipeline

class MonitoredPipeline(MetricsPipeline):
    async def process(self, data: dict) -> dict:
        # Start timer
        with self.timer("process"):
            # Process data
            result = await super().process(data)
            
            # Record metrics
            self.record_metric(
                "items_processed",
                len(result)
            )
            
            return result
```

### Pipeline with Logging

```python
from pepperpy_core.pipeline import LoggedPipeline

class AuditedPipeline(LoggedPipeline):
    async def process(self, data: dict) -> dict:
        # Log input
        self.log.info(
            "Processing data",
            input=data
        )
        
        try:
            # Process data
            result = await super().process(data)
            
            # Log success
            self.log.info(
                "Processing complete",
                output=result
            )
            
            return result
        except Exception as e:
            # Log error
            self.log.error(
                "Processing failed",
                error=str(e)
            )
            raise
```

## API Reference

### Base Pipeline

```python
class Pipeline:
    async def process(self, data: Any) -> Any:
        """Process data through pipeline."""
        
    def validate(self, data: Any) -> bool:
        """Validate input data."""
        
    async def cleanup(self):
        """Clean up resources."""
```

### Pipeline Options

```python
class PipelineOptions:
    retry: bool = False
    cache: bool = False
    validate: bool = True
    log: bool = True
    metrics: bool = False
    timeout: float = 30.0
```

### Pipeline Events

The pipeline module emits the following events:

- `pipeline.start` - When processing starts
- `pipeline.complete` - When processing completes
- `pipeline.error` - When an error occurs
- `pipeline.retry` - When a retry occurs

### Error Handling

```python
try:
    result = await pipeline.process(data)
except ValidationError as e:
    logger.error(f"Validation error: {e}")
except ProcessingError as e:
    logger.error(f"Processing error: {e}")
except PipelineTimeout as e:
    logger.error(f"Pipeline timeout: {e}")
``` 