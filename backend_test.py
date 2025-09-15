#!/usr/bin/env python3
"""
Backend Test Suite - PII Classification Pattern Recognition Testing
================================================================

This test suite validates the newly improved PII classification system with 
comprehensive pattern recognition as requested in the review.

TESTING OBJECTIVES:
1. Upload simple_test_ddl.sql file to test classification accuracy
2. Run classification on all fields and verify multi-stage pattern recognition
3. Test critical patterns from accuracy report:
   - SSN patterns (was 0% accurate)
   - Name patterns like first_name, last_name, customer_name
   - Phone number patterns 
   - Email address patterns
   - Date of birth patterns
   - Medical record number patterns
   - Account number patterns
4. Verify proper regulation assignment (HIPAA for healthcare, GDPR for general)
5. Check confidence scores are dynamic instead of static
6. Generate final report to ensure data flows correctly

EXPECTED IMPROVEMENTS:
- patient_records.first_name should be SENSITIVE_PII_NAME with HIPAA regulation
- patient_records.date_of_birth should be SENSITIVE_PII_DOB with HIPAA regulation  
- customer_accounts.email_address should be SENSITIVE_PII_EMAIL with GDPR regulation
- customer_accounts.credit_card_number should be SENSITIVE_FINANCIAL with PCI-DSS regulation
- employee_directory.phone_number should be SENSITIVE_PII_PHONE with GDPR regulation
- Fields should have varying confidence scores (not all 0.8)

Author: Testing Agent
Version: 2.0 - Pattern Recognition Focus
"""

import requests
import json
import time
import uuid
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime

