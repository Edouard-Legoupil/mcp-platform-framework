"""RBAC Engine"""
from typing import Dict, List, Set, Optional
from .models import Role, AccessRequest, AccessDecision
import logging

logger = logging.getLogger(__name__)

class RBACEngine:
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        self.role_permissions: Dict[str, Set[str]] = {}
    
    def add_role(self, role: Role):
        self.roles[role.name] = role
        self.role_permissions[role.name] = set(role.permissions)
    
    def assign_role_to_user(self, user_id: str, role_name: str):
        if role_name not in self.roles:
            raise ValueError(f"Role {role_name} does not exist")
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        self.user_roles[user_id].add(role_name)
    
    def get_user_permissions(self, user_id: str) -> Set[str]:
        if user_id not in self.user_roles:
            return set()
        permissions = set()
        for role_name in self.user_roles[user_id]:
            if role_name in self.role_permissions:
                permissions.update(self.role_permissions[role_name])
        return permissions
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions
    
    def check_access(self, request: AccessRequest) -> AccessDecision:
        user_permissions = self.get_user_permissions(request.user_id)
        required_permission = f"{request.resource}.{request.action}"
        
        if required_permission in user_permissions:
            return AccessDecision(allowed=True, reason="Permission granted")
        
        wildcard_permission = f"{request.resource}.*"
        if wildcard_permission in user_permissions:
            return AccessDecision(allowed=True, reason="Wildcard permission granted")
        
        return AccessDecision(
            allowed=False,
            reason="Insufficient permissions",
            required_permissions=[required_permission],
            missing_permissions=[required_permission]
        )

# Global RBAC engine
_rbac_engine: Optional[RBACEngine] = None

def set_rbac_engine(engine: RBACEngine):
    global _rbac_engine
    _rbac_engine = engine

def get_rbac_engine() -> RBACEngine:
    global _rbac_engine
    if _rbac_engine is None:
        _rbac_engine = RBACEngine()
    return _rbac_engine
