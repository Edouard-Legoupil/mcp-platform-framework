"""Classification Decorators"""
from functools import wraps
from typing import Callable, Any, Optional
from .models import ClassificationLevel
from .controls import get_classification_engine
from platform.auth import get_current_identity, AuthenticationError
from platform.errors import AuthorizationException
import logging

logger = logging.getLogger(__name__)

def classification(level: ClassificationLevel):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            engine = get_classification_engine()
            identity = get_current_identity()
            
            if identity is None:
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            decision = engine.check_access_control(
                resource_id=func.__name__,
                action="execute",
                user_permissions=identity.claims.get("scopes", []),
                user_roles=identity.claims.get("roles", [])
            )
            
            if not decision.get("allowed"):
                raise AuthorizationException(
                    f"Access denied to {level.value} tool: {func.__name__}",
                    "CLASS-001",
                    details={"required_classification": level.value, "policy_violations": decision.get("policy_violations", [])}
                )
            
            return func(*args, **kwargs)
        
        wrapper._classification = level
        return wrapper
    return decorator

def classify_data(level: ClassificationLevel):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # In production, apply data protection based on classification
            return result
        
        wrapper._data_classification = level
        return wrapper
    return decorator

def requires_classification(min_level: ClassificationLevel):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            engine = get_classification_engine()
            identity = get_current_identity()
            
            if identity is None:
                raise AuthenticationError("Authentication required", "AUTH-001")
            
            current_level = ClassificationLevel.INTERNAL
            level_order = [ClassificationLevel.PUBLIC, ClassificationLevel.INTERNAL, ClassificationLevel.CONFIDENTIAL, ClassificationLevel.STRICTLY_CONFIDENTIAL]
            current_index = level_order.index(current_level)
            required_index = level_order.index(min_level)
            
            if current_index < required_index:
                raise AuthorizationException(
                    f"Requires {min_level.value} classification or higher",
                    "CLASS-002",
                    details={"current_classification": current_level.value, "required_classification": min_level.value}
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
