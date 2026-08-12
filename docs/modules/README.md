# 📦 Platform Modules

The MCP Platform Framework consists of several specialized modules, each handling a specific infrastructure concern. This section provides detailed documentation for each module.

## 🗂️ Module Overview

| Module | Purpose | Key Features | Decorators |
|--------|---------|--------------|------------|
| **[Authentication](authentication.md)** | Identity verification and token management | Entra ID, Managed Identity, JWT validation | `@authenticated_tool` |
| **[Authorization](authorization.md)** | Access control and permission management | RBAC, policy enforcement | `@requires_permission`, `@requires_role` |
| **[Telemetry](telemetry.md)** | Observability and monitoring | Application Insights, automatic tracking | `@track_tool_telemetry` |
| **[Audit](audit.md)** | Compliance logging | Immutable logs, Azure Blob Storage | `@audit_tool_access`, `@audit_data_access` |
| **[Errors](errors.md)** | Error handling and standardization | Error codes, exception hierarchy | - |
| **[Configuration](configuration.md)** | Environment-aware settings | Key Vault, multi-source config | - |
| **[Classification](classification.md)** | Data governance | Classification levels, policy enforcement | `@classification`, `@classify_data` |
| **[Registration](registration.md)** | Tool discovery and registration | Automatic discovery, metadata generation | `@tool`, `@resource`, `@query`, `@action` |
| **[Connectivity](connectivity.md)** | Fabric integration | Semantic models, warehouses, lakehouses | - |
| **[Framework](framework.md)** | Main integration | Unified interface, lifecycle management | - |

## 🎯 Module Architecture

Each module follows a consistent architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      MODULE STRUCTURE                          │
├─────────────────────────────────────────────────────────────┤
│                                                                 │
│  module/                                                           │
│  ├── __init__.py             # Public exports                    │
│  ├── models.py              # Data models (Pydantic)            │
│  ├── exceptions.py          # Module-specific exceptions         │
│  ├── core.py                # Core functionality                 │
│  ├── decorators.py          # Decorator implementations          │
│  ├── handlers.py            # Event/operation handlers           │
│  └── utils.py               # Utility functions                  │
│                                                                 │
│  # Global instances and factory functions                     │
│  ├── get_<module>()         # Get singleton instance             │
│  ├── reset_<module>()       # Reset global instance               │
│  └── create_<module>()      # Create new instance                │
│                                                                 │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Authentication Module

**Purpose**: Handle identity verification, token validation, and authentication flows.

**Key Components**:
- `EntraIDAuthenticator` - Azure AD authentication
- `ManagedIdentityAuthenticator` - Managed Identity support
- `JWTValidator` - JWT token validation with public key caching
- `Identity` - Identity model with roles and permissions

**Usage**:
```python
from platform.auth import authenticated_tool, get_authenticator

@authenticated_tool
def my_tool():
    # Tool requires authentication
    pass

# Manual authentication
authenticator = get_authenticator()
result = authenticator.authenticate(token)
```

📖 **[Full Documentation](authentication.md)**

---

## 🛡️ Authorization Module

**Purpose**: Manage access control, permissions, and role-based authorization.

**Key Components**:
- `RBACEngine` - Role-Based Access Control engine
- `Policy` - Permission and role definitions
- `AccessRequest` - Request context for authorization decisions
- `AccessDecision` - Authorization decision with reasoning

**Usage**:
```python
from platform.authorization import requires_permission, requires_role

@requires_permission("donor.read")
def get_donor_info(donor_id: str):
    # Requires "donor.read" permission
    pass

@requires_role("donor_manager")
def update_donor(donor_id: str, data: dict):
    # Requires "donor_manager" role
    pass
```

📖 **[Full Documentation](authorization.md)**

---

## 📊 Telemetry Module

**Purpose**: Collect, buffer, and export telemetry data for observability.

**Key Components**:
- `TelemetryCollector` - Collects and buffers telemetry data
- `ApplicationInsightsExporter` - Exports to Azure Application Insights
- `ConsoleExporter` - Exports to console (for development)
- `TelemetryData` - Standardized telemetry data model

**Usage**:
```python
from platform.telemetry import track_tool_telemetry, get_telemetry_collector

@track_tool_telemetry
def my_tool():
    # Automatically tracks execution time, status, etc.
    pass

# Manual tracking
telemetry = get_telemetry_collector()
telemetry.track_tool_execution("my_tool", duration=100, status="success")
```

