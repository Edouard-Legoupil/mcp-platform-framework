"""
Authorization Module for Azure Environment

Provides enterprise RBAC, permission decorators, and policy enforcement.
"""

from .models import Role, Policy, AccessRequest, AccessDecision
from .rbac import RBACEngine
from .decorators import requires_permission, requires_role, set_rbac_engine, get_rbac_engine

__all__ = [
    'Role', 'Policy', 'AccessRequest', 'AccessDecision',
    'RBACEngine', 'requires_permission', 'requires_role',
    'set_rbac_engine', 'get_rbac_engine'
]
