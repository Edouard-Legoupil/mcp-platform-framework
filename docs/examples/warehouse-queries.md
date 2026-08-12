# 🏭 Warehouse Queries Guide

## Overview

This guide demonstrates how to query **Microsoft Fabric Warehouses** using the MCP Platform Framework. Fabric Warehouses provide SQL endpoints for your data, allowing you to use familiar T-SQL syntax to query your data.

## 🎯 Key Concepts

### What are Fabric Warehouses?

Fabric Warehouses are:
- **SQL endpoints** for your data in Microsoft Fabric
- **T-SQL compatible** - Use standard SQL syntax
- **Serverless** - No infrastructure to manage
- **Scalable** - Automatically scale based on workload
- **Integrated** - Part of the unified Fabric platform

### When to Use Warehouses vs Semantic Models

| Feature | Warehouse | Semantic Model |
|---------|-----------|-----------------|
| **Query Language** | T-SQL | DAX |
| **Use Case** | Complex joins, transactions | Business analytics, calculations |
| **Performance** | Optimized for large scans | Optimized for aggregations |
| **Security** | SQL permissions | Row-level security |
| **Learning Curve** | Low (SQL knowledge) | Medium (DAX knowledge) |

## 🏗️ Setup

### Prerequisites

1. **Microsoft Fabric Workspace** with warehouses deployed
2. **Service Principal** with access to Fabric
3. **MCP Platform Framework** installed
4. **Required Permissions**: SQL Reader or Contributor on the warehouse

### Configuration

**config/development.json**
```json
{
  "fabric": {
    "tenant_id": "your-fabric-tenant-id",
    "workspace_id": "your-workspace-id",
    "warehouses": {
      "DataWarehouse": {
        "warehouse_id": "DataWarehouse",
        "classification": "CONFIDENTIAL"
      },
      "ReportingWarehouse": {
        "warehouse_id": "ReportingWarehouse",
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

## 🔧 Warehouse Client

### Basic Usage

```python
from mcp_framework.fabric import WarehouseClient

# Initialize the client
client = WarehouseClient(
    tenant_id="your-tenant-id",
    workspace_id="your-workspace-id",
    warehouse_id="DataWarehouse"
)

# Or use framework configuration
from mcp_framework.platform import MCPFramework

framework = MCPFramework()
client = WarehouseClient(
    workspace_id=framework.config.get("fabric.workspace_id"),
    warehouse_id="DataWarehouse"
)
```

### Client Configuration

```python
# Configure client with additional options
client = WarehouseClient(
    tenant_id="your-tenant-id",
    workspace_id="your-workspace-id",
    warehouse_id="DataWarehouse",
    timeout=30,  # Request timeout in seconds
    retry_count=3,  # Number of retries for failed requests
    pool_size=10,  # Connection pool size
    autocommit=True  # Auto-commit transactions
)
```

## 📊 Querying Warehouses

### Basic Queries

#### 1. Simple SELECT Query

```python
# Get all donors
query = "SELECT * FROM DonorTable"
result = client.execute(query)

for row in result:
    print(row)
```

#### 2. Filtered Query

```python
# Get donors from a specific organization
query = """
SELECT DonorID, DonorName, Organization, TotalContributions
FROM DonorTable
WHERE Organization = 'UNHCR'
ORDER BY TotalContributions DESC
"""

result = client.execute(query)
```

#### 3. Aggregation Query

```python
# Get total contributions by organization
query = """
SELECT 
    Organization,
    COUNT(*) as DonorCount,
    SUM(TotalContributions) as TotalAmount,
    AVG(TotalContributions) as AverageAmount
FROM DonorTable
GROUP BY Organization
ORDER BY TotalAmount DESC
"""

result = client.execute(query)
```

### Advanced Queries

#### 4. Join Query

```python
# Get donor information with their contributions
query = """
SELECT 
    d.DonorID,
    d.DonorName,
    d.Organization,
    c.ContributionID,
    c.ContributionDate,
    c.Amount,
    c.CampaignID
FROM DonorTable d
INNER JOIN ContributionTable c ON d.DonorID = c.DonorID
WHERE c.ContributionDate >= '2024-01-01'
ORDER BY c.ContributionDate DESC
"""

result = client.execute(query)
```

#### 5. Window Functions

```python
# Get donors with their rank by total contributions
query = """
SELECT 
    DonorID,
    DonorName,
    Organization,
    TotalContributions,
    RANK() OVER (ORDER BY TotalContributions DESC) as ContributionRank,
    DENSE_RANK() OVER (ORDER BY TotalContributions DESC) as DenseRank
FROM DonorTable
ORDER BY ContributionRank
"""

