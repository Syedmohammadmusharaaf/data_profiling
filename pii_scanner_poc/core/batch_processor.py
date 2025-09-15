"""
Batch processing engine for PII Scanner
Handles intelligent batching, retries, and fallback strategies
"""

import time
import uuid
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from pii_scanner_poc.models.data_models import (
    BatchAnalysisRequest, BatchAnalysisResponse, TableAnalysisResult,
    ColumnMetadata, PIIAnalysisResult, RiskLevel, PIIType, Regulation,
    AnalysisSession, convert_strings_to_regulations, convert_string_to_risk_level,
    convert_string_to_pii_type
)
from pii_scanner_poc.services.ai_service import ai_service, json_extractor
from pii_scanner_poc.config.config_manager import config_manager
from pii_scanner_poc.utils.logging_config import batch_logger, log_function_entry, log_function_exit, log_performance


class BatchProcessor:
    """Intelligent batch processing with retry logic and fallback strategies"""
    
    def __init__(self):
        self.batch_config = config_manager.get_config().batch_config
        self.current_session: Optional[AnalysisSession] = None
    
    def start_analysis_session(self, total_tables: int, total_columns: int, 
                              regulations: List[Regulation]) -> str:
        """Start a new analysis session"""
        session_id = str(uuid.uuid4())
        
        self.current_session = AnalysisSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            total_tables=total_tables,
            total_columns=total_columns,
            regulations=regulations,
            results=[]
        )
        
        batch_logger.info("Analysis session started", extra={
            'component': 'batch_processor',
            'session_id': session_id,
            'total_tables': total_tables,
            'total_columns': total_columns,
            'regulations': [reg.value for reg in regulations]
        })
        
        return session_id
    
    def end_analysis_session(self) -> Optional[AnalysisSession]:
        """End the current analysis session"""
        if not self.current_session:
            return None
        
        self.current_session.end_time = datetime.now()
        
        # Calculate processing summary
        total_sensitive = sum(result.sensitive_columns for result in self.current_session.results)
        processing_time = self.current_session.total_processing_time or 0
        
        self.current_session.processing_summary = {
            'total_processing_time': processing_time,
            'total_sensitive_columns': total_sensitive,
            'average_processing_time_per_table': processing_time / len(self.current_session.results) if self.current_session.results else 0,
            'tables_processed': len(self.current_session.results),
            'success_rate': len([r for r in self.current_session.results if r.processing_method != 'fallback']) / len(self.current_session.results) if self.current_session.results else 0
        }
        
        batch_logger.info("Analysis session completed", extra={
            'component': 'batch_processor',
            'session_id': self.current_session.session_id,
            'processing_time': processing_time,
            'total_sensitive_columns': total_sensitive,
            'tables_processed': len(self.current_session.results)
        })
        
        session = self.current_session
        self.current_session = None
        return session
    
    def process_tables(self, tables_data: Dict[str, List[ColumnMetadata]], 
                      regulations: List[Regulation]) -> List[TableAnalysisResult]:
        """Process multiple tables with intelligent batching"""
        log_function_entry(batch_logger, "process_tables", 
                          tables=len(tables_data), 
                          total_columns=sum(len(cols) for cols in tables_data.values()))
        
        start_time = time.time()
        results = []
        
        try:
            # Determine optimal batch configuration
            batches = self._create_optimal_batches(tables_data, regulations)
            
            batch_logger.info("Processing tables in batches", extra={
                'component': 'batch_processor',
                'total_tables': len(tables_data),
                'total_batches': len(batches),
                'batch_configuration': [
                    {
                        'batch_number': i + 1,
                        'tables': len(batch.tables),
                        'columns': batch.total_columns
                    } for i, batch in enumerate(batches)
                ]
            })
            
            # Process each batch
            for batch_request in batches:
                batch_response = self._process_single_batch(batch_request)
                
                if batch_response.success:
                    results.extend(batch_response.results)
                    batch_logger.log_batch_processing(
                        batch_num=batch_request.batch_number,
                        table_count=len(batch_request.tables),
                        column_count=batch_request.total_columns,
                        status='success',
                        details={'processing_time': batch_response.processing_time}
                    )
                else:
                    # Handle failed batch with individual processing
                    fallback_results = self._process_batch_individually(batch_request)
                    results.extend(fallback_results)
                    
                    batch_logger.log_batch_processing(
                        batch_num=batch_request.batch_number,
                        table_count=len(batch_request.tables),
                        column_count=batch_request.total_columns,
                        status='fallback',
                        details={
                            'error': batch_response.error_message,
                            'retry_count': batch_response.retry_count
                        }
                    )
            
            processing_time = time.time() - start_time
            
            log_performance(batch_logger, "process_tables", processing_time,
                          tables_processed=len(results),
                          total_sensitive_columns=sum(r.sensitive_columns for r in results))
            
            log_function_exit(batch_logger, "process_tables", 
                            f"Processed {len(results)} tables in {processing_time:.2f}s")
            
            return results
            
        except Exception as e:
            batch_logger.error("Failed to process tables", extra={
                'component': 'batch_processor',
                'error': str(e),
                'tables_count': len(tables_data)
            })
            
            # Create fallback results for all tables
            fallback_results = []
            for table_name, columns in tables_data.items():
                fallback_result = self._create_fallback_table_result(table_name, columns, regulations)
                fallback_results.append(fallback_result)
            
            return fallback_results
    
    def _create_optimal_batches(self, tables_data: Dict[str, List[ColumnMetadata]], 
                               regulations: List[Regulation]) -> List[BatchAnalysisRequest]:
        """Create optimal batch configuration based on column count and complexity"""
        total_columns = sum(len(columns) for columns in tables_data.values())
        total_tables = len(tables_data)
        
        # Apply hard limits first
        max_columns = self.batch_config.max_columns_per_batch
        max_tables = self.batch_config.max_tables_per_batch
        
        batch_logger.info("Creating batches with limits", extra={
            'component': 'batch_processor',
            'total_tables': total_tables,
            'total_columns': total_columns,
            'max_columns_per_batch': max_columns,
            'max_tables_per_batch': max_tables
        })
        
        # Split tables into batches based on hard limits
        table_items = list(tables_data.items())
        batches = []
        current_batch = {}
        current_columns = 0
        
        for table_name, columns in table_items:
            table_column_count = len(columns)
            
            # Check if adding this table would exceed limits
            if (len(current_batch) >= max_tables or 
                current_columns + table_column_count > max_columns):
                
                # Create batch from current tables
                if current_batch:
                    batch_number = len(batches) + 1
                    batch_request = BatchAnalysisRequest(
                        tables=current_batch,
                        regulations=regulations,
                        batch_number=batch_number,
                        total_batches=0  # Will be updated later
                    )
                    batches.append(batch_request)
                
                # Start new batch
                current_batch = {table_name: columns}
                current_columns = table_column_count
            else:
                # Add to current batch
                current_batch[table_name] = columns
                current_columns += table_column_count
        
        # Add the last batch if it has content
        if current_batch:
            batch_number = len(batches) + 1
            batch_request = BatchAnalysisRequest(
                tables=current_batch,
                regulations=regulations,
                batch_number=batch_number,
                total_batches=0  # Will be updated later
            )
            batches.append(batch_request)
        
        # Update total_batches for all batches
        total_batches = len(batches)
        for batch in batches:
            batch.total_batches = total_batches
        
        batch_logger.info("Batch creation completed", extra={
            'component': 'batch_processor',
            'total_batches': total_batches,
            'batch_details': [
                {
                    'batch_number': batch.batch_number,
                    'tables': len(batch.tables),
                    'columns': batch.total_columns
                } for batch in batches
            ]
        })
        
        return batches
    
    def _process_single_batch(self, request: BatchAnalysisRequest) -> BatchAnalysisResponse:
        """Process a single batch with retry logic"""
        start_time = time.time()
        
        for retry in range(self.batch_config.max_retries + 1):
            try:
                batch_logger.info(f"Processing batch {request.batch_number} (attempt {retry + 1})", extra={
                    'component': 'batch_processor',
                    'batch_number': request.batch_number,
                    'retry_count': retry,
                    'tables': len(request.tables),
                    'columns': request.total_columns
                })
                
                # Generate analysis prompt
                prompt = ai_service.generate_batch_analysis_prompt(request)
                
                # Send to AI service with timeout
                timeout = self.batch_config.timeout_seconds
                ai_response = ai_service.send_analysis_request(prompt, request.batch_number, timeout)
                
                if not ai_response.success:
                    if retry < self.batch_config.max_retries:
                        batch_logger.warning(f"AI request failed for batch {request.batch_number}, retrying", extra={
                            'component': 'batch_processor',
                            'batch_number': request.batch_number,
                            'retry_count': retry,
                            'error': ai_response.error_message
                        })
                        time.sleep(self.batch_config.retry_delay)
                        continue
                    else:
                        processing_time = time.time() - start_time
                        return BatchAnalysisResponse(
                            request=request,
                            results=[],
                            success=False,
                            processing_time=processing_time,
                            error_message=ai_response.error_message,
                            retry_count=retry
                        )
                
                # Extract JSON from response
                json_data = json_extractor.extract_json_from_response(ai_response)
                
                if json_data is None:
                    if retry < self.batch_config.max_retries:
                        batch_logger.warning(f"JSON extraction failed for batch {request.batch_number}, retrying", extra={
                            'component': 'batch_processor',
                            'batch_number': request.batch_number,
                            'retry_count': retry,
                            'response_length': len(ai_response.content)
                        })
                        time.sleep(self.batch_config.retry_delay)
                        continue
                    else:
                        processing_time = time.time() - start_time
                        return BatchAnalysisResponse(
                            request=request,
                            results=[],
                            success=False,
                            processing_time=processing_time,
                            error_message="Failed to extract valid JSON from AI response",
                            retry_count=retry
                        )
                
                # Parse results
                results = self._parse_batch_results(json_data, request)
                
                processing_time = time.time() - start_time
                
                return BatchAnalysisResponse(
                    request=request,
                    results=results,
                    success=True,
                    processing_time=processing_time,
                    retry_count=retry
                )
                
            except Exception as e:
                if retry < self.batch_config.max_retries:
                    batch_logger.warning(f"Exception processing batch {request.batch_number}, retrying", extra={
                        'component': 'batch_processor',
                        'batch_number': request.batch_number,
                        'retry_count': retry,
                        'error': str(e)
                    })
                    time.sleep(self.batch_config.retry_delay)
                    continue
                else:
                    processing_time = time.time() - start_time
                    return BatchAnalysisResponse(
                        request=request,
                        results=[],
                        success=False,
                        processing_time=processing_time,
                        error_message=str(e),
                        retry_count=retry
                    )
        
        # This should not be reached
        processing_time = time.time() - start_time
        return BatchAnalysisResponse(
            request=request,
            results=[],
            success=False,
            processing_time=processing_time,
            error_message="Maximum retries exceeded",
            retry_count=self.batch_config.max_retries
        )
    
    def _parse_batch_results(self, json_data: Dict[str, Any], 
                            request: BatchAnalysisRequest) -> List[TableAnalysisResult]:
        """Parse JSON results into TableAnalysisResult objects"""
        results = []
        
        if 'table_results' not in json_data:
            batch_logger.warning("No table_results found in JSON response", extra={
                'component': 'batch_processor',
                'batch_number': request.batch_number,
                'json_keys': list(json_data.keys())
            })
            return results
        
        for table_data in json_data['table_results']:
            try:
                table_result = self._parse_single_table_result(table_data, request)
                results.append(table_result)
                
                # Add to current session if active
                if self.current_session:
                    self.current_session.results.append(table_result)
                    
            except Exception as e:
                batch_logger.warning(f"Failed to parse table result", extra={
                    'component': 'batch_processor',
                    'batch_number': request.batch_number,
                    'table_name': table_data.get('table_name', 'unknown'),
                    'error': str(e)
                })
                
                # Create fallback result for this table
                table_name = table_data.get('table_name', 'unknown')
                if table_name in request.tables:
                    fallback_result = self._create_fallback_table_result(
                        table_name, request.tables[table_name], request.regulations
                    )
                    results.append(fallback_result)
        
        return results
    
    def _parse_single_table_result(self, table_data: Dict[str, Any], 
                                  request: BatchAnalysisRequest) -> TableAnalysisResult:
        """Parse a single table result from JSON data"""
        table_name = table_data['table_name']
        
        # Parse column analysis
        column_results = []
        for col_data in table_data.get('column_analysis', []):
            column_result = PIIAnalysisResult(
                column_name=col_data['column_name'],
                data_type=col_data['data_type'],
                is_sensitive=col_data['is_sensitive'],
                sensitivity_level=convert_string_to_risk_level(col_data.get('sensitivity_level', 'None')),
                pii_type=convert_string_to_pii_type(col_data.get('pii_type', 'None')),
                applicable_regulations=convert_strings_to_regulations(col_data.get('applicable_regulations', [])),
                confidence_score=col_data.get('confidence_score', 0.8),  # Default confidence
                risk_explanation=col_data.get('risk_explanation', ''),
                recommendations=col_data.get('recommendations', [])
            )
            column_results.append(column_result)
        
        return TableAnalysisResult(
            table_name=table_name,
            risk_level=convert_string_to_risk_level(table_data.get('risk_level', 'Unknown')),
            total_columns=table_data.get('total_columns', len(column_results)),
            sensitive_columns=table_data.get('sensitive_columns', sum(1 for c in column_results if c.is_sensitive)),
            applicable_regulations=convert_strings_to_regulations(table_data.get('applicable_regulations', [])),
            column_analysis=column_results,
            processing_method="batch_analysis",
            analysis_timestamp=datetime.now(),
            batch_info={
                'batch_number': request.batch_number,
                'total_batches': request.total_batches
            }
        )
    
    def _process_batch_individually(self, request: BatchAnalysisRequest) -> List[TableAnalysisResult]:
        """Process each table in the batch individually as fallback"""
        batch_logger.info(f"Processing batch {request.batch_number} individually", extra={
            'component': 'batch_processor',
            'batch_number': request.batch_number,
            'tables': len(request.tables)
        })
        
        results = []
        
        for table_name, columns in request.tables.items():
            individual_request = BatchAnalysisRequest(
                tables={table_name: columns},
                regulations=request.regulations,
                batch_number=request.batch_number,
                total_batches=request.total_batches
            )
            
            individual_response = self._process_single_batch(individual_request)
            
            if individual_response.success and individual_response.results:
                results.extend(individual_response.results)
            else:
                # Create fallback result
                fallback_result = self._create_fallback_table_result(table_name, columns, request.regulations)
                results.append(fallback_result)
        
        return results
    
    def _create_fallback_table_result(self, table_name: str, columns: List[ColumnMetadata], 
                                     regulations: List[Regulation]) -> TableAnalysisResult:
        """Create a fallback result when AI analysis fails"""
        column_results = []
        
        for column in columns:
            # Simple heuristic-based analysis as fallback
            is_sensitive, pii_type, sensitivity_level = self._simple_column_analysis(column)
            
            column_result = PIIAnalysisResult(
                column_name=column.column_name,
                data_type=column.data_type,
                is_sensitive=is_sensitive,
                sensitivity_level=sensitivity_level,
                pii_type=pii_type,
                applicable_regulations=regulations if is_sensitive else [],
                confidence_score=0.5,  # Low confidence for heuristic analysis
                risk_explanation="Analysis based on column name heuristics (AI analysis failed)",
                recommendations=["Manual review recommended"]
            )
            column_results.append(column_result)
        
        sensitive_count = sum(1 for c in column_results if c.is_sensitive)
        
        return TableAnalysisResult(
            table_name=table_name,
            risk_level=RiskLevel.HIGH if sensitive_count > 0 else RiskLevel.UNKNOWN,
            total_columns=len(column_results),
            sensitive_columns=sensitive_count,
            applicable_regulations=regulations if sensitive_count > 0 else [],
            column_analysis=column_results,
            processing_method="fallback_heuristic",
            analysis_timestamp=datetime.now()
        )
    
    def _simple_column_analysis(self, column: ColumnMetadata) -> Tuple[bool, PIIType, RiskLevel]:
        """Simple heuristic-based column analysis for fallback"""
        column_name_lower = column.column_name.lower()
        
        # Common sensitive column patterns
        sensitive_patterns = {
            'name': (PIIType.NAME, RiskLevel.HIGH),
            'email': (PIIType.EMAIL, RiskLevel.HIGH),
            'phone': (PIIType.PHONE, RiskLevel.HIGH),
            'address': (PIIType.ADDRESS, RiskLevel.HIGH),
            'ssn': (PIIType.ID, RiskLevel.HIGH),
            'social': (PIIType.ID, RiskLevel.HIGH),
            'credit_card': (PIIType.FINANCIAL, RiskLevel.HIGH),
            'medical': (PIIType.MEDICAL, RiskLevel.HIGH),
            'patient': (PIIType.MEDICAL, RiskLevel.HIGH),
            'diagnosis': (PIIType.MEDICAL, RiskLevel.HIGH),
            'ip_address': (PIIType.NETWORK, RiskLevel.MEDIUM),
            'user_id': (PIIType.ID, RiskLevel.MEDIUM),
            'birth': (PIIType.OTHER, RiskLevel.HIGH),
        }
        
        for pattern, (pii_type, risk_level) in sensitive_patterns.items():
            if pattern in column_name_lower:
                return True, pii_type, risk_level
        
        return False, PIIType.NONE, RiskLevel.NONE


# Global batch processor instance
batch_processor = BatchProcessor()