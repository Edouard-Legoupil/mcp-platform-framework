# 🚀 Getting Started with MCP Platform Framework

Welcome to the MCP Platform Framework! This guide will help you get started with building and deploying MCP services on Microsoft Azure.

## 📋 Table of Contents

- [Installation Guide](installation.md) - Step-by-step installation instructions
- [Quick Start](quick-start.md) - Get up and running in 5 minutes
- [Prerequisites](prerequisites.md) - What you need before you begin
- [Configuration Guide](configuration.md) - How to configure the framework

## 🎯 Who Should Use This Framework?

### Domain Developers
You're building business capabilities for a specific domain (Donor Management, Finance, Supply Chain, etc.). You want to:
- ✅ Focus on business logic, not infrastructure
- ✅ Use standardized Fabric connectivity
- ✅ Leverage automatic tool discovery
- ✅ Get enterprise-grade security out of the box

### Platform Administrators
You're responsible for deploying and managing the MCP Platform infrastructure. You want to:
- ✅ Deploy Function Apps with proper configuration
- ✅ Set up CI/CD pipelines
- ✅ Manage authentication and authorization
- ✅ Configure monitoring and observability

### DevOps Engineers
You're setting up the deployment pipeline and infrastructure. You want to:
- ✅ Use ARM or Bicep templates for infrastructure
- ✅ Configure Azure DevOps or GitHub Actions
- ✅ Set up security scanning
- ✅ Manage environment configurations

## 🏗️ Quick Architecture Overview

Before diving in, understand the key components:

```
┌───────────────────────────────────────────────────────────────────────┐
│                    Your Domain Repository                             │
├───────────────────────────────────────────────────────────────────────┤
│  tools/           │  semantic_models/  │  tests/                      │
│  - get_donor.py   │  - portfolio.py    │  - test_tools.py             │
│  - update_donor.py│  - revenue.py      │  - test_integration.py       │
└───────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────────┐
│                 MCP Platform Framework                                │
├───────────────────────────────────────────────────────────────────────┤
│  Authentication │  Authorization  │  Telemetry   │  Audit             │
│  Configuration  │  Classification │  Connectivity│  Registration      │
└───────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    Microsoft Azure                                    │
├───────────────────────────────────────────────────────────────────────┤
│  Function App     │  Fabric           │  Key Vault     │ App Insights │
│  Storage Account  │  - Semantic Models│  - Secrets     │  - Telemetry │
│  Managed Identity │  - Warehouses     │  - Certificates│  - Logs      │
│                   │  - Lakehouses     │                │              │
└───────────────────────────────────────────────────────────────────────┘
```

## 🎯 Key Concepts

### 1. Domains vs Platform
- **Domains** own business capabilities (business logic, ontologies, semantic definitions)
- **Platform** owns everything else (authentication, authorization, telemetry, error handling, connectivity)

### 2. Tool Registration
Tools are automatically discovered and registered using decorators:
```python
from platform import tool, resource, query, action

@tool(description="Get donor information")
def get_donor_info(donor_id: str) -> dict:
    return {"id": donor_id, "name": "John Doe"}
```

### 3. Fabric Connectivity
Standardized access to Microsoft Fabric services:
```python
from platform.connectivity import semantic_model, warehouse, lakehouse

# Query a semantic model
result = semantic_model.execute("EVALUATE DonorPortfolio")

# Query a warehouse
result = warehouse.execute("SELECT * FROM Donors")

# Query a lakehouse
result = lakehouse.execute("SELECT * FROM Pipeline")
```

### 4. Security
Enterprise-grade security built-in:
```python
from platform.auth import authenticated_tool, requires_permission, requires_role
from platform.classification import classification

@tool(description="Update donor information")
@authenticated_tool
@requires_permission("donor.write")
@requires_role("donor_manager")
@classification("CONFIDENTIAL")
def update_donor_info(donor_id: str, data: dict) -> bool:
    # Business logic here
    return True
```

## 🚀 Next Steps

### For Domain Developers
1. **[Quick Start](quick-start.md)** - Create your first domain in 5 minutes
2. **[Tool Development](examples/tool-development.md)** - Learn how to create MCP tools
3. **[Semantic Model Access](examples/semantic-models.md)** - Query Power BI semantic models

### For Platform Administrators
1. **[Prerequisites](prerequisites.md)** - Set up your Azure environment
2. **[Installation Guide](installation.md)** - Install the framework
3. **[Deployment Guide](deployment/overview.md)** - Deploy to Azure

### For DevOps Engineers
1. **[ARM Templates](deployment/arm-templates.md)** - Infrastructure as Code
2. **[Bicep Templates](deployment/bicep-templates.md)** - Modern deployment templates
3. **[Azure DevOps Pipeline](deployment/azure-devops.md)** - CI/CD automation

## 💡 Tips for Success

⭐ **Start Small**: Begin with a simple domain and add complexity gradually

⭐ **Use the Templates**: The domain template system creates a complete, working structure

⭐ **Leverage Semantic Models**: Always use semantic models instead of direct table access

⭐ **Enable All Security Features**: Authentication, authorization, and classification should always be enabled

⭐ **Monitor Everything**: Use the built-in telemetry and audit logging for observability

⚠️ **Never Fork the Platform**: All domains should use the central platform template

🔒 **Never Embed Secrets**: Always use Key Vault for secrets management

## 📖 Documentation Structure

This documentation is organized to help you find what you need quickly:

```
docs/
├── getting-started/      # Installation, quick start, prerequisites
├── architecture/         # Design principles, components, data flow
├── modules/             # Detailed module documentation
├── deployment/          # Deployment guides and templates
├── examples/            # Practical usage examples
├── api-reference/       # Complete API documentation
├── templates/           # Domain template system
└── best-practices/      # Recommended patterns
```

## 💬 Need Help?

- **Documentation Issues**: Open a PR to fix documentation errors
- **Bug Reports**: Open an issue with detailed reproduction steps
- **Feature Requests**: Open an issue with your use case
- **General Questions**: Check the [FAQ](../FAQ.md) or start a discussion

---

**🎉 Ready to get started?**

- **Domain Developers**: [Quick Start Guide](quick-start.md) →
- **Platform Administrators**: [Prerequisites](prerequisites.md) →
- **DevOps Engineers**: [ARM Templates](deployment/arm-templates.md) →
