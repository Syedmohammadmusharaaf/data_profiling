"""
Report generation service for PII Scanner
Handles creation of comprehensive analysis reports in various formats
"""

import json
import csv
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from pii_scanner_poc.models.data_models import (
    TableAnalysisResult, AnalysisSession, Regulation, RiskLevel
)
from pii_scanner_poc.utils.logging_config import main_logger, log_function_entry, log_function_exit


class ReportService:
    """Service for generating comprehensive analysis reports"""
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_comprehensive_report(self, results: List[TableAnalysisResult],
                                     regulations: List[Regulation],
                                     session: Optional[AnalysisSession] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis report
        
        Args:
            results: List of table analysis results
            regulations: Regulations that were checked
            session: Optional analysis session information
            
        Returns:
            Comprehensive report dictionary
        """
        log_function_entry(main_logger, "generate_comprehensive_report",
                          results_count=len(results),
                          regulations=[r.value for r in regulations])
        
        try:
            # Calculate summary statistics
            summary_stats = self._calculate_summary_statistics(results, regulations)
            
            # Generate detailed analysis
            detailed_analysis = self._generate_detailed_analysis(results)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(results, regulations)
            
            # Create compliance summary
            compliance_summary = self._generate_compliance_summary(results, regulations)
            
            # Session information
            session_info = session.to_dict() if session else None
            
            report = {
                'report_metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'report_version': '2.0',
                    'scanner_version': '1.0.0',
                    'session_id': session.session_id if session else None
                },
                'analysis_summary': summary_stats,
                'compliance_summary': compliance_summary,
                'detailed_results': detailed_analysis,
                'recommendations': recommendations,
                'session_information': session_info
            }
            
            main_logger.info("Comprehensive report generated", extra={
                'component': 'report_service',
                'tables_analyzed': len(results),
                'total_sensitive_columns': summary_stats['total_sensitive_columns'],
                'high_risk_tables': summary_stats['high_risk_tables']
            })
            
            log_function_exit(main_logger, "generate_comprehensive_report",
                            f"Report generated for {len(results)} tables")
            
            return report
            
        except Exception as e:
            main_logger.error("Failed to generate comprehensive report", extra={
                'component': 'report_service',
                'error': str(e)
            }, exc_info=True)
            raise
    
    def save_report_to_file(self, report_data: Dict[str, Any], 
                           format_type: str, session_id: str) -> str:
        """
        Save report to file in specified format
        
        Args:
            report_data: Report data dictionary
            format_type: Format type ('json', 'html', 'csv')
            session_id: Session ID for filename
            
        Returns:
            Path to saved file
        """
        log_function_entry(main_logger, "save_report_to_file",
                          format_type=format_type,
                          session_id=session_id)
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pii_analysis_report_{session_id}_{timestamp}.{format_type}"
            file_path = self.reports_dir / filename
            
            if format_type == 'json':
                self._save_json_report(report_data, file_path)
            elif format_type == 'html':
                self._save_html_report(report_data, file_path)
            elif format_type == 'csv':
                self._save_csv_report(report_data, file_path)
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
            
            main_logger.info("Report saved to file", extra={
                'component': 'report_service',
                'file_path': str(file_path),
                'format_type': format_type,
                'file_size': file_path.stat().st_size
            })
            
            log_function_exit(main_logger, "save_report_to_file",
                            f"Report saved: {filename}")
            
            return str(file_path)
            
        except Exception as e:
            main_logger.error("Failed to save report to file", extra={
                'component': 'report_service',
                'format_type': format_type,
                'session_id': session_id,
                'error': str(e)
            }, exc_info=True)
            raise
    
    def _calculate_summary_statistics(self, results: List[TableAnalysisResult],
                                     regulations: List[Regulation]) -> Dict[str, Any]:
        """Calculate summary statistics for the analysis"""
        total_tables = len(results)
        total_columns = sum(result.total_columns for result in results)
        total_sensitive_columns = sum(result.sensitive_columns for result in results)
        
        # Risk level distribution
        risk_distribution = {level.value: 0 for level in RiskLevel}
        for result in results:
            risk_distribution[result.risk_level.value] += 1
        
        # Regulation coverage
        regulation_coverage = {}
        for regulation in regulations:
            applicable_tables = len([r for r in results if regulation in r.applicable_regulations])
            regulation_coverage[regulation.value] = applicable_tables
        
        # PII type distribution
        pii_type_counts = {}
        for result in results:
            for column in result.column_analysis:
                if column.is_sensitive:
                    pii_type = column.pii_type.value
                    pii_type_counts[pii_type] = pii_type_counts.get(pii_type, 0) + 1
        
        return {
            'total_tables_analyzed': total_tables,
            'total_columns_analyzed': total_columns,
            'total_sensitive_columns': total_sensitive_columns,
            'sensitivity_ratio': total_sensitive_columns / total_columns if total_columns > 0 else 0,
            'high_risk_tables': risk_distribution.get('High', 0),
            'medium_risk_tables': risk_distribution.get('Medium', 0),
            'low_risk_tables': risk_distribution.get('Low', 0),
            'risk_distribution': risk_distribution,
            'regulation_coverage': regulation_coverage,
            'pii_type_distribution': pii_type_counts,
            'regulations_analyzed': [reg.value for reg in regulations]
        }
    
    def _generate_detailed_analysis(self, results: List[TableAnalysisResult]) -> List[Dict[str, Any]]:
        """Generate detailed analysis for each table"""
        detailed_results = []
        
        for result in results:
            table_detail = {
                'table_name': result.table_name,
                'risk_assessment': {
                    'overall_risk': result.risk_level.value,
                    'sensitivity_ratio': result.sensitivity_ratio,
                    'risk_factors': self._identify_risk_factors(result)
                },
                'column_breakdown': {
                    'total_columns': result.total_columns,
                    'sensitive_columns': result.sensitive_columns,
                    'columns_by_sensitivity': self._group_columns_by_sensitivity(result),
                    'columns_by_pii_type': self._group_columns_by_pii_type(result)
                },
                'regulatory_compliance': {
                    'applicable_regulations': [reg.value for reg in result.applicable_regulations],
                    'compliance_details': self._generate_compliance_details(result)
                },
                'detailed_columns': [col.to_dict() for col in result.column_analysis if col.is_sensitive],
                'processing_metadata': {
                    'processing_method': result.processing_method,
                    'analysis_timestamp': result.analysis_timestamp.isoformat(),
                    'batch_info': result.batch_info
                }
            }
            
            detailed_results.append(table_detail)
        
        return detailed_results
    
    def _generate_recommendations(self, results: List[TableAnalysisResult],
                                 regulations: List[Regulation]) -> Dict[str, Any]:
        """Generate actionable recommendations"""
        recommendations = {
            'immediate_actions': [],
            'medium_term_actions': [],
            'long_term_actions': [],
            'regulatory_compliance': [],
            'technical_improvements': []
        }
        
        # High-risk table recommendations
        high_risk_tables = [r for r in results if r.risk_level == RiskLevel.HIGH]
        if high_risk_tables:
            recommendations['immediate_actions'].append({
                'priority': 'Critical',
                'action': 'Review and secure high-risk tables',
                'details': f'Found {len(high_risk_tables)} high-risk tables containing sensitive data',
                'affected_tables': [t.table_name for t in high_risk_tables]
            })
        
        # Encryption recommendations
        sensitive_columns = sum(result.sensitive_columns for result in results)
        if sensitive_columns > 0:
            recommendations['medium_term_actions'].append({
                'priority': 'High',
                'action': 'Implement column-level encryption',
                'details': f'Consider encrypting {sensitive_columns} sensitive columns',
                'estimated_effort': 'Medium'
            })
        
        # Regulation-specific recommendations
        for regulation in regulations:
            applicable_tables = [r for r in results if regulation in r.applicable_regulations]
            if applicable_tables:
                recommendations['regulatory_compliance'].append({
                    'regulation': regulation.value,
                    'affected_tables': len(applicable_tables),
                    'recommendations': self._get_regulation_specific_recommendations(regulation)
                })
        
        return recommendations
    
    def _generate_compliance_summary(self, results: List[TableAnalysisResult],
                                   regulations: List[Regulation]) -> Dict[str, Any]:
        """Generate compliance summary"""
        compliance_summary = {}
        
        for regulation in regulations:
            applicable_tables = [r for r in results if regulation in r.applicable_regulations]
            sensitive_columns = sum(
                len([c for c in r.column_analysis if c.is_sensitive and regulation in c.applicable_regulations])
                for r in applicable_tables
            )
            
            compliance_summary[regulation.value] = {
                'applicable_tables': len(applicable_tables),
                'sensitive_columns': sensitive_columns,
                'compliance_status': self._assess_compliance_status(applicable_tables, regulation),
                'key_requirements': self._get_regulation_requirements(regulation)
            }
        
        return compliance_summary
    
    def _save_json_report(self, report_data: Dict[str, Any], file_path: Path):
        """Save report in JSON format"""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(report_data, file, indent=2, ensure_ascii=False, default=str)
    
    def _save_html_report(self, report_data: Dict[str, Any], file_path: Path):
        """Save report in HTML format"""
        html_content = self._generate_html_report(report_data)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
    
    def _save_csv_report(self, report_data: Dict[str, Any], file_path: Path):
        """Save report in CSV format"""
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write headers
            writer.writerow([
                'Table Name', 'Risk Level', 'Total Columns', 'Sensitive Columns',
                'Column Name', 'Data Type', 'PII Type', 'Sensitivity Level',
                'Applicable Regulations', 'Risk Explanation'
            ])
            
            # Write data
            for table_detail in report_data.get('detailed_results', []):
                table_name = table_detail['table_name']
                risk_level = table_detail['risk_assessment']['overall_risk']
                total_columns = table_detail['column_breakdown']['total_columns']
                sensitive_columns = table_detail['column_breakdown']['sensitive_columns']
                
                for column in table_detail['detailed_columns']:
                    # Convert enum objects to strings for CSV export
                    applicable_regulations = column.get('applicable_regulations', [])
                    if applicable_regulations:
                        # Handle both string and enum formats
                        regulation_strings = []
                        for reg in applicable_regulations:
                            if hasattr(reg, 'value'):
                                regulation_strings.append(reg.value)
                            elif hasattr(reg, 'name'):
                                regulation_strings.append(reg.name)
                            else:
                                regulation_strings.append(str(reg))
                        regulations_str = '; '.join(regulation_strings)
                    else:
                        regulations_str = ''
                    
                    # Convert other enum fields to strings
                    pii_type_str = column.get('pii_type', '')
                    if hasattr(pii_type_str, 'value'):
                        pii_type_str = pii_type_str.value
                    elif hasattr(pii_type_str, 'name'):
                        pii_type_str = pii_type_str.name
                    else:
                        pii_type_str = str(pii_type_str)
                    
                    sensitivity_level_str = column.get('sensitivity_level', '')
                    if hasattr(sensitivity_level_str, 'value'):
                        sensitivity_level_str = sensitivity_level_str.value
                    elif hasattr(sensitivity_level_str, 'name'):
                        sensitivity_level_str = sensitivity_level_str.name
                    else:
                        sensitivity_level_str = str(sensitivity_level_str)
                    
                    writer.writerow([
                        table_name, risk_level, total_columns, sensitive_columns,
                        column['column_name'], column['data_type'], pii_type_str,
                        sensitivity_level_str, regulations_str,
                        column['risk_explanation']
                    ])
    
    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report content"""
        # This is a simplified HTML template
        # In a real implementation, you'd use a proper templating engine
        
        summary = report_data.get('analysis_summary', {})
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PII/PHI Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; }}
                .summary {{ background-color: #e8f4f8; padding: 15px; margin: 20px 0; }}
                .table {{ border-collapse: collapse; width: 100%; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .table th {{ background-color: #f2f2f2; }}
                .high-risk {{ background-color: #ffebee; }}
                .medium-risk {{ background-color: #fff3e0; }}
                .low-risk {{ background-color: #e8f5e8; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PII/PHI Analysis Report</h1>
                <p>Generated on: {report_data.get('report_metadata', {}).get('generated_at', 'Unknown')}</p>
            </div>
            
            <div class="summary">
                <h2>Analysis Summary</h2>
                <ul>
                    <li>Total Tables Analyzed: {summary.get('total_tables_analyzed', 0)}</li>
                    <li>Total Columns Analyzed: {summary.get('total_columns_analyzed', 0)}</li>
                    <li>Sensitive Columns Found: {summary.get('total_sensitive_columns', 0)}</li>
                    <li>High Risk Tables: {summary.get('high_risk_tables', 0)}</li>
                </ul>
            </div>
            
            <h2>Detailed Analysis</h2>
            {self._generate_html_table_details(report_data.get('detailed_results', []))}
        </body>
        </html>
        """
        
        return html_template
    
    def _generate_html_table_details(self, detailed_results: List[Dict[str, Any]]) -> str:
        """Generate HTML for detailed table analysis"""
        html_parts = []
        
        for table_detail in detailed_results:
            risk_level = table_detail['risk_assessment']['overall_risk'].lower()
            risk_class = f"{risk_level}-risk"
            
            html_parts.append(f"""
            <div class="{risk_class}" style="margin: 20px 0; padding: 15px;">
                <h3>{html.escape(table_detail['table_name'])}</h3>
                <p><strong>Risk Level:</strong> {table_detail['risk_assessment']['overall_risk']}</p>
                <p><strong>Sensitive Columns:</strong> {table_detail['column_breakdown']['sensitive_columns']} 
                   of {table_detail['column_breakdown']['total_columns']}</p>
            </div>
            """)
        
        return ''.join(html_parts)
    
    # Helper methods for analysis
    def _identify_risk_factors(self, result: TableAnalysisResult) -> List[str]:
        """Identify specific risk factors for a table"""
        risk_factors = []
        
        if result.sensitivity_ratio > 0.5:
            risk_factors.append("High proportion of sensitive columns")
        
        high_risk_columns = result.get_columns_by_risk(RiskLevel.HIGH)
        if high_risk_columns:
            risk_factors.append(f"{len(high_risk_columns)} high-risk columns identified")
        
        return risk_factors
    
    def _group_columns_by_sensitivity(self, result: TableAnalysisResult) -> Dict[str, int]:
        """Group columns by sensitivity level"""
        sensitivity_groups = {level.value: 0 for level in RiskLevel}
        
        for column in result.column_analysis:
            sensitivity_groups[column.sensitivity_level.value] += 1
        
        return sensitivity_groups
    
    def _group_columns_by_pii_type(self, result: TableAnalysisResult) -> Dict[str, int]:
        """Group columns by PII type"""
        pii_groups = {}
        
        for column in result.column_analysis:
            if column.is_sensitive:
                pii_type = column.pii_type.value
                pii_groups[pii_type] = pii_groups.get(pii_type, 0) + 1
        
        return pii_groups
    
    def _generate_compliance_details(self, result: TableAnalysisResult) -> Dict[str, Any]:
        """Generate compliance details for a table"""
        return {
            'gdpr_applicable': Regulation.GDPR in result.applicable_regulations,
            'hipaa_applicable': Regulation.HIPAA in result.applicable_regulations,
            'ccpa_applicable': Regulation.CCPA in result.applicable_regulations
        }
    
    def _assess_compliance_status(self, tables: List[TableAnalysisResult], 
                                 regulation: Regulation) -> str:
        """Assess compliance status for a regulation"""
        if not tables:
            return "Not Applicable"
        
        high_risk_count = len([t for t in tables if t.risk_level == RiskLevel.HIGH])
        
        if high_risk_count > 0:
            return "Requires Review"
        else:
            return "Low Risk"
    
    def _get_regulation_requirements(self, regulation: Regulation) -> List[str]:
        """Get key requirements for a regulation"""
        requirements_map = {
            Regulation.GDPR: [
                "Data subject consent management",
                "Right to be forgotten implementation",
                "Data breach notification procedures",
                "Privacy by design principles"
            ],
            Regulation.HIPAA: [
                "PHI access controls and audit trails",
                "Encryption of PHI in transit and at rest",
                "Business associate agreements",
                "Security incident procedures"
            ],
            Regulation.CCPA: [
                "Consumer privacy rights implementation",
                "Data collection disclosure requirements",
                "Opt-out mechanisms for data sale",
                "Data deletion procedures"
            ]
        }
        
        return requirements_map.get(regulation, [])
    
    def _get_regulation_specific_recommendations(self, regulation: Regulation) -> List[str]:
        """Get regulation-specific recommendations"""
        recommendations_map = {
            Regulation.GDPR: [
                "Implement consent management system",
                "Establish data retention policies",
                "Create data subject request procedures"
            ],
            Regulation.HIPAA: [
                "Implement access controls for PHI",
                "Establish audit logging for PHI access",
                "Create incident response procedures"
            ],
            Regulation.CCPA: [
                "Implement consumer request portal",
                "Establish data inventory and mapping",
                "Create privacy policy updates"
            ]
        }
        
        return recommendations_map.get(regulation, [])


# Global report service instance
report_service = ReportService()