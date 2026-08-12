# 🔧 Tool Registration Module

The Tool Registration Module provides automatic MCP tool discovery, registration, and metadata generation for the MCP Platform Framework, making it easy for domains to expose their functionality without manual registration.

## 🎯 Overview

The Tool Registration Module handles:
- **Automatic Discovery**: Scans domain packages for `@tool` decorated functions
- **Metadata Generation**: Extracts function signatures, docstrings, and annotations
- **Registration Management**: Central tool registry with dynamic registration/unregistration
- **Tool Versioning**: Support for multiple versions of tools

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│        Tool Registration Module          │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Automatic       │  │ Metadata        │ │
│  │ Discovery       │  │ Generation      │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Tool           │  │ Registration     │ │
│  │ Decorators     │  │ Management      │ │
│  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Basic Usage

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

### Configuration

```python
# config/registration.py
from platform.registration.config import RegistrationConfig

REGISTRATION_CONFIG = RegistrationConfig(
    # Discovery settings
    discovery_enabled=True,
    discovery_paths=["tools", "services"],
    discovery_patterns=["*_tool.py", "tools.py"],
    
    # Registration settings
    auto_register=True,
    registry_type="memory",  # or "database", "azure_table"
    
    # Metadata settings
    include_docstrings=True,
    include_type_hints=True,
    include_source_location=True,
    
    # Versioning
    versioning_enabled=True,
    default_version="1.0.0",
    
    # Caching
    cache_enabled=True,
    cache_ttl=300
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Registration Configuration
REGISTRATION_DISCOVERY_ENABLED=true
REGISTRATION_AUTO_REGISTER=true
REGISTRATION_REGISTRY_TYPE=memory
REGISTRATION_INCLUDE_DOCSTRINGS=true
REGISTRATION_INCLUDE_TYPE_HINTS=true
REGISTRATION_VERSIONING_ENABLED=true
REGISTRATION_CACHE_ENABLED=true
```

### Configuration File

```yaml
# config/registration.yaml
registration:
  discovery:
    enabled: true
    paths:
      - "tools"
      - "services"
    patterns:
      - "*_tool.py"
      - "tools.py"
    exclude:
      - "test_*"
      - "*_test.py"
    
  registration:
    auto_register: true
    registry_type: memory  # memory, database, azure_table
    
  metadata:
    include_docstrings: true
    include_type_hints: true
    include_source_location: true
    include_parameter_descriptions: true
    
  versioning:
    enabled: true
    default_version: "1.0.0"
    version_format: "semver"
    
  cache:
    enabled: true
    ttl: 300
    max_size: 10000
```

## 🎯 API Reference

### Decorators

#### `@tool`

Decorates a function as an MCP tool.

```python
from platform.registration import tool

@tool
def get_donor_data(donor_id: str):
    """Get donor data"""
    return donor_service.get(donor_id)

# With full configuration
@tool(
    name="GetDonorData",
    description="Retrieves donor information from the database",
    classification="CONFIDENTIAL",
    required_permissions=["donor.read"],
    required_roles=["donor_analyst"],
    audit=True,
    version="1.0.0",
    deprecated=False,
    tags=["donor", "data", "read"]
)
def get_donor_data(donor_id: str):
    pass
```

**Parameters:**
- `name` (str, optional): Tool name (defaults to function name)
- `description` (str, optional): Tool description (defaults to docstring)
- `classification` (str, optional): Data classification level
- `required_permissions` (List[str], optional): Required permissions
- `required_roles` (List[str], optional): Required roles
- `audit` (bool, optional): Whether to audit this tool
- `version` (str, optional): Tool version
- `deprecated` (bool, optional): Whether the tool is deprecated
- `tags` (List[str], optional): Tool tags
- `timeout` (int, optional): Tool timeout in seconds
- `max_retries` (int, optional): Maximum number of retries

#### `@tool_async`

Async version of `@tool`.

```python
from platform.registration import tool_async

@tool_async
async def get_donor_data_async(donor_id: str):
    """Async version of get donor data"""
    return await donor_service.get(donor_id)
```

