"""
Key Vault Integration Module for MCP Platform Framework

This module provides secure access to Azure Key Vault for managing secrets,
keys, and certificates used by MCP tools. It ensures that sensitive information
is never hardcoded or stored in configuration files.

Key Features:
- Secure secret retrieval from Azure Key Vault
- Automatic secret caching with TTL
- Support for multiple secret types (secrets, keys, certificates)
- Integration with Managed Identity for authentication
- Circuit breaker pattern for resilience
- Comprehensive error handling and logging
"""

from .client import KeyVaultClient
from .cache import SecretCache
from .models import SecretReference, SecretType
from .exceptions import (
    KeyVaultError,
    KeyVaultConnectionError,
    KeyVaultAuthenticationError,
    KeyVaultAuthorizationError,
    KeyVaultNotFoundError,
    KeyVaultSecretExpiredError
)

__all__ = [
    'KeyVaultClient',
    'SecretCache',
    'SecretReference',
    'SecretType',
    'KeyVaultError',
    'KeyVaultConnectionError',
    'KeyVaultAuthenticationError',
    'KeyVaultAuthorizationError',
    'KeyVaultNotFoundError',
    'KeyVaultSecretExpiredError',
    'get_secret',
    'get_key',
    'get_certificate'
]

# Module version
__version__ = "1.2.0"

# Convenience functions for direct access
def get_secret(secret_name: str, vault_name: str = None, **kwargs) -> str:
    """
    Get a secret from Azure Key Vault.
    
    Args:
        secret_name: Name of the secret to retrieve
        vault_name: Optional Key Vault name (uses default if not provided)
        **kwargs: Additional arguments passed to KeyVaultClient
        
    Returns:
        The secret value
        
    Raises:
        KeyVaultError: If secret retrieval fails
    """
    client = KeyVaultClient(vault_name=vault_name, **kwargs)
    return client.get_secret(secret_name)


def get_key(key_name: str, vault_name: str = None, **kwargs) -> bytes:
    """
    Get a key from Azure Key Vault.
    
    Args:
        key_name: Name of the key to retrieve
        vault_name: Optional Key Vault name (uses default if not provided)
        **kwargs: Additional arguments passed to KeyVaultClient
        
    Returns:
        The key as bytes
        
    Raises:
        KeyVaultError: If key retrieval fails
    """
    client = KeyVaultClient(vault_name=vault_name, **kwargs)
    return client.get_key(key_name)


def get_certificate(certificate_name: str, vault_name: str = None, **kwargs) -> bytes:
    """
    Get a certificate from Azure Key Vault.
    
    Args:
        certificate_name: Name of the certificate to retrieve
        vault_name: Optional Key Vault name (uses default if not provided)
        **kwargs: Additional arguments passed to KeyVaultClient
        
    Returns:
        The certificate as bytes
        
    Raises:
        KeyVaultError: If certificate retrieval fails
    """
    client = KeyVaultClient(vault_name=vault_name, **kwargs)
    return client.get_certificate(certificate_name)
