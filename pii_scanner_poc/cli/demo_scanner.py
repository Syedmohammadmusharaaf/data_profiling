#!/usr/bin/env python3
"""
Demo PII/PHI Scanner Script
===========================

This demonstration script showcases the PII/PHI Scanner functionality without
requiring actual Azure OpenAI API credentials. It's designed for:

1. **Educational Purposes:** Understanding how the scanner works
2. **Testing Setup:** Validating that all components are working
3. **Development:** Testing changes without API costs
4. **Presentations:** Demonstrating capabilities to stakeholders

**Key Features:**
- Uses the new facade pattern with hybrid classification
- Analyzes sample DDL file with realistic healthcare/business data
- Generates comprehensive reports with detailed findings
- Shows the complete analysis workflow from start to finish

**How It Works:**
1. Loads schema from the sample DDL file using the facade
2. Uses the hybrid classification system for PII/PHI detection
3. Generates risk assessments and compliance mappings
4. Produces comprehensive reports in the new format

**Demo Mode:**
The demo uses a sample DDL file and demonstrates the full workflow
without requiring actual API credentials or database connections.

Author: AI Assistant
Version: 2.0 POC (Updated for Facade Pattern)
"""

# Standard library imports
import os                           # Operating system interface
import sys                          # System-specific parameters
import json                         # JSON data handling for reports
from datetime import datetime       # Date/time operations for timestamps
from typing import Dict, List, Tuple, Any  # Type hints for better documentation
from collections import defaultdict        # Efficient dictionary operations

# Add current directory to Python path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import local modules for schema extraction and scanning
from pii_scanner_poc.services.db_fetch import extract_schema_data, load_db_config
from pii_scanner_poc.core.pii_scanner_facade import pii_scanner

def demo_analysis():
    """
    Execute a complete demonstration of the PII/PHI scanner workflow using the new facade.
    
    This function demonstrates the entire analysis process:
    1. Create a sample DDL file for demonstration
    2. Use the facade to analyze the schema file
    3. Display the comprehensive results
    4. Show the new hybrid classification capabilities
    
    The demo provides a realistic preview of how the actual scanner works,
    including the new facade pattern and hybrid classification system.
    
    Features Demonstrated:
    - New facade pattern usage
    - Hybrid classification system
    - Schema file analysis
    - Comprehensive reporting
    - Error handling and validation
    
    Note:
        This demo uses the actual facade but with a sample file,
        demonstrating the real workflow without requiring API credentials.
    """
    print("🔐 PII/PHI Scanner POC - Demo Mode (Facade Pattern)")
    print("=" * 60)
    print("ℹ️  This demo showcases the new facade pattern and hybrid classification")
    print("📋 Demo will analyze for both GDPR and HIPAA regulations")
    
    # Step 1: Create sample DDL file for demonstration
    print("\n📄 Creating sample DDL file for demonstration...")
    sample_ddl_path = create_sample_ddl_file()
    
    try:
        # Step 2: Validate scanner configuration
        print("\n🔧 Validating scanner configuration...")
        validation_result = pii_scanner.validate_configuration()
        
        if not validation_result['valid']:
            print("⚠️  Configuration validation found issues:")
            for error in validation_result['errors']:
                print(f"   ❌ {error}")
            for warning in validation_result['warnings']:
                print(f"   ⚠️  {warning}")
            print("\n💡 Note: Demo will continue with mock analysis")
        else:
            print("✅ Configuration validation passed")
        
        # Step 3: Display system statistics
        print("\n📊 System Statistics:")
        stats = pii_scanner.get_system_statistics()
        if 'error' not in stats:
            print(f"   🔄 Analysis Mode: {stats.get('performance_metrics', {}).get('analysis_mode', 'hybrid')}")
            print(f"   🧠 Hybrid Classification: {'Enabled' if stats.get('system_configuration', {}).get('hybrid_classification_enabled', True) else 'Disabled'}")
        
        # Step 4: Analyze the sample schema file using the facade
        print(f"\n🔍 Analyzing schema file using facade pattern...")
        print(f"   📁 File: {sample_ddl_path}")
        print(f"   📋 Regulations: GDPR, HIPAA")
        print(f"   🔄 Using hybrid classification system")
        
        # Use the facade to analyze the schema file
        analysis_results = pii_scanner.analyze_schema_file(
            schema_file_path=sample_ddl_path,
            regulations=["GDPR", "HIPAA"],
            output_format="json",
            enable_caching=True,
            enable_llm=False  # Disable LLM for demo to avoid API calls
        )
        
        # Step 5: Display analysis results
        print("\n" + "=" * 80)
        print("📋 PII/PHI ANALYSIS RESULTS - FACADE DEMO")
        print("=" * 80)
        
        if analysis_results.get('success', True):
            display_analysis_results(analysis_results)
        else:
            print(f"❌ Analysis failed: {analysis_results.get('error', 'Unknown error')}")
            print("💡 This is expected in demo mode without proper API configuration")
        
        print("\n✅ Demo completed successfully!")
        print("\n💡 Next Steps:")
        print("1. Configure your Azure OpenAI API credentials in .env file")
        print("2. Run the full scanner with: python -m cli.main --file your_schema.ddl")
        print("3. Try the interactive CLI mode for more options")
        print("4. Explore the hybrid classification system capabilities")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("💡 This is expected in demo mode - the demo shows the workflow structure")
        import traceback
        traceback.print_exc()
    
    finally:
        # Step 6: Clean up temporary files
        if os.path.exists(sample_ddl_path):
            os.remove(sample_ddl_path)
            print(f"🧹 Cleaned up sample file: {sample_ddl_path}")

