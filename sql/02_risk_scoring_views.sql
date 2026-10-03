-- ============================================================================
-- Project Sentinel: Commercial Credit Risk & Early-Warning Surveillance
-- Analytical Risk Scoring Views & Prioritization Views
-- Author: Dhruv Chaudhary, Commercial Risk Analytics Case Study
-- ============================================================================

-- ----------------------------------------------------------------------------
-- VIEW 1: Statutory Filing Lag Telemetry
-- Calculates exact calendar days past statutory filing deadlines
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_corporate_group_exposure;
DROP VIEW IF EXISTS vw_portfolio_triage_actions;
DROP VIEW IF EXISTS vw_statutory_distress_index;
DROP VIEW IF EXISTS vw_charge_telemetry;
DROP VIEW IF EXISTS vw_filing_lag_telemetry;

CREATE VIEW vw_filing_lag_telemetry AS
SELECT 
    p.loan_id,
    p.client_name,
    p.company_number,
    p.parent_group_comp_number,
    p.parent_group_name,
    p.drawn_amount,
    p.facility_limit,
    p.region,
    p.facility_type,
    p.unpaid_dd_count_90d,
    p.consecutive_od_pinned_days,
    p.hard_core_borrowing_flag,
    ch.company_status,
    ch.accounts_next_due_date,
    ch.snapshot_date,
    -- Compute calendar days overdue past statutory accounts deadline
    CASE 
        WHEN ch.accounts_next_due_date IS NULL THEN 0
        WHEN ch.accounts_next_due_date < ch.snapshot_date 
        THEN CAST((julianday(ch.snapshot_date) - julianday(ch.accounts_next_due_date)) AS INTEGER)
        ELSE 0 
    END AS accounts_days_overdue,
    -- Filing Lag Severity Tiers
    CASE 
        WHEN ch.accounts_next_due_date >= ch.snapshot_date THEN 'CURRENT'
        WHEN (julianday(ch.snapshot_date) - julianday(ch.accounts_next_due_date)) BETWEEN 1 AND 21 THEN 'GRACE_PERIOD_1_21D'
        WHEN (julianday(ch.snapshot_date) - julianday(ch.accounts_next_due_date)) BETWEEN 22 AND 60 THEN 'MODERATE_DELAY_22_60D'
        WHEN (julianday(ch.snapshot_date) - julianday(ch.accounts_next_due_date)) > 60 THEN 'SEVERE_DELAY_OVER_60D'
        ELSE 'UNKNOWN'
    END AS filing_delinquency_tier,
    -- Confirmation Statement delinquency check
    CASE 
        WHEN ch.confirmation_stmt_next_due < ch.snapshot_date 
        THEN CAST((julianday(ch.snapshot_date) - julianday(ch.confirmation_stmt_next_due)) AS INTEGER)
        ELSE 0 
    END AS conf_stmt_days_overdue
FROM tbl_borrower_portfolio p
JOIN tbl_companies_house_profile ch ON p.company_number = ch.company_number;

-- ----------------------------------------------------------------------------
-- VIEW 2: Charge & Collateral Encumbrance Telemetry
-- Summarizes registered charges and collateral encumbrance
-- ----------------------------------------------------------------------------
CREATE VIEW vw_charge_telemetry AS
SELECT 
    p.company_number,
    ch.num_mort_charges,
    ch.num_mort_outstanding,
    ch.num_mort_satisfied,
    CASE WHEN ch.num_mort_outstanding >= 3 THEN 1 ELSE 0 END AS high_charge_encumbrance_flag
FROM tbl_borrower_portfolio p
JOIN tbl_companies_house_profile ch ON p.company_number = ch.company_number;

