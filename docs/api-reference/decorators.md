# 🎪 Decorators API Reference

The Decorators API provides a comprehensive set of decorators for the MCP Platform Framework, enabling developers to easily add cross-cutting concerns like authentication, authorization, telemetry, audit logging, and data classification to their tools with minimal code.

## 🎯 Overview

The MCP Platform Framework provides a rich set of decorators that handle:

- **Authentication**: Ensure tools are accessed by authenticated users
- **Authorization**: Enforce permission and role requirements
- **Telemetry**: Automatically track tool execution and performance
- **Audit Logging**: Automatically log sensitive data access
- **Data Classification**: Enforce data classification requirements
- **Error Handling**: Standardize error handling and reporting
- **Tool Registration**: Register tools with the MCP framework

## 🏗️ Decorator Categories

### Authentication Decorators

#### `@authenticated_tool`
Ensure a tool requires authentication.

**Signature:**
```python
def authenticated_tool(
    func: Optional[Callable] = None,
    *,
    allow_anonymous: bool = False,
    required_claims: Optional[List[str]] = None,
    validate_token: bool = True
) -> Callable:
```

**Parameters:**
- `func`: Function to decorate
- `allow_anonymous`: If True, allow unauthenticated access (default: False)
- `required_claims`: List of claims that must be present in the token
- `validate_token`: Whether to validate the token (default: True)

**Example:**
```python
from platform.auth import authenticated_tool

# Basic usage - requires authentication
@authenticated_tool
def get_donor_data(donor_id: str):
    caller = get_caller_identity()
    return donor_service.get_donor(donor_id)

# Allow anonymous access
@authenticated_tool(allow_anonymous=True)
def get_public_info():
    return public_service.get_info()

# Require specific claims
@authenticated_tool(required_claims=["email", "name"])
def get_user_profile():
    caller = get_caller_identity()
    return user_service.get_profile(caller.username)
```

### Authorization Decorators

#### `@requires_permission()`
Ensure a tool requires specific permissions.

**Signature:**
```python
def requires_permission(
    *permissions: str,
    any_permission: bool = False
) -> Callable:
```

**Parameters:**
- `*permissions`: List of required permissions
- `any_permission`: If True, caller needs any of the permissions (AND logic by default)

**Example:**
```python
from platform.authorization import requires_permission

# Require single permission
@requires_permission("donor.read")
def get_donor_data(donor_id: str):
    return donor_service.get_donor(donor_id)

# Require multiple permissions (AND logic)
@requires_permission("donor.read", "donor.analytics")
def get_donor_analytics(donor_id: str):
    return analytics_service.get_analytics(donor_id)

# Require any of multiple permissions (OR logic)
@requires_permission("donor.read", "donor.write", any_permission=True)
def get_or_create_donor(donor_id: str):
    return donor_service.get_or_create(donor_id)
```

#### `@requires_role()`
Ensure a tool requires specific roles.

**Signature:**
```python
def requires_role(
    *roles: str,
    any_role: bool = False
) -> Callable:
```

**Parameters:**
- `*roles`: List of required roles
- `any_role`: If True, caller needs any of the roles (AND logic by default)

**Example:**
```python
from platform.authorization import requires_role

# Require single role
@requires_role("donor_analyst")
def get_donor_analytics():
    return analytics_service.get_analytics()

# Require multiple roles (AND logic)
@requires_role("donor_analyst", "finance_viewer")
def get_financial_analytics():
    return analytics_service.get_financial_analytics()

# Require any of multiple roles (OR logic)
@requires_role("admin", "super_admin", any_role=True)
def admin_operation():
    return admin_service.perform_operation()
```

### Telemetry Decorators

#### `@track_tool_telemetry`
Automatically track tool execution telemetry.

**Signature:**
```python
def track_tool_telemetry(
    func: Optional[Callable] = None,
    *,
    track_arguments: bool = True,
    track_result: bool = False,
    include_classification: bool = True,
    include_caller: bool = True,
    include_duration: bool = True
) -> Callable:
```

**Parameters:**
- `func`: Function to decorate
- `track_arguments`: Whether to track function arguments (default: True)
- `track_result`: Whether to track function result (default: False)
- `include_classification`: Whether to include classification in metadata (default: True)
- `include_caller`: Whether to include caller identity (default: True)
- `include_duration`: Whether to include execution duration (default: True)

