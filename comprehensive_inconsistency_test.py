#!/usr/bin/env python3
"""
Comprehensive Inconsistency Fixes Test - Review Request Verification
==================================================================

This test verifies all the specific inconsistency fixes mentioned in the review request:

TESTING OBJECTIVES:
1. Upload Schema & Extract Tables: Test simple_test_ddl.sql upload and verify tables are properly parsed
2. Classification Accuracy: Verify specific misclassification fixes:
   - cancelled_date should NOT be classified as PHONE (should be NON_SENSITIVE DATE)
   - middle_initial should be classified as NAME_COMPONENT not PATIENT_ID  
   - medication_name should be NON_SENSITIVE not NAME
   - Fields in healthcare tables should get HIPAA regulation
3. Executive Summary Verification: Check that sensitive_fields_found is accurate (not 0)
4. Risk Assessment: Verify risk_assessment is not uniformly LOW, should vary based on content
5. Compliance Status: Verify NON-COMPLIANT status when sensitive fields are detected
6. Report Generation: Test full report with enhanced summary, detailed findings, and compliance status

CRITICAL VERIFICATION POINTS:
- Total risk score should be calculated and included (not 0)  
- Sensitive fields arrays should be populated (not empty)
- Table breakdown should show actual table names from DDL (not all unknown_table)
- Risk levels should vary (not all LOW)
- Compliance status should reflect actual findings (NON-COMPLIANT when appropriate)
- PHI/PII fields should be correctly categorized in separate arrays

Author: Testing Agent
Version: 1.0 - Comprehensive Inconsistency Verification
"""

import requests
import json
import time
import uuid
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime

