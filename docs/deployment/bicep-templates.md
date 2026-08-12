# Bicep Templates for MCP Framework Deployment

## 📄 Overview

This guide provides comprehensive Bicep templates for deploying the MCP Platform Framework infrastructure. Bicep is a domain-specific language (DSL) for deploying Azure resources declaratively, offering a cleaner syntax and better development experience than ARM JSON templates.

---

## 🏗️ Bicep vs ARM Templates

### Why Use Bicep?

| Feature | Bicep | ARM JSON |
|---------|-------|----------|
| **Syntax** | Clean, concise DSL | Verbose JSON |
| **Readability** | ✅ High | ❌ Low |
| **Maintainability** | ✅ Easy | ⚠️ Complex |
| **Tooling** | ✅ First-class | ✅ Mature |
| **Validation** | ✅ Built-in | ✅ Built-in |
| **Modularity** | ✅ Native | ⚠️ Workarounds |
| **Type Safety** | ✅ Strong | ❌ Weak |

### Bicep Advantages for MCP Framework

1. **Simplified Syntax**: Clean, readable code for complex infrastructure
2. **Type Safety**: Compile-time validation of resource properties
3. **Modular Design**: Native support for modules and reusable components
4. **Better Tooling**: First-class support in VS Code, Azure CLI, etc.
5. **Automatic Conversion**: Can convert existing ARM templates to Bicep

---

## 🚀 Quick Start with Bicep

### Install Bicep CLI

```bash
# Install Bicep CLI
az bicep install

# Verify installation
az bicep version
```

### Deploy Using Bicep

```bash
# Set variables
RESOURCE_GROUP="mcp-prod-rg"
LOCATION="eastus"
TEMPLATE_FILE="./templates/main.bicep"
PARAMETERS="environment=prod domain=DonorManagement owner=DER"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy Bicep template
az deployment group create \
    --name "mcp-deployment" \
    --resource-group $RESOURCE_GROUP \
    --template-file $TEMPLATE_FILE \
    --parameters $PARAMETERS
```

### Convert ARM to Bicep

```bash
# Convert existing ARM template to Bicep
az bicep decompile --file ./templates/main.json

# Output will be main.bicep
```

---

## 📁 Main Bicep Template

### Complete Infrastructure Template (`main.bicep`)

