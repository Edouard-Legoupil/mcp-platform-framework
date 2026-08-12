# 📊 Telemetry Module

The Telemetry Module provides automatic, comprehensive telemetry collection for all MCP tool calls, ensuring observability and monitoring across the entire platform.

## 🎯 Overview

The Telemetry Module handles:
- **Automatic Instrumentation**: Every tool call generates telemetry automatically
- **Standardized Metrics**: Consistent format across all domains
- **Context Propagation**: Request context flows through all layers
- **Performance Monitoring**: Duration, status, token usage, and resource consumption tracking

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Telemetry Module                │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Metric         │  │  Trace          │ │
│  │  Collection     │  │  Collection     │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Log Collection  │  │  Context        │ │
│  │                 │  │  Propagation     │ │
│  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Basic Usage

```python
from platform.telemetry import telemetry

@telemetry.capture_tool_metrics
def get_donor_pipeline():
    # Domain logic - telemetry automatically captured
    return pipeline_service.get_health()
```

### Configuration

```python
# config/telemetry.py
from platform.telemetry.config import TelemetryConfig

TELEMETRY_CONFIG = TelemetryConfig(
    # Application Insights
    app_insights_enabled=True,
    app_insights_connection_string="InstrumentationKey=...",
    
    # Log Analytics
    log_analytics_enabled=True,
    log_analytics_workspace_id="your-workspace-id",
    log_analytics_workspace_key="your-workspace-key",
    
    # Custom endpoints
    custom_endpoints=[
        "https://telemetry.my-org.org/api/metrics"
    ],
    
    # Sampling
    sampling_rate=1.0,  # 100% sampling
    
    # Batch processing
    batch_enabled=True,
    batch_size=100,
    batch_interval=5  # seconds
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Application Insights
APP_INSIGHTS_ENABLED=true
APP_INSIGHTS_CONNECTION_STRING=InstrumentationKey=...

# Log Analytics
LOG_ANALYTICS_ENABLED=true
LOG_ANALYTICS_WORKSPACE_ID=your-workspace-id
LOG_ANALYTICS_WORKSPACE_KEY=your-workspace-key

# Telemetry Settings
TELEMETRY_SAMPLING_RATE=1.0
TELEMETRY_BATCH_ENABLED=true
TELEMETRY_BATCH_SIZE=100
TELEMETRY_BATCH_INTERVAL=5
```

### Configuration File

```yaml
# config/telemetry.yaml
telemetry:
  application_insights:
    enabled: true
    connection_string: ${APP_INSIGHTS_CONNECTION_STRING}
    
  log_analytics:
    enabled: true
    workspace_id: ${LOG_ANALYTICS_WORKSPACE_ID}
    workspace_key: ${LOG_ANALYTICS_WORKSPACE_KEY}
    
  custom_endpoints:
    - "https://telemetry.my-org.org/api/metrics"
    
  sampling:
    rate: 1.0
    
  batch:
    enabled: true
    size: 100
    interval: 5
    
  metrics:
    enabled: true
    retention_days: 90
    
  traces:
    enabled: true
    retention_days: 30
    
  logs:
    enabled: true
    retention_days: 365
```

## 🎯 API Reference

### Decorators

#### `@capture_tool_metrics`

Automatically captures telemetry for a tool.

```python
from platform.telemetry import capture_tool_metrics

@capture_tool_metrics
def get_donor_data(donor_id: str):
    # Telemetry automatically captured
    return donor_service.get(donor_id)

# With custom tool name
@capture_tool_metrics(tool_name="GetDonorData")
def get_donor_data(donor_id: str):
    pass
```

**Parameters:**
- `tool_name` (str, optional): Custom tool name
- `domain` (str, optional): Custom domain name
- `classification` (str, optional): Data classification level

#### `@capture_tool_metrics_async`

Async version of `@capture_tool_metrics`.

```python
from platform.telemetry import capture_tool_metrics_async

@capture_tool_metrics_async
async def get_donor_data_async(donor_id: str):
    # Async telemetry capture
    return await donor_service.get(donor_id)
```

### Functions

#### `get_telemetry_client()`

Gets the telemetry client instance.

```python
from platform.telemetry import get_telemetry_client

client = get_telemetry_client()
```

**Returns:**
- `TelemetryClient`: The telemetry client instance

#### `track_tool_call(tool, duration, status, **kwargs)`

Manually track a tool call.

```python
from platform.telemetry import track_tool_call

track_tool_call(
    tool="GetDonorPortfolioHealth",
    duration=450,
    status="Success",
    domain="DonorManagement",
    requester="john.doe@my-org.org"
)
```

**Parameters:**
- `tool` (str): Tool name
- `duration` (float): Duration in milliseconds
- `status` (str): Status ("Success", "Error", etc.)
- `**kwargs`: Additional telemetry properties

