# Executive Presentation: Early-Warning Commercial Credit Surveillance
## Project Sentinel: Integrating Companies House Registry Filings with Account Conduct
### Commercial Credit Operations & Risk Committee Briefing

> [!NOTE]
> **Project Context & Methodology Disclosure**
> This repository represents a self-initiated commercial credit risk analytics portfolio case study. The corporate registry data (company names, registration numbers, incorporation dates, SIC codes, and statutory filing records) is sourced directly from public UK Government Companies House bulk registry data (`BasicCompanyData-part1.zip`). Internal account conduct signals (unpaid direct debit counts, overdraft utilization, and hardcore borrowing telemetry) are algorithmically synthesized to illustrate dual-source behavioral surveillance without using confidential bank records.

| Document Attribute | Specification |
|---|---|
| **Document Reference** | PRES-COMM-2026-03 |
| **Author** | Dhruv Chaudhary (Commercial Credit Risk Analytics Portfolio Case Study) |
| **Presented To** | Hypothetical Business Persona: J. Thornton (Regional Director - Commercial Lending Operations), Credit Risk Committee |
| **Effective Date** | September 2026 |
| **Classification** | Commercial Lending Operations Presentation |

---

### Slide 1: Executive Overview & Business Case
* **Project Objective:** Establish an automated, continuous early-warning surveillance engine for the commercial loan book by connecting official Companies House statutory registry filings with internal transactional account conduct.
* **Core Problem:** The 9–18 month statutory delay in annual accounts filings leaves relationship managers without timely visibility into emerging corporate distress.
* **Simulated Portfolio Impact:** Projected **£816,404 net annual reduction in credit losses** across an illustrative £110.51M commercial loan portfolio simulation (£210k implementation cost, **388.8% Net ROI / 3.9x**; **3-year NPV @ 8% of £2.46M**).

---

### Slide 2: Market Context & Portfolio Performance
* **Economic Backdrop:** Sustained interest rates, margin compression, and supply chain working capital friction continue to impact UK manufacturing, haulage, construction, and wholesale businesses.
* **Corporate Default Risk:** UK corporate liquidations remain elevated, increasing default vulnerability across middle-market and SME debt portfolios.
* **Operational Goal:** Detect operational and statutory deterioration 60 to 90 days before formal insolvency proceedings commence, enabling timely consensual workout intervention.

---

### Slide 3: Operational Constraints in Conventional Monitoring
* **Annual Accounts Latency:** Under Section 442 of the Companies Act 2006, borrowers have up to 9 months post-year-end to submit statutory accounts, resulting in review data that is up to 18 months old.
* **Alert Quality & Team Capacity:** Basic heuristic screening generates excessive false positives, overwhelming the Business Support & Recoveries Unit (BSRU capacity: 10–14 concurrent intensive files).
* **Bilateral Contractual Compliance:** Facilities cannot be arbitrarily restricted; interventions must follow standard bilateral commercial lending terms and notice procedures to avoid potential wrongful acceleration counter-claims.

---

### Slide 4: Proposed Solution: Project Sentinel
* **Core Functionality:** An asynchronous surveillance sidecar that monitors official Companies House data feeds and fuses them with internal commercial account conduct.
* **Key Risk Indicators:**
  * Statutory accounts delinquency (calendar days overdue beyond statutory deadline).
  * Section 859A registered charges and cumulative collateral encumbrance.
  * Internal payment conduct (unpaid HMRC VAT/PAYE direct debits and consecutive days pinned near overdraft limits).
  * Chronic working capital dependency flags.
  * Formal insolvency and London Gazette strike-off notices.

---

### Slide 5: System Architecture & Integration Pattern
* **Sidecar Deployment:** Operates as an external analytical engine, eliminating the need for costly and complex modifications to legacy core banking transaction engines.
* **Data Flow:**
  * Daily ingestion of Companies House updates and overnight internal account transaction deltas.
  * Analytical scoring executed in a dedicated relational data store (`sentinel_credit_radar.db`).
  * Structured triage dossiers pushed directly to Salesforce / CRM and workout queues for officer action.
* **Governance:** All credit interventions require formal officer approval; the system operates strictly on an advisory basis without automated write-backs.

---

### Slide 6: Risk Scoring Methodology: Dual Telemetry Fusion
* **Rationale:** Statutory filing delays often stem from routine administrative delays. Genuine distress occurs when filing delays coincide with internal payment friction.
* **Score Allocation (0–100 Scale):**
  * Accounts overdue >60 days: **+25 pts** (22–60 days: **+15 pts**, 1–21 days: **+5 pts**)
  * Confirmation statement overdue >30 days: **+10 pts** (15–30 days: **+5 pts**)
  * Formal insolvency / Administration filing: **+35 pts**
  * Collateral gearing (charges >= 4): **+10 pts** (2–3 charges: **+5 pts**)
  * Unpaid HMRC direct debits (>=3 in 90 days): **+30 pts** (1–2 in 90 days: **+15 pts**)
  * Overdraft pinned >=90% limit for >=60 days: **+25 pts** (30–59 days: **+15 pts**)
  * Chronic working capital dependency (`hard_core_flag = 1`): **+10 pts**
