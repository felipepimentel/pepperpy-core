# Registry (Registro)

O módulo Registry do PepperPy Core fornece um sistema de registro para implementações de protocolos, permitindo o gerenciamento dinâmico de implementações.

## Componentes Principais

### Registry

Classe principal para registro de implementações:

```python
from pepperpy_core import Registry
from typing import Protocol

# Definir protocolo
class DataProcessor(Protocol):
    def process(self, data: dict) -> dict:
        ...

# Criar registro
registry = Registry[DataProcessor](DataProcessor)

# Registrar implementação
class JsonProcessor:
    def process(self, data: dict) -> dict:
        return {"json": data}

registry.register("json", JsonProcessor)

# Usar implementação
processor = registry.get("json")
result = processor.process({"value": 42})
```

## Exemplos de Uso

### Registro Básico

```python
from pepperpy_core import Registry
from typing import Protocol

class Formatter(Protocol):
    def format(self, text: str) -> str:
        ...

async def exemplo_registro_basico():
    # Criar registro
    registry = Registry[Formatter](Formatter)
    
    # Implementar formatador
    class UpperFormatter:
        def format(self, text: str) -> str:
            return text.upper()
    
    # Registrar implementação
    registry.register("upper", UpperFormatter())
    
    # Usar formatador
    formatter = registry.get("upper")
    result = formatter.format("hello")  # "HELLO"
```

### Múltiplas Implementações

```python
from pepperpy_core import Registry
from typing import Protocol

class Validator(Protocol):
    def validate(self, data: Any) -> bool:
        ...

async def exemplo_multiplas_implementacoes():
    # Criar registro
    registry = Registry[Validator](Validator)
    
    # Registrar implementações
    class TypeValidator:
        def validate(self, data: Any) -> bool:
            return isinstance(data, (str, int, float))
    
    class RangeValidator:
        def validate(self, data: Any) -> bool:
            return 0 <= data <= 100
    
    registry.register("type", TypeValidator())
    registry.register("range", RangeValidator())
    
    # Listar implementações
    implementations = registry.list_implementations()
    print(f"Validadores: {implementations}")
    
    # Usar validadores
    type_validator = registry.get("type")
    range_validator = registry.get("range")
    
    value = 42
    if type_validator.validate(value) and range_validator.validate(value):
        print("Valor válido")
```

## Recursos Avançados

### Registro com Factory

```python
class ProcessorRegistry(Registry[DataProcessor]):
    def create_processor(
        self,
        name: str,
        **kwargs
    ) -> DataProcessor:
        # Obter implementação base
        base = self.get(name)
        
        # Criar nova instância com kwargs
        if isinstance(base, type):
            return base(**kwargs)
        
        # Clonar instância e configurar
        processor = copy.deepcopy(base)
        for key, value in kwargs.items():
            setattr(processor, key, value)
        
        return processor
```

### Registro com Validação

```python
class ValidatedRegistry(Registry[T]):
    def __init__(
        self,
        protocol: type[T],
        validators: list[callable]
    ):
        super().__init__(protocol)
        self.validators = validators
    
    def register(
        self,
        name: str,
        implementation: T | type[T]
    ) -> None:
        # Validar implementação
        impl = implementation
        if isinstance(impl, type):
            impl = impl()
        
        for validator in self.validators:
            if not validator(impl):
                raise ValueError(
                    f"Validação falhou: {validator.__name__}"
                )
        
        super().register(name, implementation)
```

## Melhores Práticas

1. **Protocolos**
   - Defina interfaces claras
   - Use type hints
   - Documente métodos
   - Mantenha simplicidade

2. **Implementações**
   - Siga o protocolo
   - Valide entrada
   - Trate erros
   - Documente comportamento

3. **Registro**
   - Use nomes descritivos
   - Valide implementações
   - Gerencie ciclo de vida
   - Mantenha organização

4. **Performance**
   - Cache implementações
   - Otimize instanciação
   - Minimize overhead
   - Monitore uso

5. **Manutenção**
   - Documente registros
   - Monitore uso
   - Limpe registros
   - Atualize implementações

## Padrões Comuns

### Registro com Cache

```python
class CachedRegistry(Registry[T]):
    def __init__(self, protocol: type[T]):
        super().__init__(protocol)
        self.cache = {}
    
    def get(self, name: str) -> T:
        if name not in self.cache:
            implementation = super().get(name)
            self.cache[name] = implementation
        return self.cache[name]
    
    def clear(self) -> None:
        super().clear()
        self.cache.clear()
```

### Registro com Eventos

```python
class EventRegistry(Registry[T]):
    def __init__(self, protocol: type[T]):
        super().__init__(protocol)
        self.listeners = []
    
    def add_listener(self, listener: callable):
        self.listeners.append(listener)
    
    def register(
        self,
        name: str,
        implementation: T | type[T]
    ) -> None:
        super().register(name, implementation)
        
        for listener in self.listeners:
            listener("register", name, implementation)
    
    def clear(self) -> None:
        for name in self.list_implementations():
            for listener in self.listeners:
                listener("unregister", name)
        
        super().clear()
```

### Registro com Dependências

```python
class DependentRegistry(Registry[T]):
    def __init__(self, protocol: type[T]):
        super().__init__(protocol)
        self.dependencies = {}
    
    def register_with_deps(
        self,
        name: str,
        implementation: T | type[T],
        dependencies: list[str]
    ) -> None:
        self.dependencies[name] = dependencies
        super().register(name, implementation)
    
    def get(self, name: str) -> T:
        # Verificar dependências
        if name in self.dependencies:
            for dep in self.dependencies[name]:
                if dep not in self._implementations:
                    raise ValueError(
                        f"Dependência não encontrada: {dep}"
                    )
        
        return super().get(name)
```
``` 