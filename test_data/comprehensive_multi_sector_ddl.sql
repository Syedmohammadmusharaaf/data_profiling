-- =================================================================
-- COMPREHENSIVE MULTI-SECTOR DDL FOR HIPAA vs PII CLASSIFICATION TESTING
-- This DDL contains multiple sectors to test accurate regulatory classification
-- Expected: ~79 HIPAA/PHI fields, rest should be PII under other regulations
-- =================================================================

-- =================================================================
-- HEALTHCARE SECTOR - SHOULD BE CLASSIFIED AS HIPAA/PHI
-- =================================================================

CREATE TABLE patient_demographics_detailed (
    patient_id VARCHAR(20) PRIMARY KEY,
    medical_record_no VARCHAR(20) NOT NULL,
    mrn VARCHAR(20) UNIQUE,
    patient_name VARCHAR(100),
    patient_first_name VARCHAR(50),
    patient_last_name VARCHAR(50),
    patient_middle_name VARCHAR(50),
    patient_ssn VARCHAR(11),
    patient_date_of_birth DATE,
    patient_phone VARCHAR(15),
    patient_email VARCHAR(100),
    patient_address VARCHAR(200),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    insurance_id VARCHAR(30),
    medicare_number VARCHAR(15),
    medicaid_id VARCHAR(15),
    diagnosis VARCHAR(500),
    primary_diagnosis VARCHAR(200),
    secondary_diagnosis VARCHAR(200),
    medical_conditions TEXT,
    allergies TEXT,
    current_medications TEXT,
    treatment_plan TEXT,
    physician_notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medical_patient_records (
    record_id VARCHAR(20) PRIMARY KEY,
    patient_mrn VARCHAR(20),
    visit_date DATE,
    chief_complaint VARCHAR(500),
    diagnosis_code VARCHAR(10),
    diagnosis_description VARCHAR(500),
    prescription VARCHAR(1000),
    medication_name VARCHAR(100),
    dosage VARCHAR(50),
    treatment_notes TEXT,
    lab_results TEXT,
    vital_signs VARCHAR(200),
    blood_pressure VARCHAR(20),
    heart_rate INT,
    temperature DECIMAL(4,2),
    physician_id VARCHAR(20),
    nurse_id VARCHAR(20),
    department VARCHAR(50),
    room_number VARCHAR(10),
    discharge_summary TEXT,
    follow_up_instructions TEXT
);

CREATE TABLE clinical_trial_participants (
    participant_id VARCHAR(20) PRIMARY KEY,
    trial_id VARCHAR(20),
    patient_mrn VARCHAR(20),
    consent_date DATE,
    enrollment_date DATE,
    randomization_code VARCHAR(10),
    treatment_arm VARCHAR(50),
    baseline_measurements TEXT,
    adverse_events TEXT,
    concomitant_medications TEXT,
    protocol_deviations TEXT,
    withdrawal_reason VARCHAR(200),
    completion_status VARCHAR(20),
    efficacy_outcomes TEXT,
    safety_outcomes TEXT
);

CREATE TABLE behavioral_health_sessions (
    session_id VARCHAR(20) PRIMARY KEY,
    patient_mrn VARCHAR(20),
    therapist_id VARCHAR(20),
    session_date DATE,
    session_type VARCHAR(50),
    mental_health_diagnosis VARCHAR(200),
    treatment_goals TEXT,
    session_notes TEXT,
    progress_assessment TEXT,
    medication_management TEXT,
    risk_assessment VARCHAR(100),
    suicide_risk_level VARCHAR(20),
    next_appointment DATE,
    treatment_modality VARCHAR(100)
);

-- =================================================================
-- FINANCIAL SECTOR - SHOULD BE CLASSIFIED AS PII UNDER GDPR (NOT HIPAA)
-- =================================================================

CREATE TABLE financial_accounts_advanced (
    account_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20),
    account_number VARCHAR(20),
    routing_number VARCHAR(9),
    account_type VARCHAR(20),
    customer_ssn VARCHAR(11),
    customer_first_name VARCHAR(50),
    customer_last_name VARCHAR(50),
    customer_email VARCHAR(100),
    customer_phone VARCHAR(15),
    customer_address VARCHAR(200),
    date_of_birth DATE,
    credit_score INT,
    annual_income DECIMAL(12,2),
    employment_status VARCHAR(50),
    employer_name VARCHAR(100),
    account_balance DECIMAL(12,2),
    credit_limit DECIMAL(12,2),
    interest_rate DECIMAL(5,4),
    account_status VARCHAR(20),
    opened_date DATE,
    last_activity_date DATE
);

