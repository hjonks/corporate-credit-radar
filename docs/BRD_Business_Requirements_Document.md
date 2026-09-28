# Project Sentinel: Commercial Credit Early-Warning Surveillance
## Business Requirements Document (BRD)

> [!NOTE]
> **Project Context & Methodology Disclosure**
> This repository represents a self-initiated commercial credit risk analytics portfolio case study. The corporate registry data (company names, registration numbers, incorporation dates, SIC codes, and statutory filing records) is sourced directly from public UK Government Companies House bulk registry data (`BasicCompanyData-part1.zip`). Internal account conduct signals (unpaid direct debit counts, overdraft utilization, and hardcore borrowing telemetry) are algorithmically synthesized to illustrate dual-source behavioral surveillance without using confidential bank records.

**Document Reference:** BRD-COMM-2026-04  
**Date:** September 2026  
**Version:** 2.0 (Reconciled Empirical Calibration)  
**Author:** Dhruv Chaudhary (Commercial Credit Risk Analytics Portfolio Case Study)  
**Business Sponsor:** Hypothetical Business Persona: J. Thornton (Regional Director - Commercial Lending Operations)  
**Audience:** Commercial Credit Operations, Special Situations / BSRU, Enterprise Solutions Architecture  

---

## 1. Background and Business Problem

The illustrative portfolio simulation models roughly £110.51m in drawn debt across 250 SME and mid-market corporate borrowers, against committed facility limits of £207.85m. In the current economic climate, several commercial sectors—notably regional haulage, specialist manufacturing, building services, and wholesale distribution—operate under compressed operating margins, rising input costs, and working capital friction.

The primary operational challenge facing commercial credit surveillance is reporting latency:

1. **The 9-to-18 Month Financial Statement Lag:** Under Section 442 of the Companies Act 2006, UK private limited companies have up to 9 months after their financial year-end to file statutory accounts at Companies House. Because internal commercial credit reviews are traditionally scheduled around these filings, Relationship Managers frequently review multi-million-pound debt facilities using balance sheets and trading accounts that reflect operating conditions from 12 to 18 months earlier.
2. **Delayed Intervention and Subordinated Recoveries:** By the time an annual review identifies that a business has deteriorated, the borrower has frequently exhausted cash reserves, accumulated substantial unpaid trade debt, and encumbered balance sheet assets with secondary charges. In an unmonitored liquidation or court winding-up, historical asset recovery rates drop to approximately 25% (Loss Given Default of 75%).
3. **Siloed Account Conduct Telemetry:** While core banking transactional databases record daily cash conduct (such as unpaid supplier direct debits and pinned overdrafts), this telemetry historically operated in isolation from statutory filing events. A company filing late accounts is not necessarily distressed; however, when statutory filing delays coincide with unpaid HMRC VAT/PAYE direct debits and persistent hardcore overdraft borrowing, the probability of default escalates sharply.

Project Sentinel addresses this blindspot by establishing an automated, daily early-warning surveillance engine. The system fuses public Companies House statutory data with internal commercial account conduct telemetry, detecting deteriorating facilities 60 to 90 days before formal insolvency occurs.

---

## 2. Key Operational Principles and Constraints

Based on input from senior credit risk officers and workout specialists, the architectural design adheres to five fundamental operational principles:

### 2.1 BSRU Workload and Alert Fatigue
The Business Support and Recoveries Unit (BSRU) operates with dedicated workout officers managing intensive debt restructurings. The team can realistically handle 10 to 14 complex corporate workouts simultaneously. If an automated surveillance tool generates 50 or 60 undifferentiated "critical" alerts monthly, workout specialists will experience alert fatigue, leading to ignored notifications and missed defaults.

Sentinel addresses this capacity reality through dual-factor prioritization:
* **Distress Severity (0 to 100):** Objective likelihood of default derived from fused statutory filings and banking account conduct.
* **Financial Materiality:** Scaled drawn debt exposure.

