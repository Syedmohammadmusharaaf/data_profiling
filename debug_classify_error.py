#!/usr/bin/env python3
"""
Debug script to reproduce the classify_field parameter error
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pii_scanner_poc'))

from pii_scanner_poc.core.inhouse_classification_engine import InHouseClassificationEngine
from pii_scanner_poc.models.enums import Regulation

def test_classify_field_call():
    """Test the exact call pattern from backend"""
    try:
        # Initialize engine
        inhouse_engine = InHouseClassificationEngine()
        
        # Test the exact call pattern from backend/main.py line 844-845
        field_name = "customer_id"
        regulation = Regulation.GDPR
        table_name = "customers"
        
        print(f"Testing classify_field with:")
        print(f"  field_name: {field_name}")
        print(f"  regulation: {regulation}")
        print(f"  table_context: {table_name}")
        
        # This is the exact call from backend/main.py line 844-845
        classification_result = inhouse_engine.classify_field(
            field_name, regulation=regulation, table_context=table_name
        )
        
        print(f"Classification result: {classification_result}")
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_classify_field_call()
