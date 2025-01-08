# Task Module

## Overview

The task module provides a robust system for managing and executing asynchronous tasks, with support for prioritization, retry, monitoring, and scheduling.

## Core Components

### TaskManager

```python
from pepperpy_core.task import TaskManager

# Create manager with advanced configuration
manager = TaskManager(
    max_workers=10,
    queue_size=1000,
    retry_policy=RetryPolicy.EXPONENTIAL
)

# Create task
@manager.task
async def process_data(data: dict):
    result = await transform_data(data)
    return result

# Execute task
task = await manager.execute(
    process_data,
    {"id": "123"}
)

# Schedule execution
scheduled = await manager.schedule(
    process_data,
    {"id": "123"},
    delay=60  # seconds
)
```

### TaskQueue

```python
from pepperpy_core.task import TaskQueue

# Wait for completion
async with TaskQueue() as queue:
    # Add tasks
    await queue.put(task1)
    await queue.put(task2)
    
    # Process tasks
    async for task in queue:
        result = await task.execute()
```

### PriorityQueue

```python
from pepperpy_core.task import PriorityQueue

# Create queue with policy
queue = PriorityQueue(
    policy=PriorityPolicy.FIFO,
    max_size=1000
)

# Add tasks with priority
await queue.put(task1, priority=1)
await queue.put(task2, priority=2)

# Process by priority
while not queue.empty():
    task = await queue.get()
    await task.execute()
```

## Usage Patterns

### 1. Task Pipeline

```python
from pepperpy_core.task import Pipeline

class DataPipeline(Pipeline):
    async def process(self, data: dict):
        # Validate
        await self.validate(data)
        
        # Transform
        result = await self.transform(data)
        
        # Store
        await self.store(result)
        
        return result
```

### 2. Task Groups

```python
from pepperpy_core.task import TaskGroup

async with TaskGroup() as group:
    # Add tasks
    task1 = group.create_task(process1())
    task2 = group.create_task(process2())
    
    # Wait for all
    results = await group.gather()
```

### 3. Periodic Tasks

```python
from pepperpy_core.task import PeriodicTask

# Daily cleanup
@manager.periodic(
    interval=24*60*60,  # 24 hours
    start_time="00:00"
)
async def cleanup():
    await cleanup_old_data()
```

### 4. Tasks with Dependencies

```python
from pepperpy_core.task import TaskGraph

# Define dependencies
graph = TaskGraph()
graph.add_dependency(task2, task1)
graph.add_dependency(task3, task2)

# Execute graph
async with graph:
    # Wait for completion
    results = await graph.execute_all()
```

## Advanced Features

### 1. Progress Tracking

```python
from pepperpy_core.task import Progress

class ProcessTask(Task):
    async def execute(self):
        progress = Progress()
        
        # Start processing
        progress.update(0.0, "Starting")
        
        # Process data
        for i in range(100):
            await process_chunk(i)
            progress.update(i/100, f"Processing {i}%")
        
        # Complete
        progress.update(1.0, "Completed")
```

### 2. Metrics

```python
from pepperpy_core.task import Metrics

# Configure metrics
metrics = Metrics(
    namespace="tasks",
    subsystem="processing"
)

# Collect metrics
@metrics.measure
async def process_data():
    await process()
```

## Best Practices

1. **Task Design**
   - Keep tasks focused
   - Handle errors gracefully
   - Include timeouts
   - Document behavior

2. **Monitoring**
   - Track progress
   - Enable metrics
   - Log state changes
   - Monitor resources

3. **Performance**
   - Optimize concurrency
   - Use batching
   - Handle exceptions
   - Implement timeouts

4. **Resource Management**
   - Clean up resources
   - Manage memory
   - Control concurrency
   - Monitor usage

## Common Patterns

### 1. Retry Pattern

```python
from pepperpy_core.task import RetryTask

class APITask(RetryTask):
    def __init__(self):
        super().__init__(
            max_retries=3,
            retry_delay=1.0
        )
    
    async def execute(self):
        try:
            return await self.api_call()
        except APIError as e:
            if self.should_retry(e):
                return await self.retry()
            raise
```

### 2. Batch Processing

```python
from pepperpy_core.task import BatchTask

class DataBatch(BatchTask):
    def __init__(self, batch_size: int = 100):
        super().__init__(batch_size)
    
    async def process_batch(self, items: list):
        results = []
        for item in items:
            result = await process_item(item)
            results.append(result)
        return results
```

### 3. Task Composition

```python
from pepperpy_core.task import CompositeTask

class ProcessingTask(CompositeTask):
    async def execute(self):
        # Execute subtasks
        await self.execute_subtask(ValidateTask())
        await self.execute_subtask(TransformTask())
        await self.execute_subtask(StoreTask())
```

## API Reference

### Task

```python
class Task:
    async def execute(self) -> Any:
        """Execute the task."""
        
    async def cancel(self):
        """Cancel the task."""
        
    def get_status(self) -> TaskStatus:
        """Get task status."""
```

### TaskManager

```python
class TaskManager:
    async def execute(
        self,
        task: Task,
        *args,
        **kwargs
    ) -> TaskResult:
        """Execute a task."""
        
    async def schedule(
        self,
        task: Task,
        delay: float
    ) -> TaskResult:
        """Schedule a task."""
```

### TaskQueue

```python
class TaskQueue:
    async def put(
        self,
        task: Task,
        priority: int = 0
    ):
        """Add task to queue."""
        
    async def get(self) -> Task:
        """Get next task."""
``` 