# 🔗 Connectivity API Reference

The Connectivity API provides standardized access to Microsoft Fabric services, enabling seamless integration with semantic models, warehouses, lakehouses, and other Fabric endpoints.

## 🎯 Overview

The Connectivity API handles:

- **Semantic Model Access**: Standardized access to Power BI semantic models
- **Warehouse Connectivity**: SQL query execution against Fabric warehouses
- **Lakehouse Integration**: Data analysis with SQL and Spark support
- **Unified Interface**: Single interface for all Fabric services
- **Connection Pooling**: Efficient connection management
- **Query Optimization**: Intelligent query routing and caching

## 🏗️ Core Classes

### FabricClient

Main client for Microsoft Fabric connectivity.

**Class Signature:**
```python
class FabricClient:
    def __init__(
        self,
        config: Optional[FabricConfig] = None,
        auth_service: Optional[AuthenticationService] = None
    ):
        """
        Initialize the Fabric Client.
        
        Args:
            config: Fabric configuration
            auth_service: Authentication service for token management
        """
```

**Methods:**

#### `get_semantic_model()`
Get a semantic model client for a specific model.

```python
def get_semantic_model(
    self,
    model_name: str,
    workspace_id: Optional[str] = None
) -> SemanticModelClient:
    """
    Get a semantic model client for a specific model.
    
    Args:
        model_name: Name of the semantic model
        workspace_id: Optional workspace ID (defaults to configured workspace)
        
    Returns:
        SemanticModelClient for the specified model
    """
```

**Example:**
```python
from platform.connectivity import FabricClient

fabric = FabricClient()

# Get semantic model client
semantic_model = fabric.get_semantic_model("DonorAnalytics")

# Execute query
results = semantic_model.execute("EVALUATE DonorPortfolio")
```

#### `get_warehouse()`
Get a warehouse client for a specific warehouse.

```python
def get_warehouse(
    self,
    warehouse_name: str,
    workspace_id: Optional[str] = None
) -> WarehouseClient:
    """
    Get a warehouse client for a specific warehouse.
    
    Args:
        warehouse_name: Name of the warehouse
        workspace_id: Optional workspace ID (defaults to configured workspace)
        
    Returns:
        WarehouseClient for the specified warehouse
    """
```

**Example:**
```python
from platform.connectivity import FabricClient

fabric = FabricClient()

# Get warehouse client
warehouse = fabric.get_warehouse("DonorDataWarehouse")

# Execute SQL query
results = warehouse.execute_sql("SELECT * FROM donors WHERE status = 'active'")
```

#### `get_lakehouse()`
Get a lakehouse client for a specific lakehouse.

```python
def get_lakehouse(
    self,
    lakehouse_name: str,
    workspace_id: Optional[str] = None
) -> LakehouseClient:
    """
    Get a lakehouse client for a specific lakehouse.
    
    Args:
        lakehouse_name: Name of the lakehouse
        workspace_id: Optional workspace ID (defaults to configured workspace)
        
    Returns:
        LakehouseClient for the specified lakehouse
    """
```

**Example:**
```python
from platform.connectivity import FabricClient

fabric = FabricClient()

# Get lakehouse client
lakehouse = fabric.get_lakehouse("DonorDataLakehouse")

# Execute SQL query
results = lakehouse.execute_sql("SELECT * FROM donor_transactions")

# Execute Spark query
spark_results = lakehouse.execute_spark("SELECT * FROM donor_transactions")
```

#### `execute_query()`
Execute a query against any Fabric endpoint.

```python
async def execute_query(
    self,
    query: str,
    endpoint_type: str = "semantic_model",
    endpoint_name: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> QueryResult:
    """
    Execute a query against any Fabric endpoint.
    
    Args:
        query: Query to execute
        endpoint_type: Type of endpoint (semantic_model, warehouse, lakehouse)
        endpoint_name: Name of the endpoint
        parameters: Query parameters
        
    Returns:
        QueryResult with query results
    """
```

**Example:**
```python
from platform.connectivity import FabricClient

fabric = FabricClient()

# Execute query against semantic model
results = await fabric.execute_query(
    query="EVALUATE DonorPortfolio",
    endpoint_type="semantic_model",
    endpoint_name="DonorAnalytics"
)
```

### SemanticModelClient

Client for interacting with Power BI semantic models.

**Class Signature:**
```python
class SemanticModelClient:
    def __init__(
        self,
        model_name: str,
        workspace_id: str,
        fabric_client: FabricClient
    ):
        """
        Initialize the Semantic Model Client.
        
        Args:
            model_name: Name of the semantic model
            workspace_id: Workspace ID
            fabric_client: Parent Fabric client
        """
```

