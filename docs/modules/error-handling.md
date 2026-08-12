# ❌ Error Handling Module

The Error Handling Module provides standardized error structures, error codes, and exception handling for the MCP Platform Framework, ensuring consistent error handling across all domains.

## 🎯 Overview

The Error Handling Module handles:
- **Standardized Error Codes**: Domain-specific prefixes (DONOR-001, FINANCE-002, etc.)
- **Error Categories**: Consistent categorization (DataAccess, Validation, Authorization, etc.)
- **Error Structures**: JSON-based error format for API responses
- **Exception Handling**: Automatic error classification and context enrichment
- **Operational Diagnostics**: Error chaining, stack traces, and debugging information

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Error Handling Module            │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Error Codes     │  │ Error          │ │
│  │ & Categories    │  │ Structures     │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Exception       │  │ Operational     │ │
│  │ Handling        │  │ Diagnostics     │ │
│  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Basic Usage

```python
from platform.errors import MCPError, ErrorCategory

# Raising a standardized error
if not has_permission("donor.read"):
    raise MCPError(
        error_code="DONOR-001",
        category=ErrorCategory.AUTHORIZATION,
        message="Access denied to donor data",
        details={"required_permission": "donor.read"}
    )
```

### Configuration

```python
# config/errors.py
from platform.errors.config import ErrorConfig

ERROR_CONFIG = ErrorConfig(
    # Error code prefixes for domains
    domain_prefixes={
        "donor": "DONOR",
        "finance": "FINANCE",
        "supply": "SUPPLY",
        "system": "SYS"
    },
    
    # Error categories
    categories={
        "DataAccess": "Data access errors",
        "Validation": "Input validation errors",
        "Authorization": "Permission or access errors",
        "Authentication": "Identity verification errors",
        "Configuration": "Configuration-related errors",
        "Integration": "External system integration errors",
        "Internal": "Internal errors"
    },
    
    # Error severity levels
    severity_levels={
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3,
        "CRITICAL": 4
    },
    
    # Error reporting
    report_errors=True,
    error_reporting_endpoint="https://errors.my-org.org/api/report"
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Error Configuration
ERROR_DOMAIN_PREFIXES=donor:DONOR,finance:FINANCE,supply:SUPPLY
ERROR_REPORTING_ENABLED=true
ERROR_REPORTING_ENDPOINT=https://errors.my-org.org/api/report

# Error Logging
ERROR_LOG_LEVEL=ERROR
ERROR_LOG_INCLUDE_STACK_TRACE=true
```

### Configuration File

```yaml
# config/errors.yaml
errors:
  domain_prefixes:
    donor: DONOR
    finance: FINANCE
    supply: SUPPLY
    system: SYS
    
  categories:
    DataAccess: "Data access errors"
    Validation: "Input validation errors"
    Authorization: "Permission or access errors"
    Authentication: "Identity verification errors"
    Configuration: "Configuration-related errors"
    Integration: "External system integration errors"
    Internal: "Internal errors"
    
  severity_levels:
    DEBUG: 0
    INFO: 1
    WARNING: 2
    ERROR: 3
    CRITICAL: 4
    
  reporting:
    enabled: true
    endpoint: ${ERROR_REPORTING_ENDPOINT}
    include_stack_trace: true
    include_context: true
    
  logging:
    level: ERROR
    include_stack_trace: true
    include_details: true
```

## 🎯 API Reference

### Decorators

#### `@handle_errors`

Automatically handles errors in a function and converts them to standardized MCP errors.

```python
from platform.errors import handle_errors

@handle_errors
def get_donor(donor_id: str):
    # Errors will be automatically converted to MCPError
    return donor_service.get(donor_id)

# With custom error mapping
@handle_errors(
    error_mapping={
        ValueError: ("DONOR-002", ErrorCategory.VALIDATION, "Invalid donor ID"),
        KeyError: ("DONOR-003", ErrorCategory.DATA_ACCESS, "Donor not found")
    }
)
def get_donor(donor_id: str):
    pass
```

**Parameters:**
- `error_mapping` (dict, optional): Mapping of exception types to (error_code, category, message)
- `include_stack_trace` (bool, optional): Include stack trace in error details
- `log_errors` (bool, optional): Log errors automatically

#### `@validate_input`

Validates input parameters and raises standardized validation errors.

```python
from platform.errors import validate_input

@validate_input({
    "donor_id": {"type": str, "required": True, "min_length": 1},
    "year": {"type": int, "min": 2020, "max": 2030}
})
def get_donor_report(donor_id: str, year: int):
    # Input is validated before function execution
    return report_service.get_report(donor_id, year)
```

