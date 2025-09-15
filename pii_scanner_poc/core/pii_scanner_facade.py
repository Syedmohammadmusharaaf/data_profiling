"""
PII Scanner Facade - Enhanced with Hybrid Classification System
Provides a clean interface for all PII scanning operations with advanced hybrid intelligence
"""

import uuid
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from pii_scanner_poc.models.data_models import (
    AnalysisSession, TableAnalysisResult, ColumnMetadata, Regulation,
    convert_strings_to_regulations
)
from pii_scanner_poc.models.enhanced_data_models import HybridClassificationSession, EnhancedFieldAnalysis
from pii_scanner_poc.core.batch_processor import batch_processor
from pii_scanner_poc.core.hybrid_classification_orchestrator import HybridClassificationOrchestrator
from pii_scanner_poc.core.exceptions import (
    PIIScannerBaseException, handle_exception, reraise_with_context,
    ConfigurationError, InputValidationError, InvalidFileFormatError
)
from pii_scanner_poc.services.database_service import database_service
from pii_scanner_poc.services.report_service import report_service
from pii_scanner_poc.config.config_manager import config_manager
from pii_scanner_poc.utils.logging_config import main_logger, log_function_entry, log_function_exit, log_performance
from pii_scanner_poc.utils.error_handler import handle_errors, ErrorContext, error_context


