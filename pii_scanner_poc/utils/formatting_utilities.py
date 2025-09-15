#!/usr/bin/env python3
"""
Centralized Formatting Utilities
Consolidates all formatting functions that were duplicated across 4 files
"""

import json
import csv
import io
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union, TextIO
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from pii_scanner_poc.models.data_models import ColumnMetadata, PIIType, RiskLevel, Regulation


class OutputFormat(Enum):
    """Supported output formats"""
    CONSOLE = "console"
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    HTML = "html"
    MARKDOWN = "markdown"
    TEXT = "text"


@dataclass
class FormattingOptions:
    """Configuration options for formatting output"""
    include_metadata: bool = True
    include_statistics: bool = True
    include_timestamps: bool = True
    pretty_print: bool = True
    indent_size: int = 2
    color_output: bool = False
    max_column_width: int = 50
    show_confidence_scores: bool = True
    show_rationale: bool = True
    group_by_table: bool = True


class ConsolidatedFormatter:
    """
    Centralized formatter that consolidates all format functions
    
    This class replaces the duplicate 'format' functions found in 4 different files
    and provides a unified, extensible formatting interface for all output types.
    """
    
    def __init__(self, options: Optional[FormattingOptions] = None):
        """
        Initialize the consolidated formatter
        
        Args:
            options: Formatting configuration options
        """
        self.options = options or FormattingOptions()
        
        # Color codes for console output
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m', 
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'underline': '\033[4m',
            'reset': '\033[0m'
        }
        
        # Risk level color mapping
        self.risk_colors = {
            RiskLevel.HIGH: 'red',
            RiskLevel.MEDIUM: 'yellow', 
            RiskLevel.LOW: 'green'
        }
    
    def format_analysis_results(self, 
                               results: List[Dict[str, Any]], 
                               format_type: Union[OutputFormat, str],
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Format analysis results in the specified format
        
        Args:
            results: List of analysis result dictionaries
            format_type: Output format type
            metadata: Optional metadata to include
            
        Returns:
            str: Formatted output string
        """
        if isinstance(format_type, str):
            format_type = OutputFormat(format_type.lower())
        
        # Dispatch to appropriate formatter
        formatters = {
            OutputFormat.CONSOLE: self._format_console,
            OutputFormat.JSON: self._format_json,
            OutputFormat.CSV: self._format_csv,
            OutputFormat.XML: self._format_xml,
            OutputFormat.HTML: self._format_html,
            OutputFormat.MARKDOWN: self._format_markdown,
            OutputFormat.TEXT: self._format_text
        }
        
        if format_type not in formatters:
            raise ValueError(f"Unsupported format type: {format_type}")
        
        formatter = formatters[format_type]
        return formatter(results, metadata)
    
    def _format_console(self, results: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format results for console output with colors and structure"""
        output = []
        
        # Header
        if self.options.color_output:
            header = f"{self.colors['bold']}{self.colors['blue']}PII/PHI Analysis Results{self.colors['reset']}"
        else:
            header = "PII/PHI Analysis Results"
        
        output.append(header)
        output.append("=" * 60)
        
        # Metadata section
        if metadata and self.options.include_metadata:
            output.append("\n📊 Analysis Metadata:")
            for key, value in metadata.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, default=str)
                output.append(f"   {key}: {value}")
        
        # Results section
        if self.options.group_by_table:
            # Group results by table
            tables = {}
            for result in results:
                table_name = result.get('table_name', 'unknown')
                if table_name not in tables:
                    tables[table_name] = []
                tables[table_name].append(result)
            
            for table_name, table_results in tables.items():
                output.append(f"\n🗂️ Table: {table_name}")
                output.append("-" * 40)
                
                for result in table_results:
                    output.append(self._format_single_result_console(result))
        else:
            # List all results sequentially
            output.append(f"\n📋 Analysis Results ({len(results)} fields):")
            for i, result in enumerate(results, 1):
                output.append(f"\n{i}. {self._format_single_result_console(result)}")
        
        # Statistics section
        if self.options.include_statistics:
            stats = self._calculate_statistics(results)
            output.append(f"\n📈 Summary Statistics:")
            output.append(f"   Total Fields: {stats['total_fields']}")
            output.append(f"   Sensitive Fields: {stats['sensitive_fields']} ({stats['sensitivity_rate']:.1f}%)")
            output.append(f"   High Risk Fields: {stats['high_risk_fields']}")
            output.append(f"   Average Confidence: {stats['average_confidence']:.2f}")
        
        return "\n".join(output)
    
    def _format_single_result_console(self, result: Dict[str, Any]) -> str:
        """Format a single result for console display"""
        field_name = result.get('field_name', 'unknown')
        pii_type = result.get('pii_type', 'NONE')
        risk_level = result.get('risk_level', 'LOW')
        confidence = result.get('confidence_score', 0.0)
        is_sensitive = result.get('is_sensitive', False)
        
        # Build status indicator
        if is_sensitive:
            if self.options.color_output:
                risk_color = self.risk_colors.get(RiskLevel(risk_level), 'white')
                status = f"{self.colors[risk_color]}●{self.colors['reset']} SENSITIVE"
            else:
                status = "● SENSITIVE"
        else:
            if self.options.color_output:
                status = f"{self.colors['green']}○{self.colors['reset']} Non-sensitive"
            else:
                status = "○ Non-sensitive"
        
        # Build main line
        main_line = f"{field_name:<30} {status:<15}"
        
        if is_sensitive:
            main_line += f" Type: {pii_type:<10} Risk: {risk_level}"
        
        if self.options.show_confidence_scores:
            main_line += f" (Confidence: {confidence:.2f})"
        
        # Add rationale if requested and available
        lines = [main_line]
        if self.options.show_rationale and result.get('rationale'):
            lines.append(f"     └─ {result['rationale']}")
        
        return "\n".join(lines)
    
    def _format_json(self, results: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format results as JSON"""
        output_data = {
            'analysis_results': results
        }
        
        if metadata and self.options.include_metadata:
            output_data['metadata'] = metadata
        
        if self.options.include_statistics:
            output_data['statistics'] = self._calculate_statistics(results)
        
        if self.options.include_timestamps:
            output_data['generated_at'] = datetime.now().isoformat()
        
        if self.options.pretty_print:
            return json.dumps(output_data, indent=self.options.indent_size, default=str, ensure_ascii=False)
        else:
            return json.dumps(output_data, default=str, ensure_ascii=False)
    
    def _format_csv(self, results: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format results as CSV"""
        if not results:
            return "No results to format"
        
        output = io.StringIO()
        
        # Determine fieldnames from first result
        fieldnames = list(results[0].keys())
        
        # Add standard fields if missing
        standard_fields = ['field_name', 'table_name', 'pii_type', 'risk_level', 'confidence_score', 'is_sensitive']
        for field in standard_fields:
            if field not in fieldnames:
                fieldnames.insert(0, field)
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Convert complex types to strings
            csv_row = {}
            for key, value in result.items():
                if isinstance(value, (list, dict)):
                    csv_row[key] = json.dumps(value, default=str)
                elif hasattr(value, 'value'):  # Enum
                    csv_row[key] = value.value
                else:
                    csv_row[key] = str(value) if value is not None else ""
            writer.writerow(csv_row)
        
        # Add metadata as comments if requested
        if metadata and self.options.include_metadata:
            output.write(f"\n# Metadata:\n")
            for key, value in metadata.items():
                output.write(f"# {key}: {value}\n")
        
        return output.getvalue()
    
    def _format_xml(self, results: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format results as XML"""
        root = ET.Element("pii_analysis")
        
        # Add metadata
        if metadata and self.options.include_metadata:
            metadata_elem = ET.SubElement(root, "metadata")
            for key, value in metadata.items():
                meta_item = ET.SubElement(metadata_elem, key.replace(' ', '_'))
                meta_item.text = str(value)
        
        # Add results
        results_elem = ET.SubElement(root, "results")
        results_elem.set("count", str(len(results)))
        
        for result in results:
            result_elem = ET.SubElement(results_elem, "field_analysis")
            
            for key, value in result.items():
                field_elem = ET.SubElement(result_elem, key.replace(' ', '_'))
                if isinstance(value, (list, dict)):
                    field_elem.text = json.dumps(value, default=str)
                elif hasattr(value, 'value'):  # Enum
                    field_elem.text = value.value
                else:
                    field_elem.text = str(value) if value is not None else ""
        
        # Add statistics
        if self.options.include_statistics:
            stats = self._calculate_statistics(results)
            stats_elem = ET.SubElement(root, "statistics")
            for key, value in stats.items():
                stat_item = ET.SubElement(stats_elem, key)
                stat_item.text = str(value)
        
        # Pretty print XML
        if self.options.pretty_print:
            self._indent_xml(root)
        
        return ET.tostring(root, encoding='unicode')
    
    def _format_html(self, results: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format results as HTML"""
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html><head>")
        html.append("<title>PII/PHI Analysis Results</title>")
        html.append("<style>")
        html.append("""
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .metadata { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .results-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            .results-table th, .results-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .results-table th { background-color: #f2f2f2; }
            .high-risk { color: #e74c3c; font-weight: bold; }
            .medium-risk { color: #f39c12; font-weight: bold; }
            .low-risk { color: #27ae60; }
            .sensitive { background-color: #ffebee; }
            .statistics { background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        """)
        html.append("</style></head><body>")
        
        # Header
        html.append("<h1 class='header'>PII/PHI Analysis Results</h1>")
        
        # Metadata
        if metadata and self.options.include_metadata:
            html.append("<div class='metadata'>")
            html.append("<h3>Analysis Metadata</h3>")
            html.append("<ul>")
            for key, value in metadata.items():
                html.append(f"<li><strong>{key}:</strong> {value}</li>")
            html.append("</ul></div>")
        
        # Results table
        if results:
            html.append("<table class='results-table'>")
            html.append("<thead><tr>")
            html.append("<th>Field Name</th><th>Table</th><th>Sensitive</th><th>PII Type</th><th>Risk Level</th><th>Confidence</th>")
            if self.options.show_rationale:
                html.append("<th>Rationale</th>")
            html.append("</tr></thead><tbody>")
            
            for result in results:
                is_sensitive = result.get('is_sensitive', False)
                risk_level = result.get('risk_level', 'LOW')
                row_class = 'sensitive' if is_sensitive else ''
                risk_class = f"{risk_level.lower()}-risk" if risk_level else ""
                
                html.append(f"<tr class='{row_class}'>")
                html.append(f"<td>{result.get('field_name', 'N/A')}</td>")
                html.append(f"<td>{result.get('table_name', 'N/A')}</td>")
                html.append(f"<td>{'Yes' if is_sensitive else 'No'}</td>")
                html.append(f"<td>{result.get('pii_type', 'N/A')}</td>")
                html.append(f"<td class='{risk_class}'>{risk_level}</td>")
                html.append(f"<td>{result.get('confidence_score', 0):.2f}</td>")
                if self.options.show_rationale:
                    html.append(f"<td>{result.get('rationale', 'N/A')}</td>")
                html.append("</tr>")
            
            html.append("</tbody></table>")
        
        # Statistics
        if self.options.include_statistics:
            stats = self._calculate_statistics(results)
            html.append("<div class='statistics'>")
            html.append("<h3>Summary Statistics</h3>")
            html.append("<ul>")
            for key, value in stats.items():
                formatted_key = key.replace('_', ' ').title()
                html.append(f"<li><strong>{formatted_key}:</strong> {value}</li>")
            html.append("</ul></div>")
        
        html.append("</body></html>")
        
        return "\n".join(html)
    
    def _format_markdown(self, results: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format results as Markdown"""
        md = []
        md.append("# PII/PHI Analysis Results")
        md.append("")
        
        # Metadata
        if metadata and self.options.include_metadata:
            md.append("## Analysis Metadata")
            md.append("")
            for key, value in metadata.items():
                md.append(f"- **{key}**: {value}")
            md.append("")
        
        # Results
        if results:
            md.append("## Analysis Results")
            md.append("")
            
            # Table header
            headers = ["Field Name", "Table", "Sensitive", "PII Type", "Risk Level", "Confidence"]
            if self.options.show_rationale:
                headers.append("Rationale")
            
            md.append("| " + " | ".join(headers) + " |")
            md.append("| " + " | ".join(["---"] * len(headers)) + " |")
            
            # Table rows
            for result in results:
                row = [
                    result.get('field_name', 'N/A'),
                    result.get('table_name', 'N/A'),
                    '✅ Yes' if result.get('is_sensitive', False) else '❌ No',
                    result.get('pii_type', 'N/A'),
                    result.get('risk_level', 'LOW'),
                    f"{result.get('confidence_score', 0):.2f}"
                ]
                
                if self.options.show_rationale:
                    row.append(result.get('rationale', 'N/A'))
                
                md.append("| " + " | ".join(row) + " |")
            
            md.append("")
        
        # Statistics
        if self.options.include_statistics:
            stats = self._calculate_statistics(results)
            md.append("## Summary Statistics")
            md.append("")
            for key, value in stats.items():
                formatted_key = key.replace('_', ' ').title()
                md.append(f"- **{formatted_key}**: {value}")
            md.append("")
        
        return "\n".join(md)
    
    def _format_text(self, results: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Format results as plain text"""
        lines = []
        lines.append("PII/PHI ANALYSIS RESULTS")
        lines.append("=" * 50)
        lines.append("")
        
        # Metadata
        if metadata and self.options.include_metadata:
            lines.append("ANALYSIS METADATA:")
            for key, value in metadata.items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        # Results
        if results:
            lines.append(f"FIELD ANALYSIS RESULTS ({len(results)} fields):")
            lines.append("-" * 40)
            
            for i, result in enumerate(results, 1):
                lines.append(f"{i}. {result.get('field_name', 'N/A')} ({result.get('table_name', 'N/A')})")
                lines.append(f"   Sensitive: {'Yes' if result.get('is_sensitive', False) else 'No'}")
                if result.get('is_sensitive', False):
                    lines.append(f"   PII Type: {result.get('pii_type', 'N/A')}")
                    lines.append(f"   Risk Level: {result.get('risk_level', 'LOW')}")
                lines.append(f"   Confidence: {result.get('confidence_score', 0):.2f}")
                if self.options.show_rationale and result.get('rationale'):
                    lines.append(f"   Rationale: {result['rationale']}")
                lines.append("")
        
        # Statistics
        if self.options.include_statistics:
            stats = self._calculate_statistics(results)
            lines.append("SUMMARY STATISTICS:")
            lines.append("-" * 20)
            for key, value in stats.items():
                formatted_key = key.replace('_', ' ').title()
                lines.append(f"{formatted_key}: {value}")
        
        return "\n".join(lines)
    
    def _calculate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for results"""
        if not results:
            return {}
        
        total_fields = len(results)
        sensitive_fields = sum(1 for r in results if r.get('is_sensitive', False))
        high_risk_fields = sum(1 for r in results if r.get('risk_level') == 'HIGH')
        
        confidences = [r.get('confidence_score', 0) for r in results if r.get('confidence_score') is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'total_fields': total_fields,
            'sensitive_fields': sensitive_fields,
            'non_sensitive_fields': total_fields - sensitive_fields,
            'sensitivity_rate': (sensitive_fields / total_fields) * 100 if total_fields > 0 else 0,
            'high_risk_fields': high_risk_fields,
            'average_confidence': avg_confidence,
            'max_confidence': max(confidences) if confidences else 0,
            'min_confidence': min(confidences) if confidences else 0
        }
    
    def _indent_xml(self, elem, level=0):
        """Add pretty-printing indentation to XML elements"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def save_formatted_output(self, 
                             formatted_content: str, 
                             file_path: Union[str, Path],
                             format_type: Union[OutputFormat, str]) -> bool:
        """
        Save formatted content to file
        
        Args:
            formatted_content: The formatted content string
            file_path: Path to save the file
            format_type: Format type for appropriate file extension
            
        Returns:
            bool: True if saved successfully
        """
        try:
            file_path = Path(file_path)
            
            # Add appropriate extension if not present
            if isinstance(format_type, str):
                format_type = OutputFormat(format_type.lower())
            
            extensions = {
                OutputFormat.JSON: '.json',
                OutputFormat.CSV: '.csv', 
                OutputFormat.XML: '.xml',
                OutputFormat.HTML: '.html',
                OutputFormat.MARKDOWN: '.md',
                OutputFormat.TEXT: '.txt'
            }
            
            if format_type in extensions and not file_path.suffix:
                file_path = file_path.with_suffix(extensions[format_type])
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            return True
            
        except Exception as e:
            print(f"Error saving formatted output: {e}")
            return False


# Global formatter instance for easy access
_default_formatter = ConsolidatedFormatter()

def format_analysis_results(results: List[Dict[str, Any]], 
                           format_type: Union[OutputFormat, str] = OutputFormat.CONSOLE,
                           metadata: Optional[Dict[str, Any]] = None,
                           options: Optional[FormattingOptions] = None) -> str:
    """
    Convenience function for formatting analysis results
    
    Args:
        results: Analysis results to format
        format_type: Output format type
        metadata: Optional metadata to include
        options: Optional formatting options
        
    Returns:
        str: Formatted output string
    """
    if options:
        formatter = ConsolidatedFormatter(options)
    else:
        formatter = _default_formatter
    
    return formatter.format_analysis_results(results, format_type, metadata)


def format_console_output(results: List[Dict[str, Any]], 
                         include_colors: bool = True,
                         show_statistics: bool = True) -> str:
    """Convenience function for console formatting"""
    options = FormattingOptions(
        color_output=include_colors,
        include_statistics=show_statistics,
        show_confidence_scores=True,
        show_rationale=True
    )
    
    formatter = ConsolidatedFormatter(options)
    return formatter.format_analysis_results(results, OutputFormat.CONSOLE)


def format_json_output(results: List[Dict[str, Any]], 
                      pretty_print: bool = True,
                      include_metadata: bool = True) -> str:
    """Convenience function for JSON formatting"""
    options = FormattingOptions(
        pretty_print=pretty_print,
        include_metadata=include_metadata,
        include_statistics=True,
        include_timestamps=True
    )
    
    formatter = ConsolidatedFormatter(options)
    return formatter.format_analysis_results(results, OutputFormat.JSON)


def format_csv_output(results: List[Dict[str, Any]]) -> str:
    """Convenience function for CSV formatting"""
    formatter = ConsolidatedFormatter()
    return formatter.format_analysis_results(results, OutputFormat.CSV)