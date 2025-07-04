import requests
import pandas as pd
import time

# === Hardcoded Bot Credentials and API Key ===
BOT_TOKEN = "7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU"
CHAT_ID = "6748992445"
API_KEY = "78ade9c6b5de4093951a1e99afa96f50"  # TwelveData API Key

# === Telegram Send Function ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"✅ Telegram message sent: {message}")
    except Exception as e:
        print(f"Telegram error: {str(e)}")

# === Fetch XAU/USD from TwelveData ===
def fetch_xauusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=15min&outputsize=50&apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if "values" not in data:
            print("API Error:", data)
            return None

        df = pd.DataFrame(data["values"])
        df = df.iloc[::-1]  # Make it chronological
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        return df

    except Exception as e:
        print("Data fetch error:", str(e))
        return None

# === Calculate and Check Stochastic ===
def check_stochastic_alert():
    df = fetch_xauusd_data()
    if df is None or len(df) < 15:
        print("Not enough data.")
        return

    # Calculate Stochastic Oscillator
    low_min = df["low"].rolling(window=14).min()
    high_max = df["high"].rolling(window=14).max()
    df["%K"] = 100 * ((df["close"] - low_min) / (high_max - low_min))
    k = df["%K"].iloc[-1]

    print(f"Latest Stochastic %K = {k:.2f}")

    if k < 20:
        send_telegram_message(f"✅ XAUUSD *OVERSOLD* Alert\n%K = {k:.2f}")
    elif k > 80:
        send_telegram_message(f"🚨 XAUUSD *OVERBOUGHT* Alert\n%K = {k:.2f}")
    else:
        print("K is neutral. No alert sent.")

# === Main Bot Loop ===
if __name__ == "__main__":
    print("Starting XAUUSD Stochastic Alert Bot...")
    while True:
        check_stochastic_alert()
        time.sleep(300)  # Wait 5 minutes
