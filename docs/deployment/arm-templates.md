# ARM Templates for MCP Framework Deployment

## 📄 Overview

This guide provides Azure Resource Manager (ARM) templates for deploying the MCP Platform Framework infrastructure. ARM templates allow you to declaratively define and deploy your Azure resources in a repeatable and consistent manner.

---

## 🏗️ Template Structure

### Directory Structure

```
templates/
├── main.bicep                    # Main Bicep template
├── main.json                     # Main ARM template (compiled)
├── parameters/
│   ├── dev.json                  # Development parameters
│   ├── test.json                 # Test parameters
│   ├── stag.json                 # Staging parameters
│   └── prod.json                # Production parameters
├── modules/
│   ├── function-app.bicep        # Function App module
│   ├── key-vault.bicep           # Key Vault module
│   ├── storage.bicep             # Storage module
│   ├── app-insights.bicep        # Application Insights module
│   ├── vnet.bicep                # Virtual Network module
│   └── fabric.bicep              # Fabric integration module
└── scripts/
    ├── deploy.ps1                # PowerShell deployment script
    └── deploy.sh                 # Bash deployment script
```

---

## 🚀 Quick Start

### Deploy Using ARM Template

```bash
# Set variables
RESOURCE_GROUP="mcp-prod-rg"
LOCATION="eastus"
TEMPLATE_FILE="./templates/main.json"
PARAMETERS_FILE="./templates/parameters/prod.json"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy template
az deployment group create \
    --name "mcp-deployment" \
    --resource-group $RESOURCE_GROUP \
    --template-file $TEMPLATE_FILE \
    --parameters @$PARAMETERS_FILE
```

### Deploy Using Bicep

```bash
# Deploy Bicep template directly
az deployment group create \
    --name "mcp-deployment" \
    --resource-group $RESOURCE_GROUP \
    --template-file ./templates/main.bicep \
    --parameters @./templates/parameters/prod.json
```

---

## 📋 Main ARM Template

