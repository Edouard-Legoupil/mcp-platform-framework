# 🚀 Installation Guide

## Overview

This guide walks you through installing and setting up the MCP Platform Framework for development and deployment in your Azure environment.

## 📋 Prerequisites

Before installing the MCP Platform Framework, ensure you have the following prerequisites:

- ✅ **Azure Account** with appropriate permissions
- ✅ **Azure CLI** installed and configured
- ✅ **Python 3.11+** installed
- ✅ **pip** (Python package manager)
- ✅ **Git** for version control
- ✅ **Visual Studio Code** (recommended)

> ⚠️ **Important**: You must have Contributor or Owner permissions on your Azure subscription to deploy resources.

## 💻 Local Development Setup

### 1. Clone the Repository

```bash
# Clone the MCP Platform Framework repository
git clone https://github.com/your-org/mcp-platform-framework.git
cd mcp-platform-framework

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 3. Install MCP Server Dependencies

```bash
# Install MCP server and Azure-specific packages
pip install mcp[azure] azure-identity azure-keyvault-secrets
```

## 🌐 Azure Environment Setup

### 1. Azure CLI Configuration

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "Your-Subscription-Name-or-ID"

# Install required Azure CLI extensions
az extension add --name azure-devops
az extension add --name azure-keyvault
```

### 2. Create Resource Group

```bash
# Create a resource group for your MCP deployment
az group create --name mcp-platform-rg --location eastus
```

### 3. Set Up Azure Resources

The MCP Platform Framework requires the following Azure resources:

- **Azure Function App** - For MCP server deployment
- **Azure Key Vault** - For secrets management
- **Azure Application Insights** - For monitoring and telemetry
- **Azure Storage Account** - For function app storage
- **Microsoft Fabric** - For data connectivity

## 🔧 Framework Configuration

### 1. Environment Variables

Create a `.env` file in your project root:

```bash
# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=mcp-platform-rg
AZURE_LOCATION=eastus

# Key Vault Configuration
KEY_VAULT_NAME=mcp-platform-kv

# Function App Configuration
FUNCTION_APP_NAME=mcp-platform-func
FUNCTION_APP_STORAGE=mcpplatformstorage

# Application Insights
APP_INSIGHTS_NAME=mcp-platform-insights

# Fabric Configuration
FABRIC_TENANT_ID=your-fabric-tenant-id
FABRIC_WORKSPACE_ID=your-workspace-id
```

### 2. Configure Authentication

```bash
# Create a service principal for authentication
az ad sp create-for-rbac --name mcp-platform-sp --skip-assignment

# Assign permissions to the service principal
az role assignment create --assignee "mcp-platform-sp" \
    --role "Contributor" \
    --resource-group mcp-platform-rg
```

## 🧪 Verify Installation

### 1. Test Local Setup

```bash
# Run the MCP server locally
python -m mcp_framework.server

# Test basic functionality
python -c "from mcp_framework.platform import MCPFramework; print('✅ Framework loaded successfully')"
```

### 2. Validate Azure Connectivity

```bash
# Test Azure authentication
az account show

# Test Key Vault access (after deployment)
az keyvault secret list --vault-name mcp-platform-kv
```

## 📦 Package Installation

### Install from PyPI (Production)

```bash
pip install mcp-platform-framework
```

### Install from Source (Development)

```bash
# From the repository root
pip install -e .
```

## 🔄 Upgrading

### Upgrade Framework

```bash
# Update to the latest version
pip install --upgrade mcp-platform-framework

# Or from source
git pull origin main
pip install -e .
```

### Migration Notes

When upgrading between major versions, check the [CHANGELOG.md](../CHANGELOG.md) for breaking changes and migration instructions.

## 🛠️ Troubleshooting

### Common Issues

#### Python Version Compatibility

**Error**: `Python version 3.11 or higher is required`

**Solution**: Upgrade your Python installation or use a compatible version.

```bash
# Check Python version
python --version

# Install specific Python version using pyenv
pyenv install 3.11.8
pyenv global 3.11.8
```

#### Missing Azure CLI

**Error**: `az: command not found`

**Solution**: Install Azure CLI from [Microsoft's documentation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).

#### Authentication Failures

**Error**: `DefaultAzureCredential failed to authenticate`

**Solution**: Ensure you're logged in and have proper permissions:

```bash
# Re-authenticate
az login

# Check permissions
az account show
az role assignment list --assignee your-email@domain.com
```

#### Dependency Conflicts

**Error**: `ModuleNotFoundError` or version conflicts

**Solution**: Create a fresh virtual environment:

```bash
# Remove existing environment
rm -rf venv

# Create new environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📚 Next Steps

After completing the installation:

1. **[Quick Start](quick-start.md)** - Get started with basic MCP tool development
2. **[Prerequisites](prerequisites.md)** - Detailed system requirements
3. **[Configuration Guide](configuration.md)** - Configure your development environment
4. **[Deployment Overview](../deployment/overview.md)** - Deploy to Azure

## 🔒 Security Considerations

- 🔒 **Never commit secrets** to version control
- 🔒 Use Azure Key Vault for all sensitive configuration
- 🔒 Regularly rotate service principal credentials
- 🔒 Follow the principle of least privilege for permissions

## ⚡ Performance Tips

- Use virtual environments to isolate dependencies
- Consider using `pip cache` to speed up installations
- For CI/CD pipelines, use cached dependencies where possible
- Test with production-like configurations in staging environments

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
