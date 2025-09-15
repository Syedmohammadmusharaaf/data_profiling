"""
Database Schema Extraction Module (db_fetch.py)
===============================================

This module provides comprehensive database schema extraction capabilities for the PII/PHI Scanner.
It supports extracting table and column metadata from multiple sources:

**Supported Data Sources:**
1. **Database Connections:**
   - Microsoft SQL Server (via pyodbc)
   - MySQL (via mysql-connector-python)
   - Oracle Database (via oracledb)

2. **File Formats:**
   - DDL/SQL files (.ddl, .sql) - SQL CREATE TABLE statements
   - CSV files - Structured column metadata
   - JSON files - Column metadata in JSON format
   - XML files - Hierarchical table/column definitions
   - Excel files (.xlsx) - Spreadsheet-based schema definitions

**Core Functions:**
- extract_schema_data(): Main entry point for schema extraction
- load_db_config(): Parse configuration files
- Various extract_from_*() functions for different data sources
- User interaction functions for table selection

**Data Format:**
All extraction functions return data in a standardized format:
List[Tuple] containing (schema_name, table_name, column_name, data_type)

**Configuration:**
Uses INI-style configuration files with sections for [database] or [schema_file]

Author: Based on user-provided code with enhancements
Version: 1.0 POC
"""

# Standard library imports
import csv                          # CSV file reading and writing
import os                          # Operating system interface
import json                         # JSON data handling
import configparser                 # INI configuration file parsing
from collections import defaultdict # Efficient dictionary with default values
import xml.etree.ElementTree as ET  # XML parsing capabilities

# Optional database connector imports
# These are wrapped in try/except blocks because they're optional dependencies
# The tool will work with file-based sources even if database connectors aren't installed

try:
    import mysql.connector           # MySQL database connectivity
except ImportError:
    mysql = None                    # Set to None if not available

try:
    import pyodbc                   # Microsoft SQL Server connectivity (also works with other ODBC sources)
except ImportError:
    pyodbc = None                   # Set to None if not available

try:
    import oracledb                 # Oracle database connectivity
except ImportError:
    oracledb = None                 # Set to None if not available

try:
    import openpyxl                 # Excel file (.xlsx) reading
except ImportError:
    openpyxl = None                 # Set to None if not available

# Configuration constants
CSV_FILE_PATH = "schema_metadata.csv"    # Default output file for database extractions
CONFIG_FILE_PATH = "db_config.ini"       # Default configuration file name

def load_db_config(config_file):
    """
    Parse configuration file to determine data source and connection details.
    
    This function reads an INI-style configuration file and determines whether to:
    1. Connect to a database directly, or
    2. Read schema from a file
    
    **Configuration File Format:**
    
    For file-based sources:
    ```ini
    [schema_file]
    path = /path/to/schema.ddl
    ```
    
    For database connections:
    ```ini
    [database]
    type = mssql|mysql|oracle
    host = server_address
    port = port_number
    user = username
    password = password
    database = database_name
    schema = schema_name (optional)
    ```
    
    Args:
        config_file (str): Path to the configuration file
    
    Returns:
        Dict: Configuration dictionary with connection details or file information
            For files: {'mode': 'file', 'file_type': 'ddl', 'path': '/path/to/file'}
            For databases: {'mode': 'db', 'type': 'mssql', 'host': '...', ...}
    
    Raises:
        ValueError: If configuration is invalid or missing required sections
    
    Examples:
        >>> config = load_db_config('config.ini')
        >>> if config['mode'] == 'file':
        ...     data = extract_from_file(config['file_type'], config['path'])
    """
    # Parse the INI configuration file
    config = configparser.ConfigParser()
    config.read(config_file)

    # Validate that we have at least one valid section
    if 'database' not in config and 'schema_file' not in config:
        raise ValueError("Either 'database' or 'schema_file' section must be present in config file.")

    # Handle file-based schema sources
    if 'schema_file' in config:
        file_conf = config['schema_file']
        file_path = file_conf.get('path')
        
        if not file_path:
            raise ValueError("Missing 'path' in 'schema_file' section.")

        # Auto-detect file type from extension for appropriate parser selection
        ext = os.path.splitext(file_path)[1].lower().strip('.')
        if ext not in ['csv', 'json', 'xml', 'ddl', 'sql','xlsx']:
            raise ValueError(f"Unsupported file extension '.{ext}' for schema file.")

        return {
            'mode': 'file',
            'file_type': ext,
            'path': file_path
        }

    # Handle database connections
    db_conf = config['database']
    db_type = db_conf.get('type')
    
    if db_type not in ['mysql', 'mssql', 'oracle']:
        raise ValueError("Unsupported database type. Choose mysql, mssql, or oracle.")

    return {
        'mode': 'db',
        'type': db_type,
        'host': db_conf.get('host'),
        'port': db_conf.get('port'),
        'user': db_conf.get('user'),
        'password': db_conf.get('password'),
        'database': db_conf.get('database'),
        'schema': db_conf.get('schema', ''),  # Optional schema name
    }

