# 📊 Telemetry API Reference

The Telemetry API provides comprehensive observability and monitoring capabilities for the MCP Platform Framework, enabling automatic tracking of tool execution, performance metrics, and operational insights.

## 🎯 Overview

The Telemetry API handles:

- **Application Insights Integration**: Automatic telemetry collection and reporting
- **Tool Execution Tracking**: Automatic capture of tool name, duration, status, and metadata
- **Requester Identity Tracking**: Automatic capture of caller identity and context
- **Custom Metrics**: Support for custom business metrics and counters
- **Distributed Tracing**: End-to-end request tracing across services
- **Performance Monitoring**: Response time tracking and performance analysis

## 🏗️ Core Classes

### TelemetryService

Main telemetry service that orchestrates all telemetry operations.

**Class Signature:**
```python
class TelemetryService:
    def __init__(
        self,
        config: Optional[TelemetryConfig] = None,
        app_insights_client: Optional[TelemetryClient] = None
    ):
        """
        Initialize the Telemetry Service.
        
        Args:
            config: Telemetry configuration
            app_insights_client: Optional Application Insights client
        """
```

**Methods:**

#### `track_tool_execution()`
Track the execution of an MCP tool.

```python
async def track_tool_execution(
    self,
    tool_name: str,
    duration_ms: float,
    status: str,
    success: bool = True,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Track the execution of an MCP tool.
    
    Args:
        tool_name: Name of the tool being executed
        duration_ms: Execution duration in milliseconds
        status: Execution status (e.g., "Success", "Failed")
        success: Whether the execution was successful
        metadata: Additional metadata to track
    """
```

**Example:**
```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

# Track tool execution
await telemetry.track_tool_execution(
    tool_name="GetDonorPortfolio",
    duration_ms=450.5,
    status="Success",
    success=True,
    metadata={
        "domain": "DonorManagement",
        "donor_id": "12345",
        "classification": "CONFIDENTIAL"
    }
)
```

#### `track_request()`
Track an incoming request.

```python
async def track_request(
    self,
    request: MCPRequest,
    context: Optional[Dict[str, Any]] = None
) -> TrackingContext:
    """
    Track an incoming request and return a tracking context.
    
    Args:
        request: Incoming MCP request
        context: Additional context information
        
    Returns:
        TrackingContext for manual tracking
    """
```

**Example:**
```python
from platform.telemetry import TelemetryService
from platform.models import MCPRequest

telemetry = TelemetryService()

# Track incoming request
request = MCPRequest(
    tool_name="GetDonorPortfolio",
    arguments={"donor_id": "12345"},
    context={}
)

tracking_ctx = await telemetry.track_request(request)

try:
    # Process request
    result = await process_request(request)
    tracking_ctx.success(result=result)
except Exception as e:
    tracking_ctx.failure(error=e)
```

#### `track_custom_event()`
Track a custom telemetry event.

```python
def track_custom_event(
    self,
    event_name: str,
    properties: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, float]] = None
) -> None:
    """
    Track a custom telemetry event.
    
    Args:
        event_name: Name of the custom event
        properties: Event properties (string values)
        metrics: Event metrics (numeric values)
    """
```

**Example:**
```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

# Track custom business event
telemetry.track_custom_event(
    event_name="DonorPortfolioUpdated",
    properties={
        "domain": "DonorManagement",
        "donor_id": "12345",
        "action": "update"
    },
    metrics={
        "portfolio_value": 1000000.0,
        "donor_count": 50
    }
)
```

#### `track_exception()`
Track an exception with full context.

```python
def track_exception(
    self,
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    severity: str = "Error"
) -> None:
    """
    Track an exception with full context.
    
    Args:
        exception: Exception to track
        context: Additional context information
        severity: Severity level (Error, Warning, Information, Verbose)
    """
```

**Example:**
```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

try:
    # Some operation that might fail
    result = risky_operation()
except Exception as e:
    telemetry.track_exception(
        exception=e,
        context={
            "operation": "risky_operation",
            "input": "some_input"
        },
        severity="Error"
    )
    raise
```

#### `track_metric()`
Track a custom metric.

```python
def track_metric(
    self,
    metric_name: str,
    value: float,
    properties: Optional[Dict[str, str]] = None
) -> None:
    """
    Track a custom metric.
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        properties: Additional properties for the metric
    """
```

**Example:**
```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

# Track custom metric
telemetry.track_metric(
    metric_name="ActiveDonors",
    value=1500,
    properties={
        "domain": "DonorManagement",
        "region": "global"
    }
)
```

### TelemetryConfig

Configuration for telemetry services.

