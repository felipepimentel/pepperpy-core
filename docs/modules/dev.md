# Dev (Desenvolvimento)

O módulo Dev do PepperPy Core fornece utilitários para desenvolvimento, incluindo ferramentas de logging, timing, debugging e testes assíncronos.

## Componentes Principais

### LogLevel

Enumeração para níveis de log:

```python
from pepperpy_core import LogLevel

# Níveis disponíveis
level = LogLevel.DEBUG    # debug
level = LogLevel.INFO     # info
level = LogLevel.WARNING  # warning
level = LogLevel.ERROR    # error
level = LogLevel.CRITICAL # critical
```

### Timer

Context manager para medição de tempo:

```python
from pepperpy_core import Timer

# Usar timer
with Timer("operation") as timer:
    # Operação a ser medida
    process_data()

# Com logger
with Timer("operation", logger=my_logger) as timer:
    process_data()
```

### AsyncTestCase

Classe base para testes assíncronos:

```python
from pepperpy_core import AsyncTestCase

class MyTests(AsyncTestCase):
    async def test_async_operation(self):
        result = await my_async_function()
        self.assertEqual(result, expected)
    
    def test_with_run_async(self):
        result = self.run_async(my_async_function())
        self.assertEqual(result, expected)
```

## Exemplos de Uso

### Debug Decorators

```python
from pepperpy_core import debug_decorator, async_debug_decorator

# Criar logger
logger = MyLogger()

# Decorador para função síncrona
@debug_decorator(logger)
def process_data(data: dict) -> dict:
    return {"processed": data}

# Decorador para função assíncrona
@async_debug_decorator(logger)
async def fetch_data(url: str) -> dict:
    return {"url": url, "status": "ok"}
```

### Timer com Logger

```python
from pepperpy_core import Timer, LoggerProtocol

class MyLogger(LoggerProtocol):
    def info(self, message: str, **kwargs):
        print(f"INFO: {message}")
        if kwargs:
            print(f"Extra: {kwargs}")
    
    # Implementar outros métodos do protocolo...

async def exemplo_timer():
    logger = MyLogger()
    
    # Usar timer com logger
    with Timer("data_processing", logger=logger):
        # Timer registrará início e fim
        await process_large_dataset()
```

## Recursos Avançados

### Logger Personalizado

```python
from pepperpy_core import LogLevel, LoggerProtocol

class StructuredLogger(LoggerProtocol):
    def log(self, level: LogLevel, message: str, **kwargs):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level.value,
            "message": message,
            **kwargs
        }
        print(json.dumps(log_entry))
    
    def debug(self, message: str, **kwargs):
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.log(LogLevel.CRITICAL, message, **kwargs)
```

### Debug Utilitários

```python
from pepperpy_core import debug_call, debug_result, debug_error

class DebugWrapper:
    def __init__(self, logger: LoggerProtocol):
        self.logger = logger
    
    async def execute(self, func: callable, *args, **kwargs):
        # Registrar chamada
        debug_call(self.logger, func.__name__, *args, **kwargs)
        
        try:
            # Executar função
            result = await func(*args, **kwargs)
            
            # Registrar resultado
            debug_result(self.logger, func.__name__, result)
            return result
        except Exception as e:
            # Registrar erro
            debug_error(self.logger, func.__name__, e)
            raise
```

## Melhores Práticas

1. **Logging**
   - Use níveis apropriados
   - Inclua contexto relevante
   - Estruture mensagens
   - Implemente todos os métodos

2. **Timing**
   - Use nomes descritivos
   - Meça operações específicas
   - Registre resultados
   - Monitore performance

3. **Debugging**
   - Use decoradores apropriados
   - Registre informações úteis
   - Mantenha contexto
   - Limpe logs de debug

4. **Testes**
   - Use AsyncTestCase
   - Implemente tearDown
   - Limpe recursos
   - Teste exceções

5. **Performance**
   - Minimize overhead
   - Use sampling
   - Otimize logging
   - Monitore memória

## Padrões Comuns

### Timer com Métricas

```python
class MetricsTimer(Timer):
    def __init__(
        self,
        name: str,
        logger: Optional[LoggerProtocol] = None
    ):
        super().__init__(name, logger)
        self.metrics = []
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        duration = time.perf_counter() - self._start
        self.metrics.append(duration)
        
        if self.logger:
            stats = {
                "min": min(self.metrics),
                "max": max(self.metrics),
                "avg": sum(self.metrics) / len(self.metrics)
            }
            self.logger.info(
                f"Timer {self.name} stats",
                timer=self.name,
                stats=stats
            )
```

### Debug com Contexto

```python
class ContextLogger(LoggerProtocol):
    def __init__(self):
        self.context = {}
    
    def add_context(self, **kwargs):
        self.context.update(kwargs)
    
    def log(self, level: LogLevel, message: str, **kwargs):
        # Mesclar contexto com kwargs
        context = {**self.context, **kwargs}
        print(f"[{level.value}] {message} {context}")
    
    # Implementar outros métodos do protocolo...
```

### Teste com Recursos

```python
class ResourceTestCase(AsyncTestCase):
    async def asyncSetUp(self):
        # Configurar recursos
        self.resource = await create_resource()
    
    async def asyncTearDown(self):
        # Limpar recursos
        await self.resource.cleanup()
    
    def setUp(self):
        super().setUp()
        self.run_async(self.asyncSetUp())
    
    def tearDown(self):
        self.run_async(self.asyncTearDown())
        super().tearDown()
```
``` 