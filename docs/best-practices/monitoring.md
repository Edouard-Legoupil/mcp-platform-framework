# 📈 Monitoring and Observability Best Practices

Comprehensive guidelines for monitoring MCP services, ensuring operational excellence, and maintaining observability into system health and performance.

## 🎯 Overview

Monitoring and observability are essential for operating MCP services in production. This guide provides best practices for:

- **Telemetry Collection**: Gathering comprehensive operational data
- **Logging Strategies**: Implementing effective logging practices
- **Metrics and Dashboards**: Tracking key performance indicators
- **Alerting**: Setting up actionable alerts
- **Distributed Tracing**: Tracking requests across service boundaries
- **Incident Response**: Handling and learning from incidents

## 📊 Telemetry Collection Best Practices

### ✅ Use Automatic Telemetry Collection

**⭐ Best Practice**: Leverage the framework's automatic telemetry collection for all tools.

```python
from platform.telemetry import track_tool_telemetry

# Good: Automatic telemetry collection
@track_tool_telemetry
def get_donor_portfolio(donor_id: str):
    # Tool execution is automatically tracked
    return donor_service.get_portfolio(donor_id)

# Even better: Include additional context
@track_tool_telemetry
@telemetry_context(domain="DonorManagement", service="Analytics")
def get_donor_analytics(donor_id: str):
    # All telemetry includes custom context
    return analytics_service.get_analytics(donor_id)
```

### ✅ Track Custom Business Metrics

**⭐ Best Practice**: Track metrics that are meaningful to your business.

```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

# Good: Track business-relevant metrics
async def process_donation(donation: dict):
    start_time = time.time()
    
    try:
        result = await donation_service.process(donation)
        duration_ms = (time.time() - start_time) * 1000
        
        # Track business metrics
        telemetry.track_metric("DonationAmount", donation["amount"])
        telemetry.track_metric("DonationProcessingTime", duration_ms)
        telemetry.track_metric("DonationsProcessed", 1)
        
        # Track custom event
        telemetry.track_custom_event(
            event_name="DonationProcessed",
            properties={
                "donor_id": donation["donor_id"],
                "campaign": donation.get("campaign", "general"),
                "currency": donation["currency"]
            },
            metrics={
                "amount": donation["amount"],
                "processing_time_ms": duration_ms
            }
        )
        
        return result
    except Exception as e:
        telemetry.track_exception(e, context={"donation_id": donation.get("id")})
        raise
```

### ✅ Configure Telemetry Sampling

**⭐ Best Practice**: Use sampling to reduce telemetry volume and costs for high-volume operations.

```python
from platform.telemetry import TelemetryConfig

# Good: Telemetry sampling configuration
config = TelemetryConfig(
    app_insights_enabled=True,
    connection_string="InstrumentationKey=...",
    
    # Sampling configuration
    sampling_enabled=True,
    sampling_percentage=100.0,  # 100% in development
    # sampling_percentage=10.0,  # 10% in production for high-volume services
    
    # What to track
    track_tool_execution=True,
    track_requests=True,
    track_exceptions=True,
    track_dependencies=True
)
```

### ✅ Include Rich Context in Telemetry

**⭐ Best Practice**: Include comprehensive context in all telemetry.

```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

# Good: Rich context in telemetry
async def process_request(request: MCPRequest):
    # Extract context from request
    caller = get_caller_identity()
    
    # Add context to telemetry
    context = {
        "domain": "DonorManagement",
        "tool": request.tool_name,
        "request_id": request.request_id,
        "user": caller.username if caller else "anonymous",
        "roles": caller.roles if caller else [],
        "environment": os.getenv("MCP_ENVIRONMENT", "unknown"),
        "version": os.getenv("MCP_VERSION", "1.0.0")
    }
    
    # Track request with context
    tracking_ctx = await telemetry.track_request(request, context=context)
    
    try:
        result = await process_tool(request)
        tracking_ctx.success(result=result)
        return result
    except Exception as e:
        tracking_ctx.failure(error=e)
        raise
```

## 📝 Logging Best Practices

### ✅ Use Structured Logging

**⭐ Best Practice**: Use structured logging for easier analysis and filtering.

```python
import structlog
from datetime import datetime

# Good: Structured logging configuration
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(structlog.stdlib.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True
)

logger = structlog.get_logger()

# Usage
logger.info(
    "Processing donor request",
    donor_id=donor_id,
    operation="get_portfolio",
    user=caller.username,
    start_time=datetime.utcnow().isoformat()
)
```

### ✅ Log at Appropriate Levels

**⭐ Best Practice**: Use appropriate log levels for different types of messages.

```python
# Good: Appropriate log levels

# DEBUG - Detailed debugging information (only in development)
logger.debug("Starting database query", query=query, parameters=parameters)

# INFO - Normal operational messages
logger.info("Donor data retrieved", donor_id=donor_id, duration_ms=duration)

# WARNING - Potentially problematic situations
logger.warning("Donor data incomplete", donor_id=donor_id, missing_fields=missing_fields)

# ERROR - Serious problems that need attention
logger.error("Failed to process donor data", donor_id=donor_id, error=str(e))

# CRITICAL - Critical failures that may cause service outage
logger.critical("Database connection failed", error=str(e), service="donor_service")
```

