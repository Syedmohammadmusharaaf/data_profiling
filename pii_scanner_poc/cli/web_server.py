#!/usr/bin/env python3
"""
Simple Web Interface for PII/PHI Scanner POC
Provides a REST API wrapper around the CLI functionality
"""

import sys
import os
import json
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("❌ FastAPI not available. Install with: pip install fastapi uvicorn python-multipart")
    sys.exit(1)

# Import our core systems
from pii_scanner_poc.core.configuration import load_config, SystemConfig
from pii_scanner_poc.core.pii_scanner_facade import PIIScannerFacade
from pii_scanner_poc.core.exceptions import PIIScannerBaseException
from pii_scanner_poc.models.data_models import Regulation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PII/PHI Scanner API",
    description="REST API for PII/PHI Scanner POC",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global scanner instance
scanner_facade: Optional[PIIScannerFacade] = None
config: Optional[SystemConfig] = None


class AnalysisRequest(BaseModel):
    """Request model for analysis"""
    ddl_content: Optional[str] = None
    regulations: List[str] = ["GDPR"]
    company_id: Optional[str] = None
    region: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]


@app.on_event("startup")
async def startup_event():
    """Initialize the scanner on startup"""
    global scanner_facade, config
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize scanner facade
        scanner_facade = PIIScannerFacade(config)
        if not scanner_facade.initialize():
            raise Exception("Failed to initialize scanner facade")
        
        logger.info("PII/PHI Scanner API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize scanner: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global scanner_facade
    
    if scanner_facade:
        scanner_facade.shutdown()
    
    logger.info("PII/PHI Scanner API shutdown completed")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "PII/PHI Scanner API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        services = {}
        
        if scanner_facade:
            # Check scanner services
            services["scanner_facade"] = "healthy"
            
            # Check AI service if enabled
            if config and config.processing.enable_llm:
                services["ai_service"] = "healthy"  # Could add actual health check
            
            services["configuration"] = "healthy"
        else:
            services["scanner_facade"] = "unhealthy"
        
        return HealthResponse(
            status="healthy" if all(s == "healthy" for s in services.values()) else "degraded",
            timestamp=datetime.now().isoformat(),
            version="2.0.0",
            services=services
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/ddl")
async def analyze_ddl(request: AnalysisRequest):
    """Analyze DDL content for PII/PHI"""
    try:
        if not scanner_facade:
            raise HTTPException(status_code=503, detail="Scanner not initialized")
        
        if not request.ddl_content:
            raise HTTPException(status_code=400, detail="DDL content is required")
        
        # Convert regulation strings to enums
        regulations = []
        for reg_str in request.regulations:
            try:
                regulations.append(Regulation(reg_str.upper()))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid regulation: {reg_str}")
        
        # Create temporary file for DDL content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(request.ddl_content)
            temp_file = f.name
        
        try:
            # Analyze the DDL
            results = scanner_facade.analyze_ddl_file(
                ddl_file_path=temp_file,
                regulations=regulations,
                company_id=request.company_id,
                region=request.region
            )
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "analysis_results": results,
                "metadata": {
                    "regulations": request.regulations,
                    "company_id": request.company_id,
                    "region": request.region
                }
            }
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass
                
    except PIIScannerBaseException as e:
        logger.error(f"Scanner error: {e}")
        raise HTTPException(status_code=400, detail=e.to_dict())
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/file")
async def analyze_file(
    file: UploadFile = File(...),
    regulations: str = Form(default="GDPR"),
    company_id: Optional[str] = Form(default=None),
    region: Optional[str] = Form(default=None)
):
    """Analyze uploaded DDL file for PII/PHI"""
    try:
        if not scanner_facade:
            raise HTTPException(status_code=503, detail="Scanner not initialized")
        
        # Validate file type
        if not file.filename.endswith(('.sql', '.ddl', '.txt')):
            raise HTTPException(status_code=400, detail="File must be .sql, .ddl, or .txt")
        
        # Read file content
        content = await file.read()
        ddl_content = content.decode('utf-8')
        
        # Parse regulations
        reg_list = [r.strip() for r in regulations.split(',')]
        
        # Create analysis request
        request = AnalysisRequest(
            ddl_content=ddl_content,
            regulations=reg_list,
            company_id=company_id,
            region=region
        )
        
        # Use the DDL analysis endpoint
        return await analyze_ddl(request)
        
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_configuration():
    """Get current configuration"""
    try:
        if not config:
            raise HTTPException(status_code=503, detail="Configuration not loaded")
        
        # Return safe configuration (no secrets)
        return {
            "processing": {
                "batch_size": config.processing.batch_size,
                "enable_llm": config.processing.enable_llm,
                "confidence_threshold": config.processing.confidence_threshold
            },
            "ai_service": {
                "model": config.ai_service.model,
                "max_tokens": config.ai_service.max_tokens,
                "temperature": config.ai_service.temperature,
                "api_configured": bool(config.ai_service.api_key)
            },
            "version": config.version,
            "debug_mode": config.debug_mode
        }
        
    except Exception as e:
        logger.error(f"Configuration retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/regulations")
async def get_supported_regulations():
    """Get list of supported regulations"""
    return {
        "regulations": [reg.value for reg in Regulation],
        "descriptions": {
            "GDPR": "General Data Protection Regulation (EU)",
            "HIPAA": "Health Insurance Portability and Accountability Act (US)",
            "CCPA": "California Consumer Privacy Act (US)",
            "PCI_DSS": "Payment Card Industry Data Security Standard"
        }
    }


def main():
    """Run the web server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PII/PHI Scanner Web API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the server
    uvicorn.run(
        "web_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info" if not args.debug else "debug"
    )


if __name__ == "__main__":
    main()