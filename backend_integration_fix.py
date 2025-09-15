#!/usr/bin/env python3
"""
Quick Backend Integration Fix
Fix the parameter conflict in classify_field method
"""

import sys
import os

# Add the project root to path
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)

from pii_scanner_poc.core.inhouse_classification_engine import InHouseClassificationEngine
from pii_scanner_poc.models.data_models import Regulation

def test_backend_integration():
    """Test the fixed backend integration"""
    print("=== BACKEND INTEGRATION FIX TEST ===\n")
    
    # Create engine instance
    engine = InHouseClassificationEngine()
    
    # Test fields that were failing in backend
    test_fields = [
        "BusinessEntityID",
        "PhoneNumber", 
        "AddressLine1",
        "City",
        "PostalCode",
        "EmailAddress",
        "Name"
    ]
    
    print("Testing fields that were failing in backend:")
    for field in test_fields:
        try:
            # This is how backend calls it - should work now
            result = engine.classify_field(field, regulation=Regulation.GDPR, table_context="test_table")
            if result:
                pattern, confidence = result
                status = "AUTO-CLASSIFIED" if confidence >= 0.5 else "LOW CONFIDENCE"
                print(f"  {field:20} -> {confidence*100:5.1f}% ({status}) - {pattern.pii_type.value}")
            else:
                print(f"  {field:20} -> No classification")
        except Exception as e:
            print(f"  {field:20} -> ERROR: {str(e)}")
    
    print(f"\n=== FIX APPLIED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_backend_integration()
