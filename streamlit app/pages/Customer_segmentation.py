import streamlit as st
import pandas as pd
import joblib
import os
from sqlalchemy import create_engine

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="Customer Segmentation", layout="wide")

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
    <a href="/Customer_segmentation" target="_self" class="active">Customer Segmentation</a>
    <a href="/revenue_forecast" target="_self">Revenue Forecast</a>
    <a href="/Investment_Insights" target="_self">Investment Insights</a>
    <a href="/Product_Simulation" target="_self">Product Simulation</a>
</div>
""", unsafe_allow_html=True)

st.title("Customer Value Segmentation")

st.divider()

# ----------------------------
# Load Model + Scaler
# ----------------------------
model_file = "ml/models/segmentation_model.pkl"

if not os.path.exists(model_file):
    st.error("Segmentation model file not found!")
    st.stop()

data = joblib.load(model_file)
model = data["model"]
scaler = data["scaler"]
features = data["features"]

# ----------------------------
# Database Connection
# ----------------------------
from supabase import create_client, Client

url = "https://yqtsngkummwynbihfyhb.supabase.co"
key = "sb_publishable_66ecgNWLttxallBAfY88WA_MLHkMk8B"

supabase: Client = create_client(url, key)

# ----------------------------
# Fix Missing Feature / Segment Names
# ----------------------------
res = supabase.table("tbl_customer_segments").select("*").execute()
df_segments = pd.DataFrame(res.data)

# Fix numeric columns
# ----------------------------
# Database Connection (Supabase)
# ----------------------------
res = supabase.table("tbl_customer_segments").select("*").execute()
df_segments = pd.DataFrame(res.data)

# Fix numeric columns safely
numeric_cols = ["total_revenue", "orders_per_month", "recency_days", "avg_order_value"]
for col in numeric_cols:
    if col in df_segments.columns:
        df_segments[col] = pd.to_numeric(df_segments[col], errors="coerce").fillna(0)
    else:
        # fallback
        if col == "orders_per_month" and "total_orders" in df_segments.columns:
            df_segments[col] = df_segments["total_orders"] / 12
        else:
            df_segments[col] = 0

# Map segment codes → business names
if "customer_segment" in df_segments.columns:
    df_segments["customer_segment"] = df_segments["customer_segment"].replace({
        "Segment 1": "VIP",
        "Segment 2": "Medium Value",
        "Segment 3": "Low Value",
        "Segment 4": "Inactive Customers"
    })
# ----------------------------
# Customer Dropdown
# ----------------------------
customer_ids = df_segments["customerNumber"].tolist()
selected_customer = st.selectbox(
    "Select Customer ID (or choose New)",
    ["New"] + customer_ids
)

# ----------------------------
# Prefill Inputs
# ----------------------------
if selected_customer != "New":
    row = df_segments[df_segments["customerNumber"] == selected_customer].iloc[0]
    total_revenue_default = float(row["total_revenue"])
    orders_per_month_default = float(row["orders_per_month"])
    recency_days_default = float(row["recency_days"])
    avg_order_value_default = float(row["avg_order_value"])
else:
    total_revenue_default = 50000.0
    orders_per_month_default = 2.0
    recency_days_default = 30.0
    avg_order_value_default = 2000.0

# ----------------------------
# User Input Section
# ----------------------------
st.markdown("### Enter Customer Behaviour Details")
col1, col2 = st.columns(2)
with col1:
    total_revenue = st.number_input(
        "Total Revenue",
        min_value=0.0,
        value=total_revenue_default
    )
with col2:
    orders_per_month = st.number_input(
        "Orders Per Month",
        min_value=0.0,
        value=orders_per_month_default
    )

col3, col4 = st.columns(2)
with col3:
    recency_days = st.number_input(
        "Days Since Last Order",
        min_value=0.0,
        value=recency_days_default
    )
with col4:
    avg_order_value = st.number_input(
        "Average Order Value",
        min_value=0.0,
        value=avg_order_value_default
    )

st.divider()

# ----------------------------
# Predict Segment
# ----------------------------
if st.button("Predict Customer Segment"):

    # Prepare input
    input_df = pd.DataFrame([{
        "total_revenue": total_revenue,
        "orders_per_month": orders_per_month,
        "recency_days": recency_days,
        "avg_order_value": avg_order_value
    }])
    input_scaled = scaler.transform(input_df)
    cluster = model.predict(input_scaled)[0]

    # ----------------------------
    # Dynamic Segment Based on Input
    # ----------------------------
    if total_revenue >= 80000 and orders_per_month >= 4 and recency_days <= 60:
        segment = "VIP"
        color = "rgba(40,167,69,0.55)"
        recommendation = "Offer loyalty rewards and exclusive premium services."
    elif total_revenue >= 30000 and orders_per_month >= 2 and recency_days <= 180:
        segment = "Medium Value"
        color = "rgba(255,193,7,0.55)"
        recommendation = "Encourage repeat purchases with targeted offers."
    elif orders_per_month == 0 and total_revenue == 0:
        segment = "Inactive Customers"
        color = "rgba(23,162,184,0.55)"
        recommendation = "Re-engage customers through win-back campaigns."
    else:
        segment = "Low Value"
        color = "rgba(220,53,69,0.55)"
        recommendation = "Run retention campaigns and targeted discount promotions."

    # ----------------------------
    # Explainable AI Reasoning
    # ----------------------------
    reasons = []
    if recency_days > 365:
        reasons.append("Customer has been inactive for a long period")
    if orders_per_month < 2:
        reasons.append("Customer places orders very infrequently")
    if total_revenue < 20000:
        reasons.append("Customer has generated relatively low revenue")
    if avg_order_value < 2000:
        reasons.append("Customer usually purchases low-value items")
    if len(reasons) == 0:
        reasons.append("Customer behaviour aligns with this segment pattern")
    reason_text = " | ".join(reasons)

    # ----------------------------
    # Segmentation Result Cards
    # ----------------------------
    st.markdown("### Segmentation Result")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="
            padding:22px;
            border-radius:16px;
            background:rgba(108,117,125,0.25);
            backdrop-filter: blur(10px);
            text-align:center;
            font-size:22px;
            font-weight:bold;
            color:white;">
        Cluster ID <br> {cluster}
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="
            padding:22px;
            border-radius:16px;
            background:{color};
            backdrop-filter: blur(10px);
            text-align:center;
            font-size:22px;
            font-weight:bold;
            color:white;">
        Customer Segment <br> {segment}
        </div>
        """, unsafe_allow_html=True)

    # ----------------------------
    # Health / Score Card
    # ----------------------------
    st.markdown("### Customer Health Score Card")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${total_revenue:,.0f}")
    col2.metric("Orders/Month", f"{orders_per_month:.1f}")
    col3.metric("Days Since Last Order", f"{recency_days:.0f} days")
    col4.metric("Avg Order Value", f"${avg_order_value:,.0f}")

    # ----------------------------
    # AI Insight
    # ----------------------------
    st.markdown("### AI Customer Insight")
    st.markdown(f"""
    <div style="
        background:rgba(33,150,243,0.12);
        padding:18px;
        border-radius:12px;
        font-size:16px;
        line-height:1.6;
        color:white;">
    <b>Reason for Segmentation:</b><br>
    {reason_text}
    <br><br>
    <b>Recommended Business Action:</b><br>
    {recommendation}
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ----------------------------
# Full Customer Table
# ----------------------------
st.markdown("### All Customer Segments")
st.dataframe(df_segments, use_container_width=True)
# ----------------------------
# Segment Distribution Chart
# ----------------------------
st.markdown("### Customer Segment Distribution")
if "customer_segment" in df_segments.columns:
    segment_counts = (
        df_segments["customer_segment"]
        .value_counts()
        .reindex(["VIP","Medium Value","Low Value","Inactive Customers"])
        .fillna(0)
    )
    st.bar_chart(segment_counts)
else:
    st.info("Customer segment data not available.")