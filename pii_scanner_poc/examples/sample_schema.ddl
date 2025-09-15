-- =============================================================================
-- Sample DDL File for PII/PHI Scanner Testing
-- =============================================================================
-- 
-- This DDL file contains realistic database table structures for testing 
-- the PII/PHI Scanner's capabilities. It includes various types of sensitive
-- data commonly found in healthcare, business, and research environments.
--
-- **Tables Included:**
-- 1. patients        - Patient demographic and contact information
-- 2. medical_records  - Medical diagnoses and treatment information  
-- 3. employees       - Employee personal and employment data
-- 4. financial_transactions - Payment and financial account information
-- 5. appointments    - Healthcare appointment scheduling data
-- 6. audit_log       - System access and activity tracking
-- 7. research_data   - Anonymized research participant information
--
-- **PII/PHI Categories Represented:**
-- - Personal Identifiers: Names, SSN, email, phone, addresses
-- - Health Information: Medical records, diagnoses, insurance data
-- - Financial Data: Credit cards, bank accounts, transaction details
-- - Employment Data: Salary information, employee records
-- - Technical Data: IP addresses, user agents, system logs
--
-- **Regulatory Scope:**
-- - HIPAA: Protected Health Information (PHI)
-- - GDPR: Personal Data and Special Categories
-- - CCPA: Personal Information and Commercial Data
--
-- Author: AI Assistant (for testing purposes)
-- Version: 1.0 POC
-- =============================================================================

-- Table 1: Patient Demographics and Contact Information
-- Contains high-sensitivity PII/PHI data subject to HIPAA, GDPR, and CCPA
CREATE TABLE dbo.patients (
    -- Primary identifier (not directly PII but enables linking)
    patient_id INT PRIMARY KEY,
    
    -- Personal identifiers (High sensitivity - GDPR/CCPA)
    first_name VARCHAR(50),          -- Personal name data
    last_name VARCHAR(50),           -- Personal name data
    date_of_birth DATE,              -- Birth information (HIPAA/GDPR)
    
    -- Government identifiers (Highest sensitivity - All regulations)
    ssn VARCHAR(11),                 -- Social Security Number
    
    -- Contact information (High sensitivity - GDPR/CCPA)
    email VARCHAR(100),              -- Email address for communications
    phone VARCHAR(20),               -- Phone number for contact
    address VARCHAR(200),            -- Physical address
    city VARCHAR(50),                -- City of residence
    state VARCHAR(20),               -- State/province
    zip_code VARCHAR(10),            -- Postal code
    
    -- Healthcare identifiers (High sensitivity - HIPAA)
    insurance_number VARCHAR(50),    -- Health insurance identifier
    medical_record_number VARCHAR(20), -- Hospital MRN
    
    -- System metadata (Low sensitivity)
    created_date DATETIME,           -- Record creation timestamp
    updated_date DATETIME            -- Last modification timestamp
);

-- Table 2: Medical Records and Health Information
-- Contains Protected Health Information (PHI) under HIPAA
CREATE TABLE dbo.medical_records (
    -- Record identifier
    record_id INT PRIMARY KEY,
    
    -- Patient reference (enables data linking)
    patient_id INT,                  -- Links to patients table
    
    -- Medical information (High sensitivity - HIPAA)
    diagnosis_code VARCHAR(10),      -- ICD-10 diagnosis codes
    diagnosis_description VARCHAR(500), -- Human-readable diagnosis
    treatment_notes TEXT,            -- Doctor's treatment notes
    prescription_details TEXT,       -- Medication prescriptions
    lab_results TEXT,                -- Laboratory test results
    doctor_notes TEXT,               -- Clinical observations
    
    -- Healthcare scheduling (Medium sensitivity - HIPAA)
    visit_date DATE,                 -- Date of medical visit
    follow_up_date DATE,             -- Scheduled follow-up
    
    -- System tracking (Low sensitivity)
    created_by VARCHAR(50),          -- User who created record
    created_date DATETIME            -- Record creation time
);

