import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from tco_math import calculate_tco

st.set_page_config(page_title="MICHELIN B2B TCO Calculator", layout="wide", page_icon="🛞", initial_sidebar_state="expanded")

# Removed corporate logo per user request

# Inject Custom Light-Mode B2B CSS
st.markdown("""
<style>
    /* Crush massive default Streamlit top padding to move everything up */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }

    /* Headers & Text */
    h1, h2, h3, h4, span, p {
        font-family: 'Inter', sans-serif;
    }
    
    /* Streamlit Metric Overrides for Light Mode */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 10px 15px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.title("B2B TCO Calculator")


# ----------------- REORGANIZED SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.markdown('<h2>Parameters</h2>', unsafe_allow_html=True)
    
    with st.expander("Fleet Profile", expanded=True):
        colA, colB = st.columns(2)
        with colA:
            num_trucks = st.number_input("Total Trucks", value=50, step=1)
            annual_miles = st.number_input("Annual Miles", value=100000, step=1000)
        with colB:
            tires_per_truck = st.number_input("Tires/Truck", value=18, step=1)
            mpg = st.number_input("Fleet MPG", value=6.5, step=0.1)

    with st.expander("Operating Costs", expanded=True):
        colC, colD = st.columns(2)
        with colC:
            fuel_price = st.number_input("Fuel Price ($)", value=4.00, step=0.05)
            downtime_hours = st.number_input("Hrs per Event", value=3.0, step=0.5)
        with colD:
            downtime_cost = st.number_input("Downtime/Hr ($)", value=120.0, step=5.0)

    with st.expander("Current Tire (Competitor)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            comp_price = st.number_input("Price ($)", value=435.23, step=10.0, key="c_p")
            comp_casing = st.number_input("Casing ($)", value=40.0, step=5.0, key="c_c")
            comp_events = st.number_input("Events/Yr", value=1.5, step=0.1, key="c_e")
        with col2:
            comp_life = st.number_input("Tread Miles", value=100000, step=5000, key="c_l")
            comp_event_cost = st.number_input("Event Cost($)", value=350.0, step=10.0, key="c_ec")
            
    with st.expander("Proposed Michelin Tire", expanded=True):
        col3, col4 = st.columns(2)
        with col3:
            mich_price = st.number_input("Price ($)", value=550.0, step=10.0, key="m_p")
            mich_casing = st.number_input("Casing ($)", value=75.0, step=5.0, key="m_c")
            mich_events = st.number_input("Events/Yr", value=0.8, step=0.1, key="m_e")
        with col4:
            mich_life = st.number_input("Tread Miles", value=180000, step=5000, key="m_l")
            mich_event_cost = st.number_input("Event Cost($)", value=350.0, step=10.0, key="m_ec")
            mich_fuel_gain = st.number_input("Fuel Gain(%)", value=3.0, step=0.1, key="m_fg") / 100.0


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

# ----------------- MAIN DASHBOARD TABS -----------------
tab1, tab2 = st.tabs(["Dashboard", "How the Math Works"])

with tab1:
    # ----------------- COMPRESSED KPIs -----------------

    kpi_col1, kpi_col2, kpi_col3 = st.columns([2, 1, 1])

    with kpi_col1:
        st.markdown(f"""
            <div style="background-color:#27509B; padding:15px; border-radius:8px; text-align:center; color:white; height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size:12px; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">FLEET ANNUAL SAVINGS</div>
                <div style="font-size:36px; font-weight:bold; color:#FCE500; line-height:1;">${tco['fleetSavings']:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with kpi_col2:
        st.metric(
            "Savings Per Truck", 
            f"${tco['annualSavingsPerTruck']:,.2f}",
            help="Combines Tire Lifecycle, Fuel Efficiency, and Downtime reduction."
        )

    with kpi_col3:
        if tco['breakEvenMiles'] is None:
            be_val = "Never Break Even"
            roi_text = "Operational constraints"
        elif tco['breakEvenMiles'] == 0:
            be_val = "Instant ROI"
            roi_text = "Cheaper upfront"
        else:
            be_val = f"{tco['breakEvenMiles']:,.0f} mi"
            roi_text = f"Pays for itself in ~{round(roi_months, 1)} Months"
            
        st.metric("Break-Even Mileage", be_val, delta=roi_text, delta_color="off")

    st.divider()

    # ----------------- CHART SECTION -----------------

    # 3. Waterfall Chart for Cost Bridge
    st.markdown("### Tire-Related Operating Costs & Penalties (Per Truck, over Annual Miles)")

num_trucks = fleet_data['numTrucks']

# 1. Update Starting Bars: Honest upfront purchase prices
mich_tires_initial_cost = fleet_data['tiresPerTruck'] * mich_tire['price']
comp_tires_initial_cost = fleet_data['tiresPerTruck'] * comp_tire['price']

# 2. Keep the Steps Exactly the Same (Delta Math)
tire_step = tco['competitor']['hardware'] - tco['michelin']['hardware']
fuel_step = tco['competitor']['fuel'] - tco['michelin']['fuel']
downtime_step = tco['competitor']['downtime'] - tco['michelin']['downtime']

# Calculate the custom Red Box & Green Box metrics defined by user
red_box_value = comp_tires_initial_cost + tire_step + fuel_step + downtime_step

# 3. Update the Maximum Chart Height: Recalculate max theoretical height
max_y = max(mich_tires_initial_cost, red_box_value)

# 2. Define the new X-Axis Labels
x_labels = [
    "Michelin Upfront<br>Purchase", 
    "Competitor Upfront<br>Purchase",
    "Early Replacement Penalty", 
    "Excess Fuel Cost", 
    "Excess Downtime Cost",
    "Total Competitor<br>Tire Cost"
]

# 3. Format text labels dynamically
def format_label(val):
    if val > 0:
        return f"+${val:,.2f}"
    else:
        return f"-${abs(val):,.2f}"

# Restore all strings natively to the Waterfall to preserve interactive tooltips
text_labels = [
    f"${mich_tires_initial_cost:,.2f}", 
    f"${comp_tires_initial_cost:,.2f}", 
    format_label(tire_step), 
    format_label(fuel_step), 
    format_label(downtime_step),
    f"${red_box_value:,.2f}" 
]

fig = go.Figure()

# 4. Build the Open-Ended Waterfall
fig.add_trace(go.Waterfall(
    name="Cost of Inaction",
    orientation="v",
    measure=["absolute", "absolute", "relative", "relative", "relative", "total"], # Switch last measure to 'total'
    x=x_labels,
    y=[mich_tires_initial_cost, comp_tires_initial_cost, tire_step, fuel_step, downtime_step, 0], 
    text=text_labels,
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Amount: %{text}<extra></extra>",
    increasing={"marker": {"color": "#EF4444"}}, # Red Alert for extra costs
    decreasing={"marker": {"color": "#6B7280"}}, # Grey for savings / downward steps
    totals={"marker": {"color": "#27509B"}},     # Official Michelin Blue for the base bar (Left)
    connector={"line": {"color": "rgb(200, 200, 200)", "width": 1, "dash": "dot"}},
))

# 4.5 Overlay the Grey Competitor Box based on pure purchase price
fig.add_trace(go.Bar(
    x=["Competitor Upfront<br>Purchase"], 
    y=[comp_tires_initial_cost], 
    marker_color="#6B7280", # Grey Box requested by user
    hoverinfo="skip",
    showlegend=False,
    text=[""], # Hide text to prevent double-printing from the active waterfall below it
    textposition="none",
))

# 5. Overlay the Custom Red Box at the identical X-Axis string
fig.add_trace(go.Bar(
    x=["Total Competitor<br>Tire Cost"], 
    y=[red_box_value], 
    marker_color="#EF4444", # Red Box requested by user
    hoverinfo="skip",
    showlegend=False,
    text=[""], # Hide text to prevent double-printing
    textposition="none",
))

# 6. Layout updates (Enforcing strict height constraint and zero vertical margins)
fig.update_layout(
    height=380,
    margin=dict(t=40, b=10, l=10, r=10),
    title="",
    barmode='overlay',
    waterfallgap=0.3,
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#0F172A'),
    yaxis=dict(
        gridcolor='#E2E8F0', 
        tickprefix='$', 
        zeroline=True,
        rangemode='tozero' # Mathematically enforce a 0-floor but allow Plotly to auto-calculate the perfect ceiling for the text
    ),
    xaxis=dict(
        gridcolor='rgba(0,0,0,0)',
        tickfont=dict(size=14) 
    ),
    hovermode='x unified'
)

with tab1:
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with tab2:
    try:
        with open("tco_math_explanation.md", "r") as f:
            st.markdown(f.read())
    except Exception:
        st.info("Mathematical breakdown document is currently unavailable.")

# ----------------- FOOTER DISCLAIMER -----------------
st.markdown("""
    <div style="font-size: 11px; color: #94A3B8; text-align: center; margin-top: 30px;">
        Calculations are estimates based on provided assumptions. Actual fuel efficiency, tire life, casing value, and downtime costs will vary based on route, driver behavior, and maintenance practices. This tool does not constitute a financial guarantee.
    </div>
""", unsafe_allow_html=True)
