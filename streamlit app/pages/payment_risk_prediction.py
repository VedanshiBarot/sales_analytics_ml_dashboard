import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from sqlalchemy import create_engine

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="Payment Risk", layout="wide")

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
    <a href="/payment_risk_prediction" target="_self "class="active" >Payment Risk</a>
    <a href="/Customer_segmentation" target="_self">Customer Segmentation</a>
    <a href="/revenue_forecast" target="_self">Revenue Forecast</a>
    <a href="/Investment_Insights" target="_self">Investment Insights</a>
    <a href="/Product_Simulation" target="_self">Product Simulation</a>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# Load Model + Scaler
# ----------------------------
model_file = "ml/models/risk_model.pkl"
if not os.path.exists(model_file):
    st.error("Payment risk model file not found!")
    st.stop()

data = joblib.load(model_file)
model = data["model"]
scaler = data["scaler"]

# ----------------------------
# Database connection
# ----------------------------
from supabase import create_client, Client

# Replace with your Supabase project URL and anon key
url = "https://yqtsngkummwynbihfyhb.supabase.co"
key = "sb_publishable_66ecgNWLttxallBAfY88WA_MLHkMk8B"


supabase: Client = create_client(url, key)
res = supabase.table("tbl_payment_risk").select("*").execute()
df_risk = pd.DataFrame(res.data)

# Ensure numeric types
numeric_cols = [
    "avg_ship_to_pay_days", "max_ship_to_pay_days", "total_payments",
    "total_amount_paid", "creditLimit", "recency_days", "payment_count"
]

for col in numeric_cols:
    df_risk[col] = pd.to_numeric(df_risk[col], errors="coerce").fillna(0)

# ----------------------------
# User Input: Customer ID
# ----------------------------
customer_ids = df_risk['customerNumber'].tolist()
selected_customer = st.selectbox("Select Customer ID (or enter New)", options=["New"] + customer_ids)

# Prefill input values if existing customer
if selected_customer != "New":
    row = df_risk[df_risk['customerNumber'] == selected_customer].iloc[0]
    avg_ship_to_pay_days_default = int(row['avg_ship_to_pay_days'])
    max_ship_to_pay_days_default = int(row['max_ship_to_pay_days'])
    total_payments_default = int(row['total_payments'])
    total_amount_paid_default = float(row['total_amount_paid'])
    creditLimit_default = float(row['creditLimit'])
    recency_days_default = int(row['recency_days'])
    payment_count_default = int(row['payment_count'])
else:
    avg_ship_to_pay_days_default = 15
    max_ship_to_pay_days_default = 25
    total_payments_default = 5
    total_amount_paid_default = 50000.0
    creditLimit_default = 100000.0
    recency_days_default = 10
    payment_count_default = 3

# ----------------------------
# User Inputs
# ----------------------------
st.markdown("### Enter / Update Customer Payment Details")
col1, col2, col3 = st.columns(3)
with col1:
    avg_ship_to_pay_days = st.number_input(
        "Average Days to Pay",
        min_value=0,
        value=avg_ship_to_pay_days_default
    )
with col2:
    max_ship_to_pay_days = st.number_input(
        "Max Days to Pay",
        min_value=0,
        value=max_ship_to_pay_days_default
    )
with col3:
    total_payments = st.number_input(
        "Total Payments",
        min_value=0,
        value=total_payments_default
    )

col4, col5 = st.columns(2)
with col4:
    total_amount_paid = st.number_input(
        "Total Amount Paid",
        min_value=0.0,
        value=total_amount_paid_default
    )
with col5:
    creditLimit = st.number_input(
        "Credit Limit",
        min_value=0.0,
        value=creditLimit_default
    )

col6, col7 = st.columns(2)
with col6:
    recency_days = st.number_input(
        "Days Since Last Payment",
        min_value=0,
        value=recency_days_default
    )
with col7:
    payment_count = st.number_input(
        "Number of Payments in Recent Period",
        min_value=0,
        value=payment_count_default
    )

st.divider()

# ----------------------------
# Prediction & Recommendations
# ----------------------------
if st.button("Predict Payment Risk"):

    # Input dataframe
    input_df = pd.DataFrame([{
        "avg_ship_to_pay_days": avg_ship_to_pay_days,
        "max_ship_to_pay_days": max_ship_to_pay_days,
        "total_payments": total_payments,
        "total_amount_paid": total_amount_paid,
        "creditLimit": creditLimit,
        "recency_days": recency_days,
        "payment_count": payment_count
    }])

    # Scale input
    input_scaled = scaler.transform(input_df)

    # Predict risk probability
    risk_prob = model.predict_proba(input_scaled)[:, 1][0]

    # Determine risk level, cause hints, and actionable recommendations
    if risk_prob <= 0.3:
        risk_level = "Low"
        risk_color = "rgba(40, 167, 69, 0.6)"
        causes = ["Payment frequency is stable", "Payments are timely"]
        recommendations = ["Maintain current credit limit", "Continue regular monitoring"]
    elif risk_prob <= 0.7:
        risk_level = "Medium"
        risk_color = "rgba(255, 193, 7, 0.6)"
        causes = []
        if avg_ship_to_pay_days > 20:
            causes.append("Average payment delay is high")
        if recency_days > 15:
            causes.append("Customer hasn't paid recently")
        if creditLimit > total_amount_paid * 2:
            causes.append("High credit exposure relative to payments")
        recommendations = [
            "Increase monitoring frequency",
            "Consider partial advance payment for new orders",
            "Engage customer for timely payment"
        ]
    else:
        risk_level = "High"
        risk_color = "rgba(220, 53, 69, 0.6)"
        causes = []
        if avg_ship_to_pay_days > 30:
            causes.append("Payments are significantly delayed")
        if payment_count < 2:
            causes.append("Low number of recent payments")
        if recency_days > 30:
            causes.append("Customer inactive for long period")
        recommendations = [
            "Reduce credit exposure immediately",
            "Follow up with customer for overdue payments",
            "Evaluate risk of new orders carefully"
        ]

    # Display Results
    st.markdown("### Prediction Result")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'''
            <div style="
                padding: 20px;
                text-align: center;
                background-color: rgba(108, 117, 125, 0.3);
                border-radius: 15px;
                color: white;
                font-weight: bold;
                font-size: 24px;
            ">
                Risk Probability<br>{risk_prob:.2f}
            </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
            <div style="
                padding: 20px;
                text-align: center;
                background-color: {risk_color};
                border-radius: 15px;
                color: white;
                font-weight: bold;
                font-size: 24px;
            ">
                Risk Level<br>{risk_level}
            </div>
        ''', unsafe_allow_html=True)

    # Explainable AI: Causes
    st.markdown("### Possible Causes of Risk")
    if causes:
        for cause in causes:
            st.warning(f"- {cause}")
    else:
        st.success("No major risk factors identified")

    # Actionable Recommendations
    st.markdown("### Recommended Actions to Mitigate Risk")
    for rec in recommendations:
        st.info(f"- {rec}")

st.divider()

# ----------------------------
# Display Full Table
# ----------------------------
st.markdown("### All Customer Risk Data")
st.dataframe(df_risk, use_container_width=True)