class PIIScannerFacade:
    """
    Enhanced facade for PII Scanner operations with hybrid classification
    Provides high-level interface for scanning database schemas using advanced AI and local intelligence
    """
    
    def __init__(self):
        self.config = config_manager.get_config()
        self.current_session: Optional[AnalysisSession] = None
        self.use_hybrid_classification = False  # Use traditional processing instead 
        self.hybrid_orchestrator = None  # Skip orchestrator to avoid hanging
    
    @handle_errors(component="pii_scanner_facade", operation="analyze_schema_file")
    async def analyze_schema_file(self, schema_file_path: str, 
                           regulations: List[str],
                           selected_tables: Optional[List[str]] = None,
                           output_format: str = "json",
                           region: str = None,
                           company_id: str = None,
                           enable_caching: bool = True,
                           enable_llm: bool = None) -> Dict[str, Any]:  # Changed default to None
        """
        Analyze a schema file for PII/PHI data using hybrid classification
        
        Args:
            schema_file_path: Path to the schema file (DDL, JSON, etc.)
            regulations: List of regulation names to check against
            selected_tables: Optional list of specific tables to analyze
            output_format: Output format ('json', 'html', 'csv')
            region: Optional region for region-specific rules
            company_id: Optional company ID for company-specific aliases
            enable_caching: Whether to use intelligent caching
            enable_llm: Whether to use LLM for edge cases (auto-detected if None)
            
        Returns:
            Enhanced analysis results dictionary with comprehensive insights
            
        Raises:
            InputValidationError: For invalid input parameters
            InvalidFileFormatError: For unsupported or corrupted files
            ConfigurationError: For missing or invalid configuration
        """
        
        # Auto-detect LLM availability if not explicitly specified
        if enable_llm is None:
            enable_llm = self._detect_valid_ai_config()
            main_logger.info(f"Auto-detected LLM availability: {enable_llm}")
            
        main_logger.info(f"Starting analyze_schema_file with LLM {'enabled' if enable_llm else 'disabled'}")
        
        log_function_entry(main_logger, "analyze_schema_file", 
                          schema_file=schema_file_path,
                          regulations=regulations,
                          selected_tables=selected_tables,
                          use_hybrid=self.use_hybrid_classification)
        
        start_time = datetime.now()
        session_id = None
        
        # Input validation
        if not schema_file_path or not isinstance(schema_file_path, str):
            raise InputValidationError(
                "Schema file path is required and must be a string",
                field_name="schema_file_path"
            ).add_context('provided_value', schema_file_path)
        
        if not regulations or not isinstance(regulations, list):
            raise InputValidationError(
                "Regulations list is required and must be a non-empty list",
                field_name="regulations"
            ).add_context('provided_value', regulations)
        
        # Validate file exists and is readable
        import os
        if not os.path.exists(schema_file_path):
            raise InvalidFileFormatError(
                file_path=schema_file_path,
                expected_formats=["ddl", "sql", "json", "csv"]
            ).add_context('file_not_found', True)
        
        if not os.access(schema_file_path, os.R_OK):
            raise InvalidFileFormatError(
                file_path=schema_file_path,
                expected_formats=["ddl", "sql", "json", "csv"]
            ).add_context('file_not_readable', True)
        
        try:
            with error_context(
                operation="convert_regulations",
                component="pii_scanner_facade",
                regulations=regulations
            ) as ctx:
                # Convert regulation strings to enum objects
                regulation_enums = convert_strings_to_regulations(regulations)
                ctx.add_metadata('converted_regulations', [r.name for r in regulation_enums])
            
            with error_context(
                operation="load_schema_data", 
                component="pii_scanner_facade",
                file_path=schema_file_path
            ) as ctx:
                # Load schema data from file
                main_logger.info("Loading schema data from file", extra={
                    'component': 'pii_scanner_facade',
                    'schema_file': schema_file_path,
                    'regulations': regulations,
                'hybrid_mode': self.use_hybrid_classification
            })
            
                schema_data = database_service.load_schema_from_file(schema_file_path)
                ctx.add_metadata('loaded_tables', len(schema_data) if schema_data else 0)
            
            if not schema_data:
                raise InvalidFileFormatError(
                    file_path=schema_file_path,
                    expected_formats=["ddl", "sql", "json", "csv"]
                ).add_context('file_content_empty', True)
            
            # Filter tables if specific tables are requested
            if selected_tables:
                with error_context(
                    operation="filter_tables",
                    component="pii_scanner_facade",
                    selected_tables=selected_tables
                ) as ctx:
                    filtered_data = {
                        table_name: columns 
                        for table_name, columns in schema_data.items() 
                        if table_name in selected_tables
                    }
                    schema_data = filtered_data
                    ctx.add_metadata('filtered_table_count', len(schema_data))
            
            if not schema_data:
                raise InputValidationError(
                    "No tables selected for analysis",
                    field_name="selected_tables"
                ).add_context('available_tables', list(schema_data.keys()))
            
            # Calculate totals
            total_tables = len(schema_data)
            total_columns = sum(len(columns) for columns in schema_data.values())
            
            main_logger.info("Schema data loaded successfully", extra={
                'component': 'pii_scanner_facade',
                'total_tables': total_tables,
                'total_columns': total_columns,
                'table_names': list(schema_data.keys())
            })
            
            # Use hybrid classification system or fallback to original batch processing
            if self.use_hybrid_classification:
                with error_context(
                    operation="hybrid_classification",
                    component="pii_scanner_facade",
                    table_count=total_tables,
                    column_count=total_columns
                ) as ctx:
                    # Use comprehensive hybrid classification orchestrator
                    hybrid_session = self.hybrid_orchestrator.classify_schema(
                        tables_data=schema_data,
                        regulations=regulation_enums,
                        region=region,
                        company_id=company_id,
                        enable_caching=enable_caching,
                        enable_llm=enable_llm
                    )
                    
                    # Extract field analyses from session
                    field_analyses = hybrid_session.field_analyses
                    
                    # Create results from field analyses
                    results = []
                    for analysis in field_analyses:
                        results.append(analysis)
                    
                    session_id = hybrid_session.session_id
                    ctx.add_metadata('session_id', session_id)
                
                with error_context(
                    operation="convert_hybrid_results",
                    component="pii_scanner_facade",
                    session_id=session_id
                ) as ctx:
                    # Convert hybrid results to traditional format for compatibility
                    results = self._convert_hybrid_to_traditional_results(
                        field_analyses, schema_data
                    )
                    ctx.add_metadata('results_count', len(results))
                
                with error_context(
                    operation="generate_hybrid_report",
                    component="pii_scanner_facade",
                    session_id=session_id
                ) as ctx:
                    # Generate enhanced report using the actual hybrid session
                    report_data = self._generate_hybrid_report(
                        hybrid_session, regulation_enums, results
                    )
                    ctx.add_metadata('report_generated', True)
                
            else:
                with error_context(
                    operation="traditional_batch_processing",
                    component="pii_scanner_facade",
                    table_count=total_tables
                ) as ctx:
                    # Fallback to original batch processing
                    session_id = batch_processor.start_analysis_session(
                        total_tables, total_columns, regulation_enums
                    )
                    
                    results = batch_processor.process_tables(schema_data, regulation_enums)
                    session = batch_processor.end_analysis_session()
                    ctx.add_metadata('session_id', session_id)
                
                with error_context(
                    operation="generate_traditional_report",
                    component="pii_scanner_facade",
                    session_id=session_id
                ) as ctx:
                    # Generate traditional report
                    report_data = report_service.generate_comprehensive_report(
                        results, regulation_enums, session
                    )
                    ctx.add_metadata('report_generated', True)
            
            # Save report to file
            if output_format.lower() in ['json', 'html', 'csv']:
                with error_context(
                    operation="save_report",
                    component="pii_scanner_facade",
                    output_format=output_format,
                    session_id=session_id
                ) as ctx:
                    report_file = report_service.save_report_to_file(
                        report_data, output_format.lower(), session_id
                    )
                    report_data['report_file_path'] = report_file
                    ctx.add_metadata('report_file', report_file)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            log_performance(main_logger, "analyze_schema_file", processing_time,
                          tables_analyzed=len(results),
                          total_sensitive_columns=sum(r.sensitive_columns for r in results),
                          session_id=session_id,
                          hybrid_mode=self.use_hybrid_classification)
            
            main_logger.info("Schema analysis completed successfully", extra={
                'component': 'pii_scanner_facade',
                'session_id': session_id,
                'processing_time': processing_time,
                'hybrid_mode': self.use_hybrid_classification,
                'results_summary': {
                    'total_tables': len(results),
                    'total_sensitive_columns': sum(r.sensitive_columns for r in results),
                    'high_risk_tables': len([r for r in results if r.risk_level.value == 'High'])
                }
            })
            
            log_function_exit(main_logger, "analyze_schema_file", 
                            f"Analysis completed: {len(results)} tables in {processing_time:.2f}s")
            
            return report_data
            
        except PIIScannerBaseException:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Convert generic exceptions to our custom types
            processing_time = (datetime.now() - start_time).total_seconds()
            context = {
                'session_id': session_id,
                'schema_file': schema_file_path,
                'processing_time': processing_time,
                'hybrid_mode': self.use_hybrid_classification
            }
            
            main_logger.error("Schema analysis failed", extra={
                'component': 'pii_scanner_facade',
                **context,
                'error': str(e)
            }, exc_info=True)
            
            reraise_with_context(e, context, "Schema analysis failed")
    
    def _convert_hybrid_to_traditional_results(self, field_analyses: List[EnhancedFieldAnalysis],
                                             schema_data: Dict[str, List[ColumnMetadata]]) -> List[TableAnalysisResult]:
        """
        Convert hybrid field analyses to traditional table analysis results for compatibility.
        
        This method bridges the new hybrid classification system with the existing
        reporting infrastructure by converting EnhancedFieldAnalysis objects to
        the traditional TableAnalysisResult format.
        
        Args:
            field_analyses (List[EnhancedFieldAnalysis]): Hybrid analysis results from the
                enhanced classification system containing detailed PII/PHI assessments
            schema_data (Dict[str, List[ColumnMetadata]]): Original schema structure
                mapping table names to their column metadata
        
        Returns:
            List[TableAnalysisResult]: Traditional format results compatible with
                existing report generation and MCP integration systems
        
        Processing Steps:
            1. Group field analyses by table name for table-level aggregation
            2. Convert each EnhancedFieldAnalysis to PIIAnalysisResult format
            3. Calculate table-level risk metrics (total/sensitive column counts)
            4. Determine overall table risk level (NONE/LOW/MEDIUM/HIGH)
            5. Aggregate applicable regulations across all sensitive columns
            6. Create TableAnalysisResult with comprehensive metadata
        
        Risk Level Calculation:
            - NONE: No sensitive columns detected
            - LOW/MEDIUM/HIGH: Highest risk level among sensitive columns
        
        Note:
            This conversion maintains backward compatibility while leveraging
            the enhanced analysis capabilities of the hybrid system.
        """
        
        # Group field analyses by table for table-level aggregation
        table_analyses = {}
        
        for analysis in field_analyses:
            table_name = analysis.table_name
            
            # Initialize table analysis collection
            if table_name not in table_analyses:
                table_analyses[table_name] = []
            
            # Convert enhanced analysis to traditional PIIAnalysisResult format
            # This conversion preserves all critical information while ensuring
            # compatibility with existing report generation systems
            from pii_scanner_poc.models.data_models import PIIAnalysisResult
            traditional_analysis = PIIAnalysisResult(
                column_name=analysis.field_name,
                data_type=analysis.data_type,
                is_sensitive=analysis.is_sensitive,
                sensitivity_level=analysis.risk_level,
                pii_type=analysis.pii_type,
                applicable_regulations=analysis.applicable_regulations,
                confidence_score=analysis.confidence_score,
                risk_explanation=analysis.rationale,
                recommendations=[analysis.justification] if analysis.justification else []
            )
            
            table_analyses[table_name].append(traditional_analysis)
        
        # Create TableAnalysisResult objects
        results = []
        
        for table_name, column_analyses in table_analyses.items():
            # Calculate table-level metrics
            total_columns = len(column_analyses)
            sensitive_columns = sum(1 for analysis in column_analyses if analysis.is_sensitive)
            
            # Determine overall table risk level
            if sensitive_columns == 0:
                from pii_scanner_poc.models.data_models import RiskLevel
                table_risk_level = RiskLevel.NONE
            else:
                # Use highest risk level from sensitive columns
                sensitive_analyses = [a for a in column_analyses if a.is_sensitive]
                risk_levels = [a.sensitivity_level for a in sensitive_analyses]
                table_risk_level = max(risk_levels, key=lambda x: x.value)
            
            # Get applicable regulations
            all_regulations = set()
            for analysis in column_analyses:
                if analysis.is_sensitive:
                    all_regulations.update(analysis.applicable_regulations)
            
            # Create table result
            table_result = TableAnalysisResult(
                table_name=table_name,
                risk_level=table_risk_level,
                total_columns=total_columns,
                sensitive_columns=sensitive_columns,
                applicable_regulations=list(all_regulations),
                column_analysis=column_analyses,
                processing_method="hybrid_classification",
                analysis_timestamp=datetime.now()
            )
            
            results.append(table_result)
        
        return results
    
    def _generate_hybrid_report(self, hybrid_session: HybridClassificationSession,
                              regulations: List[Regulation],
                              traditional_results: List[TableAnalysisResult]) -> Dict[str, Any]:
        """Generate enhanced report with hybrid classification insights"""
        
        # Start with traditional report structure
        base_report = report_service.generate_comprehensive_report(
            traditional_results, regulations, None
        )
        
        # Add hybrid-specific insights
        hybrid_insights = {
            'hybrid_classification_metrics': {
                'session_id': hybrid_session.session_id,
                'total_processing_time': hybrid_session.total_processing_time,
                'local_detection_rate': hybrid_session.local_classifications / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0,
                'llm_usage_rate': hybrid_session.llm_classifications / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0,
                'cache_hit_rate': hybrid_session.cache_hits / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0,
                'high_confidence_results': hybrid_session.high_confidence_results,
                'low_confidence_results': hybrid_session.low_confidence_results,
                'validation_errors': hybrid_session.validation_errors
            },
            'performance_analysis': {
                'target_achievement': {
                    'local_coverage_target': 0.95,
                    'local_coverage_actual': hybrid_session.local_classifications / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0,
                    'local_coverage_met': (hybrid_session.local_classifications / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0) >= 0.95,
                    'llm_usage_target': 0.05,
                    'llm_usage_actual': hybrid_session.llm_classifications / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0,
                    'llm_usage_met': (hybrid_session.llm_classifications / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0) <= 0.05
                },
                'workflow_performance': {
                    'total_steps': len(hybrid_session.workflow_steps),
                    'successful_steps': sum(1 for step in hybrid_session.workflow_steps if step.success),
                    'failed_steps': sum(1 for step in hybrid_session.workflow_steps if not step.success),
                    'step_details': [
                        {
                            'step_name': step.step_name,
                            'step_type': step.step_type,
                            'duration': step.duration,
                            'success': step.success
                        } for step in hybrid_session.workflow_steps
                    ]
                }
            },
            'detection_method_breakdown': self._calculate_detection_method_breakdown(hybrid_session.field_analyses),
            'confidence_distribution': self._calculate_confidence_distribution(hybrid_session.field_analyses),
            'processing_recommendations': self._generate_processing_recommendations(hybrid_session)
        }
        
        # Merge hybrid insights into base report
        base_report.update(hybrid_insights)
        
        # Add session summary if available
        if hybrid_session.summary_report:
            base_report['session_summary'] = hybrid_session.summary_report
        
        return base_report
    
    def _calculate_detection_method_breakdown(self, field_analyses: List[EnhancedFieldAnalysis]) -> Dict[str, int]:
        """Calculate breakdown of detection methods used"""
        method_counts = {}
        
        for analysis in field_analyses:
            # Handle both enum and string detection methods
            if hasattr(analysis.detection_method, 'value'):
                method = analysis.detection_method.value
            else:
                method = str(analysis.detection_method)
            method_counts[method] = method_counts.get(method, 0) + 1
        
        return method_counts
    
    def _calculate_confidence_distribution(self, field_analyses: List[EnhancedFieldAnalysis]) -> Dict[str, int]:
        """Calculate distribution of confidence levels"""
        confidence_counts = {}
        
        for analysis in field_analyses:
            confidence_level = analysis.confidence_level.value
            confidence_counts[confidence_level] = confidence_counts.get(confidence_level, 0) + 1
        
        return confidence_counts
    
    def _generate_processing_recommendations(self, hybrid_session: HybridClassificationSession) -> List[str]:
        """Generate recommendations based on processing results"""
        recommendations = []
        
        # Check local coverage rate
        local_coverage = hybrid_session.local_classifications / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0
        if local_coverage < 0.95:
            recommendations.append(
                f"Local detection rate ({local_coverage:.1%}) is below target (95%). "
                "Consider expanding pattern library or adding company-specific aliases."
            )
        
        # Check LLM usage rate
        llm_usage = hybrid_session.llm_classifications / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0
        if llm_usage > 0.05:
            recommendations.append(
                f"LLM usage rate ({llm_usage:.1%}) exceeds target (5%). "
                "Consider improving local pattern recognition for better performance."
            )
        
        # Check confidence levels
        if hybrid_session.low_confidence_results > hybrid_session.total_fields * 0.1:
            recommendations.append(
                "High number of low-confidence results detected. "
                "Consider manual review of uncertain classifications."
            )
        
        # Check cache effectiveness
        cache_rate = hybrid_session.cache_hits / hybrid_session.total_fields if hybrid_session.total_fields > 0 else 0
        if cache_rate > 0.5:
            recommendations.append(
                f"High cache hit rate ({cache_rate:.1%}) indicates good pattern reuse. "
                "System is efficiently leveraging previous analyses."
            )
        
        # Check for validation errors
        if hybrid_session.validation_errors > 0:
            recommendations.append(
                f"{hybrid_session.validation_errors} validation errors detected. "
                "Review and correct data quality issues."
            )
        
        return recommendations
    
    def analyze_database_connection(self, connection_config: Dict[str, Any],
                                   regulations: List[str],
                                   schema_name: Optional[str] = None,
                                   selected_tables: Optional[List[str]] = None,
                                   region: str = None,
                                   company_id: str = None,
                                   enable_caching: bool = True,
                                   enable_llm: bool = True) -> Dict[str, Any]:
        """
        Analyze a live database connection for PII/PHI data using hybrid classification
        
        Args:
            connection_config: Database connection configuration
            regulations: List of regulation names to check against
            schema_name: Optional specific schema to analyze
            selected_tables: Optional list of specific tables to analyze
            region: Optional region for region-specific rules
            company_id: Optional company ID for company-specific aliases
            enable_caching: Whether to use intelligent caching
            enable_llm: Whether to use LLM for edge cases
            
        Returns:
            Enhanced analysis results dictionary
        """
        log_function_entry(main_logger, "analyze_database_connection",
                          regulations=regulations,
                          schema_name=schema_name,
                          selected_tables=selected_tables,
                          use_hybrid=self.use_hybrid_classification)
        
        start_time = datetime.now()
        session_id = None
        
        try:
            # Convert regulation strings to enum objects
            regulation_enums = convert_strings_to_regulations(regulations)
            
            # Connect to database and load schema
            main_logger.info("Connecting to database", extra={
                'component': 'pii_scanner_facade',
                'schema_name': schema_name,
                'regulations': regulations,
                'hybrid_mode': self.use_hybrid_classification
            })
            
            schema_data = database_service.load_schema_from_database(
                connection_config, schema_name, selected_tables
            )
            
            if not schema_data:
                raise ValueError("No schema data found in database")
            
            # Calculate totals
            total_tables = len(schema_data)
            total_columns = sum(len(columns) for columns in schema_data.values())
            
            main_logger.info("Database schema loaded successfully", extra={
                'component': 'pii_scanner_facade',
                'total_tables': total_tables,
                'total_columns': total_columns,
                'table_names': list(schema_data.keys())
            })
            
            # Use hybrid classification system
            if self.use_hybrid_classification:
                hybrid_session = self.hybrid_orchestrator.classify_schema(
                    schema_data,
                    regulation_enums,
                    region=region,
                    company_id=company_id,
                    enable_caching=enable_caching,
                    enable_llm=enable_llm
                )
                
                session_id = hybrid_session.session_id
                
                # Convert results and generate report
                results = self._convert_hybrid_to_traditional_results(
                    hybrid_session.field_analyses, schema_data
                )
                
                report_data = self._generate_hybrid_report(
                    hybrid_session, regulation_enums, results
                )
            else:
                # Fallback to original processing
                session_id = batch_processor.start_analysis_session(
                    total_tables, total_columns, regulation_enums
                )
                
                results = batch_processor.process_tables(schema_data, regulation_enums)
                session = batch_processor.end_analysis_session()
                
                report_data = report_service.generate_comprehensive_report(
                    results, regulation_enums, session
                )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            log_performance(main_logger, "analyze_database_connection", processing_time,
                          tables_analyzed=len(results),
                          total_sensitive_columns=sum(r.sensitive_columns for r in results),
                          session_id=session_id,
                          hybrid_mode=self.use_hybrid_classification)
            
            main_logger.info("Database analysis completed successfully", extra={
                'component': 'pii_scanner_facade',
                'session_id': session_id,
                'processing_time': processing_time,
                'hybrid_mode': self.use_hybrid_classification
            })
            
            log_function_exit(main_logger, "analyze_database_connection",
                            f"Analysis completed: {len(results)} tables in {processing_time:.2f}s")
            
            return report_data
            
        except Exception as e:
            main_logger.error("Database analysis failed", extra={
                'component': 'pii_scanner_facade',
                'session_id': session_id,
                'error': str(e),
                'hybrid_mode': self.use_hybrid_classification
            }, exc_info=True)
            
            # Create error report
            error_report = {
                'success': False,
                'error': str(e),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'analysis_mode': 'hybrid' if self.use_hybrid_classification else 'traditional'
            }
            
            return error_report
    
    def get_analysis_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of an ongoing analysis session"""
        if self.current_session and self.current_session.session_id == session_id:
            return {
                'session_id': session_id,
                'status': 'in_progress',
                'start_time': self.current_session.start_time.isoformat(),
                'tables_processed': len(self.current_session.results),
                'total_tables': self.current_session.total_tables,
                'analysis_mode': 'hybrid' if self.use_hybrid_classification else 'traditional'
            }
        else:
            return {
                'session_id': session_id,
                'status': 'not_found',
                'analysis_mode': 'hybrid' if self.use_hybrid_classification else 'traditional'
            }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration including hybrid system components"""
        log_function_entry(main_logger, "validate_configuration")
        
        try:
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'configuration': {},
                'hybrid_system_status': {}
            }
            
            # Validate AI configuration
            ai_config = self.config.ai_config
            if not ai_config.api_key or ai_config.api_key == 'temp':
                validation_results['errors'].append("Invalid or missing AI API key")
                validation_results['valid'] = False
            
            if not ai_config.endpoint:
                validation_results['errors'].append("Missing AI endpoint configuration")
                validation_results['valid'] = False
            
            # Test AI connection if hybrid system is enabled
            if self.use_hybrid_classification:
                try:
                    # Get hybrid system statistics
                    hybrid_stats = self.hybrid_orchestrator.get_system_statistics()
                    validation_results['hybrid_system_status'] = {
                        'orchestrator_available': True,
                        'local_engine_patterns': hybrid_stats['engine_statistics']['total_patterns'],
                        'cache_available': hybrid_stats['cache_statistics']['total_entries'] >= 0,
                        'enhanced_ai_available': hybrid_stats['ai_statistics']['total_interactions'] >= 0,
                        'performance_metrics': hybrid_stats['performance_metrics']
                    }
                except Exception as e:
                    validation_results['warnings'].append(f"Hybrid system validation failed: {str(e)}")
                    validation_results['hybrid_system_status']['error'] = str(e)
            
            # Test basic AI connection
            try:
                from pii_scanner_poc.services.ai_service import ai_service
                test_response = ai_service.send_analysis_request("Test connection", 0)
                if not test_response.success:
                    validation_results['warnings'].append(f"AI service test failed: {test_response.error_message}")
            except Exception as e:
                validation_results['warnings'].append(f"Could not test AI connection: {str(e)}")
            
            validation_results['configuration'] = {
                'supported_regulations': [reg.value for reg in [Regulation.GDPR, Regulation.HIPAA, Regulation.CCPA]],
                'batch_configuration': {
                    'small_threshold': self.config.batch_config.small_batch_threshold,
                    'medium_threshold': self.config.batch_config.medium_batch_threshold,
                    'large_threshold': self.config.batch_config.large_batch_threshold,
                    'max_retries': self.config.batch_config.max_retries,
                    'timeout_seconds': getattr(self.config.batch_config, 'timeout_seconds', 45)
                },
                'hybrid_classification': {
                    'enabled': self.use_hybrid_classification,
                    'local_coverage_target': 0.95,
                    'llm_usage_target': 0.05
                }
            }
            
            main_logger.info("Configuration validation completed", extra={
                'component': 'pii_scanner_facade',
                'valid': validation_results['valid'],
                'errors': len(validation_results['errors']),
                'warnings': len(validation_results['warnings']),
                'hybrid_enabled': self.use_hybrid_classification
            })
            
            log_function_exit(main_logger, "validate_configuration", 
                            f"Valid: {validation_results['valid']}")
            
            return validation_results
            
        except Exception as e:
            main_logger.error("Configuration validation failed", extra={
                'component': 'pii_scanner_facade',
                'error': str(e)
            })
            
            return {
                'valid': False,
                'errors': [f"Validation failed: {str(e)}"],
                'warnings': [],
                'configuration': {},
                'hybrid_system_status': {}
            }
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics including hybrid components"""
        try:
            if self.use_hybrid_classification:
                return self.hybrid_orchestrator.get_system_statistics()
            else:
                # Return basic statistics for traditional mode
                return {
                    'performance_metrics': {
                        'analysis_mode': 'traditional',
                        'hybrid_available': False
                    },
                    'system_configuration': {
                        'hybrid_classification_enabled': False
                    }
                }
        except Exception as e:
            main_logger.error("Failed to get system statistics", extra={
                'component': 'pii_scanner_facade',
                'error': str(e)
            })
            return {'error': str(e)}
    
    def set_hybrid_mode(self, enabled: bool):
        """Enable or disable hybrid classification mode"""
        self.use_hybrid_classification = enabled
        
        main_logger.info("Hybrid classification mode changed", extra={
            'component': 'pii_scanner_facade',
            'hybrid_enabled': enabled
        })
    
    def _detect_valid_ai_config(self) -> bool:
        """Auto-detect if valid AI configuration is available with enhanced validation"""
        try:
            import os
            api_key = os.environ.get('AZURE_OPENAI_API_KEY', '').strip()
            endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT', '').strip()
            deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT', '').strip()
            
            # Check if we have placeholder or missing values
            placeholder_values = ['temp', 'placeholder', 'your_key_here', 'test', 'demo']
            
            if not api_key or api_key.lower() in placeholder_values or len(api_key) < 10:
                main_logger.info("AI config invalid: API key is placeholder, missing, or too short", extra={
                    'component': 'pii_scanner_facade',
                    'key': f"{api_key[:10]}..." if api_key else "empty",
                    'reason': 'invalid_api_key'
                })
                return False
            
            if not endpoint or endpoint.lower() in placeholder_values or not endpoint.startswith('https://'):
                main_logger.info("AI config invalid: endpoint is placeholder, missing, or invalid", extra={
                    'component': 'pii_scanner_facade',
                    'endpoint': f"{endpoint[:50]}..." if endpoint else "empty",
                    'reason': 'invalid_endpoint'
                })
                return False
            
            if not deployment or deployment.lower() in placeholder_values:
                main_logger.info("AI config invalid: deployment is placeholder or missing", extra={
                    'component': 'pii_scanner_facade',
                    'deployment': deployment,
                    'reason': 'invalid_deployment'
                })
                return False
            
            # Additional validation - check if the key looks like a real Azure OpenAI key
            if not (api_key.startswith('sk-') or len(api_key) >= 32):
                main_logger.info("AI config invalid: API key format appears incorrect", extra={
                    'component': 'pii_scanner_facade',
                    'key_length': len(api_key),
                    'reason': 'invalid_key_format'
                })
                return False
            
            main_logger.info("Valid AI configuration detected - AI will be enabled", extra={
                'component': 'pii_scanner_facade',
                'endpoint_configured': bool(endpoint),
                'key_configured': bool(api_key),
                'deployment_configured': bool(deployment),
                'ai_enabled': True
            })
            return True
            
        except Exception as e:
            main_logger.error(f"Error detecting AI config: {e}", extra={
                'component': 'pii_scanner_facade',
                'error': str(e)
            })
            return False


# Global facade instance
pii_scanner = PIIScannerFacade()