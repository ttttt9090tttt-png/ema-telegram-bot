import requests
import pandas as pd
import time

BOT_TOKEN =8878020030:AAEAG5LwlQUiXWuJDplPr7kZ0wNCQP-IAYg 
CHAT_ID = "1186512882"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
TIMEFRAME = "15m"

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def get_data(symbol):
    url = f"https://api.nobitex.ir/market/udf/history?symbol={symbol}&resolution=15&count=100"
    r = requests.get(url).json()
    df = pd.DataFrame({"close": r["c"]})
    return df

def ema(series, period):
    return series.ewm(span=period).mean()

def check_cross(df):
    df["ema7"] = ema(df["close"], 7)
    df["ema25"] = ema(df["close"], 25)

    if df["ema7"].iloc[-2] < df["ema25"].iloc[-2] and df["ema7"].iloc[-1] > df["ema25"].iloc[-1]:
        return "bullish"
    if df["ema7"].iloc[-2] > df["ema25"].iloc[-2] and df["ema7"].iloc[-1] < df["ema25"].iloc[-1]:
        return "bearish"
    return None

def run():
    for symbol in SYMBOLS:
        df = get_data(symbol)
        signal = check_cross(df)

        if signal == "bullish":
            send_msg(f"🟢 Bullish EMA Cross\n{symbol} ({TIMEFRAME})\nEMA7 > EMA25")
        elif signal == "bearish":
            send_msg(f"🔴 Bearish EMA Cross\n{symbol} ({TIMEFRAME})\nEMA7 < EMA25")

run()
