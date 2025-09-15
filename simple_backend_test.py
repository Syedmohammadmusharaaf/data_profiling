#!/usr/bin/env python3
"""
Simple Backend Test for PII Scanner - Review Request
====================================================

This test performs a simple functionality test of the PII Scanner backend
to verify the accuracy fix is working correctly.

Test Requirements:
1. Test the basic health check endpoint (/api/health) 
2. Upload a simple test DDL with mixed field types (healthcare, financial, general) 
3. Extract schema from the uploaded file
4. Run classification on a few sample fields 
5. Verify that context-aware regulation assignment is working:
   - Healthcare fields → HIPAA
   - Financial fields → GDPR  
   - General business fields → GDPR
"""

import requests
import json
import time
from typing import Dict, List, Any, Tuple

class SimpleBackendTester:
    def __init__(self):
        # Use localhost for testing since that's how the frontend connects
        self.base_url = "http://localhost:8001"
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        print(f"🔧 Simple PII Scanner Backend Tester")
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
                print(f"   Version: {health_data.get('version', 'Unknown')}")
                print(f"   Components: {health_data.get('components', {})}")
                return True
            else:
                print(f"❌ Health Check Failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health Check Error: {str(e)}")
            return False

    def test_upload_simple_ddl(self) -> Tuple[bool, str]:
        """Test schema upload endpoint with simple DDL"""
        print("📤 Testing Schema Upload with Simple DDL...")
        
        # Simple DDL content with mixed field types
        ddl_content = """-- Simple Test DDL for PII Scanner Backend Testing
-- Contains mixed field types: healthcare, financial, and general business

-- Healthcare table (should be classified as HIPAA)
CREATE TABLE patient_records (
    patient_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    medical_record_number VARCHAR(20),
    diagnosis_code VARCHAR(10)
);

-- Financial table (should be classified as GDPR)
CREATE TABLE customer_accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100),
    email_address VARCHAR(255),
    credit_card_number VARCHAR(20),
    account_balance DECIMAL(15,2),
    created_date TIMESTAMP
);

-- General business table (should be classified as GDPR)
CREATE TABLE employee_directory (
    employee_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(100),
    department VARCHAR(50),
    phone_number VARCHAR(20),
    hire_date DATE,
    salary DECIMAL(10,2)
);"""

        try:
            # Prepare multipart form data
            files = {
                'file': ('simple_test.sql', ddl_content, 'text/plain')
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
                print(f"   File: {upload_data.get('file_name')}")
                print(f"   Size: {upload_data.get('file_size')} bytes")
                return True, session_id
            else:
                print(f"❌ Schema Upload Failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False, ""
                
        except Exception as e:
            print(f"❌ Schema Upload Error: {str(e)}")
            return False, ""

    def test_extract_schema(self, session_id: str) -> bool:
        """Test schema extraction endpoint"""
        print("🔍 Testing Schema Extraction...")
        
        try:
            response = self.session.post(
                f"{self.api_base}/extract-schema/{session_id}",
                json={},
                timeout=30
            )
            
            if response.status_code == 200:
                extract_data = response.json()
                tables = extract_data.get('tables', {})
                print(f"✅ Schema Extraction Success: {len(tables)} tables extracted")
                
                # Print table details
                for table_name, columns in tables.items():
                    print(f"   📋 Table: {table_name} ({len(columns)} columns)")
                    for col in columns[:3]:  # Show first 3 columns
                        print(f"      - {col['column_name']} ({col['data_type']})")
                    if len(columns) > 3:
                        print(f"      ... and {len(columns) - 3} more columns")
                
                return True
            else:
                print(f"❌ Schema Extraction Failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Schema Extraction Error: {str(e)}")
            return False

    def test_classification(self, session_id: str) -> bool:
        """Test classification endpoint and verify context-aware regulation assignment"""
        print("🎯 Testing Classification and Context-Aware Regulation Assignment...")
        
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
            tables = list(tables_dict.keys())
            
            print(f"📋 Found {len(tables)} tables for scanning: {tables}")
            
            # Configure scan settings
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
                timeout=120
            )
            
            if classify_response.status_code == 200:
                classify_data = classify_response.json()
                print(f"✅ Classification Success: {classify_data.get('message', 'Completed')}")
                
                # Analyze classification results for context-aware regulation assignment
                return self.analyze_context_aware_results(classify_data)
            else:
                print(f"❌ Classification Failed: HTTP {classify_response.status_code}")
                print(f"Response: {classify_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Classification Error: {str(e)}")
            return False

    def analyze_context_aware_results(self, classify_data: Dict) -> bool:
        """Analyze classification results for context-aware regulation assignment"""
        print("📊 Analyzing Context-Aware Regulation Assignment...")
        
        try:
            result_data = classify_data.get('results', {})
            field_analyses = result_data.get('field_analyses', {})
            
            if not field_analyses:
                print("❌ No field analyses found in results")
                return False
            
            # Expected regulation assignments based on table context
            expected_regulations = {
                'patient_records': 'HIPAA',      # Healthcare table
                'customer_accounts': 'GDPR',     # Financial table  
                'employee_directory': 'GDPR'     # General business table
            }
            
            # Track results by table
            results_by_table = {}
            total_fields = 0
            correct_assignments = 0
            
            for field_key, field_data in field_analyses.items():
                table_name = field_data.get('table_name', '')
                field_name = field_data.get('field_name', '')
                is_sensitive = field_data.get('is_sensitive', False)
                regulations = field_data.get('applicable_regulations', [])
                
                if table_name not in results_by_table:
                    results_by_table[table_name] = {
                        'fields': [],
                        'hipaa_count': 0,
                        'gdpr_count': 0,
                        'non_pii_count': 0
                    }
                
                # Only analyze sensitive fields
                if is_sensitive and regulations:
                    total_fields += 1
                    expected_reg = expected_regulations.get(table_name, 'GDPR')
                    actual_reg = regulations[0] if regulations else 'None'
                    
                    field_result = {
                        'field_name': field_name,
                        'expected': expected_reg,
                        'actual': actual_reg,
                        'correct': expected_reg == actual_reg
                    }
                    
                    results_by_table[table_name]['fields'].append(field_result)
                    
                    if actual_reg == 'HIPAA':
                        results_by_table[table_name]['hipaa_count'] += 1
                    elif actual_reg == 'GDPR':
                        results_by_table[table_name]['gdpr_count'] += 1
                    
                    if field_result['correct']:
                        correct_assignments += 1
            
            # Print detailed results
            print(f"\n📈 Context-Aware Regulation Assignment Results:")
            print(f"   Total Sensitive Fields Analyzed: {total_fields}")
            
            for table_name, table_results in results_by_table.items():
                expected_reg = expected_regulations.get(table_name, 'GDPR')
                print(f"\n   📋 Table: {table_name} (Expected: {expected_reg})")
                print(f"      HIPAA: {table_results['hipaa_count']}")
                print(f"      GDPR: {table_results['gdpr_count']}")
                print(f"      Non-PII: {table_results['non_pii_count']}")
                
                # Show field-level results
                for field in table_results['fields']:
                    status = "✅" if field['correct'] else "❌"
                    print(f"      {status} {field['field_name']}: {field['actual']} (expected {field['expected']})")
            
            # Calculate accuracy
            accuracy = (correct_assignments / total_fields * 100) if total_fields > 0 else 0
            print(f"\n🎯 Context-Aware Accuracy: {correct_assignments}/{total_fields} ({accuracy:.1f}%)")
            
            # Verify specific expectations
            success_criteria = []
            
            # Healthcare fields should be HIPAA
            patient_table = results_by_table.get('patient_records', {})
            if patient_table.get('hipaa_count', 0) > 0:
                success_criteria.append("✅ Healthcare fields correctly classified as HIPAA")
            else:
                success_criteria.append("❌ Healthcare fields NOT classified as HIPAA")
            
            # Financial fields should be GDPR
            customer_table = results_by_table.get('customer_accounts', {})
            if customer_table.get('gdpr_count', 0) > 0:
                success_criteria.append("✅ Financial fields correctly classified as GDPR")
            else:
                success_criteria.append("❌ Financial fields NOT classified as GDPR")
            
            # Business fields should be GDPR
            employee_table = results_by_table.get('employee_directory', {})
            if employee_table.get('gdpr_count', 0) > 0:
                success_criteria.append("✅ Business fields correctly classified as GDPR")
            else:
                success_criteria.append("❌ Business fields NOT classified as GDPR")
            
            print(f"\n🏆 Success Criteria:")
            for criterion in success_criteria:
                print(f"   {criterion}")
            
            # Overall success if accuracy > 80% and all criteria met
            all_criteria_met = all("✅" in criterion for criterion in success_criteria)
            overall_success = accuracy >= 80.0 and all_criteria_met
            
            if overall_success:
                print(f"\n🎉 CONTEXT-AWARE REGULATION ASSIGNMENT: WORKING CORRECTLY!")
                print(f"   Accuracy: {accuracy:.1f}% (Target: >80%)")
                print(f"   All context criteria met: {all_criteria_met}")
            else:
                print(f"\n⚠️ CONTEXT-AWARE REGULATION ASSIGNMENT: NEEDS ATTENTION")
                print(f"   Accuracy: {accuracy:.1f}% (Target: >80%)")
                print(f"   All context criteria met: {all_criteria_met}")
            
            return overall_success
                
        except Exception as e:
            print(f"❌ Context-Aware Analysis Error: {str(e)}")
            return False

    def run_simple_test(self) -> bool:
        """Run the simple functionality test"""
        print("🚀 Starting Simple PII Scanner Backend Test")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. Test health endpoint
        print("\n1️⃣ HEALTH CHECK")
        health_ok = self.test_health_endpoint()
        
        if not health_ok:
            print("❌ Health check failed - aborting further tests")
            return False
        
        # 2. Test schema upload
        print("\n2️⃣ SCHEMA UPLOAD")
        upload_ok, session_id = self.test_upload_simple_ddl()
        
        if not upload_ok or not session_id:
            print("❌ Schema upload failed - aborting further tests")
            return False
        
        # 3. Test schema extraction
        print("\n3️⃣ SCHEMA EXTRACTION")
        extract_ok = self.test_extract_schema(session_id)
        
        if not extract_ok:
            print("❌ Schema extraction failed - aborting classification test")
            return False
        
        # 4. Test classification and context-aware regulation assignment
        print("\n4️⃣ CLASSIFICATION & CONTEXT-AWARE REGULATION ASSIGNMENT")
        classify_ok = self.test_classification(session_id)
        
        # Calculate overall results
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 SIMPLE TEST SUMMARY")
        print("=" * 60)
        
        print(f"⏱️ Test Duration: {test_duration:.1f} seconds")
        print(f"🆔 Session ID: {session_id}")
        
        # Test Results
        print(f"\n🔗 Test Results:")
        print(f"   {'✅' if health_ok else '❌'} Health Check: {'PASS' if health_ok else 'FAIL'}")
        print(f"   {'✅' if upload_ok else '❌'} Schema Upload: {'PASS' if upload_ok else 'FAIL'}")
        print(f"   {'✅' if extract_ok else '❌'} Schema Extraction: {'PASS' if extract_ok else 'FAIL'}")
        print(f"   {'✅' if classify_ok else '❌'} Context-Aware Classification: {'PASS' if classify_ok else 'FAIL'}")
        
        overall_success = health_ok and upload_ok and extract_ok and classify_ok
        
        print(f"\n🏁 OVERALL RESULT: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("🎉 All tests passed! PII Scanner backend is working correctly.")
            print("✅ Context-aware regulation assignment is functioning properly:")
            print("   - Healthcare fields → HIPAA")
            print("   - Financial fields → GDPR")
            print("   - General business fields → GDPR")
        else:
            print("⚠️ Some tests failed. Review issues above.")
        
        return overall_success

def main():
    """Main test execution function"""
    tester = SimpleBackendTester()
    success = tester.run_simple_test()
    
    # Return exit code based on results
    exit(0 if success else 1)

if __name__ == "__main__":
    main()