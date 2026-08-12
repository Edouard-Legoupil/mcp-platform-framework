# ❌ Error Handling Best Practices

Comprehensive guidelines for effective error handling, error classification, and graceful error recovery in MCP services.

## 🎯 Overview

Effective error handling is crucial for building robust and user-friendly MCP services. This guide provides best practices for:

- **Error Classification**: Standardizing error types and categories
- **Error Messages**: Creating clear, actionable error messages
- **Error Recovery**: Implementing graceful recovery strategies
- **Error Logging**: Proper error logging and monitoring
- **Error Propagation**: Handling errors across service boundaries

## 🏗️ Error Classification Best Practices

### ✅ Use Standard Error Categories

**⭐ Best Practice**: Classify errors into standard categories for consistent handling.

```python
from platform.errors import ErrorCategory

# Good: Standard error categories
class MCPError(Exception):
    def __init__(self, error_code: str, category: ErrorCategory, message: str, **kwargs):
        self.error_code = error_code
        self.category = category
        self.message = message
        self.details = kwargs
        super().__init__(f"[{error_code}] {message}")

# Standard categories
AUTHENTICATION_ERROR = ErrorCategory("Authentication")
AUTHORIZATION_ERROR = ErrorCategory("Authorization")
VALIDATION_ERROR = ErrorCategory("Validation")
DATA_ACCESS_ERROR = ErrorCategory("DataAccess")
EXTERNAL_SERVICE_ERROR = ErrorCategory("ExternalService")
INTERNAL_ERROR = ErrorCategory("Internal")
NOT_FOUND_ERROR = ErrorCategory("NotFound")
```

**❌ Anti-Pattern**: Inconsistent error categories
```python
# Bad: Inconsistent error classification
class MyError(Exception):
    pass  # No standard structure

class AnotherError(Exception):
    def __init__(self, msg):
        self.msg = msg  # Different structure
```

### ✅ Use Meaningful Error Codes

**⭐ Best Practice**: Use descriptive, hierarchical error codes.

```python
# Good: Meaningful error codes
class ErrorCodes:
    # Authentication errors
    AUTH_001 = "InvalidToken"
    AUTH_002 = "TokenExpired"
    AUTH_003 = "InvalidSignature"
    AUTH_004 = "MissingToken"
    
    # Authorization errors
    AUTHZ_001 = "InsufficientPermissions"
    AUTHZ_002 = "RoleRequired"
    AUTHZ_003 = "AccessDenied"
    
    # Validation errors
    VAL_001 = "InvalidInput"
    VAL_002 = "MissingRequiredField"
    VAL_003 = "InvalidFormat"
    VAL_004 = "ValueOutOfRange"
    
    # Data access errors
    DATA_001 = "RecordNotFound"
    DATA_002 = "DatabaseError"
    DATA_003 = "ConnectionFailed"
    
    # External service errors
    EXT_001 = "ExternalServiceUnavailable"
    EXT_002 = "ExternalServiceTimeout"
    EXT_003 = "ExternalServiceError"
```

**❌ Anti-Pattern**: Vague or generic error codes
```python
# Bad: Vague error codes
ERROR_1 = "Error occurred"
ERROR_2 = "Something went wrong"
ERROR_3 = "Failed"
```

### ✅ Create Error Hierarchies

**⭐ Best Practice**: Create hierarchical error classes for better error handling.

```python
from platform.errors import MCPError, ErrorCategory

# Good: Error hierarchy
class AuthenticationError(MCPError):
    def __init__(self, error_code: str, message: str, **kwargs):
        super().__init__(error_code, ErrorCategory.AUTHENTICATION, message, **kwargs)

class AuthorizationError(MCPError):
    def __init__(self, error_code: str, message: str, **kwargs):
        super().__init__(error_code, ErrorCategory.AUTHORIZATION, message, **kwargs)

class ValidationError(MCPError):
    def __init__(self, error_code: str, message: str, field: str = None, **kwargs):
        kwargs["field"] = field
        super().__init__(error_code, ErrorCategory.VALIDATION, message, **kwargs)

class DataAccessError(MCPError):
    def __init__(self, error_code: str, message: str, resource: str = None, **kwargs):
        kwargs["resource"] = resource
        super().__init__(error_code, ErrorCategory.DATA_ACCESS, message, **kwargs)

class ExternalServiceError(MCPError):
    def __init__(self, error_code: str, message: str, service: str = None, **kwargs):
        kwargs["service"] = service
        super().__init__(error_code, ErrorCategory.EXTERNAL_SERVICE, message, **kwargs)
```

