#!/usr/bin/env python3
"""
Enhanced Logging Configuration Hierarchy
Provides centralized, hierarchical logging configuration for the entire PII/PHI Scanner system
"""

import logging
import logging.handlers
import sys
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from pii_scanner_poc.core.configuration import SystemConfig, LogLevel


class LoggerType(Enum):
    """Types of specialized loggers in the system"""
    MAIN = "main"
    AI_SERVICE = "ai_service" 
    DATABASE = "database"
    ALIAS_MANAGEMENT = "alias_management"
    CLASSIFICATION = "classification"
    MCP_SERVER = "mcp_server"
    WORKFLOW = "workflow"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TEST = "test"


@dataclass
class LogEntry:
    """Structured log entry for JSON logging"""
    timestamp: str
    level: str
    logger_name: str
    component: str
    message: str
    extra_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None


class StructuredJSONFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def __init__(self, include_extra: bool = True):
        """
        Initialize JSON formatter
        
        Args:
            include_extra: Whether to include extra fields in JSON output
        """
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON
        
        Args:
            record: Log record to format
            
        Returns:
            str: JSON formatted log entry
        """
        # Create base log entry
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            logger_name=record.name,
            component=getattr(record, 'component', record.name.split('.')[-1]),
            message=record.getMessage(),
            session_id=getattr(record, 'session_id', None),
            user_id=getattr(record, 'user_id', None),
            request_id=getattr(record, 'request_id', None)
        )
        
        # Add extra data if available and requested
        if self.include_extra:
            extra_data = {}
            
            # Extract custom attributes
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                              'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                              'relativeCreated', 'thread', 'threadName', 'processName', 'process',
                              'getMessage', 'exc_info', 'exc_text', 'stack_info', 'component',
                              'session_id', 'user_id', 'request_id']:
                    try:
                        # Ensure value is JSON serializable
                        json.dumps(value)
                        extra_data[key] = value
                    except (TypeError, ValueError):
                        extra_data[key] = str(value)
            
            if extra_data:
                log_entry.extra_data = extra_data
        
        # Add exception info if present
        if record.exc_info:
            log_entry.extra_data = log_entry.extra_data or {}
            log_entry.extra_data['exception'] = self.formatException(record.exc_info)
        
        # Convert to JSON
        return json.dumps(asdict(log_entry), default=str, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Custom formatter with color coding for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def __init__(self, include_component: bool = True, include_timestamp: bool = True):
        """
        Initialize colored formatter
        
        Args:
            include_component: Whether to include component name
            include_timestamp: Whether to include timestamp
        """
        self.include_component = include_component
        self.include_timestamp = include_timestamp
        
        # Build format string
        format_parts = []
        if include_timestamp:
            format_parts.append('%(asctime)s')
        
        format_parts.extend(['%(levelname)s', '%(name)s'])
        
        if include_component:
            format_parts.append('[%(component)s]')
        
        format_parts.append('%(message)s')
        
        format_string = ' - '.join(format_parts)
        super().__init__(format_string, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors
        
        Args:
            record: Log record to format
            
        Returns:
            str: Colored formatted log entry
        """
        # Add component if not present
        if not hasattr(record, 'component'):
            record.component = record.name.split('.')[-1]
        
        # Get base formatted message
        formatted = super().format(record)
        
        # Add color if terminal supports it
        if sys.stderr.isatty():
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            formatted = f"{color}{formatted}{reset}"
        
        return formatted


