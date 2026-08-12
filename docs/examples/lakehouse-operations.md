# 🏞️ Lakehouse Operations Guide

## Overview

This guide demonstrates how to work with **Microsoft Fabric Lakehouses** using the MCP Platform Framework. Lakehouses combine the best features of data lakes and data warehouses, providing a unified platform for data storage, analytics, and machine learning.

## 🎯 Key Concepts

### What are Fabric Lakehouses?

Fabric Lakehouses are:
- **Unified platforms** combining data lake and warehouse capabilities
- **Open format** based on Delta Lake and Parquet
- **ACID compliant** for reliable transactions
- **Scalable** for petabyte-scale data
- **Multi-language** supporting SQL, Spark, and Python

### Lakehouse Architecture

```
Lakehouse
├── Tables (Delta format)
│   ├── Files (Parquet)
│   └── Metadata
├── SQL Endpoint
├── Spark Compute
└── Integration with OneLake
```

### When to Use Lakehouses

| Use Case | Lakehouse | Warehouse | Semantic Model |
|----------|-----------|-----------|-----------------|
| **Data Ingestion** | ✅ Best | ❌ Limited | ❌ No |
| **Big Data Processing** | ✅ Best | ⚠️ Limited | ❌ No |
| **ETL/ELT** | ✅ Best | ⚠️ Good | ❌ No |
| **SQL Analytics** | ✅ Good | ✅ Best | ⚠️ Good |
| **Business Reporting** | ⚠️ Good | ✅ Good | ✅ Best |
| **Machine Learning** | ✅ Best | ❌ Limited | ❌ No |

## 🏗️ Setup

### Prerequisites

1. **Microsoft Fabric Workspace** with lakehouses deployed
2. **Service Principal** with access to Fabric
3. **MCP Platform Framework** installed
4. **Required Permissions**: Contributor or Admin on the lakehouse

### Configuration

**config/development.json**
```json
{
  "fabric": {
    "tenant_id": "your-fabric-tenant-id",
    "workspace_id": "your-workspace-id",
    "lakehouses": {
      "DataLakehouse": {
        "lakehouse_id": "DataLakehouse",
        "classification": "CONFIDENTIAL"
      },
      "AnalyticsLakehouse": {
        "lakehouse_id": "AnalyticsLakehouse",
        "classification": "INTERNAL"
      }
    }
  }
}
```

### Environment Variables

```bash
# Required environment variables
export FABRIC_TENANT_ID=your-tenant-id
export FABRIC_WORKSPACE_ID=your-workspace-id
export AZURE_SUBSCRIPTION_ID=your-subscription-id
```

## 🔧 Lakehouse Client

### Basic Usage

```python
from mcp_framework.fabric import LakehouseClient

# Initialize the client
client = LakehouseClient(
    tenant_id="your-tenant-id",
    workspace_id="your-workspace-id",
    lakehouse_id="DataLakehouse"
)

# Or use framework configuration
from mcp_framework.platform import MCPFramework

framework = MCPFramework()
client = LakehouseClient(
    workspace_id=framework.config.get("fabric.workspace_id"),
    lakehouse_id="DataLakehouse"
)
```

### Client Configuration

```python
# Configure client with additional options
client = LakehouseClient(
    tenant_id="your-tenant-id",
    workspace_id="your-workspace-id",
    lakehouse_id="DataLakehouse",
    timeout=30,  # Request timeout in seconds
    retry_count=3,  # Number of retries for failed requests
    spark_pool_size=5,  # Spark connection pool size
    temp_dir="/temp"  # Temporary directory for operations
)
```

## 📊 Lakehouse Operations

### Table Operations

#### List Tables

```python
# List all tables in the lakehouse
tables = client.list_tables()

for table in tables:
    print(f"Table: {table['name']}")
    print(f"  Type: {table['type']}")
    print(f"  Created: {table['created']}")
    print(f"  Size: {table['size']}")
```

#### Get Table Schema

```python
# Get schema for a specific table
schema = client.get_table_schema("DonorTable")

print(f"Table: {schema['name']}")
print(f"Columns:")
for column in schema['columns']:
    print(f"  {column['name']}: {column['type']}")
```

#### Create Table

