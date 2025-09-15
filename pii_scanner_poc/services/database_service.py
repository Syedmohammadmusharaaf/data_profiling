"""
Database service for PII Scanner
Handles schema loading from files and database connections
"""

import re
import json
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Any

from pii_scanner_poc.models.data_models import ColumnMetadata
from pii_scanner_poc.utils.logging_config import main_logger, log_function_entry, log_function_exit


class DatabaseService:
    """Service for loading database schema information"""
    
    def load_schema_from_content(self, content: str, file_type: str) -> List[ColumnMetadata]:
        """
        Load schema from file content string
        
        Args:
            content: File content as string
            file_type: Type of file (ddl, sql, json, csv, etc.)
            
        Returns:
            List of ColumnMetadata objects
        """
        log_function_entry(main_logger, "load_schema_from_content", file_type=file_type)
        
        try:
            import tempfile
            import os
            
            # Create temporary file with content
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{file_type}', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Load schema from temporary file
                schema_data = self.load_schema_from_file(temp_file_path)
                
                # Convert to list format expected by the API
                column_list = []
                for table_name, columns in schema_data.items():
                    column_list.extend(columns)
                
                main_logger.info("Schema loaded from content", extra={
                    'component': 'database_service',
                    'file_type': file_type,
                    'total_columns': len(column_list),
                    'total_tables': len(schema_data)
                })
                
                log_function_exit(main_logger, "load_schema_from_content",
                                f"Loaded {len(column_list)} columns from {len(schema_data)} tables")
                
                return column_list
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            main_logger.error("Failed to load schema from content", extra={
                'component': 'database_service',
                'file_type': file_type,
                'error': str(e)
            }, exc_info=True)
            raise

    def load_schema_from_file(self, file_path: str) -> Dict[str, List[ColumnMetadata]]:
        """
        Load schema from various file formats (DDL, JSON, etc.)
        
        Args:
            file_path: Path to the schema file
            
        Returns:
            Dictionary mapping table names to list of ColumnMetadata
        """
        log_function_entry(main_logger, "load_schema_from_file", file_path=file_path)
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"Schema file not found: {file_path}")
            
            file_extension = file_path_obj.suffix.lower()
            
            main_logger.info("Loading schema from file", extra={
                'component': 'database_service',
                'file_path': file_path,
                'file_extension': file_extension,
                'file_size': file_path_obj.stat().st_size
            })
            
            if file_extension in ['.ddl', '.sql']:
                schema_data = self._parse_ddl_file(file_path)
            elif file_extension == '.json':
                schema_data = self._parse_json_file(file_path)
            elif file_extension == '.ini':
                schema_data = self._parse_ini_file(file_path)
            else:
                # Try to auto-detect format
                schema_data = self._auto_detect_and_parse(file_path)
            
            total_tables = len(schema_data)
            total_columns = sum(len(columns) for columns in schema_data.values())
            
            main_logger.info("Schema loaded successfully", extra={
                'component': 'database_service',
                'file_path': file_path,
                'total_tables': total_tables,
                'total_columns': total_columns,
                'table_names': list(schema_data.keys())
            })
            
            log_function_exit(main_logger, "load_schema_from_file",
                            f"Loaded {total_tables} tables with {total_columns} columns")
            
            return schema_data
            
        except Exception as e:
            main_logger.error("Failed to load schema from file", extra={
                'component': 'database_service',
                'file_path': file_path,
                'error': str(e)
            }, exc_info=True)
            raise
    
    def load_schema_from_database(self, connection_config: Dict[str, Any],
                                 schema_name: Optional[str] = None,
                                 selected_tables: Optional[List[str]] = None) -> Dict[str, List[ColumnMetadata]]:
        """
        Load schema from live database connection
        
        Args:
            connection_config: Database connection configuration
            schema_name: Optional specific schema to analyze
            selected_tables: Optional list of specific tables to analyze
            
        Returns:
            Dictionary mapping table names to list of ColumnMetadata
        """
        log_function_entry(main_logger, "load_schema_from_database",
                          schema_name=schema_name,
                          selected_tables=selected_tables)
        
        try:
            # This is a placeholder for actual database connectivity
            # In a real implementation, this would use appropriate database drivers
            
            main_logger.info("Loading schema from database", extra={
                'component': 'database_service',
                'schema_name': schema_name,
                'selected_tables': selected_tables
            })
            
            # For now, return empty schema - this would be implemented with actual DB connectivity
            schema_data = {}
            
            main_logger.warning("Database connectivity not implemented", extra={
                'component': 'database_service',
                'message': "This feature requires database driver implementation"
            })
            
            log_function_exit(main_logger, "load_schema_from_database", "Placeholder implementation")
            
            return schema_data
            
        except Exception as e:
            main_logger.error("Failed to load schema from database", extra={
                'component': 'database_service',
                'error': str(e)
            }, exc_info=True)
            raise
    
    def _parse_ddl_file(self, file_path: str) -> Dict[str, List[ColumnMetadata]]:
        """Enhanced DDL/SQL file parser for complex schemas"""
        schema_data = {}
        
        try:
            # Read file with multiple encoding attempts
            content = self._read_file_with_encoding(file_path)
            
            # Clean and normalize DDL content
            cleaned_content = self._clean_ddl_content(content)
            
            # Parse CREATE TABLE statements with enhanced regex
            table_data = self._extract_create_table_statements(cleaned_content)
            
            main_logger.info(f"Found {len(table_data)} CREATE TABLE statements", extra={
                'component': 'database_service',
                'file_path': file_path,
                'tables_found': list(table_data.keys())
            })
            
            # Process each table
            for table_name, table_definition in table_data.items():
                columns = self._parse_table_columns(table_name, table_definition)
                if columns:
                    schema_data[table_name] = columns
                    
            main_logger.info(f"Successfully parsed DDL file", extra={
                'component': 'database_service',
                'file_path': file_path,
                'total_tables': len(schema_data),
                'total_columns': sum(len(cols) for cols in schema_data.values())
            })
            
            return schema_data
            
        except Exception as e:
            main_logger.error(f"Error parsing DDL file: {e}", extra={
                'component': 'database_service',
                'file_path': file_path,
                'error': str(e)
            }, exc_info=True)
            raise
    
    def _read_file_with_encoding(self, file_path: str) -> str:
        """Read file with multiple encoding attempts"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail, try with error handling
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            main_logger.warning("File read with encoding errors ignored", extra={
                'component': 'database_service',
                'file_path': file_path
            })
            return content
    
    def _clean_ddl_content(self, content: str) -> str:
        """Clean and normalize DDL content"""
        # Remove comments
        content = re.sub(r'--.*?\n', '\n', content)  # Single line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)  # Multi-line comments
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        content = content.replace('\n', ' ').replace('\r', ' ')
        
        # Remove extra semicolons and normalize
        content = re.sub(r';\s*;+', ';', content)
        
        return content.strip()
    
    def _extract_create_table_statements(self, content: str) -> Dict[str, str]:
        """Extract CREATE TABLE statements with enhanced parsing"""
        table_data = {}
        
        # Enhanced regex patterns for various CREATE TABLE formats
        patterns = [
            # Standard CREATE TABLE
            r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)\s*\((.*?)\)\s*(?:ENGINE\s*=\s*[^;]*)?;',
            # With schema prefix
            r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^.\s]+\.)?([^\s(]+)\s*\((.*?)\)\s*(?:ENGINE\s*=\s*[^;]*)?;',
            # With constraints and options
            r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)\s*\((.*?)\)\s*(?:WITH\s*\([^)]*\))?(?:ENGINE\s*=\s*[^;]*)?;',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                if len(match) == 2:
                    # Standard pattern (table_name, columns)
                    table_name, columns_text = match
                elif len(match) == 3:
                    # Schema.table pattern (schema, table_name, columns)
                    schema_prefix, table_name, columns_text = match
                    if schema_prefix:  # Include schema in table name
                        table_name = f"{schema_prefix.rstrip('.')}.{table_name}"
                else:
                    continue
                
                # Clean table name
                table_name = table_name.strip().strip('`"[]')
                if table_name and columns_text:
                    table_data[table_name] = columns_text.strip()
        
        return table_data
    
    def _parse_table_columns(self, table_name: str, table_definition: str) -> List[ColumnMetadata]:
        """Parse columns from table definition with enhanced logic"""
        columns = []
        
        try:
            # Split by commas but handle nested parentheses
            column_definitions = self._split_column_definitions(table_definition)
            
            for col_def in column_definitions:
                col_def = col_def.strip()
                if not col_def or col_def.upper().startswith(('PRIMARY KEY', 'FOREIGN KEY', 'KEY ', 'INDEX ', 'CONSTRAINT', 'UNIQUE')):
                    continue
                
                column_metadata = self._parse_single_column(table_name, col_def)
                if column_metadata:
                    columns.append(column_metadata)
            
            main_logger.debug(f"Parsed {len(columns)} columns for table {table_name}", extra={
                'component': 'database_service',
                'table_name': table_name,
                'column_count': len(columns)
            })
            
        except Exception as e:
            main_logger.error(f"Error parsing columns for table {table_name}: {e}", extra={
                'component': 'database_service',
                'table_name': table_name,
                'error': str(e)
            })
        
        return columns
    
    def _split_column_definitions(self, table_definition: str) -> List[str]:
        """Split column definitions handling nested parentheses"""
        definitions = []
        current_def = ""
        paren_count = 0
        in_quotes = False
        quote_char = None
        
        for char in table_definition:
            if char in ('"', "'", '`') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif not in_quotes:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == ',' and paren_count == 0:
                    definitions.append(current_def.strip())
                    current_def = ""
                    continue
            
            current_def += char
        
        if current_def.strip():
            definitions.append(current_def.strip())
        
        return definitions
    
    def _parse_single_column(self, table_name: str, column_definition: str) -> Optional[ColumnMetadata]:
        """Parse a single column definition"""
        try:
            # Enhanced column parsing regex
            column_patterns = [
                # Basic pattern: column_name data_type [constraints]
                r'^\s*([`"\[]?)([^`"\]\s]+)\1\s+([^\s]+)(.*)$',
                # Pattern with quotes: "column_name" data_type [constraints]
                r'^\s*[`"\[]([^`"\]]+)[`"\]]\s+([^\s]+)(.*)$'
            ]
            
            for pattern in column_patterns:
                match = re.match(pattern, column_definition, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 4:
                        # Pattern with quote indicator
                        _, column_name, data_type, constraints = match.groups()
                    else:
                        # Pattern without quote indicator
                        column_name, data_type, constraints = match.groups()
                    
                    break
            else:
                # Fallback: simple split
                parts = column_definition.strip().split()
                if len(parts) >= 2:
                    column_name = parts[0].strip('`"[]')
                    data_type = parts[1]
                    constraints = ' '.join(parts[2:]) if len(parts) > 2 else ""
                else:
                    return None
            
            # Clean column name and data type
            column_name = column_name.strip().strip('`"[]')
            data_type = data_type.strip().upper()
            
            # Parse constraints for additional metadata
            is_nullable = not ('NOT NULL' in constraints.upper())
            
            # Extract length/precision information
            max_length = None
            if '(' in data_type and ')' in data_type:
                length_match = re.search(r'\((\d+)(?:,\d+)?\)', data_type)
                if length_match:
                    max_length = int(length_match.group(1))
                    data_type = re.sub(r'\([^)]*\)', '', data_type)
            
            # Extract default value
            default_value = None
            default_match = re.search(r'DEFAULT\s+([^\s]+)', constraints, re.IGNORECASE)
            if default_match:
                default_value = default_match.group(1).strip("'\"")
            
            # Extract schema name from table name if present
            if '.' in table_name:
                schema_name, table_name_only = table_name.split('.', 1)
            else:
                schema_name = "public"  # Default schema
                table_name_only = table_name
            
            return ColumnMetadata(
                schema_name=schema_name,
                table_name=table_name_only,
                column_name=column_name,
                data_type=data_type,
                is_nullable=is_nullable,
                max_length=max_length,
                default_value=default_value
            )
            
        except Exception as e:
            main_logger.error(f"Error parsing column definition: {column_definition}", extra={
                'component': 'database_service',
                'table_name': table_name,
                'column_definition': column_definition,
                'error': str(e)
            })
            return None
    
    def _parse_ddl_columns(self, columns_text: str, schema_name: str, table_name: str) -> List[ColumnMetadata]:
        """Parse column definitions from DDL"""
        columns = []
        
        # Pre-process the text to remove comments and clean up
        cleaned_text = self._clean_ddl_text(columns_text)
        
        # Split by comma, but be careful with nested parentheses  
        column_lines = self._split_ddl_columns(cleaned_text)
        
        for line in column_lines:
            line = line.strip()
            
            # Skip empty lines and remaining comments
            if not line or line.startswith('--') or line.startswith('/*'):
                continue
            
            # Skip constraint definitions (but allow column-level constraints)
            if line.upper().startswith(('CONSTRAINT', 'PRIMARY KEY (', 'FOREIGN KEY (', 'INDEX', 'KEY (')):
                continue
            
            # Parse column definition
            column = self._parse_single_column_definition(line, schema_name, table_name)
            if column:
                columns.append(column)
        
        return columns
    
    def _clean_ddl_text(self, text: str) -> str:
        """Clean DDL text by removing comments and normalizing whitespace"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove inline comments
            if '--' in line:
                line = line[:line.find('--')]
            
            # Remove block comments (/* ... */)
            while '/*' in line and '*/' in line:
                start = line.find('/*')
                end = line.find('*/', start) + 2
                line = line[:start] + line[end:]
            
            # Keep the line if it has content after cleaning
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _split_ddl_columns(self, columns_text: str) -> List[str]:
        """Split column definitions handling nested parentheses"""
        lines = []
        current_line = ""
        paren_depth = 0
        
        for char in columns_text:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                if current_line.strip():
                    lines.append(current_line.strip())
                current_line = ""
                continue
            
            current_line += char
        
        if current_line.strip():
            lines.append(current_line.strip())
        
        return lines
    
    def _parse_single_column_definition(self, line: str, schema_name: str, table_name: str) -> Optional[ColumnMetadata]:
        """Parse a single column definition"""
        try:
            # Basic pattern: column_name data_type [constraints]
            parts = line.split()
            if len(parts) < 2:
                return None
            
            column_name = parts[0].strip('`"[]')
            data_type = parts[1]
            
            # Handle data types with parameters like VARCHAR(50)
            if '(' in data_type:
                type_match = re.match(r'([A-Z]+)\((\d+)\)', data_type.upper())
                if type_match:
                    base_type = type_match.group(1)
                    max_length = int(type_match.group(2))
                else:
                    base_type = data_type.split('(')[0]
                    max_length = None
            else:
                base_type = data_type.upper()
                max_length = None
            
            # Check for NULL constraints
            is_nullable = 'NOT NULL' not in line.upper()
            
            return ColumnMetadata(
                schema_name=schema_name,
                table_name=table_name,
                column_name=column_name,
                data_type=base_type,
                is_nullable=is_nullable,
                max_length=max_length
            )
            
        except Exception as e:
            main_logger.warning(f"Could not parse column definition: {line}", extra={
                'component': 'database_service',
                'table_name': table_name,
                'error': str(e)
            })
            return None
    
    def _parse_json_file(self, file_path: str) -> Dict[str, List[ColumnMetadata]]:
        """Parse JSON file format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            schema_data = {}
            
            if isinstance(data, dict) and 'tables' in data:
                # Handle structured JSON format
                for table_info in data['tables']:
                    table_name = table_info['name']
                    columns = []
                    
                    for col_info in table_info.get('columns', []):
                        column = ColumnMetadata(
                            schema_name=table_info.get('schema', ''),
                            table_name=table_name,
                            column_name=col_info['name'],
                            data_type=col_info['type'],
                            is_nullable=col_info.get('nullable', True),
                            max_length=col_info.get('max_length')
                        )
                        columns.append(column)
                    
                    schema_data[table_name] = columns
            
            return schema_data
            
        except Exception as e:
            main_logger.error("Failed to parse JSON file", extra={
                'component': 'database_service',
                'file_path': file_path,
                'error': str(e)
            })
            raise
    
    def _parse_ini_file(self, file_path: str) -> Dict[str, List[ColumnMetadata]]:
        """Parse INI configuration file format"""
        try:
            config = configparser.ConfigParser()
            config.read(file_path)
            
            schema_data = {}
            
            # This is a placeholder - actual implementation would depend on INI structure
            main_logger.warning("INI file parsing not fully implemented", extra={
                'component': 'database_service',
                'file_path': file_path
            })
            
            return schema_data
            
        except Exception as e:
            main_logger.error("Failed to parse INI file", extra={
                'component': 'database_service',
                'file_path': file_path,
                'error': str(e)
            })
            raise
    
    def _auto_detect_and_parse(self, file_path: str) -> Dict[str, List[ColumnMetadata]]:
        """Auto-detect file format and parse accordingly"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Check for DDL patterns
            if re.search(r'CREATE\s+TABLE', content, re.IGNORECASE):
                main_logger.info("Auto-detected DDL format", extra={
                    'component': 'database_service',
                    'file_path': file_path
                })
                return self._parse_ddl_file(file_path)
            
            # Check for JSON
            if content.strip().startswith('{'):
                main_logger.info("Auto-detected JSON format", extra={
                    'component': 'database_service',
                    'file_path': file_path
                })
                return self._parse_json_file(file_path)
            
            # Default to DDL
            main_logger.warning("Could not auto-detect format, defaulting to DDL", extra={
                'component': 'database_service',
                'file_path': file_path
            })
            return self._parse_ddl_file(file_path)
            
        except Exception as e:
            main_logger.error("Auto-detection failed", extra={
                'component': 'database_service',
                'file_path': file_path,
                'error': str(e)
            })
            raise


# Global database service instance
database_service = DatabaseService()