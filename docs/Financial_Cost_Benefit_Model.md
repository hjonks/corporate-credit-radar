# Financial Cost-Benefit & Loss Mitigation Model
## Commercial Credit Risk Analytics: Portfolio Capital Preservation
### Project Sentinel

> [!NOTE]
> **Project Context & Methodology Disclosure**
> This repository represents a self-initiated commercial credit risk analytics portfolio case study. The corporate registry data (company names, registration numbers, incorporation dates, SIC codes, and statutory filing records) is sourced directly from public UK Government Companies House bulk registry data (`BasicCompanyData-part1.zip`). Internal account conduct signals (unpaid direct debit counts, overdraft utilization, and hardcore borrowing telemetry) are algorithmically synthesized to illustrate dual-source behavioral surveillance without using confidential bank records.

| Document Attribute | Specification |
|---|---|
| **Document Reference** | FIN-COMM-MOD-01 |
| **Version** | 2.0 (Reconciled Empirical Calibration) |
| **Author** | Dhruv Chaudhary (Commercial Credit Risk Analytics Portfolio Case Study) |
| **Business Sponsor** | Hypothetical Business Persona: J. Thornton (Regional Director - Commercial Lending Operations) |
| **Portfolio Base** | UK Commercial SME & Mid-Market Loan Book (Illustrative Simulation: £110.51M Drawn / £207.85M Committed) |
| **Effective Date** | September 2026 |
| **Classification** | Commercial Credit Risk Analytics |

---

## 1. Portfolio Parameters & Baseline Profile

The financial model is evaluated against an illustrative regional commercial loan portfolio simulation (`sentinel_credit_radar.db`), comprising 250 active UK commercial trading companies across manufacturing, construction, wholesale/logistics, and professional services.

### 1.1 Commercial Loan Book Composition

| Portfolio Metric | Value | Operational Context |
|---|---|---|
| **Total Committed Facility Limits** | **£207,845,000.00** | Total contractual credit limits across all 250 commercial borrowers. |
| **Total Current Drawn Debt Exposure** | **£110,506,300.97** | Active balance sheet debt exposure. |
| **Total Undrawn Committed Headroom** | **£97,338,699.03** | Total unutilized contractual lines across the portfolio. |
| **Average Portfolio Utilization** | **53.2%** | Blended utilization across revolving lines, overdrafts, and term debt. |
| **Borrower Count** | **250 commercial entities** | Core SMEs (£250k–£950k) and mid-market (£1.5m–£3.5m) enterprises. |
| **Regional Distribution** | Nationwide UK | London & South East (38.0%), Midlands (15.6%), East of England (11.6%), North West (11.2%), Yorkshire & Humber (9.6%), South West (4.8%), North East (4.0%), Scotland (4.0%), Wales (1.2%). |

---

## 2. Risk Tier Exposure at Default (EAD) & Empirical Calibration

The portfolio is triaged into three operational risk tiers based on the fused Composite Distress Index (combining statutory filing lag, confirmation statement delinquency, charges encumbrance, and internal account conduct):

```
+-------------------------------------------------------------------------------------------------------------------+
|                                          PORTFOLIO EXPOSURE BY RISK TIER                                          |
+-------------------+------------+---------------------+-------------------+---------------------+------------------+
| Operational Tier  | Borrowers  | Total Drawn (£)     | Total Limit (£)   | Undrawn Headroom (£)| Assigned Routing |
+-------------------+------------+---------------------+-------------------+---------------------+------------------+
| RED_CRITICAL      | 11         | £  6,748,211.61     | £  7,110,000.00   | £   361,788.39      | BSRU Squad (11)  |
| AMBER_ELEVATED    | 32         | £ 22,255,758.13     | £ 25,951,000.00   | £ 3,695,241.87      | RM Intensive Care|
| GREEN_STANDARD    | 207        | £ 81,502,331.23     | £174,784,000.00   | £93,281,668.77      | Auto-Surveillance|
+-------------------+------------+---------------------+-------------------+---------------------+------------------+
| TOTAL PORTFOLIO   | 250        | £110,506,300.97     | £207,845,000.00   | £97,338,699.03      | Full Portfolio   |
+-------------------+------------+---------------------+-------------------+---------------------+------------------+
```