**Example:**
```python
from platform.telemetry import track_tool_telemetry

# Basic usage - automatic telemetry
@track_tool_telemetry
def get_donor_portfolio(donor_id: str):
    return donor_service.get_portfolio(donor_id)

# Customize tracking
@track_tool_telemetry(
    track_arguments=False,  # Don't track arguments
    track_result=True,      # Track result
    include_classification=True
)
def get_donor_summary(donor_id: str):
    return donor_service.get_summary(donor_id)
```

#### `@telemetry_context()`
Add custom telemetry context to a function.

**Signature:**
```python
def telemetry_context(
    **context_kwargs: Any
) -> Callable:
```

**Parameters:**
- `**context_kwargs`: Context key-value pairs to add to all telemetry from this function

**Example:**
```python
from platform.telemetry import telemetry_context

# Add custom context
@telemetry_context(domain="DonorManagement", service="Analytics")
def get_donor_analytics():
    # All telemetry from this function includes custom context
    return analytics_service.get_analytics()

# Multiple context values
@telemetry_context(
    domain="DonorManagement",
    service="Analytics",
    environment="production",
    version="1.0.0"
)
def get_donor_portfolio():
    return portfolio_service.get_portfolio()
```

### Audit Logging Decorators

#### `@audit_tool_access`
Automatically log access to a tool.

**Signature:**
```python
def audit_tool_access(
    func: Optional[Callable] = None,
    *,
    classification: Optional[str] = None,
    log_arguments: bool = False,
    sensitive_fields: Optional[List[str]] = None,
    include_caller: bool = True,
    include_metadata: bool = True
) -> Callable:
```

**Parameters:**
- `func`: Function to decorate
- `classification`: Tool classification level (default: None)
- `log_arguments`: Whether to log function arguments (default: False)
- `sensitive_fields`: Fields to redact from arguments
- `include_caller`: Whether to include caller identity (default: True)
- `include_metadata`: Whether to include additional metadata (default: True)

**Example:**
```python
from platform.audit import audit_tool_access

# Basic usage - automatic audit logging
@audit_tool_access(classification="CONFIDENTIAL")
def get_donor_portfolio(donor_id: str):
    return donor_service.get_portfolio(donor_id)

# Customize audit logging
@audit_tool_access(
    classification="STRICTLY_CONFIDENTIAL",
    log_arguments=False,  # Don't log arguments
    sensitive_fields=["ssn", "credit_card", "password"]
)
def get_sensitive_donor_data(donor_id: str):
    return donor_service.get_sensitive_data(donor_id)
```

#### `@audit_data_access()`
Automatically log access to specific data.

**Signature:**
```python
def audit_data_access(
    data_type: str,
    access_type: str = "read",
    classification: Optional[str] = None,
    fields: Optional[List[str]] = None,
    include_caller: bool = True
) -> Callable:
```

**Parameters:**
- `data_type`: Type of data being accessed (e.g., "donor", "transaction")
- `access_type`: Type of access (e.g., "read", "write", "delete", "export")
- `classification`: Data classification level
- `fields`: Specific fields being accessed
- `include_caller`: Whether to include caller identity (default: True)

**Example:**
```python
from platform.audit import audit_data_access

# Basic usage
@audit_data_access(
    data_type="donor",
    access_type="read",
    classification="CONFIDENTIAL"
)
def get_donor_info(donor_id: str):
    return donor_service.get_donor(donor_id)

# Specify fields
@audit_data_access(
    data_type="donor",
    access_type="read",
    classification="CONFIDENTIAL",
    fields=["name", "contact_info", "contribution_history"]
)
def get_donor_details(donor_id: str):
    return donor_service.get_details(donor_id)
```

### Data Classification Decorators

#### `@classification()`
Set the data classification level for a tool.

**Signature:**
```python
def classification(
    level: str,
    enforce: bool = True
) -> Callable:
```

**Parameters:**
- `level`: Classification level ("PUBLIC", "INTERNAL", "CONFIDENTIAL", "STRICTLY_CONFIDENTIAL")
- `enforce`: Whether to enforce classification requirements (default: True)

**Example:**
```python
from platform.classification import classification

# Set classification level
@classification("CONFIDENTIAL")
def get_donor_portfolio(donor_id: str):
    return donor_service.get_portfolio(donor_id)

@classification("STRICTLY_CONFIDENTIAL", enforce=True)
def get_sensitive_financial_data():
    return financial_service.get_sensitive_data()

@classification("PUBLIC", enforce=False)
def get_public_info():
    return public_service.get_info()
```

