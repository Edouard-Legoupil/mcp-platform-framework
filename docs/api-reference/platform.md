# 🏗️ Platform API Reference

The Platform API provides the core framework classes, initialization, and integration points for the MCP Platform Framework.

## 🎯 Overview

The Platform API is the foundation of the MCP Platform Framework, providing:

- **Framework Initialization**: Configure and initialize the platform
- **Tool Registration**: Automatic discovery and registration of MCP tools
- **Request Handling**: Process incoming MCP requests
- **Integration Points**: Extend and customize framework behavior
- **Lifecycle Management**: Startup and shutdown hooks

## 🏗️ Core Classes

### MCPFramework

The main framework class that orchestrates all platform modules.

**Class Signature:**
```python
class MCPFramework:
    def __init__(
        self,
        domain: str,
        environment: str = "dev",
        config: Optional[FrameworkConfig] = None
    ):
        """
        Initialize the MCP Platform Framework.
        
        Args:
            domain: The domain name (e.g., "DonorManagement", "Finance")
            environment: Deployment environment (dev, test, prod)
            config: Optional framework configuration
        """
```

**Methods:**

#### `initialize()`
Initialize all platform modules and prepare for request handling.

```python
def initialize(self) -> None:
    """Initialize all platform modules."""
```

**Example:**
```python
from platform.framework import MCPFramework

# Initialize the framework
framework = MCPFramework(
    domain="DonorManagement",
    environment="prod"
)
framework.initialize()
```

#### `register_tools()`
Discover and register all tools from the specified module.

```python
def register_tools(self, module: ModuleType) -> List[ToolMetadata]:
    """
    Discover and register all tools from a module.
    
    Args:
        module: Python module containing tool functions
        
    Returns:
        List of registered tool metadata
    """
```

**Example:**
```python
import my_domain.tools
from platform.framework import MCPFramework

framework = MCPFramework(domain="MyDomain")
registered_tools = framework.register_tools(my_domain.tools)
```

#### `handle_request()`
Process an incoming MCP request.

```python
async def handle_request(
    self,
    request: MCPRequest
) -> MCPResponse:
    """
    Process an incoming MCP request.
    
    Args:
        request: Incoming MCP request
        
    Returns:
        MCP response with results or errors
    """
```

**Example:**
```python
from platform.framework import MCPFramework
from platform.models import MCPRequest

framework = MCPFramework(domain="DonorManagement")

# Process a request
request = MCPRequest(
    tool_name="GetDonorPortfolio",
    arguments={"donor_id": "12345"},
    context={}
)

response = await framework.handle_request(request)
```

#### `shutdown()`
Gracefully shutdown the framework and all modules.

```python
def shutdown(self) -> None:
    """Gracefully shutdown the framework."""
```

### FrameworkConfig

Configuration class for the MCP Platform Framework.

**Class Signature:**
```python
@dataclass
class FrameworkConfig:
    domain: str
    environment: str = "dev"
    
    # Authentication Configuration
    auth_enabled: bool = True
    entra_id_config: Optional[EntraIDConfig] = None
    managed_identity_enabled: bool = True
    
    # Telemetry Configuration
    telemetry_enabled: bool = True
    app_insights_connection_string: Optional[str] = None
    
    # Audit Configuration
    audit_enabled: bool = True
    audit_storage_account: Optional[str] = None
    audit_container: str = "audit-logs"
    
    # Classification Configuration
    classification_enabled: bool = True
    default_classification: Classification = Classification.INTERNAL
    
    # Connectivity Configuration
    fabric_enabled: bool = True
    semantic_model_endpoint: Optional[str] = None
    
    # Registration Configuration
    auto_discovery_enabled: bool = True
    tool_modules: List[str] = field(default_factory=list)
```

**Example:**
```python
from platform.framework import FrameworkConfig
from platform.auth.config import EntraIDConfig

config = FrameworkConfig(
    domain="DonorManagement",
    environment="prod",
    auth_enabled=True,
    entra_id_config=EntraIDConfig(
        tenant_id="your-tenant-id",
        client_id="your-client-id",
        audience="api://mcp-platform"
    ),
    telemetry_enabled=True,
    app_insights_connection_string="InstrumentationKey=..."
)
```

## 🔧 Framework Integration

### Tool Discovery

The framework automatically discovers tools decorated with `@tool` decorator.

**Example:**
```python
from platform.registration import tool

@tool(
    name="GetDonorPortfolio",
    description="Retrieve donor portfolio information",
    classification="CONFIDENTIAL"
)
def get_donor_portfolio(donor_id: str) -> Dict:
    # Tool implementation
    return donor_service.get_portfolio(donor_id)
```

