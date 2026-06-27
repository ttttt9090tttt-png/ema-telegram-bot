import os
import time
import threading
import pandas as pd
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler

# =============== تنظیمات ================
BOT_TOKEN = "8878020030:AAEAG5LwlQUiXWuJDplPr7kZ0wNCQP-IAYg"
CHAT_ID = "1186512882"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

# ✅ تغییر مورد نظر شما: تایم‌فریم‌ها = 5، 15، 60
TIMEFRAMES = ["5", "15", "60"]

sent_signals = {}
app = Flask(__name__)

# =============== توابع ربات ================
def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print(f"Error sending message: {e}")

def get_data(symbol, interval):
    url = f"https://api.nobitex.ir/market/udf/history?symbol={symbol}&resolution={interval}&count=100"
    try:
        r = requests.get(url).json()
        if "c" in r and len(r["c"]) > 0:
            return pd.DataFrame({"close": r["c"]})
    except:
        pass
    return None

def ema(series, period):
    return series.ewm(span=period).mean()

def check_cross(df):
    if df is None or len(df) < 30:
        return None
    df["ema7"] = ema(df["close"], 7)
    df["ema25"] = ema(df["close"], 25)
    if df["ema7"].iloc[-2] < df["ema25"].iloc[-2] and df["ema7"].iloc[-1] > df["ema25"].iloc[-1]:
        return "BUY"
    if df["ema7"].iloc[-2] > df["ema25"].iloc[-2] and df["ema7"].iloc[-1] < df["ema25"].iloc[-1]:
        return "SELL"
    return None

def run():
    while True:
        for symbol in SYMBOLS:
            for interval in TIMEFRAMES:
                try:
                    df = get_data(symbol, interval)
                    if df is None:
                        continue
                    signal = check_cross(df)
                    key = f"{symbol}_{interval}"
                    if signal is None:
                        continue
                    if sent_signals.get(key) == signal:
                        continue
                    sent_signals[key] = signal
                    if signal == "BUY":
                        send_msg(f"BUY Signal for {symbol} ({interval})")
                    elif signal == "SELL":
                        send_msg(f"SELL Signal for {symbol} ({interval})")
                except Exception as e:
                    print(f"Error in {symbol} {interval}: {e}")
                    continue
        time.sleep(300)

# =============== وب‌سرور برای Render ================
@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/ping')
def ping():
    return "Pong", 200

# =============== اجرا ================
if __name__ == "__main__":
    # اجرای ربات در یک ترد جداگانه
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    
    # اجرای وب‌سرور
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
