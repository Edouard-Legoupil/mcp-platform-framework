# 🌐 Fabric Connectivity Module

The Fabric Connectivity Module provides standardized connectors for Microsoft Fabric integration, enabling domains to access semantic models, warehouses, lakehouses, and other Fabric endpoints in a consistent and secure manner.

## 🎯 Overview

The Fabric Connectivity Module handles:
- **Semantic Model Access**: Standardized connectors for semantic models
- **Warehouse Connectors**: SQL query execution and data retrieval
- **Lakehouse Connectors**: Delta table access and file system operations
- **Fabric Endpoint Adapters**: REST API, GraphQL, and WebSocket integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│       Fabric Connectivity Module         │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Semantic Model  │  │ Warehouse       │ │
│  │ Connectors      │  │ Connectors      │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Lakehouse       │  │ Fabric          │ │
│  │ Connectors      │  │ Endpoint        │ │
│  └─────────────────┘  │ Adapters        │ │
│                      └─────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Basic Usage

```python
from platform.fabric import get_semantic_model, get_warehouse

# Semantic model access
semantic_model = get_semantic_model("DonorManagement")
result = semantic_model.execute(
    query="SELECT DonorCount, TotalRevenue FROM DonorMetrics WHERE Year = 2026"
)

# Warehouse access
warehouse = get_warehouse("GoldLayer")
data = warehouse.query(
    sql="SELECT * FROM dimDonor WHERE Status = 'Active'"
)
```

### Configuration

```python
# config/fabric.py
from platform.fabric.config import FabricConfig

FABRIC_CONFIG = FabricConfig(
    # Fabric endpoint
    endpoint="https://fabric.my-org.org",
    
    # Authentication
    authentication_type="managed_identity",  # or "service_principal", "entra_id"
    
    # Semantic models
    semantic_models={
        "DonorManagement": {
            "workspace": "DER-Analytics",
            "model_id": "DonorManagement-Model",
            "classification": "CONFIDENTIAL"
        },
        "Finance": {
            "workspace": "DER-Finance",
            "model_id": "Finance-Model",
            "classification": "STRICTLY CONFIDENTIAL"
        }
    },
    
    # Warehouses
    warehouses={
        "GoldLayer": {
            "workspace": "DER-Data",
            "warehouse_id": "GoldLayer-Warehouse",
            "classification": "INTERNAL"
        },
        "SilverLayer": {
            "workspace": "DER-Data",
            "warehouse_id": "SilverLayer-Warehouse",
            "classification": "INTERNAL"
        }
    },
    
    # Lakehouses
    lakehouses={
        "Gold": {
            "workspace": "DER-Data",
            "lakehouse_id": "Gold-Lakehouse",
            "classification": "CONFIDENTIAL"
        }
    },
    
    # Connection pooling
    connection_pooling={
        "enabled": True,
        "max_connections": 10,
        "connection_timeout": 30,
        "max_retries": 3
    },
    
    # Caching
    caching={
        "enabled": True,
        "ttl": 300,
        "max_size": 1000
    }
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Fabric Configuration
FABRIC_ENDPOINT=https://fabric.my-org.org
FABRIC_AUTHENTICATION_TYPE=managed_identity

# Semantic Models
FABRIC_SEMANTIC_MODELS=DonorManagement,Finance

# Warehouses
FABRIC_WAREHOUSES=GoldLayer,SilverLayer

# Lakehouses
FABRIC_LAKEHOUSES=Gold

# Connection Pooling
FABRIC_POOLING_ENABLED=true
FABRIC_MAX_CONNECTIONS=10
FABRIC_CONNECTION_TIMEOUT=30

# Caching
FABRIC_CACHING_ENABLED=true
FABRIC_CACHE_TTL=300
```

### Configuration File

