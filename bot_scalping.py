import requests
import pandas as pd
import ta
import time

# ==========================
# 📌 DATOS DEL BOT
# ==========================
TOKEN = "8302022116:AAEBzzmCv9oy-aSeRGyhFDWbOVCktxC_MWg"   # 👉 pon tu token real
CHAT_ID = "7147837684"  # 👉 pon tu chat_id real
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def send_signal(message):
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(URL, data=payload)

def get_klines(symbol="BTCUSDT", interval="5m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=[
        "time","o","h","l","c","v","ct","qv","nt","tb","tq","i"
    ])
    df["c"] = df["c"].astype(float)
    df["h"] = df["h"].astype(float)
    df["l"] = df["l"].astype(float)
    df["v"] = df["v"].astype(float)
    return df

def check_signal(symbol="BTCUSDT"):
    df = get_klines(symbol)

    # Indicadores
    df["rsi"] = ta.momentum.RSIIndicator(df["c"], window=14).rsi()
    df["ema20"] = ta.trend.EMAIndicator(df["c"], window=20).ema_indicator()
    df["ema50"] = ta.trend.EMAIndicator(df["c"], window=50).ema_indicator()
    df["ema200"] = ta.trend.EMAIndicator(df["c"], window=200).ema_indicator()
    df["atr"] = ta.volatility.AverageTrueRange(df["h"], df["l"], df["c"], window=14).average_true_range()
    df["adx"] = ta.trend.ADXIndicator(df["h"], df["l"], df["c"], window=14).adx()

    last = df.iloc[-1]

    precio = last["c"]
    rsi = last["rsi"]
    atr = last["atr"]
    adx = last["adx"]

    if rsi < 25 and adx > 18:
        entrada = precio
        tp1 = round(entrada + 0.8 * atr, 2)
        tp2 = round(entrada + 1.5 * atr, 2)
        sl = round(entrada - 1.0 * atr, 2)
        mensaje = f"""🚀 COMPRA DETECTADA 🚀
Par: {symbol}
Entrada: {entrada}
TP1: {tp1}
TP2: {tp2}
SL: {sl}
"""
        send_signal(mensaje)

    elif rsi > 75 and adx > 18:
        entrada = precio
        tp1 = round(entrada - 0.8 * atr, 2)
        tp2 = round(entrada - 1.5 * atr, 2)
        sl = round(entrada + 1.0 * atr, 2)
        mensaje = f"""⚡ VENTA DETECTADA ⚡
Par: {symbol}
Entrada: {entrada}
TP1: {tp1}
TP2: {tp2}
SL: {sl}
"""
        send_signal(mensaje)

pares = ["BTCUSDT","ETHUSDT","SOLUSDT","NOTUSDT","WUSDT","ENAUSDT","AEVOUSDT","ALTUSDT"]

while True:
    for par in pares:
        try:
            check_signal(par)
        except Exception as e:
            print(f"Error en {par}: {e}")
    time.sleep(300)  # 5 minutos

