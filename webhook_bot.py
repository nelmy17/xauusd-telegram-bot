
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
    high_max = df["high"].rolling(window=_