### Functions

#### `register_tool(function, **kwargs)`

Registers a function as an MCP tool.

```python
from platform.registration import register_tool

def get_donor_data(donor_id: str):
    return donor_service.get(donor_id)

# Register the function as a tool
register_tool(
    get_donor_data,
    name="GetDonorData",
    description="Retrieves donor information",
    classification="CONFIDENTIAL"
)
```

**Parameters:**
- `function` (callable): The function to register
- `**kwargs`: Same parameters as `@tool` decorator

#### `unregister_tool(name, version=None)`

Unregisters a tool.

```python
from platform.registration import unregister_tool

# Unregister a tool
unregister_tool("GetDonorData")

# Unregister a specific version
unregister_tool("GetDonorData", version="1.0.0")
```

**Parameters:**
- `name` (str): Tool name
- `version` (str, optional): Tool version (unregisters all versions if not specified)

#### `get_tool(name, version=None)`

Gets a registered tool.

```python
from platform.registration import get_tool

# Get a tool
tool_func = get_tool("GetDonorData")

# Get a specific version
tool_func = get_tool("GetDonorData", version="1.0.0")
```

**Parameters:**
- `name` (str): Tool name
- `version` (str, optional): Tool version

**Returns:**
- `callable`: The tool function

#### `list_tools(domain=None, tags=None, **kwargs)`

Lists registered tools.

```python
from platform.registration import list_tools

# List all tools
all_tools = list_tools()

# List tools in a domain
 domain_tools = list_tools(domain="DonorManagement")

# List tools with specific tags
 tagged_tools = list_tools(tags=["donor", "read"])

# List tools with filters
 filtered_tools = list_tools(
     domain="DonorManagement",
     classification="CONFIDENTIAL",
     deprecated=False
 )
```

**Parameters:**
- `domain` (str, optional): Filter by domain
- `tags` (List[str], optional): Filter by tags
- `classification` (str, optional): Filter by classification
- `deprecated` (bool, optional): Filter by deprecated status
- `version` (str, optional): Filter by version

**Returns:**
- `List[ToolMetadata]`: List of tool metadata

#### `register_domain_tools(module_name)`

Automatically discovers and registers all tools in a module.

```python
from platform.registration import register_domain_tools

# Register all tools in the current module
register_domain_tools(__name__)

# Register all tools in a specific module
register_domain_tools("donor.tools")
```

**Parameters:**
- `module_name` (str): Module name to scan for tools

### Classes

#### `ToolMetadata`

Represents metadata about a tool.

```python
from platform.registration import ToolMetadata

# Create tool metadata
metadata = ToolMetadata(
    name="GetDonorData",
    function=get_donor_data,
    description="Retrieves donor information",
    module="donor.tools",
    classification="CONFIDENTIAL",
    required_permissions=["donor.read"],
    required_roles=["donor_analyst"],
    audit=True,
    version="1.0.0",
    deprecated=False,
    tags=["donor", "data", "read"],
    timeout=30,
    max_retries=3,
    parameters={
        "donor_id": {
            "type": str,
            "required": True,
            "description": "The ID of the donor"
        }
    },
    returns={
        "type": dict,
        "description": "Donor information"
    }
)

# Convert to dictionary
metadata_dict = metadata.to_dict()

# Convert to JSON
metadata_json = metadata.to_json()
```

**Attributes:**
- `name` (str): Tool name
- `function` (callable): The tool function
- `description` (str): Tool description
- `module` (str): Module where the tool is defined
- `classification` (str): Data classification level
- `required_permissions` (List[str]): Required permissions
- `required_roles` (List[str]): Required roles
- `audit` (bool): Whether to audit this tool
- `version` (str): Tool version
- `deprecated` (bool): Whether the tool is deprecated
- `tags` (List[str]): Tool tags
- `timeout` (int): Tool timeout in seconds
- `max_retries` (int): Maximum number of retries
- `parameters` (dict): Parameter metadata
- `returns` (dict): Return type metadata
- `docstring` (str): Function docstring
- `source_location` (str): Source file and line number

