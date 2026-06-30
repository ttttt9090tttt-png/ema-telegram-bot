import os
import time
import threading
import pandas as pd
import requests
import logging

from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# ============================================
# تنظیمات
# ============================================

TOKEN = "8993671459:AAGc0qEfrWx8tbXY5n4TsyBz_McpV58Gsv8"
PORT = int(os.environ.get("PORT", 10000))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# ============================================
# دستور /start
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ ربات کراس EMA فعال است!\n\n"
        "📊 نماد: BTC/USDT\n"
        "⏱️ تایم‌فریم: 5m\n"
        "📈 EMA سریع: 9\n"
        "📉 EMA کند: 26\n\n"
        "🟢 وقتی EMA 9 از EMA 26 عبور کند، به شما هشدار می‌دهم.\n"
        "🔴 ربات به‌صورت خودکار کار می‌کند."
    )

application.add_handler(CommandHandler("start", start))

# ============================================
# مسیر Webhook
# ============================================

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), bot)
       await application.process_update(update)
        return 'ok', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'error', 500

# ============================================
# مسیر اصلی
# ============================================

@app.route('/')
def home():
    return "Bot is running!"

# ============================================
# اجرا
# ============================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
