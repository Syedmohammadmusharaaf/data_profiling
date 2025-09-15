"""
Comprehensive Logging System for Hybrid Classification
Separate, detailed logging for workflow and LLM interactions with audit compliance
"""

import json
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from pii_scanner_poc.models.enhanced_data_models import (
    WorkflowStep, LLMInteraction, HybridClassificationSession,
    SystemPerformanceMetrics
)
from pii_scanner_poc.utils.logging_config import PIILogger


class WorkflowLogger:
    """Specialized logger for workflow tracking and debugging"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup workflow logger
        self.logger = logging.getLogger("hybrid_workflow")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Workflow log file handler
        workflow_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "workflow_trace.log",
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        workflow_handler.setLevel(logging.DEBUG)
        workflow_formatter = logging.Formatter(
            '%(asctime)s | WORKFLOW | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        workflow_handler.setFormatter(workflow_formatter)
        
        # JSON structured workflow log
        json_workflow_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "workflow_structured.json",
            maxBytes=50*1024*1024,
            backupCount=10
        )
        json_workflow_handler.setLevel(logging.DEBUG)
        json_workflow_handler.setFormatter(WorkflowJSONFormatter())
        
        self.logger.addHandler(workflow_handler)
        self.logger.addHandler(json_workflow_handler)
        
        self.logger.info("Workflow logger initialized", extra={
            'component': 'workflow_logger',
            'log_dir': str(self.log_dir)
        })
    
    def log_session_start(self, session: HybridClassificationSession):
        """Log start of classification session"""
        self.logger.info("Classification session started", extra={
            'event_type': 'session_start',
            'session_id': session.session_id,
            'regulations': [reg.value for reg in session.regulations],
            'region': session.region,
            'company_id': session.company_id,
            'schema_hash': session.schema_fingerprint.schema_hash,
            'total_fields': session.total_fields
        })
    
    def log_session_end(self, session: HybridClassificationSession):
        """Log end of classification session"""
        self.logger.info("Classification session completed", extra={
            'event_type': 'session_end',
            'session_id': session.session_id,
            'total_processing_time': session.total_processing_time,
            'local_classifications': session.local_classifications,
            'llm_classifications': session.llm_classifications,
            'cache_hits': session.cache_hits,
            'high_confidence_results': session.high_confidence_results,
            'low_confidence_results': session.low_confidence_results,
            'validation_errors': session.validation_errors
        })
    
    def log_workflow_step(self, step: WorkflowStep):
        """Log individual workflow step"""
        if step.end_time:
            self.logger.info(f"Workflow step completed: {step.step_name}", extra={
                'event_type': 'workflow_step',
                'step_id': step.step_id,
                'step_name': step.step_name,
                'step_type': step.step_type,
                'duration': step.duration,
                'success': step.success,
                'error_message': step.error_message,
                'performance_metrics': step.performance_metrics
            })
        else:
            self.logger.info(f"Workflow step started: {step.step_name}", extra={
                'event_type': 'workflow_step_start',
                'step_id': step.step_id,
                'step_name': step.step_name,
                'step_type': step.step_type
            })
    
    def log_cache_operation(self, operation: str, cache_key: str, hit: bool = None, 
                          metadata: Dict[str, Any] = None):
        """Log cache operations with sanitized data"""
        # Sanitize cache key to avoid logging sensitive data
        sanitized_key = self._sanitize_cache_key(cache_key)
        
        log_data = {
            'event_type': 'cache_operation',
            'operation': operation,
            'cache_key': sanitized_key,
            'metadata': self._sanitize_metadata(metadata or {})
        }
        
        if hit is not None:
            log_data['cache_hit'] = hit
        
        self.logger.info(f"Cache {operation}: {sanitized_key}", extra=log_data)
    
    def _sanitize_cache_key(self, cache_key: str) -> str:
        """Sanitize cache key to remove potential sensitive data"""
        # Remove email patterns
        import re
        sanitized = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '***@***.***', cache_key)
        
        # Remove potential phone numbers
        sanitized = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '***-***-****', sanitized)
        
        # Remove potential SSN patterns
        sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****', sanitized)
        
        return sanitized
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata to remove sensitive information"""
        sanitized = {}
        sensitive_keys = {'password', 'token', 'key', 'secret', 'credential', 'ssn', 'email'}
        
        for key, value in metadata.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '***REDACTED***'
            elif isinstance(value, str):
                # Sanitize string values
                sanitized[key] = self._sanitize_string_value(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_string_value(self, value: str) -> str:
        """Sanitize string values to remove sensitive patterns"""
        import re
        
        # Remove email patterns
        sanitized = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '***@***.***', value)
        
        # Remove phone patterns
        sanitized = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '***-***-****', sanitized)
        
        # Remove SSN patterns
        sanitized = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****', sanitized)
        
        # Remove credit card patterns
        sanitized = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '****-****-****-****', sanitized)
        
        return sanitized
    
    def log_pattern_match(self, field_name: str, pattern_id: str, method: str, 
                         confidence: float, table_context: List[str] = None):
        """Log pattern matching results"""
        self.logger.debug(f"Pattern match: {field_name} -> {pattern_id}", extra={
            'event_type': 'pattern_match',
            'field_name': field_name,
            'pattern_id': pattern_id,
            'detection_method': method,
            'confidence': confidence,
            'table_context': table_context or []
        })
    
    def log_validation_result(self, field_name: str, validation_type: str, 
                            passed: bool, details: Dict[str, Any] = None):
        """Log validation results"""
        level = logging.INFO if passed else logging.WARNING
        self.logger.log(level, f"Validation {validation_type}: {field_name}", extra={
            'event_type': 'validation_result',
            'field_name': field_name,
            'validation_type': validation_type,
            'passed': passed,
            'details': details or {}
        })
    
    def log_performance_metrics(self, metrics: SystemPerformanceMetrics):
        """Log system performance metrics"""
        self.logger.info("Performance metrics recorded", extra={
            'event_type': 'performance_metrics',
            'date': metrics.date.isoformat(),
            'total_schemas_processed': metrics.total_schemas_processed,
            'total_fields_analyzed': metrics.total_fields_analyzed,
            'local_detection_rate': metrics.local_detection_rate,
            'llm_usage_rate': metrics.llm_usage_rate,
            'cache_hit_rate': metrics.cache_hit_rate,
            'avg_processing_time': metrics.avg_processing_time,
            'accuracy_rate': metrics.accuracy_rate,
            'total_errors': metrics.total_errors
        })
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log errors with context"""
        self.logger.error(f"Error: {error_type}", extra={
            'event_type': 'error',
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        })


class LLMInteractionLogger:
    """Specialized logger for LLM interactions and debugging"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup LLM interaction logger
        self.logger = logging.getLogger("llm_interactions")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # LLM interaction log file handler
        llm_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "llm_interactions.log",
            maxBytes=100*1024*1024,  # 100MB
            backupCount=15
        )
        llm_handler.setLevel(logging.DEBUG)
        llm_formatter = logging.Formatter(
            '%(asctime)s | LLM | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        llm_handler.setFormatter(llm_formatter)
        
        # JSON structured LLM log
        json_llm_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "llm_interactions_structured.json",
            maxBytes=100*1024*1024,
            backupCount=15
        )
        json_llm_handler.setLevel(logging.DEBUG)
        json_llm_handler.setFormatter(LLMJSONFormatter())
        
        # Separate prompt/response archive
        prompt_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "llm_prompts_responses.log",
            maxBytes=200*1024*1024,  # 200MB for full prompts
            backupCount=20
        )
        prompt_handler.setLevel(logging.INFO)
        prompt_formatter = logging.Formatter(
            '%(asctime)s | PROMPT_RESPONSE | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        prompt_handler.setFormatter(prompt_formatter)
        
        self.logger.addHandler(llm_handler)
        self.logger.addHandler(json_llm_handler)
        self.logger.addHandler(prompt_handler)
        
        self.logger.info("LLM interaction logger initialized", extra={
            'component': 'llm_logger',
            'log_dir': str(self.log_dir)
        })
    
    def log_interaction_start(self, interaction: LLMInteraction):
        """Log start of LLM interaction"""
        self.logger.info(f"LLM interaction started: {interaction.interaction_id}", extra={
            'event_type': 'interaction_start',
            'interaction_id': interaction.interaction_id,
            'session_id': interaction.session_id,
            'prompt_template_id': interaction.prompt_template_id,
            'model_name': interaction.model_name,
            'temperature': interaction.temperature,
            'max_tokens': interaction.max_tokens,
            'fields_count': len(interaction.fields_analyzed),
            'regulation': interaction.regulation.value if interaction.regulation else None,
            'region': interaction.region,
            'company_id': interaction.company_id
        })
    
    def log_interaction_complete(self, interaction: LLMInteraction):
        """Log completion of LLM interaction"""
        level = logging.INFO if interaction.success else logging.ERROR
        
        self.logger.log(level, f"LLM interaction completed: {interaction.interaction_id}", extra={
            'event_type': 'interaction_complete',
            'interaction_id': interaction.interaction_id,
            'session_id': interaction.session_id,
            'success': interaction.success,
            'response_time': interaction.response_time,
            'response_tokens': interaction.response_tokens,
            'classifications_extracted': interaction.classifications_extracted,
            'avg_confidence': sum(interaction.confidence_scores) / len(interaction.confidence_scores) if interaction.confidence_scores else 0.0,
            'error_message': interaction.error_message,
            'retry_count': interaction.retry_count,
            'cost_estimate': interaction.cost_estimate
        })
    
    def log_full_prompt_response(self, interaction: LLMInteraction):
        """Log full prompt and response for debugging"""
        prompt_response_data = {
            'interaction_id': interaction.interaction_id,
            'timestamp': interaction.timestamp.isoformat(),
            'prompt_template_id': interaction.prompt_template_id,
            'system_message': interaction.system_message,
            'full_prompt': interaction.full_prompt,
            'response_content': interaction.response_content,
            'success': interaction.success,
            'error_message': interaction.error_message
        }
        
        # Log as JSON for easier parsing
        self.logger.info(json.dumps(prompt_response_data, ensure_ascii=False))
    
    def log_prompt_optimization(self, template_id: str, optimization_type: str, 
                              before_metrics: Dict[str, float], 
                              after_metrics: Dict[str, float]):
        """Log prompt optimization results"""
        self.logger.info(f"Prompt optimization: {template_id}", extra={
            'event_type': 'prompt_optimization',
            'template_id': template_id,
            'optimization_type': optimization_type,
            'before_metrics': before_metrics,
            'after_metrics': after_metrics,
            'improvement': {
                key: after_metrics.get(key, 0) - before_metrics.get(key, 0)
                for key in before_metrics.keys()
            }
        })
    
    def log_json_extraction_attempt(self, interaction_id: str, method: str, 
                                  success: bool, error: str = None):
        """Log JSON extraction attempts"""
        level = logging.DEBUG if success else logging.WARNING
        
        self.logger.log(level, f"JSON extraction {method}: {interaction_id}", extra={
            'event_type': 'json_extraction',
            'interaction_id': interaction_id,
            'extraction_method': method,
            'success': success,
            'error': error
        })
    
    def log_cost_analysis(self, session_id: str, total_interactions: int, 
                         total_cost: float, cost_breakdown: Dict[str, float]):
        """Log cost analysis for session"""
        self.logger.info(f"Cost analysis for session: {session_id}", extra={
            'event_type': 'cost_analysis',
            'session_id': session_id,
            'total_interactions': total_interactions,
            'total_cost': total_cost,
            'avg_cost_per_interaction': total_cost / total_interactions if total_interactions > 0 else 0,
            'cost_breakdown': cost_breakdown
        })


class WorkflowJSONFormatter(logging.Formatter):
    """JSON formatter for workflow logs"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 'funcName', 
                          'created', 'msecs', 'relativeCreated', 'thread', 
                          'threadName', 'processName', 'process', 'getMessage', 'message']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class LLMJSONFormatter(logging.Formatter):
    """JSON formatter for LLM interaction logs"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 'funcName', 
                          'created', 'msecs', 'relativeCreated', 'thread', 
                          'threadName', 'processName', 'process', 'getMessage', 'message']:
                # Handle special serialization for complex objects
                if hasattr(value, '__dict__'):
                    try:
                        log_entry[key] = asdict(value)
                    except:
                        log_entry[key] = str(value)
                else:
                    log_entry[key] = value
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class AuditLogger:
    """Specialized logger for regulatory compliance and audit trails"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup audit logger
        self.logger = logging.getLogger("audit_trail")
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Audit log handler (never rotated for compliance)
        audit_handler = logging.FileHandler(
            self.log_dir / f"audit_trail_{datetime.now().strftime('%Y%m%d')}.log"
        )
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            '%(asctime)s | AUDIT | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        audit_handler.setFormatter(audit_formatter)
        
        self.logger.addHandler(audit_handler)
        
        self.logger.info("Audit logger initialized", extra={
            'component': 'audit_logger',
            'log_dir': str(self.log_dir)
        })
    
    def log_data_access(self, user_id: str, data_type: str, operation: str, 
                       records_affected: int, compliance_context: Dict[str, Any]):
        """Log data access for compliance"""
        self.logger.info(f"Data access: {operation} on {data_type}", extra={
            'event_type': 'data_access',
            'user_id': user_id,
            'data_type': data_type,
            'operation': operation,
            'records_affected': records_affected,
            'compliance_context': compliance_context,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_classification_decision(self, field_name: str, classification: str, 
                                  method: str, confidence: float, 
                                  regulation: str, justification: str):
        """Log classification decisions for audit"""
        self.logger.info(f"Classification decision: {field_name} -> {classification}", extra={
            'event_type': 'classification_decision',
            'field_name': field_name,
            'classification': classification,
            'detection_method': method,
            'confidence_score': confidence,
            'regulation': regulation,
            'justification': justification,
            'timestamp': datetime.now().isoformat()
        })
    
    def log_system_event(self, event_type: str, description: str, 
                        severity: str, metadata: Dict[str, Any]):
        """Log system events for compliance"""
        level = getattr(logging, severity.upper(), logging.INFO)
        
        self.logger.log(level, f"System event: {event_type}", extra={
            'event_type': 'system_event',
            'system_event_type': event_type,
            'description': description,
            'severity': severity,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        })


class HybridLoggingManager:
    """Central manager for all hybrid classification logging"""
    
    def __init__(self, log_dir: str = "logs"):
        self.workflow_logger = WorkflowLogger(log_dir)
        self.llm_logger = LLMInteractionLogger(log_dir)
        self.audit_logger = AuditLogger(log_dir)
        
        # Statistics tracking
        self.session_stats: Dict[str, Dict[str, Any]] = {}
        
    def start_session_logging(self, session: HybridClassificationSession):
        """Start logging for a classification session"""
        self.workflow_logger.log_session_start(session)
        self.session_stats[session.session_id] = {
            'start_time': session.start_time,
            'workflow_steps': 0,
            'llm_interactions': 0,
            'errors': 0
        }
    
    def end_session_logging(self, session: HybridClassificationSession):
        """End logging for a classification session"""
        self.workflow_logger.log_session_end(session)
        
        if session.session_id in self.session_stats:
            stats = self.session_stats[session.session_id]
            self.workflow_logger.logger.info("Session statistics", extra={
                'event_type': 'session_statistics',
                'session_id': session.session_id,
                'workflow_steps': stats['workflow_steps'],
                'llm_interactions': stats['llm_interactions'],
                'errors': stats['errors'],
                'duration': session.total_processing_time
            })
            
            del self.session_stats[session.session_id]
    
    def log_workflow_step(self, session_id: str, step: WorkflowStep):
        """Log workflow step with session tracking"""
        self.workflow_logger.log_workflow_step(step)
        
        if session_id in self.session_stats:
            self.session_stats[session_id]['workflow_steps'] += 1
            if not step.success:
                self.session_stats[session_id]['errors'] += 1
    
    def log_llm_interaction(self, session_id: str, interaction: LLMInteraction):
        """Log LLM interaction with session tracking"""
        self.llm_logger.log_interaction_start(interaction)
        self.llm_logger.log_interaction_complete(interaction)
        self.llm_logger.log_full_prompt_response(interaction)
        
        if session_id in self.session_stats:
            self.session_stats[session_id]['llm_interactions'] += 1
            if not interaction.success:
                self.session_stats[session_id]['errors'] += 1
    
    def get_logging_statistics(self) -> Dict[str, Any]:
        """Get comprehensive logging statistics"""
        return {
            'active_sessions': len(self.session_stats),
            'session_stats': self.session_stats.copy(),
            'log_directory': str(self.workflow_logger.log_dir),
            'log_files': {
                'workflow_trace': (self.workflow_logger.log_dir / "workflow_trace.log").exists(),
                'workflow_structured': (self.workflow_logger.log_dir / "workflow_structured.json").exists(),
                'llm_interactions': (self.llm_logger.log_dir / "llm_interactions.log").exists(),
                'llm_structured': (self.llm_logger.log_dir / "llm_interactions_structured.json").exists(),
                'prompts_responses': (self.llm_logger.log_dir / "llm_prompts_responses.log").exists(),
                'audit_trail': any(self.audit_logger.log_dir.glob("audit_trail_*.log"))
            }
        }


# Global logging manager instance
hybrid_logging_manager = HybridLoggingManager()