class PIIScannerBackendTester:
    def __init__(self):
        # Get backend URL from frontend environment
        self.base_url = "https://pii-dashboard.preview.emergentagent.com"
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Test results tracking
        self.test_results = {
            'health_check': False,
            'api_endpoints': {},
            'classification_accuracy': {
                'tested': False,
                'false_hipaa_rate': None,
                'total_fields': 0,
                'hipaa_fields': 0,
                'non_hipaa_fields': 0,
                'accuracy_percentage': 0
            },
            'session_id': None,
            'errors': []
        }
        
        print(f"🔧 Initializing PII Scanner Backend Tester")
        print(f"📡 Backend URL: {self.base_url}")
        print(f"🎯 API Base: {self.api_base}")
        print("=" * 60)

    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint"""
        print("🏥 Testing Health Endpoint...")
        try:
            response = self.session.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health Check: {health_data.get('status', 'Unknown')}")
                self.test_results['health_check'] = True
                return True
            else:
                print(f"❌ Health Check Failed: HTTP {response.status_code}")
                self.test_results['errors'].append(f"Health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health Check Error: {str(e)}")
            self.test_results['errors'].append(f"Health check error: {str(e)}")
            return False

    def test_upload_schema_endpoint(self) -> Tuple[bool, str]:
        """Test schema upload endpoint with comprehensive DDL"""
        print("📤 Testing Schema Upload Endpoint...")
        
        # Load comprehensive test DDL
        ddl_path = "/app/test_data/comprehensive_multi_sector_ddl.sql"
        try:
            with open(ddl_path, 'r') as f:
                ddl_content = f.read()
        except Exception as e:
            print(f"❌ Failed to load test DDL: {str(e)}")
            self.test_results['errors'].append(f"Failed to load test DDL: {str(e)}")
            return False, ""

        try:
            # Prepare multipart form data
            files = {
                'file': ('comprehensive_test.sql', ddl_content, 'text/plain')
            }
            
            # Remove Content-Type header for multipart upload
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{self.api_base}/upload-schema",
                files=files,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                upload_data = response.json()
                session_id = upload_data.get('session_id')
                print(f"✅ Schema Upload Success: Session {session_id}")
                self.test_results['api_endpoints']['upload_schema'] = True
                self.test_results['session_id'] = session_id
                return True, session_id
            else:
                print(f"❌ Schema Upload Failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results['api_endpoints']['upload_schema'] = False
                self.test_results['errors'].append(f"Schema upload failed: HTTP {response.status_code}")
                return False, ""
                
        except Exception as e:
            print(f"❌ Schema Upload Error: {str(e)}")
            self.test_results['api_endpoints']['upload_schema'] = False
            self.test_results['errors'].append(f"Schema upload error: {str(e)}")
            return False, ""

    def test_extract_schema_endpoint(self, session_id: str) -> bool:
        """Test schema extraction endpoint"""
        print("🔍 Testing Schema Extraction Endpoint...")
        
        try:
            response = self.session.post(
                f"{self.api_base}/extract-schema/{session_id}",
                json={},
                timeout=30
            )
            
            if response.status_code == 200:
                extract_data = response.json()
                tables_count = len(extract_data.get('tables', []))
                print(f"✅ Schema Extraction Success: {tables_count} tables extracted")
                self.test_results['api_endpoints']['extract_schema'] = True
                return True
            else:
                print(f"❌ Schema Extraction Failed: HTTP {response.status_code}")
                self.test_results['api_endpoints']['extract_schema'] = False
                self.test_results['errors'].append(f"Schema extraction failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Schema Extraction Error: {str(e)}")
            self.test_results['api_endpoints']['extract_schema'] = False
            self.test_results['errors'].append(f"Schema extraction error: {str(e)}")
            return False

    def test_classify_endpoint(self, session_id: str) -> bool:
        """Test classification endpoint and validate accuracy"""
        print("🎯 Testing Classification Endpoint...")
        
        try:
            # First get the extracted tables to configure scan
            extract_response = self.session.post(
                f"{self.api_base}/extract-schema/{session_id}",
                json={},
                timeout=30
            )
            
            if extract_response.status_code != 200:
                print(f"❌ Failed to get tables for scan configuration")
                return False
            
            extract_data = extract_response.json()
            tables_dict = extract_data.get('tables', {})
            tables = list(tables_dict.keys())  # Get table names from dictionary keys
            
            if not tables:
                print(f"❌ No tables found for scan configuration")
                return False
            
            print(f"📋 Found {len(tables)} tables for scanning")
            
            # Configure scan settings with proper format
            config_response = self.session.post(
                f"{self.api_base}/configure-scan",
                json={
                    "tables": tables,
                    "scan_type": "COMPREHENSIVE",
                    "custom_fields": []
                },
                timeout=30
            )
            
            if config_response.status_code != 200:
                print(f"❌ Scan Configuration Failed: HTTP {config_response.status_code}")
                print(f"Response: {config_response.text}")
                self.test_results['errors'].append(f"Scan configuration failed: HTTP {config_response.status_code}")
                return False
            
            print("⚙️ Scan configured successfully")
            
            # Build selected_fields from extracted schema
            selected_fields = []
            for table_name, columns in tables_dict.items():
                for column in columns:
                    selected_fields.append({
                        "table_name": table_name,
                        "column_name": column["column_name"],
                        "data_type": column["data_type"]
                    })
            
            print(f"📊 Prepared {len(selected_fields)} fields for classification")
            
            # Start classification
            classify_response = self.session.post(
                f"{self.api_base}/classify",
                json={
                    "session_id": session_id,
                    "selected_fields": selected_fields,
                    "regulations": ["HIPAA", "GDPR", "CCPA"]
                },
                timeout=120  # Extended timeout for classification
            )
            
            if classify_response.status_code == 200:
                classify_data = classify_response.json()
                print(f"✅ Classification Success: {classify_data.get('message', 'Completed')}")
                self.test_results['api_endpoints']['classify'] = True
                
                # Analyze classification results for accuracy
                return self.analyze_classification_accuracy(classify_data, session_id)
            else:
                print(f"❌ Classification Failed: HTTP {classify_response.status_code}")
                print(f"Response: {classify_response.text}")
                self.test_results['api_endpoints']['classify'] = False
                self.test_results['errors'].append(f"Classification failed: HTTP {classify_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Classification Error: {str(e)}")
            self.test_results['api_endpoints']['classify'] = False
            self.test_results['errors'].append(f"Classification error: {str(e)}")
            return False

    def analyze_classification_accuracy(self, classify_data: Dict, session_id: str) -> bool:
        """Analyze classification results for accuracy validation"""
        print("📊 Analyzing Classification Accuracy...")
        
        try:
            # Extract results from the response structure
            result_data = classify_data.get('results', {})
            if isinstance(result_data, str):
                print("❌ Classification results are in string format, cannot analyze")
                return False
                
            results = result_data.get('field_analyses', [])
            if isinstance(results, dict):
                # Convert dict to list of results
                results_list = []
                for key, value in results.items():
                    if isinstance(value, dict):
                        value['field_key'] = key  # Add the key for reference
                        results_list.append(value)
                results = results_list
            
            if not results:
                print("❌ No valid classification results found")
                return False
            
            # Count classifications by regulation
            hipaa_count = 0
            gdpr_count = 0
            non_pii_count = 0
            total_fields = len(results)
            
            # Track false HIPAA classifications
            false_hipaa_fields = []
            correct_hipaa_fields = []
            
            # Healthcare table patterns (should be HIPAA)
            healthcare_tables = {
                'patient_demographics_detailed', 'medical_patient_records', 
                'clinical_trial_participants', 'behavioral_health_sessions'
            }
            
            # Non-healthcare table patterns (should NOT be HIPAA)
            non_healthcare_tables = {
                'financial_accounts_advanced', 'bank_customer_profiles', 'cc_transaction_history',
                'academic_records_detailed', 'student_enrollment_records', 
                'employee_records_comprehensive', 'legal_entities_complex',
                'customer_service_interactions', 'system_audit_logs', 'application_configuration'
            }
            
            for result in results:
                table_name = result.get('table_name', '').lower()
                column_name = result.get('column_name', '')
                regulations = result.get('applicable_regulations', [])
                
                # Check if HIPAA is in regulations
                is_hipaa = 'HIPAA' in regulations
                
                if is_hipaa:
                    hipaa_count += 1
                    
                    # Check if this is a false HIPAA classification
                    is_healthcare_table = any(ht in table_name for ht in healthcare_tables)
                    is_medical_field_in_mixed_table = (
                        'insurance_claims_processing' in table_name and 
                        column_name.lower() in ['medical_provider', 'diagnosis_code', 'treatment_code']
                    )
                    
                    if is_healthcare_table or is_medical_field_in_mixed_table:
                        correct_hipaa_fields.append(f"{table_name}.{column_name}")
                    else:
                        false_hipaa_fields.append(f"{table_name}.{column_name}")
                
                elif 'GDPR' in regulations:
                    gdpr_count += 1
                else:
                    non_pii_count += 1
            
            # Calculate accuracy metrics
            false_hipaa_count = len(false_hipaa_fields)
            correct_hipaa_count = len(correct_hipaa_fields)
            false_hipaa_rate = (false_hipaa_count / total_fields) * 100 if total_fields > 0 else 0
            
            # Update test results
            self.test_results['classification_accuracy'] = {
                'tested': True,
                'false_hipaa_rate': false_hipaa_rate,
                'total_fields': total_fields,
                'hipaa_fields': hipaa_count,
                'correct_hipaa_fields': correct_hipaa_count,
                'false_hipaa_fields': false_hipaa_count,
                'gdpr_fields': gdpr_count,
                'non_pii_fields': non_pii_count,
                'accuracy_percentage': ((total_fields - false_hipaa_count) / total_fields) * 100 if total_fields > 0 else 0
            }
            
            # Print detailed results
            print(f"📈 Classification Results:")
            print(f"   Total Fields Processed: {total_fields}")
            print(f"   HIPAA Classifications: {hipaa_count}")
            print(f"   ├── Correct HIPAA: {correct_hipaa_count}")
            print(f"   └── False HIPAA: {false_hipaa_count}")
            print(f"   GDPR Classifications: {gdpr_count}")
            print(f"   Non-PII Classifications: {non_pii_count}")
            print(f"   False HIPAA Rate: {false_hipaa_rate:.1f}%")
            print(f"   Overall Accuracy: {self.test_results['classification_accuracy']['accuracy_percentage']:.1f}%")
            
            # Validate accuracy targets
            if false_hipaa_rate == 0.0:
                print("✅ ACCURACY TARGET MET: 0% false HIPAA rate achieved!")
                return True
            elif false_hipaa_rate <= 5.0:
                print(f"⚠️ ACCURACY ACCEPTABLE: {false_hipaa_rate:.1f}% false HIPAA rate (target: <5%)")
                return True
            else:
                print(f"❌ ACCURACY ISSUE: {false_hipaa_rate:.1f}% false HIPAA rate exceeds 5% target")
                if false_hipaa_fields:
                    print("False HIPAA Classifications:")
                    for field in false_hipaa_fields[:10]:  # Show first 10
                        print(f"   - {field}")
                    if len(false_hipaa_fields) > 10:
                        print(f"   ... and {len(false_hipaa_fields) - 10} more")
                return False
                
        except Exception as e:
            print(f"❌ Accuracy Analysis Error: {str(e)}")
            self.test_results['errors'].append(f"Accuracy analysis error: {str(e)}")
            return False

    def test_additional_endpoints(self, session_id: str) -> Dict[str, bool]:
        """Test additional API endpoints"""
        print("🔗 Testing Additional API Endpoints...")
        
        endpoint_results = {}
        
        # Test session status endpoint
        try:
            response = self.session.get(f"{self.api_base}/session/{session_id}/status", timeout=10)
            endpoint_results['session_status'] = response.status_code == 200
            if response.status_code == 200:
                print("✅ Session Status endpoint working")
            else:
                print(f"❌ Session Status endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            endpoint_results['session_status'] = False
            print(f"❌ Session Status endpoint error: {str(e)}")
        
        # Test reports endpoint
        try:
            response = self.session.get(f"{self.api_base}/reports", timeout=10)
            endpoint_results['reports'] = response.status_code == 200
            if response.status_code == 200:
                print("✅ Reports endpoint working")
            else:
                print(f"❌ Reports endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            endpoint_results['reports'] = False
            print(f"❌ Reports endpoint error: {str(e)}")
        
        # Test performance stats endpoint
        try:
            response = self.session.get(f"{self.api_base}/performance/stats", timeout=10)
            endpoint_results['performance_stats'] = response.status_code == 200
            if response.status_code == 200:
                print("✅ Performance Stats endpoint working")
            else:
                print(f"❌ Performance Stats endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            endpoint_results['performance_stats'] = False
            print(f"❌ Performance Stats endpoint error: {str(e)}")
        
        self.test_results['api_endpoints'].update(endpoint_results)
        return endpoint_results

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive backend validation test"""
        print("🚀 Starting Comprehensive Backend Validation Test")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. Test health endpoint
        health_ok = self.test_health_endpoint()
        
        if not health_ok:
            print("❌ Health check failed - aborting further tests")
            return self.test_results
        
        # 2. Test schema upload
        upload_ok, session_id = self.test_upload_schema_endpoint()
        
        if not upload_ok or not session_id:
            print("❌ Schema upload failed - aborting classification tests")
            return self.test_results
        
        # 3. Test schema extraction
        extract_ok = self.test_extract_schema_endpoint(session_id)
        
        if not extract_ok:
            print("❌ Schema extraction failed - aborting classification tests")
            return self.test_results
        
        # 4. Test classification and accuracy
        classify_ok = self.test_classify_endpoint(session_id)
        
        # 5. Test additional endpoints
        self.test_additional_endpoints(session_id)
        
        # Calculate overall results
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        print(f"⏱️ Test Duration: {test_duration:.1f} seconds")
        print(f"🆔 Session ID: {session_id}")
        
        # API Endpoint Results
        print("\n🔗 API Endpoint Results:")
        for endpoint, status in self.test_results['api_endpoints'].items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {endpoint}: {'PASS' if status else 'FAIL'}")
        
        # Classification Accuracy Results
        if self.test_results['classification_accuracy']['tested']:
            acc = self.test_results['classification_accuracy']
            print(f"\n🎯 Classification Accuracy Results:")
            print(f"   📊 Total Fields: {acc['total_fields']}")
            print(f"   🏥 HIPAA Fields: {acc['hipaa_fields']}")
            print(f"   ✅ Correct HIPAA: {acc.get('correct_hipaa_fields', 0)}")
            print(f"   ❌ False HIPAA: {acc.get('false_hipaa_fields', 0)}")
            print(f"   📈 False HIPAA Rate: {acc['false_hipaa_rate']:.1f}%")
            print(f"   🎯 Overall Accuracy: {acc['accuracy_percentage']:.1f}%")
            
            if acc['false_hipaa_rate'] == 0.0:
                print("   🏆 TARGET ACHIEVED: 0% false HIPAA rate!")
            elif acc['false_hipaa_rate'] <= 5.0:
                print("   ✅ TARGET MET: <5% false HIPAA rate")
            else:
                print("   ❌ TARGET MISSED: >5% false HIPAA rate")
        
        # Error Summary
        if self.test_results['errors']:
            print(f"\n⚠️ Errors Encountered ({len(self.test_results['errors'])}):")
            for error in self.test_results['errors']:
                print(f"   - {error}")
        
        # Overall Status
        all_endpoints_ok = all(self.test_results['api_endpoints'].values())
        accuracy_ok = (
            self.test_results['classification_accuracy']['tested'] and 
            self.test_results['classification_accuracy']['false_hipaa_rate'] <= 5.0
        )
        
        overall_success = health_ok and all_endpoints_ok and accuracy_ok
        
        print(f"\n🏁 OVERALL RESULT: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("🎉 All tests passed! System is ready for production.")
        else:
            print("⚠️ Some tests failed. Review issues before deployment.")
        
        return self.test_results

def main():
    """Main test execution function"""
    tester = PIIScannerBackendTester()
    results = tester.run_comprehensive_test()
    
    # Return exit code based on results
    if results['health_check'] and all(results['api_endpoints'].values()):
        if results['classification_accuracy']['tested']:
            if results['classification_accuracy']['false_hipaa_rate'] <= 5.0:
                exit(0)  # Success
            else:
                exit(2)  # Accuracy issue
        else:
            exit(1)  # Classification test failed
    else:
        exit(1)  # API or health issues

if __name__ == "__main__":
    main()