"""
Enhanced Data Models for Hybrid Schema Sensitivity Classification System
Provides comprehensive data structures for advanced pattern recognition and caching
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Union
from enum import Enum
from datetime import datetime
import hashlib
import json

from .data_models import Regulation, RiskLevel, PIIType


class DetectionMethod(Enum):
    """Method used to detect sensitivity"""
    LOCAL_PATTERN = "local_pattern"
    LOCAL_FUZZY = "local_fuzzy"
    LOCAL_CONTEXT = "local_context"
    LOCAL_SYNONYM = "local_synonym"
    LLM_ANALYSIS = "llm_analysis"
    CACHE_HIT = "cache_hit"
    HYBRID = "hybrid"


class ConfidenceLevel(Enum):
    """Confidence level in classification"""
    VERY_HIGH = "very_high"  # 95-100%
    HIGH = "high"            # 85-94%
    MEDIUM = "medium"        # 70-84%
    LOW = "low"              # 50-69%
    VERY_LOW = "very_low"    # <50%


@dataclass
class SensitivityPattern:
    """Pattern for local sensitivity detection"""
    pattern_id: str
    pattern_name: str
    pattern_type: str  # exact, fuzzy, regex, context
    pattern_value: str
    pii_type: PIIType
    risk_level: RiskLevel
    applicable_regulations: List[Regulation]
    confidence: float
    region_specific: Optional[str] = None
    company_specific: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    context_keywords: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0


@dataclass
class CompanyAlias:
    """Company-specific field aliases"""
    company_id: str
    company_name: str
    field_aliases: Dict[str, List[str]]  # standard_field -> [alias1, alias2, ...]
    region: Optional[str] = None
    industry: Optional[str] = None
    confidence_threshold: float = 0.8
    created_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)


@dataclass
class RegionSpecificRule:
    """Region-specific classification rules"""
    region_code: str
    region_name: str
    regulation: Regulation
    specific_patterns: List[SensitivityPattern]
    cultural_aliases: Dict[str, List[str]]
    language_variants: Dict[str, List[str]]
    compliance_notes: str
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class EnhancedFieldAnalysis:
    """Enhanced analysis result for a single field"""
    field_name: str
    table_name: str
    schema_name: str
    data_type: str
    
    # Classification results
    is_sensitive: bool
    pii_type: PIIType
    risk_level: RiskLevel
    applicable_regulations: List[Regulation]
    confidence_score: float
    confidence_level: ConfidenceLevel
    
    # Detection details
    detection_method: DetectionMethod
    matched_patterns: List[str] = field(default_factory=list)
    rationale: str = ""
    justification: str = ""
    
    # Context information
    similar_fields: List[str] = field(default_factory=list)
    context_clues: List[str] = field(default_factory=list)
    synonyms_matched: List[str] = field(default_factory=list)
    
    # Company/Region specific
    company_alias_matched: Optional[str] = None
    region_specific_rule: Optional[str] = None
    
    # Performance metrics
    processing_time: float = 0.0
    cache_hit: bool = False
    llm_required: bool = False
    
    # Audit trail
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    analyzer_version: str = "1.0"


@dataclass
class SchemaFingerprint:
    """Unique fingerprint for schema caching"""
    schema_hash: str
    table_names: List[str]
    column_names: List[str]
    data_types: List[str]
    regulation: Regulation
    region: Optional[str] = None
    company_id: Optional[str] = None
    
    def __post_init__(self):
        """Generate hash if not provided"""
        if not self.schema_hash:
            content = {
                'tables': sorted(self.table_names),
                'columns': sorted(self.column_names),
                'types': sorted(self.data_types),
                'regulation': self.regulation.value,
                'region': self.region,
                'company': self.company_id
            }
            self.schema_hash = hashlib.sha256(
                json.dumps(content, sort_keys=True).encode()
            ).hexdigest()[:16]


@dataclass
class CachedClassification:
    """Cached classification result"""
    fingerprint: SchemaFingerprint
    classifications: List[EnhancedFieldAnalysis]
    cache_metadata: Dict[str, Any]
    created_date: datetime
    last_accessed: datetime
    access_count: int = 0
    cache_version: str = "1.0"
    
    def update_access(self):
        """Update access statistics"""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class LLMPromptTemplate:
    """Template for LLM prompt generation"""
    template_id: str
    template_name: str
    prompt_type: str  # few_shot, chain_of_thought, multi_step
    base_template: str
    examples: List[Dict[str, str]] = field(default_factory=list)
    context_variables: List[str] = field(default_factory=list)
    optimization_notes: str = ""
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    created_date: datetime = field(default_factory=datetime.now)
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    cost_per_use: float = 0.0


@dataclass
class LLMInteraction:
    """Detailed LLM interaction logging"""
    interaction_id: str
    session_id: str
    prompt_template_id: str
    
    # Request details
    full_prompt: str
    system_message: str
    user_message: str
    model_name: str
    temperature: float
    max_tokens: int
    
    # Response details
    response_content: str
    response_tokens: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    
    # Context
    fields_analyzed: List[str] = field(default_factory=list)
    regulation: Optional[Regulation] = None
    region: Optional[str] = None
    company_id: Optional[str] = None
    
    # Results
    classifications_extracted: int = 0
    confidence_scores: List[float] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    cost_estimate: float = 0.0
    retry_count: int = 0


@dataclass
class WorkflowStep:
    """Individual step in the classification workflow"""
    step_id: str
    step_name: str
    step_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    
    # Step-specific data
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def complete_step(self, success: bool = True, error_message: str = None):
        """Mark step as completed"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.error_message = error_message