**Methods:**
- `to_dict()`: Convert to dictionary
- `to_json()`: Convert to JSON string
- `get_signature()`: Get function signature
- `validate_parameters(params)`: Validate parameters

#### `ToolRegistry`

Manages the central registry of tools.

```python
from platform.registration import ToolRegistry

# Create tool registry
registry = ToolRegistry(
    registry_type="memory",
    cache_enabled=True
)

# Register a tool
registry.register(get_donor_data, name="GetDonorData")

# Unregister a tool
registry.unregister("GetDonorData")

# Get a tool
tool_func = registry.get("GetDonorData")

# List tools
tools = registry.list()

# Search tools
results = registry.search(name="*Donor*")
```

**Parameters:**
- `registry_type` (str): Type of registry ("memory", "database", "azure_table")
- `cache_enabled` (bool, optional): Enable caching
- `cache_ttl` (int, optional): Cache TTL in seconds

**Methods:**
- `register(function, **kwargs)`: Register a tool
- `unregister(name, version=None)`: Unregister a tool
- `get(name, version=None)`: Get a tool
- `list(**kwargs)`: List tools
- `search(**kwargs)`: Search tools
- `clear()`: Clear all tools
- `get_metadata(name, version=None)`: Get tool metadata
- `update_metadata(name, **kwargs)`: Update tool metadata

#### `ToolDiscovery`

Discovers tools in modules and packages.

```python
from platform.registration import ToolDiscovery

# Create tool discovery
discovery = ToolDiscovery(
    paths=["tools", "services"],
    patterns=["*_tool.py", "tools.py"],
    exclude=["test_*", "*_test.py"]
)

# Discover tools in a module
tools = discovery.discover_module("donor.tools")

# Discover tools in a package
tools = discovery.discover_package("donor")

# Discover all tools
discovery.discover_all()
```

**Parameters:**
- `paths` (List[str]): Paths to search for tools
- `patterns` (List[str]): File patterns to match
- `exclude` (List[str]): Patterns to exclude
- `recursive` (bool, optional): Search recursively

**Methods:**
- `discover_module(module_name)`: Discover tools in a module
- `discover_package(package_name)`: Discover tools in a package
- `discover_all()`: Discover all tools
- `discover_file(file_path)`: Discover tools in a file
- `get_discovered_tools()`: Get list of discovered tools

## 📊 Tool Metadata

### Metadata Structure

```json
{
  "name": "GetDonorData",
  "description": "Retrieves donor information from the database",
  "module": "donor.tools",
  "function": "get_donor_data",
  "classification": "CONFIDENTIAL",
  "required_permissions": ["donor.read"],
  "required_roles": ["donor_analyst"],
  "audit": true,
  "version": "1.0.0",
  "deprecated": false,
  "tags": ["donor", "data", "read"],
  "timeout": 30,
  "max_retries": 3,
  "parameters": {
    "donor_id": {
      "type": "str",
      "required": true,
      "description": "The ID of the donor",
      "default": null
    }
  },
  "returns": {
    "type": "dict",
    "description": "Donor information"
  },
  "docstring": "Retrieves donor information from the database\n\nArgs:\n    donor_id: The ID of the donor\n\nReturns:\n    Donor information",
  "source_location": "donor/tools.py:42"
}
```

### Parameter Metadata

```json
{
  "type": "str",
  "required": true,
  "description": "The ID of the donor",
  "default": null,
  "min_length": 1,
  "max_length": 50,
  "pattern": null,
  "enum": null
}
```

## 📈 Monitoring and Metrics

### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Registered Tools | Number of registered tools | Varies | < 1000 |
| Tool Discovery Time | Time to discover tools | < 100ms | > 500ms |
| Tool Registration Rate | Tools registered per minute | Varies | > 100/min |
| Tool Errors | Number of tool execution errors | 0 | > 10/hour |
| Deprecated Tools | Number of deprecated tools | 0 | > 5 |

