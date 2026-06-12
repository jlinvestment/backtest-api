from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "API RUNNING"

# =========================
# BACKTEST API
# =========================
@app.route("/backtest")
def backtest():

    symbol = request.args.get("symbol", "SPY")
    amount = float(request.args.get("amount", 300000))
    years = int(request.args.get("years", 10))

    # =========================
    # 1. 캐시 처리 (중요)
    # =========================
    cache_file = f"/tmp/{symbol}_{years}.pkl"

    if os.path.exists(cache_file):
        df = pd.read_pickle(cache_file)
    else:
        df = yf.download(symbol, period=f"{years}y")

        if df is None or df.empty:
            return jsonify({"error": "NO_DATA"})

        df.to_pickle(cache_file)

    # =========================
    # 2. 데이터 정리
    # =========================
    df = df[["Close"]].dropna()

    # 월말 기준
    df = df.resample("ME").last().dropna()

    prices = df["Close"].to_numpy()

    # =========================
    # 3. 백테스트
    # =========================
    cash = 0
    shares = 0
    values = []

    for price in prices:

        if price <= 0:
            continue

        buy_qty = amount // price
        cash += amount - (buy_qty * price)
        shares += buy_qty

        total = shares * price + cash

        # numpy 안전 처리
        values.append(float(total.item() if hasattr(total, "item") else total))

    # =========================
    # 4. 수익률 계산
    # =========================
    invested = amount * len(values)
    end_value = values[-1] if values else 0

    ret = ((end_value - invested) / invested) * 100 if invested > 0 else 0

    # =========================
    # 5. 응답
    # =========================
    return jsonify({
        "symbol": symbol,
        "return": round(ret, 2),
        "values": values
    })

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