#### `track_event(name, properties, measurements)`

Track a custom event.

```python
from platform.telemetry import track_event

track_event(
    name="DonorDataAccessed",
    properties={"donor_id": "DON-12345", "classification": "CONFIDENTIAL"},
    measurements={"data_size": 1024, "processing_time": 50}
)
```

**Parameters:**
- `name` (str): Event name
- `properties` (dict, optional): Event properties
- `measurements` (dict, optional): Event measurements

#### `track_exception(exception, properties)`

Track an exception.

```python
from platform.telemetry import track_exception

try:
    # Some operation
    pass
except Exception as e:
    track_exception(
        e,
        properties={"operation": "get_donor", "donor_id": "DON-12345"}
    )
    raise
```

**Parameters:**
- `exception` (Exception): The exception to track
- `properties` (dict, optional): Additional properties

#### `track_metric(name, value, properties)`

Track a custom metric.

```python
from platform.telemetry import track_metric

track_metric(
    name="DonorCount",
    value=1500,
    properties={"region": "EMEA"}
)
```

**Parameters:**
- `name` (str): Metric name
- `value` (float): Metric value
- `properties` (dict, optional): Metric properties

### Classes

#### `TelemetryData`

Represents telemetry data for a tool call.

```python
from platform.telemetry import TelemetryData

# Create telemetry data
telemetry = TelemetryData(
    tool="GetDonorPortfolioHealth",
    domain="DonorManagement",
    duration_ms=450,
    status="Success",
    requester_identity="john.doe@my-org.org",
    requester_roles=["donor_analyst"],
    requester_permissions=["donor.read", "donor.analytics"],
    environment="Production",
    workspace="DER-Analytics",
    token_usage={"input_tokens": 150, "output_tokens": 250}
)

# Convert to dictionary
telemetry_dict = telemetry.to_dict()
```

**Attributes:**
- `tool` (str): Tool name
- `domain` (str): Domain name
- `duration_ms` (float): Duration in milliseconds
- `status` (str): Status
- `requester_identity` (str): Requester identity
- `requester_roles` (List[str]): Requester roles
- `requester_permissions` (List[str]): Requester permissions
- `environment` (str): Environment
- `workspace` (str): Workspace
- `timestamp` (datetime): Timestamp
- `request_id` (str): Request ID
- `correlation_id` (str): Correlation ID
- `token_usage` (dict): Token usage information
- `error_code` (str): Error code (if error)
- `error_message` (str): Error message (if error)

**Methods:**
- `to_dict()`: Convert to dictionary
- `to_json()`: Convert to JSON string

#### `TelemetryClient`

The main telemetry client.

```python
from platform.telemetry import TelemetryClient

# Create client
client = TelemetryClient(
    app_insights_enabled=True,
    connection_string="InstrumentationKey=..."
)

# Track tool call
client.track_tool_call(
    tool="GetDonorData",
    duration=150,
    status="Success"
)

# Track event
client.track_event(
    name="DataAccessed",
    properties={"resource": "donor:DON-12345"}
)

# Flush telemetry
client.flush()
```

**Parameters:**
- `app_insights_enabled` (bool, optional): Enable Application Insights
- `connection_string` (str, optional): Application Insights connection string
- `log_analytics_enabled` (bool, optional): Enable Log Analytics
- `workspace_id` (str, optional): Log Analytics workspace ID
- `workspace_key` (str, optional): Log Analytics workspace key
- `custom_endpoints` (List[str], optional): Custom telemetry endpoints
- `sampling_rate` (float, optional): Sampling rate (0.0 to 1.0)
- `batch_enabled` (bool, optional): Enable batch processing
- `batch_size` (int, optional): Batch size
- `batch_interval` (int, optional): Batch interval in seconds

**Methods:**
- `track_tool_call(tool, duration, status, **kwargs)`: Track a tool call
- `track_event(name, properties, measurements)`: Track an event
- `track_exception(exception, properties)`: Track an exception
- `track_metric(name, value, properties)`: Track a metric
- `track_trace(message, severity, properties)`: Track a trace
- `flush()`: Flush telemetry data
- `close()`: Close the client

## 📊 Telemetry Structure

### Standard Telemetry Format

```json
{
  "tool": "GetDonorPortfolioHealth",
  "domain": "DonorManagement",
  "duration_ms": 450,
  "status": "Success",
  "requester": {
    "identity": "john.doe@my-org.org",
    "roles": ["donor_analyst"],
    "permissions": ["donor.read", "donor.analytics"]
  },
  "environment": "Production",
  "workspace": "DER-Analytics",
  "timestamp": "2026-05-01T10:30:00Z",
  "request_id": "req-20260501-103000-001",
  "correlation_id": "corr-20260501-100000-001",
  "token_usage": {
    "input_tokens": 150,
    "output_tokens": 250
  }
}
```

