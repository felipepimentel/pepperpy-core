# Network (Rede)

O módulo Network do PepperPy Core fornece uma interface assíncrona para operações de rede, incluindo requisições HTTP, WebSockets e gerenciamento de conexões.

## Componentes Principais

### HttpClient

Cliente HTTP assíncrono:

```python
from pepperpy_core import HttpClient

# Criar cliente
client = HttpClient()

# Fazer requisição
response = await client.get("https://api.example.com/data")
data = await response.json()

# Post com dados
response = await client.post(
    "https://api.example.com/users",
    json={"name": "John"}
)
```

### WebSocket

Cliente WebSocket assíncrono:

```python
from pepperpy_core import WebSocket

# Conectar ao servidor
ws = WebSocket("wss://ws.example.com")
await ws.connect()

# Enviar mensagem
await ws.send({"type": "hello"})

# Receber mensagem
message = await ws.receive()
```

### NetworkManager

Gerenciador de conexões:

```python
from pepperpy_core import NetworkManager

# Criar gerenciador
manager = NetworkManager()
await manager.initialize()

# Verificar conectividade
is_online = await manager.check_connection()

# Monitorar conexão
await manager.monitor_connection(
    on_disconnect=lambda: print("Desconectado"),
    on_reconnect=lambda: print("Reconectado")
)
```

## Exemplos de Uso

### Cliente HTTP

```python
from pepperpy_core import HttpClient
from typing import Any

async def exemplo_http():
    # Criar cliente com configuração
    client = HttpClient(
        base_url="https://api.example.com",
        timeout=30.0,
        retries=3
    )
    
    try:
        # GET com parâmetros
        response = await client.get(
            "/users",
            params={"page": 1, "limit": 10}
        )
        users = await response.json()
        
        # POST com JSON
        response = await client.post(
            "/users",
            json={
                "name": "John",
                "email": "john@example.com"
            }
        )
        
        # Upload de arquivo
        files = {"file": open("data.txt", "rb")}
        response = await client.post(
            "/upload",
            files=files
        )
    finally:
        await client.close()
```

### WebSocket com Eventos

```python
from pepperpy_core import WebSocket
import json

async def exemplo_websocket():
    # Conectar ao servidor
    ws = WebSocket("wss://ws.example.com")
    
    try:
        await ws.connect()
        
        # Registrar handlers
        @ws.on("message")
        async def handle_message(data: dict):
            print(f"Mensagem: {data}")
        
        @ws.on("error")
        async def handle_error(error: Exception):
            print(f"Erro: {error}")
        
        # Enviar mensagem
        await ws.send({
            "type": "subscribe",
            "channel": "updates"
        })
        
        # Receber mensagens
        async for message in ws:
            print(f"Recebido: {message}")
    finally:
        await ws.close()
```

## Recursos Avançados

### Cliente com Rate Limit

```python
class RateLimitedClient(HttpClient):
    def __init__(
        self,
        max_requests: int = 100,
        window: float = 60.0
    ):
        super().__init__()
        self.max_requests = max_requests
        self.window = window
        self.requests = []
    
    async def _send_request(self, *args, **kwargs):
        # Limpar requisições antigas
        now = time.time()
        self.requests = [
            t for t in self.requests
            if now - t < self.window
        ]
        
        # Verificar limite
        if len(self.requests) >= self.max_requests:
            raise RateLimitError(
                f"Limite de {self.max_requests} "
                f"requisições por {self.window}s excedido"
            )
        
        # Registrar requisição
        self.requests.append(now)
        
        return await super()._send_request(*args, **kwargs)
```

### WebSocket com Retry

```python
class RetryWebSocket(WebSocket):
    def __init__(
        self,
        url: str,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__(url)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def connect(self) -> None:
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                await super().connect()
                return
            except Exception as e:
                last_error = e
                retries += 1
                if retries < self.max_retries:
                    await asyncio.sleep(
                        self.retry_delay * (2 ** retries)
                    )
        
        raise ConnectionError(
            f"Falha após {retries} tentativas: {last_error}"
        )
```

## Melhores Práticas

1. **HTTP**
   - Use timeouts
   - Implemente retry
   - Valide respostas
   - Feche conexões

2. **WebSocket**
   - Monitore conexão
   - Implemente heartbeat
   - Trate reconexão
   - Valide mensagens

3. **Segurança**
   - Use HTTPS/WSS
   - Valide certificados
   - Proteja credenciais
   - Sanitize dados

4. **Performance**
   - Use connection pool
   - Implemente cache
   - Otimize payloads
   - Monitore latência

5. **Resiliência**
   - Trate erros
   - Implemente fallback
   - Monitore status
   - Registre eventos

## Padrões Comuns

### Cliente com Cache

```python
class CachedClient(HttpClient):
    def __init__(self, cache_ttl: float = 300.0):
        super().__init__()
        self.cache = {}
        self.cache_ttl = cache_ttl
    
    async def get(self, url: str, **kwargs) -> Any:
        # Verificar cache
        cache_key = f"{url}:{json.dumps(kwargs)}"
        now = time.time()
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if now - entry["timestamp"] < self.cache_ttl:
                return entry["data"]
        
        # Fazer requisição
        response = await super().get(url, **kwargs)
        data = await response.json()
        
        # Atualizar cache
        self.cache[cache_key] = {
            "data": data,
            "timestamp": now
        }
        
        return data
```

### WebSocket com Batch

```python
class BatchWebSocket(WebSocket):
    def __init__(
        self,
        url: str,
        batch_size: int = 100,
        flush_interval: float = 1.0
    ):
        super().__init__(url)
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
    
    async def send(self, data: Any) -> None:
        # Adicionar à batch
        self.batch.append(data)
        
        # Verificar flush
        now = time.time()
        should_flush = (
            len(self.batch) >= self.batch_size or
            now - self.last_flush >= self.flush_interval
        )
        
        if should_flush:
            await self._flush()
    
    async def _flush(self) -> None:
        if not self.batch:
            return
        
        # Enviar batch
        try:
            await super().send(self.batch)
        finally:
            self.batch = []
            self.last_flush = time.time()
```

### Cliente com Métricas

```python
class MetricsClient(HttpClient):
    def __init__(self):
        super().__init__()
        self.metrics = {
            "requests": 0,
            "errors": 0,
            "latency": []
        }
    
    async def _send_request(self, *args, **kwargs):
        start_time = time.time()
        
        try:
            response = await super()._send_request(
                *args,
                **kwargs
            )
            self.metrics["requests"] += 1
            return response
        except Exception as e:
            self.metrics["errors"] += 1
            raise
        finally:
            latency = time.time() - start_time
            self.metrics["latency"].append(latency)
    
    def get_metrics(self) -> dict:
        latency = self.metrics["latency"]
        return {
            "total_requests": self.metrics["requests"],
            "total_errors": self.metrics["errors"],
            "avg_latency": sum(latency) / len(latency)
            if latency else 0
        }
```
``` 