def create_sample_ddl_file() -> str:
    """
    Create a sample DDL file with realistic healthcare/business data for demonstration.
    
    Returns:
        str: Path to the created sample DDL file
    """
    sample_ddl_content = """
-- Sample Healthcare Database Schema for PII/PHI Scanner Demo
-- This file contains realistic table structures commonly found in healthcare systems

-- Patient Information Table
CREATE TABLE patients (
    patient_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    ssn VARCHAR(11) UNIQUE,
    email VARCHAR(100),
    phone_number VARCHAR(15),
    address VARCHAR(200),
    insurance_number VARCHAR(20),
    medical_record_number VARCHAR(15) UNIQUE
);

-- Medical Records Table
CREATE TABLE medical_records (
    record_id INT PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    diagnosis_code VARCHAR(10),
    diagnosis_description TEXT,
    treatment_notes TEXT,
    prescription_details TEXT,
    lab_results TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employee Information Table
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email_address VARCHAR(100) UNIQUE,
    telephone VARCHAR(15),
    salary DECIMAL(10,2),
    bank_account_number VARCHAR(20),
    tax_id VARCHAR(11),
    hire_date DATE,
    department VARCHAR(50)
);

-- System Audit Table
CREATE TABLE audit_logs (
    log_id INT PRIMARY KEY,
    user_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(50),
    action_performed VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial Transactions Table
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY,
    account_number VARCHAR(20),
    credit_card_number VARCHAR(19),
    routing_number VARCHAR(9),
    amount DECIMAL(12,2),
    transaction_date TIMESTAMP,
    description TEXT
);
"""
    
    sample_file_path = "demo_sample_schema.ddl"
    
    with open(sample_file_path, 'w') as f:
        f.write(sample_ddl_content.strip())
    
    print(f"✅ Created sample DDL file: {sample_file_path}")
    print(f"   📊 Contains 5 tables with various PII/PHI data types")
    print(f"   🏥 Healthcare: patients, medical_records")
    print(f"   👥 Employee: employees")
    print(f"   💰 Financial: transactions")
    print(f"   🔍 System: audit_logs")
    
    return sample_file_path

def display_analysis_results(results: Dict[str, Any]):
    """
    Display the analysis results in a formatted, user-friendly way.
    
    Args:
        results: Analysis results dictionary from the facade
    """
    print("📈 Analysis Summary:")
    
    # Display basic metrics if available
    if 'analysis_summary' in results:
        summary = results['analysis_summary']
        print(f"   📋 Total Tables: {summary.get('total_tables', 'N/A')}")
        print(f"   📊 Total Columns: {summary.get('total_columns', 'N/A')}")
        print(f"   🚨 Sensitive Columns: {summary.get('sensitive_columns', 'N/A')}")
        print(f"   ⚠️  High Risk Tables: {summary.get('high_risk_tables', 'N/A')}")
    
    # Display hybrid classification metrics if available
    if 'hybrid_classification_metrics' in results:
        metrics = results['hybrid_classification_metrics']
        print(f"\n🧠 Hybrid Classification Performance:")
        print(f"   🎯 Local Detection Rate: {metrics.get('local_detection_rate', 0):.1%}")
        print(f"   🤖 LLM Usage Rate: {metrics.get('llm_usage_rate', 0):.1%}")
        print(f"   💾 Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1%}")
        print(f"   ✅ High Confidence Results: {metrics.get('high_confidence_results', 0)}")
        print(f"   ⚠️  Low Confidence Results: {metrics.get('low_confidence_results', 0)}")
    
    # Display table-level results if available
    if 'table_results' in results:
        print(f"\n📋 Table Analysis Results:")
        for table_result in results['table_results']:
            table_name = table_result.get('table_name', 'Unknown')
            risk_level = table_result.get('risk_level', 'Unknown')
            sensitive_cols = table_result.get('sensitive_columns', 0)
            total_cols = table_result.get('total_columns', 0)
            
            risk_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢", "None": "⚪"}.get(risk_level, "❓")
            
            print(f"   {risk_emoji} {table_name}: {risk_level} risk ({sensitive_cols}/{total_cols} sensitive)")
            
            # Show applicable regulations
            if 'applicable_regulations' in table_result:
                regs = table_result['applicable_regulations']
                if regs:
                    print(f"      📜 Regulations: {', '.join(regs)}")
    
    # Display processing recommendations if available
    if 'processing_recommendations' in results:
        recommendations = results['processing_recommendations']
        if recommendations:
            print(f"\n💡 Processing Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
    
    # Display report file path if available
    if 'report_file_path' in results:
        print(f"\n📄 Detailed report saved to: {results['report_file_path']}")
    
    # Display session information
    if 'session_id' in results:
        print(f"\n🔍 Session ID: {results['session_id']}")
    
    if 'processing_time' in results:
        print(f"⏱️  Processing Time: {results['processing_time']:.2f} seconds")


def main():
    """Main entry point for demo scanner"""
    try:
        demo_analysis()
        return 0
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())