### Error Telemetry Format

```json
{
  "tool": "GetTopDonorContributions",
  "domain": "DonorManagement",
  "duration_ms": 50,
  "status": "Error",
  "requester": {
    "identity": "john.doe@my-org.org",
    "roles": ["donor_analyst"]
  },
  "environment": "Production",
  "timestamp": "2026-05-01T10:30:00Z",
  "error": {
    "code": "AUTHZ-002",
    "message": "Permission denied: finance.confidential required"
  }
}
```

## 📈 Monitoring and Metrics

### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Request Volume | Requests per minute | Varies | > 1000 RPM |
| Average Latency | End-to-end request time | < 500ms | > 1000ms |
| Error Rate | Percentage of failed requests | < 1% | > 5% |
| Token Usage | Tokens consumed per request | < 1000 | > 5000 |
| Cache Hit Rate | Percentage of cached requests | > 90% | < 70% |

### Application Insights Queries

```kusto
// Get request volume by tool
requests
| where cloud_RoleName == "mcp-platform"
| summarize count() by name
| order by count_ desc

// Get average latency by tool
requests
| where cloud_RoleName == "mcp-platform"
| summarize avg(duration) by name
| order by avg_duration desc

// Get error rate by tool
requests
| where cloud_RoleName == "mcp-platform"
| where success == false
| summarize count() by name
| order by count_ desc

// Get token usage by domain
traces
| where cloud_RoleName == "mcp-platform"
| where message contains "token_usage"
| extend token_usage = todynamic(customDimensions.token_usage)
| summarize sum(todouble(token_usage.input_tokens)) by domain
| order by sum_ desc
```

### Log Analytics Queries

```kusto
// Get telemetry data
Telemetry
| where TimeGenerated > ago(1d)
| summarize count() by Tool, Status
| order by count_ desc

// Get error details
Telemetry
| where TimeGenerated > ago(1d)
| where Status == "Error"
| project TimeGenerated, Tool, Domain, ErrorCode, ErrorMessage, Requester
| order by TimeGenerated desc

// Get performance metrics
Telemetry
| where TimeGenerated > ago(1d)
| summarize avg(DurationMs), max(DurationMs), min(DurationMs) by Tool
| order by avg_DurationMs desc
```

## 🚀 Best Practices

### ⭐ Use Automatic Instrumentation

Always use the `@capture_tool_metrics` decorator for automatic telemetry.

```python
# Good
@capture_tool_metrics
def get_donor_data(donor_id: str):
    pass

# Bad - Manual telemetry
@tool
def get_donor_data(donor_id: str):
    start = time.time()
    try:
        result = donor_service.get(donor_id)
        track_tool_call("get_donor_data", time.time() - start, "Success")
        return result
    except Exception as e:
        track_tool_call("get_donor_data", time.time() - start, "Error")
        raise
```

### ⭐ Include Context in Telemetry

Always include request context in telemetry.

```python
# Good - Context included
track_tool_call(
    tool="GetDonorData",
    duration=150,
    status="Success",
    domain="DonorManagement",
    requester=caller.identity,
    requester_roles=caller.roles
)

# Bad - Missing context
track_tool_call(
    tool="GetDonorData",
    duration=150,
    status="Success"
)
```

### ⭐ Track Token Usage

Always track token usage for LLM-powered tools.

```python
# Good - Token usage tracked
@capture_tool_metrics
def generate_report(prompt: str):
    result = llm_service.generate(prompt)
    return {
        "result": result,
        "token_usage": {
            "input_tokens": len(prompt.split()),
            "output_tokens": len(result.split())
        }
    }

# Bad - Token usage not tracked
@capture_tool_metrics
def generate_report(prompt: str):
    return llm_service.generate(prompt)
```

### ⭐ Use Sampling for High Volume

Use sampling to reduce telemetry volume for high-frequency tools.

```python
# Good - Sampling configured
config = TelemetryConfig(
    sampling_rate=0.1  # 10% sampling for high-volume tools
)

# Bad - No sampling
config = TelemetryConfig(
    sampling_rate=1.0  # 100% sampling - may be too much
)
```

### ⭐ Use Batch Processing

Enable batch processing for better performance.

```python
# Good - Batch processing enabled
config = TelemetryConfig(
    batch_enabled=True,
    batch_size=100,
    batch_interval=5
)

# Bad - No batch processing
config = TelemetryConfig(
    batch_enabled=False
)
```

### ⭐ Monitor Telemetry Health

Monitor telemetry collection health.

```python
# Good - Health monitoring
from platform.telemetry import TelemetryHealthMonitor

monitor = TelemetryHealthMonitor()

# Check if telemetry is being collected
is_healthy = await monitor.is_healthy()

# Get telemetry collection statistics
stats = await monitor.get_statistics()

# Bad - No health monitoring
# No monitoring of telemetry collection
```

