"""Warehouse Client for Microsoft Fabric Warehouses"""
import logging
import json
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError
from .fabric_client import FabricClient, get_fabric_client
from platform.config import get_config_manager
from platform.auth import get_current_identity

logger = logging.getLogger(__name__)


@dataclass
class WarehouseQuery:
    """Query for warehouse execution"""
    query: str
    warehouse_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 60
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary"""
        return {
            'query': self.query,
            'warehouse_id': self.warehouse_id,
            'parameters': self.parameters,
            'options': self.options,
            'timeout_seconds': self.timeout_seconds
        }


@dataclass
class WarehouseResult:
    """Result from warehouse query"""
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time_ms: float
    query: str
    warehouse_id: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'data': self.data,
            'columns': self.columns,
            'row_count': self.row_count,
            'execution_time_ms': self.execution_time_ms,
            'query': self.query,
            'warehouse_id': self.warehouse_id,
            'error': self.error
        }


class WarehouseClient:
    """
    Client for accessing Microsoft Fabric Warehouses.
    
    Provides standardized access to Fabric warehouses for SQL queries.
    """
    
    def __init__(self, fabric_client: Optional[FabricClient] = None):
        """
        Initialize the warehouse client.
        
        Args:
            fabric_client: Fabric client instance (defaults to global client)
        """
        self.fabric_client = fabric_client or get_fabric_client()
        self._credential = DefaultAzureCredential()
        self._cache: Dict[str, Any] = {}
    
    def get_warehouse(self, warehouse_id: str) -> Dict[str, Any]:
        """
        Get warehouse metadata.
        
        Args:
            warehouse_id: Warehouse ID or name
        
        Returns:
            Warehouse metadata dictionary
        """
        cache_key = f"warehouse_{warehouse_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # This would use the Fabric REST API
            # For now, this is a placeholder implementation
            warehouse_data = {
                'id': warehouse_id,
                'name': warehouse_id,
                'description': f"Fabric Warehouse: {warehouse_id}",
                'type': 'Warehouse',
                'sku': 'Standard',
                'provisioning_state': 'Succeeded',
                'last_refreshed': datetime.utcnow().isoformat()
            }
            
            self._cache[cache_key] = warehouse_data
            return warehouse_data
            
        except Exception as e:
            logger.error(f"Error getting warehouse {warehouse_id}: {str(e)}")
            raise
    
    def list_warehouses(self) -> List[Dict[str, Any]]:
        """
        List all available warehouses in the workspace.
        
        Returns:
            List of warehouse metadata dictionaries
        """
        try:
            # This would use the Fabric REST API
            # For now, return a placeholder list
            return [
                {
                    'id': 'DataWarehouse',
                    'name': 'Data Warehouse',
                    'description': 'Enterprise data warehouse',
                    'type': 'Warehouse'
                },
                {
                    'id': 'AnalyticsWarehouse',
                    'name': 'Analytics Warehouse',
                    'description': 'Analytics data warehouse',
                    'type': 'Warehouse'
                }
            ]
        except Exception as e:
            logger.error(f"Error listing warehouses: {str(e)}")
            raise
    
    def execute(self, query: Union[str, WarehouseQuery], warehouse_id: Optional[str] = None) -> WarehouseResult:
        """
        Execute a SQL query against a warehouse.
        
        Args:
            query: Query string or WarehouseQuery object
            warehouse_id: Warehouse ID (optional if query is WarehouseQuery)
        
        Returns:
            WarehouseResult with query results
        
        Example:
            # Simple query
            result = warehouse.execute("SELECT * FROM Donors")
            
            # Query with warehouse ID
            result = warehouse.execute("SELECT * FROM Revenue", warehouse_id="DataWarehouse")
            
            # Query object
            query = WarehouseQuery(
                query="SELECT * FROM Pipeline WHERE Status = @status",
                warehouse_id="DataWarehouse",
                parameters={"status": "Active"}
            )
            result = warehouse.execute(query)
        """
        import time
        start_time = time.time()
        
        try:
            # Convert string query to WarehouseQuery if needed
            if isinstance(query, str):
                query_obj = WarehouseQuery(query=query, warehouse_id=warehouse_id)
            else:
                query_obj = query
            
            # Get current identity for audit purposes
            identity = get_current_identity()
            user = identity.user_id if identity else "unknown"
            
            logger.info(f"Executing warehouse query: {query_obj.query[:50]}... by {user}")
            
            # This would use the Fabric SQL endpoint
            # For now, this is a placeholder implementation
            
            # Simulate query execution
            if "error" in query_obj.query.lower():
                raise ValueError("Simulated query error")
            
            # Return mock data based on query
            data = self._generate_mock_data(query_obj.query)
            columns = list(data[0].keys()) if data else []
            
            execution_time = (time.time() - start_time) * 1000
            
            return WarehouseResult(
                data=data,
                columns=columns,
                row_count=len(data),
                execution_time_ms=execution_time,
                query=query_obj.query,
                warehouse_id=query_obj.warehouse_id or warehouse_id
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error executing warehouse query: {str(e)}")
            return WarehouseResult(
                data=[],
                columns=[],
                row_count=0,
                execution_time_ms=execution_time,
                query=query_obj.query if isinstance(query, WarehouseQuery) else query,
                warehouse_id=warehouse_id,
                error=str(e)
            )
    
    def _generate_mock_data(self, query: str) -> List[Dict[str, Any]]:
        """Generate mock data based on query type"""
        query_lower = query.lower()
        
        if "select" in query_lower and "donor" in query_lower:
            return [
                {"DonorID": 1, "Name": "John Doe", "Email": "john@example.com", "TotalDonations": 10000},
                {"DonorID": 2, "Name": "Jane Smith", "Email": "jane@example.com", "TotalDonations": 15000}
            ]
        elif "select" in query_lower and "revenue" in query_lower:
            return [
                {"Year": 2024, "Month": 1, "Revenue": 100000, "Source": "Donations"},
                {"Year": 2024, "Month": 2, "Revenue": 120000, "Source": "Grants"}
            ]
        elif "select" in query_lower and "pipeline" in query_lower:
            return [
                {"PipelineID": 1, "Stage": "Prospect", "Value": 50000, "Probability": 0.3, "Status": "Active"},
                {"PipelineID": 2, "Stage": "Negotiation", "Value": 75000, "Probability": 0.7, "Status": "Active"}
            ]
        else:
            return [{"Result": "Query executed successfully"}]
    
    def get_table_schema(self, warehouse_id: str, table_name: str) -> Dict[str, Any]:
        """
        Get schema for a specific table in a warehouse.
        
        Args:
            warehouse_id: Warehouse ID
            table_name: Table name
        
        Returns:
            Table schema dictionary
        """
        try:
            warehouse = self.get_warehouse(warehouse_id)
            # This would query the warehouse for table schema
            # For now, return mock schema
            return {
                'table': table_name,
                'columns': [
                    {'name': 'ID', 'type': 'INT', 'nullable': False},
                    {'name': 'Name', 'type': 'VARCHAR', 'nullable': True},
                    {'name': 'CreatedAt', 'type': 'DATETIME', 'nullable': True}
                ]
            }
        except Exception as e:
            logger.error(f"Error getting table schema: {str(e)}")
            raise
    
    def list_tables(self, warehouse_id: str) -> List[str]:
        """
        List all tables in a warehouse.
        
        Args:
            warehouse_id: Warehouse ID
        
        Returns:
            List of table names
        """
        try:
            # This would query the warehouse for table list
            # For now, return mock table list
            return ["Donors", "Revenue", "Pipeline", "Campaigns"]
        except Exception as e:
            logger.error(f"Error listing tables: {str(e)}")
            raise
    
    def clear_cache(self):
        """Clear the warehouse cache"""
        self._cache.clear()


# Global warehouse client instance
_warehouse_client: Optional[WarehouseClient] = None


def get_warehouse_client() -> WarehouseClient:
    """Get the global warehouse client instance"""
    global _warehouse_client
    if _warehouse_client is None:
        _warehouse_client = WarehouseClient()
    return _warehouse_client


def reset_warehouse_client():
    """Reset the global warehouse client instance"""
    global _warehouse_client
    _warehouse_client = None