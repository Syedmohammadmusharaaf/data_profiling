-- Advanced Training DDL - Edge Cases and Complex Patterns
-- Designed to test scanner accuracy with challenging scenarios

-- =================================================================
-- COMPLEX NAMING PATTERNS & EDGE CASES
-- =================================================================

CREATE TABLE user_profiles_complex (
    -- Mixed case and underscore variations
    UserId VARCHAR(20) PRIMARY KEY,
    USER_SSN VARCHAR(11) NOT NULL,
    Social_Security_Num VARCHAR(11),
    social_sec_no VARCHAR(11),
    SocialSecurityNumber VARCHAR(11),
    -- Name variations with prefixes/suffixes
    cust_first_name VARCHAR(50),
    customer_fname VARCHAR(50),
    usr_given_name VARCHAR(50),
    client_firstname VARCHAR(50),
    member_first_nm VARCHAR(50),
    -- Complex email patterns
    primary_email_addr VARCHAR(100),
    secondary_email_address VARCHAR(100),
    work_email_id VARCHAR(100),
    personal_email_contact VARCHAR(100),
    backup_email_info VARCHAR(100),
    -- Phone number variations
    primary_phone_no VARCHAR(15),
    home_telephone_number VARCHAR(15),
    mobile_phone_contact VARCHAR(15),
    cell_phone_info VARCHAR(15),
    emergency_phone_contact VARCHAR(15),
    -- Address complexity
    residential_street_address VARCHAR(200),
    home_mailing_address VARCHAR(200),
    current_living_address VARCHAR(200),
    permanent_home_address VARCHAR(200),
    billing_street_addr VARCHAR(200),
    -- Date variations
    birth_dt DATE,
    date_birth DATE,
    birth_date_info DATE,
    customer_birth_date DATE,
    user_date_of_birth DATE,
    -- Financial info
    bank_acct_num VARCHAR(20),
    checking_account_number VARCHAR(20),
    savings_acct_no VARCHAR(20),
    credit_card_num VARCHAR(19),
    debit_card_number VARCHAR(19)
);

-- =================================================================
-- INTERNATIONAL & MULTILINGUAL PATTERNS
-- =================================================================

CREATE TABLE international_customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    -- International ID variations
    national_id VARCHAR(20),
    passport_no VARCHAR(15),
    visa_number VARCHAR(20),
    sin_number VARCHAR(11), -- Canadian SIN
    nino VARCHAR(13), -- UK National Insurance Number
    bsn VARCHAR(9), -- Dutch BSN
    fiscal_code VARCHAR(16), -- Italian Codice Fiscale
    cpf VARCHAR(14), -- Brazilian CPF
    -- Name variations
    given_names VARCHAR(100),
    family_names VARCHAR(100),
    surname_family VARCHAR(100),
    apellidos VARCHAR(100), -- Spanish surnames
    nom_famille VARCHAR(100), -- French family name
    cognome VARCHAR(100), -- Italian surname
    -- International address
    street_number VARCHAR(10),
    street_name VARCHAR(100),
    apartment_flat VARCHAR(20),
    suburb_district VARCHAR(50),
    postcode VARCHAR(20),
    postal_area VARCHAR(50),
    region_province VARCHAR(50),
    country_code VARCHAR(3),
    -- International phone
    country_code_phone VARCHAR(5),
    area_code VARCHAR(5),
    local_number VARCHAR(15),
    international_phone VARCHAR(20),
    mobile_intl VARCHAR(20)
);

-- =================================================================
-- HEALTHCARE SPECIALIZED PATTERNS
-- =================================================================

CREATE TABLE patient_demographics_detailed (
    patient_identifier VARCHAR(20) PRIMARY KEY,
    -- Medical IDs
    hospital_id VARCHAR(20),
    clinic_number VARCHAR(20),
    patient_chart_id VARCHAR(20),
    medical_record_id VARCHAR(20),
    health_card_number VARCHAR(20),
    medicare_beneficiary_id VARCHAR(15),
    medicaid_member_id VARCHAR(15),
    -- Insurance variations
    primary_insurance_id VARCHAR(30),
    secondary_insurance_number VARCHAR(30),
    group_policy_id VARCHAR(20),
    subscriber_member_id VARCHAR(30),
    -- Contact variations
    patient_home_phone VARCHAR(15),
    patient_work_telephone VARCHAR(15),
    patient_mobile_contact VARCHAR(15),
    emergency_contact_person VARCHAR(100),
    emergency_contact_telephone VARCHAR(15),
    next_of_kin_name VARCHAR(100),
    next_of_kin_phone VARCHAR(15),
    -- Address healthcare specific
    patient_home_address VARCHAR(200),
    patient_mailing_addr VARCHAR(200),
    emergency_contact_address VARCHAR(200),
    pharmacy_address VARCHAR(200),
    -- Sensitive health data
    diagnosis_primary VARCHAR(100),
    diagnosis_secondary VARCHAR(100),
    allergies_medications TEXT,
    medical_conditions TEXT,
    treatment_history TEXT,
    prescription_medications TEXT
);

-- =================================================================
-- FINANCIAL ADVANCED PATTERNS
-- =================================================================

CREATE TABLE financial_accounts_advanced (
    account_identifier VARCHAR(20) PRIMARY KEY,
    -- Account variations
    primary_account_num VARCHAR(20),
    secondary_account_number VARCHAR(20),
    joint_account_id VARCHAR(20),
    business_account_number VARCHAR(20),
    trust_account_id VARCHAR(20),
    -- Routing variations
    bank_routing_num VARCHAR(9),
    aba_routing_number VARCHAR(9),
    wire_routing_code VARCHAR(9),
    fed_routing_number VARCHAR(9),
    -- Card variations
    primary_card_num VARCHAR(19),
    secondary_card_number VARCHAR(19),
    business_card_id VARCHAR(19),
    corporate_card_number VARCHAR(19),
    -- Security codes
    card_security_code VARCHAR(4),
    cvv_code VARCHAR(4),
    cvc_number VARCHAR(4),
    card_verification_value VARCHAR(4),
    -- Investment accounts
    brokerage_account_num VARCHAR(20),
    investment_account_id VARCHAR(20),
    retirement_account_number VARCHAR(20),
    ira_account_id VARCHAR(20),
    pension_fund_number VARCHAR(20),
    -- International banking
    iban_number VARCHAR(34),
    swift_code VARCHAR(11),
    sort_code VARCHAR(6), -- UK
    bic_code VARCHAR(11)
);

-- =================================================================
-- EDUCATION ADVANCED PATTERNS
-- =================================================================

CREATE TABLE academic_records_detailed (
    record_identifier VARCHAR(20) PRIMARY KEY,
    -- Student ID variations
    student_identification VARCHAR(20),
    enrollment_number VARCHAR(20),
    matriculation_id VARCHAR(20),
    registration_number VARCHAR(20),
    academic_id VARCHAR(20),
    -- Parent/Guardian info
    parent_guardian_name VARCHAR(100),
    mother_full_name VARCHAR(100),
    father_full_name VARCHAR(100),
    legal_guardian_name VARCHAR(100),
    emergency_contact_parent VARCHAR(100),
    -- Contact variations
    student_personal_phone VARCHAR(15),
    parent_home_phone VARCHAR(15),
    parent_work_telephone VARCHAR(15),
    parent_mobile_contact VARCHAR(15),
    guardian_contact_number VARCHAR(15),
    -- Academic emails
    student_institutional_email VARCHAR(100),
    student_personal_email VARCHAR(100),
    parent_contact_email VARCHAR(100),
    guardian_email_address VARCHAR(100),
    -- Financial aid
    financial_aid_id VARCHAR(20),
    scholarship_id VARCHAR(20),
    grant_number VARCHAR(20),
    loan_reference_number VARCHAR(20),
    work_study_id VARCHAR(20),
    -- Academic performance
    cumulative_gpa DECIMAL(3,2),
    semester_gpa DECIMAL(3,2),
    class_ranking INTEGER,
    academic_standing VARCHAR(20),
    disciplinary_records TEXT
);

