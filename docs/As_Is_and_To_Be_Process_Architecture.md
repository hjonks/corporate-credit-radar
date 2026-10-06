# Process Architecture & Value Stream Mapping
## Commercial Credit Operations: As-Is vs. To-Be Workflow Architecture
### Project Sentinel

> [!NOTE]
> **Project Context & Methodology Disclosure**
> This repository represents a self-initiated commercial credit risk analytics portfolio case study. The corporate registry data (company names, registration numbers, incorporation dates, SIC codes, and statutory filing records) is sourced directly from public UK Government Companies House bulk registry data (`BasicCompanyData-part1.zip`). Internal account conduct signals (unpaid direct debit counts, overdraft utilization, and hardcore borrowing telemetry) are algorithmically synthesized to illustrate dual-source behavioral surveillance without using confidential bank records.

| Document Attribute | Specification |
|---|---|
| **Document Reference** | PROC-COMM-ARCH-01 |
| **Version** | 2.0 (Reconciled Empirical Calibration) |
| **Author** | Dhruv Chaudhary (Commercial Credit Risk Analytics Portfolio Case Study) |
| **Operational Scope** | Commercial Credit Surveillance, BSRU Workouts, Relationship Management |
| **Effective Date** | September 2026 |
| **Classification** | Commercial Process Architecture & Value Stream Mapping |

---

## 1. As-Is Process Analysis: The Annual Review Cycle & Operational Latency

Under the conventional commercial credit monitoring model, borrower creditworthiness is reviewed on an episodic, annual schedule tied to statutory filing deadlines.

```
+---------------------------------------------------------------------------------------------------+
|                                       AS-IS PROCESS WORKFLOW                                      |
+---------------------------------------------------------------------------------------------------+
[Borrower Financial Year-End (Day 0)]
        |
        | <--- [9-Month Statutory Grace Period: Section 442 Companies Act 2006]
        |      Bank has no updated balance sheet or P&L visibility.
        v
[Annual Accounts Filed at Companies House (Month 9)]
        |
        | <--- [1-2 Month Bureau Ingestion & Processing Lag]
        v
[Credit Bureau Rating Updated (Month 11)]
        |
        | <--- [Scheduling Window for Annual Credit Review]
        v
[Annual Review Conducted by Relationship Manager (Month 12 - 15)]
        |
        +---> Borrower Trading Satisfactorily: Facility Renewed.
        |
        +---> Severe Distress Discovered:
              - Accounts 12-15 months out of date.
              - Working capital exhausted; uncommitted lines fully drawn down.
              - Secondary debentures / asset pledges registered under s.859A.
              - Unmonitored liquidation initiated: Recovery ~25.0% (LGD 75.0%).
+---------------------------------------------------------------------------------------------------+
```

### 1.1 Root Failure Modes in the As-Is Operating Model
1. **Severe Information Latency (9 to 18 Months):** Because credit reviews rely on filed statutory accounts, Relationship Managers evaluate facilities using obsolete financial statements that reflect trading conditions from over a year prior.
2. **Pre-Insolvency Cash Dissipation:** When an unmonitored borrower enters financial distress, management aggressively draws down remaining revolving credit headroom and overdraft limits to meet trade creditor demands. In the portfolio baseline, distressed borrowers draw down an average of 75.0% of undrawn headroom prior to failure.
3. **Alert Fatigue and Lack of Prioritization:** When automated tools simply flag every overdue company without assessing balance sheet exposure materiality, credit officers are overwhelmed by dozens of low-value administrative delays, resulting in ignored notifications.

---

## 2. To-Be Process Architecture: Sentinel Dual-Source Surveillance

Project Sentinel replaces the annual retrospective review with an automated, daily intelligence layer that fuses external Companies House filings with internal account conduct.