def extract_from_mysql(config):
    """
    Extract schema metadata from a MySQL database.
    
    Connects to MySQL database and retrieves table and column information
    using the INFORMATION_SCHEMA views. This provides standardized access
    to database metadata across different MySQL versions.
    
    Args:
        config (Dict): Database configuration containing:
            - host: MySQL server hostname/IP
            - port: MySQL server port (usually 3306)
            - user: Database username
            - password: Database password
            - database: Database name to analyze
    
    Returns:
        List[Tuple]: Schema data in format:
            [(schema_name, table_name, column_name, data_type), ...]
    
    Raises:
        ImportError: If mysql-connector-python is not installed
        mysql.connector.Error: For database connection or query errors
    
    Example:
        >>> config = {'host': 'localhost', 'user': 'root', 'password': 'pass', 'database': 'mydb'}
        >>> data = extract_from_mysql(config)
        >>> print(data[0])  # ('mydb', 'users', 'id', 'int(11)')
    """
    # Check if MySQL connector is available
    if not mysql:
        raise ImportError("mysql.connector not installed. Install with: pip install mysql-connector-python")

    # Establish database connection
    conn = mysql.connector.connect(
        host=config['host'], 
        user=config['user'],
        password=config['password'], 
        database=config['database'],
        port=int(config['port'])
    )
    cursor = conn.cursor()
    
    # Get list of all tables in the database
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s", (config['database'],))
    tables = [row[0] for row in cursor.fetchall()]

    # Extract column information for each table
    data = []
    for table in tables:
        # Use DESCRIBE to get column details (MySQL-specific command)
        cursor.execute(f"DESCRIBE `{table}`")
        for col in cursor.fetchall():
            # DESCRIBE returns: (Field, Type, Null, Key, Default, Extra)
            # We extract: column_name (col[0]) and data_type (col[1])
            data.append((config['database'], table, col[0], col[1]))
    
    # Clean up database connection
    cursor.close()
    conn.close()
    
    return data