### Module Integration

All platform modules are automatically integrated and available through the framework.

**Example:**
```python
from platform.framework import MCPFramework

framework = MCPFramework(domain="DonorManagement")

# Access authentication service
auth_service = framework.auth_service

# Access telemetry service
telemetry_service = framework.telemetry_service

# Access audit service
audit_service = framework.audit_service
```

## 📊 Platform Models

### MCPRequest

Represents an incoming MCP request.

```python
@dataclass
class MCPRequest:
    tool_name: str
    arguments: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

### MCPResponse

Represents an MCP response.

```python
@dataclass
class MCPResponse:
    request_id: str
    results: Any
    status: str = "success"
    error: Optional[MCPError] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
```

### MCPError

Standard error format for MCP responses.

```python
@dataclass
class MCPError:
    error_code: str
    category: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

## 🚀 Quick Start

### Basic Framework Setup

```python
from platform.framework import MCPFramework

# Initialize framework
framework = MCPFramework(
    domain="DonorManagement",
    environment="dev"
)

# Initialize all modules
framework.initialize()

# Register tools from your domain
import donor_management.tools
framework.register_tools(donor_management.tools)

# Start processing requests
# (In Azure Functions, this would be triggered by HTTP requests)
```

### Azure Function Integration

```python
from platform.framework import MCPFramework
from platform.azure import AzureFunctionHandler
import azure.functions as func

# Initialize framework
framework = MCPFramework(domain="DonorManagement")
framework.initialize()

# Create Azure Function handler
handler = AzureFunctionHandler(framework)

def main(req: func.HttpRequest) -> func.HttpResponse:
    return handler.handle_request(req)
```

## 🔧 Configuration

### Environment Variables

```bash
# Framework Configuration
MCP_DOMAIN=DonorManagement
MCP_ENVIRONMENT=prod

# Module Configuration
MCP_AUTH_ENABLED=true
MCP_TELEMETRY_ENABLED=true
MCP_AUDIT_ENABLED=true
MCP_CLASSIFICATION_ENABLED=true

# Azure Configuration
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

### Configuration File

```yaml
# config/framework.yaml
framework:
  domain: DonorManagement
  environment: prod
  
  modules:
    auth:
      enabled: true
      entra_id:
        tenant_id: your-tenant-id
        client_id: your-client-id
        audience: api://mcp-platform
    
    telemetry:
      enabled: true
      connection_string: InstrumentationKey=...
    
    audit:
      enabled: true
      storage_account: mystorageaccount
      container: audit-logs
```

## ⭐ Best Practices

### Framework Initialization

✅ **Initialize Early**
```python
# Good: Initialize framework at application startup
framework = MCPFramework(domain="DonorManagement")
framework.initialize()
```

❌ **Avoid Late Initialization**
```python
# Bad: Initialize framework on first request
def handle_request(request):
    framework = MCPFramework(domain="DonorManagement")  # Too late!
    framework.initialize()
```

### Error Handling

✅ **Use Framework Error Handling**
```python
from platform.errors import FrameworkError

try:
    framework.initialize()
except FrameworkError as e:
    logger.error(f"Framework initialization failed: {e.error_code}")
    raise
```

### Performance Optimization

✅ **Lazy Load Modules**
```python
# Good: Only initialize modules you need
framework = MCPFramework(
    domain="DonorManagement",
    config=FrameworkConfig(
        telemetry_enabled=False,  # Disable if not needed
        audit_enabled=False       # Disable if not needed
    )
)
```

## 🔍 Troubleshooting

### Common Issues

**Framework initialization fails with authentication errors**
- Check that `AZURE_TENANT_ID` and `AZURE_CLIENT_ID` are set
- Verify that the Managed Identity has the required permissions
- Ensure the audience matches your API's expected audience

**Tools are not being discovered**
- Verify that tools are decorated with `@tool` decorator
- Check that the module is passed to `register_tools()`
- Ensure the module is importable (no syntax errors)

**Requests are timing out**
- Check Application Insights for performance metrics
- Verify that all required modules are initialized
- Check for blocking operations in tool implementations

## 📚 Related Documentation

- [Authentication API](authentication.md) - Authentication services
- [Authorization API](authorization.md) - Authorization services
- [Telemetry API](telemetry.md) - Observability services
- [Audit API](audit.md) - Compliance logging
- [Connectivity API](connectivity.md) - Fabric integration
- [Decorators](decorators.md) - Framework decorators

---

**🎉 Ready to build with the Platform API?** Start with the framework initialization and tool registration examples above.

**Need more details?** Check the module-specific API references for detailed information about each service.