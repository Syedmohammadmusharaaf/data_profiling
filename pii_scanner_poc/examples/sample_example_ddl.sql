CREATE TABLE Person.PersonPhone (
    BusinessEntityID INT,
    PhoneNumber NVARCHAR(50),
    PhoneNumberTypeID INT,
    ModifiedDate DATETIME
);

CREATE TABLE Person.PhoneNumberType (
    PhoneNumberTypeID INT,
    Name NVARCHAR(100),
    ModifiedDate DATETIME
);

CREATE TABLE Person.Address (
    AddressID INT,
    AddressLine1 NVARCHAR(100),
    AddressLine2 NVARCHAR(100),
    City NVARCHAR(50),
    StateProvinceID INT,
    PostalCode NVARCHAR(20),
    SpatialLocation GEOGRAPHY,
    rowguid UNIQUEIDENTIFIER,
    ModifiedDate DATETIME
);

CREATE TABLE Person.AddressType (
    AddressTypeID INT,
    Name NVARCHAR(50),
    rowguid UNIQUEIDENTIFIER,
    ModifiedDate DATETIME
);

CREATE TABLE Person.StateProvince (
    StateProvinceID INT,
    StateProvinceCode NCHAR(3),
    CountryRegionCode NVARCHAR(10),
    IsOnlyStateProvinceFlag BIT,
    Name NVARCHAR(100),
    TerritoryID INT,
    rowguid UNIQUEIDENTIFIER,
    ModifiedDate DATETIME
);

CREATE TABLE Person.BusinessEntity (
    BusinessEntityID INT,
    rowguid UNIQUEIDENTIFIER,
    ModifiedDate DATETIME
);

CREATE TABLE Person.BusinessEntityAddress (
    BusinessEntityID INT,
    AddressID INT,
    AddressTypeID INT,
    rowguid UNIQUEIDENTIFIER,
    ModifiedDate DATETIME
);

CREATE TABLE Person.BusinessEntityContact (
    BusinessEntityID INT,
    PersonID INT,
    ContactTypeID INT,
    rowguid UNIQUEIDENTIFIER,
    ModifiedDate DATETIME
);

CREATE TABLE Person.ContactType (
    ContactTypeID INT,
    Name NVARCHAR(50),
    ModifiedDate DATETIME
);

CREATE TABLE Person.CountryRegion (
    CountryRegionCode NVARCHAR(5),
    Name NVARCHAR(100),
    ModifiedDate DATETIME
);

CREATE TABLE Person.EmailAddress (
    BusinessEntityID INT,
    EmailAddressID INT,
    EmailAddress NVARCHAR(100),
    rowguid UNIQUEIDENTIFIER,
    ModifiedDate DATETIME
);

CREATE TABLE Person.Password (
    BusinessEntityID INT,
    PasswordHash VARCHAR(128),
    PasswordSalt VARCHAR(128),
    rowguid UNIQUEIDENTIFIER,
    ModifiedDate DATETIME
);

CREATE TABLE Person.Person (
    BusinessEntityID INT,
    PersonType NCHAR(2),
    NameStyle BIT,
    Title NVARCHAR(50),
    FirstName NVARCHAR(50),
    MiddleName NVARCHAR(50),
    LastName NVARCHAR(50),
    Suffix NVARCHAR(50),
    EmailPromotion INT,
    AdditionalContactInfo XML,
    Demographics XML,
    rowguid UNIQUEIDENTIFIER,
    ModifiedDate DATETIME
);
CREATE TABLE Person.PersonCreditCard (
    BusinessEntityID INT,
    CreditCardID INT,
    CardType NVARCHAR(50),
    CardNumber NVARCHAR(25),
    ExpMonth INT,
    ExpYear INT,
    ModifiedDate DATETIME
);


--===== 1-5: HR =====
CREATE TABLE hr_employees (
  emp_id             INT        PRIMARY KEY,
  first_name         VARCHAR(50),
  last_name          VARCHAR(50),
  dob                DATE,
  ssn                CHAR(9),
  email              VARCHAR(150),
  phone              VARCHAR(20),
  hire_date          DATE,
  department_id      INT
);

