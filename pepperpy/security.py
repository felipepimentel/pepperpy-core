"""Security module."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AuthInfo:
    """Authentication information."""

    username: str
    password: str
    token: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class SecurityConfig:
    """Security configuration."""

    enabled: bool = True
    auth_info: Optional[AuthInfo] = None
    require_auth: bool = False
    allow_anonymous: bool = True