-- =================================================================
-- EMPLOYMENT ADVANCED PATTERNS
-- =================================================================

CREATE TABLE employee_records_comprehensive (
    employee_identifier VARCHAR(20) PRIMARY KEY,
    -- Employee ID variations
    personnel_number VARCHAR(20),
    badge_number VARCHAR(20),
    payroll_id VARCHAR(20),
    worker_identification VARCHAR(20),
    staff_member_id VARCHAR(20),
    -- Tax and legal IDs
    federal_tax_id VARCHAR(11),
    state_tax_number VARCHAR(15),
    workers_comp_id VARCHAR(20),
    unemployment_id VARCHAR(20),
    -- Emergency contacts
    emergency_contact_primary VARCHAR(100),
    emergency_contact_secondary VARCHAR(100),
    emergency_phone_primary VARCHAR(15),
    emergency_phone_secondary VARCHAR(15),
    emergency_relationship_primary VARCHAR(50),
    emergency_relationship_secondary VARCHAR(50),
    -- Compensation details
    base_annual_salary DECIMAL(12,2),
    hourly_wage_rate DECIMAL(8,2),
    overtime_rate DECIMAL(8,2),
    commission_rate DECIMAL(5,4),
    bonus_percentage DECIMAL(5,2),
    -- Banking for payroll
    direct_deposit_account_1 VARCHAR(20),
    direct_deposit_routing_1 VARCHAR(9),
    direct_deposit_account_2 VARCHAR(20),
    direct_deposit_routing_2 VARCHAR(9),
    -- Benefits enrollment
    health_plan_member_id VARCHAR(30),
    dental_plan_number VARCHAR(30),
    vision_plan_id VARCHAR(30),
    life_insurance_policy_num VARCHAR(30),
    disability_policy_number VARCHAR(30),
    retirement_plan_id VARCHAR(30),
    -- Performance and HR
    performance_review_id VARCHAR(20),
    disciplinary_record_id VARCHAR(20),
    training_record_id VARCHAR(20),
    background_check_id VARCHAR(20)
);

-- =================================================================
-- LEGAL & COMPLIANCE PATTERNS
-- =================================================================

CREATE TABLE legal_entities_complex (
    entity_identifier VARCHAR(20) PRIMARY KEY,
    -- Legal IDs
    federal_ein VARCHAR(9),
    state_registration_id VARCHAR(20),
    dba_registration VARCHAR(20),
    corporate_id VARCHAR(20),
    llc_number VARCHAR(20),
    -- Regulatory IDs
    sec_filing_number VARCHAR(20),
    finra_id VARCHAR(20),
    fdic_cert_number VARCHAR(10),
    occ_charter_number VARCHAR(10),
    -- Attorney information
    legal_counsel_name VARCHAR(100),
    attorney_bar_number VARCHAR(20),
    law_firm_contact VARCHAR(100),
    legal_counsel_phone VARCHAR(15),
    legal_counsel_email VARCHAR(100),
    -- Compliance officer
    compliance_officer_name VARCHAR(100),
    compliance_officer_phone VARCHAR(15),
    compliance_officer_email VARCHAR(100),
    -- Audit information
    external_auditor_firm VARCHAR(100),
    auditor_contact_person VARCHAR(100),
    auditor_phone VARCHAR(15),
    auditor_email VARCHAR(100),
    -- Sensitive legal data
    litigation_case_numbers TEXT,
    regulatory_actions TEXT,
    compliance_violations TEXT,
    confidential_settlements DECIMAL(15,2)
);

-- =================================================================
-- TECHNOLOGY & SECURITY PATTERNS
-- =================================================================

CREATE TABLE system_access_records (
    access_record_id VARCHAR(20) PRIMARY KEY,
    -- User identification
    system_user_id VARCHAR(50),
    network_username VARCHAR(50),
    domain_account VARCHAR(50),
    active_directory_id VARCHAR(50),
    ldap_distinguished_name VARCHAR(200),
    -- Authentication
    password_hash VARCHAR(255),
    security_token VARCHAR(100),
    biometric_template BLOB,
    security_questions TEXT,
    two_factor_phone VARCHAR(15),
    backup_email VARCHAR(100),
    -- Network information
    ip_address_primary VARCHAR(15),
    mac_address VARCHAR(17),
    device_serial_number VARCHAR(50),
    computer_hostname VARCHAR(50),
    -- Security clearance
    clearance_level VARCHAR(20),
    background_investigation_id VARCHAR(20),
    security_sponsor VARCHAR(100),
    clearance_expiry_date DATE,
    -- Access logs
    last_login_timestamp TIMESTAMP,
    failed_login_attempts INTEGER,
    account_locked_timestamp TIMESTAMP,
    password_last_changed TIMESTAMP
);


-- =================================================================

-- ===== HEALTHCARE & MEDICAL (HIPAA Focus) =====

-- 1. Medical Records with various naming patterns
CREATE TABLE medical_patient_records (
    record_uuid UUID PRIMARY KEY,
    patient_full_name VARCHAR(100),          -- PII
    birth_date DATE,                         -- PHI
    ssn_number CHAR(11),                     -- PHI/PII
    medical_record_no VARCHAR(20),           -- PHI
    home_address TEXT,                       -- PII/PHI
    contact_phone VARCHAR(15),               -- PII/PHI
    emergency_contact_info TEXT,             -- PII
    insurance_member_id VARCHAR(30),         -- PHI
    blood_type VARCHAR(5),                   -- PHI
    genetic_markers TEXT,                    -- Sensitive health data
    mental_health_notes TEXT,                -- Sensitive PHI
    substance_abuse_history TEXT,            -- Sensitive PHI
    created_timestamp TIMESTAMP
);

-- 2. Clinical test results
CREATE TABLE lab_test_results_tbl (
    test_id BIGSERIAL PRIMARY KEY,
    patient_identifier UUID,                 -- PHI
    physician_name VARCHAR(100),             -- PII
    test_type VARCHAR(50),
    result_values TEXT,                      -- PHI
    hiv_status VARCHAR(10),                  -- Sensitive PHI
    hepatitis_markers VARCHAR(100),          -- Sensitive PHI
    drug_screening_results TEXT,             -- Sensitive PHI
    dna_sequence TEXT,                       -- Biometric/Genetic data
    test_date_time TIMESTAMP,                -- PHI
    lab_technician_id VARCHAR(20)
);

-- 3. Prescription database
CREATE TABLE rx_prescriptions (
    prescription_num VARCHAR(25) PRIMARY KEY, -- PHI
    patient_id_ref UUID,                     -- PHI
    prescriber_npi VARCHAR(15),              -- Provider identifier
    medication_name VARCHAR(100),
    controlled_substance_flag BOOLEAN,        -- Sensitive
    psychiatric_med_indicator BOOLEAN,       -- Sensitive
    dosage_instructions TEXT,
    pharmacy_name VARCHAR(100),
    pharmacy_address TEXT,                   -- PII
    dispensed_date DATE,                     -- PHI
    patient_phone_backup VARCHAR(15)         -- PII/PHI
);

-- 4. Mental health sessions
CREATE TABLE behavioral_health_sessions (
    session_guid UUID PRIMARY KEY,
    client_name VARCHAR(100),                -- PII
    therapist_license_no VARCHAR(20),        -- Professional ID
    session_notes TEXT,                      -- Sensitive PHI
    suicide_risk_assessment VARCHAR(20),     -- Sensitive PHI
    substance_use_discussion TEXT,           -- Sensitive PHI
    family_history_mental_illness TEXT,     -- Sensitive PHI
    trauma_history TEXT,                     -- Sensitive PHI
    session_datetime TIMESTAMP,              -- PHI
    emergency_contact_person VARCHAR(100),   -- PII
    insurance_authorization_code VARCHAR(30) -- PHI
);

-- ===== FINANCIAL SERVICES (PCI/PII Focus) =====

