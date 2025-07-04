import os
import requests
import pandas as pd
import time

# === Load from environment variables ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
API_KEY = os.environ.get("API_KEY")

# === Telegram alert function ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        print(f"✅ Telegram sent: {message}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# === Fetch XAU/USD 5min data from Alpha Vantage ===
def fetch_xauusd():
    print("📡 Fetching XAUUSD data...")
    url = (
        f"https://www.alphavantage.co/query?"
        f"function=FX_INTRADAY&from_symbol=XAU&to_symbol=USD&interval=5min"
        f"&outputsize=compact&apikey={API_KEY}"
    )
    res = requests.get(url)
    data = res.json()

    if "Time Series FX (5min)" not in data:
        print("❌ Error fetching Alpha Vantage data:", data)
        return None

    df = pd.DataFrame.from_dict(data["Time Series FX (5min)"], orient="index")
    df = df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close"
    }).astype(float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

# === Calculate Stochastic Oscillator ===
def calculate_stochastic(df, k_period=14, d_period=3):
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    df['%K'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    return df

# === Main alert logic ===
def check_stochastic_alert():
    df = fetch_xauusd()
    if df is None or df.shape[0] < 20:
        print("⚠️ Not enough data to calculate stochastic.")
        return

    df = calculate_stochastic(df)
    latest_k = df['%K'].iloc[-1]
    latest_d = df['%D'].iloc[-1]
    print(f"📊 Latest %K: {latest_k:.2f} | %D: {latest_d:.2f}")

    if latest_k < 20:
        send_telegram_message(f"📉 *XAUUSD OVERSOLD*\n%K = {latest_k:.2f}\n%D = {latest_d:.2f}")
    elif latest_k > 80:
        send_telegram_message(f"📈 *XAUUSD OVERBOUGHT*\n%K = {latest_k:.2f}\n%D = {latest_d:.2f}")
    else:
        print("⏳ No signal triggered.")

# === Main loop for background worker ===
if __name__ == "__main__":
    print("🚀 XAUUSD Stochastic Bot started.")
    while True:
        check_stochastic_alert()
        time.sleep(300)  # 5 minutes
