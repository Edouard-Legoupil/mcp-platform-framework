"""
Key Vault Client for MCP Platform Framework

This module provides the main client for interacting with Azure Key Vault.
It handles authentication, secret retrieval, caching, and error handling.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from .models import (
    SecretReference, SecretType, SecretMetadata, 
    SecretCacheEntry, KeyVaultConfig
)
from .cache import SecretCache
from .exceptions import (
    KeyVaultError,
    KeyVaultConnectionError,
    KeyVaultAuthenticationError,
    KeyVaultAuthorizationError,
    KeyVaultNotFoundError,
    KeyVaultSecretExpiredError,
    KeyVaultSecretDisabledError,
    KeyVaultRateLimitError,
    KeyVaultCacheError,
    KeyVaultConfigurationError,
    KeyVaultCircuitBreakerError
)
from platform.config import ConfigManager
from platform.telemetry import telemetry

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for resilience.
    
    This class implements the circuit breaker pattern to prevent
    cascading failures when Key Vault is unavailable.
    """
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 30):
        """
        Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening
            reset_timeout: Time in seconds before attempting to reset
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def record_failure(self):
        """Record a failure."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def record_success(self):
        """Record a success."""
        with self._lock:
            if self.state == "OPEN":
                # Transition to HALF_OPEN to test if service is back
                self.state = "HALF_OPEN"
                self.failure_count = 0
            elif self.state == "HALF_OPEN":
                # If success in HALF_OPEN, go back to CLOSED
                self.state = "CLOSED"
                self.failure_count = 0
            else:
                # In CLOSED state, just reset failure count
                self.failure_count = 0
    
    def can_execute(self) -> bool:
        """
        Check if a request can be executed.
        
        Returns:
            True if request can be executed, False otherwise
        """
        with self._lock:
            if self.state == "CLOSED":
                return True
            elif self.state == "OPEN":
                # Check if reset timeout has passed
                if time.time() - self.last_failure_time > self.reset_timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            else:  # HALF_OPEN
                return True
    
    def get_retry_after(self) -> Optional[int]:
        """
        Get time to wait before retrying.
        
        Returns:
            Seconds to wait, or None if no wait is needed
        """
        with self._lock:
            if self.state == "OPEN":
                remaining = self.reset_timeout - (time.time() - self.last_failure_time)
                return max(0, int(remaining))
            return None