### Complete Infrastructure Template (`main.json`)

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "apiProfile": "2023-03-01-hybrid",
  "parameters": {
    "environment": {
      "type": "string",
      "defaultValue": "dev",
      "allowedValues": ["dev", "test", "stag", "prod"],
      "metadata": {
        "description": "Deployment environment"
      }
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {
        "description": "Location for all resources"
      }
    },
    "domain": {
      "type": "string",
      "metadata": {
        "description": "MCP domain name (e.g., DonorManagement)"
      }
    },
    "owner": {
      "type": "string",
      "defaultValue": "DER",
      "metadata": {
        "description": "Domain owner team"
      }
    },
    "catalogEndpoint": {
      "type": "string",
      "defaultValue": "https://catalog.my-org.org/api/v1",
      "metadata": {
        "description": "Enterprise catalog API endpoint"
      }
    },
    "fabricWorkspace": {
      "type": "string",
      "defaultValue": "PROD",
      "metadata": {
        "description": "Microsoft Fabric workspace name"
      }
    },
    "enablePrivateEndpoints": {
      "type": "bool",
      "defaultValue": false,
      "metadata": {
        "description": "Enable private endpoints for security"
      }
    },
    "enableMonitoring": {
      "type": "bool",
      "defaultValue": true,
      "metadata": {
        "description": "Enable monitoring and diagnostics"
      }
    }
  },
  "variables": {
    "resourcePrefix": "[format('mcp-{0}-{1}', parameters('environment'), parameters('domain'))]",
    "storageAccountName": "[format('{0}sa', variables('resourcePrefix'))]",
    "keyVaultName": "[format('{0}-kv', variables('resourcePrefix'))]",
    "appInsightsName": "[format('{0}-appinsights', variables('resourcePrefix'))]",
    "functionAppName": "[format('{0}-func', variables('resourcePrefix'))]",
    "vnetName": "[format('{0}-vnet', variables('resourcePrefix'))]",
    "subnetName": "[format('{0}-subnet', variables('resourcePrefix'))]",
    "privateEndpointName": "[format('{0}-pe', variables('resourcePrefix'))]",
    "tags": {
      "Environment": "[parameters('environment')]",
      "Domain": "[parameters('domain')]",
      "Owner": "[parameters('owner')]",
      "Project": "MCP Platform Framework",
      "CostCenter": "IT",
      "ManagedBy": "Terraform/ARM"
    }
  },
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2023-01-01",
      "name": "[variables('storageAccountName')]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "Standard_LRS",
        "tier": "Standard"
      },
      "kind": "StorageV2",
      "properties": {
        "accessTier": "Hot",
        "supportsHttpsTrafficOnly": true,
        "allowBlobPublicAccess": false,
        "minimumTlsVersion": "TLS1_2"
      },
      "tags": "[variables('tags')]"
    },
    {
      "type": "Microsoft.KeyVault/vaults",
      "apiVersion": "2023-02-01",
      "name": "[variables('keyVaultName')]",
      "location": "[parameters('location')]",
      "properties": {
        "enabledForDeployment": true,
        "enabledForDiskEncryption": true,
        "enabledForTemplateDeployment": true,
        "enableSoftDelete": true,
        "softDeleteRetentionInDays": 90,
        "enablePurgeProtection": true,
        "enableRbacAuthorization": true,
        "sku": {
          "name": "standard",
          "family": "A"
        },
        "tenantId": "[subscription().tenantId]",
        "accessPolicies": []
      },
      "tags": "[variables('tags')]"
    },
    {
      "type": "Microsoft.Insights/components",
      "apiVersion": "2020-02-02",
      "name": "[variables('appInsightsName')]",
      "location": "[parameters('location')]",
      "kind": "web",
      "properties": {
        "Application_Type": "web",
        "Flow_Type": "Bluefield",
        "Request_Source": "rest"
      },
      "tags": "[variables('tags')]"
    },
    {
      "type": "Microsoft.Web/sites",
      "apiVersion": "2022-03-01",
      "name": "[variables('functionAppName')]",
      "location": "[parameters('location')]",
      "kind": "functionapp,linux",
      "properties": {
        "serverFarmId": "/subscriptions/[subscription().subscriptionId]/resourceGroups/[resourceGroup().name]/providers/Microsoft.Web/serverfarms/AzureFunctionsFlexConsumptionPlan",
        "reserved": true,
        "siteConfig": {
          "appSettings": [
            {
              "name": "AzureWebJobsStorage",
              "value": "[concat('DefaultEndpointsProtocol=https;AccountName=', variables('storageAccountName'), ';AccountKey=', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('storageAccountName')), '2023-01-01').keys[0].value, ';EndpointSuffix=core.windows.net')]"
            },
            {
              "name": "FUNCTIONS_EXTENSION_VERSION",
              "value": "~4"
            },
            {
              "name": "FUNCTIONS_WORKER_RUNTIME",
              "value": "python"
            },
            {
              "name": "PYTHON_VERSION",
              "value": "3.11"
            },
            {
              "name": "APPINSIGHTS_INSTRUMENTATIONKEY",
              "value": "[reference(resourceId('Microsoft.Insights/components', variables('appInsightsName')), '2020-02-02').InstrumentationKey]"
            },
            {
              "name": "MCP_ENVIRONMENT",
              "value": "[parameters('environment')]"
            },
            {
              "name": "MCP_DOMAIN",
              "value": "[parameters('domain')]"
            },
            {
              "name": "MCP_OWNER",
              "value": "[parameters('owner')]"
            },
            {
              "name": "MCP_CATALOG_ENDPOINT",
              "value": "[parameters('catalogEndpoint')]"
            },
            {
              "name": "FABRIC_ENDPOINT",
              "value": "https://api.fabric.microsoft.com"
            },
            {
              "name": "FABRIC_WORKSPACE",
              "value": "[parameters('fabricWorkspace')]"
            },
            {
              "name": "WEBSITE_RUN_FROM_PACKAGE",
              "value": "1"
            },
            {
              "name": "WEBSITE_CONTENTOVERWRITE",
              "value": "1"
            }
          ],
          "connectionStrings": [
            {
              "name": "AzureWebJobsStorage",
              "value": "[concat('DefaultEndpointsProtocol=https;AccountName=', variables('storageAccountName'), ';AccountKey=', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('storageAccountName')), '2023-01-01').keys[0].value, ';EndpointSuffix=core.windows.net')]",
              "type": "Custom"
            }
          ]
        },
        "httpsOnly": true,
        "clientAffinityEnabled": false
      },
      "dependsOn": [
        "[resourceId('Microsoft.Storage/storageAccounts', variables('storageAccountName'))]",
        "[resourceId('Microsoft.Insights/components', variables('appInsightsName'))]"
      ],
      "tags": "[variables('tags')]"
    }
  ],
  "outputs": {
    "storageAccountName": {
      "type": "string",
      "value": "[variables('storageAccountName')]"
    },
    "keyVaultName": {
      "type": "string",
      "value": "[variables('keyVaultName')]"
    },
    "appInsightsName": {
      "type": "string",
      "value": "[variables('appInsightsName')]"
    },
    "functionAppName": {
      "type": "string",
      "value": "[variables('functionAppName')]"
    },
    "functionAppEndpoint": {
      "type": "string",
      "value": "[concat('https://', variables('functionAppName'), '.azurewebsites.net')]"
    }
  }
}
```

---

## 📁 Bicep Templates

### Main Bicep Template (`main.bicep`)

```bicep
@description('MCP Platform Framework - Main Deployment Template')
param environment string = 'dev'
@allowed([
  'dev'
  'test' 
  'stag'
  'prod'
])
param location string = resourceGroup().location
param domain string
param owner string = 'DER'
param catalogEndpoint string = 'https://catalog.my-org.org/api/v1'
param fabricWorkspace string = 'PROD'
param enablePrivateEndpoints bool = false
param enableMonitoring bool = true

