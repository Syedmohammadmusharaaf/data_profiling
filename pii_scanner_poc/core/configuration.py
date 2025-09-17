#!/usr/bin/env python3
"""
Central Configuration Management Module
Consolidates all system configuration into a unified, type-safe interface
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from dotenv import load_dotenv
from enum import Enum
import json
import logging
from configparser import ConfigParser


class LogLevel(Enum):
    """Enumeration for logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OutputFormat(Enum):
    """Enumeration for output formats"""
    CONSOLE = "console"
    JSON = "json"
    CSV = "csv"
    DETAILED = "detailed"


class Regulation(Enum):
    """Enumeration for privacy regulations"""
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    CCPA = "CCPA"


@dataclass
class AIServiceConfig:
    """Configuration for AI service integration"""
    api_key: str = ""
    api_base: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.1
    timeout: int = 30
    max_retries: int = 3
    enable_caching: bool = True


@dataclass
class DatabaseConfig:
    """Configuration for database connections"""
    connection_string: str = ""
    timeout: int = 30
    max_connections: int = 10
    enable_ssl: bool = True
    charset: str = "utf8mb4"


@dataclass
class AliasConfig:
    """Configuration for alias database"""
    database_path: str = "data/alias_database.db"
    fuzzy_threshold: float = 0.7
    confidence_threshold: float = 0.8
    enable_learning: bool = True
    cache_size: int = 1000


@dataclass
class ProcessingConfig:
    """Configuration for processing parameters"""
    batch_size: int = 50
    max_columns_per_batch: int = 15
    max_tables_per_batch: int = 3
    enable_parallel: bool = True
    max_workers: int = 4
    enable_llm: bool = True
    confidence_threshold: float = 0.7


@dataclass
class LoggingConfig:
    """Configuration for logging system"""
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_structured: bool = True


@dataclass
class OutputConfig:
    """Configuration for output formatting"""
    format: OutputFormat = OutputFormat.CONSOLE
    file_path: Optional[str] = None
    include_metadata: bool = True
    include_statistics: bool = True
    verbosity: int = 1  # 0=minimal, 1=normal, 2=verbose


@dataclass
class SecurityConfig:
    """Configuration for security settings"""
    enable_encryption: bool = True
    encryption_key: Optional[str] = None
    enable_audit_trail: bool = True
    max_session_duration: int = 3600  # 1 hour
    enable_input_validation: bool = True


