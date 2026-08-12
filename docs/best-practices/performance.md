# ⚡ Performance Best Practices

Comprehensive performance optimization strategies and recommendations for building high-performance MCP services using the MCP Platform Framework.

## 🎯 Overview

Performance is critical for MCP services that serve business users and integrate with other systems. This guide provides best practices for:

- **Query Optimization**: Efficient data access and query design
- **Caching Strategies**: Intelligent caching for better performance
- **Resource Management**: Efficient use of system resources
- **Scalability**: Designing for horizontal and vertical scaling
- **Monitoring**: Performance monitoring and optimization

## 🏗️ Query Optimization Best Practices

### ✅ Use Semantic Models for Business Metrics

**⭐ Best Practice**: Always use semantic models instead of direct table access for business metrics.

```python
from platform.connectivity import FabricClient

fabric = FabricClient()

# Good: Use semantic models for business metrics
semantic_model = fabric.get_semantic_model("DonorAnalytics")
results = await semantic_model.execute("EVALUATE DonorPortfolioHealth")

# Bad: Direct table access
warehouse = fabric.get_warehouse("DonorDataWarehouse")
results = await warehouse.execute_sql("SELECT * FROM gold_donor_metrics")
```

**Why**: Semantic models provide:
- Pre-aggregated metrics for better performance
- Business logic encapsulation
- Consistent calculations across the organization
- Optimized query plans

### ✅ Optimize SQL Queries

**⭐ Best Practice**: Write efficient SQL queries with proper indexing and filtering.

```python
# Good: Optimized SQL query
query = """
    SELECT 
        d.donor_id,
        d.name,
        SUM(t.amount) as total_contribution,
        COUNT(t.transaction_id) as transaction_count
    FROM donors d
    JOIN transactions t ON d.donor_id = t.donor_id
    WHERE d.status = 'active'
        AND t.date >= '2024-01-01'
    GROUP BY d.donor_id, d.name
    ORDER BY total_contribution DESC
    LIMIT 100
"""

# Bad: Inefficient query
query = """
    SELECT * FROM donors
"""  # Retrieves all columns and rows
```

### ✅ Use Appropriate Query Types

**⭐ Best Practice**: Use the right Fabric endpoint for each query type.

```python
from platform.connectivity import FabricClient

fabric = FabricClient()

# Good: Use semantic models for business metrics
semantic_model = fabric.get_semantic_model("DonorAnalytics")
business_metrics = await semantic_model.execute("EVALUATE RevenueForecast")

# Good: Use warehouses for SQL queries
warehouse = fabric.get_warehouse("DonorDataWarehouse")
sql_results = await warehouse.execute_sql("SELECT * FROM transactions WHERE date > '2024-01-01'")

# Good: Use lakehouses for big data processing
lakehouse = fabric.get_lakehouse("DonorDataLakehouse")
spark_results = await lakehouse.execute_spark("SELECT * FROM large_dataset")
```

### ✅ Implement Query Pagination

**⭐ Best Practice**: Use pagination for large result sets.

```python
# Good: Paginated query
async def get_donors_page(page: int = 1, page_size: int = 100):
    offset = (page - 1) * page_size
    query = f"""
        SELECT donor_id, name, total_contribution
        FROM donors
        WHERE status = 'active'
        ORDER BY total_contribution DESC
        OFFSET {offset} ROWS
        FETCH NEXT {page_size} ROWS ONLY
    """
    return await warehouse.execute_sql(query)

# Bad: No pagination - can return too much data
async def get_all_donors():
    query = "SELECT * FROM donors"  # Can return millions of rows
    return await warehouse.execute_sql(query)
```

### ✅ Use Parameterized Queries

**⭐ Best Practice**: Always use parameterized queries to prevent SQL injection.

```python
# Good: Parameterized query
async def get_donor_by_id(donor_id: str):
    query = "SELECT * FROM donors WHERE donor_id = @donor_id"
    parameters = {"donor_id": donor_id}
    return await warehouse.execute_sql(query, parameters)

# Bad: String concatenation - SQL injection risk!
async def get_donor_by_id(donor_id: str):
    query = f"SELECT * FROM donors WHERE donor_id = '{donor_id}'"  # SQL injection risk!
    return await warehouse.execute_sql(query)
```

## 🚀 Caching Best Practices

### ✅ Implement Multi-Level Caching

**⭐ Best Practice**: Use caching at multiple levels for optimal performance.

