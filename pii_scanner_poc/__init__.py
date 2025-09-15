"""
PII Scanner POC Package
Enterprise-grade PII/PHI detection and classification system
"""

__version__ = "2.0.0"
__author__ = "PII Scanner Team"
__description__ = "Enterprise PII/PHI Scanner with Enhanced Regulatory Compliance"

# Package-level imports for easy access
from .core.pii_scanner_facade import PIIScannerFacade
from .core.hybrid_classification_orchestrator import HybridClassificationOrchestrator
from .models.data_models import PIIType, RiskLevel, Regulation, ColumnMetadata
from .services.database_service import DatabaseService

__all__ = [
    'PIIScannerFacade',
    'HybridClassificationOrchestrator', 
    'PIIType',
    'RiskLevel',
    'Regulation',
    'ColumnMetadata',
    'DatabaseService'
]