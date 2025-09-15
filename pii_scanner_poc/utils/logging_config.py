"""
Centralized logging configuration for PII Scanner POC
Provides structured logging with different levels and outputs
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

class PIILogger:
    """Enhanced logger for PII Scanner with structured logging capabilities"""
    
    def __init__(self, name: str = "pii_scanner", log_level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers with proper formatting"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Console handler with colored output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for all logs
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}_errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # JSON structured log handler for debugging
        json_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}_structured.json",
            maxBytes=10*1024*1024,
            backupCount=3
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JSONFormatter())
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(json_handler)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message with optional structured data"""
        self.logger.debug(message, extra=extra or {})
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message with optional structured data"""
        self.logger.info(message, extra=extra or {})
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message with optional structured data"""
        self.logger.warning(message, extra=extra or {})
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        """Log error message with optional structured data and exception info"""
        self.logger.error(message, extra=extra or {}, exc_info=exc_info)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message with optional structured data"""
        self.logger.critical(message, extra=extra or {})
    
    def log_json_parsing_attempt(self, response_length: int, method: str, success: bool, 
                                error: Optional[str] = None):
        """Specialized logging for JSON parsing attempts"""
        extra = {
            'component': 'json_parser',
            'response_length': response_length,
            'extraction_method': method,
            'success': success,
            'error': error
        }
        
        if success:
            self.info(f"JSON extraction successful using {method}", extra=extra)
        else:
            self.warning(f"JSON extraction failed with {method}: {error}", extra=extra)
    
    def log_batch_processing(self, batch_num: int, table_count: int, column_count: int, 
                           status: str, details: Optional[Dict] = None):
        """Specialized logging for batch processing"""
        extra = {
            'component': 'batch_processor',
            'batch_number': batch_num,
            'table_count': table_count,
            'column_count': column_count,
            'status': status,
            'details': details or {}
        }
        
        if status == 'success':
            self.info(f"Batch {batch_num} processed successfully", extra=extra)
        elif status == 'retry':
            self.warning(f"Batch {batch_num} failed, retrying", extra=extra)
        else:
            self.error(f"Batch {batch_num} failed", extra=extra)
    
    def log_ai_interaction(self, prompt_length: int, response_length: int, 
                          model_name: str, success: bool, duration: float):
        """Specialized logging for AI model interactions"""
        extra = {
            'component': 'ai_service',
            'prompt_length': prompt_length,
            'response_length': response_length,
            'model_name': model_name,
            'success': success,
            'duration_seconds': duration
        }
        
        if success:
            self.info(f"AI interaction successful in {duration:.2f}s", extra=extra)
        else:
            self.error(f"AI interaction failed after {duration:.2f}s", extra=extra)


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, self.RESET)
        return f"{color}{log_message}{self.RESET}"


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'component'):
            log_entry['component'] = record.component
        
        # Add any additional extra data
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'message', 'component']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


# Global logger instances
main_logger = PIILogger("pii_scanner_main", "INFO")
json_logger = PIILogger("json_processor", "DEBUG")
ai_logger = PIILogger("ai_service", "DEBUG")
batch_logger = PIILogger("batch_processor", "DEBUG")
mcp_logger = PIILogger("mcp_server", "DEBUG")

# Convenience functions for common logging patterns
def log_function_entry(logger: PIILogger, function_name: str, **kwargs):
    """Log function entry with parameters"""
    logger.debug(f"Entering {function_name}", extra={
        'component': 'function_trace',
        'function': function_name,
        'parameters': kwargs
    })

def log_function_exit(logger: PIILogger, function_name: str, result_summary: str = ""):
    """Log function exit with result summary"""
    logger.debug(f"Exiting {function_name}: {result_summary}", extra={
        'component': 'function_trace',
        'function': function_name
    })

def log_performance(logger: PIILogger, operation: str, duration: float, **metrics):
    """Log performance metrics"""
    logger.info(f"Performance: {operation} completed in {duration:.2f}s", extra={
        'component': 'performance',
        'operation': operation,
        'duration_seconds': duration,
        **metrics
    })