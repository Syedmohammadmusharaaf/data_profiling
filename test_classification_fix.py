#!/usr/bin/env python3
"""
Test script to verify PII classification engine fixes.
This will test dynamic confidence scoring vs static 80% scores.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'pii_scanner_poc'))

def test_classification_engine():
    print("Testing PII Classification Engine...")
    print("=" * 50)
    
    try:
        from core.inhouse_classification_engine import InHouseClassificationEngine
        from models.column_metadata import ColumnMetadata
        print("✓ Imports successful!")
        
        engine = InHouseClassificationEngine()
        print("✓ Engine initialized!")
        
        # Test cases for high-sensitivity PII fields
        high_sensitivity_fields = [
            ('email_address', 'VARCHAR'),
            ('phone_number', 'VARCHAR'),
            ('first_name', 'VARCHAR'),
            ('last_name', 'VARCHAR'),
            ('social_security_number', 'VARCHAR'),
            ('home_address', 'TEXT')
        ]
        
        # Test cases for low-sensitivity technical fields  
        low_sensitivity_fields = [
            ('record_id', 'INTEGER'),
            ('created_at', 'TIMESTAMP'),
            ('status_code', 'INTEGER'),
            ('session_token', 'VARCHAR'),
            ('system_flag', 'BOOLEAN'),
            ('row_count', 'INTEGER')
        ]
        
        print("\nHIGH SENSITIVITY FIELDS (should get 90-98% confidence + HIGH risk):")
        print("-" * 70)
        for field_name, data_type in high_sensitivity_fields:
            try:
                field = ColumnMetadata(field_name, data_type, '', 'test_table')
                result = engine.classify_field(field)
                confidence_pct = result[1] * 100
                risk_level = result[0].risk_level
                pii_type = result[0].pii_type
                
                print(f"Field: {field_name:20} | Confidence: {confidence_pct:5.1f}% | Risk: {risk_level} | Type: {pii_type}")
                
            except Exception as e:
                print(f"Field: {field_name:20} | ERROR: {e}")
        
        print("\nLOW SENSITIVITY FIELDS (should get 5-20% confidence + LOW risk):")
        print("-" * 70)
        for field_name, data_type in low_sensitivity_fields:
            try:
                field = ColumnMetadata(field_name, data_type, '', 'test_table')
                result = engine.classify_field(field)
                confidence_pct = result[1] * 100
                risk_level = result[0].risk_level
                pii_type = result[0].pii_type
                
                print(f"Field: {field_name:20} | Confidence: {confidence_pct:5.1f}% | Risk: {risk_level} | Type: {pii_type}")
                
            except Exception as e:
                print(f"Field: {field_name:20} | ERROR: {e}")
        
        print("\n" + "=" * 50)
        print("✓ Classification test completed!")
        print("\nExpected Results:")
        print("- High sensitivity fields should show 90-98% confidence + HIGH risk")
        print("- Low sensitivity fields should show 5-20% confidence + LOW risk") 
        print("- No more static 80% scores for all fields!")
        
    except Exception as e:
        print(f"❌ Import/Setup Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_classification_engine()
