import asyncio
from telegram import Bot

# Replace with your actual Bot Token and Chat ID
BOT_TOKEN = '7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU'
CHAT_ID = '6748992445'

async def send_test_message():
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="✅ Manual test message from local")

# Run the async function
asyncio.run(send_test_message())

