from flask import Flask
import requests
import pandas as pd
import os

# === HARDCODED CREDENTIALS ===
BOT_TOKEN = "7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU"
CHAT_ID = "674899244"
TWELVE_API_KEY = "78ade9c6b5de4093951a1e99afa96f50"  # Your Twelve Data API key

# === Flask App ===
app = Flask(__name__)

# === Telegram Alert ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

# === Fetch XAU/USD from Twelve Data ===
def get_xauusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=5min&apikey={TWELVE_API_KEY}&outputsize=50"
    response = requests.get(url).json()

    if "values" not in response:
        return None, "❌ Error fetching data"

    df = pd.DataFrame(response["values"])
    df.columns = ["datetime", "open", "high", "low", "close"]
    df = df.astype({"open": float, "high": float, "low": float, "close": float})
    df = df.sort_values("datetime").reset_index(drop=True)

    return df, "✅ Data fetched"

# === Stochastic Signal Logic ===
def check_stochastic_signal():
    df, status = get_xauusd_data()
    if df is None:
        return status

    low_min = df["low"].rolling(window=14).min()
    high_max = df["high"].rolling(window=14).max()
    df["%K"] = 100 * ((df["close"] - low_min) / (high_max - low_min))
    df["%D"] = df["%K"].rolling(window=3).mean()

    latest_k = df["%K"].iloc[-1]
    latest_d = df["%D"].iloc[-1]

    if latest_k < 20 and latest_k > latest_d:
        send_telegram_message(f"🟢 BUY Signal on XAUUSD\nStochastic %K={latest_k:.2f}, %D={latest_d:.2f}")
    elif latest_k > 80 and latest_k < latest_d:
        send_telegram_message(f"🔴 SELL Signal on XAUUSD\nStochastic %K={latest_k:.2f}, %D={latest_d:.2f}")
    else:
        print(f"ℹ️ No signal. %K={latest_k:.2f}, %D={latest_d:.2f}")

    return "✅ Check complete"

# === Webhook Endpoint ===
@app.route("/check")
def check():
    result = check_stochastic_signal()
    return result, 200

# === Run Locally or on Render ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