-- Table 3: Employee Information
-- Contains employment-related PII subject to GDPR and CCPA
CREATE TABLE dbo.employees (
    -- Employee identifier
    employee_id INT PRIMARY KEY,
    
    -- Personal information (High sensitivity - GDPR/CCPA)
    first_name VARCHAR(50),          -- Employee first name
    last_name VARCHAR(50),           -- Employee last name
    email VARCHAR(100),              -- Work email address
    phone VARCHAR(20),               -- Contact phone number
    
    -- Employment information (Medium sensitivity)
    department VARCHAR(50),          -- Work department
    position VARCHAR(100),           -- Job title/position
    salary DECIMAL(10,2),            -- Compensation (Financial - CCPA)
    hire_date DATE,                  -- Employment start date
    manager_id INT,                  -- Reference to manager
    
    -- System metadata
    created_date DATETIME            -- Record creation timestamp
);

-- Table 4: Financial Transaction Data
-- Contains financial information subject to CCPA and banking regulations
CREATE TABLE dbo.financial_transactions (
    -- Transaction identifier
    transaction_id INT PRIMARY KEY,
    
    -- Customer reference
    patient_id INT,                  -- Links to patient for medical billing
    
    -- Financial details (High sensitivity - CCPA/Banking)
    amount DECIMAL(10,2),            -- Transaction amount
    payment_method VARCHAR(20),      -- Payment type (cash, card, etc.)
    credit_card_number VARCHAR(20),  -- Credit card PAN (masked)
    bank_account_number VARCHAR(20), -- Bank account identifier
    routing_number VARCHAR(20),      -- Bank routing number
    
    -- Transaction metadata
    transaction_date DATE,           -- Date of transaction
    description VARCHAR(200),        -- Transaction description
    created_date DATETIME            -- System creation time
);

-- Table 5: Healthcare Appointments
-- Contains scheduling information with moderate sensitivity
CREATE TABLE dbo.appointments (
    -- Appointment identifier
    appointment_id INT PRIMARY KEY,
    
    -- References to other entities
    patient_id INT,                  -- Patient receiving care
    doctor_id INT,                   -- Healthcare provider
    
    -- Appointment details (Medium sensitivity - HIPAA)
    appointment_date DATETIME,       -- Scheduled date and time
    appointment_type VARCHAR(50),    -- Type of appointment
    notes TEXT,                      -- Appointment notes
    status VARCHAR(20),              -- Current status (scheduled, completed, etc.)
    
    -- System metadata
    created_date DATETIME            -- Record creation timestamp
);

-- Table 6: System Audit Log
-- Contains system access and activity tracking information
CREATE TABLE dbo.audit_log (
    -- Log entry identifier
    log_id INT PRIMARY KEY,
    
    -- User and system information
    user_id INT,                     -- User performing action
    action VARCHAR(100),             -- Action performed
    table_name VARCHAR(50),          -- Database table affected
    record_id INT,                   -- Specific record ID affected
    
    -- Technical tracking (Medium sensitivity - GDPR)
    timestamp DATETIME,              -- When action occurred
    ip_address VARCHAR(50),          -- Source IP address (GDPR tracking)
    user_agent TEXT                  -- Browser/client information (Low GDPR)
);

-- Table 7: Research Data (Anonymized)
-- Contains de-identified research information with reduced sensitivity
CREATE TABLE dbo.research_data (
    -- Research record identifier
    research_id INT PRIMARY KEY,
    
    -- Anonymized participant information (Low-Medium sensitivity)
    subject_id VARCHAR(20),          -- De-identified subject ID
    age_group VARCHAR(20),           -- Age range (not exact age)
    gender VARCHAR(10),              -- Gender for research purposes
    condition VARCHAR(100),          -- Medical condition being studied
    treatment_outcome VARCHAR(100),  -- Research outcome measures
    
    -- Research data (Low sensitivity when properly anonymized)
    anonymized_data TEXT,            -- De-identified research data
    
    -- Study metadata
    study_date DATE,                 -- Date of study participation
    created_date DATETIME            -- Record creation time
);

-- =============================================================================
-- End of Sample DDL
-- =============================================================================
-- 
-- **Usage Notes:**
-- 1. This DDL is designed for testing PII/PHI detection capabilities
-- 2. Real implementations should use appropriate constraints and indexes
-- 3. Production systems should implement proper encryption and access controls
-- 4. Consider data masking for non-production environments
-- 
-- **Expected Analysis Results:**
-- - High-risk tables: patients, medical_records, financial_transactions
-- - Medium-risk tables: employees, appointments, audit_log
-- - Lower-risk tables: research_data (when properly anonymized)
-- 
-- **Compliance Considerations:**
-- - HIPAA applies to patients, medical_records, appointments tables
-- - GDPR applies to most tables containing personal identifiers
-- - CCPA applies to personal and commercial information
-- =============================================================================