📖 **[Full Documentation](telemetry.md)**

---

## 📝 Audit Module

**Purpose**: Create immutable audit logs for compliance and security monitoring.

**Key Components**:
- `AuditLogger` - Main audit logging interface
- `AuditRecord` - Standardized audit record model
- `AzureBlobStorage` - Blob Storage backend for audit logs
- `InMemoryStorage` - In-memory backend (for testing)

**Usage**:
```python
from platform.audit import audit_tool_access, get_audit_logger

@audit_tool_access
def sensitive_tool():
    # Automatically logs access to this tool
    pass

# Manual logging
audit = get_audit_logger()
audit.log_tool_access(user="user@example.com", tool="sensitive_tool", success=True)
```

📖 **[Full Documentation](audit.md)**

---

## ❌ Error Handling Module

**Purpose**: Standardize error handling, error codes, and exception management.

**Key Components**:
- `ErrorHandler` - Central error handling
- `MCPError` - Base exception class
- `ErrorCategory` - Error categorization (DataAccess, Validation, etc.)
- `ErrorResponse` - Standardized error response model

**Usage**:
```python
from platform.errors import get_error_handler, MCPError, ErrorCategory

# Raise standardized errors
raise MCPError(
    error_code="DONOR-001",
    category=ErrorCategory.DataAccess,
    message="Donor not found",
    details={"donor_id": "12345"}
)

# Handle errors
error_handler = get_error_handler()
response = error_handler.handle_error(exception)
```

📖 **[Full Documentation](errors.md)**

---

## ⚙️ Configuration Module

**Purpose**: Manage environment-aware configuration from multiple sources.

**Key Components**:
- `ConfigManager` - Central configuration management
- `ConfigLoader` - Loads configuration from files, env vars, Key Vault
- `AzureConfig` - Azure-specific configuration
- `FabricConfig` - Fabric-specific configuration

**Usage**:
```python
from platform.config import get_config_manager

config = get_config_manager()

# Get Azure configuration
azure_config = config.get_azure_config()
print(azure_config.subscription_id)

# Get Fabric configuration
fabric_config = config.get_fabric_config()
print(fabric_config.workspace_id)
```

📖 **[Full Documentation](configuration.md)**

---

## 🏷️ Classification Module

**Purpose**: Enforce data classification and governance policies.

**Key Components**:
- `ClassificationEngine` - Policy enforcement engine
- `ClassificationLevel` - PUBLIC, INTERNAL, CONFIDENTIAL, STRICTLY_CONFIDENTIAL
- `ClassificationPolicy` - Governance policies
- `ClassificationViolation` - Policy violation tracking

**Usage**:
```python
from platform.classification import classification, classify_data

@classification("CONFIDENTIAL")
def sensitive_tool():
    # This tool handles confidential data
    pass

@classify_data("PUBLIC")
def get_public_data():
    # This tool returns public data
    pass
```

📖 **[Full Documentation](classification.md)**

---

## 🔧 Registration Module

**Purpose**: Automatic tool discovery, registration, and metadata management.

**Key Components**:
- `ToolRegistry` - Central registry for all tools
- `ToolDiscovery` - Automatically discovers tools in domain modules
- `ToolMetadata` - Standardized tool metadata
- `ToolType` - FUNCTION, QUERY, ACTION, RESOURCE

**Usage**:
```python
from platform.registration import tool, resource, query, action

@tool(description="Get donor information")
def get_donor(donor_id: str):
    # Automatically registered as a FUNCTION tool
    pass

@resource(description="Get donor data")
def get_donor_data(donor_id: str):
    # Automatically registered as a RESOURCE tool
    pass

@query(description="Query donors")
def query_donors(filter: str):
    # Automatically registered as a QUERY tool
    pass

@action(description="Update donor")
def update_donor(donor_id: str, data: dict):
    # Automatically registered as an ACTION tool
    pass
```

📖 **[Full Documentation](registration.md)**

---

## 🔗 Connectivity Module

**Purpose**: Provide standardized access to Microsoft Fabric services.

