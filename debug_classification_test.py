#!/usr/bin/env python3

"""Debug classification test to understand why patterns aren't matching"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from pii_scanner_poc.core.inhouse_classification_engine import InHouseClassificationEngine
from pii_scanner_poc.core.configuration import Regulation

def test_single_field():
    """Test single field classification in detail"""
    
    # Initialize classification engine directly
    engine = InHouseClassificationEngine()
    
    # Test a few key fields that should be caught by aggressive patterns
    test_fields = [
        'employee_id',  # Should be caught by aggressive ID patterns
        'product_id',   # Should be caught by aggressive ID patterns
        'status',       # Should be caught by aggressive status patterns
        'type',         # Should be caught by aggressive classification patterns
        'description',  # Should be caught by aggressive descriptive patterns
        'created_date', # Should be caught by aggressive date patterns
        'amount',       # Should be caught by aggressive measurement patterns
        'position'      # Should be caught by medium patterns or fallback
    ]
    
    print("=== DEBUG SINGLE FIELD CLASSIFICATION ===")
    
    for field in test_fields:
        print(f"\nTesting field: {field}")
        result = engine.classify_field(
            field_name=field,
            regulation=Regulation.GDPR,
            table_context=None
        )
        
        if result:
            pattern, confidence = result
            confidence_pct = confidence * 100
            category = "HIGH" if confidence_pct >= 90 else "MEDIUM" if confidence_pct >= 50 else "LOW"
            pii_type = pattern.pii_type.name if hasattr(pattern.pii_type, 'name') else str(pattern.pii_type)
            print(f"  Result: {confidence_pct:.1f}% ({category}) - {pii_type}")
            print(f"  Pattern ID: {pattern.pattern_id}")
            print(f"  Pattern Name: {pattern.pattern_name}")
        else:
            print(f"  Result: NO MATCH")

if __name__ == "__main__":
    test_single_field()
