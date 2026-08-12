# 🏗️ Framework Integration Module

## Overview

The **Framework Integration Module** provides the core infrastructure for the MCP Platform Framework, including tool registration, dependency injection, lifecycle management, and integration with the MCP server.

## 🎯 Core Components

### 1. MCPFramework Class

The main class that orchestrates all framework components.

```python
from mcp_framework.platform import MCPFramework

# Initialize the framework
framework = MCPFramework()

# Configure framework
framework.configure(
    environment="production",
    debug=False,
    log_level="INFO"
)

# Start the framework
framework.start()

# Stop the framework
framework.stop()
```

### 2. Tool Registration System

Automatic and manual tool registration with metadata extraction.

```python
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

# Manual tool registration
@framework.tool(name="MyTool", description="My tool description")
def my_tool(param1: str, param2: int = 10) -> dict:
    return {"result": f"{param1} - {param2}"}

# Auto-discover and register tools from a module
framework.register_tools_from_module("my_domain.tools")

# Register multiple tools at once
framework.register_tools([tool1, tool2, tool3])
```

## 📋 Configuration

### Framework Configuration

**Configuration Options:**

```python
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

# Set configuration
framework.config.set({
    "environment": "production",
    "debug": False,
    "log_level": "INFO",
    "azure": {
        "subscription_id": "your-subscription-id",
        "resource_group": "mcp-platform-rg"
    },
    "fabric": {
        "tenant_id": "your-tenant-id",
        "workspace_id": "your-workspace-id"
    }
})

# Get configuration values
environment = framework.config.get("environment")
subscription_id = framework.config.get("azure.subscription_id")
```

### Environment Configuration

**Environment Detection:**

```python
# Environment is automatically detected from:
# 1. MCP_ENVIRONMENT environment variable
# 2. AZURE_ENVIRONMENT environment variable
# 3. Default: "development"

environment = framework.get_environment()
print(f"Current environment: {environment}")
```

**Environment-Specific Configuration:**

```python
# Load environment-specific configuration
framework.load_environment_config("production")

# Or automatically load based on current environment
framework.load_environment_config()
```

## 🔌 Dependency Injection

### Service Container

```python
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

# Register services in the container
framework.container.register("fabric_client", FabricClient)
framework.container.register("auth_service", AuthService)
framework.container.register("telemetry", TelemetryClient)

# Resolve services
fabric_client = framework.container.resolve("fabric_client")
auth_service = framework.container.resolve("auth_service")
```

### Singleton Services

```python
# Register singleton services
framework.container.register_singleton("config", Config)
framework.container.register_singleton("logger", Logger)

# Resolve the same instance every time
config1 = framework.container.resolve("config")
config2 = framework.container.resolve("config")
assert config1 is config2  # Same instance
```

### Factory Services

```python
# Register factory functions
def create_fabric_client():
    return FabricClient(
        tenant_id=framework.config.get("fabric.tenant_id"),
        workspace_id=framework.config.get("fabric.workspace_id")
    )

framework.container.register_factory("fabric_client", create_fabric_client)

# Each resolution creates a new instance
client1 = framework.container.resolve("fabric_client")
client2 = framework.container.resolve("fabric_client")
assert client1 is not client2  # Different instances
```

## 📦 Tool Management

### Tool Discovery

**Automatic Tool Discovery:**

```python
# Discover and register tools from a directory
framework.discover_tools("my_domain/tools")

# Discover tools with specific patterns
framework.discover_tools("my_domain/tools", pattern="*.py")

# Discover tools recursively
framework.discover_tools("my_domain", recursive=True)
```

**Tool Discovery Configuration:**

```python
framework.configure_tool_discovery(
    paths=["tools", "src/tools"],
    pattern="*.py",
    recursive=True,
    exclude=["tests", "__pycache__"],
    auto_register=True
)
```

### Tool Metadata

**Metadata Extraction:**

```python
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

# Extract metadata from docstrings
@framework.tool
def my_tool(param: str) -> dict:
    """
    My tool description.
    
    Args:
        param: The parameter description
        
    Returns:
        Dictionary with results
        
    Examples:
        >>> my_tool("test")
        {'result': 'test'}
    """
    return {"result": param}

# Tool will have metadata extracted from docstring
```

