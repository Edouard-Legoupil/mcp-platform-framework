# 🔗 MCP Server to Fabric Semantic Model Integration Guide

**For MCP Server Developers - Connecting to Microsoft Fabric Semantic Models**

This guide explains **exactly how to connect your MCP server to your specific Fabric semantic models** using the built-in connectivity layer. The framework already includes everything you need!

---

## 🎯 **Quick Answer: It's Already Built-In!**

The MCP Framework includes a **ready-to-use Fabric semantic model connector** in:
```python
from platform.connectivity import get_semantic_model_connector
```

**You only need to set 3 environment variables:**
```bash
FABRIC_WORKSPACE_ID=your-workspace-id
FABRIC_SEMANTIC_MODEL_ID=your-model-id
FABRIC_SEMANTIC_MODEL_NAME=YourModelName
```

**That's it!** No complex configuration needed.

---

## 🧠 **Understanding Fabric Semantic Models**

### What is a Semantic Model?

A **Semantic Model** in Microsoft Fabric is a business-friendly abstraction layer over your data. It:
- Defines **business entities** (Customers, Products, Orders, etc.)
- Establishes **relationships** between entities
- Provides **business-friendly names** (instead of technical column names)
- Enables **self-service analytics** for business users
- Powers **Power BI reports** and **Copilot experiences**

### How MCP Servers Use Semantic Models

Your MCP server can:
1. **Query semantic models** - Execute DAX or SQL queries against your models
2. **Expose semantic models as resources** - Make your models discoverable via MCP
3. **Create tools that use semantic models** - Build business logic on top of your data
4. **Enable Copilot to access your data** - Allow Copilot to query your semantic models

---

## 🚀 **Quick Start - 5 Minutes to Fabric Integration**

### Step 1: Set Environment Variables

Add these to your `.env` file:

```bash
# Required: Fabric Workspace
FABRIC_WORKSPACE_ID=your-workspace-id  # GUID from Fabric

# Required: Semantic Model
FABRIC_SEMANTIC_MODEL_ID=your-model-id    # GUID from Fabric
FABRIC_SEMANTIC_MODEL_NAME=YourModelName # Your model name

# Required: Azure AD Authentication (same as other Azure services)
AZURE_TENANT_ID=your-tenant-id            # Your Azure AD tenant
AZURE_CLIENT_ID=your-client-id           # Service principal client ID
AZURE_CLIENT_SECRET=your-client-secret # Service principal secret
```

**💡 Note:** `FABRIC_TENANT_ID` is **NOT needed** - the framework uses `AZURE_TENANT_ID` automatically.

### Step 2: Use the Built-In Connector

```python
# In your tool implementation
from platform.connectivity import get_semantic_model_connector

def my_tool_function(param: str) -> dict:
    # Get connector for your semantic model
    connector = get_semantic_model_connector("YourModelName")
    
    # Execute a DAX query
    result = connector.execute_dax_query("EVALUATE Sales")
    
    return {"data": result["results"]}
```

### Step 3: Register Your Tool

```python
# In platform/registration/registry.py
TOOLS = [
    {
        "name": "my_tool",
        "description": "My tool that queries Fabric",
        "handler": "my_domain.tools.my_tool.my_tool_function",
        "domain": "my_domain",
        "version": "1.0.0"
    }
]
```

### Step 4: Test It

```bash
# Start your MCP server
cd src/azure
func start

# Test your tool
curl -X POST http://localhost:7071/mcp/tools/my_tool \
  -H "Content-Type: application/json" \
  -d '{"param": "value"}'
```

**🎉 You're done!** Your MCP server is now connected to your Fabric semantic model.

---

## 🔧 **Detailed Usage**

### The Built-In Connector

The framework provides `SemanticModelConnector` with these methods:

```python
from platform.connectivity import (
    get_semantic_model_connector,
    SemanticModelConnector,
    FabricSemanticModel
)

# Get a connector
connector = get_semantic_model_connector("YourModelName")

# Available methods:
connector.execute_dax_query("EVALUATE Sales")      # DAX queries
connector.execute_sql_query("SELECT * FROM Sales") # SQL queries
connector.get_model_metadata()                      # Get model info
connector.get_table_schema("Sales")               # Get table schema
```

### Authentication

The connector uses **DefaultAzureCredential** which automatically tries:
1. **Managed Identity** (if running in Azure)
2. **Service Principal** (using AZURE_CLIENT_ID/SECRET)
3. **Visual Studio Code** (for local development)
4. **Azure CLI** (if logged in)

**No manual authentication needed!**

---

## 🛠️ **Complete Examples**

### Example 1: Simple Query Tool

