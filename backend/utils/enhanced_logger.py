#!/usr/bin/env python3
"""
Enhanced Logging System for PII Scanner Backend
==============================================

Comprehensive logging utility with performance tracking,
error handling, and structured logging for debugging
"""

import logging
import time
import json
import traceback
import functools
from datetime import datetime
from typing import Any, Dict, Optional
from contextlib import contextmanager

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m'   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

# Configure enhanced logger
def setup_enhanced_logging():
    """Setup enhanced logging configuration"""
    logger = logging.getLogger('pii_scanner')
    logger.setLevel(logging.DEBUG)
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    formatter = ColoredFormatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # File handler for persistent logs
    file_handler = logging.FileHandler('/var/log/supervisor/pii_scanner_debug.log')
    file_handler.setLevel(logging.DEBUG)
    
    file_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Global logger instance
enhanced_logger = setup_enhanced_logging()

class APILogger:
    """Enhanced API request/response logger"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f'pii_scanner.{name}')
        self.name = name
    
    def log_request(self, endpoint: str, method: str, data: Any = None, params: Dict = None):
        """Log incoming API request"""
        request_data = {
            'endpoint': endpoint,
            'method': method,
            'timestamp': datetime.now().isoformat(),
            'data_size': len(str(data)) if data else 0,
            'params': params or {}
        }
        
        self.logger.info(f"🔵 API REQUEST [{method}] {endpoint}")
        self.logger.debug(f"📊 Request details: {json.dumps(request_data, indent=2)}")
        
        if data and len(str(data)) < 1000:  # Log small payloads
            self.logger.debug(f"📦 Request payload: {json.dumps(data, default=str, indent=2)}")
    
    def log_response(self, endpoint: str, status_code: int, response_data: Any = None, 
                    processing_time: float = None):
        """Log API response"""
        response_info = {
            'endpoint': endpoint,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat(),
            'response_size': len(str(response_data)) if response_data else 0,
            'processing_time_ms': round(processing_time * 1000, 2) if processing_time else None
        }
        
        status_emoji = "✅" if status_code < 400 else "❌"
        self.logger.info(f"{status_emoji} API RESPONSE [{status_code}] {endpoint}")
        
        if processing_time:
            self.logger.info(f"⏱️ Processing time: {processing_time:.3f}s")
        
        self.logger.debug(f"📊 Response details: {json.dumps(response_info, indent=2)}")
        
        if response_data and len(str(response_data)) < 1000:  # Log small responses
            self.logger.debug(f"📦 Response payload: {json.dumps(response_data, default=str, indent=2)}")
    
    def log_error(self, endpoint: str, error: Exception, context: Dict = None):
        """Log API error with full context"""
        error_info = {
            'endpoint': endpoint,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        self.logger.error(f"💥 API ERROR in {endpoint}: {error}")
        self.logger.error(f"🔍 Error details: {json.dumps(error_info, indent=2)}")

def performance_monitor(func_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = func_name or f"{func.__module__}.{func.__name__}"
            logger = logging.getLogger(f'pii_scanner.performance')
            
            start_time = time.time()
            logger.debug(f"⚡ Starting {name}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"✅ {name} completed in {duration:.3f}s")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {name} failed after {duration:.3f}s: {e}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = func_name or f"{func.__module__}.{func.__name__}"
            logger = logging.getLogger(f'pii_scanner.performance')
            
            start_time = time.time()
            logger.debug(f"⚡ Starting {name}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"✅ {name} completed in {duration:.3f}s")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"❌ {name} failed after {duration:.3f}s: {e}")
                raise
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

@contextmanager
def operation_context(operation_name: str, **context):
    """Context manager for tracking operations with metadata"""
    logger = logging.getLogger(f'pii_scanner.operations')
    operation_id = f"{operation_name}_{int(time.time() * 1000)}"
    
    start_time = time.time()
    logger.info(f"🚀 Starting operation: {operation_name} (ID: {operation_id})")
    
    if context:
        logger.debug(f"📋 Operation context: {json.dumps(context, default=str, indent=2)}")
    
    try:
        yield operation_id
        duration = time.time() - start_time
        logger.info(f"✅ Operation completed: {operation_name} in {duration:.3f}s")
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"❌ Operation failed: {operation_name} after {duration:.3f}s")
        logger.error(f"💥 Error: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        raise

class DebugCollector:
    """Collects debug information for troubleshooting"""
    
    def __init__(self):
        self.logger = logging.getLogger('pii_scanner.debug')
        self.debug_data = {}
    
    def collect_system_info(self):
        """Collect system information"""
        import psutil
        import os
        
        system_info = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'python_version': os.sys.version,
            'environment_vars': {
                key: value for key, value in os.environ.items() 
                if 'API' not in key and 'SECRET' not in key and 'PASSWORD' not in key
            }
        }
        
        self.logger.debug(f"🖥️ System info: {json.dumps(system_info, indent=2)}")
        return system_info
    
    def collect_request_debug(self, request_data: Dict):
        """Collect request-specific debug information"""
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'request_size': len(str(request_data)),
            'request_keys': list(request_data.keys()) if isinstance(request_data, dict) else None,
            'data_types': {
                key: type(value).__name__ 
                for key, value in request_data.items()
            } if isinstance(request_data, dict) else None
        }
        
        self.logger.debug(f"🔍 Request debug: {json.dumps(debug_info, indent=2)}")
        return debug_info
    
    def log_classification_debug(self, fields: list, results: list):
        """Log detailed classification debugging"""
        debug_info = {
            'input_fields_count': len(fields),
            'output_results_count': len(results),
            'sample_input': fields[:3] if fields else [],
            'sample_output': results[:3] if results else [],
            'field_types': list(set(f.get('data_type', 'unknown') for f in fields)) if fields else [],
            'result_regulations': list(set(r.get('regulation', 'unknown') for r in results)) if results else []
        }
        
        self.logger.info(f"🔍 Classification debug: {json.dumps(debug_info, indent=2)}")
        return debug_info

# Global debug collector
debug_collector = DebugCollector()

# Utility functions
def log_function_entry(func_name: str, *args, **kwargs):
    """Log function entry with parameters"""
    logger = logging.getLogger('pii_scanner.trace')
    logger.debug(f"→ Entering {func_name} with args={len(args)}, kwargs={list(kwargs.keys())}")

def log_function_exit(func_name: str, result=None, error=None):
    """Log function exit with result or error"""
    logger = logging.getLogger('pii_scanner.trace')
    if error:
        logger.debug(f"← Exiting {func_name} with ERROR: {error}")
    else:
        result_info = f"result_type={type(result).__name__}" if result is not None else "no_result"
        logger.debug(f"← Exiting {func_name} with {result_info}")

def log_data_flow(stage: str, data_description: str, data_size: int = None):
    """Log data flow through the system"""
    logger = logging.getLogger('pii_scanner.dataflow')
    size_info = f" ({data_size} items)" if data_size is not None else ""
    logger.info(f"📊 Data flow [{stage}]: {data_description}{size_info}")

# Export main components
__all__ = [
    'enhanced_logger',
    'APILogger', 
    'performance_monitor',
    'operation_context',
    'debug_collector',
    'log_function_entry',
    'log_function_exit',
    'log_data_flow'
]