CREATE TABLE hr_departments (
  department_id      INT        PRIMARY KEY,
  name               VARCHAR(100),
  manager_emp_id     INT        REFERENCES hr_employees(emp_id)
);

CREATE TABLE hr_payroll (
  payroll_id         BIGSERIAL  PRIMARY KEY,
  emp_id             INT        REFERENCES hr_employees(emp_id),
  salary             DECIMAL(12,2),
  bonus              DECIMAL(12,2),
  pay_date           DATE
);

CREATE TABLE hr_attendance (
  attendance_id      BIGSERIAL  PRIMARY KEY,
  emp_id             INT        REFERENCES hr_employees(emp_id),
  date               DATE,
  status             VARCHAR(10)  -- PRESENT, ABSENT, REMOTE
);

CREATE TABLE hr_performance_reviews (
  review_id          BIGSERIAL  PRIMARY KEY,
  emp_id             INT        REFERENCES hr_employees(emp_id),
  review_date        DATE,
  score              INT,
  comments           TEXT
);

-- ===== 6-10: Finance =====
CREATE TABLE fin_customers (
  customer_id        BIGSERIAL  PRIMARY KEY,
  name               VARCHAR(100),
  email              VARCHAR(150),
  phone              VARCHAR(20),
  address            TEXT
);

CREATE TABLE fin_accounts (
  account_id         BIGSERIAL  PRIMARY KEY,
  customer_id        BIGINT     REFERENCES fin_customers(customer_id),
  account_type       VARCHAR(20),
  opened_date        DATE,
  balance            DECIMAL(15,2)
);

CREATE TABLE fin_transactions (
  txn_id             BIGSERIAL  PRIMARY KEY,
  account_id         BIGINT     REFERENCES fin_accounts(account_id),
  txn_date           TIMESTAMP,
  amount             DECIMAL(12,2),
  merchant           VARCHAR(100)
);

CREATE TABLE fin_loans (
  loan_id            BIGSERIAL  PRIMARY KEY,
  customer_id        BIGINT     REFERENCES fin_customers(customer_id),
  principal_amount   DECIMAL(15,2),
  interest_rate      DECIMAL(5,2),
  start_date         DATE,
  end_date           DATE
);

CREATE TABLE fin_payments (
  payment_id         BIGSERIAL  PRIMARY KEY,
  loan_id            BIGINT     REFERENCES fin_loans(loan_id),
  payment_date       DATE,
  amount             DECIMAL(12,2)
);

-- ===== 11-15: Healthcare =====
CREATE TABLE hc_patients (
  patient_id         UUID       PRIMARY KEY,
  full_name          VARCHAR(100),
  dob                DATE,
  gender             VARCHAR(10),
  phone              VARCHAR(20),
  email              VARCHAR(150),
  address            TEXT
);

CREATE TABLE hc_visits (
  visit_id           BIGSERIAL  PRIMARY KEY,
  patient_id         UUID       REFERENCES hc_patients(patient_id),
  visit_date         TIMESTAMP,
  reason             TEXT
);

CREATE TABLE hc_diagnoses (
  diag_id            BIGSERIAL  PRIMARY KEY,
  visit_id           BIGSERIAL  REFERENCES hc_visits(visit_id),
  code               VARCHAR(10),
  description        TEXT
);

CREATE TABLE hc_prescriptions (
  prescription_id    BIGSERIAL  PRIMARY KEY,
  diag_id            BIGSERIAL  REFERENCES hc_diagnoses(diag_id),
  medication_name    VARCHAR(100),
  dosage             VARCHAR(50),
  start_date         DATE,
  end_date           DATE
);

CREATE TABLE hc_insurance (
  insurance_id       BIGSERIAL  PRIMARY KEY,
  patient_id         UUID       REFERENCES hc_patients(patient_id),
  provider           VARCHAR(100),
  policy_number      VARCHAR(50),
  effective_date     DATE,
  expiry_date        DATE
);