```python
# my_domain/tools/sales_query.py
from typing import Dict, Any
from platform.connectivity import get_semantic_model_connector

def query_sales(model_name: str, query: str) -> Dict[str, Any]:
    """Execute a query against a Fabric semantic model"""
    connector = get_semantic_model_connector(model_name)
    result = connector.execute_dax_query(query)
    return result
```

### Example 2: Business-Specific Tool

```python
# my_domain/tools/sales_analytics.py
from typing import Dict, Any, List
from platform.connectivity import get_semantic_model_connector

def get_top_products(
    model_name: str,
    limit: int = 10
) -> Dict[str, Any]:
    """Get top products by sales"""
    connector = get_semantic_model_connector(model_name)
    
    dax_query = f"""
    EVALUATE
    TOPN(
        {limit},
        SUMMARIZE(
            Sales,
            Sales[ProductName],
            "Total Sales", SUM(Sales[Amount])
        ),
        [Total Sales]
    )
    """
    
    result = connector.execute_dax_query(dax_query)
    
    # Format results
    products = []
    for row in result.get("results", []):
        products.append({
            "product": row.get("Sales_ProductName", "Unknown"),
            "total_sales": row.get("Total Sales", 0)
        })
    
    return {
        "success": True,
        "products": products,
        "count": len(products)
    }
```

### Example 3: Get Model Metadata

```python
# my_domain/tools/model_info.py
from typing import Dict, Any
from platform.connectivity import get_semantic_model_connector

def get_model_info(model_name: str) -> Dict[str, Any]:
    """Get information about a semantic model"""
    connector = get_semantic_model_connector(model_name)
    metadata = connector.get_model_metadata()
    
    return {
        "success": True,
        "model_name": model_name,
        "model_id": metadata.get("id"),
        "workspace_id": metadata.get("workspace_id"),
        "tables": metadata.get("tables", []),
        "table_count": len(metadata.get("tables", []))
    }
```

### Example 4: Direct Integration in Function App

```python
# In src/azure/function_app.py
from platform.connectivity import get_semantic_model_connector
import json

@app.function_name(name="sales_dashboard")
@app.route(route="sales/dashboard", methods=["GET"])
def sales_dashboard(req: func.HttpRequest) -> func.HttpResponse:
    """Get sales dashboard data from Fabric semantic model"""
    try:
        connector = get_semantic_model_connector("SalesModel")
        
        # DAX query for sales summary
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

## 🌐 **Exposing Semantic Models as MCP Resources**

### Simple Resource Registration

```python
# my_domain/resources/fabric_resources.py
from typing import List
from platform.catalog.models import Resource
import os

def get_fabric_resources() -> List[Resource]:
    """Get MCP resources for Fabric semantic models"""
    workspace_id = os.getenv('FABRIC_WORKSPACE_ID')
    model_name = os.getenv('FABRIC_SEMANTIC_MODEL_NAME')
    model_id = os.getenv('FABRIC_SEMANTIC_MODEL_ID')
    
    if not all([workspace_id, model_name, model_id]):
        return []
    
    return [
        Resource(
            name=f"fabric_semantic_model_{model_name}",
            description=f"Microsoft Fabric Semantic Model: {model_name}",
            type="fabric_semantic_model",
            uri=f"/fabric/workspaces/{workspace_id}/models/{model_id}",
            mime_type="application/json",
            metadata={
                "model_id": model_id,
                "workspace_id": workspace_id,
                "model_name": model_name
            }
        )
    ]
```

### Register Resources on Startup

```python
# In src/azure/function_app.py
from my_domain.resources.fabric_resources import get_fabric_resources
from platform.catalog.client import get_catalog_client

@app.function_name(name="initialize_fabric")
@app.route(route="mcp/initialize_fabric", methods=["POST"])
def initialize_fabric_resources(req: func.HttpRequest) -> func.HttpResponse:
    """Initialize Fabric resources"""
    try:
        client = get_catalog_client()
        for resource in get_fabric_resources():
            client.register_resource(resource)
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message": "Fabric resources initialized",
                "resources": [r.name for r in get_fabric_resources()]
            }),
            status_code=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error initializing Fabric resources: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )
```

---

## 📋 **Configuration Reference**

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FABRIC_WORKSPACE_ID` | Your Fabric workspace ID (GUID) | `11111111-2222-3333-4444-555555555555` |
| `FABRIC_SEMANTIC_MODEL_ID` | Your semantic model ID (GUID) | `22222222-3333-4444-5555-666666666666` |
| `FABRIC_SEMANTIC_MODEL_NAME` | Your semantic model name | `SalesModel` |
| `AZURE_TENANT_ID` | Your Azure AD tenant ID | `33333333-4444-5555-6666-777777777777` |
| `AZURE_CLIENT_ID` | Service principal client ID | `44444444-5555-6666-7777-888888888888` |
| `AZURE_CLIENT_SECRET` | Service principal secret | `your-secret-value` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FABRIC_ENDPOINT` | Custom Fabric API endpoint | `https://api.fabric.microsoft.com` |