### ✅ Include Request IDs in Logs

**⭐ Best Practice**: Include request IDs in all log messages for correlation.

```python
from contextvars import ContextVar
import uuid

# Good: Request ID context
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

def set_request_id():
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id

def get_request_id():
    return request_id_var.get()

# Usage in logging
logger.info(
    "Processing request",
    request_id=get_request_id(),
    tool=tool_name,
    user=caller.username
)
```

### ✅ Log to Multiple Destinations

**⭐ Best Practice**: Log to multiple destinations for redundancy and different use cases.

```python
import logging
import sys
from logging.handlers import RotatingFileHandler

# Good: Multiple logging destinations

# Create logger
logger = logging.getLogger("mcp")
logger.setLevel(logging.INFO)

# Console handler (for development)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# File handler (for production)
file_handler = RotatingFileHandler(
    'mcp.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Application Insights handler (for cloud monitoring)
from opencensus.ext.azure import logging_exporter
app_insights_handler = logging_exporter.AzureLogHandler(
    connection_string='InstrumentationKey=...'
)
app_insights_handler.setLevel(logging.INFO)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(app_insights_handler)
```

## 📈 Metrics and Dashboards Best Practices

### ✅ Define Key Performance Indicators (KPIs)

**⭐ Best Practice**: Define and track KPIs that measure business and technical success.

```python
# Good: Key performance indicators

# Business KPIs
BUSINESS_KPIS = {
    "TotalDonors": "Number of active donors",
    "TotalContributions": "Total contribution amount",
    "AverageContribution": "Average contribution per donor",
    "DonorRetentionRate": "Percentage of donors retained",
    "NewDonors": "Number of new donors",
    "DonationFrequency": "Average donations per donor"
}

# Technical KPIs
TECHNICAL_KPIS = {
    "RequestCount": "Total number of requests",
    "RequestDuration": "Average request duration",
    "ErrorRate": "Percentage of failed requests",
    "CacheHitRate": "Percentage of cache hits",
    "DatabaseQueryTime": "Average database query time",
    "ExternalServiceLatency": "Average external service latency"
}

# Resource KPIs
RESOURCE_KPIS = {
    "MemoryUsage": "Current memory usage",
    "CPUUsage": "Current CPU usage",
    "ActiveConnections": "Number of active connections",
    "QueueLength": "Length of processing queue"
}
```

### ✅ Create Comprehensive Dashboards

**⭐ Best Practice**: Create dashboards that provide visibility into all aspects of your service.

```python
# Good: Dashboard configuration (conceptual)

# Azure Application Insights Dashboard Configuration
dashboards = {
    "Overview": {
        "description": "High-level overview of MCP service health",
        "tiles": [
            {
                "type": "metric",
                "metric": "RequestCount",
                "title": "Total Requests",
                "time_range": "PT1H"  # Last hour
            },
            {
                "type": "metric",
                "metric": "RequestDuration",
                "title": "Avg Request Duration",
                "time_range": "PT1H"
            },
            {
                "type": "metric",
                "metric": "ErrorRate",
                "title": "Error Rate",
                "time_range": "PT1H"
            },
            {
                "type": "metric",
                "metric": "CacheHitRate",
                "title": "Cache Hit Rate",
                "time_range": "PT1H"
            }
        ]
    },
    "Performance": {
        "description": "Performance metrics and analysis",
        "tiles": [
            {
                "type": "chart",
                "metric": "RequestDuration",
                "title": "Request Duration Over Time",
                "chart_type": "line",
                "time_range": "PT24H"
            },
            {
                "type": "chart",
                "metric": "DatabaseQueryTime",
                "title": "Database Query Time",
                "chart_type": "bar",
                "time_range": "PT1H"
            },
            {
                "type": "metric",
                "metric": "SlowRequests",
                "title": "Slow Requests (>1s)",
                "time_range": "PT1H"
            }
        ]
    },
    "Business": {
        "description": "Business metrics and KPIs",
        "tiles": [
            {
                "type": "metric",
                "metric": "TotalDonors",
                "title": "Active Donors",
                "time_range": "P1D"  # Last day
            },
            {
                "type": "metric",
                "metric": "TotalContributions",
                "title": "Total Contributions",
                "time_range": "P1D"
            },
            {
                "type": "chart",
                "metric": "NewDonors",
                "title": "New Donors Over Time",
                "chart_type": "line",
                "time_range": "P30D"  # Last 30 days
            }
        ]
    },
    "Errors": {
        "description": "Error analysis and monitoring",
        "tiles": [
            {
                "type": "chart",
                "metric": "ErrorCount",
                "title": "Errors Over Time",
                "chart_type": "line",
                "time_range": "PT24H",
                "group_by": "error_code"
            },
            {
                "type": "table",
                "metric": "TopErrors",
                "title": "Top 10 Errors",
                "time_range": "PT24H",
                "limit": 10
            },
            {
                "type": "metric",
                "metric": "CriticalErrors",
                "title": "Critical Errors",
                "time_range": "PT1H"
            }
        ]
    }
}
```

