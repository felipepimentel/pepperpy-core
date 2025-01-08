# Validation (Validação)

O módulo Validation do PepperPy Core fornece um sistema flexível e extensível para validação de dados, com suporte a regras customizadas e validação assíncrona.

## Componentes Principais

### Validator

Classe base para validadores:

```python
from pepperpy_core import Validator, ValidationResult

class MyValidator(Validator[dict]):
    async def validate(self, value: dict) -> ValidationResult:
        if not isinstance(value, dict):
            return ValidationResult(
                valid=False,
                errors=["Valor deve ser um dicionário"]
            )
        return ValidationResult(valid=True)

# Usar validador
validator = MyValidator()
result = await validator.validate({"key": "value"})
```

### ValidationRule

Regra de validação:

```python
from pepperpy_core import ValidationRule

# Criar regra
rule = ValidationRule(
    name="length",
    validate=lambda x: len(x) >= 3,
    message="Valor deve ter no mínimo 3 caracteres"
)
```

### ValidationSchema

Schema para validação:

```python
from pepperpy_core import ValidationSchema

# Criar schema
schema = ValidationSchema({
    "name": [
        ValidationRule(
            name="required",
            validate=lambda x: x is not None,
            message="Nome é obrigatório"
        ),
        ValidationRule(
            name="length",
            validate=lambda x: len(x) >= 3,
            message="Nome deve ter no mínimo 3 caracteres"
        )
    ],
    "age": [
        ValidationRule(
            name="range",
            validate=lambda x: 0 <= x <= 120,
            message="Idade deve estar entre 0 e 120"
        )
    ]
})
```

## Exemplos de Uso

### Validação Básica

```python
from pepperpy_core import Validator, ValidationRule, ValidationResult

class UserValidator(Validator[dict]):
    def __init__(self):
        super().__init__()
        self.rules = {
            "name": [
                ValidationRule(
                    name="required",
                    validate=lambda x: x is not None,
                    message="Nome é obrigatório"
                ),
                ValidationRule(
                    name="length",
                    validate=lambda x: len(x) >= 3,
                    message="Nome deve ter no mínimo 3 caracteres"
                )
            ],
            "email": [
                ValidationRule(
                    name="email",
                    validate=lambda x: "@" in x,
                    message="Email inválido"
                )
            ]
        }
    
    async def validate(self, value: dict) -> ValidationResult:
        errors = []
        
        for field, rules in self.rules.items():
            field_value = value.get(field)
            
            for rule in rules:
                if not rule.validate(field_value):
                    errors.append(
                        f"{field}: {rule.message}"
                    )
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )

async def exemplo_validacao_basica():
    # Criar validador
    validator = UserValidator()
    
    # Validar dados
    data = {
        "name": "Jo",
        "email": "invalid-email"
    }
    
    result = await validator.validate(data)
    if not result.valid:
        print("Erros de validação:")
        for error in result.errors:
            print(f"- {error}")
```

### Validação Assíncrona

```python
from pepperpy_core import Validator, ValidationResult
import aiohttp

class AsyncValidator(Validator[str]):
    async def validate(self, value: str) -> ValidationResult:
        async with aiohttp.ClientSession() as session:
            # Validar valor remotamente
            async with session.post(
                "https://api.validator.com/check",
                json={"value": value}
            ) as response:
                result = await response.json()
                
                return ValidationResult(
                    valid=result["valid"],
                    errors=result.get("errors", [])
                )

async def exemplo_validacao_async():
    validator = AsyncValidator()
    result = await validator.validate("test@example.com")
    
    if result.valid:
        print("Valor válido")
    else:
        print("Erros:", result.errors)
```

## Recursos Avançados

### Validador com Cache

```python
class CachedValidator(Validator[T]):
    def __init__(self):
        super().__init__()
        self.cache = {}
    
    async def validate(self, value: T) -> ValidationResult:
        # Gerar chave de cache
        key = str(value)
        
        # Verificar cache
        if key in self.cache:
            return self.cache[key]
        
        # Validar e cachear
        result = await self._do_validate(value)
        self.cache[key] = result
        return result
    
    async def _do_validate(self, value: T) -> ValidationResult:
        # Implementação específica
        return ValidationResult(valid=True)
```

