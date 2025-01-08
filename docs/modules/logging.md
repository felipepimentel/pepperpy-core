# Logging (Logging)

O módulo de Logging do PepperPy Core fornece uma implementação flexível e extensível para logging, com suporte a múltiplos handlers, formatação personalizada e níveis de log.

## Componentes Principais

### Logger

Classe principal para logging:

```python
from pepperpy_core import Logger

# Criar logger
logger = Logger("app")

# Usar logger
logger.info("Aplicação iniciada")
logger.debug("Detalhes de debug", module="auth")
logger.error("Erro encontrado", error="Connection failed")
```

### LogLevel

Enumeração de níveis de log:

```python
from pepperpy_core import LogLevel

# Níveis disponíveis
level = LogLevel.DEBUG    # Informações detalhadas
level = LogLevel.INFO     # Informações gerais
level = LogLevel.WARNING  # Avisos
level = LogLevel.ERROR    # Erros
level = LogLevel.CRITICAL # Erros críticos
```

### LoggingConfig

Configuração do sistema de logging:

```python
from pepperpy_core import LoggingConfig

# Configuração básica
config = LoggingConfig(
    name="app_logger",
    enabled=True,
    level=LogLevel.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
```

## Exemplos de Uso

### Logger Básico

```python
from pepperpy_core import Logger, LogLevel

async def exemplo_logger_basico():
    # Criar logger
    logger = Logger("app")
    
    # Logs em diferentes níveis
    logger.debug("Iniciando processamento")
    logger.info("Processo em andamento")
    logger.warning("Recurso próximo do limite")
    logger.error("Falha no processo")
    logger.critical("Sistema indisponível")
    
    # Log com metadados
    logger.info(
        "Usuário autenticado",
        user_id=123,
        ip="192.168.1.1"
    )
```

### Handlers Personalizados

```python
from pepperpy_core import BaseHandler, HandlerConfig, LogRecord

class FileHandler(BaseHandler):
    def __init__(self, filename: str, config: HandlerConfig | None = None):
        super().__init__(config)
        self.filename = filename
    
    def emit(self, record: LogRecord) -> None:
        message = self.format(record)
        with open(self.filename, "a") as f:
            f.write(message + "\n")

# Usar handler personalizado
logger = Logger("app")
handler = FileHandler(
    "app.log",
    HandlerConfig(level=LogLevel.INFO)
)
logger.add_handler(handler)
```

## Recursos Avançados

### Logger com Contexto

```python
class ContextLogger(Logger):
    def __init__(self, name: str):
        super().__init__(name)
        self.context = {}
    
    def add_context(self, **kwargs):
        self.context.update(kwargs)
    
    def log(self, level: LogLevel, message: str, **kwargs):
        # Mesclar contexto com kwargs
        context = {**self.context, **kwargs}
        super().log(level, message, **context)

# Usar logger com contexto
logger = ContextLogger("app")
logger.add_context(
    environment="production",
    version="1.0.0"
)
logger.info("Sistema iniciado")  # Inclui contexto
```

### Logger com Formatação Avançada

```python
class JsonHandler(BaseHandler):
    def format(self, record: LogRecord) -> str:
        return json.dumps({
            "timestamp": time.time(),
            "level": record.level.value,
            "message": record.message,
            "logger": record.logger_name,
            "module": record.module,
            "function": record.function,
            "line": record.line,
            "metadata": record.metadata
        })
```

## Melhores Práticas

1. **Níveis de Log**
   - Use níveis apropriados
   - Seja consistente
   - Documente uso
   - Evite logging excessivo

2. **Formatação**
   - Use formatos claros
   - Inclua timestamp
   - Adicione contexto
   - Estruture dados

3. **Handlers**
   - Configure apropriadamente
   - Use múltiplos handlers
   - Implemente rotação
   - Gerencie recursos

4. **Performance**
   - Minimize overhead
   - Use buffering
   - Otimize formatação
   - Monitore volume

5. **Segurança**
   - Sanitize dados sensíveis
   - Controle acesso
   - Valide entrada
   - Proteja logs

## Padrões Comuns

### Logger com Métricas

```python
class MetricsLogger(Logger):
    def __init__(self, name: str):
        super().__init__(name)
        self.metrics = {level: 0 for level in LogLevel}
    
    def log(self, level: LogLevel, message: str, **kwargs):
        self.metrics[level] += 1
        super().log(level, message, **kwargs)
    
    def get_metrics(self) -> dict[str, int]:
        return {
            level.value: count
            for level, count in self.metrics.items()
        }
```

### Logger com Rate Limiting

```python
class RateLimitedLogger(Logger):
    def __init__(self, name: str, rate_limit: float = 1.0):
        super().__init__(name)
        self.rate_limit = rate_limit
        self.last_log = {}
    
    def log(self, level: LogLevel, message: str, **kwargs):
        now = time.time()
        key = (level, message)
        
        if key in self.last_log:
            if now - self.last_log[key] < self.rate_limit:
                return
        
        self.last_log[key] = now
        super().log(level, message, **kwargs)
```

### Logger com Agregação

```python
class AggregatingLogger(Logger):
    def __init__(self, name: str, window: float = 60.0):
        super().__init__(name)
        self.window = window
        self.messages = []
    
    def log(self, level: LogLevel, message: str, **kwargs):
        now = time.time()
        self.messages.append((now, level, message, kwargs))
        
        # Limpar mensagens antigas
        cutoff = now - self.window
        self.messages = [
            m for m in self.messages
            if m[0] > cutoff
        ]
        
        # Agregar se necessário
        if len(self.messages) > 100:
            counts = {}
            for _, lvl, msg, _ in self.messages:
                key = (lvl, msg)
                counts[key] = counts.get(key, 0) + 1
            
            # Log agregado
            for (lvl, msg), count in counts.items():
                super().log(
                    lvl,
                    f"[Agregado x{count}] {msg}"
                )
            
            self.messages.clear()
``` 