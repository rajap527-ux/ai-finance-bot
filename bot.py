import os
import logging
import pytz
import requests
import yfinance as yf
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # optional
DEFAULT_STOCK = "AAPL"

UAETIME = pytz.timezone("Asia/Dubai")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================= AI STOCK ENGINE =================
def get_stock_data(symbol: str):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="5d", interval="1d")
    if hist.empty:
        return None
    return hist

def ai_signal(symbol: str):
    data = get_stock_data(symbol)
    if data is None or len(data) < 3:
        return f"⚠️ No data for {symbol}"

    close = data["Close"]

    latest = close.iloc[-1]
    prev = close.iloc[-2]

    change = ((latest - prev) / prev) * 100

    # Simple "AI-style" logic (replaceable with ML later)
    if change > 1.2:
        signal = "🟢 BUY"
        reason = "Strong upward momentum detected"
    elif change < -1.2:
        signal = "🔴 SELL"
        reason = "Downward pressure detected"
    else:
        signal = "🟡 HOLD"
        reason = "Market is stable / uncertain movement"

    return (
        f"📊 *AI SIGNAL FOR {symbol}*\n"
        f"Price: {latest:.2f}\n"
        f"Change: {change:.2f}%\n\n"
        f"Signal: {signal}\n"
        f"Reason: {reason}"
    )

# ================= NEWS REASONING =================
def get_news(symbol: str):
    if not NEWS_API_KEY:
        return "🧠 News module not configured."

    url = f"https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()

    articles = r.get("articles", [])[:3]
    if not articles:
        return "No recent news found."

    summary = "🧠 *News Impact Summary:*\n"
    for a in articles:
        summary += f"- {a['title']}\n"

    summary += "\n📌 Market sentiment may be influenced by above news."
    return summary

# ================= TELEGRAM COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 AI Trading Bot Active\n\n"
        "Commands:\n"
        "/signal AAPL - Get AI buy/sell signal\n"
        "/price TSLA - Get stock price\n"
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper() if context.args else DEFAULT_STOCK

    msg = ai_signal(symbol)
    news = get_news(symbol)

    await update.message.reply_text(msg + "\n\n" + news, parse_mode="Markdown")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper() if context.args else DEFAULT_STOCK
    data = yf.Ticker(symbol).history(period="1d")

    if data.empty:
        await update.message.reply_text("No data found.")
        return

    price = data["Close"].iloc[-1]
    await update.message.reply_text(f"💰 {symbol} Price: {price:.2f}")

# ================= DAILY 9 AM UAE ALERT =================
async def daily_alert(app):
    symbols = ["AAPL", "TSLA", "GOOGL"]

    message = "📢 *DAILY AI TRADING ALERT (UAE TIME 9 AM)*\n\n"

    for s in symbols:
        message += ai_signal(s) + "\n\n"

    # Broadcast to all users (replace with DB later)
    for chat_id in app.chat_data:
        try:
            await app.bot.send_message(chat_id, message, parse_mode="Markdown")
        except:
            pass

# ================= SCHEDULER =================
def setup_scheduler(app):
    scheduler = AsyncIOScheduler(timezone=UAETIME)

    scheduler.add_job(
        daily_alert,
        "cron",
        hour=9,
        minute=0,
        args=[app]
    )

    scheduler.start()

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("price", price))

    setup_scheduler(app)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()