**Manual Metadata:**

```python
@framework.tool(
    name="CustomToolName",
    description="Custom tool description",
    parameters={
        "param1": {"type": "string", "description": "First parameter"},
        "param2": {"type": "int", "description": "Second parameter", "default": 10}
    },
    returns={"type": "dict", "description": "Tool result"},
    tags=["tag1", "tag2"],
    classification="CONFIDENTIAL"
)
def custom_tool(param1: str, param2: int = 10) -> dict:
    return {"param1": param1, "param2": param2}
```

### Tool Lifecycle

**Tool Initialization:**

```python
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

@framework.tool(init=True)
def init_tool():
    """Called when the tool is initialized"""
    print("Tool initialized")

@framework.tool(cleanup=True)
def cleanup_tool():
    """Called when the tool is being cleaned up"""
    print("Tool cleanup")
```

**Tool Validation:**

```python
@framework.tool(validate=True)
def validate_tool_input(param: str) -> bool:
    """Validate tool input"""
    return len(param) > 0
```

## 🔄 Lifecycle Management

### Framework Lifecycle

```python
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

# Lifecycle hooks
@framework.on_startup
def on_framework_startup():
    """Called when the framework starts"""
    print("Framework starting...")

@framework.on_shutdown
def on_framework_shutdown():
    """Called when the framework shuts down"""
    print("Framework shutting down...")

@framework.on_error
def on_framework_error(error: Exception):
    """Called when an error occurs in the framework"""
    print(f"Framework error: {error}")
```

### Tool Lifecycle

```python
@framework.tool
class MyToolClass:
    """Tool implemented as a class"""
    
    def __init__(self):
        """Constructor - called when tool is registered"""
        self.initialized = False
    
    def __call__(self, param: str) -> dict:
        """Called when tool is invoked"""
        if not self.initialized:
            self.setup()
            self.initialized = True
        return self.execute(param)
    
    def setup(self):
        """Setup - called before first invocation"""
        print("Tool setup")
    
    def execute(self, param: str) -> dict:
        """Execute - main tool logic"""
        return {"result": param}
    
    def cleanup(self):
        """Cleanup - called when framework shuts down"""
        print("Tool cleanup")
```

## 🌐 MCP Server Integration

### Server Configuration

```python
from mcp_framework.platform import MCPFramework
from mcp_framework.server import MCPServer

# Initialize framework
framework = MCPFramework()

# Configure MCP server
server = MCPServer(framework)

# Set server configuration
server.configure(
    host="0.0.0.0",
    port=8080,
    debug=True,
    cors_origins=["*"],
    max_connections=100,
    timeout=30
)

# Start the server
server.start()

# Stop the server
server.stop()
```

### Server Hooks

```python
from mcp_framework.server import MCPServer

server = MCPServer()

@server.on_start
def on_server_start():
    """Called when the server starts"""
    print("MCP Server started")

@server.on_stop
def on_server_stop():
    """Called when the server stops"""
    print("MCP Server stopped")

@server.on_request
def on_server_request(request):
    """Called for each incoming request"""
    print(f"Request received: {request.method} {request.path}")

@server.on_error
def on_server_error(error: Exception, request):
    """Called when an error occurs during request processing"""
    print(f"Error processing request: {error}")
```

### Server Middleware

```python
from mcp_framework.server import MCPServer

server = MCPServer()

# Add middleware
@server.middleware
def logging_middleware(request, call_next):
    """Log all requests"""
    print(f"Request: {request.method} {request.path}")
    response = call_next(request)
    print(f"Response: {response.status_code}")
    return response

@server.middleware
def timing_middleware(request, call_next):
    """Measure request processing time"""
    import time
    start_time = time.time()
    response = call_next(request)
    end_time = time.time()
    print(f"Request took {end_time - start_time:.2f} seconds")
    return response
```

## 📊 Monitoring and Metrics

### Framework Metrics