```bicep
@description('MCP Platform Framework - Complete Infrastructure Deployment')

// ============================================
// PARAMETERS
// ============================================

param environment string = 'dev'
@allowed([
  'dev'
  'test'
  'stag'
  'prod'
])
@description('Deployment environment')

param location string = resourceGroup().location
@description('Azure region for deployment')

param domain string
@description('MCP domain name (e.g., DonorManagement, Finance, SupplyChain)')

param owner string = 'DER'
@description('Domain owner team code')

param catalogEndpoint string = 'https://catalog.unhcr.org/api/v1'
@description('Enterprise catalog API endpoint')

param fabricWorkspace string = 'PROD'
@description('Microsoft Fabric workspace name')

param enablePrivateEndpoints bool = false
@description('Enable private endpoints for enhanced security')

param enableMonitoring bool = true
@description('Enable comprehensive monitoring and diagnostics')

param enableBackup bool = true
@description('Enable automated backups')

param storageAccountSku string = 'Standard_LRS'
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_ZRS'
  'Premium_LRS'
])
@description('Storage account SKU')

param keyVaultSku string = 'standard'
@allowed([
  'standard'
  'premium'
])
@description('Key Vault SKU')

// ============================================
// VARIABLES
// ============================================

var resourcePrefix = 'mcp-${environment}-${domain}'
var storageAccountName = '${resourcePrefix}sa'
var keyVaultName = '${resourcePrefix}-kv'
var appInsightsName = '${resourcePrefix}-appinsights'
var functionAppName = '${resourcePrefix}-func'
var vnetName = '${resourcePrefix}-vnet'
var subnetName = '${resourcePrefix}-subnet'
var logAnalyticsName = '${resourcePrefix}-loganalytics'
var actionGroupName = '${resourcePrefix}-alerts'

var tags = {
  Environment: environment
  Domain: domain
  Owner: owner
  Project: 'MCP Platform Framework'
  CostCenter: 'IT'
  ManagedBy: 'Bicep'
  Version: '1.0.0'
}

// ============================================
// RESOURCES
// ============================================

// Storage Account for Function App
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageAccountSku
    tier: 'Standard'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    allowSharedKeyAccess: true
    
    // Enable static website for documentation hosting
    staticWebsite: {
      enabled: true
      indexDocument: 'index.html'
      error404Document: '404.html'
    }
  }
  tags: tags
}

// Key Vault for secrets management
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
      name: keyVaultSku
      family: 'A'
    }
    
    tenantId: subscription().tenantId
    
    // Initial access policy for deployment
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
            'backup'
            'restore'
          ]
          secrets: [
            'get'
            'list'
            'set'
            'delete'
            'recover'
            'backup'
            'restore'
          ]
          certificates: [
            'get'
            'list'
            'create'
            'import'
            'delete'
            'recover'
            'backup'
            'restore'
          ]
        }
      }
    ]
  }
  tags: tags
}

// Application Insights for monitoring
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Bluefield'
    Request_Source: 'rest'
    DisableIpMasking: false
    DisableLocalAuth: false
    
    // Enable sampling for high-volume scenarios
    SamplingPercentage: 100
    
    // Enable live metrics
    EnableLiveMetrics: true
  }
  tags: tags
}

// Log Analytics workspace for centralized logging
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = if (enableMonitoring) {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAnalyticsForStorageAccount: true
      searchVersion: 1
    }
    workspaceCapping: {
      dailyQuotaGb: -1  // Unlimited
    }
  }
  tags: tags
}

// Function App - The core MCP hosting platform
resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: '/subscriptions/${subscription().subscriptionId}/resourceGroups/${resourceGroup().name}/providers/Microsoft.Web/serverfarms/AzureFunctionsFlexConsumptionPlan'
    reserved: true
    
    siteConfig: {
      // Application settings
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
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'WEBSITE_CONTENTOVERWRITE'
          value: '1'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: '${functionAppName}-content'
        }
        
        // MCP Framework settings
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
          name: 'MCP_VERSION'
          value: '1.0.0'
        }
        {
          name: 'MCP_CATALOG_ENDPOINT'
          value: catalogEndpoint
        }
        {
          name: 'MCP_TELEMETRY_ENABLED'
          value: '${enableMonitoring}'
        }
        {
          name: 'MCP_AUDIT_ENABLED'
          value: 'true'
        }
        {
          name: 'MCP_DEBUG'
          value: '${environment == \'dev\' ? \'true\' : \'false\'}'
        }
        
        // Fabric integration
        {
          name: 'FABRIC_ENDPOINT'
          value: 'https://api.fabric.microsoft.com'
        }
        {
          name: 'FABRIC_WORKSPACE'
          value: fabricWorkspace
        }
        {
          name: 'FABRIC_TENANT_ID'
          value: subscription().tenantId
        }
        
        // Security settings
        {
          name: 'WEBSITE_ENABLE_APP_SERVICE_DIAGNOSTIC'
          value: 'true'
        }
        {
          name: 'WEBSITE_HEALTH_CHECK_EVOLVED'
          value: '1'
        }
        {
          name: 'HEALTH_CHECK_PATH'
          value: '/api/health'
        }
      ]
      
      // Connection strings
      connectionStrings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
          type: 'Custom'
        }
      ]
      
      // HTTP settings
      http20Enabled: true
      minTlsVersion: '1.2'
      ftpsState: 'FtpsOnly'
      
      // Always On for Premium plans
      alwaysOn: false
      
      // CORS settings
      cors: {
        allowedOrigins: [
          'https://unhcr.org'
          'https://portal.unhcr.org'
          'https://localhost:3000'
          'https://localhost:8080'
        ]
        allowedMethods: [
          'GET'
          'POST'
          'OPTIONS'
          'HEAD'
        ]
        allowedHeaders: [
          'Content-Type'
          'Authorization'
          'X-Request-ID'
          'X-MCP-Version'
        ]
        exposedHeaders: [
          'X-Request-ID'
          'X-MCP-Version'
        ]
        maxAgeInSeconds: 86400
      }
    }
    
    // Function App settings
    httpsOnly: true
    clientAffinityEnabled: false
    clientCertEnabled: false
    hostNamesDisabled: false
    
    // Identity
    identity: {
      type: 'SystemAssigned'
    }
  }
  dependsOn: [
    storageAccount
    appInsights
  ]
  tags: tags
}

// Virtual Network for private connectivity
resource vnet 'Microsoft.Network/virtualNetworks@2023-05-01' = if (enablePrivateEndpoints) {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: '10.0.1.0/24'
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
          
          // Service endpoints for Azure services
          serviceEndpoints: [
            {
              service: 'Microsoft.Storage'
              locations: [
                location
              ]
            }
            {
              service: 'Microsoft.KeyVault'
              locations: [
                location
              ]
            }
            {
              service: 'Microsoft.Web'
              locations: [
                location
              ]
            }
          ]
        }
      }
    ]
    
    // DNS servers
    dhcpOptions: {
      dnsServers: [
        '168.63.129.16'
      ]
    }
  }
  tags: tags
}

// Private Endpoint for Function App
resource functionAppPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (enablePrivateEndpoints) {
  name: '${functionAppName}-pe'
  location: location
  properties: {
    subnet: {
      id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, subnetName)
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
  dependsOn: [
    functionApp
    vnet
  ]
  tags: tags
}

// Private DNS Zone for Function App
resource functionAppPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (enablePrivateEndpoints) {
  name: 'privatelink.azurewebsites.net'
  location: 'global'
  properties: {}
  tags: tags
}

// DNS Zone Link to VNET
resource functionAppDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = if (enablePrivateEndpoints) {
  name: '${vnetName}-dns-link'
  parent: functionAppPrivateDnsZone
  properties: {
    virtualNetwork: {
      id: vnet.id
    }
    registrationEnabled: false
  }
  dependsOn: [
    functionAppPrivateDnsZone
    vnet
  ]
  tags: tags
}

// DNS A Record for Function App
resource functionAppDnsRecord 'Microsoft.Network/privateDnsZones/A@2020-06-01' = if (enablePrivateEndpoints) {
  name: functionAppName
  parent: functionAppPrivateDnsZone
  properties: {
    aRecords: [
      {
        ipv4Address: functionAppPrivateEndpoint.properties.networkInterfaces[0].ipConfigurations[0].properties.privateIpAddress
      }
    ]
    ttlInSeconds: 300
  }
  dependsOn: [
    functionAppPrivateEndpoint
    functionAppPrivateDnsZone
  ]
  tags: tags
}

// Private Endpoint for Storage Account
resource storagePrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (enablePrivateEndpoints) {
  name: '${storageAccountName}-pe'
  location: location
  properties: {
    subnet: {
      id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, subnetName)
    }
    privateLinkServiceConnections: [
      {
        name: '${storageAccountName}-pe-conn'
        properties: {
          privateLinkServiceId: storageAccount.id
          groupIds: [
            'blob'
            'file'
            'table'
            'queue'
          ]
        }
      }
    ]
  }
  dependsOn: [
    storageAccount
    vnet
  ]
  tags: tags
}

// Private DNS Zone for Storage
resource storagePrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (enablePrivateEndpoints) {
  name: 'privatelink.blob.core.windows.net'
  location: 'global'
  properties: {}
  tags: tags
}

// DNS Zone Link for Storage
resource storageDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = if (enablePrivateEndpoints) {
  name: '${vnetName}-storage-dns-link'
  parent: storagePrivateDnsZone
  properties: {
    virtualNetwork: {
      id: vnet.id
    }
    registrationEnabled: false
  }
  dependsOn: [
    storagePrivateDnsZone
    vnet
  ]
  tags: tags
}

// Private Endpoint for Key Vault
resource keyVaultPrivateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = if (enablePrivateEndpoints) {
  name: '${keyVaultName}-pe'
  location: location
  properties: {
    subnet: {
      id: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, subnetName)
    }
    privateLinkServiceConnections: [
      {
        name: '${keyVaultName}-pe-conn'
        properties: {
          privateLinkServiceId: keyVault.id
          groupIds: [
            'vault'
          ]
        }
      }
    ]
  }
  dependsOn: [
    keyVault
    vnet
  ]
  tags: tags
}

// Private DNS Zone for Key Vault
resource keyVaultPrivateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (enablePrivateEndpoints) {
  name: 'privatelink.vaultcore.azure.net'
  location: 'global'
  properties: {}
  tags: tags
}

// DNS Zone Link for Key Vault
resource keyVaultDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = if (enablePrivateEndpoints) {
  name: '${vnetName}-kv-dns-link'
  parent: keyVaultPrivateDnsZone
  properties: {
    virtualNetwork: {
      id: vnet.id
    }
    registrationEnabled: false
  }
  dependsOn: [
    keyVaultPrivateDnsZone
    vnet
  ]
  tags: tags
}

// Diagnostic Settings for Monitoring
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
      {
        category: 'ApplicationInsights'
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
  dependsOn: [
    functionApp
    logAnalytics
  ]
  tags: tags
}

// Alert Rules for Monitoring
resource alertRules 'Microsoft.Insights/metricAlerts@2018-03-01' = if (enableMonitoring) {
  for alert in [
    {
      name: 'HighErrorRate'
      condition: 'Requests'
      metricName: 'Requests'
      dimensions: [{ name: 'ResponseCode', operator: 'Include', values: ['5xx'] }]
      operator: 'GreaterThan'
      threshold: 5
      timeAggregation: 'Total'
      windowSize: 'PT5M'
      evaluationFrequency: 'PT1M'
      severity: 3
      description: 'High number of failed requests (5xx errors)'
    }
    {
      name: 'HighLatency'
      condition: 'RequestDuration'
      metricName: 'RequestDuration'
      dimensions: []
      operator: 'GreaterThan'
      threshold: 5000
      timeAggregation: 'Average'
      windowSize: 'PT5M'
      evaluationFrequency: 'PT1M'
      severity: 2
      description: 'High request latency (> 5 seconds)'
    }
    {
      name: 'HighFunctionExecutionTime'
      condition: 'FunctionExecutionUnits'
      metricName: 'FunctionExecutionUnits'
      dimensions: []
      operator: 'GreaterThan'
      threshold: 10000000  // 10,000,000 = 10,000 milliseconds * 1000 (units)
      timeAggregation: 'Total'
      windowSize: 'PT5M'
      evaluationFrequency: 'PT1M'
      severity: 2
      description: 'High function execution time'
    }
    {
      name: 'HighFunctionExecutionCount'
      condition: 'FunctionExecutionCount'
      metricName: 'FunctionExecutionCount'
      dimensions: []
      operator: 'GreaterThan'
      threshold: 1000
      timeAggregation: 'Total'
      windowSize: 'PT1H'
      evaluationFrequency: 'PT5M'
      severity: 1
      description: 'High function execution count (> 1000 per hour)'
    }
  ]: {
    name: '${functionAppName}-${alert.name}'
    location: 'global'
    properties: {
      description: alert.description
      severity: alert.severity
      enabled: true
      scopes: [functionApp.id]
      evaluationFrequency: alert.evaluationFrequency
      windowSize: alert.windowSize
      criteria: {
        odata.type: 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
        allOf: [
          {
            name: alert.name
            metricName: alert.metricName
            dimensions: alert.dimensions
            operator: alert.operator
            threshold: alert.threshold
            timeAggregation: alert.timeAggregation
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
    dependsOn: [
      functionApp
    ]
    tags: tags
  }
}

// Action Group for Alerts
resource actionGroup 'Microsoft.Insights/actionGroups@2022-01-01' = if (enableMonitoring) {
  name: actionGroupName
  location: 'global'
  properties: {
    groupShortName: 'MCPAlerts'
    enabled: true
    emailReceivers: [
      {
        name: 'MCPAdmins'
        emailAddress: 'mcp-alerts@unhcr.org'
        useCommonAlertSchema: true
      }
    ]
    smsReceivers: []
    armRoleReceivers: []
    azureAppPushReceivers: []
    azureFunctionReceivers: []
    logicAppReceivers: []
    webHookReceivers: []
    itsmReceivers: []
    automationRunbookReceivers: []
    voiceReceivers: []
    eventHubReceivers: []
  }
  tags: tags
}

// Backup Policy for Function App
resource backupPolicy 'Microsoft.Web/sites/backupPolicies@2022-03-01' = if (enableBackup) {
  name: '${functionAppName}/default'
  properties: {
    enabled: true
    backupSchedule: {
      frequencyInterval: 1
      frequencyUnit: 'Day'
      keepAtLeastOneBackup: true
      retentionPeriodInDays: 7
    }
    storageAccountUrl: 'https://${storageAccountName}.blob.core.windows.net/backups'
  }
  dependsOn: [
    functionApp
    storageAccount
  ]
  tags: tags
}

// ============================================
// OUTPUTS
// ============================================

output storageAccountName string = storageAccountName
output storageAccountId string = storageAccount.id
output storageAccountPrimaryKey string = storageAccount.listKeys().keys[0].value
output storageAccountConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'

output keyVaultName string = keyVaultName
output keyVaultId string = keyVault.id
output keyVaultUri string = keyVault.properties.vaultUri

output appInsightsName string = appInsightsName
output appInsightsId string = appInsights.id
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = 'InstrumentationKey=${appInsights.properties.InstrumentationKey};IngestionEndpoint=https://${location}.in.applicationinsights.azure.com/'

output functionAppName string = functionAppName
output functionAppId string = functionApp.id
output functionAppEndpoint string = 'https://${functionAppName}.azurewebsites.net'
output functionAppHostNames array = functionApp.properties.hostNames

output vnetName string = if (enablePrivateEndpoints) { vnetName } else { '' }
output vnetId string = if (enablePrivateEndpoints) { vnet.id } else { '' }
output subnetId string = if (enablePrivateEndpoints) { resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, subnetName) } else { '' }

output logAnalyticsName string = if (enableMonitoring) { logAnalyticsName } else { '' }
output logAnalyticsId string = if (enableMonitoring) { logAnalytics.id } else { '' }
output logAnalyticsWorkspaceId string = if (enableMonitoring) { logAnalytics.properties.customerId } else { '' }

output privateEndpointEnabled bool = enablePrivateEndpoints
output monitoringEnabled bool = enableMonitoring
output backupEnabled bool = enableBackup
```

