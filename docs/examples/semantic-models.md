# 🔗 Semantic Model Access Guide

## Overview

This guide demonstrates how to access and query **Microsoft Fabric Semantic Models** using the MCP Platform Framework. Semantic models provide a business-friendly abstraction over your data, allowing you to query data using familiar business terms without needing to understand the underlying database schema.

## 🎯 Key Concepts

### What are Semantic Models?

Semantic models in Microsoft Fabric are:
- **Business abstractions** over raw data tables
- **DAX-based** (Data Analysis Expressions) for calculations
- **Reusable** across multiple reports and tools
- **Secure** with row-level security support
- **Optimized** for performance

### Why Use Semantic Models?

✅ **Business Terms**: Query using business vocabulary (e.g., "Total Revenue" instead of "SUM(Sales[Amount])")
✅ **Consistency**: Ensure everyone uses the same calculations and definitions
✅ **Security**: Apply row-level security at the model level
✅ **Performance**: Leverage Fabric's query optimization
✅ **Maintainability**: Centralize business logic in one place

## 🏗️ Setup

### Prerequisites

1. **Microsoft Fabric Workspace** with semantic models deployed
2. **Service Principal** with access to Fabric
3. **MCP Platform Framework** installed
4. **Required Permissions**: Reader or Contributor on the workspace

### Configuration

**config/development.json**
```json
{
  "fabric": {
    "tenant_id": "your-fabric-tenant-id",
    "workspace_id": "your-workspace-id",
    "semantic_models": {
      "DonorManagement": {
        "model_id": "DonorManagementModel",
        "classification": "CONFIDENTIAL"
      },
      "FinancialMetrics": {
        "model_id": "FinancialMetricsModel",
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

## 🔧 Semantic Model Client

### Basic Usage

```python
from mcp_framework.fabric import SemanticModelClient

# Initialize the client
client = SemanticModelClient(
    tenant_id="your-tenant-id",
    workspace_id="your-workspace-id"
)

# Or use framework configuration
from mcp_framework.platform import MCPFramework

framework = MCPFramework()
client = SemanticModelClient(
    workspace_id=framework.config.get("fabric.workspace_id")
)
```

### Client Configuration

```python
# Configure client with additional options
client = SemanticModelClient(
    tenant_id="your-tenant-id",
    workspace_id="your-workspace-id",
    timeout=30,  # Request timeout in seconds
    retry_count=3,  # Number of retries for failed requests
    cache_enabled=True,  # Enable query caching
    cache_ttl=300  # Cache time-to-live in seconds
)
```

## 📊 Querying Semantic Models

### Basic Queries

#### 1. Simple Table Query

```python
# Get all donors from the DonorTable
query = """
EVALUATE
VAR Donors = DonorTable
RETURN
GENERATE(Donors, ALL)
"""

result = client.execute(query, model_id="DonorManagementModel")
print(f"Found {len(result)} donors")
```

#### 2. Filtered Query

```python
# Get donors from a specific organization
query = """
EVALUATE
VAR FilteredDonors = FILTER(
    DonorTable,
    DonorTable[Organization] = "UNHCR"
)
RETURN
GENERATE(FilteredDonors, ALL)
"""

result = client.execute(query, model_id="DonorManagementModel")
```

#### 3. Sorted Query

```python
# Get donors sorted by total contributions (descending)
query = """
EVALUATE
VAR SortedDonors = ORDERBY(
    DonorTable,
    DonorTable[TotalContributions],
    DESC
)
RETURN
GENERATE(SortedDonors, ALL)
"""

result = client.execute(query, model_id="DonorManagementModel")
```

### Advanced Queries

#### 4. Aggregation Query

```python
# Get total contributions by organization
query = """
EVALUATE
VAR ContributionsByOrg = GROUPBY(
    ContributionTable,
    ContributionTable[Organization],
    "TotalAmount", SUM(ContributionTable[Amount])
)
RETURN
GENERATE(ContributionsByOrg, ALL)
"""

