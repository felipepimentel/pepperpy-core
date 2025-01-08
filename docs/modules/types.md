# Types (Tipos)

O módulo Types do PepperPy Core fornece definições de tipos e classes base para tipagem estática, incluindo tipos genéricos, protocolos, e utilitários para type hints.

## Componentes Principais

### DataClass

Classe base para dados:

```python
from pepperpy_core import DataClass
from dataclasses import field

@dataclass
class User(DataClass):
    id: str
    name: str
    email: str
    active: bool = True
    metadata: dict = field(default_factory=dict)
```

### Protocol

Protocolos para interfaces:

```python
from pepperpy_core import Protocol
from typing import Any

class Serializable(Protocol):
    def serialize(self) -> bytes:
        ...
    
    def deserialize(self, data: bytes) -> Any:
        ...
```

### TypeVar

Tipos genéricos:

```python
from pepperpy_core import TypeVar, Generic

T = TypeVar("T")

class Container(Generic[T]):
    def __init__(self, value: T):
        self.value = value
    
    def get(self) -> T:
        return self.value
```

## Exemplos de Uso

### Dados Tipados

```python
from pepperpy_core import DataClass
from typing import Optional, List

@dataclass
class Address(DataClass):
    street: str
    city: str
    country: str
    postal_code: str

@dataclass
class Contact(DataClass):
    email: str
    phone: Optional[str] = None
    address: Optional[Address] = None

@dataclass
class Person(DataClass):
    id: str
    name: str
    age: int
    contacts: List[Contact] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def add_contact(self, contact: Contact) -> None:
        self.contacts.append(contact)
    
    def get_primary_email(self) -> Optional[str]:
        return self.contacts[0].email if self.contacts else None
```

### Interfaces Tipadas

```python
from pepperpy_core import Protocol
from typing import TypeVar, Generic

T = TypeVar("T")

class Repository(Protocol[T]):
    async def get(self, id: str) -> T:
        ...
    
    async def save(self, item: T) -> None:
        ...
    
    async def delete(self, id: str) -> None:
        ...
    
    async def list(self) -> list[T]:
        ...

class UserRepository(Repository[User]):
    async def get(self, id: str) -> User:
        # Implementação
        pass
    
    async def save(self, user: User) -> None:
        # Implementação
        pass
    
    async def delete(self, id: str) -> None:
        # Implementação
        pass
    
    async def list(self) -> list[User]:
        # Implementação
        pass
```

## Recursos Avançados

### Type Guards

```python
from pepperpy_core import TypeGuard
from typing import Any

def is_user(obj: Any) -> TypeGuard[User]:
    return (
        isinstance(obj, dict) and
        "id" in obj and
        "name" in obj and
        "email" in obj
    )

def process_user(data: Any) -> None:
    if is_user(data):
        # data é tipado como User
        print(f"Usuário: {data['name']}")
    else:
        # data é tipado como Any
        print("Dados inválidos")
```

### Type Aliases

```python
from pepperpy_core import TypeAlias
from typing import Union, Dict, List

# Tipos complexos
JsonValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
JsonObject = Dict[str, JsonValue]
JsonArray = List[JsonValue]

# Tipos de negócio
UserId = str
UserMap = Dict[UserId, User]
UserList = List[User]

# Tipos de função
Handler = Callable[[Event], Awaitable[None]]
Middleware = Callable[[Request, Handler], Awaitable[Response]]
```

## Melhores Práticas

1. **Tipagem**
   - Use type hints
   - Defina protocolos
   - Valide tipos
   - Documente tipos

2. **Genéricos**
   - Use TypeVar
   - Restrinja tipos
   - Defina bounds
   - Documente variância

3. **Validação**
   - Use type guards
   - Valide runtime
   - Trate erros
   - Documente checks

4. **Manutenção**
   - Atualize tipos
   - Refatore aliases
   - Remova duplicação
   - Mantenha coerência

5. **Qualidade**
   - Use mypy
   - Teste tipos
   - Verifique cobertura
   - Documente mudanças

## Padrões Comuns

### Builder Tipado

```python
from pepperpy_core import Builder
from typing import TypeVar, Generic

T = TypeVar("T")

class TypedBuilder(Builder[T], Generic[T]):
    def __init__(self, cls: Type[T]):
        self.cls = cls
        self.attrs = {}
    
    def set(
        self,
        name: str,
        value: Any
    ) -> "TypedBuilder[T]":
        self.attrs[name] = value
        return self
    
    def build(self) -> T:
        return self.cls(**self.attrs)

# Uso
user_builder = TypedBuilder(User)
user = (
    user_builder
    .set("id", "123")
    .set("name", "John")
    .set("email", "john@example.com")
    .build()
)
```

### Factory Tipado

```python
from pepperpy_core import Factory
from typing import TypeVar, Generic, Type

T = TypeVar("T")

class TypedFactory(Factory[T], Generic[T]):
    def __init__(self):
        self.types: Dict[str, Type[T]] = {}
    
    def register(
        self,
        name: str,
        cls: Type[T]
    ) -> None:
        self.types[name] = cls
    
    def create(
        self,
        name: str,
        **kwargs
    ) -> T:
        if name not in self.types:
            raise ValueError(f"Tipo {name} não registrado")
        
        return self.types[name](**kwargs)

# Uso
factory = TypedFactory[User]()
factory.register("admin", AdminUser)
factory.register("customer", CustomerUser)

user = factory.create(
    "admin",
    id="123",
    name="John"
)
```

### Visitor Tipado

```python
from pepperpy_core import Visitor
from typing import TypeVar, Generic

T = TypeVar("T")
R = TypeVar("R")

class TypedVisitor(Visitor[T, R], Generic[T, R]):
    def __init__(self):
        self.handlers: Dict[Type[T], Callable[[T], R]] = {}
    
    def register(
        self,
        cls: Type[T],
        handler: Callable[[T], R]
    ) -> None:
        self.handlers[cls] = handler
    
    def visit(self, obj: T) -> R:
        for cls, handler in self.handlers.items():
            if isinstance(obj, cls):
                return handler(obj)
        
        raise TypeError(f"Tipo não suportado: {type(obj)}")

# Uso
visitor = TypedVisitor[Node, str]()
visitor.register(TextNode, lambda n: n.text)
visitor.register(LinkNode, lambda n: n.url)

result = visitor.visit(node)
``` 