"""
Input Validation and Sanitization Utilities
Provides secure input handling and validation functions
"""

import re
import html
import urllib.parse
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Common validation patterns
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?[1-9]\d{1,14}$',
        'alphanumeric': r'^[a-zA-Z0-9]+$',
        'safe_filename': r'^[a-zA-Z0-9._-]+$',
        'sql_identifier': r'^[a-zA-Z_][a-zA-Z0-9_]*$',
        'url': r'^https?://[^\s/$.?#].[^\s]*$'
    }
    
    # Dangerous patterns to reject
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'union\s+select',  # SQL injection
        r'drop\s+table',  # SQL injection
        r'\.\./|\.\.\.',  # Path traversal
        r'<\s*iframe',  # Iframe injection
    ]
    
    @classmethod
    def validate_string(cls, value: str, pattern_name: str = None, 
                       max_length: int = None, required: bool = True) -> Dict[str, Any]:
        """Validate string input against patterns and constraints"""
        
        result = {
            'valid': True,
            'errors': [],
            'sanitized_value': value,
            'original_value': value
        }
        
        # Check if required
        if required and not value:
            result['valid'] = False
            result['errors'].append('Value is required')
            return result
        
        # Check length
        if max_length and len(value) > max_length:
            result['valid'] = False
            result['errors'].append(f'Value exceeds maximum length of {max_length}')
        
        # Check for dangerous patterns
        for dangerous_pattern in cls.DANGEROUS_PATTERNS:
            if re.search(dangerous_pattern, value, re.IGNORECASE):
                result['valid'] = False
                result['errors'].append('Input contains potentially dangerous content')
                break
        
        # Validate against specific pattern
        if pattern_name and pattern_name in cls.PATTERNS:
            if not re.match(cls.PATTERNS[pattern_name], value):
                result['valid'] = False
                result['errors'].append(f'Value does not match required {pattern_name} format')
        
        # Sanitize the value
        result['sanitized_value'] = cls.sanitize_string(value)
        
        return result
    
    @classmethod
    def sanitize_string(cls, value: str) -> str:
        """Sanitize string by removing/escaping dangerous content"""
        
        if not isinstance(value, str):
            return str(value)
        
        # HTML escape
        sanitized = html.escape(value)
        
        # Remove null bytes
        sanitized = sanitized.replace('', '')
        
        # Remove control characters except newline and tab
        sanitized = re.sub(r'[--]', '', sanitized)
        
        return sanitized.strip()
    
    @classmethod
    def validate_file_path(cls, path: str) -> Dict[str, Any]:
        """Validate file path for security"""
        
        result = {
            'valid': True,
            'errors': [],
            'sanitized_path': path,
            'absolute_path': None
        }
        
        try:
            # Convert to Path object
            path_obj = Path(path)
            
            # Check for path traversal attempts
            if '..' in path_obj.parts:
                result['valid'] = False
                result['errors'].append('Path traversal detected')
            
            # Check for absolute paths if not expected
            if path_obj.is_absolute():
                result['absolute_path'] = str(path_obj.resolve())
            
            # Sanitize filename
            safe_parts = []
            for part in path_obj.parts:
                # Remove dangerous characters
                safe_part = re.sub(r'[<>:"|?*]', '', part)
                safe_parts.append(safe_part)
            
            result['sanitized_path'] = str(Path(*safe_parts))
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f'Invalid path format: {str(e)}')
        
        return result
    
    @classmethod
    def validate_database_identifier(cls, identifier: str) -> Dict[str, Any]:
        """Validate database table/column identifiers"""
        
        result = cls.validate_string(
            identifier, 
            pattern_name='sql_identifier',
            max_length=64,
            required=True
        )
        
        # Additional checks for SQL identifiers
        sql_keywords = {
            'select', 'insert', 'update', 'delete', 'drop', 'create', 
            'alter', 'table', 'database', 'index', 'view', 'union'
        }
        
        if identifier.lower() in sql_keywords:
            result['valid'] = False
            result['errors'].append('Identifier cannot be a SQL keyword')
        
        return result
    
    @classmethod
    def validate_json_input(cls, json_str: str, max_size: int = 1024*1024) -> Dict[str, Any]:
        """Validate JSON input"""
        
        result = {
            'valid': True,
            'errors': [],
            'parsed_data': None
        }
        
        # Check size
        if len(json_str) > max_size:
            result['valid'] = False
            result['errors'].append(f'JSON exceeds maximum size of {max_size} bytes')
            return result
        
        # Parse JSON
        try:
            import json
            result['parsed_data'] = json.loads(json_str)
        except json.JSONDecodeError as e:
            result['valid'] = False
            result['errors'].append(f'Invalid JSON format: {str(e)}')
        
        return result
    
    @classmethod
    def sanitize_log_data(cls, data: Any) -> str:
        """Sanitize data for logging (remove sensitive information)"""
        
        if isinstance(data, dict):
            sanitized = {}
            sensitive_keys = {'password', 'token', 'key', 'secret', 'credential'}
            
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = '***REDACTED***'
                else:
                    sanitized[key] = cls.sanitize_log_data(value)
            
            return str(sanitized)
        
        elif isinstance(data, list):
            return str([cls.sanitize_log_data(item) for item in data])
        
        elif isinstance(data, str):
            # Redact potential sensitive data patterns
            sanitized = data
            
            # Redact email addresses partially
            sanitized = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', 
                             r'***@', sanitized)
            
            # Redact phone numbers
            sanitized = re.sub(r'\d{3}-\d{3}-\d{4}', '***-***-****', sanitized)
            
            return sanitized
        
        else:
            return str(data)


# Global validator instance
input_validator = InputValidator()
