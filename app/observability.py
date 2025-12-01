"""
Observability Module
====================

Provides structured logging, tracing, and monitoring for the enterprise agent system.

Features:
- Structured JSON logging
- Request/response tracing
- Performance metrics
- Error tracking
- Agent interaction analytics
"""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps
import traceback

# Configure structured logging
class StructuredLogger:
    """Structured logger with JSON formatting"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler with JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def log(self, level: str, message: str, **kwargs):
        """Log with structured data"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        
        if level == "DEBUG":
            self.logger.debug(json.dumps(log_data))
        elif level == "INFO":
            self.logger.info(json.dumps(log_data))
        elif level == "WARNING":
            self.logger.warning(json.dumps(log_data))
        elif level == "ERROR":
            self.logger.error(json.dumps(log_data))
        elif level == "CRITICAL":
            self.logger.critical(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log("INFO", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.log("DEBUG", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.log("CRITICAL", message, **kwargs)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data)


class RequestTracer:
    """Traces requests through the system"""
    
    def __init__(self):
        self.traces = {}
        self.logger = StructuredLogger("tracer")
    
    def start_trace(self, request_id: str, endpoint: str, **metadata):
        """Start tracing a request"""
        self.traces[request_id] = {
            "request_id": request_id,
            "endpoint": endpoint,
            "start_time": time.time(),
            "events": [],
            "metadata": metadata
        }
        
        self.logger.info(
            "Request started",
            request_id=request_id,
            endpoint=endpoint,
            **metadata
        )
    
    def add_event(self, request_id: str, event_type: str, **data):
        """Add event to trace"""
        if request_id in self.traces:
            event = {
                "timestamp": time.time(),
                "type": event_type,
                **data
            }
            self.traces[request_id]["events"].append(event)
            
            self.logger.debug(
                "Trace event",
                request_id=request_id,
                event_type=event_type,
                **data
            )
    
    def end_trace(self, request_id: str, status: str = "success", **metadata):
        """End tracing a request"""
        if request_id in self.traces:
            trace = self.traces[request_id]
            duration = time.time() - trace["start_time"]
            
            self.logger.info(
                "Request completed",
                request_id=request_id,
                endpoint=trace["endpoint"],
                duration_seconds=duration,
                status=status,
                event_count=len(trace["events"]),
                **metadata
            )
            
            # Clean up old traces (keep last 1000)
            if len(self.traces) > 1000:
                oldest = sorted(self.traces.keys())[0]
                del self.traces[oldest]
    
    def get_trace(self, request_id: str) -> Optional[Dict]:
        """Get trace data for a request"""
        return self.traces.get(request_id)


class PerformanceMonitor:
    """Monitors performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "endpoint_latencies": {},  # endpoint -> [latencies]
            "tool_latencies": {},      # tool -> [latencies]
            "agent_latencies": {},     # agent -> [latencies]
        }
        self.logger = StructuredLogger("performance")
    
    def record_latency(self, category: str, name: str, latency: float):
        """Record latency metric"""
        key = f"{category}_latencies"
        if key in self.metrics:
            if name not in self.metrics[key]:
                self.metrics[key][name] = []
            
            self.metrics[key][name].append(latency)
            
            # Keep only last 1000 measurements
            if len(self.metrics[key][name]) > 1000:
                self.metrics[key][name] = self.metrics[key][name][-1000:]
            
            self.logger.debug(
                "Latency recorded",
                category=category,
                name=name,
                latency_seconds=latency
            )
    
    def get_stats(self, category: str, name: str) -> Dict:
        """Get statistics for a metric"""
        key = f"{category}_latencies"
        if key in self.metrics and name in self.metrics[key]:
            latencies = self.metrics[key][name]
            
            if not latencies:
                return {}
            
            sorted_latencies = sorted(latencies)
            count = len(sorted_latencies)
            
            return {
                "count": count,
                "min": min(sorted_latencies),
                "max": max(sorted_latencies),
                "mean": sum(sorted_latencies) / count,
                "median": sorted_latencies[count // 2],
                "p95": sorted_latencies[int(count * 0.95)],
                "p99": sorted_latencies[int(count * 0.99)],
            }
        
        return {}
    
    def get_all_stats(self) -> Dict:
        """Get all performance statistics"""
        stats = {}
        
        for category in ["endpoint", "tool", "agent"]:
            key = f"{category}_latencies"
            if key in self.metrics:
                stats[category] = {}
                for name in self.metrics[key]:
                    stats[category][name] = self.get_stats(category, name)
        
        return stats


def trace_function(category: str):
    """Decorator to trace function execution"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = StructuredLogger(func.__module__)
            
            try:
                logger.debug(
                    f"{category} started",
                    function=func.__name__,
                    args=str(args)[:100],
                    kwargs=str(kwargs)[:100]
                )
                
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.info(
                    f"{category} completed",
                    function=func.__name__,
                    duration_seconds=duration,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{category} failed",
                    function=func.__name__,
                    duration_seconds=duration,
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = StructuredLogger(func.__module__)
            
            try:
                logger.debug(
                    f"{category} started",
                    function=func.__name__,
                    args=str(args)[:100],
                    kwargs=str(kwargs)[:100]
                )
                
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                logger.info(
                    f"{category} completed",
                    function=func.__name__,
                    duration_seconds=duration,
                    status="success"
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{category} failed",
                    function=func.__name__,
                    duration_seconds=duration,
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global instances
logger = StructuredLogger("app")
tracer = RequestTracer()
performance = PerformanceMonitor()


# Example usage
if __name__ == "__main__":
    # Test structured logging
    logger.info("Application started", version="1.0.0")
    logger.debug("Debug information", user_id="123")
    logger.error("An error occurred", error_code="E001")
    
    # Test tracing
    tracer.start_trace("req-001", "/api/translate", user="alice")
    tracer.add_event("req-001", "llm_call", model="gemini-2.0")
    tracer.end_trace("req-001", status="success", tokens=150)
    
    # Test performance monitoring
    performance.record_latency("endpoint", "/api/translate", 0.5)
    performance.record_latency("endpoint", "/api/translate", 0.6)
    stats = performance.get_stats("endpoint", "/api/translate")
    print(json.dumps(stats, indent=2))
