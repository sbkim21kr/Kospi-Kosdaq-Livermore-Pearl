import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime

# --- Load KRX listing for fundamentals ---
krx = fdr.StockListing('KRX')
krx = krx[['Code', 'Name', 'MarketCap', 'EPS', 'P/E', 'Market']].copy()
krx['MarketCap'] = pd.to_numeric(krx['MarketCap'], errors='coerce')
krx['EPS'] = pd.to_numeric(krx['EPS'], errors='coerce')
krx['P/E'] = pd.to_numeric(krx['P/E'], errors='coerce')

# --- Calculate Pearl Score ---
krx['Pearl Score'] = krx.apply(
    lambda row: row['EPS'] / row['P/E'] if pd.notna(row['EPS']) and pd.notna(row['P/E']) and row['P/E'] > 0 else None,
    axis=1
)

# --- Load price data for Volume Spike and Trend Arrow ---
def get_price_data(code):
    try:
        df = fdr.DataReader(code)
        df = df.sort_index()
        df['20-day Avg Close'] = df['Close'].rolling(window=20).mean()
        df['20-day Avg Volume'] = df['Volume'].rolling(window=20).mean()
        latest = df.iloc[-1]
        return {
            'Close': latest['Close'],
            'Volume': latest['Volume'],
            '20-day Avg Close': latest['20-day Avg Close'],
            '20-day Avg Volume': latest['20-day Avg Volume']
        }
    except:
        return None

# --- Merge price data into krx ---
records = []
for idx, row in krx.iterrows():
    price = get_price_data(row['Code'])
    if price:
        record = {
            'Code': row['Code'],
            'Name': row['Name'],
            'MarketCap': row['MarketCap'],
            'EPS': row['EPS'],
            'P/E': row['P/E'],
            'Pearl Score': row['Pearl Score'],
            'Market': row['Market'],
            'Close': price['Close'],
            'Volume': price['Volume'],
            '20-day Avg Close': price['20-day Avg Close'],
            '20-day Avg Volume': price['20-day Avg Volume']
        }
        records.append(record)

df = pd.DataFrame(records)

# --- Calculate Volume Spike ---
df['Volume Spike'] = df.apply(
    lambda row: row['Volume'] / row['20-day Avg Volume'] if pd.notna(row['Volume']) and pd.notna(row['20-day Avg Volume']) and row['20-day Avg Volume'] > 0 else None,
    axis=1
)

# --- Calculate Trend Arrow ---
def get_arrow(row):
    try:
        change = (row['Close'] - row['20-day Avg Close']) / row['20-day Avg Close']
        return "⬆️" if change > 0.03 else "⬇️" if change < -0.03 else "➡️"
    except:
        return ""

df['Trend Arrow'] = df.apply(get_arrow, axis=1)

# --- Save full dataset with timestamp ---
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
df['Retrieved At'] = timestamp
df.to_csv('latest_kospi_kosdaq.csv', index=False)
