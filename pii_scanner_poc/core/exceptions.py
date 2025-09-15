#!/usr/bin/env python3
"""
Custom Exception Classes for PII/PHI Scanner POC
Provides specific, meaningful exceptions for different error scenarios
"""

from typing import Optional, Dict, Any, List
from enum import Enum


class ErrorSeverity(Enum):
    """Enumeration for error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Enumeration for error categories"""
    CONFIGURATION = "configuration"
    INPUT_VALIDATION = "input_validation"
    PARSING = "parsing"
    CLASSIFICATION = "classification"
    DATABASE = "database"
    AI_SERVICE = "ai_service"
    NETWORK = "network"
    SECURITY = "security"
    PERFORMANCE = "performance"
    SYSTEM = "system"


class PIIScannerBaseException(Exception):
    """
    Base exception class for all PII Scanner exceptions
    
    Provides common functionality for error handling, logging, and reporting.
    """
    
    def __init__(self, 
                 message: str,
                 error_code: Optional[str] = None,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 context: Optional[Dict[str, Any]] = None,
                 suggestions: Optional[List[str]] = None):
        """
        Initialize base exception
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for tracking
            severity: Error severity level
            category: Error category for classification
            context: Additional context information
            suggestions: Suggested solutions or actions
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._generate_error_code()
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.suggestions = suggestions or []
    
    def _generate_error_code(self) -> str:
        """Generate unique error code based on exception class"""
        class_name = self.__class__.__name__
        return f"{class_name.upper()}_001"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'context': self.context,
            'suggestions': self.suggestions,
            'exception_type': self.__class__.__name__
        }
    
    def __str__(self) -> str:
        """String representation of exception"""
        return f"[{self.error_code}] {self.message}"
    
    def add_context(self, key: str, value: Any) -> 'PIIScannerBaseException':
        """Add context information to the exception"""
        self.context[key] = value
        return self
    
    def add_suggestion(self, suggestion: str) -> 'PIIScannerBaseException':
        """Add a suggestion to the exception"""
        self.suggestions.append(suggestion)
        return self
    
    def chain_from(self, parent_exception: Exception) -> 'PIIScannerBaseException':
        """Chain this exception from a parent exception"""
        self.context['parent_exception'] = {
            'type': type(parent_exception).__name__,
            'message': str(parent_exception),
            'traceback': str(parent_exception.__traceback__) if hasattr(parent_exception, '__traceback__') else None
        }
        return self


# Configuration Exceptions
class ConfigurationError(PIIScannerBaseException):
    """Exception raised for configuration-related errors"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            **kwargs
        )
        self.config_key = config_key
        if config_key:
            self.context['config_key'] = config_key


class MissingConfigurationError(ConfigurationError):
    """Exception raised when required configuration is missing"""
    
    def __init__(self, config_key: str, **kwargs):
        message = f"Required configuration '{config_key}' is missing"
        suggestions = [
            f"Set the '{config_key}' in your configuration file",
            "Check environment variables for the required setting",
            "Verify your .env file contains all necessary configurations"
        ]
        super().__init__(
            message=message,
            config_key=config_key,
            severity=ErrorSeverity.HIGH,
            suggestions=suggestions,
            **kwargs
        )


