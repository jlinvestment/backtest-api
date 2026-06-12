from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# =========================
# CAGR
# =========================
def calc_cagr(start, end, years):
    if start <= 0 or years <= 0:
        return 0
    return ((end / start) ** (1 / years) - 1) * 100

# =========================
# 데이터
# =========================
def get_data(symbol, years):

    cache_file = f"/tmp/{symbol}_{years}.pkl"

    if os.path.exists(cache_file):
        df = pd.read_pickle(cache_file)
    else:
        df = yf.download(symbol, period=f"{years}y")
        if df is None or df.empty:
            return None
        df.to_pickle(cache_file)

    return df

# =========================
# 백테스트
# =========================
@app.route("/backtest")
def backtest():

    symbol = request.args.get("symbol", "QQQ")
    amount = float(request.args.get("amount", 300000))
    years = int(request.args.get("years", 10))

    df = get_data(symbol, years)

    if df is None or df.empty:
        return jsonify({"error": "NO_DATA"})

    df = df.dropna()
    df = df.resample("ME").last()

    prices = df["Close"].to_numpy()

    dividends = df["Dividends"].fillna(0).to_numpy() if "Dividends" in df else [0]*len(prices)

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

        # 배당
        dividend_income = shares * div
        cash += dividend_income
        total_dividend += dividend_income

        total = shares * price + cash
        values.append(float(total))

    invested = amount * len(values)
    final_value = values[-1] if values else 0

    profit = final_value - invested
    return_rate = (profit / invested) * 100 if invested > 0 else 0

    cagr = calc_cagr(invested, final_value, years)

    return jsonify({
        "symbol": symbol,

        # 🔥 정리된 값
        "invested": round(invested),
        "dividend": round(total_dividend),
        "final_value": round(final_value),
        "profit": round(profit),

        # % 값
        "return": round(return_rate, 2),
        "cagr": round(cagr, 2),

        "values": values
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
