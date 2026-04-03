import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.set_page_config(page_title="Product Simulation", layout="wide")

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
    <a href="/Investment_Insights" target="_self">Investment Insights</a>
    <a href="/Product_Simulation" target="_self" class="active">Product Simulation</a>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# SUPABASE Connection
# ----------------------------
from supabase import create_client, Client
import pandas as pd

# Replace with your Supabase project URL and anon key
url = "https://yqtsngkummwynbihfyhb.supabase.co"
key = "sb_publishable_66ecgNWLttxallBAfY88WA_MLHkMk8B"

supabase: Client = create_client(url, key)

# ----------------------------
# Load Products
# ----------------------------

res = supabase.table("products").select("*").execute()
products = pd.DataFrame(res.data)

# ----------------------------
# Product Line + Product Selection
# ----------------------------

st.subheader("Select Product")

col1, col2 = st.columns(2)

with col1:
    product_line_selected = st.selectbox(
        "Select Product Line",
        sorted(products["productLine"].unique())
    )

# Filter products
filtered_products = products[
    products["productLine"] == product_line_selected
]

with col2:
    product = st.selectbox(
        "Select Product",
        filtered_products["productName"]
    )

# Selected product row
product_row = filtered_products[
    filtered_products["productName"] == product
].iloc[0]

product_code = product_row["productCode"]
product_name = product_row["productName"]
product_line_name = product_row["productLine"]

# ----------------------------
# Previous 3 Months Performance
# ----------------------------

res = (
    supabase
    .table("vw_sales_fact")
    .select("orderDate, productCode, quantityOrdered, priceEach")
    .eq("productCode", product_code)
    .order("orderDate", desc=True)
    .limit(90)  # approximate last 3 months
    .execute()
)

history = pd.DataFrame(res.data)

if not history.empty:
    history["month"] = pd.to_datetime(history["orderDate"]).dt.to_period("M").astype(str)
    history = history.groupby("month").agg(
        units_sold=("quantityOrdered", "sum"),
        revenue=("priceEach", lambda x: (x * history.loc[x.index, "quantityOrdered"]).sum())
    ).reset_index()

    # Profit calculation
    history["profit"] = history["revenue"] - (history["units_sold"] * product_row["buyPrice"])

# Sort for chart
history = history.sort_values("month")

res = supabase.table("vw_sales_fact").select(
    "productCode, quantityOrdered, priceEach"
).execute()

sales_df = pd.DataFrame(res.data)

# Merge with products info
df = sales_df.merge(products, on="productCode")

opportunity_products = (
    df.groupby(["productName", "productLine"])
    .agg(
        units_sold=("quantityOrdered", "sum"),
        revenue=("priceEach", lambda x: (x * df.loc[x.index, "quantityOrdered"]).sum()),
        profit=("priceEach", lambda x: ((x - df.loc[x.index, "buyPrice"]) * df.loc[x.index, "quantityOrdered"]).sum())
    )
    .reset_index()
    .sort_values("profit", ascending=False)
    .head(5)
)

best_product = opportunity_products.iloc[0]
# ----------------------------
# Display Previous Performance
# ----------------------------

st.subheader("Previous Performance")

col1, col2 = st.columns(2)

with col1:
    st.dataframe(history)

with col2:
    chart_data = history.set_index("month")[["revenue", "profit"]]
    st.line_chart(chart_data)

# ----------------------------
# Product Simulation
# ----------------------------

st.subheader("Product Simulation")

units = st.slider("Units to Sell", 1, 5000, 100)

# Formula-based calculations

revenue_pred = units * product_row["MSRP"]
profit_pred = units * (product_row["MSRP"] - product_row["buyPrice"])

if st.button("Run Simulation"):

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Expected Revenue", f"${revenue_pred:,.0f}")

    with col2:
        st.metric("Expected Profit", f"${profit_pred:,.0f}")

    # ----------------------------
    # Strategic Business Insight
    # ----------------------------

    avg_revenue = history["revenue"].mean()
    stock = product_row["quantityInStock"]

    revenue_ratio = revenue_pred / avg_revenue if avg_revenue > 0 else 1
    inventory_ratio = units / stock if stock > 0 else 0
    profit_margin = profit_pred / revenue_pred if revenue_pred > 0 else 0

    # ----------------------------
    # Performance Classification
    # ----------------------------

    if revenue_ratio < 0.8:

        level = "Low Potential"

        cause = "Predicted revenue is lower than the product's recent historical performance."

        recommendation = "Consider promotional discounts or bundling this product with popular products."

    elif revenue_ratio <= 1.2:

        level = "Moderate Potential"

        cause = "Predicted revenue is close to normal historical performance."

        recommendation = "Maintain current pricing and inventory levels while monitoring demand."

    else:

        level = "High Potential"

        cause = "Predicted revenue is significantly higher than historical performance."

        recommendation = "Increase marketing focus and ensure sufficient inventory availability."

    # Inventory insight

    if inventory_ratio > 0.8:
        recommendation += " Inventory may run out soon, consider restocking."

    elif inventory_ratio < 0.2:
        recommendation += " Only a small portion of inventory is used, which may indicate overstock."

    # Profit margin insight

    if profit_margin < 0.15:
        recommendation += " Profit margin is relatively low; pricing optimization could improve profitability."

    # ----------------------------
    # Display Strategic Decision
    # ----------------------------

    st.subheader("Strategic Business Decision")

    st.success(
        f"Product: {product_name} | Product Line: {product_line_name}"
    )

    st.write("Performance Level")
    st.info(level)

    st.write("Cause")
    st.info(cause)

    st.write("Recommendation")
    st.warning(
        f"For **{product_name}** from the **{product_line_name}** category: {recommendation}"
    )
    
    st.subheader("Product Growth Opportunity")

col1, col2 = st.columns(2)

with col1:
    st.dataframe(opportunity_products)

with col2:
    st.success(
        f"""
Recommended Product to Scale

Product: {best_product['productName']}

Product Line: {best_product['productLine']}

Reason:
This product has generated the highest historical profit and shows strong demand trends.
"""
    )