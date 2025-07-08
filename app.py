from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simulated database
user_balances = {}

@app.route("/")
def home():
    return "✅ DiceMint Backend is Live!"

@app.route("/get_balance", methods=["POST"])
def get_balance():
    data = request.get_json()
    telegram_id = str(data.get("telegram_id"))
    balance = user_balances.get(telegram_id, 0)
    return jsonify({"balance": balance})

@app.route("/update_balance", methods=["POST"])
def update_balance():
    data = request.get_json()
    telegram_id = str(data.get("telegram_id"))
    balance = data.get("balance", 0)
    user_balances[telegram_id] = balance
    return jsonify({"success": True, "new_balance": balance})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)