By combining distress severity with exposure materiality into an exposure-weighted triage metric, Sentinel routes only the highest-materiality distressed accounts (11 facilities in the portfolio) directly to the BSRU Specialist Workout Squad. Moderate-risk accounts are directed to commercial Relationship Managers for structured intensive care.

### 2.2 Bilateral Contractual Safe Harbors
Commercial SME facilities (£250k to £3.5m) sit under the bank's standard bilateral lending terms, with overdrafts repayable on demand and committed term facilities governed by standard information undertakings. Arbitrarily freezing committed drawdowns without demonstrating a contractual Event of Default creates severe legal liability for wrongful acceleration and consequential trading losses.

Sentinel operates strictly as an **advisory intelligence engine**:
* High-distress alerts do not automatically trigger write-backs to freeze transactional ledgers.
* Instead, Sentinel generates structured briefing dossiers, recommends formal Information Demands under Standard Terms Clause 14 (13-week cash flow forecasts and aged debtor ledgers), and convenes the Special Situations Credit Committee.
* Uncommitted discretionary facilities (such as uncommitted revolving headroom and discretionary overdraft limits) are reviewed for consensual curtailment, while committed facilities follow formal legal protocols.

### 2.3 Transparent Collateral Encumbrance Monitoring
Rather than misinterpreting mainstream commercial facilities (such as invoice discounting from accredited asset-based lenders or institutional security trustees) as distress indicators, Sentinel focuses on genuine collateral dilution: tracking the cumulative volume of active outstanding charges, debenture priority registrations under Section 859A, and sudden increases in asset encumbrance.

### 2.4 Corporate Group Structures (OpCo / HoldCo)
Many commercial borrowers operate within holding company or sister operating structures. A borrowing OpCo may appear up to date with its filings, while its parent holding company has received a Gazette strike-off notice or registered secondary charges. Sentinel tracks parent company identifiers (`parent_group_comp_number`) to aggregate exposures across related entities and identify cross-guarantee contagion.

### 2.5 Sidecar Architecture vs. Core Mainframe Modifications
Directly modifying legacy core banking transaction engines would involve multi-year lead times and substantial integration risk. Sentinel is built as an **asynchronous, read-only sidecar**:
* It ingests statutory registry deltas and overnight transaction telemetry into a dedicated analytical datastore (`sentinel_credit_radar.db`).
* It executes analytical scoring views independently.
* It outputs structured triage dossiers and action briefs into relationship management CRM and workout queues.

---

## 3. Project Scope

### In-Scope
* Daily ingestion of official Companies House statutory registry data: accounts due dates, confirmation statement deadlines, Section 859A registered charges, and company legal status changes.
* Overnight ingestion of internal commercial account conduct telemetry: 90-day count of unpaid direct debits (distinguishing HMRC tax demands from commercial suppliers), consecutive days overdraft utilization exceeds 90%, and chronic hardcore borrowing flags.
* Computation of an auditable 0 to 100 Composite Distress Score and exposure-weighted Materiality Index for every facility.
* Automated triage into three risk tiers: Green (Standard), Amber (Elevated), and Red (Critical).
* Operational routing across four specialized queues: BSRU Workout Squad, Special Situations Watch, RM Intensive Care, and Standard Surveillance.
* Integration with workflow systems to generate standardized, bilateral credit action recommendations.
* Group-level exposure consolidation for corporate families with parent-subsidiary structures.

### Out-of-Scope
* Direct automated write-back of balance freezes to core banking transaction ledgers (all credit actions require human underwriter sign-off).
* Retail or consumer credit facilities (the engine is dedicated to commercial SME and mid-market portfolios).
* Unverified third-party sentiment or social media scraping.

---

## 4. Functional Specifications

### 4.1 Statutory Registry Ingestion & Tracking
* The pipeline must evaluate official Companies House registry attributes for all active portfolio borrowers.
* Required statutory attributes include: legal status (`Active`, `In Administration`, `Liquidation`), accounts next due date, accounts last made up date, confirmation statement next due date, and outstanding charge counts.
* The system records the reference snapshot date (`2026-09-01`) for complete auditability.