def extract_from_mssql(config):
    """
    Extract schema metadata from a Microsoft SQL Server database.
    
    Connects to SQL Server using ODBC and retrieves table/column information
    using INFORMATION_SCHEMA views. Supports schema-level filtering for
    multi-schema databases.
    
    Args:
        config (Dict): Database configuration containing:
            - host: SQL Server hostname/IP (can include instance name)
            - port: SQL Server port (usually 1433)
            - user: Database username
            - password: Database password
            - database: Database name to analyze
            - schema: Optional schema name filter
    
    Returns:
        List[Tuple]: Schema data in format:
            [(schema_name, table_name, column_name, data_type), ...]
    
    Raises:
        ImportError: If pyodbc is not installed
        pyodbc.Error: For database connection or query errors
    
    Note:
        Requires "ODBC Driver 17 for SQL Server" or compatible driver
        If schema is not specified, user will be prompted interactively
    """
    # Check if pyodbc is available
    if not pyodbc:
        raise ImportError("pyodbc not installed. Install with: pip install pyodbc")

    # Build ODBC connection string
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={config['host']},{config['port']};"
        f"DATABASE={config['database']};"
        f"UID={config['user']};PWD={config['password']}"
    )
    
    # Establish database connection
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Handle schema selection - prompt user if not specified
    if not config.get('schema'):
        config['schema'] = ask_user_for_schema('mssql')

    # Build schema filter for SQL query
    schema_filter = f"AND TABLE_SCHEMA = '{config['schema']}'" if config['schema'] else ""

    # Get list of all base tables (excluding views and system tables)
    cursor.execute(f"""
        SELECT TABLE_NAME, TABLE_SCHEMA
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE' {schema_filter}
    """)
    tables = cursor.fetchall()

    # Extract column information for each table
    data = []
    for table_name, schema in tables:
        # Get column details using INFORMATION_SCHEMA.COLUMNS
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{schema}'
        """)
        for col in cursor.fetchall():
            # Extract: column_name (col[0]) and data_type (col[1])
            data.append((schema, table_name, col[0], col[1]))
    
    # Clean up database connection
    cursor.close()
    conn.close()
    
    return data

def extract_from_oracle(config):
    """
    Extract schema metadata from an Oracle database.
    
    Connects to Oracle database and retrieves table/column information
    using Oracle's system views (ALL_TABLES, ALL_TAB_COLUMNS).
    
    Args:
        config (Dict): Database configuration containing:
            - host: Oracle server hostname/IP
            - port: Oracle server port (usually 1521)
            - user: Database username
            - password: Database password
            - database: Service name or SID
            - schema: Optional schema name (defaults to username)
    
    Returns:
        List[Tuple]: Schema data in format:
            [(schema_name, table_name, column_name, data_type), ...]
    
    Raises:
        ImportError: If oracledb is not installed
        oracledb.Error: For database connection or query errors
    
    Note:
        Oracle schema names are case-sensitive and typically uppercase
        If schema is not specified, uses username as default
    """
    # Check if Oracle connector is available
    if not oracledb:
        raise ImportError("oracledb not installed. Install with: pip install oracledb")

    # Create Oracle DSN (Data Source Name)
    dsn = oracledb.makedsn(
        config['host'], 
        int(config['port']), 
        service_name=config['database']
    )
    
    # Establish database connection
    conn = oracledb.connect(
        user=config['user'], 
        password=config['password'], 
        dsn=dsn
    )
    cursor = conn.cursor()

    # Handle schema selection - Oracle schemas are typically uppercase
    if not config.get('schema'):
        user_default = config['user'].upper()
        schema_input = ask_user_for_schema('oracle')
        config['schema'] = schema_input if schema_input else user_default

    schema = config['schema'].upper()  # Ensure uppercase for Oracle

    # Get list of all tables owned by the schema
    cursor.execute(f"SELECT table_name FROM all_tables WHERE owner = '{schema}'")
    tables = [row[0] for row in cursor.fetchall()]

    # Extract column information for each table
    data = []
    for table in tables:
        # Get column details using ALL_TAB_COLUMNS view
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM all_tab_columns 
            WHERE table_name = '{table}' AND owner = '{schema}'
        """)
        for col in cursor.fetchall():
            # Extract: column_name (col[0]) and data_type (col[1])
            data.append((schema, table, col[0], col[1]))
    
    # Clean up database connection
    cursor.close()
    conn.close()
    
    return data

