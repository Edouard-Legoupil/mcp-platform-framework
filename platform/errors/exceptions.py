"""Standardized Exceptions"""
from typing import Optional, Dict, Any
from .models import ErrorCategory, ErrorSeverity
import uuid

class MCPException(Exception):
    def __init__(self, message: str, error_code: str, category: ErrorCategory = ErrorCategory.INTERNAL,
                 severity: ErrorSeverity = ErrorSeverity.ERROR, http_status: int = 400,
                 details: Optional[Dict[str, Any]] = None, retryable: bool = False):
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.http_status = http_status
        self.details = details or {}
        self.retryable = retryable
        self.request_id = str(uuid.uuid4())
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "category": self.category.value,
            "message": self.message,
            "severity": self.severity.value,
            "details": self.details,
            "request_id": self.request_id,
            "retryable": self.retryable
        }
    
    def to_error_response(self) -> "ErrorResponse":
        from .models import ErrorResponse
        return ErrorResponse(
            error_code=self.error_code,
            category=self.category,
            message=self.message,
            severity=self.severity,
            details=self.details,
            request_id=self.request_id
        )

class DataAccessException(MCPException):
    def __init__(self, message: str = "Data access error", error_code: str = "DATA-001",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, ErrorCategory.DATA_ACCESS, details=details)

class AuthenticationException(MCPException):
    def __init__(self, message: str = "Authentication failed", error_code: str = "AUTH-001",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, ErrorCategory.AUTHENTICATION, http_status=401, details=details)

class AuthorizationException(MCPException):
    def __init__(self, message: str = "Authorization failed", error_code: str = "AUTHZ-001",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, ErrorCategory.AUTHORIZATION, http_status=403, details=details)

class ValidationException(MCPException):
    def __init__(self, message: str = "Validation failed", error_code: str = "VAL-001",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, ErrorCategory.VALIDATION, http_status=400, details=details)

class NotFoundException(MCPException):
    def __init__(self, resource_type: str, resource_id: str, error_code: str = "NOTFOUND-001",
                 details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} not found: {resource_id}"
        super().__init__(message, error_code, ErrorCategory.NOT_FOUND, http_status=404,
                        details={"resource_type": resource_type, "resource_id": resource_id, **(details or {})})

class ConflictException(MCPException):
    def __init__(self, message: str = "Conflict occurred", error_code: str = "CONFLICT-001",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, ErrorCategory.CONFLICT, http_status=409, details=details)

class RateLimitException(MCPException):
    def __init__(self, message: str = "Rate limit exceeded", error_code: str = "RATE-001",
                 retry_after: int = 60, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, ErrorCategory.RATE_LIMIT, http_status=429,
                        details={"retry_after": retry_after, **(details or {})}, retryable=True)

class InternalException(MCPException):
    def __init__(self, message: str = "Internal server error", error_code: str = "INTERNAL-001",
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code, ErrorCategory.INTERNAL, ErrorSeverity.CRITICAL, http_status=500, details=details)

class ExternalServiceException(MCPException):
    def __init__(self, service_name: str, message: str = "External service error",
                 error_code: str = "EXT-001", retryable: bool = True,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(f"{service_name} error: {message}", error_code, ErrorCategory.EXTERNAL_SERVICE,
                        details={"service": service_name, **(details or {})}, retryable=retryable)