result = client.execute(query)
```

#### 6. Common Table Expressions (CTEs)

```python
# Use CTEs for complex queries
query = """
WITH TopDonors AS (
    SELECT 
        DonorID,
        DonorName,
        TotalContributions
    FROM DonorTable
    WHERE TotalContributions > 10000
),
DonorStats AS (
    SELECT 
        AVG(TotalContributions) as AvgContribution,
        MAX(TotalContributions) as MaxContribution,
        MIN(TotalContributions) as MinContribution
    FROM DonorTable
)
SELECT 
    td.DonorID,
    td.DonorName,
    td.TotalContributions,
    ds.AvgContribution,
    CASE 
        WHEN td.TotalContributions > ds.AvgContribution * 2 THEN 'High Value'
        WHEN td.TotalContributions > ds.AvgContribution THEN 'Medium Value'
        ELSE 'Standard'
    END as DonorCategory
FROM TopDonors td
CROSS JOIN DonorStats ds
ORDER BY td.TotalContributions DESC
"""

result = client.execute(query)
```

## 🎯 Common Query Patterns

### Donor Management Queries

#### Get Donor by ID

```python
def get_donor_by_id(donor_id: str) -> dict:
    """Retrieve a specific donor by ID"""
    query = """
    SELECT *
    FROM DonorTable
    WHERE DonorID = %s
    """
    
    result = client.execute(query, params=(donor_id,))
    return result[0] if result else None
```

#### Get Donor Contribution History

```python
def get_donor_contributions(donor_id: str, start_date: str = None, end_date: str = None) -> list:
    """Retrieve contribution history for a donor"""
    query = """
    SELECT 
        ContributionID,
        ContributionDate,
        Amount,
        Currency,
        CampaignID,
        PaymentMethod,
        Status
    FROM ContributionTable
    WHERE DonorID = %s
    """
    
    params = [donor_id]
    
    if start_date and end_date:
        query += "AND ContributionDate BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    elif start_date:
        query += "AND ContributionDate >= %s"
        params.append(start_date)
    elif end_date:
        query += "AND ContributionDate <= %s"
        params.append(end_date)
    
    query += " ORDER BY ContributionDate DESC"
    
    return client.execute(query, params=tuple(params))
```

#### Get Top Donors

```python
def get_top_donors(limit: int = 10) -> list:
    """Retrieve top donors by total contributions"""
    query = f"""
    SELECT 
        DonorID,
        DonorName,
        Organization,
        TotalContributions
    FROM DonorTable
    ORDER BY TotalContributions DESC
    LIMIT {limit}
    """
    
    return client.execute(query)
```

### Financial Queries

#### Get Revenue by Campaign

```python
def get_revenue_by_campaign() -> list:
    """Retrieve revenue breakdown by campaign"""
    query = """
    SELECT 
        CampaignID,
        SUM(Amount) as TotalRevenue,
        COUNT(*) as ContributionCount,
        AVG(Amount) as AverageContribution
    FROM ContributionTable
    WHERE Status = 'Completed'
    GROUP BY CampaignID
    ORDER BY TotalRevenue DESC
    """
    
    return client.execute(query)
```

#### Get Year-to-Date Revenue

```python
def get_ytd_revenue() -> float:
    """Calculate year-to-date revenue"""
    query = """
    SELECT SUM(Amount) as YTDRevenue
    FROM ContributionTable
    WHERE ContributionDate >= DATE_TRUNC('year', CURRENT_DATE)
    AND Status = 'Completed'
    """
    
    result = client.execute(query)
    return result[0]['YTDRevenue'] if result else 0.0
```

#### Get Monthly Revenue Trend

```python
def get_monthly_revenue_trend(year: int = None) -> list:
    """Retrieve monthly revenue trend"""
    if year is None:
        year = datetime.now().year
    
    query = f"""
    SELECT 
        DATE_TRUNC('month', ContributionDate) as Month,
        SUM(Amount) as TotalRevenue,
        COUNT(*) as ContributionCount
    FROM ContributionTable
    WHERE YEAR(ContributionDate) = {year}
    AND Status = 'Completed'
    GROUP BY DATE_TRUNC('month', ContributionDate)
    ORDER BY Month
    """
    
    return client.execute(query)
```

## 🔄 Transactions

### Basic Transactions

```python
# Execute a transaction
with client.transaction() as tx:
    # Insert a new donor
    tx.execute("""
    INSERT INTO DonorTable (DonorID, DonorName, Organization, Email)
    VALUES (%s, %s, %s, %s)
    """, params=("D999", "New Donor", "New Org", "new@donor.com"))
    
    # Insert a contribution
    tx.execute("""
    INSERT INTO ContributionTable (ContributionID, DonorID, Amount, ContributionDate)
    VALUES (%s, %s, %s, %s)
    """, params=("C999", "D999", 1000.00, "2024-01-01"))
    
    # Transaction will be committed automatically if no errors

