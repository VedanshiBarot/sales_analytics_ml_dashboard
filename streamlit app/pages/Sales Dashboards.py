import streamlit as st
import pandas as pd
import joblib
from supabase import create_client
import os
import streamlit.components.v1 as components

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Interactive Power BI Dashboard",
    layout="wide"
)

# -------------------------------------------------------
# NAVIGATION BAR
# -------------------------------------------------------
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
    <a href="/Sales_Dashboards" target="_self" class="active">Analytics Reports</a>
    <a href="/payment_risk_prediction" target="_self">Payment Risk</a>
    <a href="/Customer_segmentation" target="_self">Customer Segmentation</a>
    <a href="/revenue_forecast" target="_self">Revenue Forecast</a>
    <a href="/Investment_Insights" target="_self">Investment Insights</a>
    <a href="/Product_Simulation" target="_self">Product Simulation</a>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# SUPABASE CONNECTION
# -------------------------------------------------------
url = "https://yqtsngkummwynbihfyhb.supabase.co"
key = "sb_publishable_66ecgNWLttxallBAfY88WA_MLHkMk8B"

supabase = create_client(url, key)

# -------------------------------------------------------
# LOAD MODELS
# -------------------------------------------------------
import joblib

# Revenue Model
revenue_model = joblib.load("ml/models/revenue_model.pkl")

# Payment Risk Model
risk_data = joblib.load("ml/models/risk_model.pkl")
risk_model = risk_data["model"]
risk_scaler = risk_data["scaler"]

# Customer Segmentation Model
seg_data = joblib.load("ml/models/segmentation_model.pkl")
seg_model = seg_data["model"]
seg_scaler = seg_data["scaler"]

# Investment Models
investment_revenue_model = joblib.load("ml/models/investment_revenue_model.pkl")
investment_profit_model = joblib.load("ml/models/investment_profit_model.pkl")

# Encoders
country_encoder = joblib.load("ml/models/country_encoder.pkl")
office_encoder = joblib.load("ml/models/office_encoder.pkl")
productline_encoder = joblib.load("ml/models/productline_encoder.pkl")
vendor_encoder = joblib.load("ml/models/vendor_encoder.pkl")

# -------------------------------------------------------
# LAYOUT: Simulation Panel
# -------------------------------------------------------
show_sim = st.checkbox("Show Simulation Panel")

if show_sim:
    col1, col2 = st.columns([3, 1])
else:
    col1 = st.container()
    col2 = None

# -------------------------------------------------------
# POWER BI DASHBOARD
# -------------------------------------------------------
with col1:
    components.html(
        """
        <iframe title="Sales_project" width="100%" height="800px"
        src="https://app.powerbi.com/view?r=eyJrIjoiNmVjYmFhZDktMDFmNy00ODU2LTg2NmYtMTViOGRjMzJlMzhlIiwidCI6ImUzNzBjZWJjLWE2NmYtNGU1ZC04YWNlLWQ1YjA4ZWMzYzE1ZSJ9&pageName=f8744b93ffb6914e451a"
        frameborder="0" allowFullScreen="true"></iframe>
        """,
        height=800
    )

