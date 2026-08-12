"""
Authentication Module for Azure Environment

Provides comprehensive authentication capabilities for MCP deployed in Azure Function Apps:
- Entra ID (Azure AD) integration
- JWT validation with Azure AD public keys
- Managed Identity support for Function Apps
- OAuth2 handling
- Token validation and caller attribution

Domain developers use decorators:
    from platform.auth import authenticated_tool, requires_permission, requires_role

    @authenticated_tool
    def get_donor_pipeline():
        ...

    @requires_permission("donor.read")
    def get_donor_data():
        ...
"""

from .models import CallerIdentity, AuthenticationResult, TokenData
from .exceptions import (
    AuthenticationError, 
    TokenValidationError, 
    TokenExpiredError, 
    InsufficientPermissionsError
)
from .entra_id import EntraIDAuthenticator
from .jwt_validation import JWTValidator
from .managed_identity import ManagedIdentityAuthenticator
from .decorators import (
    authenticated_tool, 
    requires_permission, 
    requires_role,
    set_current_identity,
    get_current_identity
)

__all__ = [
    'authenticated_tool',
    'requires_permission',
    'requires_role',
    'set_current_identity',
    'get_current_identity',
    'CallerIdentity',
    'AuthenticationResult',
    'TokenData',
    'AuthenticationError',
    'TokenValidationError',
    'TokenExpiredError',
    'InsufficientPermissionsError',
    'EntraIDAuthenticator',
    'JWTValidator',
    'ManagedIdentityAuthenticator'
]
