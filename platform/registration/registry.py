"""Tool Registry"""
from typing import Dict, List, Optional, Any
from .models import ToolMetadata, ToolRegistration, RegistrationRequest, RegistrationResult, ToolStatus
import uuid
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolRegistration] = {}
        self._name_index: Dict[str, str] = {}
        self._domain_index: Dict[str, List[str]] = {}
        self._status_index: Dict[ToolStatus, List[str]] = {}
        self._lock = threading.Lock()
        for status in ToolStatus:
            self._status_index[status] = []
    
    def register_tool(self, request: RegistrationRequest) -> RegistrationResult:
        with self._lock:
            tool_id = str(uuid.uuid4())
            registration = ToolRegistration(
                tool_id=tool_id,
                metadata=request.metadata,
                endpoint=request.endpoint,
                handler=request.handler,
                is_loaded=False
            )
            self._tools[tool_id] = registration
            self._name_index[request.metadata.name] = tool_id
            
            if request.metadata.domain not in self._domain_index:
                self._domain_index[request.metadata.domain] = []
            self._domain_index[request.metadata.domain].append(tool_id)
            self._status_index[ToolStatus.ACTIVE].append(tool_id)
            
            logger.info(f"Registered tool: {request.metadata.name} (ID: {tool_id})")
            return RegistrationResult(success=True, tool_id=tool_id, message="Tool registered successfully")
    
    def get_tool(self, tool_id: str) -> Optional[ToolRegistration]:
        with self._lock:
            return self._tools.get(tool_id)
    
    def get_tool_by_name(self, name: str) -> Optional[ToolRegistration]:
        with self._lock:
            tool_id = self._name_index.get(name)
            return self._tools.get(tool_id) if tool_id else None
    
    def get_tools_by_domain(self, domain: str) -> List[ToolRegistration]:
        with self._lock:
            tool_ids = self._domain_index.get(domain, [])
            return [self._tools[tool_id] for tool_id in tool_ids if tool_id in self._tools]
    
    def get_all_tools(self) -> List[ToolRegistration]:
        with self._lock:
            return list(self._tools.values())
    
    def unregister_tool(self, tool_id: str) -> bool:
        with self._lock:
            if tool_id not in self._tools:
                return False
            registration = self._tools[tool_id]
            if registration.metadata.name in self._name_index:
                del self._name_index[registration.metadata.name]
            if registration.metadata.domain in self._domain_index:
                if tool_id in self._domain_index[registration.metadata.domain]:
                    self._domain_index[registration.metadata.domain].remove(tool_id)
            if registration.metadata.status in self._status_index:
                if tool_id in self._status_index[registration.metadata.status]:
                    self._status_index[registration.metadata.status].remove(tool_id)
            del self._tools[tool_id]
            return True
    
    def update_tool_status(self, tool_id: str, status: ToolStatus) -> bool:
        with self._lock:
            if tool_id not in self._tools:
                return False
            registration = self._tools[tool_id]
            old_status = registration.metadata.status
            registration.metadata.status = status
            registration.metadata.updated_at = datetime.utcnow()
            if tool_id in self._status_index[old_status]:
                self._status_index[old_status].remove(tool_id)
            self._status_index[status].append(tool_id)
            return True
    
    def increment_usage(self, tool_id: str, success: bool = True):
        with self._lock:
            if tool_id not in self._tools:
                return
            registration = self._tools[tool_id]
            registration.metadata.usage_count += 1
            registration.metadata.last_used_at = datetime.utcnow()
            if not success:
                registration.metadata.error_count += 1

# Global registry
_registry: Optional[ToolRegistry] = None

def set_tool_registry(registry: ToolRegistry):
    global _registry
    _registry = registry

def get_tool_registry() -> ToolRegistry:
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