* **Outcome:** Fused scores reflect confirmed operational and liquidity distress, eliminating false alarms.

---

### Slide 7: Portfolio Reconciliation & Risk Distribution
* **Total Portfolio Evaluated:** **£110.51m** drawn exposure across 250 borrowing facilities (**£207.85M** committed limits, **£97.34M** undrawn headroom).
* **Green Tier (Standard):** 207 borrowers (82.8% | £81.50M drawn) | Score < 40 | Automated continuous monitoring.
* **Amber Tier (Elevated):** 32 borrowers (12.8% | £22.26M drawn) | Score 40–69 | Relationship Manager structured review & 13-week cash review.
* **Red Tier (Critical):** 11 borrowers (4.4% | £6.75M drawn) | Score >= 70 | BSRU specialist workout squad triage.

---

### Slide 8: Workouts Capacity & Materiality Prioritization
* **Operational Constraint:** The BSRU workout team operates with dedicated specialists, capable of handling 10 to 14 intensive files concurrently.
* **Prioritization Formula:** Accounts are ranked by Materiality Score:
  $$	ext{Materiality Score} = rac{	ext{Distress Score} 	imes 	ext{Drawn Exposure}}{100,000}$$
* **Operational Queue Allocation:**
  * **BSRU Workout Squad:** **11 files (£6.75M drawn)** | Score >= 70 and drawn balance >= £350,000.
  * **Special Situations Watch:** **0 files (£0.00 drawn)** | Score >= 70 and drawn balance < £350,000.
  * **RM Intensive Care:** **32 files (£22.26M drawn)** | Score 40–69.
  * **Standard Surveillance:** **207 files (£81.50M drawn)** | Score < 40.
* **Result:** Workload matches BSRU capacity while covering 100% of Red Tier financial exposure.

---

### Slide 9: Bilateral Credit Action Protocol
* **Contractual Alignment:** Replaces unilateral automated facility restrictions with legally verified notice workflows under standard UK bilateral commercial loan agreements.
* **Standard Terms Clause 14 Information Demand:**
  * Empowers Relationship Managers and workout officers to demand rolling 13-week cash flow forecasts, aged debtor ledgers, and management accounts within 3 business days.
* **Discretionary Headroom Curtailment:**
  * Leverages on-demand overdraft facility terms to proactively freeze uncommitted discretionary headroom, preventing distressed cash dissipation before insolvency.

---

### Slide 10: Cross-Sectional Registry Association Study & Diagnostic Signal Benchmark
* **Data Source:** Evaluated against 1,200 commercial companies in the official UK Companies House census archive (1,000 active, 200 in administration/liquidation).
* **Model Discrimination:** **ROC-AUC: 0.8604** (Gini Coefficient: **0.7208**), confirming strong rank-ordering discrimination.
* **Statutory Warning Lead Time:** Median **213 days** (Interquartile Range: 124–275 days) ahead of formal insolvency appointments.
* **Insolvency Capture Rate:** **69.0%** of insolvent entities flagged via observable statutory delinquency prior to formal winding-up.
* **Empirical Default Probabilities:** Red: **42.8%**, Amber: **12.5%**, Green: **1.4%**.

---

### Slide 11: Capital Preservation & Loss Mitigation Breakdown
On the £6.75M Red Tier exposure:
* **Unmitigated Baseline Red Expected Loss (75.0% LGD in late insolvency, 42.8% PD):** **£2,253,276.48**.
* **Mitigated Capital Recovered (45.5% loss reduction via early intervention):** **£1,026,403.54**.
  * *Consensual restructuring & turnaround (+20% recovery uplift, LGD 75% -> 55%):* **+£577,646.91**.
  * *Curtailment of discretionary undrawn overdraft headroom (£271k prevented draw):* **+£87,100.55**.
  * *Amber early remediation & default prevention (curing 20% of Amber cohort):* **+£361,656.07**.
* **Net Residual Distressed Expected Loss:** **£1,226,872.94**.

---

### Slide 12: Cost-Benefit Analysis & Return on Investment
* **Annual Operating & Implementation Investment:** **£210,000**.
* **Net Year-1 Capital Preserved:** **£816,403.54**.
* **First-Year Financial ROI:** **388.8% Net ROI (3.9x)**.
* **Payback Period:** Less than 3 months.
* **Three-Year Net Present Value (NPV @ 8% discount rate):** **£2,462,536**.

---

### Slide 13: 90-Day Implementation Timeline
* **Weeks 1–4 (Core Setup):** Establish Companies House automated ingestion and overnight transactional conduct data feeds.
* **Weeks 5–8 (Integration & Scoring):** Deploy SQL analytical views, calibrate score weights, and configure CRM task dispatches into Salesforce / workflow queues.
* **Weeks 9–12 (Enablement & Go-Live):** Complete operational training for BSRU officers and commercial RMs; execute parallel-run validation.
* **Day 90:** Full operational go-live across regional commercial portfolios.

---

### Slide 14: Recommended Next Steps & Sign-off
* **Action Requested:**
  1. Approve the **£210,000 Year-1 budget** for Project Sentinel sidecar implementation.
  2. Endorse the **Commercial Credit Surveillance SOP** and bilateral notice protocols.
  3. Authorize transition to Phase 2 technical integration.