-- 5. Customer financial profiles
CREATE TABLE bank_customer_profiles (
    customer_account_id BIGSERIAL PRIMARY KEY,
    full_legal_name VARCHAR(120),            -- PII
    social_security_num CHAR(11),            -- PII
    date_of_birth DATE,                      -- PII
    mothers_maiden_name VARCHAR(50),         -- PII/Security question
    home_address_line1 VARCHAR(100),         -- PII
    home_address_line2 VARCHAR(100),         -- PII
    city_state_zip VARCHAR(100),             -- PII
    primary_phone VARCHAR(15),               -- PII
    email_address VARCHAR(150),              -- PII
    annual_income DECIMAL(12,2),             -- Financial PII
    credit_score INTEGER,                    -- Financial PII
    account_opening_date DATE,
    kyc_document_type VARCHAR(30),           -- Know Your Customer
    drivers_license_number VARCHAR(25),      -- PII
    passport_number VARCHAR(20),             -- PII
    tax_id_number VARCHAR(15)                -- PII
);

-- 6. Credit card transactions
CREATE TABLE cc_transaction_history (
    transaction_ref_id BIGSERIAL PRIMARY KEY,
    cardholder_name VARCHAR(100),            -- PII
    card_number_encrypted VARCHAR(200),      -- PCI data
    card_expiry_month INTEGER,               -- PCI data
    card_expiry_year INTEGER,                -- PCI data
    cvv_code_hash VARCHAR(100),              -- PCI data
    transaction_amount DECIMAL(10,2),
    merchant_category_code VARCHAR(10),
    transaction_timestamp TIMESTAMP,
    billing_address TEXT,                    -- PII
    ip_address_origin VARCHAR(45),           -- PII
    device_fingerprint TEXT,                 -- PII
    geolocation_data VARCHAR(100)            -- Location data
);

-- 7. Loan applications
CREATE TABLE loan_application_data (
    app_reference_number VARCHAR(30) PRIMARY KEY,
    applicant_first_name VARCHAR(50),        -- PII
    applicant_last_name VARCHAR(50),         -- PII
    applicant_ssn CHAR(11),                  -- PII
    co_applicant_name VARCHAR(100),          -- PII
    co_applicant_ssn CHAR(11),               -- PII
    employment_history TEXT,                 -- PII
    salary_information DECIMAL(12,2),        -- Financial PII
    bank_account_numbers TEXT,               -- Financial PII
    asset_information TEXT,                  -- Financial PII
    debt_obligations TEXT,                   -- Financial PII
    reference_contacts TEXT,                 -- PII
    application_date TIMESTAMP
);

-- ===== E-COMMERCE & RETAIL =====

-- 8. Customer shopping profiles
CREATE TABLE ecommerce_user_accounts (
    user_account_uuid UUID PRIMARY KEY,
    username_chosen VARCHAR(50),             -- PII
    email_primary VARCHAR(150),              -- PII
    password_hash_bcrypt VARCHAR(255),       -- Security data
    first_name VARCHAR(50),                  -- PII
    last_name VARCHAR(50),                   -- PII
    phone_mobile VARCHAR(15),                -- PII
    shipping_address_default TEXT,           -- PII
    billing_address_default TEXT,            -- PII
    date_of_birth DATE,                      -- PII
    gender_identity VARCHAR(20),             -- Sensitive PII
    browsing_history_json TEXT,              -- Behavioral data
    purchase_preferences TEXT,               -- Behavioral data
    wishlist_items TEXT,                     -- Behavioral data
    loyalty_program_number VARCHAR(25),      -- PII
    referred_by_friend VARCHAR(100)          -- PII
);

-- 9. Payment methods storage
CREATE TABLE customer_payment_methods (
    payment_method_id BIGSERIAL PRIMARY KEY,
    customer_uuid UUID,
    payment_type VARCHAR(20),
    credit_card_last_four CHAR(4),           -- PCI data
    credit_card_brand VARCHAR(20),
    cardholder_full_name VARCHAR(100),       -- PII
    billing_street_address VARCHAR(200),     -- PII
    billing_city VARCHAR(50),                -- PII
    billing_state_province VARCHAR(50),      -- PII
    billing_postal_code VARCHAR(20),         -- PII
    bank_routing_number VARCHAR(15),         -- Financial PII
    bank_account_number_encrypted VARCHAR(200), -- Financial PII
    paypal_email_address VARCHAR(150),       -- PII
    is_default_payment BOOLEAN,
    added_timestamp TIMESTAMP
);

-- 10. Order tracking with personal data
CREATE TABLE order_fulfillment_tracking (
    order_tracking_id VARCHAR(50) PRIMARY KEY,
    customer_user_id UUID,
    recipient_full_name VARCHAR(100),        -- PII
    shipping_phone_number VARCHAR(15),       -- PII
    delivery_address_complete TEXT,          -- PII
    delivery_instructions TEXT,              -- May contain PII
    package_weight DECIMAL(6,2),
    delivery_signature_image BYTEA,          -- Biometric data
    gps_delivery_coordinates VARCHAR(50),    -- Location data
    delivery_photo BYTEA,                    -- May contain PII
    delivery_timestamp TIMESTAMP,
    delivery_person_name VARCHAR(100),       -- PII
    special_handling_notes TEXT             -- May contain sensitive info
);

-- ===== HUMAN RESOURCES & EMPLOYMENT =====

-- 11. Employee personal information
CREATE TABLE hr_employee_master_data (
    employee_id_number INTEGER PRIMARY KEY,
    social_security_number CHAR(11),         -- PII
    first_name VARCHAR(50),                  -- PII
    middle_initial CHAR(1),                  -- PII
    last_name VARCHAR(50),                   -- PII
    preferred_name VARCHAR(50),              -- PII
    date_of_birth DATE,                      -- PII
    place_of_birth VARCHAR(100),             -- PII
    citizenship_status VARCHAR(50),          -- PII
    visa_status VARCHAR(50),                 -- PII
    home_address_street VARCHAR(200),        -- PII
    home_address_city VARCHAR(50),           -- PII
    home_address_state VARCHAR(50),          -- PII
    home_address_zip VARCHAR(20),            -- PII
    personal_phone_number VARCHAR(15),       -- PII
    personal_email_address VARCHAR(150),     -- PII
    emergency_contact_name VARCHAR(100),     -- PII
    emergency_contact_phone VARCHAR(15),     -- PII
    emergency_contact_relationship VARCHAR(50), -- PII
    marital_status VARCHAR(20),              -- PII
    spouse_name VARCHAR(100),                -- PII
    number_of_dependents INTEGER,            -- PII
    military_service_record TEXT,            -- PII
    background_check_results TEXT,           -- Sensitive PII
    drug_test_results VARCHAR(20),           -- Sensitive PII
    hire_date DATE,
    termination_date DATE,
    termination_reason TEXT                  -- Sensitive PII
);

-- 12. Payroll and compensation
CREATE TABLE payroll_compensation_records (
    payroll_record_id BIGSERIAL PRIMARY KEY,
    employee_reference_id INTEGER,
    salary_annual_amount DECIMAL(12,2),      -- Financial PII
    hourly_wage_rate DECIMAL(8,2),           -- Financial PII
    overtime_hours_worked DECIMAL(6,2),
    commission_earned DECIMAL(10,2),         -- Financial PII
    bonus_amount DECIMAL(10,2),              -- Financial PII
    stock_options_granted INTEGER,           -- Financial PII
    retirement_contribution DECIMAL(10,2),   -- Financial PII
    health_insurance_deduction DECIMAL(8,2), -- Financial PII/PHI
    dental_insurance_deduction DECIMAL(6,2), -- Financial PII/PHI
    vision_insurance_deduction DECIMAL(6,2), -- Financial PII/PHI
    life_insurance_deduction DECIMAL(8,2),   -- Financial PII
    federal_tax_withheld DECIMAL(10,2),      -- Financial PII
    state_tax_withheld DECIMAL(10,2),        -- Financial PII
    social_security_tax DECIMAL(10,2),       -- Financial PII
    medicare_tax DECIMAL(8,2),               -- Financial PII
    bank_routing_number VARCHAR(15),         -- Financial PII
    bank_account_number_encrypted VARCHAR(200), -- Financial PII
    pay_period_start_date DATE,
    pay_period_end_date DATE,
    pay_date DATE
);

