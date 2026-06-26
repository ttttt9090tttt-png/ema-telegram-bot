import requests
import pandas as pd
import time

BOT_TOKEN = "8878020030:AAEAG5LwlQUiXWuJDplPr7kZ0wNCQP-IAYg "
CHAT_ID = "1186512882"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT"
]

TIMEFRAMES = [
    "5m",
    "15m"
]

EMA_FAST = 7
EMA_SLOW = 25


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        }
    )


def get_data(symbol, interval):

    url = (
        "https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval={interval}&limit=100"
    )

    r = requests.get(url, timeout=15)

    if r.status_code != 200:
        return None

    candles = r.json()

    closes = []

    for c in candles:
        closes.append(float(c[4]))

    df = pd.DataFrame(
        closes,
        columns=["close"]
    )

    return df


def calculate(df):

    df["ema7"] = df["close"].ewm(
        span=EMA_FAST,
        adjust=False
    ).mean()

    df["ema25"] = df["close"].ewm(
        span=EMA_SLOW,
        adjust=False
    ).mean()

    return df
def check_cross(df):

    df = calculate(df)

    prev7 = df["ema7"].iloc[-2]
    prev25 = df["ema25"].iloc[-2]

    last7 = df["ema7"].iloc[-1]
    last25 = df["ema25"].iloc[-1]

    if prev7 < prev25 and last7 > last25:
        return "BUY"

    if prev7 > prev25 and last7 < last25:
        return "SELL"

    return None


sent_signals = {}


def run():

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

                    send_message(
                        f"🟢 EMA 7/25 Bullish Cross\n\n"
                        f"{symbol}\n"
                        f"TimeFrame : {interval}"
                    )

                if signal == "SELL":

                    send_message(
                        f"🔴 EMA 7/25 Bearish Cross\n\n"
                        f"{symbol}\n"
                        f"TimeFrame : {interval}"
                    )

            except Exception as e:
                print(e)
if name == "__main__":

    print("EMA Bot Started")

    while True:

        run()

        time.sleep(300)
