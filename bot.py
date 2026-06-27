import os
import time
import threading
import requests
import pandas as pd
from flask import Flask

# ==================== تنظیمات ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8878020030:AAEAG5LwlQUiXWuJDplPr7kZ0wNCQP-IAYg")
CHAT_ID = os.getenv("CHAT_ID", "1186512882")

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
TIMEFRAMES = ["5", "15", "60"]

EMA_FAST = 7
EMA_SLOW = 25
CHECK_INTERVAL = 300  # ۵ دقیقه

app = Flask(__name__)
sent_signals = {}

# ==================== توابع کمکی ====================
def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=15)
    except Exception as e:
        print(f"❌ خطا در ارسال پیام: {e}")

def get_data(symbol, interval):
    """دریافت داده از نوبیتکس (یا Binance)"""
    url = f"https://api.nobitex.ir/market/udf/history?symbol={symbol}&resolution={interval}&count=150"
    try:
        r = requests.get(url, timeout=20).json()
        if "c" not in r or not r["c"]:
            return None
        df = pd.DataFrame({"close": pd.to_numeric(r["c"])})
        return df
    except Exception as e:
        print(f"⚠️ خطا در دریافت {symbol}: {e}")
        return None

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def check_cross(df):
    if df is None or len(df) < EMA_SLOW + 5:
        return None
    
    df["ema7"] = ema(df["close"], EMA_FAST)
    df["ema25"] = ema(df["close"], EMA_SLOW)
    
    prev_fast, prev_slow = df["ema7"].iloc[-2], df["ema25"].iloc[-2]
    now_fast, now_slow = df["ema7"].iloc[-1], df["ema25"].iloc[-1]
    
    if prev_fast < prev_slow and now_fast > now_slow:
        return "BUY"
    if prev_fast > prev_slow and now_fast < now_slow:
        return "SELL"
    return None

# ==================== حلقه اصلی ربات ====================
def run():
    print("🚀 ربات EMA شروع به کار کرد...")
    while True:
        for symbol in SYMBOLS:
            for interval in TIMEFRAMES:
                try:
                    df = get_data(symbol, interval)
                    signal = check_cross(df)
                    if signal is None:
                        continue
                    
                    key = f"{symbol}_{interval}"
                    if sent_signals.get(key) == signal:
                        continue
                    
                    sent_signals[key] = signal
                    icon = "🟢" if signal == "BUY" else "🔴"
                    
                    text = (
                        f"{icon} سیگنال {signal}\n"
                        f"سکه: {symbol}\n"
                        f"تایم‌فریم: {interval} دقیقه\n"
                        f"تقاطع EMA{EMA_FAST} × EMA{EMA_SLOW}"
                    )
                    
                    send_msg(text)
                    print(f"✅ {text}")
                    
                except Exception as e:
                    print(f"❌ خطا در {symbol} {interval}: {e}")
        
        time.sleep(CHECK_INTERVAL)

# ==================== وب‌سرور (برای رندر) ====================
@app.route("/")
def home():
    return "✅ ربات EMA فعال است!"

@app.route("/ping")
def ping():
    return "🏓 Pong"

# ==================== اجرای همزمان ====================
if __name__ == "__main__":
    # اجرای ربات در ترد جداگانه
    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    
    # راه‌اندازی وب‌سرور
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 وب‌سرور روی پورت {port} راه‌اندازی شد...")
    app.run(host="0.0.0.0", port=port)
