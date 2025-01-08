# Event System (Sistema de Eventos)

O Sistema de Eventos do PepperPy Core fornece uma implementação robusta de um barramento de eventos (event bus) para comunicação baseada em eventos. Ele suporta eventos tipados, manipuladores com prioridade e processamento assíncrono.

## Componentes Principais

### Event

A classe base para eventos:

```python
from pepperpy_core import Event

# Criar um evento simples
event = Event(
    data={"user_id": 123, "action": "login"},
    metadata={"timestamp": "2024-01-08T12:00:00Z"}
)

# Criar um evento personalizado
class UserEvent(Event):
    def __init__(self, user_id: int, action: str):
        super().__init__(
            data={"user_id": user_id, "action": action},
            metadata={"event_type": "user_action"}
        )
```

### EventListener

Gerencia os ouvintes de eventos:

```python
from pepperpy_core import EventListener

# Criar um manipulador de eventos
async def handle_user_event(event: UserEvent) -> None:
    user_id = event.data["user_id"]
    action = event.data["action"]
    print(f"User {user_id} performed {action}")

# Criar um ouvinte com prioridade
listener = EventListener(
    event_type=UserEvent,
    handler=handle_user_event,
    priority=10  # Prioridade mais alta
)
```

### EventBus

O barramento central de eventos:

```python
from pepperpy_core import EventBus

# Criar e inicializar o barramento de eventos
event_bus = EventBus()
await event_bus.initialize()

# Registrar um ouvinte
event_bus.add_listener(UserEvent, handle_user_event)

# Emitir um evento
user_event = UserEvent(user_id=123, action="login")
await event_bus.emit(user_event)
```

## Exemplos de Uso

### Eventos Básicos

```python
from pepperpy_core import Event, EventBus

async def exemplo_eventos_basicos():
    # Inicializar barramento
    bus = EventBus()
    await bus.initialize()
    
    # Definir manipulador
    async def log_event(event: Event) -> None:
        print(f"Evento recebido: {event.data}")
    
    # Registrar manipulador
    bus.add_listener(Event, log_event)
    
    # Emitir evento
    event = Event(data={"message": "Hello, World!"})
    await bus.emit(event)
```

### Eventos Tipados

```python
from pepperpy_core import Event, EventBus
from dataclasses import dataclass

@dataclass
class UserCreatedEvent(Event):
    def __init__(self, user_id: int, username: str):
        super().__init__(
            data={"user_id": user_id, "username": username},
            metadata={"event_type": "user.created"}
        )

async def exemplo_eventos_tipados():
    bus = EventBus()
    await bus.initialize()
    
    async def handle_user_created(event: UserCreatedEvent):
        user_id = event.data["user_id"]
        username = event.data["username"]
        print(f"Novo usuário criado: {username} (ID: {user_id})")
    
    bus.add_listener(UserCreatedEvent, handle_user_created)
    
    # Emitir evento tipado
    event = UserCreatedEvent(user_id=1, username="john_doe")
    await bus.emit(event)
```

### Manipuladores com Prioridade

```python
from pepperpy_core import Event, EventBus

async def exemplo_prioridades():
    bus = EventBus()
    await bus.initialize()
    
    # Manipuladores com diferentes prioridades
    async def high_priority(event: Event):
        print("Manipulador de alta prioridade")
    
    async def medium_priority(event: Event):
        print("Manipulador de média prioridade")
    
    async def low_priority(event: Event):
        print("Manipulador de baixa prioridade")
    
    # Registrar manipuladores
    bus.add_listener(Event, low_priority, priority=1)
    bus.add_listener(Event, medium_priority, priority=5)
    bus.add_listener(Event, high_priority, priority=10)
    
    # Emitir evento (manipuladores serão chamados em ordem de prioridade)
    await bus.emit(Event(data={"test": True}))
```

## Recursos Avançados

### Gerenciamento de Ouvintes