# -------------------------------------------------------
# SIMULATION PANEL
# -------------------------------------------------------
if show_sim and col2:
    with col2:
        st.subheader("Simulation Panel")
        sim_type = st.selectbox(
            "Select Simulation",
            [
                "Revenue Forecast",
                "Payment Risk",
                "Customer Segmentation",
                "Investment Insights",
                "Product Simulation"
            ]
        )

        # -------------------------------------------------------
        # REVENUE FORECAST
        # -------------------------------------------------------
        if sim_type == "Revenue Forecast":
            st.markdown("### Revenue Forecast")
            month_num = st.number_input("Month Number", 1, 12, 6)
            total_orders = st.number_input("Total Orders", 100)
            total_customers = st.number_input("Total Customers", 50)
            units_sold = st.number_input("Units Sold", 200)
            avg_price_each = st.number_input("Average Price", 60.0)
            rev_lag_1 = st.number_input("Revenue Last Month", 50000)
            rev_lag_2 = st.number_input("Revenue 2 Months Ago", 48000)
            rev_lag_3 = st.number_input("Revenue 3 Months Ago", 47000)

            rev_roll_3 = (rev_lag_1 + rev_lag_2 + rev_lag_3) / 3

            if st.button("Predict Revenue"):
                input_df = pd.DataFrame({
                    "month_num": [month_num],
                    "total_orders": [total_orders],
                    "total_customers": [total_customers],
                    "units_sold": [units_sold],
                    "avg_price_each": [avg_price_each],
                    "rev_lag_1": [rev_lag_1],
                    "rev_lag_2": [rev_lag_2],
                    "rev_lag_3": [rev_lag_3],
                    "rev_roll_3": [rev_roll_3]
                })
                input_df = input_df.reindex(columns=revenue_model.feature_names_in_)
                pred = revenue_model.predict(input_df)[0]
                st.success(f"Predicted Revenue: ${pred:,.0f}")

                # Recommendation
                if pred > rev_lag_1:
                    st.info("📈 Recommendation: Increase marketing investment and inventory to capture expected demand growth.")
                else:
                    st.warning("⚠ Recommendation: Focus on promotional campaigns and customer retention to prevent revenue decline.")

        # -------------------------------------------------------
        # PAYMENT RISK
        # -------------------------------------------------------
        elif sim_type == "Payment Risk":
            st.markdown("### Payment Risk")
            avg_ship_to_pay_days = st.number_input("Average Days to Pay", 15)
            max_ship_to_pay_days = st.number_input("Max Days to Pay", 25)
            total_payments = st.number_input("Total Payments", 5)
            total_amount_paid = st.number_input("Total Amount Paid", 50000.0)
            creditLimit = st.number_input("Credit Limit", 100000.0)
            recency_days = st.number_input("Days Since Last Payment", 10)
            payment_count = st.number_input("Payment Count", 3)

            if st.button("Predict Risk"):
                input_df = pd.DataFrame({
                    "avg_ship_to_pay_days": [avg_ship_to_pay_days],
                    "max_ship_to_pay_days": [max_ship_to_pay_days],
                    "total_payments": [total_payments],
                    "total_amount_paid": [total_amount_paid],
                    "creditLimit": [creditLimit],
                    "recency_days": [recency_days],
                    "payment_count": [payment_count]
                })
                input_scaled = risk_scaler.transform(input_df)
                risk_prob = risk_model.predict_proba(input_scaled)[:, 1][0]
                st.success(f"Risk Probability: {risk_prob:.2f}")

                if risk_prob > 0.7:
                    st.error("Strategy: High risk customer. Reduce credit limit and enforce stricter payment terms.")
                elif risk_prob > 0.4:
                    st.warning("Strategy: Moderate risk. Monitor payment behaviour and send payment reminders.")
                else:
                    st.info("Strategy: Low risk. Maintain current credit policy.")

        # -------------------------------------------------------
        # CUSTOMER SEGMENTATION
        # -------------------------------------------------------
        elif sim_type == "Customer Segmentation":
            st.markdown("### Customer Segmentation")
            total_revenue = st.number_input("Total Revenue", 50000)
            orders_per_month = st.number_input("Orders Per Month", 2)
            recency_days = st.number_input("Days Since Last Order", 15)
            avg_order_value = st.number_input("Avg Order Value", 5000)

            if st.button("Predict Segment"):
                input_df = pd.DataFrame({
                    "total_revenue": [total_revenue],
                    "orders_per_month": [orders_per_month],
                    "recency_days": [recency_days],
                    "avg_order_value": [avg_order_value]
                })
                scaled = seg_scaler.transform(input_df)
                cluster = seg_model.predict(scaled)[0]

                segment_map = {
                    0: "Low Value Customer",
                    1: "Medium Value Customer",
                    2: "High Value Customer",
                    3: "VIP Customer",
                    4: "Inactive Customer"
                }
                segment = segment_map.get(cluster, "Unknown")
                st.success(f"Customer Segment: {segment}")

                # Recommendations
                if segment == "VIP Customer":
                    st.info("Recommendation: Provide loyalty rewards, early product access, and premium service.")
                elif segment == "High Value Customer":
                    st.info("Recommendation: Upsell premium products and cross-sell related products.")
                elif segment == "Medium Value Customer":
                    st.info("Recommendation: Targeted promotions to increase purchase frequency.")
                elif segment == "Low Value Customer":
                    st.warning("Recommendation: Offer discounts and bundle deals.")
                elif segment == "Inactive Customer":
                    st.error("Recommendation: Launch re-engagement campaigns and personalized offers.")

        # -------------------------------------------------------
        # INVESTMENT INSIGHTS
        # -------------------------------------------------------
        elif sim_type == "Investment Insights":
            st.markdown("### Investment Simulation")

            res = supabase.table("vw_sales_enriched").select("*").execute()
            df = pd.DataFrame(res.data)

           # Keep column consistency (IMPORTANT)
            df.rename(columns={
            "quantityOrdered": "units_sold",
            "line_revenue": "revenue"
            }, inplace=True)

            df["profit"] = df["revenue"] * 0.25

            country = st.selectbox("Country", sorted(df["country"].unique()))
            office = st.selectbox("Office Code", sorted(df[df["country"]==country]["officeCode"].unique()))
            vendor = st.selectbox("Vendor", sorted(df[df["officeCode"]==office]["productVendor"].unique()))
            productline = st.selectbox("Product Line", sorted(df[df["productVendor"]==vendor]["productLine"].unique()))
            units = st.number_input("Units", 50)
            price = st.number_input("Price", 50.0)
            prev_rev = st.number_input("Previous Revenue", 50000)
            prev_profit = st.number_input("Previous Profit", 12000)

            if st.button("Predict Investment"):
                input_df = pd.DataFrame({
                    "country_enc": [country_encoder.transform([country])[0]],
                    "office_enc": [office_encoder.transform([office])[0]],
                    "productline_enc": [productline_encoder.transform([productline])[0]],
                    "vendor_enc": [vendor_encoder.transform([vendor])[0]],
                    "units_sold": [units],
                    "priceEach": [price],
                    "vendor_avg_revenue": [prev_rev],
                    "office_avg_revenue": [prev_rev],
                    "product_avg_revenue": [prev_rev],
                    "prev_month_revenue": [prev_rev],
                    "prev_month_profit": [prev_profit]
                })
                rev = investment_revenue_model.predict(input_df)[0]
                prof = investment_profit_model.predict(input_df)[0]
                st.success(f"Expected Revenue: ${rev:,.0f}")
                st.success(f"Expected Profit: ${prof:,.0f}")

                if prof > prev_profit:
                    st.info("Investment Strategy: Increase inventory or marketing in this product line.")
                else:
                    st.warning("Investment Strategy: Consider alternative product lines or cost optimization.")

        # -------------------------------------------------------
        # PRODUCT SIMULATION
        # -------------------------------------------------------
        elif sim_type == "Product Simulation":
            st.markdown("### Product Simulation")
            units = st.number_input("Units to Sell", 100)
            price = st.number_input("Price", 80)
            cost = st.number_input("Cost", 40)

            if st.button("Run Simulation"):
                revenue = units * price
                profit = units * (price - cost)
                st.success(f"Expected Revenue: ${revenue:,.0f}")
                st.success(f"Expected Profit: ${profit:,.0f}")

                if profit > 0:
                    st.info("Pricing Strategy: Maintain current pricing or increase marketing to maximize profit.")
                else:
                    st.error("Pricing Strategy: Reduce cost or adjust price to avoid losses.")