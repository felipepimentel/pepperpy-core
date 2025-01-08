# Validators Module

The PepperPy Core Validators module provides a robust set of classes for data validation. It includes validators for basic types and common formats, with support for compositional validation and generic typing.

## Core Components

### Base Validator

```python
from pepperpy_core.validators import Validator

class CustomValidator(Validator):
    def validate(self, value: Any) -> bool:
        # Implement validation logic
        if not self._is_valid(value):
            raise ValidationError("Invalid value")
        return True
```

### Basic Validators

```python
from pepperpy_core.validators import (
    StringValidator,
    NumberValidator,
    BooleanValidator,
    DictValidator
)

# Dictionary validator
validator = DictValidator({
    "name": StringValidator(),
    "age": NumberValidator(),
    "active": BooleanValidator()
})
```

### Format Validators

Validators for specific formats:

```python
from pepperpy_core.validators import (
    EmailValidator,
    URLValidator,
    DateValidator,
    PhoneValidator
)

email = EmailValidator()
url = URLValidator()
date = DateValidator()
phone = PhoneValidator()
```

## Usage Examples

### Basic Validation

```python
from pepperpy_core.validators import StringValidator

validator = StringValidator(min_length=3, max_length=20)

try:
    validator.validate("user123")
except ValidationError as e:
    print(f"Invalid username: {e}")
```

### Composite Validation

```python
from pepperpy_core.validators import (
    DictValidator,
    StringValidator,
    EmailValidator
)

# Specific validators for fields
user_validator = DictValidator({
    "name": StringValidator(min_length=2),
    "email": EmailValidator()
})

data = {"name": "John", "email": "john@example.com"}

# Validate basic structure
user_validator.validate(data)

# Validate specific fields
email_validator = user_validator.fields["email"]
email_validator.validate(data["email"])
```

### List Validation

```python
from pepperpy_core.validators import ListValidator, EmailValidator

validator = ListValidator(EmailValidator())

try:
    validator.validate([
        "user1@example.com",
        "user2@example.com"
    ])
except ValidationError as e:
    print(f"Invalid email list: {e}")
```

## Advanced Features

### Custom Rules

```python
from pepperpy_core.validators import Validator, ValidationError
import re

class PasswordValidator(Validator):
    def __init__(self):
        self.uppercase = re.compile(r'[A-Z]')
        self.number = re.compile(r'[0-9]')
    
    def validate(self, value: str) -> bool:
        if not self.uppercase.search(value):
            raise ValidationError("Password must contain uppercase letter")
            
        if not self.number.search(value):
            raise ValidationError("Password must contain number")
            
        return True
```

### Async Validation

```python
from pepperpy_core.validators import AsyncValidator

class DatabaseValidator(AsyncValidator):
    async def validate(self, value: str) -> bool:
        # Check database
        exists = await self.db.exists(value)
        return not exists
```

## Best Practices

1. **Design**
   - Keep validators simple
   - Compose for complexity
   - Implement complete validation
   - Follow standards

2. **Error Handling**
   - Use appropriate exceptions
   - Provide useful messages
   - Handle edge cases
   - Log validation failures

3. **Performance**
   - Optimize regex patterns
   - Avoid redundant validations
   - Monitor validation time
   - Cache when possible

4. **Security**
   - Validate user input
   - Prevent code injection
   - Limit input size
   - Sanitize sensitive data

5. **Maintenance**
   - Document validation rules
   - Keep rules consistent
   - Update patterns when needed
   - Monitor validation failures

## Common Patterns

### Validation Chain

```python
from pepperpy_core.validators import ValidationChain

class UserValidation(ValidationChain):
    def __init__(self):
        super().__init__([
            NotEmptyValidator(),
            LengthValidator(min=2, max=50),
            CharacterValidator(allowed="a-zA-Z0-9_"),
            DatabaseValidator()
        ])
    
    async def validate(self, value: str) -> bool:
        for validator in self.validators:
            if asyncio.iscoroutinefunction(validator.validate):
                await validator.validate(value)
            else:
                validator.validate(value)
        return True
```

### Validator with Transformation

```python
from pepperpy_core.validators import TransformValidator

class EmailNormalizer(TransformValidator):
    def transform(self, value: str) -> str:
        # Normalize email
        return value.lower().strip()
    
    def validate(self, value: str) -> bool:
        # Validate email format
        if not re.match(self.email_pattern, value):
            raise ValidationError("Invalid email format")
        return True
```

## API Reference

### Base Classes

```python
class Validator:
    def validate(self, value: Any) -> bool:
        """Validate value."""
        
    def is_valid(self, value: Any) -> bool:
        """Check if value is valid."""

class AsyncValidator:
    async def validate(self, value: Any) -> bool:
        """Validate value asynchronously."""
        
    async def is_valid(self, value: Any) -> bool:
        """Check if value is valid asynchronously."""
```

### Common Validators

```python
class StringValidator(Validator):
    def __init__(
        self,
        min_length: int = None,
        max_length: int = None,
        pattern: str = None
    ):
        """Initialize string validator."""

class NumberValidator(Validator):
    def __init__(
        self,
        min_value: float = None,
        max_value: float = None,
        integer: bool = False
    ):
        """Initialize number validator."""

class ListValidator(Validator):
    def __init__(
        self,
        item_validator: Validator,
        min_length: int = None,
        max_length: int = None
    ):
        """Initialize list validator."""
``` 