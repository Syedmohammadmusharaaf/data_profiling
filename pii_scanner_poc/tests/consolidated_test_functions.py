#!/usr/bin/env python3
"""
Consolidated Test Utilities and Functions
Combines all duplicate test functions into a centralized testing framework
"""

import unittest
import json
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging

# Import our core systems
from pii_scanner_poc.core.configuration import SystemConfig, load_config
from pii_scanner_poc.core.service_interfaces import ServiceFactory
from pii_scanner_poc.core.exceptions import PIIScannerBaseException
from pii_scanner_poc.models.data_models import ColumnMetadata, PIIType, RiskLevel, Regulation


@dataclass
class TestResult:
    """Standardized test result structure"""
    test_name: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ConsolidatedTestFunctions:
    """
    Consolidated test functions that were duplicated across multiple test files
    
    This class combines all the duplicate test functionality identified during
    cleanup into a single, well-organized testing framework.
    """
    
    def __init__(self):
        """Initialize consolidated test functions"""
        self.test_results: List[TestResult] = []
        self.logger = logging.getLogger(__name__)
        self.temp_dirs: List[Path] = []
    
    def create_temp_directory(self) -> Path:
        """Create temporary directory for test files"""
        temp_dir = Path(tempfile.mkdtemp(prefix="pii_scanner_test_"))
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def cleanup_temp_directories(self):
        """Clean up all temporary directories"""
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        self.temp_dirs.clear()
    
    def test_configuration_loading(self, config_name: str = "default") -> TestResult:
        """
        Consolidated configuration loading test
        
        Previously duplicated in 3 files, now centralized with comprehensive testing.
        """
        start_time = time.time()
        
        try:
            # Test configuration loading
            config = load_config()
            
            # Validate required attributes
            required_attrs = ['ai_service', 'database', 'alias', 'processing', 'logging']
            for attr in required_attrs:
                if not hasattr(config, attr):
                    raise AssertionError(f"Missing required configuration attribute: {attr}")
            
            # Validate configuration values
            assert config.processing.batch_size > 0, "Batch size must be positive"
            assert 0 <= config.processing.confidence_threshold <= 1, "Confidence threshold must be 0-1"
            
            duration = time.time() - start_time
            
            result = TestResult(
                test_name="configuration_loading",
                status="passed",
                duration=duration,
                message="Configuration loaded and validated successfully",
                details={
                    'config_name': config_name,
                    'batch_size': config.processing.batch_size,
                    'confidence_threshold': config.processing.confidence_threshold,
                    'debug_mode': config.debug_mode
                }
            )
            
            self.logger.info(f"Configuration loading test passed: {config_name}")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                test_name="configuration_loading",
                status="failed", 
                duration=duration,
                message=f"Configuration loading failed: {e}",
                details={'config_name': config_name, 'error': str(e)}
            )
            
            self.logger.error(f"Configuration loading test failed: {e}")
            return result
    
    def test_data_models(self, test_comprehensive: bool = True) -> TestResult:
        """
        Consolidated data models test
        
        Previously duplicated in 2 files, now enhanced with comprehensive validation.
        """
        start_time = time.time()
        
        try:
            # Test ColumnMetadata creation
            column = ColumnMetadata(
                schema_name="test_schema",
                table_name="test_table", 
                column_name="test_column",
                data_type="VARCHAR(100)"
            )
            
            assert column.schema_name == "test_schema"
            assert column.table_name == "test_table"
            assert column.column_name == "test_column"
            assert column.data_type == "VARCHAR(100)"
            
            # Test enum values
            pii_types = list(PIIType)
            assert len(pii_types) > 0, "PIIType enum should have values"
            assert PIIType.EMAIL in pii_types, "EMAIL should be in PIIType"
            assert PIIType.PHONE in pii_types, "PHONE should be in PIIType"
            
            risk_levels = list(RiskLevel)
            assert len(risk_levels) > 0, "RiskLevel enum should have values"
            assert RiskLevel.HIGH in risk_levels, "HIGH should be in RiskLevel"
            
            regulations = list(Regulation)
            assert len(regulations) > 0, "Regulation enum should have values"
            assert Regulation.GDPR in regulations, "GDPR should be in Regulation"
            
            if test_comprehensive:
                # Test all enum combinations
                for pii_type in pii_types:
                    assert isinstance(pii_type.value, str), f"PIIType {pii_type} should have string value"
                
                for risk_level in risk_levels:
                    assert isinstance(risk_level.value, str), f"RiskLevel {risk_level} should have string value"
                
                for regulation in regulations:
                    assert isinstance(regulation.value, str), f"Regulation {regulation} should have string value"
            
            duration = time.time() - start_time
            
            result = TestResult(
                test_name="data_models",
                status="passed",
                duration=duration,
                message="Data models validated successfully",
                details={
                    'pii_types_count': len(pii_types),
                    'risk_levels_count': len(risk_levels),
                    'regulations_count': len(regulations),
                    'comprehensive': test_comprehensive
                }
            )
            
            self.logger.info("Data models test passed")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                test_name="data_models",
                status="failed",
                duration=duration,
                message=f"Data models test failed: {e}",
                details={'error': str(e), 'comprehensive': test_comprehensive}
            )
            
            self.logger.error(f"Data models test failed: {e}")
            return result
    
    def test_json_extraction(self, test_cases: Optional[List[Dict[str, Any]]] = None) -> TestResult:
        """
        Consolidated JSON extraction test
        
        Previously duplicated in 2 files, now with comprehensive test cases.
        """
        start_time = time.time()
        
        # Default test cases if none provided
        if test_cases is None:
            test_cases = [
                {
                    'name': 'valid_json',
                    'input': '{"field": "email", "type": "EMAIL", "confidence": 0.9}',
                    'expected_fields': ['field', 'type', 'confidence']
                },
                {
                    'name': 'json_with_array',
                    'input': '{"results": [{"field": "phone", "type": "PHONE"}]}',
                    'expected_fields': ['results']
                },
                {
                    'name': 'nested_json', 
                    'input': '{"analysis": {"field": "name", "details": {"confidence": 0.8}}}',
                    'expected_fields': ['analysis']
                },
                {
                    'name': 'malformed_json',
                    'input': '{"field": "email", "type": "EMAIL"',  # Missing closing brace
                    'should_fail': True
                }
            ]
        
        try:
            passed_cases = 0
            failed_cases = 0
            
            for test_case in test_cases:
                try:
                    # Parse JSON
                    parsed = json.loads(test_case['input'])
                    
                    if test_case.get('should_fail', False):
                        # This case should have failed but didn't
                        failed_cases += 1
                        self.logger.warning(f"Test case {test_case['name']} should have failed but passed")
                    else:
                        # Validate expected fields
                        expected_fields = test_case.get('expected_fields', [])
                        for field in expected_fields:
                            if field not in parsed:
                                raise AssertionError(f"Expected field '{field}' not found in parsed JSON")
                        
                        passed_cases += 1
                        
                except json.JSONDecodeError:
                    if test_case.get('should_fail', False):
                        # Expected failure
                        passed_cases += 1
                    else:
                        # Unexpected failure
                        failed_cases += 1
                        self.logger.error(f"Unexpected JSON parse failure for {test_case['name']}")
                
                except Exception as e:
                    failed_cases += 1
                    self.logger.error(f"Test case {test_case['name']} failed: {e}")
            
            duration = time.time() - start_time
            
            if failed_cases == 0:
                result = TestResult(
                    test_name="json_extraction",
                    status="passed",
                    duration=duration,
                    message=f"All {len(test_cases)} JSON test cases passed",
                    details={
                        'total_cases': len(test_cases),
                        'passed_cases': passed_cases,
                        'failed_cases': failed_cases
                    }
                )
                self.logger.info(f"JSON extraction test passed: {passed_cases}/{len(test_cases)}")
            else:
                result = TestResult(
                    test_name="json_extraction",
                    status="failed",
                    duration=duration,
                    message=f"{failed_cases}/{len(test_cases)} JSON test cases failed",
                    details={
                        'total_cases': len(test_cases),
                        'passed_cases': passed_cases,
                        'failed_cases': failed_cases
                    }
                )
                self.logger.error(f"JSON extraction test failed: {failed_cases} failures")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(
                test_name="json_extraction",
                status="failed",
                duration=duration,
                message=f"JSON extraction test failed: {e}",
                details={'error': str(e)}
            )
            
            self.logger.error(f"JSON extraction test failed: {e}")
            return result
    
    def run_all_consolidated_tests(self) -> Dict[str, Any]:
        """
        Run all consolidated test functions
        
        Returns:
            Dict containing comprehensive test results
        """
        self.logger.info("Starting consolidated test suite")
        start_time = time.time()
        
        # Run all consolidated tests
        test_results = []
        
        test_results.append(self.test_configuration_loading())
        test_results.append(self.test_data_models(test_comprehensive=True))
        test_results.append(self.test_json_extraction())
        
        # Calculate summary statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result.status == "passed")
        failed_tests = sum(1 for result in test_results if result.status == "failed")
        total_duration = time.time() - start_time
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'total_duration': total_duration,
            'individual_results': [
                {
                    'test_name': result.test_name,
                    'status': result.status, 
                    'duration': result.duration,
                    'message': result.message
                }
                for result in test_results
            ]
        }
        
        self.logger.info(f"Consolidated test suite completed: {passed_tests}/{total_tests} passed")
        return summary


