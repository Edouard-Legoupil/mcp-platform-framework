# 🏗️ Architecture Overview

The MCP Platform Framework is designed with a **strict separation of concerns** principle, ensuring that domains focus solely on business capabilities while the platform handles all infrastructure concerns. This architecture enables consistency, security, and maintainability across all MCP implementations.

## 🎯 Design Philosophy

### Core Principles

1. **🏛️ Separation of Concerns**
   - Domains own business capabilities (business logic, ontologies, semantic definitions)
   - Platform owns everything else (authentication, authorization, telemetry, error handling, connectivity)

2. **🔄 No Domain Forking**
   - All domains use the same central platform template
   - Domains never create custom frameworks
   - Platform evolves independently of domains

3. **🔗 Standardized Integration**
   - Consistent interfaces for all platform services
   - Uniform error handling and observability
   - Common patterns for Fabric connectivity

4. **🔒 Security by Default**
   - Authentication and authorization are enabled by default
   - Data classification is enforced at the framework level
   - Audit logging is automatic and immutable

5. **📊 Observability First**
   - Every operation generates telemetry
   - All sensitive access is audited
   - Performance metrics are automatically collected

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP Ecosystem                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    MCP Platform Framework                            │   │
│  │  ┌───────────────┐  ┌──────────────┐  ┌─────────────┐  ┌───────────┐ │   │
│  │  │ Authentication│  │ Authorization│  │   Telemetry │  │    Audit  │ │   │
│  │  └───────────────┘  └──────────────┘  └─────────────┘  └───────────┘ │   │
│  │  ┌─────────────┐  ┌───────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │  Config     │  │ Classification│  │   Errors    │  │Connectivity│ │   │
│  │  └─────────────┘  └───────────────┘  └─────────────┘  └────────────┘ │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │                    Registration & Discovery                     │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                              ││││││││││││││││                               │
│                              ▼▼▼▼▼▼▼▼▼▼▼▼▼                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Domain Repositories                             │   │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐     │   │
│  │  │  DonorManagement │  │     Finance      │  │     Supply      │     │   │
│  │  │                  │  │                  │  │                 │     │   │
│  │  │  • Business Logic│  │  • Business Logic│  │ • Business Logic│     │   │
│  │  │  • Ontologies    │  │  • Ontologies    │  │ • Ontologies    │     │   │
│  │  │  • Semantic Defs │  │  • Semantic Defs │  │ • Semantic Defs │     │   │
│  │  │  • Tools         │  │  • Tools         │  │ • Tools         │     │   │
│  │  └──────────────────┘  └──────────────────┘  └─────────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Microsoft Azure                                   │   │
│  │  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │ Function App │  │    Fabric   │  │ Key Vault   │  │App Insights │ │   │
│  │  └──────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  │  ┌───────────────┐  ┌─────────────────────────────────────────────┐  │   │
│  │  │Storage Account│  │        Microsoft Fabric Services            │  │   │
│  │  └───────────────┘  │  • Semantic Models (Power BI)               │  │   │
│  │                     │  • Warehouses (SQL)                         │  │   │
│  │                     │  • Lakehouses (Delta/Parquet)               │  │   │
│  │                     └─────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Architecture

### Platform Layer

The platform layer provides all infrastructure services that domains can consume:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PLATFORM LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🔐 AUTHENTICATION                                                  │
│  ├── EntraIDAuthenticator    # Azure AD authentication              │
│  ├── ManagedIdentityAuth     # Managed Identity support             │
│  ├── JWTValidator           # JWT token validation                  │
│  └── Decorators             # @authenticated_tool, etc.             │
│                                                                     │
│  🛡️ AUTHORIZATION                                                   │
│  ├── RBACEngine            # Role-Based Access Control              │
│  ├── PolicyEnforcer        # Policy enforcement                     │
│  └── Decorators            # @requires_permission, @requires_role   │
│                                                                     │
│  📊 TELEMETRY                                                       │
│  ├── TelemetryCollector     # Collects metrics and traces           │
│  ├── ApplicationInsights    # Azure Monitor integration             │
│  └── Decorators             # @track_tool_telemetry                 │
│                                                                     │
│  📝 AUDIT LOGGING                                                   │
│  ├── AuditLogger            # Immutable audit logging               │
│  ├── AzureBlobStorage       # Audit log storage                     │
│  └── Decorators             # @audit_tool_access, @audit_data_access│
│                                                                     │
│  ❌ ERROR HANDLING                                                  │
│  ├── ErrorHandler           # Standardized error handling           │
│  ├── ExceptionHierarchy     # Platform-specific exceptions          │
│  └── ErrorCodes             # Standardized error codes              │
│                                                                     │
│  ⚙️ CONFIGURATION                                                   │
│  ├── ConfigManager          # Environment-aware configuration       │
│  ├── ConfigLoader           # Loads from files, env vars, Key Vault │
│  └── KeyVaultClient         # Azure Key Vault integration           │
│                                                                     │
│  🏷️ CLASSIFICATION                                                  │
│  ├── ClassificationEngine   # Policy enforcement                    │
│  ├── ClassificationLevels   # PUBLIC, INTERNAL, CONFIDENTIAL, etc.  │
│  └── Decorators             # @classification, @classify_data       │
│                                                                     │
│  🔧 REGISTRATION                                                    │
│  ├── ToolRegistry           # Central tool registry                 │
│  ├── ToolDiscovery          # Automatic tool discovery              │
│  └── Decorators             # @tool, @resource, @query, @action     │
│                                                                     │
│  🔗 CONNECTIVITY                                                    │
│  ├── FabricClient           # Fabric management client              │
│  ├── SemanticModelClient    # Power BI semantic model access        │
│  ├── WarehouseClient        # Fabric warehouse access               │
│  ├── LakehouseClient        # Fabric lakehouse access               │
│  └── FabricConnectors       # Unified interface                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Domain Layer

