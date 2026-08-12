"""Semantic Model Client for Microsoft Fabric Power BI Semantic Models"""
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
class SemanticModelQuery:
    """Query for semantic model execution"""
    query: str
    model_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary"""
        return {
            'query': self.query,
            'model_id': self.model_id,
            'parameters': self.parameters,
            'options': self.options,
            'timeout_seconds': self.timeout_seconds
        }


@dataclass
class SemanticModelResult:
    """Result from semantic model query"""
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time_ms: float
    query: str
    model_id: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'data': self.data,
            'columns': self.columns,
            'row_count': self.row_count,
            'execution_time_ms': self.execution_time_ms,
            'query': self.query,
            'model_id': self.model_id,
            'error': self.error
        }


class SemanticModelClient:
    """
    Client for accessing Microsoft Fabric Power BI Semantic Models.
    
    Provides standardized access to semantic models for business metrics consumption.
    Domains should use this client rather than querying Gold tables directly.
    """
    
    def __init__(self, fabric_client: Optional[FabricClient] = None):
        """
        Initialize the semantic model client.
        
        Args:
            fabric_client: Fabric client instance (defaults to global client)
        """
        self.fabric_client = fabric_client or get_fabric_client()
        self._credential = DefaultAzureCredential()
        self._cache: Dict[str, Any] = {}
    
    def get_semantic_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get semantic model metadata.
        
        Args:
            model_id: Semantic model ID or name
        
        Returns:
            Semantic model metadata dictionary
        """
        cache_key = f"semantic_model_{model_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # This would use the Power BI REST API or Fabric API
            # For now, this is a placeholder implementation
            model_data = {
                'id': model_id,
                'name': model_id,
                'description': f"Semantic model: {model_id}",
                'tables': [],
                'measures': [],
                'relationships': [],
                'last_refreshed': datetime.utcnow().isoformat()
            }
            
            self._cache[cache_key] = model_data
            return model_data
            
        except Exception as e:
            logger.error(f"Error getting semantic model {model_id}: {str(e)}")
            raise
    
    def list_semantic_models(self) -> List[Dict[str, Any]]:
        """
        List all available semantic models in the workspace.
        
        Returns:
            List of semantic model metadata dictionaries
        """
        try:
            # This would use the Power BI REST API or Fabric API
            # For now, return a placeholder list
            return [
                {
                    'id': 'DonorManagement',
                    'name': 'Donor Management',
                    'description': 'Donor management semantic model',
                    'type': 'SemanticModel'
                },
                {
                    'id': 'Finance',
                    'name': 'Finance',
                    'description': 'Financial metrics semantic model',
                    'type': 'SemanticModel'
                }
            ]
        except Exception as e:
            logger.error(f"Error listing semantic models: {str(e)}")
            raise
    
    def execute(self, query: Union[str, SemanticModelQuery], model_id: Optional[str] = None) -> SemanticModelResult:
        """
        Execute a query against a semantic model.
        
        This is the main method that domains should use to access semantic models.
        
        Args:
            query: Query string or SemanticModelQuery object
            model_id: Semantic model ID (optional if query is SemanticModelQuery)
        
        Returns:
            SemanticModelResult with query results
        
        Example:
            # Simple query
            result = semantic_model.execute("EVALUATE DonorPortfolio")
            
            # Query with model ID
            result = semantic_model.execute("EVALUATE Revenue", model_id="Finance")
            
            # Query object
            query = SemanticModelQuery(
                query="EVALUATE DonorHealth",
                model_id="DonorManagement",
                parameters={"year": 2026}
            )
            result = semantic_model.execute(query)
        """
        import time
        start_time = time.time()
        
        try:
            # Convert string query to SemanticModelQuery if needed
            if isinstance(query, str):
                query_obj = SemanticModelQuery(query=query, model_id=model_id)
            else:
                query_obj = query
            
            # Get current identity for audit purposes
            identity = get_current_identity()
            user = identity.user_id if identity else "unknown"
            
            logger.info(f"Executing semantic model query: {query_obj.query[:50]}... by {user}")
            
            # This would use the Power BI REST API or XMLA endpoint
            # For now, this is a placeholder implementation
            
            # Simulate query execution
            if "error" in query_obj.query.lower():
                raise ValueError("Simulated query error")
            
            # Return mock data based on query
            data = self._generate_mock_data(query_obj.query)
            columns = list(data[0].keys()) if data else []
            
            execution_time = (time.time() - start_time) * 1000
            
            return SemanticModelResult(
                data=data,
                columns=columns,
                row_count=len(data),
                execution_time_ms=execution_time,
                query=query_obj.query,
                model_id=query_obj.model_id or model_id
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error executing semantic model query: {str(e)}")
            return SemanticModelResult(
                data=[],
                columns=[],
                row_count=0,
                execution_time_ms=execution_time,
                query=query_obj.query if isinstance(query, SemanticModelQuery) else query,
                model_id=model_id,
                error=str(e)
            )
    
    def _generate_mock_data(self, query: str) -> List[Dict[str, Any]]:
        """Generate mock data based on query type"""
        query_lower = query.lower()
        
        if "donor" in query_lower:
            return [
                {"DonorID": 1, "Name": "John Doe", "HealthScore": 85, "TotalContributions": 10000},
                {"DonorID": 2, "Name": "Jane Smith", "HealthScore": 92, "TotalContributions": 15000}
            ]
        elif "revenue" in query_lower:
            return [
                {"Year": 2024, "Revenue": 1000000, "Growth": 0.15},
                {"Year": 2025, "Revenue": 1150000, "Growth": 0.18}
            ]
        elif "pipeline" in query_lower:
            return [
                {"PipelineID": 1, "Stage": "Prospect", "Value": 50000, "Probability": 0.3},
                {"PipelineID": 2, "Stage": "Negotiation", "Value": 75000, "Probability": 0.7}
            ]
        else:
            return [{"Result": "Query executed successfully"}]
    
    def get_table_metadata(self, model_id: str, table_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific table in a semantic model.
        
        Args:
            model_id: Semantic model ID
            table_name: Table name
        
        Returns:
            Table metadata dictionary
        """
        try:
            model = self.get_semantic_model(model_id)
            for table in model.get('tables', []):
                if table.get('name') == table_name:
                    return table
            return {'error': f"Table {table_name} not found in model {model_id}"}
        except Exception as e:
            logger.error(f"Error getting table metadata: {str(e)}")
            raise
    
    def list_tables(self, model_id: str) -> List[str]:
        """
        List all tables in a semantic model.
        
        Args:
            model_id: Semantic model ID
        
        Returns:
            List of table names
        """
        try:
            model = self.get_semantic_model(model_id)
            return [table.get('name') for table in model.get('tables', [])]
        except Exception as e:
            logger.error(f"Error listing tables: {str(e)}")
            raise
    
    def clear_cache(self):
        """Clear the semantic model cache"""
        self._cache.clear()


# Global semantic model client instance
_semantic_model_client: Optional[SemanticModelClient] = None


def get_semantic_model_client() -> SemanticModelClient:
    """Get the global semantic model client instance"""
    global _semantic_model_client
    if _semantic_model_client is None:
        _semantic_model_client = SemanticModelClient()
    return _semantic_model_client


def reset_semantic_model_client():
    """Reset the global semantic model client instance"""
    global _semantic_model_client
    _semantic_model_client = None


# Convenience function for direct semantic model access
semantic_model = get_semantic_model_client()