class InvalidConfigurationError(ConfigurationError):
    """Exception raised when configuration values are invalid"""
    
    def __init__(self, config_key: str, value: Any, expected: str, **kwargs):
        message = f"Invalid configuration '{config_key}': got '{value}', expected {expected}"
        suggestions = [
            f"Update '{config_key}' to a valid {expected}",
            "Check the configuration documentation",
            "Verify the data type and format of the configuration value"
        ]
        super().__init__(
            message=message,
            config_key=config_key,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        self.context.update({
            'invalid_value': str(value),
            'expected_type': expected
        })


# Input Validation Exceptions
class InputValidationError(PIIScannerBaseException):
    """Exception raised for input validation errors"""
    
    def __init__(self, message: str, field_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.INPUT_VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        self.field_name = field_name
        if field_name:
            self.context['field_name'] = field_name


class InvalidFileFormatError(InputValidationError):
    """Exception raised when file format is invalid or unsupported"""
    
    def __init__(self, file_path: str, expected_formats: List[str], **kwargs):
        message = f"Invalid file format for '{file_path}'. Expected: {', '.join(expected_formats)}"
        suggestions = [
            f"Ensure the file has one of these extensions: {', '.join(expected_formats)}",
            "Verify the file content matches the expected format",
            "Check if the file is corrupted or incomplete"
        ]
        # Call the parent InputValidationError with field_name
        super().__init__(
            message=message,
            field_name="file_path",
            suggestions=suggestions,
            **kwargs
        )
        self.context.update({
            'file_path': file_path,
            'expected_formats': expected_formats
        })


class FileSizeError(InputValidationError):
    """Exception raised when file size exceeds limits"""
    
    def __init__(self, file_path: str, file_size: int, max_size: int, **kwargs):
        message = f"File '{file_path}' ({file_size} bytes) exceeds maximum size limit ({max_size} bytes)"
        suggestions = [
            "Split the file into smaller chunks",
            "Increase the maximum file size limit if appropriate",
            "Use streaming processing for large files"
        ]
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        self.context.update({
            'file_path': file_path,
            'file_size': file_size,
            'max_size': max_size
        })


# Parsing Exceptions  
class ParsingError(PIIScannerBaseException):
    """Exception raised for parsing-related errors"""
    
    def __init__(self, message: str, source: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.PARSING,
            **kwargs
        )
        self.source = source
        if source:
            self.context['source'] = source


class DDLParsingError(ParsingError):
    """Exception raised when DDL parsing fails"""
    
    def __init__(self, message: str, line_number: Optional[int] = None, **kwargs):
        if line_number:
            message = f"DDL parsing error at line {line_number}: {message}"
        
        suggestions = [
            "Verify DDL syntax is correct",
            "Check for missing semicolons or parentheses",
            "Ensure table and column names are properly quoted if needed"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            suggestions=suggestions,
            **kwargs
        )
        self.line_number = line_number
        if line_number:
            self.context['line_number'] = line_number


class JSONParsingError(ParsingError):
    """Exception raised when JSON parsing fails"""
    
    def __init__(self, message: str, json_content: Optional[str] = None, **kwargs):
        suggestions = [
            "Verify JSON syntax is valid",
            "Check for trailing commas or missing quotes",
            "Use a JSON validator to identify syntax issues"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        if json_content:
            # Only store first 500 chars to avoid memory issues
            self.context['json_snippet'] = json_content[:500]


# Classification Exceptions
class ClassificationError(PIIScannerBaseException):
    """Exception raised for classification-related errors"""
    
    def __init__(self, message: str, field_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CLASSIFICATION,
            **kwargs
        )
        self.field_name = field_name
        if field_name:
            self.context['field_name'] = field_name


class PatternMatchingError(ClassificationError):
    """Exception raised when pattern matching fails"""
    
    def __init__(self, pattern: str, field_name: str, **kwargs):
        message = f"Pattern matching failed for field '{field_name}' with pattern '{pattern}'"
        suggestions = [
            "Verify the pattern syntax is correct",
            "Check if the pattern is appropriate for the field type",
            "Consider using fuzzy matching with lower threshold"
        ]
        
        super().__init__(
            message=message,
            field_name=field_name,
            severity=ErrorSeverity.LOW,
            suggestions=suggestions,
            **kwargs
        )
        self.context['pattern'] = pattern


class ConfidenceThresholdError(ClassificationError):
    """Exception raised when confidence scores are below threshold"""
    
    def __init__(self, field_name: str, confidence: float, threshold: float, **kwargs):
        message = f"Field '{field_name}' confidence ({confidence:.2f}) below threshold ({threshold:.2f})"
        suggestions = [
            "Lower the confidence threshold if appropriate",
            "Add more training data or aliases for similar fields",
            "Use manual review for low-confidence classifications"
        ]
        
        super().__init__(
            message=message,
            field_name=field_name,
            severity=ErrorSeverity.LOW,
            suggestions=suggestions,
            **kwargs
        )
        self.context.update({
            'confidence': confidence,
            'threshold': threshold
        })


# Database Exceptions
class DatabaseError(PIIScannerBaseException):
    """Exception raised for database-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            **kwargs
        )


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails"""
    
    def __init__(self, connection_string: str, **kwargs):
        message = f"Failed to connect to database: {connection_string}"
        suggestions = [
            "Verify database server is running and accessible",
            "Check connection string format and credentials",
            "Ensure network connectivity to database server",
            "Verify database permissions for the user"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            suggestions=suggestions,
            **kwargs
        )
        # Don't store full connection string for security
        self.context['connection_info'] = self._mask_connection_string(connection_string)
    
    def _mask_connection_string(self, conn_str: str) -> str:
        """Mask sensitive information in connection string"""
        import re
        # Mask passwords and sensitive information
        masked = re.sub(r'password=[^;]+', 'password=***', conn_str, flags=re.IGNORECASE)
        masked = re.sub(r'pwd=[^;]+', 'pwd=***', masked, flags=re.IGNORECASE)
        return masked


class DatabaseQueryError(DatabaseError):
    """Exception raised when database query fails"""
    
    def __init__(self, query: str, error_message: str, **kwargs):
        message = f"Database query failed: {error_message}"
        suggestions = [
            "Verify SQL syntax is correct for the database type",
            "Check if required tables and columns exist",
            "Ensure database user has necessary permissions"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        # Store only first 200 chars of query for security
        self.context.update({
            'query_snippet': query[:200],
            'db_error': error_message
        })


# AI Service Exceptions
class AIServiceError(PIIScannerBaseException):
    """Exception raised for AI service-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.AI_SERVICE,
            **kwargs
        )


class AIServiceUnavailableError(AIServiceError):
    """Exception raised when AI service is unavailable"""
    
    def __init__(self, service_name: str, **kwargs):
        message = f"AI service '{service_name}' is currently unavailable"
        suggestions = [
            "Check AI service status and connectivity",
            "Verify API keys and authentication",
            "Enable fallback to local pattern recognition",
            "Retry the request after a brief delay"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            suggestions=suggestions,
            **kwargs
        )
        self.context['service_name'] = service_name


class AIServiceTimeoutError(AIServiceError):
    """Exception raised when AI service request times out"""
    
    def __init__(self, timeout_seconds: int, **kwargs):
        message = f"AI service request timed out after {timeout_seconds} seconds"
        suggestions = [
            "Increase the timeout value if appropriate",
            "Reduce the batch size for large requests",
            "Check network connectivity and service performance",
            "Consider using asynchronous processing"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        self.context['timeout_seconds'] = timeout_seconds


class AIServiceQuotaExceededError(AIServiceError):
    """Exception raised when AI service quota is exceeded"""
    
    def __init__(self, quota_type: str, limit: int, **kwargs):
        message = f"AI service {quota_type} quota exceeded (limit: {limit})"
        suggestions = [
            "Wait for quota reset period",
            "Increase quota limit if available",
            "Implement request throttling",
            "Use local classification to reduce AI usage"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            suggestions=suggestions,
            **kwargs
        )
        self.context.update({
            'quota_type': quota_type,
            'limit': limit
        })


# Network Exceptions
class NetworkError(PIIScannerBaseException):
    """Exception raised for network-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            **kwargs
        )


class HTTPError(NetworkError):
    """Exception raised for HTTP-related errors"""
    
    def __init__(self, status_code: int, response_text: str, url: str, **kwargs):
        message = f"HTTP {status_code} error for {url}: {response_text}"
        suggestions = [
            "Check if the service endpoint is correct",
            "Verify authentication credentials",
            "Check service status and availability",
            "Review request parameters and format"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        self.context.update({
            'status_code': status_code,
            'url': url,
            'response_snippet': response_text[:200]
        })


# Security Exceptions  
class SecurityError(PIIScannerBaseException):
    """Exception raised for security-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class AuthenticationError(SecurityError):
    """Exception raised for authentication failures"""
    
    def __init__(self, service: str, **kwargs):
        message = f"Authentication failed for service '{service}'"
        suggestions = [
            "Verify API keys and credentials are correct",
            "Check if credentials have expired",
            "Ensure proper authentication method is used",
            "Contact service provider for credential issues"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.CRITICAL,
            suggestions=suggestions,
            **kwargs
        )
        self.context['service'] = service


class PermissionError(SecurityError):
    """Exception raised for permission/authorization failures"""
    
    def __init__(self, resource: str, required_permission: str, **kwargs):
        message = f"Insufficient permissions to access '{resource}'. Required: {required_permission}"
        suggestions = [
            "Verify user has the required permissions",
            "Contact administrator to grant necessary access",
            "Check role-based access control settings"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            suggestions=suggestions,
            **kwargs
        )
        self.context.update({
            'resource': resource,
            'required_permission': required_permission
        })


# Performance Exceptions
class PerformanceError(PIIScannerBaseException):
    """Exception raised for performance-related issues"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.PERFORMANCE,
            **kwargs
        )


class MemoryError(PerformanceError):
    """Exception raised when memory usage exceeds limits"""
    
    def __init__(self, current_usage: int, limit: int, **kwargs):
        message = f"Memory usage ({current_usage}MB) exceeds limit ({limit}MB)"
        suggestions = [
            "Reduce batch size for processing",
            "Enable streaming for large datasets",
            "Increase memory allocation if possible",
            "Optimize data structures and processing"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.HIGH,
            suggestions=suggestions,
            **kwargs
        )
        self.context.update({
            'current_usage': current_usage,
            'limit': limit
        })


class ProcessingTimeoutError(PerformanceError):
    """Exception raised when processing exceeds time limits"""
    
    def __init__(self, operation: str, timeout_seconds: int, **kwargs):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        suggestions = [
            "Increase timeout value if appropriate",
            "Optimize processing logic for better performance",
            "Consider breaking operation into smaller chunks",
            "Use asynchronous processing for long operations"
        ]
        
        super().__init__(
            message=message,
            severity=ErrorSeverity.MEDIUM,
            suggestions=suggestions,
            **kwargs
        )
        self.context.update({
            'operation': operation,
            'timeout_seconds': timeout_seconds
        })


# Utility functions for exception handling
def handle_exception(exception: Exception, 
                    context: Optional[Dict[str, Any]] = None,
                    logger: Optional[Any] = None) -> PIIScannerBaseException:
    """
    Convert generic exceptions to PII Scanner exceptions
    
    Args:
        exception: Original exception
        context: Additional context information
        logger: Logger instance for recording
        
    Returns:
        PIIScannerBaseException: Converted exception
    """
    context = context or {}
    
    # If it's already our exception, just return it
    if isinstance(exception, PIIScannerBaseException):
        return exception
    
    # Map common exceptions to our custom types
    exception_map = {
        ConnectionError: lambda e: DatabaseConnectionError(str(e), context=context),
        TimeoutError: lambda e: ProcessingTimeoutError("unknown_operation", 30, context=context),
        MemoryError: lambda e: MemoryError(0, 0, context=context),
        ValueError: lambda e: InputValidationError(str(e), context=context),
        FileNotFoundError: lambda e: InvalidFileFormatError(str(e), [], context=context),
        PermissionError: lambda e: SecurityError("unknown_resource", "unknown", context=context)
    }
    
    converter = exception_map.get(type(exception))
    if converter:
        converted = converter(exception)
    else:
        # Create generic system exception
        converted = PIIScannerBaseException(
            message=str(exception),
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            context=context
        )
    
    # Chain from parent exception
    converted.chain_from(exception)
    
    # Log the exception if logger provided
    if logger:
        logger.error(f"Exception handled: {converted}")
    
    return converted


def create_exception_chain(*exceptions: Exception) -> List[PIIScannerBaseException]:
    """
    Create a chain of exceptions for proper error propagation
    
    Args:
        *exceptions: Sequence of exceptions to chain
        
    Returns:
        List of chained PII Scanner exceptions
    """
    chain = []
    parent = None
    
    for exc in exceptions:
        converted = handle_exception(exc)
        if parent:
            converted.chain_from(parent)
        chain.append(converted)
        parent = exc
    
    return chain


def reraise_with_context(exception: Exception, 
                        context: Dict[str, Any],
                        message_prefix: Optional[str] = None) -> None:
    """
    Re-raise an exception with additional context
    
    Args:
        exception: Original exception
        context: Additional context to add
        message_prefix: Optional prefix for the message
    """
    if isinstance(exception, PIIScannerBaseException):
        # Add context to existing exception
        for key, value in context.items():
            exception.add_context(key, value)
        if message_prefix:
            exception.message = f"{message_prefix}: {exception.message}"
        raise exception
    else:
        # Convert and re-raise
        converted = handle_exception(exception, context)
        if message_prefix:
            converted.message = f"{message_prefix}: {converted.message}"
        raise converted from exception