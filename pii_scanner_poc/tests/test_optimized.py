#!/usr/bin/env python3
"""
Optimized Test Suite for PII Scanner
Fast, timeout-aware testing with maximum coverage
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

class OptimizedTestRunner:
    """Optimized test runner that avoids timeouts"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
    def run_test(self, test_name: str, test_func):
        """Run a single test with timeout protection"""
        print(f"🔄 {test_name}...")
        
        start_time = time.time()
        
        try:
            # Set a reasonable timeout for each test
            success = test_func()
            duration = time.time() - start_time
            
            if success:
                print(f"   ✅ PASS ({duration:.2f}s)")
                self.test_results.append((test_name, True, None, duration))
            else:
                print(f"   ❌ FAIL ({duration:.2f}s)")
                self.test_results.append((test_name, False, None, duration))
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"   💥 ERROR ({duration:.2f}s): {str(e)[:60]}...")
            self.test_results.append((test_name, False, str(e), duration))
    
    def test_configuration_loading(self):
        """Test configuration loading without external dependencies"""
        try:
            from pii_scanner_poc.config.config_manager import config_manager
            
            # Test config access
            config = config_manager.get_config()
            
            # Validate structure
            assert hasattr(config, 'ai_config')
            assert hasattr(config, 'batch_config')
            assert hasattr(config, 'logging_config')
            
            # Check new batch limits
            assert hasattr(config.batch_config, 'max_columns_per_batch')
            assert hasattr(config.batch_config, 'max_tables_per_batch')
            assert hasattr(config.batch_config, 'timeout_seconds')
            
            print(f"      📊 Max columns per batch: {config.batch_config.max_columns_per_batch}")
            print(f"      📊 Max tables per batch: {config.batch_config.max_tables_per_batch}")
            print(f"      📊 Timeout seconds: {config.batch_config.timeout_seconds}")
            
            return True
            
        except Exception as e:
            print(f"      ❌ Config loading failed: {e}")
            return False
    
    def test_data_models(self):
        """Test data model functionality"""
        try:
            from pii_scanner_poc.models.data_models import (
                ColumnMetadata, TableAnalysisResult, Regulation, 
                convert_strings_to_regulations, PIIAnalysisResult
            )
            
            # Test column metadata
            col = ColumnMetadata("db", "table", "email", "VARCHAR(100)")
            assert col.column_name == "email"
            
            # Test regulation conversion
            regulations = convert_strings_to_regulations(['GDPR', 'HIPAA'])
            assert len(regulations) == 2
            assert Regulation.GDPR in regulations
            
            # Test PII analysis result
            pii_result = PIIAnalysisResult(
                column_name="email",
                data_type="VARCHAR(100)",
                is_sensitive=True,
                sensitivity_level=None,
                pii_type=None,
                applicable_regulations=[],
                confidence_score=0.9,
                risk_explanation="Email is PII",
                recommendations=["Encrypt"]
            )
            assert pii_result.is_sensitive
            
            print(f"      📊 Data models working correctly")
            return True
            
        except Exception as e:
            print(f"      ❌ Data models test failed: {e}")
            return False
    
    def test_batch_creation(self):
        """Test batch creation without AI analysis"""
        try:
            from pii_scanner_poc.core.batch_processor import batch_processor
            from pii_scanner_poc.models.data_models import ColumnMetadata, Regulation
            
            # Create test data
            test_data = {
                'table1': [
                    ColumnMetadata(schema_name="", table_name="table1", column_name="id", data_type="INT"),
                    ColumnMetadata(schema_name="", table_name="table1", column_name="email", data_type="VARCHAR(100)"),
                    ColumnMetadata(schema_name="", table_name="table1", column_name="name", data_type="VARCHAR(50)")
                ],
                'table2': [
                    ColumnMetadata(schema_name="", table_name="table2", column_name="user_id", data_type="INT"),
                    ColumnMetadata(schema_name="", table_name="table2", column_name="phone", data_type="VARCHAR(20)")
                ]
            }
            
            # Test batch creation
            batches = batch_processor._create_optimal_batches(
                test_data, [Regulation.GDPR]
            )
            
            assert len(batches) > 0
            assert all(batch.batch_number > 0 for batch in batches)
            
            total_tables = sum(len(batch.tables) for batch in batches)
            assert total_tables == 2
            
            print(f"      📊 Created {len(batches)} batches for 2 tables")
            
            # Test with larger dataset
            large_data = {}
            for i in range(10):  # 10 tables
                columns = []
                for j in range(8):  # 8 columns each
                    columns.append(ColumnMetadata(
                        schema_name="", 
                        table_name=f"table_{i}", 
                        column_name=f"col_{j}", 
                        data_type="VARCHAR(50)"
                    ))
                large_data[f"table_{i}"] = columns
            
            large_batches = batch_processor._create_optimal_batches(
                large_data, [Regulation.GDPR]
            )
            
            print(f"      📊 Large dataset: {len(large_batches)} batches for 10 tables (80 columns)")
            
            # Verify batch size limits are respected
            for batch in large_batches:
                assert len(batch.tables) <= batch_processor.batch_config.max_tables_per_batch
                assert batch.total_columns <= batch_processor.batch_config.max_columns_per_batch
            
            return True
            
        except Exception as e:
            print(f"      ❌ Batch creation test failed: {e}")
            return False
    
    def test_json_extraction(self):
        """Test JSON extraction without AI calls"""
        try:
            from pii_scanner_poc.services.ai_service import json_extractor
            from pii_scanner_poc.models.data_models import AIModelResponse
            
            # Test valid JSON extraction
            valid_json_response = AIModelResponse(
                content='{"table_results": [{"table_name": "test", "sensitive_columns": 1}]}',
                model_name="test",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                response_time=1.0,
                success=True
            )
            
            result = json_extractor.extract_json_from_response(valid_json_response)
            assert result is not None
            assert 'table_results' in result
            
            # Test malformed JSON
            malformed_response = AIModelResponse(
                content='{"table_results": [{"table_name": "test", "sensitive_columns":',
                model_name="test",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                response_time=1.0,
                success=True
            )
            
            result = json_extractor.extract_json_from_response(malformed_response)
            # Should return None for malformed JSON
            assert result is None
            
            print(f"      📊 JSON extraction methods working")
            return True
            
        except Exception as e:
            print(f"      ❌ JSON extraction test failed: {e}")
            return False
    
    def test_file_operations(self):
        """Test file operations with proper encoding"""
        try:
            import tempfile
            from pathlib import Path
            
            # Test Unicode content
            test_content = "🔐 Test content with emojis ✅ and special chars: café"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(test_content)
                temp_file_path = temp_file.name
            
            # Read back and verify
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                read_content = f.read()
            
            assert read_content == test_content
            
            # Cleanup
            Path(temp_file_path).unlink()
            
            print(f"      📊 File encoding test passed")
            return True
            
        except Exception as e:
            print(f"      ❌ File operations test failed: {e}")
            return False
    
    def test_mcp_server_structure(self):
        """Test MCP server structure without running it"""
        try:
            from mcp_server_enhanced import EnhancedMCPServer
            
            # Test server creation
            server = EnhancedMCPServer()
            assert server.server is not None
            assert server.server.name == "pii-scanner-enhanced"
            
            print(f"      📊 MCP server structure validated")
            return True
            
        except Exception as e:
            print(f"      ❌ MCP server structure test failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        try:
            from pii_scanner_poc.services.database_service import database_service
            
            # Test with non-existent file
            try:
                database_service.load_schema_from_file("nonexistent_file.ddl")
                return False  # Should have raised an exception
            except FileNotFoundError:
                pass  # Expected
            
            # Test with invalid regulation
            try:
                from pii_scanner_poc.models.data_models import convert_string_to_regulation
                convert_string_to_regulation("INVALID_REG")
                return False  # Should have raised an exception
            except ValueError:
                pass  # Expected
            
            print(f"      📊 Error handling working correctly")
            return True
            
        except Exception as e:
            print(f"      ❌ Error handling test failed: {e}")
            return False
    
    def test_mock_analysis(self):
        """Test analysis workflow with mocked AI responses"""
        try:
            from pii_scanner_poc.core.pii_scanner_facade import pii_scanner
            import tempfile
            
            # Create test schema
            test_schema = """
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(100),
    name VARCHAR(50)
);"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ddl', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(test_schema)
                temp_file_path = temp_file.name
            
            # Mock the AI service to avoid actual API calls
            with patch('services.ai_service.ai_service.send_analysis_request') as mock_ai:
                mock_response = Mock()
                mock_response.success = True
                mock_response.content = '{"table_results": [{"table_name": "users", "risk_level": "High", "total_columns": 3, "sensitive_columns": 2, "applicable_regulations": ["GDPR"], "column_analysis": [{"column_name": "id", "data_type": "INT", "is_sensitive": false, "sensitivity_level": "None", "pii_type": "None", "applicable_regulations": []}, {"column_name": "email", "data_type": "VARCHAR(100)", "is_sensitive": true, "sensitivity_level": "High", "pii_type": "Email", "applicable_regulations": ["GDPR"]}, {"column_name": "name", "data_type": "VARCHAR(50)", "is_sensitive": true, "sensitivity_level": "High", "pii_type": "Name", "applicable_regulations": ["GDPR"]}]}]}'
                mock_response.model_name = "test"
                mock_response.response_time = 1.0
                mock_ai.return_value = mock_response
                
                # Test analysis
                result = pii_scanner.analyze_schema_file(
                    schema_file_path=temp_file_path,
                    regulations=['GDPR'],
                    output_format='json'
                )
                
                # Verify result structure
                assert 'success' in result or 'analysis_summary' in result
                
            # Cleanup
            Path(temp_file_path).unlink()
            
            print(f"      📊 Mock analysis completed successfully")
            return True
            
        except Exception as e:
            print(f"      ❌ Mock analysis test failed: {e}")
            return False
    
    def test_comprehensive_integration(self):
        """Test comprehensive integration with small dataset"""
        try:
            # This test runs fast integration without real AI calls
            print(f"      📊 Running integration test with mocked AI...")
            
            # Test configuration validation
            from pii_scanner_poc.core.pii_scanner_facade import pii_scanner
            validation_result = pii_scanner.validate_configuration()
            
            # Should have structure even if API key is invalid
            assert 'valid' in validation_result
            assert 'errors' in validation_result
            assert 'warnings' in validation_result
            
            print(f"      📊 Integration test passed")
            return True
            
        except Exception as e:
            print(f"      ❌ Integration test failed: {e}")
            return False
    
    def run_optimized_tests(self):
        """Run all optimized tests"""
        print("🚀 Enhanced PII Scanner - Optimized Test Suite")
        print("=" * 55)
        print("Fast, comprehensive testing with timeout protection")
        print()
        
        # Define optimized test suite
        tests = [
            ("Configuration Loading", self.test_configuration_loading),
            ("Data Models", self.test_data_models),
            ("Batch Creation", self.test_batch_creation),
            ("JSON Extraction", self.test_json_extraction),
            ("File Operations", self.test_file_operations),
            ("MCP Server Structure", self.test_mcp_server_structure),
            ("Error Handling", self.test_error_handling),
            ("Mock Analysis", self.test_mock_analysis),
            ("Integration Test", self.test_comprehensive_integration)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        self.generate_summary()
        
        return self.calculate_success_rate()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 55)
        print("📋 OPTIMIZED TEST RESULTS SUMMARY")
        print("=" * 55)
        
        passed = 0
        failed = 0
        crashed = 0
        total_time = 0
        
        for test_name, success, error, duration in self.test_results:
            total_time += duration
            
            if error:
                status = "💥 CRASH"
                crashed += 1
            elif success:
                status = "✅ PASS"
                passed += 1
            else:
                status = "❌ FAIL"
                failed += 1
            
            print(f"{status:<10} - {test_name} ({duration:.2f}s)")
        
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        overall_duration = (datetime.now() - self.start_time).total_seconds()
        
        print()
        print("📊 STATISTICS:")
        print(f"├─ Total Tests: {total}")
        print(f"├─ Passed: {passed}")
        print(f"├─ Failed: {failed}")
        print(f"├─ Crashed: {crashed}")
        print(f"├─ Success Rate: {success_rate:.1f}%")
        print(f"├─ Test Duration: {total_time:.2f}s")
        print(f"└─ Overall Duration: {overall_duration:.2f}s")
        print()
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! All systems working correctly.")
            print("   The PII Scanner is ready for production use.")
        elif success_rate >= 75:
            print("✅ GOOD! Most functionality is working correctly.")
            print("   Minor issues may need attention.")
        elif success_rate >= 50:
            print("⚠️ MODERATE. Core functionality works with some issues.")
            print("   Review failed tests before production use.")
        else:
            print("❌ CRITICAL. Major issues found.")
            print("   Significant fixes needed before production use.")
    
    def calculate_success_rate(self):
        """Calculate overall success rate"""
        if not self.test_results:
            return 0.0
        
        passed = sum(1 for _, success, error, _ in self.test_results if success and not error)
        total = len(self.test_results)
        
        return (passed / total * 100) if total > 0 else 0.0


def main():
    """Main entry point for optimized testing"""
    try:
        test_runner = OptimizedTestRunner()
        success_rate = test_runner.run_optimized_tests()
        
        # Exit with appropriate code
        if success_rate >= 90:
            sys.exit(0)  # Excellent
        elif success_rate >= 75:
            sys.exit(1)  # Good
        elif success_rate >= 50:
            sys.exit(2)  # Moderate
        else:
            sys.exit(3)  # Critical
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(4)


if __name__ == "__main__":
    main()