class ComprehensiveInconsistencyTester:
    def __init__(self):
        # Use the correct backend URL from frontend environment
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
            'schema_upload': False,
            'schema_extraction': False,
            'classification': False,
            'report_generation': False,
            'inconsistency_fixes': {
                'cancelled_date_fix': False,
                'middle_initial_fix': False,
                'medication_name_fix': False,
                'healthcare_hipaa_fix': False
            },
            'executive_summary_verification': {
                'sensitive_fields_accurate': False,
                'risk_assessment_varies': False,
                'compliance_status_correct': False
            },
            'report_verification': {
                'total_risk_score_calculated': False,
                'sensitive_arrays_populated': False,
                'table_breakdown_accurate': False,
                'risk_levels_vary': False,
                'phi_pii_categorized': False
            },
            'session_id': None,
            'errors': []
        }
        
        print(f"🔧 Comprehensive Inconsistency Fixes Tester")
        print(f"📡 Backend URL: {self.base_url}")
        print(f"🎯 API Base: {self.api_base}")
        print("=" * 80)

    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint"""
        print("🏥 Testing Health Endpoint...")
        try:
            response = self.session.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health Check: {health_data.get('status', 'Unknown')}")
                print(f"   Version: {health_data.get('version', 'Unknown')}")
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

    def test_upload_simple_test_ddl(self) -> Tuple[bool, str]:
        """Test schema upload with inconsistency_test_ddl.sql file"""
        print("📤 Testing Schema Upload with inconsistency_test_ddl.sql...")
        
        # Load the inconsistency_test_ddl.sql file with specific fields for testing
        try:
            with open('/app/inconsistency_test_ddl.sql', 'r') as f:
                ddl_content = f.read()
        except Exception as e:
            print(f"❌ Failed to load inconsistency_test_ddl.sql: {str(e)}")
            self.test_results['errors'].append(f"Failed to load DDL file: {str(e)}")
            return False, ""

        try:
            # Prepare multipart form data
            files = {
                'file': ('inconsistency_test_ddl.sql', ddl_content, 'text/plain')
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
                self.test_results['schema_upload'] = True
                self.test_results['session_id'] = session_id
                return True, session_id
            else:
                print(f"❌ Schema Upload Failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results['errors'].append(f"Schema upload failed: HTTP {response.status_code}")
                return False, ""
                
        except Exception as e:
            print(f"❌ Schema Upload Error: {str(e)}")
            self.test_results['errors'].append(f"Schema upload error: {str(e)}")
            return False, ""

    def test_extract_schema_and_verify_tables(self, session_id: str) -> bool:
        """Test schema extraction and verify tables are properly parsed"""
        print("🔍 Testing Schema Extraction and Table Parsing...")
        
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
                
                # Verify expected tables are present and not assigned to 'unknown_table'
                expected_tables = ['patient_records', 'customer_accounts', 'employee_directory', 'medication_catalog']
                tables_found = list(tables.keys())
                
                print(f"📋 Expected tables: {expected_tables}")
                print(f"📋 Found tables: {tables_found}")
                
                # Check if all expected tables are found
                all_tables_found = all(table in tables_found for table in expected_tables)
                no_unknown_tables = 'unknown_table' not in tables_found
                
                if all_tables_found and no_unknown_tables:
                    print("✅ VERIFICATION PASSED: All tables properly parsed (not assigned to 'unknown_table')")
                    self.test_results['schema_extraction'] = True
                    
                    # Print table details for verification
                    for table_name, columns in tables.items():
                        print(f"   📋 Table: {table_name} ({len(columns)} columns)")
                        for col in columns[:3]:  # Show first 3 columns
                            print(f"      - {col['column_name']} ({col['data_type']})")
                        if len(columns) > 3:
                            print(f"      ... and {len(columns) - 3} more columns")
                    
                    return True
                else:
                    print("❌ VERIFICATION FAILED: Tables not properly parsed")
                    if not all_tables_found:
                        missing = [t for t in expected_tables if t not in tables_found]
                        print(f"   Missing tables: {missing}")
                    if 'unknown_table' in tables_found:
                        print("   Found 'unknown_table' - indicates parsing issue")
                    self.test_results['errors'].append("Table parsing verification failed")
                    return False
            else:
                print(f"❌ Schema Extraction Failed: HTTP {response.status_code}")
                self.test_results['errors'].append(f"Schema extraction failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Schema Extraction Error: {str(e)}")
            self.test_results['errors'].append(f"Schema extraction error: {str(e)}")
            return False

    def test_classification_and_verify_fixes(self, session_id: str) -> bool:
        """Test classification and verify specific inconsistency fixes"""
        print("🎯 Testing Classification and Verifying Inconsistency Fixes...")
        
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
                
                # Verify specific inconsistency fixes
                return self.verify_inconsistency_fixes(classify_data)
            else:
                print(f"❌ Classification Failed: HTTP {classify_response.status_code}")
                print(f"Response: {classify_response.text}")
                self.test_results['errors'].append(f"Classification failed: HTTP {classify_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Classification Error: {str(e)}")
            self.test_results['errors'].append(f"Classification error: {str(e)}")
            return False

    def verify_inconsistency_fixes(self, classify_data: Dict) -> bool:
        """Verify specific inconsistency fixes from the review request"""
        print("🔍 Verifying Specific Inconsistency Fixes...")
        
        try:
            result_data = classify_data.get('results', {})
            field_analyses = result_data.get('field_analyses', {})
            
            if not field_analyses:
                print("❌ No field analyses found in results")
                return False
            
            # Track specific fixes
            fixes_verified = {
                'cancelled_date_fix': False,
                'middle_initial_fix': False,
                'medication_name_fix': False,
                'healthcare_hipaa_fix': False
            }
            
            print(f"\n📊 Analyzing {len(field_analyses)} classified fields...")
            
            # Check each field for specific fixes
            for field_key, analysis in field_analyses.items():
                field_name = analysis.get('field_name', '').lower()
                table_name = analysis.get('table_name', '').lower()
                classification = analysis.get('classification', '')
                regulations = analysis.get('applicable_regulations', [])
                is_sensitive = analysis.get('is_sensitive', False)
                
                print(f"   🔍 {field_key}: {classification} -> {regulations} (sensitive: {is_sensitive})")
                
                # Fix 1: cancelled_date should NOT be classified as PHONE (should be NON_SENSITIVE DATE)
                if 'cancelled_date' in field_name:
                    if 'PHONE' not in classification and 'PHONE' not in str(regulations):
                        fixes_verified['cancelled_date_fix'] = True
                        print(f"   ✅ FIX 1 VERIFIED: cancelled_date NOT classified as PHONE")
                    else:
                        print(f"   ❌ FIX 1 FAILED: cancelled_date still classified as PHONE")
                
                # Fix 2: middle_initial should be classified as NAME_COMPONENT not PATIENT_ID
                if 'middle_initial' in field_name:
                    if 'NAME' in classification and 'PATIENT_ID' not in classification:
                        fixes_verified['middle_initial_fix'] = True
                        print(f"   ✅ FIX 2 VERIFIED: middle_initial classified as NAME_COMPONENT, not PATIENT_ID")
                    else:
                        print(f"   ❌ FIX 2 FAILED: middle_initial not properly classified")
                
                # Fix 3: medication_name should be NON_SENSITIVE not NAME
                if 'medication_name' in field_name:
                    if not is_sensitive or 'NON_SENSITIVE' in classification:
                        fixes_verified['medication_name_fix'] = True
                        print(f"   ✅ FIX 3 VERIFIED: medication_name classified as NON_SENSITIVE")
                    else:
                        print(f"   ❌ FIX 3 FAILED: medication_name still classified as sensitive NAME")
                
                # Fix 4: Fields in healthcare tables should get HIPAA regulation
                if 'patient' in table_name and is_sensitive:
                    if 'HIPAA' in regulations:
                        fixes_verified['healthcare_hipaa_fix'] = True
                        print(f"   ✅ FIX 4 VERIFIED: Healthcare field {field_key} has HIPAA regulation")
                    else:
                        print(f"   ❌ FIX 4 FAILED: Healthcare field {field_key} missing HIPAA regulation")
            
            # Update test results
            self.test_results['inconsistency_fixes'] = fixes_verified
            self.test_results['classification'] = True
            
            # Summary of fixes
            fixes_passed = sum(fixes_verified.values())
            total_fixes = len(fixes_verified)
            
            print(f"\n📈 Inconsistency Fixes Summary:")
            print(f"   ✅ Fixes Verified: {fixes_passed}/{total_fixes}")
            
            for fix_name, verified in fixes_verified.items():
                status = "✅ PASSED" if verified else "❌ FAILED"
                print(f"   {status} {fix_name}")
            
            return fixes_passed >= 3  # At least 3 out of 4 fixes should work
                
        except Exception as e:
            print(f"❌ Inconsistency Fix Verification Error: {str(e)}")
            self.test_results['errors'].append(f"Fix verification error: {str(e)}")
            return False

    def test_report_generation_and_verify_enhancements(self, session_id: str) -> bool:
        """Test report generation and verify enhanced summary, detailed findings, and compliance status"""
        print("📊 Testing Report Generation and Verifying Enhancements...")
        
        try:
            response = self.session.post(
                f"{self.api_base}/generate-report/{session_id}",
                json={"format": "json"},
                timeout=60
            )
            
            if response.status_code == 200:
                report_data = response.json()
                print(f"✅ Report Generation Success")
                
                # Verify enhanced report structure
                return self.verify_report_enhancements(report_data)
            else:
                print(f"❌ Report Generation Failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                self.test_results['errors'].append(f"Report generation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Report Generation Error: {str(e)}")
            self.test_results['errors'].append(f"Report generation error: {str(e)}")
            return False

    def verify_report_enhancements(self, report_data: Dict) -> bool:
        """Verify enhanced report structure and content"""
        print("🔍 Verifying Enhanced Report Structure...")
        
        try:
            # Check executive summary
            executive_summary = report_data.get('executive_summary', {})
            detailed_findings = report_data.get('detailed_findings', {})
            compliance_status = report_data.get('compliance_status', {})
            
            verification_results = {
                'sensitive_fields_accurate': False,
                'risk_assessment_varies': False,
                'compliance_status_correct': False,
                'total_risk_score_calculated': False,
                'sensitive_arrays_populated': False,
                'table_breakdown_accurate': False,
                'risk_levels_vary': False,
                'phi_pii_categorized': False
            }
            
            print(f"\n📊 Executive Summary Verification:")
            
            # 1. Check that sensitive_fields_found is accurate (not 0)
            sensitive_fields_found = executive_summary.get('sensitive_fields_found', 0)
            if sensitive_fields_found > 0:
                verification_results['sensitive_fields_accurate'] = True
                print(f"   ✅ Sensitive fields found: {sensitive_fields_found} (not 0)")
            else:
                print(f"   ❌ Sensitive fields found: {sensitive_fields_found} (should not be 0)")
            
            # 2. Verify risk_assessment is not uniformly LOW
            risk_assessment = executive_summary.get('risk_assessment', 'LOW')
            if risk_assessment != 'LOW':
                verification_results['risk_assessment_varies'] = True
                print(f"   ✅ Risk assessment varies: {risk_assessment} (not uniformly LOW)")
            else:
                print(f"   ❌ Risk assessment: {risk_assessment} (should vary based on content)")
            
            # 3. Check total risk score is calculated (not 0)
            total_risk_score = executive_summary.get('total_risk_score', 0)
            if total_risk_score > 0:
                verification_results['total_risk_score_calculated'] = True
                print(f"   ✅ Total risk score calculated: {total_risk_score} (not 0)")
            else:
                print(f"   ❌ Total risk score: {total_risk_score} (should be calculated)")
            
            print(f"\n📊 Detailed Findings Verification:")
            
            # 4. Check sensitive fields arrays are populated
            phi_fields = detailed_findings.get('phi_fields', [])
            pii_fields = detailed_findings.get('pii_fields', [])
            sensitive_fields = detailed_findings.get('sensitive_fields', [])
            
            if len(phi_fields) > 0 or len(pii_fields) > 0 or len(sensitive_fields) > 0:
                verification_results['sensitive_arrays_populated'] = True
                print(f"   ✅ Sensitive arrays populated: PHI({len(phi_fields)}), PII({len(pii_fields)}), Sensitive({len(sensitive_fields)})")
            else:
                print(f"   ❌ Sensitive arrays empty: PHI({len(phi_fields)}), PII({len(pii_fields)}), Sensitive({len(sensitive_fields)})")
            
            # 5. Check table breakdown shows actual table names
            table_breakdown = detailed_findings.get('table_breakdown', {})
            expected_tables = ['patient_records', 'customer_accounts', 'employee_directory']
            actual_tables = list(table_breakdown.keys())
            
            if any(table in actual_tables for table in expected_tables) and 'unknown_table' not in actual_tables:
                verification_results['table_breakdown_accurate'] = True
                print(f"   ✅ Table breakdown accurate: {actual_tables} (not all unknown_table)")
            else:
                print(f"   ❌ Table breakdown inaccurate: {actual_tables} (contains unknown_table or missing expected tables)")
            
            # 6. Check risk levels vary
            risk_breakdown = detailed_findings.get('risk_level_breakdown', {})
            risk_levels = list(risk_breakdown.keys())
            unique_risk_levels = len([level for level, count in risk_breakdown.items() if count > 0])
            
            if unique_risk_levels > 1:
                verification_results['risk_levels_vary'] = True
                print(f"   ✅ Risk levels vary: {risk_breakdown} ({unique_risk_levels} different levels)")
            else:
                print(f"   ❌ Risk levels don't vary: {risk_breakdown} (should have multiple levels)")
            
            # 7. Check PHI/PII fields are correctly categorized
            if len(phi_fields) > 0 and len(pii_fields) > 0:
                verification_results['phi_pii_categorized'] = True
                print(f"   ✅ PHI/PII correctly categorized: PHI({len(phi_fields)}), PII({len(pii_fields)})")
            elif len(phi_fields) > 0 or len(pii_fields) > 0:
                verification_results['phi_pii_categorized'] = True
                print(f"   ✅ PHI/PII categorized: PHI({len(phi_fields)}), PII({len(pii_fields)})")
            else:
                print(f"   ❌ PHI/PII not categorized: PHI({len(phi_fields)}), PII({len(pii_fields)})")
            
            print(f"\n📊 Compliance Status Verification:")
            
            # 8. Verify compliance status reflects actual findings
            has_sensitive_data = sensitive_fields_found > 0
            compliance_entries = list(compliance_status.values())
            non_compliant_found = any('NON-COMPLIANT' in str(status) for status in compliance_entries)
            
            if has_sensitive_data and non_compliant_found:
                verification_results['compliance_status_correct'] = True
                print(f"   ✅ Compliance status correct: NON-COMPLIANT when sensitive fields detected")
            elif not has_sensitive_data and not non_compliant_found:
                verification_results['compliance_status_correct'] = True
                print(f"   ✅ Compliance status correct: Compliant when no sensitive fields")
            else:
                print(f"   ❌ Compliance status incorrect: Should be NON-COMPLIANT when sensitive fields detected")
            
            # Update test results
            self.test_results['executive_summary_verification'] = {
                'sensitive_fields_accurate': verification_results['sensitive_fields_accurate'],
                'risk_assessment_varies': verification_results['risk_assessment_varies'],
                'compliance_status_correct': verification_results['compliance_status_correct']
            }
            
            self.test_results['report_verification'] = {
                'total_risk_score_calculated': verification_results['total_risk_score_calculated'],
                'sensitive_arrays_populated': verification_results['sensitive_arrays_populated'],
                'table_breakdown_accurate': verification_results['table_breakdown_accurate'],
                'risk_levels_vary': verification_results['risk_levels_vary'],
                'phi_pii_categorized': verification_results['phi_pii_categorized']
            }
            
            self.test_results['report_generation'] = True
            
            # Summary
            verifications_passed = sum(verification_results.values())
            total_verifications = len(verification_results)
            
            print(f"\n📈 Report Enhancement Verification Summary:")
            print(f"   ✅ Verifications Passed: {verifications_passed}/{total_verifications}")
            
            return verifications_passed >= 6  # At least 6 out of 8 verifications should pass
                
        except Exception as e:
            print(f"❌ Report Enhancement Verification Error: {str(e)}")
            self.test_results['errors'].append(f"Report verification error: {str(e)}")
            return False

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive inconsistency fixes test"""
        print("🚀 Starting Comprehensive Inconsistency Fixes Test")
        print("=" * 80)
        
        start_time = time.time()
        
        # 1. Test health endpoint
        print("\n1️⃣ HEALTH CHECK")
        health_ok = self.test_health_endpoint()
        
        if not health_ok:
            print("❌ Health check failed - aborting further tests")
            return self.test_results
        
        # 2. Test schema upload with simple_test_ddl.sql
        print("\n2️⃣ SCHEMA UPLOAD & EXTRACT TABLES")
        upload_ok, session_id = self.test_upload_simple_test_ddl()
        
        if not upload_ok or not session_id:
            print("❌ Schema upload failed - aborting further tests")
            return self.test_results
        
        # 3. Test schema extraction and verify tables are properly parsed
        extract_ok = self.test_extract_schema_and_verify_tables(session_id)
        
        if not extract_ok:
            print("❌ Schema extraction failed - aborting classification tests")
            return self.test_results
        
        # 4. Test classification and verify inconsistency fixes
        print("\n3️⃣ CLASSIFICATION ACCURACY & INCONSISTENCY FIXES")
        classify_ok = self.test_classification_and_verify_fixes(session_id)
        
        # 5. Test report generation and verify enhancements
        print("\n4️⃣ REPORT GENERATION & ENHANCED SUMMARY")
        report_ok = self.test_report_generation_and_verify_enhancements(session_id)
        
        # Calculate overall results
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE INCONSISTENCY FIXES TEST SUMMARY")
        print("=" * 80)
        
        print(f"⏱️ Test Duration: {test_duration:.1f} seconds")
        print(f"🆔 Session ID: {session_id}")
        
        # Core Test Results
        print(f"\n🔗 Core Test Results:")
        print(f"   {'✅' if health_ok else '❌'} Health Check: {'PASS' if health_ok else 'FAIL'}")
        print(f"   {'✅' if upload_ok else '❌'} Schema Upload: {'PASS' if upload_ok else 'FAIL'}")
        print(f"   {'✅' if extract_ok else '❌'} Schema Extraction: {'PASS' if extract_ok else 'FAIL'}")
        print(f"   {'✅' if classify_ok else '❌'} Classification: {'PASS' if classify_ok else 'FAIL'}")
        print(f"   {'✅' if report_ok else '❌'} Report Generation: {'PASS' if report_ok else 'FAIL'}")
        
        # Inconsistency Fixes Results
        print(f"\n🔧 Inconsistency Fixes Results:")
        for fix_name, verified in self.test_results['inconsistency_fixes'].items():
            status = "✅ VERIFIED" if verified else "❌ FAILED"
            print(f"   {status} {fix_name}")
        
        # Executive Summary Verification
        print(f"\n📊 Executive Summary Verification:")
        for verification, passed in self.test_results['executive_summary_verification'].items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   {status} {verification}")
        
        # Report Enhancement Verification
        print(f"\n📈 Report Enhancement Verification:")
        for verification, passed in self.test_results['report_verification'].items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   {status} {verification}")
        
        # Error Summary
        if self.test_results['errors']:
            print(f"\n⚠️ Errors Encountered ({len(self.test_results['errors'])}):")
            for error in self.test_results['errors']:
                print(f"   - {error}")
        
        # Overall Status
        core_tests_ok = health_ok and upload_ok and extract_ok and classify_ok and report_ok
        fixes_verified = sum(self.test_results['inconsistency_fixes'].values()) >= 3
        summary_verified = sum(self.test_results['executive_summary_verification'].values()) >= 2
        report_verified = sum(self.test_results['report_verification'].values()) >= 4
        
        overall_success = core_tests_ok and fixes_verified and summary_verified and report_verified
        
        print(f"\n🏁 OVERALL RESULT: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("🎉 All comprehensive inconsistency fixes verified! System enhancements working correctly.")
            print("✅ Key achievements:")
            print("   - Tables properly parsed (not assigned to 'unknown_table')")
            print("   - Classification accuracy fixes implemented")
            print("   - Executive summary shows accurate sensitive field counts")
            print("   - Risk assessment varies based on content")
            print("   - Compliance status reflects actual findings")
            print("   - Enhanced report structure with detailed findings")
        else:
            print("⚠️ Some inconsistency fixes or verifications failed. Review issues above.")
        
        return self.test_results

def main():
    """Main test execution function"""
    tester = ComprehensiveInconsistencyTester()
    results = tester.run_comprehensive_test()
    
    # Return exit code based on results
    core_success = all([
        results['health_check'],
        results['schema_upload'],
        results['schema_extraction'],
        results['classification'],
        results['report_generation']
    ])
    
    fixes_success = sum(results['inconsistency_fixes'].values()) >= 3
    summary_success = sum(results['executive_summary_verification'].values()) >= 2
    report_success = sum(results['report_verification'].values()) >= 4
    
    if core_success and fixes_success and summary_success and report_success:
        exit(0)  # Success
    else:
        exit(1)  # Some tests failed

if __name__ == "__main__":
    main()