// Resource naming
var resourcePrefix = 'mcp-${environment}-${domain}'
var storageAccountName = '${resourcePrefix}sa'
var keyVaultName = '${resourcePrefix}-kv'
var appInsightsName = '${resourcePrefix}-appinsights'
var functionAppName = '${resourcePrefix}-func'
var vnetName = '${resourcePrefix}-vnet'
var subnetName = '${resourcePrefix}-subnet'

// Tags
var tags = {
  Environment: environment
  Domain: domain
  Owner: owner
  Project: 'MCP Platform Framework'
  CostCenter: 'IT'
  ManagedBy: 'Bicep/ARM'
}

// Deploy resources
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }
  tags: tags
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    enabledForDeployment: true
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    enableRbacAuthorization: true
    sku: {
      name: 'standard'
      family: 'A'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
  }
  tags: tags
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Bluefield'
    Request_Source: 'rest'
  }
  tags: tags
}

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.Web/serverfarms/AzureFunctionsFlexConsumptionPlan'
    reserved: true
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'PYTHON_VERSION'
          value: '3.11'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'MCP_ENVIRONMENT'
          value: environment
        }
        {
          name: 'MCP_DOMAIN'
          value: domain
        }
        {
          name: 'MCP_OWNER'
          value: owner
        }
        {
          name: 'MCP_CATALOG_ENDPOINT'
          value: catalogEndpoint
        }
        {
          name: 'FABRIC_ENDPOINT'
          value: 'https://api.fabric.microsoft.com'
        }
        {
          name: 'FABRIC_WORKSPACE'
          value: fabricWorkspace
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'WEBSITE_CONTENTOVERWRITE'
          value: '1'
        }
      ]
      connectionStrings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
          type: 'Custom'
        }
      ]
    }
    httpsOnly: true
    clientAffinityEnabled: false
  }
  dependsOn: [
    storageAccount
    appInsights
  ]
  tags: tags
}

// Outputs
output storageAccountName string = storageAccountName
output keyVaultName string = keyVaultName
output appInsightsName string = appInsightsName
output functionAppName string = functionAppName
output functionAppEndpoint string = 'https://${functionAppName}.azurewebsites.net'
```

---

## 📋 Parameter Files

### Development Parameters (`parameters/dev.json`)

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environment": {
      "value": "dev"
    },
    "location": {
      "value": "eastus"
    },
    "domain": {
      "value": "DonorManagement"
    },
    "owner": {
      "value": "DER"
    },
    "catalogEndpoint": {
      "value": "https://catalog-dev.my-org.org/api/v1"
    },
    "fabricWorkspace": {
      "value": "DEV"
    },
    "enablePrivateEndpoints": {
      "value": false
    },
    "enableMonitoring": {
      "value": true
    }
  }
}
```

