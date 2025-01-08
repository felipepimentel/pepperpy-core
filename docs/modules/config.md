# Configuration (Configuração)

O módulo de Configuração do PepperPy Core fornece uma estrutura flexível para gerenciamento de configurações, suportando múltiplos formatos, validação e carregamento dinâmico.

## Componentes Principais

### Config

Classe base para configurações:

```python
from pepperpy_core import Config

# Criar configuração
config = Config(
    name="app_config",
    data={
        "debug": True,
        "host": "localhost",
        "port": 8080
    }
)

# Acessar valores
debug = config.get("debug")
host = config.get("host")
port = config.get("port", default=8000)
```

### ConfigLoader

Carregador de configurações de diferentes fontes:

```python
from pepperpy_core import ConfigLoader

# Criar loader
loader = ConfigLoader()

# Carregar de arquivo
config = await loader.load_file("config.json")

# Carregar de ambiente
config = await loader.load_env(prefix="APP_")

# Carregar de string
config = await loader.load_string('{"debug": true}')
```

### ConfigValidator

Validador de configurações:

```python
from pepperpy_core import ConfigValidator

class AppConfigValidator(ConfigValidator):
    def validate(self, config: Config) -> bool:
        # Validar valores obrigatórios
        if not config.has("host"):
            raise ValueError("Host é obrigatório")
        
        # Validar tipos
        if not isinstance(config.get("port"), int):
            raise TypeError("Port deve ser inteiro")
        
        return True
```

## Exemplos de Uso

### Configuração Básica

```python
from pepperpy_core import Config, ConfigLoader

async def exemplo_config_basica():
    # Criar configuração
    config = Config("app")
    
    # Definir valores
    config.set("debug", True)
    config.set("database", {
        "host": "localhost",
        "port": 5432,
        "name": "app_db"
    })
    
    # Acessar valores
    debug = config.get("debug")
    db_host = config.get("database.host")
    
    # Salvar configuração
    await config.save("config.json")
```

### Configuração Hierárquica

```python
from pepperpy_core import Config

async def exemplo_config_hierarquica():
    # Configuração base
    base_config = Config("base", {
        "app": {
            "name": "MyApp",
            "version": "1.0.0"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(message)s"
        }
    })
    
    # Configuração específica
    dev_config = Config("development", parent=base_config)
    dev_config.set("app.debug", True)
    dev_config.set("database.host", "localhost")
    
    # Acessar valores (herda da base)
    app_name = dev_config.get("app.name")      # "MyApp"
    debug = dev_config.get("app.debug")        # True
    log_level = dev_config.get("logging.level") # "INFO"
```

## Recursos Avançados

### Configuração com Validação

```python
from pepperpy_core import Config, ConfigValidator
from pydantic import BaseModel

class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: str

class AppConfigValidator(ConfigValidator):
    def __init__(self):
        self.models = {
            "database": DatabaseConfig
        }
    
    def validate(self, config: Config) -> bool:
        for key, model in self.models.items():
            if config.has(key):
                try:
                    # Validar usando Pydantic
                    model(**config.get(key))
                except ValidationError as e:
                    raise ConfigError(
                        f"Erro na validação de {key}: {e}"
                    )
        return True
```

### Configuração com Observadores

```python
class ObservableConfig(Config):
    def __init__(self, name: str, data: dict | None = None):
        super().__init__(name, data)
        self.observers = []
    
    def add_observer(self, observer: callable):
        self.observers.append(observer)
    
    def set(self, key: str, value: Any):
        old_value = self.get(key)
        super().set(key, value)
        
        # Notificar observadores
        for observer in self.observers:
            observer(key, old_value, value)
```

## Melhores Práticas

1. **Estrutura**
   - Use hierarquia clara
   - Agrupe configurações relacionadas
   - Use nomes descritivos
   - Mantenha consistência

2. **Validação**
   - Valide tipos de dados
   - Verifique valores obrigatórios
   - Implemente regras de negócio
   - Forneça mensagens claras

3. **Segurança**
   - Proteja dados sensíveis
   - Use variáveis de ambiente
   - Implemente criptografia
   - Controle acesso

4. **Performance**
   - Use cache apropriadamente
   - Otimize carregamento
   - Minimize operações de I/O
   - Implemente lazy loading

5. **Manutenção**
   - Documente configurações
   - Mantenha versionamento
   - Implemente migração
   - Faça backup regular

## Padrões Comuns

### Configuração com Cache

```python
class CachedConfig(Config):
    def __init__(self, name: str, cache_time: int = 300):
        super().__init__(name)
        self.cache = {}
        self.cache_time = cache_time
    
    def get(self, key: str, default: Any = None) -> Any:
        # Verificar cache
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.cache_time:
                return entry["value"]
        
        # Buscar valor
        value = super().get(key, default)
        
        # Atualizar cache
        self.cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
        
        return value
```

### Configuração com Encriptação

```python
from cryptography.fernet import Fernet

class EncryptedConfig(Config):
    def __init__(self, name: str, key: bytes):
        super().__init__(name)
        self.fernet = Fernet(key)
    
    def set(self, key: str, value: Any):
        if self.is_sensitive(key):
            # Encriptar valor
            value = self.encrypt(value)
        super().set(key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        value = super().get(key, default)
        if self.is_sensitive(key):
            # Decriptar valor
            value = self.decrypt(value)
        return value
    
    def is_sensitive(self, key: str) -> bool:
        return any(k in key.lower() for k in ["password", "secret", "key"])
    
    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode()).decode()
    
    def decrypt(self, value: str) -> str:
        return self.fernet.decrypt(value.encode()).decode()
```

### Configuração com Migração

```python
class VersionedConfig(Config):
    def __init__(self, name: str, version: str):
        super().__init__(name)
        self.version = version
        self.migrations = {}
    
    def register_migration(
        self,
        from_version: str,
        to_version: str,
        func: callable
    ):
        self.migrations[(from_version, to_version)] = func
    
    async def load(self, path: str):
        data = await self.load_file(path)
        
        # Verificar versão
        current_version = data.get("_version", "1.0.0")
        if current_version != self.version:
            # Aplicar migrações
            data = await self.migrate(
                data,
                current_version,
                self.version
            )
        
        self.data = data
    
    async def migrate(
        self,
        data: dict,
        from_version: str,
        to_version: str
    ) -> dict:
        if (from_version, to_version) in self.migrations:
            migration = self.migrations[(from_version, to_version)]
            return await migration(data)
        
        raise ValueError(
            f"Não há migração de {from_version} para {to_version}"
        )
``` 