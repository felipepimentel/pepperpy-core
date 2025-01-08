# IO (Input/Output)

O módulo IO do PepperPy Core fornece uma interface assíncrona para operações de entrada e saída, incluindo leitura e escrita de arquivos, streams e buffers.

## Componentes Principais

### AsyncFile

Classe para operações assíncronas em arquivos:

```python
from pepperpy_core import AsyncFile

# Abrir arquivo
async with AsyncFile("data.txt", "r") as file:
    # Ler conteúdo
    content = await file.read()
    print(content)

# Escrever em arquivo
async with AsyncFile("output.txt", "w") as file:
    await file.write("Hello World!")
```

### AsyncBuffer

Buffer para operações assíncronas:

```python
from pepperpy_core import AsyncBuffer

# Criar buffer
buffer = AsyncBuffer()

# Escrever dados
await buffer.write(b"Hello")
await buffer.write(b" World!")

# Ler dados
data = await buffer.read()  # b"Hello World!"
```

### AsyncStream

Stream para operações assíncronas:

```python
from pepperpy_core import AsyncStream

# Criar stream
stream = AsyncStream()

# Processar dados
async for chunk in stream:
    # Processar chunk
    process_data(chunk)
```

## Exemplos de Uso

### Leitura de Arquivo

```python
from pepperpy_core import AsyncFile

async def exemplo_leitura():
    # Abrir arquivo para leitura
    async with AsyncFile("data.txt", "r") as file:
        # Ler linha por linha
        async for line in file:
            print(f"Linha: {line.strip()}")
        
        # Voltar ao início
        await file.seek(0)
        
        # Ler tudo
        content = await file.read()
        print(f"Conteúdo: {content}")
```

### Escrita em Arquivo

```python
from pepperpy_core import AsyncFile
import json

async def exemplo_escrita():
    # Dados para escrever
    data = {
        "name": "John",
        "age": 30
    }
    
    # Escrever JSON
    async with AsyncFile("user.json", "w") as file:
        # Converter e escrever
        json_str = json.dumps(data)
        await file.write(json_str)
        
        # Forçar flush
        await file.flush()
```

## Recursos Avançados

### Buffer com Compressão

```python
class CompressedBuffer(AsyncBuffer):
    def __init__(self):
        super().__init__()
        self.compression = "gzip"
    
    async def write(self, data: bytes) -> None:
        # Comprimir dados
        compressed = gzip.compress(data)
        await super().write(compressed)
    
    async def read(self) -> bytes:
        # Ler e descomprimir
        data = await super().read()
        return gzip.decompress(data)
```

### Stream com Transformação

```python
class TransformStream(AsyncStream):
    def __init__(self, transform_func: callable):
        super().__init__()
        self.transform = transform_func
    
    async def process(self, chunk: bytes) -> bytes:
        # Transformar chunk
        return self.transform(chunk)
    
    async def __aiter__(self):
        async for chunk in super().__aiter__():
            # Transformar e yield
            yield await self.process(chunk)
```

## Melhores Práticas

1. **Arquivos**
   - Use context managers
   - Feche recursos
   - Trate erros
   - Valide paths

2. **Buffers**
   - Gerencie memória
   - Limite tamanho
   - Implemente flush
   - Otimize operações

3. **Streams**
   - Processe em chunks
   - Controle fluxo
   - Implemente backpressure
   - Libere recursos

4. **Performance**
   - Use buffers apropriados
   - Otimize tamanho de chunk
   - Cache quando possível
   - Monitore memória

5. **Segurança**
   - Valide paths
   - Limite acesso
   - Sanitize dados
   - Proteja recursos

## Padrões Comuns

### Arquivo com Cache

```python
class CachedFile(AsyncFile):
    def __init__(self, path: str, mode: str = "r"):
        super().__init__(path, mode)
        self.cache = {}
    
    async def read(self) -> str:
        # Verificar cache
        if self.name in self.cache:
            return self.cache[self.name]
        
        # Ler e cachear
        content = await super().read()
        self.cache[self.name] = content
        return content
    
    async def write(self, data: str) -> None:
        # Escrever e invalidar cache
        await super().write(data)
        self.cache.pop(self.name, None)
```

### Buffer com Rate Limit

```python
class RateLimitedBuffer(AsyncBuffer):
    def __init__(self, rate_limit: float = 1024):
        super().__init__()
        self.rate_limit = rate_limit
        self.last_write = time.time()
    
    async def write(self, data: bytes) -> None:
        # Controlar taxa
        now = time.time()
        elapsed = now - self.last_write
        
        if len(data) / elapsed > self.rate_limit:
            await asyncio.sleep(
                len(data) / self.rate_limit - elapsed
            )
        
        await super().write(data)
        self.last_write = time.time()
```

### Stream com Retry

```python
class RetryStream(AsyncStream):
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def process(self, chunk: bytes) -> bytes:
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                return await self._process(chunk)
            except Exception as e:
                last_error = e
                retries += 1
                if retries < self.max_retries:
                    await asyncio.sleep(
                        self.retry_delay * (2 ** retries)
                    )
        
        raise Exception(
            f"Failed after {retries} retries: {last_error}"
        )
    
    async def _process(self, chunk: bytes) -> bytes:
        # Implementação específica
        return chunk
```
``` 