```yaml
# config/fabric.yaml
fabric:
  endpoint: ${FABRIC_ENDPOINT}
  
  authentication:
    type: managed_identity  # managed_identity, service_principal, entra_id
    client_id: ${AZURE_CLIENT_ID}
    client_secret: ${AZURE_CLIENT_SECRET}
    tenant_id: ${AZURE_TENANT_ID}
    
  semantic_models:
    DonorManagement:
      workspace: DER-Analytics
      model_id: DonorManagement-Model
      classification: CONFIDENTIAL
      timeout: 60
      max_retries: 3
      
    Finance:
      workspace: DER-Finance
      model_id: Finance-Model
      classification: STRICTLY CONFIDENTIAL
      timeout: 120
      max_retries: 5
      
  warehouses:
    GoldLayer:
      workspace: DER-Data
      warehouse_id: GoldLayer-Warehouse
      classification: INTERNAL
      timeout: 300
      
    SilverLayer:
      workspace: DER-Data
      warehouse_id: SilverLayer-Warehouse
      classification: INTERNAL
      timeout: 180
      
  lakehouses:
    Gold:
      workspace: DER-Data
      lakehouse_id: Gold-Lakehouse
      classification: CONFIDENTIAL
      timeout: 300
      
  connection_pooling:
    enabled: true
    max_connections: 10
    connection_timeout: 30
    max_retries: 3
    
  caching:
    enabled: true
    ttl: 300
    max_size: 1000
    
  query:
    batch_size: 1000
    fetch_size: 100
    max_rows: 100000
    
  security:
    encrypt_in_transit: true
    validate_certificates: true
    audit_queries: true
```

## 🎯 API Reference

### Functions

#### `get_semantic_model(name)`

Gets a semantic model connector.

```python
from platform.fabric import get_semantic_model

# Get semantic model
semantic_model = get_semantic_model("DonorManagement")

# Execute query
result = semantic_model.execute(
    query="SELECT DonorCount, TotalRevenue FROM DonorMetrics WHERE Year = 2026"
)

# Execute with parameters
result = semantic_model.execute(
    query="SELECT * FROM DonorMetrics WHERE Year = @year",
    parameters={"year": 2026}
)
```

**Parameters:**
- `name` (str): Semantic model name

**Returns:**
- `SemanticModel`: Semantic model connector

#### `get_warehouse(name)`

Gets a warehouse connector.

```python
from platform.fabric import get_warehouse

# Get warehouse
warehouse = get_warehouse("GoldLayer")

# Execute SQL query
result = warehouse.query(
    sql="SELECT * FROM dimDonor WHERE Status = 'Active'"
)

# Execute with parameters
result = warehouse.query(
    sql="SELECT * FROM dimDonor WHERE Year = @year",
    parameters={"year": 2026}
)

# Execute and fetch all results
all_results = warehouse.query_all(
    sql="SELECT * FROM dimDonor"
)
```

**Parameters:**
- `name` (str): Warehouse name

**Returns:**
- `Warehouse`: Warehouse connector

#### `get_lakehouse(name)`

Gets a lakehouse connector.

```python
from platform.fabric import get_lakehouse

# Get lakehouse
lakehouse = get_lakehouse("Gold")

# Read table
result = lakehouse.read_table("DonorData")

# Read with filters
result = lakehouse.read_table(
    "DonorData",
    filters=[{"column": "Status", "operator": "=", "value": "Active"}]
)

# Write data
lakehouse.write_table("NewDonorData", data=dataframe)

# Delete data
lakehouse.delete_table(
    "DonorData",
    filters=[{"column": "DonorID", "operator": "=", "value": "DON-12345"}]
)
```

**Parameters:**
- `name` (str): Lakehouse name

**Returns:**
- `Lakehouse`: Lakehouse connector

#### `get_fabric_client()`

Gets the Fabric client for direct API access.

```python
from platform.fabric import get_fabric_client

# Get Fabric client
client = get_fabric_client()

# Execute REST API call
response = client.get("/api/v1/workspaces")

# Execute GraphQL query
result = client.graphql(
    query="""
    query {
        workspaces {
            name
            id
        }
    }
    """
)
```

**Returns:**
- `FabricClient`: Fabric API client

### Classes

#### `SemanticModel`

Provides access to Fabric semantic models.

