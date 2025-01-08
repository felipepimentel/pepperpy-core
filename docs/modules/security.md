# Security Module

## Overview

The security module provides a comprehensive security framework for your application, including authentication, authorization, encryption, and secure data handling. It implements industry best practices and follows security-first design principles.

## Key Components

### SecurityManager

```python
from pepperpy_core.security import (
    SecurityManager,
    SecurityConfig
)

# Create manager
manager = SecurityManager(
    config=SecurityConfig(
        secret_key=os.getenv("SECRET_KEY"),
        encryption_key=os.getenv("ENCRYPTION_KEY"),
        auth_enabled=True,
        ssl_verify=True
    )
)

# Initialize security
await manager.initialize()
```

### Authentication

```python
from pepperpy_core.security import (
    AuthManager,
    AuthConfig,
    AuthProvider
)

# Configure auth
auth = AuthManager(
    config=AuthConfig(
        providers=[
            "jwt",
            "oauth2",
            "basic"
        ],
        token_ttl=3600,
        refresh_ttl=86400
    )
)

# Authenticate
token = await auth.authenticate(
    credentials={
        "username": "user",
        "password": "pass"
    }
)
```

### Authorization

```python
from pepperpy_core.security import (
    AccessControl,
    Permission,
    Role
)

# Create ACL
acl = AccessControl()

# Define roles
admin = Role("admin", permissions=[
    Permission("users", ["create", "read", "update", "delete"]),
    Permission("settings", ["read", "update"])
])

user = Role("user", permissions=[
    Permission("users", ["read"]),
    Permission("settings", ["read"])
])

# Check access
if await acl.has_permission(user, "users.read"):
    # Allow access
    pass
```

## Usage Patterns

### 1. Secure Data Handling

```python
from pepperpy_core.security import (
    DataEncryption,
    EncryptionConfig
)

class SecureData:
    def __init__(self):
        self.encryption = DataEncryption(
            config=EncryptionConfig(
                algorithm="AES-256-GCM",
                key_size=32,
                iterations=100000
            )
        )
    
    async def encrypt_data(self, data: dict):
        try:
            # Generate key
            key = await self.encryption.generate_key()
            
            # Encrypt data
            encrypted = await self.encryption.encrypt(
                data=data,
                key=key
            )
            
            return encrypted
            
        except Exception as e:
            raise SecurityError(f"Encryption failed: {e}")
    
    async def decrypt_data(
        self,
        encrypted: bytes,
        key: bytes
    ):
        try:
            # Decrypt data
            decrypted = await self.encryption.decrypt(
                data=encrypted,
                key=key
            )
            
            return decrypted
            
        except Exception as e:
            raise SecurityError(f"Decryption failed: {e}")
```

### 2. Secure Communication

```python
from pepperpy_core.security import (
    SecureChannel,
    ChannelConfig
)

class SecureCommunication:
    def __init__(self):
        self.channel = SecureChannel(
            config=ChannelConfig(
                ssl_verify=True,
                cert_file="certs/server.crt",
                key_file="certs/server.key"
            )
        )
    
    async def send_secure(
        self,
        data: dict,
        recipient: str
    ):
        try:
            # Establish secure channel
            channel = await self.channel.connect(
                recipient
            )
            
            # Send data
            await channel.send(data)
            
        except Exception as e:
            raise SecurityError(f"Send failed: {e}")
    
    async def receive_secure(self):
        try:
            # Accept connection
            channel = await self.channel.accept()
            
            # Receive data
            data = await channel.receive()
            
            return data
            
        except Exception as e:
            raise SecurityError(f"Receive failed: {e}")
```

### 3. Access Control

```python
from pepperpy_core.security import (
    AccessControl,
    Policy,
    Resource
)

class SecurityControl:
    def __init__(self):
        self.acl = AccessControl()
    
    async def setup_policies(self):
        # Define resources
        users = Resource(
            name="users",
            actions=["create", "read", "update", "delete"]
        )
        
        settings = Resource(
            name="settings",
            actions=["read", "update"]
        )
        
        # Define policies
        admin_policy = Policy(
            name="admin",
            resources=[users, settings],
            effect="allow"
        )
        
        user_policy = Policy(
            name="user",
            resources=[
                Resource(
                    name="users",
                    actions=["read"]
                ),
                Resource(
                    name="settings",
                    actions=["read"]
                )
            ],
            effect="allow"
        )
        
        # Apply policies
        await self.acl.apply_policy(admin_policy)
        await self.acl.apply_policy(user_policy)
    
    async def check_access(
        self,
        user: dict,
        resource: str,
        action: str
    ):
        try:
            # Get user role
            role = await self.get_user_role(user)
            
            # Check permission
            allowed = await self.acl.check_permission(
                role=role,
                resource=resource,
                action=action
            )
            
            return allowed
            
        except Exception as e:
            raise SecurityError(f"Access check failed: {e}")
```

## Best Practices

### 1. Authentication