---

## 🔍 **Finding Your Fabric Information**

### Via Power BI Service (Easiest)

1. Go to [Power BI Service](https://app.powerbi.com)
2. Navigate to your workspace
3. Click on your semantic model
4. **Workspace ID** is in the URL: `https://app.powerbi.com/groups/{workspace-id}/...`
5. **Model ID** is in the URL when you click on the model

### Via Fabric REST API

```bash
# List workspaces (requires authentication)
curl -X GET "https://api.fabric.microsoft.com/v1/workspaces" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get semantic models in a workspace
curl -X GET "https://api.fabric.microsoft.com/v1/workspaces/{workspace-id}/semanticModels" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## ⚙️ **Authentication Setup**

### Option 1: Service Principal (Recommended for Production)

```bash
# Create a service principal
az ad sp create-for-rbac --name MyMCPServerSP

# Output will include:
# AZURE_TENANT_ID=...
# AZURE_CLIENT_ID=...
# AZURE_CLIENT_SECRET=...
```

**Required Permissions in Fabric:**
- Workspace: **Contributor** or **Admin**
- Semantic Model: **Reader**
- Underlying Data: **Data Reader**

### Option 2: Managed Identity (Best for Azure Deployments)

When deployed to Azure, the framework automatically uses **Managed Identity** if available.

**Required Setup:**
1. Enable Managed Identity for your Function App
2. Grant the Managed Identity access to your Fabric workspace
3. No environment variables needed for authentication!

### Option 3: Local Development (Azure CLI)

For local development, the framework can use your Azure CLI credentials:

```bash
# Login to Azure CLI
az login

# The framework will automatically use these credentials
```

---

## 🐛 **Troubleshooting**

### Common Issues

#### "FABRIC_WORKSPACE_ID environment variable is not set"

**Solution:** Add `FABRIC_WORKSPACE_ID` to your `.env` file or environment.

#### "Semantic model not found"

**Solution:** Verify that:
1. `FABRIC_SEMANTIC_MODEL_ID` is correct
2. `FABRIC_SEMANTIC_MODEL_NAME` matches your model name
3. The service principal has access to the workspace

#### "Authentication failed"

**Solution:** Verify that:
1. `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` are correct
2. The service principal hasn't expired
3. The service principal has the correct permissions in Fabric

#### "Permission denied"

**Solution:** Grant the service principal:
- **Workspace Contributor** or **Admin** role
- **Reader** access to the semantic model
- **Data Reader** permissions on underlying data

### Debugging Tips

```python
# Test your configuration
from platform.connectivity import get_semantic_model_connector

try:
    connector = get_semantic_model_connector("YourModelName")
    metadata = connector.get_model_metadata()
    print(f"✅ Connected to model: {metadata['name']}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
```

---

## 📚 **Best Practices**

### 1. Connection Management

✅ **Do:**
- Reuse connector instances (they're cached automatically)
- Use the built-in `get_semantic_model_connector()` function
- Let the framework handle authentication

❌ **Don't:**
- Create your own Fabric client classes
- Hardcode credentials in your code
- Manage connections manually

### 2. Query Design

✅ **Do:**
- Use DAX for analytical queries (aggregations, filtering)
- Use SQL for transactional queries (joins, complex filtering)
- Filter at the query level, not in Python
- Use aggregation functions in queries

❌ **Don't:**
- Retrieve all data and filter in Python
- Use complex queries that return large result sets
- Forget to limit result sets

### 3. Error Handling

✅ **Do:**
- Catch exceptions from Fabric operations
- Provide meaningful error messages to users
- Log errors for debugging

❌ **Don't:**
- Let Fabric exceptions bubble up to users
- Return generic error messages
- Ignore authentication errors

### 4. Security

✅ **Do:**
- Use Managed Identity for Azure deployments
- Use Service Principal for production
- Store secrets in Azure Key Vault
- Implement least-privilege access

❌ **Don't:**
- Hardcode credentials in your code
- Use personal accounts for service authentication
- Grant excessive permissions

---

## 🎯 **Complete Example: Sales Analytics MCP Server**

Here's a complete example showing how to build a sales analytics MCP server connected to Fabric:

### 1. Environment Configuration (`.env`)

```bash
# Azure AD
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Fabric
FABRIC_WORKSPACE_ID=your-workspace-id
FABRIC_SEMANTIC_MODEL_ID=your-sales-model-id
FABRIC_SEMANTIC_MODEL_NAME=SalesModel
```

### 2. Tool Implementation

```python
# my_domain/tools/sales_tools.py
from typing import Dict, Any, List
from platform.connectivity import get_semantic_model_connector

def get_sales_by_region(
    model_name: str,
    region: str = "All"
) -> Dict[str, Any]:
    """Get sales data by region"""
    connector = get_semantic_model_connector(model_name)
    
    if region == "All":
        dax_query = "EVALUATE SUMMARIZE(Sales, Sales[Region], \"Total Sales\", SUM(Sales[Amount]))"
    else:
        dax_query = f'EVALUATE FILTER(SUMMARIZE(Sales, Sales[Region], "Total Sales", SUM(Sales[Amount])), Sales[Region] = "{region}")'
    
    result = connector.execute_dax_query(dax_query)
    
    sales_data = []
    for row in result.get("results", []):
        sales_data.append({
            "region": row.get("Sales_Region", "Unknown"),
            "total_sales": row.get("Total Sales", 0)
        })
    
    return {
        "success": True,
        "region": region,
        "sales_data": sales_data
    }

def get_top_products(
    model_name: str,
    limit: int = 10
) -> Dict[str, Any]:
    """Get top products by sales"""
    connector = get_semantic_model_connector(model_name)
    
    dax_query = f"""
    EVALUATE
    TOPN(
        {limit},
        SUMMARIZE(Sales, Sales[ProductName], "Total Sales", SUM(Sales[Amount])),
        [Total Sales]
    )
    """
    
    result = connector.execute_dax_query(dax_query)
    
    products = []
    for row in result.get("results", []):
        products.append({
            "product": row.get("Sales_ProductName", "Unknown"),
            "total_sales": row.get("Total Sales", 0)
        })
    
    return {
        "success": True,
        "limit": limit,
        "products": products
    }
```

### 3. Tool Registration

```python
# platform/registration/registry.py
from my_domain.tools.sales_tools import get_sales_by_region, get_top_products

TOOLS = [
    {
        "name": "get_sales_by_region",
        "description": "Get sales data by region from Fabric semantic model",
        "handler": "my_domain.tools.sales_tools.get_sales_by_region",
        "domain": "sales",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name": {"type": "string", "description": "Name of the semantic model"},
                "region": {"type": "string", "default": "All", "description": "Region to filter by"}
            },
            "required": ["model_name"]
        }
    },
    {
        "name": "get_top_products",
        "description": "Get top products by sales from Fabric semantic model",
        "handler": "my_domain.tools.sales_tools.get_top_products",
        "domain": "sales",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name": {"type": "string", "description": "Name of the semantic model"},
                "limit": {"type": "integer", "default": 10, "description": "Number of top products"}
            },
            "required": ["model_name"]
        }
    }
]
```

### 4. Test Your Server

```bash
# Start the server
cd src/azure
func start

