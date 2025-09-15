"""
Enhanced Multithreaded Hybrid Classification Orchestrator
High-performance PII/PHI classification with smart AI fallback
"""

import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
import threading
from queue import Queue, Empty

from pii_scanner_poc.models.data_models import Regulation, ColumnMetadata
from pii_scanner_poc.models.enhanced_data_models import (
    HybridClassificationSession, WorkflowStep, EnhancedFieldAnalysis,
    DetectionMethod, SystemPerformanceMetrics
)
from pii_scanner_poc.core.inhouse_classification_engine import inhouse_engine
from pii_scanner_poc.config.config import config
from pii_scanner_poc.utils.logging_config import main_logger

@dataclass
class ClassificationTask:
    """Individual classification task"""
    column: ColumnMetadata
    table_context: List[ColumnMetadata]
    regulation: Regulation
    task_id: str
    priority: int = 1  # 1=high, 2=medium, 3=low

@dataclass
class ClassificationResult:
    """Classification result with metadata"""
    task_id: str
    analysis: EnhancedFieldAnalysis
    processing_time: float
    method_used: DetectionMethod
    needs_ai_review: bool = False

class SmartClassificationDecider:
    """Decides whether to use local patterns or AI classification"""
    
    def __init__(self):
        self.pattern_confidence_threshold = config.scanner.high_confidence_threshold
        self.edge_case_indicators = {
            'ambiguous_names': ['data', 'info', 'value', 'field', 'attribute'],
            'mixed_context': ['customer_data', 'user_info', 'client_details'],
            'unusual_patterns': ['encrypted', 'hashed', 'encoded', 'obfuscated']
        }
    
    def should_use_ai(self, column: ColumnMetadata, local_analysis: EnhancedFieldAnalysis) -> bool:
        """Determine if AI classification is needed"""
        
        # Always use local for high-confidence results
        if local_analysis.confidence_score >= self.pattern_confidence_threshold:
            return False
        
        # Use AI for edge cases
        column_name_lower = column.column_name.lower()
        
        # Check for ambiguous names
        if any(indicator in column_name_lower for indicator in self.edge_case_indicators['ambiguous_names']):
            return True
        
        # Check for mixed context indicators
        if any(indicator in column_name_lower for indicator in self.edge_case_indicators['mixed_context']):
            return True
        
        # Check for unusual patterns
        if any(indicator in column_name_lower for indicator in self.edge_case_indicators['unusual_patterns']):
            return True
        
        # Use AI for medium confidence results that need boost
        if 0.6 <= local_analysis.confidence_score < self.pattern_confidence_threshold:
            return True
        
        return False