```python
from platform.cache import MultiLevelCache

# Good: Multi-level caching
cache = MultiLevelCache(
    memory_cache_ttl=300,      # 5 minutes in memory
    distributed_cache_ttl=3600, # 1 hour in Redis
    storage_cache_ttl=86400    # 1 day in blob storage
)

# Check cache first
async def get_donor_portfolio(donor_id: str):
    cache_key = f"donor_portfolio:{donor_id}"
    
    # Try memory cache
    result = cache.get_memory(cache_key)
    if result:
        return result
    
    # Try distributed cache
    result = await cache.get_distributed(cache_key)
    if result:
        return result
    
    # Try storage cache
    result = await cache.get_storage(cache_key)
    if result:
        return result
    
    # Get from source
    result = await donor_service.get_portfolio(donor_id)
    
    # Cache at all levels
    cache.set_memory(cache_key, result)
    await cache.set_distributed(cache_key, result)
    await cache.set_storage(cache_key, result)
    
    return result
```

### ✅ Cache Frequently Accessed Data

**⭐ Best Practice**: Cache data that is accessed frequently but changes infrequently.

```python
from platform.cache import CacheService

cache = CacheService()

# Good: Cache frequently accessed data
@cache.cached(ttl=300, key_func=lambda donor_id: f"donor:{donor_id}")
async def get_donor_data(donor_id: str):
    return await donor_service.get_donor(donor_id)

# Good: Cache expensive computations
@cache.cached(ttl=3600, key_func=lambda: "donor_analytics_all")
async def get_all_donor_analytics():
    return await analytics_service.compute_all_analytics()
```

### ✅ Use Appropriate Cache TTLs

**⭐ Best Practice**: Set cache TTLs based on data volatility and freshness requirements.

```python
# Good: Appropriate cache TTLs
@cache.cached(ttl=60)           # 1 minute - highly volatile data
async def get_realtime_metrics():
    return await metrics_service.get_realtime()

@cache.cached(ttl=300)          # 5 minutes - moderately volatile
async def get_donor_portfolio(donor_id: str):
    return await donor_service.get_portfolio(donor_id)

@cache.cached(ttl=3600)         # 1 hour - relatively stable
async def get_donor_history(donor_id: str):
    return await donor_service.get_history(donor_id)

@cache.cached(ttl=86400)        # 1 day - very stable
async def get_donor_profile(donor_id: str):
    return await donor_service.get_profile(donor_id)
```

### ✅ Implement Cache Invalidation

**⭐ Best Practice**: Invalidate cache when underlying data changes.

```python
from platform.cache import CacheService

cache = CacheService()

# Good: Cache invalidation on data changes
async def update_donor(donor_id: str, data: dict):
    # Update donor
    result = await donor_service.update_donor(donor_id, data)
    
    # Invalidate cache
    await cache.invalidate(f"donor:{donor_id}")
    await cache.invalidate(f"donor_portfolio:{donor_id}")
    await cache.invalidate_pattern(f"donor_*:{donor_id}")
    
    return result
```

### ✅ Use Cache for External API Calls

**⭐ Best Practice**: Cache results from external APIs to reduce latency and costs.

```python
from platform.cache import CacheService

cache = CacheService()

# Good: Cache external API calls
@cache.cached(ttl=300, key_func=lambda donor_id: f"external_api:donor:{donor_id}")
async def get_external_donor_data(donor_id: str):
    # Call external API
    response = await external_api.get_donor_data(donor_id)
    return response.json()
```

## ⚙️ Resource Management Best Practices

### ✅ Use Connection Pooling

**⭐ Best Practice**: Use connection pooling for database and external service connections.

```python
from platform.connectivity import FabricConfig

# Good: Connection pooling configuration
config = FabricConfig(
    connection_pooling=True,
    max_connections=20,        # Maximum connections in pool
    connection_timeout=30,     # Connection timeout in seconds
    max_retries=3,             # Maximum retry attempts
    retry_delay=1.0            # Delay between retries in seconds
)
```

### ✅ Implement Circuit Breakers

**⭐ Best Practice**: Use circuit breakers to prevent cascading failures.

```python
from platform.resilience import CircuitBreaker

# Good: Circuit breaker for external service calls
circuit_breaker = CircuitBreaker(
    failure_threshold=5,      # Number of failures before opening
    recovery_timeout=60,      # Time before trying again (seconds)
    expected_exception=ExternalServiceError
)

@circuit_breaker.protect
async def call_external_service(data: dict):
    return await external_service.process(data)
```

### ✅ Use Async I/O for Better Throughput

**⭐ Best Practice**: Use async/await for I/O-bound operations to improve throughput.

```python
import aiohttp

# Good: Async HTTP requests
async def fetch_multiple_donors(donor_ids: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for donor_id in donor_ids:
            task = fetch_donor(session, donor_id)
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)
        return results

async def fetch_donor(session: aiohttp.ClientSession, donor_id: str):
    url = f"https://api.example.com/donors/{donor_id}"
    async with session.get(url) as response:
        return await response.json()
```

