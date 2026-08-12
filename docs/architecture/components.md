# 🧩 Architecture Components

The MCP Platform Framework consists of several key components that work together to provide a comprehensive platform for domain development. This document describes each component in detail.

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MCP Platform Framework                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   Authentication│    │   Authorization │    │    Telemetry    │  │
│  │     Module      │    │     Module      │    │     Module      │  │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘  │
│           │                      │                      │           │
│           └──────────────────────┼──────────────────────┘           │
│                               │ │ │                                 │
│                               ▼ ▼ ▼                                 │
│                    ┌─────────────────────────┐                      │
│                    │    Platform Framework   │                      │
│                    │   (Core Integration)    │                      │
│                    └────────────┬────────────┘                      │
│                                 │                                   │
│        ┌────────────────────────┼──────────────────────────┐        │
│        │                        │                          │        │
│   ┌────▼────────┐          ┌────▼────────┐          ┌──────▼────┐   │
│   │ Fabric      │          │  Semantic   │          │  Key      │   │
│   │ Connectivity│          │  Models     │          │  Vault    │   │
│   └────┬────────┘          └──────┬──────┘          └─────┬─────┘   │
│        │                        │                         │         │
│        └────────────────────────┼─────────────────────────┘         │
│                                 │                                   │
│                    ┌────────────▼──────────────┐                    │
│                    │   Domain Template System  │                    │
│                    │   (Tool Discovery, etc.)  │                    │
│                    └────────────┬──────────────┘                    │
│                                 │                                   │
│        ┌────────────────────────┼────────────────────────┐          │
│        │                        │                        │          │
│   ┌────▼─────┐          ┌───────▼──────┐          ┌─────▼────┐      │
│   │  Domain  │          │   Domain     │          │  Domain  │      │
│   │   A      │          │     B        │          │    C     │      │
│   │ (e.g.,   │          │ (e.g.,       │          │ (e.g.,   │      │
│   │ Donor    │          │ Finance)     │          │ Supply)  │      │
│   └──────────┘          └──────────────┘          └──────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔐 Authentication Module

### Overview
Provides comprehensive authentication capabilities for Azure environments, ensuring that every request is properly authenticated before processing.

### Components

```
┌───────────────────────────────────────────┐
│         Authentication Module             │
├───────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Entra ID       │  │  JWT Validation │ │
│  │  Integration    │  │  & Verification │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Managed Identity│  │ OAuth2 Handling │ │
│  │   Support       │  │                 │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │        Token Validation              │ │
│  │      & Caller Attribution            │ │
│  └──────────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

### Key Features

1. **Entra ID Integration**
   - Azure AD authentication
   - Multi-tenant support
   - User and service principal authentication

2. **JWT Validation**
   - Token signature verification
   - Claims validation
   - Expiration checking
   - Audience validation

3. **Managed Identity Support**
   - System-assigned identities
   - User-assigned identities
   - Automatic token acquisition

4. **OAuth2 Handling**
   - Authorization code flow
   - Client credentials flow
   - Token refresh

5. **Caller Attribution**
   - User identity extraction
   - Service principal identification
   - Request context enrichment

### Usage Example

```python
from platform.auth import authenticated_tool, get_caller_identity

@authenticated_tool
def get_donor_data(donor_id: str):
    # Get caller information
    caller = get_caller_identity()
    
    # Domain logic
    return donor_service.get_donor(donor_id)
```

## 🛡️ Authorization Module

### Overview
Provides enterprise-grade Role-Based Access Control (RBAC) with fine-grained permission management.

### Components

```
┌─────────────────────────────────────────┐
│         Authorization Module            │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌───────────────┐ │
│  │   RBAC Engine   │  │ Permission    │ │
│  │                 │  │  Decorators   │ │
│  └─────────────────┘  └───────────────┘ │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Policy          │  │ Standardized  │ │
│  │  Enforcement    │  │  Checks       │ │
│  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────┘
```

### Key Features

1. **Enterprise RBAC**
   - Role definitions and management
   - Role hierarchy support
   - Role assignment and inheritance

2. **Permission Decorators**
   - `@requires_permission("resource.action")`
   - `@requires_role("role_name")`
   - `@requires_any_permission(["perm1", "perm2"])`

3. **Policy Enforcement**
   - Centralized policy definitions
   - Dynamic policy evaluation
   - Policy caching for performance

4. **Standardized Checks**
   - Consistent permission naming
   - Domain-scoped permissions
   - Audit logging for all checks

### Usage Example

```python
from platform.auth import requires_permission, requires_role

# Permission-based authorization
@requires_permission("donor.read")
def get_donor(donor_id: str):
    return donor_service.get(donor_id)

# Role-based authorization
@requires_role("donor_analyst")
def get_donor_analytics():
    return analytics_service.get_donor_metrics()

# Multiple permissions
@requires_any_permission(["donor.read", "donor.admin"])
def get_donor_list():
    return donor_service.list_all()
```

## 📊 Telemetry Module

### Overview
Provides automatic, comprehensive telemetry collection for all MCP tool calls.

### Components

```
┌───────────────────────────────────────────┐
│           Telemetry Module                │
├───────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Metric         │  │  Trace          │ │
│  │  Collection     │  │  Collection     │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Log Collection  │  │  Context       │ │
│  │                 │  │  Propagation    │ │
│  └─────────────────┘  └─────────────────┘ │
└───────────────────────────────────────────┘
```

### Key Features

1. **Automatic Instrumentation**
   - Tool name capture
   - Requester identity tracking
   - Duration measurement
   - Status tracking

2. **Standardized Metrics**
   - Consistent format across all domains
   - JSON-based structure
   - Easy integration with monitoring tools

3. **Context Propagation**
   - Request ID tracking
   - Correlation IDs
   - Distributed tracing support

4. **Performance Monitoring**
   - Execution duration
   - Token usage tracking
   - Resource consumption

### Telemetry Structure

```json
{
  "tool": "GetDonorPortfolioHealth",
  "domain": "DonorManagement",
  "duration_ms": 450,
  "status": "Success",
  "requester": {
    "identity": "john.doe@my-org.org",
    "roles": ["donor_analyst"],
    "permissions": ["donor.read", "donor.analytics"]
  },
  "environment": "Production",
  "workspace": "DER-Analytics",
  "timestamp": "2026-05-01T10:30:00Z",
  "token_usage": {
    "input_tokens": 150,
    "output_tokens": 250
  }
}
```

### Usage Example

```python
from platform.telemetry import telemetry

@telemetry.capture_tool_metrics
def get_donor_pipeline():
    # Domain logic - telemetry automatically captured
    return pipeline_service.get_health()
```

## 📝 Audit Logging Module

### Overview
Provides immutable audit logging for sensitive operations and compliance monitoring.

### Components

```
┌───────────────────────────────────────────┐
│          Audit Logging Module             │
├───────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Audit Record   │  │  Sensitive      │ │
│  │  Generation     │  │  Query Detection│ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Compliance      │  │ Immutable       │ │
│  │ Monitoring      │  │ Storage         │ │
│  └─────────────────┘  └─────────────────┘ │
└───────────────────────────────────────────┘
```

### Key Features

1. **Automatic Audit Records**
   - User identification
   - Tool name and parameters
   - Timestamp
   - Operation result

2. **Sensitive Query Detection**
   - Pattern matching for sensitive data
   - Automatic audit triggering
   - Configurable sensitivity levels

3. **Compliance Monitoring**
   - Access pattern analysis
   - Anomaly detection
   - Compliance reporting

4. **Immutable Storage**
   - Write-once, read-many storage
   - Tamper-evident logging
   - Long-term retention

### Audit Record Structure

```json
{
  "audit_id": "aud-20260501-103000-001",
  "user": "john.doe@my-org.org",
  "tool": "GetTopDonorContributions",
  "time": "2026-05-01T10:30:00Z",
  "parameters": {
    "year": 2026,
    "limit": 10
  },
  "result": "Success",
  "classification": "CONFIDENTIAL",
  "ip_address": "192.168.1.100",
  "user_agent": "MCP-Client/1.0",
  "session_id": "sess-20260501-100000-001"
}
```

### Usage Example

```python
from platform.audit import audit_log

@audit_log.sensitive_operation
@requires_permission("finance.confidential")
def get_top_contributions():
    # This operation will be automatically audited
    return contribution_service.get_top(10)
```

## ❌ Error Handling Module

### Overview
Provides standardized error structures, error codes, and exception handling.

### Components

```
┌──────────────────────────────────────────┐
│         Error Handling Module            │
├──────────────────────────────────────────┤
│  ┌─────────────────┐  ┌────────────────┐ │
│  │ Error Codes     │  │ Error          │ │
│  │ & Categories    │  │ Structures     │ │
│  └─────────────────┘  └────────────────┘ │
│  ┌─────────────────┐  ┌────────────────┐ │
│  │ Exception       │  │ Operational    │ │
│  │ Handling        │  │ Diagnostics    │ │
│  └─────────────────┘  └────────────────┘ │
└──────────────────────────────────────────┘
```

### Key Features

1. **Standardized Error Codes**
   - Domain-specific prefixes (DONOR-001, FINANCE-002, etc.)
   - Consistent categorization
   - Human-readable messages

2. **Error Categories**
   - `DataAccess`: Database or storage access errors
   - `Validation`: Input validation errors
   - `Authorization`: Permission or access errors
   - `Authentication`: Identity verification errors
   - `Configuration`: Configuration-related errors
   - `Integration`: External system integration errors

3. **Error Structure**

```json
{
  "error_code": "DONOR-001",
  "category": "DataAccess",
  "message": "Access denied to donor data",
  "details": {
    "donor_id": "DON-12345",
    "required_permission": "donor.read"
  },
  "timestamp": "2026-05-01T10:30:00Z",
  "severity": "ERROR",
  "correlation_id": "corr-20260501-103000-001"
}
```

4. **Exception Handling**
   - Automatic error classification
   - Context enrichment
   - Error chaining support

### Usage Example

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

# Automatic error handling in tools
@tool
def get_donor(donor_id: str):
    try:
        return donor_service.get(donor_id)
    except MCPError:
        raise  # Re-raise with proper formatting
    except Exception as e:
        # Convert to standardized error
        raise MCPError.from_exception(e)
```

## 🏷️ Data Classification Module

### Overview
Provides data classification controls and governance policy enforcement.

### Components

```
┌─────────────────────────────────────────┐
│       Data Classification Module        │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Classification  │  │ Governance    │ │
│  │ Levels          │  │ Policy        │ │
│  └─────────────────┘  │ Enforcement   │ │
│                       └───────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │         Framework Controls         │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Classification Levels

| Level | Description | Access Requirements | Audit Required |
|-------|-------------|---------------------|----------------|
| **PUBLIC** | Non-sensitive data | None | No |
| **INTERNAL** | Internal business data | Domain access | Yes |
| **CONFIDENTIAL** | Sensitive business data | Explicit permission | Yes |
| **STRICTLY CONFIDENTIAL** | Highly sensitive data | Special approval | Yes |

### Key Features

1. **Classification Decorators**
   - `@classification("CONFIDENTIAL")`
   - Automatic classification enforcement
   - Access control integration

2. **Governance Policy Enforcement**
   - Centralized policy definitions
   - Automatic policy application
   - Compliance checking

3. **Framework Controls**
   - Classification validation
   - Access restriction enforcement
   - Audit logging integration

### Usage Example

```python
from platform.classification import classification, ClassificationLevel

@classification(ClassificationLevel.CONFIDENTIAL)
@requires_permission("finance.confidential")
def get_financial_reports():
    return finance_service.get_reports()

# Classification can also be checked programmatically
current_classification = classification.get_current_level()
if current_classification >= ClassificationLevel.CONFIDENTIAL:
    # Apply additional security measures
    enable_encryption()
```

## 🔧 Tool Registration Module

### Overview
Provides automatic MCP tool discovery, registration, and metadata generation.

### Components

```
┌─────────────────────────────────────────┐
│        Tool Registration Module         │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Automatic       │  │ Metadata      │ │
│  │ Discovery       │  │ Generation    │ │
│  └─────────────────┘  └───────────────┘ │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Tool            │  │ Registration  │ │
│  │ Decorators      │  │ Management    │ │
│  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────┘
```

### Key Features

1. **Automatic Discovery**
   - Scans domain packages for `@tool` decorated functions
   - Extracts function signatures and docstrings
   - Generates tool metadata automatically

2. **Metadata Generation**
   - Tool name and description
   - Parameter definitions
   - Return type information
   - Classification level
   - Required permissions

3. **Registration Management**
   - Central tool registry
   - Dynamic registration and unregistration
   - Tool versioning support

### Tool Declaration

```python
from platform.registration import tool

@tool(
    name="GetFundingPipelineRisk",
    description="Calculates risk score for funding pipeline",
    classification="CONFIDENTIAL"
)
def get_funding_pipeline_risk(pipeline_id: str, days: int = 30) -> dict:
    """
    Calculate risk score for a funding pipeline.
    
    Args:
        pipeline_id: The ID of the funding pipeline
        days: Number of days to analyze (default: 30)
    
    Returns:
        Dictionary containing risk score and analysis
    """
    return risk_service.calculate_pipeline_risk(pipeline_id, days)
```

### Automatic Registration

```python
# In your domain's __init__.py
from platform.registration import register_domain_tools

# Automatically discover and register all tools in this domain
register_domain_tools(__name__)
```

## 🌐 Fabric Connectivity Module

### Overview
Provides standardized connectors for Microsoft Fabric integration.

### Components

```
┌─────────────────────────────────────────┐
│       Fabric Connectivity Module        │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Semantic Model  │  │ Warehouse     │ │
│  │ Connectors      │  │ Connectors    │ │
│  └─────────────────┘  └───────────────┘ │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Lakehouse       │  │ Fabric        │ │
│  │ Connectors      │  │ Endpoint      │ │
│  └─────────────────┘  │ Adapters      │ │
│                       └───────────────┘ │
└─────────────────────────────────────────┘
```

### Key Features

1. **Semantic Model Access**
   - Standardized semantic model connectors
   - Encourages metric consumption through semantic models
   - Prevents direct table access

2. **Warehouse Connectors**
   - SQL query execution
   - Data retrieval and manipulation
   - Transaction support

3. **Lakehouse Connectors**
   - Delta table access
   - File system operations
   - Spark integration

4. **Fabric Endpoint Adapters**
   - REST API integration
   - GraphQL support
   - WebSocket connections

### Usage Example

```python
from platform.fabric import get_semantic_model, get_warehouse

# Semantic model access
semantic_model = get_semantic_model("DonorManagement")
result = semantic_model.execute(
    query="SELECT DonorCount, TotalRevenue FROM DonorMetrics WHERE Year = 2026"
)

# Warehouse access
warehouse = get_warehouse("GoldLayer")
data = warehouse.query(
    sql="SELECT * FROM dimDonor WHERE Status = 'Active'"
)
```

## 📁 Configuration Management Module

### Overview
Provides environment-aware configuration management with Azure Key Vault integration.

### Components

```
┌─────────────────────────────────────────┐
│      Configuration Management Module    │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Environment     │  │ Key Vault     │ │
│  │ Configuration   │  │ Integration   │ │
│  └─────────────────┘  └───────────────┘ │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Validation      │  │ Secret        │ │
│  │                 │  │ Management    │ │
│  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────┘
```

### Key Features

1. **Environment-Aware Configuration**
   - Separate configurations for DEV, TEST, PROD
   - Automatic environment detection
   - Configuration inheritance and overrides

2. **Key Vault Integration**
   - Standardized secret retrieval
   - Automatic secret caching
   - Secret rotation support

3. **Validation**
   - Configuration schema validation
   - Required field checking
   - Type validation

4. **Secret Management**
   - No credentials in code
   - Developers cannot access secrets directly
   - Centralized secret management

### Configuration Structure

```yaml
# config/dev.yaml
domain: DonorManagement
environment: Dev

fabric:
  endpoint: "https://dev-fabric.my-org.org"
  semantic_models:
    - DonorManagement
    - Finance

azure:
  key_vault: "dev-kv-unhcr"
  function_app: "dev-mcp-donor"

logging:
  level: DEBUG
  telemetry: true

# config/prod.yaml
domain: DonorManagement
environment: Production

fabric:
  endpoint: "https://fabric.my-org.org"
  semantic_models:
    - DonorManagement
    - Finance

azure:
  key_vault: "prod-kv-unhcr"
  function_app: "mcp-donor"

logging:
  level: INFO
  telemetry: true
```

### Usage Example

```python
from platform.config import config, keyvault

# Access configuration
environment = config.environment  # "Dev", "Test", or "Production"
domain = config.domain  # "DonorManagement"

# Retrieve secrets from Key Vault
fabric_credentials = keyvault.get_secret("fabric-credentials")
database_password = keyvault.get_secret("db-password")
```

## 🚀 Deployment Module

### Overview
Provides CI/CD pipeline templates and deployment automation for Azure Function Apps.

### Components

```
┌─────────────────────────────────────────┐
│          Deployment Module              │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Build           │  │ Testing       │ │
│  │ Validation      │  │ Frameworks    │ │
│  └─────────────────┘  └───────────────┘ │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Security        │  │ Deployment    │ │
│  │ Scanning        │  │ Pipelines     │ │
│  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────┘
```

### Key Features

1. **Build Validation**
   - Code quality checks
   - Dependency validation
   - Package building

2. **Testing Frameworks**
   - Unit test execution
   - Integration test execution
   - Performance testing
   - Security testing

3. **Security Scanning**
   - Dependency vulnerability scanning
   - Secret detection
   - Code analysis

4. **Deployment Pipelines**
   - ARM template deployment
   - Bicep template deployment
   - Azure DevOps integration
   - GitHub Actions support

## 📚 Catalog Integration Module

### Overview
Provides automatic registration of MCP services with the enterprise registry and governance catalog.

### Components

```
┌─────────────────────────────────────────┐
│        Catalog Integration Module       │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Service         │  │ Metadata      │ │
│  │ Registration    │  │ Generation    │ │
│  └─────────────────┘  └───────────────┘ │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │ Governance      │  │ Enterprise    │ │
│  │ Catalog         │  │ Registry      │ │
│  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────┘
```

### Service Metadata

```yaml
owner: DER
domain: DonorManagement
service: GetDonorPortfolioHealth
version: 1.0.0
sla: Gold
classification: Confidential
description: Retrieves health metrics for donor portfolios
endpoint: /tools/GetDonorPortfolioHealth
authentication: EntraID
authorization: donor.read
telemetry: true
audit: true
```

## 📖 Documentation Generator Module

### Overview
Automatically generates technical documentation from tool metadata and annotations.

### Generated Documentation

- **Tool Documentation**: Description, parameters, return types
- **Authentication Requirements**: Required permissions and roles
- **Owner Information**: Domain and service ownership
- **Version Information**: Service version and changelog
- **API Reference**: Complete API documentation

---

## 🎯 Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Request Processing Flow                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Request Arrives                                                 │
│     └── Function App receives HTTP request                          │
│                                                                     │
│  2. Authentication                                                  │
│     └── @authenticated_tool validates JWT token                     │
│     └── Extracts caller identity                                    │
│                                                                     │
│  3. Authorization                                                   │
│     └── @requires_permission checks user permissions                │
│     └── Validates access to requested resource                      │
│                                                                     │
│  4. Classification Check                                            │
│     └── @classification verifies data access level                  │
│     └── Enforces governance policies                                │
│                                                                     │
│  5. Telemetry Start                                                 │
│     └── Automatic telemetry collection begins                       │
│     └── Request context captured                                    │
│                                                                     │
│  6. Tool Execution                                                  │
│     └── Domain logic executes                                       │
│     └── Fabric connectors used for data access                      │
│     └── Semantic models queried                                     │
│                                                                     │
│  7. Audit Logging (if sensitive)                                    │
│     └── Immutable audit record created                              │
│     └── Compliance monitoring triggered                             │
│                                                                     │
│  8. Telemetry End                                                   │
│     └── Duration and status captured                                │
│     └── Token usage tracked                                         │
│                                                                     │
│  9. Response Returned                                               │
│     └── Formatted response sent to client                           │
│     └── Error handling applied if needed                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*