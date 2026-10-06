# Standard Operating Procedure (SOP)
## Commercial Credit Surveillance & Early-Warning Triage Policy
### Target Operating Model (TOM), Bilateral Protocols, and Workouts Governance

> [!NOTE]
> **Project Context & Methodology Disclosure**
> This repository represents a self-initiated commercial credit risk analytics portfolio case study. The corporate registry data (company names, registration numbers, incorporation dates, SIC codes, and statutory filing records) is sourced directly from public UK Government Companies House bulk registry data (`BasicCompanyData-part1.zip`). Internal account conduct signals (unpaid direct debit counts, overdraft utilization, and hardcore borrowing telemetry) are algorithmically synthesized to illustrate dual-source behavioral surveillance without using confidential bank records.

| Document Attribute | Specification |
|---|---|
| **Document Reference** | SOP-COMM-POL-02 |
| **Version** | 2.0 (Reconciled Empirical Calibration) |
| **Policy Owner** | Commercial Credit Risk Operations Committee |
| **Operational Leads** | Hypothetical Business Persona: J. Thornton (Regional Operations Director), Lead Workout Director (BSRU) |
| **Target Audience** | Commercial Relationship Directors, Credit Risk Underwriters, BSRU Workout Squad |
| **Effective Date** | September 2026 |
| **Classification** | Commercial Credit Policy & Target Operating Model |

---

## 1. Credit Policy Architecture & Scoring Matrix

Project Sentinel computes an auditable **Composite Distress Score (0 to 100)** by fusing public statutory filing records from Companies House with internal transactional account conduct telemetry.

### 1.1 Risk Factor Weighting Matrix

| Risk Dimension | Operational Indicator | Weight | Data Source | Operational Rationale |
|---|---|---|---|---|
| **Statutory Delinquency** | Accounts overdue by >60 calendar days | **+25 pts** | Companies House (s.453 Companies Act) | Prolonged filing delays frequently indicate unresolved audit qualifications or cash flow distress. |
| **Statutory Delinquency** | Accounts overdue by 22 to 60 calendar days | **+15 pts** | Companies House (s.442 Companies Act) | Moderate administrative delay; warrants active relationship manager contact. |
| **Statutory Delinquency** | Accounts overdue by 1 to 21 calendar days | **+5 pts** | Companies House (Grace period) | Early warning of potential statutory accounting delay. |
| **Statutory Delinquency** | Confirmation Statement overdue by >30 days | **+10 pts** | Companies House (s.853A Companies Act) | Failure to maintain baseline statutory corporate governance. |
| **Statutory Delinquency** | Confirmation Statement overdue by 15 to 30 days | **+5 pts** | Companies House (s.853A Companies Act) | Initial administrative non-compliance. |
| **Statutory Insolvency** | Formal Administration / Liquidation | **+35 pts** | London Gazette / Companies House | Formal insolvency or restructuring proceeding initiated. |
| **Collateral Gearing** | Outstanding charges count >= 4 | **+10 pts** | Charges Register (s.859A Companies Act) | Balance sheet asset encumbrance diluting unencumbered asset cover. |
| **Collateral Gearing** | Outstanding charges count 2 to 3 | **+5 pts** | Charges Register (s.859A Companies Act) | Multiple existing charges registered against the entity. |
| **Internal Conduct** | Unpaid Direct Debits >= 3 in 90 days | **+30 pts** | Core Account Telemetry (HMRC VAT/PAYE) | Primary leading indicator of cash exhaustion and statutory tax delinquency. |
| **Internal Conduct** | Unpaid Direct Debits 1 to 2 in 90 days | **+15 pts** | Core Account Telemetry (Supplier DDs) | Early indicator of trade payment friction and liquidity tightness. |
| **Internal Conduct** | Overdraft Pinned >=90% Limit for >=60 days | **+25 pts** | Core Account Telemetry | Continuous hard-core overdraft utilization without swinging into credit. |
| **Internal Conduct** | Overdraft Pinned >=90% Limit for 30 to 59 days | **+15 pts** | Core Account Telemetry | Emerging reliance on working capital facilities for permanent funding. |
| **Internal Conduct** | Overdraft Pinned >=90% Limit for 14 to 29 days | **+5 pts** | Core Account Telemetry | Initial sign of elevated facility utilization. |
| **Internal Conduct** | Chronic Borrowing Dependency (`hard_core_flag = 1`) | **+10 pts** | Core Account Telemetry | Chronic reliance on working capital lines without clearing seasonal cycles. |