class LoggingHierarchyManager:
    """
    Central manager for the logging hierarchy
    
    Provides centralized configuration, specialized loggers, and performance monitoring
    for all logging operations in the PII/PHI Scanner system.
    """
    
    def __init__(self, config: SystemConfig):
        """
        Initialize logging hierarchy manager
        
        Args:
            config: System configuration containing logging settings
        """
        self.config = config
        self.log_config = config.logging
        self._initialized_loggers: Dict[str, logging.Logger] = {}
        self._handlers: Dict[str, logging.Handler] = {}
        
        # Initialize root logger configuration
        self._setup_root_logger()
        
        # Create main application logger
        self.main_logger = self.get_logger(LoggerType.MAIN)
        self.main_logger.info("Logging hierarchy manager initialized")
    
    def _setup_root_logger(self):
        """Setup root logger configuration"""
        root_logger = logging.getLogger()
        
        # Set level
        root_logger.setLevel(getattr(logging, self.log_config.level.value))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add console handler if enabled
        if self.log_config.enable_console:
            console_handler = self._create_console_handler()
            root_logger.addHandler(console_handler)
        
        # Add file handler if configured
        if self.log_config.file_path:
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)
            
            # Add structured JSON handler for detailed logging
            if self.log_config.enable_structured:
                json_handler = self._create_json_handler()
                root_logger.addHandler(json_handler)
    
    def _create_console_handler(self) -> logging.Handler:
        """Create console handler with colored formatting"""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, self.log_config.level.value))
        
        formatter = ColoredConsoleFormatter(
            include_component=True,
            include_timestamp=True
        )
        handler.setFormatter(formatter)
        
        self._handlers['console'] = handler
        return handler
    
    def _create_file_handler(self) -> logging.Handler:
        """Create rotating file handler"""
        log_path = Path(self.log_config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=self.log_config.max_file_size,
            backupCount=self.log_config.backup_count,
            encoding='utf-8'
        )
        handler.setLevel(getattr(logging, self.log_config.level.value))
        
        formatter = logging.Formatter(
            fmt=self.log_config.format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self._handlers['file'] = handler
        return handler
    
    def _create_json_handler(self) -> logging.Handler:
        """Create structured JSON handler"""
        json_log_path = Path(self.log_config.file_path).with_suffix('.json')
        json_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.handlers.RotatingFileHandler(
            filename=json_log_path,
            maxBytes=self.log_config.max_file_size,
            backupCount=self.log_config.backup_count,
            encoding='utf-8'
        )
        handler.setLevel(logging.DEBUG)  # Capture all levels for structured logging
        
        formatter = StructuredJSONFormatter(include_extra=True)
        handler.setFormatter(formatter)
        
        self._handlers['json'] = handler
        return handler
    
    def get_logger(self, logger_type: Union[LoggerType, str], 
                   component: Optional[str] = None) -> logging.Logger:
        """
        Get or create a specialized logger
        
        Args:
            logger_type: Type of logger to retrieve
            component: Optional specific component name
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if isinstance(logger_type, LoggerType):
            logger_name = f"pii_scanner.{logger_type.value}"
        else:
            logger_name = f"pii_scanner.{logger_type}"
        
        if component:
            logger_name = f"{logger_name}.{component}"
        
        # Return existing logger if already created
        if logger_name in self._initialized_loggers:
            return self._initialized_loggers[logger_name]
        
        # Create new logger
        logger = logging.getLogger(logger_name)
        
        # Add default component attribute
        if not hasattr(logger, 'component'):
            logger.component = component or logger_name.split('.')[-1]
        
        # Store for reuse
        self._initialized_loggers[logger_name] = logger
        
        return logger
    
    def create_context_logger(self, base_logger: Union[LoggerType, str], 
                            session_id: Optional[str] = None,
                            user_id: Optional[str] = None,
                            request_id: Optional[str] = None) -> logging.LoggerAdapter:
        """
        Create a context-aware logger adapter
        
        Args:
            base_logger: Base logger type or name
            session_id: Optional session identifier
            user_id: Optional user identifier  
            request_id: Optional request identifier
            
        Returns:
            logging.LoggerAdapter: Context-enhanced logger
        """
        logger = self.get_logger(base_logger)
        
        extra_context = {}
        if session_id:
            extra_context['session_id'] = session_id
        if user_id:
            extra_context['user_id'] = user_id
        if request_id:
            extra_context['request_id'] = request_id
        
        return logging.LoggerAdapter(logger, extra_context)
    
    def log_performance_metric(self, 
                             operation: str,
                             duration: float,
                             additional_metrics: Optional[Dict[str, Any]] = None):
        """
        Log performance metrics
        
        Args:
            operation: Name of the operation
            duration: Operation duration in seconds
            additional_metrics: Optional additional performance data
        """
        perf_logger = self.get_logger(LoggerType.PERFORMANCE)
        
        metrics = {
            'operation': operation,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        if additional_metrics:
            metrics.update(additional_metrics)
        
        perf_logger.info(f"Performance: {operation} completed in {duration:.3f}s", 
                        extra=metrics)
    
    def log_security_event(self, 
                          event_type: str,
                          severity: str,
                          details: Dict[str, Any]):
        """
        Log security-related events
        
        Args:
            event_type: Type of security event
            severity: Event severity level
            details: Event details and context
        """
        security_logger = self.get_logger(LoggerType.SECURITY)
        
        security_data = {
            'security_event_type': event_type,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            **details
        }
        
        log_level = getattr(logging, severity.upper(), logging.INFO)
        security_logger.log(log_level, f"Security Event: {event_type}", 
                           extra=security_data)
    
    def log_workflow_step(self, 
                         workflow_name: str,
                         step_name: str,
                         status: str,
                         duration: Optional[float] = None,
                         metadata: Optional[Dict[str, Any]] = None):
        """
        Log workflow step completion
        
        Args:
            workflow_name: Name of the workflow
            step_name: Name of the step
            status: Step completion status
            duration: Optional step duration
            metadata: Optional step metadata
        """
        workflow_logger = self.get_logger(LoggerType.WORKFLOW)
        
        step_data = {
            'workflow_name': workflow_name,
            'step_name': step_name,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        if duration is not None:
            step_data['duration_seconds'] = duration
        
        if metadata:
            step_data['metadata'] = metadata
        
        workflow_logger.info(f"Workflow Step: {workflow_name}.{step_name} - {status}",
                           extra=step_data)
    
    def get_logging_statistics(self) -> Dict[str, Any]:
        """
        Get logging system statistics
        
        Returns:
            Dict containing logging metrics and status
        """
        return {
            'initialized_loggers': list(self._initialized_loggers.keys()),
            'active_handlers': list(self._handlers.keys()),
            'root_level': logging.getLogger().level,
            'log_file_path': self.log_config.file_path,
            'console_enabled': self.log_config.enable_console,
            'structured_enabled': self.log_config.enable_structured,
            'max_file_size': self.log_config.max_file_size,
            'backup_count': self.log_config.backup_count
        }
    
    def reconfigure_logging(self, new_config: SystemConfig):
        """
        Reconfigure logging with new settings
        
        Args:
            new_config: Updated system configuration
        """
        self.config = new_config
        self.log_config = new_config.logging
        
        # Reconfigure root logger
        self._setup_root_logger()
        
        # Clear cached loggers to force reconfiguration
        self._initialized_loggers.clear()
        
        self.main_logger = self.get_logger(LoggerType.MAIN)
        self.main_logger.info("Logging configuration updated")
    
    def create_audit_trail(self, 
                          action: str,
                          resource: str,
                          user: Optional[str] = None,
                          result: str = "success",
                          details: Optional[Dict[str, Any]] = None):
        """
        Create audit trail entry
        
        Args:
            action: Action performed
            resource: Resource affected
            user: User who performed action
            result: Action result
            details: Additional audit details
        """
        audit_logger = self.get_logger('audit')
        
        audit_data = {
            'audit_action': action,
            'audit_resource': resource,
            'audit_user': user,
            'audit_result': result,
            'audit_timestamp': datetime.now().isoformat()
        }
        
        if details:
            audit_data['audit_details'] = details
        
        audit_logger.info(f"Audit: {action} on {resource} - {result}",
                         extra=audit_data)


# Global logging manager instance
_logging_manager: Optional[LoggingHierarchyManager] = None


def initialize_logging(config: SystemConfig) -> LoggingHierarchyManager:
    """
    Initialize the global logging hierarchy
    
    Args:
        config: System configuration
        
    Returns:
        LoggingHierarchyManager: Initialized logging manager
    """
    global _logging_manager
    _logging_manager = LoggingHierarchyManager(config)
    return _logging_manager


def get_logger(logger_type: Union[LoggerType, str], 
               component: Optional[str] = None) -> logging.Logger:
    """
    Get logger instance from global manager
    
    Args:
        logger_type: Type of logger to retrieve
        component: Optional component name
        
    Returns:
        logging.Logger: Configured logger
        
    Raises:
        RuntimeError: If logging system not initialized
    """
    if _logging_manager is None:
        raise RuntimeError("Logging system not initialized. Call initialize_logging() first.")
    
    return _logging_manager.get_logger(logger_type, component)


def get_context_logger(base_logger: Union[LoggerType, str],
                      session_id: Optional[str] = None,
                      user_id: Optional[str] = None,
                      request_id: Optional[str] = None) -> logging.LoggerAdapter:
    """
    Get context-aware logger from global manager
    
    Args:
        base_logger: Base logger type
        session_id: Optional session ID
        user_id: Optional user ID
        request_id: Optional request ID
        
    Returns:
        logging.LoggerAdapter: Context-enhanced logger
    """
    if _logging_manager is None:
        raise RuntimeError("Logging system not initialized. Call initialize_logging() first.")
    
    return _logging_manager.create_context_logger(
        base_logger, session_id, user_id, request_id
    )


# Convenience functions for common logging operations
def log_performance(operation: str, duration: float, **metrics):
    """Log performance metric"""
    if _logging_manager:
        _logging_manager.log_performance_metric(operation, duration, metrics)


def log_security_event(event_type: str, severity: str, **details):
    """Log security event"""
    if _logging_manager:
        _logging_manager.log_security_event(event_type, severity, details)


def log_workflow_step(workflow: str, step: str, status: str, 
                     duration: Optional[float] = None, **metadata):
    """Log workflow step"""
    if _logging_manager:
        _logging_manager.log_workflow_step(workflow, step, status, duration, metadata)


def audit_trail(action: str, resource: str, user: Optional[str] = None, 
               result: str = "success", **details):
    """Create audit trail entry"""
    if _logging_manager:
        _logging_manager.create_audit_trail(action, resource, user, result, details)