result = client.execute(query, model_id="FinancialMetricsModel")
```

#### 5. Join Query

```python
# Get donor information with their latest contribution
query = """
EVALUATE
VAR DonorsWithLatestContribution = 
    GENERATE(
        DonorTable,
        VAR LatestContribution = TOPN(
            FILTER(
                ContributionTable,
                ContributionTable[DonorID] = DonorTable[DonorID]
            ),
            1,
            ContributionTable[ContributionDate],
            DESC
        )
        RETURN
        ROW(
            "DonorID", DonorTable[DonorID],
            "DonorName", DonorTable[DonorName],
            "LatestContributionDate", LatestContribution[ContributionDate],
            "LatestContributionAmount", LatestContribution[Amount]
        )
    )
RETURN
DonorsWithLatestContribution
"""

result = client.execute(query, model_id="DonorManagementModel")
```

#### 6. Time Intelligence Query

```python
# Get monthly contributions for the current year
query = """
EVALUATE
VAR MonthlyContributions = 
    GROUPBY(
        FILTER(
            ContributionTable,
            YEAR(ContributionTable[ContributionDate]) = YEAR(TODAY())
        ),
        FORMAT(ContributionTable[ContributionDate], "yyyy-MM"),
        "TotalAmount", SUM(ContributionTable[Amount])
    )
RETURN
GENERATE(MonthlyContributions, ALL)
"""

result = client.execute(query, model_id="FinancialMetricsModel")
```

## 🎯 Common Query Patterns

### Donor Management Queries

#### Get Donor by ID

```python
def get_donor_by_id(donor_id: str) -> dict:
    """Retrieve a specific donor by ID"""
    query = f"""
    EVALUATE
    VAR Donor = FILTER(DonorTable, DonorTable[DonorID] = "{donor_id}")
    RETURN
    GENERATE(Donor, ALL)
    """
    
    result = client.execute(query, model_id="DonorManagementModel")
    return result[0] if result else None
```

#### Get Donor Contribution History

```python
def get_donor_contributions(donor_id: str, start_date: str = None, end_date: str = None) -> list:
    """Retrieve contribution history for a donor"""
    date_filter = ""
    if start_date and end_date:
        date_filter = f"&& ContributionTable[ContributionDate] >= DATE({start_date}) && ContributionTable[ContributionDate] <= DATE({end_date})"
    elif start_date:
        date_filter = f"&& ContributionTable[ContributionDate] >= DATE({start_date})"
    elif end_date:
        date_filter = f"&& ContributionTable[ContributionDate] <= DATE({end_date})"
    
    query = f"""
    EVALUATE
    VAR Contributions = FILTER(
        ContributionTable,
        ContributionTable[DonorID] = "{donor_id}"{date_filter}
    )
    VAR SortedContributions = ORDERBY(Contributions, ContributionTable[ContributionDate], DESC)
    RETURN
    GENERATE(SortedContributions, ALL)
    """
    
    return client.execute(query, model_id="FinancialMetricsModel")
```

#### Get Top Donors

```python
def get_top_donors(limit: int = 10) -> list:
    """Retrieve top donors by total contributions"""
    query = f"""
    EVALUATE
    VAR ContributionsByDonor = GROUPBY(
        ContributionTable,
        ContributionTable[DonorID],
        "TotalAmount", SUM(ContributionTable[Amount])
    )
    VAR SortedDonors = ORDERBY(ContributionsByDonor, TotalAmount, DESC)
    VAR TopDonors = TOPN(SortedDonors, {limit})
    RETURN
    GENERATE(TopDonors, ALL)
    """
    
    return client.execute(query, model_id="FinancialMetricsModel")
```

### Financial Queries

#### Get Revenue by Campaign

```python
def get_revenue_by_campaign() -> list:
    """Retrieve revenue breakdown by campaign"""
    query = """
    EVALUATE
    VAR RevenueByCampaign = GROUPBY(
        ContributionTable,
        ContributionTable[CampaignID],
        "TotalRevenue", SUM(ContributionTable[Amount]),
        "ContributionCount", COUNTROWS(ContributionTable)
    )
    VAR SortedByRevenue = ORDERBY(RevenueByCampaign, TotalRevenue, DESC)
    RETURN
    GENERATE(SortedByRevenue, ALL)
    """
    
    return client.execute(query, model_id="FinancialMetricsModel")
