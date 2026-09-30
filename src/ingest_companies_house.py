#!/usr/bin/env python3
"""
Project Sentinel: Commercial Credit Risk & Early-Warning Surveillance Engine
Module: Companies House Statutory Ingestion & Account Conduct Pipeline
Author: Dhruv Chaudhary, Commercial Risk Analytics Case Study

Ingests official UK Government Companies House bulk registry data (BasicCompanyData-part1.zip),
samples an authentic commercial SME / mid-market corporate borrowing cohort,
synthesizes realistic bilateral commercial facilities, group parent structures, and internal
account conduct telemetry (unpaid direct debits, hard-core overdraft utilization),
and loads the schema into SQLite.
"""

import os
import sys
import zipfile
import csv
import io
import re
import sqlite3
import random
from datetime import datetime, timedelta

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_PATH = os.path.join(BASE_DIR, 'data', 'BasicCompanyData-part1.zip')
DB_PATH = os.path.join(BASE_DIR, 'data', 'sentinel_credit_radar.db')
SQL_DIR = os.path.join(BASE_DIR, 'sql')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

SNAPSHOT_DATE = datetime(2026, 9, 1).date()

def parse_uk_date(d_str):
    if not d_str or not d_str.strip():
        return None
    d_str = d_str.strip()
    try:
        return datetime.strptime(d_str, '%d/%m/%Y').date()
    except Exception:
        try:
            return datetime.strptime(d_str, '%Y-%m-%d').date()
        except Exception:
            return None

EXCLUDE_NAME_WORDS = [
    'MANAGEMENT', 'RESIDENTS', 'FREEHOLD', 'FLATS', 'ESTATES',
    'PROPERTY', 'PROPERTIES', 'HOLDINGS', 'SPV', 'NOMINEES',
    'LETTINGS', 'LANDLORD', 'APARTMENTS', 'HOUSE MANAGEMENT', 'DEVELOPMENTS'
]

COMMERCIAL_SIC_PREFIXES = [
    '10', '11', '13', '14', '15', '16', '17', '18', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33',
    '41', '42', '43',
    '45', '46', '47',
    '49', '50', '51', '52', '53',
    '69', '70', '71', '72', '73', '74'
]

def is_commercial_sic(sic_text):
    if not sic_text:
        return False
    for code in sic_text.replace(',', ' ').split():
        for prefix in COMMERCIAL_SIC_PREFIXES:
            if code.startswith(prefix):
                return True
    return False

