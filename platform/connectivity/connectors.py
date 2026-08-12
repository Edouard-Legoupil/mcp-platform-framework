"""Fabric Connectors for MCP Framework"""
import logging
from typing import Optional, Dict, Any, List, Union
from .fabric_client import FabricClient, get_fabric_client, reset_fabric_client
from .semantic_models import SemanticModelClient, get_semantic_model_client, reset_semantic_model_client
from .warehouse import WarehouseClient, get_warehouse_client, reset_warehouse_client
from .lakehouse import LakehouseClient, get_lakehouse_client, reset_lakehouse_client

logger = logging.getLogger(__name__)


class FabricConnectors:
    """
    Unified Fabric connectors for MCP Framework.
    
    Provides a single interface for accessing all Fabric services:
    - Semantic Models (Power BI)
    - Warehouses
    - Lakehouses
    - General Fabric operations
    """
    
    def __init__(
        self,
        fabric_client: Optional[FabricClient] = None,
        semantic_model_client: Optional[SemanticModelClient] = None,
        warehouse_client: Optional[WarehouseClient] = None,
        lakehouse_client: Optional[LakehouseClient] = None
    ):
        """
        Initialize the Fabric connectors.
        
        Args:
            fabric_client: Fabric client instance
            semantic_model_client: Semantic model client instance
            warehouse_client: Warehouse client instance
            lakehouse_client: Lakehouse client instance
        """
        self.fabric = fabric_client or get_fabric_client()
        self.semantic_models = semantic_model_client or get_semantic_model_client()
        self.warehouse = warehouse_client or get_warehouse_client()
        self.lakehouse = lakehouse_client or get_lakehouse_client()
    
    def get_semantic_model(self, model_id: str) -> Dict[str, Any]:
        """Get semantic model metadata"""
        return self.semantic_models.get_semantic_model(model_id)
    
    def list_semantic_models(self) -> List[Dict[str, Any]]:
        """List all semantic models"""
        return self.semantic_models.list_semantic_models()
    
    def execute_semantic_query(self, query: Union[str, Any], model_id: Optional[str] = None) -> Any:
        """Execute a semantic model query"""
        return self.semantic_models.execute(query, model_id)
    
    def get_warehouse(self, warehouse_id: str) -> Dict[str, Any]:
        """Get warehouse metadata"""
        return self.warehouse.get_warehouse(warehouse_id)
    
    def list_warehouses(self) -> List[Dict[str, Any]]:
        """List all warehouses"""
        return self.warehouse.list_warehouses()
    
    def execute_warehouse_query(self, query: Union[str, Any], warehouse_id: Optional[str] = None) -> Any:
        """Execute a warehouse query"""
        return self.warehouse.execute(query, warehouse_id)
    
    def get_lakehouse(self, lakehouse_id: str) -> Dict[str, Any]:
        """Get lakehouse metadata"""
        return self.lakehouse.get_lakehouse(lakehouse_id)
    
    def list_lakehouses(self) -> List[Dict[str, Any]]:
        """List all lakehouses"""
        return self.lakehouse.list_lakehouses()
    
    def execute_lakehouse_query(self, query: Union[str, Any], lakehouse_id: Optional[str] = None) -> Any:
        """Execute a lakehouse query"""
        return self.lakehouse.execute(query, lakehouse_id)
    
    def get_workspace(self, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        """Get workspace information"""
        return self.fabric.get_workspace(workspace_id)
    
    def list_workspaces(self) -> List[Dict[str, Any]]:
        """List all workspaces"""
        return self.fabric.list_workspaces()
    
    def get_capacity(self, capacity_id: str) -> Dict[str, Any]:
        """Get capacity information"""
        return self.fabric.get_capacity(capacity_id)
    
    def list_capacities(self) -> List[Dict[str, Any]]:
        """List all capacities"""
        return self.fabric.list_capacities()


# Global Fabric connectors instance
_fabric_connectors: Optional[FabricConnectors] = None


def get_fabric_connectors() -> FabricConnectors:
    """Get the global Fabric connectors instance"""
    global _fabric_connectors
    if _fabric_connectors is None:
        _fabric_connectors = FabricConnectors()
    return _fabric_connectors


def reset_fabric_connectors():
    """Reset all Fabric connectors"""
    global _fabric_connectors
    _fabric_connectors = None
    reset_fabric_client()
    reset_semantic_model_client()
    reset_warehouse_client()
    reset_lakehouse_client()


# Convenience functions for direct access
def get_fabric() -> FabricConnectors:
    """Get the global Fabric connectors (alias for get_fabric_connectors)"""
    return get_fabric_connectors()


# Create a global fabric connector instance for direct access
fabric = get_fabric_connectors()


__all__ = [
    'FabricConnectors',
    'get_fabric_connectors', 'reset_fabric_connectors',
    'get_fabric', 'fabric',
    'get_fabric_client', 'reset_fabric_client',
    'get_semantic_model_client', 'reset_semantic_model_client',
    'get_warehouse_client', 'reset_warehouse_client',
    'get_lakehouse_client', 'reset_lakehouse_client'
]