### ✅ Limit Concurrent Operations

**⭐ Best Practice**: Limit concurrent operations to prevent resource exhaustion.

```python
import asyncio

# Good: Semaphore for limiting concurrent operations
concurrency_semaphore = asyncio.Semaphore(10)  # Max 10 concurrent operations

async def process_donor(donor_id: str):
    async with concurrency_semaphore:
        # Only 10 of these can run concurrently
        return await donor_service.process(donor_id)

async def process_all_donors(donor_ids: List[str]):
    tasks = [process_donor(donor_id) for donor_id in donor_ids]
    return await asyncio.gather(*tasks)
```

### ✅ Optimize Memory Usage

**⭐ Best Practice**: Be mindful of memory usage, especially with large datasets.

```python
# Good: Stream large datasets instead of loading into memory
async def process_large_dataset():
    # Use streaming to process data in chunks
    async for chunk in data_service.stream_data():
        for item in chunk:
            await process_item(item)
        # Memory is freed after each chunk

# Bad: Load entire dataset into memory
async def process_large_dataset():
    # Load all data into memory - can cause OOM
    all_data = await data_service.get_all_data()
    for item in all_data:
        await process_item(item)
```

## 📈 Scalability Best Practices

### ✅ Design for Horizontal Scaling

**⭐ Best Practice**: Design services to scale horizontally by adding more instances.

```python
# Good: Stateless service design for horizontal scaling
class DonorService:
    def __init__(self):
        # No instance-specific state
        self.client = FabricClient()
    
    async def get_donor(self, donor_id: str):
        # All state is external (database, cache, etc.)
        return await self.client.get_warehouse("DonorData").execute_sql(
            "SELECT * FROM donors WHERE donor_id = @donor_id",
            {"donor_id": donor_id}
        )
```

### ✅ Use Azure Functions for Auto-Scaling

**⭐ Best Practice**: Deploy MCP services as Azure Functions for automatic scaling.

```python
import azure.functions as func
from platform.framework import MCPFramework

# Good: Azure Function with auto-scaling
framework = MCPFramework(domain="DonorManagement")
framework.initialize()

@app.route(route="donors/{donor_id}")
@authenticated_tool
@track_tool_telemetry
async def get_donor(req: func.HttpRequest) -> func.HttpResponse:
    donor_id = req.route_params.get("donor_id")
    result = await donor_service.get_donor(donor_id)
    return func.HttpResponse(f"Donor: {result}")
```

### ✅ Implement Rate Limiting

**⭐ Best Practice**: Implement rate limiting to prevent abuse and ensure fair usage.

```python
from platform.rate_limiting import RateLimiter

# Good: Rate limiting
rate_limiter = RateLimiter(
    max_requests=100,      # Max requests
    time_window=60,       # Per 60 seconds
    key_func=lambda req: req.headers.get("X-User-ID", req.ip)
)

@app.route("/api/donors")
@rate_limiter.limit
async def get_donors(req: func.HttpRequest):
    # This endpoint is rate limited
    return await donor_service.get_all_donors()
```

### ✅ Use Queue-Based Processing for Heavy Workloads

**⭐ Best Practice**: Use message queues for heavy or long-running operations.

```python
from platform.messaging import QueueClient

queue = QueueClient("donor-processing")

# Good: Queue-based processing
async def process_donor_async(donor_id: str, data: dict):
    # Add to queue instead of processing immediately
    await queue.send_message({
        "donor_id": donor_id,
        "data": data,
        "operation": "update"
    })
    return {"status": "queued", "message": "Processing started"}

# Worker function
async def process_queue_messages():
    async for message in queue.receive_messages():
        donor_id = message["donor_id"]
        data = message["data"]
        operation = message["operation"]
        
        if operation == "update":
            await donor_service.update_donor(donor_id, data)
        
        await queue.complete_message(message)
```

## 📊 Performance Monitoring Best Practices

### ✅ Monitor Key Performance Metrics

**⭐ Best Practice**: Track performance metrics that matter to your business.

```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

# Good: Track key performance metrics
telemetry.track_metric("RequestDuration", duration_ms)
telemetry.track_metric("DonorsProcessed", count)
telemetry.track_metric("CacheHitRate", hit_rate)
telemetry.track_metric("QueryExecutionTime", execution_time_ms)
```

### ✅ Set Up Performance Alerts

**⭐ Best Practice**: Configure alerts for performance degradation.

