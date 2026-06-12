from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import numpy as np

app = Flask(__name__)
CORS(app)

# =========================
# CAGR 계산
# =========================
def calc_cagr(start, end, years):
    if start <= 0 or years <= 0:
        return 0
    return ((end / start) ** (1 / years) - 1) * 100

# =========================
# TEST DATA
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

    symbol = request.args.get("symbol", "QQQ")
    amount = float(request.args.get("amount", 300000))
    years = int(request.args.get("years", 10))

    # =====================
    # TEST MODE
    # =====================
    if symbol.upper() == "TEST":
        return jsonify(test_data())

    # =====================
    # REAL DATA
    # =====================
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

    for price in prices:

        price = float(price)

        if price <= 0:
            continue

        buy_qty = amount // price
        cash += amount - (buy_qty * price)
        shares += buy_qty

        total = shares * price + cash

        values.append(float(np.float64(total)))

    invested = amount * len(values)
    final_value = float(values[-1]) if values else 0

    profit = final_value - invested
    return_rate = (profit / invested) * 100 if invested > 0 else 0

    cagr = calc_cagr(invested, final_value, years)

    return jsonify({
        "symbol": symbol,

        "invested": round(invested),
        "dividend": round(total_dividend),   # (현재는 0, 나중에 확장)
        "final_value": round(final_value),
        "profit": round(profit),

        "return": round(return_rate, 2),
        "cagr": round(cagr, 2),

        "values": values
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
