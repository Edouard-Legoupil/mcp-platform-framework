"""Audit Logger for Azure Blob Storage"""
from typing import Dict, List, Optional, Any, Callable
from .models import AuditRecord, AuditEventType, SensitivityLevel
import uuid
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditLogger:
    def __init__(self):
        self._storage_backends: List = []
        self._lock = threading.Lock()
        self._enabled = True
    
    def add_storage_backend(self, backend):
        self._storage_backends.append(backend)
    
    def log(self, event_type: AuditEventType, user_id: str, action: str, resource: str,
            domain: str, status: str = "Success", sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL,
            details: Dict[str, Any] = None, user_email: Optional[str] = None,
            ip_address: Optional[str] = None, user_agent: Optional[str] = None,
            session_id: Optional[str] = None) -> Optional[AuditRecord]:
        if not self._enabled:
            return None
        
        record = AuditRecord(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_type,
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource=resource,
            domain=domain,
            status=status,
            sensitivity=sensitivity,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        
        self._store_record(record)
        return record
    
    def _store_record(self, record: AuditRecord):
        if not self._storage_backends:
            logger.warning("No audit storage backends configured")
            return
        for backend in self._storage_backends:
            try:
                backend.store(record)
            except Exception as e:
                logger.error(f"Failed to store audit record: {e}")
    
    def enable(self):
        self._enabled = True
    
    def disable(self):
        self._enabled = False

# Global audit logger
_audit_logger: Optional[AuditLogger] = None

def set_audit_logger(logger: AuditLogger):
    global _audit_logger
    _audit_logger = logger

def get_audit_logger() -> AuditLogger:
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
        _audit_logger.add_storage_backend(InMemoryAuditStorage())
    return _audit_logger
