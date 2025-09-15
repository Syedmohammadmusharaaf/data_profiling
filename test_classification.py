#!/usr/bin/env python3

from pii_scanner_poc.core.inhouse_classification_engine import InHouseClassificationEngine
from pii_scanner_poc.models.data_models import Regulation

# Test the classification engine with backward compatibility
engine = InHouseClassificationEngine()

# Test high confidence sensitive fields (should return tuple with 90-98% confidence)
print('Testing sensitive fields:')
test_fields = ['customer_name', 'email_address', 'phone_number', 'home_address', 'ssn']
for field in test_fields:
    result = engine.classify_field(field, regulation=Regulation.GDPR, table_context='customers')
    if result:
        pattern, confidence = result
        print(f'{field}: confidence={confidence:.2f}, pii_type={pattern.pii_type}, risk={pattern.risk_level}')
    else:
        print(f'{field}: Not classified as sensitive')

print('\nTesting non-sensitive fields:')
tech_fields = ['id', 'created_at', 'updated_at', 'status', 'version']
for field in tech_fields:
    result = engine.classify_field(field, regulation=Regulation.GDPR, table_context='customers')
    if result:
        pattern, confidence = result
        print(f'{field}: confidence={confidence:.2f}, pii_type={pattern.pii_type}, risk={pattern.risk_level}')
    else:
        print(f'{field}: Not classified as sensitive (low confidence)')