### Validador com Dependências

```python
class DependentValidator(Validator[dict]):
    def __init__(self):
        super().__init__()
        self.dependencies = {}
    
    def add_dependency(
        self,
        field: str,
        depends_on: str,
        validator: callable
    ):
        if field not in self.dependencies:
            self.dependencies[field] = []
        
        self.dependencies[field].append({
            "field": depends_on,
            "validator": validator
        })
    
    async def validate(self, value: dict) -> ValidationResult:
        errors = []
        
        for field, deps in self.dependencies.items():
            field_value = value.get(field)
            
            for dep in deps:
                dep_value = value.get(dep["field"])
                if not dep["validator"](field_value, dep_value):
                    errors.append(
                        f"Validação falhou: {field} depende de {dep['field']}"
                    )
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors
        )
```

## Melhores Práticas

1. **Regras**
   - Mantenha simplicidade
   - Documente regras
   - Valide entrada
   - Use mensagens claras

2. **Performance**
   - Use cache quando apropriado
   - Otimize validações
   - Agrupe regras
   - Minimize I/O

3. **Mensagens**
   - Seja específico
   - Use linguagem clara
   - Forneça contexto
   - Sugira correções

4. **Segurança**
   - Valide entrada
   - Sanitize dados
   - Limite tamanhos
   - Proteja recursos

5. **Manutenção**
   - Documente regras
   - Teste validações
   - Monitore erros
   - Atualize regras

## Padrões Comuns

### Validador com Rate Limit

```python
class RateLimitedValidator(Validator[T]):
    def __init__(
        self,
        max_per_second: float = 100.0
    ):
        super().__init__()
        self.max_per_second = max_per_second
        self.last_validation = time.time()
        self.current_count = 0
    
    async def validate(self, value: T) -> ValidationResult:
        now = time.time()
        elapsed = now - self.last_validation
        
        if elapsed >= 1.0:
            self.current_count = 0
            self.last_validation = now
        
        if self.current_count >= self.max_per_second:
            return ValidationResult(
                valid=False,
                errors=["Taxa de validação excedida"]
            )
        
        self.current_count += 1
        return await self._do_validate(value)
    
    async def _do_validate(self, value: T) -> ValidationResult:
        # Implementação específica
        return ValidationResult(valid=True)
```

### Validador com Retry

```python
class RetryValidator(Validator[T]):
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        super().__init__()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def validate(self, value: T) -> ValidationResult:
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                return await self._do_validate(value)
            except Exception as e:
                last_error = str(e)
                retries += 1
                if retries < self.max_retries:
                    await asyncio.sleep(
                        self.retry_delay * (2 ** retries)
                    )
        
        return ValidationResult(
            valid=False,
            errors=[f"Falha após {retries} tentativas: {last_error}"]
        )
    
    async def _do_validate(self, value: T) -> ValidationResult:
        # Implementação específica
        return ValidationResult(valid=True)
```

### Validador com Eventos

```python
class EventValidator(Validator[T]):
    def __init__(self):
        super().__init__()
        self.listeners = []
    
    def add_listener(self, listener: callable):
        self.listeners.append(listener)
    
    async def validate(self, value: T) -> ValidationResult:
        # Notificar início
        await self._notify("start", value)
        
        try:
            result = await self._do_validate(value)
            # Notificar resultado
            await self._notify(
                "complete",
                value,
                result=result
            )
            return result
        except Exception as e:
            # Notificar erro
            await self._notify(
                "error",
                value,
                error=str(e)
            )
            raise
    
    async def _notify(
        self,
        event: str,
        value: T,
        **kwargs
    ):
        for listener in self.listeners:
            try:
                await listener(event, value, **kwargs)
            except Exception as e:
                print(f"Erro no listener: {e}")
    
    async def _do_validate(self, value: T) -> ValidationResult:
        # Implementação específica
        return ValidationResult(valid=True)
```
``` 