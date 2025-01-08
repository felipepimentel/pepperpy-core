# Storage (Armazenamento)

O módulo Storage do PepperPy Core fornece uma interface unificada para operações de armazenamento, suportando diferentes backends como sistema de arquivos, memória, e armazenamento em nuvem.

## Componentes Principais

### StorageManager

Gerenciador central de armazenamento:

```python
from pepperpy_core import StorageManager

# Criar gerenciador
manager = StorageManager()

# Salvar dados
await manager.put("config.json", '{"debug": true}')

# Carregar dados
data = await manager.get("config.json")
```

### FileStorage

Armazenamento em arquivo:

```python
from pepperpy_core import FileStorage

# Criar storage
storage = FileStorage(base_path="data")

# Salvar arquivo
await storage.write("logs/app.log", "log message")

# Ler arquivo
content = await storage.read("logs/app.log")
```

### MemoryStorage

Armazenamento em memória:

```python
from pepperpy_core import MemoryStorage

# Criar storage
storage = MemoryStorage()

# Armazenar dados
await storage.set("cache:user:123", user_data)

# Recuperar dados
data = await storage.get("cache:user:123")
```

## Exemplos de Uso

### Gerenciamento de Arquivos

```python
from pepperpy_core import StorageManager
from typing import Optional

async def exemplo_arquivos():
    # Criar gerenciador
    manager = StorageManager()
    
    try:
        # Salvar arquivo
        content = "Hello World"
        await manager.put(
            "hello.txt",
            content,
            encoding="utf-8"
        )
        
        # Verificar existência
        exists = await manager.exists("hello.txt")
        
        # Ler arquivo
        if exists:
            content = await manager.get(
                "hello.txt",
                encoding="utf-8"
            )
            print(f"Conteúdo: {content}")
        
        # Listar arquivos
        files = await manager.list("*.txt")
        for file in files:
            print(f"Arquivo: {file}")
    finally:
        # Limpar recursos
        await manager.cleanup()
```

### Cache em Memória

```python
from pepperpy_core import MemoryStorage
import json

async def exemplo_cache():
    # Criar storage
    storage = MemoryStorage()
    
    # Dados para cache
    user_data = {
        "id": "123",
        "name": "John"
    }
    
    try:
        # Salvar no cache
        key = f"user:{user_data['id']}"
        await storage.set(
            key,
            json.dumps(user_data)
        )
        
        # Recuperar do cache
        if await storage.exists(key):
            data = await storage.get(key)
            user = json.loads(data)
            print(f"Usuário: {user['name']}")
        
        # Limpar cache
        await storage.delete(key)
    finally:
        await storage.cleanup()
```

## Recursos Avançados

### Storage com Compressão

```python
class CompressedStorage(StorageManager):
    def __init__(self):
        super().__init__()
        self.compression = "gzip"
    
    async def put(
        self,
        path: str,
        content: bytes,
        **kwargs
    ) -> None:
        # Comprimir conteúdo
        compressed = gzip.compress(content)
        
        # Salvar comprimido
        await super().put(
            path,
            compressed,
            **kwargs
        )
    
    async def get(
        self,
        path: str,
        **kwargs
    ) -> bytes:
        # Carregar comprimido
        compressed = await super().get(
            path,
            **kwargs
        )
        
        # Descomprimir
        return gzip.decompress(compressed)
```

### Storage com Encriptação

```python
class EncryptedStorage(StorageManager):
    def __init__(self, key: bytes):
        super().__init__()
        self.key = key
        self.cipher = Fernet(key)
    
    async def put(
        self,
        path: str,
        content: bytes,
        **kwargs
    ) -> None:
        # Encriptar conteúdo
        encrypted = self.cipher.encrypt(content)
        
        # Salvar encriptado
        await super().put(
            path,
            encrypted,
            **kwargs
        )
    
    async def get(
        self,
        path: str,
        **kwargs
    ) -> bytes:
        # Carregar encriptado
        encrypted = await super().get(
            path,
            **kwargs
        )
        
        # Desencriptar
        return self.cipher.decrypt(encrypted)
```

## Melhores Práticas

1. **Arquivos**
   - Use paths relativos
   - Valide extensões
   - Limite tamanhos
   - Limpe recursos

2. **Cache**
   - Defina TTL
   - Limite tamanho
   - Monitore uso
   - Implemente LRU

3. **Performance**
   - Use buffers
   - Comprima dados
   - Otimize I/O
   - Cache seletivo

4. **Segurança**
   - Valide paths
   - Encripte dados
   - Controle acesso
   - Backup regular

5. **Manutenção**
   - Monitore espaço
   - Limpe cache
   - Arquive dados
   - Verifique integridade

## Padrões Comuns

### Storage com Cache

```python
class CachedStorage(StorageManager):
    def __init__(self, ttl: float = 300.0):
        super().__init__()
        self.ttl = ttl
        self.cache = {}
    
    async def get(
        self,
        path: str,
        **kwargs
    ) -> bytes:
        # Verificar cache
        now = time.time()
        if path in self.cache:
            entry = self.cache[path]
            if now - entry["timestamp"] < self.ttl:
                return entry["data"]
        
        # Carregar dados
        data = await super().get(path, **kwargs)
        
        # Atualizar cache
        self.cache[path] = {
            "data": data,
            "timestamp": now
        }
        
        return data
    
    async def put(
        self,
        path: str,
        content: bytes,
        **kwargs
    ) -> None:
        # Invalidar cache
        self.cache.pop(path, None)
        
        # Salvar dados
        await super().put(path, content, **kwargs)
```

### Storage com Retry

```python
class RetryStorage(StorageManager):
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def get(
        self,
        path: str,
        **kwargs
    ) -> bytes:
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                return await super().get(
                    path,
                    **kwargs
                )
            except Exception as e:
                last_error = e
                retries += 1
                if retries < self.max_retries:
                    await asyncio.sleep(
                        self.retry_delay * (2 ** retries)
                    )
        
        raise StorageError(
            f"Falha após {retries} tentativas: {last_error}"
        )
```

### Storage com Métricas

```python
class MetricsStorage(StorageManager):
    def __init__(self):
        super().__init__()
        self.metrics = {
            "reads": 0,
            "writes": 0,
            "errors": 0,
            "bytes_read": 0,
            "bytes_written": 0
        }
    
    async def get(
        self,
        path: str,
        **kwargs
    ) -> bytes:
        try:
            data = await super().get(path, **kwargs)
            self.metrics["reads"] += 1
            self.metrics["bytes_read"] += len(data)
            return data
        except Exception as e:
            self.metrics["errors"] += 1
            raise
    
    async def put(
        self,
        path: str,
        content: bytes,
        **kwargs
    ) -> None:
        try:
            await super().put(path, content, **kwargs)
            self.metrics["writes"] += 1
            self.metrics["bytes_written"] += len(content)
        except Exception as e:
            self.metrics["errors"] += 1
            raise
    
    def get_metrics(self) -> dict:
        return {
            "total_reads": self.metrics["reads"],
            "total_writes": self.metrics["writes"],
            "total_errors": self.metrics["errors"],
            "total_bytes_read": self.metrics["bytes_read"],
            "total_bytes_written": self.metrics["bytes_written"]
        }
``` 