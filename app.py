import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tco_math import calculate_tco

st.set_page_config(page_title="MICHELIN B2B TCO Calculator", layout="wide", page_icon="🛞", initial_sidebar_state="expanded")

# Michelin Corporate Logo
try:
    st.logo("https://upload.wikimedia.org/wikipedia/commons/4/41/Michelin_Logo.svg")
except Exception:
    pass # Fallback for older Streamlit versions

# Inject Custom Light-Mode B2B CSS
st.markdown("""
<style>
    /* Headers & Text */
    h1, h2, h3, h4, span, p {
        font-family: 'Inter', sans-serif;
    }
    
    .yellow-text {
        color: #FCE500 !important;
        font-weight: 800;
    }
    .blue-text {
        color: #27509B !important;
    }

    /* Giant Fleet Savings Metric - Navy Box for Contrast against #FCE500 */
    .giant-savings-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #27509B;
        border-radius: 12px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .giant-savings-label {
        color: #FFFFFF;
        font-size: 1.25rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .giant-savings-value {
        color: #FCE500;
        font-size: 5rem;
        font-weight: 900;
        line-height: 1;
        /* Text glow removed as requested */
    }
    .giant-savings-subtext {
        color: #E2E8F0;
        font-size: 1rem;
        margin-top: 0.5rem;
    }

    /* Demoted Break Even Metric */
    .secondary-metric {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    .sec-title {
        color: #64748B;
        font-size: 1rem;
        font-weight: 500;
    }
    .sec-value {
        color: #0F172A;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .sec-subtext {
        color: #10B981; /* Green delta color */
        font-size: 0.9rem;
        font-weight: 600;
        text-align: right;
    }

    /* Streamlit Metric Overrides for Light Mode */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main Title (Styling removed logo string from title)
st.markdown('<h1>B2B TCO Calculator</h1>', unsafe_allow_html=True)

# ----------------- REORGANIZED SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.markdown('<h2>Parameters</h2>', unsafe_allow_html=True)
    
    with st.expander("Fleet Profile", expanded=True):
        colA, colB = st.columns(2)
        num_trucks = colA.number_input("Total Class 8 Trucks", value=50, step=1)
        tires_per_truck = colB.number_input("Tires per Truck", value=18, step=1)
        annual_miles = st.number_input("Annual Miles/Truck", value=100000, step=1000)
        mpg = st.number_input("Fleet Avg MPG", value=6.5, step=0.1)

    with st.expander("Operating Costs", expanded=True):
        fuel_price = st.number_input("Fuel Price / Gallon ($)", value=4.00, step=0.05)
        colC, colD = st.columns(2)
        downtime_cost = colC.number_input("Downtime Cost/Hr ($)", value=120.0, step=5.0)
        downtime_hours = colD.number_input("Hours per Event", value=3.0, step=0.5)

    with st.expander("Tire Parameters", expanded=True):
        st.markdown("**Current Tire (Competitor)**")
        comp_price = st.number_input("Purchase Price ($)", value=350.0, step=10.0, key="c_p")
        comp_casing = st.number_input("Casing Value ($)", value=40.0, step=5.0, key="c_c")
        comp_life = st.number_input("Expected Tread Mileage", value=120000, step=5000, key="c_l")
        comp_events = st.number_input("Annual Events / Truck", value=1.5, step=0.1, key="c_e")
        comp_event_cost = st.number_input("Cost per Service Call ($)", value=350.0, step=10.0, key="c_ec")
        
        st.markdown("---")
        st.markdown("**Proposed Michelin Tire**")
        mich_price = st.number_input("Quoted Price ($)", value=550.0, step=10.0, key="m_p")
        mich_casing = st.number_input("Guaranteed Casing ($)", value=120.0, step=10.0, key="m_c")
        mich_life = st.number_input("Projected Tread Mileage", value=180000, step=5000, key="m_l")
        mich_events = st.number_input("Annual Events / Truck", value=0.8, step=0.1, key="m_e")
        mich_event_cost = st.number_input("Cost per Service Call ($)", value=350.0, step=10.0, key="m_ec")
        mich_fuel_gain = st.number_input("Fuel Efficiency Gain (%)", value=3.0, step=0.1, key="m_fg") / 100.0


# Build Data Dicts
fleet_data = {
    'numTrucks': num_trucks,
    'tiresPerTruck': tires_per_truck,
    'annualMiles': annual_miles,
    'mpg': mpg,
    'fuelPrice': fuel_price,
    'downtimeHoursPerEvent': downtime_hours,
    'downtimeCostPerHour': downtime_cost
}

comp_tire = {
    'price': comp_price,
    'casingValue': comp_casing,
    'lifeMiles': comp_life,
    'annualEvents': comp_events,
    'eventCost': comp_event_cost
}

mich_tire = {
    'price': mich_price,
    'casingValue': mich_casing,
    'lifeMiles': mich_life,
    'annualEvents': mich_events,
    'eventCost': mich_event_cost,
    'fuelImprovementPct': mich_fuel_gain
}

# Calculate TCO
tco = calculate_tco(fleet_data, comp_tire, mich_tire)

# Time to ROI Calculation (Months)
if tco['breakEvenMiles'] is not None and annual_miles > 0:
    roi_months = (tco['breakEvenMiles'] / annual_miles) * 12
else:
    roi_months = None

# ----------------- MAIN CONTENT AREA -----------------

# 1. Giant Savings KPI
st.markdown(f"""
<div class="giant-savings-container" title="Fleet Savings = (Competitor Total Annual Cost - Michelin Total Annual Cost) × {num_trucks} Trucks. This combines Tire Hardware (Lifecycle), Fuel Efficiency gains, and Downtime reduction.">
    <div class="giant-savings-label">Fleet Annual Savings</div>
    <div class="giant-savings-value">${tco['fleetSavings']:,.0f}</div>
    <div class="giant-savings-subtext">Optimized total cost reduction across {num_trucks} trucks</div>
</div>
""", unsafe_allow_html=True)

# 2. Secondary Metrics Row
col1, col2 = st.columns(2)
with col1:
    st.metric(
        "Savings Per Truck", 
        f"${tco['annualSavingsPerTruck']:,.0f}",
        help="Net annual operational savings per truck minus any upfront hardware premium."
    )
with col2:
    if tco['breakEvenMiles'] is None:
        be_val = "Never Break Even"
        roi_text = "Operational constraints offset savings"
    elif tco['breakEvenMiles'] == 0:
        be_val = "Instant ROI"
        roi_text = "Michelin is cheaper upfront"
    else:
        be_val = f"{tco['breakEvenMiles']:,.0f} mi"
        roi_text = f"Pays for itself in ~{round(roi_months, 1)} Months"
        
    st.markdown(f"""
    <div class="secondary-metric" title="Break-Even = (Michelin Upfront Premium) ÷ (Operational Savings per Mile). The exact odometer mark where fuel & downtime savings entirely pay off the higher initial tire price.">
        <div>
            <div class="sec-title">Break-Even Mileage</div>
            <div style="font-size: 0.8rem; color: #94A3B8;">Distance to offset initial premium</div>
        </div>
        <div>
            <div class="sec-value">{be_val}</div>
            <div class="sec-subtext">{roi_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 3. Waterfall Chart for Cost Bridge
st.markdown("### Total Cost of Ownership Bridge (Per Truck)")

comp_total = tco['competitor']['total']
mich_total = tco['michelin']['total']

hw_delta = tco['michelin']['hardware'] - tco['competitor']['hardware']
fuel_delta = tco['michelin']['fuel'] - tco['competitor']['fuel']
dt_delta = tco['michelin']['downtime'] - tco['competitor']['downtime']

x_labels = ["Competitor Total", "Tire Cost Difference", "Fuel Savings", "Downtime Savings", "Michelin Total"]
y_values = [comp_total, hw_delta, fuel_delta, dt_delta, mich_total]
measures = ["absolute", "relative", "relative", "relative", "total"]

# Calculate Y-axis truncation range
min_y = min(comp_total, mich_total)
max_y = max(comp_total, mich_total)
if hw_delta > 0:
    max_y = max(max_y, comp_total + hw_delta)

axis_min = min_y * 0.95
axis_max = max_y * 1.05

# Determine dynamic colors for each waterfall bar
bar_colors = [
    "#F97316", # 0: Orange for Competitor Total
    "#EF4444" if hw_delta > 0 else "#10B981", # 1: Red if hardware costs more, green if it saves
    "#EF4444" if fuel_delta > 0 else "#10B981", # 2: Fuel
    "#EF4444" if dt_delta > 0 else "#10B981", # 3: Downtime
    "#27509B"  # 4: Michelin Blue for Final Total
]

fig = go.Figure(go.Waterfall(
    name="TCO",
    orientation="v",
    measure=measures,
    x=x_labels,
    textposition="outside",
    text=[f"${abs(v):,.0f}" for v in y_values],
    y=y_values,
    connector={"line": {"color": "rgb(200, 200, 200)", "width": 1, "dash": "dot"}},
    marker={"color": bar_colors}
))

# Set background to transparent since we are in light mode
fig.update_layout(
    title="",
    waterfallgap=0.3,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#0F172A'),
    yaxis=dict(
        gridcolor='#E2E8F0', 
        tickprefix='$', 
        zeroline=False,
        range=[axis_min, axis_max] # Truncated Y-Axis
    ),
    xaxis=dict(
        gridcolor='rgba(0,0,0,0)',
        tickfont=dict(size=14) # Increased typography
    ),
    margin=dict(l=40, r=40, t=30, b=40),
    hovermode='x unified'
)

fig.update_traces(
    hovertemplate="<b>%{x}</b><br>Amount: %{text}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)
colCTA1, colCTA2, colCTA3 = st.columns([1, 2, 1])
with colCTA2:
    st.button("Contact a Fleet Expert", type="primary", use_container_width=True)
