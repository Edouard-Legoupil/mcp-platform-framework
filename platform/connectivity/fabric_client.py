"""Fabric Client for Microsoft Fabric Integration"""
import logging
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from azure.identity import DefaultAzureCredential
from azure.mgmt.fabric import FabricManagementClient
from azure.core.exceptions import AzureError
from platform.config import get_config_manager

logger = logging.getLogger(__name__)


@dataclass
class FabricConnectionConfig:
    """Configuration for Microsoft Fabric connection"""
    subscription_id: str
    resource_group: str
    workspace_id: str
    endpoint: Optional[str] = None
    credential: Optional[Any] = None
    
    @classmethod
    def from_config(cls) -> 'FabricConnectionConfig':
        """Create FabricConnectionConfig from platform configuration"""
        config = get_config_manager()
        
        return cls(
            subscription_id=config.get_azure_config().subscription_id,
            resource_group=config.get_fabric_config().resource_group,
            workspace_id=config.get_fabric_config().workspace_id,
            endpoint=config.get_fabric_config().endpoint,
            credential=DefaultAzureCredential()
        )


class FabricClient:
    """
    Client for Microsoft Fabric operations.
    
    Provides connectivity to Microsoft Fabric workspaces, capacity, and governance.
    """
    
    def __init__(self, config: FabricConnectionConfig):
        """
        Initialize the Fabric client.
        
        Args:
            config: Fabric connection configuration
        """
        self.config = config
        self._mgmt_client: Optional[FabricManagementClient] = None
        self._credential = config.credential or DefaultAzureCredential()
    
    @property
    def mgmt_client(self) -> FabricManagementClient:
        """Get or create the Fabric management client"""
        if self._mgmt_client is None:
            self._mgmt_client = FabricManagementClient(
                credential=self._credential,
                subscription_id=self.config.subscription_id
            )
        return self._mgmt_client
    
    def get_workspace(self, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get workspace information.
        
        Args:
            workspace_id: Workspace ID (defaults to configured workspace)
        
        Returns:
            Workspace information dictionary
        """
        workspace_id = workspace_id or self.config.workspace_id
        try:
            workspace = self.mgmt_client.workspaces.get(
                resource_group_name=self.config.resource_group,
                workspace_name=workspace_id
            )
            return {
                'id': workspace.id,
                'name': workspace.name,
                'location': workspace.location,
                'provisioning_state': workspace.provisioning_state,
                'type': workspace.type,
                'sku': workspace.sku.name if workspace.sku else None
            }
        except AzureError as e:
            logger.error(f"Error getting workspace {workspace_id}: {str(e)}")
            raise
    
    def list_workspaces(self) -> List[Dict[str, Any]]:
        """
        List all workspaces in the resource group.
        
        Returns:
            List of workspace information dictionaries
        """
        try:
            workspaces = self.mgmt_client.workspaces.list(
                resource_group_name=self.config.resource_group
            )
            return [
                {
                    'id': ws.id,
                    'name': ws.name,
                    'location': ws.location,
                    'provisioning_state': ws.provisioning_state,
                    'type': ws.type
                }
                for ws in workspaces
            ]
        except AzureError as e:
            logger.error(f"Error listing workspaces: {str(e)}")
            raise
    
    def get_capacity(self, capacity_id: str) -> Dict[str, Any]:
        """
        Get capacity information.
        
        Args:
            capacity_id: Capacity ID
        
        Returns:
            Capacity information dictionary
        """
        try:
            capacity = self.mgmt_client.capacities.get(
                resource_group_name=self.config.resource_group,
                capacity_name=capacity_id
            )
            return {
                'id': capacity.id,
                'name': capacity.name,
                'location': capacity.location,
                'sku': capacity.sku.name if capacity.sku else None,
                'provisioning_state': capacity.provisioning_state,
                'administrators': [admin.identity.principal_id for admin in capacity.administrators]
                if capacity.administrators else []
            }
        except AzureError as e:
            logger.error(f"Error getting capacity {capacity_id}: {str(e)}")
            raise
    
    def list_capacities(self) -> List[Dict[str, Any]]:
        """
        List all capacities in the resource group.
        
        Returns:
            List of capacity information dictionaries
        """
        try:
            capacities = self.mgmt_client.capacities.list(
                resource_group_name=self.config.resource_group
            )
            return [
                {
                    'id': cap.id,
                    'name': cap.name,
                    'location': cap.location,
                    'sku': cap.sku.name if cap.sku else None,
                    'provisioning_state': cap.provisioning_state
                }
                for cap in capacities
            ]
        except AzureError as e:
            logger.error(f"Error listing capacities: {str(e)}")
            raise
    
    def execute_query(self, query: str, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a Fabric query (using REST API).
        
        Args:
            query: The query to execute
            workspace_id: Workspace ID (defaults to configured workspace)
        
        Returns:
            Query results dictionary
        """
        # This would use the Fabric REST API or SDK
        # For now, this is a placeholder implementation
        logger.warning("Fabric query execution not yet implemented")
        return {'results': [], 'query': query}
    
    def get_endpoint(self) -> str:
        """Get the Fabric endpoint URL"""
        return self.config.endpoint or f"https://api.fabric.microsoft.com"


# Global Fabric client instance
_fabric_client: Optional[FabricClient] = None


def get_fabric_client() -> FabricClient:
    """Get the global Fabric client instance"""
    global _fabric_client
    if _fabric_client is None:
        config = FabricConnectionConfig.from_config()
        _fabric_client = FabricClient(config)
    return _fabric_client


def reset_fabric_client():
    """Reset the global Fabric client instance"""
    global _fabric_client
    _fabric_client = None