### 4.2 Account Conduct Telemetry Integration
* Each evening, the pipeline ingests internal account conduct metrics:
  * Count of unpaid direct debits in the preceding 90 calendar days (identifying HMRC VAT and PAYE payment friction).
  * Number of consecutive days the facility has operated pinned at elevated overdraft utilization (>90%).
  * Chronic working capital dependency flag (`hard_core_borrowing_flag`).
* The engine joins these behavioral metrics with statutory registry profiles using registered company numbers.

### 4.3 Risk Scoring Engine & Calibrated Weightings
The engine calculates an auditable Composite Distress Score (0 to 100) using the following calibrated weightings:

| Risk Dimension | Trigger Condition | Points Allocated |
|---|---|---|
| **Statutory Delinquency** | Accounts overdue by >60 calendar days | +25 |
| **Statutory Delinquency** | Accounts overdue by 22 to 60 calendar days | +15 |
| **Statutory Delinquency** | Accounts overdue by 1 to 21 calendar days (grace period) | +5 |
| **Governance Delinquency** | Confirmation statement overdue by >30 calendar days | +10 |
| **Governance Delinquency** | Confirmation statement overdue by 15 to 30 calendar days | +5 |
| **Formal Insolvency** | Company status in Administration or Liquidation | +35 |
| **Balance Sheet Gearing** | Outstanding charges count >= 4 | +10 |
| **Balance Sheet Gearing** | Outstanding charges count 2 to 3 | +5 |
| **Payment Friction** | Unpaid direct debits >= 3 in 90 days (HMRC tax focus) | +30 |
| **Payment Friction** | Unpaid direct debits 1 to 2 in 90 days | +15 |
| **Overdraft Utilization** | Overdraft pinned at limit for >=60 consecutive days | +25 |
| **Overdraft Utilization** | Overdraft pinned at limit for 30 to 59 consecutive days | +15 |
| **Overdraft Utilization** | Overdraft pinned at limit for 14 to 29 consecutive days | +5 |
| **Chronic Borrowing** | Chronic working capital dependency (`hard_core_borrowing_flag = 1`) | +10 |

*Composite raw score is capped at 100 points.*

#### Operational Risk Tier Definitions:
* **Green Standard (Score < 40):** 207 borrowers (£81.50m drawn exposure | 73.8% of drawn book). Prime commercial borrowers operating within normal parameters. Assigned to continuous automated sidecar scan.
* **Amber Elevated (Score 40 to 69):** 32 borrowers (£22.26m drawn exposure | 20.1% of drawn book). Early emerging strain (filing delays or initial payment friction). Assigned to Relationship Manager Intensive Care for structured 13-week cash review.
* **Red Critical (Score >= 70):** 11 borrowers (£6.75m drawn exposure | 6.1% of drawn book). Acute multi-signal distress (severe filing lag coinciding with tax arrears and pinned overdrafts). Assigned to BSRU Specialist Workout Squad for immediate consensual intervention.

### 4.4 Materiality Index & Capacity-Based Routing
To allocate workout resources strictly where balance sheet exposure is material, Sentinel evaluates:
$$	ext{Materiality Exposure Score} = rac{	ext{Composite Distress Score} 	imes 	ext{Current Drawn Exposure}}{100,000}$$

Operational triage rules are executed as follows:
* **BSRU Specialist Workout Squad (11 files | £6.75m drawn):**
  * Condition: Score >= 70 AND Drawn Balance >= £350,000.
  * Operational Assignment: Dedicated Senior Workout Officer; 13-week cash monitoring; debenture audit; consensual turnaround negotiation.
* **Special Situations Watch (0 files):**
  * Condition: Score >= 70 AND Drawn Balance < £350,000.
  * Operational Assignment: Monitored on credit watchlist; discretionary extensions restricted.