#### `@classify_data()`
Classify specific data fields or parameters.

**Signature:**
```python
def classify_data(
    **field_classifications: str
) -> Callable:
```

**Parameters:**
- `**field_classifications`: Dictionary mapping field names to classification levels

**Example:**
```python
from platform.classification import classify_data

# Classify specific fields
@classify_data(
    ssn="STRICTLY_CONFIDENTIAL",
    credit_card="STRICTLY_CONFIDENTIAL",
    name="CONFIDENTIAL",
    email="CONFIDENTIAL"
)
def process_donor_data(donor_data: dict):
    return data_service.process(donor_data)
```

### Error Handling Decorators

#### `@handle_errors()`
Standardize error handling for a tool.

**Signature:**
```python
def handle_errors(
    func: Optional[Callable] = None,
    *,
    error_mapping: Optional[Dict[Type[Exception], str]] = None,
    default_error_code: str = "UNKNOWN_ERROR",
    log_exceptions: bool = True,
    include_stack_trace: bool = False
) -> Callable:
```

**Parameters:**
- `func`: Function to decorate
- `error_mapping`: Mapping of exception types to error codes
- `default_error_code`: Default error code for unhandled exceptions
- `log_exceptions`: Whether to log exceptions (default: True)
- `include_stack_trace`: Whether to include stack trace in error response (default: False)

**Example:**
```python
from platform.errors import handle_errors

# Basic usage
@handle_errors
def get_donor_data(donor_id: str):
    return donor_service.get_donor(donor_id)

# Custom error mapping
@handle_errors(
    error_mapping={
        ValueError: "INVALID_INPUT",
        PermissionError: "ACCESS_DENIED",
        TimeoutError: "TIMEOUT"
    },
    default_error_code="DONOR_SERVICE_ERROR"
)
def get_donor_with_custom_errors(donor_id: str):
    return donor_service.get_donor(donor_id)
```

### Tool Registration Decorators

#### `@tool`
Register a function as an MCP tool.

**Signature:**
```python
def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    classification: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable:
```

**Parameters:**
- `func`: Function to decorate
- `name`: Tool name (defaults to function name)
- `description`: Tool description
- `classification`: Tool classification level
- `tags`: List of tags for categorization
- `metadata`: Additional tool metadata

**Example:**
```python
from platform.registration import tool

# Basic usage
@tool
def get_donor_portfolio(donor_id: str):
    """Retrieve donor portfolio information."""
    return donor_service.get_portfolio(donor_id)

# Full configuration
@tool(
    name="GetDonorPortfolioHealth",
    description="Retrieve comprehensive donor portfolio health metrics",
    classification="CONFIDENTIAL",
    tags=["donor", "analytics", "portfolio"],
    metadata={
        "domain": "DonorManagement",
        "version": "1.0.0",
        "owner": "DER"
    }
)
def get_donor_portfolio_health(donor_id: str):
    return analytics_service.get_portfolio_health(donor_id)
```

## 🚀 Quick Start

### Basic Decorator Usage

```python
from platform.auth import authenticated_tool
from platform.authorization import requires_permission
from platform.telemetry import track_tool_telemetry
from platform.audit import audit_tool_access
from platform.classification import classification
from platform.registration import tool

# Complete tool with all decorators
@tool(
    name="GetDonorPortfolio",
    description="Retrieve donor portfolio information",
    classification="CONFIDENTIAL"
)
@authenticated_tool
@requires_permission("donor.read")
@track_tool_telemetry
@audit_tool_access(classification="CONFIDENTIAL")
@classification("CONFIDENTIAL")
@handle_errors
def get_donor_portfolio(donor_id: str):
    """Get donor portfolio data."""
    caller = get_caller_identity()
    return donor_service.get_portfolio(donor_id)
```

### Decorator Composition

