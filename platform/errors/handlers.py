"""Error Handlers"""
from typing import Optional, Dict, Any, Callable
from .models import ErrorResponse
from .exceptions import MCPException
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self):
        self._error_mappings: Dict[str, type] = {}
        self._custom_handlers: Dict[str, Callable] = {}
    
    def handle_exception(self, exception: Exception) -> ErrorResponse:
        if isinstance(exception, MCPException):
            return self._handle_mcp_exception(exception)
        else:
            return self._handle_generic_exception(exception)
    
    def _handle_mcp_exception(self, exception: MCPException) -> ErrorResponse:
        if exception.error_code in self._custom_handlers:
            try:
                return self._custom_handlers[exception.error_code](exception)
            except Exception as e:
                logger.error(f"Custom error handler failed: {e}")
        
        self._log_error(exception)
        return exception.to_error_response()
    
    def _handle_generic_exception(self, exception: Exception) -> ErrorResponse:
        logger.error(f"Unhandled exception: {exception}\n{traceback.format_exc()}")
        return ErrorResponse(
            error_code="INTERNAL-001",
            category="Internal",
            message="An unexpected error occurred",
            severity="Critical",
            details={"exception_type": type(exception).__name__}
        )
    
    def _log_error(self, exception: MCPException):
        if exception.severity.value == "Critical":
            logger.critical(f"{exception.error_code}: {exception.message}")
        elif exception.severity.value == "Error":
            logger.error(f"{exception.error_code}: {exception.message}")
        elif exception.severity.value == "Warning":
            logger.warning(f"{exception.error_code}: {exception.message}")
        else:
            logger.info(f"{exception.error_code}: {exception.message}")

# Global error handler
_error_handler: Optional[ErrorHandler] = None

def get_error_handler() -> ErrorHandler:
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def handle_exception(exception: Exception) -> ErrorResponse:
    return get_error_handler().handle_exception(exception)
