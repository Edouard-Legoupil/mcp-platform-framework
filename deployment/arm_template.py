"""ARM Template Generator for MCP Framework"""
import json
from typing import Dict, Any, List, Optional
from .parameters import DeploymentParameters, EnvironmentType


def get_arm_template(params: Optional[DeploymentParameters] = None) -> str:
    """
    Generate an ARM template for deploying the MCP Framework.
    
    Args:
        params: Deployment parameters (defaults to test parameters)
    
    Returns:
        ARM template as JSON string
    """
    if params is None:
        params = DeploymentParameters(
            project_name="mcp-test",
            environment=EnvironmentType.DEVELOPMENT,
            location="eastus",
            mcp_domain="TestDomain"
        )
    
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "apiProfile": "",
        "parameters": get_arm_parameters(params),
        "variables": get_arm_variables(params),
        "resources": get_arm_resources(params),
        "outputs": get_arm_outputs(params)
    }
    
    return json.dumps(template, indent=2)


def get_arm_parameters(params: DeploymentParameters) -> List[Dict[str, Any]]:
    """Generate ARM template parameters"""
    return [
        {
            "name": "projectName",
            "type": "string",
            "defaultValue": params.project_name,
            "metadata": {
                "description": "Name of the MCP project"
            }
        },
        {
            "name": "environment",
            "type": "string",
            "defaultValue": params.environment.value,
            "metadata": {
                "description": "Deployment environment (dev, test, prod)"
            }
        },
        {
            "name": "location",
            "type": "string",
            "defaultValue": params.location,
            "metadata": {
                "description": "Azure region for deployment"
            }
        },
        {
            "name": "mcpDomain",
            "type": "string",
            "defaultValue": params.mcp_domain,
            "metadata": {
                "description": "MCP domain name"
            }
        },
        {
            "name": "mcpVersion",
            "type": "string",
            "defaultValue": params.mcp_version,
            "metadata": {
                "description": "MCP framework version"
            }
        },
        {
            "name": "enableTelemetry",
            "type": "bool",
            "defaultValue": params.enable_telemetry,
            "metadata": {
                "description": "Enable telemetry collection"
            }
        },
        {
            "name": "enableAudit",
            "type": "bool",
            "defaultValue": params.enable_audit,
            "metadata": {
                "description": "Enable audit logging"
            }
        },
        {
            "name": "enableAuthentication",
            "type": "bool",
            "defaultValue": params.enable_authentication,
            "metadata": {
                "description": "Enable authentication"
            }
        },
        {
            "name": "enableAuthorization",
            "type": "bool",
            "defaultValue": params.enable_authorization,
            "metadata": {
                "description": "Enable authorization"
            }
        },
        {
            "name": "enableClassification",
            "type": "bool",
            "defaultValue": params.enable_classification,
            "metadata": {
                "description": "Enable data classification"
            }
        }
    ]


def get_arm_variables(params: DeploymentParameters) -> Dict[str, Any]:
    """Generate ARM template variables"""
    return {
        "resourceGroupName": f"[{params.get_resource_group_name()}]",
        "functionAppName": f"[{params.get_function_app_name()}]",
        "storageAccountName": f"[{params.get_storage_account_name()}]",
        "keyVaultName": f"[{params.get_key_vault_name()}]",
        "appInsightsName": f"[{params.get_application_insights_name()}]",
        "managedIdentityName": f"[{params.managed_identity.name}]",
        "fabricWorkspaceName": f"[{params.fabric.workspace_name}]",
        
        "storageAccountApiVersion": "2023-01-01",
        "functionAppApiVersion": "2023-01-01",
        "appInsightsApiVersion": "2020-02-02",
        "keyVaultApiVersion": "2023-01-01",
        "managedIdentityApiVersion": "2023-01-01",
        
        "tags": params.tags,
        
        # Connection strings and keys
        "storageConnectionString": f"[concat('DefaultEndpointsProtocol=https;AccountName=', variables('storageAccountName'), ';AccountKey=', listKeys(resourceId('Microsoft.Storage/storageAccounts', variables('storageAccountName')), variables('storageAccountApiVersion')).keys[0].value, ';EndpointSuffix=core.windows.net')]",
        "appInsightsInstrumentationKey": f"[reference(resourceId('Microsoft.Insights/components', variables('appInsightsName')), variables('appInsightsApiVersion')).InstrumentationKey]"
    }


