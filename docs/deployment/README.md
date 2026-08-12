# 🚀 Deployment Guide

**Deploy the MCP Platform Framework to Microsoft Azure**

This section provides comprehensive guides for deploying the MCP Platform Framework and domain repositories to Azure. Choose the deployment method that best fits your organization's workflow.

## 📋 Table of Contents

- [Deployment Overview](overview.md) - High-level deployment architecture and options
- [Prerequisites](prerequisites.md) - Azure requirements and setup
- [Azure Function App](function-app.md) - Function App deployment guide
- [ARM Templates](arm-templates.md) - Azure Resource Manager templates
- [Bicep Templates](bicep-templates.md) - Bicep deployment templates
- [Environment Configuration](environments.md) - Multi-environment setup

### CI/CD Pipelines
- [Azure DevOps](azure-devops.md) - Azure DevOps pipeline setup
- [GitHub Actions](github-actions.md) - GitHub Actions workflow setup
- [Pipeline Configuration](pipeline-config.md) - Customize CI/CD pipelines

## 🎯 Deployment Options

The MCP Platform Framework supports multiple deployment approaches:

| Approach | Best For | Complexity | Automation |
|----------|----------|------------|------------|
| **[Manual Deployment](function-app.md)** | Quick testing, development | Low | Manual |
| **[ARM Templates](arm-templates.md)** | Enterprise, production | Medium | High |
| **[Bicep Templates](bicep-templates.md)** | Modern Azure, recommended | Medium | High |
| **[Azure DevOps](azure-devops.md)** | Enterprise CI/CD | High | Full |
| **[GitHub Actions](github-actions.md)** | Open source, GitHub users | Medium | Full |

## 🏗️ Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP Deployment Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Azure Subscription                               │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │                    Resource Group (per environment)               │ │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │ │   │
│  │  │  │ Function App │  │ App Insights│  │ Key Vault   │              │ │   │
│  │  │  │ (MCP Service)│  │ (Telemetry) │  │ (Secrets)   │              │ │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘              │ │   │
│  │  │  ┌─────────────────────────────────────────────────────────────┐│ │   │
│  │  │  │                    Storage Account                              ││ │   │
│  │  │  │  • Function App Storage (AzureWebJobsStorage)                  ││ │   │
│  │  │  │  • Audit Logs (Blob Storage)                                    ││ │   │
│  │  │  └─────────────────────────────────────────────────────────────┘│ │   │
│  │  │  ┌─────────────┐  ┌─────────────┐                              │ │   │
│  │  │  │ Managed     │  │ Fabric      │                              │ │   │
│  │  │  │ Identity    │  │ Workspace   │                              │ │   │
│  │  │  └─────────────┘  └─────────────┘                              │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │                    Domain Repositories                          │ │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │ │   │
│  │  │  │ mcp-donor-  │  │ mcp-finance- │  │ mcp-supply-  │              │ │   │
│  │  │  │ management  │  │ domain      │  │ chain       │              │ │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘              │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Microsoft Fabric                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │                    Fabric Capacity                                  │ │   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │ │   │
│  │  │  │ Semantic    │  │ Warehouses  │  │ Lakehouses  │              │ │   │
│  │  │  │ Models      │  │ (SQL)       │  │ (Delta)     │              │ │   │
│  │  │  │ (Power BI)  │  │             │  │             │              │ │   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘              │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🌐 Environment Strategy

The MCP Platform Framework supports **multi-environment deployment**:

| Environment | Purpose | Configuration | Auto-Deploy |
|-------------|---------|---------------|-------------|
| **DEV** | Development, testing | Minimal, local testing | On PR merge |
| **TEST** | Integration testing | Full, shared resources | On main merge |
| **PROD** | Production | Full, production resources | Manual/Tag |

### Environment Isolation

Each environment should have:
- ✅ **Separate Resource Group** - `mcp-{domain}-{env}-rg`
- ✅ **Separate Function App** - `mcp-{domain}-{env}-func`
- ✅ **Separate Storage Account** - `mcp{domain}{env}storage`
- ✅ **Separate Key Vault** - `mcp-{domain}-{env}-kv`
- ✅ **Separate Application Insights** - `mcp-{domain}-{env}-appinsights`
- ✅ **Shared Fabric Workspace** - (or separate if needed)

## 🚀 Quick Deployment

### Using Bicep (Recommended)

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name mcp-donor-management-dev-rg --location eastus

# 3. Deploy infrastructure
az deployment group create \
    --resource-group mcp-donor-management-dev-rg \
    --template-file deployment/mcp-deployment.bicep \
    --parameters \
        projectName=donor-management \
        environment=dev \
        location=eastus \
        mcpDomain=DonorManagement

# 4. Deploy Function App
az functionapp deployment source config-zip \
    --resource-group mcp-donor-management-dev-rg \
    --name donor-management-dev-func \
    --src .
