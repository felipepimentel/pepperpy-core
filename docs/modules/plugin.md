# Plugin (Plugin)

O módulo Plugin do PepperPy Core fornece uma estrutura para gerenciamento de plugins, permitindo estender a funcionalidade da aplicação de forma dinâmica.

## Componentes Principais

### PluginManager

Gerenciador central de plugins:

```python
from pepperpy_core import PluginManager, PluginConfig

# Criar gerenciador
manager = PluginManager(
    PluginConfig(
        name="app_plugins",
        plugin_dir="plugins"
    )
)

# Inicializar
await manager.initialize()

# Carregar plugin
manager.load_plugin("plugins/my_plugin.py")

# Obter plugin
plugin = manager.get_plugin("my_plugin")
```

### Plugin Decorator

Decorador para definir plugins:

```python
from pepperpy_core import plugin

@plugin("my_plugin")
class MyPlugin:
    def process(self, data: dict) -> dict:
        return {"processed": data}

@plugin("formatter")
class FormatterPlugin:
    def format(self, text: str) -> str:
        return text.upper()
```

## Exemplos de Uso

### Plugin Básico

```python
from pepperpy_core import plugin, PluginManager

# Definir plugin
@plugin("data_processor")
class DataProcessor:
    def process(self, data: dict) -> dict:
        # Processar dados
        result = {
            "processed_at": time.time(),
            **data
        }
        return result

# Usar plugin
async def exemplo_plugin_basico():
    # Criar gerenciador
    manager = PluginManager()
    await manager.initialize()
    
    # Carregar plugin
    manager.load_plugin("plugins/processor.py")
    
    # Usar plugin
    processor = manager.get_plugin("data_processor")
    result = processor.process({"value": 42})
```

### Múltiplos Plugins

```python
from pepperpy_core import plugin, PluginManager

@plugin("validator")
class ValidationPlugin:
    def validate(self, data: dict) -> bool:
        return all(
            isinstance(v, (str, int, float))
            for v in data.values()
        )

@plugin("transformer")
class TransformPlugin:
    def transform(self, data: dict) -> dict:
        return {
            k: str(v).upper()
            if isinstance(v, str)
            else v
            for k, v in data.items()
        }

async def exemplo_multiplos_plugins():
    manager = PluginManager()
    await manager.initialize()
    
    # Carregar plugins
    manager.load_plugin("plugins/validator.py")
    manager.load_plugin("plugins/transformer.py")
    
    # Usar plugins em sequência
    data = {"name": "john", "age": 30}
    
    validator = manager.get_plugin("validator")
    if validator.validate(data):
        transformer = manager.get_plugin("transformer")
        result = transformer.transform(data)
```

## Recursos Avançados

### Plugin com Configuração

```python
from dataclasses import dataclass
from pepperpy_core import plugin

@dataclass
class PluginConfig:
    max_size: int = 1000
    timeout: float = 30.0

@plugin("configurable")
class ConfigurablePlugin:
    def __init__(self):
        self.config = PluginConfig()
    
    def configure(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self.config, k):
                setattr(self.config, k, v)
    
    def process(self, data: dict) -> dict:
        if len(data) > self.config.max_size:
            raise ValueError("Data too large")
        return data
```

### Plugin com Lifecycle

```python
@plugin("lifecycle")
class LifecyclePlugin:
    def __init__(self):
        self.initialized = False
        self.resources = {}
    
    async def initialize(self):
        if self.initialized:
            return
        
        # Inicializar recursos
        self.resources = await load_resources()
        self.initialized = True
    
    async def shutdown(self):
        if not self.initialized:
            return
        
        # Limpar recursos
        for resource in self.resources.values():
            await resource.cleanup()
        self.resources.clear()
        self.initialized = False
```

## Melhores Práticas

1. **Plugins**
   - Mantenha foco único
   - Documente interface
   - Valide entrada
   - Trate erros

2. **Gerenciamento**
   - Carregue sob demanda
   - Valide plugins
   - Gerencie dependências
   - Monitore uso

3. **Performance**
   - Otimize carregamento
   - Cache resultados
   - Minimize overhead
   - Gerencie recursos

4. **Segurança**
   - Valide plugins
   - Sandbox execução
   - Controle acesso
   - Monitore uso

5. **Manutenção**
   - Versione plugins
   - Documente mudanças
   - Teste plugins
   - Monitore erros

## Padrões Comuns

### Plugin com Cache

```python
@plugin("cached")
class CachedPlugin:
    def __init__(self):
        self.cache = {}
        self.ttl = 300  # 5 minutos
    
    def process(self, key: str, data: Any) -> Any:
        # Verificar cache
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["value"]
        
        # Processar dados
        result = self._process(data)
        
        # Atualizar cache
        self.cache[key] = {
            "value": result,
            "timestamp": time.time()
        }
        
        return result
    
    def _process(self, data: Any) -> Any:
        # Implementação específica
        return data
```

### Plugin com Pipeline

```python
@plugin("pipeline")
class PipelinePlugin:
    def __init__(self):
        self.steps = []
    
    def add_step(self, step: callable):
        self.steps.append(step)
    
    async def process(self, data: Any) -> Any:
        result = data
        
        for step in self.steps:
            try:
                result = await step(result)
            except Exception as e:
                print(f"Error in step {step.__name__}: {e}")
                raise
        
        return result
```

### Plugin com Eventos

```python
@plugin("events")
class EventPlugin:
    def __init__(self):
        self.listeners = {}
    
    def on(self, event: str, callback: callable):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
    
    async def emit(self, event: str, data: Any = None):
        if event not in self.listeners:
            return
        
        for listener in self.listeners[event]:
            try:
                await listener(data)
            except Exception as e:
                print(f"Error in listener: {e}")
```
``` 