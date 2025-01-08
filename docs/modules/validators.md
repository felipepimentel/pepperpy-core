# Validators (Validadores)

O módulo de Validadores do PepperPy Core fornece um conjunto robusto de classes para validação de dados. Ele inclui validadores para tipos básicos e formatos comuns, com suporte a validação composicional e tipagem genérica.

## Componentes Principais

### BaseValidator

Classe base abstrata para todos os validadores:

```python
from pepperpy_core import BaseValidator
from typing import Any, TypeVar

T = TypeVar("T")

class CustomValidator(BaseValidator[T]):
    def validate(self, value: Any) -> T:
        # Implementar lógica de validação
        if not self.is_valid(value):
            raise ValidationError("Valor inválido")
        return value
```

### Validadores Básicos

Validadores para tipos de dados fundamentais:

```python
from pepperpy_core import (
    StringValidator,
    IntegerValidator,
    ListValidator,
    DictValidator
)

# Validador de strings
string_validator = StringValidator()
valid_string = string_validator.validate("texto")  # OK
# string_validator.validate(123)  # Raises ValidationError

# Validador de inteiros
int_validator = IntegerValidator()
valid_int = int_validator.validate(42)  # OK
# int_validator.validate("42")  # Raises ValidationError

# Validador de listas
list_validator = ListValidator(StringValidator())
valid_list = list_validator.validate(["a", "b", "c"])  # OK
# list_validator.validate(["a", 1, "c"])  # Raises ValidationError

# Validador de dicionários
dict_validator = DictValidator(
    key_validator=StringValidator(),
    value_validator=IntegerValidator()
)
valid_dict = dict_validator.validate({"a": 1, "b": 2})  # OK
# dict_validator.validate({"a": "1"})  # Raises ValidationError
```

### Validadores de Formato

Validadores para formatos específicos:

```python
from pepperpy_core import (
    EmailValidator,
    URLValidator,
    IPAddressValidator,
    PhoneNumberValidator
)

# Validador de email
email_validator = EmailValidator()
valid_email = email_validator.validate("user@example.com")  # OK
# email_validator.validate("invalid-email")  # Raises ValidationError

# Validador de URL
url_validator = URLValidator()
valid_url = url_validator.validate("https://example.com")  # OK
# url_validator.validate("not-a-url")  # Raises ValidationError

# Validador de IP
ip_validator = IPAddressValidator()
valid_ip = ip_validator.validate("192.168.1.1")  # OK
# ip_validator.validate("256.256.256.256")  # Raises ValidationError

# Validador de telefone
phone_validator = PhoneNumberValidator()
valid_phone = phone_validator.validate("+1 234-567-8900")  # OK
# phone_validator.validate("invalid-phone")  # Raises ValidationError
```

## Exemplos de Uso

### Validação Básica

```python
from pepperpy_core import StringValidator, ValidationError

def validar_nome_usuario(nome: str) -> str:
    validator = StringValidator()
    try:
        return validator.validate(nome)
    except ValidationError as e:
        print(f"Nome de usuário inválido: {e}")
        raise
```

### Validação Composta

```python
from pepperpy_core import (
    DictValidator,
    StringValidator,
    EmailValidator,
    PhoneNumberValidator
)

def validar_contato(dados: dict) -> dict:
    validator = DictValidator(
        key_validator=StringValidator(),
        value_validator=StringValidator()
    )
    
    # Validadores específicos para campos
    email_validator = EmailValidator()
    phone_validator = PhoneNumberValidator()
    
    # Validar estrutura básica
    dados_validados = validator.validate(dados)
    
    # Validar campos específicos
    dados_validados["email"] = email_validator.validate(dados["email"])
    dados_validados["telefone"] = phone_validator.validate(dados["telefone"])
    
    return dados_validados
```

### Validação de Lista

