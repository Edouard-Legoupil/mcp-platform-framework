# MCP Platform Framework

## Overview

The MCP Platform Framework provides a comprehensive infrastructure layer for implementing MCP (Model Context Protocol) domains, enforcing strict separation between platform concerns and domain business capabilities.

## Principles

### Domain Ownership
- **Domains own business capabilities**: Business logic, ontologies, semantic definitions
- **Platform owns everything else**: Authentication, authorization, telemetry, error handling, connectivity
- **No domain forking**: All domains use the same template from this central repository

### Key Benefits
- **Prevents integration sprawl**: Clear separation prevents the MCP ecosystem from becoming the next generation of enterprise integration complexity
- **Consistent infrastructure**: All domains benefit from the same robust platform services
- **Rapid development**: Domain developers focus on business logic, not infrastructure
- **Governance and compliance**: Built-in support for audit, security, and data classification

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Platform Framework                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Authentication│  │ Authorization │  │  Telemetry   │        │
│  │  (Entra ID,  │  │   (RBAC,     │  │ (Auto-collect│        │
│  │   JWT, etc.) │  │  Policies)    │  │  tool calls) │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Audit      │  │   Error       │  │ Classification│        │
│  │  (Immutable  │  │  Handling     │  │  (Data        │        │
│  │   logs)      │  │  (Standardized│  │   controls)   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Connectivity Layer                      ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ││
│  │  │ Semantic    │  │  Warehouse    │  │  Lakehouse    │  ││
│  │  │  Models     │  │  (SQL)        │  │  (Delta)      │  ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Tool Registration                        ││
│  │  - Auto-discovery from domain modules                     ││
│  │  - Metadata generation                                     ││
│  │  - MCP server integration                                  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Domain Repositories                         │
│  (Created from template - no forking between domains)          │
│                                                               │
│  mcp-donor-management-domain/                                │
│  ├── tools/                  # Domain-specific tools          │
│  ├── semantic_models/        # Semantic model access          │
│  ├── tests/                 # Domain tests                   │
│  ├── docs/                  # Domain documentation           │
│  ├── config/                # Environment configs            │
│  ├── metadata/              # Domain metadata                │
│  └── pipelines/             # CI/CD pipelines                │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install the Framework

```bash
# Clone the platform framework
git clone https://github.com/your-org/mcp-platform-framework.git
cd mcp-platform-framework

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### 2. Create a Domain Repository

```bash
# Use the template generator
python -m platform.template create_domain DonorManagement \
    "Manages donor information and analytics" \
    "DER Team"

# Or programmatically
from platform.template import DomainGenerator

generator = DomainGenerator()
generator.create_domain(
    name="DonorManagement",
    description="Manages donor information and analytics",
    owner="DER Team"
)
```

### 3. Develop Domain Tools

```python
# In mcp-donor-management-domain/tools.py

from platform.registration import tool
from platform.auth import authenticated_tool, requires_permission
from platform.telemetry import track_tool_telemetry
from platform.audit import audit_tool_access
from platform.classification import classification
from platform.connectivity import semantic_model_execute

@tool(domain="DonorManagement")
@authenticated_tool
@requires_permission("donor.read")
@track_tool_telemetry(domain="DonorManagement")
@audit_tool_access(resource="GetDonorPortfolioHealth", domain="DonorManagement")
@classification("CONFIDENTIAL")
def get_donor_portfolio_health(donor_id: str) -> dict:
    """
    Get the health status of a donor's portfolio
    """
    # Use semantic model for business metrics
    result = semantic_model_execute(
        model_name="DonorSemanticModel",
        query=f"Donor Portfolio Health for Donor {donor_id}"
    )
    
    return {
        "donor_id": donor_id,
        "health_score": result.data[0]["health_score"],
        "risk_level": result.data[0]["risk_level"]
    }
```

### 4. Start the MCP Server

```bash
# Start the server with all domains
python -m platform.main --config config.yaml --serve --port 8080
```

## Platform Modules

### Authentication
- **Entra ID Integration**: Microsoft Entra ID (Azure AD) authentication
- **JWT Validation**: Automatic JWT token validation
- **Managed Identity**: Azure Managed Identity support
- **OAuth2 Handling**: OAuth2 authentication flows

```python
from platform.auth import authenticated_tool, requires_permission

@authenticated_tool
def public_tool():
    pass

@requires_permission("donor.read")
def read_donor_data():
    pass
```

### Authorization
- **Enterprise RBAC**: Role-Based Access Control
- **Permission Decorators**: Easy permission checking
- **Policy Enforcement**: Complex policy evaluation

```python
from platform.authorization import requires_permission

@requires_permission("donor.analyze")
def analyze_donor_data():
    pass
```

### Telemetry
- **Automatic Collection**: Every call generates standard telemetry
- **Tool Name**: Automatically captured
- **Requester Identity**: User information captured
- **Duration**: Execution time measured
- **Status**: Success/failure tracking

```python
from platform.telemetry import track_tool_telemetry

@track_tool_telemetry(tool_name="GetDonorPortfolioHealth", domain="DonorManagement")
def get_donor_portfolio_health():
    pass
```

### Audit Logging
- **Immutable Records**: Tamper-proof audit logs
- **Sensitive Access**: Automatic logging of sensitive queries

```python
from platform.audit import audit_tool_access

@audit_tool_access(resource="GetTopDonorContributions", domain="DonorManagement")
def get_top_donor_contributions():
    pass
```

### Error Handling
- **Standardized Errors**: Consistent error structures
- **Error Codes**: Unique error codes for each error type

```python
from platform.errors import DataAccessException

raise DataAccessException("Access denied", "DONOR-001")
```

### Data Classification
- **Classification Levels**: PUBLIC, INTERNAL, CONFIDENTIAL, STRICTLY_CONFIDENTIAL
- **Governance Policies**: Enforce policies through framework controls

```python
from platform.classification import classification

@classification("CONFIDENTIAL")
def GetFundingPipelineRisk():
    pass
```

### Tool Registration
- **Automatic Discovery**: Tools are automatically discovered from domain modules
- **Metadata Generation**: Tool metadata is automatically generated

```python
from platform.registration import tool

@tool(domain="DonorManagement")
def GetDonorPortfolioHealth():
    pass
```

### Fabric Connectivity
- **Semantic Models**: Encourage business metrics consumption through semantic models
- **Warehouses**: Standardized warehouse connectors
- **Lakehouses**: Lakehouse connectivity

```python
from platform.connectivity import semantic_model_execute

result = semantic_model_execute(
    model_name="FinanceSemanticModel",
    query="Total Revenue by Region"
)
```

### Configuration Management
- **Environment-Aware**: Separate configurations for DEV, TEST, PROD
- **Key Vault Integration**: Standardized retrieval of secrets

```python
from platform.config import get_config_value, get_secret

timeout = get_config_value("request_timeout", default=30)
db_password = get_secret("database_password", domain="DonorManagement")
```

## Repository Strategy

- **Central Repository**: `mcp-platform-framework` contains all platform code
- **Domain Repositories**: Created from the template (e.g., `mcp-donor-management-domain`)
- **No Forking**: Domains do not fork each other and do not create custom frameworks

## Configuration

### Platform Configuration

```yaml
# config.yaml
platform:
  environment: Dev
  auth_enabled: true
  auth_provider: entra_id
  telemetry_enabled: true
  audit_enabled: true
  
  connections:
    - name: FinanceSemanticModel
      connection_type: semantic_model
      connection_string: powerbi://dev-finance-model

domains:
  DonorManagement:
    settings:
      max_retries: 3
    connections:
      - name: DonorSemanticModel
        connection_type: semantic_model
    secrets:
      api_key:
        source: keyvault
        name: donor-api-key
```

## CI/CD Pipeline

Each domain receives a pipeline out-of-the-box with:
- Build validation
- Testing (unit, integration, performance, security)
- Security scanning
- Deployment

## Security

- **Authentication**: Entra ID, JWT, Managed Identity, OAuth2
- **Authorization**: RBAC with permission decorators
- **Audit Logging**: Immutable logs for sensitive access
- **Data Classification**: Enforcement of classification levels
- **Secret Management**: Key Vault integration, no embedded credentials

## Support

For issues, questions, or contributions, please contact the platform team.

## License

This project is licensed under the MIT License.