---

## 🧩 Modular Bicep Templates

### Benefits of Modular Design

1. **Reusability**: Use the same module across multiple deployments
2. **Maintainability**: Update modules independently
3. **Readability**: Smaller, focused files are easier to understand
4. **Testing**: Test modules in isolation
5. **Collaboration**: Different teams can work on different modules

### Module Structure

```
templates/
├── main.bicep                    # Main deployment template
├── modules/
│   ├── function-app.bicep        # Function App module
│   ├── key-vault.bicep           # Key Vault module
│   ├── storage.bicep             # Storage module
│   ├── app-insights.bicep        # Application Insights module
│   ├── vnet.bicep                # Virtual Network module
│   ├── monitoring.bicep          # Monitoring module
│   ├── security.bicep            # Security module
│   └── fabric.bicep              # Fabric integration module
└── parameters/
    ├── dev.bicepparam            # Development parameters
    ├── test.bicepparam            # Test parameters
    ├── stag.bicepparam            # Staging parameters
    └── prod.bicepparam           # Production parameters
```

### Function App Module (`modules/function-app.bicep`)

```bicep
@description('MCP Function App Module - Deploys a Function App with MCP-specific configuration')

param functionAppName string
param location string
param storageAccountName string
param appInsightsName string
param environment string
param domain string
param owner string
param catalogEndpoint string
param fabricWorkspace string
param fabricTenantId string = subscription().tenantId
param enableMonitoring bool = true
param enablePrivateEndpoints bool = false
param tags object = {}

// Deploy Function App
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
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'WEBSITE_CONTENTOVERWRITE'
          value: '1'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${resourceGroup().listKeys('Microsoft.Storage/storageAccounts', storageAccountName).keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: '${functionAppName}-content'
        }
        
        // MCP Framework settings
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
          name: 'MCP_VERSION'
          value: '1.0.0'
        }
        {
          name: 'MCP_CATALOG_ENDPOINT'
          value: catalogEndpoint
        }
        {
          name: 'MCP_TELEMETRY_ENABLED'
          value: '${enableMonitoring}'
        }
        {
          name: 'MCP_AUDIT_ENABLED'
          value: 'true'
        }
        {
          name: 'MCP_DEBUG'
          value: '${environment == \'dev\' ? \'true\' : \'false\'}'
        }
        
        // Fabric integration
        {
          name: 'FABRIC_ENDPOINT'
          value: 'https://api.fabric.microsoft.com'
        }
        {
          name: 'FABRIC_WORKSPACE'
          value: fabricWorkspace
        }
        {
          name: 'FABRIC_TENANT_ID'
          value: fabricTenantId
        }
        
        // Security settings
        {
          name: 'WEBSITE_ENABLE_APP_SERVICE_DIAGNOSTIC'
          value: 'true'
        }
        {
          name: 'WEBSITE_HEALTH_CHECK_EVOLVED'
          value: '1'
        }
        {
          name: 'HEALTH_CHECK_PATH'
          value: '/api/health'
        }
      ]
      
      connectionStrings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${resourceGroup().listKeys('Microsoft.Storage/storageAccounts', storageAccountName).keys[0].value};EndpointSuffix=core.windows.net'
          type: 'Custom'
        }
      ]
      
      http20Enabled: true
      minTlsVersion: '1.2'
      ftpsState: 'FtpsOnly'
      
      cors: {
        allowedOrigins: [
          'https://unhcr.org'
          'https://portal.unhcr.org'
          'https://localhost:3000'
          'https://localhost:8080'
        ]
        allowedMethods: [
          'GET'
          'POST'
          'OPTIONS'
          'HEAD'
        ]
        allowedHeaders: [
          'Content-Type'
          'Authorization'
          'X-Request-ID'
          'X-MCP-Version'
        ]
        exposedHeaders: [
          'X-Request-ID'
          'X-MCP-Version'
        ]
        maxAgeInSeconds: 86400
      }
    }
    
    httpsOnly: true
    clientAffinityEnabled: false
    
    identity: {
      type: 'SystemAssigned'
    }
  }
  tags: tags
}

// Outputs
output functionAppId string = functionApp.id
output functionAppEndpoint string = 'https://${functionAppName}.azurewebsites.net'
output functionAppHostNames array = functionApp.properties.hostNames
output functionAppIdentityPrincipalId string = functionApp.identity.principalId
output functionAppIdentityTenantId string = functionApp.identity.tenantId
```

