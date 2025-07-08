from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simulated database
user_balances = {}
user_referrals = {}

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

# ✅ NEW: Referral logic
@app.route("/api/referral", methods=["POST"])
def referral():
    data = request.get_json()
    new_user_id = str(data.get("new_user_id"))
    referrer_id = str(data.get("referrer_id"))

    # Prevent self-referral
    if new_user_id == referrer_id:
        return jsonify({"status": "error", "message": "Self-referral is not allowed"}), 400

    # Only allow referral if new_user doesn't already exist
    if new_user_id in user_balances:
        return jsonify({"status": "skipped", "message": "User already registered"}), 200

    # Register new user and reward referrer
    user_balances[new_user_id] = 0
    user_referrals[new_user_id] = referrer_id

    # Give referrer $5 (500 coins)
    user_balances[referrer_id] = user_balances.get(referrer_id, 0) + 500

    return jsonify({
        "status": "success",
        "message": f"Referrer {referrer_id} rewarded for inviting {new_user_id}"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)