### ✅ Track Service Level Objectives (SLOs)

**⭐ Best Practice**: Define and track SLOs to measure service reliability.

```python
# Good: Service Level Objectives

SLOs = {
    "Availability": {
        "target": 99.95,  # 99.95% availability
        "description": "Percentage of time the service is available",
        "measurement": "(Total requests - Failed requests) / Total requests * 100",
        "time_window": "P30D"  # 30 days
    },
    "Latency": {
        "target": 500,  # 500ms
        "description": "95th percentile request latency",
        "measurement": "Percentile(RequestDuration, 95)",
        "time_window": "PT5M"  # 5 minutes
    },
    "ErrorRate": {
        "target": 0.1,  # 0.1%
        "description": "Percentage of requests that fail",
        "measurement": "Failed requests / Total requests * 100",
        "time_window": "PT1H"  # 1 hour
    },
    "CacheHitRate": {
        "target": 80,  # 80%
        "description": "Percentage of cache hits",
        "measurement": "Cache hits / (Cache hits + Cache misses) * 100",
        "time_window": "PT1H"  # 1 hour
    }
}
```

### ✅ Use Custom Metrics for Business Insights

**⭐ Best Practice**: Create custom metrics that provide business insights.

```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

# Good: Custom business metrics
class BusinessMetrics:
    def __init__(self):
        self.telemetry = telemetry
    
    def track_donation(self, donation: dict):
        # Track donation metrics
        self.telemetry.track_metric("DonationAmount", donation["amount"])
        self.telemetry.track_metric("DonationCount", 1)
        
        # Track by campaign
        campaign = donation.get("campaign", "general")
        self.telemetry.track_metric(f"DonationAmount:{campaign}", donation["amount"])
        self.telemetry.track_metric(f"DonationCount:{campaign}", 1)
        
        # Track by donor type
        donor_type = donation.get("donor_type", "individual")
        self.telemetry.track_metric(f"DonationAmount:{donor_type}", donation["amount"])
    
    def track_donor_engagement(self, donor_id: str, engagement_type: str):
        # Track donor engagement
        self.telemetry.track_metric("DonorEngagement", 1)
        self.telemetry.track_metric(f"DonorEngagement:{engagement_type}", 1)
        self.telemetry.track_metric(f"DonorEngagement:{donor_id}", 1)
    
    def track_portfolio_performance(self, portfolio: dict):
        # Track portfolio performance metrics
        self.telemetry.track_metric("PortfolioValue", portfolio["total_value"])
        self.telemetry.track_metric("PortfolioGrowth", portfolio["growth"])
        self.telemetry.track_metric("PortfolioRiskScore", portfolio["risk_score"])
```

## 🚨 Alerting Best Practices

### ✅ Set Up Actionable Alerts

**⭐ Best Practice**: Configure alerts that are actionable and provide clear guidance.

```python
# Good: Alert configuration (conceptual)

alerts = [
    {
        "name": "HighErrorRate",
        "condition": "ErrorRate > 1",  # More than 1% errors
        "severity": "High",
        "description": "Error rate is higher than 1%",
        "action": "Investigate error logs and check service health",
        "notification": {
            "email": ["team@example.com"],
            "teams": ["mcp-team"],
            "sms": ["+1234567890"]
        },
        "threshold": {
            "operator": ">",
            "value": 1,
            "time_aggregation": "PT5M",  # 5 minutes
            "evaluation_frequency": "PT1M"  # Check every minute
        }
    },
    {
        "name": "HighLatency",
        "condition": "RequestDuration > 2000",  # More than 2 seconds
        "severity": "Medium",
        "description": "Request latency is higher than 2 seconds",
        "action": "Check performance metrics and investigate slow requests",
        "notification": {
            "email": ["team@example.com"],
            "teams": ["mcp-team"]
        },
        "threshold": {
            "operator": ">",
            "value": 2000,
            "time_aggregation": "PT5M",
            "evaluation_frequency": "PT1M"
        }
    },
    {
        "name": "ServiceUnavailable",
        "condition": "Availability < 99.9",  # Less than 99.9% available
        "severity": "Critical",
        "description": "Service availability is below 99.9%",
        "action": "Check service status and investigate outages",
        "notification": {
            "email": ["team@example.com", "management@example.com"],
            "teams": ["mcp-team", "devops-team"],
            "sms": ["+1234567890", "+1987654321"],
            "voice": ["+1234567890"]
        },
        "threshold": {
            "operator": "<",
            "value": 99.9,
            "time_aggregation": "PT1H",  # 1 hour
            "evaluation_frequency": "PT5M"  # Check every 5 minutes
        }
    },
    {
        "name": "LowCacheHitRate",
        "condition": "CacheHitRate < 70",  # Less than 70%
        "severity": "Low",
        "description": "Cache hit rate is below 70%",
        "action": "Review cache configuration and consider adding more cacheable data",
        "notification": {
            "email": ["team@example.com"]
        },
        "threshold": {
            "operator": "<",
            "value": 70,
            "time_aggregation": "PT1H",
            "evaluation_frequency": "PT15M"  # Check every 15 minutes
        }
    },
    {
        "name": "HighMemoryUsage",
        "condition": "MemoryUsage > 80",  # More than 80%
        "severity": "Medium",
        "description": "Memory usage is higher than 80%",
        "action": "Check memory usage and investigate memory leaks",
        "notification": {
            "email": ["team@example.com"],
            "teams": ["mcp-team"]
        },
        "threshold": {
            "operator": ">",
            "value": 80,
            "time_aggregation": "PT5M",
            "evaluation_frequency": "PT1M"
        }
    }
]
```