**Methods:**

#### `execute()`
Execute a DAX query against the semantic model.

```python
async def execute(
    self,
    query: str,
    parameters: Optional[Dict[str, Any]] = None
) -> SemanticModelResult:
    """
    Execute a DAX query against the semantic model.
    
    Args:
        query: DAX query to execute
        parameters: Query parameters
        
    Returns:
        SemanticModelResult with query results
    """
```

**Example:**
```python
from platform.connectivity import FabricClient

fabric = FabricClient()
semantic_model = fabric.get_semantic_model("DonorAnalytics")

# Execute DAX query
results = await semantic_model.execute(
    "EVALUATE FILTER(Donors, Donors[Status] = \"Active\")"
)

# Access results
for row in results.rows:
    print(f"Donor: {row['DonorName']}, Contribution: {row['TotalContribution']}")
```

#### `get_metadata()`
Get metadata about the semantic model.

```python
async def get_metadata(self) -> SemanticModelMetadata:
    """
    Get metadata about the semantic model.
    
    Returns:
        SemanticModelMetadata with model structure and information
    """
```

**Example:**
```python
from platform.connectivity import FabricClient

fabric = FabricClient()
semantic_model = fabric.get_semantic_model("DonorAnalytics")

# Get model metadata
metadata = await semantic_model.get_metadata()

print(f"Model: {metadata.name}")
print(f"Tables: {list(metadata.tables.keys())}")
print(f"Measures: {list(metadata.measures.keys())}")
```

### WarehouseClient

Client for interacting with Fabric warehouses.

**Class Signature:**
```python
class WarehouseClient:
    def __init__(
        self,
        warehouse_name: str,
        workspace_id: str,
        fabric_client: FabricClient
    ):
        """
        Initialize the Warehouse Client.
        
        Args:
            warehouse_name: Name of the warehouse
            workspace_id: Workspace ID
            fabric_client: Parent Fabric client
        """
```

**Methods:**

#### `execute_sql()`
Execute a SQL query against the warehouse.

```python
async def execute_sql(
    self,
    query: str,
    parameters: Optional[Dict[str, Any]] = None
) -> SQLResult:
    """
    Execute a SQL query against the warehouse.
    
    Args:
        query: SQL query to execute
        parameters: Query parameters
        
    Returns:
        SQLResult with query results
    """
```

**Example:**
```python
from platform.connectivity import FabricClient

fabric = FabricClient()
warehouse = fabric.get_warehouse("DonorDataWarehouse")

# Execute SQL query
results = await warehouse.execute_sql("""
    SELECT 
        d.donor_id,
        d.name,
        SUM(t.amount) as total_contribution
    FROM donors d
    JOIN transactions t ON d.donor_id = t.donor_id
    WHERE d.status = 'active'
    GROUP BY d.donor_id, d.name
    ORDER BY total_contribution DESC
    LIMIT 100
""")

# Access results
for row in results.rows:
    print(f"{row['name']}: ${row['total_contribution']}")
```

### LakehouseClient

Client for interacting with Fabric lakehouses.

**Class Signature:**
```python
class LakehouseClient:
    def __init__(
        self,
        lakehouse_name: str,
        workspace_id: str,
        fabric_client: FabricClient
    ):
        """
        Initialize the Lakehouse Client.
        
        Args:
            lakehouse_name: Name of the lakehouse
            workspace_id: Workspace ID
            fabric_client: Parent Fabric client
        """
```

**Methods:**

#### `execute_sql()`
Execute a SQL query against the lakehouse.

```python
async def execute_sql(
    self,
    query: str,
    parameters: Optional[Dict[str, Any]] = None
) -> SQLResult:
    """
    Execute a SQL query against the lakehouse.
    
    Args:
        query: SQL query to execute
        parameters: Query parameters
        
    Returns:
        SQLResult with query results
    """
```

#### `execute_spark()`
Execute a Spark query against the lakehouse.

```python
async def execute_spark(
    self,
    query: str,
    language: str = "sql",
    parameters: Optional[Dict[str, Any]] = None
) -> SparkResult:
    """
    Execute a Spark query against the lakehouse.
    
    Args:
        query: Spark query to execute
        language: Query language (sql, pyspark, sparksql)
        parameters: Query parameters
        
    Returns:
        SparkResult with query results
    """
```

**Example:**
```python
from platform.connectivity import FabricClient

fabric = FabricClient()
lakehouse = fabric.get_lakehouse("DonorDataLakehouse")

# Execute SQL query
sql_results = await lakehouse.execute_sql("SELECT * FROM donor_transactions")

# Execute PySpark query
pyspark_results = await lakehouse.execute_spark("""
df = spark.table("donor_transactions")
df.filter(df.status == "completed").groupBy("donor_id").sum("amount").show()
""", language="pyspark")
```