```python
# Good: Performance alert configuration
# In your monitoring configuration

alerts:
  - name: "HighRequestLatency"
    condition: "RequestDuration > 1000"  # 1 second
    severity: "Warning"
    action: "NotifyTeam"
    
  - name: "VeryHighRequestLatency"
    condition: "RequestDuration > 5000"  # 5 seconds
    severity: "Critical"
    action: "NotifyTeam,ScaleUp"
    
  - name: "LowCacheHitRate"
    condition: "CacheHitRate < 0.5"  # Less than 50%
    severity: "Warning"
    action: "NotifyTeam"
```

### ✅ Use Application Insights for Deep Monitoring

**⭐ Best Practice**: Configure Application Insights for comprehensive monitoring.

```python
from platform.telemetry import TelemetryConfig

# Good: Application Insights configuration
config = TelemetryConfig(
    app_insights_enabled=True,
    connection_string="InstrumentationKey=...",
    track_tool_execution=True,
    track_requests=True,
    track_exceptions=True,
    track_dependencies=True,
    sampling_percentage=100.0,  # Sample all telemetry in development
    slow_request_threshold_ms=1000.0,  # 1 second
    very_slow_request_threshold_ms=5000.0  # 5 seconds
)
```

### ✅ Profile Your Code

**⭐ Best Practice**: Regularly profile your code to identify performance bottlenecks.

```python
import cProfile
import pstats
from io import StringIO

# Good: Code profiling
def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    
    # Print profiling results
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    
    print(stream.getvalue())
    
    return result

# Profile a function
result = profile_function(get_donor_analytics, donor_id="12345")
```

## 📋 Performance Checklist

### ✅ Pre-Deployment Performance Checklist

- [ ] All queries use semantic models where appropriate
- [ ] SQL queries are optimized with proper indexing and filtering
- [ ] Caching is implemented for frequently accessed data
- [ ] Cache TTLs are appropriately set based on data volatility
- [ ] Connection pooling is enabled for database connections
- [ ] Circuit breakers are implemented for external service calls
- [ ] Async I/O is used for I/O-bound operations
- [ ] Concurrent operations are limited to prevent resource exhaustion
- [ ] Memory usage is optimized for large datasets
- [ ] Service design supports horizontal scaling

### ✅ Runtime Performance Checklist

- [ ] Performance metrics are being tracked and monitored
- [ ] Cache hit rates are acceptable (> 70% for frequently accessed data)
- [ ] Query execution times are within expected ranges
- [ ] No memory leaks or excessive memory usage
- [ ] Connection pools are not exhausted
- [ ] Circuit breakers are working correctly
- [ ] Rate limiting is preventing abuse
- [ ] Queue-based processing is handling heavy workloads

## 🚨 Common Performance Pitfalls

### ❌ N+1 Query Problem

**Problem**: Executing one query per item in a collection, leading to many round trips.

**Solution**: Use batch queries or joins to reduce the number of queries.

```python
# Bad: N+1 query problem
async def get_donors_with_transactions(donor_ids: List[str]):
    donors = []
    for donor_id in donor_ids:
        donor = await donor_service.get_donor(donor_id)
        transactions = await transaction_service.get_transactions(donor_id)
        donors.append({**donor, "transactions": transactions})
    return donors

# Good: Batch query
async def get_donors_with_transactions(donor_ids: List[str]):
    # Get all donors in one query
    donors = await donor_service.get_donors(donor_ids)
    
    # Get all transactions in one query
    transactions = await transaction_service.get_transactions_by_donors(donor_ids)
    
    # Combine results
    for donor in donors:
        donor["transactions"] = [t for t in transactions if t["donor_id"] == donor["donor_id"]]
    
    return donors
```

### ❌ Large Result Sets

**Problem**: Retrieving too much data in a single query.

**Solution**: Use pagination and filtering to limit result sets.

### ❌ Missing Indexes

**Problem**: Queries are slow due to missing database indexes.

**Solution**: Add appropriate indexes for frequently queried columns.

### ❌ No Caching

**Problem**: Repeatedly fetching the same data without caching.

**Solution**: Implement caching for frequently accessed data.

### ❌ Synchronous I/O

**Problem**: Using synchronous I/O operations that block the event loop.

**Solution**: Use async/await for all I/O operations.

### ❌ Memory Leaks

**Problem**: Accumulating data in memory without proper cleanup.

**Solution**: Use streaming and proper memory management.

## 📚 Related Documentation

- [Telemetry API](../api-reference/telemetry.md) - Telemetry and monitoring services
- [Fabric Connectivity API](../api-reference/connectivity.md) - Fabric integration
- [Performance Best Practices](../best-practices/performance.md) - This document
- [Monitoring Best Practices](monitoring.md) - Monitoring and observability

---

**🎉 Ready to optimize your MCP services?** Implement these performance best practices to build fast, scalable, and efficient services.

**Need more details?** Check the specific API references for implementation details and advanced performance patterns.