### ✅ Implement Alert Escalation

**⭐ Best Practice**: Implement escalation policies for alerts that aren't acknowledged.

```python
# Good: Alert escalation configuration

escalation_policies = {
    "HighErrorRate": {
        "initial_notification": {
            "channels": ["email", "teams"],
            "recipients": ["primary-team"]
        },
        "escalation_steps": [
            {
                "after_minutes": 15,
                "notification": {
                    "channels": ["email", "teams", "sms"],
                    "recipients": ["primary-team", "backup-team"]
                }
            },
            {
                "after_minutes": 30,
                "notification": {
                    "channels": ["email", "teams", "sms", "voice"],
                    "recipients": ["primary-team", "backup-team", "management"]
                }
            },
            {
                "after_minutes": 60,
                "notification": {
                    "channels": ["email", "teams", "sms", "voice"],
                    "recipients": ["primary-team", "backup-team", "management", "executives"]
                },
                "action": "Page on-call engineer"
            }
        ]
    },
    "ServiceUnavailable": {
        "initial_notification": {
            "channels": ["email", "teams", "sms", "voice"],
            "recipients": ["primary-team", "devops-team"]
        },
        "escalation_steps": [
            {
                "after_minutes": 5,
                "notification": {
                    "channels": ["email", "teams", "sms", "voice"],
                    "recipients": ["primary-team", "devops-team", "management"]
                }
            },
            {
                "after_minutes": 10,
                "action": "Page on-call engineer"
            }
        ]
    }
}
```

### ✅ Avoid Alert Fatigue

**⭐ Best Practice**: Configure alerts to avoid overwhelming the team.

```python
# Good: Alert fatigue prevention

# 1. Use appropriate severity levels
# - Critical: Immediate action required (service down, data loss)
# - High: Urgent action required (high error rate, performance degradation)
# - Medium: Action required (resource usage, configuration issues)
# - Low: Informational (cache hit rate, minor issues)

# 2. Set appropriate thresholds
# - Don't alert on every single error
# - Use time aggregation to smooth out spikes
# - Set thresholds that indicate real problems

# 3. Group related alerts
# - Group alerts by service, component, or issue type
# - Use alert correlation to reduce duplicate alerts

# 4. Implement alert suppression
# - Suppress alerts during known maintenance windows
# - Suppress alerts that are already being worked on
# - Suppress alerts for known issues

# 5. Use rate limiting
# - Limit the number of alerts per time period
# - Use exponential backoff for repeated alerts

# Example: Rate-limited alert
class RateLimitedAlert:
    def __init__(self, max_alerts: int, time_window_minutes: int):
        self.max_alerts = max_alerts
        self.time_window = timedelta(minutes=time_window_minutes)
        self.alert_history = []
    
    def should_alert(self) -> bool:
        now = datetime.utcnow()
        # Remove old alerts
        self.alert_history = [t for t in self.alert_history if now - t < self.time_window]
        
        # Check if we've reached the limit
        if len(self.alert_history) >= self.max_alerts:
            return False
        
        # Add current alert
        self.alert_history.append(now)
        return True
```

### ✅ Include Clear Action Items in Alerts

**⭐ Best Practice**: Provide clear, actionable information in alerts.

```python
# Good: Alert with clear action items

alert_template = """
🚨 {severity} Alert: {alert_name}

📊 Current Value: {current_value}
🎯 Threshold: {threshold} {operator}
⏱️ Time: {timestamp}
📈 Trend: {trend}

📝 Description:
{description}

✅ Recommended Actions:
{actions}

🔗 Related Resources:
{resources}

📞 Contact:
{contact}
"""

# Example usage
def format_alert(alert: dict, current_value: float) -> str:
    severity_emoji = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢"
    }
    
    trend = "↑ Increasing" if current_value > alert.get("previous_value", current_value) else "↓ Decreasing"
    
    return alert_template.format(
        severity=severity_emoji.get(alert["severity"], ""),
        alert_name=alert["name"],
        current_value=f"{current_value:.2f}",
        threshold=f"{alert['threshold']['value']}",
        operator=alert["threshold"]["operator"],
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        trend=trend,
        description=alert["description"],
        actions="\n".join([f"- {action}" for action in alert["action"].split(", ")]),
        resources="\n".join([f"- [{name}]({url})" for name, url in alert.get("resources", {}).items()]),
        contact=alert.get("contact", "MCP Team")
    )
```

## 🔍 Distributed Tracing Best Practices

