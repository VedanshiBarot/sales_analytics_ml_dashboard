
import streamlit as st

st.set_page_config(
    page_title="Sales Intelligence Platform",
    layout="wide"
)

st.markdown("""
<style>

/* ---------- APP BACKGROUND ---------- */
.stApp{
background:
radial-gradient(circle at 20% 20%, rgba(56,189,248,0.18), transparent 40%),
radial-gradient(circle at 80% 30%, rgba(99,102,241,0.18), transparent 40%),
radial-gradient(circle at 40% 80%, rgba(236,72,153,0.18), transparent 40%),
linear-gradient(135deg,#050816,#0B0F1A,#111827);
color:white;
font-family:'Segoe UI',sans-serif;
overflow-x:hidden;
}

/* Neon animated glow */
.stApp::before{
content:"";
position:fixed;
top:-200px;
left:-200px;
width:700px;
height:700px;
background:radial-gradient(circle,#38BDF8,transparent 70%);
opacity:0.18;
filter:blur(120px);
animation: neonMove 18s infinite alternate;
z-index:-1;
}

@keyframes neonMove{
0%{transform:translate(0px,0px);}
100%{transform:translate(200px,150px);}
}

/* ---------- HEADER ---------- */
.header-banner{
background: linear-gradient(90deg,#2563EB,#38BDF8);
padding:30px;
border-radius:16px;
margin-bottom:30px;
box-shadow:
0px 0px 25px rgba(56,189,248,0.6),
0px 10px 40px rgba(0,0,0,0.6);
border:1px solid rgba(56,189,248,0.5);
}

.main-title{
font-size:48px;   /* Increased from 42px */
font-weight:700;
color:white;
text-shadow:0px 0px 12px rgba(56,189,248,0.8);
}

.sub-text{
color:#E5E7EB;
font-size:25px;   /* Increased from 20px */
margin-top:8px;
}

/* ---------- CARD ---------- */
.card{
background: rgba(17,24,39,0.75);
padding:28px;
border-radius:18px;
border:1px solid rgba(255,255,255,0.08);
backdrop-filter: blur(12px);
height:210px;
display:flex;
flex-direction:column;
justify-content:space-between;
transition: all 0.35s ease;
box-shadow:
0px 0px 25px rgba(0,0,0,0.6),
0px 0px 10px rgba(56,189,248,0.2);
position:relative;
cursor:pointer;
}

/* Neon hover */
.card:hover{
transform: translateY(-10px) scale(1.02);
border:1px solid #38BDF8;
box-shadow:
0px 0px 15px #38BDF8,
0px 0px 40px rgba(56,189,248,0.7),
0px 0px 80px rgba(56,189,248,0.4);
}

/* ---------- TEXT ---------- */
.card-title{
font-size:24px;   /* Increased from 21px */
font-weight:600;
margin-bottom:6px;
text-shadow:0px 0px 6px rgba(255,255,255,0.3);
}

.card-text{
font-size:18px;   /* Increased from 16px */
color:#D1D5DB;
line-height:1.6;
}

/* ---------- ARROW ---------- */
.arrow-link{
font-size:20px;   /* Increased from 18px */
color:#9CA3AF;
text-decoration:none;
cursor:pointer;
transition:0.25s;
}

.arrow-link:hover{
color:#38BDF8;
transform:scale(1.35);
text-shadow:0px 0px 10px #38BDF8;
}

/* ---------- FOOTER ---------- */
.footer-text{
    font-size:22px;   /* Increased for readability */
    color:#F3F4F6;
    text-align:center;
    margin-top:20px;
    font-weight:500;
}

/* Hide Sidebar */
[data-testid="stSidebar"] {
display:none;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class='header-banner'>
<div class='main-title'>Sales Intelligence Platform</div>
<div class='sub-text'>
Interactive sales intelligence platform for forecasting revenue, analyzing customer behavior, managing payment risk, and evaluating investment opportunities.
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------- ROW 1 ----------
col1, col2, col3 = st.columns(3, gap="large")

# ---------------- Analytics Reports ----------------
with col1:
    st.markdown("""
    <a href="/Sales_Dashboards" target="_self" style="text-decoration:none;">
    <div class='card'>
      <div>
        <div class='card-title' style='color:#22C55E;'>📊 Analytics Reports</div>
        <div class='card-text'>
          Explore interactive dashboards and detailed analytics reports.
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
        <div class='card-text'><b>Includes:</b> Sales, Revenue & Customer dashboards</div>
        <div class='arrow-link'>↗</div>
      </div>
    </div>
    </a>
    """, unsafe_allow_html=True)


# ---------------- Payment Risk ----------------
with col2:
    st.markdown("""
    <a href="/payment_risk_prediction" target="_self" style="text-decoration:none;">
    <div class='card'>
      <div>
        <div class='card-title' style='color:#F59E0B;'>⚠ Payment Risk</div>
        <div class='card-text'>
          Detect customers likely to delay payments and manage credit exposure.
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
        <div class='card-text'><b>Output:</b> Risk score + payment action</div>
        <div class='arrow-link'>↗</div>
      </div>
    </div>
    </a>
    """, unsafe_allow_html=True)

# ---------------- Customer Segmentation ----------------
with col3:
    st.markdown("""
    <a href="/Customer_segmentation" target="_self" style="text-decoration:none;">
    <div class='card'>
      <div>
        <div class='card-title' style='color:#6366F1;'>👥 Customer Segmentation</div>
        <div class='card-text'>
          Classify customers into VIP, Medium, and Low value segments.
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
        <div class='card-text'><b>Output:</b> Customer segment + strategy</div>
        <div class='arrow-link'>↗</div>
      </div>
    </div>
    </a>
    """, unsafe_allow_html=True)

# ---------- ROW 2 ----------
st.markdown("<br>", unsafe_allow_html=True)
col4, col5, col6 = st.columns(3, gap="large")

# ---------------- Revenue Forecast ----------------
with col4:
    st.markdown("""
    <a href="/revenue_forecast" target="_self" style="text-decoration:none;">
    <div class='card'>
      <div>
        <div class='card-title' style='color:#38BDF8;'>📈 Revenue Forecast</div>
        <div class='card-text'>
          Predict next 6 months revenue trends using AI forecasting models.
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
        <div class='card-text'><b>Output:</b> Revenue prediction</div>
        <div class='arrow-link'>↗</div>
      </div>
    </div>
    </a>
    """, unsafe_allow_html=True)

# ---------------- Investment Insights ----------------
with col5:
    st.markdown("""
    <a href="/Investment_Insights" target="_self" style="text-decoration:none;">
    <div class='card'>
      <div>
        <div class='card-title' style='color:#EC4899;'>💰 Investment Insights</div>
        <div class='card-text'>
          Evaluate investment opportunities across vendors and product lines.
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
        <div class='card-text'><b>Output:</b> Revenue, profit & recommendation</div>
        <div class='arrow-link'>↗</div>
      </div>
    </div>
    </a>
    """, unsafe_allow_html=True)

# ---------------- Product Simulation ----------------
with col6:
    st.markdown("""
    <a href="/Product_Simulation" target="_self" style="text-decoration:none;">
    <div class='card'>
      <div>
        <div class='card-title' style='color:#10B981;'>📦 Product Simulation</div>
        <div class='card-text'>
          Simulate new product sales performance before launching.
        </div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
        <div class='card-text'><b>Output:</b> Demand forecast & launch strategy</div>
        <div class='arrow-link'>↗</div>
      </div>
    </div>
    </a>
    """, unsafe_allow_html=True)

st.divider()

# ---------- FOOTER ----------
st.markdown("""
<div class='footer-text'>
Welcome to the Sales Intelligence Platform. Select a module above to begin.
</div>
""", unsafe_allow_html=True)  
