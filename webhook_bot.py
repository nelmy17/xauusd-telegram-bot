from flask import Flask, request
import requests
import pandas as pd
from telegram import Bot
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
API_KEY = os.environ.get("TWELVE_API_KEY")  # your Twelve Data API key

bot = Bot(token=BOT_TOKEN)

def get_xauusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=15min&outputsize=100&apikey={API_KEY}"
    r = requests.get(url)
    data = r.json()

    if 'values' not in data:
        raise ValueError("Invalid response from API")

    df = pd.DataFrame(data['values'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')
    df.set_index('datetime', inplace=True)
    df = df.astype(float)
    return df

def calculate_stochastic(df, k_period=14, d_period=3):
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    df['%K'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    return df

@app.route('/')
def home():
    return '✅ Python-only XAUUSD bot running!'

@app.route('/check', methods=['GET'])
def check_stochastic():
    try:
        df = get_xauusd_data()
        df = calculate_stochastic(df)
        k = df['%K'].iloc[-1]

        if k > 80:
            bot.send_message(chat_id=CHAT_ID, text=f"🚨 XAUUSD Overbought! %K = {k:.2f}")
        elif k < 20:
            bot.send_message(chat_id=CHAT_ID, text=f"✅ XAUUSD Oversold! %K = {k:.2f}")
        else:
            return f"Stochastic neutral (%K = {k:.2f})", 200

        return "ok", 200

    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"❌ Error: {e}")
        return "error", 500