### 2.1 Cross-Sectional Registry Association Study & Supervisory PD Calibration

Model discrimination and calibration parameters are empirically validated against official UK Companies House historical insolvency records (1,200 companies evaluated):
* **Model ROC-AUC:** **0.8604** (Gini Coefficient: **0.7208**), confirming strong rank-ordering discrimination.
* **Insolvency Capture Rate:** **69.0%** of insolvent companies exhibited observable statutory filing delinquencies prior to formal winding-up.
* **Warning Lead Time:** Median **213 days** (Interquartile Range: 124–275 days) ahead of formal insolvency appointments.
* **Calibrated Default Rates (PD):**
  * **Red Tier PD:** **42.8%** (reflecting severe multi-signal distress and working capital exhaustion).
  * **Amber Tier PD:** **12.5%** (reflecting emerging operational or statutory strain).
  * **Green Tier PD:** **1.4%** (reflecting baseline prime commercial corporate default rates).

---

## 3. Loss Mitigation Analysis: Baseline vs. Early Surveillance

Loss mitigation is modeled using the standard Basel Expected Loss (EL) framework:
$$\text{Expected Loss (EL)} = \text{Exposure at Default (EAD)} \times \text{Probability of Default (PD)} \times \text{Loss Given Default (LGD)}$$

### 3.1 Baseline Scenario (As-Is: Conventional Late Detection / Annual Review)
Under conventional annual review workflows, deteriorating borrowers are detected only after formal winding-up petitions, court administration orders, or sudden cash exhaustion:
* **Drawn Exposure in Critical Distress (Red Tier):** £6,748,211.61 across 11 facilities.
* **Distressed Undrawn Drawdown:** In the absence of proactive surveillance, distressed borrowers aggressively draw down uncommitted overdrafts and revolving lines before insolvency. Historical empirical studies indicate an average **75.0%** drawdown of undrawn headroom prior to failure:
  $$\text{Additional Distressed Drawdown} = £361,788.39 \times 75.0\% = £271,341.29$$
  $$\text{Baseline Red EAD} = £6,748,211.61 + £271,341.29 = £7,019,552.90$$
* **Baseline Loss Given Default (LGD) in Unmonitored Liquidation:** **75.0%** (i.e. only 25.0% asset recovery due to fire-sale liquidation, unmonitored dissipation of book debts, priority HMRC preferential claims, and heavy insolvency practitioner fees).
* **Baseline Expected Loss on Red Tier:**
  $$\text{Baseline Red EL} = £7,019,552.90 \times 42.8\% \times 75.0\% = \mathbf{£2,253,276.48}$$

---

### 3.2 Sentinel Early-Surveillance Scenario (To-Be: 60–90 Day Behavioral Lead Time)
With early warning of statutory filing lag and internal account conduct strain (bounced direct debits, pinned overdrafts), the bank engages 60 to 90 days ahead of formal insolvency. Capital is preserved across three legally defensible, bilateral operational mechanisms:

#### Mechanism 1: Consensual Turnaround & Asset Recovery Uplift
* **Operational Rationale:** Early intervention enables the bank's Special Situations / BSRU workout squad to engage while the borrower is still a solvent going concern. Proactive covenant resets, structured debtor book collections, and solvent asset dispositions avoid forced liquidations.
* **Legal Robustness:** Does **NOT** rely on taking vulnerable new floating charges within the 12-month insolvency clawback window (Insolvency Act 1986 s245/s239 voidable preferences). It operates entirely through existing security debentures, bilateral standstill agreements, and consensual cash management.
* **Recovery Impact:** Increases recovery from 25.0% (LGD 75.0%) to 45.0% (LGD 55.0%), delivering a **+20.0% recovery uplift** on defaulting drawn exposure.
* **Capital Preserved:**
  $$\text{Preserved}_{\text{Uplift}} = £6,748,211.61 \times 42.8\% \times (75.0\% - 55.0\%) = \mathbf{£577,646.91}$$

