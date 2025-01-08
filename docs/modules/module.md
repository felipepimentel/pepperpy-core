# Module (Módulo)

O módulo Module do PepperPy Core fornece a estrutura base para implementação de módulos, com suporte a inicialização, configuração e ciclo de vida.

## Componentes Principais

### BaseModule

Classe base para implementação de módulos:

```python
from pepperpy_core import BaseModule, ModuleConfig

class MyModule(BaseModule[ModuleConfig]):
    async def _setup(self) -> None:
        # Inicialização do módulo
        pass
    
    async def _teardown(self) -> None:
        # Limpeza do módulo
        pass

# Criar e inicializar módulo
config = ModuleConfig(name="my_module")
module = MyModule(config)
await module.initialize()
```

### ModuleConfig

Configuração base para módulos:

```python
from pepperpy_core import ModuleConfig

# Configuração básica
config = ModuleConfig(
    name="app_module",
    metadata={"version": "1.0.0"}
)
```

## Exemplos de Uso

### Módulo Básico

```python
from pepperpy_core import BaseModule, ModuleConfig
from dataclasses import dataclass

@dataclass
class DatabaseConfig(ModuleConfig):
    host: str = "localhost"
    port: int = 5432
    database: str = "app_db"

class DatabaseModule(BaseModule[DatabaseConfig]):
    async def _setup(self) -> None:
        # Conectar ao banco
        self.connection = await create_connection(
            self.config.host,
            self.config.port,
            self.config.database
        )
    
    async def _teardown(self) -> None:
        # Fechar conexão
        await self.connection.close()
    
    async def execute(self, query: str) -> Any:
        self._ensure_initialized()
        return await self.connection.execute(query)
```

### Módulo com Recursos

```python
from pepperpy_core import BaseModule, ModuleConfig
from typing import Any

class ResourceModule(BaseModule[ModuleConfig]):
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.resources = {}
    
    async def _setup(self) -> None:
        # Inicializar recursos
        self.resources = await load_resources()
    
    async def _teardown(self) -> None:
        # Liberar recursos
        for resource in self.resources.values():
            await resource.cleanup()
        self.resources.clear()
    
    async def get_resource(self, name: str) -> Any:
        self._ensure_initialized()
        return self.resources.get(name)
```

## Recursos Avançados

### Módulo com Dependências

```python
class DependentModule(BaseModule[ModuleConfig]):
    def __init__(
        self,
        config: ModuleConfig,
        dependencies: list[BaseModule]
    ):
        super().__init__(config)
        self.dependencies = dependencies
    
    async def initialize(self) -> None:
        # Inicializar dependências primeiro
        for dep in self.dependencies:
            if not dep.is_initialized:
                await dep.initialize()
        
        # Inicializar este módulo
        await super().initialize()
    
    async def teardown(self) -> None:
        # Teardown na ordem reversa
        await super().teardown()
        
        for dep in reversed(self.dependencies):
            await dep.teardown()
```

### Módulo com Estado

```python
from dataclasses import dataclass
from enum import Enum

class ModuleState(Enum):
    CREATED = "created"
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"

class StatefulModule(BaseModule[ModuleConfig]):
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.state = ModuleState.CREATED
    
    async def initialize(self) -> None:
        self.state = ModuleState.INITIALIZING
        await super().initialize()
        self.state = ModuleState.RUNNING
    
    async def teardown(self) -> None:
        self.state = ModuleState.STOPPING
        await super().teardown()
        self.state = ModuleState.STOPPED
```

## Melhores Práticas

1. **Inicialização**
   - Valide configuração
   - Inicialize recursos
   - Gerencie dependências
   - Trate erros

2. **Ciclo de Vida**
   - Implemente cleanup
   - Libere recursos
   - Mantenha estado
   - Documente ciclo

3. **Configuração**
   - Valide parâmetros
   - Use valores padrão
   - Documente opções
   - Mantenha simplicidade

4. **Performance**
   - Otimize inicialização
   - Cache recursos
   - Minimize overhead
   - Monitore uso

5. **Segurança**
   - Valide entrada
   - Proteja recursos
   - Controle acesso
   - Sanitize dados

## Padrões Comuns

### Módulo com Cache

```python
class CachedModule(BaseModule[ModuleConfig]):
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.cache = {}
    
    async def _setup(self) -> None:
        # Inicializar cache
        self.cache = await self.load_initial_data()
    
    async def _teardown(self) -> None:
        # Limpar cache
        self.cache.clear()
    
    async def get_data(self, key: str) -> Any:
        self._ensure_initialized()
        
        if key not in self.cache:
            self.cache[key] = await self.fetch_data(key)
        
        return self.cache[key]
```

### Módulo com Retry

```python
class RetryModule(BaseModule[ModuleConfig]):
    async def initialize(self) -> None:
        retries = 3
        delay = 1.0
        
        for attempt in range(retries):
            try:
                await super().initialize()
                return
            except Exception as e:
                if attempt == retries - 1:
                    raise
                
                await asyncio.sleep(delay)
                delay *= 2
```

### Módulo com Eventos

```python
class EventModule(BaseModule[ModuleConfig]):
    def __init__(self, config: ModuleConfig):
        super().__init__(config)
        self.listeners = []
    
    def add_listener(self, listener: callable):
        self.listeners.append(listener)
    
    async def notify(self, event: str, data: Any = None):
        self._ensure_initialized()
        
        for listener in self.listeners:
            try:
                await listener(event, data)
            except Exception as e:
                # Log erro mas continua notificando
                print(f"Error in listener: {e}")
```
``` 