### FabricConfig

Configuration for Fabric connectivity.

```python
@dataclass
class FabricConfig:
    # Workspace Configuration
    default_workspace: Optional[str] = None
    workspace_ids: Dict[str, str] = field(default_factory=dict)
    
    # Endpoint Configuration
    semantic_model_endpoint: Optional[str] = None
    warehouse_endpoint: Optional[str] = None
    lakehouse_endpoint: Optional[str] = None
    
    # Connection Configuration
    connection_timeout: int = 30
    query_timeout: int = 300
    max_connections: int = 10
    connection_pooling: bool = True
    
    # Query Configuration
    max_rows: int = 10000
    batch_size: int = 1000
    
    # Caching Configuration
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    cache_max_size: int = 1000
    
    # Retry Configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
```

## 🎪 Decorators

### `@fabric_query`
Decorator to automatically handle Fabric queries with error handling and telemetry.

```python
def fabric_query(
    endpoint_type: str = "semantic_model",
    endpoint_name: Optional[str] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None
) -> Callable:
    """
    Decorator to automatically handle Fabric queries.
    
    Args:
        endpoint_type: Type of Fabric endpoint
        endpoint_name: Name of the endpoint
        timeout: Query timeout in seconds
        max_retries: Maximum number of retries
        
    Returns:
        Decorated function
    """
```

**Example:**
```python
from platform.connectivity import fabric_query

@fabric_query(endpoint_type="semantic_model", endpoint_name="DonorAnalytics")
async def get_donor_portfolio():
    # Query is automatically executed against the specified endpoint
    return "EVALUATE DonorPortfolio"

# Usage
results = await get_donor_portfolio()
```

## 🔧 Configuration

### Environment Variables

```bash
# Fabric Configuration
FABRIC_DEFAULT_WORKSPACE=your-workspace-id
FABRIC_SEMANTIC_MODEL_ENDPOINT=https://api.fabric.microsoft.com/v1/semanticModels
FABRIC_WAREHOUSE_ENDPOINT=https://api.fabric.microsoft.com/v1/warehouses
FABRIC_LAKEHOUSE_ENDPOINT=https://api.fabric.microsoft.com/v1/lakehouses

# Connection Configuration
FABRIC_CONNECTION_TIMEOUT=30
FABRIC_QUERY_TIMEOUT=300
FABRIC_MAX_CONNECTIONS=10

# Caching Configuration
FABRIC_CACHE_ENABLED=true
FABRIC_CACHE_TTL=300
FABRIC_CACHE_MAX_SIZE=1000
```

### Configuration File

```yaml
# config/fabric.yaml
fabric:
  default_workspace: your-workspace-id
  workspace_ids:
    production: prod-workspace-id
    development: dev-workspace-id
  
  endpoints:
    semantic_model: https://api.fabric.microsoft.com/v1/semanticModels
    warehouse: https://api.fabric.microsoft.com/v1/warehouses
    lakehouse: https://api.fabric.microsoft.com/v1/lakehouses
  
  connection:
    timeout: 30
    query_timeout: 300
    max_connections: 10
    pooling: true
  
  query:
    max_rows: 10000
    batch_size: 1000
  
  cache:
    enabled: true
    ttl: 300
    max_size: 1000
  
  retry:
    max_retries: 3
    delay: 1.0
    backoff: 2.0
```

## 🚀 Quick Start

### Basic Fabric Connectivity

```python
from platform.connectivity import FabricClient

# Initialize Fabric client
fabric = FabricClient()

# Get semantic model
semantic_model = fabric.get_semantic_model("DonorAnalytics")

# Execute DAX query
results = await semantic_model.execute("EVALUATE DonorPortfolio")

# Access results
for row in results.rows:
    print(row)
```

### Warehouse Operations

```python
from platform.connectivity import FabricClient

# Initialize Fabric client
fabric = FabricClient()

# Get warehouse
warehouse = fabric.get_warehouse("DonorDataWarehouse")

# Execute SQL query
results = await warehouse.execute_sql("""
    SELECT donor_id, name, total_contribution
    FROM donors
    WHERE status = 'active'
    ORDER BY total_contribution DESC
    LIMIT 10
""")

# Process results
active_donors = [dict(row) for row in results.rows]
```

### Lakehouse Operations

