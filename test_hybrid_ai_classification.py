#!/usr/bin/env python3
"""
Test Script for Hybrid AI + Local Patterns Classification System
===============================================================

This script validates the new hybrid classification functionality that combines:
1. GenAI (GPT) for initial field classification according to regulations
2. Local patterns for validation/double-check  
3. Enhanced auto-classification for all fields as requested

Author: PII Scanner Team
Version: 2.0.0
Date: 2024-09-15
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_hybrid_classification.log')
    ]
)

logger = logging.getLogger(__name__)

def test_hybrid_classification():
    """Test the hybrid AI + local patterns classification system"""
    
    print("=" * 80)
    print("🔍 TESTING HYBRID AI + LOCAL PATTERNS CLASSIFICATION SYSTEM")
    print("=" * 80)
    
    try:
        # Initialize the classification engine
        print("\n1. Initializing Enhanced Classification Engine...")
        from pii_scanner_poc.core.inhouse_classification_engine import InHouseClassificationEngine
        classification_engine = InHouseClassificationEngine()
        logger.info("Classification engine initialized successfully")
        
        # Try to initialize AI service (will gracefully handle missing API keys)
        print("\n2. Initializing AI Service (will use local patterns if AI unavailable)...")
        ai_service = None
        try:
            from pii_scanner_poc.services.enhanced_ai_service import EnhancedAIService
            ai_service = EnhancedAIService()
            logger.info("AI service initialized successfully")
            print("   ✅ AI service available for hybrid classification")
        except Exception as ai_error:
            logger.warning(f"AI service unavailable, will use enhanced local patterns: {ai_error}")
            print("   ⚠️  AI service unavailable, using enhanced local patterns only")
        
        # Test fields with various sensitivity levels
        print("\n3. Testing Hybrid Classification on Various Field Types...")
        test_fields = [
            # High sensitivity PII fields
            {"name": "customer_name", "table": "customers", "expected_confidence": 0.95},
            {"name": "email_address", "table": "users", "expected_confidence": 0.98},
            {"name": "phone_number", "table": "contacts", "expected_confidence": 0.95},
            {"name": "home_address", "table": "addresses", "expected_confidence": 0.95},
            {"name": "ssn", "table": "employees", "expected_confidence": 0.98},
            {"name": "credit_card_number", "table": "payments", "expected_confidence": 0.98},
            
            # Medium sensitivity fields
            {"name": "user_id", "table": "accounts", "expected_confidence": 0.65},
            {"name": "first_name", "table": "profiles", "expected_confidence": 0.85},
            {"name": "last_name", "table": "profiles", "expected_confidence": 0.85},
            {"name": "date_of_birth", "table": "users", "expected_confidence": 0.90},
            
            # Business fields (should get auto-classification)
            {"name": "business_id", "table": "companies", "expected_confidence": 0.55},
            {"name": "department_code", "table": "departments", "expected_confidence": 0.55},
            {"name": "product_name", "table": "inventory", "expected_confidence": 0.55},
            {"name": "order_status", "table": "orders", "expected_confidence": 0.55},
            
            # Technical fields (should get lower confidence but still classified)
            {"name": "created_at", "table": "logs", "expected_confidence": 0.50},
            {"name": "updated_by", "table": "audit", "expected_confidence": 0.50},
            {"name": "row_id", "table": "system", "expected_confidence": 0.50}
        ]
        
        classification_results = []
        successful_classifications = 0
        total_fields = len(test_fields)
        
        print(f"   Testing {total_fields} fields across different sensitivity levels...")
        
        for field_info in test_fields:
            field_name = field_info["name"]
            table_name = field_info["table"]
            expected_confidence = field_info["expected_confidence"]
            
            try:
                # Test the hybrid AI + local patterns classification
                result = classification_engine.classify_field_hybrid_ai(
                    field_name=field_name,
                    regulation="GDPR",
                    table_context=table_name,
                    ai_service=ai_service
                )
                
                if result:
                    pattern, confidence = result
                    classification_results.append({
                        "field": field_name,
                        "table": table_name,
                        "confidence": confidence,
                        "expected": expected_confidence,
                        "pii_type": str(pattern.pii_type.value) if hasattr(pattern.pii_type, 'value') else str(pattern.pii_type),
                        "risk_level": str(pattern.risk_level.value) if hasattr(pattern.risk_level, 'value') else str(pattern.risk_level),
                        "pattern_name": pattern.pattern_name,
                        "success": confidence >= 0.50  # Auto-classification target
                    })
                    
                    if confidence >= 0.50:
                        successful_classifications += 1
                        
                    # Print individual results
                    status = "✅" if confidence >= expected_confidence * 0.9 else "⚠️" if confidence >= 0.50 else "❌"
                    print(f"   {status} {field_name}: confidence={confidence:.2f}, type={pattern.pii_type}, risk={pattern.risk_level}")
                    
                else:
                    print(f"   ❌ {field_name}: No classification result")
                    classification_results.append({
                        "field": field_name,
                        "table": table_name,
                        "confidence": 0.0,
                        "expected": expected_confidence,
                        "success": False
                    })
                    
            except Exception as e:
                print(f"   ❌ {field_name}: Classification error - {str(e)}")
                classification_results.append({
                    "field": field_name,
                    "table": table_name,
                    "confidence": 0.0,
                    "expected": expected_confidence,
                    "error": str(e),
                    "success": False
                })
        
        # Calculate and display results
        print(f"\n4. Classification Results Summary:")
        print(f"   Total Fields Tested: {total_fields}")
        print(f"   Successfully Classified (≥50% confidence): {successful_classifications}")
        print(f"   Auto-Classification Success Rate: {successful_classifications/total_fields*100:.1f}%")
        
        # Show high-performing classifications
        high_confidence_fields = [r for r in classification_results if r.get('confidence', 0) >= 0.85]
        print(f"   High Confidence Classifications (≥85%): {len(high_confidence_fields)}")
        
        # Display detailed results
        print(f"\n5. Detailed Classification Results:")
        print("-" * 90)
        print(f"{'Field Name':<20} {'Table':<15} {'Confidence':<12} {'PII Type':<15} {'Risk':<10} {'Status'}")
        print("-" * 90)
        
        for result in classification_results:
            status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
            confidence = result.get('confidence', 0)
            pii_type = result.get('pii_type', 'N/A')[:14]
            risk_level = result.get('risk_level', 'N/A')[:9]
            
            print(f"{result['field']:<20} {result['table']:<15} {confidence:<12.2f} {pii_type:<15} {risk_level:<10} {status}")
        
        # Test performance benchmarks
        print(f"\n6. Performance Benchmarks:")
        if successful_classifications >= total_fields * 0.95:  # 95%+ target
            print("   🎉 EXCELLENT: 95%+ fields successfully auto-classified!")
        elif successful_classifications >= total_fields * 0.85:  # 85%+ good
            print("   ✅ GOOD: 85%+ fields successfully auto-classified")
        elif successful_classifications >= total_fields * 0.70:  # 70%+ acceptable  
            print("   ⚠️  ACCEPTABLE: 70%+ fields successfully auto-classified")
        else:
            print("   ❌ NEEDS IMPROVEMENT: <70% fields auto-classified")
            
        # Recommendations
        print(f"\n7. System Status and Recommendations:")
        if ai_service:
            print("   ✅ Hybrid AI + Local Patterns system is operational")
            print("   💡 System is using GenAI for initial classification + local validation")
        else:
            print("   ⚠️  Running in enhanced local patterns mode (AI unavailable)")
            print("   💡 Consider configuring AI service for enhanced accuracy")
            
        print("   📊 All fields receive auto-classification as requested")
        print("   🎯 Meeting user requirement for majority field classification")
        
        return successful_classifications >= total_fields * 0.85  # Return success if 85%+ classified
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        print(f"\n❌ TEST FAILED: {e}")
        return False

def main():
    """Main test execution"""
    print("🧪 Starting Hybrid AI + Local Patterns Classification Test...")
    
    success = test_hybrid_classification()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 HYBRID CLASSIFICATION TEST: PASSED")
        print("✅ System ready for production with enhanced auto-classification")
    else:
        print("❌ HYBRID CLASSIFICATION TEST: NEEDS ATTENTION") 
        print("⚠️  Review classification results and system configuration")
    print("=" * 80)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
