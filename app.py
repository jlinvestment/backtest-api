from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "API RUNNING"

@app.route("/backtest")
def backtest():

    symbol = request.args.get("symbol", "SPY")
    amount = float(request.args.get("amount", 300000))
    years = int(request.args.get("years", 10))

    # =========================
    # 캐시
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
    # 데이터 처리
    # =========================
    df = df[["Close"]].dropna()
    df = df.resample("ME").last().dropna()

    prices = df["Close"].to_numpy()

    # =========================
    # 백테스트
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

        values.append(float(total.item() if hasattr(total, "item") else total))

    # =========================
    # 핵심 계산
    # =========================
    invested = amount * len(values)        # 총 투자 원금
    final_value = values[-1] if values else 0  # 최종 자산

    profit = final_value - invested        # 손익

    return_rate = (profit / invested) * 100 if invested > 0 else 0

    # =========================
    # 응답
    # =========================
    return jsonify({
        "symbol": symbol,
        "return": round(return_rate, 2),
        "invested": round(invested, 2),
        "final_value": round(final_value, 2),
        "profit": round(profit, 2),
        "values": values
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
