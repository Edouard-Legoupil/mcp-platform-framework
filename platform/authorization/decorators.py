"""Authorization Decorators"""
from functools import wraps
from typing import Callable, Any, Optional, List
from platform.auth import get_current_identity, AuthenticationError
from .rbac import get_rbac_engine
from platform.auth.exceptions import InsufficientPermissionsError
import logging

logger = logging.getLogger(__name__)

def requires_permission(permission: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_current_identity()
            if identity is None:
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            rbac_engine = get_rbac_engine()
            if not rbac_engine.check_permission(identity.user_id, permission):
                raise InsufficientPermissionsError(permission)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def requires_role(role: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_current_identity()
            if identity is None:
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            rbac_engine = get_rbac_engine()
            user_roles = rbac_engine.get_user_roles(identity.user_id)
            
            if role not in user_roles:
                raise InsufficientPermissionsError(f"Role required: {role}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
