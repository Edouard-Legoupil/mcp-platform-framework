# ⚡ Quick Start Guide

**Get started with the MCP Platform Framework in 5 minutes!**

This guide will walk you through creating your first MCP domain and running it locally.

## 🎯 Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.11+** installed
- ✅ **pip** (Python package manager)
- ✅ **Azure CLI** installed (for deployment)
- ✅ **Git** installed

> ⚠️ **Note**: For local development, you don't need Azure resources. For deployment, you'll need an Azure account.

## 🚀 Step 1: Create a New Domain

The easiest way to get started is to use the domain template generator:

```bash
# Clone the MCP Platform Framework (if you haven't already)
git clone https://github.com/your-org/mcp-platform-framework.git
cd mcp-platform-framework

# Create a new domain from template
python -m platform.template.template_generator \
    --domain DonorManagement \
    --description "Domain for managing donor information and relationships" \
    --author "Your Name" \
    --maintainer "your.email@example.com" \
    --output ./donor-management
```

This creates a complete domain repository structure in the `donor-management/` directory.

### What's Created?

```
donor-management/
├── README.md                    # Domain documentation
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── setup.py                     # Package configuration
├── main.py                      # Function App entry point
├── config.py                    # Domain configuration
├── platform_framework/          # Platform framework reference
├── tools/                       # Your domain tools
│   ├── __init__.py
│   └── example_tool.py          # Example tools to get you started
├── tests/                       # Tests for your domain
│   ├── unit/
│   │   └── test_tools.py
│   └── integration/
│       └── test_integration.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml            # GitHub Actions workflow
└── deployment/
    └── parameters.json           # Deployment parameters
```

## 📦 Step 2: Install Dependencies

Navigate to your new domain directory and install the dependencies:

```bash
cd donor-management

# Install the platform framework and dependencies
pip install -r requirements.txt

# For development, also install dev dependencies
pip install -r requirements-dev.txt
```

> 💡 **Tip**: Consider using a virtual environment:
> ```bash
> python -m venv venv
> source venv/bin/activate  # On Windows: venv\Scripts\activate
> pip install -r requirements.txt
> ```

## 🛠️ Step 3: Explore the Example Tools

Open `tools/example_tool.py` to see the example tools:

```python
from platform import tool, resource, query, action
from platform.classification import classification
from platform.auth import authenticated_tool, requires_permission

@tool(description="Example tool for DonorManagement domain")
@classification("INTERNAL")
@authenticated_tool
@requires_permission("domain.read")
def example_tool(user_id: str = None) -> dict:
    '''Example tool that demonstrates MCP framework features'''
    return {
        'message': 'Hello from DonorManagement domain!',
        'user_id': user_id,
        'domain': 'DonorManagement',
        'version': '1.0.0'
    }

@resource(description="Get domain information")
@classification("PUBLIC")
def get_domain_info() -> dict:
    '''Get information about this domain'''
    return {
        'name': 'DonorManagement',
        'description': 'Domain for managing donor information',
        'version': '1.0.0',
        'author': 'Your Name'
    }
```

## ✍️ Step 4: Create Your First Tool

Let's create a simple donor information tool. Edit `tools/donor_tools.py`:

```python
from platform import tool, resource
from platform.classification import classification
from platform.auth import authenticated_tool, requires_permission
from platform.connectivity import semantic_model

@tool(description="Get donor portfolio health score")
@classification("CONFIDENTIAL")
@authenticated_tool
@requires_permission("donor.read")
def get_donor_portfolio_health(donor_id: str) -> dict:
    '''Get the health score for a specific donor's portfolio'''
    
    # Query the semantic model (this would query your Power BI semantic model)
    query = f"EVALUATE DonorPortfolioHealth WHERE DonorID = {donor_id}"
    result = semantic_model.execute(query, model_id="DonorManagement")
    
    if result.error:
        return {"error": result.error}
    
    # Return the health score
    return {
        "donor_id": donor_id,
        "health_score": result.data[0]["HealthScore"] if result.data else None,
        "status": "success"
    }

@resource(description="Get basic donor information")
@classification("INTERNAL")
@authenticated_tool
def get_donor_info(donor_id: str) -> dict:
    '''Get basic information about a donor'''
    # In a real implementation, this would query your data source
    return {
        "donor_id": donor_id,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "total_contributions": 15000,
        "status": "active"
    }
```

Don't forget to update `tools/__init__.py` to export your new tools:

```python
from .example_tool import *
from .donor_tools import *

__all__ = []
```

## 🏃 Step 5: Run Locally

Start the local development server:

```bash
# Set environment variables for local development
export MCP_DOMAIN=DonorManagement
export MCP_ENVIRONMENT=Dev

# Run the Function App locally
python main.py
```

This starts a local HTTP server on port 8080. You can test your tools using curl or any HTTP client:

```bash
# Test the health endpoint
curl http://localhost:8080/api/health

# Test your tool (note: authentication is required for most tools)
curl -X POST http://localhost:8080/get_donor_info \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-test-token" \
  -d '{"donor_id": "12345"}'
```

> ⚠️ **Note**: For local testing without authentication, you can temporarily disable it in your configuration.

## 🧪 Step 6: Run Tests