```python
class EventManager:
    def __init__(self):
        self.bus = EventBus()
        self.registered_handlers = {}
    
    async def initialize(self):
        await self.bus.initialize()
    
    def register_handler(self, event_type: type[Event], handler: callable, priority: int = 0):
        self.bus.add_listener(event_type, handler, priority)
        if event_type not in self.registered_handlers:
            self.registered_handlers[event_type] = []
        self.registered_handlers[event_type].append(handler)
    
    def unregister_handler(self, event_type: type[Event], handler: callable):
        self.bus.remove_listener(event_type, handler)
        if event_type in self.registered_handlers:
            self.registered_handlers[event_type].remove(handler)
    
    def unregister_all(self, event_type: type[Event]):
        if event_type in self.registered_handlers:
            for handler in self.registered_handlers[event_type]:
                self.bus.remove_listener(event_type, handler)
            del self.registered_handlers[event_type]
```

### Middleware de Eventos

```python
class EventMiddleware:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.middlewares = []
    
    def add_middleware(self, middleware: callable):
        self.middlewares.append(middleware)
    
    async def process_event(self, event: Event):
        # Aplicar middlewares em ordem
        current_event = event
        for middleware in self.middlewares:
            current_event = await middleware(current_event)
            if current_event is None:
                return  # Evento foi filtrado
        
        # Emitir evento processado
        await self.bus.emit(current_event)
```

## Melhores Práticas

1. **Design de Eventos**
   - Mantenha eventos imutáveis
   - Use tipos específicos de eventos
   - Inclua metadados relevantes
   - Documente a estrutura do evento

2. **Gerenciamento de Ouvintes**
   - Limite o número de ouvintes
   - Use prioridades com moderação
   - Remova ouvintes não utilizados
   - Monitore o desempenho

3. **Tratamento de Erros**
   - Implemente tratamento de erros
   - Não deixe erros se propagarem
   - Registre erros adequadamente
   - Use eventos de erro específicos

4. **Performance**
   - Otimize eventos frequentes
   - Evite processamento pesado
   - Use eventos assíncronos
   - Monitore a latência

5. **Organização**
   - Agrupe eventos relacionados
   - Use namespaces consistentes
   - Mantenha documentação atualizada
   - Siga padrões de nomenclatura

## Padrões Comuns

### Cadeia de Eventos

```python
class EventChain:
    def __init__(self, bus: EventBus):
        self.bus = bus
    
    async def start_chain(self, initial_event: Event):
        # Registrar manipuladores temporários
        self.bus.add_listener(EventA, self.handle_event_a)
        self.bus.add_listener(EventB, self.handle_event_b)
        self.bus.add_listener(EventC, self.handle_event_c)
        
        # Iniciar cadeia
        await self.bus.emit(initial_event)
    
    async def handle_event_a(self, event: EventA):
        # Processar e emitir próximo evento
        await self.bus.emit(EventB(...))
    
    async def handle_event_b(self, event: EventB):
        # Processar e emitir próximo evento
        await self.bus.emit(EventC(...))
    
    async def handle_event_c(self, event: EventC):
        # Finalizar cadeia
        pass
```

### Agregador de Eventos

```python
class EventAggregator:
    def __init__(self, timeout: float = 1.0):
        self.events = []
        self.timeout = timeout
        self.processing = False
    
    async def add_event(self, event: Event):
        self.events.append(event)
        if not self.processing:
            self.processing = True
            await self.process_events()
    
    async def process_events(self):
        await asyncio.sleep(self.timeout)
        if self.events:
            # Processar eventos agregados
            events_to_process = self.events.copy()
            self.events.clear()
            await self.handle_batch(events_to_process)
        self.processing = False
    
    async def handle_batch(self, events: list[Event]):
        # Implementar lógica de processamento em lote
        pass
```

### Filtro de Eventos

```python
class EventFilter:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.filters = {}
    
    def add_filter(self, event_type: type[Event], filter_func: callable):
        if event_type not in self.filters:
            self.filters[event_type] = []
        self.filters[event_type].append(filter_func)
    
    async def process_event(self, event: Event):
        event_type = type(event)
        if event_type in self.filters:
            for filter_func in self.filters[event_type]:
                if not filter_func(event):
                    return  # Evento filtrado
        
        # Evento passou pelos filtros
        await self.bus.emit(event)
``` 