"""Deployment Parameters for MCP Framework"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class EnvironmentType(str, Enum):
    """Environment types for deployment"""
    DEVELOPMENT = "dev"
    TEST = "test"
    PRODUCTION = "prod"


class SkuTier(str, Enum):
    """SKU tiers for Azure resources"""
    FREE = "Free"
    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"
    CONSUMPTION = "Y1"  # Consumption plan


class StorageAccountKind(str, Enum):
    """Storage account kinds"""
    STORAGE_V2 = "StorageV2"
    BLOB_STORAGE = "BlobStorage"
    FILE_STORAGE = "FileStorage"


class StorageAccountPerformance(str, Enum):
    """Storage account performance tiers"""
    STANDARD = "Standard"
    PREMIUM = "Premium"


class StorageAccountReplication(str, Enum):
    """Storage account replication types"""
    LRS = "LRS"
    GRS = "GRS"
    RAGRS = "RAGRS"
    ZRS = "ZRS"
    GZRS = "GZRS"
    RAZRS = "RAZRS"


@dataclass
class FunctionAppConfig:
    """Configuration for Azure Function App"""
    name: str
    runtime: str = "python"
    runtime_version: str = "3.11"
    sku_tier: SkuTier = SkuTier.CONSUMPTION
    sku_size: Optional[str] = None  # For Elastic Premium
    always_on: bool = False
    min_instances: int = 0
    max_instances: int = 200
    memory_limit_mb: int = 1536
    timeout_minutes: int = 10
    enable_application_insights: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template parameters"""
        result = {
            'name': self.name,
            'runtime': self.runtime,
            'runtimeVersion': self.runtime_version,
            'skuTier': self.sku_tier.value,
            'alwaysOn': self.always_on,
            'minInstances': self.min_instances,
            'maxInstances': self.max_instances,
            'memoryLimitMB': self.memory_limit_mb,
            'timeoutMinutes': self.timeout_minutes,
            'enableApplicationInsights': self.enable_application_insights
        }
        if self.sku_size:
            result['skuSize'] = self.sku_size
        return result


@dataclass
class ApplicationInsightsConfig:
    """Configuration for Application Insights"""
    name: str
    workspace_resource_id: Optional[str] = None  # Log Analytics workspace
    retention_days: int = 90
    sampling_percentage: float = 100.0
    disable_ip_masking: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template parameters"""
        result = {
            'name': self.name,
            'retentionDays': self.retention_days,
            'samplingPercentage': self.sampling_percentage,
            'disableIPMasking': self.disable_ip_masking
        }
        if self.workspace_resource_id:
            result['workspaceResourceId'] = self.workspace_resource_id
        return result


@dataclass
class StorageAccountConfig:
    """Configuration for Azure Storage Account"""
    name: str
    kind: StorageAccountKind = StorageAccountKind.STORAGE_V2
    performance: StorageAccountPerformance = StorageAccountPerformance.STANDARD
    replication: StorageAccountReplication = StorageAccountReplication.LRS
    access_tier: str = "Hot"
    enable_https_traffic_only: bool = True
    allow_blob_public_access: bool = False
    enable_static_website: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template parameters"""
        return {
            'name': self.name,
            'kind': self.kind.value,
            'performance': self.performance.value,
            'replication': self.replication.value,
            'accessTier': self.access_tier,
            'enableHttpsTrafficOnly': self.enable_https_traffic_only,
            'allowBlobPublicAccess': self.allow_blob_public_access,
            'enableStaticWebsite': self.enable_static_website
        }


@dataclass
class KeyVaultConfig:
    """Configuration for Azure Key Vault"""
    name: str
    enabled_for_deployment: bool = True
    enabled_for_disk_encryption: bool = True
    enabled_for_template_deployment: bool = True
    enable_purge_protection: bool = True
    enable_soft_delete: bool = True
    soft_delete_retention_days: int = 90
    sku_name: str = "standard"  # standard or premium
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template parameters"""
        return {
            'name': self.name,
            'enabledForDeployment': self.enabled_for_deployment,
            'enabledForDiskEncryption': self.enabled_for_disk_encryption,
            'enabledForTemplateDeployment': self.enabled_for_template_deployment,
            'enablePurgeProtection': self.enable_purge_protection,
            'enableSoftDelete': self.enable_soft_delete,
            'softDeleteRetentionDays': self.soft_delete_retention_days,
            'skuName': self.sku_name
        }


@dataclass
class ManagedIdentityConfig:
    """Configuration for Managed Identity"""
    name: str
    type: str = "SystemAssigned"  # SystemAssigned or UserAssigned
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template parameters"""
        return {
            'name': self.name,
            'type': self.type
        }


