"""Classification Controls for Azure Purview"""
from typing import Dict, List, Optional, Any, Set
from .models import ClassificationLevel, ClassificationPolicy, ClassifiedResource
import logging

logger = logging.getLogger(__name__)

class ClassificationEngine:
    def __init__(self):
        self._policies: Dict[ClassificationLevel, ClassificationPolicy] = {}
        self._resources: Dict[str, ClassifiedResource] = {}
        self._classification_rules: List[Callable] = []
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        self._policies = {
            ClassificationLevel.PUBLIC: ClassificationPolicy(
                level=ClassificationLevel.PUBLIC,
                description="Public data - no restrictions",
                allowed_actions=["read", "list", "search"],
                requires_approval=False,
                requires_justification=False,
                encryption_required=False,
                audit_required=False
            ),
            ClassificationLevel.INTERNAL: ClassificationPolicy(
                level=ClassificationLevel.INTERNAL,
                description="Internal data - restricted to organization",
                allowed_actions=["read", "write", "list"],
                requires_approval=False,
                requires_justification=False,
                encryption_required=True,
                audit_required=True
            ),
            ClassificationLevel.CONFIDENTIAL: ClassificationPolicy(
                level=ClassificationLevel.CONFIDENTIAL,
                description="Confidential data - restricted access",
                allowed_actions=["read", "write"],
                requires_approval=True,
                requires_justification=True,
                encryption_required=True,
                audit_required=True,
                access_logging_required=True
            ),
            ClassificationLevel.STRICTLY_CONFIDENTIAL: ClassificationPolicy(
                level=ClassificationLevel.STRICTLY_CONFIDENTIAL,
                description="Strictly confidential data - highest restrictions",
                allowed_actions=["read"],
                requires_approval=True,
                requires_justification=True,
                encryption_required=True,
                audit_required=True,
                access_logging_required=True,
                retention_days=365
            )
        }
    
    def get_policy(self, level: ClassificationLevel) -> ClassificationPolicy:
        return self._policies.get(level)
    
    def register_resource(self, resource: ClassifiedResource):
        self._resources[resource.resource_id] = resource
    
    def get_resource_classification(self, resource_id: str) -> Optional[ClassificationLevel]:
        resource = self._resources.get(resource_id)
        if resource:
            return resource.classification
        return None
    
    def check_access_control(self, resource_id: str, action: str, user_permissions: List[str], user_roles: List[str]) -> Any:
        resource = self._resources.get(resource_id)
        if not resource:
            return {"allowed": False, "reason": "Resource not found"}
        
        policy = self.get_policy(resource.classification)
        if action not in policy.allowed_actions:
            return {"allowed": False, "reason": f"Action '{action}' not allowed for {resource.classification.value} data"}
        
        required_permissions = self._get_required_permissions(resource, action)
        missing_permissions = []
        for perm in required_permissions:
            if perm not in user_permissions and perm not in user_roles:
                missing_permissions.append(perm)
        
        if missing_permissions:
            return {"allowed": False, "reason": "Insufficient permissions", "missing_permissions": missing_permissions}
        
        policy_violations = []
        if policy.requires_approval:
            policy_violations.append("Approval required")
        if policy.requires_justification:
            policy_violations.append("Justification required")
        
        if policy_violations:
            return {"allowed": False, "reason": "Policy violations", "policy_violations": policy_violations}
        
        return {"allowed": True, "classification": resource.classification}
    
    def _get_required_permissions(self, resource: ClassifiedResource, action: str) -> List[str]:
        classification_permissions = {
            ClassificationLevel.PUBLIC: [],
            ClassificationLevel.INTERNAL: ["internal.access"],
            ClassificationLevel.CONFIDENTIAL: ["confidential.access"],
            ClassificationLevel.STRICTLY_CONFIDENTIAL: ["strictly_confidential.access"]
        }
        permissions = classification_permissions.get(resource.classification, [])
        action_permissions = {"read": ["read"], "write": ["write"], "delete": ["delete"], "admin": ["admin"]}
        if action in action_permissions:
            permissions.extend(action_permissions[action])
        permissions.append(f"{resource.domain}.{action}")
        return permissions

# Global engine
_engine: Optional[ClassificationEngine] = None

def set_classification_engine(engine: ClassificationEngine):
    global _engine
    _engine = engine

def get_classification_engine() -> ClassificationEngine:
    global _engine
    if _engine is None:
        _engine = ClassificationEngine()
    return _engine
