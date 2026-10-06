# -*- coding: utf-8 -*-
"""
Project Sentinel: Commercial Credit Risk & Early-Warning Surveillance Engine
Module: Executive MI Dashboard Generator (Institutional Banking Standard)
Author: Dhruv Chaudhary, Commercial Risk Analytics
"""

import os
import html
import sys
import sqlite3
import pandas as pd
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from .dashboard_charts import (
        build_fig1_exposure_donut,
        build_fig2_materiality_scatter,
        build_fig3_queue_capacity,
        build_fig4_loss_waterfall
    )
except ImportError:
    from dashboard_charts import (
        build_fig1_exposure_donut,
        build_fig2_materiality_scatter,
        build_fig3_queue_capacity,
        build_fig4_loss_waterfall
    )

DB_PATH = os.path.join(BASE_DIR, "data", "sentinel_credit_radar.db")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
OUTPUT_HTML = os.path.join(RESULTS_DIR, "sentinel_executive_dashboard.html")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en-GB">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Sentinel | Commercial Credit Surveillance & Portfolio Remediation MI</title>
    <style>
        /* ==========================================================================
           INSTITUTIONAL BANKING MI PORTAL STYLESHEET
           Designed for Senior Credit Risk Officers, BSRU & Special Situations Committee
           Commercial Credit Portfolio Surveillance Standards
           ========================================================================== */
        
        :root {
            --navy-900: #0a192f;
            --navy-800: #0b2545;
            --navy-700: #133a68;
            --navy-600: #1e4b85;
            --slate-900: #0f172a;
            --slate-800: #1e293b;
            --slate-700: #334155;
            --slate-600: #475569;
            --slate-500: #64748b;
            --slate-400: #94a3b8;
            --slate-300: #cbd5e1;
            --slate-200: #e2e8f0;
            --slate-100: #f1f5f9;
            --slate-50: #f8fafc;
            
            --red-bg: #fef2f2;
            --red-border: #fecaca;
            --red-text: #991b1b;
            --red-primary: #dc2626;

            --amber-bg: #fffbeb;
            --amber-border: #fde68a;
            --amber-text: #92400e;
            --amber-primary: #d97706;

            --green-bg: #f0fdf4;
            --green-border: #bbf7d0;
            --green-text: #166534;
            --green-primary: #059669;

            --blue-bg: #eff6ff;
            --blue-border: #bfdbfe;
            --blue-text: #1e40af;
            --blue-primary: #2563eb;

            --card-radius: 4px;
            --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            --font-mono: ui-monospace, "SF Mono", "Cascadia Mono", "Segoe UI Mono", Menlo, Consolas, monospace;
        }

        *, *::before, *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-sans);
            background-color: var(--slate-100);
            color: var(--slate-800);
            line-height: 1.45;
            font-size: 13px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* Institutional Top Header Bar */
        .portal-header {
            background-color: var(--navy-800);
            color: #ffffff;
            border-bottom: 2px solid #06172b;
            padding: 14px 24px;
        }

        .header-top-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .branding-group {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .bank-crest {
            width: 34px;
            height: 34px;
            background: #ffffff;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 14px;
            color: var(--navy-800);
            border: 1px solid var(--slate-300);
            letter-spacing: -0.5px;
        }

        .portal-title-block {
            display: flex;
            flex-direction: column;
        }

        .portal-title {
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 0.02em;
            color: #ffffff;
        }

        .portal-subtitle {
            font-size: 11.5px;
            color: var(--slate-300);
            font-weight: 400;
            margin-top: 1px;
        }

        .header-controls {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .confidentiality-pill {
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 4px 8px;
            border-radius: 3px;
            background-color: rgba(220, 38, 38, 0.2);
            color: #fca5a5;
            border: 1px solid rgba(220, 38, 38, 0.4);
        }

        .btn-header {
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 3px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }

        .btn-header:hover {
            background: rgba(255, 255, 255, 0.18);
            border-color: rgba(255, 255, 255, 0.35);
        }

        .header-metadata-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: var(--slate-300);
            padding-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.12);
        }

        .metadata-items {
            display: flex;
            gap: 20px;
        }

        .meta-item strong {
            color: #ffffff;
            font-weight: 600;
        }

        /* Main Workspace Container */
        .workspace {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px 24px;
        }

        /* Executive KPI Summary Tiles */
        .kpi-deck {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }

        @media (max-width: 1400px) {
            .kpi-deck { grid-template-columns: repeat(3, 1fr); }
        }

        @media (max-width: 768px) {
            .kpi-deck { grid-template-columns: 1fr; }
        }

        .kpi-tile {
            background-color: #ffffff;
            border: 1px solid var(--slate-300);
            border-radius: var(--card-radius);
            padding: 14px 16px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .kpi-tile-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 6px;
        }

        .kpi-label {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--slate-600);
        }

        .kpi-tag {
            font-size: 10px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 3px;
        }

        .tag-red { background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }
        .tag-amber { background: var(--amber-bg); color: var(--amber-text); border: 1px solid var(--amber-border); }
        .tag-green { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
        .tag-blue { background: var(--blue-bg); color: var(--blue-text); border: 1px solid var(--blue-border); }
        .tag-slate { background: var(--slate-100); color: var(--slate-700); border: 1px solid var(--slate-300); }

        .kpi-primary-val {
            font-size: 22px;
            font-weight: 700;
            color: var(--slate-900);
            font-variant-numeric: tabular-nums;
            margin-bottom: 4px;
        }

        .kpi-subtext {
            font-size: 11px;
            color: var(--slate-500);
            line-height: 1.35;
        }

        /* Analytics Grid (Plotly Charts) */
        .analytics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }

        @media (max-width: 1080px) {
            .analytics-grid { grid-template-columns: 1fr; }
        }

        .chart-panel {
            background: #ffffff;
            border: 1px solid var(--slate-300);
            border-radius: var(--card-radius);
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
            padding: 12px;
        }

        /* Operational Guidance Callout Banner */
        .governance-strip {
            background: #ffffff;
            border: 1px solid var(--slate-300);
            border-radius: var(--card-radius);
            padding: 14px 18px;
            margin-bottom: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        }

        @media (max-width: 900px) {
            .governance-strip { grid-template-columns: 1fr; }
        }

        .gov-col h4 {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--slate-700);
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .gov-col p {
            font-size: 11px;
            color: var(--slate-500);
            line-height: 1.4;
        }

        /* Interactive Table Console Card */
        .console-card {
            background: #ffffff;
            border: 1px solid var(--slate-300);
            border-radius: var(--card-radius);
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
            overflow: hidden;
            margin-bottom: 24px;
        }

        .console-toolbar {
            padding: 14px 18px;
            background: #ffffff;
            border-bottom: 1px solid var(--slate-200);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
        }

        .filter-group {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: center;
        }

        .filter-btn {
            font-family: var(--font-sans);
            font-size: 11px;
            font-weight: 600;
            padding: 5px 10px;
            border-radius: 3px;
            border: 1px solid var(--slate-300);
            background: var(--slate-50);
            color: var(--slate-700);
            cursor: pointer;
            transition: all 0.12s ease;
        }

        .filter-btn:hover {
            background: var(--slate-200);
            color: var(--slate-900);
        }

        .filter-btn.active {
            background: var(--navy-800);
            color: #ffffff;
            border-color: var(--navy-800);
        }

        .search-box-wrapper {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .search-input {
            font-family: var(--font-sans);
            font-size: 12px;
            padding: 6px 12px;
            width: 280px;
            border: 1px solid var(--slate-300);
            border-radius: 3px;
            color: var(--slate-800);
            background: #ffffff;
            outline: none;
            transition: border-color 0.15s ease;
        }

        .search-input:focus {
            border-color: var(--navy-600);
            box-shadow: 0 0 0 1px var(--navy-600);
        }

        .record-counter {
            font-size: 11px;
            font-weight: 600;
            color: var(--slate-600);
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
        }

        /* Data Table Styling */
        .table-responsive {
            max-height: 600px;
            overflow-y: auto;
            position: relative;
        }

        table.triage-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            text-align: left;
        }

        table.triage-table thead th {
            position: sticky;
            top: 0;
            background: var(--slate-50);
            color: var(--slate-700);
            font-weight: 700;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 10px 12px;
            border-bottom: 1px solid var(--slate-300);
            z-index: 5;
            white-space: nowrap;
        }

        table.triage-table tbody tr {
            border-bottom: 1px solid var(--slate-200);
            transition: background 0.08s ease;
        }

        table.triage-table tbody tr:hover {
            background-color: #f8fafc;
        }

        table.triage-table tbody td {
            padding: 8px 12px;
            vertical-align: middle;
            color: var(--slate-800);
        }

        /* Cell Formatting */
        .font-mono { font-family: var(--font-mono); font-size: 11px; }
        .text-bold { font-weight: 600; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        .num-cell { font-variant-numeric: tabular-nums; }

        .cell-loan { white-space: nowrap; color: var(--slate-600); }
        .cell-crn { white-space: nowrap; }
        .cell-crn a { color: var(--navy-600); text-decoration: none; }
        .cell-crn a:hover { text-decoration: underline; }

        .entity-name { font-weight: 600; color: var(--slate-900); font-size: 12px; }
        .entity-group { font-size: 10.5px; color: var(--slate-500); margin-top: 1px; }

        /* Utilisation Bar */
        .util-wrapper {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 6px;
        }
        .util-text { font-size: 10.5px; width: 38px; text-align: right; }
        .util-track {
            width: 48px;
            height: 5px;
            background: var(--slate-200);
            border-radius: 2px;
            overflow: hidden;
        }
        .util-fill { height: 100%; border-radius: 2px; }
        .util-normal { background-color: var(--green-primary); }
        .util-med { background-color: var(--amber-primary); }
        .util-high { background-color: var(--red-primary); }

        /* Score Pills */
        .score-pill {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 700;
            font-size: 11px;
            min-width: 28px;
        }
        .score-high { background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }
        .score-med { background: var(--amber-bg); color: var(--amber-text); border: 1px solid var(--amber-border); }
        .score-low { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }

        /* Signal Pills */
        .cell-signals { white-space: nowrap; }
        .sig-pill {
            display: inline-block;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 5px;
            border-radius: 2px;
            margin-right: 3px;
        }
        .sig-dd { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
        .sig-lag { background: #fff7ed; color: #c2410c; border: 1px solid #ffedd5; }
        .sig-chg { background: #f5f3ff; color: #5b21b6; border: 1px solid #ddd6fe; }
        .sig-od { background: #fefce8; color: #854d0e; border: 1px solid #fef08a; }
        .sig-clear { background: var(--slate-100); color: var(--slate-500); font-weight: 400; }

        /* Risk Tier Status Badges */
        .status-badge {
            display: inline-block;
            font-size: 10.5px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 3px;
            white-space: nowrap;
        }
        .badge-red { background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }
        .badge-amber { background: var(--amber-bg); color: var(--amber-text); border: 1px solid var(--amber-border); }
        .badge-green { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }

        /* Operational Queue Badges */
        .queue-badge {
            display: inline-block;
            font-size: 10.5px;
            font-weight: 600;
            padding: 3px 7px;
            border-radius: 3px;
            white-space: nowrap;
        }
        .q-bsru { background: #450a0a; color: #fecaca; }
        .q-spec { background: #431407; color: #fed7aa; }
        .q-rm { background: #172554; color: #bfdbfe; }
        .q-std { background: var(--slate-100); color: var(--slate-600); }

        /* Policy Action */
        .cell-action { font-size: 11px; max-width: 320px; line-height: 1.35; }
        .action-desc { color: var(--slate-600); }

        /* Footer */
        .portal-footer {
            margin-top: 24px;
            padding: 16px 24px;
            border-top: 1px solid var(--slate-300);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: var(--slate-500);
        }

        /* Print Media Query */
        @media print {
            body { background: #ffffff; font-size: 10pt; }
            .portal-header { background: #ffffff; color: #000000; border-bottom: 2px solid #000000; padding: 0 0 10px 0; }
            .portal-title { color: #000000; }
            .portal-subtitle { color: #475569; }
            .btn-header, .console-toolbar, .search-box-wrapper { display: none !important; }
            .workspace { max-width: 100%; padding: 0; }
            .table-responsive { max-height: none; overflow: visible; }
            .chart-panel, .kpi-tile, .console-card { box-shadow: none; border: 1px solid #cccccc; page-break-inside: avoid; }
        }
        /* Persistent Disclosure Banner */
        .disclosure-bar {
            background-color: #081a30;
            border-bottom: 1px solid #1e3a5f;
            padding: 8px 24px;
            font-size: 11.5px;
            color: #cbd5e1;
            display: flex;
            align-items: center;
            gap: 12px;
            line-height: 1.4;
        }
        .disclosure-tag {
            background-color: #d97706;
            color: #ffffff;
            font-weight: 700;
            font-size: 9.5px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 2px 7px;
            border-radius: 3px;
            white-space: nowrap;
        }
        .disclosure-text {
            color: #94a3b8;
        }

    </style>
</head>
<body>

    <!-- Persistent Disclosure Notice Banner -->
    <div class="disclosure-bar">
        <span class="disclosure-tag">Methodology & Data Disclosure</span>
        <span class="disclosure-text">This dashboard is an illustrative credit risk analytics prototype. Corporate registry details are sourced from public UK Companies House bulk data. Account conduct telemetry (unpaid direct debits, overdraft utilization pinning, and facility headroom containment) is algorithmically simulated for methodology demonstration and does not represent actual bank records.</span>
    </div>


    <!-- Institutional Header -->
    <header class="portal-header">
        <div class="header-top-row">
            <div class="branding-group">
                <div class="bank-crest">PS</div>
                <div class="portal-title-block">
                    <h1 class="portal-title">PROJECT SENTINEL | COMMERCIAL CREDIT RISK & SURVEILLANCE MI</h1>
                    <span class="portal-subtitle">Commercial & Mid-Market Portfolio Early-Warning Engine & Special Recoveries Triage</span>
                </div>
            </div>
            <div class="header-controls">
                <span class="confidentiality-pill" style="background-color: rgba(37, 99, 235, 0.2); color: #93c5fd; border-color: rgba(37, 99, 235, 0.4);">Portfolio Analytics Demonstration</span>
                <a class="btn-header" href="portfolio_triage_master.csv" download="portfolio_triage_master.csv">📥 Export Master CSV</a>
                <button class="btn-header" onclick="window.print()">🖨️ Print MI Pack</button>
            </div>
        </div>
        <div class="header-metadata-bar">
            <div class="metadata-items">
                <span class="meta-item">Facility Scope: <strong>Commercial SME & Mid-Market (£200k–£3.5m lines)</strong></span>
                <span class="meta-item">Portfolio Scope: <strong>£110.51M Drawn across 250 Facilities (£207.85M Committed Limits)</strong></span>
                <span class="meta-item">Surveillance Cycle: <strong>FY26-W39 (Weekly Close)</strong></span>
                <span class="meta-item">Telemetry: <strong>Companies House Registry + Behavioural Banking</strong></span>
            </div>
            <div>
                <span>Framework: <strong>Illustrative Credit Policy & Workouts Triage Protocol</strong></span>
            </div>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="workspace">

        <!-- Executive KPI Deck -->
        <section class="kpi-deck">
            <div class="kpi-tile">
                <div class="kpi-tile-header">
                    <span class="kpi-label">Monitored Portfolio</span>
                    <span class="kpi-tag tag-slate">Book Overview</span>
                </div>
                <div class="kpi-primary-val">__KPI_TOTAL_DRAWN__</div>
                <div class="kpi-subtext">Committed: __KPI_TOTAL_LIMIT__ across 250 facilities (Utilisation: __KPI_UTIL__%)</div>
            </div>

            <div class="kpi-tile">
                <div class="kpi-tile-header">
                    <span class="kpi-label">Red Tier (Critical)</span>
                    <span class="kpi-tag tag-red">__KPI_RED_COUNT__ Facilities</span>
                </div>
                <div class="kpi-primary-val" style="color: var(--red-text);">__KPI_RED_DRAWN__</div>
                <div class="kpi-subtext">__KPI_RED_SHARE__% book share. Advisory credit review & discretionary headroom curtailment audit</div>
            </div>

            <div class="kpi-tile">
                <div class="kpi-tile-header">
                    <span class="kpi-label">Amber Tier (Elevated)</span>
                    <span class="kpi-tag tag-amber">__KPI_AMBER_COUNT__ Facilities</span>
                </div>
                <div class="kpi-primary-val" style="color: var(--amber-text);">__KPI_AMBER_DRAWN__</div>
                <div class="kpi-subtext">__KPI_AMBER_SHARE__% book share. 30-day RM cash-flow review & 13-week liquidity monitoring</div>
            </div>

            <div class="kpi-tile">
                <div class="kpi-tile-header">
                    <span class="kpi-label">BSRU Priority Queue</span>
                    <span class="kpi-tag tag-red">__KPI_BSRU_COUNT__ Active Files</span>
                </div>
                <div class="kpi-primary-val">__KPI_BSRU_DRAWN__</div>
                <div class="kpi-subtext">__KPI_BSRU_COUNT__ Workout files allocated. Target caseload limit: 10-14 files</div>
            </div>

            <div class="kpi-tile">
                <div class="kpi-tile-header">
                    <span class="kpi-label">Balance Sheet Gearing</span>
                    <span class="kpi-tag tag-amber">__KPI_SEC_CHARGES__ High Gearing</span>
                </div>
                <div class="kpi-primary-val">__KPI_SEC_CHARGES__ Entities</div>
                <div class="kpi-subtext">Commercial borrowers with ≥3 charges registered on Companies House</div>
            </div>

            <div class="kpi-tile">
                <div class="kpi-tile-header">
                    <span class="kpi-label">Net Preserved Capital</span>
                    <span class="kpi-tag tag-green">+£816k Net Y1</span>
                </div>
                <div class="kpi-primary-val" style="color: var(--green-primary); font-size: 20px;">£1.03M Gross</div>
                <div class="kpi-subtext">388.8% Net ROI (3.9x) | 3-Year NPV @ 8%: £2.46M</div>
            </div>
        </section>

        <!-- Analytics Charts Grid -->
        <section class="analytics-grid">
            <div class="chart-panel">__FIG1__</div>
            <div class="chart-panel">__FIG2__</div>
            <div class="chart-panel">__FIG3__</div>
            <div class="chart-panel">__FIG4__</div>
        </section>

        <!-- Governance Briefing Ribbon -->
        <section class="governance-strip">
            <div class="gov-col">
                <h4>🏛️ BSRU Special Workouts Protocol</h4>
                <p>High-exposure commercial borrowers (≥£350k) scoring ≥70 distress are prioritized for the Business Support & Recoveries Unit. Operational policy limits caseload to 10–14 intensive files to preserve workout negotiation effectiveness and ensure collateral review within 48 hours.</p>
            </div>
            <div class="gov-col">
                <h4>⏱️ High-Frequency Behavioural Telemetry</h4>
                <p>Unpaid HMRC Direct Debits and hard-core overdraft utilization (≥60 consecutive days at >90% limit) trigger early relationship manager notifications 60–90 days prior to formal statutory defaults, enabling proactive working capital review.</p>
            </div>
            <div class="gov-col">
                <h4>🛡️ Capital Preservation & Value Recovery</h4>
                <p>Early consensual intervention enables working capital restructuring, bilateral information covenants, and discretionary headroom containment, delivering a +20% recovery uplift over unmonitored liquidation.</p>
            </div>
        </section>

        <!-- Interactive Surveillance Table Console -->
        <section class="console-card">
            <div class="console-toolbar">
                <div class="filter-group">
                    <button class="filter-btn active" onclick="applyFilter(this, 'ALL')">All Facilities (__COUNT_ALL__)</button>
                    <button class="filter-btn" onclick="applyFilter(this, 'BSRU')">BSRU Squad (__COUNT_BSRU__)</button>
                    <button class="filter-btn" onclick="applyFilter(this, 'SPEC')">Special Situations (__COUNT_SPEC__)</button>
                    <button class="filter-btn" onclick="applyFilter(this, 'RM')">RM Intensive Care (__COUNT_RM__)</button>
                    <button class="filter-btn" onclick="applyFilter(this, 'RED')">Red Critical (__COUNT_RED__)</button>
                    <button class="filter-btn" onclick="applyFilter(this, 'AMBER')">Amber Elevated (__COUNT_AMBER__)</button>
                    <button class="filter-btn" onclick="applyFilter(this, 'GREEN')">Green Standard (__COUNT_GREEN__)</button>
                </div>
                <div class="search-box-wrapper">
                    <input type="text" id="searchInput" class="search-input" placeholder="Search Client, CRN, Group, or Loan ID..." onkeyup="handleSearch()" />
                    <span id="recordCount" class="record-counter">Showing __COUNT_ALL__ of __COUNT_ALL__ facilities | Exposure: __KPI_TOTAL_DRAWN__</span>
                </div>
            </div>

            <div class="table-responsive">
                <table class="triage-table" id="triageTable">
                    <thead>
                        <tr>
                            <th>Facility Ref</th>
                            <th>Counterparty & Corporate Group</th>
                            <th>CRN</th>
                            <th class="text-right">Committed Limit</th>
                            <th class="text-right">Drawn Balance</th>
                            <th class="text-right">Utilisation</th>
                            <th class="text-center">Distress</th>
                            <th>Surveillance Telemetry</th>
                            <th>Risk Tier</th>
                            <th>Operational Queue</th>
                            <th>Credit Policy Action Directive</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                        __TABLE_BODY__
                    </tbody>
                </table>
            </div>
        </section>

    </main>

    <!-- Institutional Footer -->
    <footer class="portal-footer">
        <div>
            <span>Project Sentinel | Commercial Credit Surveillance Engine | Model Ref: SEN-MI-2026-W39</span>
        </div>
        <div>
            <span>Snapshot Date: 01 Sep 2026 | Environment: Prototype Demonstration | Illustrative Methodology</span>
        </div>
    </footer>

    <!-- Interactive Client-Side JavaScript -->
    <script>
        let currentFilter = 'ALL';
        const searchInput = document.getElementById('searchInput');
        const recordCount = document.getElementById('recordCount');
        const rows = Array.from(document.querySelectorAll('#tableBody tr'));

        function applyFilter(btnElement, filterType) {
            currentFilter = filterType;
            
            // Update active button state
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            if (btnElement) {
                btnElement.classList.add('active');
            }

            filterTable();
        }

        function handleSearch() {
            filterTable();
        }

        function filterTable() {
            const query = searchInput.value.toLowerCase().trim();
            let visibleCount = 0;
            let visibleExposure = 0;

            rows.forEach(row => {
                const tier = row.getAttribute('data-tier');
                const queue = row.getAttribute('data-queue');
                const searchData = row.getAttribute('data-search');
                const drawn = parseFloat(row.getAttribute('data-drawn')) || 0;

                // Check button filter
                let matchesButton = false;
                if (currentFilter === 'ALL') matchesButton = true;
                else if (currentFilter === 'BSRU' && queue === 'BSRU_WORKOUT_SQUAD') matchesButton = true;
                else if (currentFilter === 'SPEC' && queue === 'SPECIAL_SITUATIONS_WATCH') matchesButton = true;
                else if (currentFilter === 'RM' && queue === 'RM_INTENSIVE_CARE') matchesButton = true;
                else if (currentFilter === 'RED' && tier === 'RED_CRITICAL') matchesButton = true;
                else if (currentFilter === 'AMBER' && tier === 'AMBER_ELEVATED') matchesButton = true;
                else if (currentFilter === 'GREEN' && tier === 'GREEN_STANDARD') matchesButton = true;

                // Check search query
                let matchesSearch = true;
                if (query.length > 0) {
                    matchesSearch = searchData.includes(query);
                }

                if (matchesButton && matchesSearch) {
                    row.style.display = '';
                    visibleCount++;
                    visibleExposure += drawn;
                } else {
                    row.style.display = 'none';
                }
            });

            // Update record counter
            const exposureMillions = (visibleExposure / 1e6).toFixed(2);
            recordCount.textContent = `Showing ${visibleCount} of ${rows.length} facilities | Filtered Exposure: £${exposureMillions}M`;
        }
    </script>
</body>
</html>"""

def main():
    print("=" * 80)
    print("PROJECT SENTINEL: GENERATING INSTITUTIONAL BANKING MI DASHBOARD")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
    SELECT 
        loan_id, client_name, company_number, parent_group_comp_number, parent_group_name,
        drawn_amount, facility_limit, facility_type, region, company_status, accounts_days_overdue,
        filing_delinquency_tier, conf_stmt_days_overdue, unpaid_dd_count_90d,
        consecutive_od_pinned_days, hard_core_borrowing_flag, num_mort_outstanding,
        high_charge_encumbrance_flag,
        score_filing_lag, score_conf_stmt, score_insolvency_event, score_charge_encumbrance,
        score_unpaid_dd, score_od_utilization, score_hard_core, statutory_distress_score,
        operational_risk_tier, materiality_exposure_score, credit_policy_action,
        operational_assignment_routing, current_drawn_exposure, undrawn_facility_exposure
    FROM vw_portfolio_triage_actions
    ORDER BY materiality_exposure_score DESC;
    """, conn)
    conn.close()

    total_drawn = df['current_drawn_exposure'].sum()
    total_limit = df['facility_limit'].sum()
    portfolio_util = (total_drawn / total_limit * 100) if total_limit > 0 else 0

    red_df = df[df['operational_risk_tier'] == 'RED_CRITICAL']
    amber_df = df[df['operational_risk_tier'] == 'AMBER_ELEVATED']
    green_df = df[df['operational_risk_tier'] == 'GREEN_STANDARD']

    red_drawn = red_df['current_drawn_exposure'].sum()
    amber_drawn = amber_df['current_drawn_exposure'].sum()
    green_drawn = green_df['current_drawn_exposure'].sum()

    bsru_df = df[df['operational_assignment_routing'] == 'BSRU_WORKOUT_SQUAD']
    bsru_drawn = bsru_df['current_drawn_exposure'].sum()
    bsru_count = len(bsru_df)

    spec_df = df[df['operational_assignment_routing'] == 'SPECIAL_SITUATIONS_WATCH']
    spec_drawn = spec_df['current_drawn_exposure'].sum()
    spec_count = len(spec_df)

    rm_df = df[df['operational_assignment_routing'] == 'RM_INTENSIVE_CARE']
    rm_drawn = rm_df['current_drawn_exposure'].sum()
    rm_count = len(rm_df)

    secondary_charges_count = int((df['high_charge_encumbrance_flag'] == 1).sum())
    hardcore_od_count = int((df['hard_core_borrowing_flag'] == 1).sum())

    print(f"Loaded {len(df)} facilities. Total Drawn: £{total_drawn:,.2f}")
    print(f"Red Tier: {len(red_df)} facilities (£{red_drawn:,.2f})")
    print(f"Amber Tier: {len(amber_df)} facilities (£{amber_drawn:,.2f})")
    print(f"BSRU Priority Squad: {bsru_count} files (£{bsru_drawn:,.2f})")

    # Generate charts
    fig1 = build_fig1_exposure_donut(df)
    fig2 = build_fig2_materiality_scatter(df)
    fig3 = build_fig3_queue_capacity(df)
    fig4 = build_fig4_loss_waterfall(df)

    fig1_html = fig1.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False, 'responsive': True})
    fig2_html = fig2.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})
    fig3_html = fig3.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})
    fig4_html = fig4.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})

    # Build Table Rows
    rows = []
    for _, r in df.iterrows():
        tier = r['operational_risk_tier']
        queue = r['operational_assignment_routing']
        drawn = r['current_drawn_exposure']
        limit = r['facility_limit']
        util = (drawn / limit * 100) if limit > 0 else 0
        score = int(r['statutory_distress_score'])
        mat_score = r['materiality_exposure_score']
        loan_id = str(r['loan_id'])
        # Use pseudonymous IDs for public demonstration alongside simulated conduct
        borrower_num = loan_id.split('-')[-1][-4:]
        client = f"Commercial Borrower BRW-{borrower_num}"
        group = f"{r['parent_group_name']} (Simulated Group)" if pd.notna(r.get('parent_group_name')) and str(r.get('parent_group_name')).strip() != '' else 'Standalone Commercial Borrower'
        pseudo_crn = f"CRN-SIM-{borrower_num}"

        # Badges
        if tier == 'RED_CRITICAL':
            tier_badge = '<span class="status-badge badge-red">Red (Critical)</span>'
        elif tier == 'AMBER_ELEVATED':
            tier_badge = '<span class="status-badge badge-amber">Amber (Elevated)</span>'
        else:
            tier_badge = '<span class="status-badge badge-green">Green (Standard)</span>'

        if queue == 'BSRU_WORKOUT_SQUAD':
            queue_badge = '<span class="queue-badge q-bsru">BSRU Squad</span>'
        elif queue == 'SPECIAL_SITUATIONS_WATCH':
            queue_badge = '<span class="queue-badge q-spec">Spec Situations</span>'
        elif queue == 'RM_INTENSIVE_CARE':
            queue_badge = '<span class="queue-badge q-rm">RM Intensive</span>'
        else:
            queue_badge = '<span class="queue-badge q-std">Standard Surveillance</span>'

        # Distress Signals
        signals = []
        if r['unpaid_dd_count_90d'] > 0:
            signals.append(f'<span class="sig-pill sig-dd">{int(r["unpaid_dd_count_90d"])} Unpaid HMRC DDs</span>')
        if r['accounts_days_overdue'] > 0:
            signals.append(f'<span class="sig-pill sig-lag">{int(r["accounts_days_overdue"])}d Filing Lag</span>')
        if r['high_charge_encumbrance_flag'] == 1:
            signals.append(f'<span class="sig-pill sig-chg">{int(r["num_mort_outstanding"])} Charges</span>')
        if r['consecutive_od_pinned_days'] >= 30:
            signals.append(f'<span class="sig-pill sig-od">{int(r["consecutive_od_pinned_days"])}d Pinned OD</span>')
        if not signals:
            signals.append('<span class="sig-pill sig-clear">No Active Red Flags</span>')

        signals_html = ' '.join(signals)

        # Policy Action brief
        policy_action = str(r['credit_policy_action'])
        if ':' in policy_action:
            action_code, action_desc = policy_action.split(':', 1)
            action_code_esc = html.escape(action_code.strip(), quote=True)
            action_desc_esc = html.escape(action_desc.strip(), quote=True)
            action_html = f'<strong>{action_code_esc}:</strong> <span class="action-desc">{action_desc_esc}</span>'
        else:
            action_html = html.escape(policy_action.strip(), quote=True)

        # HTML-escape every variable including attributes using html.escape(..., quote=True)
        loan_id_esc = html.escape(loan_id, quote=True)
        client_esc = html.escape(client, quote=True)
        group_esc = html.escape(group, quote=True)
        pseudo_crn_esc = html.escape(pseudo_crn, quote=True)
        tier_esc = html.escape(tier, quote=True)
        queue_esc = html.escape(queue, quote=True)

        search_str = f"{loan_id} {client} {group} {pseudo_crn} {tier} {queue}".lower()
        search_str_esc = html.escape(search_str, quote=True)

        row_html = f'''<tr data-tier="{tier_esc}" data-queue="{queue_esc}" data-drawn="{drawn:.2f}" data-search="{search_str_esc}">
            <td class="font-mono text-bold cell-loan">{loan_id_esc}</td>
            <td class="cell-entity">
                <div class="entity-name">{client_esc}</div>
                <div class="entity-group">{group_esc}</div>
            </td>
            <td class="font-mono cell-crn"><span title="Pseudonymised borrower identifier">{pseudo_crn_esc}</span></td>
            <td class="text-right num-cell font-mono">£{limit:,.0f}</td>
            <td class="text-right num-cell font-mono text-bold">£{drawn:,.0f}</td>
            <td class="text-right num-cell">
                <div class="util-wrapper">
                    <span class="util-text font-mono">{util:.1f}%</span>
                    <div class="util-track"><div class="util-fill {'util-high' if util > 90 else 'util-med' if util > 70 else 'util-normal'}" style="width: {min(util, 100):.1f}%;"></div></div>
                </div>
            </td>
            <td class="text-center font-mono">
                <span class="score-pill score-{'high' if score >= 70 else 'med' if score >= 40 else 'low'}">{score}</span>
            </td>
            <td class="cell-signals">{signals_html}</td>
            <td class="cell-tier">{tier_badge}</td>
            <td class="cell-queue">{queue_badge}</td>
            <td class="cell-action">{action_html}</td>
        </tr>'''
        rows.append(row_html)

    table_body = "\n".join(rows)

    # Replace placeholders in template
    html_output = HTML_TEMPLATE
    html_output = html_output.replace("__KPI_TOTAL_DRAWN__", f"£{total_drawn/1e6:,.1f}M")
    html_output = html_output.replace("__KPI_TOTAL_LIMIT__", f"£{total_limit/1e6:,.1f}M")
    html_output = html_output.replace("__KPI_UTIL__", f"{portfolio_util:.1f}")
    html_output = html_output.replace("__KPI_RED_COUNT__", str(len(red_df)))
    html_output = html_output.replace("__KPI_RED_DRAWN__", f"£{red_drawn/1e6:,.2f}M")
    html_output = html_output.replace("__KPI_AMBER_COUNT__", str(len(amber_df)))
    html_output = html_output.replace("__KPI_AMBER_DRAWN__", f"£{amber_drawn/1e6:,.2f}M")
    html_output = html_output.replace("__KPI_BSRU_COUNT__", str(bsru_count))
    html_output = html_output.replace("__KPI_BSRU_DRAWN__", f"£{bsru_drawn/1e6:,.2f}M")
    html_output = html_output.replace("__KPI_SEC_CHARGES__", str(secondary_charges_count))
    red_share = (red_drawn / total_drawn * 100) if total_drawn > 0 else 0
    amber_share = (amber_drawn / total_drawn * 100) if total_drawn > 0 else 0
    html_output = html_output.replace("__COUNT_ALL__", str(len(df)))
    html_output = html_output.replace("__COUNT_BSRU__", str(bsru_count))
    html_output = html_output.replace("__COUNT_SPEC__", str(spec_count))
    html_output = html_output.replace("__COUNT_RM__", str(rm_count))
    html_output = html_output.replace("__COUNT_RED__", str(len(red_df)))
    html_output = html_output.replace("__COUNT_AMBER__", str(len(amber_df)))
    html_output = html_output.replace("__COUNT_GREEN__", str(len(green_df)))
    html_output = html_output.replace("__KPI_RED_SHARE__", f"{red_share:.1f}")
    html_output = html_output.replace("__KPI_AMBER_SHARE__", f"{amber_share:.1f}")
    html_output = html_output.replace("__FIG1__", fig1_html)
    html_output = html_output.replace("__FIG2__", fig2_html)
    html_output = html_output.replace("__FIG3__", fig3_html)
    html_output = html_output.replace("__FIG4__", fig4_html)
    html_output = html_output.replace("__TABLE_BODY__", table_body)

        # Export Sanitized Master Triage CSVs (Zero association of real company names with simulated conduct)
    export_df = df.copy()
    export_df['borrower_id'] = export_df['loan_id'].apply(lambda x: f"Commercial Borrower BRW-{str(x).split('-')[-1][-4:]}")
    export_df['simulated_crn'] = export_df['loan_id'].apply(lambda x: f"CRN-SIM-{str(x).split('-')[-1][-4:]}")
    export_df['group_name'] = export_df.apply(lambda r: f"{r['parent_group_name']} (Simulated Group)" if pd.notna(r.get('parent_group_name')) and str(r.get('parent_group_name')).strip() != '' else 'Standalone Commercial Borrower', axis=1)
    
    clean_csv_df = export_df[[
        'loan_id', 'borrower_id', 'simulated_crn', 'group_name', 'facility_type',
        'facility_limit', 'current_drawn_exposure', 'undrawn_facility_exposure',
        'statutory_distress_score', 'operational_risk_tier', 'materiality_exposure_score',
        'operational_assignment_routing', 'credit_policy_action',
        'accounts_days_overdue', 'unpaid_dd_count_90d', 'consecutive_od_pinned_days', 'hard_core_borrowing_flag'
    ]]
    
    master_csv_path = os.path.join(RESULTS_DIR, "portfolio_triage_master.csv")
    clean_csv_df.to_csv(master_csv_path, index=False, encoding='utf-8')
    print(f"Exported sanitized master CSV: {master_csv_path}")

    dossier_csv_path = os.path.join(RESULTS_DIR, "high_risk_amber_red_dossier.csv")
    clean_csv_df[clean_csv_df['operational_risk_tier'].isin(['RED_CRITICAL', 'AMBER_ELEVATED'])].to_csv(dossier_csv_path, index=False, encoding='utf-8')
    print(f"Exported priority dossier CSV: {dossier_csv_path}")

    group_csv_path = os.path.join(RESULTS_DIR, "corporate_group_exposure_summary.csv")
    conn_grp = sqlite3.connect(DB_PATH)
    grp_df = pd.read_sql_query("SELECT * FROM vw_corporate_group_exposure;", conn_grp)
    conn_grp.close()
    grp_df.to_csv(group_csv_path, index=False, encoding='utf-8')
    print(f"Exported corporate group summary CSV: {group_csv_path}")

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"Executive dashboard generated successfully at: {OUTPUT_HTML}")
    file_size_kb = os.path.getsize(OUTPUT_HTML) / 1024
    print(f"File size: {file_size_kb:.1f} KB")

    # Update TARGET_SCRIPT on E: only if different
    
if __name__ == '__main__':
    main()
