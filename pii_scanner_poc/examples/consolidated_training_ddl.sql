-- Consolidated Training DDL for PII/PHI Scanner POC
-- Comprehensive database schema covering all common PII/PHI scenarios
-- Purpose: Training and testing the hybrid classification engine
-- Version: 2.0 - Enhanced Coverage

-- =============================================================================
-- FINANCIAL SERVICES SECTOR - HIGH COMPLEXITY
-- =============================================================================

-- Primary Customer Database
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    account_number VARCHAR(16) UNIQUE NOT NULL,
    ssn VARCHAR(11), -- XXX-XX-XXXX format
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_initial CHAR(1),
    date_of_birth DATE,
    mothers_maiden_name VARCHAR(50),
    drivers_license VARCHAR(20),
    passport_number VARCHAR(15),
    email_address VARCHAR(100),
    phone_primary VARCHAR(15),
    phone_secondary VARCHAR(15),
    residential_address TEXT,
    mailing_address TEXT,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    annual_income DECIMAL(12,2),
    credit_score INTEGER,
    account_opening_date DATE,
    last_login_timestamp TIMESTAMP,
    ip_address_last_login VARCHAR(45),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit Card Information
CREATE TABLE credit_cards (
    card_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    card_number VARCHAR(19), -- Full PAN (Primary Account Number)
    card_number_masked VARCHAR(19), -- XXXX-XXXX-XXXX-1234
    expiration_date VARCHAR(7), -- MM/YYYY
    cvv VARCHAR(4),
    card_type VARCHAR(20), -- Visa, MasterCard, AMEX
    cardholder_name VARCHAR(100),
    billing_address TEXT,
    credit_limit DECIMAL(10,2),
    current_balance DECIMAL(10,2),
    last_transaction_date DATE,
    pin_hash VARCHAR(255),
    security_questions TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Banking Transactions
CREATE TABLE transactions (
    transaction_id VARCHAR(25) PRIMARY KEY,
    account_number VARCHAR(16),
    routing_number VARCHAR(9),
    transaction_type VARCHAR(20),
    amount DECIMAL(12,2),
    transaction_date TIMESTAMP,
    merchant_name VARCHAR(100),
    merchant_category VARCHAR(50),
    transaction_location VARCHAR(200),
    transaction_coordinates VARCHAR(50), -- GPS coordinates
    cardholder_verification_method VARCHAR(20),
    authorization_code VARCHAR(10),
    transaction_reference VARCHAR(50),
    currency_code CHAR(3),
    exchange_rate DECIMAL(10,6),
    fee_amount DECIMAL(8,2),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Investment Portfolio
CREATE TABLE investment_accounts (
    portfolio_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    account_type VARCHAR(30), -- 401k, IRA, Roth IRA, Brokerage
    account_value DECIMAL(15,2),
    risk_tolerance VARCHAR(20),
    investment_advisor_id VARCHAR(20),
    beneficiary_name VARCHAR(100),
    beneficiary_ssn VARCHAR(11),
    beneficiary_relationship VARCHAR(30),
    tax_id_number VARCHAR(15), -- EIN or SSN
    account_manager VARCHAR(100),
    last_review_date DATE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- HEALTHCARE SECTOR - HIPAA COMPLIANCE
-- =============================================================================

-- Patient Master Index
CREATE TABLE patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    medical_record_number VARCHAR(15) UNIQUE,
    ssn VARCHAR(11),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    date_of_birth DATE,
    gender CHAR(1),
    race VARCHAR(50),
    ethnicity VARCHAR(50),
    marital_status VARCHAR(20),
    religion VARCHAR(50),
    primary_language VARCHAR(30),
    email_address VARCHAR(100),
    home_phone VARCHAR(15),
    work_phone VARCHAR(15),
    mobile_phone VARCHAR(15),
    emergency_contact_name VARCHAR(100),
    emergency_contact_relationship VARCHAR(30),
    emergency_contact_phone VARCHAR(15),
    home_address TEXT,
    employer_name VARCHAR(100),
    employer_address TEXT,
    insurance_primary VARCHAR(100),
    insurance_member_id VARCHAR(50),
    insurance_group_number VARCHAR(50),
    insurance_secondary VARCHAR(100),
    pharmacy_name VARCHAR(100),
    pharmacy_phone VARCHAR(15),
    primary_care_physician VARCHAR(100),
    allergies TEXT,
    current_medications TEXT,
    medical_history TEXT,
    family_history TEXT,
    blood_type VARCHAR(5),
    organ_donor_status BOOLEAN,
    advance_directives TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clinical Encounters
CREATE TABLE medical_encounters (
    encounter_id VARCHAR(20) PRIMARY KEY,
    patient_id VARCHAR(20) REFERENCES patients(patient_id),
    visit_date DATE,
    visit_time TIME,
    encounter_type VARCHAR(30),
    department VARCHAR(50),
    attending_physician VARCHAR(100),
    physician_npi VARCHAR(10), -- National Provider Identifier
    chief_complaint TEXT,
    present_illness TEXT,
    vital_signs TEXT,
    physical_examination TEXT,
    assessment_and_plan TEXT,
    diagnosis_codes TEXT, -- ICD-10 codes
    procedure_codes TEXT, -- CPT codes
    prescription_details TEXT,
    follow_up_instructions TEXT,
    discharge_summary TEXT,
    billing_amount DECIMAL(10,2),
    insurance_claim_number VARCHAR(50),
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Laboratory Results
CREATE TABLE lab_results (
    result_id VARCHAR(20) PRIMARY KEY,
    patient_id VARCHAR(20) REFERENCES patients(patient_id),
    encounter_id VARCHAR(20) REFERENCES medical_encounters(encounter_id),
    test_name VARCHAR(100),
    test_code VARCHAR(20),
    specimen_type VARCHAR(50),
    collection_date DATE,
    collection_time TIME,
    result_value VARCHAR(100),
    reference_range VARCHAR(100),
    abnormal_flag VARCHAR(10),
    units VARCHAR(20),
    performing_lab VARCHAR(100),
    lab_technician VARCHAR(100),
    pathologist VARCHAR(100),
    clinical_notes TEXT,
    critical_value_notification BOOLEAN,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prescription Management
CREATE TABLE prescriptions (
    prescription_id VARCHAR(20) PRIMARY KEY,
    patient_id VARCHAR(20) REFERENCES patients(patient_id),
    prescribing_physician VARCHAR(100),
    physician_dea_number VARCHAR(15),
    medication_name VARCHAR(100),
    medication_strength VARCHAR(50),
    dosage_form VARCHAR(30),
    quantity INTEGER,
    days_supply INTEGER,
    refills_remaining INTEGER,
    prescription_date DATE,
    fill_date DATE,
    pharmacy_name VARCHAR(100),
    pharmacy_npi VARCHAR(10),
    pharmacist_name VARCHAR(100),
    drug_interactions TEXT,
    contraindications TEXT,
    patient_counseling TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- GOVERNMENT & PUBLIC SECTOR
-- =============================================================================

-- Citizen Records
CREATE TABLE citizen_records (
    citizen_id VARCHAR(20) PRIMARY KEY,
    ssn VARCHAR(11) UNIQUE,
    passport_number VARCHAR(15),
    drivers_license_number VARCHAR(20),
    drivers_license_state CHAR(2),
    state_id_number VARCHAR(20),
    voter_registration_id VARCHAR(20),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    suffix VARCHAR(10),
    date_of_birth DATE,
    place_of_birth VARCHAR(100),
    citizenship_status VARCHAR(30),
    immigration_status VARCHAR(50),
    visa_number VARCHAR(20),
    alien_registration_number VARCHAR(15),
    gender CHAR(1),
    race VARCHAR(50),
    ethnicity VARCHAR(50),
    height VARCHAR(10),
    weight VARCHAR(10),
    eye_color VARCHAR(20),
    hair_color VARCHAR(20),
    distinguishing_marks TEXT,
    current_address TEXT,
    previous_addresses TEXT,
    phone_number VARCHAR(15),
    email_address VARCHAR(100),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(15),
    employer_name VARCHAR(100),
    occupation VARCHAR(100),
    annual_income DECIMAL(12,2),
    tax_filing_status VARCHAR(20),
    dependents INTEGER,
    military_service_history TEXT,
    security_clearance_level VARCHAR(30),
    background_check_date DATE,
    fingerprint_on_file BOOLEAN,
    photo_id_path VARCHAR(255),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Law Enforcement Records
CREATE TABLE criminal_records (
    record_id VARCHAR(20) PRIMARY KEY,
    citizen_id VARCHAR(20) REFERENCES citizen_records(citizen_id),
    arrest_number VARCHAR(20),
    booking_number VARCHAR(20),
    case_number VARCHAR(20),
    arrest_date DATE,
    arrest_time TIME,
    arresting_officer VARCHAR(100),
    arresting_agency VARCHAR(100),
    charges TEXT,
    charge_codes TEXT,
    disposition VARCHAR(100),
    court_case_number VARCHAR(30),
    court_date DATE,
    judge_name VARCHAR(100),
    attorney_name VARCHAR(100),
    sentence_details TEXT,
    probation_officer VARCHAR(100),
    parole_officer VARCHAR(100),
    incarceration_facility VARCHAR(100),
    release_date DATE,
    victim_information TEXT,
    witness_information TEXT,
    evidence_description TEXT,
    mugshot_path VARCHAR(255),
    fingerprints_path VARCHAR(255),
    dna_profile_id VARCHAR(50),
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Social Services
CREATE TABLE social_services (
    case_id VARCHAR(20) PRIMARY KEY,
    citizen_id VARCHAR(20) REFERENCES citizen_records(citizen_id),
    case_type VARCHAR(50),
    case_status VARCHAR(30),
    case_worker VARCHAR(100),
    opening_date DATE,
    closing_date DATE,
    benefit_type VARCHAR(50),
    benefit_amount DECIMAL(10,2),
    eligibility_criteria TEXT,
    household_size INTEGER,
    household_income DECIMAL(12,2),
    housing_status VARCHAR(30),
    employment_status VARCHAR(30),
    disability_status VARCHAR(100),
    medical_conditions TEXT,
    children_in_household INTEGER,
    child_custody_details TEXT,
    child_support_obligations DECIMAL(10,2),
    asset_information TEXT,
    fraud_indicators TEXT,
    investigation_notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- EDUCATION SECTOR
-- =============================================================================

-- Student Information System
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    student_number VARCHAR(15) UNIQUE,
    ssn VARCHAR(11),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    preferred_name VARCHAR(50),
    date_of_birth DATE,
    gender CHAR(1),
    race VARCHAR(50),
    ethnicity VARCHAR(50),
    citizenship_status VARCHAR(30),
    primary_language VARCHAR(30),
    home_address TEXT,
    mailing_address TEXT,
    phone_number VARCHAR(15),
    email_address VARCHAR(100),
    emergency_contact_name VARCHAR(100),
    emergency_contact_relationship VARCHAR(30),
    emergency_contact_phone VARCHAR(15),
    emergency_contact_address TEXT,
    parent_guardian_name VARCHAR(100),
    parent_guardian_phone VARCHAR(15),
    parent_guardian_email VARCHAR(100),
    parent_guardian_employer VARCHAR(100),
    family_income_range VARCHAR(30),
    free_lunch_eligible BOOLEAN,
    special_education_services BOOLEAN,
    iep_status BOOLEAN, -- Individualized Education Program
    section_504_plan BOOLEAN,
    english_learner_status BOOLEAN,
    transportation_needs VARCHAR(100),
    medical_conditions TEXT,
    medications TEXT,
    allergies TEXT,
    immunization_records TEXT,
    previous_schools TEXT,
    enrollment_date DATE,
    graduation_date DATE,
    gpa DECIMAL(3,2),
    class_rank INTEGER,
    standardized_test_scores TEXT,
    disciplinary_actions TEXT,
    extracurricular_activities TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Academic Records
CREATE TABLE academic_records (
    record_id VARCHAR(20) PRIMARY KEY,
    student_id VARCHAR(20) REFERENCES students(student_id),
    school_year VARCHAR(9),
    semester VARCHAR(20),
    course_code VARCHAR(15),
    course_name VARCHAR(100),
    instructor_name VARCHAR(100),
    credit_hours DECIMAL(3,1),
    grade VARCHAR(5),
    grade_points DECIMAL(3,2),
    attendance_percentage DECIMAL(5,2),
    behavior_notes TEXT,
    parent_conference_notes TEXT,
    accommodation_notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- EMPLOYMENT & HR SECTOR
-- =============================================================================

-- Employee Master Data
CREATE TABLE employees (
    employee_id VARCHAR(20) PRIMARY KEY,
    employee_number VARCHAR(15) UNIQUE,
    ssn VARCHAR(11) UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    preferred_name VARCHAR(50),
    date_of_birth DATE,
    gender CHAR(1),
    race VARCHAR(50),
    ethnicity VARCHAR(50),
    marital_status VARCHAR(20),
    citizenship_status VARCHAR(30),
    work_authorization VARCHAR(50),
    visa_status VARCHAR(50),
    home_address TEXT,
    mailing_address TEXT,
    personal_phone VARCHAR(15),
    work_phone VARCHAR(15),
    personal_email VARCHAR(100),
    work_email VARCHAR(100),
    emergency_contact_name VARCHAR(100),
    emergency_contact_relationship VARCHAR(30),
    emergency_contact_phone VARCHAR(15),
    job_title VARCHAR(100),
    department VARCHAR(100),
    manager_name VARCHAR(100),
    manager_employee_id VARCHAR(20),
    hire_date DATE,
    termination_date DATE,
    employment_status VARCHAR(30),
    employment_type VARCHAR(30),
    work_location VARCHAR(100),
    salary_amount DECIMAL(12,2),
    hourly_rate DECIMAL(8,2),
    pay_frequency VARCHAR(20),
    tax_withholding_info TEXT,
    direct_deposit_info TEXT,
    bank_account_number VARCHAR(20),
    bank_routing_number VARCHAR(9),
    benefits_elections TEXT,
    health_insurance_plan VARCHAR(100),
    retirement_plan_contribution DECIMAL(5,2),
    stock_options INTEGER,
    performance_rating VARCHAR(20),
    background_check_date DATE,
    drug_test_date DATE,
    security_clearance VARCHAR(30),
    training_records TEXT,
    disciplinary_actions TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payroll Information
CREATE TABLE payroll (
    payroll_id VARCHAR(20) PRIMARY KEY,
    employee_id VARCHAR(20) REFERENCES employees(employee_id),
    pay_period_start DATE,
    pay_period_end DATE,
    pay_date DATE,
    gross_pay DECIMAL(10,2),
    federal_tax_withheld DECIMAL(8,2),
    state_tax_withheld DECIMAL(8,2),
    social_security_tax DECIMAL(8,2),
    medicare_tax DECIMAL(8,2),
    unemployment_tax DECIMAL(8,2),
    health_insurance_deduction DECIMAL(8,2),
    retirement_contribution DECIMAL(8,2),
    other_deductions DECIMAL(8,2),
    net_pay DECIMAL(10,2),
    hours_worked DECIMAL(6,2),
    overtime_hours DECIMAL(6,2),
    vacation_hours_used DECIMAL(6,2),
    sick_hours_used DECIMAL(6,2),
    vacation_balance DECIMAL(6,2),
    sick_balance DECIMAL(6,2),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TECHNOLOGY & SECURITY SECTOR
-- =============================================================================

-- User Authentication & Access
CREATE TABLE user_accounts (
    user_id VARCHAR(20) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email_address VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    password_salt VARCHAR(100),
    two_factor_secret VARCHAR(100),
    security_questions TEXT,
    last_login_timestamp TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked BOOLEAN DEFAULT FALSE,
    account_expires DATE,
    password_expires DATE,
    user_agent TEXT,
    ip_address_history TEXT,
    session_tokens TEXT,
    api_keys TEXT,
    oauth_tokens TEXT,
    role_assignments TEXT,
    permission_levels TEXT,
    access_control_list TEXT,
    data_classification_level VARCHAR(30),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit & Security Logs
CREATE TABLE security_logs (
    log_id VARCHAR(25) PRIMARY KEY,
    user_id VARCHAR(20) REFERENCES user_accounts(user_id),
    event_type VARCHAR(50),
    event_description TEXT,
    timestamp TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(100),
    resource_accessed VARCHAR(255),
    action_performed VARCHAR(100),
    success_flag BOOLEAN,
    error_message TEXT,
    risk_score INTEGER,
    geolocation VARCHAR(100),
    device_fingerprint TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- LEGAL & COMPLIANCE SECTOR
-- =============================================================================

-- Legal Case Management
CREATE TABLE legal_cases (
    case_id VARCHAR(20) PRIMARY KEY,
    case_number VARCHAR(30) UNIQUE,
    case_type VARCHAR(50),
    case_status VARCHAR(30),
    court_jurisdiction VARCHAR(100),
    judge_assigned VARCHAR(100),
    case_filing_date DATE,
    trial_date DATE,
    client_name VARCHAR(100),
    client_ssn VARCHAR(11),
    client_contact_info TEXT,
    opposing_party VARCHAR(100),
    opposing_counsel VARCHAR(100),
    lead_attorney VARCHAR(100),
    attorney_bar_number VARCHAR(20),
    case_description TEXT,
    legal_issues TEXT,
    evidence_inventory TEXT,
    witness_list TEXT,
    expert_witnesses TEXT,
    settlement_amount DECIMAL(15,2),
    judgment_amount DECIMAL(15,2),
    attorney_fees DECIMAL(12,2),
    court_costs DECIMAL(10,2),
    case_outcome VARCHAR(100),
    appeal_status VARCHAR(50),
    confidentiality_level VARCHAR(30),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TELECOMMUNICATIONS SECTOR
-- =============================================================================

-- Customer Service Records
CREATE TABLE telecom_customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    account_number VARCHAR(16) UNIQUE,
    ssn VARCHAR(11),
    drivers_license VARCHAR(20),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE,
    service_address TEXT,
    billing_address TEXT,
    phone_numbers TEXT, -- Multiple phone lines
    email_address VARCHAR(100),
    account_pin VARCHAR(10),
    security_questions TEXT,
    credit_check_score INTEGER,
    deposit_amount DECIMAL(8,2),
    service_plan VARCHAR(100),
    monthly_charges DECIMAL(8,2),
    usage_data TEXT,
    call_detail_records TEXT,
    data_usage_logs TEXT,
    roaming_charges DECIMAL(8,2),
    international_usage TEXT,
    device_information TEXT,
    imei_numbers TEXT,
    sim_card_numbers TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INSURANCE SECTOR
-- =============================================================================

-- Insurance Policy Holders
CREATE TABLE insurance_policies (
    policy_id VARCHAR(20) PRIMARY KEY,
    policy_number VARCHAR(20) UNIQUE,
    policyholder_ssn VARCHAR(11),
    policyholder_name VARCHAR(100),
    policyholder_dob DATE,
    policyholder_address TEXT,
    policyholder_phone VARCHAR(15),
    policyholder_email VARCHAR(100),
    policy_type VARCHAR(50),
    coverage_amount DECIMAL(15,2),
    premium_amount DECIMAL(10,2),
    deductible_amount DECIMAL(8,2),
    policy_start_date DATE,
    policy_end_date DATE,
    beneficiaries TEXT,
    medical_information TEXT,
    driving_record TEXT,
    claims_history TEXT,
    risk_assessment TEXT,
    underwriting_notes TEXT,
    agent_name VARCHAR(100),
    agent_license_number VARCHAR(20),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- BIOMETRIC DATA TABLES
-- =============================================================================

-- Biometric Identifiers
CREATE TABLE biometric_data (
    biometric_id VARCHAR(20) PRIMARY KEY,
    person_id VARCHAR(20),
    biometric_type VARCHAR(30), -- fingerprint, facial, iris, voice, DNA
    template_data BLOB,
    template_hash VARCHAR(255),
    quality_score INTEGER,
    enrollment_date DATE,
    last_verification_date DATE,
    verification_count INTEGER,
    device_serial_number VARCHAR(50),
    capture_location VARCHAR(100),
    operator_id VARCHAR(20),
    retention_period INTEGER, -- days
    deletion_date DATE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Customer Indexes
CREATE INDEX idx_customers_ssn ON customers(ssn);
CREATE INDEX idx_customers_email ON customers(email_address);
CREATE INDEX idx_customers_phone ON customers(phone_primary);

-- Patient Indexes
CREATE INDEX idx_patients_ssn ON patients(ssn);
CREATE INDEX idx_patients_mrn ON patients(medical_record_number);
CREATE INDEX idx_patients_dob ON patients(date_of_birth);

-- Employee Indexes
CREATE INDEX idx_employees_ssn ON employees(ssn);
CREATE INDEX idx_employees_email_work ON employees(work_email);
CREATE INDEX idx_employees_employee_number ON employees(employee_number);

-- Citizen Indexes
CREATE INDEX idx_citizens_ssn ON citizen_records(ssn);
CREATE INDEX idx_citizens_passport ON citizen_records(passport_number);
CREATE INDEX idx_citizens_drivers_license ON citizen_records(drivers_license_number);

-- Student Indexes
CREATE INDEX idx_students_ssn ON students(ssn);
CREATE INDEX idx_students_number ON students(student_number);
CREATE INDEX idx_students_email ON students(email_address);

-- Security Indexes
CREATE INDEX idx_user_accounts_username ON user_accounts(username);
CREATE INDEX idx_user_accounts_email ON user_accounts(email_address);
CREATE INDEX idx_security_logs_timestamp ON security_logs(timestamp);
CREATE INDEX idx_security_logs_user_id ON security_logs(user_id);

-- Biometric Indexes
CREATE INDEX idx_biometric_person_id ON biometric_data(person_id);
CREATE INDEX idx_biometric_type ON biometric_data(biometric_type);

-- =============================================================================
-- VIEWS FOR COMMON PII/PHI QUERIES
-- =============================================================================

-- Customer PII Summary View
CREATE VIEW customer_pii_summary AS
SELECT 
    customer_id,
    CASE WHEN ssn IS NOT NULL THEN 'SSN_PRESENT' ELSE 'SSN_MISSING' END as ssn_status,
    CASE WHEN email_address IS NOT NULL THEN 'EMAIL_PRESENT' ELSE 'EMAIL_MISSING' END as email_status,
    CASE WHEN phone_primary IS NOT NULL THEN 'PHONE_PRESENT' ELSE 'PHONE_MISSING' END as phone_status,
    CASE WHEN drivers_license IS NOT NULL THEN 'DL_PRESENT' ELSE 'DL_MISSING' END as dl_status
FROM customers;

-- Patient PHI Summary View
CREATE VIEW patient_phi_summary AS
SELECT 
    patient_id,
    medical_record_number,
    CASE WHEN ssn IS NOT NULL THEN 'SSN_PRESENT' ELSE 'SSN_MISSING' END as ssn_status,
    CASE WHEN insurance_member_id IS NOT NULL THEN 'INSURANCE_PRESENT' ELSE 'INSURANCE_MISSING' END as insurance_status,
    CASE WHEN allergies IS NOT NULL THEN 'ALLERGIES_DOCUMENTED' ELSE 'ALLERGIES_NOT_DOCUMENTED' END as allergy_status
FROM patients;

-- =============================================================================
-- STORED PROCEDURES FOR DATA ANONYMIZATION
-- =============================================================================

-- Note: These are template stored procedures - actual implementation may vary by database system

/*
DELIMITER //
CREATE PROCEDURE AnonymizeCustomerData(IN customer_id_param VARCHAR(20))
BEGIN
    UPDATE customers 
    SET 
        ssn = CONCAT('XXX-XX-', RIGHT(ssn, 4)),
        email_address = CONCAT('user', customer_id_param, '@example.com'),
        phone_primary = CONCAT('XXX-XXX-', RIGHT(phone_primary, 4))
    WHERE customer_id = customer_id_param;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE AnonymizePatientData(IN patient_id_param VARCHAR(20))
BEGIN
    UPDATE patients 
    SET 
        ssn = CONCAT('XXX-XX-', RIGHT(ssn, 4)),
        email_address = CONCAT('patient', patient_id_param, '@healthcare.com'),
        home_phone = CONCAT('XXX-XXX-', RIGHT(home_phone, 4))
    WHERE patient_id = patient_id_param;
END //
DELIMITER ;
*/

-- =============================================================================
-- COMMENT DOCUMENTATION
-- =============================================================================

-- Table Comments
COMMENT ON TABLE customers IS 'Financial services customer data with comprehensive PII fields';
COMMENT ON TABLE credit_cards IS 'Credit card information including PAN and security data';
COMMENT ON TABLE patients IS 'Healthcare patient master index with HIPAA-protected PHI';
COMMENT ON TABLE medical_encounters IS 'Clinical encounter records with diagnostic information';
COMMENT ON TABLE citizen_records IS 'Government citizen records with extensive identifying information';
COMMENT ON TABLE employees IS 'Employee master data with payroll and benefits information';
COMMENT ON TABLE biometric_data IS 'Biometric identifiers and templates for authentication';

-- Column Comments for Key PII/PHI Fields
COMMENT ON COLUMN customers.ssn IS 'Social Security Number - PII, GDPR Personal Data, CCPA Personal Information';
COMMENT ON COLUMN customers.email_address IS 'Email Address - PII, GDPR Personal Data, CCPA Personal Information';
COMMENT ON COLUMN customers.drivers_license IS 'Drivers License Number - PII, Government ID';
COMMENT ON COLUMN patients.medical_record_number IS 'Medical Record Number - PHI, HIPAA Protected';
COMMENT ON COLUMN patients.insurance_member_id IS 'Insurance Member ID - PHI, HIPAA Protected';
COMMENT ON COLUMN credit_cards.card_number IS 'Primary Account Number (PAN) - PCI DSS Protected, Financial Data';
COMMENT ON COLUMN biometric_data.template_data IS 'Biometric Template - GDPR Special Category, Sensitive Personal Data';
