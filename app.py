from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route("/backtest")
def backtest():

    symbol = request.args.get("symbol", "QQQ")
    amount = float(request.args.get("amount", 300000))
    years = int(request.args.get("years", 10))

    # ======================
    # 1. 데이터 (안정화)
    # ======================
    try:
        df = yf.download(symbol, period=f"{years}y", progress=False)
    except:
        return jsonify({"error": "DATA_ERROR"})

    if df is None or df.empty:
        return jsonify({"error": "NO_DATA"})

    df = df.dropna()

    prices = df["Close"].values

    cash = 0.0
    shares = 0.0
    values = []
    total_dividend = 0.0

    # ======================
    # 2. 백테스트
    # ======================
    for price in prices:

        price = float(price)

        if price <= 0:
            continue

        buy_qty = amount // price
        cash += amount - (buy_qty * price)
        shares += buy_qty

        total = (shares * price) + cash

        # 🔥 핵심 수정: 무조건 float로 강제
        values.append(float(np.float64(total)))

    # ======================
    # 3. 결과 계산
    # ======================
    invested = amount * len(values)
    final_value = float(values[-1]) if values else 0

    profit = final_value - invested
    return_rate = (profit / invested) * 100 if invested > 0 else 0

    cagr = ((final_value / invested) ** (1 / years) - 1) * 100 if invested > 0 else 0

    return jsonify({
        "symbol": symbol,
        "invested": round(invested),
        "final_value": round(final_value),
        "profit": round(profit),
        "return": round(return_rate, 2),
        "cagr": round(cagr, 2),
        "values": values
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
