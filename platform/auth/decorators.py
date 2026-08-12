"""
Authentication Decorators for Azure Function Apps

Provides decorators for easy authentication integration in MCP tools.
"""

from functools import wraps
from typing import Callable, Any, Optional, List
from .models import CallerIdentity
from .exceptions import (
    AuthenticationError, 
    InsufficientPermissionsError
)
import logging

logger = logging.getLogger(__name__)

# Global identity context (set by authentication middleware)
_current_identity: Optional[CallerIdentity] = None


def set_current_identity(identity: CallerIdentity):
    """Set the current caller identity (used by middleware)"""
    global _current_identity
    _current_identity = identity


def get_current_identity() -> Optional[CallerIdentity]:
    """Get the current caller identity"""
    return _current_identity


def authenticated_tool(func: Callable) -> Callable:
    """
    Decorator to ensure tool is called by authenticated user
    
    Usage:
        @authenticated_tool
        def get_donor_pipeline():
            ...
    
    Raises:
        AuthenticationError: If user is not authenticated
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        identity = get_current_identity()
        if identity is None or not identity.is_authenticated:
            logger.warning("Unauthenticated access attempt")
            raise AuthenticationError("Authentication required", "AUTH-001")
        return func(*args, **kwargs)
    return wrapper


def requires_permission(permission: str):
    """
    Decorator to check for specific permission
    
    Usage:
        @requires_permission("donor.read")
        def get_donor_data():
            ...
    
    Args:
        permission: The required permission (e.g., "donor.read")
        
    Raises:
        AuthenticationError: If user is not authenticated
        InsufficientPermissionsError: If user lacks the required permission
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_current_identity()
            if identity is None:
                logger.warning("Unauthenticated access attempt")
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            # Check if user has the required permission
            user_permissions = identity.claims.get("scopes", [])
            user_roles = identity.claims.get("roles", [])
            
            # Check direct permission match
            if permission in user_permissions or permission in user_roles:
                return func(*args, **kwargs)
            
            # Check for wildcard permissions
            if any(perm.endswith(".*") and permission.startswith(perm[:-2]) 
                   for perm in user_permissions):
                return func(*args, **kwargs)
            
            # Check for domain-level permissions
            if any(perm == permission.split(".")[0] for perm in user_permissions):
                return func(*args, **kwargs)
            
            logger.warning(f"Permission denied: {permission} required")
            raise InsufficientPermissionsError(permission)
        
        return wrapper
    return decorator


def requires_any_permission(permissions: List[str]):
    """
    Decorator to check for any of the specified permissions
    
    Usage:
        @requires_any_permission(["donor.read", "donor.admin"])
        def get_donor_data():
            ...
    
    Args:
        permissions: List of permissions, any one of which is required
        
    Raises:
        AuthenticationError: If user is not authenticated
        InsufficientPermissionsError: If user lacks all required permissions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_current_identity()
            if identity is None:
                logger.warning("Unauthenticated access attempt")
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            user_permissions = identity.claims.get("scopes", [])
            user_roles = identity.claims.get("roles", [])
            
            # Check if user has any of the required permissions
            has_permission = any(
                perm in user_permissions or perm in user_roles or
                any(p.endswith(".*") and perm.startswith(p[:-2]) for p in user_permissions)
                for perm in permissions
            )
            
            if not has_permission:
                logger.warning(f"Permission denied: one of {permissions} required")
                raise InsufficientPermissionsError(f"One of: {permissions}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def requires_role(role: str):
    """
    Decorator to check for specific role
    
    Usage:
        @requires_role("donor_analyst")
        def analyze_donor_portfolio():
            ...
    
    Args:
        role: The required role (e.g., "donor_analyst")
        
    Raises:
        AuthenticationError: If user is not authenticated
        InsufficientPermissionsError: If user lacks the required role
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_current_identity()
            if identity is None:
                logger.warning("Unauthenticated access attempt")
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            user_roles = identity.claims.get("roles", [])
            user_groups = identity.claims.get("groups", [])
            
            # Check direct role match
            if role in user_roles or role in user_groups:
                return func(*args, **kwargs)
            
            # Check for role prefixes (e.g., "admin" matches "donor_admin")
            if any(r.endswith(f"_{role}") or r.startswith(f"{role}_") for r in user_roles):
                return func(*args, **kwargs)
            
            logger.warning(f"Role denied: {role} required")
            raise InsufficientPermissionsError(f"Role required: {role}")
        
        return wrapper
    return decorator


def requires_any_role(roles: List[str]):
    """
    Decorator to check for any of the specified roles
    
    Usage:
        @requires_any_role(["donor_analyst", "donor_admin"])
        def analyze_donor_data():
            ...
    
    Args:
        roles: List of roles, any one of which is required
        
    Raises:
        AuthenticationError: If user is not authenticated
        InsufficientPermissionsError: If user lacks all required roles
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_current_identity()
            if identity is None:
                logger.warning("Unauthenticated access attempt")
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            user_roles = identity.claims.get("roles", [])
            user_groups = identity.claims.get("groups", [])
            
            # Check if user has any of the required roles
            has_role = any(
                role in user_roles or role in user_groups or
                any(r.endswith(f"_{role}") or r.startswith(f"{role}_") for r in user_roles)
                for role in roles
            )
            
            if not has_role:
                logger.warning(f"Role denied: one of {roles} required")
                raise InsufficientPermissionsError(f"One of roles: {roles}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def requires_azure_ad_group(group_id: str):
    """
    Decorator to check for Azure AD group membership
    
    Usage:
        @requires_azure_ad_group("12345678-1234-5678-1234-567812345678")
        def admin_function():
            ...
    
    Args:
        group_id: The Azure AD group object ID
        
    Raises:
        AuthenticationError: If user is not authenticated
        InsufficientPermissionsError: If user is not in the required group
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_current_identity()
            if identity is None:
                logger.warning("Unauthenticated access attempt")
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            user_groups = identity.claims.get("groups", [])
            
            if group_id not in user_groups:
                logger.warning(f"Group membership denied: {group_id} required")
                raise InsufficientPermissionsError(f"Azure AD group required: {group_id}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def requires_managed_identity():
    """
    Decorator to ensure the caller is a Managed Identity
    
    Usage:
        @requires_managed_identity()
        def internal_service_call():
            ...
    
    Raises:
        AuthenticationError: If caller is not a Managed Identity
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_current_identity()
            if identity is None:
                logger.warning("Unauthenticated access attempt")
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            if identity.authentication_type != "managed_identity":
                logger.warning("Non-Managed Identity access attempt")
                raise AuthenticationError("Managed Identity required", "AUTH-010")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
