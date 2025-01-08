# Pipeline (Pipeline)

O módulo de Pipeline do PepperPy Core fornece uma estrutura para criação e execução de pipelines de processamento, permitindo encadear operações de forma flexível e eficiente.

## Componentes Principais

### Pipeline

Classe base para definição de pipelines:

```python
from pepperpy_core import Pipeline

# Criar pipeline
pipeline = Pipeline("data_processor")

# Adicionar etapas
pipeline.add_step("validate", validate_data)
pipeline.add_step("transform", transform_data)
pipeline.add_step("save", save_data)

# Executar pipeline
result = await pipeline.execute(input_data)
```

### PipelineStep

Classe que representa uma etapa do pipeline:

```python
from pepperpy_core import PipelineStep

class ValidationStep(PipelineStep):
    async def execute(self, data: Any) -> Any:
        if not self.is_valid(data):
            raise ValidationError("Dados inválidos")
        return data
    
    def is_valid(self, data: Any) -> bool:
        # Implementar validação
        return True
```

### PipelineContext

Contexto compartilhado entre etapas do pipeline:

```python
from pepperpy_core import PipelineContext

# Criar contexto
context = PipelineContext(
    metadata={"source": "api"},
    config={"validate": True}
)

# Executar pipeline com contexto
result = await pipeline.execute(data, context=context)
```

## Exemplos de Uso

### Pipeline Básico

```python
from pepperpy_core import Pipeline, PipelineStep

class LoadDataStep(PipelineStep):
    async def execute(self, data: str) -> dict:
        # Carregar dados de arquivo
        with open(data, "r") as f:
            return json.load(f)

class ProcessDataStep(PipelineStep):
    async def execute(self, data: dict) -> dict:
        # Processar dados
        data["processed"] = True
        return data

class SaveDataStep(PipelineStep):
    async def execute(self, data: dict) -> bool:
        # Salvar dados processados
        with open("output.json", "w") as f:
            json.dump(data, f)
        return True

async def exemplo_pipeline_basico():
    # Criar pipeline
    pipeline = Pipeline("data_pipeline")
    
    # Adicionar etapas
    pipeline.add_step("load", LoadDataStep())
    pipeline.add_step("process", ProcessDataStep())
    pipeline.add_step("save", SaveDataStep())
    
    # Executar pipeline
    result = await pipeline.execute("input.json")
```

### Pipeline com Ramificação

```python
from pepperpy_core import Pipeline, PipelineStep

class RouterStep(PipelineStep):
    async def execute(self, data: dict) -> dict:
        if data.get("type") == "user":
            return await self.process_user(data)
        return await self.process_system(data)
    
    async def process_user(self, data: dict) -> dict:
        # Processar dados de usuário
        return data
    
    async def process_system(self, data: dict) -> dict:
        # Processar dados do sistema
        return data

async def exemplo_pipeline_roteado():
    # Criar pipelines
    user_pipeline = Pipeline("user_pipeline")
    system_pipeline = Pipeline("system_pipeline")
    
    # Configurar pipelines específicos
    user_pipeline.add_step("validate", ValidateUserStep())
    user_pipeline.add_step("process", ProcessUserStep())
    
    system_pipeline.add_step("validate", ValidateSystemStep())
    system_pipeline.add_step("process", ProcessSystemStep())
    
    # Criar pipeline principal
    main_pipeline = Pipeline("main_pipeline")
    main_pipeline.add_step("route", RouterStep())
    main_pipeline.add_step("log", LogStep())
    
    # Executar pipeline
    result = await main_pipeline.execute(input_data)
```

## Recursos Avançados

### Pipeline com Retry

```python
class RetryPipeline(Pipeline):
    def __init__(
        self,
        name: str,
        max_retries: int = 3,
        delay: float = 1.0
    ):
        super().__init__(name)
        self.max_retries = max_retries
        self.delay = delay
    
    async def execute(
        self,
        data: Any,
        context: PipelineContext | None = None
    ) -> Any:
        retries = 0
        while True:
            try:
                return await super().execute(data, context)
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    raise
                
                await asyncio.sleep(self.delay)
                continue
```

