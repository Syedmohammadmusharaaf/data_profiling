"""
Configuration management for PII Scanner
Handles environment variables, config files, and validation
"""

import os
import configparser
from typing import Dict, Optional, List, Any
from pathlib import Path
from dataclasses import dataclass
from pii_scanner_poc.utils.logging_config import main_logger

@dataclass
class AIConfig:
    """AI service configuration"""
    api_key: str
    endpoint: str
    api_version: str
    deployment_name: str
    max_tokens: int = 2000
    temperature: float = 0.0
    timeout: int = 60

@dataclass
class BatchConfig:
    """Batch processing configuration"""
    small_batch_threshold: int = 10  # Reduced from 20
    medium_batch_threshold: int = 20  # Reduced from 40
    large_batch_threshold: int = 30   # Reduced from 60
    max_retries: int = 2             # Reduced from 3
    retry_delay: float = 2.0         # Increased from 1.0
    max_columns_per_batch: int = 15  # New: limit columns per batch
    max_tables_per_batch: int = 3    # New: limit tables per batch
    timeout_seconds: int = 45        # New: timeout per batch

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file_level: str = "DEBUG"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class PIIConfig:
    """Main PII Scanner configuration"""
    ai_config: AIConfig
    batch_config: BatchConfig
    logging_config: LoggingConfig
    supported_regulations: List[str]
    output_format: str = "json"

class ConfigurationManager:
    """Manages all configuration aspects of the PII Scanner"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or ".env"
        self.config = None
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from various sources"""
        try:
            main_logger.info("Loading configuration", extra={
                'component': 'config_manager',
                'config_path': self.config_path
            })
            
            # Load environment variables
            from dotenv import load_dotenv
            load_dotenv(self.config_path)
            
            # Create configuration objects
            ai_config = self._load_ai_config()
            batch_config = self._load_batch_config()
            logging_config = self._load_logging_config()
            
            self.config = PIIConfig(
                ai_config=ai_config,
                batch_config=batch_config,
                logging_config=logging_config,
                supported_regulations=['GDPR', 'HIPAA', 'CCPA'],
                output_format=os.getenv('OUTPUT_FORMAT', 'json')
            )
            
            # Validate configuration
            self._validate_configuration()
            
            main_logger.info("Configuration loaded successfully", extra={
                'component': 'config_manager',
                'regulations': self.config.supported_regulations
            })
            
        except Exception as e:
            main_logger.error("Failed to load configuration", extra={
                'component': 'config_manager',
                'error': str(e)
            })
            raise
    
    def _load_ai_config(self) -> AIConfig:
        """Load AI service configuration with fallback for missing variables"""
        required_vars = [
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_ENDPOINT', 
            'AZURE_OPENAI_API_VERSION',
            'AZURE_OPENAI_DEPLOYMENT'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            # Instead of raising an error, use placeholder values for testing/development
            main_logger.warning(f"Missing AI environment variables: {missing_vars}. Using placeholders.", extra={
                'component': 'config_manager',
                'missing_vars': missing_vars
            })
            
            return AIConfig(
                api_key=os.getenv('AZURE_OPENAI_API_KEY', 'temp'),
                endpoint=os.getenv('AZURE_OPENAI_ENDPOINT', 'https://temp.openai.azure.com'),
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2023-08-01-preview'),
                deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'temp'),
                max_tokens=int(os.getenv('AZURE_OPENAI_MAX_TOKENS', 2000)),
                temperature=float(os.getenv('AZURE_OPENAI_TEMPERATURE', 0.0)),
                timeout=int(os.getenv('AZURE_OPENAI_TIMEOUT', 60))
            )
        
        return AIConfig(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
            deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT'),
            max_tokens=int(os.getenv('AZURE_OPENAI_MAX_TOKENS', 2000)),
            temperature=float(os.getenv('AZURE_OPENAI_TEMPERATURE', 0.0)),
            timeout=int(os.getenv('AZURE_OPENAI_TIMEOUT', 60))
        )
    
    def _load_batch_config(self) -> BatchConfig:
        """Load batch processing configuration"""
        return BatchConfig(
            small_batch_threshold=int(os.getenv('BATCH_SMALL_THRESHOLD', 10)),
            medium_batch_threshold=int(os.getenv('BATCH_MEDIUM_THRESHOLD', 20)),
            large_batch_threshold=int(os.getenv('BATCH_LARGE_THRESHOLD', 30)),
            max_retries=int(os.getenv('BATCH_MAX_RETRIES', 2)),
            retry_delay=float(os.getenv('BATCH_RETRY_DELAY', 2.0)),
            max_columns_per_batch=int(os.getenv('BATCH_MAX_COLUMNS', 15)),
            max_tables_per_batch=int(os.getenv('BATCH_MAX_TABLES', 3)),
            timeout_seconds=int(os.getenv('BATCH_TIMEOUT', 45))
        )
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration"""
        return LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            file_level=os.getenv('LOG_FILE_LEVEL', 'DEBUG'),
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', 10*1024*1024)),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', 5))
        )
    
    def _validate_configuration(self):
        """Validate configuration values"""
        # Validate AI config
        if not self.config.ai_config.endpoint.startswith(('http://', 'https://')):
            raise ValueError("Invalid AI endpoint format")
        
        if self.config.ai_config.max_tokens < 100 or self.config.ai_config.max_tokens > 4000:
            raise ValueError("Max tokens must be between 100 and 4000")
        
        if not 0.0 <= self.config.ai_config.temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        
        # Validate batch config
        if self.config.batch_config.max_retries < 1:
            raise ValueError("Max retries must be at least 1")
        
        main_logger.debug("Configuration validation passed", extra={
            'component': 'config_manager'
        })
    
    def get_config(self) -> PIIConfig:
        """Get the current configuration"""
        if not self.config:
            raise RuntimeError("Configuration not loaded")
        return self.config
    
    def reload_config(self):
        """Reload configuration from sources"""
        main_logger.info("Reloading configuration", extra={
            'component': 'config_manager'
        })
        self._load_configuration()
    
    def get_database_config(self, config_file: str = "db_config.ini") -> Dict[str, Any]:
        """Load database configuration from INI file"""
        try:
            if not Path(config_file).exists():
                main_logger.warning(f"Database config file not found: {config_file}")
                return {}
            
            config_parser = configparser.ConfigParser()
            config_parser.read(config_file)
            
            db_config = {}
            for section in config_parser.sections():
                db_config[section] = dict(config_parser[section])
            
            main_logger.debug("Database configuration loaded", extra={
                'component': 'config_manager',
                'sections': list(db_config.keys())
            })
            
            return db_config
            
        except Exception as e:
            main_logger.error("Failed to load database configuration", extra={
                'component': 'config_manager',
                'error': str(e)
            })
            return {}

# Global configuration instance
config_manager = ConfigurationManager()