def extract_from_file(file_type, path):
    """
    Extract schema metadata from various file formats.
    
    This function serves as a universal file parser that can handle multiple
    formats commonly used for schema documentation and data exchange.
    Each format is parsed differently but returns the same standardized structure.
    
    **Supported Formats:**
    
    1. **CSV Files:** Column metadata in tabular format
       Expected columns: schema_name, table_name, column_name, data_type
    
    2. **JSON Files:** Structured metadata as JSON objects
       Expected format: [{"schema_name": "...", "table_name": "...", ...}, ...]
    
    3. **XML Files:** Hierarchical table/column definitions
       Expected structure: <Table name="..." schema="..."><Column name="..." type="..."/></Table>
    
    4. **DDL/SQL Files:** SQL CREATE TABLE statements
       Parses CREATE TABLE statements to extract column definitions
    
    5. **Excel Files (.xlsx):** Spreadsheet-based schema definitions
       Expected columns: schema_name, table_name, column_name, data_type
    
    Args:
        file_type (str): Type of file to parse ('csv', 'json', 'xml', 'ddl', 'sql', 'xlsx')
        path (str): Path to the file to be parsed
    
    Returns:
        List[Tuple]: Schema data in standardized format:
            [(schema_name, table_name, column_name, data_type), ...]
    
    Raises:
        ImportError: If required library is not installed (e.g., openpyxl for Excel)
        ValueError: If file format is not supported or file structure is invalid
        FileNotFoundError: If specified file path doesn't exist
        
    Examples:
        >>> # Parse a DDL file
        >>> data = extract_from_file('ddl', 'schema.sql')
        >>> print(data[0])  # ('dbo', 'users', 'id', 'INT')
        
        >>> # Parse a CSV file
        >>> data = extract_from_file('csv', 'metadata.csv')
    """
    print(f"📁 Parsing {file_type.upper()} file: {path}")
    
    # Initialize empty data container
    data = []

    if file_type.lower() == "csv":
        """
        Parse CSV files with column metadata.
        Expected format: schema_name,table_name,column_name,data_type
        """
        print("📊 Processing CSV format...")
        
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate that required columns exist
            required_columns = ["table_name", "column_name", "data_type"]
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"CSV file missing required columns: {required_columns}")
            
            for row_num, row in enumerate(reader, 2):  # Start at 2 since header is row 1
                try:
                    # Extract data with fallback for missing schema
                    schema_name = row.get("schema_name", "")
                    table_name = row["table_name"]
                    column_name = row["column_name"]
                    data_type = row["data_type"]
                    
                    if not all([table_name, column_name, data_type]):
                        print(f"⚠️ Skipping row {row_num}: missing required data")
                        continue
                        
                    data.append((schema_name, table_name, column_name, data_type))
                    
                except KeyError as e:
                    print(f"⚠️ Row {row_num}: Missing column {e}")
                    continue

    elif file_type.lower() == "json":
        """
        Parse JSON files with structured metadata.
        Expected format: [{"schema_name": "...", "table_name": "...", ...}, ...]
        """
        print("🔧 Processing JSON format...")
        
        with open(path, encoding='utf-8') as f:
            json_data = json.load(f)
            
        # Validate that we have a list of objects
        if not isinstance(json_data, list):
            raise ValueError("JSON file must contain an array of column objects")
            
        for item_num, entry in enumerate(json_data):
            try:
                # Extract required fields with validation
                if not isinstance(entry, dict):
                    print(f"⚠️ Skipping item {item_num}: not a valid object")
                    continue
                    
                schema_name = entry.get("schema_name", "")
                table_name = entry["table_name"]
                column_name = entry["column_name"]
                data_type = entry["data_type"]
                
                data.append((schema_name, table_name, column_name, data_type))
                
            except KeyError as e:
                print(f"⚠️ Item {item_num}: Missing required field {e}")
                continue

    elif file_type.lower() == "xml":
        """
        Parse XML files with hierarchical table/column structure.
        Expected format: <Table name="..." schema="..."><Column name="..." type="..."/></Table>
        """
        print("🌳 Processing XML format...")
        
        tree = ET.parse(path)
        root = tree.getroot()
        
        # Find all table elements
        for table in root.findall('Table'):
            schema = table.get('schema', '')  # Optional schema attribute
            table_name = table.get('name')
            
            if not table_name:
                print("⚠️ Skipping table without name attribute")
                continue
            
            # Find all column elements within this table
            for column in table.findall('Column'):
                col_name = column.get('name')
                data_type = column.get('type')
                
                if not all([col_name, data_type]):
                    print(f"⚠️ Skipping column in {table_name}: missing name or type")
                    continue
                    
                data.append((schema, table_name, col_name, data_type))

    elif file_type.lower() in ["ddl", "sql"]:
        """
        Parse DDL/SQL files containing CREATE TABLE statements.
        Uses regular expressions to extract table and column definitions.
        """
        print("🔨 Processing DDL/SQL format...")
        
        with open(path, 'r', encoding='utf-8') as f:
            ddl_text = f.read()
            
        import re
        
        # Regular expression to match CREATE TABLE statements
        # Captures: schema.table and column definitions
        table_pattern = r'CREATE\s+TABLE\s+(\w+)\.(\w+)\s*\((.*?)\);'
        table_blocks = re.findall(table_pattern, ddl_text, re.DOTALL | re.IGNORECASE)
        
        print(f"📋 Found {len(table_blocks)} CREATE TABLE statements")
        
        for schema, table, cols_text in table_blocks:
            print(f"   Processing table: {schema}.{table}")
            
            # Parse individual column definitions
            for line in cols_text.strip().splitlines():
                line = line.strip().strip(',')
                
                # Skip empty lines, comments, and constraint definitions
                if (not line or 
                    line.startswith('--') or 
                    line.startswith('/*') or
                    line.lower().startswith(('primary', 'foreign', 'constraint', 'index', 'key'))):
                    continue
                
                # Remove inline comments
                if '--' in line:
                    line = line[:line.find('--')].strip()
                
                # Extract column name and data type using regex
                # Matches patterns like: column_name DATA_TYPE[(size)] [constraints]
                column_pattern = r'(\w+)\s+([\w\(\)]+)'
                match = re.match(column_pattern, line)
                
                if match:
                    col_name, data_type = match.groups()
                    data.append((schema, table, col_name, data_type))
                else:
                    print(f"⚠️ Could not parse column definition: {line}")

    elif file_type.lower() == "xlsx":
        """
        Parse Excel (.xlsx) files with column metadata.
        Expected columns: schema_name, table_name, column_name, data_type
        """
        print("📗 Processing Excel format...")
        
        # Check if openpyxl is available
        if not openpyxl:
            raise ImportError("openpyxl is not installed. Install with: pip install openpyxl")

        # Load the Excel workbook
        wb = openpyxl.load_workbook(path)
        sheet = wb.active  # Use the active sheet
        
        # Get header row to identify columns
        headers = [cell.value for cell in sheet[1]]  # First row contains headers
        
        # Validate required headers
        required_headers = ["table_name", "column_name", "data_type"]
        missing_headers = [h for h in required_headers if h not in headers]
        if missing_headers:
            raise ValueError(f"Excel file missing required headers: {missing_headers}")

        # Create index mapping for efficient column access
        idx_map = {h: headers.index(h) for h in required_headers}
        schema_idx = headers.index("schema_name") if "schema_name" in headers else None

        # Process data rows (skip header row)
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
            try:
                # Handle potential None values in cells
                if not row or all(cell is None for cell in row):
                    continue  # Skip completely empty rows
                
                # Extract required data
                table_name = row[idx_map["table_name"]]
                column_name = row[idx_map["column_name"]]
                data_type = row[idx_map["data_type"]]
                schema_name = row[schema_idx] if schema_idx is not None else ""
                
                # Validate required fields
                if not all([table_name, column_name, data_type]):
                    print(f"⚠️ Row {row_num}: Missing required data")
                    continue
                
                # Convert to string and clean up
                schema_name = str(schema_name) if schema_name else ""
                table_name = str(table_name)
                column_name = str(column_name)
                data_type = str(data_type)
                
                data.append((schema_name, table_name, column_name, data_type))
                
            except (IndexError, TypeError) as e:
                print(f"⚠️ Row {row_num}: Error processing data - {e}")
                continue

    else:
        # Unsupported file type
        raise ValueError(f"Unsupported file type: {file_type}. Supported types: csv, json, xml, ddl, sql, xlsx")

    print(f"✅ Successfully extracted {len(data)} column records from {file_type.upper()} file")
    
    # Show sample of extracted data for verification
    if data:
        print("📊 Sample extracted data:")
        for i, (schema, table, column, dtype) in enumerate(data[:3]):
            schema_display = schema if schema else "(default)"
            print(f"   {i+1}. {schema_display}.{table}.{column} ({dtype})")
        
        if len(data) > 3:
            print(f"   ... and {len(data) - 3} more records")
    
    return data

