"""Audit Models"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class AuditEventType(str, Enum):
    TOOL_ACCESS = "tool_access"
    DATA_ACCESS = "data_access"
    ADMIN_ACTION = "admin_action"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"

class SensitivityLevel(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    STRICTLY_CONFIDENTIAL = "STRICTLY_CONFIDENTIAL"

class AuditRecord(BaseModel):
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    user_id: str
    user_email: Optional[str] = None
    action: str
    resource: str
    domain: str
    status: str
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