* **RM Intensive Care (32 files | £22.26m drawn):**
  * Condition: Score between 40 and 69.
  * Operational Assignment: Commercial Relationship Manager structured review; request updated monthly management accounts; assess working capital headroom.
* **Standard Surveillance (207 files | £81.50m drawn):**
  * Condition: Score < 40.
  * Operational Assignment: Automated daily sidecar scan; no manual intervention required.

### 4.5 Standardized Credit Action Protocols
Each daily triage record generates standardized, bilateral policy guidance:
* **For Red Tier Facilities:**
  `CREDIT_COMMITTEE_ESCALATION: Issue formal Information Covenant Request under Standard Commercial Terms (13-week cash flow forecast & debtor ledger within 3 business days); convene Special Situations Credit Committee; review discretionary undrawn headroom; verify collateral perfection.`
* **For Amber Tier Facilities:**
  `RM_STRUCTURED_REVIEW: Relationship Manager to conduct structured review; request updated monthly management accounts; assess working capital headroom.`
* **For Green Tier Facilities:**
  `CONTINUOUS_SURVEILLANCE: Routine automated Companies House statutory & account conduct sidecar scan.`

---

## 5. Illustrative Portfolio Simulation & Financial Loss Mitigation Summary (Synthetic Portfolio)

> [!NOTE]
> **Simulated Portfolio Framing:** The loan facilities, drawn exposures (£110.51M), and financial loss mitigation calculations detailed below represent an illustrative commercial portfolio simulation calibrated to realistic UK banking parameters. Empirical model discrimination (ROC-AUC 0.8604, Gini 0.7208 on 1,200 real Companies House entities) is evaluated separately in the statistical model validation benchmark.

The initial baseline evaluation on our simulated commercial loan portfolio (£110.51m drawn across 250 facilities) yields the following operational breakdown:

| Operational Queue | Facilities | Total Drawn Exposure | Share of Drawn Debt | Average Distress Score | Assigned Operational Unit |
|---|---|---|---|---|---|
| **BSRU Workout Squad** | 11 | £  6,748,211.61 | 6.1% | 77.7 / 100 | Dedicated Senior Workout Officer |
| **Special Situations Watch** | 0 | £           0.00 | 0.0% | — | Credit Risk Portfolio Watchlist |
| **RM Intensive Care** | 32 | £ 22,255,758.13 | 20.1% | 51.7 / 100 | Commercial Relationship Directors |
| **Standard Surveillance** | 207 | £ 81,502,331.23 | 73.8% | 1.8 / 100 | Automated Daily Sidecar Scan |
| **Total Portfolio** | **250** | **£110,506,300.97** | **100.0%** | **11.2 / 100** | **Full Commercial Loan Book** |

### Projected Financial Impact & Loss Mitigation
* **Unmitigated Baseline Loss:** On the £6.75m Red exposure, an unmonitored default results in additional pre-insolvency drawdowns (£271k) and an unmonitored LGD of 75.0% (25.0% recovery). Across the calibrated 42.8% default rate, baseline expected loss is **£2,253,276.48**.
* **Mitigated Early-Intervention Position:** Early detection (60 to 90 days lead time) preserves capital through three operational mechanisms:
  1. *Consensual Restructuring & Recovery Uplift (+20% LGD, 75% -> 55%):* **+£577,646.91**.
  2. *Discretionary Undrawn Headroom Containment (freezing £271k drawdown):* **+£87,100.55**.
  3. *Amber Early Remediation & Default Prevention (curing 20% of Amber cohort):* **+£361,656.07**.
* **Total Gross Capital Preserved:** **£1,026,403.54**.
* **Net Projected Benefit:** Against an annual implementation and operating expenditure of £210,000, Sentinel delivers a **net first-year financial benefit of £816,403.54**, representing a **388.8% Net ROI (3.9x)** and a **3-year Net Present Value (NPV @ 8%) of £2,462,536**.