### Production Parameters (`parameters/prod.json`)

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environment": {
      "value": "prod"
    },
    "location": {
      "value": "eastus"
    },
    "domain": {
      "value": "DonorManagement"
    },
    "owner": {
      "value": "DER"
    },
    "catalogEndpoint": {
      "value": "https://catalog.my-org.org/api/v1"
    },
    "fabricWorkspace": {
      "value": "PROD"
    },
    "enablePrivateEndpoints": {
      "value": true
    },
    "enableMonitoring": {
      "value": true
    }
  }
}
```

---

## 🧩 Modular Templates

### Function App Module (`modules/function-app.bicep`)

```bicep
@description('MCP Function App Module')
param functionAppName string
param location string
param storageAccountName string
param appInsightsName string
param environment string
param domain string
param owner string
param catalogEndpoint string
param fabricWorkspace string
param tags object = {}

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.Web/serverfarms/AzureFunctionsFlexConsumptionPlan'
    reserved: true
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${resourceGroup().listKeys('Microsoft.Storage/storageAccounts', storageAccountName).keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'PYTHON_VERSION'
          value: '3.11'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: resourceGroup().listKeys('Microsoft.Insights/components', appInsightsName).InstrumentationKey
        }
        {
          name: 'MCP_ENVIRONMENT'
          value: environment
        }
        {
          name: 'MCP_DOMAIN'
          value: domain
        }
        {
          name: 'MCP_OWNER'
          value: owner
        }
        {
          name: 'MCP_CATALOG_ENDPOINT'
          value: catalogEndpoint
        }
        {
          name: 'FABRIC_ENDPOINT'
          value: 'https://api.fabric.microsoft.com'
        }
        {
          name: 'FABRIC_WORKSPACE'
          value: fabricWorkspace
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'WEBSITE_CONTENTOVERWRITE'
          value: '1'
        }
      ]
      connectionStrings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${resourceGroup().listKeys('Microsoft.Storage/storageAccounts', storageAccountName).keys[0].value};EndpointSuffix=core.windows.net'
          type: 'Custom'
        }
      ]
    }
    httpsOnly: true
    clientAffinityEnabled: false
  }
  tags: tags
}

output functionAppId string = functionApp.id
output functionAppEndpoint string = 'https://${functionAppName}.azurewebsites.net'
```

### Key Vault Module (`modules/key-vault.bicep`)

```bicep
@description('MCP Key Vault Module')
param keyVaultName string
param location string
param environment string
param domain string
param owner string
param tags object = {}

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    enabledForDeployment: true
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    enableRbacAuthorization: true
    sku: {
      name: 'standard'
      family: 'A'
    }
    tenantId: subscription().tenantId
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: subscription().subscriptionId
        permissions: {
          keys: [
            'get'
            'list'
            'create'
            'import'
            'delete'
            'recover'
          ]
          secrets: [
            'get'
            'list'
            'set'
            'delete'
            'recover'
          ]
          certificates: [
            'get'
            'list'
            'create'
            'import'
            'delete'
            'recover'
          ]
        }
      }
    ]
  }
  tags: tags
}

output keyVaultId string = keyVault.id
output keyVaultUri string = keyVault.properties.vaultUri
```

### Virtual Network Module (`modules/vnet.bicep`)

```bicep
@description('MCP Virtual Network Module')
param vnetName string
param location string
param environment string
param domain string
param owner string
param addressPrefix string = '10.0.0.0/16'
param subnetPrefix string = '10.0.0.0/24'
param tags object = {}

resource vnet 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      {
        name: '${vnetName}-subnet'
        properties: {
          addressPrefix: subnetPrefix
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
    ]
  }
  tags: tags
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2023-05-01' = {
  name: '${vnetName}-subnet'
  parent: vnet
}