```python
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

# Get framework metrics
metrics = framework.get_metrics()
print(f"Registered tools: {metrics['tools_registered']}")
print(f"Active connections: {metrics['active_connections']}")
print(f"Total requests: {metrics['total_requests']}")
print(f"Error rate: {metrics['error_rate']}")
```

### Health Checks

```python
# Add health check endpoint
@framework.health_check
def check_database_health() -> bool:
    """Check database connectivity"""
    try:
        # Test database connection
        return True
    except Exception:
        return False

@framework.health_check
def check_fabric_health() -> bool:
    """Check Fabric connectivity"""
    try:
        # Test Fabric connection
        return True
    except Exception:
        return False

# Get health status
health = framework.get_health_status()
print(f"Overall health: {health['status']}")
print(f"Checks: {health['checks']}")
```

## 🔐 Security Integration

### Authentication Integration

```python
from mcp_framework.platform import MCPFramework
from mcp_framework.auth import AuthService

framework = MCPFramework()

# Configure authentication
auth_service = AuthService(
    providers=["entra_id", "managed_identity"],
    require_authentication=True,
    allowed_audiences=["api://mcp-platform"]
)

framework.integrate_authentication(auth_service)

# Check authentication
is_authenticated = framework.auth.is_authenticated()
user_info = framework.auth.get_user_info()
```

### Authorization Integration

```python
from mcp_framework.platform import MCPFramework
from mcp_framework.authorization import AuthZService

framework = MCPFramework()

# Configure authorization
authz_service = AuthZService(
    rbac_enabled=True,
    roles={
        "donor_analyst": {
            "permissions": ["donor.read", "donor.analytics"],
            "description": "Access to donor data and analytics"
        }
    }
)

framework.integrate_authorization(authz_service)

# Check permissions
can_read = framework.authz.has_permission("donor.read")
can_write = framework.authz.has_permission("donor.write")
```

## 📝 Logging

### Framework Logging

```python
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

# Configure logging
framework.configure_logging(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=["console", "file", "application_insights"]
)

# Log messages
framework.logger.debug("Debug message")
framework.logger.info("Info message")
framework.logger.warning("Warning message")
framework.logger.error("Error message")
framework.logger.critical("Critical message")
```

### Structured Logging

```python
# Log with structured data
framework.logger.info(
    "Tool executed",
    extra={
        "tool": "GetDonor",
        "donor_id": "D001",
        "duration_ms": 450,
        "status": "success"
    }
)

# Log with context
with framework.logger.context({"request_id": "req-123", "user": "user@domain.com"}):
    framework.logger.info("Processing request")
```

## 🛡️ Error Handling

### Framework Error Handling

```python
from mcp_framework.platform import MCPFramework
from mcp_framework.error_handling import MCPError, ErrorCodes

framework = MCPFramework()

# Configure error handling
framework.configure_error_handling(
    default_category="FrameworkError",
    log_errors=True,
    report_to_telemetry=True,
    include_stack_trace=True
)

# Handle errors
@framework.on_error
def handle_framework_error(error: Exception, context: dict):
    """Custom error handler"""
    framework.logger.error(
        f"Framework error: {error}",
        extra={"context": context, "type": type(error).__name__}
    )
    
    # Report to monitoring
    framework.telemetry.track_exception(error)
```

### Custom Error Types

```python
from mcp_framework.error_handling import MCPError, ErrorCodes

# Define custom error codes
class DonorErrorCodes:
    DONOR_NOT_FOUND = "DONOR-001"
    DONOR_ACCESS_DENIED = "DONOR-002"
    DONOR_CREATION_FAILED = "DONOR-003"
    DONOR_UPDATE_FAILED = "DONOR-004"
    DONOR_DELETION_FAILED = "DONOR-005"

# Raise custom errors
raise MCPError(
    error_code=DonorErrorCodes.DONOR_NOT_FOUND,
    message="Donor with specified ID not found",
    category="DataNotFound",
    severity="MEDIUM",
    http_status=404
)
```

## 📁 File Structure