```python
from platform.fabric import SemanticModel

# Create semantic model
semantic_model = SemanticModel(
    name="DonorManagement",
    workspace="DER-Analytics",
    model_id="DonorManagement-Model"
)

# Execute query
result = semantic_model.execute(
    query="SELECT DonorCount, TotalRevenue FROM DonorMetrics WHERE Year = 2026"
)

# Execute with parameters
result = semantic_model.execute(
    query="SELECT * FROM DonorMetrics WHERE Year = @year AND Region = @region",
    parameters={"year": 2026, "region": "EMEA"}
)

# Execute and get as dataframe
import pandas as pd
df = semantic_model.execute_to_dataframe(
    query="SELECT * FROM DonorMetrics WHERE Year = 2026"
)

# Get metadata
metadata = semantic_model.get_metadata()

# List tables
tables = semantic_model.list_tables()

# Get table schema
schema = semantic_model.get_table_schema("DonorMetrics")
```

**Parameters:**
- `name` (str): Semantic model name
- `workspace` (str): Workspace name
- `model_id` (str): Model ID
- `classification` (str, optional): Data classification level
- `timeout` (int, optional): Query timeout in seconds
- `max_retries` (int, optional): Maximum number of retries

**Methods:**
- `execute(query, parameters=None)`: Execute a query
- `execute_to_dataframe(query, parameters=None)`: Execute query and return as dataframe
- `execute_to_json(query, parameters=None)`: Execute query and return as JSON
- `get_metadata()`: Get semantic model metadata
- `list_tables()`: List all tables in the model
- `get_table_schema(table_name)`: Get schema for a specific table
- `get_table_metadata(table_name)`: Get metadata for a specific table
- `refresh()`: Refresh the semantic model connection

#### `Warehouse`

Provides access to Fabric warehouses.

```python
from platform.fabric import Warehouse

# Create warehouse connector
warehouse = Warehouse(
    name="GoldLayer",
    workspace="DER-Data",
    warehouse_id="GoldLayer-Warehouse"
)

# Execute SQL query
result = warehouse.query(
    sql="SELECT * FROM dimDonor WHERE Status = 'Active'"
)

# Execute with parameters
result = warehouse.query(
    sql="SELECT * FROM dimDonor WHERE Year = @year",
    parameters={"year": 2026}
)

# Execute and fetch all results
all_results = warehouse.query_all(
    sql="SELECT * FROM dimDonor",
    batch_size=1000
)

# Execute and get as dataframe
import pandas as pd
df = warehouse.query_to_dataframe(
    sql="SELECT * FROM dimDonor WHERE Status = 'Active'"
)

# Get metadata
metadata = warehouse.get_metadata()

# List tables
tables = warehouse.list_tables()

# Get table schema
schema = warehouse.get_table_schema("dimDonor")

# Execute stored procedure
result = warehouse.execute_procedure(
    procedure="sp_GetDonorMetrics",
    parameters={"year": 2026}
)
```

**Parameters:**
- `name` (str): Warehouse name
- `workspace` (str): Workspace name
- `warehouse_id` (str): Warehouse ID
- `classification` (str, optional): Data classification level
- `timeout` (int, optional): Query timeout in seconds
- `max_retries` (int, optional): Maximum number of retries

**Methods:**
- `query(sql, parameters=None)`: Execute a SQL query
- `query_all(sql, batch_size=None)`: Execute query and fetch all results
- `query_to_dataframe(sql, parameters=None)`: Execute query and return as dataframe
- `query_to_json(sql, parameters=None)`: Execute query and return as JSON
- `execute_procedure(procedure, parameters=None)`: Execute a stored procedure
- `get_metadata()`: Get warehouse metadata
- `list_tables()`: List all tables in the warehouse
- `get_table_schema(table_name)`: Get schema for a specific table
- `list_procedures()`: List all stored procedures
- `begin_transaction()`: Begin a transaction
- `commit_transaction()`: Commit a transaction
- `rollback_transaction()`: Rollback a transaction

#### `Lakehouse`

Provides access to Fabric lakehouses.