```python
from platform.auth import authenticated_tool
from platform.authorization import requires_permission, requires_role
from platform.telemetry import track_tool_telemetry, telemetry_context
from platform.audit import audit_tool_access, audit_data_access

# Combined decorators for comprehensive tool protection
@authenticated_tool
@requires_permission("donor.read", "donor.analytics")
@requires_role("donor_analyst")
@track_tool_telemetry(track_arguments=False, track_result=True)
@telemetry_context(domain="DonorManagement", service="Analytics")
@audit_tool_access(classification="CONFIDENTIAL")
@audit_data_access(
    data_type="donor",
    access_type="read",
    classification="CONFIDENTIAL",
    fields=["name", "contact_info", "contribution_history"]
)
@classification("CONFIDENTIAL")
@handle_errors(
    error_mapping={
        ValueError: "INVALID_DONOR_ID",
        PermissionError: "ACCESS_DENIED"
    }
)
def get_comprehensive_donor_analytics(donor_id: str):
    """Get comprehensive donor analytics with full tracking and protection."""
    return analytics_service.get_comprehensive_analytics(donor_id)
```

## ⭐ Best Practices

### Decorator Order

✅ **Follow the Recommended Order**
```python
# Good: Recommended decorator order
@tool()                    # Tool registration (outermost)
@classification()         # Data classification
@audit_tool_access()      # Audit logging
@handle_errors()           # Error handling
@track_tool_telemetry()   # Telemetry
@requires_role()          # Authorization (role-based)
@requires_permission()    # Authorization (permission-based)
@authenticated_tool()     # Authentication (innermost)
def my_tool():
    pass
```

❌ **Avoid Incorrect Order**
```python
# Bad: Incorrect decorator order can cause issues
@authenticated_tool()     # Should be innermost
@tool()                    # Should be outermost
def my_tool():
    pass
```

### Decorator Usage Patterns

✅ **Use Decorators for Cross-Cutting Concerns**
```python
# Good: Use decorators for authentication, authorization, telemetry
@authenticated_tool
@requires_permission("donor.read")
@track_tool_telemetry
def get_donor_data(donor_id: str):
    pass
```

❌ **Avoid Manual Implementation**
```python
# Bad: Manual implementation of cross-cutting concerns
def get_donor_data(donor_id: str):
    # Manual authentication check
    if not is_authenticated():
        raise AuthenticationError()
    
    # Manual permission check
    if not has_permission("donor.read"):
        raise AuthorizationError()
    
    # Manual telemetry
    start_time = time.time()
    try:
        result = donor_service.get_donor(donor_id)
        track_telemetry(tool_name="get_donor_data", duration=time.time() - start_time)
        return result
    except Exception as e:
        track_exception(e)
        raise
```

### Performance Considerations

✅ **Be Mindful of Decorator Overhead**
```python
# Good: Use appropriate decorators for the tool's needs
@authenticated_tool
@track_tool_telemetry  # Only add telemetry if needed
@audit_tool_access      # Only add audit if sensitive
@classification("CONFIDENTIAL")
def get_donor_data(donor_id: str):
    pass
```

✅ **Disable Unnecessary Features**
```python
# Good: Disable features that aren't needed
@track_tool_telemetry(
    track_arguments=False,  # Don't track arguments if sensitive
    track_result=False      # Don't track result if large
)
def get_large_dataset():
    pass
```

## 🔍 Troubleshooting

### Common Issues

**Decorators not working**
- Verify that decorators are applied in the correct order
- Check that the decorated function is properly registered
- Ensure all required dependencies are imported

**Authentication/Authorization failures**
- Verify that authentication is properly configured
- Check that the caller has the required permissions/roles
- Ensure the token is valid and not expired

**Telemetry not appearing**
- Verify that telemetry is enabled in configuration
- Check that Application Insights is properly configured
- Ensure the connection string is valid

**Audit logs missing**
- Verify that audit logging is enabled
- Check that storage account is properly configured
- Ensure the container exists and is accessible

**Classification enforcement not working**
- Verify that classification is enabled
- Check that classification levels are correctly specified
- Ensure classification enforcement is enabled

## 📚 Related Documentation

- [Platform API](platform.md) - Core framework classes
- [Authentication API](authentication.md) - Authentication services
- [Authorization API](authorization.md) - Authorization services
- [Telemetry API](telemetry.md) - Telemetry services
- [Audit API](audit.md) - Audit logging services
- [Classification Module](../modules/data-classification.md) - Data classification
- [Tool Registration Module](../modules/tool-registration.md) - Tool registration

---

**🎉 Ready to use decorators?** Start with the basic decorators like `@authenticated_tool`, `@requires_permission`, and `@track_tool_telemetry` for comprehensive tool protection.

**Need more details?** Check the individual module documentation for specific decorator details and advanced usage patterns.