```python
# Create a new table
schema = {
    "columns": [
        {"name": "DonorID", "type": "STRING", "nullable": False},
        {"name": "DonorName", "type": "STRING"},
        {"name": "Organization", "type": "STRING"},
        {"name": "Email", "type": "STRING"},
        {"name": "TotalContributions", "type": "DOUBLE"},
        {"name": "FirstContributionDate", "type": "DATE"},
        {"name": "LastContributionDate", "type": "DATE"}
    ],
    "primary_key": ["DonorID"]
}

client.create_table("NewDonorTable", schema)
```

#### Delete Table

```python
# Delete a table
client.delete_table("OldDonorTable")
```

### Data Operations

#### Query Data (SQL)

```python
# Execute SQL query on lakehouse
query = """
SELECT 
    DonorID,
    DonorName,
    Organization,
    TotalContributions
FROM DonorTable
WHERE TotalContributions > 10000
ORDER BY TotalContributions DESC
LIMIT 100
"""

result = client.execute_sql(query)

for row in result:
    print(row)
```

#### Query Data (Spark)

```python
# Execute Spark query
from pyspark.sql import functions as F

# Get Spark session
spark = client.get_spark_session()

# Read table
df = spark.table("DonorTable")

# Filter and aggregate
result = df.filter(F.col("TotalContributions") > 10000) \
    .groupBy("Organization") \
    .agg(
        F.sum("TotalContributions").alias("TotalAmount"),
        F.count("*").alias("DonorCount"),
        F.avg("TotalContributions").alias("AverageAmount")
    ) \
    .orderBy(F.desc("TotalAmount")) \
    .collect()

for row in result:
    print(row)
```

#### Insert Data

```python
# Insert data using SQL
insert_query = """
INSERT INTO DonorTable 
(DonorID, DonorName, Organization, Email, TotalContributions)
VALUES (%s, %s, %s, %s, %s)
"""

client.execute_sql(insert_query, params=(
    "D999", "New Donor", "New Org", "new@donor.com", 5000.00
))
```

#### Bulk Insert

```python
# Bulk insert data
data = [
    ("D001", "Donor 1", "Org 1", "donor1@org1.com", 10000.00),
    ("D002", "Donor 2", "Org 2", "donor2@org2.com", 20000.00),
    ("D003", "Donor 3", "Org 3", "donor3@org3.com", 30000.00)
]

insert_query = """
INSERT INTO DonorTable 
(DonorID, DonorName, Organization, Email, TotalContributions)
VALUES (%s, %s, %s, %s, %s)
"""

client.execute_batch(insert_query, params_list=data)
```

#### Update Data

```python
# Update data
update_query = """
UPDATE DonorTable 
SET TotalContributions = TotalContributions + %s
WHERE DonorID = %s
"""

client.execute_sql(update_query, params=(1000.00, "D001"))
```

#### Delete Data

```python
# Delete data
delete_query = """
DELETE FROM DonorTable 
WHERE DonorID = %s
"""

client.execute_sql(delete_query, params=("D999",))
```

### File Operations

#### List Files

```python
# List files in the lakehouse
files = client.list_files("/path/to/directory")

for file in files:
    print(f"File: {file['name']}")
    print(f"  Path: {file['path']}")
    print(f"  Size: {file['size']}")
    print(f"  Type: {file['type']}")
```

#### Upload File

```python
# Upload a local file to the lakehouse
client.upload_file(
    local_path="/local/path/data.csv",
    lakehouse_path="/data/uploads/data.csv",
    overwrite=True
)
```

#### Download File

```python
# Download a file from the lakehouse
client.download_file(
    lakehouse_path="/data/uploads/data.csv",
    local_path="/local/path/data.csv"
)
```

#### Delete File

```python
# Delete a file
client.delete_file("/data/uploads/old-data.csv")
```

### Data Ingestion

#### Ingest from CSV

```python
# Ingest data from CSV file
client.ingest_csv(
    source_path="/data/uploads/donors.csv",
    table_name="DonorTable",
    options={
        "header": "true",
        "inferSchema": "true",
        "delimiter": ","
    }
)
```

#### Ingest from JSON

```python
# Ingest data from JSON file
client.ingest_json(
    source_path="/data/uploads/donors.json",
    table_name="DonorTable",
    options={
        "multiLine": "true",
        "mode": "APPEND"
    }
)
```

#### Ingest from Parquet

```python
# Ingest data from Parquet file
client.ingest_parquet(
    source_path="/data/uploads/donors.parquet",
    table_name="DonorTable"
)
```

