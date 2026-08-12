"""Bicep Template Generator for MCP Framework"""
from typing import Optional, List, Dict, Any
from .parameters import DeploymentParameters, EnvironmentType


def get_bicep_template(params: Optional[DeploymentParameters] = None) -> str:
    """
    Generate a Bicep template for deploying the MCP Framework.
    
    Args:
        params: Deployment parameters (defaults to test parameters)
    
    Returns:
        Bicep template as string
    """
    if params is None:
        params = DeploymentParameters(
            project_name="mcp-test",
            environment=EnvironmentType.DEVELOPMENT,
            location="eastus",
            mcp_domain="TestDomain"
        )
    
    template_lines = []
    
    # Add parameters
    template_lines.extend(get_bicep_parameters(params))
    template_lines.append("")
    
    # Add variables
    template_lines.extend(get_bicep_variables(params))
    template_lines.append("")
    
    # Add resources
    template_lines.extend(get_bicep_resources(params))
    template_lines.append("")
    
    # Add outputs
    template_lines.extend(get_bicep_outputs(params))
    
    return "\n".join(template_lines)


def get_bicep_parameters(params: DeploymentParameters) -> List[str]:
    """Generate Bicep template parameters"""
    lines = [
        "// MCP Platform Framework - Bicep Deployment Template",
        "// Generated for " + params.project_name,
        "",
        "param projectName string = '" + params.project_name + "'",
        "param environment string = '" + params.environment.value + "'",
        "param location string = '" + params.location + "'",
        "param mcpDomain string = '" + params.mcp_domain + "'",
        "param mcpVersion string = '" + params.mcp_version + "'",
        "",
        "param enableTelemetry bool = " + str(params.enable_telemetry).lower(),
        "param enableAudit bool = " + str(params.enable_audit).lower(),
        "param enableAuthentication bool = " + str(params.enable_authentication).lower(),
        "param enableAuthorization bool = " + str(params.enable_authorization).lower(),
        "param enableClassification bool = " + str(params.enable_classification).lower(),
        "",
        "// Storage Account parameters",
        "param storageAccountName string = '" + params.get_storage_account_name() + "'",
        "param storageAccountKind string = '" + params.storage_account.kind.value + "'",
        "param storageAccountPerformance string = '" + params.storage_account.performance.value + "'",
        "param storageAccountReplication string = '" + params.storage_account.replication.value + "'",
        "param storageAccountAccessTier string = '" + params.storage_account.access_tier + "'",
        "",
        "// Application Insights parameters",
        "param appInsightsName string = '" + params.get_application_insights_name() + "'",
        "param appInsightsRetentionDays int = " + str(params.application_insights.retention_days),
        "param appInsightsSamplingPercentage float = " + str(params.application_insights.sampling_percentage),
        "",
        "// Key Vault parameters",
        "param keyVaultName string = '" + params.get_key_vault_name() + "'",
        "param keyVaultSku string = '" + params.key_vault.sku_name + "'",
        "param enableKeyVaultPurgeProtection bool = " + str(params.key_vault.enable_purge_protection).lower(),
        "param enableKeyVaultSoftDelete bool = " + str(params.key_vault.enable_soft_delete).lower(),
        "param keyVaultSoftDeleteRetentionDays int = " + str(params.key_vault.soft_delete_retention_days),
        "",
        "// Function App parameters",
        "param functionAppName string = '" + params.get_function_app_name() + "'",
        "param functionAppRuntime string = '" + params.function_app.runtime + "'",
        "param functionAppRuntimeVersion string = '" + params.function_app.runtime_version + "'",
        "param functionAppSkuTier string = '" + params.function_app.sku_tier.value + "'",
        "param functionAppAlwaysOn bool = " + str(params.function_app.always_on).lower(),
        "param functionAppTimeoutMinutes int = " + str(params.function_app.timeout_minutes),
        "",
        "// Managed Identity parameters",
        "param managedIdentityName string = '" + params.managed_identity.name + "'",
        "",
        "// Fabric parameters",
        "param fabricWorkspaceName string = '" + params.fabric.workspace_name + "'"
    ]
    
    return lines


def get_bicep_variables(params: DeploymentParameters) -> List[str]:
    """Generate Bicep template variables"""
    lines = [
        "// Variables",
        "var resourceGroupName = resourceGroup().name",
        "var tags = {",
        "  Project: projectName",
        "  Environment: environment",
        "  MCP-Domain: mcpDomain",
        "  MCP-Version: mcpVersion",
        "}",
        "",
        "// Storage connection string",
        "var storageConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=' + listKeys(resourceId('Microsoft.Storage/storageAccounts', storageAccountName), '2023-01-01').keys[0].value + ';EndpointSuffix=core.windows.net'",
        "",
        "// Application Insights instrumentation key",
        "var appInsightsInstrumentationKey = reference(resourceId('Microsoft.Insights/components', appInsightsName), '2020-02-02').InstrumentationKey",
        "",
        "// Managed Identity client ID",
        "var managedIdentityClientId = reference(resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', managedIdentityName), '2023-01-01').clientId"
    ]
    
    return lines


