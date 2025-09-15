#!/usr/bin/env python3
"""
Security Integration Module for PII/PHI Scanner POC
Integrates security utilities with the main application
"""

import os
import logging
from typing import Any, Dict, Optional, List
from functools import wraps

from pii_scanner_poc.utils.input_validation import input_validator
from pii_scanner_poc.utils.secure_credentials import credential_manager
from pii_scanner_poc.utils.security_logging import security_logger
from pii_scanner_poc.core.exceptions import (
    SecurityError, InputValidationError, PIIScannerBaseException
)


class SecurityManager:
    """
    Centralized security management for the PII Scanner
    Integrates all security utilities and provides unified interface
    """
    
    def __init__(self):
        self.input_validator = input_validator
        self.credential_manager = credential_manager
        self.security_logger = security_logger
        self._initialized = False
        self._setup_security()
    
    def _setup_security(self):
        """Initialize security components"""
        try:
            # Set up security logging
            self.security_logger.log_security_event(
                'system_startup',
                'Security manager initialized',
                additional_data={'component': 'security_manager'}
            )
            
            self._initialized = True
            
        except Exception as e:
            logging.error(f"Failed to initialize security manager: {e}")
            raise SecurityError(
                "Security manager initialization failed",
                component="security_manager"
            ).add_context('initialization_error', str(e))
    
    def validate_input(self, 
                      value: Any,
                      field_name: str,
                      validation_rules: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Validate input using integrated validation rules
        
        Args:
            value: Value to validate
            field_name: Name of the field being validated
            validation_rules: Optional validation rules
            
        Returns:
            Dictionary with validation results
            
        Raises:
            InputValidationError: If validation fails
        """
        if not self._initialized:
            raise SecurityError("Security manager not initialized")
        
        try:
            # Apply default validation rules
            if validation_rules is None:
                validation_rules = self._get_default_validation_rules(field_name)
            
            # Perform validation
            if isinstance(value, str):
                result = self.input_validator.validate_string(
                    value,
                    pattern_name=validation_rules.get('pattern'),
                    max_length=validation_rules.get('max_length'),
                    required=validation_rules.get('required', True)
                )
            elif field_name.endswith('_path') or 'file' in field_name.lower():
                result = self.input_validator.validate_file_path(str(value))
            elif field_name in ['table_name', 'column_name', 'schema_name']:
                result = self.input_validator.validate_database_identifier(str(value))
            else:
                # Generic validation
                result = self.input_validator.validate_string(
                    str(value),
                    max_length=validation_rules.get('max_length', 1000),
                    required=validation_rules.get('required', True)
                )
            
            # Log validation attempt
            self.security_logger.log_security_event(
                'input_validation',
                f"Input validation for field '{field_name}'",
                additional_data={
                    'field_name': field_name,
                    'validation_result': result['valid'],
                    'errors': result.get('errors', [])
                }
            )
            
            if not result['valid']:
                raise InputValidationError(
                    f"Validation failed for field '{field_name}': {', '.join(result['errors'])}",
                    field_name=field_name
                ).add_context('validation_errors', result['errors'])
            
            return result
            
        except Exception as e:
            if isinstance(e, PIIScannerBaseException):
                raise
            else:
                raise InputValidationError(
                    f"Validation error for field '{field_name}': {str(e)}",
                    field_name=field_name
                ).add_context('original_error', str(e))
    
    def _get_default_validation_rules(self, field_name: str) -> Dict[str, Any]:
        """Get default validation rules based on field name"""
        
        rules_map = {
            'email': {'pattern': 'email', 'max_length': 254},
            'phone': {'pattern': 'phone', 'max_length': 20},
            'url': {'pattern': 'url', 'max_length': 2048},
            'file_path': {'max_length': 4096, 'required': True},
            'table_name': {'pattern': 'sql_identifier', 'max_length': 64},
            'column_name': {'pattern': 'sql_identifier', 'max_length': 64},
            'schema_name': {'pattern': 'sql_identifier', 'max_length': 64},
            'session_id': {'pattern': 'alphanumeric', 'max_length': 50},
            'user_id': {'pattern': 'alphanumeric', 'max_length': 50}
        }
        
        # Check for exact matches first
        if field_name in rules_map:
            return rules_map[field_name]
        
        # Check for pattern matches
        for pattern, rules in rules_map.items():
            if pattern in field_name.lower():
                return rules
        
        # Default rules
        return {'max_length': 500, 'required': False}
    
    def sanitize_for_logging(self, data: Any) -> str:
        """Sanitize data for safe logging"""
        return self.input_validator.sanitize_log_data(data)
    
    def validate_database_query_params(self, query: str, params: tuple) -> bool:
        """
        Validate database query parameters for SQL injection prevention
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            True if validation passes
            
        Raises:
            SecurityError: If query appears to be malicious
        """
        if not self._initialized:
            raise SecurityError("Security manager not initialized")
        
        try:
            # Check for dangerous SQL patterns
            dangerous_patterns = [
                '; DROP TABLE',
                '; DELETE FROM',
                'UNION SELECT',
                '-- ',
                '/*',
                'xp_cmdshell',
                'sp_executesql'
            ]
            
            query_upper = query.upper()
            for pattern in dangerous_patterns:
                if pattern in query_upper:
                    self.security_logger.log_security_event(
                        'sql_injection_attempt',
                        f"Potentially malicious SQL pattern detected: {pattern}",
                        additional_data={
                            'query_snippet': query[:100],
                            'detected_pattern': pattern
                        }
                    )
                    raise SecurityError(
                        f"Potentially malicious SQL pattern detected: {pattern}",
                        component="database_security"
                    ).add_context('query_snippet', query[:100])
            
            # Validate parameter count matches placeholders
            placeholder_count = query.count('?') + query.count('%s')
            if len(params) != placeholder_count:
                raise SecurityError(
                    f"Parameter count mismatch: query has {placeholder_count} placeholders, {len(params)} parameters provided",
                    component="database_security"
                )
            
            # Log successful validation
            self.security_logger.log_security_event(
                'query_validation',
                "Database query validation passed",
                additional_data={
                    'placeholder_count': placeholder_count,
                    'param_count': len(params)
                }
            )
            
            return True
            
        except Exception as e:
            if isinstance(e, PIIScannerBaseException):
                raise
            else:
                raise SecurityError(
                    f"Query validation failed: {str(e)}",
                    component="database_security"
                ).add_context('original_error', str(e))
    
    def log_access_attempt(self, 
                          resource: str,
                          user_id: str,
                          success: bool,
                          additional_context: Optional[Dict] = None):
        """Log access attempts for security auditing"""
        
        if not self._initialized:
            return  # Fail silently for logging
        
        try:
            self.security_logger.log_access_attempt(
                resource=resource,
                user_id=user_id,
                success=success
            )
            
            if additional_context:
                self.security_logger.log_security_event(
                    'access_attempt_detail',
                    f"Access attempt to {resource}",
                    user_id=user_id,
                    additional_data=additional_context
                )
                
        except Exception as e:
            # Log security logging failures to standard logger
            logging.error(f"Failed to log access attempt: {e}")
    
    def log_data_processing(self,
                           operation: str,
                           data_type: str,
                           record_count: int,
                           user_id: Optional[str] = None,
                           additional_context: Optional[Dict] = None):
        """Log data processing activities for compliance"""
        
        if not self._initialized:
            return  # Fail silently for logging
        
        try:
            self.security_logger.log_data_processing(
                operation=operation,
                data_type=data_type,
                record_count=record_count,
                user_id=user_id
            )
            
            if additional_context:
                self.security_logger.log_security_event(
                    'data_processing_detail',
                    f"Data processing: {operation}",
                    user_id=user_id,
                    additional_data=additional_context
                )
                
        except Exception as e:
            logging.error(f"Failed to log data processing: {e}")


def secure_input(field_name: str, validation_rules: Optional[Dict] = None):
    """
    Decorator for automatic input validation
    
    Args:
        field_name: Name of the field to validate
        validation_rules: Optional validation rules
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Find the input parameter to validate
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Get the parameter value
            if field_name in bound_args.arguments:
                value = bound_args.arguments[field_name]
                
                # Validate the input
                security_manager.validate_input(value, field_name, validation_rules)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def secure_database_query(func):
    """
    Decorator for database query security validation
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Look for query and params in arguments
        import inspect
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        query = bound_args.arguments.get('query') or bound_args.arguments.get('sql')
        params = bound_args.arguments.get('params') or bound_args.arguments.get('parameters') or ()
        
        if query:
            security_manager.validate_database_query_params(query, params)
        
        return func(*args, **kwargs)
    return wrapper


# Global security manager instance
security_manager = SecurityManager()


def setup_application_security():
    """Set up application-wide security measures"""
    
    # Set secure file permissions for sensitive files
    sensitive_files = [
        '.env',
        'credentials.enc',
        'encryption.key',
        'credential_salt.key'
    ]
    
    for filename in sensitive_files:
        if os.path.exists(filename):
            try:
                os.chmod(filename, 0o600)  # Read/write for owner only
            except Exception as e:
                logging.warning(f"Could not set secure permissions on {filename}: {e}")
    
    # Log security setup completion
    security_manager.security_logger.log_security_event(
        'security_setup',
        'Application security setup completed',
        additional_data={
            'secured_files': sensitive_files,
            'security_manager_initialized': security_manager._initialized
        }
    )


if __name__ == "__main__":
    # Test security manager
    setup_application_security()
    
    # Test input validation
    try:
        result = security_manager.validate_input("test@example.com", "email")
        print(f"Email validation result: {result}")
    except Exception as e:
        print(f"Validation error: {e}")
    
    # Test database query validation
    try:
        security_manager.validate_database_query_params(
            "SELECT * FROM users WHERE id = ?",
            (123,)
        )
        print("Database query validation passed")
    except Exception as e:
        print(f"Query validation error: {e}")