### Data Export

#### Export to CSV

```python
# Export table to CSV
client.export_to_csv(
    table_name="DonorTable",
    output_path="/data/exports/donors.csv",
    options={
        "header": "true",
        "delimiter": ","
    }
)
```

#### Export to Parquet

```python
# Export table to Parquet
client.export_to_parquet(
    table_name="DonorTable",
    output_path="/data/exports/donors.parquet"
)
```

## 🎯 Common Operation Patterns

### Donor Data Management

#### Load Donor Data

```python
def load_donor_data(file_path: str, table_name: str = "DonorTable") -> dict:
    """Load donor data from CSV file into lakehouse"""
    try:
        # Upload file
        client.upload_file(
            local_path=file_path,
            lakehouse_path=f"/data/uploads/{os.path.basename(file_path)}",
            overwrite=True
        )
        
        # Ingest data
        lakehouse_path = f"/data/uploads/{os.path.basename(file_path)}"
        client.ingest_csv(
            source_path=lakehouse_path,
            table_name=table_name,
            options={
                "header": "true",
                "inferSchema": "true",
                "delimiter": ","
            }
        )
        
        # Clean up uploaded file
        client.delete_file(lakehouse_path)
        
        return {"status": "success", "message": "Data loaded successfully"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

#### Get Donor Statistics

```python
def get_donor_statistics() -> dict:
    """Calculate statistics for donor data"""
    query = """
    SELECT 
        COUNT(*) as TotalDonors,
        SUM(TotalContributions) as TotalContributions,
        AVG(TotalContributions) as AverageContributions,
        MAX(TotalContributions) as MaxContributions,
        MIN(TotalContributions) as MinContributions,
        COUNT(DISTINCT Organization) as UniqueOrganizations
    FROM DonorTable
    """
    
    result = client.execute_sql(query)
    return result[0] if result else {}
```

#### Get Donor Distribution

```python
def get_donor_distribution() -> list:
    """Get distribution of donors by organization"""
    query = """
    SELECT 
        Organization,
        COUNT(*) as DonorCount,
        SUM(TotalContributions) as TotalContributions,
        AVG(TotalContributions) as AverageContributions
    FROM DonorTable
    GROUP BY Organization
    ORDER BY TotalContributions DESC
    """
    
    return client.execute_sql(query)
