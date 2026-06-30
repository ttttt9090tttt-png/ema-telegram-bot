import os
import time
import threading
import pandas as pd
import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = "8993671459:AAGc0qEfrWx8tbXY5n4TsyBz_McpV58Gsv8"
CHAT_ID = "1186512882"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
TIMEFRAMES = ["5", "15", "60"]

sent_signals = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print(f"Error: {e}")

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
                    print(f"Error: {e}")
                    continue
        time.sleep(300)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/ping')
def ping():
    return "Pong", 200

if __name__ == "__main__":
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), bot)
        dispatcher.process_update(update)
        return 'ok', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'error', 500