## 📝 Error Message Best Practices

### ✅ Create User-Friendly Error Messages

**⭐ Best Practice**: Provide clear, actionable error messages for users.

```python
# Good: User-friendly error messages
def get_error_message(error_code: str, **context) -> str:
    messages = {
        "AUTH_001": "Invalid authentication token. Please log in again.",
        "AUTH_002": "Your session has expired. Please refresh your token.",
        "AUTHZ_001": "You do not have permission to perform this action. Required permission: {permission}",
        "AUTHZ_002": "This action requires the '{role}' role.",
        "VAL_001": "Invalid input: {field} must be {expected_format}.",
        "VAL_002": "Missing required field: {field}.",
        "DATA_001": "Donor with ID '{donor_id}' not found.",
        "EXT_001": "External service '{service}' is currently unavailable. Please try again later."
    }
    
    message = messages.get(error_code, "An unexpected error occurred.")
    return message.format(**context)
```

**❌ Anti-Pattern**: Technical or cryptic error messages
```python
# Bad: Technical error messages
raise Exception("NullReferenceException in DataService.GetDonor()")
raise Exception("SQL Error: Connection timeout after 30000ms")
```

### ✅ Include Context in Error Messages

**⭐ Best Practice**: Include relevant context to help diagnose issues.

```python
# Good: Error with context
class ValidationError(MCPError):
    def __init__(self, field: str, expected: str, actual: Any, **kwargs):
        message = f"Invalid value for '{field}'. Expected {expected}, got {actual}."
        super().__init__(
            error_code="VAL_001",
            category=ErrorCategory.VALIDATION,
            message=message,
            field=field,
            expected=expected,
            actual=actual,
            **kwargs
        )

# Usage
try:
    validate_donor_data(data)
except ValidationError as e:
    logger.error(f"Validation failed: {e.message}")
    logger.error(f"Field: {e.field}, Expected: {e.expected}, Actual: {e.actual}")
    return {"error": e.error_code, "message": e.message, "details": e.details}
```

### ✅ Provide Actionable Error Messages

**⭐ Best Practice**: Tell users what they can do to resolve the error.

```python
# Good: Actionable error messages
def create_error_response(error: MCPError) -> dict:
    actions = {
        "AUTH_001": "Please log in again to get a new authentication token.",
        "AUTH_002": "Please refresh your session token.",
        "AUTHZ_001": "Contact your administrator to request the required permissions.",
        "AUTHZ_002": "Contact your administrator to request the required role.",
        "VAL_001": "Please correct the input and try again.",
        "VAL_002": "Please provide a value for the required field.",
        "DATA_001": "Please verify the ID and try again.",
        "EXT_001": "Please try again later or contact support if the issue persists."
    }
    
    response = {
        "error_code": error.error_code,
        "category": error.category.value,
        "message": error.message,
        "action": actions.get(error.error_code, "Please try again or contact support.")
    }
    
    if error.details:
        response["details"] = error.details
    
    return response
```

## 🛡️ Error Handling Best Practices

### ✅ Use Decorators for Consistent Error Handling

**⭐ Best Practice**: Use the `@handle_errors` decorator for consistent error handling.

```python
from platform.errors import handle_errors

# Good: Consistent error handling with decorator
@handle_errors(
    error_mapping={
        ValueError: "INVALID_INPUT",
        PermissionError: "ACCESS_DENIED",
        TimeoutError: "TIMEOUT",
        ConnectionError: "CONNECTION_FAILED"
    },
    default_error_code="UNKNOWN_ERROR",
    log_exceptions=True,
    include_stack_trace=False  # Don't expose stack traces to users
)
async def get_donor_data(donor_id: str):
    return await donor_service.get_donor(donor_id)
```