# If an error occurs, the transaction will be rolled back
```

### Manual Transaction Control

```python
# Start a transaction
client.begin_transaction()

try:
    # Execute queries
    client.execute("INSERT INTO Table1 VALUES (%s)", params=(1,))
    client.execute("INSERT INTO Table2 VALUES (%s)", params=(2,))
    
    # Commit the transaction
    client.commit()
    print("Transaction committed successfully")
    
except Exception as e:
    # Roll back the transaction
    client.rollback()
    print(f"Transaction rolled back: {str(e)}")
    raise
```

### Batch Operations

```python
# Batch insert
contributions = [
    ("C001", "D001", 1000.00, "2024-01-01"),
    ("C002", "D002", 2000.00, "2024-01-02"),
    ("C003", "D003", 3000.00, "2024-01-03")
]

query = """
INSERT INTO ContributionTable (ContributionID, DonorID, Amount, ContributionDate)
VALUES (%s, %s, %s, %s)
"""

# Execute batch insert
client.execute_batch(query, params_list=contributions)
```

## ⚡ Performance Optimization

### Query Optimization

```python
# Use parameterized queries (prevents SQL injection and improves performance)
def get_donors_by_organization(organization: str) -> list:
    """Retrieve donors by organization"""
    query = """
    SELECT *
    FROM DonorTable
    WHERE Organization = %s
    """
    
    return client.execute(query, params=(organization,))
```

### Indexing

```python
# Create an index (if you have permissions)
query = """
CREATE INDEX idx_donor_organization ON DonorTable(Organization)
"""

client.execute(query)
```

### Query Hints

```python
# Use query hints for optimization
query = """
SELECT /*+ INDEX(DonorTable idx_donor_organization) */ *
FROM DonorTable
WHERE Organization = %s
"""

result = client.execute(query, params=("UNHCR",))
```

### Pagination

```python
# Query with pagination
def get_donors_page(page_size: int = 100, page_number: int = 1) -> list:
    """Retrieve donors with pagination"""
    offset = (page_number - 1) * page_size
    
    query = """
    SELECT *
    FROM DonorTable
    ORDER BY DonorName
    LIMIT %s OFFSET %s
    """
    
    return client.execute(query, params=(page_size, offset))

# Get all donors with automatic pagination
def get_all_donors() -> list:
    """Retrieve all donors with automatic pagination"""
    all_donors = []
    page = 1
    page_size = 1000
    
    while True:
        donors = get_donors_page(page_size, page)
        if not donors:
            break
        all_donors.extend(donors)
        page += 1
    
    return all_donors
```

## 🔐 Security

### Parameterized Queries

```python
# Always use parameterized queries to prevent SQL injection
def get_donor_by_name_safe(donor_name: str) -> list:
    """Safely query by donor name"""
    query = """
    SELECT *
    FROM DonorTable
    WHERE DonorName = %s
    """
    
    return client.execute(query, params=(donor_name,))
```

### Row-Level Security

Warehouses support row-level security (RLS) defined in Fabric:

```python
# Query with RLS automatically applied
# The user's permissions determine which rows they can see
query = "SELECT * FROM DonorTable"

# RLS is automatically enforced by Fabric
result = client.execute(query)
```

### Secure Connection

```python
# Use SSL for secure connections
client = WarehouseClient(
    workspace_id="your-workspace-id",
    warehouse_id="DataWarehouse",
    use_ssl=True,  # Default is True
    verify_ssl=True  # Default is True
)
```

## 🛡️ Error Handling

### Common Errors

```python
from mcp_framework.error_handling import MCPError, ErrorCodes
from mcp_framework.fabric import WarehouseError

try:
    result = client.execute(query)
except WarehouseError as e:
    # Handle warehouse-specific errors
    if e.error_code == "SYNTAX_ERROR":
        raise MCPError(
            error_code=ErrorCodes.INVALID_QUERY,
            message=f"SQL syntax error: {str(e)}",
            category="Validation"
        )
    elif e.error_code == "PERMISSION_DENIED":
        raise MCPError(
            error_code=ErrorCodes.ACCESS_DENIED,
            message="Access denied to warehouse",
            category="Authorization"
        )
    elif e.error_code == "TABLE_NOT_FOUND":
        raise MCPError(
            error_code=ErrorCodes.TABLE_NOT_FOUND,
            message=f"Table not found: {str(e)}",
            category="Configuration"
        )
    else:
        raise MCPError(
            error_code=ErrorCodes.WAREHOUSE_ERROR,
            message=f"Warehouse error: {str(e)}",
            category="DataAccess"
        )