The domain layer contains business-specific implementations:

```
┌───────────────────────────────────────────────────────────────────┐
│                        DOMAIN LAYER (e.g., DonorManagement)       │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  tools/                                                           │
│  ├── __init__.py                  # Tool exports                  │
│  ├── donor_tools.py               # Donor-specific tools          │
│  ├── portfolio_tools.py           # Portfolio tools               │
│  └── campaign_tools.py            # Campaign tools                │
│                                                                   │
│  semantic_models/                                                 │
│  ├── __init__.py                  # Model exports                 │
│  ├── donor_model.py               # Donor semantic model access   │
│  └── revenue_model.py             # Revenue semantic model access │
│                                                                   │
│  tests/                                                           │
│  ├── unit/                        # Unit tests                    │
│  │   └── test_tools.py            # Tool unit tests               │
│  └── integration/                  # Integration tests            │
│      └── test_integration.py      # Integration tests             │
│                                                                   │
│  config/                                                          │
│  └── domain_config.py             # Domain-specific configuration │
│                                                                   │
│  main.py                                                          │
│  # Function App entry point with framework initialization         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### Request Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  Function   │────▶│   MCP       │────▶│   Domain    │
│ (MCP Client)│     │    App      │     │  Framework  │     │   Tools     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌───────────────┐     ┌─────────────┐
│  Request    │     │  HTTP       │     │ Authentication│     │  Tool       │
│ (MCP JSON)  │     │  Trigger    │     │ & Validation  │     │ Execution   │
└─────────────┘     └─────────────┘     └───────────────┘     └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Response   │◀────│  HTTP       │◀────│  Telemetry  │◀────│  Result     │
│ (MCP JSON)  │     │  Response   │     │  & Audit    │     │ (Processed) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Detailed Request Processing

```
1. Request Received
   ├─ HTTP request hits Function App
   ├─ Path-based routing (e.g., /GetDonorPortfolioHealth)
   └─ Request body parsed

2. Tool Lookup
   ├─ Tool name extracted from path
   ├─ Tool registry queried
   └─ Tool metadata retrieved

3. Authentication
   ├─ Authorization header extracted
   ├─ JWT token validated
   ├─ Identity established
   └─ Authentication result cached

4. Authorization
   ├─ Required permissions checked
   ├─ Required roles verified
   └─ Access decision made

5. Classification Check
   ├─ Tool classification level verified
   ├─ User clearance checked
   └─ Access allowed/denied

6. Tool Execution
   ├─ Tool function called with parameters
   ├─ Business logic executed
   └─ Result generated

7. Response Processing
   ├─ Result serialized
   ├─ Telemetry collected
   ├─ Audit log created
   └─ HTTP response returned

8. Observability
   ├─ Telemetry sent to Application Insights
   ├─ Audit log written to Blob Storage
   └─ Metrics and traces collected
```

## 🔒 Security Architecture

### Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │  Function   │     │   Entra ID  │
│             │     │    App      │     │             │
└──────────┬──┘     └──────────┬──┘     └──────────┬──┘
           │                   │                   │
           │  1. Get Token     │                   │
           │──────────────────▶│                   │
           │                   │  2. Authenticate  │
           │                   │──────────────────▶│
           │                   │                   │
           │                   │  3. Validate Token │
           │                   │◀──────────────────│
           │                   │                   │
           │  4. Access        │                   │
           │  Resource         │                   │
           │──────────────────▶│                   │
           │                   │                   │
           ▼                   ▼                   ▼
```