```python
from platform.fabric import Lakehouse

# Create lakehouse connector
lakehouse = Lakehouse(
    name="Gold",
    workspace="DER-Data",
    lakehouse_id="Gold-Lakehouse"
)

# Read table
result = lakehouse.read_table("DonorData")

# Read with filters
result = lakehouse.read_table(
    "DonorData",
    filters=[
        {"column": "Status", "operator": "=", "value": "Active"},
        {"column": "Year", "operator": ">=", "value": 2024}
    ]
)

# Read with selection
result = lakehouse.read_table(
    "DonorData",
    select=["DonorID", "Name", "TotalDonations"],
    filters=[{"column": "Status", "operator": "=", "value": "Active"}]
)

# Write data
lakehouse.write_table("NewDonorData", data=dataframe)

# Write with options
lakehouse.write_table(
    "NewDonorData",
    data=dataframe,
    mode="append",  # or "overwrite", "ignore"
    partition_by=["Year", "Region"]
)

# Delete data
lakehouse.delete_table(
    "DonorData",
    filters=[{"column": "DonorID", "operator": "=", "value": "DON-12345"}]
)

# Update data
lakehouse.update_table(
    "DonorData",
    updates={"Status": "Inactive"},
    filters=[{"column": "DonorID", "operator": "=", "value": "DON-12345"}]
)

# List files
files = lakehouse.list_files("/data/donors")

# Read file
content = lakehouse.read_file("/data/donors/donor_list.csv")

# Write file
lakehouse.write_file("/data/donors/new_list.csv", content)
```

**Parameters:**
- `name` (str): Lakehouse name
- `workspace` (str): Workspace name
- `lakehouse_id` (str): Lakehouse ID
- `classification` (str, optional): Data classification level
- `timeout` (int, optional): Operation timeout in seconds
- `max_retries` (int, optional): Maximum number of retries

**Methods:**
- `read_table(table_name, select=None, filters=None, limit=None)`: Read a table
- `write_table(table_name, data, mode=None, partition_by=None)`: Write to a table
- `delete_table(table_name, filters=None)`: Delete from a table
- `update_table(table_name, updates, filters=None)`: Update a table
- `list_tables()`: List all tables
- `get_table_schema(table_name)`: Get table schema
- `list_files(path)`: List files in a path
- `read_file(path)`: Read a file
- `write_file(path, content)`: Write a file
- `delete_file(path)`: Delete a file
- `create_directory(path)`: Create a directory
- `delete_directory(path, recursive=False)`: Delete a directory
- `execute_spark(sql)`: Execute Spark SQL

#### `FabricClient`

Provides direct access to Fabric APIs.

```python
from platform.fabric import FabricClient

# Create Fabric client
client = FabricClient(
    endpoint="https://fabric.my-org.org",
    authentication_type="managed_identity"
)

# REST API calls
response = client.get("/api/v1/workspaces")
response = client.post("/api/v1/workspaces", json={"name": "NewWorkspace"})
response = client.put("/api/v1/workspaces/123", json={"name": "UpdatedWorkspace"})
response = client.delete("/api/v1/workspaces/123")

# GraphQL queries
result = client.graphql(
    query="""
    query {
        workspaces {
            name
            id
            description
        }
    }
    """
)

# GraphQL mutations
result = client.graphql(
    query="""
    mutation {
        createWorkspace(name: "NewWorkspace", description: "Test workspace") {
            id
            name
        }
    }
    """
)

# WebSocket connections
async with client.websocket("/realtime") as ws:
    await ws.send({"action": "subscribe", "topic": "data_updates"})
    async for message in ws:
        print(f"Received: {message}")
```

**Parameters:**
- `endpoint` (str): Fabric endpoint URL
- `authentication_type` (str): Authentication type ("managed_identity", "service_principal", "entra_id")
- `timeout` (int, optional): Request timeout in seconds
- `max_retries` (int, optional): Maximum number of retries

**Methods:**
- `get(path, **kwargs)`: HTTP GET request
- `post(path, json=None, **kwargs)`: HTTP POST request
- `put(path, json=None, **kwargs)`: HTTP PUT request
- `delete(path, **kwargs)`: HTTP DELETE request
- `patch(path, json=None, **kwargs)`: HTTP PATCH request
- `graphql(query, variables=None)`: Execute GraphQL query
- `websocket(path)`: Create WebSocket connection
- `upload_file(path, file_content)`: Upload a file
- `download_file(path)`: Download a file

