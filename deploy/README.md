# MCP Framework - Azure Functions v4 Deployment

## Overview

This directory contains deployment scripts and configuration for deploying the MCP Framework as an Azure Function App using **Azure Functions v4 Python programming model**.

## Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- Azure account with appropriate permissions
- Python 3.11+ installed locally (for testing)

## Quick Start

### 1. Configure Environment Variables

Copy the `.env.example` file to `.env` and fill in the required values:

```bash
cp .env.example .env
# Edit .env with your configuration
```

**Required Azure Resource Tags** (must be set in .env):
- `APPLICATION_NAME` - Application name
- `BUSINESS_OWNER` - Business owner email
- `COST_CENTRE` - Cost center code
- `ENVIRONMENT` - Deployment environment (Dev, Test, Prod)
- `PROJECT` - Project name
- `TECHNICAL_OWNER` - Technical owner email

### 2. Deploy

```bash
# Make deploy script executable
chmod +x deploy/scripts/deploy.sh

# Run deployment
./deploy/scripts/deploy.sh \
    --resource-group your-resource-group \
    --location eastus \
    --function-app-name your-function-app \
    --storage-account-name yourstorageaccount \
    --deployment-method remote
```

Or use environment variables from .env file:

```bash
# Deployment will automatically use values from .env
./deploy/scripts/deploy.sh
```

## Project Structure

```
mcp_framework/
├── src/
│   └── azure/
│       ├── __init__.py          # Package initialization
│       ├── function_app.py      # Azure Functions v4 implementation
│       ├── host.json            # Function App configuration
│       └── requirements.txt     # Production dependencies
├── .env.example                # Environment variables template
├── .env                        # Your environment variables (not committed)
├── .funcignore                 # Deployment ignore file
├── .gitignore                 # Git ignore file
└── deploy/
    └── scripts/
        └── deploy.sh            # Deployment script
```

## Azure Functions v4 Implementation

The implementation uses **Azure Functions v4 Python programming model** with explicit function decorators:

### Function App (`src/azure/function_app.py`)

- Single `app = func.FunctionApp()` instance
- All MCP endpoints implemented as individual functions with `@app.function_name` decorators
- All functions use `@app.route()` decorators for HTTP routing

### MCP Protocol Endpoints

| Function | Route | Method | Purpose |
|----------|-------|--------|---------|
| `mcp_health` | `/mcp/health` | GET | Server health check |
| `mcp_metadata` | `/mcp/metadata` | GET | Server capabilities |
| `mcp_tools_list` | `/mcp/tools` | GET | List all tools |
| `mcp_tools_metadata` | `/mcp/tools/{tool_name}` | GET | Tool metadata |
| `mcp_tools_execute` | `/mcp/tools/{tool_name}/execute` | POST | Execute tool |
| `mcp_resources_list` | `/mcp/resources` | GET | List all resources |
| `mcp_resources_access` | `/mcp/resources/{resource_name}` | GET | Access resource |
| `mcp_prompts_list` | `/mcp/prompts` | GET | List prompt templates |
| `mcp_prompts_get` | `/mcp/prompts/{prompt_name}` | GET | Get prompt template |
| `mcp_completions` | `/mcp/completions` | POST | Generate completion |

## Configuration Files

### host.json

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  },
  "functions": [
    "mcp_health",
    "mcp_metadata",
    "mcp_tools_list",
    "mcp_tools_metadata",
    "mcp_tools_execute",
    "mcp_resources_list",
    "mcp_resources_access",
    "mcp_prompts_list",
    "mcp_prompts_get",
    "mcp_completions"
  ]
}
```

### requirements.txt

Clean production dependencies with:
- `azure-functions>=1.21.0` (v4 compatible)
- `cryptography>=3.3.0,<42.0.0` (avoids Rust compilation)
- No development packages (black, flake8, mypy, pytest)

### .funcignore

Excludes unnecessary files from deployment:
- `.python_packages/` (Oryx build output)
- `__pycache__/`
- `.venv/` and other virtual environments
- `tests/` and other test files
- `docs/` and documentation
- `.env` and environment files

## Deployment Script

The `deploy.sh` script performs the following steps:

1. **Validation** - Checks Azure CLI, authentication, and configuration
2. **Infrastructure Creation** - Creates resource group, storage account, Application Insights
3. **Function App Creation** - Creates Function App with v4 configuration
4. **Configuration** - Sets all required Function App settings including tags
5. **Deployment** - Deploys the function app using Oryx (remote) or local build
6. **Verification** - Checks deployment status and tests MCP endpoints

### Usage

```bash
# Show help
./deploy/scripts/deploy.sh --help