def write_schema_to_csv(data):
    with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["schema_name", "table_name", "column_name", "data_type"])
        writer.writerows(data)
    print(f"✅ Schema metadata saved to '{CSV_FILE_PATH}'.")

def get_all_tables(schema_data):
    return sorted(set((schema, table) for schema, table, _, _ in schema_data))

def filter_tables(data, selected_tables):
    return [row for row in data if (row[0], row[1]) in selected_tables]

def ask_user_for_schema(db_type):
    print(f"\n⚠️ Schema is missing in the config for {db_type.upper()} database.")
    while True:
        response = input("Would you like to provide a schema name? (yes/no): ").strip().lower()
        if response == 'yes':
            schema = input("Please enter the schema name: ").strip()
            if schema:
                return schema
            else:
                print("❌ Schema name cannot be empty. Try again.")
        elif response == 'no':
            print("ℹ️ Proceeding without schema filter. Fetching all available tables.")
            return None
        else:
            print("❌ Invalid input. Please type 'yes' or 'no'.")

def get_user_table_selection(tables):
    while True:
        print("\n📋 Available Tables:")
        for idx, (schema, table) in enumerate(tables, 1):
            print(f"{idx}.{table}")

        print("\n🔧 Selection Mode:")
        print("1. Include (only selected tables will be used)")
        print("2. Exclude (all except selected tables will be used)")
        print("3. Use all tables")

        mode_input = input("Choose option (1 / 2 / 3): ").strip()

        # Reject anything that is not exactly "1", "2", or "3"
        if mode_input not in {"1", "2", "3"}:
            print("❌ Invalid selection. Please enter only one number: 1, 2, or 3.\n")
            continue

        # Use all tables without further filtering
        if mode_input == "3":
            return set(tables)

        # Prompt for table selection
        while True:
            table_input = input("Enter table numbers (comma-separated): ").strip()
            if not table_input:
                print("⚠️ No table numbers entered. Please try again.\n")
                continue

            try:
                parts = [part.strip() for part in table_input.split(',') if part.strip()]
                indices = []

                for part in parts:
                    if not part.isdigit():
                        raise ValueError(f"'{part}' is not a valid number.")
                    idx = int(part)
                    if not (1 <= idx <= len(tables)):
                        raise IndexError(f"Table number {idx} is out of range.")
                    indices.append(idx)

                if not indices:
                    print("⚠️ No valid table numbers found. Try again.\n")
                    continue

                selected = set([tables[i - 1] for i in indices])
                return selected if mode_input == "1" else set(tables) - selected

            except (ValueError, IndexError) as e:
                print(f"❌ {e}\n")