## 📊 Query Results

### Semantic Model Query Result

```python
# Query result structure
result = {
    "columns": [
        {"name": "DonorCount", "type": "INT"},
        {"name": "TotalRevenue", "type": "DECIMAL"},
        {"name": "Year", "type": "INT"}
    ],
    "rows": [
        [1500, 15000000.00, 2026],
        [1200, 12000000.00, 2025],
        [1000, 10000000.00, 2024]
    ],
    "row_count": 3,
    "execution_time_ms": 450,
    "query_id": "query-20260501-103000-001",
    "cache_hit": False
}

# Access data
for row in result["rows"]:
    donor_count = row[0]
    total_revenue = row[1]
    year = row[2]
    print(f"{year}: {donor_count} donors, ${total_revenue:,.2f}")

# Convert to dataframe
import pandas as pd
df = pd.DataFrame(result["rows"], columns=[col["name"] for col in result["columns"]])
```

### Warehouse Query Result

```python
# Query result structure
result = {
    "columns": [
        {"name": "DonorID", "type": "VARCHAR"},
        {"name": "Name", "type": "VARCHAR"},
        {"name": "Status", "type": "VARCHAR"},
        {"name": "TotalDonations", "type": "DECIMAL"}
    ],
    "rows": [
        ["DON-12345", "John Doe", "Active", 50000.00],
        ["DON-12346", "Jane Smith", "Active", 75000.00],
        ["DON-12347", "Bob Johnson", "Inactive", 25000.00]
    ],
    "row_count": 3,
    "total_rows": 1500,
    "has_more": True,
    "continuation_token": "token-123",
    "execution_time_ms": 150,
    "query_id": "query-20260501-103000-002"
}

# Access data
for row in result["rows"]:
    donor_id = row[0]
    name = row[1]
    status = row[2]
    total_donations = row[3]
    print(f"{donor_id}: {name} ({status}) - ${total_donations:,.2f}")

# Get next page
next_result = warehouse.query(
    sql="SELECT * FROM dimDonor WHERE Status = 'Active'",
    continuation_token=result["continuation_token"]
)
```

## 📈 Monitoring and Metrics

### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Query Execution Time | Average query execution time | < 500ms | > 1000ms |
| Query Volume | Queries per minute | Varies | > 1000/min |
| Query Errors | Failed queries | 0 | > 10/hour |
| Connection Pool Usage | Connection pool utilization | < 80% | > 95% |
| Cache Hit Rate | Query cache hit rate | > 70% | < 50% |
| Data Volume | Data transferred per query | < 10MB | > 100MB |

### Fabric Queries

```kusto
// Get query execution statistics
FabricQueries
| where TimeGenerated > ago(1d)
| summarize 
    count() by bin(TimeGenerated, 1h), 
    semantic_model, 
    warehouse,
    lakehouse
| order by TimeGenerated asc

// Get slow queries
FabricQueries
| where TimeGenerated > ago(1d)
| where DurationMs > 1000
| project TimeGenerated, Query, DurationMs, semantic_model, warehouse, lakehouse
| order by DurationMs desc
| take 10

// Get query errors
FabricQueryErrors
| where TimeGenerated > ago(1d)
| summarize count() by ErrorType, semantic_model, warehouse, lakehouse
| order by count_ desc

// Get data volume by query
FabricQueries
| where TimeGenerated > ago(1d)
| summarize sum(DataVolumeBytes) by Query, semantic_model, warehouse
| order by sum_DataVolumeBytes desc
| take 10
```

## 🚀 Best Practices

### ⭐ Use Semantic Models over Direct Tables

Always prefer semantic models over direct table access.