### Tool Queries

```kusto
// Get tool registration statistics
ToolRegistry
| summarize count() by domain
| order by count_ desc

// Get most used tools
ToolCalls
| summarize count() by tool_name
| order by count_ desc
| take 10

// Get tool errors
ToolErrors
| summarize count() by tool_name, error_code
| order by count_ desc

// Get deprecated tools
ToolRegistry
| where deprecated == true
| project name, version, deprecated_since
```

## 🚀 Best Practices

### ⭐ Use Tool Decorators

Always use the `@tool` decorator for functions that should be exposed as MCP tools.

```python
# Good
@tool(
    name="GetDonorData",
    description="Retrieves donor information",
    classification="CONFIDENTIAL"
)
def get_donor_data(donor_id: str):
    pass

# Bad - No decorator
@tool
def get_donor_data(donor_id: str):
    pass
```

### ⭐ Include Comprehensive Metadata

Include all relevant metadata in tool definitions.

```python
# Good - Comprehensive metadata
@tool(
    name="GetDonorData",
    description="Retrieves donor information from the database",
    classification="CONFIDENTIAL",
    required_permissions=["donor.read"],
    required_roles=["donor_analyst"],
    audit=True,
    version="1.0.0",
    tags=["donor", "data", "read"],
    timeout=30
)
def get_donor_data(donor_id: str):
    pass

# Bad - Minimal metadata
@tool
def get_donor_data(donor_id: str):
    pass
```

### ⭐ Use Automatic Registration

Use automatic registration for domains.

```python
# Good - Automatic registration
# In domain/__init__.py
from platform.registration import register_domain_tools
register_domain_tools(__name__)

# Bad - Manual registration
# In domain/__init__.py
from platform.registration import register_tool
from .tools import get_donor_data, get_donor_list

register_tool(get_donor_data, name="GetDonorData")
register_tool(get_donor_list, name="GetDonorList")
```

### ⭐ Use Semantic Versioning

Use semantic versioning for tools.

```python
# Good - Semantic versioning
@tool(version="1.0.0")
def get_donor_data_v1(donor_id: str):
    pass

@tool(version="2.0.0")
def get_donor_data_v2(donor_id: str):
    pass

# Bad - No versioning or arbitrary versioning
@tool(version="1")
def get_donor_data(donor_id: str):
    pass

@tool(version="latest")
def get_donor_data(donor_id: str):
    pass
```

### ⭐ Document Tools Thoroughly

Include comprehensive docstrings for tools.

```python
# Good - Comprehensive docstring
@tool
def get_donor_data(donor_id: str):
    """
    Retrieves donor information from the database.
    
    This tool retrieves comprehensive donor information including
    contact details, donation history, and engagement metrics.
    
    Args:
        donor_id (str): The unique identifier of the donor.
            Must be a valid donor ID in the format DON-XXXX.
    
    Returns:
        dict: Donor information including:
            - id (str): Donor ID
            - name (str): Donor name
            - email (str): Email address
            - phone (str): Phone number
            - address (dict): Mailing address
            - donations (list): Donation history
            - engagement (dict): Engagement metrics
    
    Raises:
        MCPError: If donor is not found or access is denied
    
    Examples:
        >>> get_donor_data("DON-12345")
        {
            "id": "DON-12345",
            "name": "John Doe",
            "email": "john@unhcr.org",
            ...
        }
    """
    pass

# Bad - Minimal docstring
@tool
def get_donor_data(donor_id: str):
    """Get donor data"""
    pass
```

### ⭐ Use Tags for Organization

Use tags to organize and categorize tools.

```python
# Good - Organized with tags
@tool(
    tags=["donor", "data", "read", "core"]
)
def get_donor_data(donor_id: str):
    pass

@tool(
    tags=["donor", "analytics", "read", "premium"]
)
def get_donor_analytics(donor_id: str):
    pass

# Bad - No tags or generic tags
@tool(
    tags=["tool"]
)
def get_donor_data(donor_id: str):
    pass
```

