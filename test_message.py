import requests

# ✅ Your Telegram bot credentials
BOT_TOKEN = "7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU"
CHAT_ID = "6748992445"  # Your personal Telegram ID

# ✅ Message to test
message = "✅ Test message from my Telegram XAUUSD bot!"

# ✅ Telegram API endpoint
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

# ✅ Send the message
response = requests.post(url, data=payload)

# ✅ Show Telegram's response
print("Telegram response:", response.status_code, response.text)
