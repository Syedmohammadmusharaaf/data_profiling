#!/usr/bin/env python3
"""
Abstract Base Classes for Service Architecture
Defines interfaces and contracts for all service components
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Iterator
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

# Import our configuration system
from pii_scanner_poc.core.configuration import SystemConfig


class ServiceStatus(Enum):
    """Enumeration for service status"""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running" 
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class ServiceHealth:
    """Health status information for services"""
    status: ServiceStatus
    last_check: datetime
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None


class BaseService(ABC):
    """
    Abstract base class for all services in the PII/PHI Scanner system
    
    Provides common functionality like configuration, logging, health checks,
    and lifecycle management that all services should implement.
    """
    
    def __init__(self, config: SystemConfig, service_name: str):
        """
        Initialize base service
        
        Args:
            config: System configuration
            service_name: Name of the service for logging
        """
        self.config = config
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
        self._status = ServiceStatus.INITIALIZING
        self._health = ServiceHealth(
            status=ServiceStatus.INITIALIZING,
            last_check=datetime.now()
        )
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the service
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Gracefully shutdown the service
        
        Returns:
            bool: True if shutdown successful, False otherwise
        """
        pass
    
    def get_health(self) -> ServiceHealth:
        """
        Get current health status of the service
        
        Returns:
            ServiceHealth: Current health information
        """
        return self._health
    
    def get_status(self) -> ServiceStatus:
        """
        Get current status of the service
        
        Returns:
            ServiceStatus: Current service status
        """
        return self._status
    
    def _update_status(self, status: ServiceStatus, error_message: Optional[str] = None):
        """Update service status and health"""
        self._status = status
        self._health = ServiceHealth(
            status=status,
            last_check=datetime.now(),
            error_message=error_message
        )