The template includes comprehensive tests. Run them to ensure everything works:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=tools --cov-report=html
```

## 🚀 Step 7: Deploy to Azure (Optional)

When you're ready to deploy to Azure:

### 7.1 Set Up Azure Resources

```bash
# Login to Azure
az login

# Create a resource group
az group create --name mcp-donor-management-dev-rg --location eastus

# Deploy infrastructure using Bicep
az deployment group create \
    --resource-group mcp-donor-management-dev-rg \
    --template-file ../mcp-platform-framework/deployment/mcp-deployment.bicep \
    --parameters \
        projectName=donor-management \
        environment=dev \
        location=eastus \
        mcpDomain=DonorManagement
```

### 7.2 Deploy the Function App

```bash
# Deploy the Function App
az functionapp deployment source config-zip \
    --resource-group mcp-donor-management-dev-rg \
    --name donor-management-dev-func \
    --src .
```

### 7.3 Test the Deployed Service

```bash
# Get the Function App URL
az functionapp show \
    --resource-group mcp-donor-management-dev-rg \
    --name donor-management-dev-func \
    --query defaultHostName -o tsv

# Test the health endpoint
curl https://donor-management-dev-func.azurewebsites.net/api/health
```

## 🎉 Congratulations!

You've successfully:

1. ✅ Created a new MCP domain from template
2. ✅ Installed all dependencies
3. ✅ Explored the example tools
4. ✅ Created your first custom tool
5. ✅ Ran the framework locally
6. ✅ Executed tests
7. ✅ (Optional) Deployed to Azure

## 🚀 Next Steps

Now that you have a working domain, here are some next steps:

### Learn More About Tool Development
- [Tool Development Guide](../examples/tool-development.md) - Deep dive into creating MCP tools
- [Semantic Model Access](../examples/semantic-models.md) - Learn how to query Power BI semantic models
- [Warehouse Queries](../examples/warehouse-queries.md) - Execute SQL queries against Fabric warehouses

### Explore Platform Features
- [Authentication Module](../modules/authentication.md) - Configure Entra ID and Managed Identity
- [Authorization Module](../modules/authorization.md) - Set up RBAC and permissions
- [Telemetry Module](../modules/telemetry.md) - Configure monitoring and observability

### Set Up CI/CD
- [GitHub Actions Pipeline](../deployment/github-actions.md) - Automate your deployment
- [Azure DevOps Pipeline](../deployment/azure-devops.md) - Enterprise CI/CD

### Create More Domains
- [Domain Template System](../templates/creating-domains.md) - Create additional domains
- [Best Practices](../best-practices/README.md) - Follow recommended patterns

## 💡 Tips for Success

⭐ **Start with Semantic Models**: Always use semantic models instead of direct table access for business metrics.

⭐ **Use Decorators**: Leverage the platform decorators for automatic registration, authentication, and classification.

⭐ **Enable All Security Features**: Always enable authentication, authorization, and classification in production.

⭐ **Write Tests**: The framework includes comprehensive testing support - use it!

⭐ **Monitor Everything**: Use the built-in telemetry and audit logging to understand usage patterns.

⚠️ **Never Embed Secrets**: Always use Key Vault for secrets management.

🔒 **Use Managed Identity**: For service-to-service authentication, use Managed Identity instead of connection strings.

## 📖 Quick Reference

### Common Decorators

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@tool` | Register a tool | `@tool(description="Get donor info")` |
| `@resource` | Register a resource tool | `@resource(description="Get data")` |
| `@query` | Register a query tool | `@query(description="Query data")` |
| `@action` | Register an action tool | `@action(description="Update data")` |
| `@authenticated_tool` | Require authentication | `@authenticated_tool` |
| `@requires_permission` | Require specific permission | `@requires_permission("donor.read")` |
| `@requires_role` | Require specific role | `@requires_role("donor_manager")` |
| `@classification` | Set data classification | `@classification("CONFIDENTIAL")` |

### Common Imports

```python
# Platform decorators
from platform import tool, resource, query, action

# Authentication and authorization
from platform.auth import authenticated_tool, requires_permission, requires_role

# Classification
from platform.classification import classification, classify_data, requires_classification

# Fabric connectivity
from platform.connectivity import fabric, semantic_model, warehouse, lakehouse

# Telemetry and audit
from platform.telemetry import track_tool_telemetry
from platform.audit import audit_tool_access, audit_data_access

# Framework
from platform.framework import get_framework, initialize_framework
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_DOMAIN` | Domain name | Required |
| `MCP_ENVIRONMENT` | Environment (Dev/Test/Prod) | Dev |
| `MCP_ENABLE_TELEMETRY` | Enable telemetry | true |
| `MCP_ENABLE_AUDIT` | Enable audit logging | true |
| `MCP_ENABLE_AUTH` | Enable authentication | true |
| `MCP_ENABLE_AUTHORIZATION` | Enable authorization | true |
| `MCP_ENABLE_CLASSIFICATION` | Enable classification | true |

---

**🎉 You're now ready to build amazing MCP services!**

- **Need more examples?** Check out the [Examples](../examples/README.md) section
- **Have questions?** See the [FAQ](../FAQ.md)
- **Found an issue?** Open a bug report
- **Have feedback?** Open a discussion
