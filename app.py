from flask import Flask, request, jsonify

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
