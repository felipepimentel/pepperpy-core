# Security (Segurança)

O módulo Security do PepperPy Core fornece funcionalidades para segurança da aplicação, incluindo autenticação, autorização, criptografia e proteção contra ataques comuns.

## Componentes Principais

### SecurityManager

Gerenciador central de segurança:

```python
from pepperpy_core import SecurityManager

# Criar gerenciador
manager = SecurityManager()

# Configurar
await manager.configure(
    secret_key="your-secret-key",
    enable_audit=True
)

# Verificar permissão
has_access = await manager.check_permission(
    user_id="123",
    resource="users",
    action="read"
)
```

### Encryptor

Serviço de criptografia:

```python
from pepperpy_core import Encryptor

# Criar encryptor
encryptor = Encryptor()

# Criptografar dados
encrypted = await encryptor.encrypt("dados sensíveis")

# Descriptografar dados
decrypted = await encryptor.decrypt(encrypted)
```

### TokenManager

Gerenciador de tokens:

```python
from pepperpy_core import TokenManager

# Criar gerenciador
token_manager = TokenManager()

# Gerar token
token = await token_manager.generate(
    user_id="123",
    scope=["read", "write"]
)

# Validar token
payload = await token_manager.validate(token)
```

## Exemplos de Uso

### Autenticação de Usuário

```python
from pepperpy_core import SecurityManager
from typing import Optional

async def autenticar_usuario(
    username: str,
    password: str
) -> Optional[str]:
    manager = SecurityManager()
    
    try:
        # Verificar credenciais
        user = await manager.authenticate(
            username=username,
            password=password
        )
        
        if user:
            # Gerar token
            token = await manager.create_token(
                user_id=user.id,
                scope=user.permissions
            )
            return token
    except Exception as e:
        await manager.log_security_event(
            "auth_failure",
            username=username,
            error=str(e)
        )
    
    return None
```

### Proteção de Dados

```python
from pepperpy_core import Encryptor
import json

async def proteger_dados(data: dict) -> str:
    # Criar encryptor
    encryptor = Encryptor()
    
    try:
        # Serializar e criptografar
        json_data = json.dumps(data)
        encrypted = await encryptor.encrypt(
            json_data,
            encoding="utf-8"
        )
        return encrypted
    except Exception as e:
        raise SecurityError(
            f"Falha ao criptografar: {e}"
        )

async def recuperar_dados(encrypted: str) -> dict:
    encryptor = Encryptor()
    
    try:
        # Descriptografar e deserializar
        decrypted = await encryptor.decrypt(
            encrypted,
            encoding="utf-8"
        )
        return json.loads(decrypted)
    except Exception as e:
        raise SecurityError(
            f"Falha ao descriptografar: {e}"
        )
```

## Recursos Avançados

### Autenticação Multi-Fator

```python
class MFAManager:
    def __init__(self):
        self.providers = {}
    
    def register_provider(
        self,
        name: str,
        provider: MFAProvider
    ):
        self.providers[name] = provider
    
    async def generate_code(
        self,
        user_id: str,
        provider: str
    ) -> str:
        if provider not in self.providers:
            raise SecurityError(
                f"Provider {provider} não encontrado"
            )
        
        return await self.providers[provider].generate(
            user_id
        )
    
    async def verify_code(
        self,
        user_id: str,
        provider: str,
        code: str
    ) -> bool:
        if provider not in self.providers:
            raise SecurityError(
                f"Provider {provider} não encontrado"
            )
        
        return await self.providers[provider].verify(
            user_id,
            code
        )
```

### Auditoria de Segurança

```python
class SecurityAuditor:
    def __init__(self):
        self.handlers = []
    
    def add_handler(self, handler: callable):
        self.handlers.append(handler)
    
    async def log_event(
        self,
        event_type: str,
        **details
    ):
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "details": details
        }
        
        for handler in self.handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"Erro no handler: {e}")
```

## Melhores Práticas

1. **Autenticação**
   - Use senhas fortes
   - Implemente MFA
   - Limite tentativas
   - Expire sessões

2. **Autorização**
   - Defina papéis
   - Valide permissões
   - Implemente RBAC
   - Audite acessos

3. **Criptografia**
   - Use algoritmos seguros
   - Gerencie chaves
   - Rotacione segredos
   - Proteja dados

4. **Proteção**
   - Valide entrada
   - Previna injeção
   - Use HTTPS
   - Monitore ataques

5. **Auditoria**
   - Registre eventos
   - Monitore acessos
   - Alerte anomalias
   - Mantenha logs

## Padrões Comuns

### Rate Limiter

```python
class RateLimiter:
    def __init__(
        self,
        max_attempts: int = 5,
        window: float = 300.0
    ):
        self.max_attempts = max_attempts
        self.window = window
        self.attempts = {}
    
    async def check(self, key: str) -> bool:
        now = time.time()
        
        # Limpar tentativas antigas
        self.attempts = {
            k: attempts for k, attempts in self.attempts.items()
            if now - attempts["timestamp"] < self.window
        }
        
        # Verificar tentativas
        if key in self.attempts:
            attempts = self.attempts[key]
            if attempts["count"] >= self.max_attempts:
                return False
            attempts["count"] += 1
        else:
            self.attempts[key] = {
                "count": 1,
                "timestamp": now
            }
        
        return True
```

### Token com Refresh

```python
class RefreshTokenManager:
    def __init__(self):
        self.tokens = {}
    
    async def generate_pair(
        self,
        user_id: str,
        scope: list[str]
    ) -> tuple[str, str]:
        # Gerar tokens
        access_token = await self._generate_access_token(
            user_id,
            scope
        )
        
        refresh_token = await self._generate_refresh_token(
            user_id
        )
        
        # Armazenar
        self.tokens[refresh_token] = {
            "user_id": user_id,
            "scope": scope,
            "created_at": time.time()
        }
        
        return access_token, refresh_token
    
    async def refresh(
        self,
        refresh_token: str
    ) -> Optional[str]:
        if refresh_token not in self.tokens:
            return None
        
        token_data = self.tokens[refresh_token]
        
        # Gerar novo access token
        return await self._generate_access_token(
            token_data["user_id"],
            token_data["scope"]
        )
```

### Proteção contra Ataques

```python
class SecurityMiddleware:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule: SecurityRule):
        self.rules.append(rule)
    
    async def process_request(
        self,
        request: Request
    ) -> bool:
        for rule in self.rules:
            if not await rule.check(request):
                await self.log_violation(
                    rule.name,
                    request
                )
                return False
        return True
    
    async def log_violation(
        self,
        rule: str,
        request: Request
    ):
        # Registrar violação
        event = {
            "rule": rule,
            "timestamp": time.time(),
            "ip": request.client_ip,
            "path": request.path,
            "headers": dict(request.headers)
        }
        
        await self.auditor.log_event(
            "security_violation",
            **event
        )
```
``` 