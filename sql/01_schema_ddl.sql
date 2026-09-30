-- ============================================================================
-- Project Sentinel: Commercial Credit Risk & Early-Warning Surveillance
-- Database Schema DDL (PostgreSQL / SQLite)
-- Author: Dhruv Chaudhary, Commercial Risk Analytics
-- ============================================================================

-- 1. Master Borrower Portfolio & Internal Account Conduct Telemetry
CREATE TABLE IF NOT EXISTS tbl_borrower_portfolio (
    loan_id                     TEXT PRIMARY KEY,
    company_number              TEXT NOT NULL,
    client_name                 TEXT NOT NULL,
    parent_group_comp_number    TEXT,             -- OpCo / HoldCo Group Structure Link
    parent_group_name           TEXT,
    facility_type               TEXT NOT NULL,    -- 'Revolving Credit Facility', 'Commercial Overdraft', 'Term Loan'
    drawn_amount                REAL NOT NULL,
    facility_limit              REAL NOT NULL,
    interest_margin_pct         REAL NOT NULL,
    origination_date            TEXT NOT NULL,
    maturity_date               TEXT NOT NULL,
    primary_rm_name             TEXT NOT NULL,    -- Commercial Relationship Manager
    region                      TEXT NOT NULL,    -- 'Yorkshire & Humber', 'North West', 'Midlands', 'London'
    security_rank               TEXT NOT NULL,    -- 'First Fixed Charge', 'Floating Charge', 'Unsecured'
    -- Internal Behavioral Account Conduct Telemetry (Bank's Own Current Account Data)
    unpaid_dd_count_90d         INTEGER DEFAULT 0,-- Unpaid direct debits (HMRC VAT / PAYE / Key Suppliers)
    consecutive_od_pinned_days  INTEGER DEFAULT 0,-- Consecutive days overdraft utilization > 95%
    hard_core_borrowing_flag    INTEGER DEFAULT 0 -- Chronic working capital dependency
);

-- 2. Official Companies House Corporate Registry Telemetry
CREATE TABLE IF NOT EXISTS tbl_companies_house_profile (
    company_number              TEXT PRIMARY KEY,
    company_name                TEXT NOT NULL,
    post_town                   TEXT,
    county                      TEXT,
    post_code                   TEXT,
    company_category            TEXT,
    company_status              TEXT,             -- 'Active', 'In Administration', 'Liquidation', 'Dissolved'
    country_of_origin           TEXT,
    incorporation_date          TEXT,
    dissolution_date            TEXT,
    accounts_next_due_date      TEXT,
    accounts_last_made_up_date  TEXT,
    accounts_category           TEXT,
    confirmation_stmt_next_due  TEXT,
    confirmation_stmt_last_made TEXT,
    num_mort_charges            INTEGER DEFAULT 0,
    num_mort_outstanding        INTEGER DEFAULT 0,
    num_mort_satisfied          INTEGER DEFAULT 0,
    sic_code_1                  TEXT,
    uri                         TEXT,
    snapshot_date               TEXT NOT NULL
);

-- 3. Register of Mortgages & Floating Charges (Section 859A Companies Act 2006)
-- Enhanced with Legal Security Trustee / Nominee Resolution
CREATE TABLE IF NOT EXISTS tbl_charges_register (
    charge_id                   TEXT PRIMARY KEY,
    company_number              TEXT NOT NULL,
    charge_number               INTEGER,
    creation_date               TEXT,
    delivered_date              TEXT,
    status                      TEXT,             -- 'outstanding', 'satisfied', 'part-satisfied'
    charge_type                 TEXT,             -- 'debenture', 'floating_charge', 'fixed_and_floating', 'specific_asset_lease'
    persons_entitled            TEXT,             -- Registered legal chargee / nominee
    distress_lender_category    TEXT,             -- 'INVOICE_FACTORING', 'DISTRESS_FUND', 'MAINSTREAM_BANK', 'ASSET_LEASE'
    is_secondary_distress_lender INTEGER DEFAULT 0,
    FOREIGN KEY (company_number) REFERENCES tbl_companies_house_profile(company_number)
);

-- 4. Statutory Filing History Events
CREATE TABLE IF NOT EXISTS tbl_filing_history (
    filing_id                   TEXT PRIMARY KEY,
    company_number              TEXT NOT NULL,
    filing_date                 TEXT NOT NULL,
    filing_type                 TEXT,             -- 'AA' (Accounts), 'CS01' (Conf Stmt), 'GAZ1' (Strike-off), 'TM01' (Resignation)
    filing_category             TEXT,             -- 'accounts', 'confirmation-statement', 'gazette', 'officers'
    description                 TEXT,
    FOREIGN KEY (company_number) REFERENCES tbl_companies_house_profile(company_number)
);

-- Indexes for Rapid Analytical Queries
CREATE INDEX IF NOT EXISTS idx_portfolio_comp_num ON tbl_borrower_portfolio(company_number);
CREATE INDEX IF NOT EXISTS idx_portfolio_parent ON tbl_borrower_portfolio(parent_group_comp_number);
CREATE INDEX IF NOT EXISTS idx_ch_status ON tbl_companies_house_profile(company_status);
CREATE INDEX IF NOT EXISTS idx_ch_accounts_due ON tbl_companies_house_profile(accounts_next_due_date);
CREATE INDEX IF NOT EXISTS idx_charges_comp_num ON tbl_charges_register(company_number);
CREATE INDEX IF NOT EXISTS idx_filing_comp_num ON tbl_filing_history(company_number);