-- ===== 16-20: E-commerce =====
CREATE TABLE ec_users (
  user_id            UUID       PRIMARY KEY,
  username           VARCHAR(50) UNIQUE,
  email              VARCHAR(150),
  password_hash      VARCHAR(255),
  signup_date        DATE
);

CREATE TABLE ec_products (
  product_id         BIGSERIAL  PRIMARY KEY,
  name               VARCHAR(150),
  description        TEXT,
  price              DECIMAL(10,2),
  sku                VARCHAR(50)
);

CREATE TABLE ec_orders (
  order_id           BIGSERIAL  PRIMARY KEY,
  user_id            UUID       REFERENCES ec_users(user_id),
  order_date         TIMESTAMP,
  status             VARCHAR(20)
);

CREATE TABLE ec_order_items (
  item_id            BIGSERIAL  PRIMARY KEY,
  order_id           BIGINT     REFERENCES ec_orders(order_id),
  product_id         BIGINT     REFERENCES ec_products(product_id),
  quantity           INT,
  unit_price         DECIMAL(10,2)
);

CREATE TABLE ec_carts (
  cart_id            UUID       PRIMARY KEY,
  user_id            UUID       REFERENCES ec_users(user_id),
  created_at         TIMESTAMP
);

-- ===== 21-25: Marketing & Sales =====
CREATE TABLE mkt_campaigns (
  campaign_id        BIGSERIAL  PRIMARY KEY,
  name               VARCHAR(150),
  start_date         DATE,
  end_date           DATE,
  budget             DECIMAL(12,2)
);

CREATE TABLE mkt_leads (
  lead_id            BIGSERIAL  PRIMARY KEY,
  campaign_id        BIGINT     REFERENCES mkt_campaigns(campaign_id),
  contact_name       VARCHAR(100),
  email              VARCHAR(150),
  phone              VARCHAR(20),
  created_at         TIMESTAMP
);

CREATE TABLE crm_opportunities (
  opp_id             BIGSERIAL  PRIMARY KEY,
  lead_id            BIGINT     REFERENCES mkt_leads(lead_id),
  stage              VARCHAR(50),
  value              DECIMAL(12,2),
  close_date         DATE
);

CREATE TABLE ad_clicks (
  click_id           BIGSERIAL  PRIMARY KEY,
  campaign_id        BIGINT     REFERENCES mkt_campaigns(campaign_id),
  clicked_at         TIMESTAMP,
  user_id            UUID
);

CREATE TABLE conversions (
  conversion_id      BIGSERIAL  PRIMARY KEY,
  click_id           BIGINT     REFERENCES ad_clicks(click_id),
  conversion_time    TIMESTAMP,
  revenue            DECIMAL(12,2)
);

-- ===== 26-30: Supply Chain, CRM & Support =====
CREATE TABLE sc_vendors (
  vendor_id          BIGSERIAL  PRIMARY KEY,
  name               VARCHAR(150),
  contact_name       VARCHAR(100),
  phone              VARCHAR(20),
  email              VARCHAR(150),
  address            TEXT
);

CREATE TABLE sc_purchase_orders (
  po_id              BIGSERIAL  PRIMARY KEY,
  vendor_id          BIGINT     REFERENCES sc_vendors(vendor_id),
  order_date         DATE,
  total_amount       DECIMAL(12,2)
);

CREATE TABLE inventory (
  sku                VARCHAR(50) PRIMARY KEY,
  product_id         BIGINT     REFERENCES ec_products(product_id),
  warehouse_id       INT,
  quantity_on_hand   INT
);

CREATE TABLE shipments (
  shipment_id        BIGSERIAL  PRIMARY KEY,
  po_id              BIGINT     REFERENCES sc_purchase_orders(po_id),
  shipped_date       DATE,
  delivered_date     DATE
);