def get_bicep_resources(params: DeploymentParameters) -> List[str]:
    """Generate Bicep template resources"""
    lines = []
    
    # 1. Storage Account
    lines.extend([
        "// Storage Account",
        "resource storageAccount 'Microsoft.Storage/storageAccounts@${storageAccountName}' = {",
        "  name: storageAccountName",
        "  location: location",
        "  sku: {",
        "    name: storageAccountReplication",
        "    tier: storageAccountPerformance",
        "  }",
        "  kind: storageAccountKind",
        "  properties: {",
        "    accessTier: storageAccountAccessTier",
        "    supportsHttpsTrafficOnly: true",
        "    allowBlobPublicAccess: false",
        "  }",
        "  tags: tags",
        "}",
        ""
    ])
    
    # 2. Application Insights
    lines.extend([
        "// Application Insights",
        "resource appInsights 'Microsoft.Insights/components@${appInsightsName}' = {",
        "  name: appInsightsName",
        "  location: location",
        "  kind: 'web'",
        "  properties: {",
        "    Application_Type: 'web'",
        "    RetentionInDays: appInsightsRetentionDays",
        "    SamplingPercentage: appInsightsSamplingPercentage",
        "    DisableIpMasking: false",
        "    Flow_Type: 'Bluefield'",
        "    Request_Source: 'rest'",
        "  }",
        "  tags: tags",
        "}",
        ""
    ])
    
    # 3. Key Vault
    lines.extend([
        "// Key Vault",
        "resource keyVault 'Microsoft.KeyVault/vaults@${keyVaultName}' = {",
        "  name: keyVaultName",
        "  location: location",
        "  properties: {",
        "    sku: {",
        "      family: 'A'",
        "      name: keyVaultSku",
        "    }",
        "    tenantId: subscription().tenantId",
        "    accessPolicies: []",
        "    enabledForDeployment: true",
        "    enabledForDiskEncryption: true",
        "    enabledForTemplateDeployment: true",
        "    enablePurgeProtection: enableKeyVaultPurgeProtection",
        "    enableSoftDelete: enableKeyVaultSoftDelete",
        "    softDeleteRetentionInDays: keyVaultSoftDeleteRetentionDays",
        "  }",
        "  tags: tags",
        "}",
        ""
    ])
    
    # 4. Managed Identity
    lines.extend([
        "// Managed Identity",
        "resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@${managedIdentityName}' = {",
        "  name: managedIdentityName",
        "  location: location",
        "  properties: {}",
        "  tags: tags",
        "}",
        ""
    ])
    
    # 5. Server Farm (Consumption Plan)
    lines.extend([
        "// Server Farm (Consumption Plan)",
        "resource serverFarm 'Microsoft.Web/serverfarms@${functionAppName}-plan' = {",
        "  name: '${functionAppName}-plan'",
        "  location: location",
        "  kind: 'functionapp,linux'",
        "  sku: {",
        "    name: functionAppSkuTier",
        "    tier: 'Dynamic'",
        "  }",
        "  properties: {",
        "    reserved: false",
        "  }",
        "  tags: tags",
        "}",
        ""
    ])
    
    # 6. Function App
    function_app_depends_on = [
        "storageAccount",
        "appInsights"
    ]
    
    if params.enable_authentication:
        function_app_depends_on.append("managedIdentity")
    
    lines.extend([
        "// Function App",
        "resource functionApp 'Microsoft.Web/sites@${functionAppName}' = {",
        "  name: functionAppName",
        "  location: location",
        "  kind: 'functionapp,linux'",
        "  dependsOn: [" + ", ".join(function_app_depends_on) + "]",
        "  properties: {",
        "    serverFarmId: serverFarm.id",
        "    siteConfig: {",
        "      appSettings: [" + get_bicep_app_settings(params) + "]",
        "      linuxFxVersion: 'python|${functionAppRuntimeVersion}'",
        "    }",
        "    httpsOnly: true" + (",\n    alwaysOn: true" if params.function_app.always_on else ""),
        "  }",
        "  tags: tags",
        "}",
        ""
    ])
    
    # 7. Assign Managed Identity to Function App (if authentication enabled)
    if params.enable_authentication:
        lines.extend([
            "// Assign Managed Identity to Function App",
            "resource functionAppIdentity 'Microsoft.Web/sites/config@${functionAppName}/identity' = {",
            "  name: '${functionAppName}/identity'",
            "  dependsOn: [",
            "    functionApp",
            "    managedIdentity",
            "  ]",
            "  properties: {",
            "    type: 'UserAssigned'",
            "    userAssignedIdentities: {",
            "      '${managedIdentity.id}': {}",
            "    }",
            "  }",
            "}",
            ""
        ])
    
    return lines