class AIServiceInterface(BaseService):
    """
    Abstract interface for AI service implementations
    
    Defines the contract that all AI service implementations must follow
    for LLM-based PII/PHI classification.
    """
    
    @abstractmethod
    def analyze_columns_for_pii(self, 
                               columns: List[Dict[str, Any]], 
                               regulation: str,
                               timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze columns for PII/PHI content using AI
        
        Args:
            columns: List of column metadata dictionaries
            regulation: Target regulation (GDPR, HIPAA, CCPA)
            timeout: Optional timeout in seconds
            
        Returns:
            Dict containing analysis results
            
        Raises:
            AIServiceError: If analysis fails
            TimeoutError: If request times out
        """
        pass
    
    @abstractmethod
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get AI service usage statistics
        
        Returns:
            Dict containing usage metrics (tokens, costs, etc.)
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate connection to AI service
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        pass


class DatabaseServiceInterface(BaseService):
    """
    Abstract interface for database service implementations
    
    Defines the contract for database connection and schema extraction services.
    """
    
    @abstractmethod
    def connect(self, connection_string: str) -> bool:
        """
        Connect to database
        
        Args:
            connection_string: Database connection string
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_schema(self, 
                      database_name: Optional[str] = None,
                      table_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract schema information from database
        
        Args:
            database_name: Optional database/schema name filter
            table_filter: Optional list of table names to include
            
        Returns:
            Dict containing extracted schema metadata
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from database
        
        Returns:
            bool: True if disconnection successful
        """
        pass


class AliasServiceInterface(BaseService):
    """
    Abstract interface for alias database service implementations
    
    Defines the contract for alias management and field classification services.
    """
    
    @abstractmethod
    def find_alias_matches(self, 
                          field_name: str,
                          company_id: Optional[str] = None,
                          region: Optional[str] = None,
                          similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Find matching aliases for a field name
        
        Args:
            field_name: Field name to search for
            company_id: Optional company context
            region: Optional regional context
            similarity_threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            List of matching alias dictionaries
        """
        pass
    
    @abstractmethod
    def add_alias(self, alias_data: Dict[str, Any]) -> bool:
        """
        Add new alias to database
        
        Args:
            alias_data: Alias information dictionary
            
        Returns:
            bool: True if alias added successfully
        """
        pass
    
    @abstractmethod
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get alias database performance statistics
        
        Returns:
            Dict containing performance metrics
        """
        pass
    
    @abstractmethod
    def record_learning_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        Record user feedback for learning improvement
        
        Args:
            feedback_data: Feedback information
            
        Returns:
            bool: True if feedback recorded successfully
        """
        pass


class CacheServiceInterface(BaseService):
    """
    Abstract interface for caching service implementations
    
    Defines the contract for caching schema analysis results and patterns.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value by key
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set cached value
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
            
        Returns:
            bool: True if value cached successfully
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete cached value
        
        Args:
            key: Cache key to delete
            
        Returns:
            bool: True if deletion successful
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all cached values
        
        Returns:
            bool: True if cache cleared successfully
        """
        pass
    
    @abstractmethod
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache performance statistics
        
        Returns:
            Dict containing cache metrics
        """
        pass


class ReportServiceInterface(BaseService):
    """
    Abstract interface for report generation service implementations
    
    Defines the contract for generating various types of compliance reports.
    """
    
    @abstractmethod
    def generate_report(self, 
                       analysis_results: Dict[str, Any],
                       output_format: str = "console",
                       include_metadata: bool = True) -> str:
        """
        Generate compliance report
        
        Args:
            analysis_results: Results from PII/PHI analysis
            output_format: Output format (console, json, csv)
            include_metadata: Whether to include metadata
            
        Returns:
            Formatted report string
        """
        pass
    
    @abstractmethod
    def export_report(self, 
                     report_content: str,
                     file_path: str,
                     format: str = "json") -> bool:
        """
        Export report to file
        
        Args:
            report_content: Report content to export
            file_path: Target file path
            format: Export format
            
        Returns:
            bool: True if export successful
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported report formats
        
        Returns:
            List of supported format strings
        """
        pass


class ClassificationServiceInterface(BaseService):
    """
    Abstract interface for field classification service implementations
    
    Defines the contract for the hybrid classification orchestrator.
    """
    
    @abstractmethod
    def classify_schema(self, 
                       schema_data: Dict[str, Any],
                       regulations: List[str],
                       company_id: Optional[str] = None,
                       region: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify entire schema for PII/PHI content
        
        Args:
            schema_data: Schema metadata
            regulations: List of regulations to check against
            company_id: Optional company context
            region: Optional regional context
            
        Returns:
            Classification results dictionary
        """
        pass
    
    @abstractmethod
    def classify_field(self, 
                      field_data: Dict[str, Any],
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify individual field for PII/PHI content
        
        Args:
            field_data: Field metadata
            context: Additional context information
            
        Returns:
            Classification result dictionary
        """
        pass
    
    @abstractmethod
    def get_classification_statistics(self) -> Dict[str, Any]:
        """
        Get classification performance statistics
        
        Returns:
            Dict containing classification metrics
        """
        pass


class PatternEngineInterface(BaseService):
    """
    Abstract interface for pattern recognition engine implementations
    
    Defines the contract for local pattern-based PII/PHI detection.
    """
    
    @abstractmethod
    def classify_field(self, 
                      field_metadata: Dict[str, Any],
                      table_context: List[str],
                      regulation: str) -> Dict[str, Any]:
        """
        Classify field using pattern recognition
        
        Args:
            field_metadata: Field information
            table_context: Other fields in the same table
            regulation: Target regulation
            
        Returns:
            Classification result
        """
        pass
    
    @abstractmethod
    def add_pattern(self, pattern_data: Dict[str, Any]) -> bool:
        """
        Add new classification pattern
        
        Args:
            pattern_data: Pattern definition
            
        Returns:
            bool: True if pattern added successfully
        """
        pass
    
    @abstractmethod
    def get_pattern_performance(self) -> Dict[str, Any]:
        """
        Get pattern recognition performance metrics
        
        Returns:
            Dict containing pattern performance data
        """
        pass


class ServiceFactory:
    """
    Factory class for creating service instances with dependency injection
    
    Manages service creation, dependency resolution, and lifecycle.
    """
    
    def __init__(self, config: SystemConfig):
        """
        Initialize service factory
        
        Args:
            config: System configuration
        """
        self.config = config
        self._services: Dict[str, BaseService] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_service(self, service_type: str, **kwargs) -> BaseService:
        """
        Create service instance by type
        
        Args:
            service_type: Type of service to create
            **kwargs: Additional service-specific parameters
            
        Returns:
            BaseService: Created service instance
            
        Raises:
            ValueError: If service type is unknown
        """
        service_map = {
            'ai_service': self._create_ai_service,
            'database_service': self._create_database_service,
            'alias_service': self._create_alias_service,
            'cache_service': self._create_cache_service,
            'report_service': self._create_report_service,
            'classification_service': self._create_classification_service,
            'pattern_engine': self._create_pattern_engine
        }
        
        if service_type not in service_map:
            raise ValueError(f"Unknown service type: {service_type}")
        
        service = service_map[service_type](**kwargs)
        self._services[service_type] = service
        
        return service
    
    def get_service(self, service_type: str) -> Optional[BaseService]:
        """
        Get existing service instance
        
        Args:
            service_type: Type of service to retrieve
            
        Returns:
            BaseService or None if not found
        """
        return self._services.get(service_type)
    
    def shutdown_all_services(self) -> bool:
        """
        Shutdown all managed services
        
        Returns:
            bool: True if all services shutdown successfully
        """
        success = True
        for service_type, service in self._services.items():
            try:
                if not service.shutdown():
                    success = False
                    self.logger.error(f"Failed to shutdown {service_type}")
            except Exception as e:
                success = False
                self.logger.error(f"Error shutting down {service_type}: {e}")
        
        self._services.clear()
        return success
    
    def _create_ai_service(self, **kwargs):
        """Create AI service instance (implementation imported dynamically)"""
        from pii_scanner_poc.services.ai_service import AIService
        return AIService(self.config, **kwargs)
    
    def _create_database_service(self, **kwargs):
        """Create database service instance"""
        from pii_scanner_poc.services.database_service import DatabaseService
        return DatabaseService(self.config, **kwargs)
    
    def _create_alias_service(self, **kwargs):
        """Create alias service instance"""
        from pii_scanner_poc.services.local_alias_database import LocalAliasService
        return LocalAliasService(self.config, **kwargs)
    
    def _create_cache_service(self, **kwargs):
        """Create cache service instance"""
        from pii_scanner_poc.services.schema_cache_service import SchemaCacheService
        return SchemaCacheService(self.config, **kwargs)
    
    def _create_report_service(self, **kwargs):
        """Create report service instance"""
        from pii_scanner_poc.services.report_service import ReportService
        return ReportService(self.config, **kwargs)
    
    def _create_classification_service(self, **kwargs):
        """Create classification service instance"""
        from pii_scanner_poc.core.hybrid_classification_orchestrator import HybridClassificationOrchestrator
        return HybridClassificationOrchestrator(self.config, **kwargs)
    
    def _create_pattern_engine(self, **kwargs):
        """Create pattern engine instance"""
        from pii_scanner_poc.core.inhouse_classification_engine import InhouseClassificationEngine
        return InhouseClassificationEngine(self.config, **kwargs)