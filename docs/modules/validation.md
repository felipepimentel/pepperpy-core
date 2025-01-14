# Validation Module

The PepperPy Core Validation module provides a flexible and extensible system for data validation, with support for custom rules and asynchronous validation.

## Core Components

### Validator

```python
from pepperpy.validation import Validator

# Create validator
validator = Validator()

# Add rules
validator.add_rule("name", str, required=True)
validator.add_rule("age", int, min_value=0)

# Validate data
errors = validator.validate({
    "name": "John",
    "age": 30
})
```

### ValidationRule

```python
from pepperpy.validation import ValidationRule

# Create rule
rule = ValidationRule(
    type=str,
    min_length=3,
    message="Value must have at least 3 characters"
)
```

### ValidationSchema

```python
from pepperpy.validation import Schema

# Create schema
schema = Schema({
    "name": {
        "type": str,
        "required": True,
        "message": "Name is required"
    },
    "email": {
        "type": str,
        "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$",
        "message": "Invalid email format"
    },
    "age": {
        "type": int,
        "min_value": 0,
        "max_value": 120
    }
})
```

## Usage Examples

### Basic Validation

```python
from pepperpy.validation import Validator

# Create validator
validator = Validator()

# Add rules
validator.add_rule(
    "name",
    str,
    required=True,
    message="Name is required"
)

# Validate data
errors = validator.validate({
    "name": "John",
    "age": 30
})

if errors:
    print(f"Validation errors: {errors}")
```

### Custom Rules

```python
from pepperpy.validation import Rule

class EmailRule(Rule):
    def __init__(self):
        super().__init__(
            pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
            message="Invalid email format"
        )
    
    def validate(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        
        return bool(self.pattern.match(value))
```

### Async Validation

```python
from pepperpy.validation import AsyncValidator

class DatabaseValidator(AsyncValidator):
    def __init__(self, db):
        self.db = db
    
    async def validate(self, value: str) -> bool:
        # Check database
        exists = await self.db.exists(value)
        return not exists
```

## Advanced Features

### Validation Chain

```python
from pepperpy.validation import ValidationChain

class UserValidation(ValidationChain):
    def __init__(self):
        super().__init__([
            NotEmptyRule(),
            LengthRule(min=2, max=50),
            CharacterRule(allowed="a-zA-Z0-9_"),
            DatabaseRule()
        ])
    
    async def validate(self, value: str) -> bool:
        for validator in self.validators:
            if asyncio.iscoroutinefunction(validator.validate):
                await validator.validate(value)
            else:
                validator.validate(value)
        return True
```

### Validation with Transform

```python
from pepperpy.validation import TransformValidator

class EmailValidator(TransformValidator):
    def transform(self, value: str) -> str:
        # Normalize email
        return value.lower().strip()
    
    def validate(self, value: str) -> bool:
        # Validate email format
        if not re.match(self.email_pattern, value):
            raise ValidationError("Invalid email format")
        return True
```

## Best Practices

1. **Rule Design**
   - Keep rules simple
   - Compose for complexity
   - Document rules
   - Handle edge cases

2. **Error Handling**
   - Use clear messages
   - Include context
   - Handle all cases
   - Log failures

3. **Performance**
   - Optimize validation
   - Cache results
   - Batch operations
   - Monitor timing

4. **Security**
   - Validate all input
   - Sanitize data
   - Limit input size
   - Handle malicious input

5. **Maintenance**
   - Document rules
   - Test edge cases
   - Update patterns
   - Monitor failures

## Common Patterns

### Rule Factory

```python
from pepperpy.validation import RuleFactory

class Factory(RuleFactory):
    def __init__(self):
        self.rules = {}
    
    def register(self, name: str, rule: Rule):
        self.rules[name] = rule
    
    def create(self, name: str, **kwargs) -> Rule:
        if name not in self.rules:
            raise ValueError(f"Rule not found: {name}")
        
        return self.rules[name](**kwargs)
```

### Rule Composition

```python
from pepperpy.validation import CompositeRule

class UserRule(CompositeRule):
    def __init__(self):
        super().__init__([
            NotEmptyRule(),
            LengthRule(min=2),
            EmailRule()
        ])
    
    def validate(self, value: str) -> bool:
        for rule in self.rules:
            if not rule.validate(value):
                return False
        return True
```

### Rule with Cache

```python
from pepperpy.validation import CachedRule

class CachedValidator(CachedRule):
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    def validate(self, value: str) -> bool:
        # Check cache
        if value in self.cache:
            return self.cache[value]
        
        # Validate
        result = super().validate(value)
        
        # Update cache
        self.cache[value] = result
        return result
```

## API Reference

### Validator

```python
class Validator:
    def add_rule(
        self,
        field: str,
        rule: Rule
    ):
        """Add validation rule."""
        
    def validate(
        self,
        data: dict
    ) -> List[str]:
        """Validate data."""
```

### Rule

```python
class Rule:
    def validate(
        self,
        value: Any
    ) -> bool:
        """Validate value."""
        
    def get_message(self) -> str:
        """Get error message."""
```

### Schema

```python
class Schema:
    def validate(
        self,
        data: dict
    ) -> List[str]:
        """Validate against schema."""
        
    def add_field(
        self,
        name: str,
        rules: dict
    ):
        """Add field to schema."""
```
``` 