CREATE TABLE bank_customer_profiles (
    profile_id VARCHAR(20) PRIMARY KEY,
    customer_ssn VARCHAR(11) UNIQUE,
    tax_id VARCHAR(20),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    middle_initial VARCHAR(1),
    email_address VARCHAR(100),
    phone_number VARCHAR(15),
    mobile_phone VARCHAR(15),
    home_address VARCHAR(200),
    mailing_address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    country VARCHAR(50),
    nationality VARCHAR(50),
    occupation VARCHAR(100),
    employer VARCHAR(100),
    work_phone VARCHAR(15),
    salary DECIMAL(12,2),
    net_worth DECIMAL(15,2),
    risk_profile VARCHAR(20),
    kyc_status VARCHAR(20),
    aml_status VARCHAR(20)
);

CREATE TABLE cc_transaction_history (
    transaction_id VARCHAR(20) PRIMARY KEY,
    credit_card_number VARCHAR(19),
    cardholder_name VARCHAR(100),
    cardholder_ssn VARCHAR(11),
    transaction_date TIMESTAMP,
    merchant_name VARCHAR(100),
    merchant_category VARCHAR(50),
    transaction_amount DECIMAL(10,2),
    currency_code VARCHAR(3),
    authorization_code VARCHAR(10),
    cvv_code VARCHAR(4),
    expiration_date VARCHAR(7),
    billing_address VARCHAR(200),
    billing_zip VARCHAR(10),
    cardholder_phone VARCHAR(15),
    cardholder_email VARCHAR(100),
    fraud_score DECIMAL(3,2),
    transaction_status VARCHAR(20),
    processor_response VARCHAR(50)
);

-- =================================================================
-- EDUCATION SECTOR - SHOULD BE CLASSIFIED AS PII UNDER GDPR (NOT HIPAA)
-- =================================================================

CREATE TABLE academic_records_detailed (
    record_id VARCHAR(20) PRIMARY KEY,
    student_id VARCHAR(20),
    student_ssn VARCHAR(11),
    student_first_name VARCHAR(50),
    student_last_name VARCHAR(50),
    student_middle_name VARCHAR(50),
    student_email VARCHAR(100),
    student_phone VARCHAR(15),
    student_address VARCHAR(200),
    parent_guardian_name VARCHAR(100),
    parent_phone VARCHAR(15),
    parent_email VARCHAR(100),
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(15),
    date_of_birth DATE,
    grade_level VARCHAR(10),
    gpa DECIMAL(3,2),
    class_rank INT,
    graduation_date DATE,
    transcript TEXT,
    standardized_test_scores VARCHAR(200),
    disciplinary_records TEXT,
    attendance_record TEXT,
    special_needs VARCHAR(200),
    iep_status VARCHAR(20)
);

CREATE TABLE student_enrollment_records (
    enrollment_id VARCHAR(20) PRIMARY KEY,
    student_ssn VARCHAR(11),
    student_number VARCHAR(20),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    preferred_name VARCHAR(50),
    email_address VARCHAR(100),
    phone_number VARCHAR(15),
    home_address VARCHAR(200),
    permanent_address VARCHAR(200),
    parent_first_name VARCHAR(50),
    parent_last_name VARCHAR(50),
    parent_phone VARCHAR(15),
    parent_email VARCHAR(100),
    guardian_name VARCHAR(100),
    guardian_phone VARCHAR(15),
    birth_date DATE,
    citizenship VARCHAR(50),
    visa_status VARCHAR(50),
    financial_aid_status VARCHAR(20),
    tuition_balance DECIMAL(10,2),
    scholarship_amount DECIMAL(10,2),
    major VARCHAR(100),
    minor VARCHAR(100),
    advisor_name VARCHAR(100),
    enrollment_status VARCHAR(20)
);

-- =================================================================
-- GENERAL BUSINESS SECTOR - SHOULD BE CLASSIFIED AS PII UNDER GDPR (NOT HIPAA)
-- =================================================================

CREATE TABLE employee_records_comprehensive (
    employee_id VARCHAR(20) PRIMARY KEY,
    employee_ssn VARCHAR(11) UNIQUE,
    tax_id VARCHAR(20),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    middle_name VARCHAR(50),
    preferred_name VARCHAR(50),
    email_address VARCHAR(100),
    work_email VARCHAR(100),
    phone_number VARCHAR(15),
    mobile_phone VARCHAR(15),
    home_address VARCHAR(200),
    mailing_address VARCHAR(200),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    date_of_birth DATE,
    hire_date DATE,
    termination_date DATE,
    job_title VARCHAR(100),
    department VARCHAR(50),
    manager_id VARCHAR(20),
    salary DECIMAL(12,2),
    hourly_rate DECIMAL(8,2),
    bonus_amount DECIMAL(10,2),
    commission_rate DECIMAL(5,4),
    benefits_enrollment TEXT,
    performance_reviews TEXT,
    disciplinary_actions TEXT,
    training_records TEXT,
    security_clearance VARCHAR(20),
    background_check_date DATE
);

