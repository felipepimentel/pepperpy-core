# Context (Contexto)

O módulo de Contexto do PepperPy Core fornece uma implementação flexível para gerenciamento de estado e contexto em aplicações, com suporte a tipos genéricos e metadados.

## Componentes Principais

### Context

Classe principal para gerenciamento de contexto:

```python
from pepperpy_core import Context

# Criar contexto tipado
context = Context[str]()

# Definir valores
context.set("language", "pt-BR")
context.set_context("main")
context.set_state("active", user="admin")

# Recuperar valores
language = context.get("language")
current = context.get_context()
state = context.get_state()
```

### State

Container para estado com metadados:

```python
from pepperpy_core import State

# Criar estado
state = State[str](
    value="processing",
    metadata={"timestamp": "2024-01-05"}
)

# Acessar valores
value = state.value
metadata = state.metadata
```

## Exemplos de Uso

### Contexto Básico

```python
from pepperpy_core import Context

async def exemplo_contexto_basico():
    # Criar contexto
    context = Context[dict]()
    
    # Definir dados
    context.set("config", {
        "debug": True,
        "environment": "development"
    })
    
    # Atualizar múltiplos valores
    context.update({
        "version": "1.0.0",
        "api_key": "secret123"
    })
    
    # Recuperar valores
    config = context.get("config")
    version = context.get("version")
```

### Contexto com Estado

```python
from dataclasses import dataclass
from pepperpy_core import Context, State

@dataclass
class UserSession:
    user_id: int
    username: str
    role: str

async def exemplo_contexto_estado():
    # Criar contexto tipado
    context = Context[UserSession]()
    
    # Definir sessão atual
    session = UserSession(1, "admin", "admin")
    context.set_state(
        session,
        login_time="2024-01-05 10:00:00"
    )
    
    # Recuperar estado
    state = context.get_state()
    if state:
        print(f"Usuário: {state.value.username}")
        print(f"Login: {state.metadata['login_time']}")
```

## Recursos Avançados

### Contexto Aninhado

```python
class NestedContext(Context[T]):
    def __init__(self, parent: Context[T] | None = None):
        super().__init__()
        self.parent = parent
    
    def get(self, key: str, default: T | None = None) -> T | None:
        value = super().get(key)
        if value is None and self.parent:
            return self.parent.get(key, default)
        return value or default
    
    def get_context(self) -> T | None:
        value = super().get_context()
        if value is None and self.parent:
            return self.parent.get_context()
        return value
```

### Contexto com Validação

```python
class ValidatedContext(Context[T]):
    def __init__(self):
        super().__init__()
        self.validators = {}
    
    def add_validator(self, key: str, validator: callable):
        self.validators[key] = validator
    
    def set(self, key: str, value: T) -> None:
        if key in self.validators:
            validator = self.validators[key]
            if not validator(value):
                raise ContextError(
                    f"Validação falhou para {key}"
                )
        super().set(key, value)
```

## Melhores Práticas

1. **Tipos**
   - Use tipos genéricos
   - Defina tipos claros
   - Valide tipos
   - Mantenha consistência

2. **Estado**
   - Gerencie ciclo de vida
   - Use metadados apropriados
   - Implemente limpeza
   - Documente estados

3. **Contexto**
   - Defina escopo claro
   - Use hierarquia apropriada
   - Implemente validação
   - Gerencie recursos

4. **Performance**
   - Otimize acessos
   - Minimize estado
   - Use cache quando apropriado
   - Monitore uso

5. **Segurança**
   - Proteja dados sensíveis
   - Valide entrada
   - Controle acesso
   - Limpe dados sensíveis

## Padrões Comuns

### Contexto com Observadores

```python
class ObservableContext(Context[T]):
    def __init__(self):
        super().__init__()
        self.observers = []
    
    def add_observer(self, observer: callable):
        self.observers.append(observer)
    
    def set(self, key: str, value: T) -> None:
        old_value = self.get(key)
        super().set(key, value)
        for observer in self.observers:
            observer(key, old_value, value)
    
    def set_state(self, value: T, **metadata: Any) -> None:
        old_state = self.get_state()
        super().set_state(value, **metadata)
        for observer in self.observers:
            observer("state", old_state, value)
```

### Contexto com Histórico

```python
class HistoryContext(Context[T]):
    def __init__(self, max_history: int = 10):
        super().__init__()
        self.history = []
        self.max_history = max_history
    
    def set_state(self, value: T, **metadata: Any) -> None:
        old_state = self.get_state()
        if old_state:
            self.history.append(old_state)
            if len(self.history) > self.max_history:
                self.history.pop(0)
        super().set_state(value, **metadata)
    
    def undo(self) -> bool:
        if not self.history:
            return False
        
        state = self.history.pop()
        super().set_state(state.value, **state.metadata)
        return True
```

### Contexto com Cache

```python
class CachedContext(Context[T]):
    def __init__(self, ttl: float = 60.0):
        super().__init__()
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str, default: T | None = None) -> T | None:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["value"]
            del self.cache[key]
        
        value = super().get(key, default)
        if value is not None:
            self.cache[key] = {
                "value": value,
                "timestamp": time.time()
            }
        return value
```
``` 