**Key Components**:
- `FabricClient` - Fabric management client
- `SemanticModelClient` - Power BI semantic model access
- `WarehouseClient` - Fabric warehouse access
- `LakehouseClient` - Fabric lakehouse access
- `FabricConnectors` - Unified interface for all Fabric services

**Usage**:
```python
from platform.connectivity import semantic_model, warehouse, lakehouse, fabric

# Query a semantic model
result = semantic_model.execute("EVALUATE DonorPortfolio")

# Query a warehouse
result = warehouse.execute("SELECT * FROM Donors WHERE Status = 'Active'")

# Query a lakehouse
result = lakehouse.execute("SELECT * FROM Pipeline")

# Access Fabric management
workspace = fabric.get_workspace()
```

📖 **[Full Documentation](connectivity.md)**

---

## 🎯 Framework Module

**Purpose**: Main integration class that unifies all platform modules.

**Key Components**:
- `MCPFramework` - Main framework class
- `FrameworkConfig` - Framework configuration
- `get_framework()` - Get singleton framework instance
- `initialize_framework()` - Initialize framework with custom config

**Usage**:
```python
from platform.framework import get_framework, initialize_framework

# Get the global framework instance
framework = get_framework()

# Access platform services
framework.auth.authenticate(token)
framework.telemetry.track_tool_execution("tool_name", duration=100)
framework.audit.log_access(user="user@example.com", tool="tool_name")

# Or initialize with custom configuration
framework = initialize_framework(
    domain="DonorManagement",
    environment="Dev",
    enable_telemetry=True,
    enable_audit=True
)
```

📖 **[Full Documentation](framework.md)**

---

## 📚 Module Index

