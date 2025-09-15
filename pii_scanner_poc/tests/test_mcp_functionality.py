#!/usr/bin/env python3
"""
MCP Functionality Test Script
Test MCP server functionality with timeout-aware processing
"""

import sys
import tempfile
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_mcp_single_table():
    """Test MCP with single table (should work)"""
    print("🔗 Testing MCP with single table...")
    
    try:
        from mcp_server import analyze_schema_data
        
        # Single table schema
        single_table_schema = """table_name,column_name,data_type
users,id,INT
users,email,VARCHAR(100)
users,name,VARCHAR(50)"""
        
        result = analyze_schema_data(
            schema_data=single_table_schema,
            data_format="csv", 
            regulations=["GDPR", "HIPAA"]
        )
        
        print("✅ Single table analysis completed")
        print(f"Result length: {len(result)} characters")
        print("Sample:", result[:200] + "..." if len(result) > 200 else result)
        return True
        
    except Exception as e:
        print(f"❌ Single table test failed: {e}")
        return False

def test_mcp_multiple_tables():
    """Test MCP with multiple tables (may timeout with old code)"""
    print("🔗 Testing MCP with multiple tables...")
    
    try:
        from mcp_server import analyze_schema_data
        
        # Multiple tables schema
        multiple_tables_schema = """table_name,column_name,data_type
users,id,INT
users,email,VARCHAR(100)
users,first_name,VARCHAR(50)
users,last_name,VARCHAR(50)
users,phone,VARCHAR(20)
users,address,TEXT
orders,id,INT
orders,user_id,INT
orders,order_date,DATETIME
orders,total_amount,DECIMAL(10,2)
orders,billing_address,TEXT
products,id,INT
products,name,VARCHAR(100)
products,price,DECIMAL(8,2)
products,description,TEXT"""
        
        result = analyze_schema_data(
            schema_data=multiple_tables_schema,
            data_format="csv", 
            regulations=["GDPR"]
        )
        
        print("✅ Multiple tables analysis completed")
        print(f"Result length: {len(result)} characters")
        print("Sample:", result[:200] + "..." if len(result) > 200 else result)
        return True
        
    except Exception as e:
        print(f"❌ Multiple tables test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_enhanced_mcp():
    """Test enhanced MCP server"""
    print("🔗 Testing Enhanced MCP server...")
    
    try:
        from mcp_server_enhanced import EnhancedMCPServer
        import asyncio
        
        server = EnhancedMCPServer()
        
        # Test schema content analysis
        test_schema = """CREATE TABLE test_table (
    id INT PRIMARY KEY,
    email VARCHAR(100),
    name VARCHAR(50)
);"""
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(server._analyze_schema_content({
                'schema_content': test_schema,
                'content_format': 'ddl',
                'regulations': ['GDPR']
            }))
            
            print("✅ Enhanced MCP analysis completed")
            print(f"Result type: {type(result)}")
            if isinstance(result, dict):
                print(f"Result keys: {list(result.keys())}")
            
            return True
            
        finally:
            loop.close()
        
    except Exception as e:
        print(f"❌ Enhanced MCP test failed: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 MCP Functionality Test Suite")
    print("=" * 40)
    
    tests = [
        ("Single Table MCP", test_mcp_single_table),
        ("Multiple Tables MCP", test_mcp_multiple_tables),
        ("Enhanced MCP", test_enhanced_mcp)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All MCP tests passed!")
    elif passed > 0:
        print("⚠️ Some MCP tests passed, check failures above")
    else:
        print("❌ All MCP tests failed")

if __name__ == "__main__":
    main()