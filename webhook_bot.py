from flask import Flask
import requests
import pandas as pd
import os

# === Your Credentials ===
BOT_TOKEN = "7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU"
CHAT_ID = "674899244"
API_KEY = "Y9U9VDI5U7Z56Z5S"  # Alpha Vantage API Key

# === Flask App ===
app = Flask(__name__)

# === Telegram Function ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

# === Fetch XAUUSD & Calculate Stochastic ===
def check_stochastic_signal():
    url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=XAU&to_symbol=USD&interval=5min&apikey={API_KEY}&outputsize=compact"
    response = requests.get(url).json()

    try:
        data = response["Time Series FX (5min)"]
    except KeyError:
        return "❌ Error fetching data"

    df = pd.DataFrame(data).T
    df.columns = ["open", "high", "low", "close"]
    df = df.astype(float).sort_index()

    # Calculate Stochastic
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

# === Web Endpoint ===
@app.route("/check")
def check():
    result = check_stochastic_signal()
    return result, 200

# === Run Flask App with Correct Port (for Render) ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # use Render's assigned port or 10000 locally
    app.run(debug=False, host="0.0.0.0", port=port)
