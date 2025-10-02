import requests
import time
import json
from datetime import datetime
from flask import Flask
import threading
import os

# ===== CONFIG =====
UPBIT_API_URL = "https://api.upbit.com/v1/market/all"
STATE_FILE = "upbit_markets.json"
CHECK_INTERVAL = 60  # seconds

# ✅ Safe Render environment variable names
UPBIT_BOT_TOKEN = os.getenv("UPBIT_BOT_TOKEN")  # your Telegram bot token
UPBIT_CHAT_ID = os.getenv("UPBIT_CHAT_ID")      # your Telegram chat ID
# ==================

# ===== FLASK KEEP-ALIVE =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Upbit scanner running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))  # Render sets PORT automatically
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web).start()
# ==============================

# ===== TELEGRAM ALERT FUNCTION =====
def send_telegram_message(message):
    if not UPBIT_BOT_TOKEN or not UPBIT_CHAT_ID:
        print("⚠️ Telegram token or chat ID not set")
        return
    url = f"https://api.telegram.org/bot{UPBIT_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": UPBIT_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")
# ===================================

# ===== UPBIT SCANNER FUNCTIONS =====
def fetch_markets():
    try:
        resp = requests.get(UPBIT_API_URL, params={"isDetails": "false"}, timeout=10)
        resp.raise_for_status()
        return sorted([m["market"] for m in resp.json()])
    except Exception as e:
        print(f"⚠️ Error fetching markets: {e}")
        return []

def load_previous_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_state(markets):
    with open(STATE_FILE, "w") as f:
        json.dump(markets, f, indent=2)
# ===================================

# ===== MAIN LOOP =====
def main():
    print("🚀 Starting Upbit Listing Scanner on Render")
    previous_markets = load_previous_state()

    while True:
        current_markets = fetch_markets()
        if not current_markets:
            time.sleep(CHECK_INTERVAL)
            continue

        new_listings = list(set(current_markets) - set(previous_markets))
        if new_listings:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"🔥 <b>New Upbit Listing Detected</b>\n🕒 {timestamp}\n"
            for m in sorted(new_listings):
                message += f"👉 <code>{m}</code>\n"
            message += "\n🚨 Check Upbit now!"
            print(message)
            send_telegram_message(message)
            previous_markets = current_markets
            save_state(current_markets)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # ✅ Send a one-time startup test message
    send_telegram_message("🚀 Test alert: Upbit scanner is live on Render!")

    # Start the main Upbit scanner loop
    main()