-- 13. Performance reviews and disciplinary actions
CREATE TABLE employee_performance_records (
    performance_review_id BIGSERIAL PRIMARY KEY,
    employee_id_ref INTEGER,
    reviewer_manager_name VARCHAR(100),      -- PII
    review_period_year INTEGER,
    performance_rating VARCHAR(20),
    performance_comments TEXT,               -- May contain sensitive info
    salary_increase_percentage DECIMAL(5,2), -- Financial PII
    promotion_eligibility BOOLEAN,
    disciplinary_actions_taken TEXT,         -- Sensitive PII
    improvement_plan_details TEXT,           -- Sensitive PII
    attendance_issues_noted TEXT,            -- Sensitive PII
    behavioral_concerns TEXT,                -- Sensitive PII
    skills_assessment_results TEXT,
    career_development_goals TEXT,
    review_date DATE,
    next_review_scheduled_date DATE
);

-- ===== EDUCATION SECTOR =====

-- 14. Student information system
CREATE TABLE student_enrollment_records (
    student_id_number VARCHAR(20) PRIMARY KEY,
    student_first_name VARCHAR(50),          -- PII
    student_last_name VARCHAR(50),           -- PII
    student_middle_name VARCHAR(50),         -- PII
    date_of_birth DATE,                      -- PII
    social_security_number CHAR(11),         -- PII
    student_home_address TEXT,               -- PII
    parent_guardian_name VARCHAR(100),       -- PII
    parent_guardian_phone VARCHAR(15),       -- PII
    parent_guardian_email VARCHAR(150),      -- PII
    emergency_contact_info TEXT,             -- PII
    medical_conditions TEXT,                 -- PHI
    medications_taken TEXT,                  -- PHI
    learning_disabilities TEXT,              -- Sensitive educational record
    behavioral_issues_history TEXT,          -- Sensitive educational record
    disciplinary_record TEXT,                -- Sensitive educational record
    free_lunch_eligibility BOOLEAN,          -- Socioeconomic PII
    transportation_needs TEXT,               -- PII
    enrollment_date DATE,
    graduation_date DATE,
    transcript_gpa DECIMAL(4,2)
);

-- 15. Academic performance tracking
CREATE TABLE student_academic_performance (
    grade_record_id BIGSERIAL PRIMARY KEY,
    student_identifier VARCHAR(20),
    course_name VARCHAR(100),
    instructor_name VARCHAR(100),            -- PII
    semester_year VARCHAR(20),
    final_grade VARCHAR(5),
    grade_points_earned DECIMAL(6,2),
    attendance_percentage DECIMAL(5,2),
    tardiness_count INTEGER,
    behavioral_notes TEXT,                   -- Sensitive educational record
    parent_conference_notes TEXT,            -- PII/Sensitive
    special_accommodations TEXT,             -- Sensitive educational record
    tutoring_services_used TEXT,
    extracurricular_participation TEXT,
    standardized_test_scores TEXT,           -- Educational record
    college_application_info TEXT,           -- PII/Educational record
    scholarship_applications TEXT,           -- Financial PII
    recommendation_letters TEXT             -- PII
);

-- ===== GOVERNMENT & LEGAL SERVICES =====

-- 16. Citizen services database
CREATE TABLE government_citizen_records (
    citizen_record_id UUID PRIMARY KEY,
    full_legal_name VARCHAR(150),            -- PII
    social_security_number CHAR(11),         -- PII
    date_of_birth DATE,                      -- PII
    place_of_birth VARCHAR(100),             -- PII
    citizenship_status VARCHAR(50),          -- PII
    passport_number VARCHAR(20),             -- PII
    drivers_license_number VARCHAR(25),      -- PII
    voter_registration_id VARCHAR(30),       -- PII
    political_party_affiliation VARCHAR(50), -- Sensitive PII
    residential_address TEXT,                -- PII
    mailing_address TEXT,                    -- PII
    phone_number_primary VARCHAR(15),        -- PII
    email_address_primary VARCHAR(150),      -- PII
    veteran_status VARCHAR(50),              -- PII
    disability_status TEXT,                  -- Sensitive PII
    public_assistance_benefits TEXT,         -- Financial PII
    criminal_background_check TEXT,          -- Sensitive PII
    sex_offender_registry_status BOOLEAN,    -- Sensitive PII
    court_orders_restraining TEXT,           -- Sensitive PII
    tax_lien_information TEXT,               -- Financial PII
    bankruptcy_history TEXT,                 -- Financial PII
    marriage_certificate_info TEXT,          -- PII
    divorce_decree_info TEXT                 -- PII
);

-- 17. Legal case management
CREATE TABLE legal_case_files (
    case_file_number VARCHAR(30) PRIMARY KEY,
    client_full_name VARCHAR(100),           -- PII
    client_ssn CHAR(11),                     -- PII
    client_contact_info TEXT,                -- PII
    opposing_party_name VARCHAR(100),        -- PII
    opposing_party_contact TEXT,             -- PII
    case_type VARCHAR(50),
    case_description TEXT,                   -- May contain sensitive info
    attorney_assigned VARCHAR(100),          -- PII
    paralegal_assigned VARCHAR(100),         -- PII
    court_jurisdiction VARCHAR(100),
    judge_assigned VARCHAR(100),             -- PII
    case_filing_date DATE,
    trial_date DATE,
    settlement_amount DECIMAL(15,2),         -- Financial PII
    case_outcome TEXT,
    confidential_notes TEXT,                 -- Attorney-client privilege
    witness_contact_information TEXT,        -- PII
    expert_witness_info TEXT,                -- PII
    evidence_inventory TEXT,
    discovery_materials TEXT,                -- May contain sensitive info
    client_communications TEXT               -- Attorney-client privilege
);

-- ===== TRAVEL & HOSPITALITY =====

-- 18. Hotel guest information
CREATE TABLE hotel_guest_registrations (
    reservation_confirmation_code VARCHAR(20) PRIMARY KEY,
    guest_first_name VARCHAR(50),            -- PII
    guest_last_name VARCHAR(50),             -- PII
    guest_title VARCHAR(10),                 -- PII
    date_of_birth DATE,                      -- PII
    passport_number VARCHAR(20),             -- PII
    drivers_license_number VARCHAR(25),      -- PII
    nationality VARCHAR(50),                 -- PII
    home_address_complete TEXT,              -- PII
    business_address TEXT,                   -- PII
    phone_number_mobile VARCHAR(15),         -- PII
    phone_number_business VARCHAR(15),       -- PII
    email_address_primary VARCHAR(150),      -- PII
    credit_card_number_encrypted VARCHAR(200), -- PCI data
    credit_card_expiry VARCHAR(10),          -- PCI data
    credit_card_holder_name VARCHAR(100),    -- PII
    loyalty_program_membership VARCHAR(30),  -- PII
    special_requests TEXT,                   -- May contain sensitive info
    dietary_restrictions TEXT,               -- May contain PHI
    accessibility_needs TEXT,                -- May contain PHI
    emergency_contact_person VARCHAR(100),   -- PII
    emergency_contact_phone VARCHAR(15),     -- PII
    check_in_datetime TIMESTAMP,
    check_out_datetime TIMESTAMP,
    room_preferences TEXT,
    guest_photo BYTEA,                       -- Biometric data
    vehicle_license_plate VARCHAR(15),       -- PII
    additional_guest_names TEXT              -- PII
);

