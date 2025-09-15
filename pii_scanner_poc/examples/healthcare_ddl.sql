-- Healthcare DDL for PII/PHI Scanner POC
-- Specialized healthcare scenarios with complex PHI patterns
-- Purpose: Testing healthcare-specific PII/PHI detection
-- Compliance: HIPAA, 21 CFR Part 11, HITECH Act

-- =============================================================================
-- ELECTRONIC HEALTH RECORDS (EHR) SYSTEM
-- =============================================================================

-- Comprehensive Patient Demographics
CREATE TABLE patient_demographics (
    patient_guid VARCHAR(36) PRIMARY KEY,
    mrn VARCHAR(20) UNIQUE NOT NULL, -- Medical Record Number
    ssn VARCHAR(11), -- Social Security Number
    medicare_number VARCHAR(15),
    medicaid_number VARCHAR(20),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    maiden_name VARCHAR(50),
    suffix VARCHAR(10),
    preferred_name VARCHAR(50),
    date_of_birth DATE NOT NULL,
    time_of_birth TIME,
    birth_city VARCHAR(100),
    birth_state VARCHAR(50),
    birth_country VARCHAR(50),
    gender CHAR(1),
    biological_sex CHAR(1),
    gender_identity VARCHAR(50),
    sexual_orientation VARCHAR(50),
    race_primary VARCHAR(50),
    race_secondary VARCHAR(50),
    ethnicity VARCHAR(50),
    primary_language VARCHAR(30),
    interpreter_needed BOOLEAN,
    religion VARCHAR(50),
    marital_status VARCHAR(20),
    occupation VARCHAR(100),
    employer_name VARCHAR(100),
    home_address_line1 VARCHAR(100),
    home_address_line2 VARCHAR(100),
    home_city VARCHAR(50),
    home_state VARCHAR(20),
    home_zipcode VARCHAR(10),
    home_country VARCHAR(50),
    mailing_address_different BOOLEAN,
    mailing_address TEXT,
    home_phone VARCHAR(15),
    work_phone VARCHAR(15),
    mobile_phone VARCHAR(15),
    email_personal VARCHAR(100),
    email_work VARCHAR(100),
    emergency_contact_1_name VARCHAR(100),
    emergency_contact_1_relationship VARCHAR(30),
    emergency_contact_1_phone VARCHAR(15),
    emergency_contact_1_address TEXT,
    emergency_contact_2_name VARCHAR(100),
    emergency_contact_2_relationship VARCHAR(30),
    emergency_contact_2_phone VARCHAR(15),
    next_of_kin_name VARCHAR(100),
    next_of_kin_relationship VARCHAR(30),
    next_of_kin_phone VARCHAR(15),
    power_of_attorney_name VARCHAR(100),
    power_of_attorney_phone VARCHAR(15),
    guardian_name VARCHAR(100),
    guardian_relationship VARCHAR(30),
    guardian_phone VARCHAR(15),
    deceased_flag BOOLEAN DEFAULT FALSE,
    death_date DATE,
    death_time TIME,
    cause_of_death TEXT,
    autopsy_performed BOOLEAN,
    organ_donor_status VARCHAR(20),
    advance_directives_on_file BOOLEAN,
    living_will_on_file BOOLEAN,
    healthcare_proxy_on_file BOOLEAN,
    hipaa_authorization_signed BOOLEAN,
    photo_consent_signed BOOLEAN,
    research_consent_signed BOOLEAN,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_by VARCHAR(100),
    last_modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clinical Encounters with Detailed PHI
CREATE TABLE clinical_encounters (
    encounter_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    visit_number VARCHAR(15),
    encounter_type VARCHAR(30), -- Inpatient, Outpatient, Emergency, Telehealth
    admission_date DATE,
    admission_time TIME,
    discharge_date DATE,
    discharge_time TIME,
    length_of_stay INTEGER, -- days
    admission_source VARCHAR(50),
    discharge_disposition VARCHAR(50),
    hospital_unit VARCHAR(50),
    room_number VARCHAR(10),
    bed_number VARCHAR(10),
    attending_physician_npi VARCHAR(10),
    attending_physician_name VARCHAR(100),
    attending_physician_specialty VARCHAR(100),
    resident_physician_name VARCHAR(100),
    consulting_physicians TEXT,
    primary_nurse_name VARCHAR(100),
    case_manager_name VARCHAR(100),
    social_worker_name VARCHAR(100),
    chaplain_name VARCHAR(100),
    chief_complaint TEXT,
    history_present_illness TEXT,
    review_of_systems TEXT,
    past_medical_history TEXT,
    past_surgical_history TEXT,
    family_history TEXT,
    social_history TEXT,
    allergies_medications TEXT,
    allergies_environmental TEXT,
    allergies_food TEXT,
    current_medications TEXT,
    vital_signs_on_admission TEXT,
    physical_examination TEXT,
    mental_status_exam TEXT,
    diagnostic_impression TEXT,
    treatment_plan TEXT,
    procedures_performed TEXT,
    complications TEXT,
    discharge_instructions TEXT,
    follow_up_appointments TEXT,
    discharge_medications TEXT,
    patient_education_provided TEXT,
    interpreter_used BOOLEAN,
    interpreter_name VARCHAR(100),
    total_charges DECIMAL(12,2),
    insurance_authorization_number VARCHAR(50),
    workers_comp_claim_number VARCHAR(30),
    auto_accident_claim_number VARCHAR(30),
    legal_case_number VARCHAR(30),
    photography_consent BOOLEAN,
    research_study_participation TEXT,
    quality_measures_met TEXT,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Laboratory Results with Sensitive Health Data
CREATE TABLE laboratory_results (
    lab_result_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    encounter_id VARCHAR(20) REFERENCES clinical_encounters(encounter_id),
    lab_order_id VARCHAR(20),
    ordering_physician_npi VARCHAR(10),
    ordering_physician_name VARCHAR(100),
    collection_date DATE,
    collection_time TIME,
    specimen_id VARCHAR(20),
    specimen_type VARCHAR(50),
    specimen_source VARCHAR(100),
    collection_method VARCHAR(50),
    collected_by VARCHAR(100),
    transport_conditions VARCHAR(100),
    test_panel_name VARCHAR(100),
    test_code VARCHAR(20),
    test_name VARCHAR(100),
    test_method VARCHAR(100),
    result_value VARCHAR(500),
    result_units VARCHAR(20),
    reference_range VARCHAR(100),
    abnormal_flag VARCHAR(10),
    critical_value_flag BOOLEAN,
    panic_value_flag BOOLEAN,
    delta_check_flag BOOLEAN,
    resulted_date DATE,
    resulted_time TIME,
    verified_by VARCHAR(100),
    performing_lab_name VARCHAR(100),
    performing_lab_clia_number VARCHAR(20),
    lab_director_name VARCHAR(100),
    pathologist_name VARCHAR(100),
    technologist_name VARCHAR(100),
    instrument_id VARCHAR(50),
    quality_control_results TEXT,
    clinical_significance TEXT,
    additional_comments TEXT,
    patient_notified BOOLEAN,
    notification_date DATE,
    notification_method VARCHAR(50),
    critical_value_called_to VARCHAR(100),
    call_back_time TIMESTAMP,
    amended_result BOOLEAN,
    amendment_reason TEXT,
    original_result_value VARCHAR(500),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prescription and Medication Administration
CREATE TABLE medication_administration (
    med_admin_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    encounter_id VARCHAR(20) REFERENCES clinical_encounters(encounter_id),
    prescription_id VARCHAR(20),
    medication_order_id VARCHAR(20),
    prescribing_physician_npi VARCHAR(10),
    prescribing_physician_name VARCHAR(100),
    prescribing_physician_dea VARCHAR(15),
    medication_name VARCHAR(100),
    medication_brand_name VARCHAR(100),
    medication_generic_name VARCHAR(100),
    ndc_number VARCHAR(15), -- National Drug Code
    medication_strength VARCHAR(50),
    dosage_form VARCHAR(30),
    route_of_administration VARCHAR(30),
    frequency VARCHAR(50),
    duration VARCHAR(30),
    quantity_prescribed INTEGER,
    quantity_dispensed INTEGER,
    days_supply INTEGER,
    refills_authorized INTEGER,
    refills_remaining INTEGER,
    prescription_date DATE,
    fill_date DATE,
    last_fill_date DATE,
    next_refill_date DATE,
    pharmacy_name VARCHAR(100),
    pharmacy_npi VARCHAR(10),
    pharmacy_address TEXT,
    pharmacist_name VARCHAR(100),
    pharmacist_license_number VARCHAR(20),
    drug_interactions_checked BOOLEAN,
    allergy_interactions_checked BOOLEAN,
    contraindications_checked BOOLEAN,
    duplicate_therapy_checked BOOLEAN,
    patient_counseling_completed BOOLEAN,
    counseling_notes TEXT,
    administration_time TIMESTAMP,
    administered_by VARCHAR(100),
    administration_site VARCHAR(50),
    administration_route VARCHAR(30),
    lot_number VARCHAR(30),
    expiration_date DATE,
    manufacturer VARCHAR(100),
    adverse_reactions TEXT,
    effectiveness_notes TEXT,
    patient_compliance_notes TEXT,
    cost_patient DECIMAL(8,2),
    cost_insurance DECIMAL(8,2),
    insurance_copay DECIMAL(6,2),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Radiology and Imaging Studies
CREATE TABLE radiology_studies (
    study_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    encounter_id VARCHAR(20) REFERENCES clinical_encounters(encounter_id),
    accession_number VARCHAR(20) UNIQUE,
    study_instance_uid VARCHAR(100),
    ordering_physician_npi VARCHAR(10),
    ordering_physician_name VARCHAR(100),
    performing_physician_npi VARCHAR(10),
    performing_physician_name VARCHAR(100),
    radiologist_npi VARCHAR(10),
    radiologist_name VARCHAR(100),
    technologist_name VARCHAR(100),
    study_date DATE,
    study_time TIME,
    modality VARCHAR(10), -- CT, MRI, X-Ray, Ultrasound, etc.
    body_part_examined VARCHAR(100),
    study_description TEXT,
    procedure_code VARCHAR(20),
    clinical_indication TEXT,
    patient_history TEXT,
    contrast_used BOOLEAN,
    contrast_type VARCHAR(50),
    contrast_amount VARCHAR(20),
    contrast_allergies_checked BOOLEAN,
    pregnancy_status_checked BOOLEAN,
    radiation_dose_recorded VARCHAR(50),
    equipment_manufacturer VARCHAR(50),
    equipment_model VARCHAR(50),
    equipment_serial_number VARCHAR(50),
    acquisition_parameters TEXT,
    image_count INTEGER,
    series_count INTEGER,
    study_status VARCHAR(20),
    preliminary_report TEXT,
    final_report TEXT,
    impression TEXT,
    recommendations TEXT,
    critical_findings BOOLEAN,
    critical_findings_communicated BOOLEAN,
    communication_date DATE,
    communication_time TIME,
    communicated_to VARCHAR(100),
    addendum_reports TEXT,
    comparison_studies TEXT,
    image_quality VARCHAR(20),
    artifacts_noted TEXT,
    patient_cooperation VARCHAR(50),
    sedation_used BOOLEAN,
    sedation_type VARCHAR(50),
    monitoring_during_study TEXT,
    adverse_events TEXT,
    dicom_study_path VARCHAR(255),
    burned_to_cd BOOLEAN,
    patient_copy_requested BOOLEAN,
    physician_copy_sent TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Surgical Procedures and Operative Notes
CREATE TABLE surgical_procedures (
    procedure_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    encounter_id VARCHAR(20) REFERENCES clinical_encounters(encounter_id),
    procedure_date DATE,
    procedure_start_time TIME,
    procedure_end_time TIME,
    procedure_duration INTEGER, -- minutes
    operating_room VARCHAR(10),
    primary_surgeon_npi VARCHAR(10),
    primary_surgeon_name VARCHAR(100),
    assistant_surgeons TEXT,
    anesthesiologist_npi VARCHAR(10),
    anesthesiologist_name VARCHAR(100),
    anesthesia_type VARCHAR(50),
    scrub_nurse_name VARCHAR(100),
    circulating_nurse_name VARCHAR(100),
    procedure_name VARCHAR(200),
    procedure_codes TEXT, -- CPT codes
    diagnosis_codes TEXT, -- ICD-10 codes
    urgency_level VARCHAR(20),
    wound_classification VARCHAR(30),
    asa_score VARCHAR(10), -- American Society of Anesthesiologists
    preoperative_diagnosis TEXT,
    postoperative_diagnosis TEXT,
    operative_findings TEXT,
    procedure_description TEXT,
    complications_intraoperative TEXT,
    estimated_blood_loss VARCHAR(20),
    fluid_replacement TEXT,
    specimens_sent TEXT,
    implants_used TEXT,
    implant_lot_numbers TEXT,
    count_discrepancies TEXT,
    postoperative_instructions TEXT,
    disposition VARCHAR(50),
    recovery_room_time INTEGER, -- minutes
    icu_admission BOOLEAN,
    postoperative_complications TEXT,
    follow_up_scheduled TEXT,
    pathology_requested BOOLEAN,
    cultures_sent BOOLEAN,
    photography_consent BOOLEAN,
    video_recording_consent BOOLEAN,
    teaching_case BOOLEAN,
    resident_participation TEXT,
    equipment_used TEXT,
    blood_products_used TEXT,
    antibiotic_prophylaxis TEXT,
    venous_thromboembolism_prophylaxis TEXT,
    quality_indicators_met TEXT,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mental Health and Behavioral Health Records
CREATE TABLE mental_health_records (
    mental_health_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    encounter_id VARCHAR(20) REFERENCES clinical_encounters(encounter_id),
    provider_npi VARCHAR(10),
    provider_name VARCHAR(100),
    provider_type VARCHAR(50), -- Psychiatrist, Psychologist, LCSW, etc.
    provider_license_number VARCHAR(20),
    session_date DATE,
    session_start_time TIME,
    session_end_time TIME,
    session_duration INTEGER, -- minutes
    session_type VARCHAR(30), -- Individual, Group, Family, etc.
    treatment_modality VARCHAR(50),
    presenting_problem TEXT,
    mental_status_exam TEXT,
    mood_assessment VARCHAR(100),
    affect_assessment VARCHAR(100),
    thought_process_assessment TEXT,
    thought_content_assessment TEXT,
    perceptual_disturbances TEXT,
    cognitive_assessment TEXT,
    insight_assessment VARCHAR(100),
    judgment_assessment VARCHAR(100),
    risk_assessment TEXT,
    suicide_risk_level VARCHAR(20),
    homicide_risk_level VARCHAR(20),
    substance_use_assessment TEXT,
    current_medications TEXT,
    medication_compliance TEXT,
    side_effects_reported TEXT,
    therapy_goals TEXT,
    treatment_plan_updates TEXT,
    progress_notes TEXT,
    homework_assignments TEXT,
    family_involvement TEXT,
    group_dynamics_notes TEXT,
    crisis_plan TEXT,
    safety_plan TEXT,
    diagnosis_primary VARCHAR(100),
    diagnosis_secondary TEXT,
    dsm5_codes TEXT,
    gaf_score INTEGER, -- Global Assessment of Functioning
    clinical_impressions TEXT,
    recommendations TEXT,
    referrals_made TEXT,
    follow_up_plan TEXT,
    session_notes TEXT,
    confidentiality_discussed BOOLEAN,
    mandatory_reporting_issues TEXT,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insurance and Billing Information
CREATE TABLE patient_insurance (
    insurance_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    insurance_rank INTEGER, -- 1=Primary, 2=Secondary, etc.
    insurance_company_name VARCHAR(100),
    insurance_company_id VARCHAR(50),
    policy_number VARCHAR(50),
    group_number VARCHAR(50),
    member_id VARCHAR(50),
    subscriber_name VARCHAR(100),
    subscriber_ssn VARCHAR(11),
    subscriber_date_of_birth DATE,
    subscriber_relationship VARCHAR(30),
    subscriber_employer VARCHAR(100),
    subscriber_address TEXT,
    subscriber_phone VARCHAR(15),
    effective_date DATE,
    termination_date DATE,
    coverage_type VARCHAR(50),
    copay_amount DECIMAL(6,2),
    deductible_amount DECIMAL(8,2),
    deductible_met_amount DECIMAL(8,2),
    out_of_pocket_max DECIMAL(8,2),
    out_of_pocket_met DECIMAL(8,2),
    prior_authorization_required BOOLEAN,
    referral_required BOOLEAN,
    pcp_name VARCHAR(100),
    pcp_npi VARCHAR(10),
    insurance_phone VARCHAR(15),
    claims_address TEXT,
    eligibility_verified BOOLEAN,
    eligibility_verification_date DATE,
    verification_representative VARCHAR(100),
    verification_reference_number VARCHAR(50),
    benefits_summary TEXT,
    exclusions TEXT,
    pre_existing_condition_waiting_period INTEGER,
    coordination_of_benefits TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Genetic Testing and Genomic Data
CREATE TABLE genetic_testing (
    genetic_test_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    test_order_date DATE,
    specimen_collection_date DATE,
    ordering_physician_npi VARCHAR(10),
    ordering_physician_name VARCHAR(100),
    genetic_counselor_name VARCHAR(100),
    testing_laboratory VARCHAR(100),
    laboratory_clia_number VARCHAR(20),
    test_type VARCHAR(100),
    test_methodology VARCHAR(100),
    genes_analyzed TEXT,
    chromosomes_analyzed TEXT,
    clinical_indication TEXT,
    family_history_relevant TEXT,
    ethnicity_considerations TEXT,
    consent_obtained BOOLEAN,
    consent_date DATE,
    test_results TEXT,
    pathogenic_variants TEXT,
    likely_pathogenic_variants TEXT,
    variants_uncertain_significance TEXT,
    benign_variants TEXT,
    copy_number_variants TEXT,
    interpretation TEXT,
    clinical_significance TEXT,
    recommendations TEXT,
    follow_up_testing_recommended TEXT,
    family_testing_recommendations TEXT,
    genetic_counseling_recommended BOOLEAN,
    incidental_findings TEXT,
    incidental_findings_reported BOOLEAN,
    patient_notification_date DATE,
    family_notification_recommendations TEXT,
    research_participation_offered BOOLEAN,
    raw_data_storage_location VARCHAR(255),
    data_sharing_permissions TEXT,
    retention_period INTEGER, -- years
    destruction_date DATE,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- SPECIALIZED HEALTHCARE TABLES
-- =============================================================================

-- Pediatric Specific Information
CREATE TABLE pediatric_records (
    pediatric_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    birth_weight DECIMAL(6,2), -- grams
    birth_length DECIMAL(5,2), -- centimeters
    head_circumference_birth DECIMAL(5,2),
    gestational_age INTEGER, -- weeks
    apgar_score_1min INTEGER,
    apgar_score_5min INTEGER,
    delivery_type VARCHAR(30),
    delivery_complications TEXT,
    mother_name VARCHAR(100),
    mother_ssn VARCHAR(11),
    mother_date_of_birth DATE,
    father_name VARCHAR(100),
    father_ssn VARCHAR(11),
    father_date_of_birth DATE,
    custody_arrangements TEXT,
    school_name VARCHAR(100),
    school_address TEXT,
    school_phone VARCHAR(15),
    teacher_name VARCHAR(100),
    grade_level VARCHAR(20),
    special_education_services BOOLEAN,
    iep_on_file BOOLEAN, -- Individualized Education Program
    section_504_plan BOOLEAN,
    developmental_milestones TEXT,
    vaccination_record TEXT,
    growth_chart_data TEXT,
    nutritional_assessment TEXT,
    behavioral_assessments TEXT,
    child_abuse_screening TEXT,
    mandated_reporter_contacts TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reproductive Health Records
CREATE TABLE reproductive_health (
    reproductive_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    menstrual_history TEXT,
    obstetric_history TEXT,
    gravida INTEGER,
    para INTEGER,
    abortus INTEGER,
    living_children INTEGER,
    contraceptive_history TEXT,
    fertility_treatments TEXT,
    pregnancy_complications TEXT,
    delivery_history TEXT,
    breastfeeding_history TEXT,
    menopause_status VARCHAR(30),
    hormone_replacement_therapy TEXT,
    gynecologic_procedures TEXT,
    pap_smear_history TEXT,
    mammography_history TEXT,
    family_planning_goals TEXT,
    sexually_transmitted_infections TEXT,
    partner_information TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Substance Abuse Treatment Records
CREATE TABLE substance_abuse_records (
    substance_abuse_id VARCHAR(20) PRIMARY KEY,
    patient_guid VARCHAR(36) REFERENCES patient_demographics(patient_guid),
    treatment_episode_id VARCHAR(20),
    admission_date DATE,
    discharge_date DATE,
    treatment_setting VARCHAR(50),
    primary_substance VARCHAR(50),
    secondary_substances TEXT,
    age_first_use INTEGER,
    frequency_of_use TEXT,
    route_of_administration TEXT,
    amount_typically_used TEXT,
    last_use_date DATE,
    withdrawal_symptoms TEXT,
    detoxification_required BOOLEAN,
    detox_medications TEXT,
    treatment_goals TEXT,
    treatment_plan TEXT,
    therapy_sessions_attended INTEGER,
    group_sessions_attended INTEGER,
    individual_counseling_sessions INTEGER,
    family_sessions_attended INTEGER,
    urine_drug_screens TEXT,
    breathalyzer_results TEXT,
    compliance_with_treatment TEXT,
    relapses_during_treatment TEXT,
    discharge_reason VARCHAR(100),
    aftercare_plan TEXT,
    recovery_support_services TEXT,
    sober_living_arrangements TEXT,
    employment_assistance BOOLEAN,
    legal_issues TEXT,
    criminal_justice_involvement TEXT,
    mandated_treatment BOOLEAN,
    confidentiality_42cfr_part2 BOOLEAN,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- HEALTHCARE PROVIDER INFORMATION
-- =============================================================================

-- Healthcare Provider Directory
CREATE TABLE healthcare_providers (
    provider_id VARCHAR(20) PRIMARY KEY,
    npi VARCHAR(10) UNIQUE, -- National Provider Identifier
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    credentials VARCHAR(100),
    specialty_primary VARCHAR(100),
    specialty_secondary VARCHAR(100),
    subspecialties TEXT,
    dea_number VARCHAR(15),
    medical_license_number VARCHAR(20),
    medical_license_state VARCHAR(20),
    medical_license_expiration DATE,
    board_certifications TEXT,
    medical_school VARCHAR(100),
    graduation_year INTEGER,
    residency_training TEXT,
    fellowship_training TEXT,
    practice_name VARCHAR(100),
    practice_address TEXT,
    practice_phone VARCHAR(15),
    practice_fax VARCHAR(15),
    office_hours TEXT,
    hospital_affiliations TEXT,
    insurance_accepted TEXT,
    languages_spoken TEXT,
    telemedicine_services BOOLEAN,
    emergency_contact_info TEXT,
    malpractice_insurance TEXT,
    background_check_date DATE,
    drug_screening_date DATE,
    quality_measures TEXT,
    patient_satisfaction_scores TEXT,
    peer_reviews TEXT,
    continuing_education_credits INTEGER,
    professional_memberships TEXT,
    research_interests TEXT,
    publications TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR HEALTHCARE PERFORMANCE
-- =============================================================================

-- Patient Demographics Indexes
CREATE INDEX idx_patient_demographics_mrn ON patient_demographics(mrn);
CREATE INDEX idx_patient_demographics_ssn ON patient_demographics(ssn);
CREATE INDEX idx_patient_demographics_dob ON patient_demographics(date_of_birth);
CREATE INDEX idx_patient_demographics_last_name ON patient_demographics(last_name);
CREATE INDEX idx_patient_demographics_phone ON patient_demographics(home_phone);

-- Clinical Encounter Indexes
CREATE INDEX idx_clinical_encounters_patient ON clinical_encounters(patient_guid);
CREATE INDEX idx_clinical_encounters_date ON clinical_encounters(admission_date);
CREATE INDEX idx_clinical_encounters_physician ON clinical_encounters(attending_physician_npi);

-- Lab Results Indexes
CREATE INDEX idx_lab_results_patient ON laboratory_results(patient_guid);
CREATE INDEX idx_lab_results_date ON laboratory_results(collection_date);
CREATE INDEX idx_lab_results_critical ON laboratory_results(critical_value_flag);

-- Medication Indexes
CREATE INDEX idx_medication_patient ON medication_administration(patient_guid);
CREATE INDEX idx_medication_prescriber ON medication_administration(prescribing_physician_npi);
CREATE INDEX idx_medication_drug ON medication_administration(medication_name);

-- Provider Indexes
CREATE INDEX idx_providers_npi ON healthcare_providers(npi);
CREATE INDEX idx_providers_dea ON healthcare_providers(dea_number);
CREATE INDEX idx_providers_specialty ON healthcare_providers(specialty_primary);

-- =============================================================================
-- VIEWS FOR HEALTHCARE REPORTING
-- =============================================================================

-- Patient Summary View with All PHI
CREATE VIEW patient_phi_summary AS
SELECT 
    pd.patient_guid,
    pd.mrn,
    CASE WHEN pd.ssn IS NOT NULL THEN 'SSN_PRESENT' ELSE 'SSN_MISSING' END as ssn_status,
    CASE WHEN pd.medicare_number IS NOT NULL THEN 'MEDICARE_PRESENT' ELSE 'MEDICARE_MISSING' END as medicare_status,
    CASE WHEN pd.email_personal IS NOT NULL THEN 'EMAIL_PRESENT' ELSE 'EMAIL_MISSING' END as email_status,
    COUNT(ce.encounter_id) as total_encounters,
    COUNT(lr.lab_result_id) as total_lab_results,
    COUNT(ma.med_admin_id) as total_medications
FROM patient_demographics pd
LEFT JOIN clinical_encounters ce ON pd.patient_guid = ce.patient_guid
LEFT JOIN laboratory_results lr ON pd.patient_guid = lr.patient_guid
LEFT JOIN medication_administration ma ON pd.patient_guid = ma.patient_guid
GROUP BY pd.patient_guid, pd.mrn, pd.ssn, pd.medicare_number, pd.email_personal;

-- Healthcare Provider PHI Summary
CREATE VIEW provider_phi_summary AS
SELECT 
    provider_id,
    npi,
    CASE WHEN dea_number IS NOT NULL THEN 'DEA_PRESENT' ELSE 'DEA_MISSING' END as dea_status,
    CASE WHEN medical_license_number IS NOT NULL THEN 'LICENSE_PRESENT' ELSE 'LICENSE_MISSING' END as license_status,
    specialty_primary,
    practice_name
FROM healthcare_providers;

-- =============================================================================
-- COMMENTS FOR HEALTHCARE PHI IDENTIFICATION
-- =============================================================================

-- Table Comments
COMMENT ON TABLE patient_demographics IS 'Comprehensive patient demographics with extensive PHI under HIPAA';
COMMENT ON TABLE clinical_encounters IS 'Clinical encounter records with detailed treatment information';
COMMENT ON TABLE laboratory_results IS 'Laboratory test results with sensitive health information';
COMMENT ON TABLE medication_administration IS 'Medication records with prescriber and patient details';
COMMENT ON TABLE genetic_testing IS 'Genetic testing results - highly sensitive PHI';
COMMENT ON TABLE mental_health_records IS 'Mental health treatment records with special confidentiality';
COMMENT ON TABLE substance_abuse_records IS 'Substance abuse treatment protected under 42 CFR Part 2';

-- Key PHI Column Comments
COMMENT ON COLUMN patient_demographics.mrn IS 'Medical Record Number - PHI Identifier under HIPAA';
COMMENT ON COLUMN patient_demographics.ssn IS 'Social Security Number - PHI under HIPAA';
COMMENT ON COLUMN patient_demographics.medicare_number IS 'Medicare Beneficiary Identifier - PHI';
COMMENT ON COLUMN healthcare_providers.npi IS 'National Provider Identifier - Healthcare Provider ID';
COMMENT ON COLUMN healthcare_providers.dea_number IS 'DEA Registration Number - Controlled Substance Prescriber ID';
COMMENT ON COLUMN genetic_testing.test_results IS 'Genetic Test Results - Highly Sensitive PHI';
COMMENT ON COLUMN mental_health_records.session_notes IS 'Mental Health Session Notes - Protected PHI';
COMMENT ON COLUMN substance_abuse_records.treatment_plan IS 'Substance Abuse Treatment Plan - 42 CFR Part 2 Protected';