#### Mechanism 2: Discretionary Undrawn Headroom Containment
* **Operational Rationale:** Proactive monitoring detects chronic overdraft pinning and unpaid direct debits. Under standard UK bilateral commercial banking terms, overdraft facilities are repayable on demand, and revolving credit drawdowns are subject to no-material-adverse-change conditions. The bank proactively curtails or freezes discretionary undrawn lines.
* **Capital Preserved:** Completely prevents the £271,341.29 distressed pre-insolvency drawdown from becoming bad debt. Valued at unmonitored baseline loss parameters (PD 42.8%, LGD 75.0%):
  $$\text{Preserved}_{\text{Headroom}} = £271,341.29 \times 42.8\% \times 75.0\% = \mathbf{£87,100.55}$$

#### Mechanism 3: Amber Early Remediation & Contagion Prevention
* **Operational Rationale:** For the 32 Amber borrowers (£22.26m drawn, baseline PD 12.5%, LGD 65.0%), early frontline RM outreach and 13-week cash flow monitoring cures **20.0%** of emerging distress cases back to Green, preventing migration into default.
* **Capital Preserved:**
  $$\text{Preserved}_{\text{Amber}} = £22,255,758.13 \times 12.5\% \times 20.0\% \times 65.0\% = \mathbf{£361,656.07}$$

---

### 3.3 Total Annual Capital Preserved

```
+---------------------------------------------------------------------------------------------------+
|                                LOSS MITIGATION RECONCILIATION WATERFALL                            |
+-------------------------------------------------------------+-------------------+-----------------+
| Loss Mitigation Component                                   | Valuation Method  | Capital Value   |
+-------------------------------------------------------------+-------------------+-----------------+
| 1. Consensual Restructuring & Recovery Uplift (+20% LGD)   | EAD x PD x dLGD   | £   577,646.91  |
| 2. Discretionary Undrawn Headroom Containment               | dDraw x PD x LGD  | £    87,100.55  |
| 3. Amber Early Remediation & Default Prevention             | EAD x PD x Cure%  | £   361,656.07  |
+-------------------------------------------------------------+-------------------+-----------------+
| TOTAL GROSS ANNUAL CAPITAL PRESERVED                        | Exact Sum         | £ 1,026,403.54  |
+-------------------------------------------------------------+-------------------+-----------------+
```

* **Red Tier Expected Loss Mitigation:**
  * **Baseline Red Unmonitored Expected Loss:** **£2,253,276.48**
  * **Red Capital Preserved (Workout Uplift + Headroom Containment):** **£664,747.46** (£577,646.91 + £87,100.55)
  * **Net Red Expected Loss After Surveillance:** **£1,588,529.02**
  * **Red Loss Mitigation Efficiency:** **29.5%** reduction in unmonitored default losses (£664,747.46 / £2,253,276.48).

* **Amber Tier Expected Loss Mitigation:**
  * **Baseline Amber Unmonitored Expected Loss:** **£1,808,280.35** (£22,255,758.13 drawn × 12.5% PD × 65.0% LGD)
  * **Amber Capital Preserved (Early RM Cure):** **£361,656.07**
  * **Net Amber Expected Loss After Surveillance:** **£1,446,624.28**
  * **Amber Loss Mitigation Efficiency:** **20.0%** reduction in emerging default losses.

* **Consolidated Distressed Portfolio Performance:**
  * **Combined Distressed Baseline Expected Loss:** **£4,061,556.83** (£2,253,276.48 Red + £1,808,280.35 Amber)
  * **Total Gross Annual Capital Preserved:** **£1,026,403.54**
  * **Net Distressed Expected Loss After Sentinel Surveillance:** **£3,035,153.29**
  * **Consolidated Portfolio Loss Mitigation Efficiency:** **25.3%** (£1,026,403.54 / £4,061,556.83).