output vnetId string = vnet.id
output subnetId string = subnet.id
```

---

## 🚀 Deployment Scripts

### PowerShell Deployment Script (`scripts/deploy.ps1`)

```powershell
<#
.SYNOPSIS
    Deploys MCP Platform Framework infrastructure using ARM templates.
.DESCRIPTION
    This script deploys all required Azure resources for the MCP Platform Framework
    using ARM templates. It supports multiple environments and configurations.
.PARAMETER Environment
    The deployment environment (dev, test, stag, prod)
.PARAMETER Location
    The Azure region for deployment
.PARAMETER Domain
    The MCP domain name
.PARAMETER Owner
    The domain owner team
.PARAMETER TemplateFile
    Path to the ARM template file
.PARAMETER ParametersFile
    Path to the parameters file
.EXAMPLE
    .\deploy.ps1 -Environment prod -Domain DonorManagement
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "test", "stag", "prod")]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$true)]
    [string]$Domain,
    
    [Parameter(Mandatory=$false)]
    [string]$Owner = "DER",
    
    [Parameter(Mandatory=$false)]
    [string]$TemplateFile = ".\templates\main.json",
    
    [Parameter(Mandatory=$false)]
    [string]$ParametersFile = ".\templates\parameters\$($Environment).json"
)

# Login to Azure
Write-Host "Logging in to Azure..." -ForegroundColor Cyan
az login | Out-Null

# Set subscription
$subscription = az account show --query "id" -o tsv
az account set --subscription $subscription

# Create resource group
$resourceGroup = "mcp-${Environment}-${Domain}-rg"
Write-Host "Creating resource group: $resourceGroup" -ForegroundColor Cyan
az group create --name $resourceGroup --location $Location | Out-Null

# Validate template
Write-Host "Validating ARM template..." -ForegroundColor Cyan
az deployment group validate \
    --resource-group $resourceGroup \
    --template-file $TemplateFile \
    --parameters @$ParametersFile | Out-Null

# Deploy template
Write-Host "Deploying ARM template..." -ForegroundColor Cyan
$deploymentName = "mcp-${Environment}-${Domain}-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

$deployment = az deployment group create \
    --name $deploymentName \
    --resource-group $resourceGroup \
    --template-file $TemplateFile \
    --parameters @$ParametersFile

# Output deployment results
Write-Host "Deployment completed!" -ForegroundColor Green
$deployment | ConvertFrom-Json | Format-List

# Get outputs
Write-Host "`nDeployment Outputs:" -ForegroundColor Cyan
az deployment group show \
    --name $deploymentName \
    --resource-group $resourceGroup \
    --query "properties.outputs" | ConvertFrom-Json | Format-Table -AutoSize
```

### Bash Deployment Script (`scripts/deploy.sh`)

```bash
#!/bin/bash

# MCP Platform Framework Deployment Script
# Usage: ./deploy.sh -e <environment> -d <domain> [-l <location>] [-o <owner>]

set -e

# Parse arguments
while getopts ":e:d:l:o:" opt; do
  case $opt in
    e) ENVIRONMENT="$OPTARG" ;;
    d) DOMAIN="$OPTARG" ;;
    l) LOCATION="$OPTARG" ;;
    o) OWNER="$OPTARG" ;;
    \?) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
  esac
done

# Set defaults
ENVIRONMENT=${ENVIRONMENT:-"dev"}
DOMAIN=${DOMAIN:-"DonorManagement"}
LOCATION=${LOCATION:-"eastus"}
OWNER=${OWNER:-"DER"}
TEMPLATE_FILE="./templates/main.json"
PARAMETERS_FILE="./templates/parameters/${ENVIRONMENT}.json"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|test|stag|prod)$ ]]; then
    echo "Error: Invalid environment. Must be one of: dev, test, stag, prod"
    exit 1
fi

# Login to Azure
echo "Logging in to Azure..."
az login

# Set subscription
SUBSCRIPTION=$(az account show --query "id" -o tsv)
az account set --subscription $SUBSCRIPTION