### ✅ Implement End-to-End Tracing

**⭐ Best Practice**: Trace requests across all service boundaries.

```python
from opencensus.trace import tracer as trace_tracer
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.exporters import azure_exporter

# Good: Distributed tracing configuration

tracer = trace_tracer.Tracer(
    exporter=azure_exporter.new_azure_exporter(
        connection_string='InstrumentationKey=...'
    ),
    sampler=ProbabilitySampler(1.0)  # Sample 100% of requests
)

# Usage in MCP tools
from opencensus.trace import execution_context

@tool(
    name="GetDonorPortfolio",
    description="Retrieve donor portfolio information"
)
@authenticated_tool
@track_tool_telemetry
async def get_donor_portfolio(donor_id: str):
    # Start a new span for this tool
    with tracer.span(name="GetDonorPortfolio") as span:
        span.add_attribute("tool", "GetDonorPortfolio")
        span.add_attribute("donor_id", donor_id)
        
        # Get caller identity
        caller = get_caller_identity()
        if caller:
            span.add_attribute("user", caller.username)
            span.add_attribute("roles", ",".join(caller.roles))
        
        try:
            # Call external service with its own span
            with tracer.span(name="fetch_donor_data") as child_span:
                child_span.add_attribute("service", "donor_service")
                donor_data = await donor_service.get_donor(donor_id)
            
            # Call another external service
            with tracer.span(name="fetch_portfolio") as child_span:
                child_span.add_attribute("service", "portfolio_service")
                portfolio = await portfolio_service.get_portfolio(donor_id)
            
            # Combine results
            result = {**donor_data, **portfolio}
            span.add_attribute("status", "success")
            return result
            
        except Exception as e:
            span.add_attribute("status", "failed")
            span.add_attribute("error", str(e))
            raise
```

### ✅ Use Correlation IDs

**⭐ Best Practice**: Use correlation IDs to track related operations across services.

```python
from contextvars import ContextVar
import uuid

# Good: Correlation ID context
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')

def set_correlation_id():
    correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id

def get_correlation_id():
    return correlation_id_var.get() or "unknown"

# Usage in telemetry and logging
def track_with_correlation(event_name: str, properties: dict = None):
    properties = properties or {}
    properties["correlation_id"] = get_correlation_id()
    telemetry.track_custom_event(event_name, properties)

def log_with_correlation(message: str, **kwargs):
    kwargs["correlation_id"] = get_correlation_id()
    logger.info(message, **kwargs)
```

### ✅ Trace Across Service Boundaries

**⭐ Best Practice**: Propagate tracing context when calling external services.

```python
from opencensus.trace import tracer as trace_tracer
from opencensus.trace.propagation import trace_context_http_header_format

# Good: Tracing across service boundaries

async def call_external_service(url: str, data: dict):
    # Get current span context
    current_span = execution_context.get_current_span()
    
    # Create headers with tracing context
    headers = {
        "Content-Type": "application/json"
    }
    
    if current_span:
        # Propagate the trace context
        propagator = trace_context_http_header_format.TraceContextPropagator()
        headers.update(propagator.to_headers(current_span.context))
    
    # Make the request with tracing headers
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            # Extract tracing context from response
            if response.headers.get("traceparent"):
                # Update current span with response context
                pass
            
            return await response.json()
```

## 🚨 Incident Response Best Practices

### ✅ Implement Incident Response Procedures

**⭐ Best Practice**: Have clear procedures for responding to incidents.

```python
# Good: Incident response procedures

incident_response_procedures = {
    "ServiceOutage": {
        "severity": "Critical",
        "description": "Complete service outage",
        "immediate_actions": [
            "Acknowledge the alert within 5 minutes",
            "Assess the scope and impact of the outage",
            "Check service health and dependencies",
            "Notify stakeholders if outage affects production"
        ],
        "investigation_steps": [
            "Check Application Insights for errors and exceptions",
            "Review recent deployments and changes",
            "Check infrastructure health (VMs, databases, etc.)",
            "Review logs for any error patterns",
            "Check external service dependencies"
        ],
        "resolution_steps": [
            "Roll back recent changes if they caused the outage",
            "Restart failed services or components",
            "Scale up resources if under heavy load",
            "Apply fixes or workarounds",
            "Verify service recovery"
        ],
        "post_incident_actions": [
            "Document the incident timeline",
            "Identify root cause",
            "Implement preventive measures",
            "Update runbooks and procedures",
            "Conduct post-mortem review"
        ],
        "escalation_path": [
            {"after_minutes": 5, "team": "primary-team"},
            {"after_minutes": 15, "team": "backup-team"},
            {"after_minutes": 30, "team": "management"},
            {"after_minutes": 60, "action": "page-on-call"}
        ]
    },
    "HighErrorRate": {
        "severity": "High",
        "description": "Error rate exceeds threshold",
        "immediate_actions": [
            "Acknowledge the alert within 15 minutes",
            "Check error logs for patterns",
            "Identify affected components",
            "Assess user impact"
        ],
        "investigation_steps": [
            "Review recent code changes",
            "Check for dependency failures",
            "Analyze error patterns and types",
            "Check resource utilization",
            "Review external service health"
        ],
        "resolution_steps": [
            "Roll back recent changes if they caused the errors",
            "Increase retry logic or circuit breaker thresholds",
            "Scale up resources if needed",
            "Apply bug fixes",
            "Implement workarounds"
        ],
        "post_incident_actions": [
            "Document the incident",
            "Identify root cause",
            "Improve error handling",
            "Add additional monitoring",
            "Update error handling patterns"
        ]
    },
    "PerformanceDegradation": {
        "severity": "Medium",
        "description": "Service performance is degraded",
        "immediate_actions": [
            "Acknowledge the alert within 30 minutes",
            "Check performance metrics",
            "Identify slow operations",
            "Assess user impact"
        ],
        "investigation_steps": [
            "Review performance metrics and trends",
            "Check for resource bottlenecks",
            "Analyze slow query patterns",
            "Review external service performance",
            "Check for database performance issues"
        ],
        "resolution_steps": [
            "Optimize slow queries",
            "Increase caching",
            "Scale up resources",
            "Implement performance improvements",
            "Tune configuration parameters"
        ],
        "post_incident_actions": [
            "Document performance issues",
            "Identify root causes",
            "Implement performance optimizations",
            "Update performance benchmarks",
            "Add performance alerts"
        ]
    }
}
```

