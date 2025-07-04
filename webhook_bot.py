from flask import Flask, request
import requests
import pandas as pd

# === CREDENTIALS (REPLACE WITH YOUR OWN IF CHANGED) ===
BOT_TOKEN = "7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU"     # Telegram Bot Token
CHAT_ID = "674899244"                                           # Your Telegram User ID
API_KEY = "78ade9c6b5de4093951a1e99afa96f50"                    # TwelveData API Key

# === INIT FLASK ===
app = Flask(__name__)

# === TELEGRAM MESSAGE FUNCTION ===
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    # 🔍 DEBUG: PRINT TELEGRAM RESPONSE
    response = requests.post(url, json=payload)
    print("Telegram response:", response.status_code, response.text)

    return response.status_code

# === ROOT ROUTE: HEALTH CHECK ===
@app.route('/')
def home():
    return "✅ XAUUSD Telegram bot is running", 200

# === MANUAL TEST ALERT ===
@app.route('/test', methods=['GET'])
def test_alert():
    send_telegram_message("✅ Manual test alert from webhook_bot.py")
    return "ok", 200

# === STOCHASTIC ALERT LOGIC ===
@app.route('/check', methods=['GET'])
def check_stochastic():
    try:
        # 📊 FETCH 15-MIN XAU/USD DATA
        url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=15min&outputsize=50&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        # ❌ API FAILED
        if "values" not in data:
            print("❌ No 'values' key in response.")
            return "❌ No data returned from API", 200

        # 📈 PROCESS DATA
        df = pd.DataFrame(data["values"])
        df = df.iloc[::-1]  # Reverse order to chronological
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)

        # 🔢 CALCULATE STOCHASTIC %K
        low_min = df["low"].rolling(window=14).min()
        high_max = df["high"].rolling(window=14).max()
        df["%K"] = 100 * ((df["close"] - low_min) / (high_max - low_min))
        k = df["%K"].iloc[-1]  # Latest value

        # 📋 DEBUG OUTPUT
        print(f"Calculated Stochastic %K: {k:.2f}")

        # 🚨 ALERT CONDITIONS
        if k > 80:
            send_telegram_message(f"🚨 XAUUSD Overbought Alert! %K = {k:.2f}")
        elif k < 20:
            send_telegram_message(f"✅ XAUUSD Oversold Alert! %K = {k:.2f}")
        else:
            print("ℹ️ %K is neutral. No alert sent.")

        return f"Stochastic %K = {k:.2f}", 200

    except Exception as e:
        print("❌ Exception occurred:", str(e))
        return f"❌ Error: {str(e)}", 500

# === RUN SERVER ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