```python
from pepperpy_core import ListValidator, EmailValidator

def validar_lista_emails(emails: list) -> list:
    validator = ListValidator(EmailValidator())
    try:
        return validator.validate(emails)
    except ValidationError as e:
        print(f"Lista de emails inválida: {e}")
        raise
```

## Recursos Avançados

### Validador Customizado

```python
from pepperpy_core import BaseValidator, ValidationError
import re

class PasswordValidator(BaseValidator[str]):
    def __init__(
        self,
        min_length: int = 8,
        require_upper: bool = True,
        require_number: bool = True,
        require_special: bool = True
    ):
        self.min_length = min_length
        self.require_upper = require_upper
        self.require_number = require_number
        self.require_special = require_special
    
    def validate(self, value: Any) -> str:
        if not isinstance(value, str):
            raise ValidationError("Senha deve ser uma string")
        
        if len(value) < self.min_length:
            raise ValidationError(
                f"Senha deve ter pelo menos {self.min_length} caracteres"
            )
        
        if self.require_upper and not re.search(r"[A-Z]", value):
            raise ValidationError("Senha deve conter letra maiúscula")
        
        if self.require_number and not re.search(r"\d", value):
            raise ValidationError("Senha deve conter número")
        
        if self.require_special and not re.search(r"[!@#$%^&*]", value):
            raise ValidationError("Senha deve conter caractere especial")
        
        return value
```

### Validador com Cache

```python
class CachedValidator(BaseValidator[T]):
    def __init__(self, validator: BaseValidator[T]):
        self.validator = validator
        self.cache = {}
    
    def validate(self, value: Any) -> T:
        cache_key = str(value)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self.validator.validate(value)
        self.cache[cache_key] = result
        return result
```

## Melhores Práticas

1. **Design de Validadores**
   - Mantenha validadores simples
   - Combine validadores para casos complexos
   - Use mensagens de erro claras
   - Implemente validação completa

2. **Tratamento de Erros**
   - Use exceções apropriadas
   - Forneça mensagens úteis
   - Capture erros adequadamente
   - Mantenha rastreabilidade

3. **Performance**
   - Cache resultados quando apropriado
   - Otimize expressões regulares
   - Evite validações redundantes
   - Monitore tempo de validação

4. **Segurança**
   - Valide entrada de usuário
   - Evite injeção de código
   - Limite tamanho de entrada
   - Sanitize dados sensíveis

5. **Manutenção**
   - Documente regras de validação
   - Mantenha testes atualizados
   - Revise regras regularmente
   - Atualize padrões quando necessário

## Padrões Comuns

### Cadeia de Validação

```python
class ValidationChain:
    def __init__(self):
        self.validators: list[BaseValidator] = []
    
    def add_validator(self, validator: BaseValidator) -> "ValidationChain":
        self.validators.append(validator)
        return self
    
    def validate(self, value: Any) -> Any:
        result = value
        for validator in self.validators:
            result = validator.validate(result)
        return result
```

### Validador Condicional

```python
class ConditionalValidator(BaseValidator[T]):
    def __init__(
        self,
        condition: callable,
        validator: BaseValidator[T],
        else_validator: BaseValidator[T] | None = None
    ):
        self.condition = condition
        self.validator = validator
        self.else_validator = else_validator
    
    def validate(self, value: Any) -> T:
        if self.condition(value):
            return self.validator.validate(value)
        elif self.else_validator:
            return self.else_validator.validate(value)
        return value
```

### Validador com Transformação

```python
class TransformingValidator(BaseValidator[T]):
    def __init__(
        self,
        validator: BaseValidator[T],
        transform_before: callable | None = None,
        transform_after: callable | None = None
    ):
        self.validator = validator
        self.transform_before = transform_before
        self.transform_after = transform_after
    
    def validate(self, value: Any) -> T:
        if self.transform_before:
            value = self.transform_before(value)
        
        result = self.validator.validate(value)
        
        if self.transform_after:
            result = self.transform_after(result)
        
        return result
``` 