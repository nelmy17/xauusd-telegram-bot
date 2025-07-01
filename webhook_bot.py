import os
import requests
import pandas as pd
from flask import Flask, request
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()  # Load .env file if you use one

# === Configuration ===
API_KEY = os.environ.get("TWELVE_DATA_API_KEY", "your_twelve_data_api_key")
TELEGRAM_TOKEN = os.environ.get("BOT_TOKEN", "your_telegram_bot_token")
CHAT_ID = os.environ.get("CHAT_ID", "your_chat_id")

app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# === Fetch XAUUSD 15min data ===
def get_xauusd_data():
    url = (
        f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=15min&outputsize=50&apikey={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data["values"])
    df = df.iloc[::-1]  # reverse to chronological order
    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    return df

# === Calculate Stochastic %K ===
def calculate_stochastic(df, k_period=14):
    if df.empty or len(df) < k_period:
        return df

    low_min = df["low"].rolling(window=k_period).min()
    high_max = df["high"].rolling(window=k_period).max()

    df["%K"] = 100 * ((df["close"] - low_min) / (high_max - low_min))
    return df

# === Test route ===
@app.route('/test', methods=['GET'])
def test_alert():
    bot.send_message(chat_id=CHAT_ID, text="✅ Manual test alert from your XAUUSD bot is working.")
    return "ok", 200

# === Main alert route ===
@app.route('/check', methods=['GET'])
def check_stochastic():
    try:
        df = get_xauusd_data()
        df = calculate_stochastic(df)

        if df.empty or df['%K'].isnull().all():
            return "No data", 200

        k = df['%K'].iloc[-1]

        if k > 80:
            bot.send_message(chat_id=CHAT_ID, text=f"🚨 XAUUSD Overbought Alert! %K = {k:.2f}")
        elif k < 20:
            bot.send_message(chat_id=CHAT_ID, text=f"✅ XAUUSD Oversold Alert! %K = {k:.2f}")

        return "ok", 200

    except Exception as e:
        return "error", 200

# === Root route ===
@app.route('/', methods=['GET'])
def home():
    return "XAUUSD bot is running", 200

# === Run for local testing ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
