from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd

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
    # 데이터 다운로드
    # =========================
    df = yf.download(symbol, period=f"{years}y")

    if df is None or df.empty:
        return jsonify({"error": "NO_DATA"})

    df = df[["Close"]].dropna()

    # 월말 기준 리샘플
    df = df.resample("ME").last().dropna()

    prices = df["Close"].values

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
        values.append(float(total))

    # =========================
    # 수익률
    # =========================
    invested = amount * len(values)
    end_value = values[-1] if values else 0

    ret = ((end_value - invested) / invested) * 100 if invested > 0 else 0

    return jsonify({
        "symbol": symbol,
        "return": round(ret, 2),
        "values": values
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