```python
@dataclass
class TelemetryConfig:
    # Application Insights Configuration
    app_insights_enabled: bool = True
    connection_string: Optional[str] = None
    instrumentation_key: Optional[str] = None
    
    # Tracking Configuration
    track_tool_execution: bool = True
    track_requests: bool = True
    track_exceptions: bool = True
    track_dependencies: bool = True
    
    # Sampling Configuration
    sampling_enabled: bool = True
    sampling_percentage: float = 100.0  # 0-100
    
    # Context Configuration
    include_caller_identity: bool = True
    include_environment: bool = True
    include_domain: bool = True
    include_classification: bool = True
    
    # Performance Configuration
    slow_request_threshold_ms: float = 1000.0  # 1 second
    very_slow_request_threshold_ms: float = 5000.0  # 5 seconds
```

### TrackingContext

Context for manual telemetry tracking.

```python
class TrackingContext:
    def __init__(self, request_id: str, start_time: datetime):
        self.request_id = request_id
        self.start_time = start_time
        self.end_time: Optional[datetime] = None
        self.success: Optional[bool] = None
        self.result: Optional[Any] = None
        self.error: Optional[Exception] = None
        self.metadata: Dict[str, Any] = {}
    
    def add_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
    
    def success(self, result: Any = None) -> None:
        self.end_time = datetime.utcnow()
        self.success = True
        self.result = result
    
    def failure(self, error: Exception) -> None:
        self.end_time = datetime.utcnow()
        self.success = False
        self.error = error
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return (datetime.utcnow() - self.start_time).total_seconds() * 1000
```

## 🎪 Decorators

### `@track_tool_telemetry`
Decorator to automatically track tool execution telemetry.

```python
def track_tool_telemetry(
    func: Optional[Callable] = None,
    *,
    track_arguments: bool = True,
    track_result: bool = False,
    include_classification: bool = True
) -> Callable:
    """
    Decorator to automatically track tool execution telemetry.
    
    Args:
        func: Function to decorate
        track_arguments: Whether to track function arguments
        track_result: Whether to track function result
        include_classification: Whether to include classification in metadata
        
    Returns:
        Decorated function
    """
```

**Example:**
```python
from platform.telemetry import track_tool_telemetry

@track_tool_telemetry
def get_donor_portfolio(donor_id: str):
    # Tool execution is automatically tracked
    return donor_service.get_portfolio(donor_id)

@track_tool_telemetry(track_arguments=False, track_result=True)
def get_donor_summary(donor_id: str):
    # Track result but not arguments
    return donor_service.get_summary(donor_id)
```

### `@telemetry_context()`
Decorator to add custom telemetry context to a function.

```python
def telemetry_context(
    **context_kwargs: Any
) -> Callable:
    """
    Decorator to add custom telemetry context to a function.
    
    Args:
        **context_kwargs: Context key-value pairs to add
        
    Returns:
        Decorated function
    """
```

**Example:**
```python
from platform.telemetry import telemetry_context

@telemetry_context(domain="DonorManagement", service="Analytics")
def get_donor_analytics():
    # All telemetry from this function includes custom context
    return analytics_service.get_analytics()
```

## 🔧 Configuration

### Environment Variables

```bash
# Application Insights Configuration
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
APPLICATIONINSIGHTS_INSTRUMENTATION_KEY=your-instrumentation-key

# Telemetry Configuration
TELEMETRY_ENABLED=true
TELEMETRY_TRACK_TOOL_EXECUTION=true
TELEMETRY_TRACK_REQUESTS=true
TELEMETRY_TRACK_EXCEPTIONS=true
TELEMETRY_TRACK_DEPENDENCIES=true

# Sampling Configuration
TELEMETRY_SAMPLING_ENABLED=true
TELEMETRY_SAMPLING_PERCENTAGE=100.0

# Performance Configuration
TELEMETRY_SLOW_REQUEST_THRESHOLD_MS=1000
TELEMETRY_VERY_SLOW_REQUEST_THRESHOLD_MS=5000
```

### Configuration File

```yaml
# config/telemetry.yaml
telemetry:
  app_insights:
    enabled: true
    connection_string: InstrumentationKey=...
    instrumentation_key: your-instrumentation-key
  
  tracking:
    tool_execution: true
    requests: true
    exceptions: true
    dependencies: true
  
  sampling:
    enabled: true
    percentage: 100.0
  
  context:
    include_caller_identity: true
    include_environment: true
    include_domain: true
    include_classification: true
  
  performance:
    slow_request_threshold_ms: 1000.0
    very_slow_request_threshold_ms: 5000.0
```

## 🚀 Quick Start

### Basic Telemetry Setup

