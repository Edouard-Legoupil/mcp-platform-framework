# 📚 MCP Platform Framework Documentation

**Welcome to the MCP Platform Framework Documentation!**

The MCP (Model Context Protocol) Platform Framework provides a comprehensive infrastructure layer for building domain-specific MCP services on Microsoft Azure. This framework enforces strict separation between platform concerns and domain business capabilities, ensuring consistency, security, and maintainability across all MCP implementations.

## 🎯 Quick Start

### For Domain Developers
If you're building a new domain (like DonorManagement, Finance, etc.), start here:

```bash
# 1. Create a new domain from template
python -m platform.template.template_generator --domain MyDomain --output ./my-domain

# 2. Navigate to your domain
cd my-domain

# 3. Install dependencies
pip install -r requirements.txt

# 4. Develop your tools
# Edit files in the tools/ directory

# 5. Test locally
python main.py
```

### For Platform Administrators
If you're deploying and managing the MCP Platform:

```bash
# 1. Deploy infrastructure using Bicep
az deployment group create \
    --resource-group mcp-platform-rg \
    --template-file deployment/mcp-deployment.bicep \
    --parameters projectName=mcp-platform environment=prod

# 2. Deploy Function App
az functionapp deployment source config-zip \
    --resource-group mcp-platform-rg \
    --name mcp-platform-prod-func \
    --src .
```

## 🏗️ Architecture Overview

The MCP Platform Framework follows a **strict separation of concerns** principle:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Platform Framework                      │
├─────────────────────────────────────────────────────────────┤
│  🔐 Authentication      │  🛡️ Authorization        │  📊 Telemetry    │
│  📝 Audit Logging        │  ❌ Error Handling        │  ⚙️  Config      │
│  🏷️ Classification       │  🔧 Registration          │  🔗 Connectivity │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Repositories                       │
├─────────────────────────────────────────────────────────────┤
│  mcp-donor-management/  │  mcp-finance/           │  mcp-supply/    │
│  mcp-campaign/          │  mcp-psp/               │  ...           │
└─────────────────────────────────────────────────────────────┘
```

**Key Principles:**
- ✅ **Domains own business capabilities** (logic, ontologies, semantic definitions)
- ✅ **Platform owns everything else** (authentication, authorization, telemetry, etc.)
- ✅ **No domain forking** - all domains use the same central platform template
- ✅ **Automatic tool discovery** - tools are automatically registered from decorators

## 📖 Documentation Sections

### [🚀 Getting Started](getting-started/README.md)
Learn how to install, configure, and start using the MCP Platform Framework.

### [🏗️ Architecture](architecture/README.md)
Understand the design principles, components, and data flow of the framework.

### [📦 Platform Modules](modules/README.md)
Detailed documentation for each platform module and its capabilities.

### [🚀 Deployment](deployment/README.md)
Comprehensive guides for deploying the framework to Azure.

### [💡 Examples](examples/README.md)
Practical examples showing how to use the framework in real scenarios.

### [🔧 API Reference](api-reference/README.md)
Complete API documentation for all platform modules.

### [🏭 Domain Templates](templates/README.md)
Learn how to create new domain repositories using the template system.

### [⭐ Best Practices](best-practices/README.md)
Recommended patterns and practices for building robust MCP services.

## 🎯 Core Features

### 🔐 Authentication & Authorization
- **Entra ID Integration**: Full Azure AD authentication with JWT validation
- **Managed Identity**: System and User Assigned Identity support
- **RBAC**: Role-Based Access Control with policy enforcement
- **Decorators**: Easy-to-use decorators for authentication and authorization

### 📊 Observability
- **Telemetry**: Automatic Application Insights integration
- **Audit Logging**: Immutable compliance logging to Azure Blob Storage
- **Tool Tracking**: Automatic capture of tool execution metrics

### 🔗 Microsoft Fabric Integration
- **Semantic Models**: Standardized access to Power BI semantic models
- **Warehouses**: SQL query execution against Fabric warehouses
- **Lakehouses**: Data analysis with SQL and Spark support
- **Unified Interface**: Single interface for all Fabric services

### ⚙️ Configuration & Management
- **Environment-Aware**: DEV, TEST, PROD configuration support
- **Key Vault Integration**: Secure secrets management
- **Automatic Discovery**: Tools are automatically discovered and registered
- **Data Classification**: Enforce governance policies through framework controls

## 📁 Project Structure

```
mcp-platform-framework/
├── platform/                    # Core platform modules
│   ├── auth/                  # Authentication & Identity
│   ├── authorization/        # RBAC & Permissions
│   ├── telemetry/            # Observability
│   ├── audit/                # Compliance Logging
│   ├── errors/               # Error Handling
│   ├── config/               # Configuration
│   ├── classification/       # Data Classification
│   ├── registration/         # Tool Discovery & Registration
│   ├── connectivity/         # Fabric Integration
│   ├── template/             # Domain Templates
│   └── framework.py          # Main Framework Integration
├── azure_functions/           # Function App Configuration
├── deployment/                # ARM/Bicep Templates
├── pipelines/                 # CI/CD Pipelines
├── docs/                      # Documentation
├── tests/                     # Unit & Integration Tests
├── examples/                  # Example Domain Implementations
├── main.py                    # Function App Entry Point
└── requirements.txt           # Dependencies
```

## 🔍 Documentation Search

Looking for something specific? Check out these common topics:

- **[Tool Development](examples/tool-development.md)** - How to create MCP tools
- **[Semantic Model Access](examples/semantic-models.md)** - Query Power BI semantic models
- **[Authentication Setup](modules/authentication.md)** - Configure Entra ID and Managed Identity
- **[Deployment Guide](deployment/overview.md)** - Deploy to Azure Function Apps
- **[CI/CD Pipelines](deployment/azure-devops.md)** - Set up automated deployment

## 💬 Support & Contributing

### Getting Help
- **Documentation**: Browse the docs in this directory
- **Examples**: Check the `examples/` directory for working examples
- **Issues**: Open an issue for bugs or feature requests
- **Discussions**: Join the discussion for Q&A

### Contributing
We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Documentation improvements

### Code of Conduct
This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Version Information

- **Framework Version**: 1.0.0
- **Python Version**: 3.11+
- **Azure Functions Version**: 4.x
- **Last Updated**: August 2026

---

**🎉 Ready to get started?**

- **Domain Developers**: [Quick Start Guide](getting-started/quick-start.md)
- **Platform Administrators**: [Deployment Guide](deployment/overview.md)
- **Everyone**: [Architecture Overview](architecture/overview.md)

**Have questions?** Check the [FAQ](FAQ.md) or open an issue.
