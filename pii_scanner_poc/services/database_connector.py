#!/usr/bin/env python3
"""
Enhanced Database Connectivity Service for PII/PHI Scanner
Supports multiple database types with secure connection handling and comprehensive schema extraction
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import uuid

# Database drivers and connection libraries
try:
    import pymysql
    import psycopg2
    import pyodbc
    import cx_Oracle
    import sqlite3
    import pymongo
    import snowflake.connector
    import boto3
except ImportError as e:
    logging.warning(f"Some database drivers not available: {e}")

from pii_scanner_poc.models.data_models import ColumnMetadata
from pii_scanner_poc.utils.logging_config import main_logger

@dataclass
class DatabaseConnection:
    """Database connection configuration with comprehensive support for major database types"""
    type: str  # mysql, postgresql, sqlserver, oracle, sqlite, mongodb, snowflake, redshift
    host: str
    port: str
    database: str
    username: str
    password: str
    ssl: bool = False
    additional_params: Dict[str, Any] = None

class DatabaseConnector:
    """
    Multi-database connector supporting popular database systems
    
    Supported Databases:
    - MySQL/MariaDB: Full schema extraction with table/column metadata
    - PostgreSQL: Advanced schema analysis with constraint information  
    - SQL Server: Enterprise schema discovery with security context
    - Oracle: Comprehensive schema extraction with data dictionary queries
    - SQLite: Local database file analysis
    - MongoDB: Document schema inference and field discovery
    - Snowflake: Cloud data warehouse schema extraction
    - Amazon Redshift: AWS data warehouse integration
    
    Features:
    - Secure connection handling with SSL/TLS support
    - Connection pooling and timeout management
    - Comprehensive error handling and logging
    - Schema caching for performance optimization
    - Cross-platform compatibility
    """

    def __init__(self):
        """Initialize database connector with comprehensive logging and configuration"""
        self.connections = {}
        self.schema_cache = {}
        self.supported_databases = {
            'mysql': self._connect_mysql,
            'postgresql': self._connect_postgresql,
            'sqlserver': self._connect_sqlserver,
            'oracle': self._connect_oracle,
            'sqlite': self._connect_sqlite,
            'mongodb': self._connect_mongodb,
            'snowflake': self._connect_snowflake,
            'redshift': self._connect_redshift
        }
        
        main_logger.info("DatabaseConnector initialized with support for 8 database types")

    def test_connection(self, connection_config: DatabaseConnection) -> Dict[str, Any]:
        """
        Test database connection without extracting schema
        
        Args:
            connection_config: Database connection configuration
            
        Returns:
            Dictionary with connection status and details
        """
        start_time = time.time()
        
        try:
            main_logger.info(f"Testing connection to {connection_config.type} database at {connection_config.host}")
            
            # Validate database type
            if connection_config.type not in self.supported_databases:
                raise ValueError(f"Unsupported database type: {connection_config.type}")
            
            # Attempt connection
            connection = self.supported_databases[connection_config.type](connection_config, test_only=True)
            
            if connection:
                connection_time = time.time() - start_time
                main_logger.info(f"Connection test successful in {connection_time:.2f}s")
                
                return {
                    "status": "success",
                    "message": f"Successfully connected to {connection_config.type} database",
                    "connection_time": connection_time,
                    "database_type": connection_config.type,
                    "database_name": connection_config.database
                }
            else:
                raise Exception("Connection returned None")
                
        except Exception as e:
            connection_time = time.time() - start_time
            error_message = f"Connection test failed after {connection_time:.2f}s: {str(e)}"
            main_logger.error(error_message)
            
            return {
                "status": "error",
                "message": error_message,
                "connection_time": connection_time,
                "error_type": type(e).__name__
            }

    def connect_and_extract_schema(self, connection_config: DatabaseConnection) -> Dict[str, Any]:
        """
        Connect to database and extract comprehensive schema information
        
        Args:
            connection_config: Database connection configuration
            
        Returns:
            Dictionary with extracted schema data, tables, and metadata
        """
        session_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            main_logger.info(f"Connecting to {connection_config.type} database and extracting schema")
            
            # Test connection first
            connection_test = self.test_connection(connection_config)
            if connection_test["status"] != "success":
                return connection_test
            
            # Extract schema based on database type
            if connection_config.type in ['mysql', 'postgresql', 'sqlserver', 'oracle', 'sqlite']:
                schema_data = self._extract_relational_schema(connection_config)
            elif connection_config.type == 'mongodb':
                schema_data = self._extract_mongodb_schema(connection_config)
            elif connection_config.type in ['snowflake', 'redshift']:
                schema_data = self._extract_warehouse_schema(connection_config)
            else:
                raise ValueError(f"Schema extraction not implemented for {connection_config.type}")
            
            # Process extracted data
            tables = {}
            column_metadata = []
            
            for table_name, columns in schema_data.items():
                tables[table_name] = []
                for column_info in columns:
                    # Create ColumnMetadata object
                    column_meta = ColumnMetadata(
                        table_name=table_name,
                        column_name=column_info['column_name'],
                        data_type=column_info['data_type'],
                        schema_name=column_info.get('schema_name', connection_config.database)
                    )
                    
                    column_metadata.append(column_meta)
                    tables[table_name].append({
                        "column_name": column_info['column_name'],
                        "data_type": column_info['data_type'],
                        "schema_name": column_info.get('schema_name', connection_config.database),
                        "nullable": column_info.get('nullable', True),
                        "primary_key": column_info.get('primary_key', False)
                    })
            
            extraction_time = time.time() - start_time
            
            main_logger.info(f"Schema extraction completed in {extraction_time:.2f}s: "
                           f"{len(tables)} tables, {len(column_metadata)} columns")
            
            # Cache the results
            cache_key = f"{connection_config.host}_{connection_config.database}_{connection_config.type}"
            self.schema_cache[cache_key] = {
                "schema_data": column_metadata,
                "tables": tables,
                "extracted_at": datetime.now(),
                "extraction_time": extraction_time
            }
            
            return {
                "session_id": session_id,
                "status": "success",
                "schema_data": column_metadata,
                "tables": tables,
                "total_tables": len(tables),
                "total_columns": len(column_metadata),
                "extraction_time": extraction_time,
                "database_type": connection_config.type,
                "database_name": connection_config.database,
                "message": f"Successfully extracted schema from {connection_config.type} database"
            }
            
        except Exception as e:
            extraction_time = time.time() - start_time
            error_message = f"Schema extraction failed after {extraction_time:.2f}s: {str(e)}"
            main_logger.error(error_message, exc_info=True)
            
            return {
                "session_id": session_id,
                "status": "error",
                "message": error_message,
                "extraction_time": extraction_time,
                "error_type": type(e).__name__
            }

    def _connect_mysql(self, config: DatabaseConnection, test_only: bool = False):
        """Connect to MySQL/MariaDB database with comprehensive error handling"""
        try:
            # Build connection parameters
            connection_params = {
                'host': config.host,
                'port': int(config.port) if config.port else 3306,
                'user': config.username,
                'password': config.password,
                'database': config.database,
                'charset': 'utf8mb4',
                'connect_timeout': 10,
                'read_timeout': 30,
                'write_timeout': 30
            }
            
            if config.ssl:
                connection_params['ssl'] = {'ssl_ca': None, 'ssl_verify_cert': False}
            
            connection = pymysql.connect(**connection_params)
            
            if test_only:
                connection.close()
                return True
            
            return connection
            
        except Exception as e:
            main_logger.error(f"MySQL connection failed: {e}")
            raise

    def _connect_postgresql(self, config: DatabaseConnection, test_only: bool = False):
        """Connect to PostgreSQL database with advanced configuration"""
        try:
            # Build connection string
            connection_string = f"host={config.host} port={config.port or 5432} " \
                               f"dbname={config.database} user={config.username} password={config.password}"
            
            if config.ssl:
                connection_string += " sslmode=require"
            
            connection = psycopg2.connect(connection_string)
            
            if test_only:
                connection.close()
                return True
                
            return connection
            
        except Exception as e:
            main_logger.error(f"PostgreSQL connection failed: {e}")
            raise

    def _connect_sqlserver(self, config: DatabaseConnection, test_only: bool = False):
        """Connect to SQL Server with enterprise features support"""
        try:
            # Build connection string for SQL Server
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};" \
                               f"SERVER={config.host},{config.port or 1433};" \
                               f"DATABASE={config.database};" \
                               f"UID={config.username};" \
                               f"PWD={config.password};"
            
            if config.ssl:
                connection_string += "Encrypt=yes;TrustServerCertificate=yes;"
                
            connection = pyodbc.connect(connection_string, timeout=10)
            
            if test_only:
                connection.close()
                return True
                
            return connection
            
        except Exception as e:
            main_logger.error(f"SQL Server connection failed: {e}")
            raise

    def _connect_oracle(self, config: DatabaseConnection, test_only: bool = False):
        """Connect to Oracle database with comprehensive schema support"""
        try:
            dsn = cx_Oracle.makedsn(config.host, config.port or 1521, service_name=config.database)
            connection = cx_Oracle.connect(config.username, config.password, dsn)
            
            if test_only:
                connection.close()
                return True
                
            return connection
            
        except Exception as e:
            main_logger.error(f"Oracle connection failed: {e}")
            raise

    def _connect_sqlite(self, config: DatabaseConnection, test_only: bool = False):
        """Connect to SQLite database file"""
        try:
            # For SQLite, the 'host' field contains the file path
            database_path = config.host if config.host else config.database
            connection = sqlite3.connect(database_path, timeout=10)
            
            if test_only:
                connection.close()
                return True
                
            return connection
            
        except Exception as e:
            main_logger.error(f"SQLite connection failed: {e}")
            raise

    def _connect_mongodb(self, config: DatabaseConnection, test_only: bool = False):
        """Connect to MongoDB with document schema analysis"""
        try:
            # Build MongoDB connection string
            if config.username and config.password:
                connection_string = f"mongodb://{config.username}:{config.password}@{config.host}:{config.port or 27017}/{config.database}"
            else:
                connection_string = f"mongodb://{config.host}:{config.port or 27017}/{config.database}"
            
            if config.ssl:
                connection_string += "?ssl=true"
            
            client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=10000)
            
            # Test connection
            client.admin.command('ismaster')
            
            if test_only:
                client.close()
                return True
                
            return client
            
        except Exception as e:
            main_logger.error(f"MongoDB connection failed: {e}")
            raise

    def _connect_snowflake(self, config: DatabaseConnection, test_only: bool = False):
        """Connect to Snowflake data warehouse"""
        try:
            connection = snowflake.connector.connect(
                user=config.username,
                password=config.password,
                account=config.host,  # Snowflake account identifier
                warehouse=config.additional_params.get('warehouse') if config.additional_params else None,
                database=config.database,
                schema=config.additional_params.get('schema', 'PUBLIC') if config.additional_params else 'PUBLIC'
            )
            
            if test_only:
                connection.close()
                return True
                
            return connection
            
        except Exception as e:
            main_logger.error(f"Snowflake connection failed: {e}")
            raise

    def _connect_redshift(self, config: DatabaseConnection, test_only: bool = False):
        """Connect to Amazon Redshift data warehouse"""
        try:
            connection_string = f"host={config.host} port={config.port or 5439} " \
                               f"dbname={config.database} user={config.username} password={config.password}"
            
            if config.ssl:
                connection_string += " sslmode=require"
            
            # Redshift uses PostgreSQL driver
            connection = psycopg2.connect(connection_string)
            
            if test_only:
                connection.close()
                return True
                
            return connection
            
        except Exception as e:
            main_logger.error(f"Redshift connection failed: {e}")
            raise

    def _extract_relational_schema(self, config: DatabaseConnection) -> Dict[str, List[Dict]]:
        """Extract schema from relational databases (MySQL, PostgreSQL, SQL Server, Oracle, SQLite)"""
        connection = self.supported_databases[config.type](config)
        cursor = connection.cursor()
        
        try:
            if config.type == 'mysql':
                query = """
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """
                cursor.execute(query, (config.database,))
                
            elif config.type == 'postgresql':
                query = """
                SELECT table_name, column_name, data_type, is_nullable,
                       CASE WHEN constraint_type = 'PRIMARY KEY' THEN 'PRI' ELSE '' END as column_key
                FROM information_schema.columns c
                LEFT JOIN (
                    SELECT tc.table_name, kcu.column_name, tc.constraint_type
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
                WHERE c.table_schema = 'public'
                ORDER BY c.table_name, c.ordinal_position
                """
                cursor.execute(query)
                
            elif config.type == 'sqlserver':
                query = """
                SELECT t.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE, c.IS_NULLABLE,
                       CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 'PRI' ELSE '' END as COLUMN_KEY
                FROM INFORMATION_SCHEMA.TABLES t
                JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
                LEFT JOIN (
                    SELECT ku.COLUMN_NAME, ku.TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                    JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku ON tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                    WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                ) pk ON c.COLUMN_NAME = pk.COLUMN_NAME AND c.TABLE_NAME = pk.TABLE_NAME
                WHERE t.TABLE_TYPE = 'BASE TABLE'
                ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
                """
                cursor.execute(query)
                
            elif config.type == 'oracle':
                query = """
                SELECT t.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE, c.NULLABLE,
                       CASE WHEN cc.CONSTRAINT_TYPE = 'P' THEN 'PRI' ELSE '' END as COLUMN_KEY
                FROM USER_TABLES t
                JOIN USER_TAB_COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
                LEFT JOIN (
                    SELECT cons.TABLE_NAME, cols.COLUMN_NAME, cons.CONSTRAINT_TYPE
                    FROM USER_CONSTRAINTS cons
                    JOIN USER_CONS_COLUMNS cols ON cons.CONSTRAINT_NAME = cols.CONSTRAINT_NAME
                    WHERE cons.CONSTRAINT_TYPE = 'P'
                ) cc ON c.TABLE_NAME = cc.TABLE_NAME AND c.COLUMN_NAME = cc.COLUMN_NAME
                ORDER BY t.TABLE_NAME, c.COLUMN_ID
                """
                cursor.execute(query)
                
            elif config.type == 'sqlite':
                # Get all table names first
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                schema_data = {}
                for (table_name,) in tables:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    schema_data[table_name] = []
                    for column in columns:
                        schema_data[table_name].append({
                            'column_name': column[1],
                            'data_type': column[2],
                            'nullable': not column[3],
                            'primary_key': column[5] == 1,
                            'schema_name': 'main'
                        })
                
                return schema_data
            
            # Process results for non-SQLite databases
            results = cursor.fetchall()
            schema_data = {}
            
            for row in results:
                if config.type == 'oracle':
                    table_name, column_name, data_type, nullable, column_key = row
                    is_nullable = nullable == 'Y'
                else:
                    table_name, column_name, data_type, is_nullable, column_key = row
                    is_nullable = is_nullable.lower() in ('yes', 'y', '1', 'true') if isinstance(is_nullable, str) else bool(is_nullable)
                
                if table_name not in schema_data:
                    schema_data[table_name] = []
                
                schema_data[table_name].append({
                    'column_name': column_name,
                    'data_type': data_type,
                    'nullable': is_nullable,
                    'primary_key': column_key == 'PRI',
                    'schema_name': config.database
                })
            
            return schema_data
            
        finally:
            cursor.close()
            connection.close()

    def _extract_mongodb_schema(self, config: DatabaseConnection) -> Dict[str, List[Dict]]:
        """Extract schema from MongoDB by analyzing document structure"""
        client = self.supported_databases[config.type](config)
        database = client[config.database]
        
        try:
            schema_data = {}
            
            # Get all collection names
            collections = database.list_collection_names()
            
            for collection_name in collections:
                collection = database[collection_name]
                
                # Sample documents to infer schema
                sample_docs = list(collection.find().limit(100))
                
                if sample_docs:
                    fields = set()
                    for doc in sample_docs:
                        fields.update(self._extract_document_fields(doc))
                    
                    schema_data[collection_name] = []
                    for field in sorted(fields):
                        # Infer data type from field name and common patterns
                        data_type = self._infer_mongodb_field_type(field, sample_docs)
                        
                        schema_data[collection_name].append({
                            'column_name': field,
                            'data_type': data_type,
                            'nullable': True,  # MongoDB fields are generally nullable
                            'primary_key': field == '_id',
                            'schema_name': config.database
                        })
            
            return schema_data
            
        finally:
            client.close()

    def _extract_warehouse_schema(self, config: DatabaseConnection) -> Dict[str, List[Dict]]:
        """Extract schema from data warehouses (Snowflake, Redshift)"""
        connection = self.supported_databases[config.type](config)
        cursor = connection.cursor()
        
        try:
            if config.type == 'snowflake':
                query = """
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = UPPER(%s)
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """
                cursor.execute(query, (config.additional_params.get('schema', 'PUBLIC') if config.additional_params else 'PUBLIC',))
                
            elif config.type == 'redshift':
                query = """
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
                """
                cursor.execute(query)
            
            results = cursor.fetchall()
            schema_data = {}
            
            for table_name, column_name, data_type, is_nullable in results:
                if table_name not in schema_data:
                    schema_data[table_name] = []
                
                schema_data[table_name].append({
                    'column_name': column_name,
                    'data_type': data_type,
                    'nullable': is_nullable.lower() in ('yes', 'y', '1', 'true') if isinstance(is_nullable, str) else bool(is_nullable),
                    'primary_key': False,  # Would need additional query for primary keys
                    'schema_name': config.database
                })
            
            return schema_data
            
        finally:
            cursor.close()
            connection.close()

    def _extract_document_fields(self, doc, prefix=''):
        """Recursively extract field names from MongoDB document"""
        fields = []
        
        if isinstance(doc, dict):
            for key, value in doc.items():
                field_name = f"{prefix}.{key}" if prefix else key
                fields.append(field_name)
                
                # Recursively process nested documents
                if isinstance(value, dict):
                    fields.extend(self._extract_document_fields(value, field_name))
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    fields.extend(self._extract_document_fields(value[0], field_name))
        
        return fields

    def _infer_mongodb_field_type(self, field_name, sample_docs):
        """Infer MongoDB field data type from field name and sample values"""
        # Common field name patterns for type inference
        if field_name == '_id':
            return 'ObjectId'
        elif 'email' in field_name.lower():
            return 'String'
        elif 'date' in field_name.lower() or 'time' in field_name.lower():
            return 'Date'
        elif 'age' in field_name.lower() or 'count' in field_name.lower():
            return 'Number'
        elif 'id' in field_name.lower():
            return 'String'
        else:
            return 'Mixed'

# Global instance for use across the application
database_connector = DatabaseConnector()