"""Telemetry Models for Azure"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TelemetryType(str, Enum):
    TOOL_CALL = "tool_call"
    API_REQUEST = "api_request"
    ERROR = "error"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class StatusType(str, Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"
    TIMEOUT = "Timeout"
    UNAUTHORIZED = "Unauthorized"

class TelemetryContext(BaseModel):
    tool_name: Optional[str] = None
    domain: Optional[str] = None
    requester_identity: Optional[str] = None
    requester_email: Optional[str] = None
    authentication_type: Optional[str] = None
    environment: str = "Dev"
    workspace: Optional[str] = None
    domain_ownership: Optional[str] = None

class TelemetryData(BaseModel):
    timestamp: datetime = datetime.utcnow()
    telemetry_type: TelemetryType
    context: TelemetryContext
    duration_ms: Optional[float] = None
    status: StatusType = StatusType.SUCCESS
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    token_usage: Optional[int] = None
    metadata: Dict[str, Any] = {}
