import streamlit as st
import pandas as pd

st.set_page_config(page_title="Livermore Flow Finder + Pearl in the Mud", layout="wide")

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_csv("latest_kospi_kosdaq.csv")
    df['MarketCap_raw'] = pd.to_numeric(df['MarketCap'], errors='coerce')
    df['Close_raw'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Volume_raw'] = pd.to_numeric(df['Volume'], errors='coerce')
    df['Volume Spike_raw'] = pd.to_numeric(df['Volume Spike'], errors='coerce')
    df['Pearl Score_raw'] = pd.to_numeric(df['Pearl Score'], errors='coerce')
    return df

df = load_data()

# --- Show retrieval timestamp ---
st.markdown(f"**📅 Data retrieved at:** `{df['Retrieved At'].iloc[0]}`")

# --- Filters ---
st.sidebar.header("🔍 Filter Breakouts")
min_volume_spike = st.sidebar.number_input("Minimum Volume Spike", value=2.0, step=0.1)
min_pearl_score = st.sidebar.number_input("Minimum Pearl Score", value=1.0, step=0.1)

# --- Filtered breakout stocks ---
filtered = df[
    (df['Volume Spike_raw'] >= min_volume_spike) &
    (df['Pearl Score_raw'] >= min_pearl_score)
].copy()

# --- Format numbers with commas ---
def format_commas(x):
    return f"{int(x):,}" if pd.notna(x) else ""

def format_float(x):
    return f"{x:,.2f}" if pd.notna(x) else ""

filtered['MarketCap'] = filtered['MarketCap_raw'].apply(format_commas)
filtered['Close'] = filtered['Close_raw'].apply(format_float)
filtered['Volume'] = filtered['Volume_raw'].apply(format_commas)
filtered['Volume Spike'] = filtered['Volume Spike_raw'].apply(format_float)
filtered['Pearl Score'] = filtered['Pearl Score_raw'].apply(format_float)

# --- Display breakout stocks ---
def show_breakouts(market_name):
    st.subheader(f"📈 Breakout Stocks — {market_name}")
    subset = filtered[filtered['Market'] == market_name]
    subset = subset.sort_values(by='MarketCap_raw', ascending=False)
    display_df = subset[['Code', 'Name', 'MarketCap', 'Close', 'Trend Arrow', 'Volume', 'Volume Spike', 'Pearl Score']]
    st.dataframe(display_df, use_container_width=True)

show_breakouts("KOSPI")
show_breakouts("KOSDAQ")
