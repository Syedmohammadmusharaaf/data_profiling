#!/usr/bin/env python3
"""
Test Hybrid AI + Local Patterns Classification
==============================================

This script validates the new hybrid classification system that combines:
1. GenAI (GPT) for initial field classification according to regulations
2. Local patterns for validation and double-check
3. Enhanced confidence scoring and final auto-classification

Usage: python test_hybrid_classification.py
"""

import sys
import os
import asyncio
import time

# Add the project path to sys.path
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('./pii_scanner_poc'))

from pii_scanner_poc.core.inhouse_classification_engine import InHouseClassificationEngine
from pii_scanner_poc.services.enhanced_ai_service import EnhancedAIService
from pii_scanner_poc.models.data_models import Regulation

def test_hybrid_classification():
    """Test the new hybrid AI + local patterns classification"""
    
    print("=" * 80)
    print("🚀 Testing Hybrid AI + Local Patterns Classification")
    print("=" * 80)
    
    # Initialize classification engine
    print("\n📚 Initializing Classification Engine...")
    try:
        classification_engine = InHouseClassificationEngine()
        print("✅ Classification engine initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize classification engine: {e}")
        return
    
    # Initialize AI service
    print("\n🤖 Initializing AI Service...")
    ai_service = None
    try:
        ai_service = EnhancedAIService()
        print("✅ AI service initialized successfully")
    except Exception as e:
        print(f"⚠️  AI service initialization failed (will test local patterns only): {e}")
    
    # Test fields - mix of high-confidence PII and business fields
    test_fields = [
        # High-confidence PII fields
        ("customer_name", "customers", "GDPR"),
        ("email_address", "users", "GDPR"), 
        ("phone_number", "contacts", "GDPR"),
        ("home_address", "addresses", "GDPR"),
        ("ssn", "employees", "GDPR"),
        ("password_hash", "authentication", "GDPR"),
        
        # Medium-confidence business fields
        ("user_id", "users", "GDPR"),
        ("account_balance", "accounts", "GDPR"),
        ("order_date", "orders", "GDPR"),
        ("product_name", "products", "GDPR"),
        
        # Low-confidence technical fields
        ("id", "table1", "GDPR"),
        ("created_at", "logs", "GDPR"),
        ("status", "transactions", "GDPR"),
        ("version", "metadata", "GDPR"),
    ]
    
    print(f"\n🔬 Testing {len(test_fields)} fields with hybrid classification...")
    print("-" * 80)
    
    results = []
    total_start_time = time.time()
    
    for field_name, table_name, regulation in test_fields:
        print(f"\n🔍 Testing field: {field_name} (table: {table_name}, regulation: {regulation})")
        
        # Test hybrid classification
        hybrid_start_time = time.time()
        hybrid_result = None
        hybrid_confidence = 0.0
        
        try:
            hybrid_result = classification_engine.classify_field_hybrid_ai(
                field_name=field_name,
                regulation=regulation,
                table_context=table_name,
                ai_service=ai_service
            )
            
            if hybrid_result:
                pattern, hybrid_confidence = hybrid_result
                hybrid_time = time.time() - hybrid_start_time
                
                print(f"  🎯 Hybrid Result: {pattern.pattern_name}")
                print(f"  📊 Confidence: {hybrid_confidence:.3f} ({hybrid_confidence*100:.1f}%)")
                print(f"  🏷️  PII Type: {pattern.pii_type}")
                print(f"  ⚠️  Risk Level: {pattern.risk_level}")
                print(f"  ⚡ Processing Time: {hybrid_time:.3f}s")
                
                results.append({
                    'field': field_name,
                    'table': table_name,
                    'hybrid_confidence': hybrid_confidence,
                    'pii_type': str(pattern.pii_type),
                    'risk_level': str(pattern.risk_level),
                    'pattern_name': pattern.pattern_name,
                    'processing_time': hybrid_time
                })
            else:
                print("  ❌ No hybrid classification result")
                
        except Exception as e:
            print(f"  ❌ Hybrid classification error: {e}")
            
        # For comparison, test local-only classification
        local_start_time = time.time()
        try:
            local_result = classification_engine.classify_field(
                field_name=field_name,
                regulation=regulation,
                table_context=table_name
            )
            
            if local_result:
                local_pattern, local_confidence = local_result
                local_time = time.time() - local_start_time
                print(f"  🏠 Local-Only Confidence: {local_confidence:.3f} ({local_confidence*100:.1f}%)")
                print(f"  ⚡ Local Processing Time: {local_time:.3f}s")
            else:
                print("  🏠 Local-Only: No result")
                
        except Exception as e:
            print(f"  🏠 Local classification error: {e}")
    
    # Summary statistics
    total_time = time.time() - total_start_time
    print("\n" + "=" * 80)
    print("📈 HYBRID CLASSIFICATION RESULTS SUMMARY")
    print("=" * 80)
    
    if results:
        high_confidence_count = len([r for r in results if r['hybrid_confidence'] > 0.7])
        medium_confidence_count = len([r for r in results if 0.4 <= r['hybrid_confidence'] <= 0.7])
        auto_classified_count = len([r for r in results if r['hybrid_confidence'] > 0.5])
        
        avg_confidence = sum(r['hybrid_confidence'] for r in results) / len(results)
        avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
        
        print(f"Total Fields Tested: {len(results)}")
        print(f"High Confidence (>70%): {high_confidence_count} ({high_confidence_count/len(results)*100:.1f}%)")
        print(f"Medium Confidence (40-70%): {medium_confidence_count} ({medium_confidence_count/len(results)*100:.1f}%)")
        print(f"Auto-Classified (>50%): {auto_classified_count} ({auto_classified_count/len(results)*100:.1f}%)")
        print(f"Average Confidence: {avg_confidence:.3f} ({avg_confidence*100:.1f}%)")
        print(f"Average Processing Time: {avg_processing_time:.3f}s")
        print(f"Total Processing Time: {total_time:.3f}s")
        
        # Show top results
        print("\n🏆 TOP CONFIDENCE RESULTS:")
        sorted_results = sorted(results, key=lambda x: x['hybrid_confidence'], reverse=True)
        for i, result in enumerate(sorted_results[:5], 1):
            print(f"{i}. {result['field']}: {result['hybrid_confidence']:.3f} ({result['hybrid_confidence']*100:.1f}%) - {result['pattern_name']}")
            
        print("\n✅ Hybrid AI + Local Patterns classification test completed successfully!")
        
        # Check if we meet the user's requirements
        auto_classification_rate = auto_classified_count / len(results) * 100
        if auto_classification_rate >= 90:
            print(f"🎉 EXCELLENT: {auto_classification_rate:.1f}% auto-classification rate achieved!")
        elif auto_classification_rate >= 70:
            print(f"✅ GOOD: {auto_classification_rate:.1f}% auto-classification rate achieved!")
        else:
            print(f"⚠️  NEEDS IMPROVEMENT: {auto_classification_rate:.1f}% auto-classification rate")
    else:
        print("❌ No classification results to analyze")
        
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_hybrid_classification()
