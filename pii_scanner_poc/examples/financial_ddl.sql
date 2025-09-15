    -- Financial Services DDL for PII/PHI Scanner POC
-- Specialized financial industry scenarios with complex PII patterns
-- Purpose: Testing financial-specific PII detection
-- Compliance: PCI DSS, SOX, GDPR, CCPA, GLBA

-- =============================================================================
-- BANKING & RETAIL FINANCIAL SERVICES
-- =============================================================================

-- Customer Master Data for Banking
CREATE TABLE bank_customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_number VARCHAR(16) UNIQUE NOT NULL,
    ssn VARCHAR(11) UNIQUE, -- Social Security Number
    itin VARCHAR(11), -- Individual Taxpayer Identification Number
    ein VARCHAR(10), -- Employer Identification Number
    legal_first_name VARCHAR(50) NOT NULL,
    legal_last_name VARCHAR(50) NOT NULL,
    legal_middle_name VARCHAR(50),
    preferred_first_name VARCHAR(50),
    name_suffix VARCHAR(10),
    maiden_name VARCHAR(50),
    date_of_birth DATE,
    place_of_birth VARCHAR(100),
    citizenship_status VARCHAR(30),
    country_of_citizenship VARCHAR(50),
    passport_number VARCHAR(15),
    passport_country VARCHAR(50),
    passport_expiration_date DATE,
    drivers_license_number VARCHAR(20),
    drivers_license_state VARCHAR(20),
    drivers_license_expiration DATE,
    state_id_number VARCHAR(20),
    military_id_number VARCHAR(20),
    gender CHAR(1),
    marital_status VARCHAR(20),
    number_of_dependents INTEGER,
    primary_language VARCHAR(30),
    residential_address_line1 VARCHAR(100),
    residential_address_line2 VARCHAR(100),
    residential_city VARCHAR(50),
    residential_state VARCHAR(20),
    residential_zip_code VARCHAR(10),
    residential_country VARCHAR(50),
    mailing_address_different BOOLEAN,
    mailing_address TEXT,
    previous_address_1 TEXT,
    previous_address_2 TEXT,
    home_phone VARCHAR(15),
    work_phone VARCHAR(15),
    mobile_phone VARCHAR(15),
    fax_number VARCHAR(15),
    email_primary VARCHAR(100),
    email_secondary VARCHAR(100),
    employer_name VARCHAR(100),
    employer_address TEXT,
    employer_phone VARCHAR(15),
    job_title VARCHAR(100),
    employment_start_date DATE,
    annual_income DECIMAL(12,2),
    other_income_sources TEXT,
    net_worth DECIMAL(15,2),
    liquid_assets DECIMAL(12,2),
    monthly_expenses DECIMAL(10,2),
    housing_status VARCHAR(30), -- Own, Rent, Other
    monthly_housing_payment DECIMAL(8,2),
    emergency_contact_name VARCHAR(100),
    emergency_contact_relationship VARCHAR(30),
    emergency_contact_phone VARCHAR(15),
    emergency_contact_address TEXT,
    next_of_kin_name VARCHAR(100),
    next_of_kin_relationship VARCHAR(30),
    next_of_kin_phone VARCHAR(15),
    beneficiary_information TEXT,
    risk_tolerance VARCHAR(20),
    investment_experience VARCHAR(50),
    investment_objectives TEXT,
    kyc_completion_date DATE, -- Know Your Customer
    kyc_updated_date DATE,
    aml_risk_rating VARCHAR(20), -- Anti-Money Laundering
    aml_last_review_date DATE,
    politically_exposed_person BOOLEAN,
    sanctions_check_status VARCHAR(30),
    sanctions_check_date DATE,
    credit_score INTEGER,
    credit_bureau VARCHAR(50),
    credit_report_date DATE,
    bankruptcy_history TEXT,
    legal_judgments TEXT,
    account_opening_date DATE,
    account_opening_branch VARCHAR(50),
    account_opening_officer VARCHAR(100),
    customer_since_date DATE,
    last_contact_date DATE,
    preferred_contact_method VARCHAR(30),
    marketing_opt_in BOOLEAN,
    privacy_policy_accepted BOOLEAN,
    terms_conditions_accepted BOOLEAN,
    fatca_status VARCHAR(50), -- Foreign Account Tax Compliance Act
    w9_on_file BOOLEAN,
    w8_on_file BOOLEAN,
    backup_withholding_status BOOLEAN,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified_by VARCHAR(100),
    last_modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Checking and Savings Accounts