except Exception as e:
    # Handle other errors
    raise MCPError(
        error_code=ErrorCodes.QUERY_EXECUTION_FAILED,
        message=f"Query execution failed: {str(e)}",
        category="DataAccess"
    )
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from mcp_framework.fabric import WarehouseError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=(WarehouseError, ConnectionError)
)
def execute_query_with_retry(query: str, params: tuple = None) -> list:
    """Execute query with automatic retry"""
    return client.execute(query, params=params)
```

## 📊 Result Processing

### Processing Query Results

```python
def process_donor_data(result: list) -> list:
    """Process raw query results into structured data"""
    processed = []
    
    for row in result:
        processed.append({
            "donor_id": row.get("DonorID"),
            "name": row.get("DonorName"),
            "organization": row.get("Organization"),
            "total_contributions": float(row.get("TotalContributions", 0)),
            "first_contribution": str(row.get("FirstContributionDate")),
            "last_contribution": str(row.get("LastContributionDate")),
            "status": row.get("Status", "Active")
        })
    
    return processed
```

### Data Transformation

```python
import pandas as pd

def query_to_dataframe(query: str, params: tuple = None) -> pd.DataFrame:
    """Execute query and return results as DataFrame"""
    result = client.execute(query, params=params)
    return pd.DataFrame(result)

# Example usage
df = query_to_dataframe("SELECT * FROM DonorTable WHERE Organization = %s", ("UNHCR",))
print(df.head())
print(df.describe())
```

### Aggregation and Analysis

```python
def analyze_contribution_trends(result: list) -> dict:
    """Analyze contribution trends from query results"""
    if not result:
        return {"status": "no_data"}
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(result)
    
    # Calculate statistics
    total_revenue = df['Amount'].sum()
    average_contribution = df['Amount'].mean()
    contribution_count = len(df)
    
    # Time-based analysis
    df['ContributionDate'] = pd.to_datetime(df['ContributionDate'])
    monthly_trend = df.groupby(df['ContributionDate'].dt.to_period('M'))['Amount'].sum()
    
    return {
        "status": "success",
        "total_revenue": float(total_revenue),
        "average_contribution": float(average_contribution),
        "contribution_count": contribution_count,
        "monthly_trend": monthly_trend.to_dict()
    }
```

## 🧪 Testing

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock
from mcp_framework.fabric import WarehouseClient

def test_warehouse_query():
    """Test warehouse query execution"""
    with patch('mcp_framework.fabric.WarehouseClient') as mock_client:
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.execute.return_value = [
            {"DonorID": "D001", "DonorName": "Test Donor", "TotalContributions": 10000}
        ]
        mock_client.return_value = mock_instance
        
        # Execute query
        client = WarehouseClient(
            workspace_id="test-workspace",
            warehouse_id="TestWarehouse"
        )
        result = client.execute("SELECT * FROM DonorTable WHERE DonorID = %s", ("D001",))
        
        # Assertions
        assert len(result) == 1
        assert result[0]["DonorID"] == "D001"
        assert result[0]["DonorName"] == "Test Donor"
```

### Integration Tests

```python
@pytest.mark.integration
def test_warehouse_integration():
    """Test integration with actual Fabric warehouse"""
    # This test requires actual Fabric credentials
    client = WarehouseClient(
        tenant_id="test-tenant-id",
        workspace_id="test-workspace-id",
        warehouse_id="TestWarehouse"
    )
    
    # Test simple query
    result = client.execute("SELECT TOP 10 * FROM DonorTable")
    assert isinstance(result, list)
    assert len(result) <= 10
```

## 📈 Monitoring

### Query Metrics

```python
from mcp_framework.telemetry import TelemetryClient
import time

telemetry = TelemetryClient()

# Track query execution
@telemetry.track_operation("warehouse.query")
def execute_tracked_query(query: str, params: tuple = None) -> list:
    """Execute query with telemetry tracking"""
    start_time = time.time()
    try:
        result = client.execute(query, params=params)
        duration = time.time() - start_time
        
        # Track metrics
        telemetry.track_metric("warehouse.query.duration", duration * 1000)  # ms
        telemetry.track_metric("warehouse.query.rows", len(result))
        telemetry.track_metric("warehouse.query.size", len(query))
        
        return result
    except Exception as e:
        telemetry.track_exception(e)
        raise
```

### Performance Logging