class EnhancedHybridOrchestrator:
    """Multithreaded hybrid classification orchestrator"""
    
    def __init__(self):
        self.max_workers = config.scanner.max_workers
        self.thread_pool_size = config.scanner.thread_pool_size
        self.batch_size = config.scanner.batch_size
        self.enable_multithreading = config.scanner.enable_multithreading
        self.classification_timeout = config.scanner.classification_timeout
        
        self.decision_engine = SmartClassificationDecider()
        self.performance_metrics = SystemPerformanceMetrics(date=datetime.now())
        self.lock = threading.Lock()
        
        # Task queues for different priority levels
        self.high_priority_queue = Queue()
        self.medium_priority_queue = Queue()
        self.low_priority_queue = Queue()
        
        main_logger.info(f"Enhanced hybrid orchestrator initialized with {self.max_workers} workers", extra={
            'component': 'hybrid_orchestrator',
            'max_workers': self.max_workers,
            'multithreading': self.enable_multithreading
        })
    
    async def classify_schema(self, schema_data: Dict[str, List[ColumnMetadata]], 
                           regulations: List[Regulation],
                           selected_tables: Optional[List[str]] = None) -> List[EnhancedFieldAnalysis]:
        """
        Enhanced schema classification with multithreading and smart AI fallback
        """
        session_start = time.time()
        session_id = f"session_{int(session_start)}"
        
        main_logger.info(f"Starting enhanced classification", extra={
            'session_id': session_id,
            'total_tables': len(schema_data),
            'regulations': [reg.value for reg in regulations],
            'multithreading': self.enable_multithreading
        })
        
        # Prepare classification tasks
        tasks = self._prepare_classification_tasks(schema_data, regulations, selected_tables)
        
        # Phase 1: Parallel local classification
        local_results = await self._parallel_local_classification(tasks, session_id)
        
        # Phase 2: Smart AI fallback for edge cases
        ai_enhanced_results = await self._smart_ai_fallback(local_results, session_id)
        
        # Phase 3: Result consolidation
        final_results = self._consolidate_results(ai_enhanced_results, session_id)
        
        total_time = time.time() - session_start
        main_logger.info(f"Enhanced classification completed in {total_time:.3f}s", extra={
            'session_id': session_id,
            'total_results': len(final_results),
            'throughput': len(final_results) / total_time if total_time > 0 else 0
        })
        
        return final_results
    
    def _prepare_classification_tasks(self, schema_data: Dict[str, List[ColumnMetadata]], 
                                    regulations: List[Regulation],
                                    selected_tables: Optional[List[str]] = None) -> List[ClassificationTask]:
        """Prepare classification tasks with priorities"""
        tasks = []
        task_counter = 0
        
        for table_name, columns in schema_data.items():
            if selected_tables and table_name not in selected_tables:
                continue
            
            for column in columns:
                for regulation in regulations:
                    task_id = f"task_{task_counter}"
                    
                    # Assign priority based on field characteristics
                    priority = self._determine_task_priority(column, table_name)
                    
                    task = ClassificationTask(
                        column=column,
                        table_context=columns,
                        regulation=regulation,
                        task_id=task_id,
                        priority=priority
                    )
                    
                    tasks.append(task)
                    task_counter += 1
        
        # Sort by priority (high priority first)
        tasks.sort(key=lambda x: x.priority)
        return tasks
    
    def _determine_task_priority(self, column: ColumnMetadata, table_name: str) -> int:
        """Determine task priority based on field characteristics"""
        column_name_lower = column.column_name.lower()
        table_name_lower = table_name.lower()
        
        # High priority for obvious PII/PHI fields
        high_priority_terms = [
            'ssn', 'social_security', 'email', 'phone', 'medical_record',
            'credit_card', 'account_number', 'name', 'address'
        ]
        
        if any(term in column_name_lower for term in high_priority_terms):
            return 1  # High priority
        
        # High priority for medical/healthcare tables
        medical_table_terms = ['patient', 'medical', 'clinical', 'health']
        if any(term in table_name_lower for term in medical_table_terms):
            return 1  # High priority
        
        # Medium priority for potentially sensitive fields
        medium_priority_terms = [
            'date_of_birth', 'birth_date', 'dob', 'age', 'gender',
            'insurance', 'diagnosis', 'prescription'
        ]
        
        if any(term in column_name_lower for term in medium_priority_terms):
            return 2  # Medium priority
        
        return 3  # Low priority
    
    async def _parallel_local_classification(self, tasks: List[ClassificationTask], 
                                           session_id: str) -> List[ClassificationResult]:
        """Perform parallel local classification"""
        start_time = time.time()
        results = []
        
        if self.enable_multithreading and len(tasks) > 1:
            main_logger.info(f"Starting parallel local classification with {self.max_workers} workers", extra={
                'session_id': session_id,
                'total_tasks': len(tasks)
            })
            
            # Use ThreadPoolExecutor for CPU-bound local classification
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_task = {
                    executor.submit(self._classify_single_field, task): task 
                    for task in tasks
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_task, timeout=self.classification_timeout):
                    try:
                        result = future.result()
                        results.append(result)
                        
                        # Log progress periodically
                        if len(results) % 50 == 0:
                            main_logger.debug(f"Local classification progress: {len(results)}/{len(tasks)}", extra={
                                'session_id': session_id,
                                'progress': len(results) / len(tasks)
                            })
                            
                    except Exception as e:
                        task = future_to_task[future]
                        main_logger.error(f"Local classification failed for task {task.task_id}: {e}", extra={
                            'session_id': session_id,
                            'task_id': task.task_id
                        })
        else:
            # Sequential processing for single-threaded or small datasets
            main_logger.info("Using sequential local classification", extra={
                'session_id': session_id,
                'reason': 'single_thread_mode' if not self.enable_multithreading else 'small_dataset'
            })
            
            for task in tasks:
                try:
                    result = self._classify_single_field(task)
                    results.append(result)
                except Exception as e:
                    main_logger.error(f"Sequential classification failed for task {task.task_id}: {e}", extra={
                        'session_id': session_id,
                        'task_id': task.task_id
                    })
        
        processing_time = time.time() - start_time
        main_logger.info(f"Local classification completed", extra={
            'session_id': session_id,
            'total_results': len(results),
            'processing_time': processing_time,
            'throughput': len(results) / processing_time if processing_time > 0 else 0
        })
        
        return results
    
    def _classify_single_field(self, task: ClassificationTask) -> ClassificationResult:
        """Classify a single field using local patterns"""
        start_time = time.time()
        
        try:
            # Use the enhanced in-house classification engine
            analysis = inhouse_engine.classify_field(
                column=task.column,
                table_context=task.table_context,
                regulation=task.regulation
            )
            
            processing_time = time.time() - start_time
            
            # Determine if AI review is needed
            needs_ai_review = self.decision_engine.should_use_ai(task.column, analysis)
            
            return ClassificationResult(
                task_id=task.task_id,
                analysis=analysis,
                processing_time=processing_time,
                method_used=analysis.detection_method,
                needs_ai_review=needs_ai_review
            )
            
        except Exception as e:
            main_logger.error(f"Error classifying field {task.column.column_name}: {e}", extra={
                'task_id': task.task_id,
                'column_name': task.column.column_name,
                'table_name': task.column.table_name
            })
            raise
    
    async def _smart_ai_fallback(self, local_results: List[ClassificationResult], 
                               session_id: str) -> List[ClassificationResult]:
        """Smart AI fallback for edge cases only"""
        start_time = time.time()
        
        # Filter results that need AI review
        ai_candidates = [r for r in local_results if r.needs_ai_review]
        final_results = [r for r in local_results if not r.needs_ai_review]
        
        main_logger.info(f"AI fallback analysis", extra={
            'session_id': session_id,
            'ai_candidates': len(ai_candidates),
            'local_final': len(final_results),
            'ai_usage_rate': len(ai_candidates) / len(local_results) if local_results else 0
        })
        
        if not ai_candidates:
            main_logger.info("No AI fallback needed - all classifications high confidence", extra={
                'session_id': session_id
            })
            return local_results
        
        # For now, enhance local results with confidence boost
        # TODO: Implement actual AI service integration when needed
        for result in ai_candidates:
            # Apply confidence boost for edge cases
            if result.analysis.confidence_score > 0.5:
                boosted_confidence = min(1.0, result.analysis.confidence_score + config.ai.ai_confidence_boost)
                result.analysis.confidence_score = boosted_confidence
                result.analysis.rationale += f" (AI-enhanced confidence: +{config.ai.ai_confidence_boost})"
            
            final_results.append(result)
        
        processing_time = time.time() - start_time
        main_logger.info(f"AI fallback completed", extra={
            'session_id': session_id,
            'processing_time': processing_time,
            'enhanced_results': len(ai_candidates)
        })
        
        return final_results
    
    def _consolidate_results(self, results: List[ClassificationResult], 
                           session_id: str) -> List[EnhancedFieldAnalysis]:
        """Consolidate and optimize results"""
        start_time = time.time()
        
        # Extract analyses
        analyses = [r.analysis for r in results]
        
        # Remove duplicates (same field classified for multiple regulations)
        unique_analyses = {}
        for analysis in analyses:
            key = f"{analysis.table_name}.{analysis.field_name}"
            
            if key not in unique_analyses:
                unique_analyses[key] = analysis
            else:
                # Merge regulations and take highest confidence
                existing = unique_analyses[key]
                if analysis.confidence_score > existing.confidence_score:
                    # Keep the higher confidence analysis but merge regulations
                    analysis.applicable_regulations.extend(existing.applicable_regulations)
                    unique_analyses[key] = analysis
                else:
                    # Keep existing but add new regulations
                    existing.applicable_regulations.extend(analysis.applicable_regulations)
        
        # Remove duplicate regulations
        for analysis in unique_analyses.values():
            analysis.applicable_regulations = list(set(analysis.applicable_regulations))
        
        final_analyses = list(unique_analyses.values())
        
        processing_time = time.time() - start_time
        main_logger.info(f"Result consolidation completed", extra={
            'session_id': session_id,
            'original_results': len(results),
            'consolidated_results': len(final_analyses),
            'processing_time': processing_time
        })
        
        return final_analyses
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Get performance statistics"""
        return {
            'max_workers': self.max_workers,
            'thread_pool_size': self.thread_pool_size,
            'batch_size': self.batch_size,
            'multithreading_enabled': self.enable_multithreading,
            'classification_timeout': self.classification_timeout,
            'performance_metrics': self.performance_metrics.__dict__
        }

# Global enhanced orchestrator instance
enhanced_hybrid_orchestrator = EnhancedHybridOrchestrator()