# Create resource group
RESOURCE_GROUP="mcp-${ENVIRONMENT}-${DOMAIN}-rg"
echo "Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION

# Validate template
echo "Validating ARM template..."
az deployment group validate \
    --resource-group $RESOURCE_GROUP \
    --template-file $TEMPLATE_FILE \
    --parameters @$PARAMETERS_FILE

# Deploy template
echo "Deploying ARM template..."
DEPLOYMENT_NAME="mcp-${ENVIRONMENT}-${DOMAIN}-$(date +%Y%m%d-%H%M%S)"

az deployment group create \
    --name $DEPLOYMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --template-file $TEMPLATE_FILE \
    --parameters @$PARAMETERS_FILE

# Output deployment results
echo "Deployment completed!"
echo ""
echo "Deployment Outputs:"
az deployment group show \
    --name $DEPLOYMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.outputs" -o json | jq .

# Get function app endpoint
FUNCTION_APP_NAME="mcp-${ENVIRONMENT}-${DOMAIN}-func"
FUNCTION_APP_ENDPOINT="https://${FUNCTION_APP_NAME}.azurewebsites.net"

echo ""
echo "Function App Endpoint: $FUNCTION_APP_ENDPOINT"
echo "Resource Group: $RESOURCE_GROUP"
```

---

## 🎯 Advanced Deployment Scenarios

### Private Endpoint Deployment

```bicep
// Add to main.bicep
param enablePrivateEndpoints bool = false

// Conditional private endpoint deployment
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (enablePrivateEndpoints) {
  name: '${functionAppName}-pe'
  location: location
  properties: {
    subnet: {
      id: subnet.id
    }
    privateLinkServiceConnections: [
      {
        name: '${functionAppName}-pe-conn'
        properties: {
          privateLinkServiceId: functionApp.id
          groupIds: [
            'sites'
          ]
        }
      }
    ]
  }
  tags: tags
}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (enablePrivateEndpoints) {
  name: 'privatelink.azurewebsites.net'
  location: 'global'
  properties: {}
  tags: tags
}

resource privateDnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = if (enablePrivateEndpoints) {
  name: '${vnetName}-dns-link'
  parent: privateDnsZone
  properties: {
    virtualNetwork: {
      id: vnet.id
    }
    registrationEnabled: false
  }
  tags: tags
}

resource privateDnsRecord 'Microsoft.Network/privateDnsZones/A@2020-06-01' = if (enablePrivateEndpoints) {
  name: functionAppName
  parent: privateDnsZone
  properties: {
    aRecords: [
      {
        ipv4Address: privateEndpoint.properties.networkInterfaces[0].ipConfigurations[0].properties.privateIpAddress
      }
    ]
    ttlInSeconds: 300
  }
  tags: tags
}
```

### Monitoring Deployment

```bicep
// Add to main.bicep
param enableMonitoring bool = true

// Monitoring resources
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = if (enableMonitoring) {
  name: '${resourcePrefix}-log-analytics'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAnalyticsForStorageAccount: true
    }
  }
  tags: tags
}

resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (enableMonitoring) {
  name: '${functionAppName}-diagnostics'
  properties: {
    workspaceResourceId: logAnalytics.id
    logs: [
      {
        category: 'FunctionAppLogs'
        enabled: true
        retention: {
          enabled: true
          retentionDays: 30
        }
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retention: {
          enabled: true
          retentionDays: 30
        }
      }
    ]
  }
  scope: functionApp
  tags: tags
}