### Key Vault Module (`modules/key-vault.bicep`)

```bicep
@description('MCP Key Vault Module - Deploys Key Vault with MCP-specific configuration')

param keyVaultName string
param location string
param environment string
param domain string
param owner string
param enableRbacAuthorization bool = true
param enableSoftDelete bool = true
param softDeleteRetentionInDays int = 90
param enablePurgeProtection bool = true
param sku string = 'standard'
@allowed([
  'standard'
  'premium'
])
param tags object = {}

// Deploy Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    enabledForDeployment: true
    enabledForDiskEncryption: true
    enabledForTemplateDeployment: true
    enableSoftDelete: enableSoftDelete
    softDeleteRetentionInDays: softDeleteRetentionInDays
    enablePurgeProtection: enablePurgeProtection
    enableRbacAuthorization: enableRbacAuthorization
    
    sku: {
      name: sku
      family: 'A'
    }
    
    tenantId: subscription().tenantId
    
    // Initial access policy for deployment
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
            'backup'
            'restore'
          ]
          secrets: [
            'get'
            'list'
            'set'
            'delete'
            'recover'
            'backup'
            'restore'
          ]
          certificates: [
            'get'
            'list'
            'create'
            'import'
            'delete'
            'recover'
            'backup'
            'restore'
          ]
        }
      }
    ]
    
    // Network ACLs for private endpoint scenarios
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
      ipRules: []
      virtualNetworkRules: []
    }
  }
  tags: tags
}

// Outputs
output keyVaultId string = keyVault.id
output keyVaultUri string = keyVault.properties.vaultUri
output keyVaultResourceId string = keyVault.id
```

