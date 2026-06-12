from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