```

### Contribution Data Management

#### Load Contribution Data

```python
def load_contribution_data(file_path: str, table_name: str = "ContributionTable") -> dict:
    """Load contribution data from CSV file"""
    try:
        # Upload file
        client.upload_file(
            local_path=file_path,
            lakehouse_path=f"/data/uploads/{os.path.basename(file_path)}",
            overwrite=True
        )
        
        # Ingest data
        lakehouse_path = f"/data/uploads/{os.path.basename(file_path)}"
        client.ingest_csv(
            source_path=lakehouse_path,
            table_name=table_name,
            options={
                "header": "true",
                "inferSchema": "true",
                "delimiter": ","
            }
        )
        
        # Clean up
        client.delete_file(lakehouse_path)
        
        return {"status": "success", "message": "Contribution data loaded"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

#### Get Contribution Trends

```python
def get_contribution_trends(start_date: str = None, end_date: str = None) -> list:
    """Get contribution trends over time"""
    date_filter = ""
    params = []
    
    if start_date and end_date:
        date_filter = "WHERE ContributionDate BETWEEN %s AND %s"
        params = [start_date, end_date]
    elif start_date:
        date_filter = "WHERE ContributionDate >= %s"
        params = [start_date]
    elif end_date:
        date_filter = "WHERE ContributionDate <= %s"
        params = [end_date]
    
    query = f"""
    SELECT 
        DATE_TRUNC('month', ContributionDate) as Month,
        SUM(Amount) as TotalAmount,
        COUNT(*) as ContributionCount,
        AVG(Amount) as AverageAmount
    FROM ContributionTable
    {date_filter}
    GROUP BY DATE_TRUNC('month', ContributionDate)
    ORDER BY Month
    """
    
    return client.execute_sql(query, params=tuple(params))
```

## ⚡ Performance Optimization

### Partitioning

```python
# Create a partitioned table
schema = {
    "columns": [
        {"name": "ContributionID", "type": "STRING"},
        {"name": "DonorID", "type": "STRING"},
        {"name": "Amount", "type": "DOUBLE"},
        {"name": "ContributionDate", "type": "DATE"},
        {"name": "CampaignID", "type": "STRING"}
    ],
    "partitioned_by": ["ContributionDate"],
    "partition_format": "YYYY-MM"
}

client.create_table("PartitionedContributions", schema)
```

### Caching

```python
# Enable caching for frequently accessed data
client = LakehouseClient(
    workspace_id="your-workspace-id",
    lakehouse_id="DataLakehouse",
    cache_enabled=True,
    cache_ttl=3600  # 1 hour
)

# First query - fetches from lakehouse
result1 = client.execute_sql("SELECT * FROM DonorTable")

# Second query - returns cached result (if within TTL)
result2 = client.execute_sql("SELECT * FROM DonorTable")
```

### Query Optimization

```python
# Optimize queries for lakehouse
# Use predicate pushdown
query = """
SELECT DonorID, DonorName, TotalContributions
FROM DonorTable
WHERE TotalContributions > 10000
  AND Organization = 'UNHCR'
ORDER BY TotalContributions DESC
LIMIT 100
"""

# Use column pruning (only select needed columns)
# Use filter pushdown (apply filters early)
# Use limit to restrict result size
```

### Parallel Processing

```python
# Use Spark for parallel processing
spark = client.get_spark_session()

# Read table
df = spark.table("DonorTable")

# Process in parallel
result = df.filter(F.col("TotalContributions") > 10000) \
    .groupBy("Organization") \
    .agg(
        F.sum("TotalContributions").alias("TotalAmount"),
        F.count("*").alias("DonorCount")
    ) \
    .collect()
```

## 🔐 Security

### Row-Level Security

```python
# Lakehouses support row-level security (RLS)
# Define RLS rules in Fabric

# Query with RLS automatically applied
query = "SELECT * FROM DonorTable"

# RLS is automatically enforced by Fabric
result = client.execute_sql(query)
```

### Column-Level Security

```python
# Lakehouses support column-level security
# Define column masks in Fabric

# Query with column security automatically applied
query = "SELECT DonorID, DonorName, Email FROM DonorTable"

# Column security is automatically enforced
result = client.execute_sql(query)
```

### Secure File Operations

```python
# Always validate file paths to prevent directory traversal
import os

def safe_upload_file(local_path: str, lakehouse_path: str) -> bool:
    """Safely upload file with path validation"""
    # Normalize paths
    local_path = os.path.normpath(local_path)
    lakehouse_path = os.path.normpath(lakehouse_path)
    
    # Prevent directory traversal
    if ".." in lakehouse_path or lakehouse_path.startswith("/"):
        lakehouse_path = lakehouse_path.lstrip("/")
    
    # Validate file exists
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")
    
    # Upload file
    client.upload_file(local_path, f"/safe/{lakehouse_path}")
    return True
```

## 🛡️ Error Handling

### Common Errors

```python
from mcp_framework.error_handling import MCPError, ErrorCodes
from mcp_framework.fabric import LakehouseError

try:
    result = client.execute_sql(query)
except LakehouseError as e:
    # Handle lakehouse-specific errors
    if e.error_code == "TABLE_NOT_FOUND":
        raise MCPError(
            error_code=ErrorCodes.TABLE_NOT_FOUND,
            message=f"Table not found: {str(e)}",
            category="Configuration"
        )
    elif e.error_code == "PERMISSION_DENIED":
        raise MCPError(
            error_code=ErrorCodes.ACCESS_DENIED,
            message="Access denied to lakehouse",
            category="Authorization"
        )
    elif e.error_code == "SYNTAX_ERROR":
        raise MCPError(
            error_code=ErrorCodes.INVALID_QUERY,
            message=f"SQL syntax error: {str(e)}",
            category="Validation"
        )
    else:
        raise MCPError(
            error_code=ErrorCodes.LAKEHOUSE_ERROR,
            message=f"Lakehouse error: {str(e)}",
            category="DataAccess"
        )
except Exception as e:
    # Handle other errors
    raise MCPError(
        error_code=ErrorCodes.OPERATION_FAILED,
        message=f"Lakehouse operation failed: {str(e)}",
        category="DataAccess"
    )
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from mcp_framework.fabric import LakehouseError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=(LakehouseError, ConnectionError)
)
def execute_lakehouse_operation_with_retry(operation, *args, **kwargs):
    """Execute lakehouse operation with automatic retry"""
    return operation(*args, **kwargs)

# Usage
result = execute_lakehouse_operation_with_retry(
    client.execute_sql,
    query,
    params=params
)
```

## 📊 Result Processing

### Processing Query Results

```python
def process_contribution_data(result: list) -> list:
    """Process raw query results into structured data"""
    processed = []
    
    for row in result:
        processed.append({
            "contribution_id": row.get("ContributionID"),
            "donor_id": row.get("DonorID"),
            "amount": float(row.get("Amount", 0)),
            "date": str(row.get("ContributionDate")),
            "campaign_id": row.get("CampaignID"),
            "status": row.get("Status", "Completed")
        })
    
    return processed
```

### Data Transformation

```python
import pandas as pd

def query_to_dataframe(query: str, params: tuple = None) -> pd.DataFrame:
    """Execute query and return results as DataFrame"""
    result = client.execute_sql(query, params=params)
    return pd.DataFrame(result)

# Example usage
df = query_to_dataframe("SELECT * FROM ContributionTable WHERE DonorID = %s", ("D001",))
print(df.head())
print(df.describe())
```

### Aggregation and Analysis

```python
def analyze_donor_portfolio(result: list) -> dict:
    """Analyze donor portfolio from query results"""
    if not result:
        return {"status": "no_data"}
    
    # Convert to DataFrame
    df = pd.DataFrame(result)
    
    # Calculate statistics
    total_donors = len(df)
    total_contributions = df['TotalContributions'].sum()
    average_contributions = df['TotalContributions'].mean()
    
    # Organization breakdown
    org_breakdown = df.groupby('Organization').agg({
        'TotalContributions': ['sum', 'count', 'mean']
    }).to_dict()
    
    return {
        "status": "success",
        "total_donors": total_donors,
        "total_contributions": float(total_contributions),
        "average_contributions": float(average_contributions),
        "organization_breakdown": org_breakdown
    }
```

## 🧪 Testing

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock
from mcp_framework.fabric import LakehouseClient

def test_lakehouse_query():
    """Test lakehouse query execution"""
    with patch('mcp_framework.fabric.LakehouseClient') as mock_client:
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.execute_sql.return_value = [
            {"DonorID": "D001", "DonorName": "Test Donor", "TotalContributions": 10000}
        ]
        mock_client.return_value = mock_instance
        
        # Execute query
        client = LakehouseClient(
            workspace_id="test-workspace",
            lakehouse_id="TestLakehouse"
        )
        result = client.execute_sql("SELECT * FROM DonorTable WHERE DonorID = %s", ("D001",))
        
        # Assertions
        assert len(result) == 1
        assert result[0]["DonorID"] == "D001"
        assert result[0]["DonorName"] == "Test Donor"
```

### Integration Tests

```python
@pytest.mark.integration
def test_lakehouse_integration():
    """Test integration with actual Fabric lakehouse"""
    # This test requires actual Fabric credentials
    client = LakehouseClient(
        tenant_id="test-tenant-id",
        workspace_id="test-workspace-id",
        lakehouse_id="TestLakehouse"
    )
    
    # Test simple query
    result = client.execute_sql("SELECT TOP 10 * FROM DonorTable")
    assert isinstance(result, list)
    assert len(result) <= 10
    
    # Test table listing
    tables = client.list_tables()
    assert isinstance(tables, list)
    assert len(tables) > 0
```

## 📈 Monitoring

### Operation Metrics

```python
from mcp_framework.telemetry import TelemetryClient
import time

telemetry = TelemetryClient()

# Track lakehouse operation
@telemetry.track_operation("lakehouse.operation")
def execute_tracked_operation(operation_name: str, func, *args, **kwargs):
    """Execute lakehouse operation with telemetry tracking"""
    start_time = time.time()
    try:
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Track metrics
        telemetry.track_metric("lakehouse.operation.duration", duration * 1000)  # ms
        telemetry.track_metric(f"lakehouse.{operation_name}.count", 1)
        
        return result
    except Exception as e:
        telemetry.track_exception(e)
        raise

# Usage
result = execute_tracked_operation(
    "query",
    client.execute_sql,
    query,
    params=params
)
```

### Performance Logging

```python
import logging
from mcp_framework.platform import MCPFramework

framework = MCPFramework()
logger = framework.logger

# Log operation performance
def log_operation_performance(operation: str, result: list, duration: float):
    """Log lakehouse operation performance metrics"""
    logger.info(
        f"Lakehouse {operation} executed",
        extra={
            "lakehouse_id": "DataLakehouse",
            "operation": operation,
            "rows_affected": len(result) if result else 0,
            "duration_ms": duration * 1000
        }
    )
```

## 🛠️ Best Practices

### Lakehouse Best Practices

1. **⭐ Use Delta Lake Format** - Always use Delta format for tables
2. **⭐ Partition Large Tables** - Partition tables by date or other logical dimensions
3. **⭐ Optimize File Sizes** - Keep file sizes between 256MB and 1GB
4. **⭐ Use Z-Ordering** - Optimize query performance with Z-ORDER BY
5. **⭐ Compact Small Files** - Regularly compact small files
6. **⭐ Use Statistics** - Update statistics for better query planning

### Performance Best Practices

1. **⭐ Filter Early** - Apply filters as early as possible in queries
2. **⭐ Use Column Pruning** - Only select the columns you need
3. **⭐ Limit Results** - Use LIMIT to restrict result sizes
4. **⭐ Cache Frequently Used Data** - Cache results of common queries
5. **⭐ Use Spark for Complex Operations** - Use Spark for data transformations

### Security Best Practices

1. **⭐ Use RLS** - Implement row-level security for sensitive data
2. **⭐ Use Column Masking** - Mask sensitive columns
3. **⭐ Validate All Inputs** - Prevent injection attacks
4. **⭐ Use Least Privilege** - Grant minimum required permissions
5. **⭐ Audit Operations** - Log all lakehouse operations

## 🛠️ Troubleshooting

### Common Issues

#### Table Not Found

**Error**: `LakehouseError: Table 'DonorTable' not found`

**Solution**:
```python
# Verify the table exists
tables = client.list_tables()
print(f"Available tables: {[t['name'] for t in tables]}")

# Check the table name is correct
# Table names are case-sensitive
```

#### Permission Denied

**Error**: `LakehouseError: Permission denied to access lakehouse`

**Solution**:
```bash
# Grant permissions to the service principal
az fabric lakehouse add-user \
  --workspace workspace-id \
  --lakehouse lakehouse-id \
  --user service-principal-id \
  --role Contributor

# Or use Managed Identity
az fabric lakehouse add-user \
  --workspace workspace-id \
  --lakehouse lakehouse-id \
  --user managed-identity-id \
  --role Contributor
```

#### Connection Failed

**Error**: `LakehouseError: Failed to connect to lakehouse`

**Solution**:
```bash
# Verify Azure authentication
az login
az account set --subscription your-subscription-id

# Check network connectivity
# Verify service principal has access to the workspace

# Test connection
python -c "from mcp_framework.fabric import LakehouseClient; c = LakehouseClient(workspace_id='test', lakehouse_id='test'); print(c.test_connection())"
```

#### Query Timeout

**Error**: `LakehouseError: Query execution timed out after 30 seconds`

**Solution**:
```python
# Increase timeout
client = LakehouseClient(
    workspace_id="your-workspace-id",
    lakehouse_id="DataLakehouse",
    timeout=60  # 60 seconds
)

# Or optimize the query
# - Add appropriate partitioning
# - Reduce result set size
# - Simplify complex operations
# - Use filters to limit data
```

#### File Not Found

**Error**: `LakehouseError: File '/data/uploads/data.csv' not found`

**Solution**:
```python
# Verify the file exists
files = client.list_files("/data/uploads")
print(f"Available files: {[f['name'] for f in files]}")

# Check the file path is correct
# Paths are case-sensitive
```

## 📚 Next Steps

1. **[Semantic Model Access](semantic-models.md)** - Learn about semantic model querying
2. **[Warehouse Queries](warehouse-queries.md)** - Explore warehouse SQL operations
3. **[Fabric Connectivity Module](../modules/fabric-connectivity.md)** - Deep dive into Fabric integration
4. **[Donor Management Example](donor-management.md)** - Complete domain example

## 🔗 Related Documentation

- [Microsoft Fabric Lakehouses](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview)
- [Delta Lake Documentation](https://delta.io/)
- [Fabric Spark Documentation](https://learn.microsoft.com/en-us/fabric/data-engineering/spark-overview)
- [MCP Platform Fabric Module](../modules/fabric-connectivity.md)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