### ✅ Handle Errors at the Right Level

**⭐ Best Practice**: Handle errors at the appropriate level of abstraction.

```python
# Good: Multi-level error handling

# Low-level service - handle technical errors
async def get_donor_from_database(donor_id: str):
    try:
        # Database operation
        return await database.query("SELECT * FROM donors WHERE donor_id = @id", {"id": donor_id})
    except DatabaseError as e:
        # Log technical error
        logger.error(f"Database error: {e}")
        # Re-raise as service-specific error
        raise DataAccessError("DATA_002", "Database operation failed", donor_id=donor_id) from e

# Mid-level service - handle business errors
async def get_donor(donor_id: str):
    try:
        donor = await get_donor_from_database(donor_id)
        if not donor:
            raise DataAccessError("DATA_001", "Donor not found", donor_id=donor_id)
        return donor
    except DataAccessError:
        # Re-raise business-level errors
        raise

# High-level API - handle user-facing errors
@handle_errors
async def get_donor_api(donor_id: str):
    try:
        return await get_donor(donor_id)
    except DataAccessError as e:
        # Convert to user-friendly response
        if e.error_code == "DATA_001":
            return {"error": "NOT_FOUND", "message": f"Donor {donor_id} not found"}
        else:
            return {"error": "DATABASE_ERROR", "message": "Unable to access donor data"}
```

### ✅ Use Try-Except Blocks Appropriately

**⭐ Best Practice**: Use try-except blocks for specific error handling, not for flow control.

```python
# Good: Specific error handling
try:
    result = await external_service.call_api(data)
except ExternalServiceTimeout as e:
    logger.warning(f"External service timeout: {e}")
    # Implement retry logic
    return await retry_with_backoff(external_service.call_api, data)
except ExternalServiceError as e:
    logger.error(f"External service error: {e}")
    # Fallback to cached data
    return get_cached_data(data)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise  # Re-raise unexpected errors
```

**❌ Anti-Pattern**: Using exceptions for flow control
```python
# Bad: Using exceptions for flow control
try:
    if not user_has_permission():
        raise PermissionDenied()  # Don't use exceptions for normal flow
    process_request()
except PermissionDenied:
    show_access_denied()

# Good: Use conditional logic instead
if not user_has_permission():
    show_access_denied()
    return
process_request()
```

### ✅ Implement Retry Logic for Transient Errors

**⭐ Best Practice**: Implement retry logic with exponential backoff for transient errors.

```python
import asyncio
from platform.errors import ExternalServiceError

# Good: Retry logic with exponential backoff
async def retry_with_backoff(func, *args, max_retries: int = 3, **kwargs):
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except ExternalServiceError as e:
            if attempt == max_retries - 1:
                raise  # Re-raise on last attempt
            
            # Exponential backoff: 1s, 2s, 4s, etc.
            delay = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
            await asyncio.sleep(delay)
    
    raise ExternalServiceError("EXT_001", "Max retries exceeded")

# Usage
result = await retry_with_backoff(external_service.call_api, data)
```

### ✅ Implement Circuit Breakers

**⭐ Best Practice**: Use circuit breakers to prevent cascading failures.

```python
from platform.resilience import CircuitBreaker

# Good: Circuit breaker pattern
circuit_breaker = CircuitBreaker(
    failure_threshold=5,      # Open circuit after 5 failures
    recovery_timeout=60,      # Try again after 60 seconds
    expected_exception=ExternalServiceError
)

@circuit_breaker.protect
async def call_external_service(data: dict):
    return await external_service.process(data)

# Usage
try:
    result = await call_external_service(data)
except CircuitBreakerOpenError:
    # Circuit is open - use fallback
    logger.warning("Circuit breaker open, using fallback")
    return get_fallback_data(data)
```

## 📊 Error Logging Best Practices

### ✅ Log Errors with Full Context

**⭐ Best Practice**: Log errors with all relevant context for debugging.

