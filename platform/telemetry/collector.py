"""Telemetry Collector for Azure Application Insights"""
from typing import Dict, List, Optional, Any, Callable
from .models import TelemetryData, TelemetryContext, TelemetryType, StatusType
import time
import threading
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class TelemetryCollector:
    def __init__(self):
        self._telemetry_buffer: List[TelemetryData] = []
        self._buffer_lock = threading.Lock()
        self._buffer_size = 100
        self._exporters: List[Callable] = []
        self._enabled = True
    
    def add_exporter(self, exporter: Callable):
        self._exporters.append(exporter)
    
    def collect(self, telemetry: TelemetryData):
        if not self._enabled:
            return
        with self._buffer_lock:
            self._telemetry_buffer.append(telemetry)
            if len(self._telemetry_buffer) >= self._buffer_size:
                self.flush()
    
    def flush(self):
        with self._buffer_lock:
            if not self._telemetry_buffer:
                return
            buffer = self._telemetry_buffer.copy()
            self._telemetry_buffer.clear()
        for exporter in self._exporters:
            try:
                exporter(buffer)
            except Exception as e:
                logger.error(f"Failed to export telemetry: {e}")
    
    @contextmanager
    def track_tool_execution(self, tool_name: str, domain: str, **context_kwargs):
        start_time = time.time()
        status = StatusType.SUCCESS
        error_code = None
        error_message = None
        try:
            yield
        except Exception as e:
            status = StatusType.FAILURE
            error_code = getattr(e, 'error_code', 'UNKNOWN')
            error_message = str(e)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            from platform.auth import get_current_identity
            identity = get_current_identity()
            telemetry = TelemetryData(
                telemetry_type=TelemetryType.TOOL_CALL,
                context=TelemetryContext(
                    tool_name=tool_name,
                    domain=domain,
                    requester_identity=identity.user_id if identity else None,
                    requester_email=identity.email if identity else None,
                    authentication_type=identity.authentication_type if identity else None
                ),
                duration_ms=duration_ms,
                status=status,
                error_code=error_code,
                error_message=error_message
            )
            self.collect(telemetry)
    
    def enable(self):
        self._enabled = True
    
    def disable(self):
        self._enabled = False

# Global collector
_collector: Optional[TelemetryCollector] = None

def set_telemetry_collector(collector: TelemetryCollector):
    global _collector
    _collector = collector

def get_telemetry_collector() -> TelemetryCollector:
    global _collector
    if _collector is None:
        _collector = TelemetryCollector()
        _collector.add_exporter(ConsoleExporter())
    return _collector