*Composite raw score is capped at 100 points.*

---

## 2. Target Operating Model (TOM) Workflow

```
+---------------------------------------------------------------------------------------------------+
|                                  SENTINEL TARGET OPERATING MODEL                                  |
+---------------------------------------------------------------------------------------------------+
                                                  |
           +--------------------------------------+--------------------------------------+
           |                                                                             |
           v                                                                             v
[ COMPANIES HOUSE REGISTRY DELTA ]                                       [ INTERNAL CORE ACCOUNT TELEMETRY ]
  - Accounts Filing Deadlines                                              - Unpaid HMRC & Supplier DDs
  - Confirmation Statement Due Dates                                       - Consecutive Overdraft Pinned Days
  - Section 859A Charges Register                                          - Hard-Core Borrowing Flags
           |                                                                             |
           +--------------------------------------+--------------------------------------+
                                                  |
                                                  v
                              [ PROJECT SENTINEL SIDECAR ENGINE ]
                                - Fuses Statutory & Conduct Telemetry
                                - Computes Composite Distress Score (0-100)
                                - Computes Exposure Materiality Index
                                                  |
           +--------------------------------------+--------------------------------------+
           |                                      |                                      |
           v                                      v                                      v
[ RED TIER: SCORE >= 70 ]              [ AMBER TIER: SCORE 40 - 69 ]          [ GREEN TIER: SCORE < 40 ]
  11 Borrowers (£6.75M Drawn)            32 Borrowers (£22.26M Drawn)           207 Borrowers (£81.50M Drawn)
  BSRU Specialist Workout Squad          RM Intensive Care Queue                Continuous Automated Scan
  Bilateral Information Covenant         Structured 13-Week Cash Review         Routine Monitoring
```

---

## 3. Operational Playbooks: Standard Operating Procedures

### 3.1 Green Tier (Score < 40): Standard Surveillance
* **Portfolio Coverage:** 207 commercial facilities (£81.50m drawn exposure | 73.8% of drawn book).
* **Monitoring Cadence:** Automated 24-hour sidecar scan against daily Companies House updates and account transactions.
* **Operational Action:** Normal annual credit review cycle. No manual relationship manager intervention required.

---

### 3.2 Amber Tier (Score 40–69): Relationship Manager Intensive Care
* **Portfolio Coverage:** 32 commercial facilities (£22.26m drawn exposure | 20.1% of drawn book).
* **Operational Trigger:** Filing delays exceeding 21 days or payment friction (1-2 bounced direct debits, elevated overdraft pinning).
* **Governing Procedure:** **Standard Terms Clause 14 Information Request & Structured Review**.
* **Action Steps:**
  1. **Triage Packet Delivery:** Sentinel delivers an Amber Triage Dossier to the primary Relationship Director via CRM within 24 hours of tier entry.
  2. **Client Outreach (Within 48 Hours):** Relationship Director contacts the borrower's finance director, referencing information undertakings in standard bilateral facility documentation.
  3. **Information Request Package:** The borrower is formally requested to provide:
     * Latest 13-week rolling cash flow forecast.
     * Most recent monthly management accounts (P&L and balance sheet).
     * Aged debtors and creditors listing.
     * Written confirmation from auditors regarding statutory filing timeline.
  4. **Credit Discretion Freeze:** Discretionary credit approvals and uncommitted limit increases are placed on hold pending review of requested management information.

---