```

#### Get Year-to-Date Revenue

```python
def get_ytd_revenue() -> float:
    """Calculate year-to-date revenue"""
    query = """
    EVALUATE
    VAR YTDRevenue = CALCULATE(
        SUM(ContributionTable[Amount]),
        DATESBETWEEN(
            ContributionTable[ContributionDate],
            DATE(YEAR(TODAY()), 1, 1),
            TODAY()
        )
    )
    RETURN
    YTDRevenue
    """
    
    result = client.execute(query, model_id="FinancialMetricsModel")
    return result[0] if result else 0.0
```

#### Get Revenue Forecast

```python
def get_revenue_forecast(months_ahead: int = 6) -> list:
    """Generate revenue forecast for the next N months"""
    query = f"""
    EVALUATE
    VAR HistoricalData = GROUPBY(
        ContributionTable,
        FORMAT(ContributionTable[ContributionDate], "yyyy-MM"),
        "TotalRevenue", SUM(ContributionTable[Amount])
    )
    VAR Forecast = FORECAST(
        HistoricalData[TotalRevenue],
        {months_ahead},
        0.95  // Confidence interval
    )
    RETURN
    Forecast
    """
    
    return client.execute(query, model_id="FinancialMetricsModel")
```

## ⚡ Performance Optimization

### Query Caching

```python
from mcp_framework.fabric import SemanticModelClient

# Enable caching
client = SemanticModelClient(
    workspace_id="your-workspace-id",
    cache_enabled=True,
    cache_ttl=300  # 5 minutes
)

# First query - fetches from Fabric
result1 = client.execute(query, model_id="DonorManagementModel")

# Second query - returns cached result (if within TTL)
result2 = client.execute(query, model_id="DonorManagementModel")
```

### Batch Queries

```python
# Execute multiple queries in a single batch
queries = [
    {
        "query": "EVALUATE DonorTable",
        "model_id": "DonorManagementModel"
    },
    {
        "query": "EVALUATE ContributionTable",
        "model_id": "FinancialMetricsModel"
    }
]

results = client.execute_batch(queries)

# results[0] contains first query result
# results[1] contains second query result
```

### Pagination

```python
# Query with pagination for large result sets
def get_all_donors_page(page_size: int = 1000, page_number: int = 1) -> list:
    """Retrieve donors with pagination"""
    skip = (page_number - 1) * page_size
    
    query = f"""
    EVALUATE
    VAR AllDonors = DonorTable
    VAR PaginatedDonors = SKIP(AllDonors, {skip})
    VAR PageDonors = TOPN(PaginatedDonors, {page_size})
    RETURN
    GENERATE(PageDonors, ALL)
    """
    
    return client.execute(query, model_id="DonorManagementModel")

# Get all donors (handles pagination automatically)
def get_all_donors() -> list:
    """Retrieve all donors with automatic pagination"""
    all_donors = []
    page = 1
    page_size = 1000
    
    while True:
        donors = get_all_donors_page(page_size, page)
        if not donors:
            break
        all_donors.extend(donors)
        page += 1
    
    return all_donors
```

## 🔐 Security

### Row-Level Security

Semantic models support row-level security (RLS) defined in Fabric:

```python
# Query with RLS automatically applied
# The user's permissions determine which rows they can see
query = """
EVALUATE
DonorTable
"""

# RLS is automatically enforced by Fabric
result = client.execute(query, model_id="DonorManagementModel")
```

### Secure Query Parameters

```python
from mcp_framework.fabric import escape_dax_value

# Always escape user input to prevent DAX injection
def get_donor_by_name_safe(donor_name: str) -> list:
    """Safely query by donor name"""
    safe_name = escape_dax_value(donor_name)
    
    query = f"""
    EVALUATE
    VAR Donors = FILTER(DonorTable, DonorTable[DonorName] = {safe_name})
    RETURN
    GENERATE(Donors, ALL)
    """
    
    return client.execute(query, model_id="DonorManagementModel")
