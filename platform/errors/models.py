"""Error Models"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class ErrorCategory(str, Enum):
    DATA_ACCESS = "DataAccess"
    AUTHENTICATION = "Authentication"
    AUTHORIZATION = "Authorization"
    VALIDATION = "Validation"
    NOT_FOUND = "NotFound"
    CONFLICT = "Conflict"
    INTERNAL = "Internal"
    RATE_LIMIT = "RateLimit"
    EXTERNAL_SERVICE = "ExternalService"

class ErrorSeverity(str, Enum):
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"
    CRITICAL = "Critical"

class ErrorResponse(BaseModel):
    error_code: str
    category: ErrorCategory
    message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    request_id: Optional[str] = None