CREATE TABLE support_tickets (
  ticket_id          BIGSERIAL  PRIMARY KEY,
  user_id            UUID       REFERENCES ec_users(user_id),
  subject            VARCHAR(200),
  description        TEXT,
  status             VARCHAR(20),
  created_at         TIMESTAMP,
  closed_at          TIMESTAMP
);



CREATE TABLE hr_employees (
  emp_id             INT        PRIMARY KEY,
  first_name         VARCHAR(50),
  last_name          VARCHAR(50),
  dob                DATE,
  ssn                CHAR(9),
  email              VARCHAR(150),
  phone              VARCHAR(20),
  address            TEXT,
  hire_date          DATE,
  department_id      INT
);

-- 2. HR: Departments
CREATE TABLE hr_departments (
  department_id      INT        PRIMARY KEY,
  name               VARCHAR(100)
);

-- 3. HR: Payroll
CREATE TABLE hr_payroll (
  payroll_id         BIGSERIAL  PRIMARY KEY,
  emp_id             INT        REFERENCES hr_employees(emp_id),
  salary             DECIMAL(12,2),
  bonus              DECIMAL(12,2),
  pay_date           DATE
);

-- 4. Healthcare: Patients
CREATE TABLE hc_patients (
  patient_id         UUID       PRIMARY KEY,
  full_name          VARCHAR(100),
  dob                DATE,
  gender             VARCHAR(10),
  address            TEXT,
  phone              VARCHAR(20),
  email              VARCHAR(150)
);

-- 5. Healthcare: Visits
CREATE TABLE hc_visits (
  visit_id           BIGSERIAL  PRIMARY KEY,
  patient_id         UUID       REFERENCES hc_patients(patient_id),
  visit_date         TIMESTAMP,
  reason             TEXT
);

-- 6. Healthcare: Diagnoses
CREATE TABLE hc_diagnoses (
  diag_id            BIGSERIAL  PRIMARY KEY,
  visit_id           BIGSERIAL  REFERENCES hc_visits(visit_id),
  code               VARCHAR(10),
  description        TEXT
);

-- 7. Finance: Customers
CREATE TABLE fin_customers (
  customer_id        BIGSERIAL  PRIMARY KEY,
  name               VARCHAR(100),
  email              VARCHAR(150),
  phone              VARCHAR(20),
  address            TEXT
);

-- 8. Finance: Accounts
CREATE TABLE fin_accounts (
  account_id         BIGSERIAL  PRIMARY KEY,
  customer_id        BIGINT     REFERENCES fin_customers(customer_id),
  type               VARCHAR(20),
  opened_date        DATE,
  balance            DECIMAL(15,2)
);

-- 9. Finance: Transactions
CREATE TABLE fin_transactions (
  txn_id             BIGSERIAL  PRIMARY KEY,
  account_id         BIGINT     REFERENCES fin_accounts(account_id),
  txn_date           TIMESTAMP,
  amount             DECIMAL(12,2),
  merchant           VARCHAR(100)
);

-- 10. E-commerce: Users
CREATE TABLE ec_users (
  user_id            UUID       PRIMARY KEY,
  username           VARCHAR(50),
  email              VARCHAR(150),
  password_hash      VARCHAR(255),
  signup_date        DATE
);

-- 11. E-commerce: Products
CREATE TABLE ec_products (
  product_id         BIGSERIAL  PRIMARY KEY,
  name               VARCHAR(150),
  description        TEXT,
  price              DECIMAL(10,2),
  sku                VARCHAR(50)
);

-- 12. E-commerce: Orders
CREATE TABLE ec_orders (
  order_id           BIGSERIAL  PRIMARY KEY,
  user_id            UUID       REFERENCES ec_users(user_id),
  order_date         TIMESTAMP,
  status             VARCHAR(20)
);

