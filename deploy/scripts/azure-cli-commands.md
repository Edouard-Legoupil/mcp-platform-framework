# MCP Framework - Azure CLI Commands Reference

## Table of Contents
1. [Resource Creation Commands](#1-resource-creation-commands)
2. [Configuration Validation Commands](#2-configuration-validation-commands)
3. [Deployment Commands](#3-deployment-commands)
4. [Diagnostic Commands](#4-diagnostic-commands)
5. [Remediation Commands](#5-remediation-commands)

---

## 1. Resource Creation Commands

### 1.1 Create Storage Account
```bash
# Create storage account with required tags
az storage account create \
    --name <storage-account-name> \
    --resource-group <resource-group> \
    --location <location> \
    --sku Standard_LRS \
    --kind StorageV2 \
    --access-tier Hot \
    --enable-hierarchical-namespace false \
    --tags ApplicationName=<application-name> \
           BusinessOwner=<business-owner> \
           CostCentre=<cost-centre> \
           Environment=<environment> \
           Project=<project> \
           TechnicalOwner=<technical-owner>
```

### 1.2 Retrieve Storage Account Connection String
```bash
# Get connection string for AzureWebJobsStorage
az storage account show-connection-string \
    --name <storage-account-name> \
    --resource-group <resource-group> \
    --query connectionString \
    -o tsv
```

### 1.3 Update AzureWebJobsStorage Setting
```bash
# Update Function App with storage connection string
az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings AzureWebJobsStorage="<connection-string>"
```

### 1.4 Create Application Insights
```bash
az monitor app-insights create \
    --name <app-insights-name> \
    --resource-group <resource-group> \
    --location <location> \
    --kind web \
    --application-type web \
    --retention-time 90 \
    --tags ApplicationName=<application-name> \
           BusinessOwner=<business-owner> \
           CostCentre=<cost-centre> \
           Environment=<environment> \
           Project=<project> \
           TechnicalOwner=<technical-owner>
```

### 1.5 Create Function App (Consumption Plan)
```bash
az functionapp create \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --consumption-plan-location <location> \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --storage-account <storage-account-name> \
    --os-type Linux \
    --tags ApplicationName=<application-name> \
           BusinessOwner=<business-owner> \
           CostCentre=<cost-centre> \
           Environment=<environment> \
           Project=<project> \
           TechnicalOwner=<technical-owner> \
    --app-insights <app-insights-name>
```

---

## 2. Configuration Validation Commands

### 2.1 Validate Function App Runtime
```bash
# Check current runtime
az functionapp show \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "siteConfig.linuxFxVersion" \
    -o tsv

# Expected: python|3.11
# If incorrect, fix with:
az functionapp update \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --linux-fx-version 'python|3.11'
```

### 2.2 Validate Python Version
```bash
# Check current Python version
az functionapp config show \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "pythonVersion" \
    -o tsv

# Expected: 3.11
# If incorrect, fix with:
az functionapp config set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --python-version 3.11
```

### 2.3 Validate FUNCTIONS_WORKER_RUNTIME
```bash
# Check current worker runtime
az functionapp config appsettings list \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "[?name=='FUNCTIONS_WORKER_RUNTIME'].value | [0]" \
    -o tsv

# Expected: python
# If incorrect, fix with:
az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings FUNCTIONS_WORKER_RUNTIME=python
```

### 2.4 Validate FUNCTIONS_EXTENSION_VERSION
```bash
# Check current extension version
az functionapp config appsettings list \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "[?name=='FUNCTIONS_EXTENSION_VERSION'].value | [0]" \
    -o tsv

# Expected: ~4
# If incorrect, fix with:
az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings FUNCTIONS_EXTENSION_VERSION=~4
```

### 2.5 Validate SCM_DO_BUILD_DURING_DEPLOYMENT
```bash
# Check current setting
az functionapp config appsettings list \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "[?name=='SCM_DO_BUILD_DURING_DEPLOYMENT'].value | [0]" \
    -o tsv

# Expected: true
# If incorrect, fix with:
az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### 2.6 Validate ENABLE_ORYX_BUILD
```bash
# Check current setting
az functionapp config appsettings list \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "[?name=='ENABLE_ORYX_BUILD'].value | [0]" \
    -o tsv

# Expected: true
# If incorrect, fix with:
az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings ENABLE_ORYX_BUILD=true
```

### 2.7 Validate WEBSITE_RUN_FROM_PACKAGE
```bash
# Check current setting
az functionapp config appsettings list \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "[?name=='WEBSITE_RUN_FROM_PACKAGE'].value | [0]" \
    -o tsv

# Expected: 1
# If incorrect, fix with:
az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings WEBSITE_RUN_FROM_PACKAGE=1
```

### 2.8 Validate AzureWebJobsStorage
```bash
# Check current setting
az functionapp config appsettings list \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "[?name=='AzureWebJobsStorage'].value | [0]" \
    -o tsv

# Expected: Valid storage connection string
# If incorrect, fix with:
az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings AzureWebJobsStorage="<valid-connection-string>"
```

---

## 3. Deployment Commands

### 3.1 Deploy with Remote Build (Oryx)
```bash
# Deploy using Oryx remote build
az functionapp deployment source config-zip \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --src ./src/azure.zip
```

### 3.2 Deploy with Local Build
```bash
# Create deployment package
cd src/azure
zip -r ../azure-deployment.zip .
cd ../..

# Deploy with --no-build flag
az functionapp deployment source config-zip \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --src ./src/azure-deployment.zip \
    --no-build
```

### 3.3 Restart Function App
```bash
az functionapp restart \
    --name <function-app-name> \
    --resource-group <resource-group>
```

---

## 4. Diagnostic Commands

### 4.1 Check Function App Status
```bash
# Get Function App state
az functionapp show \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "state" \
    -o tsv

# Get all Function App details
az functionapp show \
    --name <function-app-name> \
    --resource-group <resource-group>
```

### 4.2 List Deployed Functions
```bash
az functionapp function list \
    --name <function-app-name> \
    --resource-group <resource-group>
```

### 4.3 Check Deployment Logs
```bash
# Get deployment logs
az functionapp deployment source show \
    --name <function-app-name> \
    --resource-group <resource-group>

# Get deployment log details
az functionapp deployment source show \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "properties.logUrl" \
    -o tsv
```

### 4.4 Check Oryx Build Status
```bash
# Check active deployments
az functionapp deployment list \
    --name <function-app-name> \
    --resource-group <resource-group>

# Check Oryx build logs
az functionapp deployment log show \
    --name <function-app-name> \
    --resource-group <resource-group>
```

### 4.5 Verify Host Storage Health
```bash
# Check if host storage is accessible
az functionapp show \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query "siteConfig.azureStorageAccounts" \
    -o json
```

---

## 5. Remediation Commands

### 5.1 Clear Deployment Locks
```bash
# Restart SCM site to clear deployment locks
az functionapp deployment scm restart \
    --name <function-app-name> \
    --resource-group <resource-group>
```

### 5.2 Force Restart Function App
```bash
# Force restart to clear any stuck processes
az functionapp restart \
    --name <function-app-name> \
    --resource-group <resource-group>
```

### 5.3 Fix Stuck Oryx Build
```bash
# Disable and re-enable Oryx build
az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings ENABLE_ORYX_BUILD=false

az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings ENABLE_ORYX_BUILD=true
```

### 5.4 Reset Function App Configuration
```bash
# Reset to known good configuration
az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings \
        FUNCTIONS_WORKER_RUNTIME=python \
        FUNCTIONS_EXTENSION_VERSION=~4 \
        WEBSITE_RUN_FROM_PACKAGE=1 \
        ENABLE_ORYX_BUILD=true \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### 5.5 Verify and Fix All Settings
```bash
# Complete configuration reset
az functionapp update \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --linux-fx-version 'python|3.11'

az functionapp config set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --python-version 3.11

az functionapp config appsettings set \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --settings \
        FUNCTIONS_WORKER_RUNTIME=python \
        FUNCTIONS_EXTENSION_VERSION=~4 \
        AzureWebJobsStorage="<connection-string>" \
        WEBSITE_RUN_FROM_PACKAGE=1 \
        ENABLE_ORYX_BUILD=true \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

---

## 6. Tag Management Commands

### 6.1 Add Tags to Existing Resources
```bash
# Add tags to Function App
az functionapp update \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --tags ApplicationName=<application-name> \
           BusinessOwner=<business-owner> \
           CostCentre=<cost-centre> \
           Environment=<environment> \
           Project=<project> \
           TechnicalOwner=<technical-owner>

# Add tags to Storage Account
az storage account update \
    --name <storage-account-name> \
    --resource-group <resource-group> \
    --tags ApplicationName=<application-name> \
           BusinessOwner=<business-owner> \
           CostCentre=<cost-centre> \
           Environment=<environment> \
           Project=<project> \
           TechnicalOwner=<technical-owner>
```

### 6.2 List All Resources with Tags
```bash
# List all resources in resource group with tags
az resource list \
    --resource-group <resource-group> \
    --query "[].{Name:name, Type:type, Tags:tags}" \
    -o json
```

---

## 7. Health Check Commands

### 7.1 Test Function App Health
```bash
# Get Function App URL
FUNCTION_APP_URL=$(az functionapp show \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --query defaultHostName \
    -o tsv)

# Test health endpoint
curl -s -o /dev/null -w "%{http_code}" "https://$FUNCTION_APP_URL/api/health"

# Expected: 200
```

### 7.2 Check Function App Logs
```bash
# Stream Function App logs
az webapp log tail \
    --name <function-app-name> \
    --resource-group <resource-group>
```

### 7.3 Download Function App Logs
```bash
# Download logs as zip file
az webapp log download \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --log-file "function-app-logs.zip"
```

---

## 8. Cleanup Commands

### 8.1 Delete Function App
```bash
az functionapp delete \
    --name <function-app-name> \
    --resource-group <resource-group> \
    --yes
```

### 8.2 Delete Storage Account
```bash
az storage account delete \
    --name <storage-account-name> \
    --resource-group <resource-group> \
    --yes
```

### 8.3 Delete Resource Group
```bash
az group delete \
    --name <resource-group> \
    --yes \
    --no-wait
```

---

## Usage Examples

### Complete Deployment Example
```bash
# Set environment variables
export RESOURCE_GROUP="mcp-dev-rg"
export FUNCTION_APP_NAME="mcp-dev-func"
export STORAGE_ACCOUNT_NAME="mcpdevstorage"
export LOCATION="eastus"

# Create resources
az storage account create --name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP --location $LOCATION --sku Standard_LRS

STORAGE_CONNECTION=$(az storage account show-connection-string --name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP --query connectionString -o tsv)

az functionapp create --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --consumption-plan-location $LOCATION --runtime python --runtime-version 3.11 --storage-account $STORAGE_ACCOUNT_NAME --os-type Linux

# Configure settings
az functionapp config appsettings set --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --settings \
    AzureWebJobsStorage="$STORAGE_CONNECTION" \
    FUNCTIONS_WORKER_RUNTIME=python \
    FUNCTIONS_EXTENSION_VERSION=~4 \
    WEBSITE_RUN_FROM_PACKAGE=1 \
    ENABLE_ORYX_BUILD=true \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Deploy
az functionapp deployment source config-zip --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --src ./src/azure.zip

# Verify
az functionapp show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --query state -o tsv
```

### Troubleshooting Stuck Oryx Build
```bash
# Check if deployment is stuck
az functionapp deployment list --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

# Restart SCM site
az functionapp deployment scm restart --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

# Restart Function App
az functionapp restart --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

# Check logs
az functionapp deployment log show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP
```