### ✅ Create Runbooks for Common Issues

**⭐ Best Practice**: Create runbooks with step-by-step procedures for common issues.

```python
# Good: Runbook for common issues

runbooks = {
    "HighErrorRate": {
        "title": "High Error Rate Runbook",
        "description": "Steps to diagnose and resolve high error rates",
        "initial_diagnosis": [
            {
                "step": 1,
                "action": "Check Application Insights for error details",
                "query": "exceptions | where timestamp > ago(1h) | summarize count() by type, message",
                "expected": "Identify the most common error types"
            },
            {
                "step": 2,
                "action": "Check error rate by operation",
                "query": "requests | where timestamp > ago(1h) | summarize count(), success=countif(success) by name | extend error_rate=todouble((count - success) / count) * 100",
                "expected": "Identify which operations have the highest error rates"
            },
            {
                "step": 3,
                "action": "Check recent deployments",
                "command": "az functionapp deployment list --name <function-app-name> --resource-group <resource-group>",
                "expected": "Identify if errors started after a recent deployment"
            }
        ],
        "common_causes": [
            {
                "cause": "Database connection issues",
                "diagnosis": [
                    "Check database connection strings",
                    "Test database connectivity",
                    "Check database resource usage"
                ],
                "solution": [
                    "Verify database credentials",
                    "Check database service health",
                    "Increase database resources if needed"
                ]
            },
            {
                "cause": "External service failures",
                "diagnosis": [
                    "Check external service health endpoints",
                    "Review Application Insights dependency calls",
                    "Check circuit breaker status"
                ],
                "solution": [
                    "Implement retry logic",
                    "Adjust circuit breaker thresholds",
                    "Add fallback mechanisms"
                ]
            },
            {
                "cause": "Code bugs",
                "diagnosis": [
                    "Review recent code changes",
                    "Check error stack traces",
                    "Reproduce errors in development"
                ],
                "solution": [
                    "Roll back recent changes",
                    "Apply bug fixes",
                    "Add additional error handling"
                ]
            }
        ],
        "escalation": {
            "if_no_improvement_after": "30 minutes",
            "escalate_to": "backup-team",
            "if_still_no_improvement_after": "60 minutes",
            "escalate_to": "management"
        }
    },
    "ServiceUnavailable": {
        "title": "Service Unavailable Runbook",
        "description": "Steps to diagnose and resolve service unavailability",
        "initial_diagnosis": [
            {
                "step": 1,
                "action": "Check service health endpoint",
                "command": "curl https://<service-url>/health",
                "expected": "HTTP 200 response with healthy status"
            },
            {
                "step": 2,
                "action": "Check Application Insights availability",
                "query": "availabilityResults | where timestamp > ago(1h) | summarize avg(duration) by name",
                "expected": "Identify availability metrics for all components"
            },
            {
                "step": 3,
                "action": "Check Azure resource health",
                "command": "az resource list --tag mcp-service=<service-name> --query '[].{Name:name, State:properties.provisioningState}' -o table",
                "expected": "All resources should be in 'Succeeded' state"
            }
        ],
        "common_causes": [
            {
                "cause": "Function App scaling issues",
                "diagnosis": [
                    "Check Function App scale status",
                    "Review scaling logs",
                    "Check for scaling errors"
                ],
                "solution": [
                    "Restart Function App",
                    "Adjust scaling configuration",
                    "Check for resource constraints"
                ]
            },
            {
                "cause": "Dependency failures",
                "diagnosis": [
                    "Check all service dependencies",
                    "Review dependency health endpoints",
                    "Check Application Insights dependency calls"
                ],
                "solution": [
                    "Restart failed dependencies",
                    "Implement fallback mechanisms",
                    "Adjust retry logic"
                ]
            },
            {
                "cause": "Configuration errors",
                "diagnosis": [
                    "Review recent configuration changes",
                    "Check configuration validation",
                    "Test configuration locally"
                ],
                "solution": [
                    "Roll back configuration changes",
                    "Fix configuration errors",
                    "Add configuration validation"
                ]
            }
        ]
    }
}
```

