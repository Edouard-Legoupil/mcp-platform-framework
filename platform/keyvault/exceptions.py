"""
Exceptions for Key Vault Integration Module
"""


class KeyVaultError(Exception):
    """Base exception for Key Vault errors."""
    
    def __init__(self, message: str = "Key Vault error", details: str = None):
        """
        Initialize KeyVaultError.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details
        self.error_code = "KEYVAULT-000"
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class KeyVaultConnectionError(KeyVaultError):
    """Exception for connection failures to Key Vault."""
    
    def __init__(self, message: str = "Connection to Key Vault failed", details: str = None):
        super().__init__(message, details)
        self.error_code = "KEYVAULT-001"


class KeyVaultAuthenticationError(KeyVaultError):
    """Exception for authentication failures with Key Vault."""
    
    def __init__(self, message: str = "Authentication to Key Vault failed", details: str = None):
        super().__init__(message, details)
        self.error_code = "KEYVAULT-002"


class KeyVaultAuthorizationError(KeyVaultError):
    """Exception for authorization failures with Key Vault."""
    
    def __init__(self, message: str = "Authorization to Key Vault failed", details: str = None):
        super().__init__(message, details)
        self.error_code = "KEYVAULT-003"


class KeyVaultNotFoundError(KeyVaultError):
    """Exception for not found errors in Key Vault."""
    
    def __init__(self, message: str = "Secret not found in Key Vault", secret_name: str = None, vault_name: str = None):
        if secret_name and vault_name:
            message = f"Secret '{secret_name}' not found in vault '{vault_name}'"
        elif secret_name:
            message = f"Secret '{secret_name}' not found"
        super().__init__(message)
        self.secret_name = secret_name
        self.vault_name = vault_name
        self.error_code = "KEYVAULT-004"


class KeyVaultSecretExpiredError(KeyVaultError):
    """Exception for expired secrets in Key Vault."""
    
    def __init__(self, message: str = "Secret has expired", secret_name: str = None, vault_name: str = None):
        if secret_name and vault_name:
            message = f"Secret '{secret_name}' in vault '{vault_name}' has expired"
        elif secret_name:
            message = f"Secret '{secret_name}' has expired"
        super().__init__(message)
        self.secret_name = secret_name
        self.vault_name = vault_name
        self.error_code = "KEYVAULT-005"


class KeyVaultSecretDisabledError(KeyVaultError):
    """Exception for disabled secrets in Key Vault."""
    
    def __init__(self, message: str = "Secret is disabled", secret_name: str = None, vault_name: str = None):
        if secret_name and vault_name:
            message = f"Secret '{secret_name}' in vault '{vault_name}' is disabled"
        elif secret_name:
            message = f"Secret '{secret_name}' is disabled"
        super().__init__(message)
        self.secret_name = secret_name
        self.vault_name = vault_name
        self.error_code = "KEYVAULT-006"


class KeyVaultRateLimitError(KeyVaultError):
    """Exception for rate limiting in Key Vault."""
    
    def __init__(self, message: str = "Key Vault rate limit exceeded", retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after
        self.error_code = "KEYVAULT-007"
    
    def __str__(self) -> str:
        if self.retry_after:
            return f"{self.message} - Retry after {self.retry_after} seconds"
        return self.message


class KeyVaultCacheError(KeyVaultError):
    """Exception for cache-related errors in Key Vault client."""
    
    def __init__(self, message: str = "Key Vault cache error", details: str = None):
        super().__init__(message, details)
        self.error_code = "KEYVAULT-008"


class KeyVaultConfigurationError(KeyVaultError):
    """Exception for configuration errors in Key Vault client."""
    
    def __init__(self, message: str = "Key Vault configuration error", details: str = None):
        super().__init__(message, details)
        self.error_code = "KEYVAULT-009"


class KeyVaultCircuitBreakerError(KeyVaultError):
    """Exception for circuit breaker being open in Key Vault client."""
    
    def __init__(self, message: str = "Key Vault circuit breaker is open", retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after
        self.error_code = "KEYVAULT-010"
    
    def __str__(self) -> str:
        if self.retry_after:
            return f"{self.message} - Retry after {self.retry_after} seconds"
        return self.message
