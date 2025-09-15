"""
Enterprise Configuration Manager
Centralized configuration management for PII/PHI Scanner
"""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration"""
    mongo_url: str = "mongodb://localhost:27017/pii_scanner"
    database_name: str = "pii_scanner"
    connection_timeout: int = 10000
    max_pool_size: int = 10

@dataclass
class APIConfig:
    """API configuration"""
    host: str = "0.0.0.0"
    port: int = 8001
    prefix: str = "/api"
    debug: bool = True
    cors_origins: List[str] = None

@dataclass
class ScannerConfig:
    """Scanner configuration"""
    confidence_threshold: float = 0.75
    fuzzy_threshold: float = 0.80
    high_confidence_threshold: float = 0.90
    certainty_threshold: float = 0.95
    max_workers: int = 4
    batch_size: int = 100
    enable_multithreading: bool = True
    thread_pool_size: int = 8
    classification_timeout: int = 120

@dataclass
class AIConfig:
    """AI service configuration"""
    enable_ai_classification: bool = True
    ai_fallback_only: bool = True
    ai_confidence_boost: float = 0.1
    max_ai_requests_per_minute: int = 100
    ai_request_timeout: int = 30

@dataclass
class FileConfig:
    """File processing configuration"""
    max_file_size: int = 52428800  # 50MB
    temp_dir: str = "./temp"
    allowed_extensions: List[str] = None
    max_tables_per_file: int = 1000
    max_columns_per_table: int = 500

@dataclass
class CacheConfig:
    """Cache configuration"""
    enable_file_cache: bool = True
    cache_directory: str = "./cache"
    cache_ttl: int = 3600
    schema_cache_enabled: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file: str = "./logs/pii_scanner.log"
    max_size: int = 10485760
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self, env_file: Optional[str] = None):
        if env_file and os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        self.database = self._load_database_config()
        self.api = self._load_api_config()
        self.scanner = self._load_scanner_config()
        self.ai = self._load_ai_config()
        self.file = self._load_file_config()
        self.cache = self._load_cache_config()
        self.logging = self._load_logging_config()
    
    def _get_env_bool(self, key: str, default: bool) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _get_env_int(self, key: str, default: int) -> int:
        """Get integer environment variable"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def _get_env_float(self, key: str, default: float) -> float:
        """Get float environment variable"""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    def _get_env_list(self, key: str, default: List[str]) -> List[str]:
        """Get list environment variable"""
        value = os.getenv(key)
        if value:
            return [item.strip() for item in value.split(',')]
        return default or []
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        return DatabaseConfig(
            mongo_url=os.getenv('MONGO_URL', 'mongodb://localhost:27017/pii_scanner'),
            database_name=os.getenv('MONGO_DATABASE', 'pii_scanner'),
            connection_timeout=self._get_env_int('MONGO_CONNECTION_TIMEOUT', 10000),
            max_pool_size=self._get_env_int('MONGO_MAX_POOL_SIZE', 10)
        )
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration"""
        cors_origins_default = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://pii-dashboard.preview.emergentagent.com"
        ]
        
        return APIConfig(
            host=os.getenv('API_HOST', '0.0.0.0'),
            port=self._get_env_int('API_PORT', 8001),
            prefix=os.getenv('API_PREFIX', '/api'),
            debug=self._get_env_bool('DEBUG', True),
            cors_origins=self._get_env_list('CORS_ORIGINS', cors_origins_default)
        )
    
    def _load_scanner_config(self) -> ScannerConfig:
        """Load scanner configuration"""
        return ScannerConfig(
            confidence_threshold=self._get_env_float('CONFIDENCE_THRESHOLD', 0.75),
            fuzzy_threshold=self._get_env_float('FUZZY_THRESHOLD', 0.80),
            high_confidence_threshold=self._get_env_float('HIGH_CONFIDENCE_THRESHOLD', 0.90),
            certainty_threshold=self._get_env_float('CERTAINTY_THRESHOLD', 0.95),
            max_workers=self._get_env_int('MAX_WORKERS', 4),
            batch_size=self._get_env_int('BATCH_SIZE', 100),
            enable_multithreading=self._get_env_bool('ENABLE_MULTITHREADING', True),
            thread_pool_size=self._get_env_int('THREAD_POOL_SIZE', 8),
            classification_timeout=self._get_env_int('CLASSIFICATION_TIMEOUT', 120)
        )
    
    def _load_ai_config(self) -> AIConfig:
        """Load AI configuration"""
        return AIConfig(
            enable_ai_classification=self._get_env_bool('ENABLE_AI_CLASSIFICATION', True),
            ai_fallback_only=self._get_env_bool('AI_FALLBACK_ONLY', True),
            ai_confidence_boost=self._get_env_float('AI_CONFIDENCE_BOOST', 0.1),
            max_ai_requests_per_minute=self._get_env_int('MAX_AI_REQUESTS_PER_MINUTE', 100),
            ai_request_timeout=self._get_env_int('AI_REQUEST_TIMEOUT', 30)
        )
    
    def _load_file_config(self) -> FileConfig:
        """Load file configuration"""
        allowed_extensions_default = ['.sql', '.ddl', '.txt', '.json', '.csv', '.xlsx']
        
        return FileConfig(
            max_file_size=self._get_env_int('MAX_FILE_SIZE', 52428800),
            temp_dir=os.getenv('TEMP_DIR', './temp'),
            allowed_extensions=self._get_env_list('ALLOWED_EXTENSIONS', allowed_extensions_default),
            max_tables_per_file=self._get_env_int('MAX_TABLES_PER_FILE', 1000),
            max_columns_per_table=self._get_env_int('MAX_COLUMNS_PER_TABLE', 500)
        )
    
    def _load_cache_config(self) -> CacheConfig:
        """Load cache configuration"""
        return CacheConfig(
            enable_file_cache=self._get_env_bool('ENABLE_FILE_CACHE', True),
            cache_directory=os.getenv('CACHE_DIRECTORY', './cache'),
            cache_ttl=self._get_env_int('CACHE_TTL', 3600),
            schema_cache_enabled=self._get_env_bool('SCHEMA_CACHE_ENABLED', True)
        )
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration"""
        return LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            file=os.getenv('LOG_FILE', './logs/pii_scanner.log'),
            max_size=self._get_env_int('LOG_MAX_SIZE', 10485760),
            backup_count=self._get_env_int('LOG_BACKUP_COUNT', 5),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            'database': self.database.__dict__,
            'api': self.api.__dict__,
            'scanner': self.scanner.__dict__,
            'ai': self.ai.__dict__,
            'file': self.file.__dict__,
            'cache': self.cache.__dict__,
            'logging': self.logging.__dict__
        }
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Validate required directories
        Path(self.file.temp_dir).mkdir(parents=True, exist_ok=True)
        Path(self.cache.cache_directory).mkdir(parents=True, exist_ok=True)
        Path(os.path.dirname(self.logging.file)).mkdir(parents=True, exist_ok=True)
        
        # Validate thresholds
        if not 0 <= self.scanner.confidence_threshold <= 1:
            errors.append("confidence_threshold must be between 0 and 1")
        
        if not 0 <= self.scanner.fuzzy_threshold <= 1:
            errors.append("fuzzy_threshold must be between 0 and 1")
        
        if self.scanner.max_workers <= 0:
            errors.append("max_workers must be greater than 0")
        
        if self.file.max_file_size <= 0:
            errors.append("max_file_size must be greater than 0")
        
        return errors

# Global configuration instance
config = ConfigManager()

# Validation on import
config_errors = config.validate_config()
if config_errors:
    print("Configuration errors found:")
    for error in config_errors:
        print(f"  - {error}")