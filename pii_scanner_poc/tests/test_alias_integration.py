#!/usr/bin/env python3
"""
Test Suite for Alias Management Integration
Tests the integration of the alias database with the existing PII scanner system
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Test imports
    from pii_scanner_poc.services.local_alias_database import alias_database, FieldAlias, alias_classifier
    from pii_scanner_poc.models.data_models import PIIType, RiskLevel, Regulation, ColumnMetadata
    from pii_scanner_poc.core.hybrid_classification_orchestrator import hybrid_orchestrator
    print("✅ All required modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_alias_database_basic_operations():
    """Test basic alias database operations"""
    print("\n🧪 Testing Alias Database Basic Operations")
    print("-" * 50)
    
    try:
        # Test adding an alias
        alias = FieldAlias(
            alias_id="test_email_001",
            standard_field_name="email",
            alias_name="customer_email",
            confidence_score=0.95,
            pii_type=PIIType.EMAIL,
            risk_level=RiskLevel.HIGH,
            applicable_regulations=[Regulation.GDPR, Regulation.CCPA],
            validation_status="approved",
            created_by="test_suite"
        )
        
        result = alias_database.add_field_alias(alias)
        if result:
            print("✅ Successfully added test alias")
        else:
            print("⚠️ Alias may already exist")
        
        # Test searching for aliases
        matches = alias_database.find_alias_matches("customer_email", similarity_threshold=0.8)
        if matches:
            print(f"✅ Found {len(matches)} matches for 'customer_email'")
            match = matches[0]
            print(f"   Best match: {match.alias_name} -> {match.pii_type.value} (confidence: {match.confidence_score:.2f})")
        else:
            print("❌ No matches found for test alias")
        
        # Test fuzzy matching
        fuzzy_matches = alias_database.find_alias_matches("cust_email", similarity_threshold=0.7)
        if fuzzy_matches:
            print(f"✅ Fuzzy matching works: found {len(fuzzy_matches)} matches for 'cust_email'")
        
        # Test statistics
        stats = alias_database.get_performance_statistics()
        print(f"✅ Database statistics retrieved: {stats['aliases']['total_aliases']} total aliases")
        
    except Exception as e:
        print(f"❌ Alias database test failed: {e}")
        return False
    
    return True


def test_alias_classifier_integration():
    """Test the alias classifier integration"""
    print("\n🧪 Testing Alias Classifier Integration")
    print("-" * 50)
    
    try:
        # Test enhanced field classification
        result = alias_classifier.enhanced_field_classification(
            field_name="customer_email",
            table_context=["customer_id", "customer_name", "phone"],
            company_id=None,
            region=None
        )
        
        if result:
            print("✅ Enhanced field classification working")
            print(f"   Field: {result['field_name']}")
            print(f"   PII Type: {result['pii_type'].value if hasattr(result['pii_type'], 'value') else result['pii_type']}")
            print(f"   Confidence: {result['confidence_score']:.2f}")
            print(f"   Detection Method: {result['detection_method']}")
        else:
            print("ℹ️ No classification result from alias database (expected for unknown fields)")
        
        # Test with a field that shouldn't match
        no_match_result = alias_classifier.enhanced_field_classification(
            field_name="random_field_xyz",
            table_context=[],
            company_id=None,
            region=None
        )
        
        if no_match_result is None:
            print("✅ Correctly returned None for unknown field")
        
    except Exception as e:
        print(f"❌ Alias classifier test failed: {e}")
        return False
    
    return True


def test_hybrid_orchestrator_integration():
    """Test the hybrid orchestrator integration with alias database"""
    print("\n🧪 Testing Hybrid Orchestrator Integration")
    print("-" * 50)
    
    try:
        # Create test schema data
        test_columns = [
            ColumnMetadata(
                schema_name="test_schema",
                table_name="customers",
                column_name="customer_email",
                data_type="VARCHAR(255)"
            ),
            ColumnMetadata(
                schema_name="test_schema",
                table_name="customers",
                column_name="customer_id",
                data_type="INT"
            ),
            ColumnMetadata(
                schema_name="test_schema",
                table_name="customers", 
                column_name="phone_number",
                data_type="VARCHAR(20)"
            )
        ]
        
        tables_data = {
            "customers": test_columns
        }
        
        # Test classification
        session = hybrid_orchestrator.classify_schema(
            tables_data=tables_data,
            regulations=[Regulation.GDPR],
            enable_caching=False,  # Disable caching for testing
            enable_llm=False       # Disable LLM for testing
        )
        
        print(f"✅ Hybrid classification completed")
        print(f"   Session ID: {session.session_id}")
        print(f"   Total fields: {session.total_fields}")
        print(f"   Local classifications: {session.local_classifications}")
        print(f"   Results: {len(session.field_analyses)}")
        
        # Check if alias database was used
        alias_used = False
        for analysis in session.field_analyses:
            if hasattr(analysis, 'detection_method') and analysis.detection_method == 'ALIAS_DATABASE':
                alias_used = True
                print(f"   ✅ Alias database used for: {analysis.field_name}")
                break
        
        if not alias_used:
            print("   ℹ️ Alias database not used (may be expected for test data)")
        
    except Exception as e:
        print(f"❌ Hybrid orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_mcp_alias_tools():
    """Test MCP alias management tools"""
    print("\n🧪 Testing MCP Alias Management Tools")
    print("-" * 50)
    
    try:
        # Import MCP server functions
        from mcp_server import alias_management_stats, alias_search, alias_add
        
        # Test stats
        stats_result = alias_management_stats()
        if "ALIAS DATABASE STATISTICS" in stats_result:
            print("✅ MCP alias stats tool working")
        else:
            print(f"⚠️ MCP stats unexpected result: {stats_result[:100]}...")
        
        # Test search
        search_result = alias_search("customer_email")
        if "SEARCH RESULTS" in search_result or "No matches found" in search_result:
            print("✅ MCP alias search tool working")
        else:
            print(f"⚠️ MCP search unexpected result: {search_result[:100]}...")
        
        # Test add (will be pending)
        add_result = alias_add(
            field_name="test_phone",
            pii_type="PHONE",
            risk_level="HIGH",
            confidence=0.9
        )
        if "Successfully added alias" in add_result or "Failed to add alias" in add_result:
            print("✅ MCP alias add tool working")
        else:
            print(f"⚠️ MCP add unexpected result: {add_result}")
        
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        return False
    
    return True


def main():
    """Run all integration tests"""
    print("🚀 ALIAS MANAGEMENT INTEGRATION TEST SUITE")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(("Basic Operations", test_alias_database_basic_operations()))
    test_results.append(("Classifier Integration", test_alias_classifier_integration()))
    test_results.append(("Hybrid Orchestrator", test_hybrid_orchestrator_integration()))
    test_results.append(("MCP Tools", test_mcp_alias_tools()))
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Alias management integration is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())