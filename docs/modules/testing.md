# Testing (Testes)

O módulo Testing do PepperPy Core fornece utilitários e classes base para testes, incluindo suporte para testes assíncronos, mocks, fixtures e asserções customizadas.

## Componentes Principais

### AsyncTestCase

Classe base para testes assíncronos:

```python
from pepperpy_core import AsyncTestCase

class TestExample(AsyncTestCase):
    async def setUp(self):
        # Setup assíncrono
        self.client = await create_client()
    
    async def test_operation(self):
        # Teste assíncrono
        result = await self.client.execute()
        self.assertEqual(result, "success")
    
    async def tearDown(self):
        # Cleanup assíncrono
        await self.client.close()
```

### MockManager

Gerenciador de mocks:

```python
from pepperpy_core import MockManager

# Criar mock
mock = MockManager()

# Configurar comportamento
mock.when("get_user").return_value({"id": "123"})

# Verificar chamadas
assert mock.verify("get_user").called_once()
```

### TestFixtures

Fixtures para testes:

```python
from pepperpy_core import fixture

@fixture
async def database():
    # Setup
    db = await create_database()
    yield db
    # Cleanup
    await db.close()
```

## Exemplos de Uso

### Teste de API

```python
from pepperpy_core import AsyncTestCase, MockClient
from typing import Optional

class TestAPI(AsyncTestCase):
    async def setUp(self):
        # Criar cliente mock
        self.client = MockClient()
        
        # Configurar respostas
        self.client.mock_response(
            "GET",
            "/users/123",
            {
                "id": "123",
                "name": "John"
            }
        )
    
    async def test_get_user(self):
        # Fazer requisição
        response = await self.client.get("/users/123")
        
        # Verificar resposta
        self.assertEqual(response.status, 200)
        data = await response.json()
        self.assertEqual(data["name"], "John")
    
    async def test_create_user(self):
        # Dados do teste
        user_data = {
            "name": "Jane",
            "email": "jane@example.com"
        }
        
        # Fazer requisição
        response = await self.client.post(
            "/users",
            json=user_data
        )
        
        # Verificar resposta
        self.assertEqual(response.status, 201)
        data = await response.json()
        self.assertIn("id", data)
```

### Teste com Database

```python
from pepperpy_core import AsyncTestCase, fixture
import asyncpg

class TestDatabase(AsyncTestCase):
    @fixture
    async def database(self):
        # Criar conexão
        conn = await asyncpg.connect(
            "postgresql://localhost/test"
        )
        
        # Setup
        await conn.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name TEXT
            )
        """)
        
        yield conn
        
        # Cleanup
        await conn.execute("DROP TABLE users")
        await conn.close()
    
    async def test_insert_user(self):
        # Inserir dados
        user_id = await self.database.fetchval("""
            INSERT INTO users (name)
            VALUES ($1)
            RETURNING id
        """, "John")
        
        # Verificar inserção
        row = await self.database.fetchrow("""
            SELECT * FROM users WHERE id = $1
        """, user_id)
        
        self.assertEqual(row["name"], "John")
```

## Recursos Avançados

### Asserções Customizadas

```python
class CustomAssertions:
    async def assertEventEmitted(
        self,
        emitter: EventEmitter,
        event_name: str,
        timeout: float = 1.0
    ):
        # Esperar evento
        try:
            event = await asyncio.wait_for(
                emitter.wait_for(event_name),
                timeout
            )
            return event
        except asyncio.TimeoutError:
            self.fail(
                f"Evento {event_name} não foi emitido"
            )
    
    async def assertStateChanged(
        self,
        store: StateStore,
        path: str,
        expected: Any,
        timeout: float = 1.0
    ):
        # Esperar mudança
        start_time = time.time()
        while time.time() - start_time < timeout:
            value = await store.get(path)
            if value == expected:
                return
            await asyncio.sleep(0.1)
        
        self.fail(
            f"Estado {path} não mudou para {expected}"
        )
```

### Mock Contextual

```python
class ContextMock:
    def __init__(self):
        self.contexts = {}
    
    def when(self, context: str):
        return ContextBuilder(self, context)
    
    async def execute(
        self,
        context: str,
        *args,
        **kwargs
    ):
        if context not in self.contexts:
            raise ValueError(
                f"Contexto {context} não configurado"
            )
        
        handler = self.contexts[context]
        return await handler(*args, **kwargs)

class ContextBuilder:
    def __init__(
        self,
        mock: ContextMock,
        context: str
    ):
        self.mock = mock
        self.context = context
    
    def then(self, handler: callable):
        self.mock.contexts[self.context] = handler
        return self
```

## Melhores Práticas

1. **Organização**
   - Agrupe testes
   - Isole recursos
   - Use fixtures
   - Documente casos

2. **Performance**
   - Mock I/O
   - Paralelize testes
   - Otimize setup
   - Cache recursos

3. **Cobertura**
   - Teste edge cases
   - Valide erros
   - Verifique tipos
   - Monitore métricas

4. **Manutenção**
   - Atualize testes
   - Remova duplicação
   - Refatore código
   - Documente mudanças

5. **Qualidade**
   - Valide inputs
   - Verifique outputs
   - Teste integrações
   - Monitore falhas

## Padrões Comuns

### Teste com Retry

```python
class RetryTest(AsyncTestCase):
    async def assertEventually(
        self,
        condition: callable,
        timeout: float = 5.0,
        interval: float = 0.1,
        message: Optional[str] = None
    ):
        start_time = time.time()
        last_error = None
        
        while time.time() - start_time < timeout:
            try:
                await condition()
                return
            except AssertionError as e:
                last_error = e
                await asyncio.sleep(interval)
        
        if message is None and last_error is not None:
            message = str(last_error)
        
        self.fail(
            message or "Condição não satisfeita"
        )
```

### Teste com Isolamento

```python
class IsolatedTest(AsyncTestCase):
    async def setUp(self):
        # Criar ambiente isolado
        self.temp_dir = tempfile.mkdtemp()
        self.old_env = os.environ.copy()
        
        # Configurar ambiente
        os.environ.update({
            "TEST_MODE": "true",
            "DATA_DIR": self.temp_dir
        })
    
    async def tearDown(self):
        # Restaurar ambiente
        os.environ.clear()
        os.environ.update(self.old_env)
        
        # Limpar recursos
        shutil.rmtree(self.temp_dir)
```

### Teste com Métricas

```python
class MetricsTest(AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = {
            "setup_time": [],
            "test_time": [],
            "teardown_time": []
        }
    
    async def setUp(self):
        start_time = time.time()
        await super().setUp()
        self.metrics["setup_time"].append(
            time.time() - start_time
        )
    
    async def run(self, *args, **kwargs):
        start_time = time.time()
        await super().run(*args, **kwargs)
        self.metrics["test_time"].append(
            time.time() - start_time
        )
    
    async def tearDown(self):
        start_time = time.time()
        await super().tearDown()
        self.metrics["teardown_time"].append(
            time.time() - start_time
        )
    
    def get_metrics(self) -> dict:
        return {
            name: {
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times)
            }
            for name, times in self.metrics.items()
            if times
        }
``` 