def get_arm_resources(params: DeploymentParameters) -> List[Dict[str, Any]]:
    """Generate ARM template resources"""
    resources = []
    
    # 1. Storage Account
    resources.append({
        "type": "Microsoft.Storage/storageAccounts",
        "apiVersion": "[variables('storageAccountApiVersion')]",
        "name": f"[{params.get_storage_account_name()}]",
        "location": f"[{params.location}]",
        "sku": {
            "name": params.storage_account.replication.value,
            "tier": params.storage_account.performance.value
        },
        "kind": params.storage_account.kind.value,
        "properties": {
            "accessTier": params.storage_account.access_tier,
            "supportsHttpsTrafficOnly": params.storage_account.enable_https_traffic_only,
            "allowBlobPublicAccess": params.storage_account.allow_blob_public_access
        },
        "tags": "[variables('tags')]"
    })
    
    # 2. Application Insights
    resources.append({
        "type": "Microsoft.Insights/components",
        "apiVersion": "[variables('appInsightsApiVersion')]",
        "name": f"[{params.get_application_insights_name()}]",
        "location": f"[{params.location}]",
        "kind": "web",
        "properties": {
            "Application_Type": "web",
            "RetentionInDays": params.application_insights.retention_days,
            "SamplingPercentage": params.application_insights.sampling_percentage,
            "DisableIpMasking": params.application_insights.disable_ip_masking,
            "Flow_Type": "Bluefield",
            "Request_Source": "rest"
        },
        "tags": "[variables('tags')]"
    })
    
    # 3. Key Vault
    resources.append({
        "type": "Microsoft.KeyVault/vaults",
        "apiVersion": "[variables('keyVaultApiVersion')]",
        "name": f"[{params.get_key_vault_name()}]",
        "location": f"[{params.location}]",
        "properties": {
            "sku": {
                "family": "A",
                "name": params.key_vault.sku_name
            },
            "tenantId": "[subscription().tenantId]",
            "accessPolicies": [],
            "enabledForDeployment": params.key_vault.enabled_for_deployment,
            "enabledForDiskEncryption": params.key_vault.enabled_for_disk_encryption,
            "enabledForTemplateDeployment": params.key_vault.enabled_for_template_deployment,
            "enablePurgeProtection": params.key_vault.enable_purge_protection,
            "enableSoftDelete": params.key_vault.enable_soft_delete,
            "softDeleteRetentionInDays": params.key_vault.soft_delete_retention_days
        },
        "tags": "[variables('tags')]"
    })
    
    # 4. Managed Identity
    resources.append({
        "type": "Microsoft.ManagedIdentity/userAssignedIdentities",
        "apiVersion": "[variables('managedIdentityApiVersion')]",
        "name": f"[{params.managed_identity.name}]",
        "location": f"[{params.location}]",
        "properties": {},
        "tags": "[variables('tags')]"
    })
    
    # 5. Function App
    function_app_depends_on = [
        f"[resourceId('Microsoft.Storage/storageAccounts', variables('storageAccountName'))]",
        f"[resourceId('Microsoft.Insights/components', variables('appInsightsName'))]"
    ]
    
    if params.enable_authentication:
        function_app_depends_on.append(f"[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', variables('managedIdentityName'))]")
    
    function_app_properties = {
        "serverFarmId": f"/subscriptions/[subscription().subscriptionId]/resourceGroups/[variables('resourceGroupName')]/providers/Microsoft.Web/serverfarms/[variables('functionAppName')]-plan",
        "siteConfig": {
            "appSettings": get_function_app_settings(params),
            "linuxFxVersion": f"python|{params.function_app.runtime_version}"
        },
        "httpsOnly": True
    }
    
    if params.function_app.always_on:
        function_app_properties["siteConfig"]["alwaysOn"] = True
    
    resources.append({
        "type": "Microsoft.Web/sites",
        "apiVersion": "[variables('functionAppApiVersion')]",
        "name": f"[{params.get_function_app_name()}]",
        "location": f"[{params.location}]",
        "kind": "functionapp,linux",
        "dependsOn": function_app_depends_on,
        "properties": function_app_properties,
        "tags": "[variables('tags')]"
    })
    
    # 6. Server Farm (Consumption Plan)
    resources.append({
        "type": "Microsoft.Web/serverfarms",
        "apiVersion": "[variables('functionAppApiVersion')]",
        "name": f"[concat(variables('functionAppName'), '-plan')]",
        "location": f"[{params.location}]",
        "kind": "functionapp,linux",
        "sku": {
            "name": params.function_app.sku_tier.value,
            "tier": "Dynamic"
        },
        "properties": {
            "reserved": False
        },
        "tags": "[variables('tags')]"
    })
    
    # 7. Assign Managed Identity to Function App (if authentication enabled)
    if params.enable_authentication:
        resources.append({
            "type": "Microsoft.Web/sites/config",
            "apiVersion": "[variables('functionAppApiVersion')]",
            "name": f"[concat(variables('functionAppName'), '/identity')]",
            "dependsOn": [
                f"[resourceId('Microsoft.Web/sites', variables('functionAppName'))]",
                f"[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', variables('managedIdentityName'))]"
            ],
            "properties": {
                "type": "UserAssigned",
                "userAssignedIdentities": {
                    f"[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', variables('managedIdentityName'))]": {}
                }
            }
        })
    
    return resources


