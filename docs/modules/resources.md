# Resources (Recursos)

O módulo Resources do PepperPy Core fornece um sistema de gerenciamento de recursos, permitindo o controle e acesso a arquivos e recursos do sistema.

## Componentes Principais

### ResourceManager

Gerenciador principal de recursos:

```python
from pepperpy_core import ResourceManager

# Criar gerenciador
manager = ResourceManager()
manager.initialize()

# Adicionar recurso
info = manager.add_resource(
    "config",
    "config.json",
    metadata={"type": "config"}
)

# Acessar recurso
resource = manager.get_resource("config")
print(f"Tamanho: {resource.size} bytes")
```

### ResourceInfo

Informações sobre recursos:

```python
from pepperpy_core import ResourceInfo
from pathlib import Path

# Informações do recurso
info = ResourceInfo(
    name="data",
    path=Path("data.json"),
    size=1024,
    metadata={"type": "data"}
)
```

## Exemplos de Uso

### Gerenciamento Básico

```python
from pepperpy_core import ResourceManager
from pathlib import Path

async def exemplo_recursos_basico():
    # Criar gerenciador
    manager = ResourceManager()
    manager.initialize()
    
    try:
        # Adicionar recursos
        manager.add_resource(
            "config",
            "config.json",
            metadata={"type": "config"}
        )
        
        manager.add_resource(
            "data",
            "data/file.dat",
            metadata={"type": "data"}
        )
        
        # Listar recursos
        resources = manager.list_resources()
        for resource in resources:
            print(f"Recurso: {resource.name}")
            print(f"Caminho: {resource.path}")
            print(f"Tamanho: {resource.size}")
    finally:
        # Limpar recursos
        manager.cleanup()
```

### Gerenciamento de Arquivos

```python
from pepperpy_core import ResourceManager
import json

async def exemplo_arquivos():
    manager = ResourceManager()
    manager.initialize()
    
    # Adicionar arquivo de configuração
    config_info = manager.add_resource(
        "config",
        "config.json"
    )
    
    # Ler arquivo
    with open(config_info.path) as f:
        config = json.load(f)
    
    # Processar configuração
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    
    # Remover recurso
    manager.remove_resource("config")
```

## Recursos Avançados

### Gerenciador com Cache

```python
class CachedResourceManager(ResourceManager):
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    def get_resource(self, name: str) -> ResourceInfo | None:
        # Verificar cache
        if name in self.cache:
            return self.cache[name]
        
        # Buscar recurso
        resource = super().get_resource(name)
        if resource:
            self.cache[name] = resource
        
        return resource
    
    def cleanup(self) -> None:
        self.cache.clear()
        super().cleanup()
```

### Gerenciador com Validação

```python
class ValidatedResourceManager(ResourceManager):
    def __init__(self):
        super().__init__()
        self.validators = {}
    
    def add_validator(self, resource_type: str, validator: callable):
        self.validators[resource_type] = validator
    
    def add_resource(
        self,
        name: str,
        path: str | Path,
        metadata: dict[str, Any] | None = None
    ) -> ResourceInfo:
        # Validar recurso
        if metadata and "type" in metadata:
            resource_type = metadata["type"]
            if resource_type in self.validators:
                validator = self.validators[resource_type]
                if not validator(path):
                    raise ResourceError(
                        f"Validação falhou para {name}"
                    )
        
        return super().add_resource(name, path, metadata)
```

## Melhores Práticas

1. **Recursos**
   - Use nomes descritivos
   - Adicione metadados
   - Valide caminhos
   - Gerencie ciclo de vida

2. **Performance**
   - Cache quando apropriado
   - Otimize acessos
   - Monitore uso
   - Limpe recursos

3. **Segurança**
   - Valide caminhos
   - Controle acesso
   - Sanitize nomes
   - Proteja recursos

4. **Gerenciamento**
   - Inicialize corretamente
   - Faça cleanup
   - Monitore recursos
   - Trate erros

5. **Manutenção**
   - Documente recursos
   - Monitore uso
   - Atualize metadados
   - Remova inativos

## Padrões Comuns

### Gerenciador com Monitoramento

```python
class MonitoredResourceManager(ResourceManager):
    def __init__(self):
        super().__init__()
        self.stats = {
            "adds": 0,
            "removes": 0,
            "accesses": 0
        }
    
    def add_resource(
        self,
        name: str,
        path: str | Path,
        metadata: dict[str, Any] | None = None
    ) -> ResourceInfo:
        info = super().add_resource(name, path, metadata)
        self.stats["adds"] += 1
        return info
    
    def remove_resource(self, name: str) -> None:
        super().remove_resource(name)
        self.stats["removes"] += 1
    
    def get_resource(self, name: str) -> ResourceInfo | None:
        resource = super().get_resource(name)
        if resource:
            self.stats["accesses"] += 1
        return resource
    
    def get_stats(self) -> dict[str, int]:
        return self.stats.copy()
```

### Gerenciador com Backup

```python
class BackupResourceManager(ResourceManager):
    def __init__(self, backup_dir: str | Path):
        super().__init__()
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def add_resource(
        self,
        name: str,
        path: str | Path,
        metadata: dict[str, Any] | None = None
    ) -> ResourceInfo:
        info = super().add_resource(name, path, metadata)
        
        # Criar backup
        backup_path = self.backup_dir / f"{name}.bak"
        shutil.copy2(info.path, backup_path)
        
        return info
    
    def restore_backup(self, name: str) -> None:
        backup_path = self.backup_dir / f"{name}.bak"
        if not backup_path.exists():
            raise ResourceError(f"Backup não encontrado: {name}")
        
        resource = self.get_resource(name)
        if resource:
            shutil.copy2(backup_path, resource.path)
```

### Gerenciador com Eventos

```python
class EventResourceManager(ResourceManager):
    def __init__(self):
        super().__init__()
        self.listeners = []
    
    def add_listener(self, listener: callable):
        self.listeners.append(listener)
    
    def _notify(self, event: str, resource: str):
        for listener in self.listeners:
            try:
                listener(event, resource)
            except Exception as e:
                print(f"Erro no listener: {e}")
    
    def add_resource(
        self,
        name: str,
        path: str | Path,
        metadata: dict[str, Any] | None = None
    ) -> ResourceInfo:
        info = super().add_resource(name, path, metadata)
        self._notify("add", name)
        return info
    
    def remove_resource(self, name: str) -> None:
        super().remove_resource(name)
        self._notify("remove", name)
```
``` 