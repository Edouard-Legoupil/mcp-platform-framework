# 🔧 API Reference

The API Reference provides comprehensive documentation for all platform modules, classes, methods, and utilities available in the MCP Platform Framework.

## 📖 Overview

This section contains detailed API documentation for all components of the MCP Platform Framework. Each module's API is documented with:

- **Classes and Methods**: Complete method signatures, parameters, return types
- **Usage Examples**: Practical code examples showing how to use each API
- **Configuration Options**: Available configuration parameters and their effects
- **Best Practices**: Recommended usage patterns and common pitfalls
- **Error Handling**: Common exceptions and how to handle them

## 🏗️ API Reference Sections

### [Platform API](platform.md)
Complete API reference for the core platform framework, including main classes, initialization, and integration points.

### [Authentication API](authentication.md)
Detailed API documentation for authentication services, including Entra ID integration, JWT validation, and Managed Identity support.

### [Authorization API](authorization.md)
Comprehensive API reference for authorization services, including RBAC, permission decorators, and policy enforcement.

### [Telemetry API](telemetry.md)
API documentation for telemetry services, including Application Insights integration, automatic tracking, and custom metrics.

### [Audit API](audit.md)
Detailed API reference for audit logging services, including compliance logging, immutable records, and Azure Blob Storage integration.

### [Connectivity API](connectivity.md)
API documentation for Microsoft Fabric connectivity, including semantic models, warehouses, lakehouses, and unified interfaces.

### [Decorators](decorators.md)
Complete reference for all framework decorators, including authentication, authorization, telemetry, audit, and classification decorators.

## 🎯 Quick Navigation

**Looking for specific functionality?**

- **Authentication & Authorization**: See [Authentication API](authentication.md) and [Authorization API](authorization.md)
- **Observability**: See [Telemetry API](telemetry.md) and [Audit API](audit.md)
- **Fabric Integration**: See [Connectivity API](connectivity.md)
- **Tool Development**: See [Decorators](decorators.md)
- **Core Framework**: See [Platform API](platform.md)

## 📁 API Organization

The MCP Platform Framework API is organized into logical modules:

```
platform/
├── auth/              # Authentication services
├── authorization/     # Authorization services
├── telemetry/         # Telemetry and observability
├── audit/             # Audit logging and compliance
├── connectivity/      # Fabric connectivity
├── config/            # Configuration management
├── classification/    # Data classification
├── registration/      # Tool registration
├── errors/            # Error handling
└── framework.py       # Main framework integration
```

## 🔍 API Conventions

### Naming Conventions
- **Classes**: PascalCase (e.g., `AuthenticationService`, `TelemetryClient`)
- **Methods**: snake_case (e.g., `validate_token()`, `log_audit_event()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TOKEN_LIFETIME`)
- **Decorators**: snake_case with underscore prefix (e.g., `@authenticated_tool`, `@requires_permission`)

### Parameter Patterns
- **Required Parameters**: Positional or keyword arguments without defaults
- **Optional Parameters**: Keyword arguments with sensible defaults
- **Configuration Parameters**: Typically passed via configuration objects or environment variables

### Return Types
- **Async Methods**: Return `awaitable` types for async operations
- **Sync Methods**: Return concrete values or None
- **Error Handling**: Raise custom exceptions with meaningful error codes

## ⭐ Best Practices

### Using the API Effectively

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
# Bad: Manual authentication and logging
def get_donor_data(donor_id: str):
    # Manual token validation
    # Manual permission checking
    # Manual telemetry logging
    pass
```

### Error Handling Patterns

✅ **Use Framework Exceptions**
```python
from platform.errors import AuthenticationError, AuthorizationError

try:
    # Framework operations
    pass
except AuthenticationError as e:
    # Handle authentication-specific errors
    logger.error(f"Authentication failed: {e.error_code}")
except AuthorizationError as e:
    # Handle authorization-specific errors
    logger.error(f"Authorization denied: {e.error_code}")
```

✅ **Leverage Context Managers**
```python
from platform.telemetry import telemetry_context

with telemetry_context("donor_operations") as ctx:
    ctx.add_tag("domain", "donor_management")
    # Operations are automatically tracked
```

## 🚀 Getting Started with the API

### For Domain Developers

Start with the [Decorators](decorators.md) reference to understand how to annotate your tools with framework capabilities.

### For Platform Integrators

Refer to the [Platform API](platform.md) for integration points and extension mechanisms.

### For DevOps Engineers

See the [Configuration Management](../modules/configuration-management.md) module for deployment and configuration options.

## 📞 Support

- **API Questions**: Check the relevant module documentation
- **Bug Reports**: Open an issue with reproduction steps
- **Feature Requests**: Submit a feature request with use case
- **Contributions**: See [Contributing](../CONTRIBUTING.md) for contribution guidelines

---

**🎉 Ready to explore the API?** Start with the [Platform API](platform.md) or jump to the module you need.

**Need examples?** Check the [Examples](../examples/README.md) section for practical usage patterns.