### Authentication
- [Overview](authentication.md)
- [Entra ID Integration](authentication.md#entra-id-integration)
- [Managed Identity](authentication.md#managed-identity)
- [JWT Validation](authentication.md#jwt-validation)
- [Decorators](authentication.md#decorators)

### Authorization
- [Overview](authorization.md)
- [RBAC Engine](authorization.md#rbac-engine)
- [Permission Management](authorization.md#permission-management)
- [Policy Enforcement](authorization.md#policy-enforcement)
- [Decorators](authorization.md#decorators)

### Telemetry
- [Overview](telemetry.md)
- [Telemetry Collector](telemetry.md#telemetry-collector)
- [Exporters](telemetry.md#exporters)
- [Automatic Tracking](telemetry.md#automatic-tracking)
- [Decorators](telemetry.md#decorators)

### Audit
- [Overview](audit.md)
- [Audit Logger](audit.md#audit-logger)
- [Storage Backends](audit.md#storage-backends)
- [Audit Records](audit.md#audit-records)
- [Decorators](audit.md#decorators)

### Errors
- [Overview](errors.md)
- [Error Handler](errors.md#error-handler)
- [Exception Hierarchy](errors.md#exception-hierarchy)
- [Error Codes](errors.md#error-codes)
- [Error Responses](errors.md#error-responses)

### Configuration
- [Overview](configuration.md)
- [Config Manager](configuration.md#config-manager)
- [Config Loader](configuration.md#config-loader)
- [Configuration Sources](configuration.md#configuration-sources)
- [Environment Configuration](configuration.md#environment-configuration)

### Classification
- [Overview](classification.md)
- [Classification Engine](classification.md#classification-engine)
- [Classification Levels](classification.md#classification-levels)
- [Policies](classification.md#policies)
- [Decorators](classification.md#decorators)

### Registration
- [Overview](registration.md)
- [Tool Registry](registration.md#tool-registry)
- [Tool Discovery](registration.md#tool-discovery)
- [Tool Metadata](registration.md#tool-metadata)
- [Decorators](registration.md#decorators)

### Connectivity
- [Overview](connectivity.md)
- [Fabric Client](connectivity.md#fabric-client)
- [Semantic Model Client](connectivity.md#semantic-model-client)
- [Warehouse Client](connectivity.md#warehouse-client)
- [Lakehouse Client](connectivity.md#lakehouse-client)
- [Unified Connectors](connectivity.md#unified-connectors)

### Framework
- [Overview](framework.md)
- [Framework Configuration](framework.md#framework-configuration)
- [Module Access](framework.md#module-access)
- [Lifecycle Management](framework.md#lifecycle-management)
- [Context Manager](framework.md#context-manager)

---

## 🎯 Best Practices for Using Modules

### 1. **Use Decorators for Automatic Integration**
⭐ **Best Practice**: Always use the provided decorators instead of manual integration.

```python
# ✅ Good - Automatic integration
@tool(description="Get donor info")
@authenticated_tool
@requires_permission("donor.read")
@classification("CONFIDENTIAL")
def get_donor_info(donor_id: str):
    pass

# ❌ Bad - Manual integration (more error-prone)
def get_donor_info(donor_id: str):
    # Manual authentication check
    # Manual permission check
    # Manual classification check
    pass
```

### 2. **Leverage Fabric Connectivity**
⭐ **Best Practice**: Always use the platform's Fabric connectivity instead of direct access.

```python
# ✅ Good - Use platform connectivity
from platform.connectivity import semantic_model

result = semantic_model.execute("EVALUATE DonorPortfolio")

# ❌ Bad - Direct access (bypasses platform features)
# import pyodbc
# conn = pyodbc.connect("...")
# cursor = conn.cursor()
# cursor.execute("SELECT * FROM Donors")
```

### 3. **Enable All Security Features**
🔒 **Security**: Always enable authentication, authorization, and classification in production.

```python
# ✅ Good - All security features enabled
framework = initialize_framework(
    enable_authentication=True,
    enable_authorization=True,
    enable_classification=True
)

# ❌ Bad - Security features disabled
framework = initialize_framework(
    enable_authentication=False,  # ❌ Never do this in production
    enable_authorization=False,   # ❌ Never do this in production
    enable_classification=False   # ❌ Never do this in production
)
```

### 4. **Use Semantic Models for Business Metrics**
⭐ **Best Practice**: Always use semantic models instead of direct table access for business metrics.

```python
# ✅ Good - Use semantic models
from platform.connectivity import semantic_model

result = semantic_model.execute("EVALUATE RevenueByRegion")

# ❌ Bad - Direct table access
# result = warehouse.execute("SELECT * FROM RevenueTable")
```

### 5. **Handle Errors Properly**
⭐ **Best Practice**: Use the platform's error handling for consistent error responses.

```python
# ✅ Good - Use platform error handling
from platform.errors import MCPError, ErrorCategory

raise MCPError(
    error_code="DONOR-001",
    category=ErrorCategory.DataAccess,
    message="Donor not found",
    details={"donor_id": donor_id}
)

# ❌ Bad - Generic exceptions
# raise ValueError("Donor not found")
```

---

## 🔍 Module Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    MODULE DEPENDENCIES                          │
├─────────────────────────────────────────────────────────────┤
│                                                                 │
│  Framework                                                        │
│  ├── Authentication                                               │
│  │   ├── azure-identity                                            │
│  │   └── PyJWT                                                     │
│  │                                                                 │
│  ├── Authorization                                                │
│  │   └── (No external dependencies)                               │
│  │                                                                 │
│  ├── Telemetry                                                     │
│  │   ├── opentelemetry-api                                        │
│  │   ├── opentelemetry-sdk                                         │
│  │   └── azure-monitor-opentelemetry                              │
│  │                                                                 │
│  ├── Audit                                                         │
│  │   ├── azure-storage-blob                                       │
│  │   └── opentelemetry-api                                         │
│  │                                                                 │
│  ├── Errors                                                        │
│  │   └── (No external dependencies)                               │
│  │                                                                 │
│  ├── Configuration                                                 │
│  │   ├── azure-keyvault-secrets                                   │
│  │   ├── pyyaml                                                    │
│  │   └── python-dotenv                                             │
│  │                                                                 │
│  ├── Classification                                                │
│  │   └── (No external dependencies)                               │
│  │                                                                 │
│  ├── Registration                                                  │
│  │   └── (No external dependencies)                               │
│  │                                                                 │
│  └── Connectivity                                                  │
│      ├── azure-identity                                            │
│      ├── azure-mgmt-fabric                                         │
│      └── (Fabric REST API)                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📖 Next Steps

- **[Authentication Module](authentication.md)** - Deep dive into authentication
- **[Authorization Module](authorization.md)** - Learn about RBAC and permissions
- **[Telemetry Module](telemetry.md)** - Set up monitoring and observability
- **[Connectivity Module](connectivity.md)** - Integrate with Microsoft Fabric
- **[Framework Module](framework.md)** - Main integration and usage patterns
