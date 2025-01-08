# Utils (Utilitários)

O módulo Utils do PepperPy Core fornece uma coleção de funções e classes utilitárias para tarefas comuns, incluindo manipulação de strings, datas, arquivos e outros recursos.

## Funções de String

### string_utils

Funções para manipulação de strings:

```python
from pepperpy_core.utils import (
    slugify,
    camel_to_snake,
    snake_to_camel
)

# Criar slug
text = "Hello World!"
slug = slugify(text)  # "hello-world"

# Converter casos
camel = "myVariableName"
snake = camel_to_snake(camel)  # "my_variable_name"

snake = "my_variable_name"
camel = snake_to_camel(snake)  # "myVariableName"
```

### text_utils

Funções para processamento de texto:

```python
from pepperpy_core.utils import (
    truncate,
    word_wrap,
    remove_accents
)

# Truncar texto
text = "Lorem ipsum dolor sit amet"
short = truncate(text, length=10)  # "Lorem ip..."

# Quebrar texto
wrapped = word_wrap(text, width=20)

# Remover acentos
text = "café"
clean = remove_accents(text)  # "cafe"
```

## Funções de Data/Hora

### date_utils

Funções para manipulação de datas:

```python
from pepperpy_core.utils import (
    format_duration,
    parse_duration,
    to_local_time
)

# Formatar duração
seconds = 3665
formatted = format_duration(seconds)  # "1h 1m 5s"

# Converter duração
duration = "2h 30m"
seconds = parse_duration(duration)  # 9000

# Converter timezone
utc_time = datetime.now(timezone.utc)
local = to_local_time(utc_time)
```

## Funções de Arquivo

### file_utils

Funções para manipulação de arquivos:

```python
from pepperpy_core.utils import (
    ensure_dir,
    safe_filename,
    get_file_hash
)

# Garantir diretório
path = "data/temp"
ensure_dir(path)

# Sanitizar nome de arquivo
name = "My File (1).txt"
safe = safe_filename(name)  # "my-file-1.txt"

# Calcular hash
file_path = "data.txt"
hash_md5 = await get_file_hash(file_path)
```

## Funções de Rede

### network_utils

Funções para operações de rede:

```python
from pepperpy_core.utils import (
    is_valid_ip,
    get_free_port,
    wait_for_port
)

# Validar IP
ip = "192.168.1.1"
valid = is_valid_ip(ip)  # True

# Obter porta livre
port = await get_free_port()  # 8080

# Esperar porta
await wait_for_port("localhost", 5432, timeout=30.0)
```

## Funções de Sistema

### system_utils

Funções para operações do sistema:

```python
from pepperpy_core.utils import (
    get_memory_usage,
    get_cpu_usage,
    get_disk_usage
)

# Uso de memória
memory = await get_memory_usage()
print(f"Memória: {memory}%")

# Uso de CPU
cpu = await get_cpu_usage()
print(f"CPU: {cpu}%")

# Uso de disco
disk = await get_disk_usage("/")
print(f"Disco: {disk}%")
```

## Classes Utilitárias

### Singleton

Base para classes singleton:

```python
from pepperpy_core.utils import Singleton

class MyService(Singleton):
    def __init__(self):
        self.initialized = False
    
    def initialize(self):
        if not self.initialized:
            # Inicialização
            self.initialized = True

# Usar singleton
service1 = MyService()
service2 = MyService()  # Mesma instância
```

### LRUCache

Cache com política LRU:

```python
from pepperpy_core.utils import LRUCache

# Criar cache
cache = LRUCache[str](max_size=1000)

# Usar cache
cache.set("key", "value")
value = cache.get("key")  # "value"

# Estatísticas
stats = cache.get_stats()
print(f"Hit ratio: {stats.hit_ratio}")
```

## Decoradores

### decorators

Decoradores úteis:

```python
from pepperpy_core.utils import (
    retry,
    timeout,
    measure_time
)

# Retry em falhas
@retry(max_retries=3, delay=1.0)
async def fetch_data():
    # Código que pode falhar
    pass

# Timeout
@timeout(seconds=5.0)
async def slow_operation():
    # Operação lenta
    pass

# Medição de tempo
@measure_time
async def process_data():
    # Código a ser medido
    pass
```

## Melhores Práticas

1. **Strings**
   - Valide entrada
   - Use codificação apropriada
   - Trate caracteres especiais
   - Normalize texto

2. **Datas**
   - Use UTC quando possível
   - Valide formatos
   - Considere timezones
   - Trate exceções

3. **Arquivos**
   - Valide caminhos
   - Use paths absolutos
   - Trate permissões
   - Limpe recursos

4. **Rede**
   - Valide endereços
   - Use timeouts
   - Trate erros
   - Monitore conexões

5. **Sistema**
   - Monitore recursos
   - Trate limites
   - Cache resultados
   - Otimize uso

## Padrões Comuns

### Retry com Backoff

```python
from pepperpy_core.utils import retry

# Configurar retry
@retry(
    max_retries=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(ConnectionError,)
)
async def fetch_with_retry():
    # Código com retry
    pass
```

### Cache com TTL

```python
from pepperpy_core.utils import TTLCache

# Criar cache
cache = TTLCache[str](
    max_size=1000,
    ttl=300.0  # 5 minutos
)

# Usar cache
await cache.set("key", "value")
value = await cache.get("key")

# Limpar expirados
await cache.cleanup()
```

### Medição de Recursos

```python
from pepperpy_core.utils import ResourceMonitor

# Criar monitor
monitor = ResourceMonitor()

# Iniciar monitoramento
async with monitor:
    # Código a ser monitorado
    await process_data()

# Obter métricas
metrics = monitor.get_metrics()
print(f"CPU Máximo: {metrics.max_cpu}%")
print(f"Memória Média: {metrics.avg_memory}%")
```
``` 