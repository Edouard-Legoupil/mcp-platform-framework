# 📋 Prerequisites Guide

## Overview

This guide details all the system requirements, software dependencies, and Azure prerequisites needed to develop and deploy the MCP Platform Framework.

## 🖥️ System Requirements

### Operating System

The MCP Platform Framework supports the following operating systems:

- ✅ **Windows 10/11** (64-bit)
- ✅ **macOS** (Intel and Apple Silicon)
- ✅ **Linux** (Ubuntu 20.04+, CentOS 7+, RHEL 8+)

> ⚠️ **Note**: Azure Function Apps run on Linux, so Linux compatibility is required for deployment.

### Hardware Requirements

| Environment | Minimum Requirements | Recommended Requirements |
|-------------|----------------------|--------------------------|
| **Local Development** | 4 CPU cores, 8GB RAM, 50GB disk | 8 CPU cores, 16GB RAM, 100GB SSD |
| **CI/CD Pipeline** | 2 CPU cores, 4GB RAM | 4 CPU cores, 8GB RAM |
| **Production Deployment** | Depends on workload | 4+ CPU cores, 8+ GB RAM |

## 🐍 Python Requirements

### Python Version

- **Minimum**: Python 3.11.0
- **Recommended**: Python 3.11.8 or 3.12.x
- **Maximum**: Python 3.13.x (tested and supported)

> ⚠️ **Important**: Python 3.10 and below are **not supported** due to dependency requirements.

### Verify Python Installation

```bash
# Check Python version
python --version

# Check pip version
pip --version

# Check Python installation details
python -c "import sys; print(sys.version); print(sys.executable)"
```

### Python Extensions

The following Python extensions are recommended for development:

- **Virtual Environment**: `venv` (built-in) or `virtualenv`
- **Package Management**: `pip` (latest version)
- **Build Tools**: `setuptools`, `wheel`, `build`

```bash
# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install build tools
pip install build twine
```

## 🌐 Azure Requirements

### Azure Account

- **Azure Subscription**: Active Azure subscription with spending limits configured
- **Permissions**: Contributor or Owner role on the subscription
- **Resource Quotas**: Sufficient quotas for Function Apps, Key Vaults, and other resources

### Azure CLI

- **Version**: Azure CLI 2.50.0 or higher
- **Extensions**: Required extensions for full functionality

#### Install Azure CLI

**Windows (PowerShell)**:
```powershell
# Download and install
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
```

**macOS (Homebrew)**:
```bash
# Install via Homebrew
brew update && brew install azure-cli
```

**Linux (Debian/Ubuntu)**:
```bash
# Add Microsoft repository and install
curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null
AZ_REPO=$(lsb_release -cs)
echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | sudo tee /etc/apt/sources.list.d/azure-cli.list
sudo apt-get update
sudo apt-get install azure-cli
```

#### Verify Azure CLI Installation

```bash
# Check version
az --version

# Login to Azure
az login

# List available subscriptions
az account list
```

#### Required Azure CLI Extensions

```bash
# Install required extensions
az extension add --name azure-devops
az extension add --name azure-keyvault
az extension add --name azure-functions
az extension add --name azure-monitor

# List installed extensions
az extension list
```

### Azure Resources

The following Azure resources are required for MCP Platform Framework deployment:

#### Core Resources

| Resource | Purpose | SKU/ Tier |
|----------|---------|-----------|
| **Resource Group** | Container for all MCP resources | Standard |
| **Azure Function App** | Hosts the MCP server | Premium or Consumption |
| **Azure Key Vault** | Stores secrets and configuration | Standard |
| **Application Insights** | Monitoring and telemetry | Standard |
| **Storage Account** | Function App storage | Standard_LRS |

#### Data Resources

| Resource | Purpose | SKU/ Tier |
|----------|---------|-----------|
| **Microsoft Fabric** | Data platform integration | Premium |
| **Fabric Workspace** | Hosts semantic models and data | Standard |
| **Fabric Lakehouse** | Data storage and analytics | Standard |
| **Fabric Warehouse** | SQL endpoints for data | Standard |

## 🔐 Authentication Requirements

### Service Principal

A service principal is required for automated authentication:

```bash
# Create a service principal
az ad sp create-for-rbac --name mcp-platform-sp --skip-assignment

# Assign Contributor role to the service principal
az role assignment create --assignee "mcp-platform-sp" \
    --role "Contributor" \
    --resource-group mcp-platform-rg
```

### Managed Identity