```python
from platform.connectivity import FabricClient

# Initialize Fabric client
fabric = FabricClient()

# Get lakehouse
lakehouse = fabric.get_lakehouse("DonorDataLakehouse")

# Execute SQL query
sql_results = await lakehouse.execute_sql("SELECT * FROM donor_transactions")

# Execute Spark query
spark_results = await lakehouse.execute_spark("""
    SELECT donor_id, COUNT(*) as transaction_count, SUM(amount) as total_amount
    FROM donor_transactions
    GROUP BY donor_id
    ORDER BY total_amount DESC
""")
```

### Using Decorators

```python
from platform.connectivity import fabric_query

# Semantic model query
@fabric_query(endpoint_type="semantic_model", endpoint_name="DonorAnalytics")
async def get_top_donors():
    return "EVALUATE TOPN(10, Donors, Donors[TotalContribution], DESC)"

# Warehouse query
@fabric_query(endpoint_type="warehouse", endpoint_name="DonorDataWarehouse")
async def get_donor_summary(donor_id: str):
    return f"SELECT * FROM donors WHERE donor_id = '{donor_id}'"

# Usage
results = await get_top_donors()
```

## ⭐ Best Practices

### Query Design

✅ **Use Semantic Models for Business Metrics**
```python
# Good: Use semantic models for business metrics
@fabric_query(endpoint_type="semantic_model", endpoint_name="DonorAnalytics")
async def get_donor_portfolio_health():
    return "EVALUATE DonorPortfolioHealth"
```

❌ **Avoid Direct Table Access**
```python
# Bad: Direct table access instead of semantic models
@fabric_query(endpoint_type="warehouse", endpoint_name="DonorDataWarehouse")
async def get_donor_metrics():
    return "SELECT * FROM gold_donor_metrics"  # Should use semantic model
```

### Performance Optimization

✅ **Use Appropriate Query Types**
```python
# Good: Use the right endpoint for the job
# Semantic models for business metrics
semantic_model.execute("EVALUATE RevenueForecast")

# Warehouses for SQL queries
warehouse.execute_sql("SELECT * FROM transactions WHERE date > '2024-01-01'")

# Lakehouses for big data processing
lakehouse.execute_spark("SELECT * FROM large_dataset")
```

✅ **Enable Caching for Frequent Queries**
```python
# Good: Enable caching for frequently accessed data
config = FabricConfig(
    cache_enabled=True,
    cache_ttl=300,  # 5 minutes
    cache_max_size=1000
)
```

### Error Handling

✅ **Handle Query Errors Gracefully**
```python
from platform.connectivity import FabricError

try:
    results = await semantic_model.execute("EVALUATE DonorPortfolio")
except FabricError as e:
    if e.error_code == "QUERY_TIMEOUT":
        # Handle timeout
        logger.warning(f"Query timeout: {e.message}")
        return cached_results
    elif e.error_code == "SYNTAX_ERROR":
        # Handle syntax error
        logger.error(f"Query syntax error: {e.message}")
        raise
    else:
        # Handle other errors
        logger.error(f"Fabric error: {e}")
        raise
```

### Connection Management

✅ **Use Connection Pooling**
```python
# Good: Enable connection pooling for better performance
config = FabricConfig(
    connection_pooling=True,
    max_connections=10
)
```

✅ **Set Appropriate Timeouts**
```python
# Good: Set timeouts based on query complexity
config = FabricConfig(
    connection_timeout=30,    # Connection timeout
    query_timeout=300        # Query timeout for complex queries
)
```

## 🔍 Troubleshooting

### Common Issues

**Connection failures**
- Verify that the workspace ID is correct
- Check that the Fabric endpoints are accessible
- Ensure authentication is properly configured

**Query timeouts**
- Increase query timeout for complex queries
- Optimize query performance
- Consider breaking large queries into smaller ones

**Permission errors**
- Verify that the service principal has access to the workspace
- Check that the required permissions are granted
- Ensure the Managed Identity has the correct roles

**Caching not working**
- Verify that caching is enabled in configuration
- Check that cache TTL is appropriate
- Ensure cache size is sufficient

**High latency**
- Review connection pooling configuration
- Check for network issues
- Consider using closer Azure regions

## 📚 Related Documentation

- [Platform API](platform.md) - Core framework classes
- [Fabric Connectivity Module](../modules/fabric-connectivity.md) - Module overview
- [Performance Best Practices](../best-practices/performance.md) - Performance optimization
- [Data Access Best Practices](../best-practices/) - Data access guidelines

---

**🎉 Ready to connect to Fabric?** Start with the `FabricClient` for unified access to all Fabric services.

**Need more details?** Check the [Fabric Connectivity Module](../modules/fabric-connectivity.md) for comprehensive module documentation.