```
+---------------------------------------------------------------------------------------------------+
|                                       TO-BE PROCESS WORKFLOW                                      |
+---------------------------------------------------------------------------------------------------+
[Daily Ingestion (05:00 GMT)]
        |
        +---> Companies House Ingestion: Filing due dates, s.859A charges, gazette events
        +---> Core Banking Account Conduct: Unpaid HMRC DDs, consecutive days overdraft pinned >90%
        |
        v
[Sentinel Analytical Sidecar Engine (sentinel_credit_radar.db)]
        |
        +---> Compute Filing Lag Telemetry (s.442 / s.453 delinquency)
        +---> Analyze Balance Sheet Charges & Asset Gearing (s.859A)
        +---> Fuse Internal Account Conduct (Unpaid HMRC DDs, Overdraft Pinning, Hard-Core Flag)
        +---> Generate Composite Distress Score (0 - 100)
        +---> Calculate Materiality Score (Distress Score x Drawn Exposure / 100,000)
        |
        v
[Automated Capacity-Controlled Triage & Routing]
        |
        +----------------------------------------+----------------------------------------+
        |                                        |                                        |
        v                                        v                                        v
[RED TIER: SCORE >= 70]                 [AMBER TIER: SCORE 40 - 69]              [GREEN TIER: SCORE < 40]
11 Files (£6.75M Drawn)                  32 Files (£22.26M Drawn)                 207 Files (£81.50M Drawn)
        |                                        |                                        |
        v                                        v                                        v
[BSRU WORKOUT SQUAD (11 Files)]         [RM INTENSIVE CARE (32 Files)]           [CONTINUOUS SCAN (207 Files)]
- Convene Credit Committee               - Relationship Manager lead              - Daily automated scan
- Clause 14 Information Request          - Request 13-week cash forecast          - No manual touch required
- Curtail uncommitted headroom           - Review management accounts             - Standard surveillance
- Audit collateral priority              - Assess working capital buffer
        |                                        |
        v                                        v
[Consensual Restructuring / Turnaround]  [Early Cure: Prevent Default]
Target Recovery Rate: 45.0% (vs 25% base) 20% Cured Back to Green
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Operational Process Framework

| Lifecycle Stage | Business Focus & Operational Implementation | Key Deliverables & Artifacts |
|---|---|---|
| **Problem Definition** | **Challenge:** Latent detection of commercial defaults leading to 75.0% LGD.<br>**Objective:** Provide 60–90 day lead time while routing cases strictly within BSRU capacity (10–14 files). | Business Requirements Document (BRD), Stakeholder RACI Matrix |
| **Baseline Measurement** | **Baseline:** 270+ days statutory reporting lag; 75.0% unmonitored LGD; £2.25m baseline expected loss on Red cohort; no dual-source account fusion. | Companies House Census Extract (`BasicCompanyData-part1.zip`), Portfolio DDL |
| **Root Cause Analysis** | Core drivers identified: statutory filing lag, uncoordinated internal conduct data, and lack of exposure-weighted triage. | 2D Materiality Matrix, Calibrated Scoring Weights (`02_risk_scoring_views.sql`) |
| **Process Improvement** | Asynchronous sidecar deployment; calibrated scoring yielding 11 Red and 32 Amber files; bilateral Clause 14 notice protocols; BSRU capacity routing. | SQL Scoring Views, Interactive Management MI Console, CSV Triage Master |
| **Ongoing Governance** | Daily automated batch ingestion; compliance SLAs (4-hour credit committee briefing, 48-hour RM outreach); model backtest validation. | Target Operating Model SOP, Model Backtest Report (`model_validation_report.json`) |

---

## 4. Value Stream Comparison: As-Is vs. To-Be Process

| Operational Dimension | As-Is Baseline Model | To-Be Sentinel Engine | Operational Impact |
|---|---|---|---|
| **Distress Detection Latency** | **270 to 365 calendar days** | **24 to 48 hours** | **Detection latency reduced from months to hours** |
| **Intervention Window** | Post-insolvency (-30 to 0 days) | **60 to 90 days pre-default** | **Provides 60+ days runway for workout turnaround** |
| **Workouts Caseload** | Unfiltered alerts (50+ files) | **11 prioritized high-materiality files** | **Aligned with 10–14 file specialist capacity** |
| **Bilateral Contractual Alignment** | Ad-hoc uncoordinated actions | **Standard Terms Clause 14 notice protocols** | **Protects bank against wrongful acceleration claims** |
| **Core Systems Impact** | Multi-year core ledger rewrite | **Asynchronous read-only sidecar** | **Zero modifications required to core banking platforms** |
| **Distressed Workout Recovery** | **25.0%** in late liquidation (LGD 75%) | **45.0%** in consensual workout (LGD 55%) | **+20.0 percentage point recovery uplift** |
| **Net Financial Preserved Value** | Baseline Red EL: £2.25M | Preserved capital: **+£816,404/yr** | **388.8% Net ROI (3.9x) | 3-Year NPV: £2.46M** |

---

## 5. Enterprise Integration Architecture (The Sidecar Pattern)

```
+---------------------------------------------------------------------------------------------------+
|                                ENTERPRISE INTEGRATION ARCHITECTURE                                |
+---------------------------------------------------------------------------------------------------+
                                                                                                    
 [Companies House Bulk / API Stream]           [Core Banking Transaction Telemetry]                 
       |                                             |                                              
       | (Daily Delta Extract)                       | (Overnight Read-Only Conduct Export)         
       v                                             v                                              
+-------------------------------------------------------------------------------------------------+ 
|                          PROJECT SENTINEL ANALYTICAL SIDECAR ENGINE                             | 
|                                                                                                 | 
|  1. Ingestion Layer: Normalizes Profiles, Charges, Accounts Due Dates & Account Conduct          | 
|  2. Resolution Module: Consolidates Corporate Groups & Multi-Facility Debt Exposure              | 
|  3. Analytical Views: Computes Calibrated Composite Distress Score (0 - 100)                     | 
|  4. Prioritization Engine: Enforces Materiality Scoring & BSRU 11-File Queue Routing            | 
+-------------------------------------------------------------------------------------------------+ 
                                             |                                                      
                                             v (Structured REST / Webhook Events)                   
+-------------------------------------------------------------------------------------------------+ 
|                         CRM & WORKFLOW ORCHESTRATION (Salesforce FSC / Pega)                    | 
|                                                                                                 | 
|  - Red Tier Dossier Dispatch  ---> Special Situations Credit Committee (Clause 14 Info Call)     | 
|  - Amber Tier Dossier Dispatch ---> Regional Commercial Relationship Directors (RM Review)       | 
|  - Executive Management MI    ---> Head of Commercial Lending & Credit Risk Committee             | 
+-------------------------------------------------------------------------------------------------+ 
```

*Architecture Principle:* Project Sentinel operates strictly on a read-only integration model with external corporate registries and internal core transaction ledgers. All credit actions and line adjustments are executed through standard bank workflow tools with appropriate human credit underwriter authorization.