def extract_schema_data(config_file=CONFIG_FILE_PATH):
    """
    Extract schema data from database or file based on configuration.
    Returns structured data for further processing.
    """
    try:
        config = load_db_config(config_file)

        if config['mode'] == 'db':
            if config['type'] == 'mysql':
                schema_data = extract_from_mysql(config)
            elif config['type'] == 'mssql':
                schema_data = extract_from_mssql(config)
            elif config['type'] == 'oracle':
                schema_data = extract_from_oracle(config)
            else:
                raise ValueError("Unsupported DB type.")

            write_schema_to_csv(schema_data)  # Only write CSV if extracted from DB

        elif config['mode'] == 'file':
            schema_data = extract_from_file(config['file_type'], config['path'])

            if not schema_data:
                print("Provided schema file is empty. Please provide a file with valid schema data.")
                return []

        else:
            raise ValueError("Invalid mode in config.")

        return schema_data

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    """
    Main function for standalone execution of DBFetch functionality.
    """
    try:
        config = load_db_config(CONFIG_FILE_PATH)

        if config['mode'] == 'db':
            if config['type'] == 'mysql':
                schema_data = extract_from_mysql(config)
            elif config['type'] == 'mssql':
                schema_data = extract_from_mssql(config)
            elif config['type'] == 'oracle':
                schema_data = extract_from_oracle(config)
            else:
                raise ValueError("Unsupported DB type.")

            write_schema_to_csv(schema_data)  # Only write CSV if extracted from DB

        elif config['mode'] == 'file':
            schema_data = extract_from_file(config['file_type'], config['path'])

            if not schema_data:
                print("Provided schema file is empty. Please provide a file with valid schema data.")
                return

        else:
            raise ValueError("Invalid mode in config.")

        all_tables = get_all_tables(schema_data)
        selected_tables = get_user_table_selection(all_tables)
        filtered = filter_tables(schema_data, selected_tables)

        print("\n📦 Final Table Info:")

        from collections import defaultdict
        table_columns = defaultdict(list)

        for schema, table, column, _ in filtered:
            table_columns[(schema, table)].append(column)

        for (schema, table), columns in table_columns.items():
            print(f"\nTable Name: {table}")
            for idx, col in enumerate(columns, 1):
                print(f"  {idx}) {col}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()