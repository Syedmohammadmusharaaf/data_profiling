-- Edge Cases DDL for PII/PHI Scanner POC
-- Complex and unusual scenarios to test pattern recognition limits
-- Purpose: Testing edge case detection and handling of ambiguous data
-- Coverage: International formats, legacy systems, unusual patterns

-- =============================================================================
-- INTERNATIONAL AND MULTI-CULTURAL DATA PATTERNS
-- =============================================================================

-- International Customer Database with Global PII Variations
CREATE TABLE international_customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    
    -- Multiple Name Formats and Cultural Variations
    family_name_primary VARCHAR(100), -- Asian surname-first format
    given_name_primary VARCHAR(100),
    family_name_secondary VARCHAR(100), -- Multiple family names (Hispanic)
    given_name_secondary VARCHAR(100),
    patronymic_name VARCHAR(100), -- Russian/Slavic patronymic
    matronymic_name VARCHAR(100), -- Icelandic matronymic
    tribal_name VARCHAR(100), -- Indigenous/tribal identification
    clan_name VARCHAR(100), -- Scottish/Celtic clan names
    nobility_title VARCHAR(50), -- von, de, du, etc.
    religious_title VARCHAR(50), -- Rabbi, Imam, Pastor, etc.
    professional_title VARCHAR(50), -- Dr., Prof., Eng., etc.
    name_prefix VARCHAR(20), -- Mr., Mrs., Ms., Dr., etc.
    name_suffix VARCHAR(20), -- Jr., Sr., III, PhD, etc.
    romanized_name VARCHAR(200), -- For non-Latin scripts
    native_script_name NVARCHAR(200), -- Original script (Cyrillic, Arabic, etc.)
    pronunciation_guide VARCHAR(200), -- Phonetic spelling
    preferred_salutation VARCHAR(100), -- How customer prefers to be addressed
    
    -- International Date Formats and Calendar Systems
    birth_date_gregorian DATE, -- Standard Gregorian calendar
    birth_date_islamic VARCHAR(20), -- Hijri calendar
    birth_date_hebrew VARCHAR(20), -- Hebrew calendar
    birth_date_chinese VARCHAR(20), -- Chinese calendar
    birth_date_buddhist VARCHAR(20), -- Buddhist calendar
    birth_date_text VARCHAR(50), -- "circa 1985", "late spring 1990"
    birth_year_only INTEGER, -- When exact date unknown
    birth_decade VARCHAR(10), -- "1980s" for privacy
    
    -- International Identification Numbers
    passport_primary_number VARCHAR(20),
    passport_primary_country CHAR(3), -- ISO 3166-1 alpha-3
    passport_secondary_number VARCHAR(20), -- Dual citizenship
    passport_secondary_country CHAR(3),
    national_id_eu VARCHAR(30), -- European national ID variations
    national_id_asia VARCHAR(30), -- Asian national ID variations
    national_id_africa VARCHAR(30), -- African national ID variations
    social_insurance_canada VARCHAR(15), -- SIN format: XXX-XXX-XXX
    national_insurance_uk VARCHAR(15), -- NINO format: XX XX XX XX X
    codice_fiscale_italy VARCHAR(20), -- Italian tax code
    dni_spain VARCHAR(15), -- Spanish DNI
    cpf_brazil VARCHAR(15), -- Brazilian CPF: XXX.XXX.XXX-XX
    rut_chile VARCHAR(15), -- Chilean RUT
    curp_mexico VARCHAR(20), -- Mexican CURP
    aadhaar_india VARCHAR(15), -- Indian Aadhaar: XXXX XXXX XXXX
    pan_india VARCHAR(15), -- Indian PAN: XXXXX9999X
    mynumber_japan VARCHAR(15), -- Japanese My Number
    jumin_korea VARCHAR(15), -- Korean Jumin registration number
    hkid_hongkong VARCHAR(15), -- Hong Kong ID
    fin_singapore VARCHAR(15), -- Singapore FIN
    tfn_australia VARCHAR(15), -- Australian Tax File Number
    
    -- International Address Formats
    address_line1_local NVARCHAR(200), -- Local script/language
    address_line2_local NVARCHAR(200),
    address_line3_local NVARCHAR(200),
    address_line1_english VARCHAR(200), -- English transliteration
    address_line2_english VARCHAR(200),
    postal_code_variant1 VARCHAR(20), -- Different postal code formats
    postal_code_variant2 VARCHAR(20),
    administrative_division1 VARCHAR(100), -- State/Province/Region
    administrative_division2 VARCHAR(100), -- County/Prefecture/Oblast
    administrative_division3 VARCHAR(100), -- District/Canton
    country_name_local NVARCHAR(100), -- Local language country name
    country_code_iso2 CHAR(2), -- ISO 3166-1 alpha-2
    country_code_iso3 CHAR(3), -- ISO 3166-1 alpha-3
    country_code_numeric CHAR(3), -- ISO 3166-1 numeric
    
    -- International Phone Number Variations
    phone_primary_e164 VARCHAR(20), -- E.164 format: +1234567890
    phone_primary_national VARCHAR(20), -- National format: (123) 456-7890
    phone_primary_local VARCHAR(20), -- Local format: 123-456-7890
    phone_mobile_international VARCHAR(20),
    phone_work_extension VARCHAR(10), -- Work phone extension
    phone_fax_international VARCHAR(20),
    voip_number VARCHAR(30), -- VoIP/Skype numbers
    satellite_phone VARCHAR(20), -- Satellite phone numbers
    
    -- Cultural and Religious Information
    ethnicity_primary VARCHAR(50),
    ethnicity_secondary VARCHAR(50),
    ethnicity_detailed TEXT, -- Complex multi-ethnic backgrounds
    country_of_birth VARCHAR(50),
    region_of_origin VARCHAR(100), -- More specific than country
    indigenous_group VARCHAR(100),
    caste_system_classification VARCHAR(100), -- South Asian caste
    tribal_affiliation VARCHAR(100),
    religious_affiliation VARCHAR(50),
    religious_sect VARCHAR(100),
    religious_dietary_restrictions TEXT,
    cultural_dietary_restrictions TEXT,
    language_primary VARCHAR(30),
    language_secondary VARCHAR(30),
    language_tertiary VARCHAR(30),
    script_preference VARCHAR(30), -- Latin, Cyrillic, Arabic, etc.
    
    -- Complex Family Relationships
    spouse_name_1 VARCHAR(100), -- Primary spouse
    spouse_name_2 VARCHAR(100), -- Polygamous marriage
    spouse_name_3 VARCHAR(100),
    ex_spouse_names TEXT, -- Multiple previous marriages
    domestic_partner_name VARCHAR(100),
    guardian_name VARCHAR(100), -- For minors
    ward_names TEXT, -- If customer is guardian
    power_of_attorney_name VARCHAR(100),
    next_of_kin_primary VARCHAR(100),
    next_of_kin_secondary VARCHAR(100),
    emergency_contact_international VARCHAR(100),
    emergency_contact_local VARCHAR(100),
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- LEGACY SYSTEM DATA WITH UNUSUAL FORMATS
-- =============================================================================

