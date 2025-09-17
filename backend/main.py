#!/usr/bin/env python3
"""
PII Scanner Enterprise Backend - FastAPI Server
===============================================

This is the main FastAPI application server for the PII Scanner Enterprise system.
It provides RESTful APIs for the React frontend to interact with the core PII/PHI 
scanning engine.

Key Features:
- Schema file upload and parsing
- Table/column extraction from DDL files
- PII/PHI classification using hybrid AI + local patterns
- Regulatory compliance (HIPAA, GDPR, CCPA) analysis
- Comprehensive report generation
- Session-based workflow management

Architecture:
- FastAPI for high-performance async API server
- MongoDB for session and configuration storage
- PII Scanner core engine for analysis logic
- Comprehensive logging and error handling

Author: PII Scanner Team
Version: 2.0.0
Last Updated: 2024-12-29
"""

# Standard library imports
import os
import sys
import asyncio
import uuid
import json
import time
import io
import tempfile
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directory to Python path for imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Third-party imports
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

# PII Scanner core imports
from pii_scanner_poc.core.pii_scanner_facade import PIIScannerFacade
from pii_scanner_poc.core.hybrid_classification_orchestrator import HybridClassificationOrchestrator
from pii_scanner_poc.services.database_service import DatabaseService
from pii_scanner_poc.services.database_connector import database_connector, DatabaseConnection
from pii_scanner_poc.models.data_models import Regulation
from pii_scanner_poc.utils.logging_config import main_logger

# =============================================================================
# SERVICE INITIALIZATION
# =============================================================================

# Initialize core services used throughout the application
database_service = DatabaseService()

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_file_logging():
    """
    Configure comprehensive file-based logging for debugging and monitoring.
    
    Creates two log handlers:
    - Debug handler: Detailed debug information with function names and line numbers
    - Activity handler: High-level activity logging for monitoring
    
    Returns:
        logging.Logger: Configured debug logger instance
    """
    try:
        # Create debug logger with appropriate level
        debug_logger = logging.getLogger('pii_scanner_debug')
        debug_logger.setLevel(logging.DEBUG)
        
        # Setup file handlers for different log types
        debug_handler = logging.FileHandler('/tmp/pii_scanner_debug.log')
        debug_handler.setLevel(logging.DEBUG)
        
        activity_handler = logging.FileHandler('/tmp/pii_scanner_activity.log')
        activity_handler.setLevel(logging.INFO)
        
        # Create detailed formatters for better log readability
        debug_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
        activity_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Apply formatters to handlers
        debug_handler.setFormatter(debug_formatter)
        activity_handler.setFormatter(activity_formatter)
        
        # Add handlers only if not already configured (avoid duplicates)
        if not debug_logger.handlers:
            debug_logger.addHandler(debug_handler)
            debug_logger.addHandler(activity_handler)
        
        return debug_logger
    except Exception as e:
        main_logger.error(f"Failed to setup file logging: {e}")
        return main_logger

# Initialize file logging system
debug_logger = setup_file_logging()

def log_activity(level: str, message: str, extra_data: Dict = None, session_id: str = None):
    """
    Centralized logging function for structured activity tracking.
    
    This function provides comprehensive logging that writes to multiple destinations:
    - Console output via main_logger
    - File output via debug_logger  
    - Structured JSON logs for analysis
    
    Args:
        level (str): Log level (INFO, WARN, ERROR)
        message (str): Primary log message
        extra_data (Dict, optional): Additional structured data
        session_id (str, optional): Session identifier for tracking
    """
    timestamp = datetime.now().isoformat()
    
    # Create structured log entry for JSON logging
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message,
        "session_id": session_id,
        "data": extra_data or {}
    }
    
    # Format human-readable log message
    log_message = f"[{session_id or 'NO_SESSION'}] {message}"
    if extra_data:
        log_message += f" | Data: {json.dumps(extra_data, default=str)}"
    
    # Route to appropriate log levels
    if level == "ERROR":
        main_logger.error(log_message)
        debug_logger.error(log_message)
    elif level == "WARN":
        main_logger.warning(log_message)
        debug_logger.warning(log_message)
    else:  # INFO and other levels
        main_logger.info(log_message)
        debug_logger.info(log_message)
    
    # Write structured JSON log for programmatic analysis
    try:
        with open('/tmp/pii_scanner_activity.jsonl', 'a') as f:
            f.write(json.dumps(log_entry, default=str) + '\n')
    except Exception as e:
        main_logger.error(f"Failed to write structured activity log: {e}")

# Log application startup with version information
log_activity("INFO", "PII Scanner Backend starting up", {
    "version": "2.0.0",
    "debug_log_file": "/tmp/pii_scanner_debug.log",
    "activity_log_file": "/tmp/pii_scanner_activity.log",
    "structured_log_file": "/tmp/pii_scanner_activity.jsonl"
})

# =============================================================================
# DATA CONVERSION UTILITIES
# =============================================================================