def get_function_app_settings(params: DeploymentParameters) -> List[Dict[str, Any]]:
    """Generate Function App application settings"""
    settings = [
        {"name": "AzureWebJobsStorage", "value": "[variables('storageConnectionString')]"},
        {"name": "FUNCTIONS_WORKER_RUNTIME", "value": params.function_app.runtime},
        {"name": "FUNCTIONS_EXTENSION_VERSION", "value": "~4"},
        {"name": "APPINSIGHTS_INSTRUMENTATIONKEY", "value": "[variables('appInsightsInstrumentationKey')]"},
        {"name": "APPLICATIONINSIGHTS_CONNECTION_STRING", "value": f"InstrumentationKey=[variables('appInsightsInstrumentationKey')];IngestionEndpoint=https://{params.location}.in.applicationinsights.azure.com/"},
        
        # MCP Framework settings
        {"name": "MCP_DOMAIN", "value": f"[{params.mcp_domain}]"},
        {"name": "MCP_ENVIRONMENT", "value": f"[{params.environment.value}]"},
        {"name": "MCP_VERSION", "value": f"[{params.mcp_version}]"},
        {"name": "MCP_ENABLE_TELEMETRY", "value": str(params.enable_telemetry).lower()},
        {"name": "MCP_ENABLE_AUDIT", "value": str(params.enable_audit).lower()},
        {"name": "MCP_ENABLE_AUTH", "value": str(params.enable_authentication).lower()},
        {"name": "MCP_ENABLE_AUTHORIZATION", "value": str(params.enable_authorization).lower()},
        {"name": "MCP_ENABLE_CLASSIFICATION", "value": str(params.enable_classification).lower()},
        
        # Azure settings
        {"name": "AZURE_SUBSCRIPTION_ID", "value": "[subscription().subscriptionId]"},
        {"name": "AZURE_RESOURCE_GROUP", "value": f"[{params.get_resource_group_name()}]"},
        {"name": "AZURE_LOCATION", "value": f"[{params.location}]"},
        
        # Storage settings
        {"name": "STORAGE_ACCOUNT_NAME", "value": f"[{params.get_storage_account_name()}]"},
        {"name": "STORAGE_CONNECTION_STRING", "value": "[variables('storageConnectionString')]"},
        
        # Key Vault settings
        {"name": "KEY_VAULT_NAME", "value": f"[{params.get_key_vault_name()}]"},
        {"name": "KEY_VAULT_URI", "value": f"https://[{params.get_key_vault_name()}].vault.azure.net/"},
        
        # Fabric settings
        {"name": "FABRIC_WORKSPACE_NAME", "value": f"[{params.fabric.workspace_name}]"},
        {"name": "FABRIC_RESOURCE_GROUP", "value": f"[{params.get_resource_group_name()}]"}
    ]
    
    # Add authentication settings if enabled
    if params.enable_authentication:
        settings.extend([
            {"name": "AZURE_TENANT_ID", "value": "[subscription().tenantId]"},
            {"name": "AZURE_CLIENT_ID", "value": "[reference(resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', variables('managedIdentityName')), variables('managedIdentityApiVersion')).clientId]"},
            {"name": "AZURE_CLIENT_SECRET", "value": ""},  # Not used with Managed Identity
            {"name": "AZURE_IDENTITY_TYPE", "value": "UserAssigned"}
        ])
    
    return settings


def get_arm_outputs(params: DeploymentParameters) -> Dict[str, Any]:
    """Generate ARM template outputs"""
    return {
        "functionAppEndpoint": {
            "type": "string",
            "value": f"[concat('https://', variables('functionAppName'), '.azurewebsites.net')]"
        },
        "functionAppName": {
            "type": "string",
            "value": f"[variables('functionAppName')]"
        },
        "storageAccountName": {
            "type": "string",
            "value": f"[variables('storageAccountName')]"
        },
        "storageConnectionString": {
            "type": "string",
            "value": "[variables('storageConnectionString')]"
        },
        "appInsightsName": {
            "type": "string",
            "value": f"[variables('appInsightsName')]"
        },
        "appInsightsInstrumentationKey": {
            "type": "string",
            "value": "[variables('appInsightsInstrumentationKey')]"
        },
        "keyVaultName": {
            "type": "string",
            "value": f"[variables('keyVaultName')]"
        },
        "keyVaultUri": {
            "type": "string",
            "value": f"[concat('https://', variables('keyVaultName'), '.vault.azure.net/')]"
        },
        "managedIdentityName": {
            "type": "string",
            "value": f"[variables('managedIdentityName')]"
        },
        "managedIdentityClientId": {
            "type": "string",
            "value": f"[reference(resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', variables('managedIdentityName')), variables('managedIdentityApiVersion')).clientId]"
        }
    }


def save_arm_template(file_path: str, params: Optional[DeploymentParameters] = None):
    """
    Save ARM template to a file.
    
    Args:
        file_path: Path to save the template
        params: Deployment parameters
    """
    template = get_arm_template(params)
    with open(file_path, 'w') as f:
        f.write(template)
    print(f"ARM template saved to {file_path}")


if __name__ == "__main__":
    # Example usage
    params = DeploymentParameters(
        project_name="mcp-donor-management",
        environment=EnvironmentType.DEVELOPMENT,
        location="eastus",
        mcp_domain="DonorManagement"
    )
    
    template = get_arm_template(params)
    print("Generated ARM Template:")
    print(template[:1000] + "..." if len(template) > 1000 else template)
    
    # Save to file
    save_arm_template("mcp-deployment.json", params)