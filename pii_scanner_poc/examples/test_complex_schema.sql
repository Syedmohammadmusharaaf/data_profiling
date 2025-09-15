-- Complex schema - Enterprise fields with domain-specific terminology
CREATE TABLE healthcare_providers (
    provider_npi BIGINT PRIMARY KEY,
    provider_taxonomy_code VARCHAR(20),
    organization_name VARCHAR(200),
    authorized_official_first_name VARCHAR(50),
    authorized_official_last_name VARCHAR(50),
    authorized_official_telephone_number VARCHAR(20),
    healthcare_provider_primary_taxonomy_switch CHAR(1),
    provider_enumeration_date DATE,
    last_update_date DATE
);

CREATE TABLE clinical_data (
    encounter_id UUID PRIMARY KEY,
    patient_mrn VARCHAR(50),
    provider_npi BIGINT,
    diagnosis_codes TEXT,
    procedure_codes TEXT,
    clinical_notes TEXT,
    protected_health_information TEXT,
    phi_access_log TEXT,
    treatment_authorization_code VARCHAR(100)
);

CREATE TABLE financial_instruments (
    instrument_id UUID PRIMARY KEY,
    cusip_identifier VARCHAR(9),
    isin_code VARCHAR(12),
    security_master_id VARCHAR(50),
    counterparty_legal_entity_identifier VARCHAR(20),
    swap_data_repository_id VARCHAR(50),
    regulatory_reporting_jurisdiction VARCHAR(10),
    prudential_valuation_adjustment DECIMAL(15,4)
);
