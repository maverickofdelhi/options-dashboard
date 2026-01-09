import streamlit as st
import plotly.express as px
from fetch_data import get_option_chain
from py_vollib.black_scholes.greeks.analytical import delta, theta
from calculations import (
    calculate_pcr,
    support_resistance,
    calculate_max_pain,
    calculate_greeks
)


# ================= PAGE CONFIG =================
st.set_page_config(page_title="NIFTY Options Dashboard", layout="wide")
st.title("📊 NIFTY Options Dashboard")

# ================= LOAD DATA =================
df = get_option_chain()

# ================= BASIC CALCULATIONS =================
pcr = calculate_pcr(df)
support, resistance = support_resistance(df)
max_pain = calculate_max_pain(df)

# ================= TOP METRICS =================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Put Call Ratio", pcr)
col2.metric("Support", support)
col3.metric("Resistance", resistance)
col4.metric("Max Pain", max_pain)

# ================= PCR INTERPRETATION =================
if pcr < 0.8:
    st.error("📉 Bearish sentiment (Low PCR)")
elif pcr > 1.2:
    st.success("📈 Bullish sentiment (High PCR)")
else:
    st.warning("⚖️ Neutral sentiment")

# ================= STRIKE RANGE FILTER =================
st.subheader("🔍 Strike Range Filter")

atm_strike = df.groupby("strike")["oi"].sum().idxmax()

strike_range = st.slider(
    "ATM ± Range",
    min_value=500,
    max_value=3000,
    step=500,
    value=1000
)

filtered_df = df[
    (df["strike"] >= atm_strike - strike_range) &
    (df["strike"] <= atm_strike + strike_range)
]

# ================= OPEN INTEREST CHARTS =================
st.subheader("📊 Open Interest by Strike")

ce_data = filtered_df[filtered_df["type"] == "CE"]
pe_data = filtered_df[filtered_df["type"] == "PE"]

ce_fig = px.bar(
    ce_data,
    x="strike",
    y="oi",
    title="Call Open Interest (CE)",
    labels={"strike": "Strike Price", "oi": "Open Interest"}
)

pe_fig = px.bar(
    pe_data,
    x="strike",
    y="oi",
    title="Put Open Interest (PE)",
    labels={"strike": "Strike Price", "oi": "Open Interest"}
)

st.plotly_chart(ce_fig, use_container_width=True)
st.plotly_chart(pe_fig, use_container_width=True)

# ================= GREEKS (ATM OPTIONS) =================
st.subheader("📐 Option Greeks (ATM)")

def calculate_greeks(row, spot, rate=0.06, days_to_expiry=7, iv=0.20):
    try:
        flag = "c" if row["type"] == "CE" else "p"
        T = days_to_expiry / 365
        d = delta(flag, spot, row["strike"], T, rate, iv)
        t = theta(flag, spot, row["strike"], T, rate, iv)
        return round(d, 3), round(t, 3)
    except:
        return None, None

atm_options = filtered_df[filtered_df["strike"] == atm_strike].copy()

atm_options["Delta"], atm_options["Theta"] = zip(
    *atm_options.apply(
        lambda x: calculate_greeks(x, atm_strike),
        axis=1
    )
)

st.dataframe(
    atm_options[["strike", "type", "Delta", "Theta", "ltp"]],
    use_container_width=True
)

# ================= STRATEGY SUGGESTIONS =================
st.subheader("🧠 Strategy Suggestions")

if pcr < 0.8:
    st.error("""
    **Bearish Bias Detected**
    - Bear Call Spread  
    - Put Debit Spread  
    - Short Call (High Risk)
    """)
elif pcr > 1.2:
    st.success("""
    **Bullish Bias Detected**
    - Bull Call Spread  
    - Call Debit Spread  
    - Short Put
    """)
else:
    st.warning("""
    **Range-Bound / Neutral Market**
    - Iron Condor  
    - Short Strangle  
    - Calendar Spread
    """)

st.caption("⚠️ For educational purposes only. Not investment advice.")

# ================= OPTIONS CHAIN TABLE =================
st.subheader("📋 Options Chain Data")
st.dataframe(
    filtered_df.sort_values(["strike", "type"]),
    use_container_width=True
)