**Parameters:**
- `schema` (dict): Validation schema for parameters
- `error_code` (str, optional): Error code for validation failures
- `category` (ErrorCategory, optional): Error category for validation failures

### Classes

#### `MCPError`

The base exception class for MCP errors.

```python
from platform.errors import MCPError, ErrorCategory

# Create an MCP error
try:
    raise MCPError(
        error_code="DONOR-001",
        category=ErrorCategory.AUTHORIZATION,
        message="Access denied to donor data",
        details={"required_permission": "donor.read"},
        severity="ERROR",
        http_status=403
    )
except MCPError as e:
    print(f"Error {e.error_code}: {e.message}")
    print(f"Category: {e.category}")
    print(f"Details: {e.details}")
    print(f"HTTP Status: {e.http_status}")
```

**Parameters:**
- `error_code` (str): Error code (e.g., "DONOR-001")
- `category` (ErrorCategory): Error category
- `message` (str): Human-readable error message
- `details` (dict, optional): Additional error details
- `severity` (str, optional): Severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `http_status` (int, optional): HTTP status code
- `cause` (Exception, optional): Original exception that caused this error
- `stack_trace` (str, optional): Stack trace

**Attributes:**
- `error_code` (str): Error code
- `category` (ErrorCategory): Error category
- `message` (str): Error message
- `details` (dict): Error details
- `severity` (str): Severity level
- `http_status` (int): HTTP status code
- `timestamp` (datetime): When the error occurred
- `request_id` (str): Request ID
- `correlation_id` (str): Correlation ID
- `cause` (Exception): Original exception
- `stack_trace` (str): Stack trace

**Methods:**
- `to_dict()`: Convert to dictionary
- `to_json()`: Convert to JSON string
- `from_exception(exception)`: Create MCPError from a regular exception

#### `ErrorCategory`

Error categories for classification.

```python
from platform.errors import ErrorCategory

# Available categories
categories = [
    ErrorCategory.DATA_ACCESS,
    ErrorCategory.VALIDATION,
    ErrorCategory.AUTHORIZATION,
    ErrorCategory.AUTHENTICATION,
    ErrorCategory.CONFIGURATION,
    ErrorCategory.INTEGRATION,
    ErrorCategory.INTERNAL
]

# Check category
if error.category == ErrorCategory.AUTHORIZATION:
    # Handle authorization error
    pass
```

**Values:**
- `DATA_ACCESS`: Database or storage access errors
- `VALIDATION`: Input validation errors
- `AUTHORIZATION`: Permission or access errors
- `AUTHENTICATION`: Identity verification errors
- `CONFIGURATION`: Configuration-related errors
- `INTEGRATION`: External system integration errors
- `INTERNAL`: Internal errors

#### `ErrorHandler`

Handles errors and converts them to standardized responses.

```python
from platform.errors import ErrorHandler

# Create error handler
handler = ErrorHandler(
    include_stack_trace=True,
    log_errors=True,
    report_errors=True
)

# Handle an exception
response = handler.handle_exception(
    exception=ValueError("Invalid donor ID"),
    request_id="req-001",
    correlation_id="corr-001"
)

# Handle an MCPError
response = handler.handle_mcp_error(
    error=MCPError(
        error_code="DONOR-001",
        category=ErrorCategory.AUTHORIZATION,
        message="Access denied"
    ),
    request_id="req-001"
)
```

**Parameters:**
- `include_stack_trace` (bool, optional): Include stack trace in responses
- `log_errors` (bool, optional): Log errors to logging system
- `report_errors` (bool, optional): Report errors to error reporting service
- `error_mapping` (dict, optional): Custom error mapping

**Methods:**
- `handle_exception(exception, **kwargs)`: Handle a regular exception
- `handle_mcp_error(error, **kwargs)`: Handle an MCPError
- `convert_to_mcp_error(exception, **kwargs)`: Convert exception to MCPError
- `get_error_response(error, **kwargs)`: Get standardized error response

#### `ErrorReporter`

Reports errors to an error reporting service.

```python
from platform.errors import ErrorReporter

# Create error reporter
reporter = ErrorReporter(
    endpoint="https://errors.my-org.org/api/report",
    api_key="your-api-key",
    batch_enabled=True,
    batch_size=100
)

# Report an error
reporter.report(
    error=MCPError(
        error_code="DONOR-001",
        category=ErrorCategory.AUTHORIZATION,
        message="Access denied"
    ),
    context={
        "user": "john.doe@my-org.org",
        "tool": "GetDonorData",
        "environment": "Production"
    }
)

# Flush pending reports
reporter.flush()
```