```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

# Good: Comprehensive error logging
try:
    result = await process_donor_data(donor_id, data)
except Exception as e:
    telemetry.track_exception(
        exception=e,
        context={
            "donor_id": donor_id,
            "operation": "process_donor_data",
            "data_size": len(data) if data else 0,
            "user": get_caller_identity().username if get_caller_identity() else "unknown"
        },
        severity="Error"
    )
    
    # Also log to application logs
    logger.error(
        f"Error processing donor {donor_id}: {e}",
        extra={
            "donor_id": donor_id,
            "error_code": getattr(e, "error_code", "UNKNOWN"),
            "error_category": getattr(e, "category", "Unknown").value,
            "stack_trace": traceback.format_exc()
        }
    )
    
    raise
```

### ✅ Use Structured Logging

**⭐ Best Practice**: Use structured logging for easier analysis and filtering.

```python
import structlog

# Good: Structured logging
logger = structlog.get_logger()

try:
    result = await donor_service.get_donor(donor_id)
except DataAccessError as e:
    logger.error(
        "Data access error",
        error_code=e.error_code,
        category=e.category.value,
        message=e.message,
        donor_id=donor_id,
        details=e.details,
        timestamp=datetime.utcnow().isoformat()
    )
    raise
```

### ✅ Log at Appropriate Severity Levels

**⭐ Best Practice**: Use appropriate log levels for different types of errors.

```python
# Good: Appropriate log levels

# Debug - Detailed debugging information
logger.debug("Starting donor data processing", donor_id=donor_id)

# Info - Normal operational messages
logger.info("Donor data processed successfully", donor_id=donor_id, duration_ms=duration)

# Warning - Potentially problematic situations
logger.warning("Donor data incomplete", donor_id=donor_id, missing_fields=missing_fields)

# Error - Serious problems that need attention
logger.error("Failed to process donor data", donor_id=donor_id, error=str(e))

# Critical - Critical failures that may cause service outage
logger.critical("Database connection failed", error=str(e), service="donor_service")
```

## 🔄 Error Propagation Best Practices

### ✅ Preserve Error Context During Propagation

**⭐ Best Practice**: Preserve error context when re-raising or wrapping errors.

```python
# Good: Preserve error context
try:
    result = await database.query(query)
except DatabaseError as e:
    # Wrap with service-specific error, preserving original
    raise DataAccessError(
        error_code="DATA_002",
        message="Database query failed",
        query=query,
        original_error=str(e)
    ) from e

# Bad: Losing error context
try:
    result = await database.query(query)
except DatabaseError as e:
    raise DataAccessError("DATA_002", "Database query failed")  # Lost original error
```

### ✅ Use Error Chains for Debugging

**⭐ Best Practice**: Use exception chaining to preserve the full error context.

```python
# Good: Exception chaining
try:
    result = await external_service.call_api(data)
except ExternalServiceTimeout as e:
    raise ServiceUnavailableError(
        error_code="SVC_001",
        message="Service temporarily unavailable",
        service="external_service"
    ) from e  # Preserves the original exception

# When catching, you can access the full chain
try:
    process_request()
except ServiceUnavailableError as e:
    logger.error(f"Service unavailable: {e}")
    logger.error(f"Original error: {e.__cause__}")  # Access the original exception
```

### ✅ Handle Errors at Service Boundaries

**⭐ Best Practice**: Handle errors appropriately at service boundaries.

```python
# Good: Service boundary error handling

# Internal service - let errors propagate
async def get_donor_from_db(donor_id: str):
    # Don't catch errors here - let them propagate
    return await database.query("SELECT * FROM donors WHERE donor_id = @id", {"id": donor_id})

# Public API - handle errors and return appropriate responses
@handle_errors
async def get_donor_api(donor_id: str):
    try:
        donor = await get_donor_from_db(donor_id)
        if not donor:
            raise DataAccessError("DATA_001", "Donor not found", donor_id=donor_id)
        return donor
    except DataAccessError as e:
        # Return appropriate HTTP status codes
        if e.error_code == "DATA_001":
            return {"error": "NOT_FOUND", "message": e.message}, 404
        else:
            return {"error": "DATABASE_ERROR", "message": e.message}, 500
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {e}")
        return {"error": "INTERNAL_ERROR", "message": "An unexpected error occurred"}, 500
```

## 📋 Error Handling Checklist