-- Legacy Mainframe Data Patterns
CREATE TABLE legacy_mainframe_data (
    record_id VARCHAR(20) PRIMARY KEY,
    
    -- Fixed-width legacy formats
    ssn_no_dashes CHAR(9), -- 123456789 (no formatting)
    ssn_with_spaces CHAR(11), -- 123 45 6789 (space delimited)
    ssn_asterisk_format CHAR(11), -- 123*45*6789 (asterisk delimited)
    ssn_period_format CHAR(11), -- 123.45.6789 (period delimited)
    
    -- Legacy date formats
    date_julian_format CHAR(7), -- YYDDD (Julian date)
    date_yymmdd CHAR(6), -- YYMMDD format
    date_ddmmyy CHAR(6), -- DDMMYY format
    date_mmddyy CHAR(6), -- MMDDYY format
    date_cymd CHAR(8), -- CYMD format (C=century)
    date_packed_decimal CHAR(4), -- Packed decimal date
    
    -- EBCDIC encoded fields (represented as VARCHAR for database compatibility)
    name_ebcdic VARCHAR(50), -- EBCDIC encoded name
    address_ebcdic VARCHAR(100), -- EBCDIC encoded address
    
    -- Mainframe numeric formats
    salary_packed_decimal CHAR(8), -- Packed decimal salary
    balance_zoned_decimal CHAR(12), -- Zoned decimal balance
    account_number_ebcdic CHAR(10), -- EBCDIC account number
    
    -- Legacy phone formats
    phone_7digit CHAR(7), -- 5551234 (local only)
    phone_10digit CHAR(10), -- 5555551234 (no formatting)
    phone_parentheses CHAR(14), -- (555) 555-1234
    phone_dots CHAR(12), -- 555.555.1234
    phone_spaces CHAR(12), -- 555 555 1234
    
    -- Legacy ID formats
    employee_id_alpha CHAR(8), -- EMP00123 (alpha prefix)
    customer_id_numeric CHAR(10), -- 0000123456 (zero padded)
    account_type_code CHAR(3), -- CHK, SAV, LON, etc.
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- AMBIGUOUS DATA PATTERNS AND EDGE CASES
-- =============================================================================

-- Ambiguous and Problematic Data Patterns
CREATE TABLE ambiguous_data_patterns (
    pattern_id VARCHAR(20) PRIMARY KEY,
    
    -- Numbers that could be SSN, phone, account numbers, etc.
    nine_digit_number1 VARCHAR(9), -- Could be SSN: 123456789
    nine_digit_number2 VARCHAR(9), -- Could be routing: 021000021
    ten_digit_number1 VARCHAR(10), -- Could be phone: 5551234567
    ten_digit_number2 VARCHAR(10), -- Could be account: 1234567890
    eleven_digit_number VARCHAR(11), -- Could be SSN with formatting
    sixteen_digit_number VARCHAR(16), -- Could be credit card or account
    
    -- Formatted numbers with multiple interpretations
    formatted_number_dashes VARCHAR(15), -- 123-45-6789 or 123-456-7890
    formatted_number_periods VARCHAR(15), -- 123.45.6789 or 123.456.7890
    formatted_number_spaces VARCHAR(15), -- 123 45 6789 or 123 456 7890
    formatted_number_mixed VARCHAR(20), -- (123) 456-7890 or similar
    
    -- Names that could be confused with other data
    numeric_name VARCHAR(50), -- Names like "Seven Johnson" or "Eleven Smith"
    company_name_person_like VARCHAR(100), -- "Johnson & Associates"
    person_name_company_like VARCHAR(100), -- "John McDonald Corp"
    
    -- Addresses with unusual patterns
    po_box_variations VARCHAR(100), -- P.O. Box, PO Box, Post Office Box
    military_address VARCHAR(200), -- APO, FPO, DPO addresses
    rural_route_address VARCHAR(200), -- Rural Route, RR, HC, Star Route
    international_address_us_format VARCHAR(200), -- Foreign address in US format
    
    -- Email patterns that could be confused
    email_all_numbers VARCHAR(100), -- 1234567890@example.com
    email_ssn_like VARCHAR(100), -- 123456789@company.com
    email_phone_like VARCHAR(100), -- 5551234567@domain.com
    email_with_plus VARCHAR(100), -- user+123456789@example.com
    
    -- Mixed language and character sets
    name_mixed_scripts NVARCHAR(100), -- Names with mixed scripts
    address_mixed_languages NVARCHAR(200), -- Addresses in multiple languages
    transliterated_data VARCHAR(200), -- Romanized from other scripts
    
    -- Partial or incomplete data
    name_initials_only VARCHAR(10), -- J. R. Smith
    partial_ssn VARCHAR(20), -- XXX-XX-1234 or ending in digits only
    partial_phone VARCHAR(20), -- XXX-XXX-1234 or (XXX) XXX-1234
    partial_account VARCHAR(20), -- XXXX-XXXX-XXXX-1234
    
    -- Test data patterns that could be mistaken for real PII
    test_ssn_patterns VARCHAR(11), -- 999-99-9999, 000-00-0000
    sequential_numbers VARCHAR(11), -- 123-45-6789, 111-22-3333
    dummy_email_patterns VARCHAR(100), -- test@test.com, example@example.com
    placeholder_names VARCHAR(100), -- John Doe, Jane Smith, Test User
    
    -- Unusual but valid patterns
    single_letter_names VARCHAR(50), -- Names like "X Æ A-XII"
    hyphenated_surnames VARCHAR(100), -- Smith-Johnson-Williams
    apostrophe_names VARCHAR(100), -- O'Connor, D'Angelo
    accent_names NVARCHAR(100), -- José, François, Müller
    
    -- Business vs. Personal ambiguity
    sole_proprietor_name VARCHAR(100), -- Could be person or business
    dba_name_personal VARCHAR(100), -- "John Smith DBA JS Consulting"
    family_business_name VARCHAR(100), -- "Smith Family Trust"
    
    -- Date ambiguity
    ambiguous_date_format VARCHAR(10), -- 01/02/03 (could be any date)
    european_vs_us_date VARCHAR(10), -- 12/01/2023 (Dec 1 or Jan 12?)
    day_month_confusion VARCHAR(10), -- 13/12/2023 vs 12/13/2023
    
    -- Time zone and international considerations
    timestamp_no_timezone TIMESTAMP, -- Ambiguous time zone
    timestamp_multiple_formats VARCHAR(30), -- Various timestamp formats
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- FALSE POSITIVE GENERATORS
-- =============================================================================

-- Data Designed to Generate False Positives in PII Detection
CREATE TABLE false_positive_generators (
    generator_id VARCHAR(20) PRIMARY KEY,
    
    -- Numbers that look like SSNs but aren't
    product_code_ssn_format VARCHAR(11), -- 123-45-6789 product code
    batch_number_ssn_format VARCHAR(11), -- Manufacturing batch number
    reference_number_ssn_format VARCHAR(11), -- Internal reference number
    invoice_number_ssn_format VARCHAR(11), -- Invoice number format
    
    -- Numbers that look like credit cards but aren't
    isbn_16_digits VARCHAR(16), -- ISBN that's 16 digits
    upc_16_digits VARCHAR(16), -- UPC/barcode number
    tracking_number_16_digits VARCHAR(16), -- Package tracking number
    serial_number_16_digits VARCHAR(16), -- Product serial number
    
    -- Strings that look like names but aren't
    product_name_person_like VARCHAR(100), -- "Johnson Controls Panel"
    street_name_person_like VARCHAR(100), -- "Smith Street" or "Johnson Avenue"
    software_name_person_like VARCHAR(100), -- "Anderson Analytics Software"
    
    -- Geographic coordinates that could be confused with other numbers
    latitude_coordinate DECIMAL(10,8), -- 40.7128° N (NYC latitude)
    longitude_coordinate DECIMAL(11,8), -- -74.0060° W (NYC longitude)
    gps_coordinate_string VARCHAR(30), -- "40.7128, -74.0060"
    
    -- Scientific and technical numbers
    chemical_formula VARCHAR(50), -- Chemical formulas with numbers
    mathematical_constant VARCHAR(20), -- π, e, φ values
    scientific_notation VARCHAR(20), -- 1.23E+10 format
    
    -- Financial data that's not PII
    stock_ticker_numeric VARCHAR(10), -- Numeric stock symbols
    currency_amount_formatted VARCHAR(20), -- $123,456.78
    percentage_formatted VARCHAR(10), -- 12.34%
    
    -- System-generated data
    uuid_format VARCHAR(36), -- UUID: 123e4567-e89b-12d3-a456-426614174000
    hash_value VARCHAR(64), -- SHA-256 hash
    mac_address VARCHAR(17), -- MAC address: 00:1B:44:11:3A:B7
    ip_address_v4 VARCHAR(15), -- IPv4: 192.168.1.1
    ip_address_v6 VARCHAR(39), -- IPv6: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    
    -- Measurement and sensor data
    temperature_reading DECIMAL(5,2), -- Temperature sensor reading
    pressure_reading DECIMAL(8,3), -- Pressure sensor reading
    voltage_reading DECIMAL(6,3), -- Electrical voltage reading
    frequency_reading DECIMAL(8,2), -- Radio frequency reading
    
    -- Time-based data that could be confused
    timestamp_epoch BIGINT, -- Unix timestamp
    duration_seconds INTEGER, -- Duration in seconds
    elapsed_time_formatted VARCHAR(20), -- HH:MM:SS format
    
    -- Encoded or encrypted data
    base64_encoded_string TEXT, -- Base64 encoded data
    encoded_reference VARCHAR(100), -- Encoded reference numbers
    encrypted_field_sample TEXT, -- Sample encrypted data
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- SYNTHETIC DATA VARIATIONS
-- =============================================================================

-- Synthetic and Generated Data Patterns
CREATE TABLE synthetic_data_variations (
    synthetic_id VARCHAR(20) PRIMARY KEY,
    
    -- AI-generated names (realistic but not real people)
    ai_generated_first_name VARCHAR(50),
    ai_generated_last_name VARCHAR(50),
    ai_generated_full_name VARCHAR(100),
    
    -- Synthetic SSNs (following valid format but not assigned)
    synthetic_ssn_valid_format VARCHAR(11), -- Valid format, unassigned number
    synthetic_ssn_test_range VARCHAR(11), -- Test SSN range (900-999)
    
    -- Generated addresses (realistic but non-existent)
    synthetic_street_address VARCHAR(200),
    synthetic_city_state VARCHAR(100),
    synthetic_zip_code VARCHAR(10),
    
    -- Fictional company names
    synthetic_company_name VARCHAR(200),
    synthetic_business_address VARCHAR(200),
    
    -- Generated phone numbers (valid format, non-working)
    synthetic_phone_555_prefix VARCHAR(12), -- 555-0100 to 555-0199 range
    synthetic_international_phone VARCHAR(20),
    
    -- Mock email addresses
    synthetic_email_address VARCHAR(100),
    synthetic_business_email VARCHAR(100),
    
    -- Generated financial data
    synthetic_account_number VARCHAR(20),
    synthetic_routing_number VARCHAR(9),
    synthetic_credit_card_number VARCHAR(16), -- Valid Luhn algorithm, not real
    
    -- Pseudonymized data
    pseudonym_first_name VARCHAR(50), -- Consistently pseudonymized
    pseudonym_last_name VARCHAR(50),
    pseudonym_id_number VARCHAR(20),
    
    -- Anonymized patterns
    anonymized_age_range VARCHAR(20), -- "25-35" instead of exact age
    anonymized_location VARCHAR(100), -- "Northeast Region" instead of address
    anonymized_income_bracket VARCHAR(30), -- "$50K-$75K" instead of exact
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- CULTURAL AND RELIGIOUS DATA VARIATIONS
-- =============================================================================

-- Religious and Cultural Data Patterns
CREATE TABLE religious_cultural_data (
    cultural_id VARCHAR(20) PRIMARY KEY,
    
    -- Religious names and titles
    religious_first_name VARCHAR(100), -- Muhammad, Moses, Jesus, Buddha variants
    religious_last_name VARCHAR(100), -- Names derived from religious terms
    religious_title VARCHAR(50), -- Father, Sister, Rabbi, Imam, etc.
    
    -- Cultural naming conventions
    patronymic_surname VARCHAR(100), -- -son, -sen, -ovich endings
    matronymic_surname VARCHAR(100), -- -daughter, -dottir endings
    generational_suffix VARCHAR(20), -- Jr., Sr., III, IV, etc.
    tribal_clan_name VARCHAR(100), -- Scottish, Irish, Native American clans
    
    -- Calendar and date variations
    lunar_calendar_date VARCHAR(30), -- Islamic, Hebrew calendar dates
    festival_reference_date VARCHAR(50), -- "3rd day after Diwali"
    seasonal_date_reference VARCHAR(50), -- "Harvest season 2023"
    
    -- Cultural address patterns
    village_compound_address TEXT, -- Traditional village addressing
    ancestral_home_reference VARCHAR(200), -- "House of [Family Name]"
    monastery_ashram_address VARCHAR(200), -- Religious institution addresses
    
    -- Religious dietary and lifestyle codes
    halal_certification_codes VARCHAR(50), -- Islamic dietary codes
    kosher_certification_codes VARCHAR(50), -- Jewish dietary codes
    vegetarian_type_codes VARCHAR(30), -- Jain, Hindu, Buddhist variations
    
    -- Cultural relationship terms
    godparent_information VARCHAR(100), -- Godfather, Godmother
    cultural_mentor_elder VARCHAR(100), -- Traditional mentorship roles
    extended_family_roles TEXT, -- Complex family relationship terms
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- GOVERNMENT AND INSTITUTIONAL EDGE CASES
-- =============================================================================

-- Government and Institutional Data Edge Cases
CREATE TABLE government_institutional_data (
    institutional_id VARCHAR(20) PRIMARY KEY,
    
    -- Military service data
    military_service_number VARCHAR(20), -- Various military ID formats
    veteran_id_number VARCHAR(20), -- VA identification numbers
    security_clearance_level VARCHAR(50), -- Classified clearance information
    military_unit_designation VARCHAR(100), -- Unit and deployment information
    
    -- Diplomatic and international service
    diplomatic_passport_number VARCHAR(20), -- Diplomatic passport IDs
    consular_registration VARCHAR(30), -- Consular services registration
    embassy_staff_id VARCHAR(20), -- Embassy employee identification
    
    -- Academic and research institutions
    student_id_variations VARCHAR(20), -- Various student ID formats
    faculty_id_number VARCHAR(20), -- Academic employee IDs
    research_participant_id VARCHAR(20), -- Research study participant IDs
    library_card_numbers VARCHAR(20), -- Academic library systems
    
    -- Healthcare institution variations
    patient_mrn_variations VARCHAR(20), -- Medical record number variations
    provider_npi_variations VARCHAR(10), -- National Provider Identifier
    insurance_group_numbers VARCHAR(50), -- Group insurance identifiers
    
    -- Legal system identifiers
    court_case_numbers VARCHAR(30), -- Various court case number formats
    legal_document_numbers VARCHAR(30), -- Legal filing numbers
    attorney_bar_numbers VARCHAR(20), -- State bar association numbers
    
    -- Immigration and naturalization
    visa_number_variations VARCHAR(30), -- Various visa number formats
    green_card_numbers VARCHAR(20), -- Permanent resident card numbers
    naturalization_certificate VARCHAR(30), -- Citizenship certificate numbers
    
    -- Professional licensing
    professional_license_numbers TEXT, -- Various professional licenses
    certification_numbers TEXT, -- Professional certifications
    registration_numbers TEXT, -- Professional registration numbers
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TECHNOLOGY AND DIGITAL IDENTITY EDGE CASES
-- =============================================================================

-- Digital Identity and Technology Edge Cases
CREATE TABLE digital_identity_data (
    digital_id VARCHAR(20) PRIMARY KEY,
    
    -- Cryptocurrency and blockchain
    bitcoin_address VARCHAR(35), -- Bitcoin wallet addresses
    ethereum_address VARCHAR(42), -- Ethereum wallet addresses
    blockchain_transaction_hash VARCHAR(66), -- Transaction hashes
    smart_contract_address VARCHAR(42), -- Smart contract addresses
    
    -- Digital certificates and keys
    ssl_certificate_fingerprint VARCHAR(64), -- SSL certificate fingerprints
    gpg_key_fingerprint VARCHAR(40), -- GPG key fingerprints
    ssh_key_fingerprint VARCHAR(47), -- SSH key fingerprints
    api_key_samples VARCHAR(100), -- API key formats (non-functional)
    
    -- Gaming and virtual worlds
    gaming_user_ids VARCHAR(50), -- Gaming platform user IDs
    virtual_world_avatars VARCHAR(100), -- Virtual world character names
    nft_token_ids VARCHAR(100), -- Non-fungible token identifiers
    
    -- Social media and platforms
    social_media_handles VARCHAR(100), -- @username variations
    platform_user_ids VARCHAR(50), -- Numeric user IDs from platforms
    vanity_urls VARCHAR(200), -- Custom URL patterns
    
    -- IoT and device identifiers
    device_serial_numbers VARCHAR(50), -- IoT device serial numbers
    rfid_tag_numbers VARCHAR(30), -- RFID tag identifiers
    nfc_chip_ids VARCHAR(30), -- NFC chip identifiers
    bluetooth_mac_addresses VARCHAR(17), -- Bluetooth device addresses
    
    -- Biometric template references
    fingerprint_template_ids VARCHAR(50), -- Biometric template IDs
    facial_recognition_ids VARCHAR(50), -- Facial template IDs
    iris_scan_reference_ids VARCHAR(50), -- Iris biometric IDs
    voice_print_ids VARCHAR(50), -- Voice recognition template IDs
    
    -- Digital asset identifiers
    domain_name_registrations VARCHAR(200), -- Domain name ownership
    digital_certificate_serial VARCHAR(50), -- Certificate serial numbers
    software_license_keys VARCHAR(100), -- Software license patterns
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR EDGE CASE PERFORMANCE
-- =============================================================================

-- International Data Indexes
CREATE INDEX idx_intl_customers_passport ON international_customers(passport_primary_number);
CREATE INDEX idx_intl_customers_national_id ON international_customers(national_id_eu);
CREATE INDEX idx_intl_customers_romanized_name ON international_customers(romanized_name);

-- Legacy Data Indexes
CREATE INDEX idx_legacy_ssn_no_dashes ON legacy_mainframe_data(ssn_no_dashes);
CREATE INDEX idx_legacy_phone_10digit ON legacy_mainframe_data(phone_10digit);

-- Ambiguous Pattern Indexes
CREATE INDEX idx_ambiguous_nine_digit ON ambiguous_data_patterns(nine_digit_number1);
CREATE INDEX idx_ambiguous_sixteen_digit ON ambiguous_data_patterns(sixteen_digit_number);

-- Synthetic Data Indexes
CREATE INDEX idx_synthetic_ssn ON synthetic_data_variations(synthetic_ssn_valid_format);
CREATE INDEX idx_synthetic_email ON synthetic_data_variations(synthetic_email_address);

-- =============================================================================
-- VIEWS FOR EDGE CASE ANALYSIS
-- =============================================================================

-- International PII Complexity View
CREATE VIEW international_pii_complexity AS
SELECT 
    customer_id,
    CASE 
        WHEN passport_primary_number IS NOT NULL AND passport_secondary_number IS NOT NULL 
        THEN 'DUAL_PASSPORT' 
        ELSE 'SINGLE_PASSPORT' 
    END as passport_complexity,
    CASE 
        WHEN national_id_eu IS NOT NULL OR national_id_asia IS NOT NULL OR national_id_africa IS NOT NULL 
        THEN 'NATIONAL_ID_PRESENT' 
        ELSE 'NATIONAL_ID_MISSING' 
    END as national_id_status,
    CASE 
        WHEN native_script_name IS NOT NULL 
        THEN 'NON_LATIN_SCRIPT' 
        ELSE 'LATIN_SCRIPT' 
    END as script_complexity
FROM international_customers;

-- =============================================================================
-- COMMENTS FOR EDGE CASE IDENTIFICATION
-- =============================================================================

-- Table Comments
COMMENT ON TABLE international_customers IS 'International customer data with complex global PII patterns';
COMMENT ON TABLE legacy_mainframe_data IS 'Legacy system data with unusual formatting and edge cases';
COMMENT ON TABLE ambiguous_data_patterns IS 'Ambiguous data patterns that could be misclassified';
COMMENT ON TABLE false_positive_generators IS 'Data designed to test false positive detection';
COMMENT ON TABLE synthetic_data_variations IS 'Synthetic and generated data patterns for testing';

-- Key Edge Case Column Comments
COMMENT ON COLUMN international_customers.aadhaar_india IS 'Indian Aadhaar Number - 12-digit unique identity';
COMMENT ON COLUMN international_customers.cpf_brazil IS 'Brazilian CPF - Cadastro de Pessoas Físicas';
COMMENT ON COLUMN legacy_mainframe_data.ssn_no_dashes IS 'Legacy SSN format without dashes - edge case';
COMMENT ON COLUMN ambiguous_data_patterns.nine_digit_number1 IS 'Ambiguous 9-digit number - could be SSN or other';
COMMENT ON COLUMN false_positive_generators.product_code_ssn_format IS 'Product code in SSN format - false positive test';