**Parameters:**
- `endpoint` (str): Error reporting endpoint
- `api_key` (str): API key for authentication
- `batch_enabled` (bool, optional): Enable batch reporting
- `batch_size` (int, optional): Batch size
- `batch_interval` (int, optional): Batch interval in seconds

**Methods:**
- `report(error, context)`: Report an error
- `report_exception(exception, context)`: Report an exception
- `flush()`: Flush pending reports
- `close()`: Close the reporter

## 📊 Error Structure

### Standard Error Format

```json
{
  "error_code": "DONOR-001",
  "category": "Authorization",
  "message": "Access denied to donor data",
  "details": {
    "required_permission": "donor.read",
    "user": "john.doe@my-org.org",
    "resource": "donor:DON-12345"
  },
  "timestamp": "2026-05-01T10:30:00Z",
  "severity": "ERROR",
  "request_id": "req-20260501-103000-001",
  "correlation_id": "corr-20260501-100000-001",
  "http_status": 403
}
```

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": "DONOR-001",
    "message": "Access denied to donor data",
    "type": "authorization",
    "category": "Authorization",
    "details": {
      "required_permission": "donor.read"
    },
    "timestamp": "2026-05-01T10:30:00Z",
    "request_id": "req-20260501-103000-001",
    "correlation_id": "corr-20260501-100000-001"
  }
}
```

## 📈 Monitoring and Metrics

### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Error Rate | Percentage of failed requests | < 1% | > 5% |
| Errors by Category | Errors grouped by category | Varies | > 10/hour for any category |
| Errors by Code | Errors grouped by error code | Varies | > 5/hour for any code |
| Error Severity | Errors grouped by severity | Varies | > 1 CRITICAL/hour |
| Error Response Time | Time to return error responses | < 100ms | > 500ms |

### Error Queries

```kusto
// Get error rate by tool
requests
| where cloud_RoleName == "mcp-platform"
| where success == false
| summarize count() by name
| order by count_ desc

// Get errors by category
exceptions
| where cloud_RoleName == "mcp-platform"
| extend category = tostring(customDimensions.category)
| summarize count() by category
| order by count_ desc

// Get errors by code
exceptions
| where cloud_RoleName == "mcp-platform"
| extend error_code = tostring(customDimensions.error_code)
| summarize count() by error_code
| order by count_ desc

// Get most frequent errors
exceptions
| where cloud_RoleName == "mcp-platform"
| summarize count() by type, message
| order by count_ desc
| take 10
```

## 🚀 Best Practices

### ⭐ Use Standardized Error Codes

Always use standardized error codes with domain prefixes.

```python
# Good - Standardized error codes
raise MCPError(
    error_code="DONOR-001",
    category=ErrorCategory.AUTHORIZATION,
    message="Access denied"
)

# Bad - Generic error codes
raise MCPError(
    error_code="ERROR-001",
    category=ErrorCategory.INTERNAL,
    message="Something went wrong"
)
```

### ⭐ Use Appropriate Error Categories

Use the most specific error category that applies.

```python
# Good - Specific category
raise MCPError(
    error_code="DONOR-001",
    category=ErrorCategory.AUTHORIZATION,  # Specific
    message="Access denied"
)

# Bad - Generic category
raise MCPError(
    error_code="DONOR-001",
    category=ErrorCategory.INTERNAL,  # Too generic
    message="Access denied"
)
```

### ⭐ Include Useful Details

Include relevant details to help with debugging.

```python
# Good - Useful details
raise MCPError(
    error_code="DONOR-001",
    category=ErrorCategory.AUTHORIZATION,
    message="Access denied to donor data",
    details={
        "required_permission": "donor.read",
        "user": "john.doe@my-org.org",
        "resource": "donor:DON-12345"
    }
)

# Bad - No details
raise MCPError(
    error_code="DONOR-001",
    category=ErrorCategory.AUTHORIZATION,
    message="Access denied"
)
```

### ⭐ Use Error Decorators

Use the `@handle_errors` decorator for consistent error handling.

```python
# Good - Using decorator
@handle_errors
def get_donor(donor_id: str):
    # Errors automatically converted to MCPError
    return donor_service.get(donor_id)

