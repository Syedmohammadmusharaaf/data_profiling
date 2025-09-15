"""
Data models for PII Scanner
Contains all data structures used throughout the application
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

# Import the new base classes
from pii_scanner_poc.utils.base_classes import ToDictMixin

class RiskLevel(Enum):
    """Risk level enumeration"""
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
    UNKNOWN = "Unknown"

class PIIType(Enum):
    """Types of PII/PHI data"""
    NAME = "Name"
    EMAIL = "Email"
    PHONE = "Phone"
    ADDRESS = "Address"
    ID = "ID"
    SSN = "SSN"
    MEDICAL = "Medical"
    FINANCIAL = "Financial"
    BIOMETRIC = "Biometric"
    NETWORK = "Network"
    DATE = "Date"
    OTHER = "Other"
    NONE = "None"

class Regulation(Enum):
    """Privacy regulations"""
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    CCPA = "CCPA"
    PCI_DSS = "PCI-DSS"
    AUTO = "AUTO"  # Context-based automatic determination

@dataclass
class ColumnMetadata:
    """Metadata for a database column"""
    schema_name: str
    table_name: str
    column_name: str
    data_type: str
    is_nullable: Optional[bool] = None
    max_length: Optional[int] = None
    default_value: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get the fully qualified column name"""
        if self.schema_name:
            return f"{self.schema_name}.{self.table_name}.{self.column_name}"
        return f"{self.table_name}.{self.column_name}"

@dataclass
@dataclass
class PIIAnalysisResult(ToDictMixin):
    """Result of PII analysis for a single column"""
    column_name: str
    data_type: str
    is_sensitive: bool
    sensitivity_level: RiskLevel
    pii_type: PIIType
    applicable_regulations: List[Regulation]
    confidence_score: float
    risk_explanation: str
    recommendations: List[str] = field(default_factory=list)


@dataclass
class TableAnalysisResult(ToDictMixin):
    """Result of PII analysis for a complete table"""
    table_name: str
    risk_level: RiskLevel
    total_columns: int
    sensitive_columns: int
    applicable_regulations: List[Regulation]
    column_analysis: List[PIIAnalysisResult]
    processing_method: str
    analysis_timestamp: datetime
    batch_info: Optional[Dict[str, Any]] = None
    
    @property
    def sensitivity_ratio(self) -> float:
        """Calculate the ratio of sensitive columns"""
        return self.sensitive_columns / self.total_columns if self.total_columns > 0 else 0.0
    
    def get_columns_by_risk(self, risk_level: RiskLevel) -> List[PIIAnalysisResult]:
        """Get columns filtered by risk level"""
        return [col for col in self.column_analysis if col.sensitivity_level == risk_level]
    
    def get_columns_by_regulation(self, regulation: Regulation) -> List[PIIAnalysisResult]:
        """Get columns applicable to a specific regulation"""
        return [col for col in self.column_analysis if regulation in col.applicable_regulations]
    
@dataclass
class BatchAnalysisRequest(ToDictMixin):
    """Request for batch analysis"""
    tables: Dict[str, List[ColumnMetadata]]
    regulations: List[Regulation]
    batch_number: int
    total_batches: int
    
    @property
    def total_columns(self) -> int:
        """Get total number of columns in this batch"""
        return sum(len(columns) for columns in self.tables.values())
    
    @property
    def table_names(self) -> List[str]:
        """Get list of table names in this batch"""
        return list(self.tables.keys())

@dataclass
class BatchAnalysisResponse:
    """Response from batch analysis"""
    request: BatchAnalysisRequest
    results: List[TableAnalysisResult]
    success: bool
    processing_time: float
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'batch_analysis': {
                'batch_number': self.request.batch_number,
                'total_batches': self.request.total_batches,
                'total_tables': len(self.request.tables),
                'total_columns': self.request.total_columns,
                'regulations_checked': [reg.value for reg in self.request.regulations],
                'processing_time': self.processing_time,
                'success': self.success,
                'retry_count': self.retry_count,
                'error_message': self.error_message
            },
            'table_results': [result.to_dict() for result in self.results]
        }

@dataclass
class AIModelResponse:
    """Response from AI model"""
    content: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    
    @property
    def is_truncated(self) -> bool:
        """Check if response appears to be truncated"""
        if not self.content:
            return True
        
        # Simple truncation detection
        content_stripped = self.content.strip()
        return not (content_stripped.endswith('}') or content_stripped.endswith('}\n'))

@dataclass
class JSONExtractionAttempt:
    """Details of a JSON extraction attempt"""
    method: str
    success: bool
    extracted_content: Optional[str]
    error_message: Optional[str]
    processing_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            'method': self.method,
            'success': self.success,
            'content_length': len(self.extracted_content) if self.extracted_content else 0,
            'error_message': self.error_message,
            'processing_time': self.processing_time
        }

@dataclass
class AnalysisSession:
    """Complete analysis session information"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_tables: int
    total_columns: int
    regulations: List[Regulation]
    results: List[TableAnalysisResult]
    processing_summary: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_processing_time(self) -> Optional[float]:
        """Calculate total processing time"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def total_sensitive_columns(self) -> int:
        """Get total number of sensitive columns found"""
        return sum(result.sensitive_columns for result in self.results)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_processing_time': self.total_processing_time,
            'total_tables': self.total_tables,
            'total_columns': self.total_columns,
            'total_sensitive_columns': self.total_sensitive_columns,
            'regulations': [reg.value for reg in self.regulations],
            'processing_summary': self.processing_summary,
            'results': [result.to_dict() for result in self.results]
        }

# Utility functions for model conversion
def convert_string_to_risk_level(level_str: str) -> RiskLevel:
    """Convert string to RiskLevel enum"""
    try:
        return RiskLevel(level_str)
    except ValueError:
        return RiskLevel.UNKNOWN

def convert_string_to_pii_type(type_str: str) -> PIIType:
    """Convert string to PIIType enum"""
    try:
        return PIIType(type_str)
    except ValueError:
        return PIIType.OTHER

def convert_string_to_regulation(reg_str: str) -> Regulation:
    """Convert string to Regulation enum"""
    try:
        return Regulation(reg_str)
    except ValueError:
        raise ValueError(f"Unknown regulation: {reg_str}")

def convert_strings_to_regulations(reg_list: List[str]) -> List[Regulation]:
    """Convert list of strings to list of Regulation enums"""
    return [convert_string_to_regulation(reg) for reg in reg_list]