### Storage Module (`modules/storage.bicep`)

```bicep
@description('MCP Storage Module - Deploys Storage Account with MCP-specific configuration')

param storageAccountName string
param location string
param environment string
param sku string = 'Standard_LRS'
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_ZRS'
  'Premium_LRS'
])
param enableStaticWebsite bool = true
param enableHttpsTrafficOnly bool = true
param minimumTlsVersion string = 'TLS1_2'
param tags object = {}

// Deploy Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: sku
    tier: 'Standard'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: enableHttpsTrafficOnly
    allowBlobPublicAccess: false
    minimumTlsVersion: minimumTlsVersion
    allowSharedKeyAccess: true
    
    // Enable static website for documentation hosting
    staticWebsite: if (enableStaticWebsite) {
      enabled: true
      indexDocument: 'index.html'
      error404Document: '404.html'
    }
    
    // Enable blob versioning
    blobProperties: {
      versioningEnabled: true
      containerDeleteRetentionPolicy: {
        enabled: true
        days: 7
      }
      deleteRetentionPolicy: {
        enabled: true
        days: 7
      }
      isVersioningEnabled: true
    }
    
    // Enable file share
    fileProperties: {
      shareDeleteRetentionPolicy: {
        enabled: true
        days: 7
      }
    }
    
    // Enable queue
    queueProperties: {
      logging: {
        delete: true
        read: true
        write: true
        retention: {
          days: 7
        }
      }
      hourMetrics: {
        enabled: true
        retention: {
          days: 7
        }
      }
      minuteMetrics: {
        enabled: true
        retention: {
          days: 7
        }
      }
    }
    
    // Enable table
    tableProperties: {
      logging: {
        delete: true
        read: true
        write: true
        retention: {
          days: 7
        }
      }
      hourMetrics: {
        enabled: true
        retention: {
          days: 7
        }
      }
      minuteMetrics: {
        enabled: true
        retention: {
          days: 7
        }
      }
    }
  }
  tags: tags
}

// Outputs
output storageAccountId string = storageAccount.id
output storageAccountPrimaryKey string = storageAccount.listKeys().keys[0].value
output storageAccountSecondaryKey string = storageAccount.listKeys().keys[1].value
output storageAccountConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
output storageAccountBlobEndpoint string = storageAccount.properties.primaryEndpoints.blob
output storageAccountFileEndpoint string = storageAccount.properties.primaryEndpoints.file
output storageAccountQueueEndpoint string = storageAccount.properties.primaryEndpoints.queue
output storageAccountTableEndpoint string = storageAccount.properties.primaryEndpoints.table
output storageAccountStaticWebsiteEndpoint string = if (enableStaticWebsite) { storageAccount.properties.primaryEndpoints.web } else { '' }
```

