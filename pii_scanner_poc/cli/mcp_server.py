"""
Enhanced MCP Server for PII Scanner
Provides Model Context Protocol interface with comprehensive logging and error handling
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

# MCP imports - Updated for latest version
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ReadResourceRequest, ReadResourceResult,
    ListResourcesRequest, ListResourcesResult, ListToolsRequest, ListToolsResult
)

# Application imports
from pii_scanner_poc.core.pii_scanner_facade import pii_scanner
from pii_scanner_poc.utils.logging_config import mcp_logger, log_function_entry, log_function_exit


class EnhancedMCPServer:
    """Enhanced MCP Server with comprehensive logging and error handling"""
    
    def __init__(self):
        self.server = Server("pii-scanner-enhanced")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources"""
            log_function_entry(mcp_logger, "handle_list_resources")
            
            try:
                resources = [
                    Resource(
                        uri="schema://sample",
                        name="Sample Database Schema",
                        description="Sample database schema for testing PII analysis",
                        mimeType="text/plain"
                    ),
                    Resource(
                        uri="config://validation",
                        name="Configuration Validation",
                        description="Current scanner configuration and validation status",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri="logs://recent",
                        name="Recent Analysis Logs",
                        description="Recent analysis session logs and debugging information",
                        mimeType="application/json"
                    )
                ]
                
                mcp_logger.info("Listed MCP resources", extra={
                    'component': 'mcp_server',
                    'resource_count': len(resources)
                })
                
                log_function_exit(mcp_logger, "handle_list_resources", f"Returned {len(resources)} resources")
                return resources
                
            except Exception as e:
                mcp_logger.error("Failed to list resources", extra={
                    'component': 'mcp_server',
                    'error': str(e)
                }, exc_info=True)
                return []
        
        @self.server.read_resource()
        async def handle_get_resource(request: ReadResourceRequest) -> ReadResourceResult:
            """Get specific resource content"""
            log_function_entry(mcp_logger, "handle_get_resource", uri=request.uri)
            
            try:
                if request.uri == "schema://sample":
                    content = await self._get_sample_schema()
                elif request.uri == "config://validation":
                    content = await self._get_config_validation()
                elif request.uri == "logs://recent":
                    content = await self._get_recent_logs()
                else:
                    raise ValueError(f"Unknown resource URI: {request.uri}")
                
                mcp_logger.info("Retrieved resource", extra={
                    'component': 'mcp_server',
                    'uri': request.uri,
                    'content_size': len(str(content))
                })
                
                log_function_exit(mcp_logger, "handle_get_resource", f"Retrieved {request.uri}")
                
                return ReadResourceResult(contents=[TextContent(type="text", text=content)])
                
            except Exception as e:
                mcp_logger.error("Failed to get resource", extra={
                    'component': 'mcp_server',
                    'uri': request.uri,
                    'error': str(e)
                }, exc_info=True)
                
                error_content = json.dumps({
                    'error': str(e),
                    'uri': request.uri,
                    'timestamp': str(asyncio.get_event_loop().time())
                }, indent=2)
                
                return ReadResourceResult(contents=[TextContent(type="text", text=error_content)])
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            log_function_entry(mcp_logger, "handle_list_tools")
            
            try:
                tools = [
                    Tool(
                        name="analyze_schema_file",
                        description="Analyze a database schema file for PII/PHI data according to privacy regulations",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "Path to the schema file (DDL, JSON, etc.)"
                                },
                                "regulations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of regulations to check (GDPR, HIPAA, CCPA)",
                                    "default": ["GDPR", "HIPAA"]
                                },
                                "selected_tables": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Optional list of specific tables to analyze"
                                },
                                "output_format": {
                                    "type": "string",
                                    "enum": ["json", "html", "csv"],
                                    "description": "Output format for the report",
                                    "default": "json"
                                }
                            },
                            "required": ["file_path"]
                        }
                    ),
                    Tool(
                        name="validate_configuration",
                        description="Validate the current PII scanner configuration and connectivity",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "additionalProperties": False
                        }
                    ),
                    Tool(
                        name="analyze_schema_content",
                        description="Analyze schema content directly without file I/O",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "schema_content": {
                                    "type": "string",
                                    "description": "Direct schema content (DDL, JSON, etc.)"
                                },
                                "content_format": {
                                    "type": "string",
                                    "enum": ["ddl", "json", "auto"],
                                    "description": "Format of the schema content",
                                    "default": "auto"
                                },
                                "regulations": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of regulations to check",
                                    "default": ["GDPR", "HIPAA"]
                                }
                            },
                            "required": ["schema_content"]
                        }
                    ),
                    Tool(
                        name="get_analysis_status",
                        description="Get the status of an analysis session",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "session_id": {
                                    "type": "string",
                                    "description": "Analysis session ID"
                                }
                            },
                            "required": ["session_id"]
                        }
                    )
                ]
                
                mcp_logger.info("Listed MCP tools", extra={
                    'component': 'mcp_server',
                    'tool_count': len(tools)
                })
                
                log_function_exit(mcp_logger, "handle_list_tools", f"Returned {len(tools)} tools")
                return tools
                
            except Exception as e:
                mcp_logger.error("Failed to list tools", extra={
                    'component': 'mcp_server',
                    'error': str(e)
                }, exc_info=True)
                return []
        
        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool execution"""
            log_function_entry(mcp_logger, "handle_call_tool", 
                              tool_name=request.name,
                              arguments=request.arguments)
            
            try:
                if request.name == "analyze_schema_file":
                    result = await self._analyze_schema_file(request.arguments)
                elif request.name == "validate_configuration":
                    result = await self._validate_configuration(request.arguments)
                elif request.name == "analyze_schema_content":
                    result = await self._analyze_schema_content(request.arguments)
                elif request.name == "get_analysis_status":
                    result = await self._get_analysis_status(request.arguments)
                else:
                    raise ValueError(f"Unknown tool: {request.name}")
                
                mcp_logger.info("Tool executed successfully", extra={
                    'component': 'mcp_server',
                    'tool_name': request.name,
                    'result_size': len(str(result))
                })
                
                log_function_exit(mcp_logger, "handle_call_tool", f"Tool {request.name} completed")
                
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2, default=str))])
                
            except Exception as e:
                mcp_logger.error("Tool execution failed", extra={
                    'component': 'mcp_server',
                    'tool_name': request.name,
                    'arguments': request.arguments,
                    'error': str(e)
                }, exc_info=True)
                
                error_result = {
                    'success': False,
                    'error': str(e),
                    'tool': request.name,
                    'timestamp': str(asyncio.get_event_loop().time())
                }
                
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(error_result, indent=2))])
    
    async def _get_sample_schema(self) -> str:
        """Get sample schema content"""
        sample_schema_path = Path("sample_schema.ddl")
        
        if sample_schema_path.exists():
            with open(sample_schema_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            return "Sample schema file not found"
    
    async def _get_config_validation(self) -> str:
        """Get configuration validation results"""
        try:
            validation_result = pii_scanner.validate_configuration()
            return json.dumps(validation_result, indent=2, default=str)
        except Exception as e:
            return json.dumps({'error': str(e)}, indent=2)
    
    async def _get_recent_logs(self) -> str:
        """Get recent analysis logs"""
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return json.dumps({'message': 'No logs directory found'}, indent=2)
            
            log_files = list(logs_dir.glob("*.log"))
            recent_logs = {}
            
            for log_file in log_files[-3:]:  # Get last 3 log files
                try:
                    with open(log_file, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                        recent_logs[log_file.name] = {
                            'file_size': log_file.stat().st_size,
                            'line_count': len(lines),
                            'last_10_lines': lines[-10:] if lines else []
                        }
                except Exception:
                    recent_logs[log_file.name] = {'error': 'Could not read log file'}
            
            return json.dumps(recent_logs, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({'error': str(e)}, indent=2)
    
    async def _analyze_schema_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze schema file tool implementation"""
        file_path = arguments.get('file_path')
        regulations = arguments.get('regulations', ['GDPR', 'HIPAA'])
        selected_tables = arguments.get('selected_tables')
        output_format = arguments.get('output_format', 'json')
        
        if not file_path:
            raise ValueError("file_path is required")
        
        mcp_logger.info("Starting schema file analysis", extra={
            'component': 'mcp_server',
            'file_path': file_path,
            'regulations': regulations,
            'selected_tables': selected_tables,
            'output_format': output_format
        })
        
        # Execute analysis
        result = pii_scanner.analyze_schema_file(
            schema_file_path=file_path,
            regulations=regulations,
            selected_tables=selected_tables,
            output_format=output_format
        )
        
        return result
    
    async def _validate_configuration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration tool implementation"""
        mcp_logger.info("Starting configuration validation", extra={
            'component': 'mcp_server'
        })
        
        result = pii_scanner.validate_configuration()
        return result
    
    async def _analyze_schema_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze schema content directly"""
        schema_content = arguments.get('schema_content')
        content_format = arguments.get('content_format', 'auto')
        regulations = arguments.get('regulations', ['GDPR', 'HIPAA'])
        
        if not schema_content:
            raise ValueError("schema_content is required")
        
        mcp_logger.info("Starting schema content analysis", extra={
            'component': 'mcp_server',
            'content_length': len(schema_content),
            'content_format': content_format,
            'regulations': regulations
        })
        
        # Create temporary file for analysis
        import tempfile
        import os
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{content_format}', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(schema_content)
                temp_file_path = temp_file.name
            
            # Analyze the temporary file
            result = pii_scanner.analyze_schema_file(
                schema_file_path=temp_file_path,
                regulations=regulations,
                output_format='json'
            )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return result
            
        except Exception as e:
            # Ensure cleanup even if analysis fails
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            raise
    
    async def _get_analysis_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get analysis status tool implementation"""
        session_id = arguments.get('session_id')
        
        if not session_id:
            raise ValueError("session_id is required")
        
        mcp_logger.info("Getting analysis status", extra={
            'component': 'mcp_server',
            'session_id': session_id
        })
        
        result = pii_scanner.get_analysis_status(session_id)
        return result
    
    async def run(self):
        """Run the MCP server"""
        mcp_logger.info("Starting Enhanced MCP Server for PII Scanner", extra={
            'component': 'mcp_server',
            'server_name': self.server.name
        })
        
        try:
            # Import and configure asyncio stdio server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="pii-scanner-enhanced",
                        server_version="2.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={}
                        )
                    )
                )
        except Exception as e:
            mcp_logger.error("MCP Server failed", extra={
                'component': 'mcp_server',
                'error': str(e)
            }, exc_info=True)
            raise


async def main():
    """Main entry point for MCP server"""
    try:
        server = EnhancedMCPServer()
        await server.run()
    except KeyboardInterrupt:
        mcp_logger.info("MCP Server shutdown requested", extra={'component': 'mcp_server'})
    except Exception as e:
        mcp_logger.error("MCP Server startup failed", extra={
            'component': 'mcp_server',
            'error': str(e)
        }, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())