from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

import yfinance as yf

from config import TELEGRAM_TOKEN


async def start(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "📊 AI Finance Bot Running"
    )


async def stock(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Usage: /stock AAPL"
        )
        return

    symbol = context.args[0]

    stock = yf.Ticker(symbol)

    hist = stock.history(period="5d")

    price = hist['Close'].iloc[-1]

    await update.message.reply_text(
        f"{symbol} Price: ${price}"
    )


app = ApplicationBuilder().token(
    TELEGRAM_TOKEN
).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("stock", stock)
)

print("Bot running...")

app.run_polling()
