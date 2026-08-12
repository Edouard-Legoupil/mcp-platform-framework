"""Telemetry Exporters for Azure"""
from typing import List
from .models import TelemetryData
import json
import logging

logger = logging.getLogger(__name__)

class ConsoleExporter:
    def __call__(self, telemetry_data: List[TelemetryData]):
        for data in telemetry_data:
            output = {
                "timestamp": data.timestamp.isoformat(),
                "type": data.telemetry_type.value,
                "tool": data.context.tool_name,
                "domain": data.context.domain,
                "duration_ms": data.duration_ms,
                "status": data.status.value,
                "user": data.context.requester_identity
            }
            if data.error_code:
                output["error_code"] = data.error_code
            if data.error_message:
                output["error_message"] = data.error_message
            logger.info(f"TELEMETRY: {json.dumps(output)}")

class ApplicationInsightsExporter:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string
        self._client = None
        if connection_string:
            self._initialize_client()
    
    def _initialize_client(self):
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
            
            # Initialize OpenTelemetry with Azure Monitor
            trace.set_tracer_provider(TracerProvider())
            exporter = AzureMonitorTraceExporter.from_connection_string(self.connection_string)
            trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))
            self._client = exporter
        except ImportError:
            logger.warning("Azure Monitor OpenTelemetry exporter not available")
        except Exception as e:
            logger.error(f"Failed to initialize Application Insights exporter: {e}")
    
    def __call__(self, telemetry_data: List[TelemetryData]):
        if not self._client:
            return
        
        for data in telemetry_data:
            try:
                # Convert telemetry data to OpenTelemetry span
                from opentelemetry import trace
                tracer = trace.get_tracer(__name__)
                
                with tracer.start_as_current_span(f"{data.telemetry_type.value}:{data.context.tool_name}") as span:
                    span.set_attribute("tool.name", data.context.tool_name)
                    span.set_attribute("domain", data.context.domain)
                    span.set_attribute("status", data.status.value)
                    span.set_attribute("duration_ms", data.duration_ms)
                    span.set_attribute("user.id", data.context.requester_identity)
                    
                    if data.error_code:
                        span.set_attribute("error.code", data.error_code)
                    if data.error_message:
                        span.set_attribute("error.message", data.error_message)
                        
            except Exception as e:
                logger.error(f"Failed to export telemetry to Application Insights: {e}")