```python
# Good - Using semantic model
semantic_model = get_semantic_model("DonorManagement")
result = semantic_model.execute(
    query="SELECT DonorCount, TotalRevenue FROM DonorMetrics WHERE Year = 2026"
)

# Bad - Direct table access
warehouse = get_warehouse("GoldLayer")
result = warehouse.query(
    sql="SELECT COUNT(*) as DonorCount, SUM(Amount) as TotalRevenue FROM factDonations WHERE Year = 2026"
)
```

### ⭐ Use Parameterized Queries

Always use parameterized queries to prevent SQL injection.

```python
# Good - Parameterized query
result = semantic_model.execute(
    query="SELECT * FROM DonorMetrics WHERE Year = @year AND Region = @region",
    parameters={"year": 2026, "region": "EMEA"}
)

# Bad - String concatenation
year = 2026
region = "EMEA"
result = semantic_model.execute(
    query=f"SELECT * FROM DonorMetrics WHERE Year = {year} AND Region = '{region}'"
)
```

### ⭐ Use Connection Pooling

Enable connection pooling for better performance.

```python
# Good - Connection pooling enabled
config = FabricConfig(
    connection_pooling={
        "enabled": True,
        "max_connections": 10,
        "connection_timeout": 30
    }
)

# Bad - No connection pooling
config = FabricConfig(
    connection_pooling={
        "enabled": False
    }
)
```

### ⭐ Use Query Caching

Enable query caching for frequently executed queries.

```python
# Good - Query caching enabled
config = FabricConfig(
    caching={
        "enabled": True,
        "ttl": 300,
        "max_size": 1000
    }
)

# Bad - No query caching
config = FabricConfig(
    caching={
        "enabled": False
    }
)
```

### ⭐ Handle Large Result Sets

Use pagination for large result sets.

```python
# Good - Pagination
all_results = []
continuation_token = None

while True:
    result = warehouse.query(
        sql="SELECT * FROM LargeTable",
        continuation_token=continuation_token,
        batch_size=1000
    )
    all_results.extend(result["rows"])
    
    if not result["has_more"]:
        break
    
    continuation_token = result["continuation_token"]

# Bad - No pagination
result = warehouse.query(
    sql="SELECT * FROM LargeTable"
)
# This could return too much data
```

### ⭐ Use Timeouts

Always set appropriate timeouts for queries.

```python
# Good - Appropriate timeout
semantic_model = SemanticModel(
    name="DonorManagement",
    timeout=60  # 60 seconds
)

# Bad - No timeout or too long
semantic_model = SemanticModel(
    name="DonorManagement",
    timeout=300  # 5 minutes - too long
)
```

### ⭐ Handle Query Errors

Handle query errors gracefully.

```python
# Good - Error handling
try:
    result = semantic_model.execute(
        query="SELECT * FROM DonorMetrics WHERE Year = 2026"
    )
except FabricQueryError as e:
    logger.error(f"Query failed: {e}")
    raise MCPError(
        error_code="FABRIC-001",
        category=ErrorCategory.INTEGRATION,
        message=f"Query execution failed: {str(e)}",
        details={"query": query, "error": str(e)}
    )

# Bad - No error handling
result = semantic_model.execute(
    query="SELECT * FROM DonorMetrics WHERE Year = 2026"
)
```

## 🔍 Troubleshooting

### Common Issues

#### Connection Failed

**Error:** `FabricConnectionError: Failed to connect to Fabric`

**Causes:**
- Incorrect endpoint URL
- Authentication issues
- Network connectivity problems
- Service unavailable

**Solutions:**
1. Check endpoint URL: `FABRIC_ENDPOINT`
2. Verify authentication configuration
3. Check network connectivity
4. Check Fabric service status

```python
# Debug connection
from platform.fabric import FabricClient

try:
    client = FabricClient()
    response = client.get("/api/v1/workspaces")
    print("Connection successful")
except Exception as e:
    print(f"Connection failed: {e}")
    print(f"Endpoint: {client.endpoint}")
    print(f"Authentication type: {client.authentication_type}")
```

#### Query Timeout

**Error:** `FabricQueryTimeoutError: Query execution timed out`

**Causes:**
- Query too complex
- Large result set
- Timeout too short
- Resource constraints