@dataclass
class HybridClassificationSession:
    """Complete session for hybrid classification"""
    session_id: str
    start_time: datetime
    schema_fingerprint: SchemaFingerprint
    regulations: List[Regulation]
    end_time: Optional[datetime] = None
    region: Optional[str] = None
    company_id: Optional[str] = None
    
    # Processing results
    total_fields: int = 0
    local_classifications: int = 0
    llm_classifications: int = 0
    cache_hits: int = 0
    
    # Performance metrics
    total_processing_time: float = 0.0
    local_processing_time: float = 0.0
    llm_processing_time: float = 0.0
    cache_processing_time: float = 0.0
    
    # Quality metrics
    high_confidence_results: int = 0
    low_confidence_results: int = 0
    validation_errors: int = 0
    
    # Workflow tracking
    workflow_steps: List[WorkflowStep] = field(default_factory=list)
    llm_interactions: List[str] = field(default_factory=list)  # Interaction IDs
    
    # Results
    field_analyses: List[EnhancedFieldAnalysis] = field(default_factory=list)
    summary_report: Dict[str, Any] = field(default_factory=dict)
    
    def add_workflow_step(self, step: WorkflowStep):
        """Add a workflow step"""
        self.workflow_steps.append(step)
    
    def complete_session(self):
        """Mark session as completed"""
        self.end_time = datetime.now()
        if self.start_time:
            self.total_processing_time = (self.end_time - self.start_time).total_seconds()


@dataclass
class SystemPerformanceMetrics:
    """System-wide performance metrics"""
    date: datetime
    
    # Classification metrics
    total_schemas_processed: int = 0
    total_fields_analyzed: int = 0
    local_detection_rate: float = 0.0  # Target: ≥95%
    llm_usage_rate: float = 0.0        # Target: ≤5%
    cache_hit_rate: float = 0.0
    
    # Performance metrics
    avg_processing_time: float = 0.0
    avg_fields_per_second: float = 0.0
    system_uptime: float = 0.0
    
    # Quality metrics
    accuracy_rate: float = 0.0
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    
    # Cost metrics
    llm_cost_per_schema: float = 0.0
    total_llm_cost: float = 0.0
    cost_savings_from_cache: float = 0.0
    
    # Error metrics
    total_errors: int = 0
    llm_errors: int = 0
    cache_errors: int = 0
    validation_errors: int = 0