### ⭐ Handle Deprecation Properly

Properly deprecate tools when replacing them.

```python
# Good - Proper deprecation
@tool(
    name="GetDonorData",
    version="1.0.0",
    deprecated=True,
    deprecation_message="Use GetDonorDataV2 instead",
    deprecated_since="2026-01-01"
)
def get_donor_data_v1(donor_id: str):
    pass

@tool(
    name="GetDonorData",
    version="2.0.0"
)
def get_donor_data_v2(donor_id: str):
    pass

# Bad - No deprecation notice
@tool(version="1.0.0")
def get_donor_data_old(donor_id: str):
    pass
```

## 🔍 Troubleshooting

### Common Issues

#### Tools Not Being Discovered

**Symptoms:** Tools not appearing in the registry

**Causes:**
- `@tool` decorator not applied
- Module not scanned for tools
- Discovery paths not configured correctly
- File patterns not matching

**Solutions:**
1. Ensure `@tool` decorator is applied
2. Check discovery configuration
3. Verify module is being scanned
4. Check file patterns

```python
# Debug tool discovery
from platform.registration import ToolDiscovery, list_tools

# Check discovery configuration
discovery = ToolDiscovery()
print(f"Discovery paths: {discovery.paths}")
print(f"Discovery patterns: {discovery.patterns}")
print(f"Discovery exclude: {discovery.exclude}")

# Check registered tools
tools = list_tools()
print(f"Registered tools: {len(tools)}")
for tool in tools:
    print(f"  - {tool.name} (v{tool.version})")
```

#### Tool Registration Conflicts

**Symptoms:** Errors when registering tools with the same name

**Causes:**
- Multiple tools with the same name
- Version conflicts
- Tools being registered multiple times

**Solutions:**
1. Use unique tool names
2. Use versioning for different implementations
3. Check for existing registrations
4. Use namespaces or domains in tool names

```python
# Debug registration conflicts
from platform.registration import ToolRegistry, list_tools

registry = ToolRegistry()

# Check for existing tool
existing = registry.get("GetDonorData")
if existing:
    print(f"Tool already exists: {existing}")
    print(f"Version: {existing.version}")
    print(f"Module: {existing.module}")

# List all versions of a tool
all_versions = [t for t in list_tools() if t.name == "GetDonorData"]
print(f"All versions: {all_versions}")
```

#### Tool Metadata Missing

**Symptoms:** Tool metadata incomplete or missing

**Causes:**
- Metadata not provided in decorator
- Docstrings missing or incomplete
- Type hints missing
- Configuration not including metadata extraction

**Solutions:**
1. Provide comprehensive metadata in decorator
2. Add docstrings to functions
3. Add type hints to parameters
4. Check metadata extraction configuration

```python
# Debug tool metadata
from platform.registration import get_tool

# Get tool metadata
tool_func = get_tool("GetDonorData")
metadata = tool_func._tool_metadata

print(f"Name: {metadata.name}")
print(f"Description: {metadata.description}")
print(f"Parameters: {metadata.parameters}")
print(f"Returns: {metadata.returns}")
print(f"Docstring: {metadata.docstring}")
```

## 📚 Examples

### Complete Tool Registration Example