**Solutions:**
1. Optimize query
2. Increase timeout
3. Use pagination
4. Check resource usage

```python
# Debug query timeout
from platform.fabric import get_semantic_model

semantic_model = get_semantic_model("DonorManagement")

try:
    # Increase timeout
    semantic_model.timeout = 120
    
    result = semantic_model.execute(
        query="SELECT * FROM LargeDonorMetrics WHERE Year = 2026"
    )
except FabricQueryTimeoutError as e:
    print(f"Query timed out: {e}")
    print(f"Query: {e.query}")
    print(f"Timeout: {e.timeout} seconds")
```

#### Authentication Failed

**Error:** `FabricAuthenticationError: Authentication failed`

**Causes:**
- Invalid credentials
- Expired token
- Insufficient permissions
- Authentication type not supported

**Solutions:**
1. Check authentication configuration
2. Verify credentials
3. Check token expiration
4. Verify permissions

```python
# Debug authentication
from platform.fabric import FabricClient

try:
    client = FabricClient(
        authentication_type="managed_identity"
    )
    token = client.get_access_token()
    print(f"Authentication successful: {token[:20]}...")
except Exception as e:
    print(f"Authentication failed: {e}")
    print(f"Authentication type: {client.authentication_type}")
```

## 📚 Examples

### Complete Fabric Integration Example

```python
from platform.auth import authenticated_tool, requires_permission
from platform.fabric import get_semantic_model, get_warehouse, get_lakehouse
from platform.classification import classification, ClassificationLevel
from platform.audit import audit_log
from platform.telemetry import capture_tool_metrics

@authenticated_tool
@requires_permission("donor.analytics")
@classification(ClassificationLevel.CONFIDENTIAL)
@audit_log.sensitive_operation
@capture_tool_metrics
def get_donor_portfolio_health(year: int = 2026):
    """
    Get comprehensive donor portfolio health metrics.
    
    This tool retrieves health metrics from multiple Fabric data sources
    and combines them into a comprehensive portfolio health report.
    """
    
    # Get caller information
    caller = get_caller_identity()
    
    # Get semantic model for metrics
    metrics_model = get_semantic_model("DonorManagement")
    
    # Get donor count and total revenue
    metrics_result = metrics_model.execute(
        query="""
        SELECT 
            DonorCount,
            TotalRevenue,
            AverageDonation,
            DonorRetentionRate
        FROM DonorMetrics 
        WHERE Year = @year
        """,
        parameters={"year": year}
    )
    
    # Get warehouse for detailed analysis
    warehouse = get_warehouse("GoldLayer")
    
    # Get donor segmentation
    segmentation_result = warehouse.query(
        sql="""
        SELECT 
            DonorSegment,
            COUNT(*) as DonorCount,
            SUM(TotalDonations) as TotalRevenue
        FROM dimDonor
        WHERE Year = @year
        GROUP BY DonorSegment
        """,
        parameters={"year": year}
    )
    
    # Get lakehouse for raw data access
    lakehouse = get_lakehouse("Gold")
    
    # Get recent donations
    donations_result = lakehouse.read_table(
        "factDonations",
        select=["DonorID", "Amount", "Date"],
        filters=[
            {"column": "Year", "operator": "=", "value": year},
            {"column": "Date", "operator": ">=", "value": f"{year}-01-01"}
        ],
        limit=1000
    )
    
    # Combine results
    report = {
        "year": year,
        "summary": {
            "donor_count": metrics_result["rows"][0][0],
            "total_revenue": metrics_result["rows"][0][1],
            "average_donation": metrics_result["rows"][0][2],
            "retention_rate": metrics_result["rows"][0][3]
        },
        "segmentation": [
            {
                "segment": row[0],
                "donor_count": row[1],
                "total_revenue": row[2]
            }
            for row in segmentation_result["rows"]
        ],
        "recent_donations": [
            {
                "donor_id": row[0],
                "amount": row[1],
                "date": row[2]
            }
            for row in donations_result["rows"]
        ]
    }
    
    # Log access
    await audit_logger.log_data_access(
        user=caller.identity,
        resource="donor:portfolio:health",
        action="read",
        classification="CONFIDENTIAL",
        metadata={"year": year}
    )
    
    return report
```