-- ----------------------------------------------------------------------------
-- VIEW 3: Composite Distress Index (0 to 100) & Behavioral Fusion
-- Combines statutory filing delinquency, confirmation statement lag,
-- involuntary dissolution events, balance sheet encumbrance, and internal account conduct.
-- Target Distribution: Red ~4-5%, Amber ~10-12%, Green ~84%
-- ----------------------------------------------------------------------------
CREATE VIEW vw_statutory_distress_index AS
SELECT 
    f.loan_id,
    f.client_name,
    f.company_number,
    f.parent_group_comp_number,
    f.parent_group_name,
    f.drawn_amount,
    f.facility_limit,
    f.facility_type,
    f.region,
    f.company_status,
    f.accounts_days_overdue,
    f.filing_delinquency_tier,
    f.conf_stmt_days_overdue,
    f.unpaid_dd_count_90d,
    f.consecutive_od_pinned_days,
    f.hard_core_borrowing_flag,
    c.num_mort_outstanding,
    c.high_charge_encumbrance_flag,
    
    -- Scoring Component 1: Statutory Accounts Filing Delay (Max 25 pts)
    CASE 
        WHEN f.filing_delinquency_tier = 'SEVERE_DELAY_OVER_60D' THEN 25
        WHEN f.filing_delinquency_tier = 'MODERATE_DELAY_22_60D' THEN 15
        WHEN f.filing_delinquency_tier = 'GRACE_PERIOD_1_21D' THEN 5
        ELSE 0 
    END AS score_filing_lag,
    
    -- Scoring Component 2: Confirmation Statement Delay (Max 10 pts)
    CASE 
        WHEN f.conf_stmt_days_overdue > 30 THEN 10
        WHEN f.conf_stmt_days_overdue > 14 THEN 5
        ELSE 0 
    END AS score_conf_stmt,
    
    -- Scoring Component 3: Formal Insolvency / Administration Event (Max 35 pts)
    CASE 
        WHEN f.company_status IN ('In Administration', 'Liquidation') THEN 35
        ELSE 0 
    END AS score_insolvency_event,
    
    -- Scoring Component 4: High Debt Encumbrance / Collateral Dilution (Max 10 pts)
    CASE 
        WHEN c.num_mort_outstanding >= 4 THEN 10
        WHEN c.num_mort_outstanding >= 2 THEN 5
        ELSE 0 
    END AS score_charge_encumbrance,
    
    -- Scoring Component 5: Internal Behavioral Account Conduct - Unpaid Direct Debits (Max 30 pts)
    CASE 
        WHEN f.unpaid_dd_count_90d >= 3 THEN 30
        WHEN f.unpaid_dd_count_90d >= 1 THEN 15
        ELSE 0 
    END AS score_unpaid_dd,
    
    -- Scoring Component 6: Internal Behavioral Account Conduct - Overdraft Pinned at Limit (Max 25 pts)
    CASE 
        WHEN f.consecutive_od_pinned_days >= 60 THEN 25
        WHEN f.consecutive_od_pinned_days >= 30 THEN 15
        WHEN f.consecutive_od_pinned_days >= 14 THEN 5
        ELSE 0 
    END AS score_od_utilization,

    -- Scoring Component 7: Chronic Working Capital Dependency / Hardcore Borrowing (Max 10 pts)
    CASE 
        WHEN f.hard_core_borrowing_flag = 1 THEN 10
        ELSE 0 
    END AS score_hard_core,

    -- Composite Raw Score capped at 100
    MIN(100, (
        (CASE WHEN f.filing_delinquency_tier = 'SEVERE_DELAY_OVER_60D' THEN 25
              WHEN f.filing_delinquency_tier = 'MODERATE_DELAY_22_60D' THEN 15
              WHEN f.filing_delinquency_tier = 'GRACE_PERIOD_1_21D' THEN 5 ELSE 0 END) +
        (CASE WHEN f.conf_stmt_days_overdue > 30 THEN 10
              WHEN f.conf_stmt_days_overdue > 14 THEN 5 ELSE 0 END) +
        (CASE WHEN f.company_status IN ('In Administration', 'Liquidation') THEN 35 ELSE 0 END) +
        (CASE WHEN c.num_mort_outstanding >= 4 THEN 10
              WHEN c.num_mort_outstanding >= 2 THEN 5 ELSE 0 END) +
        (CASE WHEN f.unpaid_dd_count_90d >= 3 THEN 30
              WHEN f.unpaid_dd_count_90d >= 1 THEN 15 ELSE 0 END) +
        (CASE WHEN f.consecutive_od_pinned_days >= 60 THEN 25
              WHEN f.consecutive_od_pinned_days >= 30 THEN 15
              WHEN f.consecutive_od_pinned_days >= 14 THEN 5 ELSE 0 END) +
        (CASE WHEN f.hard_core_borrowing_flag = 1 THEN 10 ELSE 0 END)
    )) AS statutory_distress_score

