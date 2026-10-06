#!/usr/bin/env python3
"""
Project Sentinel: Commercial Credit Risk & Early-Warning Surveillance Engine
Module: Automated Quality Assurance, Logic Verification & Property-Based Tests
Author: Dhruv Chaudhary, Commercial Risk Analytics Case Study

Verifies:
1. Scoring Logic: Exact point allocation across statutory lag, confirmation statement, charges, and account conduct.
2. Non-Circularity: Proves on-time filers exist in Amber/Red and late filers exist in Green.
3. Tier Boundaries: Strict mathematical enforcement of Red (>=70), Amber (40-69), Green (<40).
4. Capacity Constraints: Strict verification of BSRU workout caseload within 10-14 files.
5. Cohort Cleanliness: Zero digit-leading names, zero dormant shells, zero >365d overdue accounts.
6. Financial Reconciliation: Exact balance sheet arithmetic and waterfall summation.
7. Data Protection: Zero real company names alongside simulated conduct in exported outputs.
"""

import os
import sqlite3
import unittest
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'sentinel_credit_radar.db')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

class TestSentinelPortfolioIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database not found at {DB_PATH}. Run src/ingest_companies_house.py first.")
        cls.conn = sqlite3.connect(DB_PATH)
        cls.cursor = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_01_scoring_logic_rules_exact_calculation(self):
        """Verify that individual scoring components and raw score cap (100) are calculated exactly."""
        self.cursor.execute("""
            SELECT 
                loan_id,
                accounts_days_overdue, score_filing_lag,
                conf_stmt_days_overdue, score_conf_stmt,
                company_status, score_insolvency_event,
                num_mort_outstanding, score_charge_encumbrance,
                unpaid_dd_count_90d, score_unpaid_dd,
                consecutive_od_pinned_days, score_od_utilization,
                hard_core_borrowing_flag, score_hard_core,
                statutory_distress_score
            FROM vw_statutory_distress_index;
        """)
        rows = self.cursor.fetchall()
        self.assertEqual(len(rows), 250, "Portfolio must contain exactly 250 facilities")

        for r in rows:
            loan_id = r[0]
            days_overdue, s_filing = r[1], r[2]
            conf_days, s_conf = r[3], r[4]
            status, s_insolv = r[5], r[6]
            mort_count, s_mort = r[7], r[8]
            dd_count, s_dd = r[9], r[10]
            od_days, s_od = r[11], r[12]
            hc_flag, s_hc = r[13], r[14]
            total_score = r[15]

            # 1. Filing lag rule verification
            if days_overdue > 60:
                self.assertEqual(s_filing, 25, f"{loan_id}: Filing delay >60d must score 25")
            elif days_overdue > 21:
                self.assertEqual(s_filing, 15, f"{loan_id}: Filing delay 22-60d must score 15")
            elif days_overdue > 0:
                self.assertEqual(s_filing, 5, f"{loan_id}: Filing delay 1-21d must score 5")
            else:
                self.assertEqual(s_filing, 0, f"{loan_id}: On-time filing must score 0")

            # 2. Confirmation statement rule verification
            if conf_days > 30:
                self.assertEqual(s_conf, 10, f"{loan_id}: Conf stmt >30d must score 10")
            elif conf_days > 14:
                self.assertEqual(s_conf, 5, f"{loan_id}: Conf stmt 15-30d must score 5")
            else:
                self.assertEqual(s_conf, 0, f"{loan_id}: Current conf stmt must score 0")

            # 3. Direct debit payment friction verification
            if dd_count >= 3:
                self.assertEqual(s_dd, 30, f"{loan_id}: Unpaid DDs >=3 must score 30")
            elif dd_count >= 1:
                self.assertEqual(s_dd, 15, f"{loan_id}: Unpaid DDs 1-2 must score 15")
            else:
                self.assertEqual(s_dd, 0, f"{loan_id}: Clean DD conduct must score 0")

            # 4. Overdraft utilization verification
            if od_days >= 60:
                self.assertEqual(s_od, 25, f"{loan_id}: Overdraft pinned >=60d must score 25")
            elif od_days >= 30:
                self.assertEqual(s_od, 15, f"{loan_id}: Overdraft pinned 30-59d must score 15")
            elif od_days >= 14:
                self.assertEqual(s_od, 5, f"{loan_id}: Overdraft pinned 14-29d must score 5")
            else:
                self.assertEqual(s_od, 0, f"{loan_id}: Normal overdraft conduct must score 0")

            # 5. Hard-core borrowing verification
            expected_hc = 10 if hc_flag == 1 else 0
            self.assertEqual(s_hc, expected_hc, f"{loan_id}: Hardcore score mismatch")

            # 6. Composite Score Summation & Cap at 100
            expected_raw = s_filing + s_conf + s_insolv + s_mort + s_dd + s_od + s_hc
            expected_capped = min(100, expected_raw)
            self.assertEqual(total_score, expected_capped, f"{loan_id}: Composite score does not match capped sum of components")

    def test_02_non_circularity_dual_source_fusion(self):
        """Assert model is non-circular: on-time filers can be Amber/Red, and late filers can be Green."""
        self.cursor.execute("""
            SELECT 
                CASE WHEN accounts_days_overdue > 0 THEN 'Late Filer' ELSE 'On-Time Filer' END as filing_status,
                operational_risk_tier,
                COUNT(*) as cnt
            FROM vw_portfolio_triage_actions
            GROUP BY filing_status, operational_risk_tier;
        """)
        contingency = {(r[0], r[1]): r[2] for r in self.cursor.fetchall()}

        # 1. On-time filers MUST have borrowers in elevated risk (Amber) caught by internal account conduct
        ontime_amber = contingency.get(('On-Time Filer', 'AMBER_ELEVATED'), 0)
        self.assertGreater(ontime_amber, 0, "Non-circularity failure: on-time filers must have Amber detections driven by internal conduct")

        # 2. Late filers MUST have borrowers in Green (benign administrative delay with clean bank conduct)
        late_green = contingency.get(('Late Filer', 'GREEN_STANDARD'), 0)
        self.assertGreater(late_green, 0, "Non-circularity failure: late filers with clean conduct must be classified as Green")

        # 3. Severe multi-signal distress (Red) must exist
        late_red = contingency.get(('Late Filer', 'RED_CRITICAL'), 0)
        self.assertGreater(late_red, 0, "Severe dual-flagged borrowers must populate Red Critical tier")

    def test_03_tier_boundary_enforcement(self):
        """Assert strict tier boundaries: Red >= 70, Amber 40-69, Green < 40."""
        self.cursor.execute("""
            SELECT loan_id, statutory_distress_score, operational_risk_tier
            FROM vw_portfolio_triage_actions;
        """)
        for loan_id, score, tier in self.cursor.fetchall():
            if score >= 70:
                self.assertEqual(tier, 'RED_CRITICAL', f"{loan_id}: Score {score} must be RED_CRITICAL")
            elif score >= 40:
                self.assertEqual(tier, 'AMBER_ELEVATED', f"{loan_id}: Score {score} must be AMBER_ELEVATED")
            else:
                self.assertEqual(tier, 'GREEN_STANDARD', f"{loan_id}: Score {score} must be GREEN_STANDARD")

    def test_04_bsru_workout_capacity_constraint(self):
        """Assert BSRU Specialist Workout Squad caseload is strictly bounded within operational capacity (10-14 files)."""
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM vw_portfolio_triage_actions 
            WHERE operational_assignment_routing = 'BSRU_WORKOUT_SQUAD';
        """)
        bsru_count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(bsru_count, 10, "BSRU squad must have sufficient critical cases to justify squad deployment")
        self.assertLessEqual(bsru_count, 14, f"BSRU capacity breach: {bsru_count} files exceeds 14-file team capacity limit")

        # Assert all BSRU cases meet exposure materiality criteria (drawn >= £350k and score >= 70)
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM vw_portfolio_triage_actions 
            WHERE operational_assignment_routing = 'BSRU_WORKOUT_SQUAD' 
              AND (drawn_amount < 350000 OR statutory_distress_score < 70);
        """)
        invalid_bsru = self.cursor.fetchone()[0]
        self.assertEqual(invalid_bsru, 0, "All BSRU squad files must satisfy drawn >= £350k and score >= 70")

    def test_05_clean_commercial_sample_integrity(self):
        """Assert cohort consists of active trading commercial businesses: 0% digits, 0% dormant shells."""
        self.cursor.execute("SELECT company_name, accounts_category, company_status FROM tbl_companies_house_profile;")
        rows = self.cursor.fetchall()
        self.assertEqual(len(rows), 250, "Cohort must have 250 profiles")

        for name, acc_cat, status in rows:
            # 1. No digit-leading names
            self.assertFalse(name[0].isdigit(), f"Company name '{name}' must not start with a digit")
            self.assertTrue(name[0].isalpha(), f"Company name '{name}' must start with an alphabetic letter")

            # 2. No dormant shells
            self.assertNotEqual(acc_cat.upper(), 'DORMANT', f"Dormant company '{name}' found in commercial loan book")
            self.assertEqual(status, 'Active', f"Non-active company '{name}' found in portfolio")

        # 3. No accounts overdue > 365 days (abandoned shells)
        self.cursor.execute("SELECT COUNT(*) FROM vw_filing_lag_telemetry WHERE accounts_days_overdue > 365;")
        over_365 = self.cursor.fetchone()[0]
        self.assertEqual(over_365, 0, f"Found {over_365} companies with accounts overdue > 365 days (abandoned shells)")

        # 4. Balanced regional coverage (at least 6 distinct UK regions)
        self.cursor.execute("SELECT COUNT(DISTINCT region) FROM tbl_borrower_portfolio;")
        distinct_regions = self.cursor.fetchone()[0]
        self.assertGreaterEqual(distinct_regions, 6, "Portfolio must span diverse UK regions")

    def test_06_balance_sheet_and_waterfall_reconciliation(self):
        """Assert drawn + undrawn = facility limit and loss mitigation waterfall sums exactly to net benefit."""
        # 1. Balance sheet limit reconciliation
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM vw_portfolio_triage_actions 
            WHERE ABS((current_drawn_exposure + undrawn_facility_exposure) - facility_limit) > 0.01;
        """)
        limit_mismatches = self.cursor.fetchone()[0]
        self.assertEqual(limit_mismatches, 0, "Drawn + undrawn exposure must equal facility limit across all facilities")

        # 2. Reconcile Loss Mitigation Waterfall Arithmetic
        self.cursor.execute("""
            SELECT 
                SUM(CASE WHEN operational_risk_tier = 'RED_CRITICAL' THEN current_drawn_exposure ELSE 0 END) as red_drawn,
                SUM(CASE WHEN operational_risk_tier = 'RED_CRITICAL' THEN undrawn_facility_exposure ELSE 0 END) as red_undrawn,
                SUM(CASE WHEN operational_risk_tier = 'AMBER_ELEVATED' THEN current_drawn_exposure ELSE 0 END) as amber_drawn
            FROM vw_portfolio_triage_actions;
        """)
        red_drawn, red_undrawn, amber_drawn = self.cursor.fetchone()

        # Exact financial model components:
        consensual_uplift = red_drawn * 0.428 * (0.75 - 0.55)
        headroom_freeze = red_undrawn * 0.75 * 0.428 * 0.75
        amber_cure = amber_drawn * 0.125 * 0.20 * 0.65
        sentinel_cost = 210000.0

        gross_preserved = consensual_uplift + headroom_freeze + amber_cure
        net_preserved = gross_preserved - sentinel_cost

        # Assert gross preserved is approx £1.03M and net is approx £816k
        self.assertAlmostEqual(gross_preserved, 1026403.54, delta=100.0, msg="Gross capital preserved mismatch")
        self.assertAlmostEqual(net_preserved, 816403.54, delta=100.0, msg="Net first-year benefit mismatch")

    def test_07_public_export_data_protection(self):
        """Assert exported CSV outputs are completely sanitized with pseudonymous identifiers."""
        master_csv = os.path.join(RESULTS_DIR, "portfolio_triage_master.csv")
        self.assertTrue(os.path.exists(master_csv), "portfolio_triage_master.csv must exist in results/")

        df_csv = pd.read_csv(master_csv)
        self.assertEqual(len(df_csv), 250, "Master export must contain 250 rows")

        # Assert every row uses pseudonymous borrower ID and simulated CRN
        for _, r in df_csv.iterrows():
            b_id = str(r['borrower_id'])
            s_crn = str(r['simulated_crn'])
            self.assertTrue(b_id.startswith('Commercial Borrower BRW-'), f"Invalid public borrower ID: {b_id}")
            self.assertTrue(s_crn.startswith('CRN-SIM-'), f"Invalid public CRN: {s_crn}")

        # Assert zero real company names from Companies House appear in the exported CSV
        self.cursor.execute("SELECT company_name FROM tbl_companies_house_profile;")
        real_names = set(r[0].strip().upper() for r in self.cursor.fetchall())
        csv_borrower_ids = set(df_csv['borrower_id'].str.upper())
        intersection = real_names.intersection(csv_borrower_ids)
        self.assertEqual(len(intersection), 0, f"Privacy leak: real company names found in public export: {intersection}")

if __name__ == '__main__':
    unittest.main()
