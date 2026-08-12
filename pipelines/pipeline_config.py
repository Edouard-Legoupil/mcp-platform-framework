"""Pipeline Configuration for MCP Framework"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


@dataclass
class EnvironmentConfig:
    """Configuration for a deployment environment"""
    resource_group: str
    location: str = "eastus"
    mcp_domain: str = "unknown"
    deploy: bool = True
    environment_name: str = "Development"
    azure_service_connection: str = ""
    
    # Feature flags
    enable_telemetry: bool = True
    enable_audit: bool = True
    enable_authentication: bool = True
    enable_authorization: bool = True
    enable_classification: bool = True
    
    # Additional settings
    auto_discover_tools: bool = True
    tool_paths: List[str] = field(default_factory=lambda: ["tools", "queries", "actions", "resources"])


@dataclass
class PipelineConfig:
    """
    Main pipeline configuration for MCP Framework.
    
    Contains all configuration needed to generate CI/CD pipelines.
    """
    # Repository configuration
    project_name: str
    repository_name: str
    branch_name: str = "main"
    
    # Container registry (optional)
    container_registry: Optional[str] = None
    container_registry_endpoint: Optional[str] = None
    
    # Environments
    environments: Dict[str, EnvironmentConfig] = field(default_factory=dict)
    
    # Build configuration
    python_version: str = "3.11"
    test_coverage_threshold: int = 80
    security_scan_enabled: bool = True
    
    # Deployment configuration
    deploy_on_pr: bool = False
    deploy_on_main: bool = True
    deploy_on_release: bool = True
    
    # Notifications
    notification_email: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    teams_webhook_url: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default environments if not provided"""
        if not self.environments:
            self.environments = {
                "dev": EnvironmentConfig(
                    resource_group=f"{self.project_name}-dev-rg",
                    location="eastus",
                    mcp_domain=self.project_name,
                    deploy=True,
                    environment_name="Development",
                    azure_service_connection="Azure-Dev-Service-Connection"
                ),
                "test": EnvironmentConfig(
                    resource_group=f"{self.project_name}-test-rg",
                    location="eastus",
                    mcp_domain=self.project_name,
                    deploy=True,
                    environment_name="Test",
                    azure_service_connection="Azure-Test-Service-Connection"
                ),
                "prod": EnvironmentConfig(
                    resource_group=f"{self.project_name}-prod-rg",
                    location="eastus",
                    mcp_domain=self.project_name,
                    deploy=True,
                    environment_name="Production",
                    azure_service_connection="Azure-Prod-Service-Connection"
                )
            }
    
    def get_environment_names(self) -> List[str]:
        """Get list of environment names"""
        return list(self.environments.keys())
    
    def get_deployable_environments(self) -> List[str]:
        """Get list of environments that should be deployed"""
        return [name for name, config in self.environments.items() if config.deploy]
    
    def get_environment(self, name: str) -> Optional[EnvironmentConfig]:
        """Get environment configuration by name"""
        return self.environments.get(name)


def get_default_pipeline_config(
    project_name: str,
    repository_name: str = "mcp-platform-framework",
    branch_name: str = "main"
) -> PipelineConfig:
    """
    Get default pipeline configuration.
    
    Args:
        project_name: Name of the project
        repository_name: Name of the repository
        branch_name: Default branch name
    
    Returns:
        PipelineConfig with sensible defaults
    """
    return PipelineConfig(
        project_name=project_name,
        repository_name=repository_name,
        branch_name=branch_name,
        environments={
            "dev": EnvironmentConfig(
                resource_group=f"{project_name}-dev-rg",
                location="eastus",
                mcp_domain=project_name,
                deploy=True,
                environment_name="Development",
                azure_service_connection="Azure-Dev-Service-Connection"
            ),
            "test": EnvironmentConfig(
                resource_group=f"{project_name}-test-rg",
                location="eastus",
                mcp_domain=project_name,
                deploy=True,
                environment_name="Test",
                azure_service_connection="Azure-Test-Service-Connection"
            ),
            "prod": EnvironmentConfig(
                resource_group=f"{project_name}-prod-rg",
                location="eastus",
                mcp_domain=project_name,
                deploy=True,
                environment_name="Production",
                azure_service_connection="Azure-Prod-Service-Connection"
            )
        }
    )