@dataclass
class SystemConfig:
    """Master configuration class containing all subsystem configurations"""
    
    # Core configurations
    ai_service: AIServiceConfig = field(default_factory=AIServiceConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    alias: AliasConfig = field(default_factory=AliasConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Runtime settings
    project_root: str = "/app/pii_scanner_poc"
    debug_mode: bool = False
    version: str = "2.0.0"
    
    # Default regulations
    default_regulations: List[Regulation] = field(default_factory=lambda: [Regulation.GDPR])
    
    # Session settings
    session_id: Optional[str] = None
    company_id: Optional[str] = None
    region: Optional[str] = None


class ConfigurationManager:
    """
    Central configuration manager with hierarchical loading and validation
    """
    
    def __init__(self, config_dir: str = "/app/pii_scanner_poc"):
        self.config_dir = Path(config_dir)
        self._config: Optional[SystemConfig] = None
        self._logger = logging.getLogger(__name__)
    
    def load_configuration(self, 
                          env_file: Optional[str] = None,
                          config_file: Optional[str] = None,
                          **overrides) -> SystemConfig:
        """
        Load configuration with hierarchical precedence:
        1. Default values (dataclass defaults)
        2. Configuration files (.env, config.ini)
        3. Environment variables
        4. Command-line overrides
        
        Args:
            env_file: Path to .env file
            config_file: Path to configuration file
            **overrides: Direct configuration overrides
            
        Returns:
            SystemConfig: Validated system configuration
        """
        
        # Start with default configuration
        config = SystemConfig()
        
        # Load from .env file
        env_path = env_file or self.config_dir / ".env"
        if env_path and Path(env_path).exists():
            # Load .env file into environment variables
            load_dotenv(env_path)
            config = self._load_env_config(config, env_path)
        
        # Load from configuration file
        if config_file and Path(config_file).exists():
            config = self._load_file_config(config, config_file)
        
        # Override with environment variables
        config = self._load_env_variables(config)
        
        # Apply direct overrides
        config = self._apply_overrides(config, overrides)
        
        # Validate configuration
        self._validate_configuration(config)
        
        # Cache the configuration
        self._config = config
        
        self._logger.info("Configuration loaded successfully")
        return config
    
    def _load_env_config(self, config: SystemConfig, env_file: str) -> SystemConfig:
        """Load configuration from .env file"""
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        
                        # Map environment variables to config attributes
                        self._set_config_value(config, key, value)
                        
        except Exception as e:
            self._logger.warning(f"Error loading .env file {env_file}: {e}")
        
        return config
    
    def _load_file_config(self, config: SystemConfig, config_file: str) -> SystemConfig:
        """Load configuration from INI or JSON file"""
        try:
            file_path = Path(config_file)
            
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self._apply_dict_config(config, data)
            
            elif file_path.suffix.lower() in ['.ini', '.cfg']:
                parser = ConfigParser()
                parser.read(file_path)
                
                for section in parser.sections():
                    for key, value in parser.items(section):
                        full_key = f"{section}.{key}"
                        self._set_config_value(config, full_key, value)
                        
        except Exception as e:
            self._logger.warning(f"Error loading config file {config_file}: {e}")
        
        return config
    
    def _load_env_variables(self, config: SystemConfig) -> SystemConfig:
        """Load configuration from environment variables"""
        
        # AI Service configuration
        if os.getenv('AZURE_OPENAI_API_KEY'):
            config.ai_service.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        if os.getenv('AZURE_OPENAI_ENDPOINT'):
            config.ai_service.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
        if os.getenv('AZURE_OPENAI_MODEL'):
            config.ai_service.model = os.getenv('AZURE_OPENAI_MODEL')
        if os.getenv('AZURE_OPENAI_DEPLOYMENT'):
            config.ai_service.model = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        if os.getenv('AZURE_OPENAI_TIMEOUT'):
            config.ai_service.timeout = int(os.getenv('AZURE_OPENAI_TIMEOUT'))
        if os.getenv('AZURE_OPENAI_MAX_TOKENS'):
            config.ai_service.max_tokens = int(os.getenv('AZURE_OPENAI_MAX_TOKENS'))
        if os.getenv('AZURE_OPENAI_TEMPERATURE'):
            config.ai_service.temperature = float(os.getenv('AZURE_OPENAI_TEMPERATURE'))
        
        # Database configuration
        if os.getenv('DATABASE_URL'):
            config.database.connection_string = os.getenv('DATABASE_URL')
        
        # Processing configuration
        if os.getenv('BATCH_SIZE'):
            config.processing.batch_size = int(os.getenv('BATCH_SIZE'))
        if os.getenv('ENABLE_LLM'):
            config.processing.enable_llm = os.getenv('ENABLE_LLM').lower() == 'true'
        
        # Logging configuration
        if os.getenv('LOG_LEVEL'):
            config.logging.level = LogLevel(os.getenv('LOG_LEVEL').upper())
        
        # Debug mode
        if os.getenv('DEBUG'):
            config.debug_mode = os.getenv('DEBUG').lower() == 'true'
        
        return config
    
    def _apply_overrides(self, config: SystemConfig, overrides: Dict[str, Any]) -> SystemConfig:
        """Apply direct configuration overrides"""
        for key, value in overrides.items():
            self._set_config_value(config, key, value)
        return config
    
    def _apply_dict_config(self, config: SystemConfig, data: Dict[str, Any]) -> None:
        """Apply configuration from dictionary (for JSON files)"""
        for key, value in data.items():
            if isinstance(value, dict):
                # Handle nested configuration
                for subkey, subvalue in value.items():
                    full_key = f"{key}.{subkey}"
                    self._set_config_value(config, full_key, subvalue)
            else:
                self._set_config_value(config, key, value)
    
    def _set_config_value(self, config: SystemConfig, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        try:
            # Handle nested keys (e.g., "ai_service.api_key")
            parts = key.lower().split('.')
            
            if len(parts) == 1:
                # Top-level attribute
                if hasattr(config, parts[0]):
                    setattr(config, parts[0], self._convert_value(value))
            
            elif len(parts) == 2:
                # Nested attribute (e.g., ai_service.api_key)
                section, attr = parts
                if hasattr(config, section):
                    section_obj = getattr(config, section)
                    if hasattr(section_obj, attr):
                        setattr(section_obj, attr, self._convert_value(value))
                        
        except Exception as e:
            self._logger.warning(f"Error setting config value {key}={value}: {e}")
    
    def _convert_value(self, value: str) -> Any:
        """Convert string values to appropriate types"""
        if isinstance(value, str):
            # Boolean conversion
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            
            # Integer conversion
            try:
                return int(value)
            except ValueError:
                pass
            
            # Float conversion
            try:
                return float(value)
            except ValueError:
                pass
        
        return value
    
    def _validate_configuration(self, config: SystemConfig) -> None:
        """
        Validate configuration values and ensure they are within acceptable bounds.
        
        This method performs comprehensive validation of all configuration parameters:
        - AI service settings (with graceful fallback for missing API keys)
        - Batch processing parameters
        - Confidence thresholds
        - File paths and directories
        
        Args:
            config: SystemConfig object to validate
            
        Raises:
            ValueError: When configuration values are invalid or out of bounds
            
        Note:
            For AI service validation, we now allow graceful fallback when LLM is enabled
            but no API key is provided - the system will disable LLM mode automatically.
        """
        
        # Validate AI service configuration with graceful fallback
        if config.processing.enable_llm and not config.ai_service.api_key:
            # Instead of raising an error, disable LLM mode and log a warning
            config.processing.enable_llm = False
            logging.warning(
                "LLM mode requested but no API key provided. Disabling LLM mode and falling back to local-only classification.",
                extra={'component': 'configuration', 'fallback_mode': 'local_only'}
            )
        
        # Validate batch sizes
        if config.processing.batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        if config.processing.max_columns_per_batch <= 0:
            raise ValueError("Max columns per batch must be positive")
        
        # Validate thresholds
        if not 0 <= config.processing.confidence_threshold <= 1:
            raise ValueError("Confidence threshold must be between 0 and 1")
        
        if not 0 <= config.alias.fuzzy_threshold <= 1:
            raise ValueError("Fuzzy threshold must be between 0 and 1")
        
        # Validate paths
        project_path = Path(config.project_root)
        if not project_path.exists():
            self._logger.warning(f"Project root does not exist: {config.project_root}")
        
        # Create alias database directory if needed
        alias_path = Path(config.alias.database_path)
        alias_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_config(self) -> SystemConfig:
        """Get the current configuration"""
        if self._config is None:
            self._config = self.load_configuration()
        return self._config
    
    def reload_configuration(self, **overrides) -> SystemConfig:
        """Reload configuration with optional overrides"""
        self._config = None
        return self.load_configuration(**overrides)
    
    def export_configuration(self, file_path: str, format: str = "json") -> None:
        """Export current configuration to file"""
        config = self.get_config()
        
        if format.lower() == "json":
            self._export_json(config, file_path)
        elif format.lower() == "ini":
            self._export_ini(config, file_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, config: SystemConfig, file_path: str) -> None:
        """Export configuration as JSON"""
        # Convert dataclass to dictionary
        config_dict = self._dataclass_to_dict(config)
        
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    def _export_ini(self, config: SystemConfig, file_path: str) -> None:
        """Export configuration as INI file"""
        parser = ConfigParser()
        
        # Convert dataclass to INI sections
        config_dict = self._dataclass_to_dict(config)
        
        for section, values in config_dict.items():
            if isinstance(values, dict):
                parser.add_section(section)
                for key, value in values.items():
                    parser.set(section, key, str(value))
        
        with open(file_path, 'w') as f:
            parser.write(f)
    
    def _dataclass_to_dict(self, obj) -> Dict[str, Any]:
        """Convert dataclass to dictionary recursively"""
        if hasattr(obj, '__dataclass_fields__'):
            result = {}
            for field_name, field_def in obj.__dataclass_fields__.items():
                value = getattr(obj, field_name)
                if hasattr(value, '__dataclass_fields__'):
                    result[field_name] = self._dataclass_to_dict(value)
                elif isinstance(value, Enum):
                    result[field_name] = value.value
                elif isinstance(value, list):
                    result[field_name] = [item.value if isinstance(item, Enum) else item for item in value]
                else:
                    result[field_name] = value
            return result
        return obj


# Global configuration manager instance with proper .env path
import os
config_manager = ConfigurationManager(config_dir=os.path.join(os.path.dirname(__file__), '..'))

# Convenience functions for accessing configuration
def get_config() -> SystemConfig:
    """Get the current system configuration"""
    return config_manager.get_config()

def reload_config(**overrides) -> SystemConfig:
    """Reload system configuration with optional overrides"""
    return config_manager.reload_configuration(**overrides)

def load_config(env_file: Optional[str] = None, 
                config_file: Optional[str] = None, 
                **overrides) -> SystemConfig:
    """Load system configuration"""
    return config_manager.load_configuration(env_file, config_file, **overrides)