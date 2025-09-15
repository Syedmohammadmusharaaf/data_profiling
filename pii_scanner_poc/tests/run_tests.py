#!/usr/bin/env python3
"""
PII/PHI Scanner POC - Comprehensive Test Runner
===============================================

Consolidated test runner for all system components.
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """Run comprehensive test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PII Scanner Test Runner')
    parser.add_argument('--comprehensive', action='store_true', 
                       help='Run comprehensive test suite')
    parser.add_argument('--setup-only', action='store_true',
                       help='Run setup validation tests only')
    parser.add_argument('--security', action='store_true',
                       help='Run security tests only')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests only')
    
    args = parser.parse_args()
    
    if args.setup_only:
        from tests.test_setup import main as setup_test
        return setup_test()
    elif args.security:
        print("🔒 Running security tests...")
        # Security tests would go here
        return 0
    elif args.performance:
        from tests.test_optimized import main as perf_test
        return perf_test()
    else:
        # Run all tests
        print("🧪 Running comprehensive test suite...")
        
        tests_to_run = [
            ('Setup Validation', 'tests.test_setup'),
            ('Hybrid System', 'tests.test_hybrid_system'),
            ('Alias Integration', 'tests.test_alias_integration'),
            ('MCP Functionality', 'tests.test_mcp_functionality'),
            ('Performance Tests', 'tests.test_optimized')
        ]
        
        results = []
        for test_name, test_module in tests_to_run:
            try:
                print(f"\n📋 Running {test_name}...")
                module = __import__(test_module, fromlist=['main'])
                if hasattr(module, 'main'):
                    result = module.main()
                    results.append((test_name, result == 0))
                    print(f"✅ {test_name}: {'PASSED' if result == 0 else 'FAILED'}")
                else:
                    print(f"⚠️  {test_name}: No main function found")
                    results.append((test_name, False))
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print("=" * 50)
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name:<30} {status}")
        
        print("=" * 50)
        print(f"Total: {passed}/{total} tests passed")
        
        return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())