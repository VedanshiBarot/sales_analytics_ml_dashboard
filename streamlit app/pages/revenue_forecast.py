import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Revenue Forecast", layout="wide")


# ---------- NAVIGATION BAR ----------
st.markdown("""
<style>

.navbar {
    display: flex;
    justify-content: space-around;
    background-color: #111827;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 25px;
}

.navbar a {
    color: #38BDF8;
    text-decoration: none;
    font-weight: 600;
    font-size: 18px;
    cursor: pointer;
    transition: 0.3s;
}

.navbar a:hover {
    color: #FBBF24;
}

/* Active page styling */
.navbar a.active {
    color: #FBBF24;
    text-shadow: 0px 0px 8px #FBBF24;
    font-weight: 700;
}

/* Hide Sidebar */
[data-testid="stSidebar"] {
    display: none;
}

</style>

<div class="navbar">
<a href="/" target="_self">Home Page</a>
<a href="/Sales_Dashboards" target="_self">Analytics Reports</a>
<a href="/payment_risk_prediction" target="_self">Payment Risk</a>
<a href="/Customer_segmentation" target="_self">Customer Segmentation</a>
<a href="/revenue_forecast" target="_self" class="active">Revenue Forecast</a>
<a href="/Investment_Insights" target="_self">Investment Insights</a>
<a href="/Product_Simulation" target="_self">Product Simulation</a>
</div>
""", unsafe_allow_html=True)


# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

.stApp {
background: linear-gradient(135deg,#0B0F1A,#111827);
color:white;
}

/* KPI Cards */

.kpi-card{
background: rgba(17,24,39,0.8);
padding:28px;
border-radius:16px;
border:1px solid #2E3A59;
text-align:center;
box-shadow:0px 0px 15px rgba(0,0,0,0.4);
}

.kpi-title{
font-size:18px;
color:#9CA3AF;
}

.kpi-value{
font-size:32px;
font-weight:700;
color:#38BDF8;
}

.section-title{
font-size:26px;
font-weight:600;
margin-top:20px;
}

</style>
""", unsafe_allow_html=True)


# ---------- PAGE TITLE ----------
st.title("Revenue Forecast")


# ---------- DATABASE CONNECTION ----------
from supabase import create_client
import pandas as pd

url = "https://yqtsngkummwynbihfyhb.supabase.co"
key = "sb_publishable_66ecgNWLttxallBAfY88WA_MLHkMk8B"

supabase = create_client(url, key)

# fetch your table
data = supabase.table("tbl_sales_forecast").select("*").execute()
df = pd.DataFrame(data.data)
df["month_start"] = pd.to_datetime(df["month_start"])
print(df.head())

# ---------- KPI SECTION ----------
if not df.empty:

    rev_lag_1 = df.iloc[-1]["predicted_revenue"]
    rev_lag_2 = df.iloc[-2]["predicted_revenue"] if len(df) > 1 else rev_lag_1
    rev_lag_3 = df.iloc[-3]["predicted_revenue"] if len(df) > 2 else rev_lag_1

    rev_roll_3 = (rev_lag_1 + rev_lag_2 + rev_lag_3) / 3
    next_month = rev_roll_3

    avg_forecast = df["predicted_revenue"].mean()

    peak_month = df.loc[df["predicted_revenue"].idxmax(), "month_start"]

else:

    next_month = avg_forecast = 0
    peak_month = datetime.today()


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Next Month Revenue</div>
        <div class="kpi-value">${next_month:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Average Forecast Revenue</div>
        <div class="kpi-value">${avg_forecast:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Peak Forecast Month</div>
        <div class="kpi-value">{peak_month.strftime("%b %Y")}</div>
    </div>
    """, unsafe_allow_html=True)


st.divider()


# ---------- USER INPUT SECTION ----------
st.markdown('<div class="section-title">Revenue Prediction Simulator</div>', unsafe_allow_html=True)


# --- Month dropdown: all months from 2003 to next 12 months ---
start_date = datetime(2003, 1, 1)
end_date = datetime.today().replace(day=1)