```python
import logging
from mcp_framework.platform import MCPFramework

framework = MCPFramework()
logger = framework.logger

# Log query performance
def log_query_performance(query: str, params: tuple, result: list, duration: float):
    """Log query performance metrics"""
    logger.info(
        "Warehouse query executed",
        extra={
            "warehouse_id": "DataWarehouse",
            "rows_returned": len(result),
            "duration_ms": duration * 1000,
            "query_length": len(query),
            "params_count": len(params) if params else 0
        }
    )
```

## 🛠️ Best Practices

### Query Best Practices

1. **⭐ Use Parameterized Queries** - Always use parameters to prevent SQL injection
2. **⭐ Filter Early** - Apply WHERE clauses as early as possible
3. **⭐ Limit Results** - Use LIMIT to restrict result sizes
4. **⭐ Select Specific Columns** - Only select the columns you need
5. **⭐ Use Appropriate Data Types** - Ensure parameters match column data types
6. **⭐ Avoid SELECT *** - Explicitly list required columns

### Performance Best Practices

1. **⭐ Use Indexes** - Create indexes on frequently filtered columns
2. **⭐ Optimize Joins** - Join on indexed columns
3. **⭐ Use Pagination** - Implement pagination for large result sets
4. **⭐ Cache Results** - Cache frequently used query results
5. **⭐ Monitor Query Performance** - Track and optimize slow queries

### Security Best Practices

1. **⭐ Always Use Parameters** - Prevent SQL injection with parameterized queries
2. **⭐ Use RLS** - Leverage Fabric's row-level security
3. **⭐ Validate Inputs** - Validate all query parameters
4. **⭐ Handle Errors Gracefully** - Never expose sensitive information in errors
5. **⭐ Use Least Privilege** - Grant minimum required permissions

## 🛠️ Troubleshooting

### Common Issues

#### Table Not Found

**Error**: `WarehouseError: Table 'DonorTable' not found`

**Solution**:
```python
# Verify the table exists
tables = client.list_tables()
print(f"Available tables: {tables}")

# Check the table name is correct
# Table names are case-sensitive in some databases
```

#### Syntax Error

**Error**: `WarehouseError: Syntax error near 'SELECT'`

**Solution**:
```python
# Validate your SQL syntax
# Use a SQL validator or test in a SQL client first

# Common issues:
# - Missing or extra commas
# - Unclosed quotes or parentheses
# - Reserved keywords used as column names without quotes
```

#### Connection Failed

**Error**: `WarehouseError: Failed to connect to warehouse`

**Solution**:
```bash
# Verify Azure authentication
az login
az account set --subscription your-subscription-id

# Check network connectivity
# Verify service principal has access to the warehouse

# Test connection
python -c "from mcp_framework.fabric import WarehouseClient; c = WarehouseClient(workspace_id='test', warehouse_id='test'); print(c.test_connection())"
```

#### Permission Denied

**Error**: `WarehouseError: Permission denied to access table 'DonorTable'`

**Solution**:
```bash
# Grant permissions to the service principal
az fabric warehouse add-user \
  --workspace workspace-id \
  --warehouse warehouse-id \
  --user service-principal-id \
  --role Reader

# Or use Managed Identity
az fabric warehouse add-user \
  --workspace workspace-id \
  --warehouse warehouse-id \
  --user managed-identity-id \
  --role Reader
```

#### Query Timeout

**Error**: `WarehouseError: Query execution timed out after 30 seconds`

**Solution**:
```python
# Increase timeout
client = WarehouseClient(
    workspace_id="your-workspace-id",
    warehouse_id="DataWarehouse",
    timeout=60  # 60 seconds
)

# Or optimize the query
# - Add appropriate indexes
# - Reduce result set size
# - Simplify complex joins
# - Use WHERE clauses to filter data early
```

## 📚 Next Steps

1. **[Lakehouse Operations](lakehouse-operations.md)** - Explore lakehouse data operations
2. **[Semantic Model Access](semantic-models.md)** - Learn about semantic model querying
3. **[Fabric Connectivity Module](../modules/fabric-connectivity.md)** - Deep dive into Fabric integration
4. **[Donor Management Example](donor-management.md)** - Complete domain example

## 🔗 Related Documentation

- [Microsoft Fabric Warehouses](https://learn.microsoft.com/en-us/fabric/data-engineering/warehouse-overview)
- [T-SQL Language Reference](https://learn.microsoft.com/en-us/sql/t-sql/language-reference)
- [Fabric SQL Querying](https://learn.microsoft.com/en-us/fabric/data-engineering/sql-query)
- [MCP Platform Fabric Module](../modules/fabric-connectivity.md)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
