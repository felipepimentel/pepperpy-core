# Telemetry (Telemetria)

O módulo Telemetry do PepperPy Core fornece funcionalidades para coleta, armazenamento e gerenciamento de métricas e telemetria da aplicação.

## Componentes Principais

### MetricsCollector

Coletor de métricas com buffer e flush automático:

```python
from pepperpy_core import MetricsCollector

# Criar coletor
collector = MetricsCollector()
await collector.initialize()

# Registrar métrica
await collector.record(
    name="requests_total",
    value=1.0,
    tags={"endpoint": "/api/users"}
)
```

### TelemetryConfig

Configuração do sistema de telemetria:

```python
from pepperpy_core import TelemetryConfig

# Configuração básica
config = TelemetryConfig(
    name="app_telemetry",
    enabled=True,
    buffer_size=1000,
    flush_interval=60.0
)
```

### Metric

Classe para representação de métricas:

```python
from pepperpy_core import Metric
from datetime import datetime

# Criar métrica
metric = Metric(
    name="response_time",
    value=0.123,
    timestamp=datetime.now(),
    tags={"service": "auth"},
    metadata={"version": "1.0.0"}
)
```

## Exemplos de Uso

### Coleta Básica

```python
from pepperpy_core import MetricsCollector

async def exemplo_coleta_basica():
    # Criar coletor
    collector = MetricsCollector()
    await collector.initialize()
    
    try:
        # Registrar métricas
        await collector.record(
            "api_requests",
            1.0,
            tags={"method": "GET", "path": "/users"}
        )
        
        await collector.record(
            "response_time",
            0.234,
            tags={"endpoint": "/users"},
            metadata={"user_id": "123"}
        )
        
        # Verificar estatísticas
        stats = await collector.get_stats()
        print(f"Métricas coletadas: {stats['metrics_count']}")
    finally:
        # Limpar recursos
        await collector.teardown()
```

### Monitoramento de Performance

```python
from pepperpy_core import MetricsCollector
import time

async def exemplo_performance():
    collector = MetricsCollector()
    await collector.initialize()
    
    async def monitor_operation():
        start_time = time.time()
        
        try:
            # Executar operação
            await process_data()
        finally:
            # Registrar duração
            duration = time.time() - start_time
            await collector.record(
                "operation_duration",
                duration,
                tags={
                    "operation": "process_data",
                    "status": "success"
                }
            )
    
    try:
        await monitor_operation()
    finally:
        await collector.teardown()
```

## Recursos Avançados

### Coletor com Agregação

```python
class AggregatingCollector(MetricsCollector):
    def __init__(self):
        super().__init__()
        self.aggregations = {}
    
    async def record(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        # Agregar valores
        key = (name, str(tags))
        if key not in self.aggregations:
            self.aggregations[key] = {
                "count": 0,
                "sum": 0.0,
                "min": float("inf"),
                "max": float("-inf")
            }
        
        agg = self.aggregations[key]
        agg["count"] += 1
        agg["sum"] += value
        agg["min"] = min(agg["min"], value)
        agg["max"] = max(agg["max"], value)
        
        # Registrar valor original
        await super().record(name, value, tags, metadata)
```

### Coletor com Sampling

```python
import random

class SamplingCollector(MetricsCollector):
    def __init__(self, sample_rate: float = 0.1):
        super().__init__()
        self.sample_rate = sample_rate
    
    async def record(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        # Aplicar sampling
        if random.random() < self.sample_rate:
            # Ajustar valor pelo rate
            adjusted_value = value / self.sample_rate
            await super().record(
                name,
                adjusted_value,
                tags,
                {
                    **(metadata or {}),
                    "sampled": True,
                    "sample_rate": self.sample_rate
                }
            )
```

## Melhores Práticas

1. **Coleta**
   - Use nomes descritivos
   - Adicione tags relevantes
   - Inclua metadados
   - Valide valores

2. **Performance**
   - Configure buffer
   - Ajuste intervalos
   - Use sampling
   - Monitore uso

3. **Armazenamento**
   - Implemente persistência
   - Gerencie volume
   - Rotacione dados
   - Backup regular

4. **Monitoramento**
   - Configure alertas
   - Monitore tendências
   - Analise padrões
   - Documente métricas

5. **Manutenção**
   - Limpe dados antigos
   - Atualize configurações
   - Monitore erros
   - Otimize recursos

## Padrões Comuns

### Coletor com Rate Limiting

```python
class RateLimitedCollector(MetricsCollector):
    def __init__(self, max_per_second: float = 100.0):
        super().__init__()
        self.max_per_second = max_per_second
        self.last_flush = time.time()
        self.current_count = 0
    
    async def record(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        now = time.time()
        elapsed = now - self.last_flush
        
        if elapsed >= 1.0:
            # Reset contador
            self.current_count = 0
            self.last_flush = now
        
        if self.current_count < self.max_per_second:
            self.current_count += 1
            await super().record(name, value, tags, metadata)
```

### Coletor com Batch

```python
class BatchCollector(MetricsCollector):
    def __init__(self, batch_size: int = 100):
        super().__init__()
        self.batch_size = batch_size
        self.batch = []
    
    async def record(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        # Adicionar à batch
        self.batch.append({
            "name": name,
            "value": value,
            "tags": tags,
            "metadata": metadata
        })
        
        # Processar batch se cheia
        if len(self.batch) >= self.batch_size:
            batch = self.batch
            self.batch = []
            
            for metric in batch:
                await super().record(
                    metric["name"],
                    metric["value"],
                    metric["tags"],
                    metric["metadata"]
                )
```

### Coletor com Retry

```python
class RetryCollector(MetricsCollector):
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.failed_metrics = []
    
    async def _flush_metrics(self) -> None:
        # Tentar métricas falhas primeiro
        if self.failed_metrics:
            retry_metrics = self.failed_metrics
            self.failed_metrics = []
            
            for metric in retry_metrics:
                try:
                    await self.record(
                        metric["name"],
                        metric["value"],
                        metric["tags"],
                        metric["metadata"]
                    )
                except Exception:
                    metric["retries"] += 1
                    if metric["retries"] < self.max_retries:
                        self.failed_metrics.append(metric)
                    await asyncio.sleep(self.retry_delay)
        
        # Processar métricas normais
        await super()._flush_metrics()
    
    async def record(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        try:
            await super().record(name, value, tags, metadata)
        except Exception:
            self.failed_metrics.append({
                "name": name,
                "value": value,
                "tags": tags,
                "metadata": metadata,
                "retries": 0
            })
```
``` 