---

## 4. Cost Structure & Implementation Investment

Sentinel is engineered as an asynchronous, read-only "sidecar" intelligence engine, querying replica database views and external registry feeds without requiring modifications to legacy core banking transaction engines:

| Investment Category | Year 1 (Capex + Opex) | Year 2 (Opex) | Year 3 (Opex) | Operational Description |
|---|---|---|---|---|
| **Data Pipeline & Schema Engineering** | £75,000 | £15,000 | £15,000 | Python/SQL ingestion pipeline, relational schema, and indexing |
| **Companies House Registry Data Integration** | £25,000 | £25,000 | £25,000 | Bulk census ingestion and delta streaming infrastructure |
| **Workflow Connectors (CRM / Triage)** | £60,000 | £12,000 | £12,000 | Automated task dispatches, RM workflow queues, and MI console |
| **Credit Risk Training & Staff Enablement** | £30,000 | £8,000 | £8,000 | Operational training for BSRU officers and commercial RMs |
| **Model Governance & Independent Validation** | £20,000 | £10,000 | £10,000 | Independent statistical validation and audit documentation |
| **TOTAL ANNUAL EXPENDITURE** | **£210,000** | **£70,000** | **£70,000** | **Fully Loaded Sidecar Operational Cost** |

---

## 5. Financial Returns, ROI & Net Present Value (NPV)

### 5.1 First-Year Financial Performance
* **Gross Capital Preserved:** £1,026,403.54
* **First-Year Investment:** £210,000.00
* **Net First-Year Value Preserved:**
  $$\text{Net First-Year Benefit} = £1,026,403.54 - £210,000.00 = \mathbf{+£816,403.54}$$
* **First-Year Net ROI:**
  $$\text{First-Year Net ROI} = \frac{£816,403.54}{£210,000.00} \times 100\% = \mathbf{388.8\% \quad (3.9\text{x})}$$
* **Payback Period:** **2.5 months** from system go-live.

### 5.2 Three-Year Cumulative Cash Flow & NPV Analysis (Discount Rate = 8.0%)
Assuming conservative 5.0% annual commercial portfolio volume maturation and steady surveillance operations:

| Financial Metric | Year 1 | Year 2 | Year 3 | 3-Year Cumulative |
|---|---|---|---|---|
| **Gross Capital Preserved** | £1,026,404 | £1,077,724 | £1,131,610 | £3,235,738 |
| **Operating Expenditure** | (£210,000) | (£70,000) | (£70,000) | (£350,000) |
| **Net Operational Cash Flow** | **£816,404** | **£1,007,724** | **£1,061,610** | **£2,885,738** |
| **Discount Factor (8.0%)** | 0.9259 | 0.8573 | 0.7938 | — |
| **Discounted Net Cash Flow** | **£755,908** | **£863,922** | **£842,706** | — |
| **Net Present Value (NPV @ 8%)** | — | — | — | **£2,462,536** |

---

## 6. Accounting & Regulatory Capital Dynamics (IFRS 9 & Basel)

### 6.1 IFRS 9 Staging Dynamics
Under IFRS 9, detecting a Significant Increase in Credit Risk (SICR) triggers an accounting migration from Stage 1 (12-month ECL) to Stage 2 (Lifetime ECL).
* **Near-Term Effect:** Flagging distress earlier causes earlier Stage 2 classification, appropriately recognizing lifetime credit risk before cash default.
* **Economic Value:** While near-term provisions increase modestly during Stage 2 migration, early consensual intervention prevents facilities from deteriorating into **Stage 3 (Credit-Impaired / Defaulted)**. Preventing Stage 3 cliff-edge write-offs and increasing workout recoveries from 25% to 45% delivers direct, permanent balance sheet capital savings.

### 6.2 Regulatory Capital Preservation
Under Basel Internal Ratings-Based (IRB) approaches, early remediation of deteriorating borrowers stabilizes Risk-Weighted Assets (RWA) and prevents severe regulatory capital charges associated with defaulted exposures.
