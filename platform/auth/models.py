"""
Authentication Models for Azure Environment
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class TokenData(BaseModel):
    """JWT token payload structure for Azure AD"""
    sub: str  # Subject (user identifier)
    name: Optional[str] = None
    email: Optional[str] = None
    preferred_username: Optional[str] = None
    oid: Optional[str] = None  # Object ID in Azure AD
    tid: Optional[str] = None  # Tenant ID
    
    # Azure AD specific claims
    roles: List[str] = []
    scopes: List[str] = []
    groups: List[str] = []
    
    # Standard JWT claims
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    nbf: Optional[datetime] = None  # Not before
    iss: str  # Issuer
    aud: str  # Audience
    jti: Optional[str] = None  # JWT ID
    
    # Additional Azure claims
    appid: Optional[str] = None  # Application ID
    appidacr: Optional[str] = None  # Application ID audience claim
    azp: Optional[str] = None  # Authorized party
    azpacr: Optional[str] = None  # Authorized party audience claim
    
    # Custom claims
    custom_claims: Dict[str, Any] = {}


class CallerIdentity(BaseModel):
    """Standardized caller identity information for Azure"""
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    object_id: Optional[str] = None  # Azure AD Object ID
    tenant_id: Optional[str] = None  # Azure AD Tenant ID
    
    authentication_type: str  # "entra_id", "managed_identity", "api_key", "anonymous"
    is_authenticated: bool = True
    
    # Azure-specific attributes
    claims: Dict[str, Any] = {}
    scopes: List[str] = []
    roles: List[str] = []
    groups: List[str] = []
    
    # Function App specific
    function_app_name: Optional[str] = None
    function_app_region: Optional[str] = None
    
    # Managed Identity specific
    managed_identity_client_id: Optional[str] = None


class AuthenticationResult(BaseModel):
    """Result of authentication attempt"""
    success: bool
    identity: Optional[CallerIdentity] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    # Azure-specific
    token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class AzureADConfig(BaseModel):
    """Azure AD configuration"""
    tenant_id: str
    client_id: str
    audience: str = "api://default"
    issuer: Optional[str] = None
    
    # For client credentials flow
    client_secret: Optional[str] = None
    certificate_thumbprint: Optional[str] = None
    
    # For on-behalf-of flow
    scope: str = "https://graph.microsoft.com/.default"
    
    def get_issuer(self) -> str:
        """Get the issuer URL for Azure AD"""
        return self.issuer or f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"


class ManagedIdentityConfig(BaseModel):
    """Managed Identity configuration for Function Apps"""
    identity_type: str = "SystemAssigned"  # SystemAssigned, UserAssigned
    user_assigned_client_id: Optional[str] = None
    
    # Resource access
    resource: str = "https://management.azure.com/"
