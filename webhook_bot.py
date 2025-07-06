from flask import Flask
import requests
import pandas as pd

# === 🔐 CREDENTIALS (hardcoded for simplicity) ===
BOT_TOKEN = "7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU"
CHAT_ID = "674899244"
API_KEY = "7f4ff730c91f41f08a1c91a9c6c62391"  # Twelve Data API key

# === ⚙️ FLASK APP ===
app = Flask(__name__)

# === 📬 Send Telegram message ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# === 📊 Get Stochastic %K and %D from Twelve Data ===
def get_stochastic():
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=5min&outputsize=100&apikey={API_KEY}"
    try:
        response = requests.get(url).json()

        if "values" not in response:
            return None, f"Twelve Data error: {response.get('message', 'No candle data returned')}"

        df = pd.DataFrame(response["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        df = df.astype(float)
        df.sort_index(inplace=True)

        # Calculate Stochastic %K and %D
        low_min = df["low"].rolling(window=14).min()
        high_max = df["high"].rolling(window=14).max()
        df["%K"] = 100 * ((df["close"] - low_min) / (high_max - low_min))
        df["%D"] = df["%K"].rolling(window=3).mean()

        latest_k = df["%K"].iloc[-1]
        latest_d = df["%D"].iloc[-1]
        return (round(latest_k, 2), round(latest_d, 2)), None

    except Exception as e:
        return None, f"❌ Exception: {str(e)}"

# === 🔁 /check endpoint ===
@app.route("/check")
def check_stochastic():
    values, error = get_stochastic()
    if error:
        message = f"⚠️ Could not fetch data.\n{error}"
        send_telegram_message(message)
        return message

    k, d = values
    print(f"📊 Latest Stochastic %K = {k}, %D = {d}")

    if k < 20:
        message = f"📉 XAUUSD Stochastic %K = {k}\n⚠️ Oversold! Possible BUY signal."
        send_telegram_message(message)
        return message
    elif k > 80:
        message = f"📈 XAUUSD Stochastic %K = {k}\n⚠️ Overbought! Possible SELL signal."
        send_telegram_message(message)
        return message
    else:
        return f"ℹ️ Neutral: %K = {k}. No alert sent."

# === 🏠 Homepage for Render health check ===
@app.route("/")
def home():
    return "✅ XAUUSD Telegram Bot is Live"

# === 🚀 Run locally (not used by gunicorn) ===
if __name__ == "__main__":
    app.run(debug=True)