```

## 🛡️ Error Handling

### Common Errors

```python
from mcp_framework.error_handling import MCPError, ErrorCodes
from mcp_framework.fabric import FabricError

try:
    result = client.execute(query, model_id="DonorManagementModel")
except FabricError as e:
    # Handle Fabric-specific errors
    if e.error_code == "MODEL_NOT_FOUND":
        raise MCPError(
            error_code=ErrorCodes.MODEL_NOT_FOUND,
            message=f"Semantic model not found: {model_id}",
            category="Configuration"
        )
    elif e.error_code == "PERMISSION_DENIED":
        raise MCPError(
            error_code=ErrorCodes.ACCESS_DENIED,
            message="Access denied to semantic model",
            category="Authorization"
        )
    else:
        raise MCPError(
            error_code=ErrorCodes.FABRIC_ERROR,
            message=f"Fabric error: {str(e)}",
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
from mcp_framework.fabric import FabricError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=(FabricError, ConnectionError)
)
def execute_query_with_retry(query: str, model_id: str) -> list:
    """Execute query with automatic retry"""
    return client.execute(query, model_id=model_id)
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
            "first_contribution": row.get("FirstContributionDate"),
            "last_contribution": row.get("LastContributionDate"),
            "status": row.get("Status", "Active")
        })
    
    return processed
```

### Data Transformation

```python
import pandas as pd

def query_to_dataframe(query: str, model_id: str) -> pd.DataFrame:
    """Execute query and return results as DataFrame"""
    result = client.execute(query, model_id=model_id)
    return pd.DataFrame(result)

# Example usage
df = query_to_dataframe("EVALUATE DonorTable", "DonorManagementModel")
print(df.head())
print(df.describe())
```

### Aggregation and Analysis

```python
def analyze_donor_portfolio(result: list) -> dict:
    """Analyze donor portfolio from query results"""
    if not result:
        return {"status": "no_data"}
    
    # Calculate statistics
    total_donors = len(result)
    total_contributions = sum(float(row.get("TotalContributions", 0)) for row in result)
    average_contributions = total_contributions / total_donors if total_donors > 0 else 0
    
    # Find top donors
    sorted_donors = sorted(result, key=lambda x: float(x.get("TotalContributions", 0)), reverse=True)
    top_10 = sorted_donors[:10]
    
    return {
        "status": "success",
        "total_donors": total_donors,
        "total_contributions": total_contributions,
        "average_contributions": average_contributions,
        "top_10_donors": top_10
    }
```

## 🧪 Testing

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock
from mcp_framework.fabric import SemanticModelClient

def test_semantic_model_query():
    """Test semantic model query execution"""
    with patch('mcp_framework.fabric.SemanticModelClient') as mock_client:
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.execute.return_value = [
            {"DonorID": "D001", "DonorName": "Test Donor", "TotalContributions": 10000}
        ]
        mock_client.return_value = mock_instance
        
        # Execute query
        client = SemanticModelClient(workspace_id="test-workspace")
        result = client.execute("EVALUATE DonorTable", model_id="DonorModel")
        
        # Assertions
        assert len(result) == 1
        assert result[0]["DonorID"] == "D001"
        assert result[0]["DonorName"] == "Test Donor"
```

### Integration Tests

```python
@pytest.mark.integration
def test_fabric_integration():
    """Test integration with actual Fabric workspace"""
    # This test requires actual Fabric credentials
    client = SemanticModelClient(
        tenant_id="test-tenant-id",
        workspace_id="test-workspace-id"
    )
    
    # Test simple query
    result = client.execute("EVALUATE TOPN(DonorTable, 10)", model_id="DonorModel")
    assert isinstance(result, list)
    assert len(result) <= 10
```

## 📈 Monitoring

### Query Metrics

