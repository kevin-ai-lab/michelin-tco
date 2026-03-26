import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tco_math import calculate_tco

st.set_page_config(page_title="MICHELIN B2B TCO Calculator", layout="wide", page_icon="🛞", initial_sidebar_state="expanded")

# Inject premium CSS (Custom UI Typography & Metrics)
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

    /* Giant Fleet Savings Metric */
    .giant-savings-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(252, 229, 0, 0.05);
        border: 2px solid rgba(252, 229, 0, 0.2);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(252, 229, 0, 0.1);
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
        text-shadow: 0 0 20px rgba(252, 229, 0, 0.3);
    }
    .giant-savings-subtext {
        color: #94A3B8;
        font-size: 1rem;
        margin-top: 0.5rem;
    }

    /* Demoted Break Even Metric */
    .secondary-metric {
        background: rgba(39, 80, 155, 0.1);
        border: 1px solid rgba(39, 80, 155, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    .sec-title {
        color: #CBD5E1;
        font-size: 1rem;
        font-weight: 500;
    }
    .sec-value {
        color: #FFFFFF;
        font-size: 1.5rem;
        font-weight: 700;
    }

    /* Streamlit Metric Overrides */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
    }
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

</style>
""", unsafe_allow_html=True)

# Main Title Let's align it left
st.markdown('<h1><span class="yellow-text">MICHELIN</span> TCO Calculator</h1>', unsafe_allow_html=True)

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.markdown('<h2>Parameters</h2>', unsafe_allow_html=True)
    
    with st.expander("⚙️ Fleet Baseline", expanded=True):
        colA, colB = st.columns(2)
        num_trucks = colA.number_input("Total Class 8 Trucks", value=50, step=1)
        tires_per_truck = colB.number_input("Tires per Truck", value=18, step=1)
        
        annual_miles = st.number_input("Annual Miles/Truck", value=100000, step=1000)
        mpg = st.number_input("Fleet Avg MPG", value=6.5, step=0.1)
        fuel_price = st.number_input("Fuel Price / Gallon ($)", value=4.00, step=0.05)
        
        colC, colD = st.columns(2)
        downtime_cost = colC.number_input("Downtime Cost/Hr ($)", value=120.0, step=5.0)
        downtime_hours = colD.number_input("Hours per Event", value=3.0, step=0.5)

    with st.expander("⚠️ Current Tire (Competitor)", expanded=True):
        comp_price = st.number_input("Purchase Price ($)", value=350.0, step=10.0, key="c_p")
        comp_casing = st.number_input("Casing Value ($)", value=40.0, step=5.0, key="c_c")
        comp_life = st.number_input("Expected Tread Mileage", value=120000, step=5000, key="c_l")
        comp_events = st.number_input("Annual Events / Truck", value=1.5, step=0.1, key="c_e")
        comp_event_cost = st.number_input("Cost per Service Call ($)", value=350.0, step=10.0, key="c_ec")

    with st.expander("🛡️ Michelin Tire", expanded=True):
        mich_price = st.number_input("Quoted Price ($)", value=550.0, step=10.0, key="m_p")
        mich_casing = st.number_input("Guaranteed Casing ($)", value=120.0, step=10.0, key="m_c")
        mich_life = st.number_input("Projected Tread Mileage", value=180000, step=5000, key="m_l")
        mich_events = st.number_input("Annual Events / Truck", value=0.8, step=0.1, key="m_e")
        mich_event_cost = st.number_input("Cost per Service Call ($)", value=350.0, step=10.0, key="m_ec")
        mich_fuel_gain = st.number_input("Fuel Efficiency Gain (%)", value=3.0, step=0.1, key="m_fg") / 100.0

    with st.expander("💵 Payload Revenue Gain (X One)", expanded=False):
        weight_saved = st.number_input("Weight Saved (lbs) / Truck", value=0.0, step=100.0)
        revenue_per_lb = st.number_input("Revenue per lb ($)", value=0.05, step=0.01)
        annual_trips = st.number_input("Billable Trips / Year", value=0, step=10)


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

extra_rev = {
    'weightSaved': weight_saved,
    'revenuePerLb': revenue_per_lb,
    'annualTrips': annual_trips
}

# Calculate TCO
tco = calculate_tco(fleet_data, comp_tire, mich_tire, extra_rev)

# ----------------- MAIN CONTENT AREA -----------------

# 1. Giant Savings KPI
st.markdown(f"""
<div class="giant-savings-container">
    <div class="giant-savings-label">Fleet Annual Savings</div>
    <div class="giant-savings-value">${tco['fleetSavings']:,.0f}</div>
    <div class="giant-savings-subtext">Optimized total cost reduction across {num_trucks} trucks</div>
</div>
""", unsafe_allow_html=True)

# 2. Secondary Metrics Row
col1, col2 = st.columns(2)
with col1:
    st.metric("Savings Per Truck", f"${tco['annualSavingsPerTruck']:,.0f}")
with col2:
    be_val = f"{tco['breakEvenMiles']:,.0f} mi" if tco['breakEvenMiles'] > 0 else "N/A"
    st.markdown(f"""
    <div class="secondary-metric">
        <div class="sec-title">Break-Even Mileage</div>
        <div class="sec-value">{be_val}</div>
    </div>
    """, unsafe_allow_html=True)

# 3. Waterfall Chart for Cost Bridge
st.markdown("### Total Cost of Ownership Bridge (Per Truck)")

comp_total = tco['competitor']['total']
mich_total = tco['michelin']['total']

# Delta calculations (From Competitor to Michelin)
# Positive means Michelin costs MORE (upward step)
# Negative means Michelin costs LESS (downward step - savings)
hw_delta = tco['michelin']['hardware'] - tco['competitor']['hardware']
fuel_delta = tco['michelin']['fuel'] - tco['competitor']['fuel']
dt_delta = tco['michelin']['downtime'] - tco['competitor']['downtime']
payload_delta = -tco['michelin']['payload'] # Payload is pure savings

x_labels = ["Competitor Total", "Hardware Diff", "Fuel Savings", "Downtime Savings", "Payload Rev", "Michelin Total"]
y_values = [comp_total, hw_delta, fuel_delta, dt_delta, payload_delta, mich_total]
measures = ["absolute", "relative", "relative", "relative", "relative", "total"]

fig = go.Figure(go.Waterfall(
    name="TCO",
    orientation="v",
    measure=measures,
    x=x_labels,
    textposition="outside",
    # Label text formats
    text=[f"${v:,.0f}" for v in y_values],
    y=y_values,
    connector={"line": {"color": "rgb(63, 63, 63)", "width": 1, "dash": "dot"}},
    decreasing={"marker": {"color": "#4ade80"}},  # Green for savings (decrease in cost)
    increasing={"marker": {"color": "#ef4444"}},  # Red for added cost (like higher hardware price)
    totals={"marker": {"color": "#27509B"}},      # Michelin Blue for totals
))

fig.update_layout(
    title="",
    waterfallgap=0.2,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#FFFFFF'),
    yaxis=dict(
        gridcolor='rgba(255,255,255,0.1)', 
        tickprefix='$', 
        zeroline=True, 
        zerolinecolor='rgba(255,255,255,0.2)'
    ),
    xaxis=dict(gridcolor='rgba(255,255,255,0.0)'),
    margin=dict(l=40, r=40, t=20, b=40),
    hovermode='x unified'
)

fig.update_traces(
    hovertemplate="<b>%{x}</b><br>Amount: $%{y:,.0f}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

if tco['michelin']['payload'] > 0:
    st.info(f"Michelin TCO includes an embedded payload revenue offset of **${tco['michelin']['payload']:,.0f}** per truck.")
