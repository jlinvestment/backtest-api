from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import os
import json
import numpy as np

app = Flask(__name__)
CORS(app)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# =========================
# CAGR 계산
# =========================
def calc_cagr(start, end, years):
    if start <= 0 or years <= 0:
        return 0
    return ((end / start) ** (1 / years) - 1) * 100

# =========================
# 캐시 파일 경로
# =========================
def get_cache_path(symbol):
    return os.path.join(DATA_DIR, f"{symbol.upper()}.json")

# =========================
# 데이터 로드 (Lazy Cache)
# =========================
def load_data(symbol, years):

    path = get_cache_path(symbol)

    # 1️⃣ 캐시 존재
    if os.path.exists(path):

        with open(path, "r") as f:
            data = json.load(f)

        return np.array(data)

    # 2️⃣ 캐시 없음 → Yahoo 호출
    df = yf.download(symbol, period=f"{years}y", progress=False)

    if df is None or df.empty:
        return None

    prices = df["Close"].dropna().tolist()

    # 3️⃣ 저장 (캐시 생성)
    with open(path, "w") as f:
        json.dump(prices, f)

    return np.array(prices)

# =========================
# TEST MODE
# =========================
def test_data():
    return {
        "symbol": "TEST",
        "invested": 3600000,
        "dividend": 150000,
        "final_value": 11200000,
        "profit": 7600000,
        "return": 120.45,
        "cagr": 10.25,
        "values": [100,120,140,180,220,260,300]
    }

# =========================
# BACKTEST API
# =========================
@app.route("/backtest")
def backtest():

    symbol = request.args.get("symbol", "QQQ").upper()
    amount = float(request.args.get("amount", 300000))
    years = int(request.args.get("years", 10))

    # =====================
    # TEST MODE
    # =====================
    if symbol == "TEST":
        return jsonify(test_data())

    # =====================
    # DATA LOAD (CACHE)
    # =====================
    prices = load_data(symbol, years)

    if prices is None or len(prices) == 0:
        return jsonify({"error": "NO_DATA"})

    cash = 0.0
    shares = 0.0
    values = []

    # =====================
    # BACKTEST
    # =====================
    for price in prices:

        price = float(price)

        if price <= 0:
            continue

        buy_qty = amount // price
        cash += amount - (buy_qty * price)
        shares += buy_qty

        total = (shares * price) + cash

        values.append(float(np.float64(total)))

    invested = amount * len(values)
    final_value = float(values[-1])

    profit = final_value - invested
    return_rate = (profit / invested) * 100 if invested > 0 else 0
    cagr = calc_cagr(invested, final_value, years)

    return jsonify({
        "symbol": symbol,

        "invested": round(invested),
        "dividend": 0,  # 확장용
        "final_value": round(final_value),
        "profit": round(profit),

        "return": round(return_rate, 2),
        "cagr": round(cagr, 2),

        "values": values
    })

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