-- 19. Airline passenger records
CREATE TABLE airline_passenger_manifest (
    passenger_record_locator VARCHAR(10) PRIMARY KEY,
    passenger_first_name VARCHAR(50),        -- PII
    passenger_last_name VARCHAR(50),         -- PII
    passenger_middle_name VARCHAR(50),       -- PII
    date_of_birth DATE,                      -- PII
    gender VARCHAR(10),                      -- PII
    passport_number VARCHAR(20),             -- PII
    passport_expiry_date DATE,               -- PII
    passport_issuing_country VARCHAR(50),    -- PII
    visa_information TEXT,                   -- PII
    known_traveler_number VARCHAR(20),       -- PII
    redress_number VARCHAR(20),              -- PII
    home_address TEXT,                       -- PII
    contact_phone_number VARCHAR(15),        -- PII
    email_address VARCHAR(150),              -- PII
    emergency_contact_name VARCHAR(100),     -- PII
    emergency_contact_phone VARCHAR(15),     -- PII
    frequent_flyer_number VARCHAR(30),       -- PII
    seat_assignment VARCHAR(10),
    meal_preference VARCHAR(50),             -- May contain dietary/religious info
    special_assistance_required TEXT,        -- May contain PHI
    baggage_information TEXT,
    security_screening_results TEXT,         -- Security sensitive
    flight_number VARCHAR(10),
    departure_datetime TIMESTAMP,
    arrival_datetime TIMESTAMP,
    ticket_purchase_method VARCHAR(50),
    payment_card_last_four CHAR(4),          -- PCI data
    travel_companion_info TEXT               -- PII
);

-- ===== SOCIAL MEDIA & DATING =====

-- 20. Social media user profiles
CREATE TABLE social_media_user_profiles (
    user_profile_id UUID PRIMARY KEY,
    username VARCHAR(50),                    -- PII
    display_name VARCHAR(100),               -- PII
    email_address VARCHAR(150),              -- PII
    phone_number VARCHAR(15),                -- PII
    date_of_birth DATE,                      -- PII
    gender_identity VARCHAR(50),             -- Sensitive PII
    sexual_orientation VARCHAR(50),          -- Sensitive PII
    relationship_status VARCHAR(50),         -- PII
    location_city VARCHAR(50),               -- PII
    location_country VARCHAR(50),            -- PII
    profile_photo BYTEA,                     -- Biometric data
    bio_description TEXT,                    -- May contain PII
    interests_hobbies TEXT,                  -- Behavioral data
    political_views VARCHAR(100),            -- Sensitive PII
    religious_views VARCHAR(100),            -- Sensitive PII
    education_background TEXT,               -- PII
    employment_information TEXT,             -- PII
    family_members_list TEXT,                -- PII
    friend_connections_data TEXT,            -- Social graph data
    private_messages_encrypted TEXT,         -- Private communications
    search_history TEXT,                     -- Behavioral data
    ad_targeting_profile TEXT,               -- Behavioral data
    device_information TEXT,                 -- Technical PII
    ip_address_history TEXT,                 -- PII
    gps_location_history TEXT,               -- Location data
    browsing_behavior TEXT                   -- Behavioral data
);

-- 21. Dating app user data
CREATE TABLE dating_app_user_data (
    dating_profile_id UUID PRIMARY KEY,
    first_name VARCHAR(50),                  -- PII
    age INTEGER,                             -- PII (derived from DOB)
    gender_identity VARCHAR(50),             -- Sensitive PII
    sexual_orientation VARCHAR(50),          -- Sensitive PII
    ethnicity VARCHAR(100),                  -- Sensitive PII
    height_inches INTEGER,                   -- Physical characteristic
    weight_pounds INTEGER,                   -- Physical characteristic
    body_type VARCHAR(50),                   -- Physical characteristic
    eye_color VARCHAR(20),                   -- Physical characteristic
    hair_color VARCHAR(20),                  -- Physical characteristic
    education_level VARCHAR(100),            -- PII
    occupation VARCHAR(100),                 -- PII
    annual_income_range VARCHAR(50),         -- Financial PII
    religion VARCHAR(100),                   -- Sensitive PII
    political_affiliation VARCHAR(100),      -- Sensitive PII
    smoking_habits VARCHAR(50),              -- Health-related PII
    drinking_habits VARCHAR(50),             -- Health-related PII
    drug_use_history VARCHAR(50),            -- Sensitive health PII
    relationship_goals TEXT,                 -- Personal preferences
    dating_preferences TEXT,                 -- Personal preferences
    sexual_preferences TEXT,                 -- Sensitive personal data
    profile_photos BYTEA,                    -- Biometric data
    verification_photos BYTEA,               -- Biometric data
    geolocation_data TEXT,                   -- Location data
    messaging_history TEXT,                  -- Private communications
    match_algorithm_data TEXT,               -- Behavioral profiling
    swipe_history TEXT,                      -- Behavioral data
    premium_subscription_info TEXT,          -- Financial data
    safety_reports_filed TEXT,               -- Safety/security data
    background_check_consent BOOLEAN,        -- Consent data
    std_test_results TEXT                    -- Health data (very sensitive)
);

-- ===== INSURANCE SECTOR =====

-- 22. Insurance policy holders
CREATE TABLE insurance_policy_holders (
    policy_number VARCHAR(30) PRIMARY KEY,
    policyholder_first_name VARCHAR(50),     -- PII
    policyholder_last_name VARCHAR(50),      -- PII
    policyholder_ssn CHAR(11),               -- PII
    date_of_birth DATE,                      -- PII
    gender VARCHAR(10),                      -- PII
    marital_status VARCHAR(20),              -- PII
    occupation VARCHAR(100),                 -- PII
    annual_income DECIMAL(12,2),             -- Financial PII
    home_address TEXT,                       -- PII
    mailing_address TEXT,                    -- PII
    phone_home VARCHAR(15),                  -- PII
    phone_mobile VARCHAR(15),                -- PII
    email_address VARCHAR(150),              -- PII
    drivers_license_number VARCHAR(25),      -- PII
    vehicle_information TEXT,                -- PII
    medical_history TEXT,                    -- PHI
    prescription_medications TEXT,           -- PHI
    smoking_status VARCHAR(20),              -- Health PII
    alcohol_consumption VARCHAR(50),         -- Health PII
    exercise_habits VARCHAR(100),            -- Health PII
    family_medical_history TEXT,             -- PHI
    beneficiary_information TEXT,            -- PII
    banking_information_encrypted TEXT,      -- Financial PII
    claims_history TEXT,                     -- Financial/Health PII
    credit_score INTEGER,                    -- Financial PII
    bankruptcy_history TEXT,                 -- Financial PII
    criminal_background TEXT,                -- Sensitive PII
    policy_effective_date DATE,
    policy_expiry_date DATE,
    premium_amount DECIMAL(10,2)
);

-- 23. Insurance claims processing
CREATE TABLE insurance_claims_data (
    claim_number VARCHAR(25) PRIMARY KEY,
    policy_number_ref VARCHAR(30),
    claimant_name VARCHAR(100),              -- PII
    claimant_ssn CHAR(11),                   -- PII
    incident_date DATE,
    incident_location TEXT,                  -- Location data
    incident_description TEXT,               -- May contain sensitive info
    police_report_number VARCHAR(30),        -- Legal document reference
    medical_provider_name VARCHAR(100),      -- PHI
    medical_diagnosis TEXT,                  -- PHI
    medical_treatment_received TEXT,         -- PHI
    medical_bills_amount DECIMAL(12,2),      -- Financial/Health PII
    lost_wages_claimed DECIMAL(10,2),        -- Financial PII
    property_damage_amount DECIMAL(12,2),    -- Financial PII
    witness_statements TEXT,                 -- May contain PII
    witness_contact_info TEXT,               -- PII
    photos_of_incident BYTEA,                -- May contain PII/biometric
    surveillance_footage BYTEA,              -- May contain biometric data
    expert_opinions TEXT,                    -- Professional assessments
    legal_representation TEXT,               -- PII of attorneys
    settlement_negotiations TEXT,            -- Financial negotiations
    claim_adjuster_name VARCHAR(100),        -- PII
    claim_status VARCHAR(50),
    payout_amount DECIMAL(12,2),             -- Financial PII
    payment_method TEXT,                     -- Financial PII
    fraud_investigation_notes TEXT           -- Sensitive investigation data
);

-- ===== REAL ESTATE =====

