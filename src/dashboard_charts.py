# -*- coding: utf-8 -*-
"""
Project Sentinel: Commercial Credit Risk & Early-Warning Surveillance Engine
Module: Institutional Chart Generators (Plotly Clean MI Theme)
Author: Dhruv Chaudhary, Commercial Risk Analytics Case Study
"""

import plotly.graph_objects as go
import pandas as pd

def build_fig1_exposure_donut(df):
    green_exposure = df[df['operational_risk_tier'] == 'GREEN_STANDARD']['current_drawn_exposure'].sum()
    amber_exposure = df[df['operational_risk_tier'] == 'AMBER_ELEVATED']['current_drawn_exposure'].sum()
    red_exposure = df[df['operational_risk_tier'] == 'RED_CRITICAL']['current_drawn_exposure'].sum()
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=['Standard Surveillance (Green)', 'Intensive Care (Amber)', 'Critical Workout (Red)'],
        values=[green_exposure, amber_exposure, red_exposure],
        hole=0.62,
        marker=dict(colors=['#059669', '#d97706', '#dc2626'], line=dict(color='#ffffff', width=2)),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        hovertemplate='<b>%{label}</b><br>Drawn Exposure: \u00A3%{value:,.2f}<br>Share: %{percent}<extra></extra>'
    ))
    fig.update_layout(
        title=dict(
            text=f'<b>Commercial Exposure by Risk Classification</b><br><span style="font-size:12px; color:#64748b;">Total Active Drawn Balance: \u00A3{df["current_drawn_exposure"].sum()/1e6:.1f}M ({len(df)} Facilities)</span>',
            font=dict(size=14, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#0f172a')
        ),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#334155'),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.18, xanchor='center', x=0.5, font=dict(size=11)),
        margin=dict(t=55, b=45, l=20, r=20)
    )
    return fig

def build_fig2_materiality_scatter(df):
    color_map = {
        'RED_CRITICAL': '#dc2626',
        'AMBER_ELEVATED': '#d97706',
        'GREEN_STANDARD': '#059669'
    }
    
    fig = go.Figure()
    for tier, color in color_map.items():
        subset = df[df['operational_risk_tier'] == tier]
        tier_label = tier.replace('_', ' ').title()
        fig.add_trace(go.Scatter(
            x=subset['statutory_distress_score'],
            y=subset['current_drawn_exposure'],
            mode='markers',
            name=tier_label,
            marker=dict(
                size=subset['unpaid_dd_count_90d'].apply(lambda x: 8 + x * 4),
                color=color,
                opacity=0.85,
                line=dict(width=1, color='#ffffff')
            ),
            text=subset['loan_id'].apply(lambda x: f'Borrower Ref: BRW-{x.split("-")[-1][-4:]}'),
            customdata=subset[['loan_id', 'materiality_exposure_score', 'unpaid_dd_count_90d', 'consecutive_od_pinned_days', 'operational_assignment_routing']],
            hovertemplate=(
                '<b>%{text}</b> (Facility: %{customdata[0]})<br>' +
                'Portfolio Scope: SME & Mid-Market Loan Book<br>' +
                'Distress Score: %{x}/100<br>' +
                'Drawn Exposure: \u00A3%{y:,.2f}<br>' +
                'Materiality Index: %{customdata[1]}<br>' +
                'Unpaid HMRC DDs: %{customdata[2]} | Overdraft Pinned: %{customdata[3]} days<br>' +
                'Operational Queue: <b>%{customdata[4]}</b><extra></extra>'
            )
        ))

    # Add shaded BSRU priority zone
    fig.add_shape(
        type='rect',
        x0=70, x1=102, y0=350000, y1=df['current_drawn_exposure'].max() * 1.05,
        fillcolor='rgba(220, 38, 38, 0.08)',
        line=dict(color='#dc2626', width=1.5, dash='dash'),
    )
    bsru_count = len(df[df['operational_assignment_routing'] == 'BSRU_WORKOUT_SQUAD'])
    fig.add_annotation(
        x=85, y=df['current_drawn_exposure'].max() * 0.88,
        text=f'<b>BSRU WORKOUT ZONE</b><br>Score \u2265 70 & \u2265 \u00A3350k ({bsru_count} Files)',
        showarrow=False,
        align='center',
        bgcolor='rgba(255, 255, 255, 0.90)',
        bordercolor='#dc2626',
        borderwidth=1,
        borderpad=4,
        font=dict(size=9.5, color='#991b1b', family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")
    )

    fig.update_layout(
        title=dict(
            text='<b>2D Risk Matrix: Distress Severity vs. Facility Exposure</b><br><span style="font-size:12px; color:#64748b;">Marker Size: 90-Day Unpaid Direct Debits (HMRC Focus)</span>',
            font=dict(size=14, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#0f172a')
        ),
        xaxis=dict(
            title='<b>Composite Distress Score (0 - 100)</b>',
            gridcolor='#f1f5f9',
            zerolinecolor='#cbd5e1',
            color='#475569'
        ),
        yaxis=dict(
            title='<b>Current Drawn Exposure (\u00A3)</b>',
            gridcolor='#f1f5f9',
            zerolinecolor='#cbd5e1',
            color='#475569'
        ),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#334155'),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=-0.22, xanchor='center', x=0.5, font=dict(size=11)),
        margin=dict(t=55, b=65, l=60, r=30)
    )
    return fig

def build_fig3_queue_capacity(df):
    routing_summary = df.groupby('operational_assignment_routing').agg(
        facilities=('loan_id', 'count'),
        total_drawn=('current_drawn_exposure', 'sum'),
        avg_materiality=('materiality_exposure_score', 'mean')
    ).reset_index().sort_values('total_drawn', ascending=True)

    routing_colors = {
        'BSRU_WORKOUT_SQUAD': '#dc2626',
        'SPECIAL_SITUATIONS_WATCH': '#ea580c',
        'RM_INTENSIVE_CARE': '#d97706',
        'STANDARD_SURVEILLANCE': '#059669'
    }

    fig = go.Figure()
    clean_titles = {
        'BSRU_WORKOUT_SQUAD': 'BSRU Workout Squad',
        'SPECIAL_SITUATIONS_WATCH': 'Special Situations Watch',
        'RM_INTENSIVE_CARE': 'RM Intensive Care',
        'STANDARD_SURVEILLANCE': 'Standard Surveillance'
    }
    fig.add_trace(go.Bar(
        y=[clean_titles.get(r, r.replace('_', ' ').title()) for r in routing_summary['operational_assignment_routing']],
        x=routing_summary['total_drawn'],
        orientation='h',
        marker=dict(
            color=[routing_colors.get(r, '#2563eb') for r in routing_summary['operational_assignment_routing']],
            line=dict(color='#ffffff', width=1)
        ),
        text=[f'\u00A3{x/1e6:.1f}M ({n} files)' for x, n in zip(routing_summary['total_drawn'], routing_summary['facilities'])],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Drawn Balance: \u00A3%{x:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>Operational Routing & Workouts Capacity Distribution</b><br><span style="font-size:12px; color:#64748b;">Specialist Caseload Routing by Balance Sheet Materiality</span>',
            font=dict(size=14, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#0f172a')
        ),
        xaxis=dict(title='<b>Total Drawn Exposure (\u00A3)</b>', gridcolor='#f1f5f9', color='#475569'),
        yaxis=dict(color='#475569', tickfont=dict(size=11)),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#334155'),
        margin=dict(t=55, b=50, l=150, r=30)
    )
    return fig

def build_fig4_loss_waterfall(df):
    red_df = df[df['operational_risk_tier'] == 'RED_CRITICAL']
    amber_df = df[df['operational_risk_tier'] == 'AMBER_ELEVATED']
    
    red_drawn = red_df['current_drawn_exposure'].sum()
    red_undrawn = red_df['undrawn_facility_exposure'].sum()
    amber_drawn = amber_df['current_drawn_exposure'].sum()
    
    # Reconciled Empirical Loss Mitigation Mechanics:
    # 1. Consensual Restructuring & Turnaround (+20% LGD, 75% -> 55% at PD 42.8%)
    consensual_turnaround_lift = red_drawn * 0.428 * (0.75 - 0.55)
    
    # 2. Discretionary Undrawn Headroom Containment (freezing 75% pre-insolvency draw at baseline loss params)
    headroom_containment_lift = red_undrawn * 0.75 * 0.428 * 0.75
    
    # 3. Amber Early Remediation & Default Prevention (curing 20% of Amber cohort at PD 12.5%, LGD 65%)
    amber_remediation_lift = amber_drawn * 0.125 * 0.20 * 0.65
    
    # 4. Sidecar Surveillance Operational Cost
    sentinel_annual_cost = 210000.0
    
    # Net Preserved Capital Benefit
    net_preserved_benefit = consensual_turnaround_lift + headroom_containment_lift + amber_remediation_lift - sentinel_annual_cost

    fig = go.Figure(go.Waterfall(
        name='Capital Preservation',
        orientation='v',
        measure=['relative', 'relative', 'relative', 'relative', 'total'],
        x=[
            'Consensual Turnaround Lift',
            'Headroom Containment Lift',
            'Amber Early Remediation',
            'Surveillance Operating Cost',
            'Net Preserved Capital Benefit'
        ],
        textposition='outside',
        text=[
            f'+\u00A3{consensual_turnaround_lift/1e6:.2f}M',
            f'+\u00A3{headroom_containment_lift/1e6:.2f}M',
            f'+\u00A3{amber_remediation_lift/1e6:.2f}M',
            f'-\u00A3{sentinel_annual_cost/1e6:.2f}M',
            f'+\u00A3{net_preserved_benefit/1e6:.2f}M'
        ],
        y=[
            consensual_turnaround_lift,
            headroom_containment_lift,
            amber_remediation_lift,
            -sentinel_annual_cost,
            0
        ],
        connector={'line': {'color': '#94a3b8'}},
        decreasing={'marker': {'color': '#dc2626'}},
        increasing={'marker': {'color': '#059669'}},
        totals={'marker': {'color': '#2563eb'}}
    ))
    fig.update_layout(
        title=dict(
            text=f'<b>Capital Preservation Waterfall: Loss Mitigation Mechanics</b><br><span style="font-size:12px; color:#64748b;">Evaluated on Commercial Loan Book (\u00A3{df["current_drawn_exposure"].sum()/1e6:.1f}M Drawn; Reconciled Basel Expected Loss Model)</span>',
            font=dict(size=14, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#0f172a')
        ),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", color='#334155'),
        yaxis=dict(title='<b>Preserved Capital (\u00A3)</b>', gridcolor='#f1f5f9', color='#475569'),
        xaxis=dict(color='#475569', tickangle=-10, tickfont=dict(size=10)),
        margin=dict(t=55, b=65, l=60, r=30)
    )
    return fig
