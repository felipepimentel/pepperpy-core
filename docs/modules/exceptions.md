# Exceptions (Exceções)

O módulo de Exceções do PepperPy Core fornece uma hierarquia completa de exceções para tratamento de erros específicos da biblioteca.

## Hierarquia de Exceções

### PepperpyError

Classe base para todas as exceções:

```python
from pepperpy_core import PepperpyError

try:
    # Operação que pode falhar
    process_data()
except PepperpyError as e:
    print(f"Erro: {e}")
    if e.__cause__:
        print(f"Causa: {e.__cause__}")
```

### Exceções de Configuração

```python
from pepperpy_core import ConfigError

try:
    load_config("config.json")
except ConfigError as e:
    print(f"Erro de configuração: {e}")
    if e.config_name:
        print(f"Configuração: {e.config_name}")
```

### Exceções de Validação

```python
from pepperpy_core import ValidationError

try:
    validate_data(data)
except ValidationError as e:
    print(f"Erro de validação: {e}")
    if e.field_name:
        print(f"Campo: {e.field_name}")
    if e.invalid_value:
        print(f"Valor inválido: {e.invalid_value}")
```

## Categorias de Exceções

### Exceções de Módulo

```python
from pepperpy_core import (
    ModuleError,
    InitializationError,
    ModuleNotFoundError
)

try:
    module.initialize()
except InitializationError as e:
    print(f"Erro de inicialização: {e}")
    if e.module_name:
        print(f"Módulo: {e.module_name}")
except ModuleNotFoundError as e:
    print(f"Módulo não encontrado: {e}")
```

### Exceções de Segurança

```python
from pepperpy_core import (
    SecurityError,
    AuthError,
    PermissionError,
    TokenError,
    CryptoError
)

try:
    authenticate_user(token)
except AuthError as e:
    print("Erro de autenticação")
except PermissionError as e:
    print("Erro de permissão")
except TokenError as e:
    print("Token inválido")
except CryptoError as e:
    print("Erro de criptografia")
```

### Exceções de Tarefa

```python
from pepperpy_core import (
    TaskError,
    TaskExecutionError,
    TaskNotFoundError
)

try:
    await task.execute()
except TaskExecutionError as e:
    print(f"Erro na execução da tarefa: {e}")
    if e.task_id:
        print(f"ID da tarefa: {e.task_id}")
except TaskNotFoundError as e:
    print(f"Tarefa não encontrada: {e}")
```

## Exemplos de Uso

### Tratamento Básico

```python
from pepperpy_core import PepperpyError, ValidationError

async def process_user_data(data: dict):
    try:
        # Validar dados
        validate_user_data(data)
        
        # Processar dados
        result = await process_data(data)
        
        return result
    except ValidationError as e:
        print(f"Dados inválidos: {e}")
        if e.field_name:
            print(f"Campo com erro: {e.field_name}")
        raise
    except PepperpyError as e:
        print(f"Erro no processamento: {e}")
        raise
```

### Encadeamento de Exceções

```python
from pepperpy_core import ConfigError, ValidationError

def load_user_config(path: str):
    try:
        # Carregar configuração
        config = load_config(path)
        
        # Validar configuração
        validate_config(config)
        
        return config
    except ValidationError as e:
        raise ConfigError(
            "Configuração inválida",
            cause=e,
            config_name=path
        )
```

## Melhores Práticas

1. **Hierarquia**
   - Use exceções específicas
   - Mantenha hierarquia clara
   - Documente exceções
   - Preserve causa original

2. **Contexto**
   - Inclua informações úteis
   - Mantenha mensagens claras
   - Use atributos específicos
   - Preserve stack trace

3. **Tratamento**
   - Trate exceções apropriadamente
   - Não silencie erros
   - Registre informações
   - Propague quando necessário

4. **Documentação**
   - Documente exceções lançadas
   - Explique condições
   - Forneça exemplos
   - Descreva atributos

5. **Performance**
   - Evite exceções para fluxo
   - Minimize overhead
   - Cache informações
   - Otimize mensagens

## Padrões Comuns

### Exceção com Contexto

```python
class ContextualError(PepperpyError):
    def __init__(
        self,
        message: str,
        context: dict,
        cause: Exception | None = None
    ):
        super().__init__(message, cause)
        self.context = context
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.context:
            return f"{base} (Contexto: {self.context})"
        return base
```

### Exceção com Retry

```python
class RetryableError(PepperpyError):
    def __init__(
        self,
        message: str,
        retry_count: int = 0,
        max_retries: int = 3,
        cause: Exception | None = None
    ):
        super().__init__(message, cause)
        self.retry_count = retry_count
        self.max_retries = max_retries
    
    @property
    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries
    
    def increment_retry(self) -> None:
        self.retry_count += 1
```

### Exceção com Recovery

```python
class RecoverableError(PepperpyError):
    def __init__(
        self,
        message: str,
        recovery_action: callable,
        cause: Exception | None = None
    ):
        super().__init__(message, cause)
        self.recovery_action = recovery_action
    
    async def recover(self) -> Any:
        try:
            return await self.recovery_action()
        except Exception as e:
            raise PepperpyError(
                "Falha na recuperação",
                cause=e
            )
```
``` 