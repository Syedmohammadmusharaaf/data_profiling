#!/usr/bin/env python3
"""
Confidence Threshold Analysis Test
=================================

Specific test to analyze confidence score distribution and verify
the effectiveness of threshold increases from 50% to 70-75%.
"""

import requests
import json
import time
from typing import Dict, List, Any

class ConfidenceAnalysisTester:
    def __init__(self):
        self.base_url = "https://pii-dashboard.preview.emergentagent.com"
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def run_confidence_analysis(self):
        """Run detailed confidence analysis test"""
        print("🔍 Starting Confidence Threshold Analysis")
        print("=" * 60)
        
        # Upload comprehensive DDL
        ddl_path = "/app/test_data/comprehensive_multi_sector_ddl.sql"
        with open(ddl_path, 'r') as f:
            ddl_content = f.read()
        
        # Upload schema
        files = {'file': ('comprehensive_test.sql', ddl_content, 'text/plain')}
        headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
        
        upload_response = requests.post(
            f"{self.api_base}/upload-schema",
            files=files,
            headers=headers,
            timeout=30
        )
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.status_code}")
            return
        
        session_id = upload_response.json()['session_id']
        print(f"✅ Session created: {session_id}")
        
        # Extract schema
        extract_response = self.session.post(
            f"{self.api_base}/extract-schema/{session_id}",
            json={},
            timeout=30
        )
        
        if extract_response.status_code != 200:
            print(f"❌ Extract failed: {extract_response.status_code}")
            return
        
        extract_data = extract_response.json()
        tables_dict = extract_data.get('tables', {})
        tables = list(tables_dict.keys())
        
        print(f"📋 Extracted {len(tables)} tables")
        
        # Configure scan
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
            print(f"❌ Config failed: {config_response.status_code}")
            return
        
        # Build selected fields
        selected_fields = []
        for table_name, columns in tables_dict.items():
            for column in columns:
                selected_fields.append({
                    "table_name": table_name,
                    "column_name": column["column_name"],
                    "data_type": column["data_type"]
                })
        
        print(f"📊 Prepared {len(selected_fields)} fields for classification")
        
        # Classify
        classify_response = self.session.post(
            f"{self.api_base}/classify",
            json={
                "session_id": session_id,
                "selected_fields": selected_fields,
                "regulations": ["HIPAA", "GDPR", "CCPA"]
            },
            timeout=120
        )
        
        if classify_response.status_code != 200:
            print(f"❌ Classification failed: {classify_response.status_code}")
            return
        
        classify_data = classify_response.json()
        results = classify_data.get('results', {}).get('field_analyses', {})
        
        # Analyze confidence distribution
        self.analyze_confidence_distribution(results)
        
    def analyze_confidence_distribution(self, results: Dict):
        """Analyze confidence score distribution and threshold effectiveness"""
        print("\n📊 CONFIDENCE THRESHOLD ANALYSIS")
        print("=" * 60)
        
        confidence_ranges = {
            "0.0-0.5": 0,    # Below old threshold
            "0.5-0.7": 0,    # Between old and new threshold  
            "0.7-0.75": 0,   # New threshold range
            "0.75-0.9": 0,   # High confidence
            "0.9-1.0": 0     # Very high confidence
        }
        
        hipaa_fields = []
        gdpr_fields = []
        non_pii_fields = []
        
        total_fields = len(results)
        
        for field_key, field_data in results.items():
            confidence = field_data.get('confidence_score', 0.0)
            regulations = field_data.get('applicable_regulations', [])
            is_sensitive = field_data.get('is_sensitive', False)
            
            # Categorize by confidence range
            if confidence < 0.5:
                confidence_ranges["0.0-0.5"] += 1
            elif confidence < 0.7:
                confidence_ranges["0.5-0.7"] += 1
            elif confidence < 0.75:
                confidence_ranges["0.7-0.75"] += 1
            elif confidence < 0.9:
                confidence_ranges["0.75-0.9"] += 1
            else:
                confidence_ranges["0.9-1.0"] += 1
            
            # Categorize by regulation
            if 'HIPAA' in regulations:
                hipaa_fields.append({
                    'field': field_key,
                    'confidence': confidence,
                    'table': field_data.get('table_name', ''),
                    'is_healthcare': self.is_healthcare_context(field_data.get('table_name', ''))
                })
            elif 'GDPR' in regulations:
                gdpr_fields.append({
                    'field': field_key,
                    'confidence': confidence,
                    'table': field_data.get('table_name', '')
                })
            elif not is_sensitive:
                non_pii_fields.append({
                    'field': field_key,
                    'confidence': confidence,
                    'table': field_data.get('table_name', '')
                })
        
        # Print confidence distribution
        print("🎯 Confidence Score Distribution:")
        for range_name, count in confidence_ranges.items():
            percentage = (count / total_fields) * 100 if total_fields > 0 else 0
            print(f"   {range_name}: {count} fields ({percentage:.1f}%)")
        
        # Analyze threshold effectiveness
        print(f"\n🔍 Threshold Effectiveness Analysis:")
        
        # Fields that would have been classified under old 50% threshold
        old_threshold_fields = sum(1 for _, data in results.items() 
                                 if data.get('confidence_score', 0) >= 0.5 and data.get('is_sensitive', False))
        
        # Fields classified under new 70-75% threshold
        new_threshold_fields = sum(1 for _, data in results.items() 
                                 if data.get('confidence_score', 0) >= 0.7 and data.get('is_sensitive', False))
        
        reduction = old_threshold_fields - new_threshold_fields
        reduction_percentage = (reduction / old_threshold_fields) * 100 if old_threshold_fields > 0 else 0
        
        print(f"   📉 Fields at 50% threshold: {old_threshold_fields}")
        print(f"   📈 Fields at 70%+ threshold: {new_threshold_fields}")
        print(f"   🎯 Reduction in classifications: {reduction} ({reduction_percentage:.1f}%)")
        
        # Analyze HIPAA accuracy
        print(f"\n🏥 HIPAA Classification Analysis:")
        print(f"   Total HIPAA fields: {len(hipaa_fields)}")
        
        correct_hipaa = sum(1 for field in hipaa_fields if field['is_healthcare'])
        false_hipaa = len(hipaa_fields) - correct_hipaa
        false_hipaa_rate = (false_hipaa / len(hipaa_fields)) * 100 if hipaa_fields else 0
        
        print(f"   ✅ Correct HIPAA: {correct_hipaa}")
        print(f"   ❌ False HIPAA: {false_hipaa}")
        print(f"   📊 False HIPAA Rate: {false_hipaa_rate:.1f}%")
        
        # Show confidence distribution for HIPAA fields
        hipaa_confidences = [field['confidence'] for field in hipaa_fields]
        if hipaa_confidences:
            avg_confidence = sum(hipaa_confidences) / len(hipaa_confidences)
            min_confidence = min(hipaa_confidences)
            max_confidence = max(hipaa_confidences)
            
            print(f"   📈 HIPAA Confidence Stats:")
            print(f"      Average: {avg_confidence:.3f}")
            print(f"      Range: {min_confidence:.3f} - {max_confidence:.3f}")
        
        # Fields requiring manual review (low confidence)
        needs_review = sum(1 for _, data in results.items() 
                          if data.get('is_sensitive', False) and data.get('confidence_score', 0) < 0.8)
        
        print(f"\n⚠️ Fields Requiring Manual Review (<80% confidence): {needs_review}")
        
        # Overall assessment
        print(f"\n🏆 OVERALL ASSESSMENT:")
        if false_hipaa_rate <= 5.0:
            print(f"   ✅ EXCELLENT: {false_hipaa_rate:.1f}% false HIPAA rate (target: <5%)")
        else:
            print(f"   ❌ NEEDS IMPROVEMENT: {false_hipaa_rate:.1f}% false HIPAA rate exceeds target")
        
        if reduction_percentage > 20:
            print(f"   ✅ SIGNIFICANT IMPROVEMENT: {reduction_percentage:.1f}% reduction in overclassification")
        elif reduction_percentage > 10:
            print(f"   ⚠️ MODERATE IMPROVEMENT: {reduction_percentage:.1f}% reduction in overclassification")
        else:
            print(f"   ❌ LIMITED IMPROVEMENT: {reduction_percentage:.1f}% reduction in overclassification")
        
        return {
            'total_fields': total_fields,
            'confidence_distribution': confidence_ranges,
            'false_hipaa_rate': false_hipaa_rate,
            'threshold_reduction': reduction_percentage,
            'needs_review': needs_review
        }
    
    def is_healthcare_context(self, table_name: str) -> bool:
        """Check if table is in healthcare context"""
        healthcare_tables = {
            'patient_demographics_detailed', 'medical_patient_records', 
            'clinical_trial_participants', 'behavioral_health_sessions'
        }
        return any(ht in table_name.lower() for ht in healthcare_tables)

if __name__ == "__main__":
    tester = ConfidenceAnalysisTester()
    tester.run_confidence_analysis()