"""
Data models for Key Vault Integration Module
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class SecretType(Enum):
    """
    Types of secrets that can be stored in Azure Key Vault.
    """
    SECRET = "secret"
    KEY = "key"
    CERTIFICATE = "certificate"
    PASSWORD = "password"
    CONNECTION_STRING = "connection_string"
    API_KEY = "api_key"
    TOKEN = "token"


@dataclass
class SecretReference:
    """
    Reference to a secret in Azure Key Vault.
    
    This class represents a reference to a secret that can be resolved
    to the actual secret value when needed.
    """
    name: str
    vault_name: Optional[str] = None
    version: Optional[str] = None
    secret_type: SecretType = SecretType.SECRET
    
    def __post_init__(self):
        """Validate and normalize the secret reference."""
        if self.secret_type and isinstance(self.secret_type, str):
            self.secret_type = SecretType(self.secret_type)
    
    @property
    def full_name(self) -> str:
        """Get the full name including vault if specified."""
        if self.vault_name:
            return f"{self.vault_name}/{self.name}"
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "secret_type": self.secret_type.value
        }
        
        if self.vault_name:
            result["vault_name"] = self.vault_name
        if self.version:
            result["version"] = self.version
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecretReference':
        """Create SecretReference from dictionary."""
        return cls(
            name=data["name"],
            vault_name=data.get("vault_name"),
            version=data.get("version"),
            secret_type=data.get("secret_type", SecretType.SECRET)
        )
    
    @classmethod
    def from_string(cls, reference: str) -> 'SecretReference':
        """
        Create SecretReference from string.
        
        Supports formats:
        - "secret-name"
        - "vault-name/secret-name"
        - "vault-name/secret-name@version"
        """
        parts = reference.split("@")
        name_part = parts[0]
        version = parts[1] if len(parts) > 1 else None
        
        if "/" in name_part:
            vault_name, name = name_part.split("/", 1)
        else:
            vault_name = None
            name = name_part
        
        return cls(
            name=name,
            vault_name=vault_name,
            version=version
        )


@dataclass
class SecretMetadata:
    """
    Metadata about a secret in Azure Key Vault.
    """
    name: str
    vault_name: str
    secret_type: SecretType
    enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    version: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "vault_name": self.vault_name,
            "secret_type": self.secret_type.value,
            "enabled": self.enabled,
            "tags": self.tags
        }
        
        if self.created_at:
            result["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            result["updated_at"] = self.updated_at.isoformat()
        if self.expires_at:
            result["expires_at"] = self.expires_at.isoformat()
        if self.version:
            result["version"] = self.version
            
        return result


@dataclass
class SecretCacheEntry:
    """
    Entry in the secret cache.
    """
    secret_name: str
    vault_name: str
    secret_value: str
    secret_type: SecretType
    cached_at: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: int = 300  # Default 5 minutes
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow())
    
    def __post_init__(self):
        """Initialize expiration time."""
        self.expires_at = self.cached_at.replace(
            second=self.cached_at.second + self.ttl_seconds
        )
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "secret_name": self.secret_name,
            "vault_name": self.vault_name,
            "secret_type": self.secret_type.value,
            "cached_at": self.cached_at.isoformat(),
            "ttl_seconds": self.ttl_seconds,
            "expires_at": self.expires_at.isoformat()
        }


@dataclass
class KeyVaultConfig:
    """
    Configuration for Azure Key Vault client.
    """
    vault_name: str
    endpoint: Optional[str] = None
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    use_managed_identity: bool = True
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    timeout_seconds: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation (excluding secrets)."""
        result = {
            "vault_name": self.vault_name,
            "use_managed_identity": self.use_managed_identity,
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "timeout_seconds": self.timeout_seconds
        }
        
        if self.endpoint:
            result["endpoint"] = self.endpoint
        if self.tenant_id:
            result["tenant_id"] = self.tenant_id
        if self.client_id:
            result["client_id"] = self.client_id
            
        return result
