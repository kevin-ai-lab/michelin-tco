import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tco_math import calculate_tco

st.set_page_config(page_title="MICHELIN B2B TCO Calculator", layout="wide", page_icon="🛞")

# Inject premium CSS (Glassmorphism + Michelin Colors)
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #1a1c29 0%, transparent 70%);
        color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    
    .yellow-text {
        color: #fde311;
        font-weight: 700;
    }

    /* Metric Cards Glassmorphism */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Specific styling for positive values */
    div[data-testid="stMetricValue"] {
        color: #4ade80 !important;
        font-weight: 700 !important;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 15, 0.9) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Michelin Primary Break-Even Box */
    .break_even_box {
        background-color: #27509b;
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 30px rgba(39, 80, 155, 0.3);
        margin: 1rem 0 2rem 0;
    }
    .be-title { font-size: 1.2rem; font-weight: 500; opacity: 0.9; }
    .be-val { font-size: 2.5rem; font-weight: 700; color: #fde311; margin: 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1><span class="yellow-text">MICHELIN</span> B2B TCO Calculator</h1>', unsafe_allow_html=True)

# Sidebar Inputs
with st.sidebar:
    st.header("⚙️ Fleet & Operations Baseline")
    colA, colB = st.columns(2)
    num_trucks = colA.number_input("Total Class 8 Trucks", value=50, step=1)
    tires_per_truck = colB.number_input("Tires per Truck", value=18, step=1)
    
    annual_miles = st.number_input("Annual Miles/Truck", value=100000, step=1000)
    mpg = st.number_input("Fleet Avg MPG", value=6.5, step=0.1)
    fuel_price = st.number_input("Fuel Price / Gallon ($)", value=4.00, step=0.05)
    
    colC, colD = st.columns(2)
    downtime_cost = colC.number_input("Downtime Cost/Hr ($)", value=120.0, step=5.0)
    downtime_hours = colD.number_input("Hours per Event", value=3.0, step=0.5)

    st.markdown("---")
    st.header("⚠️ Current Tire (Competitor)")
    comp_price = st.number_input("Purchase Price ($)", value=350.0, step=10.0, key="c_p")
    comp_casing = st.number_input("Casing Value (End of Life) ($)", value=40.0, step=5.0, key="c_c")
    comp_life = st.number_input("Expected Tread Mileage", value=120000, step=5000, key="c_l")
    comp_events = st.number_input("Annual Events / Truck", value=1.5, step=0.1, key="c_e")
    comp_event_cost = st.number_input("Cost per Service Call ($)", value=350.0, step=10.0, key="c_ec")

    st.markdown("---")
    st.header("🛡️ Proposed Michelin Tire")
    mich_price = st.number_input("Quoted Price ($)", value=550.0, step=10.0, key="m_p")
    mich_casing = st.number_input("Guaranteed Casing Value ($)", value=120.0, step=10.0, key="m_c")
    mich_life = st.number_input("Projected Tread Mileage", value=180000, step=5000, key="m_l")
    mich_events = st.number_input("Annual Events / Truck", value=0.8, step=0.1, key="m_e")
    mich_event_cost = st.number_input("Cost per Service Call ($)", value=350.0, step=10.0, key="m_ec")
    mich_fuel_gain = st.number_input("Fuel Efficiency Gain (%)", value=3.0, step=0.1, key="m_fg") / 100.0

    st.markdown("---")
    st.header("💵 Payload Revenue Gain (X One)")
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

# Display Dashboard
col1, col2 = st.columns(2)
with col1:
    st.metric(
        label=f"Fleet Annual Savings (Across {num_trucks} trucks)",
        value=f"${tco['fleetSavings']:,.0f}",
        delta="Operating Expense Reduction",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Savings Per Truck",
        value=f"${tco['annualSavingsPerTruck']:,.0f}",
        delta="Per Truck Reduction",
        delta_color="normal"
    )

# Break Even Banner
break_even_val = f"{tco['breakEvenMiles']:,.0f}" if tco['breakEvenMiles'] > 0 else "0"
st.markdown(f"""
<div class="break_even_box">
    <div>
        <div class="be-title">Break-Even Mileage</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Distance required to offset initial premium</div>
    </div>
    <div class="be-val">{break_even_val} mi</div>
</div>
""", unsafe_allow_html=True)

# Plotly Chart
fig = go.Figure()

fig.add_trace(go.Bar(
    x=['Competitor', 'Michelin'],
    y=[tco['competitor']['hardware'], tco['michelin']['hardware']],
    name='Hardware',
    marker_color='rgba(255, 255, 255, 0.4)'
))
fig.add_trace(go.Bar(
    x=['Competitor', 'Michelin'],
    y=[tco['competitor']['fuel'], tco['michelin']['fuel']],
    name='Fuel',
    marker_color='#27509b'
))
fig.add_trace(go.Bar(
    x=['Competitor', 'Michelin'],
    y=[tco['competitor']['downtime'], tco['michelin']['downtime']],
    name='Downtime',
    marker_color='#ef4444'
))

fig.update_layout(
    barmode='stack',
    title="Total Annual Cost of Ownership Per Truck",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#ffffff'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickprefix='$'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig, use_container_width=True)

if tco['michelin']['payload'] > 0:
    st.info(f"Michelin TCO includes an embedded payload revenue offset of **${tco['michelin']['payload']:,.0f}** per truck.")