For production deployments, use Managed Identity:

```bash
# Enable system-assigned identity for Function App
az functionapp identity assign --name mcp-platform-func --resource-group mcp-platform-rg

# Assign permissions to the identity
az role assignment create --assignee "mcp-platform-func" \
    --role "Key Vault Secrets User" \
    --scope "/subscriptions/your-subscription-id/resourceGroups/mcp-platform-rg/providers/Microsoft.KeyVault/vaults/mcp-platform-kv"
```

## 📦 Development Tools

### Version Control

- **Git**: 2.30.0 or higher
- **Git LFS**: Optional, for large files

```bash
# Check Git version
git --version

# Install Git LFS (optional)
git lfs install
```

### Code Editor

- **Visual Studio Code** (Recommended)
- **Extensions**: Python, Azure Functions, Azure Account, Pylance

```bash
# Install VS Code extensions
code --install-extension ms-python.python
code --install-extension ms-azuretools.vscode-azurefunctions
code --install-extension ms-azuretools.vscode-azure-account
code --install-extension ms-python.vscode-pylance
```

### Container Tools (Optional)

For local development with containers:

- **Docker**: 20.10.0 or higher
- **Docker Compose**: 2.0 or higher

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version
```

## 🧪 Testing Requirements

### Testing Frameworks

- **pytest**: 7.4.0 or higher
- **pytest-azurepipelines**: For Azure DevOps integration
- **pytest-cov**: For code coverage

```bash
# Install testing dependencies
pip install pytest pytest-azurepipelines pytest-cov pytest-mock
```

### Test Data

- **Fabric Test Workspace**: For integration testing
- **Test Semantic Models**: Sample models for testing
- **Mock Data**: Sample data for unit testing

## 🔧 CI/CD Requirements

### Azure DevOps

- **Organization**: Azure DevOps organization
- **Project**: Dedicated project for MCP Platform
- **Agent Pools**: Self-hosted or Microsoft-hosted agents
- **Service Connections**: Azure service connections configured

### GitHub Actions

- **Repository**: GitHub repository for the project
- **Secrets**: GitHub secrets configured for Azure authentication
- **Runners**: GitHub-hosted or self-hosted runners

## 📋 Checklist

Use this checklist to verify all prerequisites are met:

### Development Environment

- [ ] ✅ Operating system supported (Windows/macOS/Linux)
- [ ] ✅ Python 3.11+ installed
- [ ] ✅ pip installed and updated
- [ ] ✅ Git installed
- [ ] ✅ Code editor installed (VS Code recommended)
- [ ] ✅ Virtual environment created

### Azure Environment

- [ ] ✅ Azure account with active subscription
- [ ] ✅ Azure CLI installed and configured
- [ ] ✅ Required Azure CLI extensions installed
- [ ] ✅ Service principal created
- [ ] ✅ Resource group created
- [ ] ✅ Required permissions assigned

### Project Setup

- [ ] ✅ Repository cloned
- [ ] ✅ Dependencies installed
- [ ] ✅ Environment variables configured
- [ ] ✅ Azure authentication working
- [ ] ✅ Local development tested

## 🛠️ Troubleshooting

### Common Prerequisite Issues

#### Python Version Too Old

**Error**: `Python 3.11 or higher is required`

**Solution**:
```bash
# Install Python 3.11 using pyenv
pyenv install 3.11.8
pyenv global 3.11.8

# Or download from python.org
```

#### Azure CLI Not Found

**Error**: `az: command not found`

**Solution**: Ensure Azure CLI is in your PATH or reinstall it.

#### Insufficient Permissions

**Error**: `Insufficient permissions to perform this operation`

**Solution**:
```bash
# Check your current permissions
az role assignment list --assignee your-email@domain.com

# Request additional permissions from your administrator
```

#### Resource Quota Exceeded

**Error**: `Quota exceeded for resource type`

**Solution**:
```bash
# Check current usage and limits
az vm list-usage --location eastus

# Request quota increase
az support request create --type quota-increase
```

## 📚 Next Steps

Once all prerequisites are met:

1. **[Installation Guide](installation.md)** - Install the MCP Platform Framework
2. **[Configuration Guide](configuration.md)** - Configure your development environment
3. **[Quick Start](quick-start.md)** - Get started with basic development

## 🔗 Useful Links

- [Python Downloads](https://www.python.org/downloads/)
- [Azure CLI Installation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Git Downloads](https://git-scm.com/downloads)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Azure Portal](https://portal.azure.com/)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