```python
from pepperpy_core.security import (
    AuthManager,
    AuthConfig
)

class SecureAuth:
    def configure(self):
        return AuthConfig(
            # Providers
            providers={
                "jwt": {
                    "secret": os.getenv("JWT_SECRET"),
                    "algorithm": "HS256",
                    "expires_in": 3600
                },
                "oauth2": {
                    "client_id": os.getenv("OAUTH_CLIENT_ID"),
                    "client_secret": os.getenv("OAUTH_CLIENT_SECRET"),
                    "redirect_uri": "https://api.example.com/oauth/callback"
                }
            },
            
            # Settings
            settings={
                "token_ttl": 3600,
                "refresh_ttl": 86400,
                "max_attempts": 3,
                "lockout_time": 300
            },
            
            # Security
            security={
                "password_hash": "bcrypt",
                "salt_rounds": 12,
                "min_length": 12,
                "require_special": True
            }
        )
```

### 2. Encryption

```python
from pepperpy_core.security import (
    EncryptionManager,
    EncryptionConfig
)

class SecureEncryption:
    def configure(self):
        return EncryptionConfig(
            # Algorithms
            algorithms={
                "aes": {
                    "mode": "GCM",
                    "key_size": 32,
                    "iv_size": 12
                },
                "chacha20": {
                    "key_size": 32,
                    "nonce_size": 12
                }
            },
            
            # Key derivation
            kdf={
                "algorithm": "PBKDF2",
                "iterations": 100000,
                "salt_size": 16
            },
            
            # Storage
            storage={
                "key_store": "vault",
                "vault_url": os.getenv("VAULT_URL"),
                "vault_token": os.getenv("VAULT_TOKEN")
            }
        )
```

### 3. Access Control

```python
from pepperpy_core.security import (
    AccessControl,
    AccessConfig
)

class SecureAccess:
    def configure(self):
        return AccessConfig(
            # Roles
            roles={
                "admin": {
                    "permissions": ["*"],
                    "priority": 100
                },
                "user": {
                    "permissions": [
                        "users.read",
                        "settings.read"
                    ],
                    "priority": 10
                }
            },
            
            # Resources
            resources={
                "users": ["create", "read", "update", "delete"],
                "settings": ["read", "update"],
                "logs": ["read"]
            },
            
            # Policies
            policies={
                "default": {
                    "effect": "deny",
                    "priority": 0
                },
                "admin": {
                    "effect": "allow",
                    "priority": 100
                }
            }
        )
```

## Complete Examples

### 1. Secure API Client

```python
from pepperpy_core.security import (
    SecureClient,
    ClientConfig,
    AuthProvider
)

class APIClient:
    def __init__(self):
        self.client = SecureClient(
            config=ClientConfig(
                base_url="https://api.example.com",
                timeout=30,
                retries=3,
                ssl_verify=True
            )
        )
        
        self.auth = AuthProvider(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET")
        )
    
    async def authenticate(self):
        # Get token
        token = await self.auth.get_token()
        
        # Set auth header
        self.client.set_header(
            "Authorization",
            f"Bearer {token}"
        )
    
    async def get_data(self, resource: str):
        try:
            # Send request
            response = await self.client.get(
                f"/api/{resource}",
                headers={
                    "Accept": "application/json"
                }
            )
            
            # Verify response
            await self.verify_response(response)
            
            return response.data
            
        except Exception as e:
            raise SecurityError(f"API request failed: {e}")
    
    async def verify_response(self, response):
        # Verify status
        if response.status != 200:
            raise SecurityError(
                f"API error: {response.status}"
            )
        
        # Verify signature
        if not await self.verify_signature(
            response.data,
            response.headers["X-Signature"]
        ):
            raise SecurityError("Invalid signature")
```

### 2. Secure Storage

```python
from pepperpy_core.security import (
    SecureStorage,
    StorageConfig,
    Encryption
)

class DataStorage:
    def __init__(self):
        self.storage = SecureStorage(
            config=StorageConfig(
                path="data",
                encryption=True,
                compression=True
            )
        )
        
        self.encryption = Encryption(
            algorithm="AES-256-GCM",
            key_size=32
        )
    
    async def store_data(
        self,
        key: str,
        data: dict
    ):
        try:
            # Encrypt data
            encrypted = await self.encryption.encrypt(
                data
            )
            
            # Store data
            await self.storage.put(
                key,
                encrypted
            )
            
        except Exception as e:
            raise SecurityError(f"Storage failed: {e}")
    
    async def retrieve_data(self, key: str):
        try:
            # Get data
            encrypted = await self.storage.get(key)
            
            # Decrypt data
            decrypted = await self.encryption.decrypt(
                encrypted
            )
            
            return decrypted
            
        except Exception as e:
            raise SecurityError(f"Retrieval failed: {e}")
    
    async def rotate_keys(self):
        try:
            # Generate new key
            new_key = await self.encryption.generate_key()
            
            # Get all data
            data = await self.storage.list()
            
            # Re-encrypt with new key
            for key in data:
                # Get old data
                old_data = await self.retrieve_data(key)
                
                # Store with new key
                await self.store_data(
                    key,
                    old_data
                )
            
        except Exception as e:
            raise SecurityError(f"Key rotation failed: {e}")
```
``` 