# Bad - Manual error handling
@tool
def get_donor(donor_id: str):
    try:
        return donor_service.get(donor_id)
    except Exception as e:
        # Manual conversion
        raise MCPError.from_exception(e)
```

### ⭐ Validate Inputs

Validate inputs and raise appropriate validation errors.

```python
# Good - Input validation
@validate_input({
    "donor_id": {"type": str, "required": True, "min_length": 1}
})
def get_donor(donor_id: str):
    pass

# Bad - No input validation
def get_donor(donor_id: str):
    # No validation
    pass
```

### ⭐ Include Context in Errors

Include request context in error responses.

```python
# Good - Context included
handler = ErrorHandler(include_context=True)
response = handler.handle_exception(
    exception=ValueError("Invalid donor ID"),
    request_id="req-001",
    correlation_id="corr-001",
    user="john.doe@my-org.org",
    tool="GetDonorData"
)

# Bad - No context
response = handler.handle_exception(
    exception=ValueError("Invalid donor ID")
)
```

### ⭐ Log Errors Appropriately

Log errors with appropriate severity levels.

```python
# Good - Appropriate logging
import logging

logger = logging.getLogger(__name__)

try:
    # Some operation
    pass
except MCPError as e:
    if e.severity == "CRITICAL":
        logger.critical(f"Critical error: {e}")
    elif e.severity == "ERROR":
        logger.error(f"Error: {e}")
    elif e.severity == "WARNING":
        logger.warning(f"Warning: {e}")
    else:
        logger.info(f"Info: {e}")
    raise

# Bad - No severity-based logging
try:
    # Some operation
    pass
except Exception as e:
    logger.error(f"Error: {e}")  # Always logs as error
    raise
```

## 🔍 Troubleshooting

### Common Issues

#### Generic Error Messages

**Symptoms:** Users see generic error messages like "Internal server error"

**Causes:**
- Errors not being converted to MCPError
- Error details not being included
- Error messages too generic

**Solutions:**
1. Use `@handle_errors` decorator
2. Include specific error messages
3. Add error details
4. Use appropriate error categories

```python
# Debug error handling
from platform.errors import handle_errors, MCPError

@handle_errors
@tool
def get_donor(donor_id: str):
    # This will automatically convert errors
    return donor_service.get(donor_id)

# Test error handling
try:
    get_donor("invalid-id")
except MCPError as e:
    print(f"Error code: {e.error_code}")
    print(f"Category: {e.category}")
    print(f"Message: {e.message}")
    print(f"Details: {e.details}")
```

#### Missing Error Details

**Symptoms:** Error responses missing useful debugging information

**Causes:**
- `include_details` not set to True
- Error details not being populated
- Stack traces not included

**Solutions:**
1. Set `include_details=True` in configuration
2. Populate error details when creating errors
3. Include stack traces for debugging

```python
# Include details in errors
config = ErrorConfig(
    include_details=True,
    include_stack_trace=True
)

# Create error with details
raise MCPError(
    error_code="DONOR-001",
    category=ErrorCategory.AUTHORIZATION,
    message="Access denied",
    details={
        "required_permission": "donor.read",
        "user": "john.doe@my-org.org",
        "resource": "donor:DON-12345"
    },
    include_stack_trace=True
)
```

#### Error Reporting Not Working

**Symptoms:** Errors not appearing in error reporting system

**Causes:**
- Error reporting endpoint incorrect
- API key invalid
- Network connectivity issues
- Batch processing not flushing

**Solutions:**
1. Check endpoint: `ERROR_REPORTING_ENDPOINT`
2. Verify API key
3. Check network connectivity
4. Flush pending reports

```python
# Debug error reporting
from platform.errors import ErrorReporter

reporter = ErrorReporter(
    endpoint="https://errors.my-org.org/api/report",
    api_key="your-api-key"
)

# Test reporting
try:
    reporter.report(
        error=MCPError(
            error_code="TEST-001",
            category=ErrorCategory.INTERNAL,
            message="Test error"
        ),
        context={"test": True}
    )
    reporter.flush()
    print("Error reporting test successful")
except Exception as e:
    print(f"Error reporting test failed: {e}")
```

## 📚 Examples

### Complete Error Handling Example

```python
from platform.auth import authenticated_tool, requires_permission
from platform.errors import handle_errors, validate_input, MCPError, ErrorCategory

