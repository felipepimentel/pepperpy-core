# State (Estado)

O módulo State do PepperPy Core fornece um sistema robusto para gerenciamento de estado da aplicação, incluindo persistência, sincronização e observabilidade de mudanças.

## Componentes Principais

### StateManager

Gerenciador central de estado:

```python
from pepperpy_core import StateManager

# Criar gerenciador
manager = StateManager()

# Definir estado
await manager.set("user.preferences", {
    "theme": "dark",
    "language": "pt"
})

# Obter estado
preferences = await manager.get("user.preferences")
```

### StateStore

Armazenamento de estado:

```python
from pepperpy_core import StateStore

# Criar store
store = StateStore()

# Registrar estado
store.register("counter", initial_value=0)

# Atualizar estado
await store.update("counter", lambda x: x + 1)
```

### StateObserver

Observador de mudanças:

```python
from pepperpy_core import StateObserver

# Criar observador
observer = StateObserver()

# Registrar handler
@observer.on("counter.changed")
async def handle_counter_change(value: int):
    print(f"Contador: {value}")
```

## Exemplos de Uso

### Gerenciamento de Estado

```python
from pepperpy_core import StateManager
from typing import Any

async def exemplo_estado():
    # Criar gerenciador
    manager = StateManager()
    
    # Definir estado inicial
    await manager.initialize({
        "app": {
            "version": "1.0.0",
            "debug": False
        },
        "user": {
            "id": None,
            "settings": {}
        }
    })
    
    # Atualizar estado
    await manager.set("user.id", "123")
    await manager.set("user.settings.theme", "dark")
    
    # Obter estado
    user_id = await manager.get("user.id")
    settings = await manager.get("user.settings")
    
    # Observar mudanças
    @manager.on("user.settings.changed")
    async def handle_settings_change(
        path: str,
        value: Any
    ):
        print(f"Configuração alterada: {path} = {value}")
```

### Persistência de Estado

```python
from pepperpy_core import PersistentStore
import json

async def exemplo_persistencia():
    # Criar store persistente
    store = PersistentStore(
        filename="state.json",
        auto_save=True
    )
    
    try:
        # Carregar estado
        await store.load()
        
        # Atualizar estado
        await store.set("session.last_access", time.time())
        await store.set("session.active", True)
        
        # Estado é salvo automaticamente
    finally:
        # Garantir que estado seja salvo
        await store.save()
```

## Recursos Avançados

### Estado com Histórico

```python
class HistoryStore(StateStore):
    def __init__(self, max_history: int = 100):
        super().__init__()
        self.max_history = max_history
        self.history = []
    
    async def set(self, path: str, value: Any):
        # Registrar mudança
        self.history.append({
            "path": path,
            "value": value,
            "timestamp": time.time()
        })
        
        # Limitar histórico
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Atualizar estado
        await super().set(path, value)
    
    def get_history(
        self,
        path: Optional[str] = None
    ) -> list[dict]:
        if path is None:
            return self.history
        
        return [
            entry for entry in self.history
            if entry["path"].startswith(path)
        ]
```

### Estado com Validação

```python
class ValidatedStore(StateStore):
    def __init__(self):
        super().__init__()
        self.validators = {}
    
    def register(
        self,
        path: str,
        validator: callable,
        initial_value: Any = None
    ):
        self.validators[path] = validator
        if initial_value is not None:
            self.set(path, initial_value)
    
    async def set(self, path: str, value: Any):
        # Verificar validador
        if path in self.validators:
            validator = self.validators[path]
            if not await validator(value):
                raise ValueError(
                    f"Valor inválido para {path}: {value}"
                )
        
        # Atualizar estado
        await super().set(path, value)
```

## Melhores Práticas

1. **Estado**
   - Defina schema
   - Valide valores
   - Use paths
   - Documente campos

2. **Persistência**
   - Backup regular
   - Valide dados
   - Trate corrupção
   - Migre schema

3. **Performance**
   - Cache seletivo
   - Batch updates
   - Otimize queries
   - Monitore uso

4. **Segurança**
   - Valide acesso
   - Sanitize dados
   - Proteja storage
   - Audite mudanças

5. **Manutenção**
   - Limpe estado
   - Monitore tamanho
   - Arquive dados
   - Atualize schema

## Padrões Comuns

### Estado com Cache

```python
class CachedStore(StateStore):
    def __init__(self, ttl: float = 300.0):
        super().__init__()
        self.ttl = ttl
        self.cache = {}
    
    async def get(self, path: str) -> Any:
        # Verificar cache
        now = time.time()
        if path in self.cache:
            entry = self.cache[path]
            if now - entry["timestamp"] < self.ttl:
                return entry["value"]
        
        # Buscar valor
        value = await super().get(path)
        
        # Atualizar cache
        self.cache[path] = {
            "value": value,
            "timestamp": now
        }
        
        return value
    
    async def set(self, path: str, value: Any):
        # Invalidar cache
        self.cache.pop(path, None)
        
        # Atualizar estado
        await super().set(path, value)
```

### Estado com Transações

```python
class TransactionalStore(StateStore):
    def __init__(self):
        super().__init__()
        self.transactions = {}
    
    async def begin(self) -> str:
        # Criar transação
        tx_id = str(uuid.uuid4())
        self.transactions[tx_id] = {
            "changes": {},
            "timestamp": time.time()
        }
        return tx_id
    
    async def commit(self, tx_id: str):
        if tx_id not in self.transactions:
            raise ValueError(f"Transação {tx_id} não existe")
        
        # Aplicar mudanças
        tx = self.transactions[tx_id]
        for path, value in tx["changes"].items():
            await super().set(path, value)
        
        # Limpar transação
        del self.transactions[tx_id]
    
    async def rollback(self, tx_id: str):
        if tx_id not in self.transactions:
            raise ValueError(f"Transação {tx_id} não existe")
        
        # Limpar transação
        del self.transactions[tx_id]
```

### Estado com Eventos

```python
class EventStore(StateStore):
    def __init__(self):
        super().__init__()
        self.listeners = []
    
    def add_listener(self, listener: callable):
        self.listeners.append(listener)
    
    async def set(self, path: str, value: Any):
        # Obter valor anterior
        old_value = await self.get(path)
        
        # Atualizar estado
        await super().set(path, value)
        
        # Notificar listeners
        event = {
            "type": "state.changed",
            "path": path,
            "old_value": old_value,
            "new_value": value,
            "timestamp": time.time()
        }
        
        for listener in self.listeners:
            try:
                await listener(event)
            except Exception as e:
                print(f"Erro no listener: {e}")
``` 