# Deploy with command line arguments
./deploy/scripts/deploy.sh \
    --resource-group mcp-dev-rg \
    --location eastus \
    --function-app-name mcp-dev-func \
    --storage-account-name mcpdevstorage \
    --deployment-method remote

# Deploy using .env file
./deploy/scripts/deploy.sh
```

### Deployment Methods

- **remote** (default) - Uses Oryx build for automatic dependency resolution
- **local** - Uses local build with `--no-build` flag

## Environment Variables

### Azure Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_RESOURCE_GROUP` | Resource group name | `mcp-dev-rg` |
| `AZURE_LOCATION` | Azure region | `eastus` |
| `AZURE_FUNCTION_APP_NAME` | Function App name | `mcp-dev-func` |
| `AZURE_STORAGE_ACCOUNT_NAME` | Storage account name | `mcpdevstorage` |
| `AZURE_APP_INSIGHTS_NAME` | Application Insights name | `mcp-dev-appinsights` |

### Required Azure Resource Tags

| Variable | Description | Example |
|----------|-------------|---------|
| `APPLICATION_NAME` | Application name | `MCPFramework` |
| `BUSINESS_OWNER` | Business owner email | `business-owner@example.com` |
| `COST_CENTRE` | Cost center code | `CC001` |
| `ENVIRONMENT` | Deployment environment | `Development` |
| `PROJECT` | Project name | `MCPPlatform` |
| `TECHNICAL_OWNER` | Technical owner email | `tech-owner@example.com` |

### MCP Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_SERVER_NAME` | MCP server name | `MCP Framework Server` |
| `MCP_SERVER_VERSION` | MCP server version | `1.0.0` |
| `MCP_PROTOCOL_VERSION` | MCP protocol version | `2024-11-05` |
| `MCP_ENVIRONMENT` | MCP environment | `Development` |
| `MCP_DOMAIN` | MCP domain | `Unknown` |

### Deployment Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DEPLOYMENT_METHOD` | Deployment method | `remote` |

## Verification

After deployment, the script automatically verifies:

1. Function App is running
2. All MCP functions are deployed
3. MCP health endpoint responds with HTTP 200

### Manual Verification

```bash
# Check Function App status
az functionapp show --name your-function-app --resource-group your-rg --query state -o tsv

# List deployed functions
az functionapp function list --name your-function-app --resource-group your-rg

# Test MCP health endpoint
curl https://your-function-app.azurewebsites.net/mcp/health

# Test MCP metadata endpoint
curl https://your-function-app.azurewebsites.net/mcp/metadata

# Test MCP tools endpoint
curl https://your-function-app.azurewebsites.net/mcp/tools
```

## Troubleshooting

### Common Issues

#### Deployment stuck at "Running oryx build..."

**Solution:**
```bash
# Ensure WEBSITE_RUN_FROM_PACKAGE=1 is set
az functionapp config appsettings set \
    --name your-function-app \
    --resource-group your-rg \
    --settings WEBSITE_RUN_FROM_PACKAGE=1

# Restart SCM site
az functionapp deployment scm restart \
    --name your-function-app \
    --resource-group your-rg
```

#### "0 functions found" error

**Solution:**
- Ensure `host.json` lists all function names
- Ensure all functions have `@app.function_name` decorators
- Ensure `function_app.py` contains `app = func.FunctionApp()`

#### Module import errors

**Solution:**
- Check `requirements.txt` for missing dependencies
- Ensure all platform imports are available or handled gracefully
- Test imports locally: `python -c "from azure.function_app import app"`

### Debugging

Use the Azure CLI to check logs:

```bash
# Stream Function App logs
az webapp log tail --name your-function-app --resource-group your-rg

# Get deployment logs
az functionapp deployment log show --name your-function-app --resource-group your-rg

# Check Function App configuration
az functionapp config show --name your-function-app --resource-group your-rg
```

## Clean Up

To delete all resources:

```bash
# Delete Function App
az functionapp delete --name your-function-app --resource-group your-rg --yes

# Delete Storage Account
az storage account delete --name yourstorageaccount --resource-group your-rg --yes

# Delete Application Insights
az resource delete --name your-app-insights --resource-group your-rg --resource-type Microsoft.Insights/components --yes

# Delete Resource Group
az group delete --name your-rg --yes --no-wait
```

## Best Practices

1. **Use .env file** - Store all configuration in `.env` file (not committed to git)
2. **Validate before deployment** - Ensure all required tags are set
3. **Use remote build** - Recommended for automatic dependency resolution
4. **Monitor deployments** - Check logs and status after deployment
5. **Test endpoints** - Verify MCP endpoints are responding correctly

## Additional Resources

- [Azure Functions Python v4 Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Model Context Protocol Specification](https://github.com/modelcontextprotocol/specification)
- [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)