resource alertRules 'Microsoft.Insights/metricAlerts@2018-03-01' = if (enableMonitoring) {
  for alert in [
    {
      name: 'HighErrorRate'
      condition: 'Requests where ResponseCode == 5xx'
      threshold: 5
      window: 'PT5M'
      description: 'High number of failed requests'
    }
    {
      name: 'HighLatency'
      condition: 'Average RequestDuration > 5000'
      threshold: 1
      window: 'PT5M'
      description: 'High request latency'
    }
  ]: {
    name: '${functionAppName}-${alert.name}'
    location: 'global'
    properties: {
      description: alert.description
      severity: 3
      enabled: true
      scopes: [functionApp.id]
      evaluationFrequency: 'PT1M'
      windowSize: alert.window
      criteria: {
        odata.type: 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
        allOf: [
          {
            name: 'HighErrorRate'
            metricName: 'Requests'
            dimensions: [
              {
                name: 'ResponseCode'
                operator: 'Include'
                values: ['5xx']
              }
            ]
            operator: 'GreaterThan'
            threshold: alert.threshold
            timeAggregation: 'Total'
          }
        ]
      }
      actions: [
        {
          actionGroupId: '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.Insights/actionGroups/EmailAdmins'
          webHookProperties: {}
        }
      ]
    }
    tags: tags
  }
}
```

---

## 🔧 Template Customization

### Customizing for Different Domains

```json
{
  "parameters": {
    "domain": {
      "value": "FinanceManagement"
    },
    "owner": {
      "value": "FIN"
    }
  }
}
```

### Customizing for Different Regions

```json
{
  "parameters": {
    "location": {
      "value": "westeurope"
    }
  }
}
```

### Customizing Resource Naming

```bicep
// Custom naming convention
var resourcePrefix = 'mcp-${environment}-${domain}-${uniqueString(resourceGroup().id)}'
var storageAccountName = '${resourcePrefix}sa'
var keyVaultName = '${resourcePrefix}kv'
```

---

## 📊 Template Validation

### Validate Template Syntax

```bash
# Validate ARM template syntax
az deployment group validate \
    --resource-group $RESOURCE_GROUP \
    --template-file ./templates/main.json \
    --parameters @./templates/parameters/dev.json
```

### Check for Errors

```bash
# Check for template errors
az deployment group what-if \
    --resource-group $RESOURCE_GROUP \
    --template-file ./templates/main.json \
    --parameters @./templates/parameters/dev.json \
    --change-type Create
```

### Test Deployment

```bash
# Test deployment without actually creating resources
az deployment group what-if \
    --resource-group $RESOURCE_GROUP \
    --template-file ./templates/main.json \
    --parameters @./templates/parameters/dev.json
```

---

## 🔍 Troubleshooting

### Common Template Errors

#### Invalid Template Syntax

**Symptom:** `InvalidTemplate: Deployment template validation failed`

**Solution:**
```bash
# Validate template syntax
az deployment group validate \
    --resource-group $RESOURCE_GROUP \
    --template-file ./templates/main.json

# Use VS Code with ARM Tools extension for syntax highlighting
```

#### Missing Required Parameters

**Symptom:** `MissingParameter: Parameter 'domain' is required`

**Solution:**
```bash
# Check required parameters in template
grep -A 5 '"parameters"' ./templates/main.json

# Provide all required parameters
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file ./templates/main.json \
    --parameters domain=DonorManagement owner=DER
```

#### Resource Name Conflicts

**Symptom:** `ResourceNameInUse: The resource name 'mcp-dev-donor-sa' is already in use`

**Solution:**
```bash
# Use unique naming
var resourcePrefix = 'mcp-${environment}-${domain}-${uniqueString(resourceGroup().id)}'

# Or manually specify unique names
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file ./templates/main.json \
    --parameters storageAccountName=mcpdevdonor12345
```

#### Permission Issues

**Symptom:** `AuthorizationFailed: The client does not have permission to perform this action`

**Solution:**
```bash
# Check current permissions
az role assignment list --assignee $(az ad signed-in-user show --query id -o tsv)

# Assign required permissions
az role assignment create \
    --assignee $(az ad signed-in-user show --query id -o tsv) \
    --role Contributor \
    --scope /subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP
```

---

## 📚 Additional Resources

- [ARM Template Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/)
- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [ARM Template Best Practices](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/template-best-practices)
- [Bicep Best Practices](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/best-practices)
- [ARM Template Reference](https://learn.microsoft.com/en-us/azure/templates/)

---

## 🔄 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-05-01 | Initial ARM template documentation |
| 1.1.0 | 2026-05-15 | Added Bicep templates and modular structure |
| 1.2.0 | 2026-06-01 | Added deployment scripts and advanced scenarios |
| 1.3.0 | 2026-06-15 | Added troubleshooting guide |