```python
from platform.auth import authenticated_tool, requires_permission
from platform.registration import tool
from platform.classification import classification, ClassificationLevel
from platform.audit import audit_log
from platform.telemetry import capture_tool_metrics

@authenticated_tool
@requires_permission("donor.read")
@classification(ClassificationLevel.CONFIDENTIAL)
@audit_log.sensitive_operation
@capture_tool_metrics
@tool(
    name="GetDonorPortfolio",
    description="Retrieves comprehensive donor portfolio information",
    classification="CONFIDENTIAL",
    required_permissions=["donor.read", "donor.analytics"],
    required_roles=["donor_analyst"],
    audit=True,
    version="1.0.0",
    tags=["donor", "portfolio", "analytics", "read"],
    timeout=60,
    max_retries=3
)
def get_donor_portfolio(donor_id: str, include_history: bool = True):
    """
    Retrieves comprehensive donor portfolio information.
    
    This tool retrieves all information about a donor's portfolio including
    current donations, historical data, engagement metrics, and risk assessment.
    
    Args:
        donor_id (str): The unique identifier of the donor.
            Must be a valid donor ID in the format DON-XXXX.
        include_history (bool, optional): Whether to include historical data.
            Defaults to True.
    
    Returns:
        dict: Donor portfolio information including:
            - donor_id (str): Donor ID
            - current_donations (list): Current active donations
            - historical_donations (list): Historical donations (if include_history=True)
            - engagement_metrics (dict): Engagement scores and trends
            - risk_assessment (dict): Risk scores and factors
            - total_value (float): Total portfolio value
    
    Raises:
        MCPError: If donor is not found or access is denied
    
    Examples:
        >>> get_donor_portfolio("DON-12345")
        {
            "donor_id": "DON-12345",
            "current_donations": [...],
            "historical_donations": [...],
            "engagement_metrics": {...},
            "risk_assessment": {...},
            "total_value": 1500000.00
        }
    """
    
    # Get caller information
    caller = get_caller_identity()
    
    # Get donor portfolio
    portfolio = await portfolio_service.get_portfolio(
        donor_id=donor_id,
        include_history=include_history
    )
    
    # Log access
    await audit_logger.log_data_access(
        user=caller.identity,
        resource=f"donor:portfolio:{donor_id}",
        action="read",
        classification="CONFIDENTIAL",
        metadata={"include_history": include_history}
    )
    
    return portfolio
```

### Domain Initialization with Automatic Registration

```python
# donor/__init__.py
"""
Donor Domain

This domain provides tools for managing donor information, 
portfolios, and analytics.
"""

from platform.registration import register_domain_tools

# Automatically discover and register all tools in this domain
register_domain_tools(__name__)

# Domain metadata
__domain__ = "DonorManagement"
__version__ = "1.0.0"
__description__ = "Donor management and analytics domain"
__owner__ = "DER"
__sla__ = "Gold"
```

### Tool Versioning Example

```python
from platform.registration import tool

# Version 1.0.0 - Original implementation
@tool(
    name="GetDonorReport",
    version="1.0.0",
    description="Original donor report implementation",
    deprecated=True,
    deprecation_message="Use version 2.0.0 for improved performance",
    deprecated_since="2026-01-01"
)
def get_donor_report_v1(donor_id: str):
    """Original implementation - deprecated"""
    return report_service.get_report_v1(donor_id)

# Version 2.0.0 - Improved implementation
@tool(
    name="GetDonorReport",
    version="2.0.0",
    description="Improved donor report implementation with caching",
    tags=["donor", "report", "performance"]
)
def get_donor_report_v2(donor_id: str):
    """Improved implementation with caching"""
    return report_service.get_report_v2(donor_id)

# Version 3.0.0 - Latest implementation
@tool(
    name="GetDonorReport",
    version="3.0.0",
    description="Latest donor report implementation with real-time data",
    tags=["donor", "report", "realtime"]
)
def get_donor_report_v3(donor_id: str):
    """Latest implementation with real-time data"""
    return report_service.get_report_v3(donor_id)
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `ToolRegistrationError` | Base tool registration error | TOOL-001 |
| `ToolAlreadyExistsError` | Tool already exists | TOOL-002 |
| `ToolNotFoundError` | Tool not found | TOOL-003 |
| `ToolDiscoveryError` | Tool discovery error | TOOL-004 |
| `ToolMetadataError` | Tool metadata error | TOOL-005 |

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| TOOL-001 | Registration error | 500 |
| TOOL-002 | Tool already exists | 409 |
| TOOL-003 | Tool not found | 404 |
| TOOL-004 | Discovery error | 500 |
| TOOL-005 | Metadata error | 400 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*