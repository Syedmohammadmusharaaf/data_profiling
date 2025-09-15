#!/usr/bin/env python3
"""
Comprehensive classification test to validate 95%+ auto-classification rate.
This test simulates real-world database schemas to ensure high coverage.
"""

from pii_scanner_poc.core.inhouse_classification_engine import InHouseClassificationEngine
from pii_scanner_poc.models.data_models import Regulation

def test_comprehensive_field_classification():
    """Test a comprehensive set of database fields to achieve 95%+ auto-classification"""
    
    engine = InHouseClassificationEngine()
    
    # Comprehensive test dataset covering typical database schemas
    test_cases = {
        # High confidence PII fields (90-98% confidence)
        'high_confidence_pii': [
            'customer_name', 'first_name', 'last_name', 'full_name', 'display_name',
            'email_address', 'email', 'user_email', 'contact_email',
            'phone_number', 'phone', 'mobile_number', 'cell_phone', 'home_phone',
            'address', 'street_address', 'home_address', 'billing_address',
            'address_line_1', 'address_line_2', 'street', 'city', 'postal_code', 'zip_code',
            'ssn', 'social_security_number', 'tax_id', 'national_id',
            'credit_card_number', 'card_number', 'account_number', 'bank_account',
            'password_hash', 'password', 'password_salt', 'auth_token',
            'birth_date', 'date_of_birth', 'dob', 'birthdate',
            'username', 'login', 'user_id', 'customer_id', 'person_id',
            'ip_address', 'mac_address', 'device_id', 'session_id'
        ],
        
        # Medium confidence business fields (60-75% confidence)  
        'medium_confidence_business': [
            'company_name', 'organization', 'business_name', 'department',
            'employee_id', 'staff_id', 'badge_number', 'employee_number',
            'salary', 'wage', 'compensation', 'bonus', 'commission',
            'hire_date', 'start_date', 'employment_date', 'join_date',
            'manager_id', 'supervisor_id', 'reports_to', 'team_lead',
            'job_title', 'position', 'role', 'designation',
            'project_name', 'task_name', 'activity', 'assignment',
            'client_name', 'customer_company', 'vendor_name', 'supplier',
            'contract_number', 'agreement_id', 'deal_id', 'opportunity_id',
            'invoice_number', 'bill_number', 'receipt_id', 'transaction_id'
        ],
        
        # Low confidence technical fields (5-15% confidence)
        'low_confidence_technical': [
            'id', 'primary_key', 'foreign_key', 'key_id', 'reference_id',
            'created_at', 'created_date', 'created_on', 'date_created',
            'updated_at', 'updated_date', 'modified_date', 'last_modified',
            'deleted_at', 'deleted_date', 'is_deleted', 'is_active',
            'status', 'state', 'flag', 'is_enabled', 'is_visible',
            'version', 'revision', 'sequence_number', 'order_index',
            'count', 'quantity', 'amount', 'total', 'sum', 'average',
            'type', 'category', 'classification', 'group', 'kind',
            'description', 'notes', 'comments', 'remarks', 'details',
            'metadata', 'properties', 'attributes', 'settings', 'config',
            'hash', 'checksum', 'signature', 'token', 'key',
            'url', 'uri', 'path', 'filename', 'extension'
        ],
        
        # Ambiguous fields that could be personal (40-60% confidence)
        'ambiguous_fields': [
            'name', 'title', 'label', 'code', 'number', 'value',
            'data', 'content', 'text', 'message', 'subject',
            'location', 'place', 'region', 'area', 'zone'
        ]
    }
    
    total_fields = 0
    auto_classified_fields = 0  # Fields with confidence >= 50%
    results_by_category = {}
    
    print("=== COMPREHENSIVE FIELD CLASSIFICATION TEST ===\n")
    
    for category, fields in test_cases.items():
        print(f"Testing {category.replace('_', ' ').title()} ({len(fields)} fields):")
        print("-" * 60)
        
        category_results = {
            'total': len(fields),
            'auto_classified': 0,
            'high_confidence': 0,
            'medium_confidence': 0, 
            'low_confidence': 0,
            'failed': 0
        }
        
        for field in fields:
            total_fields += 1
            try:
                result = engine.classify_field(field, regulation=Regulation.GDPR, table_context='test_table')
                
                if result:
                    pattern, confidence = result
                    
                    if confidence >= 0.50:  # Auto-classification threshold
                        auto_classified_fields += 1
                        category_results['auto_classified'] += 1
                        
                        if confidence >= 0.80:
                            category_results['high_confidence'] += 1
                            confidence_label = "HIGH"
                        elif confidence >= 0.50:
                            category_results['medium_confidence'] += 1  
                            confidence_label = "MEDIUM"
                        else:
                            category_results['low_confidence'] += 1
                            confidence_label = "LOW"
                    else:
                        category_results['low_confidence'] += 1
                        confidence_label = "LOW"
                    
                    print(f"  {field:<25} -> {confidence:.0%} ({confidence_label}) - {pattern.pii_type.name}")
                else:
                    category_results['failed'] += 1
                    print(f"  {field:<25} -> FAILED (No classification result)")
                    
            except Exception as e:
                category_results['failed'] += 1
                print(f"  {field:<25} -> ERROR: {str(e)}")
        
        results_by_category[category] = category_results
        
        auto_rate = (category_results['auto_classified'] / category_results['total']) * 100
        print(f"\nCategory Auto-Classification Rate: {auto_rate:.1f}%")
        print(f"High Confidence: {category_results['high_confidence']}, Medium: {category_results['medium_confidence']}, Low: {category_results['low_confidence']}, Failed: {category_results['failed']}\n")
    
    # Overall results
    overall_auto_rate = (auto_classified_fields / total_fields) * 100
    print("=" * 80)
    print(f"OVERALL RESULTS:")
    print(f"Total Fields Tested: {total_fields}")
    print(f"Auto-Classified (≥50% confidence): {auto_classified_fields}")
    print(f"Overall Auto-Classification Rate: {overall_auto_rate:.1f}%")
    print(f"Target: 95% | Status: {'✅ PASSED' if overall_auto_rate >= 95.0 else '❌ NEEDS IMPROVEMENT'}")
    print("=" * 80)
    
    # Detailed breakdown
    print(f"\nDETAILED BREAKDOWN:")
    for category, results in results_by_category.items():
        rate = (results['auto_classified'] / results['total']) * 100
        print(f"{category.replace('_', ' ').title():<30}: {rate:5.1f}% ({results['auto_classified']}/{results['total']})")
    
    return overall_auto_rate

