import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Load Telegram Bot Token from Environment Variable
TOKEN = os.getenv("BOT_TOKEN")

# Check if token exists
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing!")

print("TOKEN LOADED SUCCESSFULLY")
print("✅ Bot running...")

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Finance Bot is running successfully!\n\n"
        "Ask me about:\n"
        "• Stocks\n"
        "• Gold price\n"
        "• Investment ideas\n"
        "• Market trends"
    )

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Commands:\n"
        "/start - Start bot\n"
        "/help - Show help"
    )

# Handle User Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    response = (
        f"📈 You asked:\n{user_message}\n\n"
        "AI finance analysis feature will be added soon."
    )

    await update.message.reply_text(response)

# Main Function
def main():
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Add message handler
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Start bot polling
    app.run_polling()

# Run Bot
if __name__ == "__main__":
    main()