### ✅ Pre-Deployment Error Handling Checklist

- [ ] All errors are classified into standard categories
- [ ] Error codes are meaningful and hierarchical
- [ ] Error messages are user-friendly and actionable
- [ ] Error handling is implemented at appropriate levels
- [ ] Retry logic is implemented for transient errors
- [ ] Circuit breakers are implemented for external services
- [ ] Errors are logged with full context
- [ ] Structured logging is used for error logging
- [ ] Error propagation preserves context
- [ ] Service boundaries handle errors appropriately

### ✅ Runtime Error Handling Checklist

- [ ] Errors are being caught and handled appropriately
- [ ] Error logs contain sufficient context for debugging
- [ ] Retry logic is working for transient errors
- [ ] Circuit breakers are preventing cascading failures
- [ ] Error responses are user-friendly
- [ ] Error metrics are being tracked
- [ ] Alerts are configured for critical errors

## 🚨 Common Error Handling Pitfalls

### ❌ Swallowing Exceptions

**Problem**: Catching exceptions and not re-raising or logging them.

**Solution**: Always log exceptions and either re-raise or return appropriate error responses.

```python
# Bad: Swallowing exceptions
try:
    process_data()
except Exception as e:
    pass  # Exception is lost!

# Good: Proper exception handling
try:
    process_data()
except Exception as e:
    logger.error(f"Error processing data: {e}")
    raise  # Re-raise or return error response
```

### ❌ Catching Generic Exceptions

**Problem**: Catching `Exception` can hide bugs and make debugging difficult.

**Solution**: Catch specific exceptions and only use generic exception catching at the top level.

```python
# Bad: Catching generic exceptions
try:
    process_data()
except Exception as e:  # Catches everything, including bugs
    logger.error(f"Error: {e}")

# Good: Catch specific exceptions
try:
    process_data()
except ValidationError as e:
    logger.error(f"Validation error: {e}")
except DatabaseError as e:
    logger.error(f"Database error: {e}")
# Let other exceptions propagate
```

### ❌ Exposing Sensitive Information in Errors

**Problem**: Including sensitive data in error messages or responses.

**Solution**: Never include sensitive data in error messages or responses.

```python
# Bad: Exposing sensitive data
try:
    process_payment(credit_card_number)
except Exception as e:
    return {"error": str(e), "credit_card": credit_card_number}  # Security risk!

# Good: Redact sensitive data
try:
    process_payment(credit_card_number)
except Exception as e:
    logger.error(f"Payment processing failed for card ending in {credit_card_number[-4:]}")
    return {"error": "Payment processing failed"}
```

### ❌ Inconsistent Error Responses

**Problem**: Different error formats make it difficult for clients to handle errors.

**Solution**: Use consistent error response formats across all APIs.

```python
# Good: Consistent error response format
def create_error_response(error: MCPError) -> dict:
    return {
        "error": {
            "code": error.error_code,
            "category": error.category.value,
            "message": error.message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": error.details or {}
        }
    }
```

### ❌ No Error Metrics

**Problem**: Without error metrics, you can't track error rates or identify patterns.

**Solution**: Track error metrics for monitoring and alerting.

```python
# Good: Track error metrics
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

try:
    process_request()
except ValidationError as e:
    telemetry.track_metric("ValidationErrors", 1)
    telemetry.track_custom_event("ValidationError", {"error_code": e.error_code})
    raise
except DatabaseError as e:
    telemetry.track_metric("DatabaseErrors", 1)
    telemetry.track_custom_event("DatabaseError", {"error_code": e.error_code})
    raise
```

## 📚 Related Documentation

- [Error Handling Module](../modules/error-handling.md) - Error handling services
- [Telemetry API](../api-reference/telemetry.md) - Telemetry and monitoring
- [Audit API](../api-reference/audit.md) - Audit logging
- [Security Best Practices](security.md) - Security guidelines
- [Monitoring Best Practices](monitoring.md) - Monitoring and observability

---

**🎉 Ready to implement robust error handling?** Use these best practices to build reliable, user-friendly MCP services.

**Need more details?** Check the Error Handling Module documentation for implementation details and advanced patterns.