## 🔍 Troubleshooting

### Common Issues

#### Telemetry Not Being Collected

**Symptoms:** No telemetry data in Application Insights or Log Analytics

**Causes:**
- Telemetry client not initialized
- Configuration missing or incorrect
- Network connectivity issues
- Sampling rate set to 0

**Solutions:**
1. Check configuration: `TELEMETRY_CONFIG`
2. Verify network connectivity to telemetry endpoints
3. Check sampling rate: `config.sampling_rate`
4. Enable debug logging: `TELEMETRY_DEBUG=true`

```python
# Debug telemetry
from platform.telemetry import get_telemetry_client

client = get_telemetry_client()
print(f"App Insights enabled: {client.app_insights_enabled}")
print(f"Log Analytics enabled: {client.log_analytics_enabled}")
print(f"Custom endpoints: {client.custom_endpoints}")
```

#### High Telemetry Volume

**Symptoms:** High costs, performance issues due to telemetry volume

**Causes:**
- Sampling rate too high
- Batch processing disabled
- Too many custom metrics

**Solutions:**
1. Reduce sampling rate: `config.sampling_rate = 0.1`
2. Enable batch processing: `config.batch_enabled = True`
3. Reduce custom metric collection
4. Filter out sensitive data

```python
# Reduce telemetry volume
config = TelemetryConfig(
    sampling_rate=0.1,  # 10% sampling
    batch_enabled=True,
    batch_size=200,
    batch_interval=10
)
```

#### Missing Context in Telemetry

**Symptoms:** Telemetry data missing requester information or other context

**Causes:**
- Context not being passed through the pipeline
- Decorators not properly applied
- Manual telemetry tracking without context

**Solutions:**
1. Ensure `@authenticated_tool` is applied before `@capture_tool_metrics`
2. Use the framework's pipeline for request processing
3. Pass context explicitly when tracking manually

```python
# Correct decorator order
@authenticated_tool
@capture_tool_metrics
def my_tool():
    pass

# Wrong decorator order
@capture_tool_metrics
@authenticated_tool
def my_tool():
    pass
```

## 📚 Examples

### Complete Telemetry Example

```python
from platform.auth import authenticated_tool
from platform.telemetry import capture_tool_metrics, track_event

@authenticated_tool
@capture_tool_metrics
def get_donor_portfolio(donor_id: str):
    """Get donor portfolio with comprehensive telemetry"""
    
    # Get caller information
    caller = get_caller_identity()
    
    # Track custom event
    track_event(
        name="DonorPortfolioRequested",
        properties={
            "donor_id": donor_id,
            "requester": caller.identity,
            "classification": "CONFIDENTIAL"
        }
    )
    
    # Get donor data
    start_time = time.time()
    donor = await donor_service.get(donor_id)
    data_retrieval_time = time.time() - start_time
    
    # Track data retrieval metric
    track_metric(
        name="DataRetrievalTime",
        value=data_retrieval_time * 1000,  # Convert to ms
        properties={"operation": "get_donor"}
    )
    
    # Process data
    start_time = time.time()
    portfolio = await portfolio_service.calculate(donor)
    processing_time = time.time() - start_time
    
    # Track processing metric
    track_metric(
        name="ProcessingTime",
        value=processing_time * 1000,
        properties={"operation": "calculate_portfolio"}
    )
    
    return portfolio
```

### Custom Telemetry Endpoint

```python
from platform.telemetry import TelemetryClient

# Create client with custom endpoint
client = TelemetryClient(
    app_insights_enabled=False,
    custom_endpoints=["https://telemetry.my-org.org/api/metrics"]
)

# Track to custom endpoint
client.track_tool_call(
    tool="CustomTool",
    duration=100,
    status="Success",
    custom_property="custom_value"
)

# Flush to send immediately
client.flush()
```

### Token Usage Tracking

```python
from platform.auth import authenticated_tool
from platform.telemetry import capture_tool_metrics

@authenticated_tool
@capture_tool_metrics
def generate_analysis(prompt: str):
    """Generate analysis with token usage tracking"""
    
    # Get caller information
    caller = get_caller_identity()
    
    # Track input tokens
    input_tokens = len(prompt.split())
    
    # Generate analysis
    result = await llm_service.analyze(prompt)
    
    # Track output tokens
    output_tokens = len(result.split())
    
    # Return result with token usage
    return {
        "result": result,
        "token_usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }
    }
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `TelemetryError` | Base telemetry error | TELE-001 |
| `TelemetryConfigurationError` | Configuration error | TELE-002 |
| `TelemetryConnectionError` | Connection error | TELE-003 |

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| TELE-001 | Telemetry error | 500 |
| TELE-002 | Configuration error | 500 |
| TELE-003 | Connection error | 503 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*