@authenticated_tool
@requires_permission("donor.read")
@handle_errors(
    error_mapping={
        ValueError: ("DONOR-002", ErrorCategory.VALIDATION, "Invalid donor ID format"),
        KeyError: ("DONOR-003", ErrorCategory.DATA_ACCESS, "Donor not found")
    }
)
@validate_input({
    "donor_id": {"type": str, "required": True, "min_length": 1, "max_length": 50}
})
def get_donor(donor_id: str):
    """Get donor information with comprehensive error handling"""
    
    # Get caller information
    caller = get_caller_identity()
    
    try:
        # Get donor data
        donor = await donor_service.get(donor_id)
        
        if not donor:
            raise MCPError(
                error_code="DONOR-003",
                category=ErrorCategory.DATA_ACCESS,
                message=f"Donor not found: {donor_id}",
                details={"donor_id": donor_id}
            )
        
        return donor
        
    except ValueError as e:
        # Re-raise with additional context
        raise MCPError(
            error_code="DONOR-002",
            category=ErrorCategory.VALIDATION,
            message=f"Invalid donor ID: {str(e)}",
            details={"donor_id": donor_id, "error": str(e)}
        )
```

### Custom Error Mapping

```python
from platform.errors import handle_errors, MCPError, ErrorCategory

# Define custom error mapping
CUSTOM_ERROR_MAPPING = {
    ValueError: ("VALIDATION-001", ErrorCategory.VALIDATION, "Invalid input value"),
    TypeError: ("VALIDATION-002", ErrorCategory.VALIDATION, "Invalid input type"),
    KeyError: ("DATA-001", ErrorCategory.DATA_ACCESS, "Resource not found"),
    ConnectionError: ("INTEGRATION-001", ErrorCategory.INTEGRATION, "Connection failed"),
    TimeoutError: ("INTEGRATION-002", ErrorCategory.INTEGRATION, "Request timeout"),
    PermissionError: ("AUTHZ-001", ErrorCategory.AUTHORIZATION, "Permission denied"),
    Exception: ("INTERNAL-001", ErrorCategory.INTERNAL, "Internal server error")
}

@handle_errors(error_mapping=CUSTOM_ERROR_MAPPING)
def process_donor_data(donor_id: str):
    """Process donor data with custom error mapping"""
    # Any exception will be converted using the custom mapping
    return donor_service.process(donor_id)
```

### Error Response Formatting

```python
from platform.errors import ErrorHandler, MCPError, ErrorCategory

# Create error handler
handler = ErrorHandler(
    include_stack_trace=True,
    include_context=True
)

# Handle different types of errors
def handle_request(request):
    try:
        # Process request
        return process_request(request)
    except MCPError as e:
        # Format MCPError response
        return handler.get_error_response(
            error=e,
            request_id=request.request_id,
            correlation_id=request.correlation_id
        )
    except ValueError as e:
        # Convert ValueError to MCPError
        mcp_error = handler.convert_to_mcp_error(
            exception=e,
            error_code="VALIDATION-001",
            category=ErrorCategory.VALIDATION,
            request_id=request.request_id
        )
        return handler.get_error_response(
            error=mcp_error,
            request_id=request.request_id
        )
    except Exception as e:
        # Handle unexpected errors
        mcp_error = handler.convert_to_mcp_error(
            exception=e,
            error_code="INTERNAL-001",
            category=ErrorCategory.INTERNAL,
            request_id=request.request_id
        )
        return handler.get_error_response(
            error=mcp_error,
            request_id=request.request_id
        )
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `MCPError` | Base MCP error | Varies |
| `ValidationError` | Input validation error | VALIDATION-001 |
| `AuthorizationError` | Authorization error | AUTHZ-001 |
| `AuthenticationError` | Authentication error | AUTH-001 |
| `DataAccessError` | Data access error | DATA-001 |
| `ConfigurationError` | Configuration error | CONFIG-001 |
| `IntegrationError` | Integration error | INTEGRATION-001 |

### Error Codes by Domain

| Domain | Code Range | Description |
|--------|-----------|-------------|
| Donor | DONOR-001 to DONOR-999 | Donor domain errors |
| Finance | FINANCE-001 to FINANCE-999 | Finance domain errors |
| Supply | SUPPLY-001 to SUPPLY-999 | Supply domain errors |
| System | SYS-001 to SYS-999 | System errors |

### HTTP Status Codes

| Error Category | HTTP Status |
|----------------|-------------|
| Validation | 400 |
| Authentication | 401 |
| Authorization | 403 |
| DataAccess | 404 |
| Configuration | 400 |
| Integration | 502 |
| Internal | 500 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*