-- Comprehensive Test DDL for Inconsistency Fixes Verification
-- Contains specific fields mentioned in the review request

-- Healthcare table (should be classified as HIPAA)
CREATE TABLE patient_records (
    patient_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    middle_initial VARCHAR(1),
    date_of_birth DATE,
    medical_record_number VARCHAR(20),
    diagnosis_code VARCHAR(10),
    cancelled_date DATE
);

-- Medical reference table (medication_name should be NON_SENSITIVE)
CREATE TABLE medication_catalog (
    medication_id VARCHAR(50) PRIMARY KEY,
    medication_name VARCHAR(200),
    dosage_form VARCHAR(50),
    strength VARCHAR(50),
    manufacturer VARCHAR(100)
);

-- Financial table (should be classified as GDPR)
CREATE TABLE customer_accounts (
    account_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100),
    email_address VARCHAR(255),
    credit_card_number VARCHAR(20),
    account_balance DECIMAL(15,2),
    created_date TIMESTAMP
);

-- General business table (should be classified as GDPR)
CREATE TABLE employee_directory (
    employee_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(100),
    department VARCHAR(50),
    phone_number VARCHAR(20),
    hire_date DATE,
    salary DECIMAL(10,2)
);