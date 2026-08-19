"""
Fabric Connectivity Layer for MCP Framework

This package provides connectivity to various data sources for MCP servers.

For MCP Server Developers:
- Use fabric_semantic_models module for simple Fabric semantic model connectivity
- Use existing clients for more advanced scenarios

For Framework Contributors:
- Extend the connectivity layer with new data source connectors
"""

from .fabric_client import FabricClient, FabricConnectionConfig
from .semantic_models import SemanticModelClient, SemanticModelQuery
from .warehouse import WarehouseClient, WarehouseQuery
from .lakehouse import LakehouseClient, LakehouseQuery
from .connectors import (
    get_fabric_client, 
    get_semantic_model_client, 
    get_warehouse_client, 
    get_lakehouse_client,
    fabric
)
from .fabric_semantic_models import (
    FabricSemanticModel,
    SemanticModelConnector,
    get_semantic_model_connector,
    reset_semantic_model_connectors,
    list_semantic_models
)

__all__ = [
    'FabricClient', 'FabricConnectionConfig',
    'SemanticModelClient', 'SemanticModelQuery',
    'WarehouseClient', 'WarehouseQuery',
    'LakehouseClient', 'LakehouseQuery',
    'get_fabric_client', 'get_semantic_model_client',
    'get_warehouse_client', 'get_lakehouse_client',
    'fabric',
    # Simplified Fabric semantic model connectivity
    'FabricSemanticModel',
    'SemanticModelConnector',
    'get_semantic_model_connector',
    'reset_semantic_model_connectors',
    'list_semantic_models'
]