POSTCODE_REGION_MAP = {
    'EC': 'London & South East', 'WC': 'London & South East', 'E': 'London & South East',
    'N': 'London & South East', 'NW': 'London & South East', 'SE': 'London & South East',
    'SW': 'London & South East', 'W': 'London & South East', 'BR': 'London & South East',
    'CR': 'London & South East', 'DA': 'London & South East', 'EN': 'London & South East',
    'HA': 'London & South East', 'IG': 'London & South East', 'KT': 'London & South East',
    'RM': 'London & South East', 'SM': 'London & South East', 'TW': 'London & South East',
    'UB': 'London & South East', 'BN': 'London & South East', 'CT': 'London & South East',
    'ME': 'London & South East', 'RH': 'London & South East', 'TN': 'London & South East',
    'GU': 'London & South East', 'RG': 'London & South East', 'SL': 'London & South East',
    'SO': 'London & South East', 'PO': 'London & South East',
    'B': 'Midlands', 'CV': 'Midlands', 'DY': 'Midlands', 'WS': 'Midlands', 'WV': 'Midlands',
    'LE': 'Midlands', 'DE': 'Midlands', 'NG': 'Midlands', 'NN': 'Midlands', 'ST': 'Midlands',
    'LN': 'Midlands', 'WR': 'Midlands',
    'M': 'North West', 'L': 'North West', 'SK': 'North West', 'WA': 'North West',
    'WN': 'North West', 'BL': 'North West', 'OL': 'North West', 'PR': 'North West',
    'BB': 'North West', 'FY': 'North West', 'LA': 'North West', 'CW': 'North West', 'CH': 'North West',
    'LS': 'Yorkshire & Humber', 'BD': 'Yorkshire & Humber', 'HG': 'Yorkshire & Humber',
    'HD': 'Yorkshire & Humber', 'HX': 'Yorkshire & Humber', 'WF': 'Yorkshire & Humber',
    'S': 'Yorkshire & Humber', 'DN': 'Yorkshire & Humber', 'YO': 'Yorkshire & Humber', 'HU': 'Yorkshire & Humber',
    'BS': 'South West', 'BA': 'South West', 'EX': 'South West', 'PL': 'South West',
    'TQ': 'South West', 'TR': 'South West', 'GL': 'South West', 'SN': 'South West', 'SP': 'South West', 'TA': 'South West',
    'CB': 'East of England', 'CM': 'East of England', 'CO': 'East of England', 'IP': 'East of England',
    'NR': 'East of England', 'PE': 'East of England', 'SS': 'East of England', 'AL': 'East of England',
    'HP': 'East of England', 'LU': 'East of England', 'SG': 'East of England',
    'NE': 'North East', 'SR': 'North East', 'DH': 'North East', 'TS': 'North East', 'DL': 'North East',
    'CF': 'Wales', 'NP': 'Wales', 'SA': 'Wales', 'LL': 'Wales', 'LD': 'Wales', 'SY': 'Wales',
    'G': 'Scotland', 'EH': 'Scotland', 'AB': 'Scotland', 'DD': 'Scotland', 'FK': 'Scotland',
    'KY': 'Scotland', 'PA': 'Scotland', 'ML': 'Scotland', 'KA': 'Scotland', 'PH': 'Scotland', 'IV': 'Scotland'
}

def get_region(postcode):
    if not postcode or not postcode.strip():
        return 'London & South East'
    m = re.match(r'^([A-Z]{1,2})', postcode.strip().upper())
    if m:
        return POSTCODE_REGION_MAP.get(m.group(1), 'London & South East')
    return 'London & South East'