@dataclass
class FabricConfig:
    """Configuration for Microsoft Fabric"""
    workspace_name: str
    capacity_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template parameters"""
        result = {
            'workspaceName': self.workspace_name
        }
        if self.capacity_name:
            result['capacityName'] = self.capacity_name
        return result


@dataclass
class DeploymentParameters:
    """
    Main deployment parameters for MCP Framework.
    
    Contains all configuration needed to deploy the MCP Framework as an Azure Function App.
    """
    # Global parameters
    project_name: str
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    location: str = "eastus"
    resource_group_name: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Function App
    function_app: FunctionAppConfig = field(default_factory=FunctionAppConfig)
    
    # Application Insights
    application_insights: ApplicationInsightsConfig = field(default_factory=ApplicationInsightsConfig)
    
    # Storage Account
    storage_account: StorageAccountConfig = field(default_factory=StorageAccountConfig)
    
    # Key Vault
    key_vault: KeyVaultConfig = field(default_factory=KeyVaultConfig)
    
    # Managed Identity
    managed_identity: ManagedIdentityConfig = field(default_factory=ManagedIdentityConfig)
    
    # Fabric
    fabric: FabricConfig = field(default_factory=FabricConfig)
    
    # MCP Framework specific
    mcp_domain: str = "unknown"
    mcp_version: str = "1.0.0"
    enable_telemetry: bool = True
    enable_audit: bool = True
    enable_authentication: bool = True
    enable_authorization: bool = True
    enable_classification: bool = True
    
    def __post_init__(self):
        """Initialize default values after creation"""
        if self.resource_group_name is None:
            self.resource_group_name = f"{self.project_name}-{self.environment.value}-rg"
        
        if not self.tags:
            self.tags = {
                'Project': self.project_name,
                'Environment': self.environment.value,
                'MCP-Domain': self.mcp_domain,
                'MCP-Version': self.mcp_version
            }
        
        # Set default names if not provided
        if not hasattr(self.function_app, 'name') or not self.function_app.name:
            self.function_app.name = f"{self.project_name}-{self.environment.value}-func"
        
        if not hasattr(self.application_insights, 'name') or not self.application_insights.name:
            self.application_insights.name = f"{self.project_name}-{self.environment.value}-appinsights"
        
        if not hasattr(self.storage_account, 'name') or not self.storage_account.name:
            self.storage_account.name = f"{self.project_name}{self.environment.value}storage"
        
        if not hasattr(self.key_vault, 'name') or not self.key_vault.name:
            self.key_vault.name = f"{self.project_name}-{self.environment.value}-kv"
        
        if not hasattr(self.managed_identity, 'name') or not self.managed_identity.name:
            self.managed_identity.name = f"{self.project_name}-{self.environment.value}-identity"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all parameters to a dictionary for template deployment"""
        return {
            'global': {
                'projectName': self.project_name,
                'environment': self.environment.value,
                'location': self.location,
                'resourceGroupName': self.resource_group_name,
                'tags': self.tags,
                'mcpDomain': self.mcp_domain,
                'mcpVersion': self.mcp_version,
                'enableTelemetry': self.enable_telemetry,
                'enableAudit': self.enable_audit,
                'enableAuthentication': self.enable_authentication,
                'enableAuthorization': self.enable_authorization,
                'enableClassification': self.enable_classification
            },
            'functionApp': self.function_app.to_dict(),
            'applicationInsights': self.application_insights.to_dict(),
            'storageAccount': self.storage_account.to_dict(),
            'keyVault': self.key_vault.to_dict(),
            'managedIdentity': self.managed_identity.to_dict(),
            'fabric': self.fabric.to_dict()
        }
    
    def get_resource_group_name(self) -> str:
        """Get the resource group name"""
        return self.resource_group_name or f"{self.project_name}-{self.environment.value}-rg"
    
    def get_function_app_name(self) -> str:
        """Get the Function App name"""
        return self.function_app.name
    
    def get_storage_account_name(self) -> str:
        """Get the Storage Account name"""
        return self.storage_account.name
    
    def get_key_vault_name(self) -> str:
        """Get the Key Vault name"""
        return self.key_vault.name
    
    def get_application_insights_name(self) -> str:
        """Get the Application Insights name"""
        return self.application_insights.name


# Default deployment parameters
def get_default_parameters(
    project_name: str,
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT,
    location: str = "eastus",
    mcp_domain: str = "unknown"
) -> DeploymentParameters:
    """
    Get default deployment parameters.
    
    Args:
        project_name: Name of the project
        environment: Deployment environment
        location: Azure region
        mcp_domain: MCP domain name
    
    Returns:
        DeploymentParameters with sensible defaults
    """
    return DeploymentParameters(
        project_name=project_name,
        environment=environment,
        location=location,
        mcp_domain=mcp_domain,
        function_app=FunctionAppConfig(
            name=f"{project_name}-{environment.value}-func",
            sku_tier=SkuTier.CONSUMPTION,
            always_on=False,
            enable_application_insights=True
        ),
        application_insights=ApplicationInsightsConfig(
            name=f"{project_name}-{environment.value}-appinsights",
            retention_days=90
        ),
        storage_account=StorageAccountConfig(
            name=f"{project_name}{environment.value}storage",
            kind=StorageAccountKind.STORAGE_V2,
            replication=StorageAccountReplication.LRS,
            enable_https_traffic_only=True,
            allow_blob_public_access=False
        ),
        key_vault=KeyVaultConfig(
            name=f"{project_name}-{environment.value}-kv",
            enable_purge_protection=True,
            enable_soft_delete=True,
            sku_name="standard"
        ),
        managed_identity=ManagedIdentityConfig(
            name=f"{project_name}-{environment.value}-identity",
            type="SystemAssigned"
        ),
        fabric=FabricConfig(
            workspace_name=f"{project_name}-{environment.value}-workspace"
        )
    )