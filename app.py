from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

def calc_cagr(start, end, years):
    if start <= 0 or years <= 0:
        return 0
    return ((end / start) ** (1 / years) - 1) * 100

def get_data(symbol, years):

    try:
        df = yf.download(symbol, period=f"{years}y", progress=False)

        if df is None or df.empty:
            return None

        return df

    except Exception:
        return None

@app.route("/backtest")
def backtest():

    symbol = request.args.get("symbol", "QQQ")
    amount = float(request.args.get("amount", 300000))
    years = int(request.args.get("years", 10))

    df = get_data(symbol, years)

    if df is None or df.empty:
        return jsonify({"error": "NO_DATA"})

    df = df.dropna()

    prices = df["Close"].to_numpy()

    # 🔥 핵심: Dividends 안전 처리
    dividends = df["Dividends"].to_numpy() if "Dividends" in df.columns else [0] * len(prices)

    cash = 0
    shares = 0
    values = []
    total_dividend = 0

    for i in range(len(prices)):

        price = prices[i]
        div = dividends[i] if i < len(dividends) else 0

        if price <= 0:
            continue

        buy_qty = amount // price
        cash += amount - (buy_qty * price)
        shares += buy_qty

        dividend_income = shares * div
        cash += dividend_income
        total_dividend += dividend_income

        total = shares * price + cash
        values.append(float(total))

    if not values:
        return jsonify({"error": "NO_VALUES"})

    invested = amount * len(values)
    final_value = values[-1]

    profit = final_value - invested
    return_rate = (profit / invested) * 100 if invested > 0 else 0

    cagr = calc_cagr(invested, final_value, years)

    return jsonify({
        "symbol": symbol,
        "invested": round(invested),
        "dividend": round(total_dividend),
        "final_value": round(final_value),
        "profit": round(profit),
        "return": round(return_rate, 2),
        "cagr": round(cagr, 2),
        "values": values
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