### Authorization Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Request   │     │   RBAC      │     │  Identity   │
│             │     │   Engine    │     │  Context    │
└──────────┬──┘     └──────────┬──┘     └──────────┬──┘
           │                   │                   │
           │  1. Check         │                   │
           │  Permissions      │                   │
           │──────────────────▶│                   │
           │                   │  2. Get User      │
           │                   │  Permissions      │
           │                   │──────────────────▶│
           │                   │                   │
           │                   │  3. Evaluate      │
           │                   │  Policies         │
           │                   │                   │
           │  4. Access        │                   │
           │  Decision         │                   │
           │◀──────────────────│                   │
           │                   │                   │
           ▼                   ▼                   ▼
```

### Data Classification Flow

```
┌─────────────┐     ┌───────────────┐     ┌─────────────┐
│   Tool      │     │ Classification│     │  Policy     │
│  Definition │     │   Engine      │     │  Store      │
└──────────┬──┘     └──────────┬────┘     └────────┬────┘
           │                   │                   │
           │  1. Get           │                   │
           │  Classification   │                   │
           │──────────────────▶│                   │
           │                   │  2. Load          │
           │                   │  Policies         │
           │                   │──────────────────▶│
           │                   │                   │
           │                   │  3. Enforce       │
           │                   │  Policies         │
           │                   │                   │
           │  4. Allow/Deny    │                   │
           │  Access           │                   │
           │◀──────────────────│                   │
           │                   │                   │
           ▼                   ▼                   ▼
```

## 📊 Observability Architecture

### Telemetry Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Tool      │     │ Telemetry   │     │ Application │
│  Execution  │     │ Collector   │     │  Insights   │
└──────────┬──┘     └──────────┬──┘     └──────────┬──┘
           │                   │                   │
           │  1. Track         │                   │
           │  Execution        │                   │
           │──────────────────▶│                   │
           │                   │  2. Buffer        │
           │                   │  Metrics          │
           │                   │                   │
           │                   │  3. Export        │
           │                   │──────────────────▶│
           │                   │                   │
           │                   │  4. Flush         │
           │                   │  (Periodic)       │
           │                   │                   │
           ▼                   ▼                   ▼
```

### Audit Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Tool      │     │ Audit       │     │ Azure Blob  │
│  Execution  │     │ Logger      │     │ Storage     │
└──────────┬──┘     └──────────┬──┘     └──────────┬──┘
           │                   │                   │
           │  1. Log           │                   │
           │  Access           │                   │
           │──────────────────▶│                   │
           │                   │  2. Create        │
           │                   │  Audit Record     │
           │                   │                   │
           │                   │  3. Write         │
           │                   │──────────────────▶│
           │                   │                   │
           │                   │  4. Flush         │
           │                   │  (Periodic)       │
           │                   │                   │
           ▼                   ▼                   ▼
```

## 🔗 Fabric Connectivity Architecture

### Semantic Model Access

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Domain    │     │ Semantic    │     │ Power BI    │
│   Tool      │     │ Model       │     │ REST API    │
└──────────┬──┘     │ Client      │     │             │
           │        └──────────┬──┘     └──────────┬──┘
           │                   │                   │
           │  1. Execute       │                   │
           │  Query            │                   │
           │──────────────────▶│                   │
           │                   │  2. Translate     │
           │                   │  to DAX/XMLA      │
           │                   │──────────────────▶│
           │                   │                   │
           │                   │  3. Get Results   │
           │                   │◀──────────────────│
           │                   │                   │
           │  4. Return        │                   │
           │  Data             │                   │
           │◀──────────────────│                   │
           │                   │                   │
           ▼                   ▼                   ▼
```

### Warehouse Access

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Domain    │     │ Warehouse   │     │ Fabric SQL  │
│   Tool      │     │ Client      │     │ Endpoint    │
└──────────┬──┘     └──────────┬──┘     └──────────┬──┘
           │                   │                   │
           │  1. Execute       │                   │
           │  SQL Query        │                   │
           │──────────────────▶│                   │
           │                   │  2. Connect to    │
           │                   │  Endpoint         │
           │                   │──────────────────▶│
           │                   │                   │
           │                   │  3. Execute       │
           │                   │  Query            │
           │                   │──────────────────▶│
           │                   │                   │
           │  4. Return        │                   │
           │  Results          │                   │
           │◀──────────────────│                   │
           │                   │                   │
           ▼                   ▼                   ▼
