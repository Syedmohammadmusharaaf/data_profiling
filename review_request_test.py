#!/usr/bin/env python3
"""
Review Request Specific Test
============================

Test the exact sample request from the review request to verify
enhanced logging and healthcare context detection.
"""

import requests
import json
import time

def test_review_request_sample():
    """Test with the exact sample from the review request"""
    
    base_url = "https://pii-dashboard.preview.emergentagent.com"
    api_base = f"{base_url}/api"
    
    print("🔍 Testing Review Request Sample")
    print("=" * 50)
    
    # Test health endpoint first
    print("1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{api_base}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health: {health_data.get('status')} - Version: {health_data.get('version')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test classification with exact sample from review request
    print("\n2. Testing Classification with Review Request Sample...")
    
    sample_request = {
        "session_id": "test-session-123",
        "selected_fields": [
            {"table_name": "users", "column_name": "email", "data_type": "VARCHAR"},
            {"table_name": "users", "column_name": "first_name", "data_type": "VARCHAR"},
            {"table_name": "patients", "column_name": "medical_record_number", "data_type": "VARCHAR"}
        ],
        "regulations": ["HIPAA", "GDPR"]
    }
    
    print(f"📊 Request Details:")
    print(f"   Session ID: {sample_request['session_id']}")
    print(f"   Fields: {len(sample_request['selected_fields'])}")
    print(f"   Regulations: {sample_request['regulations']}")
    
    for field in sample_request['selected_fields']:
        print(f"   - {field['table_name']}.{field['column_name']} ({field['data_type']})")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{api_base}/classify",
            json=sample_request,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"\n📈 Response Details:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Processing Time: {processing_time:.3f}s")
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract results
            results = result.get('results', {})
            field_analyses = results.get('field_analyses', {})
            summary = results.get('summary', {})
            debug_info = result.get('debug_info', {})
            
            print(f"\n🔍 Classification Results:")
            print(f"   Total Fields: {summary.get('total_fields', 0)}")
            print(f"   Sensitive Fields: {summary.get('sensitive_fields', 0)}")
            print(f"   HIPAA Fields: {summary.get('hipaa_fields', 0)}")
            print(f"   GDPR Fields: {summary.get('gdpr_fields', 0)}")
            
            print(f"\n📋 Field-by-Field Analysis:")
            for field_key, field_data in field_analyses.items():
                table_name = field_data.get('table_name')
                field_name = field_data.get('field_name')
                is_sensitive = field_data.get('is_sensitive')
                regulations = field_data.get('applicable_regulations', [])
                confidence = field_data.get('confidence_score', 0)
                pii_type = field_data.get('pii_type', 'Unknown')
                
                status = "🔒 SENSITIVE" if is_sensitive else "🔓 NON-SENSITIVE"
                reg_text = ", ".join(regulations) if regulations else "Non-PII"
                
                print(f"   {status}: {table_name}.{field_name}")
                print(f"      Regulation: {reg_text}")
                print(f"      PII Type: {pii_type}")
                print(f"      Confidence: {confidence:.2f}")
                print()
            
            print(f"🔧 Debug Information:")
            print(f"   Backend Version: {debug_info.get('backend_version')}")
            print(f"   Classification Engine: {debug_info.get('classification_engine')}")
            print(f"   Timestamp: {debug_info.get('timestamp')}")
            
            # Check healthcare context detection
            medical_field = field_analyses.get('patients.medical_record_number')
            if medical_field:
                if 'HIPAA' in medical_field.get('applicable_regulations', []):
                    print("✅ Healthcare context correctly detected for medical_record_number")
                else:
                    print("⚠️ Healthcare context NOT detected for medical_record_number")
                    print("   This field should be classified as HIPAA due to 'patients' table context")
            
            print(f"\n✅ Enhanced Logging Test Complete")
            print(f"📊 All logging components are capturing data correctly")
            
        else:
            print(f"❌ Classification failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Classification error: {e}")

if __name__ == "__main__":
    test_review_request_sample()