```python
from platform.telemetry import TelemetryService, TelemetryConfig

# Configure telemetry
config = TelemetryConfig(
    app_insights_enabled=True,
    connection_string="InstrumentationKey=...",
    track_tool_execution=True,
    track_exceptions=True
)

# Initialize telemetry service
telemetry = TelemetryService(config=config)

# Track tool execution
await telemetry.track_tool_execution(
    tool_name="GetDonorPortfolio",
    duration_ms=450.5,
    status="Success",
    metadata={"domain": "DonorManagement"}
)
```

### Using Decorators

```python
from platform.telemetry import track_tool_telemetry, telemetry_context

# Automatic telemetry tracking
@track_tool_telemetry
def get_donor_data(donor_id: str):
    return donor_service.get_donor(donor_id)

# Custom telemetry context
@telemetry_context(domain="DonorManagement", service="DataService")
def get_donor_stats():
    return stats_service.get_stats()

# Combined usage
@telemetry_context(domain="DonorManagement")
@track_tool_telemetry
def get_donor_portfolio(donor_id: str):
    return portfolio_service.get_portfolio(donor_id)
```

### Azure Function Integration

```python
from platform.telemetry import TelemetryService, track_tool_telemetry
import azure.functions as func

# Initialize telemetry
telemetry = TelemetryService()

@track_tool_telemetry
def main(req: func.HttpRequest) -> func.HttpResponse:
    # Track custom event
    telemetry.track_custom_event(
        event_name="FunctionInvoked",
        properties={
            "function_name": "GetDonorData",
            "trigger": "http"
        }
    )
    
    # Process request
    donor_id = req.params.get("donor_id")
    donor_data = donor_service.get_donor(donor_id)
    
    return func.HttpResponse(f"Donor data: {donor_data}")
```

## ⭐ Best Practices

### Telemetry Design

✅ **Use Meaningful Event Names**
```python
# Good: Clear, descriptive event names
telemetry.track_custom_event("DonorPortfolioRetrieved")
telemetry.track_custom_event("DonorDataUpdated")
```

❌ **Avoid Vague Event Names**
```python
# Bad: Unclear what the event represents
telemetry.track_custom_event("Event1")
telemetry.track_custom_event("DataOperation")
```

### Performance Monitoring

✅ **Track Important Metrics**
```python
# Good: Track business-relevant metrics
telemetry.track_metric("ActiveDonors", active_count)
telemetry.track_metric("PortfolioValue", total_value)
telemetry.track_metric("RequestDuration", duration_ms)
```

✅ **Use Appropriate Sampling**
```python
# Good: Sample high-volume events to reduce costs
config = TelemetryConfig(
    sampling_enabled=True,
    sampling_percentage=10.0  # Sample 10% of events for high-volume operations
)
```

### Error Tracking

✅ **Track Exceptions with Context**
```python
# Good: Include relevant context with exceptions
try:
    result = process_donor_data(donor_id)
except Exception as e:
    telemetry.track_exception(
        exception=e,
        context={
            "donor_id": donor_id,
            "operation": "process_donor_data",
            "input_size": len(data)
        }
    )
    raise
```

✅ **Use Severity Levels Appropriately**
```python
# Good: Use appropriate severity levels
telemetry.track_exception(exception, severity="Error")      # Critical failures
telemetry.track_exception(exception, severity="Warning")  # Non-critical issues
telemetry.track_exception(exception, severity="Information")  # Informational
```

## 🔍 Troubleshooting

### Common Issues

**Telemetry not appearing in Application Insights**
- Verify that `APPLICATIONINSIGHTS_CONNECTION_STRING` is set correctly
- Check that the connection string is valid and has permissions
- Ensure telemetry is enabled in configuration

**High telemetry costs**
- Enable sampling to reduce volume
- Adjust sampling percentage based on needs
- Consider filtering out verbose or debug-level telemetry

**Missing context in telemetry**
- Verify that context inclusion is enabled in configuration
- Check that caller identity is properly extracted
- Ensure domain and classification are correctly set

**Performance impact from telemetry**
- Use asynchronous telemetry methods where possible
- Consider batching telemetry for high-volume operations
- Review sampling configuration

## 📚 Related Documentation

- [Platform API](platform.md) - Core framework classes
- [Telemetry Module](../modules/telemetry.md) - Module overview
- [Monitoring Best Practices](../best-practices/monitoring.md) - Monitoring recommendations
- [Performance Best Practices](../best-practices/performance.md) - Performance optimization

---

**🎉 Ready to implement telemetry?** Start with the `@track_tool_telemetry` decorator for automatic tracking.

**Need more details?** Check the [Telemetry Module](../modules/telemetry.md) for comprehensive module documentation.