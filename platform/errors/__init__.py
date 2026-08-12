"""Error Handling Module"""
from .models import ErrorCategory, ErrorSeverity, ErrorResponse
from .exceptions import (
    MCPException, DataAccessException, AuthenticationException,
    AuthorizationException, ValidationException, NotFoundException,
    ConflictException, RateLimitException, InternalException, ExternalServiceException
)
from .handlers import ErrorHandler, get_error_handler, handle_exception

__all__ = [
    'ErrorCategory', 'ErrorSeverity', 'ErrorResponse',
    'MCPException', 'DataAccessException', 'AuthenticationException',
    'AuthorizationException', 'ValidationException', 'NotFoundException',
    'ConflictException', 'RateLimitException', 'InternalException', 'ExternalServiceException',
    'ErrorHandler', 'get_error_handler', 'handle_exception'
]
