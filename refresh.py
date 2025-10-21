import pandas as pd
import requests
import random
from datetime import datetime
from io import StringIO

# --- Load full KRX stock list ---
krx_url = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"
response = requests.get(krx_url)
response.encoding = 'cp949'
html = response.text

df_krx = pd.read_html(StringIO(html))[0]
print(f"✅ Raw table rows: {len(df_krx)}")

# --- Rename columns to English ---
df_krx = df_krx.rename(columns={
    "종목코드": "Code",
    "회사명": "Name",
    "시장구분": "Market",
    "업종": "Industry",
    "주요제품": "MainProduct",
    "상장일": "ListingDate",
    "결산월": "FiscalMonth",
    "대표자명": "CEO",
    "홈페이지": "Website",
    "지역": "Region"
})

# --- Normalize and filter ---
df_krx["Code"] = df_krx["Code"].astype(str).str.zfill(6)
df_krx["Market"] = df_krx["Market"].str.strip()
print("🔍 Unique Market values:", df_krx["Market"].unique())

# Map Korean market labels to English
df_krx["Market"] = df_krx["Market"].replace({
    "유가": "KOSPI",
    "코스닥": "KOSDAQ"
})

df_krx = df_krx[df_krx["Market"].isin(["KOSPI", "KOSDAQ"])].reset_index(drop=True)
print(f"✅ Filtered KOSPI/KOSDAQ rows: {len(df_krx)}")

# --- Simulate financial data ---
def simulate_stock_data(row):
    market_cap = random.uniform(1e3, 1e6)
    eps = random.uniform(0.1, 100)
    pe = random.uniform(1, 50)
    volume_today = random.randint(10_000, 1_000_000)
    volume_avg = random.randint(10_000, 1_000_000)
    close_today = random.uniform(1_000, 100_000)
    close_avg = close_today * random.uniform(0.95, 1.05)

    pearl_score = eps / pe if pe > 0 else 0
    volume_spike = volume_today / volume_avg if volume_avg > 0 else 0
    change = (close_today - close_avg) / close_avg
    trend_arrow = "⬆️" if change > 0.03 else "⬇️" if change < -0.03 else "➡️"

    return {
        "Code": row["Code"],
        "Name": row["Name"],
        "Market": row["Market"],
        "MarketCap": market_cap,
        "EPS": eps,
        "P/E": pe,
        "Pearl Score": pearl_score,
        "Volume": volume_today,
        "20-day Avg Volume": volume_avg,
        "Volume Spike": volume_spike,
        "Close": close_today,
        "20-day Avg Close": close_avg,
        "Trend Arrow": trend_arrow,
        "Retrieved At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# --- Process and save ---
processed = [simulate_stock_data(row) for _, row in df_krx.iterrows()]
df_final = pd.DataFrame(processed)
df_final.to_csv("latest_kospi_kosdaq.csv", index=False)
print(f"✅ Saved {len(df_final)} stocks to latest_kospi_kosdaq.csv")