def convert_scanner_result_to_frontend_format(scanner_result):
    """
    Convert enhanced scanner results to frontend-compatible format.
    
    Args:
        scanner_result (dict): Raw scanner results from PII analysis
        
    Returns:
        dict: Frontend-compatible results with field_analyses structure
    """
    try:
        main_logger.info(f"Converting scanner result with {len(scanner_result.get('detailed_results', {}))} detailed results")
        
        # Handle already converted format
        if isinstance(scanner_result, dict) and "findings" in scanner_result:
            return scanner_result
        
        # Extract findings from enhanced scanner report
        findings = []
        total_fields = 0
        pii_fields = 0
        high_risk = 0
        
        if isinstance(scanner_result, dict):
            # Check for detailed_results structure from enhanced scanner
            if "detailed_results" in scanner_result:
                main_logger.info("Found detailed_results in scanner result")
                
                for table_result in scanner_result["detailed_results"]:
                    if "detailed_columns" in table_result:
                        for column in table_result["detailed_columns"]:
                            # Extract field information
                            field_name = column.get("column_name", "")
                            table_name = table_result.get("table_name", "")
                            is_sensitive = column.get("is_sensitive", False)
                            confidence = column.get("confidence_score", 0.0)
                            pii_type = column.get("pii_type", "Other")
                            risk_level = column.get("sensitivity_level", "Low")
                            
                            # CRITICAL FIX: Extract applicable regulations from scanner results
                            applicable_regulations = column.get("applicable_regulations", [])
                            
                            # Convert pii_type if it's an enum
                            if hasattr(pii_type, 'value'):
                                pii_type = pii_type.value
                            
                            # Convert risk_level if it's an enum  
                            if hasattr(risk_level, 'value'):
                                risk_level = risk_level.value
                            
                            # Convert applicable_regulations if they are enums
                            if applicable_regulations:
                                regulation_strings = []
                                for reg in applicable_regulations:
                                    if hasattr(reg, 'value'):
                                        regulation_strings.append(reg.value)
                                    else:
                                        regulation_strings.append(str(reg))
                                applicable_regulations = regulation_strings
                            
                            # Only include sensitive fields or convert all based on is_sensitive
                            classification = "PII" if is_sensitive else "Non-PII"
                            
                            finding = {
                                "field_name": field_name,
                                "classification": classification,
                                "confidence": float(confidence) if confidence else 0.0,
                                "table_name": table_name,
                                "pii_type": pii_type,
                                "risk_level": risk_level.lower() if risk_level else "low",
                                "applicable_regulations": applicable_regulations  # Preserve actual regulations
                            }
                            findings.append(finding)
                            total_fields += 1
            
            # Check for analysis_summary to get totals
            elif "analysis_summary" in scanner_result:
                main_logger.info("Found analysis_summary in scanner result")
                summary = scanner_result["analysis_summary"]
                total_fields = summary.get("total_columns_analyzed", 0)
                
                # If we don't have detailed results, create summary findings
                if not findings and total_fields > 0:
                    sensitive_count = summary.get("total_sensitive_columns", 0)
                    findings.append({
                        "field_name": "Multiple fields detected",
                        "classification": "PII", 
                        "confidence": 0.85,
                        "table_name": "Multiple tables",
                        "pii_type": "Mixed",
                        "risk_level": "medium"
                    })
        
        # Handle object-based results (EnhancedFieldAnalysis objects)
        elif hasattr(scanner_result, 'field_analyses'):
            main_logger.info("Found field_analyses in scanner result")
            for analysis in scanner_result.field_analyses:
                # Extract applicable regulations 
                applicable_regulations = []
                if hasattr(analysis, 'applicable_regulations') and analysis.applicable_regulations:
                    for reg in analysis.applicable_regulations:
                        if hasattr(reg, 'value'):
                            applicable_regulations.append(reg.value)
                        else:
                            applicable_regulations.append(str(reg))
                
                finding = {
                    "field_name": analysis.field_name,
                    "classification": "PII" if analysis.is_sensitive else "Non-PII",
                    "confidence": analysis.confidence_score,
                    "table_name": analysis.table_name,
                    "pii_type": analysis.pii_type.value if hasattr(analysis.pii_type, 'value') else str(analysis.pii_type),
                    "risk_level": analysis.risk_level.value.lower() if hasattr(analysis.risk_level, 'value') else str(analysis.risk_level).lower(),
                    "applicable_regulations": applicable_regulations  # Preserve actual regulations
                }
                findings.append(finding)
                total_fields += 1
        
        # Calculate summary statistics
        pii_fields = len([f for f in findings if f["classification"] == "PII"])
        high_risk = len([f for f in findings if f.get("risk_level") == "high"])
        
        main_logger.info(f"Converted {len(findings)} findings, {pii_fields} PII fields, {high_risk} high risk")
        
        # Convert findings array to field_analyses object format expected by frontend
        field_analyses = {}
        for finding in findings:
            field_key = f"{finding['table_name']}.{finding['field_name']}"
            field_analyses[field_key] = {
                "field_name": finding["field_name"],
                "table_name": finding["table_name"],
                "confidence_score": finding["confidence"],
                "is_sensitive": finding["classification"] != "Non-PII",
                "pii_type": finding["pii_type"],
                "risk_level": finding["risk_level"].upper(),
                "applicable_regulations": finding.get("applicable_regulations", []) if finding["classification"] != "Non-PII" else [],
                "rationale": f"Classified as {finding['pii_type']} with {int(finding['confidence'] * 100)}% confidence"
            }
        
        return {
            "field_analyses": field_analyses,
            "summary": {
                "total_fields": total_fields or len(findings),
                "pii_fields": pii_fields,
                "high_risk": high_risk,
                "message": f"Analyzed {len(findings)} fields with {pii_fields} PII fields detected"
            },
            "status": "completed"
        }
        
    except Exception as e:
        main_logger.error(f"Error converting scanner result: {e}", exc_info=True)
        # Return fallback format with field_analyses structure
        return {
            "field_analyses": {},
            "summary": {"total_fields": 0, "pii_fields": 0, "high_risk": 0, "message": "Error in analysis"},
            "status": "error",
            "error": str(e)
        }

