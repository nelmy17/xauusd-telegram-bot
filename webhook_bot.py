from flask import Flask, request
from telegram import Bot
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU")
CHAT_ID = os.environ.get("6748992445D")
bot = Bot(token=BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = data.get('message', '🚨 TradingView Alert Triggered!')
    bot.send_message(chat_id=CHAT_ID, text=message)
    return 'ok', 200

@app.route('/')
def home():
    return '✅ TradingView to Telegram bot is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