FROM vw_filing_lag_telemetry f
JOIN vw_charge_telemetry c ON f.company_number = c.company_number;

-- ----------------------------------------------------------------------------
-- VIEW 4: Portfolio Triage, Bilateral Safe-Harbor Actions & Materiality Index
-- Score Tiers: RED >= 70 (~4-5%), AMBER 40-69 (~12-13%), GREEN < 40 (~83-84%)
-- ----------------------------------------------------------------------------
CREATE VIEW vw_portfolio_triage_actions AS
SELECT 
    s.*,
    -- Operational Risk Tiering
    CASE 
        WHEN s.statutory_distress_score >= 70 THEN 'RED_CRITICAL'
        WHEN s.statutory_distress_score >= 40 THEN 'AMBER_ELEVATED'
        ELSE 'GREEN_STANDARD'
    END AS operational_risk_tier,
    
    -- Materiality Exposure Score (Scaled exposure weighted by score)
    ROUND((s.statutory_distress_score * s.drawn_amount) / 100000.0, 2) AS materiality_exposure_score,
    
    -- Legally Compliant Bilateral Commercial Credit Actions
    CASE 
        WHEN s.statutory_distress_score >= 70 
        THEN 'CREDIT_COMMITTEE_ESCALATION: Issue formal Information Covenant Request under Standard Commercial Terms (13-week cash flow forecast & debtor ledger within 3 business days); convene Special Situations Credit Committee; review discretionary undrawn headroom; verify collateral perfection.'
        
        WHEN s.statutory_distress_score >= 40 
        THEN 'RM_STRUCTURED_REVIEW: Relationship Manager to conduct structured review; request updated monthly management accounts; assess working capital headroom.'
        
        ELSE 'CONTINUOUS_SURVEILLANCE: Routine automated Companies House statutory & account conduct sidecar scan.'
    END AS credit_policy_action,
    
    -- Workouts Capacity Triage Assignment (BSRU Capacity Limit: 10-14 Intense Files)
    CASE 
        WHEN s.statutory_distress_score >= 70 AND s.drawn_amount >= 350000 
        THEN 'BSRU_WORKOUT_SQUAD'
        WHEN s.statutory_distress_score >= 70 
        THEN 'SPECIAL_SITUATIONS_WATCH'
        WHEN s.statutory_distress_score >= 40 
        THEN 'RM_INTENSIVE_CARE'
        ELSE 'STANDARD_SURVEILLANCE'
    END AS operational_assignment_routing,

    s.drawn_amount AS current_drawn_exposure,
    (s.facility_limit - s.drawn_amount) AS undrawn_facility_exposure
FROM vw_statutory_distress_index s;

-- ----------------------------------------------------------------------------
-- VIEW 5: Corporate Group Exposure & Contagion Telemetry
-- Aggregates OpCo / HoldCo group exposures and cross-default risk
-- ----------------------------------------------------------------------------
CREATE VIEW vw_corporate_group_exposure AS
SELECT 
    COALESCE(parent_group_comp_number, 'GRP-STANDALONE-' || SUBSTR(loan_id, 11)) AS consolidated_group_id,
    COALESCE(parent_group_name, client_name || ' (Standalone)') AS consolidated_group_name,
    COUNT(DISTINCT loan_id) AS total_group_facilities,
    COUNT(DISTINCT company_number) AS total_group_entities,
    ROUND(SUM(current_drawn_exposure), 2) AS total_group_drawn,
    ROUND(SUM(facility_limit), 2) AS total_group_limit,
    MAX(statutory_distress_score) AS max_group_distress_score,
    MAX(CASE WHEN operational_risk_tier = 'RED_CRITICAL' THEN 1 ELSE 0 END) AS has_critical_group_member
FROM vw_portfolio_triage_actions
GROUP BY COALESCE(parent_group_comp_number, 'GRP-STANDALONE-' || SUBSTR(loan_id, 11)), COALESCE(parent_group_name, client_name || ' (Standalone)');
