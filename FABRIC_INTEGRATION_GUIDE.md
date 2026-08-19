# 🔗 MCP Server to Fabric Semantic Model Integration Guide

**For MCP Server Developers - Connecting to Microsoft Fabric Semantic Models**

This guide explains **exactly how to connect your MCP server to your specific Fabric semantic models**. If you're building an MCP server that needs to access Microsoft Fabric data (Lakehouses, Warehouses, Semantic Models), this is the guide for you.

---

## 🎯 **What You'll Learn**

1. [Understanding Fabric Semantic Models](#-understanding-fabric-semantic-models)
2. [Prerequisites for Fabric Integration](#-prerequisites-for-fabric-integration)
3. [Step 1: Configure Fabric Connection](#-step-1-configure-fabric-connection)
4. [Step 2: Define Your Semantic Model Connections](#-step-2-define-your-semantic-model-connections)
5. [Step 3: Create Semantic Model Tools](#-step-3-create-semantic-model-tools)
6. [Step 4: Query Semantic Models from Your MCP Server](#-step-4-query-semantic-models-from-your-mcp-server)
7. [Step 5: Expose Semantic Models as MCP Resources](#-step-5-expose-semantic-models-as-mcp-resources)
8. [Complete Example: End-to-End Integration](#-complete-example-end-to-end-integration)
9. [Troubleshooting Fabric Integration](#-troubleshooting-fabric-integration)

---

## 🧠 **Understanding Fabric Semantic Models**

### What is a Semantic Model?

A **Semantic Model** in Microsoft Fabric is a business-friendly abstraction layer over your data. It:
- Defines **business entities** (Customers, Products, Orders, etc.)
- Establishes **relationships** between entities
- Provides **business-friendly names** (instead of technical column names)
- Enables **self-service analytics** for business users
- Powers **Power BI reports** and **Copilot experiences**

### Semantic Model Types in Fabric

| Type | Description | Use Case |
|------|-------------|----------|
| **Lakehouse Semantic Model** | Built on Delta tables in a Lakehouse | Analytical workloads, large datasets |
| **Warehouse Semantic Model** | Built on SQL tables in a Warehouse | Transactional workloads, SQL queries |
| **Direct Lake Semantic Model** | Direct query on Delta tables | Real-time analytics |

### How MCP Servers Use Semantic Models

Your MCP server can:
1. **Query semantic models** - Execute DAX or SQL queries against your models
2. **Expose semantic models as resources** - Make your models discoverable via MCP
3. **Create tools that use semantic models** - Build business logic on top of your data
4. **Enable Copilot to access your data** - Allow Copilot to query your semantic models

---

## 🔧 **Prerequisites for Fabric Integration**

### 1. Azure & Fabric Setup

✅ **Microsoft Fabric Workspace** - You need a Fabric workspace
✅ **Semantic Models** - At least one semantic model created in your workspace
✅ **Fabric Admin Access** - Service principal with Fabric access
✅ **Azure AD App Registration** - For authentication

### 2. Required Information

Gather this information before starting:

```bash
# Fabric Workspace
FABRIC_TENANT_ID="your-tenant-id"           # Azure AD tenant ID
FABRIC_WORKSPACE_ID="your-workspace-id"     # Fabric workspace ID (GUID)

# Semantic Model
SEMANTIC_MODEL_ID="your-model-id"           # Semantic model ID (GUID)
SEMANTIC_MODEL_NAME="YourModel"            # Semantic model name

# Authentication
AZURE_TENANT_ID="your-tenant-id"            # Same as FABRIC_TENANT_ID
AZURE_CLIENT_ID="your-client-id"           # Azure AD app registration client ID
AZURE_CLIENT_SECRET="your-client-secret"   # Azure AD app registration secret
```

### 3. Fabric Permissions

Your service principal needs these permissions in Fabric:
- **Workspace Admin** or **Contributor** role on the workspace
- **Reader** access to the semantic models
- **Data Reader** permissions on underlying data

---

## ⚙️ **Step 1: Configure Fabric Connection**

### 1.1 Add Fabric Configuration to .env

Edit your `.env` file:

```bash
# Fabric Configuration
FABRIC_TENANT_ID=your-tenant-id
FABRIC_WORKSPACE_ID=your-workspace-id
FABRIC_SEMANTIC_MODEL_ID=your-model-id
FABRIC_SEMANTIC_MODEL_NAME=YourModel

# Azure AD Authentication for Fabric
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Optional: Specific endpoint (usually not needed)
FABRIC_ENDPOINT=https://api.fabric.microsoft.com
```

### 1.2 Configure Fabric Client in Your MCP Server

Create a Fabric configuration file:

```python
# my_domain/config/fabric_config.py
"""
Fabric Configuration for MCP Server
"""
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class FabricSemanticModel:
    """Represents a Fabric semantic model connection"""
    name: str
    model_id: str
    workspace_id: str
    tenant_id: str
    description: str = ""
    
    @property
    def full_name(self) -> str:
        return f"{self.workspace_id}/{self.name}"

@dataclass
class FabricConfig:
    """Fabric configuration for MCP server"""
    tenant_id: str
    workspace_id: str
    client_id: str
    client_secret: str
    semantic_models: List[FabricSemanticModel]
    
    @classmethod
    def from_environment(cls) -> "FabricConfig":
        """Load configuration from environment variables"""
        semantic_models = []
        
        # You can define multiple semantic models
        # For now, we'll use the one from environment
        if os.getenv('FABRIC_SEMANTIC_MODEL_ID') and os.getenv('FABRIC_SEMANTIC_MODEL_NAME'):
            semantic_models.append(
                FabricSemanticModel(
                    name=os.getenv('FABRIC_SEMANTIC_MODEL_NAME'),
                    model_id=os.getenv('FABRIC_SEMANTIC_MODEL_ID'),
                    workspace_id=os.getenv('FABRIC_WORKSPACE_ID'),
                    tenant_id=os.getenv('FABRIC_TENANT_ID'),
                    description=f"Semantic model: {os.getenv('FABRIC_SEMANTIC_MODEL_NAME')}"
                )
            )
        
        return cls(
            tenant_id=os.getenv('FABRIC_TENANT_ID', os.getenv('AZURE_TENANT_ID')),
            workspace_id=os.getenv('FABRIC_WORKSPACE_ID'),
            client_id=os.getenv('AZURE_CLIENT_ID'),
            client_secret=os.getenv('AZURE_CLIENT_SECRET'),
            semantic_models=semantic_models
        )

# Global fabric configuration instance
fabric_config = FabricConfig.from_environment()
```

---

## 🔗 **Step 2: Define Your Semantic Model Connections**

### 2.1 Create Semantic Model Connection Class

```python
# my_domain/connectivity/fabric_connector.py
"""
Fabric Semantic Model Connector
Handles connections to Microsoft Fabric semantic models
"""
import os
import logging
from typing import Optional, Dict, Any, List
from azure.identity import ClientSecretCredential
from azure.monitor.opentelemetry import AzureMonitorOpenTelemetryExporter

# Framework connectivity imports
from platform.connectivity.fabric_client import FabricClient
from my_domain.config.fabric_config import fabric_config, FabricSemanticModel

logger = logging.getLogger(__name__)

class SemanticModelConnector:
    """
    Connects to and queries Microsoft Fabric semantic models
    """
    
    def __init__(self, semantic_model: FabricSemanticModel):
        self.semantic_model = semantic_model
        self._client = None
    
    @property
    def client(self):
        """Lazy load Fabric client"""
        if self._client is None:
            # Use framework's Fabric client
            self._client = FabricClient(
                tenant_id=self.semantic_model.tenant_id,
                workspace_id=self.semantic_model.workspace_id,
                client_id=fabric_config.client_id,
                client_secret=fabric_config.client_secret
            )
        return self._client
    
    def get_model_metadata(self) -> Dict[str, Any]:
        """Get metadata about the semantic model"""
        try:
            metadata = self.client.get_semantic_model_metadata(
                workspace_id=self.semantic_model.workspace_id,
                model_id=self.semantic_model.model_id
            )
            return {
                "name": self.semantic_model.name,
                "id": self.semantic_model.model_id,
                "workspace_id": self.semantic_model.workspace_id,
                "tables": metadata.get("tables", []),
                "relationships": metadata.get("relationships", []),
                "measures": metadata.get("measures", []),
                "columns": metadata.get("columns", [])
            }
        except Exception as e:
            logger.error(f"Error getting model metadata: {str(e)}")
            raise
    
    def execute_dax_query(self, dax_query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a DAX query against the semantic model
        
        Args:
            dax_query: DAX query string (e.g., "EVALUATE Sales")
            **kwargs: Additional query parameters
            
        Returns:
            Dict with query results
        """
        try:
            result = self.client.execute_dax_query(
                workspace_id=self.semantic_model.workspace_id,
                model_id=self.semantic_model.model_id,
                query=dax_query,
                **kwargs
            )
            return {
                "success": True,
                "query": dax_query,
                "results": result.get("results", []),
                "columns": result.get("columns", []),
                "row_count": len(result.get("results", []))
            }
        except Exception as e:
            logger.error(f"Error executing DAX query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": dax_query
            }
    
    def execute_sql_query(self, sql_query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a SQL query against the semantic model
        
        Args:
            sql_query: SQL query string
            **kwargs: Additional query parameters
            
        Returns:
            Dict with query results
        """
        try:
            result = self.client.execute_sql_query(
                workspace_id=self.semantic_model.workspace_id,
                model_id=self.semantic_model.model_id,
                query=sql_query,
                **kwargs
            )
            return {
                "success": True,
                "query": sql_query,
                "results": result.get("results", []),
                "columns": result.get("columns", []),
                "row_count": len(result.get("results", []))
            }
        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": sql_query
            }
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema for a specific table in the semantic model"""
        try:
            schema = self.client.get_table_schema(
                workspace_id=self.semantic_model.workspace_id,
                model_id=self.semantic_model.model_id,
                table_name=table_name
            )
            return {
                "table": table_name,
                "columns": schema.get("columns", []),
                "measures": schema.get("measures", []),
                "relationships": schema.get("relationships", [])
            }
        except Exception as e:
            logger.error(f"Error getting table schema: {str(e)}")
            raise

# Global connector instances (one per semantic model)
semantic_model_connectors = {}

def get_semantic_model_connector(model_name: str) -> SemanticModelConnector:
    """Get a connector for a specific semantic model"""
    global semantic_model_connectors
    
    if model_name not in semantic_model_connectors:
        # Find the semantic model by name
        model = next(
            (m for m in fabric_config.semantic_models if m.name == model_name),
            None
        )
        if model is None:
            raise ValueError(f"Semantic model '{model_name}' not found in configuration")
        
        semantic_model_connectors[model_name] = SemanticModelConnector(model)
    
    return semantic_model_connectors[model_name]
```

---

## 🛠️ **Step 3: Create Semantic Model Tools**

### 3.1 Create Tools for Your Semantic Model

Here are examples of tools that interact with your Fabric semantic models:

```python
# my_domain/tools/semantic_model_tools.py
"""
Tools for interacting with Fabric Semantic Models
"""
from typing import Dict, Any, List, Optional
import logging

from my_domain.connectivity.fabric_connector import get_semantic_model_connector

logger = logging.getLogger(__name__)

def query_semantic_model(
    model_name: str,
    query_type: str = "dax",
    query: str = "",
    **kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a query against a semantic model
    
    Args:
        model_name: Name of the semantic model to query
        query_type: Type of query - "dax" or "sql"
        query: The query to execute
        **kwargs: Additional query parameters
        
    Returns:
        Dict with query results
    """
    try:
        connector = get_semantic_model_connector(model_name)
        
        if query_type.lower() == "dax":
            result = connector.execute_dax_query(query, **kwargs)
        elif query_type.lower() == "sql":
            result = connector.execute_sql_query(query, **kwargs)
        else:
            return {
                "success": False,
                "error": f"Unknown query type: {query_type}. Use 'dax' or 'sql'."
            }
        
        logger.info(f"Executed {query_type} query on model {model_name}")
        return result
        
    except Exception as e:
        logger.error(f"Error querying semantic model {model_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model": model_name,
            "query": query
        }

def get_semantic_model_metadata(model_name: str) -> Dict[str, Any]:
    """
    Get metadata about a semantic model
    
    Args:
        model_name: Name of the semantic model
        
    Returns:
        Dict with model metadata (tables, columns, relationships, etc.)
    """
    try:
        connector = get_semantic_model_connector(model_name)
        metadata = connector.get_model_metadata()
        
        logger.info(f"Retrieved metadata for model {model_name}")
        return {
            "success": True,
            "model": model_name,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Error getting metadata for model {model_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model": model_name
        }

def get_table_schema(model_name: str, table_name: str) -> Dict[str, Any]:
    """
    Get schema for a specific table in a semantic model
    
    Args:
        model_name: Name of the semantic model
        table_name: Name of the table
        
    Returns:
        Dict with table schema (columns, measures, relationships)
    """
    try:
        connector = get_semantic_model_connector(model_name)
        schema = connector.get_table_schema(table_name)
        
        logger.info(f"Retrieved schema for table {table_name} in model {model_name}")
        return {
            "success": True,
            "model": model_name,
            "table": table_name,
            "schema": schema
        }
        
    except Exception as e:
        logger.error(f"Error getting schema for table {table_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model": model_name,
            "table": table_name
        }

# Business-specific tools using semantic models
def get_sales_by_region(
    model_name: str,
    region: str = "All",
    year: int = 2024
) -> Dict[str, Any]:
    """
    Get sales data by region from a semantic model
    
    Args:
        model_name: Name of the semantic model containing sales data
        region: Region to filter by (default: "All")
        year: Year to filter by (default: current year)
        
    Returns:
        Dict with sales data by region
    """
    try:
        connector = get_semantic_model_connector(model_name)
        
        # DAX query for sales by region
        if region == "All":
            dax_query = f"EVALUATE SUMMARIZE(Sales, Sales[Region], \"Total Sales\", SUM(Sales[Amount]))"
        else:
            dax_query = f"EVALUATE FILTER(SUMMARIZE(Sales, Sales[Region], \"Total Sales\", SUM(Sales[Amount])), Sales[Region] = \"{region}\")"
        
        result = connector.execute_dax_query(dax_query)
        
        # Transform results for better presentation
        sales_data = []
        for row in result.get("results", []):
            sales_data.append({
                "region": row.get("Sales_Region", "Unknown"),
                "total_sales": row.get("Total Sales", 0)
            })
        
        logger.info(f"Retrieved sales data by region from model {model_name}")
        return {
            "success": True,
            "model": model_name,
            "region": region,
            "year": year,
            "sales_data": sales_data,
            "total_records": len(sales_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting sales by region: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model": model_name,
            "region": region,
            "year": year
        }
```

### 3.2 Register Semantic Model Tools

Edit `platform/registration/registry.py`:

```python
from my_domain.tools.semantic_model_tools import (
    query_semantic_model,
    get_semantic_model_metadata,
    get_table_schema,
    get_sales_by_region
)

SEMANTIC_MODEL_TOOLS = [
    {
        "name": "query_semantic_model",
        "description": "Execute DAX or SQL queries against a Fabric semantic model",
        "handler": "my_domain.tools.semantic_model_tools.query_semantic_model",
        "domain": "fabric",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Name of the semantic model to query"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["dax", "sql"],
                    "default": "dax",
                    "description": "Type of query to execute"
                },
                "query": {
                    "type": "string",
                    "description": "The query to execute"
                }
            },
            "required": ["model_name", "query"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "query": {"type": "string"},
                "results": {"type": "array"},
                "columns": {"type": "array"},
                "row_count": {"type": "integer"}
            }
        }
    },
    {
        "name": "get_semantic_model_metadata",
        "description": "Get metadata about a Fabric semantic model (tables, columns, relationships)",
        "handler": "my_domain.tools.semantic_model_tools.get_semantic_model_metadata",
        "domain": "fabric",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Name of the semantic model"
                }
            },
            "required": ["model_name"]
        }
    },
    {
        "name": "get_table_schema",
        "description": "Get schema for a specific table in a semantic model",
        "handler": "my_domain.tools.semantic_model_tools.get_table_schema",
        "domain": "fabric",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Name of the semantic model"
                },
                "table_name": {
                    "type": "string",
                    "description": "Name of the table"
                }
            },
            "required": ["model_name", "table_name"]
        }
    },
    {
        "name": "get_sales_by_region",
        "description": "Get sales data by region from a semantic model",
        "handler": "my_domain.tools.semantic_model_tools.get_sales_by_region",
        "domain": "business",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Name of the semantic model containing sales data"
                },
                "region": {
                    "type": "string",
                    "default": "All",
                    "description": "Region to filter by"
                },
                "year": {
                    "type": "integer",
                    "default": 2024,
                    "description": "Year to filter by"
                }
            },
            "required": ["model_name"]
        }
    }
]

# Add semantic model tools to your main TOOLS list
TOOLS = [
    # ... your existing tools ...
    *SEMANTIC_MODEL_TOOLS
]
```

---

## 📊 **Step 4: Query Semantic Models from Your MCP Server**

### 4.1 Using the Tools in Your MCP Server

Once registered, your tools can be called via the MCP protocol:

```bash
# Query a semantic model
curl -X POST http://localhost:7071/mcp/tools/query_semantic_model \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "SalesModel",
    "query_type": "dax",
    "query": "EVALUATE Sales"
  }'

# Get model metadata
curl -X POST http://localhost:7071/mcp/tools/get_semantic_model_metadata \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "SalesModel"
  }'

# Get sales by region
curl -X POST http://localhost:7071/mcp/tools/get_sales_by_region \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "SalesModel",
    "region": "North America",
    "year": 2024
  }'
```

### 4.2 Direct Integration in Function App

You can also directly integrate semantic model queries in your function app:

```python
# In src/azure/function_app.py
from my_domain.connectivity.fabric_connector import get_semantic_model_connector

@app.function_name(name="sales_dashboard")
@app.route(route="sales/dashboard", methods=["GET"])
def sales_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get sales dashboard data from semantic model
    """
    try:
        # Get the semantic model connector
        connector = get_semantic_model_connector("SalesModel")
        
        # Execute DAX query
        dax_query = """
        EVALUATE
        SUMMARIZE(
            Sales,
            Sales[Region],
            Sales[ProductCategory],
            "Total Sales", SUM(Sales[Amount]),
            "Average Sale", AVERAGE(Sales[Amount]),
            "Transaction Count", COUNTROWS(Sales)
        )
        """
        
        result = connector.execute_dax_query(dax_query)
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "data": result.get("results", []),
                "columns": result.get("columns", [])
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error in sales dashboard: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )
```

---

## 🌐 **Step 5: Expose Semantic Models as MCP Resources**

### 5.1 Create Resource Definitions for Semantic Models

```python
# my_domain/resources/semantic_model_resources.py
"""
Fabric Semantic Model Resources for MCP
"""
from typing import Dict, Any, List, Optional
from platform.catalog.models import Resource
from my_domain.config.fabric_config import fabric_config

# Define semantic models as MCP resources
SEMANTIC_MODEL_RESOURCES: List[Resource] = []

# Dynamically create resources from configuration
for semantic_model in fabric_config.semantic_models:
    SEMANTIC_MODEL_RESOURCES.append(
        Resource(
            name=f"fabric_semantic_model_{semantic_model.name}",
            description=f"Microsoft Fabric Semantic Model: {semantic_model.description}",
            type="fabric_semantic_model",
            uri=f"/fabric/workspaces/{semantic_model.workspace_id}/models/{semantic_model.model_id}",
            mime_type="application/json",
            metadata={
                "model_id": semantic_model.model_id,
                "workspace_id": semantic_model.workspace_id,
                "tenant_id": semantic_model.tenant_id,
                "model_name": semantic_model.name
            }
        )
    )
    
    # Also create resources for each table in the semantic model
    # (This would be populated dynamically at runtime)

# You can also define specific table resources
def get_semantic_model_table_resources(model_name: str) -> List[Resource]:
    """Get resources for tables in a semantic model"""
    try:
        connector = get_semantic_model_connector(model_name)
        metadata = connector.get_model_metadata()
        
        table_resources = []
        for table in metadata.get("tables", []):
            table_resources.append(
                Resource(
                    name=f"fabric_table_{model_name}_{table['name']}",
                    description=f"Table: {table['name']} in semantic model {model_name}",
                    type="fabric_table",
                    uri=f"/fabric/workspaces/{fabric_config.workspace_id}/models/{metadata['id']}/tables/{table['name']}",
                    mime_type="application/json",
                    metadata={
                        "model_name": model_name,
                        "table_name": table['name'],
                        "columns": table.get('columns', [])
                    }
                )
            )
        
        return table_resources
        
    except Exception as e:
        logger.error(f"Error getting table resources: {str(e)}")
        return []
```

### 5.2 Register Semantic Model Resources

Edit `platform/catalog/client.py` or create a resource registration file:

```python
# my_domain/resources/registration.py
"""
Register semantic model resources with the MCP framework
"""
from platform.catalog.client import get_catalog_client
from my_domain.resources.semantic_model_resources import SEMANTIC_MODEL_RESOURCES

def register_semantic_model_resources():
    """Register all semantic model resources with the catalog"""
    client = get_catalog_client()
    
    for resource in SEMANTIC_MODEL_RESOURCES:
        try:
            client.register_resource(resource)
            logger.info(f"Registered semantic model resource: {resource.name}")
        except Exception as e:
            logger.error(f"Error registering resource {resource.name}: {str(e)}")
    
    # Also register table resources for each semantic model
    from my_domain.config.fabric_config import fabric_config
    for semantic_model in fabric_config.semantic_models:
        table_resources = get_semantic_model_table_resources(semantic_model.name)
        for resource in table_resources:
            try:
                client.register_resource(resource)
                logger.info(f"Registered table resource: {resource.name}")
            except Exception as e:
                logger.error(f"Error registering table resource {resource.name}: {str(e)}")

# Call this during your MCP server initialization
# This could be in src/azure/function_app.py or in your domain initialization
```

---

## 🎯 **Complete Example: End-to-End Integration**

### Scenario: Sales Analytics MCP Server

Let's walk through a complete example of connecting an MCP server to a Fabric semantic model for sales analytics.

### Step 1: Set Up Your Environment

```bash
# .env file
FABRIC_TENANT_ID=your-tenant-id
FABRIC_WORKSPACE_ID=your-workspace-id
FABRIC_SEMANTIC_MODEL_ID=your-sales-model-id
FABRIC_SEMANTIC_MODEL_NAME=SalesModel

AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

### Step 2: Create Your Domain Structure

```bash
my_domain/
├── config/
│   └── fabric_config.py
├── connectivity/
│   └── fabric_connector.py
├── tools/
│   ├── __init__.py
│   └── sales_tools.py
└── resources/
    ├── __init__.py
    ├── semantic_model_resources.py
    └── registration.py
```

### Step 3: Implement Sales Tools

```python
# my_domain/tools/sales_tools.py
from typing import Dict, Any, List
import logging
from my_domain.connectivity.fabric_connector import get_semantic_model_connector

logger = logging.getLogger(__name__)

def get_top_products(
    model_name: str,
    limit: int = 10,
    by_metric: str = "sales"
) -> Dict[str, Any]:
    """
    Get top products by sales, quantity, or profit
    """
    try:
        connector = get_semantic_model_connector(model_name)
        
        if by_metric == "sales":
            dax_query = f"EVALUATE TOPN({limit}, SUMMARIZE(Sales, Sales[ProductName], \"Total Sales\", SUM(Sales[Amount])))"
        elif by_metric == "quantity":
            dax_query = f"EVALUATE TOPN({limit}, SUMMARIZE(Sales, Sales[ProductName], \"Total Quantity\", SUM(Sales[Quantity])))"
        elif by_metric == "profit":
            dax_query = f"EVALUATE TOPN({limit}, SUMMARIZE(Sales, Sales[ProductName], \"Total Profit\", SUM(Sales[Profit])))"
        else:
            return {"success": False, "error": f"Unknown metric: {by_metric}"}
        
        result = connector.execute_dax_query(dax_query)
        
        # Format results
        products = []
        for row in result.get("results", []):
            products.append({
                "product": row.get("Sales_ProductName", "Unknown"),
                "value": row.get(f"Total {by_metric.capitalize()}", 0)
            })
        
        return {
            "success": True,
            "model": model_name,
            "metric": by_metric,
            "limit": limit,
            "products": products
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_sales_trend(
    model_name: str,
    time_period: str = "monthly",
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """
    Get sales trend over time
    """
    try:
        connector = get_semantic_model_connector(model_name)
        
        if time_period == "daily":
            dax_query = "EVALUATE SUMMARIZE(Sales, Sales[Date], \"Total Sales\", SUM(Sales[Amount]))"
        elif time_period == "weekly":
            dax_query = "EVALUATE SUMMARIZE(Sales, \"Week\", FORMAT(Sales[Date], \"yyyy-w\"), \"Total Sales\", SUM(Sales[Amount]))"
        elif time_period == "monthly":
            dax_query = "EVALUATE SUMMARIZE(Sales, \"Month\", FORMAT(Sales[Date], \"yyyy-MM\"), \"Total Sales\", SUM(Sales[Amount]))"
        elif time_period == "quarterly":
            dax_query = "EVALUATE SUMMARIZE(Sales, \"Quarter\", \"Q\" & QUARTER(Sales[Date]) & \" \" & YEAR(Sales[Date]), \"Total Sales\", SUM(Sales[Amount]))"
        elif time_period == "yearly":
            dax_query = "EVALUATE SUMMARIZE(Sales, \"Year\", YEAR(Sales[Date]), \"Total Sales\", SUM(Sales[Amount]))"
        else:
            return {"success": False, "error": f"Unknown time period: {time_period}"}
        
        result = connector.execute_dax_query(dax_query)
        
        return {
            "success": True,
            "model": model_name,
            "time_period": time_period,
            "trend_data": result.get("results", [])
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Step 4: Register Tools and Resources

```python
# In platform/registration/registry.py
from my_domain.tools.sales_tools import get_top_products, get_sales_trend

SALES_TOOLS = [
    {
        "name": "get_top_products",
        "description": "Get top products by sales, quantity, or profit",
        "handler": "my_domain.tools.sales_tools.get_top_products",
        "domain": "sales",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name": {"type": "string", "description": "Name of the semantic model"},
                "limit": {"type": "integer", "default": 10, "description": "Number of top products"},
                "by_metric": {"type": "string", "enum": ["sales", "quantity", "profit"], "default": "sales"}
            },
            "required": ["model_name"]
        }
    },
    {
        "name": "get_sales_trend",
        "description": "Get sales trend over time (daily, weekly, monthly, quarterly, yearly)",
        "handler": "my_domain.tools.sales_tools.get_sales_trend",
        "domain": "sales",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name": {"type": "string", "description": "Name of the semantic model"},
                "time_period": {"type": "string", "enum": ["daily", "weekly", "monthly", "quarterly", "yearly"], "default": "monthly"}
            },
            "required": ["model_name"]
        }
    }
]

TOOLS = [
    # ... other tools ...
    *SALES_TOOLS
]
```

### Step 5: Initialize and Test

```python
# In src/azure/function_app.py
import logging
from my_domain.resources.registration import register_semantic_model_resources

logger = logging.getLogger(__name__)

# Initialize semantic model resources when the app starts
@app.function_name(name="initialize_semantic_models")
@app.route(route="mcp/initialize", methods=["POST"])
def initialize_semantic_models(req: func.HttpRequest) -> func.HttpResponse:
    """
    Initialize semantic model resources
    """
    try:
        register_semantic_model_resources()
        return func.HttpResponse(
            json.dumps({"success": True, "message": "Semantic models initialized"}),
            status_code=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error initializing semantic models: {str(e)}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )
```

### Step 6: Test Your Integration

```bash
# Test the tools
curl -X POST http://localhost:7071/mcp/tools/get_top_products \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "SalesModel",
    "limit": 5,
    "by_metric": "sales"
  }'

curl -X POST http://localhost:7071/mcp/tools/get_sales_trend \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "SalesModel",
    "time_period": "monthly"
  }'

# List resources (should show your semantic models)
curl http://localhost:7071/mcp/resources
```

---

## 🐛 **Troubleshooting Fabric Integration**

### Common Issues and Solutions

#### Issue 1: Authentication Failed

**Symptoms:**
```
Error: Authentication failed - Invalid credentials
```

**Solutions:**
1. Verify `AZURE_CLIENT_ID` and `AZURE_CLIENT_SECRET` are correct
2. Check that the service principal has the correct permissions in Fabric
3. Ensure the service principal is in the same tenant as your Fabric workspace
4. Verify the service principal hasn't expired

**Debugging:**
```python
from azure.identity import ClientSecretCredential

# Test authentication
credential = ClientSecretCredential(
    tenant_id=fabric_config.tenant_id,
    client_id=fabric_config.client_id,
    client_secret=fabric_config.client_secret
)

try:
    token = credential.get_token("https://api.fabric.microsoft.com/.default")
    print(f"Authentication successful. Token expires: {token.expires_on}")
except Exception as e:
    print(f"Authentication failed: {str(e)}")
```

#### Issue 2: Semantic Model Not Found

**Symptoms:**
```
Error: Semantic model 'SalesModel' not found
```

**Solutions:**
1. Verify `FABRIC_SEMANTIC_MODEL_ID` is correct
2. Check that the semantic model exists in the specified workspace
3. Ensure the service principal has access to the workspace
4. Verify the workspace ID is correct

**Debugging:**
```python
from my_domain.connectivity.fabric_connector import get_semantic_model_connector

try:
    connector = get_semantic_model_connector("SalesModel")
    metadata = connector.get_model_metadata()
    print(f"Model found: {metadata}")
except Exception as e:
    print(f"Error: {str(e)}")
```

#### Issue 3: Query Execution Failed

**Symptoms:**
```
Error: Query execution failed - Syntax error in DAX query
```

**Solutions:**
1. Validate your DAX query syntax
2. Check that the table and column names exist in the semantic model
3. Ensure you're using the correct case (DAX is case-insensitive, but column names might be)
4. Test the query in Power BI first

**Debugging:**
```python
# Test your query directly
connector = get_semantic_model_connector("SalesModel")
result = connector.execute_dax_query("EVALUATE Sales")
print(result)
```

#### Issue 4: Permission Denied

**Symptoms:**
```
Error: Permission denied - User does not have access to the resource
```

**Solutions:**
1. Verify the service principal has **Reader** role on the semantic model
2. Check that the service principal has **Data Reader** permissions on the underlying data
3. Ensure the service principal has **Workspace Contributor** or **Admin** role
4. Check if the semantic model has row-level security (RLS) that might be blocking access

**Debugging:**
```python
# Check permissions
from my_domain.connectivity.fabric_connector import get_semantic_model_connector

try:
    connector = get_semantic_model_connector("SalesModel")
    # Try a simple query
    result = connector.execute_dax_query("EVALUATE ROW(\"Test\", 1)")
    print("Permissions OK")
except Exception as e:
    print(f"Permission error: {str(e)}")
```

#### Issue 5: Connection Timeout

**Symptoms:**
```
Error: Connection timeout - Request timed out
```

**Solutions:**
1. Check your network connectivity to Fabric
2. Verify that the Fabric endpoint is accessible
3. Increase timeout settings in your Fabric client
4. Check if there are any firewall rules blocking access

**Debugging:**
```python
import requests

# Test connectivity to Fabric
try:
    response = requests.get("https://api.fabric.microsoft.com/v1/workspaces", timeout=10)
    print(f"Fabric API accessible. Status: {response.status_code}")
except Exception as e:
    print(f"Connection error: {str(e)}")
```

---

## 📚 **Best Practices for Fabric Integration**

### 1. Connection Management

✅ **Do:**
- Use connection pooling for better performance
- Implement retry logic for transient failures
- Cache metadata to reduce API calls
- Use lazy loading for connectors

❌ **Don't:**
- Create a new connection for every query
- Hardcode credentials in your code
- Ignore connection errors
- Forget to close connections

### 2. Query Optimization

✅ **Do:**
- Use DAX queries for analytical operations
- Use SQL queries for transactional operations
- Filter data at the query level
- Use aggregation functions in queries
- Limit result sets

❌ **Don't:**
- Retrieve all data and filter in Python
- Use complex queries that return large result sets
- Ignore query performance
- Forget to add query timeouts

### 3. Error Handling

✅ **Do:**
- Catch and handle Fabric-specific exceptions
- Provide meaningful error messages
- Log errors for debugging
- Implement retry logic for transient errors
- Validate inputs before querying

❌ **Don't:**
- Let exceptions bubble up to users
- Return generic error messages
- Ignore authentication errors
- Forget to log errors

### 4. Security

✅ **Do:**
- Use service principals for authentication
- Store credentials in Azure Key Vault
- Implement least-privilege access
- Use managed identities when possible
- Rotate credentials regularly

❌ **Don't:**
- Hardcode credentials in your code
- Use personal accounts for service authentication
- Grant excessive permissions
- Store credentials in plain text files
- Forget to rotate credentials

### 5. Performance

✅ **Do:**
- Cache frequently accessed data
- Use pagination for large result sets
- Implement query timeouts
- Monitor query performance
- Optimize DAX/SQL queries

❌ **Don't:**
- Execute long-running queries without timeouts
- Retrieve more data than needed
- Ignore performance metrics
- Forget to monitor query execution times

---

## 🎯 **Next Steps**

Now that you've connected your MCP server to your Fabric semantic models:

1. ✅ **Test locally** - Verify all tools and resources work
2. ✅ **Deploy to Azure** - Use the deployment script
3. ✅ **Test in production** - Verify Fabric connectivity in Azure
4. ✅ **Integrate with Copilot** - Connect your MCP server to Copilot
5. ✅ **Monitor usage** - Set up telemetry and logging
6. ✅ **Optimize performance** - Fine-tune queries and caching

---

## 📞 **Getting Help**

### Fabric Documentation
- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [Fabric Semantic Models](https://learn.microsoft.com/en-us/fabric/data-engineering/semantic-model-overview)
- [Fabric REST API](https://learn.microsoft.com/en-us/rest/api/fabric/)

### MCP Framework Help
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user guide
- **[FRAMEWORK_DOCUMENTATION.md](FRAMEWORK_DOCUMENTATION.md)** - Framework internals
- **[TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md)** - Quick start template

---

## 💡 **Key Takeaways**

1. **Fabric Connection** - Configure your Fabric tenant, workspace, and semantic model IDs
2. **Authentication** - Use service principals with proper permissions
3. **Semantic Model Tools** - Create tools that query your semantic models
4. **Resources** - Expose your semantic models as MCP resources
5. **Testing** - Always test locally before deploying
6. **Error Handling** - Implement robust error handling for Fabric operations

**Remember:** Your MCP server acts as a bridge between Copilot/Copilot Studio and your Fabric semantic models. The clearer and more robust this connection, the better the experience for your users!

---

**🚀 Your MCP server is now connected to your Fabric semantic models!**

Users can now:
- Query your semantic models through MCP tools
- Discover your semantic models as MCP resources
- Access your data through Copilot and Copilot Studio
- Build intelligent applications on top of your Fabric data