-- 24. Property listings and transactions
CREATE TABLE real_estate_transactions (
    transaction_id UUID PRIMARY KEY,
    property_address_full TEXT,              -- PII
    property_parcel_id VARCHAR(30),          -- Public record identifier
    seller_name VARCHAR(100),                -- PII
    seller_ssn CHAR(11),                     -- PII
    seller_contact_phone VARCHAR(15),        -- PII
    seller_email VARCHAR(150),               -- PII
    buyer_name VARCHAR(100),                 -- PII
    buyer_ssn CHAR(11),                      -- PII
    buyer_contact_phone VARCHAR(15),         -- PII
    buyer_email VARCHAR(150),                -- PII
    real_estate_agent_name VARCHAR(100),     -- PII
    agent_license_number VARCHAR(30),        -- Professional license
    agent_commission DECIMAL(10,2),          -- Financial PII
    mortgage_lender_name VARCHAR(100),
    loan_amount DECIMAL(15,2),               -- Financial PII
    down_payment_amount DECIMAL(12,2),       -- Financial PII
    interest_rate DECIMAL(5,4),              -- Financial terms
    buyer_credit_score INTEGER,              -- Financial PII
    buyer_income_verification DECIMAL(12,2), -- Financial PII
    buyer_employment_info TEXT,              -- PII
    property_appraisal_value DECIMAL(12,2),  -- Financial data
    home_inspection_report TEXT,             -- Property condition
    closing_date DATE,
    sale_price DECIMAL(12,2),                -- Financial data
    property_taxes_annual DECIMAL(10,2),     -- Financial data
    homeowners_insurance_info TEXT,          -- Insurance PII
    title_company_info TEXT,                 -- Service provider info
    deed_information TEXT,                   -- Legal document
    escrow_account_details TEXT              -- Financial account info
);

-- 25. Rental applications
CREATE TABLE rental_application_data (
    application_id UUID PRIMARY KEY,
    applicant_first_name VARCHAR(50),        -- PII
    applicant_last_name VARCHAR(50),         -- PII
    applicant_middle_name VARCHAR(50),       -- PII
    applicant_ssn CHAR(11),                  -- PII
    date_of_birth DATE,                      -- PII
    phone_number VARCHAR(15),                -- PII
    email_address VARCHAR(150),              -- PII
    current_address TEXT,                    -- PII
    previous_addresses TEXT,                 -- PII
    employment_status VARCHAR(50),           -- PII
    employer_name VARCHAR(100),              -- PII
    employer_contact_info TEXT,              -- PII
    monthly_income DECIMAL(10,2),            -- Financial PII
    bank_account_info_encrypted TEXT,        -- Financial PII
    credit_score INTEGER,                    -- Financial PII
    bankruptcy_history TEXT,                 -- Financial PII
    eviction_history TEXT,                   -- Legal/Financial PII
    criminal_background_check TEXT,          -- Sensitive PII
    references_personal TEXT,                -- PII of references
    references_professional TEXT,            -- PII of references
    pet_information TEXT,                    -- Pet ownership data
    vehicle_information TEXT,                -- Vehicle PII
    emergency_contact_name VARCHAR(100),     -- PII
    emergency_contact_phone VARCHAR(15),     -- PII
    co_applicant_information TEXT,           -- PII of co-applicant
    rental_history TEXT,                     -- Previous rental PII
    reason_for_moving TEXT,                  -- Personal information
    desired_move_in_date DATE,
    lease_term_requested INTEGER,
    monthly_rent_budget DECIMAL(8,2)         -- Financial preference
);

-- ===== AUTOMOTIVE =====

-- 26. Vehicle registration and ownership
CREATE TABLE vehicle_registration_records (
    registration_id UUID PRIMARY KEY,
    vehicle_identification_number VARCHAR(20), -- VIN (unique identifier)
    license_plate_number VARCHAR(15),         -- PII
    owner_full_name VARCHAR(100),             -- PII
    owner_address TEXT,                       -- PII
    owner_phone VARCHAR(15),                  -- PII
    owner_email VARCHAR(150),                 -- PII
    co_owner_name VARCHAR(100),               -- PII
    vehicle_make VARCHAR(50),
    vehicle_model VARCHAR(50),
    vehicle_year INTEGER,
    vehicle_color VARCHAR(30),
    odometer_reading INTEGER,
    purchase_price DECIMAL(12,2),             -- Financial PII
    purchase_date DATE,
    dealer_information TEXT,                  -- Business info
    financing_company VARCHAR(100),
    loan_amount DECIMAL(12,2),                -- Financial PII
    monthly_payment DECIMAL(8,2),             -- Financial PII
    insurance_company VARCHAR(100),
    insurance_policy_number VARCHAR(30),      -- Insurance PII
    registration_expiry_date DATE,
    emissions_test_results VARCHAR(50),
    safety_inspection_date DATE,
    traffic_violations_history TEXT,          -- Legal record PII
    accident_history TEXT,                    -- Insurance/Legal PII
    maintenance_records TEXT,                 -- Service history
    warranty_information TEXT,
    recall_notices TEXT,
    theft_recovery_flag BOOLEAN,              -- Security flag
    lien_holder_information TEXT              -- Financial/Legal info
);

-- 27. Automotive insurance claims
CREATE TABLE auto_insurance_claims (
    claim_id VARCHAR(30) PRIMARY KEY,
    policy_holder_name VARCHAR(100),          -- PII
    policy_holder_ssn CHAR(11),               -- PII
    drivers_license_number VARCHAR(25),       -- PII
    vehicle_vin VARCHAR(20),                  -- Vehicle identifier
    license_plate VARCHAR(15),                -- PII
    accident_date_time TIMESTAMP,
    accident_location TEXT,                   -- Location data
    police_report_number VARCHAR(30),         -- Legal document
    other_driver_name VARCHAR(100),           -- PII of third party
    other_driver_license VARCHAR(25),         -- PII of third party
    other_driver_insurance TEXT,              -- Third party insurance PII
    witness_information TEXT,                 -- Witness PII
    accident_description TEXT,                -- Incident details
    fault_determination TEXT,                 -- Legal determination
    vehicle_damage_photos BYTEA,              -- Visual evidence
    repair_estimates TEXT,                    -- Financial estimates
    medical_injuries_reported TEXT,           -- PHI
    medical_treatment_received TEXT,          -- PHI
    medical_bills TEXT,                       -- Financial/Health PII
    lost_wages_claimed DECIMAL(10,2),         -- Financial PII
    pain_suffering_claim DECIMAL(10,2),       -- Financial/Health PII
    property_damage_amount DECIMAL(12,2),     -- Financial data
    bodily_injury_amount DECIMAL(12,2),       -- Financial/Health data
    settlement_amount DECIMAL(12,2),          -- Financial settlement
    legal_representation TEXT,                -- Attorney PII
    court_case_number VARCHAR(30),            -- Legal case reference
    claim_adjuster_notes TEXT                 -- Internal assessment
);

-- ===== TELECOMMUNICATIONS =====

-- 28. Telecom customer accounts
CREATE TABLE telecom_customer_accounts (
    account_number VARCHAR(20) PRIMARY KEY,
    customer_first_name VARCHAR(50),          -- PII
    customer_last_name VARCHAR(50),           -- PII
    customer_ssn CHAR(11),                    -- PII
    date_of_birth DATE,                       -- PII
    service_address TEXT,                     -- PII
    billing_address TEXT,                     -- PII
    phone_number_primary VARCHAR(15),         -- PII
    phone_number_secondary VARCHAR(15),       -- PII
    email_address VARCHAR(150),               -- PII
    emergency_contact_info TEXT,              -- PII
    credit_check_score INTEGER,               -- Financial PII
    deposit_amount DECIMAL(8,2),              -- Financial PII
    service_plan_details TEXT,
    monthly_charges DECIMAL(8,2),             -- Financial data
    usage_history_calls TEXT,                 -- Communication metadata
    usage_history_data TEXT,                  -- Internet usage data
    text_message_logs TEXT,                   -- Communication metadata
    voicemail_recordings BYTEA,               -- Voice biometric data
    international_calling_patterns TEXT,      -- Communication behavior
    roaming_usage_data TEXT,                  -- Location/usage data
    device_information TEXT,                  -- Device identifiers
    imei_numbers TEXT,                        -- Device identifiers
    sim_card_numbers TEXT,                    -- Device identifiers
    network_access_logs TEXT,                 -- Technical usage data
    customer_service_interactions TEXT,       -- Service history
    payment_history TEXT,                     -- Financial history
    account_suspension_history TEXT,          -- Service issues
    fraud_alerts_history TEXT,                -- Security incidents
    location_services_data TEXT,              -- GPS/location data
    wifi_usage_patterns TEXT                  -- Network usage behavior
);