-- 13. E-commerce: Order Items
CREATE TABLE ec_order_items (
  item_id            BIGSERIAL  PRIMARY KEY,
  order_id           BIGINT     REFERENCES ec_orders(order_id),
  product_id         BIGINT     REFERENCES ec_products(product_id),
  quantity           INT,
  unit_price         DECIMAL(10,2)
);

-- 14. Logging: Access Logs
CREATE TABLE app_access_logs (
  log_id             BIGSERIAL  PRIMARY KEY,
  user_id            UUID,
  access_time        TIMESTAMP,
  ip_address         VARCHAR(45),
  resource           VARCHAR(200)
);

-- 15. Logging: Error Logs
CREATE TABLE app_error_logs (
  error_id           BIGSERIAL  PRIMARY KEY,
  occurred_at        TIMESTAMP,
  service_name       VARCHAR(100),
  error_message      TEXT,
  stack_trace        TEXT
);

-- 16. Marketing: Campaigns
CREATE TABLE mkt_campaigns (
  campaign_id        BIGSERIAL  PRIMARY KEY,
  name               VARCHAR(150),
  start_date         DATE,
  end_date           DATE,
  budget             DECIMAL(12,2)
);

-- 17. Marketing: Leads
CREATE TABLE mkt_leads (
  lead_id            BIGSERIAL  PRIMARY KEY,
  campaign_id        BIGINT     REFERENCES mkt_campaigns(campaign_id),
  contact_name       VARCHAR(100),
  email              VARCHAR(150),
  phone              VARCHAR(20),
  lead_source        VARCHAR(50),
  created_at         TIMESTAMP
);

-- 18. Supply Chain: Vendors
CREATE TABLE sc_vendors (
  vendor_id          BIGSERIAL  PRIMARY KEY,
  name               VARCHAR(150),
  contact_name       VARCHAR(100),
  phone              VARCHAR(20),
  email              VARCHAR(150),
  address            TEXT
);

-- 19. Supply Chain: Purchase Orders
CREATE TABLE sc_purchase_orders (
  po_id              BIGSERIAL  PRIMARY KEY,
  vendor_id          BIGINT     REFERENCES sc_vendors(vendor_id),
  order_date         DATE,
  total_amount       DECIMAL(12,2)
);

-- 20. CRM: Contacts
CREATE TABLE crm_contacts (
  contact_id         BIGSERIAL  PRIMARY KEY,
  first_name         VARCHAR(50),
  last_name          VARCHAR(50),
  email              VARCHAR(150),
  phone              VARCHAR(20),
  company            VARCHAR(100)
);

-- 21. CRM: Opportunities
CREATE TABLE crm_opportunities (
  opp_id             BIGSERIAL  PRIMARY KEY,
  contact_id         BIGINT     REFERENCES crm_contacts(contact_id),
  stage              VARCHAR(50),
  value              DECIMAL(12,2),
  close_date         DATE
);

-- 22. IoT: Devices
CREATE TABLE iot_devices (
  device_id          UUID       PRIMARY KEY,
  model              VARCHAR(100),
  deployed_at        TIMESTAMP,
  location           VARCHAR(100)
);

-- 23. IoT: Telemetry
CREATE TABLE iot_telemetry (
  telemetry_id       BIGSERIAL  PRIMARY KEY,
  device_id          UUID       REFERENCES iot_devices(device_id),
  recorded_at        TIMESTAMP,
  temperature        DECIMAL(5,2),
  humidity           DECIMAL(5,2)
);

-- 24. R&D: Experiments
CREATE TABLE rnd_experiments (
  experiment_id      BIGSERIAL  PRIMARY KEY,
  name               VARCHAR(150),
  start_date         DATE,
  end_date           DATE,
  lead_scientist     VARCHAR(100)
);

-- 25. R&D: Results
CREATE TABLE rnd_results (
  result_id          BIGSERIAL  PRIMARY KEY,
  experiment_id      BIGINT     REFERENCES rnd_experiments(experiment_id),
  recorded_at        TIMESTAMP,
  metric_name        VARCHAR(100),
  metric_value       DECIMAL(12,4)
);

