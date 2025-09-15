#!/usr/bin/env python3
"""
Comprehensive Logging System for PII/PHI Scanner Enterprise
Advanced logging with detailed tracking, performance metrics, and debugging capabilities
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import traceback
import threading
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

@dataclass
class LogEntry:
    """Structured log entry for comprehensive tracking"""
    timestamp: str
    level: str
    component: str
    operation: str
    message: str
    session_id: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary for JSON serialization"""
        return {k: v for k, v in asdict(self).items() if v is not None}

class PerformanceTracker:
    """Track performance metrics for operations"""
    
    def __init__(self):
        self.operations = {}
        self.lock = threading.Lock()
    
    @contextmanager
    def track(self, operation_name: str, component: str = None, metadata: Dict[str, Any] = None):
        """Track operation performance with context manager"""
        start_time = time.perf_counter()
        operation_id = f"{component}_{operation_name}" if component else operation_name
        
        try:
            yield
        except Exception as e:
            # Log exception with performance data
            duration = (time.perf_counter() - start_time) * 1000
            comprehensive_logger.error(
                f"Operation {operation_name} failed",
                component=component,
                operation=operation_name,
                duration_ms=duration,
                metadata=metadata,
                exception=e
            )
            raise
        finally:
            duration = (time.perf_counter() - start_time) * 1000
            
            with self.lock:
                if operation_id not in self.operations:
                    self.operations[operation_id] = []
                self.operations[operation_id].append({
                    'duration_ms': duration,
                    'timestamp': datetime.now().isoformat(),
                    'metadata': metadata
                })
            
            # Log successful completion
            comprehensive_logger.info(
                f"Operation {operation_name} completed",
                component=component,
                operation=operation_name,
                duration_ms=duration,
                metadata=metadata
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        with self.lock:
            stats = {}
            for operation, measurements in self.operations.items():
                durations = [m['duration_ms'] for m in measurements]
                stats[operation] = {
                    'count': len(durations),
                    'avg_ms': sum(durations) / len(durations) if durations else 0,
                    'min_ms': min(durations) if durations else 0,
                    'max_ms': max(durations) if durations else 0,
                    'total_ms': sum(durations)
                }
            return stats

class ComprehensiveLogger:
    """
    Advanced logging system for PII/PHI Scanner with detailed tracking
    
    Features:
    - Structured JSON logging with metadata
    - Performance tracking and metrics
    - Component-based logging with context
    - Automatic log rotation and archival
    - Debug mode with enhanced details
    - Session tracking across requests
    - Error aggregation and reporting
    """
    
    def __init__(self, log_dir: str = "/app/logs"):
        """Initialize comprehensive logging system"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Performance tracker
        self.performance_tracker = PerformanceTracker()
        
        # Session tracking
        self.active_sessions = {}
        self.session_lock = threading.Lock()
        
        # Setup loggers
        self._setup_loggers()
        
        self.info("ComprehensiveLogger initialized", component="logger", operation="init")
    
    def _setup_loggers(self):
        """Setup multiple specialized loggers"""
        
        # Main application logger
        self.main_logger = logging.getLogger('pii_scanner_main')
        self.main_logger.setLevel(logging.DEBUG)
        
        # Performance logger
        self.perf_logger = logging.getLogger('pii_scanner_performance')
        self.perf_logger.setLevel(logging.INFO)
        
        # Error logger
        self.error_logger = logging.getLogger('pii_scanner_errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # Security logger
        self.security_logger = logging.getLogger('pii_scanner_security')
        self.security_logger.setLevel(logging.WARNING)
        
        # Clear existing handlers
        for logger in [self.main_logger, self.perf_logger, self.error_logger, self.security_logger]:
            logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        json_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Main application log (rotating daily)
        main_handler = TimedRotatingFileHandler(
            self.log_dir / "pii_scanner_main.log",
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        main_handler.setFormatter(detailed_formatter)
        self.main_logger.addHandler(main_handler)
        
        # Performance log (rotating by size)
        perf_handler = RotatingFileHandler(
            self.log_dir / "pii_scanner_performance.log",
            maxBytes=50*1024*1024,  # 50MB
            backupCount=5,
            encoding='utf-8'
        )
        perf_handler.setFormatter(json_formatter)
        self.perf_logger.addHandler(perf_handler)
        
        # Error log (rotating daily, keep 90 days)
        error_handler = TimedRotatingFileHandler(
            self.log_dir / "pii_scanner_errors.log",
            when='midnight',
            interval=1,
            backupCount=90,
            encoding='utf-8'
        )
        error_handler.setFormatter(detailed_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Security log (rotating daily, keep 365 days)
        security_handler = TimedRotatingFileHandler(
            self.log_dir / "pii_scanner_security.log",
            when='midnight',
            interval=1,
            backupCount=365,
            encoding='utf-8'
        )
        security_handler.setFormatter(detailed_formatter)
        self.security_logger.addHandler(security_handler)
        
        # Console handler for development
        if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(detailed_formatter)
            self.main_logger.addHandler(console_handler)
    
    def _create_log_entry(self, level: str, message: str, component: str = None, 
                         operation: str = None, session_id: str = None, 
                         duration_ms: float = None, metadata: Dict[str, Any] = None,
                         exception: Exception = None) -> LogEntry:
        """Create structured log entry"""
        
        stack_trace = None
        if exception:
            stack_trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        
        return LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.upper(),
            component=component or "unknown",
            operation=operation or "unknown",
            message=message,
            session_id=session_id,
            duration_ms=duration_ms,
            metadata=metadata,
            stack_trace=stack_trace
        )
    
    def _log(self, logger: logging.Logger, level: str, log_entry: LogEntry):
        """Internal logging method"""
        # Create enhanced message
        enhanced_message = f"{log_entry.message}"
        
        if log_entry.component:
            enhanced_message = f"[{log_entry.component}] {enhanced_message}"
        
        if log_entry.operation:
            enhanced_message = f"({log_entry.operation}) {enhanced_message}"
        
        if log_entry.duration_ms is not None:
            enhanced_message = f"{enhanced_message} [Duration: {log_entry.duration_ms:.2f}ms]"
        
        if log_entry.session_id:
            enhanced_message = f"{enhanced_message} [Session: {log_entry.session_id}]"
        
        if log_entry.metadata:
            metadata_str = json.dumps(log_entry.metadata, default=str)
            enhanced_message = f"{enhanced_message} [Metadata: {metadata_str}]"
        
        # Log to appropriate level
        if level.upper() == 'DEBUG':
            logger.debug(enhanced_message)
        elif level.upper() == 'INFO':
            logger.info(enhanced_message)
        elif level.upper() == 'WARNING':
            logger.warning(enhanced_message)
        elif level.upper() == 'ERROR':
            logger.error(enhanced_message)
            if log_entry.stack_trace:
                logger.error(f"Stack trace: {log_entry.stack_trace}")
        elif level.upper() == 'CRITICAL':
            logger.critical(enhanced_message)
    
    # Public logging methods
    def debug(self, message: str, component: str = None, operation: str = None, 
              session_id: str = None, metadata: Dict[str, Any] = None):
        """Log debug message"""
        log_entry = self._create_log_entry('DEBUG', message, component, operation, session_id, None, metadata)
        self._log(self.main_logger, 'DEBUG', log_entry)
    
    def info(self, message: str, component: str = None, operation: str = None, 
             session_id: str = None, duration_ms: float = None, metadata: Dict[str, Any] = None):
        """Log info message"""
        log_entry = self._create_log_entry('INFO', message, component, operation, session_id, duration_ms, metadata)
        self._log(self.main_logger, 'INFO', log_entry)
        
        # Also log to performance logger if duration is provided
        if duration_ms is not None:
            perf_entry = {
                'timestamp': log_entry.timestamp,
                'component': component,
                'operation': operation,
                'duration_ms': duration_ms,
                'session_id': session_id,
                'metadata': metadata
            }
            self.perf_logger.info(json.dumps(perf_entry, default=str))
    
    def warning(self, message: str, component: str = None, operation: str = None, 
                session_id: str = None, metadata: Dict[str, Any] = None):
        """Log warning message"""
        log_entry = self._create_log_entry('WARNING', message, component, operation, session_id, None, metadata)
        self._log(self.main_logger, 'WARNING', log_entry)
    
    def error(self, message: str, component: str = None, operation: str = None, 
              session_id: str = None, metadata: Dict[str, Any] = None, exception: Exception = None):
        """Log error message"""
        log_entry = self._create_log_entry('ERROR', message, component, operation, session_id, None, metadata, exception)
        self._log(self.main_logger, 'ERROR', log_entry)
        self._log(self.error_logger, 'ERROR', log_entry)
    
    def critical(self, message: str, component: str = None, operation: str = None, 
                 session_id: str = None, metadata: Dict[str, Any] = None, exception: Exception = None):
        """Log critical message"""
        log_entry = self._create_log_entry('CRITICAL', message, component, operation, session_id, None, metadata, exception)
        self._log(self.main_logger, 'CRITICAL', log_entry)
        self._log(self.error_logger, 'CRITICAL', log_entry)
    
    def security(self, message: str, component: str = None, operation: str = None, 
                 session_id: str = None, metadata: Dict[str, Any] = None):
        """Log security-related message"""
        log_entry = self._create_log_entry('WARNING', message, component, operation, session_id, None, metadata)
        self._log(self.security_logger, 'WARNING', log_entry)
    
    # Context managers for operation tracking
    @contextmanager
    def operation_context(self, operation_name: str, component: str = None, 
                         session_id: str = None, metadata: Dict[str, Any] = None):
        """Context manager for tracking complete operations with automatic logging"""
        self.debug(f"Starting operation: {operation_name}", component, operation_name, session_id, metadata)
        
        start_time = time.perf_counter()
        
        try:
            with self.performance_tracker.track(operation_name, component, metadata):
                yield
        except Exception as e:
            duration = (time.perf_counter() - start_time) * 1000
            self.error(
                f"Operation failed: {operation_name}",
                component=component,
                operation=operation_name,
                session_id=session_id,
                metadata=metadata,
                exception=e
            )
            raise
        else:
            duration = (time.perf_counter() - start_time) * 1000
            self.info(
                f"Operation completed: {operation_name}",
                component=component,
                operation=operation_name,
                session_id=session_id,
                duration_ms=duration,
                metadata=metadata
            )
    
    # Session management
    def start_session(self, session_id: str, session_type: str = "analysis", metadata: Dict[str, Any] = None):
        """Start tracking a new session"""
        with self.session_lock:
            self.active_sessions[session_id] = {
                'session_id': session_id,
                'session_type': session_type,
                'start_time': datetime.now(),
                'metadata': metadata or {},
                'operations': []
            }
        
        self.info(f"Session started: {session_type}", component="session_manager", 
                 operation="start_session", session_id=session_id, metadata=metadata)
    
    def end_session(self, session_id: str, status: str = "completed", metadata: Dict[str, Any] = None):
        """End session tracking"""
        with self.session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session['end_time'] = datetime.now()
                session['duration'] = (session['end_time'] - session['start_time']).total_seconds()
                session['status'] = status
                if metadata:
                    session['metadata'].update(metadata)
                
                # Log session completion
                self.info(
                    f"Session ended: {session['session_type']} ({status})",
                    component="session_manager",
                    operation="end_session",
                    session_id=session_id,
                    duration_ms=session['duration'] * 1000,
                    metadata=session['metadata']
                )
                
                # Archive session (could be saved to database in production)
                del self.active_sessions[session_id]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            'operation_stats': self.performance_tracker.get_stats(),
            'active_sessions': len(self.active_sessions),
            'log_files': {
                'main': str(self.log_dir / "pii_scanner_main.log"),
                'performance': str(self.log_dir / "pii_scanner_performance.log"),
                'errors': str(self.log_dir / "pii_scanner_errors.log"),
                'security': str(self.log_dir / "pii_scanner_security.log")
            }
        }

# Global comprehensive logger instance
comprehensive_logger = ComprehensiveLogger()

# Convenience function for backwards compatibility
def get_logger(component: str = None):
    """Get logger instance for a specific component"""
    return comprehensive_logger