### 3.3 Red Tier (Score >= 70): Workouts & Special Situations
* **Portfolio Coverage:** 11 commercial facilities (£6.75m drawn exposure | 6.1% of drawn book).
* **Operational Trigger:** Score >= 70, reflecting severe filing delinquency (>60 days), multiple unpaid HMRC direct debits, and pinned overdrafts.
* **Governing Procedure:** **Bilateral Reservation of Rights & Consensual Workout Protocol**.
* **Action Steps:**
  1. **Credit Committee Escalation (Within 4 Hours):** Convene an emergency triage review including J. Thornton (Regional Director - Commercial Lending Operations), the assigned BSRU Workout Officer, and panel legal counsel.
  2. **Bilateral Information Demand (Within 24 Hours):** Issue formal Information Covenant Request under Standard Commercial Terms (13-week cash flow forecast & debtor ledger within 3 business days).
  3. **Collateral Audit & Perfection Review (Days 1–3):**
     * Review the Companies House charges register to confirm the bank's first fixed and floating charge priority under the existing debenture.
     * Verify debenture registration under Companies Act Section 859A.
     * Review assets to ensure no unpermitted secondary pledges exist.
  4. **Uncommitted Headroom Freeze:** Under standard bilateral terms (overdrafts repayable on demand; revolving drawdowns subject to no-material-adverse-change conditions), immediately curtail uncommitted discretionary headroom to contain loss exposure.
  5. **Consensual Workout Engagement (Days 4–21):** Initiate consensual turnaround discussions, exploring HMRC Time-to-Pay arrangements, debtor book realization, or solvent business sale to maximize recovery (targeting 45% recovery vs 25% unmonitored salvage).

---

## 4. BSRU Operational Capacity & Value-at-Risk Materiality Routing

The Business Support & Recoveries Unit (BSRU) operates with dedicated workout officers, establishing an operational capacity of **10 to 14 concurrent intensive restructuring files**.

### 4.1 Value-at-Risk Materiality Index
To prioritize cases where potential loss is greatest, Sentinel evaluates:
$$	ext{Materiality Exposure Score} = rac{	ext{Distress Score} 	imes 	ext{Current Drawn Exposure (£)}}{100,000}$$

### 4.2 Departmental Routing Breakdown

| Department / Queue | Qualification Criteria | Account Count | Total Drawn Exposure | Operational Handling |
|---|---|---|---|---|
| **BSRU Workout Squad** | Score >= 70 AND Drawn Exposure >= £350,000 | **11 files** | **£6,748,211.61** | **Dedicated Workout Officer:** Daily cash flow tracking, debenture audit, consensual turnaround. |
| **Special Situations Watch** | Score >= 70 AND Drawn Exposure < £350,000 | **0 files** | **£           0.00** | **Credit Officer Watchlist:** Weekly monitoring; uncommitted lines capped. |
| **RM Intensive Care** | Score 40–69 | **32 files** | **£22,255,758.13** | **Relationship Manager Lead:** Standard Terms Clause 14 13-week cash flow request. |
| **Standard Surveillance** | Score < 40 | **207 files** | **£81,502,331.23** | **Automated Surveillance:** Continuous daily registry and conduct scanning. |

*Operational Result:* The BSRU Workout Squad receives exactly **11 prioritized files**, matching specialist team capacity while covering **100% of the £6.75M Red Tier drawn exposure**.

---

## 5. Contractual Safe Harbors: Bilateral Commercial Facility Alignment

### 5.1 Mitigation of Wrongful Acceleration Claims
Under English commercial contract law, arbitrarily cancelling committed credit lines or accelerating term balances without complying with contractual notice periods constitutes an anticipatory breach of contract. Borrowers whose banking facilities are improperly terminated may assert significant counter-claims for consequential trading losses.

### 5.2 Key Bilateral Agreement Principles
* **Standard Information Undertakings (Clause 14):** Provides contractual standing to demand rolling cash flow forecasts, aged debtor ledgers, and explanations for statutory accounting delays.
* **On-Demand Overdraft Nature:** Standard commercial overdraft terms confirm that overdraft facilities are repayable on demand, permitting immediate discretionary headroom curtailment without contractual breach.
* **Committed Facility Draw Conditions:** Committed revolving credit facilities specify that further drawdowns are conditional upon the absence of a Potential or actual Event of Default or Material Adverse Change (MAC).

### 5.3 Function of the Reservation of Rights Protocol
When an account enters the Red Tier, the bank issues a formal Reservation of Rights communication to:
* Acknowledge awareness of the statutory delay or payment friction.
* Formally reserve all rights and contractual remedies under the facility agreement.
* Preserve legal standing without prematurely terminating the loan, allowing turnaround negotiations to proceed from a secure contractual position.