### Semantic Model Query with Parameters

```python
from platform.auth import authenticated_tool
from platform.fabric import get_semantic_model
from platform.registration import tool

@authenticated_tool
@tool(
    name="GetDonorMetrics",
    description="Get donor metrics for a specific period and region",
    classification="CONFIDENTIAL"
)
def get_donor_metrics(year: int, region: str = None):
    """
    Get donor metrics for a specific period and region.
    
    Args:
        year: The year to get metrics for
        region: Optional region filter
    
    Returns:
        Dictionary containing donor metrics
    """
    
    # Get semantic model
    semantic_model = get_semantic_model("DonorManagement")
    
    # Build query
    query = """
    SELECT 
        DonorCount,
        TotalRevenue,
        AverageDonation,
        NewDonors,
        LostDonors,
        RetentionRate
    FROM DonorMetrics 
    WHERE Year = @year
    """
    
    # Add region filter if provided
    params = {"year": year}
    if region:
        query += " AND Region = @region"
        params["region"] = region
    
    # Execute query
    result = semantic_model.execute(query, parameters=params)
    
    # Format results
    if result["rows"]:
        row = result["rows"][0]
        return {
            "year": year,
            "region": region or "All",
            "donor_count": row[0],
            "total_revenue": row[1],
            "average_donation": row[2],
            "new_donors": row[3],
            "lost_donors": row[4],
            "retention_rate": row[5]
        }
    else:
        return {
            "year": year,
            "region": region or "All",
            "error": "No data found"
        }
```

### Warehouse Query with Transactions

```python
from platform.auth import authenticated_tool
from platform.fabric import get_warehouse
from platform.registration import tool

@authenticated_tool
@tool(
    name="UpdateDonorStatus",
    description="Update donor status in bulk",
    classification="CONFIDENTIAL"
)
def update_donor_status(donor_updates: list):
    """
    Update donor status in bulk using transactions.
    
    Args:
        donor_updates: List of donor updates, each with donor_id and new_status
    
    Returns:
        Dictionary with update results
    """
    
    # Get warehouse
    warehouse = get_warehouse("GoldLayer")
    
    # Begin transaction
    warehouse.begin_transaction()
    
    try:
        # Update each donor
        updated_count = 0
        failed_count = 0
        
        for update in donor_updates:
            donor_id = update["donor_id"]
            new_status = update["new_status"]
            
            try:
                warehouse.query(
                    sql="""
                    UPDATE dimDonor 
                    SET Status = @status, 
                        LastUpdated = GETDATE(),
                        UpdatedBy = @updated_by
                    WHERE DonorID = @donor_id
                    """,
                    parameters={
                        "status": new_status,
                        "updated_by": "system",
                        "donor_id": donor_id
                    }
                )
                updated_count += 1
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to update donor {donor_id}: {e}")
        
        # Commit transaction
        warehouse.commit_transaction()
        
        return {
            "status": "success",
            "updated_count": updated_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        # Rollback transaction on error
        warehouse.rollback_transaction()
        raise MCPError(
            error_code="FABRIC-002",
            category=ErrorCategory.INTEGRATION,
            message=f"Bulk update failed: {str(e)}",
            details={"error": str(e)}
        )
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `FabricError` | Base Fabric error | FABRIC-001 |
| `FabricConnectionError` | Connection error | FABRIC-002 |
| `FabricAuthenticationError` | Authentication error | FABRIC-003 |
| `FabricQueryError` | Query execution error | FABRIC-004 |
| `FabricQueryTimeoutError` | Query timeout error | FABRIC-005 |
| `FabricResourceNotFoundError` | Resource not found | FABRIC-006 |

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| FABRIC-001 | Fabric error | 500 |
| FABRIC-002 | Connection error | 503 |
| FABRIC-003 | Authentication error | 401 |
| FABRIC-004 | Query error | 400 |
| FABRIC-005 | Query timeout | 408 |
| FABRIC-006 | Resource not found | 404 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*