def run_ingestion():
    print("=" * 75)
    print("PROJECT SENTINEL: STATUTORY & ACCOUNT CONDUCT INGESTION")
    print(f"Snapshot Reference Date: {SNAPSHOT_DATE}")
    print("=" * 75)

    random.seed(42)

    # 1. Connect to Database & Create Schema
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    ddl_path = os.path.join(SQL_DIR, '01_schema_ddl.sql')
    if os.path.exists(ddl_path):
        with open(ddl_path, 'r', encoding='utf-8') as f:
            ddl_sql = f.read()
        
        cursor.executescript("""
        DROP VIEW IF EXISTS vw_corporate_group_exposure;
        DROP VIEW IF EXISTS vw_portfolio_triage_actions;
        DROP VIEW IF EXISTS vw_statutory_distress_index;
        DROP VIEW IF EXISTS vw_charge_telemetry;
        DROP VIEW IF EXISTS vw_filing_lag_telemetry;

        DROP TABLE IF EXISTS tbl_filing_history;
        DROP TABLE IF EXISTS tbl_charges_register;
        DROP TABLE IF EXISTS tbl_companies_house_profile;
        DROP TABLE IF EXISTS tbl_borrower_portfolio;
        """)
        cursor.executescript(ddl_sql)
        conn.commit()
        print("Loaded enterprise DDL schema from sql/01_schema_ddl.sql successfully.")
    else:
        print("Error: 01_schema_ddl.sql not found!")
        sys.exit(1)

    # 2. Extract Real UK Commercial Companies from Companies House Archive
    selected_cohort = []
    
    if os.path.exists(ZIP_PATH):
        print("\nStreaming official UK Companies House census...")
        on_time_pool_a = []
        on_time_pool_b = []
        overdue_pool = []
        seen_stems = set()
        seen_numbers = set()

        with zipfile.ZipFile(ZIP_PATH, 'r') as z:
            csv_filename = [n for n in z.namelist() if n.endswith('.csv')][0]
            print(f"Reading: {csv_filename}")
            
            with z.open(csv_filename) as f:
                text_stream = io.TextIOWrapper(f, encoding='utf-8', errors='ignore')
                reader = csv.DictReader(text_stream)
                
                for raw_row in reader:
                    row = {k.strip(): (v.strip() if v else '') for k, v in raw_row.items() if k}
                    cnum = row.get('CompanyNumber', '')
                    if not cnum or cnum in seen_numbers:
                        continue
                    
                    name = row.get('CompanyName', '').strip()
                    if not name or not name[0].isalpha():
                        continue
                    
                    name_upper = name.upper()
                    if any(w in name_upper for w in EXCLUDE_NAME_WORDS):
                        continue
                    
                    # Deduplicate name stems (first 2 words) to prevent unlinked duplicates
                    words = name_upper.split()
                    stem = ' '.join(words[:2]) if len(words) >= 2 else words[0]
                    if stem in seen_stems:
                        continue
                    
                    status = row.get('CompanyStatus', '').strip()
                    if status != 'Active':
                        continue
                        
                    acc_cat = row.get('Accounts.AccountCategory', '').strip().upper()
                    if acc_cat in ['DORMANT', '']:
                        continue
                        
                    sic = row.get('SICCode.SicText_1', '').strip()
                    if not is_commercial_sic(sic):
                        continue
                        
                    acc_due = parse_uk_date(row.get('Accounts.NextDueDate', ''))
                    if not acc_due:
                        continue
                        
                    days_overdue = (SNAPSHOT_DATE - acc_due).days
                    if days_overdue > 365 or days_overdue < -365:
                        continue
                    
                    seen_stems.add(stem)
                    seen_numbers.add(cnum)
                    
                    item = {
                        'CompanyNumber': cnum,
                        'CompanyName': name,
                        'CompanyCategory': row.get('CompanyCategory', 'Private Limited Company').strip(),
                        'CompanyStatus': status,
                        'CountryOfOrigin': row.get('CountryOfOrigin', 'United Kingdom').strip(),
                        'IncorporationDate': row.get('IncorporationDate', '').strip(),
                        'Accounts.AccountCategory': acc_cat,
                        'Accounts.NextDueDate': row.get('Accounts.NextDueDate', '').strip(),
                        'Accounts.LastMadeUpDate': row.get('Accounts.LastMadeUpDate', '').strip(),
                        'ConfStmtNextDueDate': row.get('ConfirmationStatement.NextDueDate', '').strip(),
                        'ConfStmtLastMadeUpDate': row.get('ConfirmationStatement.LastMadeUpDate', '').strip(),
                        'RegAddress.PostTown': row.get('RegAddress.PostTown', '').strip() or 'LEEDS',
                        'RegAddress.County': row.get('RegAddress.County', '').strip() or 'WEST YORKSHIRE',
                        'RegAddress.PostCode': row.get('RegAddress.PostCode', '').strip() or 'LS1 5QL',
                        'SICCode.SicText_1': sic,
                        'Mortgages.NumMortCharges': row.get('Mortgages.NumMortCharges', '0').strip(),
                        'Mortgages.NumMortOutstanding': row.get('Mortgages.NumMortOutstanding', '0').strip(),
                        'Mortgages.NumMortSatisfied': row.get('Mortgages.NumMortSatisfied', '0').strip(),
                        'URI': row.get('URI', '').strip(),
                        'days_overdue': days_overdue
                    }
                    
                    first_letter = name_upper[0]
                    if days_overdue > 0:
                        overdue_pool.append(item)
                    else:
                        if first_letter == 'A' and len(on_time_pool_a) < 1500:
                            on_time_pool_a.append(item)
                        elif first_letter == 'B' and len(on_time_pool_b) < 1500:
                            on_time_pool_b.append(item)
                    
                    if len(on_time_pool_a) >= 1500 and len(on_time_pool_b) >= 1500 and len(overdue_pool) >= 100:
                        break

        print(f"Discovered {len(on_time_pool_a)} 'A' on-time, {len(on_time_pool_b)} 'B' on-time, and {len(overdue_pool)} overdue candidates.")
        
        # Sample balanced cohort: 109 A on-time, 109 B on-time, 32 overdue
        random.shuffle(on_time_pool_a)
        random.shuffle(on_time_pool_b)
        random.shuffle(overdue_pool)

        # Sort overdue by days descending
        overdue_pool.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        # Exact allocations:
        # Red: 11 overdue borrowers (acute delay 35 - 280 days)
        # Amber: 12 overdue (moderate delay) + 20 on-time (early warning conduct)
        # Green: 9 overdue (benign delay) + 198 on-time (sound conduct)
        red_cohort = overdue_pool[:11]
        amber_cohort = overdue_pool[11:23] + on_time_pool_a[:10] + on_time_pool_b[:10]
        green_cohort = overdue_pool[23:32] + on_time_pool_a[10:109] + on_time_pool_b[10:109]
        
        selected_cohort = red_cohort + amber_cohort + green_cohort
        print(f"Selected portfolio cohort of {len(selected_cohort)} borrowers (Red: {len(red_cohort)}, Amber: {len(amber_cohort)}, Green: {len(green_cohort)}).")
    else:
        print(f"Notice: Bulk data archive not found at {ZIP_PATH}.")
        print("Generating realistic representative UK commercial borrowing cohort...")
        # Self-contained offline generator for clean clone execution
        sample_towns = [
            ('LEEDS', 'WEST YORKSHIRE', 'LS1 5QL'), ('BIRMINGHAM', 'WEST MIDLANDS', 'B2 4ND'),
            ('MANCHESTER', 'GREATER MANCHESTER', 'M2 3DE'), ('SHEFFIELD', 'SOUTH YORKSHIRE', 'S1 2GU'),
            ('BRISTOL', 'CITY OF BRISTOL', 'BS1 4ST'), ('NEWCASTLE', 'TYNE AND WEAR', 'NE1 1EE'),
            ('NOTTINGHAM', 'NOTTINGHAMSHIRE', 'NG1 2BY'), ('NORWICH', 'NORFOLK', 'NR1 3PN'),
            ('CARDIFF', 'SOUTH GLAMORGAN', 'CF10 1EP'), ('GLASGOW', 'LANARKSHIRE', 'G1 1XQ'),
            ('LONDON', 'GREATER LONDON', 'EC2M 7PP'), ('LONDON', 'GREATER LONDON', 'SE1 9SG')
        ]
        sample_sics = [
            '25620 - Machining and precision engineering',
            '41202 - Construction of commercial buildings',
            '45200 - Maintenance and repair of motor vehicles',
            '49410 - Freight transport by road',
            '46690 - Wholesale of other machinery and equipment',
            '71129 - Other engineering activities',
            '10710 - Manufacture of bread; manufacture of fresh pastry goods',
            '43210 - Electrical installation',
            '70229 - Management consultancy activities other than financial'
        ]
        prefixes = ['BRITANNIA', 'BRADLEY', 'BELGRAVIA', 'BEACON', 'BERKSHIRE', 'BRUNEL', 'BARNSLEY',
                    'APEX', 'ATLAS', 'ANGLIA', 'ARDEN', 'ARROW', 'ABBEY', 'ALBION', 'AVON', 'ASTRAL']
        suffixes = ['ENGINEERING LTD', 'LOGISTICS LTD', 'PRECISION TOOLS LTD', 'DISTRIBUTION LTD',
                    'CONTRACTING LTD', 'MANUFACTURING LTD', 'TRANSPORT LTD', 'COMMERCIAL SERVICES LTD']
        
        comp_idx = 10000000
        for i in range(250):
            pfx = prefixes[i % len(prefixes)]
            sfx = suffixes[(i * 3) % len(suffixes)]
            cname = f"{pfx} {sfx}"
            town, county, pcode = sample_towns[i % len(sample_towns)]
            sic = sample_sics[i % len(sample_sics)]
            comp_idx += random.randint(11, 89)
            
            # 32 overdue (11 Red, 12 Amber, 9 Green), 218 on-time (20 Amber, 198 Green)
            if i < 11:
                days_ov = random.randint(45, 240)
            elif i < 23:
                days_ov = random.randint(15, 44)
            elif i < 32:
                days_ov = random.randint(1, 14)
            else:
                days_ov = random.randint(-300, -5)
                
            acc_due = SNAPSHOT_DATE - timedelta(days=days_ov)
            selected_cohort.append({
                'CompanyNumber': f"{comp_idx:08d}",
                'CompanyName': cname,
                'CompanyCategory': 'Private Limited Company',
                'CompanyStatus': 'Active',
                'CountryOfOrigin': 'United Kingdom',
                'IncorporationDate': str(SNAPSHOT_DATE - timedelta(days=random.randint(1500, 6000))),
                'Accounts.AccountCategory': 'TOTAL EXEMPTION FULL',
                'Accounts.NextDueDate': acc_due.strftime('%d/%m/%Y'),
                'Accounts.LastMadeUpDate': str(acc_due - timedelta(days=365)),
                'ConfStmtNextDueDate': str(acc_due + timedelta(days=60)),
                'ConfStmtLastMadeUpDate': str(acc_due - timedelta(days=305)),
                'RegAddress.PostTown': town,
                'RegAddress.County': county,
                'RegAddress.PostCode': pcode,
                'SICCode.SicText_1': sic,
                'Mortgages.NumMortCharges': '2',
                'Mortgages.NumMortOutstanding': str(random.choice([0, 0, 1, 1, 2, 3])),
                'Mortgages.NumMortSatisfied': '1',
                'URI': f"http://business.data.gov.uk/id/company/{comp_idx:08d}",
                'days_overdue': days_ov
            })
        print(f"Generated synthetic representative cohort of {len(selected_cohort)} borrowers.")

    # 3. Insert Companies House Profiles (all 21 columns)
    print("\nInserting Companies House registry profiles...")
    for c in selected_cohort:
        comp_num = c['CompanyNumber']
        comp_name = c['CompanyName']
        post_town = c.get('RegAddress.PostTown', 'LEEDS')
        county = c.get('RegAddress.County', 'WEST YORKSHIRE')
        post_code = c.get('RegAddress.PostCode', 'LS1 5QL')
        comp_cat = c.get('CompanyCategory', 'Private Limited Company')
        status = c.get('CompanyStatus', 'Active')
        origin = c.get('CountryOfOrigin', 'United Kingdom')
        incorp_date = parse_uk_date(c.get('IncorporationDate'))
        acc_next_due = parse_uk_date(c.get('Accounts.NextDueDate'))
        acc_last_made = parse_uk_date(c.get('Accounts.LastMadeUpDate'))
        acc_cat = c.get('Accounts.AccountCategory', 'TOTAL EXEMPTION FULL')
        conf_next_due = parse_uk_date(c.get('ConfStmtNextDueDate'))
        conf_last_made = parse_uk_date(c.get('ConfStmtLastMadeUpDate'))
        num_charges = int(c.get('Mortgages.NumMortCharges', 0) or 0)
        num_outstanding = int(c.get('Mortgages.NumMortOutstanding', 0) or 0)
        num_satisfied = int(c.get('Mortgages.NumMortSatisfied', 0) or 0)
        sic_1 = c.get('SICCode.SicText_1', '70229 - Management consultancy')
        uri = c.get('URI', f"http://business.data.gov.uk/id/company/{comp_num}")

        cursor.execute("""
        INSERT INTO tbl_companies_house_profile VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            comp_num, comp_name, post_town, county, post_code, comp_cat,
            status, origin,
            str(incorp_date) if incorp_date else str(SNAPSHOT_DATE - timedelta(days=2000)),
            None,
            str(acc_next_due) if acc_next_due else None,
            str(acc_last_made) if acc_last_made else None,
            acc_cat,
            str(conf_next_due) if conf_next_due else str(SNAPSHOT_DATE + timedelta(days=60)),
            str(conf_last_made) if conf_last_made else None,
            num_charges, num_outstanding, num_satisfied,
            sic_1, uri, str(SNAPSHOT_DATE)
        ))

    # 4. Synthesize Bank Loan Facilities & Coupled Conduct Telemetry
    print("Synthesizing bilateral commercial facilities and account conduct...")

    rm_names = [
        "Alistair Vance (Head of Commercial Credit - Leeds)",
        "Marcus Thorne (Head of Corporate Debt - Birmingham)",
        "Priya Patel (Mid-Market Relationship Lead - London)",
        "Gareth Edwards (SME Portfolio Manager - Sheffield)"
    ]
    
    facility_types = [
        ("Revolving Credit Facility", 0.40, 3.25),
        ("Commercial Overdraft", 0.35, 4.10),
        ("Term Loan", 0.25, 2.85)
    ]

    mainstream_lenders = [
        "Barclays Bank PLC", "Lloyds Bank PLC", "National Westminster Bank Plc",
        "HSBC UK Bank Plc", "Santander UK plc"
    ]
    
    specialist_lenders = [
        "Commercial Asset Finance Ltd", "Equipment Leasing Direct Ltd",
        "Working Capital Partners Ltd", "Midlands Trade Finance Ltd"
    ]

    corporate_groups = [
        ("GP-0010984", "Apex Industrial Group UK Ltd", 3),
        ("GP-0024512", "Northern Precision Engineering Holdings Ltd", 3),
        ("GP-0038741", "Vanguard National Logistics Group Ltd", 2),
        ("GP-0049210", "Pennine Thermal & Building Services Group Ltd", 2),
        ("GP-0056193", "Yorkshire Food Processing Holdings Ltd", 2),
        ("GP-0067342", "Midlands Advanced Tooling Holdings Ltd", 2),
        ("GP-0078125", "Britannia Freight & Marine Group Ltd", 2)
    ]

    # Pre-calculate realistic dispersed facility limits and drawn balances matching exact totals
    def gen_dispersed(n, target_total, min_p, max_p, s):
        random.seed(s)
        mean_v = target_total / n
        raw = [round(mean_v * random.uniform(min_p, max_p), 2) for _ in range(n)]
        sum_r = sum(raw)
        scaled = [round(r / sum_r * target_total, 2) for r in raw]
        scaled[0] = round(scaled[0] + round(target_total - sum(scaled), 2), 2)
        return scaled

    # Red
    red_limits = gen_dispersed(11, 7110000.00, 0.85, 1.15, 101)
    random.seed(102)
    red_utils = [random.uniform(0.92, 0.97) for _ in range(11)]
    raw_rd = [round(lim * u, 2) for lim, u in zip(red_limits, red_utils)]
    red_drawn = [round(d / sum(raw_rd) * 6748211.61, 2) for d in raw_rd]
    red_drawn[0] = round(red_drawn[0] + round(6748211.61 - sum(red_drawn), 2), 2)

    # Amber
    amber_limits = gen_dispersed(32, 25951000.00, 0.80, 1.20, 201)
    random.seed(202)
    amber_utils = [random.uniform(0.82, 0.89) for _ in range(32)]
    raw_ad = [round(lim * u, 2) for lim, u in zip(amber_limits, amber_utils)]
    amber_drawn = [round(d / sum(raw_ad) * 22255758.13, 2) for d in raw_ad]
    amber_drawn[0] = round(amber_drawn[0] + round(22255758.13 - sum(amber_drawn), 2), 2)

    # Green
    green_limits = gen_dispersed(207, 174784000.00, 0.70, 1.30, 301)
    random.seed(302)
    green_utils = [random.uniform(0.35, 0.58) for _ in range(207)]
    raw_gd = [round(lim * u, 2) for lim, u in zip(green_limits, green_utils)]
    green_drawn = [round(d / sum(raw_gd) * 81502331.23, 2) for d in raw_gd]
    green_drawn[0] = round(green_drawn[0] + round(81502331.23 - sum(green_drawn), 2), 2)

    # Pre-assign corporate groups to 16 borrowers; remainder are Standalone
    group_assignments = {}
    curr_idx = 0
    for gid, gname, size in corporate_groups:
        for _ in range(size):
            if curr_idx < len(selected_cohort):
                group_assignments[curr_idx] = (gid, gname)
                curr_idx += 1

    total_portfolio_limit = 0.0
    total_portfolio_drawn = 0.0

    # Ensure deterministic facility parameters
    for idx, c in enumerate(selected_cohort, start=1):
        comp_num = c['CompanyNumber']
        post_code = c.get('RegAddress.PostCode', 'LS1 5QL')
        num_outstanding = int(c.get('Mortgages.NumMortOutstanding', 0) or 0)

        loan_id = f"LN-UK-2026{idx:03d}"
        client_name = f"Commercial Borrower BRW-{idx:04d}"

        # Group membership
        if (idx - 1) in group_assignments:
            parent_group_id, parent_group_name = group_assignments[idx - 1]
        else:
            parent_group_id, parent_group_name = None, None

        # Dispersed, realistic commercial loan limits and balances matching exact totals
        if idx <= 11:
            # Red cohort: 11 facilities (Total Drawn: £6,748,211.61, Total Limit: £7,110,000.00)
            limit = red_limits[idx - 1]
            drawn = red_drawn[idx - 1]
            # Dispersed acute conduct telemetry
            dd_patterns = [3, 2, 3, 3, 2, 3, 2, 3, 2, 3, 2]
            od_patterns = [65, 62, 70, 64, 61, 68, 63, 66, 61, 67, 63]
            unpaid_dd_count = dd_patterns[idx - 1]
            consecutive_od_pinned = od_patterns[idx - 1]
            hard_core_flag = 1
        elif idx <= 43:
            # Amber cohort: 32 facilities (Total Drawn: £22,255,758.13, Total Limit: £25,951,000.00)
            a_idx = idx - 12
            limit = amber_limits[a_idx]
            drawn = amber_drawn[a_idx]
            # Moderate conduct strain
            unpaid_dd_count = 1 if a_idx % 2 == 0 else 2
            consecutive_od_pinned = 25 if a_idx < 12 else 45
            hard_core_flag = 1 if consecutive_od_pinned >= 30 else 0
        else:
            # Green cohort: 207 facilities (Total Drawn: £81,502,331.23, Total Limit: £174,784,000.00)
            g_idx = idx - 44
            limit = green_limits[g_idx]
            drawn = green_drawn[g_idx]
            unpaid_dd_count = 0
            consecutive_od_pinned = 8 if g_idx % 4 == 0 else 0
            hard_core_flag = 0
        
        fac_choice = random.choices(facility_types, weights=[40, 35, 25])[0]
        fac_type = fac_choice[0]
        margin = fac_choice[2] + round(random.uniform(-0.25, 0.65), 2)
        
        orig_date = SNAPSHOT_DATE - timedelta(days=random.randint(180, 1100))
        mat_date = orig_date + timedelta(days=random.randint(730, 1825))
        rm_name = random.choice(rm_names)
        region = get_region(post_code)
        security = "First Fixed Charge" if idx % 3 == 0 else ("Floating Charge" if idx % 2 == 0 else "Unsecured")

        # Insert into tbl_borrower_portfolio
        cursor.execute("""
        INSERT INTO tbl_borrower_portfolio VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            loan_id, comp_num, client_name, parent_group_id, parent_group_name,
            fac_type, drawn, limit, margin, str(orig_date), str(mat_date),
            rm_name, region, security,
            unpaid_dd_count, consecutive_od_pinned, hard_core_flag
        ))
        
        total_portfolio_limit += limit
        total_portfolio_drawn += drawn

        # Populate Charges Register
        if num_outstanding > 0:
            for chg_idx in range(1, num_outstanding + 1):
                charge_id = f"CHG-{comp_num}-{chg_idx}"
                chg_date = SNAPSHOT_DATE - timedelta(days=random.randint(30, 800))
                deliv_date = chg_date + timedelta(days=random.randint(2, 14))
                lender = random.choice(mainstream_lenders) if chg_idx == 1 else random.choice(specialist_lenders)
                chg_type = "fixed_and_floating" if chg_idx == 1 else "specific_asset_lease"
                    
                cursor.execute("""
                INSERT INTO tbl_charges_register VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                    charge_id, comp_num, chg_idx, str(chg_date), str(deliv_date),
                    'outstanding', chg_type, lender, 'COMMERCIAL_LENDER', 0
                ))

    conn.commit()

    print("\n" + "=" * 75)
    print("PORTFOLIO INGESTION RECONCILIATION SUMMARY")
    print(f"Total Corporate Borrowers Ingested : {len(selected_cohort)}")
    print(f"Total Commercial Facility Limits   : £{total_portfolio_limit:,.2f}")
    print(f"Total Current Drawn Exposure       : £{total_portfolio_drawn:,.2f}")
    print(f"Average Portfolio Utilization Rate : {total_portfolio_drawn/total_portfolio_limit*100:.1f}%")
    print("=" * 75)

    # 5. Load Scoring Views
    views_path = os.path.join(SQL_DIR, '02_risk_scoring_views.sql')
    if os.path.exists(views_path):
        print(f"\nLoading analytical views from sql/02_risk_scoring_views.sql...")
        with open(views_path, 'r', encoding='utf-8') as f:
            views_sql = f.read()
        cursor.executescript(views_sql)
        conn.commit()
        print("Risk scoring views loaded and materialized successfully.")

    # 6. Verify Non-Circularity and Tier Distribution
    cursor.execute("""
    SELECT operational_risk_tier, COUNT(*), ROUND(SUM(drawn_amount), 2), ROUND(SUM(facility_limit), 2), ROUND(AVG(statutory_distress_score), 1)
    FROM vw_portfolio_triage_actions
    GROUP BY operational_risk_tier
    ORDER BY CASE operational_risk_tier WHEN 'RED_CRITICAL' THEN 1 WHEN 'AMBER_ELEVATED' THEN 2 ELSE 3 END;
    """)
    rows = cursor.fetchall()
    print("\nPORTFOLIO RISK TIER SUMMARY:")
    print(f"{'Tier':<18} | {'Count':<6} | {'Drawn (£)':<16} | {'Limit (£)':<16} | {'Avg Score'}")
    print("-" * 70)
    for r in rows:
        print(f"{r[0]:<18} | {r[1]:<6} | £{r[2]:>14,.2f} | £{r[3]:>14,.2f} | {r[4]}")

    cursor.execute("""
    SELECT 
        CASE WHEN accounts_days_overdue > 0 THEN 'Late Filer' ELSE 'On-Time Filer' END as filing_status,
        operational_risk_tier,
        COUNT(*) as cnt
    FROM vw_portfolio_triage_actions
    GROUP BY 1, 2
    ORDER BY 1, 2;
    """)
    matrix = cursor.fetchall()
    print("\nNON-CIRCULARITY VERIFICATION (Filing Status x Risk Tier):")
    for m in matrix:
        print(f"  {m[0]:<14} x {m[1]:<18} : {m[2]} borrowers")

    cursor.execute("SELECT COUNT(*) FROM vw_portfolio_triage_actions WHERE operational_assignment_routing = 'BSRU_WORKOUT_SQUAD';")
    bsru_cnt = cursor.fetchone()[0]
    print(f"\nBSRU Specialist Workout Queue: {bsru_cnt} files (Capacity: 10-14 files)")

    conn.close()
    print(f"\nPipeline execution complete. Database: {DB_PATH} ready.")

if __name__ == '__main__':
    run_ingestion()
