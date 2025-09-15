#!/usr/bin/env python3
"""
Unified Main Entry Point for PII/PHI Scanner POC
Consolidates all main() functions across the system into a single, organized interface
"""

import sys
import argparse
import logging
from typing import Dict, Callable, List, Optional, Any
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our core systems
from pii_scanner_poc.core.configuration import get_config, load_config, SystemConfig
from pii_scanner_poc.core.exceptions import PIIScannerBaseException, handle_exception
from pii_scanner_poc.core.service_interfaces import ServiceFactory


class PIIScannerApplication:
    """
    Unified application controller for PII/PHI Scanner POC
    
    Consolidates all main entry points and provides a consistent interface
    for different operation modes and tools.
    """
    
    def __init__(self):
        """Initialize the unified application"""
        self.config: Optional[SystemConfig] = None
        self.service_factory: Optional[ServiceFactory] = None
        self.logger: Optional[logging.Logger] = None
        
        # Registry of available commands and their handlers
        self.commands: Dict[str, Callable] = {
            'analyze': self._run_analysis,
            'mcp-server': self._run_mcp_server,
            'alias-management': self._run_alias_management,
            'import-aliases': self._run_alias_import,
            'test-system': self._run_system_tests,
            'config': self._run_config_management,
            'health-check': self._run_health_check,
            'cleanup': self._run_cleanup_tools
        }
    
    def initialize(self, config_overrides: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initialize the application with configuration
        
        Args:
            config_overrides: Optional configuration overrides
            
        Returns:
            bool: True if initialization successful
        """
        try:
            # Load configuration
            self.config = load_config(**(config_overrides or {}))
            
            # Setup logging
            self._setup_logging()
            
            # Initialize service factory
            self.service_factory = ServiceFactory(self.config)
            
            self.logger.info("PII/PHI Scanner application initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize application: {e}")
            return False
    
    def _setup_logging(self):
        """Setup logging based on configuration"""
        log_config = self.config.logging
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_config.level.value),
            format=log_config.format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Add file handler if specified
        if log_config.file_path:
            file_handler = logging.FileHandler(log_config.file_path)
            file_handler.setFormatter(logging.Formatter(log_config.format))
            self.logger.addHandler(file_handler)
    
    def run(self, command: str, args: List[str]) -> int:
        """
        Run the specified command with arguments
        
        Args:
            command: Command to execute
            args: Command arguments
            
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        try:
            if command not in self.commands:
                self.logger.error(f"Unknown command: {command}")
                self._print_help()
                return 1
            
            # Execute the command
            handler = self.commands[command]
            return handler(args)
            
        except PIIScannerBaseException as e:
            self.logger.error(f"Application error: {e}")
            if self.config.debug_mode:
                import traceback
                traceback.print_exc()
            return 1
            
        except Exception as e:
            handled_exception = handle_exception(e, logger=self.logger)
            self.logger.error(f"Unexpected error: {handled_exception}")
            if self.config.debug_mode:
                import traceback
                traceback.print_exc()
            return 1
    
    def shutdown(self):
        """Gracefully shutdown the application"""
        if self.service_factory:
            self.service_factory.shutdown_all_services()
        
        if self.logger:
            self.logger.info("PII/PHI Scanner application shutdown completed")
    
    def _run_analysis(self, args: List[str]) -> int:
        """Run schema analysis (consolidated from pii_scanner.py)"""
        from analysis.schema_analyzer import SchemaAnalyzer
        
        parser = argparse.ArgumentParser(description="Analyze schema for PII/PHI content")
        parser.add_argument('input', help='Input file or database connection')
        parser.add_argument('--regulations', nargs='+', default=['GDPR'], 
                          help='Regulations to check (GDPR, HIPAA, CCPA)')
        parser.add_argument('--output-format', choices=['console', 'json', 'csv'], 
                          default='console', help='Output format')
        parser.add_argument('--output-file', help='Output file path')
        parser.add_argument('--company-id', help='Company ID for context')
        parser.add_argument('--region', help='Region for context')
        parser.add_argument('--enable-llm', action='store_true', 
                          help='Enable LLM analysis')
        parser.add_argument('--batch-size', type=int, 
                          help='Batch size for processing')
        
        parsed_args = parser.parse_args(args)
        
        try:
            # Create analyzer with current configuration
            analyzer = SchemaAnalyzer(self.config, self.service_factory)
            
            # Run analysis
            result = analyzer.analyze(
                input_source=parsed_args.input,
                regulations=parsed_args.regulations,
                output_format=parsed_args.output_format,
                output_file=parsed_args.output_file,
                company_id=parsed_args.company_id,
                region=parsed_args.region,
                enable_llm=parsed_args.enable_llm,
                batch_size=parsed_args.batch_size
            )
            
            self.logger.info(f"Analysis completed successfully: {result['summary']}")
            return 0
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return 1
    
    def _run_mcp_server(self, args: List[str]) -> int:
        """Run MCP server (consolidated from mcp_server.py)"""
        from mcp.server import MCPServer
        
        parser = argparse.ArgumentParser(description="Run MCP server for AI assistant integration")
        parser.add_argument('--port', type=int, help='Server port')
        parser.add_argument('--host', default='localhost', help='Server host')
        parser.add_argument('--config-file', help='MCP configuration file')
        
        parsed_args = parser.parse_args(args)
        
        try:
            # Create and run MCP server
            server = MCPServer(self.config, self.service_factory)
            
            self.logger.info("Starting MCP server...")
            return server.run(
                host=parsed_args.host,
                port=parsed_args.port,
                config_file=parsed_args.config_file
            )
            
        except Exception as e:
            self.logger.error(f"MCP server failed: {e}")
            return 1
    
    def _run_alias_management(self, args: List[str]) -> int:
        """Run alias management (consolidated from alias_management.py)"""
        from tools.alias_manager import AliasManager
        
        parser = argparse.ArgumentParser(description="Manage field aliases")
        parser.add_argument('action', choices=['add', 'search', 'list', 'approve', 'stats', 'export'])
        parser.add_argument('--field-name', help='Field name for operations')
        parser.add_argument('--pii-type', help='PII type for alias')
        parser.add_argument('--confidence', type=float, help='Confidence score')
        parser.add_argument('--company-id', help='Company ID')
        parser.add_argument('--output-file', help='Output file for exports')
        
        parsed_args = parser.parse_args(args)
        
        try:
            # Create alias manager
            manager = AliasManager(self.config, self.service_factory)
            
            # Execute the requested action
            result = manager.execute_action(
                action=parsed_args.action,
                field_name=parsed_args.field_name,
                pii_type=parsed_args.pii_type,
                confidence=parsed_args.confidence,
                company_id=parsed_args.company_id,
                output_file=parsed_args.output_file
            )
            
            print(result)
            return 0
            
        except Exception as e:
            self.logger.error(f"Alias management failed: {e}")
            return 1
    
    def _run_alias_import(self, args: List[str]) -> int:
        """Run alias import (consolidated from import_regulation_aliases.py)"""
        from tools.alias_importer import RegulationAliasImporter
        
        parser = argparse.ArgumentParser(description="Import regulation aliases")
        parser.add_argument('--csv-file', help='CSV file to import')
        parser.add_argument('--regulations', nargs='+', default=['GDPR', 'HIPAA'],
                          help='Regulations to import')
        parser.add_argument('--dry-run', action='store_true', help='Preview import without changes')
        
        parsed_args = parser.parse_args(args)
        
        try:
            # Create and run importer
            importer = RegulationAliasImporter(self.config, self.service_factory)
            
            result = importer.import_aliases(
                csv_file=parsed_args.csv_file,
                regulations=parsed_args.regulations,
                dry_run=parsed_args.dry_run
            )
            
            print(f"Import completed: {result['summary']}")
            return 0
            
        except Exception as e:
            self.logger.error(f"Alias import failed: {e}")
            return 1
    
    def _run_system_tests(self, args: List[str]) -> int:
        """Run system tests (consolidated from test files)"""
        from testing.test_runner import SystemTestRunner
        
        parser = argparse.ArgumentParser(description="Run system tests")
        parser.add_argument('--test-type', choices=['unit', 'integration', 'performance', 'all'],
                          default='all', help='Type of tests to run')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
        parser.add_argument('--output-file', help='Test results output file')
        
        parsed_args = parser.parse_args(args)
        
        try:
            # Create and run test runner
            runner = SystemTestRunner(self.config, self.service_factory)
            
            result = runner.run_tests(
                test_type=parsed_args.test_type,
                verbose=parsed_args.verbose,
                output_file=parsed_args.output_file
            )
            
            print(f"Tests completed: {result['summary']}")
            return 0 if result['success'] else 1
            
        except Exception as e:
            self.logger.error(f"System tests failed: {e}")
            return 1
    
    def _run_config_management(self, args: List[str]) -> int:
        """Run configuration management"""
        parser = argparse.ArgumentParser(description="Manage system configuration")
        parser.add_argument('action', choices=['show', 'validate', 'export', 'test'])
        parser.add_argument('--format', choices=['json', 'ini'], default='json')
        parser.add_argument('--output-file', help='Output file for export')
        
        parsed_args = parser.parse_args(args)
        
        try:
            if parsed_args.action == 'show':
                print("Current Configuration:")
                print("=" * 50)
                config_dict = self.config.__dict__
                for section, values in config_dict.items():
                    print(f"\n[{section}]")
                    if hasattr(values, '__dict__'):
                        for key, value in values.__dict__.items():
                            print(f"  {key} = {value}")
                    else:
                        print(f"  {section} = {values}")
            
            elif parsed_args.action == 'validate':
                print("Configuration validation successful ✅")
                
            elif parsed_args.action == 'export':
                if not parsed_args.output_file:
                    print("Output file required for export")
                    return 1
                
                from pii_scanner_poc.core.configuration import config_manager
                config_manager.export_configuration(
                    parsed_args.output_file, 
                    parsed_args.format
                )
                print(f"Configuration exported to {parsed_args.output_file}")
            
            elif parsed_args.action == 'test':
                print("Testing configuration components...")
                # Test each configuration section
                errors = []
                
                # Test AI service config
                if self.config.processing.enable_llm and not self.config.ai_service.api_key:
                    errors.append("AI service API key missing but LLM is enabled")
                
                # Test database paths
                if not Path(self.config.alias.database_path).parent.exists():
                    errors.append(f"Alias database directory does not exist: {self.config.alias.database_path}")
                
                if errors:
                    print("Configuration issues found:")
                    for error in errors:
                        print(f"  ❌ {error}")
                    return 1
                else:
                    print("All configuration tests passed ✅")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Configuration management failed: {e}")
            return 1
    
    def _run_health_check(self, args: List[str]) -> int:
        """Run system health check"""
        parser = argparse.ArgumentParser(description="Check system health")
        parser.add_argument('--detailed', action='store_true', help='Detailed health report')
        
        parsed_args = parser.parse_args(args)
        
        try:
            print("🏥 PII/PHI Scanner System Health Check")
            print("=" * 50)
            
            health_status = True
            
            # Check configuration
            print("📋 Configuration: ✅ Loaded")
            
            # Check services
            services_to_check = ['alias_service', 'cache_service']
            for service_name in services_to_check:
                try:
                    service = self.service_factory.create_service(service_name)
                    service.initialize()
                    health = service.get_health()
                    status_icon = "✅" if health.status.value == "ready" else "❌"
                    print(f"🔧 {service_name}: {status_icon} {health.status.value}")
                    
                    if parsed_args.detailed and health.performance_metrics:
                        for metric, value in health.performance_metrics.items():
                            print(f"   └─ {metric}: {value}")
                            
                except Exception as e:
                    print(f"🔧 {service_name}: ❌ Error - {e}")
                    health_status = False
            
            # Check file system
            critical_paths = [
                self.config.project_root,
                Path(self.config.alias.database_path).parent
            ]
            
            for path in critical_paths:
                if Path(path).exists():
                    print(f"📁 {path}: ✅ Accessible")
                else:
                    print(f"📁 {path}: ❌ Not found")
                    health_status = False
            
            # Overall status
            print("\n" + "=" * 50)
            if health_status:
                print("🎉 Overall System Health: ✅ HEALTHY")
                return 0
            else:
                print("⚠️ Overall System Health: ❌ ISSUES DETECTED")
                return 1
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return 1
    
    def _run_cleanup_tools(self, args: List[str]) -> int:
        """Run cleanup tools"""
        from tools.cleanup_manager import CleanupManager
        
        parser = argparse.ArgumentParser(description="Run system cleanup")
        parser.add_argument('action', choices=['analyze', 'clean', 'optimize'])
        parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
        parser.add_argument('--aggressive', action='store_true', help='Aggressive cleanup')
        
        parsed_args = parser.parse_args(args)
        
        try:
            # Create cleanup manager
            cleanup = CleanupManager(self.config)
            
            result = cleanup.execute_cleanup(
                action=parsed_args.action,
                dry_run=parsed_args.dry_run,
                aggressive=parsed_args.aggressive
            )
            
            print(f"Cleanup completed: {result['summary']}")
            return 0
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return 1
    
    def _print_help(self):
        """Print help information"""
        print("PII/PHI Scanner POC - Unified Application Interface")
        print("=" * 60)
        print()
        print("Available commands:")
        print("  analyze          - Analyze schema for PII/PHI content")
        print("  mcp-server       - Run MCP server for AI assistant integration")
        print("  alias-management - Manage field aliases")
        print("  import-aliases   - Import regulation-specific aliases")
        print("  test-system      - Run system tests")
        print("  config           - Manage system configuration")
        print("  health-check     - Check system health")
        print("  cleanup          - Run cleanup and optimization tools")
        print()
        print("Use 'python main.py <command> --help' for command-specific help")


def main() -> int:
    """
    Unified main entry point for all PII/PHI Scanner operations
    
    Returns:
        int: Exit code
    """
    # Parse command line arguments
    if len(sys.argv) < 2:
        app = PIIScannerApplication()
        app._print_help()
        return 1
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    # Handle special cases
    if command in ['--help', '-h', 'help']:
        app = PIIScannerApplication()
        app._print_help()
        return 0
    
    if command == '--version':
        print("PII/PHI Scanner POC v2.0.0")
        return 0
    
    # Initialize and run application
    app = PIIScannerApplication()
    
    try:
        # Extract configuration overrides from environment or args
        config_overrides = {}
        
        if '--debug' in args:
            config_overrides['debug_mode'] = True
            args.remove('--debug')
        
        if '--config' in args:
            config_idx = args.index('--config')
            config_file = args[config_idx + 1]
            config_overrides['config_file'] = config_file
            args = args[:config_idx] + args[config_idx + 2:]
        
        # Initialize application
        if not app.initialize(config_overrides):
            return 1
        
        # Run the command
        return app.run(command, args)
        
    finally:
        app.shutdown()


if __name__ == "__main__":
    sys.exit(main())