# =============================================================================
# API DATA MODELS - PYDANTIC SCHEMAS FOR REQUEST/RESPONSE VALIDATION
# =============================================================================

class SchemaUploadRequest(BaseModel):
    """
    Data model for schema file upload requests.
    
    Used by the /api/upload-schema endpoint to validate uploaded DDL files.
    Supports various schema formats including DDL, SQL, and structured text files.
    """
    file_content: str = Field(
        ..., 
        description="Raw content of the uploaded schema file",
        min_length=1,
        max_length=10485760  # 10MB limit
    )
    file_name: str = Field(
        ..., 
        description="Original filename with extension (e.g., 'schema.ddl')"
    )
    file_type: str = Field(
        default="ddl", 
        description="File format type - supported: ddl, sql, txt",
        pattern="^(ddl|sql|txt)$"
    )

class ScanTypeRequest(BaseModel):
    """
    Data model for scan configuration requests.
    
    Used by workflow step 2 to configure which tables and scan types to apply.
    Allows selective table scanning and custom field filtering.
    """
    tables: List[str] = Field(
        ..., 
        description="List of table names to include in the scan",
        min_items=1
    )
    scan_type: str = Field(
        ..., 
        description="Type of regulatory scan to perform",
        pattern="^(PII|HIPAA|GDPR|COMPREHENSIVE)$"
    )
    custom_fields: Optional[List[str]] = Field(
        default=[], 
        description="Additional custom field patterns to detect"
    )

class ClassificationRequest(BaseModel):
    """
    Data model for PII/PHI classification requests.
    
    Core request model for the /api/classify endpoint. Contains all necessary
    information to perform context-aware regulatory classification.
    """
    session_id: str = Field(
        ..., 
        description="Unique session identifier from schema upload",
        min_length=1
    )
    selected_fields: List[Dict] = Field(
        ..., 
        description="Array of field objects with table_name, column_name, data_type",
        min_items=1
    )
    regulations: List[str] = Field(
        ..., 
        description="Regulatory frameworks to apply - supported: HIPAA, GDPR, CCPA",
        min_items=1
    )

class DatabaseConnectionRequest(BaseModel):
    """
    Data model for live database connection requests.
    
    Enables direct connection to production databases for real-time schema analysis.
    Supports major database types with secure connection handling.
    """
    type: str = Field(
        ..., 
        description="Database engine type",
        pattern="^(mysql|postgresql|sqlserver|oracle|mongodb)$"
    )
    host: str = Field(
        ..., 
        description="Database server hostname or IP address"
    )
    port: str = Field(
        default="", 
        description="Database server port (auto-detected if empty)"
    )
    database: str = Field(
        ..., 
        description="Target database/schema name"
    )
    username: str = Field(
        default="", 
        description="Database authentication username"
    )
    password: str = Field(
        default="", 
        description="Database authentication password"
    )
    ssl: bool = Field(
        default=False, 
        description="Enable SSL/TLS encrypted connection"
    )
    additional_params: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Database-specific connection parameters"
    )

class ValidationRequest(BaseModel):
    """
    Data model for classification result validation and correction.
    
    Used by workflow step 4 to apply user corrections and generate final reports.
    Supports manual field reclassification and filtering.
    """
    session_id: str = Field(
        ..., 
        description="Session identifier for the classification to validate",
        min_length=1
    )
    changes: Optional[Dict] = Field(
        default={}, 
        description="User corrections: field_key -> new_classification_data"
    )
    pii_fields_only: Optional[List] = Field(
        default=None, 
        description="Filtered list of confirmed PII fields for final report"
    )


# =============================================================================
# APPLICATION STATE MANAGEMENT
# =============================================================================

class AppState:
    """
    Global application state manager for performance and session management.
    """
    def __init__(self):
        self.pii_scanner = None
        self.orchestrator = None
        self.classification_engine = None
        self.ai_service = None  # Add AI service to app state
        self.active_sessions = {}
        self.performance_cache = {}