### ✅ Conduct Post-Mortem Reviews

**⭐ Best Practice**: Conduct thorough post-mortem reviews after incidents.

```python
# Good: Post-mortem template

post_mortem_template = """
# Incident Post-Mortem: {incident_name}

## 📋 Summary
- **Incident ID**: {incident_id}
- **Severity**: {severity}
- **Start Time**: {start_time}
- **End Time**: {end_time}
- **Duration**: {duration}
- **Affected Services**: {affected_services}
- **Impact**: {impact_description}

## 📅 Timeline
| Time | Event | Owner |
|------|-------|-------|
{timeline_rows}

## 🔍 Root Cause Analysis
{root_cause_analysis}

## 🎯 Root Cause
{root_cause}

## ✅ Resolution Steps
{resolution_steps}

## 📊 Impact Assessment
- **Users Affected**: {users_affected}
- **Requests Failed**: {requests_failed}
- **Data Loss**: {data_loss}
- **Financial Impact**: {financial_impact}

## 🛡️ Preventive Measures
{preventive_measures}

## 📝 Action Items
| Action Item | Owner | Priority | Due Date | Status |
|-------------|-------|----------|----------|--------|
{action_items_rows}

## 🤝 Lessons Learned
{lessons_learned}

## 📎 Attachments
- [Application Insights logs]({logs_url})
- [Error snapshots]({snapshots_url})
- [Monitoring dashboards]({dashboards_url})
"""

# Example usage
def generate_post_mortem(incident: dict) -> str:
    timeline_rows = "\n".join([
        f"| {event['time']} | {event['description']} | {event.get('owner', 'N/A')} |"
        for event in incident["timeline"]
    ])
    
    action_items_rows = "\n".join([
        f"| {item['action']} | {item['owner']} | {item['priority']} | {item['due_date']} | {item['status']} |"
        for item in incident["action_items"]
    ])
    
    return post_mortem_template.format(
        incident_name=incident["name"],
        incident_id=incident["id"],
        severity=incident["severity"],
        start_time=incident["start_time"],
        end_time=incident["end_time"],
        duration=incident["duration"],
        affected_services=", ".join(incident["affected_services"]),
        impact_description=incident["impact"],
        timeline_rows=timeline_rows,
        root_cause_analysis=incident["root_cause_analysis"],
        root_cause=incident["root_cause"],
        resolution_steps="\n".join([f"{i+1}. {step}" for i, step in enumerate(incident["resolution_steps"])]),
        users_affected=incident["impact_assessment"]["users_affected"],
        requests_failed=incident["impact_assessment"]["requests_failed"],
        data_loss=incident["impact_assessment"]["data_loss"],
        financial_impact=incident["impact_assessment"]["financial_impact"],
        preventive_measures="\n".join([f"- {measure}" for measure in incident["preventive_measures"]]),
        lessons_learned=incident["lessons_learned"],
        action_items_rows=action_items_rows,
        logs_url=incident["attachments"]["logs"],
        snapshots_url=incident["attachments"]["snapshots"],
        dashboards_url=incident["attachments"]["dashboards"]
    )
```

## 📋 Monitoring Checklist

### ✅ Pre-Deployment Monitoring Checklist

- [ ] Application Insights is configured and working
- [ ] All required metrics are being tracked
- [ ] Telemetry sampling is appropriately configured
- [ ] Log levels are set appropriately for each environment
- [ ] Security headers are configured
- [ ] Health endpoints are implemented and monitored
- [ ] Dashboards are created for all key metrics
- [ ] Alerts are configured for critical issues
- [ ] Alert thresholds are set appropriately
- [ ] Alert notifications are configured
- [ ] Incident response procedures are documented
- [ ] Runbooks are created for common issues

### ✅ Runtime Monitoring Checklist

- [ ] Metrics are being collected and stored
- [ ] Logs are being generated and retained
- [ ] Alerts are being triggered appropriately
- [ ] Dashboards are up-to-date and accessible
- [ ] Incident response procedures are being followed
- [ ] Runbooks are being used and updated
- [ ] Post-mortem reviews are conducted after incidents
- [ ] Monitoring is reviewed and improved regularly

## 🚨 Common Monitoring Pitfalls

### ❌ Monitoring Too Much

**Problem**: Monitoring too many metrics can be overwhelming and expensive.

**Solution**: Focus on metrics that provide actionable insights.

```python
# Bad: Monitoring too many metrics
# Tracking hundreds of metrics that are never used

# Good: Focus on actionable metrics
# Track only metrics that help you make decisions
ACTIONABLE_METRICS = [
    "RequestCount",
    "RequestDuration",
    "ErrorRate",
    "CacheHitRate",
    "DatabaseQueryTime",
    "MemoryUsage",
    "CPUUsage"
]
```

