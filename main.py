


import requests
import time
import json
from datetime import datetime

# ====== CONFIG ======
UPBIT_API_URL = "https://api.upbit.com/v1/market/all"
STATE_FILE = "upbit_markets.json"

BOT_TOKEN = "8205514298:AAEaL4Btdl0oT5Ohu3RZj7moY3DU3HuPS6w"
CHAT_ID = "Y7523660884"
CHECK_INTERVAL = 60  # seconds
# ====================

def send_telegram_message(message):
    """Send message to Telegram chat"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")

def fetch_markets():
    """Fetch all current markets from Upbit API"""
    try:
        response = requests.get(UPBIT_API_URL, params={"isDetails": "false"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return sorted([m["market"] for m in data])
    except Exception as e:
        print(f"⚠️ Error fetching markets: {e}")
        return []

def load_previous_state():
    """Load previously saved markets"""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_state(markets):
    """Save current markets to file"""
    with open(STATE_FILE, "w") as f:
        json.dump(markets, f, indent=2)

def main():
    print("🚀 Starting Upbit Listing Scanner with Telegram Alerts")
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
            message += "\n🚨 Check Upbit now — possible new token(s)!"
            print(message)
            send_telegram_message(message)
            previous_markets = current_markets
            save_state(current_markets)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
