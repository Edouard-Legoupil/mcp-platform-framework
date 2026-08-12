# 📚 MCP Platform Framework Examples

## Overview

This section provides comprehensive examples demonstrating how to use the MCP Platform Framework to build domain-specific tools, integrate with Microsoft Fabric, and deploy to Azure Function Apps.

## 🎯 Example Categories

### 🏗️ Domain Examples
- **[Donor Management Domain](donor-management.md)** - Complete example of a donor management domain
- **[Tool Development](tool-development.md)** - Guide for developing MCP tools

### 🔗 Microsoft Fabric Examples
- **[Semantic Model Access](semantic-models.md)** - How to access and query semantic models
- **[Warehouse Queries](warehouse-queries.md)** - Examples of warehouse querying patterns
- **[Lakehouse Operations](lakehouse-operations.md)** - Lakehouse data operations

### 🔐 Authentication & Authorization Examples
- **[Authentication Examples](authentication.md)** - Various authentication patterns
- **[Authorization Examples](authorization.md)** - RBAC and permission examples

## 📁 Example Structure

```
examples/
├── README.md                    # This file - Examples overview
├── donor-management.md          # Donor Management domain example
├── tool-development.md          # Tool development guide
├── semantic-models.md            # Semantic model access examples
├── warehouse-queries.md          # Warehouse querying examples
├── lakehouse-operations.md      # Lakehouse operations examples
├── authentication.md            # Authentication examples
├── authorization.md             # Authorization examples
└── code-samples/                # Runnable code samples
    ├── python/
    │   ├── donor_tools.py
    │   ├── fabric_client.py
    │   ├── auth_examples.py
    │   └── telemetry_examples.py
    └── bash/
        ├── deploy.sh
        └── test.sh
```

## 🚀 Getting Started with Examples

### Prerequisites

Before running the examples, ensure you have:

1. ✅ **MCP Platform Framework** installed
2. ✅ **Azure Account** with appropriate permissions
3. ✅ **Microsoft Fabric** workspace configured
4. ✅ **Python 3.11+** installed
5. ✅ **Required dependencies** installed

```bash
# Install the framework and dependencies
pip install mcp-platform-framework
pip install azure-identity azure-keyvault-secrets
```

### Running Examples

Most examples can be run directly:

```bash
# Run a Python example
python examples/code-samples/python/donor_tools.py

# Or import and use in your code
from examples.code_samples.python.fabric_client import FabricClient
```

## 📋 Example Index

### Domain Examples

| Example | Description | Complexity | Use Case |
|---------|-------------|------------|----------|
| [Donor Management](donor-management.md) | Complete donor domain implementation | ⭐⭐⭐⭐ | Production-ready domain |
| [Tool Development](tool-development.md) | Guide for creating MCP tools | ⭐⭐ | Learning tool development |

### Fabric Integration Examples

| Example | Description | Complexity | Use Case |
|---------|-------------|------------|----------|
| [Semantic Models](semantic-models.md) | Query semantic models | ⭐⭐ | Data access |
| [Warehouse Queries](warehouse-queries.md) | SQL warehouse operations | ⭐⭐⭐ | Analytics |
| [Lakehouse Operations](lakehouse-operations.md) | Lakehouse data operations | ⭐⭐⭐ | Data engineering |

### Security Examples

| Example | Description | Complexity | Use Case |
|---------|-------------|------------|----------|
| [Authentication](authentication.md) | Various auth patterns | ⭐⭐ | Secure access |
| [Authorization](authorization.md) | RBAC and permissions | ⭐⭐⭐ | Access control |

## 🏆 Featured Examples

### 1. Donor Management Domain

The [Donor Management Domain](donor-management.md) example demonstrates:
- Complete domain structure
- Tool development patterns
- Semantic model integration
- Authentication and authorization
- Telemetry and audit logging
- Error handling and classification

**Perfect for:** Understanding how to build a complete MCP domain

### 2. Semantic Model Access

The [Semantic Model Access](semantic-models.md) example shows:
- Connecting to Fabric semantic models
- Executing DAX queries
- Handling query results
- Caching strategies
- Error handling

**Perfect for:** Learning how to integrate with Microsoft Fabric

### 3. Tool Development Guide

The [Tool Development](tool-development.md) guide covers:
- Tool creation patterns
- Decorator usage
- Parameter handling
- Return value formatting
- Testing tools

**Perfect for:** Getting started with MCP tool development

## 🛡️ Security Considerations

When working with examples:

- 🔒 **Never use production credentials** in examples
- 🔒 **Always use test data** for development
- 🔒 **Clean up resources** after testing
- 🔒 **Follow least privilege** principles
- 🔒 **Enable audit logging** for all examples

## ⚡ Performance Tips

For optimal performance with examples:

- Use caching for Fabric queries
- Implement retry logic for transient failures
- Use parallel execution for independent operations
- Monitor resource usage
- Optimize query patterns

## 📖 Learning Path

### Beginner Path
1. **[Tool Development](tool-development.md)** - Learn the basics
2. **[Authentication Examples](authentication.md)** - Secure your tools
3. **[Semantic Model Access](semantic-models.md)** - Connect to data

### Intermediate Path
1. **[Donor Management Domain](donor-management.md)** - Build a complete domain
2. **[Warehouse Queries](warehouse-queries.md)** - Advanced data access
3. **[Authorization Examples](authorization.md)** - Implement access control

### Advanced Path
1. **[Lakehouse Operations](lakehouse-operations.md)** - Complex data operations
2. Custom domain development
3. Performance optimization

## 🛠️ Example Utilities

### Code Snippets

**Quick Start Template:**
```python
from mcp_framework.platform import MCPFramework
from mcp_framework.auth import authenticated_tool
from mcp_framework.telemetry import track_tool_execution

# Initialize framework
framework = MCPFramework()

@authenticated_tool
@track_tool_execution
def my_tool(param1: str, param2: int = 10) -> dict:
    """
    Example MCP tool with authentication and telemetry
    
    Args:
        param1: First parameter
        param2: Second parameter with default
        
    Returns:
        Dictionary with results
    """
    # Your tool logic here
    result = {
        "status": "success",
        "param1": param1,
        "param2": param2,
        "message": "Tool executed successfully"
    }
    return result

# Register tool
framework.register_tool(my_tool)
```

### Testing Examples

**Test Template:**
```python
import pytest
from mcp_framework.testing import MCPTestClient

@pytest.fixture
def client():
    return MCPTestClient()

def test_my_tool(client):
    # Test the tool
    result = client.call_tool("my_tool", {"param1": "test", "param2": 5})
    
    # Assert results
    assert result["status"] == "success"
    assert result["param1"] == "test"
    assert result["param2"] == 5
```

## 📚 Next Steps

After exploring the examples:

1. **[Getting Started](../getting-started/quick-start.md)** - Quick start guide
2. **[API Reference](../api-reference/README.md)** - Detailed API documentation
3. **[Best Practices](../best-practices/README.md)** - Recommended patterns
4. **[Deployment](../deployment/overview.md)** - Deploy your MCP server

## 🔗 Related Documentation

- [MCP Framework Documentation](../README.md)
- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Python MCP Server Documentation](https://github.com/modelcontextprotocol/python-sdk)

## 💬 Feedback

Found an error in the examples? Have suggestions for new examples?

- Open an issue in the repository
- Submit a pull request with improvements
- Contact the team at mcp-team@domain.com

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
