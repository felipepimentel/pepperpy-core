# Serialization (Serialização)

O módulo Serialization do PepperPy Core fornece utilitários para serialização e deserialização de objetos, com suporte especial para JSON e objetos personalizados.

## Componentes Principais

### Serializable

Protocolo para objetos serializáveis:

```python
from pepperpy_core import Serializable

class User(Serializable):
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "age": self.age
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        return cls(
            name=data["name"],
            age=data["age"]
        )
```

### JsonSerializer

Serializador JSON com suporte a objetos complexos:

```python
from pepperpy_core import JsonSerializer

# Criar serializador
serializer = JsonSerializer()

# Serializar objeto
user = User("John", 30)
json_str = serializer.serialize(user)

# Deserializar objeto
user_copy = serializer.deserialize(json_str, User)
```

## Exemplos de Uso

### Serialização Básica

```python
from pepperpy_core import Serializable, JsonSerializer
from dataclasses import dataclass

@dataclass
class Point(Serializable):
    x: float
    y: float
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Point":
        return cls(
            x=data["x"],
            y=data["y"]
        )

async def exemplo_serializacao_basica():
    # Criar objeto
    point = Point(10.5, 20.3)
    
    # Serializar
    serializer = JsonSerializer()
    json_data = serializer.serialize(point)
    
    # Deserializar
    point_copy = serializer.deserialize(
        json_data,
        Point
    )
    
    print(f"X: {point_copy.x}, Y: {point_copy.y}")
```

### Serialização Complexa

```python
from pepperpy_core import Serializable, JsonSerializer
from typing import List

class Address(Serializable):
    def __init__(self, street: str, city: str):
        self.street = street
        self.city = city
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "street": self.street,
            "city": self.city
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Address":
        return cls(
            street=data["street"],
            city=data["city"]
        )

class Person(Serializable):
    def __init__(
        self,
        name: str,
        addresses: List[Address]
    ):
        self.name = name
        self.addresses = addresses
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "addresses": [
                addr.to_dict()
                for addr in self.addresses
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Person":
        return cls(
            name=data["name"],
            addresses=[
                Address.from_dict(addr)
                for addr in data["addresses"]
            ]
        )

async def exemplo_serializacao_complexa():
    # Criar objeto complexo
    person = Person(
        "John",
        [
            Address("123 Main St", "New York"),
            Address("456 Park Ave", "Boston")
        ]
    )
    
    # Serializar
    serializer = JsonSerializer()
    json_data = serializer.serialize(person)
    
    # Deserializar
    person_copy = serializer.deserialize(
        json_data,
        Person
    )
```

## Recursos Avançados

### Serializador com Validação

```python
class ValidatedSerializer(JsonSerializer):
    def __init__(self, schema: dict):
        super().__init__()
        self.schema = schema
    
    def serialize(self, obj: Any) -> str:
        # Validar objeto
        self._validate(obj)
        return super().serialize(obj)
    
    def _validate(self, obj: Any) -> None:
        if not hasattr(obj, "__annotations__"):
            return
        
        for field, type_hint in obj.__annotations__.items():
            value = getattr(obj, field)
            if not isinstance(value, type_hint):
                raise TypeError(
                    f"Campo {field} deve ser do tipo {type_hint}"
                )
```

### Serializador com Cache

```python
class CachedSerializer(JsonSerializer):
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    def serialize(self, obj: Any) -> str:
        # Gerar chave de cache
        cache_key = id(obj)
        
        # Verificar cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Serializar e cachear
        result = super().serialize(obj)
        self.cache[cache_key] = result
        return result
    
    def clear_cache(self):
        self.cache.clear()
```

## Melhores Práticas

1. **Serialização**
   - Implemente to_dict
   - Valide dados
   - Trate tipos especiais
   - Documente formato

2. **Deserialização**
   - Valide entrada
   - Trate dados faltantes
   - Converta tipos
   - Mantenha consistência

3. **Performance**
   - Use cache quando apropriado
   - Otimize conversões
   - Minimize overhead
   - Agrupe operações

4. **Segurança**
   - Valide entrada
   - Sanitize dados
   - Limite tamanho
   - Proteja sensíveis

5. **Manutenção**
   - Versione formato
   - Documente mudanças
   - Teste conversões
   - Monitore erros

## Padrões Comuns

### Serializador com Versão

```python
class VersionedSerializer(JsonSerializer):
    def __init__(self, version: str = "1.0"):
        super().__init__()
        self.version = version
    
    def serialize(self, obj: Any) -> str:
        # Adicionar versão
        data = {
            "_version": self.version,
            "data": obj.to_dict()
        }
        return super().serialize(data)
    
    def deserialize(
        self,
        data: str,
        target_type: type[T] | None = None
    ) -> Any:
        # Extrair e verificar versão
        parsed = json.loads(data)
        version = parsed.get("_version", "1.0")
        
        if version != self.version:
            raise ValueError(
                f"Versão incompatível: {version}"
            )
        
        # Deserializar dados
        if target_type:
            return target_type.from_dict(parsed["data"])
        return parsed["data"]
```

### Serializador com Compressão

```python
import zlib
import base64

class CompressedSerializer(JsonSerializer):
    def serialize(self, obj: Any) -> str:
        # Serializar normalmente
        json_str = super().serialize(obj)
        
        # Comprimir e codificar
        compressed = zlib.compress(json_str.encode())
        return base64.b64encode(compressed).decode()
    
    def deserialize(
        self,
        data: str,
        target_type: type[T] | None = None
    ) -> Any:
        # Decodificar e descomprimir
        decoded = base64.b64decode(data.encode())
        json_str = zlib.decompress(decoded).decode()
        
        # Deserializar normalmente
        return super().deserialize(json_str, target_type)
```

### Serializador com Logging

```python
class LoggedSerializer(JsonSerializer):
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def serialize(self, obj: Any) -> str:
        try:
            result = super().serialize(obj)
            self._log("serialize", obj, None)
            return result
        except Exception as e:
            self._log("serialize", obj, e)
            raise
    
    def deserialize(
        self,
        data: str,
        target_type: type[T] | None = None
    ) -> Any:
        try:
            result = super().deserialize(data, target_type)
            self._log("deserialize", result, None)
            return result
        except Exception as e:
            self._log("deserialize", data, e)
            raise
    
    def _log(
        self,
        operation: str,
        data: Any,
        error: Exception | None
    ):
        self.logs.append({
            "timestamp": time.time(),
            "operation": operation,
            "data_type": type(data).__name__,
            "error": str(error) if error else None
        })
```
``` 