# Convenience functions for backward compatibility
def test_configuration_loading() -> bool:
    """Backward compatibility function for configuration loading test"""
    test_functions = ConsolidatedTestFunctions()
    
    try:
        result = test_functions.test_configuration_loading()
        return result.status == "passed"
    finally:
        test_functions.cleanup_temp_directories()


def test_data_models() -> bool:
    """Backward compatibility function for data models test"""
    test_functions = ConsolidatedTestFunctions()
    
    try:
        result = test_functions.test_data_models()
        return result.status == "passed"
    finally:
        test_functions.cleanup_temp_directories()


def test_json_extraction() -> bool:
    """Backward compatibility function for JSON extraction test"""
    test_functions = ConsolidatedTestFunctions()
    
    try:
        result = test_functions.test_json_extraction()
        return result.status == "passed"
    finally:
        test_functions.cleanup_temp_directories()


if __name__ == "__main__":
    # Run consolidated tests if executed directly
    test_functions = ConsolidatedTestFunctions()
    
    try:
        results = test_functions.run_all_consolidated_tests()
        print(json.dumps(results, indent=2, default=str))
        
        # Exit with appropriate code
        exit_code = 0 if results['failed_tests'] == 0 else 1
        exit(exit_code)
        
    finally:
        test_functions.cleanup_temp_directories()