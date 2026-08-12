"""
Entra ID (Azure AD) Authentication for Function Apps

Provides comprehensive Azure AD authentication capabilities optimized for Azure Function Apps.
"""

from typing import Optional, Dict, Any, List
from .models import (
    CallerIdentity, 
    AuthenticationResult,
    AzureADConfig
)
from .jwt_validation import AzureADJWTValidator
from .exceptions import (
    AuthenticationError,
    TokenValidationError,
    AzureADError
)
import logging
import os
import requests
import json

logger = logging.getLogger(__name__)


class EntraIDAuthenticator:
    """
    Azure AD (Entra ID) authenticator for Function Apps
    
    Supports:
    - Bearer token validation
    - Client credentials flow (for service-to-service)
    - On-behalf-of flow (for delegated permissions)
    - Managed Identity integration
    """
    
    def __init__(self, 
                 tenant_id: Optional[str] = None,
                 client_id: Optional[str] = None,
                 audience: str = "api://default",
                 config: Optional[AzureADConfig] = None):
        
        # Use config if provided, otherwise use individual parameters
        if config:
            self.tenant_id = config.tenant_id
            self.client_id = config.client_id
            self.audience = config.audience
            self.scope = config.scope
            self.client_secret = config.client_secret
            self.certificate_thumbprint = config.certificate_thumbprint
        else:
            self.tenant_id = tenant_id or os.environ.get("AZURE_TENANT_ID")
            self.client_id = client_id or os.environ.get("AZURE_CLIENT_ID")
            self.audience = audience
            self.scope = "https://graph.microsoft.com/.default"
            self.client_secret = os.environ.get("AZURE_CLIENT_SECRET")
            self.certificate_thumbprint = os.environ.get("AZURE_CERTIFICATE_THUMBPRINT")
        
        if not self.tenant_id:
            raise AuthenticationError("Azure AD tenant ID is required")
        
        if not self.client_id:
            raise AuthenticationError("Azure AD client ID is required")
        
        # Initialize JWT validator
        self.jwt_validator = AzureADJWTValidator(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            audience=self.audience
        )
        
        # Token cache for client credentials
        self._token_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"EntraIDAuthenticator initialized for tenant: {self.tenant_id}")
    
    def authenticate_bearer_token(self, token: str) -> AuthenticationResult:
        """
        Authenticate using Bearer token (user context)
        
        Args:
            token: Bearer token (without 'Bearer ' prefix)
            
        Returns:
            AuthenticationResult with caller identity
        """
        try:
            identity = self.jwt_validator.get_identity_from_token(token)
            identity.authentication_type = "entra_id"
            
            return AuthenticationResult(
                success=True,
                identity=identity,
                token=token
            )
        except Exception as e:
            logger.error(f"Entra ID bearer token authentication failed: {e}")
            return AuthenticationResult(
                success=False,
                error=str(e),
                error_code=getattr(e, 'error_code', 'AUTH-002')
            )
    
    def get_client_credentials_token(self, resource: str = None) -> Optional[str]:
        """
        Get access token using client credentials flow
        
        Args:
            resource: The resource to get token for (default: self.audience)
            
        Returns:
            Access token or None if failed
        """
        resource = resource or self.audience
        
        # Check cache first
        cache_key = f"client_credentials:{resource}"
        if cache_key in self._token_cache:
            cached_token = self._token_cache[cache_key]
            if cached_token["expires_at"] > self._get_current_timestamp():
                return cached_token["access_token"]
        
        # Get token from Azure AD
        try:
            token_endpoint = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "scope": f"{resource}/.default"
            }
            
            # Add client secret if available
            if self.client_secret:
                data["client_secret"] = self.client_secret
            
            # Add certificate if available
            elif self.certificate_thumbprint:
                # In production, would sign the request with certificate
                data["client_assertion_type"] = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
                # Would generate client assertion JWT here
                pass
            
            response = requests.post(token_endpoint, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            
            if access_token:
                # Cache the token
                self._token_cache[cache_key] = {
                    "access_token": access_token,
                    "expires_at": self._get_current_timestamp() + expires_in - 60  # 1 minute buffer
                }
                return access_token
            
            logger.error("Failed to get client credentials token: no access_token in response")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get client credentials token: {e}")
            return None
    
    def get_on_behalf_of_token(self, user_token: str, resource: str = None) -> Optional[str]:
        """
        Get access token using on-behalf-of flow
        
        Args:
            user_token: User's access token
            resource: The resource to get token for
            
        Returns:
            Access token or None if failed
        """
        resource = resource or self.scope
        
        try:
            token_endpoint = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            data = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "assertion": user_token,
                "requested_token_use": "on_behalf_of",
                "scope": resource
            }
            
            response = requests.post(token_endpoint, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get("access_token")
            
        except Exception as e:
            logger.error(f"Failed to get on-behalf-of token: {e}")
            return None
    
    def validate_and_get_identity(self, token: str) -> Optional[CallerIdentity]:
        """
        Validate token and return caller identity
        
        Args:
            token: Bearer token
            
        Returns:
            CallerIdentity or None if validation failed
        """
        try:
            return self.jwt_validator.get_identity_from_token(token)
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return None
    
    def get_managed_identity_token(self, resource: str = "https://management.azure.com/") -> Optional[str]:
        """
        Get access token for Managed Identity (for Function Apps)
        
        In Azure Function Apps, this uses the built-in Managed Identity.
        
        Args:
            resource: The Azure resource to get token for
            
        Returns:
            Access token or None if failed
        """
        try:
            # In Azure Function Apps, we can use the Azure Identity library
            from azure.identity import DefaultAzureCredential
            
            credential = DefaultAzureCredential()
            token = credential.get_token(resource)
            return token.token
            
        except ImportError:
            logger.warning("Azure Identity library not available")
            return None
        except Exception as e:
            logger.error(f"Failed to get Managed Identity token: {e}")
            return None
    
    def _get_current_timestamp(self) -> int:
        """Get current timestamp in seconds"""
        import time
        return int(time.time())
    
    def clear_cache(self):
        """Clear all token caches"""
        self._token_cache.clear()
        self.jwt_validator.clear_cache()


# Global Entra ID authenticator instance
_entra_id_authenticator: Optional[EntraIDAuthenticator] = None


def get_entra_id_authenticator() -> Optional[EntraIDAuthenticator]:
    """Get the global Entra ID authenticator"""
    return _entra_id_authenticator


def set_entra_id_authenticator(authenticator: EntraIDAuthenticator):
    """Set the global Entra ID authenticator"""
    global _entra_id_authenticator
    _entra_id_authenticator = authenticator


# Alias for backward compatibility
EntraIDAuthenticator = EntraIDAuthenticator