class KeyVaultClient:
    """
    Client for interacting with Azure Key Vault.
    
    This client provides methods for:
    - Retrieving secrets, keys, and certificates
    - Managing secret lifecycle
    - Caching secrets for performance
    - Handling errors and retries
    - Circuit breaker for resilience
    """
    
    def __init__(
        self, 
        vault_name: Optional[str] = None,
        config: Optional[KeyVaultConfig] = None,
        cache_enabled: Optional[bool] = None,
        cache_ttl: Optional[int] = None
    ):
        """
        Initialize the KeyVaultClient.
        
        Args:
            vault_name: Name of the Key Vault to use
            config: Optional KeyVaultConfig
            cache_enabled: Whether to enable caching
            cache_ttl: Cache TTL in seconds
        """
        self.config = config or self._load_config(vault_name)
        self.vault_name = vault_name or self.config.vault_name
        self.session = requests.Session()
        self.cache = SecretCache(
            ttl_seconds=cache_ttl or self.config.cache_ttl_seconds
        ) if (cache_enabled or self.config.cache_enabled) else None
        self.circuit_breaker = CircuitBreaker()
        
        self._initialize_session()
        
    def _load_config(self, vault_name: str = None) -> KeyVaultConfig:
        """Load configuration from environment and config files."""
        config_manager = ConfigManager()
        keyvault_config = config_manager.get_config("azure.key_vault")
        
        # Get vault name from environment or config
        vault_name = vault_name or os.getenv("KEY_VAULT_NAME") or keyvault_config.get("name")
        
        if not vault_name:
            raise KeyVaultConfigurationError(
                "Key Vault name not configured. "
                "Set KEY_VAULT_NAME environment variable or configure in config file."
            )
        
        return KeyVaultConfig(
            vault_name=vault_name,
            endpoint=os.getenv("KEY_VAULT_ENDPOINT") or keyvault_config.get("endpoint"),
            tenant_id=os.getenv("AZURE_TENANT_ID") or keyvault_config.get("tenant_id"),
            client_id=os.getenv("AZURE_CLIENT_ID") or keyvault_config.get("client_id"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
            use_managed_identity=os.getenv("KEY_VAULT_USE_MANAGED_IDENTITY", "true").lower() == "true",
            cache_enabled=os.getenv("KEY_VAULT_CACHE_ENABLED", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("KEY_VAULT_CACHE_TTL_SECONDS", "300")),
            max_retries=int(os.getenv("KEY_VAULT_MAX_RETRIES", "3")),
            retry_delay_seconds=float(os.getenv("KEY_VAULT_RETRY_DELAY_SECONDS", "1.0")),
            timeout_seconds=int(os.getenv("KEY_VAULT_TIMEOUT_SECONDS", "30"))
        )
    
    def _initialize_session(self):
        """Initialize the HTTP session with headers and authentication."""
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Set User-Agent
        user_agent = f"MCP-KeyVault-Client/{os.getenv('MCP_VERSION', '1.0.0')}"
        self.session.headers["User-Agent"] = user_agent
        
        # Get access token for authentication
        self._ensure_authentication()
    
    def _ensure_authentication(self):
        """Ensure we have valid authentication for Key Vault."""
        if self.config.use_managed_identity:
            self._authenticate_with_managed_identity()
        else:
            self._authenticate_with_service_principal()
    
    def _authenticate_with_managed_identity(self):
        """Authenticate using Managed Identity."""
        try:
            # Try to get token using DefaultAzureCredential
            from azure.identity import DefaultAzureCredential
            
            credential = DefaultAzureCredential()
            token = credential.get_token("https://vault.azure.net/.default")
            
            self.session.headers["Authorization"] = f"Bearer {token.token}"
            logger.debug("Authenticated with Managed Identity")
            
        except ImportError:
            logger.warning("azure-identity not available, trying alternative methods")
            self._authenticate_with_alternative()
        except Exception as e:
            logger.error(f"Failed to authenticate with Managed Identity: {str(e)}")
            raise KeyVaultAuthenticationError(
                "Failed to authenticate with Managed Identity",
                str(e)
            )
    
    def _authenticate_with_service_principal(self):
        """Authenticate using Service Principal."""
        if not all([self.config.tenant_id, self.config.client_id, self.config.client_secret]):
            raise KeyVaultConfigurationError(
                "Service Principal authentication requires tenant_id, client_id, and client_secret"
            )
        
        try:
            # Get token using service principal
            from azure.identity import ClientSecretCredential
            
            credential = ClientSecretCredential(
                tenant_id=self.config.tenant_id,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret
            )
            
            token = credential.get_token("https://vault.azure.net/.default")
            self.session.headers["Authorization"] = f"Bearer {token.token}"
            logger.debug("Authenticated with Service Principal")
            
        except ImportError:
            logger.warning("azure-identity not available, trying alternative methods")
            self._authenticate_with_alternative()
        except Exception as e:
            logger.error(f"Failed to authenticate with Service Principal: {str(e)}")
            raise KeyVaultAuthenticationError(
                "Failed to authenticate with Service Principal",
                str(e)
            )
    
    def _authenticate_with_alternative(self):
        """Alternative authentication method using direct token acquisition."""
        # This is a fallback method that might work in some environments
        try:
            # Try to get token from environment
            token = os.getenv("KEY_VAULT_TOKEN")
            if token:
                self.session.headers["Authorization"] = f"Bearer {token}"
                logger.debug("Authenticated with environment token")
                return
            
            # Try to get token from file
            token_file = os.getenv("KEY_VAULT_TOKEN_FILE")
            if token_file and os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    token = f.read().strip()
                self.session.headers["Authorization"] = f"Bearer {token}"
                logger.debug("Authenticated with token file")
                return
            
            raise KeyVaultAuthenticationError(
                "No valid authentication method available. "
                "Configure Managed Identity, Service Principal, or provide a token."
            )
            
        except Exception as e:
            logger.error(f"Alternative authentication failed: {str(e)}")
            raise KeyVaultAuthenticationError(
                "Alternative authentication failed",
                str(e)
            )
    
    def _get_vault_url(self) -> str:
        """Get the full URL for the Key Vault."""
        if self.config.endpoint:
            return self.config.endpoint
        return f"https://{self.vault_name}.vault.azure.net"
    
    def _make_request(
        self, 
        method: str, 
        path: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Key Vault with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            data: Request body data
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary containing response data
            
        Raises:
            KeyVaultConnectionError: If connection to Key Vault fails
            KeyVaultAuthenticationError: If authentication fails
            KeyVaultAuthorizationError: If authorization fails
            KeyVaultNotFoundError: If resource is not found
            KeyVaultRateLimitError: If rate limit is exceeded
        """
        url = urljoin(self._get_vault_url(), path)
        timeout = timeout or self.config.timeout_seconds
        
        max_retries = self.config.max_retries
        retry_delay = self.config.retry_delay_seconds
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            retry_after = self.circuit_breaker.get_retry_after()
            raise KeyVaultCircuitBreakerError(
                "Key Vault circuit breaker is open",
                retry_after
            )
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=timeout
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Track telemetry
                telemetry.track_request(
                    service="keyvault",
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    duration_ms=duration_ms
                )
                
                # Record success with circuit breaker
                self.circuit_breaker.record_success()
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    self.circuit_breaker.record_failure()
                    raise KeyVaultAuthenticationError("Authentication failed")
                elif response.status_code == 403:
                    self.circuit_breaker.record_failure()
                    raise KeyVaultAuthorizationError("Access denied")
                elif response.status_code == 404:
                    self.circuit_breaker.record_failure()
                    raise KeyVaultNotFoundError(
                        f"Resource not found: {path}",
                        path.split("/")[-1] if "/" in path else path,
                        self.vault_name
                    )
                elif response.status_code == 429:
                    # Rate limiting
                    retry_after = int(response.headers.get("Retry-After", 5))
                    self.circuit_breaker.record_failure()
                    raise KeyVaultRateLimitError(
                        "Key Vault rate limit exceeded",
                        retry_after
                    )
                elif response.status_code >= 500:
                    self.circuit_breaker.record_failure()
                    if attempt < max_retries:
                        logger.warning(f"Request failed, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries + 1})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise KeyVaultConnectionError(f"Server error: {response.text}")
                else:
                    self.circuit_breaker.record_failure()
                    raise KeyVaultError(f"Unexpected status code: {response.status_code}")
                    
            except (ConnectionError, Timeout) as e:
                self.circuit_breaker.record_failure()
                if attempt < max_retries:
                    logger.warning(f"Connection failed, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise KeyVaultConnectionError(f"Connection failed: {str(e)}")
        
        # This should never be reached
        raise KeyVaultError("Request failed after all retries")
    
    def get_secret(self, secret_name: str, version: str = None) -> str:
        """
        Get a secret from Azure Key Vault.
        
        Args:
            secret_name: Name of the secret to retrieve
            version: Optional version of the secret
            
        Returns:
            The secret value
            
        Raises:
            KeyVaultError: If secret retrieval fails
        """
        # Check cache first
        if self.cache:
            cached_value = self.cache.get(secret_name, self.vault_name)
            if cached_value is not None:
                logger.debug(f"Retrieved secret {secret_name} from cache")
                telemetry.track_cache_hit("keyvault", secret_name)
                return cached_value
            telemetry.track_cache_miss("keyvault", secret_name)
        
        # Build path
        path = f"/secrets/{secret_name}"
        if version:
            path += f"/{version}"
        
        try:
            response = self._make_request("GET", path)
            secret_value = response.get("value")
            
            if not secret_value:
                raise KeyVaultNotFoundError(
                    f"Secret '{secret_name}' not found or has no value",
                    secret_name,
                    self.vault_name
                )
            
            # Check if secret is enabled
            if not response.get("attributes", {}).get("enabled", True):
                raise KeyVaultSecretDisabledError(
                    f"Secret '{secret_name}' is disabled",
                    secret_name,
                    self.vault_name
                )
            
            # Check if secret is expired
            expires = response.get("attributes", {}).get("exp")
            if expires:
                exp_date = datetime.fromisoformat(expires.replace("Z", "+00:00"))
                if exp_date < datetime.utcnow():
                    raise KeyVaultSecretExpiredError(
                        f"Secret '{secret_name}' has expired",
                        secret_name,
                        self.vault_name
                    )
            
            # Cache the secret
            if self.cache:
                self.cache.set(
                    secret_name=secret_name,
                    secret_value=secret_value,
                    vault_name=self.vault_name,
                    secret_type=SecretType.SECRET
                )
            
            logger.debug(f"Retrieved secret {secret_name} from Key Vault")
            telemetry.track_event("keyvault.secret.retrieved", {"secret_name": secret_name})
            
            return secret_value
            
        except KeyVaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {str(e)}")
            telemetry.track_exception(e, context={"secret_name": secret_name})
            raise KeyVaultError(f"Failed to get secret: {str(e)}")
    
    def get_secret_by_reference(self, reference: Union[str, SecretReference]) -> str:
        """
        Get a secret using a SecretReference.
        
        Args:
            reference: SecretReference or string reference
            
        Returns:
            The secret value
            
        Raises:
            KeyVaultError: If secret retrieval fails
        """
        if isinstance(reference, str):
            reference = SecretReference.from_string(reference)
        
        return self.get_secret(
            secret_name=reference.name,
            version=reference.version
        )
    
    def get_key(self, key_name: str, version: str = None) -> bytes:
        """
        Get a key from Azure Key Vault.
        
        Args:
            key_name: Name of the key to retrieve
            version: Optional version of the key
            
        Returns:
            The key as bytes
            
        Raises:
            KeyVaultError: If key retrieval fails
        """
        # Build path
        path = f"/keys/{key_name}"
        if version:
            path += f"/{version}"
        
        try:
            response = self._make_request("GET", path)
            
            # Extract key material (this is a simplified example)
            # In a real implementation, you would handle the key properly
            key_value = response.get("key", {}).get("n")  # Public modulus
            
            if not key_value:
                raise KeyVaultNotFoundError(
                    f"Key '{key_name}' not found or has no value",
                    key_name,
                    self.vault_name
                )
            
            logger.debug(f"Retrieved key {key_name} from Key Vault")
            telemetry.track_event("keyvault.key.retrieved", {"key_name": key_name})
            
            # Note: This returns the public key modulus as an example
            # In a real implementation, you would handle the key properly
            return key_value.encode() if key_value else b""
            
        except KeyVaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get key {key_name}: {str(e)}")
            telemetry.track_exception(e, context={"key_name": key_name})
            raise KeyVaultError(f"Failed to get key: {str(e)}")
    
    def get_certificate(self, certificate_name: str, version: str = None) -> bytes:
        """
        Get a certificate from Azure Key Vault.
        
        Args:
            certificate_name: Name of the certificate to retrieve
            version: Optional version of the certificate
            
        Returns:
            The certificate as bytes (PEM format)
            
        Raises:
            KeyVaultError: If certificate retrieval fails
        """
        # Build path
        path = f"/certificates/{certificate_name}"
        if version:
            path += f"/{version}"
        
        try:
            response = self._make_request("GET", path)
            
            # Extract certificate (this is a simplified example)
            # In a real implementation, you would handle the certificate properly
            cert_value = response.get("cer")  # Certificate data
            
            if not cert_value:
                raise KeyVaultNotFoundError(
                    f"Certificate '{certificate_name}' not found or has no value",
                    certificate_name,
                    self.vault_name
                )
            
            logger.debug(f"Retrieved certificate {certificate_name} from Key Vault")
            telemetry.track_event("keyvault.certificate.retrieved", {"certificate_name": certificate_name})
            
            # Note: This returns the certificate data as an example
            # In a real implementation, you would handle the certificate properly
            return cert_value.encode() if cert_value else b""
            
        except KeyVaultNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get certificate {certificate_name}: {str(e)}")
            telemetry.track_exception(e, context={"certificate_name": certificate_name})
            raise KeyVaultError(f"Failed to get certificate: {str(e)}")
    
    def list_secrets(self, prefix: str = None) -> List[str]:
        """
        List secrets in the Key Vault.
        
        Args:
            prefix: Optional prefix to filter secrets
            
        Returns:
            List of secret names
            
        Raises:
            KeyVaultError: If listing fails
        """
        try:
            path = "/secrets"
            params = {}
            if prefix:
                params["$filter"] = f"startswith(name, '{prefix}')"
            
            response = self._make_request("GET", path, params=params)
            secrets = response.get("value", [])
            
            return [secret["name"] for secret in secrets]
            
        except Exception as e:
            logger.error(f"Failed to list secrets: {str(e)}")
            telemetry.track_exception(e, context={"operation": "list_secrets"})
            raise KeyVaultError(f"Failed to list secrets: {str(e)}")
    
    def get_secret_metadata(self, secret_name: str) -> SecretMetadata:
        """
        Get metadata about a secret.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            SecretMetadata object
            
        Raises:
            KeyVaultError: If metadata retrieval fails
        """
        try:
            path = f"/secrets/{secret_name}"
            response = self._make_request("GET", path)
            
            attributes = response.get("attributes", {})
            
            return SecretMetadata(
                name=secret_name,
                vault_name=self.vault_name,
                secret_type=SecretType.SECRET,
                enabled=attributes.get("enabled", True),
                created_at=datetime.fromisoformat(attributes.get("created", "").replace("Z", "+00:00")) if attributes.get("created") else None,
                updated_at=datetime.fromisoformat(attributes.get("updated", "").replace("Z", "+00:00")) if attributes.get("updated") else None,
                expires_at=datetime.fromisoformat(attributes.get("exp", "").replace("Z", "+00:00")) if attributes.get("exp") else None,
                version=attributes.get("version"),
                tags=attributes.get("tags", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to get secret metadata for {secret_name}: {str(e)}")
            raise KeyVaultError(f"Failed to get secret metadata: {str(e)}")
    
    def set_secret(self, secret_name: str, secret_value: str, **kwargs) -> str:
        """
        Set a secret in Azure Key Vault.
        
        Args:
            secret_name: Name of the secret
            secret_value: Value of the secret
            **kwargs: Additional secret attributes
            
        Returns:
            The version of the created/updated secret
            
        Raises:
            KeyVaultError: If setting secret fails
        """
        try:
            path = f"/secrets/{secret_name}"
            data = {"value": secret_value}
            
            # Add additional attributes if provided
            if kwargs:
                data["attributes"] = kwargs
            
            response = self._make_request("PUT", path, data)
            
            # Invalidate cache
            if self.cache:
                self.cache.remove(secret_name, self.vault_name)
            
            logger.debug(f"Set secret {secret_name} in Key Vault")
            telemetry.track_event("keyvault.secret.set", {"secret_name": secret_name})
            
            return response.get("version")
            
        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {str(e)}")
            telemetry.track_exception(e, context={"secret_name": secret_name})
            raise KeyVaultError(f"Failed to set secret: {str(e)}")
    
    def delete_secret(self, secret_name: str) -> bool:
        """
        Delete a secret from Azure Key Vault.
        
        Args:
            secret_name: Name of the secret to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            KeyVaultError: If deletion fails
        """
        try:
            path = f"/secrets/{secret_name}"
            response = self._make_request("DELETE", path)
            
            # Invalidate cache
            if self.cache:
                self.cache.remove(secret_name, self.vault_name)
            
            logger.debug(f"Deleted secret {secret_name} from Key Vault")
            telemetry.track_event("keyvault.secret.deleted", {"secret_name": secret_name})
            
            return response.get("status", False)
            
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {str(e)}")
            telemetry.track_exception(e, context={"secret_name": secret_name})
            raise KeyVaultError(f"Failed to delete secret: {str(e)}")
    
    def clear_cache(self) -> int:
        """
        Clear the secret cache.
        
        Returns:
            Number of entries cleared
        """
        if self.cache:
            count = self.cache.clear()
            logger.info(f"Cleared {count} entries from Key Vault cache")
            return count
        return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        if self.cache:
            return self.cache.get_stats()
        return {"status": "disabled"}
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """
        Get circuit breaker status.
        
        Returns:
            Dictionary with circuit breaker status
        """
        return {
            "state": self.circuit_breaker.state,
            "failure_count": self.circuit_breaker.failure_count,
            "failure_threshold": self.circuit_breaker.failure_threshold,
            "reset_timeout": self.circuit_breaker.reset_timeout,
            "retry_after": self.circuit_breaker.get_retry_after()
        }


# Import threading for CircuitBreaker
import threading
