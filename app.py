from flask import Flask, request, jsonify
from flask_cors import CORS
from tinydb import TinyDB, Query

app = Flask(__name__)
CORS(app)

# Initialize TinyDB (data saved in db.json)
db = TinyDB('db.json')
balances = db.table('balances')
referrals = db.table('referrals')
bonus_table = db.table('bonuses')

@app.route("/")
def home():
    return "✅ DiceMint Backend with TinyDB is Live!"

# Get user balance
@app.route("/get_balance", methods=["POST"])
def get_balance():
    data = request.get_json()
    telegram_id = str(data.get("telegram_id"))
    user = balances.get(Query().telegram_id == telegram_id)
    balance = user["balance"] if user else 0
    return jsonify({"balance": balance})

# Update balance
@app.route("/update_balance", methods=["POST"])
def update_balance():
    data = request.get_json()
    telegram_id = str(data.get("telegram_id"))
    balance = data.get("balance", 0)
    if balances.contains(Query().telegram_id == telegram_id):
        balances.update({"balance": balance}, Query().telegram_id == telegram_id)
    else:
        balances.insert({"telegram_id": telegram_id, "balance": balance})
    return jsonify({"success": True, "new_balance": balance})

# Claim $10 bonus only once
@app.route("/claim_bonus", methods=["POST"])
def claim_bonus():
    data = request.get_json()
    telegram_id = str(data.get("telegram_id"))

    # Check if already claimed
    if bonus_table.contains(Query().telegram_id == telegram_id):
        return jsonify({"success": False, "message": "Bonus already claimed."})

    # Give 1000 coins ($10)
    user = balances.get(Query().telegram_id == telegram_id)
    current = user["balance"] if user else 0
    new_balance = current + 1000

    if user:
        balances.update({"balance": new_balance}, Query().telegram_id == telegram_id)
    else:
        balances.insert({"telegram_id": telegram_id, "balance": new_balance})

    bonus_table.insert({"telegram_id": telegram_id})
    return jsonify({"success": True, "message": "$10 bonus added."})

# Referral system: give $5 (500 coins) to referrer
@app.route("/api/referral", methods=["POST"])
def referral():
    data = request.get_json()
    new_user_id = str(data.get("new_user_id"))
    referrer_id = str(data.get("referrer_id"))

    if new_user_id == referrer_id:
        return jsonify({"status": "error", "message": "Self-referral not allowed"}), 400

    if balances.contains(Query().telegram_id == new_user_id):
        return jsonify({"status": "skipped", "message": "User already registered"}), 200

    # Register new user
    balances.insert({"telegram_id": new_user_id, "balance": 0})
    referrals.insert({"referrer": referrer_id, "new_user": new_user_id})

    # Update referrer's balance
    ref_user = balances.get(Query().telegram_id == referrer_id)
    if ref_user:
        new_balance = ref_user["balance"] + 500  # $5
        balances.update({"balance": new_balance}, Query().telegram_id == referrer_id)
    else:
        balances.insert({"telegram_id": referrer_id, "balance": 500})

    return jsonify({"status": "success", "message": "Referral successful"}), 200

if __name__ == "__main__":
    app.run()