### ❌ Not Monitoring the Right Things

**Problem**: Monitoring metrics that don't provide useful insights.

**Solution**: Focus on business and user impact.

```python
# Bad: Monitoring technical metrics without business context
# Tracking CPU usage without understanding user impact

# Good: Monitoring business impact
# Track metrics that directly affect users and business outcomes
BUSINESS_METRICS = [
    "ActiveUsers",
    "RequestSuccessRate",
    "AverageResponseTime",
    "BusinessProcessCompletionRate",
    "UserSatisfactionScore"
]
```

### ❌ Alert Storms

**Problem**: Too many alerts make it difficult to identify real issues.

**Solution**: Use alert grouping, suppression, and rate limiting.

```python
# Good: Alert storm prevention

# 1. Group related alerts
alert_groups = {
    "DatabaseIssues": ["DatabaseConnectionFailed", "DatabaseQueryTimeout", "DatabaseErrorRate"],
    "ExternalServiceIssues": ["ExternalServiceUnavailable", "ExternalServiceTimeout", "ExternalServiceError"],
    "PerformanceIssues": ["HighLatency", "LowThroughput", "HighMemoryUsage"]
}

# 2. Suppress alerts during known issues
suppression_rules = [
    {
        "condition": "MaintenanceWindowActive",
        "suppress_alerts": ["ServiceUnavailable", "HighErrorRate"]
    },
    {
        "condition": "KnownIssue:DatabaseMigration",
        "suppress_alerts": ["DatabaseConnectionFailed", "DatabaseQueryTimeout"]
    }
]

# 3. Rate limit alerts
rate_limits = {
    "HighErrorRate": {"max_alerts": 5, "time_window": "PT1H"},
    "ServiceUnavailable": {"max_alerts": 3, "time_window": "PT30M"}
}
```

### ❌ No Baseline Metrics

**Problem**: Without baseline metrics, it's hard to identify anomalies.

**Solution**: Establish baseline metrics and set thresholds based on them.

```python
# Good: Baseline metrics and dynamic thresholds

# Establish baselines for key metrics
BASELINES = {
    "RequestDuration": {
        "avg": 200,  # ms
        "p95": 500,  # ms
        "p99": 1000  # ms
    },
    "ErrorRate": {
        "avg": 0.1,  # 0.1%
        "p95": 0.5,  # 0.5%
        "p99": 1.0   # 1%
    },
    "CacheHitRate": {
        "avg": 80,   # 80%
        "p95": 70,   # 70%
        "p99": 60    # 60%
    }
}

# Set dynamic thresholds based on baselines
def get_dynamic_threshold(metric: str, percentile: float = 95) -> float:
    baseline = BASELINES.get(metric, {})
    
    if percentile == 95:
        return baseline.get("p95", baseline.get("avg", 0))
    elif percentile == 99:
        return baseline.get("p99", baseline.get("p95", baseline.get("avg", 0)))
    else:
        return baseline.get("avg", 0)

# Example: Set alert threshold at 2x the 95th percentile
alert_threshold = get_dynamic_threshold("RequestDuration", 95) * 2
```

### ❌ Not Testing Monitoring

**Problem**: Monitoring configuration isn't tested, leading to blind spots.

**Solution**: Test monitoring configuration and alerting.

```python
import pytest
from unittest.mock import AsyncMock, patch

# Good: Testing monitoring configuration
class TestMonitoring:
    def test_telemetry_configuration(self):
        from platform.telemetry import TelemetryConfig
        
        config = TelemetryConfig()
        
        # Test that required settings are configured
        assert config.app_insights_enabled is True
        assert config.track_tool_execution is True
        assert config.track_exceptions is True
    
    @pytest.mark.asyncio
    async def test_alert_triggering(self):
        from platform.monitoring import AlertService
        
        alert_service = AlertService()
        
        # Mock the alert condition
        with patch.object(alert_service, 'check_condition', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = True
            
            # Test that alert is triggered
            result = await alert_service.check_alert("HighErrorRate")
            assert result["triggered"] is True
            assert result["severity"] == "High"
    
    @pytest.mark.asyncio
    async def test_alert_notification(self):
        from platform.monitoring import AlertService
        
        alert_service = AlertService()
        
        # Mock the notification service
        with patch('platform.notification.send_notification', new_callable=AsyncMock) as mock_send:
            await alert_service.send_alert_notification(
                alert_name="HighErrorRate",
                severity="High",
                message="Error rate is high",
                recipients=["team@example.com"]
            )
            
            mock_send.assert_called_once()
```

## 📚 Related Documentation

- [Telemetry API](../api-reference/telemetry.md) - Telemetry services
- [Audit API](../api-reference/audit.md) - Audit logging
- [Performance Best Practices](performance.md) - Performance monitoring
- [Security Best Practices](security.md) - Security monitoring
- [Error Handling Best Practices](errors.md) - Error monitoring

---

**🎉 Ready to implement comprehensive monitoring?** Use these best practices to build observable, reliable MCP services.

**Need more details?** Check the Telemetry API documentation for implementation details and advanced monitoring patterns.