# Test your tools
curl -X POST http://localhost:7071/mcp/tools/get_sales_by_region \
  -H "Content-Type: application/json" \
  -d '{"model_name": "SalesModel", "region": "North America"}'

curl -X POST http://localhost:7071/mcp/tools/get_top_products \
  -H "Content-Type: application/json" \
  -d '{"model_name": "SalesModel", "limit": 5}'
```

---

## 🎉 **You're Ready!**

The MCP Framework includes **everything you need** to connect to Fabric semantic models:

✅ **Built-in connector** - `get_semantic_model_connector()`
✅ **Simple configuration** - Just 3 environment variables
✅ **Automatic authentication** - Uses DefaultAzureCredential
✅ **DAX & SQL support** - Both query types available
✅ **Metadata access** - Get model and table information
✅ **Resource exposure** - Easy MCP resource registration

**No complex setup needed!** Just configure your environment variables and start using the built-in connector.

---

## 📞 **Getting Help**

### Documentation
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete MCP server development guide
- **[FRAMEWORK_DOCUMENTATION.md](FRAMEWORK_DOCUMENTATION.md)** - Framework internals
- **[TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md)** - Quick start template

### External Resources
- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [Fabric Semantic Models](https://learn.microsoft.com/en-us/fabric/data-engineering/semantic-model-overview)
- [DAX Language Reference](https://learn.microsoft.com/en-us/dax/dax-function-reference)
- [Fabric REST API](https://learn.microsoft.com/en-us/rest/api/fabric/)

---

**🚀 Your MCP server is now connected to your Fabric semantic models with minimal configuration!**