```

### Using ARM Template

```bash
# 1. Generate ARM template
python -m deployment.arm_template --save mcp-deployment.json

# 2. Deploy using ARM template
az deployment group create \
    --resource-group mcp-donor-management-dev-rg \
    --template-file mcp-deployment.json \
    --parameters @deployment/parameters.json
```

## 🔧 Configuration Reference

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `projectName` | Project/domain name | `donor-management` |
| `environment` | Deployment environment | `dev`, `test`, `prod` |
| `location` | Azure region | `eastus`, `westeurope` |
| `mcpDomain` | MCP domain name | `DonorManagement` |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `enableTelemetry` | Enable Application Insights | `true` |
| `enableAudit` | Enable audit logging | `true` |
| `enableAuthentication` | Enable authentication | `true` |
| `enableAuthorization` | Enable authorization | `true` |
| `enableClassification` | Enable data classification | `true` |
| `autoDiscoverTools` | Auto-discover tools | `true` |

## 📊 Deployment Checklist

### Pre-Deployment
- [ ] Azure subscription with required permissions
- [ ] Azure CLI installed and logged in
- [ ] Python 3.11+ installed
- [ ] Required Azure resources created (or will be created by template)
- [ ] Domain repository cloned and configured
- [ ] All dependencies in `requirements.txt`
- [ ] Environment variables configured
- [ ] CI/CD pipeline set up (optional but recommended)

### Post-Deployment
- [ ] Function App is running
- [ ] Health endpoint responds (`/api/health`)
- [ ] Tools are registered (`/api/tools`)
- [ ] Telemetry is being collected (check Application Insights)
- [ ] Audit logs are being written (check Blob Storage)
- [ ] Authentication is working (test with valid token)
- [ ] Authorization is enforced (test with different roles)
- [ ] Classification is enforced (test with different classification levels)

## 🛡️ Security Considerations

### Identity and Access
- 🔒 **Use Managed Identity** for Function App to access other Azure resources
- 🔒 **Enable System Assigned Identity** for the Function App
- 🔒 **Grant appropriate RBAC roles** to the Managed Identity
- 🔒 **Use User Assigned Identity** for cross-resource access

### Secrets Management
- 🔒 **Never embed secrets** in code or configuration files
- 🔒 **Use Azure Key Vault** for all secrets
- 🔒 **Reference Key Vault secrets** in Function App configuration
- 🔒 **Enable Key Vault soft delete** and purge protection

### Network Security
- 🔒 **Enable HTTPS only** for Function App
- 🔒 **Restrict inbound traffic** using NSGs if needed
- 🔒 **Use Private Endpoints** for sensitive resources
- 🔒 **Enable Storage Account firewall** for audit logs

## ⚡ Performance Optimization

### Function App Configuration
- ⚡ **Consumption Plan** for variable workloads (default)
- ⚡ **Premium Plan** for high-performance requirements
- ⚡ **Elastic Premium** for enterprise-scale workloads
- ⚡ **Always On** enabled for Premium plans
- ⚡ **Minimum Instances** set appropriately

### Resource Sizing
- ⚡ **Memory Limit**: 1536 MB (default), increase for memory-intensive operations
- ⚡ **Timeout**: 10 minutes (default), increase for long-running operations
- ⚡ **Concurrency**: Adjust based on expected load

### Caching
- ⚡ **Enable Application Insights sampling** for high-volume telemetry
- ⚡ **Cache Fabric metadata** to reduce API calls
- ⚡ **Cache JWT public keys** to improve authentication performance

## 📈 Monitoring and Observability

### Built-in Monitoring
- 📊 **Application Insights**: Automatic telemetry collection
- 📊 **Azure Monitor**: Metrics and alerts
- 📊 **Log Analytics**: Centralized logging
- 📊 **Audit Logs**: Immutable compliance logging

### Key Metrics to Monitor
| Metric | Description | Target |
|--------|-------------|--------|
| Request Count | Total requests | Baseline + growth |
| Request Duration | Average request time | < 500ms |
| Success Rate | Percentage of successful requests | > 99.9% |
| Error Rate | Percentage of failed requests | < 0.1% |
| Tool Execution Time | Time per tool execution | < 1s |
| Memory Usage | Function App memory | < 80% |
| Throttled Requests | Requests throttled | 0 |

### Alerts
Set up alerts for:
- ⚠️ **High Error Rate** (> 1% for 5 minutes)
- ⚠️ **High Latency** (> 1s average for 5 minutes)
- ⚠️ **High Memory Usage** (> 90% for 5 minutes)
- ⚠️ **Failed Deployments** (any deployment failure)
- ⚠️ **Authentication Failures** (> 5 in 1 minute)
- ⚠️ **Authorization Failures** (> 5 in 1 minute)

## 🔄 CI/CD Integration

### Recommended Pipeline Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE                               │
├─────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │
│  │  Build  │───▶│  Test   │───▶│ Security│───▶│ Deploy  │   │
│  │         │    │         │    │         │    │         │   │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘   │
│       │              │              │              │        │
│       ▼              ▼              ▼              ▼        │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    ARTIFACTS                               ││
│  │  • Build artifacts (wheel, sdist)                          ││
│  │  • Test results (JUnit XML)                               ││
│  │  • Coverage reports                                        ││
│  │  • Security reports (Safety, Bandit)                       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────┘
```