```python
from mcp_framework.telemetry import TelemetryClient

telemetry = TelemetryClient()

# Track query execution
@telemetry.track_operation("fabric.query")
def execute_tracked_query(query: str, model_id: str) -> list:
    """Execute query with telemetry tracking"""
    start_time = time.time()
    try:
        result = client.execute(query, model_id=model_id)
        duration = time.time() - start_time
        
        # Track metrics
        telemetry.track_metric("fabric.query.duration", duration * 1000)  # ms
        telemetry.track_metric("fabric.query.rows", len(result))
        
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
def log_query_performance(query: str, model_id: str, result: list, duration: float):
    """Log query performance metrics"""
    logger.info(
        "Fabric query executed",
        extra={
            "model_id": model_id,
            "rows_returned": len(result),
            "duration_ms": duration * 1000,
            "query_length": len(query)
        }
    )
```

## 🛠️ Best Practices

### Query Best Practices

1. **⭐ Use Semantic Models** - Always query through semantic models, not direct tables
2. **⭐ Filter Early** - Apply filters as early as possible in your queries
3. **⭐ Limit Results** - Use TOPN or LIMIT to restrict result sizes
4. **⭐ Aggregate at Source** - Perform aggregations in the query, not in Python
5. **⭐ Use Variables** - Use DAX variables for complex expressions
6. **⭐ Avoid SELECT *** - Only select the columns you need

### Performance Best Practices

1. **⭐ Enable Caching** - Cache frequently used queries
2. **⭐ Use Pagination** - Implement pagination for large result sets
3. **⭐ Batch Queries** - Combine multiple queries into batches when possible
4. **⭐ Monitor Query Performance** - Track and optimize slow queries
5. **⭐ Use Indexed Columns** - Filter on indexed columns for better performance

### Security Best Practices

1. **⭐ Always Escape Inputs** - Prevent DAX injection by escaping user inputs
2. **⭐ Use RLS** - Leverage Fabric's row-level security
3. **⭐ Validate Results** - Check query results for expected structure
4. **⭐ Handle Errors Gracefully** - Never expose sensitive information in errors
5. **⭐ Use Least Privilege** - Grant minimum required permissions to service principals

## 🛠️ Troubleshooting

### Common Issues

#### Model Not Found

**Error**: `FabricError: Model 'DonorModel' not found in workspace 'workspace-id'`

**Solution**:
```python
# Verify the model exists in the workspace
models = client.list_models()
print(f"Available models: {models}")

# Check the model ID is correct
# Model IDs are case-sensitive
```

#### Permission Denied

**Error**: `FabricError: Permission denied to access model 'DonorModel'`

**Solution**:
```bash
# Grant permissions to the service principal
az fabric workspace add-user \
  --workspace workspace-id \
  --user service-principal-id \
  --role Reader

# Or use Managed Identity
az fabric workspace add-user \
  --workspace workspace-id \
  --user managed-identity-id \
  --role Reader
```

#### Query Timeout

**Error**: `FabricError: Query execution timed out after 30 seconds`

**Solution**:
```python
# Increase timeout
client = SemanticModelClient(
    workspace_id="your-workspace-id",
    timeout=60  # 60 seconds
)

# Or optimize the query
# - Reduce result set size
# - Simplify complex calculations
# - Use filters to limit data
```

#### Connection Failed

**Error**: `FabricError: Failed to connect to Fabric workspace`

**Solution**:
```bash
# Verify Azure authentication
az login
az account set --subscription your-subscription-id

# Check network connectivity
# Verify service principal has access

# Test connection
python -c "from mcp_framework.fabric import SemanticModelClient; c = SemanticModelClient(workspace_id='test'); print(c.test_connection())"
```

## 📚 Next Steps

1. **[Warehouse Queries](warehouse-queries.md)** - Learn about warehouse querying
2. **[Lakehouse Operations](lakehouse-operations.md)** - Explore lakehouse data operations
3. **[Fabric Connectivity Module](../modules/fabric-connectivity.md)** - Deep dive into Fabric integration
4. **[Donor Management Example](donor-management.md)** - Complete domain example

## 🔗 Related Documentation

- [Microsoft Fabric Semantic Models](https://learn.microsoft.com/en-us/fabric/data-engineering/semantic-model-overview)
- [DAX Language Reference](https://learn.microsoft.com/en-us/dax/dax-function-reference)
- [Fabric REST API](https://learn.microsoft.com/en-us/rest/api/fabric/)
- [MCP Platform Fabric Module](../modules/fabric-connectivity.md)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
