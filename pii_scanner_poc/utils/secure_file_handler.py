#!/usr/bin/env python3
"""
Secure File Handling Utilities for PII/PHI Scanner POC
Provides secure file operations with proper encoding and error handling
"""

import os
import json
import csv
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, IO
from contextlib import contextmanager

from pii_scanner_poc.core.exceptions import (
    InvalidFileFormatError, SecurityError, PIIScannerBaseException
)
from pii_scanner_poc.utils.security_integration import security_manager


class SecureFileHandler:
    """
    Secure file handling with proper encoding, validation, and error handling
    """
    
    ALLOWED_EXTENSIONS = {
        'text': ['.txt', '.log', '.ddl', '.sql'],
        'data': ['.json', '.csv', '.xml'],
        'config': ['.ini', '.conf', '.cfg', '.env'],
        'temp': ['.tmp', '.temp']
    }
    
    DEFAULT_ENCODING = 'utf-8'
    SAFE_FILE_PERMISSIONS = 0o644  # Read/write for owner, read for group/others
    SECURE_FILE_PERMISSIONS = 0o600  # Read/write for owner only
    
    def __init__(self, enforce_security: bool = True):
        self.enforce_security = enforce_security
        self._temp_files = []  # Track temporary files for cleanup
    
    def validate_file_path(self, file_path: Union[str, Path]) -> Path:
        """
        Validate file path for security and accessibility
        
        Args:
            file_path: File path to validate
            
        Returns:
            Validated Path object
            
        Raises:
            SecurityError: If path is unsafe
            InvalidFileFormatError: If file type is not allowed
        """
        path = Path(file_path)
        
        # Check for path traversal attempts
        try:
            resolved_path = path.resolve()
            if '..' in str(path) or str(resolved_path) != str(path.resolve()):
                raise SecurityError(
                    f"Path traversal detected in file path: {file_path}",
                    component="file_handler"
                ).add_context('attempted_path', str(file_path))
        except Exception as e:
            if isinstance(e, PIIScannerBaseException):
                raise
            raise SecurityError(
                f"Invalid file path: {file_path}",
                component="file_handler"
            ).add_context('path_error', str(e))
        
        # Validate file extension if enforcing security
        if self.enforce_security and path.suffix:
            allowed = False
            for extensions in self.ALLOWED_EXTENSIONS.values():
                if path.suffix.lower() in extensions:
                    allowed = True
                    break
            
            if not allowed:
                raise InvalidFileFormatError(
                    f"File extension '{path.suffix}' is not allowed",
                    supported_formats=sum(self.ALLOWED_EXTENSIONS.values(), [])
                ).add_context('file_path', str(file_path))
        
        # Log file access attempt
        security_manager.log_access_attempt(
            resource=f"file:{resolved_path}",
            user_id="system",
            success=True,
            additional_context={
                'operation': 'file_validation',
                'file_type': path.suffix,
                'file_size': path.stat().st_size if path.exists() else 0
            }
        )
        
        return resolved_path
    
    @contextmanager
    def secure_open(self,
                   file_path: Union[str, Path],
                   mode: str = 'r',
                   encoding: str = None,
                   secure: bool = False):
        """
        Securely open a file with proper encoding and error handling
        
        Args:
            file_path: Path to file
            mode: File opening mode
            encoding: File encoding (defaults to utf-8)
            secure: Whether to use secure permissions
            
        Yields:
            File handle
            
        Raises:
            SecurityError: If file operations are unsafe
            InvalidFileFormatError: If file cannot be opened
        """
        validated_path = self.validate_file_path(file_path)
        encoding = encoding or self.DEFAULT_ENCODING
        
        # Set appropriate permissions for new files
        permissions = self.SECURE_FILE_PERMISSIONS if secure else self.SAFE_FILE_PERMISSIONS
        
        try:
            # Ensure parent directory exists
            validated_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Open file with proper encoding
            file_handle = open(validated_path, mode, encoding=encoding, newline='')
            
            # Set file permissions if creating a new file
            if 'w' in mode or 'a' in mode:
                os.chmod(validated_path, permissions)
            
            try:
                yield file_handle
            finally:
                file_handle.close()
                
                # Log file operation
                security_manager.log_access_attempt(
                    resource=f"file:{validated_path}",
                    user_id="system",
                    success=True,
                    additional_context={
                        'operation': f'file_{mode}',
                        'encoding': encoding,
                        'secure_permissions': secure
                    }
                )
                
        except Exception as e:
            security_manager.log_access_attempt(
                resource=f"file:{validated_path}",
                user_id="system",
                success=False,
                additional_context={
                    'operation': f'file_{mode}',
                    'error': str(e)
                }
            )
            
            if isinstance(e, PIIScannerBaseException):
                raise
            elif isinstance(e, (PermissionError, OSError)):
                raise SecurityError(
                    f"File access denied: {validated_path}",
                    component="file_handler"
                ).add_context('original_error', str(e))
            else:
                raise InvalidFileFormatError(
                    f"Cannot open file: {validated_path}",
                    supported_formats=[]
                ).add_context('open_error', str(e))
    
    def read_text_file(self, file_path: Union[str, Path], encoding: str = None) -> str:
        """
        Securely read a text file
        
        Args:
            file_path: Path to text file
            encoding: File encoding
            
        Returns:
            File contents as string
        """
        with self.secure_open(file_path, 'r', encoding) as f:
            return f.read()
    
    def write_text_file(self,
                       file_path: Union[str, Path],
                       content: str,
                       encoding: str = None,
                       secure: bool = False) -> None:
        """
        Securely write content to a text file
        
        Args:
            file_path: Path to text file
            content: Content to write
            encoding: File encoding
            secure: Whether to use secure permissions
        """
        with self.secure_open(file_path, 'w', encoding, secure) as f:
            f.write(content)
        
        # Log data processing
        security_manager.log_data_processing(
            operation='file_write',
            data_type='text',
            record_count=len(content.splitlines()),
            additional_context={
                'file_path': str(file_path),
                'content_length': len(content),
                'secure': secure
            }
        )
    
    def read_json_file(self, file_path: Union[str, Path], encoding: str = None) -> Any:
        """
        Securely read a JSON file
        
        Args:
            file_path: Path to JSON file
            encoding: File encoding
            
        Returns:
            Parsed JSON data
            
        Raises:
            InvalidFileFormatError: If JSON is invalid
        """
        try:
            with self.secure_open(file_path, 'r', encoding) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidFileFormatError(
                f"Invalid JSON in file: {file_path}",
                supported_formats=['.json']
            ).add_context('json_error', str(e))
    
    def write_json_file(self,
                       file_path: Union[str, Path],
                       data: Any,
                       encoding: str = None,
                       secure: bool = False,
                       indent: int = 2) -> None:
        """
        Securely write data to a JSON file
        
        Args:
            file_path: Path to JSON file
            data: Data to write
            encoding: File encoding
            secure: Whether to use secure permissions
            indent: JSON indentation
        """
        with self.secure_open(file_path, 'w', encoding, secure) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        # Log data processing
        record_count = 1
        if isinstance(data, (list, tuple)):
            record_count = len(data)
        elif isinstance(data, dict):
            record_count = len(data)
        
        security_manager.log_data_processing(
            operation='json_write',
            data_type='json',
            record_count=record_count,
            additional_context={
                'file_path': str(file_path),
                'secure': secure
            }
        )
    
    def read_csv_file(self,
                     file_path: Union[str, Path],
                     encoding: str = None,
                     delimiter: str = ',') -> List[Dict[str, str]]:
        """
        Securely read a CSV file
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding
            delimiter: CSV delimiter
            
        Returns:
            List of dictionaries representing CSV rows
        """
        rows = []
        try:
            with self.secure_open(file_path, 'r', encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = list(reader)
        except Exception as e:
            raise InvalidFileFormatError(
                f"Cannot read CSV file: {file_path}",
                supported_formats=['.csv']
            ).add_context('csv_error', str(e))
        
        # Log data processing
        security_manager.log_data_processing(
            operation='csv_read',
            data_type='csv',
            record_count=len(rows),
            additional_context={
                'file_path': str(file_path),
                'delimiter': delimiter
            }
        )
        
        return rows
    
    def write_csv_file(self,
                      file_path: Union[str, Path],
                      data: List[Dict[str, Any]],
                      encoding: str = None,
                      secure: bool = False,
                      delimiter: str = ',') -> None:
        """
        Securely write data to a CSV file
        
        Args:
            file_path: Path to CSV file
            data: List of dictionaries to write
            encoding: File encoding
            secure: Whether to use secure permissions
            delimiter: CSV delimiter
        """
        if not data:
            raise InvalidFileFormatError(
                "Cannot write empty data to CSV file",
                supported_formats=['.csv']
            )
        
        fieldnames = list(data[0].keys())
        
        with self.secure_open(file_path, 'w', encoding, secure) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(data)
        
        # Log data processing
        security_manager.log_data_processing(
            operation='csv_write',
            data_type='csv',
            record_count=len(data),
            additional_context={
                'file_path': str(file_path),
                'fields': fieldnames,
                'secure': secure
            }
        )
    
    @contextmanager
    def create_temp_file(self,
                        suffix: str = '.tmp',
                        prefix: str = 'piiscan_',
                        dir: Optional[str] = None,
                        secure: bool = True):
        """
        Create a secure temporary file
        
        Args:
            suffix: File suffix
            prefix: File prefix
            dir: Directory for temp file
            secure: Whether to use secure permissions
            
        Yields:
            Temporary file path
        """
        temp_fd = None
        temp_path = None
        
        try:
            # Create temporary file
            temp_fd, temp_path_str = tempfile.mkstemp(
                suffix=suffix,
                prefix=prefix,
                dir=dir
            )
            temp_path = Path(temp_path_str)
            
            # Set secure permissions
            permissions = self.SECURE_FILE_PERMISSIONS if secure else self.SAFE_FILE_PERMISSIONS
            os.chmod(temp_path, permissions)
            
            # Close the file descriptor, we'll use our secure_open
            os.close(temp_fd)
            temp_fd = None
            
            # Track for cleanup
            self._temp_files.append(temp_path)
            
            # Log temp file creation
            security_manager.log_security_event(
                'temp_file_created',
                f"Temporary file created: {temp_path}",
                additional_data={
                    'temp_path': str(temp_path),
                    'secure': secure
                }
            )
            
            yield temp_path
            
        finally:
            # Cleanup
            if temp_fd is not None:
                try:
                    os.close(temp_fd)
                except:
                    pass
            
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                    if temp_path in self._temp_files:
                        self._temp_files.remove(temp_path)
                except Exception as e:
                    # Log cleanup failure but don't raise
                    security_manager.security_logger.log_security_event(
                        'temp_file_cleanup_failed',
                        f"Failed to cleanup temporary file: {temp_path}",
                        additional_data={'error': str(e)}
                    )
    
    def cleanup_temp_files(self):
        """Clean up any remaining temporary files"""
        for temp_path in self._temp_files.copy():
            try:
                if temp_path.exists():
                    temp_path.unlink()
                self._temp_files.remove(temp_path)
            except Exception as e:
                security_manager.security_logger.log_security_event(
                    'temp_file_cleanup_failed',
                    f"Failed to cleanup temporary file: {temp_path}",
                    additional_data={'error': str(e)}
                )
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.cleanup_temp_files()


# Global secure file handler instance
secure_file_handler = SecureFileHandler()


if __name__ == "__main__":
    # Test secure file operations
    import tempfile
    import os
    
    # Test text file operations
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.txt"
        
        # Write and read text
        secure_file_handler.write_text_file(test_file, "Hello, World!")
        content = secure_file_handler.read_text_file(test_file)
        print(f"Text content: {content}")
        
        # Test JSON operations
        json_file = Path(temp_dir) / "test.json"
        test_data = {"message": "Hello, JSON!", "numbers": [1, 2, 3]}
        
        secure_file_handler.write_json_file(json_file, test_data)
        loaded_data = secure_file_handler.read_json_file(json_file)
        print(f"JSON data: {loaded_data}")
        
        # Test CSV operations
        csv_file = Path(temp_dir) / "test.csv"
        csv_data = [
            {"name": "Alice", "age": "30"},
            {"name": "Bob", "age": "25"}
        ]
        
        secure_file_handler.write_csv_file(csv_file, csv_data)
        loaded_csv = secure_file_handler.read_csv_file(csv_file)
        print(f"CSV data: {loaded_csv}")
        
        print("All file operations completed successfully!")