app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application state"""
    try:
        # Initialize PII Scanner components with minimal configuration
        main_logger.info("Starting PII Scanner initialization...")
        app_state.pii_scanner = PIIScannerFacade()
        main_logger.info("PII Scanner facade initialized")
        
        # Initialize classification engine for direct classification
        from pii_scanner_poc.core.inhouse_classification_engine import InHouseClassificationEngine
        app_state.classification_engine = InHouseClassificationEngine()
        main_logger.info("Classification engine initialized")
        
        # Initialize AI service for hybrid AI + local patterns classification with proper config
        try:
            from pii_scanner_poc.services.enhanced_ai_service import EnhancedAIService
            from pii_scanner_poc.core.configuration import ConfigurationManager
            
            # Create configuration manager and load config from .env file
            config_manager = ConfigurationManager()
            config = config_manager.load_configuration(
                env_file="C:/Users/syed_musharaaf/Downloads/dataprofiling-temp19-fixing-main/dataprofiling-temp19-fixing-main/pii_scanner_poc/.env"
            )
            
            app_state.ai_service = EnhancedAIService(config)
            main_logger.info("AI service initialized for hybrid classification with proper config")
        except Exception as ai_error:
            main_logger.warning(f"AI service initialization failed, will use local patterns only: {ai_error}")
            app_state.ai_service = None
        
        # Skip orchestrator initialization for now to avoid hanging
        # app_state.orchestrator = HybridClassificationOrchestrator()
        main_logger.info("PII Scanner Enterprise Backend initialized")
        yield
    except Exception as e:
        main_logger.error(f"Failed to initialize backend: {e}")
        raise
    finally:
        # Cleanup
        app_state.active_sessions.clear()
        main_logger.info("PII Scanner Enterprise Backend shutdown")

app = FastAPI(
    title="PII Scanner Enterprise API",
    description="High-performance PII/PHI scanning with React frontend",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware for performance and security
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002", 
        "http://localhost:3003",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "https://pii-dashboard.preview.emergentagent.com",
        "http://robust-scanner.preview.emergentagent.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# HEALTH CHECK AND SYSTEM STATUS
# =============================================================================

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring system status.
    
    Returns:
        dict: System health status and component availability
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "components": {
            "pii_scanner": app_state.pii_scanner is not None,
            "orchestrator": app_state.orchestrator is not None,
            "classification_engine": app_state.classification_engine is not None
        }
    }


# =============================================================================
# DATA PREPARATION ENDPOINTS
# =============================================================================

@app.post("/api/upload-schema")
async def upload_schema(
    file: UploadFile = File(...),
    file_type: str = Form("ddl"),
    regulation: str = Form("COMPREHENSIVE")
):
    """Step 1: Upload and validate schema file"""
    try:
        # Validate file type
        allowed_types = ['ddl', 'sql', 'json', 'csv', 'xlsx']
        if file_type.lower() not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Create session
        session_id = str(uuid.uuid4())
        
        # Store in session
        app_state.active_sessions[session_id] = {
            "file_content": content_str,
            "file_name": file.filename,
            "original_filename": file.filename,
            "file_type": file_type,
            "created_at": datetime.now().isoformat(),
            "status": "uploaded",
            "regulations": [regulation] if regulation else ["COMPREHENSIVE"]
        }
        
        return {
            "session_id": session_id,
            "file_name": file.filename,
            "file_size": len(content),
            "file_type": file_type,
            "status": "success",
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        main_logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract-schema/{session_id}")
async def extract_schema(session_id: str):
    """Step 2: Extract schema and get available tables"""
    try:
        if session_id not in app_state.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = app_state.active_sessions[session_id]
        
        # Extract schema using database service
        schema_data = database_service.load_schema_from_content(
            session["file_content"], 
            session["file_type"]
        )
        
        # Get table information
        tables = {}
        for column in schema_data:
            table_name = column.table_name
            if table_name not in tables:
                tables[table_name] = []
            tables[table_name].append({
                "column_name": column.column_name,
                "data_type": column.data_type,
                "schema_name": column.schema_name
            })
        
        # Update session
        session["schema_data"] = schema_data
        session["tables"] = tables
        session["status"] = "extracted"
        
        return {
            "session_id": session_id,
            "tables": tables,
            "total_tables": len(tables),
            "total_columns": len(schema_data),
            "status": "success"
        }
        
    except Exception as e:
        main_logger.error(f"Schema extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 2. Profiling Configuration Endpoints
@app.post("/api/configure-scan")
async def configure_scan(request: ScanTypeRequest):
    """Step 3-6: Configure scan type and display relevant fields"""
    try:
        # Map scan types to regulations
        regulation_map = {
            "PII": ["GDPR"],
            "HIPAA": ["HIPAA"], 
            "GDPR": ["GDPR"],
            "ALL": ["GDPR", "HIPAA", "CCPA"]
        }
        
        regulations = regulation_map.get(request.scan_type, ["GDPR"])
        
        # Get predefined patterns for the regulation
        patterns = [
            "ssn", "social_security", "email", "phone", "credit_card",
            "medical_record", "patient_id", "diagnosis", "prescription",
            "first_name", "last_name", "address", "date_of_birth"
        ]
        
        return {
            "scan_type": request.scan_type,
            "regulations": regulations,
            "predefined_patterns": patterns[:20],  # Limit for UI
            "custom_fields": request.custom_fields,
            "recommended_fields": [
                "ssn", "social_security", "email", "phone", "credit_card",
                "medical_record", "patient_id", "diagnosis", "prescription"
            ],
            "status": "configured"
        }
        
    except Exception as e:
        main_logger.error(f"Scan configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PII CLASSIFICATION AND ANALYSIS ENDPOINTS
# =============================================================================

@app.post("/api/classify")
async def classify_fields(request: ClassificationRequest):
    """
    Step 7-10: Perform PII/PHI classification using hybrid analysis.
    
    Args:
        request (ClassificationRequest): Classification request with fields and regulations
        
    Returns:
        dict: Classification results with field analyses and summary
    """
    session_id = request.session_id
    log_activity("INFO", "Starting classification request", {
        "session_id": session_id,
        "regulations": request.regulations,
        "selected_fields_count": len(request.selected_fields) if request.selected_fields else 0,
        "enable_ai": getattr(request, 'enable_ai', True)
    }, session_id)

    try:
        if session_id not in app_state.active_sessions:
            log_activity("ERROR", "Session not found", {"session_id": session_id}, session_id)
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = app_state.active_sessions[session_id]
        log_activity("INFO", "Found session", {
            "session_keys": list(session.keys()),
            "file_content_length": len(session.get("file_content", ""))
        }, session_id)
        
        # Perform hybrid classification
        regulations = [Regulation(reg) for reg in request.regulations]
        log_activity("INFO", "Processing regulations", {
            "regulation_count": len(regulations),
            "regulation_names": [reg.value for reg in regulations]
        }, session_id)
        
        if app_state.pii_scanner:
            # Create a temporary file with the schema content
            import tempfile
            import os
            
            try:
                # Get the original file content from session
                file_content = session.get("file_content", "")
                log_activity("INFO", "Retrieved file content", {
                    "content_length": len(file_content),
                    "has_content": bool(file_content)
                }, session_id)
                
                if not file_content:
                    log_activity("ERROR", "No file content found in session", {}, session_id)
                    raise HTTPException(status_code=400, detail="No file content found in session")
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ddl', delete=False) as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name
                
                log_activity("INFO", "Created temporary file", {
                    "temp_file_path": temp_file_path,
                    "file_size": len(file_content)
                }, session_id)
                
                # Extract table names from selected fields
                selected_table_names = None
                if request.selected_fields:
                    selected_table_names = list(set(field.get("table_name") for field in request.selected_fields if field.get("table_name")))
                    log_activity("INFO", "Extracted table names", {
                        "selected_tables": selected_table_names,
                        "total_fields": len(request.selected_fields)
                    }, session_id)
                
                # Use the facade for analysis with timeout handling
                try:
                    log_activity("INFO", "Starting scanner analysis", {
                        "temp_file": temp_file_path,
                        "selected_tables": selected_table_names,
                        "regulations": request.regulations
                    }, session_id)
                    
                    analysis_start_time = time.time()
                    scanner_result = await app_state.pii_scanner.analyze_schema_file(
                        schema_file_path=temp_file_path,
                        regulations=request.regulations,
                        selected_tables=selected_table_names,
                        enable_llm=False  # Disable LLM to prevent timeouts
                    )
                    analysis_time = time.time() - analysis_start_time
                    
                    log_activity("INFO", "Scanner analysis completed successfully", {
                        "analysis_time": f"{analysis_time:.2f}s",
                        "result_type": type(scanner_result).__name__,
                        "result_keys": list(scanner_result.keys()) if isinstance(scanner_result, dict) else "not_dict",
                        "field_analyses_count": len(scanner_result.get("field_analyses", {})) if isinstance(scanner_result, dict) else 0
                    }, session_id)
                    
                    # Convert enhanced results to frontend format
                    result = convert_scanner_result_to_frontend_format(scanner_result)
                    
                    # Log detailed results
                    field_analyses = result.get("field_analyses", {})
                    sensitive_fields = {k: v for k, v in field_analyses.items() if v.get("is_sensitive", False)}
                    
                    log_activity("INFO", "Classification results processed", {
                        "total_fields_analyzed": len(field_analyses),
                        "sensitive_fields_found": len(sensitive_fields),
                        "pii_fields": len([f for f in sensitive_fields.values() if not any(term in f.get("pii_type", "").lower() for term in ["medical", "health", "patient"])]),
                        "phi_fields": len([f for f in sensitive_fields.values() if any(term in f.get("pii_type", "").lower() for term in ["medical", "health", "patient"])]),
                        "summary": result.get("summary", {})
                    }, session_id)
                    
                except Exception as scanner_error:
                    log_activity("ERROR", "Scanner analysis failed, attempting direct classification fallback", {
                        "error": str(scanner_error),
                        "error_type": type(scanner_error).__name__
                    }, session_id)
                    
                    # Instead of fallback, let's try direct classification
                    log_activity("INFO", "Attempting direct field classification as fallback", {}, session_id)
                    try:
                        # Use the properly initialized classification engine from app_state
                        classification_engine = app_state.classification_engine
                        if not classification_engine:
                            # Fallback to creating a new engine if not initialized
                            from pii_scanner_poc.core.inhouse_classification_engine import InHouseClassificationEngine
                            classification_engine = InHouseClassificationEngine()
                        
                        # Create field analyses directly from selected fields
                        field_analyses = {}
                        total_fields = len(request.selected_fields)
                        pii_count = 0
                        
                        log_activity("INFO", "Starting direct classification of fields", {
                            "total_fields_to_classify": total_fields
                        }, session_id)
                        
                        for field_data in request.selected_fields:
                            field_name = field_data.get("column_name", "")
                            table_name = field_data.get("table_name", "")
                            
                            # Try classification with each regulation using new Hybrid AI + Local Patterns
                            classification_result = None
                            for regulation in regulations:
                                try:
                                    # Use the new hybrid AI + local patterns classification method
                                    classification_result = classification_engine.classify_field_hybrid_ai(
                                        field_name, regulation=regulation, table_context=table_name, ai_service=app_state.ai_service
                                    )
                                    if classification_result and classification_result[1] > 0.5:  # confidence > 0.5
                                        break
                                except Exception as class_error:
                                    log_activity("WARN", f"Hybrid classification failed for field {field_name}, falling back to local", {
                                        "field_name": field_name,
                                        "regulation": regulation.value,
                                        "error": str(class_error)
                                    }, session_id)
                                    
                                    # Fallback to local patterns only
                                    try:
                                        # Use the hybrid method with ai_service=None for local-only classification
                                        classification_result = classification_engine.classify_field_hybrid_ai(
                                            field_name, regulation=regulation, table_context=table_name, ai_service=None
                                        )
                                        if classification_result and classification_result[1] > 0.5:
                                            break
                                    except Exception as fallback_error:
                                        log_activity("WARN", f"Local classification also failed for field {field_name}", {
                                            "field_name": field_name,
                                            "regulation": regulation.value,
                                            "error": str(fallback_error)
                                        }, session_id)
                                        continue
                            
                            # Create field analysis
                            field_key = f"{table_name}.{field_name}"
                            is_sensitive = False
                            confidence = 0.0
                            pii_type = "OTHER"
                            risk_level = "LOW"
                            
                            if classification_result:
                                pattern, confidence = classification_result
                                if confidence > 0.5:
                                    is_sensitive = True
                                    pii_count += 1
                                    pii_type = str(pattern.pii_type.value) if hasattr(pattern.pii_type, 'value') else str(pattern.pii_type)
                                    risk_level = str(pattern.risk_level.value) if hasattr(pattern.risk_level, 'value') else str(pattern.risk_level)
                            
                            field_analyses[field_key] = {
                                "field_name": field_name,
                                "table_name": table_name,
                                "confidence_score": confidence,
                                "is_sensitive": is_sensitive,
                                "pii_type": pii_type,
                                "risk_level": risk_level.upper(),
                                "applicable_regulations": [reg.value for reg in regulations] if is_sensitive else [],
                                "rationale": f"Direct classification: {pii_type} with {int(confidence * 100)}% confidence"
                            }
                        
                        # Create fallback result
                        result = {
                            "field_analyses": field_analyses,
                            "summary": {
                                "total_fields": total_fields,
                                "pii_fields": pii_count,
                                "high_risk": len([f for f in field_analyses.values() if f.get('risk_level') == 'HIGH']),
                                "message": f"Direct classification: {pii_count} PII fields found out of {total_fields} total fields"
                            },
                            "status": "completed"
                        }
                        
                        log_activity("INFO", "Direct classification completed successfully", {
                            "total_fields": total_fields,
                            "pii_fields": pii_count,
                            "high_risk_fields": len([f for f in field_analyses.values() if f.get('risk_level') == 'HIGH']),
                            "success": True
                        }, session_id)
                        
                    except Exception as fallback_error:
                        log_activity("ERROR", "Fallback classification also failed", {
                            "fallback_error": str(fallback_error),
                            "error_type": type(fallback_error).__name__
                        }, session_id)
                        # Return minimal error result
                        result = {
                            "field_analyses": {},
                            "summary": {"total_fields": 0, "pii_fields": 0, "high_risk": 0, "message": "Classification failed"},
                            "status": "error",
                            "error": f"Classification failed: {str(fallback_error)}"
                        }
                
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                    log_activity("INFO", "Cleaned up temporary file", {"temp_file": temp_file_path}, session_id)
                except Exception as cleanup_error:
                    log_activity("WARN", "Failed to cleanup temp file", {
                        "temp_file": temp_file_path,
                        "error": str(cleanup_error)
                    }, session_id)
                
            except Exception as e:
                log_activity("ERROR", "Scanner analysis error", {
                    "error": str(e),
                    "error_type": type(e).__name__
                }, session_id)
                raise HTTPException(status_code=500, detail=f"Scanner analysis failed: {str(e)}")
            
            # Update session with results
            session["classification_results"] = result
            session["status"] = "classified"
            
            log_activity("INFO", "Classification completed for session", {
                "session_id": session_id,
                "status": "success",
                "results_summary": result.get("summary", {})
            }, session_id)
            
            return {
                "session_id": session_id,
                "results": result,
                "status": "success"
            }
        else:
            log_activity("ERROR", "PII Scanner not initialized", {}, session_id)
            raise HTTPException(status_code=500, detail="PII Scanner not initialized")
            
    except Exception as e:
        log_activity("ERROR", "Classification error occurred", {
            "error": str(e),
            "error_type": type(e).__name__
        }, session_id)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# VALIDATION AND COMPLETION ENDPOINTS
# =============================================================================

@app.post("/api/validate-results")
async def validate_results(request: ValidationRequest):
    """
    Step 11: User review and validation of results.
    
    Args:
        request (ValidationRequest): Validation request with user changes
        
    Returns:
        dict: Final validated results with JSON report
    """
    try:
        main_logger.info(f"Starting validation for session {request.session_id}")
        
        if request.session_id not in app_state.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = app_state.active_sessions[request.session_id]
        
        # Get original classification results
        original_results = session.get("classification_results", {})
        main_logger.info(f"Original results has {len(original_results.get('field_analyses', {}))} field analyses")
        
        # Apply user changes if any
        if request.changes or request.pii_fields_only:
            main_logger.info(f"Applying user changes: {len(request.changes or {})} field changes")
            
            if request.pii_fields_only:
                # Use the filtered PII fields provided by frontend
                main_logger.info(f"Filtering to PII fields only: {len(request.pii_fields_only)} fields")
                
                # Create filtered results with only PII fields
                filtered_results = {
                    "field_analyses": {},
                    "summary": {
                        "total_fields": len(request.pii_fields_only),
                        "pii_fields": len(request.pii_fields_only),
                        "high_risk": sum(1 for field in request.pii_fields_only if field.get('riskLevel') == 'HIGH'),
                        "message": f"Filtered to include only {len(request.pii_fields_only)} PII fields"
                    },
                    "status": "completed"
                }
                
                # Add each PII field to field_analyses
                for field in request.pii_fields_only:
                    field_key = f"{field.get('table', 'unknown')}.{field.get('field', 'unknown')}"
                    filtered_results["field_analyses"][field_key] = {
                        "field_name": field.get('field'),
                        "table_name": field.get('table'),
                        "is_sensitive": True,  # All included fields are PII
                        "pii_type": field.get('classification', 'PII'),
                        "risk_level": field.get('riskLevel', 'MEDIUM'),
                        "confidence_score": field.get('confidence', 0.9),
                        "source": field.get('source', 'User Validated'),
                        "rationale": f"User-validated {field.get('classification', 'PII')} field",
                        "applicable_regulations": field.get('regulations', ['HIPAA'])
                    }
                
                session["final_results"] = filtered_results
            else:
                # Apply changes to original results
                session["final_results"] = original_results
        else:
            session["final_results"] = original_results
        
        session["status"] = "validated"
        
        # Generate comprehensive JSON report
        try:
            final_results = session["final_results"]
            field_analyses = final_results.get("field_analyses", {})
            
            # Create detailed JSON report
            json_report = {
                "scan_metadata": {
                    "session_id": request.session_id,
                    "scan_timestamp": datetime.now().isoformat(),
                    "regulation": request.changes.get('regulation') if request.changes else 'HIPAA',
                    "total_fields_analyzed": final_results.get("summary", {}).get("total_fields", 0),
                    "pii_fields_detected": final_results.get("summary", {}).get("pii_fields", 0),
                    "high_risk_fields": final_results.get("summary", {}).get("high_risk", 0)
                },
                "sensitive_fields": [],
                "non_sensitive_fields": [],
                "summary": {
                    "total_sensitive": 0,
                    "total_non_sensitive": 0,
                    "risk_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
                    "regulation_compliance": {}
                }
            }
            
            # Process each field
            for field_key, field_data in field_analyses.items():
                field_info = {
                    "field_name": field_data.get("field_name"),
                    "table_name": field_data.get("table_name"),
                    "classification": field_data.get("pii_type", "OTHER"),
                    "risk_level": field_data.get("risk_level", "LOW"),
                    "confidence_score": field_data.get("confidence_score", 0.0),
                    "applicable_regulations": field_data.get("applicable_regulations", []),
                    "rationale": field_data.get("rationale", "No rationale provided"),
                    "is_sensitive": field_data.get("is_sensitive", False)
                }
                
                if field_data.get("is_sensitive", False):
                    json_report["sensitive_fields"].append(field_info)
                    json_report["summary"]["total_sensitive"] += 1
                    
                    # Update risk distribution
                    risk = field_data.get("risk_level", "LOW")
                    json_report["summary"]["risk_distribution"][risk] = json_report["summary"]["risk_distribution"].get(risk, 0) + 1
                else:
                    json_report["non_sensitive_fields"].append(field_info)
                    json_report["summary"]["total_non_sensitive"] += 1
            
            # Add regulation compliance info
            if json_report["sensitive_fields"]:
                regulations = set()
                for field in json_report["sensitive_fields"]:
                    regulations.update(field.get("applicable_regulations", []))
                
                for reg in regulations:
                    reg_fields = [f for f in json_report["sensitive_fields"] if reg in f.get("applicable_regulations", [])]
                    json_report["summary"]["regulation_compliance"][reg] = {
                        "applicable_fields": len(reg_fields),
                        "field_names": [f["field_name"] for f in reg_fields]
                    }
            
            # Store JSON report in session
            session["json_report"] = json_report
            
            main_logger.info(f"Results validated and JSON report generated for session {request.session_id}")
            
            return {
                "session_id": request.session_id,
                "final_results": session["final_results"],
                "json_report": json_report,
                "status": "success"
            }
            
        except Exception as report_error:
            main_logger.error(f"Error generating JSON report: {report_error}", exc_info=True)
            # Still return results even if report generation fails
            return {
                "session_id": request.session_id,
                "final_results": session["final_results"],
                "json_report": {"error": "Report generation failed", "message": str(report_error)},
                "status": "success"
            }
        
    except Exception as e:
        main_logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


# =============================================================================
# REPORTS API ENDPOINTS
# =============================================================================

@app.get("/api/reports")
async def get_reports():
    """
    Get all previous scan reports.
    
    Returns:
        dict: List of completed scan reports with metadata
    """
    try:
        reports = []
        
        # Get all completed sessions that have reports
        for session_id, session_data in app_state.active_sessions.items():
            if session_data.get("status") == "validated" and session_data.get("final_results"):
                final_results = session_data.get("final_results", {})
                summary = final_results.get("summary", {})
                
                report = {
                    "id": session_id,
                    "session_id": session_id,
                    "name": f"PII Scan - {session_id[:8]}",
                    "fileName": session_data.get("original_filename", "unknown.sql"),
                    "type": session_data.get("scan_type", "COMPREHENSIVE"),
                    "status": "completed",
                    "createdDate": session_data.get("created_at", "2025-01-30"),
                    "riskLevel": "HIGH" if summary.get("high_risk", 0) > 0 else "MEDIUM" if summary.get("pii_fields", 0) > 0 else "LOW",
                    "piiFields": summary.get("pii_fields", 0),
                    "totalFields": summary.get("total_fields", 0),
                    "complianceScore": min(95, max(50, 100 - (summary.get("high_risk", 0) * 10))),
                    "scanDuration": f"{session_data.get('scan_duration', 1.5):.1f}s",
                    "regulations": session_data.get("regulations", ["HIPAA"])
                }
                reports.append(report)
        
        # Sort by creation date (most recent first)
        reports.sort(key=lambda x: x["createdDate"], reverse=True)
        
        main_logger.info(f"Retrieved {len(reports)} reports")
        
        return {
            "reports": reports,
            "total": len(reports),
            "status": "success"
        }
        
    except Exception as e:
        main_logger.error(f"Error retrieving reports: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reports: {str(e)}")


@app.get("/api/reports/{session_id}")
async def get_report_details(session_id: str):
    """
    Get detailed report for a specific session.
    
    Args:
        session_id (str): The session ID of the report to retrieve
        
    Returns:
        dict: Detailed report data with metadata
    """
    try:
        if session_id not in app_state.active_sessions:
            raise HTTPException(status_code=404, detail="Report not found")
        
        session = app_state.active_sessions[session_id]
        
        if session.get("status") != "validated":
            raise HTTPException(status_code=404, detail="Report not completed")
        
        return {
            "session_id": session_id,
            "report_data": session.get("final_results", {}),
            "metadata": {
                "created_at": session.get("created_at"),
                "scan_type": session.get("scan_type"),
                "original_filename": session.get("original_filename"),
                "regulations": session.get("regulations", [])
            },
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        main_logger.error(f"Error retrieving report details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report details: {str(e)}")


# =============================================================================
# REPORT GENERATION ENDPOINTS  
# =============================================================================


@app.post("/api/generate-report/{session_id}")
async def generate_report(session_id: str, format: str = "json"):
    """Step 12: Generate final report"""
    try:
        if session_id not in app_state.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = app_state.active_sessions[session_id]
        results = session.get("final_results", {})
        
        # Generate report in requested format
        report = {
            "session_id": session_id,
            "generated_at": datetime.now().isoformat(),
            "file_info": {
                "name": session["file_name"],
                "type": session["file_type"]
            },
            "analysis_results": results,
            "summary": {
                "total_tables": len(session.get("tables", {})),
                "total_columns": len(session.get("schema_data", [])),
                "high_risk_fields": 0,  # Calculate from results
                "medium_risk_fields": 0,  # Calculate from results
                "low_risk_fields": 0  # Calculate from results
            }
        }
        
        session["report"] = report
        session["status"] = "completed"
        
        if format.lower() == "json":
            return JSONResponse(content=report)
        else:
            # For other formats, return as file download
            return StreamingResponse(
                io.StringIO(json.dumps(report, indent=2)),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=pii_report_{session_id}.json"}
            )
        
    except Exception as e:
        main_logger.error(f"Report generation error: {e}")
        main_logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# DATABASE CONNECTIVITY ENDPOINTS
# =============================================================================

@app.post("/api/test-database-connection")
async def test_database_connection(request: DatabaseConnectionRequest):
    """
    Test database connection without extracting schema.
    
    Args:
        request (DatabaseConnectionRequest): Database connection configuration
        
    Returns:
        dict: Connection test results
    """
    try:
        # Create database connection config
        connection_config = DatabaseConnection(
            type=request.type,
            host=request.host,
            port=request.port,
            database=request.database,
            username=request.username,
            password=request.password,
            ssl=request.ssl,
            additional_params=request.additional_params
        )
        
        # Test connection
        result = database_connector.test_connection(connection_config)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": result["message"],
                "connection_time": result["connection_time"],
                "database_type": result["database_type"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        main_logger.error(f"Database connection test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/connect-database")
async def connect_database(request: DatabaseConnectionRequest):
    """Connect to database and extract schema for PII/PHI analysis"""
    try:
        # Create database connection config
        connection_config = DatabaseConnection(
            type=request.type,
            host=request.host,
            port=request.port,
            database=request.database,
            username=request.username,
            password=request.password,
            ssl=request.ssl,
            additional_params=request.additional_params
        )
        
        # Connect and extract schema
        result = database_connector.connect_and_extract_schema(connection_config)
        
        if result["status"] == "success":
            # Store in session for later processing
            session_id = result["session_id"]
            app_state.active_sessions[session_id] = {
                "database_connection": connection_config,
                "schema_data": result["schema_data"],
                "tables": result["tables"],
                "file_name": f"{request.type}://{request.host}/{request.database}",
                "file_type": "database",
                "created_at": datetime.now(),
                "status": "extracted",
                "source": "database"
            }
            
            return {
                "session_id": session_id,
                "status": "success",
                "tables": result["tables"],
                "schema_data": result["schema_data"],
                "total_tables": result["total_tables"],
                "total_columns": result["total_columns"],
                "extraction_time": result["extraction_time"],
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        main_logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Performance and Monitoring Endpoints
@app.get("/api/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get session status and progress"""
    if session_id not in app_state.active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = app_state.active_sessions[session_id]
    return {
        "session_id": session_id,
        "status": session.get("status", "unknown"),
        "created_at": session.get("created_at"),
        "progress": {
            "uploaded": session.get("status") in ["uploaded", "extracted", "classified", "validated", "completed"],
            "extracted": session.get("status") in ["extracted", "classified", "validated", "completed"],
            "classified": session.get("status") in ["classified", "validated", "completed"],
            "validated": session.get("status") in ["validated", "completed"],
            "completed": session.get("status") == "completed"
        }
    }

@app.get("/api/performance/stats")
async def get_performance_stats():
    """Get system performance statistics"""
    return {
        "active_sessions": len(app_state.active_sessions),
        "cache_size": len(app_state.performance_cache),
        "uptime": time.time(),
        "memory_usage": "N/A",  # Could implement actual memory monitoring
        "processing_queue": 0
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )