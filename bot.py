from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Hello! I'm your Telegram bot!")

app = ApplicationBuilder().token("7308283803:AAHm3CmrIlpGoehyAhX9xgJdAzTn_bZcJcU").build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