### Environment Promotion

```
┌─────────────────────────────────────────────────────────────┐
│                 ENVIRONMENT PROMOTION                          │
├─────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                   │
│  │  DEV    │───▶│  TEST   │───▶│  PROD   │                   │
│  │         │    │         │    │         │                   │
│  └─────────┘    └─────────┘    └─────────┘                   │
│       │              │              │                         │
│       ▼              ▼              ▼                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    TRIGGERS                               ││
│  │  • PR merge to main → DEV                                ││
│  │  • PR merge to main → TEST (manual approval)              ││
│  │  • Release tag → PROD (manual approval)                   ││
│  └─────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Troubleshooting

### Common Deployment Issues

#### Function App Deployment Fails
**Symptoms**: Deployment fails with "Deployment failed" error

**Solutions**:
- ✅ Check Azure CLI version (`az --version`)
- ✅ Verify you have Contributor role on the resource group
- ✅ Check the deployment logs for specific errors
- ✅ Ensure Python 3.11 is selected in Function App configuration
- ✅ Verify all dependencies are in `requirements.txt`

#### Function App Won't Start
**Symptoms**: Function App shows "Starting" status indefinitely

**Solutions**:
- ✅ Check Application Insights for startup errors
- ✅ Verify `FUNCTIONS_WORKER_RUNTIME` is set to `python`
- ✅ Check `FUNCTIONS_EXTENSION_VERSION` is set to `~4`
- ✅ Ensure `AzureWebJobsStorage` connection string is valid
- ✅ Check for import errors in your code

#### Tools Not Registered
**Symptoms**: Tools are not appearing in `/api/tools` endpoint

**Solutions**:
- ✅ Verify `MCP_DOMAIN` environment variable is set
- ✅ Check that tool decorators are applied correctly
- ✅ Ensure `auto_discover_tools` is enabled
- ✅ Check for Python import errors
- ✅ Verify tool modules are in the `tool_paths`

#### Authentication Fails
**Symptoms**: Authentication always fails with 401 error

**Solutions**:
- ✅ Verify `AZURE_TENANT_ID` is set correctly
- ✅ Check `AZURE_CLIENT_ID` for Managed Identity
- ✅ Ensure Managed Identity is assigned to Function App
- ✅ Verify token is valid and not expired
- ✅ Check token audience matches Function App client ID

#### Fabric Connectivity Fails
**Symptoms**: Fabric queries fail with connection errors

**Solutions**:
- ✅ Verify Managed Identity has Fabric permissions
- ✅ Check Fabric workspace exists and is accessible
- ✅ Ensure `FABRIC_WORKSPACE_NAME` is set correctly
- ✅ Verify Managed Identity has "Fabric Contributor" role
- ✅ Check for network restrictions (firewalls, NSGs)

### Debugging Tools

#### Azure CLI
```bash
# Check Function App logs
az webapp log tail --name my-function-app --resource-group my-rg

# Check deployment status
az functionapp deployment source show --name my-function-app --resource-group my-rg

# Check Function App configuration
az functionapp config show --name my-function-app --resource-group my-rg
```

#### Application Insights
```bash
# Query Application Insights
az monitor app-insights query \
    --app my-app-insights \
    --resource-group my-rg \
    --query "requests | where success == false | take 10"
```

#### Kudu Console
```bash
# Access Kudu console
https://my-function-app.scm.azurewebsites.net/DebugConsole

# Check environment variables
printenv

# Check Python version
python --version

# Check installed packages
pip list
```

## 📚 Next Steps

- **[Deployment Overview](overview.md)** - Understand the deployment architecture
- **[Azure Function App](function-app.md)** - Detailed Function App deployment
- **[ARM Templates](arm-templates.md)** - Infrastructure as Code with ARM
- **[Bicep Templates](bicep-templates.md)** - Modern deployment with Bicep
- **[Azure DevOps](azure-devops.md)** - Set up CI/CD with Azure DevOps
- **[GitHub Actions](github-actions.md)** - Set up CI/CD with GitHub Actions

---

**🚀 Ready to deploy?**

- **First deployment?** Start with [Deployment Overview](overview.md)
- **Using Azure DevOps?** See [Azure DevOps Pipeline](azure-devops.md)
- **Using GitHub?** See [GitHub Actions Pipeline](github-actions.md)
- **Need templates?** See [ARM Templates](arm-templates.md) or [Bicep Templates](bicep-templates.md)