def get_bicep_app_settings(params: DeploymentParameters) -> str:
    """Generate Bicep Function App application settings"""
    settings = [
        "{ name: 'AzureWebJobsStorage'; value: storageConnectionString }",
        "{ name: 'FUNCTIONS_WORKER_RUNTIME'; value: functionAppRuntime }",
        "{ name: 'FUNCTIONS_EXTENSION_VERSION'; value: '~4' }",
        "{ name: 'APPINSIGHTS_INSTRUMENTATIONKEY'; value: appInsightsInstrumentationKey }",
        f"{{ name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'; value: 'InstrumentationKey=' + appInsightsInstrumentationKey + ';IngestionEndpoint=https://{params.location}.in.applicationinsights.azure.com/' }}",
        "",
        "// MCP Framework settings",
        "{ name: 'MCP_DOMAIN'; value: mcpDomain }",
        "{ name: 'MCP_ENVIRONMENT'; value: environment }",
        "{ name: 'MCP_VERSION'; value: mcpVersion }",
        f"{{ name: 'MCP_ENABLE_TELEMETRY'; value: '{str(params.enable_telemetry).lower()}' }}",
        f"{{ name: 'MCP_ENABLE_AUDIT'; value: '{str(params.enable_audit).lower()}' }}",
        f"{{ name: 'MCP_ENABLE_AUTH'; value: '{str(params.enable_authentication).lower()}' }}",
        f"{{ name: 'MCP_ENABLE_AUTHORIZATION'; value: '{str(params.enable_authorization).lower()}' }}",
        f"{{ name: 'MCP_ENABLE_CLASSIFICATION'; value: '{str(params.enable_classification).lower()}' }}",
        "",
        "// Azure settings",
        "{ name: 'AZURE_SUBSCRIPTION_ID'; value: subscription().subscriptionId }",
        "{ name: 'AZURE_RESOURCE_GROUP'; value: resourceGroup().name }",
        "{ name: 'AZURE_LOCATION'; value: location }",
        "",
        "// Storage settings",
        "{ name: 'STORAGE_ACCOUNT_NAME'; value: storageAccountName }",
        "{ name: 'STORAGE_CONNECTION_STRING'; value: storageConnectionString }",
        "",
        "// Key Vault settings",
        "{ name: 'KEY_VAULT_NAME'; value: keyVaultName }",
        "{ name: 'KEY_VAULT_URI'; value: 'https://' + keyVaultName + '.vault.azure.net/' }",
        "",
        "// Fabric settings",
        "{ name: 'FABRIC_WORKSPACE_NAME'; value: fabricWorkspaceName }",
        "{ name: 'FABRIC_RESOURCE_GROUP'; value: resourceGroup().name }"
    ]
    
    # Add authentication settings if enabled
    if params.enable_authentication:
        settings.extend([
            "",
            "// Authentication settings",
            "{ name: 'AZURE_TENANT_ID'; value: subscription().tenantId }",
            "{ name: 'AZURE_CLIENT_ID'; value: managedIdentityClientId }",
            "{ name: 'AZURE_CLIENT_SECRET'; value: '' }",  # Not used with Managed Identity
            "{ name: 'AZURE_IDENTITY_TYPE'; value: 'UserAssigned' }"
        ])
    
    return "\n        ".join(settings)


def get_bicep_outputs(params: DeploymentParameters) -> List[str]:
    """Generate Bicep template outputs"""
    lines = [
        "// Outputs",
        "output functionAppEndpoint string = 'https://${functionAppName}.azurewebsites.net'",
        "output functionAppName string = functionAppName",
        "output storageAccountName string = storageAccountName",
        "output storageConnectionString string = storageConnectionString",
        "output appInsightsName string = appInsightsName",
        "output appInsightsInstrumentationKey string = appInsightsInstrumentationKey",
        "output keyVaultName string = keyVaultName",
        "output keyVaultUri string = 'https://${keyVaultName}.vault.azure.net/'",
        "output managedIdentityName string = managedIdentityName",
        "output managedIdentityClientId string = managedIdentityClientId"
    ]
    
    return lines


def save_bicep_template(file_path: str, params: Optional[DeploymentParameters] = None):
    """
    Save Bicep template to a file.
    
    Args:
        file_path: Path to save the template
        params: Deployment parameters
    """
    template = get_bicep_template(params)
    with open(file_path, 'w') as f:
        f.write(template)
    print(f"Bicep template saved to {file_path}")


if __name__ == "__main__":
    # Example usage
    params = DeploymentParameters(
        project_name="mcp-donor-management",
        environment=EnvironmentType.DEVELOPMENT,
        location="eastus",
        mcp_domain="DonorManagement"
    )
    
    template = get_bicep_template(params)
    print("Generated Bicep Template:")
    print(template[:1000] + "..." if len(template) > 1000 else template)
    
    # Save to file
    save_bicep_template("mcp-deployment.bicep", params)