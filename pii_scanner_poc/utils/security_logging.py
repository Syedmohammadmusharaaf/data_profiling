"""
Security-Enhanced Logging Configuration
Provides secure logging with sensitive data protection and audit capabilities
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class SecurityLogFilter(logging.Filter):
    """Filter to sanitize log records and remove sensitive data"""
    
    SENSITIVE_PATTERNS = [
        r'password["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)',
        r'token["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)',
        r'key["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)',
        r'secret["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)',
        r'credential["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)'
    ]
    
    def filter(self, record):
        """Filter and sanitize log record"""
        
        # Sanitize message
        if hasattr(record, 'msg'):
            record.msg = self._sanitize_message(str(record.msg))
        
        # Sanitize arguments
        if hasattr(record, 'args') and record.args:
            record.args = tuple(self._sanitize_message(str(arg)) for arg in record.args)
        
        return True
    
    def _sanitize_message(self, message: str) -> str:
        """Remove sensitive data from log message"""
        
        sanitized = message
        
        # Replace sensitive patterns
        for pattern in self.SENSITIVE_PATTERNS:
            import re
            sanitized = re.sub(pattern, r'\1: ***REDACTED***', sanitized, flags=re.IGNORECASE)
        
        return sanitized


class SecurityAuditHandler(logging.Handler):
    """Custom handler for security audit logging"""
    
    def __init__(self, audit_file: str):
        super().__init__()
        self.audit_file = Path(audit_file)
        self.audit_file.parent.mkdir(exist_ok=True)
    
    def emit(self, record):
        """Emit security audit record"""
        
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'component': getattr(record, 'component', 'unknown'),
            'event_type': getattr(record, 'event_type', 'general'),
            'message': record.getMessage(),
            'user_id': getattr(record, 'user_id', 'system'),
            'session_id': getattr(record, 'session_id', None),
            'ip_address': getattr(record, 'ip_address', None),
            'additional_data': getattr(record, 'additional_data', {})
        }
        
        # Write to audit file
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')


class SecureLogger:
    """Security-enhanced logger with audit capabilities"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Add security filter to all handlers
        security_filter = SecurityLogFilter()
        
        # Main log handler with rotation
        main_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{name}.log",
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        main_handler.setLevel(logging.INFO)
        main_handler.addFilter(security_filter)
        main_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        ))
        
        # Error handler
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{name}_errors.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.addFilter(security_filter)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(pathname)s:%(lineno)d | %(message)s'
        ))
        
        # Security audit handler
        audit_handler = SecurityAuditHandler(
            self.log_dir / f"{name}_security_audit.log"
        )
        audit_handler.setLevel(logging.WARNING)
        
        # Add handlers to logger
        self.logger.addHandler(main_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(audit_handler)
        
        # Set secure file permissions
        for handler in [main_handler, error_handler]:
            if hasattr(handler, 'baseFilename'):
                os.chmod(handler.baseFilename, 0o640)
    
    def log_security_event(self, event_type: str, message: str, 
                          user_id: str = None, session_id: str = None,
                          ip_address: str = None, additional_data: Dict = None):
        """Log security-specific events"""
        
        extra = {
            'component': self.name,
            'event_type': event_type,
            'user_id': user_id,
            'session_id': session_id,
            'ip_address': ip_address,
            'additional_data': additional_data or {}
        }
        
        self.logger.warning(message, extra=extra)
    
    def log_access_attempt(self, resource: str, user_id: str, 
                          success: bool, ip_address: str = None):
        """Log access attempts for audit"""
        
        event_type = 'access_granted' if success else 'access_denied'
        message = f"Access {'granted' if success else 'denied'} to {resource}"
        
        self.log_security_event(
            event_type, message, user_id, ip_address=ip_address,
            additional_data={'resource': resource, 'success': success}
        )
    
    def log_data_processing(self, operation: str, data_type: str, 
                           record_count: int, user_id: str = None):
        """Log data processing activities"""
        
        message = f"Data processing: {operation} on {data_type} ({record_count} records)"
        
        self.log_security_event(
            'data_processing', message, user_id,
            additional_data={
                'operation': operation,
                'data_type': data_type,
                'record_count': record_count
            }
        )


# Global security logger instances
security_logger = SecureLogger('security')
audit_logger = SecureLogger('audit')