# Utility functions for data model operations

def create_schema_fingerprint(tables_data: Dict[str, List], regulation: Regulation, 
                            region: str = None, company_id: str = None) -> SchemaFingerprint:
    """Create a schema fingerprint for caching"""
    table_names = list(tables_data.keys())
    column_names = []
    data_types = []
    
    for table_name, columns in tables_data.items():
        for column in columns:
            if hasattr(column, 'column_name'):
                column_names.append(f"{table_name}.{column.column_name}")
                data_types.append(column.data_type)
    
    return SchemaFingerprint(
        schema_hash="",  # Will be generated in __post_init__
        table_names=table_names,
        column_names=column_names,
        data_types=data_types,
        regulation=regulation,
        region=region,
        company_id=company_id
    )


def calculate_confidence_level(confidence_score: float) -> ConfidenceLevel:
    """Convert confidence score to confidence level"""
    if confidence_score >= 0.95:
        return ConfidenceLevel.VERY_HIGH
    elif confidence_score >= 0.85:
        return ConfidenceLevel.HIGH
    elif confidence_score >= 0.70:
        return ConfidenceLevel.MEDIUM
    elif confidence_score >= 0.50:
        return ConfidenceLevel.LOW
    else:
        return ConfidenceLevel.VERY_LOW


def merge_field_analyses(local_analysis: EnhancedFieldAnalysis, 
                        llm_analysis: Optional[EnhancedFieldAnalysis]) -> EnhancedFieldAnalysis:
    """Merge local and LLM analysis results"""
    if not llm_analysis:
        return local_analysis
    
    # Create hybrid result
    merged = EnhancedFieldAnalysis(
        field_name=local_analysis.field_name,
        table_name=local_analysis.table_name,
        schema_name=local_analysis.schema_name,
        data_type=local_analysis.data_type,
        
        # Use higher confidence classification
        is_sensitive=local_analysis.is_sensitive or llm_analysis.is_sensitive,
        pii_type=llm_analysis.pii_type if llm_analysis.confidence_score > local_analysis.confidence_score else local_analysis.pii_type,
        risk_level=max(local_analysis.risk_level, llm_analysis.risk_level, key=lambda x: x.value),
        applicable_regulations=list(set(local_analysis.applicable_regulations + llm_analysis.applicable_regulations)),
        confidence_score=max(local_analysis.confidence_score, llm_analysis.confidence_score),
        confidence_level=calculate_confidence_level(max(local_analysis.confidence_score, llm_analysis.confidence_score)),
        
        detection_method=DetectionMethod.HYBRID,
        matched_patterns=local_analysis.matched_patterns + llm_analysis.matched_patterns,
        rationale=f"Local: {local_analysis.rationale} | LLM: {llm_analysis.rationale}",
        justification=f"Hybrid analysis - Local confidence: {local_analysis.confidence_score:.2f}, LLM confidence: {llm_analysis.confidence_score:.2f}",
        
        similar_fields=list(set(local_analysis.similar_fields + llm_analysis.similar_fields)),
        context_clues=list(set(local_analysis.context_clues + llm_analysis.context_clues)),
        synonyms_matched=list(set(local_analysis.synonyms_matched + llm_analysis.synonyms_matched)),
        
        company_alias_matched=local_analysis.company_alias_matched or llm_analysis.company_alias_matched,
        region_specific_rule=local_analysis.region_specific_rule or llm_analysis.region_specific_rule,
        
        processing_time=local_analysis.processing_time + llm_analysis.processing_time,
        cache_hit=local_analysis.cache_hit,
        llm_required=True,
        
        analysis_timestamp=datetime.now(),
        analyzer_version="1.0-hybrid"
    )
    
    return merged