CREATE TABLE legal_entities_complex (
    entity_id VARCHAR(20) PRIMARY KEY,
    entity_name VARCHAR(200),
    legal_name VARCHAR(200),
    tax_identification VARCHAR(20),
    ein VARCHAR(10),
    registration_number VARCHAR(50),
    incorporation_date DATE,
    business_type VARCHAR(50),
    industry_code VARCHAR(10),
    primary_contact_name VARCHAR(100),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(15),
    registered_address VARCHAR(200),
    business_address VARCHAR(200),
    mailing_address VARCHAR(200),
    authorized_signatory VARCHAR(100),
    signatory_ssn VARCHAR(11),
    signatory_title VARCHAR(100),
    board_members TEXT,
    shareholders TEXT,
    annual_revenue DECIMAL(15,2),
    employee_count INT,
    credit_rating VARCHAR(10),
    risk_assessment VARCHAR(100),
    compliance_status VARCHAR(50),
    audit_date DATE,
    regulatory_filings TEXT
);

-- =================================================================
-- MIXED CONTEXT TABLES - TESTING EDGE CASES
-- =================================================================

CREATE TABLE insurance_claims_processing (
    claim_id VARCHAR(20) PRIMARY KEY,
    policy_number VARCHAR(20),
    policyholder_ssn VARCHAR(11),
    policyholder_name VARCHAR(100),
    claim_type VARCHAR(50), -- Could be health, auto, property, etc.
    claim_amount DECIMAL(12,2),
    incident_date DATE,
    claim_description TEXT,
    adjuster_name VARCHAR(100),
    medical_provider VARCHAR(100), -- Only relevant for health claims
    diagnosis_code VARCHAR(10), -- Only for health claims
    treatment_code VARCHAR(10), -- Only for health claims
    vehicle_vin VARCHAR(17), -- Only for auto claims
    property_address VARCHAR(200), -- Only for property claims
    claim_status VARCHAR(20),
    settlement_amount DECIMAL(12,2),
    settlement_date DATE
);

CREATE TABLE customer_service_interactions (
    interaction_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20),
    customer_ssn VARCHAR(11),
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    customer_phone VARCHAR(15),
    interaction_type VARCHAR(50),
    interaction_channel VARCHAR(20),
    interaction_date TIMESTAMP,
    agent_id VARCHAR(20),
    case_category VARCHAR(50),
    case_description TEXT,
    resolution_notes TEXT,
    satisfaction_score INT,
    follow_up_required BOOLEAN,
    escalation_level VARCHAR(20),
    resolution_date TIMESTAMP,
    case_status VARCHAR(20)
);

-- =================================================================
-- TECHNICAL/SYSTEM TABLES - SHOULD BE NON-PII
-- =================================================================

CREATE TABLE system_audit_logs (
    log_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20), -- System user, not customer
    session_id VARCHAR(50),
    action_type VARCHAR(50),
    resource_accessed VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP,
    success_flag BOOLEAN,
    error_message TEXT,
    request_payload TEXT,
    response_code INT,
    processing_time_ms INT
);

CREATE TABLE application_configuration (
    config_id VARCHAR(20) PRIMARY KEY,
    config_category VARCHAR(50),
    config_key VARCHAR(100),
    config_value TEXT,
    config_description TEXT,
    environment VARCHAR(20),
    created_date TIMESTAMP,
    modified_date TIMESTAMP,
    created_by VARCHAR(50),
    modified_by VARCHAR(50),
    is_active BOOLEAN,
    version_number INT
);

-- =================================================================
-- SUMMARY STATISTICS FOR TESTING
-- =================================================================
-- Expected Classification Results:
-- 
-- HIPAA/PHI Fields (~79 fields):
-- - All fields in patient_demographics_detailed (26 fields)
-- - All fields in medical_patient_records (21 fields) 
-- - All fields in clinical_trial_participants (15 fields)
-- - All fields in behavioral_health_sessions (14 fields)
-- - Medical-related fields in insurance_claims_processing (3 fields: medical_provider, diagnosis_code, treatment_code)
-- 
-- PII under GDPR/Other Regulations (~200+ fields):
-- - All fields in financial_accounts_advanced (22 fields)
-- - All fields in bank_customer_profiles (25 fields)
-- - All fields in cc_transaction_history (19 fields)
-- - All fields in academic_records_detailed (25 fields)
-- - All fields in student_enrollment_records (26 fields)
-- - All fields in employee_records_comprehensive (30 fields)
-- - All fields in legal_entities_complex (27 fields)
-- - Non-medical fields in insurance_claims_processing (15 fields)
-- - All fields in customer_service_interactions (18 fields)
-- 
-- Non-PII Fields (~30 fields):
-- - Most fields in system_audit_logs (13 fields, except potentially user_id)
-- - All fields in application_configuration (12 fields)
-- =================================================================