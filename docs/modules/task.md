# Task System (Sistema de Tarefas)

O Sistema de Tarefas do PepperPy Core fornece uma infraestrutura robusta para gerenciamento e execução de tarefas assíncronas. Ele suporta execução prioritária, cancelamento de tarefas, pools de workers e monitoramento de estado.

## Componentes Principais

### TaskState

Enumeração que representa os possíveis estados de uma tarefa:

```python
from pepperpy_core import TaskState

# Estados disponíveis
TaskState.PENDING    # Tarefa aguardando execução
TaskState.RUNNING    # Tarefa em execução
TaskState.COMPLETED  # Tarefa concluída com sucesso
TaskState.FAILED     # Tarefa falhou durante execução
TaskState.CANCELLED  # Tarefa foi cancelada
```

### TaskConfig

Configuração para o gerenciamento de tarefas:

```python
from pepperpy_core import TaskConfig

config = TaskConfig(
    name="processor",
    max_workers=4,      # Número máximo de workers concorrentes
    max_queue_size=100, # Tamanho máximo da fila (0 = ilimitado)
    metadata={"environment": "production"}
)
```

### Task

A implementação principal de uma tarefa:

```python
from pepperpy_core import Task

async def process_data(data: dict) -> dict:
    # Processamento assíncrono
    return processed_data

# Criar uma tarefa
task = Task("process_user_data", process_data, user_data)

# Executar a tarefa
result = await task.run()
print(f"Status: {result.status}")
print(f"Resultado: {result.result}")
```

## Exemplos de Uso

### Tarefa Básica

```python
from pepperpy_core import Task, TaskState

async def exemplo_tarefa_basica():
    # Definir função assíncrona
    async def calcular_soma(a: int, b: int) -> int:
        await asyncio.sleep(1)  # Simulando processamento
        return a + b
    
    # Criar e executar tarefa
    task = Task("soma", calcular_soma, 10, 20)
    result = await task.run()
    
    assert result.status == TaskState.COMPLETED
    assert result.result == 30
```

### Gerenciamento de Erros

```python
from pepperpy_core import Task, TaskError

async def exemplo_tratamento_erro():
    async def operacao_arriscada():
        raise ValueError("Algo deu errado")

    task = Task("operacao_arriscada", operacao_arriscada)
    try:
        await task.run()
    except TaskError as e:
        print(f"Tarefa falhou: {e}")
        print(f"Estado: {task.status}")  # TaskState.FAILED
        print(f"Erro original: {task.error}")
```

### Fila de Tarefas com Prioridade

```python
from pepperpy_core import TaskQueue, Task

async def exemplo_fila_prioridade():
    queue = TaskQueue(maxsize=100)
    
    # Adicionar tarefas com diferentes prioridades
    await queue.put(task1, priority=1)  # Baixa prioridade
    await queue.put(task2, priority=3)  # Alta prioridade
    await queue.put(task3, priority=2)  # Média prioridade
    
    # Processar tarefas (serão executadas em ordem de prioridade)
    while True:
        task = await queue.get()
        try:
            await task.run()
        finally:
            queue.task_done()
```

## Recursos Avançados

### Pool de Workers

```python
from pepperpy_core import TaskManager, TaskConfig

async def exemplo_pool_workers():
    # Configurar pool com 4 workers
    config = TaskConfig(
        name="worker_pool",
        max_workers=4,
        max_queue_size=100
    )
    manager = TaskManager(config)
    
    # Adicionar múltiplas tarefas
    for data in dataset:
        task = Task(f"process_{data['id']}", process_data, data)
        await manager.add_task(task)
    
    # Processar todas as tarefas com 4 workers
    await manager.execute_tasks()
```

### Cancelamento de Tarefas

```python
async def exemplo_cancelamento():
    async def long_operation():
        await asyncio.sleep(10)
        return "completed"

    task = Task("long_running", long_operation)
    
    # Em uma corotina
    task_execution = asyncio.create_task(task.run())
    
    # Em outra corotina
    await asyncio.sleep(2)  # Esperar um pouco
    await task.cancel()     # Cancelar a tarefa
    
    assert task.status == TaskState.CANCELLED
```

## Melhores Práticas

1. **Nomeação de Tarefas**
   - Use nomes descritivos e únicos
   - Inclua identificadores relevantes
   - Mantenha um padrão consistente
   - Documente o propósito da tarefa

2. **Gerenciamento de Prioridades**
   - Use prioridades com moderação
   - Documente os níveis de prioridade
   - Reserve prioridades altas para tarefas críticas
   - Evite starvation de tarefas de baixa prioridade

3. **Tratamento de Erros**
   - Sempre implemente tratamento de erros
   - Registre erros apropriadamente
   - Forneça contexto nos erros
   - Implemente retry quando apropriado

4. **Monitoramento**
   - Monitore o estado das tarefas
   - Implemente logging adequado
   - Acompanhe métricas de performance
   - Configure alertas para falhas

5. **Recursos**
   - Gerencie recursos adequadamente
   - Implemente timeouts
   - Limite o número de workers
   - Monitore uso de memória

## Padrões Comuns

### Cadeia de Tarefas

```python
async def exemplo_cadeia_tarefas():
    async def step1(data: dict) -> dict:
        return {"step1": "done", **data}
    
    async def step2(data: dict) -> dict:
        return {"step2": "done", **data}
    
    # Criar cadeia
    task1 = Task("step1", step1, {"input": "data"})
    result1 = await task1.run()
    
    task2 = Task("step2", step2, result1.result)
    final_result = await task2.run()
```

### Tarefas Periódicas

```python
class PeriodicTask:
    def __init__(self, name: str, interval: float):
        self.name = name
        self.interval = interval
        self.running = False
    
    async def start(self):
        self.running = True
        while self.running:
            task = Task(f"{self.name}_{int(time.time())}", self.run)
            await task.run()
            await asyncio.sleep(self.interval)
    
    async def stop(self):
        self.running = False
    
    async def run(self):
        # Implementar lógica da tarefa
        pass
```

### Tarefas com Retry

```python
class RetryableTask:
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        self.max_retries = max_retries
        self.delay = delay
    
    async def execute(self, task: Task) -> TaskResult:
        retries = 0
        while retries <= self.max_retries:
            try:
                return await task.run()
            except TaskError:
                retries += 1
                if retries <= self.max_retries:
                    await asyncio.sleep(self.delay)
                    continue
                raise
``` 