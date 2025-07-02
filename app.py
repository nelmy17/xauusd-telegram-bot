from flask import Flask, request
from telegram import Bot
import requests
import pandas as pd

# === Your credentials ===
TELEGRAM_TOKEN = "7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU"
CHAT_ID = "6748992445"
API_KEY = "78ade9c6b5de4093951a1e99afa96f50"  # TwelveData API Key

# === Initialize bot and Flask app ===
bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# === Home route ===
@app.route('/')
def home():
    return "✅ XAUUSD Telegram bot is running", 200

# === Manual test route ===
@app.route('/test', methods=['GET'])
def test_alert():
    bot.send_message(chat_id=CHAT_ID, text="✅ Manual test alert from webhook_bot.py")
    return "ok", 200

# === Route to check Stochastic ===
@app.route('/check', methods=['GET'])
def check_stochastic():
    try:
        url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=15min&outputsize=50&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "values" not in data:
            return "No data available", 200

        df = pd.DataFrame(data["values"])
        df = df.iloc[::-1]  # Reverse to chronological
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)

        # Calculate %K (Stochastic)
        low_min = df["low"].rolling(window=14).min()
        high_max = df["high"].rolling(window=14).max()
        df["%K"] = 100 * ((df["close"] - low_min) / (high_max - low_min))

        k = df["%K"].iloc[-1]

        # Send alerts
        if k > 80:
            bot.send_message(chat_id=CHAT_ID, text=f"🚨 XAUUSD Overbought Alert! %K = {k:.2f}")
        elif k < 20:
            bot.send_message(chat_id=CHAT_ID, text=f"✅ XAUUSD Oversold Alert! %K = {k:.2f}")

        return "ok", 200

    except Exception as e:
        return f"Error: {str(e)}", 500

# === Run locally if needed ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




