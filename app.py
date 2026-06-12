from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API RUNNING"

@app.route("/backtest")
def backtest():
    symbol = request.args.get("symbol", "SPY")
    amount = float(request.args.get("amount", 300))
    years = int(request.args.get("years", 10))

    return jsonify({
        "symbol": symbol,
        "values": [100, 120, 140, 180],
        "return": 18.5
    })

# 🔥 중요: Render용 실행 방식
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
