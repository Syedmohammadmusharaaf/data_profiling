"""
Common Mixins and Base Classes
============================

Reduces code duplication by providing common functionality
that can be shared across multiple classes.
"""

from typing import Dict, Any
import json
from dataclasses import asdict, is_dataclass


class ToDictMixin:
    """Mixin class providing standardized to_dict() functionality"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary representation"""
        if is_dataclass(self):
            # Handle dataclass objects
            return asdict(self)
        
        # Handle regular classes
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):  # Skip private attributes
                if hasattr(value, 'to_dict'):
                    result[key] = value.to_dict()
                elif hasattr(value, '__dict__'):
                    result[key] = dict(value.__dict__)
                else:
                    result[key] = value
        
        return result
    
    def to_json(self, indent: int = 2) -> str:
        """Convert object to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)


class BaseCommandHandler:
    """Base class for all command handlers to reduce duplication"""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace('CommandHandler', '').lower()
        self.description = f"Handler for {self.name} command"
    
    def execute(self, args) -> int:
        """Execute the command and return exit code"""
        raise NotImplementedError(f"execute() must be implemented in {self.__class__.__name__}")
    
    def setup_parser(self, subparsers):
        """Setup argument parser for this command"""
        raise NotImplementedError(f"setup_parser() must be implemented in {self.__class__.__name__}")
    
    def handle_error(self, error: Exception, context: str = "") -> int:
        """Standardized error handling for all commands"""
        print(f"❌ Error{f' in {context}' if context else ''}: {error}")
        if hasattr(error, '__traceback__'):
            import traceback
            traceback.print_exc()
        return 1
    
    def print_success(self, message: str):
        """Standardized success message"""
        print(f"✅ {message}")
    
    def print_info(self, message: str):
        """Standardized info message"""
        print(f"🔍 {message}")


class BaseService:
    """Base class for all services to standardize initialization and cleanup"""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the service"""
        if self._initialized:
            return True
        
        try:
            self._do_initialize()
            self._initialized = True
            return True
        except Exception as e:
            print(f"❌ Failed to initialize {self.name}: {e}")
            return False
    
    def _do_initialize(self):
        """Override this method in subclasses for actual initialization"""
        pass
    
    def shutdown(self):
        """Cleanup service resources"""
        if self._initialized:
            try:
                self._do_shutdown()
            except Exception as e:
                print(f"⚠️ Error during {self.name} shutdown: {e}")
            finally:
                self._initialized = False
    
    def _do_shutdown(self):
        """Override this method in subclasses for actual cleanup"""
        pass
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized


class BaseEngine:
    """Base class for classification engines"""
    
    def __init__(self, name: str):
        self.name = name
        self.statistics = {
            'classifications_performed': 0,
            'errors_encountered': 0,
            'average_processing_time': 0.0
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return self.statistics.copy()
    
    def reset_statistics(self):
        """Reset engine statistics"""
        self.statistics = {
            'classifications_performed': 0,
            'errors_encountered': 0,
            'average_processing_time': 0.0
        }
    
    def _update_statistics(self, processing_time: float, success: bool = True):
        """Update internal statistics"""
        self.statistics['classifications_performed'] += 1
        if not success:
            self.statistics['errors_encountered'] += 1
        
        # Update average processing time
        current_avg = self.statistics['average_processing_time']
        current_count = self.statistics['classifications_performed']
        self.statistics['average_processing_time'] = (
            (current_avg * (current_count - 1) + processing_time) / current_count
        )


class ConfigurableMixin:
    """Mixin for classes that need configuration management"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._default_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Override this method to provide default configuration"""
        return {}
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback to default"""
        return self.config.get(key, self._default_config.get(key, default))
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration values"""
        self.config.update(updates)
    
    def validate_config(self) -> bool:
        """Validate current configuration - override in subclasses"""
        return True


class LoggingMixin:
    """Mixin for standardized logging functionality"""
    
    def __init__(self):
        self._logger = None
    
    @property
    def logger(self):
        """Get logger instance for this class"""
        if self._logger is None:
            import logging
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    def log_info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def log_error(self, message: str, exception: Exception = None, **kwargs):
        """Log error message"""
        if exception:
            self.logger.error(f"{message}: {exception}", exc_info=True, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)