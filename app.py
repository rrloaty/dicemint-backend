from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB = "users.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id TEXT PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/get_balance", methods=["POST"])
def get_balance():
    data = request.get_json()
    telegram_id = str(data.get("telegram_id"))
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cur.fetchone()
    if result:
        balance = result[0]
    else:
        balance = 0
        cur.execute("INSERT INTO users (telegram_id, balance) VALUES (?, ?)", (telegram_id, 0))
        conn.commit()
    conn.close()
    return jsonify({"balance": balance})

@app.route("/update_balance", methods=["POST"])
def update_balance():
    data = request.get_json()
    telegram_id = str(data.get("telegram_id"))
    balance = int(data.get("balance", 0))
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO users (telegram_id, balance) VALUES (?, ?)", (telegram_id, balance))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "balance": balance})

@app.route("/")
def home():
    return "DiceMint Backend is Running!"

if __name__ == "__main__":
    app.run(debug=True)