---

## 📋 Parameter Files

### Using Bicep Parameter Files

Bicep supports parameter files with the `.bicepparam` extension:

#### Development Parameters (`parameters/dev.bicepparam`)

```bicep
using 'main.bicep'

param environment = 'dev'
param location = 'eastus'
param domain = 'DonorManagement'
param owner = 'DER'
param catalogEndpoint = 'https://catalog-dev.unhcr.org/api/v1'
param fabricWorkspace = 'DEV'
param enablePrivateEndpoints = false
param enableMonitoring = true
param enableBackup = false
param storageAccountSku = 'Standard_LRS'
param keyVaultSku = 'standard'
```

#### Production Parameters (`parameters/prod.bicepparam`)

```bicep
using 'main.bicep'

param environment = 'prod'
param location = 'eastus'
param domain = 'DonorManagement'
param owner = 'DER'
param catalogEndpoint = 'https://catalog.unhcr.org/api/v1'
param fabricWorkspace = 'PROD'
param enablePrivateEndpoints = true
param enableMonitoring = true
param enableBackup = true
param storageAccountSku = 'Standard_GRS'
param keyVaultSku = 'standard'
```

### Deploying with Parameter Files

```bash
# Deploy with parameter file
az deployment group create \
    --name "mcp-deployment" \
    --resource-group $RESOURCE_GROUP \
    --template-file ./templates/main.bicep \
    --parameters @./templates/parameters/prod.bicepparam
```

---

## 🚀 Deployment Scripts

### PowerShell Deployment Script