-- 29. Internet service provider logs
CREATE TABLE isp_connection_logs (
    log_entry_id BIGSERIAL PRIMARY KEY,
    customer_account_ref VARCHAR(20),
    subscriber_name VARCHAR(100),             -- PII
    service_address TEXT,                     -- PII
    ip_address_assigned VARCHAR(45),          -- PII/Technical identifier
    mac_address VARCHAR(20),                  -- Device identifier
    connection_timestamp TIMESTAMP,
    disconnection_timestamp TIMESTAMP,
    data_uploaded_mb DECIMAL(12,2),           -- Usage data
    data_downloaded_mb DECIMAL(12,2),         -- Usage data
    websites_visited TEXT,                    -- Browsing history (sensitive)
    dns_queries_log TEXT,                     -- Technical/behavioral data
    bandwidth_usage_pattern TEXT,             -- Usage behavior
    device_user_agent TEXT,                   -- Device/browser fingerprint
    geolocation_data VARCHAR(100),            -- Location data
    vpn_usage_detected BOOLEAN,               -- Privacy tool usage
    tor_usage_detected BOOLEAN,               -- Anonymity tool usage
    p2p_activity_detected BOOLEAN,            -- File sharing activity
    streaming_services_used TEXT,             -- Entertainment preferences
    social_media_activity TEXT,               -- Social behavior
    online_shopping_patterns TEXT,            -- Commercial behavior
    search_engine_queries TEXT,               -- Search behavior (very sensitive)
    email_server_connections TEXT,            -- Email usage patterns
    cloud_storage_usage TEXT,                 -- Data storage behavior
    gaming_activity TEXT,                     -- Gaming behavior
    video_conferencing_usage TEXT,            -- Communication patterns
    network_security_events TEXT             -- Security incidents
);

-- ===== GAMING & ENTERTAINMENT =====

-- 30. Gaming platform user data
CREATE TABLE gaming_platform_users (
    player_id UUID PRIMARY KEY,
    username VARCHAR(50),                     -- PII
    email_address VARCHAR(150),               -- PII
    real_name VARCHAR(100),                   -- PII
    date_of_birth DATE,                       -- PII
    country_region VARCHAR(50),               -- PII
    preferred_language VARCHAR(30),           -- Personal preference
    profile_avatar BYTEA,                     -- Visual identifier
    voice_chat_recordings BYTEA,              -- Voice biometric data
    friend_list TEXT,                         -- Social connections
    blocked_users_list TEXT,                  -- Social interactions
    private_messages TEXT,                    -- Private communications
    public_chat_logs TEXT,                    -- Public communications
    game_purchase_history TEXT,               -- Financial history
    in_game_purchase_transactions TEXT,       -- Financial data
    payment_methods_stored TEXT,              -- Financial PII
    gaming_session_logs TEXT,                 -- Behavioral data
    gameplay_statistics TEXT,                 -- Performance data
    achievement_progress TEXT,                -- Gaming progress
    streaming_activity TEXT,                  -- Content creation
    spectator_mode_usage TEXT,                -- Viewing behavior
    tournament_participation TEXT,            -- Competitive activity
    gambling_related_purchases TEXT,          -- Potentially regulated activity
    age_verification_documents BYTEA,         -- Identity verification
    parental_control_settings TEXT,           -- Family data
    device_hardware_fingerprints TEXT,        -- Technical identifiers
    anti_cheat_violation_records TEXT,        -- Disciplinary records
    customer_support_tickets TEXT,            -- Service interactions
    location_based_matchmaking_data TEXT      -- Geographic gaming data
);

-- 31. Streaming service viewer data
CREATE TABLE streaming_service_analytics (
    viewing_session_id UUID PRIMARY KEY,
    subscriber_account_id VARCHAR(30),
    subscriber_name VARCHAR(100),             -- PII
    subscriber_email VARCHAR(150),            -- PII
    household_members TEXT,                   -- Family PII
    viewing_device_info TEXT,                 -- Device fingerprinting
    ip_address VARCHAR(45),                   -- PII/Location data
    geographic_location VARCHAR(100),         -- Location data
    content_watched TEXT,                     -- Viewing preferences
    watch_time_minutes INTEGER,               -- Usage data
    pause_resume_timestamps TEXT,             -- Detailed behavior
    rewind_fast_forward_actions TEXT,         -- Viewing behavior
    subtitle_language_preferences VARCHAR(30), -- Accessibility/language PII
    audio_language_preferences VARCHAR(30),    -- Language PII
    content_rating_preferences TEXT,          -- Content preferences
    search_queries TEXT,                      -- Search behavior
    recommendation_interactions TEXT,         -- Algorithm interaction
    watchlist_contents TEXT,                  -- Personal preferences
    download_activity TEXT,                   -- Offline viewing behavior
    simultaneous_streams_count INTEGER,       -- Usage patterns
    family_profile_usage TEXT,                -- Household viewing data
    parental_control_violations TEXT,         -- Age-restricted content access
    billing_information_encrypted TEXT,       -- Financial PII
    subscription_tier VARCHAR(30),            -- Service level
    promotional_email_interactions TEXT,      -- Marketing response
    customer_service_contacts TEXT,           -- Support interactions
    account_sharing_detection_data TEXT,      -- Security/usage analysis
    content_piracy_monitoring_flags TEXT,     -- Security flags
    viewing_session_start TIMESTAMP,
    viewing_session_end TIMESTAMP
);

-- ===== RESEARCH & CLINICAL TRIALS =====

-- 32. Clinical trial participant data
CREATE TABLE clinical_trial_participants (
    participant_id UUID PRIMARY KEY,
    trial_protocol_number VARCHAR(30),
    participant_first_name VARCHAR(50),       -- PII
    participant_last_name VARCHAR(50),        -- PII
    date_of_birth DATE,                       -- PII/PHI
    social_security_number CHAR(11),          -- PII
    medical_record_number VARCHAR(25),        -- PHI
    contact_address TEXT,                     -- PII
    phone_number VARCHAR(15),                 -- PII
    email_address VARCHAR(150),               -- PII
    emergency_contact_info TEXT,              -- PII
    primary_care_physician VARCHAR(100),      -- PHI
    medical_history_detailed TEXT,            -- PHI
    current_medications TEXT,                 -- PHI
    allergies_documented TEXT,                -- PHI
    baseline_vital_signs TEXT,                -- PHI
    laboratory_test_results TEXT,             -- PHI
    genetic_test_results TEXT,                -- Genetic/biometric data
    dna_samples_collected BOOLEAN,            -- Biometric data flag
    blood_samples_analysis TEXT,              -- PHI/biometric
    tissue_samples_collected TEXT,            -- PHI/biometric
    imaging_studies_results TEXT,             -- PHI
    psychological_assessments TEXT,           -- Mental health PHI
    quality_of_life_surveys TEXT,             -- Health-related PII
    adverse_reactions_reported TEXT,          -- PHI
    serious_adverse_events TEXT,              -- PHI
    concomitant_medications TEXT,             -- PHI
    protocol_deviations TEXT,                 -- Clinical data
    withdrawal_reasons TEXT,                  -- Clinical/personal data
    informed_consent_documents TEXT,          -- Legal/ethical documentation
    compensation_payments DECIMAL(8,2),       -- Financial PII
    travel_reimbursements DECIMAL(6,2),       -- Financial PII
    study_completion_status VARCHAR(50),
    follow_up_schedule TEXT,
    long_term_outcome_data TEXT               -- Long-term PHI
);

