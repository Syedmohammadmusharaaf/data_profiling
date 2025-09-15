#!/usr/bin/env python3
"""
Simple Demo for PII/PHI Scanner POC
Quick demonstration of the scanner capabilities
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Simple demo of scanner functionality"""
    print("🔐 PII/PHI Scanner POC - Quick Demo")
    print("=" * 50)
    
    try:
        # Test core imports
        from pii_scanner_poc.core.pii_scanner_facade import pii_scanner
        print("✅ Core scanner imported successfully")
        
        # Test configuration
        config_result = pii_scanner.validate_configuration()
        if config_result['valid']:
            print("✅ Configuration validation passed")
        else:
            print("⚠️  Configuration has warnings (expected in demo mode)")
            for warning in config_result.get('warnings', []):
                print(f"   ⚠️  {warning}")
        
        # Create simple test DDL
        test_ddl = '''
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone_number VARCHAR(20)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    total_amount DECIMAL(10,2)
);
'''
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ddl', delete=False) as f:
            f.write(test_ddl)
            temp_file = f.name
        
        print(f"\n🔍 Analyzing test schema...")
        print("📋 Regulations: GDPR")
        
        try:
            # Use facade to analyze
            results = pii_scanner.analyze_schema_file(
                schema_file_path=temp_file,
                regulations=["GDPR"],
                output_format="json"
            )
            
            if isinstance(results, dict) and 'error' not in results:
                print("✅ Analysis completed successfully!")
                
                # Display results summary
                if 'table_results' in results:
                    table_results = results['table_results']
                    print(f"📊 Analyzed {len(table_results)} tables")
                    
                    for table in table_results:
                        if hasattr(table, 'table_name'):
                            print(f"   📋 {table.table_name}: {table.sensitive_columns} sensitive columns")
                
                if 'session_id' in results:
                    print(f"🔍 Session ID: {results['session_id']}")
                    
            else:
                print("⚠️  Analysis completed with configuration warnings")
                if 'error' in results:
                    print(f"   ❌ {results['error']}")
                    
        except Exception as e:
            print(f"⚠️  Analysis failed (expected without API key): {e}")
            
        finally:
            # Cleanup
            import os
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        print("\n💡 Demo completed!")
        print("   To run full analysis with API key:")
        print("   python main.py analyze --ddl examples/sample_schema.ddl --regulations GDPR HIPAA")
        
        return 0
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())