CREATE TABLE deposit_accounts (
    account_id VARCHAR(20) PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id VARCHAR(20) REFERENCES bank_customers(customer_id),
    account_type VARCHAR(30), -- Checking, Savings, Money Market, CD
    account_subtype VARCHAR(50),
    product_code VARCHAR(20),
    account_title VARCHAR(100),
    ownership_type VARCHAR(30), -- Individual, Joint, Trust, Business
    joint_owner_1_name VARCHAR(100),
    joint_owner_1_ssn VARCHAR(11),
    joint_owner_2_name VARCHAR(100),
    joint_owner_2_ssn VARCHAR(11),
    authorized_signer_1_name VARCHAR(100),
    authorized_signer_1_ssn VARCHAR(11),
    authorized_signer_2_name VARCHAR(100),
    authorized_signer_2_ssn VARCHAR(11),
    trust_name VARCHAR(100),
    trustee_name VARCHAR(100),
    trustee_ssn VARCHAR(11),
    beneficiary_names TEXT,
    pod_beneficiaries TEXT, -- Payable on Death
    account_opening_date DATE,
    account_closing_date DATE,
    account_status VARCHAR(20),
    branch_code VARCHAR(10),
    opening_deposit DECIMAL(12,2),
    current_balance DECIMAL(12,2),
    available_balance DECIMAL(12,2),
    minimum_balance DECIMAL(8,2),
    interest_rate DECIMAL(6,4),
    interest_earned_ytd DECIMAL(8,2),
    overdraft_protection BOOLEAN,
    overdraft_limit DECIMAL(8,2),
    debit_card_issued BOOLEAN,
    debit_card_number VARCHAR(19),
    debit_card_expiration VARCHAR(7),
    atm_pin_set BOOLEAN,
    online_banking_enrolled BOOLEAN,
    mobile_banking_enrolled BOOLEAN,
    paper_statements BOOLEAN,
    electronic_statements BOOLEAN,
    statement_frequency VARCHAR(20),
    last_statement_date DATE,
    dormancy_date DATE,
    escheatment_date DATE,
    routing_number VARCHAR(9),
    swift_code VARCHAR(11),
    iban VARCHAR(34),
    correspondent_bank_info TEXT,
    regulatory_reporting_codes TEXT,
    cra_assessment_area VARCHAR(50), -- Community Reinvestment Act
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Credit Card Accounts and Payment Cards
CREATE TABLE credit_card_accounts (
    card_account_id VARCHAR(20) PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id VARCHAR(20) REFERENCES bank_customers(customer_id),
    primary_cardholder_name VARCHAR(100),
    primary_cardholder_ssn VARCHAR(11),
    card_product_type VARCHAR(50),
    card_network VARCHAR(20), -- Visa, MasterCard, American Express, Discover
    primary_card_number VARCHAR(19), -- PAN (Primary Account Number)
    primary_card_number_encrypted VARCHAR(255),
    primary_card_number_masked VARCHAR(19), -- XXXX-XXXX-XXXX-1234
    primary_card_expiration_date VARCHAR(7), -- MM/YYYY
    primary_card_cvv VARCHAR(4),
    primary_card_issue_date DATE,
    primary_card_activation_date DATE,
    primary_card_status VARCHAR(20),
    additional_card_1_number VARCHAR(19),
    additional_card_1_holder_name VARCHAR(100),
    additional_card_1_holder_relationship VARCHAR(30),
    additional_card_1_expiration VARCHAR(7),
    additional_card_2_number VARCHAR(19),
    additional_card_2_holder_name VARCHAR(100),
    additional_card_2_holder_relationship VARCHAR(30),
    additional_card_2_expiration VARCHAR(7),
    billing_address_line1 VARCHAR(100),
    billing_address_line2 VARCHAR(100),
    billing_city VARCHAR(50),
    billing_state VARCHAR(20),
    billing_zip_code VARCHAR(10),
    billing_country VARCHAR(50),
    credit_limit DECIMAL(10,2),
    cash_advance_limit DECIMAL(8,2),
    current_balance DECIMAL(10,2),
    available_credit DECIMAL(10,2),
    minimum_payment_due DECIMAL(8,2),
    payment_due_date DATE,
    last_payment_amount DECIMAL(8,2),
    last_payment_date DATE,
    purchase_apr DECIMAL(6,4),
    cash_advance_apr DECIMAL(6,4),
    penalty_apr DECIMAL(6,4),
    balance_transfer_apr DECIMAL(6,4),
    annual_fee DECIMAL(6,2),
    late_fee DECIMAL(6,2),
    overlimit_fee DECIMAL(6,2),
    foreign_transaction_fee_percent DECIMAL(4,2),
    rewards_program VARCHAR(50),
    rewards_points_balance INTEGER,
    rewards_cash_back_balance DECIMAL(8,2),
    pin_set BOOLEAN,
    pin_hash VARCHAR(255),
    security_questions TEXT,
    account_opening_date DATE,
    account_closing_date DATE,
    account_closing_reason VARCHAR(100),
    credit_bureau_reporting BOOLEAN,
    fraud_alerts TEXT,
    disputed_transactions TEXT,
    chargebacks TEXT,
    collection_status VARCHAR(30),
    charge_off_date DATE,
    bankruptcy_flag BOOLEAN,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Records for All Account Types
CREATE TABLE financial_transactions (
    transaction_id VARCHAR(25) PRIMARY KEY,
    account_id VARCHAR(20),
    account_number VARCHAR(20),
    transaction_date DATE,
    transaction_time TIME,
    posting_date DATE,
    transaction_type VARCHAR(30),
    transaction_code VARCHAR(10),
    transaction_description TEXT,
    transaction_amount DECIMAL(12,2),
    transaction_currency CHAR(3),
    exchange_rate DECIMAL(10,6),
    usd_amount DECIMAL(12,2),
    debit_credit_indicator CHAR(1), -- D or C
    running_balance DECIMAL(12,2),
    merchant_name VARCHAR(100),
    merchant_category_code VARCHAR(4),
    merchant_address TEXT,
    merchant_phone VARCHAR(15),
    merchant_id VARCHAR(50),
    terminal_id VARCHAR(20),
    transaction_location VARCHAR(200),
    transaction_coordinates VARCHAR(50), -- GPS coordinates
    cardholder_present BOOLEAN,
    card_present BOOLEAN,
    entry_method VARCHAR(20), -- Chip, Swipe, Contactless, Manual, Online
    authorization_code VARCHAR(10),
    reference_number VARCHAR(50),
    trace_number VARCHAR(20),
    batch_number VARCHAR(10),
    sequence_number VARCHAR(10),
    acquiring_bank_id VARCHAR(20),
    issuing_bank_id VARCHAR(20),
    payment_processor VARCHAR(50),
    network_reference_id VARCHAR(50),
    atm_id VARCHAR(20),
    atm_location VARCHAR(200),
    check_number VARCHAR(10),
    check_image_front_path VARCHAR(255),
    check_image_back_path VARCHAR(255),
    check_routing_number VARCHAR(9),
    check_account_number VARCHAR(20),
    wire_fed_reference VARCHAR(20),
    wire_originator_name VARCHAR(100),
    wire_originator_account VARCHAR(20),
    wire_originator_address TEXT,
    wire_beneficiary_name VARCHAR(100),
    wire_beneficiary_account VARCHAR(20),
    wire_beneficiary_address TEXT,
    wire_purpose VARCHAR(100),
    ach_company_name VARCHAR(100),
    ach_company_id VARCHAR(10),
    ach_entry_class_code VARCHAR(3),
    ach_trace_number VARCHAR(15),
    international_transaction BOOLEAN,
    country_of_transaction VARCHAR(50),
    foreign_transaction_fee DECIMAL(8,2),
    cash_advance_fee DECIMAL(8,2),
    overlimit_fee DECIMAL(6,2),
    nsf_fee DECIMAL(6,2), -- Non-Sufficient Funds
    fraud_score INTEGER,
    fraud_indicators TEXT,
    risk_assessment VARCHAR(20),
    transaction_approved BOOLEAN,
    decline_reason VARCHAR(100),
    chargeback_flag BOOLEAN,
    chargeback_reason VARCHAR(100),
    dispute_flag BOOLEAN,
    dispute_reason TEXT,
    reversal_flag BOOLEAN,
    reversal_reason VARCHAR(100),
    suspicious_activity_flag BOOLEAN,
    sar_filed BOOLEAN, -- Suspicious Activity Report
    ctr_filed BOOLEAN, -- Currency Transaction Report
    regulatory_reporting_required BOOLEAN,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INVESTMENT AND WEALTH MANAGEMENT
-- =============================================================================

-- Investment Account Information
CREATE TABLE investment_accounts (
    investment_account_id VARCHAR(20) PRIMARY KEY,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id VARCHAR(20) REFERENCES bank_customers(customer_id),
    account_type VARCHAR(50), -- IRA, Roth IRA, 401k, 403b, Brokerage, Trust
    account_subtype VARCHAR(50),
    account_title VARCHAR(100),
    ownership_type VARCHAR(30),
    registration_type VARCHAR(50),
    custodian_name VARCHAR(100),
    custodian_account_number VARCHAR(30),
    investment_advisor_id VARCHAR(20),
    investment_advisor_name VARCHAR(100),
    investment_advisor_firm VARCHAR(100),
    investment_advisor_license VARCHAR(20),
    portfolio_manager_name VARCHAR(100),
    account_representative VARCHAR(100),
    account_opening_date DATE,
    account_closing_date DATE,
    account_status VARCHAR(20),
    tax_status VARCHAR(30),
    qualified_plan_type VARCHAR(50),
    employer_plan_name VARCHAR(100),
    employer_ein VARCHAR(10),
    participant_id VARCHAR(20),
    vesting_schedule TEXT,
    contribution_limits TEXT,
    current_year_contributions DECIMAL(12,2),
    employer_match_amount DECIMAL(8,2),
    rollover_eligibility BOOLEAN,
    distribution_restrictions TEXT,
    beneficiary_primary_name VARCHAR(100),
    beneficiary_primary_ssn VARCHAR(11),
    beneficiary_primary_relationship VARCHAR(30),
    beneficiary_primary_percentage DECIMAL(5,2),
    beneficiary_contingent_name VARCHAR(100),
    beneficiary_contingent_ssn VARCHAR(11),
    beneficiary_contingent_relationship VARCHAR(30),
    beneficiary_contingent_percentage DECIMAL(5,2),
    account_value DECIMAL(15,2),
    cash_balance DECIMAL(12,2),
    margin_balance DECIMAL(12,2),
    margin_interest_rate DECIMAL(6,4),
    buying_power DECIMAL(12,2),
    unrealized_gains_losses DECIMAL(12,2),
    realized_gains_losses_ytd DECIMAL(12,2),
    dividend_income_ytd DECIMAL(8,2),
    interest_income_ytd DECIMAL(8,2),
    fees_paid_ytd DECIMAL(6,2),
    investment_objectives TEXT,
    risk_tolerance VARCHAR(20),
    time_horizon VARCHAR(30),
    liquidity_needs VARCHAR(50),
    investment_experience VARCHAR(50),
    asset_allocation_target TEXT,
    rebalancing_frequency VARCHAR(30),
    performance_benchmark VARCHAR(50),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Securities Holdings and Positions
CREATE TABLE securities_holdings (
    holding_id VARCHAR(20) PRIMARY KEY,
    investment_account_id VARCHAR(20) REFERENCES investment_accounts(investment_account_id),
    security_symbol VARCHAR(20),
    security_cusip VARCHAR(9), -- Committee on Uniform Securities Identification
    security_isin VARCHAR(12), -- International Securities Identification Number
    security_name VARCHAR(100),
    security_type VARCHAR(30), -- Stock, Bond, Mutual Fund, ETF, Option, etc.
    asset_class VARCHAR(30),
    sector VARCHAR(50),
    industry VARCHAR(50),
    quantity DECIMAL(15,4),
    unit_price DECIMAL(12,4),
    market_value DECIMAL(15,2),
    cost_basis DECIMAL(15,2),
    unrealized_gain_loss DECIMAL(12,2),
    unrealized_gain_loss_percent DECIMAL(6,4),
    purchase_date DATE,
    purchase_price DECIMAL(12,4),
    dividend_yield DECIMAL(6,4),
    annual_dividend DECIMAL(8,2),
    last_dividend_date DATE,
    ex_dividend_date DATE,
    maturity_date DATE,
    coupon_rate DECIMAL(6,4),
    credit_rating VARCHAR(10),
    option_type VARCHAR(10), -- Call, Put
    strike_price DECIMAL(12,4),
    expiration_date DATE,
    option_multiplier INTEGER,
    margin_eligible BOOLEAN,
    marginable_percent DECIMAL(5,2),
    short_position BOOLEAN,
    tax_lot_method VARCHAR(30),
    wash_sale_flag BOOLEAN,
    tax_deferred BOOLEAN,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- MORTGAGE AND LENDING
-- =============================================================================

-- Loan Applications and Mortgage Information
CREATE TABLE loan_applications (
    application_id VARCHAR(20) PRIMARY KEY,
    application_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id VARCHAR(20) REFERENCES bank_customers(customer_id),
    co_applicant_name VARCHAR(100),
    co_applicant_ssn VARCHAR(11),
    co_applicant_dob DATE,
    co_applicant_phone VARCHAR(15),
    co_applicant_email VARCHAR(100),
    co_applicant_employer VARCHAR(100),
    co_applicant_income DECIMAL(12,2),
    loan_type VARCHAR(50), -- Conventional, FHA, VA, USDA, Jumbo
    loan_purpose VARCHAR(30), -- Purchase, Refinance, Cash-out Refinance
    loan_amount_requested DECIMAL(12,2),
    loan_term_months INTEGER,
    interest_rate_requested DECIMAL(6,4),
    property_address TEXT,
    property_city VARCHAR(50),
    property_state VARCHAR(20),
    property_zip_code VARCHAR(10),
    property_type VARCHAR(30), -- Single Family, Condo, Townhouse, etc.
    property_use VARCHAR(30), -- Primary Residence, Second Home, Investment
    property_value DECIMAL(12,2),
    down_payment_amount DECIMAL(12,2),
    down_payment_source TEXT,
    loan_to_value_ratio DECIMAL(5,2),
    debt_to_income_ratio DECIMAL(5,2),
    applicant_gross_monthly_income DECIMAL(10,2),
    applicant_net_monthly_income DECIMAL(10,2),
    applicant_monthly_debt_payments DECIMAL(8,2),
    applicant_assets_liquid DECIMAL(12,2),
    applicant_assets_retirement DECIMAL(12,2),
    applicant_assets_real_estate DECIMAL(12,2),
    applicant_liabilities TEXT,
    credit_score_primary INTEGER,
    credit_score_secondary INTEGER,
    credit_bureau_used VARCHAR(50),
    credit_report_date DATE,
    bankruptcies_last_7_years INTEGER,
    foreclosures_last_7_years INTEGER,
    judgments_liens TEXT,
    employment_history TEXT,
    income_verification_documents TEXT,
    asset_verification_documents TEXT,
    property_appraisal_value DECIMAL(12,2),
    property_appraisal_date DATE,
    property_appraiser_name VARCHAR(100),
    property_appraiser_license VARCHAR(20),
    title_insurance_company VARCHAR(100),
    title_insurance_policy_number VARCHAR(30),
    homeowners_insurance_company VARCHAR(100),
    homeowners_insurance_policy_number VARCHAR(30),
    homeowners_insurance_amount DECIMAL(8,2),
    pmi_required BOOLEAN, -- Private Mortgage Insurance
    pmi_company VARCHAR(100),
    pmi_monthly_payment DECIMAL(6,2),
    escrow_account BOOLEAN,
    estimated_closing_costs DECIMAL(8,2),
    good_faith_estimate_provided BOOLEAN,
    truth_in_lending_provided BOOLEAN,
    application_date DATE,
    application_status VARCHAR(30),
    underwriter_name VARCHAR(100),
    underwriting_decision VARCHAR(30),
    underwriting_conditions TEXT,
    approval_amount DECIMAL(12,2),
    approval_terms TEXT,
    closing_date DATE,
    loan_officer_name VARCHAR(100),
    loan_officer_license VARCHAR(20),
    loan_processor_name VARCHAR(100),
    originating_branch VARCHAR(50),
    hmda_reporting_required BOOLEAN, -- Home Mortgage Disclosure Act
    cra_credit_applicable BOOLEAN, -- Community Reinvestment Act
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Active Loan Accounts
CREATE TABLE loan_accounts (
    loan_account_id VARCHAR(20) PRIMARY KEY,
    loan_number VARCHAR(20) UNIQUE NOT NULL,
    application_id VARCHAR(20) REFERENCES loan_applications(application_id),
    customer_id VARCHAR(20) REFERENCES bank_customers(customer_id),
    borrower_name VARCHAR(100),
    borrower_ssn VARCHAR(11),
    co_borrower_name VARCHAR(100),
    co_borrower_ssn VARCHAR(11),
    loan_type VARCHAR(50),
    loan_product_code VARCHAR(20),
    original_loan_amount DECIMAL(12,2),
    current_principal_balance DECIMAL(12,2),
    interest_rate DECIMAL(6,4),
    interest_rate_type VARCHAR(20), -- Fixed, Variable, Adjustable
    loan_term_months INTEGER,
    remaining_term_months INTEGER,
    monthly_payment_amount DECIMAL(8,2),
    monthly_payment_due_date INTEGER, -- Day of month
    next_payment_due_date DATE,
    last_payment_date DATE,
    last_payment_amount DECIMAL(8,2),
    escrow_balance DECIMAL(8,2),
    escrow_monthly_payment DECIMAL(6,2),
    property_taxes_annual DECIMAL(8,2),
    homeowners_insurance_annual DECIMAL(6,2),
    pmi_monthly_payment DECIMAL(6,2),
    interest_paid_ytd DECIMAL(8,2),
    principal_paid_ytd DECIMAL(8,2),
    escrow_paid_ytd DECIMAL(6,2),
    late_fees_paid_ytd DECIMAL(6,2),
    loan_origination_date DATE,
    first_payment_date DATE,
    maturity_date DATE,
    payoff_amount DECIMAL(12,2),
    payoff_good_through_date DATE,
    loan_status VARCHAR(30),
    days_past_due INTEGER,
    payment_history_12_months VARCHAR(12), -- 0=On Time, 1=30 Days Late, etc.
    delinquency_status VARCHAR(30),
    foreclosure_status VARCHAR(30),
    foreclosure_start_date DATE,
    bankruptcy_flag BOOLEAN,
    modification_flag BOOLEAN,
    modification_terms TEXT,
    loan_servicer VARCHAR(100),
    servicer_loan_number VARCHAR(20),
    servicer_transfer_date DATE,
    investor_name VARCHAR(100),
    investor_loan_number VARCHAR(30),
    loan_purpose VARCHAR(30),
    property_address TEXT,
    property_value_current DECIMAL(12,2),
    property_value_original DECIMAL(12,2),
    ltv_current DECIMAL(5,2), -- Loan to Value
    ltv_original DECIMAL(5,2),
    hazard_insurance_company VARCHAR(100),
    hazard_insurance_policy VARCHAR(30),
    flood_insurance_required BOOLEAN,
    flood_insurance_company VARCHAR(100),
    subordinate_liens TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INSURANCE PRODUCTS
-- =============================================================================

-- Life Insurance Policies
CREATE TABLE life_insurance_policies (
    policy_id VARCHAR(20) PRIMARY KEY,
    policy_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id VARCHAR(20) REFERENCES bank_customers(customer_id),
    policyholder_name VARCHAR(100),
    policyholder_ssn VARCHAR(11),
    policyholder_dob DATE,
    insured_person_name VARCHAR(100),
    insured_person_ssn VARCHAR(11),
    insured_person_dob DATE,
    insured_person_gender CHAR(1),
    relationship_to_policyholder VARCHAR(30),
    policy_type VARCHAR(50), -- Term, Whole Life, Universal Life, Variable
    coverage_amount DECIMAL(12,2),
    premium_amount DECIMAL(8,2),
    premium_frequency VARCHAR(20), -- Monthly, Quarterly, Semi-Annual, Annual
    premium_payment_method VARCHAR(30),
    policy_effective_date DATE,
    policy_expiration_date DATE,
    policy_status VARCHAR(20),
    cash_value DECIMAL(10,2),
    loan_against_policy DECIMAL(8,2),
    dividend_balance DECIMAL(6,2),
    beneficiary_primary_name VARCHAR(100),
    beneficiary_primary_ssn VARCHAR(11),
    beneficiary_primary_relationship VARCHAR(30),
    beneficiary_primary_percentage DECIMAL(5,2),
    beneficiary_contingent_name VARCHAR(100),
    beneficiary_contingent_ssn VARCHAR(11),
    beneficiary_contingent_relationship VARCHAR(30),
    beneficiary_contingent_percentage DECIMAL(5,2),
    medical_exam_required BOOLEAN,
    medical_exam_date DATE,
    medical_examiner VARCHAR(100),
    health_questionnaire_completed BOOLEAN,
    medical_records_reviewed BOOLEAN,
    underwriting_class VARCHAR(20),
    smoking_status VARCHAR(20),
    medical_conditions TEXT,
    medications TEXT,
    hazardous_activities TEXT,
    travel_restrictions TEXT,
    agent_name VARCHAR(100),
    agent_license_number VARCHAR(20),
    agent_commission_rate DECIMAL(5,2),
    medical_information_bureau_check BOOLEAN,
    prescription_database_check BOOLEAN,
    motor_vehicle_report_check BOOLEAN,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- BUSINESS BANKING
-- =============================================================================

-- Business Customer Information
CREATE TABLE business_customers (
    business_customer_id VARCHAR(20) PRIMARY KEY,
    business_account_number VARCHAR(20) UNIQUE NOT NULL,
    legal_business_name VARCHAR(200),
    dba_name VARCHAR(200), -- Doing Business As
    federal_tax_id VARCHAR(10), -- EIN
    state_tax_id VARCHAR(20),
    business_type VARCHAR(50), -- Corporation, LLC, Partnership, Sole Proprietorship
    incorporation_state VARCHAR(20),
    incorporation_date DATE,
    naics_code VARCHAR(10), -- North American Industry Classification System
    sic_code VARCHAR(10), -- Standard Industrial Classification
    business_description TEXT,
    annual_revenue DECIMAL(15,2),
    number_of_employees INTEGER,
    years_in_business INTEGER,
    business_address_line1 VARCHAR(100),
    business_address_line2 VARCHAR(100),
    business_city VARCHAR(50),
    business_state VARCHAR(20),
    business_zip_code VARCHAR(10),
    business_country VARCHAR(50),
    business_phone VARCHAR(15),
    business_fax VARCHAR(15),
    business_email VARCHAR(100),
    business_website VARCHAR(100),
    principal_owner_1_name VARCHAR(100),
    principal_owner_1_ssn VARCHAR(11),
    principal_owner_1_dob DATE,
    principal_owner_1_title VARCHAR(50),
    principal_owner_1_ownership_percent DECIMAL(5,2),
    principal_owner_1_address TEXT,
    principal_owner_2_name VARCHAR(100),
    principal_owner_2_ssn VARCHAR(11),
    principal_owner_2_dob DATE,
    principal_owner_2_title VARCHAR(50),
    principal_owner_2_ownership_percent DECIMAL(5,2),
    principal_owner_2_address TEXT,
    authorized_signer_1_name VARCHAR(100),
    authorized_signer_1_ssn VARCHAR(11),
    authorized_signer_1_title VARCHAR(50),
    authorized_signer_2_name VARCHAR(100),
    authorized_signer_2_ssn VARCHAR(11),
    authorized_signer_2_title VARCHAR(50),
    financial_statements_required BOOLEAN,
    financial_statements_frequency VARCHAR(20),
    cpa_firm_name VARCHAR(100),
    cpa_contact_name VARCHAR(100),
    cpa_phone VARCHAR(15),
    business_license_number VARCHAR(30),
    business_license_state VARCHAR(20),
    business_license_expiration DATE,
    professional_license_info TEXT,
    insurance_carrier VARCHAR(100),
    insurance_policy_numbers TEXT,
    workers_compensation_carrier VARCHAR(100),
    workers_compensation_policy VARCHAR(30),
    kyb_completion_date DATE, -- Know Your Business
    kyb_risk_rating VARCHAR(20),
    sanctions_screening_date DATE,
    pep_screening_date DATE, -- Politically Exposed Person
    adverse_media_screening_date DATE,
    cash_intensive_business BOOLEAN,
    money_services_business BOOLEAN,
    high_risk_business BOOLEAN,
    correspondent_banking BOOLEAN,
    international_transactions BOOLEAN,
    account_opening_date DATE,
    relationship_manager VARCHAR(100),
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- ANTI-MONEY LAUNDERING (AML) AND COMPLIANCE
-- =============================================================================

-- Suspicious Activity Monitoring
CREATE TABLE suspicious_activity_reports (
    sar_id VARCHAR(20) PRIMARY KEY,
    sar_number VARCHAR(20) UNIQUE,
    customer_id VARCHAR(20),
    account_numbers TEXT,
    report_type VARCHAR(50),
    filing_date DATE,
    incident_date_begin DATE,
    incident_date_end DATE,
    total_dollar_amount DECIMAL(15,2),
    suspicious_activity_type TEXT,
    narrative_description TEXT,
    law_enforcement_contacted BOOLEAN,
    law_enforcement_agency VARCHAR(100),
    law_enforcement_contact_name VARCHAR(100),
    law_enforcement_contact_phone VARCHAR(15),
    subject_1_name VARCHAR(100),
    subject_1_ssn VARCHAR(11),
    subject_1_dob DATE,
    subject_1_address TEXT,
    subject_1_phone VARCHAR(15),
    subject_1_occupation VARCHAR(100),
    subject_2_name VARCHAR(100),
    subject_2_ssn VARCHAR(11),
    subject_2_dob DATE,
    subject_2_address TEXT,
    subject_2_phone VARCHAR(15),
    financial_institution_name VARCHAR(100),
    financial_institution_ein VARCHAR(10),
    financial_institution_address TEXT,
    filing_institution_contact_name VARCHAR(100),
    filing_institution_contact_title VARCHAR(50),
    filing_institution_contact_phone VARCHAR(15),
    corrected_report BOOLEAN,
    previous_sar_number VARCHAR(20),
    continuing_activity BOOLEAN,
    fincen_acknowledgment VARCHAR(50),
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Currency Transaction Reports
CREATE TABLE currency_transaction_reports (
    ctr_id VARCHAR(20) PRIMARY KEY,
    ctr_number VARCHAR(20) UNIQUE,
    transaction_date DATE,
    financial_institution_name VARCHAR(100),
    financial_institution_ein VARCHAR(10),
    financial_institution_address TEXT,
    account_number VARCHAR(20),
    transaction_type VARCHAR(50),
    total_cash_in DECIMAL(12,2),
    total_cash_out DECIMAL(12,2),
    person_on_whose_behalf VARCHAR(100),
    conducting_person_name VARCHAR(100),
    conducting_person_ssn VARCHAR(11),
    conducting_person_dob DATE,
    conducting_person_address TEXT,
    conducting_person_phone VARCHAR(15),
    conducting_person_id_type VARCHAR(30),
    conducting_person_id_number VARCHAR(30),
    conducting_person_id_state VARCHAR(20),
    conducting_person_occupation VARCHAR(100),
    armored_car_service BOOLEAN,
    multiple_persons BOOLEAN,
    cash_in_amounts TEXT,
    cash_out_amounts TEXT,
    foreign_currency_involved BOOLEAN,
    foreign_currency_details TEXT,
    structured_transaction BOOLEAN,
    filing_reason TEXT,
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- PAYMENT PROCESSING AND MERCHANT SERVICES
-- =============================================================================

-- Merchant Account Information
CREATE TABLE merchant_accounts (
    merchant_id VARCHAR(20) PRIMARY KEY,
    merchant_account_number VARCHAR(20) UNIQUE NOT NULL,
    business_customer_id VARCHAR(20) REFERENCES business_customers(business_customer_id),
    dba_name VARCHAR(200),
    legal_business_name VARCHAR(200),
    federal_tax_id VARCHAR(10),
    merchant_category_code VARCHAR(4),
    business_type VARCHAR(50),
    processing_services TEXT, -- Credit Cards, Debit Cards, ACH, etc.
    settlement_account_number VARCHAR(20),
    settlement_routing_number VARCHAR(9),
    average_monthly_volume DECIMAL(12,2),
    maximum_transaction_amount DECIMAL(10,2),
    chargeback_threshold DECIMAL(5,2),
    reserve_account_required BOOLEAN,
    reserve_percentage DECIMAL(5,2),
    reserve_amount DECIMAL(10,2),
    discount_rate_visa DECIMAL(6,4),
    discount_rate_mastercard DECIMAL(6,4),
    discount_rate_amex DECIMAL(6,4),
    discount_rate_discover DECIMAL(6,4),
    transaction_fee_visa DECIMAL(6,2),
    transaction_fee_mastercard DECIMAL(6,2),
    monthly_statement_fee DECIMAL(6,2),
    chargeback_fee DECIMAL(6,2),
    equipment_lease_fee DECIMAL(6,2),
    pci_compliance_fee DECIMAL(6,2),
    early_termination_fee DECIMAL(8,2),
    contract_start_date DATE,
    contract_end_date DATE,
    contract_term_months INTEGER,
    auto_renewal BOOLEAN,
    terminal_ids TEXT,
    gateway_provider VARCHAR(50),
    risk_monitoring_level VARCHAR(20),
    high_risk_merchant BOOLEAN,
    industry_risk_level VARCHAR(20),
    underwriting_approval_date DATE,
    underwriting_conditions TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- FOREIGN EXCHANGE AND INTERNATIONAL BANKING
-- =============================================================================

-- Foreign Exchange Transactions
CREATE TABLE foreign_exchange_transactions (
    fx_transaction_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES bank_customers(customer_id),
    transaction_date DATE,
    transaction_time TIME,
    value_date DATE,
    transaction_type VARCHAR(30), -- Spot, Forward, Swap
    buy_currency CHAR(3),
    sell_currency CHAR(3),
    buy_amount DECIMAL(15,2),
    sell_amount DECIMAL(15,2),
    exchange_rate DECIMAL(12,6),
    usd_equivalent DECIMAL(15,2),
    purpose_of_transaction TEXT,
    beneficiary_name VARCHAR(100),
    beneficiary_account VARCHAR(50),
    beneficiary_bank VARCHAR(100),
    beneficiary_bank_swift VARCHAR(11),
    beneficiary_address TEXT,
    originator_name VARCHAR(100),
    originator_account VARCHAR(50),
    originator_address TEXT,
    intermediary_bank VARCHAR(100),
    intermediary_swift VARCHAR(11),
    correspondent_bank VARCHAR(100),
    correspondent_swift VARCHAR(11),
    wire_instructions TEXT,
    regulatory_reporting_required BOOLEAN,
    ofac_screening_performed BOOLEAN,
    ofac_screening_result VARCHAR(30),
    aml_screening_performed BOOLEAN,
    enhanced_due_diligence BOOLEAN,
    country_risk_rating VARCHAR(20),
    transaction_fees DECIMAL(8,2),
    commission_earned DECIMAL(6,2),
    profit_loss DECIMAL(8,2),
    hedge_contract_number VARCHAR(20),
    created_by VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR FINANCIAL PERFORMANCE
-- =============================================================================

-- Customer Indexes
CREATE INDEX idx_bank_customers_ssn ON bank_customers(ssn);
CREATE INDEX idx_bank_customers_email ON bank_customers(email_primary);
CREATE INDEX idx_bank_customers_phone ON bank_customers(mobile_phone);
CREATE INDEX idx_bank_customers_customer_number ON bank_customers(customer_number);

-- Account Indexes
CREATE INDEX idx_deposit_accounts_customer ON deposit_accounts(customer_id);
CREATE INDEX idx_deposit_accounts_number ON deposit_accounts(account_number);
CREATE INDEX idx_credit_cards_customer ON credit_card_accounts(customer_id);
CREATE INDEX idx_credit_cards_pan ON credit_card_accounts(primary_card_number_masked);

-- Transaction Indexes
CREATE INDEX idx_transactions_account ON financial_transactions(account_id);
CREATE INDEX idx_transactions_date ON financial_transactions(transaction_date);
CREATE INDEX idx_transactions_amount ON financial_transactions(transaction_amount);
CREATE INDEX idx_transactions_merchant ON financial_transactions(merchant_name);

-- Investment Indexes
CREATE INDEX idx_investment_accounts_customer ON investment_accounts(customer_id);
CREATE INDEX idx_securities_holdings_account ON securities_holdings(investment_account_id);
CREATE INDEX idx_securities_cusip ON securities_holdings(security_cusip);

-- Loan Indexes
CREATE INDEX idx_loan_applications_customer ON loan_applications(customer_id);
CREATE INDEX idx_loan_applications_ssn ON loan_applications(co_applicant_ssn);
CREATE INDEX idx_loan_accounts_customer ON loan_accounts(customer_id);
CREATE INDEX idx_loan_accounts_borrower_ssn ON loan_accounts(borrower_ssn);

-- Business Customer Indexes
CREATE INDEX idx_business_customers_ein ON business_customers(federal_tax_id);
CREATE INDEX idx_business_customers_owner1_ssn ON business_customers(principal_owner_1_ssn);
CREATE INDEX idx_business_customers_owner2_ssn ON business_customers(principal_owner_2_ssn);

-- AML Indexes
CREATE INDEX idx_sar_customer ON suspicious_activity_reports(customer_id);
CREATE INDEX idx_sar_subject1_ssn ON suspicious_activity_reports(subject_1_ssn);
CREATE INDEX idx_ctr_person_ssn ON currency_transaction_reports(conducting_person_ssn);
CREATE INDEX idx_ctr_date ON currency_transaction_reports(transaction_date);

-- =============================================================================
-- VIEWS FOR FINANCIAL PII REPORTING
-- =============================================================================

-- Customer PII Summary View
CREATE VIEW customer_pii_summary AS
SELECT 
    customer_id,
    customer_number,
    CASE WHEN ssn IS NOT NULL THEN 'SSN_PRESENT' ELSE 'SSN_MISSING' END as ssn_status,
    CASE WHEN email_primary IS NOT NULL THEN 'EMAIL_PRESENT' ELSE 'EMAIL_MISSING' END as email_status,
    CASE WHEN mobile_phone IS NOT NULL THEN 'PHONE_PRESENT' ELSE 'PHONE_MISSING' END as phone_status,
    CASE WHEN drivers_license_number IS NOT NULL THEN 'DL_PRESENT' ELSE 'DL_MISSING' END as dl_status
FROM bank_customers;

-- Credit Card PII Summary View
CREATE VIEW credit_card_pii_summary AS
SELECT 
    card_account_id,
    account_number,
    CASE WHEN primary_cardholder_ssn IS NOT NULL THEN 'SSN_PRESENT' ELSE 'SSN_MISSING' END as ssn_status,
    CASE WHEN primary_card_number_masked IS NOT NULL THEN 'PAN_MASKED' ELSE 'PAN_NOT_MASKED' END as pan_status,
    card_network,
    card_product_type
FROM credit_card_accounts;

-- =============================================================================
-- COMMENTS FOR FINANCIAL PII IDENTIFICATION
-- =============================================================================

-- Table Comments
COMMENT ON TABLE bank_customers IS 'Banking customer master data with comprehensive PII fields';
COMMENT ON TABLE credit_card_accounts IS 'Credit card account information with PCI DSS protected data';
COMMENT ON TABLE financial_transactions IS 'Financial transaction records with payment card data';
COMMENT ON TABLE investment_accounts IS 'Investment account data with beneficial ownership information';
COMMENT ON TABLE loan_applications IS 'Mortgage and loan applications with extensive financial PII';
COMMENT ON TABLE business_customers IS 'Business customer data with beneficial ownership details';

-- Key PII Column Comments
COMMENT ON COLUMN bank_customers.ssn IS 'Social Security Number - PII, GDPR Personal Data, CCPA Personal Information';
COMMENT ON COLUMN bank_customers.email_primary IS 'Primary Email Address - PII, GDPR Personal Data';
COMMENT ON COLUMN credit_card_accounts.primary_card_number IS 'Primary Account Number (PAN) - PCI DSS Protected Data';
COMMENT ON COLUMN credit_card_accounts.primary_card_cvv IS 'Card Verification Value - PCI DSS Sensitive Authentication Data';
COMMENT ON COLUMN loan_applications.co_applicant_ssn IS 'Co-Applicant SSN - PII, HMDA Reportable Data';
COMMENT ON COLUMN business_customers.principal_owner_1_ssn IS 'Business Owner SSN - PII, Beneficial Ownership Information';