-- 33. Research survey responses
CREATE TABLE research_survey_responses (
    response_id UUID PRIMARY KEY,
    study_identifier VARCHAR(30),
    participant_anonymous_id VARCHAR(50),     -- Pseudonymized ID
    participant_demographics TEXT,            -- Age, gender, etc. (PII)
    socioeconomic_status TEXT,                -- Income, education (sensitive PII)
    ethnicity_race VARCHAR(100),              -- Sensitive PII
    sexual_orientation VARCHAR(50),           -- Sensitive PII
    religious_affiliation VARCHAR(100),       -- Sensitive PII
    political_opinions TEXT,                  -- Sensitive PII
    health_status_self_reported TEXT,         -- PHI
    mental_health_history TEXT,               -- Sensitive PHI
    substance_use_history TEXT,               -- Sensitive PHI
    sexual_behavior_data TEXT,                -- Sensitive personal data
    family_history_medical TEXT,              -- PHI
    genetic_predispositions TEXT,             -- Genetic data
    lifestyle_habits TEXT,                    -- Health-related behavior
    dietary_patterns TEXT,                    -- Health-related data
    exercise_routines TEXT,                   -- Health-related data
    sleep_patterns TEXT,                      -- Health-related data
    stress_levels_reported TEXT,              -- Mental health data
    relationship_status_history TEXT,         -- Personal relationship data
    parenting_information TEXT,               -- Family data
    employment_history TEXT,                  -- Professional PII
    financial_status_details TEXT,            -- Financial PII
    housing_situation TEXT,                   -- Socioeconomic PII
    transportation_access TEXT,               -- Socioeconomic data
    technology_usage_patterns TEXT,           -- Behavioral data
    social_media_behavior TEXT,               -- Online behavior
    privacy_concerns_expressed TEXT,          -- Privacy attitudes
    survey_completion_timestamp TIMESTAMP,
    ip_address_recorded VARCHAR(45),          -- Technical PII
    device_information TEXT,                  -- Technical fingerprinting
    geolocation_data VARCHAR(100)             -- Location data
);

-- ===== LEGAL SERVICES & LAW ENFORCEMENT =====

-- 34. Legal case evidence database
CREATE TABLE legal_evidence_database (
    evidence_id UUID PRIMARY KEY,
    case_number VARCHAR(30),
    evidence_type VARCHAR(50),
    evidence_description TEXT,
    chain_of_custody_log TEXT,                -- Legal tracking
    collected_by_officer VARCHAR(100),        -- PII of law enforcement
    collection_date_time TIMESTAMP,
    collection_location TEXT,                 -- Location data
    witness_statements TEXT,                  -- Witness PII
    suspect_information TEXT,                 -- Subject PII
    victim_information TEXT,                  -- Victim PII
    digital_evidence_hash VARCHAR(255),       -- Digital forensics
    dna_analysis_results TEXT,                -- Biometric evidence
    fingerprint_data BYTEA,                   -- Biometric evidence
    photographs_evidence BYTEA,               -- Visual evidence (may contain faces)
    audio_recordings BYTEA,                   -- Voice recordings
    video_surveillance BYTEA,                 -- Video evidence (faces, behavior)
    computer_forensics_data TEXT,             -- Digital device analysis
    phone_records_extracted TEXT,             -- Communication metadata
    email_communications TEXT,                -- Private communications
    social_media_activity TEXT,               -- Online behavior evidence
    financial_records_seized TEXT,            -- Financial investigation data
    search_warrant_details TEXT,              -- Legal authorization
    miranda_rights_acknowledgment TEXT,       -- Legal rights documentation
    interrogation_transcripts TEXT,           -- Legal questioning records
    polygraph_test_results TEXT,              -- Investigation tool results
    psychological_evaluation TEXT,            -- Mental health assessment
    medical_examination_results TEXT,         -- Physical evidence/PHI
    ballistics_analysis TEXT,                 -- Forensic analysis
    toxicology_reports TEXT,                  -- Substance analysis/PHI
    crime_scene_reconstruction TEXT           -- Investigation analysis
);

-- 35. Law enforcement incident reports
CREATE TABLE law_enforcement_incidents (
    incident_report_id VARCHAR(30) PRIMARY KEY,
    reporting_officer_name VARCHAR(100),      -- PII of officer
    reporting_officer_badge VARCHAR(20),      -- Officer identifier
    incident_date_time TIMESTAMP,
    incident_location TEXT,                   -- Location data
    incident_type VARCHAR(100),
    incident_description TEXT,
    subjects_involved TEXT,                   -- Subject PII
    subject_names TEXT,                       -- PII
    subject_addresses TEXT,                   -- PII
    subject_phone_numbers TEXT,               -- PII
    subject_identification_numbers TEXT,      -- Government IDs (PII)
    subject_physical_descriptions TEXT,       -- Physical characteristics
    subject_criminal_history TEXT,            -- Criminal background (sensitive)
    victims_involved TEXT,                    -- Victim PII
    victim_names TEXT,                        -- PII
    victim_contact_information TEXT,          -- PII
    victim_medical_information TEXT,          -- PHI
    witness_information TEXT,                 -- Witness PII
    witness_statements TEXT,                  -- Witness testimony
    property_involved TEXT,                   -- Property descriptions
    property_damage_assessment TEXT,          -- Damage reports
    evidence_collected_list TEXT,             -- Evidence inventory
    body_camera_footage BYTEA,                -- Video evidence with faces/voices
    dash_camera_footage BYTEA,                -- Vehicle camera evidence
    photographs_taken BYTEA,                  -- Scene photography
    911_call_recordings BYTEA,                -- Emergency call audio
    dispatch_communications TEXT,             -- Radio communications
    backup_officers_responding TEXT,          -- Officer PII
    supervisor_notifications TEXT,            -- Chain of command
    medical_treatment_provided TEXT,          -- Medical/PHI information
    arrests_made TEXT,                        -- Arrest records
    citations_issued TEXT,                    -- Legal citations
    charges_filed TEXT,                       -- Legal charges
    court_appearance_scheduled TEXT,          -- Legal proceedings
    case_status VARCHAR(50),
    follow_up_required TEXT,
    report_approved_by VARCHAR(100),          -- Supervisor PII
    report_approval_timestamp TIMESTAMP
);

-- ===== ADDITIONAL SPECIALIZED TABLES =====

-- 36. Biometric authentication system
CREATE TABLE biometric_authentication_data (
    biometric_record_id UUID PRIMARY KEY,
    user_identifier VARCHAR(50),              -- User reference
    fingerprint_template BYTEA,               -- Biometric data
    facial_recognition_template BYTEA,        -- Biometric data
    iris_scan_template BYTEA,                 -- Biometric data
    voice_print_template BYTEA,               -- Biometric data
    retinal_scan_data BYTEA,                  -- Biometric data
    palm_print_template BYTEA,                -- Biometric data
    dna_genetic_markers TEXT,                 -- Genetic biometric data
    gait_analysis_pattern BYTEA,              -- Behavioral biometric
    keystroke_dynamics_profile TEXT,          -- Behavioral biometric
    signature_dynamics_template BYTEA,        -- Behavioral biometric
    enrollment_timestamp TIMESTAMP,
    last_authentication_timestamp TIMESTAMP,
    authentication_attempts_log TEXT,
    failed_authentication_count INTEGER,
    biometric_quality_scores TEXT,
    enrollment_device_info TEXT,              -- Device used for enrollment
    authentication_device_info TEXT,          -- Device used for auth
    template_encryption_key_id VARCHAR(50),   -- Security key reference
    biometric_data_retention_policy TEXT,     -- Privacy policy reference
    consent_to_biometric_processing BOOLEAN,  -- Privacy consent
    biometric_data_sharing_permissions TEXT,  -- Privacy permissions
    cross_system_matching_allowed BOOLEAN,    -- Privacy setting
    law_enforcement_access_flag BOOLEAN,      -- Legal access flag
    data_breach_notification_sent BOOLEAN,    -- Security incident flag
    biometric_template_version VARCHAR(10),   -- Technical version
    quality_threshold_met BOOLEAN,            -- Technical quality flag
    liveness_detection_passed BOOLEAN,        -- Anti-spoofing flag
    multi_modal_fusion_score DECIMAL(5,4)     -- Combined biometric score
);

