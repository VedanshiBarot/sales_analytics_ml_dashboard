import streamlit as st
import pandas as pd
import joblib
from sqlalchemy import create_engine
import plotly.express as px

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(
    page_title="AI Investment Opportunity Insights",
    layout="wide"
)

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
    color: #FBBF24;  /* Neon yellow for active */
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
    <a href="/revenue_forecast" target="_self">Revenue Forecast</a>
    <a href="/Investment_Insights" target="_self" class="active">Investment Insights</a>
    <a href="/Product_Simulation" target="_self">Product Simulation</a>
</div>
""", unsafe_allow_html=True)

st.title("AI Investment Opportunity Insights")
st.write("Predict revenue, profit and investment potential using AI.")

# ----------------------------------------------------
# DATABASE CONNECTION
# ----------------------------------------------------
from supabase import create_client
import os

# ----------------------------------------------------
# SUPABASE CONNECTION
# ----------------------------------------------------
url = "https://yqtsngkummwynbihfyhb.supabase.co"
key = "sb_publishable_66ecgNWLttxallBAfY88WA_MLHkMk8B"

# print("SUPABASE URL:", url)
supabase = create_client(url, key)

# ----------------------------------------------------
# LOAD DATA FROM VIEW (IMPORTANT CHANGE)
# ----------------------------------------------------
res = supabase.table("vw_sales_enriched").select("*").execute()
df = pd.DataFrame(res.data)

# Rename columns to match existing code (NO OTHER CHANGES)
df.rename(columns={
    "quantityOrdered": "units_sold",
    "line_revenue": "revenue"
}, inplace=True)

# ----------------------------------------------------
# NEW PROFIT CALCULATION (Independent of revenue)
# ----------------------------------------------------
# Assume variable cost between 60%-75% of price
df["cost_per_unit"] = df["priceEach"] * (0.60 + (df["priceEach"] % 0.15))
df["profit"] = (df["priceEach"] - df["cost_per_unit"]) * df["units_sold"]

# ----------------------------------------------------
# BUSINESS FEATURES (same as training)
# ----------------------------------------------------
vendor_avg = df.groupby("productVendor")["revenue"].mean()
office_avg = df.groupby("officeCode")["revenue"].mean()
product_avg = df.groupby("productLine")["revenue"].mean()

# NEW PROFIT FEATURES
vendor_profit_avg = df.groupby("productVendor")["profit"].mean()
office_profit_avg = df.groupby("officeCode")["profit"].mean()
product_profit_avg = df.groupby("productLine")["profit"].mean()

df["vendor_avg_revenue"] = df["productVendor"].map(vendor_avg)
df["office_avg_revenue"] = df["officeCode"].map(office_avg)
df["product_avg_revenue"] = df["productLine"].map(product_avg)
df["vendor_avg_profit"] = df["productVendor"].map(vendor_profit_avg)
df["office_avg_profit"] = df["officeCode"].map(office_profit_avg)
df["product_avg_profit"] = df["productLine"].map(product_profit_avg)

df["prev_month_revenue"] = df["revenue"].rolling(2).mean().fillna(df["revenue"])
df["prev_month_profit"] = df["profit"].rolling(2).mean().fillna(df["profit"])

# ----------------------------------------------------
# LOAD MODELS
# ----------------------------------------------------
revenue_model = joblib.load(
    "ml/models/investment_revenue_model.pkl"
)
profit_model = joblib.load(
    "ml/models/investment_profit_model.pkl"
)

# ----------------------------------------------------
# LOAD ENCODERS
# ----------------------------------------------------
country_encoder = joblib.load(
    "ml/models/country_encoder.pkl"
)
office_encoder = joblib.load(
    "ml/models/office_encoder.pkl"
)
productline_encoder = joblib.load(
    "ml/models/productline_encoder.pkl"
)
vendor_encoder = joblib.load(
    "ml/models/vendor_encoder.pkl"
)

# ----------------------------------------------------
# USER INPUTS
# ----------------------------------------------------
st.subheader("Investment Scenario")
col1, col2 = st.columns(2)

with col1:
    country = st.selectbox(
        "Country",
        sorted(df["country"].unique())
    )
    filtered_office = df[df["country"] == country]

with col2:
    office = st.selectbox(
        "Office",
        sorted(filtered_office["officeCode"].unique())
    )
    filtered_vendor = df[df["officeCode"] == office]

col3, col4 = st.columns(2)
with col3:
    vendor = st.selectbox(
        "Vendor",
        sorted(filtered_vendor["productVendor"].unique())
    )
    filtered_product = df[df["productVendor"] == vendor]

with col4:
    product_line = st.selectbox(
        "Product Line",
        sorted(filtered_product["productLine"].unique())
    )

# ----------------------------------------------------
# SALES INPUTS
# ----------------------------------------------------
col5, col6 = st.columns(2)
with col5:
    units = st.number_input(
        "Expected Units Sold",
        min_value=1,
        value=50
    )
with col6:
    price = st.number_input(
        "Expected Price Per Unit",
        min_value=1.0,
        value=50.0
    )

# ----------------------------------------------------
# PREVIOUS PERFORMANCE
# ----------------------------------------------------
office_data = df[df["officeCode"] == office]
prev_rev = st.selectbox(
    "Previous Month Revenue",
    sorted(office_data["revenue"].round(0).unique())
)
prev_profit = st.selectbox(
    "Previous Month Profit",
    sorted(office_data["profit"].round(0).unique())
)
# ----------------------------------------------------
# PREDICTION
# ----------------------------------------------------
if st.button("Generate AI Investment Insights"):

    country_val = country_encoder.transform([country])[0]
    office_val = office_encoder.transform([office])[0]
    product_val = productline_encoder.transform([product_line])[0]
    vendor_val = vendor_encoder.transform([vendor])[0]

    vendor_avg_rev = vendor_avg[vendor]
    office_avg_rev = office_avg[office]
    product_avg_rev = product_avg[product_line]

    input_df = pd.DataFrame({
        "country_enc": [country_val],
        "office_enc": [office_val],
        "productline_enc": [product_val],
        "vendor_enc": [vendor_val],
        "units_sold": [units],
        "priceEach": [price],
        "vendor_avg_revenue": [vendor_avg_rev],
        "office_avg_revenue": [office_avg_rev],
        "product_avg_revenue": [product_avg_rev],
        "prev_month_revenue": [prev_rev],
        "prev_month_profit": [prev_profit]
    })

    predicted_revenue = revenue_model.predict(input_df)[0]
    predicted_profit = profit_model.predict(input_df)[0]

    # ----------------------------------------------------
    # KPI CARDS
    # ----------------------------------------------------
    st.subheader("Expected Business Impact")
    k1, k2 = st.columns(2)
    k1.metric("Expected Revenue", f"${predicted_revenue:,.2f}")
    k2.metric("Expected Profit", f"${predicted_profit:,.2f}")

    # ----------------------------------------------------
    # INVESTMENT SIGNAL
    # ----------------------------------------------------


    # compute predicted_revenue, predicted_profit
    growth = predicted_profit - prev_profit
    if growth > 3000:
        signal = "High"
        st.success("High Growth Opportunity")
    elif growth > 1000:
        signal = "Moderate"
        st.warning("Moderate Growth Potential")
    else:
        signal = "Low"
        st.error("Low Investment Potential")

    # Strategic Recommendation
    st.subheader("AI Strategic Recommendation")
    # Glassy box CSS
    st.markdown("""
    <style>
    .glass-box {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    padding: 25px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

    
    if signal == "High":
        st.markdown(f"""
        <div class="glass-box">
        • Strong opportunity in <b>{product_line}</b><br><br>
        • Vendor <b>{vendor}</b> shows strong historical performance<br><br>
        • Consider expanding operations in <b>Office {office} ({country})</b><br><br>
        • Increase inventory and marketing investment
        </div>
        """, unsafe_allow_html=True)

    elif signal == "Moderate":
        st.markdown(f"""
        <div class="glass-box">
        • Maintain partnership with <b>{vendor}</b><br><br>
        • Run targeted promotions for <b>{product_line}</b><br><br>
        • Monitor sales growth in <b>{office}</b>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="glass-box">
        • Avoid large investment in <b>{vendor}</b><br><br>
        • Demand appears weak for <b>{product_line}</b><br><br>
        • Consider alternative vendors or markets
        </div>
        """, unsafe_allow_html=True)

    # Visualization
    chart_df = pd.DataFrame({
        "Metric": ["Revenue", "Profit"],
        "Value": [predicted_revenue, predicted_profit]
    })
    fig = px.bar(chart_df, x="Metric", y="Value", title="Predicted Revenue vs Profit")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# HISTORICAL ANALYSIS
# ----------------------------------------------------
st.subheader("Product Line Revenue Performance")
trend = df.groupby("productLine")["revenue"].sum().reset_index()

fig2 = px.bar(
    trend,
    x="productLine",
    y="revenue"
)

st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------
# VENDOR PERFORMANCE
# ----------------------------------------------------
st.subheader("Vendor Revenue Performance")
vendor_perf = df.groupby("productVendor")["revenue"].sum().reset_index()

fig3 = px.bar(
    vendor_perf,
    x="productVendor",
    y="revenue"
)

st.plotly_chart(fig3, use_container_width=True)