### Pipeline com Cache

```python
class CachedPipeline(Pipeline):
    def __init__(self, name: str, cache_time: int = 300):
        super().__init__(name)
        self.cache = {}
        self.cache_time = cache_time
    
    async def execute(
        self,
        data: Any,
        context: PipelineContext | None = None
    ) -> Any:
        cache_key = self._get_cache_key(data)
        
        # Verificar cache
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry["timestamp"] < self.cache_time:
                return entry["result"]
        
        # Executar pipeline
        result = await super().execute(data, context)
        
        # Atualizar cache
        self.cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }
        
        return result
    
    def _get_cache_key(self, data: Any) -> str:
        return str(hash(str(data)))
```

## Melhores Práticas

1. **Design de Pipeline**
   - Mantenha etapas focadas
   - Use contexto apropriadamente
   - Implemente validações
   - Documente fluxo de dados

2. **Tratamento de Erros**
   - Implemente retry quando apropriado
   - Registre erros adequadamente
   - Mantenha contexto de erro
   - Permita recuperação

3. **Performance**
   - Use cache quando possível
   - Otimize etapas pesadas
   - Monitore tempo de execução
   - Implemente timeouts

4. **Manutenção**
   - Monitore execução
   - Mantenha logs detalhados
   - Documente mudanças
   - Teste cada etapa

5. **Extensibilidade**
   - Projete para extensão
   - Use interfaces claras
   - Permita customização
   - Mantenha compatibilidade

## Padrões Comuns

### Pipeline com Validação

```python
class ValidatedPipeline(Pipeline):
    def __init__(self, name: str):
        super().__init__(name)
        self.validators = []
    
    def add_validator(self, validator: callable):
        self.validators.append(validator)
    
    async def execute(
        self,
        data: Any,
        context: PipelineContext | None = None
    ) -> Any:
        # Executar validadores
        for validator in self.validators:
            if not await validator(data):
                raise ValidationError(
                    f"Validação falhou: {validator.__name__}"
                )
        
        # Executar pipeline
        return await super().execute(data, context)
```

### Pipeline com Métricas

```python
class MetricsPipeline(Pipeline):
    def __init__(self, name: str):
        super().__init__(name)
        self.metrics = {}
    
    async def execute(
        self,
        data: Any,
        context: PipelineContext | None = None
    ) -> Any:
        start_time = time.time()
        
        try:
            result = await super().execute(data, context)
            self._record_success()
            return result
        except Exception as e:
            self._record_error(str(e))
            raise
        finally:
            duration = time.time() - start_time
            self._record_duration(duration)
    
    def _record_success(self):
        self.metrics.setdefault("successes", 0)
        self.metrics["successes"] += 1
    
    def _record_error(self, error: str):
        self.metrics.setdefault("errors", {})
        self.metrics["errors"][error] = \
            self.metrics["errors"].get(error, 0) + 1
    
    def _record_duration(self, duration: float):
        self.metrics.setdefault("durations", [])
        self.metrics["durations"].append(duration)
```

### Pipeline com Logging

```python
class LoggedPipeline(Pipeline):
    def __init__(self, name: str):
        super().__init__(name)
        self.logger = logging.getLogger(name)
    
    async def execute(
        self,
        data: Any,
        context: PipelineContext | None = None
    ) -> Any:
        self.logger.info(
            "Iniciando execução",
            extra={"data": data, "context": context}
        )
        
        try:
            result = await super().execute(data, context)
            self.logger.info(
                "Execução concluída",
                extra={"result": result}
            )
            return result
        except Exception as e:
            self.logger.error(
                "Erro na execução",
                exc_info=True,
                extra={"error": str(e)}
            )
            raise
``` 