```

## 📁 File Structure

```
mcp-platform-framework/
├── platform/                    # Core platform modules
│   ├── __init__.py             # Platform exports
│   ├── auth/                  # Authentication module
│   │   ├── __init__.py
│   │   ├── models.py          # Token claims, identity models
│   │   ├── exceptions.py      # Authentication exceptions
│   │   ├── jwt_validation.py  # JWT token validation
│   │   ├── entra_id.py        # Entra ID authenticator
│   │   ├── managed_identity.py # Managed Identity authenticator
│   │   └── decorators.py      # Authentication decorators
│   │
│   ├── authorization/        # Authorization module
│   │   ├── __init__.py
│   │   ├── models.py          # RBAC models
│   │   ├── rbac.py            # RBAC engine
│   │   └── decorators.py      # Authorization decorators
│   │
│   ├── telemetry/            # Telemetry module
│   │   ├── __init__.py
│   │   ├── models.py          # Telemetry data models
│   │   ├── collector.py       # Telemetry collector
│   │   ├── exporter.py        # Telemetry exporters
│   │   └── decorators.py      # Telemetry decorators
│   │
│   ├── audit/                # Audit module
│   │   ├── __init__.py
│   │   ├── models.py          # Audit record models
│   │   ├── logger.py          # Audit logger
│   │   ├── storage.py         # Audit storage backends
│   │   └── decorators.py      # Audit decorators
│   │
│   ├── errors/               # Error handling module
│   │   ├── __init__.py
│   │   ├── models.py          # Error models
│   │   ├── exceptions.py      # Exception hierarchy
│   │   └── handlers.py        # Error handlers
│   │
│   ├── config/               # Configuration module
│   │   ├── __init__.py
│   │   ├── models.py          # Configuration models
│   │   ├── loader.py          # Configuration loader
│   │   ├── manager.py         # Configuration manager
│   │   └── keyvault.py        # Key Vault client
│   │
│   ├── classification/       # Classification module
│   │   ├── __init__.py
│   │   ├── models.py          # Classification models
│   │   ├── controls.py        # Classification controls
│   │   └── decorators.py      # Classification decorators
│   │
│   ├── registration/         # Registration module
│   │   ├── __init__.py
│   │   ├── models.py          # Tool metadata models
│   │   ├── registry.py        # Tool registry
│   │   ├── decorators.py      # Tool decorators
│   │   └── discovery.py       # Tool discovery
│   │
│   ├── connectivity/         # Connectivity module
│   │   ├── __init__.py
│   │   ├── fabric_client.py   # Fabric client
│   │   ├── semantic_models.py # Semantic model client
│   │   ├── warehouse.py       # Warehouse client
│   │   ├── lakehouse.py       # Lakehouse client
│   │   └── connectors.py      # Unified connectors
│   │
│   ├── template/             # Template system
│   │   ├── __init__.py
│   │   ├── domain_template.py # Domain template
│   │   └── template_generator.py # Template generator
│   │
│   └── framework.py          # Main framework integration
│
├── azure_functions/           # Function App configuration
│   ├── __init__.py
│   ├── function.json          # Function binding configuration
│   ├── mcp_http_trigger/     # HTTP trigger
│   │   └── __init__.py
│   └── mcp_tool_trigger/     # Tool trigger
│       └── __init__.py
│
├── deployment/                # Deployment templates
│   ├── __init__.py
│   ├── parameters.py          # Deployment parameters
│   ├── arm_template.py        # ARM template generator
│   └── bicep_template.py      # Bicep template generator
│
├── pipelines/                 # CI/CD pipelines
│   ├── __init__.py
│   ├── pipeline_config.py     # Pipeline configuration
│   ├── azure_devops_pipeline.py # Azure DevOps generator
│   └── github_actions_pipeline.py # GitHub Actions generator
│
├── docs/                      # Documentation
├── tests/                     # Tests
├── examples/                  # Example domains
├── main.py                    # Function App entry point
└── requirements.txt           # Dependencies
```

## 🎯 Next Steps

- **[Design Principles](principles.md)** - Deep dive into the design philosophy
- **[Component Details](components.md)** - Detailed architecture of each component
- **[Data Flow](data-flow.md)** - How data moves through the system
- **[Security Architecture](security.md)** - Comprehensive security design

---

**🏗️ Architecture Summary**

The MCP Platform Framework provides a robust, enterprise-grade foundation for building MCP services on Microsoft Azure. With its strict separation of concerns, comprehensive security features, and seamless Fabric integration, the framework enables domain developers to focus on business capabilities while the platform handles all infrastructure concerns.

**Key Takeaways:**
- ✅ **Separation of Concerns**: Domains own business, platform owns infrastructure
- ✅ **No Forking**: All domains use the same central template
- ✅ **Security by Default**: Authentication, authorization, classification enabled
- ✅ **Observability First**: Automatic telemetry and audit logging
- ✅ **Fabric Native**: Seamless integration with Microsoft Fabric services
