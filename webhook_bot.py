import os
import requests
import pandas as pd
from flask import Flask, request
from telegram import Bot

# === YOUR CREDENTIALS HERE ===
API_KEY = "78ade9c6b5de4093951a1e99afa96f50"  # TwelveData API key
TELEGRAM_TOKEN = "7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU"  # Your bot token from BotFather
CHAT_ID = "6748992445"  # Your Telegram chat ID

app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# === Function to get XAU/USD 15-minute data ===
def get_xauusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=15min&outputsize=50&apikey={API_KEY}"
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

# === Function to calculate Stochastic %K ===
def calculate_stochastic(df, k_period=14):
    if df.empty or len(df) < k_period:
        return df

    low_min = df["low"].rolling(window=k_period).min()
    high_max = df["high"].rolling(window=k_period).max()
    df["%K"] = 100 * ((df["close"] - low_min) / (high_max - low_min))
    return df

# === /test route: sends a manual message ===
@app.route('/test', methods=['GET'])
def test_alert():
    bot.send_message(chat_id=CHAT_ID, text="✅ Manual test alert from your XAUUSD bot is working.")
    return "ok", 200

# === /check route: sends alert if overbought/oversold ===
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
        return f"error: {str(e)}", 500

# === Home route for Render ===
@app.route('/', methods=['GET'])
def home():
    return "✅ XAUUSD Telegram bot is running!", 200

# === Main ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




