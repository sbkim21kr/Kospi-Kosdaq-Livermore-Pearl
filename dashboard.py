import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="KOSPI & KOSDAQ Breakouts", layout="centered")
st.title("📈 Breakout Stocks — KOSPI & KOSDAQ")

# --- Load Data ---
try:
    df = pd.read_csv('latest_kospi_kosdaq.csv')
except FileNotFoundError:
    st.error("CSV file not found. Please run refresh.py or wait for GitHub Actions.")
    st.stop()

# --- Timestamp ---
timestamp = datetime.fromtimestamp(os.path.getmtime('latest_kospi_kosdaq.csv')).strftime('%Y-%m-%d %H:%M:%S')
st.markdown(f"**📅 Data retrieved at:** `{timestamp} KST`")

# --- Metric Definitions ---
st.markdown("""
---

### 📘 Metric Definitions

**📊 Volume Spike**  
Measures how much today's trading volume exceeds the 20-day average.  
Formula: `Volume Spike = Today's Volume ÷ 20-day Avg Volume`  
A value above 2.0 suggests unusual trading activity — often a sign of accumulation or breakout.

**📈 Trend Arrow**  
Shows the short-term price direction based on the 20-day average:  
- ⬆️ Upward: Price is rising more than 3% above average  
- ➡️ Sideways: Price is within ±3% of average  
- ⬇️ Downward: Price is falling more than 3% below average

**💎 Pearl Score**  
A custom valuation metric: `EPS ÷ P/E`  
Higher scores may indicate undervalued companies with strong earnings relative to price.
""")

# --- User Inputs ---
st.markdown("### 🔧 Adjust Breakout Criteria")
min_volume_spike = st.number_input("Minimum Volume Spike", min_value=1.0, max_value=10.0, value=2.0, step=0.1)
min_pearl_score = st.number_input("Minimum Pearl Score", min_value=0.0, max_value=100.0, value=1.5, step=0.1)
trend_choice = st.selectbox("Trend Direction", ["⬆️", "➡️", "⬇️"])

# --- Ensure numeric columns ---
for col in ['MarketCap', 'EPS', 'P/E', 'Pearl Score', 'Volume Spike', 'Close', '20-day Avg Close']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# --- Format float columns to fixed decimal points ---
float_cols = ['MarketCap', 'EPS', 'P/E', 'Pearl Score', 'Volume Spike', 'Close', '20-day Avg Close']
df[float_cols] = df[float_cols].applymap(lambda x: f"{x:.2f}" if pd.notnull(x) else "")

# --- Format volume columns as integers ---
int_cols = ['Volume', '20-day Avg Volume']
df[int_cols] = df[int_cols].applymap(lambda x: f"{int(x)}" if pd.notnull(x) else "")

# --- Add Trend Arrow ---
def get_arrow(row):
    try:
        change = (float(row['Close']) - float(row['20-day Avg Close'])) / float(row['20-day Avg Close'])
        return "⬆️" if change > 0.03 else "⬇️" if change < -0.03 else "➡️"
    except:
        return ""

df['Trend Arrow'] = df.apply(get_arrow, axis=1)

# --- Filter Diagnostics ---
st.markdown("### 🧮 Filter Diagnostics")
st.markdown(f"- Total stocks loaded: `{len(df)}`")
st.markdown(f"- Volume Spike ≥ {min_volume_spike}: `{len(df[df['Volume Spike'].astype(float) >= min_volume_spike])}`")
st.markdown(f"- Pearl Score ≥ {min_pearl_score}: `{len(df[df['Pearl Score'].astype(float) >= min_pearl_score])}`")
st.markdown(f"- Trend Arrow = {trend_choice}: `{len(df[df['Trend Arrow'] == trend_choice])}`")

# --- Apply Filters ---
filtered = df[
    (df['Volume Spike'].astype(float) >= min_volume_spike) &
    (df['Pearl Score'].astype(float) >= min_pearl_score) &
    (df['Trend Arrow'] == trend_choice)
]

st.markdown(f"**🔎 Matching stocks after all filters: `{len(filtered)}`**")

# --- Split by Market ---
kospi_breakouts = filtered[filtered['Market'] == 'KOSPI']
kosdaq_breakouts = filtered[filtered['Market'] == 'KOSDAQ']

# --- Display Breakouts ---
st.markdown("### 🔥 KOSPI Breakouts")
st.dataframe(
    kospi_breakouts[['Code', 'Name', 'MarketCap', 'Close', 'Pearl Score', 'Trend Arrow', 'Volume', 'Volume Spike']],
    use_container_width=True
)

st.markdown("### 🚀 KOSDAQ Breakouts")
st.dataframe(
    kosdaq_breakouts[['Code', 'Name', 'MarketCap', 'Close', 'Pearl Score', 'Trend Arrow', 'Volume', 'Volume Spike']],
    use_container_width=True
)

# --- Debug: Raw Data Sample at Bottom ---
st.markdown("### 🧪 Raw Data Sample (Debugging)")
st.dataframe(df, use_container_width=True)
