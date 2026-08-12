"""
Managed Identity Authentication for Azure Function Apps

Provides Managed Identity authentication specifically for Azure Function Apps.
"""

from typing import Optional, Dict, Any
from .models import CallerIdentity, AuthenticationResult
from .exceptions import ManagedIdentityError, AuthenticationError
import logging
import os

logger = logging.getLogger(__name__)


class ManagedIdentityAuthenticator:
    """
    Managed Identity authenticator for Azure Function Apps
    
    Supports:
    - System-assigned Managed Identity
    - User-assigned Managed Identity
    - Token acquisition for various Azure resources
    """
    
    def __init__(self, 
                 identity_type: str = "SystemAssigned",
                 user_assigned_client_id: Optional[str] = None,
                 resource: str = "https://management.azure.com/"):
        
        self.identity_type = identity_type
        self.user_assigned_client_id = user_assigned_client_id
        self.resource = resource
        self._token_cache: Dict[str, Dict[str, Any]] = {}
        
        # Validate identity type
        if identity_type not in ["SystemAssigned", "UserAssigned"]:
            raise AuthenticationError(f"Invalid identity type: {identity_type}")
        
        if identity_type == "UserAssigned" and not user_assigned_client_id:
            raise AuthenticationError("User-assigned identity requires client_id")
        
        logger.info(f"ManagedIdentityAuthenticator initialized with {identity_type} identity")
    
    def get_token(self, resource: Optional[str] = None) -> Optional[str]:
        """
        Get access token for the specified resource
        
        Args:
            resource: The Azure resource to get token for (default: self.resource)
            
        Returns:
            Access token or None if failed
        """
        resource = resource or self.resource
        
        # Check cache first
        cache_key = f"managed_identity:{resource}"
        if cache_key in self._token_cache:
            cached_token = self._token_cache[cache_key]
            if cached_token["expires_at"] > self._get_current_timestamp():
                return cached_token["access_token"]
        
        # Get token using Azure Identity library
        try:
            from azure.identity import (
                DefaultAzureCredential,
                ManagedIdentityCredential
            )
            
            # Use DefaultAzureCredential which tries multiple authentication methods
            credential = DefaultAzureCredential()
            
            # For Function Apps, ManagedIdentityCredential is more specific
            if self.identity_type == "UserAssigned" and self.user_assigned_client_id:
                credential = ManagedIdentityCredential(
                    client_id=self.user_assigned_client_id
                )
            
            token = credential.get_token(resource)
            access_token = token.token
            expires_at = token.expires_on.timestamp() if token.expires_on else 0
            
            if access_token:
                # Cache the token
                self._token_cache[cache_key] = {
                    "access_token": access_token,
                    "expires_at": int(expires_at) - 60  # 1 minute buffer
                }
                return access_token
            
            logger.error("Failed to get Managed Identity token: no access_token in response")
            return None
            
        except ImportError:
            logger.warning("Azure Identity library not available")
            return None
        except Exception as e:
            logger.error(f"Failed to get Managed Identity token: {e}")
            return None
    
    def get_identity(self) -> Optional[CallerIdentity]:
        """
        Get the Managed Identity information
        
        Returns:
            CallerIdentity representing the Managed Identity
        """
        try:
            # Get token to extract identity information
            token = self.get_token("https://graph.microsoft.com/")
            if not token:
                return None
            
            # Decode the token to get identity information
            import jwt
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                
                return CallerIdentity(
                    user_id=payload.get("sub", "unknown"),
                    username=payload.get("name"),
                    email=payload.get("email"),
                    object_id=payload.get("oid"),
                    tenant_id=payload.get("tid"),
                    authentication_type="managed_identity",
                    is_authenticated=True,
                    claims={"iss": payload.get("iss"), "aud": payload.get("aud")},
                    managed_identity_client_id=self.user_assigned_client_id
                )
            except Exception as e:
                logger.error(f"Failed to decode Managed Identity token: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get Managed Identity: {e}")
            return None
    
    def authenticate(self) -> AuthenticationResult:
        """
        Authenticate using Managed Identity
        
        Returns:
            AuthenticationResult with Managed Identity information
        """
        identity = self.get_identity()
        token = self.get_token() if identity else None
        
        if identity:
            return AuthenticationResult(
                success=True,
                identity=identity,
                token=token
            )
        else:
            return AuthenticationResult(
                success=False,
                error="Failed to authenticate with Managed Identity",
                error_code="AUTH-010"
            )
    
    def _get_current_timestamp(self) -> int:
        """Get current timestamp in seconds"""
        import time
        return int(time.time())
    
    def clear_cache(self):
        """Clear all token caches"""
        self._token_cache.clear()


# Global Managed Identity authenticator instance
_managed_identity_authenticator: Optional[ManagedIdentityAuthenticator] = None


def get_managed_identity_authenticator() -> Optional[ManagedIdentityAuthenticator]:
    """Get the global Managed Identity authenticator"""
    return _managed_identity_authenticator


def set_managed_identity_authenticator(authenticator: ManagedIdentityAuthenticator):
    """Set the global Managed Identity authenticator"""
    global _managed_identity_authenticator
    _managed_identity_authenticator = authenticator


# Alias for backward compatibility
ManagedIdentityAuthenticator = ManagedIdentityAuthenticator