```powershell
<#
.SYNOPSIS
    Deploys MCP Platform Framework using Bicep templates.
.DESCRIPTION
    This script deploys the MCP Platform Framework infrastructure
    using Bicep templates with support for multiple environments.
.PARAMETER Environment
    The deployment environment (dev, test, stag, prod)
.PARAMETER Domain
    The MCP domain name
.PARAMETER Location
    The Azure region for deployment
.PARAMETER Owner
    The domain owner team
.PARAMETER TemplateFile
    Path to the Bicep template file
.PARAMETER ParametersFile
    Path to the parameter file
.EXAMPLE
    .\deploy.ps1 -Environment prod -Domain DonorManagement
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "test", "stag", "prod")]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [string]$Domain,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [string]$Owner = "DER",
    
    [Parameter(Mandatory=$false)]
    [string]$TemplateFile = ".\templates\main.bicep",
    
    [Parameter(Mandatory=$false)]
    [string]$ParametersFile = ".\templates\parameters\$($Environment).bicepparam"
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

# Validate Bicep template
Write-Host "Validating Bicep template..." -ForegroundColor Cyan
az deployment group validate \
    --resource-group $resourceGroup \
    --template-file $TemplateFile \
    --parameters @$ParametersFile | Out-Null

# Deploy Bicep template
Write-Host "Deploying Bicep template..." -ForegroundColor Cyan
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

# Get function app endpoint
$functionAppName = "mcp-${Environment}-${Domain}-func"
$functionAppEndpoint = "https://${functionAppName}.azurewebsites.net"

Write-Host "`nFunction App Endpoint: $functionAppEndpoint" -ForegroundColor Green
Write-Host "Resource Group: $resourceGroup" -ForegroundColor Green
```

### Bash Deployment Script

```bash
#!/bin/bash

# MCP Platform Framework Bicep Deployment Script
# Usage: ./deploy-bicep.sh -e <environment> -d <domain> [-l <location>] [-o <owner>]

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
TEMPLATE_FILE="./templates/main.bicep"
PARAMETERS_FILE="./templates/parameters/${ENVIRONMENT}.bicepparam"

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

# Validate Bicep template
echo "Validating Bicep template..."
az deployment group validate \
    --resource-group $RESOURCE_GROUP \
    --template-file $TEMPLATE_FILE \
    --parameters @$PARAMETERS_FILE

# Deploy Bicep template
echo "Deploying Bicep template..."
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

## 🎯 Advanced Bicep Features

### Conditional Deployment

```bicep
// Conditional resource deployment
resource monitoringResources 'Microsoft.OperationalInsights/workspaces@2022-10-01' = if (enableMonitoring) {
  name: '${resourcePrefix}-log-analytics'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
  tags: tags
}

// Conditional properties
resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  properties: {
    httpsOnly: enablePrivateEndpoints ? false : true  // Disable HTTPS if using private endpoints
    
    siteConfig: {
      appSettings: [
        {
          name: 'MCP_DEBUG'
          value: environment == 'dev' ? 'true' : 'false'  // Enable debug only in dev
        }
      ]
    }
  }
}
```

### Loops and Iteration

```bicep
// Deploy multiple storage accounts
param storageAccounts array = [
  'mcp-${environment}-${domain}-primary'
  'mcp-${environment}-${domain}-secondary'
]

resource storageAccounts 'Microsoft.Storage/storageAccounts@2023-01-01' = [for saName in storageAccounts: {
  name: saName
  location: location
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
  }
  tags: tags
}]

// Deploy multiple alert rules
param alertConfigurations array = [
  {
    name: 'HighErrorRate'
    metricName: 'Requests'
    condition: 'ResponseCode == 5xx'
    threshold: 5
    severity: 3
  }
  {
    name: 'HighLatency'
    metricName: 'RequestDuration'
    condition: 'Average > 5000'
    threshold: 5000
    severity: 2
  }
]

resource alertRules 'Microsoft.Insights/metricAlerts@2018-03-01' = [for alert in alertConfigurations: {
  name: '${functionAppName}-${alert.name}'
  location: 'global'
  properties: {
    description: 'Alert for ${alert.name}'
    severity: alert.severity
    enabled: true
    scopes: [functionApp.id]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      odata.type: 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: alert.name
          metricName: alert.metricName
          dimensions: []
          operator: 'GreaterThan'
          threshold: alert.threshold
          timeAggregation: 'Total'
        }
      ]
    }
  }
}]
```

### Decorators for Validation

```bicep
// Parameter validation with decorators
@description('Storage account SKU')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_ZRS'
  'Premium_LRS'
])
param storageAccountSku string = 'Standard_LRS'

// Secure parameter (not shown in logs)
@secure()
param adminPassword string

// Parameter with min/max constraints
@minValue(1)
@maxValue(90)
param softDeleteRetentionInDays int = 90

// Parameter with regex pattern
@match('^[a-zA-Z0-9-]{3,24}$')
param storageAccountName string

// Parameter with allowed values
@allowed([
  'dev'
  'test'
  'stag'
  'prod'
])
param environment string = 'dev'
```

### Custom Functions

```bicep
// Custom function to generate resource names
function generateResourceName(prefix: string, suffix: string) => '${prefix}-${suffix}-${uniqueString(resourceGroup().id)}'

// Custom function to generate tags
function generateTags(environment: string, domain: string, owner: string) => {
  Environment: environment
  Domain: domain
  Owner: owner
  Project: 'MCP Platform Framework'
  CostCenter: 'IT'
  ManagedBy: 'Bicep'
}

// Usage
var storageAccountName = generateResourceName('mcp', '${environment}-${domain}-sa')
var tags = generateTags(environment, domain, owner)
```

