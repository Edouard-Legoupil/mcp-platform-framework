"""Telemetry Decorators"""
from functools import wraps
from typing import Callable, Any, Optional
from .collector import get_telemetry_collector
from .models import TelemetryContext
import time
import logging

logger = logging.getLogger(__name__)

def track_tool_telemetry(tool_name: Optional[str] = None, domain: Optional[str] = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            collector = get_telemetry_collector()
            actual_tool_name = tool_name or func.__name__
            
            from platform.auth import get_current_identity
            identity = get_current_identity()
            
            context = TelemetryContext(
                tool_name=actual_tool_name,
                domain=domain or "",
                requester_identity=identity.user_id if identity else None,
                requester_email=identity.email if identity else None,
                authentication_type=identity.authentication_type if identity else None
            )
            
            with collector.track_tool_execution(
                tool_name=actual_tool_name,
                domain=domain or "",
                requester_identity=context.requester_identity,
                requester_email=context.requester_email,
                authentication_type=context.authentication_type
            ):
                return func(*args, **kwargs)
        return wrapper
    return decorator