```
mcp_framework/
├── platform/
│   ├── __init__.py          # Main exports
│   ├── framework.py         # MCPFramework class
│   ├── config.py            # Configuration management
│   ├── container.py         # Dependency injection container
│   ├── lifecycle.py         # Lifecycle management
│   ├── server.py            # MCP server integration
│   ├── metrics.py           # Metrics and monitoring
│   ├── health.py            # Health checks
│   └── errors.py            # Error handling
│
└── __init__.py              # Package exports
```

## 📚 API Reference

### MCPFramework Class

**Attributes:**
- `config` - Configuration manager
- `container` - Dependency injection container
- `logger` - Logger instance
- `telemetry` - Telemetry client
- `auth` - Authentication service
- `authz` - Authorization service
- `tools` - Registered tools registry

**Methods:**
- `configure(**kwargs)` - Configure the framework
- `start()` - Start the framework
- `stop()` - Stop the framework
- `register_tool(tool)` - Register a tool
- `register_tools(tools)` - Register multiple tools
- `discover_tools(path)` - Discover and register tools
- `get_environment()` - Get current environment
- `get_metrics()` - Get framework metrics
- `get_health_status()` - Get health status

### Configuration Methods

- `config.set(key, value)` - Set configuration value
- `config.get(key, default=None)` - Get configuration value
- `config.get_required(key)` - Get required configuration value
- `config.has(key)` - Check if configuration key exists
- `config.load(file_path)` - Load configuration from file
- `config.save(file_path)` - Save configuration to file

### Container Methods

- `container.register(name, service)` - Register a service
- `container.register_singleton(name, service)` - Register a singleton service
- `container.register_factory(name, factory)` - Register a factory function
- `container.resolve(name)` - Resolve a service
- `container.has(name)` - Check if service is registered
- `container.unregister(name)` - Unregister a service

## 🛠️ Best Practices

1. **⭐ Use Dependency Injection** - Register services in the container for better testability
2. **⭐ Centralize Configuration** - Use the framework configuration system
3. **⭐ Implement Lifecycle Hooks** - Use startup/shutdown hooks for proper resource management
4. **⭐ Monitor Framework Health** - Implement health checks and metrics
5. **⭐ Handle Errors Gracefully** - Use the error handling system for consistent error responses
6. **⭐ Use Structured Logging** - Log with context for better debugging

## 🛠️ Troubleshooting

### Framework Initialization Failed

**Error**: `Framework initialization failed: Configuration not found`

**Solution**:
```python
# Ensure configuration is properly set
framework.configure(
    environment="development",
    # Other required configuration
)

# Or load from file
framework.config.load("config/development.json")
```

### Tool Registration Failed

**Error**: `Tool registration failed: Tool 'MyTool' already registered`

**Solution**:
```python
# Check for duplicate registrations
# Ensure each tool is only registered once

# Instead of:
framework.register_tool(my_tool)
framework.register_tool(my_tool)  # Duplicate!

# Use:
framework.register_tools([tool1, tool2, tool3])  # Register all at once
```

### Service Resolution Failed

**Error**: `Service resolution failed: Service 'fabric_client' not registered`

**Solution**:
```python
# Register the service before resolving
framework.container.register("fabric_client", FabricClient)

# Or check if registered
if framework.container.has("fabric_client"):
    client = framework.container.resolve("fabric_client")
```

### Configuration Not Found

**Error**: `Configuration key 'azure.subscription_id' not found`

**Solution**:
```python
# Set the configuration value
framework.config.set("azure.subscription_id", "your-subscription-id")

# Or provide a default
subscription_id = framework.config.get("azure.subscription_id", "default-value")
```

## 📚 Next Steps

1. **[Platform API Reference](../api-reference/platform.md)** - Detailed platform API
2. **[Tool Development Guide](../examples/tool-development.md)** - Create MCP tools
3. **[Deployment Guide](../deployment/overview.md)** - Deploy your MCP server
4. **[Best Practices](../best-practices/README.md)** - Follow recommended patterns

## 🔗 Related Documentation

- [MCP Server SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Dependency Injection Patterns](https://docs.microsoft.com/en-us/dotnet/core/extensions/dependency-injection)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