---

## 🔧 Bicep Tooling

### VS Code Extension

1. Install the **Bicep** extension from the marketplace
2. Features:
   - Syntax highlighting
   - IntelliSense
   - Code navigation
   - Error detection
   - Formatting
   - Snippets

### Azure CLI Commands

```bash
# Install Bicep CLI
az bicep install

# Upgrade Bicep CLI
az bicep upgrade

# Check Bicep version
az bicep version

# Build Bicep file (compile to ARM JSON)
az bicep build --file main.bicep

# Decompile ARM JSON to Bicep
az bicep decompile --file main.json

# Validate Bicep file
az bicep validate --file main.bicep

# Get Bicep help
az bicep --help
```

### Bicep CLI Commands

```bash
# Install Bicep CLI standalone
curl -Lo bicep https://github.com/Azure/bicep/releases/latest/download/bicep-linux-x64
chmod +x bicep
sudo mv bicep /usr/local/bin/bicep

# Build Bicep file
bicep build main.bicep

# Decompile ARM JSON
bicep decompile main.json

# Validate Bicep file
bicep validate main.bicep

# Get version
bicep --version
```

---

## 📊 Best Practices

### Template Organization

1. **Modular Design**: Break templates into reusable modules
2. **Parameter Validation**: Use decorators for parameter validation
3. **Conditional Deployment**: Use `if` statements for optional resources
4. **Naming Conventions**: Use consistent naming patterns
5. **Tagging**: Apply consistent tags to all resources
6. **Documentation**: Add descriptions to parameters and resources
7. **Version Control**: Store templates in source control

### Security Best Practices

1. **Secure Parameters**: Use `@secure()` decorator for sensitive parameters
2. **RBAC**: Use Azure RBAC instead of access policies when possible
3. **Private Endpoints**: Use private endpoints for production deployments
4. **Network Security**: Configure network ACLs and firewalls
5. **Minimum TLS**: Enforce TLS 1.2 or higher
6. **HTTPS Only**: Enable HTTPS-only for all web resources

### Performance Best Practices

1. **Parallel Deployment**: Bicep deploys resources in parallel by default
2. **Dependencies**: Only specify `dependsOn` when absolutely necessary
3. **Modular Deployment**: Deploy independent modules in separate deployments
4. **Parameter Files**: Use parameter files for environment-specific values

---

## 🔍 Troubleshooting

### Common Bicep Errors

#### Syntax Errors

**Symptom:** `Bicep syntax error: Expected identifier or keyword`

**Solution:**
```bash
# Validate Bicep syntax
az bicep validate --file main.bicep

# Use VS Code with Bicep extension for real-time validation
```

#### Type Mismatch

**Symptom:** `The value "true" is not valid for parameter "storageAccountSku" which expects a value of type "string"`

**Solution:**
```bicep
// Ensure correct types
param storageAccountSku string = 'Standard_LRS'  // String, not boolean
param enableMonitoring bool = true  // Boolean, not string
```

#### Missing Required Parameter

**Symptom:** `The required parameter "domain" is missing`

**Solution:**
```bash
# Provide all required parameters
az deployment group create \
    --name "mcp-deployment" \
    --resource-group $RESOURCE_GROUP \
    --template-file main.bicep \
    --parameters domain=DonorManagement
```

#### Resource Name Conflicts

**Symptom:** `Resource name "mcp-prod-donor-sa" is already in use`

**Solution:**
```bicep
// Use unique naming
var storageAccountName = 'mcp-${environment}-${domain}-${uniqueString(resourceGroup().id)}'
```

#### Permission Issues

**Symptom:** `The client does not have permission to perform this action`

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

#### Template Validation Errors

**Symptom:** `Template validation failed: Invalid template`

**Solution:**
```bash
# Validate template before deployment
az deployment group validate \
    --resource-group $RESOURCE_GROUP \
    --template-file main.bicep \
    --parameters @parameters/prod.bicepparam

# Check for specific errors
az bicep validate --file main.bicep
```

---

## 📚 Additional Resources

- [Bicep Documentation](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Bicep GitHub Repository](https://github.com/Azure/bicep)
- [Bicep vs ARM Templates](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/bicep-vs-json)
- [Bicep Best Practices](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/best-practices)
- [Bicep Reference](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Bicep Samples](https://github.com/Azure/bicep/tree/main/docs/examples)

---

## 🔄 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-05-01 | Initial Bicep template documentation |
| 1.1.0 | 2026-05-15 | Added modular templates and parameter files |
| 1.2.0 | 2026-06-01 | Added deployment scripts and advanced features |
| 1.3.0 | 2026-06-15 | Added troubleshooting guide and best practices |
