# Cache (Cache)

O módulo de Cache do PepperPy Core fornece uma implementação genérica de cache em memória com suporte a TTL (Time To Live) e limite de tamanho.

## Componentes Principais

### Cache

Classe principal para gerenciamento de cache:

```python
from pepperpy_core import Cache, CacheConfig

# Criar cache
config = CacheConfig(
    name="app_cache",
    max_size=1000,
    ttl=60.0
)
cache = Cache[str](config)  # Cache tipado para strings

# Inicializar cache
await cache.initialize()

# Usar cache
await cache.set("key", "value")
value = await cache.get("key")
```

### CacheConfig

Configuração do cache:

```python
from pepperpy_core import CacheConfig

# Configuração básica
config = CacheConfig(
    name="data_cache",
    max_size=1000,  # Número máximo de itens
    ttl=60.0,       # Tempo de vida em segundos
    metadata={"type": "memory"}
)
```

## Exemplos de Uso

### Cache Básico

```python
from pepperpy_core import Cache, CacheConfig

async def exemplo_cache_basico():
    # Criar e configurar cache
    cache = Cache[dict](CacheConfig(
        name="user_cache",
        max_size=100,
        ttl=300  # 5 minutos
    ))
    
    # Inicializar
    await cache.initialize()
    
    # Armazenar dados
    user_data = {"id": 1, "name": "John"}
    await cache.set("user:1", user_data)
    
    # Recuperar dados
    cached_user = await cache.get("user:1")
    if cached_user:
        print(f"Usuário: {cached_user['name']}")
    
    # Limpar cache
    await cache.clear()
```

### Cache com Tipos Genéricos

```python
from dataclasses import dataclass
from pepperpy_core import Cache, CacheConfig

@dataclass
class UserProfile:
    id: int
    name: str
    email: str

async def exemplo_cache_tipado():
    # Cache tipado para UserProfile
    cache = Cache[UserProfile](CacheConfig(
        name="profile_cache",
        max_size=1000
    ))
    await cache.initialize()
    
    # Armazenar perfil
    profile = UserProfile(1, "John", "john@example.com")
    await cache.set(f"profile:{profile.id}", profile)
    
    # Recuperar perfil
    cached_profile = await cache.get(f"profile:1")
    if cached_profile:
        print(f"Nome: {cached_profile.name}")
```

## Recursos Avançados

### Cache com Estatísticas

```python
class MonitoredCache(Cache[T]):
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self.hits = 0
        self.misses = 0
    
    async def get(self, key: str, default: T | None = None) -> T | None:
        value = await super().get(key, default)
        if value is not default:
            self.hits += 1
        else:
            self.misses += 1
        return value
    
    async def get_stats(self) -> dict[str, Any]:
        stats = await super().get_stats()
        stats.update({
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        })
        return stats
```

### Cache com Eventos

```python
class EventCache(Cache[T]):
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self.listeners = []
    
    def add_listener(self, listener: callable):
        self.listeners.append(listener)
    
    async def set(self, key: str, value: T) -> None:
        await super().set(key, value)
        for listener in self.listeners:
            await listener("set", key, value)
    
    async def delete(self, key: str) -> None:
        await super().delete(key)
        for listener in self.listeners:
            await listener("delete", key, None)
```

## Melhores Práticas

1. **Configuração**
   - Defina tamanho máximo apropriado
   - Configure TTL adequado
   - Use nomes descritivos
   - Documente configurações

2. **Uso de Memória**
   - Monitore uso de memória
   - Implemente limpeza periódica
   - Use tipos apropriados
   - Evite objetos muito grandes

3. **Performance**
   - Monitore hit ratio
   - Otimize chaves de cache
   - Implemente warm-up
   - Use batch operations

4. **Manutenção**
   - Monitore estatísticas
   - Implemente logging
   - Faça limpeza periódica
   - Atualize configurações

5. **Tipos**
   - Use tipos genéricos
   - Valide tipos de dados
   - Documente tipos
   - Mantenha consistência

## Padrões Comuns

### Cache com Expiração

```python
class ExpiringCache(Cache[T]):
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self.expiration = {}
    
    async def set(self, key: str, value: T) -> None:
        await super().set(key, value)
        self.expiration[key] = time.time() + self.config.ttl
    
    async def get(self, key: str, default: T | None = None) -> T | None:
        if key in self.expiration:
            if time.time() > self.expiration[key]:
                await self.delete(key)
                return default
        return await super().get(key, default)
```

### Cache com Fallback

```python
class FallbackCache(Cache[T]):
    def __init__(
        self,
        config: CacheConfig,
        fallback_func: callable
    ):
        super().__init__(config)
        self.fallback = fallback_func
    
    async def get(self, key: str, default: T | None = None) -> T | None:
        value = await super().get(key, default)
        if value is default:
            # Buscar do fallback
            value = await self.fallback(key)
            if value is not None:
                await self.set(key, value)
        return value
```

### Cache com Prefixo

```python
class PrefixedCache(Cache[T]):
    def __init__(
        self,
        config: CacheConfig,
        prefix: str
    ):
        super().__init__(config)
        self.prefix = prefix
    
    def _get_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str, default: T | None = None) -> T | None:
        return await super().get(self._get_key(key), default)
    
    async def set(self, key: str, value: T) -> None:
        await super().set(self._get_key(key), value)
    
    async def delete(self, key: str) -> None:
        await super().delete(self._get_key(key))
```
``` 