future_months = [end_date + relativedelta(months=i) for i in range(1, 13)]

all_months = pd.date_range(start=start_date, end=end_date, freq='MS').append(pd.DatetimeIndex(future_months))

month_options = [d.strftime("%b %Y") for d in all_months]

selected_month = st.selectbox("Select Month for Prediction", month_options)


# ---------- INPUTS ----------
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = st.number_input("Total Orders", value=100)

with col2:
    total_customers = st.number_input("Total Customers", value=50)

with col3:
    units_sold = st.number_input("Units Sold", value=200)


col4, col5 = st.columns(2)

with col4:
    avg_price_each = st.number_input("Average Price Each", value=60.0)

with col5:
    rev_lag_1_input = st.number_input("Revenue Last Month", value=50000)


rev_lag_2_input = st.number_input("Revenue 2 Months Ago", value=48000)
rev_lag_3_input = st.number_input("Revenue 3 Months Ago", value=47000)


# ---------- FORMULA-BASED PREDICTION ----------
if st.button("Predict Revenue"):

    rev_roll_3_input = (rev_lag_1_input + rev_lag_2_input + rev_lag_3_input) / 3

    new_order_revenue = units_sold * avg_price_each

    predicted_revenue = 0.6 * rev_roll_3_input + 0.4 * new_order_revenue

    st.success(f"Predicted Revenue for {selected_month}: ${predicted_revenue:,.0f}")


    # ---------- EXPLAINABLE AI ----------
    st.subheader("Possible Causes Affecting Revenue Forecast")

    causes = []

    if new_order_revenue < rev_roll_3_input * 0.8:
        causes.append("Current order volume is lower than past average")

    if units_sold < total_customers:
        causes.append("Low units sold per customer compared to historical trends")

    if avg_price_each < rev_roll_3_input / units_sold:
        causes.append("Average price per unit lower than expected based on past revenue")

    if predicted_revenue < rev_roll_3_input:
        causes.append("Overall predicted revenue below rolling average trend")

    if not causes:
        causes.append("Revenue forecast aligns with historical trends")

    for cause in causes:
        st.warning(f"- {cause}")


    # ---------- ACTIONABLE RECOMMENDATIONS ----------
    st.subheader("Recommended Business Actions")

    recommendations = []

    if predicted_revenue > 1.2 * rev_roll_3_input:
        recommendations.append("High revenue expected. Increase inventory and marketing spend.")

    elif predicted_revenue > 0.8 * rev_roll_3_input:
        recommendations.append("Moderate revenue expected. Maintain current supply levels.")

    else:
        recommendations.append("Low revenue expected. Consider promotional campaigns, discounts, or targeted marketing.")

    for rec in recommendations:
        st.info(f"- {rec}")


st.divider()


# ---------- FORECAST CHART ----------
st.markdown('<div class="section-title">Revenue Forecast Trend</div>', unsafe_allow_html=True)

chart_df = df.copy()

if not chart_df.empty:
    st.line_chart(chart_df.set_index("month_start")["predicted_revenue"], height=420)


st.divider()


# ---------- FORECAST TABLE ----------
st.markdown('<div class="section-title">Forecast Data</div>', unsafe_allow_html=True)

st.dataframe(chart_df, use_container_width=True)

st.divider()


# ---------- AI BUSINESS INSIGHTS ----------
st.subheader("AI Business Insights")

if not df.empty:
    latest = df.iloc[-1]["predicted_revenue"]
    trend = df["predicted_revenue"].pct_change().mean()
else:
    latest = trend = 0
    avg_forecast = 0


insights = []

if trend > 0.05:
    insights.append("Revenue is trending upwards. Consider increasing inventory and marketing spend.")

if trend < -0.05:
    insights.append("Revenue may decline. Review pricing strategy and marketing campaigns.")

if latest > avg_forecast:
    insights.append("Next month revenue is higher than average forecast. Prepare operations for higher demand.")

if latest < avg_forecast:
    insights.append("Next month revenue is below average forecast. Consider promotional strategies.")


for insight in insights:
    st.info(insight)