def test_real_world_database_schema():
    """Test with real-world database schema field names"""
    
    engine = InHouseClassificationEngine()
    
    print(f"\n{'='*80}")
    print("REAL-WORLD DATABASE SCHEMA TEST")
    print(f"{'='*80}")
    
    # Simulate AdventureWorks-style database schema
    real_world_fields = [
        # Person/Customer table
        'BusinessEntityID', 'PersonID', 'FirstName', 'MiddleName', 'LastName', 
        'EmailAddress', 'PhoneNumber', 'AddressLine1', 'AddressLine2', 'City', 
        'StateProvinceID', 'PostalCode', 'CountryRegionCode',
        
        # Employee table  
        'EmployeeID', 'LoginID', 'HireDate', 'BirthDate', 'MaritalStatus',
        'Gender', 'SalariedFlag', 'VacationHours', 'SickLeaveHours',
        
        # Product table
        'ProductID', 'ProductName', 'ProductNumber', 'StandardCost', 'ListPrice',
        'Color', 'Size', 'Weight', 'ProductCategoryID', 'ProductSubcategoryID',
        
        # Sales table
        'SalesOrderID', 'OrderDate', 'DueDate', 'ShipDate', 'CustomerID',
        'SalesPersonID', 'TerritoryID', 'SubTotal', 'TaxAmt', 'Freight', 'TotalDue',
        
        # Technical/System fields
        'CreatedDate', 'ModifiedDate', 'rowguid', 'IsActive', 'StatusID',
        'VersionStamp', 'ConcurrencyToken', 'LastUpdateDate', 'SortOrder'
    ]
    
    auto_classified = 0
    total = len(real_world_fields)
    
    print(f"Testing {total} real-world database fields:\n")
    
    for field in real_world_fields:
        try:
            result = engine.classify_field(field, regulation=Regulation.GDPR, table_context='business_table')
            
            if result:
                pattern, confidence = result
                if confidence >= 0.50:
                    auto_classified += 1
                    status = "AUTO" 
                else:
                    status = "REVIEW"
                    
                print(f"  {field:<25} -> {confidence:.0%} ({status}) - {pattern.pii_type.name}")
            else:
                print(f"  {field:<25} -> No Result")
                
        except Exception as e:
            print(f"  {field:<25} -> ERROR: {str(e)}")
    
    real_world_rate = (auto_classified / total) * 100
    print(f"\nReal-World Auto-Classification Rate: {real_world_rate:.1f}%")
    print(f"Auto-Classified: {auto_classified}/{total}")
    print(f"Target: 95% | Status: {'✅ PASSED' if real_world_rate >= 95.0 else '❌ NEEDS IMPROVEMENT'}")
    
    return real_world_rate

if __name__ == "__main__":
    try:
        # Run comprehensive test
        overall_rate = test_comprehensive_field_classification()
        
        # Run real-world test  
        real_world_rate = test_real_world_database_schema()
        
        # Final assessment
        print(f"\n{'='*80}")
        print("FINAL ASSESSMENT")
        print(f"{'='*80}")
        print(f"Comprehensive Test Rate: {overall_rate:.1f}%")
        print(f"Real-World Schema Rate: {real_world_rate:.1f}%") 
        
        average_rate = (overall_rate + real_world_rate) / 2
        print(f"Average Auto-Classification Rate: {average_rate:.1f}%")
        
        if average_rate >= 95.0:
            print("🎉 SUCCESS: System achieves 95%+ auto-classification rate!")
        else:
            print("⚠️  NEEDS IMPROVEMENT: System below 95% auto-classification target")
            print("   - Consider enhancing medium-confidence patterns")
            print("   - Add more business domain patterns")
            print("   - Improve fuzzy matching capabilities")
            
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
