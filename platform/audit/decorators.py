"""Audit Decorators"""
from functools import wraps
from typing import Callable, Any, Optional
from .logger import get_audit_logger
from .models import AuditEventType, SensitivityLevel
from platform.auth import get_current_identity
import logging

logger = logging.getLogger(__name__)

def audit_tool_access(resource: str, domain: str, sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            audit_logger = get_audit_logger()
            identity = get_current_identity()
            
            audit_logger.log(
                event_type=AuditEventType.TOOL_ACCESS,
                user_id=identity.user_id if identity else "anonymous",
                user_email=identity.email if identity else None,
                action=func.__name__,
                resource=resource,
                domain=domain,
                sensitivity=sensitivity,
                details={"arguments": list(args), "kwargs": dict(kwargs)}
            )
            
            try:
                result = func(*args, **kwargs)
                audit_logger.log(
                    event_type=AuditEventType.TOOL_ACCESS,
                    user_id=identity.user_id if identity else "anonymous",
                    action=func.__name__,
                    resource=resource,
                    domain=domain,
                    status="Success",
                    sensitivity=sensitivity
                )
                return result
            except Exception as e:
                audit_logger.log(
                    event_type=AuditEventType.TOOL_ACCESS,
                    user_id=identity.user_id if identity else "anonymous",
                    action=func.__name__,
                    resource=resource,
                    domain=domain,
                    status="Failure",
                    sensitivity=sensitivity,
                    details={"error": str(e)}
                )
                raise
        return wrapper
    return decorator

def audit_data_access(resource: str, domain: str, sensitivity: SensitivityLevel = SensitivityLevel.CONFIDENTIAL):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            audit_logger = get_audit_logger()
            identity = get_current_identity()
            
            audit_logger.log(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=identity.user_id if identity else "anonymous",
                user_email=identity.email if identity else None,
                action="read",
                resource=resource,
                domain=domain,
                sensitivity=sensitivity,
                details={"access_type": "read", "parameters": dict(kwargs)}
            )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
